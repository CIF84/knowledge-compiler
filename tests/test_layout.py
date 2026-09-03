from __future__ import annotations

import json
from pathlib import Path

from knowledge_compiler.layout import layout_representation, with_layouts
from knowledge_compiler.representations import RepresentationModel
from knowledge_compiler.structures import StructureType


ROOT = Path(__file__).parents[1]
BASELINE = ROOT / "examples" / "evaluations" / "spec-005-minimal-representation-20260903"


def accepted(domain: str) -> RepresentationModel:
    return RepresentationModel.from_dict(
        json.loads((BASELINE / f"{domain}.representation.json").read_text())
    )


def view(domain: str, structure_type: StructureType):
    return next(
        item for item in accepted(domain).representations
        if item.representation_type is structure_type
    )


def test_each_representation_type_has_a_distinct_structure_aware_strategy() -> None:
    examples = {
        StructureType.HIERARCHY: view("software_architecture", StructureType.HIERARCHY),
        StructureType.CAUSAL_PATH: view("economics", StructureType.CAUSAL_PATH),
        StructureType.DEPENDENCY_CHAIN: view("history", StructureType.DEPENDENCY_CHAIN),
        StructureType.PROCESS_CHAIN: view("history", StructureType.PROCESS_CHAIN),
        StructureType.FEEDBACK_CANDIDATE: view("electromagnetism", StructureType.FEEDBACK_CANDIDATE),
    }
    layouts = {kind: layout_representation(representation) for kind, representation in examples.items()}
    assert {layout.strategy for layout in layouts.values()} == {
        "layered_hierarchy", "layered_causal", "layered_dependency",
        "chronological_axis", "explicit_feedback_loop",
    }
    assert layouts[StructureType.HIERARCHY].orientation == "TOP_DOWN"
    assert layouts[StructureType.FEEDBACK_CANDIDATE].orientation == "LOOP"
    assert all(
        layout.orientation == "LEFT_TO_RIGHT"
        for kind, layout in layouts.items()
        if kind not in {StructureType.HIERARCHY, StructureType.FEEDBACK_CANDIDATE}
    )


def test_economics_branching_and_convergence_are_layered_deterministically() -> None:
    representation = view("economics", StructureType.CAUSAL_PATH)
    first = layout_representation(representation)
    second = layout_representation(representation)
    assert first == second
    layers = {node.entity_id: node.layer for node in first.nodes}
    assert layers == {
        "shortage": 0,
        "supply-reduction": 0,
        "upward-price-pressure": 1,
        "market-price": 2,
        "quantity-demanded": 3,
        "quantity-supplied": 3,
    }
    assert first.diagnostics["crossing_count"] == 0
    assert first.diagnostics["node_overlap_count"] == 0
    assert first.diagnostics["canonical_edges_opposing_layout_flow"] == 0


def test_hierarchy_places_whole_above_parts_without_reversing_canonical_edges() -> None:
    representation = view("software_architecture", StructureType.HIERARCHY)
    layout = layout_representation(representation)
    positions = {node.entity_id: node for node in layout.nodes}
    whole = positions["modular-order-processing-service"]
    assert whole.layer == 0
    assert all(
        positions[edge.source_entity_id].y > positions[edge.target_entity_id].y
        for edge in representation.edges
    )
    assert all(edge.target_entity_id == "modular-order-processing-service" for edge in representation.edges)
    assert layout.diagnostics["canonical_edges_opposing_layout_flow"] == len(representation.edges)
    assert layout.diagnostics["crossing_count"] == 0


def test_dependency_and_sparse_process_use_clean_directional_layers() -> None:
    dependency = view("software_architecture", StructureType.DEPENDENCY_CHAIN)
    dependency_layout = layout_representation(dependency)
    layers = {node.entity_id: node.layer for node in dependency_layout.nodes}
    assert layers == {"order-component": 0, "payment-component": 1, "database": 2}

    process = view("history", StructureType.PROCESS_CHAIN)
    process_layout = layout_representation(process)
    assert process_layout.strategy == "chronological_axis"
    assert process_layout.width == 450
    assert process_layout.diagnostics["layer_count"] == 2
    assert process_layout.diagnostics["node_overlap_count"] == 0


def test_feedback_candidate_has_two_visibly_distinct_loop_arcs() -> None:
    representation = view("electromagnetism", StructureType.FEEDBACK_CANDIDATE)
    layout = layout_representation(representation)
    assert all(route.path_kind == "QUADRATIC" for route in layout.edges)
    control_y = sorted(route.points[1].y for route in layout.edges)
    assert control_y[0] < layout.height / 2 < control_y[1]
    assert layout.diagnostics["crossing_count"] == 0
    assert layout.diagnostics["node_overlap_count"] == 0


def test_layout_edge_identity_and_serialization_are_stable() -> None:
    baseline = accepted("economics")
    laid_out = with_layouts(baseline)
    representation = laid_out.representations[0]
    assert {edge.edge_key for edge in representation.edges} == {
        route.edge_key for route in representation.layout.edges
    }
    raw = laid_out.to_dict()
    assert all(edge["edge_key"].startswith("edge-") for edge in raw["representations"][0]["edges"])
    restored = RepresentationModel.from_dict(raw)
    assert restored == laid_out


def test_legacy_spec005_serialization_remains_byte_shape_compatible() -> None:
    path = BASELINE / "economics.representation.json"
    raw = json.loads(path.read_text())
    normalized = json.loads(json.dumps(RepresentationModel.from_dict(raw).to_dict()))
    assert normalized == raw


def test_all_fixed_benchmark_layouts_are_deterministic_and_non_overlapping() -> None:
    for domain in ("electromagnetism", "software_architecture", "economics", "biology", "history"):
        first = with_layouts(accepted(domain))
        second = with_layouts(accepted(domain))
        assert first.to_dict() == second.to_dict()
        assert all(
            representation.layout.diagnostics["node_overlap_count"] == 0
            for representation in first.representations
        )
    biology = with_layouts(accepted("biology"))
    assert biology.representations == ()
    assert biology.empty_state == accepted("biology").empty_state
