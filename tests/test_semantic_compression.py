from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from knowledge_compiler.models import ValidationError
from knowledge_compiler.openai_semantic_compression import (
    COMPRESSION_PROMPT_VERSION,
    OpenAISemanticCompressionJudge,
    compression_response_schema,
)
from knowledge_compiler.semantic_compression import (
    EXPECTED_SOURCE_PACKET_SHA256,
    CompressionDecision,
    CompressionLabel,
    CompressionResult,
    CompressionVerdict,
    aggregate_compression_metrics,
    load_frozen_benchmark,
    select_compression_experiment_verdict,
    validate_blinded_packet,
    validate_historical_evidence,
)
from knowledge_compiler.semantic_compression_evaluation import (
    prepare_compression_evaluation,
    run_compression_evaluation,
)


ROOT = Path(__file__).parents[1]
PACKET = ROOT / (
    "examples/evaluations/review-003-endpoint-role-benchmark-20260904/"
    "endpoint-role-packet.json"
)


def benchmark():
    return load_frozen_benchmark(PACKET)


def decisions_for(value, *, false_reject: str | None = None, false_admit: str | None = None):
    decisions = []
    for item in value.cases:
        adequate = item.label is CompressionLabel.ROLE_ADEQUATE
        if item.blind_id == false_reject:
            adequate = False
        if item.blind_id == false_admit:
            adequate = True
        decisions.append({
            "case_id": item.blind_id,
            "verdict": "BINARY_ADEQUATE" if adequate else "TARGET_ROLE_INADEQUATE",
            "rationale": "The proposed endpoints do or do not fill the supplied predicate roles.",
        })
    return decisions


def test_frozen_packet_sha_counts_and_opaque_ids() -> None:
    value = benchmark()
    assert hashlib.sha256(PACKET.read_bytes()).hexdigest() == EXPECTED_SOURCE_PACKET_SHA256
    assert value.source_sha256 == EXPECTED_SOURCE_PACKET_SHA256
    assert len(value.cases) == 10
    assert sum(item.label is CompressionLabel.ROLE_ADEQUATE for item in value.cases) == 5
    assert sum(item.label is CompressionLabel.ROLE_INADEQUATE for item in value.cases) == 5
    assert value.case_ids == frozenset(f"endpoint-role-{index:03d}" for index in range(1, 11))


def test_historical_candidate_evidence_contract_symbol_and_provenance_integrity() -> None:
    result = validate_historical_evidence(benchmark(), ROOT)
    assert result["case_count"] == 10
    assert result["positive_case_count"] == 5
    assert result["negative_case_count"] == 5
    assert result["evidence_spans_preserved"] is True
    assert result["historical_candidates_preserved"] is True
    assert result["predicate_contracts_preserved"] is True
    assert result["symbol_identity_integrity"] is True
    assert result["provenance_paths_exist"] is True


def test_blinded_packet_uses_only_fixed_model_facing_projection() -> None:
    value = benchmark()
    blinded = value.to_blinded_dict()
    validate_blinded_packet(blinded, value)
    serialized = json.dumps(blinded)
    assert set(blinded) == {"protocol_version", "cases"}
    assert [item["case_id"] for item in blinded["cases"]] == sorted(value.case_ids)
    assert all(set(item) == {
        "case_id", "grounded_assertion", "symbols", "candidate_relationship",
        "predicate_contract",
    } for item in blinded["cases"])
    assert all(set(item["candidate_relationship"]) == {
        "source_entity_id", "relationship_type", "target_entity_id"
    } for item in blinded["cases"])
    for forbidden in (
        "ROLE_ADEQUATE", "ROLE_INADEQUATE", "historical_classification",
        "defect_family", "provenance", "positive_control_reason",
        "negative-pauli-constrains-electron", "candidate_rewrites",
    ):
        assert forbidden not in serialized


def test_blinding_validation_rejects_label_or_candidate_description_leakage() -> None:
    value = benchmark()
    leaked_label = copy.deepcopy(value.to_blinded_dict())
    leaked_label["cases"][0]["label"] = "ROLE_INADEQUATE"
    with pytest.raises(ValidationError, match="blinded case fields"):
        validate_blinded_packet(leaked_label, value)
    leaked_statement = copy.deepcopy(value.to_blinded_dict())
    leaked_statement["cases"][0]["candidate_relationship"]["statement"] = "revealing"
    with pytest.raises(ValidationError, match="candidate must contain only"):
        validate_blinded_packet(leaked_statement, value)


def test_packet_sha_validation_fails_closed_before_parsing_modified_packet(tmp_path: Path) -> None:
    changed = tmp_path / "packet.json"
    changed.write_bytes(PACKET.read_bytes() + b"\n")
    with pytest.raises(ValidationError, match="SHA-256 mismatch"):
        load_frozen_benchmark(changed)


def test_decision_vocabulary_and_no_rewrite_output_contract() -> None:
    with pytest.raises(ValueError):
        CompressionDecision("endpoint-role-001", "REWRITE", "Not allowed")
    with pytest.raises(ValidationError, match="only case_id, verdict, and rationale"):
        CompressionDecision.from_dict({
            "case_id": "endpoint-role-001",
            "verdict": "BINARY_ADEQUATE",
            "rationale": "Supported.",
            "replacement_candidate": {},
        })
    schema = compression_response_schema(frozenset({"endpoint-role-001"}))
    item = schema["properties"]["decisions"]["items"]
    assert item["additionalProperties"] is False
    assert set(item["properties"]["verdict"]["enum"]) == {
        verdict.value for verdict in CompressionVerdict
    }


def test_result_requires_one_valid_decision_per_case() -> None:
    value = benchmark()
    raw = decisions_for(value)
    result = CompressionResult.from_dict({"decisions": raw}, value.case_ids)
    assert len(result.decisions) == 10
    with pytest.raises(ValidationError, match="exactly once"):
        CompressionResult.from_dict({"decisions": raw[:-1]}, value.case_ids)
    with pytest.raises(ValidationError, match="exactly once"):
        CompressionResult.from_dict({"decisions": [*raw, raw[0]]}, value.case_ids)
    unknown = [*raw[:-1], {**raw[-1], "case_id": "unknown"}]
    with pytest.raises(ValidationError, match=r"unknown=\['unknown'\]"):
        CompressionResult.from_dict({"decisions": unknown}, value.case_ids)
    bad = copy.deepcopy(raw)
    bad[0]["verdict"] = "UNKNOWN"
    with pytest.raises(ValueError):
        CompressionResult.from_dict({"decisions": bad}, value.case_ids)


def test_metrics_cover_cases_predicates_families_and_trivial_strategies() -> None:
    value = benchmark()
    result = CompressionResult.from_dict({"decisions": decisions_for(value)}, value.case_ids)
    metrics = aggregate_compression_metrics(value, result)
    assert metrics["true_adequate_admits"] == 5
    assert metrics["false_adequate_admits"] == 0
    assert metrics["true_inadequate_rejects"] == 5
    assert metrics["false_inadequate_rejects"] == 0
    assert metrics["adequate_admission_precision"] == 1.0
    assert metrics["adequate_admission_recall"] == 1.0
    assert metrics["negative_rejection_rate"] == 1.0
    assert metrics["overall_agreement"] == 1.0
    assert set(metrics["per_predicate"]) == {
        "BINDS_TO", "CAUSES", "CONSTRAINS", "ENABLES", "PART_OF", "TRANSFERS_TO"
    }
    assert set(metrics["per_family"]) == {"CAUSAL", "DEPENDENCY", "INTERACTION", "STRUCTURAL"}
    assert metrics["trivial_strategy_checks"]["blanket_rejection"] is False
    assert metrics["trivial_strategy_checks"]["all_positive_controls_include_dropped_context"] is True
    assert select_compression_experiment_verdict(metrics) == "COMPRESSION_JUDGE_BETTER"


def test_verdict_thresholds_are_frozen_and_blanket_rejection_has_no_signal() -> None:
    value = benchmark()
    positives = sorted(
        item.blind_id for item in value.cases
        if item.label is CompressionLabel.ROLE_ADEQUATE
    )
    negatives = sorted(
        item.blind_id for item in value.cases
        if item.label is CompressionLabel.ROLE_INADEQUATE
    )
    one_error = CompressionResult.from_dict({
        "decisions": decisions_for(value, false_admit=negatives[0])
    }, value.case_ids)
    assert select_compression_experiment_verdict(
        aggregate_compression_metrics(value, one_error)
    ) == "COMPRESSION_JUDGE_BETTER"
    two_errors = decisions_for(value, false_admit=negatives[0])
    for item in two_errors:
        if item["case_id"] == positives[0]:
            item["verdict"] = "TARGET_ROLE_INADEQUATE"
    mixed = CompressionResult.from_dict({"decisions": two_errors}, value.case_ids)
    assert select_compression_experiment_verdict(
        aggregate_compression_metrics(value, mixed)
    ) == "MIXED"
    reject_all = CompressionResult.from_dict({
        "decisions": [
            {**item, "verdict": "INSUFFICIENT_FOR_BINARY_RELATIONSHIP"}
            for item in decisions_for(value)
        ]
    }, value.case_ids)
    assert select_compression_experiment_verdict(
        aggregate_compression_metrics(value, reject_all)
    ) == "NO_MEANINGFUL_SIGNAL"
    assert select_compression_experiment_verdict({}, operational_failure=True) == "INCONCLUSIVE"


class FixtureJudge:
    def __init__(self, raw: list[dict[str, str]]) -> None:
        self.raw = raw
        self.last_raw = {"decisions": raw}
        self.last_output_text = json.dumps(self.last_raw)
        self.last_metadata = {}

    def judge(self, _blinded, expected_case_ids):
        metadata = {
            "provider": "fixture",
            "requested_model": "fixture",
            "model": "fixture",
            "provider_request_id": "fixture-request",
            "prompt_version": COMPRESSION_PROMPT_VERSION,
            "store": False,
            "sdk_retries": 0,
            "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
        }
        self.last_metadata = metadata
        return CompressionResult.from_dict(
            {"decisions": self.raw, "metadata": metadata}, expected_case_ids
        )


def test_prepare_and_fixture_evaluation_write_required_artifacts_without_mutating_source(
    tmp_path: Path,
) -> None:
    before = PACKET.read_bytes()
    output = tmp_path / "spec-015"
    reference = prepare_compression_evaluation(PACKET, output, root=ROOT)
    assert reference["source_packet_sha256"] == EXPECTED_SOURCE_PACKET_SHA256
    assert reference["blinding_validation"] == "PASS"
    assert set(path.name for path in output.iterdir()) == {
        "README.md", "blinded-packet.json", "source-packet-reference.json"
    }
    value = benchmark()
    report = run_compression_evaluation(
        PACKET, output, model="fixture", root=ROOT,
        judge_factory=lambda: FixtureJudge(decisions_for(value)),
    )
    assert report["verdict"] == "COMPRESSION_JUDGE_BETTER"
    assert report["required_result_questions"]["all_legitimate_binary_relationships_preserved"] is True
    assert report["required_result_questions"]["all_known_lossy_compressions_rejected"] is True
    assert report["required_result_questions"]["spec_014_pauli_false_admit_caught"] is True
    assert report["production_integration_ready"] is False
    assert report["safety"]["candidate_rewrites"] == 0
    assert PACKET.read_bytes() == before
    assert set(path.name for path in output.iterdir()) == {
        "README.md", "blinded-packet.json", "source-packet-reference.json",
        "judge-result.json", "metrics.json", "comparison.json", "report.json",
        "run-history.json",
    }
    history = json.loads((output / "run-history.json").read_text())
    assert history["live_call_count"] == 1
    assert history["automatic_retry_count"] == 0
    assert history["hidden_retries"] is False


def test_evaluation_preserves_invalid_output_and_fails_closed(tmp_path: Path) -> None:
    value = benchmark()

    class FailingJudge:
        last_raw = {"decisions": decisions_for(value)[:-1]}
        last_output_text = json.dumps(last_raw)
        last_metadata = {
            "provider": "fixture", "requested_model": "fixture", "model": "fixture",
            "provider_request_id": "failed-request", "prompt_version": COMPRESSION_PROMPT_VERSION,
            "usage": {"input_tokens": 100, "output_tokens": 10, "total_tokens": 110},
        }

        def judge(self, _blinded, _expected_case_ids):
            raise ValidationError("one decision missing")

    output = tmp_path / "failure"
    with pytest.raises(ValidationError, match="one decision missing"):
        run_compression_evaluation(
            PACKET, output, model="fixture", root=ROOT, judge_factory=FailingJudge,
        )
    preserved = json.loads((output / "judge-result.json").read_text())
    assert preserved["outcome"] == "JUDGE_CALL_OR_VALIDATION_FAILED"
    assert preserved["raw_proposal"] == FailingJudge.last_raw
    assert preserved["raw_output_text"] == FailingJudge.last_output_text
    assert json.loads((output / "report.json").read_text())["verdict"] == "INCONCLUSIVE"
    history = json.loads((output / "run-history.json").read_text())
    assert history["live_call_count"] == 1
    assert history["semantic_retry_count"] == 0


def test_openai_adapter_uses_one_store_false_call_with_no_answers() -> None:
    value = benchmark()
    blinded = value.to_blinded_dict()
    calls = []

    class Responses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                id="request-1",
                model="gpt-5.6-luna",
                output_text=json.dumps({"decisions": decisions_for(value)}),
                usage=SimpleNamespace(input_tokens=90, output_tokens=10, total_tokens=100),
            )

    judge = OpenAISemanticCompressionJudge(
        model="gpt-5.6-luna", client=SimpleNamespace(responses=Responses())
    )
    result = judge.judge(blinded, value.case_ids)
    assert len(result.decisions) == 10
    assert len(calls) == 1
    assert calls[0]["store"] is False
    assert calls[0]["model"] == "gpt-5.6-luna"
    assert calls[0]["text"]["format"]["strict"] is True
    assert calls[0]["reasoning"] == {"effort": "low"}
    assert "ROLE_ADEQUATE" not in calls[0]["input"]
    assert "historical_classification" not in calls[0]["input"]
    assert judge.last_metadata["sdk_retries"] == 0
    assert judge.last_metadata["benchmark_labels_exposed"] is False
