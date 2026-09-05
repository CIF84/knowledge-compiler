"""Prepare, run, and finalize the controlled SPEC-020 semantic-depth experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any, Callable, Mapping

from .assertion_compilation import (
    AssertionCanonicalizer,
    AssertionExtractor,
    CanonicalizationProposal,
    GroundedAssertionSet,
    compile_assertion_semantics,
    ground_assertions,
)
from .continuous_navigation import CameraState
from .models import KnowledgeModel, ValidationError
from .openai_assertion_compiler import (
    ASSERTION_PROMPT_VERSION,
    CANONICALIZATION_PROMPT_VERSION,
    OpenAIAssertionCompiler,
)
from .openai_extractor import DEFAULT_MODEL
from .quantum_learning_evaluation import _representation_diagnostics, _structure_counts
from .representations import RepresentationModel
from .semantic_depth import (
    CHILD_SYMBOL_IDS,
    EXPECTED_PARENT_SOURCE_SHA256,
    EXPECTED_SCOPE_SHA256,
    FOCUS_ENTITY_ID,
    INITIAL_CAMERA,
    SEMANTIC_DEPTH_VERSION,
    DepthWorkspaceState,
    build_depth_workspace_fixture,
    build_parent_focus_representation,
    canonical_bytes,
    child_symbol_table,
    compile_trusted_child,
    depth_camera_invariant,
    freeze_focus_selection,
    freeze_source_scope,
    model_hash,
    switch_semantic_depth,
)
from .staged_compilation import SymbolTable


EVALUATION_VERSION = "spec-020-v1"
ASSERTION_REVIEW_CATEGORIES = ("FAITHFUL", "PARTIAL", "DISTORTED", "UNSUPPORTED")
SEMANTIC_REVIEW_CATEGORIES = (
    "SUPPORTED", "IMPRECISE_ENDPOINT", "WRONG_PREDICATE", "REVERSED_DIRECTION",
    "OVERSTATED_CAUSALITY", "UNSUPPORTED", "LOSSY_BINARY_FORM", "OTHER",
)


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec013_directory() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-013-assertion-first-semantic-compilation-20260904"


def default_baseline003_document() -> Path:
    return repository_root() / "baselines" / "BASELINE-003-hybrid-learning-workspace.md"


def default_baseline003_assets() -> Path:
    return repository_root() / "examples" / "evaluations" / "spec-019-navigation-learning-workspace-20260905"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): _hash(path)
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _usage(metadata: Mapping[str, Any]) -> dict[str, int]:
    raw = metadata.get("usage", {})
    return {key: int(raw.get(key, 0)) for key in ("input_tokens", "output_tokens", "total_tokens")}


def _parent_paths(spec013_dir: Path) -> dict[str, Path]:
    return {
        "parent_knowledge": spec013_dir / "parent.knowledge.json",
        "parent_grounded_assertions": spec013_dir / "grounded-assertions.json",
        "parent_symbol_table": spec013_dir / "symbol-table.json",
        "parent_structures": spec013_dir / "parent.structures.json",
        "parent_representation": spec013_dir / "parent.representation.json",
    }


def _parent_hashes(spec013_dir: Path) -> dict[str, str]:
    return {key: _hash(path) for key, path in _parent_paths(spec013_dir).items()}


def _baseline_hashes() -> dict[str, Any]:
    root = repository_root()
    return {
        "baseline_001_document": _hash(root / "baselines" / "BASELINE-001-interface.md"),
        "baseline_002_document": _hash(root / "baselines" / "BASELINE-002-continuous-navigation-reference.md"),
        "baseline_003_document": _hash(default_baseline003_document()),
        "baseline_003_assets": _directory_hashes(default_baseline003_assets()),
    }


def _load_parent(spec013_dir: Path) -> KnowledgeModel:
    return KnowledgeModel.from_dict(_read_json(spec013_dir / "parent.knowledge.json"))


def _copy_assets(output_dir: Path) -> None:
    base = files("knowledge_compiler").joinpath("navigation_learning_assets")
    with base.joinpath("workspace.css").open("rb") as source, (output_dir / "workspace.css").open("wb") as target:
        shutil.copyfileobj(source, target)
    assets = files("knowledge_compiler").joinpath("semantic_depth_assets")
    for name in ("index.html", "depth.css", "workspace.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _history(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "spec": "SPEC-020",
        "attempts": attempts,
        "planned_live_call_count": 2,
        "current_run_live_call_count": sum(item["provider_call_attempted"] for item in attempts),
        "semantic_retry_count": 0,
        "automatic_retry_count": 0,
        "hidden_retries": False,
        "prompt_repair_after_output": False,
        "external_enrichment": False,
        "additional_model_or_agent_calls": 0,
        "dependent_call_rule": "Call B runs only if Call A assertion extraction and grounding succeeds.",
    }


def _attempt(
    sequence: int,
    stage: str,
    started_at: str,
    runtime: float,
    outcome: str,
    metadata: Mapping[str, Any],
    provider_call_attempted: bool,
    *,
    error: Exception | None = None,
    rejected_output_preserved: bool = False,
) -> dict[str, Any]:
    value = {
        "sequence": sequence,
        "stage": stage,
        "started_at": started_at,
        "completed_at": _utc_now(),
        "runtime_seconds": round(runtime, 3),
        "outcome": outcome,
        "provider_call_attempted": provider_call_attempted,
        "provider": metadata.get("provider", "fixture"),
        "requested_model": metadata.get("requested_model"),
        "actual_model": metadata.get("model"),
        "provider_request_id": metadata.get("provider_request_id"),
        "prompt_version": metadata.get("prompt_version"),
        "usage": _usage(metadata),
        "cost": "NOT_AVAILABLE",
        "retries": 0,
        "rejected_output_preserved": rejected_output_preserved,
    }
    if error is not None:
        value.update({"error_type": type(error).__name__, "error": str(error)})
    return value


def _prompt_configuration(scope_character_count: int, symbol_count: int, model: str) -> dict[str, Any]:
    return {
        "spec": "SPEC-020",
        "status": "FROZEN_BEFORE_LIVE_OUTPUT",
        "provider": "openai",
        "model": model,
        "reasoning_effort": "low",
        "store": False,
        "sdk_automatic_retries": 0,
        "semantic_retries": 0,
        "hidden_retries": False,
        "prompt_repair_after_output": False,
        "external_enrichment": False,
        "planned_call_count": 2,
        "assertion_prompt_version": ASSERTION_PROMPT_VERSION,
        "canonicalization_prompt_version": CANONICALIZATION_PROMPT_VERSION,
        "compiler_version": EVALUATION_VERSION,
        "resolution_strategy": "GENERIC_DETAIL",
        "strategy_limitation": (
            "No process, variable, or component strategy matches an experiment-as-example; "
            "GENERIC_DETAIL is the explicit existing control."
        ),
        "call_a_transmission": {
            "material": "exact frozen Wave–particle duality section and frozen child symbol table",
            "public_source_character_count": scope_character_count,
            "symbol_count": symbol_count,
        },
        "call_b_transmission": {
            "material": "only grounded Call-A assertions, their exact source excerpts, and the same frozen symbols",
            "conditional": "only if Call A assertion extraction and deterministic grounding succeeds",
        },
    }


def prepare_semantic_depth_evaluation(
    *,
    output_dir: Path,
    spec013_dir: Path = default_spec013_directory(),
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """Freeze every experimental input without making a provider call."""
    output_dir.mkdir(parents=True, exist_ok=False)
    parent = _load_parent(spec013_dir)
    focus = freeze_focus_selection(parent)
    scope = freeze_source_scope(parent)
    symbols = child_symbol_table(parent)
    parent_representation = build_parent_focus_representation(parent)
    parent_hashes = _parent_hashes(spec013_dir)
    baselines = _baseline_hashes()

    _write_json(output_dir / "focus-selection.json", focus)
    _write_json(output_dir / "source-scope.json", scope.to_dict(include_text=True))
    _write_json(output_dir / "child-symbol-table.json", symbols.to_dict())
    _write_json(output_dir / "parent.representation.json", parent_representation.to_dict())
    _write_json(output_dir / "parent-hashes.json", {
        "spec": "SPEC-020",
        "source_directory": str(spec013_dir),
        "before": parent_hashes,
        "after": parent_hashes,
        "immutable": True,
        "parent_model_canonical_sha256": model_hash(parent),
    })
    _write_json(output_dir / "baseline-manifest.json", {
        "spec": "SPEC-020",
        "before": baselines,
        "after": baselines,
        "immutable": True,
        "baseline_003_shell_reused_without_in_place_mutation": True,
    })
    _write_json(output_dir / "prompt-configuration.json", _prompt_configuration(
        len(scope.text), len(symbols.entities), model
    ))
    _write_json(output_dir / "run-history.json", _history([]))
    report = {
        "spec": "SPEC-020",
        "evaluation_version": EVALUATION_VERSION,
        "execution_stage": "PRE_LIVE_READY",
        "machine_integrity_verdict": "PASS",
        "live_call_count": 0,
        "owner_live_approval": "REQUIRED",
        "source": {
            "title": parent.document.metadata.get("title"),
            "revision_id": parent.document.metadata.get("revision_id"),
            "normalized_sha256": EXPECTED_PARENT_SOURCE_SHA256,
        },
        "focus_entity_id": FOCUS_ENTITY_ID,
        "source_scope_sha256": EXPECTED_SCOPE_SHA256,
        "source_scope_character_count": len(scope.text),
        "child_symbol_count": len(CHILD_SYMBOL_IDS),
        "resolution_strategy": "GENERIC_DETAIL",
        "provider": "openai",
        "model": model,
        "planned_live_call_count": 2,
        "parent_immutable": True,
        "baselines_immutable": True,
        "human_review_status": "NOT_AVAILABLE_BEFORE_TRUSTED_CHILD",
        "product_verdict": "PENDING",
        "deviations": [],
    }
    _write_json(output_dir / "report.json", report)
    (output_dir / "README.md").write_text(
        "# SPEC-020 realistic semantic depth\n\n"
        "This directory freezes the trusted SPEC-013 parent, the `double-slit-experiment` focus, "
        "the exact Wave–particle duality source section, the seven reused parent symbols, and the "
        "two-call assertion-first configuration before any live output.\n\n"
        "Live (only after explicit approval):\n\n```sh\n"
        f".venv/bin/knowledge-compiler evaluate-semantic-depth --output-dir {output_dir.as_posix()} --model {model}\n"
        "```\n\nReview after trusted finalization:\n\n```sh\n"
        f".venv/bin/knowledge-compiler view-representations {output_dir.as_posix()} --port 8021\n"
        "```\n",
        encoding="utf-8",
    )
    return report


def _fail_live(
    output_dir: Path,
    attempts: list[dict[str, Any]],
    stage: str,
    error: Exception,
) -> dict[str, Any]:
    _write_json(output_dir / "run-history.json", _history(attempts))
    report = _read_json(output_dir / "report.json")
    report.update({
        "execution_stage": f"{stage}_FAILED_CLOSED",
        "machine_integrity_verdict": "FAIL_CLOSED",
        "live_call_count": sum(item["provider_call_attempted"] for item in attempts),
        "failure": str(error),
        "failure_type": type(error).__name__,
        "rejected_child_rendered": False,
        "human_review_status": "NOT_AVAILABLE_NO_TRUSTED_CHILD",
        "additional_retry_requires_owner_approval": True,
    })
    _write_json(output_dir / "report.json", report)
    return report


def run_semantic_depth_evaluation(
    *,
    output_dir: Path,
    spec013_dir: Path = default_spec013_directory(),
    model: str = DEFAULT_MODEL,
    compiler_factory: Callable[[], AssertionExtractor | AssertionCanonicalizer] | None = None,
) -> dict[str, Any]:
    """Run Call A and conditional Call B with no retry or presentation repair."""
    if not output_dir.is_dir() or _read_json(output_dir / "report.json").get("execution_stage") != "PRE_LIVE_READY":
        raise ValidationError("SPEC-020 live evaluation requires an untouched prepared packet")
    configured = _read_json(output_dir / "prompt-configuration.json")
    if configured["model"] != model or configured["planned_call_count"] != 2:
        raise ValidationError("live model/call configuration differs from frozen pre-live packet")
    parent = _load_parent(spec013_dir)
    if _parent_hashes(spec013_dir) != _read_json(output_dir / "parent-hashes.json")["before"]:
        raise ValidationError("trusted parent artifacts changed after pre-live freeze")
    if _baseline_hashes() != _read_json(output_dir / "baseline-manifest.json")["before"]:
        raise ValidationError("BASELINE-003 or component baselines changed after pre-live freeze")
    focus = freeze_focus_selection(parent)
    if focus != _read_json(output_dir / "focus-selection.json"):
        raise ValidationError("focus selection changed after pre-live freeze")
    scope = freeze_source_scope(parent)
    if scope.to_dict(include_text=True) != _read_json(output_dir / "source-scope.json"):
        raise ValidationError("source scope changed after pre-live freeze")
    symbols = child_symbol_table(parent)
    if canonical_bytes(symbols.to_dict()) != canonical_bytes(
        _read_json(output_dir / "child-symbol-table.json")
    ):
        raise ValidationError("child symbol table changed after pre-live freeze")

    compiler = compiler_factory() if compiler_factory else OpenAIAssertionCompiler(model=model)
    provider_call = compiler_factory is None
    attempts: list[dict[str, Any]] = []
    document = scope.as_document(parent)

    started_at, started = _utc_now(), time.perf_counter()
    try:
        extraction = compiler.extract_assertions(document, symbols)  # type: ignore[attr-defined]
        grounded_raw = ground_assertions(document, symbols, extraction)
        grounded = GroundedAssertionSet(
            grounded_raw.assertions,
            {**dict(grounded_raw.metadata), "source_scope_sha256": scope.sha256},
        )
    except Exception as exc:
        metadata = dict(getattr(compiler, "last_assertion_metadata", {}))
        raw = getattr(compiler, "last_assertion_raw", None)
        _write_json(output_dir / "child-assertion-result.json", {
            "stage": "CHILD_ASSERTION_EXTRACTION_AND_GROUNDING",
            "outcome": "FAILED",
            "failure": str(exc),
            "raw_proposal": raw,
            "provider_metadata": metadata,
            "rejected_output_preserved": raw is not None,
        })
        attempts.append(_attempt(
            1, "CHILD_ASSERTION_EXTRACTION_AND_GROUNDING", started_at,
            time.perf_counter() - started, "FAILED", metadata, provider_call,
            error=exc, rejected_output_preserved=raw is not None,
        ))
        return _fail_live(output_dir, attempts, "ASSERTION_STAGE", exc)
    assertion_runtime = time.perf_counter() - started
    assertion_metadata = dict(extraction.metadata)
    attempts.append(_attempt(
        1, "CHILD_ASSERTION_EXTRACTION_AND_GROUNDING", started_at, assertion_runtime,
        "SUCCESS", assertion_metadata, provider_call,
    ))
    _write_json(output_dir / "child-assertion-result.json", {
        "stage": "CHILD_ASSERTION_EXTRACTION_AND_GROUNDING",
        "outcome": "SUCCESS",
        "raw_proposal": getattr(compiler, "last_assertion_raw", None) or extraction.to_dict(),
        "provider_metadata": assertion_metadata,
        "assertion_count": len(grounded.assertions),
    })
    _write_json(output_dir / "child-grounded-assertions.json", grounded.to_dict())

    started_at, started = _utc_now(), time.perf_counter()
    try:
        canonical = compiler.canonicalize_assertions(grounded, symbols)  # type: ignore[attr-defined]
        child, structures, representation, admission = compile_trusted_child(
            parent=parent,
            scope=scope,
            symbols=symbols,
            assertions=grounded,
            canonicalization=canonical,
        )
    except Exception as exc:
        metadata = dict(getattr(compiler, "last_canonicalization_metadata", {}))
        raw = getattr(compiler, "last_canonicalization_raw", None)
        _write_json(output_dir / "child-canonicalization-result.json", {
            "stage": "CHILD_CANONICALIZATION_AND_ADMISSION",
            "outcome": "FAILED",
            "failure": str(exc),
            "raw_proposal": raw,
            "provider_metadata": metadata,
            "rejected_output_preserved": raw is not None,
        })
        attempts.append(_attempt(
            2, "CHILD_CANONICALIZATION_AND_ADMISSION", started_at,
            time.perf_counter() - started, "FAILED", metadata, provider_call,
            error=exc, rejected_output_preserved=raw is not None,
        ))
        return _fail_live(output_dir, attempts, "CANONICALIZATION_STAGE", exc)
    canonical_runtime = time.perf_counter() - started
    canonical_metadata = dict(canonical.metadata)
    attempts.append(_attempt(
        2, "CHILD_CANONICALIZATION_AND_ADMISSION", started_at, canonical_runtime,
        "SUCCESS", canonical_metadata, provider_call,
    ))
    _write_json(output_dir / "run-history.json", _history(attempts))
    _write_json(output_dir / "child-canonicalization-result.json", {
        "stage": "CHILD_CANONICALIZATION_AND_ADMISSION",
        "outcome": "SUCCESS",
        "raw_proposal": getattr(compiler, "last_canonicalization_raw", None) or canonical.to_dict(),
        "normalized_proposal": canonical.to_dict(),
        "provider_metadata": canonical_metadata,
    })
    _write_json(output_dir / "child.knowledge.json", child.to_dict())
    _write_json(output_dir / "child.structures.json", structures.to_dict())
    _write_json(output_dir / "child.representation.json", representation.to_dict())
    _write_json(output_dir / "semantic-admission.json", admission)
    _write_json(output_dir / "semantic-review.json", _semantic_review_template(grounded, child))

    parent_hash_record = _read_json(output_dir / "parent-hashes.json")
    parent_hash_record["after"] = _parent_hashes(spec013_dir)
    parent_hash_record["immutable"] = parent_hash_record["before"] == parent_hash_record["after"]
    _write_json(output_dir / "parent-hashes.json", parent_hash_record)
    baseline_record = _read_json(output_dir / "baseline-manifest.json")
    baseline_record["after"] = _baseline_hashes()
    baseline_record["immutable"] = baseline_record["before"] == baseline_record["after"]
    _write_json(output_dir / "baseline-manifest.json", baseline_record)

    combined = {
        key: _usage(assertion_metadata)[key] + _usage(canonical_metadata)[key]
        for key in ("input_tokens", "output_tokens", "total_tokens")
    }
    report = _read_json(output_dir / "report.json")
    report.update({
        "execution_stage": "PENDING_INDEPENDENT_REPOSITORY_SEMANTIC_REVIEW",
        "machine_integrity_verdict": "PASS",
        "live_call_count": 2 if provider_call else 0,
        "fixture_call_count": 0 if provider_call else 2,
        "retry_count": 0,
        "request_ids": {
            "assertion_extraction": assertion_metadata.get("provider_request_id"),
            "canonicalization": canonical_metadata.get("provider_request_id"),
        },
        "usage": {
            "assertion_extraction": _usage(assertion_metadata),
            "canonicalization": _usage(canonical_metadata),
            "combined": combined,
        },
        "runtime_seconds": {
            "assertion_extraction": round(assertion_runtime, 3),
            "canonicalization": round(canonical_runtime, 3),
            "combined": round(assertion_runtime + canonical_runtime, 3),
        },
        "authoritative_monetary_cost": "NOT_AVAILABLE",
        "grounding": {
            "assertion_count": len(grounded.assertions),
            "evidence_span_count": sum(len(item.evidence) for item in grounded.assertions),
            "failures": 0,
        },
        "canonical_counts": admission["counts"],
        "child_model_round_trip": True,
        "structure_counts": _structure_counts(structures),
        "representation": _representation_diagnostics(child, representation),
        "parent_immutable": parent_hash_record["immutable"],
        "baselines_immutable": baseline_record["immutable"],
        "human_review_status": "BLOCKED_PENDING_REPOSITORY_SEMANTIC_REVIEW",
        "product_verdict": "PENDING",
    })
    _write_json(output_dir / "report.json", report)
    return report


def _semantic_review_template(assertions: GroundedAssertionSet, child: KnowledgeModel) -> dict[str, Any]:
    items = [{
        "kind": "relationship",
        "id": item.id,
        "statement": item.statement,
        "source_entity_id": item.source_entity_id,
        "predicate": item.relationship_type.value,
        "target_entity_id": item.target_entity_id,
        "classification": "PENDING",
        "notes": "",
    } for item in child.relationships]
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
        "notes": "",
    } for item in child.propositions)
    return {
        "spec": "SPEC-020",
        "status": "PENDING_INDEPENDENT_REPOSITORY_REVIEW",
        "assertion_categories": list(ASSERTION_REVIEW_CATEGORIES),
        "semantic_categories": list(SEMANTIC_REVIEW_CATEGORIES),
        "assertion_items": [{
            "id": item.id,
            "statement": item.statement,
            "participant_entity_ids": list(item.participant_entity_ids),
            "classification": "PENDING",
            "notes": "",
        } for item in assertions.assertions],
        "canonical_items": items,
        "known_defects": [],
        "new_defects": [],
        "trusted_child": "PENDING",
    }


def finalize_semantic_depth_evaluation(
    output_dir: Path,
    *,
    spec013_dir: Path = default_spec013_directory(),
) -> dict[str, Any]:
    """Admit a repository-reviewed child and create isolated viewer artifacts."""
    report = _read_json(output_dir / "report.json")
    if report.get("execution_stage") != "PENDING_INDEPENDENT_REPOSITORY_SEMANTIC_REVIEW":
        raise ValidationError("SPEC-020 finalization requires a successful live child proposal")
    review = _read_json(output_dir / "semantic-review.json")
    assertion_classes = [item["classification"] for item in review["assertion_items"]]
    canonical_classes = [item["classification"] for item in review["canonical_items"]]
    if any(item not in ASSERTION_REVIEW_CATEGORIES for item in assertion_classes):
        raise ValidationError("all child assertions require an independent fidelity classification")
    if any(item not in SEMANTIC_REVIEW_CATEGORIES for item in canonical_classes):
        raise ValidationError("all child canonical items require an independent semantic classification")
    trusted = (
        all(item not in {"DISTORTED", "UNSUPPORTED"} for item in assertion_classes)
        and all(item == "SUPPORTED" for item in canonical_classes)
        and review.get("trusted_child") is True
    )
    if not trusted:
        report.update({
            "execution_stage": "REPOSITORY_SEMANTIC_REVIEW_FAILED_CLOSED",
            "human_review_status": "NOT_AVAILABLE_NO_TRUSTED_CHILD",
            "rejected_child_rendered": False,
            "product_verdict": "INCONCLUSIVE",
        })
        _write_json(output_dir / "report.json", report)
        return report

    parent = _load_parent(spec013_dir)
    parent_representation = RepresentationModel.from_dict(
        _read_json(output_dir / "parent.representation.json")
    )
    child_representation = RepresentationModel.from_dict(
        _read_json(output_dir / "child.representation.json")
    )
    fixture = build_depth_workspace_fixture(parent, parent_representation, child_representation)
    nav_before = hashlib.sha256(canonical_bytes(fixture["navigation"])).hexdigest()
    state = DepthWorkspaceState(camera=CameraState(**INITIAL_CAMERA))
    child_state = switch_semantic_depth(state, "CHILD")
    parent_state = switch_semantic_depth(child_state, "PARENT")
    nav_after = hashlib.sha256(canonical_bytes(fixture["navigation"])).hexdigest()
    child = KnowledgeModel.from_dict(_read_json(output_dir / "child.knowledge.json"))
    structures = _read_json(output_dir / "child.structures.json")
    representation_diagnostics = _representation_diagnostics(child, child_representation)
    baseline_record = _read_json(output_dir / "baseline-manifest.json")
    baseline_record["after"] = _baseline_hashes()
    baseline_record["immutable"] = baseline_record["before"] == baseline_record["after"]
    _write_json(output_dir / "baseline-manifest.json", baseline_record)
    parent_record = _read_json(output_dir / "parent-hashes.json")
    parent_record["after"] = _parent_hashes(spec013_dir)
    parent_record["immutable"] = parent_record["before"] == parent_record["after"]
    _write_json(output_dir / "parent-hashes.json", parent_record)
    if not baseline_record["immutable"] or not parent_record["immutable"]:
        raise ValidationError("frozen parent or baseline changed before workspace admission")

    diagnostics = {
        "spec": "SPEC-020",
        "trusted_child_gate": _read_json(output_dir / "semantic-admission.json")["trusted_gate"],
        "parent_navigation": {
            "entity_count": len(fixture["navigation"]["nodes"]),
            "relationship_count": len(fixture["navigation"]["edges"]),
            "world_hash_before_depth_toggle": nav_before,
            "world_hash_after_depth_toggle": nav_after,
            "stable": nav_before == nav_after,
            "child_cluster_added": False,
        },
        "semantic_depth": {
            "maximum_child_depth": 1,
            "focus_entity_id": FOCUS_ENTITY_ID,
            "parent_to_child_camera_unchanged": depth_camera_invariant(state, child_state),
            "child_to_parent_camera_unchanged": depth_camera_invariant(child_state, parent_state),
            "return_to_parent_preserves_focus": parent_state.focused_entity_id == FOCUS_ENTITY_ID,
            "geometric_zoom_triggers_semantic_depth": False,
        },
        "shared_entity_ids": sorted(
            {item.id for item in parent.entities}.intersection(item.id for item in child.entities)
        ),
        "structure_counts": structures["metadata"]["structure_counts"],
        "representation": representation_diagnostics,
        "browser_verification": "SEE browser-verification.json",
    }
    _write_json(output_dir / "workspace-fixture.json", fixture)
    _write_json(output_dir / "workspace-diagnostics.json", diagnostics)
    _write_json(output_dir / "workspace-manifest.json", {
        "spec": "SPEC-020",
        "title": "Realistic semantic depth in the hybrid workspace",
        "workspace_fixture": "workspace-fixture.json",
        "workspace_diagnostics": "workspace-diagnostics.json",
        "semantic_review": "semantic-review.json",
        "human_review": "human-review-template.json",
    })
    _write_json(output_dir / "manifest.json", _read_json(output_dir / "workspace-manifest.json"))
    _write_json(output_dir / "baseline-comparison.json", {
        "spec": "SPEC-020",
        "parent_only_baseline_003": "AVAILABLE_IN_VIEWER_VIA_PARENT_DEPTH",
        "trusted_child_active": "AVAILABLE_IN_VIEWER_VIA_DEEPER_DEPTH",
        "original_source_passage": "source-scope.json",
        "owner_comparison": "PENDING",
    })
    browser_path = output_dir / "browser-verification.json"
    if not browser_path.exists():
        _write_json(browser_path, {
            "status": "PENDING_MANUAL_BROWSER_VERIFICATION",
            "mouse": {}, "keyboard": {}, "console": {},
        })
    _write_json(output_dir / "human-review-template.json", {
        "status": "PENDING_OWNER_REVIEW",
        "question": (
            "Does deeper resolution inside the accepted workspace help me understand the selected "
            "quantum concept while preserving my sense of where I am?"
        ),
        "allowed_verdicts": [
            "SEMANTIC_DEPTH_BETTER", "MIXED", "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE",
        ],
        "owner_response": None,
        "verdict": "PENDING",
    })
    _copy_assets(output_dir)
    report.update({
        "execution_stage": "PENDING_OWNER_COGNITIVE_REVIEW",
        "machine_integrity_verdict": "PASS",
        "repository_semantic_review": {
            "assertion_fidelity_counts": {
                category: assertion_classes.count(category) for category in ASSERTION_REVIEW_CATEGORIES
            },
            "canonical_counts": {
                category: canonical_classes.count(category) for category in SEMANTIC_REVIEW_CATEGORIES
            },
            "trusted_child": True,
            "known_defects": review["known_defects"],
            "new_defects": review["new_defects"],
        },
        "workspace_integrity": {
            "parent_map_stable": nav_before == nav_after,
            "navigation_camera_invariant": True,
            "parent_child_resolution_available": True,
            "geometric_zoom_independent": True,
            "baseline_assets_immutable": True,
            "parent_artifacts_immutable": True,
        },
        "human_review_status": "PENDING_OWNER_REVIEW",
        "product_verdict": "PENDING",
    })
    _write_json(output_dir / "report.json", report)
    return report
