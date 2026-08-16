"""Empty-model-response recovery behavior.

A gateway or reasoning model may occasionally return an empty response (no
content, no tool call) mid-run. The agent loop must nudge the model to
continue (bounded retries) instead of failing the whole run immediately,
while still failing when the model stays silent repeatedly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pytest

from src.providers.chat import LLMResponse


class _FlakyEmptyLLM:
    """LLM stub that returns empty responses a scripted number of times."""

    def __init__(self, empty_times: int, final_content: str = "Final answer.") -> None:
        self._empty_remaining = empty_times
        self._final_content = final_content
        self.calls = 0
        self.messages_history: list[list[dict[str, Any]]] = []

    def stream_chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[Any] | None = None,
        on_text_chunk: Callable[[str], None] | None = None,
        on_reasoning_chunk: Callable[[str], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> LLMResponse:
        self.calls += 1
        self.messages_history.append(list(messages))
        del tools, on_reasoning_chunk, should_cancel
        if self._empty_remaining > 0:
            self._empty_remaining -= 1
            return LLMResponse(content="")
        if on_text_chunk:
            on_text_chunk(self._final_content)
        return LLMResponse(content=self._final_content)

    def chat(self, messages: list[dict[str, Any]], **_: Any) -> LLMResponse:
        return LLMResponse(content="")


class _AlwaysEmptyLLM:
    """LLM stub that always returns an empty response."""

    def __init__(self) -> None:
        self.calls = 0

    def stream_chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[Any] | None = None,
        on_text_chunk: Callable[[str], None] | None = None,
        on_reasoning_chunk: Callable[[str], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> LLMResponse:
        self.calls += 1
        del tools, on_text_chunk, on_reasoning_chunk, should_cancel
        return LLMResponse(content="")

    def chat(self, messages: list[dict[str, Any]], **_: Any) -> LLMResponse:
        return LLMResponse(content="")


def _run(
    tmp_path: Path,
    llm: Any,
    max_iterations: int = 5,
) -> dict[str, Any]:
    from src.agent.loop import AgentLoop
    from src.memory.persistent import PersistentMemory
    from src.tools import build_registry

    pm = PersistentMemory()
    agent = AgentLoop(
        registry=build_registry(persistent_memory=pm, include_shell_tools=False),
        llm=llm,
        max_iterations=max_iterations,
        persistent_memory=pm,
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    agent.memory.run_dir = str(run_dir)
    return agent.run(user_message="hello")


def _read_trace(run_dir: str) -> list[dict[str, Any]]:
    from src.agent.trace import TraceWriter

    return TraceWriter.read(Path(run_dir))


def test_single_empty_response_recovers_and_succeeds(tmp_path: Path) -> None:
    llm = _FlakyEmptyLLM(empty_times=1, final_content="Final answer.")

    result = _run(tmp_path, llm)

    assert result["status"] == "success"
    assert result["content"] == "Final answer."
    assert llm.calls == 2


def test_repeated_empty_responses_ultimately_fail_with_named_reason(tmp_path: Path) -> None:
    llm = _AlwaysEmptyLLM()

    result = _run(tmp_path, llm)

    assert result["status"] == "failed"
    assert result["reason"].startswith("empty_model_response")


def test_empty_recovery_entries_written_to_trace(tmp_path: Path) -> None:
    from src.agent.loop import MAX_EMPTY_MODEL_RECOVERY_PROMPTS

    llm = _FlakyEmptyLLM(empty_times=2, final_content="Final answer.")

    result = _run(tmp_path, llm)

    assert result["status"] == "success"
    trace = _read_trace(result["run_dir"])
    recovery = [e for e in trace if e.get("type") == "empty_model_recovery"]
    assert len(recovery) == 2
    assert recovery[0]["attempt"] <= MAX_EMPTY_MODEL_RECOVERY_PROMPTS


def test_salvage_ignores_short_or_generic_reasoning() -> None:
    from src.agent.loop import salvage_reasoning_as_answer

    assert salvage_reasoning_as_answer(None) == ""
    assert salvage_reasoning_as_answer("thinking...") == ""
    assert salvage_reasoning_as_answer("I need more data from the tools.") == ""
    assert salvage_reasoning_as_answer(
        "DIRECTION: NONE\nFINAL STATUS: NO_SETUP\nReason: no key level yet."
    ).startswith("DIRECTION")


def test_reasoning_trace_with_direction_is_salvaged(tmp_path: Path) -> None:
    class _ReasoningOnlyLLM:
        def stream_chat(self, *args: Any, **kwargs: Any) -> LLMResponse:
            del args, kwargs
            return LLMResponse(
                content="",
                reasoning_content=(
                    "DIRECTION: BEARISH\n"
                    "FINAL STATUS: WAITING\n"
                    "Reason: daily SSL swept, waiting 5M CISD."
                ),
            )

        def chat(self, *args: Any, **kwargs: Any) -> LLMResponse:
            del args, kwargs
            return LLMResponse(content="")

    result = _run(tmp_path, _ReasoningOnlyLLM())

    assert result["status"] == "success"
    assert "DIRECTION: BEARISH" in result["content"]
    trace = _read_trace(result["run_dir"])
    assert any(e.get("type") == "reasoning_salvage" for e in trace)


def test_fallback_model_activates_after_empty_exhaustion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import src.agent.loop as loop_mod
    from src.config.accessor import reset_env_config

    monkeypatch.setenv("LANGCHAIN_FALLBACK_MODEL_NAME", "fallback-flash")
    reset_env_config()

    class _FallbackLLM:
        def __init__(self, model_name: str = "fallback-flash") -> None:
            self.model_name = model_name
            self.calls = 0

        def stream_chat(self, *args: Any, **kwargs: Any) -> LLMResponse:
            del args, kwargs
            self.calls += 1
            return LLMResponse(content="DIRECTION: BULLISH\nFINAL STATUS: WAITING")

        def chat(self, *args: Any, **kwargs: Any) -> LLMResponse:
            del args, kwargs
            return LLMResponse(content="")

    fallback = _FallbackLLM()
    monkeypatch.setattr(
        loop_mod,
        "build_fallback_chat_llm",
        lambda model_name="": fallback,
        raising=False,
    )

    result = _run(tmp_path, _AlwaysEmptyLLM(), max_iterations=6)

    assert result["status"] == "success"
    assert "DIRECTION: BULLISH" in result["content"]
    assert fallback.calls == 1
    trace = _read_trace(result["run_dir"])
    assert any(e.get("type") == "fallback_model_activated" for e in trace)
    reset_env_config()


def test_recovery_nudge_message_added_to_messages(tmp_path: Path) -> None:
    from src.agent.loop import EMPTY_MODEL_RECOVERY_MESSAGE

    llm = _FlakyEmptyLLM(empty_times=1, final_content="Final answer.")

    result = _run(tmp_path, llm)
    assert result["status"] == "success"
    # Second call carries the nudge message appended to the transcript.
    nudge_found = any(
        msg.get("role") == "system"
        and EMPTY_MODEL_RECOVERY_MESSAGE in str(msg.get("content", ""))
        for msg in llm.messages_history[1]
    )
    assert nudge_found