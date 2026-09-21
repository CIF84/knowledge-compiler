from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from knowledge_compiler import spec060_semantic_compression_evaluation as spec060
from knowledge_compiler import spec061_explanatory_structure_evaluation as spec061


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / spec061.OUTPUT_DIR


@pytest.fixture(scope="module")
def packet() -> dict:
    return json.loads((OUTPUT / "cases.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def report() -> dict:
    return json.loads((OUTPUT / "report.json").read_text(encoding="utf-8"))


def test_exact_spec060_six_case_packet_is_frozen(packet: dict) -> None:
    frozen = json.loads((ROOT / spec061.SPEC060_CASES).read_text(encoding="utf-8"))
    assert len(packet["cases"]) == 6
    assert [case["spec060_case_identity"] for case in packet["cases"]] == [
        case["case_identity"] for case in frozen["cases"]
    ]
    assert [case["review_index"] for case in packet["cases"]] == list(range(1, 7))
    for path, expected in spec061.EXPECTED_FROZEN_IDENTITIES.items():
        assert spec061._sha(ROOT / path) == expected


def test_e0_is_exact_spec060_r0(packet: dict) -> None:
    frozen = json.loads((ROOT / spec061.SPEC060_CASES).read_text(encoding="utf-8"))
    by_id = {case["case_identity"]: case for case in frozen["cases"]}
    for case in packet["cases"]:
        prior = by_id[case["spec060_case_identity"]]
        assert case["views"]["E0"]["text"] == prior["views"]["R0"]["text"]
        assert (
            case["views"]["E0"]["identity_sha256"]
            == prior["views"]["R0"]["identity_sha256"]
        )


def test_blocks_have_exact_source_ranges_and_complete_sentence_assignment(packet: dict) -> None:
    for case in packet["cases"]:
        source = case["views"]["E0"]["text"]
        model = case["explanatory_structure_model"]
        sentence_ids = []
        previous_end = -1
        for block in model["blocks"]:
            assert block["start_char"] >= previous_end
            assert source[block["start_char"] : block["end_char"]] == block["source_text"]
            assert len(block["source_ranges"]) == 1
            exact = block["source_ranges"][0]
            assert source[exact["start_char"] : exact["end_char"]] == exact["quote"]
            assert spec061._text_sha(exact["quote"]) == exact["sha256"]
            sentence_ids.extend(block["sentence_ids"])
            previous_end = block["end_char"]
        manifest_ids = [row["id"] for row in model["sentence_manifest"]]
        assert sentence_ids == manifest_ids
        assert len(sentence_ids) == len(set(sentence_ids))
        assert model["diagnostics"]["source_sentences_assigned_once"] is True
        assert model["unassigned_material"] == []


def test_paragraph_boundaries_are_evidence_not_block_identity(packet: dict) -> None:
    split_count = 0
    cross_paragraph_count = 0
    for case in packet["cases"]:
        model = case["explanatory_structure_model"]
        assert model["detector"]["paragraph_equals_block_assumption"] is False
        split_count += model["diagnostics"]["paragraphs_split_across_blocks"]
        cross_paragraph_count += model["diagnostics"][
            "blocks_spanning_multiple_paragraphs"
        ]
        for paragraph in model["paragraph_mapping"]:
            expected = [
                block["id"]
                for block in model["blocks"]
                if paragraph["id"] in block["paragraph_ids"]
            ]
            assert paragraph["block_ids"] == expected
            assert paragraph["split_across_blocks"] == (len(expected) > 1)
    assert split_count > 0
    assert cross_paragraph_count > 0


def test_detector_is_generic_and_case01_pattern_is_post_hoc(packet: dict) -> None:
    detector_source = inspect.getsource(spec061.detect_explanatory_structure).casefold()
    for forbidden in (
        "mid-atlantic",
        "mid atlantic",
        "krafla",
        "red sea",
        "iceland",
        "usgs",
        "jet stream",
        "solar system",
    ):
        assert forbidden not in detector_source
    for case in packet["cases"]:
        detector = case["explanatory_structure_model"]["detector"]
        assert detector["domain_or_source_specific_rules"] is False
    alignment = packet["cases"][0]["case01_owner_pattern_alignment"]
    assert alignment["audit_timing"] == "POST_HOC_AFTER_GENERIC_OUTPUT_FROZEN"
    assert alignment["output_changed_after_comparison"] is False
    assert alignment["owner_pattern_used_as_detector_input"] is False
    assert alignment["owner_approval_inferred"] is False
    assert alignment["classification"] == "ALIGNED"
    assert all(
        case["case01_owner_pattern_alignment"]["applicable"] is False
        for case in packet["cases"][1:]
    )


def test_function_and_relation_registries_are_bounded(packet: dict) -> None:
    seen_functions = set()
    seen_relations = set()
    for case in packet["cases"]:
        model = case["explanatory_structure_model"]
        seen_functions.update(block["explanatory_function"] for block in model["blocks"])
        seen_relations.update(row["discourse_relation"] for row in model["traversal"])
    assert seen_functions <= set(spec061.EXPLANATORY_FUNCTIONS)
    assert seen_relations <= set(spec061.DISCOURSE_RELATIONS)
    assert seen_functions
    assert seen_relations


def test_every_traversal_is_adjacent_supported_and_source_ordered(packet: dict) -> None:
    for case in packet["cases"]:
        model = case["explanatory_structure_model"]
        by_id = {block["id"]: block for block in model["blocks"]}
        assert len(model["traversal"]) == max(0, len(model["blocks"]) - 1)
        for index, transition in enumerate(model["traversal"]):
            previous = model["blocks"][index]
            current = model["blocks"][index + 1]
            assert transition["from_block"] == previous["id"]
            assert transition["to_block"] == current["id"]
            assert by_id[transition["from_block"]]["sequence"] + 1 == by_id[
                transition["to_block"]
            ]["sequence"]
            assert transition["support"]
            assert transition["support"][0]["type"] == "SOURCE_ORDER"
            assert transition["source_order_preserved"] is True


def test_e1_and_e2_are_peer_views_with_block_order_preserved(packet: dict) -> None:
    for case in packet["cases"]:
        expected = [
            block["id"] for block in case["explanatory_structure_model"]["blocks"]
        ]
        assert [block["block_id"] for block in case["views"]["E1"]["blocks"]] == expected
        assert [block["block_id"] for block in case["views"]["E2"]["blocks"]] == expected
        assert case["views"]["E1"]["depends_on"] == []
        assert case["views"]["E2"]["depends_on"] == []
        audit = case["independent_generation_audit"]
        assert audit["e1_depends_on_e0_view"] is False
        assert audit["e2_depends_on_e1_view"] is False
        assert audit["destructive_summary_chaining"] is False


def test_semantic_and_epistemic_preservation_fail_closed(packet: dict) -> None:
    for case in packet["cases"]:
        semantic = case["semantic_preservation_audit"]
        assert semantic["required_item_count"] >= len(case["frozen_required_item_ids"])
        assert semantic["forbidden_status_count"] == 0
        assert semantic["unsupported_new_information_count"] == 0
        assert semantic["material_omission_count"] == 0
        assert semantic["semantic_change_count"] == 0
        assert all(
            row["e1_status"].startswith("PRESERVED")
            and row["e2_status"].startswith("PRESERVED")
            for row in semantic["required_items"]
        )
        epistemic = case["epistemic_preservation_audit"]
        assert epistemic["strengthened_certainty_or_causality_count"] == 0
        assert epistemic["e1_uses_exact_source_sentences"] is True
        assert epistemic["e2_uses_exact_admitted_semantic_statements"] is True


def test_explanatory_preservation_and_dropped_material_are_audited(packet: dict) -> None:
    for case in packet["cases"]:
        audit = case["explanatory_preservation_audit"]
        assert audit["traversal_lost_count"] == 0
        assert audit["function_changed_count"] == 0
        assert audit["unsupported_structure_added_count"] == 0
        assert audit["unresolved_explanatory_loss_count"] == 0
        assert audit["source_order_reordering_count"] == 0
        assert audit["all_transitions_have_source_grounded_support"] is True
        assert all(
            row["e1_status"] == row["e2_status"] == "PRESERVED"
            for row in audit["block_audit"] + audit["transition_audit"]
        )
        assert all(
            row["status"] == "DROPPED_AS_REDUNDANT"
            for row in audit["dropped_sentence_dispositions"]
        )


def test_provenance_is_exact_and_complete(packet: dict) -> None:
    for case in packet["cases"]:
        source = case["views"]["E0"]["text"]
        identity = case["source_identity"]
        for block in case["explanatory_structure_model"]["blocks"]:
            for row in block["semantic_support"]:
                assert row["evidence"]
                for evidence in row["evidence"]:
                    assert source[evidence["start_char"] : evidence["end_char"]] == evidence["quote"]
                    assert evidence["source_id"] == identity["source_id"]
                    assert evidence["model_sha256"] == identity["model_sha256"]
        provenance = case["provenance_recoverability_audit"]
        assert provenance["coverage_ratio"] == 1.0
        assert provenance["recoverable_to_exact_e0"] is True


def test_metrics_are_diagnostic_and_preserve_mixed_result(report: dict) -> None:
    assert report["decision_branch"] == "INCONCLUSIVE"
    assert report["recommended_next_step"] == "OWNER_REVIEW_REQUIRED"
    assert report["compression_metrics"]["mean_e1_to_e0_word_ratio"] == 0.94
    assert report["compression_metrics"]["mean_e2_to_e0_word_ratio"] == 0.826
    assert report["compression_metrics"]["word_count_is_diagnostic_not_objective"] is True
    assert report["compression_metrics"]["pseudo_scientific_reconstruction_score_assigned"] is False
    per_case = report["compression_metrics"]["per_case"]
    assert sum(row["e1"]["words"] < row["e0"]["words"] for row in per_case) == 3
    assert sum(row["e2"]["words"] < row["e0"]["words"] for row in per_case) == 5


def test_browser_contract_has_no_visualization_or_verdict() -> None:
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    script = (OUTPUT / "app.js").read_text(encoding="utf-8")
    assert 'data-paragraph-equals-block="false"' in html
    assert 'data-case01-hardcoding="false"' in html
    assert 'data-visualization-work="false"' in html
    assert 'data-production-promotion="false"' in html
    assert 'data-human-verdict="PENDING"' in html
    assert "machineGate" in script
    assert "paragraph_overlay_complete" in script
    assert "createElement(\"svg\")" not in script
    assert "canvas" not in html.casefold()


def test_browser_verification_record_is_complete(report: dict) -> None:
    browser = json.loads((OUTPUT / "browser-verification.json").read_text(encoding="utf-8"))
    assert browser["status"] == "PASS"
    assert browser["desktop"]["viewport"] == "1280x720"
    assert browser["narrow"]["viewport"] == "390x844"
    assert browser["desktop"]["horizontal_overflow"] is False
    assert browser["narrow"]["horizontal_overflow"] is False
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert report["browser_gate"] == browser


def test_project_vision_places_structure_before_compression(report: dict) -> None:
    text = (ROOT / spec061.PROJECT_VISION).read_text(encoding="utf-8")
    principle = (
        "Semantic preservation is necessary but not sufficient; useful explanatory "
        "structure is itself information that compression should preserve."
    )
    assert principle in text
    assert text.index("EXPLANATORY STRUCTURE") < text.index(
        "GOAL-PRESERVING SEMANTIC COMPRESSION"
    )
    assert "They are not current implemented capabilities or commitments." in text
    assert report["project_vision"]["sha256"] == spec061._sha(ROOT / spec061.PROJECT_VISION)
    assert report["project_vision"]["product_ambition_expanded"] is False


def test_report_preserves_owner_gate_and_zero_call_policy(report: dict) -> None:
    assert report["status"] == "IMPLEMENTED_AWAITING_REVIEW"
    assert report["authority"] == "OFFLINE_ONLY"
    assert report["owner_review"] == {
        "command": spec061.OWNER_COMMAND,
        "promotion": "NOT_AUTHORIZED",
        "rubric": "owner-review-rubric.json",
        "state": "OWNER_REVIEW",
        "url": "http://127.0.0.1:8061/",
        "verdict": "PENDING",
    }
    assert all(value == 0 for value in report["protected_state"].values())
    assert all(value == 0 for value in report["execution_integrity"].values())
    assert report["zero_call_zero_retrieval_statement"].startswith("No provider/model call")


def test_required_manifests_match_cases(packet: dict) -> None:
    blocks = json.loads((OUTPUT / "block-manifest.json").read_text(encoding="utf-8"))
    functions = json.loads((OUTPUT / "function-manifest.json").read_text(encoding="utf-8"))
    traversal = json.loads((OUTPUT / "traversal-manifest.json").read_text(encoding="utf-8"))
    paragraphs = json.loads((OUTPUT / "paragraph-mapping.json").read_text(encoding="utf-8"))
    for aggregate, key in (
        (blocks, "blocks"),
        (traversal, "traversal"),
        (paragraphs, "paragraph_mapping"),
    ):
        assert [row["case_identity"] for row in aggregate["cases"]] == [
            case["case_identity"] for case in packet["cases"]
        ]
        assert [row[key] for row in aggregate["cases"]] == [
            case["explanatory_structure_model"][key] for case in packet["cases"]
        ]
    assert functions["registry"] == list(spec061.EXPLANATORY_FUNCTIONS)
    assert functions["source_or_domain_specific_labels"] is False
    for row, case in zip(functions["cases"], packet["cases"]):
        assert row["case_identity"] == case["case_identity"]
        assert [assignment["block_id"] for assignment in row["assignments"]] == [
            block["id"] for block in case["explanatory_structure_model"]["blocks"]
        ]


def test_deterministic_regeneration(tmp_path: Path) -> None:
    regenerated = tmp_path / "spec061"
    regenerated_report = spec061.generate(ROOT, regenerated)
    assert regenerated_report == json.loads((OUTPUT / "report.json").read_text(encoding="utf-8"))
    expected = sorted(path.relative_to(OUTPUT) for path in OUTPUT.rglob("*") if path.is_file())
    actual = sorted(path.relative_to(regenerated) for path in regenerated.rglob("*") if path.is_file())
    assert actual == expected
    for relative in expected:
        assert (regenerated / relative).read_bytes() == (OUTPUT / relative).read_bytes()
