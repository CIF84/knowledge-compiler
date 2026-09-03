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

__all__ = [
    "Claim",
    "Entity",
    "EntityType",
    "KnowledgeModel",
    "Origin",
    "Relationship",
    "RelationshipDefinition",
    "RelationshipFamily",
    "RelationshipType",
    "SourceDocument",
    "SourceSpan",
    "SourceType",
    "ValidationError",
    "compile_knowledge_model",
]
