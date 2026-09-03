"""Bounded, source-grounded one-level resolution compilation for SPEC-008."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Protocol

from .deduplicate import deduplicate_entities
from .extractor import ExtractionResult
from .layout import with_layouts
from .models import KnowledgeModel, Origin, ValidationError
from .openai_extractor import ExtractionError, resolve_output_evidence
from .representation_builder import RepresentationBuilder
from .representations import RepresentationModel
from .resolution_strategies import (
    ResolutionStrategyId,
    get_resolution_strategy,
)
from .structure_detection import StructureDetector
from .structures import DetectedStructureSet


RESOLUTION_COMPILER_VERSION = "spec-008-v1"
RESOLUTION_PROMPT_VERSION = "spec-008-v1"
SPEC_009_COMPILER_VERSION = "spec-009-v1"


class ResolutionOutcome(StrEnum):
    SUCCESS = "SUCCESS"
    INSUFFICIENT_SOURCE_DETAIL = "INSUFFICIENT_SOURCE_DETAIL"
    GROUNDING_FAILURE = "GROUNDING_FAILURE"
    SEMANTIC_VALIDATION_FAILURE = "SEMANTIC_VALIDATION_FAILURE"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"


@dataclass(frozen=True, slots=True)
class ResolutionRequest:
    parent_document_id: str
    parent_representation_id: str
    focus_entity_id: str
    focus_label: str
    domain: str
    strategy_id: ResolutionStrategyId = ResolutionStrategyId.GENERIC_DETAIL

    def __post_init__(self) -> None:
        for name in (
            "parent_document_id", "parent_representation_id", "focus_entity_id",
            "focus_label", "domain",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"resolution request {name} must be non-empty")
        try:
            object.__setattr__(self, "strategy_id", ResolutionStrategyId(self.strategy_id))
        except (TypeError, ValueError) as exc:
            raise ValidationError("resolution request strategy_id is invalid") from exc

    def validate_against(
        self, parent: KnowledgeModel, parent_representation: RepresentationModel
    ) -> None:
        if self.parent_document_id != parent.document.id:
            raise ValidationError("resolution request parent document does not match KnowledgeModel")
        representation = next(
            (item for item in parent_representation.representations
             if item.id == self.parent_representation_id),
            None,
        )
        if representation is None:
            raise ValidationError("resolution request parent representation does not exist")
        node = next((item for item in representation.nodes if item.entity_id == self.focus_entity_id), None)
        entity = next((item for item in parent.entities if item.id == self.focus_entity_id), None)
        if node is None or entity is None or node.label != self.focus_label or entity.name != self.focus_label:
            raise ValidationError("resolution request focus does not match parent semantics")

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceScope:
    strategy: str
    document_id: str
    start_char: int
    end_char: int
    text: str
    connected_relationship_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.strategy != "FULL_DOCUMENT_SMALL_SOURCE":
            raise ValidationError("unsupported SPEC-008 source scope strategy")
        if self.start_char != 0 or self.end_char != len(self.text) or self.end_char <= 0:
            raise ValidationError("full-document source scope coordinates are invalid")
        object.__setattr__(self, "connected_relationship_ids", tuple(self.connected_relationship_ids))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_source_scope(parent: KnowledgeModel, focus_entity_id: str) -> SourceScope:
    """Use the complete accepted source because both benchmark documents are tiny."""
    if not any(entity.id == focus_entity_id for entity in parent.entities):
        raise ValidationError("source scope focus entity does not exist")
    connected = tuple(sorted(
        relationship.id for relationship in parent.relationships
        if focus_entity_id in (relationship.source_entity_id, relationship.target_entity_id)
        and relationship.origin is Origin.SOURCE
    ))
    return SourceScope(
        strategy="FULL_DOCUMENT_SMALL_SOURCE",
        document_id=parent.document.id,
        start_char=0,
        end_char=len(parent.document.text),
        text=parent.document.text,
        connected_relationship_ids=connected,
    )


@dataclass(frozen=True, slots=True)
class ResolutionNomination:
    outcome: ResolutionOutcome
    reason: str
    extraction: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "outcome", ResolutionOutcome(self.outcome))
        except (TypeError, ValueError) as exc:
            raise ValidationError("resolution nomination outcome is invalid") from exc
        if self.outcome not in {
            ResolutionOutcome.SUCCESS, ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL
        }:
            raise ValidationError("extractors may nominate only success or insufficient detail")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValidationError("resolution nomination reason must be non-empty")
        if not isinstance(self.extraction, Mapping) or not isinstance(self.metadata, Mapping):
            raise ValidationError("resolution nomination extraction and metadata must be objects")
        object.__setattr__(self, "extraction", dict(self.extraction))
        object.__setattr__(self, "metadata", dict(self.metadata))


class ResolutionExtractor(Protocol):
    def nominate(self, request: ResolutionRequest, parent: KnowledgeModel, scope: SourceScope) -> ResolutionNomination:
        """Nominate one child semantic model using only the supplied scope."""


class FixtureResolutionExtractor:
    """Deterministic adapter for offline resolution-compiler tests."""

    def __init__(self, nomination: ResolutionNomination | Exception) -> None:
        self.nomination = nomination

    def nominate(self, request: ResolutionRequest, parent: KnowledgeModel, scope: SourceScope) -> ResolutionNomination:
        if isinstance(self.nomination, Exception):
            raise self.nomination
        return self.nomination


@dataclass(frozen=True, slots=True)
class ResolutionAssessment:
    focus_relevance: bool
    mechanistic_detail_gain: bool
    explanatory_structure: bool
    source_support: bool
    parent_coherence: bool
    compression_relationship: str = "REQUIRES_HUMAN_REVIEW"

    @property
    def passes_automatic_gate(self) -> bool:
        return all((
            self.focus_relevance,
            self.mechanistic_detail_gain,
            self.explanatory_structure,
            self.source_support,
            self.parent_coherence,
        ))


@dataclass(frozen=True, slots=True)
class ChildResolutionArtifact:
    request: ResolutionRequest
    source_scope: SourceScope
    provider: str
    model: str
    prompt_version: str
    compiler_version: str
    child_model: KnowledgeModel
    structures: DetectedStructureSet
    representation: RepresentationModel
    assessment: ResolutionAssessment

    def __post_init__(self) -> None:
        for name in ("provider", "model", "prompt_version", "compiler_version"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValidationError(f"child resolution {name} must be non-empty")
        if self.child_model.document.id != self.request.parent_document_id:
            raise ValidationError("child resolution must retain the parent document identity")
        self.structures.validate_against(self.child_model)
        self.representation.validate_against(self.child_model, self.structures)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "source_scope": self.source_scope.to_dict(),
            "provider": self.provider,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "compiler_version": self.compiler_version,
            "child_model": self.child_model.to_dict(),
            "structures": self.structures.to_dict(),
            "representation": self.representation.to_dict(),
            "assessment": asdict(self.assessment),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ChildResolutionArtifact:
        request = ResolutionRequest(**value["request"])
        scope_value = value["source_scope"]
        scope = SourceScope(
            strategy=scope_value["strategy"], document_id=scope_value["document_id"],
            start_char=scope_value["start_char"], end_char=scope_value["end_char"],
            text=scope_value["text"],
            connected_relationship_ids=tuple(scope_value["connected_relationship_ids"]),
        )
        return cls(
            request=request,
            source_scope=scope,
            provider=value["provider"], model=value["model"],
            prompt_version=value["prompt_version"], compiler_version=value["compiler_version"],
            child_model=KnowledgeModel.from_dict(value["child_model"]),
            structures=DetectedStructureSet.from_dict(value["structures"]),
            representation=RepresentationModel.from_dict(value["representation"]),
            assessment=ResolutionAssessment(**value["assessment"]),
        )


@dataclass(frozen=True, slots=True)
class ResolutionCompilationResult:
    outcome: ResolutionOutcome
    request: ResolutionRequest
    source_scope: SourceScope
    reason: str
    provider_metadata: Mapping[str, Any] = field(default_factory=dict)
    artifact: ChildResolutionArtifact | None = None
    grounding_failures: tuple[str, ...] = ()
    rejected_extraction: Mapping[str, Any] | None = None
    retries: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "request": self.request.to_dict(),
            "source_scope": self.source_scope.to_dict(),
            "reason": self.reason,
            "provider_metadata": dict(self.provider_metadata),
            "artifact": self.artifact.to_dict() if self.artifact else None,
            "grounding_failures": list(self.grounding_failures),
            "rejected_extraction": (
                dict(self.rejected_extraction) if self.rejected_extraction is not None else None
            ),
            "retries": self.retries,
        }


def _failure(
    outcome: ResolutionOutcome,
    request: ResolutionRequest,
    scope: SourceScope,
    reason: str,
    *,
    metadata: Mapping[str, Any] | None = None,
    grounding_failures: tuple[str, ...] = (),
    rejected_extraction: Mapping[str, Any] | None = None,
) -> ResolutionCompilationResult:
    return ResolutionCompilationResult(
        outcome=outcome, request=request, source_scope=scope, reason=reason,
        provider_metadata=metadata or {}, grounding_failures=grounding_failures,
        rejected_extraction=rejected_extraction,
    )


def _scope_contains(scope: SourceScope, start: int, end: int) -> bool:
    return scope.start_char <= start < end <= scope.end_char


def _assessment(parent: KnowledgeModel, child: KnowledgeModel, request: ResolutionRequest, structures: DetectedStructureSet) -> ResolutionAssessment:
    parent_ids = {entity.id for entity in parent.entities}
    child_text = " ".join(
        [entity.name for entity in child.entities]
        + [entity.description for entity in child.entities]
        + [relationship.statement for relationship in child.relationships]
    ).casefold()
    focus_terms = {request.focus_label.casefold(), *(alias.casefold() for entity in parent.entities if entity.id == request.focus_entity_id for alias in entity.aliases)}
    source_relationships = [item for item in child.relationships if item.origin is Origin.SOURCE]
    return ResolutionAssessment(
        focus_relevance=any(term in child_text for term in focus_terms),
        mechanistic_detail_gain=len({entity.id for entity in child.entities} - parent_ids) >= 2,
        explanatory_structure=len(child.relationships) >= 2 and bool(structures.structures),
        source_support=bool(source_relationships) and all(item.evidence for item in source_relationships),
        parent_coherence=request.focus_label.casefold() in child_text,
    )


def compile_resolution(
    parent: KnowledgeModel,
    parent_representation: RepresentationModel,
    request: ResolutionRequest,
    extractor: ResolutionExtractor,
    *,
    compiler_version: str = RESOLUTION_COMPILER_VERSION,
) -> ResolutionCompilationResult:
    """Compile one child resolution; failures are explicit and never retried."""
    if not isinstance(compiler_version, str) or not compiler_version.strip():
        raise ValidationError("resolution compiler version must be non-empty")
    request.validate_against(parent, parent_representation)
    strategy = get_resolution_strategy(request.strategy_id)
    scope = build_source_scope(parent, request.focus_entity_id)
    parent_before = json.dumps(parent.to_dict(), sort_keys=True)
    try:
        nomination = extractor.nominate(request, parent, scope)
    except Exception as exc:
        reason = str(exc) if isinstance(exc, ExtractionError) else f"resolution provider failed: {exc}"
        return _failure(ResolutionOutcome.PROVIDER_FAILURE, request, scope, reason)
    if nomination.outcome is ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL:
        return _failure(
            ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL, request, scope,
            nomination.reason, metadata=nomination.metadata,
        )
    try:
        resolved = resolve_output_evidence(nomination.extraction, parent.document)
        extraction = ExtractionResult.from_dict(
            {**resolved, "metadata": nomination.metadata}, parent.document
        )
        extraction = deduplicate_entities(extraction)
        child = KnowledgeModel(
            document=parent.document,
            entities=extraction.entities,
            claims=extraction.claims,
            relationships=extraction.relationships,
            metadata={
                **dict(extraction.metadata),
                "resolution_compiler_version": compiler_version,
                "parent_document_id": request.parent_document_id,
                "parent_representation_id": request.parent_representation_id,
                "focus_entity_id": request.focus_entity_id,
                "source_scope_strategy": scope.strategy,
                "resolution_strategy_id": strategy.id.value,
                "resolution_strategy_semantic_role": strategy.semantic_role,
            },
        )
        for item in (*child.claims, *child.relationships):
            if any(not _scope_contains(scope, span.start_char, span.end_char) for span in item.evidence):
                raise ValidationError("resolved evidence lies outside permitted source scope")
    except ValidationError as exc:
        message = str(exc)
        outcome = (
            ResolutionOutcome.GROUNDING_FAILURE
            if "evidence" in message or "quote" in message or "source" in message
            else ResolutionOutcome.SEMANTIC_VALIDATION_FAILURE
        )
        return _failure(
            outcome, request, scope, message, metadata=nomination.metadata,
            grounding_failures=(message,) if outcome is ResolutionOutcome.GROUNDING_FAILURE else (),
            rejected_extraction=nomination.extraction,
        )
    structures = StructureDetector().detect(child)
    representation = with_layouts(RepresentationBuilder().build(child, structures))
    assessment = _assessment(parent, child, request, structures)
    if not assessment.passes_automatic_gate:
        return _failure(
            ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL,
            request,
            scope,
            "The nominated graph is valid but does not pass the automatic finer-resolution gate.",
            metadata={**nomination.metadata, "resolution_assessment": asdict(assessment)},
            rejected_extraction=nomination.extraction,
        )
    metadata = nomination.metadata
    artifact = ChildResolutionArtifact(
        request=request,
        source_scope=scope,
        provider=str(metadata.get("provider") or "fixture"),
        model=str(metadata.get("model") or "deterministic-fixture"),
        prompt_version=str(metadata.get("prompt_version") or RESOLUTION_PROMPT_VERSION),
        compiler_version=compiler_version,
        child_model=child,
        structures=structures,
        representation=representation,
        assessment=assessment,
    )
    if json.dumps(parent.to_dict(), sort_keys=True) != parent_before:
        raise AssertionError("resolution compilation mutated the parent KnowledgeModel")
    return ResolutionCompilationResult(
        outcome=ResolutionOutcome.SUCCESS,
        request=request,
        source_scope=scope,
        reason=nomination.reason,
        provider_metadata=metadata,
        artifact=artifact,
    )
