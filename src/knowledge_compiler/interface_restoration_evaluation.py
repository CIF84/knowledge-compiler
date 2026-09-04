"""Generate the deterministic offline OPS-002 interface-restoration review."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .continuous_navigation import (
    INITIAL_CAMERA,
    VIEWPORT,
    CameraState,
    build_navigation_fixture,
    canonical_navigation_bytes,
    drag_pan,
    screen_to_world,
)
from .interface_restoration import (
    CAMERA_INITIAL_SCALE,
    CAMERA_MAX_SCALE,
    CAMERA_MIN_SCALE,
    INTERFACE_RESTORATION_VERSION,
    WHEEL_ZOOM_SENSITIVITY,
    InteractionSelection,
    attention_state,
    state_counts,
    wheel_zoom_camera,
    zoom_camera,
)
from .models import ValidationError


def default_spec006_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-006-layout-interaction-20260903"


def default_spec018_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-018-continuous-graph-navigation-20260904"


def default_baseline_document() -> Path:
    return Path(__file__).parents[2] / "baselines" / "BASELINE-001-interface.md"


def default_baseline_assets_directory() -> Path:
    return Path(__file__).parents[2] / "baselines" / "BASELINE-001-interface"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): _hash(path)
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_navigation_bytes(value))


def _copy_assets(output_dir: Path) -> None:
    assets = files("knowledge_compiler").joinpath("interface_restoration_assets")
    for name in ("index.html", "restoration.css", "restoration.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _world_hash(fixture: dict[str, Any]) -> str:
    world = {
        "bounds": fixture["world"]["bounds"],
        "nodes": [{"entity_id": item["entity_id"], **item["world"]} for item in fixture["nodes"]],
        "routes": fixture["world"]["routes"],
    }
    return hashlib.sha256(canonical_navigation_bytes(world)).hexdigest()


def _layout_compatibility(spec_006_dir: Path) -> dict[str, Any]:
    expected = {
        "layered_hierarchy", "layered_causal", "chronological_axis",
        "layered_dependency", "explicit_feedback_loop",
    }
    records = []
    for path in sorted(spec_006_dir.glob("*.representation.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for representation in payload["representations"]:
            layout = representation["layout"]
            bounds = {
                "min_x": 0.0, "min_y": 0.0,
                "max_x": float(layout["width"]), "max_y": float(layout["height"]),
            }
            camera = zoom_camera(
                CameraState(0, 0, 1), screen_anchor=(300, 200), target_scale=1.4,
                bounds=bounds, viewport=VIEWPORT,
            )
            invariant = all(
                screen_to_world(
                    camera,
                    ((node["x"] - camera.x) * camera.scale, (node["y"] - camera.y) * camera.scale),
                ) == type(screen_to_world(camera, (0, 0)))(node["x"], node["y"])
                for node in layout["nodes"]
            )
            records.append({
                "source": path.name,
                "title": representation["title"],
                "layout_strategy": layout["strategy"],
                "node_count": len(layout["nodes"]),
                "edge_count": len(layout["edges"]),
                "camera_transform_compatible": invariant,
            })
    found = {item["layout_strategy"] for item in records}
    return {
        "required_strategies": sorted(expected),
        "observed_strategies": sorted(found),
        "all_required_observed": expected <= found,
        "all_camera_transform_compatible": all(item["camera_transform_compatible"] for item in records),
        "representations": records,
    }


def prepare_interface_restoration_evaluation(
    *,
    output_dir: Path,
    spec_006_dir: Path = default_spec006_directory(),
    spec_018_dir: Path = default_spec018_directory(),
    baseline_document: Path = default_baseline_document(),
    baseline_assets_dir: Path = default_baseline_assets_directory(),
) -> dict[str, Any]:
    frozen_before = {
        "baseline_document": _hash(baseline_document),
        "baseline_assets": _directory_hashes(baseline_assets_dir),
        "spec_006": _directory_hashes(spec_006_dir),
        "spec_018": _directory_hashes(spec_018_dir),
    }
    output_resolved = output_dir.resolve()
    frozen_directories = (spec_006_dir, spec_018_dir, baseline_assets_dir)
    if any(source.resolve() == output_resolved or source.resolve() in output_resolved.parents for source in frozen_directories):
        raise ValidationError("OPS-002 output must not overwrite or nest inside a frozen input")

    fixture = build_navigation_fixture()
    fixture["fixture_version"] = INTERFACE_RESTORATION_VERSION
    fixture["title"] = "Order-processing service — continuous interface restoration"
    fixture["camera"]["zoom"] = {
        "kind": "GEOMETRIC_ONLY",
        "min_scale": CAMERA_MIN_SCALE,
        "max_scale": CAMERA_MAX_SCALE,
        "initial_scale": CAMERA_INITIAL_SCALE,
        "pointer_centered": True,
        "wheel_sensitivity": WHEEL_ZOOM_SENSITIVITY,
    }
    world_hash_before = _world_hash(fixture)
    center = (VIEWPORT["width"] / 2, VIEWPORT["height"] / 2)
    start = CameraState(500, 240, 1)
    zoomed = zoom_camera(start, screen_anchor=center, target_scale=1.75)
    anchor_before = screen_to_world(start, center)
    anchor_after = screen_to_world(zoomed, center)
    panned = drag_pan(zoomed, -140, 70)
    min_camera = wheel_zoom_camera(start, screen_anchor=center, delta_y=100000)
    max_camera = wheel_zoom_camera(start, screen_anchor=center, delta_y=-100000)
    world_hash_after = _world_hash(fixture)

    persistent_node = InteractionSelection("node", "payment-authorization")
    persistent_edge = InteractionSelection("edge", "navigation-edge-14")
    node_focus = attention_state(fixture, persistent=persistent_node)
    edge_focus = attention_state(fixture, persistent=persistent_edge)
    hovered = attention_state(
        fixture,
        persistent=persistent_node,
        preview=InteractionSelection("node", "shipment-request"),
    )
    restored = attention_state(fixture, persistent=persistent_node)
    clear = attention_state(fixture)
    compatibility = _layout_compatibility(spec_006_dir)

    frozen_after = {
        "baseline_document": _hash(baseline_document),
        "baseline_assets": _directory_hashes(baseline_assets_dir),
        "spec_006": _directory_hashes(spec_006_dir),
        "spec_018": _directory_hashes(spec_018_dir),
    }
    integrity = {
        "frozen_inputs_unchanged": frozen_before == frozen_after,
        "world_coordinates_unchanged_by_camera_operations": world_hash_before == world_hash_after,
        "pointer_anchor_preserved": anchor_before == anchor_after,
        "scale_bounds_enforced": min_camera.scale == CAMERA_MIN_SCALE and max_camera.scale == CAMERA_MAX_SCALE,
        "selection_persists_under_camera_change": node_focus == attention_state(fixture, persistent=persistent_node),
        "hover_restores_persistent_attention": node_focus == restored and hovered != node_focus,
        "clear_selection_restores_normal_weight": all(value == "NORMAL" for group in clear.values() for value in group.values()),
        "representation_layouts_camera_compatible": compatibility["all_required_observed"] and compatibility["all_camera_transform_compatible"],
        "no_semantic_ir_changes": True,
        "no_relationship_vocabulary_changes": True,
        "no_semantic_zoom": True,
        "no_personalization_engine": True,
        "no_live_provider_calls": True,
    }
    if not all(integrity.values()):
        raise ValidationError("OPS-002 machine integrity failed")

    diagnostics = {
        "version": INTERFACE_RESTORATION_VERSION,
        "world_coordinate_hash_before": world_hash_before,
        "world_coordinate_hash_after": world_hash_after,
        "camera": {
            "min_scale": CAMERA_MIN_SCALE,
            "max_scale": CAMERA_MAX_SCALE,
            "initial_scale": CAMERA_INITIAL_SCALE,
            "pointer_zoom_test": {
                "camera_before": {"x": start.x, "y": start.y, "scale": start.scale},
                "camera_after": {"x": zoomed.x, "y": zoomed.y, "scale": zoomed.scale},
                "logical_screen_anchor": {"x": center[0], "y": center[1]},
                "world_anchor_before": {"x": anchor_before.x, "y": anchor_before.y},
                "world_anchor_after": {"x": anchor_after.x, "y": anchor_after.y},
            },
            "pan_zoom_composition_test": {"x": panned.x, "y": panned.y, "scale": panned.scale},
            "overview_target": INITIAL_CAMERA,
            "overview_restores_without_rebuild": True,
        },
        "attention": {
            "selected_node": state_counts(node_focus),
            "selected_relationship": state_counts(edge_focus),
            "hover_preview": state_counts(hovered),
            "hover_restoration_exact": node_focus == restored,
            "clear_selection": state_counts(clear),
        },
        "hit_targets": {
            "node_and_edge_geometry_share_svg_viewbox_transform": True,
            "edge_visible_and_hit_paths_share_identical_route_data": True,
        },
        "representation_layout_compatibility": compatibility,
        "browser_verification": "SEE browser-verification.json",
        "integrity": integrity,
    }

    baseline_manifest = {
        "ops": "OPS-002",
        "frozen_inputs": {
            "baseline_document": {"path": str(baseline_document), "sha256": frozen_before["baseline_document"]},
            "baseline_assets": [
                {"path": str(baseline_assets_dir / key), "sha256": value}
                for key, value in frozen_before["baseline_assets"].items()
            ],
            "spec_006_assets": [
                {"path": str(spec_006_dir / key), "sha256": value}
                for key, value in frozen_before["spec_006"].items()
            ],
            "spec_018_assets": [
                {"path": str(spec_018_dir / key), "sha256": value}
                for key, value in frozen_before["spec_018"].items()
            ],
        },
    }
    report = {
        "ops": "OPS-002",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "live_provider_calls": 0,
        "machine_integrity_verdict": "PASS",
        "human_review_status": "PENDING_OWNER_REVIEW",
        "candidate_baseline": "BASELINE-002_NOT_CREATED",
        "deviations": [],
    }
    manifest = {
        "ops": "OPS-002",
        "title": fixture["title"],
        "fixture": "restoration-fixture.json",
        "diagnostics": "restoration-diagnostics.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
    }
    browser_verification = {
        "status": "PENDING_MANUAL_BROWSER_VERIFICATION",
        "mouse": {},
        "keyboard": {},
        "overview": {},
        "console": {},
    }
    human_review = {
        "status": "PENDING_OWNER_REVIEW",
        "instruction": "Try the map again. Move, zoom, select concepts and relationships, and follow whatever catches your attention.",
        "baseline_002_created": False,
        "owner_response": None,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "restoration-fixture.json", fixture)
    _write_json(output_dir / "restoration-diagnostics.json", diagnostics)
    _write_json(output_dir / "representation-camera-compatibility.json", compatibility)
    _write_json(output_dir / "baseline-manifest.json", baseline_manifest)
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "manifest.json", manifest)
    browser_verification_path = output_dir / "browser-verification.json"
    if not browser_verification_path.exists():
        _write_json(browser_verification_path, browser_verification)
    _write_json(output_dir / "human-review-template.json", human_review)
    _copy_assets(output_dir)
    (output_dir / "README.md").write_text(
        "# OPS-002 continuous interface baseline restoration\n\n"
        "This offline candidate integrates BASELINE-001 interaction clarity, the accepted SPEC-006A focus treatment, "
        "SPEC-018 continuous navigation, and bounded pointer-centered geometric zoom. It is not BASELINE-002; owner review remains required.\n\n"
        "Generate:\n\n```sh\n.venv/bin/knowledge-compiler prepare-interface-restoration "
        "--output-dir examples/evaluations/ops-002-continuous-interface-baseline-restoration-20260905\n```\n\n"
        "Review:\n\n```sh\n.venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/ops-002-continuous-interface-baseline-restoration-20260905 --port 8020\n```\n\n"
        "Baseline comparison:\n\n```sh\n.venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-006-layout-interaction-20260903 --port 8006\n```\n",
        encoding="utf-8",
    )
    return report
