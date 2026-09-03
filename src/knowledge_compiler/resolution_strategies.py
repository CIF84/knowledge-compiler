"""Provider-independent semantic-resolution strategies for SPEC-009."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .models import ValidationError


class ResolutionStrategyId(StrEnum):
    GENERIC_DETAIL = "GENERIC_DETAIL"
    PROCESS_STAGES = "PROCESS_STAGES"
    VARIABLE_CAUSAL_NEIGHBORHOOD = "VARIABLE_CAUSAL_NEIGHBORHOOD"
    COMPONENT_INTERNALS = "COMPONENT_INTERNALS"


@dataclass(frozen=True, slots=True)
class ResolutionStrategy:
    id: ResolutionStrategyId
    semantic_role: str
    objective: str
    seek: tuple[str, ...]
    avoid: tuple[str, ...]

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "id", ResolutionStrategyId(self.id))
        except (TypeError, ValueError) as exc:
            raise ValidationError("resolution strategy id is invalid") from exc
        if not isinstance(self.semantic_role, str) or not self.semantic_role.strip():
            raise ValidationError("resolution strategy semantic_role must be non-empty")
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValidationError("resolution strategy objective must be non-empty")
        seek = tuple(self.seek)
        avoid = tuple(self.avoid)
        if not seek or any(not isinstance(item, str) or not item.strip() for item in seek):
            raise ValidationError("resolution strategy seek must contain non-empty guidance")
        if not avoid or any(not isinstance(item, str) or not item.strip() for item in avoid):
            raise ValidationError("resolution strategy avoid must contain non-empty guidance")
        object.__setattr__(self, "seek", seek)
        object.__setattr__(self, "avoid", avoid)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id.value,
            "semantic_role": self.semantic_role,
            "objective": self.objective,
            "seek": list(self.seek),
            "avoid": list(self.avoid),
        }


RESOLUTION_STRATEGIES = (
    ResolutionStrategy(
        id=ResolutionStrategyId.GENERIC_DETAIL,
        semantic_role="GENERIC_CONTROL",
        objective=(
            "Produce a local explanatory model centered on the selected concept that exposes "
            "lower-level detail not visible in its parent representation."
        ),
        seek=(
            "supported steps, components, variables, interactions, or mechanisms",
            "meaningful typed relationships that plausibly compress back into the parent concept",
        ),
        avoid=(
            "merely repeating a subset of the parent graph",
            "paraphrasing the selected node or importing detail from general knowledge",
        ),
    ),
    ResolutionStrategy(
        id=ResolutionStrategyId.PROCESS_STAGES,
        semantic_role="PROCESS",
        objective=(
            "Explain the selected process at finer resolution through its source-supported "
            "internal stages and handoffs."
        ),
        seek=(
            "ordered stages and transitions",
            "prerequisites or dependencies between stages",
            "outputs and handoffs produced during the process",
        ),
        avoid=(
            "forcing PRECEDES when chronology is not explicit in the source",
            "turning surrounding causes or consequences into invented internal stages",
        ),
    ),
    ResolutionStrategy(
        id=ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD,
        semantic_role="VARIABLE",
        objective=(
            "Explain the selected variable at finer resolution through its source-supported "
            "causal neighborhood."
        ),
        seek=(
            "upstream drivers, constraints, or pressures",
            "downstream consequences or responses",
            "mechanisms connecting those influences and effects",
        ),
        avoid=(
            "closing a causal or feedback loop that the source does not support",
            "treating correlation, chronology, or interaction as causation",
        ),
    ),
    ResolutionStrategy(
        id=ResolutionStrategyId.COMPONENT_INTERNALS,
        semantic_role="COMPONENT_OR_SYSTEM",
        objective=(
            "Explain the selected component or system at finer resolution through its "
            "source-supported internals and their interactions."
        ),
        seek=(
            "internal parts or responsibilities",
            "interactions, interfaces, or handoffs among internals",
            "dependencies and supported containment relationships",
        ),
        avoid=(
            "inventing internal parts from general architectural convention",
            "using PART_OF unless the source supports containment",
        ),
    ),
)


def strategy_registry() -> dict[ResolutionStrategyId, ResolutionStrategy]:
    registry: dict[ResolutionStrategyId, ResolutionStrategy] = {}
    for strategy in RESOLUTION_STRATEGIES:
        if strategy.id in registry:
            raise ValidationError(f"duplicate resolution strategy: {strategy.id.value}")
        registry[strategy.id] = strategy
    missing = set(ResolutionStrategyId) - set(registry)
    extra = set(registry) - set(ResolutionStrategyId)
    if missing or extra:
        raise ValidationError(
            "resolution strategy registry does not match active strategy IDs; "
            f"missing={sorted(item.value for item in missing)}, "
            f"extra={sorted(item.value for item in extra)}"
        )
    return registry


RESOLUTION_STRATEGY_REGISTRY = strategy_registry()


def get_resolution_strategy(
    strategy_id: ResolutionStrategyId | str,
) -> ResolutionStrategy:
    try:
        return RESOLUTION_STRATEGY_REGISTRY[ResolutionStrategyId(strategy_id)]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError("resolution strategy is unsupported") from exc


def render_resolution_strategy(strategy: ResolutionStrategy) -> str:
    """Render only canonical strategy semantics for provider prompt consumption."""
    seek = "\n".join(f"- {item}" for item in strategy.seek)
    avoid = "\n".join(f"- {item}" for item in strategy.avoid)
    return (
        f"RESOLUTION STRATEGY: {strategy.id.value}\n"
        f"SEMANTIC ROLE: {strategy.semantic_role}\n"
        f"OBJECTIVE: {strategy.objective}\n"
        f"SEEK:\n{seek}\n"
        f"AVOID:\n{avoid}"
    )
