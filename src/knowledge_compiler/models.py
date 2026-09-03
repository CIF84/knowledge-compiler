"""Domain types and validation for the KnowledgeModel intermediate representation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when input cannot satisfy the semantic model invariants."""


class SourceType(StrEnum):
    TEXT = "text"


class EntityType(StrEnum):
    CONCEPT = "CONCEPT"
    OBJECT = "OBJECT"
    PROCESS = "PROCESS"
    VARIABLE = "VARIABLE"
    SYSTEM = "SYSTEM"
    COMPONENT = "COMPONENT"


class Origin(StrEnum):
    SOURCE = "SOURCE"
    INFERRED = "INFERRED"


class RelationshipType(StrEnum):
    IS_A = "IS_A"
    PART_OF = "PART_OF"
    CAUSES = "CAUSES"
    INCREASES = "INCREASES"
    DECREASES = "DECREASES"
    ENABLES = "ENABLES"
    REQUIRES = "REQUIRES"
    CONSTRAINS = "CONSTRAINS"
    PRECEDES = "PRECEDES"
    TRANSFORMS_INTO = "TRANSFORMS_INTO"
    INTERACTS_WITH = "INTERACTS_WITH"
    MEASURED_BY = "MEASURED_BY"
    EXAMPLE_OF = "EXAMPLE_OF"
    CONTRADICTS = "CONTRADICTS"
    CREATES = "CREATES"
    INDUCES = "INDUCES"
    EXERTS_FORCE_ON = "EXERTS_FORCE_ON"
    AFFECTS = "AFFECTS"
    BINDS_TO = "BINDS_TO"
    TRANSFERS_TO = "TRANSFERS_TO"


class PropositionType(StrEnum):
    COMPARISON_CONDITION = "COMPARISON_CONDITION"
    TRANSFER_EVENT = "TRANSFER_EVENT"


class PropositionRole(StrEnum):
    LEFT_OPERAND = "LEFT_OPERAND"
    RIGHT_OPERAND = "RIGHT_OPERAND"
    OUTCOME = "OUTCOME"
    EVENT = "EVENT"
    OBJECT = "OBJECT"
    DESTINATION = "DESTINATION"


class ComparisonOperator(StrEnum):
    GREATER_THAN = "GREATER_THAN"


def _enum(enum_type: type[StrEnum], value: Any, path: str) -> Any:
    try:
        return enum_type(value)
    except (ValueError, TypeError) as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ValidationError(f"{path} must be one of: {allowed}") from exc


def _confidence(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{path} must be a number between 0 and 1")
    result = float(value)
    if not 0.0 <= result <= 1.0:
        raise ValidationError(f"{path} must be between 0 and 1")
    return result


def _nonempty(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class SourceDocument:
    id: str
    text: str
    source_type: SourceType = SourceType.TEXT
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _nonempty(self.id, "document.id")
        if not isinstance(self.text, str) or not self.text:
            raise ValidationError("document.text must be a non-empty string")
        object.__setattr__(self, "source_type", _enum(SourceType, self.source_type, "document.source_type"))
        if not isinstance(self.metadata, Mapping):
            raise ValidationError("document.metadata must be an object")
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SourceDocument:
        return cls(
            id=value.get("id"),
            text=value.get("text"),
            source_type=value.get("source_type", SourceType.TEXT),
            metadata=value.get("metadata", {}),
        )


@dataclass(frozen=True, slots=True)
class SourceSpan:
    document_id: str
    start_char: int
    end_char: int
    quote: str

    def validate_against(self, document: SourceDocument) -> None:
        if self.document_id != document.id:
            raise ValidationError(f"evidence references unknown document {self.document_id!r}")
        if isinstance(self.start_char, bool) or not isinstance(self.start_char, int):
            raise ValidationError("evidence.start_char must be an integer")
        if isinstance(self.end_char, bool) or not isinstance(self.end_char, int):
            raise ValidationError("evidence.end_char must be an integer")
        if self.start_char < 0 or self.end_char <= self.start_char or self.end_char > len(document.text):
            raise ValidationError("evidence span lies outside the document")
        actual = document.text[self.start_char : self.end_char]
        if self.quote != actual:
            raise ValidationError(f"evidence quote mismatch: expected {actual!r}, got {self.quote!r}")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], document_id: str | None = None) -> SourceSpan:
        return cls(
            document_id=value.get("document_id", document_id),
            start_char=value.get("start_char"),
            end_char=value.get("end_char"),
            quote=value.get("quote"),
        )


@dataclass(frozen=True, slots=True)
class Entity:
    id: str
    name: str
    description: str
    entity_type: EntityType
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _nonempty(self.id, "entity.id")
        _nonempty(self.name, "entity.name")
        if not isinstance(self.description, str):
            raise ValidationError("entity.description must be a string")
        object.__setattr__(self, "entity_type", _enum(EntityType, self.entity_type, "entity.entity_type"))
        if not isinstance(self.aliases, (list, tuple)) or any(not isinstance(alias, str) or not alias.strip() for alias in self.aliases):
            raise ValidationError("entity.aliases must contain non-empty strings")
        object.__setattr__(self, "aliases", tuple(self.aliases))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> Entity:
        return cls(
            id=value.get("id"), name=value.get("name"),
            description=value.get("description", ""),
            entity_type=value.get("entity_type"), aliases=value.get("aliases", ()),
        )


@dataclass(frozen=True, slots=True)
class Claim:
    id: str
    statement: str
    evidence: tuple[SourceSpan, ...]
    confidence: float
    origin: Origin

    def __post_init__(self) -> None:
        _nonempty(self.id, "claim.id")
        _nonempty(self.statement, "claim.statement")
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "confidence", _confidence(self.confidence, "claim.confidence"))
        object.__setattr__(self, "origin", _enum(Origin, self.origin, "claim.origin"))
        if self.origin is Origin.SOURCE and not self.evidence:
            raise ValidationError("SOURCE claims require evidence")
        if self.origin is Origin.INFERRED and self.evidence:
            raise ValidationError("INFERRED claims must not present source evidence")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], document_id: str | None = None) -> Claim:
        return cls(
            id=value.get("id"), statement=value.get("statement"),
            evidence=tuple(SourceSpan.from_dict(span, document_id) for span in value.get("evidence", ())),
            confidence=value.get("confidence"), origin=value.get("origin"),
        )


@dataclass(frozen=True, slots=True)
class Relationship:
    id: str
    source_entity_id: str
    relationship_type: RelationshipType
    target_entity_id: str
    statement: str
    evidence: tuple[SourceSpan, ...]
    confidence: float
    origin: Origin

    def __post_init__(self) -> None:
        for field_name in ("id", "source_entity_id", "target_entity_id", "statement"):
            _nonempty(getattr(self, field_name), f"relationship.{field_name}")
        object.__setattr__(self, "relationship_type", _enum(RelationshipType, self.relationship_type, "relationship.relationship_type"))
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "confidence", _confidence(self.confidence, "relationship.confidence"))
        object.__setattr__(self, "origin", _enum(Origin, self.origin, "relationship.origin"))
        if self.origin is Origin.SOURCE and not self.evidence:
            raise ValidationError("SOURCE relationships require evidence")
        if self.origin is Origin.INFERRED and self.evidence:
            raise ValidationError("INFERRED relationships must not present source evidence")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], document_id: str | None = None) -> Relationship:
        return cls(
            id=value.get("id"), source_entity_id=value.get("source_entity_id"),
            relationship_type=value.get("relationship_type"), target_entity_id=value.get("target_entity_id"),
            statement=value.get("statement"),
            evidence=tuple(SourceSpan.from_dict(span, document_id) for span in value.get("evidence", ())),
            confidence=value.get("confidence"), origin=value.get("origin"),
        )


@dataclass(frozen=True, slots=True)
class PropositionRoleBinding:
    role: PropositionRole
    entity_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "role", _enum(PropositionRole, self.role, "proposition role"))
        _nonempty(self.entity_id, "proposition role entity_id")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> PropositionRoleBinding:
        return cls(role=value.get("role"), entity_id=value.get("entity_id"))


def deterministic_proposition_id(
    proposition_type: PropositionType | str,
    role_bindings: tuple[PropositionRoleBinding, ...],
    relationship_type: RelationshipType | str,
    comparison_operator: ComparisonOperator | str | None = None,
) -> str:
    """Derive a stable identity from the proposition's canonical semantic shape."""
    kind = PropositionType(proposition_type)
    relationship = RelationshipType(relationship_type)
    operator = ComparisonOperator(comparison_operator).value if comparison_operator is not None else "NONE"
    roles = sorted((PropositionRole(item.role).value, item.entity_id) for item in role_bindings)
    signature = "|".join((kind.value, relationship.value, operator, *(f"{role}={entity}" for role, entity in roles)))
    digest = sha256(signature.encode()).hexdigest()[:16]
    return f"proposition-{kind.value.lower().replace('_', '-')}-{digest}"


@dataclass(frozen=True, slots=True)
class Proposition:
    id: str
    proposition_type: PropositionType
    statement: str
    role_bindings: tuple[PropositionRoleBinding, ...]
    relationship_type: RelationshipType
    evidence: tuple[SourceSpan, ...]
    confidence: float
    origin: Origin
    comparison_operator: ComparisonOperator | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "proposition_type", _enum(PropositionType, self.proposition_type, "proposition.type"))
        object.__setattr__(self, "relationship_type", _enum(RelationshipType, self.relationship_type, "proposition.relationship_type"))
        object.__setattr__(self, "origin", _enum(Origin, self.origin, "proposition.origin"))
        operator = (
            _enum(ComparisonOperator, self.comparison_operator, "proposition.comparison_operator")
            if self.comparison_operator is not None else None
        )
        bindings = tuple(sorted(self.role_bindings, key=lambda item: item.role.value))
        evidence = tuple(self.evidence)
        _nonempty(self.statement, "proposition.statement")
        if len({item.role for item in bindings}) != len(bindings):
            raise ValidationError("proposition roles must be unique")
        roles = {item.role for item in bindings}
        if self.proposition_type is PropositionType.COMPARISON_CONDITION:
            required = {PropositionRole.LEFT_OPERAND, PropositionRole.RIGHT_OPERAND, PropositionRole.OUTCOME}
            if roles != required or operator is None or self.relationship_type is not RelationshipType.CAUSES:
                raise ValidationError(
                    "comparison condition requires left operand, right operand, outcome, operator, and CAUSES"
                )
            by_role = {item.role: item.entity_id for item in bindings}
            if by_role[PropositionRole.LEFT_OPERAND] == by_role[PropositionRole.RIGHT_OPERAND]:
                raise ValidationError("comparison condition operands must be distinct")
        elif self.proposition_type is PropositionType.TRANSFER_EVENT:
            required = {PropositionRole.EVENT, PropositionRole.OBJECT, PropositionRole.DESTINATION}
            if roles != required or operator is not None or self.relationship_type is not RelationshipType.TRANSFERS_TO:
                raise ValidationError(
                    "transfer event requires event, object, destination, TRANSFERS_TO, and no comparison operator"
                )
        object.__setattr__(self, "comparison_operator", operator)
        object.__setattr__(self, "role_bindings", bindings)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "confidence", _confidence(self.confidence, "proposition.confidence"))
        expected_id = deterministic_proposition_id(
            self.proposition_type, bindings, self.relationship_type, operator
        )
        if self.id != expected_id:
            raise ValidationError(f"proposition.id must equal deterministic ID {expected_id!r}")
        if self.origin is Origin.SOURCE and not evidence:
            raise ValidationError("SOURCE propositions require evidence")
        if self.origin is Origin.INFERRED and evidence:
            raise ValidationError("INFERRED propositions must not present source evidence")

    def entity_id_for(self, role: PropositionRole | str) -> str:
        canonical = PropositionRole(role)
        return next(item.entity_id for item in self.role_bindings if item.role is canonical)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], document_id: str | None = None) -> Proposition:
        bindings = tuple(
            PropositionRoleBinding.from_dict(item) for item in value.get("role_bindings", ())
        )
        proposition_type = value.get("proposition_type")
        relationship_type = value.get("relationship_type")
        operator = value.get("comparison_operator")
        try:
            proposition_id = value.get("id") or deterministic_proposition_id(
                proposition_type, bindings, relationship_type, operator
            )
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"malformed proposition identity: {exc}") from exc
        return cls(
            id=proposition_id,
            proposition_type=proposition_type,
            statement=value.get("statement"),
            role_bindings=bindings,
            relationship_type=relationship_type,
            evidence=tuple(SourceSpan.from_dict(span, document_id) for span in value.get("evidence", ())),
            confidence=value.get("confidence"),
            origin=value.get("origin"),
            comparison_operator=operator,
        )


@dataclass(frozen=True, slots=True)
class KnowledgeModel:
    document: SourceDocument
    entities: tuple[Entity, ...]
    claims: tuple[Claim, ...]
    relationships: tuple[Relationship, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    propositions: tuple[Proposition, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "entities", tuple(self.entities))
        object.__setattr__(self, "claims", tuple(self.claims))
        object.__setattr__(self, "relationships", tuple(self.relationships))
        object.__setattr__(self, "metadata", dict(self.metadata))
        object.__setattr__(self, "propositions", tuple(self.propositions))
        entity_ids = [entity.id for entity in self.entities]
        if len(entity_ids) != len(set(entity_ids)):
            raise ValidationError("entity IDs must be unique")
        if len({claim.id for claim in self.claims}) != len(self.claims):
            raise ValidationError("claim IDs must be unique")
        if len({relationship.id for relationship in self.relationships}) != len(self.relationships):
            raise ValidationError("relationship IDs must be unique")
        proposition_ids = [proposition.id for proposition in self.propositions]
        if len(proposition_ids) != len(set(proposition_ids)):
            raise ValidationError("proposition IDs must be unique")
        known = set(entity_ids)
        if known.intersection(proposition_ids):
            raise ValidationError("domain entity and proposition IDs must be distinct")
        for relationship in self.relationships:
            missing = {relationship.source_entity_id, relationship.target_entity_id} - known
            if missing:
                raise ValidationError(f"relationship {relationship.id!r} references unknown entities: {sorted(missing)}")
        entities = {entity.id: entity for entity in self.entities}
        for proposition in self.propositions:
            missing = {item.entity_id for item in proposition.role_bindings} - known
            if missing:
                raise ValidationError(f"proposition {proposition.id!r} references unknown entities: {sorted(missing)}")
            if proposition.proposition_type is PropositionType.TRANSFER_EVENT:
                event_id = proposition.entity_id_for(PropositionRole.EVENT)
                destination_id = proposition.entity_id_for(PropositionRole.DESTINATION)
                if event_id == destination_id:
                    raise ValidationError("transfer event cannot be its own destination")
                if entities[event_id].entity_type is not EntityType.PROCESS:
                    raise ValidationError("transfer event role must reference a PROCESS entity")
                if entities[destination_id].entity_type is EntityType.PROCESS:
                    raise ValidationError("transfer destination must reference a domain endpoint, not a PROCESS")
        for item in (*self.claims, *self.relationships, *self.propositions):
            for evidence in item.evidence:
                evidence.validate_against(self.document)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        if not self.propositions:
            value.pop("propositions")
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> KnowledgeModel:
        if not isinstance(value, Mapping):
            raise ValidationError("knowledge model must be an object")
        document = SourceDocument.from_dict(value.get("document", {}))
        return cls(
            document=document,
            entities=tuple(Entity.from_dict(item) for item in value.get("entities", ())),
            claims=tuple(Claim.from_dict(item, document.id) for item in value.get("claims", ())),
            relationships=tuple(Relationship.from_dict(item, document.id) for item in value.get("relationships", ())),
            metadata=value.get("metadata", {}),
            propositions=tuple(
                Proposition.from_dict(item, document.id) for item in value.get("propositions", ())
            ),
        )
