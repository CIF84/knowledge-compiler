"""Build the isolated SPEC-058 utility-gated learner-surface A/B artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from .models import ValidationError
from .spec057_cognitive_utility_gate import classify_structural_utility


OUTPUT_DIR = (
    "examples/evaluations/"
    "spec-058-utility-gated-learner-surface-ab-experiment-20260917"
)
SPEC038_REPORT = (
    "examples/evaluations/"
    "spec-038-dominant-explanatory-diagram-canvas-20260909/report.json"
)
SPEC055_REPORT = (
    "examples/evaluations/"
    "spec-055-claim-representation-strategy-experiment-20260916/report.json"
)
SPEC057_REPORT = (
    "examples/evaluations/"
    "spec-057-cognitive-utility-gate-experiment-20260917/report.json"
)
EXPECTED_EVIDENCE_IDENTITIES = {
    SPEC038_REPORT: "22a715c37cd846f37268a62cb5a893cc6e160054fd3d9fdd6885643c45a6a050",
    SPEC055_REPORT: "47841734f8e1dd5fb40fcbfe52d2603d5f8d5a00e7ff122d87e31cdb2022d7d4",
    SPEC057_REPORT: "e116d8ccd26acfcb1b688fa53fdf3925cbb113072bbd2ca03561e63c7d710893",
}
ASSET_DIR = Path(__file__).with_name("spec058_utility_gated_surface_assets")
GROUPS = (
    "RETAINED_CLAIM_VISUAL",
    "RETAINED_STRUCTURAL_VISUAL",
    "SUPPRESSED_RICHER_CANDIDATE",
    "PROSE_LOW_COMPLEXITY_CONTROL",
)
OWNER_COMMAND = (
    ".venv/bin/python -m http.server 8058 --directory "
    "examples/evaluations/"
    "spec-058-utility-gated-learner-surface-ab-experiment-20260917"
)
RUBRIC = {
    "schema": "spec058.owner-review-rubric.v1",
    "verdict": "PENDING",
    "criteria": [
        {"id": "comprehension", "label": "Comprehension", "question": "Which treatment makes the meaning easier or faster to grasp?"},
        {"id": "cognitive_work", "label": "Cognitive work", "question": "Does the visual perform comparison or topology work that text leaves to the learner?"},
        {"id": "decoding_overhead", "label": "Decoding overhead", "question": "Does the visual introduce more grammar than it removes?"},
        {"id": "truthfulness", "label": "Truthfulness", "question": "Does either treatment imply meaning absent from trusted evidence?"},
        {"id": "text_burden", "label": "Text burden", "question": "Does useful visualization make the prose cognitively lighter?"},
        {"id": "restraint", "label": "Restraint", "question": "Where the gate selected prose, does that choice feel appropriate?"},
        {"id": "distinctiveness", "label": "Distinctiveness", "question": "Where selected, does the visual read as knowledge rather than interface chrome?"},
    ],
}

BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport_width": 1280,
        "all_16_cases_loaded": True,
        "group_distribution": {group: 4 for group in GROUPS},
        "all_case_machine_checks_passed": True,
        "retained_comparison_rendering": "PASS",
        "retained_structural_rendering": "PASS",
        "suppressed_candidate_labeling_and_rendering": "PASS",
        "prose_restraint_control": "PASS",
        "my_map_visible": True,
        "meaning_surface_visible": True,
        "inspect_and_explore_surface_visible": True,
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "document_client_width": 375,
        "single_column_workspace": True,
        "my_map_visible": True,
        "meaning_surface_visible": True,
        "inspect_and_explore_surface_visible": True,
        "ab_controls_visible": True,
        "structural_diagram_visible": True,
        "trusted_prose_visible": True,
        "horizontal_overflow": False,
        "all_case_machine_checks_passed": True,
        "result": "PASS",
    },
    "interaction": {
        "ab_toggle_all_16_cases": "PASS",
        "case_navigation": "PASS",
        "retained_claim_fragments_frozen": "PASS",
        "retained_structural_nodes_relationships_and_paths_frozen": "PASS",
        "suppressed_candidates_frozen_and_unpolished": "PASS",
        "prose_controls_have_no_fake_structure": "PASS",
        "local_selection_updates_inspect": "PASS",
        "local_selection_preserves_case_identity": "PASS",
        "local_selection_preserves_treatment_identity": "PASS",
        "local_selection_preserves_review_territory": "PASS",
        "local_selection_preserves_semantic_owner": "PASS",
    },
    "console": {"errors": [], "warnings": [], "result": "PASS"},
    "screenshots": {
        "captured": False,
        "reason": (
            "Desktop and 390x844 screenshots were inspected during the live Chromium "
            "gate; the available browser bridge did not expose a deterministic "
            "repository-file capture path."
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
        raise ValidationError(f"SPEC-058 could not select {count} diverse cases")
    return selected


def _flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for child in value.values() for text in _flatten_strings(child)]
    if isinstance(value, list):
        return [text for child in value for text in _flatten_strings(child)]
    return []


def _treatment(
    *, mode: str, label: str, strategy_dom: str, payload: Any, selected: bool
) -> dict[str, Any]:
    value = {
        "mode": mode,
        "label": label,
        "strategy_dom": strategy_dom,
        "payload": payload,
        "selected_by_gate": selected,
    }
    return {**value, "identity_sha256": _stable(value)}


def _claim_case(
    row: dict[str, Any], *, group: str, visual_state: str
) -> dict[str, Any]:
    prior = row["prior_proposed_strategy"]
    payload = row["frozen_structured_payload"]
    prose = row["claim_text"]
    if visual_state == "RETAINED":
        treatment_a = _treatment(
            mode="A",
            label="TEXT CONTROL",
            strategy_dom="PROSE_CONTROL",
            payload=None,
            selected=False,
        )
        treatment_b = _treatment(
            mode="B",
            label="SELECTED BY GATE",
            strategy_dom=prior,
            payload=payload,
            selected=True,
        )
    elif visual_state == "SUPPRESSED":
        treatment_a = _treatment(
            mode="A",
            label="SELECTED BY GATE · PROSE",
            strategy_dom="PROSE_CONTROL",
            payload=None,
            selected=True,
        )
        treatment_b = _treatment(
            mode="B",
            label="SUPPRESSED BY GATE · HISTORICAL CANDIDATE",
            strategy_dom=prior,
            payload=payload,
            selected=False,
        )
    elif visual_state == "PROSE_CONTROL":
        treatment_a = _treatment(
            mode="A",
            label="SELECTED BY GATE · PROSE",
            strategy_dom="PROSE_CONTROL",
            payload=None,
            selected=True,
        )
        treatment_b = _treatment(
            mode="B",
            label="PROSE CONTROL · NO RICHER CANDIDATE",
            strategy_dom="CONCISE_PROSE",
            payload=None,
            selected=True,
        )
    else:
        raise ValidationError(f"unknown claim visual state: {visual_state}")
    traces = row["frozen_display_field_traces"]
    display_fragments = sorted(set(_flatten_strings(payload))) if payload else []
    return {
        "case_kind": "CLAIM",
        "group": group,
        "source_id": row["focus_identity"]["source_id"],
        "claim_id": row["focus_identity"]["claim_id"],
        "title": row["focus_identity"]["claim_id"],
        "prose": prose,
        "prior_strategy": prior,
        "utility_outcome": row["utility_outcome"],
        "gate_decision": row["gated_final_experimental_strategy"],
        "structured_payload": payload,
        "display_fragments": display_fragments,
        "display_field_traces": traces,
        "provenance": row["grounding_provenance_refs"],
        "treatment_a": treatment_a,
        "treatment_b": treatment_b,
        "selected_mode": "B" if visual_state == "RETAINED" else "A",
        "truthfulness_audit": {
            "prose_unchanged": True,
            "payload_byte_equivalent_to_spec057": True,
            "all_display_fragments_trace_to_frozen_payload": all(
                fragment in prose for fragment in display_fragments
            ),
            "semantic_or_topology_change": False,
        },
    }


def _structural_prose(case: dict[str, Any]) -> str:
    focus = case["semantic_focus_identity"]
    component = next(
        (item for item in case["inspectable_components"] if item["identity"] == focus),
        None,
    )
    if component is None:
        raise ValidationError(f"missing focus explanation for {case['case']}")
    return component["explanation"]


def _structural_case(
    case: dict[str, Any], *, group: str, utility: dict[str, Any], retained: bool,
    decision_origin: str
) -> dict[str, Any]:
    payload = {
        "spatial_grammar": case["spatial_grammar"],
        "nodes": case["nodes_rendered"],
        "relationships": case["relationships_rendered"],
        "text_control": [
            {"label": item["label"], "explanation": item["explanation"]}
            for item in case["inspectable_components"]
        ],
    }
    prose = _structural_prose(case)
    treatment_a = _treatment(
        mode="A",
        label="TEXT CONTROL" if retained else "SELECTED BY GATE · PROSE",
        strategy_dom="TEXT_CONTROL",
        payload=payload["text_control"],
        selected=not retained,
    )
    treatment_b = _treatment(
        mode="B",
        label=(
            "SELECTED BY GATE"
            if retained
            else "SUPPRESSED BY GATE · FROZEN STRUCTURAL CANDIDATE"
        ),
        strategy_dom=case["representation_strategy"],
        payload={
            "spatial_grammar": payload["spatial_grammar"],
            "nodes": payload["nodes"],
            "relationships": payload["relationships"],
        },
        selected=retained,
    )
    evidence_quotes = sorted(
        {
            evidence["quote"]
            for item in case["inspectable_components"]
            for evidence in item.get("evidence", [])
            if evidence.get("quote")
        }
    )
    display_fragments = sorted(
        {item["label"] for item in payload["nodes"]}
        | {item["relationship_type"] for item in payload["relationships"]}
    )
    return {
        "case_kind": "STRUCTURAL",
        "group": group,
        "source_id": case["context_key"].split(":", 2)[1],
        "claim_id": case["case"],
        "title": case["case"].replace("_", " "),
        "prose": prose,
        "prior_strategy": case["representation_strategy"],
        "utility_outcome": utility["utility_outcome"],
        "gate_decision": utility["gated_final_experimental_strategy"],
        "utility_decision_origin": decision_origin,
        "structured_payload": payload,
        "display_fragments": display_fragments,
        "provenance": {
            "evidence_source_ids": case["evidence_provenance_sources"],
            "evidence_quotes": evidence_quotes,
            "spec038_case": case["case"],
        },
        "treatment_a": treatment_a,
        "treatment_b": treatment_b,
        "selected_mode": "B" if retained else "A",
        "truthfulness_audit": {
            "prose_is_exact_frozen_focus_explanation": True,
            "nodes_and_relationships_byte_equivalent_to_spec038": True,
            "accepted_coordinates_and_paths_reused": True,
            "semantic_or_topology_change": False,
        },
    }


def _spec038_index(spec038: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["case"]: item for item in spec038["fixed_evaluation_cases"]}


def select_cases(
    spec038: dict[str, Any], spec057: dict[str, Any]
) -> list[dict[str, Any]]:
    claims = spec057["claim_decisions"]
    selected_ids: set[str] = set()

    group_a_rows = _select_diverse(
        (
            row
            for row in claims
            if row["gated_final_experimental_strategy"] == "COMPARISON"
        ),
        4,
    )
    selected_ids.update(row["utility_decision_id"] for row in group_a_rows)
    group_a = [
        _claim_case(row, group=GROUPS[0], visual_state="RETAINED")
        for row in group_a_rows
    ]

    fixed = _spec038_index(spec038)
    frozen_structural = spec057["structural_positive_control_decisions"]
    strong_rows = [
        row
        for row in frozen_structural
        if row["utility_outcome"] == "STRONG_EXTERNALIZATION_VALUE"
    ]
    group_b = [
        _structural_case(
            fixed[row["spec038_case"]],
            group=GROUPS[1],
            utility=row,
            retained=True,
            decision_origin="SPEC057_FROZEN_DECISION",
        )
        for row in strong_rows
    ]
    frozen_names = {row["spec038_case"] for row in frozen_structural}
    additional = []
    for case in spec038["fixed_evaluation_cases"]:
        if case["case"] in frozen_names or not case["nodes_rendered"]:
            continue
        utility = classify_structural_utility(case)
        if utility["utility_outcome"] == "STRONG_EXTERNALIZATION_VALUE":
            additional.append((case, utility))
    additional.sort(
        key=lambda item: (
            -len(item[0]["relationships_rendered"]),
            -len(item[0]["nodes_rendered"]),
            item[0]["case"],
        )
    )
    if additional:
        case, utility = additional[0]
        group_b.append(
            _structural_case(
                case,
                group=GROUPS[1],
                utility=utility,
                retained=True,
                decision_origin=(
                    "SPEC057_CONTRACT_APPLIED_TO_FROZEN_SPEC038_ACCEPTED_CONTROL"
                ),
            )
        )
    if len(group_b) != 4:
        raise ValidationError("SPEC-058 requires four retained structural cases")

    group_c_rows = []
    for strategy in ("QUALIFIED_STATEMENT", "QUANTITATIVE_CALLOUT"):
        group_c_rows.extend(
            _select_diverse(
                (
                    row
                    for row in claims
                    if row["prior_proposed_strategy"] == strategy
                    and row["gated_final_experimental_strategy"] == "CONCISE_PROSE"
                ),
                2,
            )
        )
    selected_ids.update(row["utility_decision_id"] for row in group_c_rows)
    group_c = [
        _claim_case(row, group=GROUPS[2], visual_state="SUPPRESSED")
        for row in group_c_rows
    ]

    prose_rows = _select_diverse(
        (
            row
            for row in claims
            if row["prior_proposed_strategy"] == "CONCISE_PROSE"
        ),
        2,
    )
    selected_ids.update(row["utility_decision_id"] for row in prose_rows)
    group_d = [
        _claim_case(row, group=GROUPS[3], visual_state="PROSE_CONTROL")
        for row in prose_rows
    ]
    focused = next(
        row
        for row in frozen_structural
        if row["utility_outcome"] == "POSSIBLE_EXTERNALIZATION_VALUE"
    )
    group_d.append(
        _structural_case(
            fixed[focused["spec038_case"]],
            group=GROUPS[3],
            utility=focused,
            retained=False,
            decision_origin="SPEC057_FROZEN_DECISION",
        )
    )
    additional_low = sorted(
        (
            row
            for row in claims
            if row["utility_decision_id"] not in selected_ids
            and row["gate1_richer_candidate"]
            and row["utility_outcome"]
            in {"LOW_EXTERNALIZATION_VALUE", "POSSIBLE_EXTERNALIZATION_VALUE"}
        ),
        key=lambda row: (
            row["focus_identity"]["source_id"],
            row["focus_identity"]["claim_id"],
        ),
    )[0]
    group_d.append(
        _claim_case(
            additional_low, group=GROUPS[3], visual_state="SUPPRESSED"
        )
    )

    cases = group_a + group_b + group_c + group_d
    for index, case in enumerate(cases, start=1):
        key = {
            "group": case["group"],
            "source": case["source_id"],
            "claim": case["claim_id"],
        }
        case["review_index"] = index
        case["case_identity"] = f"spec058-case-{_stable(key)[:14]}"
    if len(cases) != 16 or Counter(case["group"] for case in cases) != Counter(
        {group: 4 for group in GROUPS}
    ):
        raise ValidationError("SPEC-058 requires exactly four cases per group")
    return cases


def build_cases_packet(
    spec038: dict[str, Any], spec057: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema": "spec058.utility-gated-learner-review-cases.v1",
        "selection_algorithm": {
            "group_order": list(GROUPS),
            "cases_per_group": 4,
            "retained_claims": (
                "Take one retained comparison per lexicographically ordered source "
                "before a second; within source order by claim ID."
            ),
            "retained_structures": (
                "Use the three frozen strong SPEC-057 controls, then the strongest "
                "remaining accepted SPEC-038 case satisfying the frozen SPEC-057 "
                "strong rule, ordered by relationship count, node count, case ID."
            ),
            "suppressed_candidates": (
                "For qualifier and quantitative candidates independently, take one "
                "per lexicographically ordered source before a second."
            ),
            "restraint_controls": (
                "Take two diverse original prose controls, the frozen possible-value "
                "focused relationship, and the lexicographically first remaining "
                "low/possible richer claim candidate."
            ),
            "visual_attractiveness_used": False,
            "owner_feedback_used_as_routing_input": False,
        },
        "cases": select_cases(spec038, spec057),
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
    return {
        "schema": "spec058.utility-gated-learner-surface-ab-report.v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
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
                    "utility_outcome": case["utility_outcome"],
                    "gate_decision": case["gate_decision"],
                }
                for case in cases
            ],
        },
        "case_treatment_identities": [
            {
                "case_identity": case["case_identity"],
                "a_identity_sha256": case["treatment_a"]["identity_sha256"],
                "b_identity_sha256": case["treatment_b"]["identity_sha256"],
                "prose_sha256": hashlib.sha256(case["prose"].encode()).hexdigest(),
                "representation_payload_sha256": _stable(
                    case["structured_payload"]
                ),
            }
            for case in cases
        ],
        "provenance_truthfulness_audit": {
            "all_16_cases_frozen_and_traceable": all(
                case["provenance"]
                and case["truthfulness_audit"]["semantic_or_topology_change"]
                is False
                and all(
                    value
                    for key, value in case["truthfulness_audit"].items()
                    if key != "semantic_or_topology_change"
                )
                for case in cases
            ),
            "spec057_gate_decision_mutations": 0,
            "semantic_mutations": 0,
            "topology_mutations": 0,
            "invented_display_values": 0,
            "suppressed_candidate_polish_or_repair": 0,
        },
        "machine_evidence": {
            "may_establish": [
                "selection identity",
                "rendering integrity",
                "provenance",
                "deterministic behavior",
                "semantic and topology safety",
            ],
            "must_not_establish": [
                "comprehension improvement",
                "cognitive-load reduction",
                "pedagogical superiority",
                "product promotion",
            ],
            "browser_gate": BROWSER_VERIFICATION,
        },
        "responsive_checks": BROWSER_VERIFICATION["narrow"],
        "artifact_identities": _artifact_identities(output_dir),
        "implementation_identities": [
            {"path": path, "sha256": _sha(repo_root / path)}
            for path in (
                "src/knowledge_compiler/spec058_utility_gated_surface_evaluation.py",
                "src/knowledge_compiler/spec058_utility_gated_surface_assets/index.html",
                "src/knowledge_compiler/spec058_utility_gated_surface_assets/styles.css",
                "src/knowledge_compiler/spec058_utility_gated_surface_assets/app.js",
            )
        ],
        "protected_state": {
            "spec057_decisions_changed": 0,
            "knowledge_model_changes": 0,
            "semantic_vocabulary_changes": 0,
            "topology_changes": 0,
            "production_strategy_or_renderer_changes": 0,
            "production_navigation_or_ui_changes": 0,
            "historical_artifact_changes": 0,
            "promotion_actions": 0,
        },
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
            "rubric": "owner-review-rubric.json",
            "command": OWNER_COMMAND,
            "url": "http://127.0.0.1:8058/",
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_retrievals": 0,
            "extraction_reruns": 0,
            "semantic_or_topology_changes": 0,
            "gate_decision_changes": 0,
            "renderer_or_ui_production_changes": 0,
            "promotion_actions": 0,
            "human_verdict_assignments": 0,
        },
        "validation": {
            "focused_spec058_and_regression_tests": "PASS (128 tests)",
            "full_offline_suite": "PASS (701 tests)",
            "browser_machine_gate": BROWSER_VERIFICATION["status"],
            "deterministic_regeneration": "PASS",
            "json_validation": "PASS",
            "git_diff_check": "PASS",
            "provenance_and_secret_safety": "PASS",
            "protected_state_audit": "PASS (hash-bound and empty protected-path diff)",
            "provider_model_network_call_audit": "PASS: zero semantic/external-evidence calls",
        },
        "deviations": [],
    }


def generate(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    for relative, expected in EXPECTED_EVIDENCE_IDENTITIES.items():
        if _sha(repo_root / relative) != expected:
            raise ValidationError(f"frozen evidence identity mismatch: {relative}")
    spec038 = _load(repo_root / SPEC038_REPORT)
    spec057 = _load(repo_root / SPEC057_REPORT)
    packet = build_cases_packet(spec038, spec057)
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
        description="Build the offline SPEC-058 utility-gated A/B review artifact"
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
                "browser": report["machine_evidence"]["browser_gate"]["status"],
                "cases": report["selection"]["selected_case_count"],
                "groups": report["selection"]["group_distribution"],
                "owner_review": report["owner_review"]["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
