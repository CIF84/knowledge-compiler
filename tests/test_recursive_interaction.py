import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.models import ValidationError
from knowledge_compiler.recursive_interaction import (
    InteractionState,
    SemanticObject,
    bidirectional_parity_matrix,
    transition,
)
from knowledge_compiler.recursive_interaction_evaluation import (
    FROZEN_SPEC026_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    VIEWER_FILES,
    default_spec026_directory,
    finalize_recursive_interaction_evaluation,
    prepare_recursive_interaction_evaluation,
    synthetic_recursive_fixture,
)
from knowledge_compiler.semantic_depth_review_evaluation import protected_baseline_hashes


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _packet() -> dict:
    return _json(default_spec026_directory() / "depth-map.json")


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "test fixture",
        "verified_at": "2026-09-05",
        "checks": {
            "ordinary_parent_navigation_intact": True,
            "parent_concept_hover_and_click_bidirectional": True,
            "parent_relationship_hover_and_click_bidirectional": True,
            "spec024_spatial_expansion_intact": True,
            "spec026_connection_legibility_intact": True,
            "depth1_map_concept_hover_to_right_preview": True,
            "depth1_map_concept_click_to_right_selection": True,
            "depth1_right_concept_hover_to_map_preview": True,
            "depth1_right_concept_click_to_map_selection": True,
            "depth1_map_relationship_hover_and_click_bidirectional": True,
            "depth1_right_relationship_hover_and_click_bidirectional": True,
            "depth1_explanation_bidirectional": True,
            "depth2_shared_contract_fixture_passes": True,
            "evidence_synchronization_intact": True,
            "clear_selection_parity": True,
            "switching_leaves_no_stale_focus": True,
            "parent_depth_switching_intact": True,
            "pan_zoom_and_collapse_intact": True,
            "no_blue_selection_artifact": True,
        },
        "console": {"errors": [], "warnings": [], "result": "PASS"},
    }


def test_transition_semantics_do_not_depend_on_location() -> None:
    snapshots = []
    for location in ("parent", "depth-1", "depth-2"):
        item = SemanticObject("same-id", "concept", location)
        current = transition(InteractionState(), "preview", item)
        current = transition(current, "clear_preview")
        current = transition(current, "select", item)
        snapshots.append((current.selected.identity, current.selected.kind, current.preview))
    assert snapshots == [("same-id", "concept", None)] * 3


def test_transition_fails_closed_when_object_is_required() -> None:
    with pytest.raises(ValidationError, match="preview requires"):
        transition(InteractionState(), "preview")
    with pytest.raises(ValidationError, match="selection requires"):
        transition(InteractionState(), "select")


def test_bidirectional_parity_matrix_covers_parent_and_recursive_depth() -> None:
    matrix = bidirectional_parity_matrix()
    assert matrix["status"] == "PASS"
    assert matrix["depth_specific_branch_count"] == 0
    assert matrix["tested_locations"] == ["parent", "depth-1", "depth-2"]
    assert len(matrix["rows"]) == 11
    exception = next(row for row in matrix["rows"] if row["interaction"] == "explanation_focus_to_map")
    assert exception["parent"] == "PRESERVED_NOT_APPLICABLE"
    assert exception["depth_1"] == exception["depth_2"] == "PASS"


def test_synthetic_depth_two_fixture_reuses_semantics_and_dispatch() -> None:
    fixture = synthetic_recursive_fixture(_packet())
    assert fixture["fixture_only"] is True
    assert fixture["new_product_semantics"] == []
    assert fixture["parent_expansion_id"] == "depth-double-slit-v1"
    assert {item["kind"] for item in fixture["sample_semantic_objects"]} == {
        "concept",
        "canonical",
        "explanation",
    }
    assert all(
        item["shared_dispatch"] == "recursiveDispatch"
        and item["locations"] == ["parent", "depth-1", "depth-2"]
        for item in fixture["sample_semantic_objects"]
    )


def test_spec027_composes_spec026_without_rewriting_runtime(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_recursive_interaction_evaluation(output_dir=output)
    control = default_spec026_directory()
    for name in VIEWER_FILES:
        if name == "index.html":
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    candidate_index = (output / "index.html").read_text(encoding="utf-8")
    assert "recursive-interaction.css" in candidate_index
    assert "recursive-interaction.js" in candidate_index
    adapter = (output / "recursive-interaction.js").read_text(encoding="utf-8")
    assert "function recursiveTransition(action,item=null)" in adapter
    assert "function recursiveDispatch(action,item=null)" in adapter
    assert 'location==="depth-1"' not in adapter
    assert 'location==="depth-2"' not in adapter


def test_spec027_machine_gate_preserves_semantics_baselines_and_history(tmp_path: Path) -> None:
    baselines_before = protected_baseline_hashes()
    output = tmp_path / "review"
    report = prepare_recursive_interaction_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert protected_baseline_hashes() == baselines_before
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["representation_algorithm_changes"] == []
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["spec026_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC026_DIRECTORY_SHA256
    )
    assert report["spec026_identity_before"] == report["spec026_identity_after"]
    assert (output / "depth-map.json").read_bytes() == (
        default_spec026_directory() / "depth-map.json"
    ).read_bytes()


def test_spec027_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_recursive_interaction_evaluation(output_dir=first)
    prepare_recursive_interaction_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec027_rejects_spec026_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec026"
    shutil.copytree(default_spec026_directory(), control)
    with (control / "semantic-interaction.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-026 historical artifact identity mismatch"):
        prepare_recursive_interaction_evaluation(
            output_dir=tmp_path / "rejected", spec026_dir=control
        )


def test_spec027_refuses_output_inside_frozen_spec026() -> None:
    output = default_spec026_directory() / "forbidden-spec027-output"
    assert not output.exists()
    with pytest.raises(ValidationError, match="must be isolated"):
        prepare_recursive_interaction_evaluation(output_dir=output)
    assert not output.exists()


def test_spec027_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_recursive_interaction_evaluation(output_dir=output)
    invalid = copy.deepcopy(_browser_pass())
    invalid["checks"].pop("depth1_right_concept_hover_to_map_preview")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_recursive_interaction_evaluation(output, invalid)
    report = finalize_recursive_interaction_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_spec027_cli_prepares_browser_pending_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "review"
    assert main(["prepare-recursive-interaction", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec027_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-027-recursive-bidirectional-interaction-grammar-20260905"
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
