import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.models import ValidationError
from knowledge_compiler.relationship_multiplicity import (
    multiplicity_groups,
    order_independence_fixture,
    recursive_multiplicity_fixture,
    relationship_index,
    resolve_relationship,
)
from knowledge_compiler.relationship_multiplicity_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC030_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    SPEC030_RUNTIME_FILES,
    default_spec030_directory,
    finalize_relationship_multiplicity_evaluation,
    prepare_relationship_multiplicity_evaluation,
)
from knowledge_compiler.semantic_depth_review_evaluation import protected_baseline_hashes


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _fixture() -> dict:
    return _json(default_spec030_directory() / "workspace-fixture.json")


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


def test_reciprocal_electromagnetism_edges_keep_independent_identity() -> None:
    groups = multiplicity_groups(_fixture())
    group = next(
        item
        for item in groups
        if item["domain_id"] == "electromagnetism" and item["kind"] == "RECIPROCAL"
    )
    assert group["canonical_relationship_count"] == 2
    assert set(group["canonical_relationship_identities"]) == {
        "changing-electric-field-induces-magnetic-field",
        "changing-magnetic-field-induces-electric-field",
    }
    assert group["synthetic_relationship_identity"] is None


def test_identity_resolution_preserves_direction_and_own_evidence() -> None:
    index = relationship_index(_fixture())
    forward = resolve_relationship(index, "changing-electric-field-induces-magnetic-field")
    reverse = resolve_relationship(index, "changing-magnetic-field-induces-electric-field")
    assert (forward["source_entity_id"], forward["target_entity_id"]) == (
        "electric-field",
        "magnetic-field",
    )
    assert (reverse["source_entity_id"], reverse["target_entity_id"]) == (
        "magnetic-field",
        "electric-field",
    )
    assert all(item["relationship_id"] == forward["identity"] for item in forward["evidence"])
    assert all(item["relationship_id"] == reverse["identity"] for item in reverse["evidence"])


def test_existing_economics_same_direction_multiplicity_is_included() -> None:
    economics = [
        group for group in multiplicity_groups(_fixture()) if group["domain_id"] == "economics"
    ]
    assert len(economics) == 2
    assert all(group["kind"] == "SAME_DIRECTION_MULTI_ASSERTION" for group in economics)
    assert all(group["canonical_relationship_count"] == 2 for group in economics)


def test_resolution_is_independent_of_array_and_visual_order() -> None:
    result = order_independence_fixture(_fixture())
    assert result["status"] == "PASS"
    assert result["resolution_key"] == "canonical relationship identity"
    assert "DOM order" in result["forbidden_resolution_keys"]


def test_recursive_multiplicity_uses_same_identity_grammar_through_depth_10() -> None:
    result = recursive_multiplicity_fixture()
    assert result["status"] == "PASS"
    assert result["tested_depths"] == [0, 1, 2, 5, 10]
    assert result["depth_is_resolver_input"] is False
    assert result["new_product_semantics"] == []


def test_spec031_composes_spec030_without_mutating_runtime(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_relationship_multiplicity_evaluation(output_dir=output)
    control = default_spec030_directory()
    for name in SPEC030_RUNTIME_FILES:
        if name == "index.html":
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    index = (output / "index.html").read_text(encoding="utf-8")
    assert index.index('src="learning-surface.js"') < index.index(
        'src="relationship-multiplicity.js"'
    )


def test_machine_gate_preserves_frozen_history_and_has_no_live_calls(tmp_path: Path) -> None:
    before = protected_baseline_hashes()
    output = tmp_path / "candidate"
    report = prepare_relationship_multiplicity_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == protected_baseline_hashes()
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["spec030_identity_before"]["aggregate_sha256"] == FROZEN_SPEC030_DIRECTORY_SHA256
    assert report["spec030_identity_before"] == report["spec030_identity_after"]
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())


def test_spec031_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_relationship_multiplicity_evaluation(output_dir=first)
    prepare_relationship_multiplicity_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec031_rejects_spec030_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec030"
    shutil.copytree(default_spec030_directory(), control)
    with (control / "learning-surface.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-030 historical artifact identity mismatch"):
        prepare_relationship_multiplicity_evaluation(
            output_dir=tmp_path / "rejected", spec030_dir=control
        )


def test_spec031_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_relationship_multiplicity_evaluation(output_dir=output)
    invalid = copy.deepcopy(_browser_pass())
    invalid["checks"].pop("reverse_selection_commits_reverse_identity")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_relationship_multiplicity_evaluation(output, invalid)
    report = finalize_relationship_multiplicity_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == "PENDING_OWNER_REVIEW"


def test_spec031_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-relationship-multiplicity", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == OWNER_REVIEW_INSTRUCTION


def test_committed_spec031_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-031-reciprocal-and-multi-edge-relationship-semantics-20260906"
    )
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert report["deterministic_regeneration_result"] == {
        "compared_file_count": 37,
        "result": "PASS_BYTE_IDENTICAL",
        "scope": "independently generated pre-browser candidate artifacts",
    }
    assert report["offline_test_result"] == {
        "focused": "12 passed",
        "full": "400 passed",
        "result": "PASS",
    }
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
