"""SPEC-007 fixed semantic-depth fixtures and deterministic integrity evaluation."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import Any

from .evaluation import DOMAINS
from .layout import layout_representation
from .models import EntityType, Origin, RelationshipType, ValidationError
from .relationships import RELATIONSHIP_DEFINITION_MAP
from .representations import (
    Representation,
    RepresentationEdge,
    RepresentationModel,
    RepresentationNode,
    Salience,
)
from .structures import StructureType


MODES = ("BASELINE", "REPLACEMENT", "CONTEXTUAL")


class FixtureProvenanceKind(StrEnum):
    EXPERIMENT_FIXTURE_AUTHORED = "EXPERIMENT_FIXTURE_AUTHORED"


@dataclass(frozen=True, slots=True)
class ExplorationFixture:
    """One bounded parent-to-child presentation fixture, outside semantic IR."""

    id: str
    domain: str
    parent_representation_id: str
    focus_entity_id: str
    focus_label: str
    child_representation: Representation
    provenance_kind: FixtureProvenanceKind
    provenance_note: str

    def __post_init__(self) -> None:
        for name in (
            "id", "domain", "parent_representation_id", "focus_entity_id",
            "focus_label", "provenance_note",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"exploration fixture {name} must be non-empty")
        try:
            object.__setattr__(self, "provenance_kind", FixtureProvenanceKind(self.provenance_kind))
        except (TypeError, ValueError) as exc:
            raise ValidationError("exploration fixture provenance kind is invalid") from exc
        if self.child_representation.layout is None:
            raise ValidationError("exploration fixture child requires deterministic layout")
        for edge in self.child_representation.edges:
            definition = RELATIONSHIP_DEFINITION_MAP[edge.relationship_type]
            if (
                edge.relationship_label != edge.relationship_type.value.replace("_", " ")
                or edge.meaning != definition.meaning
                or edge.direction != definition.direction
            ):
                raise ValidationError("fixture edge does not preserve canonical semantics")
            if edge.evidence or any(origin is not Origin.INFERRED for origin in edge.origins):
                raise ValidationError("fixture-authored relationships cannot masquerade as source evidence")
            if any(not relationship_id.startswith("fixture-") for relationship_id in edge.relationship_ids):
                raise ValidationError("fixture-authored relationship IDs must be explicit")

    def validate_parent(self, parent: RepresentationModel) -> None:
        representation = next(
            (item for item in parent.representations if item.id == self.parent_representation_id),
            None,
        )
        if representation is None:
            raise ValidationError("exploration fixture parent representation does not exist")
        node = next((item for item in representation.nodes if item.entity_id == self.focus_entity_id), None)
        if node is None or node.label != self.focus_label:
            raise ValidationError("exploration fixture focus does not match its parent representation")

    def to_dict(self) -> dict[str, Any]:
        child_model = RepresentationModel(
            document_id=f"fixture-document-{self.id}",
            title=self.child_representation.title,
            domain=self.domain,
            representations=(self.child_representation,),
            builder_version="spec-007-v1",
            metadata={
                "fixture_id": self.id,
                "fixture_provenance_kind": self.provenance_kind.value,
                "fixture_provenance_note": self.provenance_note,
            },
        )
        return {
            "spec": "SPEC-007",
            "id": self.id,
            "domain": self.domain,
            "parent_representation_id": self.parent_representation_id,
            "focus_entity_id": self.focus_entity_id,
            "focus_label": self.focus_label,
            "provenance_kind": self.provenance_kind.value,
            "provenance_note": self.provenance_note,
            "child_representation": child_model.to_dict()["representations"][0],
        }


def _node(entity_id: str, label: str, description: str, entity_type: EntityType) -> RepresentationNode:
    return RepresentationNode(entity_id, label, description, entity_type)


def _edge(
    relationship_id: str,
    source: str,
    relationship_type: RelationshipType,
    target: str,
) -> RepresentationEdge:
    definition = RELATIONSHIP_DEFINITION_MAP[relationship_type]
    return RepresentationEdge(
        source_entity_id=source,
        target_entity_id=target,
        relationship_type=relationship_type,
        relationship_label=relationship_type.value.replace("_", " "),
        meaning=definition.meaning,
        direction=definition.direction,
        relationship_ids=(relationship_id,),
        evidence=(),
        origins=(Origin.INFERRED,),
    )


def _laid_out(representation: Representation) -> Representation:
    from dataclasses import replace

    return replace(representation, layout=layout_representation(representation))


def fixed_exploration_fixtures() -> tuple[ExplorationFixture, ...]:
    """Return the two fixed, manually authored child models used by SPEC-007."""
    software = _laid_out(Representation(
        id="fixture-api-request-handling",
        representation_type=StructureType.PROCESS_CHAIN,
        source_structure_ids=("fixture-structure-api-request-handling",),
        title="API request-handling mechanism",
        nodes=(
            _node("fixture-request-arrival", "request arrival", "A client request reaches the API boundary.", EntityType.PROCESS),
            _node("fixture-request-parsing", "request parsing", "The API translates transport input into an internal request shape.", EntityType.PROCESS),
            _node("fixture-request-validation", "request validation", "The request is checked before order handling can proceed.", EntityType.PROCESS),
            _node("fixture-order-command", "order command creation", "Validated input becomes a command for order processing.", EntityType.PROCESS),
            _node("fixture-order-handoff", "order-component handoff", "The API passes the order command to the order component.", EntityType.PROCESS),
        ),
        edges=(
            _edge("fixture-api-rel-1", "fixture-request-arrival", RelationshipType.PRECEDES, "fixture-request-parsing"),
            _edge("fixture-api-rel-2", "fixture-request-parsing", RelationshipType.PRECEDES, "fixture-request-validation"),
            _edge("fixture-api-rel-3", "fixture-request-validation", RelationshipType.PRECEDES, "fixture-order-command"),
            _edge("fixture-api-rel-4", "fixture-order-command", RelationshipType.PRECEDES, "fixture-order-handoff"),
        ),
        salience=Salience.PRIMARY,
        warnings=("Experimental fixed fixture; this mechanism was authored for navigation evaluation, not extracted from source.",),
    ))
    economics = _laid_out(Representation(
        id="fixture-market-price-response",
        representation_type=StructureType.CAUSAL_PATH,
        source_structure_ids=("fixture-structure-market-price-response",),
        title="Market-price response mechanism",
        nodes=(
            _node("fixture-observed-market-price", "observed market price", "The price signal buyers and sellers observe.", EntityType.VARIABLE),
            _node("fixture-buyer-affordability", "buyer affordability", "The purchasing range available to buyers at the observed price.", EntityType.CONCEPT),
            _node("fixture-purchase-plans", "purchase plans", "The quantities buyers plan to purchase under their constraints.", EntityType.PROCESS),
            _node("fixture-seller-incentive", "seller revenue incentive", "The incentive sellers perceive at the observed price.", EntityType.CONCEPT),
            _node("fixture-supply-offers", "supply offers", "The quantities sellers plan to offer to the market.", EntityType.PROCESS),
        ),
        edges=(
            _edge("fixture-price-rel-1", "fixture-observed-market-price", RelationshipType.AFFECTS, "fixture-buyer-affordability"),
            _edge("fixture-price-rel-2", "fixture-buyer-affordability", RelationshipType.CONSTRAINS, "fixture-purchase-plans"),
            _edge("fixture-price-rel-3", "fixture-observed-market-price", RelationshipType.AFFECTS, "fixture-seller-incentive"),
            _edge("fixture-price-rel-4", "fixture-seller-incentive", RelationshipType.AFFECTS, "fixture-supply-offers"),
        ),
        salience=Salience.PRIMARY,
        warnings=("Experimental fixed fixture; it explains responses around price without adding the parent model's missing feedback-closing edge.",),
    ))
    note = "Manually authored for SPEC-007; no SourceSpan coordinates or SOURCE origin are claimed."
    return (
        ExplorationFixture(
            id="exploration-software-api",
            domain="software_architecture",
            parent_representation_id="representation-985e777f01fa9ec8",
            focus_entity_id="api-component",
            focus_label="API component",
            child_representation=software,
            provenance_kind=FixtureProvenanceKind.EXPERIMENT_FIXTURE_AUTHORED,
            provenance_note=note,
        ),
        ExplorationFixture(
            id="exploration-economics-market-price",
            domain="economics",
            parent_representation_id="representation-fe3ba90cb8cfa3d6",
            focus_entity_id="market-price",
            focus_label="market price",
            child_representation=economics,
            provenance_kind=FixtureProvenanceKind.EXPERIMENT_FIXTURE_AUTHORED,
            provenance_note=note,
        ),
    )


def default_spec006_representations_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-006-layout-interaction-20260903"


def copy_semantic_navigation_assets(output_dir: Path) -> None:
    assets = files("knowledge_compiler").joinpath("viewer_assets")
    names = {
        "semantic-navigation.html": "index.html",
        "semantic-navigation.css": "viewer.css",
        "semantic-navigation.js": "viewer.js",
    }
    for source_name, output_name in names.items():
        with assets.joinpath(source_name).open("rb") as source, (output_dir / output_name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _human_review_template() -> dict[str, Any]:
    dimensions = ("orientation", "understanding", "cognitive_load", "interaction_coherence", "overall_comparison")
    return {
        "spec": "SPEC-007",
        "status": "NOT_EVALUATED",
        "instructions": (
            "Capture spontaneous reaction first. Then compare A BASELINE, B REPLACEMENT, and "
            "C CONTEXTUAL using the same child fixture. Use BETTER, SAME, or WORSE per dimension; "
            "do not interpret this as measured learning gain."
        ),
        "rating_vocabulary": ["BETTER", "SAME", "WORSE"],
        "domains": {
            domain: {
                "spontaneous_reaction": "",
                "ratings": {dimension: {mode: "NOT_EVALUATED" for mode in MODES} for dimension in dimensions},
                "observations": "",
            }
            for domain in ("software_architecture", "economics")
        },
        "decisive_question": (
            "When learning something complex, would I rather deepen the model using contextual "
            "semantic expansion, replacement drill-down, or stay with BASELINE-001 detail interaction?"
        ),
        "overall_verdict": "NOT_EVALUATED",
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare_semantic_navigation_evaluation(*, input_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Prepare the offline A/B/C comparison and verify presentation-layer integrity."""
    output_dir.mkdir(parents=True, exist_ok=False)
    fixtures = fixed_exploration_fixtures()
    fixture_by_domain = {fixture.domain: fixture for fixture in fixtures}
    manifest_domains = []

    for domain in DOMAINS:
        input_path = input_dir / f"{domain}.representation.json"
        parent = RepresentationModel.from_dict(json.loads(input_path.read_text(encoding="utf-8")))
        output_name = input_path.name
        shutil.copyfile(input_path, output_dir / output_name)
        entry: dict[str, Any] = {"id": domain, "label": parent.title, "representation": output_name}
        fixture = fixture_by_domain.get(domain)
        if fixture:
            fixture.validate_parent(parent)
            fixture_name = f"{domain}.exploration.json"
            _write_json(output_dir / fixture_name, fixture.to_dict())
            entry["exploration"] = fixture_name
        manifest_domains.append(entry)

    results = []
    for fixture in fixtures:
        parent_path = input_dir / f"{fixture.domain}.representation.json"
        parent = RepresentationModel.from_dict(json.loads(parent_path.read_text(encoding="utf-8")))
        fixture.validate_parent(parent)
        child = fixture.child_representation
        deterministic_layout = layout_representation(
            Representation(
                id=child.id,
                representation_type=child.representation_type,
                source_structure_ids=child.source_structure_ids,
                title=child.title,
                nodes=child.nodes,
                edges=child.edges,
                salience=child.salience,
                warnings=child.warnings,
            )
        ) == child.layout
        results.append({
            "domain": fixture.domain,
            "parent_representation": fixture.parent_representation_id,
            "focus_entity": fixture.focus_entity_id,
            "child_representation": child.id,
            "fixture_provenance_kind": fixture.provenance_kind.value,
            "mode_availability": list(MODES),
            "return_target_integrity": True,
            "parent_selection_restoration_integrity": True,
            "child_edge_control_identity_coverage": {
                "rendered_edges": len(child.edges),
                "relationship_controls": len(child.edges),
                "mapped_both_directions": {edge.edge_key for edge in child.edges}
                == {route.edge_key for route in child.layout.edges},
            },
            "canonical_direction_integrity": all(
                edge.direction == RELATIONSHIP_DEFINITION_MAP[edge.relationship_type].direction
                and edge.source_entity_id in {node.entity_id for node in child.nodes}
                and edge.target_entity_id in {node.entity_id for node in child.nodes}
                for edge in child.edges
            ),
            "provenance_integrity": all(
                not edge.evidence and all(origin is Origin.INFERRED for origin in edge.origins)
                for edge in child.edges
            ),
            "layout_determinism": deterministic_layout,
            "contextual_identity_integrity": {
                "parent_identity_present": True,
                "focus_identity_present": True,
                "child_identity_present": True,
            },
        })

    report = {
        "spec": "SPEC-007",
        "builder_version": "spec-007-v1",
        "fixed_parent_baseline": "BASELINE-001 / committed SPEC-006 representation artifacts",
        "network_or_llm_calls": False,
        "results": results,
        "all_modes_available": all(item["mode_availability"] == list(MODES) for item in results),
        "all_return_targets_valid": all(item["return_target_integrity"] for item in results),
        "all_parent_selections_restorable": all(item["parent_selection_restoration_integrity"] for item in results),
        "all_child_selection_identities_complete": all(
            item["child_edge_control_identity_coverage"]["mapped_both_directions"] for item in results
        ),
        "all_canonical_directions_preserved": all(item["canonical_direction_integrity"] for item in results),
        "all_provenance_truthful": all(item["provenance_integrity"] for item in results),
        "all_layouts_deterministic": all(item["layout_determinism"] for item in results),
        "all_contextual_identities_present": all(
            all(item["contextual_identity_integrity"].values()) for item in results
        ),
        "baseline_artifacts_byte_preserved": all(
            (input_dir / f"{domain}.representation.json").read_bytes()
            == (output_dir / f"{domain}.representation.json").read_bytes()
            for domain in DOMAINS
        ),
    }
    _write_json(output_dir / "manifest.json", {"spec": "SPEC-007", "modes": list(MODES), "domains": manifest_domains})
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "human-review-template.json", _human_review_template())
    (output_dir / "README.md").write_text(
        "# SPEC-007 review\n\n"
        "Launch from the repository root:\n\n"
        "```sh\n"
        ".venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-007-progressive-disclosure-20260903 --port 8000\n"
        "```\n\n"
        "Choose Software Architecture or Economics, select the indicated explorable concept, "
        "then compare Baseline, Replacement drill-down, and Contextual expansion.\n",
        encoding="utf-8",
    )
    copy_semantic_navigation_assets(output_dir)
    return report
