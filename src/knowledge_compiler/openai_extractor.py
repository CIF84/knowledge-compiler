"""OpenAI Responses API adapter for semantic extraction.

Provider output uses exact source quotes. Character coordinates are derived locally
and validated before the result crosses into the provider-neutral pipeline.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

from .extractor import ExtractionResult
from .models import EntityType, Origin, RelationshipType, SourceDocument, ValidationError
from .relationships import render_relationship_grammar

DEFAULT_MODEL = "gpt-5.6-luna"
PROMPT_VERSION = "spec-003-v1"
PROVIDER = "openai"


class ExtractionError(RuntimeError):
    """A provider request or response could not produce an extraction."""


INSTRUCTIONS_BASE = """You extract a semantic knowledge model from explanatory source text.

Identify important concepts, objects, processes, variables, systems, and components.
Create claims for meaningful propositions that do not naturally form graph edges.
Create relationships only when one supplied semantic contract fits both the meaning and
direction. Prefer important explanatory structure over exhaustive sentence decomposition.
If no relationship contract represents a meaningful proposition truthfully, preserve it
as a claim instead of forcing it into the nearest edge label. Fewer truthful edges are
better than more misleading edges. Use concise grounded descriptions and conservative
confidence values.

SOURCE means the item is explicitly supported by the supplied text. Every SOURCE item
must cite one or more exact, verbatim, uniquely occurring source substrings in evidence.
Use a complete clause or sentence long enough to occur exactly once; never cite a short
entity name or other repeated fragment. Do not count characters; return quotes only.
INFERRED means useful structure not stated explicitly and must have an empty evidence
list. Any item with evidence must be SOURCE. Before returning, verify every SOURCE item
has at least one unique quote and every INFERRED item has none. Do not use external
knowledge unless the item is marked INFERRED. Do not fabricate evidence.

Avoid entities created only to reproduce grammar. Avoid duplicates; use aliases only
for genuine naming equivalence, and keep related but distinct concepts separate.
Relationship endpoints must use IDs from the entities array. IDs must be unique,
concise, stable kebab-case strings. Do not generate summaries, visualizations, Mermaid,
teaching prose, or output outside the requested schema."""


def build_instructions() -> str:
    return f"{INSTRUCTIONS_BASE}\n\n{render_relationship_grammar()}"


def extraction_schema() -> dict[str, Any]:
    string = {"type": "string"}
    evidence = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"quote": string},
            "required": ["quote"],
            "additionalProperties": False,
        },
    }
    entity = {
        "type": "object",
        "properties": {
            "id": string,
            "name": string,
            "description": string,
            "entity_type": {"type": "string", "enum": [item.value for item in EntityType]},
            "aliases": {"type": "array", "items": string},
        },
        "required": ["id", "name", "description", "entity_type", "aliases"],
        "additionalProperties": False,
    }
    claim = {
        "type": "object",
        "properties": {
            "id": string,
            "statement": string,
            "evidence": evidence,
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "origin": {"type": "string", "enum": [item.value for item in Origin]},
        },
        "required": ["id", "statement", "evidence", "confidence", "origin"],
        "additionalProperties": False,
    }
    relationship = {
        "type": "object",
        "properties": {
            "id": string,
            "source_entity_id": string,
            "relationship_type": {"type": "string", "enum": [item.value for item in RelationshipType]},
            "target_entity_id": string,
            "statement": string,
            "evidence": evidence,
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "origin": {"type": "string", "enum": [item.value for item in Origin]},
        },
        "required": [
            "id", "source_entity_id", "relationship_type", "target_entity_id",
            "statement", "evidence", "confidence", "origin",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "entities": {"type": "array", "items": entity},
            "claims": {"type": "array", "items": claim},
            "relationships": {"type": "array", "items": relationship},
        },
        "required": ["entities", "claims", "relationships"],
        "additionalProperties": False,
    }


def resolve_evidence_quote(document: SourceDocument, quote: str) -> dict[str, Any]:
    if not isinstance(quote, str) or not quote:
        raise ValidationError("evidence quote must be a non-empty string")
    start = document.text.find(quote)
    if start < 0:
        raise ValidationError(f"evidence quote was not found in source: {quote!r}")
    if document.text.find(quote, start + 1) >= 0:
        raise ValidationError(f"evidence quote is ambiguous in source: {quote!r}")
    return {
        "document_id": document.id,
        "start_char": start,
        "end_char": start + len(quote),
        "quote": quote,
    }


def resolve_output_evidence(raw: Mapping[str, Any], document: SourceDocument) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValidationError("provider extraction output must be an object")
    resolved = dict(raw)
    for collection_name in ("claims", "relationships"):
        collection = resolved.get(collection_name, [])
        if not isinstance(collection, list):
            raise ValidationError(f"provider output {collection_name} must be an array")
        converted = []
        for index, item in enumerate(collection):
            if not isinstance(item, Mapping):
                raise ValidationError(f"provider output {collection_name}[{index}] must be an object")
            converted_item = dict(item)
            evidence = converted_item.get("evidence", [])
            if not isinstance(evidence, list):
                raise ValidationError(f"provider output {collection_name}[{index}].evidence must be an array")
            converted_item["evidence"] = [
                resolve_evidence_quote(document, evidence_item.get("quote"))
                if isinstance(evidence_item, Mapping)
                else resolve_evidence_quote(document, evidence_item)
                for evidence_item in evidence
            ]
            converted.append(converted_item)
        resolved[collection_name] = converted
    return resolved


def _usage_metadata(usage: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for source_name, target_name in (
        ("input_tokens", "input_tokens"),
        ("output_tokens", "output_tokens"),
        ("total_tokens", "total_tokens"),
    ):
        value = getattr(usage, source_name, None)
        if isinstance(value, int):
            result[target_name] = value
    return result


class OpenAILLMExtractor:
    """Real structured-output extractor backed by one OpenAI model."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self._client = client

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ExtractionError("OPENAI_API_KEY is required for --extractor llm")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ExtractionError("OpenAI support is not installed; install knowledge-compiler[llm]") from exc
        self._client = OpenAI(api_key=api_key)
        return self._client

    def extract(self, document: SourceDocument) -> ExtractionResult:
        try:
            response = self._client_or_create().responses.create(
                model=self.model,
                instructions=build_instructions(),
                input=document.text,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "knowledge_extraction",
                        "strict": True,
                        "schema": extraction_schema(),
                    }
                },
                reasoning={"effort": "low"},
                store=False,
            )
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError(f"OpenAI extraction request failed: {exc}") from exc

        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text:
            raise ExtractionError("OpenAI response did not contain structured output text")
        try:
            raw = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ExtractionError(f"OpenAI structured output was not valid JSON: {exc}") from exc

        resolved = resolve_output_evidence(raw, document)
        actual_model = getattr(response, "model", None) or self.model
        metadata: dict[str, Any] = {
            "extractor": "llm",
            "provider": PROVIDER,
            "model": actual_model,
            "prompt_version": PROMPT_VERSION,
        }
        request_id = getattr(response, "id", None)
        if request_id:
            metadata["provider_request_id"] = request_id
        usage = _usage_metadata(getattr(response, "usage", None))
        if usage:
            metadata["usage"] = usage
        resolved["metadata"] = metadata
        return ExtractionResult.from_dict(resolved, document)
