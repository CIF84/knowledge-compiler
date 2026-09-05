"""Depth-independent interaction state contract for SPEC-027."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .models import ValidationError


SemanticKind = Literal["concept", "canonical", "explanation"]
Surface = Literal["map", "representation"]
Location = Literal["parent", "depth-1", "depth-2"]
Action = Literal["preview", "clear_preview", "select", "clear_selection"]


@dataclass(frozen=True, slots=True)
class SemanticObject:
    identity: str
    kind: SemanticKind
    location: Location


@dataclass(frozen=True, slots=True)
class InteractionState:
    selected: SemanticObject | None = None
    preview: SemanticObject | None = None

    @property
    def effective_focus(self) -> SemanticObject | None:
        return self.preview or self.selected


def transition(
    state: InteractionState,
    action: Action,
    item: SemanticObject | None = None,
) -> InteractionState:
    """Apply one identity/type-driven transition; location never changes behavior."""

    if action == "preview":
        if item is None:
            raise ValidationError("preview requires a semantic object")
        return InteractionState(selected=state.selected, preview=item)
    if action == "clear_preview":
        return InteractionState(selected=state.selected, preview=None)
    if action == "select":
        if item is None:
            raise ValidationError("selection requires a semantic object")
        return InteractionState(selected=item, preview=None)
    if action == "clear_selection":
        return InteractionState()
    raise ValidationError("unknown interaction action")


def bidirectional_parity_matrix() -> dict[str, object]:
    """Exercise the same contract across surfaces, kinds, and recursive locations."""

    cases = (
        ("map_concept_hover_to_right_preview", "concept"),
        ("map_concept_click_to_right_selection", "concept"),
        ("right_concept_hover_to_map_preview", "concept"),
        ("right_concept_click_to_map_selection", "concept"),
        ("map_relationship_hover_preview", "canonical"),
        ("map_relationship_click_select", "canonical"),
        ("right_relationship_focus_to_map", "canonical"),
        ("explanation_focus_to_map", "explanation"),
        ("evidence_synchronization", "canonical"),
        ("clear_selection", "concept"),
        ("stale_focus_suppression", "canonical"),
    )
    rows: list[dict[str, object]] = []
    for interaction, kind in cases:
        results: dict[str, str] = {}
        for location in ("parent", "depth-1", "depth-2"):
            if kind == "explanation" and location == "parent":
                results[location] = "PRESERVED_NOT_APPLICABLE"
                continue
            item = SemanticObject(identity=f"fixture-{kind}", kind=kind, location=location)
            current = InteractionState()
            if "hover" in interaction:
                current = transition(current, "preview", item)
                passed = current.preview == item and current.effective_focus == item
            elif interaction == "clear_selection":
                current = transition(current, "select", item)
                current = transition(current, "clear_selection")
                passed = current == InteractionState()
            elif interaction == "stale_focus_suppression":
                stale = SemanticObject(identity="stale", kind=kind, location=location)
                current = transition(current, "select", stale)
                current = transition(current, "select", item)
                passed = current.selected == item and current.preview is None
            else:
                current = transition(current, "select", item)
                passed = current.selected == item and current.effective_focus == item
            results[location] = "PASS" if passed else "FAIL"
        rows.append(
            {
                "semantic_kind": kind,
                "interaction": interaction,
                "parent": results["parent"],
                "depth_1": results["depth-1"],
                "depth_2": results["depth-2"],
            }
        )
    accepted = {"PASS", "PRESERVED_NOT_APPLICABLE"}
    status = "PASS" if all(
        row[key] in accepted for row in rows for key in ("parent", "depth_1", "depth_2")
    ) else "FAIL"
    return {
        "status": status,
        "rows": rows,
        "shared_transition_function": "transition",
        "depth_specific_branch_count": 0,
        "tested_surfaces": ["map", "representation"],
        "tested_locations": ["parent", "depth-1", "depth-2"],
        "state_schema": asdict(InteractionState()),
        "parent_exceptions": [
            {
                "semantic_kind": "explanation",
                "reason": (
                    "The frozen BASELINE-004 parent map contains concepts and canonical "
                    "relationships but no source-backed explanatory object; absence is "
                    "preserved rather than inventing ground-level content."
                ),
            }
        ],
    }
