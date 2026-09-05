from __future__ import annotations

import hashlib
import json
from pathlib import Path

from knowledge_compiler.continuous_navigation import CameraState
from knowledge_compiler.interface_restoration import zoom_camera
from knowledge_compiler.navigation_learning_evaluation import (
    default_baseline001_assets,
    default_baseline001_document,
    default_baseline002_document,
    default_ops002_directory,
    default_spec006_directory,
    prepare_navigation_learning_evaluation,
)
from knowledge_compiler.navigation_learning_workspace import (
    WORKSPACE_INITIAL_CAMERA,
    build_workspace_fixture,
    canonical_workspace_bytes,
    change_camera,
    context_path,
    initial_workspace_state,
    switch_learning_representation,
    synchronize_focus,
)


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def test_workspace_composes_only_existing_learning_semantics_with_explicit_provenance() -> None:
    first = build_workspace_fixture(default_spec006_directory())
    second = build_workspace_fixture(default_spec006_directory())

    assert canonical_workspace_bytes(first) == canonical_workspace_bytes(second)
    assert first["fixture_status"] == "COMPOSED_EXISTING_DETERMINISTIC_SPEC_006_REPRESENTATIONS_NOT_SINGLE_EXTRACTED_WORLD"
    assert first["provenance_note"] == "No cross-domain semantic relationships were added; domain regions are presentation-only context."
    assert len(first["domains"]) == 4
    assert len(first["navigation"]["nodes"]) == 21
    assert len(first["navigation"]["edges"]) == 18
    assert all(domain["composition_status"].startswith("UNCHANGED_SPEC_006") for domain in first["domains"])


def test_navigation_and_learning_share_exact_stable_entity_and_relationship_ids() -> None:
    fixture = build_workspace_fixture(default_spec006_directory())
    navigation_entities = {item["entity_id"] for item in fixture["navigation"]["nodes"]}
    learning_entities = {
        node["entity_id"] for domain in fixture["domains"]
        for representation in domain["learning_model"]["representations"]
        for node in representation["nodes"]
    }
    navigation_relationships = {
        relationship_id for edge in fixture["navigation"]["edges"]
        for relationship_id in edge["relationship_ids"]
    }
    learning_relationships = {
        relationship_id for domain in fixture["domains"]
        for representation in domain["learning_model"]["representations"]
        for edge in representation["edges"] for relationship_id in edge["relationship_ids"]
    }

    assert navigation_entities == learning_entities
    assert navigation_relationships == learning_relationships
    assert len(navigation_entities) == 21
    assert len(navigation_relationships) == 20


def test_bidirectional_concept_sync_selects_structure_appropriate_learning_context() -> None:
    fixture = build_workspace_fixture(default_spec006_directory())
    initial = initial_workspace_state(fixture)

    economics = synchronize_focus(
        fixture, initial, origin="navigation", kind="entity", stable_id="market-price"
    )
    same_domain = synchronize_focus(
        fixture, initial, origin="learning", kind="entity", stable_id="order-component"
    )
    feedback = synchronize_focus(
        fixture, initial, origin="navigation", kind="entity", stable_id="electric-field"
    )

    assert (economics.domain_id, economics.representation_index) == ("economics", 0)
    assert economics.focused_entity_id == "market-price"
    assert economics.camera != initial.camera
    assert (same_domain.domain_id, same_domain.representation_index) == ("software_architecture", 0)
    assert same_domain.camera == initial.camera
    assert (feedback.domain_id, feedback.representation_index) == ("electromagnetism", 0)
    assert context_path(fixture, feedback) == ["Electromagnetism", "Feedback candidate", "electric-field"]


def test_relationship_sync_uses_relationship_ids_and_preserves_camera() -> None:
    fixture = build_workspace_fixture(default_spec006_directory())
    initial = initial_workspace_state(fixture)

    dependency = synchronize_focus(
        fixture, initial, origin="navigation", kind="relationship", stable_id="rel-6"
    )
    causal = synchronize_focus(
        fixture, initial, origin="learning", kind="relationship",
        stable_id="rel-shortage-upward-pressure",
    )

    assert (dependency.domain_id, dependency.representation_index) == ("software_architecture", 1)
    assert dependency.focused_relationship_id == "rel-6"
    assert dependency.camera == initial.camera
    assert (causal.domain_id, causal.representation_index) == ("economics", 0)
    assert causal.camera == initial.camera


def test_camera_and_learning_focus_are_independent_and_overview_is_stable() -> None:
    fixture = build_workspace_fixture(default_spec006_directory())
    initial = initial_workspace_state(fixture)
    camera = zoom_camera(
        CameraState(300, 220, 1), screen_anchor=(600, 400), target_scale=1.4,
        bounds=fixture["navigation"]["world"]["bounds"],
        viewport=fixture["navigation"]["camera"]["viewport"],
    )

    moved = change_camera(initial, camera)
    switched = switch_learning_representation(moved, 1)

    assert moved.focused_entity_id == initial.focused_entity_id
    assert moved.domain_id == initial.domain_id
    assert moved.representation_index == initial.representation_index
    assert switched.camera == moved.camera
    assert WORKSPACE_INITIAL_CAMERA == {"x": 0.0, "y": 0.0, "scale": 1.0}


def test_viewer_contains_synchronized_surfaces_and_accessible_focus_invariants(tmp_path: Path) -> None:
    prepare_navigation_learning_evaluation(output_dir=tmp_path)
    html = (tmp_path / "index.html").read_text()
    css = (tmp_path / "workspace.css").read_text()
    javascript = (tmp_path / "workspace.js").read_text()

    assert 'id="navigation-pane"' in html and 'id="learning-pane"' in html
    assert 'id="context-path"' in html and 'id="learning-detail"' in html
    assert 'id="representation-presets"' in html
    assert ".nav-node:focus,.learn-node:focus { outline:none; }" in css
    assert ".nav-node:focus-visible rect,.learn-node:focus-visible rect" in css
    assert ".nav-edge-hit:focus,.learn-edge-hit:focus { outline:none; }" in css
    assert ".nav-edge-hit:focus-visible,.learn-edge-hit:focus-visible" in css
    assert "button:focus-visible" in css
    assert 'viewport.addEventListener("wheel"' in javascript
    assert "state.camera.scale*Math.exp" in javascript
    assert "contextForEntity(entityId)" in javascript
    assert "contextForRelationship(relationshipId)" in javascript
    assert "edge.relationship_ids.includes(id)" in javascript
    assert "learningEffectiveFocus()" in javascript
    assert "focusExistsInRepresentation" in javascript
    assert "cameraSnapshot()" in javascript
    assert "state.representationIndex=index" in javascript
    assert "label.toLowerCase" not in javascript
    assert "semantic zoom" not in javascript.lower()


def test_evaluation_is_deterministic_and_preserves_both_baselines(tmp_path: Path) -> None:
    frozen_files = (default_baseline001_document(), default_baseline002_document())
    frozen_dirs = (
        default_baseline001_assets(), default_spec006_directory(), default_ops002_directory()
    )
    before = (
        tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in frozen_files),
        tuple(_hashes(path) for path in frozen_dirs),
    )
    left, right = tmp_path / "left", tmp_path / "right"

    first = prepare_navigation_learning_evaluation(output_dir=left)
    second = prepare_navigation_learning_evaluation(output_dir=right)

    assert first == second
    assert first["machine_integrity_verdict"] == "PASS"
    assert first["human_review_status"] == "PENDING_OWNER_REVIEW"
    assert first["replacement_baseline_created"] is False
    assert first["live_provider_calls"] == 0
    assert _hashes(left) == _hashes(right)
    assert before == (
        tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in frozen_files),
        tuple(_hashes(path) for path in frozen_dirs),
    )
    diagnostics = json.loads((left / "synchronization-diagnostics.json").read_text())
    assert diagnostics["navigation_fixture"] == {
        "concept_count": 21,
        "domain_count": 4,
        "relationship_edge_count": 18,
        "relationship_id_count": 20,
    }
    assert diagnostics["learning"]["representation_count"] == 7
    assert diagnostics["synchronization"]["unnecessary_recenter_count"] == 0
    assert diagnostics["state_separation"]["pure_pan_zoom_learning_state_before"] == diagnostics["state_separation"]["pure_pan_zoom_learning_state_after"]
    assert all(diagnostics["integrity"].values())
