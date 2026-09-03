"""Typed, deterministic presentation models downstream of detected structures."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import Any, Mapping

from .models import EntityType, KnowledgeModel, Origin, RelationshipType, ValidationError
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .structures import DetectedStructureSet, StructureType


class Salience(StrEnum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    SPARSE = "SPARSE"


def edge_key(
    source_entity_id: str,
    relationship_type: RelationshipType | str,
    target_entity_id: str,
    relationship_ids: tuple[str, ...],
) -> str:
    """Return the stable viewer identity for one rendered semantic edge."""
    relationship_value = RelationshipType(relationship_type).value
    signature = "|".join(
        (source_entity_id, relationship_value, target_entity_id, *sorted(relationship_ids))
    )
    return f"edge-{sha256(signature.encode()).hexdigest()[:16]}"


@dataclass(frozen=True, slots=True)
class LayoutNode:
    entity_id: str
    x: int
    y: int
    layer: int
    order: int

    def __post_init__(self) -> None:
        if not isinstance(self.entity_id, str) or not self.entity_id.strip():
            raise ValidationError("layout node entity_id must be non-empty")
        for name in ("x", "y", "layer", "order"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValidationError(f"layout node {name} must be a non-negative integer")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> LayoutNode:
        return cls(
            entity_id=value.get("entity_id"),
            x=value.get("x"),
            y=value.get("y"),
            layer=value.get("layer"),
            order=value.get("order"),
        )


@dataclass(frozen=True, slots=True)
class LayoutPoint:
    x: int
    y: int

    def __post_init__(self) -> None:
        for name in ("x", "y"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValidationError(f"layout point {name} must be an integer")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> LayoutPoint:
        return cls(x=value.get("x"), y=value.get("y"))


@dataclass(frozen=True, slots=True)
class LayoutEdge:
    edge_key: str
    path_kind: str
    points: tuple[LayoutPoint, ...]
    label_x: int
    label_y: int

    def __post_init__(self) -> None:
        if not isinstance(self.edge_key, str) or not self.edge_key.strip():
            raise ValidationError("layout edge edge_key must be non-empty")
        if self.path_kind not in {"LINE", "QUADRATIC", "CUBIC"}:
            raise ValidationError("layout edge path_kind is invalid")
        points = tuple(self.points)
        expected = {"LINE": 2, "QUADRATIC": 3, "CUBIC": 4}[self.path_kind]
        if len(points) != expected:
            raise ValidationError(f"{self.path_kind} layout edge requires {expected} points")
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (self.label_x, self.label_y)
        ):
            raise ValidationError("layout edge label coordinates must be integers")
        object.__setattr__(self, "points", points)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> LayoutEdge:
        return cls(
            edge_key=value.get("edge_key"),
            path_kind=value.get("path_kind"),
            points=tuple(LayoutPoint.from_dict(item) for item in value.get("points", ())),
            label_x=value.get("label_x"),
            label_y=value.get("label_y"),
        )


@dataclass(frozen=True, slots=True)
class RepresentationLayout:
    strategy: str
    orientation: str
    width: int
    height: int
    nodes: tuple[LayoutNode, ...]
    edges: tuple[LayoutEdge, ...]
    diagnostics: Mapping[str, int | float]

    def __post_init__(self) -> None:
        if not isinstance(self.strategy, str) or not self.strategy.strip():
            raise ValidationError("layout strategy must be non-empty")
        if self.orientation not in {"LEFT_TO_RIGHT", "TOP_DOWN", "LOOP"}:
            raise ValidationError("layout orientation is invalid")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for value in (self.width, self.height)
        ):
            raise ValidationError("layout dimensions must be positive integers")
        nodes = tuple(self.nodes)
        edges = tuple(self.edges)
        if len({item.entity_id for item in nodes}) != len(nodes):
            raise ValidationError("layout node IDs must be unique")
        if len({item.edge_key for item in edges}) != len(edges):
            raise ValidationError("layout edge keys must be unique")
        if not isinstance(self.diagnostics, Mapping):
            raise ValidationError("layout diagnostics must be an object")
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", edges)
        object.__setattr__(self, "diagnostics", dict(self.diagnostics))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> RepresentationLayout:
        return cls(
            strategy=value.get("strategy"),
            orientation=value.get("orientation"),
            width=value.get("width"),
            height=value.get("height"),
            nodes=tuple(LayoutNode.from_dict(item) for item in value.get("nodes", ())),
            edges=tuple(LayoutEdge.from_dict(item) for item in value.get("edges", ())),
            diagnostics=value.get("diagnostics", {}),
        )


@dataclass(frozen=True, slots=True)
class RepresentationNode:
    entity_id: str
    label: str
    description: str
    entity_type: EntityType

    def __post_init__(self) -> None:
        for name in ("entity_id", "label"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValidationError(f"representation node {name} must be non-empty")
        if not isinstance(self.description, str):
            raise ValidationError("representation node description must be a string")
        try:
            object.__setattr__(self, "entity_type", EntityType(self.entity_type))
        except (TypeError, ValueError) as exc:
            raise ValidationError("representation node entity_type is invalid") from exc

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> RepresentationNode:
        return cls(
            entity_id=value.get("entity_id"), label=value.get("label"),
            description=value.get("description", ""), entity_type=value.get("entity_type"),
        )


@dataclass(frozen=True, slots=True)
class RepresentationEvidence:
    relationship_id: str
    document_id: str
    start_char: int
    end_char: int
    quote: str

    def __post_init__(self) -> None:
        for name in ("relationship_id", "document_id", "quote"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValidationError(f"representation evidence {name} must be non-empty")
        if (
            isinstance(self.start_char, bool) or not isinstance(self.start_char, int)
            or isinstance(self.end_char, bool) or not isinstance(self.end_char, int)
            or self.start_char < 0 or self.end_char <= self.start_char
        ):
            raise ValidationError("representation evidence coordinates are invalid")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> RepresentationEvidence:
        return cls(
            relationship_id=value.get("relationship_id"), document_id=value.get("document_id"),
            start_char=value.get("start_char"), end_char=value.get("end_char"), quote=value.get("quote"),
        )


@dataclass(frozen=True, slots=True)
class RepresentationEdge:
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    relationship_label: str
    meaning: str
    direction: str
    relationship_ids: tuple[str, ...]
    evidence: tuple[RepresentationEvidence, ...]
    origins: tuple[Origin, ...]

    def __post_init__(self) -> None:
        for name in ("source_entity_id", "target_entity_id", "relationship_label", "meaning", "direction"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValidationError(f"representation edge {name} must be non-empty")
        try:
            object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
            origins = tuple(Origin(value) for value in self.origins)
        except (TypeError, ValueError) as exc:
            raise ValidationError("representation edge enum value is invalid") from exc
        relationship_ids = tuple(self.relationship_ids)
        evidence = tuple(self.evidence)
        if not relationship_ids or len(relationship_ids) != len(set(relationship_ids)):
            raise ValidationError("representation edge relationship_ids must be non-empty and unique")
        if len(origins) != len(relationship_ids):
            raise ValidationError("representation edge origins must align with relationship_ids")
        object.__setattr__(self, "relationship_ids", relationship_ids)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "origins", origins)

    @property
    def provenance_status(self) -> str:
        return "SOURCE_EVIDENCE" if self.evidence else "INFERRED_NO_SOURCE_EVIDENCE"

    @property
    def edge_key(self) -> str:
        return edge_key(
            self.source_entity_id,
            self.relationship_type,
            self.target_entity_id,
            self.relationship_ids,
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> RepresentationEdge:
        return cls(
            source_entity_id=value.get("source_entity_id"),
            target_entity_id=value.get("target_entity_id"),
            relationship_type=value.get("relationship_type"),
            relationship_label=value.get("relationship_label"),
            meaning=value.get("meaning"), direction=value.get("direction"),
            relationship_ids=tuple(value.get("relationship_ids", ())),
            evidence=tuple(RepresentationEvidence.from_dict(item) for item in value.get("evidence", ())),
            origins=tuple(value.get("origins", ())),
        )


@dataclass(frozen=True, slots=True)
class Representation:
    id: str
    representation_type: StructureType
    source_structure_ids: tuple[str, ...]
    title: str
    nodes: tuple[RepresentationNode, ...]
    edges: tuple[RepresentationEdge, ...]
    salience: Salience
    warnings: tuple[str, ...] = ()
    layout: RepresentationLayout | None = None

    def __post_init__(self) -> None:
        for name in ("id", "title"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValidationError(f"representation {name} must be non-empty")
        try:
            object.__setattr__(self, "representation_type", StructureType(self.representation_type))
            object.__setattr__(self, "salience", Salience(self.salience))
        except (TypeError, ValueError) as exc:
            raise ValidationError("representation enum value is invalid") from exc
        source_ids = tuple(self.source_structure_ids)
        nodes = tuple(self.nodes)
        edges = tuple(self.edges)
        warnings = tuple(self.warnings)
        if not source_ids or len(source_ids) != len(set(source_ids)):
            raise ValidationError("representation source_structure_ids must be non-empty and unique")
        if not nodes or not edges:
            raise ValidationError("representation must contain nodes and edges")
        node_ids = [node.entity_id for node in nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValidationError("representation node IDs must be unique")
        if any(edge.source_entity_id not in node_ids or edge.target_entity_id not in node_ids for edge in edges):
            raise ValidationError("representation edge references an unknown displayed node")
        if any(not isinstance(warning, str) or not warning.strip() for warning in warnings):
            raise ValidationError("representation warnings must be non-empty strings")
        if self.layout is not None:
            if {item.entity_id for item in self.layout.nodes} != set(node_ids):
                raise ValidationError("layout nodes must match displayed representation nodes")
            if {item.edge_key for item in self.layout.edges} != {edge.edge_key for edge in edges}:
                raise ValidationError("layout edges must match displayed representation edges")
        object.__setattr__(self, "source_structure_ids", source_ids)
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(self, "edges", edges)
        object.__setattr__(self, "warnings", warnings)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> Representation:
        return cls(
            id=value.get("id"), representation_type=value.get("representation_type"),
            source_structure_ids=tuple(value.get("source_structure_ids", ())), title=value.get("title"),
            nodes=tuple(RepresentationNode.from_dict(item) for item in value.get("nodes", ())),
            edges=tuple(RepresentationEdge.from_dict(item) for item in value.get("edges", ())),
            salience=value.get("salience"), warnings=tuple(value.get("warnings", ())),
            layout=(RepresentationLayout.from_dict(value["layout"]) if value.get("layout") else None),
        )


@dataclass(frozen=True, slots=True)
class RepresentationModel:
    document_id: str
    title: str
    domain: str
    representations: tuple[Representation, ...]
    empty_state: str | None = None
    builder_version: str = "spec-005-v1"
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("document_id", "title", "domain", "builder_version"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValidationError(f"representation model {name} must be non-empty")
        representations = tuple(self.representations)
        ids = [item.id for item in representations]
        if len(ids) != len(set(ids)):
            raise ValidationError("representation IDs must be unique")
        if representations and self.empty_state is not None:
            raise ValidationError("non-empty representation model cannot have an empty state")
        if not representations and (not isinstance(self.empty_state, str) or not self.empty_state.strip()):
            raise ValidationError("empty representation model requires an explanatory empty state")
        warnings = tuple(self.warnings)
        if any(not isinstance(warning, str) or not warning.strip() for warning in warnings):
            raise ValidationError("representation model warnings must be non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise ValidationError("representation model metadata must be an object")
        object.__setattr__(self, "representations", representations)
        object.__setattr__(self, "warnings", warnings)
        object.__setattr__(self, "metadata", dict(self.metadata))

    def validate_against(self, model: KnowledgeModel, structures: DetectedStructureSet) -> None:
        if self.document_id != model.document.id or self.document_id != structures.source_document_id:
            raise ValidationError("representation inputs reference different documents")
        structure_ids = {item.id for item in structures.structures}
        entities = {item.id: item for item in model.entities}
        relationships = {item.id: item for item in model.relationships}
        for representation in self.representations:
            if set(representation.source_structure_ids) - structure_ids:
                raise ValidationError("representation references an unknown detected structure")
            for node in representation.nodes:
                entity = entities.get(node.entity_id)
                if entity is None or (node.label, node.description, node.entity_type) != (
                    entity.name, entity.description, entity.entity_type
                ):
                    raise ValidationError("representation node does not match KnowledgeModel entity")
            for edge in representation.edges:
                definition = RELATIONSHIP_DEFINITION_MAP[edge.relationship_type]
                if (
                    edge.relationship_label != edge.relationship_type.value.replace("_", " ")
                    or edge.meaning != definition.meaning
                    or edge.direction != definition.direction
                ):
                    raise ValidationError("representation edge does not preserve canonical semantics")
                for relationship_id in edge.relationship_ids:
                    relationship = relationships.get(relationship_id)
                    if relationship is None or (
                        relationship.source_entity_id,
                        relationship.target_entity_id,
                        relationship.relationship_type,
                    ) != (edge.source_entity_id, edge.target_entity_id, edge.relationship_type):
                        raise ValidationError("representation edge provenance does not match KnowledgeModel")
                for excerpt in edge.evidence:
                    if excerpt.relationship_id not in edge.relationship_ids:
                        raise ValidationError("representation evidence references unrelated provenance")
                    relationship = relationships.get(excerpt.relationship_id)
                    if relationship is None or not any(
                        (span.document_id, span.start_char, span.end_char, span.quote)
                        == (excerpt.document_id, excerpt.start_char, excerpt.end_char, excerpt.quote)
                        for span in relationship.evidence
                    ):
                        raise ValidationError("representation evidence was not copied from a source span")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        for representation, raw_representation in zip(self.representations, value["representations"]):
            if representation.layout is None:
                raw_representation.pop("layout")
            for edge, raw_edge in zip(representation.edges, raw_representation["edges"]):
                if representation.layout is not None:
                    raw_edge["edge_key"] = edge.edge_key
                raw_edge["provenance_status"] = edge.provenance_status
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> RepresentationModel:
        if not isinstance(value, Mapping):
            raise ValidationError("representation model must be an object")
        return cls(
            document_id=value.get("document_id"), title=value.get("title"), domain=value.get("domain"),
            representations=tuple(Representation.from_dict(item) for item in value.get("representations", ())),
            empty_state=value.get("empty_state"), builder_version=value.get("builder_version", "spec-005-v1"),
            warnings=tuple(value.get("warnings", ())), metadata=value.get("metadata", {}),
        )
