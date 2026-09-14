"""Frozen live-execution harness for SPEC-048.

This module does not alter Candidate B.  It verifies the complete SPEC-047
freeze, executes each authorized source once through the frozen adapter, and
persists auditable per-stage evidence and the historical-control comparison.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from .blind_evaluation import BlindSource, BlindSourcePacket
from .decomposed_ab_evaluation import (
    build_ab_comparison,
    candidate_comparison_record,
    load_historical_control_records,
)
from .decomposed_extraction import (
    CANDIDATE_B_VERSION,
    CandidateBRun,
    GateStatus,
    StageName,
    run_candidate_b,
    stable_hash,
)
from .depth_interaction_evaluation import directory_identity
from .openai_decomposed_extractor import (
    MODEL,
    OpenAIDecomposedExtractor,
    frozen_stage_contracts,
)
from .semantic_representation_compiler import compile_semantic_representation
from .structure_detection import StructureDetector


EVALUATION_VERSION = "spec-048-live-ab-v1"
OUTPUT_DIRECTORY = (
    "examples/evaluations/"
    "spec-048-decomposed-extraction-live-ab-execution-20260913"
)
SPEC047_DIRECTORY = (
    "examples/evaluations/"
    "spec-047-decomposed-extraction-ab-harness-20260913"
)
PACKET_PATHS = (
    "examples/evaluations/spec-041-blind-source-set-freeze-20260911/"
    "blind-source-packet.json",
    "examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/"
    "blind-source-packet.json",
)
EXPECTED_PACKET_HASHES = (
    "ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0",
    "85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b",
)
EXPECTED_SOURCES = (
    ("usgs-divergent-plate-boundaries-1996", "a9539d135ff1577d7e2791d498b92f55239175565b925b24aec2ed0bf633f186"),
    ("noaa-nesdis-jet-stream-2025", "256ade61be620cfaa7b1327e3c982576611dd29b6a1fb42217d86ffdc0783ca1"),
    ("crs-legislative-process-r42843-17", "fe61b7c3b2a9373e7eb3b30d16b94adc2c8b5f4307327265943995550a6384b4"),
    ("nasa-solar-system-formation-2026", "c0cb2519673b8f3ef23c0be2856e03790f53d44971cbff09d593190ab3fa155d"),
    ("epa-ecological-processes-2026", "70e7e3d20325dd5d22e9cf4484934419447907ba9f6cf5a4dfd65ddcbfa80ad5"),
    ("doe-iron-platinum-atomic-structure-2017", "e9d2260c9980239431fc195e7dc687afea93598af4f28d774ed5e4c4317f9e1e"),
    ("nhgri-dna-fact-sheet-2020", "54e2147221cf186fe1b4f965422c69e815f986a7d009eddae9c01bf32ec25f89"),
    ("fhwa-traffic-bottleneck-concepts-2016", "1fd7e9851839f5f35cd2a231cd3ce5aea8196ec85cabd04694f681c063ea4345"),
    ("nist-measurement-uncertainty-2025", "b3ae508f3982dfdd89f41a1d9ca59eb1f658b1648e3fae35168feba212046730"),
)
EXPECTED_CANDIDATE_HASHES = {
    "src/knowledge_compiler/decomposed_extraction.py": "a09bb36a2214364f915b05e0f7818ffe0b145760b76afb1f00fc66ed09dc75ea",
    "src/knowledge_compiler/openai_decomposed_extractor.py": "2d91a2fdfcf04bcc2180331571e3d7c2a20e797fe9fbc83c046aafdad1764280",
    "src/knowledge_compiler/decomposed_ab_evaluation.py": "85e60376aabc797e75bafbda71df3ec2a68d24f0220f931b2eb89f0d9b9824fc",
}
EXPECTED_STAGE_CONTRACT_HASH = (
    "b13c96ac01b2f0730f57852078c702f01a2234bca1f7567654686d214c50f694"
)
EXPECTED_SPEC047_IDENTITY = {
    "file_count": 7,
    "aggregate_sha256": "5f516effcedc8acd2c3ee29a6bba929a75572d9049d4d0126ae44b32b84306fc",
}
EXPECTED_REPRESENTATION_COMPILER_HASH = (
    "84dbfe048da4b27ecdad2139bd2db3c1a9ef1be56676496bc9fc18974dea107a"
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _check(checks: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    passed = actual == expected
    checks.append(
        {"check": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected}
    )
    if not passed:
        raise RuntimeError(f"SPEC-048 preflight failed: {name}")


def load_frozen_sources(repo_root: Path) -> tuple[BlindSource, ...]:
    sources: list[BlindSource] = []
    for path in PACKET_PATHS:
        sources.extend(BlindSourcePacket.from_path(repo_root / path).sources)
    actual = tuple((item.source_id, item.source_sha256) for item in sources)
    if actual != EXPECTED_SOURCES:
        raise RuntimeError("SPEC-048 frozen source identity/order mismatch")
    return tuple(sources)


def build_preflight(repo_root: Path, *, require_api_key: bool = True) -> dict[str, Any]:
    """Validate every frozen identity before provider transmission."""

    checks: list[dict[str, Any]] = []
    for path, expected in EXPECTED_CANDIDATE_HASHES.items():
        _check(checks, f"candidate file {path}", _sha(repo_root / path), expected)

    frozen_contract = _load(repo_root / SPEC047_DIRECTORY / "candidate-b-contract.json")
    _check(checks, "stage contract artifact/runtime equality", frozen_stage_contracts(), frozen_contract)
    _check(checks, "stage contract SHA-256", stable_hash(frozen_contract), EXPECTED_STAGE_CONTRACT_HASH)

    for path, expected in zip(PACKET_PATHS, EXPECTED_PACKET_HASHES, strict=True):
        _check(checks, f"source packet {path}", _sha(repo_root / path), expected)
    sources = load_frozen_sources(repo_root)
    _check(
        checks,
        "nine source identities and fixed order",
        [[item.source_id, item.source_sha256] for item in sources],
        [list(item) for item in EXPECTED_SOURCES],
    )

    manifest = _load(repo_root / SPEC047_DIRECTORY / "proposed-live-execution-manifest.json")
    _check(
        checks,
        "SPEC-047 manifest source order",
        [[item["source_id"], item["source_sha256"]] for item in manifest["fixed_source_order"]],
        [list(item) for item in EXPECTED_SOURCES],
    )
    controls = manifest["candidate_b"]
    for name, expected in {
        "model": "gpt-5.6-luna",
        "store": False,
        "sdk_retries": 0,
        "hidden_retries": 0,
        "semantic_retries": 0,
        "repair_calls": 0,
        "follow_up_calls_outside_defined_stages": 0,
        "external_enrichment": 0,
        "prompt_adaptation_between_sources": 0,
        "implementation_adaptation_after_execution_begins": 0,
        "maximum_total_calls": 27,
    }.items():
        _check(checks, f"execution control {name}", controls[name], expected)
    _check(checks, "runtime model", MODEL, "gpt-5.6-luna")

    hashes = _load(repo_root / SPEC047_DIRECTORY / "implementation-hashes.json")
    for group in ("control_a_files", "canonical_validator_files"):
        for item in hashes[group]:
            _check(checks, f"protected {item['path']}", _sha(repo_root / item["path"]), item["sha256"])
    _check(
        checks,
        "representation compiler",
        _sha(repo_root / "src/knowledge_compiler/semantic_representation_compiler.py"),
        EXPECTED_REPRESENTATION_COMPILER_HASH,
    )
    identity = directory_identity(repo_root / SPEC047_DIRECTORY)
    _check(
        checks,
        "SPEC-047 directory identity",
        {"file_count": identity["file_count"], "aggregate_sha256": identity["aggregate_sha256"]},
        EXPECTED_SPEC047_IDENTITY,
    )
    protected = _load(repo_root / SPEC047_DIRECTORY / "report.json")["protected_evidence_identity"]
    protected_actual = {
        "spec038": {
            key: value
            for key, value in directory_identity(
                repo_root / "examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-20260909"
            ).items()
            if key in {"file_count", "aggregate_sha256"}
        },
        "spec041_packet_sha256": _sha(repo_root / PACKET_PATHS[0]),
        "spec041_live_manifest_sha256": _sha(
            repo_root / "examples/evaluations/spec-041-blind-source-set-freeze-20260911/live-execution-manifest.json"
        ),
        "spec042": {
            key: value
            for key, value in directory_identity(
                repo_root / "examples/evaluations/spec-042-blind-out-of-sample-live-execution-20260911"
            ).items()
            if key in {"file_count", "aggregate_sha256"}
        },
        "spec043_report_sha256": _sha(
            repo_root / "examples/evaluations/spec-043-blind-failure-diagnosis-20260911/report.json"
        ),
        "spec044_packet_sha256": _sha(repo_root / PACKET_PATHS[1]),
        "spec044_live_manifest_sha256": _sha(
            repo_root / "examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/live-execution-manifest.json"
        ),
        "spec045": {
            key: value
            for key, value in directory_identity(
                repo_root / "examples/evaluations/spec-045-blind-replication-live-execution-20260912"
            ).items()
            if key in {"file_count", "aggregate_sha256"}
        },
        "spec046_report_sha256": _sha(
            repo_root / "examples/evaluations/spec-046-extraction-reliability-failure-mode-analysis-20260913/report.json"
        ),
    }
    _check(checks, "SPEC-038 through SPEC-046 evidence", protected_actual, protected)

    key_present = bool(os.environ.get("OPENAI_API_KEY"))
    if require_api_key:
        _check(checks, "OPENAI_API_KEY present", key_present, True)
    return {
        "schema": "spec-048-preflight-v1",
        "status": "PASS",
        "candidate_version": CANDIDATE_B_VERSION,
        "checks": checks,
        "source_count": len(sources),
        "provider": "OpenAI Responses API",
        "model": MODEL,
        "store": False,
        "maximum_calls": 27,
        "all_retry_classes": 0,
        "external_retrievals": 0,
        "control_a_reruns": 0,
    }


def _stage_directory(source_dir: Path, index: int, stage: StageName) -> Path:
    return source_dir / "stages" / f"{index:02d}-{stage.value.casefold().replace('_', '-')}"


def persist_source_run(source_dir: Path, source: BlindSource, run: CandidateBRun) -> dict[str, Any]:
    """Persist every proposal, raw response, gate, and request ledger entry."""

    _write(source_dir / "source-identity.json", {
        "source_id": source.source_id,
        "source_sha256": source.source_sha256,
        "title": source.title,
        "provenance": source.provenance,
    })
    attempts = {item.stage: item for item in run.attempts}
    entries = {
        StageName(item["stage"]): item
        for item in run.provider_call_ledger.get("entries", [])
    }
    gates = {item.stage: item for item in (*run.stage_gates, run.canonical_gate)}
    for index, stage in enumerate(
        (
            StageName.ENTITY_INVENTORY,
            StageName.SEMANTIC_STRUCTURE,
            StageName.CLAIM_EVIDENCE_BINDING,
            StageName.CANONICAL_VALIDATION,
        ),
        start=1,
    ):
        stage_dir = _stage_directory(source_dir, index, stage)
        _write(stage_dir / "gate.json", gates[stage].to_dict())
        _write(stage_dir / "execution.json", {
            "stage": stage.value,
            "ran": gates[stage].status is not GateStatus.NOT_RUN_UPSTREAM_FAILURE,
            "downstream_stages_ran": [
                later.value
                for later in list(gates)[index:]
                if gates[later].status is not GateStatus.NOT_RUN_UPSTREAM_FAILURE
            ],
        })
        if stage in attempts:
            attempt = attempts[stage]
            _write(stage_dir / "parsed-proposal.json", attempt.raw_proposal)
            _write(stage_dir / "provider-metadata.json", attempt.provider_metadata)
            _write(stage_dir / "raw-provider-response.json", attempt.raw_provider_response)
        if stage in entries:
            _write(stage_dir / "request-ledger-entry.json", entries[stage])

    _write(source_dir / "candidate-run.json", run.to_dict())
    record = candidate_comparison_record(run)
    structures: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    if run.model is not None:
        _write(source_dir / "admitted-knowledge-model.json", run.model.to_dict())
        structures = StructureDetector().detect(run.model).to_dict()["structures"]
        foci = [
            *(("concept", item.id) for item in run.model.entities),
            *(("canonical", item.id) for item in run.model.relationships),
            *(("proposition", item.id) for item in run.model.propositions),
        ]
        decisions = [
            compile_semantic_representation(run.model, kind, identity).to_dict()
            for kind, identity in sorted(foci)
        ]
    _write(source_dir / "detected-structures.json", {"structures": structures})
    _write(source_dir / "representation-decisions.json", {"decisions": decisions})
    failed = next(
        (
            item
            for item in (*run.stage_gates, run.canonical_gate)
            if item.status is GateStatus.FAIL_CLOSED
        ),
        None,
    )
    outcome = {
        **record,
        "detection_stage": failed.stage.value if failed else None,
        "exact_failure": failed.exact_failure if failed else None,
        "error_type": failed.error_type if failed else None,
    }
    _write(source_dir / "final-outcome.json", outcome)
    return outcome


def _richness_differences(
    control: Sequence[Mapping[str, Any]], candidate: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    by_control = {item["source_id"]: item for item in control}
    rows = []
    for item in candidate:
        prior = by_control[item["source_id"]]
        count_delta = {}
        for key in ("entities", "relationships", "propositions", "claims"):
            left = prior["admitted_counts"][key] if prior["admitted_counts"] else None
            right = item["admitted_counts"][key] if item["admitted_counts"] else None
            count_delta[key] = None if left is None or right is None else right - left
        rows.append({
            "source_id": item["source_id"],
            "control_status": prior["status"],
            "candidate_status": item["status"],
            "admitted_count_delta_candidate_minus_control": count_delta,
            "detected_structure_count_delta": (
                item["detected_structure_count"] - prior["detected_structure_count"]
                if item["status"] == prior["status"] == "PASS" else None
            ),
            "sufficient_representation_decision_delta": (
                item["sufficient_representation_decision_count"]
                - prior["sufficient_representation_decision_count"]
                if item["status"] == prior["status"] == "PASS" else None
            ),
        })
    return rows


def mechanically_supported_branch(comparison: Mapping[str, Any]) -> str:
    control = comparison["arm_summaries"]["CONTROL_A"]
    candidate = comparison["arm_summaries"]["CANDIDATE_B"]
    if candidate["known_invalid_objects_admitted"]:
        return "B_REGRESSION"
    delta = candidate["admitted_sources"] - control["admitted_sources"]
    if delta < 0:
        return "B_REGRESSION"
    if delta == 0:
        return "B_NO_MATERIAL_GAIN"
    if delta == 1:
        return "INCONCLUSIVE"
    control_semantics = sum(control["admitted_semantic_totals"].values()) / max(
        control["admitted_sources"], 1
    )
    candidate_semantics = sum(candidate["admitted_semantic_totals"].values()) / max(
        candidate["admitted_sources"], 1
    )
    if candidate_semantics < control_semantics * 0.5:
        return "B_SAFER_BUT_TOO_SPARSE"
    return "B_CLEAR_IMPROVEMENT"


def validate_execution(
    sources: Sequence[BlindSource], runs: Sequence[CandidateBRun]
) -> dict[str, Any]:
    if tuple((item.source_id, item.source_sha256) for item in sources) != EXPECTED_SOURCES:
        raise RuntimeError("executed source order changed")
    if len(runs) != 9:
        raise RuntimeError("execution did not preserve nine source outcomes")
    all_entries = []
    for source, run in zip(sources, runs, strict=True):
        if (run.source_id, run.source_sha256) != (source.source_id, source.source_sha256):
            raise RuntimeError(f"run identity mismatch for {source.source_id}")
        entries = list(run.provider_call_ledger.get("entries", []))
        all_entries.extend({**item, "source_ordinal": len(all_entries) + 1} for item in entries)
        if len(entries) > 3 or len({item["stage"] for item in entries}) != len(entries):
            raise RuntimeError(f"per-stage call ceiling violated for {source.source_id}")
        expected_called = [
            gate.stage.value
            for gate in run.stage_gates
            if gate.status is not GateStatus.NOT_RUN_UPSTREAM_FAILURE
        ]
        if [item["stage"] for item in entries] != expected_called:
            raise RuntimeError(f"stage order/accounting mismatch for {source.source_id}")
        for item in entries:
            if any(item.get(key) != 0 for key in (
                "sdk_retries", "hidden_retries", "semantic_retries", "repair_calls"
            )) or item.get("store") is not False:
                raise RuntimeError(f"execution-control violation for {source.source_id}")
    if len(all_entries) > 27:
        raise RuntimeError("global 27-call ceiling exceeded")
    return {
        "status": "PASS",
        "source_count": len(runs),
        "provider_calls": len(all_entries),
        "one_call_per_stage_per_source": True,
        "short_circuiting": True,
        "fixed_order": True,
        "request_start_accounting": True,
        "store": False,
        "all_retry_classes": 0,
        "repairs": 0,
        "follow_up_calls": 0,
    }


def run_live_evaluation(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    """Execute exactly the authorized Candidate-B arm once."""

    if output_dir.exists():
        raise RuntimeError("SPEC-048 output directory already exists; refusing any rerun")
    preflight = build_preflight(repo_root, require_api_key=True)
    sources = load_frozen_sources(repo_root)
    output_dir.mkdir(parents=True)
    _write(output_dir / "preflight.json", preflight)
    runs: list[CandidateBRun] = []
    outcomes: list[dict[str, Any]] = []
    global_entries: list[dict[str, Any]] = []
    for index, source in enumerate(sources, start=1):
        adapter = OpenAIDecomposedExtractor(model=MODEL)
        run = run_candidate_b(
            source.text,
            adapter,
            source_metadata={
                "source_id": source.source_id,
                "title": source.title,
                "provenance": source.provenance,
            },
            allow_live=True,
        )
        runs.append(run)
        source_dir = output_dir / "sources" / f"{index:02d}-{source.source_id}"
        outcomes.append(persist_source_run(source_dir, source, run))
        for entry in run.provider_call_ledger.get("entries", []):
            global_entries.append({
                **entry,
                "global_call_ordinal": len(global_entries) + 1,
                "source_ordinal": index,
            })
        _write(output_dir / "provider-call-ledger.json", {
            "candidate_version": CANDIDATE_B_VERSION,
            "calls_started": len(global_entries),
            "entries": global_entries,
        })
        _write(output_dir / "run-progress.json", {
            "completed_source_count": len(runs),
            "completed_source_ids": [item.source_id for item in sources[:len(runs)]],
            "provider_calls_started": len(global_entries),
            "no_retry_or_repair": True,
        })

    validation = validate_execution(sources, runs)
    controls = load_historical_control_records(repo_root)
    candidate_records = [candidate_comparison_record(run) for run in runs]
    comparison = build_ab_comparison(controls, candidate_records)
    branch = mechanically_supported_branch(comparison)
    comparison["semantic_richness_source_differences"] = _richness_differences(
        controls, candidate_records
    )
    comparison["mechanically_supported_branch"] = branch
    comparison["owner_verdict"] = "PENDING"
    _write(output_dir / "candidate-b-comparison-records.json", {
        "schema": "spec-048-candidate-b-comparison-records-v1",
        "records": candidate_records,
    })
    _write(output_dir / "ab-comparison.json", comparison)
    _write(output_dir / "validation.json", validation)
    status_counts = Counter(item["status"] for item in outcomes)
    report = {
        "schema": "spec-048-report-v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "evaluation_version": EVALUATION_VERSION,
        "candidate_version": CANDIDATE_B_VERSION,
        "source_outcomes": outcomes,
        "candidate_status_counts": dict(sorted(status_counts.items())),
        "control_a_summary": comparison["arm_summaries"]["CONTROL_A"],
        "candidate_b_summary": comparison["arm_summaries"]["CANDIDATE_B"],
        "semantic_richness_source_differences": comparison[
            "semantic_richness_source_differences"
        ],
        "mechanically_supported_branch": branch,
        "owner_verdict": "PENDING",
        "historical_control_caveat": (
            "Control A is historical rather than contemporaneous; marginal differences "
            "must not be interpreted as strong causal evidence."
        ),
        "execution_validation": validation,
        "preflight": preflight,
        "deviations": [],
        "owner_review": {
            "state": "OWNER_REVIEW",
            "promotion": "NOT_AUTHORIZED",
            "question": (
                "Does decomposed extraction materially improve trustworthy admission "
                "and failure isolation enough to justify its added call, token, latency, "
                "and architecture cost?"
            ),
        },
    }
    _write(output_dir / "report.json", report)
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    output = args.output_dir.resolve() if args.output_dir else root / OUTPUT_DIRECTORY
    run_live_evaluation(root, output)
