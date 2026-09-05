"""Semantic connection classification for SPEC-026."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .models import ValidationError


@dataclass(frozen=True, slots=True)
class LearnerConnection:
    identity: str
    semantic_class: str
    label: str
    directional: bool
    canonical: bool
    selectable_kind: str | None
    selectable_identity: str | None
    source_identity: str
    target_identity: str
    semantic_tier: str


def classify_expansion_connections(expansion: Mapping[str, Any]) -> list[LearnerConnection]:
    """Classify every learner-visible connection without minting semantics."""

    concepts = {item["entity_id"] for item in expansion["concepts"]}
    explanations = {item["id"]: item for item in expansion["explanatory_items"]}
    if len(explanations) != len(expansion["explanatory_items"]):
        raise ValidationError("explanatory identities are not unique")

    result: list[LearnerConnection] = []
    for item in expansion["canonical_items"]:
        if item["source_entity_id"] not in concepts or item["target_entity_id"] not in concepts:
            raise ValidationError("canonical relationship endpoint is not present")
        if item["semantic_tier"] != "TRUSTED_CANONICAL" or not item["evidence"]:
            raise ValidationError("canonical relationship lacks trusted evidence")
        result.append(
            LearnerConnection(
                identity=item["id"],
                semantic_class="CANONICAL_RELATIONSHIP",
                label=item["relationship_type"],
                directional=True,
                canonical=True,
                selectable_kind="canonical",
                selectable_identity=item["id"],
                source_identity=item["source_entity_id"],
                target_identity=item["target_entity_id"],
                semantic_tier=item["semantic_tier"],
            )
        )

    for index, attachment in enumerate(expansion["explanatory_attachments"]):
        item = explanations.get(attachment["explanatory_item_id"])
        if item is None:
            raise ValidationError("explanatory attachment has no source item")
        participant = attachment["participant_entity_id"]
        if participant not in concepts or participant not in item["participant_entity_ids"]:
            raise ValidationError("explanatory attachment participant is not grounded")
        if (
            attachment["kind"] != "NON_DIRECTIONAL_PRESENTATION_ATTACHMENT"
            or item["directional"] is not False
            or item["semantic_tier"] != "SOURCE_BACKED_NON_CANONICAL"
            or item["presentation_role"] != "SOURCE_BACKED_EXPLANATION"
        ):
            raise ValidationError("explanatory attachment semantic class changed")
        result.append(
            LearnerConnection(
                identity=f"attachment-{index:02d}",
                semantic_class="SOURCE_BACKED_EXPLANATORY_ATTACHMENT",
                label="EXPLANATORY",
                directional=False,
                canonical=False,
                selectable_kind="explanation",
                selectable_identity=item["id"],
                source_identity=item["id"],
                target_identity=participant,
                semantic_tier=item["semantic_tier"],
            )
        )

    result.append(
        LearnerConnection(
            identity=f"ancestry-{expansion['id']}",
            semantic_class="DEPTH_ANCESTRY",
            label="DEEPER FROM",
            directional=True,
            canonical=False,
            selectable_kind=None,
            selectable_identity=None,
            source_identity=expansion["origin"]["entity_id"],
            target_identity=expansion["id"],
            semantic_tier="NAVIGATION_CONTEXT",
        )
    )
    return result


def connection_classification_audit(expansion: Mapping[str, Any]) -> dict[str, Any]:
    connections = classify_expansion_connections(expansion)
    return {
        "status": "PASS",
        "connections": [asdict(item) for item in connections],
        "counts": {
            "all_visible_connections": len(connections),
            "canonical_relationships": sum(item.canonical for item in connections),
            "explanatory_attachments": sum(
                item.semantic_class == "SOURCE_BACKED_EXPLANATORY_ATTACHMENT"
                for item in connections
            ),
            "depth_ancestry_paths": sum(
                item.semantic_class == "DEPTH_ANCESTRY" for item in connections
            ),
            "unclassified": 0,
            "fabricated_pairwise_relationships": 0,
        },
    }
