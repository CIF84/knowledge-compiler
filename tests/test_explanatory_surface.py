import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.explanatory_surface import (
    ExplanatoryLocalState,
    LearningFocus,
)
from knowledge_compiler.explanatory_surface_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC034_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    default_spec034_directory,
    finalize_explanatory_surface_evaluation,
    prepare_explanatory_surface_evaluation,
)
from knowledge_compiler.models import ValidationError


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
    return {
        "status": "PASS",
        "browser": "test fixture",
        "checks": {name: True for name in BROWSER_CHECKS},
        "console": {"errors": [], "warnings": [], "result": "PASS"},
    }


@pytest.mark.parametrize(
    ("kind", "identity", "local_key"),
    [
        ("concept", "double-slit-experiment", "concept:interference-pattern"),
        (
            "canonical",
            "changing-electric-field-induces-magnetic-field",
            "concept:electric-field",
        ),
        (
            "canonical",
            "changing-electric-field-induces-magnetic-field",
            "concept:magnetic-field",
        ),
        ("concept", "light", "concept:electromagnetic-wave"),
    ],
)
def test_local_interaction_never_mutates_focus(kind, identity, local_key) -> None:
    focus = LearningFocus("trusted-context", kind, identity)
    state = ExplanatoryLocalState()
    result = state.interact(focus=focus, local_key=local_key)
    assert result["focus_before"] == result["focus_after"] == focus.to_dict()
    assert result["navigation_mutation"] is False
    assert result["highlighted_key"] == local_key


def test_local_highlight_toggles_without_becoming_navigation_state() -> None:
    focus = LearningFocus("context-a", "concept", "double-slit-experiment")
    state = ExplanatoryLocalState()
    assert state.interact(focus=focus, local_key="concept:interference-pattern")[
        "highlighted_key"
    ] == "concept:interference-pattern"
    result = state.interact(focus=focus, local_key="concept:interference-pattern")
    assert result["highlighted_key"] is None
    assert result["interaction_count"] == 2
    assert result["navigation_mutation"] is False


def test_local_state_resets_when_authoritative_context_changes() -> None:
    state = ExplanatoryLocalState()
    state.interact(
        focus=LearningFocus("context-a", "concept", "a"),
        local_key="concept:b",
    )
    state.synchronize_context("context-b")
    assert state.context_key == "context-b"
    assert state.highlighted_key is None
    assert state.interaction_count == 1


@pytest.mark.parametrize(
    "focus",
    [
        ("", "concept", "a"),
        ("context", "", "a"),
        ("context", "concept", ""),
    ],
)
def test_empty_authoritative_focus_fails_closed(focus) -> None:
    with pytest.raises(ValidationError, match="non-empty"):
        LearningFocus(*focus)


def test_empty_local_key_fails_closed() -> None:
    with pytest.raises(ValidationError, match="non-empty"):
        ExplanatoryLocalState().interact(
            focus=LearningFocus("context", "concept", "a"), local_key=""
        )


def test_evaluation_composes_exact_spec034_and_passes_machine_gate(
    tmp_path: Path,
) -> None:
    before = _hashes(default_spec034_directory())
    output = tmp_path / "candidate"
    report = prepare_explanatory_surface_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == _hashes(default_spec034_directory())
    assert report["spec034_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC034_DIRECTORY_SHA256
    )
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert all(
        item["focus_before"] == item["focus_after"]
        for item in report["focus_isolation_cases"]
    )
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []


def test_candidate_preserves_heterogeneous_strategy_catalog(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    report = prepare_explanatory_surface_evaluation(output_dir=output)
    strategies = report["representation_strategies_preserved"]
    assert len(strategies) == 7
    assert "CAUSAL_MECHANISM" in strategies
    assert "HIERARCHY_COMPOSITION" in strategies
    assert "FOCUSED_RELATIONSHIP" in strategies
    assert "CONCISE_PROSE" in strategies


def test_browser_overlay_removes_navigation_contract_and_depth_shortcut(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_explanatory_surface_evaluation(output_dir=output)
    script = (output / "explanatory-surface.js").read_text()
    stylesheet = (output / "explanatory-surface.css").read_text()
    assert "purificationAtomicAttributes" in script
    assert "removeAttribute" in script
    assert "purificationLocalInteraction" in script
    assert "button.hidden=true" in script
    assert "button.disabled=true" in script
    assert "#learning-pane .contextual-depth" in stylesheet
    assert "history-back" not in script
    assert "breadcrumb" not in script.casefold()


def test_evaluation_regeneration_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_explanatory_surface_evaluation(output_dir=first)
    prepare_explanatory_surface_evaluation(output_dir=second)
    assert _hashes(first, exclude_lifecycle=True) == _hashes(
        second, exclude_lifecycle=True
    )


def test_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_explanatory_surface_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("browser_console_clean")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_explanatory_surface_evaluation(output, invalid)
    report = finalize_explanatory_surface_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["explore_next_operational"] is True
    assert report["my_map_navigation_operational"] is True
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-explanatory-surface", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec035_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-035-explanatory-surface-purification-20260907"
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
