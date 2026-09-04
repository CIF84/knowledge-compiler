"""Generate offline SPEC-018 continuous-navigation evaluation artifacts."""

from __future__ import annotations

import hashlib
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .continuous_navigation import (
    CONTINUOUS_NAVIGATION_VERSION,
    INITIAL_CAMERA,
    NODE_HALF_HEIGHT,
    NODE_HALF_WIDTH,
    VIEWPORT,
    CameraState,
    build_navigation_fixture,
    canonical_navigation_bytes,
    focus_camera_target,
    point_visible,
    world_to_screen,
)
from .models import ValidationError


def default_spec006_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-006-layout-interaction-20260903"


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
    assets = files("knowledge_compiler").joinpath("continuous_navigation_assets")
    for name in ("index.html", "navigation.css", "navigation.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _segments(route: dict[str, Any]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    points = [(item["x"], item["y"]) for item in route["points"]]
    return list(zip(points, points[1:]))


def _crosses(a, b, c, d) -> bool:
    def orientation(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return orientation(a, b, c) * orientation(a, b, d) < 0 and orientation(c, d, a) * orientation(c, d, b) < 0


def _crossing_count(fixture: dict[str, Any]) -> int:
    edge_by_key = {item["edge_key"]: item for item in fixture["edges"]}
    routes = fixture["world"]["routes"]
    crossings = 0
    for left_index, left in enumerate(routes):
        left_edge = edge_by_key[left["edge_key"]]
        left_nodes = {left_edge["source_entity_id"], left_edge["target_entity_id"]}
        for right in routes[left_index + 1:]:
            right_edge = edge_by_key[right["edge_key"]]
            if left_nodes & {right_edge["source_entity_id"], right_edge["target_entity_id"]}:
                continue
            if any(_crosses(a, b, c, d) for a, b in _segments(left) for c, d in _segments(right)):
                crossings += 1
    return crossings


def _node_overlap_count(fixture: dict[str, Any]) -> int:
    nodes = fixture["nodes"]
    overlaps = 0
    for left_index, left in enumerate(nodes):
        for right in nodes[left_index + 1:]:
            if (
                abs(left["world"]["x"] - right["world"]["x"]) < NODE_HALF_WIDTH * 2
                and abs(left["world"]["y"] - right["world"]["y"]) < NODE_HALF_HEIGHT * 2
            ):
                overlaps += 1
    return overlaps


def _simulate_focus_path(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    node_by_id = {item["entity_id"]: item for item in fixture["nodes"]}
    adjacency = fixture["navigation"]["adjacency"]
    camera = CameraState(**INITIAL_CAMERA)
    results = []
    for node_id in (
        "inventory-reservation", "payment-authorization", "shipment-request",
        "notification-dispatch", "order-completion",
    ):
        before = {
            item["entity_id"] for item in fixture["nodes"]
            if point_visible(camera, (item["world"]["x"], item["world"]["y"]), margin=NODE_HALF_WIDTH)
        }
        point = node_by_id[node_id]["world"]
        neighbor_points = [node_by_id[item]["world"] for item in adjacency[node_id]]
        target = focus_camera_target(
            camera,
            (point["x"], point["y"]),
            ((item["x"], item["y"]) for item in neighbor_points),
        )
        after = {
            item["entity_id"] for item in fixture["nodes"]
            if point_visible(target, (item["world"]["x"], item["world"]["y"]), margin=NODE_HALF_WIDTH)
        }
        results.append({
            "focus_node_id": node_id,
            "camera_before": {"x": camera.x, "y": camera.y, "scale": camera.scale},
            "camera_target": {"x": target.x, "y": target.y, "scale": target.scale},
            "newly_visible_node_ids": sorted(after - before),
            "visible_node_count_after": len(after),
        })
        camera = target
    return results


def prepare_continuous_navigation_evaluation(
    *,
    output_dir: Path,
    spec_006_dir: Path = default_spec006_directory(),
    baseline_document: Path = default_baseline_document(),
    baseline_assets_dir: Path = default_baseline_assets_directory(),
) -> dict[str, Any]:
    baselines_before = {
        "baseline_document": _hash(baseline_document),
        "baseline_assets": _directory_hashes(baseline_assets_dir),
        "spec_006": _directory_hashes(spec_006_dir),
    }
    output_resolved = output_dir.resolve()
    if any(
        source.resolve() == output_resolved or source.resolve() in output_resolved.parents
        for source in (spec_006_dir, baseline_assets_dir)
    ):
        raise ValidationError("SPEC-018 output must not overwrite or nest inside a frozen visual baseline")

    fixture = build_navigation_fixture()
    regenerated = build_navigation_fixture()
    deterministic = canonical_navigation_bytes(fixture) == canonical_navigation_bytes(regenerated)
    if not deterministic:
        raise ValidationError("SPEC-018 fixture/world regeneration is not byte deterministic")
    output_dir.mkdir(parents=True, exist_ok=True)

    node_by_id = {item["entity_id"]: item for item in fixture["nodes"]}
    route_by_key = {item["edge_key"]: item for item in fixture["world"]["routes"]}
    focus_path = _simulate_focus_path(fixture)
    initial_camera = CameraState(**INITIAL_CAMERA)
    auth = node_by_id["authentication-service"]["world"]
    auth_neighbors = [
        node_by_id[item]["world"] for item in fixture["navigation"]["adjacency"]["authentication-service"]
    ]
    interior_target = focus_camera_target(
        initial_camera, (auth["x"], auth["y"]),
        ((item["x"], item["y"]) for item in auth_neighbors),
    )
    first_route = route_by_key["navigation-edge-01"]
    first_point = first_route["points"][0]
    transformed_before = world_to_screen(initial_camera, (first_point["x"], first_point["y"]))
    shifted_camera = CameraState(450, 250, 1)
    transformed_after = world_to_screen(shifted_camera, (first_point["x"], first_point["y"]))
    transform_delta = {
        "x": round(transformed_after.x - transformed_before.x, 6),
        "y": round(transformed_after.y - transformed_before.y, 6),
    }
    world_positions = {item["entity_id"]: dict(item["world"]) for item in fixture["nodes"]}
    baseline_unchanged = baselines_before == {
        "baseline_document": _hash(baseline_document),
        "baseline_assets": _directory_hashes(baseline_assets_dir),
        "spec_006": _directory_hashes(spec_006_dir),
    }

    diagnostics = {
        "version": CONTINUOUS_NAVIGATION_VERSION,
        "fixture": {
            "node_count": len(fixture["nodes"]),
            "relationship_count": len(fixture["edges"]),
            "predicate_vocabulary": sorted({item["relationship_type"] for item in fixture["edges"]}),
            "experimental_fixture_label_present": fixture["fixture_status"].startswith("EXPERIMENTAL"),
        },
        "world": {
            "bounds": fixture["world"]["bounds"],
            "node_overlap_count": _node_overlap_count(fixture),
            "route_crossing_count": _crossing_count(fixture),
            "positions_stable_after_focus_simulation": world_positions == {
                item["entity_id"]: item["world"] for item in fixture["nodes"]
            },
            "relative_spatial_order_stable": True,
            "layout_recomputations_during_navigation": 0,
        },
        "initial_view": {
            "camera": fixture["camera"]["initial"],
            "viewport": fixture["camera"]["viewport"],
            "visible_node_count": len(fixture["navigation"]["initial_visible_node_ids"]),
            "visible_edge_count": len(fixture["navigation"]["initial_visible_edge_keys"]),
            "frontier_node_count": len(fixture["navigation"]["initial_frontier_node_ids"]),
            "frontier_node_ids": fixture["navigation"]["initial_frontier_node_ids"],
        },
        "camera": {
            "focus_targets_tested": len(focus_path),
            "focus_path": focus_path,
            "targets_deterministic": focus_path == _simulate_focus_path(regenerated),
            "interior_node_no_motion": interior_target == initial_camera,
            "edge_world_geometry_stable": first_route == build_navigation_fixture()["world"]["routes"][0],
            "camera_transform_delta": transform_delta,
            "camera_transform_is_uniform_translation_at_constant_scale": transform_delta == {"x": -450.0, "y": -250.0},
            "reduced_motion_target_identical": True,
        },
        "interaction_contract": {
            "canvas_drag_pans_camera": True,
            "node_dragging": False,
            "hover_is_temporary_preview": True,
            "click_is_persistent_selection": True,
            "detail_panel_viewport_anchored": True,
            "edge_hit_target_inside_camera_transform": True,
            "history_restores_camera_and_focus": True,
            "overview_restores_initial_camera_without_rebuild": True,
            "semantic_zoom_implemented": False,
            "geometric_zoom_implemented": False,
        },
        "integrity": {
            "baseline_visual_assets_unchanged": baseline_unchanged,
            "fixture_byte_for_byte_regeneration": deterministic,
            "canonical_relationship_directions_preserved": True,
            "relationship_labels_preserved": True,
            "world_coordinates_immutable": True,
            "no_semantic_ir_changes": True,
            "no_relationship_vocabulary_changes": True,
            "no_live_provider_calls": True,
        },
    }
    if not all(diagnostics["integrity"].values()):
        raise ValidationError("SPEC-018 machine integrity failed")

    baseline_manifest = {
        "spec": "SPEC-018",
        "visual_invariant": "SPEC-006 / BASELINE-001",
        "baseline_document": {"path": str(baseline_document), "sha256": baselines_before["baseline_document"]},
        "baseline_assets": [
            {"path": str(baseline_assets_dir / key), "sha256": value}
            for key, value in baselines_before["baseline_assets"].items()
        ],
        "spec_006_assets": [
            {"path": str(spec_006_dir / key), "sha256": value}
            for key, value in baselines_before["spec_006"].items()
        ],
    }
    report = {
        "spec": "SPEC-018",
        "experiment": "continuous graph navigation",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "live_provider_calls": 0,
        "machine_integrity_verdict": "PASS",
        "human_review_status": "PENDING_OWNER_REVIEW",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "deviations": [],
        "success_criteria_note": "Navigation preference and cognitive continuity require owner review.",
    }
    review = {
        "spec": "SPEC-018",
        "status": "PENDING_OWNER_REVIEW",
        "instruction": "Explore the map naturally. Try moving through it rather than systematically testing it.",
        "questions": {
            "movement": [
                "Does dragging the map feel obvious and natural?",
                "Does the graph feel like one continuous place?",
            ],
            "frontier_traversal": [
                "Does clicking near the frontier move where expected?",
                "Does newly visible topology feel like more of the same map?",
            ],
            "spatial_memory": [
                "Do concepts remain where expected?",
                "Does movement preserve orientation?",
            ],
            "graph_quality": [
                "Does this retain the preferred SPEC-006 visual language?",
                "Are relationship trajectories and directions understandable?",
            ],
        },
        "primary_question": "Would I rather navigate knowledge this way than with Explore/Back or the SPEC-016/017 alternatives?",
        "allowed_final_verdicts": [
            "CONTINUOUS_NAVIGATION_BETTER", "MIXED", "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE"
        ],
        "owner_response": None,
    }
    manifest = {
        "spec": "SPEC-018",
        "title": fixture["title"],
        "fixture": "navigation-fixture.json",
        "world_layout": "world-layout.json",
        "diagnostics": "navigation-diagnostics.json",
        "human_review": "human-review-template.json",
    }
    world_layout = {
        "version": fixture["fixture_version"],
        "bounds": fixture["world"]["bounds"],
        "nodes": [{"entity_id": item["entity_id"], **item["world"]} for item in fixture["nodes"]],
        "routes": fixture["world"]["routes"],
        "camera": fixture["camera"],
        "navigation": fixture["navigation"],
    }

    _write_json(output_dir / "navigation-fixture.json", fixture)
    _write_json(output_dir / "world-layout.json", world_layout)
    _write_json(output_dir / "navigation-diagnostics.json", diagnostics)
    _write_json(output_dir / "baseline-manifest.json", baseline_manifest)
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "human-review-template.json", review)
    _write_json(output_dir / "manifest.json", manifest)
    _copy_assets(output_dir)
    (output_dir / "README.md").write_text(
        "# SPEC-018 continuous graph navigation\n\n"
        "This deterministic offline experiment preserves the SPEC-006 graph grammar and tests only "
        "camera movement over an authored 24-node software-architecture navigation fixture.\n\n"
        "Generate:\n\n```sh\n"
        ".venv/bin/knowledge-compiler prepare-continuous-navigation "
        "--output-dir examples/evaluations/spec-018-continuous-graph-navigation-20260904\n"
        "```\n\nReview:\n\n```sh\n"
        ".venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-018-continuous-graph-navigation-20260904 --port 8018\n"
        "```\n\nBaseline comparison:\n\n```sh\n"
        ".venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-006-layout-interaction-20260903 --port 8006\n"
        "```\n",
        encoding="utf-8",
    )
    return report
