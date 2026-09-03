"""Provider-neutral output types for deterministic graph structure detection."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .models import KnowledgeModel, RelationshipType, ValidationError


class StructureType(StrEnum):
    HIERARCHY = "HIERARCHY"
    CAUSAL_PATH = "CAUSAL_PATH"
    PROCESS_CHAIN = "PROCESS_CHAIN"
    DEPENDENCY_CHAIN = "DEPENDENCY_CHAIN"
    FEEDBACK_CANDIDATE = "FEEDBACK_CANDIDATE"


def _nonempty_strings(values: Any, path: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)) or any(
        not isinstance(value, str) or not value.strip() for value in values
    ):
        raise ValidationError(f"{path} must contain non-empty strings")
    return tuple(values)


@dataclass(frozen=True, slots=True)
class DetectedStructure:
    id: str
    structure_type: StructureType
    entity_ids: tuple[str, ...]
    relationship_ids: tuple[str, ...]
    relationship_types: tuple[RelationshipType, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("structure.id must be a non-empty string")
        try:
            structure_type = StructureType(self.structure_type)
        except (TypeError, ValueError) as exc:
            raise ValidationError("structure.structure_type is invalid") from exc
        object.__setattr__(self, "structure_type", structure_type)
        entity_ids = _nonempty_strings(self.entity_ids, "structure.entity_ids")
        relationship_ids = _nonempty_strings(self.relationship_ids, "structure.relationship_ids")
        try:
            relationship_types = tuple(RelationshipType(value) for value in self.relationship_types)
        except (TypeError, ValueError) as exc:
            raise ValidationError("structure.relationship_types contains an invalid type") from exc
        if len(entity_ids) < 2:
            raise ValidationError("structure.entity_ids must contain at least two entities")
        if not relationship_ids:
            raise ValidationError("structure.relationship_ids must contain at least one relationship")
        if len(relationship_ids) != len(relationship_types):
            raise ValidationError("structure relationship IDs and types must have equal length")
        if structure_type is not StructureType.HIERARCHY and len(entity_ids) != len(relationship_ids) + 1:
            raise ValidationError("path and cycle structures require one more entity than relationship")
        if structure_type is StructureType.FEEDBACK_CANDIDATE and entity_ids[0] != entity_ids[-1]:
            raise ValidationError("feedback candidates must return to their starting entity")
        if not isinstance(self.metadata, Mapping):
            raise ValidationError("structure.metadata must be an object")
        object.__setattr__(self, "entity_ids", entity_ids)
        object.__setattr__(self, "relationship_ids", relationship_ids)
        object.__setattr__(self, "relationship_types", relationship_types)
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> DetectedStructure:
        if not isinstance(value, Mapping):
            raise ValidationError("structure must be an object")
        return cls(
            id=value.get("id"),
            structure_type=value.get("structure_type"),
            entity_ids=value.get("entity_ids", ()),
            relationship_ids=value.get("relationship_ids", ()),
            relationship_types=value.get("relationship_types", ()),
            metadata=value.get("metadata", {}),
        )


@dataclass(frozen=True, slots=True)
class DetectedStructureSet:
    source_document_id: str
    structures: tuple[DetectedStructure, ...]
    detector_version: str = "spec-004-v1"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source_document_id, str) or not self.source_document_id.strip():
            raise ValidationError("structure set source_document_id must be non-empty")
        if not isinstance(self.detector_version, str) or not self.detector_version.strip():
            raise ValidationError("structure set detector_version must be non-empty")
        structures = tuple(self.structures)
        ids = [structure.id for structure in structures]
        if len(ids) != len(set(ids)):
            raise ValidationError("detected structure IDs must be unique")
        if not isinstance(self.metadata, Mapping):
            raise ValidationError("structure set metadata must be an object")
        object.__setattr__(self, "structures", structures)
        object.__setattr__(self, "metadata", dict(self.metadata))

    def validate_against(self, model: KnowledgeModel) -> None:
        if self.source_document_id != model.document.id:
            raise ValidationError("structure set references a different source document")
        entity_ids = {entity.id for entity in model.entities}
        relationship_ids = {relationship.id for relationship in model.relationships}
        for structure in self.structures:
            missing_entities = set(structure.entity_ids) - entity_ids
            missing_relationships = set(structure.relationship_ids) - relationship_ids
            if missing_entities or missing_relationships:
                raise ValidationError(
                    f"structure {structure.id!r} has unknown provenance: "
                    f"entities={sorted(missing_entities)}, relationships={sorted(missing_relationships)}"
                )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> DetectedStructureSet:
        if not isinstance(value, Mapping):
            raise ValidationError("detected structure set must be an object")
        return cls(
            source_document_id=value.get("source_document_id"),
            structures=tuple(DetectedStructure.from_dict(item) for item in value.get("structures", ())),
            detector_version=value.get("detector_version", "spec-004-v1"),
            metadata=value.get("metadata", {}),
        )
