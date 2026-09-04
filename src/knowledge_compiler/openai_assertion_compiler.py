"""OpenAI adapter for SPEC-013 assertion extraction and canonicalization."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

from .assertion_compilation import (
    AssertionExtractionProposal,
    CanonicalizationProposal,
    GroundedAssertionSet,
)
from .models import (
    ComparisonOperator,
    Origin,
    PropositionRole,
    PropositionType,
    RelationshipType,
    SourceDocument,
)
from .openai_extractor import DEFAULT_MODEL, ExtractionError, _usage_metadata
from .relationships import render_relationship_grammar
from .staged_compilation import SymbolTable


ASSERTION_PROMPT_VERSION = "spec-013-assertions-v1"
CANONICALIZATION_PROMPT_VERSION = "spec-013-canonicalization-v1"
PROVIDER = "openai"


class AssertionProviderError(ExtractionError):
    """An assertion-first provider call failed before trusted compilation."""


ASSERTION_INSTRUCTIONS = """You perform neutral source-assertion extraction.

Read only the supplied full source and frozen symbol table. Extract important, atomic,
source-supported statements before choosing any Knowledge Compiler graph semantics. Each
assertion must preserve what the source says in neutral language, name every relevant
participant that exists in the frozen table, and cite one or more exact, verbatim,
uniquely occurring source substrings.

Use only frozen symbol IDs. Do not create entities. Do not choose or mention canonical
graph predicate names.
Do not force assertions into binary form: assertions may have one, two, or more frozen
participants. Prefer a smaller set of important faithful assertions over exhaustive
sentence decomposition. Split compound passages only when each resulting assertion is
independently supported by its cited evidence. Use SOURCE origin only. Do not use external
knowledge or return anything outside the requested schema."""


CANONICALIZATION_INSTRUCTIONS_BASE = """You perform canonical semantic normalization only
after neutral source assertions have been extracted and grounded by trusted code.

For every supplied assertion ID, choose exactly one disposition:
- one safe binary relationship using the canonical relationship grammar;
- one supported existing typed proposition;
- one claim when the source meaning should remain textual rather than be strengthened;
- one explicit uncompiled assertion with a concrete reason when current canonical forms
  cannot preserve the meaning safely.

Account for every assertion exactly once. Never merge or split assertions. Use only the
supplied frozen symbol IDs and assertion IDs. Do not create entities or evidence. Trusted
code copies the already-resolved source evidence from the assertion into compiled items.
Do not strengthen explanation into causality, an application list into dependency, or a
phenomenon explained by a theory into classification. Never substitute a nearby symbol
when an event, state, condition, or participant is absent. Prefer claims or abstention to
a misleading edge. Fewer truthful edges are better than more graph volume.

Use a typed proposition only for existing forms:
- COMPARISON_CONDITION: LEFT_OPERAND, RIGHT_OPERAND, OUTCOME; GREATER_THAN; CAUSES.
- TRANSFER_EVENT: EVENT, OBJECT, DESTINATION; TRANSFERS_TO; no comparison operator.

Return only the requested schema."""


def build_assertion_instructions() -> str:
    return ASSERTION_INSTRUCTIONS


def build_canonicalization_instructions() -> str:
    return f"{CANONICALIZATION_INSTRUCTIONS_BASE}\n\n{render_relationship_grammar()}"


def assertion_extraction_schema(symbol_ids: frozenset[str]) -> dict[str, Any]:
    string = {"type": "string"}
    return {
        "type": "object",
        "properties": {
            "assertions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "statement": string,
                        "participant_entity_ids": {
                            "type": "array",
                            "items": {"type": "string", "enum": sorted(symbol_ids)},
                        },
                        "evidence": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"quote": string},
                                "required": ["quote"],
                                "additionalProperties": False,
                            },
                        },
                        "origin": {"type": "string", "enum": [Origin.SOURCE.value]},
                    },
                    "required": ["statement", "participant_entity_ids", "evidence", "origin"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["assertions"],
        "additionalProperties": False,
    }


def canonicalization_schema(
    assertion_ids: frozenset[str], symbol_ids: frozenset[str]
) -> dict[str, Any]:
    string = {"type": "string"}
    assertion_id = {"type": "string", "enum": sorted(assertion_ids)}
    entity_id = {"type": "string", "enum": sorted(symbol_ids)}
    confidence = {"type": "number", "minimum": 0, "maximum": 1}
    relationship = {
        "type": "object",
        "properties": {
            "assertion_id": assertion_id,
            "source_entity_id": entity_id,
            "relationship_type": {
                "type": "string", "enum": [item.value for item in RelationshipType]
            },
            "target_entity_id": entity_id,
            "statement": string,
            "confidence": confidence,
        },
        "required": [
            "assertion_id", "source_entity_id", "relationship_type",
            "target_entity_id", "statement", "confidence",
        ],
        "additionalProperties": False,
    }
    role_binding = {
        "type": "object",
        "properties": {
            "role": {"type": "string", "enum": [item.value for item in PropositionRole]},
            "entity_id": entity_id,
        },
        "required": ["role", "entity_id"],
        "additionalProperties": False,
    }
    proposition = {
        "type": "object",
        "properties": {
            "assertion_id": assertion_id,
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
            "confidence": confidence,
        },
        "required": [
            "assertion_id", "proposition_type", "statement", "role_bindings",
            "relationship_type", "comparison_operator", "confidence",
        ],
        "additionalProperties": False,
    }
    claim = {
        "type": "object",
        "properties": {
            "assertion_id": assertion_id,
            "statement": string,
            "confidence": confidence,
        },
        "required": ["assertion_id", "statement", "confidence"],
        "additionalProperties": False,
    }
    uncompiled = {
        "type": "object",
        "properties": {"assertion_id": assertion_id, "reason": string},
        "required": ["assertion_id", "reason"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "relationships": {"type": "array", "items": relationship},
            "propositions": {"type": "array", "items": proposition},
            "claims": {"type": "array", "items": claim},
            "uncompiled_assertions": {"type": "array", "items": uncompiled},
        },
        "required": ["relationships", "propositions", "claims", "uncompiled_assertions"],
        "additionalProperties": False,
    }


def _metadata(response: Any, requested_model: str, prompt_version: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "provider": PROVIDER,
        "requested_model": requested_model,
        "model": getattr(response, "model", None) or requested_model,
        "prompt_version": prompt_version,
        "store": False,
        "sdk_retries": 0,
    }
    request_id = getattr(response, "id", None)
    if request_id:
        result["provider_request_id"] = request_id
    usage = _usage_metadata(getattr(response, "usage", None))
    if usage:
        result["usage"] = usage
    return result


class OpenAIAssertionCompiler:
    """Two-call provider adapter for the assertion-first experiment."""

    def __init__(
        self, *, model: str = DEFAULT_MODEL, api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self._client = client
        self.last_assertion_raw: Mapping[str, Any] | None = None
        self.last_assertion_metadata: Mapping[str, Any] = {}
        self.last_canonicalization_raw: Mapping[str, Any] | None = None
        self.last_canonicalization_metadata: Mapping[str, Any] = {}

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise AssertionProviderError("OPENAI_API_KEY is required for assertion-first compilation")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AssertionProviderError(
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
                text={"format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": dict(schema),
                }},
                reasoning={"effort": "low"},
                store=False,
            )
        except AssertionProviderError:
            raise
        except Exception as exc:
            raise AssertionProviderError(f"OpenAI {schema_name} request failed: {exc}") from exc
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text:
            raise AssertionProviderError(
                f"OpenAI {schema_name} response did not contain structured output text"
            )
        try:
            raw = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise AssertionProviderError(
                f"OpenAI {schema_name} structured output was not valid JSON: {exc}"
            ) from exc
        if not isinstance(raw, Mapping):
            raise AssertionProviderError(f"OpenAI {schema_name} output was not an object")
        return raw, _metadata(response, self.model, prompt_version)

    def extract_assertions(
        self, document: SourceDocument, symbol_table: SymbolTable
    ) -> AssertionExtractionProposal:
        instructions = build_assertion_instructions()
        symbol_json = json.dumps(
            symbol_table.to_dict()["entities"], ensure_ascii=False, separators=(",", ":")
        )
        input_text = (
            "FROZEN SYMBOL TABLE (use only these participant IDs):\n"
            f"{symbol_json}\n\nEXACT FULL SOURCE:\n{document.text}"
        )
        raw, metadata = self._request(
            input_text=input_text,
            instructions=instructions,
            schema_name="source_assertions",
            schema=assertion_extraction_schema(symbol_table.ids),
            prompt_version=ASSERTION_PROMPT_VERSION,
        )
        metadata = {
            **metadata,
            "prompt_character_count": len(instructions),
            "input_character_count": len(input_text),
            "source_character_count": len(document.text),
            "symbol_table_character_count": len(symbol_json),
            "symbol_table_size": len(symbol_table.entities),
        }
        self.last_assertion_raw = dict(raw)
        self.last_assertion_metadata = metadata
        return AssertionExtractionProposal.from_dict({**raw, "metadata": metadata})

    def canonicalize_assertions(
        self, assertions: GroundedAssertionSet, symbol_table: SymbolTable
    ) -> CanonicalizationProposal:
        instructions = build_canonicalization_instructions()
        symbol_json = json.dumps(
            symbol_table.to_dict()["entities"], ensure_ascii=False, separators=(",", ":")
        )
        assertion_json = json.dumps(
            [{
                "id": item.id,
                "statement": item.statement,
                "participant_entity_ids": list(item.participant_entity_ids),
                "evidence_quotes": [span.quote for span in item.evidence],
                "origin": item.origin.value,
            } for item in assertions.assertions],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        input_text = (
            "FROZEN SYMBOL TABLE:\n"
            f"{symbol_json}\n\nGROUNDED SOURCE ASSERTIONS:\n{assertion_json}"
        )
        raw, metadata = self._request(
            input_text=input_text,
            instructions=instructions,
            schema_name="assertion_canonicalization",
            schema=canonicalization_schema(assertions.ids, symbol_table.ids),
            prompt_version=CANONICALIZATION_PROMPT_VERSION,
        )
        metadata = {
            **metadata,
            "prompt_character_count": len(instructions),
            "input_character_count": len(input_text),
            "symbol_table_character_count": len(symbol_json),
            "grounded_assertion_character_count": len(assertion_json),
            "assertion_count": len(assertions.assertions),
            "symbol_table_size": len(symbol_table.entities),
        }
        self.last_canonicalization_raw = dict(raw)
        self.last_canonicalization_metadata = metadata
        return CanonicalizationProposal.from_dict({**raw, "metadata": metadata})
