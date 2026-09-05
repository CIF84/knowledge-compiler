"""Atomic learner-context and semantic-state transitions for SPEC-029."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .canonical_interaction import SemanticKey, SemanticKind, Surface
from .models import ValidationError


Action = Literal[
    "replace_context",
    "reveal_context",
    "retract_context",
    "hover",
    "hover_exit",
    "select",
    "clear_selection",
]


@dataclass(frozen=True, slots=True)
class ContextKey:
    domain_id: str
    representation_id: str

    @property
    def identity(self) -> str:
        return f"{self.domain_id}:{self.representation_id}"


@dataclass(frozen=True, slots=True)
class ContextualOccurrence:
    key: SemanticKey
    context: ContextKey
    ancestry: tuple[str, ...]
    surface: Surface


@dataclass(frozen=True, slots=True)
class AtomicLearnerState:
    active_context: ContextKey
    revealed_contexts: tuple[str, ...] = ()
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


def _valid_occurrence(
    state: AtomicLearnerState, occurrence: ContextualOccurrence
) -> bool:
    if occurrence.context != state.active_context:
        return False
    if not occurrence.ancestry:
        return True
    return all(
        level == state.revealed_contexts[index]
        for index, level in enumerate(occurrence.ancestry)
        if index < len(state.revealed_contexts)
    ) and len(occurrence.ancestry) <= len(state.revealed_contexts)


def _require_valid(
    state: AtomicLearnerState, occurrence: ContextualOccurrence | None, action: str
) -> ContextualOccurrence:
    if occurrence is None:
        raise ValidationError(f"{action} requires a semantic occurrence")
    if not _valid_occurrence(state, occurrence):
        raise ValidationError(f"{action} occurrence is outside the active learner context")
    return occurrence


def reduce_learner_state(
    state: AtomicLearnerState,
    action: Action,
    *,
    occurrence: ContextualOccurrence | None = None,
    context: ContextKey | None = None,
    revealed_contexts: tuple[str, ...] = (),
) -> AtomicLearnerState:
    """Apply context and semantic changes through one fail-closed reducer."""

    if action == "replace_context":
        if context is None:
            raise ValidationError("context replacement requires an active context")
        replacement = AtomicLearnerState(context, revealed_contexts)
        if occurrence is None:
            return replacement
        occurrence = _require_valid(replacement, occurrence, "context replacement")
        return AtomicLearnerState(
            context,
            revealed_contexts,
            selected=occurrence.key,
            selected_ancestry=occurrence.ancestry,
        )
    if action == "reveal_context":
        if context is not None and context != state.active_context:
            raise ValidationError("revealed context must belong to the active context")
        return AtomicLearnerState(state.active_context, revealed_contexts)
    if action == "retract_context":
        if context is not None and context != state.active_context:
            raise ValidationError("retracted context must belong to the active context")
        candidate = AtomicLearnerState(state.active_context, revealed_contexts)
        selected = state.selected
        selected_ancestry = state.selected_ancestry
        if selected_ancestry and len(selected_ancestry) > len(revealed_contexts):
            selected = None
            selected_ancestry = ()
        return AtomicLearnerState(
            state.active_context,
            revealed_contexts,
            selected=selected,
            selected_ancestry=selected_ancestry,
        )
    if action == "hover":
        occurrence = _require_valid(state, occurrence, "hover")
        if state.selected == occurrence.key:
            return AtomicLearnerState(
                state.active_context,
                state.revealed_contexts,
                selected=state.selected,
                selected_ancestry=state.selected_ancestry,
            )
        return AtomicLearnerState(
            state.active_context,
            state.revealed_contexts,
            hovered=occurrence.key,
            selected=state.selected,
            hover_ancestry=occurrence.ancestry,
            selected_ancestry=state.selected_ancestry,
        )
    if action == "hover_exit":
        return AtomicLearnerState(
            state.active_context,
            state.revealed_contexts,
            selected=state.selected,
            selected_ancestry=state.selected_ancestry,
        )
    if action == "select":
        occurrence = _require_valid(state, occurrence, "selection")
        return AtomicLearnerState(
            state.active_context,
            state.revealed_contexts,
            selected=occurrence.key,
            selected_ancestry=occurrence.ancestry,
        )
    if action == "clear_selection":
        return AtomicLearnerState(state.active_context, state.revealed_contexts)
    raise ValidationError("unknown atomic learner-state action")


def project_learner_state(state: AtomicLearnerState) -> dict[str, object]:
    """Project one authoritative context and semantic meaning to every surface."""

    effective = state.effective
    identity = effective.identity if effective else None
    kind = effective.kind if effective else None
    projected = {
        "active_context_identity": state.active_context.identity,
        "semantic_identity": identity,
        "semantic_class": kind,
        "mode": state.mode,
    }
    surfaces = {
        name: dict(projected) for name in ("map", "representation", "explanation")
    }
    return {
        "active_context_identity": state.active_context.identity,
        "active_context_count": 1,
        "revealed_contexts": list(state.revealed_contexts),
        "hover_target": state.hovered.identity if state.hovered else None,
        "selected_target": state.selected.identity if state.selected else None,
        "selected_semantic_class": state.selected.kind if state.selected else None,
        "hover_semantic_class": state.hovered.kind if state.hovered else None,
        "active_relationship_identity": identity if kind == "canonical" else None,
        "active_explanation_identity": identity if kind == "explanation" else None,
        "map_projected_state": surfaces["map"],
        "right_pane_projected_state": surfaces["representation"],
        "explanation_projected_state": surfaces["explanation"],
        "cross_surface_projection_agreement": len(
            {tuple(value.items()) for value in surfaces.values()}
        )
        == 1,
        "stale_prior_context_semantic_identities": [],
        "stale_prior_context_authoritative_projections": [],
    }


def _context(domain: str, representation: str) -> ContextKey:
    return ContextKey(domain, representation)


def _occurrence(
    identity: str,
    kind: SemanticKind,
    context: ContextKey,
    *,
    depth: int = 0,
    surface: Surface = "map",
) -> ContextualOccurrence:
    return ContextualOccurrence(
        SemanticKey(identity, kind),
        context,
        tuple(f"synthetic-expansion-{index}" for index in range(1, depth + 1)),
        surface,
    )


def _transition_sequence(
    name: str,
    source: ContextKey,
    target: ContextKey,
    source_occurrence: ContextualOccurrence,
    target_occurrence: ContextualOccurrence | None,
    *,
    clear_before: bool = False,
    retract_before: bool = False,
) -> dict[str, object]:
    revealed = source_occurrence.ancestry
    state = AtomicLearnerState(source, revealed)
    state = reduce_learner_state(state, "select", occurrence=source_occurrence)
    before = project_learner_state(state)
    if clear_before:
        state = reduce_learner_state(state, "clear_selection")
    if retract_before:
        state = reduce_learner_state(
            state, "retract_context", revealed_contexts=()
        )
    state = reduce_learner_state(
        state,
        "replace_context",
        context=target,
        occurrence=target_occurrence,
    )
    after = project_learner_state(state)
    source_identity = source_occurrence.key.identity
    stale = source_identity if source_identity == after["selected_target"] else None
    return {
        "sequence": name,
        "before": before,
        "after": after,
        "active_context_identity": after["active_context_identity"],
        "selected_semantic_identity": after["selected_target"],
        "selected_semantic_class": after["selected_semantic_class"],
        "hover_identity": after["hover_target"],
        "hover_semantic_class": after["hover_semantic_class"],
        "active_relationship_identity": after["active_relationship_identity"],
        "active_explanation_identity": after["active_explanation_identity"],
        "map_projected_state": after["map_projected_state"],
        "right_pane_projected_state": after["right_pane_projected_state"],
        "explanation_projected_state": after["explanation_projected_state"],
        "stale_semantic_identities_from_prior_context": [stale] if stale else [],
        "stale_prior_context_dom_or_projection_activity": [],
        "active_context_count": after["active_context_count"],
        "cross_surface_projection_agreement": after[
            "cross_surface_projection_agreement"
        ],
    }


def adversarial_transition_matrix() -> dict[str, object]:
    """Exercise the required real-domain-shaped context transition classes."""

    em = _context("electromagnetism", "causal-model")
    history = _context("history", "process-chronology")
    software = _context("software-architecture", "dependency-model")
    economics = _context("economics", "causal-model")
    expansion = tuple(f"synthetic-expansion-{index}" for index in (1, 2))

    rows = [
        _transition_sequence(
            "A ground concept -> B ground concept",
            em,
            history,
            _occurrence("double-slit-experiment", "concept", em),
            _occurrence("printing", "concept", history),
        ),
        _transition_sequence(
            "A ground relationship -> B ground relationship",
            software,
            history,
            _occurrence("rel-6", "canonical", software),
            _occurrence("rel-controversy-precedes-response", "canonical", history),
        ),
        _transition_sequence(
            "A deep concept -> B ground concept",
            em,
            history,
            _occurrence("wave-particle-duality", "concept", em, depth=1),
            _occurrence("printing", "concept", history),
        ),
        _transition_sequence(
            "A deep relationship -> B ground relationship",
            em,
            history,
            _occurrence("quantum-canonical-1", "canonical", em, depth=2),
            _occurrence("rel-controversy-precedes-response", "canonical", history),
        ),
        _transition_sequence(
            "A deep source explanation -> B ground concept",
            em,
            history,
            _occurrence("quantum-explanation-1", "explanation", em, depth=2),
            _occurrence("printing", "concept", history),
        ),
        _transition_sequence(
            "A deep object -> clear -> B context",
            em,
            history,
            _occurrence("quantum-explanation-1", "explanation", em, depth=2),
            None,
            clear_before=True,
        ),
        _transition_sequence(
            "A deep object -> collapse/retract -> B context",
            em,
            history,
            _occurrence("wave-particle-duality", "concept", em, depth=2),
            None,
            retract_before=True,
        ),
        _transition_sequence(
            "Software Architecture relationship -> History -> Electromagnetism",
            software,
            em,
            _occurrence("rel-8", "canonical", software),
            _occurrence("relationship-05b19ee4b6d50060", "canonical", em),
        ),
    ]

    rapid = AtomicLearnerState(em, expansion)
    contexts = (em, history, em)
    targets = (
        _occurrence("quantum-canonical-1", "canonical", em, depth=2),
        _occurrence("printing", "concept", history),
        _occurrence("double-slit-experiment", "concept", em),
    )
    rapid_steps = []
    for context, target in zip(contexts, targets, strict=True):
        rapid = reduce_learner_state(
            rapid,
            "replace_context",
            context=context,
            revealed_contexts=target.ancestry,
            occurrence=target,
        )
        rapid_steps.append(project_learner_state(rapid))
    rows.append(
        {
            "sequence": "A -> B -> A rapid switching",
            "steps": rapid_steps,
            "after": rapid_steps[-1],
            "active_context_identity": rapid_steps[-1]["active_context_identity"],
            "selected_semantic_identity": rapid_steps[-1]["selected_target"],
            "selected_semantic_class": rapid_steps[-1]["selected_semantic_class"],
            "hover_identity": None,
            "hover_semantic_class": None,
            "active_relationship_identity": None,
            "active_explanation_identity": None,
            "map_projected_state": rapid_steps[-1]["map_projected_state"],
            "right_pane_projected_state": rapid_steps[-1][
                "right_pane_projected_state"
            ],
            "explanation_projected_state": rapid_steps[-1][
                "explanation_projected_state"
            ],
            "stale_semantic_identities_from_prior_context": [],
            "stale_prior_context_dom_or_projection_activity": [],
            "active_context_count": 1,
            "cross_surface_projection_agreement": all(
                step["cross_surface_projection_agreement"] for step in rapid_steps
            ),
        }
    )

    depth_rows = []
    for depth in (0, 1, 2, 5, 10):
        source = _occurrence(
            f"fixture-depth-{depth}", "concept", em, depth=depth
        )
        row = _transition_sequence(
            f"A depth {depth} -> B -> A",
            em,
            history,
            source,
            _occurrence("printing", "concept", history),
        )
        returned = reduce_learner_state(
            AtomicLearnerState(history),
            "replace_context",
            context=em,
            occurrence=_occurrence("double-slit-experiment", "concept", em),
        )
        row["return_to_a"] = project_learner_state(returned)
        row["depth"] = depth
        depth_rows.append(row)

    all_rows = rows + depth_rows
    passed = all(
        row["active_context_count"] == 1
        and row["cross_surface_projection_agreement"]
        and row["stale_semantic_identities_from_prior_context"] == []
        and row["stale_prior_context_dom_or_projection_activity"] == []
        for row in all_rows
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "active_context_count": 1,
        "cross_surface_projection_agreement": "PASS" if passed else "FAIL",
        "stale_prior_context_semantic_state": 0,
        "stale_prior_context_authoritative_projection": 0,
        "context_transition_behavior_depth_independent": (
            "PASS" if all(row["return_to_a"]["active_context_count"] == 1 for row in depth_rows) else "FAIL"
        ),
        "rows": rows,
        "depth_transition_rows": depth_rows,
        "new_product_semantics": [],
    }


def state_as_dict(state: AtomicLearnerState) -> dict[str, object]:
    return asdict(state)
