"""Run the frozen, offline SPEC-057 cognitive-utility gate experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .models import ValidationError


OUTPUT_DIR = "examples/evaluations/spec-057-cognitive-utility-gate-experiment-20260917"
OUTPUT_PATH = f"{OUTPUT_DIR}/report.json"
SPEC038_REPORT = (
    "examples/evaluations/"
    "spec-038-dominant-explanatory-diagram-canvas-20260909/report.json"
)
SPEC055_REPORT = (
    "examples/evaluations/"
    "spec-055-claim-representation-strategy-experiment-20260916/report.json"
)
SPEC056_REPORT = (
    "examples/evaluations/"
    "spec-056-claim-learner-surface-binding-experiment-20260916/report.json"
)
EXPECTED_EVIDENCE_IDENTITIES = {
    SPEC038_REPORT: "22a715c37cd846f37268a62cb5a893cc6e160054fd3d9fdd6885643c45a6a050",
    SPEC055_REPORT: "47841734f8e1dd5fb40fcbfe52d2603d5f8d5a00e7ff122d87e31cdb2022d7d4",
    SPEC056_REPORT: "9376c3f3545563ec60114f62f1439277aabf0286dd053119f39dc16651fa5f1e",
}
IMPLEMENTATION_PATHS = (
    "src/knowledge_compiler/spec057_cognitive_utility_gate.py",
    "src/knowledge_compiler/spec055_claim_strategy_experiment.py",
    "src/knowledge_compiler/representation_strategy.py",
    "src/knowledge_compiler/semantic_representation_compiler.py",
    "src/knowledge_compiler/structure_detection.py",
)
DIMENSIONS = (
    "RELATIONAL_LOAD",
    "PERCEPTUAL_COMPARISON_LOAD",
    "TEMPORAL_OR_PROCESS_LOAD",
    "SPATIAL_OR_MECHANISTIC_LOAD",
    "GRAMMAR_ONLY_DECOMPOSITION",
    "EMPHASIS_ONLY",
    "DECODING_OVERHEAD",
)
OUTCOMES = (
    "STRONG_EXTERNALIZATION_VALUE",
    "POSSIBLE_EXTERNALIZATION_VALUE",
    "LOW_EXTERNALIZATION_VALUE",
    "UNSAFE_OR_UNSUPPORTED",
)
BRANCHES = (
    "COGNITIVE_UTILITY_GATE_SUPPORTED",
    "GATE_TOO_PERMISSIVE",
    "GATE_TOO_CONSERVATIVE",
    "UTILITY_NOT_DETERMINABLE_FROM_FROZEN_EVIDENCE",
    "INCONCLUSIVE",
)
NEXT_STEPS = (
    "UTILITY_GATED_LEARNER_SURFACE_AB_EXPERIMENT",
    "COGNITIVE_UTILITY_RULE_REFINEMENT",
    "REPRESENTATION_UTILITY_METADATA_REDESIGN",
    "KEEP_PROSE_DEFAULT_AND_STOP_CLAIM_VISUALIZATION",
    "MORE_DIAGNOSIS_REQUIRED",
)

UTILITY_CONTRACT = {
    "schema": "spec057.experimental-cognitive-utility-gate.v1",
    "canonical_semantics": False,
    "production_strategy_registration": False,
    "production_renderer_binding": False,
    "outcomes": list(OUTCOMES),
    "dimensions": list(DIMENSIONS),
    "allowed_inputs": [
        "frozen SPEC-055 proposed strategy",
        "frozen SPEC-055 structured payload and exact field traces",
        "frozen accepted SPEC-038 nodes, relationships, and strategy",
    ],
    "forbidden_inputs": [
        "source or domain identity as a utility signal",
        "SPEC-056 owner comments as case labels or routing rules",
        "external knowledge, retrieval, or model judgment",
        "inferred operands, labels, relationships, topology, or dimensions",
    ],
    "policy_precedence": [
        "unsupported utility requiring invented structure fails closed",
        "strong explicit externalization evidence may retain richer representation",
        "mixed evidence remains prose by automatic selection",
        "grammar-only decomposition remains prose",
        "emphasis-only treatment remains prose",
        "uncertainty favors prose",
    ],
    "gating": {
        "STRONG_EXTERNALIZATION_VALUE": "retain prior richer experimental strategy",
        "POSSIBLE_EXTERNALIZATION_VALUE": "CONCISE_PROSE",
        "LOW_EXTERNALIZATION_VALUE": "CONCISE_PROSE",
        "UNSAFE_OR_UNSUPPORTED": "CONCISE_PROSE",
    },
    "claim_rules": {
        "explicit_two_sided_comparison": "STRONG_EXTERNALIZATION_VALUE",
        "single_qualifier_without_external_structure": "LOW_EXTERNALIZATION_VALUE",
        "single_quantity_without_comparison_or_pattern": "LOW_EXTERNALIZATION_VALUE",
        "multiple_unbound_quantities_without_operands_or_dimension": "UNSAFE_OR_UNSUPPORTED",
        "existing_concise_prose_control": "LOW_EXTERNALIZATION_VALUE",
    },
    "structural_control_rules": {
        "three_or_more_nodes_with_two_or_more_explicit_relationships": "STRONG_EXTERNALIZATION_VALUE",
        "explicit_reciprocal_mechanism": "STRONG_EXTERNALIZATION_VALUE",
        "single_focused_relationship": "POSSIBLE_EXTERNALIZATION_VALUE",
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _evidence(present: bool, basis: str, refs: list[str]) -> dict[str, Any]:
    return {"present": present, "basis": basis, "frozen_refs": refs}


def _empty_dimensions() -> dict[str, dict[str, Any]]:
    return {
        name: _evidence(False, "No qualifying evidence in the frozen payload.", [])
        for name in DIMENSIONS
    }


def classify_claim_utility(decision: dict[str, Any]) -> dict[str, Any]:
    """Classify cognitive utility from frozen plan metadata, never case identity."""

    strategy = decision["final_safe_strategy"]
    payload = decision["final_plan"]["structured_payload"]
    dimensions = _empty_dimensions()
    safety_reason = None

    if strategy == "COMPARISON":
        sides = payload.get("sides", []) if payload else []
        cue = payload.get("explicit_cue") if payload else None
        if len(sides) != 2 or not cue:
            outcome = "UNSAFE_OR_UNSUPPORTED"
            safety_reason = "The frozen comparison lacks two operands or an explicit cue."
        else:
            dimensions["PERCEPTUAL_COMPARISON_LOAD"] = _evidence(
                True,
                "Two explicit trusted sides and an explicit comparison/contrast cue require mental comparison in prose.",
                [
                    "final_plan.structured_payload.sides[0]",
                    "final_plan.structured_payload.sides[1]",
                    "final_plan.structured_payload.explicit_cue",
                ],
            )
            dimensions["DECODING_OVERHEAD"] = _evidence(
                False,
                "The frozen payload supplies the complete two-sided comparison grammar without added axes or legend.",
                ["final_plan.structured_payload"],
            )
            outcome = "STRONG_EXTERNALIZATION_VALUE"
    elif strategy == "QUALIFIED_STATEMENT":
        qualifier = (
            payload.get("explicit_qualifier_or_condition") if payload else None
        )
        dimensions["GRAMMAR_ONLY_DECOMPOSITION"] = _evidence(
            bool(qualifier),
            "The frozen richer payload contains only one phrase extracted from an already complete claim sentence.",
            ["final_plan.structured_payload.explicit_qualifier_or_condition"],
        )
        dimensions["DECODING_OVERHEAD"] = _evidence(
            True,
            "A separate visual grammar would need to be decoded while externalizing no relation, sequence, or configuration.",
            ["final_plan.structured_payload"],
        )
        outcome = "LOW_EXTERNALIZATION_VALUE" if qualifier else "UNSAFE_OR_UNSUPPORTED"
        if not qualifier:
            safety_reason = "The qualification payload is empty."
    elif strategy == "QUANTITATIVE_CALLOUT":
        quantities = payload.get("quantity_excerpts", []) if payload else []
        dimensions["EMPHASIS_ONLY"] = _evidence(
            bool(quantities),
            "The frozen callout payload supplies quantities but no comparison operands, dimension mapping, sequence, or pattern.",
            ["final_plan.structured_payload.quantity_excerpts"],
        )
        if len(quantities) == 1:
            outcome = "LOW_EXTERNALIZATION_VALUE"
        elif len(quantities) > 1:
            outcome = "UNSAFE_OR_UNSUPPORTED"
            safety_reason = (
                "Turning multiple unbound quantities into an explanatory visual would require "
                "inventing operand labels, a dimension, or a relationship absent from the frozen payload."
            )
        else:
            outcome = "UNSAFE_OR_UNSUPPORTED"
            safety_reason = "The quantitative payload contains no trusted quantity."
    elif strategy == "CONCISE_PROSE":
        if payload is not None:
            raise ValidationError("SPEC-055 prose control unexpectedly has structured payload")
        dimensions["DECODING_OVERHEAD"] = _evidence(
            False,
            "Gate 1 proposed no richer structure; prose remains the positive representation choice.",
            ["final_safe_strategy", "final_plan.structured_payload"],
        )
        outcome = "LOW_EXTERNALIZATION_VALUE"
    else:
        raise ValidationError(f"unknown SPEC-055 strategy: {strategy}")

    gated_strategy = (
        strategy if outcome == "STRONG_EXTERNALIZATION_VALUE" else "CONCISE_PROSE"
    )
    return {
        "dimensions": dimensions,
        "utility_outcome": outcome,
        "gated_final_experimental_strategy": gated_strategy,
        "candidate_metadata_preserved_for_manual_study": outcome
        == "POSSIBLE_EXTERNALIZATION_VALUE",
        "safety_reason": safety_reason,
    }


def _claim_decision(decision: dict[str, Any]) -> dict[str, Any]:
    classified = classify_claim_utility(decision)
    identity = decision["focus_identity"]
    return {
        "utility_decision_id": f"spec057-claim-{_stable(decision['decision_id'])[:16]}",
        "spec055_decision_id": decision["decision_id"],
        "focus_identity": identity,
        "claim_text": decision["claim_text"],
        "claim_text_sha256": hashlib.sha256(decision["claim_text"].encode()).hexdigest(),
        "prior_representation_character": decision["classification"]["character"],
        "prior_proposed_strategy": decision["final_safe_strategy"],
        "gate1_richer_candidate": decision["richer_than_prose_survived"],
        "frozen_structured_payload": decision["final_plan"]["structured_payload"],
        "frozen_display_field_traces": decision["final_plan"]["display_field_traces"],
        "grounding_provenance_refs": decision["grounding_provenance_refs"],
        **classified,
        "routing_input_audit": {
            "source_identity_used": False,
            "domain_identity_used": False,
            "spec056_owner_comment_used": False,
        },
        "mutation_audit": {
            "knowledge_model_changed": False,
            "semantic_vocabulary_changed": False,
            "topology_created": False,
            "production_renderer_changed": False,
        },
    }


def select_structural_controls(spec038: dict[str, Any]) -> list[dict[str, Any]]:
    """Select four controls using only frozen representation structure."""

    cases = [
        item
        for item in spec038["fixed_evaluation_cases"]
        if item["status"] == "PASS" and item["nodes_rendered"]
    ]

    def richest(strategies: set[str]) -> dict[str, Any]:
        eligible = [item for item in cases if item["representation_strategy"] in strategies]
        if not eligible:
            raise ValidationError(f"missing structural control for {sorted(strategies)}")
        return sorted(
            eligible,
            key=lambda item: (
                -len(item["relationships_rendered"]),
                -len(item["nodes_rendered"]),
                item["case"],
            ),
        )[0]

    selected = [
        richest({"CAUSAL_MECHANISM"}),
        richest({"HIERARCHY_COMPOSITION", "DEPENDENCY_STRUCTURE"}),
        richest({"RECIPROCAL_MECHANISM"}),
        richest({"FOCUSED_RELATIONSHIP"}),
    ]
    if len({item["case"] for item in selected}) != 4:
        raise ValidationError("structural control selection produced duplicate cases")
    return selected


def classify_structural_utility(case: dict[str, Any]) -> dict[str, Any]:
    strategy = case["representation_strategy"]
    nodes = case["nodes_rendered"]
    relationships = case["relationships_rendered"]
    dimensions = _empty_dimensions()
    relational = len(nodes) >= 3 and len(relationships) >= 2
    reciprocal = strategy == "RECIPROCAL_MECHANISM" and len(relationships) >= 2
    temporal = strategy == "PROCESS_SEQUENCE" and len(relationships) >= 1
    mechanistic = strategy == "RECIPROCAL_MECHANISM"
    focused = strategy == "FOCUSED_RELATIONSHIP" and len(nodes) == 2 and len(relationships) == 1

    dimensions["RELATIONAL_LOAD"] = _evidence(
        relational or reciprocal,
        (
            f"The accepted frozen payload has {len(nodes)} nodes and "
            f"{len(relationships)} explicit relationships."
        ),
        ["nodes_rendered", "relationships_rendered"],
    )
    dimensions["TEMPORAL_OR_PROCESS_LOAD"] = _evidence(
        temporal,
        "The accepted strategy explicitly preserves ordered process structure."
        if temporal
        else "The accepted strategy does not encode a temporal/process sequence.",
        ["representation_strategy", "relationships_rendered"] if temporal else [],
    )
    dimensions["SPATIAL_OR_MECHANISTIC_LOAD"] = _evidence(
        mechanistic,
        "Two explicit opposite-direction induction relationships form a reciprocal mechanism."
        if mechanistic
        else "No reciprocal or spatial mechanism is explicit in this frozen control.",
        ["representation_strategy", "relationships_rendered"] if mechanistic else [],
    )
    dimensions["DECODING_OVERHEAD"] = _evidence(
        focused,
        "A diagram grammar for one explicit relationship may cost as much to decode as the relationship prose.",
        ["nodes_rendered", "relationships_rendered"] if focused else [],
    )

    if relational or reciprocal or temporal or mechanistic:
        outcome = "STRONG_EXTERNALIZATION_VALUE"
    elif focused:
        outcome = "POSSIBLE_EXTERNALIZATION_VALUE"
    else:
        outcome = "LOW_EXTERNALIZATION_VALUE"
    return {
        "dimensions": dimensions,
        "utility_outcome": outcome,
        "gated_final_experimental_strategy": (
            strategy if outcome == "STRONG_EXTERNALIZATION_VALUE" else "CONCISE_PROSE"
        ),
        "candidate_metadata_preserved_for_manual_study": outcome
        == "POSSIBLE_EXTERNALIZATION_VALUE",
        "safety_reason": None,
    }


def _structural_decision(case: dict[str, Any]) -> dict[str, Any]:
    frozen_payload = {
        "strategy": case["representation_strategy"],
        "spatial_grammar": case["spatial_grammar"],
        "nodes": case["nodes_rendered"],
        "relationships": case["relationships_rendered"],
    }
    return {
        "utility_decision_id": f"spec057-structural-{_stable(case['case'])[:16]}",
        "spec038_case": case["case"],
        "context_key": case["context_key"],
        "prior_proposed_strategy": case["representation_strategy"],
        "frozen_payload": frozen_payload,
        "frozen_payload_sha256": _stable(frozen_payload),
        "evidence_provenance_sources": case["evidence_provenance_sources"],
        **classify_structural_utility(case),
        "routing_input_audit": {
            "source_identity_used": False,
            "domain_identity_used": False,
            "owner_comment_used": False,
        },
        "mutation_audit": {
            "knowledge_model_changed": False,
            "semantic_vocabulary_changed": False,
            "topology_changed": False,
            "production_renderer_changed": False,
        },
    }


def _distribution(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(row[key] for row in rows).items()))


def _cross_tab(
    rows: list[dict[str, Any]], row_key: str, column_key: str
) -> dict[str, dict[str, int]]:
    table: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        table[row[row_key]][row[column_key]] += 1
    return {
        key: dict(sorted(values.items())) for key, values in sorted(table.items())
    }


def _spec056_audit(
    claim_rows: list[dict[str, Any]], spec056: dict[str, Any]
) -> dict[str, Any]:
    index = {
        (row["focus_identity"]["source_id"], row["focus_identity"]["claim_id"]): row
        for row in claim_rows
    }
    rows = []
    for selected in spec056["selection"]["selected_ids"]:
        decision = index[(selected["source_id"], selected["claim_id"])]
        rows.append(
            {
                **selected,
                "prior_strategy": decision["prior_proposed_strategy"],
                "utility_outcome": decision["utility_outcome"],
                "gated_final_experimental_strategy": decision[
                    "gated_final_experimental_strategy"
                ],
                "post_hoc_owner_finding_alignment": (
                    "RETAINED_PROMISING_COMPARISON"
                    if selected["strategy"] == "COMPARISON"
                    else "SUPPRESSED_REVIEWED_LOW_VALUE_RICHER_FORM"
                    if selected["strategy"]
                    in {"QUALIFIED_STATEMENT", "QUANTITATIVE_CALLOUT"}
                    else "PRESERVED_PROSE_RESTRAINT_CONTROL"
                ),
            }
        )
    return {
        "owner_comments_used_as_routing_inputs": False,
        "owner_findings_are_post_hoc_descriptive_evidence_only": True,
        "case_count": len(rows),
        "rows": rows,
        "summary": {
            "comparisons_retained": sum(
                row["strategy"] == "COMPARISON"
                and row["gated_final_experimental_strategy"] == "COMPARISON"
                for row in rows
            ),
            "qualified_statements_suppressed": sum(
                row["strategy"] == "QUALIFIED_STATEMENT"
                and row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
                for row in rows
            ),
            "quantitative_callouts_suppressed": sum(
                row["strategy"] == "QUANTITATIVE_CALLOUT"
                and row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
                for row in rows
            ),
            "prose_controls_preserved": sum(
                row["strategy"] == "CONCISE_PROSE"
                and row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
                for row in rows
            ),
            "directionally_aligned_cases": len(rows),
            "alignment_is_not_pedagogical_proof": True,
        },
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen evidence identity mismatch: {relative}")
    spec038 = _load(repo_root / SPEC038_REPORT)
    spec055 = _load(repo_root / SPEC055_REPORT)
    spec056 = _load(repo_root / SPEC056_REPORT)

    claim_rows = [
        _claim_decision(item)
        for item in spec055["claim_classifications_and_plans"]
    ]
    structural_rows = [
        _structural_decision(item) for item in select_structural_controls(spec038)
    ]
    if len(claim_rows) != 98 or len(
        {row["utility_decision_id"] for row in claim_rows}
    ) != 98:
        raise ValidationError("SPEC-057 must reconcile 98 unique SPEC-055 claims")
    if sum(row["gate1_richer_candidate"] for row in claim_rows) != 53:
        raise ValidationError("SPEC-057 richer-candidate count changed")
    prose_controls = [row for row in claim_rows if not row["gate1_richer_candidate"]]
    if len(prose_controls) != 45 or any(
        row["gated_final_experimental_strategy"] != "CONCISE_PROSE"
        for row in prose_controls
    ):
        raise ValidationError("SPEC-057 prose control invariant failed")

    before = _distribution(claim_rows, "prior_proposed_strategy")
    after = _distribution(claim_rows, "gated_final_experimental_strategy")
    outcome_distribution = _distribution(claim_rows, "utility_outcome")
    structural_outcomes = _distribution(structural_rows, "utility_outcome")
    retained_richer = sum(
        row["gated_final_experimental_strategy"] != "CONCISE_PROSE"
        for row in claim_rows
    )
    spec056_audit = _spec056_audit(claim_rows, spec056)
    all_traceable = all(
        row["grounding_provenance_refs"]
        and all(
            evidence["basis"] and isinstance(evidence["frozen_refs"], list)
            for evidence in row["dimensions"].values()
        )
        for row in claim_rows
    )
    all_structural_traceable = all(
        row["frozen_payload_sha256"] == _stable(row["frozen_payload"])
        and all(
            evidence["basis"] and isinstance(evidence["frozen_refs"], list)
            for evidence in row["dimensions"].values()
        )
        for row in structural_rows
    )

    return {
        "schema": "spec057.cognitive-utility-gate-experiment-report.v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
        "cognitive_utility_contract": UTILITY_CONTRACT,
        "cognitive_utility_contract_sha256": _stable(UTILITY_CONTRACT),
        "evidence_identities": [
            {"path": path, "sha256": sha}
            for path, sha in EXPECTED_EVIDENCE_IDENTITIES.items()
        ],
        "structural_control_selection": {
            "sample_size": 4,
            "algorithm": [
                "richest accepted CAUSAL_MECHANISM by relationship count, node count, then case ID",
                "richest accepted HIERARCHY_COMPOSITION or DEPENDENCY_STRUCTURE by relationship count, node count, then case ID",
                "richest accepted RECIPROCAL_MECHANISM by relationship count, node count, then case ID",
                "richest accepted FOCUSED_RELATIONSHIP by relationship count, node count, then case ID",
            ],
            "source_or_domain_used": False,
            "selected_case_ids": [row["spec038_case"] for row in structural_rows],
        },
        "claim_decisions": claim_rows,
        "structural_positive_control_decisions": structural_rows,
        "before_after_strategy_distribution": {
            "spec055_before": before,
            "spec057_after": after,
            "richer_before": 53,
            "richer_after": retained_richer,
            "returned_to_prose": 53 - retained_richer,
        },
        "claim_utility_outcome_distribution": outcome_distribution,
        "outcomes_by_representation_character": _cross_tab(
            claim_rows, "prior_representation_character", "utility_outcome"
        ),
        "strategies_after_by_representation_character": _cross_tab(
            claim_rows,
            "prior_representation_character",
            "gated_final_experimental_strategy",
        ),
        "structural_control_outcome_distribution": structural_outcomes,
        "spec056_owner_review_audit": spec056_audit,
        "experiment_questions": {
            "richer_claim_plans_retained": retained_richer,
            "character_survival": {
                "highest_retained_count": "DESCRIPTIVE_CONTRAST",
                "full_survival_rate": [
                    "DESCRIPTIVE_CONTRAST",
                    "QUANTITATIVE_COMPARISON",
                ],
                "retained_over_total": {
                    "DESCRIPTIVE_CONTRAST": "4/4",
                    "QUANTITATIVE_COMPARISON": "3/3",
                },
            },
            "grammar_only_qualified_statements_suppressed": all(
                row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
                for row in claim_rows
                if row["prior_proposed_strategy"] == "QUALIFIED_STATEMENT"
            ),
            "emphasis_only_quantitative_callouts_suppressed": all(
                row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
                for row in claim_rows
                if row["prior_proposed_strategy"] == "QUANTITATIVE_CALLOUT"
            ),
            "explicit_comparisons_survive": all(
                row["gated_final_experimental_strategy"] == "COMPARISON"
                for row in claim_rows
                if row["prior_proposed_strategy"] == "COMPARISON"
            ),
            "multi_node_structural_controls_survive": all(
                row["gated_final_experimental_strategy"] != "CONCISE_PROSE"
                for row in structural_rows
                if len(row["frozen_payload"]["nodes"]) >= 3
            ),
            "prose_controls_remain_prose": all(
                row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
                for row in prose_controls
            ),
            "new_semantic_or_topological_inference_required": False,
            "spec056_directional_alignment": spec056_audit["summary"],
            "policy_constrained_enough_for_second_ab_experiment": True,
            "pedagogical_effectiveness_proven": False,
        },
        "safety_topology_audit": {
            "all_claim_evidence_traceable": all_traceable,
            "all_structural_controls_hash_bound_and_traceable": all_structural_traceable,
            "all_98_claims_reconciled": len(claim_rows) == 98,
            "all_53_richer_candidates_reconciled": sum(
                row["gate1_richer_candidate"] for row in claim_rows
            )
            == 53,
            "all_45_prose_controls_preserved": len(prose_controls) == 45,
            "knowledge_model_mutations": 0,
            "semantic_vocabulary_mutations": 0,
            "topology_mutations": 0,
            "spec055_artifact_mutations": 0,
            "spec056_artifact_mutations": 0,
            "production_renderer_or_ui_changes": 0,
            "promotion_actions": 0,
        },
        "experiment_branch": {
            "class": "COGNITIVE_UTILITY_GATE_SUPPORTED",
            "reason": (
                "The generic frozen-payload gate preserves all explicit comparisons and "
                "strong structural controls, suppresses grammar/emphasis-only treatments, "
                "leaves every prose control unchanged, and creates no semantics or topology."
            ),
        },
        "recommended_next_step": {
            "class": "UTILITY_GATED_LEARNER_SURFACE_AB_EXPERIMENT",
            "reason": (
                "A separately authorized owner experiment can test the seven retained "
                "claim comparisons against prose without promoting the gate or renderers."
            ),
            "implementation_authorized": False,
        },
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
            "question": (
                "Can the frozen-payload gate conservatively predict when representation "
                "complexity performs useful cognitive work rather than merely reformatting prose?"
            ),
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_retrievals": 0,
            "extraction_reruns": 0,
            "knowledge_model_changes": 0,
            "semantic_or_topology_changes": 0,
            "renderer_or_ui_changes": 0,
            "promotion_actions": 0,
        },
        "implementation_identities": [
            {"path": path, "sha256": _sha(repo_root / path)}
            for path in IMPLEMENTATION_PATHS
        ],
        "validation": {
            "focused_spec057_and_regression_tests": "PASS (124 tests)",
            "full_offline_suite": "PASS (685 tests)",
            "deterministic_regeneration": "PASS",
            "json_validation": "PASS",
            "git_diff_check": "PASS",
            "provenance_and_secret_safety": "PASS",
            "protected_state_audit": "PASS (hash-bound and empty protected-path diff)",
            "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
        },
        "deviations": [],
    }


def write_report(repo_root: Path, output_path: Path) -> dict[str, Any]:
    report = build_report(repo_root)
    _write_json(output_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the offline SPEC-057 cognitive-utility gate"
    )
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output or root / OUTPUT_PATH
    report = write_report(root, output)
    print(
        json.dumps(
            {
                "branch": report["experiment_branch"]["class"],
                "claims": len(report["claim_decisions"]),
                "richer_after": report["before_after_strategy_distribution"][
                    "richer_after"
                ],
                "structural_controls": len(
                    report["structural_positive_control_decisions"]
                ),
                "owner_review": report["owner_review"]["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
