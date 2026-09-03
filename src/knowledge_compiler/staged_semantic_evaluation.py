"""SPEC-012 staged semantic compilation benchmark and comparison artifacts."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Mapping

from .layout import with_layouts
from .models import KnowledgeModel, Origin, ValidationError
from .normalize import normalize_document, normalize_text
from .openai_extractor import DEFAULT_MODEL
from .openai_staged_extractor import (
    LINKING_PROMPT_VERSION,
    SYMBOL_PROMPT_VERSION,
    OpenAIStagedExtractor,
)
from .quantum_learning_evaluation import (
    _read_source_metadata,
    _representation_diagnostics,
    _structure_counts,
)
from .representation_builder import RepresentationBuilder
from .semantic_navigation import copy_semantic_navigation_assets
from .staged_compilation import (
    STAGED_COMPILER_VERSION,
    SemanticLinkingResult,
    StagedSemanticExtractor,
    SymbolDiscoveryProposal,
    SymbolTable,
    assemble_staged_knowledge_model,
    canonicalize_symbol_table,
)
from .structure_detection import StructureDetector


EVALUATION_VERSION = "spec-012-v1"
SEMANTIC_REVIEW_CATEGORIES = (
    "SUPPORTED",
    "IMPRECISE_ENDPOINT",
    "WRONG_PREDICATE",
    "REVERSED_DIRECTION",
    "OVERSTATED_CAUSALITY",
    "UNSUPPORTED",
    "LOSSY_BINARY_FORM",
    "OTHER",
)
ALLOWED_VERDICTS = (
    "STAGED_BETTER",
    "NO_MEANINGFUL_IMPROVEMENT",
    "STAGED_WORSE",
    "MIXED",
    "INCONCLUSIVE",
)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _usage(metadata: Mapping[str, Any]) -> dict[str, int]:
    raw = metadata.get("usage", {})
    return {
        key: int(raw.get(key, 0))
        for key in ("input_tokens", "output_tokens", "total_tokens")
    }


def _counts(model: KnowledgeModel) -> dict[str, int]:
    return {
        "entities": len(model.entities),
        "relationships": len(model.relationships),
        "claims": len(model.claims),
        "propositions": len(model.propositions),
    }


def _grounding(model: KnowledgeModel) -> dict[str, Any]:
    items = (*model.claims, *model.relationships, *model.propositions)
    source_items = [item for item in items if item.origin is Origin.SOURCE]
    inferred_items = [item for item in items if item.origin is Origin.INFERRED]
    spans = [span for item in source_items for span in item.evidence]
    exact = [span.quote == model.document.text[span.start_char:span.end_char] for span in spans]
    unique = [model.document.text.count(span.quote) == 1 for span in spans]
    return {
        "source_item_count": len(source_items),
        "inferred_item_count": len(inferred_items),
        "source_items_with_evidence": sum(bool(item.evidence) for item in source_items),
        "evidence_span_count": len(spans),
        "exact_evidence_span_count": sum(exact),
        "unique_evidence_span_count": sum(unique),
        "exact_evidence_resolution_rate": sum(exact) / len(exact) if exact else None,
        "unique_evidence_rate": sum(unique) / len(unique) if unique else None,
        "missing_quote_failures": 0,
        "ambiguous_quote_failures": 0,
        "source_inferred_invariant_violations": sum(
            (item.origin is Origin.SOURCE and not item.evidence)
            or (item.origin is Origin.INFERRED and bool(item.evidence))
            for item in items
        ),
    }


def _structural(model: KnowledgeModel, symbol_table: SymbolTable, linking: SemanticLinkingResult) -> dict[str, Any]:
    known = symbol_table.ids
    dangling_relationships = [
        item.id for item in model.relationships
        if item.source_entity_id not in known or item.target_entity_id not in known
    ]
    dangling_roles = [
        item.id for item in model.propositions
        if any(binding.entity_id not in known for binding in item.role_bindings)
    ]
    round_trip = KnowledgeModel.from_dict(model.to_dict()).to_dict() == model.to_dict()
    return {
        "valid_entity_inventory": True,
        "dangling_relationship_endpoint_count": len(dangling_relationships),
        "dangling_relationship_ids": dangling_relationships,
        "dangling_proposition_role_binding_count": len(dangling_roles),
        "dangling_proposition_ids": dangling_roles,
        "unknown_claim_reference_count": 0,
        "unknown_claim_references": "NOT_APPLICABLE_CLAIMS_HAVE_NO_ENTITY_REFERENCE_FIELD",
        "duplicate_or_alias_identity_count": 0,
        "schema_violation_count": 0,
        "symbol_table_violation_count": 0,
        "reported_missing_symbol_count": len(linking.missing_symbols),
        "reported_missing_symbols": [dict(item) for item in linking.missing_symbols],
        "pass_2_entity_creation_field_present": False,
        "knowledge_model_round_trip": round_trip,
    }


_CONTROL_CLASSIFICATIONS = {
    "rel-quantum-is-study": (
        "UNSUPPORTED", "IMPRECISE", "IMPRECISE",
        "Undefined target; cited QFT history does not support the asserted taxonomy.",
    ),
    "rel-revolution-develops-qm": (
        "OTHER", "PRECISE", "IMPRECISE",
        "CREATES overstates a historical/paradigm-development relation.",
    ),
    "rel-qm-explains-chemistry": (
        "IMPRECISE_ENDPOINT", "IMPRECISE", "PRECISE",
        "The source supports understanding chemistry, not enabling chemistry itself.",
    ),
    "rel-qm-explains-molecules": (
        "OVERSTATED_CAUSALITY", "IMPRECISE", "IMPRECISE",
        "A theory explaining molecular formation is not the physical cause of molecules.",
    ),
    "rel-energy-explains-blackbody": (
        "UNSUPPORTED", "PRECISE", "IMPRECISE",
        "The cited quote concerns a volume/current increase and does not support this edge.",
    ),
    "rel-frequency-increases-velocity": (
        "SUPPORTED", "PRECISE", "PRECISE",
        "The endpoints, direction, and INCREASES predicate match the cited sentence.",
    ),
    "rel-measurement-collapses-state": (
        "LOSSY_BINARY_FORM", "IMPRECISE", "IMPRECISE",
        "A collapse self-loop loses measurement as actor and the affected quantum state.",
    ),
    "rel-qft-is-quantum-theory": (
        "WRONG_PREDICATE", "IMPRECISE", "IMPRECISE",
        "The target and statement disagree, and the excerpt does not establish IS_A.",
    ),
    "rel-qed-is-qft": (
        "WRONG_PREDICATE", "PRECISE", "IMPRECISE",
        "The cited sentence calls QED a quantum theory of electromagnetism, not a QFT.",
    ),
    "rel-standard-model-is-qft": (
        "SUPPORTED", "PRECISE", "PRECISE",
        "The source explicitly identifies the Standard Model as the quantum field theory.",
    ),
    "rel-tunneling-enables-electron-penetration": (
        "IMPRECISE_ENDPOINT", "IMPRECISE", "PRECISE",
        "The target should be electron penetration through a barrier, not electron.",
    ),
}


def build_control_semantic_review(control_proposal: Mapping[str, Any]) -> dict[str, Any]:
    relationships = control_proposal.get("relationships", [])
    actual_ids = {item.get("id") for item in relationships}
    missing = sorted(set(_CONTROL_CLASSIFICATIONS) - actual_ids)
    unknown = sorted(actual_ids - set(_CONTROL_CLASSIFICATIONS))
    if missing or unknown:
        raise ValidationError(
            f"SPEC-011 control proposal no longer matches fixed review mapping; missing={missing}, unknown={unknown}"
        )
    items = []
    for relationship in relationships:
        classification, endpoint, predicate, notes = _CONTROL_CLASSIFICATIONS[relationship["id"]]
        items.append({
            "kind": "relationship",
            "id": relationship["id"],
            "classification": classification,
            "endpoint_precision": endpoint,
            "predicate_precision": predicate,
            "notes": notes,
        })
    supported = sum(item["classification"] == "SUPPORTED" for item in items)
    return {
        "spec": "SPEC-012",
        "review_subject": "SPEC-011_PRESERVED_SECOND_REJECTED_PROPOSAL",
        "review_categories": list(SEMANTIC_REVIEW_CATEGORIES),
        "mapping_basis": "SPEC-011 repository semantic review and accepted DEBRIEF-011",
        "items": items,
        "reviewed_accepted_item_count": len(items),
        "supported_item_count": supported,
        "semantic_precision": supported / len(items) if items else None,
        "known_structural_rejection_count": 1,
        "known_grounding_rejection_count": 0,
    }


def _staged_review_template(model: KnowledgeModel) -> dict[str, Any]:
    items = []
    for relationship in model.relationships:
        items.append({
            "kind": "relationship",
            "id": relationship.id,
            "statement": relationship.statement,
            "source_entity_id": relationship.source_entity_id,
            "predicate": relationship.relationship_type.value,
            "target_entity_id": relationship.target_entity_id,
            "classification": "PENDING",
            "endpoint_precision": "PENDING",
            "predicate_precision": "PENDING",
            "notes": "",
        })
    for proposition in model.propositions:
        items.append({
            "kind": "proposition",
            "id": proposition.id,
            "statement": proposition.statement,
            "role_bindings": [
                {"role": binding.role.value, "entity_id": binding.entity_id}
                for binding in proposition.role_bindings
            ],
            "predicate": proposition.relationship_type.value,
            "classification": "PENDING",
            "endpoint_precision": "PENDING",
            "predicate_precision": "PENDING",
            "notes": "",
        })
    return {
        "spec": "SPEC-012",
        "status": "PENDING_INDEPENDENT_REPOSITORY_REVIEW",
        "review_categories_fixed_before_live_output": list(SEMANTIC_REVIEW_CATEGORIES),
        "review_scope": "ALL_ACCEPTED_RELATIONSHIPS_AND_PROPOSITIONS",
        "independent_from_generation": True,
        "items": items,
        "control_defect_comparison": [
            {
                "control_defect": "theory represented as physical cause of molecules",
                "control_item_ids": ["rel-qm-explains-molecules"],
                "staged_status": "PENDING",
                "notes": "",
            },
            {
                "control_defect": "energy quanta asserted to cause black-body radiation with mismatched evidence",
                "control_item_ids": ["rel-energy-explains-blackbody"],
                "staged_status": "PENDING",
                "notes": "",
            },
            {
                "control_defect": "wave-function collapse self-loop loses measurement/state roles",
                "control_item_ids": ["rel-measurement-collapses-state"],
                "staged_status": "PENDING",
                "notes": "",
            },
            {
                "control_defect": "mismatched IS_A semantics around QFT and QED",
                "control_item_ids": ["rel-qft-is-quantum-theory", "rel-qed-is-qft"],
                "staged_status": "PENDING",
                "notes": "",
            },
            {
                "control_defect": "tunneling targets electron rather than electron penetration",
                "control_item_ids": ["rel-tunneling-enables-electron-penetration"],
                "staged_status": "PENDING",
                "notes": "",
            },
        ],
        "verdict": "PENDING",
        "verdict_rationale": {
            "structural": "",
            "grounding": "",
            "semantic": "",
            "cost_complexity": "",
        },
        "reliability_gain_worth_additional_pass_on_this_benchmark": "PENDING",
        "new_staged_semantic_defects": [],
    }


def _attempt(
    *, sequence: int, stage: str, started_at: str, elapsed: float,
    outcome: str, metadata: Mapping[str, Any], provider_call_attempted: bool,
    error: Exception | None = None, rejected_output_preserved: bool = False,
) -> dict[str, Any]:
    result = {
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
        result.update({"error_type": type(error).__name__, "error": str(error)})
    return result


def _write_history(output_dir: Path, attempts: list[dict[str, Any]]) -> None:
    _write_json(output_dir / "run-history.json", {
        "spec": "SPEC-012",
        "attempts": attempts,
        "primary_live_call_budget": 2,
        "current_run_live_call_count": sum(bool(item["provider_call_attempted"]) for item in attempts),
        "semantic_retry_count": 0,
        "automatic_retry_count": 0,
        "hidden_retries_or_favorable_run_selection": False,
        "prompt_iteration_after_live_output": False,
        "external_semantic_enrichment": False,
        "third_semantic_pass": False,
        "child_resolution_call": False,
    })


def _write_failure(
    output_dir: Path, source_report: Mapping[str, Any], attempts: list[dict[str, Any]],
    stage: str, error: Exception,
) -> None:
    _write_history(output_dir, attempts)
    _write_json(output_dir / "comparison.json", {
        "spec": "SPEC-012", "status": "COMPLETE_OPERATIONAL_FAILURE",
        "verdict": "INCONCLUSIVE", "failed_stage": stage, "failure": str(error),
        "control_observed_dangling_endpoint_failures": 2,
        "control_preserved_proposal_dangling_endpoint_count": 1,
        "staged_dangling_endpoint_count": "NOT_AVAILABLE",
    })
    _write_json(output_dir / "report.json", {
        "spec": "SPEC-012", "evaluation_version": EVALUATION_VERSION,
        "outcome": f"{stage}_FAILED", "verdict": "INCONCLUSIVE",
        "failure": str(error), "source": dict(source_report),
        "live_call_count": sum(bool(item["provider_call_attempted"]) for item in attempts),
        "retry_count": 0, "monetary_cost": "NOT_AVAILABLE",
        "downstream": "NOT_RUN_NO_TRUSTED_PARENT",
    })
    (output_dir / "README.md").write_text(
        "# SPEC-012 preserved staged failure\n\n"
        f"The staged experiment failed during `{stage}` and preserved all available proposals "
        "and provider metadata. No rejected graph was rendered. See `report.json`, "
        "`run-history.json`, and the pass result artifacts.\n",
        encoding="utf-8",
    )


def run_staged_semantic_evaluation(
    *,
    source_path: Path,
    source_metadata_path: Path,
    control_proposal_path: Path,
    output_dir: Path,
    model: str = DEFAULT_MODEL,
    extractor_factory: Callable[[], StagedSemanticExtractor] | None = None,
) -> dict[str, Any]:
    """Run the primary two-call staged experiment without any retry."""
    output_dir.mkdir(parents=True, exist_ok=False)
    normalized_text = normalize_text(source_path.read_text(encoding="utf-8"))
    source_metadata = _read_source_metadata(source_metadata_path, normalized_text)
    source_report = {
        **source_metadata,
        "word_count": len(normalized_text.split()),
        "character_count": len(normalized_text),
        "source_processing_strategy": "FULL_SOURCE_TWO_PASS_STAGED",
        "segment_count": 1,
        "source_text_unchanged": True,
        "external_semantic_enrichment": False,
    }
    _write_json(output_dir / "source-metadata.json", source_report)
    control_proposal = json.loads(control_proposal_path.read_text(encoding="utf-8"))
    _write_json(output_dir / "control-semantic-review.json", build_control_semantic_review(control_proposal))

    extractor = extractor_factory() if extractor_factory else OpenAIStagedExtractor(model=model)
    provider_call_attempted = extractor_factory is None
    attempts: list[dict[str, Any]] = []

    started_at = _utc_now()
    started = time.perf_counter()
    try:
        symbol_proposal = extractor.discover_symbols(
            normalize_document(normalized_text, metadata=source_report)
        )
        symbol_table = canonicalize_symbol_table(symbol_proposal)
    except Exception as exc:
        metadata = dict(getattr(extractor, "last_pass_1_metadata", {}))
        raw = getattr(extractor, "last_pass_1_raw", None)
        _write_json(output_dir / "pass-1-result.json", {
            "spec": "SPEC-012", "stage": "SYMBOL_DISCOVERY", "outcome": "FAILED",
            "failure": str(exc), "raw_proposal": raw, "provider_metadata": metadata,
        })
        attempts.append(_attempt(
            sequence=1, stage="SYMBOL_DISCOVERY", started_at=started_at,
            elapsed=time.perf_counter() - started, outcome="FAILED", metadata=metadata,
            provider_call_attempted=provider_call_attempted, error=exc,
            rejected_output_preserved=raw is not None,
        ))
        _write_failure(output_dir, source_report, attempts, "PASS_1", exc)
        raise

    pass_1_runtime = time.perf_counter() - started
    pass_1_metadata = dict(symbol_proposal.metadata)
    attempts.append(_attempt(
        sequence=1, stage="SYMBOL_DISCOVERY", started_at=started_at,
        elapsed=pass_1_runtime, outcome="SUCCESS", metadata=pass_1_metadata,
        provider_call_attempted=provider_call_attempted,
    ))
    _write_json(output_dir / "symbol-table.json", symbol_table.to_dict())
    _write_json(output_dir / "pass-1-result.json", {
        "spec": "SPEC-012", "stage": "SYMBOL_DISCOVERY", "outcome": "SUCCESS",
        "prompt_version": pass_1_metadata.get("prompt_version", SYMBOL_PROMPT_VERSION),
        "raw_proposal": getattr(extractor, "last_pass_1_raw", None) or symbol_proposal.to_dict(),
        "provider_metadata": pass_1_metadata,
        "normalization": dict(symbol_table.diagnostics),
    })

    document = normalize_document(normalized_text, metadata=source_report)
    started_at = _utc_now()
    started = time.perf_counter()
    try:
        linking = extractor.link_semantics(document, symbol_table)
        parent = assemble_staged_knowledge_model(document, symbol_table, linking)
    except Exception as exc:
        metadata = dict(getattr(extractor, "last_pass_2_metadata", {}))
        raw = getattr(extractor, "last_pass_2_raw", None)
        _write_json(output_dir / "pass-2-result.json", {
            "spec": "SPEC-012", "stage": "SEMANTIC_LINKING", "outcome": "FAILED",
            "failure": str(exc), "raw_proposal": raw, "provider_metadata": metadata,
            "symbol_table_size": len(symbol_table.entities),
            "symbol_table_violations": [
                dict(item) for item in getattr(exc, "violations", ())
            ],
        })
        attempts.append(_attempt(
            sequence=2, stage="SEMANTIC_LINKING", started_at=started_at,
            elapsed=time.perf_counter() - started, outcome="FAILED", metadata=metadata,
            provider_call_attempted=provider_call_attempted, error=exc,
            rejected_output_preserved=raw is not None,
        ))
        _write_failure(output_dir, source_report, attempts, "PASS_2", exc)
        raise

    pass_2_runtime = time.perf_counter() - started
    pass_2_metadata = dict(linking.metadata)
    attempts.append(_attempt(
        sequence=2, stage="SEMANTIC_LINKING", started_at=started_at,
        elapsed=pass_2_runtime, outcome="SUCCESS", metadata=pass_2_metadata,
        provider_call_attempted=provider_call_attempted,
    ))
    _write_history(output_dir, attempts)
    _write_json(output_dir / "pass-2-result.json", {
        "spec": "SPEC-012", "stage": "SEMANTIC_LINKING", "outcome": "SUCCESS",
        "prompt_version": pass_2_metadata.get("prompt_version", LINKING_PROMPT_VERSION),
        "raw_proposal": getattr(extractor, "last_pass_2_raw", None) or linking.to_dict(),
        "normalized_proposal": linking.to_dict(),
        "provider_metadata": pass_2_metadata,
        "symbol_table_size": len(symbol_table.entities),
    })
    parent = KnowledgeModel(
        document=parent.document,
        entities=parent.entities,
        claims=parent.claims,
        relationships=parent.relationships,
        propositions=parent.propositions,
        metadata={
            **dict(parent.metadata),
            "domain": "quantum_mechanics",
            "evaluation_version": EVALUATION_VERSION,
            "symbol_discovery_provider": pass_1_metadata,
            "semantic_linking_provider": pass_2_metadata,
        },
    )
    structural = _structural(parent, symbol_table, linking)
    grounding = _grounding(parent)
    structures = StructureDetector().detect(parent)
    representation = with_layouts(RepresentationBuilder().build(
        parent,
        structures,
        presentation_metadata={
            "domain": "quantum_mechanics",
            "title": "Introduction to quantum mechanics — staged compilation",
        },
    ))
    _write_json(output_dir / "parent.knowledge.json", parent.to_dict())
    _write_json(output_dir / "parent.structures.json", structures.to_dict())
    _write_json(output_dir / "parent.representation.json", representation.to_dict())
    _write_json(output_dir / "staged-semantic-review.json", _staged_review_template(parent))
    _write_json(output_dir / "comparison.json", {
        "spec": "SPEC-012", "status": "PENDING_INDEPENDENT_SEMANTIC_REVIEW",
        "verdict": "PENDING", "control_dangling_endpoint_count": 1,
        "staged_dangling_endpoint_count": structural["dangling_relationship_endpoint_count"],
    })
    report = {
        "spec": "SPEC-012",
        "evaluation_version": EVALUATION_VERSION,
        "outcome": "PENDING_INDEPENDENT_SEMANTIC_REVIEW",
        "verdict": "PENDING",
        "source": source_report,
        "control_evidence": {
            "source": "SPEC-011 preserved one-pass run history and second rejected proposal",
            "attempt_1_failure": "dangling relationship endpoint: measurement",
            "attempt_2_failure": "dangling relationship endpoint: quantum-theory",
            "observed_dangling_endpoint_failures": 2,
            "preserved_second_proposal_dangling_endpoint_count": 1,
            "control_proposal_path": str(control_proposal_path),
            "control_artifacts_modified": False,
        },
        "provider": pass_1_metadata.get("provider", "fixture"),
        "requested_model": model,
        "prompt_versions": {
            "pass_1": pass_1_metadata.get("prompt_version", SYMBOL_PROMPT_VERSION),
            "pass_2": pass_2_metadata.get("prompt_version", LINKING_PROMPT_VERSION),
        },
        "compiler_version": STAGED_COMPILER_VERSION,
        "provider_request_ids": {
            "pass_1": pass_1_metadata.get("provider_request_id"),
            "pass_2": pass_2_metadata.get("provider_request_id"),
        },
        "provider_controls": {
            "store": False,
            "sdk_automatic_retries": 0,
            "semantic_retries": 0,
            "prompt_iteration_after_live_output": False,
        },
        "prompt_sizes": {
            "pass_1_instruction_characters": pass_1_metadata.get("prompt_character_count"),
            "pass_1_input_characters": pass_1_metadata.get("input_character_count"),
            "pass_2_instruction_characters": pass_2_metadata.get("prompt_character_count"),
            "pass_2_input_characters": pass_2_metadata.get("input_character_count"),
            "pass_2_symbol_table_characters": pass_2_metadata.get("symbol_table_character_count"),
        },
        "counts": _counts(parent),
        "structural": structural,
        "grounding": grounding,
        "symbol_table": dict(symbol_table.diagnostics),
        "downstream": {
            "structure_counts": _structure_counts(structures),
            "representation": _representation_diagnostics(parent, representation),
            "child_resolution": "NOT_ATTEMPTED_BY_SPEC",
        },
        "usage": {
            "pass_1": _usage(pass_1_metadata),
            "pass_2": _usage(pass_2_metadata),
            "combined": {
                key: _usage(pass_1_metadata)[key] + _usage(pass_2_metadata)[key]
                for key in ("input_tokens", "output_tokens", "total_tokens")
            },
            "control_known_second_attempt": {
                "input_tokens": 11006, "output_tokens": 2788, "total_tokens": 13794,
            },
            "control_first_attempt": "NOT_AVAILABLE",
        },
        "runtime_seconds": {
            "pass_1": round(pass_1_runtime, 3),
            "pass_2": round(pass_2_runtime, 3),
            "combined": round(pass_1_runtime + pass_2_runtime, 3),
            "control_known_total": 44.493,
        },
        "monetary_cost": "NOT_AVAILABLE",
        "live_call_count": sum(bool(item["provider_call_attempted"]) for item in attempts),
        "retry_count": 0,
        "no_hidden_retries": True,
        "external_semantic_enrichment": False,
        "dependencies_added": [],
        "dependencies_removed": [],
        "complexity": {
            "new_runtime_modules": [
                "staged_compilation",
                "openai_staged_extractor",
                "staged_semantic_evaluation",
            ],
            "new_provider_calls_vs_one_pass": 1,
            "canonical_ir_changed": False,
            "relationship_vocabulary_changed": False,
            "proposition_vocabulary_changed": False,
            "grounding_rules_changed": False,
        },
    }
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "manifest.json", {
        "spec": "SPEC-012", "modes": ["BASELINE"],
        "domains": [{
            "id": "quantum_mechanics_staged",
            "label": "Quantum mechanics — staged diagnostic",
            "representation": "parent.representation.json",
        }],
    })
    copy_semantic_navigation_assets(output_dir)
    (output_dir / "README.md").write_text(
        "# SPEC-012 staged semantic compilation\n\n"
        f"Original source: [{source_metadata['title']}]({source_metadata['permanent_url']})\n\n"
        "The trusted parent and viewer are diagnostic artifacts pending independent semantic "
        "review. Graph appearance is not evidence of semantic correctness.\n\n"
        f"Source-derived content is reused under {source_metadata['license']}.\n\n"
        "After completing `staged-semantic-review.json`, finalize with:\n\n"
        "```sh\n.venv/bin/knowledge-compiler finalize-staged-semantic-compilation "
        f"{output_dir.as_posix()}\n```\n",
        encoding="utf-8",
    )
    return report


def finalize_staged_semantic_evaluation(output_dir: Path) -> dict[str, Any]:
    """Validate the independent review and write the final comparison/verdict."""
    report_path = output_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    review = json.loads((output_dir / "staged-semantic-review.json").read_text(encoding="utf-8"))
    control = json.loads((output_dir / "control-semantic-review.json").read_text(encoding="utf-8"))
    parent = KnowledgeModel.from_dict(json.loads((output_dir / "parent.knowledge.json").read_text(encoding="utf-8")))
    expected = {
        ("relationship", item.id) for item in parent.relationships
    } | {("proposition", item.id) for item in parent.propositions}
    actual = {(item.get("kind"), item.get("id")) for item in review.get("items", [])}
    if actual != expected:
        raise ValidationError(
            f"staged semantic review item set mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
        )
    for item in review["items"]:
        if item.get("classification") not in SEMANTIC_REVIEW_CATEGORIES:
            raise ValidationError(f"invalid or pending semantic classification for {item.get('id')!r}")
        if item.get("endpoint_precision") not in {"PRECISE", "IMPRECISE", "NOT_APPLICABLE"}:
            raise ValidationError(f"invalid or pending endpoint precision for {item.get('id')!r}")
        if item.get("predicate_precision") not in {"PRECISE", "IMPRECISE", "NOT_APPLICABLE"}:
            raise ValidationError(f"invalid or pending predicate precision for {item.get('id')!r}")
        if not isinstance(item.get("notes"), str) or not item["notes"].strip():
            raise ValidationError(f"semantic review notes are required for {item.get('id')!r}")
    for item in review.get("control_defect_comparison", []):
        if item.get("staged_status") not in {"FIXED", "RETAINED", "REPLACED", "NOT_COMPARABLE"}:
            raise ValidationError(
                f"invalid or pending control-defect comparison for {item.get('control_defect')!r}"
            )
        if not isinstance(item.get("notes"), str) or not item["notes"].strip():
            raise ValidationError(
                f"control-defect comparison notes required for {item.get('control_defect')!r}"
            )
    verdict = review.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        raise ValidationError(f"final verdict must be one of: {', '.join(ALLOWED_VERDICTS)}")
    rationale = review.get("verdict_rationale", {})
    for dimension in ("structural", "grounding", "semantic", "cost_complexity"):
        if not isinstance(rationale.get(dimension), str) or not rationale[dimension].strip():
            raise ValidationError(f"verdict rationale requires non-empty {dimension}")
    supported = sum(item["classification"] == "SUPPORTED" for item in review["items"])
    reviewed = len(review["items"])
    staged_precision = supported / reviewed if reviewed else None
    review.update({
        "status": "COMPLETE_INDEPENDENT_REPOSITORY_REVIEW",
        "reviewed_accepted_item_count": reviewed,
        "supported_item_count": supported,
        "semantic_precision": staged_precision,
    })
    _write_json(output_dir / "staged-semantic-review.json", review)
    comparison = {
        "spec": "SPEC-012",
        "status": "COMPLETE",
        "verdict": verdict,
        "structural": {
            "control_observed_dangling_endpoint_failures": 2,
            "control_preserved_proposal_dangling_relationship_endpoints": 1,
            "staged_dangling_relationship_endpoints": report["structural"]["dangling_relationship_endpoint_count"],
            "control_round_trip": False,
            "staged_round_trip": report["structural"]["knowledge_model_round_trip"],
            "staged_missing_symbol_diagnostics": report["structural"]["reported_missing_symbols"],
        },
        "grounding": {
            "control": {
                "source_items": 20, "inferred_items": 0,
                "exact_evidence_spans": 20, "evidence_spans": 20,
                "exact_resolution_rate": 1.0, "unique_evidence_rate": 1.0,
                "grounding_rejections": 0,
            },
            "staged": report["grounding"],
        },
        "semantic": {
            "control_reviewed_accepted_items": control["reviewed_accepted_item_count"],
            "control_supported_items": control["supported_item_count"],
            "control_semantic_precision": control["semantic_precision"],
            "staged_reviewed_accepted_items": reviewed,
            "staged_supported_items": supported,
            "staged_semantic_precision": staged_precision,
            "review_categories": list(SEMANTIC_REVIEW_CATEGORIES),
            "semantic_volume_not_used_as_quality_proxy": True,
            "recall_or_completeness_claimed": False,
            "control_defect_comparison": review.get("control_defect_comparison", []),
            "new_staged_semantic_defects": review.get("new_staged_semantic_defects", []),
        },
        "cost_complexity": {
            "staged_usage": report["usage"],
            "runtime_seconds": report["runtime_seconds"],
            "monetary_cost": "NOT_AVAILABLE",
            "additional_provider_passes_vs_control": 1,
            "worth_additional_pass_on_this_benchmark": review[
                "reliability_gain_worth_additional_pass_on_this_benchmark"
            ],
        },
        "verdict_rationale": rationale,
    }
    _write_json(output_dir / "comparison.json", comparison)
    report.update({
        "outcome": "COMPLETE",
        "verdict": verdict,
        "semantic_review": {
            "categories": list(SEMANTIC_REVIEW_CATEGORIES),
            "control_precision": control["semantic_precision"],
            "staged_precision": staged_precision,
            "reviewed_accepted_items": reviewed,
            "supported_items": supported,
            "new_staged_semantic_defects": review.get("new_staged_semantic_defects", []),
        },
        "verdict_rationale": rationale,
        "reliability_gain_worth_additional_pass_on_this_benchmark": review[
            "reliability_gain_worth_additional_pass_on_this_benchmark"
        ],
    })
    _write_json(report_path, report)
    (output_dir / "README.md").write_text(
        "# SPEC-012 staged semantic compilation\n\n"
        f"Final benchmark verdict: `{verdict}`. Read `comparison.json` and "
        "`staged-semantic-review.json` before inspecting the graph. The viewer is a "
        "diagnostic, not semantic proof.\n\nLaunch from the repository root:\n\n"
        "```sh\n.venv/bin/knowledge-compiler view-representations "
        f"{output_dir.as_posix()} --port 8012\n```\n",
        encoding="utf-8",
    )
    return report
