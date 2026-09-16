from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.models import KnowledgeModel, ValidationError
from knowledge_compiler.semantic_representation_compiler import compile_semantic_representation
from knowledge_compiler.spec054_claim_focus_experiment import (
    BRANCHES,
    EXPECTED_EVIDENCE_IDENTITIES,
    FOCUS_CONTRACT,
    IMPLEMENTATION_PATHS,
    NEXT_STEPS,
    OUTCOMES,
    OUTPUT_PATH,
    enumerate_claim_focuses,
    build_report,
    write_report,
)


ROOT = Path(__file__).parents[1]


def _report():
    return json.loads((ROOT / OUTPUT_PATH).read_text(encoding="utf-8"))


def test_all_98_frozen_claims_become_unique_deterministic_focuses():
    report = _report()
    decisions = report["claim_focus_decisions"]
    assert len(decisions) == 98
    assert len(
        {(item["focus"]["source_id"], item["focus"]["claim_id"]) for item in decisions}
    ) == 98
    focuses, models, directories = enumerate_claim_focuses(ROOT)
    assert len(focuses) == 98
    assert len(models) == len(directories) - 1 == 8
    assert [item.to_dict() for item in focuses] == [item["focus"] for item in decisions]


def test_focus_contract_preserves_claim_identity_without_diagnostic_routing_inputs():
    report = _report()
    assert report["experimental_claim_focus_contract"] == FOCUS_CONTRACT
    assert FOCUS_CONTRACT["semantic_class"] == "CLAIM"
    for decision in report["claim_focus_decisions"]:
        focus = decision["focus"]
        assert focus["semantic_class"] == "CLAIM"
        assert focus["claim_text"]
        assert focus["evidence"]
        assert focus["origin"] == "SOURCE"
        assert 0.0 <= focus["confidence"] <= 1.0
        assert "diagnostic_semantic_character" not in focus
        assert decision["resolver_adapter"]["diagnostic_character_used"] is False
        assert decision["resolver_adapter"]["source_or_domain_rule_used"] is False


def test_every_focus_receives_exactly_one_fixed_outcome_from_existing_grammar():
    report = _report()
    assert report["outcome_taxonomy"] == list(OUTCOMES)
    assert report["outcome_distribution"] == {
        "EXISTING_NON_FALLBACK_STRATEGY": 0,
        "TRUTHFUL_PROSE_FALLBACK": 98,
        "NO_STRATEGY": 0,
        "INVALID_OR_UNSAFE_DECISION": 0,
    }
    assert report["strategy_family_distribution"] == {"CONCISE_PROSE": 98}
    assert all(item["outcome"] in OUTCOMES for item in report["claim_focus_decisions"])
    assert all(
        item["selected_rule_id"] == "TRUTHFUL_PROSE_FALLBACK"
        for item in report["claim_focus_decisions"]
    )


def test_claim_decisions_are_grounded_safe_and_create_no_topology_or_surface_binding():
    report = _report()
    for decision in report["claim_focus_decisions"]:
        focus = decision["focus"]
        plan = decision["representation_plan"]
        assert all(decision["semantic_safety_audit"].values())
        assert decision["grounding_provenance_refs"] == focus["evidence"]
        assert plan["payload"]["body"] == focus["claim_text"]
        assert plan["payload"]["nodes"] == []
        assert plan["payload"]["relationships"] == []
        assert decision["learner_surface_binding_created"] is False
    assert report["semantic_safety_summary"] == {
        "all_claim_text_and_evidence_unchanged": True,
        "all_provenance_attached": True,
        "claim_focus_count": 98,
        "knowledge_models_unchanged": True,
        "learner_surface_bindings_created": 0,
        "relationships_or_propositions_created": 0,
        "topology_created_or_inferred": 0,
        "unsafe_decision_count": 0,
    }


def test_frozen_non_claim_decisions_structures_and_models_are_identical():
    control = _report()["baseline_control_comparison"]
    assert control["source_count"] == 8
    assert control["all_models_unchanged"] is True
    assert control["all_non_claim_decisions_equal"] is True
    assert control["all_detected_structures_equal"] is True
    for row in control["sources"]:
        assert row["model_identity_before_sha256"] == row["model_identity_after_sha256"]
        assert row["canonical_non_claim_decisions_sha256"] == row["regenerated_non_claim_decisions_sha256"]
        assert row["canonical_structures_sha256"] == row["regenerated_structures_sha256"]


def test_diagnostic_characters_are_post_hoc_only_and_all_fall_back_truthfully():
    analysis = _report()["post_hoc_diagnostic_character_analysis"]
    assert analysis["labels_are_not_strategy_inputs"] is True
    expected_counts = {
        "CONTEXTUAL_FACT": 33,
        "DEFINITION_DESCRIPTION": 15,
        "DESCRIPTIVE_CONTRAST": 6,
        "QUALIFICATION_CONDITION": 19,
        "QUANTITATIVE_FACT": 22,
        "SCALAR_NUMERIC_COMPARISON": 3,
    }
    assert analysis["outcomes_by_character"] == {
        key: {"TRUTHFUL_PROSE_FALLBACK": count} for key, count in expected_counts.items()
    }
    assert analysis["strategies_by_character"] == {
        key: {"CONCISE_PROSE": count} for key, count in expected_counts.items()
    }


def test_named_spec053_review_sample_is_preserved_and_safely_resolved():
    samples = _report()["named_review_sample"]
    assert len(samples) == 4
    assert {item["selection_reason"] for item in samples} == {
        "standalone scalar comparison",
        "descriptive contrast",
        "quantitative fact",
        "claim sharing exact evidence with existing topology",
    }
    assert all(item["outcome"] == "TRUTHFUL_PROSE_FALLBACK" for item in samples)
    assert all(item["selected_strategy_family"] == "CONCISE_PROSE" for item in samples)
    assert all(item["semantic_safety_pass"] for item in samples)
    assert all(not item["diagnostic_character_used_for_selection"] for item in samples)


def test_branch_and_next_step_are_singular_owner_gated_and_not_implemented():
    report = _report()
    assert report["experiment_branch"]["class"] == "LEARNER_SURFACE_REQUIRED_TO_DECIDE"
    assert report["experiment_branch"]["class"] in BRANCHES
    assert report["recommended_next_step"]["class"] == "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT"
    assert report["recommended_next_step"]["class"] in NEXT_STEPS
    assert report["recommended_next_step"]["implementation_authorized"] is False
    assert report["owner_review"] == {
        "promotion": "NOT_AUTHORIZED",
        "state": "OWNER_REVIEW",
        "verdict": "PENDING",
    }
    assert all(value == 0 for value in report["execution_integrity"].values())


def test_frozen_evidence_and_implementation_hashes_match_and_production_rejects_claim():
    report = _report()
    evidence = {item["path"]: item["sha256"] for item in report["evidence_identities"]}
    assert evidence == EXPECTED_EVIDENCE_IDENTITIES
    for path, expected in evidence.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    implementation = {
        item["path"]: item["sha256"] for item in report["implementation_identities"]
    }
    assert set(implementation) == set(IMPLEMENTATION_PATHS)
    for path, expected in implementation.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    first = report["claim_focus_decisions"][0]["focus"]
    model = KnowledgeModel.from_dict(json.loads((ROOT / first["model_path"]).read_text()))
    with pytest.raises(ValidationError, match="unsupported compiler semantic class"):
        compile_semantic_representation(model, "claim", first["claim_id"])


def test_report_regenerates_byte_identically_and_records_final_validation(tmp_path):
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    expected = build_report(ROOT)
    write_report(ROOT, left)
    write_report(ROOT, right)
    assert left.read_bytes() == right.read_bytes()
    assert left.read_bytes() == (ROOT / OUTPUT_PATH).read_bytes()
    assert json.loads(left.read_text()) == expected
    assert expected["validation"] == {
        "deterministic_regeneration": "PASS",
        "focused_spec054_and_frozen_control_tests": "PASS (103 tests)",
        "full_offline_suite": "PASS (642 tests)",
        "git_diff_check": "PASS",
        "json_validation": "PASS",
        "protected_state_audit": "PASS (hash-bound and baseline-equivalent)",
        "provenance_and_secret_safety": "PASS",
        "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
    }
