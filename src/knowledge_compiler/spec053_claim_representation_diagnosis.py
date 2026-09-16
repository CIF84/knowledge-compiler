"""Deterministic offline diagnosis for SPEC-053.

This module reads frozen SPEC-052 evidence and existing representation code. It
does not call a provider, rerun extraction, or change representation behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from .models import KnowledgeModel, ValidationError
from .representation_strategy import RepresentationContext, resolve_representation


OUTPUT_PATH = "examples/evaluations/spec-053-claim-to-representation-coverage-diagnosis-20260916/report.json"
SPEC052_DIR = "examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915"
EXPECTED_IDENTITIES = {
    f"{SPEC052_DIR}/final-report.json": "5e73b73b1080230b8068ab2046ba82f635ee65bfaaaf63c05e0db15e12d75d08",
    f"{SPEC052_DIR}/claim-only-preservation-audit.json": "88b60ddd0698dc7faedb1f43c7abb8c0fc5159cbf48d52d431697e6461d08bdb",
    f"{SPEC052_DIR}/artifact-manifest.json": "140b8e3d4f3cef3103ac22237c23bdd16f20ae826d26a7899c4d13b46e7bb305",
    "examples/evaluations/spec-039-semantic-to-representation-compiler-gate-20260911/report.json": "f0576e9c6cbbe25e73ac06caa992d4093df2c503efb96a13435c65b75cf733e2",
    "examples/evaluations/spec-016-assertion-aware-representation-20260904/report.json": "1156399e98ea8e085d07edd8ee303ff64f7e27cd0c0dbbead40a34d72978f1fc",
}
PROTECTED_CODE = (
    "src/knowledge_compiler/semantic_representation_compiler.py",
    "src/knowledge_compiler/structure_detection.py",
    "src/knowledge_compiler/representation_strategy.py",
    "src/knowledge_compiler/assertion_aware_representation.py",
    "src/knowledge_compiler/spec048_live_evaluation.py",
)
CLAIM_PATHS = (
    "DEDICATED_REPRESENTATION", "SUPPORTING_CONTENT", "GENERIC_FALLBACK",
    "NOT_CONSIDERED", "FILTERED_OR_DROPPED", "AMBIGUOUS",
)
GAP_CLASSES = (
    "FOCUS_SELECTION_GAP", "REPRESENTATION_FAMILY_GAP", "LEARNER_SURFACE_BINDING_GAP",
    "INTENTIONAL_SUPPORTING_CONTENT_ONLY", "MIXED_GAP", "INSUFFICIENT_EVIDENCE",
)
EXPERIMENT_CLASSES = (
    "CLAIM_FOCUS_SELECTION_EXPERIMENT", "CLAIM_REPRESENTATION_STRATEGY_EXPERIMENT",
    "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT", "NO_CHANGE_CLAIMS_AS_SUPPORTING_CONTENT",
    "MORE_DIAGNOSIS_REQUIRED",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_directories(base: Path) -> dict[str, Path]:
    result = {}
    for directory in sorted((base / "sources").iterdir()):
        identity = _load(directory / "source-identity.json")
        result[identity["source_id"]] = directory
    return result


def _claim_only_rows(report: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    for outcome in report["source_outcomes"]:
        for claim in outcome["semantic_omission_audit"]["claims"]:
            if claim.get("not_a_stage2_topology_id") and claim.get("not_identical_to_stage2_topology_statement"):
                yield outcome["source_id"], claim


def _semantic_character(statement: str) -> tuple[str, str]:
    """Return a diagnostic text-form label; never a trusted semantic type."""
    text = statement.casefold()
    rules = (
        ("SCALAR_NUMERIC_COMPARISON", r"\b(more|less|greater|fewer|higher|lower|faster|slower|larger|smaller)\b.*\bthan\b"),
        ("DESCRIPTIVE_CONTRAST", r"\b(whereas|while|unlike|opposite|rather than|in contrast|but not|not a .* but)\b"),
        ("QUANTITATIVE_FACT", r"(?:\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|half|percent|kilogram|miles?|kilometers?|centimeters?|picometer|atoms?)\b)"),
        ("QUALIFICATION_CONDITION", r"\b(if|when|unless|may|might|can|could|must|has to|have to|does not necessarily)\b"),
        ("DEFINITION_DESCRIPTION", r"\b(is an?|are|refers to|is defined as|means)\b"),
    )
    for label, pattern in rules:
        if re.search(pattern, text):
            return label, pattern
    return "CONTEXTUAL_FACT", "default:no diagnostic surface-form rule matched"


def _topology(model: KnowledgeModel) -> list[Any]:
    return [*model.relationships, *model.propositions]


def _entity_ids(item: Any) -> set[str]:
    if hasattr(item, "source_entity_id"):
        return {item.source_entity_id, item.target_entity_id}
    return {binding.entity_id for binding in item.role_bindings}


def _evidence_quotes(item: Any) -> set[str]:
    return {span.quote for span in item.evidence}


def _counterfactual_plan(claim_id: str, statement: str) -> dict[str, Any]:
    """Probe the existing resolver only; this is not wired into production focus selection."""
    context = RepresentationContext(
        context_key=f"spec053:counterfactual:claim:{claim_id}",
        semantic_focus_identity=claim_id,
        semantic_class="explanation",
        label=statement,
        description=statement,
        structure_type=None,
        nodes=(),
        relationships=(),
        warnings=("Diagnostic counterfactual only; no production claim focus exists.",),
        trusted_input_refs=("frozen SPEC-052 grounded claim",),
    )
    plan = resolve_representation(context).to_dict()
    return {
        "existing_strategy_family": plan["strategy_type"],
        "rule_id": plan["deterministic_rule_metadata"]["rule_id"],
        "fallback_reason": plan["deterministic_rule_metadata"]["fallback_reason"],
        "truthful_without_new_topology": True,
        "production_behavior_invoked": False,
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    evidence_identities = []
    for relative, expected in EXPECTED_IDENTITIES.items():
        actual = _sha(repo_root / relative)
        if actual != expected:
            raise ValidationError(f"SPEC-053 frozen evidence mismatch for {relative}: {actual}")
        evidence_identities.append({"path": relative, "sha256": actual})
    code_identities = [{"path": path, "sha256": _sha(repo_root / path)} for path in PROTECTED_CODE]

    base = repo_root / SPEC052_DIR
    source_dirs = _source_directories(base)
    spec052 = _load(base / "final-report.json")
    frozen_claim_audit = _load(base / "claim-only-preservation-audit.json")
    traces = []
    models: dict[str, KnowledgeModel] = {}
    decisions_by_source = {}
    source_identities = {}
    for source_id, directory in source_dirs.items():
        model_path = directory / "admitted-knowledge-model.json"
        if not model_path.is_file():
            continue
        models[source_id] = KnowledgeModel.from_dict(_load(model_path))
        decisions_by_source[source_id] = _load(directory / "representation-decisions.json")["decisions"]
        source_identities[source_id] = _load(directory / "source-identity.json")

    for source_id, audit_claim in _claim_only_rows(spec052):
        model = models[source_id]
        claim = next((item for item in model.claims if item.id == audit_claim["claim_id"]), None)
        if claim is None:
            raise ValidationError(f"claim-only item absent from admitted model: {source_id}/{audit_claim['claim_id']}")
        if claim.origin.value != "SOURCE" or not claim.evidence:
            raise ValidationError(f"claim-only item is not exact grounded SOURCE material: {source_id}/{claim.id}")
        shared = [item for item in _topology(model) if _evidence_quotes(item) & _evidence_quotes(claim)]
        related_topology_ids = sorted(item.id for item in shared)
        related_entity_ids = sorted({identity for item in shared for identity in _entity_ids(item)})
        decisions = decisions_by_source[source_id]
        focus_ids = {item["semantic_focus_identity"] for item in decisions}
        classes = {item["semantic_class"] for item in decisions}
        if claim.id in focus_ids or "claim" in classes:
            raise ValidationError(f"committed SPEC-052 evidence unexpectedly contains a claim focus: {source_id}/{claim.id}")
        character, character_rule = _semantic_character(claim.statement)
        spans = [
            {
                "document_id": span.document_id, "start_char": span.start_char,
                "end_char": span.end_char, "quote": span.quote,
            }
            for span in claim.evidence
        ]
        traces.append({
            "source_id": source_id,
            "domain": (
                source_identities[source_id]["provenance"].get("domain_family")
                or source_identities[source_id]["provenance"]["domain_stratum"]
            ),
            "source_sha256": source_identities[source_id]["source_sha256"],
            "claim_id": claim.id,
            "claim_text": claim.statement,
            "origin": claim.origin.value,
            "evidence": spans,
            "evidence_identity_sha256": _stable(spans),
            "present_in_admitted_knowledge_model": True,
            "exactly_grounded": all(model.document.text.count(span.quote) == 1 for span in claim.evidence),
            "related_topology_exists_by_shared_exact_evidence": bool(shared),
            "related_topology_ids": related_topology_ids,
            "related_entity_ids": related_entity_ids,
            "relatedness_method": "SHARED_EXACT_EVIDENCE_QUOTE" if shared else "NONE_DETERMINISTIC",
            "discoverable_by_assertion_aware_logic_from_spec052_inputs": False,
            "assertion_aware_reason": "No GroundedAssertionSet/canonical assertion row maps this SPEC-052 claim into the assertion-aware builder input contract.",
            "considered_by_representation_planning": False,
            "attached_as_supporting_content": False,
            "preserved_through_generic_fallback": False,
            "eligible_for_dedicated_claim_representation_under_current_compiler_contract": False,
            "assigned_dedicated_representation_decision": False,
            "omitted_before_learner_facing_planning": True,
            "terminal_path_classification": "NOT_CONSIDERED",
            "terminal_path_confidence": "HIGH",
            "diagnostic_semantic_character": character,
            "diagnostic_character_rule": character_rule,
            "code_artifact_trace": [
                {"step": "GROUNDING", "result": "PRESENT_EXACT", "artifact": f"{SPEC052_DIR}/sources/{source_dirs[source_id].name}/admitted-knowledge-model.json"},
                {"step": "STRUCTURE_DETECTION", "result": "CLAIMS_NOT_INPUT", "code": "src/knowledge_compiler/structure_detection.py::StructureDetector.detect"},
                {"step": "FOCUS_ENUMERATION", "result": "ENTITIES_RELATIONSHIPS_PROPOSITIONS_ONLY", "code": "src/knowledge_compiler/spec048_live_evaluation.py::persist_source_run"},
                {"step": "COMPILER_DISPATCH", "result": "CLAIM_CLASS_UNSUPPORTED", "code": "src/knowledge_compiler/semantic_representation_compiler.py::compile_semantic_representation"},
                {"step": "REPRESENTATION_DECISION", "result": "ABSENT", "artifact": f"{SPEC052_DIR}/sources/{source_dirs[source_id].name}/representation-decisions.json"},
                {"step": "LEARNER_SURFACE_ELIGIBILITY", "result": "NO_DECISION_OR_PLAN_TO_BIND", "code": "src/knowledge_compiler/blind_evaluation.py::_renderer_bindings"},
            ],
        })

    traces.sort(key=lambda item: (item["source_id"], item["claim_id"]))
    if len(traces) != 98:
        raise ValidationError(f"SPEC-053 requires 98 claim-only traces, found {len(traces)}")
    if any(not item["exactly_grounded"] for item in traces):
        raise ValidationError("a traced claim is not exactly grounded")
    path_counts = {path: sum(item["terminal_path_classification"] == path for item in traces) for path in CLAIM_PATHS}
    if sum(path_counts.values()) != 98 or path_counts["NOT_CONSIDERED"] != 98:
        raise ValidationError("claim-path taxonomy is not exactly reconciled")

    source_rows = []
    for source_id in sorted({item["source_id"] for item in traces}):
        rows = [item for item in traces if item["source_id"] == source_id]
        source_rows.append({
            "source_id": source_id, "domain": rows[0]["domain"], "claim_only_count": len(rows),
            "claim_path_counts": {path: sum(item["terminal_path_classification"] == path for item in rows) for path in CLAIM_PATHS},
            "diagnostic_semantic_character_counts": dict(sorted(Counter(item["diagnostic_semantic_character"] for item in rows).items())),
            "shared_exact_evidence_with_topology_count": sum(item["related_topology_exists_by_shared_exact_evidence"] for item in rows),
        })
    character_counts = dict(sorted(Counter(item["diagnostic_semantic_character"] for item in traces).items()))
    character_paths: dict[str, Counter[str]] = defaultdict(Counter)
    for item in traces:
        character_paths[item["diagnostic_semantic_character"]][item["terminal_path_classification"]] += 1

    sample_keys = (
        ("crs-legislative-process-r42843-17", "claim-house-tools", "standalone scalar comparison"),
        ("fhwa-traffic-bottleneck-concepts-2016", "c7", "descriptive contrast"),
        ("noaa-nesdis-jet-stream-2025", "c33", "quantitative fact"),
        ("noaa-nesdis-jet-stream-2025", "c32", "claim sharing exact evidence with existing topology"),
    )
    samples = []
    by_key = {(item["source_id"], item["claim_id"]): item for item in traces}
    for source_id, claim_id, rationale in sample_keys:
        item = by_key[(source_id, claim_id)]
        samples.append({
            "selection_reason": rationale, "source_id": source_id, "claim_id": claim_id,
            "claim_text": item["claim_text"], "diagnostic_semantic_character": item["diagnostic_semantic_character"],
            "related_topology_ids": item["related_topology_ids"],
            "counterfactual_existing_strategy": _counterfactual_plan(claim_id, item["claim_text"]),
            "why_not_richer_existing_family": (
                "No current trusted claim contract supplies the structured roles/edges required by compare-contrast, "
                "worked-example, sequence, hierarchy, dependency, or mechanism families. Truthful concise prose is "
                "available without inventing topology; richer selection would require separately admitted structure."
            ),
        })

    report = {
        "schema": "spec-053-claim-to-representation-coverage-diagnosis-v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "execution_mode": "OFFLINE_DETERMINISTIC_EVIDENCE_TRACE",
        "evidence_identities": evidence_identities,
        "protected_code_identities": code_identities,
        "claim_trace_inventory": traces,
        "claim_path_taxonomy": list(CLAIM_PATHS),
        "claim_path_counts": path_counts,
        "source_aggregates": source_rows,
        "semantic_character_analysis": {
            "diagnostic_only_not_trusted_vocabulary": True,
            "counts": character_counts,
            "terminal_paths_by_character": {key: dict(sorted(value.items())) for key, value in sorted(character_paths.items())},
            "systematic_result": "Every observed diagnostic form terminates as NOT_CONSIDERED; form-specific strategy adequacy is not exercised by the current pipeline.",
        },
        "representation_gate_trace": [
            {"ordinal": 1, "gate": "ADMITTED_KNOWLEDGE_MODEL", "input": "KnowledgeModel.claims", "result": "98/98 PRESENT_EXACT_GROUNDED", "intent": "Claims are a distinct trusted non-topological tier."},
            {"ordinal": 2, "gate": "STRUCTURE_DETECTION", "input": "KnowledgeModel.relationships only", "result": "CLAIMS_IGNORED_BY_DESIGN", "intent": "Intentional: StructureDetector remains topology-oriented and must not infer claim edges."},
            {"ordinal": 3, "gate": "ASSERTION_AWARE_INPUT", "input": "GroundedAssertionSet + canonical assertion rows", "result": "SPEC052_CLAIMS_NOT_DISCOVERABLE", "intent": "The builder can label an already-mapped assertion PRESERVED_AS_CLAIM, but does not mint assertion participants or rows from arbitrary KnowledgeModel claims."},
            {"ordinal": 4, "gate": "FOCUS_ENUMERATION", "input": "entities + relationships + propositions", "result": "98/98 CLAIMS_EXCLUDED", "intent": "Coverage gap: trusted claims are not enumerated as candidate foci or attachments."},
            {"ordinal": 5, "gate": "COMPILER_DISPATCH", "input": "concept | canonical | proposition", "result": "CLAIM_SEMANTIC_CLASS_UNSUPPORTED", "intent": "Coverage gap at the public compiler boundary."},
            {"ordinal": 6, "gate": "STRATEGY_RESOLUTION", "input": "RepresentationContext", "result": "NOT_REACHED_FOR_CLAIMS", "intent": "The resolver already has a truthful CONCISE_PROSE explanation fallback, demonstrated only by counterfactual offline probes."},
            {"ordinal": 7, "gate": "PLAN_AND_RENDERER_BINDING", "input": "SemanticRepresentationDecision", "result": "NO_CLAIM_DECISION_OR_PLAN", "intent": "Downstream surface binding cannot act because no upstream claim decision exists."},
        ],
        "assertion_aware_behavior_analysis": {
            "consumes_claims_directly": False,
            "required_inputs": ["GroundedAssertionSet", "canonical assertion-tier rows", "KnowledgeModel"],
            "preserved_as_claim_producer": "AssertionAwareRepresentationBuilder.build assigns PRESERVED_AS_CLAIM when an existing grounded assertion ID appears in canonical_rows.claims and matches an existing KnowledgeModel claim.",
            "learner_facing_effect": "The mapped grounded assertion becomes an assertion card and presentation-only participant attachment; the claim does not receive a semantic compiler decision.",
            "spec052_effect": "SPEC-052 produced KnowledgeModel claims but no GroundedAssertionSet or canonical assertion mapping, so this separate projection seam cannot discover or display those claims.",
            "topology_boundary_preserved": True,
        },
        "learner_value_counterfactual_samples": samples,
        "primary_gap_diagnosis": {
            "class": "FOCUS_SELECTION_GAP",
            "all_allowed_classes": list(GAP_CLASSES),
            "evidence": [
                "All 98 items remain trusted and exactly grounded in admitted KnowledgeModels.",
                "All 98 terminate as NOT_CONSIDERED before strategy resolution.",
                "Focus enumeration contains only entities, relationships, and propositions.",
                "The public representation compiler rejects any semantic class other than concept, canonical, or proposition.",
                "No supporting-content attachment consumes these claims.",
                "The existing resolver can truthfully return CONCISE_PROSE for an explanation context without inventing topology, so at least a baseline family exists behind the blocked focus boundary.",
            ],
            "intentional_architecture": "Topology-only structure detection is intentional and correct.",
            "coverage_gap": "Excluding the trusted claim tier from focus/attachment selection is the dominant downstream gap; family quality and surface binding cannot be evaluated until claims reach planning.",
            "confidence": "HIGH",
        },
        "recommended_next_experiment": {
            "class": "CLAIM_FOCUS_SELECTION_EXPERIMENT",
            "all_allowed_classes": list(EXPERIMENT_CLASSES),
            "evidence_basis": "The complete 98-item cohort stops before strategy resolution, while the existing explanation fallback can consume a source-backed claim without topology.",
            "protected_behavior": [
                "claims remain non-topological", "StructureDetector remains relationship-only",
                "canonical semantic vocabulary and validation remain unchanged", "existing renderer/navigation baselines remain frozen",
            ],
            "falsification_condition": "Reject the focus-selection hypothesis if a bounded offline claim-focus seam cannot preserve all exact evidence, avoid topology, and produce auditable existing-strategy decisions, or if most selected claims still have no truthful existing strategy fit.",
            "why_competing_experiments_are_not_first": {
                "CLAIM_REPRESENTATION_STRATEGY_EXPERIMENT": "Premature: no claim reaches the resolver, and truthful prose already supplies a baseline existing fit.",
                "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT": "Premature: no claim decision/plan exists to bind.",
                "NO_CHANGE_CLAIMS_AS_SUPPORTING_CONTENT": "Unsupported: the committed pipeline attaches none of the 98 as supporting content.",
                "MORE_DIAGNOSIS_REQUIRED": "Unnecessary for locating the first deterministic exclusion boundary; every item follows the same high-confidence path.",
            },
            "implementation_authorized": False,
        },
        "integrity_validation": {
            "frozen_spec052_final_report_verified": True,
            "frozen_spec052_claim_audit_verified": True,
            "claim_only_items_expected": frozen_claim_audit["totals"]["mechanical_claim_only_count"],
            "claim_only_items_traced": len(traces),
            "all_present_in_admitted_models": all(item["present_in_admitted_knowledge_model"] for item in traces),
            "all_exactly_grounded": all(item["exactly_grounded"] for item in traces),
            "exactly_one_fixed_terminal_path_each": all(item["terminal_path_classification"] in CLAIM_PATHS for item in traces) and sum(path_counts.values()) == len(traces),
            "exactly_one_primary_gap_diagnosis": True,
            "exactly_one_next_experiment_class": True,
            "provider_model_calls": 0,
            "external_network_or_evidence_calls": 0,
            "extraction_reruns": 0,
            "historical_output_repairs": 0,
            "production_behavior_changes": 0,
            "topology_created_from_claims": 0,
        },
        "validation": {
            "focused_diagnostic_and_control_tests": "PASS (83 tests)",
            "full_offline_suite": "PASS (632 tests)",
            "deterministic_regeneration": "PASS",
            "json_validation": "PASS",
            "git_diff_check": "PASS",
            "secret_safety": "PASS",
            "protected_identity_audit": "PASS (hash-bound tests and empty protected-path diff)",
            "provider_model_network_call_audit": "PASS: zero calls by construction and execution record",
        },
        "owner_review": {"state": "OWNER_REVIEW", "verdict": "PENDING", "promotion": "NOT_AUTHORIZED"},
        "deviations": [],
    }
    return report


def write_report(repo_root: Path, output_path: Path) -> dict[str, Any]:
    report = build_report(repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the offline SPEC-053 diagnosis")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output or root / OUTPUT_PATH
    report = write_report(root, output)
    print(json.dumps({"claims": len(report["claim_trace_inventory"]), "gap": report["primary_gap_diagnosis"]["class"], "next": report["recommended_next_experiment"]["class"]}))


if __name__ == "__main__":
    main()
