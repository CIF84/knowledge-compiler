"""Deterministic learner traversal history and trusted exploration suggestions."""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from typing import Any

from .models import ValidationError
from .relationship_multiplicity import relationship_records


def _object_key(kind: str, identity: str) -> str:
    return f"{kind}:{identity}"


def _concept(
    *,
    identity: str,
    label: str,
    domain_id: str,
    representation_index: int,
    ancestry: list[str] | None = None,
    source: str,
) -> dict[str, Any]:
    return {
        "object_key": _object_key("concept", identity),
        "semantic_identity": identity,
        "kind": "concept",
        "label": label,
        "domain_id": domain_id,
        "representation_index": representation_index,
        "ancestry": list(ancestry or []),
        "trusted_source": source,
    }


def trusted_object_catalog(
    fixture: dict[str, Any], depth_packet: dict[str, Any]
) -> list[dict[str, Any]]:
    """Index committed semantic objects without minting learner-path semantics."""

    objects: dict[str, dict[str, Any]] = {}
    domains = {item["domain_id"]: item for item in fixture["domains"]}
    for domain in fixture["domains"]:
        domain_id = domain["domain_id"]
        orientation_index = 0
        orientation_identity = f"domain:{domain_id}"
        objects[_object_key("orientation", orientation_identity)] = {
            "object_key": _object_key("orientation", orientation_identity),
            "semantic_identity": None,
            "orientation_identity": orientation_identity,
            "kind": "orientation",
            "label": domain["label"],
            "domain_id": domain_id,
            "representation_index": orientation_index,
            "ancestry": [],
            "trusted_source": "workspace-fixture.json domains[]",
        }
        for representation_index, representation in enumerate(
            domain["learning_model"]["representations"]
        ):
            for node in representation["nodes"]:
                key = _object_key("concept", node["entity_id"])
                objects.setdefault(
                    key,
                    _concept(
                        identity=node["entity_id"],
                        label=node["label"],
                        domain_id=domain_id,
                        representation_index=representation_index,
                        source="workspace-fixture.json trusted representation node",
                    ),
                )

    for record in relationship_records(fixture):
        domain = domains[record["domain_id"]]
        matches = [
            index
            for index, representation in enumerate(
                domain["learning_model"]["representations"]
            )
            if any(
                record["identity"] in edge["relationship_ids"]
                for edge in representation["edges"]
            )
        ]
        if len(matches) != 1:
            raise ValidationError(
                f"relationship {record['identity']} lacks one trusted representation context"
            )
        labels = {
            node["entity_id"]: node["label"]
            for node in domain["learning_model"]["representations"][matches[0]]["nodes"]
        }
        objects[_object_key("canonical", record["identity"])] = {
            "object_key": _object_key("canonical", record["identity"]),
            "semantic_identity": record["identity"],
            "kind": "canonical",
            "label": (
                f"{labels[record['source_entity_id']]} → "
                f"{labels[record['target_entity_id']]}"
            ),
            "predicate": record["predicate"],
            "domain_id": record["domain_id"],
            "representation_index": matches[0],
            "ancestry": [],
            "trusted_source": "workspace-fixture.json canonical relationship",
        }

    for expansion in depth_packet["expansions"]:
        ancestry = [expansion["id"]]
        domain_id = "electromagnetism"
        representation_index = 2
        labels = {item["entity_id"]: item["label"] for item in expansion["concepts"]}
        for item in expansion["concepts"]:
            key = _object_key("concept", item["entity_id"])
            objects.setdefault(
                key,
                _concept(
                    identity=item["entity_id"],
                    label=item["label"],
                    domain_id=domain_id,
                    representation_index=representation_index,
                    ancestry=ancestry,
                    source="depth-map.json trusted concept",
                ),
            )
        for item in expansion["canonical_items"]:
            objects[_object_key("canonical", item["id"])] = {
                "object_key": _object_key("canonical", item["id"]),
                "semantic_identity": item["id"],
                "kind": "canonical",
                "label": (
                    f"{labels[item['source_entity_id']]} → "
                    f"{labels[item['target_entity_id']]}"
                ),
                "predicate": item["relationship_type"],
                "domain_id": domain_id,
                "representation_index": representation_index,
                "ancestry": ancestry,
                "trusted_source": "depth-map.json admitted canonical relationship",
            }
        for item in expansion["explanatory_items"]:
            objects[_object_key("explanation", item["id"])] = {
                "object_key": _object_key("explanation", item["id"]),
                "semantic_identity": item["id"],
                "kind": "explanation",
                "label": item["short_label"],
                "domain_id": domain_id,
                "representation_index": representation_index,
                "ancestry": ancestry,
                "trusted_source": "depth-map.json source-backed explanation",
            }
    return sorted(objects.values(), key=lambda item: item["object_key"])


def trusted_continuations(
    fixture: dict[str, Any], depth_packet: dict[str, Any]
) -> list[dict[str, Any]]:
    """Build non-generative continuation evidence from committed relationships."""

    links: list[dict[str, Any]] = []
    for record in relationship_records(fixture):
        links.append(
            {
                "source_object_key": _object_key(
                    "concept", record["source_entity_id"]
                ),
                "target_object_key": _object_key(
                    "concept", record["target_entity_id"]
                ),
                "relationship_object_key": _object_key(
                    "canonical", record["identity"]
                ),
                "basis": "CANONICAL_RELATIONSHIP",
                "basis_identity": record["identity"],
            }
        )
    for expansion in depth_packet["expansions"]:
        for item in expansion["canonical_items"]:
            links.append(
                {
                    "source_object_key": _object_key(
                        "concept", item["source_entity_id"]
                    ),
                    "target_object_key": _object_key(
                        "concept", item["target_entity_id"]
                    ),
                    "relationship_object_key": _object_key(
                        "canonical", item["id"]
                    ),
                    "basis": "CANONICAL_RELATIONSHIP",
                    "basis_identity": item["id"],
                }
            )
        for item in expansion["explanatory_items"]:
            for left, right in combinations(sorted(item["participant_entity_ids"]), 2):
                links.append(
                    {
                        "source_object_key": _object_key("concept", left),
                        "target_object_key": _object_key("concept", right),
                        "relationship_object_key": None,
                        "basis": "SHARED_SOURCE_EXPLANATION",
                        "basis_identity": item["id"],
                    }
                )
    return sorted(
        links,
        key=lambda item: (
            item["basis"],
            item["basis_identity"],
            item["source_object_key"],
            item["target_object_key"],
        ),
    )


def exploration_suggestions(
    current_object_key: str,
    *,
    catalog: list[dict[str, Any]],
    continuations: list[dict[str, Any]],
    visited_object_keys: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Rank trusted continuations by a fixed, inspectable offline rule."""

    by_key = {item["object_key"]: item for item in catalog}
    try:
        current = by_key[current_object_key]
    except KeyError as error:
        raise ValidationError(f"unknown current learning object: {current_object_key}") from error
    candidates: dict[str, dict[str, Any]] = {}

    def add(target_key: str, priority: int, basis: str, basis_identity: str) -> None:
        target = by_key.get(target_key)
        if target is None or target_key == current_object_key:
            return
        value = {
            "target_object_key": target_key,
            "target_semantic_identity": target["semantic_identity"],
            "target_kind": target["kind"],
            "target_label": target["label"],
            "basis": basis,
            "basis_identity": basis_identity,
            "priority": priority,
        }
        existing = candidates.get(target_key)
        if existing is None or (
            priority,
            basis_identity,
        ) < (existing["priority"], existing["basis_identity"]):
            candidates[target_key] = value

    if current["kind"] == "orientation":
        for item in catalog:
            if item["kind"] == "concept" and item["domain_id"] == current["domain_id"]:
                add(
                    item["object_key"],
                    30,
                    "DOMAIN_ENTRY",
                    current["orientation_identity"],
                )
    elif current["kind"] == "concept":
        for link in continuations:
            endpoints = (link["source_object_key"], link["target_object_key"])
            if current_object_key not in endpoints:
                continue
            other = endpoints[1] if endpoints[0] == current_object_key else endpoints[0]
            if link["basis"] == "CANONICAL_RELATIONSHIP":
                add(other, 10, link["basis"], link["basis_identity"])
                add(
                    link["relationship_object_key"],
                    30,
                    "CANONICAL_RELATIONSHIP_OBJECT",
                    link["basis_identity"],
                )
            else:
                add(other, 20, link["basis"], link["basis_identity"])
    elif current["kind"] == "canonical":
        for link in continuations:
            if link["relationship_object_key"] == current_object_key:
                add(
                    link["source_object_key"], 10, "CANONICAL_ENDPOINT", link["basis_identity"]
                )
                add(
                    link["target_object_key"], 10, "CANONICAL_ENDPOINT", link["basis_identity"]
                )
    elif current["kind"] == "explanation":
        for link in continuations:
            if (
                link["basis"] == "SHARED_SOURCE_EXPLANATION"
                and link["basis_identity"] == current["semantic_identity"]
            ):
                add(
                    link["source_object_key"],
                    10,
                    "SOURCE_EXPLANATION_PARTICIPANT",
                    link["basis_identity"],
                )
                add(
                    link["target_object_key"],
                    10,
                    "SOURCE_EXPLANATION_PARTICIPANT",
                    link["basis_identity"],
                )
    visited = visited_object_keys or set()
    return sorted(
        candidates.values(),
        key=lambda item: (
            item["target_object_key"] in visited,
            item["priority"],
            item["target_label"].casefold(),
            item["target_object_key"],
            item["basis_identity"],
        ),
    )


class TraversalHistory:
    """A learner path whose edges mean only that the learner travelled."""

    def __init__(self, root_object: dict[str, Any]):
        self._nodes: list[dict[str, Any]] = []
        self._current_node_id = self._append(root_object, None)

    def _append(self, learning_object: dict[str, Any], parent_id: str | None) -> str:
        node_id = f"path-{len(self._nodes) + 1:04d}"
        self._nodes.append(
            {
                "path_node_id": node_id,
                "object_key": learning_object["object_key"],
                "semantic_identity": learning_object["semantic_identity"],
                "kind": learning_object["kind"],
                "label": learning_object["label"],
                "domain_id": learning_object["domain_id"],
                "parent_path_node_id": parent_id,
                "created_index": len(self._nodes),
            }
        )
        return node_id

    @property
    def current_node_id(self) -> str:
        return self._current_node_id

    def travel(self, learning_object: dict[str, Any]) -> str:
        for node in self._nodes:
            if (
                node["parent_path_node_id"] == self._current_node_id
                and node["object_key"] == learning_object["object_key"]
            ):
                self._current_node_id = node["path_node_id"]
                return self._current_node_id
        self._current_node_id = self._append(learning_object, self._current_node_id)
        return self._current_node_id

    def activate(self, path_node_id: str) -> None:
        if not any(node["path_node_id"] == path_node_id for node in self._nodes):
            raise ValidationError(f"unknown traversal node: {path_node_id}")
        self._current_node_id = path_node_id

    def snapshot(self) -> dict[str, Any]:
        nodes = deepcopy(self._nodes)
        return {
            "current_path_node_id": self._current_node_id,
            "nodes": [
                {**node, "current": node["path_node_id"] == self._current_node_id}
                for node in nodes
            ],
            "edges": [
                {
                    "source_path_node_id": node["parent_path_node_id"],
                    "target_path_node_id": node["path_node_id"],
                    "semantics": "TRAVELLED",
                    "canonical_predicate": None,
                }
                for node in nodes
                if node["parent_path_node_id"] is not None
            ],
        }


def ten_step_branching_fixture() -> dict[str, Any]:
    objects = [
        {
            "object_key": f"concept:synthetic-{index}",
            "semantic_identity": f"synthetic-{index}",
            "kind": "concept",
            "label": f"Synthetic step {index}",
            "domain_id": "synthetic-test-only",
        }
        for index in range(12)
    ]
    history = TraversalHistory(objects[0])
    main_path = [history.current_node_id]
    for item in objects[1:11]:
        main_path.append(history.travel(item))
    history.activate(main_path[4])
    branch_id = history.travel(objects[11])
    history.activate(main_path[10])
    snapshot = history.snapshot()
    children_at_branch = [
        node
        for node in snapshot["nodes"]
        if node["parent_path_node_id"] == main_path[4]
    ]
    return {
        "status": "PASS"
        if len(main_path) == 11
        and len(children_at_branch) == 2
        and branch_id in {item["path_node_id"] for item in children_at_branch}
        and snapshot["current_path_node_id"] == main_path[10]
        and all(edge["semantics"] == "TRAVELLED" for edge in snapshot["edges"])
        and all(edge["canonical_predicate"] is None for edge in snapshot["edges"])
        else "FAIL",
        "fixture_only": True,
        "tested_traversal_steps": 10,
        "branch_parent": main_path[4],
        "main_leaf": main_path[10],
        "alternate_leaf": branch_id,
        "path_model": snapshot,
        "depth_is_path_rule_input": False,
        "new_product_semantics": [],
    }
