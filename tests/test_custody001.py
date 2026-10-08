"""Custody fail-closed evidence checks, never candidate adjudication/selection."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from knowledge_compiler.control_plane import validate_control_plane

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("custody001",ROOT/"tools/custody001_preflight.py")
custody=importlib.util.module_from_spec(spec);spec.loader.exec_module(custody)

@pytest.fixture(scope="module")
def artifacts():return custody.build()

def test_deterministic_regeneration(artifacts):
    assert artifacts==custody.build()
    for path,raw in artifacts.items():assert (ROOT/path).read_bytes()==raw

def test_five_families_explicitly_unresolved_not_false_attested(artifacts):
    m=json.loads(artifacts[str(custody.EXPORT/"contamination-reference-manifest.json")])
    assert [r["family"] for r in m["family_coverage"]]==custody.FAMILIES
    assert m["completeness_status"]=="FAMILY_COMPLETENESS_UNRESOLVED"
    assert m["family_coverage"][0]["status"]=="FAMILY_COMPLETENESS_UNRESOLVED"
    assert all(r["status"]=="NOT_EVALUATED_AFTER_FAIL_CLOSED" for r in m["family_coverage"][1:])
    with pytest.raises(ValueError,match="withheld"):custody.require_complete(m)
    changed=copy.deepcopy(m);changed["completeness_status"]="COMPLETE"
    with pytest.raises(ValueError,match="withheld"):custody.require_complete(changed)

def test_identity_inventory_contains_no_response_text_or_project_context(artifacts):
    raw=artifacts[str(custody.EXPORT/"contamination-reference-manifest.json")]
    m=json.loads(raw)
    assert len(m["records"])==2
    for row in m["records"]:
        assert row["exact_historical_input_passage_text"] is None
        assert row["exact_passage_sha256"] is None and row["normalized_passage_sha256"] is None
        path=row["original_bytes_repository_identity"]["path"]
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==custody.ORIGINALS[path]==row["original_document_sha256"]
    for forbidden in [b"STATUS.md",b"gpt-",b"BENCHMARK_HARNESS_ACCEPTED",b"current-team",b"C+",b"prompts/",b"learner verdict",b"mental model","Don’t visualize sentences".encode()]:
        assert forbidden not in raw

def test_no_continuation_authority_or_zip_generated(artifacts):
    assert not any(p.endswith((".zip",".md",".pdf",".rtf")) for p in artifacts)
    report=json.loads(artifacts[str(custody.BASE/"custody-001-report.json")])
    assert report["selector_continuation_authority_created"] is False
    assert report["continuation_zip_created"] is False and report["continuation_zip_sha256"] is None
    assert report["selector_continuation_prompt"] is None
    assert report["selector_provisional_package_imported_or_inspected"] is False

def test_artifact_tamper_or_lineage_substitution_fails_closed():
    files=custody.snapshot(ROOT)
    files["audits/electromagnetism.rtf"]+=b" alteration"
    with pytest.raises(ValueError,match="identity mismatch"):custody.export_claims(files)
    files=custody.snapshot(ROOT);files[custody.THESIS]=files[custody.THESIS].replace(b"No original input source, source hash, exact prompt",b"altered evidence")
    with pytest.raises(ValueError,match="missing-input finding"):custody.export_claims(files)

def test_quantum_later_full_source_not_mistaken_for_missing(artifacts):
    r=json.loads(artifacts[str(custody.BASE/"custody-001-report.json")])
    q=r["evidence"]["quantum_concern_resolved"]
    assert q["text_characters"]==39735 and q["exact_passage_sha256"]==custody.QUANTUM_SHA
    assert q["normalized_passage_sha256"]==custody.QUANTUM_SHA
    assert r["blocking_family"]=="recovered electromagnetism"

def test_all_protected_historical_bytes_unchanged(artifacts):
    rows=json.loads(artifacts[str(custody.BASE/"custody-001-protected-state.json")])["files"]
    for row in rows:
        raw=(ROOT/row["path"]).read_bytes()
        assert len(raw)==row["bytes"] and hashlib.sha256(raw).hexdigest()==row["sha256"]

def test_control_plane_preserves_owner_bench_verdict_without_implicit_execution():
    state=validate_control_plane(ROOT)
    assert state.packet in {custody.CONTRACT,None}
    if state.packet:
        assert state.control.authority=="OFFLINE_ONLY" and state.control.status=="APPROVED_FOR_IMPLEMENTATION"
    text=(ROOT/"STATUS.md").read_text()
    assert "BENCHMARK_HARNESS_ACCEPTED_PREEXISTING_AUDIT_HASH_FAILURE_NON_BLOCKING" in text
    old=json.loads((ROOT/custody.BASE/"benchmark-readiness-v1/readiness-report.json").read_bytes())
    assert old["mechanical_readiness_branch"]=="INCONCLUSIVE"
