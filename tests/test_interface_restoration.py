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
    screen_to_world,
)
from knowledge_compiler.interface_restoration import (
    CAMERA_MAX_SCALE,
    CAMERA_MIN_SCALE,
    InteractionSelection,
    attention_state,
    state_counts,
    wheel_zoom_camera,
    zoom_camera,
)
from knowledge_compiler.interface_restoration_evaluation import (
    default_baseline_assets_directory,
    default_baseline_document,
    default_spec006_directory,
    default_spec018_directory,
    prepare_interface_restoration_evaluation,
)


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def _world_bytes() -> bytes:
    fixture = build_navigation_fixture()
    return canonical_navigation_bytes({
        "bounds": fixture["world"]["bounds"],
        "nodes": [{"entity_id": item["entity_id"], **item["world"]} for item in fixture["nodes"]],
        "routes": fixture["world"]["routes"],
    })


def test_pointer_centered_zoom_preserves_anchor_and_enforces_scale_bounds() -> None:
    start = CameraState(500, 240, 1)
    anchor = (600, 400)
    world_before = screen_to_world(start, anchor)

    zoomed = zoom_camera(start, screen_anchor=anchor, target_scale=1.75)

    assert zoomed == CameraState(757.142857, 411.428571, 1.75)
    assert screen_to_world(zoomed, anchor) == world_before
    assert wheel_zoom_camera(start, screen_anchor=anchor, delta_y=100000).scale == CAMERA_MIN_SCALE
    assert wheel_zoom_camera(start, screen_anchor=anchor, delta_y=-100000).scale == CAMERA_MAX_SCALE


def test_pan_and_zoom_compose_without_mutating_world_geometry() -> None:
    world_before = _world_bytes()
    zoomed = zoom_camera(CameraState(500, 240, 1), screen_anchor=(600, 400), target_scale=1.75)
    panned = drag_pan(zoomed, -140, 70)

    assert panned == CameraState(837.142857, 371.428571, 1.75)
    assert _world_bytes() == world_before
    assert CameraState(**INITIAL_CAMERA) == CameraState(0, 0, 1)


def test_selected_node_suppression_keeps_neighbors_and_relationships_strong() -> None:
    fixture = build_navigation_fixture()
    selection = InteractionSelection("node", "payment-authorization")

    focused = attention_state(fixture, persistent=selection)

    assert state_counts(focused) == {
        "nodes": {"NEIGHBOR": 4, "SELECTED": 1, "SUBDUED": 19},
        "edges": {"CONNECTED": 4, "SUBDUED": 24},
    }
    assert focused["nodes"]["inventory-reservation"] == "NEIGHBOR"
    assert focused["nodes"]["shipment-request"] == "NEIGHBOR"
    assert focused["edges"]["navigation-edge-04"] == "CONNECTED"


def test_selected_relationship_suppression_keeps_connector_and_endpoints_strong() -> None:
    fixture = build_navigation_fixture()

    focused = attention_state(
        fixture,
        persistent=InteractionSelection("edge", "navigation-edge-14"),
    )

    assert state_counts(focused) == {
        "nodes": {"ENDPOINT": 2, "SUBDUED": 22},
        "edges": {"SELECTED": 1, "SUBDUED": 27},
    }
    assert focused["nodes"]["payment-authorization"] == "ENDPOINT"
    assert focused["nodes"]["payment-service"] == "ENDPOINT"


def test_hover_is_temporary_and_clear_restores_normal_weight() -> None:
    fixture = build_navigation_fixture()
    persistent = InteractionSelection("node", "payment-authorization")
    before = attention_state(fixture, persistent=persistent)
    during = attention_state(
        fixture,
        persistent=persistent,
        preview=InteractionSelection("edge", "navigation-edge-17"),
    )
    after = attention_state(fixture, persistent=persistent)
    clear = attention_state(fixture)

    assert during != before
    assert during["edges"]["navigation-edge-17"] == "PREVIEW"
    assert after == before
    assert all(value == "NORMAL" for group in clear.values() for value in group.values())


def test_viewer_restores_focus_zoom_suppression_and_hit_target_invariants(tmp_path: Path) -> None:
    prepare_interface_restoration_evaluation(output_dir=tmp_path)
    html = (tmp_path / "index.html").read_text()
    css = (tmp_path / "restoration.css").read_text()
    javascript = (tmp_path / "restoration.js").read_text()

    assert 'id="zoom-in"' in html and 'id="zoom-out"' in html
    assert ".node:focus { outline:none; }" in css
    assert ".node:focus-visible rect" in css
    assert ".edge-hit:focus { outline:none; }" in css
    assert ".edge-hit:focus-visible" in css
    assert "button:focus { outline:none; }" in css
    assert "button:focus-visible" in css
    assert ".node.is-unrelated { opacity:.18; }" in css
    assert ".edge-line.is-unrelated,.edge-label.is-unrelated { opacity:.12; }" in css
    assert 'viewport.addEventListener("wheel"' in javascript
    assert "event.preventDefault()" in javascript
    assert "pointerLogicalPoint(event)" in javascript
    assert "Math.exp(-event.deltaY*sensitivity)" in javascript
    assert "start.scale+(target.scale-start.scale)*eased" in javascript
    assert "state.selectedNodeId" in javascript and "state.selectedEdgeKey" in javascript
    assert 'hit=svgElement("path",{d:path' in javascript
    assert 'line=svgElement("path",{d:path' in javascript
    assert "tabindex:\"0\"" in javascript
    assert 'event.key==="Enter"||event.key===" "' in javascript
    assert "semantic zoom" not in javascript.lower()


def test_evaluation_is_deterministic_preserves_frozen_inputs_and_covers_layout_grammar(tmp_path: Path) -> None:
    baseline_doc = default_baseline_document()
    frozen_dirs = (
        default_baseline_assets_directory(), default_spec006_directory(), default_spec018_directory()
    )
    before = (hashlib.sha256(baseline_doc.read_bytes()).hexdigest(), *(_hashes(path) for path in frozen_dirs))
    left, right = tmp_path / "left", tmp_path / "right"

    first = prepare_interface_restoration_evaluation(output_dir=left)
    second = prepare_interface_restoration_evaluation(output_dir=right)

    assert first == second
    assert first["machine_integrity_verdict"] == "PASS"
    assert first["human_review_status"] == "PENDING_OWNER_REVIEW"
    assert first["candidate_baseline"] == "BASELINE-002_NOT_CREATED"
    assert first["live_provider_calls"] == 0
    assert _hashes(left) == _hashes(right)
    assert (hashlib.sha256(baseline_doc.read_bytes()).hexdigest(), *(_hashes(path) for path in frozen_dirs)) == before
    diagnostics = json.loads((left / "restoration-diagnostics.json").read_text())
    assert diagnostics["world_coordinate_hash_before"] == diagnostics["world_coordinate_hash_after"]
    assert diagnostics["camera"]["pointer_zoom_test"]["world_anchor_before"] == diagnostics["camera"]["pointer_zoom_test"]["world_anchor_after"]
    assert diagnostics["attention"]["hover_restoration_exact"] is True
    compatibility = diagnostics["representation_layout_compatibility"]
    assert compatibility["all_required_observed"] is True
    assert compatibility["all_camera_transform_compatible"] is True
    assert {item["layout_strategy"] for item in compatibility["representations"]} == {
        "layered_hierarchy", "layered_causal", "chronological_axis",
        "layered_dependency", "explicit_feedback_loop",
    }
    assert all(diagnostics["integrity"].values())
