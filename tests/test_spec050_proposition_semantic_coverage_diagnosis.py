from __future__ import annotations

import hashlib
import json
from pathlib import Path

from knowledge_compiler.models import Claim, KnowledgeModel, Origin, SourceDocument, SourceSpan
from knowledge_compiler.structure_detection import StructureDetector


ROOT = Path(__file__).parents[1]
REPORT = (
    ROOT
    / "examples/evaluations/spec-050-proposition-semantic-coverage-diagnosis-20260914/report.json"
)
SPEC049 = json.loads(
    (
        ROOT
        / "examples/evaluations/spec-049-stage2-proposition-contract-diagnosis-20260914/report.json"
    ).read_text()
)

DESTINATIONS = {
    "CANONICAL_PROPOSITION_FIT",
    "EXISTING_RELATIONSHIP_FIT",
    "CLAIM_ONLY_FIT",
    "TRUE_SEMANTIC_COVERAGE_GAP",
    "AMBIGUOUS",
}
BRANCHES = {
    "SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION",
    "SEMANTIC_MODEL_EXPANSION_DIAGNOSIS",
    "ABANDON_DECOMPOSITION_RETURN_TO_CONTROL_A",
    "MORE_EVIDENCE_REQUIRED",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_report_reconstructs_exactly_five_mixed_cases_and_one_control() -> None:
    report = json.loads(REPORT.read_text())
    prior = {item["source_id"]: item for item in SPEC049["failure_audits"]}
    mixed = report["mixed_cases"]
    assert len(mixed) == 5
    assert {item["source_id"] for item in mixed} == {
        source_id
        for source_id, item in prior.items()
        if item["primary_diagnosis"] == "BOTH_STRUCTURE_AND_SEMANTICS"
    }
    for item in mixed:
        assert item["spec049_diagnosis"] == "BOTH_STRUCTURE_AND_SEMANTICS"
        assert item["candidate_proposition_objects"] == prior[item["source_id"]][
            "provider_proposition_objects"
        ]
        assert item["primary_destination"] in DESTINATIONS
        assert {
            "canonical_proposition_test",
            "existing_relationship_test",
            "claim_only_test",
            "true_coverage_gap_test",
        } <= set(item)

    control = report["structural_only_control"]
    prior_control = prior[control["source_id"]]
    assert prior_control["primary_diagnosis"] == "STRUCTURALLY_PREVENTABLE"
    assert control["candidate_proposition_objects"] == prior_control[
        "provider_proposition_objects"
    ]
    assert control["semantic_destination"] == "CANONICAL_PROPOSITION_FIT"


def test_fixed_taxonomies_counts_and_single_branch_are_consistent() -> None:
    report = json.loads(REPORT.read_text())
    destinations = [item["primary_destination"] for item in report["mixed_cases"]]
    assert set(destinations) <= DESTINATIONS
    assert report["aggregate_answers"]["destination_counts"] == {
        name: destinations.count(name) for name in sorted(DESTINATIONS)
    }
    assert report["aggregate_answers"]["destination_counts"] == {
        "AMBIGUOUS": 0,
        "CANONICAL_PROPOSITION_FIT": 0,
        "CLAIM_ONLY_FIT": 4,
        "EXISTING_RELATIONSHIP_FIT": 1,
        "TRUE_SEMANTIC_COVERAGE_GAP": 0,
    }
    assert report["recommended_branch"] in BRANCHES
    assert report["recommended_branch"] == (
        "SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION"
    )
    assert isinstance(report["recommended_branch"], str)


def test_every_evidence_and_protected_identity_hash_is_exact() -> None:
    report = json.loads(REPORT.read_text())
    records = [*report["immutable_evidence"], *report["protected_identities"]]
    for item in report["mixed_cases"]:
        records.append(item["control_a_comparison"]["evidence"])
    records.append(report["structural_only_control"]["control_a_comparison"]["evidence"])
    for record in records:
        path = ROOT / record["path"]
        assert path.is_file(), record["path"]
        assert _sha256(path) == record["sha256"], record["path"]


def test_source_support_is_exactly_present_in_each_frozen_source() -> None:
    report = json.loads(REPORT.read_text())
    sources = {}
    for record in report["immutable_evidence"]:
        if record["path"].endswith("/source.json"):
            value = json.loads((ROOT / record["path"]).read_text())
            sources[value["source_id"]] = value["text"]
    for item in report["mixed_cases"]:
        source = sources[item["source_id"]]
        assert item["source_support"]
        assert all(source.count(quote) == 1 for quote in item["source_support"])


def test_claim_only_meaning_remains_grounded_but_creates_no_false_topology() -> None:
    text = "Alpha is greater than beta."
    document = SourceDocument(id="semantic-destination-control", text=text)
    span = SourceSpan(
        document_id=document.id,
        start_char=0,
        end_char=len(text),
        quote=text,
    )
    claim = Claim(
        id="claim-comparison",
        statement=text,
        evidence=(span,),
        confidence=1.0,
        origin=Origin.SOURCE,
    )
    model = KnowledgeModel(
        document=document,
        entities=(),
        claims=(claim,),
        relationships=(),
        propositions=(),
    )
    restored = KnowledgeModel.from_dict(model.to_dict())
    assert restored.claims == (claim,)
    assert StructureDetector().detect(restored).structures == ()


def test_report_records_zero_calls_zero_changes_and_owner_gate() -> None:
    report = json.loads(REPORT.read_text())
    assert report["schema"] == "spec-050-proposition-semantic-coverage-diagnosis-v1"
    assert report["status"] == "IMPLEMENTED_AWAITING_REVIEW"
    assert report["controls"] == {
        "candidate_b_v1_changes": 0,
        "canonical_semantic_model_changes": 0,
        "external_network_calls": 0,
        "historical_output_repairs": 0,
        "production_changes": 0,
        "provider_model_calls": 0,
        "retries": 0,
    }
    assert report["owner_review"] == {
        "promotion": "NOT_AUTHORIZED",
        "state": "OWNER_REVIEW",
        "verdict": "PENDING",
    }
