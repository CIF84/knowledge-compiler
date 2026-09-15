"""Distinct frozen model-facing contract for SPEC-051 Candidate B v2.

No provider request is made by contract generation or offline fixtures.
"""

from __future__ import annotations

from typing import Any, Mapping

from .decomposed_extraction import FrozenEntityInventory, SemanticStructure, StageAttempt, StageExecutionError, StageName, canonical_json, stable_hash
from .decomposed_extraction_v2 import CANDIDATE_B_V2_VERSION, STAGE2_V2_VERSION, STAGE3_V2_VERSION
from .models import EntityType, Origin, SourceDocument
from .openai_decomposed_extractor import (
    MODEL,
    PROVIDER,
    OpenAIDecomposedExtractor,
    ProviderCallLedger,
    build_claim_evidence_instructions,
    build_entity_inventory_instructions,
    claim_evidence_schema,
    entity_inventory_schema,
    semantic_structure_schema,
)
from .relationships import render_relationship_grammar


_STAGE2_INSTRUCTIONS = """You perform Stage 2 semantic structure extraction for Candidate B v2.

Use only the exact source and immutable frozen entity inventory. Every endpoint must
be one of the exact supplied entity IDs. Do not invent or substitute an identity.
Return only source-supported canonical relationships, COMPARISON_CONDITION instances,
TRANSFER_EVENT instances, and missing_symbols diagnostics in the requested schema.

Emit topology only when the exact source-supported meaning fits the trusted relationship
contract or one of the two canonical proposition forms. Otherwise omit the meaning from
Stage-2 topology. Never approximate, coerce, or choose a nearby predicate/proposition.
Stage 3 independently reads the exact source and can preserve omitted meaning as an
exact grounded claim. Do not use missing_symbols for non-topological omission; reserve it
for an otherwise valid canonical semantic item lacking a required frozen identity.

COMPARISON_CONDITION means a comparison used as a causal antecedent with a distinct
LEFT_OPERAND and RIGHT_OPERAND, an OUTCOME caused by that condition, GREATER_THAN, and
CAUSES. A standalone comparison without a causal outcome is not this proposition.
TRANSFER_EVENT means a PROCESS EVENT, transferred OBJECT, and non-PROCESS DESTINATION,
with TRANSFERS_TO and no comparison operator. Input to a calculation is not automatically
a transfer event. Emit neither proposition when these exact meanings are unsupported.

Do not return entities, claims, evidence, teaching prose, or new semantic vocabulary.
Proposition IDs are assigned by trusted code; do not return them."""

_STAGE3_OMISSION_INSTRUCTIONS = """\n\nCandidate B v2 semantic omission invariant: independently preserve source-supported,
learner-useful meanings as exact grounded claims even when Stage 2 emitted no relationship
or proposition for them. Do not convert a claim into topology or alter the frozen Stage-2
structure. A claim must cite exact, uniquely occurring source text."""


def build_stage2_v2_instructions() -> str:
    return f"{_STAGE2_INSTRUCTIONS}\n\n{render_relationship_grammar()}"


def build_stage3_v2_instructions() -> str:
    return build_claim_evidence_instructions() + _STAGE3_OMISSION_INSTRUCTIONS


def stage2_v2_schema(inventory: FrozenEntityInventory) -> dict[str, Any]:
    """Separate strict variant arrays avoid provider-specific union features."""
    baseline = semantic_structure_schema(inventory.ids)
    base = baseline["properties"]
    frozen_ids = sorted(inventory.ids)
    process_ids = sorted(entity.id for entity in inventory.symbol_table.entities if entity.entity_type is EntityType.PROCESS)
    destination_ids = sorted(entity.id for entity in inventory.symbol_table.entities if entity.entity_type is not EntityType.PROCESS)
    endpoint = {"type": "string", "enum": frozen_ids}
    common = {
        "statement": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "origin": {"type": "string", "enum": [item.value for item in Origin]},
    }
    comparison_properties = {
        **common,
        "proposition_type": {"type": "string", "enum": ["COMPARISON_CONDITION"]},
        "left_operand_entity_id": endpoint,
        "right_operand_entity_id": endpoint,
        "outcome_entity_id": endpoint,
        "relationship_type": {"type": "string", "enum": ["CAUSES"]},
        "comparison_operator": {"type": "string", "enum": ["GREATER_THAN"]},
    }
    transfer_properties = {
        **common,
        "proposition_type": {"type": "string", "enum": ["TRANSFER_EVENT"]},
        "event_entity_id": {"type": "string", "enum": process_ids or frozen_ids},
        "object_entity_id": endpoint,
        "destination_entity_id": {"type": "string", "enum": destination_ids or frozen_ids},
        "relationship_type": {"type": "string", "enum": ["TRANSFERS_TO"]},
        "comparison_operator": {"type": "null"},
    }
    comparison = {"type": "object", "properties": comparison_properties, "required": list(comparison_properties), "additionalProperties": False}
    transfer = {"type": "object", "properties": transfer_properties, "required": list(transfer_properties), "additionalProperties": False}
    transfer_array: dict[str, Any] = {"type": "array", "items": transfer}
    if not process_ids or not destination_ids:
        transfer_array["maxItems"] = 0
    return {
        "type": "object",
        "properties": {
            "relationships": base["relationships"],
            "comparison_conditions": {"type": "array", "items": comparison},
            "transfer_events": transfer_array,
            "missing_symbols": base["missing_symbols"],
        },
        "required": ["relationships", "comparison_conditions", "transfer_events", "missing_symbols"],
        "additionalProperties": False,
    }


class ProviderCallLedgerV2(ProviderCallLedger):
    def begin(self, **kwargs: Any) -> dict[str, Any]:
        stage = kwargs["stage"]
        if stage is StageName.SEMANTIC_STRUCTURE:
            kwargs["prompt_version"] = STAGE2_V2_VERSION
        elif stage is StageName.CLAIM_EVIDENCE_BINDING:
            kwargs["prompt_version"] = STAGE3_V2_VERSION
        entry = super().begin(**kwargs)
        entry["candidate_version"] = CANDIDATE_B_V2_VERSION
        return entry

    def to_dict(self) -> dict[str, Any]:
        value = super().to_dict()
        value["candidate_version"] = CANDIDATE_B_V2_VERSION
        return value


class OpenAICandidateBV2Extractor(OpenAIDecomposedExtractor):
    """Three-stage v2 adapter; inherited Stage 1 mechanics and zero SDK retries."""

    candidate_version = CANDIDATE_B_V2_VERSION

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("call_ledger", ProviderCallLedgerV2())
        super().__init__(**kwargs)

    def _request(self, **kwargs: Any) -> StageAttempt:
        stage = kwargs["stage"]
        try:
            attempt = super()._request(**kwargs)
        except StageExecutionError as exc:
            if exc.attempt is None:
                raise
            metadata = self._versioned_metadata(stage, exc.attempt.provider_metadata)
            raise StageExecutionError(str(exc), StageAttempt(stage, exc.attempt.raw_proposal, metadata, exc.attempt.raw_provider_response)) from exc
        metadata = self._versioned_metadata(stage, attempt.provider_metadata)
        return StageAttempt(stage, attempt.raw_proposal, metadata, attempt.raw_provider_response)

    @staticmethod
    def _versioned_metadata(stage: StageName, metadata: Mapping[str, Any]) -> dict[str, Any]:
        version = {StageName.SEMANTIC_STRUCTURE: STAGE2_V2_VERSION, StageName.CLAIM_EVIDENCE_BINDING: STAGE3_V2_VERSION}.get(stage)
        return {**metadata, "candidate_version": CANDIDATE_B_V2_VERSION, "prompt_version": version or metadata.get("prompt_version")}

    def extract_semantic_structure(self, document: SourceDocument, inventory: FrozenEntityInventory) -> StageAttempt:
        return self._request(
            document=document,
            stage=StageName.SEMANTIC_STRUCTURE,
            instructions=build_stage2_v2_instructions(),
            schema_name="candidate_b_v2_semantic_structure",
            schema=stage2_v2_schema(inventory),
            input_text=f"FROZEN ENTITY INVENTORY:\n{canonical_json(inventory.to_dict())}\n\nEXACT SOURCE:\n{document.text}",
            upstream_input_sha256=inventory.identity_sha256,
        )

    def extract_claim_evidence(self, document: SourceDocument, inventory: FrozenEntityInventory, structure: SemanticStructure) -> StageAttempt:
        return self._request(
            document=document,
            stage=StageName.CLAIM_EVIDENCE_BINDING,
            instructions=build_stage3_v2_instructions(),
            schema_name="candidate_b_v2_claim_evidence_binding",
            schema=claim_evidence_schema(structure.semantic_object_ids),
            input_text=(
                f"FROZEN ENTITY INVENTORY:\n{canonical_json(inventory.to_dict())}\n\n"
                f"FROZEN SEMANTIC STRUCTURE:\n{canonical_json(structure.to_dict())}\n\n"
                f"EXACT SOURCE:\n{document.text}"
            ),
            upstream_input_sha256=stable_hash({"inventory": inventory.identity_sha256, "structure": structure.identity_sha256}),
        )


def frozen_v2_stage_contracts(template_inventory: FrozenEntityInventory) -> dict[str, Any]:
    stages = (
        (StageName.ENTITY_INVENTORY, "spec-047-entity-inventory-v1", build_entity_inventory_instructions(), entity_inventory_schema()),
        (StageName.SEMANTIC_STRUCTURE, STAGE2_V2_VERSION, build_stage2_v2_instructions(), stage2_v2_schema(template_inventory)),
        (StageName.CLAIM_EVIDENCE_BINDING, STAGE3_V2_VERSION, build_stage3_v2_instructions(), claim_evidence_schema(frozenset({"frozen-semantic-object-a"}))),
    )
    return {
        "candidate_version": CANDIDATE_B_V2_VERSION,
        "provider": PROVIDER,
        "model": MODEL,
        "store": False,
        "sdk_retries": 0,
        "hidden_retries": 0,
        "semantic_retries": 0,
        "repair_calls": 0,
        "schema_form": "separate strict comparison_conditions and transfer_events arrays with fixed subtype fields",
        "residual_deterministic_rules": ["comparison operand distinctness", "frozen entity/type checks", "canonical source/evidence and KnowledgeModel validation"],
        "stages": [
            {
                "stage": stage.value,
                "prompt_version": version,
                "instructions": instructions,
                "prompt_sha256": stable_hash({"instructions": instructions}),
                "schema_template": schema,
                "schema_sha256": stable_hash(schema),
            }
            for stage, version, instructions, schema in stages
        ],
    }
