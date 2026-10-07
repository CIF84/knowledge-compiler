from __future__ import annotations

import copy
import inspect
import json
from collections import Counter
from pathlib import Path

import pytest

from knowledge_compiler import spec064_abstraction_diagnostic as diagnostic
from knowledge_compiler.models import ValidationError


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / diagnostic.OUTPUT_DIR


@pytest.fixture(scope="module")
def packet():
    return [(diagnostic.load(OUTPUT / "substrates" / f"{i:02d}.json"),
             diagnostic.load(OUTPUT / "cases" / f"{i:02d}.json")) for i in range(1, 4)]


def test_every_historical_implementation_and_evidence_file_is_byte_identical():
    rows = diagnostic.check_frozen(ROOT)
    manifest = diagnostic.load(OUTPUT / "manifest.json")
    assert len(rows) == 2016
    assert rows == manifest["protected_files"]
    assert diagnostic.stable(rows) == diagnostic.PROTECTED_SHA256
    assert diagnostic.sha(ROOT / diagnostic.EXPERIMENT_SOURCE) == manifest["implementation"]["sha256"]


def test_frozen_corpus_substrates_are_exact_independent_copies(packet):
    frozen = diagnostic._frozen_cases(ROOT)
    for (sub, case), original in zip(packet, frozen, strict=True):
        assert sub == diagnostic.make_substrate(ROOT, original)
        assert case["substrate_sha256"] == diagnostic.stable(sub)
        assert sub["schema"] == original["conceptual_schema_model"]
        assert sub["semantic_items"] == original["semantic_items"]
        assert sub["explanatory_structure"] == original["frozen_explanatory_structure"]
    assert sum(len(s["semantic_items"]) for s, _ in packet) == 141
    assert sum(len(s["material_implications"]) for s, _ in packet) == 54


def test_r0_source_and_every_text_file_are_exact(packet):
    for i, (sub, case) in enumerate(packet, 1):
        assert case["stages"][0]["text"] == sub["source_text"]
        for stage in case["stages"]:
            assert (OUTPUT / "views" / f"{i:02d}-{stage['resolution']}.txt").read_text() == stage["text"]


def test_every_stage_independently_validates_and_recovers_every_frozen_item(packet):
    for sub, case in packet:
        for index, stage in enumerate(case["stages"]):
            prior = case["stages"][index-1] if index else None
            ledger = diagnostic.validate_stage(sub, stage, prior)
            assert ledger == case["preservation_ledgers"][stage["resolution"]]
            semantic = [r for r in ledger if r["category"] == "SEMANTIC_COMMITMENT"]
            assert {r["frozen_id"] for r in semantic} == {i["upstream_id"] for i in sub["semantic_items"]}
            implications = [r for r in ledger if r["category"] == "MATERIAL_IMPLICATION"]
            assert len(implications) == len(sub["material_implications"])
            for row in ledger:
                recovered = diagnostic.recover(sub, row)
                assert recovered
                if row["category"] == "SEMANTIC_COMMITMENT":
                    assert recovered["statement"] == row["statement"]
                    assert recovered["epistemic_status"] == row["epistemic_status"]
                    assert recovered["qualification_links"] == row["qualification_links"]
                    assert recovered["evidence"] == row["evidence"]
                for field in ("qualification", "implication", "dependency"):
                    if field in row:
                        assert recovered == row[field]


def test_truthful_subsumption_does_not_require_independent_restatement(packet):
    for sub, case in packet:
        r2 = case["stages"][2]
        semantic = [r for r in case["preservation_ledgers"]["R2"] if r["category"] == "SEMANTIC_COMMITMENT"]
        assert len(r2["units"]) < len(semantic)
        assert "SUBSUMED" in {r["mode"] for r in semantic}
        assert any(item["statement"] not in r2["text"] for item in sub["semantic_items"])
        assert all(r["carrier_ids"] and r["evidence"] and r["recovery_pointer"] for r in semantic)


def test_all_three_modes_have_real_carriers(packet):
    rows = [r for _,c in packet for ledger in c["preservation_ledgers"].values() for r in ledger]
    assert {r["mode"] for r in rows} == diagnostic.MODES
    assert all(r["proof_rule"] and r["carrier_ids"] for r in rows)
    for sub, case in packet:
        for stage in case["stages"]:
            ids = {u["id"] for u in stage["units"]}
            assert all(set(r["carrier_ids"]) <= ids for r in case["preservation_ledgers"][stage["resolution"]])


def test_qualifications_are_carried_by_the_qualified_assertions_not_headings(packet):
    for sub, case in packet:
        expected = sum(len(i["qualification_links"]) for i in sub["semantic_items"])
        block_expected = sum(len(b["qualifications"]) for b in sub["explanatory_structure"]["blocks"])
        for ledger in case["preservation_ledgers"].values():
            assert sum(r["category"] == "QUALIFICATION" for r in ledger) == expected
            assert sum(r["category"] == "EXPLANATORY_QUALIFICATION" for r in ledger) == block_expected
            assert all(r["carrier_ids"] for r in ledger if "QUALIFICATION" in r["category"])


def test_r1_preserves_rejected_cost_outcomes_and_chooses_smallest_safe_candidate(packet):
    for sub, case in packet:
        r1 = case["stages"][1]
        candidates = r1["candidate_audit"]
        assert len(candidates) == 2
        assert sum(c["selected"] for c in candidates) == 1
        selected = next(c for c in candidates if c["selected"])
        assert selected["words"] == min(c["words"] for c in candidates)
        assert selected["words"] <= len(sub["source_text"].split())
        assert all(c["preservation_validated"] for c in candidates)
        for candidate in candidates:
            assert diagnostic.stable(candidate["candidate_artifact"]) == candidate["candidate_sha256"]
            diagnostic.validate_stage(sub, candidate["candidate_artifact"], case["stages"][0])
    assert any(not c["selected"] and c["words"] > len(s["source_text"].split()) for s,case in packet for c in case["stages"][1]["candidate_audit"])


def test_duplicate_collapse_never_merges_different_qualifications_or_certainty(packet):
    sub, _ = packet[0]
    item = sub["semantic_items"][0]
    changed = copy.deepcopy(item)
    assert diagnostic.statement_key(changed) == diagnostic.statement_key(item)
    changed["epistemic_status"] = "CERTAIN"
    assert diagnostic.statement_key(changed) != diagnostic.statement_key(item)
    changed = copy.deepcopy(item)
    changed["qualification_links"] = []
    assert diagnostic.statement_key(changed) != diagnostic.statement_key(item)


def test_synthesis_declares_grounding_scope_implications_and_composition(packet):
    for sub, case in packet:
        for u in case["stages"][2]["units"]:
            assert u["text"] == sub["source_text"][u["start_char"]:u["end_char"]]
            assert u["item_ids"] == [c["upstream_id"] for c in u["preserved_commitments"]]
            assert u["distinct_commitment_count"] >= 0
            assert u["why_more_than_shorter_wording"]
            assert u["preceding_unit_ids"] or not u["item_ids"]
            if u["distinct_commitment_count"] > 1:
                assert u["synthesis_relationship"] == "COEXPRESSED_IN_SAME_EXACT_SOURCE_ASSERTION"
                assert u["synthesis_kind"] == "SOURCE_ASSERTION_INTEGRATION"


@pytest.mark.parametrize("case_index", range(3))
def test_twelve_negative_controls_fail_closed_and_are_preserved(packet, case_index):
    sub, case = packet[case_index]
    results = diagnostic.negative_controls(sub, case)
    assert len(results) == 12
    assert all(r["result"] == "REJECTED_AS_REQUIRED" and r["failure"] for r in results)
    assert results == diagnostic.load(OUTPUT / "negative-controls.json")[case_index]["controls"]


def test_grouping_and_labels_earn_no_abstraction_or_hidden_unit_credit(packet):
    for sub, case in packet:
        for handle in case["stages"][3]["handles"]:
            assert diagnostic.classify_handle(sub, handle) in {"SUPPORTED_GROUPING_ONLY", "LABEL_ONLY"}
            assert handle["abstraction_unit_reduction"] == 0
            assert handle["initially_hidden_semantic_items"] == 0
            assert handle["definition_evidence"]
            assert handle["shared_principle"] is None
        assert case["measurements"][3]["explanatory_abstraction_count"] == 0


def test_labels_shared_entities_and_roles_are_not_a_membership_explanation(packet):
    sub, case = packet[0]
    isolated = copy.deepcopy(sub)
    for chunk in isolated["schema"]["chunks"]:
        chunk["membership_audit"] = []
    handle = case["stages"][3]["handles"][0]
    assert diagnostic.classify_handle(isolated, handle) == "LABEL_ONLY"
    unsupported = copy.deepcopy(handle)
    unsupported["definition"] += " Therefore every member always obeys the same rule."
    assert diagnostic.classify_handle(sub, unsupported) == "UNSUPPORTED"


def test_prior_artifact_cannot_replace_authoritative_substrate(packet):
    sub, case = packet[0]
    altered = copy.deepcopy(case["stages"][1])
    altered["units"][0]["text"] = "Invented certainty."
    altered["text"] = altered["text"].replace(case["stages"][1]["units"][0]["text"], "Invented certainty.")
    with pytest.raises(ValidationError):
        diagnostic.build_r2(sub, altered)
    r2 = copy.deepcopy(case["stages"][2])
    r2["units"][0]["text"] = "Invented certainty."
    r2["text"] = "\n\n".join(u["text"] for u in r2["units"])
    r3 = copy.deepcopy(case["stages"][3])
    r3["composition"]["preceding_artifact_sha256"] = diagnostic.stable(r2)
    with pytest.raises(ValidationError):
        diagnostic.build_r3(sub, r2)


def test_duplicate_carrier_identity_is_rejected(packet):
    sub, case = packet[0]
    stage = copy.deepcopy(case["stages"][2])
    stage["units"][1]["id"] = stage["units"][0]["id"]
    with pytest.raises(ValidationError, match="ambiguous carrier"):
        diagnostic.validate_stage(sub, stage, case["stages"][1])


def test_structural_path_is_frozen_discourse_not_invented_domain_causality(packet):
    for sub, case in packet:
        paths = case["stages"][3]["structures"]
        for path, frozen in zip(paths, sub["explanatory_structure"]["traversal"], strict=True):
            assert path["relation"] == frozen["discourse_relation"]
            assert path["from_block"] == frozen["from_block"]
            assert path["to_block"] == frozen["to_block"]
            assert path["text"] in case["stages"][3]["text"]
        assert "not a new causal assertion" in case["stages"][3]["text"]


def test_measurements_count_actual_language_and_modes_instead_of_recovered_ids(packet):
    rows = []
    for sub, case in packet:
        for stage, measure in zip(case["stages"], case["measurements"], strict=True):
            assert measure == diagnostic.metrics(sub, stage, case["preservation_ledgers"][stage["resolution"]])
            assert measure["word_count"] == len(stage["text"].split())
            assert measure["character_count"] == len(stage["text"])
            assert sum(measure["commitment_preservation_modes"].values()) == len(sub["semantic_items"])
            assert sum(measure["implication_preservation_modes"].values()) == len(sub["material_implications"])
            rows.append(measure)
    for aggregate in diagnostic.load(OUTPUT / "aggregate-measurements.json"):
        selected = [r for r in rows if r["resolution"] == aggregate["resolution"]]
        for field in ("word_count", "character_count", "explicit_learner_facing_unit_count", "material_implications", "atomic_semantic_commitments_covered", "supported_grouping_only_count"):
            assert aggregate[field] == sum(r[field] for r in selected)


def test_architecture_gate_is_evidence_driven_and_never_authorizes_live_calls(packet):
    cases = [c for _,c in packet]
    gate = diagnostic.architecture_gate(cases)
    assert gate == diagnostic.load(OUTPUT / "architecture-decision.json")
    assert gate["finding"] == "BOUNDED_MODEL_CANDIDATE_REQUIRES_SEPARATE_AUTHORIZATION"
    assert gate["substrate_insufficiency_proven"] is False
    assert gate["model_call_authorized"] is False
    assert gate["human_verdict"] == "PENDING"
    changed = copy.deepcopy(cases)
    changed[0]["measurements"][3]["explanatory_abstraction_count"] = 1
    assert diagnostic.architecture_gate(changed)["finding"] == "INCONCLUSIVE"
    for case in changed:
        case["measurements"][3]["explanatory_abstraction_count"] = 1
        case["measurements"][3]["word_count"] = case["measurements"][0]["word_count"]-1
        case["measurements"][2]["explicit_learner_facing_unit_count"] = case["measurements"][1]["explicit_learner_facing_unit_count"]-1
    assert diagnostic.architecture_gate(changed)["finding"] == "DETERMINISTIC_COMPILATION_ADEQUATE"


def test_compiler_has_no_source_domain_case_expected_answer_or_network_routing():
    source = "\n".join(inspect.getsource(f) for f in (diagnostic.build_r0, diagnostic.build_r1, diagnostic.build_r2, diagnostic.build_r3, diagnostic.classify_handle, diagnostic.validate_stage, diagnostic.architecture_gate)).lower()
    for forbidden in ("geology", "astronomy", "meteorology", "magma", "nebula", "jet stream", "usgs", "nasa", "noaa", "source_identity", "case_identity", "owner_anchor", "r14", "r15"):
        assert forbidden not in source
    module = inspect.getsource(diagnostic)
    for forbidden in ("import openai", "import requests", "urlopen", "http.client", "urllib", "cua", "playwright"):
        assert forbidden not in module


def test_artifact_inventory_json_text_links_and_secrets_are_valid(packet):
    report = diagnostic.load(OUTPUT / "report.json")
    assert report["artifact_identities"] == diagnostic.artifact_rows(OUTPUT)
    assert all(v == 0 for v in report["execution_integrity"].values())
    for path in OUTPUT.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        assert "\x00" not in text
        assert "sk-proj-" not in text and "sk-ant-" not in text and "OPENAI_API_KEY=" not in text
        if path.suffix == ".json":
            json.loads(text)
    review = (OUTPUT / "owner-review.md").read_text()
    for i in range(1,4):
        assert f"cases/{i:02d}.json" in review
        assert f"substrates/{i:02d}.json" in review
    assert all(review.count(f"### {r}") == 3 for r in ("R0", "R1", "R2", "R3"))
    assert "Owner verdict: PENDING" in review


def test_full_deterministic_regeneration_includes_receipts_and_report(tmp_path):
    diagnostic.generate(ROOT, tmp_path)
    original = {p.relative_to(OUTPUT).as_posix(): p.read_bytes() for p in OUTPUT.rglob("*") if p.is_file()}
    regenerated = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert regenerated == original
    receipt = diagnostic.load(tmp_path / "deterministic-regeneration.json")
    assert receipt["result"] == "PASS"
    assert receipt["compared_core_tree_sha256"] == diagnostic.stable(diagnostic.artifact_rows(tmp_path, core_only=True))
