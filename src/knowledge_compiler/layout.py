"""Small deterministic, structure-aware layouts for representation models."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from math import cos, hypot, pi, sin

from .representations import (
    LayoutEdge,
    LayoutNode,
    LayoutPoint,
    Representation,
    RepresentationLayout,
    RepresentationModel,
)
from .structures import StructureType


NODE_WIDTH = 168
NODE_HEIGHT = 60
_HALF_WIDTH = NODE_WIDTH // 2
_HALF_HEIGHT = NODE_HEIGHT // 2

_STRATEGIES = {
    StructureType.HIERARCHY: ("layered_hierarchy", "TOP_DOWN"),
    StructureType.CAUSAL_PATH: ("layered_causal", "LEFT_TO_RIGHT"),
    StructureType.DEPENDENCY_CHAIN: ("layered_dependency", "LEFT_TO_RIGHT"),
    StructureType.PROCESS_CHAIN: ("chronological_axis", "LEFT_TO_RIGHT"),
    StructureType.FEEDBACK_CANDIDATE: ("explicit_feedback_loop", "LOOP"),
}


def _layer_assignment(representation: Representation, *, reverse: bool) -> dict[str, int]:
    node_ids = sorted(node.entity_id for node in representation.nodes)
    pairs = [
        (edge.target_entity_id, edge.source_entity_id) if reverse
        else (edge.source_entity_id, edge.target_entity_id)
        for edge in representation.edges
    ]
    outgoing: dict[str, list[str]] = defaultdict(list)
    indegree = dict.fromkeys(node_ids, 0)
    for source, target in pairs:
        outgoing[source].append(target)
        indegree[target] += 1
    ready = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
    layers = dict.fromkeys(node_ids, 0)
    visited: list[str] = []
    while ready:
        source = ready.pop(0)
        visited.append(source)
        for target in sorted(outgoing[source]):
            layers[target] = max(layers[target], layers[source] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort()
    if len(visited) != len(node_ids):
        # Non-feedback representations are expected to be acyclic. This stable
        # fallback keeps layout total and deterministic if an upstream cycle leaks through.
        for index, node_id in enumerate(sorted(set(node_ids) - set(visited)), start=1):
            layers[node_id] = max(layers.values(), default=0) + index
    return layers


def _ordered_layers(
    representation: Representation, layers: dict[str, int], *, reverse: bool
) -> dict[int, list[str]]:
    groups: dict[int, list[str]] = defaultdict(list)
    for node_id, layer in layers.items():
        groups[layer].append(node_id)
    for values in groups.values():
        values.sort()

    oriented = [
        (edge.target_entity_id, edge.source_entity_id) if reverse
        else (edge.source_entity_id, edge.target_entity_id)
        for edge in representation.edges
    ]
    predecessors: dict[str, list[str]] = defaultdict(list)
    successors: dict[str, list[str]] = defaultdict(list)
    for source, target in oriented:
        predecessors[target].append(source)
        successors[source].append(target)

    layer_numbers = sorted(groups)
    for _ in range(3):
        positions = {node_id: index for values in groups.values() for index, node_id in enumerate(values)}
        for layer in layer_numbers[1:]:
            groups[layer].sort(key=lambda node_id: (
                sum(positions[item] for item in predecessors[node_id]) / len(predecessors[node_id])
                if predecessors[node_id] else positions[node_id],
                node_id,
            ))
        positions = {node_id: index for values in groups.values() for index, node_id in enumerate(values)}
        for layer in reversed(layer_numbers[:-1]):
            groups[layer].sort(key=lambda node_id: (
                sum(positions[item] for item in successors[node_id]) / len(successors[node_id])
                if successors[node_id] else positions[node_id],
                node_id,
            ))
    return dict(groups)


def _layered_positions(
    representation: Representation, *, top_down: bool
) -> tuple[tuple[LayoutNode, ...], int, int]:
    layers = _layer_assignment(representation, reverse=top_down)
    groups = _ordered_layers(representation, layers, reverse=top_down)
    max_layer = max(groups, default=0)
    max_rows = max((len(values) for values in groups.values()), default=1)
    if top_down:
        width = max(560, 220 + max(0, max_rows - 1) * 190)
        height = max(320, 160 + max_layer * 170)
        positions = []
        for layer in sorted(groups):
            values = groups[layer]
            total_width = max(0, len(values) - 1) * 190
            start_x = (width - total_width) // 2
            for order, node_id in enumerate(values):
                positions.append(LayoutNode(node_id, start_x + order * 190, 80 + layer * 170, layer, order))
    else:
        width = max(450, 220 + max_layer * 230)
        height = max(360, 160 + max(0, max_rows - 1) * 120)
        positions = []
        for layer in sorted(groups):
            values = groups[layer]
            total_height = max(0, len(values) - 1) * 120
            start_y = (height - total_height) // 2
            for order, node_id in enumerate(values):
                positions.append(LayoutNode(node_id, 110 + layer * 230, start_y + order * 120, layer, order))
    return tuple(sorted(positions, key=lambda item: item.entity_id)), width, height


def _feedback_positions(representation: Representation) -> tuple[tuple[LayoutNode, ...], int, int]:
    node_ids = sorted(node.entity_id for node in representation.nodes)
    width, height = 620, 380
    if len(node_ids) == 2:
        return (
            LayoutNode(node_ids[0], 170, 190, 0, 0),
            LayoutNode(node_ids[1], 450, 190, 0, 1),
        ), width, height
    radius = min(width, height) // 3
    nodes = []
    for order, node_id in enumerate(node_ids):
        angle = -pi / 2 + order * 2 * pi / len(node_ids)
        nodes.append(LayoutNode(
            node_id,
            round(width / 2 + radius * cos(angle)),
            round(height / 2 + radius * sin(angle)),
            0,
            order,
        ))
    return tuple(nodes), width, height


def _cubic_label(points: tuple[LayoutPoint, ...]) -> tuple[int, int]:
    return (
        round((points[0].x + 3 * points[1].x + 3 * points[2].x + points[3].x) / 8),
        round((points[0].y + 3 * points[1].y + 3 * points[2].y + points[3].y) / 8),
    )


def _quadratic_label(points: tuple[LayoutPoint, ...]) -> tuple[int, int]:
    return (
        round((points[0].x + 2 * points[1].x + points[2].x) / 4),
        round((points[0].y + 2 * points[1].y + points[2].y) / 4),
    )


def _layered_routes(
    representation: Representation, positions: dict[str, LayoutNode], *, top_down: bool
) -> tuple[LayoutEdge, ...]:
    routes = []
    for edge in representation.edges:
        source = positions[edge.source_entity_id]
        target = positions[edge.target_entity_id]
        if top_down:
            direction = -1 if target.y < source.y else 1
            start = LayoutPoint(source.x, source.y + direction * _HALF_HEIGHT)
            end = LayoutPoint(target.x, target.y - direction * _HALF_HEIGHT)
            middle = (start.y + end.y) // 2
            points = (start, LayoutPoint(start.x, middle), LayoutPoint(end.x, middle), end)
        else:
            direction = 1 if target.x > source.x else -1
            start = LayoutPoint(source.x + direction * _HALF_WIDTH, source.y)
            end = LayoutPoint(target.x - direction * _HALF_WIDTH, target.y)
            middle = (start.x + end.x) // 2
            points = (start, LayoutPoint(middle, start.y), LayoutPoint(middle, end.y), end)
        label_x, label_y = _cubic_label(points)
        routes.append(LayoutEdge(edge.edge_key, "CUBIC", points, label_x, label_y - 9))
    return tuple(sorted(routes, key=lambda item: item.edge_key))


def _feedback_routes(
    representation: Representation, positions: dict[str, LayoutNode], width: int, height: int
) -> tuple[LayoutEdge, ...]:
    routes = []
    if len(positions) == 2:
        ordered_edges = sorted(representation.edges, key=lambda edge: edge.edge_key)
        for index, edge in enumerate(ordered_edges):
            source = positions[edge.source_entity_id]
            target = positions[edge.target_entity_id]
            direction = 1 if target.x > source.x else -1
            start = LayoutPoint(source.x + direction * _HALF_WIDTH, source.y)
            end = LayoutPoint(target.x - direction * _HALF_WIDTH, target.y)
            control = LayoutPoint((source.x + target.x) // 2, 55 if index == 0 else height - 55)
            points = (start, control, end)
            label_x, label_y = _quadratic_label(points)
            routes.append(LayoutEdge(
                edge.edge_key, "QUADRATIC", points, label_x,
                label_y - 10 if index == 0 else label_y + 16,
            ))
        return tuple(routes)

    center_x, center_y = width // 2, height // 2
    for edge in representation.edges:
        source = positions[edge.source_entity_id]
        target = positions[edge.target_entity_id]
        dx, dy = target.x - source.x, target.y - source.y
        distance = max(1.0, hypot(dx, dy))
        start = LayoutPoint(
            round(source.x + dx / distance * _HALF_WIDTH),
            round(source.y + dy / distance * _HALF_HEIGHT),
        )
        end = LayoutPoint(
            round(target.x - dx / distance * _HALF_WIDTH),
            round(target.y - dy / distance * _HALF_HEIGHT),
        )
        midpoint_x, midpoint_y = (start.x + end.x) / 2, (start.y + end.y) / 2
        outward_x, outward_y = midpoint_x - center_x, midpoint_y - center_y
        magnitude = max(1.0, hypot(outward_x, outward_y))
        control = LayoutPoint(
            round(midpoint_x + outward_x / magnitude * 42),
            round(midpoint_y + outward_y / magnitude * 42),
        )
        points = (start, control, end)
        label_x, label_y = _quadratic_label(points)
        routes.append(LayoutEdge(edge.edge_key, "QUADRATIC", points, label_x, label_y))
    return tuple(sorted(routes, key=lambda item: item.edge_key))


def _segments_cross(a: LayoutNode, b: LayoutNode, c: LayoutNode, d: LayoutNode) -> bool:
    def orientation(p: LayoutNode, q: LayoutNode, r: LayoutNode) -> int:
        value = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
        return 0 if value == 0 else (1 if value > 0 else -1)

    return orientation(a, b, c) != orientation(a, b, d) and orientation(c, d, a) != orientation(c, d, b)


def _diagnostics(
    representation: Representation,
    nodes: tuple[LayoutNode, ...],
    routes: tuple[LayoutEdge, ...],
    orientation: str,
) -> dict[str, int | float]:
    positions = {node.entity_id: node for node in nodes}
    crossings = 0
    for index, first in enumerate(representation.edges):
        for second in representation.edges[index + 1:]:
            first_ids = {first.source_entity_id, first.target_entity_id}
            second_ids = {second.source_entity_id, second.target_entity_id}
            if first_ids.intersection(second_ids):
                continue
            if _segments_cross(
                positions[first.source_entity_id], positions[first.target_entity_id],
                positions[second.source_entity_id], positions[second.target_entity_id],
            ):
                crossings += 1
    overlaps = 0
    for index, first in enumerate(nodes):
        for second in nodes[index + 1:]:
            if abs(first.x - second.x) < NODE_WIDTH and abs(first.y - second.y) < NODE_HEIGHT:
                overlaps += 1
    length = sum(
        sum(hypot(b.x - a.x, b.y - a.y) for a, b in zip(route.points, route.points[1:]))
        for route in routes
    )
    opposing = 0
    if orientation == "LEFT_TO_RIGHT":
        opposing = sum(
            positions[edge.target_entity_id].x <= positions[edge.source_entity_id].x
            for edge in representation.edges
        )
    elif orientation == "TOP_DOWN":
        opposing = sum(
            positions[edge.target_entity_id].y <= positions[edge.source_entity_id].y
            for edge in representation.edges
        )
    return {
        "crossing_count": crossings,
        "node_overlap_count": overlaps,
        "connector_length": round(length, 2),
        "layer_count": len({node.layer for node in nodes}),
        "canonical_edges_opposing_layout_flow": opposing,
    }


def layout_representation(representation: Representation) -> RepresentationLayout:
    """Generate deterministic presentation geometry without changing semantics."""
    strategy, orientation = _STRATEGIES[representation.representation_type]
    if representation.representation_type is StructureType.FEEDBACK_CANDIDATE:
        nodes, width, height = _feedback_positions(representation)
        positions = {node.entity_id: node for node in nodes}
        routes = _feedback_routes(representation, positions, width, height)
    else:
        top_down = representation.representation_type is StructureType.HIERARCHY
        nodes, width, height = _layered_positions(representation, top_down=top_down)
        positions = {node.entity_id: node for node in nodes}
        routes = _layered_routes(representation, positions, top_down=top_down)
    return RepresentationLayout(
        strategy=strategy,
        orientation=orientation,
        width=width,
        height=height,
        nodes=nodes,
        edges=routes,
        diagnostics=_diagnostics(representation, nodes, routes, orientation),
    )


def with_layouts(model: RepresentationModel) -> RepresentationModel:
    """Add SPEC-006 layout metadata to an accepted SPEC-005 representation model."""
    representations = tuple(
        replace(representation, layout=layout_representation(representation))
        for representation in model.representations
    )
    metadata = dict(model.metadata)
    metadata["layout_version"] = "spec-006-v1"
    return replace(
        model,
        representations=representations,
        builder_version="spec-006-v1",
        metadata=metadata,
    )
