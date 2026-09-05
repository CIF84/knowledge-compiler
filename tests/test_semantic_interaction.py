import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.models import ValidationError
from knowledge_compiler.semantic_depth_review_evaluation import protected_baseline_hashes
from knowledge_compiler.semantic_interaction import (
    classify_expansion_connections,
    connection_classification_audit,
)
from knowledge_compiler.semantic_interaction_evaluation import (
    FROZEN_SPEC025_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    VIEWER_FILES,
    apply_semantic_connection_grammar,
    default_spec025_directory,
    finalize_semantic_interaction_evaluation,
    prepare_semantic_interaction_evaluation,
    recursive_classification_regression,
    remove_semantic_connection_grammar,
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _packet() -> dict:
    return _json(default_spec025_directory() / "depth-map.json")


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "test fixture",
        "verified_at": "2026-09-05",
        "checks": {
            "ordinary_navigation_intact": True,
            "spec024_spatial_expansion_intact": True,
            "spec025_selection_synchronization_intact": True,
            "canonical_predicates_and_direction_readable": True,
            "canonical_relationships_selectable_and_synchronized": True,
            "explanatory_connections_explicitly_noncanonical_and_nondirectional": True,
            "explanatory_connections_selectable_and_synchronized": True,
            "no_unexplained_relationship_like_connectors": True,
            "concept_focus_preserves_connected_semantics": True,
            "switching_has_no_stale_focus": True,
            "parent_deeper_switching_intact": True,
            "map_learning_focus_mirror": True,
            "recursive_classification_contract": True,
            "pan_zoom_and_collapse_intact": True,
            "no_blue_selection_artifact": True,
        },
        "console": {"errors": [], "warnings": [], "result": "PASS"},
    }


def test_every_visible_connection_has_an_honest_semantic_class() -> None:
    audit = connection_classification_audit(_packet()["expansions"][0])
    assert audit["status"] == "PASS"
    assert audit["counts"] == {
        "all_visible_connections": 16,
        "canonical_relationships": 2,
        "explanatory_attachments": 13,
        "depth_ancestry_paths": 1,
        "unclassified": 0,
        "fabricated_pairwise_relationships": 0,
    }
    canonical = [item for item in audit["connections"] if item["canonical"]]
    explanatory = [
        item
        for item in audit["connections"]
        if item["semantic_class"] == "SOURCE_BACKED_EXPLANATORY_ATTACHMENT"
    ]
    assert all(item["directional"] and item["label"] != "" for item in canonical)
    assert all(
        not item["directional"]
        and not item["canonical"]
        and item["label"] == "EXPLANATORY"
        and item["selectable_kind"] == "explanation"
        for item in explanatory
    )


def test_connection_classification_fails_closed_on_untrusted_attachment() -> None:
    expansion = copy.deepcopy(_packet()["expansions"][0])
    expansion["explanatory_attachments"][0]["participant_entity_id"] = "not-grounded"
    with pytest.raises(ValidationError, match="participant is not grounded"):
        classify_expansion_connections(expansion)


def test_synthetic_second_expansion_uses_identical_classification_contract() -> None:
    regression = recursive_classification_regression(_packet())
    assert regression == {
        "status": "PASS",
        "same_contract": True,
        "parent_expansion_id": "depth-double-slit-v1",
        "nested_expansion_id": "synthetic-second-expansion",
        "connection_count_per_expansion": 16,
        "depth_specific_branch_count": 0,
    }


def test_spec026_composes_spec025_with_only_connection_hooks(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_semantic_interaction_evaluation(output_dir=output)
    control = default_spec025_directory()
    for name in VIEWER_FILES:
        if name in {"index.html", "depth-expansion.js", "depth-interaction.js"}:
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    control_map = (control / "depth-expansion.js").read_text(encoding="utf-8")
    control_learning = (control / "depth-interaction.js").read_text(encoding="utf-8")
    candidate_map = (output / "depth-expansion.js").read_text(encoding="utf-8")
    candidate_learning = (output / "depth-interaction.js").read_text(encoding="utf-8")
    assert remove_semantic_connection_grammar(candidate_map, candidate_learning) == (
        control_map,
        control_learning,
    )
    assert apply_semantic_connection_grammar(control_map, control_learning) == (
        candidate_map,
        candidate_learning,
    )
    assert "semantic-interaction.js" in (output / "index.html").read_text(encoding="utf-8")


def test_spec026_machine_gate_preserves_semantics_baselines_and_history(tmp_path: Path) -> None:
    baselines_before = protected_baseline_hashes()
    output = tmp_path / "review"
    report = prepare_semantic_interaction_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert protected_baseline_hashes() == baselines_before
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["representation_algorithm_changes"] == []
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["spec025_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC025_DIRECTORY_SHA256
    )
    assert report["spec025_identity_before"] == report["spec025_identity_after"]
    assert (output / "depth-map.json").read_bytes() == (
        default_spec025_directory() / "depth-map.json"
    ).read_bytes()


def test_spec026_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_semantic_interaction_evaluation(output_dir=first)
    prepare_semantic_interaction_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec026_rejects_spec025_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec025"
    shutil.copytree(default_spec025_directory(), control)
    with (control / "depth-interaction.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-025 historical artifact identity mismatch"):
        prepare_semantic_interaction_evaluation(
            output_dir=tmp_path / "rejected", spec025_dir=control
        )


def test_spec026_refuses_output_inside_frozen_spec025() -> None:
    output = default_spec025_directory() / "forbidden-spec026-output"
    assert not output.exists()
    with pytest.raises(ValidationError, match="must be isolated"):
        prepare_semantic_interaction_evaluation(output_dir=output)
    assert not output.exists()


def test_spec026_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_semantic_interaction_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("no_unexplained_relationship_like_connectors")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_semantic_interaction_evaluation(output, invalid)
    report = finalize_semantic_interaction_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_spec026_cli_prepares_browser_pending_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "review"
    assert main(["prepare-semantic-interaction", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec026_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-026-semantic-interaction-invariance-20260905"
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
