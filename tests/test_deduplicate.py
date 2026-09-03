from knowledge_compiler.deduplicate import deduplicate_entities, normalized_entity_name
from knowledge_compiler.extractor import ExtractionResult
from knowledge_compiler.models import Entity, EntityType, Origin, Relationship, RelationshipType


def test_case_duplicate_is_merged_and_relationship_rewritten() -> None:
    entities = (
        Entity("field", "electric field", "canonical", EntityType.CONCEPT),
        Entity("field-duplicate", "Electric Field", "duplicate", EntityType.CONCEPT),
        Entity("charge", "Charge", "", EntityType.CONCEPT),
    )
    edge = Relationship("r", "charge", RelationshipType.CREATES, "field-duplicate", "Charge creates a field", (), 0.8, Origin.INFERRED)
    result = deduplicate_entities(ExtractionResult(entities, (), (edge,), {}))
    assert [entity.id for entity in result.entities] == ["field", "charge"]
    assert result.relationships[0].target_entity_id == "field"


def test_alias_matches_merge_but_related_names_do_not() -> None:
    entities = (
        Entity("em", "Electromagnetic field", "", EntityType.CONCEPT),
        Entity("electric", "Electric field", "", EntityType.CONCEPT),
        Entity("current", "Current", "", EntityType.PROCESS, ("electric current",)),
        Entity("moving", "Electric current", "", EntityType.PROCESS),
    )
    result = deduplicate_entities(ExtractionResult(entities, (), (), {}))
    assert [entity.id for entity in result.entities] == ["em", "electric", "current"]
    assert normalized_entity_name("  Electric   FIELD ") == "electric field"
