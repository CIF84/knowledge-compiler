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

__all__ = [
    "Claim",
    "Entity",
    "EntityType",
    "KnowledgeModel",
    "Origin",
    "Relationship",
    "RelationshipType",
    "SourceDocument",
    "SourceSpan",
    "SourceType",
    "ValidationError",
    "compile_knowledge_model",
]
