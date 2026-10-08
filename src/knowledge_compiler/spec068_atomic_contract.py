"""SPEC-068 isolated native-grammar audit; no NLP atomizer or live transport.

The new contract admits only components already declared in the frozen explicit
grammar. It does not assert that arbitrary English carriers are irreducible
atoms, and does not modify the earlier SPEC-066/067 trust boundaries.
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from . import spec066_semantic_boundary as old
from . import spec067_judge_preflight as prior
from .control_plane import validate_control_plane
from .models import ValidationError

OUTPUT = "examples/evaluations/spec-068-atomic-judgment-contract-repair-20261008"
SPEC = "specs/SPEC-068-atomic-judgment-contract-repair.md"
PROTECTED_REF = "2fdadb5414ee61994404ba7e4c67f109033e3e15"
PROTECTED_SHA = "13467e25fd562d39b9c43e6df652e17ba079e1e1bf9a3d66c929ac492ccebf32"
STATUSES = ["EXPLICIT_ATOMIC", "EXPLICIT_COMPOSITE_DECOMPOSABLE",
            "OPAQUE_ATOMIZATION_UNRESOLVED", "MALFORMED"]
VERDICTS = ["ENTAILED", "CONTRADICTED", "UNCERTAIN", "UNRESOLVED"]
REQUIRED_POSITIVES = ["faithful paraphrase", "faithful synthesis of multiple commitments",
                      "valid explanatory abstraction", "valid relation projection onto compressed endpoints"]


def protected(root: Path) -> list[dict]:
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PROTECTED_REF],
                                    cwd=root, text=True).splitlines()
    rows = [{"path": p, "sha256": old.sha(root/p)} for p in paths if p.startswith(
        ("baselines/", "examples/evaluations/", "examples/sources/", "src/knowledge_compiler/", "tests/fixtures/"))]
    if len(rows) != 2143 or old.stable(rows) != PROTECTED_SHA:
        raise ValidationError("SPEC-068 frozen protected-state drift")
    return rows


def atom_schema() -> dict:
    string = {"type": "string"}
    return old.obj({
        "atom_id": string, "fixture_id": string, "component_ordinal": {"type": "integer", "minimum": 1},
        "candidate_text": string, "composition_role": old.enum(["ALL_REQUIRED", "IDENTITY_REQUIRED"]),
        "evidence_packet_sha256": string, "supporting_evidence_ids": old.arr(string),
        "expected_semantic_verdict": old.enum(VERDICTS),
        "expected_preservation_flags": old.obj({f: old.enum(["PASS", "FAIL", "UNRESOLVED", "NOT_APPLICABLE"]) for f in old.FLAGS}),
        "required_preservation_flags": old.arr(old.enum(old.FLAGS)),
        "atomization_status": old.enum(["EXPLICIT_ATOMIC"]),
        "atomization_proof_type": old.enum(["DECLARED_NATIVE_GRAMMAR_COMPONENT_IDENTITY"]),
        "provenance": old.obj({"fixture_packet_sha256": string, "component_sha256": string,
                               "frozen_source_commitment_id": string, "proof_scope": string}),
    })


def classify(packet: dict) -> tuple[str, str]:
    try:
        old.check_packet(packet)
    except (ValidationError, KeyError, TypeError, ValueError) as exc:
        return "MALFORMED", str(exc)
    if packet["encoding"] != "EXPLICIT_AND":
        return "OPAQUE_ATOMIZATION_UNRESOLVED", "Opaque carrier identity is not proof of exhaustive atomization; no split or relabeling permitted."
    status = "EXPLICIT_ATOMIC" if len(packet["commitments"]) == 1 else "EXPLICIT_COMPOSITE_DECOMPOSABLE"
    return status, "Exact native AND rendering, declared components and membership; no English punctuation parsing or semantic rewrite."


def derive_truth(fixture: dict, component: dict, corpus: list[dict], labels: list[dict]) -> dict:
    """Logical AND elimination / identical proposition in identical authority.

    A rejected parent says nothing about any particular conjunct. Opaque gold
    can license the truth of an already-explicit component with identical text
    and evidence, but never licenses atomization of that opaque parent.
    """
    packet = fixture["packet"]
    gold = {r["fixture_id"]: r for r in labels}
    parent = gold[fixture["fixture_id"]]
    sources, candidates = [], []
    if (packet["encoding"] == "EXPLICIT_AND" and parent["verdict"] == "ENTAILED"
            and old.exact(component["candidate_text"], component["supporting_evidence_ids"], packet["frozen_witnesses"])):
        sources.append({"rule": "EXPLICIT_POSITIVE_AND_ELIMINATION_WITH_EXACT_GROUNDED_WITNESS",
                        "fixture_id": fixture["fixture_id"], "label_sha256": old.stable(parent)})
        candidates.append(("ENTAILED", {f: "PASS" for f in old.FLAGS}))
    for other in corpus:
        p = other["packet"]
        if (other["fixture_id"] != fixture["fixture_id"]
                and p["candidate_text"] == component["candidate_text"]
                and old.authority(p) == old.authority(packet)
                and set(component["supporting_evidence_ids"]) <= set(p["evidence"])):
            label = gold[other["fixture_id"]]
            sources.append({"rule": "EXACT_FROZEN_PROPOSITION_AND_EVIDENCE_AUTHORITY_MATCH",
                            "fixture_id": other["fixture_id"], "label_sha256": old.stable(label)})
            candidates.append((label["verdict"], label["preservation_flags"]))
    truths = {v for v, _ in candidates}
    if len(truths) != 1:
        return {"verdict": "UNRESOLVED", "flags": {f: "UNRESOLVED" for f in old.FLAGS},
                "sources": sources, "reason": "No unique evidence-bound component truth; parent rejection was not distributed to conjuncts."}
    verdict = next(iter(truths))
    flags = {f: next(iter(values)) if len(values := {flags[f] for _, flags in candidates}) == 1
             else "UNRESOLVED" for f in old.FLAGS}
    return {"verdict": verdict, "flags": flags, "sources": sources,
            "reason": "Exact truth transfer only, no new semantic entailment judgment."}


def audit(corpus: list[dict], labels: list[dict]) -> tuple[list, list, list, list]:
    rows, mappings, atoms, truth_rows = [], [], [], []
    gold = {r["fixture_id"]: r for r in labels}
    for fixture in corpus:
        packet, fid = fixture["packet"], fixture["fixture_id"]
        status, reason = classify(packet)
        ids, local = [], []
        if status in STATUSES[:2]:
            for ordinal, component in enumerate(packet["commitments"], 1):
                truth = derive_truth(fixture, component, corpus, labels)
                atom = {"atom_id": component["commitment_id"], "fixture_id": fid,
                        "component_ordinal": ordinal, "candidate_text": component["candidate_text"],
                        "composition_role": "ALL_REQUIRED" if len(packet["commitments"]) > 1 else "IDENTITY_REQUIRED",
                        "evidence_packet_sha256": old.stable(old.authority(packet)),
                        "supporting_evidence_ids": component["supporting_evidence_ids"].copy(),
                        "expected_semantic_verdict": truth["verdict"], "expected_preservation_flags": truth["flags"],
                        "required_preservation_flags": old.FLAGS.copy(), "atomization_status": "EXPLICIT_ATOMIC",
                        "atomization_proof_type": "DECLARED_NATIVE_GRAMMAR_COMPONENT_IDENTITY",
                        "provenance": {"fixture_packet_sha256": old.stable(packet),
                                       "component_sha256": old.stable(component),
                                       "frozen_source_commitment_id": component["commitment_id"],
                                       "proof_scope": "Native declared grammar only; no claim of general natural-language semantic irreducibility."}}
                old.validate_json(atom, atom_schema())
                ids.append(atom["atom_id"])
                local.append(atom)
                truth_rows.append({"atom_id": atom["atom_id"], "fixture_id": fid, **truth})
            atoms.extend(local)
        eligible = bool(local) and all(a["expected_semantic_verdict"] != "UNRESOLVED" for a in local)
        mapping = {"fixture_id": fid, "fixture_packet_sha256": old.stable(packet), "atomization_status": status,
                   "operator": "AND_ALL_REQUIRED" if status in STATUSES[:2] else "UNRESOLVED",
                   "atom_ids": ids, "declared_carrier_ids": [a["commitment_id"] for a in packet["commitments"]],
                   "fully_known_atom_truth": eligible, "future_scored_execution_eligible": eligible}
        mappings.append(mapping)
        rows.append({"fixture_id": fid, "category": fixture["category"], "domain": fixture["domain"],
                     "declared_carriers": len(packet["commitments"]), "atomization_status": status,
                     "admissible_atoms": len(local), "atom_truth_status": "FULLY_KNOWN" if eligible else "UNRESOLVED",
                     "expected_fixture_verdict": gold[fid]["verdict"], "eligible": eligible, "reason": reason})
    if len({a["atom_id"] for a in atoms}) != len(atoms):
        raise ValidationError("atom IDs are not globally unique")
    return rows, mappings, atoms, truth_rows


def verify_mapping(fixture: dict, mapping: dict, atoms: list[dict]) -> None:
    status, _ = classify(fixture["packet"])
    if status not in STATUSES[:2]:
        raise ValidationError("opaque/malformed fixture has no admissible atomic mapping")
    components = fixture["packet"]["commitments"]
    wanted = [c["commitment_id"] for c in components]
    if (mapping["fixture_id"] != fixture["fixture_id"] or mapping["atom_ids"] != wanted
            or mapping["declared_carrier_ids"] != wanted or mapping["atomization_status"] != status
            or mapping["fixture_packet_sha256"] != old.stable(fixture["packet"])
            or mapping["operator"] != "AND_ALL_REQUIRED" or len(atoms) != len(components)):
        raise ValidationError("fixture coverage/membership changed")
    for i, (atom, component) in enumerate(zip(atoms, components, strict=True), 1):
        old.validate_json(atom, atom_schema())
        if (atom["fixture_id"] != fixture["fixture_id"] or atom["atom_id"] != component["commitment_id"]
                or atom["component_ordinal"] != i or atom["candidate_text"] != component["candidate_text"]
                or atom["supporting_evidence_ids"] != component["supporting_evidence_ids"]
                or atom["required_preservation_flags"] != old.FLAGS
                or atom["composition_role"] != ("ALL_REQUIRED" if len(components) > 1 else "IDENTITY_REQUIRED")
                or atom["evidence_packet_sha256"] != old.stable(old.authority(fixture["packet"]))
                or atom["provenance"]["component_sha256"] != old.stable(component)
                or atom["provenance"]["frozen_source_commitment_id"] != component["commitment_id"]
                or atom["provenance"]["fixture_packet_sha256"] != old.stable(fixture["packet"])):
            raise ValidationError("atom lost/merged/rewritten/forged component or evidence")


def judge_data(root: Path, fixture: dict, atom: dict) -> dict:
    """Future input contains just one original component, never expected truth."""
    component = fixture["packet"]["commitments"][atom["component_ordinal"]-1]
    if old.stable(component) != atom["provenance"]["component_sha256"]:
        raise ValidationError("atom origin mismatch")
    evidence = {eid: fixture["packet"]["evidence"][eid] for eid in component["supporting_evidence_ids"]}
    model = old.load(root/next(iter(evidence.values()))["model_path"])
    data = {"commitments": [copy.deepcopy(component)], "evidence": evidence,
            "source_context": {"document_id": model["document"]["id"], "text": model["document"]["text"],
                               "text_sha256": old.stable(model["document"]["text"])},
            "complete_candidate_text": component["candidate_text"],
            "decomposition_admission": "DECLARED_NATIVE_GRAMMAR_COMPONENT_IDENTITY"}
    # Explicitly supply the binding for a later judge to echo, not to compute.
    data["input_sha256"] = old.stable(data)
    return data


def aggregate(contract: dict, responses: list[dict]) -> dict:
    """Receipt aggregation only, NOT semantic judging. No truth-label input."""
    def rejected(reason, verdict="UNCERTAIN"):
        return {"fixture_id": contract["fixture_id"], "verdict": verdict,
                "admission": "FAIL_CLOSED", "reason": reason}
    if contract["operator"] != "AND_ALL_REQUIRED" or not contract["atoms"]:
        return rejected("UNRESOLVED_AGGREGATION")
    expected = {a["atom_id"]: a for a in contract["atoms"]}
    try:
        if (len(expected) != len(contract["atoms"]) or len(responses) != len(expected)
                or {r["commitment_id"] for r in responses} != set(expected)
                or len({r["commitment_id"] for r in responses}) != len(responses)):
            return rejected("MISSING_DUPLICATE_OR_UNREQUESTED_ATOM")
        for row in responses:
            old.validate_json(row, old.schemas()["semantic-verdict"])
            atom = expected[row["commitment_id"]]
            if (row["input_sha256"] != atom["input_sha256"] or len(row["notes"]) > 500
                    or atom["required_preservation_flags"] != old.FLAGS):
                return rejected("BINDING_OR_REQUIRED_FLAGS_FAILURE")
            for field in ("supporting_evidence_ids", "contradicting_evidence_ids"):
                refs = row[field]
                if len(refs) != len(set(refs)) or not set(refs) <= set(atom["evidence_ids"]):
                    return rejected("FABRICATED_OR_CROSS_ATOM_EVIDENCE")
        if any(r["verdict"] == "CONTRADICTED" for r in responses):
            return rejected("CONTRADICTED_REQUIRED_ATOM", "CONTRADICTED")
        if any(r["verdict"] != "ENTAILED" for r in responses):
            return rejected("UNCERTAIN_REQUIRED_ATOM")
        if any(not r["supporting_evidence_ids"] or r["contradicting_evidence_ids"]
               or any(r[f] != "PASS" for f in old.FLAGS) for r in responses):
            return rejected("PRESERVATION_OR_SUPPORT_FAILURE")
    except (ValidationError, KeyError, TypeError):
        return rejected("MALFORMED_ATOM_RESULT")
    return {"fixture_id": contract["fixture_id"], "verdict": "ENTAILED",
            "admission": "ADMIT", "reason": "ALL_REQUIRED_ATOMS_ENTAILED_AND_FLAGS_PASS"}


def batch_atoms(atoms: list[dict], size: int = 4) -> list[list[dict]]:
    """Greedy atom-ID order; prefer no sibling in each fixed four-atom batch."""
    if size != 4:
        raise ValidationError("future batch size frozen at four atoms")
    remaining, groups = atoms.copy(), []
    while remaining:
        group = []
        for _ in range(min(size, len(remaining))):
            chosen = min(remaining, key=lambda a: (a["fixture_id"] in {b["fixture_id"] for b in group},
                                                  a["atom_id"]))
            group.append(chosen)
            remaining.remove(chosen)
        groups.append(group)
    return groups


def coverage(corpus: list, rows: list, atoms: list, truth_rows: list) -> dict:
    eligible = {r["fixture_id"] for r in rows if r["eligible"]}
    result = {}
    for dimension, values in (("category", old.CATEGORIES), ("domain", sorted({f["domain"] for f in corpus}))):
        groups = {}
        for value in values:
            fs = [f for f in corpus if f[dimension] == value]
            keep = [f for f in fs if f["fixture_id"] in eligible]
            groups[value] = {"original_fixtures": len(fs), "eligible_fixtures": len(keep),
                             "excluded_fixtures": len(fs)-len(keep),
                             "eligible_atom_count": sum(a["fixture_id"] in {f["fixture_id"] for f in keep} for a in atoms)}
        result[dimension] = groups
        result[f"lost_{dimension}_values"] = [v for v, n in groups.items() if not n["eligible_fixtures"]]
    original = {f["fixture_id"]: f for f in corpus}
    result["component_truth_source_categories"] = dict(Counter(
        original[t["sources"][-1]["fixture_id"]]["category"] for t in truth_rows if t["sources"]))
    result["limit"] = "Truth-source categories are provenance only; do not relabel surviving parent fixtures or call them novel abstractions/paraphrases."
    return result


def generate(root: Path, output: Path, require_active=True) -> dict:
    if require_active:
        state = validate_control_plane(root)
        if state.packet != SPEC or state.control.authority != "OFFLINE_ONLY":
            raise ValidationError("SPEC-068 offline authority missing")
    protected_rows = protected(root)
    corpus, labels, _ = prior.verify_frozen(root)
    rows, mappings, atoms, truths = audit(corpus, labels)
    schema = atom_schema()
    old.validate_schema(schema)
    by_fixture = {f["fixture_id"]: f for f in corpus}
    by_atom = {a["atom_id"]: a for a in atoms}
    for m in mappings:
        if m["atom_ids"]:
            verify_mapping(by_fixture[m["fixture_id"]], m, [by_atom[key] for key in m["atom_ids"]])
    eligible = [m for m in mappings if m["future_scored_execution_eligible"]]
    # Retain every safe case. No reduced selection can recover a lost category.
    selected_atoms = [by_atom[key] for m in eligible for key in m["atom_ids"]]
    inputs = {a["atom_id"]: judge_data(root, by_fixture[a["fixture_id"]], a) for a in selected_atoms}
    contracts = [{"fixture_id": m["fixture_id"], "operator": m["operator"],
                  "fixture_packet_sha256": m["fixture_packet_sha256"],
                  "atoms": [{"atom_id": key, "input_sha256": inputs[key]["input_sha256"],
                             "evidence_ids": by_atom[key]["supporting_evidence_ids"],
                             "required_preservation_flags": old.FLAGS.copy()} for key in m["atom_ids"]]} for m in eligible]
    settings = {k: v for k, v in prior.SETTINGS.items() if k != "maximum_calls"}
    groups = batch_atoms(selected_atoms)
    manifests = {}
    for protocol, batches in (("J1", [[a] for a in selected_atoms]), ("J2", groups)):
        mode = "precision-first" if protocol == "J1" else "bounded-batch"
        manifests[protocol] = {"status": "PROPOSED_NOT_AUTHORIZED_NOT_REPRESENTATIVE",
            "settings": settings, "prompt_path": f"{old.OUTPUT}/{mode}-prompt.txt",
            "prompt_file_sha256": old.sha(root/old.OUTPUT/f"{mode}-prompt.txt"),
            "schema_sha256": old.stable(old.schemas()["batch-verdict"]),
            "schema_path": f"{old.OUTPUT}/batch-verdict-schema.json",
            "calls": [{"ordinal": i, "atom_ids": [a["atom_id"] for a in group],
                       "fixture_ids": [a["fixture_id"] for a in group],
                       "input": [inputs[a["atom_id"]] for a in group],
                       "per_atom_input_sha256": [inputs[a["atom_id"]]["input_sha256"] for a in group],
                       "state": "NOT_AUTHORIZED_NOT_ATTEMPTED"} for i, group in enumerate(batches, 1)]}
    controls = []
    truth_by_id = {t["atom_id"]: t for t in truths}
    for c in contracts:
        expected = [by_atom[a["atom_id"]]["expected_semantic_verdict"] for a in c["atoms"]]
        receipts = [{"commitment_id": a["atom_id"], "input_sha256": a["input_sha256"], "verdict": by_atom[a["atom_id"]]["expected_semantic_verdict"],
                     "supporting_evidence_ids": a["evidence_ids"] if by_atom[a["atom_id"]]["expected_semantic_verdict"] == "ENTAILED" else [],
                     "contradicting_evidence_ids": [], **by_atom[a["atom_id"]]["expected_preservation_flags"],
                     "reason_code": "EXACT_FROZEN_WITNESS" if by_atom[a["atom_id"]]["expected_semantic_verdict"] == "ENTAILED" else "INSUFFICIENT_EVIDENCE",
                     "notes": "OFFLINE SYNTHETIC CONTROL, NOT A JUDGE OUTPUT."} for a in c["atoms"]]
        result = aggregate(c, receipts)
        if result["verdict"] != next(l["verdict"] for l in labels if l["fixture_id"] == c["fixture_id"]):
            raise ValidationError("derived component truth failed frozen parent reconciliation")
        if "ENTAILED" in expected and any(v != "ENTAILED" for v in expected):
            controls.append({"fixture_id": c["fixture_id"], "atom_truth": expected,
                             "truth_proofs": [truth_by_id[a["atom_id"]] for a in c["atoms"]],
                             "synthetic_receipts": receipts, "aggregation": result,
                             "entailed_atom_alone": aggregate(c, receipts[:1]), "synthetic_not_live": True})
    cov = coverage(corpus, rows, atoms, truths)
    missing_positives = [c for c in REQUIRED_POSITIVES if not cov["category"][c]["eligible_fixtures"]]
    representative = bool(eligible) and not missing_positives
    if representative:
        branch, next_step = "ATOMIC_EXECUTION_CONTRACT_READY", "REAUTHORIZE_SEMANTIC_JUDGE_LIVE_EVALUATION"
    elif eligible:
        branch, next_step = "ATOMIC_SUBSET_TOO_NARROW", "BOUNDED_ATOMIZATION_EXPERIMENT"
    elif atoms:
        branch, next_step = "FIXTURE_TRUTH_INSUFFICIENT_FOR_ATOM_LABELS", "FIXTURE_REDESIGN_REQUIRED"
    else:
        branch, next_step = "ATOMIZATION_REQUIRES_SEMANTIC_JUDGMENT", "BOUNDED_ATOMIZATION_EXPERIMENT"
    report = {"packet": "SPEC-068", "entering_owner_verdict": "LIVE_JUDGE_NOT_TESTED_ATOMIC_EXECUTION_CONTRACT_REQUIRES_REPAIR",
              "mechanical_branch": branch, "recommended_next_step": next_step,
              "owner_verdict": "PENDING", "promotion": "NOT_AUTHORIZED", "live_calls": 0,
              "provider_calls": 0, "evaluation_network_calls": 0,
              "network_scope": "No evaluation/model/provider/source-retrieval network activity. Repository-required Git fetch/push are coordination only.",
              "audited_fixtures": len(rows), "atomization_distribution": {s: sum(r["atomization_status"] == s for r in rows) for s in STATUSES},
              "declared_carriers": sum(r["declared_carriers"] for r in rows), "admissible_atoms": len(atoms),
              "fully_known_atom_truth_fixtures": len(eligible), "unresolved_atom_truth_fixtures": len(rows)-len(eligible),
              "atom_truth_distribution": dict(Counter(a["expected_semantic_verdict"] for a in atoms)),
              "selected_fixtures": len(eligible), "selected_atoms": len(selected_atoms),
              "remaining_categories": len(old.CATEGORIES)-len(cov["lost_category_values"]),
              "remaining_domains": len(cov["domain"])-len(cov["lost_domain_values"]),
              "lost_categories": cov["lost_category_values"], "lost_domains": cov["lost_domain_values"],
              "missing_faithful_positive_classes": missing_positives, "representative_future_subset_exists": representative,
              "mixed_validity_composite_controls": len(controls), "future_J1_calls": len(selected_atoms),
              "future_J2_batch_size": 4, "future_J2_calls": len(groups),
              "future_maximum_calls": len(selected_atoms)+len(groups), "future_execution_authorized": False,
              "scope_limit": "Native explicit components are judge units under SPEC-068; opaque English remains excluded, including the opaque truth-reference fixtures. No NLP semantic irreducibility certified.",
              "why_not_representative": "Only exact-assertion conjunction controls and unsupported-abstraction composites survive; novel faithful transformations and subtle drift categories remain excluded.",
              "representativeness_gate": "Missing the faithful transformation classes needed to assess usefulness is a categorical design gap, not a numerical accuracy threshold or a human cognitive verdict."}
    output.mkdir(parents=True, exist_ok=True)
    def write(name, value):
        old.write_json(output/name, value)
    write("report.json", report)
    write("frozen-identities.json", {"corpus_sha256": prior.CORPUS_SHA, "labels_sha256": prior.LABELS_SHA,
          "spec067_report_file_sha256": old.sha(root/prior.OUTPUT/"report.json"),
          "spec067_manifest_file_sha256": old.sha(root/prior.OUTPUT/"freeze-identities.json"),
          "atom_schema_sha256": old.stable(schema), "atoms_sha256": old.stable(atoms), "mapping_sha256": old.stable(mappings),
          "implementation_file_sha256": old.sha(root/"src/knowledge_compiler/spec068_atomic_contract.py"),
          "future_J1_manifest_sha256": old.stable(manifests["J1"]),
          "future_J2_manifest_sha256": old.stable(manifests["J2"])})
    write("full-fixture-audit.json", rows)
    write("atomic-commitment-schema.json", schema)
    write("atomic-commitments.json", atoms)
    write("atomization-quality-audit.json", [{"atom_id": a["atom_id"],
          "fixture_id": a["fixture_id"], "exact_parent_and_component_origin": True,
          "no_lost_or_invented_conjunct": True, "no_merge_or_semantic_rewrite": True,
          "evidence_binding": "PASS", "label_derivation": "PASS" if a["expected_semantic_verdict"] != "UNRESOLVED" else "UNRESOLVED",
          "proof_scope": a["provenance"]["proof_scope"]} for a in atoms])
    write("fixture-atom-mapping.json", mappings)
    write("atom-truth-derivation-audit.json", truths)
    write("fixture-aggregation-contract.json", {"rule": "All required ENTAILED + every flag PASS + valid IDs/binding/support. Any contradiction rejects; uncertainty or malformed/missing/duplicate/extra result fails closed. No majority or label-based admission.",
          "unsupported_operators": "UNRESOLVED; do not infer OR/negation or English grammar.", "contracts": contracts})
    write("mixed-validity-controls.json", controls)
    write("excluded-opaque-fixtures.json", [r for r in rows if r["atomization_status"] == "OPAQUE_ATOMIZATION_UNRESOLVED"])
    write("category-domain-coverage.json", cov)
    write("proposed-future-subset.json", {"fixture_ids": [m["fixture_id"] for m in eligible],
          "atom_ids": [a["atom_id"] for a in selected_atoms], "representative": representative,
          "selection_policy": "Retain all safe fully labeled fixtures, including every mixed control. A smaller subset cannot restore excluded categories. Diagnostic controls only, not the full semantic-judge experiment.",
          "status": "PROPOSED_NOT_AUTHORIZED"})
    write("future-J1-atom-manifest.json", manifests["J1"])
    write("future-J2-atom-batch-manifest.json", manifests["J2"])
    write("future-call-budget.json", {"selected_fixtures": len(eligible), "selected_atoms": len(selected_atoms),
          "J1": len(selected_atoms), "J2_batch_size": 4, "J2": len(groups),
          "maximum_total": len(selected_atoms)+len(groups), "retries": 0, "repair_calls": 0,
          "actual_calls": 0, "authorized": False, "algorithm": batch_atoms.__doc__ or "Greedy atom-ID order, prefer no sibling in current four-atom batch.",
          "sibling_collisions": sum(len({a["fixture_id"] for a in g}) != len(g) for g in groups),
          "binding_hash_scope": "Canonical per-atom input object without its input_sha256 field; the supplied hash is echoed in verdict.input_sha256.",
          "same_atoms_both_protocols": True, "money_tokens_latency": "UNMEASURED_NO_CALLS"})
    write("protected-state.json", {"reference": PROTECTED_REF, "aggregate_sha256": PROTECTED_SHA, "files": protected_rows})
    (output/"zero-call-statement.txt").write_text("Zero model/provider/evaluation-network calls; zero semantic judging, synthesis, retrieval, or model/heuristic atomization. Future manifests are not authorized. Git coordination is separate.\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay", action="store_true", help="Offline replay after closure; never grants authority.")
    args = parser.parse_args()
    output = args.output or args.root/OUTPUT
    report = generate(args.root, output, require_active=not args.replay)
    with tempfile.TemporaryDirectory(prefix="spec068-regenerate-") as directory:
        other = Path(directory)
        second = generate(args.root, other, require_active=not args.replay)
        checks = [{"path": str(p.relative_to(other)), "sha256": old.sha(p),
                   "byte_identical": p.read_bytes() == (output/p.relative_to(other)).read_bytes()}
                  for p in sorted(other.rglob("*")) if p.is_file()]
        if report != second or not all(r["byte_identical"] for r in checks):
            raise ValidationError("SPEC-068 regeneration mismatch")
        old.write_json(output/"deterministic-regeneration.json", {"result": "PASS", "files": checks})
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
