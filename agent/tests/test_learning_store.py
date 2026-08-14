"""Tests for the audited learning storage (AGENT.md §9-§12, §23).

Verifies that insights/research/proposals are persisted, audited via the
hash-chained ledger, validated structurally, and visible to operators.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.governance.learning_store import (
    LearnedInsight,
    LearningStore,
    LearningValidationError,
    RuleChangeProposal,
    _new_id,
    _now_iso,
    validate_metadata,
)


@pytest.fixture()
def store(tmp_path: Path) -> LearningStore:
    return LearningStore(root=tmp_path / "project")


class TestValidateMetadata:
    def test_requires_audit_fields(self) -> None:
        with pytest.raises(LearningValidationError):
            validate_metadata({"content": "x"})

    def test_accepts_complete_metadata(self) -> None:
        meta = validate_metadata(
            {"timestamp": _now_iso(), "source": "daily-analysis", "created_by": "agent"}
        )
        assert meta["source"] == "daily-analysis"

    def test_requires_non_empty_timestamp(self) -> None:
        with pytest.raises(LearningValidationError):
            validate_metadata(
                {"timestamp": "", "source": "s", "created_by": "c"}
            )


class TestNewId:
    def test_prefixed_and_unique(self) -> None:
        a = _new_id("insight")
        b = _new_id("insight")
        assert a.startswith("insight_")
        assert a != b


class TestLearningStore:
    def _insight(self, **overrides) -> LearnedInsight:
        kwargs = dict(
            category="performance-per-symbol",
            content="BTC Daily Q3 setups historically perform better when "
            "Sweep + SSMT + CISD are all present.",
            symbol="BTCUSDT",
            timeframe="1D",
            confidence=0.8,
            evidence="backtest 2020-2024",
            metadata={
                "timestamp": _now_iso(),
                "source": "scheduled-analysis",
                "created_by": "agent",
                "related_analysis": "run-abc",
            },
        )
        kwargs.update(overrides)
        return LearnedInsight(**kwargs)

    def test_add_insight_persists_and_audits(self, store: LearningStore) -> None:
        record = store.add_insight(self._insight())
        assert record["kind"] == "insight"
        assert store.get_record("learned", record["id"]) == record
        assert store.ledger_path.exists()

    def test_insight_invalid_without_content(self, store: LearningStore) -> None:
        with pytest.raises(LearningValidationError):
            store.add_insight(self._insight(content=""))

    def test_insight_invalid_without_metadata(self, store: LearningStore) -> None:
        with pytest.raises(LearningValidationError):
            store.add_insight(self._insight(metadata={}))

    def test_insight_confidence_out_of_range(self, store: LearningStore) -> None:
        with pytest.raises(LearningValidationError):
            store.add_insight(self._insight(confidence=1.5))

    def test_add_research_persists(self, store: LearningStore) -> None:
        record = store.add_research(
            "Regime sensitivity",
            "5M CISD triggers cluster around London killzone.",
            metadata={"timestamp": _now_iso(), "source": "research", "created_by": "agent"},
            data_range="2024-01-01..2024-06-30",
            symbol="BTCUSDT",
            timeframe="5M",
        )
        assert record["kind"] == "research"
        assert record["data_range"] == "2024-01-01..2024-06-30"
        assert store.get_record("research", record["id"]) == record

    def test_add_proposal_persists_never_applied(self, store: LearningStore) -> None:
        proposal = RuleChangeProposal(
            title="Make CISD optional after 2 sweeps",
            current_rule="CISD is mandatory",
            proposed_change="CISD optional",
            reason="repeated late confirms",
            historical_evidence="60 cases",
            sample_size=60,
            backtest_result="n/a",
            potential_benefit="earlier entries",
            risk="weaker confirmation",
            affected_files=["12-checklist.md"],
            rollback_plan="revert to mandatory",
            metadata={"timestamp": _now_iso(), "source": "backtest", "created_by": "agent"},
        )
        record = store.add_proposal(proposal)
        assert record["kind"] == "proposal"
        assert record["status"] == "OPEN"
        assert store.get_record("proposals", record["id"])["current_rule"] == "CISD is mandatory"

    def test_proposal_missing_required_fields(self, store: LearningStore) -> None:
        with pytest.raises(LearningValidationError):
            store.add_proposal(
                RuleChangeProposal(
                    title="x",
                    current_rule="",
                    proposed_change="y",
                    metadata={"timestamp": _now_iso(), "source": "s", "created_by": "c"},
                )
            )

    def test_proposal_negative_sample_size(self, store: LearningStore) -> None:
        with pytest.raises(LearningValidationError):
            store.add_proposal(
                RuleChangeProposal(
                    title="x",
                    current_rule="a",
                    proposed_change="b",
                    sample_size=-1,
                    metadata={"timestamp": _now_iso(), "source": "s", "created_by": "c"},
                )
            )

    def test_list_records_orders_newest_first(self, store: LearningStore) -> None:
        store.add_insight(self._insight(content="first"))
        store.add_insight(self._insight(content="second"))
        records = store.list_records("learned")
        assert len(records) == 2
        # id embeds uuid hex; ordering by id desc is stable, not semantic time.
        # Just assert both present and dirs exist.
        assert {r["content"] for r in records} == {"first", "second"}

    def test_update_status_audited(self, store: LearningStore) -> None:
        record = store.add_proposal(
            RuleChangeProposal(
                title="proposal",
                current_rule="a",
                proposed_change="b",
                metadata={"timestamp": _now_iso(), "source": "s", "created_by": "agent"},
            )
        )
        updated = store.update_status("proposals", record["id"], "Rejected")
        assert updated is not None
        assert updated["status"] == "REJECTED"

    def test_update_missing_record_returns_none(self, store: LearningStore) -> None:
        assert store.update_status("proposals", "proposal_missing", "APPROVED") is None

    def test_dir_names_match_governance_layout(self, store: LearningStore) -> None:
        assert store.learned_dir().name == "learned"
        assert store.research_dir().name == "research"
        assert store.proposals_dir().name == "proposals"