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
from .semantic_gate import (
    CandidateLabel,
    GateDecision,
    GatePacket,
    GateResult,
    GateVerdict,
    SemanticCandidate,
    aggregate_gate_metrics,
    apply_gate_decisions,
)
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
    "CandidateLabel",
    "AssertionCompilationResult",
    "AssertionExtractionProposal",
    "CanonicalizationProposal",
    "GroundedAssertionSet",
    "SourceAssertion",
    "Entity",
    "EntityType",
    "GateDecision",
    "GatePacket",
    "GateResult",
    "GateVerdict",
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
    "SemanticCandidate",
    "RelationshipType",
    "SourceDocument",
    "SourceSpan",
    "SourceType",
    "ValidationError",
    "compile_knowledge_model",
    "aggregate_gate_metrics",
    "apply_gate_decisions",
    "compile_assertion_semantics",
    "compile_staged_knowledge_model",
    "ground_assertions",
]
