from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from knowledge_compiler import spec061_explanatory_structure_evaluation as spec061
from knowledge_compiler import spec062_conceptual_schema_evaluation as spec062


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / spec062.OUTPUT_DIR


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def packet() -> dict:
    return _load(OUTPUT / "cases.json")


@pytest.fixture(scope="module")
def report() -> dict:
    return _load(OUTPUT / "report.json")


def test_exact_spec061_packet_and_all_frozen_identities_are_preserved(packet: dict) -> None:
    frozen = _load(ROOT / spec062.SPEC061_CASES)
    assert len(packet["cases"]) == 6
    assert [case["spec061_case_identity"] for case in packet["cases"]] == [
        case["case_identity"] for case in frozen["cases"]
    ]
    assert [case["review_index"] for case in packet["cases"]] == list(range(1, 7))
    for path, expected in spec062.EXPECTED_FROZEN_IDENTITIES.items():
        assert spec062._sha(ROOT / path) == expected


def test_s0_is_exact_frozen_spec061_e1(packet: dict) -> None:
    frozen = {
        case["case_identity"]: case
        for case in _load(ROOT / spec062.SPEC061_CASES)["cases"]
    }
    for case in packet["cases"]:
        prior = frozen[case["spec061_case_identity"]]
        assert case["views"]["S0"]["text"] == prior["views"]["E1"]["text"]
        assert case["views"]["S0"]["identity_sha256"] == prior["views"]["E1"]["identity_sha256"]


def test_all_244_semantic_items_are_explicit_and_unchanged_in_s1_and_s2(packet: dict) -> None:
    total = 0
    for case in packet["cases"]:
        model = _load(ROOT / case["source_identity"]["model_path"])
        upstream = spec061._semantic_index(model)
        rows = case["semantic_items"]
        assert {row["upstream_id"] for row in rows} == set(upstream)
        assert len(rows) == len(upstream)
        for row in rows:
            assert row["statement"] == upstream[row["upstream_id"]]["statement"]
            assert row["statement"] in case["views"]["S1"]["text"]
            assert row["statement"] in case["views"]["S2"]["text"]
            assert row["s1_status"] == row["s2_status"] == "PRESERVED_EXPLICITLY"
        total += len(rows)
    assert total == 244


def test_all_46_explanatory_blocks_and_traversal_are_preserved(packet: dict) -> None:
    block_total = transition_total = 0
    for case in packet["cases"]:
        frozen = case["frozen_explanatory_structure"]
        block_ids = [block["id"] for block in frozen["blocks"]]
        member_ids = [
            block_id
            for chunk in case["conceptual_schema_model"]["chunks"]
            if len(chunk["member_blocks"]) == 1
            for block_id in chunk["member_blocks"]
        ]
        assert len(member_ids) == len(set(member_ids)) == len(block_ids)
        assert set(member_ids) == set(block_ids)
        audit = case["explanatory_preservation_audit"]
        assert audit["s1_blocks_preserved"] == audit["s2_blocks_preserved"] == len(block_ids)
        assert audit["s2_traversal_preserved"] == len(frozen["traversal"])
        assert audit["traversal_loss_count"] == audit["function_change_count"] == 0
        block_total += len(block_ids)
        transition_total += len(frozen["traversal"])
    assert block_total == 46
    assert transition_total == 40


def test_chunk_memberships_are_supported_and_complete(packet: dict) -> None:
    for case in packet["cases"]:
        chunks = case["conceptual_schema_model"]["chunks"]
        for chunk in chunks:
            assert chunk["membership_audit"]
            assert all(row["status"] == "SUPPORTED" and row["support"] for row in chunk["membership_audit"])
            assert chunk["evidence_support"]
            assert chunk["semantic_support_ids"] or all(
                not block["all_grounded_semantic_ids"]
                for block in case["frozen_explanatory_structure"]["blocks"]
                if block["id"] in chunk["member_blocks"]
            )
        audit = case["chunk_membership_support_audit"]
        assert audit["membership_count"] == audit["supported_count"]
        assert audit["unsupported_count"] == audit["invented_hierarchy_count"] == 0


def test_schema_roles_and_relations_remain_in_bounded_experimental_registries(packet: dict) -> None:
    seen_roles: set[str] = set()
    seen_relations: set[str] = set()
    for case in packet["cases"]:
        model = case["conceptual_schema_model"]
        seen_roles.update(chunk["role"] for chunk in model["chunks"])
        seen_relations.update(edge["relation"] for edge in model["schema_edges"])
        assert model["inducer"]["source_or_domain_specific_rules"] is False
        assert model["inducer"]["owner_anchor_inputs"] is False
        assert model["inducer"]["paragraph_or_source_order_grouping_rule"] is False
    assert seen_roles <= set(spec062.SCHEMA_ROLES)
    assert seen_relations <= set(spec062.SCHEMA_RELATIONS)
    assert seen_roles and seen_relations


def test_all_schema_edges_have_grounded_support(packet: dict) -> None:
    for case in packet["cases"]:
        edges = case["conceptual_schema_model"]["schema_edges"]
        assert edges
        assert all(edge["support"] for edge in edges)
        audit = case["schema_edge_support_audit"]
        assert audit["edge_count"] == audit["supported_count"] == len(edges)
        assert audit["unsupported_count"] == 0


def test_material_implications_are_preserved_including_astronomy_r14_r15(packet: dict) -> None:
    implication_total = 0
    for case in packet["cases"]:
        audit = case["implication_preservation_audit"]
        assert audit["preserved_count"] == audit["material_implication_count"]
        assert audit["lost_between_endpoints_count"] == 0
        assert audit["unsupported_edge_added_count"] == 0
        assert audit["unresolved_count"] == 0
        assert all(row["s1_status"].startswith("PRESERVED") and row["s2_status"].startswith("PRESERVED") for row in audit["material_implications"])
        implication_total += audit["material_implication_count"]
    astronomy = next(case for case in packet["cases"] if case["source_identity"]["source_id"].startswith("nasa-"))
    by_identity = {row["upstream_identity"]: row for row in astronomy["implication_preservation_audit"]["material_implications"]}
    assert {"r14", "r15"} <= set(by_identity)
    assert implication_total == 95


def test_generic_induction_contains_no_owner_anchor_or_source_identity_routing(packet: dict) -> None:
    implementation = (inspect.getsource(spec062._induce_chunks) + inspect.getsource(spec062._pair_support)).casefold()
    for forbidden in (
        "mid-atlantic",
        "mid atlantic",
        "iceland",
        "krafla",
        "red sea",
        "usgs",
        "nasa",
        "noaa",
        "geology",
        "astronomy",
        "meteorology",
        "r14",
        "r15",
    ):
        assert forbidden not in implementation
    assert all(case["conceptual_schema_model"]["inducer"]["owner_anchor_inputs"] is False for case in packet["cases"])


def test_posthoc_owner_anchors_are_audits_only(report: dict) -> None:
    audit = report["posthoc_owner_anchor_audits"]
    assert audit["audit_timing"] == "POST_HOC_AFTER_GENERIC_OUTPUT_FROZEN"
    assert audit["output_changed_after_comparison"] is False
    assert audit["owner_anchors_used_as_induction_input"] is False
    assert audit["owner_approval_inferred"] is False
    assert audit["geology"]["classification"] in {"ALIGNED", "PARTIALLY_ALIGNED", "MISALIGNED", "UNRESOLVED"}
    assert audit["astronomy"]["classification"] == "ALIGNED"
    assert audit["meteorology"]["semantic_deletion"] == 0


def test_top_level_diagnostic_is_transparent_not_an_optimization(report: dict) -> None:
    per_case = report["schema_distribution"]["per_case"]
    assert [row["top_level_conceptual_chunk_count"] for row in per_case] == [2, 2, 1, 1, 1, 3]
    assert [row["top_level_unit_ratio"] for row in per_case] == [0.2857, 0.1667, 0.25, 0.2, 0.0909, 0.4286]
    assert report["schema_distribution"]["mean_top_level_unit_ratio"] == 0.237
    assert all(row["word_count_is_diagnostic_not_objective"] is True for row in per_case)
    assert all(row["cognitive_load_score_assigned"] is False for row in per_case)


def test_semantic_epistemic_and_provenance_audits_fail_closed(packet: dict) -> None:
    for case in packet["cases"]:
        assert case["semantic_preservation_audit"]["forbidden_status_count"] == 0
        assert case["semantic_preservation_audit"]["material_omission_count"] == 0
        assert case["semantic_preservation_audit"]["unsupported_addition_count"] == 0
        assert case["epistemic_preservation_audit"]["strengthened_certainty_or_causality_count"] == 0
        provenance = case["provenance_recoverability_audit"]
        assert provenance["coverage_ratio"] == 1.0
        assert provenance["semantic_items_with_exact_evidence"] == provenance["semantic_item_count"]
        assert provenance["blocks_with_exact_ranges"] == provenance["block_count"]
        assert provenance["schema_edges_with_support"] == provenance["schema_edge_count"]


def test_every_semantic_evidence_excerpt_is_exactly_recoverable(packet: dict) -> None:
    for case in packet["cases"]:
        source = _load(ROOT / case["source_identity"]["model_path"])["document"]["text"]
        for row in case["semantic_items"]:
            assert row["evidence"]
            for evidence in row["evidence"]:
                assert source[evidence["start_char"] : evidence["end_char"]] == evidence["quote"]
                assert evidence["source_sha256"] == case["source_identity"]["source_sha256"]
                assert evidence["model_sha256"] == case["source_identity"]["model_sha256"]


def test_views_are_independently_generated_peers_without_fact_deletion(packet: dict) -> None:
    for case in packet["cases"]:
        assert case["views"]["S1"]["depends_on"] == []
        assert case["views"]["S2"]["depends_on"] == []
        assert case["independent_generation_audit"] == {
            "all_views_are_peers": True,
            "fact_deletion": False,
            "s0_exact_frozen_spec061_e1": True,
            "s1_not_derived_from_s0": True,
            "s2_not_derived_from_s1": True,
        }


def test_required_standalone_artifacts_match_case_packet(packet: dict) -> None:
    required = (
        "chunk-membership-manifest.json",
        "schema-edge-manifest.json",
        "implication-preservation-audit.json",
        "semantic-preservation-audit.json",
        "epistemic-preservation-audit.json",
        "explanatory-preservation-audit.json",
        "provenance-recoverability-audit.json",
        "top-level-unit-metrics.json",
        "posthoc-owner-anchor-audits.json",
        "deterministic-regeneration.json",
        "project-vision-identity.json",
        "zero-call-zero-retrieval.txt",
        "owner-review-command.txt",
    )
    assert all((OUTPUT / name).is_file() for name in required)
    for case in packet["cases"]:
        for resolution in ("S0", "S1", "S2"):
            path = OUTPUT / "views" / f"{case['case_identity']}-{resolution}.txt"
            assert path.read_text(encoding="utf-8") == case["views"][resolution]["text"] + "\n"


def test_browser_surface_is_textual_neutral_and_verdict_free(report: dict) -> None:
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    script = (OUTPUT / "app.js").read_text(encoding="utf-8")
    assert 'data-owner-anchor-induction="false"' in html
    assert 'data-fact-deletion="false"' in html
    assert 'data-word-count-objective="false"' in html
    assert 'data-diagram-work="false"' in html
    assert 'data-production-promotion="false"' in html
    assert 'data-human-verdict="PENDING"' in html
    assert "machineGate" in script
    assert "case_button_count" in script
    assert "six_cases_present" in script
    assert "all_cases_selectable" in script
    assert "trace_evidence_visible" in script
    assert "no_visualization_dom" in script
    assert html.index('src="review-data.js"') < html.index('src="app.js"')
    assert "DETERMINISTIC_EMBEDDED_PACKET" in script
    assert "createElement(\"svg\")" not in script
    assert "createElement(\"canvas\")" not in script
    browser = _load(OUTPUT / "browser-verification.json")
    assert browser["desktop"]["viewport"] == "1280x720"
    assert browser["narrow"]["viewport"] == "390x844"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert report["browser_gate"] == browser


def test_embedded_review_packet_exactly_matches_frozen_cases_and_rubric(packet: dict) -> None:
    path = OUTPUT / "review-data.js"
    source = path.read_text(encoding="utf-8")
    prefix = '"use strict";\nwindow.__SPEC062_REVIEW_DATA__='
    assert source.startswith(prefix) and source.endswith(";\n")
    embedded = json.loads(source[len(prefix) : -2])
    assert embedded["packet"] == packet
    assert embedded["rubric"] == _load(OUTPUT / "owner-review-rubric.json")
    assert len(embedded["packet"]["cases"]) == 6
    assert all(case["views"]["S0"]["text"] for case in embedded["packet"]["cases"])
    assert all(case["views"]["S1"]["text"] for case in embedded["packet"]["cases"])
    assert all(case["views"]["S2"]["text"] for case in embedded["packet"]["cases"])


def test_review_surface_repair_preserves_frozen_experimental_payload(packet: dict, report: dict) -> None:
    audit = _load(OUTPUT / "artifact-repair-audit.json")
    identity = spec062._frozen_payload_identity(OUTPUT, packet["cases"])
    assert identity == spec062.FROZEN_EXPERIMENTAL_PAYLOAD_SHA256
    assert audit["frozen_experimental_payload_sha256_before"] == identity
    assert audit["frozen_experimental_payload_sha256_after"] == identity
    assert audit["frozen_experimental_payload_file_count"] == 40
    assert audit["identity_preserved"] is True
    assert audit["semantic_schema_or_compression_changes"] == 0
    assert audit["owner_verdict"] == "PENDING"
    assert {
        row["path"]: row["sha256"]
        for row in audit["frozen_evaluation_evidence_identities"]
    } == spec062.FROZEN_SPEC062_EVIDENCE_IDENTITIES
    assert all(
        spec062._sha(OUTPUT / name) == expected
        for name, expected in spec062.FROZEN_SPEC062_EVIDENCE_IDENTITIES.items()
    )
    repair_browser = audit["browser_gate"]
    assert repair_browser["desktop"]["all_6_case_buttons_selectable"] is True
    assert repair_browser["narrow"]["all_6_case_buttons_selectable"] is True
    assert repair_browser["desktop"]["evidence_trace_all_6_cases"] == "PASS"
    assert repair_browser["narrow"]["evidence_trace_all_6_cases"] == "PASS"
    assert repair_browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert report["owner_review"]["verdict"] == "PENDING"


def test_project_vision_distinguishes_compression_and_schema_layers(report: dict) -> None:
    text = (ROOT / spec062.PROJECT_VISION).read_text(encoding="utf-8")
    assert "Linguistic compression reduces expression" in text
    assert "Schema and traversal are complementary." in text
    assert "Reduce avoidable reconstruction." in text
    assert text.index("CONCEPTUAL ORGANIZATION") < text.index("GOAL-PRESERVING SEMANTIC COMPRESSION")
    assert "visualization remains downstream of schema and representation selection" in text
    assert "They are not current implemented capabilities or commitments." in text
    # SPEC-062 records the canonical vision identity at the time its evidence was
    # frozen. Later approved increments may extend the living vision document
    # without rewriting this historical evaluation artifact.
    assert report["project_vision"]["sha256"] == (
        "6e339ef6412396a4959a4cbab11b2e99741bf4d22a143bd398e7bc724e8498a3"
    )
    assert report["project_vision"]["ambition_expanded"] is False


def test_report_stops_at_owner_review_with_zero_calls_and_no_promotion(report: dict) -> None:
    assert report["decision_branch"] == "CONCEPTUAL_SCHEMA_SAFE_FOR_OWNER_REVIEW"
    assert report["recommended_next_step"] == "OWNER_REVIEW_REQUIRED"
    assert report["status"] == "IMPLEMENTED_AWAITING_REVIEW"
    assert report["authority"] == "OFFLINE_ONLY"
    assert report["owner_review"] == {
        "command": spec062.OWNER_COMMAND,
        "promotion": "NOT_AUTHORIZED",
        "rubric": "owner-review-rubric.json",
        "state": "OWNER_REVIEW",
        "url": "http://127.0.0.1:8062/",
        "verdict": "PENDING",
    }
    assert all(value == 0 for value in report["protected_state"].values())
    assert all(value == 0 for value in report["execution_integrity"].values())


def test_generation_is_byte_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    regenerated = tmp_path / "spec062"
    original_sha = spec062._sha

    def historical_vision_sha(path: Path) -> str:
        if path.resolve() == (ROOT / spec062.PROJECT_VISION).resolve():
            return "6e339ef6412396a4959a4cbab11b2e99741bf4d22a143bd398e7bc724e8498a3"
        return original_sha(path)

    monkeypatch.setattr(spec062, "_sha", historical_vision_sha)
    spec062.generate(ROOT, regenerated)
    expected = sorted(path.relative_to(OUTPUT) for path in OUTPUT.rglob("*") if path.is_file())
    actual = sorted(path.relative_to(regenerated) for path in regenerated.rglob("*") if path.is_file())
    assert actual == expected
    assert all((regenerated / path).read_bytes() == (OUTPUT / path).read_bytes() for path in expected)
