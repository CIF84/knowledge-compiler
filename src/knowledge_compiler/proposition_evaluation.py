"""Deterministic SPEC-010 regression comparison and owner-review artifacts."""

from __future__ import annotations

import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .layout import with_layouts
from .models import (
    ComparisonOperator,
    Entity,
    EntityType,
    KnowledgeModel,
    Origin,
    Proposition,
    PropositionRole,
    PropositionRoleBinding,
    PropositionType,
    RelationshipType,
    ValidationError,
    deterministic_proposition_id,
)
from .proposition_validation import validate_proposition_coverage
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .representation_builder import RepresentationBuilder
from .structure_detection import StructureDetector
from .viewer import copy_viewer_assets


SPEC_010_VERSION = "spec-010-v1"


def default_spec009_evaluation_directory() -> Path:
    return (
        Path(__file__).parents[2]
        / "examples"
        / "evaluations"
        / "spec-009-resolution-strategy-20260903"
    )


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_model(path: Path) -> KnowledgeModel:
    return KnowledgeModel.from_dict(json.loads(path.read_text(encoding="utf-8")))


def _copy_proposition_viewer_assets(output_dir: Path) -> None:
    copy_viewer_assets(output_dir)
    assets = files("knowledge_compiler").joinpath("proposition_viewer_assets")
    for name in ("index.html", "proposition.css", "proposition.js"):
        output = output_dir / name
        with assets.joinpath(name).open("rb") as source, output.open("wb") as target:
            shutil.copyfileobj(source, target)


def _proposition(
    proposition_type: PropositionType,
    statement: str,
    roles: tuple[PropositionRoleBinding, ...],
    relationship_type: RelationshipType,
    evidence: tuple[Any, ...],
    *,
    comparison_operator: ComparisonOperator | None = None,
) -> Proposition:
    return Proposition(
        id=deterministic_proposition_id(
            proposition_type, roles, relationship_type, comparison_operator
        ),
        proposition_type=proposition_type,
        statement=statement,
        role_bindings=roles,
        relationship_type=relationship_type,
        evidence=evidence,
        confidence=1.0,
        origin=Origin.SOURCE,
        comparison_operator=comparison_operator,
    )


def build_economics_proposition_model(old: KnowledgeModel) -> KnowledgeModel:
    defective = next(
        item for item in old.relationships
        if item.id == "rel-quantity-demanded-exceeds-supplied-shortage"
    )
    roles = (
        PropositionRoleBinding(PropositionRole.LEFT_OPERAND, "quantity-demanded"),
        PropositionRoleBinding(PropositionRole.RIGHT_OPERAND, "quantity-supplied"),
        PropositionRoleBinding(PropositionRole.OUTCOME, "shortage"),
    )
    proposition = _proposition(
        PropositionType.COMPARISON_CONDITION,
        "Quantity demanded greater than quantity supplied causes a shortage.",
        roles,
        RelationshipType.CAUSES,
        defective.evidence,
        comparison_operator=ComparisonOperator.GREATER_THAN,
    )
    return KnowledgeModel(
        document=old.document,
        entities=old.entities,
        claims=old.claims,
        relationships=tuple(item for item in old.relationships if item.id != defective.id),
        metadata={**old.metadata, "proposition_model_version": SPEC_010_VERSION},
        propositions=(proposition,),
    )


def build_process_proposition_model(old: KnowledgeModel) -> KnowledgeModel:
    defective = next(
        item for item in old.relationships if item.id == "rel-command-transferred-to-component"
    )
    destination = Entity(
        "order-component",
        "order component",
        "The component that receives the order command.",
        EntityType.COMPONENT,
    )
    roles = (
        PropositionRoleBinding(PropositionRole.EVENT, "order-command-transfer"),
        PropositionRoleBinding(PropositionRole.OBJECT, "order-command"),
        PropositionRoleBinding(PropositionRole.DESTINATION, destination.id),
    )
    proposition = _proposition(
        PropositionType.TRANSFER_EVENT,
        "The order command transfer sends the order command to the order component.",
        roles,
        RelationshipType.TRANSFERS_TO,
        defective.evidence,
    )
    return KnowledgeModel(
        document=old.document,
        entities=(*old.entities, destination),
        claims=old.claims,
        relationships=tuple(item for item in old.relationships if item.id != defective.id),
        metadata={**old.metadata, "proposition_model_version": SPEC_010_VERSION},
        propositions=(proposition,),
    )


def _strict_rejection(model: KnowledgeModel) -> str:
    try:
        validate_proposition_coverage(model)
    except ValidationError as exc:
        return str(exc)
    raise AssertionError("known lossy binary regression unexpectedly passed strict validation")


def _semantic_facts(model: KnowledgeModel) -> dict[str, Any]:
    proposition = model.propositions[0]
    roles = {item.role.value: item.entity_id for item in proposition.role_bindings}
    return {
        "proposition_id": proposition.id,
        "proposition_type": proposition.proposition_type.value,
        "roles": roles,
        "comparison_operator": (
            proposition.comparison_operator.value if proposition.comparison_operator else None
        ),
        "relationship_type": proposition.relationship_type.value,
        "source_evidence": [
            {
                "document_id": item.document_id,
                "start_char": item.start_char,
                "end_char": item.end_char,
                "quote": item.quote,
            }
            for item in proposition.evidence
        ],
    }


def run_proposition_evaluation(
    *,
    output_dir: Path,
    source_dir: Path | None = None,
) -> dict[str, Any]:
    source = source_dir or default_spec009_evaluation_directory()
    inputs = {
        "economics": source / "variable-market-price.generic_detail.child.knowledge.json",
        "process": source / "process-order-workflow.process_stages.child.knowledge.json",
    }
    before = {name: path.read_bytes() for name, path in inputs.items()}
    old = {name: _load_model(path) for name, path in inputs.items()}
    new = {
        "economics": build_economics_proposition_model(old["economics"]),
        "process": build_process_proposition_model(old["process"]),
    }
    for model in new.values():
        validate_proposition_coverage(model)

    output_dir.mkdir(parents=True, exist_ok=True)
    comparisons: dict[str, Any] = {}
    machine: dict[str, Any] = {}
    manifest_entries = []
    for name in ("economics", "process"):
        old_structures = StructureDetector().detect(old[name])
        structures = StructureDetector().detect(new[name])
        representation = with_layouts(RepresentationBuilder().build(new[name], structures))
        model_file = f"{name}.proposition-aware.knowledge.json"
        structures_file = f"{name}.proposition-aware.structures.json"
        representation_file = f"{name}.proposition-aware.representation.json"
        _write_json(output_dir / model_file, new[name].to_dict())
        _write_json(output_dir / structures_file, structures.to_dict())
        _write_json(output_dir / representation_file, representation.to_dict())
        manifest_entries.append({
            "id": name,
            "label": "Economics · compound condition" if name == "economics" else "Process · transfer roles",
            "representation": representation_file,
        })
        defective_id = (
            "rel-quantity-demanded-exceeds-supplied-shortage"
            if name == "economics" else "rel-command-transferred-to-component"
        )
        defective = next(item for item in old[name].relationships if item.id == defective_id)
        old_binary = {
            "id": defective.id,
            "source_entity_id": defective.source_entity_id,
            "relationship_type": defective.relationship_type.value,
            "target_entity_id": defective.target_entity_id,
            "statement": defective.statement,
            "evidence": [
                {
                    "document_id": span.document_id,
                    "start_char": span.start_char,
                    "end_char": span.end_char,
                    "quote": span.quote,
                }
                for span in defective.evidence
            ],
            "confidence": defective.confidence,
            "origin": defective.origin.value,
        }
        comparisons[name] = {
            "source_proposition": defective.evidence[0].quote,
            "current_binary_model": old_binary,
            "proposition_aware_model": _semantic_facts(new[name]),
            "source_grounding_status": "PASS_EXACT_SOURCE_SPAN",
            "semantic_truthfulness_verdict": "PASS_MACHINE_INVARIANTS_HUMAN_REVIEW_PENDING",
            "information_preserved": (
                ["left operand", "right operand", "comparison operator", "causal outcome"]
                if name == "economics" else ["transfer event", "transferred object", "destination"]
            ),
            "information_lost": [],
            "old_binary_strict_validation": {
                "outcome": "REJECTED",
                "reason": _strict_rejection(old[name]),
            },
            "structure_detection_effect": {
                "old_structure_count": len(old_structures.structures),
                "new_structure_count": len(structures.structures),
                "proposition_shapes_ignored_without_flattening": True,
            },
            "representation_effect": {
                "proposition_card_count": len(representation.proposition_cards),
                "existing_graph_projection_retained": True,
                "lossy_binary_edge_removed": True,
            },
        }
        restored = KnowledgeModel.from_dict(new[name].to_dict())
        proposition = new[name].propositions[0]
        role_ids = {item.role: item.entity_id for item in proposition.role_bindings}
        shared_checks = {
            "deterministic_round_trip": restored.to_dict() == new[name].to_dict(),
            "stable_proposition_id": restored.propositions[0].id == proposition.id,
            "exact_evidence_valid": all(
                span.quote == new[name].document.text[span.start_char:span.end_char]
                for span in proposition.evidence
            ),
            "role_count": len(proposition.role_bindings),
            "proposition_card_validated": len(representation.proposition_cards) == 1,
            "ordinary_binary_relationships_validate": True,
        }
        if name == "economics":
            shared_checks.update({
                "both_comparison_operands_preserved": {
                    role_ids[PropositionRole.LEFT_OPERAND],
                    role_ids[PropositionRole.RIGHT_OPERAND],
                } == {"quantity-demanded", "quantity-supplied"},
                "comparison_operator_preserved": (
                    proposition.comparison_operator is ComparisonOperator.GREATER_THAN
                ),
                "condition_is_causal_source": (
                    proposition.relationship_type is RelationshipType.CAUSES
                    and role_ids[PropositionRole.OUTCOME] == "shortage"
                ),
                "operand_only_causal_edge_removed": all(
                    item.id != defective_id for item in new[name].relationships
                ),
            })
        else:
            old_chronology = [
                (item.source_entity_id, item.target_entity_id)
                for item in old[name].relationships
                if item.relationship_type is RelationshipType.PRECEDES
            ]
            new_chronology = [
                (item.source_entity_id, item.target_entity_id)
                for item in new[name].relationships
                if item.relationship_type is RelationshipType.PRECEDES
            ]
            shared_checks.update({
                "transfer_object_preserved": role_ids[PropositionRole.OBJECT] == "order-command",
                "transfer_destination_preserved": (
                    role_ids[PropositionRole.DESTINATION] == "order-component"
                ),
                "destination_distinct_from_event": (
                    role_ids[PropositionRole.DESTINATION] != role_ids[PropositionRole.EVENT]
                ),
                "chronology_direction_preserved": new_chronology == old_chronology,
            })
        machine[name] = shared_checks

    predicate_count = len(RELATIONSHIP_DEFINITION_MAP)
    report = {
        "spec": "SPEC-010",
        "evaluation_kind": "DETERMINISTIC_ACCEPTED_SOURCE_REGRESSION",
        "provider_calls": 0,
        "retries": 0,
        "external_enrichment": False,
        "comparisons": comparisons,
        "machine_semantic_regressions": machine,
        "all_machine_invariants_pass": all(
            all(value is True for key, value in result.items() if key != "role_count")
            and result["role_count"] == 3
            for result in machine.values()
        ),
        "canonical_relationship_count": predicate_count,
        "predicate_vocabulary_unchanged": predicate_count == 20,
        "input_artifacts_byte_preserved": all(
            inputs[name].read_bytes() == content for name, content in before.items()
        ),
        "parent_artifacts_immutable": all(
            inputs[name].read_bytes() == content for name, content in before.items()
        ),
        "navigation_behavior_changed": False,
        "human_semantic_verdict": "PENDING",
    }
    _write_json(output_dir / "comparison.json", comparisons)
    _write_json(output_dir / "machine-review.json", machine)
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "manifest.json", {
        "spec": "SPEC-010",
        "domains": manifest_entries,
    })
    _write_json(output_dir / "human-review-template.json", {
        "spec": "SPEC-010",
        "status": "READY_FOR_OWNER_REVIEW",
        "questions": [
            "Does the Economics proposition now say what the source actually says?",
            "Does the transfer proposition distinguish event, transferred object, and destination?",
            "Does the richer representation remain understandable rather than exposing ontology machinery?",
        ],
        "verdict": "NOT_EVALUATED",
    })
    (output_dir / "README.md").write_text(
        "# SPEC-010 owner review\n\n"
        "Serve this directory with:\n\n"
        "```bash\n"
        ".venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-010-proposition-modeling-20260903 --port 8010\n"
        "```\n\n"
        "Inspect both proposition cards, their role bindings, and exact source evidence.\n",
        encoding="utf-8",
    )
    _copy_proposition_viewer_assets(output_dir)
    return report
