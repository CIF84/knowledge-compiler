"""Trusted one-level semantic depth and workspace state for SPEC-020."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from typing import Any, Literal

from .assertion_compilation import (
    CanonicalizationProposal,
    GroundedAssertionSet,
    compile_assertion_semantics,
)
from .continuous_navigation import CameraState, VIEWPORT
from .layout import with_layouts
from .models import KnowledgeModel, Origin, RelationshipType, SourceDocument, ValidationError
from .navigation_learning_workspace import _route
from .representation_builder import RepresentationBuilder
from .representations import RepresentationModel
from .resolution_strategies import ResolutionStrategyId
from .staged_compilation import SymbolTable
from .structure_detection import StructureDetector
from .structures import DetectedStructure, DetectedStructureSet, StructureType


SEMANTIC_DEPTH_VERSION = "spec-020-v1"
FOCUS_ENTITY_ID = "double-slit-experiment"
FOCUS_LABEL = "double-slit experiment"
PARENT_RELATIONSHIP_ID = "relationship-05b19ee4b6d50060"
SCOPE_START_MARKER = "Wave–particle duality\n\n"
SCOPE_END_MARKER = "\n\nUncertainty principle"
EXPECTED_PARENT_SOURCE_SHA256 = "9e978db999ee67134d347f91fe9f32934c982f4de9b496e4bf664cb00cce23ea"
EXPECTED_SCOPE_SHA256 = "eb184226638e5cbb331865f87ed613c22aaf68f3188b9ee3dcd4c743b94997a1"
CHILD_SYMBOL_IDS = (
    "atom",
    "double-slit-experiment",
    "electron",
    "interference-pattern",
    "photon",
    "principle-of-complementarity",
    "waveparticle-duality",
)
WORLD_BOUNDS = {"min_x": 0.0, "min_y": 0.0, "max_x": 2400.0, "max_y": 1500.0}
INITIAL_CAMERA = {"x": 0.0, "y": 0.0, "scale": 1.0}


@dataclass(frozen=True, slots=True)
class FrozenSourceScope:
    parent_document_id: str
    start_char: int
    end_char: int
    text: str
    sha256: str

    def __post_init__(self) -> None:
        if self.start_char < 0 or self.end_char <= self.start_char:
            raise ValidationError("semantic-depth source scope coordinates are invalid")
        if self.end_char - self.start_char != len(self.text):
            raise ValidationError("semantic-depth source scope length does not match coordinates")
        if hashlib.sha256(self.text.encode()).hexdigest() != self.sha256:
            raise ValidationError("semantic-depth source scope hash mismatch")

    @property
    def document_id(self) -> str:
        return f"scope-{self.sha256[:16]}"

    def to_dict(self, *, include_text: bool = True) -> dict[str, Any]:
        value = {
            "strategy": "DETERMINISTIC_CONTIGUOUS_SECTION",
            "parent_document_id": self.parent_document_id,
            "document_id": self.document_id,
            "section": "Wave–particle duality",
            "start_char": self.start_char,
            "end_char": self.end_char,
            "character_count": len(self.text),
            "word_count": len(self.text.split()),
            "sha256": self.sha256,
        }
        if include_text:
            value["text"] = self.text
        return value

    def as_document(self, parent: KnowledgeModel) -> SourceDocument:
        return SourceDocument(
            id=self.document_id,
            text=self.text,
            metadata={
                **dict(parent.document.metadata),
                "source_processing_strategy": "DETERMINISTIC_CONTIGUOUS_SECTION",
                "parent_document_id": self.parent_document_id,
                "parent_source_start_char": self.start_char,
                "parent_source_end_char": self.end_char,
                "scope_sha256": self.sha256,
            },
        )


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def model_hash(model: KnowledgeModel) -> str:
    return hashlib.sha256(canonical_bytes(model.to_dict())).hexdigest()


def freeze_focus_selection(parent: KnowledgeModel) -> dict[str, Any]:
    entity = next((item for item in parent.entities if item.id == FOCUS_ENTITY_ID), None)
    relationship = next(
        (item for item in parent.relationships if item.id == PARENT_RELATIONSHIP_ID), None
    )
    if entity is None or entity.name != FOCUS_LABEL:
        raise ValidationError("frozen semantic-depth focus is absent from the trusted parent")
    if relationship is None or FOCUS_ENTITY_ID not in (
        relationship.source_entity_id,
        relationship.target_entity_id,
    ):
        raise ValidationError("frozen focus lacks its accepted direct parent relationship")
    return {
        "spec": "SPEC-020",
        "selection_status": "FROZEN_BEFORE_LIVE_OUTPUT",
        "entity_id": FOCUS_ENTITY_ID,
        "name": entity.name,
        "entity_type": entity.entity_type.value,
        "parent_relationship_id": PARENT_RELATIONSHIP_ID,
        "parent_relationship": {
            "source_entity_id": relationship.source_entity_id,
            "relationship_type": relationship.relationship_type.value,
            "target_entity_id": relationship.target_entity_id,
            "statement": relationship.statement,
        },
        "rationale": (
            "The double-slit experiment is a concrete, pedagogically meaningful process already "
            "admitted in the trusted parent, and its fixed source section explains how wave-like "
            "interference and particle-like detections coexist without external enrichment."
        ),
        "expected_resolution_strategy": ResolutionStrategyId.GENERIC_DETAIL.value,
        "expected_depth": (
            "A source-supported local model connecting the experiment, interference, quantum "
            "objects, wave–particle duality, and complementarity."
        ),
        "alternatives_not_selected": [
            {
                "entity_id": "waveparticle-duality",
                "reason": "Broader and less concrete; selecting the experiment makes added mechanism easier to judge.",
            },
            {
                "entity_id": "uncertainty-principle",
                "reason": "Its adjacent section is separate and it has no accepted direct parent relationship.",
            },
            {
                "entity_id": "quantum-mechanics",
                "reason": "Too broad for one bounded child and likely to restate the full parent.",
            },
        ],
    }


def freeze_source_scope(parent: KnowledgeModel) -> FrozenSourceScope:
    source_hash = hashlib.sha256(parent.document.text.encode()).hexdigest()
    if source_hash != EXPECTED_PARENT_SOURCE_SHA256:
        raise ValidationError(
            f"trusted parent source hash changed: expected {EXPECTED_PARENT_SOURCE_SHA256}, got {source_hash}"
        )
    if parent.document.text.count(SCOPE_START_MARKER) != 1 or parent.document.text.count(SCOPE_END_MARKER) != 1:
        raise ValidationError("semantic-depth scope markers must each occur exactly once")
    start = parent.document.text.index(SCOPE_START_MARKER)
    end = parent.document.text.index(SCOPE_END_MARKER, start)
    text = parent.document.text[start:end]
    scope = FrozenSourceScope(
        parent_document_id=parent.document.id,
        start_char=start,
        end_char=end,
        text=text,
        sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
    if scope.sha256 != EXPECTED_SCOPE_SHA256:
        raise ValidationError("frozen semantic-depth source scope no longer matches its accepted hash")
    return scope


def child_symbol_table(parent: KnowledgeModel) -> SymbolTable:
    by_id = {item.id: item for item in parent.entities}
    missing = sorted(set(CHILD_SYMBOL_IDS) - set(by_id))
    if missing:
        raise ValidationError(f"trusted parent is missing frozen child symbols: {missing}")
    return SymbolTable(
        tuple(by_id[item] for item in CHILD_SYMBOL_IDS),
        {
            "spec": "SPEC-020",
            "selection": "OFFLINE_SOURCE_SECTION_AND_PARENT_SEMANTICS",
            "parent_symbol_count": len(parent.entities),
            "child_symbol_count": len(CHILD_SYMBOL_IDS),
            "entity_minting": False,
        },
    )


def build_parent_focus_representation(parent: KnowledgeModel) -> RepresentationModel:
    relationship = next(
        (item for item in parent.relationships if item.id == PARENT_RELATIONSHIP_ID), None
    )
    if relationship is None or relationship.relationship_type is not RelationshipType.CAUSES:
        raise ValidationError("trusted parent focus relationship is unavailable or changed")
    structure = DetectedStructure(
        id="structure-causal-path-spec020-parent-focus",
        structure_type=StructureType.CAUSAL_PATH,
        entity_ids=(relationship.source_entity_id, relationship.target_entity_id),
        relationship_ids=(relationship.id,),
        relationship_types=(relationship.relationship_type,),
        metadata={
            "edge_count": 1,
            "supporting_relationship_ids_by_edge": [[relationship.id]],
            "selection": "TRUSTED_PARENT_FOCUS_RELATIONSHIP",
        },
    )
    structures = DetectedStructureSet(
        source_document_id=parent.document.id,
        structures=(structure,),
        detector_version="spec-020-parent-focus-v1",
        metadata={"source": "accepted SPEC-013 parent relationship"},
    )
    return with_layouts(RepresentationBuilder().build(
        parent,
        structures,
        presentation_metadata={
            "domain": "quantum_mechanics",
            "title": "Double-slit experiment — parent context",
        },
    ))


def compile_trusted_child(
    *,
    parent: KnowledgeModel,
    scope: FrozenSourceScope,
    symbols: SymbolTable,
    assertions: GroundedAssertionSet,
    canonicalization: CanonicalizationProposal,
) -> tuple[KnowledgeModel, DetectedStructureSet, RepresentationModel, dict[str, Any]]:
    parent_before = model_hash(parent)
    if assertions.metadata.get("source_scope_sha256") not in (None, scope.sha256):
        raise ValidationError("assertion metadata references a different frozen source scope")
    document = scope.as_document(parent)
    for assertion in assertions.assertions:
        if not set(assertion.participant_entity_ids).issubset(symbols.ids):
            raise ValidationError("child assertion references an entity outside frozen child symbols")
        for evidence in assertion.evidence:
            evidence.validate_against(document)
    if not any(FOCUS_ENTITY_ID in item.participant_entity_ids for item in assertions.assertions):
        raise ValidationError("child assertions do not resolve the frozen focus")

    result = compile_assertion_semantics(document, symbols, assertions, canonicalization)
    child = result.model
    if {item.id for item in child.entities} != symbols.ids:
        raise ValidationError("child compilation changed the frozen child symbol inventory")
    if any(item.origin is not Origin.SOURCE for item in (*child.claims, *child.relationships, *child.propositions)):
        raise ValidationError("semantic-depth child must remain entirely source-grounded")
    if KnowledgeModel.from_dict(child.to_dict()) != child:
        raise ValidationError("semantic-depth child KnowledgeModel failed round-trip")
    structures = StructureDetector().detect(child)
    representation = with_layouts(RepresentationBuilder().build(
        child,
        structures,
        presentation_metadata={
            "domain": "quantum_mechanics",
            "title": "Double-slit experiment — deeper resolution",
        },
    ))
    if not representation.representations:
        raise ValidationError("trusted child has no detected structure suitable for learning representation")
    if not any(
        any(node.entity_id == FOCUS_ENTITY_ID for node in item.nodes)
        for item in representation.representations
    ):
        raise ValidationError("trusted child representations do not retain the parent focus")
    if model_hash(parent) != parent_before:
        raise AssertionError("semantic-depth compilation mutated the trusted parent")

    evidence = [
        span
        for item in (*child.claims, *child.relationships, *child.propositions)
        for span in item.evidence
    ]
    diagnostics = {
        "trusted_gate": {
            "source_evidence_exact": all(
                span.quote == document.text[span.start_char:span.end_char] for span in evidence
            ),
            "participant_entity_integrity": True,
            "canonical_semantic_validation": True,
            "proposition_validation": True,
            "no_unknown_endpoints_or_roles": True,
            "no_silent_entity_minting": True,
            "knowledge_model_round_trip": True,
            "focus_retained": True,
        },
        "counts": {
            "assertions": len(assertions.assertions),
            "relationships": len(child.relationships),
            "propositions": len(child.propositions),
            "claims": len(child.claims),
            "uncompiled_assertions": len(canonicalization.uncompiled_assertions),
            "evidence_spans": len(evidence),
            "structures": len(structures.structures),
            "representations": len(representation.representations),
        },
    }
    if not all(diagnostics["trusted_gate"].values()):
        raise ValidationError("semantic-depth child failed trusted admission")
    return child, structures, representation, diagnostics


def _navigation_positions(parent: KnowledgeModel) -> dict[str, dict[str, float]]:
    result = {}
    for index, entity in enumerate(sorted(parent.entities, key=lambda item: item.id)):
        column, row = index % 6, index // 6
        result[entity.id] = {"x": 200.0 + column * 360.0, "y": 180.0 + row * 190.0}
    return result


def build_depth_workspace_fixture(
    parent: KnowledgeModel,
    parent_representation: RepresentationModel,
    child_representation: RepresentationModel,
) -> dict[str, Any]:
    positions = _navigation_positions(parent)
    nodes = [{
        "entity_id": entity.id,
        "label": entity.name,
        "description": entity.description,
        "entity_type": entity.entity_type.value,
        "domain_id": "quantum_mechanics",
        "world": positions[entity.id],
        "has_deeper_resolution": entity.id == FOCUS_ENTITY_ID,
    } for entity in sorted(parent.entities, key=lambda item: item.id)]
    edges = []
    routes = []
    adjacency = {item["entity_id"]: [] for item in nodes}
    for relationship in sorted(parent.relationships, key=lambda item: item.id):
        edge_key = f"parent-{relationship.id}"
        edges.append({
            "edge_key": edge_key,
            "source_entity_id": relationship.source_entity_id,
            "target_entity_id": relationship.target_entity_id,
            "relationship_type": relationship.relationship_type.value,
            "relationship_label": relationship.relationship_type.value.replace("_", " "),
            "relationship_ids": [relationship.id],
            "domain_id": "quantum_mechanics",
        })
        routes.append({
            "edge_key": edge_key,
            **_route(positions[relationship.source_entity_id], positions[relationship.target_entity_id]),
        })
        adjacency[relationship.source_entity_id].append(relationship.target_entity_id)
        adjacency[relationship.target_entity_id].append(relationship.source_entity_id)
    for value in adjacency.values():
        value.sort()

    fixture = {
        "version": SEMANTIC_DEPTH_VERSION,
        "fixture_status": "TRUSTED_SPEC_013_PARENT_WITH_ONE_ADMITTED_SOURCE_BOUNDED_CHILD",
        "domains": [{
            "domain_id": "quantum_mechanics",
            "label": "Quantum mechanics",
            "world_region": {"x": 70.0, "y": 70.0, "width": 2200.0, "height": 1340.0},
            "learning_model": parent_representation.to_dict(),
        }],
        "navigation": {
            "nodes": nodes,
            "edges": edges,
            "adjacency": adjacency,
            "world": {
                "bounds": WORLD_BOUNDS,
                "layout_strategy": "DETERMINISTIC_PARENT_SYMBOL_GRID",
                "node_positions_stable": True,
                "routes": routes,
            },
            "camera": {
                "initial": INITIAL_CAMERA,
                "viewport": VIEWPORT,
                "transform": "SVG_VIEWBOX_WORLD_TO_VIEWPORT",
                "zoom": {
                    "kind": "GEOMETRIC_ONLY",
                    "min_scale": 0.55,
                    "max_scale": 2.25,
                    "initial_scale": 1.0,
                    "pointer_centered": True,
                    "wheel_sensitivity": 0.0015,
                },
                "focus_animation_ms": 280,
            },
        },
        "workspace": {
            "default_domain_id": "quantum_mechanics",
            "default_representation_index": 0,
            "default_focused_entity_id": FOCUS_ENTITY_ID,
            "shared_focus": "STABLE_PARENT_ENTITY_ID",
            "camera_independent_from_semantic_focus": True,
        },
        "semantic_depth": {
            "focus_entity_id": FOCUS_ENTITY_ID,
            "focus_label": FOCUS_LABEL,
            "levels": ["PARENT", "CHILD"],
            "default_level": "PARENT",
            "maximum_child_depth": 1,
            "child_learning_model": child_representation.to_dict(),
            "navigation_world_replaced": False,
            "geometric_zoom_independent": True,
        },
    }
    validate_depth_workspace_fixture(fixture)
    return fixture


def validate_depth_workspace_fixture(fixture: dict[str, Any]) -> None:
    nodes = fixture["navigation"]["nodes"]
    parent_ids = {item["entity_id"] for item in nodes}
    if len(parent_ids) != len(nodes):
        raise ValidationError("semantic-depth parent navigation IDs must be unique")
    child = fixture["semantic_depth"]["child_learning_model"]
    child_ids = {
        node["entity_id"]
        for representation in child["representations"]
        for node in representation["nodes"]
    }
    if not child_ids.issubset(parent_ids):
        raise ValidationError("semantic-depth child may only reuse parent entity IDs")
    if FOCUS_ENTITY_ID not in child_ids or FOCUS_ENTITY_ID not in parent_ids:
        raise ValidationError("semantic-depth focus must remain visible across resolutions")
    if fixture["semantic_depth"]["maximum_child_depth"] != 1:
        raise ValidationError("SPEC-020 permits exactly one child level")
    if fixture["semantic_depth"]["navigation_world_replaced"]:
        raise ValidationError("semantic depth must not replace the parent navigation world")


@dataclass(frozen=True, slots=True)
class DepthWorkspaceState:
    camera: CameraState
    level: Literal["PARENT", "CHILD"] = "PARENT"
    representation_index: int = 0
    focused_entity_id: str = FOCUS_ENTITY_ID
    focused_relationship_id: str | None = None


def switch_semantic_depth(state: DepthWorkspaceState, level: Literal["PARENT", "CHILD"]) -> DepthWorkspaceState:
    if level not in ("PARENT", "CHILD"):
        raise ValidationError("semantic depth level must be PARENT or CHILD")
    return replace(
        state,
        level=level,
        representation_index=0,
        focused_entity_id=FOCUS_ENTITY_ID,
        focused_relationship_id=None,
    )


def depth_camera_invariant(before: DepthWorkspaceState, after: DepthWorkspaceState) -> bool:
    return before.camera == after.camera
