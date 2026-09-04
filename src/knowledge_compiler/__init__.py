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
from .assertion_compilation import (
    AssertionCompilationResult,
    AssertionExtractionProposal,
    CanonicalizationProposal,
    GroundedAssertionSet,
    SourceAssertion,
    compile_assertion_semantics,
    ground_assertions,
)
from .pipeline import compile_knowledge_model
from .relationships import RelationshipDefinition, RelationshipFamily
from .structure_detection import StructureDetector
from .staged_compilation import (
    SemanticLinkingResult,
    StagedCompilationResult,
    StagedSemanticExtractor,
    SymbolDiscoveryProposal,
    SymbolNomination,
    SymbolTable,
    compile_staged_knowledge_model,
)
from .structures import DetectedStructure, DetectedStructureSet, StructureType
from .representation_builder import RepresentationBuilder
from .representations import Representation, RepresentationEdge, RepresentationModel, RepresentationNode, Salience

__all__ = [
    "Claim",
    "AssertionCompilationResult",
    "AssertionExtractionProposal",
    "CanonicalizationProposal",
    "GroundedAssertionSet",
    "SourceAssertion",
    "Entity",
    "EntityType",
    "KnowledgeModel",
    "Origin",
    "Relationship",
    "RelationshipDefinition",
    "RelationshipFamily",
    "StructureDetector",
    "SemanticLinkingResult",
    "StagedCompilationResult",
    "StagedSemanticExtractor",
    "SymbolDiscoveryProposal",
    "SymbolNomination",
    "SymbolTable",
    "DetectedStructure",
    "DetectedStructureSet",
    "StructureType",
    "RepresentationBuilder",
    "Representation",
    "RepresentationEdge",
    "RepresentationModel",
    "RepresentationNode",
    "Salience",
    "RelationshipType",
    "SourceDocument",
    "SourceSpan",
    "SourceType",
    "ValidationError",
    "compile_knowledge_model",
    "compile_assertion_semantics",
    "compile_staged_knowledge_model",
    "ground_assertions",
]
