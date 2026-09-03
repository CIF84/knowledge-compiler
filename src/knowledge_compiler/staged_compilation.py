"""Provider-independent two-pass semantic compilation.

Pass 1 discovers entity nominations. Trusted code then assigns canonical, stable
identifiers and freezes the symbol table. Pass 2 may only link semantic items to
that frozen inventory; it cannot add entities.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Protocol

from .deduplicate import normalized_entity_name
from .models import (
    Claim,
    Entity,
    EntityType,
    KnowledgeModel,
    Proposition,
    Relationship,
    SourceDocument,
    ValidationError,
)
from .normalize import normalize_document
from .proposition_validation import validate_proposition_coverage


STAGED_COMPILER_VERSION = "spec-012-v1"


def _nonempty(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class SymbolNomination:
    """Provider-proposed entity semantics before trusted identity assignment."""

    name: str
    description: str
    entity_type: EntityType
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _nonempty(self.name, "symbol.name")
        if not isinstance(self.description, str):
            raise ValidationError("symbol.description must be a string")
        try:
            object.__setattr__(self, "entity_type", EntityType(self.entity_type))
        except (TypeError, ValueError) as exc:
            allowed = ", ".join(item.value for item in EntityType)
            raise ValidationError(f"symbol.entity_type must be one of: {allowed}") from exc
        if not isinstance(self.aliases, (list, tuple)) or any(
            not isinstance(alias, str) or not alias.strip() for alias in self.aliases
        ):
            raise ValidationError("symbol.aliases must contain non-empty strings")
        object.__setattr__(self, "aliases", tuple(self.aliases))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SymbolNomination:
        if not isinstance(value, Mapping):
            raise ValidationError("symbol nomination must be an object")
        allowed = {"name", "description", "entity_type", "aliases"}
        unknown = set(value) - allowed
        if unknown:
            raise ValidationError(f"unknown symbol nomination fields: {sorted(unknown)}")
        return cls(
            name=value.get("name"),
            description=value.get("description", ""),
            entity_type=value.get("entity_type"),
            aliases=tuple(value.get("aliases", ())),
        )


@dataclass(frozen=True, slots=True)
class SymbolDiscoveryProposal:
    nominations: tuple[SymbolNomination, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "nominations", tuple(self.nominations))
        object.__setattr__(self, "metadata", dict(self.metadata))
        if not self.nominations:
            raise ValidationError("symbol discovery must nominate at least one entity")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SymbolDiscoveryProposal:
        if not isinstance(value, Mapping):
            raise ValidationError("symbol discovery proposal must be an object")
        allowed = {"symbols", "metadata"}
        unknown = set(value) - allowed
        if unknown:
            raise ValidationError(f"unknown symbol discovery fields: {sorted(unknown)}")
        symbols = value.get("symbols")
        if not isinstance(symbols, list):
            raise ValidationError("symbol discovery symbols must be an array")
        return cls(
            tuple(SymbolNomination.from_dict(item) for item in symbols),
            value.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbols": [asdict(item) for item in self.nominations],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class SymbolTable:
    entities: tuple[Entity, ...]
    diagnostics: Mapping[str, Any]
    compiler_version: str = STAGED_COMPILER_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "entities", tuple(self.entities))
        object.__setattr__(self, "diagnostics", dict(self.diagnostics))
        if not self.entities:
            raise ValidationError("symbol table must contain at least one entity")
        ids = [item.id for item in self.entities]
        if len(ids) != len(set(ids)):
            raise ValidationError("symbol table entity IDs must be unique")

    @property
    def ids(self) -> frozenset[str]:
        return frozenset(item.id for item in self.entities)

    def to_dict(self) -> dict[str, Any]:
        return {
            "compiler_version": self.compiler_version,
            "immutable": True,
            "entities": [asdict(item) for item in self.entities],
            "diagnostics": dict(self.diagnostics),
        }


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-")
    return slug or "entity"


def canonicalize_symbol_table(proposal: SymbolDiscoveryProposal) -> SymbolTable:
    """Deterministically normalize duplicate names and assign stable IDs/order."""
    grouped: dict[str, list[SymbolNomination]] = {}
    for nomination in proposal.nominations:
        grouped.setdefault(normalized_entity_name(nomination.name), []).append(nomination)

    canonical_rows: list[tuple[str, str, str, EntityType, tuple[str, ...]]] = []
    alias_normalizations: list[dict[str, Any]] = []
    for normalized_name, nominations in sorted(grouped.items()):
        entity_types = {item.entity_type for item in nominations}
        if len(entity_types) != 1:
            raise ValidationError(
                f"duplicate symbol {normalized_name!r} has conflicting entity types: "
                f"{sorted(item.value for item in entity_types)}"
            )
        canonical_name = min((item.name.strip() for item in nominations), key=lambda x: (x.casefold(), x))
        descriptions = sorted(
            {item.description.strip() for item in nominations},
            key=lambda x: (-len(x), x.casefold(), x),
        )
        description = descriptions[0] if descriptions else ""
        alias_by_normalized: dict[str, str] = {}
        for nomination in nominations:
            for alias in nomination.aliases:
                normalized_alias = normalized_entity_name(alias)
                if normalized_alias != normalized_name:
                    candidate = alias.strip()
                    current = alias_by_normalized.get(normalized_alias)
                    if current is None or (candidate.casefold(), candidate) < (current.casefold(), current):
                        alias_by_normalized[normalized_alias] = candidate
        aliases = tuple(alias_by_normalized[key] for key in sorted(alias_by_normalized))
        if len(nominations) > 1 or aliases:
            alias_normalizations.append({
                "canonical_name": canonical_name,
                "merged_nomination_count": len(nominations),
                "aliases": list(aliases),
            })
        canonical_rows.append((normalized_name, canonical_name, description, next(iter(entity_types)), aliases))

    term_owners: dict[str, str] = {}
    for normalized_name, canonical_name, _description, _entity_type, aliases in canonical_rows:
        for term in (normalized_name, *(normalized_entity_name(alias) for alias in aliases)):
            owner = term_owners.get(term)
            if owner is not None and owner != normalized_name:
                raise ValidationError(
                    f"symbol alias {term!r} conflicts between canonical symbols {owner!r} and {normalized_name!r}"
                )
            term_owners[term] = normalized_name

    base_slugs = [_slug(row[1]) for row in canonical_rows]
    counts = {slug: base_slugs.count(slug) for slug in set(base_slugs)}
    entities = []
    for row, base_slug in zip(canonical_rows, base_slugs, strict=True):
        normalized_name, name, description, entity_type, aliases = row
        entity_id = base_slug
        if counts[base_slug] > 1:
            digest = hashlib.sha256(
                f"{normalized_name}|{entity_type.value}".encode("utf-8")
            ).hexdigest()[:8]
            entity_id = f"{base_slug}-{digest}"
        entities.append(Entity(entity_id, name, description, entity_type, aliases))

    entities.sort(key=lambda item: item.id)
    diagnostics = {
        "raw_nomination_count": len(proposal.nominations),
        "accepted_symbol_count": len(entities),
        "rejected_nomination_count": 0,
        "duplicate_nomination_count": len(proposal.nominations) - len(entities),
        "alias_normalizations": alias_normalizations,
        "entity_type_counts": {
            kind.value: sum(entity.entity_type is kind for entity in entities)
            for kind in EntityType
        },
        "id_strategy": "NORMALIZED_ASCII_KEBAB_NAME_WITH_HASH_SUFFIX_ON_SLUG_COLLISION",
        "ordering": "LEXICOGRAPHIC_STABLE_ENTITY_ID",
    }
    return SymbolTable(tuple(entities), diagnostics)


@dataclass(frozen=True, slots=True)
class SemanticLinkingResult:
    claims: tuple[Claim, ...]
    relationships: tuple[Relationship, ...]
    propositions: tuple[Proposition, ...]
    missing_symbols: tuple[Mapping[str, str], ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "claims", tuple(self.claims))
        object.__setattr__(self, "relationships", tuple(self.relationships))
        object.__setattr__(self, "propositions", tuple(self.propositions))
        object.__setattr__(self, "missing_symbols", tuple(dict(item) for item in self.missing_symbols))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any], document: SourceDocument
    ) -> SemanticLinkingResult:
        if not isinstance(value, Mapping):
            raise ValidationError("semantic linking result must be an object")
        allowed = {"claims", "relationships", "propositions", "missing_symbols", "metadata"}
        unknown = set(value) - allowed
        if unknown:
            raise ValidationError(
                f"Pass 2 cannot create entities or unknown fields: {sorted(unknown)}"
            )
        missing_symbols = value.get("missing_symbols", [])
        if not isinstance(missing_symbols, list):
            raise ValidationError("missing_symbols must be an array")
        normalized_missing = []
        for index, item in enumerate(missing_symbols):
            if not isinstance(item, Mapping):
                raise ValidationError(f"missing_symbols[{index}] must be an object")
            expected = {"surface_form", "semantic_item", "reason"}
            if set(item) != expected:
                raise ValidationError(
                    f"missing_symbols[{index}] must contain exactly {sorted(expected)}"
                )
            normalized_missing.append({key: _nonempty(item[key], f"missing_symbols[{index}].{key}") for key in sorted(expected)})
        return cls(
            claims=tuple(Claim.from_dict(item, document.id) for item in value.get("claims", ())),
            relationships=tuple(
                Relationship.from_dict(item, document.id)
                for item in value.get("relationships", ())
            ),
            propositions=tuple(
                Proposition.from_dict(item, document.id)
                for item in value.get("propositions", ())
            ),
            missing_symbols=tuple(normalized_missing),
            metadata=value.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "claims": [asdict(item) for item in self.claims],
            "relationships": [asdict(item) for item in self.relationships],
            "propositions": [asdict(item) for item in self.propositions],
            "missing_symbols": [dict(item) for item in self.missing_symbols],
            "metadata": dict(self.metadata),
        }


class SymbolTableViolation(ValidationError):
    """Pass 2 referenced endpoints outside the frozen symbol table."""

    def __init__(self, violations: tuple[Mapping[str, Any], ...]) -> None:
        self.violations = tuple(dict(item) for item in violations)
        details = ", ".join(
            f"{item['kind']} {item['id']!r} -> {item['unknown_entity_ids']}"
            for item in self.violations
        )
        super().__init__(f"Pass 2 referenced unknown frozen symbols: {details}")


class StagedSemanticExtractor(Protocol):
    def discover_symbols(self, document: SourceDocument) -> SymbolDiscoveryProposal:
        """Propose source-bounded symbols without assigning canonical IDs."""

    def link_semantics(
        self, document: SourceDocument, symbol_table: SymbolTable
    ) -> SemanticLinkingResult:
        """Propose semantics restricted to the supplied frozen symbol table."""


@dataclass(frozen=True, slots=True)
class StagedCompilationResult:
    model: KnowledgeModel
    symbol_table: SymbolTable
    symbol_proposal: SymbolDiscoveryProposal
    semantic_result: SemanticLinkingResult


def assemble_staged_knowledge_model(
    document: SourceDocument,
    symbol_table: SymbolTable,
    semantic_result: SemanticLinkingResult,
) -> KnowledgeModel:
    known = symbol_table.ids
    violations: list[dict[str, Any]] = []
    for relationship in semantic_result.relationships:
        missing = sorted(
            {relationship.source_entity_id, relationship.target_entity_id} - known
        )
        if missing:
            violations.append({
                "kind": "relationship",
                "id": relationship.id,
                "unknown_entity_ids": missing,
            })
    for proposition in semantic_result.propositions:
        missing = sorted({item.entity_id for item in proposition.role_bindings} - known)
        if missing:
            violations.append({
                "kind": "proposition",
                "id": proposition.id,
                "unknown_entity_ids": missing,
            })
    if violations:
        raise SymbolTableViolation(tuple(violations))

    model = KnowledgeModel(
        document=document,
        entities=symbol_table.entities,
        claims=semantic_result.claims,
        relationships=semantic_result.relationships,
        propositions=semantic_result.propositions,
        metadata={
            "compiler_version": STAGED_COMPILER_VERSION,
            "symbol_discovery": dict(getattr(symbol_table, "diagnostics", {})),
            "symbol_discovery_provider": {},
            "semantic_linking_provider": dict(semantic_result.metadata),
        },
    )
    validate_proposition_coverage(model)
    return model


def compile_staged_knowledge_model(
    text: str,
    extractor: StagedSemanticExtractor,
    *,
    source_metadata: Mapping[str, Any] | None = None,
) -> StagedCompilationResult:
    """Compile text through the fixed two-pass staged boundary."""
    document = normalize_document(text, metadata=source_metadata)
    proposal = extractor.discover_symbols(document)
    symbol_table = canonicalize_symbol_table(proposal)
    semantic_result = extractor.link_semantics(document, symbol_table)
    model = assemble_staged_knowledge_model(document, symbol_table, semantic_result)
    model = KnowledgeModel(
        document=model.document,
        entities=model.entities,
        claims=model.claims,
        relationships=model.relationships,
        propositions=model.propositions,
        metadata={
            **dict(model.metadata),
            "symbol_discovery_provider": dict(proposal.metadata),
        },
    )
    return StagedCompilationResult(model, symbol_table, proposal, semantic_result)
