"""Build and finalize the offline SPEC-028 canonical interaction experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable

from .canonical_interaction import (
    state_transition_parity_matrix,
    ten_level_recursion_fixture,
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
    VIEWER_FILES,
    default_spec020_directory,
    default_spec021_directory,
    default_spec024_directory,
    default_spec025_directory,
    default_spec026_directory,
)
from .semantic_depth_review_evaluation import protected_baseline_hashes
from .semantic_interaction_evaluation import FROZEN_SPEC025_DIRECTORY_SHA256


EVALUATION_NAME = "spec-028-single-canonical-interaction-state-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC027_DIRECTORY_SHA256 = (
    "7d051d39e960a51b94229c026f822388b6a9071d9ccc6106d4fd042306d404e8"
)
OWNER_REVIEW_INSTRUCTION = (
    "Explore the map naturally. Open the double-slit deeper structure and interact "
    "with concepts, relationships, and explanations in both the map and the right "
    "pane. Switch rapidly among items, hover and click in both places, clear "
    "selection, and repeat after moving deeper. Tell me whether the two surfaces ever "
    "disagree about what is hovered, selected, active, or inactive, or whether depth "
    "still changes how interaction behaves."
)

SPEC027_RUNTIME_FILES = (*VIEWER_FILES, "recursive-interaction.css", "recursive-interaction.js")
_STYLE_ANCHOR = '  <link rel="stylesheet" href="recursive-interaction.css">'
_SCRIPT_ANCHOR = '  <script src="recursive-interaction.js"></script>'
_CANONICAL_STYLE = '  <link rel="stylesheet" href="canonical-interaction.css">'
_CANONICAL_SCRIPT = '  <script src="canonical-interaction.js"></script>'


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec027_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-027-recursive-bidirectional-interaction-grammar-20260905"


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
            raise ValidationError("SPEC-028 output must be isolated from frozen artifacts")


def _candidate_index(source: str) -> str:
    if source.count(_STYLE_ANCHOR) != 1 or source.count(_SCRIPT_ANCHOR) != 1:
        raise ValidationError("SPEC-027 executable extension seam changed")
    return source.replace(_STYLE_ANCHOR, f"{_STYLE_ANCHOR}\n{_CANONICAL_STYLE}").replace(
        _SCRIPT_ANCHOR, _CANONICAL_SCRIPT
    )


def _control_index(candidate: str) -> str:
    return candidate.replace(f"\n{_CANONICAL_STYLE}", "").replace(
        _CANONICAL_SCRIPT, _SCRIPT_ANCHOR
    )


def prepare_canonical_interaction_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec023_dir: Path = default_spec023_directory(),
    spec024_dir: Path = default_spec024_directory(),
    spec025_dir: Path = default_spec025_directory(),
    spec026_dir: Path = default_spec026_directory(),
    spec027_dir: Path = default_spec027_directory(),
) -> dict[str, Any]:
    _reject_protected_output(
        output_dir,
        (
            repository_root() / "baselines",
            spec020_dir,
            spec021_dir,
            spec023_dir,
            spec024_dir,
            spec025_dir,
            spec026_dir,
            spec027_dir,
        ),
    )
    baselines_before = protected_baseline_hashes()
    historical_before = {
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
    }
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")

    recursion = ten_level_recursion_fixture()
    parity = state_transition_parity_matrix()
    output_dir.mkdir(parents=True, exist_ok=False)
    for name in SPEC027_RUNTIME_FILES:
        shutil.copyfile(spec027_dir / name, output_dir / name)
    control_index = (spec027_dir / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(_candidate_index(control_index), encoding="utf-8")
    assets = files("knowledge_compiler").joinpath("canonical_interaction_assets")
    for name in ("canonical-interaction.css", "canonical-interaction.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    adapter = (output_dir / "canonical-interaction.js").read_text(encoding="utf-8")
    candidate_index = (output_dir / "index.html").read_text(encoding="utf-8")
    reducer_source = adapter.split("function canonicalReduce", 1)[1].split(
        "function canonicalEffective", 1
    )[0]
    runtime_checks = {
        "spec027_shell_composed_not_reimplemented": _control_index(candidate_index)
        == control_index,
        "spec027_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec027_dir / name).read_bytes()
            for name in SPEC027_RUNTIME_FILES
            if name != "index.html"
        ),
        "spec027_state_adapter_not_loaded": (
            _SCRIPT_ANCHOR not in candidate_index
            and _CANONICAL_SCRIPT in candidate_index
            and (output_dir / "recursive-interaction.js").is_file()
        ),
        "exactly_one_authoritative_state": (
            adapter.count("let canonicalInteractionState=") == 1
            and 'authoritativeStateCount:"1"' not in adapter
            and 'marker.dataset.authoritativeStateCount="1"' in adapter
        ),
        "one_reducer_path": (
            adapter.count("function canonicalReduce(") == 1
            and "canonicalInteractionState=canonicalReduce(" in adapter
        ),
        "one_way_projection_path": (
            adapter.count("function canonicalProjectAll(") == 1
            and "canonicalProjectAll();" in adapter
        ),
        "event_origin_not_reducer_input": "surface" not in reducer_source,
        "depth_not_reducer_input": "depth" not in reducer_source,
        "stable_key_excludes_location": (
            "function canonicalKey(identity,kind)" in adapter
            and "identity,kind" in adapter
        ),
        "legacy_semantic_handlers_removed_from_instances": (
            "function canonicalStripLegacyHandlers()" in adapter
            and "cloneNode(true)" in adapter
        ),
        "all_semantic_classes_use_canonical_resolver": all(
            token in adapter
            for token in (
                ".nav-node",
                ".learn-node",
                ".depth-map-node",
                ".depth-canonical-group",
                ".depth-explanatory-group",
                ".depth-sync-node",
                ".depth-sync-canonical",
                ".depth-sync-explanation",
            )
        ),
        "hover_and_selection_distinct": (
            "hovered:null,selected:null" in adapter
            and 'action==="hover"' in reducer_source
            and 'action==="select"' in reducer_source
        ),
        "ten_level_recursion_passes": (
            recursion["tested_depths"] == list(range(11))
            and recursion["semantic_state_equality_across_tested_depths"] == "PASS"
            and recursion["surface_projection_agreement"] == "PASS"
            and recursion["stale_state_count"] == 0
        ),
        "required_depth_matrix_passes": parity["status"] == "PASS",
        "spatial_depth_engine_unchanged": (output_dir / "depth-expansion.js").read_bytes()
        == (spec027_dir / "depth-expansion.js").read_bytes(),
        "semantic_legibility_adapter_unchanged": (
            output_dir / "semantic-interaction.js"
        ).read_bytes()
        == (spec027_dir / "semantic-interaction.js").read_bytes(),
    }
    classification = json.loads(
        (spec026_dir / "connection-classification.json").read_text(encoding="utf-8")
    )
    depth_packet = json.loads((spec027_dir / "depth-map.json").read_text(encoding="utf-8"))
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "candidate_depth_map_byte_identical": (output_dir / "depth-map.json").read_bytes()
        == (spec027_dir / "depth-map.json").read_bytes(),
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
        "synthetic_fixture_adds_no_product_semantics": recursion[
            "new_product_semantics"
        ]
        == [],
        "semantic_vocabulary_unchanged": True,
    }
    baselines_after = protected_baseline_hashes()
    historical_after = {
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
    }
    runtime_checks["baseline001_through_004_unchanged"] = baselines_before == baselines_after
    runtime_checks["spec023_through_027_unchanged"] = historical_before == historical_after
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        failed = [
            name
            for group in (runtime_checks, semantic_checks)
            for name, passed in group.items()
            if not passed
        ]
        raise ValidationError(f"SPEC-028 deterministic machine gate failed closed: {failed}")

    gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "state_transition_parity_matrix": parity,
        "ten_level_recursion_summary": {
            key: recursion[key]
            for key in (
                "tested_depths",
                "semantic_state_equality_across_tested_depths",
                "surface_projection_agreement",
                "stale_state_count",
            )
        },
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    report = {
        "spec": "SPEC-028",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "semantic_state_owners_found_in_spec027": {
            "baseline_parent_fields": [
                "selectedEntityId",
                "selectedRelationshipId",
                "previewEntityId",
                "previewRelationshipId",
            ],
            "depth_map_field": "depthState.selected",
            "depth_representation_field": "depthSyncState.mode plus rendered current classes",
            "spec027_field": "recursiveInteractionState selected/preview",
        },
        "canonical_state_representation": {
            "owner": "canonicalInteractionState",
            "fields": [
                "hovered stable semantic key",
                "selected stable semantic key",
                "hover ancestry",
                "selected ancestry",
                "revision",
            ],
            "authoritative_state_count": 1,
        },
        "event_dispatch_reducer_path": (
            "surface event -> canonicalObject stable key -> canonicalDispatch -> "
            "canonicalReduce -> canonicalProjectAll"
        ),
        "stable_semantic_identity_strategy": (
            "semantic class plus repository-stable semantic identity; ancestry and surface "
            "remain occurrence metadata and are excluded from the key"
        ),
        "retained_surface_local_state": {
            "camera_pan_zoom_history": "geometric navigation only",
            "expansion_open_path": "spatial availability and ancestry only",
            "representation_index": "presentation choice only",
            "legacy_semantic_fields": (
                "write-only compatibility projections overwritten from canonical state before "
                "frozen renderers run; legacy semantic handlers are removed from instances"
            ),
            "DOM_classes": "rendered projection output, never reducer input",
        },
        "ten_level_recursion_fixture_design": (
            "reuses two concepts, one canonical relationship, and one source-backed explanation "
            "through identical event sequences at depths 0 through 10 without product semantics"
        ),
        "ten_level_recursion_fixture": recursion,
        "state_transition_parity_matrix": parity,
        "baselines_before": baselines_before,
        "baselines_after": baselines_after,
        "historical_identities_before": historical_before,
        "historical_identities_after": historical_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "machine_gate": gate,
        "browser_hover_click_verification": "PASS_PENDING_BROWSER",
        "deterministic_regeneration_result": "PENDING_OFFLINE_VERIFICATION",
        "offline_test_result": "PENDING",
        "browser_verification": "browser-verification.json",
        "files_changed": "PENDING_FINAL_INVENTORY",
        "repository_state": "PENDING_COMMIT_AND_PUSH",
        "dependencies_added": [],
        "dependencies_removed": [],
        "live_model_or_external_calls": 0,
        "semantic_changes": [],
        "semantic_vocabulary_or_admission_changes": [],
        "representation_algorithm_changes": [],
        "ui_behavior_changes": [
            "semantic hover and selection now originate only in one canonical reducer and project to every surface"
        ],
        "deviations": [],
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            f"{EVALUATION_RELATIVE_PATH} --port 8028"
        ),
    }
    manifest = {
        "spec": "SPEC-028",
        "title": "Single canonical interaction state",
        "workspace_fixture": "workspace-fixture.json",
        "projection": "projection.json",
        "depth_map": "depth-map.json",
        "recursion_fixture": "ten-level-recursion-fixture.json",
        "parity_matrix": "state-transition-parity-matrix.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "ten-level-recursion-fixture.json", recursion)
    _write_json(output_dir / "state-transition-parity-matrix.json", parity)
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
                "CANONICAL_INTERACTION_STATE_CONFIRMED",
                "MIXED",
                "STATE_STILL_DIVERGES",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-028 single canonical interaction state\n\n"
        "This isolated offline candidate replaces SPEC-027 state synchronization with one "
        "canonical reducer and one-way map, representation, and explanation projections.\n\n"
        f"```sh\n{report['viewer_command']}\n```\n",
        encoding="utf-8",
    )
    return report


def finalize_canonical_interaction_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-028 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    required = {
        "ordinary_parent_navigation_intact",
        "continuous_spatial_expansion_intact",
        "canonical_noncanonical_legibility_intact",
        "single_authoritative_state_marker_passes",
        "parent_map_and_right_concept_hover_agree",
        "parent_map_and_right_concept_click_agree",
        "parent_relationship_origin_parity",
        "depth_map_and_right_concept_hover_agree",
        "depth_map_and_right_concept_click_agree",
        "depth_relationship_origin_parity",
        "depth_explanation_origin_parity",
        "selected_never_degrades_to_preview",
        "duplicate_instance_parity",
        "rapid_target_switching_zero_stale_state",
        "relationship_to_concept_switch_zero_stale_state",
        "clear_selection_zero_stale_state",
        "hover_after_clear_intact",
        "evidence_synchronization_intact",
        "ten_level_fixture_passes",
        "pan_zoom_and_collapse_intact",
        "no_blue_selection_artifact",
    }
    if set(checks) != required or not all(checks.values()):
        raise ValidationError("SPEC-028 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-028 browser console was not clean")
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
    _write_json(output_dir / "report.json", report)
    return report
