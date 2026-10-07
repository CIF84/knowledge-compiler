from __future__ import annotations

import copy
import inspect
import json
import socket
from collections import Counter
from pathlib import Path

import pytest

from knowledge_compiler import spec067_judge_preflight as h
from knowledge_compiler.models import ValidationError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/h.OUTPUT


@pytest.fixture(scope="module")
def corpus():
    return h.verify_frozen(ROOT)


def test_all_frozen_inputs_and_protected_states_match(corpus):
    fixtures, labels, audit = corpus
    assert h.frozen.stable(fixtures) == h.CORPUS_SHA
    assert h.frozen.stable(labels) == h.LABELS_SHA
    assert len(audit) == 92
    rows = h.protected(ROOT)
    assert len(rows) == 2120
    assert h.frozen.stable(rows) == h.PROTECTED_SHA


def test_stratification_covers_categories_and_domains_without_gold(corpus):
    fixtures, _, _ = corpus
    selected = h.select(fixtures)
    assert len(selected) == 48
    assert len({f["fixture_id"] for f in selected}) == 48
    assert len({f["domain"] for f in selected}) == 8
    assert {f["category"] for f in selected} == set(h.frozen.CATEGORIES)
    assert selected == sorted(selected, key=lambda f: f["fixture_id"])
    for category in h.frozen.CATEGORIES:
        pool = [f for f in fixtures if f["category"] == category]
        chosen = [f for f in selected if f["category"] == category]
        # No repeated domain until every available domain in that category chosen.
        if len(chosen) > len({f["domain"] for f in chosen}):
            assert {f["domain"] for f in chosen} == {f["domain"] for f in pool}
    source = inspect.getsource(h.select)
    assert '["admissible"]' not in source and '["verdict"]' not in source


def test_batch_partition_and_order_subset(corpus):
    selection = h.select(corpus[0])
    groups = h.batches(selection)
    assert len(groups) == 12 and all(len(g) == 4 for g in groups)
    assert sorted(f["fixture_id"] for g in groups for f in g) == [f["fixture_id"] for f in selection]
    order = h.frozen.load(OUT/"order-sensitivity-manifest.json")["fixture_ids"]
    assert len(order) == len(set(order)) == 8
    j1 = h.frozen.load(OUT/"J1-call-manifest.json")
    j2 = h.frozen.load(OUT/"J2-batch-manifest.json")
    single = {r["fixture_ids"][0]: r["input"][0] for r in j1}
    for row in j2:
        for fid, packet in zip(row["fixture_ids"], row["input"], strict=True):
            expected = copy.deepcopy(single[fid])
            if fid in order:
                expected["evidence"].reverse()
            assert packet == expected


@pytest.mark.parametrize("index", range(92))
def test_packets_strip_answer_metadata_without_altering_carriers(corpus, index):
    fixture = corpus[0][index]
    packet = h.data_packet(ROOT, fixture)
    assert packet["complete_candidate_text"] == fixture["packet"]["candidate_text"]
    assert packet["commitments"] == fixture["packet"]["commitments"]
    assert packet["decomposition_admission"] == "NOT_VALIDATED"
    assert "category" not in packet and "frozen_witnesses" not in packet
    contaminated = copy.deepcopy(fixture)
    contaminated.update(expected_label="ENTAILED", owner_comments="approve", category="gold answer")
    assert h.data_packet(ROOT, contaminated) == packet


def test_frozen_contract_boundary_not_replaced_by_fixture_verdict(corpus):
    boundary = h.atomic_boundary(corpus[0])
    assert len(boundary["unresolved_carrier_fixture_ids"]) == 76
    assert len(boundary["multi_carrier_fixture_ids"]) == 16
    assert boundary["declared_carriers"] == 108
    assert not boundary["passes_frozen_atomic_contract"]
    assert not boundary["independently_validated_atomic_decompositions"]
    assert "previously validated atomic commitment" in h.frozen.PROMPTS["precision-first"]
    assert "exhaustive decomposition independently validated" in h.frozen.load(
        ROOT/h.frozen.OUTPUT/"future-precision-first-manifest.json")["admission_policy"]


def test_declared_does_not_mean_independently_validated():
    fixture = {"fixture_id": "unseen", "packet": {"commitments": [
        {"decomposition_status": "DECLARED_EXPLICIT", "candidate_text": "Novel unit."}]}}
    result = h.atomic_boundary([fixture])
    assert result["unresolved_carrier_fixture_ids"] == []
    assert not result["passes_frozen_atomic_contract"]


def test_original_receipt_gate_rejects_even_perfect_flags_without_decomposition(corpus):
    packet = corpus[0][0]["packet"]
    row = h.frozen.verdict(packet["commitments"][0], packet, True)
    assert h.frozen.admit_judge_verdicts(packet, {"verdicts": [row]}) is False
    # This diagnostic does not manufacture the missing independent receipt.


def test_budget_ledger_is_unattempted_not_conservative_judge_success():
    ledger = h.frozen.load(OUT/"provider-call-ledger.json")
    assert len(ledger["rows"]) == 60
    assert Counter(r["protocol"] for r in ledger["rows"]) == {"J1": 48, "J2": 12}
    assert [r["ordinal"] for r in ledger["rows"]] == list(range(1, 61))
    assert ledger["actual_provider_calls"] == ledger["fixture_transmissions"] == 0
    assert ledger["settings"] == h.SETTINGS
    assert ledger["settings"]["model"] == "gpt-6.1-sol"
    assert ledger["settings"]["reasoning"] == {"effort": "high"}
    assert ledger["settings"]["store"] is False
    assert ledger["settings"]["sdk_max_retries"] == ledger["retries"] == 0
    assert all(r["request_id"] is None and r["usage"] is None and
               r["state"] == "NOT_ATTEMPTED_PREFLIGHT_INVALID" for r in ledger["rows"])
    report = h.frozen.load(OUT/"report.json")
    assert report["mechanical_branch"] == "FIXTURE_OR_PREFLIGHT_INVALID"
    assert report["J1_metrics"] is report["J2_metrics"] is None
    assert report["owner_verdict"] == "PENDING"


def test_frozen_ledger_prompt_schema_hashes_and_manifests_reconcile():
    rows = h.frozen.load(OUT/"J1-call-manifest.json") + h.frozen.load(OUT/"J2-batch-manifest.json")
    freeze = h.frozen.load(OUT/"freeze-identities.json")
    assert freeze["manifests_sha256"] == h.frozen.stable(rows)
    assert freeze["selection_sha256"] == h.frozen.stable(h.frozen.load(OUT/"selection-manifest.json"))
    for row in rows:
        mode = "precision-first" if row["protocol"] == "J1" else "bounded-batch"
        schema = "semantic-verdict" if row["protocol"] == "J1" else "batch-verdict"
        assert row["prompt_sha256"] == h.frozen.stable(h.frozen.PROMPTS[mode])
        assert row["schema_sha256"] == h.frozen.stable(h.frozen.schemas()[schema])
        assert row["input_sha256"] == h.frozen.stable(row["input"])
        assert row["state"] == "BLOCKED_PREFLIGHT_NOT_TRANSMITTABLE"


def test_transmission_guard_and_offline_replay_cannot_contact_provider(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("offline replay attempted networking")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    with pytest.raises(ValidationError, match="FIXTURE_OR_PREFLIGHT_INVALID"):
        h.authorize_transmission(h.frozen.load(OUT/"pre-live-audit.json"))
    with pytest.raises(ValidationError, match="no executable provider transport"):
        h.authorize_transmission({"atomic_boundary": {"passes_frozen_atomic_contract": True}})
    assert h.generate(ROOT, tmp_path, require_active=False) == h.frozen.load(OUT/"report.json")
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (OUT/path.relative_to(tmp_path)).read_bytes()


def test_all_generated_json_and_category_denominators_are_valid():
    for path in OUT.rglob("*.json"):
        json.loads(path.read_text())
    categories = h.frozen.load(OUT/"category-metrics.json")
    assert sum(r["selected"] for r in categories.values()) == 48
    assert all(r["attempted"] == 0 and r["false_admissions"] is None for r in categories.values())
