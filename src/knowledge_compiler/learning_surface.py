"""Deterministic learner-facing representation resolution for SPEC-030."""

from __future__ import annotations

from typing import Any, Literal

from .models import ValidationError


SemanticKind = Literal["orientation", "concept", "canonical", "explanation"]

CAUSAL_PREDICATES = {"CAUSES", "INCREASES", "DECREASES", "INDUCES"}
HIERARCHY_PREDICATES = {"PART_OF", "IS_A"}
SEQUENCE_PREDICATES = {"PRECEDES", "ENABLES"}


def representation_form(kind: SemanticKind, predicate: str | None = None) -> str:
    """Choose a small truthful presentation form without consulting depth."""

    if kind == "orientation":
        return "ORIENTATION_SUMMARY"
    if kind == "concept":
        return "CONCISE_CONCEPT_EXPLANATION"
    if kind == "explanation":
        return "SOURCE_BACKED_EXPLANATION"
    if kind != "canonical":
        raise ValidationError(f"unsupported learning-surface semantic class: {kind}")
    normalized = (predicate or "").upper()
    if normalized in CAUSAL_PREDICATES:
        return "FOCUSED_CAUSAL_RELATIONSHIP"
    if normalized in HIERARCHY_PREDICATES:
        return "FOCUSED_HIERARCHY_RELATIONSHIP"
    if normalized in SEQUENCE_PREDICATES:
        return "FOCUSED_SEQUENCE_RELATIONSHIP"
    return "FOCUSED_RELATIONSHIP"


def _evidence(value: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(item) for item in value.get("evidence", [])]


def orientation_payload(
    *, domain: dict[str, Any], representation: dict[str, Any]
) -> dict[str, Any]:
    return {
        "semantic_identity": None,
        "semantic_class": "orientation",
        "form": representation_form("orientation"),
        "title": domain["label"],
        "summary": representation["title"],
        "facts": [
            {"label": "Concepts", "value": len(representation["nodes"])},
            {"label": "Relationships", "value": len(representation["edges"])},
            {"label": "Structure", "value": representation["layout"]["strategy"]},
        ],
        "semantic_inputs": [
            "domain.label",
            "representation.title",
            "representation.layout.strategy",
            "representation node/edge counts",
        ],
        "interactive_semantic_elements": [],
        "full_navigation_map": False,
    }


def depth_orientation_payload(*, expansion: dict[str, Any]) -> dict[str, Any]:
    return {
        "semantic_identity": None,
        "semantic_class": "orientation",
        "form": representation_form("orientation"),
        "title": "Double-slit experiment · deeper map",
        "summary": "Focus-centered deeper explanatory context",
        "facts": [
            {"label": "Concepts", "value": len(expansion["concepts"])},
            {"label": "Canonical relationships", "value": len(expansion["canonical_items"])},
            {"label": "Source explanations", "value": len(expansion["explanatory_items"])},
        ],
        "semantic_inputs": [
            "canonical revealed ancestry",
            "depth-map concept/canonical/explanation counts",
        ],
        "interactive_semantic_elements": [],
        "full_navigation_map": False,
    }


def ground_concept_payload(
    *,
    domain: dict[str, Any],
    representation: dict[str, Any],
    identity: str,
) -> dict[str, Any]:
    item = next(
        (node for node in representation["nodes"] if node["entity_id"] == identity),
        None,
    )
    if item is None:
        raise ValidationError(f"concept {identity} is absent from the active representation")
    return {
        "semantic_identity": identity,
        "semantic_class": "concept",
        "form": representation_form("concept"),
        "title": item["label"],
        "description": item.get("description") or "No description was provided.",
        "entity_type": item["entity_type"],
        "context_label": domain["label"],
        "representation_title": representation["title"],
        "semantic_inputs": [
            "representation.nodes[].entity_id",
            "representation.nodes[].label",
            "representation.nodes[].description",
            "representation.nodes[].entity_type",
        ],
        "interactive_semantic_elements": [identity],
        "full_navigation_map": False,
    }


def ground_relationship_payload(
    *,
    domain: dict[str, Any],
    representation: dict[str, Any],
    identity: str,
) -> dict[str, Any]:
    edge = next(
        (
            candidate
            for candidate in representation["edges"]
            if identity in candidate["relationship_ids"]
        ),
        None,
    )
    if edge is None:
        raise ValidationError(
            f"relationship {identity} is absent from the active representation"
        )
    nodes = {item["entity_id"]: item for item in representation["nodes"]}
    source = nodes[edge["source_entity_id"]]
    target = nodes[edge["target_entity_id"]]
    return {
        "semantic_identity": identity,
        "semantic_class": "canonical",
        "form": representation_form("canonical", edge["relationship_type"]),
        "title": f"{source['label']} → {target['label']}",
        "predicate": edge["relationship_type"],
        "direction": edge["direction"],
        "meaning": edge["meaning"],
        "source": {"entity_id": source["entity_id"], "label": source["label"]},
        "target": {"entity_id": target["entity_id"], "label": target["label"]},
        "relationship_ids": list(edge["relationship_ids"]),
        "provenance_status": edge["provenance_status"],
        "evidence": _evidence(edge),
        "context_label": domain["label"],
        "semantic_inputs": [
            "representation.edges selected canonical edge",
            "representation.nodes selected endpoints",
            "edge evidence/provenance",
        ],
        "interactive_semantic_elements": [
            source["entity_id"],
            identity,
            target["entity_id"],
        ],
        "full_navigation_map": False,
    }


def depth_concept_payload(
    *, expansion: dict[str, Any], identity: str
) -> dict[str, Any]:
    item = next(
        (candidate for candidate in expansion["concepts"] if candidate["entity_id"] == identity),
        None,
    )
    if item is None:
        raise ValidationError(f"depth concept {identity} is absent")
    return {
        "semantic_identity": identity,
        "semantic_class": "concept",
        "form": representation_form("concept"),
        "title": item["label"],
        "description": item["description"],
        "entity_type": item["entity_type"],
        "context_label": "Double-slit experiment · deeper map",
        "semantic_inputs": ["depth-map concepts selected item"],
        "interactive_semantic_elements": [identity],
        "full_navigation_map": False,
    }


def depth_relationship_payload(
    *, expansion: dict[str, Any], identity: str
) -> dict[str, Any]:
    item = next(
        (candidate for candidate in expansion["canonical_items"] if candidate["id"] == identity),
        None,
    )
    if item is None:
        raise ValidationError(f"depth relationship {identity} is absent")
    labels = {value["entity_id"]: value["label"] for value in expansion["concepts"]}
    return {
        "semantic_identity": identity,
        "semantic_class": "canonical",
        "form": representation_form("canonical", item["relationship_type"]),
        "title": f"{labels[item['source_entity_id']]} → {labels[item['target_entity_id']]}",
        "predicate": item["relationship_type"],
        "direction": "DIRECTED",
        "meaning": item["predicate_meaning"],
        "statement": item["statement"],
        "source": {
            "entity_id": item["source_entity_id"],
            "label": labels[item["source_entity_id"]],
        },
        "target": {
            "entity_id": item["target_entity_id"],
            "label": labels[item["target_entity_id"]],
        },
        "provenance_status": "EXACT_SOURCE_EVIDENCE",
        "evidence": _evidence(item),
        "context_label": "Double-slit experiment · deeper map",
        "semantic_inputs": ["depth-map canonical_items selected item and endpoints"],
        "interactive_semantic_elements": [
            item["source_entity_id"],
            identity,
            item["target_entity_id"],
        ],
        "full_navigation_map": False,
    }


def depth_explanation_payload(
    *, expansion: dict[str, Any], identity: str
) -> dict[str, Any]:
    item = next(
        (candidate for candidate in expansion["explanatory_items"] if candidate["id"] == identity),
        None,
    )
    if item is None:
        raise ValidationError(f"depth explanation {identity} is absent")
    return {
        "semantic_identity": identity,
        "semantic_class": "explanation",
        "form": representation_form("explanation"),
        "title": item["short_label"],
        "statement": item["statement"],
        "presentation_role": item["presentation_role"],
        "semantic_tier": item["semantic_tier"],
        "participant_entity_ids": list(item["participant_entity_ids"]),
        "evidence": _evidence(item),
        "context_label": "Double-slit experiment · deeper map",
        "semantic_inputs": ["depth-map explanatory_items selected item"],
        "interactive_semantic_elements": [
            identity,
            *item["participant_entity_ids"],
        ],
        "full_navigation_map": False,
    }


def depth_independence_fixture() -> dict[str, Any]:
    rows = []
    for depth in range(11):
        rows.extend(
            {
                "depth": depth,
                "semantic_class": kind,
                "predicate": predicate,
                "form": representation_form(kind, predicate),
            }
            for kind, predicate in (
                ("concept", None),
                ("canonical", "CAUSES"),
                ("canonical", "PART_OF"),
                ("canonical", "PRECEDES"),
                ("explanation", None),
            )
        )
    by_case: dict[tuple[str, str | None], set[str]] = {}
    for row in rows:
        by_case.setdefault((row["semantic_class"], row["predicate"]), set()).add(
            row["form"]
        )
    return {
        "status": "PASS" if all(len(forms) == 1 for forms in by_case.values()) else "FAIL",
        "tested_depths": list(range(11)),
        "resolver_inputs": ["semantic_class", "trusted_relationship_predicate"],
        "depth_is_resolver_input": False,
        "rows": rows,
        "new_product_semantics": [],
    }
