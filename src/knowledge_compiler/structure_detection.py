"""Deterministic composition of a KnowledgeModel into higher-order structures."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

from .models import KnowledgeModel, Relationship, RelationshipType
from .relationships import RELATIONSHIP_DEFINITION_MAP, RelationshipFamily
from .structures import DetectedStructure, DetectedStructureSet, StructureType

MAX_CAUSAL_PATH_EDGES = 5


@dataclass(frozen=True, slots=True)
class _Edge:
    source: str
    type: RelationshipType
    target: str
    relationship_ids: tuple[str, ...]

    @property
    def id(self) -> str:
        return self.relationship_ids[0]

    @property
    def key(self) -> tuple[str, str, str]:
        return self.source, self.type.value, self.target


def _logical_edges(relationships: Iterable[Relationship]) -> tuple[_Edge, ...]:
    grouped: dict[tuple[str, RelationshipType, str], list[str]] = defaultdict(list)
    for relationship in relationships:
        grouped[(relationship.source_entity_id, relationship.relationship_type, relationship.target_entity_id)].append(
            relationship.id
        )
    return tuple(
        _Edge(source, relationship_type, target, tuple(sorted(ids)))
        for (source, relationship_type, target), ids in sorted(
            grouped.items(), key=lambda item: (item[0][0], item[0][1].value, item[0][2])
        )
    )


def _stable_id(structure_type: StructureType, signature: str) -> str:
    digest = sha256(f"{structure_type.value}|{signature}".encode()).hexdigest()[:16]
    return f"structure-{structure_type.value.lower().replace('_', '-')}-{digest}"


def _support_metadata(edges: tuple[_Edge, ...], **extra: object) -> dict[str, object]:
    metadata: dict[str, object] = {
        "supporting_relationship_ids_by_edge": [list(edge.relationship_ids) for edge in edges],
    }
    metadata.update(extra)
    return metadata


def _path_structure(structure_type: StructureType, edges: tuple[_Edge, ...]) -> DetectedStructure:
    entities = (edges[0].source, *(edge.target for edge in edges))
    signature = "|".join(f"{edge.source}>{edge.type.value}>{edge.target}" for edge in edges)
    return DetectedStructure(
        id=_stable_id(structure_type, signature),
        structure_type=structure_type,
        entity_ids=entities,
        relationship_ids=tuple(edge.id for edge in edges),
        relationship_types=tuple(edge.type for edge in edges),
        metadata=_support_metadata(edges, edge_count=len(edges)),
    )


def _maximal_paths(
    edges: tuple[_Edge, ...], *, minimum_edges: int, maximum_edges: int
) -> tuple[tuple[_Edge, ...], ...]:
    adjacency: dict[str, list[_Edge]] = defaultdict(list)
    indegree: Counter[str] = Counter()
    nodes: set[str] = set()
    for edge in edges:
        adjacency[edge.source].append(edge)
        indegree[edge.target] += 1
        nodes.update((edge.source, edge.target))
    for outgoing in adjacency.values():
        outgoing.sort(key=lambda edge: edge.key)

    starts = sorted(node for node in nodes if indegree[node] == 0 and adjacency[node])
    if not starts:
        starts = sorted(node for node in nodes if adjacency[node])
    paths: set[tuple[_Edge, ...]] = set()

    def walk(node: str, path: tuple[_Edge, ...], visited: frozenset[str]) -> None:
        candidates = [edge for edge in adjacency[node] if edge.target not in visited]
        if len(path) == maximum_edges or not candidates:
            if len(path) >= minimum_edges:
                paths.add(path)
            return
        extended = False
        for edge in candidates:
            extended = True
            walk(edge.target, (*path, edge), visited | {edge.target})
        if not extended and len(path) >= minimum_edges:
            paths.add(path)

    for start in starts:
        walk(start, (), frozenset({start}))
    return tuple(sorted(paths, key=lambda path: tuple(edge.key for edge in path)))


def _weak_components(edges: tuple[_Edge, ...]) -> tuple[tuple[str, ...], ...]:
    neighbors: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        neighbors[edge.source].add(edge.target)
        neighbors[edge.target].add(edge.source)
    remaining = set(neighbors)
    components: list[tuple[str, ...]] = []
    while remaining:
        pending = [min(remaining)]
        seen: set[str] = set()
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            pending.extend(sorted(neighbors[node] - seen, reverse=True))
        remaining -= seen
        components.append(tuple(sorted(seen)))
    return tuple(sorted(components))


def _contains_directed_cycle(edges: tuple[_Edge, ...]) -> bool:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        adjacency[edge.source].append(edge.target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(target) for target in sorted(adjacency[node])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in sorted(adjacency) if node not in visited)


def _hierarchies(edges: tuple[_Edge, ...]) -> list[DetectedStructure]:
    structures: list[DetectedStructure] = []
    structural_types = sorted(
        (kind for kind, definition in RELATIONSHIP_DEFINITION_MAP.items()
         if definition.family is RelationshipFamily.STRUCTURAL),
        key=lambda kind: kind.value,
    )
    for relationship_type in structural_types:
        typed_edges = tuple(edge for edge in edges if edge.type is relationship_type)
        for component in _weak_components(typed_edges):
            component_edges = tuple(
                edge for edge in typed_edges if edge.source in component and edge.target in component
            )
            targets = {edge.target for edge in component_edges}
            sources = {edge.source for edge in component_edges}
            roots = sorted(targets - sources)
            leaves = sorted(sources - targets)
            signature = f"{relationship_type.value}|" + "|".join(
                f"{edge.source}>{edge.target}" for edge in component_edges
            )
            structures.append(DetectedStructure(
                id=_stable_id(StructureType.HIERARCHY, signature),
                structure_type=StructureType.HIERARCHY,
                entity_ids=component,
                relationship_ids=tuple(edge.id for edge in component_edges),
                relationship_types=tuple(edge.type for edge in component_edges),
                metadata=_support_metadata(
                    component_edges,
                    hierarchy_relationship_type=relationship_type.value,
                    roots=roots,
                    leaves=leaves,
                    contains_cycle=_contains_directed_cycle(component_edges),
                ),
            ))
    return structures


def _canonical_cycle(edges: tuple[_Edge, ...]) -> tuple[_Edge, ...]:
    rotations = tuple(edges[index:] + edges[:index] for index in range(len(edges)))
    return min(rotations, key=lambda cycle: tuple(edge.key for edge in cycle))


def _feedback_candidates(causal_edges: tuple[_Edge, ...]) -> list[DetectedStructure]:
    adjacency: dict[str, list[_Edge]] = defaultdict(list)
    for edge in causal_edges:
        adjacency[edge.source].append(edge)
    for outgoing in adjacency.values():
        outgoing.sort(key=lambda edge: edge.key)
    cycles: dict[tuple[tuple[str, str, str], ...], tuple[_Edge, ...]] = {}

    def walk(start: str, node: str, path: tuple[_Edge, ...], visited: frozenset[str]) -> None:
        for edge in adjacency[node]:
            if edge.target == start:
                cycle = _canonical_cycle((*path, edge))
                cycles[tuple(item.key for item in cycle)] = cycle
            elif edge.target not in visited:
                walk(start, edge.target, (*path, edge), visited | {edge.target})

    for start in sorted(adjacency):
        walk(start, start, (), frozenset({start}))

    structures = []
    for signature, cycle in sorted(cycles.items()):
        entities = (cycle[0].source, *(edge.target for edge in cycle))
        structures.append(DetectedStructure(
            id=_stable_id(StructureType.FEEDBACK_CANDIDATE, repr(signature)),
            structure_type=StructureType.FEEDBACK_CANDIDATE,
            entity_ids=entities,
            relationship_ids=tuple(edge.id for edge in cycle),
            relationship_types=tuple(edge.type for edge in cycle),
            metadata=_support_metadata(cycle, edge_count=len(cycle), polarity="UNCLASSIFIED"),
        ))
    return structures


class StructureDetector:
    """Detect graph patterns without source text or provider dependencies."""

    def detect(self, model: KnowledgeModel) -> DetectedStructureSet:
        edges = _logical_edges(model.relationships)
        structures: list[DetectedStructure] = _hierarchies(edges)

        causal_edges = tuple(
            edge for edge in edges
            if RELATIONSHIP_DEFINITION_MAP[edge.type].family is RelationshipFamily.CAUSAL
        )
        structures.extend(
            _path_structure(StructureType.CAUSAL_PATH, path)
            for path in _maximal_paths(
                causal_edges, minimum_edges=2, maximum_edges=MAX_CAUSAL_PATH_EDGES
            )
        )
        structures.extend(_feedback_candidates(causal_edges))

        temporal_edges = tuple(edge for edge in edges if edge.type is RelationshipType.PRECEDES)
        structures.extend(
            _path_structure(StructureType.PROCESS_CHAIN, path)
            for path in _maximal_paths(temporal_edges, minimum_edges=1, maximum_edges=MAX_CAUSAL_PATH_EDGES)
        )

        dependency_types = sorted(
            (kind for kind, definition in RELATIONSHIP_DEFINITION_MAP.items()
             if definition.family is RelationshipFamily.DEPENDENCY),
            key=lambda kind: kind.value,
        )
        for relationship_type in dependency_types:
            typed_edges = tuple(edge for edge in edges if edge.type is relationship_type)
            structures.extend(
                _path_structure(StructureType.DEPENDENCY_CHAIN, path)
                for path in _maximal_paths(typed_edges, minimum_edges=2, maximum_edges=MAX_CAUSAL_PATH_EDGES)
            )

        structures.sort(key=lambda item: (item.structure_type.value, item.entity_ids, item.relationship_types, item.id))
        counts = Counter(structure.structure_type.value for structure in structures)
        result = DetectedStructureSet(
            source_document_id=model.document.id,
            structures=tuple(structures),
            metadata={
                "structure_counts": {kind.value: counts.get(kind.value, 0) for kind in StructureType},
                "logical_relationship_count": len(edges),
                "input_relationship_count": len(model.relationships),
                **({"input_proposition_count": len(model.propositions)} if model.propositions else {}),
                "maximum_causal_path_edges": MAX_CAUSAL_PATH_EDGES,
            },
        )
        result.validate_against(model)
        return result
