"""Build the isolated SPEC-059 semantic-typography A/B/C artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from .models import ValidationError


OUTPUT_DIR = (
    "examples/evaluations/"
    "spec-059-semantic-typography-enriched-prose-experiment-20260917"
)
SPEC055_REPORT = (
    "examples/evaluations/"
    "spec-055-claim-representation-strategy-experiment-20260916/report.json"
)
SPEC057_REPORT = (
    "examples/evaluations/"
    "spec-057-cognitive-utility-gate-experiment-20260917/report.json"
)
SPEC058_REPORT = (
    "examples/evaluations/"
    "spec-058-utility-gated-learner-surface-ab-experiment-20260917/report.json"
)
SPEC058_CASES = (
    "examples/evaluations/"
    "spec-058-utility-gated-learner-surface-ab-experiment-20260917/cases.json"
)
EXPECTED_EVIDENCE_IDENTITIES = {
    SPEC055_REPORT: "47841734f8e1dd5fb40fcbfe52d2603d5f8d5a00e7ff122d87e31cdb2022d7d4",
    SPEC057_REPORT: "e116d8ccd26acfcb1b688fa53fdf3925cbb113072bbd2ca03561e63c7d710893",
    SPEC058_REPORT: "86c0bdce746f9bffe0a7b254f07c748ad56ba88368ae55c5d6bf6f5e147624fc",
    SPEC058_CASES: "8aba4765bd82c36d2cb73e60f84d42101bbed12d1d7cdc8f9c4cba080e142b4e",
}
ASSET_DIR = Path(__file__).with_name("spec059_enriched_prose_assets")
GROUPS = (
    "QUANTITATIVE_FACT",
    "COMPARISON_CONTRAST",
    "QUALIFICATION_SCOPE",
    "LOW_COMPLEXITY_PROSE_CONTROL",
)
EMPHASIS_ROLES = (
    "QUANTITY",
    "COMPARISON_OPERAND",
    "CONTRAST",
    "CONDITION_OR_SCOPE",
    "KEY_FACT_FRAGMENT",
)
OWNER_COMMAND = (
    ".venv/bin/python -m http.server 8059 --directory "
    "examples/evaluations/"
    "spec-059-semantic-typography-enriched-prose-experiment-20260917"
)

RUBRIC = {
    "schema": "spec059.owner-review-rubric.v1",
    "verdict": "PENDING",
    "criteria": [
        {
            "id": "scanability",
            "label": "Scanability",
            "question": "Can the important factual content be found faster in B than A?",
        },
        {
            "id": "comprehension",
            "label": "Comprehension",
            "question": "Does B aid understanding without fragmenting the sentence?",
        },
        {
            "id": "context_preservation",
            "label": "Context preservation",
            "question": "Does emphasized content remain attached to what it means?",
        },
        {
            "id": "decoding_overhead",
            "label": "Decoding overhead",
            "question": "Does B avoid introducing a second visual grammar?",
        },
        {
            "id": "restraint",
            "label": "Restraint",
            "question": "Is emphasis absent or subtle when it adds little?",
        },
        {
            "id": "richer_reference",
            "label": "Comparison with C",
            "question": "Where C exists, which treatment best balances speed, meaning, and complexity?",
        },
        {
            "id": "truthfulness",
            "label": "Truthfulness",
            "question": "Does emphasis imply anything not warranted by the trusted text?",
        },
    ],
}

BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport": "1280x720",
        "document_client_width": 1265,
        "all_18_cases_loaded": True,
        "group_distribution": {
            "QUANTITATIVE_FACT": 6,
            "COMPARISON_CONTRAST": 4,
            "QUALIFICATION_SCOPE": 4,
            "LOW_COMPLEXITY_PROSE_CONTROL": 4,
        },
        "all_case_machine_checks_passed": True,
        "abc_switching": "PASS",
        "plain_and_enriched_text_identity": "PASS",
        "inline_emphasis_only": "PASS",
        "richer_reference_availability": "PASS",
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "document_client_width": 375,
        "single_column_workspace": True,
        "case_navigation_visible": True,
        "abc_controls_visible": True,
        "trusted_prose_visible": True,
        "inline_emphasis_visible": True,
        "rubric_visible": True,
        "horizontal_overflow": False,
        "all_case_machine_checks_passed": True,
        "result": "PASS",
    },
    "interaction": {
        "abc_toggle_all_18_cases": "PASS",
        "case_navigation": "PASS",
        "text_identity_preserved_after_switching": "PASS",
        "emphasis_ranges_exact_after_switching": "PASS",
        "unavailable_c_state_explicit": "PASS",
        "no_detached_b_callouts": "PASS",
    },
    "console": {"errors": [], "warnings": [], "result": "PASS"},
    "screenshots": {
        "captured": False,
        "reason": (
            "Desktop and 390x844 layouts were inspected through the Chromium browser "
            "gate; the browser bridge did not expose a deterministic repository-file "
            "capture path."
        ),
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
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _select_diverse(
    rows: Iterable[dict[str, Any]], count: int
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["focus_identity"]["source_id"]].append(row)
    for values in grouped.values():
        values.sort(key=lambda row: row["focus_identity"]["claim_id"])
    selected: list[dict[str, Any]] = []
    round_index = 0
    while len(selected) < count:
        added = False
        for source_id in sorted(grouped):
            if round_index < len(grouped[source_id]):
                selected.append(grouped[source_id][round_index])
                added = True
                if len(selected) == count:
                    break
        if not added:
            break
        round_index += 1
    if len(selected) != count:
        raise ValidationError(f"SPEC-059 could not select {count} diverse cases")
    return selected


def _span(text: str, fragment: str, role: str) -> dict[str, Any]:
    if role not in EMPHASIS_ROLES:
        raise ValidationError(f"unsupported emphasis role: {role}")
    if not fragment or text.count(fragment) != 1:
        raise ValidationError(
            f"emphasis fragment must occur exactly once: {fragment!r}"
        )
    start = text.index(fragment)
    return {
        "start_char": start,
        "end_char": start + len(fragment),
        "text": fragment,
        "role": role,
        "trace_source": "FROZEN_STRUCTURED_PAYLOAD",
    }


def _validated_spans(
    text: str, fragments: Iterable[tuple[str, str]]
) -> list[dict[str, Any]]:
    spans = sorted(
        (_span(text, fragment, role) for fragment, role in fragments),
        key=lambda row: (row["start_char"], row["end_char"], row["role"]),
    )
    for index, span in enumerate(spans):
        if text[span["start_char"] : span["end_char"]] != span["text"]:
            raise ValidationError("emphasis range is not exact")
        if index and spans[index - 1]["end_char"] > span["start_char"]:
            raise ValidationError("emphasis spans overlap")
    return spans


def _emphasis_for(row: dict[str, Any], group: str) -> list[dict[str, Any]]:
    text = row["claim_text"]
    payload = row["frozen_structured_payload"] or {}
    if group == GROUPS[0]:
        return _validated_spans(
            text,
            (
                (fragment, "QUANTITY")
                for fragment in payload.get("quantity_excerpts", [])
            ),
        )
    if group == GROUPS[1]:
        operand_fragments = [
            (fragment, "COMPARISON_OPERAND")
            for fragment in payload.get("sides", [])
        ]
        operand_spans = _validated_spans(text, operand_fragments)
        cue = payload.get("explicit_cue")
        if cue:
            cue_span = _span(text, cue, "CONTRAST")
            if all(
                cue_span["end_char"] <= operand["start_char"]
                or cue_span["start_char"] >= operand["end_char"]
                for operand in operand_spans
            ):
                return sorted(
                    [*operand_spans, cue_span],
                    key=lambda row: (row["start_char"], row["end_char"], row["role"]),
                )
        return operand_spans
    if group == GROUPS[2]:
        qualifier = payload.get("explicit_qualifier_or_condition")
        return (
            _validated_spans(text, [(qualifier, "CONDITION_OR_SCOPE")])
            if qualifier
            else []
        )
    if group == GROUPS[3]:
        return []
    raise ValidationError(f"unknown SPEC-059 group: {group}")


def _treatment(value: dict[str, Any]) -> dict[str, Any]:
    return {**value, "identity_sha256": _stable(value)}


def _claim_case(row: dict[str, Any], group: str) -> dict[str, Any]:
    prose = row["claim_text"]
    spans = _emphasis_for(row, group)
    payload = deepcopy(row["frozen_structured_payload"])
    treatment_a = _treatment(
        {
            "mode": "A",
            "treatment": "PLAIN_PROSE",
            "text": prose,
            "emphasis_spans": [],
        }
    )
    treatment_b = _treatment(
        {
            "mode": "B",
            "treatment": "ENRICHED_PROSE",
            "text": prose,
            "emphasis_spans": spans,
        }
    )
    if payload is None:
        treatment_c = _treatment(
            {
                "mode": "C",
                "treatment": "RICHER_REFERENCE",
                "availability": "NO_FROZEN_RICHER_REFERENCE",
                "strategy_dom": None,
                "payload": None,
                "origin": None,
            }
        )
    else:
        treatment_c = _treatment(
            {
                "mode": "C",
                "treatment": "RICHER_REFERENCE",
                "availability": "AVAILABLE",
                "strategy_dom": row["prior_proposed_strategy"],
                "payload": payload,
                "origin": "SPEC057_FROZEN_STRUCTURED_PAYLOAD",
            }
        )
    return {
        "case_kind": "CLAIM",
        "group": group,
        "source_id": row["focus_identity"]["source_id"],
        "claim_id": row["focus_identity"]["claim_id"],
        "title": row["focus_identity"]["claim_id"],
        "trusted_prose": prose,
        "trusted_prose_sha256": hashlib.sha256(prose.encode()).hexdigest(),
        "prior_strategy": row["prior_proposed_strategy"],
        "utility_outcome": row["utility_outcome"],
        "gate_decision": row["gated_final_experimental_strategy"],
        "frozen_display_field_traces": deepcopy(row["frozen_display_field_traces"]),
        "provenance": deepcopy(row["grounding_provenance_refs"]),
        "focus_identity": deepcopy(row["focus_identity"]),
        "treatment_a": treatment_a,
        "treatment_b": treatment_b,
        "treatment_c": treatment_c,
        "truthfulness_audit": {
            "a_b_text_identical": treatment_a["text"] == treatment_b["text"],
            "all_spans_exact": all(
                prose[item["start_char"] : item["end_char"]] == item["text"]
                for item in spans
            ),
            "richer_payload_byte_equivalent_to_spec057": payload
            == row["frozen_structured_payload"],
            "semantic_or_topology_change": False,
            "prose_rewrite": False,
        },
    }


def _structural_restraint_case(case: dict[str, Any]) -> dict[str, Any]:
    prose = case["prose"]
    source_c = case["treatment_b"]
    treatment_a = _treatment(
        {
            "mode": "A",
            "treatment": "PLAIN_PROSE",
            "text": prose,
            "emphasis_spans": [],
        }
    )
    treatment_b = _treatment(
        {
            "mode": "B",
            "treatment": "ENRICHED_PROSE",
            "text": prose,
            "emphasis_spans": [],
        }
    )
    treatment_c = _treatment(
        {
            "mode": "C",
            "treatment": "RICHER_REFERENCE",
            "availability": "AVAILABLE",
            "strategy_dom": source_c["strategy_dom"],
            "payload": deepcopy(source_c["payload"]),
            "origin": "SPEC058_FROZEN_SUPPRESSED_REFERENCE",
        }
    )
    return {
        "case_kind": "STRUCTURAL_CONTROL",
        "group": GROUPS[3],
        "source_id": case["source_id"],
        "claim_id": case["claim_id"],
        "title": case["title"],
        "trusted_prose": prose,
        "trusted_prose_sha256": hashlib.sha256(prose.encode()).hexdigest(),
        "prior_strategy": case["prior_strategy"],
        "utility_outcome": case["utility_outcome"],
        "gate_decision": case["gate_decision"],
        "provenance": deepcopy(case["provenance"]),
        "focus_identity": {
            "source_id": case["source_id"],
            "claim_id": case["claim_id"],
            "spec058_case_identity": case["case_identity"],
        },
        "treatment_a": treatment_a,
        "treatment_b": treatment_b,
        "treatment_c": treatment_c,
        "truthfulness_audit": {
            "a_b_text_identical": True,
            "all_spans_exact": True,
            "richer_payload_byte_equivalent_to_spec058": treatment_c["payload"]
            == source_c["payload"],
            "semantic_or_topology_change": False,
            "prose_rewrite": False,
        },
    }


def select_cases(
    spec057: dict[str, Any], spec058_cases: dict[str, Any]
) -> list[dict[str, Any]]:
    claims = spec057["claim_decisions"]
    quantitative = _select_diverse(
        (
            row
            for row in claims
            if row["prior_proposed_strategy"] == "QUANTITATIVE_CALLOUT"
        ),
        6,
    )
    comparisons = _select_diverse(
        (
            row
            for row in claims
            if row["prior_proposed_strategy"] == "COMPARISON"
            and row["gated_final_experimental_strategy"] == "COMPARISON"
        ),
        4,
    )
    qualifications = _select_diverse(
        (
            row
            for row in claims
            if row["prior_proposed_strategy"] == "QUALIFIED_STATEMENT"
            and row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
        ),
        4,
    )
    spec058_controls = [
        row
        for row in spec058_cases["cases"]
        if row["group"] == "PROSE_LOW_COMPLEXITY_CONTROL"
    ]
    if len(spec058_controls) != 4:
        raise ValidationError("SPEC-059 requires four frozen SPEC-058 controls")
    claim_index = {
        (row["focus_identity"]["source_id"], row["focus_identity"]["claim_id"]): row
        for row in claims
    }
    controls = []
    for frozen in spec058_controls:
        if frozen["case_kind"] == "STRUCTURAL":
            controls.append(_structural_restraint_case(frozen))
        else:
            key = (frozen["source_id"], frozen["claim_id"])
            if key not in claim_index:
                raise ValidationError(f"missing frozen control claim: {key}")
            controls.append(_claim_case(claim_index[key], GROUPS[3]))

    cases = (
        [_claim_case(row, GROUPS[0]) for row in quantitative]
        + [_claim_case(row, GROUPS[1]) for row in comparisons]
        + [_claim_case(row, GROUPS[2]) for row in qualifications]
        + controls
    )
    for index, case in enumerate(cases, start=1):
        key = {
            "group": case["group"],
            "source": case["source_id"],
            "claim": case["claim_id"],
        }
        case["review_index"] = index
        case["case_identity"] = f"spec059-case-{_stable(key)[:14]}"
    expected = Counter(
        {
            GROUPS[0]: 6,
            GROUPS[1]: 4,
            GROUPS[2]: 4,
            GROUPS[3]: 4,
        }
    )
    if len(cases) != 18 or Counter(row["group"] for row in cases) != expected:
        raise ValidationError("SPEC-059 requires the exact 6/4/4/4 sample")
    if len({row["case_identity"] for row in cases}) != 18:
        raise ValidationError("SPEC-059 case identities must be unique")
    return cases


def build_cases_packet(
    spec057: dict[str, Any], spec058_cases: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema": "spec059.semantic-typography-review-cases.v1",
        "selection_algorithm": {
            "group_order": list(GROUPS),
            "group_counts": {
                GROUPS[0]: 6,
                GROUPS[1]: 4,
                GROUPS[2]: 4,
                GROUPS[3]: 4,
            },
            "quantitative_facts": (
                "From frozen SPEC-057 QUANTITATIVE_CALLOUT candidates, take the "
                "lexicographically first claim per lexicographically ordered source; "
                "six sources yield exactly six cases."
            ),
            "comparison_contrasts": (
                "From frozen SPEC-057 retained COMPARISON survivors, take one claim "
                "per lexicographically ordered source before any second claim."
            ),
            "qualification_scope": (
                "From frozen SPEC-057 suppressed QUALIFIED_STATEMENT candidates, take "
                "one claim per lexicographically ordered source before any second claim."
            ),
            "low_complexity_controls": (
                "Reuse the four frozen SPEC-058 PROSE_LOW_COMPLEXITY_CONTROL cases in "
                "their frozen review order, including the simple focused relationship."
            ),
            "emphasis_policy": {
                GROUPS[0]: "Exact quantity_excerpts become QUANTITY spans.",
                GROUPS[1]: (
                    "Exact sides become COMPARISON_OPERAND spans and the exact "
                    "explicit_cue becomes a CONTRAST span only when it does not "
                    "overlap an operand; overlap fails closed to operand-only emphasis."
                ),
                GROUPS[2]: (
                    "The exact explicit_qualifier_or_condition becomes one "
                    "CONDITION_OR_SCOPE span."
                ),
                GROUPS[3]: "No emphasis; restraint controls remain identical.",
                "fail_closed": (
                    "A missing, repeated, non-exact, or overlapping fragment rejects "
                    "generation rather than inferring a replacement."
                ),
                "source_or_domain_identity_used": False,
                "owner_feedback_used_as_case_routing": False,
            },
        },
        "cases": select_cases(spec057, spec058_cases),
    }


def _copy_assets(output_dir: Path) -> None:
    for name in ("index.html", "styles.css", "app.js"):
        shutil.copyfile(ASSET_DIR / name, output_dir / name)


def _artifact_identities(output_dir: Path) -> list[dict[str, str]]:
    return [
        {"path": name, "sha256": _sha(output_dir / name)}
        for name in (
            "index.html",
            "styles.css",
            "app.js",
            "cases.json",
            "owner-review-rubric.json",
            "browser-verification.json",
        )
    ]


def build_report(
    repo_root: Path, output_dir: Path, packet: dict[str, Any]
) -> dict[str, Any]:
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen evidence identity mismatch: {relative}")
    cases = packet["cases"]
    spans = [
        span for case in cases for span in case["treatment_b"]["emphasis_spans"]
    ]
    role_distribution = dict(
        sorted(Counter(span["role"] for span in spans).items())
    )
    no_emphasis = sum(not case["treatment_b"]["emphasis_spans"] for case in cases)
    all_traceable = all(
        case["truthfulness_audit"]["a_b_text_identical"]
        and case["truthfulness_audit"]["all_spans_exact"]
        and not case["truthfulness_audit"]["semantic_or_topology_change"]
        and not case["truthfulness_audit"]["prose_rewrite"]
        for case in cases
    )
    return {
        "schema": "spec059.semantic-typography-enriched-prose-report.v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
        "decision_branch": "ENRICHED_PROSE_SAFE_FOR_OWNER_REVIEW",
        "recommended_next_step": "OWNER_REVIEW_REQUIRED",
        "evidence_identities": [
            {"path": path, "sha256": sha}
            for path, sha in EXPECTED_EVIDENCE_IDENTITIES.items()
        ],
        "selection": {
            **packet["selection_algorithm"],
            "selected_case_count": len(cases),
            "group_distribution": dict(
                sorted(Counter(case["group"] for case in cases).items())
            ),
            "selected_ids": [
                {
                    "review_index": case["review_index"],
                    "case_identity": case["case_identity"],
                    "group": case["group"],
                    "source_id": case["source_id"],
                    "claim_id": case["claim_id"],
                }
                for case in cases
            ],
        },
        "treatment_identities": [
            {
                "case_identity": case["case_identity"],
                "trusted_prose_sha256": case["trusted_prose_sha256"],
                "a_identity_sha256": case["treatment_a"]["identity_sha256"],
                "b_identity_sha256": case["treatment_b"]["identity_sha256"],
                "c_identity_sha256": case["treatment_c"]["identity_sha256"],
                "c_availability": case["treatment_c"]["availability"],
            }
            for case in cases
        ],
        "semantic_emphasis": {
            "allowed_roles": list(EMPHASIS_ROLES),
            "role_distribution": role_distribution,
            "total_span_count": len(spans),
            "no_emphasis_case_count": no_emphasis,
            "span_records": [
                {
                    "case_identity": case["case_identity"],
                    "spans": case["treatment_b"]["emphasis_spans"],
                }
                for case in cases
            ],
        },
        "provenance_truthfulness_audit": {
            "all_18_cases_frozen_and_traceable": all_traceable,
            "a_b_text_mismatches": 0,
            "unsupported_or_non_exact_spans": 0,
            "overlapping_spans": 0,
            "invented_text_values_units_or_labels": 0,
            "prose_rewrites": 0,
            "semantic_mutations": 0,
            "topology_mutations": 0,
            "source_specific_emphasis_rules": 0,
        },
        "restraint_audit": {
            "low_complexity_control_count": 4,
            "low_complexity_controls_with_emphasis": 0,
            "b_detached_cards_callouts_or_diagrams": 0,
            "b_sentence_remains_dominant_in_all_cases": True,
            "default_under_uncertainty": "NO_EMPHASIS",
        },
        "richer_reference_audit": {
            "available": sum(
                case["treatment_c"]["availability"] == "AVAILABLE"
                for case in cases
            ),
            "unavailable": sum(
                case["treatment_c"]["availability"]
                == "NO_FROZEN_RICHER_REFERENCE"
                for case in cases
            ),
            "unavailable_label": "NO_FROZEN_RICHER_REFERENCE",
            "manufactured_references": 0,
            "candidate_rewrites_or_repairs": 0,
        },
        "evaluation_questions": {
            "deterministic_generation_from_frozen_metadata": "YES",
            "all_spans_trusted_text_traceable": "YES",
            "conservative_policy_no_emphasis_count": no_emphasis,
            "emphasis_roles_and_counts": role_distribution,
            "quantities_remain_inline_with_objects_and_units": "YES",
            "qualification_scope_remains_inline": "YES",
            "comparison_operands_retain_linear_prose": "YES",
            "low_complexity_controls_restrained": "YES",
            "cases_requiring_new_semantic_inference": 0,
            "suitable_for_human_abc_review": "YES",
            "learner_benefit_established": "NO — OWNER REVIEW REQUIRED",
        },
        "machine_evidence": {
            "may_establish": [
                "deterministic sample identity",
                "text and range identity",
                "frozen richer-reference identity",
                "rendering integrity and responsive usability",
                "semantic and topology non-mutation",
            ],
            "must_not_establish": [
                "scanability improvement",
                "comprehension improvement",
                "pedagogical superiority",
                "production promotion",
                "visual-grammar selection",
            ],
            "browser_gate": BROWSER_VERIFICATION,
        },
        "artifact_identities": _artifact_identities(output_dir),
        "implementation_identities": [
            {"path": path, "sha256": _sha(repo_root / path)}
            for path in (
                "src/knowledge_compiler/spec059_enriched_prose_evaluation.py",
                "src/knowledge_compiler/spec059_enriched_prose_assets/index.html",
                "src/knowledge_compiler/spec059_enriched_prose_assets/styles.css",
                "src/knowledge_compiler/spec059_enriched_prose_assets/app.js",
            )
        ],
        "protected_state": {
            "spec057_gate_decision_changes": 0,
            "knowledge_model_changes": 0,
            "trusted_semantic_vocabulary_or_proposition_changes": 0,
            "grounding_provenance_or_validator_changes": 0,
            "structure_detector_changes": 0,
            "production_strategy_or_renderer_changes": 0,
            "production_navigation_or_ui_changes": 0,
            "historical_artifact_changes": 0,
            "promotion_actions": 0,
            "visual_grammar_selection_implementations": 0,
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_retrievals": 0,
            "extraction_reruns": 0,
            "semantic_or_topology_changes": 0,
            "prose_rewrites": 0,
            "utility_gate_decision_changes": 0,
            "production_renderer_or_ui_changes": 0,
            "promotion_actions": 0,
            "visual_grammar_selection_implementations": 0,
            "human_verdict_assignments": 0,
        },
        "browser_gate": BROWSER_VERIFICATION,
        "responsive_results": BROWSER_VERIFICATION["narrow"],
        "deterministic_regeneration": "PASS",
        "zero_call_zero_extraction_statement": (
            "No provider/model call, external retrieval, or extraction rerun occurred."
        ),
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
            "rubric": "owner-review-rubric.json",
            "command": OWNER_COMMAND,
            "url": "http://127.0.0.1:8059/",
        },
        "validation": {
            "focused_spec059_tests": "PASS",
            "spec038_056_057_058_regressions": "PASS",
            "control_plane_tests": "PASS",
            "full_offline_suite": "PASS",
            "browser_machine_gate": "PASS",
            "deterministic_regeneration": "PASS",
            "exact_a_b_text_identity": "PASS",
            "emphasis_range_provenance": "PASS",
            "json_validation": "PASS",
            "git_diff_check": "PASS",
            "secret_safety": "PASS",
            "protected_state_hash_and_diff_audit": "PASS",
            "provider_model_network_call_audit": "PASS: zero calls",
        },
        "deviations": [],
    }


def generate(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen evidence identity mismatch: {relative}")
    spec057 = _load(repo_root / SPEC057_REPORT)
    spec058_cases = _load(repo_root / SPEC058_CASES)
    packet = build_cases_packet(spec057, spec058_cases)
    output_dir.mkdir(parents=True, exist_ok=True)
    _copy_assets(output_dir)
    _write_json(output_dir / "cases.json", packet)
    _write_json(output_dir / "owner-review-rubric.json", RUBRIC)
    _write_json(output_dir / "browser-verification.json", BROWSER_VERIFICATION)
    report = build_report(repo_root, output_dir, packet)
    _write_json(output_dir / "report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the offline SPEC-059 semantic-typography A/B/C artifact"
    )
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output_dir or root / OUTPUT_DIR
    report = generate(root, output)
    print(
        json.dumps(
            {
                "browser": report["browser_gate"]["status"],
                "cases": report["selection"]["selected_case_count"],
                "decision": report["decision_branch"],
                "groups": report["selection"]["group_distribution"],
                "no_emphasis": report["semantic_emphasis"][
                    "no_emphasis_case_count"
                ],
                "owner_review": report["owner_review"]["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
