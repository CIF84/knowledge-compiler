from __future__ import annotations

import hashlib
import json
from pathlib import Path

from knowledge_compiler.spec060_semantic_compression_evaluation import (
    BROWSER_VERIFICATION,
    EXPECTED_EVIDENCE_IDENTITIES,
    OUTPUT_DIR,
    OWNER_COMMAND,
    PROJECT_VISION,
    SEMANTIC_ROLES,
    SOURCES,
    SOURCE_ROOT,
    build_case,
    generate,
)


ROOT = Path(__file__).parents[1]
OUTPUT = ROOT / OUTPUT_DIR


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _cases():
    return _load(OUTPUT / "cases.json")["cases"]


def _model(case):
    return _load(ROOT / case["source_identity"]["model_path"])


def _item_index(model):
    return {
        item["id"]: item
        for semantic_class in ("claims", "propositions", "relationships")
        for item in model.get(semantic_class, [])
    }


def test_manifest_selects_first_six_admitted_sources_without_success_cherry_picking():
    manifest = _load(OUTPUT / "manifest.json")
    assert manifest["case_count"] == 6
    assert [Path(row["source_identity"]["model_path"]).parent.name for row in manifest["cases"]] == list(SOURCES)
    algorithm = manifest["selection_algorithm"]
    assert algorithm["ordering"] == "Frozen SPEC-052 source-directory ordinal, ascending."
    assert algorithm["cherry_pick_expected_success"] is False
    assert len({row["source_identity"]["domain"] for row in manifest["cases"]}) == 6
    coverage = set(algorithm["required_coverage"])
    assert {"PROCESS_MECHANISM", "STRUCTURAL_RELATIONSHIP", "QUANTITATIVE_FACT", "QUALIFICATION_UNCERTAINTY", "RHETORICAL_REPETITION"} <= coverage


def test_each_r0_is_the_exact_full_admitted_document_text():
    for case in _cases():
        model = _model(case)
        assert case["views"]["R0"]["text"] == model["document"]["text"]
        assert case["views"]["R0"]["identity_sha256"] == hashlib.sha256(
            model["document"]["text"].encode()
        ).hexdigest()
        assert case["views"]["R0"]["direct_input"] == "FROZEN_ADMITTED_DOCUMENT_TEXT"


def test_r1_is_exact_source_ranges_selected_directly_from_grounded_evidence():
    for case in _cases():
        source = case["views"]["R0"]["text"]
        segments = case["views"]["R1"]["segments"]
        assert segments
        assert case["views"]["R1"]["text"] == "\n\n".join(
            row["text"] for row in segments
        )
        for row in segments:
            assert source[row["start_char"] : row["end_char"]] == row["text"]
            assert hashlib.sha256(row["text"].encode()).hexdigest() == row["text_sha256"]
        assert case["views"]["R1"]["direct_input"] == (
            "FROZEN_SOURCE_TEXT_AND_REQUIRED_EVIDENCE_RANGES"
        )


def test_r2_units_are_exact_admitted_semantic_statements_with_broad_roles_only():
    for case in _cases():
        items = _item_index(_model(case))
        units = case["essential_information_model"]["units"]
        assert units
        assert case["views"]["R2"]["text"] == "\n".join(
            unit["concise_text"] for unit in units
        )
        assert case["views"]["R2"]["unit_ids"] == [unit["id"] for unit in units]
        for unit in units:
            assert unit["semantic_role"] in SEMANTIC_ROLES
            represented_ids = {row["id"] for row in unit["preserved_from"]}
            assert any(items[item_id]["statement"] == unit["concise_text"] for item_id in represented_ids)
            assert unit["epistemic_status"] in {
                "ASSERTED_SOURCE_CLAIM",
                "ATTRIBUTED_SOURCE_CLAIM",
                "OBSERVATIONAL_OR_ASSOCIATIONAL",
                "QUALIFIED_OR_UNCERTAIN",
            }
        assert case["views"]["R2"]["direct_input"] == (
            "FROZEN_ADMITTED_SEMANTIC_ITEMS_AND_EVIDENCE"
        )


def test_all_three_views_are_independent_peers_not_a_destructive_chain():
    for case in _cases():
        assert all(not case["views"][mode]["depends_on"] for mode in ("R0", "R1", "R2"))
        assert case["independent_generation_audit"] == {
            "destructive_chaining": False,
            "r0_derived_directly_from_grounded_substrate": True,
            "r1_derived_directly_from_grounded_substrate": True,
            "r1_is_not_input_to_r2": True,
            "r2_derived_directly_from_grounded_substrate": True,
            "r2_is_not_input_to_r1": True,
        }


def test_compression_metrics_are_exact_and_progressively_smaller_by_content_words():
    report = _load(OUTPUT / "report.json")
    for case in _cases():
        metrics = case["essential_information_model"]["compression_metrics"]
        assert metrics["r0"]["words"] > metrics["r1"]["words"] > metrics["r2"]["words"]
        assert metrics["r0"]["characters"] == len(case["views"]["R0"]["text"])
        assert metrics["r1"]["characters"] == len(case["views"]["R1"]["text"])
        assert metrics["r2"]["characters"] == len(case["views"]["R2"]["text"])
        assert 0 < metrics["r1_to_r0_word_ratio"] < 1
        assert 0 < metrics["r2_to_r0_word_ratio"] < metrics["r1_to_r0_word_ratio"]
    aggregate = report["compression_metrics"]
    assert aggregate["all_r1_views_smaller_than_r0"] is True
    assert aggregate["all_r2_views_smaller_than_r0"] is True
    assert aggregate["all_r2_content_views_smaller_than_r1"] is True
    assert aggregate["semantic_role_labels_excluded_from_content_metrics"] is True


def test_every_required_semantic_item_has_only_admitted_preservation_statuses():
    allowed = {"PRESERVED_EXPLICITLY", "PRESERVED_BY_FAITHFUL_COMBINATION"}
    for case in _cases():
        audit = case["semantic_preservation_audit"]
        assert audit["required_item_count"] == len(audit["required_items"])
        assert audit["forbidden_required_status_count"] == 0
        assert audit["material_omission_count"] == 0
        assert audit["semantic_change_count"] == 0
        assert audit["unsupported_new_information_count"] == 0
        assert all(row["r1_status"] in allowed and row["r2_status"] in allowed for row in audit["required_items"])


def test_audit_accounts_for_every_upstream_semantic_identity_exactly_once():
    for case in _cases():
        model = _model(case)
        expected = {
            item["id"]
            for semantic_class in ("claims", "propositions", "relationships")
            for item in model.get(semantic_class, [])
        }
        audit = case["semantic_preservation_audit"]
        actual = [row["upstream_id"] for row in audit["required_items"]] + [
            row["upstream_id"] for row in audit["contextual_item_disposition"]
        ]
        assert len(actual) == len(set(actual))
        assert set(actual) == expected
        assert all(
            row["status"] in {
                "PRESERVED_BY_FAITHFUL_COMBINATION",
                "OMITTED_AS_DEMONSTRABLY_REDUNDANT",
            }
            for row in audit["contextual_item_disposition"]
        )


def test_epistemic_qualification_values_causality_and_attribution_audits_pass():
    for case in _cases():
        audit = case["epistemic_preservation_audit"]
        assert audit["qualification_links_preserved_verbatim"] is True
        assert audit["values_and_units_preserved_verbatim"] is True
        assert audit["causal_vs_associational_status_preserved"] is True
        assert audit["attribution_preserved"] is True
        assert audit["temporal_scope_preserved_where_selected"] is True
        assert audit["precision_preserved_where_selected"] is True
        assert audit["strengthened_certainty_or_causality_count"] == 0
    doe = next(case for case in _cases() if case["source_identity"]["source_id"].startswith("doe-"))
    assert "OBSERVATIONAL_OR_ASSOCIATIONAL" in doe["epistemic_preservation_audit"]["epistemic_status_distribution"]


def test_every_unit_support_is_an_exact_source_range_with_frozen_model_identity():
    for case in _cases():
        source = case["views"]["R0"]["text"]
        expected_model_sha = case["source_identity"]["model_sha256"]
        for unit in case["essential_information_model"]["units"]:
            assert unit["support"]
            for support in unit["support"]:
                assert source[support["start_char"] : support["end_char"]] == support["quote"]
                assert support["model_sha256"] == expected_model_sha
                assert support["model_path"] == case["source_identity"]["model_path"]
        audit = case["provenance_recoverability_audit"]
        assert audit["unit_count"] == audit["units_with_support"] == audit["units_with_source_and_model_identity"]
        assert audit["coverage_ratio"] == 1.0
        assert audit["recoverable_to_r0"] is True


def test_omitted_fragments_remain_byte_recoverable_in_r0_with_explicit_reasons():
    allowed = {
        "RHETORICAL_OR_EVALUATIVE_FRAMING",
        "DETAIL_OR_LINGUISTIC_CONTEXT_RETAINED_IN_R0",
    }
    for case in _cases():
        source = case["views"]["R0"]["text"]
        for row in case["essential_information_model"]["omitted_fragments"]:
            identity = row["upstream_identity"]
            assert source[identity["start_char"] : identity["end_char"]] == row["text"]
            assert hashlib.sha256(row["text"].encode()).hexdigest() == identity["sha256"]
            assert row["omission_reason"] in allowed


def test_same_projection_contract_applies_to_every_source_without_identity_routing():
    for case in _cases():
        assert case["selection"]["source_or_domain_specific_rule"] is False
        rebuilt = build_case(
            ROOT,
            Path(case["source_identity"]["model_path"]).parent.name,
            case["review_index"],
        )
        assert rebuilt == case


def test_browser_artifact_is_neutral_textual_and_contains_no_visualization_surface():
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    script = (OUTPUT / "app.js").read_text(encoding="utf-8")
    for marker in (
        "R0 · Source-rich",
        "R1 · Explanation",
        "R2 · Units",
        "Audit",
        'data-view-lineage="INDEPENDENT_FROM_GROUNDED_SUBSTRATE"',
        'data-visualization-work="false"',
        'data-personalization="false"',
        'data-production-promotion="false"',
        'data-human-verdict="PENDING"',
    ):
        assert marker in html
    assert 'querySelectorAll("svg,canvas,.diagram,.chart")' in script
    assert "renderUnits" in script and "renderAudit" in script


def test_browser_gate_passes_desktop_narrow_interaction_and_clean_console():
    record = _load(OUTPUT / "browser-verification.json")
    assert record == BROWSER_VERIFICATION
    assert record["status"] == "PASS"
    assert record["desktop"]["all_6_cases_loaded"] is True
    assert record["desktop"]["all_case_machine_checks_passed"] is True
    assert record["desktop"]["horizontal_overflow"] is False
    assert record["narrow"]["viewport"] == "390x844"
    assert record["narrow"]["single_column_workspace"] is True
    assert record["narrow"]["horizontal_overflow"] is False
    assert record["narrow"]["all_case_machine_checks_passed"] is True
    assert all(value == "PASS" for value in record["interaction"].values())
    assert record["console"] == {"errors": [], "result": "PASS", "warnings": []}


def test_project_vision_is_canonical_hash_bound_and_respects_ambition_boundary():
    report = _load(OUTPUT / "report.json")
    vision = (ROOT / PROJECT_VISION).read_text(encoding="utf-8")
    assert report["vision_and_mission"]["mission_document"] == PROJECT_VISION
    assert report["vision_and_mission"]["mission_document_sha256"] == hashlib.sha256(
        vision.encode()
    ).hexdigest()
    for phrase in (
        "Compression is a view over knowledge, not destruction of knowledge.",
        "Meaning before medium.",
        "Compression before visualization.",
        "Prose is first-class.",
        "Podcast and video ingestion",
        "not current implemented capabilities",
    ):
        assert phrase in vision
    assert report["vision_and_mission"]["future_ambition_presented_as_current_capability"] is False


def test_frozen_evidence_artifact_and_implementation_hashes_match():
    report = _load(OUTPUT / "report.json")
    evidence = {row["path"]: row["sha256"] for row in report["evidence_identities"]}
    assert evidence == EXPECTED_EVIDENCE_IDENTITIES
    for path, expected in evidence.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    for key, base in (("artifact_identities", OUTPUT), ("implementation_identities", ROOT)):
        for row in report[key]:
            assert hashlib.sha256((base / row["path"]).read_bytes()).hexdigest() == row["sha256"]


def test_artifact_regeneration_is_byte_deterministic(tmp_path):
    generated = tmp_path / "generated"
    generate(ROOT, generated)
    expected_files = sorted(
        path.relative_to(OUTPUT) for path in OUTPUT.rglob("*") if path.is_file()
    )
    actual_files = sorted(
        path.relative_to(generated) for path in generated.rglob("*") if path.is_file()
    )
    assert actual_files == expected_files
    for relative in expected_files:
        assert (generated / relative).read_bytes() == (OUTPUT / relative).read_bytes()


def test_report_stops_at_owner_review_without_calls_promotion_or_human_verdict():
    report = _load(OUTPUT / "report.json")
    assert report["decision_branch"] == "SEMANTIC_COMPRESSION_SAFE_FOR_OWNER_REVIEW"
    assert report["recommended_next_step"] == "OWNER_REVIEW_REQUIRED"
    assert report["evaluation_questions"]["learning_improvement_established"] == (
        "NO — OWNER REVIEW REQUIRED"
    )
    assert report["owner_review"] == {
        "command": OWNER_COMMAND,
        "promotion": "NOT_AUTHORIZED",
        "rubric": "owner-review-rubric.json",
        "state": "OWNER_REVIEW",
        "url": "http://127.0.0.1:8060/",
        "verdict": "PENDING",
    }
    assert all(value == 0 for value in report["protected_state"].values())
    assert all(value == 0 for value in report["execution_integrity"].values())
    assert report["zero_call_zero_retrieval_statement"].startswith("No provider/model call")
