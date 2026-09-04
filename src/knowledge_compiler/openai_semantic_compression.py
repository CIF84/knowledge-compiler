"""OpenAI adapter for the one-call SPEC-015 semantic-compression judge."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

from .models import ValidationError
from .openai_extractor import ExtractionError, _usage_metadata
from .semantic_compression import CompressionResult, CompressionVerdict


COMPRESSION_PROMPT_VERSION = "spec-015-compression-judge-v1"
DEFAULT_COMPRESSION_MODEL = "gpt-5.6-luna"
PROVIDER = "openai"


class SemanticCompressionProviderError(ExtractionError):
    """The single semantic-compression provider call failed."""


COMPRESSION_INSTRUCTIONS = """You are an independent bounded semantic-compression judge.

For each case, decide whether the proposed binary relationship faithfully preserves the grounded
source assertion under the supplied canonical predicate source/target role contract. Judge source
meaning, not general plausibility. Context may be omitted when the binary relationship remains true
as the source means it. Reject lossy compression when an endpoint substitutes for the real role-holder,
an essential explicit or implicit participant/event/state/condition is lost, or the assertion requires
an existing structured proposition rather than this binary edge.

Use exactly one verdict per opaque case ID from this fixed vocabulary:
- BINARY_ADEQUATE: predicate and endpoints faithfully preserve the essential assertion.
- SOURCE_ROLE_INADEQUATE: the source endpoint does not fill the predicate's source role.
- TARGET_ROLE_INADEQUATE: the target endpoint does not fill the predicate's target role.
- MISSING_ESSENTIAL_PARTICIPANT: an explicit omitted participant is essential to the meaning.
- MISSING_IMPLICIT_PARTICIPANT: an unrepresented implicit event/state/condition/role-holder is essential.
- REQUIRES_STRUCTURED_PROPOSITION: an existing structured proposition is required for faithful meaning.
- INSUFFICIENT_FOR_BINARY_RELATIONSHIP: the proposed edge should not be admitted, but no more specific
  category is justified.

Do not rewrite the relationship, propose replacement endpoints, mint symbols, invent predicates or
proposition types, repair the assertion/evidence, use outside knowledge, or produce an alternative
graph. Return only the requested case ID, verdict, and a brief source-bounded rationale."""


def compression_response_schema(case_ids: frozenset[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "decisions": {
                "type": "array",
                "minItems": len(case_ids),
                "maxItems": len(case_ids),
                "items": {
                    "type": "object",
                    "properties": {
                        "case_id": {"type": "string", "enum": sorted(case_ids)},
                        "verdict": {
                            "type": "string",
                            "enum": [item.value for item in CompressionVerdict],
                        },
                        "rationale": {"type": "string"},
                    },
                    "required": ["case_id", "verdict", "rationale"],
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
        "prompt_version": COMPRESSION_PROMPT_VERSION,
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


class OpenAISemanticCompressionJudge:
    """Isolated one-call adapter; benchmark construction and scoring remain offline."""

    def __init__(
        self, *, model: str = DEFAULT_COMPRESSION_MODEL, api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self._client = client
        self.last_raw: Mapping[str, Any] | None = None
        self.last_output_text: str | None = None
        self.last_metadata: Mapping[str, Any] = {}

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SemanticCompressionProviderError(
                "OPENAI_API_KEY is required for SPEC-015 semantic-compression evaluation"
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise SemanticCompressionProviderError(
                "OpenAI support is not installed; install knowledge-compiler[llm]"
            ) from exc
        self._client = OpenAI(api_key=api_key, max_retries=0)
        return self._client

    def judge(
        self, blinded_packet: Mapping[str, Any], expected_case_ids: frozenset[str]
    ) -> CompressionResult:
        input_text = json.dumps(blinded_packet, ensure_ascii=False, separators=(",", ":"))
        try:
            response = self._client_or_create().responses.create(
                model=self.model,
                instructions=COMPRESSION_INSTRUCTIONS,
                input=input_text,
                text={"format": {
                    "type": "json_schema",
                    "name": "semantic_compression_decisions",
                    "strict": True,
                    "schema": compression_response_schema(expected_case_ids),
                }},
                reasoning={"effort": "low"},
                store=False,
            )
        except SemanticCompressionProviderError:
            raise
        except Exception as exc:
            raise SemanticCompressionProviderError(
                f"OpenAI semantic-compression request failed: {exc}"
            ) from exc
        metadata = {
            **_metadata(response, self.model),
            "prompt_character_count": len(COMPRESSION_INSTRUCTIONS),
            "input_character_count": len(input_text),
            "case_count": len(expected_case_ids),
            "benchmark_labels_exposed": False,
            "candidate_descriptions_exposed": False,
            "external_enrichment": False,
        }
        self.last_metadata = metadata
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text:
            raise SemanticCompressionProviderError(
                "OpenAI semantic-compression response lacked structured output"
            )
        self.last_output_text = output_text
        try:
            raw = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise SemanticCompressionProviderError(
                f"OpenAI semantic-compression structured output was invalid JSON: {exc}"
            ) from exc
        if not isinstance(raw, Mapping):
            raise SemanticCompressionProviderError(
                "OpenAI semantic-compression output was not an object"
            )
        self.last_raw = dict(raw)
        try:
            return CompressionResult.from_dict(
                {**raw, "metadata": metadata}, expected_case_ids
            )
        except ValidationError:
            raise
