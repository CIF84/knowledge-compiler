"""Camera and attention-state restoration primitives for OPS-002."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Literal

from .continuous_navigation import (
    INITIAL_CAMERA,
    VIEWPORT,
    WORLD_BOUNDS,
    CameraState,
)


INTERFACE_RESTORATION_VERSION = "ops-002-v1"
CAMERA_MIN_SCALE = 0.55
CAMERA_MAX_SCALE = 2.25
CAMERA_INITIAL_SCALE = INITIAL_CAMERA["scale"]
WHEEL_ZOOM_SENSITIVITY = 0.0015

SelectionKind = Literal["node", "edge"]


@dataclass(frozen=True, slots=True)
class InteractionSelection:
    kind: SelectionKind
    identifier: str


def clamp_scale(scale: float) -> float:
    """Clamp camera scale to the deterministic OPS-002 geometric range."""
    return round(min(CAMERA_MAX_SCALE, max(CAMERA_MIN_SCALE, scale)), 6)


def clamp_restored_camera(
    camera: CameraState,
    *,
    bounds: dict[str, float] = WORLD_BOUNDS,
    viewport: dict[str, float] = VIEWPORT,
) -> CameraState:
    """Clamp a scale-aware camera while leaving world coordinates untouched."""
    scale = clamp_scale(camera.scale)
    view_width = viewport["width"] / scale
    view_height = viewport["height"] / scale
    max_x = max(bounds["min_x"], bounds["max_x"] - view_width)
    max_y = max(bounds["min_y"], bounds["max_y"] - view_height)
    return CameraState(
        round(min(max_x, max(bounds["min_x"], camera.x)), 6),
        round(min(max_y, max(bounds["min_y"], camera.y)), 6),
        scale,
    )


def zoom_camera(
    camera: CameraState,
    *,
    screen_anchor: tuple[float, float],
    target_scale: float,
    bounds: dict[str, float] = WORLD_BOUNDS,
    viewport: dict[str, float] = VIEWPORT,
) -> CameraState:
    """Zoom around a logical screen point, preserving its world anchor where bounds permit."""
    scale = clamp_scale(target_scale)
    world_x = camera.x + screen_anchor[0] / camera.scale
    world_y = camera.y + screen_anchor[1] / camera.scale
    return clamp_restored_camera(
        CameraState(
            world_x - screen_anchor[0] / scale,
            world_y - screen_anchor[1] / scale,
            scale,
        ),
        bounds=bounds,
        viewport=viewport,
    )


def wheel_zoom_camera(
    camera: CameraState,
    *,
    screen_anchor: tuple[float, float],
    delta_y: float,
    bounds: dict[str, float] = WORLD_BOUNDS,
    viewport: dict[str, float] = VIEWPORT,
) -> CameraState:
    """Map wheel/trackpad delta to smooth bounded geometric zoom."""
    return zoom_camera(
        camera,
        screen_anchor=screen_anchor,
        target_scale=camera.scale * math.exp(-delta_y * WHEEL_ZOOM_SENSITIVITY),
        bounds=bounds,
        viewport=viewport,
    )


def attention_state(
    fixture: dict[str, Any],
    *,
    persistent: InteractionSelection | None = None,
    preview: InteractionSelection | None = None,
) -> dict[str, dict[str, str]]:
    """Calculate SPEC-006-like focus suppression without changing graph geometry.

    A preview temporarily supplies the visible attention context. The persistent
    selection remains an input and therefore restores exactly when preview ends.
    """
    active = preview or persistent
    node_states = {item["entity_id"]: "NORMAL" for item in fixture["nodes"]}
    edge_states = {item["edge_key"]: "NORMAL" for item in fixture["edges"]}
    if active is None:
        return {"nodes": node_states, "edges": edge_states}

    node_states = {key: "SUBDUED" for key in node_states}
    edge_states = {key: "SUBDUED" for key in edge_states}
    primary = "PREVIEW" if preview is not None else "SELECTED"

    if active.kind == "node":
        if active.identifier not in node_states:
            raise ValueError(f"unknown node selection: {active.identifier}")
        node_states[active.identifier] = primary
        for edge in fixture["edges"]:
            if active.identifier not in (edge["source_entity_id"], edge["target_entity_id"]):
                continue
            edge_states[edge["edge_key"]] = "CONNECTED"
            neighbor = (
                edge["target_entity_id"]
                if edge["source_entity_id"] == active.identifier
                else edge["source_entity_id"]
            )
            node_states[neighbor] = "NEIGHBOR"
    else:
        edge_by_key = {item["edge_key"]: item for item in fixture["edges"]}
        if active.identifier not in edge_by_key:
            raise ValueError(f"unknown relationship selection: {active.identifier}")
        edge = edge_by_key[active.identifier]
        edge_states[active.identifier] = primary
        node_states[edge["source_entity_id"]] = "ENDPOINT"
        node_states[edge["target_entity_id"]] = "ENDPOINT"

    return {"nodes": node_states, "edges": edge_states}


def state_counts(states: dict[str, dict[str, str]]) -> dict[str, dict[str, int]]:
    """Return deterministic attention-state counts for diagnostics."""
    result: dict[str, dict[str, int]] = {}
    for kind in ("nodes", "edges"):
        counts: dict[str, int] = {}
        for value in states[kind].values():
            counts[value] = counts.get(value, 0) + 1
        result[kind] = dict(sorted(counts.items()))
    return result
