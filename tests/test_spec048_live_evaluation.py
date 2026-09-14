from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from knowledge_compiler.blind_evaluation import BlindSource
from knowledge_compiler.decomposed_extraction import (
    CandidateBRun,
    GateStatus,
    StageAttempt,
    StageGateResult,
    StageName,
    run_candidate_b,
)
from knowledge_compiler.spec048_live_evaluation import (
    EXPECTED_SOURCES,
    build_preflight,
    mechanically_supported_branch,
    persist_source_run,
    validate_execution,
)


ROOT = Path(__file__).parents[1]
SOURCE = "A controller causes a pump to start. The pump is part of the water system."


class FixtureAdapter:
    live_capable = False
    call_ledger = {"calls_started": 0, "entries": []}

    def extract_entity_inventory(self, document):
        return StageAttempt(
            StageName.ENTITY_INVENTORY,
            {"symbols": [
                {"name": "controller", "description": "A controller.", "entity_type": "COMPONENT", "aliases": []},
                {"name": "pump", "description": "A pump.", "entity_type": "COMPONENT", "aliases": []},
                {"name": "water system", "description": "A water system.", "entity_type": "SYSTEM", "aliases": []},
            ]},
            {"live_call": False},
            {"synthetic": True},
        )

    def extract_semantic_structure(self, document, inventory):
        return StageAttempt(
            StageName.SEMANTIC_STRUCTURE,
            {
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
            },
            {"live_call": False},
            {"synthetic": True},
        )

    def extract_claim_evidence(self, document, inventory, structure):
        return StageAttempt(
            StageName.CLAIM_EVIDENCE_BINDING,
            {
                "claims": [],
                "semantic_evidence_bindings": [
                    {"semantic_object_id": "controller-causes-pump", "evidence": [{"quote": "A controller causes a pump to start."}]},
                    {"semantic_object_id": "pump-part-of-system", "evidence": [{"quote": "The pump is part of the water system."}]},
                ],
            },
            {"live_call": False},
            {"synthetic": True},
        )


def test_preflight_matches_every_frozen_identity_without_requiring_a_credential() -> None:
    result = build_preflight(ROOT, require_api_key=False)
    assert result["status"] == "PASS"
    assert result["source_count"] == 9
    assert result["model"] == "gpt-5.6-luna"
    assert result["store"] is False
    assert result["all_retry_classes"] == 0
    assert all(item["status"] == "PASS" for item in result["checks"])


def test_source_evidence_persists_all_stages_and_downstream_outputs(tmp_path: Path) -> None:
    run = run_candidate_b(
        SOURCE,
        FixtureAdapter(),
        source_metadata={"source_id": "synthetic-control-system"},
    )
    source = BlindSource(
        source_id="synthetic-control-system",
        title="Synthetic control system",
        text=SOURCE,
        source_sha256=hashlib.sha256(SOURCE.encode()).hexdigest(),
        provenance={"kind": "synthetic"},
    )
    outcome = persist_source_run(tmp_path, source, run)
    assert outcome["status"] == "PASS"
    assert outcome["detection_stage"] is None
    assert (tmp_path / "admitted-knowledge-model.json").exists()
    assert (tmp_path / "detected-structures.json").exists()
    assert (tmp_path / "representation-decisions.json").exists()
    for index, stage in enumerate(
        ("entity-inventory", "semantic-structure", "claim-evidence-binding"), start=1
    ):
        directory = tmp_path / "stages" / f"{index:02d}-{stage}"
        assert json.loads((directory / "gate.json").read_text())["status"] == "PASS"
        assert (directory / "raw-provider-response.json").exists()


def _failed_run(source_id: str, source_sha256: str) -> CandidateBRun:
    stage_1 = StageGateResult(
        StageName.ENTITY_INVENTORY,
        GateStatus.FAIL_CLOSED,
        source_sha256,
        exact_failure="synthetic failure",
        error_type="ValidationError",
    )
    return CandidateBRun(
        source_id=source_id,
        source_sha256=source_sha256,
        status=GateStatus.FAIL_CLOSED,
        stage_gates=(
            stage_1,
            StageGateResult(StageName.SEMANTIC_STRUCTURE, GateStatus.NOT_RUN_UPSTREAM_FAILURE, None),
            StageGateResult(StageName.CLAIM_EVIDENCE_BINDING, GateStatus.NOT_RUN_UPSTREAM_FAILURE, None),
        ),
        canonical_gate=StageGateResult(
            StageName.CANONICAL_VALIDATION, GateStatus.NOT_RUN_UPSTREAM_FAILURE, None
        ),
        attempts=(),
        model=None,
        inventory=None,
        structure=None,
        binding=None,
        provider_call_ledger={
            "calls_started": 1,
            "entries": [{
                "stage": "ENTITY_INVENTORY",
                "sdk_retries": 0,
                "hidden_retries": 0,
                "semantic_retries": 0,
                "repair_calls": 0,
                "store": False,
            }],
        },
    )


def test_execution_validation_enforces_order_short_circuit_and_call_accounting() -> None:
    sources = [
        SimpleNamespace(source_id=source_id, source_sha256=digest)
        for source_id, digest in EXPECTED_SOURCES
    ]
    runs = [_failed_run(source.source_id, source.source_sha256) for source in sources]
    result = validate_execution(sources, runs)
    assert result["provider_calls"] == 9
    assert result["short_circuiting"] is True
    broken = list(runs)
    broken[0] = CandidateBRun(
        **{
            **{field: getattr(runs[0], field) for field in runs[0].__dataclass_fields__},
            "provider_call_ledger": {
                "calls_started": 2,
                "entries": [
                    *runs[0].provider_call_ledger["entries"],
                    {**runs[0].provider_call_ledger["entries"][0]},
                ],
            },
        }
    )
    with pytest.raises(RuntimeError, match="per-stage call ceiling"):
        validate_execution(sources, broken)


@pytest.mark.parametrize(
    ("control_admitted", "candidate_admitted", "invalid", "expected"),
    [
        (4, 3, 0, "B_REGRESSION"),
        (4, 4, 0, "B_NO_MATERIAL_GAIN"),
        (4, 5, 0, "INCONCLUSIVE"),
        (4, 6, 0, "B_CLEAR_IMPROVEMENT"),
        (4, 6, 1, "B_REGRESSION"),
    ],
)
def test_mechanical_branch_is_frozen_and_conservative(
    control_admitted, candidate_admitted, invalid, expected
) -> None:
    comparison = {
        "arm_summaries": {
            "CONTROL_A": {
                "admitted_sources": control_admitted,
                "known_invalid_objects_admitted": 0,
                "admitted_semantic_totals": {
                    "entities": 40, "relationships": 20, "propositions": 0, "claims": 20
                },
            },
            "CANDIDATE_B": {
                "admitted_sources": candidate_admitted,
                "known_invalid_objects_admitted": invalid,
                "admitted_semantic_totals": {
                    "entities": 60, "relationships": 30, "propositions": 0, "claims": 30
                },
            },
        }
    }
    assert mechanically_supported_branch(comparison) == expected
