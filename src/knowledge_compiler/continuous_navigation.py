"""Deterministic world/camera model for the SPEC-018 navigation experiment."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .models import EntityType, RelationshipType, ValidationError
from .relationships import relationship_definition_map


CONTINUOUS_NAVIGATION_VERSION = "spec-018-v1"
WORLD_BOUNDS = {"min_x": 0.0, "min_y": 0.0, "max_x": 2920.0, "max_y": 1340.0}
INITIAL_CAMERA = {"x": 0.0, "y": 0.0, "scale": 1.0}
VIEWPORT = {"width": 1200.0, "height": 800.0}
NODE_HALF_WIDTH = 84.0
NODE_HALF_HEIGHT = 30.0
COMFORT_MARGIN_X = 0.22
COMFORT_MARGIN_Y = 0.20


@dataclass(frozen=True, slots=True)
class CameraState:
    x: float
    y: float
    scale: float = 1.0


@dataclass(frozen=True, slots=True)
class ScreenPoint:
    x: float
    y: float


def clamp_camera(camera: CameraState) -> CameraState:
    view_width = VIEWPORT["width"] / camera.scale
    view_height = VIEWPORT["height"] / camera.scale
    max_x = max(WORLD_BOUNDS["min_x"], WORLD_BOUNDS["max_x"] - view_width)
    max_y = max(WORLD_BOUNDS["min_y"], WORLD_BOUNDS["max_y"] - view_height)
    return CameraState(
        round(min(max_x, max(WORLD_BOUNDS["min_x"], camera.x)), 6),
        round(min(max_y, max(WORLD_BOUNDS["min_y"], camera.y)), 6),
        camera.scale,
    )


def world_to_screen(camera: CameraState, point: tuple[float, float]) -> ScreenPoint:
    return ScreenPoint(
        round((point[0] - camera.x) * camera.scale, 6),
        round((point[1] - camera.y) * camera.scale, 6),
    )


def screen_to_world(camera: CameraState, point: tuple[float, float]) -> ScreenPoint:
    return ScreenPoint(
        round(camera.x + point[0] / camera.scale, 6),
        round(camera.y + point[1] / camera.scale, 6),
    )


def drag_pan(
    camera: CameraState,
    screen_dx: float,
    screen_dy: float,
    *,
    rendered_width: float = VIEWPORT["width"],
    rendered_height: float = VIEWPORT["height"],
) -> CameraState:
    view_width = VIEWPORT["width"] / camera.scale
    view_height = VIEWPORT["height"] / camera.scale
    return clamp_camera(CameraState(
        camera.x - screen_dx * view_width / rendered_width,
        camera.y - screen_dy * view_height / rendered_height,
        camera.scale,
    ))


def point_visible(camera: CameraState, point: tuple[float, float], *, margin: float = 0.0) -> bool:
    width = VIEWPORT["width"] / camera.scale
    height = VIEWPORT["height"] / camera.scale
    return (
        camera.x + margin <= point[0] <= camera.x + width - margin
        and camera.y + margin <= point[1] <= camera.y + height - margin
    )


def point_comfortable(camera: CameraState, point: tuple[float, float]) -> bool:
    width = VIEWPORT["width"] / camera.scale
    height = VIEWPORT["height"] / camera.scale
    return (
        camera.x + width * COMFORT_MARGIN_X <= point[0] <= camera.x + width * (1 - COMFORT_MARGIN_X)
        and camera.y + height * COMFORT_MARGIN_Y <= point[1] <= camera.y + height * (1 - COMFORT_MARGIN_Y)
    )


def focus_camera_target(
    camera: CameraState,
    point: tuple[float, float],
    adjacent_points: Iterable[tuple[float, float]],
) -> CameraState:
    adjacent_outside = any(not point_visible(camera, neighbor, margin=NODE_HALF_WIDTH) for neighbor in adjacent_points)
    if point_comfortable(camera, point) and not adjacent_outside:
        return camera
    width = VIEWPORT["width"] / camera.scale
    height = VIEWPORT["height"] / camera.scale
    return clamp_camera(CameraState(point[0] - width / 2, point[1] - height / 2, camera.scale))


def _node(
    node_id: str, label: str, description: str, entity_type: EntityType, x: int, y: int
) -> dict[str, Any]:
    return {
        "entity_id": node_id,
        "label": label,
        "description": description,
        "entity_type": entity_type.value,
        "world": {"x": x, "y": y},
    }


def _nodes() -> list[dict[str, Any]]:
    rows = (
        ("customer-request", "customer request", "A request to place an order.", EntityType.PROCESS, 250, 650),
        ("order-validation", "order validation", "The step that validates an incoming order.", EntityType.PROCESS, 650, 650),
        ("inventory-reservation", "inventory reservation", "The step that reserves available inventory.", EntityType.PROCESS, 1050, 650),
        ("payment-authorization", "payment authorization", "The step that authorizes payment.", EntityType.PROCESS, 1450, 650),
        ("shipment-request", "shipment request", "The step that requests shipment fulfillment.", EntityType.PROCESS, 1850, 650),
        ("notification-dispatch", "notification dispatch", "The step that dispatches an order notification.", EntityType.PROCESS, 2250, 650),
        ("order-completion", "order completion", "The terminal order-processing step.", EntityType.PROCESS, 2650, 650),
        ("api-gateway", "API gateway", "Entry component for customer order requests.", EntityType.COMPONENT, 250, 280),
        ("authentication-service", "authentication service", "Service that authenticates incoming requests.", EntityType.COMPONENT, 650, 220),
        ("identity-store", "identity store", "Durable identity data used during authentication.", EntityType.COMPONENT, 1050, 160),
        ("fraud-service", "fraud service", "Service used during payment risk checks.", EntityType.COMPONENT, 1450, 260),
        ("payment-provider", "payment provider", "External destination for payment authorization.", EntityType.SYSTEM, 1750, 180),
        ("shipping-adapter", "shipping adapter", "Component connecting order processing to shipping.", EntityType.COMPONENT, 2150, 260),
        ("email-provider", "email provider", "External destination for order email delivery.", EntityType.SYSTEM, 2550, 180),
        ("order-service", "order service", "Component coordinating order processing.", EntityType.COMPONENT, 650, 1000),
        ("order-database", "order database", "Durable store for order state.", EntityType.COMPONENT, 950, 1200),
        ("inventory-service", "inventory service", "Component managing inventory reservations.", EntityType.COMPONENT, 1150, 960),
        ("inventory-database", "inventory database", "Durable store for inventory state.", EntityType.COMPONENT, 1450, 1200),
        ("payment-service", "payment service", "Component coordinating payment authorization.", EntityType.COMPONENT, 1550, 960),
        ("message-broker", "message broker", "Infrastructure carrying asynchronous processing events.", EntityType.COMPONENT, 1950, 1080),
        ("notification-service", "notification service", "Component coordinating outbound notifications.", EntityType.COMPONENT, 2350, 960),
        ("audit-log", "audit log", "Durable record of processing events.", EntityType.COMPONENT, 2750, 1160),
        ("observability-collector", "observability collector", "Component collecting processing measurements.", EntityType.COMPONENT, 2050, 500),
        ("metrics-store", "metrics store", "Durable store for collected measurements.", EntityType.COMPONENT, 2450, 400),
    )
    return [_node(*row) for row in rows]


def _edge_rows() -> tuple[tuple[str, str, RelationshipType, str], ...]:
    return (
        ("customer-request", "order-validation", RelationshipType.PRECEDES, "The customer request precedes order validation."),
        ("order-validation", "inventory-reservation", RelationshipType.PRECEDES, "Order validation precedes inventory reservation."),
        ("inventory-reservation", "payment-authorization", RelationshipType.PRECEDES, "Inventory reservation precedes payment authorization."),
        ("payment-authorization", "shipment-request", RelationshipType.PRECEDES, "Payment authorization precedes the shipment request."),
        ("shipment-request", "notification-dispatch", RelationshipType.PRECEDES, "The shipment request precedes notification dispatch."),
        ("notification-dispatch", "order-completion", RelationshipType.PRECEDES, "Notification dispatch precedes order completion."),
        ("customer-request", "api-gateway", RelationshipType.REQUIRES, "The customer request requires the API gateway as its entry component."),
        ("order-validation", "authentication-service", RelationshipType.REQUIRES, "Order validation requires the authentication service."),
        ("authentication-service", "identity-store", RelationshipType.REQUIRES, "The authentication service requires the identity store."),
        ("order-validation", "order-service", RelationshipType.REQUIRES, "Order validation requires the order service."),
        ("order-service", "order-database", RelationshipType.REQUIRES, "The order service requires the order database."),
        ("inventory-reservation", "inventory-service", RelationshipType.REQUIRES, "Inventory reservation requires the inventory service."),
        ("inventory-service", "inventory-database", RelationshipType.REQUIRES, "The inventory service requires the inventory database."),
        ("payment-authorization", "payment-service", RelationshipType.REQUIRES, "Payment authorization requires the payment service."),
        ("payment-service", "payment-provider", RelationshipType.REQUIRES, "The payment service requires the payment provider."),
        ("payment-service", "fraud-service", RelationshipType.REQUIRES, "The payment service requires the fraud service."),
        ("shipment-request", "shipping-adapter", RelationshipType.REQUIRES, "The shipment request requires the shipping adapter."),
        ("notification-dispatch", "notification-service", RelationshipType.REQUIRES, "Notification dispatch requires the notification service."),
        ("notification-service", "email-provider", RelationshipType.REQUIRES, "The notification service requires the email provider."),
        ("notification-service", "message-broker", RelationshipType.REQUIRES, "The notification service requires the message broker."),
        ("order-service", "message-broker", RelationshipType.REQUIRES, "The order service requires the message broker."),
        ("inventory-service", "message-broker", RelationshipType.REQUIRES, "The inventory service requires the message broker."),
        ("payment-authorization", "observability-collector", RelationshipType.MEASURED_BY, "Payment authorization is measured by the observability collector."),
        ("shipment-request", "observability-collector", RelationshipType.MEASURED_BY, "The shipment request is measured by the observability collector."),
        ("notification-dispatch", "observability-collector", RelationshipType.MEASURED_BY, "Notification dispatch is measured by the observability collector."),
        ("observability-collector", "metrics-store", RelationshipType.REQUIRES, "The observability collector requires the metrics store."),
        ("order-service", "audit-log", RelationshipType.CREATES, "The order service creates audit-log records."),
        ("payment-service", "audit-log", RelationshipType.CREATES, "The payment service creates audit-log records."),
    )


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
    start = _boundary_point(source, target)
    end = _boundary_point(target, source)
    if abs(start[1] - end[1]) < 1:
        points = ({"x": start[0], "y": start[1]}, {"x": end[0], "y": end[1]})
        return {
            "path_kind": "LINE", "points": points,
            "label_x": round((start[0] + end[0]) / 2, 3),
            "label_y": round((start[1] + end[1]) / 2 - 10, 3),
        }
    midpoint_x = (start[0] + end[0]) / 2
    points = (
        {"x": start[0], "y": start[1]},
        {"x": midpoint_x, "y": start[1]},
        {"x": midpoint_x, "y": end[1]},
        {"x": end[0], "y": end[1]},
    )
    return {
        "path_kind": "CUBIC", "points": points,
        "label_x": round(midpoint_x, 3),
        "label_y": round((start[1] + end[1]) / 2 - 8, 3),
    }


def build_navigation_fixture() -> dict[str, Any]:
    nodes = _nodes()
    node_by_id = {item["entity_id"]: item for item in nodes}
    definitions = relationship_definition_map()
    source_text = "\n".join(row[3] for row in _edge_rows())
    document_id = f"navigation-fixture-{hashlib.sha256(source_text.encode()).hexdigest()[:16]}"
    cursor = 0
    relationships = []
    routes = []
    for index, (source_id, target_id, relationship_type, statement) in enumerate(_edge_rows(), 1):
        start = source_text.index(statement, cursor)
        end = start + len(statement)
        cursor = end
        relationship_id = f"navigation-rel-{index:02d}"
        edge_key = f"navigation-edge-{index:02d}"
        definition = definitions[relationship_type]
        relationships.append({
            "source_entity_id": source_id,
            "target_entity_id": target_id,
            "relationship_type": relationship_type.value,
            "relationship_label": relationship_type.value.replace("_", " "),
            "meaning": definition.meaning,
            "direction": definition.direction,
            "relationship_ids": [relationship_id],
            "evidence": [{
                "relationship_id": relationship_id,
                "document_id": document_id,
                "start_char": start,
                "end_char": end,
                "quote": statement,
            }],
            "origins": ["SOURCE"],
            "edge_key": edge_key,
            "provenance_status": "EXPERIMENTAL_FIXTURE_EVIDENCE",
        })
        route = _route(node_by_id[source_id]["world"], node_by_id[target_id]["world"])
        routes.append({"edge_key": edge_key, **route})

    adjacency: dict[str, list[str]] = {item["entity_id"]: [] for item in nodes}
    for edge in relationships:
        adjacency[edge["source_entity_id"]].append(edge["target_entity_id"])
        adjacency[edge["target_entity_id"]].append(edge["source_entity_id"])
    for values in adjacency.values():
        values.sort()
    initial_camera = CameraState(**INITIAL_CAMERA)
    initial_visible = [
        item["entity_id"] for item in nodes
        if point_visible(initial_camera, (item["world"]["x"], item["world"]["y"]), margin=NODE_HALF_WIDTH)
    ]
    frontier_ids = []
    for node_id in initial_visible:
        point = node_by_id[node_id]["world"]
        if any(
            not point_visible(
                initial_camera,
                (node_by_id[neighbor]["world"]["x"], node_by_id[neighbor]["world"]["y"]),
                margin=NODE_HALF_WIDTH,
            )
            for neighbor in adjacency[node_id]
        ):
            frontier_ids.append(node_id)
    initial_edges = [
        edge["edge_key"] for edge in relationships
        if edge["source_entity_id"] in initial_visible and edge["target_entity_id"] in initial_visible
    ]
    focus_targets = {}
    for node_id in frontier_ids:
        node = node_by_id[node_id]["world"]
        neighbors = [node_by_id[item]["world"] for item in adjacency[node_id]]
        target = focus_camera_target(
            initial_camera,
            (node["x"], node["y"]),
            ((item["x"], item["y"]) for item in neighbors),
        )
        focus_targets[node_id] = asdict(target)

    fixture = {
        "fixture_version": CONTINUOUS_NAVIGATION_VERSION,
        "fixture_status": "EXPERIMENTAL_PRESENTATION_NAVIGATION_FIXTURE_NOT_EXTRACTED_SOURCE",
        "title": "Order-processing service — continuous navigation",
        "domain": "software_architecture",
        "document": {
            "id": document_id,
            "source_type": "TEXT",
            "text": source_text,
            "metadata": {
                "authorship": "deterministic SPEC-018 navigation fixture",
                "purpose": "navigation mechanics only",
                "semantic_benchmark": False,
            },
        },
        "nodes": nodes,
        "edges": relationships,
        "world": {
            "bounds": WORLD_BOUNDS,
            "layout_strategy": "AUTHORED_DETERMINISTIC_LAYERED_SOFTWARE_ARCHITECTURE_FIXTURE",
            "node_positions_stable": True,
            "layout_recomputed_on_selection": False,
            "routes": routes,
        },
        "camera": {
            "initial": INITIAL_CAMERA,
            "viewport": VIEWPORT,
            "transform": "SVG_VIEWBOX_WORLD_TO_VIEWPORT",
            "focus_zone": {
                "horizontal_margin_ratio": COMFORT_MARGIN_X,
                "vertical_margin_ratio": COMFORT_MARGIN_Y,
            },
            "focus_animation_ms": 280,
            "reduced_motion_animation_ms": 0,
        },
        "navigation": {
            "frontier_strategy": "FULL_PRECOMPUTED_WORLD_VIEWPORT_CLIPPING",
            "frontier_definition": "visible node with at least one adjacent node outside current viewport",
            "initial_visible_node_ids": initial_visible,
            "initial_visible_edge_keys": initial_edges,
            "initial_frontier_node_ids": frontier_ids,
            "initial_frontier_focus_targets": focus_targets,
            "adjacency": adjacency,
            "node_dragging": False,
            "canvas_drag_panning": True,
            "history": "camera and focused-node snapshots",
        },
    }
    validate_navigation_fixture(fixture)
    return fixture


def validate_navigation_fixture(fixture: dict[str, Any]) -> None:
    nodes = fixture["nodes"]
    edges = fixture["edges"]
    if not 18 <= len(nodes) <= 30:
        raise ValidationError("navigation fixture must contain approximately 18–30 nodes")
    ids = {item["entity_id"] for item in nodes}
    if len(ids) != len(nodes):
        raise ValidationError("navigation fixture node IDs must be unique")
    if any(edge["source_entity_id"] not in ids or edge["target_entity_id"] not in ids for edge in edges):
        raise ValidationError("navigation fixture edge references an unknown node")
    if any(edge["relationship_type"] not in {item.value for item in RelationshipType} for edge in edges):
        raise ValidationError("navigation fixture uses a predicate outside the canonical vocabulary")
    document = fixture["document"]
    for edge in edges:
        for evidence in edge["evidence"]:
            if evidence["document_id"] != document["id"]:
                raise ValidationError("fixture evidence references the wrong document")
            if document["text"][evidence["start_char"]:evidence["end_char"]] != evidence["quote"]:
                raise ValidationError("fixture evidence does not match the authored source text")
    if fixture["world"]["layout_recomputed_on_selection"]:
        raise ValidationError("world layout must remain stable during navigation")
    if fixture["navigation"]["node_dragging"]:
        raise ValidationError("SPEC-018 must not drag individual nodes")


def canonical_navigation_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
