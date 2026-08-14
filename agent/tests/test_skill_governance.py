"""Tests for the skill write governance policy (AGENT.md §8-§10).

Verifies that protected trading-rule skills cannot be saved, patched, deleted
or file-mutated by the agent through the skill writer tools.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from src.governance.skill_policy import (
    SkillWriteDeniedError,
    SkillWritePolicy,
    get_skill_write_policy,
)
from src.tools.skill_writer_tool import (
    DeleteSkillTool,
    PatchSkillTool,
    SaveSkillTool,
    SkillFileTool,
)


# ---------------------------------------------------------------------------
# Pure policy
# ---------------------------------------------------------------------------


class TestSkillWritePolicy:
    def test_default_protects_qt_ipda_mmxm(self) -> None:
        policy = SkillWritePolicy()
        assert policy.is_protected("qt-ipda-mmxm")

    def test_default_protection_is_exact_and_case_insensitive(self) -> None:
        policy = SkillWritePolicy()
        assert policy.is_protected("QT-IPDA-MMXM")
        assert not policy.is_protected("qt-ipda-mmxm2")
        assert not policy.is_protected("learned-btc-regime")

    def test_env_override_extends_protection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VIBE_TRADING_PROTECTED_SKILLS", "my-custom-rule")
        policy = get_skill_write_policy()
        assert policy.is_protected("my-custom-rule")
        # Default floor remains even when env overrides (never lifted).
        assert policy.is_protected("qt-ipda-mmxm")

    def test_env_override_empty_keeps_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VIBE_TRADING_PROTECTED_SKILLS", "  ")
        policy = get_skill_write_policy()
        assert policy.is_protected("qt-ipda-mmxm")

    def test_deny_reason_for_protected_name(self) -> None:
        policy = SkillWritePolicy()
        reason = policy.deny_reason("qt-ipda-mmxm")
        assert reason is not None
        assert "immutable" in reason

    def test_deny_reason_for_core_path_segment(self) -> None:
        policy = SkillWritePolicy()
        reason = policy.deny_reason("any-skill", "core/01-foundation.md")
        assert reason is not None
        assert "protected" in reason

    def test_no_denial_for_writable_learned_path(self) -> None:
        policy = SkillWritePolicy()
        assert policy.deny_reason("learned-insight-1", "observations.md") is None
        assert policy.deny_reason("research-btc", "findings.md") is None
        assert policy.deny_reason("qt-ipda-mmxm-proposal", "proposal.md") is None

    def test_enforce_raises_for_protected(self) -> None:
        policy = SkillWritePolicy()
        with pytest.raises(SkillWriteDeniedError):
            policy.enforce("qt-ipda-mmxm")
        with pytest.raises(SkillWriteDeniedError):
            policy.enforce("normal-skill", "core/rules.md")

    def test_enforce_passes_for_writable(self) -> None:
        policy = SkillWritePolicy()
        # Should not raise
        policy.enforce("learned-observation")


# ---------------------------------------------------------------------------
# Tool integration
# ---------------------------------------------------------------------------


@pytest.fixture()
def user_dir(tmp_path: Path) -> Path:
    return tmp_path


class TestSaveSkillGovernance:
    def _tool(self, tmp_path: Path) -> SaveSkillTool:
        from unittest.mock import patch

        with patch("src.tools.skill_writer_tool.USER_SKILLS_DIR", tmp_path):
            return SaveSkillTool()

    def test_cannot_save_protected_skill(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("VIBE_TRADING_PROTECTED_SKILLS", "qt-ipda-mmxm")
        tool = self._tool(tmp_path)
        result = json.loads(tool.execute(name="qt-ipda-mmxm", content="core rules"))
        assert result["status"] == "error"
        assert "immutable" in result["error"] or "protected" in result["error"]
        assert not (tmp_path / "qt-ipda-mmxm").exists()

    def test_can_save_non_protected_skill(self, user_dir: Path) -> None:
        tool = self._tool(user_dir)
        result = json.loads(tool.execute(name="learned-pattern", content="insight"))
        assert result["status"] == "ok"


class TestPatchSkillGovernance:
    def test_cannot_patch_protected_skill(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        from unittest.mock import patch as mock_patch

        monkeypatch.setenv("VIBE_TRADING_PROTECTED_SKILLS", "qt-ipda-mmxm")
        with mock_patch("src.tools.skill_writer_tool.USER_SKILLS_DIR", tmp_path):
            tool = PatchSkillTool()
            result = json.loads(
                tool.execute(name="qt-ipda-mmxm", find="A", replace="B")
            )
        assert result["status"] == "error"
        assert "immutable" in result["error"] or "protected" in result["error"]


class TestDeleteSkillGovernance:
    def test_cannot_delete_protected_skill(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        from unittest.mock import patch as mock_patch

        monkeypatch.setenv("VIBE_TRADING_PROTECTED_SKILLS", "qt-ipda-mmxm")
        (tmp_path / "qt-ipda-mmxm").mkdir(parents=True)
        with mock_patch("src.tools.skill_writer_tool.USER_SKILLS_DIR", tmp_path):
            tool = DeleteSkillTool()
            result = json.loads(tool.execute(name="qt-ipda-mmxm"))
        assert result["status"] == "error"
        assert (tmp_path / "qt-ipda-mmxm").exists()

    def test_can_delete_non_protected_user_skill(self, tmp_path: Path) -> None:
        from unittest.mock import patch as mock_patch

        (tmp_path / "unrelated").mkdir(parents=True)
        with mock_patch("src.tools.skill_writer_tool.USER_SKILLS_DIR", tmp_path):
            tool = DeleteSkillTool()
            result = json.loads(tool.execute(name="unrelated"))
        assert result["status"] == "ok"
        assert not (tmp_path / "unrelated").exists()


class TestSkillFileGovernance:
    def test_cannot_write_core_path_in_protected_skill(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        from unittest.mock import patch as mock_patch

        monkeypatch.setenv("VIBE_TRADING_PROTECTED_SKILLS", "qt-ipda-mmxm")
        skill_dir = tmp_path / "qt-ipda-mmxm"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: qt-ipda-mmxm\n---\n", encoding="utf-8")
        with mock_patch("src.tools.skill_writer_tool.USER_SKILLS_DIR", tmp_path):
            tool = SkillFileTool()
            result = json.loads(
                tool.execute(
                    action="write",
                    skill_name="qt-ipda-mmxm",
                    path="references/core-rules.md",
                    content="x",
                )
            )
        assert result["status"] == "error"
        assert not (skill_dir / "references" / "core-rules.md").exists()