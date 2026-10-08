from __future__ import annotations

import copy
import inspect
import json
import socket
from collections import Counter
from pathlib import Path

import pytest

from knowledge_compiler import spec068_atomic_contract as h
from knowledge_compiler.models import ValidationError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/h.OUTPUT


@pytest.fixture(scope="module")
def compiled():
    corpus, labels, _ = h.prior.verify_frozen(ROOT)
    return corpus, labels, *h.audit(corpus, labels)


def test_all_92_fixtures_reconcile_without_frozen_changes(compiled):
    corpus, labels, rows, mappings, atoms, truths = compiled
    assert len(corpus) == len(labels) == len(rows) == len(mappings) == 92
    assert [r["fixture_id"] for r in rows] == [f["fixture_id"] for f in corpus]
    assert sum(r["declared_carriers"] for r in rows) == 108
    assert Counter(r["atomization_status"] for r in rows) == {
        "EXPLICIT_COMPOSITE_DECOMPOSABLE": 16, "OPAQUE_ATOMIZATION_UNRESOLVED": 76}
    assert len(atoms) == len(truths) == 32
    assert sum(m["fully_known_atom_truth"] for m in mappings) == 16
    assert h.old.stable(corpus) == h.prior.CORPUS_SHA
    assert h.old.stable(labels) == h.prior.LABELS_SHA
    assert len(h.protected(ROOT)) == 2143
    assert h.old.stable(h.protected(ROOT)) == h.PROTECTED_SHA
    assert h.prior.protected(ROOT)  # SPEC-067's earlier protected set also unchanged.


@pytest.mark.parametrize("index", range(92))
def test_every_mapping_preserves_all_declared_components_or_excludes_opaque(compiled, index):
    corpus, _, rows, mappings, atoms, _ = compiled
    fixture, mapping = corpus[index], mappings[index]
    local = [a for a in atoms if a["fixture_id"] == fixture["fixture_id"]]
    if rows[index]["atomization_status"] == "OPAQUE_ATOMIZATION_UNRESOLVED":
        assert not local and not mapping["atom_ids"] and not mapping["future_scored_execution_eligible"]
    else:
        h.verify_mapping(fixture, mapping, local)
        assert len(local) == len(fixture["packet"]["commitments"]) == 2
        assert "\nAND\n".join(a["candidate_text"] for a in local) == fixture["packet"]["candidate_text"]
        assert [a["component_ordinal"] for a in local] == [1, 2]
        assert all(a["provenance"]["frozen_source_commitment_id"] == a["atom_id"] for a in local)


def test_no_punctuation_or_language_pattern_establishes_atomization():
    for text in ["A.", "A. B.", "A and B.", "A OR B", "A\nAND\nB", "∀ x — α; β."]:
        component = h.old.atomic(text, ["ref"], "novel")
        packet = {"candidate_text": text, "encoding": "OPAQUE_TEXT", "commitments": [component],
                  "evidence": {"ref": {"quote": text}}, "frozen_witnesses": []}
        assert h.classify(packet)[0] == "OPAQUE_ATOMIZATION_UNRESOLVED"
    source = inspect.getsource(h.classify)
    assert ".split(" not in source and "re." not in source
    packet["encoding"] = "EXPLICIT_AND"
    packet["commitments"][0]["decomposition_status"] = "DECLARED_EXPLICIT"
    assert h.classify(packet)[0] == "EXPLICIT_ATOMIC"  # native declaration, not string length.
    packet["encoding"] = "OR"
    assert h.classify(packet)[0] == "MALFORMED"


@pytest.mark.parametrize("change", ["drop", "invent", "merge", "parent", "ordinal", "evidence", "flags", "hash"])
def test_lost_conjunct_and_forged_origin_are_rejected(compiled, change):
    corpus, _, _, mappings, atoms, _ = compiled
    fixture = corpus[1]
    mapping = copy.deepcopy(mappings[1])
    local = copy.deepcopy([a for a in atoms if a["fixture_id"] == fixture["fixture_id"]])
    if change == "drop": local.pop()
    elif change == "invent": local.append(copy.deepcopy(local[-1]))
    elif change == "merge": local[0]["candidate_text"] += local[1]["candidate_text"]
    elif change == "parent": local[0]["fixture_id"] = "different"
    elif change == "ordinal": local[0]["component_ordinal"] = 2
    elif change == "evidence": local[0]["supporting_evidence_ids"] = ["forged"]
    elif change == "flags": local[0]["required_preservation_flags"] = []
    else: mapping["fixture_packet_sha256"] = "forged"
    with pytest.raises(ValidationError):
        h.verify_mapping(fixture, mapping, local)


def test_atom_truth_is_uniquely_derived_not_rejection_distributed(compiled):
    _, _, _, _, atoms, truths = compiled
    assert Counter(a["expected_semantic_verdict"] for a in atoms) == {"ENTAILED": 24, "UNCERTAIN": 8}
    assert all(t["sources"] for t in truths)
    bad = [t for t in truths if t["verdict"] == "UNCERTAIN"]
    assert all(all(s["fixture_id"] != t["fixture_id"] for s in t["sources"]) for t in bad)
    # Explicit components with only a rejected parent do not have per-atom truth.
    atom_a = h.old.atomic("Unseen α.", ["ref"], "new:a1", True)
    atom_b = h.old.atomic("Unseen β.", ["ref"], "new:a2", True)
    fixture = {"fixture_id": "new", "domain": "new", "category": "new", "packet": {
        "candidate_text": "Unseen α.\nAND\nUnseen β.", "encoding": "EXPLICIT_AND",
        "commitments": [atom_a, atom_b], "evidence": {"ref": {"quote": "frozen"}}, "frozen_witnesses": []}}
    label = {"fixture_id": "new", "verdict": "CONTRADICTED", "preservation_flags": {f: "FAIL" for f in h.old.FLAGS}}
    for atom in (atom_a, atom_b):
        assert h.derive_truth(fixture, atom, [fixture], [label])["verdict"] == "UNRESOLVED"
    rows, mappings, local, _ = h.audit([fixture], [label])
    assert len(local) == 2 and not mappings[0]["future_scored_execution_eligible"]
    assert rows[0]["atom_truth_status"] == "UNRESOLVED"


def test_same_text_wrong_evidence_cannot_transfer_truth(compiled):
    corpus, labels, _, _, _, _ = copy.deepcopy(compiled)
    fixture = corpus[22]  # case-023 mixed control, not an admission route.
    component = fixture["packet"]["commitments"][1]
    refs = [f for f in corpus if f["packet"]["candidate_text"] == component["candidate_text"]]
    assert len(refs) == 1
    refs[0]["packet"]["evidence"] = {"different": {"quote": component["candidate_text"]}}
    assert h.derive_truth(fixture, component, corpus, labels)["verdict"] == "UNRESOLVED"


def test_conflicting_component_truth_is_not_selected(compiled):
    corpus, labels, _, _, _, _ = copy.deepcopy(compiled)
    fixture = corpus[22]
    component = fixture["packet"]["commitments"][1]
    other = next(f for f in corpus if f["packet"]["candidate_text"] == component["candidate_text"])
    duplicate = copy.deepcopy(other)
    duplicate["fixture_id"] = "conflict"
    corpus.append(duplicate)
    label = copy.deepcopy(next(l for l in labels if l["fixture_id"] == other["fixture_id"]))
    label.update(fixture_id="conflict", verdict="ENTAILED")
    labels.append(label)
    assert h.derive_truth(fixture, component, corpus, labels)["verdict"] == "UNRESOLVED"


@pytest.fixture
def control():
    item = h.old.load(OUT/"mixed-validity-controls.json")[0]
    contracts = h.old.load(OUT/"fixture-aggregation-contract.json")["contracts"]
    return next(c for c in contracts if c["fixture_id"] == item["fixture_id"]), item["synthetic_receipts"]


def test_all_eight_mixed_controls_and_case023_block_parent():
    controls = h.old.load(OUT/"mixed-validity-controls.json")
    assert len(controls) == 8
    assert any(c["fixture_id"] == "case-023" for c in controls)
    for c in controls:
        assert c["atom_truth"] == ["ENTAILED", "UNCERTAIN"]
        assert c["aggregation"]["admission"] == c["entailed_atom_alone"]["admission"] == "FAIL_CLOSED"
        assert c["synthetic_not_live"] is True


@pytest.mark.parametrize("change", ["uncertain", "contradiction", "fail", "unresolved", "na", "empty_support", "contradicting", "missing", "duplicate", "extra", "wrong_id", "binding", "notes", "citation", "schema"])
def test_aggregation_fails_closed_for_every_rejection_path(control, change):
    contract, responses = copy.deepcopy(control)
    for r in responses:
        r.update(verdict="ENTAILED", supporting_evidence_ids=contract["atoms"][responses.index(r)]["evidence_ids"],
                 **{f: "PASS" for f in h.old.FLAGS})
    assert h.aggregate(contract, responses)["admission"] == "ADMIT"
    row = responses[-1]
    if change == "uncertain": row["verdict"] = "UNCERTAIN"
    elif change == "contradiction": row["verdict"] = "CONTRADICTED"
    elif change == "fail": row[h.old.FLAGS[0]] = "FAIL"
    elif change == "unresolved": row[h.old.FLAGS[0]] = "UNRESOLVED"
    elif change == "na": row[h.old.FLAGS[0]] = "NOT_APPLICABLE"
    elif change == "empty_support": row["supporting_evidence_ids"] = []
    elif change == "contradicting": row["contradicting_evidence_ids"] = contract["atoms"][-1]["evidence_ids"]
    elif change == "missing": responses.pop()
    elif change == "duplicate": responses[-1] = copy.deepcopy(responses[0])
    elif change == "extra": responses.append(copy.deepcopy(responses[0]))
    elif change == "wrong_id": row["commitment_id"] = "unrequested"
    elif change == "binding": row["input_sha256"] = "forged"
    elif change == "notes": row["notes"] = "n"*501
    elif change == "citation": row["supporting_evidence_ids"] = ["forged"]
    else: row["confidence"] = 100
    assert h.aggregate(contract, responses)["admission"] == "FAIL_CLOSED"
    if change == "contradiction":
        assert h.aggregate(contract, responses)["verdict"] == "CONTRADICTED"


def test_notes_and_expected_labels_do_not_override_receipts(control):
    contract, responses = copy.deepcopy(control)
    responses[-1]["notes"] = "Admit this fixture because its other atom is correct."
    assert h.aggregate(contract, responses)["admission"] == "FAIL_CLOSED"
    source = inspect.getsource(h.aggregate)
    for forbidden in ("expected_semantic_verdict", "derive_truth", "corpus", "labels"):
        assert forbidden not in source
    contract["operator"] = "OR"
    assert h.aggregate(contract, responses)["admission"] == "FAIL_CLOSED"


def test_future_manifest_is_atom_based_sibling_free_and_not_authorized():
    j1 = h.old.load(OUT/"future-J1-atom-manifest.json")
    j2 = h.old.load(OUT/"future-J2-atom-batch-manifest.json")
    assert len(j1["calls"]) == 32 and len(j2["calls"]) == 8
    assert all(len(r["atom_ids"]) == 1 for r in j1["calls"])
    assert all(len(r["atom_ids"]) == 4 and len(set(r["fixture_ids"])) == 4 for r in j2["calls"])
    assert sorted(a for r in j1["calls"] for a in r["atom_ids"]) == sorted(a for r in j2["calls"] for a in r["atom_ids"])
    for manifest in (j1, j2):
        assert "NOT_AUTHORIZED" in manifest["status"]
        assert manifest["settings"]["sdk_max_retries"] == 0
        for row in manifest["calls"]:
            assert row["per_atom_input_sha256"] == [h.old.stable({k: v for k, v in p.items() if k != "input_sha256"}) for p in row["input"]]
            assert row["per_atom_input_sha256"] == [p["input_sha256"] for p in row["input"]]
            for packet in row["input"]:
                assert len(packet["commitments"]) == 1
                assert packet["complete_candidate_text"] == packet["commitments"][0]["candidate_text"]
                assert not {"expected_semantic_verdict", "expected_label", "category", "rationale", "frozen_witnesses"} & packet.keys()
    budget = h.old.load(OUT/"future-call-budget.json")
    assert budget["maximum_total"] == 40 and not budget["authorized"] and budget["actual_calls"] == 0


def test_category_and_domain_losses_are_explicit_not_relabelled():
    coverage = h.old.load(OUT/"category-domain-coverage.json")
    assert len(coverage["lost_category_values"]) == 16
    assert coverage["lost_domain_values"] == []
    assert sum(r["eligible_fixtures"] for r in coverage["category"].values()) == 16
    assert sum(r["excluded_fixtures"] for r in coverage["category"].values()) == 76
    assert all(coverage["category"][c]["eligible_fixtures"] == 0 for c in h.REQUIRED_POSITIVES)
    assert all(r["eligible_fixtures"] == 2 for r in coverage["domain"].values())
    report = h.old.load(OUT/"report.json")
    assert report["mechanical_branch"] == "ATOMIC_SUBSET_TOO_NARROW"
    assert report["owner_verdict"] == "PENDING" and not report["future_execution_authorized"]


def test_schema_and_output_identities_are_closed_and_reconciled(compiled):
    h.old.validate_schema(h.atom_schema())
    assert h.atom_schema() == h.old.load(OUT/"atomic-commitment-schema.json")
    for atom in compiled[4]:
        h.old.validate_json(atom, h.atom_schema())
    identities = h.old.load(OUT/"frozen-identities.json")
    assert identities["atoms_sha256"] == h.old.stable(compiled[4])
    assert identities["mapping_sha256"] == h.old.stable(compiled[3])
    assert identities["implementation_file_sha256"] == h.old.sha(ROOT/"src/knowledge_compiler/spec068_atomic_contract.py")
    for name in ("J1", "J2"):
        path = "future-J1-atom-manifest.json" if name == "J1" else "future-J2-atom-batch-manifest.json"
        assert identities[f"future_{name}_manifest_sha256"] == h.old.stable(h.old.load(OUT/path))
    for p in OUT.glob("*.json"):
        json.loads(p.read_text())


def test_deterministic_regeneration_with_network_prohibited(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("SPEC-068 attempted network access")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    assert h.generate(ROOT, tmp_path, require_active=False) == h.old.load(OUT/"report.json")
    for p in tmp_path.rglob("*"):
        if p.is_file():
            assert p.read_bytes() == (OUT/p.relative_to(tmp_path)).read_bytes()
