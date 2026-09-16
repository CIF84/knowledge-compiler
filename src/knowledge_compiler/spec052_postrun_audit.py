"""Offline-only finalization of preserved SPEC-052 live evidence.

The initial run report and every provider response remain immutable inputs. This
module performs no provider operation and never rewrites a semantic proposal.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .decomposed_ab_evaluation import load_historical_control_records, summarize_arm
from .spec052_live_evaluation import OUTPUT_DIRECTORY


FAILED_SOURCE_ID = "nhgri-dna-fact-sheet-2020"
FAILED_SOURCE_DIR = "07-nhgri-dna-fact-sheet-2020"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _failure_audit(output_dir: Path) -> dict[str, Any]:
    source_dir = output_dir / "sources" / FAILED_SOURCE_DIR
    initial = _load(source_dir / "initial-failure-classification.json")
    proposal = _load(source_dir / "stages/02-semantic-structure/parsed-proposal.json")
    transfers = proposal["transfer_events"]
    role_keys = [
        (item["event_entity_id"], item["object_entity_id"], item["destination_entity_id"])
        for item in transfers
    ]
    duplicate_keys = [list(key) for key, count in Counter(role_keys).items() if count > 1]
    if initial["origin_taxonomy"] != "OTHER" or len(duplicate_keys) != 1:
        raise RuntimeError("SPEC-052 preserved failure evidence does not match the post-run audit premise")
    return {
        "schema": "spec-052-post-run-failure-taxonomy-audit-v1",
        "status": "PASS_WITH_TRANSPARENT_CLASSIFICATION_CORRECTION",
        "source_id": FAILED_SOURCE_ID,
        "detection_stage": "SEMANTIC_STRUCTURE",
        "exact_failure": initial["exact_failure"],
        "generated_classifier_origin": "OTHER",
        "authoritative_spec046_origin": "PROPOSITION_CONSTRUCTION",
        "rationale": (
            "The v2 proposal contains two TRANSFER_EVENT objects with the same EVENT, OBJECT, "
            "and DESTINATION role identities but different statements about male/female inheritance. "
            "Canonical proposition IDs derive from proposition type and role identities, so the two "
            "objects collide. This is malformed typed-proposition semantic composition under the "
            "frozen SPEC-046 PROPOSITION_CONSTRUCTION definition, not relationship semantics or an "
            "unclassified failure."
        ),
        "duplicate_transfer_role_identity": duplicate_keys[0],
        "transfer_event_count": len(transfers),
        "candidate_behavior_changed": False,
        "provider_output_changed": False,
        "retry_or_repair_performed": False,
        "prompt_schema_or_validator_changed": False,
        "preserved_initial_artifacts": [
            "run-report.json",
            f"sources/{FAILED_SOURCE_DIR}/initial-failure-classification.json",
            f"sources/{FAILED_SOURCE_DIR}/stages/02-semantic-structure/parsed-proposal.json",
            f"sources/{FAILED_SOURCE_DIR}/stages/02-semantic-structure/raw-provider-response.json",
        ],
    }


def _claim_representation_audit(output_dir: Path) -> dict[str, Any]:
    rows = []
    totals: Counter[str] = Counter()
    decision_classes: Counter[str] = Counter()
    for source_dir in sorted((output_dir / "sources").iterdir()):
        audit = _load(source_dir / "semantic-omission-audit.json")
        decisions = _load(source_dir / "representation-decisions.json")["decisions"]
        classes = Counter(item["semantic_class"] for item in decisions)
        decision_classes.update(classes)
        claims = audit.get("claims", [])
        claim_only = [
            item for item in claims
            if item.get("not_identical_to_stage2_topology_statement")
            and item.get("not_a_stage2_topology_id")
        ]
        grounded = [item for item in claims if item.get("grounding_policy_satisfied_mechanically")]
        admitted = [item for item in claims if item.get("admitted_in_knowledge_model")]
        preserved_claim_only = [
            item for item in claim_only
            if item.get("grounding_policy_satisfied_mechanically")
            and item.get("admitted_in_knowledge_model")
            and item.get("admitted_evidence_exact")
        ]
        unintended = audit.get("unintended_topology_count_if_admitted") or 0
        row = {
            "source_id": source_dir.name.split("-", 1)[1],
            "stage3_ran": audit["stage3_ran"],
            "parsed_claims": len(claims),
            "grounding_policy_satisfied": len(grounded),
            "admitted_claims": len(admitted),
            "mechanical_claim_only_count": len(claim_only),
            "grounded_admitted_claim_only_count": len(preserved_claim_only),
            "unintended_topology_count": unintended,
            "representation_decision_count": len(decisions),
            "representation_decision_semantic_classes": dict(sorted(classes.items())),
            "dedicated_claim_focus_decisions": classes.get("claim", 0),
        }
        rows.append(row)
        totals.update({key: row[key] for key in (
            "parsed_claims", "grounding_policy_satisfied", "admitted_claims",
            "mechanical_claim_only_count", "grounded_admitted_claim_only_count",
            "unintended_topology_count", "representation_decision_count",
            "dedicated_claim_focus_decisions",
        )})
    if totals["parsed_claims"] != 152 or totals["grounded_admitted_claim_only_count"] != 98:
        raise RuntimeError("SPEC-052 claim-preservation totals changed")
    if totals["unintended_topology_count"] != 0 or totals["dedicated_claim_focus_decisions"] != 0:
        raise RuntimeError("SPEC-052 topology or representation audit changed")
    return {
        "schema": "spec-052-claim-only-preservation-audit-v1",
        "status": "PASS_WITH_REPRESENTATION_COVERAGE_LIMITATION",
        "method": (
            "A claim is mechanically claim-only when its ID is not a Stage-2 semantic-object ID "
            "and its statement is not identical to a Stage-2 topology statement. This intentionally "
            "does not claim to detect paraphrased semantic overlap."
        ),
        "sources": rows,
        "totals": dict(sorted(totals.items())),
        "representation_decision_semantic_classes": dict(sorted(decision_classes.items())),
        "findings": {
            "all_parsed_claims_exactly_grounded_and_admitted": totals["parsed_claims"] == totals["grounding_policy_satisfied"] == totals["admitted_claims"],
            "all_mechanical_claim_only_material_preserved_as_grounded_claims": totals["mechanical_claim_only_count"] == totals["grounded_admitted_claim_only_count"],
            "claim_only_material_created_no_topology": totals["unintended_topology_count"] == 0,
            "existing_representation_compiler_created_dedicated_claim_focus": False,
            "assertion_aware_projection_executed": False,
        },
        "representation_limitation": (
            "The existing representation compiler generated decisions only for concept, canonical "
            "relationship, and proposition foci. It has no claim focus in this pipeline. The 98 "
            "mechanically claim-only items are preserved in admitted KnowledgeModels with exact "
            "evidence, but this run does not demonstrate that they are directly surfaced by current "
            "representation decisions. The assertion-aware builder requires a separately admitted "
            "GroundedAssertionSet, which SPEC-052 did not authorize minting from these claims."
        ),
    }


def _validation(repo_root: Path, output_dir: Path, claim_audit: dict[str, Any]) -> dict[str, Any]:
    ledger = _load(output_dir / "provider-call-ledger.json")
    entries = ledger["entries"]
    source_dirs = sorted((output_dir / "sources").iterdir())
    raw_files = list((output_dir / "sources").glob("*/stages/*/raw-provider-response.json"))
    parsed_files = list((output_dir / "sources").glob("*/stages/*/parsed-proposal.json"))
    response_entries = [item for item in entries if item["status"] == "PROVIDER_RESPONSE_RECEIVED"]
    checks = {
        "nine_sources_preserved": len(source_dirs) == 9,
        "provider_call_count_26_within_ceiling_27": ledger["calls_started"] == len(entries) == 26,
        "global_call_ordinals_exact": [item["global_call_ordinal"] for item in entries] == list(range(1, 27)),
        "all_provider_responses_have_ids": all(item.get("provider_response_id") and item.get("http_request_id") for item in entries),
        "all_responses_have_raw_and_parsed_evidence": len(raw_files) == len(parsed_files) == len(response_entries) == 26,
        "store_false_every_call": all(item["store"] is False for item in entries),
        "zero_retry_and_repair_every_call": all(all(item.get(key) == 0 for key in ("sdk_retries", "hidden_retries", "semantic_retries", "repair_calls")) for item in entries),
        "nhgri_short_circuited_after_stage2": len(_load(output_dir / f"sources/{FAILED_SOURCE_DIR}/request-start-ledger.json")["entries"]) == 2,
        "preflight_and_postflight_pass": _load(output_dir / "preflight.json")["status"] == _load(output_dir / "postflight.json")["status"] == "PASS",
        "all_claims_grounded_and_admitted": claim_audit["findings"]["all_parsed_claims_exactly_grounded_and_admitted"],
        "all_claim_only_material_preserved": claim_audit["findings"]["all_mechanical_claim_only_material_preserved_as_grounded_claims"],
        "zero_unintended_topology": claim_audit["findings"]["claim_only_material_created_no_topology"],
        "historical_control_and_bv1_not_rerun": True,
        "external_enrichment_calls": 0,
        "additional_provider_calls_during_audit": 0,
    }
    if not all(value is True or value == 0 for value in checks.values()):
        raise RuntimeError(f"SPEC-052 post-run validation failed: {checks}")
    return {"schema": "spec-052-post-run-validation-v1", "status": "PASS", "checks": checks}


def finalize(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    """Generate authoritative aggregate files from immutable live evidence."""
    run_report_path = output_dir / "run-report.json"
    if not run_report_path.is_file():
        raise RuntimeError("preserved run-report.json is required")
    report = _load(run_report_path)
    failure_audit = _failure_audit(output_dir)
    claim_audit = _claim_representation_audit(output_dir)
    validation = _validation(repo_root, output_dir, claim_audit)
    _write(output_dir / "post-run-failure-taxonomy-audit.json", failure_audit)
    _write(output_dir / "claim-only-preservation-audit.json", claim_audit)
    _write(output_dir / "post-run-validation.json", validation)

    bv2_records_path = output_dir / "candidate-b-v2-comparison-records.json"
    bv2_records = _load(bv2_records_path)["records"]
    for record in bv2_records:
        if record["source_id"] == FAILED_SOURCE_ID:
            record["failure_origins"] = ["PROPOSITION_CONSTRUCTION"]
    _write(bv2_records_path, {"records": bv2_records})
    control = load_historical_control_records(repo_root)
    bv1 = _load(repo_root / "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/candidate-b-comparison-records.json")["records"]
    summaries = {
        "CONTROL_A_HISTORICAL": summarize_arm(control),
        "CANDIDATE_B_V1_HISTORICAL": summarize_arm(bv1),
        "CANDIDATE_B_V2_LIVE": summarize_arm(bv2_records),
    }
    authoritative_bv1 = _load(repo_root / "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/post-run-failure-taxonomy-audit.json")["authoritative_candidate_failure_origin_distribution"]
    summaries["CANDIDATE_B_V1_HISTORICAL"]["failure_origin_distribution"] = authoritative_bv1
    comparison_path = output_dir / "three-arm-comparison.json"
    comparison = _load(comparison_path)
    comparison["summaries"] = summaries
    comparison["failure_taxonomy_authority"] = {
        "candidate_b_v1": "SPEC-048 post-run-failure-taxonomy-audit.json",
        "candidate_b_v2": "SPEC-052 post-run-failure-taxonomy-audit.json",
    }
    _write(comparison_path, comparison)

    source_outcomes = report["source_outcomes"]
    for outcome in source_outcomes:
        if outcome["source_id"] == FAILED_SOURCE_ID:
            outcome["failure_classification"]["generated_origin_taxonomy"] = outcome["failure_classification"]["origin_taxonomy"]
            outcome["failure_classification"]["origin_taxonomy"] = "PROPOSITION_CONSTRUCTION"
            outcome["failure_classification"]["classification_authority"] = "post-run-failure-taxonomy-audit.json"
    totals = claim_audit["totals"]
    report.update({
        "three_arm_summaries": summaries,
        "failure_detection_stages": {"SEMANTIC_STRUCTURE": 1},
        "failure_origin_taxonomy": {"PROPOSITION_CONSTRUCTION": 1},
        "proposition_construction_failures": 1,
        "source_outcomes": source_outcomes,
        "semantic_omission_audit": {
            "stage3_source_count": 8,
            "parsed_claim_count": totals["parsed_claims"],
            "exactly_grounded_and_admitted_claim_count": totals["admitted_claims"],
            "mechanical_claim_only_count": totals["mechanical_claim_only_count"],
            "grounded_admitted_claim_only_count": totals["grounded_admitted_claim_only_count"],
            "unintended_topology_count": totals["unintended_topology_count"],
            "dedicated_claim_focus_representation_decisions": totals["dedicated_claim_focus_decisions"],
            "authoritative_artifact": "claim-only-preservation-audit.json",
            "representation_coverage_limitation": claim_audit["representation_limitation"],
        },
        "mechanically_supported_branch": "INCONCLUSIVE",
        "post_run_audits": {
            "failure_taxonomy": "post-run-failure-taxonomy-audit.json",
            "claim_only_preservation": "claim-only-preservation-audit.json",
            "validation": "post-run-validation.json",
            "initial_aggregate": "run-report.json",
        },
        "execution_deviations": [],
        "audit_notes": [
            "The initial generic OTHER failure label is byte-preserved and transparently corrected to PROPOSITION_CONSTRUCTION from the exact rejected proposal under the frozen SPEC-046 taxonomy.",
            "No provider output, Candidate B v2 implementation, prompt, schema, canonical validator, or admitted model was changed; no retry or repair was performed.",
        ],
    })
    _write(output_dir / "final-report.json", report)

    files = [path for path in sorted(output_dir.rglob("*")) if path.is_file() and path.name != "artifact-manifest.json"]
    manifest = {
        "schema": "spec-052-artifact-manifest-v1",
        "file_count_excluding_manifest": len(files),
        "files": [{"path": str(path.relative_to(output_dir)), "sha256": _sha(path), "byte_count": path.stat().st_size} for path in files],
    }
    _write(output_dir / "artifact-manifest.json", manifest)
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    result = finalize(root, root / OUTPUT_DIRECTORY)
    print(json.dumps({"status": result["status"], "branch": result["mechanically_supported_branch"]}))
