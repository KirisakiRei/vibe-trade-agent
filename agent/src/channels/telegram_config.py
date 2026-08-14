"""Telegram channel configuration model.

Lives in its own module (no ``python-telegram-bot`` import) so the config
layer can be unit-tested without the heavy SDK: the Pydantic model, its
camelCase aliasing, and the webhook validation rules are pure config logic.

The alias design accepts BOTH spellings everywhere ``agent.json`` or the
operator UI writes channel settings:

- snake_case field names (``allowlist_enabled``, ``group_policy``)
- camelCase aliases (``allowlistEnabled``, ``groupPolicy``)

Case matters for ``allowlist_enabled`` in particular: the Telegram channel
fail-closes by default, so a misspelt alias would silently leave the bot
closed to every sender.
"""

from __future__ import annotations

import re
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__all__ = ["TelegramConfig"]


_STREAM_EDIT_INTERVAL_DEFAULT = 0.6  # min seconds between edit_message_text calls


def _to_camel(name: str) -> str:
    """Convert snake_case field names to camelCase config aliases.

    Args:
        name: Pydantic field name in snake_case form (e.g. ``allowlist_enabled``).

    Returns:
        The camelCase alias accepted in ``agent.json`` (e.g. ``allowlistEnabled``).
    """
    parts = name.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class TelegramConfig(BaseModel):
    """Telegram channel configuration."""

    # Accept both snake_case (Python field names) and the camelCase aliases
    # used in agent.json / the operator UI (allowlistEnabled, groupPolicy,
    # allowFrom, ...). populate_by_name keeps snake_case working, so either
    # spelling is valid and unambiguous.
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    enabled: bool = False
    token: str = ""
    mode: Literal["polling", "webhook"] = "polling"
    allow_from: list[str] = Field(default_factory=list)
    # Master access switch: True (default, fail-closed) enforces allowlist +
    # pairing; False opens the bot to every sender (no pairing required).
    allowlist_enabled: bool = True
    proxy: str | None = None
    reply_to_message: bool = False
    react_emoji: str = "👀"
    group_policy: Literal["open", "mention"] = "mention"
    connection_pool_size: int = 32
    pool_timeout: float = 5.0
    streaming: bool = True
    # Enable inline keyboard buttons in Telegram messages.
    inline_keyboards: bool = False
    # Opt in to Bot API 10.1 sendRichMessage for richer markdown rendering.
    rich_messages: bool = False
    stream_edit_interval: float = Field(default=_STREAM_EDIT_INTERVAL_DEFAULT, ge=0.1)
    webhook_url: str = ""
    webhook_listen_host: str = "127.0.0.1"
    webhook_listen_port: int = Field(default=8081, ge=1, le=65535)
    webhook_path: str = "/telegram"
    webhook_secret_token: str = ""
    webhook_max_connections: int = Field(default=4, ge=1, le=100)

    @field_validator("webhook_path")
    @classmethod
    def webhook_path_must_start_with_slash(cls, value: str) -> str:
        value = value.strip() or "/telegram"
        if not value.startswith("/"):
            raise ValueError('webhook_path must start with "/"')
        return value

    @model_validator(mode="after")
    def validate_webhook_config(self) -> "TelegramConfig":
        if self.mode != "webhook":
            return self

        url = self.webhook_url.strip()
        if not url:
            raise ValueError("webhook_url is required when Telegram mode is webhook")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("webhook_url must be a public HTTPS URL")
        secret = self.webhook_secret_token.strip()
        if not secret:
            raise ValueError("webhook_secret_token is required when Telegram mode is webhook")
        if len(secret) > 256 or re.match(r"^[A-Za-z0-9_-]+$", secret) is None:
            raise ValueError(
                "webhook_secret_token must be 1-256 characters using only A-Z, a-z, 0-9, _ and -"
            )
        return self