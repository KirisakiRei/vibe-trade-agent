"""Allowlist master-switch tests.

A channel may run in two modes:

- ``allowlist_enabled`` true (default, fail-closed): only senders on
  ``allow_from`` / a ``"*"`` wildcard / approved pairing entries may interact.
- ``allowlist_enabled`` false: every sender is allowed, no pairing required.

The toggle lives on the shared ``BaseChannel.is_allowed`` so every channel gets
it consistently, and ``TelegramConfig`` exposes it as a configurable field.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from src.channels.base import BaseChannel
from src.channels.bus.events import OutboundMessage


class _DummyChannel(BaseChannel):
    """Minimal concrete channel for permission tests."""

    name = "dummy"

    async def start(self) -> None:  # pragma: no cover - test double
        pass

    async def stop(self) -> None:  # pragma: no cover - test double
        pass

    async def send(self, msg: OutboundMessage) -> None:  # pragma: no cover
        pass


class _FakeBus:
    async def publish_outbound(self, msg: OutboundMessage) -> None:  # pragma: no cover
        pass


def _channel(config: Any) -> _DummyChannel:
    return _DummyChannel(config=config, bus=_FakeBus())


def _dict_config(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"allow_from": []}
    base.update(overrides)
    return base


class TestAllowlistToggle:
    def test_default_is_fail_closed(self) -> None:
        ch = _channel(_dict_config())
        assert ch.is_allowed("111111111") is False

    def test_allowlist_only_sender_admitted(self) -> None:
        ch = _channel(_dict_config(allow_from=["111111111"]))
        assert ch.is_allowed("111111111") is True
        assert ch.is_allowed("222222222") is False

    def test_star_wildcard_admits_everyone(self) -> None:
        ch = _channel(_dict_config(allow_from=["*"]))
        assert ch.is_allowed("999999999") is True

    def test_open_mode_admits_everyone_without_allowlist(self) -> None:
        ch = _channel(_dict_config(allowlist_enabled=False))
        assert ch.is_allowed("111111111") is True
        assert ch.is_allowed("222222222") is True
        assert ch.is_allowed("unknown-user") is True

    def test_open_mode_ignores_allowlist_whilst_on(self) -> None:
        ch = _channel(
            _dict_config(allowlist_enabled=False, allow_from=["111111111"])
        )
        assert ch.is_allowed("987654321") is True

    def test_object_config_reads_toggle_with_default(self) -> None:
        closed = _channel(SimpleNamespace(allow_from=[], allowlist_enabled=True))
        assert closed.is_allowed("111111111") is False

        # Attribute absent → default True (fail-closed), preserving behaviour
        # for any channel whose config object predates the field.
        legacy = _channel(SimpleNamespace(allow_from=[]))
        assert legacy.is_allowed("111111111") is False

        open_obj = _channel(SimpleNamespace(allow_from=[], allowlist_enabled=False))
        assert open_obj.is_allowed("111111111") is True


class TestChannelsConfigWiring:
    def test_agent_config_accepts_allowlist_enabled_via_channels(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        from src.channels.config import load_channels_config

        tmp = tmp_path.mkdir("cfg") if not hasattr(tmp_path, "mkdir") else tmp_path
        config_path = tmp / "agent.json"
        config_path.write_text(
            """
            {
              "channels": {
                "telegram": {
                  "enabled": true,
                  "token": "x",
                  "allowlistEnabled": false,
                  "allowFrom": ["111111111"]
                }
              }
            }
            """.strip(),
            encoding="utf-8",
        )

        channels = load_channels_config(config_path)

        # The per-channel section is an extra field and passes through
        # verbatim (camelCase); TelegramConfig accepts the alias on load.
        assert channels["telegram"]["allowlistEnabled"] is False
        assert channels["telegram"]["allowFrom"] == ["111111111"]

    def test_agent_config_defaults_to_fail_closed(self, tmp_path: pytest.TempPathFactory) -> None:
        from src.channels.config import load_channels_config

        tmp = tmp_path.mkdir("cfg") if not hasattr(tmp_path, "mkdir") else tmp_path
        config_path = tmp / "agent.json"
        config_path.write_text(
            """
            {
              "channels": {
                "telegram": {
                  "enabled": true,
                  "token": "x"
                }
              }
            }
            """.strip(),
            encoding="utf-8",
        )

        channels = load_channels_config(config_path)

        assert channels["telegram"].get("allowlistEnabled", True) is True


class TestTelegramConfigAliasing:
    """The per-channel dict passes through agent.json verbatim, so the Pydantic
    model itself must accept the camelCase aliases we document (allowlistEnabled
    etc.). A misspelt ignore would silently leave the bot fail-closed."""

    def test_camelcase_open_mode_drives_is_allowed(self) -> None:
        from src.channels.telegram_config import TelegramConfig

        cfg = TelegramConfig.model_validate({"allowlistEnabled": False})
        assert cfg.allowlist_enabled is False

        ch = _channel(cfg)
        assert ch.is_allowed("111111111") is True

    def test_camelcase_group_policy_and_allow_from(self) -> None:
        from src.channels.telegram_config import TelegramConfig

        cfg = TelegramConfig.model_validate(
            {"allowFrom": ["111111111"], "groupPolicy": "open"}
        )
        assert cfg.allow_from == ["111111111"]
        assert cfg.group_policy == "open"

    def test_snake_case_still_valid(self) -> None:
        from src.channels.telegram_config import TelegramConfig

        cfg = TelegramConfig.model_validate(
            {"allowlist_enabled": False, "allow_from": ["111111111"]}
        )
        assert cfg.allowlist_enabled is False
        assert cfg.allow_from == ["111111111"]

    def test_officially_documented_snippet(self) -> None:
        """The .env.example / agent.json snippet must produce an OPEN bot."""
        from src.channels.telegram_config import TelegramConfig

        cfg = TelegramConfig.model_validate(
            {
                "enabled": True,
                "token": "123:abc",
                "allowlistEnabled": False,
                "mode": "polling",
            }
        )
        assert cfg.allowlist_enabled is False
        assert cfg.token == "123:abc"

        ch = _channel(cfg)
        assert ch.is_allowed("999999999") is True