import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.depth_interaction import resolve_learning_focus
from knowledge_compiler.depth_interaction_evaluation import (
    FROZEN_SPEC024_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    VIEWER_FILES,
    apply_spec025_synchronization,
    default_spec024_directory,
    finalize_depth_interaction_evaluation,
    prepare_depth_interaction_evaluation,
    recursive_synchronization_regression,
    remove_spec025_synchronization,
)
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


def _packet() -> dict:
    return _json(default_spec024_directory() / "depth-map.json")


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "test fixture",
        "viewport": "1280x720",
        "verified_at": "2026-09-05",
        "checks": {
            "ordinary_navigation_intact": True,
            "spec024_spatial_expansion_intact": True,
            "deep_concept_updates_full_learning_surface": True,
            "deep_canonical_relationship_updates_surface_and_evidence": True,
            "deep_noncanonical_explanation_updates_surface_and_evidence": True,
            "switching_deep_items_has_no_stale_focus": True,
            "parent_selection_restores_ordinary_interaction": True,
            "map_and_learning_focus_mirror": True,
            "clear_selection_is_coherent_at_depth": True,
            "pan_zoom_and_collapse_intact": True,
            "no_blue_selection_artifact": True,
        },
        "console": {"errors": [], "warnings": [], "result": "PASS"},
    }


def test_focus_resolution_uses_semantic_item_type_not_depth_label() -> None:
    packet = _packet()
    expansion_id = packet["root_expansion_id"]
    concept = resolve_learning_focus(packet, expansion_id, "concept", "waveparticle-duality")
    relationship = resolve_learning_focus(
        packet, expansion_id, "canonical", "relationship-7d1b3317e1e4c682"
    )
    explanation = resolve_learning_focus(
        packet, expansion_id, "explanation", "explanation-ae10fa8748fdac1f"
    )

    assert concept.item_type == "CONCEPT"
    assert concept.representation_role == "FOCUS_CONTEXT"
    assert relationship.item_type == "CANONICAL_RELATIONSHIP"
    assert relationship.semantic_tier == "TRUSTED_CANONICAL"
    assert relationship.evidence_count == 1
    assert explanation.item_type == "SOURCE_BACKED_EXPLANATION"
    assert explanation.semantic_tier == "SOURCE_BACKED_NON_CANONICAL"
    assert explanation.evidence_count == 1


def test_focus_resolution_fails_closed_on_unknown_identity_or_type() -> None:
    packet = _packet()
    expansion_id = packet["root_expansion_id"]
    with pytest.raises(ValidationError, match="not uniquely present"):
        resolve_learning_focus(packet, expansion_id, "concept", "missing")
    with pytest.raises(ValidationError, match="unknown selectable"):
        resolve_learning_focus(packet, expansion_id, "unsupported", "missing")  # type: ignore[arg-type]


def test_synthetic_second_expansion_uses_identical_focus_contract() -> None:
    regression = recursive_synchronization_regression(_packet())
    assert regression["status"] == "PASS"
    assert regression["depth_specific_branch_count"] == 0
    assert len(regression["cases"]) == 3
    assert all(case["same_contract"] for case in regression["cases"])


def test_spec025_composes_spec024_with_only_sync_hooks_and_adapter(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_depth_interaction_evaluation(output_dir=output)
    control = default_spec024_directory()

    for name in VIEWER_FILES:
        if name in {"index.html", "depth-expansion.js"}:
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    control_script = (control / "depth-expansion.js").read_text(encoding="utf-8")
    candidate_script = (output / "depth-expansion.js").read_text(encoding="utf-8")
    assert remove_spec025_synchronization(candidate_script) == control_script
    assert apply_spec025_synchronization(control_script) == candidate_script
    assert "depth-interaction.js" in (output / "index.html").read_text(encoding="utf-8")
    assert "Selected deeper concept" not in candidate_script


def test_spec025_machine_gate_preserves_semantics_baselines_and_history(tmp_path: Path) -> None:
    baselines_before = protected_baseline_hashes()
    output = tmp_path / "review"
    report = prepare_depth_interaction_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")

    assert protected_baseline_hashes() == baselines_before
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["representation_algorithm_changes"] == []
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["spec024_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC024_DIRECTORY_SHA256
    )
    assert report["spec024_identity_before"] == report["spec024_identity_after"]
    assert (output / "projection.json").read_bytes() == (
        default_spec024_directory() / "projection.json"
    ).read_bytes()


def test_spec025_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_depth_interaction_evaluation(output_dir=first)
    prepare_depth_interaction_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec025_rejects_spec024_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec024"
    shutil.copytree(default_spec024_directory(), control)
    with (control / "depth-expansion.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-024 historical artifact identity mismatch"):
        prepare_depth_interaction_evaluation(
            output_dir=tmp_path / "rejected", spec024_dir=control
        )


def test_spec025_refuses_output_inside_frozen_spec024() -> None:
    output = default_spec024_directory() / "forbidden-spec025-output"
    assert not output.exists()
    with pytest.raises(ValidationError, match="must be isolated"):
        prepare_depth_interaction_evaluation(output_dir=output)
    assert not output.exists()


def test_spec025_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_depth_interaction_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("map_and_learning_focus_mirror")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_depth_interaction_evaluation(output, invalid)

    report = finalize_depth_interaction_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_spec025_cli_prepares_browser_pending_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "review"
    assert main(["prepare-depth-interaction", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec025_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-025-depth-invariant-interaction-grammar-20260905"
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
