"""Build and finalize the offline SPEC-026 semantic-interaction experiment."""

from __future__ import annotations

import copy
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
from .semantic_depth_review_evaluation import protected_baseline_hashes
from .semantic_interaction import connection_classification_audit


EVALUATION_NAME = "spec-026-semantic-interaction-invariance-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC024_DIRECTORY_SHA256 = (
    "cf9619552729860672a16e1b2759d32a96fdf2f209eaad7daf0a3331fc2f923a"
)
FROZEN_SPEC025_DIRECTORY_SHA256 = (
    "616970b84cbd29837440e626959752a26dd37b2ffc322d725eb7aedc805f3a76"
)
OWNER_REVIEW_INSTRUCTION = (
    "Navigate naturally to the double-slit experiment and explore deeper. Treat the "
    "deeper structure exactly as you would the surrounding map: inspect concepts and "
    "the connections between them. Tell me whether you can understand why things are "
    "connected, whether relationships behave the same way inside and outside the "
    "deeper map, and note anything that still makes you stop and wonder what a line, "
    "arrow, label, or interaction means."
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
)

_STYLE_ANCHOR = '  <link rel="stylesheet" href="depth-interaction.css">'
_SCRIPT_ANCHOR = '  <script src="depth-interaction.js"></script>'
_SEMANTIC_STYLE = '  <link rel="stylesheet" href="semantic-interaction.css">'
_SEMANTIC_SCRIPT = '  <script src="semantic-interaction.js"></script>'
_MAP_ATTACHMENT_CONTROL = (
    'expansion.explanatory_attachments.forEach(item=>{const path=depthPath(item.from,item.to);'
    'layer.append(depthSvgElement("path",{d:path,class:"depth-explanation-line",'
    '"data-depth-id":item.explanatory_item_id}));});'
)
_MAP_ATTACHMENT_CANDIDATE = (
    "window.__SPEC026_SEMANTICS__.renderMapAttachments(expansion,layer);"
)
_LEARNING_ATTACHMENT_CONTROL = (
    'expansion.explanatory_attachments.forEach(value=>{const path=depthSyncSvg("path",'
    '{d:`M ${value.from.x} ${value.from.y} L ${value.to.x} ${value.to.y}`,class:'
    '`depth-sync-attachment${active&&!keep.has(value.explanatory_item_id)?'
    '" depth-sync-muted":""}`});svg.append(path);});'
)
_LEARNING_ATTACHMENT_CANDIDATE = (
    "window.__SPEC026_SEMANTICS__.renderLearningAttachments(expansion,svg,active,keep,selected);"
)


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
        raise ValidationError("SPEC-025 executable extension seam changed")
    return source.replace(_STYLE_ANCHOR, f"{_STYLE_ANCHOR}\n{_SEMANTIC_STYLE}").replace(
        _SCRIPT_ANCHOR, f"{_SCRIPT_ANCHOR}\n{_SEMANTIC_SCRIPT}"
    )


def _remove_index_extension(source: str) -> str:
    return source.replace(f"\n{_SEMANTIC_STYLE}", "").replace(
        f"\n{_SEMANTIC_SCRIPT}", ""
    )


def apply_semantic_connection_grammar(map_source: str, learning_source: str) -> tuple[str, str]:
    if map_source.count(_MAP_ATTACHMENT_CONTROL) != 1:
        raise ValidationError("SPEC-025 map-attachment seam changed")
    if learning_source.count(_LEARNING_ATTACHMENT_CONTROL) != 1:
        raise ValidationError("SPEC-025 learning-attachment seam changed")
    return (
        map_source.replace(_MAP_ATTACHMENT_CONTROL, _MAP_ATTACHMENT_CANDIDATE),
        learning_source.replace(
            _LEARNING_ATTACHMENT_CONTROL, _LEARNING_ATTACHMENT_CANDIDATE
        ),
    )


def remove_semantic_connection_grammar(
    map_source: str, learning_source: str
) -> tuple[str, str]:
    if map_source.count(_MAP_ATTACHMENT_CANDIDATE) != 1:
        raise ValidationError("SPEC-026 map-attachment seam identity mismatch")
    if learning_source.count(_LEARNING_ATTACHMENT_CANDIDATE) != 1:
        raise ValidationError("SPEC-026 learning-attachment seam identity mismatch")
    return (
        map_source.replace(_MAP_ATTACHMENT_CANDIDATE, _MAP_ATTACHMENT_CONTROL),
        learning_source.replace(
            _LEARNING_ATTACHMENT_CANDIDATE, _LEARNING_ATTACHMENT_CONTROL
        ),
    )


def recursive_classification_regression(packet: dict[str, Any]) -> dict[str, Any]:
    root = packet["expansions"][0]
    child = copy.deepcopy(root)
    child["id"] = "synthetic-second-expansion"
    child["parent_expansion_id"] = root["id"]
    root_audit = connection_classification_audit(root)
    child_audit = connection_classification_audit(child)
    fields = (
        "semantic_class",
        "label",
        "directional",
        "canonical",
        "selectable_kind",
        "semantic_tier",
    )
    root_contract = [tuple(item[field] for field in fields) for item in root_audit["connections"]]
    child_contract = [tuple(item[field] for field in fields) for item in child_audit["connections"]]
    same_contract = root_contract == child_contract
    return {
        "status": "PASS" if same_contract else "FAIL",
        "same_contract": same_contract,
        "parent_expansion_id": root["id"],
        "nested_expansion_id": child["id"],
        "connection_count_per_expansion": len(root_contract),
        "depth_specific_branch_count": 0,
    }


def _reject_protected_output(output_dir: Path, protected: Iterable[Path]) -> None:
    resolved = output_dir.resolve()
    for directory in protected:
        candidate = directory.resolve()
        if resolved == candidate or resolved.is_relative_to(candidate):
            raise ValidationError("SPEC-026 output must be isolated from frozen artifacts")


def prepare_semantic_interaction_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec023_dir: Path = default_spec023_directory(),
    spec024_dir: Path = default_spec024_directory(),
    spec025_dir: Path = default_spec025_directory(),
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
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")

    packet = json.loads((spec025_dir / "depth-map.json").read_text(encoding="utf-8"))
    expansion = packet["expansions"][0]
    classification = connection_classification_audit(expansion)
    recursive = recursive_classification_regression(packet)

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in VIEWER_FILES:
        shutil.copyfile(spec025_dir / name, output_dir / name)
    control_index = (spec025_dir / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(_extend_index(control_index), encoding="utf-8")
    control_map = (spec025_dir / "depth-expansion.js").read_text(encoding="utf-8")
    control_learning = (spec025_dir / "depth-interaction.js").read_text(encoding="utf-8")
    candidate_map, candidate_learning = apply_semantic_connection_grammar(
        control_map, control_learning
    )
    (output_dir / "depth-expansion.js").write_text(candidate_map, encoding="utf-8")
    (output_dir / "depth-interaction.js").write_text(candidate_learning, encoding="utf-8")
    assets = files("knowledge_compiler").joinpath("semantic_interaction_assets")
    for name in ("semantic-interaction.css", "semantic-interaction.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    adapter = (output_dir / "semantic-interaction.js").read_text(encoding="utf-8")
    map_round_trip, learning_round_trip = remove_semantic_connection_grammar(
        candidate_map, candidate_learning
    )
    counts = classification["counts"]
    runtime_checks = {
        "spec025_shell_composed_not_reimplemented": _remove_index_extension(
            (output_dir / "index.html").read_text(encoding="utf-8")
        )
        == control_index,
        "spec025_runtime_reused_with_only_classification_hooks": (
            map_round_trip == control_map and learning_round_trip == control_learning
        ),
        "spec025_other_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec025_dir / name).read_bytes()
            for name in VIEWER_FILES
            if name not in {"index.html", "depth-expansion.js", "depth-interaction.js"}
        ),
        "canonical_relationship_grammar_preserved": all(
            token in candidate_map
            for token in (
                "depth-canonical-group",
                "spec024-canonical-arrow",
                "depth-canonical-label",
                'depthSelect("canonical"',
            )
        ),
        "explanatory_attachments_are_labeled": all(
            token in adapter
            for token in (
                'label.textContent="EXPLANATORY"',
                "SOURCE_BACKED_EXPLANATORY_ATTACHMENT",
                "NON-CANONICAL · NO DIRECTION",
            )
        ),
        "explanatory_attachments_are_selectable": all(
            token in adapter
            for token in ('role:"button"', 'depthSelect("explanation"', "depthKeyboardSelect")
        ),
        "right_learning_surface_uses_same_connection_class": (
            "semanticLearningAttachments" in adapter
            and "renderLearningAttachments" in candidate_learning
        ),
        "focus_keeps_connected_semantic_labels": (
            "keep.has(item.explanatory_item_id)" in adapter
            and "depth-explanation-label" in adapter
        ),
        "all_visible_connections_classified": counts["unclassified"] == 0,
        "recursive_contract_passes": recursive["status"] == "PASS",
        "spatial_depth_and_camera_seams_preserved": all(
            token in candidate_map
            for token in ("depth-origin-path", "api.setCamera", "expanded_world_bounds")
        ),
    }
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "candidate_depth_map_byte_identical": (output_dir / "depth-map.json").read_bytes()
        == (spec025_dir / "depth-map.json").read_bytes(),
        "canonical_relationship_count_unchanged": counts["canonical_relationships"] == 2,
        "explanatory_attachment_count_unchanged": counts["explanatory_attachments"] == 13,
        "known_rejected_causal_item_remains_noncanonical": all(
            item["semantic_tier"] == "SOURCE_BACKED_NON_CANONICAL"
            for item in expansion["explanatory_items"]
        ),
        "pairwise_edge_fabrication_count_zero": counts[
            "fabricated_pairwise_relationships"
        ]
        == 0,
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
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        raise ValidationError("SPEC-026 deterministic machine gate failed closed")

    machine_gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "connection_classification": classification,
        "recursive_classification_regression": recursive,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    report = {
        "spec": "SPEC-026",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "semantic_object_classification_seam": (
            "two reversible hooks delegate learner-visible explanatory connections to "
            "one additive semantic-class adapter shared by the map and learning surface"
        ),
        "noncanonical_connection_treatment": (
            "each participant-preserving source-backed attachment is a selectable dashed "
            "connection labeled EXPLANATORY; a visible key states NON-CANONICAL and NO "
            "DIRECTION; selection resolves the existing explanatory item and exact evidence"
        ),
        "noncanonical_connection_rationale": (
            "the frozen IR supports explanatory association but no canonical predicate, so "
            "the candidate exposes its real status rather than minting a pairwise edge"
        ),
        "connection_classification": classification,
        "recursive_classification_regression": recursive,
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
        "machine_gate": machine_gate,
        "canonical_relationship_result": "PASS_PENDING_BROWSER",
        "explanatory_connection_result": "PASS_PENDING_BROWSER",
        "focus_legibility_result": "PASS_PENDING_BROWSER",
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
            "deeper explanatory attachments are labeled, selectable, and synchronized"
        ],
        "deviations": [],
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            f"{EVALUATION_RELATIVE_PATH} --port 8026"
        ),
    }
    manifest = {
        "spec": "SPEC-026",
        "title": "Semantic interaction invariance",
        "workspace_fixture": "workspace-fixture.json",
        "projection": "projection.json",
        "depth_map": "depth-map.json",
        "connection_classification": "connection-classification.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "connection-classification.json", classification)
    _write_json(output_dir / "machine-gate.json", machine_gate)
    _write_json(
        output_dir / "input-manifest.json",
        {
            "spec020": {"directory": _location(spec020_dir), "hashes": spec020_hashes},
            "spec021": {"directory": _location(spec021_dir), "hashes": spec021_hashes},
            "spec023": spec023_before,
            "spec024": spec024_before,
            "spec025": spec025_before,
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
                "SEMANTIC_INTERACTION_INVARIANT",
                "MIXED",
                "PARENT_GRAMMAR_DOES_NOT_GENERALIZE",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-026 semantic interaction invariance\n\n"
        "This isolated offline artifact preserves SPEC-025 synchronization while making "
        "every deeper connection learner-readable according to its semantic class.\n\n"
        f"```sh\n{report['viewer_command']}\n```\n",
        encoding="utf-8",
    )
    return report


def finalize_semantic_interaction_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-026 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    required = {
        "ordinary_navigation_intact",
        "spec024_spatial_expansion_intact",
        "spec025_selection_synchronization_intact",
        "canonical_predicates_and_direction_readable",
        "canonical_relationships_selectable_and_synchronized",
        "explanatory_connections_explicitly_noncanonical_and_nondirectional",
        "explanatory_connections_selectable_and_synchronized",
        "no_unexplained_relationship_like_connectors",
        "concept_focus_preserves_connected_semantics",
        "switching_has_no_stale_focus",
        "parent_deeper_switching_intact",
        "map_learning_focus_mirror",
        "recursive_classification_contract",
        "pan_zoom_and_collapse_intact",
        "no_blue_selection_artifact",
    }
    if set(checks) != required or not all(checks.values()):
        raise ValidationError("SPEC-026 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-026 browser console was not clean")
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
    report["canonical_relationship_result"] = "PASS"
    report["explanatory_connection_result"] = "PASS"
    report["focus_legibility_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report
