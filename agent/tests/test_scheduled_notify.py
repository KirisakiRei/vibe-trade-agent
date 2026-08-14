"""Owner-only scheduled notification tests.

Verifies that user-specific scheduled jobs deliver notifications only to
their owner's private chat, that global jobs never get a user target, and that
scheduler-created sessions carry the owner's canonical identity (so the run
gets the owner's private scoped memory).
"""

from __future__ import annotations

import asyncio

import pytest

from src.channels.bus.events import OutboundMessage
from src.scheduled_research.models import ScheduledResearchJob, set_job_owner
from src.scheduled_research.notify import (
    SCHEDULED_NOTIFICATION_META_KEY,
    owner_outbound_message,
    publish_owner_notification,
    session_config_for_job,
)


class _FakeBus:
    """Capture published outbound messages."""

    def __init__(self) -> None:
        self.messages: list[OutboundMessage] = []

    async def publish_outbound(self, msg: OutboundMessage) -> None:
        self.messages.append(msg)


def _job(job_id: str = "job-1") -> ScheduledResearchJob:
    return ScheduledResearchJob(id=job_id, prompt="Daily bias", schedule="60000")


class TestOwnerOutboundMessage:
    def test_global_job_has_no_user_target(self) -> None:
        assert owner_outbound_message(_job(), "hello") is None

    def test_user_job_targets_owner_chat(self) -> None:
        job = _job()
        set_job_owner(job, "telegram", "111111111")
        msg = owner_outbound_message(job, "bias ready")
        assert msg is not None
        assert msg.channel == "telegram"
        assert msg.chat_id == "111111111"
        assert msg.content == "bias ready"
        assert msg.metadata.get(SCHEDULED_NOTIFICATION_META_KEY) is True

    def test_owner_a_and_owner_b_never_share_target(self) -> None:
        job_a = _job("a")
        set_job_owner(job_a, "telegram", "111111111")
        job_b = _job("b")
        set_job_owner(job_b, "telegram", "222222222")
        msg_a = owner_outbound_message(job_a, "x")
        msg_b = owner_outbound_message(job_b, "x")
        assert msg_a is not None and msg_b is not None
        assert msg_a.chat_id == "111111111"
        assert msg_b.chat_id == "222222222"
        assert msg_a.chat_id != msg_b.chat_id


class TestPublishOwnerNotification:
    def test_no_bus_is_safe_noop(self) -> None:
        job = _job()
        set_job_owner(job, "telegram", "111111111")
        assert asyncio.run(publish_owner_notification(job, "x", bus=None)) is False

    def test_global_job_never_published(self) -> None:
        bus = _FakeBus()
        assert asyncio.run(publish_owner_notification(_job(), "x", bus=bus)) is False
        assert bus.messages == []

    def test_publishes_to_owner_only(self) -> None:
        bus = _FakeBus()
        job = _job()
        set_job_owner(job, "telegram", "555555555")
        published = asyncio.run(
            publish_owner_notification(job, "analysis done", bus=bus)
        )
        assert published is True
        assert len(bus.messages) == 1
        assert bus.messages[0].channel == "telegram"
        assert bus.messages[0].chat_id == "555555555"

    def test_publish_failure_never_breaks_scheduling(self) -> None:
        class _BrokenBus:
            async def publish_outbound(self, msg: OutboundMessage) -> None:
                raise RuntimeError("bus down")

        job = _job()
        set_job_owner(job, "telegram", "111111111")
        assert asyncio.run(
            publish_owner_notification(job, "x", bus=_BrokenBus())
        ) is False


class TestSessionConfigForJob:
    def test_global_job_config_passes_through(self) -> None:
        job = _job()
        job.config["scope"] = "market-wide"
        config = session_config_for_job(job)
        assert config["scope"] == "market-wide"
        assert "user_identity" not in config

    def test_user_job_carries_owner_identity(self) -> None:
        job = _job()
        set_job_owner(job, "telegram", "111111111")
        config = session_config_for_job(job)
        assert config.get("user_identity") == "telegram:111111111"

    def test_input_config_is_not_mutated(self) -> None:
        job = _job()
        set_job_owner(job, "telegram", "111111111")
        original = dict(job.config)
        session_config_for_job(job, base={"existing": True})
        assert job.config == original

    def test_base_config_is_preserved(self) -> None:
        job = _job()
        set_job_owner(job, "telegram", "222222222")
        config = session_config_for_job(job, base={"channel": "telegram"})
        assert config["channel"] == "telegram"
        assert config.get("user_identity") == "telegram:222222222"