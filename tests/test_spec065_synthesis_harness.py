from __future__ import annotations

import copy
import inspect
import json
import socket
from pathlib import Path

import pytest

from knowledge_compiler import spec065_synthesis_harness as harness
from knowledge_compiler.models import ValidationError


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / harness.OUTPUT_DIR


@pytest.fixture(scope="module")
def fixtures():
    return harness.fixtures()


def named(fixtures, name):
    return next(r for r in fixtures[1] if r["name"] == name)


def test_protected_startup_tree_is_exact_and_future_new_paths_do_not_change_snapshot():
    rows=harness.protected(ROOT)
    assert len(rows)==2060
    assert harness.stable(rows)==harness.PROTECTED_SHA
    assert rows==harness.load(OUTPUT/"protected-state.json")["files"]
    assert all("spec-065" not in r["path"] for r in rows)


def test_real_substrates_and_input_packages_are_exact_frozen_copies():
    sources=harness.corpus(ROOT)
    manifest=harness.load(OUTPUT/"input-manifest.json")
    assert len(sources)==3
    assert sum(len(s["semantic_items"]) for s in sources)==141
    assert sum(len(s["material_implications"]) for s in sources)==54
    for i,source in enumerate(sources,1):
        assert source==harness.load(ROOT/harness.INPUT_DIR/"substrates"/f"{i:02d}.json")
        assert source==harness.load(OUTPUT/"inputs"/f"{i:02d}-substrate.json")
        assert harness.input_packet(source,"A",[])==harness.load(OUTPUT/"inputs"/f"{i:02d}-stage-A-package.json")
        assert harness.stable(source)==manifest["sources"][i-1]["substrate_sha256"]


@pytest.mark.parametrize("stage", ["A","B","C"])
def test_schema_is_strict_supported_and_matches_frozen_artifact(stage):
    schema=harness.schemas()[stage]
    harness.validate_schema(schema)
    assert schema==harness.load(OUTPUT/"schemas"/(stage+".json"))
    assert schema["additionalProperties"] is False
    assert set(schema["required"])==set(schema["properties"])


def test_schema_never_treats_bool_as_integer_or_ignores_extra_or_missing_fields(fixtures):
    original=named(fixtures,"valid_truthful_subsumption")["raw"]
    for mutation in ("bool_integer","extra","missing","no_new_meaning"):
        value=copy.deepcopy(original)
        if mutation=="bool_integer":value["units"][0]["proof"]["start_char"]=False
        elif mutation=="extra":value["units"][0]["repair"]=True
        elif mutation=="missing":value["units"][0].pop("constraints")
        else:value["units"][0]["no_new_meaning"]=False
        with pytest.raises(ValidationError):harness.validate_json(value,harness.schemas()["A"])
    schema=harness.schemas()["A"]
    schema["unimplemented_semantic_keyword"]=True
    with pytest.raises(ValidationError):harness.validate_schema(schema)


def test_prompt_versions_hashes_and_constraints_are_frozen():
    manifest=harness.load(OUTPUT/"schemas-prompts-manifest.json")
    for entry in manifest["contracts"]:
        s=entry["stage"]
        file=OUTPUT/"prompts"/(s+".txt")
        assert file.read_text()==harness.PROMPTS[s]
        assert harness.sha(file)==entry["prompt_file_sha256"]
        assert harness.stable(harness.schemas()[s])==entry["schema_canonical_sha256"]
        for text in ("ONLY", "DATA", "uncertainty", "causal status", "No external", "personalization", "No retry", "not a compressed stage", "no new meaning"):
            assert text.lower() in harness.PROMPTS[s].lower()


def test_fixture_corpus_preserves_all_expected_admissions_and_rejections(fixtures):
    sub,rows=fixtures
    assert len(rows)==30
    assert sum(r["expected_status"]=="ADMITTED" for r in rows)==4
    assert rows==harness.load(OUTPUT/"fixtures-and-results.json")
    for row in rows:
        assert row["result"]["status"]==row["expected_status"]
        assert row["result"]["raw"]==row["raw"]
        assert row["result"]["raw_sha256"]==harness.stable(row["raw"])
        if row["expected_code"]:
            assert row["result"]["failure"]["code"]==row["expected_code"]
    assert {r["result"]["failure"]["category"] for r in rows if r["result"]["failure"]}=={
        "CANDIDATE_GENERATION_FAILURE","SCHEMA_FORMAT_FAILURE","PRESERVATION_FAILURE",
        "GROUNDING_PROVENANCE_FAILURE","ABSTRACTION_QUALITY_FAILURE","COMPRESSION_FAILURE","ARCHITECTURE_FAILURE"}


def test_admitted_fixture_proofs_preserve_every_item_qualification_and_implication(fixtures):
    sub,rows=fixtures
    for row in rows:
        result=row["result"]
        if result["status"]!="ADMITTED":continue
        semantic=[r for r in result["ledger"] if r["category"]=="SEMANTIC"]
        assert {r["id"] for r in semantic}=={i["upstream_id"] for i in sub["semantic_items"]}
        for entry in result["ledger"]:
            assert harness.recover(sub,entry["recovery_pointer"])==entry["exact_value"]
            assert entry["evidence_ids"]
        assert result["metrics"]["provenance_coverage"]==1.0
        assert result["metrics"]["recovery_coverage"]==1.0
        assert result["metrics"]["words"]<len(sub["source_text"].split())
        assert "Pressure is 5 Pa." in result["learner_text"]
    a=named(fixtures,"valid_truthful_subsumption")["result"]
    b=named(fixtures,"valid_shared_mechanism_abstraction")["result"]
    assert a["metrics"]["commitment_modes"]["SUBSUMED"]==8
    assert b["metrics"]["commitment_modes"]["STRUCTURALLY_ENCODED"]==4
    assert b["metrics"]["admitted_explanatory_abstractions"]==1
    assert " may " in b["learner_text"]


def test_positive_control_is_formal_fixture_not_general_natural_language_entailment(fixtures):
    sub,_=fixtures
    a=named(fixtures,"valid_truthful_subsumption")["result"]
    b=named(fixtures,"valid_shared_mechanism_abstraction")["raw"]
    assert harness.classify_b(sub,b["abstractions"][0],a)[0]=="EXPLANATORY_ABSTRACTION"
    assert harness.controlled_principle("Channels often transport fluid.") is None
    assert harness.controlled_principle("Every member of channel must transport fluid.") is None
    assert harness.controlled_principle("Every member of channel may walk by river.") is None
    assert harness.controlled_principle("Every member of channel may transport-fluid VIA open-valve.")==("channel","transport-fluid","open-valve")
    assert harness.controlled_member("Alpha may be a member of channel.","channel") is None
    changed=copy.deepcopy(sub)
    changed["semantic_items"][2]["qualification_links"]=[{"cue":"possibly","start_char":0,"end_char":8}]
    assert harness.classify_b(changed,b["abstractions"][0],a)[0]=="UNRESOLVED"


def test_generation_metadata_or_overlap_cannot_close_semantic_validation_gap(fixtures):
    for name in ("unproven_novel_synthesis","unresolved_novel_abstraction"):
        row=named(fixtures,name)
        assert row["result"]["status"]=="REJECTED"
        assert row["result"]["failure"]["semantic_validation_gaps"]==["SEMANTIC_VALIDATION_GAP"]
    assert any(r["capability"]=="SEMANTIC_VALIDATION_GAP" for r in harness.CAPABILITIES)


def test_grouping_and_labels_never_receive_abstraction_admission(fixtures):
    for name,code in (("grouping_only_false_abstraction","SUPPORTED_GROUPING_ONLY"),("label_only_false_abstraction","LABEL_ONLY"),("unsupported_abstraction","UNSUPPORTED")):
        result=named(fixtures,name)["result"]
        assert result["status"]=="REJECTED"
        assert result["failure"]["code"]==code


def test_unsupported_types_and_duplicate_members_fail_closed(fixtures):
    sub,_=fixtures
    row=named(fixtures,"valid_shared_mechanism_abstraction")
    for type_name in ("COMMON_DEPENDENCY","CAUSAL_PRINCIPLE","CONTRASTING_CASES","CONSTRAINT_OR_BOUNDARY","PROCESS_PATTERN","UNRESOLVED"):
        raw=copy.deepcopy(row["raw"])
        raw["abstractions"][0]["abstraction_type"]=type_name
        result=harness.admit(sub,"B",raw,row["parents"])
        assert result["status"]=="REJECTED"
        assert result["failure"]["code"]=="SEMANTIC_VALIDATION_GAP"
    raw=copy.deepcopy(row["raw"]);raw["abstractions"][0]["member_unit_ids"]=["u2","u2"]
    assert harness.admit(sub,"B",raw,row["parents"])["status"]=="REJECTED"


def test_parent_receipts_replay_against_independent_authority_not_model_declared_status(fixtures):
    sub,_=fixtures
    a=named(fixtures,"valid_truthful_subsumption")["result"]
    b=named(fixtures,"valid_shared_mechanism_abstraction")["raw"]
    for mutation in ("raw","ledger","hash","status","candidate"):
        altered=copy.deepcopy(a)
        if mutation=="raw":altered["raw"]["units"][0]["statement"]="certain transport"
        elif mutation=="ledger":altered["ledger"]=[]
        elif mutation=="hash":altered["substrate_sha256"]="0"*64
        elif mutation=="status":altered["status"]="REJECTED"
        else:altered["candidate"]["units"][0]["statement"]="certain transport"
        result=harness.admit(sub,"B",b,[altered])
        assert result["status"]=="REJECTED"
        assert result["failure"]["code"]=="UNADMITTED_PARENT"


def test_json_string_response_has_preserved_raw_and_normalized_admitted_parent(fixtures):
    sub,_=fixtures
    raw=json.dumps(named(fixtures,"valid_truthful_subsumption")["raw"])
    a=harness.admit(sub,"A",raw)
    assert a["status"]=="ADMITTED" and a["raw"]==raw
    bv=harness.b_fixture(sub,a)
    b=harness.admit(sub,"B",json.dumps(bv),[a])
    assert b["status"]=="ADMITTED"
    cv=harness.c_fixture(sub,a,b)
    assert harness.admit(sub,"C",json.dumps(cv),[a,b])["status"]=="ADMITTED"


def test_source_certificate_cannot_clip_scope_or_point_to_unrelated_assertion(fixtures):
    sub,_=fixtures
    original=named(fixtures,"valid_exact_source_assertion")["raw"]
    altered=copy.deepcopy(original)
    altered["units"][0]["proof"]["start_char"]=1
    result=harness.admit(sub,"A",altered)
    assert result["status"]=="REJECTED"
    assert result["failure"]["code"]=="SOURCE_ASSERTION_RANGE_DRIFT"
    altered=copy.deepcopy(original)
    start=sub["source_text"].index("Pressure is 5 Pa.")
    altered["units"][0]["proof"]={"kind":"EXACT_SOURCE_SPAN","start_char":start,"end_char":start+len("Pressure is 5 Pa.")}
    altered["units"][0]["statement"]="Pressure is 5 Pa."
    assert harness.admit(sub,"A",altered)["failure"]["code"]=="SOURCE_WITNESS_DOES_NOT_CARRY_ITEM"


def test_full_context_and_dependency_checks_use_frozen_corpus_not_partial_matching():
    for sub in harness.corpus(ROOT):
        payload=harness.auxiliary(sub)
        harness.check_aux(sub,payload)
        altered=copy.deepcopy(payload);altered["context"][0]["text"]="heading only"
        with pytest.raises(ValidationError):harness.check_aux(sub,altered)
        altered=copy.deepcopy(payload);altered["dependencies"].pop()
        with pytest.raises(ValidationError):harness.check_aux(sub,altered)


def test_staged_dry_run_stops_after_first_rejection_and_preserves_skipped_slots():
    histories=harness.load(OUTPUT/"staged-dry-run-history.json")
    assert [r["status"] for r in histories["all_admitted"]]==["ADMITTED"]*3
    assert [r["status"] for r in histories["A_rejection_stops_B_C"]]==["REJECTED","SKIPPED","SKIPPED"]
    assert [r["status"] for r in histories["B_rejection_stops_C"]]==["ADMITTED","REJECTED","SKIPPED"]
    assert histories["provider_calls"]==0


def test_future_model_effort_storage_retry_sampling_and_nine_call_controls_are_exact():
    manifest=harness.load(OUTPUT/"future-live-execution-manifest.json")
    ledger=harness.load(OUTPUT/"max-nine-call-ledger-template.json")
    harness.validate_future_contract(manifest)
    assert manifest["settings"]=={"model":"gpt-6.1-sol","reasoning":{"effort":"high"},"store":False,"max_output_tokens":32768}
    assert len(manifest["calls"])==len(ledger["rows"])==9
    assert ledger["actual_provider_calls"]==ledger["actual_attempts"]==0
    assert ledger["total_usage"] is None and ledger["total_cost"] is None
    assert all(r["request_id"] is None and r["usage"] is None and r["cost"] is None and r["state"]=="NOT_AUTHORIZED_NOT_ATTEMPTED" for r in ledger["rows"])
    assert manifest["provider_support"]["provider_contract_verified"] is False
    assert "FAIL_CLOSED" in manifest["provider_support"]["status"]


@pytest.mark.parametrize("mutation",["model","effort","store","sdk_retry","semantic_retry","repair","sampling","extra_call","reordered_call","condition","prompt"])
def test_future_contract_rejects_substitution_retry_budget_gate_or_identity_drift(mutation):
    manifest=harness.load(OUTPUT/"future-live-execution-manifest.json")
    if mutation=="model":manifest["settings"]["model"]="gpt-5.6-luna"
    elif mutation=="effort":manifest["settings"]["reasoning"]["effort"]="low"
    elif mutation=="store":manifest["settings"]["store"]=0
    elif mutation=="sdk_retry":manifest["controls"]["sdk_max_retries"]=1
    elif mutation=="semantic_retry":manifest["controls"]["semantic_retries"]=1
    elif mutation=="repair":manifest["controls"]["repair_calls"]=1
    elif mutation=="sampling":manifest["controls"]["sampling_parameters"]={"temperature":0}
    elif mutation=="extra_call":manifest["calls"].append(copy.deepcopy(manifest["calls"][0]))
    elif mutation=="reordered_call":manifest["calls"].reverse()
    elif mutation=="condition":manifest["calls"][3]["condition"]="ALWAYS"
    else:manifest["calls"][0]["prompt_sha256"]="0"*64
    with pytest.raises(ValidationError):harness.validate_future_contract(manifest)


def test_future_request_is_local_only_exact_and_never_accepts_unadmitted_parent(fixtures):
    sub,_=fixtures
    request=harness.future_request(sub,"A",[])
    assert all(request[key]==value for key,value in harness.MODEL.items())
    assert request["text"]["format"]["strict"] is True
    assert json.loads(request["input"])["authoritative_substrate"]==sub
    with pytest.raises(ValidationError):harness.future_request(sub,"B",[])
    with pytest.raises(ValidationError):harness.future_request(sub,"C",[named(fixtures,"valid_truthful_subsumption")["result"]])


def test_no_domain_case_expected_answer_or_owner_routing_in_admission():
    code="\n".join(inspect.getsource(f) for f in (harness.input_packet,harness.admit,harness.proof_a,harness.classify_b,harness.check_a,harness.check_b,harness.check_c,harness.controlled_principle,harness.controlled_member,harness.future_request)).lower()
    for text in ("geology","astronomy","meteorology","magma","nebula","jet stream","usgs","nasa","noaa","source_identity","case_identity","synthetic-spec065","owner_anchor","s1","u2","u3"):
        assert text not in code
    module=inspect.getsource(harness)
    assert "os.environ" not in module
    assert "OpenAI(" not in module
    assert ".responses.create(" not in module
    assert "urlopen" not in module and "import requests" not in module


def test_no_model_provider_or_network_execution_even_with_credentials(monkeypatch,fixtures,tmp_path):
    calls=[]
    def forbidden(*args,**kwargs):
        calls.append(True)
        raise AssertionError("network/provider attempted")
    monkeypatch.setenv("OPENAI_API_KEY","not-a-real-key")
    monkeypatch.setattr(socket.socket,"connect",forbidden)
    monkeypatch.setattr(socket,"create_connection",forbidden)
    import openai
    monkeypatch.setattr(openai,"OpenAI",forbidden)
    sub,rows=fixtures
    positive={r["stage"]:r["raw"] for r in rows if r["name"] in {"valid_truthful_subsumption","valid_shared_mechanism_abstraction","valid_admitted_handle_architecture"}}
    assert all(r["status"]=="ADMITTED" for r in harness.dry_run(sub,positive))
    harness.future_request(sub,"A",[])
    with pytest.raises(ValidationError,match="OFFLINE_ONLY"):harness.execute_live()
    harness.generate(ROOT,tmp_path)
    assert calls==[]


def test_machine_decision_records_semantic_limits_not_cognitive_success():
    report=harness.load(OUTPUT/"report.json")
    assert report["mechanical_branch"]=="VALIDATION_BOUNDARY_INSUFFICIENT"
    assert report["recommended_next_step"]=="SEMANTIC_VALIDATION_BOUNDARY_EXPERIMENT"
    assert report["owner_verdict"]=="PENDING"
    assert report["live_execution_authorized"] is False
    assert report["promotion"]=="NOT_AUTHORIZED"
    assert len(report["capability_gaps"])==4


def test_artifacts_hashes_json_links_and_secret_safety():
    report=harness.load(OUTPUT/"report.json")
    assert report["artifact_identities"]==harness.artifact_rows(OUTPUT)
    implementation=harness.load(OUTPUT/"implementation-manifest.json")
    assert implementation["implementation"]["sha256"]==harness.sha(ROOT/harness.IMPLEMENTATION)
    assert all(v==0 for v in report["execution_integrity"].values())
    for path in OUTPUT.rglob("*"):
        if not path.is_file():continue
        text=path.read_text()
        assert "sk-proj-" not in text and "OPENAI_API_KEY=" not in text
        if path.suffix==".json":json.loads(text)


def test_complete_artifact_regeneration_is_byte_identical(tmp_path):
    harness.generate(ROOT,tmp_path)
    original={p.relative_to(OUTPUT).as_posix():p.read_bytes() for p in OUTPUT.rglob("*") if p.is_file()}
    new={p.relative_to(tmp_path).as_posix():p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert original==new
    assert harness.load(tmp_path/"deterministic-regeneration.json")["result"]=="PASS"
