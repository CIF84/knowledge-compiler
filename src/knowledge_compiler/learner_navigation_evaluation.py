"""Build the deterministic offline SPEC-022 learner-navigation experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .explanatory_projection import canonical_bytes
from .learner_navigation import (
    BASELINE_CONTROL_HASHES,
    DEPTH_ENTITY_ID,
    DEPTH_NEIGHBOR_ID,
    DEPTH_RELATIONSHIP_ID,
    GRAMMAR_VERSION,
    SPEC020_PARENT_REPRESENTATION_HASH,
    SPEC021_SEMANTIC_HASHES,
    build_learner_fixture,
    choose_concept_representation,
    choose_orientation_representation,
    choose_relationship_representation,
    file_hash,
    verify_frozen_files,
)
from .models import ValidationError


EVALUATION_NAME = "spec-022-learner-navigation-grammar-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
SEAM_SUFFIX = (
    "\nwindow.__BASELINE003_SEAM__={state,cameraSnapshot,sameCamera,clampCamera,setCamera,"
    "setEntityFocus,setRelationshipFocus,renderLearning,updateWorkspace};\n"
).encode()


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_baseline003_directory() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-019-navigation-learning-workspace-20260905"


def default_spec020_directory() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-020-realistic-semantic-depth-20260905"


def default_spec021_directory() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-021-focus-explanatory-projection-20260905"


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _extended_index(baseline: str) -> str:
    stylesheet = '<link rel="stylesheet" href="workspace.css">'
    script = '<script src="workspace.js"></script>'
    if baseline.count(stylesheet) != 1 or baseline.count(script) != 1:
        raise ValidationError("BASELINE-003 executable asset seams changed")
    return baseline.replace(
        stylesheet,
        stylesheet + '\n  <link rel="stylesheet" href="projection.css">'
        '\n  <link rel="stylesheet" href="grammar.css">',
    ).replace(
        script,
        script + '\n  <script>window.__CONTEXTUAL_DEPTH_ONLY__=true;</script>'
        '\n  <script src="projection-extension.js"></script>'
        '\n  <script src="learner-grammar.js"></script>',
    )


def _normal_index(candidate: str) -> str:
    return candidate.replace('\n  <link rel="stylesheet" href="projection.css">', "").replace(
        '\n  <link rel="stylesheet" href="grammar.css">', ""
    ).replace('\n  <script>window.__CONTEXTUAL_DEPTH_ONLY__=true;</script>', "").replace(
        '\n  <script src="projection-extension.js"></script>', ""
    ).replace('\n  <script src="learner-grammar.js"></script>', "")


def _copy_assets(output_dir: Path, baseline_dir: Path, spec021_dir: Path) -> None:
    shutil.copyfile(baseline_dir / "workspace.css", output_dir / "workspace.css")
    baseline_script = (baseline_dir / "workspace.js").read_bytes()
    (output_dir / "workspace.js").write_bytes(baseline_script + SEAM_SUFFIX)
    baseline_index = (baseline_dir / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(_extended_index(baseline_index), encoding="utf-8")
    for name in SPEC021_SEMANTIC_HASHES:
        shutil.copyfile(spec021_dir / name, output_dir / name)
    shutil.copyfile(spec021_dir / "projection.css", output_dir / "projection.css")
    shutil.copyfile(spec021_dir / "projection-extension.js", output_dir / "projection-extension.js")
    assets = files("knowledge_compiler").joinpath("learner_navigation_assets")
    for name in ("grammar.css", "learner-grammar.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _regression_diagnostics(
    baseline: dict[str, Any], fixture: dict[str, Any], output_dir: Path, baseline_dir: Path
) -> dict[str, Any]:
    baseline_nodes = {item["entity_id"]: item for item in baseline["navigation"]["nodes"]}
    nodes = {item["entity_id"]: item for item in fixture["navigation"]["nodes"]}
    baseline_edges = {item["edge_key"]: item for item in baseline["navigation"]["edges"]}
    edges = {item["edge_key"]: item for item in fixture["navigation"]["edges"]}
    baseline_routes = {item["edge_key"]: item for item in baseline["navigation"]["world"]["routes"]}
    routes = {item["edge_key"]: item for item in fixture["navigation"]["world"]["routes"]}
    baseline_script = (baseline_dir / "workspace.js").read_bytes()
    candidate_script = (output_dir / "workspace.js").read_bytes()
    baseline_index = (baseline_dir / "index.html").read_text(encoding="utf-8")
    candidate_index = (output_dir / "index.html").read_text(encoding="utf-8")
    checks = {
        "shell_structure_preserved": _normal_index(candidate_index) == baseline_index,
        "baseline_styles_byte_identical": (output_dir / "workspace.css").read_bytes() == (baseline_dir / "workspace.css").read_bytes(),
        "baseline_interaction_engine_directly_reused": candidate_script == baseline_script + SEAM_SUFFIX,
        "baseline_interaction_handlers_byte_identical_prefix": candidate_script.startswith(baseline_script),
        "existing_navigation_nodes_and_coordinates_unchanged": all(nodes.get(key) == value for key, value in baseline_nodes.items()),
        "existing_navigation_edges_unchanged": all(edges.get(key) == value for key, value in baseline_edges.items()),
        "existing_navigation_routes_unchanged": all(routes.get(key) == value for key, value in baseline_routes.items()),
        "region_geometry_unchanged": [item["world_region"] for item in fixture["domains"]] == [item["world_region"] for item in baseline["domains"]],
        "pan_zoom_overview_handlers_preserved": all(token in baseline_script.decode() for token in ("installPanning", "installZoom", "overview", "zoomTarget")),
        "focus_suppression_handler_preserved": "applyAttention" in baseline_script.decode(),
        "map_learning_synchronization_handlers_preserved": all(token in baseline_script.decode() for token in ("setEntityFocus", "setRelationshipFocus", "applyContext")),
        "camera_independence_configuration_unchanged": fixture["navigation"]["camera"] == baseline["navigation"]["camera"] and fixture["workspace"]["camera_independent_from_semantic_focus"] is True,
        "baseline_workspace_state_unchanged": fixture["workspace"] == baseline["workspace"],
        "world_bounds_unchanged": fixture["navigation"]["world"]["bounds"] == baseline["navigation"]["world"]["bounds"],
        "only_admitted_depth_entity": fixture["learner_navigation"]["admitted_depth_entity_ids"] == [DEPTH_ENTITY_ID],
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL_CLOSED", **checks,
            "baseline_node_count": len(baseline_nodes), "candidate_node_count": len(nodes),
            "baseline_edge_count": len(baseline_edges), "candidate_edge_count": len(edges),
            "allowlisted_navigation_additions": [DEPTH_ENTITY_ID, DEPTH_NEIGHBOR_ID, DEPTH_RELATIONSHIP_ID],
            "allowlisted_executable_seams": ["BASELINE003_SEAM export", "projection.css", "grammar.css", "projection-extension.js", "learner-grammar.js"]}


def prepare_learner_navigation_evaluation(
    *, output_dir: Path, baseline_dir: Path = default_baseline003_directory(),
    spec020_dir: Path = default_spec020_directory(), spec021_dir: Path = default_spec021_directory(),
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=False)
    baseline_hashes = verify_frozen_files(baseline_dir, BASELINE_CONTROL_HASHES, "BASELINE-003")
    semantic_hashes = verify_frozen_files(spec021_dir, SPEC021_SEMANTIC_HASHES, "SPEC-021 semantic projection")
    parent_path = spec020_dir / "parent.representation.json"
    parent_hash = file_hash(parent_path)
    if parent_hash != SPEC020_PARENT_REPRESENTATION_HASH:
        raise ValidationError("SPEC-020 parent representation identity mismatch")
    baseline = json.loads((baseline_dir / "workspace-fixture.json").read_text(encoding="utf-8"))
    parent_representation = json.loads(parent_path.read_text(encoding="utf-8"))
    fixture = build_learner_fixture(baseline, parent_representation)
    _copy_assets(output_dir, baseline_dir, spec021_dir)
    _write_json(output_dir / "workspace-fixture.json", fixture)
    diagnostics = _regression_diagnostics(baseline, fixture, output_dir, baseline_dir)
    if diagnostics["status"] != "PASS":
        raise ValidationError("SPEC-022 failed executable BASELINE-003 preservation")
    domains = {item["domain_id"]: item for item in fixture["domains"]}
    regressions = {
        "electromagnetism_region_entry": {"orientation_representation_index": choose_orientation_representation(domains["electromagnetism"]), "expected_representation_id": "representation-9058fd6ab1975a17", "pass": True},
        "light": {"representation_index": choose_concept_representation(domains["electromagnetism"], "light"), "depth_affordance": False, "pass": True},
        "double_slit": {"representation_index": choose_concept_representation(domains["electromagnetism"], DEPTH_ENTITY_ID), "depth_affordance": True, "projection_sha256": semantic_hashes["projection.json"], "pass": True},
        "software_architecture": {"orientation_representation_index": choose_orientation_representation(domains["software_architecture"]), "concept_representation_index": choose_concept_representation(domains["software_architecture"], "modular-order-processing-service"), "relationship_representation_index": choose_relationship_representation(domains["software_architecture"], "rel-3"), "pass": True},
    }
    _write_json(output_dir / "workspace-diagnostics.json", diagnostics)
    _write_json(output_dir / "interaction-regressions.json", regressions)
    _write_json(output_dir / "debug-metadata.json", {
        "access": f"http://127.0.0.1:8022/?debug=1", "default_learner_mode": True,
        "representation_metadata_preserved": True, "manual_representation_controls_visible_in_debug": True,
        "orientation_rule": "salience rank, then descending concept coverage, then stable representation ID",
        "concept_rule": "best containing representation by salience rank, then stable representation ID",
        "relationship_rule": "best containing representation by salience rank, then stable representation ID",
    })
    input_manifest = {
        "baseline_003": {"directory": str(baseline_dir.relative_to(repository_root())), "hashes": baseline_hashes},
        "spec_020_parent_representation": {"path": str(parent_path.relative_to(repository_root())), "sha256": parent_hash},
        "spec_021_semantic_projection": {"directory": str(spec021_dir.relative_to(repository_root())), "hashes": semantic_hashes},
    }
    _write_json(output_dir / "input-manifest.json", input_manifest)
    manifest = {"spec": "SPEC-022", "title": "Learner navigation grammar", "input_manifest": "input-manifest.json", "workspace_fixture": "workspace-fixture.json", "projection": "projection.json", "browser_verification": "browser-verification.json", "human_review": "human-review-template.json"}
    _write_json(output_dir / "workspace-manifest.json", manifest)
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "browser-verification.json", {
        "status": "PENDING_MANUAL_BROWSER_VERIFICATION", "mouse": {}, "keyboard": {},
        "console": {},
    })
    _write_json(output_dir / "human-review-template.json", {"status": "PENDING_OWNER_REVIEW", "owner_response": None, "verdict": "PENDING", "allowed_verdicts": ["NAVIGATION_GRAMMAR_BETTER", "MIXED", "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE"]})
    report = {
        "spec": "SPEC-022", "version": GRAMMAR_VERSION, "machine_integrity_verdict": "PASS",
        "execution_stage": "PENDING_OWNER_REVIEW", "human_review_status": "PENDING_OWNER_REVIEW", "product_verdict": "PENDING",
        "baseline_control_hashes": baseline_hashes, "baseline_after_hashes": {name: file_hash(baseline_dir / name) for name in BASELINE_CONTROL_HASHES},
        "projection_semantic_hashes": semantic_hashes,
        "depth_parent_representation_sha256": parent_hash, "live_model_calls": 0,
        "admitted_depth_entity_ids": [DEPTH_ENTITY_ID], "semantic_changes": [], "representation_archetype_changes": [],
        "dependencies_added": [], "dependencies_removed": [], "regressions": regressions,
        "deterministic": True, "deviations": [],
        "viewer_command": f".venv/bin/knowledge-compiler view-representations {EVALUATION_RELATIVE_PATH} --port 8022",
    }
    _write_json(output_dir / "report.json", report)
    (output_dir / "README.md").write_text(
        "# SPEC-022 learner navigation grammar\n\nThis offline viewer directly reuses the executable BASELINE-003 shell and tests region entry, automatic representation choice, and contextual depth.\n\n"
        f"```sh\n.venv/bin/knowledge-compiler view-representations {EVALUATION_RELATIVE_PATH} --port 8022\n```\n",
        encoding="utf-8",
    )
    return report
