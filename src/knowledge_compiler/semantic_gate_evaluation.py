"""Frozen-packet construction and one-call evaluation for SPEC-014."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Mapping

from .assertion_compilation import SourceAssertion, deterministic_assertion_id
from .models import Entity, KnowledgeModel, Origin, SourceSpan, ValidationError
from .openai_extractor import DEFAULT_MODEL
from .openai_extractor import resolve_evidence_quote
from .openai_semantic_gate import GATE_PROMPT_VERSION, OpenAISemanticGate
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .semantic_gate import (
    SEMANTIC_GATE_VERSION,
    CandidateKind,
    CandidateLabel,
    GatePacket,
    GatePacketItem,
    GateResult,
    GateVerdict,
    PreservationFallback,
    SemanticCandidate,
    aggregate_gate_metrics,
    apply_gate_decisions,
    select_experimental_verdict,
    validate_packet_contracts,
)
from .staged_compilation import SymbolTable


EVALUATION_VERSION = "spec-014-v1"
PACKET_ID = "spec-014-quantum-semantic-gate-v1"

NEGATIVE_CASES = (
    ("negative-r1", "r1", "assertion-2fcb725a5b198912", "OVERSTATED_CAUSALITY"),
    ("negative-r2", "r2", "assertion-6bb1fee4b6754585", "WRONG_PREDICATE"),
    ("negative-r5", "r5", "assertion-c2c5a86b98108470", "WRONG_PREDICATE"),
    ("negative-r9", "r9", "assertion-88adf8f8ab0e82aa", "IMPRECISE_ENDPOINT"),
    ("negative-r12", "r12", "assertion-bc3d8941f16641ef", "IMPRECISE_ENDPOINT"),
    ("negative-r14", "r14", "assertion-d1cadc9675bc9732", "WRONG_PREDICATE"),
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_assertions(path: Path) -> dict[str, SourceAssertion]:
    value = _read_json(path)
    result = {}
    for item in value.get("assertions", []):
        evidence = item.get("evidence", [])
        if not evidence:
            raise ValidationError("preserved grounded assertion lacks evidence")
        assertion = SourceAssertion.from_dict(item, evidence[0]["document_id"])
        result[assertion.id] = assertion
    return result


def _relationship_candidate(
    candidate_id: str, value: Mapping[str, Any]
) -> SemanticCandidate:
    return SemanticCandidate(
        id=candidate_id,
        kind=CandidateKind.RELATIONSHIP,
        statement=value["statement"],
        confidence=value["confidence"],
        origin=value.get("origin", Origin.SOURCE.value),
        source_entity_id=value["source_entity_id"],
        relationship_type=value["relationship_type"],
        target_entity_id=value["target_entity_id"],
    )


def _participant_symbols(assertion: SourceAssertion, symbols: Mapping[str, Entity]) -> tuple[Entity, ...]:
    missing = sorted(set(assertion.participant_entity_ids) - set(symbols))
    if missing:
        raise ValidationError(f"preserved assertion references missing frozen symbols: {missing}")
    return tuple(symbols[item] for item in sorted(assertion.participant_entity_ids))


def _candidate_symbols(candidate: SemanticCandidate, symbols: Mapping[str, Entity]) -> tuple[Entity, ...]:
    ids = (
        {candidate.source_entity_id, candidate.target_entity_id}
        if candidate.kind is CandidateKind.RELATIONSHIP
        else {entity_id for _role, entity_id in candidate.role_bindings}
    )
    missing = sorted(ids - set(symbols))
    if missing:
        raise ValidationError(f"preserved candidate references missing frozen symbols: {missing}")
    return tuple(symbols[item] for item in sorted(ids))


def build_frozen_gate_packet(spec_013_dir: Path, spec_012_dir: Path) -> GatePacket:
    """Build labels entirely offline from the preserved independent reviews."""
    grounded = _source_assertions(spec_013_dir / "grounded-assertions.json")
    parent = KnowledgeModel.from_dict(_read_json(spec_013_dir / "parent.knowledge.json"))
    symbol_path = spec_013_dir / "symbol-table.json"
    symbol_table = SymbolTable.from_dict(_read_json(symbol_path))
    symbols = {item.id: item for item in symbol_table.entities}
    source = _read_json(spec_013_dir / "source-metadata.json")
    source_identity = {
        key: source[key] for key in (
            "title", "permanent_url", "revision_id", "revision_timestamp",
            "normalized_sha256", "word_count", "character_count",
        )
    }

    canonicalization = _read_json(spec_013_dir / "canonicalization-result.json")
    positive_values = canonicalization["normalized_proposal"]["relationships"]
    positive_review = {
        item["id"]: item
        for item in _read_json(spec_013_dir / "canonical-semantic-review.json")["items"]
    }
    spec_013_claims = {
        item["assertion_id"]: item
        for item in canonicalization["normalized_proposal"]["claims"]
    }
    items: list[GatePacketItem] = []
    for value in positive_values:
        assertion_id = value["assertion_id"]
        relationship_id = f"relationship-{assertion_id.removeprefix('assertion-')}"
        review = positive_review.get(relationship_id)
        if review is None or review["classification"] != "SUPPORTED":
            raise ValidationError("positive packet may contain only independently supported SPEC-013 items")
        assertion = grounded[assertion_id]
        candidate = _relationship_candidate(relationship_id, value)
        items.append(GatePacketItem(
            packet_candidate_id=f"positive-{relationship_id}",
            label=CandidateLabel.POSITIVE,
            expected_category=review["classification"],
            assertion=assertion,
            participant_symbols=_participant_symbols(assertion, symbols),
            candidate_symbols=_candidate_symbols(candidate, symbols),
            candidate=candidate,
            canonical_contract=asdict(RELATIONSHIP_DEFINITION_MAP[candidate.relationship_type]),
            independent_review_note=review["notes"],
            control_source={
                "artifact": "SPEC-013 canonicalization-result.json and canonical-semantic-review.json",
                "item_id": relationship_id,
            },
            fallback=PreservationFallback(
                "SOURCE_ASSERTION", assertion.id, assertion.statement
            ),
        ))

    raw_negative = {
        item["id"]: item
        for item in _read_json(spec_012_dir / "pass-2-result.json")["raw_proposal"]["relationships"]
    }
    negative_review = {
        item["id"]: item
        for item in _read_json(spec_012_dir / "staged-semantic-review.json")["items"]
        if item["kind"] == "relationship"
    }
    for packet_id, control_id, assertion_id, expected_category in NEGATIVE_CASES:
        value = raw_negative[control_id]
        review = negative_review[control_id]
        if review["classification"] != expected_category:
            raise ValidationError(f"preserved review category changed for {control_id}")
        if control_id == "r2":
            quote = value["evidence"][0]["quote"]
            span = SourceSpan.from_dict(
                resolve_evidence_quote(parent.document, quote), parent.document.id
            )
            participants = ("quantum-mechanics", "superfluidity")
            statement = "Quantum mechanics can explain superfluidity."
            assertion = SourceAssertion(
                deterministic_assertion_id(statement, participants, (span,)),
                statement, participants, (span,), Origin.SOURCE,
            )
        else:
            assertion = grounded[assertion_id]
        candidate = _relationship_candidate(control_id, value)
        claim = spec_013_claims.get(assertion_id)
        if claim is None:
            raise ValidationError(f"negative control {control_id} lacks SPEC-013 claim fallback")
        fallback = (
            PreservationFallback("SOURCE_ASSERTION", assertion.id, assertion.statement)
            if control_id == "r2"
            else PreservationFallback("CLAIM", assertion.id, claim["statement"])
        )
        items.append(GatePacketItem(
            packet_candidate_id=packet_id,
            label=CandidateLabel.NEGATIVE,
            expected_category=expected_category,
            assertion=assertion,
            participant_symbols=_participant_symbols(assertion, symbols),
            candidate_symbols=_candidate_symbols(candidate, symbols),
            candidate=candidate,
            canonical_contract=asdict(RELATIONSHIP_DEFINITION_MAP[candidate.relationship_type]),
            independent_review_note=review["notes"],
            control_source={
                "artifact": "SPEC-012 pass-2-result.json and staged-semantic-review.json",
                "item_id": control_id,
                "candidate_semantics_preserved_without_rewrite": True,
            },
            fallback=fallback,
        ))

    packet = GatePacket(
        packet_id=PACKET_ID,
        items=tuple(sorted(items, key=lambda item: item.packet_candidate_id)),
        source_metadata=source_identity,
        symbol_table_sha256=_sha256(symbol_path),
        frozen_symbol_ids=tuple(sorted(symbol_table.ids)),
    )
    validate_packet_contracts(packet, symbol_table.ids)
    return packet


def prepare_gate_evaluation(
    spec_013_dir: Path, spec_012_dir: Path, output_dir: Path
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    packet = build_frozen_gate_packet(spec_013_dir, spec_012_dir)
    _write_json(output_dir / "gate-packet.json", packet.to_dict())
    summary = {
        "spec": "SPEC-014",
        "evaluation_version": EVALUATION_VERSION,
        "status": "FROZEN_AWAITING_LIVE_GATE",
        "packet_id": packet.packet_id,
        "packet_hash": packet.packet_hash,
        "positive_candidate_count": sum(
            item.label is CandidateLabel.POSITIVE for item in packet.items
        ),
        "negative_candidate_count": sum(
            item.label is CandidateLabel.NEGATIVE for item in packet.items
        ),
        "candidate_count": len(packet.items),
        "gate_call_budget": 1,
        "verdict_vocabulary": [item.value for item in GateVerdict],
        "benchmark_labels_excluded_from_live_input": True,
        "thresholds_frozen_before_live_output": {
            "GATE_BETTER": {
                "justified_admission_recall_minimum": 2 / 3,
                "negative_rejection_rate_minimum": 5 / 6,
                "admit_precision_minimum": 2 / 3,
            },
            "GATE_TOO_CONSERVATIVE": {
                "justified_admission_recall_below": 2 / 3,
                "negative_rejection_rate_minimum": 2 / 3,
            },
            "GATE_UNRELIABLE": {"overall_classification_agreement_below": 0.6},
            "fallback": "NO_MEANINGFUL_IMPROVEMENT",
            "operational_failure": "INCONCLUSIVE",
        },
    }
    _write_json(output_dir / "packet-summary.json", summary)
    (output_dir / "README.md").write_text(
        "# SPEC-014 independent semantic gate\n\n"
        "The nine-candidate packet is frozen and awaits the single authorized live gate call. "
        "Expected labels are committed in `gate-packet.json` for auditability but excluded from "
        "the provider input by trusted code.\n",
        encoding="utf-8",
    )
    return summary


def _usage(metadata: Mapping[str, Any]) -> dict[str, int]:
    raw = metadata.get("usage", {})
    return {key: int(raw.get(key, 0)) for key in ("input_tokens", "output_tokens", "total_tokens")}


def _disagreements(packet: GatePacket, result: GateResult) -> list[dict[str, Any]]:
    items = {item.packet_candidate_id: item for item in packet.items}
    result_items = []
    for decision in result.decisions:
        expected_admit = items[decision.packet_candidate_id].label is CandidateLabel.POSITIVE
        actual_admit = decision.verdict.value == "ADMIT"
        if expected_admit != actual_admit:
            result_items.append({
                "packet_candidate_id": decision.packet_candidate_id,
                "independent_label": items[decision.packet_candidate_id].label.value,
                "expected_category": items[decision.packet_candidate_id].expected_category,
                "gate_verdict": decision.verdict.value,
                "gate_rationale": decision.rationale,
            })
    return result_items


def run_gate_evaluation(
    packet_path: Path,
    output_dir: Path,
    *,
    model: str = DEFAULT_MODEL,
    gate_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    packet = GatePacket.from_dict(_read_json(packet_path))
    validate_packet_contracts(packet, frozenset(packet.frozen_symbol_ids))
    frozen_output = output_dir / "gate-packet.json"
    if frozen_output.resolve() != packet_path.resolve():
        if frozen_output.exists() and frozen_output.read_bytes() != packet_path.read_bytes():
            raise ValidationError("output gate packet differs from the explicitly supplied frozen packet")
        frozen_output.write_bytes(packet_path.read_bytes())
    gate = gate_factory() if gate_factory else OpenAISemanticGate(model=model)
    started_at = _utc_now()
    start = time.perf_counter()
    try:
        result = gate.judge(packet)
    except Exception as exc:
        elapsed = round(time.perf_counter() - start, 3)
        metadata = dict(getattr(gate, "last_metadata", {}))
        raw = getattr(gate, "last_raw", None)
        _write_json(output_dir / "gate-result.json", {
            "spec": "SPEC-014", "outcome": "GATE_CALL_OR_VALIDATION_FAILED",
            "raw_proposal": raw, "provider_metadata": metadata,
            "validation_failure": {"type": type(exc).__name__, "message": str(exc)},
        })
        history = {
            "spec": "SPEC-014", "attempts": [{
                "sequence": 1, "stage": "SEMANTIC_ADMISSION_GATE",
                "started_at": started_at, "completed_at": _utc_now(),
                "runtime_seconds": elapsed, "outcome": "FAILED",
                "provider_call_attempted": True,
                "provider": metadata.get("provider", "openai"),
                "requested_model": metadata.get("requested_model", model),
                "actual_model": metadata.get("model"),
                "provider_request_id": metadata.get("provider_request_id"),
                "prompt_version": metadata.get("prompt_version", GATE_PROMPT_VERSION),
                "usage": _usage(metadata), "cost": "NOT_AVAILABLE",
                "error_type": type(exc).__name__, "error": str(exc),
                "raw_rejected_output_preserved": raw is not None,
            }],
            "live_call_count": 1, "semantic_retry_count": 0,
            "automatic_retry_count": 0, "hidden_retries": False,
            "prompt_repair_after_live_output": False, "candidate_rewrites": 0,
            "external_enrichment": False, "additional_models_or_agents": 0,
        }
        _write_json(output_dir / "run-history.json", history)
        report = {
            "spec": "SPEC-014", "evaluation_version": EVALUATION_VERSION,
            "outcome": "GATE_CALL_OR_VALIDATION_FAILED", "verdict": "INCONCLUSIVE",
            "packet_id": packet.packet_id, "packet_hash": packet.packet_hash,
            "candidate_count": len(packet.items), "failure": str(exc),
            "live_call_count": 1, "retry_count": 0,
            "authoritative_monetary_cost": "NOT_AVAILABLE",
        }
        _write_json(output_dir / "report.json", report)
        raise

    elapsed = round(time.perf_counter() - start, 3)
    metadata = dict(result.metadata)
    raw = dict(getattr(gate, "last_raw", {}) or {})
    _write_json(output_dir / "gate-result.json", {
        "spec": "SPEC-014", "outcome": "SUCCESS",
        "prompt_version": GATE_PROMPT_VERSION,
        "raw_proposal": raw,
        "normalized_result": result.to_dict(),
        "provider_metadata": metadata,
    })
    integration = apply_gate_decisions(packet, result)
    _write_json(output_dir / "admission-result.json", integration)
    metrics = aggregate_gate_metrics(packet, result)
    _write_json(output_dir / "metrics.json", metrics)
    verdict = select_experimental_verdict(metrics)
    disagreements = _disagreements(packet, result)
    multi_agent = (
        "NOT_JUSTIFIED" if verdict == "GATE_BETTER"
        else "STILL_UNRESOLVED" if verdict in {"GATE_TOO_CONSERVATIVE", "NO_MEANINGFUL_IMPROVEMENT"}
        else "NOT_JUSTIFIED_BY_THIS_RESULT"
    )
    comparison = {
        "spec": "SPEC-014", "control": "SPEC-013 accepted assertion-first result",
        "control_canonical_precision": 1.0,
        "control_compilation_calls": 2,
        "control_compilation_usage": {
            "input_tokens": 18807, "output_tokens": 3606, "total_tokens": 22413,
        },
        "control_compilation_runtime_seconds": 30.33,
        "incremental_gate": {
            "calls": 1, "usage": _usage(metadata), "runtime_seconds": elapsed,
            "authoritative_monetary_cost": "NOT_AVAILABLE",
        },
        "metrics": metrics,
        "notable_disagreements": disagreements,
        "verdict": verdict,
        "multi_agent_deliberation": multi_agent,
    }
    _write_json(output_dir / "comparison.json", comparison)
    history = {
        "spec": "SPEC-014", "attempts": [{
            "sequence": 1, "stage": "SEMANTIC_ADMISSION_GATE",
            "started_at": started_at, "completed_at": _utc_now(),
            "runtime_seconds": elapsed, "outcome": "SUCCESS",
            "provider_call_attempted": True, "provider": metadata.get("provider"),
            "requested_model": metadata.get("requested_model", model),
            "actual_model": metadata.get("model", model),
            "provider_request_id": metadata.get("provider_request_id"),
            "prompt_version": metadata.get("prompt_version", GATE_PROMPT_VERSION),
            "usage": _usage(metadata), "cost": "NOT_AVAILABLE",
            "raw_rejected_output_preserved": False,
        }],
        "live_call_count": 1, "semantic_retry_count": 0,
        "automatic_retry_count": 0, "hidden_retries": False,
        "prompt_repair_after_live_output": False, "candidate_rewrites": 0,
        "external_enrichment": False, "additional_models_or_agents": 0,
    }
    _write_json(output_dir / "run-history.json", history)
    report = {
        "spec": "SPEC-014", "evaluation_version": EVALUATION_VERSION,
        "gate_version": SEMANTIC_GATE_VERSION, "prompt_version": GATE_PROMPT_VERSION,
        "outcome": "COMPLETE", "verdict": verdict,
        "packet_id": packet.packet_id, "packet_hash": packet.packet_hash,
        "packet_size": len(packet.items),
        "provider": metadata.get("provider"), "requested_model": model,
        "actual_model": metadata.get("model", model),
        "provider_request_id": metadata.get("provider_request_id"),
        "usage": _usage(metadata), "runtime_seconds": elapsed,
        "authoritative_monetary_cost": "NOT_AVAILABLE",
        "metrics": metrics, "notable_disagreements": disagreements,
        "safety": integration,
        "knowledge_model_changes": [], "relationship_vocabulary_changes": [],
        "proposition_vocabulary_changes": [], "grounding_rule_changes": [],
        "dependencies_added": [], "dependencies_removed": [],
        "multi_agent_deliberation": multi_agent,
        "recommended_next_discriminator": (
            "Evaluate production integration of the isolated gate, then return to the "
            "assertion-aware representation bottleneck; do not add multi-agent deliberation."
            if verdict == "GATE_BETTER" else
            "Inspect the preserved disagreement pattern before changing context or agent count."
        ),
    }
    _write_json(output_dir / "report.json", report)
    (output_dir / "README.md").write_text(
        "# SPEC-014 independent semantic gate\n\n"
        f"Final verdict: `{verdict}`. The frozen packet contains "
        f"{metrics['positive_candidate_count']} positive and "
        f"{metrics['negative_candidate_count']} negative candidates. Read `gate-packet.json`, "
        "`gate-result.json`, `metrics.json`, `comparison.json`, and `run-history.json`.\n",
        encoding="utf-8",
    )
    return report
