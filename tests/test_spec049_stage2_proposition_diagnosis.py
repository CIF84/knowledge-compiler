from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import pytest


ROOT = Path(__file__).parents[1]
REPORT = (
    ROOT
    / "examples/evaluations/spec-049-stage2-proposition-contract-diagnosis-20260914/report.json"
)
SPEC048 = (
    ROOT
    / "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913"
)

FAILED_SOURCE_DIRECTORIES = {
    "noaa-nesdis-jet-stream-2025": "02-noaa-nesdis-jet-stream-2025",
    "crs-legislative-process-r42843-17": "03-crs-legislative-process-r42843-17",
    "epa-ecological-processes-2026": "05-epa-ecological-processes-2026",
    "doe-iron-platinum-atomic-structure-2017": "06-doe-iron-platinum-atomic-structure-2017",
    "nhgri-dna-fact-sheet-2020": "07-nhgri-dna-fact-sheet-2020",
    "fhwa-traffic-bottleneck-concepts-2016": "08-fhwa-traffic-bottleneck-concepts-2016",
}

CONTRACTS = {
    "COMPARISON_CONDITION": {
        "roles": {"LEFT_OPERAND", "RIGHT_OPERAND", "OUTCOME"},
        "relationship_type": "CAUSES",
        "comparison_operator": "GREATER_THAN",
    },
    "TRANSFER_EVENT": {
        "roles": {"EVENT", "OBJECT", "DESTINATION"},
        "relationship_type": "TRANSFERS_TO",
        "comparison_operator": None,
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _diagnostic_contract_errors(
    proposition: Mapping[str, Any], known_entity_ids: set[str]
) -> list[str]:
    """Offline-only replay of canonical shape rules; never used by extraction."""

    errors: list[str] = []
    proposition_type = proposition.get("proposition_type")
    contract = CONTRACTS.get(proposition_type)
    if contract is None:
        return ["unsupported proposition_type"]
    bindings = proposition.get("role_bindings")
    if not isinstance(bindings, list):
        return ["role_bindings must be an array"]
    roles = [item.get("role") for item in bindings if isinstance(item, Mapping)]
    entity_ids = [item.get("entity_id") for item in bindings if isinstance(item, Mapping)]
    if len(bindings) != 3 or set(roles) != contract["roles"] or len(set(roles)) != len(roles):
        errors.append("roles must be exactly the subtype's three unique required roles")
    if any(entity_id not in known_entity_ids for entity_id in entity_ids):
        errors.append("role entity IDs must come from the frozen inventory")
    if proposition.get("relationship_type") != contract["relationship_type"]:
        errors.append("relationship_type is incompatible with proposition_type")
    if proposition.get("comparison_operator") != contract["comparison_operator"]:
        errors.append("comparison_operator is incompatible with proposition_type")
    if proposition_type == "COMPARISON_CONDITION":
        by_role = {
            item.get("role"): item.get("entity_id")
            for item in bindings
            if isinstance(item, Mapping)
        }
        if (
            by_role.get("LEFT_OPERAND") is not None
            and by_role.get("LEFT_OPERAND") == by_role.get("RIGHT_OPERAND")
        ):
            errors.append("comparison operands must be distinct")
    return errors


def _known_ids(source_directory: str) -> set[str]:
    run = json.loads(
        (SPEC048 / "sources" / source_directory / "candidate-run.json").read_text()
    )
    return {
        entity["id"]
        for entity in run["entity_inventory"]["symbol_table"]["entities"]
    }


def test_all_six_preserved_outputs_fail_the_diagnostic_contract_before_canonical_validation() -> None:
    for source_id, directory in FAILED_SOURCE_DIRECTORIES.items():
        proposal = json.loads(
            (
                SPEC048
                / "sources"
                / directory
                / "stages/02-semantic-structure/parsed-proposal.json"
            ).read_text()
        )
        errors = [
            _diagnostic_contract_errors(item, _known_ids(directory))
            for item in proposal["propositions"]
        ]
        assert any(errors), source_id


def test_diagnostic_contract_preserves_valid_variants_and_rejects_invalid_states() -> None:
    known = {"demand", "supply", "shortage", "transfer", "command", "component"}
    comparison = {
        "proposition_type": "COMPARISON_CONDITION",
        "role_bindings": [
            {"role": "LEFT_OPERAND", "entity_id": "demand"},
            {"role": "RIGHT_OPERAND", "entity_id": "supply"},
            {"role": "OUTCOME", "entity_id": "shortage"},
        ],
        "relationship_type": "CAUSES",
        "comparison_operator": "GREATER_THAN",
    }
    transfer = {
        "proposition_type": "TRANSFER_EVENT",
        "role_bindings": [
            {"role": "EVENT", "entity_id": "transfer"},
            {"role": "OBJECT", "entity_id": "command"},
            {"role": "DESTINATION", "entity_id": "component"},
        ],
        "relationship_type": "TRANSFERS_TO",
        "comparison_operator": None,
    }
    assert _diagnostic_contract_errors(comparison, known) == []
    assert _diagnostic_contract_errors(transfer, known) == []

    mutations = [
        {**comparison, "role_bindings": comparison["role_bindings"][:2]},
        {**comparison, "relationship_type": "AFFECTS"},
        {**comparison, "comparison_operator": None},
        {
            **comparison,
            "role_bindings": [comparison["role_bindings"][0]] * 3,
        },
        {**transfer, "role_bindings": transfer["role_bindings"][:2]},
        {**transfer, "relationship_type": "CAUSES"},
        {**transfer, "comparison_operator": "GREATER_THAN"},
        {
            **transfer,
            "role_bindings": [transfer["role_bindings"][0]] * 3,
        },
    ]
    assert all(_diagnostic_contract_errors(item, known) for item in mutations)


def test_report_is_complete_consistent_and_bound_to_frozen_evidence() -> None:
    report = json.loads(REPORT.read_text())
    assert report["schema"] == "spec-049-stage2-proposition-contract-diagnosis-v1"
    assert report["status"] == "IMPLEMENTED_AWAITING_REVIEW"
    assert report["owner_review"]["state"] == "OWNER_REVIEW"
    assert report["owner_review"]["verdict"] == "PENDING"
    assert len(report["failure_audits"]) == 6
    assert {item["source_id"] for item in report["failure_audits"]} == set(
        FAILED_SOURCE_DIRECTORIES
    )
    assert all(item["current_schema_allowed_combination"] for item in report["failure_audits"])
    assert all(
        item["diagnostic_contract_replay"]["exact_source_output_rejected"]
        for item in report["failure_audits"]
    )
    assert report["aggregate_answers"]["taxonomy_counts"] == {
        "STRUCTURALLY_PREVENTABLE": 1,
        "SEMANTICALLY_WRONG": 0,
        "BOTH_STRUCTURE_AND_SEMANTICS": 5,
        "NOT_SCHEMA_EXPRESSIBLE_OR_AMBIGUOUS": 0,
    }
    assert report["aggregate_answers"]["exact_outputs_prevented_before_canonical_validation"] == 6
    assert report["recommended_branch"] == "MIXED_SIGNAL_MORE_DIAGNOSIS_REQUIRED"
    assert report["controls"]["provider_model_calls"] == 0
    assert report["controls"]["external_network_calls"] == 0

    audits = {item["source_id"]: item for item in report["failure_audits"]}
    for source_id, directory in FAILED_SOURCE_DIRECTORIES.items():
        proposal = json.loads(
            (
                SPEC048
                / "sources"
                / directory
                / "stages/02-semantic-structure/parsed-proposal.json"
            ).read_text()
        )
        invalid = [
            item
            for item in proposal["propositions"]
            if _diagnostic_contract_errors(item, _known_ids(directory))
        ]
        assert audits[source_id]["provider_proposition_objects"] == invalid

    for evidence in report["immutable_evidence"]:
        path = ROOT / evidence["path"]
        assert path.is_file()
        assert _sha256(path) == evidence["sha256"]
    for audit in report["failure_audits"]:
        for evidence in audit["evidence"].values():
            path = ROOT / evidence["path"]
            assert path.is_file()
            assert _sha256(path) == evidence["sha256"]


@pytest.mark.parametrize(
    "protected_path",
    [
        "src/knowledge_compiler/models.py",
        "src/knowledge_compiler/openai_decomposed_extractor.py",
        "src/knowledge_compiler/decomposed_extraction.py",
        "examples/evaluations/spec-047-decomposed-extraction-ab-harness-20260913/candidate-b-contract.json",
        "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/final-report.json",
        "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/post-run-failure-taxonomy-audit.json",
    ],
)
def test_report_records_the_exact_protected_identity(protected_path: str) -> None:
    report = json.loads(REPORT.read_text())
    recorded = {item["path"]: item["sha256"] for item in report["protected_identities"]}
    assert recorded[protected_path] == _sha256(ROOT / protected_path)
