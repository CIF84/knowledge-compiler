"""Provider-neutral three-stage extraction candidate for SPEC-047.

Candidate B freezes entity identities before semantic topology is proposed, then
binds exact evidence without allowing the evidence stage to alter that topology.
The existing ``KnowledgeModel`` remains the final trusted boundary.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Protocol

from .models import (
    Claim,
    KnowledgeModel,
    Origin,
    Proposition,
    Relationship,
    SourceDocument,
    SourceSpan,
    ValidationError,
)
from .normalize import normalize_document
from .openai_extractor import resolve_evidence_quote, resolve_output_evidence
from .proposition_validation import validate_proposition_coverage
from .staged_compilation import (
    SymbolDiscoveryProposal,
    SymbolTable,
    canonicalize_symbol_table,
)


CANDIDATE_B_VERSION = "spec-047-candidate-b-v1"
STAGE_VERSIONS = {
    "ENTITY_INVENTORY": "spec-047-entity-inventory-v1",
    "SEMANTIC_STRUCTURE": "spec-047-semantic-structure-v1",
    "CLAIM_EVIDENCE_BINDING": "spec-047-claim-evidence-binding-v1",
    "CANONICAL_VALIDATION": "existing-knowledge-model-validator",
}


class StageName(StrEnum):
    ENTITY_INVENTORY = "ENTITY_INVENTORY"
    SEMANTIC_STRUCTURE = "SEMANTIC_STRUCTURE"
    CLAIM_EVIDENCE_BINDING = "CLAIM_EVIDENCE_BINDING"
    CANONICAL_VALIDATION = "CANONICAL_VALIDATION"


class GateStatus(StrEnum):
    PASS = "PASS"
    FAIL_CLOSED = "FAIL_CLOSED"
    NOT_RUN_UPSTREAM_FAILURE = "NOT_RUN_UPSTREAM_FAILURE"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{path} must be an object")
    return value


def _array(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{path} must be an array")
    return value


def _exact_fields(value: Mapping[str, Any], expected: set[str], path: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ValidationError(
            f"{path} must contain exactly {sorted(expected)}; "
            f"missing={sorted(expected - actual)}, unknown={sorted(actual - expected)}"
        )


@dataclass(frozen=True, slots=True)
class StageAttempt:
    """One provider or deterministic fixture result before its stage gate."""

    stage: StageName
    raw_proposal: Mapping[str, Any]
    provider_metadata: Mapping[str, Any] = field(default_factory=dict)
    raw_provider_response: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage", StageName(self.stage))
        object.__setattr__(self, "raw_proposal", _copy(_mapping(self.raw_proposal, "raw_proposal")))
        object.__setattr__(self, "provider_metadata", _copy(_mapping(self.provider_metadata, "provider_metadata")))
        if self.raw_provider_response is not None:
            object.__setattr__(
                self,
                "raw_provider_response",
                _copy(_mapping(self.raw_provider_response, "raw_provider_response")),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "raw_proposal": _copy(self.raw_proposal),
            "provider_metadata": _copy(self.provider_metadata),
            "raw_provider_response": _copy(self.raw_provider_response),
        }


class StageExecutionError(RuntimeError):
    """A stage failed after a request began; any available attempt is retained."""

    def __init__(self, message: str, attempt: StageAttempt | None = None) -> None:
        super().__init__(message)
        self.attempt = attempt


@dataclass(frozen=True, slots=True)
class StageGateResult:
    stage: StageName
    status: GateStatus
    upstream_identity_sha256: str | None
    exact_failure: str | None = None
    error_type: str | None = None
    output_identity_sha256: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "stage_version": STAGE_VERSIONS[self.stage.value],
            "status": self.status.value,
            "upstream_identity_sha256": self.upstream_identity_sha256,
            "output_identity_sha256": self.output_identity_sha256,
            "error_type": self.error_type,
            "exact_failure": self.exact_failure,
        }


@dataclass(frozen=True, slots=True)
class FrozenEntityInventory:
    symbol_table: SymbolTable
    identity_sha256: str

    @property
    def ids(self) -> frozenset[str]:
        return self.symbol_table.ids

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_version": CANDIDATE_B_VERSION,
            "identity_sha256": self.identity_sha256,
            "immutable": True,
            "symbol_table": self.symbol_table.to_dict(),
        }


def freeze_entity_inventory(
    raw: Mapping[str, Any], document: SourceDocument
) -> FrozenEntityInventory:
    """Validate Stage 1 and freeze stable IDs without repairing duplicates."""

    proposal = SymbolDiscoveryProposal.from_dict(_mapping(raw, "Stage 1 proposal"))
    normalized_names: set[str] = set()
    aliases: dict[str, str] = {}
    from .deduplicate import normalized_entity_name

    for index, nomination in enumerate(proposal.nominations):
        name = normalized_entity_name(nomination.name)
        if name in normalized_names:
            raise ValidationError(f"Stage 1 duplicate entity declaration: {nomination.name!r}")
        normalized_names.add(name)
        for term in (nomination.name, *nomination.aliases):
            normalized = normalized_entity_name(term)
            owner = aliases.get(normalized)
            if owner is not None and owner != name:
                raise ValidationError(
                    f"Stage 1 alias {term!r} conflicts between {owner!r} and {name!r}"
                )
            aliases[normalized] = name
        if not nomination.description.strip():
            raise ValidationError(f"Stage 1 symbols[{index}].description must be non-empty")

    table = canonicalize_symbol_table(proposal)
    table = SymbolTable(
        entities=table.entities,
        diagnostics={
            **dict(table.diagnostics),
            "candidate_version": CANDIDATE_B_VERSION,
            "source_document_id": document.id,
            "strict_duplicate_policy": "FAIL_CLOSED_NO_MERGE",
        },
        compiler_version=CANDIDATE_B_VERSION,
    )
    value = table.to_dict()
    return FrozenEntityInventory(table, stable_hash(value))


@dataclass(frozen=True, slots=True)
class SemanticStructure:
    relationships: tuple[Mapping[str, Any], ...]
    propositions: tuple[Mapping[str, Any], ...]
    missing_symbols: tuple[Mapping[str, str], ...]
    identity_sha256: str

    @property
    def semantic_object_ids(self) -> frozenset[str]:
        return frozenset(
            item["id"] for item in (*self.relationships, *self.propositions)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_version": CANDIDATE_B_VERSION,
            "identity_sha256": self.identity_sha256,
            "relationships": [_copy(item) for item in self.relationships],
            "propositions": [_copy(item) for item in self.propositions],
            "missing_symbols": [_copy(item) for item in self.missing_symbols],
        }


def _validate_relationship_skeleton(
    raw: Mapping[str, Any], document: SourceDocument, known: frozenset[str]
) -> dict[str, Any]:
    expected = {
        "id", "source_entity_id", "relationship_type", "target_entity_id",
        "statement", "confidence", "origin",
    }
    _exact_fields(raw, expected, "Stage 2 relationship")
    origin = Origin(raw.get("origin"))
    temporary = Relationship.from_dict(
        {**raw, "origin": Origin.INFERRED.value, "evidence": []}, document.id
    )
    missing = sorted(
        {temporary.source_entity_id, temporary.target_entity_id} - known
    )
    if missing:
        raise ValidationError(
            f"Stage 2 relationship {temporary.id!r} references unknown frozen entities: {missing}"
        )
    return {
        "id": temporary.id,
        "source_entity_id": temporary.source_entity_id,
        "relationship_type": temporary.relationship_type.value,
        "target_entity_id": temporary.target_entity_id,
        "statement": temporary.statement,
        "confidence": temporary.confidence,
        "origin": origin.value,
    }


def _validate_proposition_skeleton(
    raw: Mapping[str, Any], document: SourceDocument, known: frozenset[str]
) -> dict[str, Any]:
    expected = {
        "proposition_type", "statement", "role_bindings", "relationship_type",
        "comparison_operator", "confidence", "origin",
    }
    _exact_fields(raw, expected, "Stage 2 proposition")
    origin = Origin(raw.get("origin"))
    temporary = Proposition.from_dict(
        {**raw, "origin": Origin.INFERRED.value, "evidence": []}, document.id
    )
    missing = sorted({item.entity_id for item in temporary.role_bindings} - known)
    if missing:
        raise ValidationError(
            f"Stage 2 proposition {temporary.id!r} references unknown frozen entities: {missing}"
        )
    return {
        "id": temporary.id,
        "proposition_type": temporary.proposition_type.value,
        "statement": temporary.statement,
        "role_bindings": [asdict(item) for item in temporary.role_bindings],
        "relationship_type": temporary.relationship_type.value,
        "comparison_operator": (
            temporary.comparison_operator.value
            if temporary.comparison_operator is not None else None
        ),
        "confidence": temporary.confidence,
        "origin": origin.value,
    }


def validate_semantic_structure(
    raw: Mapping[str, Any], document: SourceDocument, inventory: FrozenEntityInventory
) -> SemanticStructure:
    """Validate Stage 2 topology against the immutable Stage 1 ID set."""

    raw = _mapping(raw, "Stage 2 proposal")
    _exact_fields(raw, {"relationships", "propositions", "missing_symbols"}, "Stage 2 proposal")
    relationships = tuple(
        _validate_relationship_skeleton(_mapping(item, f"relationships[{index}]"), document, inventory.ids)
        for index, item in enumerate(_array(raw["relationships"], "relationships"))
    )
    propositions = tuple(
        _validate_proposition_skeleton(_mapping(item, f"propositions[{index}]"), document, inventory.ids)
        for index, item in enumerate(_array(raw["propositions"], "propositions"))
    )
    ids = [item["id"] for item in (*relationships, *propositions)]
    if len(ids) != len(set(ids)):
        raise ValidationError("Stage 2 semantic object IDs must be unique")

    missing_symbols = []
    for index, item in enumerate(_array(raw["missing_symbols"], "missing_symbols")):
        item = _mapping(item, f"missing_symbols[{index}]")
        expected = {"surface_form", "semantic_item", "reason"}
        _exact_fields(item, expected, f"missing_symbols[{index}]")
        normalized = {}
        for key in sorted(expected):
            value = item[key]
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"missing_symbols[{index}].{key} must be non-empty")
            normalized[key] = value
        missing_symbols.append(normalized)

    value = {
        "relationships": relationships,
        "propositions": propositions,
        "missing_symbols": missing_symbols,
    }
    return SemanticStructure(
        relationships=relationships,
        propositions=propositions,
        missing_symbols=tuple(missing_symbols),
        identity_sha256=stable_hash(value),
    )


@dataclass(frozen=True, slots=True)
class ClaimEvidenceBinding:
    claims: tuple[Claim, ...]
    evidence_by_semantic_id: Mapping[str, tuple[SourceSpan, ...]]
    identity_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_version": CANDIDATE_B_VERSION,
            "identity_sha256": self.identity_sha256,
            "claims": [asdict(item) for item in self.claims],
            "semantic_evidence_bindings": [
                {
                    "semantic_object_id": semantic_id,
                    "evidence": [asdict(span) for span in spans],
                }
                for semantic_id, spans in sorted(self.evidence_by_semantic_id.items())
            ],
        }


def validate_claim_evidence_binding(
    raw: Mapping[str, Any], document: SourceDocument, structure: SemanticStructure
) -> ClaimEvidenceBinding:
    """Resolve exact Stage 3 evidence while forbidding topology changes."""

    raw = _mapping(raw, "Stage 3 proposal")
    _exact_fields(raw, {"claims", "semantic_evidence_bindings"}, "Stage 3 proposal")
    claims_raw = _array(raw["claims"], "claims")
    resolved_claims = resolve_output_evidence(
        {"claims": claims_raw, "relationships": [], "propositions": []}, document
    )["claims"]
    claims = tuple(Claim.from_dict(item, document.id) for item in resolved_claims)
    if len({item.id for item in claims}) != len(claims):
        raise ValidationError("Stage 3 claim IDs must be unique")

    evidence_by_id: dict[str, tuple[SourceSpan, ...]] = {}
    for index, item in enumerate(
        _array(raw["semantic_evidence_bindings"], "semantic_evidence_bindings")
    ):
        item = _mapping(item, f"semantic_evidence_bindings[{index}]")
        _exact_fields(
            item, {"semantic_object_id", "evidence"},
            f"semantic_evidence_bindings[{index}]",
        )
        semantic_id = item["semantic_object_id"]
        if semantic_id not in structure.semantic_object_ids:
            raise ValidationError(
                f"Stage 3 evidence references unknown frozen semantic object {semantic_id!r}"
            )
        if semantic_id in evidence_by_id:
            raise ValidationError(f"Stage 3 duplicate evidence binding for {semantic_id!r}")
        spans = []
        for evidence_index, evidence in enumerate(
            _array(item["evidence"], f"semantic_evidence_bindings[{index}].evidence")
        ):
            evidence = _mapping(
                evidence,
                f"semantic_evidence_bindings[{index}].evidence[{evidence_index}]",
            )
            _exact_fields(
                evidence,
                {"quote"},
                f"semantic_evidence_bindings[{index}].evidence[{evidence_index}]",
            )
            spans.append(
                SourceSpan.from_dict(resolve_evidence_quote(document, evidence["quote"]))
            )
        evidence_by_id[semantic_id] = tuple(spans)

    semantic_items = {
        item["id"]: item for item in (*structure.relationships, *structure.propositions)
    }
    for semantic_id, item in semantic_items.items():
        spans = evidence_by_id.get(semantic_id, ())
        origin = Origin(item["origin"])
        if origin is Origin.SOURCE and not spans:
            raise ValidationError(
                f"Stage 3 missing exact evidence for SOURCE semantic object {semantic_id!r}"
            )
        if origin is Origin.INFERRED and spans:
            raise ValidationError(
                f"Stage 3 cannot bind source evidence to INFERRED semantic object {semantic_id!r}"
            )
    value = {
        "claims": [asdict(item) for item in claims],
        "semantic_evidence_bindings": {
            key: [asdict(span) for span in spans]
            for key, spans in sorted(evidence_by_id.items())
        },
    }
    return ClaimEvidenceBinding(claims, evidence_by_id, stable_hash(value))


def assemble_candidate_model(
    document: SourceDocument,
    inventory: FrozenEntityInventory,
    structure: SemanticStructure,
    binding: ClaimEvidenceBinding,
) -> KnowledgeModel:
    """Cross the unchanged canonical trusted boundary."""

    relationships = tuple(
        Relationship.from_dict(
            {
                **item,
                "evidence": [
                    asdict(span)
                    for span in binding.evidence_by_semantic_id.get(item["id"], ())
                ],
            },
            document.id,
        )
        for item in structure.relationships
    )
    propositions = tuple(
        Proposition.from_dict(
            {
                **{key: value for key, value in item.items() if key != "id"},
                "id": item["id"],
                "evidence": [
                    asdict(span)
                    for span in binding.evidence_by_semantic_id.get(item["id"], ())
                ],
            },
            document.id,
        )
        for item in structure.propositions
    )
    model = KnowledgeModel(
        document=document,
        entities=inventory.symbol_table.entities,
        claims=binding.claims,
        relationships=relationships,
        propositions=propositions,
        metadata={
            "candidate_version": CANDIDATE_B_VERSION,
            "entity_inventory_sha256": inventory.identity_sha256,
            "semantic_structure_sha256": structure.identity_sha256,
            "claim_evidence_binding_sha256": binding.identity_sha256,
        },
    )
    validate_proposition_coverage(model)
    return model


class DecomposedExtractionAdapter(Protocol):
    live_capable: bool

    def extract_entity_inventory(self, document: SourceDocument) -> StageAttempt: ...

    def extract_semantic_structure(
        self, document: SourceDocument, inventory: FrozenEntityInventory
    ) -> StageAttempt: ...

    def extract_claim_evidence(
        self,
        document: SourceDocument,
        inventory: FrozenEntityInventory,
        structure: SemanticStructure,
    ) -> StageAttempt: ...


@dataclass(frozen=True, slots=True)
class CandidateBRun:
    source_id: str
    source_sha256: str
    status: GateStatus
    stage_gates: tuple[StageGateResult, ...]
    canonical_gate: StageGateResult
    attempts: tuple[StageAttempt, ...]
    model: KnowledgeModel | None
    inventory: FrozenEntityInventory | None
    structure: SemanticStructure | None
    binding: ClaimEvidenceBinding | None
    provider_call_ledger: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_version": CANDIDATE_B_VERSION,
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "status": self.status.value,
            "stage_gates": [item.to_dict() for item in self.stage_gates],
            "canonical_gate": self.canonical_gate.to_dict(),
            "attempts": [item.to_dict() for item in self.attempts],
            "model": self.model.to_dict() if self.model else None,
            "entity_inventory": self.inventory.to_dict() if self.inventory else None,
            "semantic_structure": self.structure.to_dict() if self.structure else None,
            "claim_evidence_binding": self.binding.to_dict() if self.binding else None,
            "provider_call_ledger": _copy(self.provider_call_ledger),
        }


def _not_run(stage: StageName) -> StageGateResult:
    return StageGateResult(stage, GateStatus.NOT_RUN_UPSTREAM_FAILURE, None)


def _ledger(extractor: Any) -> Mapping[str, Any]:
    ledger = getattr(extractor, "call_ledger", None)
    if ledger is None:
        return {"calls_started": 0, "entries": []}
    if hasattr(ledger, "to_dict"):
        return ledger.to_dict()
    return _copy(ledger)


def run_candidate_b(
    text: str,
    extractor: DecomposedExtractionAdapter,
    *,
    source_metadata: Mapping[str, Any] | None = None,
    allow_live: bool = False,
) -> CandidateBRun:
    """Run Candidate B once, preserving fail-closed stage and attempt history."""

    if getattr(extractor, "live_capable", True) and not allow_live:
        raise ValidationError("a live-capable Candidate-B adapter requires explicit authority")
    document = normalize_document(text, metadata=source_metadata)
    source_id = str(document.metadata.get("source_id", document.id))
    source_sha256 = hashlib.sha256(document.text.encode("utf-8")).hexdigest()
    attempts: list[StageAttempt] = []
    gates: list[StageGateResult] = []
    inventory = None
    structure = None
    binding = None

    stages = (
        StageName.ENTITY_INVENTORY,
        StageName.SEMANTIC_STRUCTURE,
        StageName.CLAIM_EVIDENCE_BINDING,
    )

    try:
        attempt = extractor.extract_entity_inventory(document)
        attempts.append(attempt)
        inventory = freeze_entity_inventory(attempt.raw_proposal, document)
        gates.append(
            StageGateResult(
                stages[0], GateStatus.PASS, source_sha256,
                output_identity_sha256=inventory.identity_sha256,
            )
        )
    except Exception as exc:
        if isinstance(exc, StageExecutionError) and exc.attempt is not None:
            attempts.append(exc.attempt)
        gates.extend((
            StageGateResult(
                stages[0], GateStatus.FAIL_CLOSED, source_sha256,
                exact_failure=str(exc), error_type=type(exc).__name__,
            ),
            _not_run(stages[1]),
            _not_run(stages[2]),
        ))
        canonical = _not_run(StageName.CANONICAL_VALIDATION)
        return CandidateBRun(
            source_id, source_sha256, GateStatus.FAIL_CLOSED, tuple(gates),
            canonical, tuple(attempts), None, None, None, None, _ledger(extractor),
        )

    try:
        attempt = extractor.extract_semantic_structure(document, inventory)
        attempts.append(attempt)
        structure = validate_semantic_structure(
            attempt.raw_proposal, document, inventory
        )
        gates.append(
            StageGateResult(
                stages[1], GateStatus.PASS, inventory.identity_sha256,
                output_identity_sha256=structure.identity_sha256,
            )
        )
    except Exception as exc:
        if isinstance(exc, StageExecutionError) and exc.attempt is not None:
            attempts.append(exc.attempt)
        gates.extend((
            StageGateResult(
                stages[1], GateStatus.FAIL_CLOSED, inventory.identity_sha256,
                exact_failure=str(exc), error_type=type(exc).__name__,
            ),
            _not_run(stages[2]),
        ))
        canonical = _not_run(StageName.CANONICAL_VALIDATION)
        return CandidateBRun(
            source_id, source_sha256, GateStatus.FAIL_CLOSED, tuple(gates),
            canonical, tuple(attempts), None, inventory, None, None, _ledger(extractor),
        )

    stage_3_upstream = stable_hash(
        {"inventory": inventory.identity_sha256, "structure": structure.identity_sha256}
    )
    try:
        attempt = extractor.extract_claim_evidence(document, inventory, structure)
        attempts.append(attempt)
        binding = validate_claim_evidence_binding(
            attempt.raw_proposal, document, structure
        )
        gates.append(
            StageGateResult(
                stages[2], GateStatus.PASS, stage_3_upstream,
                output_identity_sha256=binding.identity_sha256,
            )
        )
    except Exception as exc:
        if isinstance(exc, StageExecutionError) and exc.attempt is not None:
            attempts.append(exc.attempt)
        gates.append(
            StageGateResult(
                stages[2], GateStatus.FAIL_CLOSED, stage_3_upstream,
                exact_failure=str(exc), error_type=type(exc).__name__,
            )
        )
        canonical = _not_run(StageName.CANONICAL_VALIDATION)
        return CandidateBRun(
            source_id, source_sha256, GateStatus.FAIL_CLOSED, tuple(gates),
            canonical, tuple(attempts), None, inventory, structure, None,
            _ledger(extractor),
        )

    canonical_upstream = stable_hash(
        {
            "inventory": inventory.identity_sha256,
            "structure": structure.identity_sha256,
            "binding": binding.identity_sha256,
        }
    )
    try:
        model = assemble_candidate_model(document, inventory, structure, binding)
        canonical = StageGateResult(
            StageName.CANONICAL_VALIDATION,
            GateStatus.PASS,
            canonical_upstream,
            output_identity_sha256=stable_hash(model.to_dict()),
        )
    except Exception as exc:
        canonical = StageGateResult(
            StageName.CANONICAL_VALIDATION,
            GateStatus.FAIL_CLOSED,
            canonical_upstream,
            exact_failure=str(exc),
            error_type=type(exc).__name__,
        )
        return CandidateBRun(
            source_id, source_sha256, GateStatus.FAIL_CLOSED, tuple(gates),
            canonical, tuple(attempts), None, inventory, structure, binding,
            _ledger(extractor),
        )
    return CandidateBRun(
        source_id, source_sha256, GateStatus.PASS, tuple(gates), canonical,
        tuple(attempts), model, inventory, structure, binding, _ledger(extractor),
    )
