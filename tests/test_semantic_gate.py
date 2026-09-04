from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from knowledge_compiler.models import ValidationError
from knowledge_compiler.openai_semantic_gate import GATE_PROMPT_VERSION, OpenAISemanticGate, gate_response_schema
from knowledge_compiler.semantic_gate import (
    CandidateLabel, GateDecision, GatePacket, GateResult, GateVerdict,
    aggregate_gate_metrics, apply_gate_decisions, select_experimental_verdict,
    validate_packet_contracts,
)
from knowledge_compiler.semantic_gate_evaluation import (
    build_frozen_gate_packet, prepare_gate_evaluation, run_gate_evaluation,
)


ROOT = Path(__file__).parents[1]
SPEC_013 = ROOT / "examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904"
SPEC_012 = ROOT / "examples/evaluations/spec-012-staged-semantic-compilation-20260904"


def packet() -> GatePacket:
    return build_frozen_gate_packet(SPEC_013, SPEC_012)


def decisions_for(value: GatePacket, *, false_reject: str | None = None, false_admit: str | None = None):
    result = []
    for item in value.items:
        admit = item.label is CandidateLabel.POSITIVE
        if item.packet_candidate_id == false_reject:
            admit = False
        if item.packet_candidate_id == false_admit:
            admit = True
        result.append({
            "packet_candidate_id": item.packet_candidate_id,
            "verdict": "ADMIT" if admit else "WRONG_PREDICATE",
            "rationale": "The exact candidate does or does not satisfy the supplied contract.",
        })
    return result


def test_frozen_packet_uses_three_positive_and_six_independent_negative_controls() -> None:
    value = packet()
    positives = [item for item in value.items if item.label is CandidateLabel.POSITIVE]
    negatives = [item for item in value.items if item.label is CandidateLabel.NEGATIVE]
    assert len(positives) == 3
    assert len(negatives) == 6
    assert {item.expected_category for item in positives} == {"SUPPORTED"}
    assert {item.candidate.id for item in negatives} == {"r1", "r2", "r5", "r9", "r12", "r14"}
    assert {item.expected_category for item in negatives} == {
        "OVERSTATED_CAUSALITY", "WRONG_PREDICATE", "IMPRECISE_ENDPOINT"
    }
    assert all(item.assertion.evidence for item in value.items)
    assert len(value.frozen_symbol_ids) == 41


def test_packet_order_serialization_and_hash_are_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    one = prepare_gate_evaluation(SPEC_013, SPEC_012, first)
    two = prepare_gate_evaluation(SPEC_013, SPEC_012, second)
    assert one["packet_hash"] == two["packet_hash"]
    assert (first / "gate-packet.json").read_bytes() == (second / "gate-packet.json").read_bytes()
    loaded = GatePacket.from_dict(json.loads((first / "gate-packet.json").read_text()))
    assert loaded.packet_hash == one["packet_hash"]
    assert [item.packet_candidate_id for item in loaded.items] == sorted(
        item.packet_candidate_id for item in loaded.items
    )
    assert loaded.packet_hash == packet().packet_hash
    assert loaded.packet_hash == "1186a75812a32c72430c42b88cc2c9957ae6791433a51b2b310ee645f3a13ba7"


def test_gate_input_excludes_benchmark_answers_and_unrelated_source_material() -> None:
    gate_input = packet().to_gate_input()
    serialized = json.dumps(gate_input)
    assert "expected_category" not in serialized
    assert "independent_review_note" not in serialized
    assert '"label"' not in serialized
    assert "control_source" not in serialized
    assert "fallback" not in serialized
    assert "5965" not in serialized
    assert all("grounded_assertion" in item for item in gate_input["candidates"])


def test_gate_decision_vocabulary_and_no_rewrite_contract() -> None:
    with pytest.raises(ValueError):
        GateDecision("candidate", "REWRITE", "Not allowed")
    with pytest.raises(ValidationError, match="only ID, verdict, and rationale"):
        GateDecision.from_dict({
            "packet_candidate_id": "candidate", "verdict": "ADMIT",
            "rationale": "Supported.", "replacement_candidate": {},
        })
    schema = gate_response_schema(frozenset({"candidate"}))
    assert schema["properties"]["decisions"]["items"]["additionalProperties"] is False
    assert set(schema["properties"]["decisions"]["items"]["properties"]["verdict"]["enum"]) == {
        item.value for item in GateVerdict
    }


def test_gate_result_requires_exactly_one_decision_per_frozen_candidate() -> None:
    value = packet()
    raw = decisions_for(value)
    with pytest.raises(ValidationError, match="exactly once"):
        GateResult.from_dict({"decisions": raw[:-1]}, value)
    with pytest.raises(ValidationError, match="exactly once"):
        GateResult.from_dict({"decisions": [*raw, raw[0]]}, value)


def test_hard_contract_checks_reject_unknown_endpoint_without_semantic_heuristics() -> None:
    value = packet()
    item = value.items[0]
    bad_candidate = replace(item.candidate, source_entity_id="invented-symbol")
    with pytest.raises(ValidationError, match="candidate symbols must exactly match"):
        replace(item, candidate=bad_candidate)
    validate_packet_contracts(value, frozenset(value.frozen_symbol_ids))


def test_gate_demotions_preserve_lower_commitment_meaning_without_mutation() -> None:
    value = packet()
    result = GateResult.from_dict({"decisions": decisions_for(value)}, value)
    integrated = apply_gate_decisions(value, result)
    assert len(integrated["admitted"]) == 3
    assert len(integrated["demoted"]) == 6
    assert integrated["source_meaning_preserved_for_all_demotions"] is True
    assert integrated["candidate_rewrites"] == 0
    assert integrated["entities_minted"] == 0
    assert integrated["evidence_created_or_changed"] == 0
    originals = {item.packet_candidate_id: item.candidate.to_dict() for item in value.items}
    for item in integrated["demoted"]:
        assert item["rejected_candidate"] == originals[item["packet_candidate_id"]]
        assert item["preserved_as"]["kind"] in {"CLAIM", "SOURCE_ASSERTION"}
    assert next(
        item for item in integrated["demoted"] if item["packet_candidate_id"] == "negative-r2"
    )["preserved_as"]["kind"] == "SOURCE_ASSERTION"


def test_metrics_and_fixed_verdict_selection() -> None:
    value = packet()
    result = GateResult.from_dict({"decisions": decisions_for(value)}, value)
    metrics = aggregate_gate_metrics(value, result)
    assert metrics["positive_candidate_count"] == 3
    assert metrics["negative_candidate_count"] == 6
    assert metrics["true_admits"] == 3
    assert metrics["false_admits"] == 0
    assert metrics["true_rejects_or_demotions"] == 6
    assert metrics["false_rejects"] == 0
    assert metrics["admit_precision"] == 1.0
    assert metrics["justified_admission_recall"] == 1.0
    assert metrics["negative_rejection_rate"] == 1.0
    assert metrics["overall_classification_agreement"] == 1.0
    assert select_experimental_verdict(metrics) == "GATE_BETTER"
    assert select_experimental_verdict(metrics, operational_failure=True) == "INCONCLUSIVE"
    too_conservative = {**metrics, "justified_admission_recall": 1 / 3}
    assert select_experimental_verdict(too_conservative) == "GATE_TOO_CONSERVATIVE"
    unreliable = {
        **metrics, "justified_admission_recall": 2 / 3,
        "negative_rejection_rate": 0.4, "admit_precision": 0.4,
        "overall_classification_agreement": 0.5,
    }
    assert select_experimental_verdict(unreliable) == "GATE_UNRELIABLE"


class FixtureGate:
    def __init__(self, raw: list[dict[str, str]]) -> None:
        self.last_raw = {"decisions": raw}
        self.last_metadata = {}
        self.raw = raw

    def judge(self, value: GatePacket) -> GateResult:
        metadata = {
            "provider": "fixture", "requested_model": "fixture", "model": "fixture",
            "provider_request_id": "fixture-request", "prompt_version": GATE_PROMPT_VERSION,
            "store": False, "sdk_retries": 0,
            "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
        }
        self.last_metadata = metadata
        return GateResult.from_dict({"decisions": self.raw, "metadata": metadata}, value)


def test_evaluation_writes_metrics_history_and_safety_seam(tmp_path: Path) -> None:
    prepared = tmp_path / "prepared"
    prepare_gate_evaluation(SPEC_013, SPEC_012, prepared)
    value = GatePacket.from_dict(json.loads((prepared / "gate-packet.json").read_text()))
    output = tmp_path / "output"
    report = run_gate_evaluation(
        prepared / "gate-packet.json", output,
        model="fixture", gate_factory=lambda: FixtureGate(decisions_for(value)),
    )
    assert report["verdict"] == "GATE_BETTER"
    assert report["metrics"]["true_admits"] == 3
    assert report["metrics"]["true_rejects_or_demotions"] == 6
    assert report["safety"]["candidate_rewrites"] == 0
    assert report["multi_agent_deliberation"] == "NOT_JUSTIFIED"
    assert report["incremental_cost_complexity_worth_it_on_this_packet"] is True
    assert report["production_threshold_claimed"] is False
    assert set(report["verdict_rationale"]) == {
        "positive_control_retention", "negative_control_rejection", "failure_modes",
        "cost_latency", "complexity", "multi_agent_deliberation",
    }
    history = json.loads((output / "run-history.json").read_text())
    assert history["live_call_count"] == 1
    assert history["automatic_retry_count"] == 0
    assert history["hidden_retries"] is False
    assert (output / "gate-packet.json").read_bytes() == (prepared / "gate-packet.json").read_bytes()


def test_evaluation_preserves_invalid_raw_gate_output_and_failure(tmp_path: Path) -> None:
    prepared = tmp_path / "prepared"
    prepare_gate_evaluation(SPEC_013, SPEC_012, prepared)
    value = GatePacket.from_dict(json.loads((prepared / "gate-packet.json").read_text()))

    class FailingGate:
        last_raw = {"decisions": decisions_for(value)[:-1]}
        last_metadata = {
            "provider": "fixture", "requested_model": "fixture", "model": "fixture",
            "provider_request_id": "failed-request", "prompt_version": GATE_PROMPT_VERSION,
            "usage": {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110},
        }

        def judge(self, _packet: GatePacket):
            raise ValidationError("one decision missing")

    output = tmp_path / "failure"
    with pytest.raises(ValidationError, match="one decision missing"):
        run_gate_evaluation(
            prepared / "gate-packet.json", output,
            model="fixture", gate_factory=FailingGate,
        )
    preserved = json.loads((output / "gate-result.json").read_text())
    assert preserved["outcome"] == "GATE_CALL_OR_VALIDATION_FAILED"
    assert preserved["raw_proposal"] == FailingGate.last_raw
    assert json.loads((output / "report.json").read_text())["verdict"] == "INCONCLUSIVE"


def test_openai_adapter_uses_one_store_false_structured_call() -> None:
    value = packet()
    calls = []

    class Responses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                id="request-1", model="gpt-5.6-luna",
                output_text=json.dumps({"decisions": decisions_for(value)}),
                usage=SimpleNamespace(input_tokens=90, output_tokens=10, total_tokens=100),
            )

    gate = OpenAISemanticGate(model="gpt-5.6-luna", client=SimpleNamespace(responses=Responses()))
    result = gate.judge(value)
    assert len(result.decisions) == 9
    assert len(calls) == 1
    assert calls[0]["store"] is False
    assert calls[0]["model"] == "gpt-5.6-luna"
    assert calls[0]["text"]["format"]["strict"] is True
    assert "expected_category" not in calls[0]["input"]
    assert gate.last_metadata["sdk_retries"] == 0


def test_preparing_packet_does_not_change_prior_benchmark_artifacts(tmp_path: Path) -> None:
    paths = sorted(SPEC_012.glob("*")) + sorted(SPEC_013.glob("*"))
    before = {path: path.read_bytes() for path in paths if path.is_file()}
    prepare_gate_evaluation(SPEC_013, SPEC_012, tmp_path / "gate")
    after = {path: path.read_bytes() for path in paths if path.is_file()}
    assert before == after
