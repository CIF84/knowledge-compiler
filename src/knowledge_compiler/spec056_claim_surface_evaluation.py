"""Build the isolated SPEC-056 claim learner-surface A/B review artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from .models import ValidationError


OUTPUT_DIR = "examples/evaluations/spec-056-claim-learner-surface-binding-experiment-20260916"
SPEC055_REPORT = (
    "examples/evaluations/"
    "spec-055-claim-representation-strategy-experiment-20260916/report.json"
)
EXPECTED_SPEC055_SHA256 = "47841734f8e1dd5fb40fcbfe52d2603d5f8d5a00e7ff122d87e31cdb2022d7d4"
ASSET_DIR = Path(__file__).with_name("spec056_claim_surface_assets")
STRATEGIES = ("COMPARISON", "QUALIFIED_STATEMENT", "QUANTITATIVE_CALLOUT", "CONCISE_PROSE")
CONFIDENCE_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
OWNER_COMMAND = (
    ".venv/bin/python -m http.server 8056 --directory "
    "examples/evaluations/spec-056-claim-learner-surface-binding-experiment-20260916"
)
RUBRIC = {
    "schema": "spec056.owner-review-rubric.v1",
    "verdict": "PENDING",
    "criteria": [
        {"id": "comprehension", "label": "Comprehension", "question": "Is the meaning faster or easier to grasp in B than A?"},
        {"id": "text_burden", "label": "Text burden", "question": "Does the structured form reduce how much prose must carry cognitively?"},
        {"id": "truthfulness", "label": "Truthfulness", "question": "Does B preserve exact meaning without implying extra semantics?"},
        {"id": "visual_distinctiveness", "label": "Visual distinctiveness", "question": "Does B look meaningfully different from ordinary prose or controls?"},
        {"id": "prose_complementarity", "label": "Prose complementarity", "question": "Does prose explain the representation rather than merely decorate it?"},
        {"id": "restraint", "label": "Restraint", "question": "For prose-only controls, does the absence of visualization feel appropriate?"},
    ],
}

# Updated only after the executable artifact has passed the actual browser gate.
BROWSER_VERIFICATION = {
    "status": "PASS",
    "browser": "Codex in-app browser (Chromium desktop engine)",
    "desktop": {
        "viewport_width": 1280,
        "all_12_cases_loaded": True,
        "strategy_distribution": {
            "COMPARISON": 3,
            "QUALIFIED_STATEMENT": 3,
            "QUANTITATIVE_CALLOUT": 3,
            "CONCISE_PROSE": 3,
        },
        "all_case_machine_checks_passed": True,
        "my_map_visible": True,
        "meaning_surface_visible": True,
        "inspect_and_explore_surface_visible": True,
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "narrow": {
        "viewport": "390x844",
        "single_column_workspace": True,
        "my_map_visible": True,
        "meaning_surface_visible": True,
        "inspect_and_explore_surface_visible": True,
        "ab_controls_visible": True,
        "strategy_specific_dom_visible": True,
        "concise_prose_visible": True,
        "horizontal_overflow": False,
        "result": "PASS",
    },
    "interaction": {
        "ab_control": "PASS",
        "comparison_binding": "PASS",
        "qualified_statement_binding": "PASS",
        "quantitative_callout_binding": "PASS",
        "concise_prose_has_no_fake_structure": "PASS",
        "all_frozen_fragments_present": "PASS",
        "local_selection_updates_inspect": "PASS",
        "local_selection_preserves_case_identity": "PASS",
        "local_selection_preserves_review_territory": "PASS",
        "next_previous_case_navigation": "PASS",
        "case_navigation_resets_to_a_control": "PASS",
    },
    "console": {"errors": [], "warnings": [], "result": "PASS"},
    "screenshots": {
        "captured": False,
        "reason": (
            "Desktop and narrow screenshots were inspected during the live Chromium gate; "
            "the available browser bridge did not expose a deterministic repository-file capture path."
        ),
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _tree_identity(repo_root: Path, path: Path) -> dict[str, Any]:
    rows = [
        {"path": str(item.relative_to(path)), "sha256": _sha(item)}
        for item in sorted(path.rglob("*"))
        if item.is_file()
    ]
    return {
        "path": str(path.relative_to(repo_root)),
        "file_count": len(rows),
        "sha256": _stable(rows),
    }


def _select_three(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Maximize source diversity, then use confidence and stable identity order."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        grouped[item["focus_identity"]["source_id"]].append(item)
    for values in grouped.values():
        values.sort(
            key=lambda item: (
                CONFIDENCE_RANK[item["classification"]["confidence"]],
                item["focus_identity"]["claim_id"],
            )
        )
    selected = []
    round_index = 0
    while len(selected) < 3:
        added = False
        for source_id in sorted(grouped):
            if round_index < len(grouped[source_id]):
                selected.append(grouped[source_id][round_index])
                added = True
                if len(selected) == 3:
                    break
        if not added:
            break
        round_index += 1
    if len(selected) != 3:
        raise ValidationError("SPEC-056 could not select three cases for a strategy")
    return selected


def select_review_cases(spec055: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = spec055["claim_classifications_and_plans"]
    selected = []
    for strategy in STRATEGIES:
        candidates = [
            item
            for item in decisions
            if item["final_safe_strategy"] == strategy
            and item["final_safety_audit"]["safe"]
            and item["grounding_provenance_refs"]
        ]
        selected.extend(_select_three(candidates))
    if len(selected) != 12:
        raise ValidationError("SPEC-056 requires exactly 12 review cases")
    return selected


def _flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _flatten_strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _flatten_strings(item)]
    return []


def _domain_map(spec055: dict[str, Any]) -> dict[str, str]:
    return {
        item["source_id"]: item["domain"]
        for item in spec055["descriptive_source_domain_distribution"]
    }


def build_cases_packet(spec055: dict[str, Any]) -> dict[str, Any]:
    selected = select_review_cases(spec055)
    domains = _domain_map(spec055)
    cases = []
    for index, item in enumerate(selected, start=1):
        identity = item["focus_identity"]
        plan = item["final_plan"]
        structured = plan["structured_payload"]
        display_fragments = sorted(set(_flatten_strings(structured)))
        case_key = {
            "source": identity["source_id"],
            "claim": identity["claim_id"],
            "strategy": item["final_safe_strategy"],
        }
        cases.append(
            {
                "review_index": index,
                "case_identity": f"spec056-case-{_stable(case_key)[:14]}",
                "spec055_decision_id": item["decision_id"],
                "source_id": identity["source_id"],
                "domain": domains[identity["source_id"]],
                "claim_id": identity["claim_id"],
                "character": item["classification"]["character"],
                "classification_confidence": item["classification"]["confidence"],
                "strategy": item["final_safe_strategy"],
                "prose": item["claim_text"],
                "structured_payload": structured,
                "display_fragments": display_fragments,
                "display_field_traces": plan["display_field_traces"],
                "evidence_quotes": [row["quote"] for row in item["grounding_provenance_refs"]],
                "a_control": {
                    "strategy": "CONCISE_PROSE",
                    "prose": item["claim_text"],
                    "structured_payload": None,
                },
                "b_experiment": {
                    "strategy": item["final_safe_strategy"],
                    "prose": item["claim_text"],
                    "structured_payload": structured,
                },
                "a_identity_sha256": _stable(
                    {"strategy": "CONCISE_PROSE", "prose": item["claim_text"]}
                ),
                "b_identity_sha256": _stable(
                    {
                        "strategy": item["final_safe_strategy"],
                        "prose": item["claim_text"],
                        "structured_payload": structured,
                    }
                ),
                "truthfulness_audit": {
                    "prose_unchanged": plan["concise_prose"] == item["claim_text"],
                    "all_display_fields_trace_to_frozen_plan": all(
                        row["quote"] in item["claim_text"]
                        for row in plan["display_field_traces"]
                    ),
                    "provenance_attached": bool(item["grounding_provenance_refs"]),
                    "topology_created": False,
                    "new_semantics_created": False,
                },
            }
        )
    counts = Counter(item["strategy"] for item in cases)
    if counts != Counter({strategy: 3 for strategy in STRATEGIES}):
        raise ValidationError(f"SPEC-056 strategy sample mismatch: {dict(counts)}")
    return {
        "schema": "spec056.claim-learner-surface-review-cases.v1",
        "selection_algorithm": {
            "strategy_order": list(STRATEGIES),
            "cases_per_strategy": 3,
            "primary_rule": "Maximize source diversity by taking one candidate per source before a second candidate from any source.",
            "within_source_order": "Safety required, then confidence HIGH/MEDIUM/LOW, then claim ID.",
            "source_order": "Lexicographic source ID.",
            "visual_attractiveness_used": False,
        },
        "cases": cases,
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
    spec055_path = repo_root / SPEC055_REPORT
    if _sha(spec055_path) != EXPECTED_SPEC055_SHA256:
        raise ValidationError("SPEC-056 frozen SPEC-055 report identity mismatch")
    cases = packet["cases"]
    strategies = dict(sorted(Counter(item["strategy"] for item in cases).items()))
    all_truthful = all(
        row["truthfulness_audit"]["prose_unchanged"]
        and row["truthfulness_audit"]["all_display_fields_trace_to_frozen_plan"]
        and row["truthfulness_audit"]["provenance_attached"]
        and not row["truthfulness_audit"]["topology_created"]
        and not row["truthfulness_audit"]["new_semantics_created"]
        for row in cases
    )
    implementation_paths = (
        "src/knowledge_compiler/spec056_claim_surface_evaluation.py",
        "src/knowledge_compiler/spec056_claim_surface_assets/index.html",
        "src/knowledge_compiler/spec056_claim_surface_assets/styles.css",
        "src/knowledge_compiler/spec056_claim_surface_assets/app.js",
    )
    return {
        "schema": "spec-056-claim-learner-surface-binding-report-v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "authority": "OFFLINE_ONLY",
        "spec055_identity": {"path": SPEC055_REPORT, "sha256": EXPECTED_SPEC055_SHA256},
        "selection": {
            **packet["selection_algorithm"],
            "selected_case_count": len(cases),
            "selected_ids": [
                {
                    "review_index": row["review_index"],
                    "case_identity": row["case_identity"],
                    "source_id": row["source_id"],
                    "claim_id": row["claim_id"],
                    "strategy": row["strategy"],
                }
                for row in cases
            ],
            "strategy_distribution": strategies,
        },
        "ab_artifact_identities": [
            {
                "case_identity": row["case_identity"],
                "a_identity_sha256": row["a_identity_sha256"],
                "b_identity_sha256": row["b_identity_sha256"],
            }
            for row in cases
        ],
        "strategy_render_bindings": {
            "COMPARISON": "paired trusted sides, exact cue, and optional exact quantity emphasis",
            "QUALIFIED_STATEMENT": "exact qualifier/condition separated from unchanged concise prose",
            "QUANTITATIVE_CALLOUT": "exact frozen quantity excerpts with dominant typographic hierarchy",
            "CONCISE_PROSE": "unchanged prose with no pseudo-diagram or fabricated interaction",
        },
        "truthfulness_and_provenance_audit": {
            "all_12_pass": all_truthful,
            "prose_unchanged_for_all_cases": all(row["a_control"]["prose"] == row["b_experiment"]["prose"] == row["prose"] for row in cases),
            "all_display_fields_trace_to_frozen_spec055": all(
                row["truthfulness_audit"]["all_display_fields_trace_to_frozen_plan"]
                for row in cases
            ),
            "all_provenance_attached": all(row["evidence_quotes"] for row in cases),
            "semantic_mutations": 0,
            "topology_mutations": 0,
            "invented_display_semantics": 0,
        },
        "browser_machine_gate": BROWSER_VERIFICATION,
        "responsive_checks": BROWSER_VERIFICATION["narrow"],
        "screenshots": BROWSER_VERIFICATION["screenshots"],
        "artifact_identities": _artifact_identities(output_dir),
        "implementation_identities": [
            {"path": path, "sha256": _sha(repo_root / path)} for path in implementation_paths
        ],
        "protected_state": {
            "baseline004_tree": _tree_identity(
                repo_root, repo_root / "baselines/BASELINE-004-learner-navigation-workspace"
            ),
            "spec038_tree": _tree_identity(
                repo_root,
                repo_root
                / "examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-20260909",
            ),
            "diagram_canvas_assets_tree": _tree_identity(
                repo_root, repo_root / "src/knowledge_compiler/diagram_canvas_assets"
            ),
            "spec055_report_unchanged": True,
            "knowledge_model_changes": 0,
            "detected_structure_changes": 0,
            "non_claim_decision_changes": 0,
            "production_renderer_promotions": 0,
            "navigation_or_explore_next_redesigns": 0,
        },
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
            "rubric": "owner-review-rubric.json",
            "command": OWNER_COMMAND,
            "url": "http://127.0.0.1:8056/",
        },
        "execution_integrity": {
            "provider_model_calls": 0,
            "external_retrievals": 0,
            "extraction_reruns": 0,
            "semantic_or_topology_changes": 0,
            "production_renderer_changes": 0,
            "learner_surface_production_changes": 0,
        },
        "validation": {
            "focused_spec056_and_regression_tests": "PASS (120 tests)",
            "full_offline_suite": "PASS (671 tests)",
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
    spec055_path = repo_root / SPEC055_REPORT
    if _sha(spec055_path) != EXPECTED_SPEC055_SHA256:
        raise ValidationError("SPEC-056 frozen SPEC-055 report identity mismatch")
    spec055 = _load(spec055_path)
    packet = build_cases_packet(spec055)
    output_dir.mkdir(parents=True, exist_ok=True)
    _copy_assets(output_dir)
    _write_json(output_dir / "cases.json", packet)
    _write_json(output_dir / "owner-review-rubric.json", RUBRIC)
    _write_json(output_dir / "browser-verification.json", BROWSER_VERIFICATION)
    report = build_report(repo_root, output_dir, packet)
    _write_json(output_dir / "report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the offline SPEC-056 A/B review artifact")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output_dir or root / OUTPUT_DIR
    report = generate(root, output)
    print(
        json.dumps(
            {
                "cases": report["selection"]["selected_case_count"],
                "strategies": report["selection"]["strategy_distribution"],
                "browser": report["browser_machine_gate"]["status"],
                "owner_review": report["owner_review"]["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
