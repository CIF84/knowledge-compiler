"""SPEC-052 one-shot evaluation of the byte-frozen Candidate B v2.

This harness changes no extraction, semantic, or representation behavior. It
refuses provider transmission unless every frozen identity and control passes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from .decomposed_ab_evaluation import (
    candidate_comparison_record,
    load_historical_control_records,
    summarize_arm,
)
from .decomposed_extraction import GateStatus, StageName, stable_hash
from .decomposed_extraction_v2 import CANDIDATE_B_V2_VERSION, CandidateBV2Run, run_candidate_b_v2
from .openai_decomposed_extractor_v2 import (
    OpenAICandidateBV2Extractor,
    ProviderCallLedgerV2,
    frozen_v2_stage_contracts,
    stage2_v2_schema,
)
from .openai_decomposed_extractor import claim_evidence_schema, entity_inventory_schema
from .spec051_offline_evaluation import _template_inventory
from .spec048_live_evaluation import (
    EXPECTED_SOURCES,
    PACKET_PATHS,
    build_preflight as historical_preflight,
    load_frozen_sources,
    persist_source_run,
)


OUTPUT_DIRECTORY = "examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915"
SPEC051_DIRECTORY = "examples/evaluations/spec-051-schema-constrained-candidate-b-v2-20260915"
SPEC048_DIRECTORY = "examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913"
CONTRACT_SHA256 = "6a149b1d3bac5789652de77af2630ffea84893413e892f4606df3c718e48d148"
SPEC051_REPORT_SHA256 = "2d55ca7a54624bffeff1c17f283740d0f78c759d1c744b0b2cde951cf5d069e4"
EXPECTED_V2_FILES = {
    "src/knowledge_compiler/decomposed_extraction_v2.py": "0d6676676fa69aaf55d3b3f974bbbbaf02d1f30d0568e9df071805bcbe4a688b",
    "src/knowledge_compiler/openai_decomposed_extractor_v2.py": "c6b30749be659006cf69fa451ee5d287d52f7e30b20e232755be0231bc31edbb",
    "src/knowledge_compiler/spec051_offline_evaluation.py": "144fa68607a64277a112301e9cba19e6377a5ab4cf7831c26719ca414b6457af",
}
EXPECTED_STAGE_HASHES = (
    ("ENTITY_INVENTORY", "spec-047-entity-inventory-v1", "b1c00eb4547de56c62dcc18c7aec013ee1e2de4a8c1dfa45bcb475f00591f785", "003db7546ae3ffafe7dc098bc50e1a5f223b891f6ee3160f7537214c8e9c9956"),
    ("SEMANTIC_STRUCTURE", "spec-051-semantic-structure-v2", "72e6b878794ac2fa45404970e2f0a931dc4c1c2efc97f64a4c7aed0ecf212299", "b9c5861354e3423f8712778048efd451b81bc52178ef798219b52e56b94d5560"),
    ("CLAIM_EVIDENCE_BINDING", "spec-051-claim-evidence-binding-v2", "a450efcc629ab3a28bb1357f5139dc343e62c4cf9772a497e7b7f1c65dedd97f", "bd8957cc40b49c7482767fb1cbbfec958ae924ad89ded740aeaa18c168e699de"),
)
ORIGIN_TAXONOMY = frozenset({
    "ENTITY_INVENTORY", "RELATIONSHIP_SEMANTICS", "PROPOSITION_CONSTRUCTION",
    "EVIDENCE_FIDELITY", "CROSS_REFERENCE_CONSISTENCY", "GROUNDING_RESOLUTION",
    "CANONICAL_VALIDATION", "OTHER",
})


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _check(checks: list[dict[str, Any]], name: str, actual: Any, expected: Any) -> None:
    passed = actual == expected
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})
    if not passed:
        raise RuntimeError(f"SPEC-052 preflight failed: {name}")


def build_preflight(repo_root: Path, *, require_api_key: bool = True) -> dict[str, Any]:
    """Fail before transmission on source, candidate, historical or trust drift."""
    checks: list[dict[str, Any]] = []
    for path, expected in EXPECTED_V2_FILES.items():
        _check(checks, f"frozen Candidate B v2 {path}", _sha(repo_root / path), expected)
    _check(checks, "SPEC-051 frozen report", _sha(repo_root / SPEC051_DIRECTORY / "report.json"), SPEC051_REPORT_SHA256)
    report = _load(repo_root / SPEC051_DIRECTORY / "report.json")
    contract = _load(repo_root / SPEC051_DIRECTORY / "candidate-b-v2-contract.json")
    runtime_contract = frozen_v2_stage_contracts(_template_inventory())
    _check(checks, "frozen v2 contract equals runtime", runtime_contract, contract)
    _check(checks, "frozen v2 contract identity", stable_hash(contract), CONTRACT_SHA256)
    _check(checks, "frozen version", contract["candidate_version"], CANDIDATE_B_V2_VERSION)
    for stage, expected in zip(contract["stages"], EXPECTED_STAGE_HASHES, strict=True):
        _check(checks, f"{expected[0]} stage/prompt/schema identity", (
            stage["stage"], stage["prompt_version"], stage["prompt_sha256"], stage["schema_sha256"]
        ), expected)
    for identity in report["protected_identities"]:
        _check(checks, f"protected {identity['path']}", _sha(repo_root / identity["path"]), identity["sha256"])
    old = historical_preflight(repo_root, require_api_key=False)
    _check(checks, "historical Control A, B v1, source and canonical preflight", old["status"], "PASS")
    manifest = _load(repo_root / SPEC051_DIRECTORY / "future-live-manifest.json")
    _check(checks, "future manifest source identities/order", tuple(
        (item["source_id"], item["source_sha256"]) for item in manifest["sources"]
    ), EXPECTED_SOURCES)
    _check(checks, "packet hashes", tuple(_sha(repo_root / path) for path in PACKET_PATHS), tuple(
        item["sha256"] for item in manifest["source_packets"]
    ))
    _check(checks, "v2 model/storage/call/retry controls", (
        manifest["model"], manifest["store"], manifest["maximum_total_provider_calls"],
        manifest["sdk_retries"], manifest["hidden_retries"], manifest["semantic_retries"],
        manifest["repair_calls"], manifest["prompt_or_schema_adaptation"],
        manifest["external_enrichment"], manifest["upstream_failure_short_circuit"],
    ), ("gpt-5.6-luna", False, 27, 0, 0, 0, 0, 0, 0, True))
    _check(checks, "production instructions contain no historical source names", any(
        source_id.casefold() in stage["instructions"].casefold()
        for stage in contract["stages"] for source_id, _ in EXPECTED_SOURCES
    ), False)
    _check(checks, "OpenAI SDK installed", importlib.util.find_spec("openai") is not None, True)
    if require_api_key:
        _check(checks, "OPENAI_API_KEY available", bool(os.environ.get("OPENAI_API_KEY")), True)
    return {
        "schema": "spec-052-preflight-v1", "status": "PASS", "candidate_version": CANDIDATE_B_V2_VERSION,
        "contract_sha256": CONTRACT_SHA256, "checks": checks, "historical_preflight": old,
        "source_count": 9, "model": "gpt-5.6-luna", "store": False,
        "maximum_provider_calls": 27, "retry_classes": 0,
    }


class DurableLedger(ProviderCallLedgerV2):
    """Persist request-start accounting even if a source run is interrupted."""

    def __init__(self, path: Path, source_id: str) -> None:
        super().__init__()
        self.path = path
        self.source_id = source_id

    def _flush(self) -> None:
        _write(self.path, {"source_id": self.source_id, **self.to_dict()})

    def begin(self, **kwargs: Any) -> dict[str, Any]:
        entry = super().begin(**kwargs)
        self._flush()
        return entry

    def complete(self, entry: dict[str, Any], **values: Any) -> None:
        super().complete(entry, **values)
        self._flush()

    def fail(self, entry: dict[str, Any], exc: Exception, duration_ms: float) -> None:
        super().fail(entry, exc, duration_ms)
        self._flush()


def _origin(stage: StageName, failure: str | None) -> str:
    if stage is StageName.ENTITY_INVENTORY:
        return "ENTITY_INVENTORY"
    text = (failure or "").casefold()
    if stage is StageName.CANONICAL_VALIDATION:
        return "CANONICAL_VALIDATION"
    if stage is StageName.CLAIM_EVIDENCE_BINDING:
        return "EVIDENCE_FIDELITY" if any(word in text for word in ("evidence", "quote", "claim")) else "GROUNDING_RESOLUTION"
    if any(word in text for word in ("frozen", "unknown", "undeclared", "identity", "entity id")):
        return "CROSS_REFERENCE_CONSISTENCY"
    if any(word in text for word in ("proposition", "comparison", "transfer", "operand", "role")):
        return "PROPOSITION_CONSTRUCTION"
    if any(word in text for word in ("relationship", "predicate", "direction")):
        return "RELATIONSHIP_SEMANTICS"
    return "OTHER"


def semantic_omission_audit(source_text: str, run: CandidateBV2Run) -> dict[str, Any]:
    """Inspect Stage-3 claims without interpreting paraphrase as semantic equality."""
    stage3 = next((item for item in run.attempts if item.stage is StageName.CLAIM_EVIDENCE_BINDING), None)
    if stage3 is None:
        ran = run.stage_gates[2].status is not GateStatus.NOT_RUN_UPSTREAM_FAILURE
        return {"stage3_ran": ran, "parsed_response_available": False,
                "reason": "REQUEST_FAILED_OR_NO_PARSED_RESPONSE" if ran else "UPSTREAM_SHORT_CIRCUIT",
                "claims": [], "claim_only_by_exact_statement_and_distinct_id_count": 0,
                "unintended_topology_count_if_admitted": None}
    proposal = stage3.raw_proposal
    claims = proposal.get("claims", []) if isinstance(proposal, Mapping) else []
    if not isinstance(claims, list):
        claims = []
    topology = run.structure
    topology_ids = {item["id"] for item in topology.relationships} | {item["id"] for item in topology.propositions} if topology else set()
    topology_statements = {item["statement"] for item in topology.relationships} | {item["statement"] for item in topology.propositions} if topology else set()
    admitted = {item.id: item for item in run.model.claims} if run.model else {}
    rows = []
    for item in claims:
        if not isinstance(item, Mapping):
            rows.append({"raw_item": item, "parsed_as_claim": False})
            continue
        spans = item.get("evidence", [])
        quotes = [span.get("quote") for span in spans if isinstance(span, Mapping)] if isinstance(spans, list) else []
        origin = item.get("origin")
        exact = (bool(quotes) and all(isinstance(quote, str) and source_text.count(quote) == 1 for quote in quotes)) if origin == "SOURCE" else not quotes if origin == "INFERRED" else False
        claim_id = item.get("id")
        statement = item.get("statement")
        rows.append({
            "claim_id": claim_id, "statement": statement, "origin": origin,
            "grounding_policy_satisfied_mechanically": exact, "exact_unique_source_quotes": exact if origin == "SOURCE" else None, "quotes": quotes,
            "not_identical_to_stage2_topology_statement": statement not in topology_statements,
            "not_a_stage2_topology_id": claim_id not in topology_ids,
            "admitted_in_knowledge_model": claim_id in admitted,
            "admitted_evidence_exact": bool(claim_id in admitted and all(source_text.count(span.quote) == 1 for span in admitted[claim_id].evidence)),
        })
    if run.model and topology:
        model_relationship_ids = {item.id for item in run.model.relationships}
        model_proposition_ids = {item.id for item in run.model.propositions}
        frozen_relationship_ids = {item["id"] for item in topology.relationships}
        frozen_proposition_ids = {item["id"] for item in topology.propositions}
        unintended_topology = len(model_relationship_ids ^ frozen_relationship_ids) + len(model_proposition_ids ^ frozen_proposition_ids)
    else:
        unintended_topology = None
    return {
        "stage3_ran": True, "parsed_response_available": True, "stage3_gate_status": run.stage_gates[2].status.value,
        "claims": rows,
        "claim_only_by_exact_statement_and_distinct_id_count": sum(
            row.get("not_identical_to_stage2_topology_statement", False) and row.get("not_a_stage2_topology_id", False)
            for row in rows
        ),
        "semantic_overlap_limitation": "Exact statement/ID audit is mechanical; paraphrased semantic overlap is not judged automatically.",
        "unintended_topology_count_if_admitted": unintended_topology,
        "structure_detection_consumes_claims": False,
        "assertion_aware_projection": "NOT_AUTOMATICALLY_RUN: existing builder requires a separately admitted grounded-assertion packet; claims remain in KnowledgeModel without minting assertion input",
        "existing_explanatory_representation": "Representation decisions are compiled from admitted canonical foci; claim-only material is not promoted into topology or assumed to be rendered.",
    }


def _stage_version(stage: StageName) -> str:
    return {
        StageName.SEMANTIC_STRUCTURE: "spec-051-semantic-structure-v2",
        StageName.CLAIM_EVIDENCE_BINDING: "spec-051-claim-evidence-binding-v2",
    }.get(stage, "spec-047-entity-inventory-v1" if stage is StageName.ENTITY_INVENTORY else "canonical-knowledge-model-v1")


def persist_v2_source(source_dir: Path, source: Any, run: CandidateBV2Run) -> dict[str, Any]:
    """Reuse frozen v1 evidence writer, then record original v2 Stage-2 proposal."""
    outcome = persist_source_run(source_dir, source, run)
    for index, gate in enumerate(run.stage_gates, start=1):
        gate_path = source_dir / "stages" / f"{index:02d}-{gate.stage.value.casefold().replace('_', '-')}" / "gate.json"
        value = _load(gate_path)
        value["stage_version"] = _stage_version(gate.stage)
        _write(gate_path, value)
    for attempt in run.attempts:
        if attempt.stage is not StageName.SEMANTIC_STRUCTURE:
            continue
        stage_dir = source_dir / "stages" / "02-semantic-structure"
        original = attempt.provider_metadata.get("original_stage2_proposal")
        if original is not None:
            _write(stage_dir / "parsed-proposal.json", original)
            _write(stage_dir / "normalized-for-canonical.json", attempt.raw_proposal)
    audit = semantic_omission_audit(source.text, run)
    _write(source_dir / "semantic-omission-audit.json", audit)
    failed = next((gate for gate in (*run.stage_gates, run.canonical_gate) if gate.status is GateStatus.FAIL_CLOSED), None)
    classification = {
        "detection_stage": failed.stage.value if failed else None,
        "origin_taxonomy": _origin(failed.stage, failed.exact_failure) if failed else None,
        "exact_failure": failed.exact_failure if failed else None,
        "error_type": failed.error_type if failed else None,
    }
    _write(source_dir / "failure-classification.json", classification)
    outcome["failure_classification"] = classification
    outcome["semantic_omission_audit"] = audit
    outcome["candidate_version"] = CANDIDATE_B_V2_VERSION
    outcome["stage_gates"] = run.to_dict()["stage_gates"]
    _write(source_dir / "final-outcome.json", outcome)
    return outcome


def validate_execution(sources: Sequence[Any], runs: Sequence[CandidateBV2Run]) -> dict[str, Any]:
    """Reconcile request-start ledger to stage invocations and raw outcomes."""
    if tuple((source.source_id, source.source_sha256) for source in sources) != EXPECTED_SOURCES or len(runs) != 9:
        raise RuntimeError("SPEC-052 source identities/order or outcome count changed")
    entries = []
    for source, run in zip(sources, runs, strict=True):
        if (run.source_id, run.source_sha256) != (source.source_id, source.source_sha256):
            raise RuntimeError(f"run source identity changed: {source.source_id}")
        local = list(run.provider_call_ledger.get("entries", []))
        if len(local) != run.provider_call_ledger.get("calls_started") or len(local) > 3:
            raise RuntimeError(f"request-start accounting/ceiling failed: {source.source_id}")
        expected = [gate.stage.value for gate in run.stage_gates if gate.status is not GateStatus.NOT_RUN_UPSTREAM_FAILURE]
        if [entry["stage"] for entry in local] != expected:
            raise RuntimeError(f"stage order or short-circuit failed: {source.source_id}")
        attempts = {item.stage.value: item for item in run.attempts}
        for entry in local:
            stage = entry["stage"]
            expected_hash = next(row[2] for row in EXPECTED_STAGE_HASHES if row[0] == stage)
            if entry["prompt_sha256"] != expected_hash or entry["prompt_version"] != _stage_version(StageName(stage)):
                raise RuntimeError(f"prompt identity drift: {source.source_id}/{stage}")
            if entry["store"] is not False or any(entry.get(key) != 0 for key in ("sdk_retries", "hidden_retries", "semantic_retries", "repair_calls")):
                raise RuntimeError(f"store/retry control drift: {source.source_id}/{stage}")
            dynamic_schema = (
                entity_inventory_schema() if stage == StageName.ENTITY_INVENTORY.value else
                stage2_v2_schema(run.inventory) if stage == StageName.SEMANTIC_STRUCTURE.value and run.inventory else
                claim_evidence_schema(run.structure.semantic_object_ids) if stage == StageName.CLAIM_EVIDENCE_BINDING.value and run.structure else None
            )
            if dynamic_schema is None or stable_hash(dynamic_schema) != entry["schema_sha256"]:
                raise RuntimeError(f"dynamic schema identity drift: {source.source_id}/{stage}")
            if entry["status"] == "PROVIDER_RESPONSE_RECEIVED" and stage not in attempts:
                raise RuntimeError(f"provider response lacks preserved attempt: {source.source_id}/{stage}")
            if stage in attempts:
                attempt = attempts[stage]
                if attempt.raw_provider_response is None and entry["status"] == "PROVIDER_RESPONSE_RECEIVED":
                    raise RuntimeError(f"raw provider response missing: {source.source_id}/{stage}")
                if attempt.provider_metadata.get("schema_sha256") != entry["schema_sha256"]:
                    raise RuntimeError(f"dynamic schema identity mismatch: {source.source_id}/{stage}")
            entries.append(entry)
        if len(local) == 0:
            raise RuntimeError(f"source was not attempted: {source.source_id}")
    if len(entries) > 27:
        raise RuntimeError("global 27-call ceiling exceeded")
    return {"status": "PASS", "sources": 9, "provider_calls_started": len(entries), "fixed_order": True,
            "one_call_per_stage": True, "short_circuit": True, "store": False, "retry_classes": 0,
            "raw_response_and_ledger_reconciled": True}


def _paired_rows(left: Sequence[Mapping[str, Any]], right: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["source_id"]: item for item in left}
    rows = []
    for item in right:
        prior = by_id[item["source_id"]]
        counts = {
            key: (item["admitted_counts"][key] - prior["admitted_counts"][key]
                  if item["admitted_counts"] and prior["admitted_counts"] else None)
            for key in ("entities", "relationships", "propositions", "claims")
        }
        rows.append({"source_id": item["source_id"], "historical_status": prior["status"],
                     "candidate_b_v2_status": item["status"], "admitted_count_delta_v2_minus_historical": counts,
                     "paired_comparison_is_descriptive": True})
    return rows


def _mechanical_branch(summary: Mapping[str, Any], outcomes: Sequence[Mapping[str, Any]]) -> str:
    """A conservative evidence label, never the owner's product verdict."""
    if summary["known_invalid_objects_admitted"]:
        return "B_V2_REGRESSION"
    # The frozen framework has no numerical promotion threshold. Admission,
    # usefulness, and claim preservation require the owner's integrated review.
    return "INCONCLUSIVE"


def run_live_evaluation(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    """Execute the one authorized B-v2 arm only; existing output forbids rerun."""
    if output_dir.exists():
        raise RuntimeError("SPEC-052 output exists; rerun is forbidden")
    preflight = build_preflight(repo_root, require_api_key=True)
    sources = load_frozen_sources(repo_root)
    output_dir.mkdir(parents=True)
    _write(output_dir / "preflight.json", preflight)
    _write(output_dir / "frozen-contract.json", _load(repo_root / SPEC051_DIRECTORY / "candidate-b-v2-contract.json"))
    runs: list[CandidateBV2Run] = []
    outcomes = []
    global_entries = []
    for index, source in enumerate(sources, start=1):
        # Read-only drift check; no prompt, schema, source, model or code adaptation.
        for path, expected in EXPECTED_V2_FILES.items():
            if _sha(repo_root / path) != expected:
                raise RuntimeError(f"frozen Candidate B v2 drifted after execution began: {path}")
        source_dir = output_dir / "sources" / f"{index:02d}-{source.source_id}"
        ledger = DurableLedger(source_dir / "request-start-ledger.json", source.source_id)
        adapter = OpenAICandidateBV2Extractor(model="gpt-5.6-luna", call_ledger=ledger)
        run = run_candidate_b_v2(
            source.text, adapter,
            source_metadata={"source_id": source.source_id, "title": source.title, "provenance": source.provenance},
            allow_live=True,
        )
        runs.append(run)
        outcomes.append(persist_v2_source(source_dir, source, run))
        for entry in run.provider_call_ledger["entries"]:
            global_entries.append({**entry, "global_call_ordinal": len(global_entries) + 1, "source_ordinal": index})
        _write(output_dir / "provider-call-ledger.json", {
            "candidate_version": CANDIDATE_B_V2_VERSION, "calls_started": len(global_entries), "entries": global_entries,
        })
        _write(output_dir / "run-progress.json", {"completed_sources": index, "source_ids": [item.source_id for item in sources[:index]],
                                                   "provider_calls_started": len(global_entries), "no_retries_or_repairs": True})
    validation = validate_execution(sources, runs)
    postflight = build_preflight(repo_root, require_api_key=False)
    _write(output_dir / "postflight.json", postflight)
    control = load_historical_control_records(repo_root)
    bv1 = _load(repo_root / SPEC048_DIRECTORY / "candidate-b-comparison-records.json")["records"]
    bv2 = [candidate_comparison_record(run) for run in runs]
    for record, run in zip(bv2, runs, strict=True):
        record["arm"] = "CANDIDATE_B_V2"
        record["execution_mode"] = "LIVE_FROZEN_SPEC052"
        record["stage_gates"] = run.to_dict()["stage_gates"]
    summaries = {"CONTROL_A_HISTORICAL": summarize_arm(control), "CANDIDATE_B_V1_HISTORICAL": summarize_arm(bv1),
                 "CANDIDATE_B_V2_LIVE": summarize_arm(bv2)}
    failures = [item["failure_classification"] for item in outcomes if item["status"] != "PASS"]
    stage_counts = dict(sorted(Counter(item["detection_stage"] for item in failures).items()))
    origin_counts = dict(sorted(Counter(item["origin_taxonomy"] for item in failures).items()))
    if not set(origin_counts) <= ORIGIN_TAXONOMY:
        raise RuntimeError("failure taxonomy expanded")
    all_audits = [item["semantic_omission_audit"] for item in outcomes if item["semantic_omission_audit"]["stage3_ran"]]
    omission = {"stage3_source_count": len(all_audits),
                "parsed_claim_count": sum(len(item["claims"]) for item in all_audits),
                "claim_only_by_exact_statement_and_distinct_id_count": sum(item["claim_only_by_exact_statement_and_distinct_id_count"] for item in all_audits),
                "admitted_claim_count": sum(row.get("admitted_in_knowledge_model", False) for item in all_audits for row in item["claims"]),
                "unintended_topology_count": sum(item["unintended_topology_count_if_admitted"] or 0 for item in all_audits),
                "assertion_aware_projection_limitation": "No new grounded-assertion packet was admitted; the existing assertion-aware builder is not silently applied to B-v2 claims."}
    branch = _mechanical_branch(summaries["CANDIDATE_B_V2_LIVE"], outcomes)
    _write(output_dir / "validation.json", validation)
    _write(output_dir / "candidate-b-v2-comparison-records.json", {"records": bv2})
    _write(output_dir / "three-arm-comparison.json", {
        "summaries": summaries, "paired_v2_vs_control_a": _paired_rows(control, bv2),
        "paired_v2_vs_b_v1": _paired_rows(bv1, bv2),
        "historical_limitation": "Non-contemporaneous stochastic arms; model/provider/time drift is uncontrolled. Different admitted source sets make aggregate richness descriptive only.",
    })
    usage = summaries["CANDIDATE_B_V2_LIVE"]["usage_total"]
    report = {
        "schema": "spec-052-final-report-v1", "status": "IMPLEMENTED_AWAITING_REVIEW",
        "candidate_version": CANDIDATE_B_V2_VERSION, "contract_sha256": CONTRACT_SHA256,
        "source_outcomes": outcomes, "three_arm_summaries": summaries,
        "failure_detection_stages": stage_counts, "failure_origin_taxonomy": origin_counts,
        "proposition_construction_failures": origin_counts.get("PROPOSITION_CONSTRUCTION", 0),
        "historical_b_v1_proposition_construction_failures": 6,
        "semantic_omission_audit": omission,
        "provider_calls_started": validation["provider_calls_started"], "usage_total": usage,
        "provider_latency_ms_total": summaries["CANDIDATE_B_V2_LIVE"]["provider_latency_ms_total"],
        "monetary_cost": {"available": False, "reason": "No provider monetary-cost evidence; no prices inferred."},
        "known_invalid_objects_admitted": summaries["CANDIDATE_B_V2_LIVE"]["known_invalid_objects_admitted"],
        "mechanically_supported_branch": branch, "owner_verdict": "PENDING",
        "historical_limitation": "Three arms are non-contemporaneous and stochastic; comparisons are descriptive, not causal.",
        "preflight": preflight, "execution_validation": validation,
        "deviations": [], "owner_review": {"state": "OWNER_REVIEW", "promotion": "NOT_AUTHORIZED"},
    }
    _write(output_dir / "final-report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run exactly one SPEC-052 B-v2 frozen evaluation")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = run_live_evaluation(root, root / OUTPUT_DIRECTORY)
    print(json.dumps({"status": report["status"], "calls": report["provider_calls_started"],
                      "admitted": report["three_arm_summaries"]["CANDIDATE_B_V2_LIVE"]["admitted_sources"]}))


if __name__ == "__main__":
    main()
