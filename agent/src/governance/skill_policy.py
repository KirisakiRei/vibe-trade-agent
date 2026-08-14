"""Write-governance policy for trading-rule skills.

Core trading rules (QT / IPDA / MMXM + custom checklist) are the project's
source of truth and must remain immutable from the agent's perspective
(AGENT.md §8, §9, §10).  The upstream skill writer tools (save_skill,
patch_skill, delete_skill, skill_file) can create, override and delete user
skills — including silently copying a *bundled* skill into the user skill
directory and patching it.  This module provides a small pure policy that the
skill writer tools consult before mutating anything.

Policy model:

    qt-ipda-mmxm (and any name listed in VIBE_TRADING_PROTECTED_SKILLS)
        -> agent write DENIED

    ``<protected-skill>/core/**``
        -> agent write DENIED

    everything else (learned/*, research/*, proposals/*)
        -> agent write ALLOWED

The policy is deliberately name-based (not path-based): the danger is an
agent-created skill *named* like a protected one, because user skills override
bundled skills in ``SkillsLoader``.  Denial at the name level therefore covers
both the bundled location and any user-directory override.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

#: Environment variable that can extend the protected-skill set
#: (comma-separated names).
_PROTECTED_SKILLS_ENV = "VIBE_TRADING_PROTECTED_SKILLS"

#: Skills protected by default.  ``qt-ipda-mmxm`` is the project's core
#: trading framework; it does not need to exist yet for the policy to apply.
_DEFAULT_PROTECTED_SKILLS = frozenset({"qt-ipda-mmxm"})

#: Path segments inside a protected skill that are always read-only for the
#: agent, regardless of the skill's own name.  ``core`` holds the immutable
#: rule definitions per AGENT.md §10.
_PROTECTED_PATH_SEGMENTS = frozenset({"core"})

#: Sub-directories of the skill root the agent may use for surrogates of the
#: protected rule set (learned insights, research, rule-change proposals).
#: These stay writable per AGENT.md §10, provided the *skill itself* is not a
#: protected name.
_WRITABLE_SUBDIRS = frozenset({"learned", "research", "proposals"})


class SkillWriteDeniedError(RuntimeError):
    """Raised when the agent attempts to mutate a protected trading-rule skill."""


@dataclass(frozen=True)
class SkillWritePolicy:
    """Pure, deterministic policy for whether a skill may be mutated.

    Attributes:
        protected_skills: Exact skill names that are read-only for the agent.
        path_segments: Resource path segments that are read-only *inside* a
            protected skill (e.g. ``core``).
    """

    protected_skills: frozenset[str] = _DEFAULT_PROTECTED_SKILLS
    path_segments: frozenset[str] = _PROTECTED_PATH_SEGMENTS

    @classmethod
    def from_env(cls) -> "SkillWritePolicy":
        """Build the policy from the explicit env override plus defaults.

        ``VIBE_TRADING_PROTECTED_SKILLS`` may add (or replace) protected skill
        names; defaults are always applied as a floor so a mis-set env var can
        never accidentally lift protection from the core framework.

        Returns:
            A policy combining the default protected set with any env override.
        """
        extra = os.getenv(_PROTECTED_SKILLS_ENV, "")
        names: set[str] = set(_DEFAULT_PROTECTED_SKILLS)
        for chunk in extra.split(","):
            name = chunk.strip().lower()
            if name:
                names.add(name)
        return cls(protected_skills=frozenset(names))

    def is_protected(self, skill_name: str) -> bool:
        """Return whether *skill_name* is protected from agent mutation.

        Matching is case-insensitive and exact.  Sub-skill variants under a
        protected framework (e.g. ``qt-ipda-mmxm-core``) are not automatically
        protected: name them explicitly in ``VIBE_TRADING_PROTECTED_SKILLS``
        when needed, keeping the policy simple and predictable.

        Args:
            skill_name: Sanitized skill slug to test.

        Returns:
            True when the skill name is in the protected set.
        """
        return skill_name.strip().lower() in self.protected_skills

    def deny_reason(self, skill_name: str, relative_path: str = "") -> str | None:
        """Return the denial reason when *skill_name* may not be mutated.

        Args:
            skill_name: Skill slug that would be written.
            relative_path: Optional path inside the skill directory (e.g.
                ``core/01-foundation.md``).  Empty for SKILL.md writes.

        Returns:
            A human-readable reason string when the write must be refused,
            otherwise ``None``.
        """
        if self.is_protected(skill_name):
            return (
                f"Skill '{skill_name}' is a protected trading-rule skill. "
                "Core trading rules are immutable and cannot be modified, "
                "patched, or deleted by the agent (AGENT.md §8-§10). "
                "Propose rule changes via the proposal mechanism instead."
            )

        segments = [s for s in relative_path.replace("\\", "/").split("/") if s]
        denied = [seg for seg in segments if seg in self.path_segments]
        if denied:
            return (
                f"Path 'core/…' inside skill '{skill_name}' is protected: "
                "core trading rules are immutable and cannot be written by "
                "the agent (AGENT.md §8-§10)."
            )
        return None

    def enforce(self, skill_name: str, relative_path: str = "") -> None:
        """Raise :class:`SkillWriteDeniedError` when the write is prohibited.

        Args:
            skill_name: Skill slug that would be written.
            relative_path: Optional path inside the skill directory.

        Raises:
            SkillWriteDeniedError: When the policy denies the write.
        """
        reason = self.deny_reason(skill_name, relative_path)
        if reason is not None:
            logger.info("skill write denied by governance policy: %s", reason)
            raise SkillWriteDeniedError(reason)


#: Module-level policy backed by the environment.  It is rebuilt on every
#: access so env overrides (Settings API, tests) take effect immediately —
#: the same freshness contract as ``src/config/accessor.py``.
def get_skill_write_policy() -> SkillWritePolicy:
    """Return the process-wide skill write policy.

    Rebuilds from the current environment on each call so a runtime env
    change is honoured without a process restart.

    Returns:
        The env-backed policy instance.
    """
    return SkillWritePolicy.from_env()