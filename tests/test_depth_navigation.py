import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.baseline004 import (
    BASELINE004_EXECUTABLE_HASHES,
    baseline004_directory,
)
from knowledge_compiler.cli import main
from knowledge_compiler.depth_navigation import (
    DEPTH_EXPANSION_ID,
    DepthMapState,
    build_depth_map_packet,
    close_expansion,
    open_expansion,
    select_depth_item,
    validate_expansion_registry,
)
from knowledge_compiler.depth_navigation_evaluation import (
    FROZEN_SPEC023_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    apply_spec024_depth_navigation,
    default_spec023_directory,
    finalize_depth_navigation_evaluation,
    nested_expansion_regression,
    prepare_depth_navigation_evaluation,
    remove_spec024_depth_navigation,
)
from knowledge_compiler.models import ValidationError
from knowledge_compiler.semantic_depth_review_evaluation import (
    FROZEN_SPEC023_TREATMENT_HASHES,
    default_spec021_directory,
    protected_baseline_hashes,
    remove_fix023_depth_entry,
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "test fixture",
        "viewport": "1280x720",
        "verified_at": "2026-09-05",
        "checks": {
            "ordinary_navigation_intact": True,
            "contextual_explore_deeper": True,
            "left_map_expands": True,
            "origin_path_visible": True,
            "deep_concept_selection_syncs_right": True,
            "canonical_relationship_evidence_syncs_right": True,
            "noncanonical_explanation_labeled_and_evidence_reveals": True,
            "parent_world_remains_navigable": True,
            "pan_zoom_with_expansion": True,
            "collapse_restores_parent_state": True,
            "no_blue_selection_artifact": True,
        },
        "console": {"errors": [], "warnings": [], "result": "PASS"},
    }


def test_depth_packet_translates_frozen_projection_without_semantic_rewrite() -> None:
    projection = _json(default_spec021_directory() / "projection.json")
    packet = build_depth_map_packet(projection)
    expansion = packet["expansions"][0]

    assert packet["root_expansion_id"] == DEPTH_EXPANSION_ID
    assert len(expansion["concepts"]) == len(projection["concepts"]) == 7
    assert [item["id"] for item in expansion["canonical_items"]] == [
        item["id"] for item in projection["canonical_items"]
    ]
    assert [item["id"] for item in expansion["explanatory_items"]] == [
        item["id"] for item in projection["explanatory_items"]
    ]
    assert expansion["origin"]["world"] != expansion["entrance"]
    assert expansion["semantic_connection_kind"] == (
        "SPATIAL_DEPTH_ORIGIN_NOT_CANONICAL_EDGE"
    )


def test_recursive_state_supports_nested_spatial_expansions() -> None:
    registry = {
        "a": {"id": "a", "parent_expansion_id": None},
        "b": {"id": "b", "parent_expansion_id": "a"},
        "c": {"id": "c", "parent_expansion_id": "b"},
    }
    state = open_expansion(DepthMapState(), registry, "a")
    state = open_expansion(state, registry, "b")
    state = open_expansion(state, registry, "c")
    state = select_depth_item(state, "explanation", "fixture-explanation")
    assert state.open_path == ("a", "b", "c")
    assert state.selected_id == "fixture-explanation"
    assert close_expansion(state, "b") == DepthMapState(open_path=("a",))
    assert nested_expansion_regression()["status"] == "PASS"


def test_recursive_state_fails_closed_on_invalid_registry_or_order() -> None:
    with pytest.raises(ValidationError, match="parent is not registered"):
        validate_expansion_registry({"child": {"id": "child", "parent_expansion_id": "missing"}})
    with pytest.raises(ValidationError, match="cycle"):
        validate_expansion_registry(
            {
                "a": {"id": "a", "parent_expansion_id": "b"},
                "b": {"id": "b", "parent_expansion_id": "a"},
            }
        )
    registry = {
        "a": {"id": "a", "parent_expansion_id": None},
        "b": {"id": "b", "parent_expansion_id": "a"},
    }
    with pytest.raises(ValidationError, match="parent is not open"):
        open_expansion(DepthMapState(), registry, "b")


def test_spec024_reuses_baseline004_with_only_additive_map_seams(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_depth_navigation_evaluation(output_dir=output)
    baseline = baseline004_directory()

    for name in BASELINE004_EXECUTABLE_HASHES:
        if name in {"index.html", "learner-grammar.js"}:
            continue
        assert (output / name).read_bytes() == (baseline / name).read_bytes()
    candidate = (output / "learner-grammar.js").read_text(encoding="utf-8")
    fixed = remove_spec024_depth_navigation(candidate)
    assert remove_fix023_depth_entry(fixed) == (
        baseline / "learner-grammar.js"
    ).read_text(encoding="utf-8")
    assert "__SPEC024_DEPTH__.expand" in candidate
    assert "__SPEC021_PROJECTION__.enter()" not in candidate
    assert "depth-expansion.js" in (output / "index.html").read_text(encoding="utf-8")


def test_spec024_machine_gate_preserves_semantics_and_history(tmp_path: Path) -> None:
    before = protected_baseline_hashes()
    output = tmp_path / "review"
    report = prepare_depth_navigation_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")

    assert protected_baseline_hashes() == before
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["representation_algorithm_changes"] == []
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["spec023_historical_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC023_DIRECTORY_SHA256
    )
    assert report["spec023_historical_identity_before"] == report[
        "spec023_historical_identity_after"
    ]
    assert {
        name: hashlib.sha256((output / name).read_bytes()).hexdigest()
        for name in FROZEN_SPEC023_TREATMENT_HASHES
    } == FROZEN_SPEC023_TREATMENT_HASHES


def test_spec024_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_depth_navigation_evaluation(output_dir=first)
    prepare_depth_navigation_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec024_rejects_frozen_input_substitution(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    shutil.copytree(baseline004_directory(), baseline)
    with (baseline / "workspace.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="BASELINE-004 executable identity mismatch"):
        prepare_depth_navigation_evaluation(
            output_dir=tmp_path / "rejected-baseline", baseline_dir=baseline
        )

    historical = tmp_path / "spec023"
    shutil.copytree(default_spec023_directory(), historical)
    with (historical / "report.json").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="historical artifact identity mismatch"):
        prepare_depth_navigation_evaluation(
            output_dir=tmp_path / "rejected-history", spec023_dir=historical
        )


def test_spec024_refuses_output_inside_frozen_inputs() -> None:
    output = baseline004_directory() / "forbidden-spec024-output"
    assert not output.exists()
    with pytest.raises(ValidationError, match="must be isolated"):
        prepare_depth_navigation_evaluation(output_dir=output)
    assert not output.exists()


def test_spec024_browser_finalize_requires_complete_clean_gate(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_depth_navigation_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("origin_path_visible")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_depth_navigation_evaluation(output, invalid)

    report = finalize_depth_navigation_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_spec024_cli_prepares_browser_pending_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "review"
    assert main(["prepare-depth-navigation", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec024_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-024-depth-as-continuous-map-expansion-20260905"
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
