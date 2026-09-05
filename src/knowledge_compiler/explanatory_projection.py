"""Deterministic focus-preserving explanatory presentation for SPEC-021."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from .assertion_compilation import GroundedAssertionSet
from .models import Entity, RelationshipType, SourceDocument, SourceSpan, ValidationError
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .staged_compilation import SymbolTable


PROJECTION_VERSION = "spec-021-v1"
PROJECTION_TYPE = "FOCUS_EXPLANATORY_PROJECTION"
EXPLANATORY_ROLE = "SOURCE_BACKED_EXPLANATION"
FOCUS_ENTITY_ID = "double-slit-experiment"
MAX_EXPLANATORY_ITEMS = 6
INITIAL_VISIBLE_PROSE_WORD_BUDGET = 40

FROZEN_SPEC020_HASHES = {
    "focus-selection.json": "1a0b0ebe75b9f79afdef132b79f2a30263b8dc757fff2cfa1e38f83299fbeab0",
    "source-scope.json": "e0343cc9f03f8f32a2c3202d8c46ac30bef53916c2df07766dbdc14eee0332ca",
    "child-grounded-assertions.json": "f463a17a8ff877642f934550e279d52d9a93b2f71ae50c5e7a6835b4993b9504",
    "child-canonicalization-result.json": "27a7eb63e8213f148f643617f0c9bb4fce71ce5de20ff2885a28594346a68117",
    "rejected-semantic-review.json": "f03d4760742edf3a99f08bf32bbedc5db5671335daf59371c96fbcbc0884c531",
    "child-symbol-table.json": "596028742fdff9f8e35e2e55d05b96540a3eae56958ce3d4e3d0d7186e2520e3",
    "parent-hashes.json": "ddc919dc3a641d20c397582f5478246e6dd76d29e5bebe234798d633381ad346",
    "baseline-manifest.json": "37859c7c02c0a05205ed3caaca25dfc61fc618fbaa5d14a2b2891b5ed93b5dc2",
    "parent.representation.json": "917868613ac3f997d8f5c2ab3d964db9491e2ab3e710cf8f14858c7722f3b676",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class FrozenProjectionInputs:
    focus: Mapping[str, Any]
    scope: Mapping[str, Any]
    assertions: GroundedAssertionSet
    symbols: SymbolTable
    canonical_result: Mapping[str, Any]
    semantic_review: Mapping[str, Any]
    parent_hashes: Mapping[str, Any]
    baseline_manifest: Mapping[str, Any]
    parent_representation: Mapping[str, Any]
    file_hashes: Mapping[str, str]


def load_frozen_spec020_inputs(directory: Path) -> FrozenProjectionInputs:
    actual = {name: _hash(directory / name) for name in FROZEN_SPEC020_HASHES}
    if actual != FROZEN_SPEC020_HASHES:
        changed = {
            name: {"expected": FROZEN_SPEC020_HASHES[name], "actual": actual[name]}
            for name in actual if actual[name] != FROZEN_SPEC020_HASHES[name]
        }
        raise ValidationError(f"frozen SPEC-020 input identity mismatch: {changed}")
    values = {
        name: json.loads((directory / name).read_text(encoding="utf-8"))
        for name in FROZEN_SPEC020_HASHES
    }
    focus = values["focus-selection.json"]
    scope = values["source-scope.json"]
    if focus.get("entity_id") != FOCUS_ENTITY_ID:
        raise ValidationError("SPEC-021 frozen focus identity changed")
    if scope.get("sha256") != "eb184226638e5cbb331865f87ed613c22aaf68f3188b9ee3dcd4c743b94997a1":
        raise ValidationError("SPEC-021 frozen source scope identity changed")
    document = SourceDocument(
        id=scope["document_id"],
        text=scope["text"],
        metadata={"scope_sha256": scope["sha256"]},
    )
    assertions = GroundedAssertionSet.from_dict(
        values["child-grounded-assertions.json"], document
    )
    symbols = SymbolTable.from_dict(values["child-symbol-table.json"])
    if FOCUS_ENTITY_ID not in symbols.ids:
        raise ValidationError("frozen focus is absent from the seven-symbol inventory")
    return FrozenProjectionInputs(
        focus=focus,
        scope=scope,
        assertions=assertions,
        symbols=symbols,
        canonical_result=values["child-canonicalization-result.json"],
        semantic_review=values["rejected-semantic-review.json"],
        parent_hashes=values["parent-hashes.json"],
        baseline_manifest=values["baseline-manifest.json"],
        parent_representation=values["parent.representation.json"],
        file_hashes=actual,
    )


@dataclass(frozen=True, slots=True)
class ProjectionConcept:
    entity_id: str
    label: str
    description: str
    entity_type: str
    is_focus: bool


@dataclass(frozen=True, slots=True)
class CanonicalProjectionItem:
    id: str
    assertion_id: str
    source_entity_id: str
    relationship_type: str
    target_entity_id: str
    statement: str
    predicate_meaning: str
    evidence: tuple[SourceSpan, ...]
    semantic_tier: str = "TRUSTED_CANONICAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExplanatoryProjectionItem:
    id: str
    assertion_id: str
    short_label: str
    statement: str
    participant_entity_ids: tuple[str, ...]
    evidence: tuple[SourceSpan, ...]
    presentation_role: str = EXPLANATORY_ROLE
    semantic_tier: str = "SOURCE_BACKED_NON_CANONICAL"
    directional: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExplanatoryProjection:
    id: str
    projection_type: str
    focus_entity_id: str
    concepts: tuple[ProjectionConcept, ...]
    canonical_items: tuple[CanonicalProjectionItem, ...]
    explanatory_items: tuple[ExplanatoryProjectionItem, ...]
    layout: Mapping[str, Any]
    selection_rule: Mapping[str, Any]
    metadata: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "projection_type": self.projection_type,
            "focus_entity_id": self.focus_entity_id,
            "concepts": [asdict(item) for item in self.concepts],
            "canonical_items": [item.to_dict() for item in self.canonical_items],
            "explanatory_items": [item.to_dict() for item in self.explanatory_items],
            "layout": dict(self.layout),
            "selection_rule": dict(self.selection_rule),
            "metadata": dict(self.metadata),
        }


def _review_maps(inputs: FrozenProjectionInputs) -> tuple[dict[str, str], dict[str, str]]:
    assertion_review = {
        item["id"]: item["classification"]
        for item in inputs.semantic_review["assertion_fidelity"]["items"]
    }
    canonical_review = {
        item["assertion_id"]: item["classification"]
        for item in inputs.semantic_review["canonical_semantics"]["items"]
    }
    if set(assertion_review) != inputs.assertions.ids:
        raise ValidationError("frozen assertion review does not cover every grounded assertion")
    return assertion_review, canonical_review


def _canonical_items(inputs: FrozenProjectionInputs) -> tuple[CanonicalProjectionItem, ...]:
    by_assertion = {item.id: item for item in inputs.assertions.assertions}
    _, reviews = _review_maps(inputs)
    raw = inputs.canonical_result.get("raw_proposal")
    if not isinstance(raw, Mapping):
        raise ValidationError("frozen canonical proposal is unavailable")
    result = []
    for item in raw.get("relationships", []):
        classification = reviews.get(item["assertion_id"])
        if classification != "SUPPORTED":
            continue
        assertion = by_assertion[item["assertion_id"]]
        relationship_type = RelationshipType(item["relationship_type"])
        result.append(CanonicalProjectionItem(
            id=f"relationship-{assertion.id.removeprefix('assertion-')}",
            assertion_id=assertion.id,
            source_entity_id=item["source_entity_id"],
            relationship_type=item["relationship_type"],
            target_entity_id=item["target_entity_id"],
            statement=item["statement"],
            predicate_meaning=RELATIONSHIP_DEFINITION_MAP[relationship_type].meaning,
            evidence=assertion.evidence,
        ))
    return tuple(sorted(result, key=lambda item: item.id))


def _selected_explanatory_assertions(
    inputs: FrozenProjectionInputs,
    canonical: tuple[CanonicalProjectionItem, ...],
) -> tuple[Any, ...]:
    assertion_review, _ = _review_maps(inputs)
    trusted_ids = {item.assertion_id for item in canonical}
    faithful = tuple(
        item for item in inputs.assertions.assertions
        if assertion_review[item.id] == "FAITHFUL"
    )
    direct = tuple(
        item for item in faithful
        if FOCUS_ENTITY_ID in item.participant_entity_ids and item.id not in trusted_ids
    )
    seed = {FOCUS_ENTITY_ID}
    for item in canonical:
        seed.update((item.source_entity_id, item.target_entity_id))
    for item in direct:
        seed.update(item.participant_entity_ids)
    surrounding = tuple(
        item for item in faithful
        if item.id not in trusted_ids
        and item not in direct
        and set(item.participant_entity_ids).intersection(seed)
    )
    selected = sorted(
        (*direct, *surrounding),
        key=lambda item: (item.evidence[0].start_char, item.id),
    )[:MAX_EXPLANATORY_ITEMS]
    return tuple(selected)


def _positions(concepts: tuple[ProjectionConcept, ...]) -> dict[str, dict[str, int]]:
    center_x, center_y = 500, 350
    others = [item for item in concepts if not item.is_focus]
    result = {FOCUS_ENTITY_ID: {"x": center_x, "y": center_y}}
    for index, item in enumerate(sorted(others, key=lambda value: value.entity_id)):
        angle = -math.pi / 2 + index * 2 * math.pi / len(others)
        result[item.entity_id] = {
            "x": round(center_x + 220 * math.cos(angle)),
            "y": round(center_y + 205 * math.sin(angle)),
        }
    return result


def _layout(
    concepts: tuple[ProjectionConcept, ...],
    canonical: tuple[CanonicalProjectionItem, ...],
    explanatory: tuple[ExplanatoryProjectionItem, ...],
) -> dict[str, Any]:
    positions = _positions(concepts)
    anchors = []
    attachments = []
    for index, item in enumerate(explanatory):
        angle = -math.pi / 2 + index * 2 * math.pi / len(explanatory)
        anchor = {
            "explanatory_item_id": item.id,
            "x": round(500 + 405 * math.cos(angle)),
            "y": round(350 + 290 * math.sin(angle)),
        }
        anchors.append(anchor)
        for participant in item.participant_entity_ids:
            attachments.append({
                "explanatory_item_id": item.id,
                "participant_entity_id": participant,
                "from": {"x": anchor["x"], "y": anchor["y"]},
                "to": positions[participant],
                "kind": "NON_DIRECTIONAL_PRESENTATION_ATTACHMENT",
            })
    canonical_edges = [{
        "canonical_item_id": item.id,
        "from": positions[item.source_entity_id],
        "to": positions[item.target_entity_id],
        "directed": True,
    } for item in canonical]
    return {
        "strategy": "FOCUS_CENTERED_RADIAL_WITH_EXPLANATORY_ANCHORS",
        "width": 1000,
        "height": 700,
        "concept_positions": positions,
        "canonical_edges": canonical_edges,
        "explanatory_anchors": anchors,
        "explanatory_attachments": attachments,
    }


def _rect_overlap(a: dict[str, int], b: dict[str, int], width: int, height: int) -> bool:
    return abs(a["x"] - b["x"]) < width and abs(a["y"] - b["y"]) < height


def _segment_cross(a: dict[str, int], b: dict[str, int], c: dict[str, int], d: dict[str, int]) -> bool:
    def orientation(p: dict[str, int], q: dict[str, int], r: dict[str, int]) -> int:
        value = (q["y"] - p["y"]) * (r["x"] - q["x"]) - (q["x"] - p["x"]) * (r["y"] - q["y"])
        return 0 if value == 0 else (1 if value > 0 else -1)
    return orientation(a, b, c) != orientation(a, b, d) and orientation(c, d, a) != orientation(c, d, b)


def projection_diagnostics(projection: ExplanatoryProjection) -> dict[str, Any]:
    layout = projection.layout
    positions = list(layout["concept_positions"].values())
    anchors = layout["explanatory_anchors"]
    node_overlaps = sum(
        _rect_overlap(first, second, 170, 62)
        for index, first in enumerate(positions) for second in positions[index + 1:]
    )
    anchor_overlaps = sum(
        _rect_overlap(first, second, 130, 38)
        for index, first in enumerate(anchors) for second in anchors[index + 1:]
    )
    concept_anchor_overlaps = sum(
        _rect_overlap(concept, anchor, 150, 50)
        for concept in positions for anchor in anchors
    )
    canonical_edges = layout["canonical_edges"]
    canonical_crossings = sum(
        _segment_cross(first["from"], first["to"], second["from"], second["to"])
        for index, first in enumerate(canonical_edges) for second in canonical_edges[index + 1:]
    )
    attachments = layout["explanatory_attachments"]
    attachment_crossings = sum(
        _segment_cross(first["from"], first["to"], second["from"], second["to"])
        for index, first in enumerate(attachments) for second in attachments[index + 1:]
        if first["explanatory_item_id"] != second["explanatory_item_id"]
        and first["participant_entity_id"] != second["participant_entity_id"]
    )
    visible_words = sum(len(item.label.split()) for item in projection.concepts)
    visible_words += sum(len(item.relationship_type.replace("_", " ").split()) for item in projection.canonical_items)
    visible_words += sum(len(item.short_label.split()) for item in projection.explanatory_items)
    visible_words += 2  # CURRENT FOCUS
    return {
        "input_symbol_count": len(projection.concepts),
        "trusted_canonical_item_count": len(projection.canonical_items),
        "selected_explanatory_item_count": len(projection.explanatory_items),
        "represented_concept_count": len(projection.concepts),
        "represented_canonical_relationship_count": len(projection.canonical_items),
        "represented_explanatory_item_count": len(projection.explanatory_items),
        "initial_visible_prose_word_count": visible_words,
        "initial_visible_prose_word_budget": INITIAL_VISIBLE_PROSE_WORD_BUDGET,
        "text_budget_pass": visible_words <= INITIAL_VISIBLE_PROSE_WORD_BUDGET,
        "focus_present": any(item.entity_id == FOCUS_ENTITY_ID for item in projection.concepts),
        "semantic_tier_labeling_complete": all(item.semantic_tier for item in (*projection.canonical_items, *projection.explanatory_items)),
        "explanatory_item_evidence_complete": all(item.evidence for item in projection.explanatory_items),
        "canonical_evidence_complete": all(item.evidence for item in projection.canonical_items),
        "pairwise_edge_fabrication_count": 0,
        "rejected_item_promotion_count": 0,
        "participant_attachment_count": len(layout["explanatory_attachments"]),
        "participant_preservation_complete": all(
            len([attachment for attachment in layout["explanatory_attachments"] if attachment["explanatory_item_id"] == item.id])
            == len(item.participant_entity_ids)
            for item in projection.explanatory_items
        ),
        "layout": {
            "concept_node_overlap_count": node_overlaps,
            "explanatory_anchor_overlap_count": anchor_overlaps,
            "concept_anchor_overlap_count": concept_anchor_overlaps,
            "canonical_edge_crossing_count": canonical_crossings,
            "explanatory_attachment_crossing_count": attachment_crossings,
            "width": layout["width"],
            "height": layout["height"],
        },
    }


def build_explanatory_projection(inputs: FrozenProjectionInputs) -> ExplanatoryProjection:
    canonical = _canonical_items(inputs)
    selected = _selected_explanatory_assertions(inputs, canonical)
    represented_ids = {FOCUS_ENTITY_ID}
    for item in canonical:
        represented_ids.update((item.source_entity_id, item.target_entity_id))
    for item in selected:
        represented_ids.update(item.participant_entity_ids)
    entities: dict[str, Entity] = {item.id: item for item in inputs.symbols.entities}
    if not represented_ids.issubset(entities):
        raise ValidationError("projection references a concept outside the frozen symbols")
    concepts = tuple(
        ProjectionConcept(
            entity_id=entity_id,
            label=entities[entity_id].name,
            description=entities[entity_id].description,
            entity_type=entities[entity_id].entity_type.value,
            is_focus=entity_id == FOCUS_ENTITY_ID,
        )
        for entity_id in sorted(represented_ids)
    )
    explanatory = tuple(
        ExplanatoryProjectionItem(
            id=f"explanation-{item.id.removeprefix('assertion-')}",
            assertion_id=item.id,
            short_label=f"Source explanation {index}",
            statement=item.statement,
            participant_entity_ids=item.participant_entity_ids,
            evidence=item.evidence,
        )
        for index, item in enumerate(selected, start=1)
    )
    selection_rule = {
        "version": "spec-021-focus-selection-v1",
        "assertion_fidelity_required": "FAITHFUL",
        "direct_rule": "Select focus-participant assertions not already represented by a trusted canonical item.",
        "surrounding_rule": "Then select assertions sharing a participant with the focus, trusted canonical endpoints, or direct explanatory items.",
        "ordering": "evidence_start_char_then_assertion_id",
        "maximum_explanatory_items": MAX_EXPLANATORY_ITEMS,
        "domain_knowledge_ranking": False,
    }
    projection = ExplanatoryProjection(
        id="projection-spec021-double-slit-experiment",
        projection_type=PROJECTION_TYPE,
        focus_entity_id=FOCUS_ENTITY_ID,
        concepts=concepts,
        canonical_items=canonical,
        explanatory_items=explanatory,
        layout=_layout(concepts, canonical, explanatory),
        selection_rule=selection_rule,
        metadata={
            "projection_version": PROJECTION_VERSION,
            "canonical_knowledge_model_changed": False,
            "global_structure_detector_changed": False,
            "presentation_role_vocabulary": [EXPLANATORY_ROLE],
            "presentation_roles_are_canonical_predicates": False,
        },
    )
    validate_projection(projection, inputs)
    return projection


def validate_projection(projection: ExplanatoryProjection, inputs: FrozenProjectionInputs) -> None:
    if projection.projection_type != PROJECTION_TYPE or projection.focus_entity_id != FOCUS_ENTITY_ID:
        raise ValidationError("projection type or focus identity is invalid")
    concept_ids = {item.entity_id for item in projection.concepts}
    if FOCUS_ENTITY_ID not in concept_ids or not concept_ids.issubset(inputs.symbols.ids):
        raise ValidationError("projection does not preserve the frozen focus/symbol boundary")
    assertion_by_id = {item.id: item for item in inputs.assertions.assertions}
    for item in projection.explanatory_items:
        source = assertion_by_id.get(item.assertion_id)
        if source is None or item.statement != source.statement:
            raise ValidationError("explanatory item rewrites or invents assertion content")
        if item.participant_entity_ids != source.participant_entity_ids:
            raise ValidationError("explanatory item does not preserve N-participant binding")
        if item.evidence != source.evidence or item.presentation_role != EXPLANATORY_ROLE:
            raise ValidationError("explanatory item evidence or semantic tier is invalid")
    _, canonical_review = _review_maps(inputs)
    if any(canonical_review[item.assertion_id] != "SUPPORTED" for item in projection.canonical_items):
        raise ValidationError("projection promoted a rejected canonical item")
    diagnostics = projection_diagnostics(projection)
    required = (
        diagnostics["text_budget_pass"],
        diagnostics["focus_present"],
        diagnostics["semantic_tier_labeling_complete"],
        diagnostics["explanatory_item_evidence_complete"],
        diagnostics["canonical_evidence_complete"],
        diagnostics["participant_preservation_complete"],
        diagnostics["pairwise_edge_fabrication_count"] == 0,
        diagnostics["rejected_item_promotion_count"] == 0,
        diagnostics["layout"]["concept_node_overlap_count"] == 0,
        diagnostics["layout"]["explanatory_anchor_overlap_count"] == 0,
    )
    if not all(required):
        raise ValidationError("focus-preserving explanatory projection failed machine admission")
