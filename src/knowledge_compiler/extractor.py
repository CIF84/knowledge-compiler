"""Vendor-neutral extraction boundary and deterministic JSON fixture adapter."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from .models import Claim, Entity, Relationship, SourceDocument, ValidationError


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    entities: tuple[Entity, ...]
    claims: tuple[Claim, ...]
    relationships: tuple[Relationship, ...]
    metadata: Mapping[str, Any]

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], document: SourceDocument) -> ExtractionResult:
        if not isinstance(value, Mapping):
            raise ValidationError("extraction result must be an object")
        allowed = {"entities", "claims", "relationships", "metadata"}
        unknown = set(value) - allowed
        if unknown:
            raise ValidationError(f"unknown extraction fields: {sorted(unknown)}")
        try:
            return cls(
                entities=tuple(Entity.from_dict(item) for item in value.get("entities", ())),
                claims=tuple(Claim.from_dict(item, document.id) for item in value.get("claims", ())),
                relationships=tuple(Relationship.from_dict(item, document.id) for item in value.get("relationships", ())),
                metadata=dict(value.get("metadata", {})),
            )
        except (KeyError, TypeError) as exc:
            raise ValidationError(f"malformed extraction result: {exc}") from exc


class KnowledgeExtractor(Protocol):
    def extract(self, document: SourceDocument) -> ExtractionResult:
        """Extract typed semantic content from a normalized document."""


class FixtureExtractor:
    """Load a checked-in extraction result; this does not make an AI call."""

    def __init__(self, fixture_path: str | Path) -> None:
        self.fixture_path = Path(fixture_path)

    def extract(self, document: SourceDocument) -> ExtractionResult:
        try:
            raw = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"cannot load extraction fixture {self.fixture_path}: {exc}") from exc
        return ExtractionResult.from_dict(raw, document)
