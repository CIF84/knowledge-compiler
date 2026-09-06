import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.learning_surface import (
    depth_independence_fixture,
    representation_form,
)
from knowledge_compiler.learning_surface_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC029_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    SPEC029_RUNTIME_FILES,
    default_spec029_directory,
    finalize_learning_surface_evaluation,
    prepare_learning_surface_evaluation,
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


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "test fixture",
        "checks": {name: True for name in BROWSER_CHECKS},
        "console": {"errors": [], "result": "PASS", "warnings": []},
    }


def test_representation_selection_uses_semantic_class_and_predicate() -> None:
    assert representation_form("orientation") == "ORIENTATION_SUMMARY"
    assert representation_form("concept") == "CONCISE_CONCEPT_EXPLANATION"
    assert representation_form("canonical", "CAUSES") == "FOCUSED_CAUSAL_RELATIONSHIP"
    assert representation_form("canonical", "PART_OF") == "FOCUSED_HIERARCHY_RELATIONSHIP"
    assert representation_form("canonical", "ENABLES") == "FOCUSED_SEQUENCE_RELATIONSHIP"
    assert representation_form("canonical", "EXAMPLE_OF") == "FOCUSED_RELATIONSHIP"
    assert representation_form("explanation") == "SOURCE_BACKED_EXPLANATION"


def test_representation_architecture_is_depth_independent() -> None:
    fixture = depth_independence_fixture()
    assert fixture["status"] == "PASS"
    assert fixture["tested_depths"] == list(range(11))
    assert fixture["depth_is_resolver_input"] is False
    assert fixture["new_product_semantics"] == []


def test_spec030_composes_spec029_without_mutating_runtime(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_learning_surface_evaluation(output_dir=output)
    control = default_spec029_directory()
    for name in SPEC029_RUNTIME_FILES:
        if name == "index.html":
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    index = (output / "index.html").read_text(encoding="utf-8")
    assert index.index('src="atomic-context.js"') < index.index('src="learning-surface.js"')
    assert 'href="learning-surface.css"' in index


def test_machine_gate_preserves_frozen_inputs_and_has_no_live_calls(tmp_path: Path) -> None:
    before = protected_baseline_hashes()
    output = tmp_path / "candidate"
    report = prepare_learning_surface_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == protected_baseline_hashes()
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["spec029_identity_before"]["aggregate_sha256"] == FROZEN_SPEC029_DIRECTORY_SHA256
    assert report["spec029_identity_before"] == report["spec029_identity_after"]
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())


def test_fixed_cases_are_truthful_and_not_duplicate_maps(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_learning_surface_evaluation(output_dir=output)
    fixed = _json(output / "learning-representation-fixtures.json")
    assert fixed["status"] == "PASS"
    assert fixed["duplicate_navigation_maps"] == 0
    assert fixed["fabricated_semantic_items"] == 0
    assert set(fixed["payloads"]) == {
        "orientation",
        "depth_orientation",
        "history_concept",
        "history_relationship",
        "software_concept",
        "software_relationship",
        "depth_concept",
        "depth_relationship",
        "depth_explanation",
    }
    assert all(not item["full_navigation_map"] for item in fixed["payloads"].values())
    assert fixed["payloads"]["depth_explanation"]["semantic_tier"] == "SOURCE_BACKED_NON_CANONICAL"


def test_owner_observed_ground_gaps_remain_explicit(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_learning_surface_evaluation(output_dir=output)
    result = _json(output / "ground-level-gap-classification.json")
    assert result["claimed_owner_issue_fixed"] is False
    assert result["parallel_handler_added"] is False
    assert {item["identity"] for item in result["cases"]} == {"rel-8", "printed-controversy"}
    assert all(item["classification"] == "C_FIXTURE_DATA_AMBIGUITY" for item in result["cases"])
    assert all(item["canonical_event_path_present"] for item in result["cases"])


def test_spec030_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_learning_surface_evaluation(output_dir=first)
    prepare_learning_surface_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec030_rejects_spec029_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec029"
    shutil.copytree(default_spec029_directory(), control)
    with (control / "atomic-context.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-029 historical artifact identity mismatch"):
        prepare_learning_surface_evaluation(output_dir=tmp_path / "rejected", spec029_dir=control)


def test_spec030_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_learning_surface_evaluation(output_dir=output)
    invalid = copy.deepcopy(_browser_pass())
    invalid["checks"].pop("map_and_learning_semantic_identity_agree")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_learning_surface_evaluation(output, invalid)
    report = finalize_learning_surface_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == "PENDING_OWNER_REVIEW"


def test_spec030_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-learning-surface", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == OWNER_REVIEW_INSTRUCTION


def test_committed_spec030_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-030-distinct-learning-surface-representation-20260906"
    )
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert report["deterministic_regeneration_result"]["result"] == "PASS_BYTE_IDENTICAL"
    assert report["offline_test_result"] == {
        "focused": "11 passed",
        "full": "388 passed",
        "result": "PASS",
    }
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
