"""Prepare the offline SPEC-023 owner-review artifact from frozen inputs."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

from .baseline004 import (
    BASELINE004_EXECUTABLE_HASHES,
    baseline004_directory,
    verify_baseline004,
)
from .explanatory_projection import (
    FOCUS_ENTITY_ID,
    FROZEN_SPEC020_HASHES,
    build_explanatory_projection,
    canonical_bytes,
    load_frozen_spec020_inputs,
)
from .learner_navigation import DEPTH_ENTITY_ID, SPEC021_SEMANTIC_HASHES
from .models import ValidationError


EVALUATION_NAME = "spec-023-realistic-semantic-depth-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
REJECTED_CAUSAL_ASSERTION_ID = "assertion-ae10fa8748fdac1f"
OWNER_REVIEW_INSTRUCTION = (
    "Use the map naturally. Find the double-slit experiment, explore it more "
    "deeply when the interface offers that option, and tell me whether the deeper "
    "view actually helps you understand it."
)


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec020_directory() -> Path:
    return (
        repository_root()
        / "examples/evaluations/spec-020-realistic-semantic-depth-20260905"
    )


def default_spec021_directory() -> Path:
    return (
        repository_root()
        / "examples/evaluations/spec-021-focus-explanatory-projection-20260905"
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _source_location(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repository_root()))
    except ValueError:
        return str(path.resolve())


def _paths(files: Iterable[Path], directories: Iterable[Path]) -> list[Path]:
    result = list(files)
    for directory in directories:
        result.extend(path for path in sorted(directory.rglob("*")) if path.is_file())
    return sorted(result)


def protected_baseline_hashes() -> dict[str, dict[str, Any]]:
    root = repository_root()
    groups = {
        "BASELINE-001": _paths(
            [root / "baselines/BASELINE-001-interface.md"],
            [root / "baselines/BASELINE-001-interface"],
        ),
        "BASELINE-002": _paths(
            [root / "baselines/BASELINE-002-continuous-navigation-reference.md"],
            [
                root
                / "examples/evaluations/ops-002-continuous-interface-baseline-restoration-20260905"
            ],
        ),
        "BASELINE-003": _paths(
            [root / "baselines/BASELINE-003-hybrid-learning-workspace.md"],
            [
                root
                / "examples/evaluations/spec-019-navigation-learning-workspace-20260905"
            ],
        ),
        "BASELINE-004": _paths(
            [root / "baselines/BASELINE-004-learner-navigation-workspace.md"],
            [root / "baselines/BASELINE-004-learner-navigation-workspace"],
        ),
    }
    result = {}
    for label, paths in groups.items():
        files = {str(path.relative_to(root)): _hash(path) for path in paths}
        result[label] = {
            "aggregate_sha256": hashlib.sha256(canonical_bytes(files)).hexdigest(),
            "file_count": len(files),
            "files": files,
        }
    return result


def _reject_protected_output(
    output_dir: Path,
    protected_directories: Iterable[Path],
) -> None:
    resolved_output = output_dir.resolve()
    for protected in protected_directories:
        resolved_protected = protected.resolve()
        if resolved_output == resolved_protected or resolved_output.is_relative_to(
            resolved_protected
        ):
            raise ValidationError(
                "SPEC-023 output must be isolated from frozen input directories"
            )


def _verify_spec021(spec021_dir: Path) -> dict[str, str]:
    actual = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if actual != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory projection identity mismatch")
    return actual


def _semantic_gate(spec020_dir: Path, spec021_dir: Path) -> dict[str, Any]:
    inputs = load_frozen_spec020_inputs(spec020_dir)
    if inputs.file_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 packet identity mismatch")
    projection_path = spec021_dir / "projection.json"
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    rebuilt = build_explanatory_projection(inputs).to_dict()
    if canonical_bytes(projection) != canonical_bytes(rebuilt):
        raise ValidationError("SPEC-021 projection differs from frozen deterministic projection")
    diagnostics = json.loads(
        (spec021_dir / "projection-diagnostics.json").read_text(encoding="utf-8")
    )
    tier_audit = json.loads(
        (spec021_dir / "semantic-tier-audit.json").read_text(encoding="utf-8")
    )
    canonical_ids = {item["assertion_id"] for item in projection["canonical_items"]}
    explanatory_ids = {
        item["assertion_id"] for item in projection["explanatory_items"]
    }
    evidence = [
        span
        for collection in (projection["canonical_items"], projection["explanatory_items"])
        for item in collection
        for span in item["evidence"]
    ]
    source = inputs.scope["text"]
    evidence_resolvable = all(
        source[span["start_char"]:span["end_char"]] == span["quote"]
        for span in evidence
    )
    checks = {
        "focus_is_double_slit_experiment": projection["focus_entity_id"]
        == FOCUS_ENTITY_ID
        == DEPTH_ENTITY_ID,
        "projection_matches_deterministic_frozen_build": True,
        "canonical_item_count_is_two": len(projection["canonical_items"]) == 2,
        "explanatory_item_count_is_six": len(projection["explanatory_items"]) == 6,
        "semantic_tiers_distinct": all(
            item["semantic_tier"] == "TRUSTED_CANONICAL"
            for item in projection["canonical_items"]
        )
        and all(
            item["semantic_tier"] == "SOURCE_BACKED_NON_CANONICAL"
            for item in projection["explanatory_items"]
        ),
        "known_rejected_causal_item_not_canonical": REJECTED_CAUSAL_ASSERTION_ID
        not in canonical_ids,
        "known_rejected_causal_item_remains_explanatory": REJECTED_CAUSAL_ASSERTION_ID
        in explanatory_ids,
        "rejected_item_promotion_count_zero": diagnostics[
            "rejected_item_promotion_count"
        ]
        == 0,
        "pairwise_edge_fabrication_count_zero": diagnostics[
            "pairwise_edge_fabrication_count"
        ]
        == 0,
        "evidence_resolvable": evidence_resolvable,
        "tier_audit_preserved": REJECTED_CAUSAL_ASSERTION_ID
        in tier_audit["rejected_or_partial_not_promoted"],
    }
    if not all(checks.values()):
        raise ValidationError("SPEC-023 semantic machine gate failed closed")
    return {
        "status": "PASS",
        "checks": checks,
        "spec020_file_hashes": inputs.file_hashes,
        "evidence_span_count": len(evidence),
    }


def prepare_semantic_depth_review_evaluation(
    *,
    output_dir: Path,
    baseline_dir: Path = baseline004_directory(),
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
) -> dict[str, Any]:
    _reject_protected_output(
        output_dir,
        (
            repository_root() / "baselines",
            baseline_dir,
            spec020_dir,
            spec021_dir,
        ),
    )
    baseline_before = protected_baseline_hashes()
    baseline_hashes = verify_baseline004(baseline_dir)
    projection_hashes = _verify_spec021(spec021_dir)
    semantic = _semantic_gate(spec020_dir, spec021_dir)
    output_dir.mkdir(parents=True, exist_ok=False)

    for name in BASELINE004_EXECUTABLE_HASHES:
        shutil.copyfile(baseline_dir / name, output_dir / name)
    for name in ("projection-diagnostics.json", "semantic-tier-audit.json"):
        shutil.copyfile(spec021_dir / name, output_dir / name)

    fixture = json.loads((output_dir / "workspace-fixture.json").read_text(encoding="utf-8"))
    depth_ids = fixture["learner_navigation"]["admitted_depth_entity_ids"]
    runtime_hashes = {name: _hash(output_dir / name) for name in baseline_hashes}
    learner_script = (output_dir / "learner-grammar.js").read_text(encoding="utf-8")
    projection_script = (output_dir / "projection-extension.js").read_text(
        encoding="utf-8"
    )
    runtime_checks = {
        "baseline004_executable_byte_identical": runtime_hashes == baseline_hashes,
        "contextual_depth_only_for_double_slit": depth_ids == [DEPTH_ENTITY_ID],
        "global_depth_control_absent": "Double-slit depth"
        not in learner_script,
        "local_depth_affordance_present": "Explore deeper" in learner_script,
        "return_control_present": '"Return"' in learner_script,
        "camera_state_not_mutated_by_projection": "state.camera"
        not in projection_script,
        "parent_state_snapshot_and_return_present": all(
            token in learner_script
            for token in ("depthSnapshot", "learnerReturnDepth", "projection-return")
        ),
        "deeper_items_selectable": all(
            token in projection_script
            for token in (
                'projectionSelect("concept"',
                'projectionSelect("canonical"',
                'projectionSelect("explanation"',
            )
        ),
        "evidence_hidden_until_requested_for_explanations": all(
            token in projection_script
            for token in (
                'projectionAddEvidence(detail,item.evidence,true)',
                'Show exact source evidence',
            )
        ),
        "semantic_strength_distinction_present": all(
            token in projection_script
            for token in (
                "Trusted canonical relationship",
                "Source-backed explanation · non-canonical",
            )
        ),
    }
    baseline_after = protected_baseline_hashes()
    runtime_checks["baseline001_through_004_unchanged"] = (
        baseline_before == baseline_after
    )
    if not all(runtime_checks.values()):
        raise ValidationError("SPEC-023 BASELINE-004 integration gate failed closed")

    machine_gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic["checks"],
        "browser_console_clean": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    report = {
        "spec": "SPEC-023",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "focus_entity_id": FOCUS_ENTITY_ID,
        "integration_seam": "exact BASELINE-004 executable plus isolated evidence records",
        "baseline_hashes_before": baseline_before,
        "baseline_hashes_after": baseline_after,
        "baseline004_executable_hashes": baseline_hashes,
        "spec020_input_hashes": semantic["spec020_file_hashes"],
        "spec021_projection_hashes": projection_hashes,
        "machine_gate": machine_gate,
        "contextual_depth_eligibility_result": "PASS",
        "camera_and_return_state_result": "PASS_PENDING_BROWSER",
        "deeper_interaction_and_evidence_result": "PASS_PENDING_BROWSER",
        "deterministic_regeneration_result": "PENDING_OFFLINE_VERIFICATION",
        "offline_test_result": "PENDING",
        "files_changed": "PENDING_FINAL_INVENTORY",
        "repository_state": "PENDING_COMMIT_AND_PUSH",
        "dependencies_added": [],
        "dependencies_removed": [],
        "live_model_or_external_calls": 0,
        "semantic_changes": [],
        "representation_algorithm_changes": [],
        "ui_behavior_changes": [],
        "deviations": [],
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            f"{EVALUATION_RELATIVE_PATH} --port 8023"
        ),
    }
    manifest = {
        "spec": "SPEC-023",
        "title": "Realistic semantic depth through explanatory projection",
        "workspace_fixture": "workspace-fixture.json",
        "projection": "projection.json",
        "projection_diagnostics": "projection-diagnostics.json",
        "semantic_tier_audit": "semantic-tier-audit.json",
        "report": "report.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "machine-gate.json", machine_gate)
    _write_json(output_dir / "input-manifest.json", {
        "baseline004": {
            "directory": _source_location(baseline_dir),
            "executable_hashes": baseline_hashes,
        },
        "identity_verified": True,
        "spec020": {
            "directory": _source_location(spec020_dir),
            "input_hashes": semantic["spec020_file_hashes"],
        },
        "spec021": {
            "directory": _source_location(spec021_dir),
            "projection_hashes": projection_hashes,
        },
    })
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "browser-verification.json", {
        "status": "PENDING_MANUAL_BROWSER_VERIFICATION",
        "console": {},
        "interaction": {},
    })
    _write_json(output_dir / "human-review-template.json", {
        "instruction": OWNER_REVIEW_INSTRUCTION,
        "status": "BLOCKED_PENDING_MACHINE_GATE",
        "owner_response": None,
        "verdict": "PENDING",
        "allowed_verdicts": [
            "SEMANTIC_DEPTH_BETTER",
            "MIXED",
            "NO_MEANINGFUL_IMPROVEMENT",
            "INCONCLUSIVE",
        ],
    })
    (output_dir / "README.md").write_text(
        "# SPEC-023 realistic semantic depth review\n\n"
        "This offline artifact reuses the exact BASELINE-004 executable and the frozen "
        "SPEC-020/021 double-slit semantic projection.\n\n"
        "```sh\n"
        f"{report['viewer_command']}\n"
        "```\n",
        encoding="utf-8",
    )
    return report
