import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.explanatory_surface import LearningFocus
from knowledge_compiler.models import ValidationError
from knowledge_compiler.structure_aware_surface import (
    RepresentationLocalState,
    inspectable_components,
)
from knowledge_compiler.structure_aware_surface_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC035_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    default_spec035_directory,
    finalize_structure_aware_surface_evaluation,
    prepare_structure_aware_surface_evaluation,
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _plans() -> dict:
    return _json(default_spec035_directory() / "representation-plans.json")["plans"]


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


def test_components_are_derived_from_trusted_plan_payload() -> None:
    plan = _plans()[
        "ground:electromagnetism:representation-9058fd6ab1975a17:canonical:changing-electric-field-induces-magnetic-field"
    ]
    components = {item.local_key: item for item in inspectable_components(plan)}
    assert set(components) == {
        "concept:electric-field",
        "concept:magnetic-field",
        "canonical:changing-electric-field-induces-magnetic-field",
    }
    relationship = components[
        "canonical:changing-electric-field-induces-magnetic-field"
    ]
    assert relationship.predicate == "INDUCES"
    assert relationship.direction == "inducer_to_induced_effect"
    assert [item["quote"] for item in relationship.evidence] == [
        "A changing electric field induces a magnetic field."
    ]


def test_rich_hierarchy_exposes_concepts_and_canonical_relationships() -> None:
    plan = _plans()[
        "ground:software_architecture:representation-985e777f01fa9ec8:concept:modular-order-processing-service"
    ]
    components = inspectable_components(plan)
    assert len([item for item in components if item.kind == "concept"]) == 5
    assert len([item for item in components if item.kind == "canonical"]) == 4
    assert {item.predicate for item in components if item.kind == "canonical"} == {
        "PART_OF"
    }


def test_concise_prose_does_not_get_artificial_inspection_components() -> None:
    plan = _plans()["depth:depth-double-slit-v1:concept:atom"]
    assert plan["strategy_type"] == "CONCISE_PROSE"
    assert inspectable_components(plan) == ()


def test_invalid_component_payload_fails_closed() -> None:
    broken = {
        "strategy_type": "CAUSAL_MECHANISM",
        "payload": {
            "nodes": [{"entity_id": "a", "label": "A"}],
            "relationships": [],
        },
    }
    with pytest.raises(ValidationError, match="identity, label, and description"):
        inspectable_components(broken)


def test_relationship_with_unknown_endpoint_fails_closed() -> None:
    broken = {
        "strategy_type": "CAUSAL_MECHANISM",
        "payload": {
            "nodes": [{"entity_id": "a", "label": "A", "description": "A."}],
            "relationships": [
                {
                    "relationship_ids": ["r"],
                    "source_entity_id": "a",
                    "target_entity_id": "missing",
                    "relationship_type": "CAUSES",
                    "meaning": "A causes missing.",
                }
            ],
        },
    }
    with pytest.raises(ValidationError, match="not fully grounded"):
        inspectable_components(broken)


@pytest.mark.parametrize("action", ["hover", "select"])
def test_local_interaction_preserves_focus_and_revealed_knowledge(action) -> None:
    state = RepresentationLocalState()
    focus = LearningFocus("context", "concept", "double-slit-experiment")
    result = state.interact(
        action=action,
        focus=focus,
        revealed_object_keys=(
            "orientation:domain:electromagnetism",
            "concept:double-slit-experiment",
        ),
        component_id="concept:interference-pattern",
    )
    assert result["focus_before"] == result["focus_after"]
    assert result["revealed_before"] == result["revealed_after"]
    assert result["navigation_mutation"] is False
    assert result["revealed_knowledge_mutation"] is False


def test_hover_preview_defers_to_pinned_selection_after_exit() -> None:
    state = RepresentationLocalState()
    focus = LearningFocus("context", "canonical", "relationship")
    revealed = ("canonical:relationship",)
    state.interact(
        action="select",
        focus=focus,
        revealed_object_keys=revealed,
        component_id="concept:a",
    )
    state.interact(
        action="hover",
        focus=focus,
        revealed_object_keys=revealed,
        component_id="concept:b",
    )
    assert state.effective_component_id == "concept:b"
    state.interact(
        action="hover_exit", focus=focus, revealed_object_keys=revealed
    )
    assert state.effective_component_id == "concept:a"


def test_clear_restores_focus_summary_without_navigation() -> None:
    state = RepresentationLocalState()
    focus = LearningFocus("context", "concept", "light")
    state.interact(
        action="select",
        focus=focus,
        revealed_object_keys=("concept:light",),
        component_id="concept:electromagnetic-wave",
    )
    result = state.interact(
        action="clear", focus=focus, revealed_object_keys=("concept:light",)
    )
    assert result["effective_component_id"] is None
    assert result["focus_before"] == result["focus_after"]


def test_context_change_resets_both_local_channels() -> None:
    state = RepresentationLocalState(
        context_key="old", hovered_component_id="concept:a", selected_component_id="concept:b"
    )
    state.synchronize_context("new")
    assert state.hovered_component_id is None
    assert state.selected_component_id is None


def test_invalid_local_action_fails_closed() -> None:
    with pytest.raises(ValidationError, match="unknown representation-local action"):
        RepresentationLocalState().interact(
            action="navigate",
            focus=LearningFocus("context", "concept", "a"),
            revealed_object_keys=(),
            component_id="concept:b",
        )


def test_evaluation_composes_exact_spec035_and_passes_machine_gate(
    tmp_path: Path,
) -> None:
    before = _hashes(default_spec035_directory())
    output = tmp_path / "candidate"
    report = prepare_structure_aware_surface_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == _hashes(default_spec035_directory())
    assert report["spec035_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC035_DIRECTORY_SHA256
    )
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []


def test_fixed_cases_cover_rich_sparse_relationship_and_prose(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    report = prepare_structure_aware_surface_evaluation(output_dir=output)
    cases = {item["case"]: item for item in report["fixed_evaluation_cases"]}
    assert cases["history_printing"]["presentation_treatment"] == (
        "DOMINANT_RICH_STRUCTURE"
    )
    assert cases["software_composition"]["relationship_count"] == 4
    assert cases["light_hierarchy"]["presentation_treatment"] == (
        "SPARSE_STRUCTURAL_CUE_PLUS_INSPECTION"
    )
    assert cases["truthful_prose_fallback"]["inspectable_components_exposed"] == []
    assert cases["field_focused_relationship"]["selected_representation_strategy"] == (
        "FOCUSED_RELATIONSHIP"
    )


def test_depth_uses_same_strategy_and_inspection_grammar(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    report = prepare_structure_aware_surface_evaluation(output_dir=output)
    assert report["depth_independence"] == {
        "status": "PASS",
        "ground_strategy": "CAUSAL_MECHANISM",
        "deep_strategy": "CAUSAL_MECHANISM",
        "component_grammar_equal": True,
    }


def test_browser_layer_has_no_navigation_dispatch_or_new_forward_control(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_structure_aware_surface_evaluation(output_dir=output)
    script = (output / "structure-aware-surface.js").read_text()
    assert "representation-inspection" in script
    assert "surfaceHover" in script
    assert "surfaceCaptureLocal" in script
    assert "surfaceClearSelection" in script
    assert "__SPEC029_ATOMIC__.dispatch" not in script
    assert "__SPEC033_REVEALED__.select" not in script
    assert "Explore deeper" not in script
    assert "history-back" not in script


def test_evaluation_regeneration_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_structure_aware_surface_evaluation(output_dir=first)
    prepare_structure_aware_surface_evaluation(output_dir=second)
    assert _hashes(first, exclude_lifecycle=True) == _hashes(
        second, exclude_lifecycle=True
    )


def test_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_structure_aware_surface_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("browser_console_clean")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_structure_aware_surface_evaluation(output, invalid)
    report = finalize_structure_aware_surface_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-structure-aware-surface", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec036_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-036-structure-aware-explanatory-surface-20260908"
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
