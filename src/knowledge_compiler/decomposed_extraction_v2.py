"""SPEC-051 Candidate B v2 seam; Candidate B v1 remains byte-frozen.

Only Stage-2 proposition shape and generic semantic omission differ. Provider
proposals are retained before lossless variant-to-canonical normalization.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from .decomposed_extraction import (
    CandidateBRun,
    DecomposedExtractionAdapter,
    FrozenEntityInventory,
    StageAttempt,
    StageExecutionError,
    StageName,
    run_candidate_b,
    stable_hash,
    validate_semantic_structure,
)
from .models import (
    EntityType,
    KnowledgeModel,
    SourceDocument,
    ValidationError,
)


CANDIDATE_B_V2_VERSION = "spec-051-candidate-b-v2"
STAGE2_V2_VERSION = "spec-051-semantic-structure-v2"
STAGE3_V2_VERSION = "spec-051-claim-evidence-binding-v2"


def _exact(value: Any, fields: set[str], path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{path} must be an object")
    if set(value) != fields:
        raise ValidationError(
            f"{path} must contain exactly {sorted(fields)}; "
            f"missing={sorted(fields - set(value))}, unknown={sorted(set(value) - fields)}"
        )
    return value


def _items(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{path} must be an array")
    return value


def _endpoint(value: Any, known: frozenset[str], path: str) -> str:
    if not isinstance(value, str) or value not in known:
        raise ValidationError(f"{path} must use an exact frozen Stage-1 entity ID")
    return value


def _common(item: Mapping[str, Any], kind: str) -> None:
    if not isinstance(item["statement"], str) or not item["statement"].strip():
        raise ValidationError(f"{kind}.statement must be non-empty")
    confidence = item["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValidationError(f"{kind}.confidence must be between 0 and 1")
    if item["origin"] not in {"SOURCE", "INFERRED"}:
        raise ValidationError(f"{kind}.origin must be SOURCE or INFERRED")


_COMMON = {"statement", "confidence", "origin", "relationship_type", "comparison_operator"}
_COMPARISON = _COMMON | {
    "proposition_type", "left_operand_entity_id", "right_operand_entity_id", "outcome_entity_id"
}
_TRANSFER = _COMMON | {
    "proposition_type", "event_entity_id", "object_entity_id", "destination_entity_id"
}


def _canonical_comparison(item: Any, inventory: FrozenEntityInventory) -> dict[str, Any]:
    item = _exact(item, _COMPARISON, "comparison_condition")
    _common(item, "comparison_condition")
    if (item["proposition_type"], item["relationship_type"], item["comparison_operator"]) != (
        "COMPARISON_CONDITION", "CAUSES", "GREATER_THAN"
    ):
        raise ValidationError("comparison_condition subtype contract requires COMPARISON_CONDITION, CAUSES, GREATER_THAN")
    left = _endpoint(item["left_operand_entity_id"], inventory.ids, "left_operand_entity_id")
    right = _endpoint(item["right_operand_entity_id"], inventory.ids, "right_operand_entity_id")
    outcome = _endpoint(item["outcome_entity_id"], inventory.ids, "outcome_entity_id")
    if left == right:
        raise ValidationError("comparison condition operands must be distinct")
    return {
        "proposition_type": "COMPARISON_CONDITION",
        "statement": item["statement"],
        "role_bindings": [
            {"role": "LEFT_OPERAND", "entity_id": left},
            {"role": "RIGHT_OPERAND", "entity_id": right},
            {"role": "OUTCOME", "entity_id": outcome},
        ],
        "relationship_type": "CAUSES",
        "comparison_operator": "GREATER_THAN",
        "confidence": item["confidence"],
        "origin": item["origin"],
    }


def _canonical_transfer(item: Any, inventory: FrozenEntityInventory) -> dict[str, Any]:
    item = _exact(item, _TRANSFER, "transfer_event")
    _common(item, "transfer_event")
    if (item["proposition_type"], item["relationship_type"], item["comparison_operator"]) != (
        "TRANSFER_EVENT", "TRANSFERS_TO", None
    ):
        raise ValidationError("transfer_event subtype contract requires TRANSFER_EVENT, TRANSFERS_TO, null operator")
    event = _endpoint(item["event_entity_id"], inventory.ids, "event_entity_id")
    obj = _endpoint(item["object_entity_id"], inventory.ids, "object_entity_id")
    destination = _endpoint(item["destination_entity_id"], inventory.ids, "destination_entity_id")
    entities = {entity.id: entity for entity in inventory.symbol_table.entities}
    if entities[event].entity_type is not EntityType.PROCESS:
        raise ValidationError("transfer EVENT must be a frozen PROCESS entity")
    if entities[destination].entity_type is EntityType.PROCESS:
        raise ValidationError("transfer DESTINATION must be a frozen non-PROCESS entity")
    if event == destination:
        raise ValidationError("transfer EVENT and DESTINATION must differ")
    return {
        "proposition_type": "TRANSFER_EVENT",
        "statement": item["statement"],
        "role_bindings": [
            {"role": "EVENT", "entity_id": event},
            {"role": "OBJECT", "entity_id": obj},
            {"role": "DESTINATION", "entity_id": destination},
        ],
        "relationship_type": "TRANSFERS_TO",
        "comparison_operator": None,
        "confidence": item["confidence"],
        "origin": item["origin"],
    }


def normalize_stage2_v2(
    raw: Mapping[str, Any], document: SourceDocument, inventory: FrozenEntityInventory
) -> dict[str, Any]:
    """Fail closed on v2 shape, then map exact roles to unchanged canonical form.

    This is mechanical interface decoding, never semantic repair. The caller must
    preserve ``raw`` separately as the original provider proposal.
    """
    raw = _exact(raw, {"relationships", "comparison_conditions", "transfer_events", "missing_symbols"}, "Stage 2 v2 proposal")
    comparison = [
        _canonical_comparison(item, inventory)
        for item in _items(raw["comparison_conditions"], "comparison_conditions")
    ]
    transfers = [
        _canonical_transfer(item, inventory)
        for item in _items(raw["transfer_events"], "transfer_events")
    ]
    normalized = {
        "relationships": _items(raw["relationships"], "relationships"),
        "propositions": [*comparison, *transfers],
        "missing_symbols": _items(raw["missing_symbols"], "missing_symbols"),
    }
    validate_semantic_structure(normalized, document, inventory)
    return normalized


def replay_v1_proposition_shape(proposition: Mapping[str, Any]) -> list[str]:
    """Audit a preserved v1 object against v2 subtype invariants without repair."""
    kind = proposition.get("proposition_type")
    expected = {
        "COMPARISON_CONDITION": ({"LEFT_OPERAND", "RIGHT_OPERAND", "OUTCOME"}, "CAUSES", "GREATER_THAN"),
        "TRANSFER_EVENT": ({"EVENT", "OBJECT", "DESTINATION"}, "TRANSFERS_TO", None),
    }.get(kind)
    if expected is None:
        return ["unsupported subtype"]
    bindings = proposition.get("role_bindings")
    if not isinstance(bindings, list):
        return ["role_bindings must be an array"]
    roles = [item.get("role") for item in bindings if isinstance(item, Mapping)]
    errors = []
    if len(bindings) != 3 or set(roles) != expected[0] or len(set(roles)) != 3:
        errors.append("invalid subtype role shape")
    if proposition.get("relationship_type") != expected[1]:
        errors.append("invalid subtype relationship_type")
    if proposition.get("comparison_operator") != expected[2]:
        errors.append("invalid subtype comparison_operator")
    if kind == "COMPARISON_CONDITION":
        by_role = {item.get("role"): item.get("entity_id") for item in bindings if isinstance(item, Mapping)}
        if by_role.get("LEFT_OPERAND") is not None and by_role.get("LEFT_OPERAND") == by_role.get("RIGHT_OPERAND"):
            errors.append("comparison operands are identical")
    return errors


class _V2StageAdapter:
    """Keep original Stage-2 provider output in the attempt's audit metadata."""

    def __init__(self, extractor: DecomposedExtractionAdapter) -> None:
        self.extractor = extractor
        self.live_capable = getattr(extractor, "live_capable", True)
        self.call_ledger = getattr(extractor, "call_ledger", {"calls_started": 0, "entries": []})

    def extract_entity_inventory(self, document: SourceDocument) -> StageAttempt:
        return self.extractor.extract_entity_inventory(document)

    def extract_semantic_structure(self, document: SourceDocument, inventory: FrozenEntityInventory) -> StageAttempt:
        original = self.extractor.extract_semantic_structure(document, inventory)
        try:
            normalized = normalize_stage2_v2(original.raw_proposal, document, inventory)
        except Exception as exc:
            raise StageExecutionError(f"Candidate-B-v2 Stage-2 contract rejected output: {exc}", original) from exc
        metadata = {**original.provider_metadata, "candidate_version": CANDIDATE_B_V2_VERSION, "original_stage2_proposal": original.raw_proposal, "normalization": "LOSSLESS_VARIANT_TO_CANONICAL_ROLE_BINDINGS"}
        return StageAttempt(StageName.SEMANTIC_STRUCTURE, normalized, metadata, original.raw_provider_response)

    def extract_claim_evidence(self, document: SourceDocument, inventory: FrozenEntityInventory, structure: Any) -> StageAttempt:
        return self.extractor.extract_claim_evidence(document, inventory, structure)


@dataclass(frozen=True, slots=True)
class CandidateBV2Run:
    underlying: CandidateBRun

    @property
    def source_id(self) -> str:
        return self.underlying.source_id

    @property
    def source_sha256(self) -> str:
        return self.underlying.source_sha256

    @property
    def inventory(self) -> FrozenEntityInventory | None:
        return self.underlying.inventory

    @property
    def structure(self) -> Any:
        return self.underlying.structure

    @property
    def binding(self) -> Any:
        return self.underlying.binding

    @property
    def provider_call_ledger(self) -> Mapping[str, Any]:
        return self.underlying.provider_call_ledger

    @property
    def status(self) -> Any:
        return self.underlying.status

    @property
    def stage_gates(self) -> Any:
        return self.underlying.stage_gates

    @property
    def canonical_gate(self) -> Any:
        gate = self.underlying.canonical_gate
        if self.model is None:
            return gate
        return replace(gate, output_identity_sha256=stable_hash(self.model.to_dict()))

    @property
    def attempts(self) -> Any:
        return self.underlying.attempts

    @property
    def model(self) -> KnowledgeModel | None:
        model = self.underlying.model
        return replace(model, metadata={**model.metadata, "candidate_version": CANDIDATE_B_V2_VERSION}) if model else None

    def to_dict(self) -> dict[str, Any]:
        value = self.underlying.to_dict()
        value["candidate_version"] = CANDIDATE_B_V2_VERSION
        value["model"] = self.model.to_dict() if self.model else None
        value["canonical_gate"] = self.canonical_gate.to_dict()
        for gate in value["stage_gates"]:
            gate["stage_version"] = {
                StageName.SEMANTIC_STRUCTURE.value: STAGE2_V2_VERSION,
                StageName.CLAIM_EVIDENCE_BINDING.value: STAGE3_V2_VERSION,
            }.get(gate["stage"], gate["stage_version"])
        for key in ("entity_inventory", "semantic_structure", "claim_evidence_binding"):
            if value[key] is not None:
                value[key]["candidate_version"] = CANDIDATE_B_V2_VERSION
        value["lineage"] = "Candidate B v1 Stage 1/3 mechanics and canonical validators; versioned v2 Stage 2 interface"
        return value


def run_candidate_b_v2(
    text: str,
    extractor: DecomposedExtractionAdapter,
    *,
    source_metadata: Mapping[str, Any] | None = None,
    allow_live: bool = False,
) -> CandidateBV2Run:
    if getattr(extractor, "candidate_version", None) != CANDIDATE_B_V2_VERSION:
        raise ValidationError("Candidate B v2 requires an explicitly versioned adapter")
    return CandidateBV2Run(
        run_candidate_b(
            text, _V2StageAdapter(extractor), source_metadata=source_metadata,
            allow_live=allow_live,
        )
    )
