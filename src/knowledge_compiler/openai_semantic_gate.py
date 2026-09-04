"""OpenAI adapter for the bounded SPEC-014 semantic admission gate."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

from .models import ValidationError
from .openai_extractor import DEFAULT_MODEL, ExtractionError, _usage_metadata
from .semantic_gate import GatePacket, GateResult, GateVerdict


GATE_PROMPT_VERSION = "spec-014-gate-v1"
PROVIDER = "openai"


class SemanticGateProviderError(ExtractionError):
    """The single semantic-gate provider call failed."""


GATE_INSTRUCTIONS = """You are an independent bounded semantic admission judge.

For each supplied candidate, decide whether its exact canonical commitment is justified by
the grounded assertion, exact evidence, frozen participant symbols, and supplied canonical
contract. Judge the candidate as written. Do not rewrite, repair, weaken, strengthen, split,
or replace it. Do not invent entities, evidence, source context, predicates, propositions,
or explanations beyond the local packet.

Return exactly one decision per candidate using only this frozen verdict vocabulary:
- ADMIT: the exact candidate, endpoints, direction, and predicate/proposition contract are supported.
- TOO_STRONG: the candidate strengthens the assertion beyond its evidence.
- WRONG_PREDICATE: the endpoints may be relevant but the canonical predicate is not justified.
- WRONG_ENDPOINT: one or more chosen endpoints do not represent what the assertion relates.
- REQUIRES_STRUCTURED_PROPOSITION: the meaning cannot safely be represented by this binary candidate.
- INSUFFICIENT_FOR_CANONICALIZATION: the local grounded material cannot justify this commitment.

Give a brief rationale tied only to the candidate and contract. The candidate IDs are opaque.
The packet deliberately omits benchmark labels and expected review answers. Return only the
requested structured output."""


def gate_response_schema(candidate_ids: frozenset[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "packet_candidate_id": {
                            "type": "string", "enum": sorted(candidate_ids)
                        },
                        "verdict": {
                            "type": "string", "enum": [item.value for item in GateVerdict]
                        },
                        "rationale": {"type": "string"},
                    },
                    "required": ["packet_candidate_id", "verdict", "rationale"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["decisions"],
        "additionalProperties": False,
    }


def _metadata(response: Any, requested_model: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "provider": PROVIDER,
        "requested_model": requested_model,
        "model": getattr(response, "model", None) or requested_model,
        "prompt_version": GATE_PROMPT_VERSION,
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


class OpenAISemanticGate:
    """One-call independent judge; candidate generation is outside this adapter."""

    def __init__(
        self, *, model: str = DEFAULT_MODEL, api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self._client = client
        self.last_raw: Mapping[str, Any] | None = None
        self.last_metadata: Mapping[str, Any] = {}

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SemanticGateProviderError("OPENAI_API_KEY is required for semantic gate evaluation")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise SemanticGateProviderError(
                "OpenAI support is not installed; install knowledge-compiler[llm]"
            ) from exc
        self._client = OpenAI(api_key=api_key, max_retries=0)
        return self._client

    def judge(self, packet: GatePacket) -> GateResult:
        gate_input = packet.to_gate_input()
        input_text = json.dumps(gate_input, ensure_ascii=False, separators=(",", ":"))
        ids = frozenset(item.packet_candidate_id for item in packet.items)
        try:
            response = self._client_or_create().responses.create(
                model=self.model,
                instructions=GATE_INSTRUCTIONS,
                input=input_text,
                text={"format": {
                    "type": "json_schema",
                    "name": "semantic_admission_decisions",
                    "strict": True,
                    "schema": gate_response_schema(ids),
                }},
                reasoning={"effort": "low"},
                store=False,
            )
        except SemanticGateProviderError:
            raise
        except Exception as exc:
            raise SemanticGateProviderError(f"OpenAI semantic gate request failed: {exc}") from exc
        metadata = {
            **_metadata(response, self.model),
            "prompt_character_count": len(GATE_INSTRUCTIONS),
            "input_character_count": len(input_text),
            "candidate_count": len(packet.items),
            "packet_hash": packet.packet_hash,
            "benchmark_labels_exposed": False,
        }
        self.last_metadata = metadata
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text:
            raise SemanticGateProviderError("OpenAI semantic gate response lacked structured output")
        try:
            raw = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise SemanticGateProviderError(
                f"OpenAI semantic gate structured output was invalid JSON: {exc}"
            ) from exc
        if not isinstance(raw, Mapping):
            raise SemanticGateProviderError("OpenAI semantic gate output was not an object")
        self.last_raw = dict(raw)
        try:
            return GateResult.from_dict({**raw, "metadata": metadata}, packet)
        except ValidationError:
            raise
