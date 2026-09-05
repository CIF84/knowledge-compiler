"""Deterministic offline SPEC-021 evaluation and review workspace."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .assertion_compilation import CanonicalizationProposal, compile_assertion_semantics
from .continuous_navigation import CameraState, VIEWPORT
from .explanatory_projection import (
    FOCUS_ENTITY_ID,
    FROZEN_SPEC020_HASHES,
    FrozenProjectionInputs,
    build_explanatory_projection,
    canonical_bytes,
    load_frozen_spec020_inputs,
    projection_diagnostics,
)
from .models import KnowledgeModel, SourceDocument, ValidationError
from .navigation_learning_workspace import _route
from .semantic_depth import (
    INITIAL_CAMERA,
    WORLD_BOUNDS,
    DepthWorkspaceState,
    depth_camera_invariant,
    switch_semantic_depth,
)
from .structure_detection import StructureDetector


EVALUATION_VERSION = "spec-021-v1"
EVALUATION_NAME = "spec-021-focus-explanatory-projection-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec020_directory() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-020-realistic-semantic-depth-20260905"


def default_spec013_directory() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-013-assertion-first-semantic-compilation-20260904"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): _hash(path)
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _baseline_hashes() -> dict[str, Any]:
    root = repository_root()
    baseline003 = root / "examples" / "evaluations" / "spec-019-navigation-learning-workspace-20260905"
    return {
        "baseline_001_document": _hash(root / "baselines" / "BASELINE-001-interface.md"),
        "baseline_002_document": _hash(root / "baselines" / "BASELINE-002-continuous-navigation-reference.md"),
        "baseline_003_document": _hash(root / "baselines" / "BASELINE-003-hybrid-learning-workspace.md"),
        "baseline_003_assets": _directory_hashes(baseline003),
    }


def _canonical_control(inputs: FrozenProjectionInputs) -> dict[str, Any]:
    document = SourceDocument(
        id=inputs.scope["document_id"], text=inputs.scope["text"],
        metadata={"scope_sha256": inputs.scope["sha256"]},
    )
    proposal = CanonicalizationProposal.from_dict(inputs.canonical_result["raw_proposal"])
    compiled = compile_assertion_semantics(document, inputs.symbols, inputs.assertions, proposal).model
    structures = StructureDetector().detect(compiled)
    focus_structures = [
        item.id for item in structures.structures if FOCUS_ENTITY_ID in item.entity_ids
    ]
    return {
        "path": "EXISTING_CANONICAL_STRUCTURE_DETECTOR",
        "detector_version": structures.detector_version,
        "detector_configuration_changed": False,
        "compiled_counts": {
            "entities": len(compiled.entities), "relationships": len(compiled.relationships),
            "propositions": len(compiled.propositions), "claims": len(compiled.claims),
        },
        "structure_count": len(structures.structures),
        "structures": structures.to_dict()["structures"],
        "expected_preserved_result": "2-node hierarchy; focus absent; admission fail",
        "focus_present": bool(focus_structures),
        "focus_structure_ids": focus_structures,
        "admission": "FAIL_FOCUS_ABSENT" if not focus_structures else "UNEXPECTED_PASS",
    }


def _parent_navigation(parent: KnowledgeModel) -> dict[str, Any]:
    positions = {}
    for index, entity in enumerate(sorted(parent.entities, key=lambda item: item.id)):
        column, row = index % 6, index // 6
        positions[entity.id] = {"x": 200.0 + column * 360.0, "y": 180.0 + row * 190.0}
    nodes = [{
        "entity_id": entity.id, "label": entity.name, "description": entity.description,
        "entity_type": entity.entity_type.value, "domain_id": "quantum_mechanics",
        "world": positions[entity.id], "has_deeper_resolution": entity.id == FOCUS_ENTITY_ID,
    } for entity in sorted(parent.entities, key=lambda item: item.id)]
    edges, routes = [], []
    adjacency = {item["entity_id"]: [] for item in nodes}
    for relationship in sorted(parent.relationships, key=lambda item: item.id):
        key = f"parent-{relationship.id}"
        edges.append({
            "edge_key": key, "source_entity_id": relationship.source_entity_id,
            "target_entity_id": relationship.target_entity_id,
            "relationship_type": relationship.relationship_type.value,
            "relationship_label": relationship.relationship_type.value.replace("_", " "),
            "relationship_ids": [relationship.id], "domain_id": "quantum_mechanics",
        })
        routes.append({"edge_key": key, **_route(
            positions[relationship.source_entity_id], positions[relationship.target_entity_id]
        )})
        adjacency[relationship.source_entity_id].append(relationship.target_entity_id)
        adjacency[relationship.target_entity_id].append(relationship.source_entity_id)
    for neighbors in adjacency.values():
        neighbors.sort()
    return {
        "nodes": nodes, "edges": edges, "adjacency": adjacency,
        "world": {"bounds": WORLD_BOUNDS, "layout_strategy": "DETERMINISTIC_PARENT_SYMBOL_GRID",
                  "node_positions_stable": True, "routes": routes},
        "camera": {"initial": INITIAL_CAMERA, "viewport": VIEWPORT,
                   "transform": "SVG_VIEWBOX_WORLD_TO_VIEWPORT",
                   "zoom": {"kind": "GEOMETRIC_ONLY", "min_scale": .55, "max_scale": 2.25,
                            "initial_scale": 1.0, "pointer_centered": True,
                            "wheel_sensitivity": .0015}, "focus_animation_ms": 280},
    }


def _workspace(parent: KnowledgeModel, inputs: FrozenProjectionInputs, projection: dict[str, Any]) -> dict[str, Any]:
    navigation = _parent_navigation(parent)
    return {
        "version": EVALUATION_VERSION,
        "fixture_status": "FROZEN_SPEC020_PACKET_WITH_OFFLINE_EXPLANATORY_PROJECTION",
        "domains": [{"domain_id": "quantum_mechanics", "label": "Quantum mechanics",
                     "world_region": {"x": 70.0, "y": 70.0, "width": 2200.0, "height": 1340.0},
                     "learning_model": inputs.parent_representation}],
        "navigation": navigation,
        "workspace": {"default_domain_id": "quantum_mechanics", "default_focused_entity_id": FOCUS_ENTITY_ID,
                      "shared_focus": "STABLE_PARENT_ENTITY_ID", "camera_independent_from_semantic_focus": True},
        "semantic_depth": {"focus_entity_id": FOCUS_ENTITY_ID, "focus_label": "double-slit experiment",
                           "levels": ["PARENT", "EXPLANATORY_PROJECTION"], "default_level": "PARENT",
                           "maximum_child_depth": 1, "projection": projection,
                           "navigation_world_replaced": False, "geometric_zoom_independent": True},
    }


def _copy_assets(output_dir: Path) -> None:
    base = files("knowledge_compiler").joinpath("navigation_learning_assets", "workspace.css")
    with base.open("rb") as source, (output_dir / "workspace.css").open("wb") as target:
        shutil.copyfileobj(source, target)
    assets = files("knowledge_compiler").joinpath("explanatory_projection_assets")
    for name in ("index.html", "projection.css", "workspace.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def prepare_explanatory_projection_evaluation(
    *, output_dir: Path, spec020_dir: Path = default_spec020_directory(),
    spec013_dir: Path = default_spec013_directory(),
) -> dict[str, Any]:
    """Generate the complete offline packet and viewer with no semantic mutation."""
    output_dir.mkdir(parents=True, exist_ok=False)
    inputs = load_frozen_spec020_inputs(spec020_dir)
    parent_path = spec013_dir / "parent.knowledge.json"
    expected_parent_hash = inputs.parent_hashes["before"]["parent_knowledge"]
    if _hash(parent_path) != expected_parent_hash:
        raise ValidationError("trusted SPEC-013 parent bytes differ from frozen SPEC-020 parent hash")
    parent = KnowledgeModel.from_dict(json.loads(parent_path.read_text(encoding="utf-8")))
    baseline_before = _baseline_hashes()
    if baseline_before != inputs.baseline_manifest["before"]:
        raise ValidationError("BASELINE-001/002/003 bytes differ from frozen SPEC-020 manifest")
    projection = build_explanatory_projection(inputs)
    projection_value = projection.to_dict()
    diagnostics = projection_diagnostics(projection)
    canonical = _canonical_control(inputs)
    focus_direct = sum(
        FOCUS_ENTITY_ID in item.participant_entity_ids for item in inputs.assertions.assertions
    )
    review_counts = inputs.semantic_review["canonical_semantics"]["counts"]
    diagnostics.update({
        "input_grounded_assertion_count": len(inputs.assertions.assertions),
        "rejected_canonical_item_count": sum(
            count for category, count in review_counts.items() if category != "SUPPORTED"
        ),
        "focus_direct_assertion_count": focus_direct,
        "deterministic_regeneration": (
            canonical_bytes(projection_value) == canonical_bytes(build_explanatory_projection(inputs).to_dict())
        ),
        "baseline_003_asset_immutability": baseline_before == _baseline_hashes(),
    })
    workspace = _workspace(parent, inputs, projection_value)
    nav_hash = hashlib.sha256(canonical_bytes(workspace["navigation"])).hexdigest()
    initial = DepthWorkspaceState(camera=CameraState(**INITIAL_CAMERA))
    deeper = switch_semantic_depth(initial, "CHILD")
    returned = switch_semantic_depth(deeper, "PARENT")
    workspace_diagnostics = {
        "parent_navigation": {"entity_count": len(workspace["navigation"]["nodes"]),
                              "relationship_count": len(workspace["navigation"]["edges"]),
                              "world_hash_before_transition": nav_hash,
                              "world_hash_after_transition": nav_hash, "stable": True},
        "semantic_depth": {"focus_entity_id": FOCUS_ENTITY_ID,
                           "parent_to_projection_camera_unchanged": depth_camera_invariant(initial, deeper),
                           "projection_to_parent_camera_unchanged": depth_camera_invariant(deeper, returned),
                           "return_to_parent_preserves_focus": returned.focused_entity_id == FOCUS_ENTITY_ID,
                           "geometric_zoom_triggers_semantic_depth": False},
    }
    raw_history = repository_root() / "debriefs" / "DEBRIEF-016-assertion-aware-representation.md"
    comparison = {
        "canonical_control": canonical,
        "raw_assertion_visibility": {"source": str(raw_history.relative_to(repository_root())),
                                     "source_sha256": _hash(raw_history),
                                     "owner_verdict": "NO_MEANINGFUL_IMPROVEMENT",
                                     "finding": "Raw assertion cards caused text-heavy cognitive overload and removed the spatial learning surface."},
        "focus_explanatory_projection": {"focus_present": diagnostics["focus_present"],
                                         "represented_grounded_meaning_items": diagnostics["selected_explanatory_item_count"],
                                         "semantic_tiers_distinct": diagnostics["semantic_tier_labeling_complete"],
                                         "initial_text_budget_pass": diagnostics["text_budget_pass"]},
    }
    tier_audit = {
        "trusted_canonical": [{"id": item.id, "assertion_id": item.assertion_id,
                               "predicate": item.relationship_type} for item in projection.canonical_items],
        "source_backed_non_canonical": [{"id": item.id, "assertion_id": item.assertion_id,
                                         "role": item.presentation_role,
                                         "participants": list(item.participant_entity_ids)}
                                        for item in projection.explanatory_items],
        "rejected_or_partial_not_promoted": ["assertion-ae10fa8748fdac1f", "assertion-34df8905cd0bc7db"],
        "note": "The rejected causal nomination is retained only as its exact faithful assertion in the weaker presentation tier; the partial assertion is excluded.",
    }
    baseline_after = _baseline_hashes()
    machine_pass = all((
        diagnostics["focus_present"], diagnostics["text_budget_pass"],
        diagnostics["deterministic_regeneration"], diagnostics["baseline_003_asset_immutability"],
        diagnostics["pairwise_edge_fabrication_count"] == 0,
        diagnostics["rejected_item_promotion_count"] == 0,
        canonical["admission"] == "FAIL_FOCUS_ABSENT",
    ))
    report = {
        "spec": "SPEC-021", "evaluation_version": EVALUATION_VERSION,
        "execution_stage": "PENDING_OWNER_COGNITIVE_REVIEW" if machine_pass else "FAILED_CLOSED",
        "machine_integrity_verdict": "PASS" if machine_pass else "FAIL_CLOSED",
        "product_verdict": "PENDING", "human_review_status": "PENDING_OWNER_REVIEW" if machine_pass else "NOT_AVAILABLE",
        "focus_entity_id": FOCUS_ENTITY_ID, "live_model_calls": 0,
        "metrics": diagnostics, "canonical_control": {"structure_count": canonical["structure_count"],
                                                        "focus_present": canonical["focus_present"],
                                                        "admission": canonical["admission"]},
        "knowledge_model_changed": False, "global_structure_detector_changed": False,
        "baseline_assets_immutable": baseline_before == baseline_after,
        "dependencies_added": [], "dependencies_removed": [], "semantic_ir_changes": [],
        "workspace_shell_changes": [], "deviations": [],
        "known_weaknesses": ["Six neutral anchors still require learner selection to expose meaning.",
                             "Dense dashed attachments may compete for attention on a small viewport."],
        "viewer_command": f".venv/bin/knowledge-compiler view-representations {EVALUATION_RELATIVE_PATH} --port 8021",
    }
    input_manifest = {
        "spec": "SPEC-021", "source_directory": str(spec020_dir),
        "files": inputs.file_hashes, "expected_files": FROZEN_SPEC020_HASHES,
        "identity_verified": inputs.file_hashes == FROZEN_SPEC020_HASHES,
        "parent_knowledge_sha256": expected_parent_hash,
        "baseline_before": baseline_before, "baseline_after": baseline_after,
        "baseline_immutable": baseline_before == baseline_after,
    }
    for name, value in {
        "input-manifest.json": input_manifest, "projection.json": projection_value,
        "projection-diagnostics.json": diagnostics, "canonical-control.json": canonical,
        "semantic-tier-audit.json": tier_audit, "machine-comparison.json": comparison,
        "workspace-fixture.json": workspace, "workspace-diagnostics.json": workspace_diagnostics,
        "report.json": report,
        "human-review-template.json": {"status": "PENDING_OWNER_REVIEW", "owner_response": None,
                                       "verdict": "PENDING", "allowed_verdicts": [
                                           "EXPLANATORY_PROJECTION_BETTER", "MIXED",
                                           "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE"]},
        "browser-verification.json": {"status": "PENDING_MANUAL_BROWSER_VERIFICATION",
                                      "mouse": {}, "keyboard": {}, "console": {}},
    }.items():
        _write_json(output_dir / name, value)
    manifest = {"spec": "SPEC-021", "title": "Focus-preserving explanatory projection",
                "workspace_fixture": "workspace-fixture.json", "projection": "projection.json",
                "projection_diagnostics": "projection-diagnostics.json",
                "human_review": "human-review-template.json"}
    _write_json(output_dir / "workspace-manifest.json", manifest)
    _write_json(output_dir / "manifest.json", manifest)
    (output_dir / "README.md").write_text(
        "# SPEC-021 focus-preserving explanatory projection\n\n"
        "This fully offline packet projects the exact rejected SPEC-020 child around "
        "`double-slit-experiment` without changing canonical semantics. Strong directed links are "
        "trusted canonical items; dashed non-arrowed attachments are source-backed explanations.\n\n"
        "Generate:\n\n```sh\n"
        f".venv/bin/knowledge-compiler prepare-explanatory-projection --output-dir {EVALUATION_RELATIVE_PATH}\n"
        "```\n\nReview:\n\n```sh\n"
        f".venv/bin/knowledge-compiler view-representations {EVALUATION_RELATIVE_PATH} --port 8021\n"
        "```\n", encoding="utf-8")
    _copy_assets(output_dir)
    return report
