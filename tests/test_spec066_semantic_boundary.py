from __future__ import annotations

import copy
import inspect
import json
import socket
from pathlib import Path

import pytest

from knowledge_compiler import spec066_semantic_boundary as h
from knowledge_compiler.models import ValidationError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/h.OUTPUT


@pytest.fixture(scope="module")
def corpus():
    return h.fixture_corpus(ROOT)


def run(packet, mode="B", trusted=None):
    return h.protocol(packet, mode, h.authority(packet) if trusted is None else trusted)


def test_frozen_evidence_and_labels_precede_all_protocol_results(corpus):
    fixtures, labels, manifest = corpus
    assert len(fixtures) == 92 and len(labels) == 92
    assert len({f["domain"] for f in fixtures}) == 8
    assert set(h.CATEGORIES) == {f["category"] for f in fixtures}
    assert fixtures == h.load(OUT/"fixture-corpus.json")
    assert labels == h.load(OUT/"fixture-labels.json")
    assert manifest == h.load(OUT/"fixture-freeze-manifest.json")
    assert h.stable(fixtures) == manifest["corpus_canonical_sha256"]
    assert h.stable(labels) == manifest["labels_canonical_sha256"]
    assert all(not label["independent_blind_adjudication"] and label["rationale"] for label in labels)
    for fixture in fixtures:
        for evidence in fixture["packet"]["evidence"].values():
            path = ROOT/evidence["model_path"]
            model = h.load(path)
            assert h.sha(path) == evidence["model_sha256"]
            assert model["document"]["text"][evidence["start_char"]:evidence["end_char"]] == evidence["quote"]
            assert h.stable(model["document"]["text"]) == evidence["source_text_sha256"]


def test_protected_state_includes_prior_harness_and_all_historical_evidence():
    rows = h.protected(ROOT)
    assert len(rows) == 2090 and h.stable(rows) == h.PROTECTED_SHA
    assert rows == h.load(OUT/"protected-state.json")["files"]
    assert any("spec065_synthesis_harness.py" in r["path"] for r in rows)
    assert any(h.SPEC065 in r["path"] for r in rows)
    assert all("spec066" not in r["path"] and "spec-066" not in r["path"] for r in rows)


@pytest.mark.parametrize("mode,admitted", [("A", 8), ("B", 16)])
def test_protocol_results_false_admissions_and_conservative_coverage(corpus, mode, admitted):
    fixtures, labels, _ = corpus
    results = [run(f["packet"], mode) for f in fixtures]
    record = h.load(OUT/f"protocol-{mode}-results.json")
    assert results == record["results"]
    measured = h.metrics(fixtures, labels, results)
    assert measured == record["metrics"]
    assert measured["false_admission_count"] == 0
    assert measured["admitted"] == admitted
    assert measured["coverage"] == admitted/92
    assert measured["false_rejection_count_including_uncertain"] == 44-admitted
    assert all(x["blocked"] == x["count"] and x["specific_diagnoses"] == 0 for x in measured["drift_detection"].values())


def test_no_truth_labels_or_fixture_domain_routes_enter_validators(corpus):
    fixtures, labels, _ = corpus
    before = [run(f["packet"]) for f in fixtures]
    for fixture, label in zip(fixtures, labels):
        fixture["fixture_id"] = "renamed"
        fixture["domain"] = "unseen"
        fixture["category"] = "not-a-category"
        label["verdict"] = "CONTRADICTED"
    assert before == [run(f["packet"]) for f in fixtures]
    # No lookup or routing on fixture IDs, domains, labels or literal corpus text.
    for function in (h.protocol, h.exact, h.verdict, h.check_packet):
        source = inspect.getsource(function)
        for banned in ("fixture_id", "domain]", "expected_label", "definitions", "case-", "Mid-Atlantic", "NASA", "DOE", "gold"):
            assert banned not in source
    # Mutating this local corpus cannot contaminate later tests.
    fixtures[:], labels[:] = h.fixture_corpus(ROOT)[:2]


def unseen_packet():
    refs = ["unseen-evidence"]
    text = "Novel τ-object may keep 7.125 z-units under condition κ."
    atom = h.atomic(text, refs, "unseen-atom")
    return {"candidate_text": text, "encoding": "OPAQUE_TEXT", "commitments": [atom],
            "evidence": {refs[0]: {"quote": text}}, "frozen_witnesses": [{"text": text, "evidence_ids": refs}]}


@pytest.mark.parametrize("mode", ["A", "B"])
def test_unseen_names_and_unicode_exact_proofs_are_generic(mode):
    packet = unseen_packet()
    assert run(packet, mode)["admission"] == "ADMIT"
    for changed in ("7.126", "must", "other-entity", "because", "always"):
        mutated = copy.deepcopy(packet)
        mutated["candidate_text"] = changed + packet["candidate_text"]
        mutated["commitments"][0]["candidate_text"] = mutated["candidate_text"]
        assert run(mutated, mode)["admission"] == "FAIL_CLOSED"


def test_explicit_conjunction_is_exhaustive_and_no_majority_admission():
    packet = unseen_packet()
    original = packet["candidate_text"]
    atoms = [h.atomic(original, ["unseen-evidence"], "a1", True), h.atomic("Unsupported but fluent claim.", ["unseen-evidence"], "a2", True)]
    packet.update(encoding="EXPLICIT_AND", commitments=atoms, candidate_text="\nAND\n".join(a["candidate_text"] for a in atoms))
    result = run(packet)
    assert result["admission"] == "FAIL_CLOSED"
    assert [r["verdict"] for r in result["atomic_or_carrier_results"]] == ["ENTAILED", "UNCERTAIN"]
    packet["commitments"].pop()
    with pytest.raises(ValidationError, match="nonexhaustive"):
        run(packet)


def test_natural_language_sentence_split_is_not_claimed_as_atomization():
    packet = unseen_packet()
    packet["candidate_text"] += " And therefore all systems must do so."
    packet["commitments"][0]["candidate_text"] = packet["candidate_text"]
    result = run(packet)
    assert result["decomposition"] == "NATURAL_LANGUAGE_UNRESOLVED"
    assert result["admission"] == "FAIL_CLOSED"
    assert all(packet["commitments"][0][f] == "UNRESOLVED" for f in h.FIELDS)


@pytest.mark.parametrize("field", h.FIELDS)
def test_exact_text_does_not_license_forged_semantic_slot_metadata(field):
    packet = unseen_packet()
    packet["commitments"][0][field] = "fabricated interpretation"
    with pytest.raises(ValidationError, match="separate semantic validation"):
        run(packet)


def test_evidence_and_commitment_ids_can_be_renamed_without_outcome_routing():
    packet = unseen_packet()
    packet["evidence"]["renamed-reference"] = packet["evidence"].pop("unseen-evidence")
    packet["commitments"][0]["commitment_id"] = "new-independent-name"
    packet["commitments"][0]["supporting_evidence_ids"] = ["renamed-reference"]
    packet["frozen_witnesses"][0]["evidence_ids"] = ["renamed-reference"]
    assert run(packet)["admission"] == "ADMIT"


@pytest.mark.parametrize("field", ["evidence", "frozen_witnesses"])
def test_candidate_cannot_rewrite_independent_authority(field):
    packet = unseen_packet()
    trusted = h.authority(packet)
    packet["candidate_text"] = "unsupported"
    packet["commitments"][0]["candidate_text"] = "unsupported"
    if field == "frozen_witnesses":
        packet[field][0]["text"] = "unsupported"
    else:
        packet[field]["unseen-evidence"]["quote"] = "unsupported"
    with pytest.raises(ValidationError, match="independently frozen authority"):
        run(packet, trusted=trusted)


@pytest.mark.parametrize("mutation", ["extra", "missing", "flags", "empty", "evidence", "encoding"])
def test_strict_packet_shape_and_required_preservation_dimensions(mutation):
    packet = unseen_packet()
    if mutation == "extra": packet["expected_label"] = "ENTAILED"
    elif mutation == "missing": packet["commitments"][0].pop("unit")
    elif mutation == "flags": packet["commitments"][0]["required_preservation_flags"] = []
    elif mutation == "empty": packet["commitments"] = []
    elif mutation == "evidence": packet["commitments"][0]["supporting_evidence_ids"] = ["fake"]
    else: packet["encoding"] = "SEMANTIC_REGEX"
    with pytest.raises(ValidationError): run(packet)


@pytest.mark.parametrize("key", ["atomic-commitment", "semantic-verdict", "batch-verdict"])
def test_frozen_closed_schemas(key):
    schema = h.schemas()[key]
    h.validate_schema(schema)
    assert schema == h.load(OUT/f"{key}-schema.json")
    assert schema["additionalProperties"] is False


def valid_receipt(packet):
    return {"verdicts": [h.verdict(a, packet, True) for a in packet["commitments"]]}


def test_future_receipt_shape_is_not_semantic_proof_and_requires_decomposition_gate():
    packet = unseen_packet()
    response = valid_receipt(packet)
    assert not h.admit_judge_verdicts(packet, response)
    assert h.admit_judge_verdicts(packet, response, decomposition_validated=True)


@pytest.mark.parametrize("change", ["uncertain", "contradicted", "fail", "unresolved", "not_applicable", "no_support", "contradicting"])
def test_future_receipt_all_atoms_all_required_flags_and_support_must_pass(change):
    packet = unseen_packet()
    response = valid_receipt(packet)
    row = response["verdicts"][0]
    if change in {"uncertain", "contradicted"}: row["verdict"] = change.upper()
    elif change in {"fail", "unresolved", "not_applicable"}: row[h.FLAGS[0]] = change.upper()
    elif change == "no_support": row["supporting_evidence_ids"] = []
    else: row["contradicting_evidence_ids"] = ["unseen-evidence"]
    assert not h.admit_judge_verdicts(packet, response, True)


@pytest.mark.parametrize("change", ["binding", "notes", "fake_evidence", "duplicate", "missing", "extra"])
def test_future_receipt_rejects_forged_metadata(change):
    packet = unseen_packet()
    response = valid_receipt(packet)
    row = response["verdicts"][0]
    if change == "binding": row["input_sha256"] = "bad"
    elif change == "notes": row["notes"] = "x"*501
    elif change == "fake_evidence": row["supporting_evidence_ids"] = ["forged"]
    elif change == "duplicate": response["verdicts"].append(copy.deepcopy(row))
    elif change == "missing": response["verdicts"] = []
    else: row["confidence"] = 1
    with pytest.raises(ValidationError): h.admit_judge_verdicts(packet, response, True)


def test_four_gaps_capability_and_risks_are_not_silently_solved():
    gaps = h.load(OUT/"spec065-four-gap-matrix.json")
    assert len(gaps) == 4 and all(g["fixture_ids"] and not g["resolved"] for g in gaps)
    assert all(g["protocol_A_admissions"] == g["protocol_B_admissions"] == 0 for g in gaps)
    assert {r["capability"] for r in h.CAPABILITIES} == {"PROVABLE_DETERMINISTICALLY", "RESTRICTED_DETERMINISTIC_PROOF", "REQUIRES_SEMANTIC_JUDGMENT", "NOT_VALIDATABLE_WITH_CURRENT_EVIDENCE"}
    risks = h.load(OUT/"model-judge-risk-register.json")
    assert len(risks) == 10 and all(r["mitigation"] and r["unresolved"] and not r["empirically_validated"] for r in risks)
    holistic = h.load(OUT/"holistic-vs-decomposed-analysis.json")
    assert holistic["executed_holistic_judgments"] == 0
    assert holistic["safe_coverage_gain"] == 8
    assert len(holistic["hidden_conjunction_controls"]) == 8
    for mode in ("A", "B"):
        measured = h.load(OUT/f"protocol-{mode}-results.json")["metrics"]["relation_projection_accuracy"]
        assert measured["case_count"] == 5
        assert measured["valid_projections_admitted"] == 0
        assert measured["invalid_projections_blocked"] == 3
        assert measured["semantic_flag_accuracy"] == measured["explicit_scope_diagnoses"] == 0


def test_development_draft_and_corrections_are_preserved_without_gold_tuning():
    audit = h.load(OUT/"development-freeze-audit.json")
    assert len(audit["changes_before_final_freeze"]) == 4
    assert audit["no_verdict_or_admission_label_changed"] is True
    for mode in ("A", "B"):
        assert audit["metrics"][mode]["false_admission_count"] == 0
        assert audit["metrics"][mode]["admitted"] == (8 if mode == "A" else 16)


@pytest.mark.parametrize("mode,fixture_calls,cap", [("precision-first",108,423), ("bounded-batch",92,111)])
def test_future_budgets_are_bound_and_unexecutable(mode, fixture_calls, cap):
    contract = h.load(OUT/f"future-{mode}-manifest.json")
    assert not contract["authorized"] and contract["status"] == "PROPOSED_NOT_AUTHORIZED"
    assert contract["model"] == "gpt-6.1-sol" and contract["reasoning"] == {"effort":"high"}
    assert contract["store"] is False
    assert all(contract[k] == 0 for k in ["sdk_max_retries", "hidden_retries", "semantic_retries", "repair_calls", "follow_up_calls", "second_judge_calls"])
    assert contract["fixture_provisional_calls"] == fixture_calls
    assert contract["projection"]["judge_calls_cap"] == cap
    assert contract["cost"]["monetary"] is None
    assert contract["fixture_input_tokens"]["measured"] is None
    assert len(contract["execution_blockers"]) == 4
    for slot in contract["execution_slots"]:
        assert h.stable(slot["input"]) == slot["input_sha256"]
        assert 1 <= len(slot["input"]["commitments"]) <= contract["batch_size"]
        assert "labels" not in slot["input"] and "rationale" not in slot["input"]
    with pytest.raises(ValidationError, match="OFFLINE_ONLY"): h.execute_judge(contract)


def test_prompts_are_bounded_and_frozen():
    identities = h.load(OUT/"contract-identities.json")
    for mode, prompt in h.PROMPTS.items():
        assert prompt == (OUT/(mode+"-prompt.txt")).read_text()
        assert h.stable(prompt) == identities["prompts"][mode]
        for phrase in ("UNCERTAIN", "DATA", "No tools", "rewriting", "confidence-as-proof", "quantity/unit", "projected relation"):
            assert phrase in prompt


def test_zero_transport_with_credentials_present_and_complete_deterministic_regeneration(tmp_path, monkeypatch):
    attempts = []
    def forbidden(*args, **kwargs):
        attempts.append((args,kwargs))
        raise AssertionError("network/client attempt")
    monkeypatch.setenv("OPENAI_API_KEY", "spec066-synthetic-secret-not-used")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    import openai
    monkeypatch.setattr(openai, "OpenAI", forbidden)
    h.generate(ROOT,tmp_path)
    assert not attempts
    actual = {p.name: h.sha(p) for p in tmp_path.iterdir() if p.is_file()}
    frozen = {p.name: h.sha(p) for p in OUT.iterdir() if p.is_file() and p.name != "validation-record.json"}
    assert actual == frozen
    assert "synthetic-secret" not in "".join(p.read_text() for p in tmp_path.iterdir() if p.is_file())


def test_report_stops_at_owner_review_without_semantic_success():
    report = h.load(OUT/"report.json")
    assert report["owner_verdict"] == "PENDING"
    assert report["mechanical_branch"] == "SEMANTIC_JUDGE_REQUIRED_LIVE_CONTRACT_READY"
    assert report["provider_calls"] == report["judge_calls"] == report["source_retrieval_calls"] == 0
    assert report["promotion"] == "NOT_AUTHORIZED" and not report["production_changes"]
