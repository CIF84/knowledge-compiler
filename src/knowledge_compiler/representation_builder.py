"""Build deterministic presentation models from semantic and detected structures."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from typing import Any, Iterable, Mapping

from .models import KnowledgeModel, Relationship
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .representations import (
    PropositionCard,
    PropositionRoleView,
    Representation,
    RepresentationEdge,
    RepresentationEvidence,
    RepresentationModel,
    RepresentationNode,
    Salience,
)
from .structures import DetectedStructure, DetectedStructureSet, StructureType


_TITLES = {
    StructureType.HIERARCHY: "Hierarchy",
    StructureType.CAUSAL_PATH: "Causal model",
    StructureType.DEPENDENCY_CHAIN: "Dependency model",
    StructureType.PROCESS_CHAIN: "Process chronology",
    StructureType.FEEDBACK_CANDIDATE: "Feedback candidate",
}


def _overlapping_groups(structures: Iterable[DetectedStructure]) -> tuple[tuple[DetectedStructure, ...], ...]:
    remaining = list(sorted(structures, key=lambda item: item.id))
    groups: list[tuple[DetectedStructure, ...]] = []
    while remaining:
        group = [remaining.pop(0)]
        entity_ids = set(group[0].entity_ids)
        changed = True
        while changed:
            changed = False
            for structure in tuple(remaining):
                if entity_ids.intersection(structure.entity_ids):
                    remaining.remove(structure)
                    group.append(structure)
                    entity_ids.update(structure.entity_ids)
                    changed = True
        groups.append(tuple(sorted(group, key=lambda item: item.id)))
    return tuple(groups)


def _support_ids(structure: DetectedStructure, index: int) -> tuple[str, ...]:
    groups = structure.metadata.get("supporting_relationship_ids_by_edge")
    if isinstance(groups, list) and index < len(groups) and isinstance(groups[index], list):
        values = tuple(value for value in groups[index] if isinstance(value, str) and value)
        if values:
            return values
    return (structure.relationship_ids[index],)


def _salience(structure_type: StructureType, edge_count: int) -> Salience:
    if edge_count <= 1:
        return Salience.SPARSE
    if structure_type is StructureType.FEEDBACK_CANDIDATE:
        return Salience.PRIMARY
    if edge_count == 2:
        return Salience.SECONDARY
    return Salience.PRIMARY


class RepresentationBuilder:
    """Map detected structures to thin, provenance-preserving presentations."""

    def build(
        self,
        model: KnowledgeModel,
        structures: DetectedStructureSet,
        *,
        presentation_metadata: Mapping[str, Any] | None = None,
    ) -> RepresentationModel:
        structures.validate_against(model)
        metadata = dict(presentation_metadata or {})
        entities = {entity.id: entity for entity in model.entities}
        relationships = {relationship.id: relationship for relationship in model.relationships}
        representations: list[Representation] = []

        by_type: dict[StructureType, list[DetectedStructure]] = defaultdict(list)
        for structure in structures.structures:
            by_type[structure.structure_type].append(structure)

        for structure_type in StructureType:
            for group in _overlapping_groups(by_type[structure_type]):
                edge_support: dict[tuple[str, str, str], set[str]] = defaultdict(set)
                for structure in group:
                    for index, relationship_id in enumerate(structure.relationship_ids):
                        relationship = relationships[relationship_id]
                        key = (
                            relationship.source_entity_id,
                            relationship.relationship_type.value,
                            relationship.target_entity_id,
                        )
                        edge_support[key].update(_support_ids(structure, index))

                edges = tuple(
                    self._edge(relationships, key, tuple(sorted(support_ids)))
                    for key, support_ids in sorted(edge_support.items())
                )
                node_ids = sorted({value for edge in edges for value in (edge.source_entity_id, edge.target_entity_id)})
                nodes = tuple(
                    RepresentationNode(
                        entity_id=entity_id,
                        label=entities[entity_id].name,
                        description=entities[entity_id].description,
                        entity_type=entities[entity_id].entity_type,
                    )
                    for entity_id in node_ids
                )
                source_ids = tuple(item.id for item in group)
                signature = f"{structure_type.value}|{'|'.join(source_ids)}"
                representation_id = f"representation-{sha256(signature.encode()).hexdigest()[:16]}"
                salience = _salience(structure_type, len(edges))
                warnings = list(metadata.get("structure_warnings", {}).get(structure_type.value, ()))
                if salience is Salience.SPARSE:
                    warnings.append("Sparse structure: this view contains only one supported relationship.")
                representations.append(Representation(
                    id=representation_id,
                    representation_type=structure_type,
                    source_structure_ids=source_ids,
                    title=_TITLES[structure_type],
                    nodes=nodes,
                    edges=edges,
                    salience=salience,
                    warnings=tuple(dict.fromkeys(warnings)),
                ))

        salience_order = {Salience.PRIMARY: 0, Salience.SECONDARY: 1, Salience.SPARSE: 2}
        representations.sort(key=lambda item: (salience_order[item.salience], item.representation_type.value, item.id))
        domain = str(model.metadata.get("domain") or metadata.get("domain") or "unknown")
        title = str(metadata.get("title") or domain.replace("_", " ").title())
        result = RepresentationModel(
            document_id=model.document.id,
            title=title,
            domain=domain,
            representations=tuple(representations),
            builder_version="spec-010-v1" if model.propositions else "spec-005-v1",
            empty_state=None if representations else (
                "No supported higher-order structure was detected. The source may still contain useful "
                "entities and relationships, but this viewer will not invent a diagram."
            ),
            warnings=tuple(metadata.get("known_upstream_limitations", ())),
            metadata={
                "representation_count": len(representations),
                "source_structure_count": len(structures.structures),
                **({"proposition_card_count": len(model.propositions)} if model.propositions else {}),
                "salience_counts": {
                    salience.value: sum(item.salience is salience for item in representations)
                    for salience in Salience
                },
            },
            proposition_cards=tuple(
                PropositionCard(
                    proposition_id=proposition.id,
                    proposition_type=proposition.proposition_type,
                    statement=proposition.statement,
                    roles=tuple(
                        PropositionRoleView(
                            role=binding.role,
                            entity_id=binding.entity_id,
                            label=entities[binding.entity_id].name,
                            entity_type=entities[binding.entity_id].entity_type,
                        )
                        for binding in proposition.role_bindings
                    ),
                    relationship_type=proposition.relationship_type,
                    comparison_operator=proposition.comparison_operator,
                    evidence=proposition.evidence,
                    origin=proposition.origin,
                )
                for proposition in sorted(model.propositions, key=lambda item: item.id)
            ),
        )
        result.validate_against(model, structures)
        return result

    @staticmethod
    def _edge(
        relationships: Mapping[str, Relationship],
        key: tuple[str, str, str],
        relationship_ids: tuple[str, ...],
    ) -> RepresentationEdge:
        supporting = tuple(relationships[relationship_id] for relationship_id in relationship_ids)
        canonical = supporting[0]
        definition = RELATIONSHIP_DEFINITION_MAP[canonical.relationship_type]
        evidence = tuple(
            RepresentationEvidence(
                relationship_id=relationship.id,
                document_id=span.document_id,
                start_char=span.start_char,
                end_char=span.end_char,
                quote=span.quote,
            )
            for relationship in supporting
            for span in sorted(relationship.evidence, key=lambda item: (item.start_char, item.end_char, item.quote))
        )
        return RepresentationEdge(
            source_entity_id=key[0],
            target_entity_id=key[2],
            relationship_type=canonical.relationship_type,
            relationship_label=canonical.relationship_type.value.replace("_", " "),
            meaning=definition.meaning,
            direction=definition.direction,
            relationship_ids=relationship_ids,
            evidence=evidence,
            origins=tuple(relationship.origin for relationship in supporting),
        )
