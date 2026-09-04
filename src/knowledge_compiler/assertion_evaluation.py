"""SPEC-013 frozen-source assertion-first evaluation harness."""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Mapping

from .assertion_compilation import (
    ASSERTION_COMPILER_VERSION,
    AssertionCanonicalizer,
    AssertionExtractionProposal,
    AssertionExtractor,
    CanonicalizationProposal,
    GroundedAssertionSet,
    compile_assertion_semantics,
    ground_assertions,
)
from .layout import with_layouts
from .models import KnowledgeModel, Origin, ValidationError
from .normalize import normalize_document, normalize_text
from .openai_assertion_compiler import (
    ASSERTION_PROMPT_VERSION,
    CANONICALIZATION_PROMPT_VERSION,
    OpenAIAssertionCompiler,
)
from .openai_extractor import DEFAULT_MODEL
from .quantum_learning_evaluation import _representation_diagnostics, _structure_counts
from .representation_builder import RepresentationBuilder
from .semantic_navigation import copy_semantic_navigation_assets
from .staged_compilation import SymbolTable
from .structure_detection import StructureDetector


EVALUATION_VERSION = "spec-013-v1"
ASSERTION_REVIEW_CATEGORIES = ("FAITHFUL", "PARTIAL", "DISTORTED", "UNSUPPORTED")
CANONICAL_REVIEW_CATEGORIES = (
    "SUPPORTED", "IMPRECISE_ENDPOINT", "WRONG_PREDICATE", "REVERSED_DIRECTION",
    "OVERSTATED_CAUSALITY", "UNSUPPORTED", "LOSSY_BINARY_FORM", "OTHER",
)
ALLOWED_VERDICTS = (
    "ASSERTION_FIRST_BETTER", "NO_MEANINGFUL_IMPROVEMENT",
    "ASSERTION_FIRST_WORSE", "MIXED", "INCONCLUSIVE",
)
SPEC_012_CONTROL_PRECISION = 0.375


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _usage(metadata: Mapping[str, Any]) -> dict[str, int]:
    raw = metadata.get("usage", {})
    return {key: int(raw.get(key, 0)) for key in ("input_tokens", "output_tokens", "total_tokens")}


def _attempt(
    sequence: int, stage: str, started_at: str, elapsed: float, outcome: str,
    metadata: Mapping[str, Any], provider_call_attempted: bool,
    error: Exception | None = None, rejected_output_preserved: bool = False,
) -> dict[str, Any]:
    value = {
        "sequence": sequence,
        "stage": stage,
        "started_at": started_at,
        "completed_at": _utc_now(),
        "runtime_seconds": round(elapsed, 3),
        "outcome": outcome,
        "provider_call_attempted": provider_call_attempted,
        "provider": metadata.get("provider", "fixture"),
        "requested_model": metadata.get("requested_model"),
        "actual_model": metadata.get("model"),
        "provider_request_id": metadata.get("provider_request_id"),
        "prompt_version": metadata.get("prompt_version"),
        "retries": 0,
        "usage": _usage(metadata),
        "cost": "NOT_AVAILABLE",
        "rejected_output_preserved": rejected_output_preserved,
    }
    if error is not None:
        value.update({"error_type": type(error).__name__, "error": str(error)})
    return value


def _write_history(output_dir: Path, attempts: list[dict[str, Any]]) -> None:
    _write_json(output_dir / "run-history.json", {
        "spec": "SPEC-013",
        "attempts": attempts,
        "symbol_discovery_call_count": 0,
        "primary_live_call_budget": 2,
        "current_run_live_call_count": sum(bool(item["provider_call_attempted"]) for item in attempts),
        "semantic_retry_count": 0,
        "automatic_retry_count": 0,
        "hidden_retries_or_favorable_run_selection": False,
        "prompt_iteration_after_live_output": False,
        "external_semantic_enrichment": False,
        "child_resolution_call": False,
    })


def _write_failure(
    output_dir: Path, source: Mapping[str, Any], attempts: list[dict[str, Any]],
    stage: str, error: Exception,
) -> None:
    _write_history(output_dir, attempts)
    _write_json(output_dir / "report.json", {
        "spec": "SPEC-013", "evaluation_version": EVALUATION_VERSION,
        "outcome": f"{stage}_FAILED", "verdict": "PENDING_REPOSITORY_REVIEW",
        "failure": str(error), "source": dict(source),
        "live_call_count": sum(bool(item["provider_call_attempted"]) for item in attempts),
        "retry_count": 0, "authoritative_monetary_cost": "NOT_AVAILABLE",
        "downstream": "NOT_RUN_NO_TRUSTED_PARENT",
    })
    (output_dir / "README.md").write_text(
        "# SPEC-013 preserved assertion-first failure\n\n"
        f"The experiment failed during `{stage}`. Available raw proposals, provider metadata, "
        "and exact validation failures are preserved. No rejected semantics were rendered.\n",
        encoding="utf-8",
    )


def _grounding(assertions: GroundedAssertionSet, document_text: str) -> dict[str, Any]:
    spans = [span for item in assertions.assertions for span in item.evidence]
    exact = [span.quote == document_text[span.start_char:span.end_char] for span in spans]
    unique = [document_text.count(span.quote) == 1 for span in spans]
    return {
        "assertion_count": len(assertions.assertions),
        "source_assertion_count": sum(item.origin is Origin.SOURCE for item in assertions.assertions),
        "inferred_assertion_count": sum(item.origin is Origin.INFERRED for item in assertions.assertions),
        "evidence_span_count": len(spans),
        "exact_evidence_span_count": sum(exact),
        "unique_evidence_span_count": sum(unique),
        "exact_evidence_resolution_rate": sum(exact) / len(exact) if exact else None,
        "unique_evidence_resolution_rate": sum(unique) / len(unique) if unique else None,
        "missing_evidence_failures": 0,
        "ambiguous_evidence_failures": 0,
        "unknown_participant_symbol_count": 0,
    }


def _canonical_counts(proposal: CanonicalizationProposal) -> dict[str, Any]:
    total = (
        len(proposal.relationships) + len(proposal.propositions)
        + len(proposal.claims) + len(proposal.uncompiled_assertions)
    )
    uncompiled = len(proposal.uncompiled_assertions)
    return {
        "relationships": len(proposal.relationships),
        "propositions": len(proposal.propositions),
        "claims": len(proposal.claims),
        "uncompiled_assertions": uncompiled,
        "total_assertions_accounted": total,
        "canonicalized_assertions": total - uncompiled,
        "canonicalization_rate": (total - uncompiled) / total if total else None,
        "abstention_rate": uncompiled / total if total else None,
    }


def _assertion_review_template(
    assertions: GroundedAssertionSet, proposal: CanonicalizationProposal
) -> dict[str, Any]:
    disposition = {
        **{item.assertion_id: "BINARY_RELATIONSHIP" for item in proposal.relationships},
        **{item.assertion_id: "STRUCTURED_PROPOSITION" for item in proposal.propositions},
        **{item.assertion_id: "CLAIM" for item in proposal.claims},
        **{item.assertion_id: "UNCOMPILED_ASSERTION" for item in proposal.uncompiled_assertions},
    }
    return {
        "spec": "SPEC-013",
        "status": "PENDING_INDEPENDENT_REPOSITORY_REVIEW",
        "review_categories_fixed_before_live_output": list(ASSERTION_REVIEW_CATEGORIES),
        "review_scope": "ALL_ASSERTIONS",
        "items": [{
            "id": item.id,
            "statement": item.statement,
            "participant_entity_ids": list(item.participant_entity_ids),
            "canonical_disposition": disposition[item.id],
            "classification": "PENDING",
            "notes": "",
            "abstention_quality": (
                "PENDING" if disposition[item.id] == "UNCOMPILED_ASSERTION" else "NOT_ABSTAINED"
            ),
            "obvious_safe_relationship_unnecessarily_abstained": False,
        } for item in assertions.assertions],
    }


def _canonical_review_template(model: KnowledgeModel) -> dict[str, Any]:
    items = [{
        "kind": "relationship",
        "id": item.id,
        "statement": item.statement,
        "source_entity_id": item.source_entity_id,
        "predicate": item.relationship_type.value,
        "target_entity_id": item.target_entity_id,
        "classification": "PENDING",
        "endpoint_precision": "PENDING",
        "predicate_precision": "PENDING",
        "notes": "",
    } for item in model.relationships]
    items.extend({
        "kind": "proposition",
        "id": item.id,
        "statement": item.statement,
        "role_bindings": [
            {"role": binding.role.value, "entity_id": binding.entity_id}
            for binding in item.role_bindings
        ],
        "predicate": item.relationship_type.value,
        "classification": "PENDING",
        "endpoint_precision": "PENDING",
        "predicate_precision": "PENDING",
        "notes": "",
    } for item in model.propositions)
    return {
        "spec": "SPEC-013",
        "status": "PENDING_INDEPENDENT_REPOSITORY_REVIEW",
        "review_categories_fixed_before_live_output": list(CANONICAL_REVIEW_CATEGORIES),
        "review_scope": "ALL_COMPILED_RELATIONSHIPS_AND_PROPOSITIONS",
        "items": items,
        "known_control_defects": [{
            "control_item": item,
            "experiment_status": "PENDING",
            "notes": "",
        } for item in (
            "quantum revolution CAUSES quantum mechanics",
            "superfluidity EXAMPLE_OF quantum mechanics",
            "quantum mechanics ENABLES four listed applications",
            "tunneling ENABLES transistor",
            "Pauli exclusion principle CONSTRAINS electron",
            "QED IS_A quantum field theory",
        )],
        "new_assertion_first_defects": [],
        "verdict": "PENDING",
        "verdict_rationale": {
            "assertion_fidelity": "", "structural_integrity": "",
            "grounding_integrity": "", "canonical_semantic_precision": "",
            "abstention_behavior": "", "cost_complexity": "",
        },
        "semantic_gain_worth_assertion_boundary_on_this_benchmark": "PENDING",
    }


def run_assertion_first_evaluation(
    *, source_path: Path, source_metadata_path: Path, symbol_table_path: Path,
    output_dir: Path, model: str = DEFAULT_MODEL,
    compiler_factory: Callable[[], AssertionExtractor | AssertionCanonicalizer] | None = None,
) -> dict[str, Any]:
    """Run exactly assertion extraction then canonicalization using reused frozen symbols."""
    output_dir.mkdir(parents=True, exist_ok=False)
    normalized_text = normalize_text(source_path.read_text(encoding="utf-8"))
    source_metadata = json.loads(source_metadata_path.read_text(encoding="utf-8"))
    actual_hash = hashlib.sha256(normalized_text.encode()).hexdigest()
    if source_metadata.get("normalized_sha256") != actual_hash:
        raise ValidationError(
            f"source text does not match frozen hash: expected {source_metadata.get('normalized_sha256')}, got {actual_hash}"
        )
    source_report = {
        **source_metadata,
        "word_count": len(normalized_text.split()),
        "character_count": len(normalized_text),
        "source_text_unchanged": True,
        "source_processing_strategy": "FULL_SOURCE_ASSERTION_FIRST",
        "segment_count": 1,
        "external_semantic_enrichment": False,
    }
    _write_json(output_dir / "source-metadata.json", source_report)
    symbol_raw = json.loads(symbol_table_path.read_text(encoding="utf-8"))
    symbol_table = SymbolTable.from_dict(symbol_raw)
    shutil.copyfile(symbol_table_path, output_dir / "symbol-table.json")
    symbol_hash = _sha256_bytes(symbol_table_path)
    if _sha256_bytes(output_dir / "symbol-table.json") != symbol_hash:
        raise ValidationError("copied frozen symbol table does not match SPEC-012 artifact")
    document = normalize_document(normalized_text, metadata=source_report)
    compiler = compiler_factory() if compiler_factory else OpenAIAssertionCompiler(model=model)
    provider_call = compiler_factory is None
    attempts: list[dict[str, Any]] = []

    started_at = _utc_now()
    started = time.perf_counter()
    try:
        extraction = compiler.extract_assertions(document, symbol_table)  # type: ignore[attr-defined]
        grounded = ground_assertions(document, symbol_table, extraction)
    except Exception as exc:
        metadata = dict(getattr(compiler, "last_assertion_metadata", {}))
        raw = getattr(compiler, "last_assertion_raw", None)
        _write_json(output_dir / "assertion-extraction-result.json", {
            "spec": "SPEC-013", "stage": "ASSERTION_EXTRACTION", "outcome": "FAILED",
            "failure": str(exc), "raw_proposal": raw, "provider_metadata": metadata,
            "failure_boundary": (
                "ASSERTION_GROUNDING" if "grounding failed" in str(exc)
                else "ASSERTION_EXTRACTION"
            ),
        })
        attempts.append(_attempt(
            1, "ASSERTION_EXTRACTION_AND_GROUNDING", started_at,
            time.perf_counter() - started, "FAILED", metadata, provider_call,
            exc, raw is not None,
        ))
        _write_failure(output_dir, source_report, attempts, "ASSERTION_STAGE", exc)
        raise
    extraction_runtime = time.perf_counter() - started
    extraction_metadata = dict(extraction.metadata)
    attempts.append(_attempt(
        1, "ASSERTION_EXTRACTION_AND_GROUNDING", started_at, extraction_runtime,
        "SUCCESS", extraction_metadata, provider_call,
    ))
    _write_json(output_dir / "assertion-extraction-result.json", {
        "spec": "SPEC-013", "stage": "ASSERTION_EXTRACTION", "outcome": "SUCCESS",
        "prompt_version": extraction_metadata.get("prompt_version", ASSERTION_PROMPT_VERSION),
        "raw_proposal": getattr(compiler, "last_assertion_raw", None) or extraction.to_dict(),
        "provider_metadata": extraction_metadata,
        "raw_assertion_count": len(extraction.assertions),
    })
    _write_json(output_dir / "grounded-assertions.json", grounded.to_dict())

    started_at = _utc_now()
    started = time.perf_counter()
    try:
        canonical = compiler.canonicalize_assertions(grounded, symbol_table)  # type: ignore[attr-defined]
        result = compile_assertion_semantics(document, symbol_table, grounded, canonical)
    except Exception as exc:
        metadata = dict(getattr(compiler, "last_canonicalization_metadata", {}))
        raw = getattr(compiler, "last_canonicalization_raw", None)
        _write_json(output_dir / "canonicalization-result.json", {
            "spec": "SPEC-013", "stage": "CANONICALIZATION", "outcome": "FAILED",
            "failure": str(exc), "raw_proposal": raw, "provider_metadata": metadata,
            "failure_boundary": "CANONICALIZATION",
        })
        attempts.append(_attempt(
            2, "CANONICALIZATION", started_at, time.perf_counter() - started,
            "FAILED", metadata, provider_call, exc, raw is not None,
        ))
        _write_failure(output_dir, source_report, attempts, "CANONICALIZATION", exc)
        raise
    canonical_runtime = time.perf_counter() - started
    canonical_metadata = dict(canonical.metadata)
    attempts.append(_attempt(
        2, "CANONICALIZATION", started_at, canonical_runtime, "SUCCESS",
        canonical_metadata, provider_call,
    ))
    _write_history(output_dir, attempts)
    _write_json(output_dir / "canonicalization-result.json", {
        "spec": "SPEC-013", "stage": "CANONICALIZATION", "outcome": "SUCCESS",
        "prompt_version": canonical_metadata.get(
            "prompt_version", CANONICALIZATION_PROMPT_VERSION
        ),
        "raw_proposal": getattr(compiler, "last_canonicalization_raw", None) or canonical.to_dict(),
        "normalized_proposal": canonical.to_dict(),
        "provider_metadata": canonical_metadata,
        "counts": _canonical_counts(canonical),
    })
    _write_json(output_dir / "uncompiled-assertions.json", {
        "spec": "SPEC-013",
        "count": len(canonical.uncompiled_assertions),
        "items": [
            {"assertion_id": item.assertion_id, "reason": item.reason}
            for item in canonical.uncompiled_assertions
        ],
    })
    parent = result.model
    structures = StructureDetector().detect(parent)
    representation = with_layouts(RepresentationBuilder().build(
        parent, structures,
        presentation_metadata={
            "domain": "quantum_mechanics",
            "title": "Introduction to quantum mechanics — assertion-first",
        },
    ))
    _write_json(output_dir / "parent.knowledge.json", parent.to_dict())
    _write_json(output_dir / "parent.structures.json", structures.to_dict())
    _write_json(output_dir / "parent.representation.json", representation.to_dict())
    _write_json(output_dir / "assertion-review.json", _assertion_review_template(grounded, canonical))
    _write_json(output_dir / "canonical-semantic-review.json", _canonical_review_template(parent))
    counts = _canonical_counts(canonical)
    grounding = _grounding(grounded, document.text)
    report = {
        "spec": "SPEC-013", "evaluation_version": EVALUATION_VERSION,
        "outcome": "PENDING_INDEPENDENT_SEMANTIC_REVIEW", "verdict": "PENDING",
        "source": source_report,
        "symbol_table": {
            "reused_from_spec_012": True,
            "source_path": str(symbol_table_path),
            "sha256": symbol_hash,
            "symbol_count": len(symbol_table.entities),
            "fresh_symbol_discovery_calls": 0,
        },
        "provider": extraction_metadata.get("provider", "fixture"),
        "requested_model": model,
        "prompt_versions": {
            "assertion_extraction": extraction_metadata.get("prompt_version", ASSERTION_PROMPT_VERSION),
            "canonicalization": canonical_metadata.get("prompt_version", CANONICALIZATION_PROMPT_VERSION),
        },
        "compiler_version": ASSERTION_COMPILER_VERSION,
        "provider_request_ids": {
            "assertion_extraction": extraction_metadata.get("provider_request_id"),
            "canonicalization": canonical_metadata.get("provider_request_id"),
        },
        "assertion_grounding": grounding,
        "canonicalization": counts,
        "structural": {
            "unknown_assertion_participants": 0,
            "dangling_relationship_endpoints": 0,
            "dangling_proposition_roles": 0,
            "silent_entity_minting": False,
            "knowledge_model_round_trip": KnowledgeModel.from_dict(parent.to_dict()) == parent,
        },
        "compiled_grounding": grounding,
        "downstream": {
            "structure_counts": _structure_counts(structures),
            "representation": _representation_diagnostics(parent, representation),
            "semantic_zoom": "NOT_ATTEMPTED_BY_SPEC",
        },
        "usage": {
            "assertion_extraction": _usage(extraction_metadata),
            "canonicalization": _usage(canonical_metadata),
            "combined": {
                key: _usage(extraction_metadata)[key] + _usage(canonical_metadata)[key]
                for key in ("input_tokens", "output_tokens", "total_tokens")
            },
            "spec_012_control": {
                "pass_1": {"input_tokens": 8464, "output_tokens": 1427, "total_tokens": 9891},
                "pass_2": {"input_tokens": 13275, "output_tokens": 2976, "total_tokens": 16251},
                "combined": {"input_tokens": 21739, "output_tokens": 4403, "total_tokens": 26142},
            },
        },
        "runtime_seconds": {
            "assertion_extraction": round(extraction_runtime, 3),
            "canonicalization": round(canonical_runtime, 3),
            "combined": round(extraction_runtime + canonical_runtime, 3),
            "spec_012_control_combined": 36.464,
        },
        "authoritative_monetary_cost": "NOT_AVAILABLE",
        "provider_controls": {
            "store": False, "sdk_automatic_retries": 0, "semantic_retries": 0,
            "hidden_retries": False, "prompt_iteration_after_live_output": False,
            "external_enrichment": False, "child_resolution_call": False,
        },
        "dependencies_added": [], "dependencies_removed": [],
    }
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "control-comparison.json", {
        "spec": "SPEC-013", "status": "PENDING_INDEPENDENT_SEMANTIC_REVIEW",
        "verdict": "PENDING", "spec_012_control_precision": SPEC_012_CONTROL_PRECISION,
    })
    _write_json(output_dir / "manifest.json", {
        "spec": "SPEC-013", "modes": ["BASELINE"],
        "domains": [{
            "id": "quantum_mechanics_assertion_first",
            "label": "Quantum mechanics — assertion-first diagnostic",
            "representation": "parent.representation.json",
        }],
    })
    copy_semantic_navigation_assets(output_dir)
    (output_dir / "README.md").write_text(
        "# SPEC-013 assertion-first semantic compilation\n\n"
        "The trusted parent is a diagnostic artifact pending independent assertion and canonical "
        "semantic review. Complete the two review JSON files before finalization.\n",
        encoding="utf-8",
    )
    return report


def finalize_assertion_first_evaluation(output_dir: Path) -> dict[str, Any]:
    report_path = output_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assertion_review_path = output_dir / "assertion-review.json"
    assertion_review = json.loads(assertion_review_path.read_text(encoding="utf-8"))
    canonical_review_path = output_dir / "canonical-semantic-review.json"
    canonical_review = json.loads(canonical_review_path.read_text(encoding="utf-8"))
    for item in assertion_review.get("items", []):
        if item.get("classification") not in ASSERTION_REVIEW_CATEGORIES:
            raise ValidationError(f"invalid or pending assertion review for {item.get('id')!r}")
        if not isinstance(item.get("notes"), str) or not item["notes"].strip():
            raise ValidationError(f"assertion review notes required for {item.get('id')!r}")
        if item.get("canonical_disposition") == "UNCOMPILED_ASSERTION":
            if item.get("abstention_quality") not in {"APPROPRIATE", "UNNECESSARY"}:
                raise ValidationError(f"abstention quality required for {item.get('id')!r}")
        elif item.get("abstention_quality") != "NOT_ABSTAINED":
            raise ValidationError(f"non-abstained assertion has invalid abstention quality")
    for item in canonical_review.get("items", []):
        if item.get("classification") not in CANONICAL_REVIEW_CATEGORIES:
            raise ValidationError(f"invalid or pending canonical review for {item.get('id')!r}")
        if item.get("endpoint_precision") not in {"PRECISE", "IMPRECISE", "NOT_APPLICABLE"}:
            raise ValidationError(f"endpoint precision required for {item.get('id')!r}")
        if item.get("predicate_precision") not in {"PRECISE", "IMPRECISE", "NOT_APPLICABLE"}:
            raise ValidationError(f"predicate precision required for {item.get('id')!r}")
        if not isinstance(item.get("notes"), str) or not item["notes"].strip():
            raise ValidationError(f"canonical review notes required for {item.get('id')!r}")
    for item in canonical_review.get("known_control_defects", []):
        if item.get("experiment_status") not in {"FIXED", "RETAINED", "REPLACED", "ABSTAINED"}:
            raise ValidationError(f"control defect status required for {item.get('control_item')!r}")
        if not isinstance(item.get("notes"), str) or not item["notes"].strip():
            raise ValidationError(f"control defect notes required for {item.get('control_item')!r}")
    verdict = canonical_review.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        raise ValidationError(f"verdict must be one of: {', '.join(ALLOWED_VERDICTS)}")
    rationale = canonical_review.get("verdict_rationale", {})
    for dimension in (
        "assertion_fidelity", "structural_integrity", "grounding_integrity",
        "canonical_semantic_precision", "abstention_behavior", "cost_complexity",
    ):
        if not isinstance(rationale.get(dimension), str) or not rationale[dimension].strip():
            raise ValidationError(f"verdict rationale requires {dimension}")

    assertion_items = assertion_review["items"]
    faithful = sum(item["classification"] == "FAITHFUL" for item in assertion_items)
    assertion_summary = {
        category: sum(item["classification"] == category for item in assertion_items)
        for category in ASSERTION_REVIEW_CATEGORIES
    }
    assertion_summary.update({
        "total": len(assertion_items),
        "faithful_rate": faithful / len(assertion_items) if assertion_items else None,
        "appropriate_abstentions": sum(item["abstention_quality"] == "APPROPRIATE" for item in assertion_items),
        "unnecessary_abstentions": sum(item["abstention_quality"] == "UNNECESSARY" for item in assertion_items),
        "obvious_safe_relationships_unnecessarily_abstained": sum(
            bool(item.get("obvious_safe_relationship_unnecessarily_abstained"))
            for item in assertion_items
        ),
    })
    assertion_review.update({"status": "COMPLETE", "summary": assertion_summary})
    _write_json(assertion_review_path, assertion_review)
    canonical_items = canonical_review["items"]
    supported = sum(item["classification"] == "SUPPORTED" for item in canonical_items)
    precision = supported / len(canonical_items) if canonical_items else None
    canonical_review.update({
        "status": "COMPLETE",
        "reviewed_compiled_semantic_items": len(canonical_items),
        "supported_compiled_semantic_items": supported,
        "canonical_semantic_precision": precision,
    })
    _write_json(canonical_review_path, canonical_review)
    comparison = {
        "spec": "SPEC-013", "status": "COMPLETE", "verdict": verdict,
        "assertion_fidelity": assertion_summary,
        "canonical_semantics": {
            "spec_012_rejected_proposal_precision": SPEC_012_CONTROL_PRECISION,
            "assertion_first_precision": precision,
            "reviewed_compiled_items": len(canonical_items),
            "supported_compiled_items": supported,
            "recall_or_completeness_claimed": False,
            "known_control_defects": canonical_review["known_control_defects"],
            "new_assertion_first_defects": canonical_review.get("new_assertion_first_defects", []),
        },
        "abstention": {
            "uncompiled_assertion_count": report["canonicalization"]["uncompiled_assertions"],
            "abstention_rate": report["canonicalization"]["abstention_rate"],
            "appropriate": assertion_summary["appropriate_abstentions"],
            "unnecessary": assertion_summary["unnecessary_abstentions"],
            "obvious_safe_relationships_unnecessarily_abstained": assertion_summary[
                "obvious_safe_relationships_unnecessarily_abstained"
            ],
        },
        "structural": report["structural"],
        "grounding": report["assertion_grounding"],
        "cost_complexity": {
            "usage": report["usage"], "runtime_seconds": report["runtime_seconds"],
            "authoritative_monetary_cost": "NOT_AVAILABLE",
            "worth_assertion_boundary": canonical_review[
                "semantic_gain_worth_assertion_boundary_on_this_benchmark"
            ],
        },
        "verdict_rationale": rationale,
    }
    _write_json(output_dir / "control-comparison.json", comparison)
    report.update({
        "outcome": "COMPLETE", "verdict": verdict,
        "assertion_fidelity_review": assertion_summary,
        "canonical_semantic_review": {
            "categories": list(CANONICAL_REVIEW_CATEGORIES),
            "reviewed_items": len(canonical_items), "supported_items": supported,
            "precision": precision, "spec_012_control_precision": SPEC_012_CONTROL_PRECISION,
            "new_defects": canonical_review.get("new_assertion_first_defects", []),
        },
        "verdict_rationale": rationale,
        "semantic_gain_worth_assertion_boundary_on_this_benchmark": canonical_review[
            "semantic_gain_worth_assertion_boundary_on_this_benchmark"
        ],
    })
    _write_json(report_path, report)
    (output_dir / "README.md").write_text(
        "# SPEC-013 assertion-first semantic compilation\n\n"
        f"Final verdict: `{verdict}`. Read the assertion and canonical semantic reviews before "
        "using the trusted parent viewer; visualization is diagnostic rather than semantic proof.\n\n"
        "Launch from the repository root:\n\n```sh\n"
        ".venv/bin/knowledge-compiler view-representations "
        f"{output_dir.as_posix()} --port 8013\n```\n",
        encoding="utf-8",
    )
    return report
