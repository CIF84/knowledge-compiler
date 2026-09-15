from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from knowledge_compiler.decomposed_extraction import GateStatus, StageAttempt, StageName, freeze_entity_inventory, validate_claim_evidence_binding
from knowledge_compiler.decomposed_extraction_v2 import CANDIDATE_B_V2_VERSION, normalize_stage2_v2, replay_v1_proposition_shape, run_candidate_b_v2
from knowledge_compiler.models import SourceDocument, ValidationError
from knowledge_compiler.openai_decomposed_extractor_v2 import OpenAICandidateBV2Extractor, build_stage2_v2_instructions, build_stage3_v2_instructions, stage2_v2_schema
from knowledge_compiler.spec051_offline_evaluation import OUTPUT_DIRECTORY, build_artifacts, write_artifacts
from knowledge_compiler.structure_detection import StructureDetector


ROOT = Path(__file__).parents[1]
SOURCE = "Demand exceeds supply and this causes shortage. Coordinates enable calculation. A is greater than B. A command moves to a component during transfer."


def symbols():
    return {"symbols": [
        {"name": name, "description": f"Source concept {name}.", "entity_type": kind, "aliases": []}
        for name, kind in (
            ("demand", "VARIABLE"), ("supply", "VARIABLE"), ("shortage", "CONCEPT"),
            ("transfer", "PROCESS"), ("command", "OBJECT"), ("component", "COMPONENT"),
            ("coordinates", "VARIABLE"), ("calculation", "PROCESS"),
            ("A", "VARIABLE"), ("B", "VARIABLE"),
        )
    ]}


def structure(*, propositions=True, relationship=True):
    return {
        "relationships": ([{
            "id": "coordinates-enables-calculation",
            "source_entity_id": "coordinates",
            "relationship_type": "ENABLES",
            "target_entity_id": "calculation",
            "statement": "Coordinates enable calculation.",
            "confidence": 1.0,
            "origin": "SOURCE",
        }] if relationship else []),
        "comparison_conditions": ([{
            "proposition_type": "COMPARISON_CONDITION",
            "statement": "Demand exceeds supply and this causes shortage.",
            "left_operand_entity_id": "demand",
            "right_operand_entity_id": "supply",
            "outcome_entity_id": "shortage",
            "relationship_type": "CAUSES",
            "comparison_operator": "GREATER_THAN",
            "confidence": 1.0,
            "origin": "SOURCE",
        }] if propositions else []),
        "transfer_events": [],
        "missing_symbols": [],
    }


def binding(structure_proposal):
    evidence = []
    if structure_proposal["relationships"]:
        evidence.append({"semantic_object_id": "coordinates-enables-calculation", "evidence": [{"quote": "Coordinates enable calculation."}]})
    if structure_proposal["comparison_conditions"] or structure_proposal["transfer_events"]:
        # The trusted compiler, not the model, derives proposition IDs.
        document = SourceDocument("fixture", SOURCE)
        inventory = freeze_entity_inventory(symbols(), document)
        normalized = normalize_stage2_v2(structure_proposal, document, inventory)
        from knowledge_compiler.decomposed_extraction import validate_semantic_structure
        propositions = validate_semantic_structure(normalized, document, inventory).propositions
        for item in propositions:
            quote = "Demand exceeds supply and this causes shortage." if item["proposition_type"] == "COMPARISON_CONDITION" else "A command moves to a component during transfer."
            evidence.append({"semantic_object_id": item["id"], "evidence": [{"quote": quote}]})
    return {"claims": [{
        "id": "claim-standalone-comparison",
        "statement": "A is greater than B.",
        "evidence": [{"quote": "A is greater than B."}],
        "confidence": 1.0,
        "origin": "SOURCE",
    }], "semantic_evidence_bindings": evidence}


class FixtureV2Adapter:
    live_capable = False
    candidate_version = CANDIDATE_B_V2_VERSION

    def __init__(self, *, structure_proposal=None, fail_stage=None, binding_proposal=None):
        self.structure_proposal = structure_proposal if structure_proposal is not None else structure(propositions=False)
        self.binding_proposal = binding_proposal
        self.fail_stage = fail_stage
        self.called = []
        self.call_ledger = {"candidate_version": CANDIDATE_B_V2_VERSION, "calls_started": 0, "entries": []}

    def _attempt(self, stage, value):
        self.called.append(stage)
        if stage is self.fail_stage:
            raise ValidationError(f"synthetic {stage.value} failure")
        return StageAttempt(stage, value, {"live_call": False, "candidate_version": CANDIDATE_B_V2_VERSION})

    def extract_entity_inventory(self, document):
        return self._attempt(StageName.ENTITY_INVENTORY, symbols())

    def extract_semantic_structure(self, document, inventory):
        return self._attempt(StageName.SEMANTIC_STRUCTURE, self.structure_proposal)

    def extract_claim_evidence(self, document, inventory, frozen_structure):
        value = self.binding_proposal if self.binding_proposal is not None else binding(self.structure_proposal)
        return self._attempt(StageName.CLAIM_EVIDENCE_BINDING, value)


def test_v2_schema_is_subtype_discriminated_with_dynamic_frozen_endpoint_sets():
    inventory = freeze_entity_inventory(symbols(), SourceDocument("fixture", SOURCE))
    schema = stage2_v2_schema(inventory)
    assert set(schema["properties"]) == {"relationships", "comparison_conditions", "transfer_events", "missing_symbols"}
    cc = schema["properties"]["comparison_conditions"]["items"]
    te = schema["properties"]["transfer_events"]["items"]
    assert cc["additionalProperties"] is False
    assert te["additionalProperties"] is False
    assert cc["properties"]["relationship_type"]["enum"] == ["CAUSES"]
    assert cc["properties"]["comparison_operator"]["enum"] == ["GREATER_THAN"]
    assert te["properties"]["relationship_type"]["enum"] == ["TRANSFERS_TO"]
    assert te["properties"]["comparison_operator"] == {"type": "null"}
    assert te["properties"]["event_entity_id"]["enum"] == ["calculation", "transfer"]
    assert "calculation" not in te["properties"]["destination_entity_id"]["enum"]
    assert "external" not in cc["properties"]["left_operand_entity_id"]["enum"]


def test_valid_canonical_proposition_variants_are_expressible_and_admitted():
    document = SourceDocument("fixture", SOURCE)
    inventory = freeze_entity_inventory(symbols(), document)
    proposal = structure()
    proposal["transfer_events"] = [{
        "proposition_type": "TRANSFER_EVENT", "statement": "A command moves to a component during transfer.",
        "event_entity_id": "transfer", "object_entity_id": "command", "destination_entity_id": "component",
        "relationship_type": "TRANSFERS_TO", "comparison_operator": None, "confidence": 1.0, "origin": "SOURCE",
    }]
    normalized = normalize_stage2_v2(proposal, document, inventory)
    assert [item["proposition_type"] for item in normalized["propositions"]] == ["COMPARISON_CONDITION", "TRANSFER_EVENT"]
    assert normalized["propositions"][0]["role_bindings"] == [
        {"role": "LEFT_OPERAND", "entity_id": "demand"},
        {"role": "RIGHT_OPERAND", "entity_id": "supply"},
        {"role": "OUTCOME", "entity_id": "shortage"},
    ]
    run = run_candidate_b_v2(SOURCE, FixtureV2Adapter(structure_proposal=proposal))
    assert run.status is GateStatus.PASS
    assert run.model is not None
    assert [item.proposition_type.value for item in run.model.propositions] == ["COMPARISON_CONDITION", "TRANSFER_EVENT"]
    assert all(item.evidence for item in run.model.propositions)


@pytest.mark.parametrize("mutation", [
    lambda value: value["comparison_conditions"][0].update(relationship_type="AFFECTS"),
    lambda value: value["comparison_conditions"][0].update(comparison_operator=None),
    lambda value: value["comparison_conditions"][0].update(right_operand_entity_id="demand"),
    lambda value: value["comparison_conditions"][0].update(left_operand_entity_id="external"),
    lambda value: value["comparison_conditions"][0].update(event_entity_id="transfer"),
    lambda value: value.update(entities=[]),
])
def test_invalid_v2_comparison_or_entity_states_fail_closed(mutation):
    proposal = structure()
    mutation(proposal)
    document = SourceDocument("fixture", SOURCE)
    inventory = freeze_entity_inventory(symbols(), document)
    with pytest.raises(ValidationError):
        normalize_stage2_v2(proposal, document, inventory)


def test_transfer_requires_frozen_process_event_and_nonprocess_destination():
    document = SourceDocument("fixture", SOURCE)
    inventory = freeze_entity_inventory(symbols(), document)
    proposal = structure(propositions=False, relationship=False)
    valid = {
        "proposition_type": "TRANSFER_EVENT", "statement": "A command moves to a component during transfer.",
        "event_entity_id": "transfer", "object_entity_id": "command", "destination_entity_id": "component",
        "relationship_type": "TRANSFERS_TO", "comparison_operator": None, "confidence": 1.0, "origin": "INFERRED",
    }
    proposal["transfer_events"] = [valid]
    assert len(normalize_stage2_v2(proposal, document, inventory)["propositions"]) == 1
    for bad in [
        {**valid, "event_entity_id": "command"},
        {**valid, "destination_entity_id": "calculation"},
        {**valid, "comparison_operator": "GREATER_THAN"},
        {**valid, "relationship_type": "ENABLES"},
        {key: value for key, value in valid.items() if key != "event_entity_id"},
    ]:
        proposal["transfer_events"] = [bad]
        with pytest.raises(ValidationError):
            normalize_stage2_v2(proposal, document, inventory)


def test_six_frozen_source_outputs_eight_invalid_objects_rejected_before_canonical_gate():
    report = json.loads((ROOT / "examples/evaluations/spec-049-stage2-proposition-contract-diagnosis-20260914/report.json").read_text())
    assert len(report["failure_audits"]) == 6
    failures = [[replay_v1_proposition_shape(item) for item in audit["provider_proposition_objects"]] for audit in report["failure_audits"]]
    assert sum(len(row) for row in failures) == 8
    assert all(errors for row in failures for errors in row)
    assert all(any(errors for errors in row) for row in failures)


def test_non_topological_comparison_becomes_grounded_claim_without_topology():
    proposal = structure(propositions=False, relationship=False)
    run = run_candidate_b_v2(SOURCE, FixtureV2Adapter(structure_proposal=proposal))
    assert run.status is GateStatus.PASS
    assert run.model is not None
    assert run.model.metadata["candidate_version"] == CANDIDATE_B_V2_VERSION
    assert len(run.model.claims) == 1
    assert run.model.claims[0].evidence[0].quote == "A is greater than B."
    assert run.model.propositions == ()
    assert run.model.relationships == ()
    assert StructureDetector().detect(run.model).structures == ()
    run_dict = run.to_dict()
    assert run_dict["candidate_version"] == CANDIDATE_B_V2_VERSION
    assert [item["stage_version"] for item in run_dict["stage_gates"]] == [
        "spec-047-entity-inventory-v1",
        "spec-051-semantic-structure-v2",
        "spec-051-claim-evidence-binding-v2",
    ]
    assert run_dict["attempts"][1]["provider_metadata"]["original_stage2_proposal"] == proposal
    from knowledge_compiler.decomposed_extraction import stable_hash
    assert run.canonical_gate.output_identity_sha256 == stable_hash(run.model.to_dict())


def test_existing_relationship_fit_is_not_coerced_into_proposition():
    run = run_candidate_b_v2(SOURCE, FixtureV2Adapter())
    assert run.status is GateStatus.PASS
    assert run.model is not None
    assert [item.relationship_type.value for item in run.model.relationships] == ["ENABLES"]
    assert run.model.propositions == ()
    assert run.model.claims[0].statement == "A is greater than B."


def test_stage3_cannot_alter_topology_or_bind_inexact_evidence():
    proposal = structure(propositions=False)
    altered = binding(proposal)
    altered["comparison_conditions"] = []
    run = run_candidate_b_v2(SOURCE, FixtureV2Adapter(structure_proposal=proposal, binding_proposal=altered))
    assert run.status is GateStatus.FAIL_CLOSED
    assert run.stage_gates[2].status is GateStatus.FAIL_CLOSED
    mismatch = binding(proposal)
    mismatch["claims"][0]["evidence"][0]["quote"] = "A exceeds B."
    run = run_candidate_b_v2(SOURCE, FixtureV2Adapter(structure_proposal=proposal, binding_proposal=mismatch))
    assert run.status is GateStatus.FAIL_CLOSED
    assert "not found in source" in run.stage_gates[2].exact_failure


@pytest.mark.parametrize("failed_stage, expected_count", [
    (StageName.ENTITY_INVENTORY, 1),
    (StageName.SEMANTIC_STRUCTURE, 2),
    (StageName.CLAIM_EVIDENCE_BINDING, 3),
])
def test_upstream_failure_still_short_circuits_downstream(failed_stage, expected_count):
    adapter = FixtureV2Adapter(fail_stage=failed_stage)
    run = run_candidate_b_v2(SOURCE, adapter)
    assert run.status is GateStatus.FAIL_CLOSED
    assert len(adapter.called) == expected_count
    assert run.canonical_gate.status is GateStatus.NOT_RUN_UPSTREAM_FAILURE


def test_live_capable_v2_adapter_is_authority_gated_before_request():
    adapter = OpenAICandidateBV2Extractor(client=SimpleNamespace(responses=None))
    with pytest.raises(ValidationError, match="requires explicit authority"):
        run_candidate_b_v2(SOURCE, adapter)
    assert adapter.call_ledger.to_dict()["calls_started"] == 0


def test_generic_omission_and_independent_stage3_claim_instructions_are_frozen():
    stage2 = build_stage2_v2_instructions()
    stage3 = build_stage3_v2_instructions()
    assert "Otherwise omit the meaning from" in stage2
    assert "Stage 3 independently reads the exact source" in stage2
    assert "independently preserve source-supported" in stage3
    for source_specific in ("jet stream", "bottleneck", "congressional", "ecological", "mitochondrial"):
        assert source_specific not in stage2.casefold()


def test_existing_assertion_aware_explanatory_behavior_preserves_claim_tier():
    frozen = json.loads((ROOT / "examples/evaluations/spec-016-assertion-aware-representation-20260904/assertion-aware-representation.json").read_text())
    claim_cards = [item for item in frozen["grounded_assertions"] if item["semantic_realization"] == "PRESERVED_AS_CLAIM"]
    assert claim_cards
    assert all(item["evidence"] for item in claim_cards)
    assert all(item["semantic_item_id"] for item in claim_cards)
    assert all(item["presentation_only"] and not item["semantic_relationship_created"] for item in frozen["assertion_participant_attachments"])


def test_spec051_artifacts_regenerate_byte_identically_and_bind_all_frozen_identities(tmp_path):
    canonical = ROOT / OUTPUT_DIRECTORY
    expected = build_artifacts(ROOT)
    left = tmp_path / "left"
    right = tmp_path / "right"
    write_artifacts(ROOT, left)
    write_artifacts(ROOT, right)
    assert {path.name for path in canonical.iterdir()} == set(expected)
    for name in expected:
        assert (left / name).read_bytes() == (right / name).read_bytes()
        assert (left / name).read_bytes() == (canonical / name).read_bytes()
    report = expected["report.json"]
    for identity in [*report["protected_identities"], *report["implementation"]]:
        import hashlib
        assert hashlib.sha256((ROOT / identity["path"]).read_bytes()).hexdigest() == identity["sha256"]
    manifest = expected["future-live-manifest.json"]
    assert len(manifest["sources"]) == 9
    assert [item["ordinal"] for item in manifest["sources"]] == list(range(1, 10))
    assert manifest["maximum_total_provider_calls"] == 27
    assert manifest["current_authorized_provider_calls"] == 0
    assert manifest["status"] == "PROPOSED_NOT_AUTHORIZED"
