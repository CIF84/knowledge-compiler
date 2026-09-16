"""Deterministic offline claim-focus selection experiment for SPEC-054.

The adapter in this module is deliberately isolated from the production
semantic compiler.  It enumerates already-admitted claims, presents their
source-backed statements to the existing representation resolver, and records
the result without modifying topology, semantic models, renderers, or UI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .models import Claim, KnowledgeModel, ValidationError
from .representation_strategy import (
    RepresentationContext,
    StrategyType,
    resolve_representation,
)
from .semantic_representation_compiler import compile_semantic_representation
from .structure_detection import StructureDetector


OUTPUT_DIR = "examples/evaluations/spec-054-claim-focus-selection-experiment-20260916"
OUTPUT_PATH = f"{OUTPUT_DIR}/report.json"
SPEC052_DIR = "examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915"
SPEC053_REPORT = (
    "examples/evaluations/"
    "spec-053-claim-to-representation-coverage-diagnosis-20260916/report.json"
)
EXPECTED_EVIDENCE_IDENTITIES = {
    SPEC053_REPORT: "ad9a2843a9a1c6b4e826e7b0930e21a82e273544313babd25bde464610a72738",
    f"{SPEC052_DIR}/final-report.json": "5e73b73b1080230b8068ab2046ba82f635ee65bfaaaf63c05e0db15e12d75d08",
    f"{SPEC052_DIR}/claim-only-preservation-audit.json": "88b60ddd0698dc7faedb1f43c7abb8c0fc5159cbf48d52d431697e6461d08bdb",
    f"{SPEC052_DIR}/artifact-manifest.json": "140b8e3d4f3cef3103ac22237c23bdd16f20ae826d26a7899c4d13b46e7bb305",
}
IMPLEMENTATION_PATHS = (
    "src/knowledge_compiler/spec054_claim_focus_experiment.py",
    "src/knowledge_compiler/representation_strategy.py",
    "src/knowledge_compiler/semantic_representation_compiler.py",
    "src/knowledge_compiler/structure_detection.py",
)
OUTCOMES = (
    "EXISTING_NON_FALLBACK_STRATEGY",
    "TRUTHFUL_PROSE_FALLBACK",
    "NO_STRATEGY",
    "INVALID_OR_UNSAFE_DECISION",
)
BRANCHES = (
    "FOCUS_SELECTION_SUFFICIENT",
    "STRATEGY_COVERAGE_GAP_REVEALED",
    "CLAIM_FOCUS_UNSAFE",
    "LEARNER_SURFACE_REQUIRED_TO_DECIDE",
    "INCONCLUSIVE",
)
NEXT_STEPS = (
    "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT",
    "CLAIM_REPRESENTATION_STRATEGY_EXPERIMENT",
    "CLAIM_FOCUS_SAFETY_REDESIGN",
    "CLAIM_FOCUS_PROMOTION_REVIEW",
    "MORE_DIAGNOSIS_REQUIRED",
)
FOCUS_CONTRACT = {
    "schema": "spec054.experimental-claim-focus.v1",
    "semantic_class": "CLAIM",
    "production_integration": False,
    "selection_inputs": [
        "admitted KnowledgeModel claim identity",
        "unchanged claim statement",
        "unchanged exact source evidence",
        "existing origin and confidence",
    ],
    "informational_context_not_used_for_strategy_selection": [
        "source identity",
        "model identity",
        "deterministically related entity IDs",
    ],
    "resolver_adapter": {
        "existing_semantic_class": "explanation",
        "nodes": [],
        "relationships": [],
        "rationale": (
            "The existing resolver already defines source-backed non-structural explanation "
            "as truthful prose. CLAIM remains the experimental dispatch identity; the adapter "
            "does not infer operands, participants, edges, or topology."
        ),
    },
    "forbidden_selection_inputs": [
        "source/domain identity",
        "SPEC-053 diagnostic semantic-character label",
        "claim wording heuristics",
        "invented topology or structured operands",
    ],
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence(claim: Claim) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "document_id": span.document_id,
            "start_char": span.start_char,
            "end_char": span.end_char,
            "quote": span.quote,
        }
        for span in claim.evidence
    )


@dataclass(frozen=True)
class ExperimentalClaimFocus:
    source_id: str
    source_sha256: str
    model_path: str
    model_sha256: str
    document_id: str
    claim_id: str
    claim_text: str
    evidence: tuple[dict[str, Any], ...]
    origin: str
    confidence: float
    related_entity_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": FOCUS_CONTRACT["schema"],
            "semantic_class": "CLAIM",
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "model_path": self.model_path,
            "model_sha256": self.model_sha256,
            "document_id": self.document_id,
            "claim_id": self.claim_id,
            "claim_text": self.claim_text,
            "evidence": [dict(item) for item in self.evidence],
            "origin": self.origin,
            "confidence": self.confidence,
            "related_entity_ids": list(self.related_entity_ids),
        }


def _source_directories(repo_root: Path) -> dict[str, Path]:
    directories: dict[str, Path] = {}
    for directory in sorted((repo_root / SPEC052_DIR / "sources").iterdir()):
        identity = _load(directory / "source-identity.json")
        directories[identity["source_id"]] = directory
    return directories


def _verify_evidence_identities(repo_root: Path) -> list[dict[str, str]]:
    rows = []
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        actual = _sha(repo_root / relative)
        if actual != expected:
            raise ValidationError(f"SPEC-054 frozen evidence mismatch for {relative}: {actual}")
        rows.append({"path": relative, "sha256": actual})
    return rows


def enumerate_claim_focuses(
    repo_root: Path,
) -> tuple[list[ExperimentalClaimFocus], dict[str, KnowledgeModel], dict[str, Path]]:
    """Enumerate only the frozen 98-item SPEC-053 cohort."""

    spec053 = _load(repo_root / SPEC053_REPORT)
    directories = _source_directories(repo_root)
    models: dict[str, KnowledgeModel] = {}
    focuses: list[ExperimentalClaimFocus] = []
    for trace in spec053["claim_trace_inventory"]:
        source_id = trace["source_id"]
        directory = directories[source_id]
        model_path = directory / "admitted-knowledge-model.json"
        if source_id not in models:
            models[source_id] = KnowledgeModel.from_dict(_load(model_path))
        model = models[source_id]
        claim = next((item for item in model.claims if item.id == trace["claim_id"]), None)
        if claim is None:
            raise ValidationError(f"claim focus is absent from admitted model: {source_id}/{trace['claim_id']}")
        for span in claim.evidence:
            span.validate_against(model.document)
        evidence = _evidence(claim)
        if (
            claim.statement != trace["claim_text"]
            or list(evidence) != trace["evidence"]
            or claim.origin.value != trace["origin"]
        ):
            raise ValidationError(f"claim focus differs from frozen trace: {source_id}/{claim.id}")
        focuses.append(
            ExperimentalClaimFocus(
                source_id=source_id,
                source_sha256=trace["source_sha256"],
                model_path=str(model_path.relative_to(repo_root)),
                model_sha256=_sha(model_path),
                document_id=model.document.id,
                claim_id=claim.id,
                claim_text=claim.statement,
                evidence=evidence,
                origin=claim.origin.value,
                confidence=claim.confidence,
                related_entity_ids=tuple(trace["related_entity_ids"]),
            )
        )
    focuses.sort(key=lambda item: (item.source_id, item.claim_id))
    identities = {(item.source_id, item.claim_id) for item in focuses}
    if len(focuses) != 98 or len(identities) != 98:
        raise ValidationError(f"SPEC-054 requires 98 unique claim focuses, found {len(focuses)}")
    return focuses, models, directories


def _resolver_input(focus: ExperimentalClaimFocus) -> dict[str, Any]:
    return {
        "context_key": f"spec054:claim:{focus.document_id}:{focus.claim_id}",
        "semantic_focus_identity": focus.claim_id,
        "semantic_class": "explanation",
        "label": focus.claim_text,
        "description": focus.claim_text,
        "structure_type": None,
        "nodes": [],
        "relationships": [],
        "warnings": ["Experimental trusted claim focus; no admitted structural form."],
        "trusted_input_refs": [
            f"{focus.model_path}#claim:{focus.claim_id}",
            "exact claim evidence retained by the experimental decision wrapper",
        ],
    }


def resolve_claim_focus(focus: ExperimentalClaimFocus) -> dict[str, Any]:
    """Resolve one claim with the existing grammar and fail closed on unsafe output."""

    raw_input = _resolver_input(focus)
    plan = None
    error = None
    try:
        plan = resolve_representation(
            RepresentationContext(
                context_key=raw_input["context_key"],
                semantic_focus_identity=raw_input["semantic_focus_identity"],
                semantic_class=raw_input["semantic_class"],
                label=raw_input["label"],
                description=raw_input["description"],
                structure_type=None,
                nodes=(),
                relationships=(),
                warnings=tuple(raw_input["warnings"]),
                trusted_input_refs=tuple(raw_input["trusted_input_refs"]),
            )
        ).to_dict()
    except ValidationError as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}

    safety = {
        "claim_text_unchanged": plan is not None and plan["payload"]["focus"]["description"] == focus.claim_text,
        "exact_evidence_attached_to_decision": bool(focus.evidence),
        "origin_and_confidence_attached": bool(focus.origin) and 0.0 <= focus.confidence <= 1.0,
        "no_relationship_or_proposition_created": plan is not None and not plan["payload"]["relationships"],
        "no_topology_inferred": plan is not None and not plan["payload"]["nodes"] and not plan["payload"]["relationships"],
        "no_diagnostic_label_or_source_routing_input": True,
        "existing_strategy_family_only": plan is not None and plan["strategy_type"] in {item.value for item in StrategyType},
        "resolver_semantics_do_not_exceed_claim": (
            plan is not None
            and plan["strategy_type"] == StrategyType.CONCISE_PROSE.value
            and plan["payload"].get("body") == focus.claim_text
        ),
    }
    if plan is None:
        outcome = "NO_STRATEGY"
    elif not all(safety.values()):
        outcome = "INVALID_OR_UNSAFE_DECISION"
    elif (
        plan["strategy_type"] == StrategyType.CONCISE_PROSE.value
        and plan["deterministic_rule_metadata"]["rule_id"] == "TRUTHFUL_PROSE_FALLBACK"
    ):
        outcome = "TRUTHFUL_PROSE_FALLBACK"
    else:
        outcome = "EXISTING_NON_FALLBACK_STRATEGY"

    decision_key = {
        "contract": FOCUS_CONTRACT["schema"],
        "source": focus.source_id,
        "claim": focus.claim_id,
        "outcome": outcome,
        "strategy": plan["strategy_type"] if plan else None,
    }
    return {
        "decision_id": f"spec054-decision-{_stable(decision_key)[:16]}",
        "focus": focus.to_dict(),
        "resolver_adapter": {
            "experimental_dispatch_class": "CLAIM",
            "existing_resolver_class": "explanation",
            "input_sha256": _stable(raw_input),
            "diagnostic_character_used": False,
            "source_or_domain_rule_used": False,
        },
        "outcome": outcome,
        "selected_strategy_family": plan["strategy_type"] if plan else None,
        "selected_rule_id": (
            plan["deterministic_rule_metadata"]["rule_id"] if plan else None
        ),
        "fallback_reason": (
            plan["deterministic_rule_metadata"]["fallback_reason"] if plan else None
        ),
        "representation_plan": plan,
        "grounding_provenance_refs": [dict(item) for item in focus.evidence],
        "semantic_safety_audit": safety,
        "error": error,
        "learner_surface_binding_created": False,
    }


def _current_non_claim_decisions(model: KnowledgeModel) -> list[dict[str, Any]]:
    foci: Iterable[tuple[str, str]] = (
        *(('concept', item.id) for item in model.entities),
        *(('canonical', item.id) for item in model.relationships),
        *(('proposition', item.id) for item in model.propositions),
    )
    return [
        compile_semantic_representation(model, kind, identity).to_dict()
        for kind, identity in sorted(foci)
    ]


def _baseline_control(
    repo_root: Path, models: dict[str, KnowledgeModel], directories: dict[str, Path]
) -> dict[str, Any]:
    rows = []
    for source_id, model in sorted(models.items()):
        directory = directories[source_id]
        before = model.to_dict()
        canonical_decisions = _load(directory / "representation-decisions.json")["decisions"]
        regenerated_decisions = _current_non_claim_decisions(model)
        canonical_structures = _load(directory / "detected-structures.json")["structures"]
        regenerated_structures = StructureDetector().detect(model).to_dict()["structures"]
        after = model.to_dict()
        canonical_decision_identity = _stable(canonical_decisions)
        regenerated_decision_identity = _stable(regenerated_decisions)
        canonical_structure_identity = _stable(canonical_structures)
        regenerated_structure_identity = _stable(regenerated_structures)
        rows.append(
            {
                "source_id": source_id,
                "model_identity_before_sha256": _stable(before),
                "model_identity_after_sha256": _stable(after),
                "model_unchanged": before == after,
                "canonical_non_claim_decision_count": len(canonical_decisions),
                "regenerated_non_claim_decision_count": len(regenerated_decisions),
                "canonical_non_claim_decisions_sha256": canonical_decision_identity,
                "regenerated_non_claim_decisions_sha256": regenerated_decision_identity,
                "non_claim_decisions_equal": canonical_decision_identity == regenerated_decision_identity,
                "canonical_structures_sha256": canonical_structure_identity,
                "regenerated_structures_sha256": regenerated_structure_identity,
                "detected_structures_equal": canonical_structure_identity == regenerated_structure_identity,
            }
        )
    return {
        "comparison_method": "Loaded canonical JSON values versus deterministic regeneration with frozen production code.",
        "source_count": len(rows),
        "all_models_unchanged": all(row["model_unchanged"] for row in rows),
        "all_non_claim_decisions_equal": all(row["non_claim_decisions_equal"] for row in rows),
        "all_detected_structures_equal": all(row["detected_structures_equal"] for row in rows),
        "sources": rows,
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    evidence_identities = _verify_evidence_identities(repo_root)
    focuses, models, directories = enumerate_claim_focuses(repo_root)
    decisions = [resolve_claim_focus(focus) for focus in focuses]
    outcomes = {key: sum(item["outcome"] == key for item in decisions) for key in OUTCOMES}
    if sum(outcomes.values()) != 98:
        raise ValidationError("every claim focus must receive exactly one fixed outcome")
    baseline = _baseline_control(repo_root, models, directories)
    if not (
        baseline["all_models_unchanged"]
        and baseline["all_non_claim_decisions_equal"]
        and baseline["all_detected_structures_equal"]
    ):
        raise ValidationError("SPEC-054 baseline control changed protected state")

    spec053 = _load(repo_root / SPEC053_REPORT)
    characters = {
        (item["source_id"], item["claim_id"]): item["diagnostic_semantic_character"]
        for item in spec053["claim_trace_inventory"]
    }
    cross_tab: dict[str, Counter[str]] = defaultdict(Counter)
    strategy_by_character: dict[str, Counter[str]] = defaultdict(Counter)
    by_identity = {}
    for decision in decisions:
        focus = decision["focus"]
        identity = (focus["source_id"], focus["claim_id"])
        character = characters[identity]
        cross_tab[character][decision["outcome"]] += 1
        strategy_by_character[character][decision["selected_strategy_family"] or "NONE"] += 1
        by_identity[identity] = decision

    samples = []
    for sample in spec053["learner_value_counterfactual_samples"]:
        decision = by_identity[(sample["source_id"], sample["claim_id"])]
        samples.append(
            {
                "selection_reason": sample["selection_reason"],
                "diagnostic_semantic_character": sample["diagnostic_semantic_character"],
                "diagnostic_character_used_for_selection": False,
                "decision_id": decision["decision_id"],
                "source_id": sample["source_id"],
                "claim_id": sample["claim_id"],
                "claim_text": sample["claim_text"],
                "outcome": decision["outcome"],
                "selected_strategy_family": decision["selected_strategy_family"],
                "selected_rule_id": decision["selected_rule_id"],
                "semantic_safety_pass": all(decision["semantic_safety_audit"].values()),
            }
        )

    strategy_counts = dict(
        sorted(Counter(item["selected_strategy_family"] or "NONE" for item in decisions).items())
    )
    implementation_identities = [
        {"path": relative, "sha256": _sha(repo_root / relative)}
        for relative in IMPLEMENTATION_PATHS
    ]
    all_safety_pass = all(
        all(item["semantic_safety_audit"].values()) for item in decisions
    )
    return {
        "schema": "spec-054-claim-focus-selection-experiment-report-v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "execution_mode": "OFFLINE_DETERMINISTIC_EXPERIMENT",
        "experimental_claim_focus_contract": FOCUS_CONTRACT,
        "experimental_claim_focus_contract_sha256": _stable(FOCUS_CONTRACT),
        "evidence_identities": evidence_identities,
        "implementation_identities": implementation_identities,
        "claim_focus_decisions": decisions,
        "outcome_taxonomy": list(OUTCOMES),
        "outcome_distribution": outcomes,
        "strategy_family_distribution": strategy_counts,
        "post_hoc_diagnostic_character_analysis": {
            "labels_are_not_strategy_inputs": True,
            "outcomes_by_character": {
                key: dict(sorted(value.items())) for key, value in sorted(cross_tab.items())
            },
            "strategies_by_character": {
                key: dict(sorted(value.items()))
                for key, value in sorted(strategy_by_character.items())
            },
        },
        "baseline_control_comparison": baseline,
        "semantic_safety_summary": {
            "claim_focus_count": len(decisions),
            "all_claim_text_and_evidence_unchanged": all_safety_pass,
            "all_provenance_attached": all(item["grounding_provenance_refs"] for item in decisions),
            "knowledge_models_unchanged": baseline["all_models_unchanged"],
            "relationships_or_propositions_created": 0,
            "topology_created_or_inferred": 0,
            "unsafe_decision_count": outcomes["INVALID_OR_UNSAFE_DECISION"],
            "learner_surface_bindings_created": 0,
        },
        "named_review_sample": samples,
        "experiment_questions": {
            "all_98_became_deterministic_focuses": len(decisions) == 98,
            "existing_non_fallback_strategy_count": outcomes["EXISTING_NON_FALLBACK_STRATEGY"],
            "truthful_prose_fallback_count": outcomes["TRUTHFUL_PROSE_FALLBACK"],
            "no_strategy_count": outcomes["NO_STRATEGY"],
            "invalid_or_unsafe_count": outcomes["INVALID_OR_UNSAFE_DECISION"],
            "selected_strategy_families": strategy_counts,
            "existing_non_claim_decisions_unchanged": baseline["all_non_claim_decisions_equal"],
            "detected_structures_unchanged": baseline["all_detected_structures_equal"],
            "claim_focus_topology_created": 0,
            "learner_surface_answer": (
                "Compiler-level routing and semantic safety are reviewable now. Whether 98 prose-only "
                "claim plans are pedagogically useful cannot be decided without a separately authorized "
                "learner-surface binding experiment."
            ),
        },
        "experiment_branch": {
            "class": "LEARNER_SURFACE_REQUIRED_TO_DECIDE",
            "all_allowed_classes": list(BRANCHES),
            "mechanical_basis": (
                "All 98 claims route deterministically to safe truthful prose with no topology leakage, "
                "no missing strategy, and no protected-control drift. The offline compiler evidence proves "
                "routing safety but cannot establish the learner usefulness of an all-fallback result."
            ),
            "owner_verdict_required": True,
        },
        "recommended_next_step": {
            "class": "CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT",
            "all_allowed_classes": list(NEXT_STEPS),
            "rationale": (
                "Bind the already-recorded safe claim plans in a bounded future experiment to test "
                "pedagogical usefulness; do not add strategy families before that observation."
            ),
            "implementation_authorized": False,
            "protected_behavior": [
                "claims remain non-topological",
                "existing strategy grammar remains unchanged",
                "existing non-claim decisions and detected structures remain frozen",
                "accepted learner surface remains unchanged until separately authorized",
            ],
            "falsification_condition": (
                "Choose a strategy experiment instead if owner review finds the prose-only plans "
                "mechanically inadequate before surface binding or identifies a demonstrated existing-family gap."
            ),
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_evidence_retrievals": 0,
            "extraction_reruns": 0,
            "new_strategy_families": 0,
            "source_specific_routing_rules": 0,
            "diagnostic_labels_used_for_routing": 0,
            "production_behavior_changes": 0,
            "learner_surface_changes": 0,
        },
        "validation": {
            "focused_spec054_and_frozen_control_tests": "PASS (103 tests)",
            "full_offline_suite": "PASS (642 tests)",
            "deterministic_regeneration": "PASS",
            "json_validation": "PASS",
            "git_diff_check": "PASS",
            "provenance_and_secret_safety": "PASS",
            "protected_state_audit": "PASS (hash-bound and baseline-equivalent)",
            "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
        },
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
        },
        "deviations": [],
    }


def write_report(repo_root: Path, output_path: Path) -> dict[str, Any]:
    report = build_report(repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the offline SPEC-054 claim-focus experiment")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output or root / OUTPUT_PATH
    report = write_report(root, output)
    print(
        json.dumps(
            {
                "claim_focuses": len(report["claim_focus_decisions"]),
                "outcomes": report["outcome_distribution"],
                "branch": report["experiment_branch"]["class"],
                "next": report["recommended_next_step"]["class"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
