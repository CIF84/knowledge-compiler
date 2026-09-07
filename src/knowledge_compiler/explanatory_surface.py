"""Local explanatory interaction state for SPEC-035.

The authoritative learning focus is deliberately an input to, never an output of,
this state holder.  Browser navigation remains owned by the existing SPEC-029 and
SPEC-033 runtimes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ValidationError


@dataclass(frozen=True)
class LearningFocus:
    """Stable identity of the one authoritative learning focus."""

    context_key: str
    kind: str
    identity: str

    def __post_init__(self) -> None:
        if not self.context_key or not self.kind or not self.identity:
            raise ValidationError("authoritative focus fields must be non-empty")

    def to_dict(self) -> dict[str, str]:
        return {
            "context_key": self.context_key,
            "kind": self.kind,
            "identity": self.identity,
        }


@dataclass
class ExplanatoryLocalState:
    """Representation-local highlight state with no navigation capability."""

    context_key: str | None = None
    highlighted_key: str | None = None
    interaction_count: int = 0

    def synchronize_context(self, context_key: str) -> None:
        if not context_key:
            raise ValidationError("representation context key must be non-empty")
        if context_key != self.context_key:
            self.context_key = context_key
            self.highlighted_key = None

    def interact(
        self, *, focus: LearningFocus, local_key: str
    ) -> dict[str, Any]:
        """Toggle a local highlight and prove the supplied focus is unchanged."""

        if not local_key:
            raise ValidationError("local explanatory key must be non-empty")
        self.synchronize_context(focus.context_key)
        before = focus.to_dict()
        self.highlighted_key = (
            None if self.highlighted_key == local_key else local_key
        )
        self.interaction_count += 1
        after = focus.to_dict()
        return {
            "local_key": local_key,
            "highlighted_key": self.highlighted_key,
            "interaction_count": self.interaction_count,
            "focus_before": before,
            "focus_after": after,
            "navigation_mutation": before != after,
        }
