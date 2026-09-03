"""Typed semantic intermediate representation for Knowledge Compiler."""

from .models import (
    Claim,
    Entity,
    EntityType,
    KnowledgeModel,
    Origin,
    Relationship,
    RelationshipType,
    SourceDocument,
    SourceSpan,
    SourceType,
    ValidationError,
)
from .pipeline import compile_knowledge_model
from .relationships import RelationshipDefinition, RelationshipFamily
from .structure_detection import StructureDetector
from .structures import DetectedStructure, DetectedStructureSet, StructureType

__all__ = [
    "Claim",
    "Entity",
    "EntityType",
    "KnowledgeModel",
    "Origin",
    "Relationship",
    "RelationshipDefinition",
    "RelationshipFamily",
    "StructureDetector",
    "DetectedStructure",
    "DetectedStructureSet",
    "StructureType",
    "RelationshipType",
    "SourceDocument",
    "SourceSpan",
    "SourceType",
    "ValidationError",
    "compile_knowledge_model",
]
