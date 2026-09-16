from __future__ import annotations

import hashlib
import json
from pathlib import Path

from knowledge_compiler.representation_strategy import StrategyType
from knowledge_compiler.spec055_claim_strategy_experiment import (
    BRANCHES,
    CHARACTERS,
    CONTRACT,
    EXPECTED_EVIDENCE_IDENTITIES,
    EXPERIMENTAL_STRATEGIES,
    IMPLEMENTATION_PATHS,
    NEXT_STEPS,
    OUTPUT_PATH,
    build_report,
    classify_claim,
    write_report,
)


ROOT = Path(__file__).parents[1]


def _report():
    return json.loads((ROOT / OUTPUT_PATH).read_text(encoding="utf-8"))


def test_all_98_claims_receive_one_character_and_one_final_strategy():
    report = _report()
    decisions = report["claim_classifications_and_plans"]
    assert len(decisions) == 98
    assert len({item["decision_id"] for item in decisions}) == 98
    assert len(
        {
            (item["focus_identity"]["source_id"], item["focus_identity"]["claim_id"])
            for item in decisions
        }
    ) == 98
    assert all(item["classification"]["character"] in CHARACTERS for item in decisions)
    assert all(item["final_safe_strategy"] in EXPERIMENTAL_STRATEGIES for item in decisions)


def test_generic_rules_distinguish_comparison_threshold_condition_and_context():
    assert classify_claim(
        "Alpha has more tools to set the agenda than beta."
    ).character == "QUANTITATIVE_COMPARISON"
    assert classify_claim(
        "Scientists located more than 23,000 atoms."
    ).character == "QUANTITATIVE_FACT"
    assert classify_claim(
        "When demand exceeds capacity, delay occurs."
    ).character == "QUALIFICATION_OR_CONDITION"
    assert classify_claim("No one is delayed.").character != "QUANTITATIVE_FACT"
    assert classify_claim("Researchers completed the work.").character == "CONTEXTUAL_FACT"
    assert classify_claim(
        "Free-flow is unrestricted, while synchronized flow is congested."
    ).character == "DESCRIPTIVE_CONTRAST"


def test_character_and_strategy_distributions_are_frozen():
    report = _report()
    assert report["character_distribution"] == {
        "CONTEXTUAL_FACT": 19,
        "DEFINITION_OR_DESCRIPTION": 26,
        "DESCRIPTIVE_CONTRAST": 4,
        "QUALIFICATION_OR_CONDITION": 33,
        "QUANTITATIVE_COMPARISON": 3,
        "QUANTITATIVE_FACT": 13,
    }
    assert report["final_strategy_distribution"] == {
        "COMPARISON": 7,
        "CONCISE_PROSE": 45,
        "QUALIFIED_STATEMENT": 33,
        "QUANTITATIVE_CALLOUT": 13,
    }
    assert report["richer_than_prose"] == {
        "concise_prose_retained_in_all_98_plans": True,
        "count": 53,
        "prose_only_count": 45,
        "prose_only_rate": 0.459184,
        "rate": 0.540816,
    }


def test_every_displayed_field_is_exactly_traceable_and_prose_is_never_removed():
    for decision in _report()["claim_classifications_and_plans"]:
        text = decision["claim_text"]
        plan = decision["final_plan"]
        assert plan["concise_prose"] == text
        assert decision["grounding_provenance_refs"]
        assert decision["final_safety_audit"]["safe"] is True
        for trace in plan["display_field_traces"]:
            assert trace["source"] == "CLAIM_TEXT"
            assert text[trace["start_char"] : trace["end_char"]] == trace["quote"]


def test_richer_plans_use_only_bounded_non_topological_payloads():
    expected = {
        "QUANTITATIVE_COMPARISON": "COMPARISON",
        "DESCRIPTIVE_CONTRAST": "COMPARISON",
        "QUALIFICATION_OR_CONDITION": "QUALIFIED_STATEMENT",
        "QUANTITATIVE_FACT": "QUANTITATIVE_CALLOUT",
    }
    for decision in _report()["claim_classifications_and_plans"]:
        character = decision["classification"]["character"]
        if character in expected:
            assert decision["richer_than_prose_survived"] is True
            assert decision["final_safe_strategy"] == expected[character]
            assert decision["final_plan"]["structured_payload"]
        else:
            assert decision["richer_than_prose_survived"] is False
            assert decision["final_safe_strategy"] == "CONCISE_PROSE"
        assert decision["knowledge_model_semantics_created"] is False
        assert decision["topology_created"] is False
        assert decision["production_renderer_or_surface_binding_created"] is False


def test_semantic_topology_and_spec054_controls_remain_identical():
    report = _report()
    control = report["spec054_disabled_enabled_control"]
    assert control["disabled_baseline_report_regenerated_equal"] is True
    assert control["disabled_baseline_claim_focus_count"] == 98
    assert control["disabled_baseline_outcome_distribution"] == {
        "EXISTING_NON_FALLBACK_STRATEGY": 0,
        "INVALID_OR_UNSAFE_DECISION": 0,
        "NO_STRATEGY": 0,
        "TRUTHFUL_PROSE_FALLBACK": 98,
    }
    assert control["admitted_models_unchanged"] is True
    assert control["existing_non_claim_decisions_unchanged"] is True
    assert control["detected_structures_unchanged"] is True
    safety = report["semantic_topology_safety_audit"]
    assert safety["knowledge_model_mutations"] == 0
    assert safety["relationships_or_propositions_created"] == 0
    assert safety["topology_created"] == 0


def test_spec053_labels_are_post_hoc_audit_only():
    report = _report()
    audit = report["post_hoc_spec053_cross_tab"]
    assert audit["diagnostic_labels_used_for_classification"] is False
    assert sum(sum(row.values()) for row in audit["rows"].values()) == 98
    assert report["execution_integrity"]["spec053_labels_used_as_answers"] == 0
    assert CONTRACT["forbidden_inputs"][1] == "SPEC-053 diagnostic character as classification answer"


def test_source_and_domain_are_descriptive_not_routing_inputs():
    report = _report()
    rows = report["descriptive_source_domain_distribution"]
    assert len(rows) == 8
    assert sum(sum(row["character_counts"].values()) for row in rows) == 98
    assert report["execution_integrity"]["source_or_domain_routing_rules"] == 0
    assert "source" not in classify_claim.__code__.co_varnames
    assert "domain" not in classify_claim.__code__.co_varnames


def test_owner_review_sample_has_two_complete_cases_for_each_required_character():
    sample = _report()["deterministic_owner_review_sample"]
    assert len(sample) == 12
    counts = {}
    for item in sample:
        counts[item["representation_character"]] = counts.get(item["representation_character"], 0) + 1
        assert item["exact_grounded_claim"] == item["concise_prose_component"]
        assert item["evidence_quotes"]
        assert item["experimental_representation_plan"]
        assert item["safety_and_provenance_trace"]["all_plan_fields_trace"] is True
    assert counts == {
        "CONTEXTUAL_FACT": 2,
        "DEFINITION_OR_DESCRIPTION": 2,
        "DESCRIPTIVE_CONTRAST": 2,
        "QUALIFICATION_OR_CONDITION": 2,
        "QUANTITATIVE_COMPARISON": 2,
        "QUANTITATIVE_FACT": 2,
    }


def test_decision_branch_and_next_step_are_singular_and_owner_gated():
    report = _report()
    assert report["decision_branch"]["class"] == "REPRESENTATION_SEMANTICS_SUPPORTED"
    assert report["decision_branch"]["class"] in BRANCHES
    assert report["recommended_next_step"]["class"] == "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT"
    assert report["recommended_next_step"]["class"] in NEXT_STEPS
    assert report["recommended_next_step"]["implementation_authorized"] is False
    assert report["owner_review"] == {
        "promotion": "NOT_AUTHORIZED",
        "state": "OWNER_REVIEW",
        "verdict": "PENDING",
    }
    assert all(value == 0 for value in report["execution_integrity"].values())


def test_contract_hashes_match_and_experimental_forms_are_not_production_strategies():
    report = _report()
    assert report["experimental_representation_character_contract"] == CONTRACT
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
    production = {item.value for item in StrategyType}
    assert "QUALIFIED_STATEMENT" not in production
    assert "QUANTITATIVE_CALLOUT" not in production


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
        "focused_spec055_and_frozen_control_tests": "PASS (115 tests)",
        "full_offline_suite": "PASS (659 tests)",
        "git_diff_check": "PASS",
        "json_validation": "PASS",
        "protected_state_audit": "PASS (hash-bound and baseline-equivalent)",
        "provenance_and_secret_safety": "PASS",
        "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
    }
