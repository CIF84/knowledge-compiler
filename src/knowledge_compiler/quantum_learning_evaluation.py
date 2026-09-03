"""SPEC-011 real-source quantum learning-slice evaluation."""

from __future__ import annotations

import hashlib
import json
import time
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .extractor import ExtractionResult, KnowledgeExtractor
from .deduplicate import deduplicate_entities
from .layout import with_layouts
from .models import Entity, EntityType, KnowledgeModel, Origin, ValidationError
from .openai_extractor import DEFAULT_MODEL, PROMPT_VERSION, OpenAILLMExtractor
from .openai_resolution import OpenAIResolutionExtractor, SPEC_010_PROMPT_VERSION
from .pipeline import compile_knowledge_model
from .representation_builder import RepresentationBuilder
from .representations import Representation, RepresentationModel, Salience
from .resolution_compiler import (
    RESOLUTION_COMPILER_VERSION,
    ResolutionCompilationResult,
    ResolutionOutcome,
    ResolutionRequest,
    compile_resolution,
)
from .resolution_strategies import ResolutionStrategyId, get_resolution_strategy
from .semantic_navigation import copy_semantic_navigation_assets
from .structure_detection import StructureDetector
from .structures import DetectedStructureSet, StructureType


EVALUATION_VERSION = "spec-011-v1"
TARGET_TERMS = (
    "quantum state",
    "superposition",
    "probability amplitude",
    "interference",
    "measurement",
    "uncertainty",
    "entanglement",
)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _extraction_to_dict(result: ExtractionResult) -> dict[str, Any]:
    return {
        "entities": [asdict(item) for item in result.entities],
        "claims": [asdict(item) for item in result.claims],
        "relationships": [asdict(item) for item in result.relationships],
        "propositions": [asdict(item) for item in result.propositions],
        "metadata": dict(result.metadata),
    }


class _RecordingExtractor:
    """Record the pre-deduplication proposal without changing the provider boundary."""

    def __init__(self, extractor: KnowledgeExtractor) -> None:
        self.extractor = extractor
        self.result: ExtractionResult | None = None

    def extract(self, document: Any) -> ExtractionResult:
        self.result = self.extractor.extract(document)
        return self.result


def _represented_entity_ids(representation: RepresentationModel) -> set[str]:
    return {
        node.entity_id
        for view in representation.representations
        for node in view.nodes
    }


def select_zoom_focus(
    model: KnowledgeModel,
    representation: RepresentationModel,
) -> tuple[Entity, Representation, dict[str, Any]]:
    """Select a source-supported represented focus only after parent compilation."""
    represented_ids = _represented_entity_ids(representation)
    if not represented_ids:
        raise ValidationError("parent representation exposes no entity eligible for semantic zoom")

    relationship_counts = Counter(
        entity_id
        for relationship in model.relationships
        if relationship.origin is Origin.SOURCE
        for entity_id in (relationship.source_entity_id, relationship.target_entity_id)
    )
    view_counts = Counter(
        node.entity_id
        for view in representation.representations
        for node in view.nodes
    )
    source_text = model.document.text.casefold()
    candidates = []
    for entity in model.entities:
        if entity.id not in represented_ids:
            continue
        names = (entity.name, *entity.aliases)
        matched_terms = tuple(
            term for term in TARGET_TERMS
            if any(term in name.casefold() or name.casefold() in term for name in names)
        )
        mention_count = sum(source_text.count(name.casefold()) for name in names)
        score = (
            bool(matched_terms),
            relationship_counts[entity.id],
            min(mention_count, 99),
            view_counts[entity.id],
            entity.name.casefold(),
        )
        candidates.append((score, entity, matched_terms, mention_count))

    targeted = [item for item in candidates if item[2]]
    pool = targeted or candidates
    _, selected, matched_terms, mention_count = max(pool, key=lambda item: item[0])
    selected_view = next(
        view
        for view in representation.representations
        if any(node.entity_id == selected.id for node in view.nodes)
    )
    diagnostics = {
        "selection_method": "POST_COMPILATION_REPRESENTED_TARGET_SCORE",
        "target_terms_considered": list(TARGET_TERMS),
        "targeted_candidate_count": len(targeted),
        "represented_candidate_count": len(candidates),
        "matched_target_terms": list(matched_terms),
        "source_relationship_degree": relationship_counts[selected.id],
        "source_mention_count": mention_count,
        "representation_occurrence_count": view_counts[selected.id],
        "fallback_to_non_target_entity": not bool(targeted),
    }
    return selected, selected_view, diagnostics


def select_resolution_strategy(
    entity: Entity,
    model: KnowledgeModel,
) -> tuple[ResolutionStrategyId, str]:
    """Use a type-aware strategy only when parent semantics support its role."""
    connected_types = {
        relationship.relationship_type.value
        for relationship in model.relationships
        if entity.id in (relationship.source_entity_id, relationship.target_entity_id)
    }
    if entity.entity_type is EntityType.PROCESS and "PRECEDES" in connected_types:
        return (
            ResolutionStrategyId.PROCESS_STAGES,
            "The focus is a PROCESS with an explicit PRECEDES neighborhood.",
        )
    if entity.entity_type is EntityType.VARIABLE and connected_types.intersection(
        {"CAUSES", "INCREASES", "DECREASES", "AFFECTS", "CONSTRAINS"}
    ):
        return (
            ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD,
            "The focus is a VARIABLE with an explicit causal or constraint neighborhood.",
        )
    if entity.entity_type in {EntityType.COMPONENT, EntityType.SYSTEM} and "PART_OF" in connected_types:
        return (
            ResolutionStrategyId.COMPONENT_INTERNALS,
            "The focus is a component/system with explicit containment semantics.",
        )
    return (
        ResolutionStrategyId.GENERIC_DETAIL,
        "No existing type-aware strategy is justified by the compiled parent neighborhood.",
    )


def _origin_counts(model: KnowledgeModel) -> dict[str, Any]:
    by_kind = {
        "claims": Counter(item.origin.value for item in model.claims),
        "relationships": Counter(item.origin.value for item in model.relationships),
        "propositions": Counter(item.origin.value for item in model.propositions),
    }
    return {
        kind: {origin.value: counts[origin.value] for origin in Origin}
        for kind, counts in by_kind.items()
    } | {
        "total": {
            origin.value: sum(counts[origin.value] for counts in by_kind.values())
            for origin in Origin
        }
    }


def _evidence_integrity(model: KnowledgeModel) -> dict[str, Any]:
    source_items = [
        item for item in (*model.claims, *model.relationships, *model.propositions)
        if item.origin is Origin.SOURCE
    ]
    inferred_items = [
        item for item in (*model.claims, *model.relationships, *model.propositions)
        if item.origin is Origin.INFERRED
    ]
    exact_spans = [
        span.quote == model.document.text[span.start_char:span.end_char]
        for item in source_items for span in item.evidence
    ]
    return {
        "source_item_count": len(source_items),
        "inferred_item_count": len(inferred_items),
        "source_items_with_evidence": sum(bool(item.evidence) for item in source_items),
        "exact_span_count": len(exact_spans),
        "all_source_items_have_evidence": all(item.evidence for item in source_items),
        "all_source_spans_exact": all(exact_spans),
        "all_inferred_items_have_no_evidence": all(not item.evidence for item in inferred_items),
    }


def _structure_counts(structures: DetectedStructureSet) -> dict[str, int]:
    counts = Counter(item.structure_type.value for item in structures.structures)
    return {kind.value: counts[kind.value] for kind in StructureType}


def _representation_diagnostics(
    model: KnowledgeModel,
    representation: RepresentationModel,
) -> dict[str, Any]:
    represented_ids = _represented_entity_ids(representation)
    per_view = []
    for view in representation.representations:
        layout = view.layout
        per_view.append({
            "id": view.id,
            "type": view.representation_type.value,
            "salience": view.salience.value,
            "node_count": len(view.nodes),
            "edge_count": len(view.edges),
            "layout_strategy": layout.strategy if layout else None,
            "layout_width": layout.width if layout else None,
            "layout_height": layout.height if layout else None,
            "layout_diagnostics": dict(layout.diagnostics) if layout else None,
        })
    salience = Counter(view.salience.value for view in representation.representations)
    return {
        "representation_count": len(representation.representations),
        "salience_distribution": {item.value: salience[item.value] for item in Salience},
        "represented_entity_count": len(represented_ids),
        "extracted_entity_count": len(model.entities),
        "represented_to_extracted_entity_ratio": (
            len(represented_ids) / len(model.entities) if model.entities else 0.0
        ),
        "per_representation": per_view,
        "total_crossing_count": sum(
            int(view.layout.diagnostics.get("crossing_count", 0))
            for view in representation.representations if view.layout
        ),
        "total_node_overlap_count": sum(
            int(view.layout.diagnostics.get("node_overlap_count", 0))
            for view in representation.representations if view.layout
        ),
    }


def _generated_exploration(result: ResolutionCompilationResult) -> dict[str, Any]:
    assert result.artifact is not None
    artifact = result.artifact
    child = artifact.representation.to_dict()["representations"][0]
    return {
        "spec": "SPEC-011",
        "id": f"generated-quantum-{artifact.request.focus_entity_id}",
        "domain": "quantum_mechanics",
        "parent_representation_id": artifact.request.parent_representation_id,
        "focus_entity_id": artifact.request.focus_entity_id,
        "focus_label": artifact.request.focus_label,
        "provenance_kind": "GENERATED_SOURCE_GROUNDED",
        "provenance_display_label": "Generated from source",
        "provenance_note": (
            "Automatically compiled only from the selected fixed source revision. SOURCE items "
            "carry exact spans; INFERRED items carry no source evidence."
        ),
        "child_representation": child,
    }


def _human_review_template(source_metadata: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "spec": "SPEC-011",
        "status": "READY_AFTER_REPOSITORY_SEMANTIC_REVIEW",
        "review_order": [
            "Open the original fixed source reference.",
            "Launch the compiled artifact.",
            "Use this to try to understand the topic.",
            "Capture spontaneous reaction before answering structured questions.",
        ],
        "source_title": source_metadata["title"],
        "source_reference": source_metadata["permanent_url"],
        "minimal_instruction": "Use this to try to understand the topic.",
        "spontaneous_reaction": "",
        "questions": {
            "orientation": [
                "Can I quickly see what the source is fundamentally about?",
                "Do I understand the major conceptual neighborhoods?",
                "Does the map reduce the burden of reconstructing structure from prose?",
            ],
            "semantic_usefulness": [
                "Are the displayed relationships meaningful rather than merely grounded?",
                "Does the representation omit or mislead about anything central?",
            ],
            "semantic_zoom": [
                "Does the child feel like peeling another semantic layer?",
                "Is the parent a plausible compression of the child?",
                "Does the deeper model help rather than merely add information?",
            ],
            "evidence_and_trust": [
                "Can I inspect why an important relationship exists?",
                "Does evidence increase confidence without overwhelming the experience?",
            ],
        },
        "decisive_question": (
            "For this quantum-mechanics material, would I prefer to continue learning through "
            "Knowledge Compiler, the original source, or a conventional AI textual explanation? Why?"
        ),
        "overall_verdict": "NOT_EVALUATED",
    }


def _read_source_metadata(path: Path, normalized_text: str) -> dict[str, Any]:
    metadata = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "title", "publisher", "authors", "source_url", "permanent_url", "revision_id",
        "revision_timestamp", "license", "license_url", "redistribution_basis",
        "committed_source_handling", "normalized_sha256",
    }
    missing = sorted(required - set(metadata))
    if missing:
        raise ValidationError(f"source metadata is missing required fields: {missing}")
    actual_hash = _sha256(normalized_text)
    if metadata["normalized_sha256"] != actual_hash:
        raise ValidationError(
            "source text does not match the fixed revision hash: "
            f"expected {metadata['normalized_sha256']}, got {actual_hash}"
        )
    return metadata


def _write_failed_parent_review_artifacts(
    *,
    output_dir: Path,
    source_metadata: Mapping[str, Any],
    source_report: Mapping[str, Any],
    attempts: list[dict[str, Any]],
    error: Exception,
    rejected: ExtractionResult | None,
) -> None:
    proposed_counts = {
        "entities": len(rejected.entities) if rejected else 0,
        "relationships": len(rejected.relationships) if rejected else 0,
        "claims": len(rejected.claims) if rejected else 0,
        "propositions": len(rejected.propositions) if rejected else 0,
    }
    if rejected:
        canonical = deduplicate_entities(rejected)
        deduplication = {
            "status": "COMPLETED_BEFORE_PARENT_VALIDATION",
            "proposed_entity_count": len(rejected.entities),
            "canonical_entity_count": len(canonical.entities),
            "merged_entity_count": len(rejected.entities) - len(canonical.entities),
            "relationship_endpoint_rewrite_count": sum(
                before.source_entity_id != after.source_entity_id
                or before.target_entity_id != after.target_entity_id
                for before, after in zip(
                    rejected.relationships, canonical.relationships, strict=True
                )
            ),
            "strategy": "CONSERVATIVE_NORMALIZED_NAME_OR_ALIAS",
        }
    else:
        deduplication = {
            "status": "NOT_RECONSTRUCTABLE_REJECTED_OUTPUT_UNAVAILABLE",
            "proposed_entity_count": 0,
        }
    _write_json(output_dir / "processing-report.json", {
        "spec": "SPEC-011",
        "source": dict(source_report),
        "processing": {
            "full_source_processing_attempted_first": True,
            "full_source_processing_succeeded": False,
            "strategy": "FULL_SOURCE_SINGLE_REQUEST",
            "segment_count": 1,
            "segmentation_required": False,
            "external_semantic_enrichment": False,
            "failure": str(error),
        },
        "rejected_proposal_counts": proposed_counts,
        "deduplication": deduplication,
    })
    _write_json(output_dir / "repository-semantic-review.json", {
        "spec": "SPEC-011",
        "status": "PENDING_REPOSITORY_SEMANTIC_REVIEW",
        "machine_outcome": "PARENT_EXTRACTION_FAILED",
        "validation_failure": str(error),
        "rejected_output_preserved": rejected is not None,
        "rejected_proposal_counts": proposed_counts,
        "semantic_findings": [],
        "proposition_findings": [],
        "relationship_vocabulary_findings": [],
        "overview_and_layout_findings": [
            "No parent representation or layout was produced because semantic validation failed."
        ],
        "failure_attribution": ["EXTRACTION", "SEMANTIC_RELATIONSHIP"],
        "owner_review": "BLOCKED_NO_VALID_LEARNER_ARTIFACT",
    })
    human_review = _human_review_template(source_metadata)
    human_review.update({
        "status": "BLOCKED_PARENT_EXTRACTION_FAILURE",
        "review_order": [
            "Open the original fixed source reference.",
            "Note that no valid compiled learner artifact exists for this run.",
            "Inspect the preserved failure only after the source if repository review is desired.",
        ],
        "compiled_artifact_available": False,
        "blocking_failure": str(error),
        "overall_verdict": "NOT_EVALUATED",
    })
    _write_json(output_dir / "human-review-template.json", human_review)
    (output_dir / "README.md").write_text(
        "# SPEC-011 preserved negative result\n\n"
        f"Original source: [{source_metadata['title']}]({source_metadata['permanent_url']})\n\n"
        "The full-source provider response failed the existing semantic validation boundary. "
        "No parent `KnowledgeModel`, representation, or child resolution was produced, so there "
        "is no learner-facing viewer to launch for this run.\n\n"
        "Inspect `report.json`, `run-history.json`, `repository-semantic-review.json`, and "
        "`rejected-parent-extraction.json` (when available). Do not treat the rejected proposal "
        "as a valid learning artifact.\n\n"
        "The source-derived text in these artifacts is reused under CC BY-SA 4.0 with attribution "
        "to Wikipedia contributors.\n",
        encoding="utf-8",
    )


def run_quantum_learning_evaluation(
    *,
    source_path: Path,
    source_metadata_path: Path,
    output_dir: Path,
    model: str = DEFAULT_MODEL,
    extractor_factory: Callable[[], KnowledgeExtractor] | None = None,
    resolution_extractor_factory: Callable[[], Any] | None = None,
    prior_run_histories: tuple[Path, ...] = (),
) -> dict[str, Any]:
    """Run exactly one full-source extraction and one automatic resolution attempt."""
    output_dir.mkdir(parents=True, exist_ok=False)
    raw_text = source_path.read_text(encoding="utf-8")
    normalized_text = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    source_metadata = _read_source_metadata(source_metadata_path, normalized_text)
    source_report = {
        **source_metadata,
        "word_count": len(normalized_text.split()),
        "character_count": len(normalized_text),
        "source_processing_strategy": "FULL_SOURCE_SINGLE_REQUEST",
        "segment_count": 1,
        "segmentation_required": False,
        "external_semantic_enrichment": False,
    }
    _write_json(output_dir / "source-metadata.json", source_report)

    attempts: list[dict[str, Any]] = []
    prior_history_files = []
    for history_path in prior_run_histories:
        history = json.loads(history_path.read_text(encoding="utf-8"))
        prior_history_files.append(str(history_path))
        for attempt in history.get("attempts", []):
            attempts.append({**attempt, "preserved_from": str(history_path)})
    extraction_sequence = len(attempts) + 1
    extraction_started_at = _utc_now()
    extraction_started = time.perf_counter()
    recording = _RecordingExtractor(
        extractor_factory() if extractor_factory else OpenAILLMExtractor(model=model)
    )
    try:
        parent = compile_knowledge_model(
            normalized_text,
            recording,
            source_metadata={
                "title": source_metadata["title"],
                "publisher": source_metadata["publisher"],
                "permanent_url": source_metadata["permanent_url"],
                "revision_id": source_metadata["revision_id"],
                "license": source_metadata["license"],
                "normalized_sha256": source_metadata["normalized_sha256"],
            },
        )
    except Exception as exc:
        rejected_output_preserved = recording.result is not None
        extraction_metadata = dict(recording.result.metadata) if recording.result else {}
        if recording.result:
            _write_json(
                output_dir / "rejected-parent-extraction.json",
                _extraction_to_dict(recording.result),
            )
        attempts.append({
            "sequence": extraction_sequence,
            "stage": "PARENT_EXTRACTION",
            "started_at": extraction_started_at,
            "completed_at": _utc_now(),
            "runtime_seconds": round(time.perf_counter() - extraction_started, 3),
            "outcome": "FAILED",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "provider_call_attempted": True,
            "provider": extraction_metadata.get("provider", "openai"),
            "requested_model": model,
            "actual_model": extraction_metadata.get("model"),
            "provider_request_id": extraction_metadata.get("provider_request_id"),
            "prompt_version": extraction_metadata.get("prompt_version", PROMPT_VERSION),
            "retries": 0,
            "usage": dict(extraction_metadata.get("usage", {})),
            "cost": "NOT_AVAILABLE",
            "rejected_output_preserved": rejected_output_preserved,
        })
        _write_json(output_dir / "run-history.json", {
            "spec": "SPEC-011", "attempts": attempts,
            "prior_run_history_files": prior_history_files,
            "hidden_retries_or_favorable_run_selection": False,
            "automatic_retry_count": 0,
            "explicit_semantic_retry_count": max(
                0, sum(item.get("stage") == "PARENT_EXTRACTION" for item in attempts) - 1
            ),
        })
        _write_json(output_dir / "report.json", {
            "spec": "SPEC-011", "evaluation_version": EVALUATION_VERSION,
            "outcome": "PARENT_EXTRACTION_FAILED", "failure": str(exc),
            "failure_attribution": ["EXTRACTION"], "source": source_report,
            "rejected_output_preserved": rejected_output_preserved,
            "prior_run_history_files": prior_history_files,
        })
        _write_failed_parent_review_artifacts(
            output_dir=output_dir,
            source_metadata=source_metadata,
            source_report=source_report,
            attempts=attempts,
            error=exc,
            rejected=recording.result,
        )
        raise

    parent = replace(parent, metadata={
        **dict(parent.metadata),
        "domain": "quantum_mechanics",
        "evaluation_version": EVALUATION_VERSION,
    })
    extraction_runtime = round(time.perf_counter() - extraction_started, 3)
    parent_round_trip = KnowledgeModel.from_dict(parent.to_dict()).to_dict() == parent.to_dict()
    raw_extraction = recording.result
    raw_entity_count = len(raw_extraction.entities) if raw_extraction else len(parent.entities)
    dedup_diagnostics = {
        "proposed_entity_count": raw_entity_count,
        "canonical_entity_count": len(parent.entities),
        "merged_entity_count": raw_entity_count - len(parent.entities),
        "relationship_endpoint_rewrite_count": sum(
            before.source_entity_id != after.source_entity_id
            or before.target_entity_id != after.target_entity_id
            for before, after in zip(
                raw_extraction.relationships if raw_extraction else (),
                parent.relationships,
                strict=False,
            )
        ),
        "strategy": "CONSERVATIVE_NORMALIZED_NAME_OR_ALIAS",
    }
    attempts.append({
        "sequence": extraction_sequence,
        "stage": "PARENT_EXTRACTION",
        "started_at": extraction_started_at,
        "completed_at": _utc_now(),
        "runtime_seconds": extraction_runtime,
        "outcome": "SUCCESS",
        "provider_call_attempted": extractor_factory is None,
        "provider": parent.metadata.get("provider", "fixture"),
        "requested_model": model,
        "actual_model": parent.metadata.get("model"),
        "provider_request_id": parent.metadata.get("provider_request_id"),
        "prompt_version": parent.metadata.get("prompt_version", PROMPT_VERSION),
        "retries": 0,
        "usage": dict(parent.metadata.get("usage", {})),
        "cost": "NOT_AVAILABLE",
    })

    structures = StructureDetector().detect(parent)
    representation = with_layouts(RepresentationBuilder().build(
        parent,
        structures,
        presentation_metadata={
            "domain": "quantum_mechanics",
            "title": "Introduction to quantum mechanics",
        },
    ))
    selected, selected_view, focus_diagnostics = select_zoom_focus(parent, representation)
    strategy_id, strategy_reason = select_resolution_strategy(selected, parent)
    request = ResolutionRequest(
        parent_document_id=parent.document.id,
        parent_representation_id=selected_view.id,
        focus_entity_id=selected.id,
        focus_label=selected.name,
        domain="quantum_mechanics",
        strategy_id=strategy_id,
    )
    parent_before = json.dumps(parent.to_dict(), sort_keys=True, ensure_ascii=False)
    resolution_started_at = _utc_now()
    resolution_started = time.perf_counter()
    resolution_extractor = (
        resolution_extractor_factory()
        if resolution_extractor_factory
        else OpenAIResolutionExtractor(model=model, prompt_version=SPEC_010_PROMPT_VERSION)
    )
    result = compile_resolution(
        parent,
        representation,
        request,
        resolution_extractor,
        compiler_version=RESOLUTION_COMPILER_VERSION,
    )
    resolution_runtime = round(time.perf_counter() - resolution_started, 3)
    parent_immutable = json.dumps(parent.to_dict(), sort_keys=True, ensure_ascii=False) == parent_before
    attempts.append({
        "sequence": extraction_sequence + 1,
        "stage": "CHILD_RESOLUTION",
        "started_at": resolution_started_at,
        "completed_at": _utc_now(),
        "runtime_seconds": resolution_runtime,
        "outcome": result.outcome.value,
        "provider_call_attempted": resolution_extractor_factory is None,
        "provider": result.provider_metadata.get("provider", "fixture"),
        "requested_model": model,
        "actual_model": result.provider_metadata.get("model"),
        "provider_request_id": result.provider_metadata.get("provider_request_id"),
        "prompt_version": result.provider_metadata.get(
            "prompt_version", SPEC_010_PROMPT_VERSION
        ),
        "strategy_id": strategy_id.value,
        "retries": result.retries,
        "usage": dict(result.provider_metadata.get("usage", {})),
        "cost": "NOT_AVAILABLE",
        "reason": result.reason,
        "grounding_failures": list(result.grounding_failures),
    })

    _write_json(output_dir / "parent.knowledge.json", parent.to_dict())
    _write_json(output_dir / "parent.structures.json", structures.to_dict())
    _write_json(output_dir / "parent.representation.json", representation.to_dict())
    _write_json(output_dir / "resolution-result.json", result.to_dict())
    if result.artifact:
        _write_json(output_dir / "child.knowledge.json", result.artifact.child_model.to_dict())
        _write_json(output_dir / "child.structures.json", result.artifact.structures.to_dict())
        _write_json(output_dir / "child.representation.json", result.artifact.representation.to_dict())
        _write_json(output_dir / "generated-exploration.json", _generated_exploration(result))

    parent_counts = {
        "entities": len(parent.entities),
        "relationships": len(parent.relationships),
        "claims": len(parent.claims),
        "propositions": len(parent.propositions),
    }
    child = result.artifact.child_model if result.artifact else None
    child_counts = {
        "entities": len(child.entities) if child else 0,
        "relationships": len(child.relationships) if child else 0,
        "claims": len(child.claims) if child else 0,
        "propositions": len(child.propositions) if child else 0,
    }
    child_structures = result.artifact.structures if result.artifact else None
    child_representation = result.artifact.representation if result.artifact else None
    parent_representation_diagnostics = _representation_diagnostics(parent, representation)
    failure_attribution = []
    if not representation.representations:
        failure_attribution.append("OVERVIEW / SALIENCE")
    if result.outcome is not ResolutionOutcome.SUCCESS:
        failure_attribution.append("SEMANTIC_RESOLUTION")
    if result.grounding_failures:
        failure_attribution.append("GROUNDING")

    report = {
        "spec": "SPEC-011",
        "evaluation_version": EVALUATION_VERSION,
        "outcome": (
            "READY_FOR_OWNER_REVIEW"
            if representation.representations and result.outcome is ResolutionOutcome.SUCCESS
            else "PRESERVED_PARTIAL_OR_NEGATIVE_RESULT"
        ),
        "source": source_report,
        "provider": "openai" if extractor_factory is None else "fixture",
        "requested_model": model,
        "extraction_prompt_version": parent.metadata.get("prompt_version", PROMPT_VERSION),
        "resolution_prompt_version": result.provider_metadata.get(
            "prompt_version", SPEC_010_PROMPT_VERSION
        ),
        "compiler_versions": {
            "evaluation": EVALUATION_VERSION,
            "parent_representation": representation.builder_version,
            "layout": representation.metadata.get("layout_version"),
            "resolution": RESOLUTION_COMPILER_VERSION,
            "semantic_navigation": "spec-007-v1",
        },
        "processing": {
            "full_source_processing_attempted_first": True,
            "full_source_processing_succeeded": True,
            "strategy": "FULL_SOURCE_SINGLE_REQUEST",
            "segment_count": 1,
            "segmentation_required": False,
            "external_semantic_enrichment": False,
            "parent_runtime_seconds": extraction_runtime,
            "resolution_runtime_seconds": resolution_runtime,
        },
        "parent": {
            "counts": parent_counts,
            "origins": _origin_counts(parent),
            "grounding": _evidence_integrity(parent),
            "round_trip": parent_round_trip,
            "deduplication": dedup_diagnostics,
            "relationship_to_entity_ratio": (
                len(parent.relationships) / len(parent.entities) if parent.entities else 0.0
            ),
            "structure_counts": _structure_counts(structures),
            "representation": parent_representation_diagnostics,
        },
        "semantic_zoom": {
            "focus_entity_id": selected.id,
            "focus_label": selected.name,
            "focus_entity_type": selected.entity_type.value,
            "parent_representation_id": selected_view.id,
            "selection_diagnostics": focus_diagnostics,
            "strategy_id": strategy_id.value,
            "strategy_semantic_role": get_resolution_strategy(strategy_id).semantic_role,
            "strategy_reason": strategy_reason,
            "outcome": result.outcome.value,
            "reason": result.reason,
            "grounding_failures": list(result.grounding_failures),
            "counts": child_counts,
            "origins": _origin_counts(child) if child else None,
            "grounding": _evidence_integrity(child) if child else None,
            "structure_counts": _structure_counts(child_structures) if child_structures else None,
            "representation": (
                _representation_diagnostics(child, child_representation)
                if child and child_representation else None
            ),
            "parent_immutable": parent_immutable,
        },
        "proposition_or_vocabulary_gap": "PENDING_REPOSITORY_SEMANTIC_REVIEW",
        "failure_attribution": failure_attribution,
        "live_call_count": sum(bool(attempt.get("provider_call_attempted")) for attempt in attempts),
        "current_run_live_call_count": (
            2 if extractor_factory is None and resolution_extractor_factory is None else 0
        ),
        "automatic_retry_count": 0,
        "explicit_semantic_retry_count": max(
            0, sum(item.get("stage") == "PARENT_EXTRACTION" for item in attempts) - 1
        ),
        "hidden_retries_or_favorable_run_selection": False,
        "external_semantic_enrichment": False,
        "usage": {
            key: sum(int(attempt.get("usage", {}).get(key, 0)) for attempt in attempts)
            for key in ("input_tokens", "output_tokens", "total_tokens")
        },
        "monetary_cost": "NOT_AVAILABLE",
        "parent_immutable": parent_immutable,
        "human_learning_verdict": "PENDING_OWNER_REVIEW",
    }
    _write_json(output_dir / "processing-report.json", {
        "spec": "SPEC-011",
        "source": source_report,
        "processing": report["processing"],
        "deduplication": dedup_diagnostics,
    })
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "run-history.json", {
        "spec": "SPEC-011",
        "attempts": attempts,
        "prior_run_history_files": prior_history_files,
        "hidden_retries_or_favorable_run_selection": False,
        "automatic_retry_count": 0,
        "explicit_semantic_retry_count": report["explicit_semantic_retry_count"],
    })
    _write_json(output_dir / "repository-semantic-review.json", {
        "spec": "SPEC-011",
        "status": "PENDING_REPOSITORY_SEMANTIC_REVIEW",
        "mechanical_integrity": {
            "parent_round_trip": parent_round_trip,
            "parent_grounding": _evidence_integrity(parent),
            "child_grounding": _evidence_integrity(child) if child else None,
            "parent_immutable": parent_immutable,
        },
        "semantic_findings": [],
        "proposition_findings": [],
        "relationship_vocabulary_findings": [],
        "overview_and_layout_findings": [],
        "failure_attribution": failure_attribution,
        "owner_review": "PENDING",
    })
    _write_json(output_dir / "human-review-template.json", _human_review_template(source_metadata))
    manifest_entry: dict[str, Any] = {
        "id": "quantum_mechanics",
        "label": "Introduction to quantum mechanics",
        "representation": "parent.representation.json",
    }
    if result.artifact:
        manifest_entry["exploration"] = "generated-exploration.json"
    _write_json(output_dir / "manifest.json", {
        "spec": "SPEC-011",
        "modes": ["BASELINE", "REPLACEMENT", "CONTEXTUAL"],
        "domains": [manifest_entry],
    })
    (output_dir / "README.md").write_text(
        "# SPEC-011 fixed owner-review artifact\n\n"
        f"Original source: [{source_metadata['title']}]({source_metadata['permanent_url']})\n\n"
        "The source text embedded in the semantic artifacts and source-derived excerpts are "
        "reused under CC BY-SA 4.0 with attribution to Wikipedia contributors. Viewer software "
        "remains under the repository license.\n\n"
        "Launch from the repository root:\n\n"
        "```sh\n"
        ".venv/bin/knowledge-compiler view-representations "
        f"{output_dir.as_posix()} --port 8011\n"
        "```\n\n"
        "Use this to try to understand the topic.\n\n"
        "Capture spontaneous reaction before opening `report.json` or "
        "`repository-semantic-review.json`.\n",
        encoding="utf-8",
    )
    copy_semantic_navigation_assets(output_dir)
    return report
