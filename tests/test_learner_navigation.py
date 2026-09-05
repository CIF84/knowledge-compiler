import hashlib
import json
import shutil

import pytest

from knowledge_compiler.learner_navigation import (
    BASELINE_CONTROL_HASHES,
    DEPTH_ENTITY_ID,
    DEPTH_NEIGHBOR_ID,
    LearnerNavigationState,
    build_learner_fixture,
    choose_concept_representation,
    choose_orientation_representation,
    choose_relationship_representation,
    enter_depth,
    return_from_depth,
    validate_learner_fixture,
    verify_frozen_files,
)
from knowledge_compiler.learner_navigation_evaluation import (
    SEAM_SUFFIX,
    default_baseline003_directory,
    default_spec020_directory,
    default_spec021_directory,
    prepare_learner_navigation_evaluation,
)
from knowledge_compiler.models import ValidationError


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _fixture():
    baseline = _json(default_baseline003_directory() / "workspace-fixture.json")
    parent = _json(default_spec020_directory() / "parent.representation.json")
    return baseline, build_learner_fixture(baseline, parent)


def _hashes(directory):
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def test_exact_executable_baseline003_control_is_verified():
    assert verify_frozen_files(
        default_baseline003_directory(), BASELINE_CONTROL_HASHES, "BASELINE-003"
    ) == BASELINE_CONTROL_HASHES


def test_existing_world_topology_coordinates_regions_and_workspace_are_unchanged():
    baseline, fixture = _fixture()
    original_nodes = {item["entity_id"]: item for item in baseline["navigation"]["nodes"]}
    nodes = {item["entity_id"]: item for item in fixture["navigation"]["nodes"]}
    original_edges = {item["edge_key"]: item for item in baseline["navigation"]["edges"]}
    edges = {item["edge_key"]: item for item in fixture["navigation"]["edges"]}
    assert all(nodes[key] == value for key, value in original_nodes.items())
    assert all(edges[key] == value for key, value in original_edges.items())
    assert [item["world_region"] for item in fixture["domains"]] == [
        item["world_region"] for item in baseline["domains"]
    ]
    assert fixture["navigation"]["camera"] == baseline["navigation"]["camera"]
    assert fixture["navigation"]["world"]["bounds"] == baseline["navigation"]["world"]["bounds"]
    assert fixture["workspace"] == baseline["workspace"]
    assert set(nodes) - set(original_nodes) == {DEPTH_ENTITY_ID, DEPTH_NEIGHBOR_ID}


def test_electromagnetism_region_entry_uses_existing_primary_orientation():
    _, fixture = _fixture()
    domain = next(item for item in fixture["domains"] if item["domain_id"] == "electromagnetism")
    index = choose_orientation_representation(domain)
    assert index == 0
    assert domain["learning_model"]["representations"][index]["id"] == "representation-9058fd6ab1975a17"


def test_light_automatic_representation_has_no_contextual_depth():
    _, fixture = _fixture()
    domain = next(item for item in fixture["domains"] if item["domain_id"] == "electromagnetism")
    index = choose_concept_representation(domain, "light")
    assert index == 1
    assert fixture["learner_navigation"]["admitted_depth_entity_ids"] == [DEPTH_ENTITY_ID]
    state = LearnerNavigationState("electromagnetism", index, "CONCEPT", "light")
    with pytest.raises(ValidationError, match="not admitted"):
        enter_depth(state)


def test_double_slit_uses_frozen_parent_representation_and_contextual_depth():
    _, fixture = _fixture()
    domain = next(item for item in fixture["domains"] if item["domain_id"] == "electromagnetism")
    index = choose_concept_representation(domain, DEPTH_ENTITY_ID)
    assert domain["learning_model"]["representations"][index]["id"] == "representation-1da8ae41cb52f95a"
    state = LearnerNavigationState(
        "electromagnetism", index, "CONCEPT", DEPTH_ENTITY_ID,
        parent_camera=(120.0, 80.0, 1.25),
    )
    deeper = enter_depth(state)
    returned = return_from_depth(deeper)
    assert deeper.depth == "DEEPER"
    assert returned.depth == "PARENT"
    assert deeper.parent_camera == state.parent_camera == returned.parent_camera
    assert returned.selected_id == DEPTH_ENTITY_ID


def test_software_architecture_automatic_selection_preserves_primary_behavior():
    _, fixture = _fixture()
    domain = next(item for item in fixture["domains"] if item["domain_id"] == "software_architecture")
    assert choose_orientation_representation(domain) == 0
    assert choose_concept_representation(domain, "modular-order-processing-service") == 0
    assert choose_relationship_representation(domain, "rel-3") == 0


def test_regression_validation_fails_if_existing_coordinate_changes():
    baseline, fixture = _fixture()
    fixture["navigation"]["nodes"][0]["world"]["x"] += 1
    with pytest.raises(ValidationError, match="node or coordinate"):
        validate_learner_fixture(baseline, fixture)


def test_generated_viewer_reuses_baseline_engine_and_styles(tmp_path):
    output = tmp_path / "viewer"
    report = prepare_learner_navigation_evaluation(output_dir=output)
    baseline = default_baseline003_directory()
    script = (output / "workspace.js").read_bytes()
    baseline_script = (baseline / "workspace.js").read_bytes()
    diagnostics = _json(output / "workspace-diagnostics.json")
    assert script == baseline_script + SEAM_SUFFIX
    assert (output / "workspace.css").read_bytes() == (baseline / "workspace.css").read_bytes()
    assert diagnostics["status"] == "PASS"
    assert diagnostics["existing_navigation_nodes_and_coordinates_unchanged"] is True
    assert diagnostics["pan_zoom_overview_handlers_preserved"] is True
    assert diagnostics["focus_suppression_handler_preserved"] is True
    assert diagnostics["map_learning_synchronization_handlers_preserved"] is True
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert report["live_model_calls"] == 0


def test_generated_viewer_preserves_spec021_semantic_artifacts_byte_for_byte(tmp_path):
    output = tmp_path / "viewer"
    prepare_learner_navigation_evaluation(output_dir=output)
    source = default_spec021_directory()
    for name in ("projection.json", "projection-diagnostics.json", "semantic-tier-audit.json"):
        assert (output / name).read_bytes() == (source / name).read_bytes()


def test_learner_controls_hide_compiler_terms_and_keep_debug_access(tmp_path):
    output = tmp_path / "viewer"
    prepare_learner_navigation_evaluation(output_dir=output)
    css = (output / "grammar.css").read_text()
    script = (output / "learner-grammar.js").read_text()
    assert "body:not(.evaluator-mode) #representation-presets" in css
    assert "body:not(.evaluator-mode) .fixture-label" in css
    assert "body:not(.evaluator-mode) #learning-detail .detail-grid" in css
    assert 'get("debug")==="1"' in script
    assert '"Explore deeper"' in script
    assert '"Return"' in script
    assert "Double-slit depth" not in script
    assert 'state.selectedEntityId!=="double-slit-experiment"' in script


def test_region_boundaries_and_titles_are_keyboard_selectable(tmp_path):
    output = tmp_path / "viewer"
    prepare_learner_navigation_evaluation(output_dir=output)
    script = (output / "learner-grammar.js").read_text()
    assert 'node.setAttribute("role","button")' in script
    assert 'node.setAttribute("tabindex","0")' in script
    assert "learnerEnterRegion" in script
    assert 'event.key==="Enter"||event.key===" "' in script


def test_spec022_regeneration_is_byte_for_byte(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    prepare_learner_navigation_evaluation(output_dir=first)
    prepare_learner_navigation_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_baseline_asset_substitution_fails_closed(tmp_path):
    baseline = tmp_path / "baseline"
    shutil.copytree(default_baseline003_directory(), baseline)
    with (baseline / "workspace.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="identity mismatch"):
        prepare_learner_navigation_evaluation(
            output_dir=tmp_path / "rejected", baseline_dir=baseline
        )
