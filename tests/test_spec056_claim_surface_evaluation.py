from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from knowledge_compiler.representation_strategy import StrategyType
from knowledge_compiler.spec056_claim_surface_evaluation import (
    BROWSER_VERIFICATION,
    EXPECTED_SPEC055_SHA256,
    OUTPUT_DIR,
    OWNER_COMMAND,
    SPEC055_REPORT,
    STRATEGIES,
    build_cases_packet,
    generate,
    select_review_cases,
)


ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / OUTPUT_DIR


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _cases():
    return _load(OUTPUT / "cases.json")["cases"]


def test_sample_contains_exactly_three_cases_for_each_frozen_strategy():
    cases = _cases()
    assert len(cases) == 12
    assert len({item["case_identity"] for item in cases}) == 12
    assert Counter(item["strategy"] for item in cases) == Counter(
        {strategy: 3 for strategy in STRATEGIES}
    )
    assert [item["review_index"] for item in cases] == list(range(1, 13))


def test_sample_selection_is_deterministic_and_maximizes_source_diversity():
    spec055 = _load(ROOT / SPEC055_REPORT)
    selected = select_review_cases(spec055)
    packet = build_cases_packet(spec055)
    assert [item["spec055_decision_id"] for item in packet["cases"]] == [
        item["decision_id"] for item in selected
    ]
    assert [
        (item["source_id"], item["claim_id"], item["strategy"])
        for item in packet["cases"]
    ] == [
        ("crs-legislative-process-r42843-17", "claim-house-tools", "COMPARISON"),
        ("epa-ecological-processes-2026", "claim-6", "COMPARISON"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c1", "COMPARISON"),
        ("crs-legislative-process-r42843-17", "claim-amendments", "QUALIFIED_STATEMENT"),
        ("doe-iron-platinum-atomic-structure-2017", "c14", "QUALIFIED_STATEMENT"),
        ("epa-ecological-processes-2026", "claim-3", "QUALIFIED_STATEMENT"),
        ("doe-iron-platinum-atomic-structure-2017", "c1", "QUANTITATIVE_CALLOUT"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c2", "QUANTITATIVE_CALLOUT"),
        ("nasa-solar-system-formation-2026", "c8", "QUANTITATIVE_CALLOUT"),
        ("crs-legislative-process-r42843-17", "claim-agenda-authority", "CONCISE_PROSE"),
        ("doe-iron-platinum-atomic-structure-2017", "c12", "CONCISE_PROSE"),
        ("epa-ecological-processes-2026", "claim-2", "CONCISE_PROSE"),
    ]
    for strategy in STRATEGIES:
        rows = [item for item in packet["cases"] if item["strategy"] == strategy]
        assert len({item["source_id"] for item in rows}) == 3


def test_a_and_b_preserve_the_identical_trusted_prose_and_frozen_plan():
    spec055 = _load(ROOT / SPEC055_REPORT)
    frozen = {item["decision_id"]: item for item in spec055["claim_classifications_and_plans"]}
    for item in _cases():
        source = frozen[item["spec055_decision_id"]]
        assert item["prose"] == source["claim_text"]
        assert item["a_control"]["prose"] == item["prose"]
        assert item["b_experiment"]["prose"] == item["prose"]
        assert item["structured_payload"] == source["final_plan"]["structured_payload"]
        assert item["display_field_traces"] == source["final_plan"]["display_field_traces"]


def test_comparison_bindings_use_only_exact_frozen_operands_cues_and_quantities():
    for item in [row for row in _cases() if row["strategy"] == "COMPARISON"]:
        payload = item["structured_payload"]
        assert len(payload["sides"]) == 2
        expected = set(payload["sides"] + [payload["explicit_cue"]] + payload["quantity_excerpts"])
        assert set(item["display_fragments"]) == expected
        assert all(fragment in item["prose"] for fragment in expected)


def test_qualified_statement_bindings_use_only_the_exact_frozen_qualifier():
    for item in [row for row in _cases() if row["strategy"] == "QUALIFIED_STATEMENT"]:
        qualifier = item["structured_payload"]["explicit_qualifier_or_condition"]
        assert item["display_fragments"] == [qualifier]
        assert qualifier in item["prose"]


def test_quantitative_bindings_use_only_exact_frozen_quantity_excerpts():
    for item in [row for row in _cases() if row["strategy"] == "QUANTITATIVE_CALLOUT"]:
        quantities = item["structured_payload"]["quantity_excerpts"]
        assert item["display_fragments"] == sorted(set(quantities))
        assert all(quantity in item["prose"] for quantity in quantities)


def test_concise_prose_controls_do_not_manufacture_visual_structure():
    for item in [row for row in _cases() if row["strategy"] == "CONCISE_PROSE"]:
        assert item["structured_payload"] is None
        assert item["display_fragments"] == []
        assert item["a_control"] == item["b_experiment"]


def test_truthfulness_provenance_and_zero_mutation_controls_hold():
    report = _load(OUTPUT / "report.json")
    audit = report["truthfulness_and_provenance_audit"]
    assert audit == {
        "all_12_pass": True,
        "all_display_fields_trace_to_frozen_spec055": True,
        "all_provenance_attached": True,
        "invented_display_semantics": 0,
        "prose_unchanged_for_all_cases": True,
        "semantic_mutations": 0,
        "topology_mutations": 0,
    }
    assert all(item["evidence_quotes"] for item in _cases())
    for item in _cases():
        assert item["truthfulness_audit"]["prose_unchanged"] is True
        assert item["truthfulness_audit"]["all_display_fields_trace_to_frozen_plan"] is True
        assert item["truthfulness_audit"]["provenance_attached"] is True
        assert item["truthfulness_audit"]["topology_created"] is False
        assert item["truthfulness_audit"]["new_semantics_created"] is False
    assert all(value == 0 for value in report["execution_integrity"].values())


def test_review_artifact_preserves_four_surfaces_and_local_interaction_contract():
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    script = (OUTPUT / "app.js").read_text(encoding="utf-8")
    for marker in (
        "MY MAP",
        "WHAT DOES THIS MEAN?",
        'aria-label="Inspect selected representation detail"',
        "EXPLORE NEXT",
        'data-navigation-authority="FIXED_REVIEW_TERRITORY"',
        'data-semantic-state-owner="FROZEN_SPEC055"',
        'data-production-promotion="false"',
    ):
        assert marker in html
    assert "local_interaction_preserves_case" in script
    assert "local_interaction_preserves_territory" in script
    assert "reviewState.territory" in script


def test_browser_gate_passes_all_cases_responsive_checks_and_console_safety():
    record = _load(OUTPUT / "browser-verification.json")
    assert record == BROWSER_VERIFICATION
    assert record["status"] == "PASS"
    assert record["desktop"]["all_12_cases_loaded"] is True
    assert record["desktop"]["all_case_machine_checks_passed"] is True
    assert record["desktop"]["horizontal_overflow"] is False
    assert record["narrow"]["viewport"] == "390x844"
    assert record["narrow"]["horizontal_overflow"] is False
    assert record["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert all(value == "PASS" for value in record["interaction"].values())


def test_frozen_evidence_implementation_and_protected_tree_hashes_match():
    report = _load(OUTPUT / "report.json")
    assert hashlib.sha256((ROOT / SPEC055_REPORT).read_bytes()).hexdigest() == EXPECTED_SPEC055_SHA256
    for group in ("artifact_identities", "implementation_identities"):
        for item in report[group]:
            base = OUTPUT if group == "artifact_identities" else ROOT
            assert hashlib.sha256((base / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    for key in ("baseline004_tree", "spec038_tree", "diagram_canvas_assets_tree"):
        identity = report["protected_state"][key]
        path = ROOT / identity["path"]
        rows = [
            {"path": str(item.relative_to(path)), "sha256": hashlib.sha256(item.read_bytes()).hexdigest()}
            for item in sorted(path.rglob("*"))
            if item.is_file()
        ]
        encoded = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        assert hashlib.sha256(encoded).hexdigest() == identity["sha256"]
    production = {item.value for item in StrategyType}
    assert "QUALIFIED_STATEMENT" not in production
    assert "QUANTITATIVE_CALLOUT" not in production


def test_review_artifacts_regenerate_byte_identically_and_remain_owner_gated(tmp_path):
    generated = tmp_path / "generated"
    report = generate(ROOT, generated)
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
    assert report["owner_review"] == {
        "command": OWNER_COMMAND,
        "promotion": "NOT_AUTHORIZED",
        "rubric": "owner-review-rubric.json",
        "state": "OWNER_REVIEW",
        "url": "http://127.0.0.1:8056/",
        "verdict": "PENDING",
    }
    assert report["validation"] == {
        "browser_machine_gate": "PASS",
        "deterministic_regeneration": "PASS",
        "focused_spec056_and_regression_tests": "PASS (120 tests)",
        "full_offline_suite": "PASS (671 tests)",
        "git_diff_check": "PASS",
        "json_validation": "PASS",
        "protected_state_audit": "PASS (hash-bound and empty protected-path diff)",
        "provenance_and_secret_safety": "PASS",
        "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
    }
