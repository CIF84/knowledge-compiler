"""Deterministic learner interaction state over the frozen BASELINE-003 workspace."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal, Mapping

from .models import ValidationError
from .navigation_learning_workspace import _route


GRAMMAR_VERSION = "spec-022-v1"
DEPTH_ENTITY_ID = "double-slit-experiment"
DEPTH_NEIGHBOR_ID = "interference-pattern"
DEPTH_RELATIONSHIP_ID = "relationship-05b19ee4b6d50060"
ORIENTATION_RANK = {"PRIMARY": 0, "SECONDARY": 1, "SPARSE": 2, "HIGH": 3}
BASELINE_CONTROL_HASHES = {
    "index.html": "471257a95c9fd31483e69b436daeed2397f8e052bddc94ddbcf847c19dab2335",
    "workspace.css": "53a6c5593da5c5da7935698d6c8682b4f1f542f6d082d96e77c634cb0432d211",
    "workspace.js": "a6bb507a4bff2eea0f968ea2d3e3dad736b2db865bc10f50124776aad79ca8de",
    "workspace-fixture.json": "a2c8c24bbd58e28f9a41598e22868916c1808133798c738bbf27712124c1b4e9",
}
SPEC021_SEMANTIC_HASHES = {
    "projection.json": "8f1d3beb0e9954040f59862c904a6d9d17574f048bdfcb1cc9059d5df3761232",
    "projection-diagnostics.json": "324a70df4cb3c05ba13bd2c8bdac7ed08e4d76d09546c10aeb3c5924bb2f2dc0",
    "semantic-tier-audit.json": "592b286bde05bf56cd6cd818b9ccb1de3716c7445018765dbc7a2534710935c9",
}
SPEC020_PARENT_REPRESENTATION_HASH = (
    "917868613ac3f997d8f5c2ab3d964db9491e2ab3e710cf8f14858c7722f3b676"
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_files(directory: Path, expected: Mapping[str, str], label: str) -> dict[str, str]:
    actual = {name: file_hash(directory / name) for name in expected}
    if actual != dict(expected):
        raise ValidationError(f"{label} executable control identity mismatch")
    return actual


def choose_orientation_representation(domain: Mapping[str, Any]) -> int:
    representations = domain["learning_model"]["representations"]
    if not representations:
        raise ValidationError(f"region {domain['domain_id']} has no orientation representation")
    return min(
        range(len(representations)),
        key=lambda index: (
            ORIENTATION_RANK.get(representations[index]["salience"], 99),
            -len(representations[index]["nodes"]),
            representations[index]["id"],
        ),
    )


def choose_concept_representation(domain: Mapping[str, Any], entity_id: str) -> int:
    candidates = [
        index for index, representation in enumerate(domain["learning_model"]["representations"])
        if entity_id in {item["entity_id"] for item in representation["nodes"]}
    ]
    if not candidates:
        raise ValidationError(f"no existing representation contains concept {entity_id}")
    return min(candidates, key=lambda index: (
        ORIENTATION_RANK.get(domain["learning_model"]["representations"][index]["salience"], 99),
        domain["learning_model"]["representations"][index]["id"],
    ))


def choose_relationship_representation(domain: Mapping[str, Any], relationship_id: str) -> int:
    candidates = [
        index for index, representation in enumerate(domain["learning_model"]["representations"])
        if any(relationship_id in edge["relationship_ids"] for edge in representation["edges"])
    ]
    if not candidates:
        raise ValidationError(f"no existing representation contains relationship {relationship_id}")
    return min(candidates, key=lambda index: (
        ORIENTATION_RANK.get(domain["learning_model"]["representations"][index]["salience"], 99),
        domain["learning_model"]["representations"][index]["id"],
    ))


def build_learner_fixture(
    baseline: Mapping[str, Any], parent_representation: Mapping[str, Any]
) -> dict[str, Any]:
    fixture = copy.deepcopy(baseline)
    electromagnetism = next(
        domain for domain in fixture["domains"] if domain["domain_id"] == "electromagnetism"
    )
    parent_items = parent_representation["representations"]
    if len(parent_items) != 1:
        raise ValidationError("frozen depth parent must contain exactly one representation")
    parent_item = copy.deepcopy(parent_items[0])
    electromagnetism["learning_model"]["representations"].append(parent_item)
    model_metadata = electromagnetism["learning_model"]["metadata"]
    model_metadata["representation_count"] = len(electromagnetism["learning_model"]["representations"])
    model_metadata["salience_counts"][parent_item["salience"]] = (
        model_metadata["salience_counts"].get(parent_item["salience"], 0) + 1
    )

    parent_nodes = {item["entity_id"]: item for item in parent_item["nodes"]}
    positions = {
        DEPTH_ENTITY_ID: {"x": 1240.0, "y": 1120.0},
        DEPTH_NEIGHBOR_ID: {"x": 1670.0, "y": 1120.0},
    }
    for entity_id in (DEPTH_ENTITY_ID, DEPTH_NEIGHBOR_ID):
        node = parent_nodes[entity_id]
        fixture["navigation"]["nodes"].append({
            "entity_id": entity_id,
            "label": node["label"],
            "description": node["description"],
            "entity_type": node["entity_type"],
            "domain_id": "electromagnetism",
            "world": positions[entity_id],
        })
        fixture["navigation"]["adjacency"][entity_id] = []
    edge = parent_item["edges"][0]
    edge_key = f"depth-{edge['edge_key']}"
    fixture["navigation"]["edges"].append({
        "edge_key": edge_key,
        "source_entity_id": edge["source_entity_id"],
        "target_entity_id": edge["target_entity_id"],
        "relationship_type": edge["relationship_type"],
        "relationship_label": edge["relationship_label"],
        "relationship_ids": list(edge["relationship_ids"]),
        "domain_id": "electromagnetism",
    })
    fixture["navigation"]["world"]["routes"].append({
        "edge_key": edge_key,
        **_route(positions[DEPTH_ENTITY_ID], positions[DEPTH_NEIGHBOR_ID]),
    })
    fixture["navigation"]["adjacency"][DEPTH_ENTITY_ID].append(DEPTH_NEIGHBOR_ID)
    fixture["navigation"]["adjacency"][DEPTH_NEIGHBOR_ID].append(DEPTH_ENTITY_ID)
    fixture["learner_navigation"] = {
        "version": GRAMMAR_VERSION,
        "mode": "LEARNER",
        "debug_mode_query": "debug=1",
        "region_entry": "BEST_EXISTING_REPRESENTATION_BY_SALIENCE_THEN_COVERAGE",
        "concept_selection": "BEST_CONTAINING_REPRESENTATION_BY_SALIENCE",
        "relationship_selection": "BEST_CONTAINING_REPRESENTATION_BY_SALIENCE",
        "admitted_depth_entity_ids": [DEPTH_ENTITY_ID],
        "depth_projection_file": "projection.json",
        "depth_parent_representation_id": parent_item["id"],
        "added_navigation_entity_ids": [DEPTH_ENTITY_ID, DEPTH_NEIGHBOR_ID],
        "added_navigation_relationship_ids": [DEPTH_RELATIONSHIP_ID],
        "existing_control_items_mutated": False,
    }
    validate_learner_fixture(baseline, fixture)
    return fixture


def validate_learner_fixture(baseline: Mapping[str, Any], fixture: Mapping[str, Any]) -> None:
    baseline_domains = {item["domain_id"]: item for item in baseline["domains"]}
    candidate_domains = {item["domain_id"]: item for item in fixture["domains"]}
    if set(candidate_domains) != set(baseline_domains):
        raise ValidationError("SPEC-022 may not replace or create navigation regions")
    for domain_id, original in baseline_domains.items():
        candidate = candidate_domains[domain_id]
        if candidate["world_region"] != original["world_region"]:
            raise ValidationError("SPEC-022 changed frozen region geometry")
        original_reps = original["learning_model"]["representations"]
        if candidate["learning_model"]["representations"][:len(original_reps)] != original_reps:
            raise ValidationError("SPEC-022 changed an existing learning representation")
    original_nodes = {item["entity_id"]: item for item in baseline["navigation"]["nodes"]}
    candidate_nodes = {item["entity_id"]: item for item in fixture["navigation"]["nodes"]}
    if any(candidate_nodes.get(key) != value for key, value in original_nodes.items()):
        raise ValidationError("SPEC-022 changed an existing navigation node or coordinate")
    original_edges = {item["edge_key"]: item for item in baseline["navigation"]["edges"]}
    candidate_edges = {item["edge_key"]: item for item in fixture["navigation"]["edges"]}
    if any(candidate_edges.get(key) != value for key, value in original_edges.items()):
        raise ValidationError("SPEC-022 changed an existing navigation relationship")
    original_routes = {item["edge_key"]: item for item in baseline["navigation"]["world"]["routes"]}
    candidate_routes = {item["edge_key"]: item for item in fixture["navigation"]["world"]["routes"]}
    if any(candidate_routes.get(key) != value for key, value in original_routes.items()):
        raise ValidationError("SPEC-022 changed an existing navigation route")
    if fixture["navigation"]["camera"] != baseline["navigation"]["camera"]:
        raise ValidationError("SPEC-022 changed frozen camera behavior")
    if fixture["navigation"]["world"]["bounds"] != baseline["navigation"]["world"]["bounds"]:
        raise ValidationError("SPEC-022 changed frozen world bounds")
    if fixture["workspace"] != baseline["workspace"]:
        raise ValidationError("SPEC-022 changed frozen workspace focus behavior")
    if set(candidate_nodes) - set(original_nodes) != {DEPTH_ENTITY_ID, DEPTH_NEIGHBOR_ID}:
        raise ValidationError("SPEC-022 navigation additions exceed the frozen depth seam")
    if fixture["learner_navigation"]["admitted_depth_entity_ids"] != [DEPTH_ENTITY_ID]:
        raise ValidationError("SPEC-022 contextual depth eligibility changed")


@dataclass(frozen=True, slots=True)
class LearnerNavigationState:
    domain_id: str
    representation_index: int
    selected_kind: Literal["REGION", "CONCEPT", "RELATIONSHIP"]
    selected_id: str
    depth: Literal["PARENT", "DEEPER"] = "PARENT"
    parent_camera: tuple[float, float, float] = (0.0, 0.0, 1.0)


def enter_depth(state: LearnerNavigationState) -> LearnerNavigationState:
    if state.selected_kind != "CONCEPT" or state.selected_id != DEPTH_ENTITY_ID:
        raise ValidationError("deeper resolution is not admitted for the selected object")
    return replace(state, depth="DEEPER")


def return_from_depth(state: LearnerNavigationState) -> LearnerNavigationState:
    return replace(state, depth="PARENT")
