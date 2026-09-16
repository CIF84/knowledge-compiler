from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from knowledge_compiler.assertion_aware_representation import (
    AssertionAwareRepresentationBuilder,
    load_frozen_spec013_inputs,
)
from knowledge_compiler.models import KnowledgeModel, ValidationError
from knowledge_compiler.semantic_representation_compiler import compile_semantic_representation
from knowledge_compiler.spec053_claim_representation_diagnosis import (
    CLAIM_PATHS,
    EXPECTED_IDENTITIES,
    EXPERIMENT_CLASSES,
    GAP_CLASSES,
    OUTPUT_PATH,
    PROTECTED_CODE,
    build_report,
    write_report,
)
from knowledge_compiler.structure_detection import StructureDetector


ROOT = Path(__file__).parents[1]


def _report():
    return json.loads((ROOT / OUTPUT_PATH).read_text())


def test_all_98_claims_receive_exactly_one_fixed_terminal_path():
    report = _report()
    traces = report["claim_trace_inventory"]
    assert len(traces) == 98
    assert len({(item["source_id"], item["claim_id"]) for item in traces}) == 98
    assert report["claim_path_taxonomy"] == list(CLAIM_PATHS)
    assert report["claim_path_counts"] == {
        "DEDICATED_REPRESENTATION": 0,
        "SUPPORTING_CONTENT": 0,
        "GENERIC_FALLBACK": 0,
        "NOT_CONSIDERED": 98,
        "FILTERED_OR_DROPPED": 0,
        "AMBIGUOUS": 0,
    }
    assert all(item["terminal_path_classification"] in CLAIM_PATHS for item in traces)
    assert all(item["terminal_path_confidence"] == "HIGH" for item in traces)
    assert all(item["present_in_admitted_knowledge_model"] for item in traces)
    assert all(item["exactly_grounded"] for item in traces)
    assert all(not item["considered_by_representation_planning"] for item in traces)
    assert all(not item["attached_as_supporting_content"] for item in traces)
    assert all(not item["preserved_through_generic_fallback"] for item in traces)
    assert all(item["omitted_before_learner_facing_planning"] for item in traces)


def test_trace_preserves_provenance_and_uses_only_deterministic_relatedness():
    report = _report()
    related = 0
    for item in report["claim_trace_inventory"]:
        assert item["origin"] == "SOURCE"
        assert item["source_sha256"]
        assert item["evidence"]
        assert item["evidence_identity_sha256"] == hashlib.sha256(
            json.dumps(item["evidence"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()
        assert item["relatedness_method"] in {"SHARED_EXACT_EVIDENCE_QUOTE", "NONE_DETERMINISTIC"}
        assert item["related_topology_exists_by_shared_exact_evidence"] == bool(item["related_topology_ids"])
        if item["related_topology_ids"]:
            related += 1
            assert item["related_entity_ids"]
    assert related == 21


def test_current_structure_and_compiler_contracts_exclude_claim_focus_without_dropping_claims():
    model_path = ROOT / (
        "examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915/"
        "sources/01-usgs-divergent-plate-boundaries-1996/admitted-knowledge-model.json"
    )
    model = KnowledgeModel.from_dict(json.loads(model_path.read_text()))
    assert model.claims
    with pytest.raises(ValidationError, match="unsupported compiler semantic class"):
        compile_semantic_representation(model, "claim", model.claims[0].id)
    with_claims = StructureDetector().detect(model).to_dict()
    without_claims = StructureDetector().detect(replace(model, claims=())).to_dict()
    assert with_claims == without_claims


def test_assertion_aware_preserved_as_claim_requires_the_separate_assertion_contract():
    frozen = load_frozen_spec013_inputs(
        ROOT / "examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904"
    )
    representation = AssertionAwareRepresentationBuilder().build(frozen)
    claim_cards = [
        item for item in representation["grounded_assertions"]
        if item["semantic_realization"] == "PRESERVED_AS_CLAIM"
    ]
    assert claim_cards
    assert all(item["semantic_item_id"] for item in claim_cards)
    assert all(item["evidence"] for item in claim_cards)
    assert all(
        item["presentation_only"] and not item["semantic_relationship_created"]
        for item in representation["assertion_participant_attachments"]
    )


def test_diagnosis_and_recommendation_are_singular_owner_gated_and_non_mutating():
    report = _report()
    diagnosis = report["primary_gap_diagnosis"]
    recommendation = report["recommended_next_experiment"]
    assert diagnosis["class"] == "FOCUS_SELECTION_GAP"
    assert diagnosis["class"] in GAP_CLASSES
    assert diagnosis["confidence"] == "HIGH"
    assert recommendation["class"] == "CLAIM_FOCUS_SELECTION_EXPERIMENT"
    assert recommendation["class"] in EXPERIMENT_CLASSES
    assert recommendation["implementation_authorized"] is False
    assert report["owner_review"] == {
        "state": "OWNER_REVIEW", "verdict": "PENDING", "promotion": "NOT_AUTHORIZED"
    }
    integrity = report["integrity_validation"]
    assert integrity["provider_model_calls"] == 0
    assert integrity["external_network_or_evidence_calls"] == 0
    assert integrity["extraction_reruns"] == 0
    assert integrity["production_behavior_changes"] == 0
    assert integrity["topology_created_from_claims"] == 0


def test_diagnostic_forms_and_required_counterfactual_sample_are_complete():
    report = _report()
    counts = report["semantic_character_analysis"]["counts"]
    assert sum(counts.values()) == 98
    assert counts["SCALAR_NUMERIC_COMPARISON"] > 0
    assert counts["DESCRIPTIVE_CONTRAST"] > 0
    assert counts["QUANTITATIVE_FACT"] > 0
    samples = report["learner_value_counterfactual_samples"]
    assert len(samples) == 4
    assert {item["selection_reason"] for item in samples} == {
        "standalone scalar comparison", "descriptive contrast", "quantitative fact",
        "claim sharing exact evidence with existing topology",
    }
    assert all(item["counterfactual_existing_strategy"]["existing_strategy_family"] == "CONCISE_PROSE" for item in samples)
    assert all(item["counterfactual_existing_strategy"]["production_behavior_invoked"] is False for item in samples)
    assert next(item for item in samples if item["selection_reason"].endswith("existing topology"))["related_topology_ids"]


def test_frozen_evidence_and_protected_code_identities_match():
    report = _report()
    evidence = {item["path"]: item["sha256"] for item in report["evidence_identities"]}
    assert evidence == EXPECTED_IDENTITIES
    for path, expected in evidence.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    code = {item["path"]: item["sha256"] for item in report["protected_code_identities"]}
    assert set(code) == set(PROTECTED_CODE)
    for path, expected in code.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected


def test_report_regenerates_byte_identically(tmp_path):
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    expected = build_report(ROOT)
    write_report(ROOT, left)
    write_report(ROOT, right)
    assert left.read_bytes() == right.read_bytes()
    assert left.read_bytes() == (ROOT / OUTPUT_PATH).read_bytes()
    assert json.loads(left.read_text()) == expected


def test_report_records_required_execution_validation():
    assert _report()["validation"] == {
        "deterministic_regeneration": "PASS",
        "focused_diagnostic_and_control_tests": "PASS (83 tests)",
        "full_offline_suite": "PASS (632 tests)",
        "git_diff_check": "PASS",
        "json_validation": "PASS",
        "protected_identity_audit": "PASS (hash-bound tests and empty protected-path diff)",
        "provider_model_network_call_audit": "PASS: zero calls by construction and execution record",
        "secret_safety": "PASS",
    }
