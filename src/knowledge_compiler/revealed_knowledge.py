"""Canonical revealed-knowledge state for the SPEC-033 navigation projection."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import ValidationError


def canonical_projection(
    catalog: list[dict[str, Any]], depth_packet: dict[str, Any]
) -> list[dict[str, Any]]:
    """Assign every trusted object one stable navigation parent.

    Projection parents are navigation grouping, never newly asserted semantic edges.
    Parent-resolution concepts and claims are grouped under their domain root. Objects
    admitted by a depth expansion are grouped under that expansion's canonical entrance.
    """

    by_key = {item["object_key"]: item for item in catalog}
    if len(by_key) != len(catalog):
        raise ValidationError("canonical projection requires unique trusted object keys")
    depth_parent: dict[str, tuple[str, str]] = {}
    for expansion in depth_packet["expansions"]:
        focus = next((item for item in expansion["concepts"] if item["is_focus"]), None)
        if focus is None:
            raise ValidationError(f"depth expansion {expansion['id']} has no focus entrance")
        parent = f"concept:{focus['entity_id']}"
        for item in expansion["concepts"]:
            key = f"concept:{item['entity_id']}"
            if key != parent and by_key.get(key, {}).get("ancestry"):
                depth_parent[key] = (parent, expansion["id"])
        for kind, items in (
            ("canonical", expansion["canonical_items"]),
            ("explanation", expansion["explanatory_items"]),
        ):
            for item in items:
                depth_parent[f"{kind}:{item['id']}"] = (parent, expansion["id"])

    projected: list[dict[str, Any]] = []
    for order, item in enumerate(catalog):
        value = deepcopy(item)
        if item["kind"] == "orientation":
            parent = None
            basis = "CANONICAL_DOMAIN_ROOT"
        elif item["object_key"] in depth_parent:
            parent, expansion_id = depth_parent[item["object_key"]]
            basis = f"ADMITTED_DEPTH_GROUP:{expansion_id}"
        else:
            parent = f"orientation:domain:{item['domain_id']}"
            basis = "DOMAIN_MEMBERSHIP_GROUP"
        if parent is not None and parent not in by_key:
            raise ValidationError(
                f"projection parent {parent} is absent for {item['object_key']}"
            )
        value.update(
            {
                "parent_object_key": parent,
                "projection_basis": basis,
                "projection_order": order,
            }
        )
        projected.append(value)
    return projected


class RevealedKnowledgeState:
    """Deduplicated revealed territory, independent of visit-history topology."""

    def __init__(self, projection: list[dict[str, Any]], initial_object_key: str):
        self._projection = {item["object_key"]: deepcopy(item) for item in projection}
        if len(self._projection) != len(projection):
            raise ValidationError("revealed state requires unique canonical identities")
        self._revealed: dict[str, dict[str, Any]] = {}
        self._expanded: set[str] = set()
        self._selected: str | None = None
        self._event_index = 0
        self.reveal(initial_object_key, revealed_from=None)
        self.select(initial_object_key)

    def _require(self, object_key: str) -> dict[str, Any]:
        try:
            return self._projection[object_key]
        except KeyError as error:
            raise ValidationError(f"unknown canonical navigation object: {object_key}") from error

    def _ancestor_chain(self, object_key: str) -> list[str]:
        chain: list[str] = []
        cursor: str | None = object_key
        seen: set[str] = set()
        while cursor is not None:
            if cursor in seen:
                raise ValidationError(f"canonical projection contains a cycle at {cursor}")
            seen.add(cursor)
            chain.append(cursor)
            cursor = self._require(cursor)["parent_object_key"]
        return list(reversed(chain))

    def reveal(self, object_key: str, *, revealed_from: str | None) -> list[str]:
        """Reveal one canonical object and any required stable projection ancestors."""

        chain = self._ancestor_chain(object_key)
        added: list[str] = []
        for key in chain:
            if key in self._revealed:
                continue
            self._event_index += 1
            item = self._require(key)
            self._revealed[key] = {
                "object_key": key,
                "first_revealed_index": self._event_index,
                "revealed_from": revealed_from if key == object_key else object_key,
                "visit_count": 0,
            }
            added.append(key)
            parent = item["parent_object_key"]
            if parent is not None:
                self._expanded.add(parent)
        return added

    def reveal_many(self, object_keys: list[str], *, revealed_from: str) -> list[str]:
        added: list[str] = []
        for key in object_keys:
            added.extend(self.reveal(key, revealed_from=revealed_from))
        return added

    def select(self, object_key: str) -> None:
        self.reveal(object_key, revealed_from=self._selected)
        self._event_index += 1
        self._selected = object_key
        self._revealed[object_key]["visit_count"] += 1
        self._revealed[object_key]["last_visited_index"] = self._event_index
        for ancestor in self._ancestor_chain(object_key)[:-1]:
            self._expanded.add(ancestor)

    def set_expanded(self, object_key: str, expanded: bool) -> None:
        self._require(object_key)
        if object_key not in self._revealed:
            raise ValidationError(f"cannot collapse unrevealed object: {object_key}")
        if expanded:
            self._expanded.add(object_key)
        else:
            self._expanded.discard(object_key)

    def visible_object_keys(self) -> list[str]:
        visible: list[str] = []
        for item in sorted(
            self._projection.values(), key=lambda value: value["projection_order"]
        ):
            key = item["object_key"]
            if key not in self._revealed:
                continue
            ancestors = self._ancestor_chain(key)[:-1]
            if all(ancestor in self._expanded for ancestor in ancestors):
                visible.append(key)
        return visible

    def snapshot(self) -> dict[str, Any]:
        nodes = []
        for item in sorted(
            self._projection.values(), key=lambda value: value["projection_order"]
        ):
            key = item["object_key"]
            if key not in self._revealed:
                continue
            telemetry = self._revealed[key]
            nodes.append(
                {
                    "object_key": key,
                    "semantic_identity": item["semantic_identity"],
                    "kind": item["kind"],
                    "label": item["label"],
                    "domain_id": item["domain_id"],
                    "parent_object_key": item["parent_object_key"],
                    "projection_basis": item["projection_basis"],
                    "expanded": key in self._expanded,
                    "selected": key == self._selected,
                    "telemetry": deepcopy(telemetry),
                }
            )
        return {
            "selected_object_key": self._selected,
            "revealed_object_count": len(nodes),
            "revealed_object_keys": [item["object_key"] for item in nodes],
            "visible_object_keys": self.visible_object_keys(),
            "nodes": nodes,
            "navigation_edge_semantics": "PROJECTION_GROUPING_ONLY",
            "history_structurally_defines_navigation": False,
        }


def large_revealed_tree_fixture() -> dict[str, Any]:
    """Return a 60-object synthetic layout fixture with several deep branches."""

    projection: list[dict[str, Any]] = []
    order = 0
    roots: list[str] = []
    for root_index in range(4):
        root = f"orientation:synthetic-root-{root_index + 1}"
        roots.append(root)
        projection.append(
            {
                "object_key": root,
                "semantic_identity": None,
                "kind": "orientation",
                "label": f"Synthetic region {root_index + 1}",
                "domain_id": f"synthetic-{root_index + 1}",
                "parent_object_key": None,
                "projection_basis": "SYNTHETIC_LAYOUT_ROOT",
                "projection_order": order,
            }
        )
        order += 1
        for branch_index in range(2):
            parent = root
            for depth in range(1, 8):
                key = f"concept:synthetic-{root_index + 1}-{branch_index + 1}-{depth}"
                projection.append(
                    {
                        "object_key": key,
                        "semantic_identity": key.removeprefix("concept:"),
                        "kind": "concept",
                        "label": (
                            f"Readable synthetic concept {root_index + 1}."
                            f"{branch_index + 1}.{depth} with a deliberately descriptive label"
                        ),
                        "domain_id": f"synthetic-{root_index + 1}",
                        "parent_object_key": parent,
                        "projection_basis": "SYNTHETIC_LAYOUT_BRANCH",
                        "projection_order": order,
                    }
                )
                order += 1
                parent = key
    state = RevealedKnowledgeState(projection, roots[0])
    state.reveal_many(
        [item["object_key"] for item in projection], revealed_from="SYNTHETIC_FIXTURE"
    )
    deepest = projection[-1]["object_key"]
    state.select(deepest)
    expanded_snapshot = state.snapshot()
    state.set_expanded(roots[0], False)
    collapsed_snapshot = state.snapshot()
    return {
        "status": "PASS"
        if len(projection) == 60
        and expanded_snapshot["revealed_object_count"] == 60
        and len(expanded_snapshot["visible_object_keys"]) == 60
        and len(collapsed_snapshot["visible_object_keys"]) < 50
        and deepest in expanded_snapshot["visible_object_keys"]
        else "FAIL",
        "fixture_only": True,
        "object_count": len(projection),
        "max_depth": 7,
        "root_count": len(roots),
        "projection": projection,
        "expanded_snapshot": expanded_snapshot,
        "collapsed_snapshot": collapsed_snapshot,
    }
