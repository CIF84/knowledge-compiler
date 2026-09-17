from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from knowledge_compiler.representation_strategy import StrategyType
from knowledge_compiler.spec057_cognitive_utility_gate import classify_structural_utility
from knowledge_compiler.spec058_utility_gated_surface_evaluation import (
    BROWSER_VERIFICATION,
    EXPECTED_EVIDENCE_IDENTITIES,
    GROUPS,
    OUTPUT_DIR,
    OWNER_COMMAND,
    SPEC038_REPORT,
    SPEC057_REPORT,
    build_cases_packet,
    generate,
    select_cases,
)


ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / OUTPUT_DIR


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _cases():
    return _load(OUTPUT / "cases.json")["cases"]


def test_sample_has_exactly_sixteen_unique_cases_and_four_per_group():
    cases = _cases()
    assert len(cases) == 16
    assert len({case["case_identity"] for case in cases}) == 16
    assert [case["review_index"] for case in cases] == list(range(1, 17))
    assert Counter(case["group"] for case in cases) == Counter(
        {group: 4 for group in GROUPS}
    )


def test_retained_claim_sample_maximizes_source_diversity_deterministically():
    rows = [case for case in _cases() if case["group"] == GROUPS[0]]
    assert [
        (row["source_id"], row["claim_id"])
        for row in rows
    ] == [
        ("crs-legislative-process-r42843-17", "claim-house-tools"),
        ("epa-ecological-processes-2026", "claim-6"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c1"),
        ("noaa-nesdis-jet-stream-2025", "c36"),
    ]
    assert len({row["source_id"] for row in rows}) == 4
    assert all(row["utility_outcome"] == "STRONG_EXTERNALIZATION_VALUE" for row in rows)
    assert all(row["gate_decision"] == "COMPARISON" for row in rows)


def test_structural_sample_uses_three_frozen_strong_controls_and_strongest_remaining_case():
    rows = [case for case in _cases() if case["group"] == GROUPS[1]]
    assert [row["claim_id"] for row in rows] == [
        "economics_market_system",
        "software_composition",
        "field_reciprocal_mechanism",
        "history_printing_dependency",
    ]
    assert [row["utility_decision_origin"] for row in rows] == [
        "SPEC057_FROZEN_DECISION",
        "SPEC057_FROZEN_DECISION",
        "SPEC057_FROZEN_DECISION",
        "SPEC057_CONTRACT_APPLIED_TO_FROZEN_SPEC038_ACCEPTED_CONTROL",
    ]
    assert all(row["utility_outcome"] == "STRONG_EXTERNALIZATION_VALUE" for row in rows)
    assert all(row["gate_decision"] != "CONCISE_PROSE" for row in rows)


def test_suppressed_group_contains_two_qualifiers_and_two_quantitative_candidates():
    rows = [case for case in _cases() if case["group"] == GROUPS[2]]
    assert [(row["source_id"], row["claim_id"], row["prior_strategy"]) for row in rows] == [
        ("crs-legislative-process-r42843-17", "claim-amendments", "QUALIFIED_STATEMENT"),
        ("doe-iron-platinum-atomic-structure-2017", "c14", "QUALIFIED_STATEMENT"),
        ("doe-iron-platinum-atomic-structure-2017", "c1", "QUANTITATIVE_CALLOUT"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c2", "QUANTITATIVE_CALLOUT"),
    ]
    assert all(row["gate_decision"] == "CONCISE_PROSE" for row in rows)
    assert all(row["treatment_a"]["selected_by_gate"] for row in rows)
    assert all(not row["treatment_b"]["selected_by_gate"] for row in rows)


def test_restraint_group_has_two_original_prose_controls_focused_relation_and_extra_low_case():
    rows = [case for case in _cases() if case["group"] == GROUPS[3]]
    assert [(row["claim_id"], row["utility_outcome"], row["prior_strategy"]) for row in rows] == [
        ("claim-agenda-authority", "LOW_EXTERNALIZATION_VALUE", "CONCISE_PROSE"),
        ("c11", "LOW_EXTERNALIZATION_VALUE", "CONCISE_PROSE"),
        (
            "double_slit_focused_relationship",
            "POSSIBLE_EXTERNALIZATION_VALUE",
            "FOCUSED_RELATIONSHIP",
        ),
        (
            "claim-committee-initiation",
            "LOW_EXTERNALIZATION_VALUE",
            "QUALIFIED_STATEMENT",
        ),
    ]
    assert all(row["gate_decision"] == "CONCISE_PROSE" for row in rows)


def test_every_claim_case_is_byte_equivalent_to_its_frozen_spec057_decision():
    report = _load(ROOT / SPEC057_REPORT)
    index = {
        (row["focus_identity"]["source_id"], row["focus_identity"]["claim_id"]): row
        for row in report["claim_decisions"]
    }
    for case in [row for row in _cases() if row["case_kind"] == "CLAIM"]:
        frozen = index[(case["source_id"], case["claim_id"])]
        assert case["prose"] == frozen["claim_text"]
        assert case["structured_payload"] == frozen["frozen_structured_payload"]
        assert case["display_field_traces"] == frozen["frozen_display_field_traces"]
        assert case["provenance"] == frozen["grounding_provenance_refs"]
        assert case["utility_outcome"] == frozen["utility_outcome"]
        assert case["gate_decision"] == frozen["gated_final_experimental_strategy"]


def test_structural_cases_reuse_exact_spec038_nodes_relationships_coordinates_and_paths():
    spec038 = _load(ROOT / SPEC038_REPORT)
    index = {row["case"]: row for row in spec038["fixed_evaluation_cases"]}
    for case in [row for row in _cases() if row["case_kind"] == "STRUCTURAL"]:
        frozen = index[case["claim_id"]]
        assert case["structured_payload"]["nodes"] == frozen["nodes_rendered"]
        assert case["structured_payload"]["relationships"] == frozen["relationships_rendered"]
        assert case["structured_payload"]["spatial_grammar"] == frozen["spatial_grammar"]
        assert all("x" in row and "y" in row for row in case["structured_payload"]["nodes"])
        assert all("path" in row for row in case["structured_payload"]["relationships"])
    history = index["history_printing_dependency"]
    assert classify_structural_utility(history)["utility_outcome"] == (
        "STRONG_EXTERNALIZATION_VALUE"
    )


def test_ab_semantics_and_system_state_labels_are_neutral_and_exact():
    for case in _cases():
        a = case["treatment_a"]
        b = case["treatment_b"]
        assert a["mode"] == "A" and b["mode"] == "B"
        assert all(word not in (a["label"] + b["label"]).casefold() for word in ("better", "correct", "recommended"))
        if case["gate_decision"] == "CONCISE_PROSE":
            assert case["selected_mode"] == "A"
            assert a["selected_by_gate"] is True
        else:
            assert case["selected_mode"] == "B"
            assert b["selected_by_gate"] is True


def test_prose_controls_have_no_fake_structure_and_counterfactuals_remain_disclosed():
    cases = _cases()
    pure = [
        row
        for row in cases
        if row["prior_strategy"] == "CONCISE_PROSE"
        and row["group"] == GROUPS[3]
    ]
    assert len(pure) == 2
    assert all(row["structured_payload"] is None for row in pure)
    assert all(row["treatment_b"]["strategy_dom"] == "CONCISE_PROSE" for row in pure)
    counterfactuals = [
        row
        for row in cases
        if row["gate_decision"] == "CONCISE_PROSE"
        and row["treatment_b"]["strategy_dom"] != "CONCISE_PROSE"
    ]
    assert len(counterfactuals) == 6
    assert all("SUPPRESSED BY GATE" in row["treatment_b"]["label"] for row in counterfactuals)


def test_treatment_and_payload_identities_recompute_exactly():
    report = _load(OUTPUT / "report.json")
    cases = {row["case_identity"]: row for row in _cases()}
    for identity in report["case_treatment_identities"]:
        case = cases[identity["case_identity"]]
        for side, key in (("treatment_a", "a_identity_sha256"), ("treatment_b", "b_identity_sha256")):
            treatment = {k: v for k, v in case[side].items() if k != "identity_sha256"}
            assert _stable(treatment) == identity[key] == case[side]["identity_sha256"]
        assert hashlib.sha256(case["prose"].encode()).hexdigest() == identity["prose_sha256"]
        assert _stable(case["structured_payload"]) == identity[
            "representation_payload_sha256"
        ]


def _stable(value):
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_provenance_truthfulness_and_zero_mutation_audits_pass():
    report = _load(OUTPUT / "report.json")
    audit = report["provenance_truthfulness_audit"]
    assert audit == {
        "all_16_cases_frozen_and_traceable": True,
        "invented_display_values": 0,
        "semantic_mutations": 0,
        "spec057_gate_decision_mutations": 0,
        "suppressed_candidate_polish_or_repair": 0,
        "topology_mutations": 0,
    }
    assert all(value == 0 for value in report["protected_state"].values())
    assert all(value == 0 for value in report["execution_integrity"].values())


def test_artifact_preserves_four_surfaces_and_machine_human_evidence_boundary():
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    script = (OUTPUT / "app.js").read_text(encoding="utf-8")
    for marker in (
        "MY MAP",
        "WHAT DOES THIS MEAN?",
        'aria-label="Inspect selected representation detail"',
        "EXPLORE NEXT",
        'data-gate-decisions="FROZEN_SPEC057"',
        'data-production-promotion="false"',
        'data-human-verdict="PENDING"',
    ):
        assert marker in html
    for invariant in (
        "local_interaction_preserves_case",
        "local_interaction_preserves_treatment",
        "local_interaction_preserves_territory",
        "local_interaction_preserves_semantic_owner",
    ):
        assert invariant in script
    boundary = _load(OUTPUT / "report.json")["machine_evidence"]
    assert "pedagogical superiority" in boundary["must_not_establish"]
    assert "product promotion" in boundary["must_not_establish"]


def test_browser_gate_passes_desktop_narrow_interaction_and_console_checks():
    record = _load(OUTPUT / "browser-verification.json")
    assert record == BROWSER_VERIFICATION
    assert record["status"] == "PASS"
    assert record["desktop"]["all_16_cases_loaded"] is True
    assert record["desktop"]["all_case_machine_checks_passed"] is True
    assert record["desktop"]["horizontal_overflow"] is False
    assert record["narrow"]["viewport"] == "390x844"
    assert record["narrow"]["horizontal_overflow"] is False
    assert record["narrow"]["all_case_machine_checks_passed"] is True
    assert all(value == "PASS" for value in record["interaction"].values())
    assert record["console"] == {"errors": [], "result": "PASS", "warnings": []}


def test_frozen_evidence_artifact_and_implementation_hashes_match():
    report = _load(OUTPUT / "report.json")
    evidence = {row["path"]: row["sha256"] for row in report["evidence_identities"]}
    assert evidence == EXPECTED_EVIDENCE_IDENTITIES
    for path, expected in evidence.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    for key, base in (("artifact_identities", OUTPUT), ("implementation_identities", ROOT)):
        for row in report[key]:
            assert hashlib.sha256((base / row["path"]).read_bytes()).hexdigest() == row[
                "sha256"
            ]
    production = {item.value for item in StrategyType}
    assert "QUALIFIED_STATEMENT" not in production
    assert "QUANTITATIVE_CALLOUT" not in production


def test_case_selection_and_artifact_regeneration_are_byte_deterministic(tmp_path):
    spec038 = _load(ROOT / SPEC038_REPORT)
    spec057 = _load(ROOT / SPEC057_REPORT)
    assert select_cases(spec038, spec057) == build_cases_packet(spec038, spec057)[
        "cases"
    ]
    generated = tmp_path / "generated"
    generate(ROOT, generated)
    for name in (
        "index.html",
        "styles.css",
        "app.js",
        "cases.json",
        "owner-review-rubric.json",
        "browser-verification.json",
        "report.json",
    ):
        assert (generated / name).read_bytes() == (OUTPUT / name).read_bytes()


def test_owner_review_remains_pending_and_final_validation_is_recorded():
    report = _load(OUTPUT / "report.json")
    assert report["owner_review"] == {
        "command": OWNER_COMMAND,
        "promotion": "NOT_AUTHORIZED",
        "rubric": "owner-review-rubric.json",
        "state": "OWNER_REVIEW",
        "url": "http://127.0.0.1:8058/",
        "verdict": "PENDING",
    }
    assert report["validation"] == {
        "browser_machine_gate": "PASS",
        "deterministic_regeneration": "PASS",
        "focused_spec058_and_regression_tests": "PASS (128 tests)",
        "full_offline_suite": "PASS (701 tests)",
        "git_diff_check": "PASS",
        "json_validation": "PASS",
        "protected_state_audit": "PASS (hash-bound and empty protected-path diff)",
        "provenance_and_secret_safety": "PASS",
        "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
    }
