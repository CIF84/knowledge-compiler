"""Typed, deterministic presentation models downstream of detected structures."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .models import EntityType, KnowledgeModel, Origin, RelationshipType, ValidationError
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .structures import DetectedStructureSet, StructureType


class Salience(StrEnum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    SPARSE = "SPARSE"


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
            for edge, raw_edge in zip(representation.edges, raw_representation["edges"]):
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
