"""Tests for analysis-only project mode (AGENT.md §13).

Verifies that:
- ``excluded_tool_names`` is deterministic: execution/copy tools are excluded
  when analysis-only is on, and read-only trading tools stay available.
- ``build_registry`` honors the flag without changing the upstream tool
  surface when the flag is off (backward compatibility).
"""

from __future__ import annotations

import pytest

from src.governance.project_mode import (
    analysis_only_enabled,
    excluded_tool_names,
    is_execution_tool,
)
from src.tools import build_registry

_EXECUTION_TOOLS = {
    "trading_place_order",
    "trading_cancel_order",
    "etoro_close_position",
    "etoro_cancel_close_order",
    "etoro_edit_position_stops",
}

_COPY_TOOLS = {
    "etoro_copy_start",
    "etoro_copy_poll",
    "etoro_copy_close",
    "etoro_copy_precheck",
}

_READ_ONLY_TRADING_TOOLS = {
    "trading_connections",
    "trading_check",
    "trading_account",
    "trading_positions",
    "trading_orders",
    "trading_quote",
    "trading_history",
}


class TestExcludedToolNames:
    def test_analysis_only_excludes_execution_tools(self) -> None:
        excluded = excluded_tool_names(True)
        assert _EXECUTION_TOOLS <= excluded

    def test_copy_tools_always_excluded(self) -> None:
        for flag in (True, False, None):
            assert _COPY_TOOLS <= excluded_tool_names(flag)

    def test_non_execution_tools_not_excluded(self) -> None:
        excluded = excluded_tool_names(True)
        assert not (_READ_ONLY_TRADING_TOOLS & excluded)

    def test_off_mode_excludes_nothing_beyond_always_forbidden(self) -> None:
        excluded = excluded_tool_names(False)
        assert excluded == _COPY_TOOLS

    def test_deterministic(self) -> None:
        assert excluded_tool_names(True) == excluded_tool_names(True)

    def test_env_flag_reads_truthy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("VIBE_TRADING_ANALYSIS_ONLY", raising=False)
        assert analysis_only_enabled() is False
        monkeypatch.setenv("VIBE_TRADING_ANALYSIS_ONLY", "true")
        assert analysis_only_enabled() is True


class TestIsExecutionTool:
    def test_classifies_place_order(self) -> None:
        assert is_execution_tool("trading_place_order")
        assert not is_execution_tool("trading_positions")
        assert not is_execution_tool("load_skill")


class TestBuildRegistryAnalysisOnly:
    def test_full_surface_preserved_when_off(self) -> None:
        registry = build_registry(analysis_only=False, agent_config=None)
        assert "trading_place_order" in registry.tool_names
        assert "trading_positions" in registry.tool_names
        assert "load_skill" in registry.tool_names

    def test_execution_tools_absent_when_on(self) -> None:
        registry = build_registry(analysis_only=True, agent_config=None)
        assert "trading_place_order" not in registry.tool_names
        assert "trading_cancel_order" not in registry.tool_names
        assert not any(name.startswith("etoro_copy_") for name in registry.tool_names)

    def test_read_tools_and_core_tools_remain_when_on(self) -> None:
        registry = build_registry(analysis_only=True, agent_config=None)
        assert "trading_positions" in registry.tool_names
        assert "trading_orders" in registry.tool_names
        assert "load_skill" in registry.tool_names
        assert "get_market_data" in registry.tool_names
        assert "remember" in registry.tool_names