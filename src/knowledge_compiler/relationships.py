"""Canonical, domain-general relationship grammar."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .models import RelationshipType, ValidationError


class RelationshipFamily(StrEnum):
    STRUCTURAL = "STRUCTURAL"
    CAUSAL = "CAUSAL"
    DEPENDENCY = "DEPENDENCY"
    TEMPORAL = "TEMPORAL"
    INTERACTION = "INTERACTION"
    TRANSFORMATION = "TRANSFORMATION"
    DESCRIPTIVE = "DESCRIPTIVE"


@dataclass(frozen=True, slots=True)
class RelationshipDefinition:
    type: RelationshipType
    family: RelationshipFamily
    meaning: str
    direction: str
    source_role: str
    target_role: str
    use_when: str
    avoid_when: str
    symmetric: bool = False

    def __post_init__(self) -> None:
        for field_name in ("meaning", "direction", "source_role", "target_role", "use_when", "avoid_when"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"relationship definition {self.type.value}.{field_name} must be non-empty")
        if self.symmetric and self.direction != "symmetric":
            raise ValidationError(f"symmetric relationship {self.type.value} must use direction='symmetric'")
        if not self.symmetric and self.direction == "symmetric":
            raise ValidationError(f"directional relationship {self.type.value} cannot use direction='symmetric'")


def _definition(
    type: RelationshipType,
    family: RelationshipFamily,
    meaning: str,
    direction: str,
    source_role: str,
    target_role: str,
    use_when: str,
    avoid_when: str,
    *,
    symmetric: bool = False,
) -> RelationshipDefinition:
    return RelationshipDefinition(type, family, meaning, direction, source_role, target_role, use_when, avoid_when, symmetric)


RELATIONSHIP_DEFINITIONS = (
    _definition(RelationshipType.IS_A, RelationshipFamily.STRUCTURAL,
                "The source is a kind, category, or subtype of the target.", "instance_to_type",
                "instance or subtype", "broader type or category",
                "The source can truthfully be described as a target.",
                "Do not use for parts, examples, similarity, or temporary states."),
    _definition(RelationshipType.PART_OF, RelationshipFamily.STRUCTURAL,
                "The source is a constituent or component of the target.", "part_to_whole",
                "part or component", "containing whole",
                "The source exists as a component or subpart of the target.",
                "Never reverse whole and part; do not use for interaction or dependency."),
    _definition(RelationshipType.EXAMPLE_OF, RelationshipFamily.STRUCTURAL,
                "The source is an illustrative instance of the target concept.", "example_to_concept",
                "example", "concept illustrated",
                "The source is presented as an example of the target.",
                "Do not use merely because the source is a subtype; prefer IS_A for classification."),
    _definition(RelationshipType.CAUSES, RelationshipFamily.CAUSAL,
                "The source brings about the target as an effect.", "cause_to_effect",
                "cause", "effect",
                "The source is stated to produce the target outcome.",
                "Do not use for chronology, association, contribution, or unspecified influence."),
    _definition(RelationshipType.AFFECTS, RelationshipFamily.CAUSAL,
                "The source causally influences the target without a specified direction or complete production.", "influence_to_affected",
                "influence", "affected entity, process, or variable",
                "The source changes or influences the target, but the text does not support CAUSES, INCREASES, or DECREASES.",
                "Do not use for mere association, chronology, physical force, or interaction with no stated effect."),
    _definition(RelationshipType.INCREASES, RelationshipFamily.CAUSAL,
                "The source causally raises the amount, rate, value, probability, or intensity of the target.", "increaser_to_increased_variable",
                "causal factor", "quantity or variable increased",
                "The source is explicitly said to make the target greater, faster, more likely, or more intense.",
                "Do not infer from nearby words such as more or faster; never use when the source says slower, lower, or less."),
    _definition(RelationshipType.DECREASES, RelationshipFamily.CAUSAL,
                "The source causally lowers the amount, rate, value, probability, or intensity of the target.", "decreaser_to_decreased_variable",
                "causal factor", "quantity or variable decreased",
                "The source is explicitly said to make the target smaller, slower, less likely, or less intense.",
                "Do not use for absence, prevention without a scalar target, or mere negative association."),
    _definition(RelationshipType.INDUCES, RelationshipFamily.CAUSAL,
                "The source produces the target through an explicitly described induction mechanism.", "inducer_to_induced_effect",
                "inducing phenomenon", "induced phenomenon",
                "The source explicitly says induces or describes a recognized induction mechanism.",
                "Do not use as a metaphor for generic causation, influence, motivation, or historical response."),
    _definition(RelationshipType.ENABLES, RelationshipFamily.DEPENDENCY,
                "The source makes the target possible without necessarily causing it to occur.", "enabler_to_enabled",
                "enabling condition or capability", "capability or process made possible",
                "The target could not occur, or is materially made possible, because of the source.",
                "Do not use for delivery, participation, weak assistance, or an effect that actually occurred."),
    _definition(RelationshipType.REQUIRES, RelationshipFamily.DEPENDENCY,
                "The source depends on the target as a prerequisite or necessary resource.", "dependent_to_requirement",
                "dependent", "prerequisite or required resource",
                "The source cannot operate or occur as described without the target.",
                "Do not reverse prerequisite and dependent; do not use for optional support."),
    _definition(RelationshipType.CONSTRAINS, RelationshipFamily.DEPENDENCY,
                "The source limits the possible behavior, values, or choices of the target.", "constraint_to_constrained",
                "constraint", "constrained entity, process, or variable",
                "The source imposes a limit, rule, boundary, or restriction on the target.",
                "Do not use to mean unchanged, unrelated, merely different, or causally reduced."),
    _definition(RelationshipType.PRECEDES, RelationshipFamily.TEMPORAL,
                "The source occurs before the target in time or an explicit process sequence.", "earlier_to_later",
                "earlier event or process", "later event or process",
                "The source explicitly occurs before, previously, first, then, or after relative to the target.",
                "Do not infer causality from order; do not reverse earlier and later."),
    _definition(RelationshipType.INTERACTS_WITH, RelationshipFamily.INTERACTION,
                "The source and target directly interact, with no more precise directional semantics supported.", "symmetric",
                "interaction participant", "interaction participant",
                "The text supports direct mutual interaction but not a more precise active predicate.",
                "Do not use for distant association, one-way effect, dependency, or chronology.", symmetric=True),
    _definition(RelationshipType.BINDS_TO, RelationshipFamily.INTERACTION,
                "The source physically or chemically binds or attaches to the target.", "symmetric",
                "binding participant", "binding participant",
                "The source explicitly binds or attaches to the target.",
                "Do not use for metaphorical commitment, dependency, influence, or literal physical force.", symmetric=True),
    _definition(RelationshipType.TRANSFERS_TO, RelationshipFamily.INTERACTION,
                "The source item, material, or information moves to the target destination or recipient.", "transferred_item_to_destination",
                "item, material, or information transferred", "destination or recipient",
                "The source is explicitly carried, delivered, moved, or transferred to the target.",
                "Do not make the carrier the source unless the carrier itself moves to the destination; do not use for enabling."),
    _definition(RelationshipType.EXERTS_FORCE_ON, RelationshipFamily.INTERACTION,
                "The source exerts a literal physical force on the target.", "force_exerter_to_physical_target",
                "physical force source", "physical object receiving force",
                "A literal physical force is explicitly exerted on the target.",
                "Never use metaphorically for influence, contribution, binding, pressure, or causation."),
    _definition(RelationshipType.TRANSFORMS_INTO, RelationshipFamily.TRANSFORMATION,
                "The source itself changes state or identity and becomes the target.", "prior_state_to_resulting_state",
                "entity or state before transformation", "same entity or resulting material after transformation",
                "The source itself becomes the target through a transformation.",
                "Do not use when an actor causes, creates, attempts, participates in, or responds to the target."),
    _definition(RelationshipType.CREATES, RelationshipFamily.TRANSFORMATION,
                "The source produces or brings a distinct target into existence.", "creator_to_created",
                "producer or generative process", "newly produced entity or result",
                "The source produces a target that is distinct from the source.",
                "Do not use when the source itself becomes the target; use TRANSFORMS_INTO instead."),
    _definition(RelationshipType.MEASURED_BY, RelationshipFamily.DESCRIPTIVE,
                "The source property or variable is quantified or assessed by the target metric, observation, or procedure.", "measurand_to_measure",
                "property or variable measured", "metric, observation, or measurement procedure",
                "The target is explicitly how the source is measured or quantified.",
                "Do not point to something that merely responds to, correlates with, or exemplifies the source."),
    _definition(RelationshipType.CONTRADICTS, RelationshipFamily.DESCRIPTIVE,
                "The source and target assert mutually incompatible propositions.", "symmetric",
                "proposition or claim", "incompatible proposition or claim",
                "Both sides are explicit propositions that cannot simultaneously hold as stated.",
                "Do not use for difference, disagreement without incompatibility, trade-off, or negative causality.", symmetric=True),
)


def relationship_definition_map() -> dict[RelationshipType, RelationshipDefinition]:
    definitions: dict[RelationshipType, RelationshipDefinition] = {}
    for definition in RELATIONSHIP_DEFINITIONS:
        if definition.type in definitions:
            raise ValidationError(f"duplicate relationship definition: {definition.type.value}")
        definitions[definition.type] = definition
    missing = set(RelationshipType) - set(definitions)
    extra = set(definitions) - set(RelationshipType)
    if missing or extra:
        raise ValidationError(
            f"relationship definitions do not match active vocabulary; "
            f"missing={sorted(item.value for item in missing)}, extra={sorted(item.value for item in extra)}"
        )
    return definitions


def render_relationship_grammar() -> str:
    """Render the canonical registry into compact extraction instructions."""
    lines = ["ACTIVE RELATIONSHIP CONTRACTS (source --TYPE--> target):"]
    for definition in RELATIONSHIP_DEFINITIONS:
        symmetry = "symmetric" if definition.symmetric else f"direction={definition.direction}"
        lines.extend(
            (
                f"{definition.type.value} [{definition.family.value}; {symmetry}]",
                f"  meaning: {definition.meaning}",
                f"  roles: source={definition.source_role}; target={definition.target_role}",
                f"  use: {definition.use_when}",
                f"  avoid: {definition.avoid_when}",
            )
        )
    return "\n".join(lines)


RELATIONSHIP_DEFINITION_MAP = relationship_definition_map()
