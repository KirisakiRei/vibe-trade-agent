"""QT/IPDA/MMXM output contract: Telegram default is BRIEF, not a full audit."""

from __future__ import annotations

from pathlib import Path


_SKILL_DIR = Path(__file__).resolve().parents[1] / "src" / "skills" / "qt-ipda-mmxm"


def test_brief_is_the_default_telegram_contract() -> None:
    output = (_SKILL_DIR / "15-output-format.md").read_text(encoding="utf-8")
    skill = (_SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "## BRIEF (default — wajib untuk Telegram)" in output
    assert "Maksimal 12 baris" in output
    assert "FULL AUDIT (hanya jika diminta)" in output
    assert "Brevity (Wajib untuk Telegram)" in skill
    assert "Default output adalah **BRIEF**" in skill


def test_brief_still_requires_direction_and_status() -> None:
    output = (_SKILL_DIR / "15-output-format.md").read_text(encoding="utf-8")
    brief = output.split("## FULL AUDIT", 1)[0]

    assert "DIRECTION" in brief
    assert "FINAL STATUS" in brief
    assert "Invalidation" in brief
    assert "Monthly:" not in brief
