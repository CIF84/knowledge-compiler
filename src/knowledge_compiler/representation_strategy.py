"""Deterministic trusted-structure to learner-facing representation plans."""

from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .models import ValidationError


class StrategyType(str, Enum):
    CAUSAL_MECHANISM = "CAUSAL_MECHANISM"
    RECIPROCAL_MECHANISM = "RECIPROCAL_MECHANISM"
    PROCESS_SEQUENCE = "PROCESS_SEQUENCE"
    HIERARCHY_COMPOSITION = "HIERARCHY_COMPOSITION"
    DEPENDENCY_STRUCTURE = "DEPENDENCY_STRUCTURE"
    FOCUSED_RELATIONSHIP = "FOCUSED_RELATIONSHIP"
    CONCISE_PROSE = "CONCISE_PROSE"


CAUSAL_PREDICATES = frozenset(
    {"CAUSES", "INCREASES", "DECREASES", "AFFECTS", "CREATES", "INDUCES"}
)
HIERARCHY_PREDICATES = frozenset({"PART_OF", "IS_A", "EXAMPLE_OF"})
DEPENDENCY_PREDICATES = frozenset({"REQUIRES", "ENABLES", "CONSTRAINS"})
SEQUENCE_PREDICATES = frozenset({"PRECEDES"})


@dataclass(frozen=True)
class RepresentationContext:
    context_key: str
    semantic_focus_identity: str | None
    semantic_class: str
    label: str
    description: str
    structure_type: str | None
    nodes: tuple[dict[str, Any], ...]
    relationships: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]
    trusted_input_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.context_key or not self.semantic_class or not self.label:
            raise ValidationError("representation context identity fields must be non-empty")
        node_ids = [item["entity_id"] for item in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValidationError("representation context node identities must be unique")
        known = set(node_ids)
        for relationship in self.relationships:
            if relationship["source_entity_id"] not in known or relationship["target_entity_id"] not in known:
                raise ValidationError("representation context relationship endpoint is absent")
        if self.semantic_class == "concept" and self.semantic_focus_identity not in known:
            raise ValidationError("concept focus is absent from representation context")


@dataclass(frozen=True)
class RepresentationPlan:
    strategy_type: StrategyType
    semantic_focus_identity: str | None
    semantic_class: str
    title: str
    payload: dict[str, Any]
    evidence_refs: tuple[dict[str, Any], ...]
    deterministic_rule_metadata: dict[str, Any]
    trusted_input_refs: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_type": self.strategy_type.value,
            "semantic_focus_identity": self.semantic_focus_identity,
            "semantic_class": self.semantic_class,
            "title": self.title,
            "payload": deepcopy(self.payload),
            "evidence_refs": [deepcopy(item) for item in self.evidence_refs],
            "deterministic_rule_metadata": deepcopy(self.deterministic_rule_metadata),
            "trusted_input_refs": list(self.trusted_input_refs),
            "warnings": list(self.warnings),
        }


def _normalized_ground_relationship(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "relationship_ids": list(edge["relationship_ids"]),
        "source_entity_id": edge["source_entity_id"],
        "target_entity_id": edge["target_entity_id"],
        "relationship_type": edge["relationship_type"],
        "meaning": edge["meaning"],
        "direction": edge["direction"],
        "provenance_status": edge["provenance_status"],
        "evidence": [deepcopy(item) for item in edge.get("evidence", [])],
    }


def _normalized_depth_relationship(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "relationship_ids": [item["id"]],
        "source_entity_id": item["source_entity_id"],
        "target_entity_id": item["target_entity_id"],
        "relationship_type": item["relationship_type"],
        "meaning": item["predicate_meaning"],
        "statement": item["statement"],
        "direction": "DIRECTED",
        "provenance_status": "EXACT_SOURCE_EVIDENCE",
        "evidence": [deepcopy(value) for value in item.get("evidence", [])],
    }


def _connected_component(
    focus: str, nodes: Iterable[dict[str, Any]], relationships: Iterable[dict[str, Any]]
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    node_by_id = {item["entity_id"]: deepcopy(item) for item in nodes}
    relationships = tuple(deepcopy(item) for item in relationships)
    adjacency: dict[str, set[str]] = defaultdict(set)
    for item in relationships:
        adjacency[item["source_entity_id"]].add(item["target_entity_id"])
        adjacency[item["target_entity_id"]].add(item["source_entity_id"])
    seen = {focus}
    queue = deque([focus])
    while queue:
        for neighbor in sorted(adjacency[queue.popleft()]):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return (
        tuple(node_by_id[key] for key in sorted(seen)),
        tuple(
            item
            for item in relationships
            if item["source_entity_id"] in seen and item["target_entity_id"] in seen
        ),
    )


def ground_context(
    domain: dict[str, Any], representation: dict[str, Any], kind: str, identity: str | None
) -> RepresentationContext:
    prefix = f"ground:{domain['domain_id']}:{representation['id']}"
    nodes = tuple(deepcopy(item) for item in representation["nodes"])
    relationships = tuple(
        _normalized_ground_relationship(item) for item in representation["edges"]
    )
    if kind == "orientation":
        return RepresentationContext(
            context_key=f"{prefix}:orientation",
            semantic_focus_identity=None,
            semantic_class=kind,
            label=domain["label"],
            description=representation["title"],
            structure_type=representation["representation_type"],
            nodes=nodes,
            relationships=relationships,
            warnings=tuple(representation.get("warnings", [])),
            trusted_input_refs=("workspace domain", "trusted representation metadata"),
        )
    if kind == "concept":
        item = next((value for value in nodes if value["entity_id"] == identity), None)
        if item is None:
            raise ValidationError(f"concept {identity} is absent from {representation['id']}")
        local_nodes, local_relationships = _connected_component(identity, nodes, relationships)
        return RepresentationContext(
            context_key=f"{prefix}:concept:{identity}",
            semantic_focus_identity=identity,
            semantic_class=kind,
            label=item["label"],
            description=item.get("description") or "No trusted description is available.",
            structure_type=representation["representation_type"],
            nodes=local_nodes,
            relationships=local_relationships,
            warnings=tuple(representation.get("warnings", [])),
            trusted_input_refs=(
                "workspace-fixture.json representation.nodes selected concept",
                "workspace-fixture.json connected representation edges",
            ),
        )
    if kind == "canonical":
        selected = next(
            (item for item in relationships if identity in item["relationship_ids"]), None
        )
        if selected is None:
            raise ValidationError(f"relationship {identity} is absent from {representation['id']}")
        selected_nodes = tuple(
            item
            for item in nodes
            if item["entity_id"]
            in {selected["source_entity_id"], selected["target_entity_id"]}
        )
        return RepresentationContext(
            context_key=f"{prefix}:canonical:{identity}",
            semantic_focus_identity=identity,
            semantic_class=kind,
            label=identity,
            description=selected["meaning"],
            structure_type=representation["representation_type"],
            nodes=selected_nodes,
            relationships=(selected,),
            warnings=tuple(representation.get("warnings", [])),
            trusted_input_refs=(
                "workspace-fixture.json selected canonical edge",
                "workspace-fixture.json selected edge endpoints and evidence",
            ),
        )
    raise ValidationError(f"unsupported ground semantic class: {kind}")


def depth_context(expansion: dict[str, Any], kind: str, identity: str | None) -> RepresentationContext:
    prefix = f"depth:{expansion['id']}"
    nodes = tuple(deepcopy(item) for item in expansion["concepts"])
    relationships = tuple(
        _normalized_depth_relationship(item) for item in expansion["canonical_items"]
    )
    if kind == "orientation":
        return RepresentationContext(
            context_key=f"{prefix}:orientation",
            semantic_focus_identity=None,
            semantic_class=kind,
            label="Double-slit experiment · deeper knowledge",
            description="Trusted source-bounded explanatory context.",
            structure_type=None,
            nodes=nodes,
            relationships=relationships,
            warnings=(),
            trusted_input_refs=("depth-map.json admitted expansion",),
        )
    if kind == "concept":
        item = next((value for value in nodes if value["entity_id"] == identity), None)
        if item is None:
            raise ValidationError(f"depth concept {identity} is absent")
        local_nodes, local_relationships = _connected_component(identity, nodes, relationships)
        return RepresentationContext(
            context_key=f"{prefix}:concept:{identity}",
            semantic_focus_identity=identity,
            semantic_class=kind,
            label=item["label"],
            description=item["description"],
            structure_type=None,
            nodes=local_nodes,
            relationships=local_relationships,
            warnings=(),
            trusted_input_refs=(
                "depth-map.json selected admitted concept",
                "depth-map.json incident admitted canonical relationships",
            ),
        )
    if kind == "canonical":
        selected = next(
            (item for item in relationships if identity in item["relationship_ids"]), None
        )
        if selected is None:
            raise ValidationError(f"depth relationship {identity} is absent")
        selected_nodes = tuple(
            item
            for item in nodes
            if item["entity_id"]
            in {selected["source_entity_id"], selected["target_entity_id"]}
        )
        return RepresentationContext(
            context_key=f"{prefix}:canonical:{identity}",
            semantic_focus_identity=identity,
            semantic_class=kind,
            label=identity,
            description=selected.get("statement") or selected["meaning"],
            structure_type=None,
            nodes=selected_nodes,
            relationships=(selected,),
            warnings=(),
            trusted_input_refs=("depth-map.json selected canonical relationship",),
        )
    if kind == "explanation":
        item = next(
            (value for value in expansion["explanatory_items"] if value["id"] == identity),
            None,
        )
        if item is None:
            raise ValidationError(f"depth explanation {identity} is absent")
        participant_nodes = tuple(
            value for value in nodes if value["entity_id"] in item["participant_entity_ids"]
        )
        return RepresentationContext(
            context_key=f"{prefix}:explanation:{identity}",
            semantic_focus_identity=identity,
            semantic_class=kind,
            label=item["short_label"],
            description=item["statement"],
            structure_type=None,
            nodes=participant_nodes,
            relationships=(),
            warnings=("Source-backed explanation; not a canonical relationship.",),
            trusted_input_refs=("depth-map.json selected source-backed explanation",),
        )
    raise ValidationError(f"unsupported depth semantic class: {kind}")


def _evidence_refs(relationships: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    values: list[dict[str, Any]] = []
    for relationship in relationships:
        for evidence in relationship.get("evidence", []):
            value = deepcopy(evidence)
            value["relationship_ids"] = list(relationship["relationship_ids"])
            values.append(value)
    return tuple(
        sorted(
            values,
            key=lambda item: (
                item.get("document_id", ""),
                item.get("start_char", -1),
                item.get("end_char", -1),
                item.get("relationship_id", ""),
            ),
        )
    )


def _node_map(context: RepresentationContext) -> dict[str, dict[str, Any]]:
    return {item["entity_id"]: deepcopy(item) for item in context.nodes}


def _relationship_payload(
    relationship: dict[str, Any], nodes: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    return {
        **deepcopy(relationship),
        "source_label": nodes[relationship["source_entity_id"]]["label"],
        "target_label": nodes[relationship["target_entity_id"]]["label"],
    }


def _topological_nodes(context: RepresentationContext) -> list[dict[str, Any]]:
    nodes = _node_map(context)
    incoming = {identity: 0 for identity in nodes}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for item in context.relationships:
        source = item["source_entity_id"]
        target = item["target_entity_id"]
        outgoing[source].append(target)
        incoming[target] += 1
    queue = deque(sorted(identity for identity, count in incoming.items() if count == 0))
    ordered: list[str] = []
    while queue:
        identity = queue.popleft()
        ordered.append(identity)
        for target in sorted(outgoing[identity]):
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    ordered.extend(sorted(set(nodes) - set(ordered)))
    return [nodes[identity] for identity in ordered]


def _is_reciprocal(context: RepresentationContext) -> bool:
    pairs = {
        (item["source_entity_id"], item["target_entity_id"])
        for item in context.relationships
        if item["relationship_type"] in CAUSAL_PREDICATES
    }
    return any((target, source) in pairs for source, target in pairs)


def _strategy_rule(context: RepresentationContext) -> tuple[StrategyType, str, str | None]:
    if context.semantic_class == "canonical":
        return StrategyType.FOCUSED_RELATIONSHIP, "CANONICAL_EDGE_FOCUS", None
    if context.semantic_class in {"orientation", "explanation"}:
        reason = (
            "ORIENTATION_HAS_NO_SINGLE_STRUCTURAL_FOCUS"
            if context.semantic_class == "orientation"
            else "SOURCE_BACKED_EXPLANATION_HAS_NO_ADMITTED_STRUCTURAL_FORM"
        )
        return StrategyType.CONCISE_PROSE, "TRUTHFUL_PROSE_FALLBACK", reason
    if context.semantic_class != "concept":
        raise ValidationError(f"unsupported semantic class: {context.semantic_class}")
    if not context.relationships:
        return (
            StrategyType.CONCISE_PROSE,
            "TRUTHFUL_PROSE_FALLBACK",
            "NO_TRUSTED_SUPPORTING_RELATIONSHIP",
        )
    predicates = {item["relationship_type"] for item in context.relationships}
    if _is_reciprocal(context):
        return StrategyType.RECIPROCAL_MECHANISM, "RECIPROCAL_DIRECTIONAL_PAIR", None
    if predicates <= SEQUENCE_PREDICATES:
        return StrategyType.PROCESS_SEQUENCE, "EXPLICIT_PRECEDES_CHAIN", None
    if predicates <= HIERARCHY_PREDICATES:
        return StrategyType.HIERARCHY_COMPOSITION, "TYPED_HIERARCHY_EDGES", None
    if predicates <= DEPENDENCY_PREDICATES:
        return StrategyType.DEPENDENCY_STRUCTURE, "TYPED_DEPENDENCY_EDGES", None
    if predicates <= CAUSAL_PREDICATES:
        return StrategyType.CAUSAL_MECHANISM, "DIRECTIONAL_CAUSAL_NETWORK", None
    return (
        StrategyType.CONCISE_PROSE,
        "TRUTHFUL_PROSE_FALLBACK",
        "MIXED_OR_UNSUPPORTED_TRUSTED_STRUCTURE",
    )


def resolve_representation(context: RepresentationContext) -> RepresentationPlan:
    strategy, rule, fallback_reason = _strategy_rule(context)
    nodes = _node_map(context)
    relationships = [
        _relationship_payload(item, nodes) for item in context.relationships
    ]
    common = {
        "focus": {
            "identity": context.semantic_focus_identity,
            "label": context.label,
            "description": context.description,
        },
        "nodes": [deepcopy(item) for item in context.nodes],
        "relationships": relationships,
        "claim_source": "TRUSTED_COMMITTED_SEMANTIC_MATERIAL",
    }
    if strategy is StrategyType.HIERARCHY_COMPOSITION:
        source_ids = {item["source_entity_id"] for item in context.relationships}
        target_ids = {item["target_entity_id"] for item in context.relationships}
        common["roots"] = [nodes[key] for key in sorted(target_ids - source_ids or target_ids)]
        common["members"] = [nodes[key] for key in sorted(source_ids)]
    elif strategy in {
        StrategyType.CAUSAL_MECHANISM,
        StrategyType.DEPENDENCY_STRUCTURE,
        StrategyType.PROCESS_SEQUENCE,
    }:
        common["ordered_nodes"] = _topological_nodes(context)
    elif strategy is StrategyType.RECIPROCAL_MECHANISM:
        common["cycle_nodes"] = [deepcopy(item) for item in context.nodes]
    elif strategy is StrategyType.FOCUSED_RELATIONSHIP:
        common["relationship"] = relationships[0]
    elif strategy is StrategyType.CONCISE_PROSE:
        common["body"] = context.description

    rationale = {
        "rule_id": rule,
        "structure_type": context.structure_type,
        "semantic_class": context.semantic_class,
        "predicates": sorted(
            {item["relationship_type"] for item in context.relationships}
        ),
        "relationship_count": len(context.relationships),
        "domain_is_resolver_input": False,
        "depth_is_resolver_input": False,
        "fallback_reason": fallback_reason,
    }
    title = context.label
    if strategy is StrategyType.FOCUSED_RELATIONSHIP:
        title = (
            f"{relationships[0]['source_label']} → "
            f"{relationships[0]['target_label']}"
        )
    return RepresentationPlan(
        strategy_type=strategy,
        semantic_focus_identity=context.semantic_focus_identity,
        semantic_class=context.semantic_class,
        title=title,
        payload=common,
        evidence_refs=_evidence_refs(context.relationships),
        deterministic_rule_metadata=rationale,
        trusted_input_refs=context.trusted_input_refs,
        warnings=context.warnings,
    )


def build_plan_catalog(
    fixture: dict[str, Any], depth_packet: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    plans: dict[str, dict[str, Any]] = {}
    for domain in fixture["domains"]:
        for representation in domain["learning_model"]["representations"]:
            contexts = [ground_context(domain, representation, "orientation", None)]
            contexts.extend(
                ground_context(domain, representation, "concept", node["entity_id"])
                for node in representation["nodes"]
            )
            contexts.extend(
                ground_context(domain, representation, "canonical", relationship_id)
                for edge in representation["edges"]
                for relationship_id in edge["relationship_ids"]
            )
            for context in contexts:
                plans[context.context_key] = resolve_representation(context).to_dict()
    for expansion in depth_packet["expansions"]:
        contexts = [depth_context(expansion, "orientation", None)]
        contexts.extend(
            depth_context(expansion, "concept", item["entity_id"])
            for item in expansion["concepts"]
        )
        contexts.extend(
            depth_context(expansion, "canonical", item["id"])
            for item in expansion["canonical_items"]
        )
        contexts.extend(
            depth_context(expansion, "explanation", item["id"])
            for item in expansion["explanatory_items"]
        )
        for context in contexts:
            plans[context.context_key] = resolve_representation(context).to_dict()
    return dict(sorted(plans.items()))
