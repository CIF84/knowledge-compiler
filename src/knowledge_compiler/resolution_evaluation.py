"""SPEC-008 live evaluation and review-artifact preparation."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Callable

from .models import KnowledgeModel, Origin
from .openai_extractor import DEFAULT_MODEL
from .openai_resolution import OpenAIResolutionExtractor
from .representations import RepresentationModel
from .resolution_compiler import (
    RESOLUTION_PROMPT_VERSION,
    ChildResolutionArtifact,
    ResolutionCompilationResult,
    ResolutionOutcome,
    ResolutionRequest,
    compile_resolution,
)
from .semantic_navigation import copy_semantic_navigation_assets


BENCHMARKS = (
    {
        "domain": "software_architecture",
        "parent_representation_id": "representation-985e777f01fa9ec8",
        "focus_entity_id": "api-component",
        "focus_label": "API component",
        "reference_fixture": "software_architecture.exploration.json",
    },
    {
        "domain": "economics",
        "parent_representation_id": "representation-fe3ba90cb8cfa3d6",
        "focus_entity_id": "market-price",
        "focus_label": "market price",
        "reference_fixture": "economics.exploration.json",
    },
)


def default_parent_models_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-003-relationship-semantics-20260903"


def default_parent_representations_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-006-layout-interaction-20260903"


def default_reference_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-007-progressive-disclosure-20260903"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compare_with_handcrafted(
    result: ResolutionCompilationResult, reference: dict[str, Any]
) -> dict[str, Any]:
    """Record structural facts without treating lexical overlap as quality."""
    reference_child = reference["child_representation"]
    if result.outcome is not ResolutionOutcome.SUCCESS or result.artifact is None:
        return {
            "status": f"NOT_AVAILABLE_{result.outcome.value}",
            "reference_child": reference_child["id"],
            "generated_child": None,
            "dimensions": {
                name: "NOT_EVALUATED"
                for name in (
                    "focus_relevance", "mechanistic_detail_gain", "relationship_truthfulness",
                    "source_grounding", "structure_usefulness", "parent_coherence",
                    "compression_relationship", "cognitive_usefulness",
                )
            },
            "lexical_overlap_score": None,
        }
    artifact = result.artifact
    generated = artifact.representation.representations[0]
    return {
        "status": "READY_FOR_HUMAN_REVIEW",
        "reference_child": reference_child["id"],
        "generated_child": generated.id,
        "deterministic_facts": {
            "reference_node_count": len(reference_child["nodes"]),
            "reference_edge_count": len(reference_child["edges"]),
            "generated_node_count": len(generated.nodes),
            "generated_edge_count": len(generated.edges),
            "generated_source_edge_count": sum(
                any(origin is Origin.SOURCE for origin in edge.origins) for edge in generated.edges
            ),
            "generated_structure_type": generated.representation_type.value,
        },
        "dimensions": {
            "focus_relevance": artifact.assessment.focus_relevance,
            "mechanistic_detail_gain": artifact.assessment.mechanistic_detail_gain,
            "relationship_truthfulness": "REQUIRES_SEMANTIC_REVIEW",
            "source_grounding": artifact.assessment.source_support,
            "structure_usefulness": "REQUIRES_HUMAN_REVIEW",
            "parent_coherence": artifact.assessment.parent_coherence,
            "compression_relationship": artifact.assessment.compression_relationship,
            "cognitive_usefulness": "REQUIRES_HUMAN_REVIEW",
        },
        "lexical_overlap_score": None,
    }


def _generated_exploration(artifact: ChildResolutionArtifact) -> dict[str, Any]:
    child = artifact.representation.to_dict()["representations"][0]
    return {
        "spec": "SPEC-008",
        "id": f"generated-{artifact.request.domain}-{artifact.request.focus_entity_id}",
        "domain": artifact.request.domain,
        "parent_representation_id": artifact.request.parent_representation_id,
        "focus_entity_id": artifact.request.focus_entity_id,
        "focus_label": artifact.request.focus_label,
        "provenance_kind": "GENERATED_SOURCE_GROUNDED",
        "provenance_display_label": "Generated from source",
        "provenance_note": (
            "Automatically compiled from the accepted parent source. Exact source spans are "
            "shown for SOURCE relationships; INFERRED relationships carry no evidence."
        ),
        "child_representation": child,
    }


def _human_review_template(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "spec": "SPEC-008",
        "status": "BLOCKED_PENDING_SUCCESSFUL_LIVE_GENERATION"
        if not any(item["outcome"] == "SUCCESS" for item in results)
        else "READY_AFTER_INDEPENDENT_REPOSITORY_REVIEW",
        "instructions": (
            "Inspect source semantics first. Then compare the handcrafted SPEC-007 child with "
            "the generated SPEC-008 child in Contextual mode. Capture spontaneous reaction "
            "before answering the focused questions."
        ),
        "questions": [
            "Does the generated child feel like peeling one semantic layer?",
            "Is it clearly about the selected parent concept?",
            "Does it expose useful mechanism or detail?",
            "Does source grounding make it trustworthy enough?",
            "Where is the handcrafted reference materially better or worse?",
            "What source-faithful insight, if any, did generation add?",
        ],
        "domains": {
            item["domain"]: {
                "outcome": item["outcome"],
                "spontaneous_reaction": "",
                "semantic_review": "NOT_EVALUATED",
                "contextual_comparison": "NOT_EVALUATED",
                "observations": "",
            }
            for item in results
        },
        "overall_verdict": "NOT_EVALUATED",
    }


def run_resolution_evaluation(
    *,
    models_dir: Path,
    representations_dir: Path,
    reference_dir: Path,
    output_dir: Path,
    model: str = DEFAULT_MODEL,
    extractor_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    """Run the two original-source live attempts and preserve every outcome."""
    output_dir.mkdir(parents=True, exist_ok=False)
    factory = extractor_factory or (lambda: OpenAIResolutionExtractor(model=model))
    results: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    manifest_domains = []

    for benchmark in BENCHMARKS:
        domain = benchmark["domain"]
        model_path = models_dir / f"{domain}.knowledge.json"
        parent_path = representations_dir / f"{domain}.representation.json"
        parent = KnowledgeModel.from_dict(json.loads(model_path.read_text(encoding="utf-8")))
        parent_representation = RepresentationModel.from_dict(json.loads(parent_path.read_text(encoding="utf-8")))
        request = ResolutionRequest(
            parent_document_id=parent.document.id,
            parent_representation_id=benchmark["parent_representation_id"],
            focus_entity_id=benchmark["focus_entity_id"],
            focus_label=benchmark["focus_label"],
            domain=domain,
        )
        result = compile_resolution(parent, parent_representation, request, factory())
        _write_json(output_dir / f"{domain}.resolution-result.json", result.to_dict())
        _write_json(output_dir / f"{domain}.source-scope.json", result.source_scope.to_dict())
        shutil.copyfile(parent_path, output_dir / parent_path.name)
        entry: dict[str, Any] = {"id": domain, "label": parent_representation.title, "representation": parent_path.name}
        if result.artifact:
            _write_json(output_dir / f"{domain}.child.knowledge.json", result.artifact.child_model.to_dict())
            _write_json(output_dir / f"{domain}.child.structures.json", result.artifact.structures.to_dict())
            _write_json(output_dir / f"{domain}.child.representation.json", result.artifact.representation.to_dict())
            exploration_name = f"{domain}.generated-exploration.json"
            _write_json(output_dir / exploration_name, _generated_exploration(result.artifact))
            entry["exploration"] = exploration_name
        manifest_domains.append(entry)
        reference_path = reference_dir / benchmark["reference_fixture"]
        reference = json.loads(reference_path.read_text(encoding="utf-8"))
        comparison = {"domain": domain, **compare_with_handcrafted(result, reference)}
        comparisons.append(comparison)
        usage = dict(result.provider_metadata.get("usage", {}))
        results.append({
            "domain": domain,
            "parent_document_id": parent.document.id,
            "parent_representation_id": request.parent_representation_id,
            "focus_entity_id": request.focus_entity_id,
            "outcome": result.outcome.value,
            "reason": result.reason,
            "source_scope": result.source_scope.to_dict(),
            "provider": "openai",
            "requested_model": model,
            "actual_model": result.provider_metadata.get("model"),
            "prompt_version": RESOLUTION_PROMPT_VERSION,
            "entity_count": len(result.artifact.child_model.entities) if result.artifact else 0,
            "relationship_count": len(result.artifact.child_model.relationships) if result.artifact else 0,
            "claim_count": len(result.artifact.child_model.claims) if result.artifact else 0,
            "source_relationship_count": sum(
                item.origin is Origin.SOURCE for item in result.artifact.child_model.relationships
            ) if result.artifact else 0,
            "inferred_relationship_count": sum(
                item.origin is Origin.INFERRED for item in result.artifact.child_model.relationships
            ) if result.artifact else 0,
            "grounding_failures": list(result.grounding_failures),
            "retries": result.retries,
            "structure_count": len(result.artifact.structures.structures) if result.artifact else 0,
            "representation_count": len(result.artifact.representation.representations) if result.artifact else 0,
            "usage": usage,
            "cost": "NOT_AVAILABLE",
        })

    report = {
        "spec": "SPEC-008",
        "experiment": "original accepted sources",
        "provider": "openai",
        "requested_model": model,
        "prompt_version": RESOLUTION_PROMPT_VERSION,
        "source_scope_strategy": "FULL_DOCUMENT_SMALL_SOURCE",
        "attempts_per_domain": 1,
        "hidden_retries_or_cherry_picking": False,
        "web_or_external_source_enrichment": False,
        "complexity_budget": {
            "maximum_generated_child_depth": 1,
            "benchmark_focus_count": len(BENCHMARKS),
            "new_semantic_predicates": 0,
            "new_runtime_dependencies": 0,
            "automatic_retries": 0,
            "recursive_semantic_ir": False,
            "frontend_rewrite": False,
        },
        "results": results,
        "outcome_counts": {
            outcome.value: sum(item["outcome"] == outcome.value for item in results)
            for outcome in ResolutionOutcome
        },
        "successful_child_count": sum(item["outcome"] == "SUCCESS" for item in results),
        "baseline_parent_artifacts_byte_preserved": all(
            (representations_dir / f"{item['domain']}.representation.json").read_bytes()
            == (output_dir / f"{item['domain']}.representation.json").read_bytes()
            for item in BENCHMARKS
        ),
    }
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "handcrafted-comparison.json", {"spec": "SPEC-008", "results": comparisons})
    _write_json(output_dir / "human-review-template.json", _human_review_template(results))
    _write_json(output_dir / "manifest.json", {
        "spec": "SPEC-008", "modes": ["BASELINE", "REPLACEMENT", "CONTEXTUAL"],
        "domains": manifest_domains,
    })
    (output_dir / "README.md").write_text(
        "# SPEC-008 review\n\n"
        "This directory preserves the original-source live outcomes. Generated child files and "
        "Explore actions exist only for successful compilations.\n\n"
        "```sh\n.venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-008-multi-resolution-20260903 --port 8000\n```\n\n"
        "Compare handcrafted references separately with the SPEC-007 viewer on port 8001.\n",
        encoding="utf-8",
    )
    copy_semantic_navigation_assets(output_dir)
    return report
