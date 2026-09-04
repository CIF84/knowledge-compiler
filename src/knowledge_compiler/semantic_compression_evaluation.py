"""Offline preparation and one-call evaluation for SPEC-015."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Mapping

from .models import ValidationError
from .openai_semantic_compression import (
    COMPRESSION_PROMPT_VERSION,
    DEFAULT_COMPRESSION_MODEL,
    OpenAISemanticCompressionJudge,
)
from .semantic_compression import (
    COMPRESSION_PROTOCOL_VERSION,
    EXPECTED_SOURCE_PACKET_SHA256,
    CompressionBenchmark,
    CompressionLabel,
    CompressionResult,
    CompressionVerdict,
    aggregate_compression_metrics,
    load_frozen_benchmark,
    select_compression_experiment_verdict,
    validate_blinded_packet,
    validate_historical_evidence,
)


EVALUATION_VERSION = "spec-015-evaluator-v1"
DEFAULT_BENCHMARK_RELATIVE_PATH = Path(
    "examples/evaluations/review-003-endpoint-role-benchmark-20260904/"
    "endpoint-role-packet.json"
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_compression_benchmark_path() -> Path:
    return repository_root() / DEFAULT_BENCHMARK_RELATIVE_PATH


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _usage(metadata: Mapping[str, Any]) -> dict[str, int]:
    raw = metadata.get("usage", {})
    return {
        key: int(raw.get(key, 0))
        for key in ("input_tokens", "output_tokens", "total_tokens")
    }


def prepare_compression_evaluation(
    benchmark_path: Path, output_dir: Path, *, root: Path | None = None
) -> dict[str, Any]:
    root = root or repository_root()
    benchmark = load_frozen_benchmark(benchmark_path)
    integrity = validate_historical_evidence(benchmark, root)
    blinded = benchmark.to_blinded_dict()
    validate_blinded_packet(blinded, benchmark)
    output_dir.mkdir(parents=True, exist_ok=True)
    reference = {
        "spec": "SPEC-015",
        "evaluation_version": EVALUATION_VERSION,
        "status": "FROZEN_FOR_ONE_CALL_EVALUATION",
        "source_packet_path": _relative(benchmark_path, root),
        "source_packet_sha256": benchmark.source_sha256,
        "expected_source_packet_sha256": EXPECTED_SOURCE_PACKET_SHA256,
        "source_packet_byte_identical": True,
        "source_packet_copied": False,
        "case_count": len(benchmark.cases),
        "positive_case_count": integrity["positive_case_count"],
        "negative_case_count": integrity["negative_case_count"],
        "opaque_case_ids": sorted(benchmark.case_ids),
        "opaque_id_strategy": "rank SHA-256(historical case_id) lexicographically; assign endpoint-role-001..010",
        "blinded_packet_canonical_sha256": hashlib.sha256(_canonical_bytes(blinded)).hexdigest(),
        "blinded_packet_file_sha256": hashlib.sha256(
            (json.dumps(blinded, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        ).hexdigest(),
        "model_facing_fields": [
            "protocol_version", "case_id", "grounded_assertion.statement",
            "grounded_assertion.participant_symbol_ids", "grounded_assertion.evidence",
            "symbols", "candidate_relationship.source_entity_id",
            "candidate_relationship.relationship_type",
            "candidate_relationship.target_entity_id", "predicate_contract",
        ],
        "withheld_fields": [
            "historical case_id", "label", "historical_classification", "defect_family",
            "assertion construction", "historical candidate id/statement/confidence/origin",
            "candidate endpoint diagnostics", "positive-control rationale", "provenance",
            "accepted corrections", "expected verdicts",
        ],
        "blinding_validation": "PASS",
        "historical_integrity": integrity,
        "verdict_vocabulary": [item.value for item in CompressionVerdict],
        "output_contract_fields": ["case_id", "verdict", "rationale"],
        "candidate_rewriting_possible": False,
        "live_call_budget": 1,
        "thresholds_frozen_before_live_output": {
            "COMPRESSION_JUDGE_BETTER": {
                "overall_agreement_minimum": 0.9,
                "adequate_admission_recall_minimum": 0.8,
                "negative_rejection_rate_minimum": 0.8,
                "adequate_admission_precision_minimum": 0.8,
                "blanket_rejection": False,
            },
            "MIXED": {
                "overall_agreement_minimum": 0.7,
                "adequate_admission_recall_minimum": 0.6,
                "negative_rejection_rate_minimum": 0.6,
            },
            "NO_MEANINGFUL_SIGNAL": "fallback or any blanket rejection",
            "INCONCLUSIVE": "provider or operational failure",
        },
    }
    _write_or_verify(output_dir / "source-packet-reference.json", reference)
    _write_or_verify(output_dir / "blinded-packet.json", blinded)
    readme = output_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            "# SPEC-015 semantic compression adequacy\n\n"
            "Offline implementation is prepared. The 10-case historical benchmark passed "
            "identity, provenance, evidence, candidate, contract, symbol, and blinding checks. "
            "Exactly one live `gpt-5.6-luna` judge call is pending explicit owner approval. "
            "The frozen REVIEW-003 packet is referenced by hash and is not copied or changed.\n\n"
            "After approval, the exact command is:\n\n"
            "```text\n"
            ".venv/bin/knowledge-compiler evaluate-semantic-compression "
            "--packet examples/evaluations/review-003-endpoint-role-benchmark-20260904/"
            "endpoint-role-packet.json --model gpt-5.6-luna "
            "--output-dir examples/evaluations/"
            "spec-015-semantic-compression-adequacy-20260904\n"
            "```\n",
            encoding="utf-8",
        )
    return reference


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _write_or_verify(path: Path, value: Any) -> None:
    serialized = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != serialized:
        raise ValidationError(f"prepared SPEC-015 artifact changed unexpectedly: {path}")
    path.write_text(serialized, encoding="utf-8")


def _comparison(
    benchmark: CompressionBenchmark, result: CompressionResult, metrics: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "spec": "SPEC-015",
        "evaluation_version": EVALUATION_VERSION,
        "source_packet_sha256": benchmark.source_sha256,
        "binary_scoring_rule": {
            "ROLE_ADEQUATE": CompressionVerdict.BINARY_ADEQUATE.value,
            "ROLE_INADEQUATE": "any verdict other than BINARY_ADEQUATE",
        },
        "cases": metrics["per_case"],
        "diagnostic_categories_secondary_to_binary_score": True,
    }


def _residual_errors(metrics: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [item for item in metrics["per_case"] if not item["correct"]]


def _negative_diagnostics(metrics: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "blind_id": item["blind_id"],
            "historical_case_id": item["historical_case_id"],
            "historical_classification": item["historical_classification"],
            "judge_verdict": item["judge_verdict"],
            "judge_rationale": item["judge_rationale"],
        }
        for item in metrics["per_case"]
        if item["label"] == CompressionLabel.ROLE_INADEQUATE.value
    ]


def _diagnostic_usefulness(negatives: list[dict[str, Any]]) -> dict[str, Any]:
    generic = CompressionVerdict.INSUFFICIENT_FOR_BINARY_RELATIONSHIP.value
    specific = [item for item in negatives if item["judge_verdict"] not in {
        CompressionVerdict.BINARY_ADEQUATE.value, generic
    }]
    generic_count = sum(item["judge_verdict"] == generic for item in negatives)
    if len(specific) == len(negatives):
        assessment = "ALL_NEGATIVE_REJECTIONS_USE_SPECIFIC_DIAGNOSTICS"
    elif specific:
        assessment = "PARTIALLY_USEFUL"
    else:
        assessment = "NO_SPECIFIC_DIAGNOSTIC_SIGNAL"
    return {
        "secondary_only": True,
        "assessment": assessment,
        "specific_negative_count": len(specific),
        "generic_negative_count": generic_count,
        "distinct_negative_verdicts": sorted({
            item["judge_verdict"] for item in negatives
        }),
        "negative_case_diagnostics": negatives,
    }


def _write_failure_artifacts(
    *, benchmark: CompressionBenchmark, output_dir: Path, model: str, judge: Any,
    started_at: str, elapsed: float, exc: Exception,
) -> None:
    metadata = dict(getattr(judge, "last_metadata", {}) or {})
    raw = getattr(judge, "last_raw", None)
    raw_text = getattr(judge, "last_output_text", None)
    _write_json(output_dir / "judge-result.json", {
        "spec": "SPEC-015",
        "outcome": "JUDGE_CALL_OR_VALIDATION_FAILED",
        "raw_proposal": raw,
        "raw_output_text": raw_text,
        "provider_metadata": metadata,
        "validation_failure": {"type": type(exc).__name__, "message": str(exc)},
    })
    _write_json(output_dir / "run-history.json", {
        "spec": "SPEC-015",
        "attempts": [{
            "sequence": 1,
            "stage": "SEMANTIC_COMPRESSION_JUDGE",
            "started_at": started_at,
            "completed_at": _utc_now(),
            "runtime_seconds": elapsed,
            "outcome": "FAILED",
            "provider_call_attempted": True,
            "provider": metadata.get("provider", "openai"),
            "requested_model": metadata.get("requested_model", model),
            "actual_model": metadata.get("model"),
            "provider_request_id": metadata.get("provider_request_id"),
            "prompt_version": metadata.get("prompt_version", COMPRESSION_PROMPT_VERSION),
            "usage": _usage(metadata),
            "cost": "NOT_AVAILABLE",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "raw_rejected_output_preserved": raw is not None or raw_text is not None,
        }],
        "live_call_count": 1,
        "semantic_retry_count": 0,
        "automatic_retry_count": 0,
        "hidden_retries": False,
        "prompt_repair_after_live_output": False,
        "candidate_rewrites": 0,
        "external_enrichment": False,
        "additional_models_or_agents": 0,
    })
    _write_json(output_dir / "report.json", {
        "spec": "SPEC-015",
        "evaluation_version": EVALUATION_VERSION,
        "outcome": "JUDGE_CALL_OR_VALIDATION_FAILED",
        "verdict": "INCONCLUSIVE",
        "source_packet_sha256": benchmark.source_sha256,
        "source_packet_byte_identical": _sha256(benchmark.source_path) == benchmark.source_sha256,
        "failure": {"type": type(exc).__name__, "message": str(exc)},
        "live_call_count": 1,
        "retry_count": 0,
        "authoritative_monetary_cost": "NOT_AVAILABLE",
        "production_integration_ready": False,
    })


def run_compression_evaluation(
    benchmark_path: Path,
    output_dir: Path,
    *,
    model: str = DEFAULT_COMPRESSION_MODEL,
    root: Path | None = None,
    judge_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    root = root or repository_root()
    prepare_compression_evaluation(benchmark_path, output_dir, root=root)
    benchmark = load_frozen_benchmark(benchmark_path)
    blinded = _read_json(output_dir / "blinded-packet.json")
    validate_blinded_packet(blinded, benchmark)
    judge = judge_factory() if judge_factory else OpenAISemanticCompressionJudge(model=model)
    started_at = _utc_now()
    start = time.perf_counter()
    try:
        result = judge.judge(blinded, benchmark.case_ids)
    except Exception as exc:
        elapsed = round(time.perf_counter() - start, 3)
        _write_failure_artifacts(
            benchmark=benchmark, output_dir=output_dir, model=model, judge=judge,
            started_at=started_at, elapsed=elapsed, exc=exc,
        )
        raise
    elapsed = round(time.perf_counter() - start, 3)
    if _sha256(benchmark_path) != EXPECTED_SOURCE_PACKET_SHA256:
        raise ValidationError("frozen REVIEW-003 packet changed during SPEC-015 evaluation")
    metadata = dict(result.metadata)
    raw = dict(getattr(judge, "last_raw", {}) or {})
    _write_json(output_dir / "judge-result.json", {
        "spec": "SPEC-015",
        "outcome": "SUCCESS",
        "prompt_version": COMPRESSION_PROMPT_VERSION,
        "raw_proposal": raw,
        "normalized_result": result.to_dict(),
        "provider_metadata": metadata,
    })
    metrics = aggregate_compression_metrics(benchmark, result)
    _write_json(output_dir / "metrics.json", metrics)
    comparison = _comparison(benchmark, result, metrics)
    _write_json(output_dir / "comparison.json", comparison)
    verdict = select_compression_experiment_verdict(metrics)
    errors = _residual_errors(metrics)
    pauli = next(
        item for item in metrics["per_case"]
        if item["historical_case_id"] == "negative-pauli-constrains-electron"
    )
    positives = [
        item for item in metrics["per_case"]
        if item["label"] == CompressionLabel.ROLE_ADEQUATE.value
    ]
    negatives = _negative_diagnostics(metrics)
    missing_context_false_rejections = [
        item for item in positives
        if item["judge_verdict"] == CompressionVerdict.MISSING_ESSENTIAL_PARTICIPANT.value
    ]
    usage = _usage(metadata)
    run_history = {
        "spec": "SPEC-015",
        "attempts": [{
            "sequence": 1,
            "stage": "SEMANTIC_COMPRESSION_JUDGE",
            "started_at": started_at,
            "completed_at": _utc_now(),
            "runtime_seconds": elapsed,
            "outcome": "SUCCESS",
            "provider_call_attempted": True,
            "provider": metadata.get("provider", "openai"),
            "requested_model": metadata.get("requested_model", model),
            "actual_model": metadata.get("model"),
            "provider_request_id": metadata.get("provider_request_id"),
            "prompt_version": metadata.get("prompt_version", COMPRESSION_PROMPT_VERSION),
            "usage": usage,
            "cost": "NOT_AVAILABLE",
        }],
        "live_call_count": 1,
        "semantic_retry_count": 0,
        "automatic_retry_count": 0,
        "hidden_retries": False,
        "prompt_repair_after_live_output": False,
        "candidate_rewrites": 0,
        "external_enrichment": False,
        "additional_models_or_agents": 0,
    }
    _write_json(output_dir / "run-history.json", run_history)
    report = {
        "spec": "SPEC-015",
        "evaluation_version": EVALUATION_VERSION,
        "protocol_version": COMPRESSION_PROTOCOL_VERSION,
        "prompt_version": COMPRESSION_PROMPT_VERSION,
        "outcome": "SUCCESS",
        "verdict": verdict,
        "source_packet_path": _relative(benchmark_path, root),
        "source_packet_sha256": benchmark.source_sha256,
        "source_packet_byte_identical": True,
        "blinding_validation": "PASS",
        "case_counts": {"positive": 5, "negative": 5, "total": 10},
        "provider": metadata.get("provider", "openai"),
        "requested_model": metadata.get("requested_model", model),
        "actual_model": metadata.get("model"),
        "provider_request_id": metadata.get("provider_request_id"),
        "live_call_count": 1,
        "retry_count": 0,
        "usage": usage,
        "runtime_seconds": elapsed,
        "authoritative_monetary_cost": "NOT_AVAILABLE",
        "metrics": {key: value for key, value in metrics.items() if key != "per_case"},
        "per_case_verdicts": metrics["per_case"],
        "positive_control_results": positives,
        "negative_control_results": negatives,
        "required_result_questions": {
            "all_legitimate_binary_relationships_preserved": metrics["false_inadequate_rejects"] == 0,
            "all_known_lossy_compressions_rejected": metrics["false_adequate_admits"] == 0,
            "spec_014_pauli_false_admit_caught": pauli["judge_verdict"] != CompressionVerdict.BINARY_ADEQUATE.value,
            "negative_diagnostic_verdicts": {
                item["historical_case_id"]: item["judge_verdict"] for item in negatives
            },
            "positive_missing_essential_due_only_to_context": [
                item["historical_case_id"] for item in missing_context_false_rejections
            ],
            "supports_narrow_gates_over_multi_agent_deliberation": (
                verdict == "COMPRESSION_JUDGE_BETTER"
            ),
            "residual_error_class": errors if errors else "NONE_ON_THIS_PACKET",
            "production_integration_ready": False,
        },
        "blanket_or_trivial_strategy_evidence": metrics["trivial_strategy_checks"],
        "diagnostic_category_usefulness": _diagnostic_usefulness(negatives),
        "comparison_to_spec_014": (
            "This narrower task is not statistically comparable to SPEC-014. It directly tests "
            "whether the endpoint-role judge catches the preserved Pauli and related compression "
            "cases while retaining legitimate binary relationships."
        ),
        "multi_agent_deliberation": (
            "NOT_JUSTIFIED" if verdict == "COMPRESSION_JUDGE_BETTER"
            else "DEFERRED_PENDING_RESIDUAL_ERROR_REVIEW"
        ),
        "production_integration_ready": False,
        "production_threshold_claimed": False,
        "safety": {
            "candidate_rewrites": 0,
            "entities_minted": 0,
            "predicates_created": 0,
            "proposition_types_created": 0,
            "evidence_changed": 0,
            "production_integration": False,
        },
        "knowledge_model_changes": [],
        "relationship_vocabulary_changes": [],
        "proposition_vocabulary_changes": [],
        "grounding_rule_changes": [],
        "dependencies_added": [],
        "dependencies_removed": [],
        "complexity_impact": (
            "Adds an isolated experimental benchmark loader/blinder, provider-independent judge "
            "protocol, OpenAI adapter, deterministic scorer, and CLI seam; no default pipeline path changes."
        ),
        "deviations": [],
        "prior_artifacts_preserved": True,
        "residual_errors": errors,
    }
    _write_json(output_dir / "report.json", report)
    (output_dir / "README.md").write_text(
        "# SPEC-015 semantic compression adequacy\n\n"
        f"Final verdict: `{verdict}`. The one-call blinded judge preserved "
        f"{metrics['true_adequate_admits']}/5 positive controls and rejected "
        f"{metrics['true_inadequate_rejects']}/5 historical lossy compressions. "
        "The result is exploratory and does not authorize production integration. "
        "See `source-packet-reference.json`, `blinded-packet.json`, `judge-result.json`, "
        "`metrics.json`, `comparison.json`, `report.json`, and `run-history.json`.\n",
        encoding="utf-8",
    )
    return report
