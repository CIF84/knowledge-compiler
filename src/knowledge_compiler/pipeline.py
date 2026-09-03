"""End-to-end compilation from plain text to validated semantic IR."""

from __future__ import annotations

from typing import Any, Mapping

from .deduplicate import deduplicate_entities
from .extractor import KnowledgeExtractor
from .models import KnowledgeModel
from .normalize import normalize_document


def compile_knowledge_model(
    text: str,
    extractor: KnowledgeExtractor,
    *,
    source_metadata: Mapping[str, Any] | None = None,
) -> KnowledgeModel:
    document = normalize_document(text, metadata=source_metadata)
    extraction = deduplicate_entities(extractor.extract(document))
    return KnowledgeModel(
        document=document,
        entities=extraction.entities,
        claims=extraction.claims,
        relationships=extraction.relationships,
        metadata=extraction.metadata,
    )
