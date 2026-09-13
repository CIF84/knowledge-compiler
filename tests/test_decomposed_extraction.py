from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from knowledge_compiler.decomposed_ab_evaluation import (
    build_ab_comparison,
    candidate_comparison_record,
    load_historical_control_records,
    proposed_live_manifest,
    summarize_arm,
    write_spec047_artifacts,
)
from knowledge_compiler.decomposed_extraction import (
    GateStatus,
    StageAttempt,
    StageName,
    freeze_entity_inventory,
    run_candidate_b,
    validate_claim_evidence_binding,
    validate_semantic_structure,
)
from knowledge_compiler.models import SourceDocument, ValidationError
from knowledge_compiler.openai_decomposed_extractor import (
    OpenAIDecomposedExtractor,
    ProviderCallLedger,
    build_claim_evidence_instructions,
    build_entity_inventory_instructions,
    build_semantic_structure_instructions,
    claim_evidence_schema,
    entity_inventory_schema,
    frozen_stage_contracts,
    semantic_structure_schema,
)


ROOT = Path(__file__).parents[1]
SOURCE = "A controller causes a pump to start. The pump is part of the water system."


def entity_proposal() -> dict:
    return {
        "symbols": [
            {"name": "controller", "description": "A controller.", "entity_type": "COMPONENT", "aliases": []},
            {"name": "pump", "description": "A pump.", "entity_type": "COMPONENT", "aliases": []},
            {"name": "water system", "description": "A water system.", "entity_type": "SYSTEM", "aliases": []},
        ]
    }


def structure_proposal() -> dict:
    return {
        "relationships": [
            {
                "id": "controller-causes-pump",
                "source_entity_id": "controller",
                "relationship_type": "CAUSES",
                "target_entity_id": "pump",
                "statement": "A controller causes a pump to start.",
                "confidence": 0.98,
                "origin": "SOURCE",
            },
            {
                "id": "pump-part-of-system",
                "source_entity_id": "pump",
                "relationship_type": "PART_OF",
                "target_entity_id": "water-system",
                "statement": "The pump is part of the water system.",
                "confidence": 0.98,
                "origin": "SOURCE",
            },
        ],
        "propositions": [],
        "missing_symbols": [],
    }


def binding_proposal() -> dict:
    return {
        "claims": [],
        "semantic_evidence_bindings": [
            {"semantic_object_id": "controller-causes-pump", "evidence": [{"quote": "A controller causes a pump to start."}]},
            {"semantic_object_id": "pump-part-of-system", "evidence": [{"quote": "The pump is part of the water system."}]},
        ],
    }


class FixtureAdapter:
    live_capable = False

    def __init__(self, *, fail_stage: StageName | None = None) -> None:
        self.fail_stage = fail_stage
        self.called: list[StageName] = []
        self.call_ledger = {"calls_started": 0, "entries": []}

    def _result(self, stage: StageName, value: dict) -> StageAttempt:
        self.called.append(stage)
        if self.fail_stage is stage:
            raise ValidationError(f"fixture {stage.value} failed")
        return StageAttempt(stage, value, {"live_call": False})

    def extract_entity_inventory(self, document):
        return self._result(StageName.ENTITY_INVENTORY, entity_proposal())

    def extract_semantic_structure(self, document, inventory):
        return self._result(StageName.SEMANTIC_STRUCTURE, structure_proposal())

    def extract_claim_evidence(self, document, inventory, structure):
        return self._result(StageName.CLAIM_EVIDENCE_BINDING, binding_proposal())


def test_valid_three_stage_flow_reaches_unchanged_model_and_downstream_compiler() -> None:
    result = run_candidate_b(
        SOURCE, FixtureAdapter(), source_metadata={"source_id": "fixture"}
    )
    assert result.status is GateStatus.PASS
    assert [item.status for item in result.stage_gates] == [GateStatus.PASS] * 3
    assert result.canonical_gate.status is GateStatus.PASS
    assert result.model is not None
    assert len(result.model.entities) == 3
    assert len(result.model.relationships) == 2
    record = candidate_comparison_record(result)
    assert record["status"] == "PASS"
    assert record["detected_structure_count"] >= 1
    assert record["detected_structure_types"] == {"HIERARCHY": 1}
    assert record["representation_strategy_counts"]
    assert record["sufficient_representation_decision_count"] >= 1


def test_stage_1_freezes_stable_ids_and_fails_duplicate_or_conflicting_inventory() -> None:
    document = SourceDocument("fixture", SOURCE)
    first = freeze_entity_inventory(entity_proposal(), document)
    reordered = {"symbols": list(reversed(entity_proposal()["symbols"]))}
    second = freeze_entity_inventory(reordered, document)
    assert first.identity_sha256 == second.identity_sha256
    assert first.ids == frozenset({"controller", "pump", "water-system"})
    duplicate = entity_proposal()
    duplicate["symbols"].append(dict(duplicate["symbols"][0]))
    with pytest.raises(ValidationError, match="duplicate entity"):
        freeze_entity_inventory(duplicate, document)

    conflict = entity_proposal()
    conflict["symbols"][0]["aliases"] = ["pump"]
    with pytest.raises(ValidationError, match="alias.*conflicts"):
        freeze_entity_inventory(conflict, document)


def test_stage_2_cannot_add_entities_or_reference_undeclared_ids() -> None:
    document = SourceDocument("fixture", SOURCE)
    inventory = freeze_entity_inventory(entity_proposal(), document)
    adding = structure_proposal()
    adding["entities"] = []
    with pytest.raises(ValidationError, match="unknown=.*entities"):
        validate_semantic_structure(adding, document, inventory)
    unknown = structure_proposal()
    unknown["relationships"][0]["target_entity_id"] = "undeclared"
    with pytest.raises(ValidationError, match="unknown frozen entities"):
        validate_semantic_structure(unknown, document, inventory)


def test_stage_3_cannot_change_topology_and_exact_evidence_mismatch_fails_closed() -> None:
    document = SourceDocument("fixture", SOURCE)
    inventory = freeze_entity_inventory(entity_proposal(), document)
    structure = validate_semantic_structure(structure_proposal(), document, inventory)
    altered = binding_proposal()
    altered["relationships"] = []
    with pytest.raises(ValidationError, match="unknown=.*relationships"):
        validate_claim_evidence_binding(altered, document, structure)
    mismatch = binding_proposal()
    mismatch["semantic_evidence_bindings"][0]["evidence"][0]["quote"] = (
        "A controller starts a pump."
    )
    with pytest.raises(ValidationError, match="not found in source"):
        validate_claim_evidence_binding(mismatch, document, structure)


@pytest.mark.parametrize(
    ("failed_stage", "expected_calls", "expected_statuses"),
    [
        (
            StageName.ENTITY_INVENTORY,
            [StageName.ENTITY_INVENTORY],
            [GateStatus.FAIL_CLOSED, GateStatus.NOT_RUN_UPSTREAM_FAILURE, GateStatus.NOT_RUN_UPSTREAM_FAILURE],
        ),
        (
            StageName.SEMANTIC_STRUCTURE,
            [StageName.ENTITY_INVENTORY, StageName.SEMANTIC_STRUCTURE],
            [GateStatus.PASS, GateStatus.FAIL_CLOSED, GateStatus.NOT_RUN_UPSTREAM_FAILURE],
        ),
        (
            StageName.CLAIM_EVIDENCE_BINDING,
            [StageName.ENTITY_INVENTORY, StageName.SEMANTIC_STRUCTURE, StageName.CLAIM_EVIDENCE_BINDING],
            [GateStatus.PASS, GateStatus.PASS, GateStatus.FAIL_CLOSED],
        ),
    ],
)
def test_upstream_failure_short_circuits_downstream_stages(
    failed_stage, expected_calls, expected_statuses
) -> None:
    adapter = FixtureAdapter(fail_stage=failed_stage)
    result = run_candidate_b(SOURCE, adapter)
    assert adapter.called == expected_calls
    assert [item.status for item in result.stage_gates] == expected_statuses
    assert result.canonical_gate.status is GateStatus.NOT_RUN_UPSTREAM_FAILURE
    assert result.model is None


def test_live_capable_adapter_requires_explicit_authority_before_invocation() -> None:
    adapter = OpenAIDecomposedExtractor(client=SimpleNamespace(responses=None))
    with pytest.raises(ValidationError, match="requires explicit authority"):
        run_candidate_b(SOURCE, adapter)
    assert adapter.call_ledger.to_dict()["calls_started"] == 0


class RaisingResponses:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        raise RuntimeError("synthetic provider failure")


class SuccessfulResponses:
    def __init__(self) -> None:
        self.calls = []
        self.outputs = [entity_proposal(), structure_proposal(), binding_proposal()]

    def create(self, **kwargs):
        self.calls.append(kwargs)
        ordinal = len(self.calls)
        output = self.outputs[ordinal - 1]
        return SimpleNamespace(
            id=f"response-{ordinal}",
            _request_id=f"request-{ordinal}",
            model="gpt-5.6-luna",
            output_text=json.dumps(output),
            usage=SimpleNamespace(
                input_tokens=10 * ordinal,
                output_tokens=5 * ordinal,
                total_tokens=15 * ordinal,
            ),
        )


def test_provider_call_accounting_occurs_when_request_starts() -> None:
    responses = RaisingResponses()
    ledger = ProviderCallLedger()
    adapter = OpenAIDecomposedExtractor(
        client=SimpleNamespace(responses=responses), call_ledger=ledger
    )
    result = run_candidate_b(SOURCE, adapter, allow_live=True)
    assert result.status is GateStatus.FAIL_CLOSED
    assert len(responses.calls) == 1
    recorded = ledger.to_dict()
    assert recorded["calls_started"] == 1
    assert recorded["entries"][0]["status"] == "PROVIDER_REQUEST_FAILED"
    assert result.stage_gates[1].status is GateStatus.NOT_RUN_UPSTREAM_FAILURE


def test_mocked_live_adapter_makes_exactly_three_frozen_zero_retry_calls() -> None:
    responses = SuccessfulResponses()
    adapter = OpenAIDecomposedExtractor(
        client=SimpleNamespace(responses=responses)
    )
    result = run_candidate_b(
        SOURCE,
        adapter,
        source_metadata={"source_id": "synthetic-mocked-provider"},
        allow_live=True,
    )
    assert result.status is GateStatus.PASS
    assert len(responses.calls) == 3
    assert all(call["model"] == "gpt-5.6-luna" for call in responses.calls)
    assert all(call["store"] is False for call in responses.calls)
    assert all(call["reasoning"] == {"effort": "low"} for call in responses.calls)
    assert [
        call["text"]["format"]["name"] for call in responses.calls
    ] == [
        "candidate_b_entity_inventory",
        "candidate_b_semantic_structure",
        "candidate_b_claim_evidence_binding",
    ]
    ledger = result.provider_call_ledger
    assert ledger["calls_started"] == 3
    assert [item["provider_response_id"] for item in ledger["entries"]] == [
        "response-1", "response-2", "response-3"
    ]
    assert sum(item["usage"]["total_tokens"] for item in ledger["entries"]) == 90


def test_openai_client_disables_sdk_retries(monkeypatch) -> None:
    captured = {}

    def fake_openai(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(responses=SuccessfulResponses())

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=fake_openai))
    adapter = OpenAIDecomposedExtractor(api_key="synthetic-not-a-secret")
    adapter._client_or_create()
    assert captured == {
        "api_key": "synthetic-not-a-secret",
        "max_retries": 0,
    }


def test_stage_schemas_and_prompts_enforce_separation_and_frozen_ids() -> None:
    stage_1 = entity_inventory_schema()
    assert set(stage_1["properties"]) == {"symbols"}
    stage_2 = semantic_structure_schema(frozenset({"a", "b"}))
    assert set(stage_2["properties"]) == {
        "relationships", "propositions", "missing_symbols"
    }
    assert "entities" not in stage_2["properties"]
    endpoint = stage_2["properties"]["relationships"]["items"]["properties"]["source_entity_id"]
    assert endpoint["enum"] == ["a", "b"]
    stage_3 = claim_evidence_schema(frozenset({"rel-1"}))
    assert set(stage_3["properties"]) == {"claims", "semantic_evidence_bindings"}
    assert "relationships" not in stage_3["properties"]
    assert "entities" not in stage_3["properties"]
    assert "Return entities only" in build_entity_inventory_instructions()
    assert "Do not return claims or evidence" in build_semantic_structure_instructions()
    assert "must not add, delete, rename, reorder, or alter" in build_claim_evidence_instructions()
    contracts = frozen_stage_contracts()
    assert len(contracts["stages"]) == 3
    assert all(item["prompt_sha256"] and item["schema_sha256"] for item in contracts["stages"])


def test_historical_control_adapter_and_future_manifest_are_exact_and_nonexecuting() -> None:
    records = load_historical_control_records(ROOT)
    assert len(records) == 9
    assert sum(item["status"] == "PASS" for item in records) == 4
    assert sum(item["status"] == "FAILED_CLOSED" for item in records) == 5
    assert all(item["execution_mode"] == "HISTORICAL_FROZEN" for item in records)
    assert all(item["provider_calls_started"] == 1 for item in records)
    manifest = proposed_live_manifest(ROOT)
    assert manifest["status"] == "PROPOSED_NOT_AUTHORIZED"
    assert manifest["candidate_b"]["maximum_total_calls"] == 27
    assert manifest["candidate_b"]["expected_total_calls"] is None
    assert manifest["candidate_b"]["store"] is False
    assert manifest["candidate_b"]["frozen_stage_contract_sha256"]
    assert len(manifest["fixed_source_order"]) == 9
    assert {
        (item["source_id"], item["source_sha256"])
        for item in manifest["fixed_source_order"]
    } == {
        (item["source_id"], item["source_sha256"])
        for item in records
    }
    assert [item["sha256"] for item in manifest["source_packets"]] == [
        "ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0",
        "85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b",
    ]
    assert manifest["blind_source_text_embedded"] is False
    assert manifest["authorization_granted"] is False
    summary = summarize_arm(records)
    assert summary["attempted_sources"] == 9
    assert summary["admitted_sources"] == 4
    assert summary["source_admission_rate"] == pytest.approx(4 / 9)
    assert summary["known_invalid_objects_admitted"] == 0
    assert summary["failure_origin_distribution"] == {
        "ENTITY_INVENTORY": 3,
        "EVIDENCE_FIDELITY": 1,
        "PROPOSITION_CONSTRUCTION": 1,
        "RELATIONSHIP_SEMANTICS": 2,
    }


def test_ab_harness_requires_identical_sources_and_reserves_verdict_for_owner() -> None:
    candidate_run = run_candidate_b(
        SOURCE,
        FixtureAdapter(),
        source_metadata={"source_id": "shared-source"},
    )
    candidate = candidate_comparison_record(candidate_run)
    control = {
        **candidate,
        "arm": "CONTROL_A",
        "execution_mode": "HISTORICAL_FROZEN",
    }
    comparison = build_ab_comparison([control], [candidate])
    assert comparison["owner_verdict"] == "PENDING"
    assert comparison["arm_summaries"]["CONTROL_A"]["admitted_sources"] == 1
    with pytest.raises(ValueError, match="same frozen source IDs"):
        build_ab_comparison(
            [{**control, "source_id": "different-source"}], [candidate]
        )


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.glob("*.json"))
    }


def test_spec047_artifacts_regenerate_deterministically_without_blind_execution(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_spec047_artifacts(ROOT, first)
    write_spec047_artifacts(ROOT, second)
    assert _directory_hashes(first) == _directory_hashes(second)
    report = json.loads((first / "report.json").read_text())
    assert report["execution_integrity"] == {
        "provider_calls": 0,
        "model_calls": 0,
        "external_source_retrievals": 0,
        "blind_corpus_candidate_b_executions": 0,
        "control_a_reruns": 0,
        "repairs": 0,
        "behavior_changes_outside_candidate_and_harness": 0,
    }
    assert report["future_execution"]["maximum_candidate_b_calls"] == 27


def test_control_a_and_canonical_validator_hashes_remain_frozen() -> None:
    expected = {
        "src/knowledge_compiler/blind_evaluation.py": "cd4311f7504cb3af02c9d74f5721f3cf64e11b7aec374e9936afd9fa17cf7873",
        "src/knowledge_compiler/blind_evaluation_harness.py": "6b9fcb305d5323913562e7d3c83f1516b58a384d5d237a8d6731f67c518b48e4",
        "src/knowledge_compiler/openai_extractor.py": "3152640aa23a5049591d83b48f706d33e207d415dab311e67a58cfbf88067be3",
        "src/knowledge_compiler/models.py": "671b5ad6fddc6edb5912bd5b3596fac56f5ba2d6351795af662a56002f6a244e",
        "src/knowledge_compiler/proposition_validation.py": "637ad67b0b28320820a4b0a43745fc97b866fa6d2b20b204148adbe30a9ef3f5",
    }
    assert {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in expected
    } == expected
