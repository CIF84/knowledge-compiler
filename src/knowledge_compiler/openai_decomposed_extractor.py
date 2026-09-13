"""Frozen OpenAI adapter contract for the SPEC-047 Candidate-B extractor.

The adapter is live-capable but is never instantiated by the SPEC-047 artifact
generator. A later explicitly authorized packet may execute it.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any, Mapping

from .decomposed_extraction import (
    CANDIDATE_B_VERSION,
    FrozenEntityInventory,
    SemanticStructure,
    StageAttempt,
    StageExecutionError,
    StageName,
    canonical_json,
    stable_hash,
)
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
from .openai_extractor import DEFAULT_MODEL
from .relationships import render_relationship_grammar


MODEL = DEFAULT_MODEL
PROVIDER = "openai"
STAGE_PROMPT_VERSIONS = {
    StageName.ENTITY_INVENTORY: "spec-047-entity-inventory-v1",
    StageName.SEMANTIC_STRUCTURE: "spec-047-semantic-structure-v1",
    StageName.CLAIM_EVIDENCE_BINDING: "spec-047-claim-evidence-binding-v1",
}

ENTITY_INVENTORY_INSTRUCTIONS = """You perform Stage 1 entity inventory for a semantic compiler.

Read only the exact supplied source. Return a precision-first inventory of concepts,
objects, processes, variables, systems, and components that later semantic statements
need as endpoints or proposition roles. Include source-supported process/event concepts
when later meaning would need to refer to them. Do not use external knowledge.

Do not assign IDs: trusted code assigns stable IDs after this stage. Each semantic thing
must appear once. Do not fragment one identity into variants, merge related but distinct
things, or use aliases except for genuine naming equivalence. Names and descriptions must
remain source-bounded.

Return entities only. Do not return claims, evidence, relationships, propositions,
teaching prose, diagnostics, or output outside the requested schema."""

SEMANTIC_STRUCTURE_INSTRUCTIONS_BASE = """You perform Stage 2 semantic structure extraction.

The user supplies an immutable entity inventory and the exact source. Return only
source-supported relationships and the two supported typed proposition forms. Every
endpoint and role binding must use an exact supplied entity ID. Never create, rename,
alias, or imply a new entity. If an important semantic item requires a missing identity,
omit it and record a missing_symbols diagnostic. Never substitute a nearby identity.

Choose a relationship only when its meaning and direction fit exactly. Do not force
association, explanation, possession, or historical context into PART_OF or CAUSES.
Use a typed proposition only for COMPARISON_CONDITION or TRANSFER_EVENT under the supplied
contract. Proposition IDs are assigned by trusted code; do not return them.

Do not return claims or evidence in this stage. Do not return entities. Do not summarize,
repair the inventory, or emit output outside the requested schema."""

CLAIM_EVIDENCE_INSTRUCTIONS = """You perform Stage 3 claim and evidence binding.

The user supplies an immutable entity inventory, immutable semantic structure, and the
exact source. You may add learner-useful claims and bind exact source evidence to the
supplied relationship/proposition IDs. You must not add, delete, rename, reorder, or alter
entities, relationships, propositions, predicates, directions, role bindings, statements,
confidence, or origin. Return no semantic topology.

Every SOURCE claim and SOURCE semantic object must cite one or more exact, verbatim,
uniquely occurring substrings from the supplied source. Use a complete clause or sentence
long enough to occur exactly once. Never paraphrase a quote or remove text from inside it.
INFERRED claims and semantic objects must have no source evidence. Do not fabricate
evidence or use external knowledge.

Return only claims and semantic_evidence_bindings in the requested schema."""


def build_entity_inventory_instructions() -> str:
    return ENTITY_INVENTORY_INSTRUCTIONS


def build_semantic_structure_instructions() -> str:
    return f"{SEMANTIC_STRUCTURE_INSTRUCTIONS_BASE}\n\n{render_relationship_grammar()}"


def build_claim_evidence_instructions() -> str:
    return CLAIM_EVIDENCE_INSTRUCTIONS


def _evidence_schema() -> dict[str, Any]:
    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"quote": {"type": "string"}},
            "required": ["quote"],
            "additionalProperties": False,
        },
    }


def entity_inventory_schema() -> dict[str, Any]:
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


def semantic_structure_schema(entity_ids: frozenset[str]) -> dict[str, Any]:
    if not entity_ids:
        raise ValidationError("Stage 2 requires a non-empty frozen entity inventory")
    string = {"type": "string"}
    endpoint = {"type": "string", "enum": sorted(entity_ids)}
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
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "origin": {"type": "string", "enum": [item.value for item in Origin]},
        },
        "required": [
            "id", "source_entity_id", "relationship_type", "target_entity_id",
            "statement", "confidence", "origin",
        ],
        "additionalProperties": False,
    }
    proposition = {
        "type": "object",
        "properties": {
            "proposition_type": {
                "type": "string", "enum": [item.value for item in PropositionType]
            },
            "statement": string,
            "role_bindings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string", "enum": [item.value for item in PropositionRole]
                        },
                        "entity_id": endpoint,
                    },
                    "required": ["role", "entity_id"],
                    "additionalProperties": False,
                },
            },
            "relationship_type": {
                "type": "string", "enum": [item.value for item in RelationshipType]
            },
            "comparison_operator": {
                "anyOf": [
                    {"type": "string", "enum": [item.value for item in ComparisonOperator]},
                    {"type": "null"},
                ]
            },
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "origin": {"type": "string", "enum": [item.value for item in Origin]},
        },
        "required": [
            "proposition_type", "statement", "role_bindings", "relationship_type",
            "comparison_operator", "confidence", "origin",
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
            "relationships": {"type": "array", "items": relationship},
            "propositions": {"type": "array", "items": proposition},
            "missing_symbols": {"type": "array", "items": missing_symbol},
        },
        "required": ["relationships", "propositions", "missing_symbols"],
        "additionalProperties": False,
    }


def claim_evidence_schema(semantic_object_ids: frozenset[str]) -> dict[str, Any]:
    string = {"type": "string"}
    claim = {
        "type": "object",
        "properties": {
            "id": string,
            "statement": string,
            "evidence": _evidence_schema(),
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "origin": {"type": "string", "enum": [item.value for item in Origin]},
        },
        "required": ["id", "statement", "evidence", "confidence", "origin"],
        "additionalProperties": False,
    }
    if semantic_object_ids:
        bindings: dict[str, Any] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "semantic_object_id": {
                        "type": "string", "enum": sorted(semantic_object_ids)
                    },
                    "evidence": _evidence_schema(),
                },
                "required": ["semantic_object_id", "evidence"],
                "additionalProperties": False,
            },
        }
    else:
        bindings = {
            "type": "array",
            "maxItems": 0,
            "items": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        }
    return {
        "type": "object",
        "properties": {
            "claims": {"type": "array", "items": claim},
            "semantic_evidence_bindings": bindings,
        },
        "required": ["claims", "semantic_evidence_bindings"],
        "additionalProperties": False,
    }


class ProviderCallLedger:
    """Counts calls at request start and retains all terminal outcomes."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def begin(
        self, *, source_id: str, source_sha256: str, stage: StageName,
        prompt_version: str, prompt_sha256: str, schema_sha256: str,
        upstream_input_sha256: str,
    ) -> dict[str, Any]:
        entry = {
            "call_ordinal": len(self._entries) + 1,
            "source_id": source_id,
            "source_sha256": source_sha256,
            "stage": stage.value,
            "prompt_version": prompt_version,
            "prompt_sha256": prompt_sha256,
            "schema_sha256": schema_sha256,
            "upstream_input_sha256": upstream_input_sha256,
            "status": "REQUEST_STARTED",
            "started_at_utc": datetime.now(UTC).isoformat(),
            "sdk_retries": 0,
            "semantic_retries": 0,
            "repair_calls": 0,
            "hidden_retries": 0,
            "store": False,
        }
        self._entries.append(entry)
        return entry

    def complete(self, entry: dict[str, Any], **values: Any) -> None:
        entry.update(values)
        entry["status"] = "PROVIDER_RESPONSE_RECEIVED"
        entry["completed_at_utc"] = datetime.now(UTC).isoformat()

    def fail(self, entry: dict[str, Any], exc: Exception, duration_ms: float) -> None:
        entry.update({
            "status": "PROVIDER_REQUEST_FAILED",
            "completed_at_utc": datetime.now(UTC).isoformat(),
            "duration_ms": duration_ms,
            "error_type": type(exc).__name__,
            "error": str(exc),
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_version": CANDIDATE_B_VERSION,
            "calls_started": len(self._entries),
            "entries": json.loads(json.dumps(self._entries, sort_keys=True)),
        }


def _response_value(response: Any) -> Mapping[str, Any]:
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    return {
        "id": getattr(response, "id", None),
        "model": getattr(response, "model", None),
        "output_text": getattr(response, "output_text", None),
        "usage": _usage(getattr(response, "usage", None)),
    }


def _usage(value: Any) -> dict[str, int]:
    return {
        name: int(getattr(value, name, 0) or 0)
        for name in ("input_tokens", "output_tokens", "total_tokens")
    }


class OpenAIDecomposedExtractor:
    """Three-call-maximum Candidate-B adapter with no internal retries."""

    live_capable = True

    def __init__(
        self, *, model: str = MODEL, api_key: str | None = None,
        client: Any | None = None, call_ledger: ProviderCallLedger | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self._client = client
        self.call_ledger = call_ledger or ProviderCallLedger()

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise StageExecutionError("OPENAI_API_KEY is required for Candidate B")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise StageExecutionError("OpenAI support is not installed") from exc
        self._client = OpenAI(api_key=api_key, max_retries=0)
        return self._client

    def _request(
        self, *, document: SourceDocument, stage: StageName, instructions: str,
        schema_name: str, schema: Mapping[str, Any], input_text: str,
        upstream_input_sha256: str,
    ) -> StageAttempt:
        client = self._client_or_create()
        prompt_version = STAGE_PROMPT_VERSIONS[stage]
        prompt_sha256 = stable_hash({"instructions": instructions})
        schema_sha256 = stable_hash(schema)
        source_sha256 = hashlib.sha256(document.text.encode("utf-8")).hexdigest()
        source_id = str(document.metadata.get("source_id", document.id))
        entry = self.call_ledger.begin(
            source_id=source_id,
            source_sha256=source_sha256,
            stage=stage,
            prompt_version=prompt_version,
            prompt_sha256=prompt_sha256,
            schema_sha256=schema_sha256,
            upstream_input_sha256=upstream_input_sha256,
        )
        started = time.perf_counter()
        try:
            response = client.responses.create(
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
        except Exception as exc:
            self.call_ledger.fail(entry, exc, (time.perf_counter() - started) * 1000)
            raise StageExecutionError(f"Candidate-B {stage.value} request failed: {exc}") from exc

        duration_ms = (time.perf_counter() - started) * 1000
        raw_response = _response_value(response)
        output_text = getattr(response, "output_text", None)
        metadata = {
            "candidate_version": CANDIDATE_B_VERSION,
            "provider": PROVIDER,
            "requested_model": self.model,
            "actual_model": getattr(response, "model", None) or self.model,
            "provider_response_id": getattr(response, "id", None),
            "http_request_id": getattr(response, "_request_id", None),
            "stage": stage.value,
            "prompt_version": prompt_version,
            "prompt_sha256": prompt_sha256,
            "schema_name": schema_name,
            "schema_sha256": schema_sha256,
            "upstream_input_sha256": upstream_input_sha256,
            "usage": _usage(getattr(response, "usage", None)),
            "duration_ms": duration_ms,
            "store": False,
            "sdk_retries": 0,
            "semantic_retries": 0,
            "repair_calls": 0,
            "hidden_retries": 0,
        }
        self.call_ledger.complete(
            entry,
            duration_ms=duration_ms,
            provider_response_id=metadata["provider_response_id"],
            http_request_id=metadata["http_request_id"],
            requested_model=self.model,
            actual_model=metadata["actual_model"],
            usage=metadata["usage"],
        )
        if not isinstance(output_text, str) or not output_text:
            attempt = StageAttempt(stage, {}, metadata, raw_response)
            raise StageExecutionError(
                f"Candidate-B {stage.value} response lacked structured output", attempt
            )
        try:
            raw = json.loads(output_text)
        except json.JSONDecodeError as exc:
            attempt = StageAttempt(stage, {"unparsed_output_text": output_text}, metadata, raw_response)
            raise StageExecutionError(
                f"Candidate-B {stage.value} output was not valid JSON: {exc}", attempt
            ) from exc
        if not isinstance(raw, Mapping):
            attempt = StageAttempt(stage, {"non_object_output": raw}, metadata, raw_response)
            raise StageExecutionError(
                f"Candidate-B {stage.value} output was not an object", attempt
            )
        return StageAttempt(stage, raw, metadata, raw_response)

    def extract_entity_inventory(self, document: SourceDocument) -> StageAttempt:
        instructions = build_entity_inventory_instructions()
        return self._request(
            document=document,
            stage=StageName.ENTITY_INVENTORY,
            instructions=instructions,
            schema_name="candidate_b_entity_inventory",
            schema=entity_inventory_schema(),
            input_text=document.text,
            upstream_input_sha256=hashlib.sha256(document.text.encode("utf-8")).hexdigest(),
        )

    def extract_semantic_structure(
        self, document: SourceDocument, inventory: FrozenEntityInventory
    ) -> StageAttempt:
        instructions = build_semantic_structure_instructions()
        frozen = canonical_json(inventory.to_dict())
        input_text = (
            f"FROZEN ENTITY INVENTORY:\n{frozen}\n\nEXACT SOURCE:\n{document.text}"
        )
        return self._request(
            document=document,
            stage=StageName.SEMANTIC_STRUCTURE,
            instructions=instructions,
            schema_name="candidate_b_semantic_structure",
            schema=semantic_structure_schema(inventory.ids),
            input_text=input_text,
            upstream_input_sha256=inventory.identity_sha256,
        )

    def extract_claim_evidence(
        self, document: SourceDocument, inventory: FrozenEntityInventory,
        structure: SemanticStructure,
    ) -> StageAttempt:
        instructions = build_claim_evidence_instructions()
        input_text = (
            f"FROZEN ENTITY INVENTORY:\n{canonical_json(inventory.to_dict())}\n\n"
            f"FROZEN SEMANTIC STRUCTURE:\n{canonical_json(structure.to_dict())}\n\n"
            f"EXACT SOURCE:\n{document.text}"
        )
        upstream = stable_hash({
            "inventory": inventory.identity_sha256,
            "structure": structure.identity_sha256,
        })
        return self._request(
            document=document,
            stage=StageName.CLAIM_EVIDENCE_BINDING,
            instructions=instructions,
            schema_name="candidate_b_claim_evidence_binding",
            schema=claim_evidence_schema(structure.semantic_object_ids),
            input_text=input_text,
            upstream_input_sha256=upstream,
        )


def frozen_stage_contracts() -> dict[str, Any]:
    """Return source-independent prompt/schema contracts for audit artifacts."""

    templates = {
        StageName.ENTITY_INVENTORY: (
            build_entity_inventory_instructions(), entity_inventory_schema()
        ),
        StageName.SEMANTIC_STRUCTURE: (
            build_semantic_structure_instructions(),
            semantic_structure_schema(frozenset({"frozen-entity-a", "frozen-entity-b"})),
        ),
        StageName.CLAIM_EVIDENCE_BINDING: (
            build_claim_evidence_instructions(),
            claim_evidence_schema(frozenset({"frozen-semantic-object-a"})),
        ),
    }
    return {
        "candidate_version": CANDIDATE_B_VERSION,
        "provider": PROVIDER,
        "model": MODEL,
        "store": False,
        "sdk_retries": 0,
        "hidden_retries": 0,
        "semantic_retries": 0,
        "repair_calls": 0,
        "dynamic_schema_note": "Stage 2 endpoint enums use the exact frozen Stage-1 IDs; Stage 3 binding enums use the exact frozen Stage-2 object IDs. Per-run schema hashes are recorded.",
        "stages": [
            {
                "stage": stage.value,
                "prompt_version": STAGE_PROMPT_VERSIONS[stage],
                "instructions": instructions,
                "prompt_sha256": stable_hash({"instructions": instructions}),
                "schema_template": schema,
                "schema_sha256": stable_hash(schema),
            }
            for stage, (instructions, schema) in templates.items()
        ],
    }
