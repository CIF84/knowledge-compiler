import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.learning_path import (
    TraversalHistory,
    exploration_suggestions,
    ten_step_branching_fixture,
    trusted_continuations,
    trusted_object_catalog,
)
from knowledge_compiler.learning_path_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC031_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    SPEC031_RUNTIME_FILES,
    default_spec031_directory,
    finalize_learning_path_evaluation,
    prepare_learning_path_evaluation,
)
from knowledge_compiler.models import ValidationError
from knowledge_compiler.semantic_depth_review_evaluation import protected_baseline_hashes


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs() -> tuple[dict, dict]:
    control = default_spec031_directory()
    return _json(control / "workspace-fixture.json"), _json(control / "depth-map.json")


def _catalog_and_links() -> tuple[list[dict], list[dict]]:
    fixture, depth = _inputs()
    return trusted_object_catalog(fixture, depth), trusted_continuations(fixture, depth)


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


def test_trusted_catalog_has_stable_unique_committed_objects() -> None:
    catalog, _ = _catalog_and_links()
    assert len(catalog) == 61
    assert len({item["object_key"] for item in catalog}) == len(catalog)
    assert all(item["trusted_source"] for item in catalog)
    assert {item["kind"] for item in catalog} == {
        "orientation",
        "concept",
        "canonical",
        "explanation",
    }


def test_fixed_electromagnetism_journey_resolves_only_trusted_suggestions() -> None:
    catalog, links = _catalog_and_links()
    sequence = [
        "orientation:domain:electromagnetism",
        "concept:double-slit-experiment",
        "concept:interference-pattern",
        "concept:photon",
        "concept:waveparticle-duality",
        "concept:principle-of-complementarity",
    ]
    visited: set[str] = set()
    for current, target in zip(sequence, sequence[1:]):
        suggestions = exploration_suggestions(
            current,
            catalog=catalog,
            continuations=links,
            visited_object_keys=visited,
        )
        assert target in {item["target_object_key"] for item in suggestions}
        visited.add(current)


def test_traversal_edges_mean_travelled_and_never_copy_predicates() -> None:
    catalog, _ = _catalog_and_links()
    by_key = {item["object_key"]: item for item in catalog}
    history = TraversalHistory(by_key["orientation:domain:history"])
    history.travel(by_key["concept:printing"])
    history.travel(by_key["concept:printed-books"])
    snapshot = history.snapshot()
    assert all(edge["semantics"] == "TRAVELLED" for edge in snapshot["edges"])
    assert all(edge["canonical_predicate"] is None for edge in snapshot["edges"])


def test_backtracking_creates_branch_and_visited_node_reuses_it() -> None:
    catalog, _ = _catalog_and_links()
    by_key = {item["object_key"]: item for item in catalog}
    history = TraversalHistory(by_key["orientation:domain:electromagnetism"])
    double_slit = history.travel(by_key["concept:double-slit-experiment"])
    interference = history.travel(by_key["concept:interference-pattern"])
    photon = history.travel(by_key["concept:photon"])
    history.activate(interference)
    electron = history.travel(by_key["concept:electron"])
    history.activate(interference)
    assert history.travel(by_key["concept:photon"]) == photon
    snapshot = history.snapshot()
    assert double_slit != interference
    assert electron != photon
    assert len(
        [node for node in snapshot["nodes"] if node["parent_path_node_id"] == interference]
    ) == 2


def test_ten_step_path_and_branch_use_one_depth_independent_grammar() -> None:
    result = ten_step_branching_fixture()
    assert result["status"] == "PASS"
    assert result["tested_traversal_steps"] == 10
    assert result["depth_is_path_rule_input"] is False
    assert result["new_product_semantics"] == []


def test_cross_domain_trusted_continuations_exist() -> None:
    catalog, links = _catalog_and_links()
    pairs = {
        "concept:double-slit-experiment": "concept:interference-pattern",
        "concept:printing": "concept:printed-books",
        "concept:payment-component": "concept:database",
    }
    for current, target in pairs.items():
        suggestions = exploration_suggestions(
            current, catalog=catalog, continuations=links
        )
        assert target in {item["target_object_key"] for item in suggestions}


def test_reciprocal_relationship_identities_remain_separate_suggestions() -> None:
    catalog, links = _catalog_and_links()
    suggestions = exploration_suggestions(
        "concept:electric-field", catalog=catalog, continuations=links
    )
    identities = {
        item["target_semantic_identity"]
        for item in suggestions
        if item["target_kind"] == "canonical"
    }
    assert {
        "changing-electric-field-induces-magnetic-field",
        "changing-magnetic-field-induces-electric-field",
    } <= identities


def test_spec032_composes_spec031_without_mutating_runtime(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_learning_path_evaluation(output_dir=output)
    control = default_spec031_directory()
    for name in SPEC031_RUNTIME_FILES:
        if name == "index.html":
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    index = (output / "index.html").read_text(encoding="utf-8")
    assert index.index("relationship.src='relationship-multiplicity.js'") < index.index(
        "path.src='learning-path.js'"
    )


def test_machine_gate_preserves_history_and_has_no_live_calls(tmp_path: Path) -> None:
    before = protected_baseline_hashes()
    output = tmp_path / "candidate"
    report = prepare_learning_path_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == protected_baseline_hashes()
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["spec031_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC031_DIRECTORY_SHA256
    )
    assert report["spec031_identity_before"] == report["spec031_identity_after"]
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())


def test_spec032_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_learning_path_evaluation(output_dir=first)
    prepare_learning_path_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec032_rejects_spec031_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec031"
    shutil.copytree(default_spec031_directory(), control)
    with (control / "relationship-multiplicity.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-031 historical artifact identity mismatch"):
        prepare_learning_path_evaluation(
            output_dir=tmp_path / "rejected", spec031_dir=control
        )


def test_spec032_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_learning_path_evaluation(output_dir=output)
    invalid = copy.deepcopy(_browser_pass())
    invalid["checks"].pop("alternate_continuation_preserves_visible_branch")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_learning_path_evaluation(output, invalid)
    report = finalize_learning_path_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_spec032_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-learning-path", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec032_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-032-learning-path-navigation-separation-20260907"
    )
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert report["deterministic_regeneration_result"] == {
        "compared_file_count": 40,
        "result": "PASS_BYTE_IDENTICAL",
        "scope": "independently generated pre-browser candidate artifacts",
    }
    assert report["offline_test_result"] == {
        "focused": "14 passed",
        "full": "414 passed",
        "result": "PASS",
    }
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
