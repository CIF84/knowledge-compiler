"""Deterministic synchronized navigation/learning workspace for SPEC-019."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Literal

from .continuous_navigation import VIEWPORT, CameraState, canonical_navigation_bytes
from .interface_restoration import clamp_restored_camera
from .models import ValidationError


WORKSPACE_VERSION = "spec-019-v1"
WORKSPACE_BOUNDS = {"min_x": 0.0, "min_y": 0.0, "max_x": 2400.0, "max_y": 1500.0}
WORKSPACE_INITIAL_CAMERA = {"x": 0.0, "y": 0.0, "scale": 1.0}
NODE_HALF_WIDTH = 84.0
NODE_HALF_HEIGHT = 30.0
DOMAIN_OFFSETS = {
    "software_architecture": (80.0, 80.0),
    "economics": (1050.0, 80.0),
    "history": (80.0, 760.0),
    "electromagnetism": (1160.0, 800.0),
}
DOMAIN_LABELS = {
    "software_architecture": "Software Architecture",
    "economics": "Economics",
    "history": "History of Printing",
    "electromagnetism": "Electromagnetism",
}
SALIENCE_RANK = {"PRIMARY": 0, "SECONDARY": 1, "SPARSE": 2}


@dataclass(frozen=True, slots=True)
class WorkspaceState:
    camera: CameraState
    domain_id: str
    representation_index: int
    focused_entity_id: str | None = None
    focused_relationship_id: str | None = None


def _source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _node_positions(payload: dict[str, Any]) -> dict[str, dict[str, float]]:
    positions: dict[str, dict[str, float]] = {}
    for representation in sorted(
        payload["representations"], key=lambda item: SALIENCE_RANK.get(item["salience"], 99)
    ):
        for node in representation["layout"]["nodes"]:
            positions.setdefault(node["entity_id"], {"x": float(node["x"]), "y": float(node["y"])})
    return positions


def _boundary_point(source: dict[str, float], target: dict[str, float]) -> tuple[float, float]:
    dx = target["x"] - source["x"]
    dy = target["y"] - source["y"]
    if not dx and not dy:
        return source["x"], source["y"]
    tx = NODE_HALF_WIDTH / abs(dx) if dx else math.inf
    ty = NODE_HALF_HEIGHT / abs(dy) if dy else math.inf
    scale = min(tx, ty)
    return source["x"] + dx * scale, source["y"] + dy * scale


def _route(source: dict[str, float], target: dict[str, float]) -> dict[str, Any]:
    """Reuse the BASELINE-002 orthogonal camera-world routing primitive."""
    start = _boundary_point(source, target)
    end = _boundary_point(target, source)
    if abs(start[1] - end[1]) < 1:
        return {
            "path_kind": "LINE",
            "points": ({"x": start[0], "y": start[1]}, {"x": end[0], "y": end[1]}),
            "label_x": round((start[0] + end[0]) / 2, 3),
            "label_y": round((start[1] + end[1]) / 2 - 10, 3),
        }
    midpoint_x = (start[0] + end[0]) / 2
    return {
        "path_kind": "CUBIC",
        "points": (
            {"x": start[0], "y": start[1]},
            {"x": midpoint_x, "y": start[1]},
            {"x": midpoint_x, "y": end[1]},
            {"x": end[0], "y": end[1]},
        ),
        "label_x": round(midpoint_x, 3),
        "label_y": round((start[1] + end[1]) / 2 - 8, 3),
    }


def build_workspace_fixture(spec_006_dir: Path) -> dict[str, Any]:
    """Compose frozen heterogeneous representations into one navigable world."""
    domains = []
    navigation_nodes: list[dict[str, Any]] = []
    navigation_edges: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    adjacency: dict[str, list[str]] = {}
    seen_entities: set[str] = set()
    seen_edges: set[str] = set()

    for domain_id in DOMAIN_OFFSETS:
        source_path = spec_006_dir / f"{domain_id}.representation.json"
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        if not payload["representations"]:
            continue
        offset_x, offset_y = DOMAIN_OFFSETS[domain_id]
        local_positions = _node_positions(payload)
        entity_by_id: dict[str, dict[str, Any]] = {}
        for representation in payload["representations"]:
            for node in representation["nodes"]:
                entity_by_id.setdefault(node["entity_id"], node)
        domain_node_ids = sorted(entity_by_id)
        for entity_id in domain_node_ids:
            if entity_id in seen_entities:
                raise ValidationError(f"workspace entity ID is not globally unique: {entity_id}")
            seen_entities.add(entity_id)
            local = local_positions[entity_id]
            navigation_nodes.append({
                **entity_by_id[entity_id],
                "domain_id": domain_id,
                "world": {"x": local["x"] + offset_x, "y": local["y"] + offset_y},
            })
            adjacency[entity_id] = []

        edge_by_key: dict[str, dict[str, Any]] = {}
        for representation in payload["representations"]:
            for edge in representation["edges"]:
                edge_by_key.setdefault(edge["edge_key"], edge)
        for edge_key in sorted(edge_by_key):
            edge = edge_by_key[edge_key]
            if edge_key in seen_edges:
                raise ValidationError(f"workspace edge key is not globally unique: {edge_key}")
            seen_edges.add(edge_key)
            navigation_edges.append({**edge, "domain_id": domain_id})
            source = next(item["world"] for item in navigation_nodes if item["entity_id"] == edge["source_entity_id"])
            target = next(item["world"] for item in navigation_nodes if item["entity_id"] == edge["target_entity_id"])
            routes.append({"edge_key": edge_key, **_route(source, target)})
            adjacency[edge["source_entity_id"]].append(edge["target_entity_id"])
            adjacency[edge["target_entity_id"]].append(edge["source_entity_id"])

        max_width = max(item["layout"]["width"] for item in payload["representations"])
        max_height = max(item["layout"]["height"] for item in payload["representations"])
        domains.append({
            "domain_id": domain_id,
            "label": DOMAIN_LABELS[domain_id],
            "source_path": str(source_path),
            "source_sha256": _source_hash(source_path),
            "composition_status": "UNCHANGED_SPEC_006_REPRESENTATIONS_EMBEDDED_FOR_UI_INTEGRATION",
            "world_region": {
                "x": offset_x, "y": offset_y,
                "width": float(max_width), "height": float(max_height),
            },
            "learning_model": payload,
        })

    for values in adjacency.values():
        values.sort()
    fixture = {
        "version": WORKSPACE_VERSION,
        "fixture_status": "COMPOSED_EXISTING_DETERMINISTIC_SPEC_006_REPRESENTATIONS_NOT_SINGLE_EXTRACTED_WORLD",
        "provenance_note": "No cross-domain semantic relationships were added; domain regions are presentation-only context.",
        "domains": domains,
        "navigation": {
            "nodes": navigation_nodes,
            "edges": navigation_edges,
            "adjacency": adjacency,
            "world": {
                "bounds": WORKSPACE_BOUNDS,
                "layout_strategy": "OFFSET_COMPOSITION_OF_FROZEN_STRUCTURE_AWARE_LAYOUTS",
                "node_positions_stable": True,
                "routes": routes,
            },
            "camera": {
                "initial": WORKSPACE_INITIAL_CAMERA,
                "viewport": VIEWPORT,
                "transform": "SVG_VIEWBOX_WORLD_TO_VIEWPORT",
                "zoom": {
                    "kind": "GEOMETRIC_ONLY", "min_scale": 0.55, "max_scale": 2.25,
                    "initial_scale": 1.0, "pointer_centered": True, "wheel_sensitivity": 0.0015,
                },
                "focus_animation_ms": 280,
            },
        },
        "workspace": {
            "default_domain_id": "software_architecture",
            "default_representation_index": 0,
            "default_focused_entity_id": "modular-order-processing-service",
            "shared_focus": "ENTITY_ID_OR_RELATIONSHIP_ID",
            "camera_independent_from_semantic_focus": True,
            "parent_context": "DOMAIN / REPRESENTATION / FOCUS",
        },
    }
    validate_workspace_fixture(fixture)
    return fixture


def validate_workspace_fixture(fixture: dict[str, Any]) -> None:
    nodes = fixture["navigation"]["nodes"]
    edges = fixture["navigation"]["edges"]
    node_ids = {item["entity_id"] for item in nodes}
    if len(node_ids) != len(nodes):
        raise ValidationError("workspace navigation entity IDs must be globally unique")
    if any(edge["source_entity_id"] not in node_ids or edge["target_entity_id"] not in node_ids for edge in edges):
        raise ValidationError("workspace edge references an unknown entity")
    learning_entity_ids = {
        node["entity_id"]
        for domain in fixture["domains"]
        for representation in domain["learning_model"]["representations"]
        for node in representation["nodes"]
    }
    learning_relationship_ids = {
        relationship_id
        for domain in fixture["domains"]
        for representation in domain["learning_model"]["representations"]
        for edge in representation["edges"]
        for relationship_id in edge["relationship_ids"]
    }
    navigation_relationship_ids = {
        relationship_id for edge in edges for relationship_id in edge["relationship_ids"]
    }
    if node_ids != learning_entity_ids:
        raise ValidationError("navigation and learning entity ID sets must match exactly")
    if navigation_relationship_ids != learning_relationship_ids:
        raise ValidationError("navigation and learning relationship ID sets must match exactly")
    if not all(domain["composition_status"].startswith("UNCHANGED_SPEC_006") for domain in fixture["domains"]):
        raise ValidationError("workspace composed fixture provenance must remain explicit")


def _domain(fixture: dict[str, Any], domain_id: str) -> dict[str, Any]:
    return next(item for item in fixture["domains"] if item["domain_id"] == domain_id)


def _context_for_entity(
    fixture: dict[str, Any], entity_id: str, preferred_domain_id: str | None = None
) -> tuple[str, int]:
    candidates = []
    for domain in fixture["domains"]:
        for index, representation in enumerate(domain["learning_model"]["representations"]):
            if any(node["entity_id"] == entity_id for node in representation["nodes"]):
                preferred = 0 if domain["domain_id"] == preferred_domain_id else 1
                candidates.append((preferred, SALIENCE_RANK.get(representation["salience"], 99), domain["domain_id"], index))
    if not candidates:
        raise ValueError(f"no learning context for entity ID: {entity_id}")
    _, _, domain_id, index = min(candidates)
    return domain_id, index


def _context_for_relationship(fixture: dict[str, Any], relationship_id: str) -> tuple[str, int]:
    candidates = []
    for domain in fixture["domains"]:
        for index, representation in enumerate(domain["learning_model"]["representations"]):
            if any(relationship_id in edge["relationship_ids"] for edge in representation["edges"]):
                candidates.append((SALIENCE_RANK.get(representation["salience"], 99), domain["domain_id"], index))
    if not candidates:
        raise ValueError(f"no learning context for relationship ID: {relationship_id}")
    _, domain_id, index = min(candidates)
    return domain_id, index


def _point_visible(camera: CameraState, point: dict[str, float], margin: float = 0.0) -> bool:
    width = VIEWPORT["width"] / camera.scale
    height = VIEWPORT["height"] / camera.scale
    return (
        camera.x + margin <= point["x"] <= camera.x + width - margin
        and camera.y + margin <= point["y"] <= camera.y + height - margin
    )


def camera_for_entity(fixture: dict[str, Any], camera: CameraState, entity_id: str) -> CameraState:
    node_by_id = {item["entity_id"]: item for item in fixture["navigation"]["nodes"]}
    point = node_by_id[entity_id]["world"]
    width = VIEWPORT["width"] / camera.scale
    height = VIEWPORT["height"] / camera.scale
    comfortable = (
        camera.x + width * 0.22 <= point["x"] <= camera.x + width * 0.78
        and camera.y + height * 0.20 <= point["y"] <= camera.y + height * 0.80
    )
    adjacent_outside = any(
        not _point_visible(camera, node_by_id[neighbor]["world"], NODE_HALF_WIDTH)
        for neighbor in fixture["navigation"]["adjacency"][entity_id]
    )
    if comfortable and not adjacent_outside:
        return camera
    return clamp_restored_camera(
        CameraState(point["x"] - width / 2, point["y"] - height / 2, camera.scale),
        bounds=fixture["navigation"]["world"]["bounds"], viewport=VIEWPORT,
    )


def initial_workspace_state(fixture: dict[str, Any]) -> WorkspaceState:
    workspace = fixture["workspace"]
    return WorkspaceState(
        camera=CameraState(**fixture["navigation"]["camera"]["initial"]),
        domain_id=workspace["default_domain_id"],
        representation_index=workspace["default_representation_index"],
        focused_entity_id=workspace["default_focused_entity_id"],
    )


def synchronize_focus(
    fixture: dict[str, Any],
    state: WorkspaceState,
    *,
    origin: Literal["navigation", "learning"],
    kind: Literal["entity", "relationship"],
    stable_id: str,
) -> WorkspaceState:
    """Synchronize by stable IDs while keeping camera and semantics separate."""
    if kind == "entity":
        domain_id, representation_index = _context_for_entity(fixture, stable_id, state.domain_id)
        camera = camera_for_entity(fixture, state.camera, stable_id)
        return WorkspaceState(camera, domain_id, representation_index, stable_id, None)
    domain_id, representation_index = _context_for_relationship(fixture, stable_id)
    return WorkspaceState(state.camera, domain_id, representation_index, None, stable_id)


def change_camera(state: WorkspaceState, camera: CameraState) -> WorkspaceState:
    """Change only navigation camera state; learning focus remains byte-for-byte equal."""
    return replace(state, camera=camera)


def switch_learning_representation(state: WorkspaceState, representation_index: int) -> WorkspaceState:
    """Switch a representation preset without moving the navigation camera."""
    return replace(state, representation_index=representation_index)


def context_path(fixture: dict[str, Any], state: WorkspaceState) -> list[str]:
    domain = _domain(fixture, state.domain_id)
    representation = domain["learning_model"]["representations"][state.representation_index]
    focus = state.focused_entity_id or state.focused_relationship_id
    return [domain["label"], representation["title"], focus or "Overview"]


def canonical_workspace_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def state_dict(state: WorkspaceState) -> dict[str, Any]:
    return asdict(state)
