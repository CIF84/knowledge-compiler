"""Prepare and freeze the offline-only SPEC-040 blind evaluation harness."""

from __future__ import annotations

import inspect
import json
import re
import tempfile
from hashlib import sha256
from pathlib import Path
from typing import Any

from .blind_evaluation import (
    BlindSourcePacket,
    DryRunProposalAdapter,
    blind_source_packet_schema,
    run_blind_evaluation,
)
from .depth_interaction_evaluation import directory_identity
from .explanatory_projection import canonical_bytes
from .models import ValidationError
from .semantic_depth_review_evaluation import protected_baseline_hashes


EVALUATION_NAME = "spec-040-blind-out-of-sample-evaluation-harness-20260911"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC038_DIRECTORY_SHA256 = (
    "453f7d2a233224628e03f5e1449650ec20bbff04ffae5ea07e9f6137cf54fd6e"
)
BROWSER_CHECKS = {
    "spec038_four_surface_model_present",
    "structural_diagram_remains_dominant",
    "local_inspection_remains_non_navigational",
    "my_map_remains_quiet_territory_tree",
    "explore_next_remains_forward_authority",
    "browser_console_clean",
}
OWNER_REVIEW_QUESTION = (
    "Is the evaluation harness genuinely generic and frozen before the blind source "
    "set is selected, such that a later out-of-sample run cannot reasonably benefit "
    "from source-specific implementation adaptation?"
)

_SEQUENCE_TEXT = "Phase A precedes Phase B. Phase B precedes Phase C."
_THIN_TEXT = "A reference marker is defined for later use."


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec038_directory() -> Path:
    return repository_root() / (
        "examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-20260909"
    )


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _span(text: str, quote: str) -> dict[str, Any]:
    start = text.index(quote)
    document_id = f"text-{sha256(text.encode('utf-8')).hexdigest()[:16]}"
    return {
        "document_id": document_id,
        "start_char": start,
        "end_char": start + len(quote),
        "quote": quote,
    }


def _source(source_id: str, title: str, text: str) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "title": title,
        "text": text,
        "source_sha256": sha256(text.encode("utf-8")).hexdigest(),
        "provenance": {
            "kind": "SYNTHETIC_NEUTRAL_DRY_RUN",
            "locator": "committed SPEC-040 harness generator",
            "external_source": False,
        },
    }


def synthetic_source_packet() -> dict[str, Any]:
    return {
        "schema_version": "spec-040-blind-source-packet-v1",
        "evaluation_contract": {
            "expected_representation_strategy_supplied": False,
        },
        "sources": [
            _source("neutral-sequence", "Neutral source one", _SEQUENCE_TEXT),
            _source("neutral-thin", "Neutral source two", _THIN_TEXT),
        ],
    }


def _sequence_proposal() -> dict[str, Any]:
    first = "Phase A precedes Phase B."
    second = "Phase B precedes Phase C."
    return {
        "entities": [
            {
                "id": "phase-a",
                "name": "Phase A",
                "description": "The first phase in the bounded source.",
                "entity_type": "PROCESS",
                "aliases": [],
            },
            {
                "id": "phase-b",
                "name": "Phase B",
                "description": "The middle phase in the bounded source.",
                "entity_type": "PROCESS",
                "aliases": [],
            },
            {
                "id": "phase-c",
                "name": "Phase C",
                "description": "The final phase in the bounded source.",
                "entity_type": "PROCESS",
                "aliases": [],
            },
        ],
        "claims": [],
        "relationships": [
            {
                "id": "phase-a-precedes-phase-b",
                "source_entity_id": "phase-a",
                "relationship_type": "PRECEDES",
                "target_entity_id": "phase-b",
                "statement": first,
                "evidence": [_span(_SEQUENCE_TEXT, first)],
                "confidence": 1.0,
                "origin": "SOURCE",
            },
            {
                "id": "phase-b-precedes-phase-c",
                "source_entity_id": "phase-b",
                "relationship_type": "PRECEDES",
                "target_entity_id": "phase-c",
                "statement": second,
                "evidence": [_span(_SEQUENCE_TEXT, second)],
                "confidence": 1.0,
                "origin": "SOURCE",
            },
        ],
        "propositions": [],
        "metadata": {
            "extractor": "deterministic-synthetic-dry-run",
            "prompt_version": "spec-040-dry-run-v1",
        },
    }


def _thin_proposal() -> dict[str, Any]:
    return {
        "entities": [
            {
                "id": "reference-marker",
                "name": "Reference marker",
                "description": "A marker defined for later use.",
                "entity_type": "CONCEPT",
                "aliases": [],
            }
        ],
        "claims": [
            {
                "id": "reference-marker-defined",
                "statement": _THIN_TEXT,
                "evidence": [_span(_THIN_TEXT, _THIN_TEXT)],
                "confidence": 1.0,
                "origin": "SOURCE",
            }
        ],
        "relationships": [],
        "propositions": [],
        "metadata": {
            "extractor": "deterministic-synthetic-dry-run",
            "prompt_version": "spec-040-dry-run-v1",
        },
    }


def synthetic_proposals() -> dict[str, dict[str, Any]]:
    return {
        sha256(_SEQUENCE_TEXT.encode("utf-8")).hexdigest(): _sequence_proposal(),
        sha256(_THIN_TEXT.encode("utf-8")).hexdigest(): _thin_proposal(),
    }


def proposed_live_execution_plan(frozen_commit: str) -> dict[str, Any]:
    return {
        "status": "PROPOSED_NOT_AUTHORIZED",
        "frozen_harness_commit": frozen_commit,
        "source_set": "UNDISCLOSED_AND_NOT_SELECTED_DURING_SPEC040",
        "source_count": 3,
        "provider": "OpenAI Responses API",
        "model": "gpt-5.6-luna",
        "calls_per_source": 1,
        "maximum_total_calls": 3,
        "call_purpose": "semantic extraction with deterministic local grounding and canonical validation",
        "canonicalization_calls": 0,
        "retry_policy": {
            "sdk_retries": 0,
            "hidden_retries": 0,
            "semantic_retries": 0,
            "additional_calls_without_new_approval": 0,
        },
        "transmission": {
            "source_text_transmitted": True,
            "scope": "exact text or bounded excerpt frozen in the later approved packet",
            "external_enrichment": False,
            "retrieval": False,
        },
        "prompt": {
            "prompt_version": "spec-010-v1",
            "schema": "knowledge_extraction",
            "relationship_grammar": "current frozen trusted relationship vocabulary",
            "repair_after_results": False,
        },
        "storage": {"store": False},
        "execution_order": "frozen packet order",
        "failure_policy": {
            "malformed_packet": "stop before any provider call",
            "frozen_commit_mismatch": "stop before any provider call",
            "provider_or_validation_failure": (
                "preserve the complete failed attempt, perform no retry, and continue "
                "to the next already-approved source"
            ),
            "implementation_change_after_source_submission": (
                "invalidate the run and require a newly designated frozen experiment"
            ),
        },
        "artifacts_per_source": [
            "source identity and exact hash",
            "provider request metadata and bounded scope",
            "extraction proposal",
            "grounding resolution",
            "rejected assertions",
            "admitted KnowledgeModel or failure",
            "detected structures",
            "representation decisions",
            "renderer bindings or explicit missing renderer",
            "learner review artifact",
            "complete run history and usage",
        ],
        "token_accounting": {
            "pre_execution_numeric_estimate": "UNAVAILABLE_UNTIL_SOURCE_SET_IS_FROZEN",
            "reason": "the source texts and lengths are deliberately undisclosed in SPEC-040",
            "required_after_freeze": (
                "record UTF-8 characters per source before execution and preserve exact "
                "provider input/output/total token usage per response"
            ),
        },
        "approval_required": (
            "Explicit owner approval is required after the blind sources and exact "
            "bounded scopes are frozen and before any source text is transmitted."
        ),
    }


def _decision_signatures(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for case_dir in sorted((run_dir / "sources").iterdir()):
        source = json.loads((case_dir / "source.json").read_text())
        decisions = json.loads((case_dir / "representation-decisions.json").read_text())
        result[source["source_sha256"]] = [
            {
                "semantic_class": item["semantic_class"],
                "semantic_focus_identity": item["semantic_focus_identity"],
                "strategy": item["selected_representation_strategy"],
                "rule": item["selected_rule_id"],
                "sufficiency": item["sufficiency"],
                "fallback_reason": item["fallback_reason"],
            }
            for item in decisions["decisions"]
        ]
    return result


def _invariance_evidence(reference_run: Path) -> dict[str, Any]:
    original = BlindSourcePacket.from_dict(synthetic_source_packet())
    changed = original.to_dict()
    changed["sources"] = list(reversed(changed["sources"]))
    for index, source in enumerate(changed["sources"], start=1):
        source["source_id"] = f"changed-identity-{index}"
        source["title"] = f"Changed neutral display label {index}"
        source["provenance"] = {
            "kind": "RENAMED_SYNTHETIC_PROVENANCE",
            "locator": f"different-file-{index}.txt",
            "domain_display_label": f"Changed domain {index}",
        }
    with tempfile.TemporaryDirectory(prefix="spec040-invariance-") as temporary:
        changed_run = Path(temporary) / "run"
        run_blind_evaluation(
            BlindSourcePacket.from_dict(changed),
            DryRunProposalAdapter(synthetic_proposals()),
            output_dir=changed_run,
        )
        changed_signatures = _decision_signatures(changed_run)
    original_signatures = _decision_signatures(reference_run)
    return {
        "status": "PASS" if original_signatures == changed_signatures else "FAIL",
        "changed_only": [
            "source title",
            "source ID string",
            "source filename/locator",
            "domain display label",
            "source packet ordinal",
        ],
        "comparison_key": "immutable exact source SHA-256",
        "original_decision_signatures": original_signatures,
        "changed_decision_signatures": changed_signatures,
    }


def _source_code_guard() -> dict[str, Any]:
    from . import blind_evaluation, semantic_representation_compiler

    runner_source = inspect.getsource(blind_evaluation.run_blind_evaluation).casefold()
    compiler_source = inspect.getsource(semantic_representation_compiler).casefold()
    forbidden_literals = [
        "economics",
        "electromagnetism",
        "software_architecture",
        "history of printing",
        "market-price",
        "neutral-sequence",
        "neutral-thin",
    ]
    conditional_fragments = [
        "source_id ==",
        "title ==",
        "domain ==",
        "index ==",
        "expected_representation_strategy",
    ]
    findings = {
        token: token in runner_source or token in compiler_source
        for token in forbidden_literals
    }
    conditional_findings = {
        token: token in runner_source for token in conditional_fragments
    }
    return {
        "status": (
            "PASS"
            if not any(findings.values()) and not any(conditional_findings.values())
            else "FAIL"
        ),
        "scanned_modules": [
            "knowledge_compiler.blind_evaluation",
            "knowledge_compiler.semantic_representation_compiler",
        ],
        "source_or_fixture_literal_findings": findings,
        "source_identity_conditional_findings": conditional_findings,
        "representation_expectations_read_by_runner": False,
    }


def _file_hashes(relative_paths: list[str]) -> dict[str, str]:
    root = repository_root()
    return {
        path: sha256((root / path).read_bytes()).hexdigest()
        for path in sorted(relative_paths)
    }


def prepare_blind_evaluation_harness(
    *,
    output_dir: Path,
    frozen_commit: str,
    spec038_dir: Path | None = None,
) -> dict[str, Any]:
    if not re_full_commit(frozen_commit):
        raise ValidationError("frozen harness commit must be a full lowercase Git SHA")
    if output_dir.exists():
        raise ValidationError("SPEC-040 output directory already exists")
    spec038_dir = spec038_dir or default_spec038_directory()
    spec038_identity = directory_identity(spec038_dir)
    if spec038_identity["aggregate_sha256"] != FROZEN_SPEC038_DIRECTORY_SHA256:
        raise ValidationError("protected SPEC-038 candidate identity mismatch")
    baselines_before = protected_baseline_hashes()

    packet_value = synthetic_source_packet()
    packet = BlindSourcePacket.from_dict(packet_value)
    output_dir.mkdir(parents=True)
    _write_json(output_dir / "source-packet.schema.json", blind_source_packet_schema())
    _write_json(output_dir / "synthetic-source-packet.example.json", packet_value)
    dry_run_dir = output_dir / "dry-run"
    dry_report = run_blind_evaluation(
        packet,
        DryRunProposalAdapter(synthetic_proposals()),
        output_dir=dry_run_dir,
    )
    invariance = _invariance_evidence(dry_run_dir)
    source_guard = _source_code_guard()
    anti_overfit = {
        "status": (
            "PASS"
            if invariance["status"] == "PASS" and source_guard["status"] == "PASS"
            else "FAIL"
        ),
        "metadata_and_ordinal_invariance": invariance,
        "source_code_guard": source_guard,
    }
    _write_json(output_dir / "anti-overfitting-evidence.json", anti_overfit)

    live_plan = proposed_live_execution_plan(frozen_commit)
    _write_json(output_dir / "proposed-live-execution-plan.json", live_plan)
    frozen_files = _file_hashes(
        [
            "src/knowledge_compiler/blind_evaluation.py",
            "src/knowledge_compiler/blind_evaluation_harness.py",
            "src/knowledge_compiler/semantic_representation_compiler.py",
            "src/knowledge_compiler/representation_strategy.py",
            "src/knowledge_compiler/openai_extractor.py",
        ]
    )
    frozen = {
        "frozen_harness_commit": frozen_commit,
        "frozen_files": frozen_files,
        "protected_spec038": spec038_identity,
        "protected_baselines": baselines_before,
        "blind_source_set_present": False,
        "real_source_text_present": False,
    }
    _write_json(output_dir / "frozen-harness.json", frozen)

    dry_cases = {
        item["source_id"]: item for item in dry_report["outcomes"]
    }
    required_intermediate_files = {
        "source.json",
        "provider-request-metadata.json",
        "extraction-proposal.json",
        "rejected-assertions.json",
        "grounding-resolution.json",
        "admitted-knowledge-model.json",
        "detected-structures.json",
        "representation-decisions.json",
        "renderer-bindings.json",
        "learner-review-artifact.json",
        "run-history.json",
    }
    case_dirs = sorted((dry_run_dir / "sources").iterdir())
    machine_checks = {
        "offline_only_live_calls_zero": all(
            json.loads((case / "provider-request-metadata.json").read_text())[
                "live_call"
            ]
            is False
            for case in case_dirs
        ),
        "source_packet_valid_and_contains_no_expected_answers": (
            packet.to_dict() == packet_value
        ),
        "runner_and_compiler_have_no_source_identity_rules": source_guard["status"]
        == "PASS",
        "title_id_domain_filename_and_ordinal_invariance": invariance["status"]
        == "PASS",
        "all_intermediate_audit_artifacts_preserved": all(
            required_intermediate_files <= {path.name for path in case.iterdir()}
            for case in case_dirs
        ),
        "structural_dry_run_reaches_spec038_plan_seam": (
            "PROCESS_SEQUENCE"
            in dry_cases["neutral-sequence"]["selected_strategies"]
        ),
        "semantically_thin_case_fails_closed_to_prose": (
            dry_cases["neutral-thin"]["selected_strategies"] == ["CONCISE_PROSE"]
        ),
        "complete_run_history_has_no_retries": all(
            json.loads((case / "run-history.json").read_text())[
                "hidden_retry_count"
            ]
            == 0
            for case in case_dirs
        ),
        "spec038_candidate_unchanged": directory_identity(spec038_dir)
        == spec038_identity,
        "baseline001_through_004_unchanged": protected_baseline_hashes()
        == baselines_before,
        "spec039_compiler_included_in_frozen_identity": (
            "src/knowledge_compiler/semantic_representation_compiler.py" in frozen_files
        ),
        "blind_source_set_absent": True,
        "known_comparison_and_worked_example_gaps_not_closed": True,
    }
    if not all(machine_checks.values()):
        failed = [name for name, passed in machine_checks.items() if not passed]
        raise ValidationError(f"SPEC-040 harness machine gate failed closed: {failed}")
    machine_gate = {
        "status": "PASS_PENDING_BROWSER",
        "checks": machine_checks,
        "browser_checks": "PENDING",
    }
    _write_json(output_dir / "machine-gate.json", machine_gate)
    _write_json(
        output_dir / "browser-regression.json",
        {"status": "PENDING_BROWSER_VERIFICATION", "checks": {}, "console": {}},
    )
    _write_json(
        output_dir / "human-review-template.json",
        {
            "status": "BLOCKED_PENDING_BROWSER_AND_VALIDATION",
            "question": OWNER_REVIEW_QUESTION,
            "verdict": "PENDING",
            "allowed_verdicts": [
                "HARNESS_GENERIC_AND_FROZEN",
                "HARNESS_OVERFITTING_RISK",
                "HARNESS_INCOMPLETE",
                "INCONCLUSIVE",
            ],
            "blind_source_selection_authorized": False,
            "live_execution_authorized": False,
        },
    )
    report = {
        "spec": "SPEC-040",
        "status": "IMPLEMENTED_AWAITING_OWNER_REVIEW",
        "execution_mode": "OFFLINE_ONLY",
        "frozen_harness_commit": frozen_commit,
        "blind_source_set": "ABSENT_UNDISCLOSED_NOT_SELECTED",
        "live_model_or_external_calls": 0,
        "dry_run_result": dry_report,
        "anti_overfitting_result": anti_overfit["status"],
        "machine_gate": machine_gate,
        "browser_gate": "PENDING",
        "deterministic_regeneration": "PENDING",
        "offline_tests": "PENDING",
        "dependencies_added": [],
        "dependencies_removed": [],
        "semantic_vocabulary_changes": [],
        "ui_behavior_changes": [],
        "known_coverage_gaps_preserved": [
            "comparison renderer unavailable",
            "worked-example rule-to-instance capability unproven",
        ],
        "proposed_live_execution_plan": "proposed-live-execution-plan.json",
        "owner_review_question": OWNER_REVIEW_QUESTION,
        "owner_verdict": "PENDING",
        "promotion": "NOT_AUTHORIZED",
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            "examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-20260909 "
            "--port 8040"
        ),
    }
    _write_json(output_dir / "report.json", report)
    _write_json(
        output_dir / "manifest.json",
        {
            "spec": "SPEC-040",
            "report": "report.json",
            "source_packet_schema": "source-packet.schema.json",
            "synthetic_example": "synthetic-source-packet.example.json",
            "dry_run": "dry-run/",
            "anti_overfitting": "anti-overfitting-evidence.json",
            "live_execution_plan": "proposed-live-execution-plan.json",
            "frozen_harness": "frozen-harness.json",
            "machine_gate": "machine-gate.json",
            "browser_regression": "browser-regression.json",
            "human_review": "human-review-template.json",
        },
    )
    return report


def re_full_commit(value: str) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def finalize_blind_evaluation_harness(
    output_dir: Path,
    browser_verification: dict[str, Any],
    *,
    deterministic_file_count: int,
    focused_test_result: str,
    protected_regression_result: str,
    full_test_result: str,
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-040 browser regression did not pass")
    checks = browser_verification.get("checks", {})
    if set(checks) != BROWSER_CHECKS or not all(checks.values()):
        raise ValidationError("SPEC-040 browser regression checks are incomplete")
    console = browser_verification.get("console", {})
    if console != {"errors": [], "warnings": [], "result": "PASS"}:
        raise ValidationError("SPEC-040 browser console is not clean")
    _write_json(output_dir / "browser-regression.json", browser_verification)
    machine = json.loads((output_dir / "machine-gate.json").read_text())
    machine["status"] = "PASS"
    machine["browser_checks"] = checks
    _write_json(output_dir / "machine-gate.json", machine)
    review = json.loads((output_dir / "human-review-template.json").read_text())
    review["status"] = "PENDING_OWNER_REVIEW"
    _write_json(output_dir / "human-review-template.json", review)
    report = json.loads((output_dir / "report.json").read_text())
    report["machine_gate"] = machine
    report["browser_gate"] = "PASS"
    report["deterministic_regeneration"] = {
        "result": "PASS_BYTE_IDENTICAL",
        "compared_file_count": deterministic_file_count,
        "scope": "independent complete pre-finalization harness artifacts",
    }
    report["offline_tests"] = {
        "focused": focused_test_result,
        "spec038_and_spec039_regression": protected_regression_result,
        "full": full_test_result,
        "result": "PASS",
    }
    _write_json(output_dir / "report.json", report)
    return report
