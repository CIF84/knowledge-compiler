from __future__ import annotations

import hashlib
import json
from pathlib import Path

from knowledge_compiler.continuous_navigation import (
    INITIAL_CAMERA,
    CameraState,
    build_navigation_fixture,
    canonical_navigation_bytes,
    drag_pan,
    focus_camera_target,
    point_visible,
    screen_to_world,
    world_to_screen,
)
from knowledge_compiler.continuous_navigation_evaluation import (
    default_baseline_assets_directory,
    default_baseline_document,
    default_spec006_directory,
    prepare_continuous_navigation_evaluation,
)


def hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def test_navigation_fixture_is_sufficient_deterministic_and_truthfully_labeled() -> None:
    first = build_navigation_fixture()
    second = build_navigation_fixture()

    assert canonical_navigation_bytes(first) == canonical_navigation_bytes(second)
    assert len(first["nodes"]) == 24
    assert len(first["edges"]) == 28
    assert first["fixture_status"] == "EXPERIMENTAL_PRESENTATION_NAVIGATION_FIXTURE_NOT_EXTRACTED_SOURCE"
    assert first["document"]["metadata"]["semantic_benchmark"] is False
    assert {item["relationship_type"] for item in first["edges"]} == {
        "CREATES", "MEASURED_BY", "PRECEDES", "REQUIRES"
    }
    assert first["world"]["layout_recomputed_on_selection"] is False
    assert first["navigation"]["node_dragging"] is False
    assert first["navigation"]["frontier_strategy"] == "FULL_PRECOMPUTED_WORLD_VIEWPORT_CLIPPING"


def test_fixture_evidence_and_canonical_direction_are_complete() -> None:
    fixture = build_navigation_fixture()
    source = fixture["document"]["text"]
    for edge in fixture["edges"]:
        assert edge["relationship_label"] == edge["relationship_type"].replace("_", " ")
        assert edge["direction"]
        assert edge["meaning"]
        assert edge["provenance_status"] == "EXPERIMENTAL_FIXTURE_EVIDENCE"
        for evidence in edge["evidence"]:
            assert source[evidence["start_char"]:evidence["end_char"]] == evidence["quote"]


def test_camera_transform_and_drag_pan_math_preserve_world_coordinates() -> None:
    camera = CameraState(450, 250, 1)
    point = (1050, 650)
    screen = world_to_screen(camera, point)
    restored = screen_to_world(camera, (screen.x, screen.y))

    assert screen == type(screen)(600, 400)
    assert restored == type(restored)(1050, 650)
    assert drag_pan(camera, 100, -80) == CameraState(350, 330, 1)
    assert drag_pan(CameraState(**INITIAL_CAMERA), 100, 100) == CameraState(0, 0, 1)


def test_frontier_focus_targets_move_and_interior_focus_does_not() -> None:
    fixture = build_navigation_fixture()
    nodes = {item["entity_id"]: item for item in fixture["nodes"]}
    adjacency = fixture["navigation"]["adjacency"]
    camera = CameraState(**INITIAL_CAMERA)

    assert fixture["navigation"]["initial_visible_node_ids"] == [
        "customer-request", "order-validation", "inventory-reservation",
        "api-gateway", "authentication-service", "identity-store",
    ]
    assert fixture["navigation"]["initial_frontier_node_ids"] == [
        "order-validation", "inventory-reservation"
    ]
    assert fixture["navigation"]["initial_frontier_focus_targets"]["inventory-reservation"] == {
        "x": 450.0, "y": 250.0, "scale": 1.0
    }
    auth = nodes["authentication-service"]["world"]
    auth_neighbors = [nodes[item]["world"] for item in adjacency["authentication-service"]]
    assert focus_camera_target(
        camera, (auth["x"], auth["y"]),
        ((item["x"], item["y"]) for item in auth_neighbors),
    ) == camera


def test_frontier_sequence_reveals_adjacent_topology_without_world_relayout() -> None:
    fixture = build_navigation_fixture()
    nodes = {item["entity_id"]: item for item in fixture["nodes"]}
    original_positions = {key: dict(value["world"]) for key, value in nodes.items()}
    adjacency = fixture["navigation"]["adjacency"]
    camera = CameraState(**INITIAL_CAMERA)
    expected_new = [
        {"inventory-service", "payment-authorization", "payment-service"},
        {"shipment-request"},
        {"notification-dispatch", "notification-service", "observability-collector"},
    ]
    for node_id, expected in zip(
        ("inventory-reservation", "payment-authorization", "shipment-request"), expected_new, strict=True
    ):
        before = {
            key for key, value in nodes.items()
            if point_visible(camera, (value["world"]["x"], value["world"]["y"]), margin=84)
        }
        node = nodes[node_id]["world"]
        neighbors = [nodes[item]["world"] for item in adjacency[node_id]]
        camera = focus_camera_target(
            camera, (node["x"], node["y"]),
            ((item["x"], item["y"]) for item in neighbors),
        )
        after = {
            key for key, value in nodes.items()
            if point_visible(camera, (value["world"]["x"], value["world"]["y"]), margin=84)
        }
        assert after - before == expected
    assert {key: value["world"] for key, value in nodes.items()} == original_positions


def test_world_routes_and_relative_spatial_order_are_camera_independent() -> None:
    fixture = build_navigation_fixture()
    positions = {item["entity_id"]: item["world"] for item in fixture["nodes"]}
    order = sorted(positions, key=lambda key: (positions[key]["x"], positions[key]["y"], key))
    camera = CameraState(850, 250, 1)
    transformed = {key: world_to_screen(camera, (value["x"], value["y"])) for key, value in positions.items()}

    assert order == sorted(transformed, key=lambda key: (transformed[key].x, transformed[key].y, key))
    assert fixture["world"]["routes"] == build_navigation_fixture()["world"]["routes"]
    assert len(fixture["navigation"]["initial_visible_edge_keys"]) == 5


def test_evaluation_preserves_visual_baselines_and_regenerates_byte_for_byte(tmp_path: Path) -> None:
    baseline_doc = default_baseline_document()
    baseline_assets = default_baseline_assets_directory()
    spec006 = default_spec006_directory()
    before = (_hash_file(baseline_doc), hashes(baseline_assets), hashes(spec006))
    left, right = tmp_path / "left", tmp_path / "right"

    first = prepare_continuous_navigation_evaluation(output_dir=left)
    second = prepare_continuous_navigation_evaluation(output_dir=right)

    assert first == second
    assert first["machine_integrity_verdict"] == "PASS"
    assert first["human_review_status"] == "PENDING_OWNER_REVIEW"
    assert first["live_provider_calls"] == 0
    assert hashes(left) == hashes(right)
    assert (_hash_file(baseline_doc), hashes(baseline_assets), hashes(spec006)) == before
    diagnostics = json.loads((left / "navigation-diagnostics.json").read_text())
    assert diagnostics["world"]["node_overlap_count"] == 0
    assert diagnostics["camera"]["targets_deterministic"] is True
    assert diagnostics["camera"]["interior_node_no_motion"] is True
    assert all(diagnostics["integrity"].values())


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_viewer_preserves_graph_grammar_and_implements_camera_navigation(tmp_path: Path) -> None:
    prepare_continuous_navigation_evaluation(output_dir=tmp_path)
    html = (tmp_path / "index.html").read_text()
    css = (tmp_path / "navigation.css").read_text()
    javascript = (tmp_path / "navigation.js").read_text()

    assert 'id="graph-viewport"' in html
    assert 'id="detail"' in html
    assert 'id="history-back"' in html
    assert ".node rect { fill:white; stroke:#819087; stroke-width:1.5; }" in css
    assert "marker-end:url(#arrow)" in css
    assert ".edge-hit { stroke:transparent; stroke-width:18" in css
    assert "cursor:grab" in css and "cursor:grabbing" in css
    assert "pointerdown" in javascript and "pointermove" in javascript
    assert 'group.addEventListener("pointerdown",event=>event.stopPropagation())' in javascript
    assert "requestAnimationFrame" in javascript
    assert 'matchMedia("(prefers-reduced-motion: reduce)")' in javascript
    assert "if(state.animating)return" in javascript
    assert "state.animating=false; clearPreview()" in javascript
    assert "historyBack" in javascript and "historyForward" in javascript
    assert "layout_recomputed" not in javascript
    assert "semantic zoom" not in javascript.lower()
