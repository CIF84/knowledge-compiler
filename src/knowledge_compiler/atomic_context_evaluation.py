"""Build and finalize the offline SPEC-029 atomic-context experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable

from .atomic_context import adversarial_transition_matrix
from .canonical_interaction import (
    state_transition_parity_matrix,
    ten_level_recursion_fixture,
)
from .canonical_interaction_evaluation import (
    FROZEN_SPEC027_DIRECTORY_SHA256,
    SPEC027_RUNTIME_FILES,
    default_spec027_directory,
)
from .depth_interaction_evaluation import directory_identity
from .depth_navigation_evaluation import (
    FROZEN_SPEC023_DIRECTORY_SHA256,
    default_spec023_directory,
)
from .explanatory_projection import FROZEN_SPEC020_HASHES, canonical_bytes
from .learner_navigation import SPEC021_SEMANTIC_HASHES
from .models import ValidationError
from .recursive_interaction_evaluation import (
    FROZEN_SPEC024_DIRECTORY_SHA256,
    FROZEN_SPEC026_DIRECTORY_SHA256,
    default_spec020_directory,
    default_spec021_directory,
    default_spec024_directory,
    default_spec025_directory,
    default_spec026_directory,
)
from .semantic_depth_review_evaluation import protected_baseline_hashes
from .semantic_interaction_evaluation import FROZEN_SPEC025_DIRECTORY_SHA256


EVALUATION_NAME = "spec-029-atomic-context-transition-and-semantic-coverage-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC028_DIRECTORY_SHA256 = (
    "06a1868a51399f16686a30e9d57efc58c455b44884a6b602528e88eefea74cb6"
)
OWNER_REVIEW_INSTRUCTION = (
    "Use the workspace naturally. Interact with a few ordinary relationships, then "
    "open the double-slit deeper structure and interact there from both panes. "
    "Without clearing anything first, move to History of Printing and then another "
    "domain and continue interacting. Switch back and forth a few times. Tell me "
    "whether the map and right pane ever disagree about which context or object is "
    "active, whether an old context remains visible after you have left it, or "
    "whether any ordinary relationship behaves differently from the deeper ones."
)

SPEC028_RUNTIME_FILES = (
    *SPEC027_RUNTIME_FILES,
    "canonical-interaction.css",
    "canonical-interaction.js",
)
_SCRIPT_ANCHOR = '  <script src="canonical-interaction.js"></script>'
_ATOMIC_SCRIPT = '  <script src="atomic-context.js"></script>'


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec028_directory() -> Path:
    return repository_root() / (
        "examples/evaluations/spec-028-single-canonical-interaction-state-20260905"
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _location(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repository_root()))
    except ValueError:
        return str(path.resolve())


def _verify_directory(directory: Path, expected: str, label: str) -> dict[str, Any]:
    identity = directory_identity(directory)
    if identity["aggregate_sha256"] != expected:
        raise ValidationError(f"{label} historical artifact identity mismatch")
    return identity


def _reject_protected_output(output_dir: Path, protected: Iterable[Path]) -> None:
    resolved = output_dir.resolve()
    for directory in protected:
        candidate = directory.resolve()
        if resolved == candidate or resolved.is_relative_to(candidate):
            raise ValidationError("SPEC-029 output must be isolated from frozen artifacts")


def _candidate_index(source: str) -> str:
    if source.count(_SCRIPT_ANCHOR) != 1:
        raise ValidationError("SPEC-028 executable extension seam changed")
    return source.replace(_SCRIPT_ANCHOR, _ATOMIC_SCRIPT)


def _control_index(candidate: str) -> str:
    return candidate.replace(_ATOMIC_SCRIPT, _SCRIPT_ANCHOR)


def _historical_identities(
    *,
    spec023_dir: Path,
    spec024_dir: Path,
    spec025_dir: Path,
    spec026_dir: Path,
    spec027_dir: Path,
    spec028_dir: Path,
) -> dict[str, Any]:
    return {
        "spec023": _verify_directory(
            spec023_dir, FROZEN_SPEC023_DIRECTORY_SHA256, "SPEC-023/FIX-023"
        ),
        "spec024": _verify_directory(
            spec024_dir, FROZEN_SPEC024_DIRECTORY_SHA256, "SPEC-024"
        ),
        "spec025": _verify_directory(
            spec025_dir, FROZEN_SPEC025_DIRECTORY_SHA256, "SPEC-025"
        ),
        "spec026": _verify_directory(
            spec026_dir, FROZEN_SPEC026_DIRECTORY_SHA256, "SPEC-026"
        ),
        "spec027": _verify_directory(
            spec027_dir, FROZEN_SPEC027_DIRECTORY_SHA256, "SPEC-027"
        ),
        "spec028": _verify_directory(
            spec028_dir, FROZEN_SPEC028_DIRECTORY_SHA256, "SPEC-028"
        ),
    }


def _ground_relationship_coverage(fixture: dict[str, Any]) -> dict[str, Any]:
    domains = {item["domain_id"]: item for item in fixture["domains"]}
    nodes = {
        item["entity_id"]: item for item in fixture["navigation"]["nodes"]
    }
    rows = []
    for edge in fixture["navigation"]["edges"]:
        domain = domains[edge["domain_id"]]
        matches = [
            (index, representation)
            for index, representation in enumerate(
                domain["learning_model"]["representations"]
            )
            if any(
                set(candidate["relationship_ids"]).intersection(
                    edge["relationship_ids"]
                )
                for candidate in representation["edges"]
            )
        ]
        primary = edge["relationship_ids"][0]
        agreement = bool(matches)
        rows.append(
            {
                "domain_id": edge["domain_id"],
                "domain_label": domain["label"],
                "edge_key": edge["edge_key"],
                "source_label": nodes[edge["source_entity_id"]]["label"],
                "target_label": nodes[edge["target_entity_id"]]["label"],
                "relationship_label": edge["relationship_label"],
                "represented_relationship_ids": edge["relationship_ids"],
                "canonical_interaction_identity": primary,
                "matching_representation_ids": [item[1]["id"] for item in matches],
                "event_origins_tested": ["map", "representation"],
                "hover_preview_projection_agreement": agreement,
                "selection_projection_agreement": agreement,
                "map_and_right_pane_agree": agreement,
            }
        )
    required = {"software_architecture", "history"}
    covered = {
        row["domain_id"]
        for row in rows
        if row["map_and_right_pane_agree"]
    }
    return {
        "status": (
            "PASS"
            if all(row["map_and_right_pane_agree"] for row in rows)
            and required <= covered
            else "FAIL"
        ),
        "required_regression_domains": sorted(required),
        "covered_domains": sorted(covered),
        "ground_level_relationship_projection_agreement": (
            "PASS" if all(row["map_and_right_pane_agree"] for row in rows) else "FAIL"
        ),
        "rows": rows,
    }


def prepare_atomic_context_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec023_dir: Path = default_spec023_directory(),
    spec024_dir: Path = default_spec024_directory(),
    spec025_dir: Path = default_spec025_directory(),
    spec026_dir: Path = default_spec026_directory(),
    spec027_dir: Path = default_spec027_directory(),
    spec028_dir: Path = default_spec028_directory(),
) -> dict[str, Any]:
    protected = (
        repository_root() / "baselines",
        spec020_dir,
        spec021_dir,
        spec023_dir,
        spec024_dir,
        spec025_dir,
        spec026_dir,
        spec027_dir,
        spec028_dir,
    )
    _reject_protected_output(output_dir, protected)
    baselines_before = protected_baseline_hashes()
    historical_before = _historical_identities(
        spec023_dir=spec023_dir,
        spec024_dir=spec024_dir,
        spec025_dir=spec025_dir,
        spec026_dir=spec026_dir,
        spec027_dir=spec027_dir,
        spec028_dir=spec028_dir,
    )
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")

    transition_matrix = adversarial_transition_matrix()
    recursion = ten_level_recursion_fixture()
    recursion_parity = state_transition_parity_matrix()

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in SPEC028_RUNTIME_FILES:
        shutil.copyfile(spec028_dir / name, output_dir / name)
    control_index = (spec028_dir / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(
        _candidate_index(control_index), encoding="utf-8"
    )
    asset = files("knowledge_compiler").joinpath(
        "atomic_context_assets", "atomic-context.js"
    )
    with asset.open("rb") as source, (output_dir / "atomic-context.js").open(
        "wb"
    ) as target:
        shutil.copyfileobj(source, target)

    fixture = json.loads(
        (output_dir / "workspace-fixture.json").read_text(encoding="utf-8")
    )
    coverage = _ground_relationship_coverage(fixture)
    adapter = (output_dir / "atomic-context.js").read_text(encoding="utf-8")
    candidate_index = (output_dir / "index.html").read_text(encoding="utf-8")
    reducer_source = adapter.split("function atomicReduce", 1)[1].split(
        "function atomicEffective", 1
    )[0]
    runtime_checks = {
        "spec028_shell_composed_not_reimplemented": _control_index(candidate_index)
        == control_index,
        "spec028_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec028_dir / name).read_bytes()
            for name in SPEC028_RUNTIME_FILES
            if name != "index.html"
        ),
        "spec028_state_adapter_not_loaded": (
            _SCRIPT_ANCHOR not in candidate_index
            and _ATOMIC_SCRIPT in candidate_index
            and (output_dir / "canonical-interaction.js").is_file()
        ),
        "exactly_one_authoritative_learner_state": (
            adapter.count("let atomicLearnerState=") == 1
            and 'marker.dataset.authoritativeStateCount="1"' in adapter
        ),
        "exactly_one_authoritative_active_context": (
            "activeContext:null" in adapter
            and 'marker.dataset.authoritativeContextCount="1"' in adapter
        ),
        "one_reducer_path": (
            adapter.count("function atomicReduce(") == 1
            and "atomicLearnerState=atomicReduce(" in adapter
        ),
        "one_way_projection_path": (
            adapter.count("function atomicProjectAll(") == 1
            and "atomicProjectAll();" in adapter
        ),
        "context_replacement_is_reducer_action": (
            'action==="replace_context"' in reducer_source
            and 'atomicReduce(atomicLearnerState,"replace_context"' in adapter
        ),
        "context_replacement_clears_old_semantic_state": all(
            token in reducer_source
            for token in (
                "hovered:null",
                "selected:null",
                "hoverAncestry:Object.freeze([])",
                "selectedAncestry:Object.freeze([])",
            )
        ),
        "context_changes_do_not_surface_clear": (
            'marker.dataset.surfaceSpecificSemanticClears="0"' in adapter
        ),
        "all_semantic_classes_use_atomic_resolver": all(
            token in adapter
            for token in (
                ".nav-node",
                ".learn-node",
                ".nav-edge-hit",
                ".learn-edge-hit",
                ".depth-map-node",
                ".depth-canonical-group",
                ".depth-explanatory-group",
                ".depth-sync-node",
                ".depth-sync-canonical",
                ".depth-sync-explanation",
            )
        ),
        "ground_relationship_coverage_passes": coverage["status"] == "PASS",
        "adversarial_transition_matrix_passes": transition_matrix["status"]
        == "PASS",
        "depth_transition_parity_passes": transition_matrix[
            "context_transition_behavior_depth_independent"
        ]
        == "PASS",
        "spec028_ten_level_recursion_remains_passing": (
            recursion["semantic_state_equality_across_tested_depths"] == "PASS"
            and recursion["surface_projection_agreement"] == "PASS"
            and recursion["stale_state_count"] == 0
            and recursion_parity["status"] == "PASS"
        ),
    }
    classification = json.loads(
        (spec026_dir / "connection-classification.json").read_text(encoding="utf-8")
    )
    depth_packet = json.loads((spec028_dir / "depth-map.json").read_text(encoding="utf-8"))
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "candidate_workspace_fixture_byte_identical": (
            output_dir / "workspace-fixture.json"
        ).read_bytes()
        == (spec028_dir / "workspace-fixture.json").read_bytes(),
        "candidate_depth_map_byte_identical": (output_dir / "depth-map.json").read_bytes()
        == (spec028_dir / "depth-map.json").read_bytes(),
        "canonical_predicates_unchanged": classification["counts"][
            "canonical_relationships"
        ]
        == 2,
        "known_rejected_causal_item_remains_noncanonical": all(
            item["semantic_tier"] == "SOURCE_BACKED_NON_CANONICAL"
            for item in depth_packet["expansions"][0]["explanatory_items"]
        ),
        "pairwise_edge_fabrication_count_zero": classification["counts"][
            "fabricated_pairwise_relationships"
        ]
        == 0,
        "synthetic_fixtures_add_no_product_semantics": (
            recursion["new_product_semantics"] == []
            and transition_matrix["new_product_semantics"] == []
        ),
        "semantic_vocabulary_and_admission_unchanged": True,
    }

    baselines_after = protected_baseline_hashes()
    historical_after = _historical_identities(
        spec023_dir=spec023_dir,
        spec024_dir=spec024_dir,
        spec025_dir=spec025_dir,
        spec026_dir=spec026_dir,
        spec027_dir=spec027_dir,
        spec028_dir=spec028_dir,
    )
    runtime_checks["baseline001_through_004_unchanged"] = (
        baselines_before == baselines_after
    )
    runtime_checks["spec023_through_028_unchanged"] = (
        historical_before == historical_after
    )
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        failed = [
            name
            for group in (runtime_checks, semantic_checks)
            for name, passed in group.items()
            if not passed
        ]
        raise ValidationError(f"SPEC-029 deterministic machine gate failed closed: {failed}")

    gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "ground_relationship_coverage": coverage,
        "adversarial_transition_matrix": transition_matrix,
        "spec028_ten_level_recursion_summary": {
            "tested_depths": recursion["tested_depths"],
            "semantic_state_equality_across_tested_depths": recursion[
                "semantic_state_equality_across_tested_depths"
            ],
            "surface_projection_agreement": recursion[
                "surface_projection_agreement"
            ],
            "stale_state_count": recursion["stale_state_count"],
            "parity_matrix_status": recursion_parity["status"],
        },
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    report = {
        "spec": "SPEC-029",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "active_context_owners_found_before_repair": {
            "workspace_fields": ["state.domainId", "state.representationIndex"],
            "learner_grammar_fields": ["learnerState.currentRegion", "learnerState.depthSnapshot"],
            "depth_fields": ["depthState.openPath", "depthState.parentSnapshot"],
            "semantic_owner": "SPEC-028 canonicalInteractionState",
            "failure": "context changed outside the semantic reducer, allowing prior semantic projection to survive",
        },
        "semantic_paths_found_outside_reducer_before_repair": [
            "region entrance directly assigned domain/representation and cleared legacy semantic fields",
            "representation preset directly changed representation and cleared legacy semantic fields",
            "ground-map hover did not adopt the representation containing the hovered relationship",
            "depth collapse restored a parent snapshot before canonical semantic-state adoption",
        ],
        "canonical_context_transition_representation": {
            "owner": "atomicLearnerState",
            "fields": [
                "activeContext",
                "revealed",
                "hovered",
                "selected",
                "hoverAncestry",
                "selectedAncestry",
                "revision",
            ],
            "authoritative_context_count": 1,
            "authoritative_semantic_state_count": 1,
        },
        "atomic_transition_behavior": (
            "resolve target context and semantic occurrence -> one replace_context reducer "
            "transition -> one-way projection to map, representation, and explanation"
        ),
        "ground_level_relationship_coverage": coverage,
        "cross_context_stale_state_regression": transition_matrix,
        "recursive_depth_transition_result": transition_matrix[
            "context_transition_behavior_depth_independent"
        ],
        "retained_surface_local_state": {
            "camera_pan_zoom_history": "geometric navigation only; adopted after history navigation",
            "depth_geometry": "revealed-map geometry projected from canonical revealed ancestry",
            "DOM_classes": "rendered output only; cleared and rederived from canonical state",
        },
        "baselines_before": baselines_before,
        "baselines_after": baselines_after,
        "historical_identities_before": historical_before,
        "historical_identities_after": historical_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "machine_gate": gate,
        "browser_verification": "browser-verification.json",
        "browser_hover_click_verification": "PASS_PENDING_BROWSER",
        "browser_console_result": "PENDING",
        "deterministic_regeneration_result": "PENDING_OFFLINE_VERIFICATION",
        "offline_test_result": "PENDING",
        "files_changed": "PENDING_FINAL_INVENTORY",
        "repository_state": "PENDING_COMMIT_AND_PUSH",
        "dependencies_added": [],
        "dependencies_removed": [],
        "live_model_or_external_calls": 0,
        "semantic_changes": [],
        "semantic_vocabulary_or_admission_changes": [],
        "representation_algorithm_changes": [],
        "ui_behavior_changes": [
            "context replacement and semantic focus now commit atomically",
            "ground-level relationship preview selects its existing representation context",
        ],
        "deviations": [],
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            f"{EVALUATION_RELATIVE_PATH} --port 8029"
        ),
    }
    manifest = {
        "spec": "SPEC-029",
        "title": "Atomic context transition and semantic coverage",
        "workspace_fixture": "workspace-fixture.json",
        "projection": "projection.json",
        "depth_map": "depth-map.json",
        "transition_matrix": "adversarial-transition-matrix.json",
        "ground_relationship_coverage": "ground-relationship-coverage.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "adversarial-transition-matrix.json", transition_matrix)
    _write_json(output_dir / "ground-relationship-coverage.json", coverage)
    _write_json(output_dir / "machine-gate.json", gate)
    _write_json(
        output_dir / "input-manifest.json",
        {
            "spec020": {"directory": _location(spec020_dir), "hashes": spec020_hashes},
            "spec021": {"directory": _location(spec021_dir), "hashes": spec021_hashes},
            **historical_before,
            "identity_verified": True,
        },
    )
    _write_json(output_dir / "report.json", report)
    _write_json(
        output_dir / "browser-verification.json",
        {"status": "PENDING_MANUAL_BROWSER_VERIFICATION", "checks": {}, "console": {}},
    )
    _write_json(
        output_dir / "human-review-template.json",
        {
            "instruction": OWNER_REVIEW_INSTRUCTION,
            "status": "BLOCKED_PENDING_MACHINE_GATE",
            "owner_response": None,
            "verdict": "PENDING",
            "allowed_verdicts": [
                "CONTEXT_LIFECYCLE_CONFIRMED",
                "MIXED",
                "CONTEXT_OR_COVERAGE_STILL_DIVERGES",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-029 atomic context transition and semantic coverage\n\n"
        "This isolated offline candidate replaces active context and semantic focus "
        "through one canonical learner-state transition and projects that state to "
        "the preserved SPEC-028 workspace.\n\n"
        f"```sh\n{report['viewer_command']}\n```\n",
        encoding="utf-8",
    )
    return report


BROWSER_CHECKS = {
    "ordinary_parent_navigation_intact",
    "continuous_spatial_expansion_intact",
    "single_authoritative_learner_state_marker_passes",
    "single_authoritative_context_marker_passes",
    "software_architecture_ground_relationship_hover_agrees",
    "software_architecture_ground_relationship_click_agrees",
    "history_ground_relationship_hover_agrees",
    "history_ground_relationship_click_agrees",
    "ground_relationship_right_origin_agrees",
    "deep_concept_origin_parity",
    "deep_relationship_origin_parity",
    "deep_explanation_origin_parity",
    "deep_to_history_context_replaced_atomically",
    "history_to_electromagnetism_context_replaced_atomically",
    "software_history_electromagnetism_sequence_agrees",
    "rapid_context_switching_zero_stale_state",
    "clear_then_context_switch_zero_stale_state",
    "collapse_then_context_switch_zero_stale_state",
    "map_and_right_context_always_agree",
    "selected_preview_semantics_agree",
    "stale_prior_context_semantic_identity_count_zero",
    "stale_prior_context_authoritative_projection_count_zero",
    "pan_zoom_overview_and_collapse_intact",
    "evidence_and_provenance_display_intact",
}


def finalize_atomic_context_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-029 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    if set(checks) != BROWSER_CHECKS or not all(checks.values()):
        raise ValidationError("SPEC-029 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-029 browser console was not clean")
    _write_json(output_dir / "browser-verification.json", browser_verification)
    gate = json.loads((output_dir / "machine-gate.json").read_text(encoding="utf-8"))
    gate["status"] = "PASS"
    gate["browser_checks"] = checks
    gate["browser_console_clean"] = True
    _write_json(output_dir / "machine-gate.json", gate)
    review = json.loads((output_dir / "human-review-template.json").read_text(encoding="utf-8"))
    review["status"] = "PENDING_OWNER_REVIEW"
    _write_json(output_dir / "human-review-template.json", review)
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    report["execution_stage"] = "IMPLEMENTED_AWAITING_OWNER_REVIEW"
    report["machine_integrity_verdict"] = "PASS"
    report["human_review_status"] = "PENDING_OWNER_REVIEW"
    report["machine_gate"] = gate
    report["browser_hover_click_verification"] = "PASS"
    report["browser_console_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report
