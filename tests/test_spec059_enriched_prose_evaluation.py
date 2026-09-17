from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from knowledge_compiler.models import ValidationError
from knowledge_compiler.spec059_enriched_prose_evaluation import (
    BROWSER_VERIFICATION,
    EMPHASIS_ROLES,
    EXPECTED_EVIDENCE_IDENTITIES,
    GROUPS,
    OUTPUT_DIR,
    OWNER_COMMAND,
    SPEC057_REPORT,
    SPEC058_CASES,
    _emphasis_for,
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


def _stable(value):
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_sample_has_exactly_eighteen_unique_cases_in_required_distribution():
    cases = _cases()
    assert len(cases) == 18
    assert len({case["case_identity"] for case in cases}) == 18
    assert [case["review_index"] for case in cases] == list(range(1, 19))
    assert Counter(case["group"] for case in cases) == Counter(
        {GROUPS[0]: 6, GROUPS[1]: 4, GROUPS[2]: 4, GROUPS[3]: 4}
    )


def test_quantitative_selection_maximizes_source_diversity_and_includes_required_examples():
    rows = [case for case in _cases() if case["group"] == GROUPS[0]]
    assert [(row["source_id"], row["claim_id"]) for row in rows] == [
        ("doe-iron-platinum-atomic-structure-2017", "c1"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c2"),
        ("nasa-solar-system-formation-2026", "c8"),
        ("nist-measurement-uncertainty-2025", "c3"),
        ("noaa-nesdis-jet-stream-2025", "c32"),
        ("usgs-divergent-plate-boundaries-1996", "c14"),
    ]
    assert len({row["source_id"] for row in rows}) == 6
    spans = {
        span["text"]
        for row in rows
        for span in row["treatment_b"]["emphasis_spans"]
    }
    assert {"more than 23,000 atoms", "22 picometer", "45 percent"} <= spans


def test_comparison_selection_uses_four_diverse_frozen_survivors():
    rows = [case for case in _cases() if case["group"] == GROUPS[1]]
    assert [(row["source_id"], row["claim_id"]) for row in rows] == [
        ("crs-legislative-process-r42843-17", "claim-house-tools"),
        ("epa-ecological-processes-2026", "claim-6"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c1"),
        ("noaa-nesdis-jet-stream-2025", "c36"),
    ]
    assert all(row["gate_decision"] == "COMPARISON" for row in rows)
    assert all(row["utility_outcome"] == "STRONG_EXTERNALIZATION_VALUE" for row in rows)
    roles = Counter(
        span["role"]
        for row in rows
        for span in row["treatment_b"]["emphasis_spans"]
    )
    assert roles == Counter({"COMPARISON_OPERAND": 8, "CONTRAST": 3})


def test_qualification_selection_uses_four_diverse_suppressed_candidates():
    rows = [case for case in _cases() if case["group"] == GROUPS[2]]
    assert [(row["source_id"], row["claim_id"]) for row in rows] == [
        ("crs-legislative-process-r42843-17", "claim-amendments"),
        ("doe-iron-platinum-atomic-structure-2017", "c14"),
        ("epa-ecological-processes-2026", "claim-3"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c10"),
    ]
    assert all(row["gate_decision"] == "CONCISE_PROSE" for row in rows)
    assert all(
        [span["role"] for span in row["treatment_b"]["emphasis_spans"]]
        == ["CONDITION_OR_SCOPE"]
        for row in rows
    )


def test_low_complexity_group_reuses_exact_spec058_controls_and_has_no_emphasis():
    rows = [case for case in _cases() if case["group"] == GROUPS[3]]
    assert [row["claim_id"] for row in rows] == [
        "claim-agenda-authority",
        "c11",
        "double_slit_focused_relationship",
        "claim-committee-initiation",
    ]
    assert all(not row["treatment_b"]["emphasis_spans"] for row in rows)
    assert all(row["treatment_a"]["text"] == row["treatment_b"]["text"] for row in rows)


def test_a_and_b_preserve_exact_text_order_punctuation_and_meaning():
    spec057 = _load(ROOT / SPEC057_REPORT)
    frozen = {
        (row["focus_identity"]["source_id"], row["focus_identity"]["claim_id"]): row
        for row in spec057["claim_decisions"]
    }
    spec058 = _load(ROOT / SPEC058_CASES)
    focused = next(
        row
        for row in spec058["cases"]
        if row["claim_id"] == "double_slit_focused_relationship"
    )
    for case in _cases():
        expected = (
            focused["prose"]
            if case["case_kind"] == "STRUCTURAL_CONTROL"
            else frozen[(case["source_id"], case["claim_id"])]["claim_text"]
        )
        assert case["trusted_prose"] == expected
        assert case["treatment_a"]["text"] == expected
        assert case["treatment_b"]["text"] == expected
        assert case["truthfulness_audit"]["prose_rewrite"] is False


def test_every_emphasis_span_is_exact_nonoverlapping_and_role_bounded():
    for case in _cases():
        text = case["trusted_prose"]
        spans = case["treatment_b"]["emphasis_spans"]
        assert spans == sorted(
            spans, key=lambda row: (row["start_char"], row["end_char"], row["role"])
        )
        for index, span in enumerate(spans):
            assert span["role"] in EMPHASIS_ROLES
            assert span["trace_source"] == "FROZEN_STRUCTURED_PAYLOAD"
            assert text[span["start_char"] : span["end_char"]] == span["text"]
            assert text.count(span["text"]) == 1
            if index:
                assert spans[index - 1]["end_char"] <= span["start_char"]


def test_overlapping_comparison_cue_fails_closed_without_rewriting_operands():
    row = next(
        case
        for case in _cases()
        if case["source_id"] == "epa-ecological-processes-2026"
        and case["claim_id"] == "claim-6"
    )
    spans = row["treatment_b"]["emphasis_spans"]
    assert [span["role"] for span in spans] == [
        "COMPARISON_OPERAND",
        "COMPARISON_OPERAND",
    ]
    assert [span["text"] for span in spans] == [
        "Indicators for respiration, nutrient cycling, and decomposition have been developed at watershed scales",
        "not at the national scale",
    ]


def test_non_unique_fragment_is_rejected_instead_of_guessed():
    report = _load(ROOT / SPEC057_REPORT)
    row = next(
        item
        for item in report["claim_decisions"]
        if item["prior_proposed_strategy"] == "QUANTITATIVE_CALLOUT"
    )
    bad = json.loads(json.dumps(row))
    bad["claim_text"] = "one one"
    bad["frozen_structured_payload"] = {"quantity_excerpts": ["one"]}
    with pytest.raises(ValidationError, match="exactly once"):
        _emphasis_for(bad, GROUPS[0])


def test_c_uses_exact_frozen_reference_or_explicit_unavailable_state():
    spec057 = _load(ROOT / SPEC057_REPORT)
    frozen = {
        (row["focus_identity"]["source_id"], row["focus_identity"]["claim_id"]): row
        for row in spec057["claim_decisions"]
    }
    available = unavailable = 0
    for case in _cases():
        c = case["treatment_c"]
        if c["availability"] == "NO_FROZEN_RICHER_REFERENCE":
            unavailable += 1
            assert c["payload"] is None and c["strategy_dom"] is None
        else:
            available += 1
            if case["case_kind"] == "CLAIM":
                row = frozen[(case["source_id"], case["claim_id"])]
                assert c["payload"] == row["frozen_structured_payload"]
                assert c["strategy_dom"] == row["prior_proposed_strategy"]
    assert (available, unavailable) == (16, 2)


def test_treatment_identities_and_report_distributions_recompute_exactly():
    report = _load(OUTPUT / "report.json")
    cases = {case["case_identity"]: case for case in _cases()}
    for record in report["treatment_identities"]:
        case = cases[record["case_identity"]]
        for side, key in (
            ("treatment_a", "a_identity_sha256"),
            ("treatment_b", "b_identity_sha256"),
            ("treatment_c", "c_identity_sha256"),
        ):
            value = {k: v for k, v in case[side].items() if k != "identity_sha256"}
            assert _stable(value) == case[side]["identity_sha256"] == record[key]
    assert report["semantic_emphasis"]["role_distribution"] == {
        "COMPARISON_OPERAND": 8,
        "CONDITION_OR_SCOPE": 4,
        "CONTRAST": 3,
        "QUANTITY": 9,
    }
    assert report["semantic_emphasis"]["total_span_count"] == 24
    assert report["semantic_emphasis"]["no_emphasis_case_count"] == 4


def test_truthfulness_restraint_and_execution_audits_are_zero_mutation():
    report = _load(OUTPUT / "report.json")
    truth = report["provenance_truthfulness_audit"]
    assert truth["all_18_cases_frozen_and_traceable"] is True
    assert all(value == 0 for key, value in truth.items() if key != "all_18_cases_frozen_and_traceable")
    assert report["restraint_audit"] == {
        "b_detached_cards_callouts_or_diagrams": 0,
        "b_sentence_remains_dominant_in_all_cases": True,
        "default_under_uncertainty": "NO_EMPHASIS",
        "low_complexity_control_count": 4,
        "low_complexity_controls_with_emphasis": 0,
    }
    assert all(value == 0 for value in report["protected_state"].values())
    assert all(value == 0 for value in report["execution_integrity"].values())


def test_html_and_css_keep_b_as_inline_prose_not_detached_callouts():
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    css = (OUTPUT / "styles.css").read_text(encoding="utf-8")
    script = (OUTPUT / "app.js").read_text(encoding="utf-8")
    for marker in (
        "A · Plain",
        "B · Enriched",
        "C · Reference",
        'data-production-promotion="false"',
        'data-visual-grammar-selection="false"',
        'data-human-verdict="PENDING"',
    ):
        assert marker in html
    assert 'paragraph.dataset.inlineSentence="true"' in script
    assert 'const mark=el("mark"' in script
    assert ".prose-treatment mark" in css
    assert "b_inline_only:b.detached_b_nodes===0" in script


def test_browser_gate_passes_desktop_narrow_interaction_and_console_checks():
    record = _load(OUTPUT / "browser-verification.json")
    assert record == BROWSER_VERIFICATION
    assert record["status"] == "PASS"
    assert record["desktop"]["all_18_cases_loaded"] is True
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
            assert hashlib.sha256((base / row["path"]).read_bytes()).hexdigest() == row["sha256"]


def test_selection_and_artifact_regeneration_are_byte_deterministic(tmp_path):
    spec057 = _load(ROOT / SPEC057_REPORT)
    spec058 = _load(ROOT / SPEC058_CASES)
    assert select_cases(spec057, spec058) == build_cases_packet(spec057, spec058)["cases"]
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


def test_report_stops_at_owner_review_without_claiming_benefit_or_promotion():
    report = _load(OUTPUT / "report.json")
    assert report["decision_branch"] == "ENRICHED_PROSE_SAFE_FOR_OWNER_REVIEW"
    assert report["recommended_next_step"] == "OWNER_REVIEW_REQUIRED"
    assert report["evaluation_questions"]["learner_benefit_established"] == (
        "NO — OWNER REVIEW REQUIRED"
    )
    assert report["owner_review"] == {
        "command": OWNER_COMMAND,
        "promotion": "NOT_AUTHORIZED",
        "rubric": "owner-review-rubric.json",
        "state": "OWNER_REVIEW",
        "url": "http://127.0.0.1:8059/",
        "verdict": "PENDING",
    }
    assert report["zero_call_zero_extraction_statement"].startswith(
        "No provider/model call"
    )
