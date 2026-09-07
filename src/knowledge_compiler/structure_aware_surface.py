"""Grounded inspectable-component contracts for SPEC-036."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .explanatory_surface import LearningFocus
from .models import ValidationError


@dataclass(frozen=True)
class InspectionComponent:
    """One trusted representation-local object available for inspection."""

    local_key: str
    kind: str
    identity: str
    label: str
    explanation: str
    predicate: str | None = None
    direction: str | None = None
    evidence: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "local_key": self.local_key,
            "kind": self.kind,
            "identity": self.identity,
            "label": self.label,
            "explanation": self.explanation,
            "predicate": self.predicate,
            "direction": self.direction,
            "evidence": [dict(item) for item in self.evidence],
        }


def inspectable_components(plan: dict[str, Any]) -> tuple[InspectionComponent, ...]:
    """Derive local inspection objects solely from a trusted representation plan."""

    payload = plan.get("payload")
    if not isinstance(payload, dict):
        raise ValidationError("representation plan payload is required")
    if plan.get("strategy_type") == "CONCISE_PROSE":
        return ()
    nodes = payload.get("nodes", [])
    relationships = payload.get("relationships", [])
    by_id: dict[str, InspectionComponent] = {}
    node_ids: set[str] = set()
    for node in nodes:
        identity = node.get("entity_id")
        label = node.get("label")
        explanation = node.get("description")
        if not identity or not label or not explanation:
            raise ValidationError("inspectable concept requires trusted identity, label, and description")
        node_ids.add(identity)
        key = f"concept:{identity}"
        by_id[key] = InspectionComponent(
            local_key=key,
            kind="concept",
            identity=identity,
            label=label,
            explanation=explanation,
        )
    for relationship in relationships:
        identities = relationship.get("relationship_ids", [])
        source = relationship.get("source_entity_id")
        target = relationship.get("target_entity_id")
        predicate = relationship.get("relationship_type")
        meaning = relationship.get("meaning")
        if (
            not identities
            or source not in node_ids
            or target not in node_ids
            or not predicate
            or not meaning
        ):
            raise ValidationError("inspectable relationship is not fully grounded")
        identity = identities[0]
        key = f"canonical:{identity}"
        by_id[key] = InspectionComponent(
            local_key=key,
            kind="canonical",
            identity=identity,
            label=(
                f"{relationship.get('source_label', source)} → "
                f"{relationship.get('target_label', target)}"
            ),
            explanation=meaning,
            predicate=predicate,
            direction=relationship.get("direction"),
            evidence=tuple(dict(item) for item in relationship.get("evidence", [])),
        )
    return tuple(by_id[key] for key in sorted(by_id))


@dataclass
class RepresentationLocalState:
    """Hover and pinned inspection state that cannot write navigation state."""

    context_key: str | None = None
    hovered_component_id: str | None = None
    selected_component_id: str | None = None

    @property
    def effective_component_id(self) -> str | None:
        return self.hovered_component_id or self.selected_component_id

    def synchronize_context(self, context_key: str) -> None:
        if not context_key:
            raise ValidationError("representation context key must be non-empty")
        if context_key != self.context_key:
            self.context_key = context_key
            self.hovered_component_id = None
            self.selected_component_id = None

    def interact(
        self,
        *,
        action: str,
        focus: LearningFocus,
        revealed_object_keys: Iterable[str],
        component_id: str | None = None,
    ) -> dict[str, Any]:
        """Apply one local action and record immutable navigation snapshots."""

        if action not in {"hover", "hover_exit", "select", "clear"}:
            raise ValidationError(f"unknown representation-local action: {action}")
        if action in {"hover", "select"} and not component_id:
            raise ValidationError(f"{action} requires a component id")
        self.synchronize_context(focus.context_key)
        focus_before = focus.to_dict()
        revealed_before = tuple(revealed_object_keys)
        if action == "hover":
            self.hovered_component_id = component_id
        elif action == "hover_exit":
            self.hovered_component_id = None
        elif action == "select":
            self.selected_component_id = (
                None if self.selected_component_id == component_id else component_id
            )
            self.hovered_component_id = None
        else:
            self.hovered_component_id = None
            self.selected_component_id = None
        focus_after = focus.to_dict()
        revealed_after = tuple(revealed_object_keys)
        return {
            "action": action,
            "component_id": component_id,
            "hovered_component_id": self.hovered_component_id,
            "selected_component_id": self.selected_component_id,
            "effective_component_id": self.effective_component_id,
            "focus_before": focus_before,
            "focus_after": focus_after,
            "revealed_before": list(revealed_before),
            "revealed_after": list(revealed_after),
            "navigation_mutation": focus_before != focus_after,
            "revealed_knowledge_mutation": revealed_before != revealed_after,
        }
