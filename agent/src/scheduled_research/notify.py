"""Per-owner notification delivery for scheduled research jobs.

User-specific jobs carry an owner (``telegram:<user-id>``) so their
notifications are delivered **only** to that owner's private chat.  Global
jobs (no owner) must never be pushed to a user chat -- they may broadcast via
their own configured channel strategy, if any.

Pure helpers are separated from the async bus publish so the routing rules are
trivially unit-testable without any channel runtime.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from src.channels.bus.events import OutboundMessage
from src.scheduled_research.models import (
    ScheduledResearchJob,
    job_owner,
    notification_target,
)

logger = logging.getLogger(__name__)

#: Outbound metadata flag marking a scheduler-originated notification.
SCHEDULED_NOTIFICATION_META_KEY = "_scheduled_notification"


def owner_outbound_message(
    job: ScheduledResearchJob,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[OutboundMessage]:
    """Build the owner-only delivery for a user-specific job.

    Args:
        job: The scheduled research job.
        content: Message body to deliver.
        metadata: Extra outbound metadata; the scheduler flag is merged in.

    Returns:
        An :class:`OutboundMessage` addressed to the owner's private chat, or
        None for global jobs (no owner) -- a global job's notification must
        never be forced into a user chat.
    """
    target = notification_target(job)
    if target is None:
        return None
    channel, chat_id = target
    meta = dict(metadata or {})
    meta[SCHEDULED_NOTIFICATION_META_KEY] = True
    return OutboundMessage(
        channel=str(channel),
        chat_id=str(chat_id),
        content=content,
        metadata=meta,
    )


async def publish_owner_notification(
    job: ScheduledResearchJob,
    content: str,
    bus: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Publish a notification to the job owner's chat, when one exists.

    Delivery is a no-op (returns False) when the job has no owner or no channel
    bus is available, so scheduling never depends on notification success.

    Args:
        job: The scheduled research job.
        content: Message body to deliver.
        bus: The channel MessageBus, or None to safely skip delivery.
        metadata: Extra outbound metadata.

    Returns:
        True when an owner target exists and the message was queued; False
        when there is no owner or no bus is available.
    """
    msg = owner_outbound_message(job, content, metadata=metadata)
    if msg is None or bus is None:
        return False
    try:
        await bus.publish_outbound(msg)
        return True
    except Exception:  # noqa: BLE001 - a notification must never break scheduling
        logger.warning(
            "scheduled owner notification failed for job %s", job.id, exc_info=True
        )
        return False


def session_config_for_job(
    job: ScheduledResearchJob, base: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build the session config for a scheduler-run job.

    Starts from the job's own ``config`` dict (carrying owner markers) and, for
    user-specific jobs, attaches the canonical ``user_identity`` so the agent
    run gets the owner's private scoped memory instead of a shared one.

    Args:
        job: The scheduled research job.
        base: Optional base config to start from; defaults to ``job.config``.

    Returns:
        A new config dict; the input is never mutated.
    """
    from src.channels.identity import session_config_with_identity

    config = dict(base if base is not None else job.config or {})
    owner = job_owner(job)
    if owner is None:
        return config
    owner_type, owner_id = owner
    try:
        return session_config_with_identity(config, f"{owner_type}:{owner_id}")
    except Exception:  # noqa: BLE001 - malformed owner must not break dispatch
        logger.debug("scheduled job %s has non-scoped owner %s:%s",
                     job.id, owner_type, owner_id)
        return config


__all__ = [
    "SCHEDULED_NOTIFICATION_META_KEY",
    "owner_outbound_message",
    "publish_owner_notification",
    "session_config_for_job",
]