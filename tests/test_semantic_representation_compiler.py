import hashlib
import inspect
import json
from dataclasses import replace
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.models import KnowledgeModel, RelationshipType, ValidationError
from knowledge_compiler.semantic_representation_compiler import (
    COMPARE_CONTRAST,
    compile_semantic_representation,
)
from knowledge_compiler.semantic_representation_gate_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC038_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    default_spec038_directory,
    finalize_semantic_representation_gate_evaluation,
    prepare_semantic_representation_gate_evaluation,
)


ROOT = Path(__file__).parents[1]
SPEC003 = ROOT / "examples/evaluations/spec-003-relationship-semantics-20260903"
SPEC010 = ROOT / "examples/evaluations/spec-010-proposition-modeling-20260903"


def _model(path: Path) -> KnowledgeModel:
    return KnowledgeModel.from_dict(json.loads(path.read_text(encoding="utf-8")))


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
    cases = (
        "causal_mechanism",
        "hierarchy_composition",
        "dependency_structure",
        "process_sequence",
        "reciprocal_mechanism",
        "prose_fallback",
    )
    return {
        "status": "PASS",
        "browser": "test fixture",
        "checks": {name: True for name in BROWSER_CHECKS},
        "console": {"errors": [], "warnings": [], "result": "PASS"},
        "deterministic_captures": [
            {"case": case, "result": "PASS"} for case in cases
        ],
    }


@pytest.mark.parametrize(
    ("filename", "identity", "expected"),
    [
        ("economics.knowledge.json", "market-price", "CAUSAL_MECHANISM"),
        (
            "software_architecture.knowledge.json",
            "modular-order-processing-service",
            "HIERARCHY_COMPOSITION",
        ),
        ("history.knowledge.json", "printing", "DEPENDENCY_STRUCTURE"),
        ("history.knowledge.json", "authorities", "PROCESS_SEQUENCE"),
        (
            "electromagnetism.knowledge.json",
            "electric-field",
            "RECIPROCAL_MECHANISM",
        ),
    ],
)
def test_strategy_is_inferred_from_detected_semantics_without_structure_hint(
    filename: str, identity: str, expected: str
) -> None:
    decision = compile_semantic_representation(
        _model(SPEC003 / filename), "concept", identity
    )
    assert decision.selected_strategy == expected
    assert decision.representation_plan is not None
    assert decision.representation_plan.deterministic_rule_metadata[
        "structure_type"
    ] is None
    assert decision.renderer_contract == "SPEC038_REPRESENTATION_PLAN"


def test_semantically_equivalent_structure_with_different_labels_resolves_identically() -> None:
    model = _model(SPEC003 / "economics.knowledge.json")
    renamed = replace(
        model,
        document=replace(
            model.document,
            metadata={"domain": "unrelated", "filename": "other.txt"},
        ),
        entities=tuple(
            replace(entity, name=f"Object {index}", description=f"Description {index}")
            for index, entity in enumerate(model.entities)
        ),
    )
    first = compile_semantic_representation(model, "concept", "market-price")
    second = compile_semantic_representation(renamed, "concept", "market-price")
    assert first.strategy_signature() == second.strategy_signature()


def test_materially_different_semantic_shapes_select_different_strategies() -> None:
    economics = compile_semantic_representation(
        _model(SPEC003 / "economics.knowledge.json"), "concept", "market-price"
    )
    history = compile_semantic_representation(
        _model(SPEC003 / "history.knowledge.json"), "concept", "authorities"
    )
    software = compile_semantic_representation(
        _model(SPEC003 / "software_architecture.knowledge.json"),
        "concept",
        "modular-order-processing-service",
    )
    assert {
        economics.selected_strategy,
        history.selected_strategy,
        software.selected_strategy,
    } == {"CAUSAL_MECHANISM", "PROCESS_SEQUENCE", "HIERARCHY_COMPOSITION"}


def test_unsupported_concept_fails_closed_to_prose() -> None:
    decision = compile_semantic_representation(
        _model(SPEC003 / "biology.knowledge.json"), "concept", "gene"
    )
    assert decision.selected_strategy == "CONCISE_PROSE"
    assert decision.sufficiency == "INSUFFICIENT_SUPPORTED_STRUCTURE"
    assert decision.fallback_reason == "NO_DETECTED_TRUSTED_STRUCTURE_CONTAINS_FOCUS"
    assert decision.available_relationships == ()


def test_reciprocal_structure_is_not_inferred_from_one_direction() -> None:
    model = _model(SPEC003 / "electromagnetism.knowledge.json")
    one_way = replace(
        model,
        entities=tuple(
            item
            for item in model.entities
            if item.id in {"electric-field", "magnetic-field"}
        ),
        relationships=tuple(
            item
            for item in model.relationships
            if item.id == "changing-electric-field-induces-magnetic-field"
        ),
        claims=(),
    )
    decision = compile_semantic_representation(one_way, "concept", "electric-field")
    assert decision.selected_strategy == "CONCISE_PROSE"
    assert decision.selected_strategy != "RECIPROCAL_MECHANISM"


def test_ambiguous_relationship_does_not_invent_topology() -> None:
    model = _model(SPEC003 / "electromagnetism.knowledge.json")
    relationship = next(
        item
        for item in model.relationships
        if item.id == "changing-electric-field-induces-magnetic-field"
    )
    ambiguous = replace(
        relationship, relationship_type=RelationshipType.INTERACTS_WITH
    )
    packet = replace(
        model,
        entities=tuple(
            item
            for item in model.entities
            if item.id in {"electric-field", "magnetic-field"}
        ),
        relationships=(ambiguous,),
        claims=(),
    )
    decision = compile_semantic_representation(packet, "concept", "electric-field")
    assert decision.selected_strategy == "CONCISE_PROSE"
    assert decision.detected_structural_signals == ()


def test_focused_relationship_preserves_exact_source_provenance() -> None:
    decision = compile_semantic_representation(
        _model(SPEC003 / "economics.knowledge.json"),
        "canonical",
        "rel-shortage-upward-pressure",
    )
    assert decision.selected_strategy == "FOCUSED_RELATIONSHIP"
    assert [item["quote"] for item in decision.grounding_provenance_refs] == [
        "a shortage puts upward pressure on price."
    ]
    assert decision.representation_plan is not None
    assert decision.representation_plan.payload["relationship"][
        "relationship_ids"
    ] == ["rel-shortage-upward-pressure"]


def test_explicit_comparison_proposition_selects_compare_contrast_before_rendering() -> None:
    model = _model(SPEC010 / "economics.proposition-aware.knowledge.json")
    decision = compile_semantic_representation(
        model, "proposition", model.propositions[0].id
    )
    assert decision.selected_strategy == COMPARE_CONTRAST
    assert decision.selected_rule_id == "EXPLICIT_COMPARISON_PROPOSITION"
    assert decision.semantic_payload["comparison_operator"] == "GREATER_THAN"
    assert decision.grounding_provenance_refs
    assert decision.representation_plan is None


def test_transfer_event_is_not_misclassified_as_worked_example() -> None:
    model = _model(SPEC010 / "process.proposition-aware.knowledge.json")
    decision = compile_semantic_representation(
        model, "proposition", model.propositions[0].id
    )
    assert decision.selected_strategy == "CONCISE_PROSE"
    assert decision.fallback_reason == "NO_SUPPORTED_RULE_TO_INSTANCE_FORM"
    assert decision.rejected_candidates == (
        {
            "candidate": "WORKED_EXAMPLE",
            "reason": "TRANSFER_EVENT_IS_NOT_A_RULE_TO_INSTANCE_MAPPING",
        },
    )


def test_compiler_decision_code_contains_no_evaluation_fixture_answers() -> None:
    import knowledge_compiler.semantic_representation_compiler as compiler

    source = inspect.getsource(compiler).casefold()
    for forbidden in (
        "market-price",
        "economics",
        "electromagnetism",
        "software_architecture",
        "spec-003",
        "spec-038",
    ):
        assert forbidden not in source


def test_frozen_spec038_candidate_identity_is_exact() -> None:
    from knowledge_compiler.depth_interaction_evaluation import directory_identity

    assert directory_identity(default_spec038_directory())["aggregate_sha256"] == (
        FROZEN_SPEC038_DIRECTORY_SHA256
    )


def test_evaluation_composes_exact_spec038_and_passes_machine_gate(
    tmp_path: Path,
) -> None:
    before = _hashes(default_spec038_directory())
    output = tmp_path / "candidate"
    report = prepare_semantic_representation_gate_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == _hashes(default_spec038_directory())
    assert report["spec038_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC038_DIRECTORY_SHA256
    )
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_vocabulary_changes"] == []


def test_evaluation_records_all_required_semantic_shapes(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_semantic_representation_gate_evaluation(output_dir=output)
    packet = _json(output / "compiler-decisions.json")
    strategies = packet["aggregate_by_strategy"]
    for expected in (
        "CAUSAL_MECHANISM",
        "HIERARCHY_COMPOSITION",
        "DEPENDENCY_STRUCTURE",
        "PROCESS_SEQUENCE",
        "RECIPROCAL_MECHANISM",
        "FOCUSED_RELATIONSHIP",
        "COMPARE_CONTRAST",
        "CONCISE_PROSE",
    ):
        assert strategies[expected] >= 1
    assert packet["coverage_findings"]["worked_example"].startswith("UNSUPPORTED")


def test_evaluation_regeneration_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_semantic_representation_gate_evaluation(output_dir=first)
    prepare_semantic_representation_gate_evaluation(output_dir=second)
    assert _hashes(first, exclude_lifecycle=True) == _hashes(
        second, exclude_lifecycle=True
    )


def test_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_semantic_representation_gate_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("browser_console_clean")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_semantic_representation_gate_evaluation(output, invalid)
    report = finalize_semantic_representation_gate_evaluation(
        output, _browser_pass()
    )
    assert report["machine_integrity_verdict"] == "PASS"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_finalize_requires_all_deterministic_browser_captures(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_semantic_representation_gate_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["deterministic_captures"].pop()
    with pytest.raises(ValidationError, match="captures are incomplete"):
        finalize_semantic_representation_gate_evaluation(output, invalid)


def test_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-semantic-representation-gate", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec039_artifact_is_ready_for_owner_review() -> None:
    output = (
        ROOT
        / "examples/evaluations/spec-039-semantic-to-representation-compiler-gate-20260911"
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
