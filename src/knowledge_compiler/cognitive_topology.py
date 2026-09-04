"""Deterministic cognitive topology derived from accepted semantic participation.

Presentation affinity controls proximity and disclosure only.  It is never a
semantic predicate and is intentionally kept outside ``KnowledgeModel``.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from typing import Any

from .assertion_aware_representation import (
    FROZEN_INPUT_SHA256,
    default_spec013_assertion_directory,
    load_frozen_spec013_inputs,
)
from .models import KnowledgeModel, ValidationError
from .relationships import relationship_definition_map


COGNITIVE_TOPOLOGY_VERSION = "spec-017-v1"
CANVAS_WIDTH = 1160
CANVAS_HEIGHT = 680
NODE_WIDTH = 150
NODE_HEIGHT = 76
AREA_PER_INITIAL_CONCEPT = 78_000
MIN_INITIAL_CONCEPTS = 6
MAX_INITIAL_CONCEPTS = 12
MAX_LOCAL_NEIGHBORS = 7


def default_spec016_directory() -> Path:
    return (
        Path(__file__).parents[2]
        / "examples"
        / "evaluations"
        / "spec-016-assertion-aware-representation-20260904"
    )


def _pair(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left < right else (right, left)


def _word_count(value: str) -> int:
    return len(value.replace("—", " ").split())


def _segments_cross(
    a: tuple[float, float], b: tuple[float, float],
    c: tuple[float, float], d: tuple[float, float],
) -> bool:
    def orientation(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    return orientation(a, b, c) * orientation(a, b, d) < 0 and orientation(c, d, a) * orientation(c, d, b) < 0


class CognitiveTopologyProjector:
    """Compile presentation geometry from frozen, trustworthy semantic inputs."""

    affinity_formula = (
        "4*shared_grounded_assertions + 8*canonical_relationship_adjacency + "
        "6*structured_proposition_coparticipation"
    )

    def build(self, frozen: dict[str, Any]) -> dict[str, Any]:
        model: KnowledgeModel = frozen["model"]
        assertions = frozen["assertions"].assertions
        entity_by_id = {item.id: item for item in model.entities}
        ids = sorted(entity_by_id)
        pair_signals: dict[tuple[str, str], dict[str, int]] = defaultdict(
            lambda: {"shared_grounded_assertions": 0, "canonical_relationship_adjacency": 0,
                     "structured_proposition_coparticipation": 0}
        )
        assertion_degree = {entity_id: 0 for entity_id in ids}
        canonical_degree = {entity_id: 0 for entity_id in ids}
        proposition_degree = {entity_id: 0 for entity_id in ids}
        assertion_ids_by_entity: dict[str, list[str]] = {entity_id: [] for entity_id in ids}

        for assertion in assertions:
            for entity_id in assertion.participant_entity_ids:
                if entity_id not in entity_by_id:
                    raise ValidationError(f"assertion {assertion.id} references unknown symbol {entity_id}")
                assertion_degree[entity_id] += 1
                assertion_ids_by_entity[entity_id].append(assertion.id)
            for left, right in combinations(sorted(assertion.participant_entity_ids), 2):
                pair_signals[left, right]["shared_grounded_assertions"] += 1
        for relationship in model.relationships:
            pair_signals[_pair(relationship.source_entity_id, relationship.target_entity_id)][
                "canonical_relationship_adjacency"
            ] += 1
            canonical_degree[relationship.source_entity_id] += 1
            canonical_degree[relationship.target_entity_id] += 1
        for proposition in model.propositions:
            participants = sorted(binding.entity_id for binding in proposition.role_bindings)
            for entity_id in participants:
                proposition_degree[entity_id] += 1
            for left, right in combinations(participants, 2):
                pair_signals[left, right]["structured_proposition_coparticipation"] += 1

        affinities = []
        adjacency: dict[str, list[tuple[str, int]]] = {entity_id: [] for entity_id in ids}
        for (left, right), signals in sorted(pair_signals.items()):
            weight = (
                4 * signals["shared_grounded_assertions"]
                + 8 * signals["canonical_relationship_adjacency"]
                + 6 * signals["structured_proposition_coparticipation"]
            )
            if not weight:
                continue
            affinities.append({
                "concept_ids": [left, right],
                **signals,
                "weight": weight,
                "presentation_only": True,
                "semantic_relationship_created": False,
                "direction": None,
                "predicate": None,
                "uses": ["layout_attraction", "proximity", "focus_neighborhood"],
            })
            adjacency[left].append((right, weight))
            adjacency[right].append((left, weight))
        affinities.sort(key=lambda item: (-item["weight"], *item["concept_ids"]))
        for entity_id in ids:
            adjacency[entity_id].sort(key=lambda item: (-item[1], item[0]))

        weighted_affinity_degree = {
            entity_id: sum(weight for _other, weight in adjacency[entity_id]) for entity_id in ids
        }
        salience = {
            entity_id: (
                4 * assertion_degree[entity_id]
                + 8 * canonical_degree[entity_id]
                + 6 * proposition_degree[entity_id]
                + weighted_affinity_degree[entity_id]
            )
            for entity_id in ids
        }
        ranked = sorted(ids, key=lambda entity_id: (-salience[entity_id], entity_id))
        initial_capacity = max(
            MIN_INITIAL_CONCEPTS,
            min(MAX_INITIAL_CONCEPTS, (CANVAS_WIDTH * CANVAS_HEIGHT) // AREA_PER_INITIAL_CONCEPT),
        )
        initial_ids = ranked[:initial_capacity]
        positions = self._layout(ids, affinities, initial_ids)

        concepts = []
        for entity_id in ids:
            entity = entity_by_id[entity_id]
            concepts.append({
                "id": entity.id,
                "label": entity.name,
                "description": entity.description,
                "entity_type": entity.entity_type.value,
                "aliases": list(entity.aliases),
                "position": positions[entity_id],
                "presentation_salience": salience[entity_id],
                "assertion_degree": assertion_degree[entity_id],
                "canonical_relationship_degree": canonical_degree[entity_id],
                "proposition_degree": proposition_degree[entity_id],
                "initially_visible": entity_id in initial_ids,
                "discoverable": True,
            })

        neighborhoods = []
        for entity_id in ranked:
            if not adjacency[entity_id]:
                continue
            neighbors = adjacency[entity_id][:MAX_LOCAL_NEIGHBORS]
            neighborhoods.append({
                "focus_concept_id": entity_id,
                "member_concept_ids": [entity_id, *(item[0] for item in neighbors)],
                "affinity_weights": [item[1] for item in neighbors],
                "derivation": "FOCUS_PLUS_STRONGEST_PRESENTATION_AFFINITIES",
                "label_source": "FOCAL_TRUSTED_CONCEPT_ONLY",
                "invented_semantic_label": False,
                "presentation_only": True,
            })

        assertion_cards = [{
            "id": item.id,
            "statement": item.statement,
            "participant_entity_ids": list(item.participant_entity_ids),
            "evidence": [asdict(span) for span in item.evidence],
            "origin": item.origin.value,
            "visibility": "LEVEL_2_EXPLICIT_REQUEST",
            "evidence_visibility": "LEVEL_3_EXPLICIT_REQUEST",
        } for item in sorted(assertions, key=lambda item: item.id)]
        relationships = [{
            "id": item.id,
            "source_entity_id": item.source_entity_id,
            "relationship_type": item.relationship_type.value,
            "predicate_meaning": relationship_definition_map()[item.relationship_type].meaning,
            "target_entity_id": item.target_entity_id,
            "statement": item.statement,
            "evidence": [asdict(span) for span in item.evidence],
            "origin": item.origin.value,
            "semantic": True,
            "visibility": "LEVEL_0_IF_BOTH_ENDPOINTS_VISIBLE",
        } for item in sorted(model.relationships, key=lambda item: item.id)]
        propositions = [{
            "id": item.id,
            "proposition_type": item.proposition_type.value,
            "statement": item.statement,
            "role_bindings": [asdict(binding) for binding in item.role_bindings],
            "relationship_type": item.relationship_type.value,
            "comparison_operator": item.comparison_operator.value if item.comparison_operator else None,
            "evidence": [asdict(span) for span in item.evidence],
            "origin": item.origin.value,
            "semantic": True,
            "visibility": "LEVEL_1_ON_RELEVANT_FOCUS",
        } for item in sorted(model.propositions, key=lambda item: item.id)]

        initial_relationships = [
            item["id"] for item in relationships
            if item["source_entity_id"] in initial_ids and item["target_entity_id"] in initial_ids
        ]
        topology = {
            "projector_version": COGNITIVE_TOPOLOGY_VERSION,
            "document_id": model.document.id,
            "title": "Quantum mechanics",
            "product_principle": "Topology first. Text on demand.",
            "semantic_boundary": {
                "semantic_ir_modified": False,
                "presentation_affinity_is_semantic": False,
                "presentation_affinity_creates_relationships": False,
                "new_semantic_truth_created": False,
            },
            "affinity_policy": {
                "formula": self.affinity_formula,
                "retention": "retain every pair with positive weight",
                "display": "proximity only at level 0; no affinity connector",
                "ordering": "descending weight, then lexicographic concept IDs",
            },
            "salience_policy": {
                "formula": "4*assertion_degree + 8*canonical_degree + 6*proposition_degree + weighted_affinity_degree",
                "purpose": "presentation visibility and visual weight only",
                "tie_breaker": "lexicographic concept ID",
            },
            "initial_selection_policy": {
                "capacity_formula": "clamp(6, 12, floor(canvas_area / 78000))",
                "canvas": {"width": CANVAS_WIDTH, "height": CANVAS_HEIGHT},
                "selected_concept_ids": initial_ids,
            },
            "disclosure_levels": [
                {"level": 0, "name": "DOMAIN_SHAPE", "visible": "selected concept labels and canonical edges"},
                {"level": 1, "name": "LOCAL_TOPOLOGY", "visible": "focused concept and up to seven affinity neighbors"},
                {"level": 2, "name": "EXPLANATION", "visible": "one requested grounded assertion"},
                {"level": 3, "name": "EVIDENCE", "visible": "exact evidence for the requested semantic item"},
            ],
            "layout": {
                "strategy": "DETERMINISTIC_FIXED_ITERATION_WEIGHTED_FORCE_2D",
                "canvas_width": CANVAS_WIDTH,
                "canvas_height": CANVAS_HEIGHT,
                "initialization": "lexicographic golden-angle spiral",
                "iterations": 360,
                "runtime_simulation": False,
                "coordinates_rounded_decimals": 3,
            },
            "concepts": concepts,
            "presentation_affinities": affinities,
            "neighborhoods": neighborhoods,
            "canonical_relationships": relationships,
            "structured_propositions": propositions,
            "grounded_assertions": assertion_cards,
            "initial_state": {
                "visible_concept_ids": initial_ids,
                "visible_canonical_relationship_ids": initial_relationships,
                "visible_assertion_ids": [],
                "visible_evidence_ids": [],
                "visible_prose": "A source-grounded topology. Select a concept to explore.",
                "visible_prose_word_count": _word_count("A source-grounded topology. Select a concept to explore."),
                "visible_paragraph_or_card_count": 0,
            },
        }
        self.validate(topology, frozen)
        return topology

    def _layout(
        self,
        ids: list[str],
        affinities: list[dict[str, Any]],
        initial_ids: list[str],
    ) -> dict[str, dict[str, float]]:
        center_x, center_y = CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2
        golden_angle = math.pi * (3 - math.sqrt(5))
        positions: dict[str, list[float]] = {}
        for index, entity_id in enumerate(ids):
            radius = 34 + 14 * math.sqrt(index)
            angle = golden_angle * index
            positions[entity_id] = [center_x + radius * math.cos(angle), center_y + radius * math.sin(angle)]

        edges = [(*item["concept_ids"], item["weight"]) for item in affinities]
        for iteration in range(360):
            movement = {entity_id: [0.0, 0.0] for entity_id in ids}
            for left_index, left in enumerate(ids):
                for right in ids[left_index + 1:]:
                    dx = positions[left][0] - positions[right][0]
                    dy = positions[left][1] - positions[right][1]
                    distance_sq = max(dx * dx + dy * dy, 16.0)
                    distance = math.sqrt(distance_sq)
                    force = 1550.0 / distance_sq
                    fx, fy = force * dx / distance, force * dy / distance
                    movement[left][0] += fx
                    movement[left][1] += fy
                    movement[right][0] -= fx
                    movement[right][1] -= fy
            for left, right, weight in edges:
                dx = positions[right][0] - positions[left][0]
                dy = positions[right][1] - positions[left][1]
                distance = max(math.sqrt(dx * dx + dy * dy), 1.0)
                desired = max(82.0, 178.0 - 5.0 * weight)
                force = 0.0018 * weight * (distance - desired)
                fx, fy = force * dx / distance, force * dy / distance
                movement[left][0] += fx
                movement[left][1] += fy
                movement[right][0] -= fx
                movement[right][1] -= fy
            cooling = 7.0 * (1.0 - iteration / 420.0)
            for entity_id in ids:
                movement[entity_id][0] += (center_x - positions[entity_id][0]) * 0.003
                movement[entity_id][1] += (center_y - positions[entity_id][1]) * 0.003
                magnitude = math.hypot(*movement[entity_id])
                scale = min(1.0, cooling / magnitude) if magnitude else 1.0
                positions[entity_id][0] = min(
                    CANVAS_WIDTH - 75, max(75, positions[entity_id][0] + movement[entity_id][0] * scale)
                )
                positions[entity_id][1] = min(
                    CANVAS_HEIGHT - 55, max(55, positions[entity_id][1] + movement[entity_id][1] * scale)
                )
        # Expand the settled field to use the available viewport before resolving
        # the visible label boxes.  This preserves relative order, not semantics.
        x_values = [value[0] for value in positions.values()]
        y_values = [value[1] for value in positions.values()]
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        for value in positions.values():
            value[0] = 90 + (value[0] - x_min) * (CANVAS_WIDTH - 180) / (x_max - x_min)
            value[1] = 70 + (value[1] - y_min) * (CANVAS_HEIGHT - 140) / (y_max - y_min)

        # Labels are presentation objects with area, not mathematical points.
        # Resolve initial-label collisions deterministically after topology settles.
        for _iteration in range(240):
            changed = False
            for left_index, left in enumerate(initial_ids):
                for right in initial_ids[left_index + 1:]:
                    dx = positions[right][0] - positions[left][0]
                    dy = positions[right][1] - positions[left][1]
                    overlap_x = NODE_WIDTH - abs(dx)
                    overlap_y = NODE_HEIGHT - abs(dy)
                    if overlap_x <= 0 or overlap_y <= 0:
                        continue
                    changed = True
                    if overlap_x / NODE_WIDTH < overlap_y / NODE_HEIGHT:
                        sign = 1.0 if dx >= 0 else -1.0
                        shift = overlap_x / 2 + 1
                        positions[left][0] -= sign * shift
                        positions[right][0] += sign * shift
                    else:
                        sign = 1.0 if dy >= 0 else -1.0
                        shift = overlap_y / 2 + 1
                        positions[left][1] -= sign * shift
                        positions[right][1] += sign * shift
                    for entity_id in (left, right):
                        positions[entity_id][0] = min(CANVAS_WIDTH - 75, max(75, positions[entity_id][0]))
                        positions[entity_id][1] = min(CANVAS_HEIGHT - 55, max(55, positions[entity_id][1]))
            if not changed:
                break
        return {
            entity_id: {"x": round(value[0], 3), "y": round(value[1], 3)}
            for entity_id, value in positions.items()
        }

    def diagnostics(self, topology: dict[str, Any]) -> dict[str, Any]:
        initial = set(topology["initial_state"]["visible_concept_ids"])
        concepts = {item["id"]: item for item in topology["concepts"]}
        overlaps = 0
        initial_list = sorted(initial)
        for index, left in enumerate(initial_list):
            for right in initial_list[index + 1:]:
                a, b = concepts[left]["position"], concepts[right]["position"]
                if abs(a["x"] - b["x"]) < NODE_WIDTH and abs(a["y"] - b["y"]) < NODE_HEIGHT:
                    overlaps += 1
        visible_edges = [
            item for item in topology["canonical_relationships"]
            if item["source_entity_id"] in initial and item["target_entity_id"] in initial
        ]
        crossings = 0
        for index, left in enumerate(visible_edges):
            left_ids = {left["source_entity_id"], left["target_entity_id"]}
            for right in visible_edges[index + 1:]:
                if left_ids & {right["source_entity_id"], right["target_entity_id"]}:
                    continue
                a = concepts[left["source_entity_id"]]["position"]
                b = concepts[left["target_entity_id"]]["position"]
                c = concepts[right["source_entity_id"]]["position"]
                d = concepts[right["target_entity_id"]]["position"]
                if _segments_cross((a["x"], a["y"]), (b["x"], b["y"]), (c["x"], c["y"]), (d["x"], d["y"])):
                    crossings += 1
        return {"initial_label_overlap_count": overlaps, "canonical_edge_crossing_count": crossings}

    def validate(self, topology: dict[str, Any], frozen: dict[str, Any]) -> None:
        model: KnowledgeModel = frozen["model"]
        assertions = frozen["assertions"].assertions
        if {item["id"] for item in topology["concepts"]} != {item.id for item in model.entities}:
            raise ValidationError("cognitive projection changed the trusted symbol inventory")
        expected_edges = {
            (item.id, item.source_entity_id, item.relationship_type.value, item.target_entity_id)
            for item in model.relationships
        }
        actual_edges = {
            (item["id"], item["source_entity_id"], item["relationship_type"], item["target_entity_id"])
            for item in topology["canonical_relationships"]
        }
        if actual_edges != expected_edges:
            raise ValidationError("cognitive projection changed canonical semantic edges")
        if {item["id"] for item in topology["grounded_assertions"]} != {item.id for item in assertions}:
            raise ValidationError("cognitive projection changed grounded assertions")
        if any(
            not item["presentation_only"] or item["semantic_relationship_created"]
            or item["direction"] is not None or item["predicate"] is not None
            for item in topology["presentation_affinities"]
        ):
            raise ValidationError("presentation affinity must remain explicitly non-semantic")
        if any(item["invented_semantic_label"] for item in topology["neighborhoods"]):
            raise ValidationError("cognitive projection invented a semantic neighborhood label")
        initial = topology["initial_state"]
        if not MIN_INITIAL_CONCEPTS <= len(initial["visible_concept_ids"]) <= MAX_INITIAL_CONCEPTS:
            raise ValidationError("initial concept density is outside the bounded range")
        if initial["visible_assertion_ids"] or initial["visible_evidence_ids"]:
            raise ValidationError("explanations and evidence must be latent at level 0")
        if initial["visible_paragraph_or_card_count"] != 0:
            raise ValidationError("level 0 must not show prose cards or paragraphs")


def load_and_build_cognitive_topology(
    spec_013_dir: Path = default_spec013_assertion_directory(),
) -> tuple[dict[str, Any], dict[str, Any]]:
    frozen = load_frozen_spec013_inputs(spec_013_dir)
    return frozen, CognitiveTopologyProjector().build(frozen)


__all__ = [
    "COGNITIVE_TOPOLOGY_VERSION", "FROZEN_INPUT_SHA256", "CognitiveTopologyProjector",
    "default_spec013_assertion_directory", "default_spec016_directory",
    "load_and_build_cognitive_topology",
]
