"""Isolated SPEC-067 preflight. No provider transport or semantic adjudicator.

The frozen SPEC-066 atomic admission boundary is not silently replaced by a
whole-fixture judge. Failed preflight is evidence, not an invitation to repair
the corpus, change the protocol, or spend the approved call budget anyway.
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
from collections import Counter
from pathlib import Path

from . import spec066_semantic_boundary as frozen
from .control_plane import validate_control_plane
from .models import ValidationError

OUTPUT = "examples/evaluations/spec-067-semantic-judge-live-evaluation-20261007"
SPEC = "specs/SPEC-067-semantic-judge-live-evaluation.md"
CORPUS_SHA = "f965d1762cb4d188303d2464e2a28e0ce229765881a3e912013bb667a8c661d2"
LABELS_SHA = "d47e1f2f6f56f425270d560046457173434523e716ba208b4ca384eedb533db4"
PROTECTED_REF = "747b08f75d6699ecff0c9d8fcd0227d36fac3262"
PROTECTED_SHA = "15ae7c95db3998a1dc3d4ec34f1816432c0d4b06045edaabb1a085e56851cd04"
SETTINGS = {"model": "gpt-6.1-sol", "reasoning": {"effort": "high"},
            "store": False, "sdk_max_retries": 0, "semantic_retries": 0,
            "repair_calls": 0, "follow_up_calls": 0, "maximum_calls": 60}


def protected(root: Path) -> list[dict]:
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", PROTECTED_REF], cwd=root,
        text=True).splitlines()
    rows = [{"path": p, "sha256": frozen.sha(root/p)} for p in paths if
            p.startswith(("baselines/", "examples/evaluations/", "examples/sources/",
                          "src/knowledge_compiler/", "tests/fixtures/"))]
    if len(rows) != 2120 or frozen.stable(rows) != PROTECTED_SHA:
        raise ValidationError("SPEC-067 protected state changed")
    return rows


def verify_frozen(root: Path) -> tuple[list, list, list]:
    fixtures = frozen.load(root/frozen.OUTPUT/"fixture-corpus.json")
    labels = frozen.load(root/frozen.OUTPUT/"fixture-labels.json")
    regenerated = frozen.fixture_corpus(root)
    if (frozen.stable(fixtures) != CORPUS_SHA or frozen.stable(labels) != LABELS_SHA
            or (fixtures, labels) != regenerated[:2] or len(fixtures) != 92):
        raise ValidationError("SPEC-067 frozen corpus/labels identity mismatch")
    audits = []
    for fixture, label in zip(fixtures, labels, strict=True):
        frozen.check_packet(fixture["packet"])
        if fixture["fixture_id"] != label["fixture_id"]:
            raise ValidationError("fixture/label order mismatch")
        for e in fixture["packet"]["evidence"].values():
            model = frozen.load(root/e["model_path"])
            text = model["document"]["text"]
            if (frozen.sha(root/e["model_path"]) != e["model_sha256"] or
                    frozen.stable(text) != e["source_text_sha256"] or
                    text[e["start_char"]:e["end_char"]] != e["quote"]):
                raise ValidationError("source/evidence binding drift")
        audits.append({"fixture_id": fixture["fixture_id"],
                       "packet_sha256": frozen.stable(fixture["packet"]),
                       "label_sha256": frozen.stable(label),
                       "candidate_text": fixture["packet"]["candidate_text"],
                       "expected_verdict": label["verdict"],
                       "frozen_rationale": label["rationale"],
                       "evidence_ids": list(fixture["packet"]["evidence"]),
                       "evidence_binding": "PASS",
                       "exhaustive_atomic_admission": "NOT_ESTABLISHED"})
    for name, schema in frozen.schemas().items():
        if schema != frozen.load(root/frozen.OUTPUT/f"{name}-schema.json"):
            raise ValidationError("frozen schema drift")
    for mode in ("precision-first", "bounded-batch"):
        if (root/frozen.OUTPUT/f"{mode}-prompt.txt").read_text() != frozen.PROMPTS[mode]:
            raise ValidationError("frozen prompt drift")
    return fixtures, labels, audits


def select(fixtures: list[dict]) -> list[dict]:
    """Round-robin categories, unused domains first within each category.

    Only category/domain coverage participates; expected verdicts never do.
    This is a frozen diagnostic proposal, not an executable atomic contract.
    """
    selected, used, domains = [], set(), {c: set() for c in frozen.CATEGORIES}
    while len(selected) < 48:
        progress = False
        for category in frozen.CATEGORIES:
            options = [f for f in fixtures if f["category"] == category and
                       f["fixture_id"] not in used]
            if not options:
                continue
            choice = min(options, key=lambda f: (
                f["domain"] in domains[category], f["fixture_id"]))
            selected.append(choice)
            used.add(choice["fixture_id"])
            domains[category].add(choice["domain"])
            progress = True
            if len(selected) == 48:
                break
        if not progress:
            raise ValidationError("insufficient fixtures for 48-case design")
    return sorted(selected, key=lambda f: f["fixture_id"])


def batches(selection: list[dict]) -> list[list[dict]]:
    remaining, groups = selection.copy(), []
    while remaining:
        group = []
        for _ in range(4):
            choice = min(remaining, key=lambda f: (
                f["domain"] in {g["domain"] for g in group},
                f["category"] in {g["category"] for g in group}, f["fixture_id"]))
            group.append(choice)
            remaining.remove(choice)
        groups.append(group)
    return groups


def data_packet(root: Path, fixture: dict, reverse: bool = False) -> dict:
    """Unchanged candidates/carriers and source data; no gold/witness answers.

    Never rename multiple atoms into one, or certify UNRESOLVED as validated.
    """
    packet = fixture["packet"]
    evidence = [{"evidence_id": eid, **e} for eid, e in packet["evidence"].items()]
    model = frozen.load(root/evidence[0]["model_path"])
    data = {"complete_candidate_text": packet["candidate_text"],
            "encoding": packet["encoding"],
            "commitments": copy.deepcopy(packet["commitments"]),
            "evidence": evidence[::-1] if reverse else evidence,
            "source_context": {"document_id": model["document"]["id"],
                               "text": model["document"]["text"],
                               "text_sha256": frozen.stable(model["document"]["text"])},
            "decomposition_admission": "NOT_VALIDATED"}
    forbidden = {"expected_label", "expected_verdict", "rationale", "category",
                 "label_origin", "admissible", "frozen_witnesses", "owner_comments"}

    def check(value):
        if isinstance(value, dict):
            if forbidden & value.keys():
                raise ValidationError("answer metadata leaked into proposed judge data")
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)

    check(data)
    return data


def atomic_boundary(fixtures: list[dict]) -> dict:
    unresolved = [f["fixture_id"] for f in fixtures if any(
        a["decomposition_status"] == "UNRESOLVED" for a in f["packet"]["commitments"])]
    multi = [f["fixture_id"] for f in fixtures if len(f["packet"]["commitments"]) != 1]
    return {"unresolved_carrier_fixture_ids": unresolved,
            "multi_carrier_fixture_ids": multi,
            "declared_carriers": sum(len(f["packet"]["commitments"]) for f in fixtures),
            "independently_validated_atomic_decompositions": 0,
            "passes_frozen_atomic_contract": False,
            "reason": "The frozen protocol-C gate requires independently validated exhaustive atomization; no such receipt exists. UNRESOLVED is not validated, and an explicit AND fixture is not one atomic judgment."}


def authorize_transmission(audit: dict) -> None:
    # Deliberately no provider import, client construction, or network adapter.
    if not audit["atomic_boundary"]["passes_frozen_atomic_contract"]:
        raise ValidationError("FIXTURE_OR_PREFLIGHT_INVALID: frozen atomic admission unresolved")
    raise ValidationError("no executable provider transport in this blocked preflight")


def generate(root: Path, output: Path, require_active: bool = True) -> dict:
    if require_active:
        state = validate_control_plane(root)
        if state.packet != SPEC or state.control.authority != "LIVE_CALLS_EXPLICITLY_BOUNDED":
            raise ValidationError("SPEC-067 active bounded authority missing")
    protected_rows = protected(root)
    fixtures, labels, rows = verify_frozen(root)
    selection = select(fixtures)
    groups = batches(selection)
    order = []
    for f in selection:
        if f["domain"] not in {g["domain"] for g in order} and len(f["packet"]["evidence"]) > 1:
            order.append(f)
    if len(order) != 8:
        raise ValidationError("eight-domain order subset unavailable")
    order_ids = {f["fixture_id"] for f in order}
    output.mkdir(parents=True, exist_ok=True)

    def write(name, value):
        frozen.write_json(output/name, value)

    identities = {"corpus_sha256": CORPUS_SHA, "labels_sha256": LABELS_SHA,
                  "prompts": {k: {"path": f"{frozen.OUTPUT}/{k}-prompt.txt",
                                   "file_sha256": frozen.sha(root/frozen.OUTPUT/f"{k}-prompt.txt"),
                                   "canonical_sha256": frozen.stable(frozen.PROMPTS[k])}
                              for k in ("precision-first", "bounded-batch")},
                  "schemas": {k: frozen.stable(v) for k, v in frozen.schemas().items()}}
    proposed = []
    for protocol, sets in (("J1", [[f] for f in selection]), ("J2", groups)):
        for group in sets:
            mode = "precision-first" if protocol == "J1" else "bounded-batch"
            data = [data_packet(root, f, protocol == "J2" and f["fixture_id"] in order_ids) for f in group]
            row = {"ordinal": len(proposed)+1, "protocol": protocol,
                   "fixture_ids": [f["fixture_id"] for f in group],
                   "state": "BLOCKED_PREFLIGHT_NOT_TRANSMITTABLE",
                   "input": data, "input_sha256": frozen.stable(data),
                   "prompt_sha256": identities["prompts"][mode]["canonical_sha256"],
                   "schema_sha256": identities["schemas"]["semantic-verdict" if protocol == "J1" else "batch-verdict"],
                   "settings": SETTINGS}
            proposed.append(row)
    selection_manifest = {"state": "FROZEN_NONEXECUTABLE_PROPOSAL", "algorithm": select.__doc__,
                          "fixtures": [{"fixture_id": f["fixture_id"], "category": f["category"],
                                        "domain": f["domain"], "packet_sha256": frozen.stable(f["packet"])} for f in selection]}
    audit = {"identity_and_source_bindings": "PASS", "label_metadata_isolation": "PASS",
             "prompt_schema_identity": "PASS", "atomic_boundary": atomic_boundary(fixtures),
             "selected_atomic_boundary": atomic_boundary(selection),
             "fixture_audits": rows,
             "label_review": "Frozen full source texts in all eight domains were inspected independently of the restricted A/B validators. This is not blinded expert adjudication. Evidence binding and rationale consistency do not certify exhaustive atomization; final decomposition review fails closed.",
             "content_contamination": "No instruction-like source content identified during source review. Evidence remains structurally delimited data; this is mitigation, not a guarantee of model isolation.",
             "provider_contract": "NOT_REACHED_EARLIER_PREFLIGHT_FAILURE",
             "result": "FIXTURE_OR_PREFLIGHT_INVALID"}
    report = {"packet": "SPEC-067", "mechanical_branch": "FIXTURE_OR_PREFLIGHT_INVALID",
              "recommended_next_step": "FIXTURE_REDESIGN_REQUIRED", "owner_verdict": "PENDING",
              "promotion": "NOT_AUTHORIZED", "live_calls": 0, "fixture_transmissions": 0,
              "maximum_authorized_calls": 60, "selection_count": 48, "proposed_J1_calls": 48,
              "proposed_J2_calls": 12, "provider_contract": audit["provider_contract"],
              "J1_metrics": None, "J2_metrics": None, "observed_usage": None,
              "observed_cost": None, "observed_latency": None,
              "reason": audit["atomic_boundary"]["reason"],
              "no_silent_repair": "No whole-fixture replacement, atom collapse, extra atomic calls, decomposition certification, prompt/schema adjustment, or receipt-gate bypass.",
              "completion": "Offline fail-closed preflight outcome only; live semantic judge not evaluated.",
              "correlated_error": "UNRESOLVED: no generator or judge ran; same-family correlated errors cannot be estimated.",
              "order_sensitivity": "NOT_MEASURED; proposed reversal is confounded with batching."}
    write("report.json", report)
    write("pre-live-audit.json", audit)
    write("selection-manifest.json", selection_manifest)
    write("J1-call-manifest.json", proposed[:48])
    write("J2-batch-manifest.json", proposed[48:])
    write("order-sensitivity-manifest.json", {"fixture_ids": sorted(order_ids),
          "transform": "Reverse only evidence array order in proposed J2 input; content identical.",
          "confound": "Batching and ordering are not independently isolated."})
    write("prompt-schema-identities.json", identities)
    write("provider-compatibility.json", {"sdk_shape": frozen.sdk_compatibility(),
          "remote_verified": False, "status": audit["provider_contract"],
          "documentation": ["https://developers.openai.com/api/docs/models/gpt-6.1-sol",
                            "https://developers.openai.com/api/docs/guides/structured-outputs",
                            "https://developers.openai.com/api/docs/guides/conversation-state"],
          "note": "Documentation/local SDK shape were inspected. No catalog or model request made because atomic preflight failed; documentation is not account compatibility proof."})
    write("provider-call-ledger.json", {"actual_provider_calls": 0, "fixture_transmissions": 0,
          "retries": 0, "repair_calls": 0, "settings": SETTINGS,
          "rows": [{"ordinal": r["ordinal"], "protocol": r["protocol"],
                    "fixture_ids": r["fixture_ids"], "state": "NOT_ATTEMPTED_PREFLIGHT_INVALID",
                    "raw_response": None, "request_id": None, "usage": None,
                    "latency_seconds": None} for r in proposed]})
    (output/"raw-responses").mkdir(exist_ok=True)
    (output/"raw-responses"/"NO_CALLS.txt").write_text("No provider requests or responses. Preflight failed before transmission.\n")
    scores = [{"fixture_id": f["fixture_id"], "J1": "NOT_ATTEMPTED", "J2": "NOT_ATTEMPTED"} for f in selection]
    write("per-fixture-scoring.json", scores)
    write("category-metrics.json", {c: {"selected": sum(f["category"] == c for f in selection),
          "attempted": 0, "false_admissions": None, "true_admissions": None,
          "uncertainty_rate": None, "confusion": None} for c in frozen.CATEGORIES})
    for name in ("batching-degradation-audit.json", "order-sensitivity-audit.json",
                 "evidence-preservation-audit.json", "usage-latency-summary.json"):
        write(name, {"status": "NOT_MEASURED_NO_CALLS", "measurements": None,
                     "note": "Not-attempted slots are not rejections or successful conservative judgments."})
    write("correlated-error-limitations.json", {"risk": report["correlated_error"], "empirically_measured": False})
    write("protected-state.json", {"reference": PROTECTED_REF, "aggregate_sha256": PROTECTED_SHA, "files": protected_rows})
    write("freeze-identities.json", {"selection_sha256": frozen.stable(selection_manifest),
          "manifests_sha256": frozen.stable(proposed), "prompt_schema_sha256": frozen.stable(identities)})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay", action="store_true", help="Offline artifact replay after packet closure; never executes calls.")
    args = parser.parse_args()
    report = generate(args.root, args.output or args.root/OUTPUT, require_active=not args.replay)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
