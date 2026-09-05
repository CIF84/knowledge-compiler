"""Deterministic recursive map-expansion state for SPEC-024."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from .models import ValidationError


DEPTH_EXPANSION_ID = "depth-double-slit-v1"
DEPTH_MAP_VERSION = "spec-024-v1"


@dataclass(frozen=True, slots=True)
class DepthMapState:
    """Open expansion path and selection, independent of camera state."""

    open_path: tuple[str, ...] = ()
    selected_kind: str | None = None
    selected_id: str | None = None


def validate_expansion_registry(registry: Mapping[str, Mapping[str, Any]]) -> None:
    """Fail closed on missing parents, self-parenting, or expansion cycles."""

    for expansion_id, expansion in registry.items():
        if expansion.get("id") != expansion_id:
            raise ValidationError("depth expansion registry identity mismatch")
        parent = expansion.get("parent_expansion_id")
        if parent is not None and parent not in registry:
            raise ValidationError("depth expansion parent is not registered")
        seen: set[str] = set()
        current: str | None = expansion_id
        while current is not None:
            if current in seen:
                raise ValidationError("depth expansion registry contains a cycle")
            seen.add(current)
            current = registry[current].get("parent_expansion_id")


def open_expansion(
    state: DepthMapState,
    registry: Mapping[str, Mapping[str, Any]],
    expansion_id: str,
) -> DepthMapState:
    """Open one registered child only after its parent path is present."""

    validate_expansion_registry(registry)
    if expansion_id not in registry:
        raise ValidationError("depth expansion is not registered")
    expansion = registry[expansion_id]
    parent = expansion.get("parent_expansion_id")
    if parent is not None and parent not in state.open_path:
        raise ValidationError("depth expansion parent is not open")
    if expansion_id in state.open_path:
        return state
    return replace(
        state,
        open_path=state.open_path + (expansion_id,),
        selected_kind=None,
        selected_id=None,
    )


def close_expansion(state: DepthMapState, expansion_id: str) -> DepthMapState:
    """Close an expansion and every descendant after it in the spatial path."""

    if expansion_id not in state.open_path:
        return state
    index = state.open_path.index(expansion_id)
    return replace(
        state,
        open_path=state.open_path[:index],
        selected_kind=None,
        selected_id=None,
    )


def select_depth_item(state: DepthMapState, kind: str, item_id: str) -> DepthMapState:
    if not state.open_path:
        raise ValidationError("cannot select a depth item without an open expansion")
    if kind not in {"concept", "canonical", "explanation"}:
        raise ValidationError("unknown depth item kind")
    return replace(state, selected_kind=kind, selected_id=item_id)


def build_depth_map_packet(projection: Mapping[str, Any]) -> dict[str, Any]:
    """Translate the frozen projection layout into an anchored map expansion."""

    if projection.get("focus_entity_id") != "double-slit-experiment":
        raise ValidationError("SPEC-024 frozen focus identity mismatch")
    layout = projection["layout"]
    if layout.get("strategy") != "FOCUS_CENTERED_RADIAL_WITH_EXPLANATORY_ANCHORS":
        raise ValidationError("SPEC-024 frozen projection layout identity mismatch")
    offset = {"x": 900.0, "y": 1250.0}

    def translate(point: Mapping[str, float]) -> dict[str, float]:
        return {
            "x": float(point["x"]) + offset["x"],
            "y": float(point["y"]) + offset["y"],
        }

    concepts = []
    for item in projection["concepts"]:
        concepts.append({**item, "world": translate(layout["concept_positions"][item["entity_id"]])})
    canonical = []
    routes = {item["canonical_item_id"]: item for item in layout["canonical_edges"]}
    for item in projection["canonical_items"]:
        route = routes[item["id"]]
        canonical.append({**item, "from": translate(route["from"]), "to": translate(route["to"])})
    anchors = {item["explanatory_item_id"]: item for item in layout["explanatory_anchors"]}
    explanations = []
    for item in projection["explanatory_items"]:
        explanations.append({**item, "world": translate(anchors[item["id"]])})
    attachments = [
        {**item, "from": translate(item["from"]), "to": translate(item["to"])}
        for item in layout["explanatory_attachments"]
    ]
    expansion = {
        "id": DEPTH_EXPANSION_ID,
        "parent_expansion_id": None,
        "origin": {
            "entity_id": "double-slit-experiment",
            "relationship_id": "relationship-05b19ee4b6d50060",
            "world": {"x": 1240.0, "y": 1120.0},
        },
        "entrance": translate(layout["concept_positions"]["double-slit-experiment"]),
        "region": {
            "x": offset["x"],
            "y": offset["y"],
            "width": float(layout["width"]),
            "height": float(layout["height"]),
        },
        "expanded_world_bounds": {
            "min_x": 0.0,
            "min_y": 0.0,
            "max_x": 2400.0,
            "max_y": 2050.0,
        },
        "focus_camera": {"x": 900.0, "y": 1120.0, "scale": 1.0},
        "concepts": concepts,
        "canonical_items": canonical,
        "explanatory_items": explanations,
        "explanatory_attachments": attachments,
        "semantic_connection_kind": "SPATIAL_DEPTH_ORIGIN_NOT_CANONICAL_EDGE",
    }
    registry = {DEPTH_EXPANSION_ID: expansion}
    validate_expansion_registry(registry)
    return {
        "version": DEPTH_MAP_VERSION,
        "projection_id": projection["id"],
        "root_expansion_id": DEPTH_EXPANSION_ID,
        "expansions": [expansion],
        "state_model": {
            "open_path": "ORDERED_PARENT_TO_CHILD_EXPANSION_IDS",
            "recursive": True,
            "navigation_mode": "CONTINUOUS_MAP",
            "right_pane_role": "EXPLANATION_AND_EVIDENCE",
        },
    }
