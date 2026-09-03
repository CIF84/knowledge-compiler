from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from knowledge_compiler.models import (
    Entity,
    EntityType,
    KnowledgeModel,
    Origin,
    Relationship,
    RelationshipType,
    SourceDocument,
    ValidationError,
)
from knowledge_compiler.representation_builder import RepresentationBuilder
from knowledge_compiler.representations import RepresentationModel, Salience
from knowledge_compiler.structure_detection import StructureDetector
from knowledge_compiler.structures import DetectedStructureSet, StructureType


ROOT = Path(__file__).parents[1]
MODELS = ROOT / "examples" / "evaluations" / "spec-003-relationship-semantics-20260903"
STRUCTURES = ROOT / "examples" / "evaluations" / "spec-004-structure-detection-20260903"
PRESENTATION_METADATA = json.loads(
    (ROOT / "tests" / "fixtures" / "domains" / "presentation_metadata.json").read_text()
)


def accepted(domain: str):
    model = KnowledgeModel.from_dict(json.loads((MODELS / f"{domain}.knowledge.json").read_text()))
    structures = DetectedStructureSet.from_dict(
        json.loads((STRUCTURES / f"{domain}.structures.json").read_text())
    )
    return model, structures


def inferred_model() -> KnowledgeModel:
    entities = tuple(Entity(value, value.upper(), f"Description {value}", EntityType.CONCEPT) for value in "abc")
    relationships = (
        Relationship("r1", "a", RelationshipType.CAUSES, "b", "A causes B", (), .8, Origin.INFERRED),
        Relationship("r2", "b", RelationshipType.AFFECTS, "c", "B affects C", (), .7, Origin.INFERRED),
    )
    return KnowledgeModel(SourceDocument("doc", "opaque source text"), entities, (), relationships, {"domain": "test"})


def test_all_detected_structure_types_map_to_presentations() -> None:
    mapped = set()
    for domain in ("electromagnetism", "software_architecture", "economics", "history"):
        model, structures = accepted(domain)
        result = RepresentationBuilder().build(model, structures)
        mapped.update(item.representation_type for item in result.representations)
    assert mapped == set(StructureType)


def test_overlapping_paths_merge_into_branching_models() -> None:
    economics_model, economics_structures = accepted("economics")
    economics = RepresentationBuilder().build(economics_model, economics_structures)
    assert len(economics.representations) == 1
    assert len(economics.representations[0].source_structure_ids) == 4
    assert len(economics.representations[0].edges) == 5

    history_model, history_structures = accepted("history")
    history = RepresentationBuilder().build(history_model, history_structures)
    dependency = next(item for item in history.representations if item.representation_type is StructureType.DEPENDENCY_CHAIN)
    assert len(dependency.source_structure_ids) == 2
    assert len(dependency.edges) == 3


def test_nodes_labels_relationship_semantics_and_evidence_are_preserved() -> None:
    model, structures = accepted("software_architecture")
    result = RepresentationBuilder().build(model, structures)
    result.validate_against(model, structures)
    hierarchy = next(item for item in result.representations if item.representation_type is StructureType.HIERARCHY)
    assert {node.label for node in hierarchy.nodes} >= {"API component", "modular order-processing service"}
    assert all(edge.relationship_type is RelationshipType.PART_OF for edge in hierarchy.edges)
    assert all(edge.relationship_label == "PART OF" for edge in hierarchy.edges)
    assert all(edge.direction == "part_to_whole" for edge in hierarchy.edges)
    assert all(edge.evidence and edge.provenance_status == "SOURCE_EVIDENCE" for edge in hierarchy.edges)


def test_duplicate_support_relationships_and_evidence_survive() -> None:
    model, structures = accepted("economics")
    result = RepresentationBuilder().build(model, structures)
    edge = next(
        edge for edge in result.representations[0].edges
        if edge.source_entity_id == "market-price" and edge.target_entity_id == "quantity-demanded"
    )
    assert edge.relationship_ids == ("rel-higher-price-decreases-demanded", "rel-price-decreases-demanded")
    assert {item.relationship_id for item in edge.evidence} == set(edge.relationship_ids)


def test_inferred_edges_explicitly_have_no_source_evidence() -> None:
    model = inferred_model()
    structures = StructureDetector().detect(model)
    result = RepresentationBuilder().build(model, structures)
    assert all(not edge.evidence for edge in result.representations[0].edges)
    assert all(edge.provenance_status == "INFERRED_NO_SOURCE_EVIDENCE" for edge in result.representations[0].edges)


def test_feedback_is_candidate_primary_and_does_not_claim_polarity() -> None:
    model, structures = accepted("electromagnetism")
    result = RepresentationBuilder().build(
        model, structures, presentation_metadata=PRESENTATION_METADATA["electromagnetism"]
    )
    feedback = next(item for item in result.representations if item.representation_type is StructureType.FEEDBACK_CANDIDATE)
    assert feedback.title == "Feedback candidate"
    assert feedback.salience is Salience.PRIMARY
    assert "polarity is not classified" in feedback.warnings[0]


def test_sparse_and_empty_behavior_is_explicit() -> None:
    model, structures = accepted("electromagnetism")
    result = RepresentationBuilder().build(model, structures)
    hierarchy = next(item for item in result.representations if item.representation_type is StructureType.HIERARCHY)
    assert hierarchy.salience is Salience.SPARSE
    assert "Sparse structure" in hierarchy.warnings[0]

    biology_model, biology_structures = accepted("biology")
    biology = RepresentationBuilder().build(biology_model, biology_structures)
    assert biology.representations == ()
    assert "will not invent a diagram" in biology.empty_state


def test_representation_serialization_and_order_are_deterministic() -> None:
    model, structures = accepted("history")
    first = RepresentationBuilder().build(model, structures)
    second = RepresentationBuilder().build(model, structures)
    assert first.to_dict() == second.to_dict()
    restored = RepresentationModel.from_dict(first.to_dict())
    restored.validate_against(model, structures)
    assert restored == first


def test_validation_rejects_unknown_structure_and_tampered_node() -> None:
    model, structures = accepted("software_architecture")
    result = RepresentationBuilder().build(model, structures)
    representation = result.representations[0]
    with pytest.raises(ValidationError, match="unknown detected structure"):
        invalid = replace(result, representations=(replace(representation, source_structure_ids=("missing",)),))
        invalid.validate_against(model, structures)
    bad_node = replace(representation.nodes[0], label="Invented")
    with pytest.raises(ValidationError, match="does not match"):
        invalid = replace(result, representations=(replace(representation, nodes=(bad_node, *representation.nodes[1:])),))
        invalid.validate_against(model, structures)
    bad_edge = replace(representation.edges[0], meaning="Generic relation")
    with pytest.raises(ValidationError, match="canonical semantics"):
        invalid = replace(result, representations=(replace(representation, edges=(bad_edge, *representation.edges[1:])),))
        invalid.validate_against(model, structures)
