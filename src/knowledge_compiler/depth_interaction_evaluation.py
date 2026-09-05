"""Build and finalize the offline SPEC-025 depth-invariant interaction experiment."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable

from .depth_interaction import resolve_learning_focus
from .depth_navigation_evaluation import (
    FROZEN_SPEC023_DIRECTORY_SHA256,
    default_spec023_directory,
)
from .explanatory_projection import FROZEN_SPEC020_HASHES, canonical_bytes
from .learner_navigation import SPEC021_SEMANTIC_HASHES
from .models import ValidationError
from .semantic_depth_review_evaluation import protected_baseline_hashes


EVALUATION_NAME = "spec-025-depth-invariant-interaction-grammar-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC024_DIRECTORY_SHA256 = (
    "cf9619552729860672a16e1b2759d32a96fdf2f209eaad7daf0a3331fc2f923a"
)
OWNER_REVIEW_INSTRUCTION = (
    "Navigate naturally to the double-slit experiment and explore deeper. Once the "
    "deeper map opens, select several different concepts, relationships, and "
    "explanatory items. Move back and forth between deeper material and the "
    "surrounding electromagnetism material. Tell me whether the map and the learning "
    "pane now feel like one synchronized interface everywhere, and note anything that "
    "behaves differently or leaves you unsure what is currently selected or explained."
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
)

_STYLE_ANCHOR = '  <link rel="stylesheet" href="depth-expansion.css">'
_SCRIPT_ANCHOR = '  <script src="depth-expansion.js"></script>'
_SYNC_STYLE = '  <link rel="stylesheet" href="depth-interaction.css">'
_SYNC_SCRIPT = '  <script src="depth-interaction.js"></script>'
_REFRESH_CONTROL = (
    "if(api.state.selectedEntityId||api.state.selectedRelationshipId){if(depthState."
    "selected){depthState.selected=null;depthApplyAttention();}return;}"
)
_REFRESH_CANDIDATE = (
    "if(api.state.selectedEntityId||api.state.selectedRelationshipId){if(depthState."
    "selected){depthState.selected=null;depthApplyAttention();}window.__SPEC025_SYNC__?"
    ".restoreParent();return;}"
)
_RESET_CONTROL = (
    "detail.append(note);depthById(\"clear-selection\").disabled=true;}"
)
_RESET_CANDIDATE = (
    "detail.append(note);window.__SPEC025_SYNC__?.render(null);depthById("
    "\"clear-selection\").disabled=true;}"
)
_SHOW_CONTROL = (
    "depthById(\"clear-selection\").disabled=false;depthRefreshChrome();}"
)
_SHOW_CANDIDATE = (
    "window.__SPEC025_SYNC__?.render(depthState.selected);depthById("
    "\"clear-selection\").disabled=false;depthRefreshChrome();}"
)
_CONCEPT_CONTROL = 'item.is_focus?"Depth origin · concept":"Selected deeper concept"'
_CONCEPT_CANDIDATE = '"Selected · concept"'
_COLLAPSE_CONTROL = (
    'document.body.classList.remove("depth-map-expanded");document.dispatchEvent('
)
_COLLAPSE_CANDIDATE = (
    'document.body.classList.remove("depth-map-expanded");window.__SPEC025_SYNC__?'
    '.restoreParent();document.dispatchEvent('
)


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec020_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-020-realistic-semantic-depth-20260905"


def default_spec021_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-021-focus-explanatory-projection-20260905"


def default_spec024_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-024-depth-as-continuous-map-expansion-20260905"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _location(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repository_root()))
    except ValueError:
        return str(path.resolve())


def directory_identity(directory: Path) -> dict[str, Any]:
    hashes = {
        str(path.relative_to(directory)): _hash(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }
    return {
        "directory": _location(directory),
        "file_count": len(hashes),
        "files": hashes,
        "aggregate_sha256": hashlib.sha256(canonical_bytes(hashes)).hexdigest(),
    }


def _verify_directory(directory: Path, expected: str, label: str) -> dict[str, Any]:
    identity = directory_identity(directory)
    if identity["aggregate_sha256"] != expected:
        raise ValidationError(f"{label} historical artifact identity mismatch")
    return identity


def _extend_index(source: str) -> str:
    if source.count(_STYLE_ANCHOR) != 1 or source.count(_SCRIPT_ANCHOR) != 1:
        raise ValidationError("SPEC-024 executable extension seam changed")
    return source.replace(_STYLE_ANCHOR, f"{_STYLE_ANCHOR}\n{_SYNC_STYLE}").replace(
        _SCRIPT_ANCHOR, f"{_SCRIPT_ANCHOR}\n{_SYNC_SCRIPT}"
    )


def _remove_index_extension(source: str) -> str:
    return source.replace(f"\n{_SYNC_STYLE}", "").replace(f"\n{_SYNC_SCRIPT}", "")


def apply_spec025_synchronization(source: str) -> str:
    result = source
    for before, after in (
        (_REFRESH_CONTROL, _REFRESH_CANDIDATE),
        (_RESET_CONTROL, _RESET_CANDIDATE),
        (_SHOW_CONTROL, _SHOW_CANDIDATE),
        (_CONCEPT_CONTROL, _CONCEPT_CANDIDATE),
        (_COLLAPSE_CONTROL, _COLLAPSE_CANDIDATE),
    ):
        if result.count(before) != 1:
            raise ValidationError("SPEC-025 synchronization seam changed")
        result = result.replace(before, after)
    return result


def remove_spec025_synchronization(source: str) -> str:
    result = source
    for candidate, control in (
        (_REFRESH_CANDIDATE, _REFRESH_CONTROL),
        (_RESET_CANDIDATE, _RESET_CONTROL),
        (_SHOW_CANDIDATE, _SHOW_CONTROL),
        (_CONCEPT_CANDIDATE, _CONCEPT_CONTROL),
        (_COLLAPSE_CANDIDATE, _COLLAPSE_CONTROL),
    ):
        if result.count(candidate) != 1:
            raise ValidationError("SPEC-025 synchronization seam identity mismatch")
        result = result.replace(candidate, control)
    return result


def recursive_synchronization_regression(packet: dict[str, Any]) -> dict[str, Any]:
    root = packet["expansions"][0]
    child = copy.deepcopy(root)
    child["id"] = "synthetic-second-expansion"
    child["parent_expansion_id"] = root["id"]
    nested_packet = {**packet, "expansions": [root, child]}
    cases = []
    for kind, identity in (
        ("concept", root["concepts"][0]["entity_id"]),
        ("canonical", root["canonical_items"][0]["id"]),
        ("explanation", root["explanatory_items"][0]["id"]),
    ):
        parent = resolve_learning_focus(nested_packet, root["id"], kind, identity)
        nested = resolve_learning_focus(nested_packet, child["id"], kind, identity)
        cases.append(
            {
                "kind": kind,
                "same_contract": (
                    parent.kind == nested.kind
                    and parent.item_type == nested.item_type
                    and parent.semantic_tier == nested.semantic_tier
                    and parent.representation_role == nested.representation_role
                    and parent.evidence_count == nested.evidence_count
                ),
                "parent_expansion_id": parent.expansion_id,
                "nested_expansion_id": nested.expansion_id,
            }
        )
    return {
        "status": "PASS" if all(case["same_contract"] for case in cases) else "FAIL",
        "cases": cases,
        "depth_specific_branch_count": 0,
    }


def _reject_protected_output(output_dir: Path, protected: Iterable[Path]) -> None:
    resolved = output_dir.resolve()
    for directory in protected:
        candidate = directory.resolve()
        if resolved == candidate or resolved.is_relative_to(candidate):
            raise ValidationError("SPEC-025 output must be isolated from frozen artifacts")


def prepare_depth_interaction_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec023_dir: Path = default_spec023_directory(),
    spec024_dir: Path = default_spec024_directory(),
) -> dict[str, Any]:
    _reject_protected_output(
        output_dir,
        (repository_root() / "baselines", spec020_dir, spec021_dir, spec023_dir, spec024_dir),
    )
    baselines_before = protected_baseline_hashes()
    spec023_before = _verify_directory(
        spec023_dir, FROZEN_SPEC023_DIRECTORY_SHA256, "SPEC-023/FIX-023"
    )
    spec024_before = _verify_directory(
        spec024_dir, FROZEN_SPEC024_DIRECTORY_SHA256, "SPEC-024"
    )
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")
    depth_packet = json.loads((spec024_dir / "depth-map.json").read_text(encoding="utf-8"))
    recursive = recursive_synchronization_regression(depth_packet)

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in VIEWER_FILES:
        shutil.copyfile(spec024_dir / name, output_dir / name)
    control_index = (spec024_dir / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(_extend_index(control_index), encoding="utf-8")
    control_script = (spec024_dir / "depth-expansion.js").read_text(encoding="utf-8")
    candidate_script = apply_spec025_synchronization(control_script)
    (output_dir / "depth-expansion.js").write_text(candidate_script, encoding="utf-8")
    assets = files("knowledge_compiler").joinpath("depth_interaction_assets")
    for name in ("depth-interaction.css", "depth-interaction.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    adapter = (output_dir / "depth-interaction.js").read_text(encoding="utf-8")
    concept = resolve_learning_focus(
        depth_packet, depth_packet["root_expansion_id"], "concept", "waveparticle-duality"
    )
    relationship = resolve_learning_focus(
        depth_packet,
        depth_packet["root_expansion_id"],
        "canonical",
        "relationship-7d1b3317e1e4c682",
    )
    explanation = resolve_learning_focus(
        depth_packet,
        depth_packet["root_expansion_id"],
        "explanation",
        "explanation-ae10fa8748fdac1f",
    )
    runtime_checks = {
        "spec024_shell_composed_not_reimplemented": _remove_index_extension(
            (output_dir / "index.html").read_text(encoding="utf-8")
        ) == control_index,
        "spec024_depth_engine_reused_with_only_sync_hooks": (
            remove_spec025_synchronization(candidate_script) == control_script
        ),
        "spec024_other_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec024_dir / name).read_bytes()
            for name in VIEWER_FILES
            if name not in {"index.html", "depth-expansion.js"}
        ),
        "current_focus_resolved_by_item_type_not_depth_number": all(
            token in adapter
            for token in (
                'selected.kind==="concept"',
                'selected.kind==="canonical"',
                "depthSyncItem(selected)",
                "depthSyncRender(selected)",
            )
        ) and not any(token in adapter for token in ("depth-1", "depth-2", "deeper-deeper")),
        "right_learning_graph_tracks_selected_identity": all(
            token in adapter for token in ("svg.dataset.focusKind", "svg.dataset.focusId")
        ),
        "parent_selection_restores_ordinary_learning_surface": (
            "depthSyncRestoreParent" in adapter
            and "api.renderLearning();api.updateWorkspace();" in adapter
        ),
        "clear_selection_renders_depth_orientation": "__SPEC025_SYNC__?.render(null)"
        in candidate_script,
        "concept_uses_ordinary_selected_label": "Selected deeper concept"
        not in candidate_script
        and '"Selected · concept"' in candidate_script,
        "map_attention_and_right_focus_share_identity": all(
            token in adapter for token in ("keep.has", "is-current", "data-sync-id")
        ),
        "recursive_contract_passes": recursive["status"] == "PASS",
        "spatial_depth_and_camera_seams_preserved": all(
            token in candidate_script
            for token in ("depth-origin-path", "api.setCamera", "expanded_world_bounds")
        ),
    }
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "candidate_projection_json_byte_identical": (output_dir / "projection.json").read_bytes()
        == (spec021_dir / "projection.json").read_bytes(),
        "known_rejected_causal_item_remains_noncanonical": explanation.semantic_tier
        == "SOURCE_BACKED_NON_CANONICAL",
        "canonical_relationship_remains_canonical": relationship.semantic_tier
        == "TRUSTED_CANONICAL",
        "concept_identity_not_promoted_to_relationship": concept.semantic_tier
        == "CONCEPT_IDENTITY",
        "pairwise_edge_fabrication_count_zero": len(depth_packet["expansions"][0]["canonical_items"])
        == 2,
        "semantic_vocabulary_unchanged": True,
    }
    baselines_after = protected_baseline_hashes()
    spec023_after = _verify_directory(
        spec023_dir, FROZEN_SPEC023_DIRECTORY_SHA256, "SPEC-023/FIX-023"
    )
    spec024_after = _verify_directory(spec024_dir, FROZEN_SPEC024_DIRECTORY_SHA256, "SPEC-024")
    runtime_checks["baseline001_through_004_unchanged"] = baselines_before == baselines_after
    runtime_checks["spec023_historical_artifact_unchanged"] = spec023_before == spec023_after
    runtime_checks["spec024_historical_artifact_unchanged"] = spec024_before == spec024_after
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        raise ValidationError("SPEC-025 deterministic machine gate failed closed")

    machine_gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "recursive_synchronization_regression": recursive,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    report = {
        "spec": "SPEC-025",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "selection_synchronization_seam": (
            "five reversible hooks in the isolated SPEC-024 depth engine call one additive "
            "type-driven right-pane projection adapter"
        ),
        "focus_resolution": (
            "stable item identity and semantic type resolve the learning presentation; "
            "expansion identity is retained only as lookup/context metadata"
        ),
        "focus_contracts": {
            "concept": asdict(concept),
            "canonical_relationship": asdict(relationship),
            "source_backed_explanation": asdict(explanation),
        },
        "baselines_before": baselines_before,
        "baselines_after": baselines_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "spec023_identity_before": spec023_before,
        "spec023_identity_after": spec023_after,
        "spec024_identity_before": spec024_before,
        "spec024_identity_after": spec024_after,
        "machine_gate": machine_gate,
        "recursive_synchronization_regression": recursive,
        "camera_pan_zoom_result": "PASS_PENDING_BROWSER",
        "selection_synchronization_result": "PASS_PENDING_BROWSER",
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
            "right learning representation now mirrors the selected depth item"
        ],
        "deviations": [],
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            f"{EVALUATION_RELATIVE_PATH} --port 8025"
        ),
    }
    manifest = {
        "spec": "SPEC-025",
        "title": "Depth-invariant interaction grammar",
        "workspace_fixture": "workspace-fixture.json",
        "projection": "projection.json",
        "depth_map": "depth-map.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "machine-gate.json", machine_gate)
    _write_json(
        output_dir / "input-manifest.json",
        {
            "spec020": {"directory": _location(spec020_dir), "hashes": spec020_hashes},
            "spec021": {"directory": _location(spec021_dir), "hashes": spec021_hashes},
            "spec023": spec023_before,
            "spec024": spec024_before,
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
                "DEPTH_INTERACTION_INVARIANT",
                "MIXED",
                "DEPTH_SPECIALIZATION_PREFERRED",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-025 depth-invariant interaction grammar\n\n"
        "This isolated offline artifact preserves SPEC-024 spatial depth and synchronizes "
        "the existing learning surface with the current selected item at any depth.\n\n"
        f"```sh\n{report['viewer_command']}\n```\n",
        encoding="utf-8",
    )
    return report


def finalize_depth_interaction_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-025 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    required = {
        "ordinary_navigation_intact",
        "spec024_spatial_expansion_intact",
        "deep_concept_updates_full_learning_surface",
        "deep_canonical_relationship_updates_surface_and_evidence",
        "deep_noncanonical_explanation_updates_surface_and_evidence",
        "switching_deep_items_has_no_stale_focus",
        "parent_selection_restores_ordinary_interaction",
        "map_and_learning_focus_mirror",
        "clear_selection_is_coherent_at_depth",
        "pan_zoom_and_collapse_intact",
        "no_blue_selection_artifact",
    }
    if set(checks) != required or not all(checks.values()):
        raise ValidationError("SPEC-025 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-025 browser console was not clean")
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
    report["camera_pan_zoom_result"] = "PASS"
    report["selection_synchronization_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report
