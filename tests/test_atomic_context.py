import copy
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.atomic_context import (
    AtomicLearnerState,
    ContextKey,
    ContextualOccurrence,
    adversarial_transition_matrix,
    project_learner_state,
    reduce_learner_state,
)
from knowledge_compiler.atomic_context_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC028_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    SPEC028_RUNTIME_FILES,
    default_spec028_directory,
    finalize_atomic_context_evaluation,
    prepare_atomic_context_evaluation,
)
from knowledge_compiler.canonical_interaction import SemanticKey
from knowledge_compiler.cli import main
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


def _context(name: str = "a") -> ContextKey:
    return ContextKey(name, "primary")


def _occurrence(
    identity: str = "item",
    kind: str = "concept",
    context: ContextKey | None = None,
    ancestry: tuple[str, ...] = (),
    surface: str = "map",
) -> ContextualOccurrence:
    return ContextualOccurrence(
        SemanticKey(identity, kind), context or _context(), ancestry, surface
    )


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "test fixture",
        "checks": {name: True for name in BROWSER_CHECKS},
        "console": {"errors": [], "result": "PASS", "warnings": []},
    }


def test_context_replacement_atomically_discards_old_focus() -> None:
    source = _context("source")
    target = _context("target")
    state = reduce_learner_state(
        AtomicLearnerState(source, ("depth-1",)),
        "select",
        occurrence=_occurrence("old", "explanation", source, ("depth-1",)),
    )
    replacement = _occurrence("new", "canonical", target)
    state = reduce_learner_state(
        state,
        "replace_context",
        context=target,
        occurrence=replacement,
    )
    assert state.active_context == target
    assert state.revealed_contexts == ()
    assert state.selected == SemanticKey("new", "canonical")
    assert state.hovered is None
    assert state.selected_ancestry == ()


def test_context_replacement_without_focus_is_clear() -> None:
    source = _context("source")
    target = _context("target")
    state = AtomicLearnerState(
        source,
        ("depth",),
        hovered=SemanticKey("old", "concept"),
        selected=SemanticKey("older", "concept"),
        hover_ancestry=("depth",),
        selected_ancestry=("depth",),
    )
    state = reduce_learner_state(state, "replace_context", context=target)
    assert state == AtomicLearnerState(target)


def test_semantic_actions_fail_closed_outside_active_context() -> None:
    state = AtomicLearnerState(_context("a"))
    foreign = _occurrence(context=_context("b"))
    with pytest.raises(ValidationError, match="outside the active learner context"):
        reduce_learner_state(state, "select", occurrence=foreign)
    with pytest.raises(ValidationError, match="outside the active learner context"):
        reduce_learner_state(state, "hover", occurrence=foreign)


def test_unrevealed_descendant_fails_closed() -> None:
    state = AtomicLearnerState(_context("a"), ("depth-1",))
    hidden = _occurrence(ancestry=("depth-1", "depth-2"))
    with pytest.raises(ValidationError, match="outside the active learner context"):
        reduce_learner_state(state, "select", occurrence=hidden)


def test_retraction_clears_only_focus_that_belongs_to_retracted_depth() -> None:
    context = _context()
    deep = reduce_learner_state(
        AtomicLearnerState(context, ("depth-1", "depth-2")),
        "select",
        occurrence=_occurrence(ancestry=("depth-1", "depth-2")),
    )
    retracted = reduce_learner_state(
        deep, "retract_context", revealed_contexts=("depth-1",)
    )
    assert retracted.selected is None
    ground = reduce_learner_state(
        AtomicLearnerState(context, ("depth-1", "depth-2")),
        "select",
        occurrence=_occurrence("ground"),
    )
    ground = reduce_learner_state(
        ground, "retract_context", revealed_contexts=("depth-1",)
    )
    assert ground.selected == SemanticKey("ground", "concept")


def test_all_projections_have_one_identical_context_and_focus() -> None:
    context = _context("history")
    state = reduce_learner_state(
        AtomicLearnerState(context),
        "select",
        occurrence=_occurrence("relationship", "canonical", context),
    )
    projection = project_learner_state(state)
    assert projection["active_context_count"] == 1
    assert projection["map_projected_state"] == projection["right_pane_projected_state"]
    assert projection["map_projected_state"] == projection["explanation_projected_state"]
    assert projection["stale_prior_context_semantic_identities"] == []
    assert projection["stale_prior_context_authoritative_projections"] == []


def test_adversarial_transition_matrix_covers_required_sequences() -> None:
    matrix = adversarial_transition_matrix()
    assert matrix["status"] == "PASS"
    assert matrix["context_transition_behavior_depth_independent"] == "PASS"
    assert matrix["stale_prior_context_semantic_state"] == 0
    assert matrix["stale_prior_context_authoritative_projection"] == 0
    names = {row["sequence"] for row in matrix["rows"]}
    assert {
        "A ground concept -> B ground concept",
        "A ground relationship -> B ground relationship",
        "A deep concept -> B ground concept",
        "A deep relationship -> B ground relationship",
        "A deep source explanation -> B ground concept",
        "A deep object -> clear -> B context",
        "A deep object -> collapse/retract -> B context",
        "A -> B -> A rapid switching",
        "Software Architecture relationship -> History -> Electromagnetism",
    } <= names
    assert [row["depth"] for row in matrix["depth_transition_rows"]] == [0, 1, 2, 5, 10]


def test_spec029_composes_spec028_without_mutating_runtime(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_atomic_context_evaluation(output_dir=output)
    control = default_spec028_directory()
    for name in SPEC028_RUNTIME_FILES:
        if name == "index.html":
            continue
        assert (output / name).read_bytes() == (control / name).read_bytes()
    index = (output / "index.html").read_text(encoding="utf-8")
    assert '<script src="canonical-interaction.js"></script>' not in index
    assert '<script src="atomic-context.js"></script>' in index
    assert (output / "canonical-interaction.js").is_file()


def test_spec029_machine_gate_preserves_semantics_baselines_and_history(
    tmp_path: Path,
) -> None:
    baselines_before = protected_baseline_hashes()
    output = tmp_path / "candidate"
    report = prepare_atomic_context_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert protected_baseline_hashes() == baselines_before
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["representation_algorithm_changes"] == []
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["historical_identities_before"]["spec028"]["aggregate_sha256"] == (
        FROZEN_SPEC028_DIRECTORY_SHA256
    )
    assert report["historical_identities_before"] == report["historical_identities_after"]


def test_ground_relationship_coverage_includes_software_and_history(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_atomic_context_evaluation(output_dir=output)
    coverage = _json(output / "ground-relationship-coverage.json")
    assert coverage["status"] == "PASS"
    assert coverage["ground_level_relationship_projection_agreement"] == "PASS"
    assert {"software_architecture", "history"} <= set(coverage["covered_domains"])
    assert all(row["event_origins_tested"] == ["map", "representation"] for row in coverage["rows"])
    assert all(row["hover_preview_projection_agreement"] for row in coverage["rows"])


def test_spec029_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_atomic_context_evaluation(output_dir=first)
    prepare_atomic_context_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec029_rejects_spec028_substitution(tmp_path: Path) -> None:
    control = tmp_path / "spec028"
    shutil.copytree(default_spec028_directory(), control)
    with (control / "canonical-interaction.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="SPEC-028 historical artifact identity mismatch"):
        prepare_atomic_context_evaluation(
            output_dir=tmp_path / "rejected", spec028_dir=control
        )


def test_spec029_refuses_output_inside_frozen_spec028() -> None:
    output = default_spec028_directory() / "forbidden-spec029-output"
    assert not output.exists()
    with pytest.raises(ValidationError, match="must be isolated"):
        prepare_atomic_context_evaluation(output_dir=output)
    assert not output.exists()


def test_spec029_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_atomic_context_evaluation(output_dir=output)
    invalid = copy.deepcopy(_browser_pass())
    invalid["checks"].pop("deep_to_history_context_replaced_atomically")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_atomic_context_evaluation(output, invalid)
    report = finalize_atomic_context_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert _json(output / "human-review-template.json")["status"] == "PENDING_OWNER_REVIEW"


def test_spec029_cli_prepares_browser_pending_artifact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-atomic-context", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec029_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-029-atomic-context-transition-and-semantic-coverage-20260905"
    )
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert report["deterministic_regeneration_result"]["result"] == (
        "PASS_BYTE_IDENTICAL"
    )
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
