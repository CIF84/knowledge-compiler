"""SPEC-006 deterministic layout and interaction-integrity evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .evaluation import DOMAINS
from .layout import with_layouts
from .models import KnowledgeModel, Origin, ValidationError
from .representation_evaluation import default_spec004_structures_directory
from .representations import RepresentationModel
from .structure_evaluation import default_spec003_models_directory
from .structures import DetectedStructureSet
from .viewer import copy_viewer_assets


def default_spec005_representations_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-005-minimal-representation-20260903"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _display_path(path: Path) -> str:
    repository_root = Path(__file__).parents[2]
    try:
        return str(path.resolve().relative_to(repository_root.resolve()))
    except ValueError:
        return str(path)


def _semantic_projection(model: RepresentationModel) -> dict[str, Any]:
    """Return every controlled SPEC-005 field, excluding presentation-only layout metadata."""
    raw = model.to_dict()
    raw.pop("builder_version", None)
    raw["metadata"].pop("layout_version", None)
    for representation in raw["representations"]:
        representation.pop("layout", None)
        for edge in representation["edges"]:
            edge.pop("edge_key", None)
    return raw


def _provenance_integrity(model: KnowledgeModel, representation: RepresentationModel) -> bool:
    relationships = {item.id: item for item in model.relationships}
    for view in representation.representations:
        for edge in view.edges:
            for relationship_id, origin in zip(edge.relationship_ids, edge.origins):
                relationship = relationships[relationship_id]
                if relationship.origin is not origin:
                    return False
                if origin is Origin.INFERRED and any(
                    evidence.relationship_id == relationship_id for evidence in edge.evidence
                ):
                    return False
                expected = {
                    (span.document_id, span.start_char, span.end_char, span.quote)
                    for span in relationship.evidence
                }
                actual = {
                    (item.document_id, item.start_char, item.end_char, item.quote)
                    for item in edge.evidence if item.relationship_id == relationship_id
                }
                if actual != expected:
                    return False
    return True


def _human_review_template() -> dict[str, Any]:
    dimensions = (
        "interaction_coherence",
        "direction_and_branching_clarity",
        "spatial_legibility",
        "detail_evidence_attachment",
        "honest_sparse_or_empty_behavior",
        "overall_coherent_mental_model",
    )
    domains = {}
    for domain in DOMAINS:
        domains[domain] = {
            "comparison_inputs": {
                "spec_005": f"SPEC-005 viewer domain: {domain}",
                "spec_006": f"SPEC-006 viewer domain: {domain}",
            },
            "ratings": {dimension: "NOT_EVALUATED" for dimension in dimensions},
            "observations": "",
        }
    return {
        "spec": "SPEC-006",
        "status": "NOT_EVALUATED",
        "instructions": (
            "Compare the committed SPEC-005 and SPEC-006 viewers using the same semantic content. "
            "Exercise edge/control reciprocity, hover preview restoration, node selection, reset, "
            "and representation/domain switching. Use only BETTER, SAME, or WORSE."
        ),
        "rating_vocabulary": ["BETTER", "SAME", "WORSE"],
        "domains": domains,
        "overall_verdict": "NOT_EVALUATED",
    }


def prepare_layout_evaluation(
    *,
    input_dir: Path,
    models_dir: Path,
    structures_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Apply layout to fixed SPEC-005 artifacts and report deterministic integrity."""
    output_dir.mkdir(parents=True, exist_ok=False)
    results = []
    manifest_domains = []
    interaction_maps = []

    for domain in DOMAINS:
        baseline_path = input_dir / f"{domain}.representation.json"
        baseline = RepresentationModel.from_dict(json.loads(baseline_path.read_text(encoding="utf-8")))
        laid_out = with_layouts(baseline)
        model_path = models_dir / f"{domain}.knowledge.json"
        structures_path = structures_dir / f"{domain}.structures.json"
        model = KnowledgeModel.from_dict(json.loads(model_path.read_text(encoding="utf-8")))
        structures = DetectedStructureSet.from_dict(json.loads(structures_path.read_text(encoding="utf-8")))
        laid_out.validate_against(model, structures)
        if _semantic_projection(laid_out) != _semantic_projection(baseline):
            raise ValidationError(f"SPEC-006 changed controlled semantic content for {domain}")

        output_name = f"{domain}.representation.json"
        _write_json(output_dir / output_name, laid_out.to_dict())
        domain_views = []
        domain_maps = []
        for view in laid_out.representations:
            if view.layout is None:
                raise ValidationError("SPEC-006 representation is missing layout metadata")
            edge_keys = [edge.edge_key for edge in view.edges]
            route_keys = [route.edge_key for route in view.layout.edges]
            identity_complete = set(edge_keys) == set(route_keys) and len(edge_keys) == len(set(edge_keys))
            domain_views.append({
                "representation_id": view.id,
                "representation_type": view.representation_type.value,
                "layout_strategy": view.layout.strategy,
                "orientation": view.layout.orientation,
                "node_count": len(view.nodes),
                "edge_count": len(view.edges),
                **view.layout.diagnostics,
                "warnings": list(view.warnings),
                "selection_identity_coverage": {
                    "rendered_edges": len(route_keys),
                    "relationship_controls": len(edge_keys),
                    "mapped_both_directions": identity_complete,
                },
            })
            domain_maps.append({
                "representation_id": view.id,
                "nodes": [node.entity_id for node in view.nodes],
                "relationships": [
                    {
                        "edge_key": edge.edge_key,
                        "source_entity_id": edge.source_entity_id,
                        "target_entity_id": edge.target_entity_id,
                        "relationship_ids": list(edge.relationship_ids),
                        "evidence_count": len(edge.evidence),
                    }
                    for edge in view.edges
                ],
            })

        provenance_ok = _provenance_integrity(model, laid_out)
        direction_ok = all(
            relationship.source_entity_id == edge.source_entity_id
            and relationship.target_entity_id == edge.target_entity_id
            for view in laid_out.representations
            for edge in view.edges
            for relationship_id in edge.relationship_ids
            for relationship in (next(item for item in model.relationships if item.id == relationship_id),)
        )
        results.append({
            "domain": domain,
            "input": _display_path(baseline_path),
            "output": output_name,
            "representations": domain_views,
            "empty_state": laid_out.empty_state,
            "warnings": list(laid_out.warnings),
            "semantic_content_unchanged": True,
            "selection_identity_complete": all(
                item["selection_identity_coverage"]["mapped_both_directions"] for item in domain_views
            ),
            "canonical_direction_integrity": direction_ok,
            "provenance_integrity": provenance_ok,
        })
        interaction_maps.append({"domain": domain, "representations": domain_maps})
        manifest_domains.append({"id": domain, "label": laid_out.title, "representation": output_name})

    report = {
        "spec": "SPEC-006",
        "builder_version": "spec-006-v1",
        "fixed_input_baseline": "SPEC-005 committed representation artifacts",
        "network_or_llm_calls": False,
        "results": results,
        "all_semantic_content_unchanged": all(item["semantic_content_unchanged"] for item in results),
        "all_selection_identity_complete": all(item["selection_identity_complete"] for item in results),
        "all_canonical_directions_preserved": all(item["canonical_direction_integrity"] for item in results),
        "all_provenance_preserved": all(item["provenance_integrity"] for item in results),
        "all_layouts_have_no_node_overlap": all(
            view["node_overlap_count"] == 0 for item in results for view in item["representations"]
        ),
    }
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "interaction-map.json", {"spec": "SPEC-006", "domains": interaction_maps})
    _write_json(output_dir / "manifest.json", {"spec": "SPEC-006", "domains": manifest_domains})
    _write_json(output_dir / "human-review-template.json", _human_review_template())
    copy_viewer_assets(output_dir)
    return report
