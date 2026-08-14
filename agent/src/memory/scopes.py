"""Scoped memory: global (shared) + per-user (private) composite.

AGENT.md §10 + the project's multi-user requirement:

- GLOBAL memory  -> shared research / market-wide insights, all users.
- USER memory    -> private per-user namespace, never shared.
- CORE rules     -> immutable skills, not stored here.

``ScopedMemory`` is a thin composite over two ``PersistentMemory`` instances
(one global, one per user).  It exposes the same surface the agent loop,
``ContextBuilder`` and ``RememberTool`` rely on, so wiring it into
``SessionService`` requires no changes to those consumers:

- ``snapshot`` merges both indexes for the system prompt.
- ``find_relevant`` merges user + global recall (user entries first, deduped).
- ``add`` routes by ``memory_type``: ``"user"`` -> user store, everything else
  (``project`` / ``reference`` / ``feedback``) -> global store.

The composite never writes a user preference into global memory, and never
exposes another user's namespace at all (only the injected user store is
reachable).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

from src.memory.persistent import (
    MAX_RESULTS,
    MEMORY_BASE,
    MemoryEntry,
    PersistentMemory,
)

#: Label used in the merged snapshot so the agent can tell scopes apart.
_USER_SNAPSHOT_HEADER = "User Memory (private, this user only)"
_GLOBAL_SNAPSHOT_HEADER = "Global Learning (shared)"


class ScopedMemory:
    """Composite of a global memory and one user's private memory.

    Attributes:
        global_memory: Shared, cross-user memory store.
        user_memory: This user's private memory store, or None when the
            session is not user-scoped (CLI, API without identity).
    """

    def __init__(
        self,
        global_memory: PersistentMemory,
        user_memory: PersistentMemory | None = None,
    ) -> None:
        """Initialize the scoped memory composite.

        Args:
            global_memory: Shared memory store.
            user_memory: Private per-user store, or None for unscoped sessions.
        """
        self.global_memory = global_memory
        self.user_memory = user_memory

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------

    @classmethod
    def for_user(
        cls,
        identity: str | None,
        *,
        memory_root: Path = MEMORY_BASE,
        global_memory: PersistentMemory | None = None,
    ) -> "ScopedMemory":
        """Build a scoped memory for one canonical identity.

        Args:
            identity: Canonical user identity (``telegram:<id>``) or None for
                an unscoped (global-only) session.
            memory_root: Memory root directory.
            global_memory: Optional shared store; defaults to the standard
                ``PersistentMemory(MEMORY_BASE)``.

        Returns:
            A ScopedMemory whose user store lives under
            ``<memory_root>/users/<namespace>`` when an identity is given.
        """
        from src.channels.identity import user_memory_dir

        scope = cls(global_memory or PersistentMemory(memory_root))
        if identity:
            user_dir = user_memory_dir(memory_root, identity)
            scope.user_memory = PersistentMemory(user_dir)
        return scope

    # ------------------------------------------------------------------
    # PersistentMemory-compatible surface
    # ------------------------------------------------------------------

    @property
    def _dir(self) -> Path:
        """Return the global memory directory (compat with lifecycle/linker).

        ``MemoryLifecycle`` and ``SemanticLinker`` accept a single directory;
        the global dir is the conservative choice because lifecycle/GC operate
        on shared storage by default.
        """
        return self.global_memory._dir

    @property
    def user_dir(self) -> Optional[Path]:
        """Return the user memory directory, if a user scope exists."""
        return self.user_memory._dir if self.user_memory else None

    @property
    def snapshot(self) -> str:
        """Merged memory index for the system prompt (user first, labeled)."""
        parts: list[str] = []
        if self.user_memory and self.user_memory.snapshot:
            parts.append(f"## {_USER_SNAPSHOT_HEADER}\n{self.user_memory.snapshot}")
        if self.global_memory.snapshot:
            parts.append(
                f"## {_GLOBAL_SNAPSHOT_HEADER}\n{self.global_memory.snapshot}"
            )
        return "\n\n".join(parts)

    def find_relevant(
        self, query: str, max_results: int = MAX_RESULTS
    ) -> List[MemoryEntry]:
        """Merge user + global recall, user entries first, deduped by body.

        Args:
            query: Keyword search query.
            max_results: Maximum total entries to return.

        Returns:
            Deduped entries; user-memory matches take priority.
        """
        merged: list[MemoryEntry] = []
        seen: set[str] = set()

        def _append(entries: list[MemoryEntry], budget: int) -> None:
            for entry in entries:
                key = entry.body[:200]
                if key in seen:
                    continue
                seen.add(key)
                merged.append(entry)
                if len(merged) >= budget:
                    return

        if self.user_memory:
            _append(self.user_memory.find_relevant(query, max_results=max_results), max_results)
        if len(merged) < max_results:
            _append(
                self.global_memory.find_relevant(query, max_results=max_results),
                max_results,
            )
        return merged[:max_results]

    def add(
        self,
        name: str,
        content: str,
        memory_type: str = "project",
        description: str = "",
    ) -> Optional[Path]:
        """Store an entry, routing by memory type to the correct scope.

        ``"user"`` entries always land in the private user store (isolated).
        ``project`` / ``reference`` / ``feedback`` entry types land in the
        shared global store, keeping agent-chosen research shared while user
        preferences stay private.

        Args:
            name: Memory title.
            content: Memory body.
            memory_type: One of ``MEMORY_TYPES``.
            description: Optional description.

        Returns:
            The written path, or None when a duplicate write was blocked.
        """
        if memory_type == "user" and self.user_memory is not None:
            return self.user_memory.add(name, content, memory_type, description=description)
        return self.global_memory.add(name, content, memory_type, description=description)

    def find(self, name: str) -> Optional[MemoryEntry]:
        """Locate an entry by title, user scope first then global.

        Args:
            name: Entry title.

        Returns:
            The matching entry or None.
        """
        if self.user_memory:
            entry = self.user_memory.find(name)
            if entry is not None:
                return entry
        return self.global_memory.find(name)

    def remove(self, name: str) -> bool:
        """Remove an entry by title from both scopes (user first).

        Args:
            name: Entry title.

        Returns:
            True when any scope removed the entry.
        """
        removed = False
        if self.user_memory and self.user_memory.remove(name):
            removed = True
        if self.global_memory.remove(name):
            removed = True
        return removed

    def list_entries(self) -> List[MemoryEntry]:
        """List all entries visible in this scope (user + global)."""
        entries: list[MemoryEntry] = []
        if self.user_memory:
            entries.extend(self.user_memory.list_entries())
        entries.extend(self.global_memory.list_entries())
        return entries

    def _rebuild_index(self) -> None:
        """Rebuild the memory index of every underlying store."""
        if self.user_memory:
            self.user_memory._rebuild_index()
        self.global_memory._rebuild_index()


def build_scoped_memory(
    identity: str | None,
    *,
    memory_root: Path = MEMORY_BASE,
) -> ScopedMemory:
    """Convenience factory used by session wiring.

    Args:
        identity: Canonical user identity or None.
        memory_root: Memory root directory.

    Returns:
        A ScopedMemory instance.
    """
    return ScopedMemory.for_user(identity, memory_root=memory_root)


__all__ = ["ScopedMemory", "build_scoped_memory"]