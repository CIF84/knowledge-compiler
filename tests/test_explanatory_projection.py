import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.continuous_navigation import CameraState
from knowledge_compiler.explanatory_projection import (
    EXPLANATORY_ROLE,
    FOCUS_ENTITY_ID,
    FROZEN_SPEC020_HASHES,
    build_explanatory_projection,
    canonical_bytes,
    load_frozen_spec020_inputs,
    projection_diagnostics,
)
from knowledge_compiler.explanatory_projection_evaluation import (
    default_spec020_directory,
    prepare_explanatory_projection_evaluation,
)
from knowledge_compiler.models import ValidationError
from knowledge_compiler.semantic_depth import (
    INITIAL_CAMERA,
    DepthWorkspaceState,
    depth_camera_invariant,
    switch_semantic_depth,
)


def _inputs():
    return load_frozen_spec020_inputs(default_spec020_directory())


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def test_frozen_spec020_packet_identity_and_fail_closed_hash_validation(tmp_path):
    inputs = _inputs()
    assert inputs.file_hashes == FROZEN_SPEC020_HASHES
    copied = tmp_path / "packet"
    shutil.copytree(default_spec020_directory(), copied)
    with (copied / "focus-selection.json").open("a", encoding="utf-8") as stream:
        stream.write(" ")
    with pytest.raises(ValidationError, match="identity mismatch"):
        load_frozen_spec020_inputs(copied)


def test_projection_preserves_focus_and_two_semantic_tiers():
    projection = build_explanatory_projection(_inputs())
    assert projection.focus_entity_id == FOCUS_ENTITY_ID
    assert {item.entity_id for item in projection.concepts} == _inputs().symbols.ids
    assert len(projection.canonical_items) == 2
    assert len(projection.explanatory_items) == 6
    assert {item.semantic_tier for item in projection.canonical_items} == {"TRUSTED_CANONICAL"}
    assert {item.presentation_role for item in projection.explanatory_items} == {EXPLANATORY_ROLE}
    assert {item.semantic_tier for item in projection.explanatory_items} == {"SOURCE_BACKED_NON_CANONICAL"}


def test_supported_canonical_relationships_preserved_and_rejected_not_promoted():
    projection = build_explanatory_projection(_inputs())
    assert {item.assertion_id for item in projection.canonical_items} == {
        "assertion-3fadf1ab890d9bde", "assertion-7d1b3317e1e4c682"
    }
    assert "assertion-ae10fa8748fdac1f" not in {
        item.assertion_id for item in projection.canonical_items
    }
    assert "assertion-ae10fa8748fdac1f" in {
        item.assertion_id for item in projection.explanatory_items
    }


def test_explanatory_items_preserve_exact_assertions_evidence_and_n_participants():
    inputs = _inputs()
    projection = build_explanatory_projection(inputs)
    assertions = {item.id: item for item in inputs.assertions.assertions}
    attachments = projection.layout["explanatory_attachments"]
    for item in projection.explanatory_items:
        source = assertions[item.assertion_id]
        assert item.statement == source.statement
        assert item.evidence == source.evidence
        assert item.participant_entity_ids == source.participant_entity_ids
        attached = {
            link["participant_entity_id"] for link in attachments
            if link["explanatory_item_id"] == item.id
        }
        assert attached == set(source.participant_entity_ids)
        assert all(link["kind"] == "NON_DIRECTIONAL_PRESENTATION_ATTACHMENT" for link in attachments)


def test_projection_machine_metrics_and_text_budget():
    diagnostics = projection_diagnostics(build_explanatory_projection(_inputs()))
    assert diagnostics["initial_visible_prose_word_count"] == 35
    assert diagnostics["initial_visible_prose_word_budget"] == 40
    assert diagnostics["text_budget_pass"] is True
    assert diagnostics["pairwise_edge_fabrication_count"] == 0
    assert diagnostics["rejected_item_promotion_count"] == 0
    assert diagnostics["layout"]["concept_node_overlap_count"] == 0
    assert diagnostics["layout"]["explanatory_anchor_overlap_count"] == 0
    assert diagnostics["layout"]["concept_anchor_overlap_count"] == 0


def test_projection_layout_is_deterministic():
    inputs = _inputs()
    first = canonical_bytes(build_explanatory_projection(inputs).to_dict())
    second = canonical_bytes(build_explanatory_projection(inputs).to_dict())
    assert first == second


def test_workspace_evaluation_preserves_control_baselines_and_camera(tmp_path):
    output = tmp_path / "one"
    report = prepare_explanatory_projection_evaluation(output_dir=output)
    control = json.loads((output / "canonical-control.json").read_text())
    manifest = json.loads((output / "input-manifest.json").read_text())
    fixture = json.loads((output / "workspace-fixture.json").read_text())
    diagnostics = json.loads((output / "workspace-diagnostics.json").read_text())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["live_model_calls"] == 0
    assert control["structure_count"] == 1
    assert control["focus_present"] is False
    assert control["admission"] == "FAIL_FOCUS_ABSENT"
    assert manifest["identity_verified"] is True
    assert manifest["baseline_immutable"] is True
    assert fixture["semantic_depth"]["navigation_world_replaced"] is False
    assert diagnostics["parent_navigation"]["stable"] is True
    assert all(diagnostics["semantic_depth"][key] for key in (
        "parent_to_projection_camera_unchanged", "projection_to_parent_camera_unchanged",
        "return_to_parent_preserves_focus",
    ))


def test_parent_projection_state_transition_preserves_camera_and_focus():
    state = DepthWorkspaceState(camera=CameraState(**INITIAL_CAMERA))
    deeper = switch_semantic_depth(state, "CHILD")
    returned = switch_semantic_depth(deeper, "PARENT")
    assert depth_camera_invariant(state, deeper)
    assert depth_camera_invariant(deeper, returned)
    assert returned.focused_entity_id == FOCUS_ENTITY_ID


def test_evaluation_regenerates_byte_for_byte(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    prepare_explanatory_projection_evaluation(output_dir=first)
    prepare_explanatory_projection_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_viewer_uses_distinct_visual_grammar_and_on_demand_evidence(tmp_path):
    output = tmp_path / "viewer"
    prepare_explanatory_projection_evaluation(output_dir=output)
    script = (output / "workspace.js").read_text()
    css = (output / "projection.css").read_text()
    assert "Source-backed explanation · non-canonical" in script
    assert "Show exact source evidence" in script
    assert "projection-attachment" in css and "stroke-dasharray" in css
    assert "projection-canonical" in css and "marker-end" in css
    assert "focus-caption" in css
