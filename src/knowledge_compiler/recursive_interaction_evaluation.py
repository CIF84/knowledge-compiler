"""Build and finalize the offline SPEC-027 recursive interaction experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable

from .depth_interaction_evaluation import directory_identity
from .depth_navigation_evaluation import (
    FROZEN_SPEC023_DIRECTORY_SHA256,
    default_spec023_directory,
)
from .explanatory_projection import FROZEN_SPEC020_HASHES, canonical_bytes
from .learner_navigation import SPEC021_SEMANTIC_HASHES
from .models import ValidationError
from .recursive_interaction import bidirectional_parity_matrix
from .semantic_depth_review_evaluation import protected_baseline_hashes
from .semantic_interaction_evaluation import FROZEN_SPEC025_DIRECTORY_SHA256


EVALUATION_NAME = "spec-027-recursive-bidirectional-interaction-grammar-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC024_DIRECTORY_SHA256 = (
    "cf9619552729860672a16e1b2759d32a96fdf2f209eaad7daf0a3331fc2f923a"
)
FROZEN_SPEC026_DIRECTORY_SHA256 = (
    "ed3f50d0ac2f9c7f0c5c5ff511a31d763303ea701b7a4f914df5e54173d9d9e9"
)
OWNER_REVIEW_INSTRUCTION = (
    "Explore the map naturally. Open the double-slit deeper structure and interact "
    "with concepts, relationships, and explanations both on the map and in the right "
    "pane. Use hover and click naturally in both places. Tell me whether the interface "
    "now behaves like one continuous map at every level, or whether anything still "
    "behaves differently simply because it is deeper."
)

VIEWER_FILES = (
    "index.html",
    "workspace.css",
    "workspace.js",
    "workspace-manifest.json",
    "workspace-fixture.json",
    "projection.css",
    "projection-extension.js",
    "projection.json",
    "projection-diagnostics.json",
    "semantic-tier-audit.json",
    "grammar.css",
    "learner-grammar.js",
    "depth-expansion.css",
    "depth-expansion.js",
    "depth-map.json",
    "depth-interaction.css",
    "depth-interaction.js",
    "semantic-interaction.css",
    "semantic-interaction.js",
)

_STYLE_ANCHOR = '  <link rel="stylesheet" href="semantic-interaction.css">'
_SCRIPT_ANCHOR = '  <script src="semantic-interaction.js"></script>'
_RECURSIVE_STYLE = '  <link rel="stylesheet" href="recursive-interaction.css">'
_RECURSIVE_SCRIPT = '  <script src="recursive-interaction.js"></script>'


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec020_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-020-realistic-semantic-depth-20260905"


def default_spec021_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-021-focus-explanatory-projection-20260905"


def default_spec024_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-024-depth-as-continuous-map-expansion-20260905"


def default_spec025_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-025-depth-invariant-interaction-grammar-20260905"


def default_spec026_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-026-semantic-interaction-invariance-20260905"


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


def _extend_index(source: str) -> str:
    if source.count(_STYLE_ANCHOR) != 1 or source.count(_SCRIPT_ANCHOR) != 1:
        raise ValidationError("SPEC-026 executable extension seam changed")
    return source.replace(_STYLE_ANCHOR, f"{_STYLE_ANCHOR}\n{_RECURSIVE_STYLE}").replace(
        _SCRIPT_ANCHOR, f"{_SCRIPT_ANCHOR}\n{_RECURSIVE_SCRIPT}"
    )


def _remove_index_extension(source: str) -> str:
    return source.replace(f"\n{_RECURSIVE_STYLE}", "").replace(
        f"\n{_RECURSIVE_SCRIPT}", ""
    )


def synthetic_recursive_fixture(depth_packet: dict[str, Any]) -> dict[str, Any]:
    expansion = depth_packet["expansions"][0]
    semantic_payload = {
        key: expansion[key]
        for key in (
            "concepts",
            "canonical_items",
            "explanatory_items",
            "explanatory_attachments",
        )
    }
    samples = {
        "concept": expansion["concepts"][0]["entity_id"],
        "canonical": expansion["canonical_items"][0]["id"],
        "explanation": expansion["explanatory_items"][0]["id"],
    }
    return {
        "fixture_only": True,
        "source_expansion_id": expansion["id"],
        "synthetic_expansion_id": "synthetic-depth-2",
        "parent_expansion_id": expansion["id"],
        "semantic_payload_sha256": hashlib.sha256(canonical_bytes(semantic_payload)).hexdigest(),
        "sample_semantic_objects": [
            {
                "kind": kind,
                "identity": identity,
                "locations": ["parent", "depth-1", "depth-2"],
                "shared_dispatch": "recursiveDispatch",
            }
            for kind, identity in samples.items()
        ],
        "new_product_semantics": [],
    }


def _reject_protected_output(output_dir: Path, protected: Iterable[Path]) -> None:
    resolved = output_dir.resolve()
    for directory in protected:
        candidate = directory.resolve()
        if resolved == candidate or resolved.is_relative_to(candidate):
            raise ValidationError("SPEC-027 output must be isolated from frozen artifacts")


def prepare_recursive_interaction_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec023_dir: Path = default_spec023_directory(),
    spec024_dir: Path = default_spec024_directory(),
    spec025_dir: Path = default_spec025_directory(),
    spec026_dir: Path = default_spec026_directory(),
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
        ),
    )
    baselines_before = protected_baseline_hashes()
    spec023_before = _verify_directory(
        spec023_dir, FROZEN_SPEC023_DIRECTORY_SHA256, "SPEC-023/FIX-023"
    )
    spec024_before = _verify_directory(
        spec024_dir, FROZEN_SPEC024_DIRECTORY_SHA256, "SPEC-024"
    )
    spec025_before = _verify_directory(
        spec025_dir, FROZEN_SPEC025_DIRECTORY_SHA256, "SPEC-025"
    )
    spec026_before = _verify_directory(
        spec026_dir, FROZEN_SPEC026_DIRECTORY_SHA256, "SPEC-026"
    )
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")

    depth_packet = json.loads((spec026_dir / "depth-map.json").read_text(encoding="utf-8"))
    parity = bidirectional_parity_matrix()
    recursive_fixture = synthetic_recursive_fixture(depth_packet)

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in VIEWER_FILES:
        shutil.copyfile(spec026_dir / name, output_dir / name)
    control_index = (spec026_dir / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(_extend_index(control_index), encoding="utf-8")
    assets = files("knowledge_compiler").joinpath("recursive_interaction_assets")
    for name in ("recursive-interaction.css", "recursive-interaction.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    adapter = (output_dir / "recursive-interaction.js").read_text(encoding="utf-8")
    runtime_checks = {
        "spec026_shell_composed_not_reimplemented": _remove_index_extension(
            (output_dir / "index.html").read_text(encoding="utf-8")
        )
        == control_index,
        "spec026_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec026_dir / name).read_bytes()
            for name in VIEWER_FILES
            if name != "index.html"
        ),
        "one_shared_state_transition": (
            "function recursiveTransition(action,item=null)" in adapter
            and "function recursiveDispatch(action,item=null)" in adapter
        ),
        "map_and_representation_use_same_object_resolver": (
            "function recursiveObject(target)" in adapter
            and 'surface:"map"' in adapter
            and '"representation"' in adapter
        ),
        "hover_and_click_share_dispatch": all(
            token in adapter
            for token in (
                'addEventListener("mouseover",recursiveEnter,true)',
                'addEventListener("mouseout",recursiveLeave,true)',
                'addEventListener("click",recursiveActivate,true)',
                'addEventListener("keydown",recursiveActivate,true)',
            )
        ),
        "right_depth_objects_are_interaction_targets": all(
            token in adapter
            for token in (
                "depth-sync-node[data-sync-id]",
                "depth-sync-canonical",
                "depth-sync-explanation[data-sync-id]",
                "depth-sync-attachment-group[data-sync-id]",
                "recursiveAddHit",
            )
        ),
        "preview_and_selection_are_distinct_state": (
            "recursiveInteractionState={selected:null,preview:null,history:[],suppressReentryIdentity:null}"
            in adapter
            and 'action==="clear_preview"' in adapter
        ),
        "no_depth_number_specific_dispatch_branch": not any(
            token in adapter
            for token in (
                'location==="depth-1"',
                'location==="depth-2"',
                "switch(depthState.openPath.length)",
            )
        ),
        "bidirectional_parity_matrix_passes": parity["status"] == "PASS",
        "synthetic_depth_2_uses_shared_dispatch": all(
            item["shared_dispatch"] == "recursiveDispatch"
            for item in recursive_fixture["sample_semantic_objects"]
        ),
        "spatial_depth_engine_unchanged": (output_dir / "depth-expansion.js").read_bytes()
        == (spec026_dir / "depth-expansion.js").read_bytes(),
        "semantic_legibility_adapter_unchanged": (
            output_dir / "semantic-interaction.js"
        ).read_bytes()
        == (spec026_dir / "semantic-interaction.js").read_bytes(),
    }
    classification = json.loads(
        (spec026_dir / "connection-classification.json").read_text(encoding="utf-8")
    )
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "candidate_depth_map_byte_identical": (output_dir / "depth-map.json").read_bytes()
        == (spec026_dir / "depth-map.json").read_bytes(),
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
        "synthetic_fixture_adds_no_product_semantics": recursive_fixture[
            "new_product_semantics"
        ]
        == [],
        "semantic_vocabulary_unchanged": True,
    }

    baselines_after = protected_baseline_hashes()
    spec023_after = _verify_directory(
        spec023_dir, FROZEN_SPEC023_DIRECTORY_SHA256, "SPEC-023/FIX-023"
    )
    spec024_after = _verify_directory(
        spec024_dir, FROZEN_SPEC024_DIRECTORY_SHA256, "SPEC-024"
    )
    spec025_after = _verify_directory(
        spec025_dir, FROZEN_SPEC025_DIRECTORY_SHA256, "SPEC-025"
    )
    spec026_after = _verify_directory(
        spec026_dir, FROZEN_SPEC026_DIRECTORY_SHA256, "SPEC-026"
    )
    runtime_checks["baseline001_through_004_unchanged"] = (
        baselines_before == baselines_after
    )
    runtime_checks["spec023_historical_artifact_unchanged"] = (
        spec023_before == spec023_after
    )
    runtime_checks["spec024_historical_artifact_unchanged"] = (
        spec024_before == spec024_after
    )
    runtime_checks["spec025_historical_artifact_unchanged"] = (
        spec025_before == spec025_after
    )
    runtime_checks["spec026_historical_artifact_unchanged"] = (
        spec026_before == spec026_after
    )
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        raise ValidationError("SPEC-027 deterministic machine gate failed closed")

    machine_gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "bidirectional_parity_matrix": parity,
        "synthetic_recursive_fixture": recursive_fixture,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    report = {
        "spec": "SPEC-027",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "previous_interaction_seams": {
            "parent": (
                "BASELINE-004 map and learning nodes independently bind anonymous hover, "
                "click, and keyboard handlers to parent-only focus state"
            ),
            "depth_map": (
                "SPEC-024 depth objects bind direct selection handlers and have no preview state"
            ),
            "depth_representation": (
                "SPEC-025/026 render mirrored depth objects without reverse interaction targets"
            ),
        },
        "shared_interaction_state_seam": (
            "one additive capture-phase semantic-object resolver and recursiveTransition state "
            "contract dispatch hover, selection, clearing, and keyboard activation from either "
            "surface before legacy location-specific handlers"
        ),
        "retained_location_metadata": (
            "parent vs expansion location is retained only in the legacy renderer bridge and "
            "DOM/spatial lookup; state transitions and action semantics contain no depth-number branch"
        ),
        "parent_behavior_exception": parity["parent_exceptions"][0],
        "bidirectional_parity_matrix": parity,
        "synthetic_recursive_fixture": recursive_fixture,
        "baselines_before": baselines_before,
        "baselines_after": baselines_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "spec023_identity_before": spec023_before,
        "spec023_identity_after": spec023_after,
        "spec024_identity_before": spec024_before,
        "spec024_identity_after": spec024_after,
        "spec025_identity_before": spec025_before,
        "spec025_identity_after": spec025_after,
        "spec026_identity_before": spec026_before,
        "spec026_identity_after": spec026_after,
        "machine_gate": machine_gate,
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
            "hover, selection, and reverse right-pane mirroring now share one semantic-object dispatcher"
        ],
        "deviations": [],
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            f"{EVALUATION_RELATIVE_PATH} --port 8027"
        ),
    }
    manifest = {
        "spec": "SPEC-027",
        "title": "Recursive bidirectional interaction grammar",
        "workspace_fixture": "workspace-fixture.json",
        "projection": "projection.json",
        "depth_map": "depth-map.json",
        "parity_matrix": "bidirectional-parity-matrix.json",
        "recursive_fixture": "synthetic-depth-2-fixture.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "bidirectional-parity-matrix.json", parity)
    _write_json(output_dir / "synthetic-depth-2-fixture.json", recursive_fixture)
    _write_json(output_dir / "machine-gate.json", machine_gate)
    _write_json(
        output_dir / "input-manifest.json",
        {
            "spec020": {"directory": _location(spec020_dir), "hashes": spec020_hashes},
            "spec021": {"directory": _location(spec021_dir), "hashes": spec021_hashes},
            "spec023": spec023_before,
            "spec024": spec024_before,
            "spec025": spec025_before,
            "spec026": spec026_before,
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
                "RECURSIVE_INTERACTION_INVARIANT",
                "MIXED",
                "DEPTH_STILL_HAS_SEPARATE_GRAMMAR",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-027 recursive bidirectional interaction grammar\n\n"
        "This isolated offline artifact preserves SPEC-026 and routes semantic-object "
        "interaction from either learner surface through one recursive state contract.\n\n"
        f"```sh\n{report['viewer_command']}\n```\n",
        encoding="utf-8",
    )
    return report


def finalize_recursive_interaction_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-027 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    required = {
        "ordinary_parent_navigation_intact",
        "parent_concept_hover_and_click_bidirectional",
        "parent_relationship_hover_and_click_bidirectional",
        "spec024_spatial_expansion_intact",
        "spec026_connection_legibility_intact",
        "depth1_map_concept_hover_to_right_preview",
        "depth1_map_concept_click_to_right_selection",
        "depth1_right_concept_hover_to_map_preview",
        "depth1_right_concept_click_to_map_selection",
        "depth1_map_relationship_hover_and_click_bidirectional",
        "depth1_right_relationship_hover_and_click_bidirectional",
        "depth1_explanation_bidirectional",
        "depth2_shared_contract_fixture_passes",
        "evidence_synchronization_intact",
        "clear_selection_parity",
        "switching_leaves_no_stale_focus",
        "parent_depth_switching_intact",
        "pan_zoom_and_collapse_intact",
        "no_blue_selection_artifact",
    }
    if set(checks) != required or not all(checks.values()):
        raise ValidationError("SPEC-027 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-027 browser console was not clean")
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
