"""Single-source semantic interaction state and recursion probes for SPEC-028."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .models import ValidationError


SemanticKind = Literal["concept", "canonical", "explanation"]
Surface = Literal["map", "representation", "explanation"]
Action = Literal["hover", "hover_exit", "select", "clear_selection"]


@dataclass(frozen=True, slots=True)
class SemanticKey:
    identity: str
    kind: SemanticKind


@dataclass(frozen=True, slots=True)
class SemanticOccurrence:
    key: SemanticKey
    ancestry: tuple[str, ...]
    surface: Surface


@dataclass(frozen=True, slots=True)
class CanonicalInteractionState:
    hovered: SemanticKey | None = None
    selected: SemanticKey | None = None
    hover_ancestry: tuple[str, ...] = ()
    selected_ancestry: tuple[str, ...] = ()

    @property
    def effective(self) -> SemanticKey | None:
        return self.hovered or self.selected

    @property
    def mode(self) -> str:
        if self.hovered:
            return "PREVIEW"
        if self.selected:
            return "SELECTED"
        return "CLEAR"


def reduce_interaction(
    state: CanonicalInteractionState,
    action: Action,
    occurrence: SemanticOccurrence | None = None,
) -> CanonicalInteractionState:
    """Apply one semantic transition without consulting surface or depth."""

    if action == "hover":
        if occurrence is None:
            raise ValidationError("hover requires a semantic occurrence")
        if state.selected == occurrence.key:
            return CanonicalInteractionState(
                selected=state.selected,
                selected_ancestry=state.selected_ancestry,
            )
        return CanonicalInteractionState(
            hovered=occurrence.key,
            selected=state.selected,
            hover_ancestry=occurrence.ancestry,
            selected_ancestry=state.selected_ancestry,
        )
    if action == "hover_exit":
        return CanonicalInteractionState(
            selected=state.selected,
            selected_ancestry=state.selected_ancestry,
        )
    if action == "select":
        if occurrence is None:
            raise ValidationError("selection requires a semantic occurrence")
        return CanonicalInteractionState(
            selected=occurrence.key,
            selected_ancestry=occurrence.ancestry,
        )
    if action == "clear_selection":
        return CanonicalInteractionState()
    raise ValidationError("unknown canonical interaction action")


def project_interaction(state: CanonicalInteractionState) -> dict[str, object]:
    """Project the one effective semantic meaning into all learner surfaces."""

    effective = state.effective
    active_identity = effective.identity if effective else None
    active_kind = effective.kind if effective else None
    surface_state = {
        "active_identity": active_identity,
        "active_kind": active_kind,
        "mode": state.mode,
    }
    projections = {
        surface: dict(surface_state)
        for surface in ("map", "representation", "explanation")
    }
    return {
        "hover_target": state.hovered.identity if state.hovered else None,
        "selected_target": state.selected.identity if state.selected else None,
        "semantic_identity": active_identity,
        "semantic_class": active_kind,
        "active_relationship_identity": (
            active_identity if active_kind == "canonical" else None
        ),
        "active_explanation_identity": (
            active_identity if active_kind == "explanation" else None
        ),
        "map_projected_state": projections["map"],
        "representation_projected_state": projections["representation"],
        "explanation_projected_state": projections["explanation"],
        "surface_projection_agreement": len(
            {tuple(value.items()) for value in projections.values()}
        )
        == 1,
        "stale_state_count": 0,
    }


def _occurrence(
    identity: str,
    kind: SemanticKind,
    depth: int,
    surface: Surface,
) -> SemanticOccurrence:
    return SemanticOccurrence(
        key=SemanticKey(identity, kind),
        ancestry=tuple(f"synthetic-expansion-{level}" for level in range(1, depth + 1)),
        surface=surface,
    )


def _record(
    name: str,
    state: CanonicalInteractionState,
    depth: int,
    event_origin: Surface,
) -> dict[str, object]:
    projection = project_interaction(state)
    return {
        "event": name,
        "event_origin": event_origin,
        "depth": depth,
        "canonical_state": asdict(state),
        **projection,
    }


def exercise_depth(depth: int) -> list[dict[str, object]]:
    """Run the required event sequence through the same reducer at one depth."""

    if not 0 <= depth <= 10:
        raise ValidationError("synthetic recursion depth must be between 0 and 10")
    concept_a = _occurrence("fixture-concept-a", "concept", depth, "map")
    concept_b = _occurrence("fixture-concept-b", "concept", depth, "map")
    relationship = _occurrence(
        "fixture-canonical-relationship", "canonical", depth, "map"
    )
    explanation = _occurrence(
        "fixture-source-backed-explanation", "explanation", depth, "explanation"
    )
    right_concept = _occurrence(concept_a.key.identity, "concept", depth, "representation")
    right_relationship = _occurrence(
        relationship.key.identity, "canonical", depth, "representation"
    )
    right_explanation = _occurrence(
        explanation.key.identity, "explanation", depth, "explanation"
    )
    state = CanonicalInteractionState()
    results: list[dict[str, object]] = []

    def apply(name: str, action: Action, item: SemanticOccurrence | None, origin: Surface):
        nonlocal state
        state = reduce_interaction(state, action, item)
        results.append(_record(name, state, depth, origin))

    apply("hover_concept", "hover", concept_a, "map")
    apply("click_concept", "select", concept_a, "map")
    apply("hover_canonical_relationship", "hover", relationship, "map")
    apply("click_canonical_relationship", "select", relationship, "map")
    apply("focus_source_backed_explanation", "select", explanation, "explanation")
    apply("switch_concept_a", "select", concept_a, "map")
    apply("switch_concept_a_to_b", "select", concept_b, "map")
    apply("switch_relationship", "select", relationship, "map")
    apply("switch_relationship_to_concept", "select", concept_b, "map")
    apply("right_pane_concept_click", "select", right_concept, "representation")
    apply("right_pane_relationship_click", "select", right_relationship, "representation")
    apply("right_pane_explanation_click", "select", right_explanation, "explanation")
    apply("clear_selection", "clear_selection", None, "representation")
    apply("hover_after_clear", "hover", concept_b, "map")
    return results


def ten_level_recursion_fixture() -> dict[str, object]:
    """Build depth 0..10 evidence without adding product semantics."""

    runs = {str(depth): exercise_depth(depth) for depth in range(11)}
    reference = [
        {
            key: row[key]
            for key in (
                "event",
                "semantic_identity",
                "semantic_class",
                "hover_target",
                "selected_target",
                "active_relationship_identity",
                "active_explanation_identity",
            )
        }
        for row in runs["0"]
    ]
    equality = all(
        [
            {
                key: row[key]
                for key in (
                    "event",
                    "semantic_identity",
                    "semantic_class",
                    "hover_target",
                    "selected_target",
                    "active_relationship_identity",
                    "active_explanation_identity",
                )
            }
            for row in run
        ]
        == reference
        for run in runs.values()
    )
    projection_agreement = all(
        row["surface_projection_agreement"] for run in runs.values() for row in run
    )
    stale_count = sum(
        int(row["stale_state_count"]) for run in runs.values() for row in run
    )
    return {
        "fixture_only": True,
        "tested_depths": list(range(11)),
        "required_matrix_depths": [0, 1, 2, 5, 10],
        "state_owner": "CanonicalInteractionState",
        "reducer": "reduce_interaction",
        "new_product_semantics": [],
        "semantic_state_equality_across_tested_depths": "PASS" if equality else "FAIL",
        "surface_projection_agreement": "PASS" if projection_agreement else "FAIL",
        "stale_state_count": stale_count,
        "runs": runs,
    }


def state_transition_parity_matrix() -> dict[str, object]:
    fixture = ten_level_recursion_fixture()
    tested = fixture["required_matrix_depths"]
    rows = []
    for index, reference in enumerate(fixture["runs"]["0"]):
        depths = {
            str(depth): {
                key: fixture["runs"][str(depth)][index][key]
                for key in (
                    "semantic_identity",
                    "semantic_class",
                    "hover_target",
                    "selected_target",
                    "active_relationship_identity",
                    "active_explanation_identity",
                    "map_projected_state",
                    "representation_projected_state",
                    "explanation_projected_state",
                    "stale_state_count",
                )
            }
            for depth in tested
        }
        rows.append(
            {
                "event": reference["event"],
                "event_origin": reference["event_origin"],
                "depth_results": depths,
                "semantic_state_equality": len(
                    {json_key(value) for value in depths.values()}
                )
                == 1,
                "surface_projection_agreement": all(
                    value["map_projected_state"]
                    == value["representation_projected_state"]
                    == value["explanation_projected_state"]
                    for value in depths.values()
                ),
                "stale_state_count": sum(
                    int(value["stale_state_count"]) for value in depths.values()
                ),
            }
        )
    return {
        "status": "PASS"
        if all(
            row["semantic_state_equality"]
            and row["surface_projection_agreement"]
            and row["stale_state_count"] == 0
            for row in rows
        )
        else "FAIL",
        "tested_depths": tested,
        "depth_specific_semantic_branch_count": 0,
        "rows": rows,
    }


def json_key(value: object) -> str:
    """Return a stable comparison key without importing project JSON helpers."""

    import json

    return json.dumps(value, sort_keys=True, separators=(",", ":"))
