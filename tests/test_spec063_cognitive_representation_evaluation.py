from __future__ import annotations

import inspect
import json
from collections import Counter
from pathlib import Path

import pytest

from knowledge_compiler import spec063_cognitive_representation_evaluation as spec063


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / spec063.OUTPUT_DIR


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def packet() -> dict:
    return _load(OUTPUT / "cases.json")


@pytest.fixture(scope="module")
def report() -> dict:
    return _load(OUTPUT / "report.json")


def test_exact_spec062_tree_and_frozen_model_files_are_preserved(packet: dict) -> None:
    identity, files = spec063._tree_identity(ROOT / spec063.SPEC062_DIR)
    assert identity == spec063.EXPECTED_SPEC062_TREE_SHA256
    assert len(files) == spec063.EXPECTED_SPEC062_TREE_FILE_COUNT
    assert spec063._sha(ROOT / spec063.SPEC062_CASES) == spec063.EXPECTED_CASES_SHA256
    assert len(packet["cases"]) == 3
    frozen = spec063._frozen_cases(ROOT)
    assert [case["spec062_case_identity"] for case in packet["cases"]] == [
        case["case_identity"] for case in frozen
    ]
    manifest = _load(OUTPUT / "manifest.json")
    assert [row["frozen_spec062_model_file_sha256"] for row in manifest["cases"]] == list(
        spec063.FROZEN_CASE_MODEL_IDENTITIES
    )


def test_contract_corpus_order_and_peer_controls_are_exact(packet: dict) -> None:
    frozen = spec063._frozen_cases(ROOT)
    assert [case["source_identity"]["title"] for case in packet["cases"]] == [
        "Understanding plate motions",
        "How did our Solar System form?",
        "What Is the Jet Stream?",
    ]
    for case, upstream in zip(packet["cases"], frozen, strict=True):
        assert case["views"]["P0"]["text"] == upstream["views"]["S0"]["text"]
        assert case["views"]["P0"]["identity_sha256"] == upstream["views"]["S0"]["identity_sha256"]
        assert case["views"]["P1"]["text"] == upstream["views"]["S1"]["text"]
        assert case["views"]["P1"]["identity_sha256"] == upstream["views"]["S1"]["identity_sha256"]


def test_generic_grammar_selection_is_deterministic_and_bounded(packet: dict) -> None:
    frozen = spec063._frozen_cases(ROOT)
    expected = ["BRANCHING", "CAUSAL_OR_DEPENDENCY_CHAIN", "HIERARCHY"]
    assert [case["compilation_decision"]["selected_grammar"] for case in packet["cases"]] == expected
    for upstream, expected_grammar in zip(frozen, expected, strict=True):
        features = spec063._grammar_features(upstream)
        assert spec063._select_grammar(features)[0] == expected_grammar
        assert spec063._select_grammar(features) == spec063._select_grammar(features)
        assert expected_grammar in spec063.GRAMMAR_FAMILIES


def test_compiler_has_no_domain_source_case_or_anchor_routing() -> None:
    selector_source = (
        inspect.getsource(spec063._grammar_features)
        + inspect.getsource(spec063._select_grammar)
    ).casefold()
    compiler_source = inspect.getsource(spec063._compile_learner_representation).casefold()
    for forbidden in (
        "geology",
        "astronomy",
        "meteorology",
        "understanding plate motions",
        "solar system",
        "jet stream",
        "usgs",
        "nasa",
        "noaa",
        "r14",
        "r15",
        "owner",
        "case_identity",
    ):
        assert forbidden not in selector_source + compiler_source
    assert "source_identity" not in selector_source
    assert "case_identity" not in selector_source


def test_all_semantics_and_material_implications_are_recoverable(packet: dict) -> None:
    semantic_total = implication_total = 0
    for case in packet["cases"]:
        semantic = case["semantic_schema_preservation_audit"]
        implication = case["implication_preservation_audit"]
        assert semantic["semantic_item_identity_set_preserved"] is True
        assert semantic["p2_recoverable_semantic_item_count"] == semantic["frozen_semantic_item_count"]
        assert semantic["schema_mutations"] == semantic["unsupported_inference_count"] == 0
        assert implication["statement_multiset_preserved"] is True
        assert implication["p2_recoverable_implication_count"] == implication["frozen_material_implication_count"]
        assert implication["lost_count"] == implication["unsupported_added_count"] == 0
        semantic_total += semantic["frozen_semantic_item_count"]
        implication_total += implication["frozen_material_implication_count"]
    assert semantic_total == 141
    assert implication_total == 54


def test_p2_statements_match_the_frozen_schema_payload(packet: dict) -> None:
    frozen = {case["case_identity"]: case for case in spec063._frozen_cases(ROOT)}
    for case in packet["cases"]:
        upstream = frozen[case["spec062_case_identity"]]
        learner = case["views"]["P2"]["learner_representation"]
        represented = [
            statement
            for group in learner["groups"]
            for unit in group["units"]
            for statement in unit["detail_statements"]
        ]
        implications = [row["statement"] for row in learner["connections"]]
        assert Counter(represented) == Counter(row["statement"] for row in upstream["semantic_items"])
        assert Counter(implications) == Counter(
            row["statement"]
            for row in upstream["implication_preservation_audit"]["material_implications"]
        )


def test_every_p2_unit_has_exact_frozen_evidence(packet: dict) -> None:
    expected_counts = [7, 5, 12]
    for case, count in zip(packet["cases"], expected_counts, strict=True):
        audit = case["provenance_recoverability_audit"]
        units = [unit for group in case["views"]["P2"]["learner_representation"]["groups"] for unit in group["units"]]
        assert len(units) == audit["learner_unit_count"] == audit["learner_units_with_evidence"] == count
        assert audit["coverage_ratio"] == 1.0
        assert all(unit["evidence"] and all(row["quote"] for row in unit["evidence"]) for unit in units)


def test_p2_exposes_no_raw_ids_or_debug_metadata(packet: dict) -> None:
    for case in packet["cases"]:
        learner_json = json.dumps(case["views"]["P2"]["learner_representation"], ensure_ascii=False)
        assert all(token not in learner_json for token in spec063.LEARNER_FORBIDDEN_TOKENS)
        assert case["p1_p2_distinction_audit"] == {
            "identity_distinct": True,
            "p1_is_raw_text_control": True,
            "p2_is_perceptual_composition": True,
            "raw_debug_metadata_visible_in_p2": False,
        }


def test_diagnostic_anchors_are_posthoc_and_astronomy_implications_visible(report: dict) -> None:
    audit = report["diagnostic_anchor_audit"]
    assert audit["audit_timing"] == "POST_HOC_AFTER_GENERIC_P2_OUTPUTS_FROZEN"
    assert audit["outputs_changed_after_comparison"] is False
    assert audit["owner_anchors_used_as_compiler_input"] is False
    assert audit["owner_verdict_inferred"] is False
    assert audit["astronomy"]["r14_primary"] is True
    assert audit["astronomy"]["r15_primary"] is True


def test_required_artifacts_and_views_are_complete(packet: dict) -> None:
    required = (
        "manifest.json",
        "grammar-selection-decisions.json",
        "cognitive-utility-audit.json",
        "semantic-schema-preservation-audit.json",
        "implication-preservation-audit.json",
        "provenance-recoverability-audit.json",
        "diagnostic-anchor-audit.json",
        "deterministic-regeneration.json",
        "browser-verification.json",
        "project-vision-identity.json",
        "zero-call-zero-retrieval.txt",
        "owner-review-command.txt",
        "owner-review-rubric.json",
    )
    assert all((OUTPUT / name).is_file() for name in required)
    for case in packet["cases"]:
        stem = case["case_identity"]
        assert (OUTPUT / "views" / f"{stem}-P0.txt").read_text(encoding="utf-8") == case["views"]["P0"]["text"] + "\n"
        assert (OUTPUT / "views" / f"{stem}-P1.txt").read_text(encoding="utf-8") == case["views"]["P1"]["text"] + "\n"
        assert _load(OUTPUT / "views" / f"{stem}-P2.json") == case["views"]["P2"]["learner_representation"]


def test_browser_contract_loads_all_cases_treatments_and_interactions(report: dict) -> None:
    html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    script = (OUTPUT / "app.js").read_text(encoding="utf-8")
    assert 'data-spec062-schema-mutated="false"' in html
    assert 'data-domain-source-case-routing="false"' in html
    assert 'data-production-promotion="false"' in html
    assert 'data-human-verdict="PENDING"' in html
    assert html.index('src="review-data.js"') < html.index('src="app.js"')
    for marker in (
        "three_cases_present",
        "all_cases_selectable",
        "p1_p2_perceptually_distinct",
        "detail_selection_works",
        "detail_and_evidence_visible",
        "DETERMINISTIC_EMBEDDED_PACKET",
    ):
        assert marker in script
    browser = _load(OUTPUT / "browser-verification.json")
    assert browser["desktop"]["viewport"] == "1280x720"
    assert browser["narrow"]["viewport"] == "390x844"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert report["browser_gate"] == browser


def test_embedded_packet_exactly_matches_case_packet_and_rubric(packet: dict) -> None:
    source = (OUTPUT / "review-data.js").read_text(encoding="utf-8")
    prefix = '"use strict";\nwindow.__SPEC063_REVIEW_DATA__='
    assert source.startswith(prefix) and source.endswith(";\n")
    embedded = json.loads(source[len(prefix) : -2])
    assert embedded["packet"] == packet
    assert embedded["rubric"] == _load(OUTPUT / "owner-review-rubric.json")


def test_project_vision_adds_only_the_required_representation_boundary(report: dict) -> None:
    text = (ROOT / spec063.PROJECT_VISION).read_text(encoding="utf-8")
    principle = "Intermediate representation is not learner representation. Internal schema must be compiled through a separate cognitive-utility boundary before exposure."
    assert principle in text
    assert """grounded semantics
→ explanatory structure
→ conceptual schema (IR)
→ cognitive representation compiler
→ learner representation""" in text
    # SPEC-063 retains the vision identity frozen with its completed evidence.
    # Later approved doctrine updates must not rewrite that historical packet.
    assert report["project_vision"]["sha256"] == (
        "2db3a175de328aee82dad1b463196a8660374bcdecbdbd8ab1e76c5a43257555"
    )
    assert report["project_vision"]["ambition_expanded"] is False


def test_report_stops_at_owner_review_with_zero_calls_and_no_promotion(report: dict) -> None:
    assert report["decision_branch"] == "COGNITIVE_REPRESENTATION_SAFE_FOR_OWNER_REVIEW"
    assert report["recommended_next_step"] == "OWNER_REVIEW_REQUIRED"
    assert report["status"] == "IMPLEMENTED_AWAITING_REVIEW"
    assert report["authority"] == "OFFLINE_ONLY"
    assert report["owner_review"]["state"] == "OWNER_REVIEW"
    assert report["owner_review"]["verdict"] == "PENDING"
    assert report["owner_review"]["promotion"] == "NOT_AUTHORIZED"
    assert report["owner_review"]["command"] == spec063.OWNER_COMMAND
    assert set(report["execution_integrity"].values()) == {0}
    assert report["protected_state"] == {
        "navigation_changes": 0,
        "production_representation_changes": 0,
        "production_semantic_changes": 0,
        "promotion_actions": 0,
        "spec038_changes": 0,
        "spec062_changes": 0,
    }


def test_regeneration_is_byte_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    regenerated = tmp_path / "spec063"
    original_sha = spec063._sha

    def historical_vision_sha(path: Path) -> str:
        if path.resolve() == (ROOT / spec063.PROJECT_VISION).resolve():
            return "2db3a175de328aee82dad1b463196a8660374bcdecbdbd8ab1e76c5a43257555"
        return original_sha(path)

    monkeypatch.setattr(spec063, "_sha", historical_vision_sha)
    spec063.generate(ROOT, regenerated)
    expected = {path.relative_to(OUTPUT): path.read_bytes() for path in OUTPUT.rglob("*") if path.is_file()}
    actual = {path.relative_to(regenerated): path.read_bytes() for path in regenerated.rglob("*") if path.is_file()}
    assert actual == expected
