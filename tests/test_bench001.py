"""Synthetic contract tests only: no benchmark passage/provider/network calls."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bench001_harness as h
import bench001_prepare as freeze
from knowledge_compiler.models import ValidationError
from knowledge_compiler.openai_extractor import OpenAILLMExtractor, build_instructions, extraction_schema
from knowledge_compiler.pipeline import compile_knowledge_model
from knowledge_compiler.decomposed_extraction import freeze_entity_inventory
from knowledge_compiler.models import SourceDocument
from knowledge_compiler.openai_decomposed_extractor_v2 import stage2_v2_schema

SOURCE = "Pulse causes opening. The shell is rigid."
SYNTHETIC_CUSTODIAN_SECRET = "ba" * 32  # Mock only, never a benchmark custody secret.

def block(text="Pulse causes opening."):
    return {"text": text, "anchors": [{"quote": "Pulse causes opening."}]}

def envelope():
    return {"title": block("Opening"), "organizing_idea": block(), "overview": [block()],
            "detail": [block()], "qualifications": [], "structures": []}

def plan():
    return {"organizing_principle": block(), "relationships_dependencies": [block()],
            "examples_contrasts": [], "essential_qualifications": [], "overview_detail_mapping": [block()]}

def inventory():
    return {"symbols": [{"name": n, "description": n, "entity_type": t, "aliases": []}
                       for n,t in (("pulse","CONCEPT"),("opening","PROCESS"),("shell","OBJECT"))]}

def relation():
    return {"id": "pulse-causes-opening", "source_entity_id": "pulse", "relationship_type": "CAUSES",
            "target_entity_id": "opening", "statement": "Pulse causes opening.", "confidence": 1.0, "origin": "SOURCE"}

def claim():
    return {"id": "shell-rigid", "statement": "The shell is rigid.", "confidence": 1.0, "origin": "SOURCE",
            "evidence": [{"quote": "The shell is rigid."}]}

def extraction():
    return {"entities": [{"id": n,"name": n,"description": n,"entity_type": t,"aliases": []}
                         for n,t in (("pulse","CONCEPT"),("opening","PROCESS"),("shell","OBJECT"))],
            "claims": [claim()], "relationships": [{**relation(), "evidence": [{"quote":"Pulse causes opening."}]}], "propositions": []}

def structure():
    return {"relationships": [relation()], "comparison_conditions": [], "transfer_events": [], "missing_symbols": []}

def bindings():
    return {"claims": [claim()], "semantic_evidence_bindings": [{"semantic_object_id": "pulse-causes-opening", "evidence": [{"quote":"Pulse causes opening."}]}]}

class Response:
    def __init__(self, value, *, input_tokens=10, output_tokens=10, status="completed", model=h.MODEL):
        self.model, self.status = model, status
        self.id, self._request_id = "synthetic-response", "synthetic-request"
        self.output_text = json.dumps(value)
        self.usage = SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens,total_tokens=input_tokens+output_tokens)
    def model_dump(self, **_):
        return {"model":self.model,"status":self.status,"id":self.id,"output_text":self.output_text,"usage":vars(self.usage)}

class Fake:
    synthetic_offline = True
    max_retries = 0
    def __init__(self, values, *, response_kwargs=None):
        self.values=list(values);self.requests=[];self.responses=self;self.kwargs=response_kwargs or {}
    def count_input_tokens(self, request):
        return {"tokens": self.kwargs.get("input_tokens",10), "request_sha256": h.sha(request), "certified": True}
    def create(self, **request):
        self.requests.append(copy.deepcopy(request))
        value=self.values.pop(0)
        if isinstance(value, Exception): raise value
        return Response(value, **self.kwargs)

@pytest.mark.parametrize("arm,values,count", [
    ("S",[],0),("A",[envelope()],1),("B",[plan(),envelope()],2),
    ("C0",[extraction()],1),("C+",[inventory(),structure(),bindings(),envelope()],4)])
def test_source_blind_arm_smoke_and_common_model_parity(arm,values,count):
    fake=Fake(values);ledger=h.RunLedger();run=h.run_arm(arm,1,SOURCE,fake,ledger)
    assert run["error"] is None,run
    assert run["calls_started"]==count
    assert run["output"]["source_recovery"]["original_text"]==SOURCE
    for r in fake.requests:
        assert r["model"]==h.MODEL and r["reasoning"]=={"effort":"high"} and r["store"] is False
        assert r["timeout"]<=300
    assert [r["max_output_tokens"] for r in fake.requests]==list(h.ALLOCATIONS[arm])
    assert run["fidelity"]=="PENDING"

def test_c0_reproduces_current_semantics_and_routing_without_fixture_substitution():
    fake=Fake([extraction()]);run=h.run_arm("C0",1,SOURCE,fake,h.RunLedger())
    native=compile_knowledge_model(SOURCE,OpenAILLMExtractor(model=h.MODEL,client=Fake([extraction()])))
    assert run["partial_artifacts"]["model"]==native.to_dict()
    assert run["output"]["plans"]==h.current_output(native)["plans"]
    assert fake.requests[0]["instructions"]==build_instructions()
    assert fake.requests[0]["text"]["format"]["schema"]==extraction_schema()
    assert len(native.claims)==1
    assert len(run["output"]["plans"])==len(native.entities)+len(native.relationships)+len(native.propositions)

def test_cplus_composer_has_original_source_entire_claim_tier_and_frozen_admission():
    fake=Fake([inventory(),structure(),bindings(),envelope()])
    run=h.run_arm("C+",1,SOURCE+" Additional trace is quiet.",fake,h.RunLedger())
    assert run["error"] is None,run
    assert "Additional trace is quiet." in fake.requests[-1]["input"]
    assert '"shell-rigid"' in fake.requests[-1]["input"] and '"claims"' in fake.requests[-1]["input"]
    assert "NOT ASSUMED COMPLETE" in fake.requests[-1]["input"]
    assert "provider_request_id" not in fake.requests[-1]["input"]

@pytest.mark.parametrize("stage",[1,2,3,4])
def test_cplus_short_circuits_failures_no_retry_or_repair(stage):
    values=[inventory(),structure(),bindings(),envelope()]
    values[stage-1]=RuntimeError("synthetic boundary failure")
    fake=Fake(values);ledger=h.RunLedger();run=h.run_arm("C+",1,SOURCE,fake,ledger)
    assert run["status"]=="FAILED" and run["output"] is None
    assert len(fake.requests)==stage and len(ledger.entries)==stage
    assert ledger.entries[-1]["error"] is not None
    with pytest.raises(h.HarnessFailure,match="already attempted"):
        h.run_arm("C+",1,SOURCE,fake,ledger)

def test_cplus_bad_grounding_blocks_composer():
    b=bindings();b["claims"][0]["evidence"]=[{"quote":"fabricated quote"}]
    fake=Fake([inventory(),structure(),b,envelope()]);run=h.run_arm("C+",1,SOURCE,fake,h.RunLedger())
    assert run["status"]=="FAILED" and len(fake.requests)==3
    assert run["partial_artifacts"]["extraction"]["model"] is None

def test_prompts_do_not_route_on_source_or_domain():
    requests=[]
    for source in [SOURCE,SOURCE+" Additional trace is quiet."]:
        f=Fake([inventory(),structure(),bindings(),envelope()]);r=h.run_arm("C+",1,source,f,h.RunLedger());assert r["error"] is None
        requests.append([(x["instructions"],x["text"]["format"]["schema"]) for x in f.requests])
    assert requests[0]==requests[1]
    assert h.SHARED_TASK in h.PROMPTS["A"] and h.SHARED_TASK in h.PROMPTS["B-plan"]

@pytest.mark.parametrize("bad", ["missing", "repeated"])
def test_unique_source_anchor_fail_closed(bad):
    e=envelope();e["title"]["anchors"][0]["quote"]="not present" if bad=="missing" else "Pulse causes opening."
    source=SOURCE if bad=="missing" else SOURCE+" Pulse causes opening."
    ledger=h.RunLedger();run=h.run_arm("A",1,source,Fake([e]),ledger)
    assert run["status"]=="FAILED" and run["output"] is None
    assert ledger.entries[0]["raw_response"] is not None

@pytest.mark.parametrize("change", [lambda e:e.update(debug="model info"),lambda e:e["overview"].clear(),lambda e:e["title"]["anchors"].clear()])
def test_strict_envelope_rejects_missingness_and_debug_fields(change):
    e=envelope();change(e);run=h.run_arm("A",1,SOURCE,Fake([e]),h.RunLedger());assert run["status"]=="FAILED"

@pytest.mark.parametrize("kwargs",[{"output_tokens":12001},{"status":"incomplete"},{"model":"other-model"}])
def test_provider_usage_output_limit_and_model_mismatch_preserved(kwargs):
    ledger=h.RunLedger();run=h.run_arm("A",1,SOURCE,Fake([envelope()],response_kwargs=kwargs),ledger)
    assert run["status"]=="FAILED" and ledger.entries[0]["raw_response"] is not None

def test_certified_input_ceiling_blocks_before_call():
    f=Fake([envelope()],response_kwargs={"input_tokens":32000})
    r=h.run_arm("A",1,SOURCE,f,h.RunLedger());assert r["status"]=="FAILED" and not f.requests

def test_input_plus_output_ceiling_and_cumulative_budget():
    f=Fake([plan(),envelope()],response_kwargs={"input_tokens":15000,"output_tokens":4000})
    r=h.run_arm("B",1,SOURCE,f,h.RunLedger());assert r["status"]=="FAILED" and len(f.requests)==1

def test_missing_token_certification_is_not_replaced_by_byte_guess():
    f=Fake([envelope()]);f.count_input_tokens=lambda r:{"tokens":10,"request_sha256":h.sha(r),"certified":False}
    r=h.run_arm("A",1,SOURCE,f,h.RunLedger());assert r["status"]=="FAILED" and not f.requests

def test_elapsed_and_per_call_timeouts_with_no_followup():
    t=[0.0]
    class Late(Fake):
        def create(self,**r):
            v=super().create(**r);t[0]+=301;return v
    ledger=h.RunLedger();f=Late([plan(),envelope()]);r=h.run_arm("B",1,SOURCE,f,ledger,clock=lambda:t[0])
    assert r["status"]=="FAILED" and len(f.requests)==1
    assert ledger.entries[0]["duration_seconds"]==301
    client=h.BudgetClient("A",1,Fake([]),h.RunLedger(),clock=lambda:t[0]);t[0]+=900
    with pytest.raises(h.HarnessFailure,match="elapsed budget"):
        client.create(instructions="",text={"format":{"schema":h.envelope_schema()}})

def test_global_ceiling_and_zero_sdk_retry_policy():
    ledger=h.RunLedger(entries=[{"arm":"other","source_slot":0,"stage":0}]*40)
    f=Fake([envelope()]);r=h.run_arm("A",1,SOURCE,f,ledger);assert r["status"]=="FAILED" and not f.requests
    f=Fake([envelope()]);f.max_retries=1;r=h.run_arm("A",1,SOURCE,f,h.RunLedger());assert r["status"]=="FAILED" and not f.requests

def test_request_start_is_durable_before_transmission():
    snapshots=[];ledger=h.RunLedger(sink=lambda e:snapshots.append(e))
    f=Fake([RuntimeError("offline synthetic error")]);r=h.run_arm("A",1,SOURCE,f,ledger)
    assert snapshots[0][0]["status"]=="REQUEST_STARTED"
    assert snapshots[-1][0]["status"]=="FAILED"
    assert r["calls_started"]==1

def test_real_transport_and_self_asserted_live_authority_denied():
    f=Fake([envelope()]);f.synthetic_offline=False
    assert h.run_arm("A",1,SOURCE,f,h.RunLedger())["status"]=="FAILED" and not f.requests
    assert h.run_arm("A",1,SOURCE,f,h.RunLedger(),gate=h.ExecutionGate(False,{}))["status"]=="FAILED"
    with pytest.raises(h.HarnessFailure,match="durable"):
        h.RunLedger().require_durable(h.ExecutionGate(False))

def test_blinding_requires_complete_denominator_and_keeps_metrics_private():
    with pytest.raises(h.HarnessFailure,match="incomplete"):
        h.blind([],freeze.SEED,SYNTHETIC_CUSTODIAN_SECRET)
    cells=[{"arm":a,"source_slot":s,"status":"FAILED","output":None,"metrics":{"cost":123}} for s in range(1,6) for a in h.ARMS]
    public,key=h.blind(cells,freeze.SEED,SYNTHETIC_CUSTODIAN_SECRET)
    assert len(public)==25 and key["release_system_metrics"] is False
    assert all(set(r)=={"source_slot","label","available","html"} for r in public)
    orders=key["counterbalanced_orders"]
    for label in key["identity_key"].values():
        assert sorted(order.index(label) for order in orders.values())==list(range(5))

def test_missingness_and_fidelity_adjustment_are_not_a_winner():
    failed={"status":"FAILED","fidelity":"UNRESOLVED"}
    good={"status":"COMPLETE_PENDING_FIDELITY","fidelity":"ACCEPTABLE"}
    bad={"status":"COMPLETE_PENDING_FIDELITY","fidelity":"MATERIAL_FAILURE"}
    assert h.pair_result(failed,failed,"LEFT")=="NEITHER"
    assert h.pair_result(bad,good,"LEFT")=="NO_FIDELITY_ADJUSTED_WIN"
    with pytest.raises(h.HarnessFailure,match="pending"):
        h.pair_result({"status":"SOURCE_CONTROL","fidelity":"PENDING"},good,"LEFT")

def test_neutral_literal_renderer_no_script_injection_or_architecture_metadata():
    f=Fake([envelope()]);r=h.run_arm("A",1,SOURCE,f,h.RunLedger());r["output"]["title"]["text"]="<script>oops</script>"
    text=h.render_output(r["output"])
    assert "<script>oops" not in text and "&lt;script&gt;" in text
    assert "Original passage" in text and SOURCE in text
    assert not any(s in text for s in [h.MODEL,"provider_request_id","semantic_core","arm_label"])

def test_frozen_native_renderer_function_slices_and_no_bootstrap_fetch():
    outputs=freeze.build(ROOT)
    for name,path,stop in [
        ("current-native-plan.js","representation_strategy_assets/representation-strategy.js","function strategyRender(){"),
        ("current-native-diagram.js","diagram_canvas_assets/diagram-canvas.js","function diagramSyncAttention(){")]:
        raw=(ROOT/"src/knowledge_compiler"/path).read_text();native=outputs["renderer/"+name]
        assert native==raw[:raw.index(stop)].encode()
        assert b"fetch(" not in native

def test_dynamic_schemas_are_frozen_factories_not_source_tuning():
    inv=freeze_entity_inventory(inventory(),SourceDocument("synthetic",SOURCE))
    schema=stage2_v2_schema(inv)
    assert schema["properties"]["relationships"]["items"]["properties"]["source_entity_id"]["enum"]==sorted(inv.ids)
    h.validate_schema(structure(),schema)
    changed=structure();changed["relationships"][0]["source_entity_id"]="invented"
    with pytest.raises(ValidationError):h.validate_schema(changed,schema)

def test_deterministic_freeze_protected_state_templates_and_call_budget():
    one=freeze.build(ROOT);assert one==freeze.build(ROOT)
    for name,data in one.items():assert (ROOT/freeze.OUT/name).read_bytes()==data
    ledger=json.loads(one["future-40-call-ledger.json"])
    assert len(ledger["slots"])==40 and ledger["provider_calls_started"]==0
    assert all(r["source_sha256"] is None and r["status"]=="NOT_EXECUTED" for r in ledger["slots"])
    custody=json.loads(one["custody-contract.json"]);assert custody["identity_key"] is None
    for p in (ROOT/freeze.OUT/"templates").glob("*.json"):json.loads(p.read_text())
    frozen=(ROOT/freeze.OUT/"IA-001-BENCH-v1-frozen-contract.md").read_text()
    assert "at least 4/5" in frozen and "No production promotion from five passages" in frozen

def test_opaque_bundle_does_not_export_identity_key_or_metrics():
    cells=[{"arm":a,"source_slot":s,"output":None,"private_cost":987} for s in range(1,6) for a in h.ARMS]
    cells[3]=h.run_arm("C0",1,SOURCE,Fake([extraction()]),h.RunLedger())
    assets={name.removeprefix("renderer/"):raw for name,raw in freeze.build(ROOT).items()
            if name.startswith("renderer/") and not name.endswith(".html")}
    files,key=h.export_blind_bundle(cells,freeze.SEED,SYNTHETIC_CUSTODIAN_SECRET,assets)
    assert len([n for n in files if n.endswith(".html")])==25
    assert all(n.startswith(("asset-","source-","review-order")) for n in files)
    assert "identity_key" not in files and key["release_system_metrics"] is False
    assert all(files[new]==assets[old] for old,new in key["asset_rename_map"].items())
    page=files[next(n for n in files if n.endswith(".html") and b"renderCurrent(" in files[n])]
    assert b"c0-adapter.js" not in page and b"current-native-plan.js" not in page
    assert b"private_cost" not in page and b"provider_request_id" not in page

def test_public_seed_alone_cannot_assign_a_blind_identity_key():
    cells=[{"arm":a,"source_slot":s,"output":None} for s in range(1,6) for a in h.ARMS]
    with pytest.raises(h.HarnessFailure,match="public seed"):
        h.blind(cells,freeze.SEED,freeze.SEED)
    _,first=h.blind(cells,freeze.SEED,SYNTHETIC_CUSTODIAN_SECRET)
    _,second=h.blind(cells,freeze.SEED,"cd"*32)
    assert first["identity_key"]!=second["identity_key"]

def test_source_control_and_pretransmission_failure_cells_are_preserved():
    stored=[];ledger=h.RunLedger(cell_sink=lambda cells:stored.append(cells))
    h.run_arm("S",1,SOURCE,Fake([]),ledger)
    bad=Fake([]);bad.max_retries=1
    h.run_arm("A",1,SOURCE,bad,ledger)
    assert len(stored[-1])==2 and not ledger.entries
    assert stored[-1][0]["transformation_gain"]==0
    assert stored[-1][1]["status"]=="FAILED" and stored[-1][1]["calls_started"]==0
    restored=h.RunLedger(cells=stored[-1])
    with pytest.raises(h.HarnessFailure,match="already attempted"):
        h.run_arm("A",1,SOURCE,Fake([envelope()]),restored)

def test_source_identity_must_match_exact_original_bytes_and_slot():
    gate=h.ExecutionGate(offline_only=False,source_manifest={"sources":[
        {"slot":s,"passage_sha256":h.hashlib.sha256(SOURCE.encode()).hexdigest()} for s in range(1,6)]})
    gate.check_source(1,SOURCE)
    with pytest.raises(h.HarnessFailure,match="not the frozen"):
        gate.check_source(1,SOURCE+" ")
    gate.source_manifest["sources"].pop()
    with pytest.raises(h.HarnessFailure,match="five-source"):
        gate.check_source(1,SOURCE)

def test_lock_validates_actual_bytes_and_runtime_code(tmp_path):
    folder=tmp_path/h.FREEZE_DIRECTORY;folder.mkdir(parents=True)
    code=b"synthetic executable identity"; (tmp_path/"code.py").write_bytes(code)
    deps=freeze.stable({"files":[{"path":"code.py","bytes":len(code),"sha256":h.hashlib.sha256(code).hexdigest()}]})
    (folder/"dependency-executable-manifest.json").write_bytes(deps)
    lock=freeze.stable({"version":h.VERSION,"files":{"dependency-executable-manifest.json":
        {"bytes":len(deps),"sha256":h.hashlib.sha256(deps).hexdigest()}}})
    (folder/"lock.json").write_bytes(lock);digest=h.hashlib.sha256(lock).hexdigest()
    h.verify_frozen_harness(tmp_path,digest)
    (tmp_path/"code.py").write_bytes(code+b" drift")
    with pytest.raises(h.HarnessFailure,match="executable identity"):
        h.verify_frozen_harness(tmp_path,digest)
    with pytest.raises(h.HarnessFailure,match="lock identity"):
        h.verify_frozen_harness(tmp_path,"0"*64)

def test_frozen_lock_and_local_sdk_request_shape():
    import inspect
    from openai.resources.responses.responses import Responses
    signature=inspect.signature(Responses.create).parameters
    assert {"model","reasoning","store","text","max_output_tokens","timeout"}<=set(signature)
    lock=(ROOT/freeze.OUT/"lock.json").read_bytes()
    h.verify_frozen_harness(ROOT,h.hashlib.sha256(lock).hexdigest())

def test_unrenderable_current_compiler_is_not_replaced_by_generated_prose():
    value={"entities":[],"relationships":[],"propositions":[],"claims":[claim()]}
    fake=Fake([value]);r=h.run_arm("C0",1,SOURCE,fake,h.RunLedger())
    assert r["status"]=="FAILED" and r["output"] is None and len(fake.requests)==1
    assert r["partial_artifacts"]["model"]["claims"]

def test_usage_missing_or_inconsistent_preserves_raw_failure():
    for broken in [{}, {"input_tokens":10,"output_tokens":10,"total_tokens":1}]:
        class BadUsage(Fake):
            def create(self,**request):
                response=super().create(**request)
                response.usage=SimpleNamespace(**broken)
                return response
        ledger=h.RunLedger();r=h.run_arm("B",1,SOURCE,BadUsage([plan(),envelope()]),ledger)
        assert r["status"]=="FAILED" and len(ledger.entries)==1
        assert ledger.entries[0]["raw_response"]["usage"]==broken

def test_every_supported_structure_preserves_literal_cells_and_source_traces():
    for kind in h.envelope_schema()["properties"]["structures"]["items"]["properties"]["kind"]["enum"]:
        e=envelope();e["structures"]=[{"kind":kind,"caption":block("Supported relation"),"rows":[[block("Pulse → opening")]]}]
        run=h.run_arm("A",1,SOURCE,Fake([e]),h.RunLedger())
        assert run["error"] is None
        text=h.render_output(run["output"])
        assert "Pulse → opening" in text and "Supported relation" in text and "Source support" in text

def test_frozen_decision_rules_are_exact_transcription_not_automated_verdict():
    artifacts=freeze.build(ROOT);rules=json.loads(artifacts["decision-rules.json"])
    frozen=artifacts["IA-001-BENCH-v1-frozen-contract.md"].decode()
    assert rules["exact_section_transcription"]==frozen.split("## Frozen decision rule\n",1)[1].split("## Required outputs",1)[0].strip()
    assert rules["automated_winner_assignment"] is False and rules["threshold_changes"] is False
