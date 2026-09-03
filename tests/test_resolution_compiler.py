from __future__ import annotations

import json
from pathlib import Path

import pytest

from knowledge_compiler.models import KnowledgeModel, Origin, ValidationError
from knowledge_compiler.openai_extractor import ExtractionError
from knowledge_compiler.openai_resolution import (
    build_resolution_input,
    build_resolution_instructions,
    resolution_schema,
)
from knowledge_compiler.relationships import RELATIONSHIP_DEFINITION_MAP
from knowledge_compiler.representations import RepresentationModel
from knowledge_compiler.resolution_compiler import (
    ChildResolutionArtifact,
    FixtureResolutionExtractor,
    ResolutionNomination,
    ResolutionOutcome,
    ResolutionRequest,
    build_source_scope,
    compile_resolution,
)
from knowledge_compiler.resolution_evaluation import (
    compare_with_handcrafted,
    default_parent_models_directory,
    default_parent_representations_directory,
    default_reference_directory,
    run_resolution_evaluation,
)


ROOT = Path(__file__).parents[1]


def parents(domain: str = "economics") -> tuple[KnowledgeModel, RepresentationModel]:
    model = KnowledgeModel.from_dict(json.loads(
        (default_parent_models_directory() / f"{domain}.knowledge.json").read_text()
    ))
    representation = RepresentationModel.from_dict(json.loads(
        (default_parent_representations_directory() / f"{domain}.representation.json").read_text()
    ))
    return model, representation


def economics_request(parent: KnowledgeModel) -> ResolutionRequest:
    return ResolutionRequest(
        parent_document_id=parent.document.id,
        parent_representation_id="representation-fe3ba90cb8cfa3d6",
        focus_entity_id="market-price",
        focus_label="market price",
        domain="economics",
    )


def success_nomination() -> ResolutionNomination:
    return ResolutionNomination(
        outcome=ResolutionOutcome.SUCCESS,
        reason="The source supports a local response sequence around market price.",
        extraction={
            "entities": [
                {"id": "market-price-signal", "name": "market price signal", "description": "The market price observed by participants.", "entity_type": "VARIABLE", "aliases": []},
                {"id": "buyer-response", "name": "buyer response", "description": "Buyers adjust their demanded quantity after observing price.", "entity_type": "PROCESS", "aliases": []},
                {"id": "quantity-adjustment", "name": "quantity adjustment", "description": "The resulting change in quantity demanded.", "entity_type": "PROCESS", "aliases": []},
            ],
            "claims": [],
            "relationships": [
                {
                    "id": "child-rel-1", "source_entity_id": "market-price-signal",
                    "relationship_type": "CAUSES", "target_entity_id": "buyer-response",
                    "statement": "A market price rise causes buyers to respond.",
                    "evidence": [{"quote": "When the price rises, buyers usually demand a smaller quantity"}],
                    "confidence": 0.9, "origin": "SOURCE",
                },
                {
                    "id": "child-rel-2", "source_entity_id": "buyer-response",
                    "relationship_type": "CAUSES", "target_entity_id": "quantity-adjustment",
                    "statement": "The buyer response produces a quantity adjustment.",
                    "evidence": [], "confidence": 0.65, "origin": "INFERRED",
                },
            ],
        },
        metadata={
            "provider": "fixture", "model": "deterministic-fixture",
            "prompt_version": "spec-008-v1",
        },
    )


def test_resolution_request_requires_real_parent_focus() -> None:
    parent, representation = parents()
    economics_request(parent).validate_against(parent, representation)
    bad = ResolutionRequest(
        parent.document.id, "representation-fe3ba90cb8cfa3d6", "missing", "market price", "economics"
    )
    with pytest.raises(ValidationError, match="focus"):
        bad.validate_against(parent, representation)


def test_source_scope_is_exact_full_small_document_with_connected_evidence_context() -> None:
    parent, _ = parents()
    scope = build_source_scope(parent, "market-price")
    assert scope.strategy == "FULL_DOCUMENT_SMALL_SOURCE"
    assert scope.document_id == parent.document.id
    assert scope.start_char == 0 and scope.end_char == len(parent.document.text)
    assert scope.text == parent.document.text
    assert "rel-price-decreases-demanded" in scope.connected_relationship_ids


def test_successful_fixture_path_builds_round_trippable_grounded_child_without_parent_mutation() -> None:
    parent, representation = parents()
    before = json.dumps(parent.to_dict(), sort_keys=True)
    result = compile_resolution(
        parent, representation, economics_request(parent), FixtureResolutionExtractor(success_nomination())
    )
    assert result.outcome is ResolutionOutcome.SUCCESS
    assert result.artifact is not None
    artifact = result.artifact
    assert artifact.child_model.document is parent.document
    assert json.dumps(parent.to_dict(), sort_keys=True) == before
    assert len(artifact.structures.structures) == 1
    assert len(artifact.representation.representations) == 1
    source = artifact.child_model.relationships[0]
    assert source.origin is Origin.SOURCE
    assert source.evidence[0].quote == "When the price rises, buyers usually demand a smaller quantity"
    assert parent.document.text[source.evidence[0].start_char:source.evidence[0].end_char] == source.evidence[0].quote
    inferred = artifact.child_model.relationships[1]
    assert inferred.origin is Origin.INFERRED and inferred.evidence == ()
    round_trip = ChildResolutionArtifact.from_dict(artifact.to_dict())
    assert round_trip.to_dict() == artifact.to_dict()


@pytest.mark.parametrize("quote", ["price", "This quote is absent."])
def test_ambiguous_and_missing_quotes_fail_closed(quote: str) -> None:
    parent, representation = parents()
    nomination = success_nomination()
    extraction = dict(nomination.extraction)
    relationships = [dict(item) for item in extraction["relationships"]]
    relationships[0] = {**relationships[0], "evidence": [{"quote": quote}]}
    extraction["relationships"] = relationships
    result = compile_resolution(
        parent, representation, economics_request(parent),
        FixtureResolutionExtractor(ResolutionNomination(
            ResolutionOutcome.SUCCESS, "test grounding", extraction, nomination.metadata
        )),
    )
    assert result.outcome is ResolutionOutcome.GROUNDING_FAILURE
    assert len(result.grounding_failures) == 1


def test_inferred_content_cannot_carry_source_evidence() -> None:
    parent, representation = parents()
    nomination = success_nomination()
    extraction = dict(nomination.extraction)
    relationships = [dict(item) for item in extraction["relationships"]]
    relationships[1] = {
        **relationships[1], "origin": "INFERRED",
        "evidence": [{"quote": "When the price rises, buyers usually demand a smaller quantity"}],
    }
    extraction["relationships"] = relationships
    result = compile_resolution(
        parent, representation, economics_request(parent),
        FixtureResolutionExtractor(ResolutionNomination(
            ResolutionOutcome.SUCCESS, "test provenance", extraction, nomination.metadata
        )),
    )
    assert result.outcome is ResolutionOutcome.GROUNDING_FAILURE


def test_invalid_child_semantics_fail_before_downstream_representation() -> None:
    parent, representation = parents()
    nomination = success_nomination()
    extraction = dict(nomination.extraction)
    relationships = [dict(item) for item in extraction["relationships"]]
    relationships[0] = {**relationships[0], "relationship_type": "HAS_DEEPER_MODEL"}
    extraction["relationships"] = relationships
    result = compile_resolution(
        parent, representation, economics_request(parent),
        FixtureResolutionExtractor(ResolutionNomination(
            ResolutionOutcome.SUCCESS, "test invalid semantics", extraction, nomination.metadata
        )),
    )
    assert result.outcome is ResolutionOutcome.SEMANTIC_VALIDATION_FAILURE
    assert result.artifact is None


def test_insufficient_source_and_provider_failure_are_explicit_without_retry() -> None:
    parent, representation = parents()
    request = economics_request(parent)
    insufficient = compile_resolution(
        parent, representation, request,
        FixtureResolutionExtractor(ResolutionNomination(
            ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL, "No finer mechanism is supported."
        )),
    )
    assert insufficient.outcome is ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL
    assert insufficient.artifact is None and insufficient.retries == 0
    failed = compile_resolution(
        parent, representation, request,
        FixtureResolutionExtractor(ExtractionError("provider unavailable")),
    )
    assert failed.outcome is ResolutionOutcome.PROVIDER_FAILURE
    assert failed.artifact is None and failed.retries == 0


def test_child_representation_preserves_canonical_direction_and_provenance() -> None:
    parent, representation = parents()
    result = compile_resolution(
        parent, representation, economics_request(parent), FixtureResolutionExtractor(success_nomination())
    )
    artifact = result.artifact
    assert artifact is not None
    relationships = {item.id: item for item in artifact.child_model.relationships}
    for view in artifact.representation.representations:
        for edge in view.edges:
            definition = RELATIONSHIP_DEFINITION_MAP[edge.relationship_type]
            assert edge.direction == definition.direction
            assert edge.origins == tuple(relationships[item].origin for item in edge.relationship_ids)
            for evidence in edge.evidence:
                assert evidence.quote == parent.document.text[evidence.start_char:evidence.end_char]


def test_prompt_contract_is_source_bounded_and_does_not_include_reference_fixture() -> None:
    parent, _ = parents()
    request = economics_request(parent)
    scope = build_source_scope(parent, request.focus_entity_id)
    instructions = build_resolution_instructions()
    prompt = build_resolution_input(request, parent, scope)
    schema = resolution_schema()
    assert "INSUFFICIENT_SOURCE_DETAIL" in instructions
    assert "permitted source" in instructions
    assert "fixture-market-price-response" not in prompt
    assert json.loads(prompt)["permitted_source"]["text"] == parent.document.text
    assert schema["additionalProperties"] is False


def test_handcrafted_comparison_uses_semantic_dimensions_not_lexical_score() -> None:
    parent, representation = parents()
    result = compile_resolution(
        parent, representation, economics_request(parent), FixtureResolutionExtractor(success_nomination())
    )
    reference = json.loads(
        (default_reference_directory() / "economics.exploration.json").read_text()
    )
    comparison = compare_with_handcrafted(result, reference)
    assert comparison["status"] == "READY_FOR_HUMAN_REVIEW"
    assert comparison["lexical_overlap_score"] is None
    assert set(comparison["dimensions"]) == {
        "focus_relevance", "mechanistic_detail_gain", "relationship_truthfulness",
        "source_grounding", "structure_usefulness", "parent_coherence",
        "compression_relationship", "cognitive_usefulness",
    }


def test_evaluation_preserves_failures_and_parent_navigation_artifacts(tmp_path: Path) -> None:
    output = tmp_path / "evaluation"
    insufficient = ResolutionNomination(
        ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL, "Fixture says source is insufficient."
    )
    report = run_resolution_evaluation(
        models_dir=default_parent_models_directory(),
        representations_dir=default_parent_representations_directory(),
        reference_dir=default_reference_directory(),
        output_dir=output,
        extractor_factory=lambda: FixtureResolutionExtractor(insufficient),
    )
    assert report["successful_child_count"] == 0
    assert report["outcome_counts"]["INSUFFICIENT_SOURCE_DETAIL"] == 2
    assert report["baseline_parent_artifacts_byte_preserved"] is True
    assert report["complexity_budget"]["maximum_generated_child_depth"] == 1
    assert report["complexity_budget"]["new_runtime_dependencies"] == 0
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["modes"] == ["BASELINE", "REPLACEMENT", "CONTEXTUAL"]
    assert all("exploration" not in entry for entry in manifest["domains"])
    for domain in ("software_architecture", "economics"):
        assert (output / f"{domain}.representation.json").read_bytes() == (
            default_parent_representations_directory() / f"{domain}.representation.json"
        ).read_bytes()
    assert not any(path.name.startswith("DEBRIEF-009") for path in (ROOT / "debriefs").iterdir())


def test_successful_navigation_artifact_is_labeled_generated_from_source(tmp_path: Path) -> None:
    class PerDomainExtractor:
        def nominate(self, request, parent, scope):
            if request.domain == "economics":
                return success_nomination()
            return ResolutionNomination(
                ResolutionOutcome.SUCCESS,
                "The fixture adapter exercises the successful Software Architecture path.",
                {
                    "entities": [
                        {"id": "api-boundary", "name": "API component boundary", "description": "The selected API component boundary.", "entity_type": "COMPONENT", "aliases": []},
                        {"id": "published-interface-use", "name": "published interface use", "description": "Use of the component's published interface.", "entity_type": "PROCESS", "aliases": []},
                        {"id": "order-call", "name": "order component call", "description": "A call from the API to the order component.", "entity_type": "PROCESS", "aliases": []},
                    ],
                    "claims": [],
                    "relationships": [
                        {"id": "software-child-1", "source_entity_id": "api-boundary", "relationship_type": "AFFECTS", "target_entity_id": "published-interface-use", "statement": "The API component boundary affects use of the published interface.", "evidence": [{"quote": "The API component calls the order component through its published interface."}], "confidence": 0.8, "origin": "SOURCE"},
                        {"id": "software-child-2", "source_entity_id": "published-interface-use", "relationship_type": "AFFECTS", "target_entity_id": "order-call", "statement": "Published interface use affects the order call.", "evidence": [], "confidence": 0.6, "origin": "INFERRED"},
                    ],
                },
                {"provider": "fixture", "model": "per-domain", "prompt_version": "spec-008-v1"},
            )

    output = tmp_path / "successful"
    report = run_resolution_evaluation(
        models_dir=default_parent_models_directory(),
        representations_dir=default_parent_representations_directory(),
        reference_dir=default_reference_directory(),
        output_dir=output,
        extractor_factory=PerDomainExtractor,
    )
    assert report["successful_child_count"] == 2
    manifest = json.loads((output / "manifest.json").read_text())
    assert all("exploration" in entry for entry in manifest["domains"])
    exploration = json.loads((output / "economics.generated-exploration.json").read_text())
    assert exploration["provenance_kind"] == "GENERATED_SOURCE_GROUNDED"
    assert exploration["provenance_display_label"] == "Generated from source"
    assert any(edge["evidence"] for edge in exploration["child_representation"]["edges"])
    script = (ROOT / "src" / "knowledge_compiler" / "viewer_assets" / "semantic-navigation.js").read_text()
    assert 'state.fixture.provenance_display_label || "Experimental fixture"' in script
