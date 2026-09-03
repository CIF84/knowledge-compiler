from __future__ import annotations

import json
from pathlib import Path

import pytest

from knowledge_compiler.models import KnowledgeModel, ValidationError
from knowledge_compiler.openai_resolution import (
    SPEC_009_PROMPT_VERSION,
    build_resolution_input,
    build_resolution_instructions,
)
from knowledge_compiler.relationships import RELATIONSHIP_DEFINITION_MAP
from knowledge_compiler.representations import RepresentationModel
from knowledge_compiler.resolution_compiler import (
    SPEC_009_COMPILER_VERSION,
    FixtureResolutionExtractor,
    ResolutionNomination,
    ResolutionOutcome,
    ResolutionRequest,
    build_source_scope,
    compile_resolution,
)
from knowledge_compiler.resolution_evaluation import (
    default_parent_models_directory,
    default_parent_representations_directory,
)
from knowledge_compiler.resolution_strategies import (
    RESOLUTION_STRATEGIES,
    RESOLUTION_STRATEGY_REGISTRY,
    ResolutionStrategyId,
    get_resolution_strategy,
    render_resolution_strategy,
)
from knowledge_compiler.resolution_strategy_evaluation import (
    PROCESS_ORIGINAL_SOURCE_ASSESSMENT,
    benchmark_cases,
    build_process_parent,
    run_resolution_strategy_evaluation,
)


ROOT = Path(__file__).parents[1]


def economics_parent() -> tuple[KnowledgeModel, RepresentationModel]:
    parent = KnowledgeModel.from_dict(json.loads(
        (default_parent_models_directory() / "economics.knowledge.json").read_text()
    ))
    representation = RepresentationModel.from_dict(json.loads(
        (default_parent_representations_directory() / "economics.representation.json").read_text()
    ))
    return parent, representation


def economics_request(strategy_id: ResolutionStrategyId) -> ResolutionRequest:
    parent, _ = economics_parent()
    return ResolutionRequest(
        parent.document.id,
        "representation-fe3ba90cb8cfa3d6",
        "market-price",
        "market price",
        "economics",
        strategy_id,
    )


def process_success_nomination() -> ResolutionNomination:
    return ResolutionNomination(
        ResolutionOutcome.SUCCESS,
        "The source supports an explicit sequence inside the workflow.",
        {
            "entities": [
                {"id": "api-accepts-request", "name": "API accepts order request", "description": "The first stage of the order-processing workflow accepts the submitted request.", "entity_type": "PROCESS", "aliases": []},
                {"id": "api-parses-payload", "name": "API parses payload", "description": "The API parses the accepted payload.", "entity_type": "PROCESS", "aliases": []},
                {"id": "api-validates-fields", "name": "API validates required fields", "description": "The API validates required customer and item fields.", "entity_type": "PROCESS", "aliases": []},
            ],
            "claims": [],
            "relationships": [
                {
                    "id": "process-rel-1", "source_entity_id": "api-accepts-request",
                    "relationship_type": "PRECEDES", "target_entity_id": "api-parses-payload",
                    "statement": "Accepting the request precedes parsing its payload.",
                    "evidence": [{"quote": "The workflow begins when the API accepts an order request. The API parses the payload before it validates the required customer and item fields."}],
                    "confidence": 1.0, "origin": "SOURCE",
                },
                {
                    "id": "process-rel-2", "source_entity_id": "api-parses-payload",
                    "relationship_type": "PRECEDES", "target_entity_id": "api-validates-fields",
                    "statement": "Parsing the payload precedes validating its required fields.",
                    "evidence": [{"quote": "The API parses the payload before it validates the required customer and item fields."}],
                    "confidence": 1.0, "origin": "SOURCE",
                },
            ],
        },
        {
            "provider": "fixture",
            "model": "deterministic-spec-009",
            "prompt_version": SPEC_009_PROMPT_VERSION,
        },
    )


def test_strategy_registry_has_exactly_three_type_aware_strategies_and_one_control() -> None:
    assert tuple(item.id for item in RESOLUTION_STRATEGIES) == (
        ResolutionStrategyId.GENERIC_DETAIL,
        ResolutionStrategyId.PROCESS_STAGES,
        ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD,
        ResolutionStrategyId.COMPONENT_INTERNALS,
    )
    assert len(RESOLUTION_STRATEGY_REGISTRY) == 4
    assert len({item.id for item in RESOLUTION_STRATEGIES}) == 4
    for strategy in RESOLUTION_STRATEGIES:
        assert strategy.objective and strategy.seek and strategy.avoid
        rendered = render_resolution_strategy(strategy)
        assert strategy.id.value in rendered
        assert rendered.count(strategy.objective) == 1
    with pytest.raises(ValidationError, match="unsupported"):
        get_resolution_strategy("UNIVERSAL_ONTOLOGY")


def test_provider_prompt_consumes_canonical_strategy_without_duplicating_its_semantics_in_input() -> None:
    parent, _ = economics_parent()
    request = economics_request(ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD)
    scope = build_source_scope(parent, request.focus_entity_id)
    strategy = get_resolution_strategy(request.strategy_id)
    instructions = build_resolution_instructions(request.strategy_id)
    payload = json.loads(build_resolution_input(request, parent, scope))
    assert strategy.objective in instructions
    assert payload["resolution_strategy"] == {
        "id": strategy.id.value,
        "semantic_role": strategy.semantic_role,
    }
    assert "objective" not in payload["resolution_strategy"]
    assert "seek" not in payload["resolution_strategy"]
    assert "INSUFFICIENT_SOURCE_DETAIL" in instructions
    assert "INFERRED items must have empty evidence" in instructions


def test_benchmark_mapping_is_explicit_and_process_original_insufficiency_is_preserved() -> None:
    cases = benchmark_cases()
    assert {case.id: case.assigned_strategy for case in cases} == {
        "variable-market-price": ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD,
        "process-order-workflow": ResolutionStrategyId.PROCESS_STAGES,
        "component-api": ResolutionStrategyId.COMPONENT_INTERNALS,
    }
    assert PROCESS_ORIGINAL_SOURCE_ASSESSMENT["outcome"] == "INSUFFICIENT_SOURCE_DETAIL"
    assert PROCESS_ORIGINAL_SOURCE_ASSESSMENT["provider_call_made"] is False
    assert sum(case.source_kind == "SPEC_009_EXPERIMENTAL_RICHER_LOCAL_SOURCE" for case in cases) == 1


def test_strategy_changes_neither_source_scope_nor_parent_context() -> None:
    for case in benchmark_cases():
        generic = ResolutionRequest(
            case.parent.document.id, case.parent_representation_id, case.focus_entity_id,
            case.focus_label, case.domain, ResolutionStrategyId.GENERIC_DETAIL,
        )
        aware = ResolutionRequest(
            case.parent.document.id, case.parent_representation_id, case.focus_entity_id,
            case.focus_label, case.domain, case.assigned_strategy,
        )
        generic_scope = build_source_scope(case.parent, case.focus_entity_id)
        aware_scope = build_source_scope(case.parent, case.focus_entity_id)
        assert generic_scope.to_dict() == aware_scope.to_dict()
        generic_input = json.loads(build_resolution_input(generic, case.parent, generic_scope))
        aware_input = json.loads(build_resolution_input(aware, case.parent, aware_scope))
        generic_input.pop("resolution_strategy")
        aware_input.pop("resolution_strategy")
        assert generic_input == aware_input


@pytest.mark.parametrize("strategy_id", tuple(ResolutionStrategyId))
def test_insufficient_source_is_supported_without_retry_under_every_strategy(
    strategy_id: ResolutionStrategyId,
) -> None:
    parent, representation = economics_parent()
    result = compile_resolution(
        parent,
        representation,
        economics_request(strategy_id),
        FixtureResolutionExtractor(ResolutionNomination(
            ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL,
            "The permitted source cannot support the requested explanatory pattern.",
        )),
        compiler_version=SPEC_009_COMPILER_VERSION,
    )
    assert result.outcome is ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL
    assert result.retries == 0
    assert result.artifact is None


def test_process_strategy_child_round_trips_through_existing_downstream_pipeline() -> None:
    parent, representation = build_process_parent()
    before = json.dumps(parent.to_dict(), sort_keys=True)
    request = ResolutionRequest(
        parent.document.id,
        representation.representations[0].id,
        "order-processing-workflow",
        "order-processing workflow",
        "software_architecture_process",
        ResolutionStrategyId.PROCESS_STAGES,
    )
    result = compile_resolution(
        parent,
        representation,
        request,
        FixtureResolutionExtractor(process_success_nomination()),
        compiler_version=SPEC_009_COMPILER_VERSION,
    )
    assert result.outcome is ResolutionOutcome.SUCCESS
    assert result.artifact is not None
    assert result.artifact.compiler_version == SPEC_009_COMPILER_VERSION
    assert result.artifact.child_model.metadata["resolution_strategy_id"] == "PROCESS_STAGES"
    assert result.artifact.structures.structures[0].structure_type.value == "PROCESS_CHAIN"
    assert result.artifact.representation.representations[0].representation_type.value == "PROCESS_CHAIN"
    assert json.dumps(parent.to_dict(), sort_keys=True) == before


@pytest.mark.parametrize("strategy_id", tuple(ResolutionStrategyId))
def test_grounding_invariant_is_unchanged_and_rejected_output_is_preserved(
    strategy_id: ResolutionStrategyId,
) -> None:
    parent, representation = economics_parent()
    nomination = ResolutionNomination(
        ResolutionOutcome.SUCCESS,
        "Deliberately invalid provenance for regression coverage.",
        {
            "entities": [
                {"id": "market-price", "name": "market price", "description": "Price.", "entity_type": "VARIABLE", "aliases": []},
                {"id": "quantity-demanded", "name": "quantity demanded", "description": "Quantity.", "entity_type": "VARIABLE", "aliases": []},
                {"id": "buyer-response", "name": "buyer response", "description": "Response.", "entity_type": "PROCESS", "aliases": []},
            ],
            "claims": [],
            "relationships": [
                {"id": "invalid-1", "source_entity_id": "market-price", "relationship_type": "DECREASES", "target_entity_id": "quantity-demanded", "statement": "Price decreases quantity demanded.", "evidence": [{"quote": "When the price rises, buyers usually demand a smaller quantity"}], "confidence": 1.0, "origin": "INFERRED"},
                {"id": "invalid-2", "source_entity_id": "quantity-demanded", "relationship_type": "AFFECTS", "target_entity_id": "buyer-response", "statement": "Quantity demanded affects the buyer response.", "evidence": [], "confidence": 0.5, "origin": "INFERRED"},
            ],
        },
        {"provider": "fixture", "model": "invalid", "prompt_version": SPEC_009_PROMPT_VERSION},
    )
    result = compile_resolution(
        parent,
        representation,
        economics_request(strategy_id),
        FixtureResolutionExtractor(nomination),
        compiler_version=SPEC_009_COMPILER_VERSION,
    )
    assert result.outcome is ResolutionOutcome.GROUNDING_FAILURE
    assert result.retries == 0
    assert result.rejected_extraction == nomination.extraction
    assert result.to_dict()["rejected_extraction"] == nomination.extraction


def test_valid_nomination_rejected_by_resolution_gate_is_preserved() -> None:
    parent, representation = economics_parent()
    nomination = ResolutionNomination(
        ResolutionOutcome.SUCCESS,
        "Valid source-grounded relationships that do not form a finer structure.",
        {
            "entities": [
                {"id": "market-price", "name": "market price", "description": "The market price.", "entity_type": "VARIABLE", "aliases": []},
                {"id": "quantity-demanded", "name": "quantity demanded", "description": "Quantity demanded.", "entity_type": "VARIABLE", "aliases": []},
                {"id": "quantity-supplied", "name": "quantity supplied", "description": "Quantity supplied.", "entity_type": "VARIABLE", "aliases": []},
            ],
            "claims": [],
            "relationships": [
                {"id": "gate-1", "source_entity_id": "market-price", "relationship_type": "DECREASES", "target_entity_id": "quantity-demanded", "statement": "A higher price decreases quantity demanded.", "evidence": [{"quote": "The higher price decreases quantity demanded and increases quantity supplied until the shortage narrows."}], "confidence": 1.0, "origin": "SOURCE"},
                {"id": "gate-2", "source_entity_id": "market-price", "relationship_type": "INCREASES", "target_entity_id": "quantity-supplied", "statement": "A higher price increases quantity supplied.", "evidence": [{"quote": "The higher price decreases quantity demanded and increases quantity supplied until the shortage narrows."}], "confidence": 1.0, "origin": "SOURCE"},
            ],
        },
        {"provider": "fixture", "model": "gate", "prompt_version": SPEC_009_PROMPT_VERSION},
    )
    result = compile_resolution(
        parent,
        representation,
        economics_request(ResolutionStrategyId.VARIABLE_CAUSAL_NEIGHBORHOOD),
        FixtureResolutionExtractor(nomination),
        compiler_version=SPEC_009_COMPILER_VERSION,
    )
    assert result.outcome is ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL
    assert result.provider_metadata["resolution_assessment"]["mechanistic_detail_gain"] is False
    assert result.rejected_extraction == nomination.extraction
    assert result.retries == 0


def test_offline_paired_evaluation_preserves_all_attempts_and_navigation_assets(tmp_path: Path) -> None:
    insufficient = ResolutionNomination(
        ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL,
        "Deterministic fixture reports insufficient source detail.",
        metadata={
            "provider": "fixture",
            "model": "deterministic-spec-009",
            "prompt_version": SPEC_009_PROMPT_VERSION,
        },
    )
    output = tmp_path / "spec-009"
    report = run_resolution_strategy_evaluation(
        output_dir=output,
        extractor_factory=lambda _case, _strategy: FixtureResolutionExtractor(insufficient),
    )
    assert report["generation_attempt_count"] == 6
    assert report["provider_call_count"] == 0
    assert report["outcome_counts"]["INSUFFICIENT_SOURCE_DETAIL"] == 6
    assert report["source_scope_equivalence"]["all_pairs_equivalent"] is True
    assert report["source_scope_equivalence"]["all_parent_context_equivalent_except_strategy_metadata"] is True
    assert report["parent_immutability"]["all_parents_unchanged"] is True
    assert report["complexity_budget"] == {
        "type_aware_strategy_count": 3,
        "generic_control_count": 1,
        "maximum_generated_child_depth": 1,
        "new_runtime_dependencies": 0,
        "new_semantic_ir_fields": 0,
        "new_semantic_ir_types": 0,
        "new_experimental_boundary_types": 2,
        "new_canonical_predicates": 0,
        "source_fixtures_added": 1,
        "automatic_retries": 0,
        "recursive_architecture_introduced": False,
        "navigation_redesign": False,
        "personalization_machinery": False,
    }
    assert report["canonical_relationship_count"] == len(RELATIONSHIP_DEFINITION_MAP) == 20
    history = json.loads((output / "run-history.json").read_text())
    assert len(history["attempts"]) == 6
    assert all(item["retries"] == 0 for item in history["attempts"])
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["modes"] == ["BASELINE", "REPLACEMENT", "CONTEXTUAL"]
    assert len(manifest["domains"]) == 6
    assert all("exploration" not in item for item in manifest["domains"])
    assert (output / "process.experimental-source.txt").read_bytes() == (
        ROOT / "tests" / "fixtures" / "spec009" / "order_processing_workflow.txt"
    ).read_bytes()


def test_paired_evaluation_writes_successful_process_navigation_artifact(tmp_path: Path) -> None:
    insufficient = ResolutionNomination(
        ResolutionOutcome.INSUFFICIENT_SOURCE_DETAIL,
        "Only the process path succeeds in this deterministic fixture run.",
        metadata={
            "provider": "fixture",
            "model": "deterministic-spec-009",
            "prompt_version": SPEC_009_PROMPT_VERSION,
        },
    )

    def factory(case, _strategy):
        nomination = process_success_nomination() if case.id == "process-order-workflow" else insufficient
        return FixtureResolutionExtractor(nomination)

    output = tmp_path / "success"
    report = run_resolution_strategy_evaluation(output_dir=output, extractor_factory=factory)
    assert report["successful_child_count"] == 2
    manifest = json.loads((output / "manifest.json").read_text())
    process_entries = [item for item in manifest["domains"] if item["id"].startswith("process-order-workflow")]
    assert all("exploration" in item for item in process_entries)
    exploration = json.loads((
        output / "process-order-workflow.process_stages.generated-exploration.json"
    ).read_text())
    assert exploration["resolution_strategy"]["id"] == "PROCESS_STAGES"
    assert exploration["child_representation"]["representation_type"] == "PROCESS_CHAIN"
    assert exploration["provenance_kind"] == "GENERATED_SOURCE_GROUNDED"
