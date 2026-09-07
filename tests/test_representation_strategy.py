import copy
import hashlib
import inspect
import json
from dataclasses import replace
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.models import ValidationError
from knowledge_compiler.representation_strategy import (
    RepresentationContext,
    StrategyType,
    _strategy_rule,
    build_plan_catalog,
    ground_context,
    resolve_representation,
)
from knowledge_compiler.representation_strategy_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC033_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    default_spec033_directory,
    finalize_representation_strategy_evaluation,
    prepare_representation_strategy_evaluation,
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs() -> tuple[dict, dict]:
    source = default_spec033_directory()
    return _json(source / "workspace-fixture.json"), _json(source / "depth-map.json")


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


def _representation(fixture: dict, domain_id: str, structure_type: str) -> tuple[dict, dict]:
    domain = next(item for item in fixture["domains"] if item["domain_id"] == domain_id)
    representation = next(
        item
        for item in domain["learning_model"]["representations"]
        if item["representation_type"] == structure_type
    )
    return domain, representation


@pytest.mark.parametrize(
    ("domain_id", "structure_type", "identity", "expected"),
    [
        ("economics", "CAUSAL_PATH", "market-price", StrategyType.CAUSAL_MECHANISM),
        ("software_architecture", "HIERARCHY", "modular-order-processing-service", StrategyType.HIERARCHY_COMPOSITION),
        ("history", "DEPENDENCY_CHAIN", "printing", StrategyType.DEPENDENCY_STRUCTURE),
        ("history", "PROCESS_CHAIN", "printed-controversy", StrategyType.PROCESS_SEQUENCE),
        ("electromagnetism", "FEEDBACK_CANDIDATE", "electric-field", StrategyType.RECIPROCAL_MECHANISM),
    ],
)
def test_strategy_follows_trusted_structure(domain_id, structure_type, identity, expected) -> None:
    fixture, _ = _inputs()
    domain, representation = _representation(fixture, domain_id, structure_type)
    plan = resolve_representation(ground_context(domain, representation, "concept", identity))
    assert plan.strategy_type is expected
    assert plan.semantic_focus_identity == identity
    assert plan.deterministic_rule_metadata["domain_is_resolver_input"] is False
    assert plan.deterministic_rule_metadata["depth_is_resolver_input"] is False


def test_canonical_relationship_uses_focused_form_with_exact_provenance() -> None:
    fixture, _ = _inputs()
    domain, representation = _representation(fixture, "economics", "CAUSAL_PATH")
    plan = resolve_representation(
        ground_context(domain, representation, "canonical", "rel-shortage-upward-pressure")
    )
    assert plan.strategy_type is StrategyType.FOCUSED_RELATIONSHIP
    assert plan.payload["relationship"]["relationship_ids"] == ["rel-shortage-upward-pressure"]
    assert [item["quote"] for item in plan.evidence_refs] == [
        "a shortage puts upward pressure on price."
    ]


def test_thin_concept_falls_back_truthfully() -> None:
    _, depth = _inputs()
    from knowledge_compiler.representation_strategy import depth_context

    plan = resolve_representation(depth_context(depth["expansions"][0], "concept", "atom"))
    assert plan.strategy_type is StrategyType.CONCISE_PROSE
    assert plan.deterministic_rule_metadata["fallback_reason"] == (
        "NO_TRUSTED_SUPPORTING_RELATIONSHIP"
    )
    assert plan.payload["relationships"] == []


def test_mixed_unsupported_structure_fails_to_prose_without_invention() -> None:
    context = RepresentationContext(
        context_key="synthetic:mixed",
        semantic_focus_identity="a",
        semantic_class="concept",
        label="A",
        description="Trusted A.",
        structure_type=None,
        nodes=(
            {"entity_id": "a", "label": "A", "description": "Trusted A."},
            {"entity_id": "b", "label": "B", "description": "Trusted B."},
        ),
        relationships=(
            {
                "relationship_ids": ["r1"],
                "source_entity_id": "a",
                "target_entity_id": "b",
                "relationship_type": "RELATED_TO",
                "meaning": "Trusted relation.",
                "direction": "DIRECTED",
                "provenance_status": "EXACT_SOURCE_EVIDENCE",
                "evidence": [],
            },
        ),
        warnings=(),
        trusted_input_refs=("synthetic trusted fixture",),
    )
    plan = resolve_representation(context)
    assert plan.strategy_type is StrategyType.CONCISE_PROSE
    assert plan.deterministic_rule_metadata["fallback_reason"] == (
        "MIXED_OR_UNSUPPORTED_TRUSTED_STRUCTURE"
    )
    assert plan.payload["relationships"][0]["relationship_type"] == "RELATED_TO"


def test_domain_and_depth_are_not_strategy_inputs() -> None:
    source = inspect.getsource(_strategy_rule).casefold()
    for forbidden in ("economics", "software_architecture", "history", "electromagnetism"):
        assert forbidden not in source
    fixture, _ = _inputs()
    domain, representation = _representation(fixture, "economics", "CAUSAL_PATH")
    context = ground_context(domain, representation, "concept", "market-price")
    deep_alias = replace(context, context_key="synthetic:depth-10")
    assert resolve_representation(context).strategy_type == resolve_representation(deep_alias).strategy_type
    assert resolve_representation(context).deterministic_rule_metadata == resolve_representation(deep_alias).deterministic_rule_metadata


def test_plan_catalog_is_deterministic_and_complete() -> None:
    fixture, depth = _inputs()
    first = build_plan_catalog(fixture, depth)
    second = build_plan_catalog(copy.deepcopy(fixture), copy.deepcopy(depth))
    assert first == second
    assert len(first) == 71
    strategies = {item["strategy_type"] for item in first.values()}
    assert {value.value for value in StrategyType} <= strategies


def test_context_validation_fails_closed_for_unknown_endpoint() -> None:
    with pytest.raises(ValidationError, match="endpoint is absent"):
        RepresentationContext(
            context_key="broken",
            semantic_focus_identity="a",
            semantic_class="concept",
            label="A",
            description="A",
            structure_type="CAUSAL_PATH",
            nodes=({"entity_id": "a", "label": "A"},),
            relationships=({"source_entity_id": "a", "target_entity_id": "missing", "relationship_type": "CAUSES"},),
            warnings=(),
            trusted_input_refs=("fixture",),
        )


def test_evaluation_composes_spec033_and_passes_offline_gate(tmp_path: Path) -> None:
    before = _hashes(default_spec033_directory())
    output = tmp_path / "candidate"
    report = prepare_representation_strategy_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert before == _hashes(default_spec033_directory())
    assert report["spec033_identity_before"]["aggregate_sha256"] == FROZEN_SPEC033_DIRECTORY_SHA256
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())
    assert len([count for count in report["strategy_counts"].values() if count]) >= 4
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []


def test_evaluation_regeneration_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_representation_strategy_evaluation(output_dir=first)
    prepare_representation_strategy_evaluation(output_dir=second)
    assert _hashes(first, exclude_lifecycle=True) == _hashes(second, exclude_lifecycle=True)


def test_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_representation_strategy_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("browser_console_clean")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_representation_strategy_evaluation(output, invalid)
    report = finalize_representation_strategy_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert _json(output / "human-review-template.json")["status"] == "PENDING_OWNER_REVIEW"


def test_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-representation-strategy", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == OWNER_REVIEW_INSTRUCTION


def test_committed_spec034_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-034-representation-strategy-grammar-20260907"
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
        "focused": "54 passed",
        "full": "445 passed",
        "result": "PASS",
    }
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
