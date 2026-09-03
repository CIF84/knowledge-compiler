"""OpenAI adapter for the bounded SPEC-008 resolution compiler."""

from __future__ import annotations

import json
import os
from typing import Any

from .models import EntityType, Origin, RelationshipType
from .openai_extractor import DEFAULT_MODEL, ExtractionError, _usage_metadata, extraction_schema
from .relationships import render_relationship_grammar
from .resolution_compiler import (
    RESOLUTION_PROMPT_VERSION,
    ResolutionNomination,
    ResolutionOutcome,
    ResolutionRequest,
    SourceScope,
)
from .resolution_strategies import (
    ResolutionStrategyId,
    get_resolution_strategy,
    render_resolution_strategy,
)


PROVIDER = "openai"
SPEC_009_PROMPT_VERSION = "spec-009-v1"
SPEC_010_PROMPT_VERSION = "spec-010-v1"


def resolution_schema() -> dict[str, Any]:
    base = extraction_schema()
    return {
        "type": "object",
        "properties": {
            "outcome": {
                "type": "string",
                "enum": ["SUCCESS", "INSUFFICIENT_SOURCE_DETAIL"],
            },
            "reason": {"type": "string"},
            "entities": base["properties"]["entities"],
            "claims": base["properties"]["claims"],
            "relationships": base["properties"]["relationships"],
            "propositions": base["properties"]["propositions"],
        },
        "required": [
            "outcome", "reason", "entities", "claims", "relationships", "propositions"
        ],
        "additionalProperties": False,
    }


def build_resolution_instructions(
    strategy_id: ResolutionStrategyId | str = ResolutionStrategyId.GENERIC_DETAIL,
) -> str:
    strategy = get_resolution_strategy(strategy_id)
    return f"""You compile exactly one finer semantic resolution for a selected parent concept.

{render_resolution_strategy(strategy)}

Use only the permitted source text supplied in the request. The selected parent focus must remain
central. Produce a finer explanatory resolution, not a summary. The child should plausibly
compress back into the parent concept. Do not add detail from general knowledge.

Return INSUFFICIENT_SOURCE_DETAIL with empty entities, claims, relationships, and propositions whenever the
permitted source cannot support at least two meaningful typed relationships at a finer level.
This is a correct and preferred outcome over fabrication.

SOURCE items require exact, verbatim, uniquely occurring quotes from the permitted source.
Return quotes only; trusted code resolves coordinates. INFERRED items must have empty evidence
and must never be used to smuggle external knowledge into a successful result. Prefer truthful
claims over forced edges. Do not return offsets, diagrams, navigation metadata, or prose outside
the schema.

Use ordinary binary relationships only when their two endpoints preserve the complete source
proposition. For a comparative antecedent, return a COMPARISON_CONDITION proposition with both
operands, the comparison operator, and outcome. For a transfer, return a TRANSFER_EVENT
proposition with distinct event, object, and destination roles. Never collapse a compound
condition to one operand or use the transfer process as its destination. Trusted code assigns
proposition IDs and rejects detectable endpoint loss.

Entity types: {', '.join(item.value for item in EntityType)}
Origins: {', '.join(item.value for item in Origin)}
Relationship types: {', '.join(item.value for item in RelationshipType)}

{render_relationship_grammar()}"""


def build_resolution_input(request: ResolutionRequest, parent: Any, scope: SourceScope) -> str:
    focus = next(item for item in parent.entities if item.id == request.focus_entity_id)
    strategy = get_resolution_strategy(request.strategy_id)
    connected = [
        {
            "id": relationship.id,
            "source": relationship.source_entity_id,
            "type": relationship.relationship_type.value,
            "target": relationship.target_entity_id,
            "statement": relationship.statement,
        }
        for relationship in parent.relationships
        if request.focus_entity_id in (relationship.source_entity_id, relationship.target_entity_id)
    ]
    return json.dumps({
        "selected_parent_concept": {
            "id": focus.id,
            "label": focus.name,
            "description": focus.description,
            "aliases": list(focus.aliases),
            "parent_representation_id": request.parent_representation_id,
            "domain": request.domain,
        },
        "direct_parent_relationships": connected,
        "resolution_strategy": {
            "id": strategy.id.value,
            "semantic_role": strategy.semantic_role,
        },
        "permitted_source": {
            "document_id": scope.document_id,
            "strategy": scope.strategy,
            "start_char": scope.start_char,
            "end_char": scope.end_char,
            "text": scope.text,
        },
    }, indent=2, ensure_ascii=False)


class OpenAIResolutionExtractor:
    """Nominate one source-bounded child model using structured Responses output."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        prompt_version: str = SPEC_010_PROMPT_VERSION,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        if not isinstance(prompt_version, str) or not prompt_version.strip():
            raise ValueError("resolution prompt version must be non-empty")
        self.prompt_version = prompt_version
        self.api_key = api_key
        self._client = client

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ExtractionError("OPENAI_API_KEY is required for live resolution evaluation")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ExtractionError("OpenAI support is not installed; install knowledge-compiler[llm]") from exc
        self._client = OpenAI(api_key=api_key, max_retries=0)
        return self._client

    def nominate(self, request: ResolutionRequest, parent: Any, scope: SourceScope) -> ResolutionNomination:
        try:
            response = self._client_or_create().responses.create(
                model=self.model,
                instructions=build_resolution_instructions(request.strategy_id),
                input=build_resolution_input(request, parent, scope),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "child_resolution_extraction",
                        "strict": True,
                        "schema": resolution_schema(),
                    }
                },
                reasoning={"effort": "low"},
                store=False,
            )
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError(f"OpenAI resolution request failed: {exc}") from exc
        output_text = getattr(response, "output_text", None)
        if not isinstance(output_text, str) or not output_text:
            raise ExtractionError("OpenAI resolution response had no structured output text")
        try:
            raw = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ExtractionError(f"OpenAI resolution output was not valid JSON: {exc}") from exc
        outcome = ResolutionOutcome(raw.pop("outcome"))
        reason = raw.pop("reason")
        metadata: dict[str, Any] = {
            "extractor": "llm-resolution",
            "provider": PROVIDER,
            "model": getattr(response, "model", None) or self.model,
            "prompt_version": self.prompt_version,
            "resolution_strategy_id": request.strategy_id.value,
        }
        request_id = getattr(response, "id", None)
        if request_id:
            metadata["provider_request_id"] = request_id
        usage = _usage_metadata(getattr(response, "usage", None))
        if usage:
            metadata["usage"] = usage
        return ResolutionNomination(outcome=outcome, reason=reason, extraction=raw, metadata=metadata)
