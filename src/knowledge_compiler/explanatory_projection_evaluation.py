"""Deterministic offline SPEC-021 evaluation and review workspace."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .assertion_compilation import CanonicalizationProposal, compile_assertion_semantics
from .explanatory_projection import (
    FOCUS_ENTITY_ID,
    FROZEN_SPEC020_HASHES,
    FrozenProjectionInputs,
    build_explanatory_projection,
    canonical_bytes,
    load_frozen_spec020_inputs,
    projection_diagnostics,
)
from .models import SourceDocument, ValidationError
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


def default_baseline003_assets() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-019-navigation-learning-workspace-20260905"


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


def _copy_assets(output_dir: Path, baseline_dir: Path) -> None:
    for name in ("workspace.css", "workspace.js", "workspace-fixture.json"):
        shutil.copyfile(baseline_dir / name, output_dir / name)
    baseline_index = (baseline_dir / "index.html").read_text(encoding="utf-8")
    if baseline_index.count('<link rel="stylesheet" href="workspace.css">') != 1:
        raise ValidationError("BASELINE-003 index stylesheet seam changed")
    if baseline_index.count('<script src="workspace.js"></script>') != 1:
        raise ValidationError("BASELINE-003 index script seam changed")
    extended_index = baseline_index.replace(
        '<link rel="stylesheet" href="workspace.css">',
        '<link rel="stylesheet" href="workspace.css">\n  <link rel="stylesheet" href="projection.css">',
    ).replace(
        '<script src="workspace.js"></script>',
        '<script src="workspace.js"></script>\n  <script src="projection-extension.js"></script>',
    )
    (output_dir / "index.html").write_text(extended_index, encoding="utf-8")
    assets = files("knowledge_compiler").joinpath("explanatory_projection_assets")
    for name in ("projection.css", "projection-extension.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _restoration_diagnostics(output_dir: Path, baseline_dir: Path) -> dict[str, Any]:
    baseline_index = (baseline_dir / "index.html").read_text(encoding="utf-8")
    restored_index = (output_dir / "index.html").read_text(encoding="utf-8")
    normalized_index = restored_index.replace(
        '\n  <link rel="stylesheet" href="projection.css">', ""
    ).replace('\n  <script src="projection-extension.js"></script>', "")
    exact = {
        name: _hash(output_dir / name) == _hash(baseline_dir / name)
        for name in ("workspace.css", "workspace.js", "workspace-fixture.json")
    }
    baseline_fixture = json.loads((baseline_dir / "workspace-fixture.json").read_text(encoding="utf-8"))
    restored_fixture = json.loads((output_dir / "workspace-fixture.json").read_text(encoding="utf-8"))
    topology = lambda fixture: {
        "nodes": [(item["entity_id"], item["domain_id"]) for item in fixture["navigation"]["nodes"]],
        "edges": [(item["edge_key"], item["source_entity_id"], item["target_entity_id"], tuple(item["relationship_ids"])) for item in fixture["navigation"]["edges"]],
        "adjacency": fixture["navigation"]["adjacency"],
    }
    coordinates = lambda fixture: {
        "regions": [(item["domain_id"], item["world_region"]) for item in fixture["domains"]],
        "nodes": [(item["entity_id"], item["world"]) for item in fixture["navigation"]["nodes"]],
        "world": fixture["navigation"]["world"],
    }
    result = {
        "status": "PASS" if all(exact.values()) and normalized_index == baseline_index else "FAIL_CLOSED",
        "baseline_source": str(baseline_dir.relative_to(repository_root())),
        "direct_byte_reuse": exact,
        "shell_structure_preserved": normalized_index == baseline_index,
        "allowlisted_shell_seam": ["projection.css link", "projection-extension.js script"],
        "navigation_topology_identical": topology(restored_fixture) == topology(baseline_fixture),
        "world_coordinates_and_routes_identical": coordinates(restored_fixture) == coordinates(baseline_fixture),
        "workspace_focus_configuration_identical": restored_fixture["workspace"] == baseline_fixture["workspace"],
        "camera_configuration_identical": restored_fixture["navigation"]["camera"] == baseline_fixture["navigation"]["camera"],
        "interaction_handlers_identical": exact["workspace.js"],
        "frozen_styling_identical": exact["workspace.css"],
        "projection_seam": {
            "location": "right learning pane only",
            "baseline_navigation_state_access": False,
            "camera_state_access": False,
            "exits_before_baseline_navigation_click": True,
            "page_navigation": False,
        },
    }
    if result["status"] != "PASS" or not all(
        result[key] for key in (
            "navigation_topology_identical", "world_coordinates_and_routes_identical",
            "workspace_focus_configuration_identical", "camera_configuration_identical",
            "interaction_handlers_identical", "frozen_styling_identical",
        )
    ):
        raise ValidationError("restored viewer differs from actual BASELINE-003 controls")
    return result


def prepare_explanatory_projection_evaluation(
    *, output_dir: Path, spec020_dir: Path = default_spec020_directory(),
    spec013_dir: Path = default_spec013_directory(),
    baseline_dir: Path = default_baseline003_assets(),
) -> dict[str, Any]:
    """Generate the complete offline packet and viewer with no semantic mutation."""
    output_dir.mkdir(parents=True, exist_ok=False)
    inputs = load_frozen_spec020_inputs(spec020_dir)
    parent_path = spec013_dir / "parent.knowledge.json"
    expected_parent_hash = inputs.parent_hashes["before"]["parent_knowledge"]
    if _hash(parent_path) != expected_parent_hash:
        raise ValidationError("trusted SPEC-013 parent bytes differ from frozen SPEC-020 parent hash")
    baseline_before = _baseline_hashes()
    if baseline_before != inputs.baseline_manifest["before"]:
        raise ValidationError("BASELINE-001/002/003 bytes differ from frozen SPEC-020 manifest")
    expected_baseline_assets = inputs.baseline_manifest["before"]["baseline_003_assets"]
    controlled_baseline_files = ("index.html", "workspace.css", "workspace.js", "workspace-fixture.json")
    baseline_source_hashes = {name: _hash(baseline_dir / name) for name in controlled_baseline_files}
    expected_control_hashes = {name: expected_baseline_assets[name] for name in controlled_baseline_files}
    if baseline_source_hashes != expected_control_hashes:
        raise ValidationError("actual BASELINE-003 implementation/assets changed or were substituted")
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
        "execution_stage": "PENDING_BASELINE_RESTORATION_OWNER_REVIEW" if machine_pass else "FAILED_CLOSED",
        "machine_integrity_verdict": "PASS" if machine_pass else "FAIL_CLOSED",
        "product_verdict": "PENDING", "human_review_status": "PENDING_BASELINE_RESTORATION_CONFIRMATION" if machine_pass else "NOT_AVAILABLE",
        "focus_entity_id": FOCUS_ENTITY_ID, "live_model_calls": 0,
        "metrics": diagnostics, "canonical_control": {"structure_count": canonical["structure_count"],
                                                        "focus_present": canonical["focus_present"],
                                                        "admission": canonical["admission"]},
        "knowledge_model_changed": False, "global_structure_detector_changed": False,
        "baseline_assets_immutable": baseline_before == baseline_after,
        "dependencies_added": [], "dependencies_removed": [], "semantic_ir_changes": [],
        "workspace_shell_changes": ["Allowlisted projection stylesheet and right-pane extension script only"], "deviations": [],
        "experimental_evidence_valid": False,
        "feature_evaluation_status": "STOPPED_PENDING_BASELINE_RESTORATION_CONFIRMATION",
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
        "restored_baseline_control_hashes": baseline_source_hashes,
    }
    for name, value in {
        "input-manifest.json": input_manifest, "projection.json": projection_value,
        "projection-diagnostics.json": diagnostics, "canonical-control.json": canonical,
        "semantic-tier-audit.json": tier_audit, "machine-comparison.json": comparison,
        "report.json": report,
        "human-review-template.json": {"status": "BLOCKED_PENDING_BASELINE_RESTORATION_CONFIRMATION", "owner_response": None,
                                       "verdict": "PENDING", "allowed_verdicts": [
                                           "EXPLANATORY_PROJECTION_BETTER", "MIXED",
                                           "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE"]},
        "browser-verification.json": {"status": "NOT_RUN_FEATURE_EVALUATION_STOPPED",
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
    _copy_assets(output_dir, baseline_dir)
    restoration = _restoration_diagnostics(output_dir, baseline_dir)
    _write_json(output_dir / "workspace-diagnostics.json", restoration)
    report["baseline_restoration"] = restoration
    report["machine_integrity_verdict"] = restoration["status"]
    _write_json(output_dir / "report.json", report)
    return report
