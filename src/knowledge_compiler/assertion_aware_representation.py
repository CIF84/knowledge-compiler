"""Deterministic, presentation-only projection of grounded assertions.

This module deliberately sits downstream of the semantic IR.  Assertion
participants become non-semantic presentation attachments; they never become
pairwise domain relationships.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .assertion_compilation import GroundedAssertionSet, SourceAssertion
from .models import Claim, KnowledgeModel, Proposition, Relationship, ValidationError
from .staged_compilation import SymbolTable
from .structures import DetectedStructureSet


ASSERTION_AWARE_REPRESENTATION_VERSION = "spec-016-v1"
TIER_LABELS = {
    "CANONICAL_RELATIONSHIP": "Established relationship",
    "STRUCTURED_PROPOSITION": "Structured condition/event",
    "GROUNDED_ASSERTION": "Source-backed explanation",
}
FROZEN_INPUT_SHA256 = {
    "symbol-table.json": "07e79ff8e0d59c62ef181fe4ca7cec7aec9fcd32452b3c734c99482d288aaa08",
    "grounded-assertions.json": "448b746c14ce9cb72f35989b7e6594f5325e91e6cf817b2fcca087a79b44d4b0",
    "parent.knowledge.json": "100e3581ada4e2a4b0c293ce94138592382e5e8233774203a3e3c93683122627",
    "parent.structures.json": "d4b3445c78e16021058ebe8d2d1d51c67d3a20b841e52faeefddc1a48599d23c",
    "parent.representation.json": "75052312fb871ba344752b5c2d16ea4c8d2b44a85049e326dfc9f1e7c39c0638",
    "canonicalization-result.json": "e574f55ac80313d50d3bff0faca0b176016c718635aa1213aee2451ccf4b643a",
}


def default_spec013_assertion_directory() -> Path:
    return (
        Path(__file__).parents[2]
        / "examples"
        / "evaluations"
        / "spec-013-assertion-first-semantic-compilation-20260904"
    )


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _span_dicts(item: SourceAssertion | Claim | Relationship | Proposition) -> list[dict[str, Any]]:
    return [asdict(span) for span in item.evidence]


def _matching_assertion_id(
    row: dict[str, Any],
    assertions: dict[str, SourceAssertion],
) -> str:
    assertion_id = row.get("assertion_id")
    if assertion_id not in assertions:
        raise ValidationError(f"canonicalization references unknown assertion {assertion_id!r}")
    return assertion_id


def load_frozen_spec013_inputs(input_dir: Path) -> dict[str, Any]:
    """Load and cross-check the six accepted SPEC-013 inputs fail-closed."""
    input_dir = input_dir.resolve()
    manifest = []
    raw: dict[str, Any] = {}
    for name, expected in FROZEN_INPUT_SHA256.items():
        path = input_dir / name
        actual = _sha256(path)
        if actual != expected:
            raise ValidationError(
                f"frozen SPEC-013 input hash mismatch for {name}: expected {expected}, got {actual}"
            )
        raw[name] = json.loads(path.read_text(encoding="utf-8"))
        manifest.append({"filename": name, "sha256": actual, "byte_count": path.stat().st_size})

    model = KnowledgeModel.from_dict(raw["parent.knowledge.json"])
    table = SymbolTable.from_dict(raw["symbol-table.json"])
    assertions = GroundedAssertionSet.from_dict(raw["grounded-assertions.json"], model.document)
    structures = DetectedStructureSet.from_dict(raw["parent.structures.json"])
    structures.validate_against(model)
    control = raw["parent.representation.json"]
    canonicalization = raw["canonicalization-result.json"]

    if table.to_dict()["entities"] != [asdict(item) for item in model.entities]:
        raise ValidationError("frozen symbol table and accepted parent entity inventory differ")
    if control.get("document_id") != model.document.id:
        raise ValidationError("control representation references a different document")
    if canonicalization.get("outcome") != "SUCCESS":
        raise ValidationError("accepted canonicalization result is not successful")

    assertion_by_id = {item.id: item for item in assertions.assertions}
    normalized = canonicalization.get("normalized_proposal", {})
    rows_by_tier: dict[str, dict[str, dict[str, Any]]] = {}
    for key in ("relationships", "propositions", "claims", "uncompiled_assertions"):
        rows = normalized.get(key)
        if not isinstance(rows, list):
            raise ValidationError(f"canonicalization normalized_proposal.{key} must be an array")
        rows_by_tier[key] = {
            _matching_assertion_id(row, assertion_by_id): row for row in rows
        }
        if len(rows_by_tier[key]) != len(rows):
            raise ValidationError(f"canonicalization has duplicate assertion use in {key}")
    accounted = set().union(*(set(value) for value in rows_by_tier.values()))
    if accounted != assertions.ids:
        raise ValidationError("canonicalization does not account for every grounded assertion exactly once")
    if sum(len(value) for value in rows_by_tier.values()) != len(accounted):
        raise ValidationError("canonicalization assigns an assertion to more than one semantic tier")

    def relationship_match(row: dict[str, Any], item: Relationship) -> bool:
        return all((
            row["source_entity_id"] == item.source_entity_id,
            row["target_entity_id"] == item.target_entity_id,
            row["relationship_type"] == item.relationship_type.value,
            row["statement"] == item.statement,
            float(row["confidence"]) == item.confidence,
        ))

    for assertion_id, row in rows_by_tier["relationships"].items():
        matches = [item for item in model.relationships if relationship_match(row, item)]
        if len(matches) != 1 or _span_dicts(matches[0]) != _span_dicts(assertion_by_id[assertion_id]):
            raise ValidationError(f"canonical relationship for {assertion_id} differs from accepted parent")
    for assertion_id, row in rows_by_tier["claims"].items():
        matches = [
            item for item in model.claims
            if item.statement == row["statement"] and item.confidence == float(row["confidence"])
        ]
        if len(matches) != 1 or _span_dicts(matches[0]) != _span_dicts(assertion_by_id[assertion_id]):
            raise ValidationError(f"claim for {assertion_id} differs from accepted parent")
    for assertion_id, row in rows_by_tier["propositions"].items():
        matches = [item for item in model.propositions if item.statement == row["statement"]]
        if len(matches) != 1 or _span_dicts(matches[0]) != _span_dicts(assertion_by_id[assertion_id]):
            raise ValidationError(f"proposition for {assertion_id} differs from accepted parent")
    if len(rows_by_tier["relationships"]) != len(model.relationships):
        raise ValidationError("canonical relationship count differs from accepted parent")
    if len(rows_by_tier["propositions"]) != len(model.propositions):
        raise ValidationError("proposition count differs from accepted parent")
    if len(rows_by_tier["claims"]) != len(model.claims):
        raise ValidationError("claim count differs from accepted parent")

    return {
        "input_dir": input_dir,
        "manifest": manifest,
        "model": model,
        "symbol_table": table,
        "assertions": assertions,
        "structures": structures,
        "control": control,
        "canonicalization": canonicalization,
        "canonical_rows": rows_by_tier,
    }


class AssertionAwareRepresentationBuilder:
    """Build a deterministic orientation model without changing semantic truth."""

    max_initial_concepts = 6
    max_initial_assertions = 6

    def build(self, frozen: dict[str, Any]) -> dict[str, Any]:
        model: KnowledgeModel = frozen["model"]
        assertion_set: GroundedAssertionSet = frozen["assertions"]
        structures: DetectedStructureSet = frozen["structures"]
        canonical_rows = frozen["canonical_rows"]
        entities = {item.id: item for item in model.entities}
        assertions = {item.id: item for item in assertion_set.assertions}

        assertion_ids_by_entity = {entity_id: [] for entity_id in entities}
        attachments = []
        for assertion in sorted(assertions.values(), key=lambda item: item.id):
            for entity_id in assertion.participant_entity_ids:
                if entity_id not in entities:
                    raise ValidationError(f"assertion {assertion.id} references unknown symbol {entity_id}")
                assertion_ids_by_entity[entity_id].append(assertion.id)
                attachments.append({
                    "assertion_id": assertion.id,
                    "entity_id": entity_id,
                    "attachment_type": "ASSERTION_PARTICIPANT",
                    "presentation_only": True,
                    "semantic_relationship_created": False,
                })

        relationship_ids_by_entity = {entity_id: [] for entity_id in entities}
        relationship_cards = []
        for item in sorted(model.relationships, key=lambda value: value.id):
            relationship_ids_by_entity[item.source_entity_id].append(item.id)
            relationship_ids_by_entity[item.target_entity_id].append(item.id)
            assertion_id = next(
                key for key, row in canonical_rows["relationships"].items()
                if row["source_entity_id"] == item.source_entity_id
                and row["target_entity_id"] == item.target_entity_id
                and row["relationship_type"] == item.relationship_type.value
                and row["statement"] == item.statement
            )
            relationship_cards.append({
                "id": item.id,
                "tier": "CANONICAL_RELATIONSHIP",
                "tier_label": TIER_LABELS["CANONICAL_RELATIONSHIP"],
                "source_entity_id": item.source_entity_id,
                "relationship_type": item.relationship_type.value,
                "target_entity_id": item.target_entity_id,
                "statement": item.statement,
                "evidence": _span_dicts(item),
                "origin": item.origin.value,
                "supporting_assertion_id": assertion_id,
            })

        proposition_ids_by_entity = {entity_id: [] for entity_id in entities}
        proposition_cards = []
        for item in sorted(model.propositions, key=lambda value: value.id):
            for binding in item.role_bindings:
                proposition_ids_by_entity[binding.entity_id].append(item.id)
            assertion_id = next(
                key for key, row in canonical_rows["propositions"].items()
                if row["statement"] == item.statement
            )
            proposition_cards.append({
                "id": item.id,
                "tier": "STRUCTURED_PROPOSITION",
                "tier_label": TIER_LABELS["STRUCTURED_PROPOSITION"],
                "proposition_type": item.proposition_type.value,
                "statement": item.statement,
                "role_bindings": [asdict(binding) for binding in item.role_bindings],
                "relationship_type": item.relationship_type.value,
                "comparison_operator": item.comparison_operator.value if item.comparison_operator else None,
                "evidence": _span_dicts(item),
                "origin": item.origin.value,
                "supporting_assertion_id": assertion_id,
            })

        structure_members = {
            entity_id for structure in structures.structures for entity_id in structure.entity_ids
        }
        relationship_degree = {key: len(value) for key, value in relationship_ids_by_entity.items()}
        proposition_degree = {key: len(value) for key, value in proposition_ids_by_entity.items()}
        assertion_degree = {key: len(value) for key, value in assertion_ids_by_entity.items()}
        salience = {
            entity_id: assertion_degree[entity_id] * 4
            + relationship_degree[entity_id] * 3
            + proposition_degree[entity_id] * 3
            + (2 if entity_id in structure_members else 0)
            for entity_id in entities
        }
        ranked_entities = sorted(entities, key=lambda key: (-salience[key], key))
        initial_entities = ranked_entities[: self.max_initial_concepts]

        relationship_assertions = canonical_rows["relationships"]
        proposition_assertions = canonical_rows["propositions"]
        claim_assertions = canonical_rows["claims"]
        assertion_cards = []
        for item in sorted(assertions.values(), key=lambda value: value.id):
            if item.id in relationship_assertions:
                realization = "SUPPORTS_CANONICAL_RELATIONSHIP"
                semantic_item_id = next(
                    card["id"] for card in relationship_cards
                    if card["supporting_assertion_id"] == item.id
                )
            elif item.id in proposition_assertions:
                realization = "SUPPORTS_STRUCTURED_PROPOSITION"
                semantic_item_id = next(
                    card["id"] for card in proposition_cards
                    if card["supporting_assertion_id"] == item.id
                )
            elif item.id in claim_assertions:
                realization = "PRESERVED_AS_CLAIM"
                semantic_item_id = next(
                    claim.id for claim in model.claims
                    if claim.statement == claim_assertions[item.id]["statement"]
                )
            else:
                realization = "PRESERVED_AS_GROUNDED_ASSERTION"
                semantic_item_id = None
            assertion_cards.append({
                "id": item.id,
                "tier": "GROUNDED_ASSERTION",
                "tier_label": TIER_LABELS["GROUNDED_ASSERTION"],
                "statement": item.statement,
                "participant_entity_ids": list(item.participant_entity_ids),
                "evidence": _span_dicts(item),
                "origin": item.origin.value,
                "semantic_realization": realization,
                "semantic_item_id": semantic_item_id,
            })

        assertion_score = {
            item.id: sum(salience[key] for key in item.participant_entity_ids)
            + len(item.participant_entity_ids)
            for item in assertions.values()
        }
        initial_assertions = []
        for entity_id in initial_entities:
            choices = sorted(
                assertion_ids_by_entity[entity_id],
                key=lambda key: (-assertion_score[key], key),
            )
            choice = next((key for key in choices if key not in initial_assertions), None)
            if choice is not None:
                initial_assertions.append(choice)
        initial_assertions = initial_assertions[: self.max_initial_assertions]

        concepts = [{
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "entity_type": item.entity_type.value,
            "aliases": list(item.aliases),
            "assertion_degree": assertion_degree[item.id],
            "canonical_relationship_degree": relationship_degree[item.id],
            "proposition_degree": proposition_degree[item.id],
            "structure_member": item.id in structure_members,
            "presentation_salience_score": salience[item.id],
            "initially_visible": item.id in initial_entities,
        } for item in sorted(entities.values(), key=lambda value: value.id)]

        neighborhoods = []
        for entity_id in ranked_entities:
            if not (
                assertion_ids_by_entity[entity_id]
                or relationship_ids_by_entity[entity_id]
                or proposition_ids_by_entity[entity_id]
            ):
                continue
            neighborhoods.append({
                "id": f"neighborhood-{entity_id}",
                "anchor_entity_id": entity_id,
                "assertion_ids": sorted(assertion_ids_by_entity[entity_id]),
                "canonical_relationship_ids": sorted(relationship_ids_by_entity[entity_id]),
                "proposition_ids": sorted(proposition_ids_by_entity[entity_id]),
                "presentation_only": True,
                "semantic_grouping_created": False,
                "size": 1 + len(assertion_ids_by_entity[entity_id])
                + len(relationship_ids_by_entity[entity_id])
                + len(proposition_ids_by_entity[entity_id]),
            })

        overview_layout = [{
            "entity_id": entity_id,
            "column": index % 3,
            "row": index // 3,
            "x": (index % 3) * 384,
            "y": (index // 3) * 284,
            "width": 360,
            "height": 260,
        } for index, entity_id in enumerate(initial_entities)]

        representation = {
            "builder_version": ASSERTION_AWARE_REPRESENTATION_VERSION,
            "document_id": model.document.id,
            "title": "Quantum mechanics — assertion-aware orientation",
            "truth_boundary": {
                "semantic_source": "accepted SPEC-013 artifacts",
                "presentation_only_projection": True,
                "assertion_participation_is_not_a_relationship": True,
                "new_semantic_truth_created": False,
            },
            "tier_labels": TIER_LABELS,
            "salience_heuristic": {
                "formula": "4*assertion_degree + 3*canonical_relationship_degree + 3*proposition_degree + 2*structure_membership",
                "purpose": "deterministic presentation ordering only; not universal semantic importance",
                "tie_breaker": "lexicographic entity ID",
            },
            "density_limits": {
                "maximum_initial_concepts": self.max_initial_concepts,
                "maximum_initial_assertions": self.max_initial_assertions,
                "all_material_available_after_interaction": True,
            },
            "overview": {
                "initial_entity_ids": initial_entities,
                "initial_assertion_ids": initial_assertions,
                "layout": overview_layout,
            },
            "concepts": concepts,
            "canonical_relationships": relationship_cards,
            "structured_propositions": proposition_cards,
            "grounded_assertions": assertion_cards,
            "assertion_participant_attachments": sorted(
                attachments, key=lambda item: (item["assertion_id"], item["entity_id"])
            ),
            "neighborhoods": neighborhoods,
        }
        self.validate(representation, frozen)
        return representation

    def validate(self, value: dict[str, Any], frozen: dict[str, Any]) -> None:
        model: KnowledgeModel = frozen["model"]
        assertions: GroundedAssertionSet = frozen["assertions"]
        expected_entities = {item.id for item in model.entities}
        if {item["id"] for item in value["concepts"]} != expected_entities:
            raise ValidationError("assertion-aware projection changed the symbol inventory")
        expected_relationships = [
            (item.id, item.source_entity_id, item.relationship_type.value, item.target_entity_id)
            for item in sorted(model.relationships, key=lambda item: item.id)
        ]
        actual_relationships = [
            (item["id"], item["source_entity_id"], item["relationship_type"], item["target_entity_id"])
            for item in value["canonical_relationships"]
        ]
        if actual_relationships != expected_relationships:
            raise ValidationError("assertion-aware projection changed canonical relationships")
        if {item["id"] for item in value["structured_propositions"]} != {
            item.id for item in model.propositions
        }:
            raise ValidationError("assertion-aware projection changed structured propositions")
        if {item["id"] for item in value["grounded_assertions"]} != assertions.ids:
            raise ValidationError("assertion-aware projection changed grounded assertions")
        expected_attachments = {
            (item.id, entity_id)
            for item in assertions.assertions for entity_id in item.participant_entity_ids
        }
        actual_attachments = {
            (item["assertion_id"], item["entity_id"])
            for item in value["assertion_participant_attachments"]
        }
        if actual_attachments != expected_attachments:
            raise ValidationError("assertion participant presentation attachments are incomplete")
        if any(
            not item["presentation_only"] or item["semantic_relationship_created"]
            for item in value["assertion_participant_attachments"]
        ):
            raise ValidationError("assertion attachments must be explicitly non-semantic")
        if any(item["tier_label"] != TIER_LABELS[item["tier"]] for key in (
            "canonical_relationships", "structured_propositions", "grounded_assertions"
        ) for item in value[key]):
            raise ValidationError("semantic tier labels are incomplete")
        if len(value["overview"]["initial_entity_ids"]) > self.max_initial_concepts:
            raise ValidationError("initial concept density exceeds its bound")
        if len(value["overview"]["initial_assertion_ids"]) > self.max_initial_assertions:
            raise ValidationError("initial assertion density exceeds its bound")
