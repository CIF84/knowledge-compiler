"""Depth-invariant focus resolution for SPEC-025."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from .models import ValidationError


SelectionKind = Literal["concept", "canonical", "explanation"]


@dataclass(frozen=True, slots=True)
class LearningFocus:
    identity: str
    kind: SelectionKind
    item_type: str
    title: str
    semantic_tier: str
    representation_role: str
    evidence_count: int
    expansion_id: str


def _expansion(packet: Mapping[str, Any], expansion_id: str) -> Mapping[str, Any]:
    matches = [item for item in packet["expansions"] if item["id"] == expansion_id]
    if len(matches) != 1:
        raise ValidationError("selected expansion identity is not uniquely registered")
    return matches[0]


def resolve_learning_focus(
    packet: Mapping[str, Any],
    expansion_id: str,
    kind: SelectionKind,
    identity: str,
) -> LearningFocus:
    """Resolve presentation from item identity/type, independent of depth level."""

    expansion = _expansion(packet, expansion_id)
    if kind == "concept":
        collection = expansion["concepts"]
        matches = [item for item in collection if item["entity_id"] == identity]
        if len(matches) != 1:
            raise ValidationError("selected concept is not uniquely present")
        item = matches[0]
        return LearningFocus(
            identity=identity,
            kind=kind,
            item_type="CONCEPT",
            title=item["label"],
            semantic_tier="CONCEPT_IDENTITY",
            representation_role="FOCUS_CONTEXT",
            evidence_count=0,
            expansion_id=expansion_id,
        )
    if kind == "canonical":
        collection = expansion["canonical_items"]
        matches = [item for item in collection if item["id"] == identity]
        if len(matches) != 1:
            raise ValidationError("selected canonical relationship is not uniquely present")
        item = matches[0]
        return LearningFocus(
            identity=identity,
            kind=kind,
            item_type="CANONICAL_RELATIONSHIP",
            title=item["statement"],
            semantic_tier=item["semantic_tier"],
            representation_role="RELATIONSHIP_ENDPOINT_CONTEXT",
            evidence_count=len(item["evidence"]),
            expansion_id=expansion_id,
        )
    if kind == "explanation":
        collection = expansion["explanatory_items"]
        matches = [item for item in collection if item["id"] == identity]
        if len(matches) != 1:
            raise ValidationError("selected explanation is not uniquely present")
        item = matches[0]
        return LearningFocus(
            identity=identity,
            kind=kind,
            item_type="SOURCE_BACKED_EXPLANATION",
            title=item["short_label"],
            semantic_tier=item["semantic_tier"],
            representation_role="PARTICIPANT_PRESERVING_EXPLANATORY_CONTEXT",
            evidence_count=len(item["evidence"]),
            expansion_id=expansion_id,
        )
    raise ValidationError("unknown selectable knowledge-item type")
