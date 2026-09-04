"""Provider-independent assertion-first semantic compilation boundary."""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Protocol

from .models import (
    Claim,
    ComparisonOperator,
    KnowledgeModel,
    Origin,
    Proposition,
    PropositionRoleBinding,
    PropositionType,
    Relationship,
    RelationshipType,
    SourceDocument,
    SourceSpan,
    ValidationError,
)
from .openai_extractor import resolve_evidence_quote
from .proposition_validation import validate_proposition_coverage
from .staged_compilation import SymbolTable


ASSERTION_COMPILER_VERSION = "spec-013-v1"


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
class AssertionNomination:
    statement: str
    participant_entity_ids: tuple[str, ...]
    evidence_quotes: tuple[str, ...]
    origin: Origin = Origin.SOURCE

    def __post_init__(self) -> None:
        _nonempty(self.statement, "assertion.statement")
        participants = tuple(self.participant_entity_ids)
        if not participants or any(not isinstance(item, str) or not item.strip() for item in participants):
            raise ValidationError("assertion participants must contain frozen symbol IDs")
        if len(participants) != len(set(participants)):
            raise ValidationError("assertion participant IDs must be unique")
        quotes = tuple(self.evidence_quotes)
        if not quotes or any(not isinstance(item, str) or not item for item in quotes):
            raise ValidationError("SOURCE assertions require non-empty evidence quotes")
        try:
            origin = Origin(self.origin)
        except (TypeError, ValueError) as exc:
            raise ValidationError("assertion.origin must be SOURCE") from exc
        if origin is not Origin.SOURCE:
            raise ValidationError("assertion extraction is source-only; origin must be SOURCE")
        object.__setattr__(self, "participant_entity_ids", participants)
        object.__setattr__(self, "evidence_quotes", quotes)
        object.__setattr__(self, "origin", origin)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> AssertionNomination:
        if not isinstance(value, Mapping):
            raise ValidationError("assertion nomination must be an object")
        allowed = {"statement", "participant_entity_ids", "evidence", "origin"}
        unknown = set(value) - allowed
        if unknown:
            raise ValidationError(
                f"assertion extraction cannot create entities or unknown fields: {sorted(unknown)}"
            )
        evidence = value.get("evidence")
        if not isinstance(evidence, list):
            raise ValidationError("assertion evidence must be an array")
        quotes = []
        for index, item in enumerate(evidence):
            if not isinstance(item, Mapping) or set(item) != {"quote"}:
                raise ValidationError(
                    f"assertion evidence[{index}] must contain exactly quote"
                )
            quotes.append(item.get("quote"))
        return cls(
            statement=value.get("statement"),
            participant_entity_ids=tuple(value.get("participant_entity_ids", ())),
            evidence_quotes=tuple(quotes),
            origin=value.get("origin", Origin.SOURCE),
        )


@dataclass(frozen=True, slots=True)
class AssertionExtractionProposal:
    assertions: tuple[AssertionNomination, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "assertions", tuple(self.assertions))
        object.__setattr__(self, "metadata", dict(self.metadata))
        if not self.assertions:
            raise ValidationError("assertion extraction must nominate at least one assertion")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> AssertionExtractionProposal:
        if not isinstance(value, Mapping):
            raise ValidationError("assertion extraction proposal must be an object")
        allowed = {"assertions", "metadata"}
        unknown = set(value) - allowed
        if unknown:
            raise ValidationError(
                f"assertion extraction cannot create entities or unknown fields: {sorted(unknown)}"
            )
        raw = value.get("assertions")
        if not isinstance(raw, list):
            raise ValidationError("assertions must be an array")
        return cls(
            tuple(AssertionNomination.from_dict(item) for item in raw),
            value.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "assertions": [
                {
                    "statement": item.statement,
                    "participant_entity_ids": list(item.participant_entity_ids),
                    "evidence": [{"quote": quote} for quote in item.evidence_quotes],
                    "origin": item.origin.value,
                }
                for item in self.assertions
            ],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class SourceAssertion:
    id: str
    statement: str
    participant_entity_ids: tuple[str, ...]
    evidence: tuple[SourceSpan, ...]
    origin: Origin = Origin.SOURCE

    def __post_init__(self) -> None:
        _nonempty(self.id, "source_assertion.id")
        _nonempty(self.statement, "source_assertion.statement")
        participants = tuple(self.participant_entity_ids)
        if not participants or len(participants) != len(set(participants)):
            raise ValidationError("source assertion participants must be non-empty and unique")
        evidence = tuple(self.evidence)
        if not evidence:
            raise ValidationError("SOURCE assertions require resolved evidence")
        if Origin(self.origin) is not Origin.SOURCE:
            raise ValidationError("source assertions must have SOURCE origin")
        object.__setattr__(self, "participant_entity_ids", participants)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "origin", Origin.SOURCE)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], document_id: str) -> SourceAssertion:
        return cls(
            id=value.get("id"),
            statement=value.get("statement"),
            participant_entity_ids=tuple(value.get("participant_entity_ids", ())),
            evidence=tuple(
                SourceSpan.from_dict(item, document_id) for item in value.get("evidence", ())
            ),
            origin=value.get("origin", Origin.SOURCE),
        )


@dataclass(frozen=True, slots=True)
class GroundedAssertionSet:
    assertions: tuple[SourceAssertion, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        assertions = tuple(self.assertions)
        ids = [item.id for item in assertions]
        if not assertions or len(ids) != len(set(ids)):
            raise ValidationError("grounded assertion IDs must be non-empty and unique")
        object.__setattr__(self, "assertions", assertions)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @property
    def ids(self) -> frozenset[str]:
        return frozenset(item.id for item in self.assertions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "compiler_version": ASSERTION_COMPILER_VERSION,
            "assertions": [item.to_dict() for item in self.assertions],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], document: SourceDocument) -> GroundedAssertionSet:
        assertions = tuple(
            SourceAssertion.from_dict(item, document.id)
            for item in value.get("assertions", ())
        )
        for assertion in assertions:
            for span in assertion.evidence:
                span.validate_against(document)
        return cls(assertions, value.get("metadata", {}))


def deterministic_assertion_id(
    statement: str, participant_entity_ids: tuple[str, ...], evidence: tuple[SourceSpan, ...]
) -> str:
    normalized = re.sub(r"\s+", " ", statement).strip().casefold()
    signature = "|".join((
        normalized,
        ",".join(sorted(participant_entity_ids)),
        ",".join(f"{span.start_char}:{span.end_char}" for span in evidence),
    ))
    return f"assertion-{hashlib.sha256(signature.encode()).hexdigest()[:16]}"


class AssertionParticipantError(ValidationError):
    def __init__(self, assertion_index: int, unknown_ids: tuple[str, ...]) -> None:
        self.assertion_index = assertion_index
        self.unknown_ids = unknown_ids
        super().__init__(
            f"assertion[{assertion_index}] references unknown frozen symbols: {list(unknown_ids)}"
        )


class AssertionGroundingError(ValidationError):
    def __init__(self, assertion_index: int, cause: Exception) -> None:
        self.assertion_index = assertion_index
        self.cause = cause
        super().__init__(f"assertion[{assertion_index}] grounding failed: {cause}")


def ground_assertions(
    document: SourceDocument,
    symbol_table: SymbolTable,
    proposal: AssertionExtractionProposal,
) -> GroundedAssertionSet:
    grounded = []
    for index, nomination in enumerate(proposal.assertions):
        unknown = tuple(sorted(set(nomination.participant_entity_ids) - symbol_table.ids))
        if unknown:
            raise AssertionParticipantError(index, unknown)
        try:
            evidence = tuple(
                SourceSpan.from_dict(resolve_evidence_quote(document, quote), document.id)
                for quote in nomination.evidence_quotes
            )
        except ValidationError as exc:
            raise AssertionGroundingError(index, exc) from exc
        assertion_id = deterministic_assertion_id(
            nomination.statement, nomination.participant_entity_ids, evidence
        )
        grounded.append(SourceAssertion(
            assertion_id,
            nomination.statement,
            nomination.participant_entity_ids,
            evidence,
            nomination.origin,
        ))
    grounded.sort(key=lambda item: item.id)
    return GroundedAssertionSet(tuple(grounded), proposal.metadata)


@dataclass(frozen=True, slots=True)
class RelationshipCompilation:
    assertion_id: str
    source_entity_id: str
    relationship_type: RelationshipType
    target_entity_id: str
    statement: str
    confidence: float

    def __post_init__(self) -> None:
        for name in ("assertion_id", "source_entity_id", "target_entity_id", "statement"):
            _nonempty(getattr(self, name), f"relationship_compilation.{name}")
        try:
            object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
        except (TypeError, ValueError) as exc:
            raise ValidationError("relationship compilation uses an unknown predicate") from exc
        object.__setattr__(self, "confidence", _confidence(self.confidence, "relationship confidence"))


@dataclass(frozen=True, slots=True)
class PropositionCompilation:
    assertion_id: str
    proposition_type: PropositionType
    statement: str
    role_bindings: tuple[PropositionRoleBinding, ...]
    relationship_type: RelationshipType
    comparison_operator: ComparisonOperator | None
    confidence: float


@dataclass(frozen=True, slots=True)
class ClaimCompilation:
    assertion_id: str
    statement: str
    confidence: float


@dataclass(frozen=True, slots=True)
class UncompiledAssertion:
    assertion_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class CanonicalizationProposal:
    relationships: tuple[RelationshipCompilation, ...]
    propositions: tuple[PropositionCompilation, ...]
    claims: tuple[ClaimCompilation, ...]
    uncompiled_assertions: tuple[UncompiledAssertion, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> CanonicalizationProposal:
        if not isinstance(value, Mapping):
            raise ValidationError("canonicalization proposal must be an object")
        allowed = {"relationships", "propositions", "claims", "uncompiled_assertions", "metadata"}
        unknown = set(value) - allowed
        if unknown:
            raise ValidationError(
                f"canonicalization cannot create entities or unknown fields: {sorted(unknown)}"
            )
        relationships = tuple(RelationshipCompilation(
            assertion_id=item.get("assertion_id"),
            source_entity_id=item.get("source_entity_id"),
            relationship_type=item.get("relationship_type"),
            target_entity_id=item.get("target_entity_id"),
            statement=item.get("statement"),
            confidence=item.get("confidence"),
        ) for item in value.get("relationships", ()))
        propositions = []
        for item in value.get("propositions", ()):
            bindings = tuple(
                PropositionRoleBinding.from_dict(binding)
                for binding in item.get("role_bindings", ())
            )
            propositions.append(PropositionCompilation(
                assertion_id=_nonempty(item.get("assertion_id"), "proposition assertion_id"),
                proposition_type=PropositionType(item.get("proposition_type")),
                statement=_nonempty(item.get("statement"), "proposition statement"),
                role_bindings=bindings,
                relationship_type=RelationshipType(item.get("relationship_type")),
                comparison_operator=(
                    ComparisonOperator(item["comparison_operator"])
                    if item.get("comparison_operator") is not None else None
                ),
                confidence=_confidence(item.get("confidence"), "proposition confidence"),
            ))
        claims = tuple(ClaimCompilation(
            _nonempty(item.get("assertion_id"), "claim assertion_id"),
            _nonempty(item.get("statement"), "claim statement"),
            _confidence(item.get("confidence"), "claim confidence"),
        ) for item in value.get("claims", ()))
        abstentions = tuple(UncompiledAssertion(
            _nonempty(item.get("assertion_id"), "uncompiled assertion_id"),
            _nonempty(item.get("reason"), "uncompiled assertion reason"),
        ) for item in value.get("uncompiled_assertions", ()))
        return cls(relationships, tuple(propositions), claims, abstentions, value.get("metadata", {}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationships": [asdict(item) for item in self.relationships],
            "propositions": [asdict(item) for item in self.propositions],
            "claims": [asdict(item) for item in self.claims],
            "uncompiled_assertions": [asdict(item) for item in self.uncompiled_assertions],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class AssertionCompilationResult:
    model: KnowledgeModel
    assertions: GroundedAssertionSet
    canonicalization: CanonicalizationProposal


def compile_assertion_semantics(
    document: SourceDocument,
    symbol_table: SymbolTable,
    assertions: GroundedAssertionSet,
    proposal: CanonicalizationProposal,
) -> AssertionCompilationResult:
    by_id = {item.id: item for item in assertions.assertions}
    decisions = [
        *(item.assertion_id for item in proposal.relationships),
        *(item.assertion_id for item in proposal.propositions),
        *(item.assertion_id for item in proposal.claims),
        *(item.assertion_id for item in proposal.uncompiled_assertions),
    ]
    unknown = sorted(set(decisions) - set(by_id))
    missing = sorted(set(by_id) - set(decisions))
    duplicates = sorted(item for item in set(decisions) if decisions.count(item) > 1)
    if unknown or missing or duplicates:
        raise ValidationError(
            "canonicalization must account for every assertion exactly once; "
            f"unknown={unknown}, missing={missing}, duplicates={duplicates}"
        )
    known_symbols = symbol_table.ids
    relationships = []
    for item in proposal.relationships:
        missing_endpoints = sorted(
            {item.source_entity_id, item.target_entity_id} - known_symbols
        )
        if missing_endpoints:
            raise ValidationError(
                f"canonical relationship for {item.assertion_id!r} references unknown symbols: {missing_endpoints}"
            )
        source = by_id[item.assertion_id]
        relationships.append(Relationship(
            id=f"relationship-{item.assertion_id.removeprefix('assertion-')}",
            source_entity_id=item.source_entity_id,
            relationship_type=item.relationship_type,
            target_entity_id=item.target_entity_id,
            statement=item.statement,
            evidence=source.evidence,
            confidence=item.confidence,
            origin=source.origin,
        ))
    propositions = []
    for item in proposal.propositions:
        missing_roles = sorted(
            {binding.entity_id for binding in item.role_bindings} - known_symbols
        )
        if missing_roles:
            raise ValidationError(
                f"canonical proposition for {item.assertion_id!r} references unknown symbols: {missing_roles}"
            )
        source = by_id[item.assertion_id]
        propositions.append(Proposition.from_dict({
            "proposition_type": item.proposition_type.value,
            "statement": item.statement,
            "role_bindings": [asdict(binding) for binding in item.role_bindings],
            "relationship_type": item.relationship_type.value,
            "comparison_operator": (
                item.comparison_operator.value if item.comparison_operator else None
            ),
            "evidence": [asdict(span) for span in source.evidence],
            "confidence": item.confidence,
            "origin": source.origin.value,
        }, document.id))
    claims = []
    for item in proposal.claims:
        source = by_id[item.assertion_id]
        claims.append(Claim(
            id=f"claim-{item.assertion_id.removeprefix('assertion-')}",
            statement=item.statement,
            evidence=source.evidence,
            confidence=item.confidence,
            origin=source.origin,
        ))
    model = KnowledgeModel(
        document=document,
        entities=symbol_table.entities,
        claims=tuple(claims),
        relationships=tuple(relationships),
        propositions=tuple(propositions),
        metadata={
            "compiler_version": ASSERTION_COMPILER_VERSION,
            "symbol_table_reused": True,
            "assertion_extraction_provider": dict(assertions.metadata),
            "canonicalization_provider": dict(proposal.metadata),
            "uncompiled_assertion_count": len(proposal.uncompiled_assertions),
        },
    )
    validate_proposition_coverage(model)
    return AssertionCompilationResult(model, assertions, proposal)


class AssertionExtractor(Protocol):
    def extract_assertions(
        self, document: SourceDocument, symbol_table: SymbolTable
    ) -> AssertionExtractionProposal:
        """Propose neutral source assertions against frozen symbols."""


class AssertionCanonicalizer(Protocol):
    def canonicalize_assertions(
        self, assertions: GroundedAssertionSet, symbol_table: SymbolTable
    ) -> CanonicalizationProposal:
        """Map already-grounded assertions to canonical forms or abstain."""
