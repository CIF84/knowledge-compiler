"""Compile trusted semantic material into renderer-independent representation decisions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from typing import Any, Iterable

from .models import KnowledgeModel, PropositionType, ValidationError
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .representation_builder import RepresentationBuilder
from .representation_strategy import (
    RepresentationContext,
    RepresentationPlan,
    StrategyType,
    ground_context,
    resolve_representation,
)
from .structure_detection import StructureDetector


COMPARE_CONTRAST = "COMPARE_CONTRAST"
WORKED_EXAMPLE = "WORKED_EXAMPLE"

_STRATEGY_PRIORITY = {
    StrategyType.RECIPROCAL_MECHANISM.value: 6,
    StrategyType.CAUSAL_MECHANISM.value: 5,
    StrategyType.HIERARCHY_COMPOSITION.value: 4,
    StrategyType.PROCESS_SEQUENCE.value: 3,
    StrategyType.DEPENDENCY_STRUCTURE.value: 2,
    StrategyType.FOCUSED_RELATIONSHIP.value: 1,
    StrategyType.CONCISE_PROSE.value: 0,
}


def _json_value(value: Any) -> Any:
    """Return a deterministic JSON-shaped copy, including StrEnum values."""

    return json.loads(json.dumps(value, sort_keys=True))


def _stable_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


@dataclass(frozen=True)
class SemanticRepresentationDecision:
    """Auditable compiler output upstream of any learner-facing renderer."""

    decision_id: str
    source_document_id: str
    semantic_focus_identity: str
    semantic_class: str
    selected_strategy: str
    sufficiency: str
    confidence: str
    selected_rule_id: str
    selected_structure_ids: tuple[str, ...]
    available_concepts: tuple[dict[str, Any], ...]
    available_relationships: tuple[dict[str, Any], ...]
    detected_structural_signals: tuple[dict[str, Any], ...]
    rejected_candidates: tuple[dict[str, Any], ...]
    grounding_provenance_refs: tuple[dict[str, Any], ...]
    fallback_reason: str | None
    renderer_contract: str
    representation_plan: RepresentationPlan | None
    semantic_payload: dict[str, Any]

    def strategy_signature(self) -> dict[str, Any]:
        """Return the label/domain-independent semantic decision signature."""

        return {
            "selected_strategy": self.selected_strategy,
            "sufficiency": self.sufficiency,
            "selected_rule_id": self.selected_rule_id,
            "selected_structure_ids": list(self.selected_structure_ids),
            "signals": [
                {
                    "structure_type": item["structure_type"],
                    "relationship_types": item["relationship_types"],
                    "relationship_count": item["relationship_count"],
                    "reciprocal": item["reciprocal"],
                }
                for item in self.detected_structural_signals
            ],
            "fallback_reason": self.fallback_reason,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "source_document_id": self.source_document_id,
            "semantic_focus_identity": self.semantic_focus_identity,
            "semantic_class": self.semantic_class,
            "available_trusted_concepts": [_json_value(item) for item in self.available_concepts],
            "available_trusted_relationships": [
                _json_value(item) for item in self.available_relationships
            ],
            "detected_structural_signals": [
                _json_value(item) for item in self.detected_structural_signals
            ],
            "selected_representation_strategy": self.selected_strategy,
            "selected_structure_ids": list(self.selected_structure_ids),
            "selected_rule_id": self.selected_rule_id,
            "sufficiency": self.sufficiency,
            "confidence": self.confidence,
            "rejected_richer_candidates": [
                _json_value(item) for item in self.rejected_candidates
            ],
            "grounding_provenance_refs": [
                _json_value(item) for item in self.grounding_provenance_refs
            ],
            "fallback_reason": self.fallback_reason,
            "renderer_contract": self.renderer_contract,
            "representation_plan": (
                self.representation_plan.to_dict() if self.representation_plan else None
            ),
            "semantic_payload": _json_value(self.semantic_payload),
            "decision_inputs": {
                "trusted_semantics_only": True,
                "domain_name_used": False,
                "fixture_filename_used": False,
                "concept_label_used": False,
                "source_id_used_as_strategy_rule": False,
                "renderer_used_as_strategy_authority": False,
            },
        }


def _domain_namespace(model: KnowledgeModel) -> str:
    """Supply a stable context namespace; it is never passed to strategy selection."""

    value = model.document.metadata.get("domain")
    return str(value) if isinstance(value, str) and value else "source"


def _representation_dicts(model: KnowledgeModel) -> tuple[dict[str, Any], ...]:
    structures = StructureDetector().detect(model)
    domain = _domain_namespace(model)
    built = RepresentationBuilder().build(
        model,
        structures,
        presentation_metadata={"domain": domain, "title": domain.replace("_", " ").title()},
    )
    return tuple(_json_value(item) for item in built.to_dict()["representations"])


def _signal(representation: dict[str, Any]) -> dict[str, Any]:
    edges = representation["edges"]
    directions = {
        (item["source_entity_id"], item["target_entity_id"])
        for item in edges
    }
    return {
        "structure_ids": list(representation["source_structure_ids"]),
        "structure_type": representation["representation_type"],
        "entity_ids": sorted(item["entity_id"] for item in representation["nodes"]),
        "relationship_ids": sorted(
            identity for item in edges for identity in item["relationship_ids"]
        ),
        "relationship_types": sorted({item["relationship_type"] for item in edges}),
        "relationship_count": len(edges),
        "reciprocal": any((target, source) in directions for source, target in directions),
        "detected_from_normalized_relationships": True,
    }


def _concepts(nodes: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "entity_id": item["entity_id"],
            "entity_type": item.get("entity_type"),
            "label": item.get("label") or item.get("name"),
        }
        for item in sorted(nodes, key=lambda value: value["entity_id"])
    )


def _relationships(edges: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "relationship_ids": list(item["relationship_ids"]),
            "source_entity_id": item["source_entity_id"],
            "relationship_type": item["relationship_type"],
            "target_entity_id": item["target_entity_id"],
            "direction": item["direction"],
            "evidence": [_json_value(value) for value in item.get("evidence", [])],
        }
        for item in sorted(
            edges,
            key=lambda value: (
                value["source_entity_id"],
                value["relationship_type"],
                value["target_entity_id"],
            ),
        )
    )


def _decision(
    *,
    model: KnowledgeModel,
    semantic_class: str,
    identity: str,
    plan: RepresentationPlan | None,
    selected_strategy: str,
    selected_rule_id: str,
    selected_structure_ids: tuple[str, ...],
    nodes: Iterable[dict[str, Any]],
    relationships: Iterable[dict[str, Any]],
    signals: Iterable[dict[str, Any]],
    rejected: Iterable[dict[str, Any]],
    evidence: Iterable[dict[str, Any]],
    fallback_reason: str | None,
    semantic_payload: dict[str, Any] | None = None,
) -> SemanticRepresentationDecision:
    signals = tuple(_json_value(item) for item in signals)
    semantic_key = {
        "document": model.document.id,
        "class": semantic_class,
        "identity": identity,
        "strategy": selected_strategy,
        "rule": selected_rule_id,
        "structures": list(selected_structure_ids),
    }
    sufficient = fallback_reason is None
    return SemanticRepresentationDecision(
        decision_id=f"decision-{_stable_digest(semantic_key)[:16]}",
        source_document_id=model.document.id,
        semantic_focus_identity=identity,
        semantic_class=semantic_class,
        selected_strategy=selected_strategy,
        sufficiency=(
            "SUFFICIENT_TRUSTED_STRUCTURE"
            if sufficient
            else "INSUFFICIENT_SUPPORTED_STRUCTURE"
        ),
        confidence=(
            "DETERMINISTIC_GROUNDED"
            if sufficient
            else "DETERMINISTIC_FAIL_CLOSED"
        ),
        selected_rule_id=selected_rule_id,
        selected_structure_ids=selected_structure_ids,
        available_concepts=_concepts(nodes),
        available_relationships=_relationships(relationships),
        detected_structural_signals=signals,
        rejected_candidates=tuple(_json_value(item) for item in rejected),
        grounding_provenance_refs=tuple(_json_value(item) for item in evidence),
        fallback_reason=fallback_reason,
        renderer_contract=(
            "SPEC038_REPRESENTATION_PLAN"
            if plan is not None
            else "SEMANTIC_DECISION_ONLY_NO_PROTECTED_RENDERER_FORM"
        ),
        representation_plan=plan,
        semantic_payload=semantic_payload or {},
    )


def _fallback_context(model: KnowledgeModel, identity: str) -> RepresentationContext:
    entity = next((item for item in model.entities if item.id == identity), None)
    if entity is None:
        raise ValidationError(f"unknown concept focus: {identity}")
    return RepresentationContext(
        context_key=f"source:{model.document.id}:concept:{identity}",
        semantic_focus_identity=identity,
        semantic_class="concept",
        label=entity.name,
        description=entity.description or "No trusted description is available.",
        structure_type=None,
        nodes=(
            {
                "entity_id": entity.id,
                "label": entity.name,
                "description": entity.description,
                "entity_type": entity.entity_type.value,
            },
        ),
        relationships=(),
        warnings=(),
        trusted_input_refs=("validated KnowledgeModel entity",),
    )


def _compile_concept(model: KnowledgeModel, identity: str) -> SemanticRepresentationDecision:
    representations = tuple(
        item
        for item in _representation_dicts(model)
        if identity in {node["entity_id"] for node in item["nodes"]}
    )
    if not representations:
        context = _fallback_context(model, identity)
        plan = resolve_representation(context)
        return _decision(
            model=model,
            semantic_class="concept",
            identity=identity,
            plan=plan,
            selected_strategy=plan.strategy_type.value,
            selected_rule_id=plan.deterministic_rule_metadata["rule_id"],
            selected_structure_ids=(),
            nodes=context.nodes,
            relationships=(),
            signals=(),
            rejected=(
                {
                    "candidate": "RICH_STRUCTURAL_REPRESENTATION",
                    "reason": "NO_DETECTED_TRUSTED_STRUCTURE_CONTAINS_FOCUS",
                },
            ),
            evidence=(),
            fallback_reason="NO_DETECTED_TRUSTED_STRUCTURE_CONTAINS_FOCUS",
        )

    candidates: list[tuple[dict[str, Any], RepresentationContext, RepresentationPlan]] = []
    domain = {"domain_id": _domain_namespace(model), "label": "Trusted source"}
    for representation in representations:
        context = ground_context(domain, representation, "concept", identity)
        context = replace(context, structure_type=None)
        candidates.append((representation, context, resolve_representation(context)))
    candidates.sort(
        key=lambda value: (
            -len(value[1].relationships),
            -_STRATEGY_PRIORITY[value[2].strategy_type.value],
            value[0]["id"],
        )
    )
    selected_representation, context, plan = candidates[0]
    signals = tuple(_signal(item[0]) for item in candidates)
    rejected = tuple(
        {
            "candidate_structure_ids": list(item[0]["source_structure_ids"]),
            "candidate_strategy": item[2].strategy_type.value,
            "reason": "LOWER_DETERMINISTIC_STRUCTURAL_RANK",
        }
        for item in candidates[1:]
    )
    return _decision(
        model=model,
        semantic_class="concept",
        identity=identity,
        plan=plan,
        selected_strategy=plan.strategy_type.value,
        selected_rule_id=plan.deterministic_rule_metadata["rule_id"],
        selected_structure_ids=tuple(selected_representation["source_structure_ids"]),
        nodes=context.nodes,
        relationships=context.relationships,
        signals=signals,
        rejected=rejected,
        evidence=plan.evidence_refs,
        fallback_reason=plan.deterministic_rule_metadata["fallback_reason"],
    )


def _compile_canonical(model: KnowledgeModel, identity: str) -> SemanticRepresentationDecision:
    representations = tuple(
        item
        for item in _representation_dicts(model)
        if any(identity in edge["relationship_ids"] for edge in item["edges"])
    )
    if not representations:
        relationship = next(
            (item for item in model.relationships if item.id == identity), None
        )
        if relationship is None:
            raise ValidationError(f"unknown canonical relationship focus: {identity}")
        entities = {item.id: item for item in model.entities}
        definition = RELATIONSHIP_DEFINITION_MAP[relationship.relationship_type]
        nodes = tuple(
            {
                "entity_id": value.id,
                "label": value.name,
                "description": value.description,
                "entity_type": value.entity_type.value,
            }
            for value in (
                entities[relationship.source_entity_id],
                entities[relationship.target_entity_id],
            )
        )
        edge = {
            "relationship_ids": [relationship.id],
            "source_entity_id": relationship.source_entity_id,
            "target_entity_id": relationship.target_entity_id,
            "relationship_type": relationship.relationship_type.value,
            "meaning": definition.meaning,
            "direction": definition.direction,
            "provenance_status": "SOURCE_EVIDENCE",
            "evidence": [asdict(value) for value in relationship.evidence],
        }
        context = RepresentationContext(
            context_key=f"source:{model.document.id}:canonical:{identity}",
            semantic_focus_identity=identity,
            semantic_class="canonical",
            label=identity,
            description=definition.meaning,
            structure_type=None,
            nodes=nodes,
            relationships=(edge,),
            warnings=(),
            trusted_input_refs=("validated KnowledgeModel canonical relationship",),
        )
        structure_ids: tuple[str, ...] = ()
        signals: tuple[dict[str, Any], ...] = ()
    else:
        representation = sorted(representations, key=lambda item: item["id"])[0]
        domain = {"domain_id": _domain_namespace(model), "label": "Trusted source"}
        context = replace(
            ground_context(domain, representation, "canonical", identity),
            structure_type=None,
        )
        structure_ids = tuple(representation["source_structure_ids"])
        signals = (_signal(representation),)
    plan = resolve_representation(context)
    return _decision(
        model=model,
        semantic_class="canonical",
        identity=identity,
        plan=plan,
        selected_strategy=plan.strategy_type.value,
        selected_rule_id=plan.deterministic_rule_metadata["rule_id"],
        selected_structure_ids=structure_ids,
        nodes=context.nodes,
        relationships=context.relationships,
        signals=signals,
        rejected=(),
        evidence=plan.evidence_refs,
        fallback_reason=None,
    )


def _compile_proposition(model: KnowledgeModel, identity: str) -> SemanticRepresentationDecision:
    proposition = next((item for item in model.propositions if item.id == identity), None)
    if proposition is None:
        raise ValidationError(f"unknown proposition focus: {identity}")
    entities = {item.id: item for item in model.entities}
    role_nodes = tuple(
        {
            "entity_id": entities[binding.entity_id].id,
            "label": entities[binding.entity_id].name,
            "description": entities[binding.entity_id].description,
            "entity_type": entities[binding.entity_id].entity_type.value,
        }
        for binding in proposition.role_bindings
    )
    evidence = tuple(asdict(value) for value in proposition.evidence)
    payload = {
        "proposition_type": proposition.proposition_type.value,
        "statement": proposition.statement,
        "role_bindings": [
            {"role": item.role.value, "entity_id": item.entity_id}
            for item in proposition.role_bindings
        ],
        "relationship_type": proposition.relationship_type.value,
        "comparison_operator": (
            proposition.comparison_operator.value
            if proposition.comparison_operator is not None
            else None
        ),
    }
    if proposition.proposition_type is PropositionType.COMPARISON_CONDITION:
        return _decision(
            model=model,
            semantic_class="proposition",
            identity=identity,
            plan=None,
            selected_strategy=COMPARE_CONTRAST,
            selected_rule_id="EXPLICIT_COMPARISON_PROPOSITION",
            selected_structure_ids=(),
            nodes=role_nodes,
            relationships=(),
            signals=(
                {
                    "structure_ids": [],
                    "structure_type": "COMPARISON_CONDITION",
                    "entity_ids": sorted(item["entity_id"] for item in role_nodes),
                    "relationship_ids": [],
                    "relationship_types": [proposition.relationship_type.value],
                    "relationship_count": 0,
                    "reciprocal": False,
                    "explicit_roles": sorted(
                        item.role.value for item in proposition.role_bindings
                    ),
                    "comparison_operator": proposition.comparison_operator.value,
                    "detected_from_normalized_relationships": False,
                    "detected_from_grounded_proposition": True,
                },
            ),
            rejected=(),
            evidence=evidence,
            fallback_reason=None,
            semantic_payload=payload,
        )

    context = RepresentationContext(
        context_key=f"source:{model.document.id}:proposition:{identity}",
        semantic_focus_identity=identity,
        semantic_class="explanation",
        label=proposition.statement,
        description=proposition.statement,
        structure_type=None,
        nodes=role_nodes,
        relationships=(),
        warnings=("No admitted rule-to-instance representation form.",),
        trusted_input_refs=("validated KnowledgeModel proposition",),
    )
    plan = resolve_representation(context)
    return _decision(
        model=model,
        semantic_class="proposition",
        identity=identity,
        plan=plan,
        selected_strategy=plan.strategy_type.value,
        selected_rule_id="UNSUPPORTED_PROPOSITION_FORM_FALLBACK",
        selected_structure_ids=(),
        nodes=role_nodes,
        relationships=(),
        signals=(
            {
                "structure_ids": [],
                "structure_type": proposition.proposition_type.value,
                "entity_ids": sorted(item["entity_id"] for item in role_nodes),
                "relationship_ids": [],
                "relationship_types": [proposition.relationship_type.value],
                "relationship_count": 0,
                "reciprocal": False,
                "detected_from_normalized_relationships": False,
                "detected_from_grounded_proposition": True,
            },
        ),
        rejected=(
            {
                "candidate": WORKED_EXAMPLE,
                "reason": "TRANSFER_EVENT_IS_NOT_A_RULE_TO_INSTANCE_MAPPING",
            },
        ),
        evidence=evidence,
        fallback_reason="NO_SUPPORTED_RULE_TO_INSTANCE_FORM",
        semantic_payload=payload,
    )


def compile_semantic_representation(
    model: KnowledgeModel, semantic_class: str, identity: str
) -> SemanticRepresentationDecision:
    """Compile one focus from validated source-bounded semantics, without label rules."""

    if not identity:
        raise ValidationError("semantic focus identity must be non-empty")
    if semantic_class == "concept":
        return _compile_concept(model, identity)
    if semantic_class == "canonical":
        return _compile_canonical(model, identity)
    if semantic_class == "proposition":
        return _compile_proposition(model, identity)
    raise ValidationError(f"unsupported compiler semantic class: {semantic_class}")
