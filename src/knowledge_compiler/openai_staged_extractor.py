"""OpenAI adapter for SPEC-012 staged semantic compilation."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

from .models import (
    ComparisonOperator,
    EntityType,
    Origin,
    PropositionRole,
    PropositionType,
    RelationshipType,
    SourceDocument,
    ValidationError,
)
from .openai_extractor import (
    DEFAULT_MODEL,
    ExtractionError,
    _usage_metadata,
    resolve_output_evidence,
)
from .relationships import render_relationship_grammar
from .staged_compilation import (
    SemanticLinkingResult,
    SymbolDiscoveryProposal,
    SymbolTable,
)


PROVIDER = "openai"
SYMBOL_PROMPT_VERSION = "spec-012-symbols-v1"
LINKING_PROMPT_VERSION = "spec-012-linking-v1"


class StagedExtractionError(ExtractionError):
    """A staged provider request or response could not produce a proposal."""


SYMBOL_INSTRUCTIONS = """You perform Pass 1 symbol discovery for a semantic compiler.

Read only the supplied source. Nominate a precision-first inventory of semantically
meaningful things that later relationships, claims, or typed propositions may refer to.
Use only the supplied entity types. Prefer a smaller coherent inventory over every noun
phrase. Include concepts needed as exact semantic endpoints, including processes or
outcomes when the source makes them important. Do not use external knowledge.

Do not assign IDs: trusted code assigns stable canonical IDs and ordering after this pass.
Reduce obvious alias fragmentation only when two source surface forms genuinely name the
same concept. Keep related but distinct concepts separate. Descriptions must be concise
and source-bounded. Return only the requested schema."""


LINKING_INSTRUCTIONS_BASE = """You perform Pass 2 semantic linking for a semantic compiler.

The user supplies a frozen symbol table and the exact full source. Extract source-supported
relationships, claims, and the two supported typed proposition forms. Every relationship
endpoint and proposition role must use an exact ID from the frozen symbol table. You must
not create, rename, or imply additional entities.

If a meaningful semantic item needs a concept absent from the symbol table, omit that item
and add a missing_symbols diagnostic containing the source surface form, a concise semantic
item description, and the reason it cannot be represented. Never substitute a nearby but
incorrect endpoint. Fewer truthful semantic items are better than more questionable ones.

Create claims for meaningful propositions that do not naturally form graph edges. Create a
relationship only when one supplied semantic contract fits both the meaning and direction.
If no contract fits truthfully, preserve the proposition as a claim instead of forcing it
into the nearest label. Do not turn explanation, association, or historical context into
causality.

Use a typed proposition only for either of these binary-edge failure modes:
- COMPARISON_CONDITION: a comparison is itself the antecedent of an outcome. Bind
  LEFT_OPERAND, RIGHT_OPERAND, and OUTCOME; use GREATER_THAN and CAUSES.
- TRANSFER_EVENT: a transfer must distinguish EVENT, OBJECT, and DESTINATION; use
  TRANSFERS_TO.
Do not also emit a lossy binary edge for the same source proposition. Proposition IDs are
assigned deterministically by trusted code; do not return an id.

SOURCE means the item is explicitly supported by the supplied source. Every SOURCE item
must cite one or more exact, verbatim, uniquely occurring source substrings in evidence.
Use a complete clause or sentence long enough to occur exactly once; never cite a repeated
short fragment. Do not count characters; return quotes only. INFERRED items must have an
empty evidence list, and items with evidence must be SOURCE. Do not fabricate evidence or
use external semantic enrichment. Return only the requested schema."""


def build_symbol_instructions() -> str:
    return SYMBOL_INSTRUCTIONS


def build_linking_instructions() -> str:
    return f"{LINKING_INSTRUCTIONS_BASE}\n\n{render_relationship_grammar()}"


def symbol_discovery_schema() -> dict[str, Any]:
    string = {"type": "string"}
    return {
        "type": "object",
        "properties": {
            "symbols": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": string,
                        "description": string,
                        "entity_type": {
                            "type": "string",
                            "enum": [item.value for item in EntityType],
                        },
                        "aliases": {"type": "array", "items": string},
                    },
                    "required": ["name", "description", "entity_type", "aliases"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["symbols"],
        "additionalProperties": False,
    }


def semantic_linking_schema(symbol_ids: frozenset[str]) -> dict[str, Any]:
    if not symbol_ids:
        raise ValidationError("cannot build Pass-2 schema for an empty symbol table")
    string = {"type": "string"}
    endpoint = {"type": "string", "enum": sorted(symbol_ids)}
    evidence = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"quote": string},
            "required": ["quote"],
            "additionalProperties": False,
        },
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
            "source_entity_id": endpoint,
            "relationship_type": {
                "type": "string", "enum": [item.value for item in RelationshipType]
            },
            "target_entity_id": endpoint,
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
    role_binding = {
        "type": "object",
        "properties": {
            "role": {"type": "string", "enum": [item.value for item in PropositionRole]},
            "entity_id": endpoint,
        },
        "required": ["role", "entity_id"],
        "additionalProperties": False,
    }
    proposition = {
        "type": "object",
        "properties": {
            "proposition_type": {
                "type": "string", "enum": [item.value for item in PropositionType]
            },
            "statement": string,
            "role_bindings": {"type": "array", "items": role_binding},
            "relationship_type": {
                "type": "string", "enum": [item.value for item in RelationshipType]
            },
            "comparison_operator": {
                "anyOf": [
                    {"type": "string", "enum": [item.value for item in ComparisonOperator]},
                    {"type": "null"},
                ]
            },
            "evidence": evidence,
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "origin": {"type": "string", "enum": [item.value for item in Origin]},
        },
        "required": [
            "proposition_type", "statement", "role_bindings", "relationship_type",
            "comparison_operator", "evidence", "confidence", "origin",
        ],
        "additionalProperties": False,
    }
    missing_symbol = {
        "type": "object",
        "properties": {
            "surface_form": string,
            "semantic_item": string,
            "reason": string,
        },
        "required": ["surface_form", "semantic_item", "reason"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "claims": {"type": "array", "items": claim},
            "relationships": {"type": "array", "items": relationship},
            "propositions": {"type": "array", "items": proposition},
            "missing_symbols": {"type": "array", "items": missing_symbol},
        },
        "required": ["claims", "relationships", "propositions", "missing_symbols"],
        "additionalProperties": False,
    }


def _response_metadata(response: Any, requested_model: str, prompt_version: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "provider": PROVIDER,
        "requested_model": requested_model,
        "model": getattr(response, "model", None) or requested_model,
        "prompt_version": prompt_version,
        "store": False,
        "sdk_retries": 0,
    }
    request_id = getattr(response, "id", None)
    if request_id:
        metadata["provider_request_id"] = request_id
    usage = _usage_metadata(getattr(response, "usage", None))
    if usage:
        metadata["usage"] = usage
    return metadata


class OpenAIStagedExtractor:
    """Two-call staged adapter; trusted compilation remains provider-neutral."""

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
        self.last_pass_1_raw: Mapping[str, Any] | None = None
        self.last_pass_2_raw: Mapping[str, Any] | None = None
        self.last_pass_1_metadata: Mapping[str, Any] = {}
        self.last_pass_2_metadata: Mapping[str, Any] = {}

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise StagedExtractionError("OPENAI_API_KEY is required for staged extraction")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise StagedExtractionError(
                "OpenAI support is not installed; install knowledge-compiler[llm]"
            ) from exc
        self._client = OpenAI(api_key=api_key, max_retries=0)
        return self._client

    def _request(
        self, *, input_text: str, instructions: str, schema_name: str,
        schema: Mapping[str, Any], prompt_version: str,
    ) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        try:
            response = self._client_or_create().responses.create(
                model=self.model,
                instructions=instructions,
                input=input_text,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": dict(schema),
                    }
                },
                reasoning={"effort": "low"},
                store=False,
            )
        except StagedExtractionError:
            raise
        except Exception as exc:
            raise StagedExtractionError(f"OpenAI {schema_name} request failed: {exc}") from exc
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text:
            raise StagedExtractionError(
                f"OpenAI {schema_name} response did not contain structured output text"
            )
        try:
            raw = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise StagedExtractionError(
                f"OpenAI {schema_name} structured output was not valid JSON: {exc}"
            ) from exc
        if not isinstance(raw, Mapping):
            raise StagedExtractionError(f"OpenAI {schema_name} output was not an object")
        return raw, _response_metadata(response, self.model, prompt_version)

    def discover_symbols(self, document: SourceDocument) -> SymbolDiscoveryProposal:
        instructions = build_symbol_instructions()
        raw, metadata = self._request(
            input_text=document.text,
            instructions=instructions,
            schema_name="symbol_discovery",
            schema=symbol_discovery_schema(),
            prompt_version=SYMBOL_PROMPT_VERSION,
        )
        metadata = {
            **metadata,
            "prompt_character_count": len(instructions),
            "input_character_count": len(document.text),
        }
        self.last_pass_1_raw = dict(raw)
        self.last_pass_1_metadata = metadata
        return SymbolDiscoveryProposal.from_dict({**raw, "metadata": metadata})

    def link_semantics(
        self, document: SourceDocument, symbol_table: SymbolTable
    ) -> SemanticLinkingResult:
        instructions = build_linking_instructions()
        symbol_json = json.dumps(
            [as_entity for as_entity in symbol_table.to_dict()["entities"]],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        input_text = (
            "FROZEN SYMBOL TABLE (use only these IDs):\n"
            f"{symbol_json}\n\nEXACT FULL SOURCE:\n{document.text}"
        )
        raw, metadata = self._request(
            input_text=input_text,
            instructions=instructions,
            schema_name="semantic_linking",
            schema=semantic_linking_schema(symbol_table.ids),
            prompt_version=LINKING_PROMPT_VERSION,
        )
        metadata = {
            **metadata,
            "prompt_character_count": len(instructions),
            "input_character_count": len(input_text),
            "source_character_count": len(document.text),
            "symbol_table_character_count": len(symbol_json),
            "symbol_table_size": len(symbol_table.entities),
        }
        self.last_pass_2_raw = dict(raw)
        self.last_pass_2_metadata = metadata
        resolved = resolve_output_evidence(raw, document)
        resolved["metadata"] = metadata
        return SemanticLinkingResult.from_dict(resolved, document)
