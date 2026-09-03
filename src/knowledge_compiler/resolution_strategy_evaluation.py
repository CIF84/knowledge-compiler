"""SPEC-009 type-aware versus generic semantic-resolution evaluation."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .layout import with_layouts
from .models import (
    Entity,
    EntityType,
    KnowledgeModel,
    Origin,
    Relationship,
    RelationshipType,
    SourceSpan,
)
from .normalize import normalize_document
from .openai_extractor import DEFAULT_MODEL
from .openai_resolution import (
    SPEC_009_PROMPT_VERSION,
    OpenAIResolutionExtractor,
    build_resolution_input,
    build_resolution_instructions,
)
from .relationships import RELATIONSHIP_DEFINITION_MAP, RelationshipFamily
from .representation_builder import RepresentationBuilder
from .representations import Representation, RepresentationModel
from .resolution_compiler import (
    SPEC_009_COMPILER_VERSION,
    ChildResolutionArtifact,
    ResolutionCompilationResult,
    ResolutionOutcome,
    ResolutionRequest,
    compile_resolution,
)
from .resolution_evaluation import (
    default_parent_models_directory,
    default_parent_representations_directory,
)
from .resolution_strategies import (
    RESOLUTION_STRATEGIES,
    ResolutionStrategyId,
    get_resolution_strategy,
    render_resolution_strategy,
)
from .semantic_navigation import MODES, copy_semantic_navigation_assets
from .structure_detection import StructureDetector
from .structures import StructureType


@dataclass(frozen=True, slots=True)
class StrategyBenchmark:
    id: str
    domain: str
    label: str
    semantic_role: str
    assigned_strategy: ResolutionStrategyId
    parent: KnowledgeModel
    parent_representation: RepresentationModel
    parent_representation_id: str
    focus_entity_id: str
    focus_label: str
    source_kind: str


def default_process_source_path() -> Path:
    return Path(__file__).parents[2] / "tests" / "fixtures" / "spec009" / "order_processing_workflow.txt"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _unique_span(document_text: str, document_id: str, quote: str) -> SourceSpan:
    start = document_text.find(quote)
    if start < 0 or document_text.find(quote, start + 1) >= 0:
        raise ValueError("experimental parent evidence quote must occur exactly once")
    return SourceSpan(document_id, start, start + len(quote), quote)


def build_process_parent(source_path: Path | None = None) -> tuple[KnowledgeModel, RepresentationModel]:
    """Build a deliberately coarse parent over one natural richer process source."""
    path = source_path or default_process_source_path()
    document = normalize_document(
        path.read_text(encoding="utf-8"),
        metadata={
            "domain": "software_architecture_process",
            "filename": path.name,
            "fixture_kind": "SPEC_009_EXPERIMENTAL_RICHER_LOCAL_SOURCE",
        },
    )
    quote = "The order-processing service contains an order-processing workflow for each submitted order."
    model = KnowledgeModel(
        document=document,
        entities=(
            Entity(
                "order-processing-service",
                "order-processing service",
                "A service that handles submitted orders.",
                EntityType.SYSTEM,
            ),
            Entity(
                "order-processing-workflow",
                "order-processing workflow",
                "The process used by the service to handle one submitted order.",
                EntityType.PROCESS,
                aliases=("workflow",),
            ),
        ),
        claims=(),
        relationships=(
            Relationship(
                "parent-rel-workflow-part-of-service",
                "order-processing-workflow",
                RelationshipType.PART_OF,
                "order-processing-service",
                "The order-processing workflow is part of the order-processing service.",
                (_unique_span(document.text, document.id, quote),),
                1.0,
                Origin.SOURCE,
            ),
        ),
        metadata={
            "domain": "software_architecture_process",
            "fixture_kind": "SPEC_009_EXPERIMENTAL_RICHER_LOCAL_SOURCE",
            "abstraction": "coarse parent prepared for bounded strategy evaluation",
        },
    )
    structures = StructureDetector().detect(model)
    representation = with_layouts(RepresentationBuilder().build(model, structures))
    if len(representation.representations) != 1:
        raise ValueError("experimental process parent must produce one representation")
    return model, representation


def benchmark_cases(
    *,
    models_dir: Path | None = None,
    representations_dir: Path | None = None,
    process_source_path: Path | None = None,
) -> tuple[StrategyBenchmark, ...]:
    model_dir = models_dir or default_parent_models_directory()
    representation_dir = representations_dir or default_parent_representations_directory()

    def accepted(domain: str) -> tuple[KnowledgeModel, RepresentationModel]:
        model = KnowledgeModel.from_dict(json.loads(
            (model_dir / f"{domain}.knowledge.json").read_text(encoding="utf-8")
        ))
        representation = RepresentationModel.from_dict(json.loads(
            (representation_dir / f"{domain}.representation.json").read_text(encoding="utf-8")
        ))
        return model, representation

    economics, economics_representation = accepted("economics")
    software, software_representation = accepted("software_architecture")
    process, process_representation = build_process_parent(process_source_path)
    process_representation_id = process_representation.representations[0].id
    return (
        StrategyBenchmark(
            id="variable-market-price",
            domain="economics",
            label="Variable · market price",
            semantic_role="VARIABLE",
            assigned_strategy=ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD,
            parent=economics,
            parent_representation=economics_representation,
            parent_representation_id="representation-fe3ba90cb8cfa3d6",
            focus_entity_id="market-price",
            focus_label="market price",
            source_kind="ACCEPTED_ORIGINAL_SOURCE",
        ),
        StrategyBenchmark(
            id="process-order-workflow",
            domain="software_architecture_process",
            label="Process · order-processing workflow",
            semantic_role="PROCESS",
            assigned_strategy=ResolutionStrategyId.PROCESS_STAGES,
            parent=process,
            parent_representation=process_representation,
            parent_representation_id=process_representation_id,
            focus_entity_id="order-processing-workflow",
            focus_label="order-processing workflow",
            source_kind="SPEC_009_EXPERIMENTAL_RICHER_LOCAL_SOURCE",
        ),
        StrategyBenchmark(
            id="component-api",
            domain="software_architecture",
            label="Component · API component",
            semantic_role="COMPONENT_OR_SYSTEM",
            assigned_strategy=ResolutionStrategyId.COMPONENT_INTERNALS,
            parent=software,
            parent_representation=software_representation,
            parent_representation_id="representation-985e777f01fa9ec8",
            focus_entity_id="api-component",
            focus_label="API component",
            source_kind="ACCEPTED_ORIGINAL_SOURCE",
        ),
    )


PROCESS_ORIGINAL_SOURCE_ASSESSMENT = {
    "domain": "software_architecture",
    "source_kind": "ACCEPTED_ORIGINAL_SOURCE",
    "outcome": "INSUFFICIENT_SOURCE_DETAIL",
    "provider_call_made": False,
    "candidate_process_concepts": ["purchase-authorization", "database-schema-change"],
    "reason": (
        "The accepted source names process-like concepts but provides no supported internal "
        "stage sequence, and neither process concept appears in an accepted parent representation."
    ),
    "richer_source_procedure": "ONE_CONTROLLED_LOCAL_FIXTURE",
}


def _request(case: StrategyBenchmark, strategy_id: ResolutionStrategyId) -> ResolutionRequest:
    return ResolutionRequest(
        parent_document_id=case.parent.document.id,
        parent_representation_id=case.parent_representation_id,
        focus_entity_id=case.focus_entity_id,
        focus_label=case.focus_label,
        domain=case.domain,
        strategy_id=strategy_id,
    )


def _selected_representation(
    artifact: ChildResolutionArtifact,
    strategy_id: ResolutionStrategyId,
) -> Representation:
    preferences = {
        ResolutionStrategyId.PROCESS_STAGES: (StructureType.PROCESS_CHAIN, StructureType.DEPENDENCY_CHAIN),
        ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD: (StructureType.CAUSAL_PATH, StructureType.FEEDBACK_CANDIDATE),
        ResolutionStrategyId.COMPONENT_INTERNALS: (StructureType.HIERARCHY, StructureType.DEPENDENCY_CHAIN),
        ResolutionStrategyId.GENERIC_DETAIL: (),
    }[strategy_id]
    for preferred in preferences:
        match = next(
            (item for item in artifact.representation.representations if item.representation_type is preferred),
            None,
        )
        if match is not None:
            return match
    return artifact.representation.representations[0]


def _strategy_diagnostics(
    result: ResolutionCompilationResult,
    strategy_id: ResolutionStrategyId,
) -> dict[str, Any]:
    strategy = get_resolution_strategy(strategy_id)
    if result.artifact is None:
        return {
            "strategy_id": strategy.id.value,
            "semantic_role": strategy.semantic_role,
            "outcome": result.outcome.value,
            "pattern_features": "NOT_AVAILABLE",
        }
    child = result.artifact.child_model
    relationships = child.relationships
    family_counts = Counter(
        RELATIONSHIP_DEFINITION_MAP[item.relationship_type].family.value for item in relationships
    )
    type_counts = Counter(item.relationship_type.value for item in relationships)
    structure_counts = Counter(
        item.structure_type.value for item in result.artifact.structures.structures
    )
    focus_ids = {
        entity.id for entity in child.entities
        if result.request.focus_label.casefold() in entity.name.casefold()
        or entity.name.casefold() in result.request.focus_label.casefold()
    }
    causal_types = {
        kind for kind, definition in RELATIONSHIP_DEFINITION_MAP.items()
        if definition.family is RelationshipFamily.CAUSAL
    }
    causal_incoming = sum(
        item.relationship_type in causal_types and item.target_entity_id in focus_ids
        for item in relationships
    )
    causal_outgoing = sum(
        item.relationship_type in causal_types and item.source_entity_id in focus_ids
        for item in relationships
    )
    pattern_features = {
        "process_stage_entity_count": sum(
            entity.entity_type is EntityType.PROCESS for entity in child.entities
        ),
        "precedence_relationship_count": type_counts[RelationshipType.PRECEDES.value],
        "dependency_relationship_count": family_counts[RelationshipFamily.DEPENDENCY.value],
        "process_chain_count": structure_counts[StructureType.PROCESS_CHAIN.value],
        "causal_relationship_count": family_counts[RelationshipFamily.CAUSAL.value],
        "focus_matching_entity_count": len(focus_ids),
        "focus_causal_incoming_count": causal_incoming,
        "focus_causal_outgoing_count": causal_outgoing,
        "feedback_candidate_count": structure_counts[StructureType.FEEDBACK_CANDIDATE.value],
        "part_of_relationship_count": type_counts[RelationshipType.PART_OF.value],
        "interaction_relationship_count": family_counts[RelationshipFamily.INTERACTION.value],
        "hierarchy_count": structure_counts[StructureType.HIERARCHY.value],
    }
    return {
        "strategy_id": strategy.id.value,
        "semantic_role": strategy.semantic_role,
        "outcome": result.outcome.value,
        "pattern_features": pattern_features,
        "diagnostic_note": "Pattern features are descriptive diagnostics, not a universal quality score.",
    }


def _result_summary(
    run_id: str,
    case: StrategyBenchmark,
    strategy_id: ResolutionStrategyId,
    result: ResolutionCompilationResult,
) -> dict[str, Any]:
    artifact = result.artifact
    child = artifact.child_model if artifact else None
    usage = dict(result.provider_metadata.get("usage", {}))
    return {
        "run_id": run_id,
        "benchmark_id": case.id,
        "domain": case.domain,
        "focus_semantic_role": case.semantic_role,
        "focus_entity_id": case.focus_entity_id,
        "focus_label": case.focus_label,
        "strategy_id": strategy_id.value,
        "source_kind": case.source_kind,
        "outcome": result.outcome.value,
        "reason": result.reason,
        "provider": result.provider_metadata.get("provider", "openai"),
        "actual_model": result.provider_metadata.get("model"),
        "prompt_version": result.provider_metadata.get("prompt_version", SPEC_009_PROMPT_VERSION),
        "compiler_version": artifact.compiler_version if artifact else SPEC_009_COMPILER_VERSION,
        "source_scope": result.source_scope.to_dict(),
        "entity_count": len(child.entities) if child else 0,
        "relationship_count": len(child.relationships) if child else 0,
        "claim_count": len(child.claims) if child else 0,
        "source_relationship_count": sum(item.origin is Origin.SOURCE for item in child.relationships) if child else 0,
        "inferred_relationship_count": sum(item.origin is Origin.INFERRED for item in child.relationships) if child else 0,
        "source_claim_count": sum(item.origin is Origin.SOURCE for item in child.claims) if child else 0,
        "inferred_claim_count": sum(item.origin is Origin.INFERRED for item in child.claims) if child else 0,
        "grounding_failures": list(result.grounding_failures),
        "rejected_extraction_preserved": result.rejected_extraction is not None,
        "retries": result.retries,
        "structure_count": len(artifact.structures.structures) if artifact else 0,
        "structure_types": sorted({item.structure_type.value for item in artifact.structures.structures}) if artifact else [],
        "representation_count": len(artifact.representation.representations) if artifact else 0,
        "representation_types": sorted({item.representation_type.value for item in artifact.representation.representations}) if artifact else [],
        "usage": usage,
        "cost": "NOT_AVAILABLE",
    }


def _generated_exploration(
    case: StrategyBenchmark,
    strategy_id: ResolutionStrategyId,
    artifact: ChildResolutionArtifact,
) -> dict[str, Any]:
    selected = _selected_representation(artifact, strategy_id)
    selected_value = next(
        item for item in artifact.representation.to_dict()["representations"]
        if item["id"] == selected.id
    )
    return {
        "spec": "SPEC-009",
        "id": f"generated-{case.id}-{strategy_id.value.lower()}",
        "domain": case.domain,
        "parent_representation_id": artifact.request.parent_representation_id,
        "focus_entity_id": artifact.request.focus_entity_id,
        "focus_label": artifact.request.focus_label,
        "resolution_strategy": get_resolution_strategy(strategy_id).to_dict(),
        "provenance_kind": "GENERATED_SOURCE_GROUNDED",
        "provenance_display_label": "Generated from source",
        "provenance_note": (
            "Compiled with the recorded resolution strategy. Exact source spans are shown for "
            "SOURCE relationships; INFERRED relationships carry no evidence."
        ),
        "child_representation": selected_value,
    }


def _comparison(
    case: StrategyBenchmark,
    generic: tuple[dict[str, Any], dict[str, Any]],
    type_aware: tuple[dict[str, Any], dict[str, Any]],
    source_scope_equivalent: bool,
    parent_context_equivalent: bool,
) -> dict[str, Any]:
    generic_summary, generic_diagnostics = generic
    aware_summary, aware_diagnostics = type_aware
    return {
        "benchmark_id": case.id,
        "focus_semantic_role": case.semantic_role,
        "focus": case.focus_label,
        "generic_run_id": generic_summary["run_id"],
        "type_aware_run_id": aware_summary["run_id"],
        "assigned_strategy": case.assigned_strategy.value,
        "experimental_isolation": {
            "source_scope_equivalent": source_scope_equivalent,
            "parent_context_equivalent_except_strategy_metadata": parent_context_equivalent,
            "provider_model_grounding_relationship_grammar_downstream_pipeline_held_constant": True,
        },
        "machine_comparison": {
            "generic": {
                "outcome": generic_summary["outcome"],
                "counts": {key: generic_summary[key] for key in (
                    "entity_count", "relationship_count", "claim_count",
                    "source_relationship_count", "inferred_relationship_count",
                    "structure_count", "representation_count",
                )},
                "strategy_pattern_diagnostics": generic_diagnostics,
            },
            "type_aware": {
                "outcome": aware_summary["outcome"],
                "counts": {key: aware_summary[key] for key in (
                    "entity_count", "relationship_count", "claim_count",
                    "source_relationship_count", "inferred_relationship_count",
                    "structure_count", "representation_count",
                )},
                "strategy_pattern_diagnostics": aware_diagnostics,
            },
        },
        "qualitative_dimensions": {
            "grounding_integrity": "REVIEW_RECORDED_OUTCOMES",
            "focus_relevance": "REQUIRES_SEMANTIC_REVIEW",
            "resolution_gain": "REQUIRES_SEMANTIC_REVIEW",
            "strategy_fit": "REQUIRES_SEMANTIC_REVIEW",
            "structural_usefulness": "REQUIRES_HUMAN_REVIEW",
            "parent_child_compression_relationship": "REQUIRES_HUMAN_REVIEW",
            "cognitive_usefulness": "REQUIRES_HUMAN_REVIEW",
        },
        "lexical_overlap_score": None,
        "owner_verdict": "NOT_EVALUATED",
    }


def _human_review_template(cases: tuple[StrategyBenchmark, ...]) -> dict[str, Any]:
    return {
        "spec": "SPEC-009",
        "status": "READY_AFTER_INDEPENDENT_REPOSITORY_AND_SEMANTIC_REVIEW",
        "rating_vocabulary": ["TYPE_AWARE_BETTER", "GENERIC_BETTER", "SAME", "BOTH_WEAK"],
        "instructions": (
            "Open each Generic and Type-aware pair in Contextual/Layers mode. Capture spontaneous "
            "reaction before answering the focused questions. Do not interpret owner-only review "
            "as general learner benefit."
        ),
        "questions": [
            "Which child feels more like a genuine semantic zoom?",
            "Which stays more coherent with the parent focus?",
            "Does the strategy produce the expected explanatory form?",
            "Does it omit important source-grounded information the generic child captured?",
            "Does strategy guidance reduce or increase forced semantics?",
            "Can the parent plausibly compress the child?",
            "Would this strategy help while actually learning the topic?",
        ],
        "benchmarks": {
            case.id: {
                "focus": case.focus_label,
                "assigned_strategy": case.assigned_strategy.value,
                "spontaneous_reaction": "",
                "semantic_review": "NOT_EVALUATED",
                "compression_review": {
                    "does_child_explain_parent_at_finer_resolution": "NOT_EVALUATED",
                    "could_parent_compress_child": "NOT_EVALUATED",
                    "information_lost_at_parent_resolution": "",
                    "is_information_loss_appropriate": "NOT_EVALUATED",
                },
                "verdict": "NOT_EVALUATED",
                "observations": "",
            }
            for case in cases
        },
        "overall_product_decision": "NOT_EVALUATED",
    }


def run_resolution_strategy_evaluation(
    *,
    output_dir: Path,
    model: str = DEFAULT_MODEL,
    models_dir: Path | None = None,
    representations_dir: Path | None = None,
    process_source_path: Path | None = None,
    extractor_factory: Callable[[StrategyBenchmark, ResolutionStrategyId], Any] | None = None,
) -> dict[str, Any]:
    """Run three paired Generic/type-aware attempts and preserve every result."""
    output_dir.mkdir(parents=True, exist_ok=False)
    cases = benchmark_cases(
        models_dir=models_dir,
        representations_dir=representations_dir,
        process_source_path=process_source_path,
    )
    live_provider = extractor_factory is None
    factory = extractor_factory or (
        lambda _case, _strategy: OpenAIResolutionExtractor(
            model=model, prompt_version=SPEC_009_PROMPT_VERSION
        )
    )
    summaries: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []
    equivalence: list[dict[str, Any]] = []
    manifest_domains: list[dict[str, Any]] = []
    parent_immutability: dict[str, bool] = {}

    _write_json(output_dir / "strategy-registry.json", {
        "spec": "SPEC-009",
        "strategies": [item.to_dict() for item in RESOLUTION_STRATEGIES],
        "benchmark_mapping": {
            case.id: {
                "semantic_role": case.semantic_role,
                "focus": case.focus_label,
                "strategy_id": case.assigned_strategy.value,
            }
            for case in cases
        },
    })
    _write_json(output_dir / "process.original-source-insufficiency.json", PROCESS_ORIGINAL_SOURCE_ASSESSMENT)
    process_source = process_source_path or default_process_source_path()
    shutil.copyfile(process_source, output_dir / "process.experimental-source.txt")

    for case in cases:
        parent_before = json.dumps(case.parent.to_dict(), sort_keys=True)
        parent_name = f"{case.id}.parent.representation.json"
        _write_json(output_dir / parent_name, case.parent_representation.to_dict())
        _write_json(output_dir / f"{case.id}.parent.knowledge.json", case.parent.to_dict())
        paired: dict[ResolutionStrategyId, tuple[dict[str, Any], dict[str, Any], ResolutionCompilationResult]] = {}
        requests = (
            _request(case, ResolutionStrategyId.GENERIC_DETAIL),
            _request(case, case.assigned_strategy),
        )
        input_payloads = []
        for sequence_in_pair, request in enumerate(requests, start=1):
            strategy_id = request.strategy_id
            run_id = f"{case.id}.{strategy_id.value.lower()}"
            result = compile_resolution(
                case.parent,
                case.parent_representation,
                request,
                factory(case, strategy_id),
                compiler_version=SPEC_009_COMPILER_VERSION,
            )
            result_name = f"{run_id}.resolution-result.json"
            _write_json(output_dir / result_name, result.to_dict())
            _write_json(output_dir / f"{run_id}.source-scope.json", result.source_scope.to_dict())
            summary = _result_summary(run_id, case, strategy_id, result)
            diagnostic = {"run_id": run_id, **_strategy_diagnostics(result, strategy_id)}
            summaries.append(summary)
            diagnostics.append(diagnostic)
            paired[strategy_id] = (summary, diagnostic, result)
            history.append({
                "sequence": len(history) + 1,
                "pair_sequence": sequence_in_pair,
                "run_id": run_id,
                "benchmark_id": case.id,
                "strategy_id": strategy_id.value,
                "outcome": result.outcome.value,
                "provider_call_attempted": live_provider,
                "provider_request_id": result.provider_metadata.get("provider_request_id"),
                "retries": result.retries,
            })
            input_payloads.append(json.loads(build_resolution_input(
                request, case.parent, result.source_scope
            )))
            manifest_entry: dict[str, Any] = {
                "id": run_id,
                "label": f"{case.label} · {'Generic' if strategy_id is ResolutionStrategyId.GENERIC_DETAIL else 'Type-aware'}",
                "representation": parent_name,
                "strategy_id": strategy_id.value,
            }
            if result.artifact is not None:
                _write_json(output_dir / f"{run_id}.child.knowledge.json", result.artifact.child_model.to_dict())
                _write_json(output_dir / f"{run_id}.child.structures.json", result.artifact.structures.to_dict())
                _write_json(output_dir / f"{run_id}.child.representation.json", result.artifact.representation.to_dict())
                exploration_name = f"{run_id}.generated-exploration.json"
                _write_json(
                    output_dir / exploration_name,
                    _generated_exploration(case, strategy_id, result.artifact),
                )
                manifest_entry["exploration"] = exploration_name
            manifest_domains.append(manifest_entry)

        generic = paired[ResolutionStrategyId.GENERIC_DETAIL]
        type_aware = paired[case.assigned_strategy]
        scope_equivalent = generic[2].source_scope.to_dict() == type_aware[2].source_scope.to_dict()
        generic_input, aware_input = input_payloads
        generic_input.pop("resolution_strategy")
        aware_input.pop("resolution_strategy")
        context_equivalent = generic_input == aware_input
        equivalence.append({
            "benchmark_id": case.id,
            "generic_run_id": generic[0]["run_id"],
            "type_aware_run_id": type_aware[0]["run_id"],
            "source_scope_equivalent": scope_equivalent,
            "parent_context_equivalent_except_strategy_metadata": context_equivalent,
        })
        comparisons.append(_comparison(
            case,
            (generic[0], generic[1]),
            (type_aware[0], type_aware[1]),
            scope_equivalent,
            context_equivalent,
        ))
        parent_immutability[case.id] = json.dumps(case.parent.to_dict(), sort_keys=True) == parent_before

    prompt_diagnostics = {
        strategy.id.value: {
            "strategy_block_characters": len(render_resolution_strategy(strategy)),
            "full_instructions_characters": len(build_resolution_instructions(strategy.id)),
            "delta_full_characters_vs_generic": (
                len(build_resolution_instructions(strategy.id))
                - len(build_resolution_instructions(ResolutionStrategyId.GENERIC_DETAIL))
            ),
        }
        for strategy in RESOLUTION_STRATEGIES
    }
    outcome_counts = {
        outcome.value: sum(item["outcome"] == outcome.value for item in summaries)
        for outcome in ResolutionOutcome
    }
    report = {
        "spec": "SPEC-009",
        "experiment": "paired generic versus explicit semantic-role strategy",
        "provider": "openai" if live_provider else "fixture",
        "requested_model": model,
        "prompt_version": SPEC_009_PROMPT_VERSION,
        "compiler_version": SPEC_009_COMPILER_VERSION,
        "generation_attempt_count": len(summaries),
        "provider_call_count": len(summaries) if live_provider else 0,
        "hidden_retries_or_favorable_run_selection": False,
        "web_or_external_source_enrichment": False,
        "original_process_source_assessment": PROCESS_ORIGINAL_SOURCE_ASSESSMENT,
        "results": summaries,
        "outcome_counts": outcome_counts,
        "successful_child_count": outcome_counts[ResolutionOutcome.SUCCESS.value],
        "source_scope_equivalence": {
            "all_pairs_equivalent": all(item["source_scope_equivalent"] for item in equivalence),
            "all_parent_context_equivalent_except_strategy_metadata": all(
                item["parent_context_equivalent_except_strategy_metadata"] for item in equivalence
            ),
            "pairs": equivalence,
        },
        "parent_immutability": {
            "all_parents_unchanged": all(parent_immutability.values()),
            "benchmarks": parent_immutability,
        },
        "prompt_diagnostics": prompt_diagnostics,
        "prompt_change_outside_strategy_section": (
            "The common SPEC-008 wording was structurally refactored only to insert the canonical "
            "strategy block; its grounding, evidence, insufficient-source, and trust rules remain unchanged."
        ),
        "complexity_budget": {
            "type_aware_strategy_count": 3,
            "generic_control_count": 1,
            "maximum_generated_child_depth": 1,
            "new_runtime_dependencies": 0,
            "new_semantic_ir_fields": 0,
            "new_semantic_ir_types": 0,
            "new_experimental_boundary_types": 2,
            "new_canonical_predicates": 0,
            "source_fixtures_added": 1,
            "automatic_retries": 0,
            "recursive_architecture_introduced": False,
            "navigation_redesign": False,
            "personalization_machinery": False,
        },
        "canonical_relationship_count": len(RELATIONSHIP_DEFINITION_MAP),
        "navigation_modes": list(MODES),
        "cost_note": (
            "Token usage is recorded per run. Monetary cost remains NOT_AVAILABLE unless the "
            "provider response supplies an authoritative charge."
        ),
    }
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "strategy-diagnostics.json", {"spec": "SPEC-009", "runs": diagnostics})
    _write_json(output_dir / "comparison-report.json", {"spec": "SPEC-009", "comparisons": comparisons})
    _write_json(output_dir / "source-scope-equivalence.json", {
        "spec": "SPEC-009", **report["source_scope_equivalence"]
    })
    _write_json(output_dir / "run-history.json", {
        "spec": "SPEC-009",
        "attempts": history,
        "hidden_retries_or_favorable_run_selection": False,
        "automatic_retry_count": 0,
    })
    _write_json(output_dir / "human-review-template.json", _human_review_template(cases))
    _write_json(output_dir / "manifest.json", {
        "spec": "SPEC-009", "modes": list(MODES), "domains": manifest_domains,
    })
    (output_dir / "README.md").write_text(
        "# SPEC-009 strategy review\n\n"
        "This directory preserves all three Generic/type-aware pairs. Explore actions exist only "
        "for successful, validated children. Capture spontaneous reaction before completing the "
        "human-review template.\n\n"
        "```sh\n.venv/bin/knowledge-compiler view-representations "
        f"{output_dir.as_posix()} --port 8000\n```\n",
        encoding="utf-8",
    )
    copy_semantic_navigation_assets(output_dir)
    return report
