"""Fail-closed validation for binary-edge information loss covered by SPEC-010."""

from __future__ import annotations

import re

from .models import EntityType, KnowledgeModel, Origin, RelationshipType, ValidationError


_COMPARATIVE_ANTECEDENT = re.compile(r"\b(exceed|exceeds|exceeding|greater than)\b", re.IGNORECASE)


def validate_proposition_coverage(model: KnowledgeModel) -> None:
    """Reject the two observed lossy binary forms without inferring new semantics.

    Core ``KnowledgeModel`` loading remains backwards-compatible. This stricter gate is
    applied when new provider output is nominated for canonical resolution state.
    """
    entities = {item.id: item for item in model.entities}
    for relationship in model.relationships:
        comparative_operand_source = False
        if relationship.origin is Origin.SOURCE and relationship.relationship_type is RelationshipType.CAUSES:
            source = entities[relationship.source_entity_id]
            source_terms = (source.name, *source.aliases)
            comparative_operand_source = any(
                (match := _COMPARATIVE_ANTECEDENT.search(span.quote)) is not None
                and any(term.casefold() in span.quote[:match.start()].casefold() for term in source_terms)
                for span in relationship.evidence
            )
        if (
            relationship.origin is Origin.SOURCE
            and relationship.relationship_type is RelationshipType.CAUSES
            and (
                _COMPARATIVE_ANTECEDENT.search(relationship.statement)
                or comparative_operand_source
            )
        ):
            raise ValidationError(
                "comparative causal antecedent must be a COMPARISON_CONDITION proposition, "
                "not a binary relationship from one operand"
            )
        if relationship.relationship_type is RelationshipType.TRANSFERS_TO:
            destination = entities[relationship.target_entity_id]
            if destination.entity_type is EntityType.PROCESS:
                raise ValidationError(
                    "transfer destination must be an explicit domain endpoint, not a PROCESS"
                )
