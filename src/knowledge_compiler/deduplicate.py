"""Conservative entity deduplication with graph reference rewriting."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import replace

from .extractor import ExtractionResult
from .models import Entity, ValidationError


def normalized_entity_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"\s+", " ", normalized)


def deduplicate_entities(result: ExtractionResult) -> ExtractionResult:
    canonical: list[Entity] = []
    owner_by_term: dict[str, str] = {}
    canonical_by_id: dict[str, str] = {}

    for entity in result.entities:
        terms = {normalized_entity_name(entity.name), *(normalized_entity_name(alias) for alias in entity.aliases)}
        owners = {owner_by_term[term] for term in terms if term in owner_by_term}
        if len(owners) > 1:
            raise ValidationError(f"entity {entity.id!r} aliases conflict with multiple canonical entities")
        if owners:
            owner_id = next(iter(owners))
            index = next(i for i, item in enumerate(canonical) if item.id == owner_id)
            owner = canonical[index]
            merged_aliases = list(owner.aliases)
            for alias in (entity.name, *entity.aliases):
                if normalized_entity_name(alias) != normalized_entity_name(owner.name) and alias not in merged_aliases:
                    merged_aliases.append(alias)
            canonical[index] = replace(owner, aliases=tuple(merged_aliases))
            canonical_by_id[entity.id] = owner_id
            for term in terms:
                owner_by_term[term] = owner_id
        else:
            canonical.append(entity)
            canonical_by_id[entity.id] = entity.id
            for term in terms:
                owner_by_term[term] = entity.id

    relationships = tuple(
        replace(
            relationship,
            source_entity_id=canonical_by_id.get(relationship.source_entity_id, relationship.source_entity_id),
            target_entity_id=canonical_by_id.get(relationship.target_entity_id, relationship.target_entity_id),
        )
        for relationship in result.relationships
    )
    return ExtractionResult(tuple(canonical), result.claims, relationships, result.metadata)
