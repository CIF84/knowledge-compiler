from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.blind_evaluation import BlindSource
from knowledge_compiler.decomposed_extraction import GateStatus
from knowledge_compiler.decomposed_extraction_v2 import run_candidate_b_v2
from knowledge_compiler.spec051_offline_evaluation import _OfflineAdapter
from knowledge_compiler.spec052_live_evaluation import (
    CONTRACT_SHA256,
    DurableLedger,
    ORIGIN_TAXONOMY,
    _mechanical_branch,
    _origin,
    build_preflight,
    persist_v2_source,
    run_live_evaluation,
    semantic_omission_audit,
)
from knowledge_compiler.spec052_postrun_audit import finalize
from knowledge_compiler.decomposed_extraction import StageName


ROOT = Path(__file__).parents[1]


def _synthetic_run(*, relationship: bool = False):
    adapter = _OfflineAdapter(relationship=relationship)
    run = run_candidate_b_v2(adapter.text, adapter, source_metadata={"source_id": "synthetic-claim-audit"})
    assert run.status is GateStatus.PASS
    return run, adapter


def test_preflight_matches_frozen_sources_candidate_and_historical_evidence_without_key():
    result = build_preflight(ROOT, require_api_key=False)
    assert result["status"] == "PASS"
    assert result["contract_sha256"] == CONTRACT_SHA256
    assert result["source_count"] == 9
    assert result["maximum_provider_calls"] == 27
    assert result["model"] == "gpt-5.6-luna"
    assert result["store"] is False
    assert result["retry_classes"] == 0
    assert all(item["status"] == "PASS" for item in result["checks"])


def test_missing_credential_stops_before_output_or_provider_transmission(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    output = tmp_path / "one-shot-output"
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY available"):
        run_live_evaluation(ROOT, output)
    assert not output.exists()


def test_existing_output_refuses_any_second_execution(tmp_path):
    output = tmp_path / "already-executed"
    output.mkdir()
    with pytest.raises(RuntimeError, match="rerun is forbidden"):
        run_live_evaluation(ROOT, output)


def test_durable_ledger_records_request_at_start_and_terminal_outcome(tmp_path):
    path = tmp_path / "request-start-ledger.json"
    ledger = DurableLedger(path, "synthetic-source")
    entry = ledger.begin(
        source_id="synthetic-source", source_sha256="a" * 64,
        stage=StageName.SEMANTIC_STRUCTURE,
        prompt_version="spec-047-semantic-structure-v1", prompt_sha256="b" * 64,
        schema_sha256="c" * 64, upstream_input_sha256="d" * 64,
    )
    started = json.loads(path.read_text())
    assert started["calls_started"] == 1
    assert started["entries"][0]["status"] == "REQUEST_STARTED"
    assert started["entries"][0]["prompt_version"] == "spec-051-semantic-structure-v2"
    ledger.complete(entry, provider_response_id="response-a", http_request_id="request-a", usage={"total_tokens": 3})
    completed = json.loads(path.read_text())
    assert completed["entries"][0]["status"] == "PROVIDER_RESPONSE_RECEIVED"
    assert completed["entries"][0]["provider_response_id"] == "response-a"
    assert completed["entries"][0]["store"] is False


def test_claim_only_audit_records_exact_grounding_and_zero_topology():
    run, adapter = _synthetic_run()
    audit = semantic_omission_audit(adapter.text, run)
    assert audit["stage3_ran"] is True
    assert audit["parsed_response_available"] is True
    assert audit["claim_only_by_exact_statement_and_distinct_id_count"] == 1
    assert audit["unintended_topology_count_if_admitted"] == 0
    assert audit["claims"][0]["exact_unique_source_quotes"] is True
    assert audit["claims"][0]["admitted_in_knowledge_model"] is True
    assert audit["claims"][0]["admitted_evidence_exact"] is True
    assert "NOT_AUTOMATICALLY_RUN" in audit["assertion_aware_projection"]


def test_existing_relationship_and_claim_remain_separate_in_source_artifacts(tmp_path):
    run, adapter = _synthetic_run(relationship=True)
    source = BlindSource(
        source_id=run.source_id, title="Synthetic claim audit", text=adapter.text,
        source_sha256=hashlib.sha256(adapter.text.encode()).hexdigest(),
        provenance={"kind": "synthetic"},
    )
    outcome = persist_v2_source(tmp_path / "source", source, run)
    assert outcome["status"] == "PASS"
    assert outcome["semantic_omission_audit"]["claim_only_by_exact_statement_and_distinct_id_count"] == 1
    assert outcome["semantic_omission_audit"]["unintended_topology_count_if_admitted"] == 0
    gate = json.loads((tmp_path / "source/stages/02-semantic-structure/gate.json").read_text())
    assert gate["stage_version"] == "spec-051-semantic-structure-v2"
    original = json.loads((tmp_path / "source/stages/02-semantic-structure/parsed-proposal.json").read_text())
    normalized = json.loads((tmp_path / "source/stages/02-semantic-structure/normalized-for-canonical.json").read_text())
    assert "comparison_conditions" in original and "propositions" not in original
    assert "propositions" in normalized and "comparison_conditions" not in normalized
    assert json.loads((tmp_path / "source/candidate-run.json").read_text())["candidate_version"] == "spec-051-candidate-b-v2"


def test_failure_taxonomy_is_frozen_and_ambiguous_product_verdict_stays_human_gated():
    assert _origin(StageName.ENTITY_INVENTORY, "duplicate identity") == "ENTITY_INVENTORY"
    assert _origin(StageName.SEMANTIC_STRUCTURE, "comparison operand is invalid") == "PROPOSITION_CONSTRUCTION"
    assert _origin(StageName.SEMANTIC_STRUCTURE, "unknown frozen entity ID") == "CROSS_REFERENCE_CONSISTENCY"
    assert _origin(StageName.CLAIM_EVIDENCE_BINDING, "quote mismatch") == "EVIDENCE_FIDELITY"
    assert _origin(StageName.CANONICAL_VALIDATION, "invalid parent") == "CANONICAL_VALIDATION"
    assert all(item in ORIGIN_TAXONOMY for item in (
        "ENTITY_INVENTORY", "PROPOSITION_CONSTRUCTION", "CROSS_REFERENCE_CONSISTENCY",
        "EVIDENCE_FIDELITY", "CANONICAL_VALIDATION",
    ))
    assert _mechanical_branch({"admitted_sources": 9, "known_invalid_objects_admitted": 0}, []) == "INCONCLUSIVE"
    assert _mechanical_branch({"admitted_sources": 9, "known_invalid_objects_admitted": 1}, []) == "B_V2_REGRESSION"


def test_committed_live_evidence_reconciles_calls_claims_and_failure_taxonomy(tmp_path):
    output = ROOT / "examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915"
    report = json.loads((output / "final-report.json").read_text())
    ledger = json.loads((output / "provider-call-ledger.json").read_text())
    run_report = json.loads((output / "run-report.json").read_text())
    assert report["provider_calls_started"] == ledger["calls_started"] == 26
    assert report["three_arm_summaries"]["CANDIDATE_B_V2_LIVE"]["admitted_sources"] == 8
    assert report["known_invalid_objects_admitted"] == 0
    assert report["failure_origin_taxonomy"] == {"PROPOSITION_CONSTRUCTION": 1}
    assert report["proposition_construction_failures"] == 1
    assert report["historical_b_v1_proposition_construction_failures"] == 6
    assert run_report["failure_origin_taxonomy"] == {"OTHER": 1}
    assert report["mechanically_supported_branch"] == "INCONCLUSIVE"
    assert report["owner_verdict"] == "PENDING"
    assert report["owner_review"]["promotion"] == "NOT_AUTHORIZED"
    assert [item["global_call_ordinal"] for item in ledger["entries"]] == list(range(1, 27))
    assert all(item["store"] is False for item in ledger["entries"])
    assert all(all(item[key] == 0 for key in ("sdk_retries", "hidden_retries", "semantic_retries", "repair_calls")) for item in ledger["entries"])
    assert all(item["provider_response_id"] and item["http_request_id"] for item in ledger["entries"])
    audit = json.loads((output / "claim-only-preservation-audit.json").read_text())
    assert audit["totals"]["parsed_claims"] == 152
    assert audit["totals"]["grounding_policy_satisfied"] == 152
    assert audit["totals"]["admitted_claims"] == 152
    assert audit["totals"]["mechanical_claim_only_count"] == 98
    assert audit["totals"]["grounded_admitted_claim_only_count"] == 98
    assert audit["totals"]["unintended_topology_count"] == 0
    assert audit["totals"]["dedicated_claim_focus_decisions"] == 0
    failure = json.loads((output / "post-run-failure-taxonomy-audit.json").read_text())
    assert failure["generated_classifier_origin"] == "OTHER"
    assert failure["authoritative_spec046_origin"] == "PROPOSITION_CONSTRUCTION"
    assert failure["retry_or_repair_performed"] is False


def test_postrun_aggregate_regeneration_is_deterministic_and_manifest_is_complete():
    output = ROOT / "examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915"
    before = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    finalize(ROOT, output)
    after = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    assert before == after
    manifest = json.loads((output / "artifact-manifest.json").read_text())
    files = [path for path in output.rglob("*") if path.is_file() and path.name != "artifact-manifest.json"]
    assert manifest["file_count_excluding_manifest"] == len(files)
    by_path = {item["path"]: item for item in manifest["files"]}
    assert set(by_path) == {str(path.relative_to(output)) for path in files}
    for path in files:
        item = by_path[str(path.relative_to(output))]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
        assert path.stat().st_size == item["byte_count"]
