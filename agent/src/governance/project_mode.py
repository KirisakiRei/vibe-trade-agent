"""Analysis-only project mode: execution-tool exclusion policy.

AGENT.md §13: the project must default to ``ANALYSIS_ONLY`` — market data,
research, technical analysis, backtesting, simulation, memory, skills,
scheduler, Telegram and reporting are allowed; live buy/sell, position
modification, withdrawals, broker execution and autonomous order submission
are forbidden.

Upstream exposes trading connector tools (``trading_place_order``,
``trading_cancel_order``, eToro position/copy tools).  Rather than deleting
them (which would complicate upstream merges), the project *gates* them out of
the agent tool registry whenever analysis-only mode is active (AGENT.md §13:
"disable / gate / exclude from agent tool registry").

Read-only trading tools (``trading_positions``, ``trading_orders``,
``trading_check``, ...) intentionally stay registered: they are pure reads and
analysis benefits from them.  ``propose_mandate_profiles`` is also read-only
(it persists a proposal file, never an order) and remains available.
"""

from __future__ import annotations

import logging
import os

logging.basicConfig()
logger = logging.getLogger(__name__)

#: Env var that turns analysis-only mode on.  Use the value ``"true"``
#: (or ``"1"``/``"yes"``/``"on"``, case-insensitive) to activate.
ANALYSIS_ONLY_ENV = "VIBE_TRADING_ANALYSIS_ONLY"

#: Tools that execute (or modify) live positions — excluded in analysis-only
#: mode.  Kept in a frozen set so the policy is deterministic and trivially
#: testable.  Names match the concrete ``BaseTool`` subclasses in
#: ``src/tools/trading_connector_tool.py``.
_EXECUTION_TOOL_NAMES = frozenset(
    {
        "trading_place_order",
        "trading_cancel_order",
        "etoro_close_position",
        "etoro_cancel_close_order",
        "etoro_edit_position_stops",
        "etoro_copy_start",
        "etoro_copy_poll",
        "etoro_copy_close",
        "etoro_copy_precheck",
    }
)

#: Copy-trading is explicitly out of scope for the project (AGENT.md §38) —
#: the eToro copy-trading tools are always treated as off-limits, independent
#: of the analysis-only flag, so no build can accidentally expose them.
_FORBIDDEN_ALWAYS_TOOL_NAMES = frozenset(
    {
        "etoro_copy_start",
        "etoro_copy_poll",
        "etoro_copy_close",
        "etoro_copy_precheck",
    }
)


def analysis_only_enabled() -> bool:
    """Return whether analysis-only mode is active for this process.

    Reads ``VIBE_TRADING_ANALYSIS_ONLY`` from the environment using the same
    truthy-string contract as the rest of the config layer.

    Returns:
        True when the env flag is truthy; False otherwise (safe default:
        upstream tool surface is preserved unless explicitly opted in).
    """
    from src.config.accessor import _parse_bool

    return _parse_bool(os.getenv(ANALYSIS_ONLY_ENV, ""))


def excluded_tool_names(analysis_only: bool | None = None) -> frozenset[str]:
    """Return the tool names the agent registry must exclude.

    The set is deterministic on its inputs, which makes the policy easy to
    unit-test: ``excluded_tool_names(True)`` always returns the execution
    tools plus the always-forbidden copy-trading tools.

    Args:
        analysis_only: Analysis-only flag.  ``None`` resolves it from the
            environment via :func:`analysis_only_enabled`.

    Returns:
        Names of tools that must not appear in the agent's tool registry.
    """
    flag = analysis_only_enabled() if analysis_only is None else analysis_only
    excluded = set(_FORBIDDEN_ALWAYS_TOOL_NAMES)
    if flag:
        excluded |= _EXECUTION_TOOL_NAMES
    return frozenset(excluded)


def is_execution_tool(name: str) -> bool:
    """Return whether *name* is a live-execution tool name.

    Args:
        name: Tool name to classify.

    Returns:
        True for tools that place, cancel, close or modify live positions.
    """
    return name in _EXECUTION_TOOL_NAMES


__all__ = [
    "ANALYSIS_ONLY_ENV",
    "analysis_only_enabled",
    "excluded_tool_names",
    "is_execution_tool",
]