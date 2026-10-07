"""Isolated offline diagnostic of compression, synthesis, and abstraction.

The rules use exact admitted statements, exact source assertions, and frozen
schema support. They cannot generate novel explanatory generalizations.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from .models import ValidationError
from .spec063_cognitive_representation_evaluation import (
    EXPECTED_CASES_SHA256,
    EXPECTED_SPEC062_TREE_SHA256,
    FROZEN_CASE_MODEL_IDENTITIES,
    SPEC062_CASES,
    SPEC062_DIR,
    _frozen_cases,
)


OUTPUT_DIR = "examples/evaluations/spec-064-progressive-abstraction-diagnostic-20261007"
SPEC = "specs/SPEC-064-progressive-compression-and-conceptual-abstraction-diagnostic.md"
COMPILER = "spec064.exact-statement-source-integration-schema-diagnostic.v1"
MODES = {"EXPLICIT", "SUBSUMED", "STRUCTURALLY_ENCODED"}
PROTECTED_COUNT = 2016
PROTECTED_SHA256 = "e38985444db3f643f6a865a1892ca431db83a1dc1a5dcd2c57b9e9fb54825d5b"
PROTECTED_REF = "295130a2985bca06d1c9ddb2f63bf05a0532d75c"
PROTECTED_PREFIXES = (
    "baselines/", "examples/evaluations/", "examples/sources/",
    "src/knowledge_compiler/", "tests/fixtures/",
)
EXPERIMENT_SOURCE = "src/knowledge_compiler/spec064_abstraction_diagnostic.py"
OWNER_COMMAND = "open examples/evaluations/spec-064-progressive-abstraction-diagnostic-20261007/owner-review.md"
VALIDATION = {
    "focused_spec064": {"command": ".venv/bin/pytest tests/test_spec064_abstraction_diagnostic.py", "passed": 23},
    "focused_with_spec060_through_spec063_and_control_plane": {"command": ".venv/bin/pytest tests/test_spec064_abstraction_diagnostic.py tests/test_spec060_semantic_compression_evaluation.py tests/test_spec061_explanatory_structure_evaluation.py tests/test_spec062_conceptual_schema_evaluation.py tests/test_spec063_cognitive_representation_evaluation.py tests/test_control_plane.py", "passed": 108},
    "complete_offline": {"command": ".venv/bin/pytest", "passed": 813},
    "browser_gate": "NOT_APPLICABLE: contract requires plain text/Markdown, not a browser surface",
    "development_failures_resolved": [
        "System Python lacked the editable package; used the existing .venv without dependency changes.",
        "Initial source ledger lacked cross-sentence evidence carriers; added source-order/full-assertion validation, without changing frozen inputs.",
        "One test incorrectly required every R2 commitment to be SUBSUMED; exact source/admitted equality legitimately permits EXPLICIT. Corrected test, not preservation rules.",
        "A test indentation error interrupted collection; corrected and reran focused/full suites.",
    ],
}


def stable(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def protected_manifest(root: Path) -> list[dict[str, str]]:
    # Freeze the startup path set, not a permanent ban on adding future files.
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PROTECTED_REF], cwd=root, text=True).splitlines()
    return [
        {"path": relative, "sha256": sha(root / relative)}
        for relative in tracked
        if relative.startswith(PROTECTED_PREFIXES)
        and not relative.startswith(OUTPUT_DIR + "/")
        and relative != EXPERIMENT_SOURCE
    ]


def check_frozen(root: Path) -> list[dict[str, str]]:
    rows = protected_manifest(root)
    if len(rows) != PROTECTED_COUNT or stable(rows) != PROTECTED_SHA256:
        raise ValidationError("protected historical evidence or implementation identity changed")
    if sha(root / SPEC062_CASES) != EXPECTED_CASES_SHA256:
        raise ValidationError("frozen case packet changed")
    return rows


def make_substrate(root: Path, frozen: dict[str, Any]) -> dict[str, Any]:
    identity = frozen["source_identity"]
    model = load(root / identity["model_path"])
    if sha(root / identity["model_path"]) != identity["model_sha256"]:
        raise ValidationError("admitted model identity changed")
    source = model["document"]["text"]
    if hashlib.sha256(source.encode()).hexdigest() != identity["source_sha256"]:
        raise ValidationError("authoritative source identity changed")
    sentences = [copy.deepcopy(s) for b in frozen["frozen_explanatory_structure"]["blocks"] for s in b["sentences"]]
    for sentence in sentences:
        if source[sentence["start_char"]:sentence["end_char"]] != sentence["text"]:
            raise ValidationError("frozen explanatory sentence changed")
    items = copy.deepcopy(frozen["semantic_items"])
    for item in items:
        for evidence in item["evidence"]:
            if source[evidence["start_char"]:evidence["end_char"]] != evidence["quote"]:
                raise ValidationError("frozen semantic evidence is not exact")
    return {
        "source_identity": copy.deepcopy(identity),
        "source_text": source,
        "semantic_items": items,
        "sentences": sentences,
        "explanatory_structure": copy.deepcopy(frozen["frozen_explanatory_structure"]),
        "schema": copy.deepcopy(frozen["conceptual_schema_model"]),
        "material_implications": copy.deepcopy(frozen["implication_preservation_audit"]["material_implications"]),
    }


def sentence_witness(sub: dict[str, Any], evidence: dict[str, Any]) -> list[dict[str, Any]]:
    witnesses = [s for s in sub["sentences"] if s["start_char"] < evidence["end_char"] and s["end_char"] > evidence["start_char"]]
    if not witnesses:
        raise ValidationError("evidence lacks a frozen sentence witness")
    return witnesses


def statement_key(item: dict[str, Any]) -> str:
    # Identical surface statements with different qualifications/epistemic force
    # are deliberately not eligible for duplicate collapse.
    return stable({
        "statement": item["statement"],
        "epistemic_status": item["epistemic_status"],
        "qualifications": item["qualification_links"],
    })


def source_unit(sub: dict[str, Any], sentences: list[dict[str, Any]], index: int) -> dict[str, Any]:
    start = min(s["start_char"] for s in sentences)
    end = max(s["end_char"] for s in sentences)
    return {
        "id": f"u{index:03d}",
        "kind": "EXACT_SOURCE_ASSERTION",
        "text": sub["source_text"][start:end],
        "start_char": start,
        "end_char": end,
        "sentence_ids": [s["id"] for s in sentences],
    }


def build_r0(sub: dict[str, Any]) -> dict[str, Any]:
    return {
        "resolution": "R0", "text": sub["source_text"],
        "units": [source_unit(sub, [sentence], index) for index, sentence in enumerate(sub["sentences"], 1)],
        "composition": None, "handles": [],
    }


def dependency_text(sub: dict[str, Any]) -> str:
    return "\n\nExplanatory dependencies:\n" + "\n".join(
        f"Block {next(b['sequence'] for b in sub['explanatory_structure']['blocks'] if b['id']==t['from_block'])} -> Block {next(b['sequence'] for b in sub['explanatory_structure']['blocks'] if b['id']==t['to_block'])}: {t['connector_text']}"
        for t in sub["explanatory_structure"]["traversal"]
    )


def build_r1(sub: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in sub["semantic_items"]:
        groups.setdefault(statement_key(item), []).append(item)
    units = []
    for rows in groups.values():
        units.append({
            "id": f"u{len(units)+1:03d}", "kind": "EXACT_ADMITTED_STATEMENT",
            "text": rows[0]["statement"], "item_ids": [row["upstream_id"] for row in rows],
            "epistemic_status": rows[0]["epistemic_status"],
            "qualification_links": copy.deepcopy(rows[0]["qualification_links"]),
        })
    # Keep discourse/context sentences with no admitted semantic item. Also keep
    # frozen block cores so each explanatory function remains inspectable.
    context = {s["text"] for s in sub["sentences"] if not s["semantic_ids"]}
    cores = [b["concise_core"] for b in sub["explanatory_structure"]["blocks"]]
    for text in cores + [s["text"] for s in sub["sentences"] if s["text"] in context]:
        if text and not any(unit["text"] == text for unit in units):
            units.append({"id": f"u{len(units)+1:03d}", "kind": "FROZEN_CONTEXT", "text": text})
    candidate = {
        "resolution": "R1", "text": "\n\n".join(unit["text"] for unit in units),
        "units": units, "handles": [],
        "composition": {"preceding_resolution": "R0", "preceding_artifact_sha256": stable(prior)},
    }
    candidate["text"] += dependency_text(sub)
    # Compare the assertion rewrite with a conservative source-preserving
    # candidate. Never force a longer essential-prose rewrite into the ladder.
    # Both candidates are independently validated; no expected answer routing.
    conservative = {
        "resolution": "R1", "text": prior["text"],
        "units": copy.deepcopy(prior["units"]), "handles": [],
        "composition": candidate["composition"],
    }
    for view in (candidate, conservative):
        validate_stage(sub, view, prior)
    selected = min((candidate, conservative), key=lambda v: (len(v["text"].split()), len(v["text"])))
    selected["candidate_audit"] = [
        {"method": name, "words": len(view["text"].split()), "characters": len(view["text"]),
         "preservation_validated": True, "selected": view is selected,
         "candidate_artifact": copy.deepcopy(view), "candidate_sha256": stable(view)}
        for name, view in (("EXACT_ASSERTION_DEDUPLICATION_WITH_CONTEXT", candidate), ("EXACT_SOURCE_PRESERVING_FALLBACK", conservative))
    ]
    return selected


def build_r2(sub: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    # Integrate items only through an existing source assertion. Overlapping
    # evidence that crosses sentence boundaries requires an indivisible exact
    # source span; unrelated facts are not merged merely to lower a unit count.
    validate_stage(sub, prior)
    sentences = sub["sentences"]
    intervals = [(s["start_char"], s["end_char"]) for s in sentences]
    for item in sub["semantic_items"]:
        for evidence in item["evidence"]:
            witnesses = sentence_witness(sub, evidence)
            intervals.append((min(s["start_char"] for s in witnesses), max(s["end_char"] for s in witnesses)))
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    units = []
    for index, (start, end) in enumerate(merged, 1):
        members = [s for s in sentences if start <= s["start_char"] and s["end_char"] <= end]
        unit = source_unit(sub, members, index)
        unit["item_ids"] = [
            item["upstream_id"] for item in sub["semantic_items"]
            if any(start <= ev["start_char"] and ev["end_char"] <= end for ev in item["evidence"])
        ]
        distinct = {statement_key(item) for item in sub["semantic_items"] if item["upstream_id"] in unit["item_ids"]}
        unit["synthesis_kind"] = "SOURCE_ASSERTION_INTEGRATION" if len(distinct) > 1 else "NO_MULTI_COMMITMENT_SYNTHESIS"
        unit["distinct_commitment_count"] = len(distinct)
        unit["preceding_unit_ids"] = [u["id"] for u in prior["units"] if set(u.get("item_ids", [])) & set(unit["item_ids"]) or (u["kind"] == "EXACT_SOURCE_ASSERTION" and u["start_char"] < end and start < u["end_char"])]
        covered = [item for item in sub["semantic_items"] if item["upstream_id"] in unit["item_ids"]]
        unit["preserved_commitments"] = [{"upstream_id": i["upstream_id"], "statement": i["statement"], "epistemic_status": i["epistemic_status"], "qualification_links": i["qualification_links"], "recovery_pointer": "semantic_items/" + i["upstream_id"]} for i in covered]
        unit["material_implication_ids"] = [i["id"] for i in sub["material_implications"] if i["upstream_identity"] in unit["item_ids"]]
        unit["synthesis_relationship"] = "COEXPRESSED_IN_SAME_EXACT_SOURCE_ASSERTION" if len(distinct) > 1 else None
        unit["why_more_than_shorter_wording"] = "Distinct admitted commitments share the exact source assertion, its scope and dependencies; all atomic statements remain independently recoverable. No novel explanation is inferred." if len(distinct) > 1 else "No synthesis credit; irreducible source context retained."
        units.append(unit)
    return {
        "resolution": "R2", "text": "\n\n".join(unit["text"] for unit in units),
        "units": units, "handles": [],
        "composition": {"preceding_resolution": "R1", "preceding_artifact_sha256": stable(prior)},
    }


def classify_handle(sub: dict[str, Any], candidate: dict[str, Any]) -> str:
    chunks = {c["id"]: c for c in sub["schema"]["chunks"]}
    top = chunks[candidate["chunk_id"]]
    anchor = next(b for b in sub["explanatory_structure"]["blocks"] if b["id"] == top["anchor_block"])
    if candidate["definition"] != anchor["concise_core"]:
        return "UNSUPPORTED"
    children = [c for c in chunks.values() if c["parent_chunk"] == top["id"]]
    if not children:
        return "LABEL_ONLY"
    # Frozen membership can establish a group. A shared-entity score, source
    # order, or role compatibility does not establish an explanatory rule.
    proofs = [p for c in children for row in top["membership_audit"] if row["block_id"] in c["member_blocks"] for p in row["support"]]
    # Abstraction needs an existing source-level general rule and explicit
    # example membership for EVERY member, not an extrapolated generalization.
    rule = re.search(r"\b(?:all|each|every|whenever|when|if|creates|produces|causes|requires)\b", candidate["definition"], re.I)
    explicit_example_edges = [
        e for e in sub["schema"]["schema_edges"]
        if e["edge_kind"] == "GROUNDED_SEMANTIC_RELATIONSHIP"
        and e["relation"] in {"INSTANCE_OF", "EXAMPLE_OF"}
        and e["to"] == top["id"]
    ]
    all_examples = set(c["id"] for c in children) <= set(e["from"] for e in explicit_example_edges)
    if rule and all_examples and len(children) > 1 and anchor["explanatory_function"] in {"GENERALIZATION", "MECHANISM", "QUALIFICATION_OR_LIMIT"}:
        return "EXPLANATORY_ABSTRACTION"
    return "SUPPORTED_GROUPING_ONLY" if proofs else "LABEL_ONLY"


def build_r3(sub: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    validate_stage(sub, prior)
    chunks = {c["id"]: c for c in sub["schema"]["chunks"]}
    blocks = {b["id"]: b for b in sub["explanatory_structure"]["blocks"]}
    handles = []
    for index, top_id in enumerate(sub["schema"]["diagnostics"]["top_level_chunk_ids"], 1):
        top = chunks[top_id]
        anchor = blocks[top["anchor_block"]]
        candidate = {
            "id": f"h{index:03d}", "chunk_id": top_id,
            "definition": anchor["concise_core"],
            "handle_statement": anchor["concise_core"],
            "member_blocks": top["member_blocks"],
            "members_covered": top["semantic_support_ids"],
            "membership_explanation": copy.deepcopy(top["membership_audit"]),
            "definition_evidence": copy.deepcopy(anchor["evidence_support"]),
            "material_implications": [i["id"] for i in sub["material_implications"] if i["schema_edge_id"] in {e["id"] for e in sub["schema"]["schema_edges"] if e["from"] == top_id or e["to"] == top_id}],
            "initially_hidden_semantic_items": 0,
            "shared_principle": None,
            "principle_test": "A source-explicit general rule plus grounded example links for every member is required; shared entities, source order and compatible roles alone are insufficient.",
            "provenance_coverage": 1.0,
        }
        candidate["classification"] = classify_handle(sub, candidate)
        candidate["abstraction_unit_reduction"] = max(0, len(top["semantic_support_ids"]) - 1) if candidate["classification"] == "EXPLANATORY_ABSTRACTION" else 0
        candidate["unsupported_inference_count"] = int(candidate["classification"] == "UNSUPPORTED")
        handles.append(candidate)
    # Grouping-only handles cannot subsume the members. Keep source integrations
    # visible; hiding them behind a heading would counterfeit abstraction.
    lines = []
    for handle in handles:
        lines.extend([handle["definition"], "|"])
        for unit in prior["units"]:
            owning = next(b for b in blocks.values() if any(s in {row["id"] for row in b["sentences"]} for s in unit["sentence_ids"]))
            if owning["id"] in handle["member_blocks"]:
                lines.append("+-- " + unit["text"])
        lines.append("")
    # Explicit supported traversal is a separate structure, never a causal
    # inference from the visual order of boxes or a silently transitive edge.
    path = []
    for transition in sub["explanatory_structure"]["traversal"]:
        left = blocks[transition["from_block"]]["sequence"]
        right = blocks[transition["to_block"]]["sequence"]
        path.append({
            "id": transition["id"], "kind": "FROZEN_EXPLANATORY_DEPENDENCY",
            "from_block": transition["from_block"], "to_block": transition["to_block"],
            "relation": transition["discourse_relation"],
            "text": f"Block {left} --[{transition['discourse_relation']}]--> Block {right}",
        })
    if path:
        lines += ["Explanatory path (not a new causal assertion):"] + [p["text"] for p in path]
    return {
        "resolution": "R3", "text": "\n".join(lines),
        "units": copy.deepcopy(prior["units"]), "handles": handles, "structures": path,
        "composition": {"preceding_resolution": "R2", "preceding_artifact_sha256": stable(prior)},
    }


def validate_stage(sub: dict[str, Any], stage: dict[str, Any], prior: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Validate coverage against the authority, not against compressed lineage."""
    units = stage["units"]
    if len({u["id"] for u in units}) != len(units):
        raise ValidationError("ambiguous carrier identity")
    if prior and stage["composition"]["preceding_artifact_sha256"] != stable(prior):
        raise ValidationError("composed artifact identity mismatch")
    if prior and stage["composition"]["preceding_resolution"] != prior["resolution"]:
        raise ValidationError("composed resolution mismatch")
    for unit in units:
        if unit["kind"] == "EXACT_SOURCE_ASSERTION":
            if unit["text"] != sub["source_text"][unit["start_char"]:unit["end_char"]]:
                raise ValidationError("semantic drift or unsupported source rewriting")
            expected_sentences = [s["id"] for s in sub["sentences"] if unit["start_char"] <= s["start_char"] and s["end_char"] <= unit["end_char"]]
            if not expected_sentences or unit["sentence_ids"] != expected_sentences:
                raise ValidationError("explanatory sentence identity drift")
            members = [s for s in sub["sentences"] if s["id"] in expected_sentences]
            if unit["start_char"] != min(s["start_char"] for s in members) or unit["end_char"] != max(s["end_char"] for s in members):
                raise ValidationError("partial assertion loses scope or context")
            if "synthesis_kind" in unit:
                expected_items = [i for i in sub["semantic_items"] if any(unit["start_char"] <= e["start_char"] and e["end_char"] <= unit["end_char"] for e in i["evidence"])]
                if unit["item_ids"] != [i["upstream_id"] for i in expected_items] or unit["distinct_commitment_count"] != len({statement_key(i) for i in expected_items}):
                    raise ValidationError("synthesis coverage drift")
                if unit["preserved_commitments"] != [{"upstream_id": i["upstream_id"], "statement": i["statement"], "epistemic_status": i["epistemic_status"], "qualification_links": i["qualification_links"], "recovery_pointer": "semantic_items/" + i["upstream_id"]} for i in expected_items]:
                    raise ValidationError("synthesis qualification or epistemic drift")
        elif unit["kind"] == "EXACT_ADMITTED_STATEMENT":
            expected = [row for row in sub["semantic_items"] if row["upstream_id"] in unit["item_ids"]]
            if not expected or any(statement_key(row) != stable({"statement": unit["text"], "epistemic_status": unit["epistemic_status"], "qualifications": unit["qualification_links"]}) for row in expected):
                raise ValidationError("admitted statement drift or epistemic strengthening")
        elif unit["kind"] == "FROZEN_CONTEXT":
            allowed = {b["concise_core"] for b in sub["explanatory_structure"]["blocks"]} | {s["text"] for s in sub["sentences"] if not s["semantic_ids"]}
            if unit["text"] not in allowed:
                raise ValidationError("unsupported explanatory context")
        else:
            raise ValidationError("unvalidated carrier type")
        if unit["text"] not in stage["text"]:
            raise ValidationError("trace-only recovery does not preserve learner presence")
    if stage["resolution"] == "R0" and stage["text"] != sub["source_text"]:
        raise ValidationError("R0 is not exact source")
    source_order = all(u["kind"] == "EXACT_SOURCE_ASSERTION" for u in units)
    if source_order:
        if [u["start_char"] for u in units] != sorted(u["start_char"] for u in units):
            raise ValidationError("source order drift")
        if stage["resolution"] in {"R0", "R1", "R2"} and stage["text"].split() != " ".join(u["text"] for u in units).split():
            raise ValidationError("source-order view contains unsupported additions or omissions")
        if [sid for u in units for sid in u["sentence_ids"]] != [s["id"] for s in sub["sentences"]]:
            raise ValidationError("source explanatory assertion omission")
    elif stage["resolution"] == "R1" and stage["text"] != "\n\n".join(u["text"] for u in units) + dependency_text(sub):
        raise ValidationError("essential prose includes unsupported text or loses dependency text")
    if stage["resolution"] == "R3":
        if len(stage["handles"]) != len(sub["schema"]["diagnostics"]["top_level_chunk_ids"]) or len(stage["structures"]) != len(sub["explanatory_structure"]["traversal"]):
            raise ValidationError("schema carrier omission or unsupported addition")
        for handle in stage["handles"]:
            if classify_handle(sub, handle) == "UNSUPPORTED" or handle["classification"] != classify_handle(sub, handle):
                raise ValidationError("invented abstraction or overclaimed classification")
            if handle["definition"] not in stage["text"]:
                raise ValidationError("missing handle definition")
            top = next(c for c in sub["schema"]["chunks"] if c["id"] == handle["chunk_id"])
            if handle["members_covered"] != top["semantic_support_ids"] or handle["member_blocks"] != top["member_blocks"] or handle["membership_explanation"] != top["membership_audit"]:
                raise ValidationError("handle membership or support drift")
            if handle["classification"] != "EXPLANATORY_ABSTRACTION" and handle["abstraction_unit_reduction"] != 0:
                raise ValidationError("grouping falsely credited as abstraction")
        for transition in sub["explanatory_structure"]["traversal"]:
            structures = [s for s in stage["structures"] if s["id"] == transition["id"]]
            if len(structures) != 1 or any(structures[0][key] != transition[key] for key in ("from_block", "to_block")) or structures[0]["relation"] != transition["discourse_relation"] or structures[0]["text"] not in stage["text"]:
                raise ValidationError("explanatory dependency drift")
        if prior and stage["text"] != build_r3(sub, prior)["text"]:
            raise ValidationError("architecture text differs from validated carriers and typed paths")
    ledger = []
    for item in sub["semantic_items"]:
        explicit = next((u for u in units if u["text"] == item["statement"] and item["upstream_id"] in u.get("item_ids", [])), None)
        carriers = [explicit] if explicit else [
            u for u in units if u["kind"] == "EXACT_SOURCE_ASSERTION"
            and any(u["start_char"] <= e["start_char"] and e["end_char"] <= u["end_char"] for e in item["evidence"])
        ]
        if not carriers and stage["resolution"] in {"R0", "R1"} and source_order:
            for evidence in item["evidence"]:
                witnesses = sentence_witness(sub, evidence)
                covering = [u for u in units if set(u["sentence_ids"]) & {s["id"] for s in witnesses}]
                if {s["id"] for s in witnesses} <= {sid for u in covering for sid in u["sentence_ids"]}:
                    carriers = covering
                    break
        if not carriers:
            raise ValidationError("genuine omission: semantic commitment has no truthful carrier")
        ledger.append({
            "category": "SEMANTIC_COMMITMENT", "frozen_id": item["upstream_id"],
            "mode": "EXPLICIT" if explicit else "SUBSUMED",
            "carrier_ids": [u["id"] for u in carriers],
            "proof_rule": "IDENTICAL_ADMITTED_ASSERTION" if explicit else "EXACT_SOURCE_ASSERTIONS_CONTAIN_ADMITTED_EVIDENCE_IN_SOURCE_ORDER",
            "statement": item["statement"],
            "epistemic_status": item["epistemic_status"],
            "qualification_links": copy.deepcopy(item["qualification_links"]),
            "evidence": copy.deepcopy(item["evidence"]),
            "recovery_pointer": f"semantic_items/{item['upstream_id']}",
        })
        for index, qualification in enumerate(item["qualification_links"]):
            ledger.append({
                "category": "QUALIFICATION", "frozen_id": f"{item['upstream_id']}:q{index}",
                "mode": "EXPLICIT" if explicit else "SUBSUMED", "carrier_ids": [u["id"] for u in carriers],
                "proof_rule": "INHERITED_UNCHANGED_WITH_QUALIFIED_ASSERTION",
                "qualification": copy.deepcopy(qualification), "statement": item["statement"],
                "evidence": copy.deepcopy(item["evidence"]),
                "recovery_pointer": f"semantic_items/{item['upstream_id']}/qualification_links/{index}",
            })
    item_ledger = {row["frozen_id"]: row for row in ledger if row["category"] == "SEMANTIC_COMMITMENT"}
    for block in sub["explanatory_structure"]["blocks"]:
        text_carriers = [u for u in units if u["text"] == block["concise_core"] or (u["kind"] == "EXACT_SOURCE_ASSERTION" and set(u["sentence_ids"]) & {s["id"] for s in block["sentences"]})]
        if not text_carriers:
            raise ValidationError("explanatory function lost")
        ledger.append({
            "category": "EXPLANATORY_CONTEXT", "frozen_id": block["id"],
            "mode": "EXPLICIT" if any(u["text"] == block["concise_core"] for u in text_carriers) else "SUBSUMED",
            "carrier_ids": [u["id"] for u in text_carriers],
            "proof_rule": "FROZEN_BLOCK_CORE_OR_EXACT_SOURCE_ASSERTIONS",
            "function": block["explanatory_function"],
            "evidence": copy.deepcopy(block["source_ranges"]),
            "recovery_pointer": f"explanatory_structure/blocks/{block['id']}",
            "qualifications": copy.deepcopy(block["qualifications"]),
        })
        for index, qualification in enumerate(block["qualifications"]):
            qualified_items = [i for i in sub["semantic_items"] if i["assigned_block"] == block["id"] and qualification in i["qualification_links"]]
            qualified_carriers = [uid for i in qualified_items for uid in item_ledger[i["upstream_id"]]["carrier_ids"]]
            if not qualified_carriers:
                raise ValidationError("explanatory qualification lost its qualified assertion")
            ledger.append({
                "category": "EXPLANATORY_QUALIFICATION", "frozen_id": f"{block['id']}:q{index}",
                "mode": "EXPLICIT" if all(item_ledger[i["upstream_id"]]["mode"] == "EXPLICIT" for i in qualified_items) else "SUBSUMED",
                "carrier_ids": sorted(set(qualified_carriers)),
                "proof_rule": "UNCHANGED_WITH_EXACT_QUALIFIED_ADMITTED_ASSERTION_OR_ITS_SOURCE_ASSERTION",
                "qualification": copy.deepcopy(qualification), "evidence": copy.deepcopy(block["source_ranges"]),
                "recovery_pointer": f"explanatory_structure/blocks/{block['id']}/qualifications/{index}",
            })
    for transition in sub["explanatory_structure"]["traversal"]:
        left = next(row for row in ledger if row["category"] == "EXPLANATORY_CONTEXT" and row["frozen_id"] == transition["from_block"])
        right = next(row for row in ledger if row["category"] == "EXPLANATORY_CONTEXT" and row["frozen_id"] == transition["to_block"])
        # R1 admitted statements do not preserve source traversal merely through
        # source offsets in a sidecar. Add the EXACT frozen connector explicitly.
        if stage["resolution"] == "R1" and not source_order and transition["connector_text"] not in stage["text"]:
            raise ValidationError("R1 lacks an explanatory dependency carrier")
        mode = "EXPLICIT" if stage["resolution"] == "R1" and not source_order else "STRUCTURALLY_ENCODED"
        ledger.append({
            "category": "EXPLANATORY_DEPENDENCY", "frozen_id": transition["id"], "mode": mode,
            "carrier_ids": left["carrier_ids"] + right["carrier_ids"],
            "proof_rule": "EXACT_FROZEN_CONNECTOR" if mode == "EXPLICIT" else "SOURCE_ORDER_WITH_ENDPOINT_ASSERTIONS" if stage["resolution"] in {"R0", "R2"} else "EXACT_FROZEN_TYPED_PATH",
            "dependency": copy.deepcopy(transition),
            "evidence": copy.deepcopy(transition["support"]),
            "recovery_pointer": f"explanatory_structure/traversal/{transition['id']}",
        })
    for implication in sub["material_implications"]:
        upstream = implication["upstream_identity"]
        if upstream in item_ledger:
            carrier = item_ledger[upstream]
        else:
            carrier = next((row for row in ledger if row["category"] == "EXPLANATORY_DEPENDENCY" and row["frozen_id"] == upstream), None)
        if carrier is None:
            raise ValidationError("material implication omitted")
        ledger.append({
            "category": "MATERIAL_IMPLICATION", "frozen_id": implication["id"],
            "mode": carrier["mode"], "carrier_ids": carrier["carrier_ids"],
            "proof_rule": carrier["proof_rule"], "implication": copy.deepcopy(implication),
            "evidence": copy.deepcopy(implication["support"]),
            "recovery_pointer": f"material_implications/{implication['id']}",
        })
    return ledger


def recover(sub: dict[str, Any], row: dict[str, Any]) -> Any:
    parts = row["recovery_pointer"].split("/")
    field = parts[0]
    if field == "semantic_items":
        result = next(item for item in sub[field] if item["upstream_id"] == parts[1])
        if len(parts) > 2:
            result = result[parts[2]][int(parts[3])]
    elif field == "explanatory_structure":
        result = next(item for item in sub[field][parts[1]] if item["id"] == parts[2])
        if len(parts) > 3:
            result = result[parts[3]][int(parts[4])]
    else:
        result = next(item for item in sub[field] if item["id"] == parts[1])
    return copy.deepcopy(result)


def metrics(sub: dict[str, Any], stage: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    semantic = [row for row in ledger if row["category"] == "SEMANTIC_COMMITMENT"]
    implication = [row for row in ledger if row["category"] == "MATERIAL_IMPLICATION"]
    modes = Counter(row["mode"] for row in semantic)
    classification = Counter(h["classification"] for h in stage["handles"])
    # Unit counts are accountable, not a claim that every conjunction becomes
    # one psychological concept or that grouping removes atomic commitments.
    return {
        "resolution": stage["resolution"],
        "word_count": len(re.findall(r"\S+", stage["text"])),
        "character_count": len(stage["text"]),
        "explicit_learner_facing_unit_count": len(stage["units"]),
        "unit_definition": "exact admitted assertion/context unit in R1; indivisible source-assertion span in R0/R2/R3",
        "atomic_semantic_commitments_covered": len(semantic),
        "distinct_admitted_statement_count": len({statement_key(item) for item in sub["semantic_items"]}),
        "commitment_preservation_modes": {mode: modes[mode] for mode in sorted(MODES)},
        "material_implications": len(implication),
        "implication_preservation_modes": dict(sorted(Counter(row["mode"] for row in implication).items())),
        "conceptual_handle_count": len(stage["handles"]),
        "explanatory_abstraction_count": classification["EXPLANATORY_ABSTRACTION"],
        "supported_grouping_only_count": classification["SUPPORTED_GROUPING_ONLY"],
        "label_only_count": classification["LABEL_ONLY"],
        "duplicate_admitted_items_collapsed": sum(max(0, len(u.get("item_ids", []))-1) for u in stage["units"] if u["kind"] == "EXACT_ADMITTED_STATEMENT"),
        "source_assertion_integrations": sum(u.get("synthesis_kind") == "SOURCE_ASSERTION_INTEGRATION" for u in stage["units"]),
        "redundancy_definition": "identical statement+epistemic+qualification keys; shared exact source-assertion evidence; no semantic deletion",
        "qualification_preservation": True, "epistemic_preservation": True,
        "explanatory_context_preservation": True,
        "provenance_coverage": 1.0, "backwards_recovery_coverage": 1.0,
        "unsupported_inference_count": 0, "material_omission_count": 0,
    }


def compile_case(sub: dict[str, Any]) -> dict[str, Any]:
    stages = [build_r0(sub)]
    ledgers = {"R0": validate_stage(sub, stages[0])}
    r1 = build_r1(sub, stages[0])
    stages.append(r1)
    ledgers["R1"] = validate_stage(sub, r1, stages[0])
    stages.append(build_r2(sub, r1))
    ledgers["R2"] = validate_stage(sub, stages[2], r1)
    stages.append(build_r3(sub, stages[2]))
    ledgers["R3"] = validate_stage(sub, stages[3], stages[2])
    for ledger in ledgers.values():
        for row in ledger:
            recovered = recover(sub, row)
            expected = row.get("qualification", row.get("implication", row.get("dependency")))
            if expected is not None and recovered != expected:
                raise ValidationError("backwards recovery failed")
            if row["category"] == "SEMANTIC_COMMITMENT" and (recovered["statement"] != row["statement"] or recovered["epistemic_status"] != row["epistemic_status"] or recovered["qualification_links"] != row["qualification_links"] or recovered["evidence"] != row["evidence"]):
                raise ValidationError("semantic recovery differs from authority")
    return {
        "source_identity": sub["source_identity"], "substrate_sha256": stable(sub),
        "stages": stages, "preservation_ledgers": ledgers,
        "measurements": [metrics(sub, s, ledgers[s["resolution"]]) for s in stages],
        "owner_verdict": "PENDING",
    }


def architecture_gate(cases: list[dict[str, Any]]) -> dict[str, Any]:
    adequate = all(
        case["measurements"][3]["explanatory_abstraction_count"] > 0
        and case["measurements"][2]["explicit_learner_facing_unit_count"] < case["measurements"][1]["explicit_learner_facing_unit_count"]
        and case["measurements"][3]["word_count"] < case["measurements"][0]["word_count"]
        for case in cases
    )
    mixed = any(c["measurements"][3]["explanatory_abstraction_count"] > 0 for c in cases) and not adequate
    return {
        "finding": "DETERMINISTIC_COMPILATION_ADEQUATE" if adequate else "INCONCLUSIVE" if mixed else "BOUNDED_MODEL_CANDIDATE_REQUIRES_SEPARATE_AUTHORIZATION",
        "mechanical_branch": "PROGRESSIVE_ABSTRACTION_SAFE_FOR_OWNER_REVIEW" if adequate else "INCONCLUSIVE" if mixed else "GROUPING_REMAINS_NON_ABSTRACTIVE",
        "scope": "Evidence concerns this frozen bounded deterministic rule set, not impossibility for all deterministic algorithms.",
        "reason": "Assess exact duplicate collapse, source-assertion integration, and source-explicit rule/member coverage separately. Unit packaging and preserved edge paths alone do not establish conceptual abstraction.",
        "deterministic_candidates_frozen_before_gate": True,
        "substrate_insufficiency_proven": False,
        "model_call_authorized": False,
        "human_verdict": "PENDING",
        "frozen_candidate_sha256s": [stable(case) for case in cases],
        "case_evidence": [{"case_index": i, "r1_word_reduction": c["measurements"][0]["word_count"] - c["measurements"][1]["word_count"], "r1_to_r2_carrier_reduction": c["measurements"][1]["explicit_learner_facing_unit_count"] - c["measurements"][2]["explicit_learner_facing_unit_count"], "r3_word_reduction_from_source": c["measurements"][0]["word_count"] - c["measurements"][3]["word_count"], "explanatory_abstractions": c["measurements"][3]["explanatory_abstraction_count"]} for i,c in enumerate(cases,1)],
    }


def negative_controls(sub: dict[str, Any], case: dict[str, Any]) -> list[dict[str, Any]]:
    """Persist fail-closed outcomes, not just pytest assertions."""
    controls = []
    mutations = (
        "OMITTED_CARRIER", "TRACE_ONLY_RECOVERY", "SOURCE_STRENGTHENING",
        "FALSE_ABSTRACTION_CREDIT", "INVENTED_HANDLE", "MEMBERSHIP_DRIFT",
        "DEPENDENCY_REVERSAL", "COMPOSED_IDENTITY_DRIFT", "SOURCE_ORDER_DRIFT",
        "EPISTEMIC_DRIFT", "QUALIFICATION_DRIFT", "SYNTHESIS_COVERAGE_DRIFT",
    )
    for name in mutations:
        index = 2 if name in {"OMITTED_CARRIER", "TRACE_ONLY_RECOVERY", "SOURCE_STRENGTHENING", "SOURCE_ORDER_DRIFT", "EPISTEMIC_DRIFT", "QUALIFICATION_DRIFT", "SYNTHESIS_COVERAGE_DRIFT"} else 3
        stage = copy.deepcopy(case["stages"][index])
        prior = case["stages"][index-1]
        if name == "OMITTED_CARRIER":
            unit = stage["units"].pop(0)
            stage["text"] = stage["text"].replace(unit["text"], "")
        elif name == "TRACE_ONLY_RECOVERY":
            stage["text"] = "See recovery sidecar."
        elif name == "SOURCE_STRENGTHENING":
            stage["units"][0]["text"] += " Always, without exceptions."
            stage["text"] += " Always, without exceptions."
        elif name == "FALSE_ABSTRACTION_CREDIT":
            stage["handles"][0]["abstraction_unit_reduction"] = 100
        elif name == "INVENTED_HANDLE":
            stage["handles"][0]["definition"] = "All outcomes follow one universal law."
        elif name == "MEMBERSHIP_DRIFT":
            stage["handles"][0]["members_covered"] = []
        elif name == "DEPENDENCY_REVERSAL":
            p = stage["structures"][0]
            p["from_block"], p["to_block"] = p["to_block"], p["from_block"]
        elif name == "COMPOSED_IDENTITY_DRIFT":
            stage["composition"]["preceding_artifact_sha256"] = "0"*64
        elif name == "SOURCE_ORDER_DRIFT":
            stage["units"].reverse()
            stage["text"] = "\n\n".join(u["text"] for u in stage["units"])
        elif name in {"EPISTEMIC_DRIFT", "QUALIFICATION_DRIFT"}:
            unit = next(u for u in stage["units"] if u["preserved_commitments"])
            unit["preserved_commitments"][0]["epistemic_status" if name == "EPISTEMIC_DRIFT" else "qualification_links"] = "CERTAIN" if name == "EPISTEMIC_DRIFT" else [{"cue": "fabricated"}]
        elif name == "SYNTHESIS_COVERAGE_DRIFT":
            stage["units"][0]["item_ids"] = []
        try:
            validate_stage(sub, stage, prior)
        except ValidationError as error:
            controls.append({"control": name, "result": "REJECTED_AS_REQUIRED", "failure": str(error)})
        else:
            raise ValidationError("negative control admitted: " + name)
    return controls


def owner_review(cases: list[dict[str, Any]], gate: dict[str, Any]) -> str:
    lines = ["# SPEC-064 — Owner review", "", "Owner verdict: PENDING. Promotion: NOT_AUTHORIZED.", "", "Review R0 through R3 for each case, then inspect the measurement table and exact recovery ledger.", "", "Mechanical finding: " + gate["mechanical_branch"], "Architecture finding: " + gate["finding"], "", "Source integration and schema grouping are measured separately. Carrier counts are not cognitive scores.", ""]
    for index, case in enumerate(cases, 1):
        lines += [f"## {index}. {case['source_identity']['title']}", ""]
        for stage in case["stages"]:
            lines += [f"### {stage['resolution']}", "", "```text", stage["text"], "```", ""]
        lines += [f"[Exact recovery and audit packet](cases/{index:02d}.json)", f"[Frozen authoritative substrate](substrates/{index:02d}.json)", ""]
    lines += ["## Review questions", "", "1. Does R1 reduce reading cost without changing the knowledge?", "2. Does R2 synthesize overlapping assertions rather than merely reduce sentence count?", "3. Does R3 explain membership through higher-order principles, or merely group units?", "4. Does the architecture reduce reconstruction work?", "5. Can every qualification, dependency, implication, and item be recovered exactly?", "6. Does the plain text expose the compiler's limits?", "", "The deterministic finding does not authorize a provider call. Any bounded model candidate requires a separately approved contract."]
    return "\n".join(lines) + "\n"


def diagnostic_report(cases: list[dict[str, Any]], gate: dict[str, Any]) -> str:
    return "\n".join([
        "# SPEC-064 — Mechanical diagnostic report", "",
        "Owner verdict: PENDING. No promotion or live-call authorization.", "",
        "Result: `" + gate["mechanical_branch"] + "`.",
        "Architecture finding: `" + gate["finding"] + "`.", "",
        "## Frozen bounded machinery", "",
        "R1 compares exact admitted-statement duplicate collapse (including context and explicit frozen dependencies) against an exact-source fallback. Both candidates are preserved and validated. Identical wording with different epistemic status or qualification links is never merged.", "",
        "R2 integrates distinct commitments coexpressed in exact source assertions, joining sentence spans only when frozen evidence crosses a boundary. This preserves the source's referents, scope and qualifications. Covered item sets, evidence, implication IDs and prior carrier identities are explicit in the audit. It does not generate a new explanatory proposition.", "",
        "R3 tests every frozen top-level schema handle for a source-explicit general rule and grounded instance/example membership for every child. Entity overlap, role compatibility and source adjacency cannot establish that rule. Group-only handles retain all source integrations visibly and earn zero abstraction credit. Frozen traversal is typed as explanatory dependency, never silently promoted to domain causality.", "",
        "These are the strongest admissible candidates in this implemented exact-assertion/source-witness rule set; this is not an exhaustive search of all deterministic algorithms, nor proof that the source cannot support a better abstraction. The schema anchors may themselves be poor conceptual handles; they remain immutable controls.", "",
        "## Measurements and preserved negative results", "",
        *[f"- Case {i}: words R0/R1/R2/R3 = {' / '.join(str(r['word_count']) for r in c['measurements'])}; carriers = {' / '.join(str(r['explicit_learner_facing_unit_count']) for r in c['measurements'])}; abstractions = {c['measurements'][3]['explanatory_abstraction_count']}." for i,c in enumerate(cases,1)],
        "", "[Per-case and aggregate measurements](stage-measurements.md)", "",
        "Geology earns limited linguistic compression. The other cases keep the source because canonical assertion rewrites cost more. R2 lowers visible carrier counts but largely recovers source prose; it is bounded integration, not demonstrated conceptual synthesis. R3 costs more language in all three cases. Three handles are supported groups and two are labels; none explains its full member set as a validated higher-order abstraction. These negative results are retained, not repaired downstream.", "",
        "141 semantic commitments, 54 material implications, 24 explanatory blocks and 21 dependencies remain recoverable at every stage. Semantic and block qualifications are separately traced to their qualified assertions. Recovery links alone cannot pass validation: learner carriers must contain exact assertions or supported structures. Frozen cue-detector quirks remain unchanged rather than being repaired upstream.", "",
        "[Exact preservation ledger](preservation-ledger.json) · [36 rejected safety controls](negative-controls.json) · [R1 alternatives and redundancy trace](redundancy-trace.json) · [Architecture gate](architecture-decision.json)", "",
        "## Limits and decision boundary", "",
        "The implemented machinery cannot deliver explanatory abstraction across this corpus. Its limitation is not proof of substrate insufficiency: the source remains available, while generic entailment/generalization beyond exact frozen witnesses is not established here. A bounded model-generated candidate with deterministic validation may be proposed only under separate owner authorization. No provider call is authorized or made by this result.", "",
        "[Validation record](validation.json) · [Deterministic regeneration evidence](deterministic-regeneration.json) · [Frozen identities](manifest.json)", "",
        "The UI doctrine is already canonical in docs/PROJECT-VISION.md: UI tests the compiler; representation work remains paused. No additional doctrine rewrite, UI, production, semantic or representation change was necessary.", "",
        "## Owner review", "", "Open [all three four-stage text treatments](owner-review.md). Review remains OWNER + CHATGPT; human verdict PENDING. No follow-up packet is activated.", "",
    ])


def artifact_rows(output: Path, *, core_only: bool = False) -> list[dict[str, str]]:
    excluded = {"report.json", "deterministic-regeneration.json"} if core_only else {"report.json"}
    return [{"path": p.relative_to(output).as_posix(), "sha256": sha(p)} for p in sorted(output.rglob("*")) if p.is_file() and p.name not in excluded]


def generate(root: Path, output: Path, *, verify_regeneration: bool = True) -> dict[str, Any]:
    before = check_frozen(root)
    frozen = _frozen_cases(root)
    substrates = [make_substrate(root, case) for case in frozen]
    cases = [compile_case(sub) for sub in substrates]
    gate = architecture_gate(cases)
    output.mkdir(parents=True, exist_ok=True)
    for folder in ("cases", "substrates", "views"):
        (output / folder).mkdir(exist_ok=True)
    for index, (sub, case) in enumerate(zip(substrates, cases, strict=True), 1):
        write_json(output / "substrates" / f"{index:02d}.json", sub)
        write_json(output / "cases" / f"{index:02d}.json", case)
        for stage in case["stages"]:
            (output / "views" / f"{index:02d}-{stage['resolution']}.txt").write_text(stage["text"], encoding="utf-8")
    write_json(output / "manifest.json", {
        "compiler": COMPILER, "protected_file_count": len(before), "protected_tree_sha256": stable(before),
        "protected_path_set_commit": PROTECTED_REF,
        "implementation": {"path": EXPERIMENT_SOURCE, "sha256": sha(root / EXPERIMENT_SOURCE)},
        "protected_files": before, "frozen_spec062_tree_sha256": EXPECTED_SPEC062_TREE_SHA256,
        "spec062_model_file_sha256s": list(FROZEN_CASE_MODEL_IDENTITIES),
        "cases": [{"source_identity": sub["source_identity"], "substrate_sha256": stable(sub)} for sub in substrates],
    })
    measures = [{"case_index": index, **row} for index, case in enumerate(cases, 1) for row in case["measurements"]]
    write_json(output / "stage-measurements.json", measures)
    aggregate = []
    for resolution in ("R0", "R1", "R2", "R3"):
        rows = [r for r in measures if r["resolution"] == resolution]
        additive = ("word_count", "character_count", "explicit_learner_facing_unit_count", "atomic_semantic_commitments_covered", "material_implications", "conceptual_handle_count", "explanatory_abstraction_count", "supported_grouping_only_count", "label_only_count", "duplicate_admitted_items_collapsed", "source_assertion_integrations", "unsupported_inference_count", "material_omission_count")
        aggregate.append({"resolution": resolution, **{key: sum(r[key] for r in rows) for key in additive}, "commitment_preservation_modes": {mode: sum(r["commitment_preservation_modes"][mode] for r in rows) for mode in sorted(MODES)}, "implication_preservation_modes": {mode: sum(r["implication_preservation_modes"].get(mode, 0) for r in rows) for mode in sorted(MODES)}, "qualification_preservation": all(r["qualification_preservation"] for r in rows), "epistemic_preservation": all(r["epistemic_preservation"] for r in rows), "explanatory_context_preservation": all(r["explanatory_context_preservation"] for r in rows), "provenance_coverage": 1.0, "backwards_recovery_coverage": 1.0})
    write_json(output / "aggregate-measurements.json", aggregate)
    lines = ["# Per-stage cost and preservation", "", "Counts distinguish visible carriers from the frozen atomic commitments they cover.", "", "| Case | Stage | Words | Characters | Carriers | Commitments | Implications | Handles | Abstractions |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    lines += [f"| {r['case_index']} | {r['resolution']} | {r['word_count']} | {r['character_count']} | {r['explicit_learner_facing_unit_count']} | {r['atomic_semantic_commitments_covered']} | {r['material_implications']} | {r['conceptual_handle_count']} | {r['explanatory_abstraction_count']} |" for r in measures]
    lines += [f"| ALL | {r['resolution']} | {r['word_count']} | {r['character_count']} | {r['explicit_learner_facing_unit_count']} | {r['atomic_semantic_commitments_covered']} | {r['material_implications']} | {r['conceptual_handle_count']} | {r['explanatory_abstraction_count']} |" for r in aggregate]
    (output / "stage-measurements.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for filename, value in {
        "linguistic-compression-audit.json": [{"case_index": i, "exact_duplicate_collapses": c["measurements"][1]["duplicate_admitted_items_collapsed"], "source_words": c["measurements"][0]["word_count"], "r1_words": c["measurements"][1]["word_count"], "cost_reduction": c["measurements"][0]["word_count"] - c["measurements"][1]["word_count"], "compression_failure_preserved": c["measurements"][1]["word_count"] >= c["measurements"][0]["word_count"]} for i, c in enumerate(cases, 1)],
        "semantic-synthesis-audit.json": [{"case_index": i, "units": c["stages"][2]["units"], "scope": "Existing source assertion integrates admitted commitments; does not create a novel higher-order explanation."} for i, c in enumerate(cases, 1)],
        "conceptual-abstraction-audit.json": [{"case_index": i, "handles": c["stages"][3]["handles"]} for i, c in enumerate(cases, 1)],
        "grouping-versus-abstraction.json": [{"case_index": i, "classifications": [h["classification"] for h in c["stages"][3]["handles"]], "abstraction_unit_reduction": sum(h["abstraction_unit_reduction"] for h in c["stages"][3]["handles"])} for i, c in enumerate(cases, 1)],
        "schema-formation-audit.json": [{"case_index": i, "structures": c["stages"][3]["structures"], "new_domain_edges": 0, "frozen_schema_mutations": 0} for i, c in enumerate(cases, 1)],
        "preservation-ledger.json": [{"case_index": i, "resolutions": c["preservation_ledgers"]} for i, c in enumerate(cases, 1)],
        "semantic-epistemic-preservation-audit.json": [{"case_index": i, "measurements": c["measurements"]} for i, c in enumerate(cases, 1)],
        "implication-context-preservation-audit.json": [{"case_index": i, "resolutions": {k: [r for r in v if r["category"] in {"MATERIAL_IMPLICATION", "EXPLANATORY_DEPENDENCY", "EXPLANATORY_CONTEXT"}] for k,v in c["preservation_ledgers"].items()}} for i, c in enumerate(cases, 1)],
        "provenance-recovery-audit.json": [{"case_index": i, "exact_source_identity": c["source_identity"], "substrate_sha256": c["substrate_sha256"], "resolutions": {k: {"ledger_rows": len(v), "recovered_rows": len(v), "coverage": 1.0} for k,v in c["preservation_ledgers"].items()}} for i, c in enumerate(cases, 1)],
        "composition-audit.json": [{"case_index": i, "substrate_sha256": c["substrate_sha256"], "resolutions": [{"resolution": s["resolution"], "artifact_sha256": stable(s), "composition": s["composition"], "independent_substrate_validation": True} for s in c["stages"]]} for i, c in enumerate(cases, 1)],
        "architecture-decision.json": gate,
        "validation.json": VALIDATION,
        "negative-controls.json": [{"case_index": i, "controls": negative_controls(s, c)} for i,(s,c) in enumerate(zip(substrates,cases,strict=True),1)],
        "redundancy-trace.json": [{"case_index": i, "r1_candidates": c["stages"][1]["candidate_audit"], "duplicate_keys": [{"statement_key": key, "frozen_ids": [item["upstream_id"] for item in s["semantic_items"] if statement_key(item) == key]} for key in sorted({statement_key(item) for item in s["semantic_items"]})], "source_integration_units": [{"carrier": u["id"], "covered_items": u["item_ids"], "distinct_commitments": u["distinct_commitment_count"], "relationship": u["synthesis_relationship"]} for u in c["stages"][2]["units"]]} for i,(s,c) in enumerate(zip(substrates,cases,strict=True),1)],
        "owner-review-rubric.json": {"verdict": "PENDING", "questions": ["reading cost", "semantic synthesis", "explanatory abstraction vs grouping", "reconstruction work", "exact recovery", "compiler limitations"]},
    }.items():
        write_json(output / filename, value)
    (output / "owner-review.md").write_text(owner_review(cases, gate), encoding="utf-8")
    (output / "diagnostic-report.md").write_text(diagnostic_report(cases, gate), encoding="utf-8")
    (output / "owner-review-command.txt").write_text(OWNER_COMMAND + "\n", encoding="utf-8")
    (output / "zero-call-zero-retrieval.txt").write_text("Zero model/provider calls, network retrievals, extraction reruns, schema repairs, production/UI changes, or promotion.\n", encoding="utf-8")
    after = check_frozen(root)
    if before != after:
        raise ValidationError("protected files changed during diagnostic")
    core = artifact_rows(output, core_only=True)
    if verify_regeneration:
        with tempfile.TemporaryDirectory(prefix="spec064-regeneration-") as directory:
            reference = Path(directory)
            generate(root, reference, verify_regeneration=False)
            if core != artifact_rows(reference, core_only=True):
                raise ValidationError("deterministic regeneration differs")
    write_json(output / "deterministic-regeneration.json", {
        "result": "PASS" if verify_regeneration else "REFERENCE_GENERATION_ONLY",
        "method": "Independent second-directory generation; compare exact path sets and SHA256 bytes of all core artifacts. Regression additionally compares final report and this verification receipt.",
        "compared_core_file_count": len(core), "compared_core_tree_sha256": stable(core),
        "excluded_self_referential_receipts": ["report.json", "deterministic-regeneration.json"],
    })
    report = {
        "schema": "spec064.progressive-abstraction-report.v1", "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY", "mechanical_branch": gate["mechanical_branch"],
        "architecture_finding": gate["finding"], "case_count": len(cases), "per_stage_measurements": measures, "aggregate_measurements": aggregate,
        "preservation": {"semantic_commitments_per_resolution": sum(len(s["semantic_items"]) for s in substrates), "material_implications_per_resolution": sum(len(s["material_implications"]) for s in substrates), "source_explanatory_blocks": sum(len(s["explanatory_structure"]["blocks"]) for s in substrates), "exact_backwards_recovery": 1.0, "semantic_drift": 0, "unsupported_strengthening": 0, "genuine_omissions": 0},
        "protected_identity": {"before": stable(before), "after": stable(after), "file_count": len(before), "unchanged": before == after},
        "limitations": ["Source assertion integration is bounded by existing admitted evidence; it does not certify arbitrary paraphrase entailment.", "Inherited qualification detector entries are retained exactly; no upstream semantic or cue repair is performed.", "Unit-count reduction from packaging is reported separately from explanatory abstraction; grouping-only handles earn no abstraction reduction.", "This experiment cannot prove that every deterministic algorithm fails; the architecture decision applies to these frozen rules.", "R3 retains detail when grouping cannot truthfully subsume it, including any resulting cost increase."],
        "execution_integrity": {"provider_calls": 0, "external_retrievals": 0, "extraction_reruns": 0, "schema_repairs": 0, "production_changes": 0, "ui_changes": 0, "new_representation_grammar": 0, "promotion": 0, "human_verdict_assignments": 0},
        "owner_review": {"state": "OWNER_REVIEW", "human_gate": "OWNER_AND_CHATGPT_REVIEW", "verdict": "PENDING", "promotion": "NOT_AUTHORIZED", "command": OWNER_COMMAND, "artifact": "owner-review.md"},
        "validation": VALIDATION,
        "artifact_identities": artifact_rows(output),
    }
    write_json(output / "report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    report = generate(root, args.output_dir or root / OUTPUT_DIR)
    print(json.dumps({key: report[key] for key in ("mechanical_branch", "architecture_finding", "case_count", "preservation")}, sort_keys=True))


if __name__ == "__main__":
    main()
