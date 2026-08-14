"""Writable learning storage for the project's self-learning layer.

AGENT.md §10-§12: learning state is stored separately from immutable core
trading rules, is writable by the agent, and every mutation must be auditable,
inspectable and reversible.  Three writable stores live under the runtime root:

    <runtime>/project/learned/     -> learned insights (writable, audited)
    <runtime>/project/research/    -> research results  (writable, audited)
    <runtime>/project/proposals/   -> rule-change proposals (writable, NEVER auto-applied)

Core rules live in the bundled (protected) trading-rule skill and are never
written here: skill_writer_tool.py enforces that with the skill write policy.

Every write is recorded in a hash-chained governance ledger
(``governance/ledger.py``), giving timestamped, tamper-evident, reversible
history per AGENT.md §12.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from src.config.paths import get_runtime_root
from src.governance.ledger import append_record

#: Sub-directories under the project root, one writable store each.
_LEARNED_DIRNAME = "learned"
_RESEARCH_DIRNAME = "research"
_PROPOSALS_DIRNAME = "proposals"

#: Ledger file name capturing every learning write.
_LEARNING_LEDGER_FILENAME = "learning.ledger.jsonl"

#: Metadata keys every category always carries (AGENT.md §12).
_REQUIRED_METADATA_KEYS = ("timestamp", "source", "created_by")


class LearningValidationError(ValueError):
    """Raised when a learning record fails structural validation."""


def _now_iso() -> str:
    """Return the current UTC time in ISO-8601 format."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _new_id(kind: str) -> str:
    """Return a short, unique, sort-friendly record id.

    Args:
        kind: Record category prefix (e.g. ``insight``, ``proposal``).

    Returns:
        ``<kind>_<uuid4-hex-prefix>``.
    """
    return f"{kind}_{uuid.uuid4().hex[:12]}"


def _coerce_timestamp(value: str) -> str:
    """Validate/normalize a timestamp value.

    Args:
        value: ISO-8601-ish timestamp string.

    Returns:
        The normalized timestamp.

    Raises:
        LearningValidationError: When the value is empty or not a string.
    """
    if not isinstance(value, str) or not value.strip():
        raise LearningValidationError("timestamp must be a non-empty string")
    return value


def validate_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize the common metadata of a learning record.

    Checks AGENT.md §12 required fields (timestamp, source, created_by) and
    normalizes known fields.  Unknown keys pass through unchanged so the
    storage is forward-compatible.

    Args:
        metadata: Raw metadata mapping.

    Returns:
        A shallow copy with validated required fields.

    Raises:
        LearningValidationError: When a required field is missing or invalid.
    """
    result: dict[str, Any] = {k: v for k, v in metadata.items()}
    missing = [key for key in _REQUIRED_METADATA_KEYS if not result.get(key)]
    if missing:
        raise LearningValidationError(
            f"learning record missing required metadata: {', '.join(sorted(missing))}"
        )
    result["timestamp"] = _coerce_timestamp(str(result["timestamp"]))
    result["source"] = str(result["source"])
    result["created_by"] = str(result["created_by"])
    return result


@dataclass(frozen=True)
class LearnedInsight:
    """One self-learning observation (AGENT.md §9 allowed learning list).

    Attributes:
        category: Insight category, e.g. ``performance-per-symbol``,
            ``market-regime``, ``backtest-observation``.
        content: The insight statement (no fabricated confirmation).
        symbol: Optional symbol the insight refers to.
        timeframe: Optional timeframe the insight refers to.
        confidence: 0..1 confidence of the insight.
        evidence: Free-form evidence backing the insight.
        metadata: Common AGENT.md §12 fields (timestamp/source/created_by)
            plus any extras (related analysis, session, previous/new value).
    """

    category: str
    content: str
    symbol: str = ""
    timeframe: str = ""
    confidence: float = 1.0
    evidence: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleChangeProposal:
    """A proposed change to core trading rules; NEVER auto-applied (AGENT.md §11).

    The proposal records the full context a human reviewer needs: current
    rule, proposed change, reason, historical evidence, sample size, backtest
    result, potential benefit, risk, affected files and rollback plan.
    """

    title: str
    current_rule: str
    proposed_change: str
    reason: str = ""
    historical_evidence: str = ""
    sample_size: int = 0
    backtest_result: str = ""
    potential_benefit: str = ""
    risk: str = ""
    affected_files: list[str] = field(default_factory=list)
    rollback_plan: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def _validated_insight(insight: LearnedInsight) -> dict[str, Any]:
    """Convert a LearnedInsight to its stored record dict (validated)."""
    if not insight.category or not insight.content:
        raise LearningValidationError(
            "insight requires non-empty 'category' and 'content'"
        )
    if not 0.0 <= insight.confidence <= 1.0:
        raise LearningValidationError("insight confidence must be within 0..1")
    return {
        "id": _new_id("insight"),
        "kind": "insight",
        "category": insight.category,
        "content": insight.content,
        "symbol": insight.symbol,
        "timeframe": insight.timeframe,
        "confidence": insight.confidence,
        "evidence": insight.evidence,
        "metadata": validate_metadata(insight.metadata),
    }


def _validated_proposal(proposal: RuleChangeProposal) -> dict[str, Any]:
    """Convert a RuleChangeProposal to its stored record dict (validated)."""
    if not proposal.title or not proposal.current_rule or not proposal.proposed_change:
        raise LearningValidationError(
            "proposal requires non-empty 'title', 'current_rule' and "
            "'proposed_change'"
        )
    if proposal.sample_size < 0:
        raise LearningValidationError("proposal sample_size must be non-negative")
    return {
        "id": _new_id("proposal"),
        "kind": "proposal",
        "status": "OPEN",
        "title": proposal.title,
        "current_rule": proposal.current_rule,
        "proposed_change": proposal.proposed_change,
        "reason": proposal.reason,
        "historical_evidence": proposal.historical_evidence,
        "sample_size": proposal.sample_size,
        "backtest_result": proposal.backtest_result,
        "potential_benefit": proposal.potential_benefit,
        "risk": proposal.risk,
        "affected_files": list(proposal.affected_files),
        "rollback_plan": proposal.rollback_plan,
        "metadata": validate_metadata(proposal.metadata),
    }


class LearningStore:
    """Persistent, audited storage for insights, research and proposals.

    Attributes:
        root: Project root directory containing the writable sub-directories.
        ledger_path: Hash-chained ledger recording every learning write.
    """

    def __init__(self, root: Path | None = None) -> None:
        """Initialize the store.

        Args:
            root: Project root; defaults to ``<runtime root>/project``.
        """
        self.root = root or (get_runtime_root() / "project")
        self.ledger_path = self.root / _LEARNING_LEDGER_FILENAME

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------

    def _dir(self, kind: str) -> Path:
        d = self.root / kind
        d.mkdir(parents=True, exist_ok=True)
        return d

    def learned_dir(self) -> Path:
        """Return the learned-insights directory (created on demand)."""
        return self._dir(_LEARNED_DIRNAME)

    def research_dir(self) -> Path:
        """Return the research-results directory (created on demand)."""
        return self._dir(_RESEARCH_DIRNAME)

    def proposals_dir(self) -> Path:
        """Return the rule-change proposals directory (created on demand)."""
        return self._dir(_PROPOSALS_DIRNAME)

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def _write_record(self, kind: str, record: dict[str, Any]) -> dict[str, Any]:
        """Persist one record as JSON + append an audit record to the ledger.

        Args:
            kind: Store sub-directory name (learned/research/proposals).
            record: Validated record dict (already carries its ``id``).

        Returns:
            The stored record.

        Raises:
            LearningValidationError: When the record structure is invalid.
        """
        if not record.get("id"):
            raise LearningValidationError("record must carry an 'id'")
        path = self._dir(kind) / f"{record['id']}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

        audit_payload = {
            "kind": record["kind"],
            "record_id": record["id"],
            "name": record.get("title") or record.get("category") or "",
            "symbol": record.get("symbol", ""),
            "timeframe": record.get("timeframe", ""),
            "created_by": record.get("metadata", {}).get("created_by", ""),
            "confidence": record.get("confidence"),
        }
        append_record(self.ledger_path, audit_payload)
        return record

    def add_insight(self, insight: LearnedInsight) -> dict[str, Any]:
        """Store a learned insight (writable, audited; AGENT.md §9-§10).

        Args:
            insight: The insight to store.

        Returns:
            The stored record dict.

        Raises:
            LearningValidationError: On invalid structure.
        """
        return self._write_record(_LEARNED_DIRNAME, _validated_insight(insight))

    def add_research(self, title: str, content: str, *, metadata: dict[str, Any] | None = None, **extras: Any) -> dict[str, Any]:
        """Store a research-result record (writable, audited).

        Args:
            title: Short research title.
            content: Research findings / conclusion text.
            metadata: Common AGENT.md §12 metadata.
            **extras: Any additional first-class fields kept on the record.

        Returns:
            The stored record dict.

        Raises:
            LearningValidationError: On invalid structure.
        """
        if not title or not content:
            raise LearningValidationError("research requires non-empty 'title' and 'content'")
        record: dict[str, Any] = {
            "id": _new_id("research"),
            "kind": "research",
            "title": title,
            "content": content,
            "metadata": validate_metadata(metadata or {}),
        }
        record.update(extras)
        return self._write_record(_RESEARCH_DIRNAME, record)

    def add_proposal(self, proposal: RuleChangeProposal) -> dict[str, Any]:
        """Store a rule-change proposal.  NEVER auto-applies anything
        (AGENT.md §11): the record is written for human review only.

        Args:
            proposal: The rule-change proposal.

        Returns:
            The stored record (status ``OPEN``).

        Raises:
            LearningValidationError: On invalid structure.
        """
        return self._write_record(_PROPOSALS_DIRNAME, _validated_proposal(proposal))

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def list_records(self, kind: str) -> list[dict[str, Any]]:
        """List stored records of one kind, newest id first.

        Args:
            kind: Store sub-directory name.

        Returns:
            Decoded record dicts found in the directory.
        """
        directory = self.root / kind
        if not directory.exists():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(directory.glob("*.json")):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                # A corrupt record must never hide the rest (fail visible via
                # listing; the JSON itself surfaces on read).
                continue
        records.sort(key=lambda r: r.get("id", ""), reverse=True)
        return records

    def get_record(self, kind: str, record_id: str) -> dict[str, Any] | None:
        """Return one stored record by id.

        Args:
            kind: Store sub-directory name.
            record_id: Stored record id (with or without the ``.json`` suffix).

        Returns:
            The record dict or ``None`` when absent/corrupt.
        """
        stored = Path(record_id)
        if stored.suffix != ".json":
            stored = stored.with_suffix(".json")
        path = self.root / kind / stored.name
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def update_status(self, kind: str, record_id: str, status: str) -> dict[str, Any] | None:
        """Update the mutable ``status`` of a record (audited).

        Used to move a proposal from ``OPEN`` to ``APPROVED`` / ``REJECTED``.
        Only the human operator may approve; this method never triggers any
        rule application by itself (AGENT.md §11).

        Args:
            kind: Store sub-directory name.
            record_id: Stored record id.
            status: New status value.

        Returns:
            The updated record, or ``None`` when the record does not exist.

        Raises:
            LearningValidationError: When the new status is invalid.
        """
        status_str = str(status).upper().strip()
        if not status_str:
            raise LearningValidationError("status must not be empty")
        record = self.get_record(kind, record_id)
        if record is None:
            return None
        previous = record.get("status", "")
        record["status"] = status_str
        path = self.root / kind / f"{Path(record_id).stem}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        append_record(
            self.ledger_path,
            {
                "kind": "status-update",
                "record_id": record["id"],
                "previous_status": previous,
                "new_status": status_str,
                "created_by": "operator",
            },
        )
        return record


__all__ = [
    "LearnedInsight",
    "RuleChangeProposal",
    "LearningStore",
    "LearningValidationError",
    "validate_metadata",
]