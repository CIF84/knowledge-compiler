"""Provider-independent bounded semantic admission gate for SPEC-014."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Mapping

from .assertion_compilation import SourceAssertion
from .models import (
    ComparisonOperator,
    Entity,
    Origin,
    PropositionRole,
    PropositionType,
    RelationshipType,
    ValidationError,
)
from .relationships import RELATIONSHIP_DEFINITION_MAP


SEMANTIC_GATE_VERSION = "spec-014-v1"

PROPOSITION_CONTRACTS = {
    PropositionType.COMPARISON_CONDITION: {
        "proposition_type": PropositionType.COMPARISON_CONDITION.value,
        "required_roles": [
            PropositionRole.LEFT_OPERAND.value,
            PropositionRole.RIGHT_OPERAND.value,
            PropositionRole.OUTCOME.value,
        ],
        "relationship_type": RelationshipType.CAUSES.value,
        "comparison_operator": ComparisonOperator.GREATER_THAN.value,
    },
    PropositionType.TRANSFER_EVENT: {
        "proposition_type": PropositionType.TRANSFER_EVENT.value,
        "required_roles": [
            PropositionRole.EVENT.value,
            PropositionRole.OBJECT.value,
            PropositionRole.DESTINATION.value,
        ],
        "relationship_type": RelationshipType.TRANSFERS_TO.value,
        "comparison_operator": None,
    },
}


class GateVerdict(StrEnum):
    ADMIT = "ADMIT"
    TOO_STRONG = "TOO_STRONG"
    WRONG_PREDICATE = "WRONG_PREDICATE"
    WRONG_ENDPOINT = "WRONG_ENDPOINT"
    REQUIRES_STRUCTURED_PROPOSITION = "REQUIRES_STRUCTURED_PROPOSITION"
    INSUFFICIENT_FOR_CANONICALIZATION = "INSUFFICIENT_FOR_CANONICALIZATION"


class CandidateLabel(StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"


class CandidateKind(StrEnum):
    RELATIONSHIP = "RELATIONSHIP"
    PROPOSITION = "PROPOSITION"


def _nonempty(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} must be a non-empty string")
    return value


def _confidence(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{path} must be a number between 0 and 1")
    result = float(value)
    if not 0 <= result <= 1:
        raise ValidationError(f"{path} must be between 0 and 1")
    return result


@dataclass(frozen=True, slots=True)
class SemanticCandidate:
    """A canonical commitment the gate may only admit or demote."""

    id: str
    kind: CandidateKind
    statement: str
    confidence: float
    origin: Origin
    source_entity_id: str | None = None
    relationship_type: RelationshipType | None = None
    target_entity_id: str | None = None
    proposition_type: PropositionType | None = None
    role_bindings: tuple[tuple[PropositionRole, str], ...] = ()
    comparison_operator: ComparisonOperator | None = None

    def __post_init__(self) -> None:
        _nonempty(self.id, "candidate.id")
        _nonempty(self.statement, "candidate.statement")
        object.__setattr__(self, "kind", CandidateKind(self.kind))
        object.__setattr__(self, "origin", Origin(self.origin))
        object.__setattr__(self, "confidence", _confidence(self.confidence, "candidate.confidence"))
        if self.origin is not Origin.SOURCE:
            raise ValidationError("semantic gate candidates must preserve SOURCE origin")
        if self.kind is CandidateKind.RELATIONSHIP:
            _nonempty(self.source_entity_id, "candidate.source_entity_id")
            _nonempty(self.target_entity_id, "candidate.target_entity_id")
            if self.relationship_type is None:
                raise ValidationError("relationship candidate requires relationship_type")
            object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
            if self.proposition_type is not None or self.role_bindings or self.comparison_operator is not None:
                raise ValidationError("relationship candidate cannot contain proposition fields")
        else:
            if self.proposition_type is None or self.relationship_type is None:
                raise ValidationError("proposition candidate requires proposition and relationship types")
            object.__setattr__(self, "proposition_type", PropositionType(self.proposition_type))
            object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
            bindings = tuple((PropositionRole(role), entity_id) for role, entity_id in self.role_bindings)
            if not bindings:
                raise ValidationError("proposition candidate requires role bindings")
            object.__setattr__(self, "role_bindings", bindings)
            if self.comparison_operator is not None:
                object.__setattr__(
                    self, "comparison_operator", ComparisonOperator(self.comparison_operator)
                )
            if self.source_entity_id is not None or self.target_entity_id is not None:
                raise ValidationError("proposition candidate cannot contain relationship endpoints")

    def to_dict(self) -> dict[str, Any]:
        base: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind.value,
            "statement": self.statement,
            "confidence": self.confidence,
            "origin": self.origin.value,
        }
        if self.kind is CandidateKind.RELATIONSHIP:
            base.update({
                "source_entity_id": self.source_entity_id,
                "relationship_type": self.relationship_type.value,
                "target_entity_id": self.target_entity_id,
            })
        else:
            base.update({
                "proposition_type": self.proposition_type.value,
                "role_bindings": [
                    {"role": role.value, "entity_id": entity_id}
                    for role, entity_id in self.role_bindings
                ],
                "relationship_type": self.relationship_type.value,
                "comparison_operator": (
                    self.comparison_operator.value if self.comparison_operator else None
                ),
            })
        return base

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SemanticCandidate:
        if not isinstance(value, Mapping):
            raise ValidationError("candidate must be an object")
        common = {"id", "kind", "statement", "confidence", "origin", "relationship_type"}
        kind = CandidateKind(value.get("kind"))
        if kind is CandidateKind.RELATIONSHIP:
            allowed = common | {"source_entity_id", "target_entity_id"}
            if set(value) != allowed:
                raise ValidationError("relationship candidate fields do not match the fixed contract")
            return cls(
                id=value.get("id"), kind=kind, statement=value.get("statement"),
                confidence=value.get("confidence"), origin=value.get("origin"),
                source_entity_id=value.get("source_entity_id"),
                relationship_type=value.get("relationship_type"),
                target_entity_id=value.get("target_entity_id"),
            )
        allowed = common | {"proposition_type", "role_bindings", "comparison_operator"}
        if set(value) != allowed:
            raise ValidationError("proposition candidate fields do not match the fixed contract")
        bindings = value.get("role_bindings")
        if not isinstance(bindings, list) or any(
            not isinstance(item, Mapping) or set(item) != {"role", "entity_id"}
            for item in bindings
        ):
            raise ValidationError("proposition role bindings do not match the fixed contract")
        return cls(
            id=value.get("id"), kind=kind, statement=value.get("statement"),
            confidence=value.get("confidence"), origin=value.get("origin"),
            relationship_type=value.get("relationship_type"),
            proposition_type=value.get("proposition_type"),
            role_bindings=tuple((item["role"], item["entity_id"]) for item in bindings),
            comparison_operator=value.get("comparison_operator"),
        )


@dataclass(frozen=True, slots=True)
class PreservationFallback:
    kind: str
    assertion_id: str
    statement: str

    def __post_init__(self) -> None:
        if self.kind not in {"CLAIM", "SOURCE_ASSERTION"}:
            raise ValidationError("fallback kind must be CLAIM or SOURCE_ASSERTION")
        _nonempty(self.assertion_id, "fallback.assertion_id")
        _nonempty(self.statement, "fallback.statement")


@dataclass(frozen=True, slots=True)
class GatePacketItem:
    packet_candidate_id: str
    label: CandidateLabel
    expected_category: str
    assertion: SourceAssertion
    participant_symbols: tuple[Entity, ...]
    candidate_symbols: tuple[Entity, ...]
    candidate: SemanticCandidate
    canonical_contract: Mapping[str, Any]
    independent_review_note: str
    control_source: Mapping[str, Any]
    fallback: PreservationFallback

    def __post_init__(self) -> None:
        _nonempty(self.packet_candidate_id, "packet_candidate_id")
        object.__setattr__(self, "label", CandidateLabel(self.label))
        _nonempty(self.expected_category, "expected_category")
        _nonempty(self.independent_review_note, "independent_review_note")
        symbols = tuple(self.participant_symbols)
        if not symbols or len({item.id for item in symbols}) != len(symbols):
            raise ValidationError("participant symbols must be non-empty and unique")
        if tuple(sorted(item.id for item in symbols)) != tuple(item.id for item in symbols):
            raise ValidationError("participant symbols must be sorted deterministically")
        if set(self.assertion.participant_entity_ids) != {item.id for item in symbols}:
            raise ValidationError("participant symbols must exactly match the grounded assertion")
        candidate_symbols = tuple(self.candidate_symbols)
        if not candidate_symbols or tuple(sorted(item.id for item in candidate_symbols)) != tuple(
            item.id for item in candidate_symbols
        ):
            raise ValidationError("candidate symbols must be non-empty and sorted deterministically")
        candidate_ids = (
            {self.candidate.source_entity_id, self.candidate.target_entity_id}
            if self.candidate.kind is CandidateKind.RELATIONSHIP
            else {entity_id for _role, entity_id in self.candidate.role_bindings}
        )
        if candidate_ids != {item.id for item in candidate_symbols}:
            raise ValidationError("candidate symbols must exactly match canonical references")
        if self.label is CandidateLabel.POSITIVE and self.expected_category != "SUPPORTED":
            raise ValidationError("positive candidates must be independently SUPPORTED")
        if self.label is CandidateLabel.NEGATIVE and self.expected_category == "SUPPORTED":
            raise ValidationError("negative candidates cannot be independently SUPPORTED")
        object.__setattr__(self, "participant_symbols", symbols)
        object.__setattr__(self, "candidate_symbols", candidate_symbols)
        object.__setattr__(self, "canonical_contract", dict(self.canonical_contract))
        object.__setattr__(self, "control_source", dict(self.control_source))

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_candidate_id": self.packet_candidate_id,
            "label": self.label.value,
            "expected_category": self.expected_category,
            "assertion": self.assertion.to_dict(),
            "participant_symbols": [asdict(item) for item in self.participant_symbols],
            "candidate_symbols": [asdict(item) for item in self.candidate_symbols],
            "candidate": self.candidate.to_dict(),
            "canonical_contract": dict(self.canonical_contract),
            "independent_review_note": self.independent_review_note,
            "control_source": dict(self.control_source),
            "fallback": asdict(self.fallback),
        }

    def to_gate_input(self) -> dict[str, Any]:
        """Exclude benchmark labels and review answers from the independent judge input."""
        return {
            "packet_candidate_id": self.packet_candidate_id,
            "grounded_assertion": self.assertion.to_dict(),
            "participant_symbols": [asdict(item) for item in self.participant_symbols],
            "candidate_symbols": [asdict(item) for item in self.candidate_symbols],
            "candidate": self.candidate.to_dict(),
            "canonical_contract": dict(self.canonical_contract),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> GatePacketItem:
        if not isinstance(value, Mapping) or set(value) != {
            "packet_candidate_id", "label", "expected_category", "assertion",
            "participant_symbols", "candidate_symbols", "candidate", "canonical_contract",
            "independent_review_note", "control_source", "fallback",
        }:
            raise ValidationError("gate packet item fields do not match the fixed contract")
        raw_assertion = value.get("assertion")
        if not isinstance(raw_assertion, Mapping):
            raise ValidationError("gate packet assertion must be an object")
        evidence = raw_assertion.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValidationError("gate packet assertion requires evidence")
        document_id = evidence[0].get("document_id")
        raw_fallback = value.get("fallback")
        if not isinstance(raw_fallback, Mapping) or set(raw_fallback) != {
            "kind", "assertion_id", "statement"
        }:
            raise ValidationError("gate packet fallback fields do not match the fixed contract")
        return cls(
            packet_candidate_id=value.get("packet_candidate_id"),
            label=value.get("label"),
            expected_category=value.get("expected_category"),
            assertion=SourceAssertion.from_dict(raw_assertion, document_id),
            participant_symbols=tuple(
                Entity.from_dict(item) for item in value.get("participant_symbols", ())
            ),
            candidate_symbols=tuple(
                Entity.from_dict(item) for item in value.get("candidate_symbols", ())
            ),
            candidate=SemanticCandidate.from_dict(value.get("candidate")),
            canonical_contract=value.get("canonical_contract", {}),
            independent_review_note=value.get("independent_review_note"),
            control_source=value.get("control_source", {}),
            fallback=PreservationFallback(
                raw_fallback.get("kind"), raw_fallback.get("assertion_id"),
                raw_fallback.get("statement"),
            ),
        )


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class GatePacket:
    packet_id: str
    items: tuple[GatePacketItem, ...]
    source_metadata: Mapping[str, Any]
    symbol_table_sha256: str
    frozen_symbol_ids: tuple[str, ...]
    packet_hash: str = ""

    def __post_init__(self) -> None:
        _nonempty(self.packet_id, "packet_id")
        items = tuple(self.items)
        ids = tuple(item.packet_candidate_id for item in items)
        if not items or len(ids) != len(set(ids)):
            raise ValidationError("gate packet candidate IDs must be non-empty and unique")
        if ids != tuple(sorted(ids)):
            raise ValidationError("gate packet candidates must use deterministic ID order")
        if not any(item.label is CandidateLabel.POSITIVE for item in items):
            raise ValidationError("gate packet requires positive controls")
        if not any(item.label is CandidateLabel.NEGATIVE for item in items):
            raise ValidationError("gate packet requires negative controls")
        frozen_ids = tuple(self.frozen_symbol_ids)
        if not frozen_ids or frozen_ids != tuple(sorted(set(frozen_ids))):
            raise ValidationError("frozen symbol IDs must be non-empty, unique, and sorted")
        object.__setattr__(self, "items", items)
        object.__setattr__(self, "frozen_symbol_ids", frozen_ids)
        object.__setattr__(self, "source_metadata", dict(self.source_metadata))
        expected = self.compute_hash()
        if self.packet_hash and self.packet_hash != expected:
            raise ValidationError("gate packet hash does not match canonical contents")
        object.__setattr__(self, "packet_hash", expected)

    def _body(self) -> dict[str, Any]:
        return {
            "spec": "SPEC-014",
            "packet_version": SEMANTIC_GATE_VERSION,
            "packet_id": self.packet_id,
            "source_metadata": dict(self.source_metadata),
            "symbol_table_sha256": self.symbol_table_sha256,
            "frozen_symbol_ids": list(self.frozen_symbol_ids),
            "items": [item.to_dict() for item in self.items],
        }

    def compute_hash(self) -> str:
        return hashlib.sha256(_canonical_json(self._body())).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {**self._body(), "packet_hash": self.packet_hash}

    def to_gate_input(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "packet_hash": self.packet_hash,
            "candidates": [item.to_gate_input() for item in self.items],
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> GatePacket:
        if not isinstance(value, Mapping) or set(value) != {
            "spec", "packet_version", "packet_id", "source_metadata",
            "symbol_table_sha256", "frozen_symbol_ids", "items", "packet_hash",
        }:
            raise ValidationError("gate packet fields do not match the fixed contract")
        if value.get("spec") != "SPEC-014" or value.get("packet_version") != SEMANTIC_GATE_VERSION:
            raise ValidationError("gate packet spec/version mismatch")
        items = value.get("items")
        if not isinstance(items, list):
            raise ValidationError("gate packet items must be an array")
        return cls(
            packet_id=value.get("packet_id"),
            items=tuple(GatePacketItem.from_dict(item) for item in items),
            source_metadata=value.get("source_metadata", {}),
            symbol_table_sha256=value.get("symbol_table_sha256"),
            frozen_symbol_ids=tuple(value.get("frozen_symbol_ids", ())),
            packet_hash=value.get("packet_hash"),
        )


@dataclass(frozen=True, slots=True)
class GateDecision:
    packet_candidate_id: str
    verdict: GateVerdict
    rationale: str

    def __post_init__(self) -> None:
        _nonempty(self.packet_candidate_id, "decision.packet_candidate_id")
        object.__setattr__(self, "verdict", GateVerdict(self.verdict))
        _nonempty(self.rationale, "decision.rationale")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> GateDecision:
        if not isinstance(value, Mapping) or set(value) != {
            "packet_candidate_id", "verdict", "rationale"
        }:
            raise ValidationError("gate decision may contain only ID, verdict, and rationale")
        return cls(value.get("packet_candidate_id"), value.get("verdict"), value.get("rationale"))


@dataclass(frozen=True, slots=True)
class GateResult:
    decisions: tuple[GateDecision, ...]
    metadata: Mapping[str, Any]

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], packet: GatePacket) -> GateResult:
        if not isinstance(value, Mapping) or set(value) - {"decisions", "metadata"}:
            raise ValidationError("gate result has unknown fields")
        raw = value.get("decisions")
        if not isinstance(raw, list):
            raise ValidationError("gate decisions must be an array")
        decisions = tuple(GateDecision.from_dict(item) for item in raw)
        expected = {item.packet_candidate_id for item in packet.items}
        actual = [item.packet_candidate_id for item in decisions]
        unknown = sorted(set(actual) - expected)
        missing = sorted(expected - set(actual))
        duplicates = sorted(item for item in set(actual) if actual.count(item) > 1)
        if unknown or missing or duplicates:
            raise ValidationError(
                "gate must decide every frozen candidate exactly once; "
                f"unknown={unknown}, missing={missing}, duplicates={duplicates}"
            )
        return cls(
            tuple(sorted(decisions, key=lambda item: item.packet_candidate_id)),
            dict(value.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "decisions": [asdict(item) for item in self.decisions],
            "metadata": dict(self.metadata),
        }


def validate_packet_contracts(packet: GatePacket, known_symbol_ids: frozenset[str]) -> None:
    """Apply only schema-level hard checks, never broad semantic heuristics."""
    for item in packet.items:
        if item.assertion.origin is not Origin.SOURCE:
            raise ValidationError("gate packet assertion must preserve SOURCE provenance")
        unknown_participants = set(item.assertion.participant_entity_ids) - known_symbol_ids
        if unknown_participants:
            raise ValidationError(f"gate packet has unknown assertion participants: {sorted(unknown_participants)}")
        candidate = item.candidate
        if candidate.kind is CandidateKind.RELATIONSHIP:
            unknown_endpoints = {
                candidate.source_entity_id, candidate.target_entity_id
            } - known_symbol_ids
            if unknown_endpoints:
                raise ValidationError(f"gate packet has unknown endpoints: {sorted(unknown_endpoints)}")
            expected_contract = asdict(RELATIONSHIP_DEFINITION_MAP[candidate.relationship_type])
        else:
            unknown_roles = {entity_id for _role, entity_id in candidate.role_bindings} - known_symbol_ids
            if unknown_roles:
                raise ValidationError(f"gate packet has unknown proposition roles: {sorted(unknown_roles)}")
            expected_contract = PROPOSITION_CONTRACTS[candidate.proposition_type]
            if sorted(role.value for role, _entity_id in candidate.role_bindings) != sorted(
                expected_contract["required_roles"]
            ):
                raise ValidationError("proposition candidate does not satisfy required roles")
            if candidate.relationship_type.value != expected_contract["relationship_type"]:
                raise ValidationError("proposition candidate uses the wrong relationship type")
            comparison = candidate.comparison_operator.value if candidate.comparison_operator else None
            if comparison != expected_contract["comparison_operator"]:
                raise ValidationError("proposition candidate uses the wrong comparison operator")
        if dict(item.canonical_contract) != expected_contract:
            raise ValidationError(f"candidate {item.packet_candidate_id!r} has the wrong canonical contract")


def apply_gate_decisions(packet: GatePacket, result: GateResult) -> dict[str, Any]:
    """Demonstrate the isolated ADMIT/demote seam without rewriting candidates."""
    by_id = {item.packet_candidate_id: item for item in packet.items}
    admitted = []
    demoted = []
    for decision in result.decisions:
        item = by_id[decision.packet_candidate_id]
        if decision.verdict is GateVerdict.ADMIT:
            admitted.append({
                "packet_candidate_id": item.packet_candidate_id,
                "candidate": item.candidate.to_dict(),
            })
        else:
            demoted.append({
                "packet_candidate_id": item.packet_candidate_id,
                "rejected_candidate": item.candidate.to_dict(),
                "verdict": decision.verdict.value,
                "preserved_as": asdict(item.fallback),
            })
    return {
        "gate_version": SEMANTIC_GATE_VERSION,
        "admitted": admitted,
        "demoted": demoted,
        "source_meaning_preserved_for_all_demotions": all(
            bool(item["preserved_as"]["statement"].strip()) for item in demoted
        ),
        "candidate_rewrites": 0,
        "entities_minted": 0,
        "evidence_created_or_changed": 0,
    }


def aggregate_gate_metrics(packet: GatePacket, result: GateResult) -> dict[str, Any]:
    labels = {item.packet_candidate_id: item for item in packet.items}
    true_admits = false_admits = true_rejects = false_rejects = 0
    distributions: dict[str, dict[str, int]] = {}
    for decision in result.decisions:
        item = labels[decision.packet_candidate_id]
        admitted = decision.verdict is GateVerdict.ADMIT
        if item.label is CandidateLabel.POSITIVE:
            true_admits += int(admitted)
            false_rejects += int(not admitted)
        else:
            false_admits += int(admitted)
            true_rejects += int(not admitted)
        category = distributions.setdefault(item.expected_category, {})
        category[decision.verdict.value] = category.get(decision.verdict.value, 0) + 1
    positive = true_admits + false_rejects
    negative = false_admits + true_rejects
    admits = true_admits + false_admits
    total = positive + negative
    ratio = lambda numerator, denominator: numerator / denominator if denominator else "NOT_AVAILABLE"
    return {
        "positive_candidate_count": positive,
        "negative_candidate_count": negative,
        "true_admits": true_admits,
        "false_admits": false_admits,
        "true_rejects_or_demotions": true_rejects,
        "false_rejects": false_rejects,
        "admit_precision": ratio(true_admits, admits),
        "justified_admission_recall": ratio(true_admits, positive),
        "negative_rejection_rate": ratio(true_rejects, negative),
        "overall_classification_agreement": ratio(true_admits + true_rejects, total),
        "verdict_distribution_by_expected_category": distributions,
    }


def select_experimental_verdict(
    metrics: Mapping[str, Any], *, operational_failure: bool = False
) -> str:
    """Apply thresholds frozen before live evaluation; not a production policy."""
    if operational_failure:
        return "INCONCLUSIVE"
    recall = metrics["justified_admission_recall"]
    negative_rate = metrics["negative_rejection_rate"]
    precision = metrics["admit_precision"]
    agreement = metrics["overall_classification_agreement"]
    if recall >= 2 / 3 and negative_rate >= 5 / 6 and precision >= 2 / 3:
        return "GATE_BETTER"
    if recall < 2 / 3 and negative_rate >= 2 / 3:
        return "GATE_TOO_CONSERVATIVE"
    if agreement < 0.6:
        return "GATE_UNRELIABLE"
    return "NO_MEANINGFUL_IMPROVEMENT"
