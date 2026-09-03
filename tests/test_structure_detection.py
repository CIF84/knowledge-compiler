from __future__ import annotations

import json
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
)
from knowledge_compiler.structure_detection import MAX_CAUSAL_PATH_EDGES, StructureDetector
from knowledge_compiler.structures import DetectedStructureSet, StructureType
from knowledge_compiler.structures import DetectedStructure
from knowledge_compiler.models import ValidationError


CASES = json.loads(
    (Path(__file__).parent / "fixtures" / "structures" / "graph_cases.json").read_text()
)


def model_for(case: str) -> KnowledgeModel:
    raw_edges = CASES[case]
    entity_ids = sorted({value for edge in raw_edges for value in (edge[0], edge[2])})
    entities = tuple(Entity(value, value, "", EntityType.CONCEPT) for value in entity_ids)
    relationships = tuple(
        Relationship(
            f"r-{index}", source, RelationshipType(kind), target,
            f"{source} {kind} {target}", (), 1.0, Origin.INFERRED,
        )
        for index, (source, kind, target) in enumerate(raw_edges)
    )
    return KnowledgeModel(SourceDocument(f"doc-{case}", "synthetic"), entities, (), relationships)


def structures(case: str, kind: StructureType):
    return [item for item in StructureDetector().detect(model_for(case)).structures if item.structure_type is kind]


def test_hierarchy_dag_and_multiple_roots_are_separate_and_directional() -> None:
    hierarchy = structures("clean_hierarchy_dag", StructureType.HIERARCHY)
    assert len(hierarchy) == 1
    assert hierarchy[0].metadata["roots"] == ["root"]
    assert hierarchy[0].metadata["leaves"] == ["leaf"]
    assert hierarchy[0].relationship_types == (RelationshipType.PART_OF,) * 4

    separate = structures("multiple_hierarchy_roots", StructureType.HIERARCHY)
    assert len(separate) == 2
    assert [item.metadata["roots"] for item in separate] == [["root-a"], ["root-b"]]


def test_structural_cycle_terminates_deterministically() -> None:
    first = StructureDetector().detect(model_for("structural_cycle"))
    second = StructureDetector().detect(model_for("structural_cycle"))
    assert first.to_dict() == second.to_dict()
    assert first.structures[0].metadata["contains_cycle"] is True


def test_causal_paths_preserve_predicate_sequence_and_branching() -> None:
    simple = structures("simple_causal_chain", StructureType.CAUSAL_PATH)
    assert [item.entity_ids for item in simple] == [("a", "b", "c")]
    assert simple[0].relationship_types == (RelationshipType.CAUSES, RelationshipType.AFFECTS)

    branching = structures("branching_causal_graph", StructureType.CAUSAL_PATH)
    assert [item.entity_ids for item in branching] == [("a", "b", "c"), ("a", "b", "d")]


def test_causal_path_length_is_bounded() -> None:
    edges = [[f"n{i}", "CAUSES", f"n{i + 1}"] for i in range(MAX_CAUSAL_PATH_EDGES + 2)]
    CASES["long_path"] = edges
    path = structures("long_path", StructureType.CAUSAL_PATH)[0]
    assert len(path.relationship_ids) == MAX_CAUSAL_PATH_EDGES


def test_temporal_and_dependency_chains_preserve_direction() -> None:
    temporal = structures("temporal_chain", StructureType.PROCESS_CHAIN)
    assert [item.entity_ids for item in temporal] == [("a", "b", "c")]
    dependency = structures("dependency_chain", StructureType.DEPENDENCY_CHAIN)
    assert [item.entity_ids for item in dependency] == [("operation", "service", "database")]
    assert not structures("mixed_dependency_directions", StructureType.DEPENDENCY_CHAIN)


def test_feedback_cycle_is_canonical_and_non_causal_cycle_is_excluded() -> None:
    feedback = structures("causal_cycle", StructureType.FEEDBACK_CANDIDATE)
    assert len(feedback) == 1
    assert feedback[0].entity_ids == ("a", "b", "c", "a")
    assert feedback[0].metadata["polarity"] == "UNCLASSIFIED"
    assert not structures("non_causal_cycle", StructureType.FEEDBACK_CANDIDATE)


def test_feedback_detection_is_not_limited_by_causal_path_bound() -> None:
    CASES["long_cycle"] = [
        [f"n{i}", "CAUSES", f"n{(i + 1) % 7}"] for i in range(7)
    ]
    feedback = structures("long_cycle", StructureType.FEEDBACK_CANDIDATE)
    assert len(feedback) == 1
    assert len(feedback[0].relationship_ids) == 7


def test_duplicates_do_not_duplicate_paths_and_preserve_all_provenance() -> None:
    paths = structures("duplicate_edges", StructureType.CAUSAL_PATH)
    assert len(paths) == 1
    assert paths[0].relationship_ids == ("r-0", "r-2")
    assert paths[0].metadata["supporting_relationship_ids_by_edge"][0] == ["r-0", "r-1"]


def test_mixed_families_are_not_reinterpreted_and_disconnected_paths_survive() -> None:
    mixed = StructureDetector().detect(model_for("mixed_relationship_families"))
    assert [item.structure_type for item in mixed.structures] == [
        StructureType.HIERARCHY, StructureType.PROCESS_CHAIN
    ]
    disconnected = structures("disconnected_graph", StructureType.CAUSAL_PATH)
    assert [item.entity_ids for item in disconnected] == [("a", "b", "c"), ("x", "y", "z")]


def test_serialization_round_trip_and_model_provenance_validation() -> None:
    model = model_for("branching_causal_graph")
    detected = StructureDetector().detect(model)
    restored = DetectedStructureSet.from_dict(detected.to_dict())
    restored.validate_against(model)
    assert restored == detected
    assert restored.to_dict() == detected.to_dict()


def test_detected_structure_rejects_invalid_path_and_feedback_shapes() -> None:
    with pytest.raises(ValidationError, match="one more entity"):
        DetectedStructure("x", StructureType.CAUSAL_PATH, ("a", "b"), ("r1", "r2"),
                          (RelationshipType.CAUSES, RelationshipType.CAUSES))
    with pytest.raises(ValidationError, match="return to"):
        DetectedStructure("x", StructureType.FEEDBACK_CANDIDATE, ("a", "b"), ("r",),
                          (RelationshipType.CAUSES,))


@pytest.mark.parametrize("case", CASES)
def test_output_ids_and_order_are_stable(case: str) -> None:
    model = model_for(case)
    assert StructureDetector().detect(model).to_dict() == StructureDetector().detect(model).to_dict()
