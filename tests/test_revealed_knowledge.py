import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.learning_path import trusted_continuations, trusted_object_catalog
from knowledge_compiler.models import ValidationError
from knowledge_compiler.revealed_knowledge import (
    RevealedKnowledgeState,
    canonical_projection,
    large_revealed_tree_fixture,
)
from knowledge_compiler.revealed_knowledge_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC032_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    SPEC031_RUNTIME_FILES,
    default_spec031_directory,
    default_spec032_directory,
    finalize_revealed_knowledge_evaluation,
    prepare_revealed_knowledge_evaluation,
)
from knowledge_compiler.semantic_depth_review_evaluation import protected_baseline_hashes


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs() -> tuple[dict, dict]:
    control = default_spec031_directory()
    return _json(control / "workspace-fixture.json"), _json(control / "depth-map.json")


def _projection() -> list[dict]:
    fixture, depth = _inputs()
    return canonical_projection(trusted_object_catalog(fixture, depth), depth)


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


def test_projection_assigns_one_stable_parent_to_each_canonical_object() -> None:
    projection = _projection()
    by_key = {item["object_key"]: item for item in projection}
    assert len(projection) == 61
    assert len(by_key) == len(projection)
    assert by_key["orientation:domain:electromagnetism"]["parent_object_key"] is None
    assert by_key["concept:electric-field"]["parent_object_key"] == (
        "orientation:domain:electromagnetism"
    )
    assert by_key["concept:waveparticle-duality"]["parent_object_key"] == (
        "concept:double-slit-experiment"
    )
    assert by_key["concept:waveparticle-duality"]["projection_basis"].startswith(
        "ADMITTED_DEPTH_GROUP:"
    )


def test_revisit_does_not_duplicate_canonical_node() -> None:
    state = RevealedKnowledgeState(
        _projection(), "orientation:domain:electromagnetism"
    )
    state.select("concept:double-slit-experiment")
    before = state.snapshot()["revealed_object_count"]
    for _ in range(8):
        state.select("concept:double-slit-experiment")
    snapshot = state.snapshot()
    assert snapshot["revealed_object_count"] == before
    assert snapshot["revealed_object_keys"].count("concept:double-slit-experiment") == 1
    node = next(
        item
        for item in snapshot["nodes"]
        if item["object_key"] == "concept:double-slit-experiment"
    )
    assert node["telemetry"]["visit_count"] == 9


def test_irrational_visit_order_does_not_become_projection_topology() -> None:
    state = RevealedKnowledgeState(
        _projection(), "orientation:domain:electromagnetism"
    )
    for key in (
        "orientation:domain:economics",
        "concept:market-price",
        "orientation:domain:history",
        "concept:printing",
        "orientation:domain:economics",
    ):
        state.select(key)
    nodes = {item["object_key"]: item for item in state.snapshot()["nodes"]}
    assert nodes["concept:market-price"]["parent_object_key"] == (
        "orientation:domain:economics"
    )
    assert nodes["concept:printing"]["parent_object_key"] == "orientation:domain:history"
    assert state.snapshot()["history_structurally_defines_navigation"] is False


def test_collapse_hides_without_forgetting_and_selection_reopens_chain() -> None:
    state = RevealedKnowledgeState(
        _projection(), "orientation:domain:electromagnetism"
    )
    state.select("concept:double-slit-experiment")
    state.select("concept:waveparticle-duality")
    before = state.snapshot()["revealed_object_keys"]
    state.set_expanded("concept:double-slit-experiment", False)
    assert "concept:waveparticle-duality" not in state.visible_object_keys()
    assert state.snapshot()["revealed_object_keys"] == before
    state.select("concept:waveparticle-duality")
    assert "concept:waveparticle-duality" in state.visible_object_keys()


def test_unrelated_collapse_state_survives_focus_change() -> None:
    state = RevealedKnowledgeState(
        _projection(), "orientation:domain:electromagnetism"
    )
    state.select("concept:double-slit-experiment")
    state.select("concept:waveparticle-duality")
    state.select("orientation:domain:economics")
    state.select("concept:market-price")
    state.set_expanded("orientation:domain:electromagnetism", False)
    state.select("concept:market-price")
    electromagnetism = next(
        item
        for item in state.snapshot()["nodes"]
        if item["object_key"] == "orientation:domain:electromagnetism"
    )
    assert electromagnetism["expanded"] is False


def test_reciprocal_relationships_remain_distinct_canonical_nodes() -> None:
    state = RevealedKnowledgeState(
        _projection(), "orientation:domain:electromagnetism"
    )
    keys = [
        "canonical:changing-electric-field-induces-magnetic-field",
        "canonical:changing-magnetic-field-induces-electric-field",
    ]
    state.reveal_many(keys, revealed_from="concept:electric-field")
    assert set(keys) <= set(state.snapshot()["revealed_object_keys"])
    assert len([item for item in state.snapshot()["nodes"] if item["object_key"] in keys]) == 2


def test_large_fixture_exercises_60_objects_and_material_collapse() -> None:
    fixture = large_revealed_tree_fixture()
    assert fixture["status"] == "PASS"
    assert fixture["object_count"] == 60
    assert fixture["root_count"] == 4
    assert fixture["max_depth"] == 7
    assert len(fixture["expanded_snapshot"]["visible_object_keys"]) == 60
    assert len(fixture["collapsed_snapshot"]["visible_object_keys"]) < 50


def test_unknown_object_and_projection_cycle_fail_closed() -> None:
    projection = _projection()
    state = RevealedKnowledgeState(
        projection, "orientation:domain:electromagnetism"
    )
    with pytest.raises(ValidationError, match="unknown canonical navigation object"):
        state.select("concept:not-trusted")
    broken = copy.deepcopy(projection)
    root = next(item for item in broken if item["object_key"] == "orientation:domain:economics")
    root["parent_object_key"] = "concept:market-price"
    with pytest.raises(ValidationError, match="cycle"):
        RevealedKnowledgeState(broken, "orientation:domain:economics")


def test_spec033_composes_spec031_without_spec032_runtime(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_revealed_knowledge_evaluation(output_dir=output)
    control = default_spec031_directory()
    for name in SPEC031_RUNTIME_FILES:
        if name == "index.html":
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    index = (output / "index.html").read_text(encoding="utf-8")
    assert "learning-path.js" not in index
    assert index.index("relationship.src='relationship-multiplicity.js'") < index.index(
        "revealed.src='revealed-knowledge.js'"
    )


def test_machine_gate_preserves_baselines_and_prior_evidence(tmp_path: Path) -> None:
    before = protected_baseline_hashes()
    spec032_before = _hashes(default_spec032_directory())
    output = tmp_path / "candidate"
    report = prepare_revealed_knowledge_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == protected_baseline_hashes()
    assert spec032_before == _hashes(default_spec032_directory())
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["spec032_evidence_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC032_DIRECTORY_SHA256
    )
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())


def test_spec033_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_revealed_knowledge_evaluation(output_dir=first)
    prepare_revealed_knowledge_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec033_rejects_spec032_historical_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec032"
    shutil.copytree(default_spec032_directory(), control)
    with (control / "learning-path.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-032 historical evidence identity mismatch"):
        prepare_revealed_knowledge_evaluation(
            output_dir=tmp_path / "rejected", spec032_dir=control
        )


def test_spec033_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_revealed_knowledge_evaluation(output_dir=output)
    invalid = copy.deepcopy(_browser_pass())
    invalid["checks"].pop("repeated_depth_and_region_switching_remains_interactive")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_revealed_knowledge_evaluation(output, invalid)
    report = finalize_revealed_knowledge_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_spec033_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-revealed-knowledge", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec033_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-033-canonical-revealed-knowledge-tree-20260907"
    )
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert report["deterministic_regeneration_result"] == {
        "compared_file_count": 36,
        "result": "PASS_BYTE_IDENTICAL",
        "scope": "independently generated non-lifecycle candidate artifacts",
    }
    assert report["offline_test_result"] == {
        "focused": "15 passed",
        "full": "429 passed",
        "result": "PASS",
    }
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
