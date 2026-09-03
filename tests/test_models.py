from dataclasses import replace

import pytest

from knowledge_compiler.models import (
    Entity,
    EntityType,
    KnowledgeModel,
    Origin,
    Relationship,
    RelationshipType,
    SourceDocument,
    SourceSpan,
    ValidationError,
)


def test_span_bounds_and_quote_are_validated() -> None:
    document = SourceDocument("doc", "electric field")
    SourceSpan("doc", 0, 8, "electric").validate_against(document)
    with pytest.raises(ValidationError, match="outside"):
        SourceSpan("doc", 0, 99, "electric").validate_against(document)
    with pytest.raises(ValidationError, match="mismatch"):
        SourceSpan("doc", 0, 8, "magnetic").validate_against(document)


def test_invalid_confidence_and_relationship_type_are_rejected() -> None:
    base = dict(
        id="r", source_entity_id="a", target_entity_id="b", statement="a affects b",
        evidence=(), origin=Origin.INFERRED,
    )
    with pytest.raises(ValidationError, match="between 0 and 1"):
        Relationship(**base, relationship_type=RelationshipType.CAUSES, confidence=1.1)
    with pytest.raises(ValidationError, match="must be one of"):
        Relationship(**base, relationship_type="MAGIC", confidence=0.5)


def test_relationship_endpoints_must_exist() -> None:
    document = SourceDocument("doc", "text")
    entity = Entity("a", "A", "", EntityType.CONCEPT)
    relationship = Relationship("r", "a", RelationshipType.CAUSES, "missing", "A causes B", (), 0.5, Origin.INFERRED)
    with pytest.raises(ValidationError, match="unknown entities"):
        KnowledgeModel(document, (entity,), (), (relationship,))


def test_serialization_round_trip() -> None:
    document = SourceDocument("doc", "A causes B")
    evidence = SourceSpan("doc", 0, 10, "A causes B")
    entities = (Entity("a", "A", "", EntityType.CONCEPT), Entity("b", "B", "", EntityType.CONCEPT))
    relationship = Relationship("r", "a", RelationshipType.CAUSES, "b", "A causes B", (evidence,), 0.9, Origin.SOURCE)
    model = KnowledgeModel(document, entities, (), (relationship,), {"stable": True})
    assert KnowledgeModel.from_dict(model.to_dict()) == model


def test_source_origin_requires_evidence_and_inference_cannot_claim_it() -> None:
    base = dict(id="r", source_entity_id="a", relationship_type=RelationshipType.CAUSES, target_entity_id="b", statement="x", confidence=0.5)
    with pytest.raises(ValidationError, match="require evidence"):
        Relationship(**base, evidence=(), origin=Origin.SOURCE)
    with pytest.raises(ValidationError, match="must not present"):
        Relationship(**base, evidence=(SourceSpan("doc", 0, 1, "x"),), origin=Origin.INFERRED)
