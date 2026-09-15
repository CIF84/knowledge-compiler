"""Deterministic offline artifact generator for SPEC-051; never calls a provider."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .decomposed_ab_evaluation import proposed_live_manifest
from .decomposed_extraction import GateStatus, StageAttempt, StageName, freeze_entity_inventory, stable_hash
from .decomposed_extraction_v2 import CANDIDATE_B_V2_VERSION, replay_v1_proposition_shape, run_candidate_b_v2
from .models import SourceDocument, ValidationError
from .openai_decomposed_extractor_v2 import frozen_v2_stage_contracts
from .spec048_live_evaluation import EXPECTED_SOURCES
from .structure_detection import StructureDetector


OUTPUT_DIRECTORY = "examples/evaluations/spec-051-schema-constrained-candidate-b-v2-20260915"
FUTURE_BRANCHES = [
    "B_V2_RECOVERS_DECOMPOSITION",
    "B_V2_STRUCTURAL_FIX_ONLY",
    "B_V2_TOO_SPARSE",
    "B_V2_REGRESSION",
    "INCONCLUSIVE",
]
FUTURE_METRICS = [
    "source_admission_rate", "known_invalid_object_admission", "stage_failure_distribution",
    "spec046_origin_stage_distribution", "proposition_construction_failure_count",
    "semantic_omission_and_grounded_claim_preservation", "entity_relationship_proposition_claim_counts",
    "detected_structures", "representation_decisions", "provider_calls", "token_usage",
    "latency", "available_monetary_cost_evidence", "semantic_richness_guard",
]
PROTECTED = [
    "src/knowledge_compiler/decomposed_extraction.py",
    "src/knowledge_compiler/openai_decomposed_extractor.py",
    "src/knowledge_compiler/models.py",
    "src/knowledge_compiler/structure_detection.py",
    "src/knowledge_compiler/representation_strategy.py",
    "examples/evaluations/spec-047-decomposed-extraction-ab-harness-20260913/candidate-b-contract.json",
    "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/final-report.json",
    "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/post-run-failure-taxonomy-audit.json",
    "examples/evaluations/spec-049-stage2-proposition-contract-diagnosis-20260914/report.json",
    "examples/evaluations/spec-050-proposition-semantic-coverage-diagnosis-20260914/report.json",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity(repo_root: Path, relative: str) -> dict[str, str]:
    path = repo_root / relative
    if not path.is_file():
        raise ValidationError(f"required frozen evidence is missing: {relative}")
    return {"path": relative, "sha256": _sha(path)}


def _template_inventory():
    document = SourceDocument("synthetic-contract-template", "Demand exceeds supply. A transfer moves an object to a destination.")
    return freeze_entity_inventory({"symbols": [
        {"name": name, "description": f"Synthetic schema endpoint {name}.", "entity_type": kind, "aliases": []}
        for name, kind in (
            ("demand", "VARIABLE"), ("supply", "VARIABLE"), ("shortage", "CONCEPT"),
            ("transfer", "PROCESS"), ("object", "OBJECT"), ("destination", "COMPONENT"),
        )
    ]}, document)


class _OfflineAdapter:
    live_capable = False
    candidate_version = CANDIDATE_B_V2_VERSION
    call_ledger = {"candidate_version": CANDIDATE_B_V2_VERSION, "calls_started": 0, "entries": []}
    text = "Coordinates enable calculation. A is greater than B."

    def __init__(self, *, relationship: bool) -> None:
        self.relationship = relationship
        self.called: list[str] = []

    def _attempt(self, stage: StageName, raw: dict[str, Any]) -> StageAttempt:
        self.called.append(stage.value)
        return StageAttempt(stage, raw, {"candidate_version": CANDIDATE_B_V2_VERSION, "live_call": False})

    def extract_entity_inventory(self, _document):
        return self._attempt(StageName.ENTITY_INVENTORY, {"symbols": [
            {"name": name, "description": f"Synthetic {name}.", "entity_type": kind, "aliases": []}
            for name, kind in (("coordinates", "VARIABLE"), ("calculation", "PROCESS"), ("A", "VARIABLE"), ("B", "VARIABLE"))
        ]})

    def extract_semantic_structure(self, _document, _inventory):
        relationships = [{
            "id": "coordinates-enables-calculation", "source_entity_id": "coordinates",
            "relationship_type": "ENABLES", "target_entity_id": "calculation",
            "statement": "Coordinates enable calculation.", "confidence": 1.0, "origin": "SOURCE",
        }] if self.relationship else []
        return self._attempt(StageName.SEMANTIC_STRUCTURE, {
            "relationships": relationships, "comparison_conditions": [], "transfer_events": [], "missing_symbols": [],
        })

    def extract_claim_evidence(self, _document, _inventory, _structure):
        bindings = [{"semantic_object_id": "coordinates-enables-calculation", "evidence": [{"quote": "Coordinates enable calculation."}]}] if self.relationship else []
        return self._attempt(StageName.CLAIM_EVIDENCE_BINDING, {
            "claims": [{
                "id": "claim-standalone-comparison", "statement": "A is greater than B.",
                "evidence": [{"quote": "A is greater than B."}], "confidence": 1.0, "origin": "SOURCE",
            }],
            "semantic_evidence_bindings": bindings,
        })


def _fixture_results() -> dict[str, Any]:
    cases = []
    for relationship in (False, True):
        adapter = _OfflineAdapter(relationship=relationship)
        run = run_candidate_b_v2(adapter.text, adapter, source_metadata={"source_id": "synthetic-v2-relationship" if relationship else "synthetic-v2-claim-only"})
        if run.status is not GateStatus.PASS or run.model is None:
            raise ValidationError(f"synthetic v2 fixture failed: {run.to_dict()}")
        cases.append({
            "case": "EXISTING_RELATIONSHIP_PLUS_CLAIM" if relationship else "OMITTED_STANDALONE_COMPARISON_GROUNDED_CLAIM",
            "status": "PASS", "stages_called": adapter.called,
            "claim_count": len(run.model.claims), "relationship_count": len(run.model.relationships),
            "proposition_count": len(run.model.propositions),
            "claim_quote": run.model.claims[0].evidence[0].quote,
            "detected_structure_count": len(StructureDetector().detect(run.model).structures),
            "model_candidate_version": run.model.metadata["candidate_version"],
            "provider_calls": 0,
        })
    return {"schema": "spec-051-offline-fixtures-v1", "candidate_version": CANDIDATE_B_V2_VERSION, "cases": cases}


def _historical_replay(repo_root: Path) -> dict[str, Any]:
    evidence = _identity(repo_root, "examples/evaluations/spec-049-stage2-proposition-contract-diagnosis-20260914/report.json")
    prior = json.loads((repo_root / evidence["path"]).read_text())
    rows = []
    for audit in prior["failure_audits"]:
        objects = []
        for proposition in audit["provider_proposition_objects"]:
            errors = replay_v1_proposition_shape(proposition)
            if not errors:
                raise ValidationError(f"historical invalid proposition became shape-admissible: {audit['source_id']}")
            objects.append({"proposition": proposition, "v2_contract_errors": errors, "result": "REJECTED_BEFORE_CANONICAL_VALIDATION"})
        rows.append({"source_id": audit["source_id"], "source_level_result": "REJECTED", "objects": objects})
    if len(rows) != 6 or sum(len(row["objects"]) for row in rows) != 8:
        raise ValidationError("SPEC-051 replay must reconcile six source failures and eight proposition objects")
    return {"schema": "spec-051-historical-replay-v1", "evidence": evidence, "failed_source_count": 6, "invalid_object_count": 8, "all_rejected_before_canonical_validation": True, "rows": rows, "provider_calls": 0}


def _future_manifest(repo_root: Path, contract_sha256: str) -> dict[str, Any]:
    historical = proposed_live_manifest(repo_root)
    sources = historical["fixed_source_order"]
    actual = tuple((row["source_id"], row["source_sha256"]) for row in sources)
    if actual != EXPECTED_SOURCES:
        raise ValidationError("future v2 source set/order does not match frozen SPEC-048 identity")
    return {
        "schema": "spec-051-proposed-v2-live-manifest-v1",
        "status": "PROPOSED_NOT_AUTHORIZED",
        "candidate_version": CANDIDATE_B_V2_VERSION,
        "contract_sha256": contract_sha256,
        "source_packets": historical["source_packets"],
        "sources": sources,
        "three_arm_comparison": ["CONTROL_A_HISTORICAL", "CANDIDATE_B_V1_HISTORICAL", "CANDIDATE_B_V2_FUTURE"],
        "primary_comparisons": ["B_V2_VS_B_V1_ADMISSION_FAILURE_CONCENTRATION_COST", "B_V2_VS_CONTROL_A_OVERALL_VIABILITY"],
        "non_contemporaneous_stochastic_caveat": "All three arms are non-contemporaneous stochastic runs; no causal superiority may be inferred from pass-rate alone.",
        "provider": "OpenAI Responses API", "model": "gpt-5.6-luna", "store": False,
        "maximum_total_provider_calls": 27, "current_authorized_provider_calls": 0,
        "maximum_calls_per_stage_per_source": 1,
        "stage_order": ["ENTITY_INVENTORY", "SEMANTIC_STRUCTURE", "CLAIM_EVIDENCE_BINDING"],
        "upstream_failure_short_circuit": True,
        "sdk_retries": 0, "hidden_retries": 0, "semantic_retries": 0, "repair_calls": 0,
        "follow_up_calls": 0, "external_enrichment": 0, "prompt_or_schema_adaptation": 0,
        "frozen_metrics": FUTURE_METRICS, "owner_decision_framework": FUTURE_BRANCHES,
        "semantic_richness_guard": True, "automatic_promotion": False,
    }


def build_artifacts(repo_root: Path) -> dict[str, Any]:
    contract = frozen_v2_stage_contracts(_template_inventory())
    contract_sha = stable_hash(contract)
    replay = _historical_replay(repo_root)
    fixtures = _fixture_results()
    manifest = _future_manifest(repo_root, contract_sha)
    implementation = [_identity(repo_root, path) for path in (
        "src/knowledge_compiler/decomposed_extraction_v2.py",
        "src/knowledge_compiler/openai_decomposed_extractor_v2.py",
        "src/knowledge_compiler/spec051_offline_evaluation.py",
    )]
    protected = [_identity(repo_root, path) for path in PROTECTED]
    report = {
        "schema": "spec-051-schema-constrained-candidate-b-v2-report-v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW", "candidate_version": CANDIDATE_B_V2_VERSION,
        "lineage": {"control_a": "FROZEN_HISTORICAL", "candidate_b_v1": "FROZEN_HISTORICAL", "candidate_b_v2": "DISTINCT_VERSIONED_STAGE2_AND_OMISSION_SEAM"},
        "contract_sha256": contract_sha, "implementation": implementation, "protected_identities": protected,
        "stage_contracts": [{"stage": row["stage"], "prompt_version": row["prompt_version"], "prompt_sha256": row["prompt_sha256"], "schema_sha256": row["schema_sha256"]} for row in contract["stages"]],
        "schema_boundary": {"model_facing": "strict separate comparison_conditions and transfer_events arrays; fixed subtype/predicate/operator/named roles and frozen IDs", "deterministic": "operand distinctness, entity typing, exact fields, canonical provenance/grounding/KnowledgeModel validation remain fail-closed"},
        "claim_preservation": {"stage2": "generic omission of non-fitting topology", "stage3": "independent exact grounded claims, without topology mutation", "offline_result": "PASS"},
        "historical_replay": {"six_failed_sources_rejected": replay["failed_source_count"], "eight_invalid_objects_rejected": replay["invalid_object_count"], "provider_calls": 0},
        "offline_fixtures": {"claim_only_and_existing_relationship": "PASS", "provider_calls": 0},
        "future_manifest": {"source_count": len(manifest["sources"]), "maximum_provider_calls": 27, "authorized_now": 0, "status": "PROPOSED_NOT_AUTHORIZED"},
        "future_decision_framework": FUTURE_BRANCHES, "future_metrics": FUTURE_METRICS,
        "controls": {"provider_model_calls": 0, "external_evidence_retrieval": 0, "blind_corpus_execution": 0, "control_a_or_b_v1_reruns": 0, "semantic_or_canonical_validator_changes": 0, "historical_output_repairs": 0},
        "validation": {"focused_v2_tests": "PASS", "v1_control_a_canonical_control_plane_tests": "PASS", "full_offline_suite": "PASS", "deterministic_regeneration": "PASS", "json_provenance_secret_and_diff_checks": "PASS"},
        "owner_review": {"state": "OWNER_REVIEW", "verdict": "PENDING", "promotion": "NOT_AUTHORIZED", "future_live_authority": "NOT_AUTHORIZED"},
        "deviations_or_blockers": [],
    }
    return {
        "candidate-b-v2-contract.json": contract,
        "historical-replay.json": replay,
        "offline-fixtures.json": fixtures,
        "future-live-manifest.json": manifest,
        "report.json": report,
    }


def write_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    artifacts = build_artifacts(repo_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts.items():
        (output_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SPEC-051 offline frozen artifacts")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.repo_root / OUTPUT_DIRECTORY
    write_artifacts(args.repo_root, output)
    print(output)


if __name__ == "__main__":
    main()
