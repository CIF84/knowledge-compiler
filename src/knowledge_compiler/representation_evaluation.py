"""Deterministic five-domain representation generation and integrity evaluation."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .evaluation import DOMAINS
from .models import KnowledgeModel, Origin, ValidationError
from .representation_builder import RepresentationBuilder
from .representations import RepresentationModel, Salience
from .structure_evaluation import default_spec003_models_directory
from .structures import DetectedStructureSet
from .viewer import copy_viewer_assets


def default_spec004_structures_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-004-structure-detection-20260903"


def default_presentation_metadata_path() -> Path:
    return Path(__file__).parents[2] / "tests" / "fixtures" / "domains" / "presentation_metadata.json"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _human_review_template() -> dict[str, Any]:
    dimensions = (
        "orientation", "relationship_clarity", "causal_or_process_clarity",
        "important_structure_identification", "edge_explanation", "cognitive_load",
        "trust_and_provenance", "overall_usefulness",
    )
    return {
        "spec": "SPEC-005",
        "status": "NOT_EVALUATED",
        "instructions": (
            "For each domain compare A: source text, B: KnowledgeModel and detected-structure JSON, "
            "and C: the local rendered representation. Use BETTER, SAME, or WORSE and add brief observations."
        ),
        "rating_vocabulary": ["BETTER", "SAME", "WORSE"],
        "domains": {
            domain: {
                "comparison_inputs": {
                    "source": f"tests/fixtures/domains/{domain}.txt",
                    "knowledge_model": f"examples/evaluations/spec-003-relationship-semantics-20260903/{domain}.knowledge.json",
                    "detected_structures": f"examples/evaluations/spec-004-structure-detection-20260903/{domain}.structures.json",
                    "rendered_representation": f"viewer domain: {domain}",
                },
                "ratings": {dimension: "NOT_EVALUATED" for dimension in dimensions},
                "would_prefer_representation_available": "NOT_EVALUATED",
                "observations": "",
            }
            for domain in ("software_architecture", "economics", "electromagnetism")
        },
        "overall_verdict": "NOT_EVALUATED",
    }


def _integrity(model: KnowledgeModel, representation: RepresentationModel) -> dict[str, Any]:
    relationships = {item.id: item for item in model.relationships}
    expected_evidence = 0
    actual_evidence = 0
    for item in representation.representations:
        for edge in item.edges:
            actual_evidence += len(edge.evidence)
            expected_evidence += sum(len(relationships[value].evidence) for value in edge.relationship_ids)
            if edge.relationship_label != edge.relationship_type.value.replace("_", " "):
                raise ValidationError("displayed relationship label does not preserve its type")
            for relationship_id, origin in zip(edge.relationship_ids, edge.origins):
                if relationships[relationship_id].origin is not origin:
                    raise ValidationError("displayed relationship origin does not match its source")
                if origin is Origin.INFERRED and any(
                    evidence.relationship_id == relationship_id for evidence in edge.evidence
                ):
                    raise ValidationError("inferred relationship fabricated source evidence")
    return {
        "references_valid": True,
        "relationship_types_and_labels_preserved": True,
        "evidence_quotes_copied_from_validated_spans": True,
        "inferred_relationships_fabricate_no_evidence": True,
        "expected_evidence_excerpt_count": expected_evidence,
        "actual_evidence_excerpt_count": actual_evidence,
        "provenance_complete": expected_evidence == actual_evidence,
    }


def prepare_representation_evaluation(
    *, models_dir: Path, structures_dir: Path, output_dir: Path, metadata_path: Path
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=False)
    presentation_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if set(presentation_metadata) != set(DOMAINS):
        raise ValidationError("presentation metadata must cover exactly the five domains")
    builder = RepresentationBuilder()
    results = []
    manifest_domains = []
    for domain in DOMAINS:
        model_path = models_dir / f"{domain}.knowledge.json"
        structures_path = structures_dir / f"{domain}.structures.json"
        model = KnowledgeModel.from_dict(json.loads(model_path.read_text(encoding="utf-8")))
        structures = DetectedStructureSet.from_dict(json.loads(structures_path.read_text(encoding="utf-8")))
        representation = builder.build(
            model, structures, presentation_metadata=presentation_metadata[domain]
        )
        representation.validate_against(model, structures)
        output_name = f"{domain}.representation.json"
        _write_json(output_dir / output_name, representation.to_dict())
        type_counts = Counter(item.representation_type.value for item in representation.representations)
        results.append({
            "domain": domain,
            "input_model": str(model_path),
            "input_structures": str(structures_path),
            "output": output_name,
            "representation_count": len(representation.representations),
            "representation_types": dict(sorted(type_counts.items())),
            "node_count": sum(len(item.nodes) for item in representation.representations),
            "edge_count": sum(len(item.edges) for item in representation.representations),
            "salience": {
                salience.value: sum(item.salience is salience for item in representation.representations)
                for salience in Salience
            },
            "empty_state": representation.empty_state,
            "integrity": _integrity(model, representation),
        })
        manifest_domains.append({
            "id": domain,
            "label": representation.title,
            "representation": output_name,
        })

    report = {
        "spec": "SPEC-005",
        "builder_version": "spec-005-v1",
        "source_model_baseline": "SPEC-003",
        "source_structure_baseline": "SPEC-004",
        "network_or_llm_calls": False,
        "results": results,
        "all_references_valid": all(item["integrity"]["references_valid"] for item in results),
        "all_provenance_complete": all(item["integrity"]["provenance_complete"] for item in results),
    }
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "manifest.json", {"spec": "SPEC-005", "domains": manifest_domains})
    _write_json(output_dir / "human-review-template.json", _human_review_template())
    copy_viewer_assets(output_dir)
    return report
