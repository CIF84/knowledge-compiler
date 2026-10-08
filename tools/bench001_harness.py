"""IA-001-BENCH-v1 isolated source-blind harness; no transport construction.

The readiness packet may exercise synthetic offline transports only. A future
approved execution packet must supply source/fidelity freezes, model verification,
certified token accounting and a zero-retry timeout-respecting transport.
"""
from __future__ import annotations

import copy
import hashlib
import html
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

from knowledge_compiler.decomposed_extraction import GateStatus
from knowledge_compiler.decomposed_extraction_v2 import run_candidate_b_v2
from knowledge_compiler.models import ValidationError
from knowledge_compiler.normalize import normalize_document
from knowledge_compiler.openai_decomposed_extractor_v2 import OpenAICandidateBV2Extractor
from knowledge_compiler.openai_extractor import OpenAILLMExtractor, resolve_evidence_quote
from knowledge_compiler.pipeline import compile_knowledge_model
from knowledge_compiler.semantic_representation_compiler import compile_semantic_representation
from knowledge_compiler.diagram_canvas_evaluation import _layout_for_plan
from knowledge_compiler.control_plane import validate_control_plane

VERSION = "IA-001-BENCH-v1"
MODEL = "gpt-6.1-sol"
FREEZE_DIRECTORY = "audits/independent-architecture-audit-001/benchmark-readiness-v1"
ARMS = ("S", "A", "B", "C0", "C+")
ALLOCATIONS = {"S": (), "A": (12000,), "B": (4000, 8000),
               "C0": (12000,), "C+": (2000, 3000, 3000, 4000)}
SHARED_TASK = "Using only this passage, help a new learner form and later retrieve a coherent explanation. Show the organizing idea and necessary relationships, preserve conditions and uncertainty, and keep detail and support accessible. Use prose where it works; use a diagram, table or causal sequence only where its encoded meaning is supported. Do not add outside facts or pretend a conceptual exercise is an executable simulation."
ENVELOPE_RULES = """Return only the neutral learner envelope. Overview and detail are peer views,
not destructive sequential shortenings. Every learner-visible title, organizing idea,
paragraph, qualification, structure caption and cell is a semantic claim: attach at
least one exact, uniquely occurring verbatim source quote. Labels, grouping, arrows
and tables require support too. Optional structures may be absent. Preserve important
conditions, uncertainty and explanatory dependencies. Do not add outside facts.
No author, model, arm, architecture, compiler/debug metadata or unsupported executable
simulation claims in the learner output. Exact anchors demonstrate recovery, not
semantic entailment: independent fidelity review will assess every representation."""
PROMPTS = {
    "A": SHARED_TASK + "\n\n" + ENVELOPE_RULES,
    "B-plan": SHARED_TASK + "\n\nReturn a small source-grounded explanation plan: organizing principle, necessary relationships/dependencies, examples/contrasts, essential qualifications, and overview/detail mapping. Attach unique exact supporting source quotes to every item. Do not generate the learner output yet; no outside facts or metadata.",
    "B-compose": SHARED_TASK + "\n\nUse the original source and the frozen plan. A plan is an aid, never the sole truth; source controls fidelity.\n" + ENVELOPE_RULES,
    "C+-compose": SHARED_TASK + "\n\nUse BOTH the admitted semantic store (including all claims) AND the original source. The store is not assumed complete. Preserve useful explanatory context, missing-in-store meaning, conditions and relationships from the source without modifying the store or claiming unsupported inference.\n" + ENVELOPE_RULES,
}

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value).encode()).hexdigest()

def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}

def arr(item):
    return {"type": "array", "items": item}

def block():
    return obj({"text": {"type": "string", "minLength": 1},
                "anchors": {**arr(obj({"quote": {"type": "string", "minLength": 1}})), "minItems": 1}})

def envelope_schema():
    b = block()
    structure = obj({"kind": {"type": "string", "enum": ["HIERARCHY", "PROCESS", "CAUSAL", "COMPARISON", "TABLE", "ASCII"]},
                     "caption": b, "rows": {**arr({**arr(b), "minItems": 1}), "minItems": 1}})
    return obj({"title": b, "organizing_idea": b, "overview": {**arr(b), "minItems": 1},
                "detail": {**arr(b), "minItems": 1}, "qualifications": arr(b), "structures": arr(structure)})

def plan_schema():
    b = block()
    return obj({"organizing_principle": b, "relationships_dependencies": arr(b),
                "examples_contrasts": arr(b), "essential_qualifications": arr(b),
                "overview_detail_mapping": {**arr(b), "minItems": 1}})

def validate_schema(value, schema):
    """Restricted strict JSON-schema evaluator for frozen request/response shapes."""
    if "anyOf" in schema:
        for alternative in schema["anyOf"]:
            try:
                validate_schema(value, alternative)
                return
            except ValidationError:
                pass
        raise ValidationError("schema alternatives failed")
    kind = schema["type"]
    checks = {"object": lambda: isinstance(value, dict), "array": lambda: isinstance(value, list),
              "string": lambda: isinstance(value, str), "number": lambda: type(value) in (int, float),
              "integer": lambda: type(value) is int, "null": lambda: value is None, "boolean": lambda: type(value) is bool}
    if not checks[kind]():
        raise ValidationError("schema type mismatch")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError("schema enum mismatch")
    if kind == "object":
        if set(value) != set(schema["properties"]):
            raise ValidationError("unexpected/missing object fields")
        for k, v in value.items():
            validate_schema(v, schema["properties"][k])
    elif kind == "array":
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", float("inf")):
            raise ValidationError("schema array bounds")
        for v in value:
            validate_schema(v, schema["items"])
    elif kind == "string" and len(value) < schema.get("minLength", 0):
        raise ValidationError("empty learner text/quote")
    elif kind in {"number", "integer"} and not schema.get("minimum", -float("inf")) <= value <= schema.get("maximum", float("inf")):
        raise ValidationError("schema number bounds")

def ground_blocks(value, source):
    """Exact backward recovery only, not semantic-judge admission."""
    doc = normalize_document(source)
    if isinstance(value, dict):
        if set(value) == {"text", "anchors"}:
            return {"text": value["text"], "anchors": [
                {**resolve_evidence_quote(doc, a["quote"]), "source_sha256": hashlib.sha256(doc.text.encode()).hexdigest()}
                for a in value["anchors"]]}
        return {k: ground_blocks(v, source) for k, v in value.items()}
    if isinstance(value, list):
        return [ground_blocks(v, source) for v in value]
    return value

class HarnessFailure(ValidationError):
    pass

def verify_frozen_harness(root, expected_lock_sha256):
    """Verify bytes, not a caller's assertion that a freeze was verified."""
    folder = root / FREEZE_DIRECTORY
    raw = (folder / "lock.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_lock_sha256:
        raise HarnessFailure("harness lock identity mismatch")
    lock = json.loads(raw)
    if lock["version"] != VERSION:
        raise HarnessFailure("benchmark version mismatch")
    for name, identity in lock["files"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise HarnessFailure("invalid freeze path")
        data = (folder / path).read_bytes()
        if len(data) != identity["bytes"] or hashlib.sha256(data).hexdigest() != identity["sha256"]:
            raise HarnessFailure("frozen artifact identity mismatch: " + name)
    dependencies = json.loads((folder / "dependency-executable-manifest.json").read_bytes())
    for identity in dependencies["files"]:
        data = (root / identity["path"]).read_bytes()
        if len(data) != identity["bytes"] or hashlib.sha256(data).hexdigest() != identity["sha256"]:
            raise HarnessFailure("frozen executable identity mismatch: " + identity["path"])

@dataclass
class ExecutionGate:
    """No implicit permission from credentials, a manifest template or a client."""
    offline_only: bool = True
    authority_receipt: dict | None = None
    source_manifest: dict | None = None

    def check(self, transport):
        if self.offline_only:
            if getattr(transport, "synthetic_offline", False) is not True:
                raise HarnessFailure("OFFLINE_ONLY: real transport denied")
            return
        state = validate_control_plane(Path(__file__).resolve().parents[1])
        if state.control is None or state.control.authority != "LIVE_CALLS_EXPLICITLY_BOUNDED":
            raise HarnessFailure("repository control plane does not authorize live benchmark execution")
        receipt = self.authority_receipt or {}
        required = {"version", "source_freeze_sha256", "fidelity_keys_sha256", "execution_manifest_sha256",
                    "model", "reasoning", "store", "sdk_retries", "remote_support_verified", "source_count",
                    "maximum_calls", "authority", "token_counter_sha256", "harness_lock_sha256",
                    "custodian_secret_commitment_sha256"}
        if set(receipt) != required or any(not receipt[k] for k in ("source_freeze_sha256", "fidelity_keys_sha256", "execution_manifest_sha256", "token_counter_sha256")):
            raise HarnessFailure("missing future execution preconditions")
        if (receipt["version"], receipt["model"], receipt["reasoning"], receipt["store"], receipt["sdk_retries"],
            receipt["remote_support_verified"], receipt["source_count"], receipt["maximum_calls"], receipt["authority"]) != (VERSION, MODEL, "high", False, 0, True, 5, 40, "LIVE_CALLS_EXPLICITLY_BOUNDED"):
            raise HarnessFailure("invalid future execution contract")
        contract = (Path(__file__).resolve().parents[1] / state.packet).read_text()
        if VERSION not in contract or any(receipt[k] not in contract for k in
                ("execution_manifest_sha256", "source_freeze_sha256", "fidelity_keys_sha256", "harness_lock_sha256", "custodian_secret_commitment_sha256")):
            raise HarnessFailure("live authority is not bound to this exact benchmark execution manifest")
        verify_frozen_harness(Path(__file__).resolve().parents[1], receipt["harness_lock_sha256"])
        if sha(self.source_manifest) != receipt["source_freeze_sha256"]:
            raise HarnessFailure("source manifest does not match approved identity")
        if getattr(transport, "token_counter_sha256", None) != receipt["token_counter_sha256"]:
            raise HarnessFailure("token counter implementation identity mismatch")

    def check_source(self, slot, source):
        if self.offline_only:
            return
        manifest = self.source_manifest or {}
        rows = manifest.get("sources", [])
        if len(rows) != 5 or {r.get("slot") for r in rows} != set(range(1,6)):
            raise HarnessFailure("five-source manifest missing or malformed")
        expected = next(r for r in rows if r["slot"] == slot)
        if hashlib.sha256(source.encode()).hexdigest() != expected.get("passage_sha256"):
            raise HarnessFailure("source content is not the frozen source for this slot")

@dataclass
class RunLedger:
    entries: list = field(default_factory=list)
    completed_cells: set = field(default_factory=set)
    sink: object = None
    cells: list = field(default_factory=list)
    cell_sink: object = None

    def __post_init__(self):
        self.completed_cells.update((r["source_slot"], r["arm"]) for r in self.cells)

    def persist(self):
        if self.sink is not None:
            self.sink(copy.deepcopy(self.entries))

    def require_durable(self, gate):
        if not gate.offline_only and (not callable(self.sink) or not callable(self.cell_sink)):
            raise HarnessFailure("live execution requires private durable request and cell ledger sinks")

    def record_cell(self, result):
        self.cells.append(copy.deepcopy(result))
        if self.cell_sink is not None:
            self.cell_sink(copy.deepcopy(self.cells))

class BudgetClient:
    """One cell, all stages; request-start ledger precedes any transmission."""
    def __init__(self, arm, slot, transport, ledger, gate=None, clock=time.monotonic):
        if arm not in ALLOCATIONS or type(slot) is not int or not 1 <= slot <= 5:
            raise HarnessFailure("invalid arm/source slot")
        self.arm, self.slot, self.transport, self.ledger = arm, slot, transport, ledger
        self.gate, self.clock = gate or ExecutionGate(), clock
        self.started, self.used, self.output_used, self.calls = clock(), 0, 0, 0
        self.failed = False
        self.responses = self

    def create(self, **incoming):
        if self.failed:
            raise HarnessFailure("failed cell cannot retry")
        self.gate.check(self.transport)
        self.ledger.require_durable(self.gate)
        elapsed = self.clock() - self.started
        if self.calls >= len(ALLOCATIONS[self.arm]) or elapsed >= 900:
            self.failed = True
            raise HarnessFailure("call/elapsed budget exhausted")
        if any(e["arm"] == self.arm and e["source_slot"] == self.slot and e["stage"] == self.calls + 1 for e in self.ledger.entries):
            raise HarnessFailure("duplicate stage: zero retries")
        if len(self.ledger.entries) >= 40:
            raise HarnessFailure("global 40-call ceiling exhausted")
        # Only plumbing fields differ from C0/C+ native adapters; their prompt,
        # schema, input and semantic admission code remain exactly unchanged.
        request = {**incoming, "model": MODEL, "reasoning": {"effort": "high"}, "store": False,
                   "max_output_tokens": ALLOCATIONS[self.arm][self.calls], "timeout": min(300, 900 - elapsed)}
        if getattr(self.transport, "max_retries", None) != 0:
            raise HarnessFailure("transport must disable SDK retries")
        count = self.transport.count_input_tokens(copy.deepcopy(request))
        if (not isinstance(count, dict) or set(count) != {"tokens", "request_sha256", "certified"}
                or type(count["tokens"]) is not int or count["tokens"] < 0
                or count["request_sha256"] != sha(request) or count["certified"] is not True):
            raise HarnessFailure("input-token counter not certified for exact request")
        remaining = 32000 - self.used - count["tokens"]
        request["max_output_tokens"] = min(request["max_output_tokens"], 12000 - self.output_used, remaining)
        if request["max_output_tokens"] <= 0:
            self.failed = True
            raise HarnessFailure("token budget exhausted before transmission")
        # Counter identity applies to content, including schema/prompt/framing.
        final_count = self.transport.count_input_tokens(copy.deepcopy(request))
        if final_count != {"tokens": count["tokens"], "request_sha256": sha(request), "certified": True}:
            raise HarnessFailure("token counter changed content count after cap binding")
        e = {"arm": self.arm, "source_slot": self.slot, "stage": self.calls + 1,
             "request_sha256": sha(request), "prompt_sha256": sha(request["instructions"]),
             "schema_sha256": sha(request["text"]["format"]["schema"]), "request": copy.deepcopy(request),
             "status": "REQUEST_STARTED", "raw_response": None, "usage": None,
             "error": None, "retries": 0, "input_token_count": count["tokens"]}
        self.ledger.entries.append(e)
        self.ledger.persist()
        self.calls += 1
        start = self.clock()
        try:
            response = self.transport.create(**request)
            raw = response.model_dump(mode="json") if hasattr(response, "model_dump") else copy.deepcopy(vars(response))
            e["raw_response"] = raw
            e["provider_request_id"] = getattr(response, "_request_id", None)
            e["response_id"] = getattr(response, "id", None)
            e["duration_seconds"] = self.clock() - start
            e["elapsed_seconds"] = self.clock() - self.started
            usage = raw.get("usage")
            e["usage"] = usage
            if getattr(response, "model", None) != MODEL:
                raise HarnessFailure("common model mismatch: no substitution")
            if getattr(response, "status", None) != "completed":
                raise HarnessFailure("incomplete/refused/timeout response")
            if not isinstance(usage, dict) or any(type(usage.get(k)) is not int or usage[k] < 0 for k in ("input_tokens", "output_tokens", "total_tokens")):
                raise HarnessFailure("missing/invalid token usage")
            if usage["total_tokens"] != usage["input_tokens"] + usage["output_tokens"]:
                raise HarnessFailure("inconsistent usage")
            self.used += usage["total_tokens"]
            self.output_used += usage["output_tokens"]
            if (usage["input_tokens"] > count["tokens"] or usage["output_tokens"] > request["max_output_tokens"]
                    or self.used > 32000 or self.output_used > 12000):
                raise HarnessFailure("token budget/counter violation")
            if e["duration_seconds"] >= request["timeout"] or e["elapsed_seconds"] >= 900:
                raise HarnessFailure("timeout/arm elapsed exhaustion")
            validate_schema(json.loads(response.output_text), request["text"]["format"]["schema"])
            e["status"] = "RESPONSE_RECEIVED"
            return response
        except Exception as exc:
            self.failed = True
            e["status"] = "FAILED"
            e["error"] = {"type": type(exc).__name__, "message": str(exc)}
            if getattr(exc, "request_id", None) is not None:
                e["provider_request_id"] = exc.request_id
            e.setdefault("duration_seconds", self.clock() - start)
            raise
        finally:
            self.ledger.persist()

def request_envelope(client, prompt, schema, input_text, source):
    response = client.create(instructions=prompt, input=input_text,
        text={"format": {"type": "json_schema", "name": "learner_envelope", "strict": True, "schema": schema}})
    raw = json.loads(response.output_text)
    validate_schema(raw, schema)
    return raw, ground_blocks(raw, source)

def current_output(model):
    """Current routing verbatim; claims are NOT silently upgraded into foci."""
    decisions = []
    for kind, items in (("concept", model.entities), ("canonical", model.relationships), ("proposition", model.propositions)):
        for item in sorted(items, key=lambda i: i.id):
            decision = compile_semantic_representation(model, kind, item.id).to_dict()
            plan = decision["representation_plan"]
            decisions.append({"plan": plan, "layout": _layout_for_plan(decision["decision_id"], plan) if plan else None})
    if not decisions or any(r["plan"] is None for r in decisions):
        raise HarnessFailure("current compiler has no complete compatible renderer output; no substitute")
    return {"plans": decisions, "source": model.document.text}

def run_arm(arm, slot, source, transport, ledger, *, gate=None, clock=time.monotonic):
    key = (slot, arm)
    if key in ledger.completed_cells:
        raise HarnessFailure("cell already attempted; zero retries")
    ledger.completed_cells.add(key)
    client = BudgetClient(arm, slot, transport, ledger, gate, clock)
    result = {"arm": arm, "source_slot": slot, "status": "FAILED", "output": None,
              "partial_artifacts": {}, "error": None, "fidelity": "PENDING", "transformation_gain": None}
    try:
        if not isinstance(source, str) or not source.strip():
            raise HarnessFailure("missing source")
        recovery = {"original_text": source, "original_sha256": hashlib.sha256(source.encode()).hexdigest(),
                    "normalized_text": normalize_document(source).text,
                    "normalized_sha256": hashlib.sha256(normalize_document(source).text.encode()).hexdigest()}
        result["partial_artifacts"]["source_recovery"] = recovery
        client.gate.check(transport)
        ledger.require_durable(client.gate)
        client.gate.check_source(slot, source)
        if arm == "S":
            result.update(status="SOURCE_CONTROL", output={"source": source}, transformation_gain=0)
        elif arm in {"A", "B"}:
            input_text = source
            if arm == "B":
                raw, plan = request_envelope(client, PROMPTS["B-plan"], plan_schema(), source, source)
                result["partial_artifacts"]["plan"] = raw
                input_text = "ORIGINAL SOURCE:\n" + source + "\nFROZEN PLAN:\n" + canonical(plan)
            raw, output = request_envelope(client, PROMPTS["A" if arm == "A" else "B-compose"], envelope_schema(), input_text, source)
            result["partial_artifacts"]["envelope"] = raw
            result.update(status="COMPLETE_PENDING_FIDELITY", output=output)
        elif arm == "C0":
            model = compile_knowledge_model(source, OpenAILLMExtractor(model=MODEL, client=client))
            result["partial_artifacts"]["model"] = model.to_dict()
            result.update(status="COMPLETE_PENDING_FIDELITY", output=current_output(model))
        elif arm == "C+":
            extractor = OpenAICandidateBV2Extractor(model=MODEL, client=client)
            extractor.live_capable = False  # real transport still checked at every request
            run = run_candidate_b_v2(source, extractor, source_metadata={"source_id": f"source-slot-{slot}"})
            result["partial_artifacts"]["extraction"] = run.to_dict()
            if run.status is not GateStatus.PASS or run.model is None:
                raise HarnessFailure("C+ typed admission failed; composer not called")
            store = run.model.to_dict()
            store.pop("metadata", None)
            store["document"].pop("metadata", None)
            input_text = "ORIGINAL SOURCE:\n" + source + "\nADMITTED SEMANTIC STORE (NOT ASSUMED COMPLETE):\n" + canonical(store)
            raw, output = request_envelope(client, PROMPTS["C+-compose"], envelope_schema(), input_text, source)
            result["partial_artifacts"]["envelope"] = raw
            result.update(status="COMPLETE_PENDING_FIDELITY", output=output)
        if result["output"] is not None:
            result["output"]["source_recovery"] = recovery
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
    result["calls_started"] = client.calls
    result["elapsed_seconds"] = clock() - client.started
    if result["elapsed_seconds"] >= 900:
        result.update(status="FAILED", output=None, error={"type": "Timeout", "message": "arm elapsed budget exhausted"})
    ledger.record_cell(result)
    return result

def pair_result(left, right, preferred):
    """No preferences inferred. Fixed missingness/fidelity adjustment only."""
    def eligible(cell):
        return cell["status"] in {"SOURCE_CONTROL", "COMPLETE_PENDING_FIDELITY"} and cell["fidelity"] == "ACCEPTABLE"
    if any(cell["status"] in {"SOURCE_CONTROL", "COMPLETE_PENDING_FIDELITY"} and cell["fidelity"] == "PENDING" for cell in (left, right)):
        raise HarnessFailure("fidelity review is pending; no decision")
    if not eligible(left) and not eligible(right):
        return "NEITHER"
    if preferred not in {"LEFT", "RIGHT", "TIE", "NEITHER", "INSUFFICIENT_EVIDENCE"}:
        raise HarnessFailure("invalid locked preference")
    if preferred == "LEFT" and not eligible(left) or preferred == "RIGHT" and not eligible(right):
        return "NO_FIDELITY_ADJUSTED_WIN"
    return preferred

def blind(cells, seed, custodian_secret):
    """Called only by independent custodian after 25 output/failure cells exist."""
    if len(cells) != 25 or {(r["source_slot"], r["arm"]) for r in cells} != {(s,a) for s in range(1,6) for a in ARMS}:
        raise HarnessFailure("outputs/missingness cells incomplete; do not assign identities")
    if not isinstance(seed, str) or len(seed) != 64 or any(c not in "0123456789abcdef" for c in seed):
        raise HarnessFailure("seed identity invalid")
    if (not isinstance(custodian_secret, str) or len(custodian_secret) != 64
            or any(c not in "0123456789abcdef" for c in custodian_secret) or custodian_secret == seed):
        raise HarnessFailure("independent custodian secret required; public seed cannot seal identity")
    # Custodian freezes the secret commitment before source exposure, keeping the
    # entropy private. A published seed alone would reveal identities and order.
    ordering = sorted(ARMS, key=lambda a: sha({"seed": seed, "secret": custodian_secret, "arm": a}))
    key = {a: "View-" + sha({"seed": seed, "secret": custodian_secret, "identity": a})[:12] for a in ARMS}
    private = {"identity_key": key, "counterbalanced_orders": {
        str(s): [key[a] for a in ordering[s-1:] + ordering[:s-1]] for s in range(1,6)},
        "release_system_metrics": False}
    public = [{"source_slot": r["source_slot"], "label": key[r["arm"]],
               "available": r["output"] is not None, "html": render_output(r["output"])} for r in cells]
    return public, private

def export_blind_bundle(cells, seed, custodian_secret, assets):
    """Pure bundle/key separation; custodian keeps private return outside serving.

    No disk writes or source retrieval; never called on benchmark outputs during
    readiness. Rewrites asset filenames/links only, not content or semantics.
    """
    public, private = blind(cells, seed, custodian_secret)
    aliases = {name: "asset-" + hashlib.sha256(raw).hexdigest()[:20] + Path(name).suffix for name,raw in assets.items()}
    files = {aliases[name]: raw for name,raw in assets.items()}
    for row in public:
        text = row["html"]
        for old,new in aliases.items():
            text = text.replace("'"+old+"'", "'"+new+"'").replace('"'+old+'"', '"'+new+'"')
        files[f"source-{row['source_slot']:02d}-{row['label']}.html"] = text.encode()
    files["review-order.json"] = canonical(private["counterbalanced_orders"]).encode()
    private["asset_rename_map"] = aliases
    return files, private

def render_output(output):
    if output is None:
        return "<!doctype html><html><meta charset='utf-8'><title>Learning view</title><main><p>No usable output was produced.</p></main></html>"
    if "plans" in output:
        payload = copy.deepcopy(output)
        for row in payload["plans"]:
            row["plan"] = {k: v for k,v in row["plan"].items() if k in {
                "strategy_type", "title", "payload", "evidence_refs", "warnings", "semantic_focus_identity"}}
        data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
        return ("<!doctype html><html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Learning view</title>"
                "<link rel='stylesheet' href='representation-strategy.css'><link rel='stylesheet' href='diagram-canvas.css'><link rel='stylesheet' href='neutral.css'>"
                "<body class='spec038-diagram-canvas'><main><div id='current'></div><details><summary>Original passage</summary><pre>"
                + html.escape(output["source_recovery"]["original_text"]) + "</pre></details></main>"
                "<script src='current-native-plan.js'></script><script src='current-native-diagram.js'></script><script src='c0-adapter.js'></script>"
                "<script>renderCurrent(" + data + ");</script></body></html>")
    if "source" in output:
        return "<!doctype html><html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Learning view</title><link rel='stylesheet' href='neutral.css'><main><pre>" + html.escape(output["source"]) + "</pre></main></html>"
    return render_envelope(output)

def render_envelope(output):
    """Neutral literal HTML, no arm identity, script or metrics payload."""
    def b(block):
        trace = "".join("<blockquote>" + html.escape(a["quote"]) + "</blockquote>" for a in block["anchors"])
        return "<p>" + html.escape(block["text"]) + "</p><details><summary>Source support</summary>" + trace + "</details>"
    text = "<h1>" + html.escape(output["title"]["text"]) + "</h1>" + b(output["organizing_idea"])
    text += "<details><summary>Title support</summary>" + b(output["title"]) + "</details>"
    for view in ("overview", "detail", "qualifications"):
        text += "<section><h2>" + view.title() + "</h2>" + "".join(b(v) for v in output[view]) + "</section>"
    for structure in output["structures"]:
        text += "<section>" + b(structure["caption"])
        text += "<table>" + "".join("<tr>" + "".join("<td>"+b(v)+"</td>" for v in row)+"</tr>" for row in structure["rows"]) + "</table></section>"
    text += "<details><summary>Original passage</summary><pre>" + html.escape(output["source_recovery"]["original_text"]) + "</pre></details>"
    return "<!doctype html><html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Learning view</title><link rel='stylesheet' href='neutral.css'><main>" + text + "</main></html>"
