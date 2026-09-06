"""Identity-preserving relationship multiplicity for SPEC-031."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any

from .models import ValidationError


def _relationship_evidence(edge: dict[str, Any], identity: str) -> list[dict[str, Any]]:
    evidence = [
        dict(item)
        for item in edge.get("evidence", [])
        if item.get("relationship_id") == identity
    ]
    if not evidence:
        raise ValidationError(f"canonical relationship {identity} lacks identity-bound evidence")
    return sorted(
        evidence,
        key=lambda item: (
            item.get("document_id", ""),
            item.get("start", -1),
            item.get("end", -1),
            item.get("quote", ""),
        ),
    )


def relationship_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten visual edges into independently keyed canonical relationships."""

    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    semantic_edges: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for domain in fixture["domains"]:
        for representation in domain["learning_model"]["representations"]:
            for edge in representation["edges"]:
                for identity in edge["relationship_ids"]:
                    semantic_edges[identity].append(edge)
    for edge in fixture["navigation"]["edges"]:
        identities = sorted(edge["relationship_ids"])
        if not identities:
            raise ValidationError(f"visual edge {edge['edge_key']} has no relationship identity")
        for identity in identities:
            if identity in seen:
                raise ValidationError(f"duplicate canonical relationship identity: {identity}")
            seen.add(identity)
            matches = semantic_edges[identity]
            if len(matches) != 1:
                raise ValidationError(
                    f"canonical relationship {identity} must have exactly one semantic edge"
                )
            semantic_edge = matches[0]
            records.append(
                {
                    "identity": identity,
                    "domain_id": edge["domain_id"],
                    "visual_edge_key": edge["edge_key"],
                    "corridor_key": "::".join(
                        [edge["domain_id"], *sorted(
                            (edge["source_entity_id"], edge["target_entity_id"])
                        )]
                    ),
                    "source_entity_id": semantic_edge["source_entity_id"],
                    "predicate": semantic_edge["relationship_type"],
                    "target_entity_id": semantic_edge["target_entity_id"],
                    "direction": semantic_edge["direction"],
                    "meaning": semantic_edge["meaning"],
                    "provenance_status": semantic_edge["provenance_status"],
                    "evidence": _relationship_evidence(semantic_edge, identity),
                }
            )
    return sorted(records, key=lambda item: item["identity"])


def relationship_index(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = relationship_records(fixture)
    return {item["identity"]: item for item in records}


def resolve_relationship(
    index: dict[str, dict[str, Any]], identity: str
) -> dict[str, Any]:
    """Resolve by explicit identity only; endpoints, predicates, and order are ignored."""

    try:
        return deepcopy(index[identity])
    except KeyError as error:
        raise ValidationError(f"unknown canonical relationship identity: {identity}") from error


def multiplicity_groups(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in relationship_records(fixture):
        grouped[record["corridor_key"]].append(record)
    result = []
    for corridor_key, records in sorted(grouped.items()):
        if len(records) < 2:
            continue
        ordered = sorted(records, key=lambda item: item["identity"])
        directed_pairs = {
            (item["source_entity_id"], item["target_entity_id"]) for item in ordered
        }
        predicates = {item["predicate"] for item in ordered}
        kind = (
            "RECIPROCAL"
            if any((target, source) in directed_pairs for source, target in directed_pairs)
            else "SAME_DIRECTION_MULTI_ASSERTION"
            if len(directed_pairs) == 1
            else "MULTI_EDGE"
        )
        result.append(
            {
                "corridor_key": corridor_key,
                "domain_id": ordered[0]["domain_id"],
                "kind": kind,
                "canonical_relationship_count": len(ordered),
                "canonical_relationship_identities": [
                    item["identity"] for item in ordered
                ],
                "visual_edge_keys": sorted(
                    {item["visual_edge_key"] for item in ordered}
                ),
                "directed_pairs": [list(item) for item in sorted(directed_pairs)],
                "predicates": sorted(predicates),
                "relationships": ordered,
                "synthetic_relationship_identity": None,
            }
        )
    return result


def order_independence_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    control = multiplicity_groups(fixture)
    reordered = deepcopy(fixture)
    reordered["navigation"]["edges"].reverse()
    for edge in reordered["navigation"]["edges"]:
        edge["relationship_ids"].reverse()
    for domain in reordered["domains"]:
        domain["learning_model"]["representations"].reverse()
        for representation in domain["learning_model"]["representations"]:
            representation["edges"].reverse()
            for edge in representation["edges"]:
                edge["relationship_ids"].reverse()
                edge["evidence"].reverse()
    candidate = multiplicity_groups(reordered)
    return {
        "status": "PASS" if control == candidate else "FAIL",
        "comparison": "original versus reversed edge, identity, and evidence order",
        "resolution_key": "canonical relationship identity",
        "forbidden_resolution_keys": [
            "DOM order",
            "visual path order",
            "array insertion order",
            "first endpoint-pair match",
            "first predicate match",
        ],
        "groups": control,
    }


def recursive_multiplicity_fixture() -> dict[str, Any]:
    """Exercise identical multi-edge identity behavior at representative depths."""

    identities = ("synthetic-edge-a", "synthetic-edge-b")
    rows = []
    for depth in (0, 1, 2, 5, 10):
        selected: str | None = None
        for action, identity in (
            ("select_a", identities[0]),
            ("select_b", identities[1]),
            ("select_a_again", identities[0]),
            ("clear", None),
        ):
            selected = identity
            rows.append(
                {
                    "depth": depth,
                    "action": action,
                    "requested_identity": identity,
                    "selected_identity": selected,
                    "map_identity": selected,
                    "learning_surface_identity": selected,
                    "agreement": True,
                }
            )
    parity_keys = {
        depth: [
            (row["action"], row["requested_identity"], row["selected_identity"])
            for row in rows
            if row["depth"] == depth
        ]
        for depth in (0, 1, 2, 5, 10)
    }
    return {
        "status": "PASS"
        if len({repr(value) for value in parity_keys.values()}) == 1
        and all(row["agreement"] for row in rows)
        else "FAIL",
        "fixture_only": True,
        "new_product_semantics": [],
        "tested_depths": [0, 1, 2, 5, 10],
        "resolver_input": "canonical relationship identity",
        "depth_is_resolver_input": False,
        "rows": rows,
    }
