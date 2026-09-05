import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.canonical_interaction import (
    CanonicalInteractionState,
    SemanticKey,
    SemanticOccurrence,
    exercise_depth,
    project_interaction,
    reduce_interaction,
    state_transition_parity_matrix,
    ten_level_recursion_fixture,
)
from knowledge_compiler.canonical_interaction_evaluation import (
    FROZEN_SPEC027_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    SPEC027_RUNTIME_FILES,
    default_spec027_directory,
    finalize_canonical_interaction_evaluation,
    prepare_canonical_interaction_evaluation,
)
from knowledge_compiler.cli import main
from knowledge_compiler.models import ValidationError
from knowledge_compiler.semantic_depth_review_evaluation import protected_baseline_hashes


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _occurrence(
    identity: str = "shared-concept",
    kind: str = "concept",
    depth: int = 0,
    surface: str = "map",
) -> SemanticOccurrence:
    return SemanticOccurrence(
        SemanticKey(identity, kind),
        tuple(f"depth-{index}" for index in range(1, depth + 1)),
        surface,
    )


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "test fixture",
        "checks": {
            "ordinary_parent_navigation_intact": True,
            "continuous_spatial_expansion_intact": True,
            "canonical_noncanonical_legibility_intact": True,
            "single_authoritative_state_marker_passes": True,
            "parent_map_and_right_concept_hover_agree": True,
            "parent_map_and_right_concept_click_agree": True,
            "parent_relationship_origin_parity": True,
            "depth_map_and_right_concept_hover_agree": True,
            "depth_map_and_right_concept_click_agree": True,
            "depth_relationship_origin_parity": True,
            "depth_explanation_origin_parity": True,
            "selected_never_degrades_to_preview": True,
            "duplicate_instance_parity": True,
            "rapid_target_switching_zero_stale_state": True,
            "relationship_to_concept_switch_zero_stale_state": True,
            "clear_selection_zero_stale_state": True,
            "hover_after_clear_intact": True,
            "evidence_synchronization_intact": True,
            "ten_level_fixture_passes": True,
            "pan_zoom_and_collapse_intact": True,
            "no_blue_selection_artifact": True,
        },
        "console": {"errors": [], "result": "PASS", "warnings": []},
    }


def test_reducer_ignores_depth_and_surface_for_semantic_state() -> None:
    results = []
    for depth in (0, 1, 2, 5, 10):
        for surface in ("map", "representation", "explanation"):
            state = reduce_interaction(
                CanonicalInteractionState(), "select", _occurrence(depth=depth, surface=surface)
            )
            results.append((state.selected, state.hovered))
    assert results == [(SemanticKey("shared-concept", "concept"), None)] * 15


def test_hover_is_transient_and_does_not_destroy_selection() -> None:
    selected = reduce_interaction(
        CanonicalInteractionState(), "select", _occurrence("a", depth=10)
    )
    hovered = reduce_interaction(selected, "hover", _occurrence("b", depth=1))
    assert hovered.effective == SemanticKey("b", "concept")
    restored = reduce_interaction(hovered, "hover_exit", _occurrence("b", depth=1))
    assert restored.selected == SemanticKey("a", "concept")
    assert restored.hovered is None


def test_hovering_duplicate_of_selected_object_preserves_selected_mode() -> None:
    selected = reduce_interaction(
        CanonicalInteractionState(), "select", _occurrence("same", depth=0, surface="map")
    )
    duplicate_hover = reduce_interaction(
        selected, "hover", _occurrence("same", depth=10, surface="representation")
    )
    assert duplicate_hover.selected == SemanticKey("same", "concept")
    assert duplicate_hover.hovered is None
    assert duplicate_hover.mode == "SELECTED"


def test_reducer_fails_closed_for_missing_target() -> None:
    with pytest.raises(ValidationError, match="hover requires"):
        reduce_interaction(CanonicalInteractionState(), "hover")
    with pytest.raises(ValidationError, match="selection requires"):
        reduce_interaction(CanonicalInteractionState(), "select")


def test_all_surface_projections_derive_identical_meaning() -> None:
    state = reduce_interaction(
        CanonicalInteractionState(),
        "select",
        _occurrence("relationship-x", "canonical", 5, "representation"),
    )
    projection = project_interaction(state)
    assert projection["map_projected_state"] == projection["representation_projected_state"]
    assert projection["map_projected_state"] == projection["explanation_projected_state"]
    assert projection["active_relationship_identity"] == "relationship-x"
    assert projection["stale_state_count"] == 0


def test_switching_and_clear_leave_no_stale_state() -> None:
    rows = exercise_depth(10)
    by_event = {row["event"]: row for row in rows}
    assert by_event["switch_concept_a_to_b"]["selected_target"] == "fixture-concept-b"
    assert by_event["switch_relationship_to_concept"]["semantic_class"] == "concept"
    assert by_event["clear_selection"]["semantic_identity"] is None
    assert by_event["hover_after_clear"]["selected_target"] is None
    assert all(row["stale_state_count"] == 0 for row in rows)


def test_ten_level_recursion_uses_identical_state_results() -> None:
    fixture = ten_level_recursion_fixture()
    assert fixture["tested_depths"] == list(range(11))
    assert fixture["semantic_state_equality_across_tested_depths"] == "PASS"
    assert fixture["surface_projection_agreement"] == "PASS"
    assert fixture["stale_state_count"] == 0
    assert fixture["new_product_semantics"] == []


def test_required_depth_parity_matrix_passes() -> None:
    matrix = state_transition_parity_matrix()
    assert matrix["status"] == "PASS"
    assert matrix["tested_depths"] == [0, 1, 2, 5, 10]
    assert matrix["depth_specific_semantic_branch_count"] == 0
    assert len(matrix["rows"]) == 14
    assert all(row["semantic_state_equality"] for row in matrix["rows"])
    assert all(row["surface_projection_agreement"] for row in matrix["rows"])
    assert all(row["stale_state_count"] == 0 for row in matrix["rows"])


def test_spec028_composes_spec027_without_mutating_runtime(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_canonical_interaction_evaluation(output_dir=output)
    control = default_spec027_directory()
    for name in SPEC027_RUNTIME_FILES:
        if name == "index.html":
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    index = (output / "index.html").read_text(encoding="utf-8")
    assert '<script src="recursive-interaction.js"></script>' not in index
    assert '<script src="canonical-interaction.js"></script>' in index
    assert (output / "recursive-interaction.js").is_file()


def test_spec028_machine_gate_preserves_semantics_baselines_and_history(tmp_path: Path) -> None:
    baselines_before = protected_baseline_hashes()
    output = tmp_path / "candidate"
    report = prepare_canonical_interaction_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert protected_baseline_hashes() == baselines_before
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["representation_algorithm_changes"] == []
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["historical_identities_before"]["spec027"]["aggregate_sha256"] == (
        FROZEN_SPEC027_DIRECTORY_SHA256
    )
    assert report["historical_identities_before"] == report["historical_identities_after"]


def test_spec028_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_canonical_interaction_evaluation(output_dir=first)
    prepare_canonical_interaction_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec028_rejects_spec027_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec027"
    shutil.copytree(default_spec027_directory(), control)
    with (control / "recursive-interaction.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-027 historical artifact identity mismatch"):
        prepare_canonical_interaction_evaluation(
            output_dir=tmp_path / "rejected", spec027_dir=control
        )


def test_spec028_refuses_output_inside_frozen_spec027() -> None:
    output = default_spec027_directory() / "forbidden-spec028-output"
    assert not output.exists()
    with pytest.raises(ValidationError, match="must be isolated"):
        prepare_canonical_interaction_evaluation(output_dir=output)
    assert not output.exists()


def test_spec028_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_canonical_interaction_evaluation(output_dir=output)
    invalid = copy.deepcopy(_browser_pass())
    invalid["checks"].pop("selected_never_degrades_to_preview")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_canonical_interaction_evaluation(output, invalid)
    report = finalize_canonical_interaction_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == "PENDING_OWNER_REVIEW"


def test_spec028_cli_prepares_browser_pending_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-canonical-interaction", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec028_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-028-single-canonical-interaction-state-20260905"
    )
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
