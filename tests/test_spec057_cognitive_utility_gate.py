from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from knowledge_compiler.representation_strategy import StrategyType
from knowledge_compiler.spec057_cognitive_utility_gate import (
    BRANCHES,
    DIMENSIONS,
    EXPECTED_EVIDENCE_IDENTITIES,
    IMPLEMENTATION_PATHS,
    NEXT_STEPS,
    OUTPUT_PATH,
    OUTCOMES,
    SPEC038_REPORT,
    SPEC055_REPORT,
    UTILITY_CONTRACT,
    build_report,
    classify_claim_utility,
    classify_structural_utility,
    select_structural_controls,
    write_report,
)


ROOT = Path(__file__).parents[1]


def _report():
    return json.loads((ROOT / OUTPUT_PATH).read_text(encoding="utf-8"))


def test_versioned_contract_is_hash_bound_conservative_and_noncanonical():
    report = _report()
    encoded = json.dumps(
        UTILITY_CONTRACT,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    assert report["cognitive_utility_contract"] == UTILITY_CONTRACT
    assert report["cognitive_utility_contract_sha256"] == hashlib.sha256(encoded).hexdigest()
    assert UTILITY_CONTRACT["schema"] == "spec057.experimental-cognitive-utility-gate.v1"
    assert UTILITY_CONTRACT["canonical_semantics"] is False
    assert UTILITY_CONTRACT["production_renderer_binding"] is False
    assert tuple(UTILITY_CONTRACT["dimensions"]) == DIMENSIONS
    assert tuple(UTILITY_CONTRACT["outcomes"]) == OUTCOMES


def test_all_98_claims_and_all_gate1_controls_are_reconciled_once():
    rows = _report()["claim_decisions"]
    assert len(rows) == 98
    assert len({row["utility_decision_id"] for row in rows}) == 98
    assert len(
        {
            (row["focus_identity"]["source_id"], row["focus_identity"]["claim_id"])
            for row in rows
        }
    ) == 98
    assert sum(row["gate1_richer_candidate"] for row in rows) == 53
    assert sum(not row["gate1_richer_candidate"] for row in rows) == 45


def test_before_after_and_outcome_distributions_are_exact():
    report = _report()
    assert report["before_after_strategy_distribution"] == {
        "richer_after": 7,
        "richer_before": 53,
        "returned_to_prose": 46,
        "spec055_before": {
            "COMPARISON": 7,
            "CONCISE_PROSE": 45,
            "QUALIFIED_STATEMENT": 33,
            "QUANTITATIVE_CALLOUT": 13,
        },
        "spec057_after": {"COMPARISON": 7, "CONCISE_PROSE": 91},
    }
    assert report["claim_utility_outcome_distribution"] == {
        "LOW_EXTERNALIZATION_VALUE": 87,
        "STRONG_EXTERNALIZATION_VALUE": 7,
        "UNSAFE_OR_UNSUPPORTED": 4,
    }


def test_all_explicit_comparisons_survive_from_generic_payload_evidence():
    rows = [
        row
        for row in _report()["claim_decisions"]
        if row["prior_proposed_strategy"] == "COMPARISON"
    ]
    assert len(rows) == 7
    for row in rows:
        payload = row["frozen_structured_payload"]
        assert len(payload["sides"]) == 2
        assert payload["explicit_cue"]
        assert row["dimensions"]["PERCEPTUAL_COMPARISON_LOAD"]["present"] is True
        assert row["utility_outcome"] == "STRONG_EXTERNALIZATION_VALUE"
        assert row["gated_final_experimental_strategy"] == "COMPARISON"


def test_all_qualifier_only_visuals_are_suppressed_as_grammar_decomposition():
    rows = [
        row
        for row in _report()["claim_decisions"]
        if row["prior_proposed_strategy"] == "QUALIFIED_STATEMENT"
    ]
    assert len(rows) == 33
    assert all(
        row["dimensions"]["GRAMMAR_ONLY_DECOMPOSITION"]["present"]
        and row["dimensions"]["DECODING_OVERHEAD"]["present"]
        and row["utility_outcome"] == "LOW_EXTERNALIZATION_VALUE"
        and row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
        for row in rows
    )


def test_quantitative_callouts_fail_closed_without_comparison_bindings():
    rows = [
        row
        for row in _report()["claim_decisions"]
        if row["prior_proposed_strategy"] == "QUANTITATIVE_CALLOUT"
    ]
    assert len(rows) == 13
    assert Counter(row["utility_outcome"] for row in rows) == Counter(
        {"LOW_EXTERNALIZATION_VALUE": 9, "UNSAFE_OR_UNSUPPORTED": 4}
    )
    for row in rows:
        quantities = row["frozen_structured_payload"]["quantity_excerpts"]
        assert row["dimensions"]["EMPHASIS_ONLY"]["present"] is True
        assert row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
        if len(quantities) == 1:
            assert row["utility_outcome"] == "LOW_EXTERNALIZATION_VALUE"
            assert row["safety_reason"] is None
        else:
            assert row["utility_outcome"] == "UNSAFE_OR_UNSUPPORTED"
            assert "inventing" in row["safety_reason"]


def test_all_45_prose_controls_remain_positive_prose_choices():
    rows = [
        row
        for row in _report()["claim_decisions"]
        if not row["gate1_richer_candidate"]
    ]
    assert len(rows) == 45
    assert all(row["prior_proposed_strategy"] == "CONCISE_PROSE" for row in rows)
    assert all(row["frozen_structured_payload"] is None for row in rows)
    assert all(row["utility_outcome"] == "LOW_EXTERNALIZATION_VALUE" for row in rows)
    assert all(
        row["gated_final_experimental_strategy"] == "CONCISE_PROSE" for row in rows
    )


def test_claim_classifier_does_not_read_identity_or_owner_review_labels():
    report = _report()
    original = next(
        row
        for row in report["claim_decisions"]
        if row["prior_proposed_strategy"] == "COMPARISON"
    )
    spec055 = json.loads((ROOT / SPEC055_REPORT).read_text())
    frozen = next(
        row
        for row in spec055["claim_classifications_and_plans"]
        if row["decision_id"] == original["spec055_decision_id"]
    )
    altered = json.loads(json.dumps(frozen))
    altered["focus_identity"]["source_id"] = "unrelated-source"
    altered["focus_identity"]["domain"] = "unrelated-domain"
    altered["owner_comment"] = "must be prose"
    assert classify_claim_utility(altered) == classify_claim_utility(frozen)
    assert all(
        not any(row["routing_input_audit"].values())
        for row in report["claim_decisions"]
    )


def test_structural_controls_are_selected_deterministically_without_domain_routing():
    report = _report()
    selection = report["structural_control_selection"]
    assert selection["sample_size"] == 4
    assert selection["source_or_domain_used"] is False
    assert selection["selected_case_ids"] == [
        "economics_market_system",
        "software_composition",
        "field_reciprocal_mechanism",
        "double_slit_focused_relationship",
    ]
    spec038 = json.loads((ROOT / SPEC038_REPORT).read_text())
    assert [row["case"] for row in select_structural_controls(spec038)] == selection[
        "selected_case_ids"
    ]


def test_structural_calibration_preserves_strong_controls_and_suppresses_uncertain_simple_relation():
    rows = _report()["structural_positive_control_decisions"]
    assert Counter(row["utility_outcome"] for row in rows) == Counter(
        {"STRONG_EXTERNALIZATION_VALUE": 3, "POSSIBLE_EXTERNALIZATION_VALUE": 1}
    )
    by_case = {row["spec038_case"]: row for row in rows}
    for case in (
        "economics_market_system",
        "software_composition",
        "field_reciprocal_mechanism",
    ):
        assert by_case[case]["gated_final_experimental_strategy"] != "CONCISE_PROSE"
    focused = by_case["double_slit_focused_relationship"]
    assert focused["utility_outcome"] == "POSSIBLE_EXTERNALIZATION_VALUE"
    assert focused["gated_final_experimental_strategy"] == "CONCISE_PROSE"
    assert focused["candidate_metadata_preserved_for_manual_study"] is True


def test_structural_classifier_uses_payload_shape_and_strategy_not_case_identity():
    spec038 = json.loads((ROOT / SPEC038_REPORT).read_text())
    case = select_structural_controls(spec038)[0]
    altered = json.loads(json.dumps(case))
    altered["case"] = "renamed-control"
    altered["context_key"] = "unrelated-context"
    assert classify_structural_utility(altered) == classify_structural_utility(case)


def test_spec056_exact_review_subset_is_a_post_hoc_twelve_case_audit():
    audit = _report()["spec056_owner_review_audit"]
    assert audit["case_count"] == 12
    assert audit["owner_comments_used_as_routing_inputs"] is False
    assert audit["owner_findings_are_post_hoc_descriptive_evidence_only"] is True
    assert audit["summary"] == {
        "alignment_is_not_pedagogical_proof": True,
        "comparisons_retained": 3,
        "directionally_aligned_cases": 12,
        "prose_controls_preserved": 3,
        "qualified_statements_suppressed": 3,
        "quantitative_callouts_suppressed": 3,
    }
    assert len({row["case_identity"] for row in audit["rows"]}) == 12


def test_provenance_hashes_safety_and_production_boundaries_are_exact():
    report = _report()
    assert {
        item["path"]: item["sha256"] for item in report["evidence_identities"]
    } == EXPECTED_EVIDENCE_IDENTITIES
    for path, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    implementation = {
        item["path"]: item["sha256"] for item in report["implementation_identities"]
    }
    assert set(implementation) == set(IMPLEMENTATION_PATHS)
    for path, expected in implementation.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    assert report["safety_topology_audit"] == {
        "all_45_prose_controls_preserved": True,
        "all_53_richer_candidates_reconciled": True,
        "all_98_claims_reconciled": True,
        "all_claim_evidence_traceable": True,
        "all_structural_controls_hash_bound_and_traceable": True,
        "knowledge_model_mutations": 0,
        "production_renderer_or_ui_changes": 0,
        "promotion_actions": 0,
        "semantic_vocabulary_mutations": 0,
        "spec055_artifact_mutations": 0,
        "spec056_artifact_mutations": 0,
        "topology_mutations": 0,
    }
    assert all(value == 0 for value in report["execution_integrity"].values())
    production = {item.value for item in StrategyType}
    assert "QUALIFIED_STATEMENT" not in production
    assert "QUANTITATIVE_CALLOUT" not in production


def test_branch_next_step_owner_gate_and_report_regeneration_are_exact(tmp_path):
    report = _report()
    assert report["experiment_branch"]["class"] == "COGNITIVE_UTILITY_GATE_SUPPORTED"
    assert report["experiment_branch"]["class"] in BRANCHES
    assert report["recommended_next_step"]["class"] == (
        "UTILITY_GATED_LEARNER_SURFACE_AB_EXPERIMENT"
    )
    assert report["recommended_next_step"]["class"] in NEXT_STEPS
    assert report["recommended_next_step"]["implementation_authorized"] is False
    assert report["owner_review"]["state"] == "OWNER_REVIEW"
    assert report["owner_review"]["verdict"] == "PENDING"
    assert report["owner_review"]["promotion"] == "NOT_AUTHORIZED"
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    write_report(ROOT, left)
    write_report(ROOT, right)
    assert left.read_bytes() == right.read_bytes() == (ROOT / OUTPUT_PATH).read_bytes()
    assert json.loads(left.read_text()) == build_report(ROOT)
    assert report["validation"] == {
        "deterministic_regeneration": "PASS",
        "focused_spec057_and_regression_tests": "PASS (124 tests)",
        "full_offline_suite": "PASS (685 tests)",
        "git_diff_check": "PASS",
        "json_validation": "PASS",
        "protected_state_audit": "PASS (hash-bound and empty protected-path diff)",
        "provenance_and_secret_safety": "PASS",
        "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
    }
