from __future__ import annotations

import json
from pathlib import Path

import pytest

from knowledge_compiler.models import (
    ComparisonOperator,
    KnowledgeModel,
    Proposition,
    PropositionRole,
    PropositionType,
    RelationshipType,
    ValidationError,
)
from knowledge_compiler.openai_extractor import extraction_schema
from knowledge_compiler.openai_resolution import build_resolution_instructions, resolution_schema
from knowledge_compiler.proposition_evaluation import (
    build_economics_proposition_model,
    build_process_proposition_model,
    default_spec009_evaluation_directory,
    run_proposition_evaluation,
)
from knowledge_compiler.proposition_validation import validate_proposition_coverage
from knowledge_compiler.relationships import RELATIONSHIP_DEFINITION_MAP
from knowledge_compiler.representation_builder import RepresentationBuilder
from knowledge_compiler.structure_detection import StructureDetector


def old_models() -> tuple[KnowledgeModel, KnowledgeModel]:
    root = default_spec009_evaluation_directory()
    economics = KnowledgeModel.from_dict(json.loads(
        (root / "variable-market-price.generic_detail.child.knowledge.json").read_text()
    ))
    process = KnowledgeModel.from_dict(json.loads(
        (root / "process-order-workflow.process_stages.child.knowledge.json").read_text()
    ))
    return economics, process


def proposition_models() -> tuple[KnowledgeModel, KnowledgeModel]:
    economics, process = old_models()
    return build_economics_proposition_model(economics), build_process_proposition_model(process)


def test_minimal_proposition_vocabulary_and_existing_predicates_are_stable() -> None:
    assert tuple(PropositionType) == (
        PropositionType.COMPARISON_CONDITION,
        PropositionType.TRANSFER_EVENT,
    )
    assert tuple(ComparisonOperator) == (ComparisonOperator.GREATER_THAN,)
    assert len(PropositionRole) == 6
    assert len(RELATIONSHIP_DEFINITION_MAP) == len(RelationshipType) == 20


def test_economics_condition_preserves_both_operands_operator_and_causal_source() -> None:
    economics, _ = proposition_models()
    validate_proposition_coverage(economics)
    proposition = economics.propositions[0]
    roles = {item.role: item.entity_id for item in proposition.role_bindings}
    assert proposition.proposition_type is PropositionType.COMPARISON_CONDITION
    assert proposition.comparison_operator is ComparisonOperator.GREATER_THAN
    assert proposition.relationship_type is RelationshipType.CAUSES
    assert roles == {
        PropositionRole.LEFT_OPERAND: "quantity-demanded",
        PropositionRole.RIGHT_OPERAND: "quantity-supplied",
        PropositionRole.OUTCOME: "shortage",
    }
    assert all(item.id != "rel-quantity-demanded-exceeds-supplied-shortage" for item in economics.relationships)


def test_transfer_event_preserves_event_object_destination_and_chronology() -> None:
    old_process = old_models()[1]
    process = build_process_proposition_model(old_process)
    validate_proposition_coverage(process)
    proposition = process.propositions[0]
    roles = {item.role: item.entity_id for item in proposition.role_bindings}
    assert roles == {
        PropositionRole.EVENT: "order-command-transfer",
        PropositionRole.OBJECT: "order-command",
        PropositionRole.DESTINATION: "order-component",
    }
    assert roles[PropositionRole.EVENT] != roles[PropositionRole.DESTINATION]
    old_precedes = [item for item in old_process.relationships if item.relationship_type is RelationshipType.PRECEDES]
    new_precedes = [item for item in process.relationships if item.relationship_type is RelationshipType.PRECEDES]
    assert new_precedes == old_precedes


def test_proposition_ids_and_serialization_are_deterministic_under_role_reordering() -> None:
    economics, _ = proposition_models()
    value = economics.to_dict()["propositions"][0]
    value.pop("id")
    value["role_bindings"] = tuple(reversed(value["role_bindings"]))
    rebuilt = Proposition.from_dict(value, economics.document.id)
    assert rebuilt.id == economics.propositions[0].id
    assert KnowledgeModel.from_dict(economics.to_dict()).to_dict() == economics.to_dict()


def test_missing_comparison_operand_and_transfer_role_confusion_fail_closed() -> None:
    economics, process = proposition_models()
    condition = economics.to_dict()["propositions"][0]
    condition.pop("id")
    condition["role_bindings"] = [
        item for item in condition["role_bindings"] if item["role"] != "RIGHT_OPERAND"
    ]
    with pytest.raises(ValidationError, match="requires left operand"):
        Proposition.from_dict(condition, economics.document.id)

    transfer = process.to_dict()["propositions"][0]
    transfer.pop("id")
    for binding in transfer["role_bindings"]:
        if binding["role"] == "DESTINATION":
            binding["entity_id"] = "order-command-transfer"
    confused = Proposition.from_dict(transfer, process.document.id)
    with pytest.raises(ValidationError, match="own destination"):
        KnowledgeModel(
            process.document, process.entities, process.claims, process.relationships,
            process.metadata, (confused,),
        )


def test_original_lossy_binary_regressions_are_rejected_by_trusted_gate() -> None:
    economics, process = old_models()
    with pytest.raises(ValidationError, match="COMPARISON_CONDITION"):
        validate_proposition_coverage(economics)
    with pytest.raises(ValidationError, match="explicit domain endpoint"):
        validate_proposition_coverage(process)


def test_general_compilation_pipeline_applies_the_same_strict_gate() -> None:
    from knowledge_compiler.pipeline import compile_knowledge_model

    fixture = (
        default_spec009_evaluation_directory()
        / "variable-market-price.generic_detail.child.knowledge.json"
    )
    raw = json.loads(fixture.read_text())

    class InlineExtractor:
        def extract(self, document):
            from knowledge_compiler.extractor import ExtractionResult

            return ExtractionResult.from_dict({
                "entities": raw["entities"],
                "claims": raw["claims"],
                "relationships": raw["relationships"],
                "metadata": {},
            }, document)

    with pytest.raises(ValidationError, match="COMPARISON_CONDITION"):
        compile_knowledge_model(raw["document"]["text"], InlineExtractor())


def test_provider_schema_and_prompt_distinguish_binary_and_richer_propositions() -> None:
    base = extraction_schema()
    resolution = resolution_schema()
    proposition = base["properties"]["propositions"]["items"]
    assert "propositions" in base["required"] and "propositions" in resolution["required"]
    assert "id" not in proposition["properties"]
    assert proposition["properties"]["proposition_type"]["enum"] == [
        "COMPARISON_CONDITION", "TRANSFER_EVENT"
    ]
    instructions = build_resolution_instructions()
    assert "Never collapse a compound" in instructions and "condition to one operand" in instructions
    assert "event, object, and destination roles" in instructions


def test_representation_exposes_validated_proposition_cards_without_flattening() -> None:
    for model in proposition_models():
        structures = StructureDetector().detect(model)
        representation = RepresentationBuilder().build(model, structures)
        representation.validate_against(model, structures)
        assert len(representation.proposition_cards) == 1
        assert representation.proposition_cards[0].proposition_id == model.propositions[0].id
        assert all(
            model.propositions[0].id not in (edge.source_entity_id, edge.target_entity_id)
            for view in representation.representations for edge in view.edges
        )


def test_controlled_evaluation_is_offline_complete_and_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    report = run_proposition_evaluation(output_dir=first)
    run_proposition_evaluation(output_dir=second)
    assert report["provider_calls"] == 0 and report["retries"] == 0
    assert report["all_machine_invariants_pass"] is True
    assert report["predicate_vocabulary_unchanged"] is True
    assert report["input_artifacts_byte_preserved"] is True
    assert report["parent_artifacts_immutable"] is True
    assert report["navigation_behavior_changed"] is False
    assert report["human_semantic_verdict"] == "PENDING"
    assert {path.name: path.read_bytes() for path in first.iterdir()} == {
        path.name: path.read_bytes() for path in second.iterdir()
    }
    economics = json.loads((first / "economics.proposition-aware.representation.json").read_text())
    labels = {item["role"]: item["label"] for item in economics["proposition_cards"][0]["roles"]}
    assert labels == {
        "LEFT_OPERAND": "quantity demanded",
        "OUTCOME": "shortage",
        "RIGHT_OPERAND": "quantity supplied",
    }
    assert "object" in (first / "human-review-template.json").read_text().lower()
