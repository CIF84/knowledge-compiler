from __future__ import annotations

import json
from pathlib import Path

from knowledge_compiler.models import (
    Entity,
    EntityType,
    KnowledgeModel,
    Origin,
    Relationship,
    RelationshipType,
    SourceDocument,
)
from knowledge_compiler.relationships import (
    RELATIONSHIP_DEFINITION_MAP,
    RELATIONSHIP_DEFINITIONS,
    RelationshipFamily,
    render_relationship_grammar,
)


def test_every_active_predicate_has_exactly_one_complete_definition() -> None:
    assert set(RELATIONSHIP_DEFINITION_MAP) == set(RelationshipType)
    assert len(RELATIONSHIP_DEFINITIONS) == len(RelationshipType)
    assert len({definition.type for definition in RELATIONSHIP_DEFINITIONS}) == len(RelationshipType)
    assert {definition.family for definition in RELATIONSHIP_DEFINITIONS} == set(RelationshipFamily)
    for definition in RELATIONSHIP_DEFINITIONS:
        assert all((
            definition.meaning,
            definition.direction,
            definition.source_role,
            definition.target_role,
            definition.use_when,
            definition.avoid_when,
        ))


def test_prompt_grammar_is_generated_from_canonical_definitions() -> None:
    rendered = render_relationship_grammar()
    for definition in RELATIONSHIP_DEFINITIONS:
        assert f"{definition.type.value} [{definition.family.value};" in rendered
        assert definition.meaning in rendered
        assert definition.use_when in rendered
        assert definition.avoid_when in rendered


def test_high_risk_predicates_include_observed_misuse_guidance() -> None:
    assert "Never reverse" in RELATIONSHIP_DEFINITION_MAP[RelationshipType.PART_OF].avoid_when
    assert "literal physical force" in RELATIONSHIP_DEFINITION_MAP[RelationshipType.EXERTS_FORCE_ON].meaning
    assert "Never use metaphorically" in RELATIONSHIP_DEFINITION_MAP[RelationshipType.EXERTS_FORCE_ON].avoid_when
    assert "source itself" in RELATIONSHIP_DEFINITION_MAP[RelationshipType.TRANSFORMS_INTO].meaning
    assert "slower" in RELATIONSHIP_DEFINITION_MAP[RelationshipType.INCREASES].avoid_when


def test_new_general_predicates_round_trip_in_existing_ir() -> None:
    document = SourceDocument("doc", "text")
    entities = (
        Entity("a", "A", "", EntityType.CONCEPT),
        Entity("b", "B", "", EntityType.CONCEPT),
    )
    relationships = tuple(
        Relationship(f"r-{kind.value}", "a", kind, "b", "A relates to B", (), 0.7, Origin.INFERRED)
        for kind in (RelationshipType.AFFECTS, RelationshipType.BINDS_TO, RelationshipType.TRANSFERS_TO)
    )
    model = KnowledgeModel(document, entities, (), relationships)
    assert KnowledgeModel.from_dict(model.to_dict()) == model


def test_regression_metadata_covers_all_domains_and_known_failures() -> None:
    path = Path(__file__).parent / "fixtures" / "domains" / "relationship_regressions.json"
    regressions = json.loads(path.read_text())
    assert set(regressions) == {"electromagnetism", "software_architecture", "economics", "biology", "history"}
    corpus = "\n".join(item for values in regressions.values() for item in values)
    for expected in ("service PART_OF component", "EXERTS_FORCE_ON", "BINDS_TO", "PRECEDES", "TRANSFORMS_INTO"):
        assert expected in corpus
