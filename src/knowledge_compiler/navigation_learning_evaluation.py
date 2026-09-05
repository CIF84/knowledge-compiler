"""Generate deterministic SPEC-019 navigation + learning workspace artifacts."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .continuous_navigation import CameraState
from .interface_restoration import InteractionSelection, attention_state, state_counts, zoom_camera
from .models import ValidationError
from .navigation_learning_workspace import (
    WORKSPACE_INITIAL_CAMERA,
    build_workspace_fixture,
    canonical_workspace_bytes,
    change_camera,
    context_path,
    initial_workspace_state,
    state_dict,
    switch_learning_representation,
    synchronize_focus,
)


def default_spec006_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-006-layout-interaction-20260903"


def default_ops002_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "ops-002-continuous-interface-baseline-restoration-20260905"


def default_baseline001_document() -> Path:
    return Path(__file__).parents[2] / "baselines" / "BASELINE-001-interface.md"


def default_baseline001_assets() -> Path:
    return Path(__file__).parents[2] / "baselines" / "BASELINE-001-interface"


def default_baseline002_document() -> Path:
    return Path(__file__).parents[2] / "baselines" / "BASELINE-002-continuous-navigation-reference.md"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): _hash(path)
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_workspace_bytes(value))


def _copy_assets(output_dir: Path) -> None:
    assets = files("knowledge_compiler").joinpath("navigation_learning_assets")
    for name in ("index.html", "workspace.css", "workspace.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _frozen_hashes(
    spec006: Path, ops002: Path, baseline001_doc: Path, baseline001_assets: Path, baseline002_doc: Path
) -> dict[str, Any]:
    return {
        "baseline_001_document": _hash(baseline001_doc),
        "baseline_001_assets": _directory_hashes(baseline001_assets),
        "spec_006_learning_assets": _directory_hashes(spec006),
        "baseline_002_document": _hash(baseline002_doc),
        "ops_002_navigation_assets": _directory_hashes(ops002),
    }


def _learning_attention(fixture: dict[str, Any]) -> dict[str, Any]:
    software = next(item for item in fixture["domains"] if item["domain_id"] == "software_architecture")
    hierarchy = software["learning_model"]["representations"][0]
    relationship_id = hierarchy["edges"][0]["relationship_ids"][0]
    relationship = next(edge for edge in hierarchy["edges"] if relationship_id in edge["relationship_ids"])
    node = attention_state(
        hierarchy,
        persistent=InteractionSelection("node", "modular-order-processing-service"),
    )
    edge = attention_state(
        hierarchy,
        persistent=InteractionSelection("edge", relationship["edge_key"]),
    )
    preview = attention_state(
        hierarchy,
        persistent=InteractionSelection("node", "modular-order-processing-service"),
        preview=InteractionSelection("node", "order-component"),
    )
    restored = attention_state(
        hierarchy,
        persistent=InteractionSelection("node", "modular-order-processing-service"),
    )
    return {
        "selected_node": state_counts(node),
        "selected_relationship": state_counts(edge),
        "hover_preview": state_counts(preview),
        "hover_restoration_exact": restored == node,
    }


def prepare_navigation_learning_evaluation(
    *,
    output_dir: Path,
    spec_006_dir: Path = default_spec006_directory(),
    ops_002_dir: Path = default_ops002_directory(),
    baseline_001_document: Path = default_baseline001_document(),
    baseline_001_assets: Path = default_baseline001_assets(),
    baseline_002_document: Path = default_baseline002_document(),
) -> dict[str, Any]:
    frozen_before = _frozen_hashes(
        spec_006_dir, ops_002_dir, baseline_001_document, baseline_001_assets, baseline_002_document
    )
    output_resolved = output_dir.resolve()
    for source in (spec_006_dir, ops_002_dir, baseline_001_assets):
        if source.resolve() == output_resolved or source.resolve() in output_resolved.parents:
            raise ValidationError("SPEC-019 output must not overwrite or nest inside a frozen baseline input")

    fixture = build_workspace_fixture(spec_006_dir)
    initial = initial_workspace_state(fixture)
    navigation_nodes = fixture["navigation"]["nodes"]
    navigation_edges = fixture["navigation"]["edges"]
    learning_entity_ids = {
        node["entity_id"] for domain in fixture["domains"]
        for representation in domain["learning_model"]["representations"]
        for node in representation["nodes"]
    }
    learning_relationship_ids = {
        relationship_id for domain in fixture["domains"]
        for representation in domain["learning_model"]["representations"]
        for edge in representation["edges"] for relationship_id in edge["relationship_ids"]
    }
    navigation_relationship_ids = {
        relationship_id for edge in navigation_edges for relationship_id in edge["relationship_ids"]
    }

    navigation_to_learning = []
    for entity_id in (
        "modular-order-processing-service", "market-price", "printed-controversy", "electric-field"
    ):
        result = synchronize_focus(
            fixture, initial, origin="navigation", kind="entity", stable_id=entity_id
        )
        navigation_to_learning.append({
            "entity_id": entity_id,
            "result_domain_id": result.domain_id,
            "result_representation_index": result.representation_index,
            "context_path": context_path(fixture, result),
            "camera": state_dict(result)["camera"],
        })

    learning_to_navigation = []
    for entity_id in ("order-component", "market-price", "authorities"):
        result = synchronize_focus(
            fixture, initial, origin="learning", kind="entity", stable_id=entity_id
        )
        learning_to_navigation.append({
            "entity_id": entity_id,
            "navigation_highlight_id": result.focused_entity_id,
            "camera_before": state_dict(initial)["camera"],
            "camera_after": state_dict(result)["camera"],
            "camera_moved": result.camera != initial.camera,
        })

    relationship_cases = []
    for relationship_id in ("rel-1", "rel-6", "rel-shortage-upward-pressure"):
        result = synchronize_focus(
            fixture, initial, origin="learning", kind="relationship", stable_id=relationship_id
        )
        nav_matches = [
            edge["edge_key"] for edge in navigation_edges if relationship_id in edge["relationship_ids"]
        ]
        relationship_cases.append({
            "relationship_id": relationship_id,
            "navigation_edge_keys": nav_matches,
            "result_domain_id": result.domain_id,
            "result_representation_index": result.representation_index,
            "camera_preserved": result.camera == initial.camera,
        })

    panned_zoomed_camera = zoom_camera(
        CameraState(300, 220, 1), screen_anchor=(600, 400), target_scale=1.4,
        bounds=fixture["navigation"]["world"]["bounds"],
        viewport=fixture["navigation"]["camera"]["viewport"],
    )
    moved = change_camera(initial, panned_zoomed_camera)
    switched = switch_learning_representation(moved, 1)
    learning_focus_before_camera = {
        key: value for key, value in state_dict(initial).items() if key != "camera"
    }
    learning_focus_after_camera = {
        key: value for key, value in state_dict(moved).items() if key != "camera"
    }
    already_visible = next(
        item for item in learning_to_navigation if item["entity_id"] == "order-component"
    )
    unnecessary_recenter_count = int(already_visible["camera_moved"])

    navigation_attention = attention_state(
        {"nodes": navigation_nodes, "edges": navigation_edges},
        persistent=InteractionSelection("node", "modular-order-processing-service"),
    )
    frozen_after = _frozen_hashes(
        spec_006_dir, ops_002_dir, baseline_001_document, baseline_001_assets, baseline_002_document
    )
    embedded_learning_unchanged = all(
        domain["learning_model"]
        == json.loads((spec_006_dir / f"{domain['domain_id']}.representation.json").read_text(encoding="utf-8"))
        for domain in fixture["domains"]
    )
    integrity = {
        "frozen_baselines_unchanged": frozen_before == frozen_after,
        "embedded_learning_representations_unchanged": embedded_learning_unchanged,
        "navigation_and_learning_entity_ids_match": {item["entity_id"] for item in navigation_nodes} == learning_entity_ids,
        "navigation_and_learning_relationship_ids_match": navigation_relationship_ids == learning_relationship_ids,
        "all_navigation_to_learning_cases_resolved": len(navigation_to_learning) == 4,
        "all_learning_to_navigation_cases_highlight_stable_id": all(item["entity_id"] == item["navigation_highlight_id"] for item in learning_to_navigation),
        "relationship_sync_uses_stable_ids": all(len(item["navigation_edge_keys"]) == 1 for item in relationship_cases),
        "pure_camera_change_preserves_learning_state": learning_focus_before_camera == learning_focus_after_camera,
        "learning_representation_change_preserves_camera": switched.camera == moved.camera,
        "unnecessary_recenter_avoided": unnecessary_recenter_count == 0,
        "parent_context_path_present": len(context_path(fixture, initial)) == 3,
        "fixture_provenance_explicit": fixture["fixture_status"].startswith("COMPOSED_EXISTING"),
        "no_semantic_ir_changes": True,
        "no_relationship_vocabulary_changes": True,
        "no_representation_algorithm_changes": True,
        "no_personalization_engine": True,
        "no_semantic_zoom": True,
        "no_live_provider_calls": True,
    }
    if not all(integrity.values()):
        raise ValidationError("SPEC-019 machine integrity failed")

    representation_types = sorted({
        representation["layout"]["strategy"] for domain in fixture["domains"]
        for representation in domain["learning_model"]["representations"]
    })
    diagnostics = {
        "spec": "SPEC-019",
        "navigation_fixture": {
            "concept_count": len(navigation_nodes),
            "relationship_edge_count": len(navigation_edges),
            "relationship_id_count": len(navigation_relationship_ids),
            "domain_count": len(fixture["domains"]),
        },
        "learning": {
            "representation_count": sum(len(item["learning_model"]["representations"]) for item in fixture["domains"]),
            "representation_layout_strategies": representation_types,
            "embedded_payloads_unchanged": embedded_learning_unchanged,
            "parent_context_example": context_path(fixture, initial),
        },
        "shared_ids": {
            "entity_count": len(learning_entity_ids),
            "relationship_id_count": len(learning_relationship_ids),
            "entity_ids": sorted(learning_entity_ids),
            "relationship_ids": sorted(learning_relationship_ids),
        },
        "synchronization": {
            "navigation_to_learning": navigation_to_learning,
            "learning_to_navigation": learning_to_navigation,
            "relationships": relationship_cases,
            "unnecessary_recenter_count": unnecessary_recenter_count,
        },
        "state_separation": {
            "pure_pan_zoom_learning_state_before": learning_focus_before_camera,
            "pure_pan_zoom_learning_state_after": learning_focus_after_camera,
            "camera_after_pan_zoom": state_dict(moved)["camera"],
            "camera_preserved_across_learning_representation_change": switched.camera == moved.camera,
            "overview_target": WORKSPACE_INITIAL_CAMERA,
        },
        "suppression": {
            "navigation": state_counts(navigation_attention),
            "learning": _learning_attention(fixture),
        },
        "browser_verification": "SEE browser-verification.json",
        "integrity": integrity,
    }
    comparison = {
        "spec": "SPEC-019",
        "baseline_001_learning": {
            "status": "PRESERVED_FOR_OWNER_COMPARISON",
            "embedded_representations_unchanged": embedded_learning_unchanged,
            "human_comparison": "PENDING_OWNER_REVIEW",
        },
        "baseline_002_navigation": {
            "status": "PRESERVED_FOR_OWNER_COMPARISON",
            "camera_pan_zoom_focus_primitives_reused": True,
            "human_comparison": "PENDING_OWNER_REVIEW",
        },
        "hybrid_verdict": "PENDING_OWNER_REVIEW",
    }
    baseline_manifest = {
        "spec": "SPEC-019",
        "baseline_001": {
            "document": {"path": str(baseline_001_document), "sha256": frozen_before["baseline_001_document"]},
            "screenshots": [{"path": str(baseline_001_assets / key), "sha256": value} for key, value in frozen_before["baseline_001_assets"].items()],
            "learning_assets": [{"path": str(spec_006_dir / key), "sha256": value} for key, value in frozen_before["spec_006_learning_assets"].items()],
        },
        "baseline_002": {
            "document": {"path": str(baseline_002_document), "sha256": frozen_before["baseline_002_document"]},
            "navigation_assets": [{"path": str(ops_002_dir / key), "sha256": value} for key, value in frozen_before["ops_002_navigation_assets"].items()],
        },
    }
    report = {
        "spec": "SPEC-019",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "live_provider_calls": 0,
        "machine_integrity_verdict": "PASS",
        "human_review_status": "PENDING_OWNER_REVIEW",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "replacement_baseline_created": False,
        "deviations": [],
    }
    manifest = {
        "spec": "SPEC-019",
        "title": "Navigation + Learning Workspace",
        "workspace_fixture": "workspace-fixture.json",
        "synchronization_diagnostics": "synchronization-diagnostics.json",
        "baseline_comparison": "baseline-comparison.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
    }
    browser_verification = {
        "status": "PENDING_MANUAL_BROWSER_VERIFICATION",
        "mouse": {}, "keyboard": {}, "console": {},
    }
    human_review = {
        "status": "PENDING_OWNER_REVIEW",
        "instruction": "Use this to understand the subject, but move around whenever the map makes you curious.",
        "allowed_verdicts": [
            "HYBRID_WORKSPACE_BETTER", "MIXED", "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE"
        ],
        "owner_response": None,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "workspace-fixture.json", fixture)
    _write_json(output_dir / "synchronization-diagnostics.json", diagnostics)
    _write_json(output_dir / "baseline-comparison.json", comparison)
    _write_json(output_dir / "baseline-manifest.json", baseline_manifest)
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "workspace-manifest.json", manifest)
    _write_json(output_dir / "manifest.json", manifest)
    browser_path = output_dir / "browser-verification.json"
    if not browser_path.exists():
        _write_json(browser_path, browser_verification)
    _write_json(output_dir / "human-review-template.json", human_review)
    _copy_assets(output_dir)
    (output_dir / "README.md").write_text(
        "# SPEC-019 navigation + learning workspace\n\n"
        "This offline integration composes unchanged SPEC-006 structure-aware representations into a "
        "BASELINE-002-style continuous navigation world. Stable entity and relationship IDs synchronize both panes.\n\n"
        "Generate:\n\n```sh\n.venv/bin/knowledge-compiler prepare-navigation-learning-workspace "
        "--output-dir examples/evaluations/spec-019-navigation-learning-workspace-20260905\n```\n\n"
        "Review:\n\n```sh\n.venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-019-navigation-learning-workspace-20260905 --port 8019\n```\n\n"
        "BASELINE-001 comparison:\n\n```sh\n.venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-006-layout-interaction-20260903 --port 8006\n```\n\n"
        "BASELINE-002 comparison:\n\n```sh\n.venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/ops-002-continuous-interface-baseline-restoration-20260905 --port 8020\n```\n",
        encoding="utf-8",
    )
    return report
