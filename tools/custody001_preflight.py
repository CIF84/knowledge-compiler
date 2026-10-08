"""Offline CUSTODY-001 completeness gate. Not a selector or source retriever.

Read only the frozen canonical repository, never external/provisional selector
material. An unresolved first family stops export/release before later workstreams.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
REF = "7d34d3dd2e68644307bcfb3327b3c89e5b8e4c1f"
BASE = Path("audits/independent-architecture-audit-001")
EXPORT = BASE / "benchmark-readiness-v1/contamination-reference-export-v1"
CONTRACT = "specs/CUSTODY-001-source-contamination-export-and-selector-v1.1.md"
THESIS = str(BASE / "01-original-thesis.md")
ORIGINALS = {
    "audits/electromagnetism.pdf": "33cf1338f57bcd95ac23418be99f5a28c9eea0f560ea7e38fa5d780abbb1b10f",
    "audits/electromagnetism.rtf": "6a75e4f5878773769f370c2ad468422fa6beea015ffc601de02de53ba5d4e2a3",
}
FAMILIES = ["recovered electromagnetism", "golden fixtures",
            "quantum/economics/software controls", "SPEC-042/045 nine-source corpus",
            "SPEC-060–068 sources/derivatives"]
QUANTUM = "examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904/parent.knowledge.json"
QUANTUM_SHA = "9e978db999ee67134d347f91fe9f32934c982f4de9b496e4bf664cb00cce23ea"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def stable(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()

def normalize(text):
    return text.replace("\r\n","\n").replace("\r","\n").strip()

def snapshot(root):
    archive = subprocess.check_output(["git","archive",REF],cwd=root)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        return {m.name:tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}

def export_claims(files):
    """Identity-only, explicitly incomplete: never treat response as input text."""
    for path,expected in ORIGINALS.items():
        if digest(files[path]) != expected:
            raise ValueError("recovered artifact identity mismatch: "+path)
    thesis = files[THESIS].decode()
    if "No original input source, source hash, exact prompt" not in thesis:
        raise ValueError("historical missing-input finding does not match frozen evidence")
    if "Later repository\nelectromagnetism fixtures are separate experiments" not in thesis:
        raise ValueError("historical fixture lineage boundary missing")
    return {
        "schema":"custody001.incomplete-source-reference.v1",
        "completeness_status":"FAMILY_COMPLETENESS_UNRESOLVED",
        "usable_for_contamination_clearance":False,
        "normalization":"UTF-8 text: CRLF/CR to LF, then strip; no unavailable passage hash is invented",
        "records":[{
            "family":FAMILIES[0],"source_id":Path(path).name,
            "title":"Recovered electromagnetism reference artifact",
            "canonical_url":None,"publisher":None,"revision_date":None,
            "original_document_sha256":digest(files[path]),
            "original_bytes_repository_identity":{"commit":REF,"path":path,"bytes":len(files[path])},
            "exact_historical_input_passage_text":None,
            "exact_passage_sha256":None,"normalized_passage_sha256":None,
            "lineage":{"original_input_source":"UNIDENTIFIED_IN_REPOSITORY_EVIDENCE",
                       "later_fixture_equivalence":"NOT_ESTABLISHED"},
            "source_evidence_repository_paths":[path,THESIS],
        } for path in sorted(ORIGINALS)],
        "family_coverage":[{"family":family,
            "status":"FAMILY_COMPLETENESS_UNRESOLVED" if i==0 else "NOT_EVALUATED_AFTER_FAIL_CLOSED",
            "enumeration":"Both recovered PDF and RTF identified; original input passage and its source lineage not recovered. Later fixtures cannot be substituted." if i==0 else "Not attested: first-family failure stopped the complete export."}
            for i,family in enumerate(FAMILIES)],
        "zero_sensitive_context_declaration":{
            "source_identity_only":True,"original_artifact_bytes_copied":False,
            "source_text_reconstructed":False,"project_context_exported":False,
            "selector_candidates_imported_or_inspected":False},
    }

def require_complete(manifest):
    if (manifest.get("completeness_status") != "COMPLETE"
            or {r["family"] for r in manifest["family_coverage"]} != set(FAMILIES)
            or any(r["status"] != "COMPLETE" for r in manifest["family_coverage"])):
        raise ValueError("FAMILY_COMPLETENESS_UNRESOLVED: continuation authority and ZIP withheld")

def build(root=ROOT):
    files=snapshot(root)
    current=(root/CONTRACT).read_bytes()
    if current.replace(b"Status: `IMPLEMENTED_AWAITING_REVIEW`",b"Status: `APPROVED_FOR_IMPLEMENTATION`",1)!=files[CONTRACT]:
        raise ValueError("CUSTODY-001 contract drift")
    protected=[]
    for path,raw in sorted(files.items()):
        if path in {"STATUS.md",CONTRACT}:continue
        if (root/path).read_bytes()!=raw:raise ValueError("protected historical drift: "+path)
        protected.append({"path":path,"sha256":digest(raw),"bytes":len(raw)})
    manifest=export_claims(files)
    quantum=json.loads(files[QUANTUM])["document"]["text"]
    if digest(quantum.encode())!=QUANTUM_SHA:raise ValueError("quantum source recovery identity mismatch")
    history=subprocess.check_output(["git","log",REF,"--format=%H","--",*ORIGINALS],cwd=root).decode().splitlines()
    report={
        "packet":CONTRACT,"frozen_input_commit":REF,
        "result":"FAMILY_COMPLETENESS_UNRESOLVED","human_gate":"OWNER_REVIEW",
        "owner_verdict":"PENDING","promotion":"NOT_AUTHORIZED",
        "bench001_owner_verdict":"BENCHMARK_HARNESS_ACCEPTED_PREEXISTING_AUDIT_HASH_FAILURE_NON_BLOCKING",
        "bench001_mechanical_readiness_preserved":"INCONCLUSIVE",
        "activation_verified":{"packet":CONTRACT,"status":"APPROVED_FOR_IMPLEMENTATION","authority":"OFFLINE_ONLY","human_gate":"OWNER_REVIEW","promotion":"NOT_AUTHORIZED"},
        "blocking_family":FAMILIES[0],
        "finding":"The recovered artifacts are a mixed explanatory response, not an identified original input passage. They include learner/representation recommendations that cannot be copied wholesale into this source-only export. Repository history identifies their recovery but does not supply the original source identity, exact input text or its lineage. Later electromagnetism fixtures are explicitly separate experiments. No reconstruction or equivalence inference is made.",
        "evidence":{"historical_record":{"path":THESIS,"sha256":digest(files[THESIS]),"locator":"No original input source, source hash, exact prompt"},
            "recovered_artifact_history_commits":history,
            "inspection":"RTF companion inspected read-only with textutil -convert txt -stdout; no converted/reconstructed artifact written. Original PDF and RTF bytes preserved.",
            "quantum_concern_resolved":{"repository_path":QUANTUM,"json_pointer":"/document/text","text_characters":len(quantum),"exact_passage_sha256":digest(quantum.encode()),"normalized_passage_sha256":digest(normalize(quantum).encode()),"finding":"Later preserved full text matches frozen quantum hash. Older metadata's not-committed statement is not used as a completeness failure."}},
        "partial_manifest":str(EXPORT/"contamination-reference-manifest.json"),
        "complete_source_export":False,"selector_continuation_authority_created":False,
        "continuation_zip_created":False,"continuation_zip_sha256":None,
        "selector_continuation_prompt":None,
        "why_no_continuation_prompt":"CUSTODY-001 explicitly stops if a required family's completeness is unresolved. Do not pass this incomplete identity inventory to the selector as clearance or continuation authority.",
        "other_families":"Not attested after first-family fail-closed stop; no claim of complete enumeration.",
        "required_owner_boundary":"Clarify/restore admissible historical source evidence or authorize a precisely scoped recovered-reference sanitization/completeness contract before continuation. No source retrieval, candidate adjudication or selector extension performed here.",
        "provider_model_calls":0,"benchmark_source_retrievals":0,"benchmark_outputs":0,
        "selector_provisional_package_imported_or_inspected":False,
        "network_activity":"Only authorized Git canonical coordination; no benchmark/provider/retrieval network calls.",
        "validation":json.loads((root/BASE/"custody-001-gates.json").read_bytes()),
        "review_command":"open audits/independent-architecture-audit-001/custody-001-report.json",
    }
    result={str(EXPORT/"contamination-reference-manifest.json"):stable(manifest),
            str(BASE/"custody-001-protected-state.json"):stable({"freeze_commit":REF,"files":protected}),
            str(BASE/"custody-001-report.json"):stable(report)}
    result[str(BASE/"custody-001-output-manifest.json")]=stable({"packet":CONTRACT,"result":report["result"],
        "files":[{"path":p,"sha256":digest(raw),"bytes":len(raw)} for p,raw in sorted(result.items())],
        "release_authorized":False,"zip_created":False})
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--check",action="store_true");args=parser.parse_args()
    outputs=build()
    for path,raw in outputs.items():
        p=ROOT/path
        if args.check:
            if not p.is_file() or p.read_bytes()!=raw:raise ValueError("non-deterministic artifact: "+path)
        else:
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    print(json.dumps({"mechanical_checks":"PASS","result":"FAMILY_COMPLETENESS_UNRESOLVED",
        "source_only_identity_manifest_complete":False,"selector_authority":False,"zip_created":False,
        "provider_calls":0,"source_retrievals":0,"owner_review":"REQUIRED"}))

if __name__=="__main__":main()
