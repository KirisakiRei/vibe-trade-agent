"""Multi-user session & memory isolation tests.

Covers the project's Telegram multi-user requirements:

1. User A and User B get different sessions.
2. Conversation history does not leak between users.
3. User A's memory cannot be recalled by User B.
4. Global research can be used by both users.
5. Core QT/IPDA/MMXM skills are available to every user.
6. Self-learning never writes personal data into global memory.
7. Scheduled notifications are delivered only to the correct owner.
8. Resetting User A's session does not reset User B.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.channels.bus.events import InboundMessage
from src.channels.identity import (
    InvalidUserIdentityError,
    canonical_user_id,
    identity_for_session,
    session_config_with_identity,
    user_memory_dir,
    user_memory_namespace,
    validate_identity,
)
from src.channels.runtime import ChannelRuntime
from src.memory.scopes import ScopedMemory, build_scoped_memory
from src.scheduled_research.models import (
    OWNER_ID_KEY,
    OWNER_TYPE_KEY,
    ScheduledResearchJob,
    job_owner,
    notification_target,
    set_job_owner,
)
from src.session.models import Session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeSessionService:
    """Minimal SessionService stand-in storing created sessions in memory."""

    def __init__(self) -> None:
        self.sessions: list[Session] = []

    def create_session(self, title: str = "", config: dict | None = None) -> Session:
        session = Session(title=title, config=dict(config or {}))
        self.sessions.append(session)
        return session


def _make_runtime(tmp_path: Path) -> tuple[ChannelRuntime, _FakeSessionService]:
    service = _FakeSessionService()
    runtime = ChannelRuntime(
        bus=None,  # typo-proof: only _session_for is exercised here
        session_service=service,
        manager=None,
        session_map_path=tmp_path / "sessions.json",
    )
    return runtime, service


def _dm_message(user_id: str, chat_id: str | None = None) -> InboundMessage:
    """Build a Telegram private-DM inbound message for one user."""
    return InboundMessage(
        channel="telegram",
        sender_id=f"{user_id}|alice" if user_id.endswith("1") else f"{user_id}|bob",
        chat_id=str(chat_id or user_id),
        content="hello",
        metadata={
            "user_id": int(user_id),
            "is_group": False,
            "username": "alice" if user_id.endswith("1") else "bob",
        },
        session_key_override=f"telegram:{user_id}",
    )


# ---------------------------------------------------------------------------
# 1. User A and User B get different sessions
# ---------------------------------------------------------------------------


class TestSessionIsolation:
    def test_dm_sessions_are_per_user(self, tmp_path: Path) -> None:
        runtime, service = _make_runtime(tmp_path)
        sid_a = runtime._session_for(_dm_message("111111111"))
        sid_b = runtime._session_for(_dm_message("222222222"))
        assert sid_a != sid_b
        assert len(service.sessions) == 2
        assert runtime._session_map["telegram:111111111"] == sid_a
        assert runtime._session_map["telegram:222222222"] == sid_b

    def test_same_user_reuses_session(self, tmp_path: Path) -> None:
        runtime, service = _make_runtime(tmp_path)
        first = runtime._session_for(_dm_message("333333333"))
        second = runtime._session_for(_dm_message("333333333"))
        assert first == second
        assert len(service.sessions) == 1

    def test_session_config_carries_canonical_identity(self, tmp_path: Path) -> None:
        runtime, service = _make_runtime(tmp_path)
        runtime._session_for(_dm_message("111111111"))
        assert service.sessions[0].config.get("user_identity") == "telegram:111111111"

    def test_group_message_gets_no_private_identity(self, tmp_path: Path) -> None:
        runtime, service = _make_runtime(tmp_path)
        msg = InboundMessage(
            channel="telegram",
            sender_id="111111111|alice",
            chat_id="-100123456",
            content="group message",
            metadata={
                "user_id": 111111111,
                "is_group": True,
            },
        )
        runtime._session_for(msg)
        assert "user_identity" not in service.sessions[0].config


# ---------------------------------------------------------------------------
# 2. Conversation history does not leak between users
# ---------------------------------------------------------------------------


class TestConversationIsolation:
    def test_user_messages_land_in_distinct_sessions(self, tmp_path: Path) -> None:
        runtime, service = _make_runtime(tmp_path)
        sid_a = runtime._session_for(_dm_message("111111111"))
        sid_b = runtime._session_for(_dm_message("222222222"))
        # Distinct sessions mean distinct message stores upstream: the map key,
        # and the session_id the store keys on, are both per-user.
        assert runtime._session_map["telegram:111111111"] == sid_a
        assert runtime._session_map["telegram:222222222"] == sid_b
        assert sid_a != sid_b
        assert all(
            s.session_id in (sid_a, sid_b) for s in service.sessions
        )


# ---------------------------------------------------------------------------
# 3 / 4 / 6. Memory scope isolation & sharing & self-learning routing
# ---------------------------------------------------------------------------


class TestMemoryScopes:
    def _scope(self, root: Path, identity: str) -> ScopedMemory:
        return build_scoped_memory(identity, memory_root=root)

    # Requirement 3: A's memory cannot be recalled by B.
    def test_user_memory_is_private(self, tmp_path: Path) -> None:
        scope_a = self._scope(tmp_path, "telegram:111111111")
        path = scope_a.add(
            "EURUSD preference",
            "User A prefers EURUSD as the primary pair.",
            memory_type="user",
            description="EURUSD preference",
        )
        assert path is not None
        assert "users" in path.parts

        scope_b = self._scope(tmp_path, "telegram:222222222")
        recall_b = scope_b.find_relevant("EURUSD preference")
        assert recall_b == []
        recall_a = scope_a.find_relevant("EURUSD preference")
        assert any("EURUSD" in e.body for e in recall_a)

    # Requirement 4: global research is visible to both users.
    def test_global_research_shared_by_all_users(self, tmp_path: Path) -> None:
        scope_a = self._scope(tmp_path, "telegram:111111111")
        scope_a.add(
            "HTF bias study",
            "Historical setup statistics: HTF bias wins 62% across 2025 samples.",
            memory_type="project",
            description="HTF bias study",
        )
        scope_b = self._scope(tmp_path, "telegram:222222222")
        assert any("HTF bias" in e.body for e in scope_a.find_relevant("HTF bias"))
        assert any("HTF bias" in e.body for e in scope_b.find_relevant("HTF bias"))

    # Requirement 6: self-learning never writes personal data to global memory.
    def test_user_preferences_never_land_in_global_scope(
        self, tmp_path: Path
    ) -> None:
        scope_aggregate = self._scope(tmp_path, "telegram:111111111")
        scope_aggregate.add(
            "wants GBP retention",
            "User likes GBPJPY; keep it in the watchlist.",
            memory_type="user",
            description="GBP preference",
        )
        global_entries = scope_aggregate.global_memory.find_relevant("GBPJPY")
        user_entries = scope_aggregate.user_memory.find_relevant("GBPJPY")
        assert global_entries == []
        assert len(user_entries) >= 1

    def test_project_memory_defaults_to_global(self, tmp_path: Path) -> None:
        scope = self._scope(tmp_path, "telegram:111111111")
        path = scope.add(
            "backtest conclusion",
            "London-New York overlap sweep outperforms standalone sessions.",
            memory_type="project",
            description="backtest conclusion",
        )
        assert path is not None
        assert "users" not in path.parts
        assert any(
            "London" in e.body for e in scope.global_memory.find_relevant("London")
        )


# ---------------------------------------------------------------------------
# 5. Core QT/IPDA/MMXM skills are shared, read-only, for all users
# ---------------------------------------------------------------------------


class TestCoreSkillsShared:
    def test_core_skill_loaded_for_everyone(self) -> None:
        from src.agent.skills import SkillsLoader

        loader = SkillsLoader()
        names = {s.name for s in loader.skills}
        assert "qt-ipda-mmxm" in names


# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------


class TestIdentity:
    def test_canonical_identity_format(self) -> None:
        assert canonical_user_id("telegram", 111111111) == "telegram:111111111"
        assert canonical_user_id("telegram", "222222222") == "telegram:222222222"

    def test_invalid_telegram_identity_rejected(self) -> None:
        with pytest.raises(InvalidUserIdentityError):
            canonical_user_id("telegram", "alice")
        with pytest.raises(InvalidUserIdentityError):
            canonical_user_id("telegram", "@username")
        with pytest.raises(InvalidUserIdentityError):
            canonical_user_id("telegram", "")

    def test_namespace_mapping(self) -> None:
        assert user_memory_namespace("telegram:111111111") == "telegram_111111111"
        assert user_memory_namespace("telegram:222222222") == "telegram_222222222"

    def test_user_memory_dir_layout(self, tmp_path: Path) -> None:
        d = user_memory_dir(tmp_path, "telegram:111111111")
        assert d == tmp_path / "users" / "telegram_111111111"

    def test_validate_roundtrip(self) -> None:
        identity = validate_identity("telegram:111111111")
        assert identity == "telegram:111111111"

    def test_session_config_identity_helpers(self) -> None:
        config = session_config_with_identity({"channel": "telegram"}, "telegram:111111111")
        assert config["user_identity"] == "telegram:111111111"
        assert identity_for_session(config) == "telegram:111111111"
        assert identity_for_session({"channel": "telegram"}) is None
        assert identity_for_session(None) is None


# ---------------------------------------------------------------------------
# 7. Scheduled notifications only to the owner
# ---------------------------------------------------------------------------


class TestSchedulerOwner:
    def _job(self) -> ScheduledResearchJob:
        return ScheduledResearchJob(
            id="user-1",
            prompt="Daily bias for EURUSD",
            schedule="60000",
        )

    def test_job_without_owner_is_global(self) -> None:
        job = self._job()
        assert job_owner(job) is None
        assert notification_target(job) is None

    def test_user_job_owner_and_target(self) -> None:
        job = self._job()
        set_job_owner(job, "telegram", "111111111")
        assert job_owner(job) == ("telegram", "111111111")
        assert notification_target(job) == ("telegram", "111111111")

    def test_notification_target_follows_owner(self) -> None:
        job_a = self._job()
        set_job_owner(job_a, "telegram", "111111111")
        job_b = self._job()
        set_job_owner(job_b, "telegram", "222222222")
        assert notification_target(job_a) == ("telegram", "111111111")
        assert notification_target(job_b) == ("telegram", "222222222")

    def test_owner_survives_disk_serialization(self, tmp_path: Path) -> None:
        job = self._job()
        set_job_owner(job, "telegram", "111111111")
        payload = json.loads(json.dumps(job.to_dict()))
        restored = ScheduledResearchJob.from_dict(payload)
        assert restored.config[OWNER_TYPE_KEY] == "telegram"
        assert restored.config[OWNER_ID_KEY] == "111111111"
        assert job_owner(restored) == ("telegram", "111111111")


# ---------------------------------------------------------------------------
# 8. Resetting User A does not reset User B
# ---------------------------------------------------------------------------


class TestSessionReset:
    def test_reset_a_keeps_b_session(self, tmp_path: Path) -> None:
        runtime, _ = _make_runtime(tmp_path)
        sid_a = runtime._session_for(_dm_message("111111111"))
        sid_b = runtime._session_for(_dm_message("222222222"))

        removed = runtime.reset_session("telegram:111111111")

        assert removed == sid_a
        assert "telegram:111111111" not in runtime._session_map
        assert runtime._session_map.get("telegram:222222222") == sid_b

    def test_reset_then_new_session_for_user_a(self, tmp_path: Path) -> None:
        runtime, service = _make_runtime(tmp_path)
        old_a = runtime._session_for(_dm_message("111111111"))
        runtime.reset_session("telegram:111111111")
        new_a = runtime._session_for(_dm_message("111111111"))
        assert new_a != old_a
        assert len(service.sessions) == 2

    def test_reset_unknown_key_is_noop(self, tmp_path: Path) -> None:
        runtime, _ = _make_runtime(tmp_path)
        assert runtime.reset_session("telegram:999999999") is None