import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.models import ValidationError
from knowledge_compiler.visual_semantic_grammar_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC036_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    default_spec036_directory,
    finalize_visual_semantic_grammar_evaluation,
    prepare_visual_semantic_grammar_evaluation,
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path, *, exclude_lifecycle: bool = False) -> dict[str, str]:
    excluded = {
        "browser-verification.json",
        "human-review-template.json",
        "machine-gate.json",
        "report.json",
    } if exclude_lifecycle else set()
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name not in excluded
    }


def _browser_pass() -> dict:
    capture_names = (
        "mixed_my_map",
        "double_slit",
        "focused_relationship",
        "light_hierarchy",
        "history_dependency",
        "history_sequence",
        "software_composition",
        "prose_fallback",
    )
    return {
        "status": "PASS",
        "browser": "test fixture",
        "checks": {name: True for name in BROWSER_CHECKS},
        "console": {"errors": [], "warnings": [], "result": "PASS"},
        "deterministic_captures": [
            {"case": name, "result": "PASS"} for name in capture_names
        ],
    }


def test_frozen_spec036_candidate_identity_is_exact() -> None:
    from knowledge_compiler.depth_interaction_evaluation import directory_identity

    assert directory_identity(default_spec036_directory())["aggregate_sha256"] == (
        FROZEN_SPEC036_DIRECTORY_SHA256
    )


def test_candidate_composes_exact_spec036_runtime(tmp_path: Path) -> None:
    before = _hashes(default_spec036_directory())
    output = tmp_path / "candidate"
    report = prepare_visual_semantic_grammar_evaluation(output_dir=output)
    assert before == _hashes(default_spec036_directory())
    assert report["spec036_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC036_DIRECTORY_SHA256
    )
    assert report["spec036_identity_before"] == report["spec036_identity_after"]


def test_machine_gate_preserves_all_prior_runtime_boundaries(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())


def test_visual_layer_has_no_interaction_or_navigation_handlers(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    script = (output / "visual-semantic-grammar.js").read_text()
    assert "addEventListener(" not in script
    assert "__SPEC029_ATOMIC__.dispatch" not in script
    assert "__SPEC033_REVEALED__.select" not in script
    assert "__SPEC033_REVEALED__.reveal" not in script
    assert "__SPEC024_DEPTH__.expand" not in script


def test_my_map_data_and_behavior_runtime_are_byte_identical(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    for name in ("revealed-knowledge.js", "revealed-knowledge-fixture.json"):
        assert (output / name).read_bytes() == (
            default_spec036_directory() / name
        ).read_bytes()


def test_spec036_local_inspection_runtime_is_byte_identical(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    assert (output / "structure-aware-surface.js").read_bytes() == (
        default_spec036_directory() / "structure-aware-surface.js"
    ).read_bytes()


def test_visual_roles_distinguish_territory_semantics_and_actions(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    script = (output / "visual-semantic-grammar.js").read_text()
    assert all(
        token in script
        for token in (
            "territory-region",
            "territory-concept",
            "territory-relationship",
            "semantic-concept",
            "semantic-connector",
            "reading-detail",
            "navigation-action",
        )
    )


def test_tree_objects_and_explore_actions_use_distinct_css(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    styles = (output / "visual-semantic-grammar.css").read_text()
    tree = styles.index(".revealed-node-button")
    semantic = styles.index(".visual-semantic-object")
    action = styles.index(".revealed-suggestion")
    assert len({tree, semantic, action}) == 3
    assert "border:0" in styles[tree : tree + 400]
    assert "border:1px" in styles[action : action + 500]


def test_relationships_are_rendered_as_connectors_not_pills(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    styles = (output / "visual-semantic-grammar.css").read_text()
    connector = styles.index(".visual-semantic-connector")
    fragment = styles[connector : connector + 500]
    assert "border:0!important" in fragment
    assert "border-radius:0!important" in fragment
    assert "background:transparent!important" in fragment


def test_redundant_trusted_relationships_heading_is_demoted_only(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    script = (output / "visual-semantic-grammar.js").read_text()
    assert 'rail.querySelector(":scope > .eyebrow")?.remove()' in script
    assert (output / "representation-plans.json").read_bytes() == (
        default_spec036_directory() / "representation-plans.json"
    ).read_bytes()
    assert "visual-connection-index" in script


def test_fixed_cases_cover_required_distinct_strategies(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    report = prepare_visual_semantic_grammar_evaluation(output_dir=output)
    strategies = set(report["strategies_exercised"])
    assert {
        "CAUSAL_MECHANISM",
        "HIERARCHY_COMPOSITION",
        "FOCUSED_RELATIONSHIP",
        "PROCESS_SEQUENCE",
        "DEPENDENCY_STRUCTURE",
        "CONCISE_PROSE",
    }.issubset(strategies)


def test_history_sequence_uses_committed_grounded_plan(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    report = prepare_visual_semantic_grammar_evaluation(output_dir=output)
    cases = {item["case"]: item for item in report["fixed_evaluation_cases"]}
    sequence = cases["history_authorities_sequence"]
    assert sequence["representation_strategy"] == "PROCESS_SEQUENCE"
    assert sequence["evidence_provenance_sources"]
    assert sequence["status"] == "PASS"


def test_local_interaction_evidence_preserves_focus_and_revealed_state(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    report = prepare_visual_semantic_grammar_evaluation(output_dir=output)
    interactions = [
        action
        for case in report["fixed_evaluation_cases"]
        for action in case["local_interactions_tested"]
    ]
    assert interactions
    assert all(action["focus_before"] == action["focus_after"] for action in interactions)
    assert all(
        action["revealed_before"] == action["revealed_after"]
        for action in interactions
    )


def test_prose_fallback_remains_unadorned(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    report = prepare_visual_semantic_grammar_evaluation(output_dir=output)
    cases = {item["case"]: item for item in report["fixed_evaluation_cases"]}
    prose = cases["truthful_prose_fallback"]
    assert prose["representation_strategy"] == "CONCISE_PROSE"
    assert prose["inspectable_components"] == []
    assert prose["visual_grammar_roles"] == ["reading-prose"]


def test_evaluation_regeneration_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_visual_semantic_grammar_evaluation(output_dir=first)
    prepare_visual_semantic_grammar_evaluation(output_dir=second)
    assert _hashes(first, exclude_lifecycle=True) == _hashes(
        second, exclude_lifecycle=True
    )


def test_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("browser_console_clean")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_visual_semantic_grammar_evaluation(output, invalid)
    report = finalize_visual_semantic_grammar_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_finalize_requires_all_deterministic_browser_captures(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_visual_semantic_grammar_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["deterministic_captures"].pop()
    with pytest.raises(ValidationError, match="captures are incomplete"):
        finalize_visual_semantic_grammar_evaluation(output, invalid)


def test_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-visual-semantic-grammar", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec037_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-037-visual-semantic-grammar-20260908"
    )
    if not output.exists():
        pytest.skip("generated after focused implementation checks")
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert report["deterministic_regeneration_result"]["result"] == (
        "PASS_BYTE_IDENTICAL"
    )
    assert report["offline_test_result"]["result"] == "PASS"
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
