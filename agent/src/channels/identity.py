"""Canonical user identity helpers for per-user session/memory isolation.

Telegram bots must isolate sessions, conversation history and personal memory
per user.  The canonical identity is ``telegram:<numeric-user-id>``; the
username is only a display/secondary identifier because it can change.

This module is pure and deterministic so it is trivially unit-testable.  It
knows nothing about the session registry or the memory store — it only maps
identifiers to canonical keys and filesystem namespaces.

Scope model (AGENT.md §10):

    CORE            -> immutable trading-rule skills (not here)
    GLOBAL LEARNING -> shared memory namespace (all users)
    USER MEMORY     -> per-user namespace, never shared
"""

from __future__ import annotations

import re
from pathlib import Path

#: Channel prefix for Telegram identities.
TELEGRAM_CHANNEL = "telegram"

#: Digits-only Telegram numeric user id.
_TELEGRAM_USER_ID_RE = re.compile(r"^\d+$")

#: Characters that are safe in a memory namespace directory name.
_NAMESPACE_DISALLOWED_RE = re.compile(r"[^a-z0-9_\-]")

#: Config key under which the canonical user identity is stored on a session.
SESSION_USER_IDENTITY_KEY = "user_identity"

#: Metadata key carrying the canonical identity on inbound messages.
MESSAGE_USER_IDENTITY_KEY = "user_identity"


class InvalidUserIdentityError(ValueError):
    """Raised when a user identity is not structurally valid."""


def canonical_user_id(channel: str, user_id: str | int) -> str:
    """Build the canonical global identity for a user.

    The numeric Telegram id is the primary stable identifier; the username is
    intentionally not part of the canonical key because it can change.

    Args:
        channel: Channel name (e.g. ``telegram``).
        user_id: Numeric platform user id.

    Returns:
        ``f"{channel}:{user_id}"``.

    Raises:
        InvalidUserIdentityError: When the id is empty / not numeric for
            Telegram (where only numeric ids are stable).
    """
    channel_norm = str(channel).strip().lower()
    id_str = str(user_id).strip()

    if channel_norm == TELEGRAM_CHANNEL:
        # Telegram chat/user ids are numeric.  Negative ids are group chats;
        # individual users are always positive digits.
        unique = _TELEGRAM_USER_ID_RE.fullmatch(id_str)
        if unique is None:
            raise InvalidUserIdentityError(
                f"invalid telegram user id {user_id!r}: must be a positive numeric id"
            )
    else:
        if not id_str:
            raise InvalidUserIdentityError("user id must not be empty")

    return f"{channel_norm}:{id_str}"


def parse_user_id(identity: str) -> str:
    """Return the platform user id component of a canonical identity.

    Args:
        identity: Canonical identity produced by :func:`canonical_user_id`.

    Returns:
        The numeric user id.

    Raises:
        InvalidUserIdentityError: When the identity is malformed.
    """
    if not isinstance(identity, str) or ":" not in identity:
        raise InvalidUserIdentityError(f"malformed user identity: {identity!r}")
    channel, _, uid = identity.partition(":")
    if not channel or not uid:
        raise InvalidUserIdentityError(f"malformed user identity: {identity!r}")
    return uid.strip()


def validate_identity(identity: str) -> str:
    """Validate a canonical identity, returning it normalized.

    Args:
        identity: Canonical identity.

    Returns:
        The identity unchanged when valid.

    Raises:
        InvalidUserIdentityError: On malformed input.
    """
    channel, sep, uid = (identity or "").partition(":")
    if not sep:
        raise InvalidUserIdentityError(f"malformed user identity: {identity!r}")
    canonical_user_id(channel, uid)
    return identity


def user_memory_namespace(identity: str) -> str:
    """Map a canonical identity to a safe memory namespace directory name.

    ``telegram:111111111`` -> ``telegram_111111111`` so it can be used as a
    directory name under the memory root (``memory/users/``).

    Args:
        identity: Canonical identity.

    Returns:
        A filesystem-safe namespace string.
    """
    normalized = validate_identity(identity)
    raw = normalized.replace(":", "_")
    slug = _NAMESPACE_DISALLOWED_RE.sub("_", raw.lower())
    return slug or "unknown_user"


def user_memory_dir(memory_root: Path, identity: str) -> Path:
    """Return the private memory directory for one user.

    Args:
        memory_root: Memory root (e.g. ``~/.vibe-trading/memory``).
        identity: Canonical user identity.

    Returns:
        ``<memory_root>/users/<namespace>``.
    """
    return Path(memory_root) / "users" / user_memory_namespace(identity)


def identity_for_session(session_config: dict | None) -> str | None:
    """Read the canonical identity stored on a session's config dict.

    Args:
        session_config: Session config mapping (may be ``None``).

    Returns:
        The canonical identity or ``None`` when not present.
    """
    if not session_config:
        return None
    value = session_config.get(SESSION_USER_IDENTITY_KEY)
    if not value:
        return None
    try:
        return validate_identity(str(value))
    except InvalidUserIdentityError:
        return None


def session_config_with_identity(config: dict | None, identity: str | None) -> dict:
    """Return a copy of a session config carrying the canonical identity.

    Args:
        config: Base session config dict (may be ``None``).
        identity: Canonical identity to store (or ``None`` to drop the key).

    Returns:
        A shallow copy of *config* with ``user_identity`` set/removed.
    """
    result = dict(config or {})
    if identity:
        result[SESSION_USER_IDENTITY_KEY] = validate_identity(identity)
    else:
        result.pop(SESSION_USER_IDENTITY_KEY, None)
    return result


__all__ = [
    "TELEGRAM_CHANNEL",
    "SESSION_USER_IDENTITY_KEY",
    "MESSAGE_USER_IDENTITY_KEY",
    "InvalidUserIdentityError",
    "canonical_user_id",
    "parse_user_id",
    "validate_identity",
    "user_memory_namespace",
    "user_memory_dir",
    "identity_for_session",
    "session_config_with_identity",
]