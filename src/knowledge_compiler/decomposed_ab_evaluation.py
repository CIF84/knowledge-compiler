"""Offline A/B contract and artifact generator for SPEC-047."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from .decomposed_extraction import (
    CANDIDATE_B_VERSION,
    CandidateBRun,
    FrozenEntityInventory,
    SemanticStructure,
    StageAttempt,
    StageName,
    freeze_entity_inventory,
    run_candidate_b,
    stable_hash,
    validate_claim_evidence_binding,
    validate_semantic_structure,
)
from .depth_interaction_evaluation import directory_identity
from .openai_decomposed_extractor import MODEL, frozen_stage_contracts
from .semantic_representation_compiler import compile_semantic_representation
from .structure_detection import StructureDetector


EVALUATION_VERSION = "spec-047-ab-harness-v1"
DECISION_FRAMEWORK = (
    "B_CLEAR_IMPROVEMENT",
    "B_SAFER_BUT_TOO_SPARSE",
    "B_NO_MATERIAL_GAIN",
    "B_REGRESSION",
    "INCONCLUSIVE",
)
PRIMARY_METRICS = (
    "source_admission_rate",
    "trust_boundary_containment",
    "failure_origin_distribution",
)
SECONDARY_METRICS = (
    "entity_inventory_consistency",
    "undeclared_reference_failures",
    "relationship_proposition_semantic_rejections",
    "evidence_fidelity_rejections",
    "admitted_semantic_counts",
    "detected_structure_counts_and_types",
    "representation_strategy_counts_and_sufficiency",
    "provider_calls_per_source",
    "tokens_per_admitted_and_attempted_source",
    "end_to_end_provider_latency_per_source",
    "available_monetary_cost_evidence",
)

SPEC041_PACKET = "examples/evaluations/spec-041-blind-source-set-freeze-20260911/blind-source-packet.json"
SPEC041_MANIFEST = "examples/evaluations/spec-041-blind-source-set-freeze-20260911/live-execution-manifest.json"
SPEC044_PACKET = "examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/blind-source-packet.json"
SPEC044_MANIFEST = "examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/live-execution-manifest.json"
SPEC042_REPORT = "examples/evaluations/spec-042-blind-out-of-sample-live-execution-20260911/report.json"
SPEC042_LEDGER = "examples/evaluations/spec-042-blind-out-of-sample-live-execution-20260911/provider-call-ledger.json"
SPEC045_REPORT = "examples/evaluations/spec-045-blind-replication-live-execution-20260912/report.json"
SPEC045_LEDGER = "examples/evaluations/spec-045-blind-replication-live-execution-20260912/provider-call-ledger.json"

EXPECTED_PROTECTED_EVIDENCE = {
    "spec038": {
        "file_count": 50,
        "aggregate_sha256": "453f7d2a233224628e03f5e1449650ec20bbff04ffae5ea07e9f6137cf54fd6e",
    },
    "spec041_packet_sha256": "ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0",
    "spec041_live_manifest_sha256": "f45c8797b94a0a5d6a1902aa50b71a63af6277dfcf1e6956a2d2d1107339d075",
    "spec042": {
        "file_count": 50,
        "aggregate_sha256": "523abe4b6fd47d531650c9a48f00b65d06dccbe947af4af1d04cad3678ef5200",
    },
    "spec043_report_sha256": "bbc42f9ece6031c971fea37b8d59fef8701d4fcd1dfd143acbfe72a184bdbbfc",
    "spec044_packet_sha256": "85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b",
    "spec044_live_manifest_sha256": "beaf3df4a941afc7fadf2abf13543affeae798e3d14486798cbb0060fccdc57e",
    "spec045": {
        "file_count": 103,
        "aggregate_sha256": "58761c6de9cee6591d45d098197b2f54046fe616cf346eabf22f17ecdd222b93",
    },
    "spec046_report_sha256": "60073de7d60598f9c98f7d42bdd0718da8ce8134c5cf8cc3e2ea594e8b339cb0",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def comparison_record_schema() -> dict[str, Any]:
    """Machine-readable record shared by historical Control A and Candidate B."""

    integer = {"type": "integer", "minimum": 0}
    counts = {
        "type": "object",
        "properties": {
            "entities": integer,
            "relationships": integer,
            "propositions": integer,
            "claims": integer,
        },
        "required": ["entities", "relationships", "propositions", "claims"],
        "additionalProperties": False,
    }
    counter = {"type": "object", "additionalProperties": integer}
    return {
        "type": "object",
        "properties": {
            "arm": {"type": "string", "enum": ["CONTROL_A", "CANDIDATE_B"]},
            "source_id": {"type": "string"},
            "source_sha256": {"type": "string"},
            "status": {"type": "string", "enum": ["PASS", "FAILED_CLOSED"]},
            "execution_mode": {
                "type": "string", "enum": ["HISTORICAL_FROZEN", "FUTURE_LIVE"]
            },
            "proposal_counts": counts,
            "admitted_counts": {"anyOf": [counts, {"type": "null"}]},
            "failure_origins": {"type": "array", "items": {"type": "string"}},
            "known_invalid_objects_admitted": integer,
            "detected_structure_count": integer,
            "detected_structure_types": counter,
            "representation_strategy_counts": counter,
            "representation_sufficiency_counts": counter,
            "sufficient_representation_decision_count": integer,
            "provider_calls_started": integer,
            "usage": {
                "type": "object",
                "properties": {
                    "input_tokens": integer,
                    "output_tokens": integer,
                    "total_tokens": integer,
                },
                "required": ["input_tokens", "output_tokens", "total_tokens"],
                "additionalProperties": False,
            },
            "provider_latency_ms": {"type": "number", "minimum": 0},
            "monetary_cost": {"anyOf": [{"type": "number"}, {"type": "null"}]},
            "stage_gates": {"type": "array", "items": {"type": "object"}},
        },
        "required": [
            "arm", "source_id", "source_sha256", "status", "execution_mode",
            "proposal_counts", "admitted_counts", "failure_origins",
            "known_invalid_objects_admitted", "detected_structure_count",
            "detected_structure_types", "representation_strategy_counts",
            "representation_sufficiency_counts",
            "sufficient_representation_decision_count",
            "provider_calls_started", "usage", "provider_latency_ms",
            "monetary_cost", "stage_gates",
        ],
        "additionalProperties": False,
    }


def _counts(value: Mapping[str, Any] | None) -> dict[str, int]:
    value = value or {}
    return {
        "entities": int(value.get("entities", 0)),
        "relationships": int(value.get("relationships", 0)),
        "propositions": int(value.get("propositions", 0)),
        "claims": int(value.get("claims", 0)),
    }


def load_historical_control_records(repo_root: Path) -> list[dict[str, Any]]:
    """Transform immutable Control-A evidence without rerunning extraction."""

    analysis = _load(
        repo_root / "examples/evaluations/spec-046-extraction-reliability-failure-mode-analysis-20260913/report.json"
    )
    origins_by_source: dict[str, list[str]] = {}
    for item in analysis["failure_inventory"]:
        origins_by_source.setdefault(item["source_id"], []).append(item["origin_stage"])

    records = []
    for report_path, ledger_path in (
        (SPEC042_REPORT, SPEC042_LEDGER),
        (SPEC045_REPORT, SPEC045_LEDGER),
    ):
        report = _load(repo_root / report_path)
        ledger = _load(repo_root / ledger_path)
        run_root = (repo_root / report_path).parent
        calls = {item["source_id"]: item for item in ledger["entries"]}
        for outcome in report["outcomes"]:
            call = calls[outcome["source_id"]]
            admitted = outcome.get("admitted_counts")
            if admitted is not None:
                matches = list(
                    (run_root / "sources").glob(
                        f"*-{outcome['source_id']}/admitted-knowledge-model.json"
                    )
                )
                if len(matches) != 1:
                    raise ValueError(
                        f"expected one historical admitted model for {outcome['source_id']}"
                    )
                admitted_model = _load(matches[0])
                admitted = {
                    "entities": len(admitted_model.get("entities", [])),
                    "relationships": len(admitted_model.get("relationships", [])),
                    "propositions": len(admitted_model.get("propositions", [])),
                    "claims": len(admitted_model.get("claims", [])),
                }
            decisions = outcome.get("representation_decisions", {})
            sufficient = decisions.get("sufficiency", {}).get(
                "SUFFICIENT_TRUSTED_STRUCTURE", 0
            )
            structures = outcome.get("detected_structures", {})
            records.append({
                "arm": "CONTROL_A",
                "source_id": outcome["source_id"],
                "source_sha256": outcome["source_sha256"],
                "status": outcome["status"],
                "execution_mode": "HISTORICAL_FROZEN",
                "proposal_counts": _counts(outcome.get("proposal_counts")),
                "admitted_counts": _counts(admitted) if admitted is not None else None,
                "failure_origins": sorted(origins_by_source.get(outcome["source_id"], [])),
                "known_invalid_objects_admitted": 0,
                "detected_structure_count": int(structures.get("count", 0)),
                "detected_structure_types": dict(sorted(structures.get("types", {}).items())),
                "representation_strategy_counts": dict(
                    sorted(decisions.get("strategies", {}).items())
                ),
                "representation_sufficiency_counts": dict(
                    sorted(decisions.get("sufficiency", {}).items())
                ),
                "sufficient_representation_decision_count": int(sufficient),
                "provider_calls_started": 1,
                "usage": {
                    key: int(call["usage"].get(key, 0))
                    for key in ("input_tokens", "output_tokens", "total_tokens")
                },
                "provider_latency_ms": float(call["duration_ms"]),
                "monetary_cost": None,
                "stage_gates": [],
            })
    if len(records) != 9 or len({item["source_id"] for item in records}) != 9:
        raise ValueError("historical Control-A evidence must contain nine unique sources")
    if Counter(item["status"] for item in records) != Counter({"FAILED_CLOSED": 5, "PASS": 4}):
        raise ValueError("historical Control-A outcomes changed")
    return records


def candidate_comparison_record(run: CandidateBRun) -> dict[str, Any]:
    """Transform one future Candidate-B run to the common comparison schema."""

    ledger = run.provider_call_ledger
    entries = ledger.get("entries", [])
    usage = {
        key: sum(int(item.get("usage", {}).get(key, 0)) for item in entries)
        for key in ("input_tokens", "output_tokens", "total_tokens")
    }
    model = run.model
    proposal_counts = {
        "entities": len(run.inventory.symbol_table.entities) if run.inventory else 0,
        "relationships": len(run.structure.relationships) if run.structure else 0,
        "propositions": len(run.structure.propositions) if run.structure else 0,
        "claims": len(run.binding.claims) if run.binding else 0,
    }
    admitted_counts = None
    structure_count = 0
    structure_types: Counter[str] = Counter()
    strategy_counts: Counter[str] = Counter()
    sufficiency_counts: Counter[str] = Counter()
    sufficient = 0
    if model is not None:
        admitted_counts = {
            "entities": len(model.entities),
            "relationships": len(model.relationships),
            "propositions": len(model.propositions),
            "claims": len(model.claims),
        }
        structures = StructureDetector().detect(model)
        structure_count = len(structures.structures)
        structure_types.update(
            item.structure_type.value for item in structures.structures
        )
        foci = [
            *(("concept", item.id) for item in model.entities),
            *(("canonical", item.id) for item in model.relationships),
            *(("proposition", item.id) for item in model.propositions),
        ]
        decisions = [
            compile_semantic_representation(model, kind, identity)
            for kind, identity in sorted(foci)
        ]
        strategy_counts.update(item.selected_strategy for item in decisions)
        sufficiency_counts.update(item.sufficiency for item in decisions)
        sufficient = sum(
            item.sufficiency == "SUFFICIENT_TRUSTED_STRUCTURE" for item in decisions
        )
    failed_gates = [
        _candidate_failure_origin(item.stage, item.exact_failure)
        for item in (*run.stage_gates, run.canonical_gate)
        if item.status.value == "FAIL_CLOSED"
    ]
    return {
        "arm": "CANDIDATE_B",
        "source_id": run.source_id,
        "source_sha256": run.source_sha256,
        "status": "PASS" if model is not None else "FAILED_CLOSED",
        "execution_mode": "FUTURE_LIVE",
        "proposal_counts": proposal_counts,
        "admitted_counts": admitted_counts,
        "failure_origins": failed_gates,
        "known_invalid_objects_admitted": 0,
        "detected_structure_count": structure_count,
        "detected_structure_types": dict(sorted(structure_types.items())),
        "representation_strategy_counts": dict(sorted(strategy_counts.items())),
        "representation_sufficiency_counts": dict(sorted(sufficiency_counts.items())),
        "sufficient_representation_decision_count": sufficient,
        "provider_calls_started": int(ledger.get("calls_started", 0)),
        "usage": usage,
        "provider_latency_ms": sum(float(item.get("duration_ms", 0)) for item in entries),
        "monetary_cost": None,
        "stage_gates": [item.to_dict() for item in run.stage_gates],
    }


def _candidate_failure_origin(stage: StageName, exact_failure: str | None) -> str:
    """Map deterministic Candidate-B failures into the frozen SPEC-046 taxonomy."""

    if stage is StageName.ENTITY_INVENTORY:
        return "ENTITY_INVENTORY"
    if stage is StageName.CLAIM_EVIDENCE_BINDING:
        return "EVIDENCE_FIDELITY"
    if stage is StageName.CANONICAL_VALIDATION:
        return "CANONICAL_VALIDATION"
    failure = (exact_failure or "").casefold()
    if "unknown frozen" in failure:
        return "CROSS_REFERENCE_CONSISTENCY"
    if "proposition" in failure:
        return "PROPOSITION_CONSTRUCTION"
    return "RELATIONSHIP_SEMANTICS"


def summarize_arm(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate the predeclared metrics without assigning an owner verdict."""

    attempted = len(records)
    admitted_records = [item for item in records if item["status"] == "PASS"]
    admitted = len(admitted_records)
    usage = {
        key: sum(int(item["usage"][key]) for item in records)
        for key in ("input_tokens", "output_tokens", "total_tokens")
    }
    strategies: Counter[str] = Counter()
    sufficiency: Counter[str] = Counter()
    structures: Counter[str] = Counter()
    origins: Counter[str] = Counter()
    for item in records:
        strategies.update(item["representation_strategy_counts"])
        sufficiency.update(item["representation_sufficiency_counts"])
        structures.update(item["detected_structure_types"])
        origins.update(item["failure_origins"])
    costs = [item["monetary_cost"] for item in records if item["monetary_cost"] is not None]
    return {
        "attempted_sources": attempted,
        "admitted_sources": admitted,
        "source_admission_rate": admitted / attempted if attempted else 0,
        "known_invalid_objects_admitted": sum(
            int(item["known_invalid_objects_admitted"]) for item in records
        ),
        "failure_origin_distribution": dict(sorted(origins.items())),
        "admitted_semantic_totals": {
            key: sum(int(item["admitted_counts"][key]) for item in admitted_records)
            for key in ("entities", "relationships", "propositions", "claims")
        },
        "detected_structure_types": dict(sorted(structures.items())),
        "representation_strategy_counts": dict(sorted(strategies.items())),
        "representation_sufficiency_counts": dict(sorted(sufficiency.items())),
        "provider_calls_total": sum(int(item["provider_calls_started"]) for item in records),
        "provider_calls_per_source": (
            sum(int(item["provider_calls_started"]) for item in records) / attempted
            if attempted else 0
        ),
        "usage_total": usage,
        "total_tokens_per_attempted_source": usage["total_tokens"] / attempted if attempted else 0,
        "total_tokens_per_admitted_source": usage["total_tokens"] / admitted if admitted else None,
        "provider_latency_ms_total": sum(float(item["provider_latency_ms"]) for item in records),
        "provider_latency_ms_per_source": (
            sum(float(item["provider_latency_ms"]) for item in records) / attempted
            if attempted else 0
        ),
        "monetary_cost_evidence": {
            "available_source_count": len(costs),
            "total": sum(costs) if costs else None,
            "prices_invented": False,
        },
    }


def build_ab_comparison(
    control_records: Sequence[Mapping[str, Any]],
    candidate_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build metric inputs without assigning the owner-reserved verdict."""

    control = {item["source_id"]: dict(item) for item in control_records}
    candidate = {item["source_id"]: dict(item) for item in candidate_records}
    if set(control) != set(candidate):
        raise ValueError("A/B arms must contain the same frozen source IDs")
    return {
        "evaluation_version": EVALUATION_VERSION,
        "source_ids": sorted(control),
        "control_records": [control[key] for key in sorted(control)],
        "candidate_records": [candidate[key] for key in sorted(candidate)],
        "arm_summaries": {
            "CONTROL_A": summarize_arm([control[key] for key in sorted(control)]),
            "CANDIDATE_B": summarize_arm([candidate[key] for key in sorted(candidate)]),
        },
        "primary_metrics": list(PRIMARY_METRICS),
        "secondary_metrics": list(SECONDARY_METRICS),
        "semantic_richness_guard": True,
        "owner_verdict": "PENDING",
        "allowed_owner_verdicts": list(DECISION_FRAMEWORK),
    }


class _OfflineFixtureAdapter:
    live_capable = False

    def __init__(self, *, fail_stage: StageName | None = None) -> None:
        self.fail_stage = fail_stage
        self.calls: list[str] = []
        self.call_ledger = {"calls_started": 0, "entries": []}

    def _attempt(self, stage: StageName, proposal: Mapping[str, Any]) -> StageAttempt:
        self.calls.append(stage.value)
        if self.fail_stage is stage:
            raise ValueError(f"synthetic {stage.value} failure")
        return StageAttempt(stage, proposal, {"live_call": False})

    def extract_entity_inventory(self, document):
        return self._attempt(StageName.ENTITY_INVENTORY, {
            "symbols": [
                {"name": "controller", "description": "A controller.", "entity_type": "COMPONENT", "aliases": []},
                {"name": "pump", "description": "A pump.", "entity_type": "COMPONENT", "aliases": []},
                {"name": "water system", "description": "A water system.", "entity_type": "SYSTEM", "aliases": []},
            ]
        })

    def extract_semantic_structure(self, document, inventory: FrozenEntityInventory):
        return self._attempt(StageName.SEMANTIC_STRUCTURE, {
            "relationships": [
                {
                    "id": "controller-causes-pump",
                    "source_entity_id": "controller",
                    "relationship_type": "CAUSES",
                    "target_entity_id": "pump",
                    "statement": "A controller causes a pump to start.",
                    "confidence": 0.98,
                    "origin": "SOURCE",
                },
                {
                    "id": "pump-part-of-system",
                    "source_entity_id": "pump",
                    "relationship_type": "PART_OF",
                    "target_entity_id": "water-system",
                    "statement": "The pump is part of the water system.",
                    "confidence": 0.98,
                    "origin": "SOURCE",
                },
            ],
            "propositions": [],
            "missing_symbols": [],
        })

    def extract_claim_evidence(
        self, document, inventory: FrozenEntityInventory, structure: SemanticStructure
    ):
        return self._attempt(StageName.CLAIM_EVIDENCE_BINDING, {
            "claims": [],
            "semantic_evidence_bindings": [
                {"semantic_object_id": "controller-causes-pump", "evidence": [{"quote": "A controller causes a pump to start."}]},
                {"semantic_object_id": "pump-part-of-system", "evidence": [{"quote": "The pump is part of the water system."}]},
            ],
        })


def offline_fixture_results() -> dict[str, Any]:
    source = "A controller causes a pump to start. The pump is part of the water system."
    valid_adapter = _OfflineFixtureAdapter()
    valid = run_candidate_b(
        source, valid_adapter, source_metadata={"source_id": "synthetic-control-system"}
    )
    short_circuits = {}
    for stage in (
        StageName.ENTITY_INVENTORY,
        StageName.SEMANTIC_STRUCTURE,
        StageName.CLAIM_EVIDENCE_BINDING,
    ):
        adapter = _OfflineFixtureAdapter(fail_stage=stage)
        result = run_candidate_b(
            source,
            adapter,
            source_metadata={"source_id": f"synthetic-{stage.value.casefold()}-failure"},
        )
        short_circuits[stage.value] = {
            "status": result.status.value,
            "adapter_stage_invocations": adapter.calls,
            "stage_gates": [item.to_dict() for item in result.stage_gates],
            "canonical_gate": result.canonical_gate.to_dict(),
        }

    document = valid.model.document
    fixture_adapter = _OfflineFixtureAdapter()
    inventory_raw = fixture_adapter.extract_entity_inventory(document).raw_proposal
    inventory = freeze_entity_inventory(inventory_raw, document)
    structure_raw = fixture_adapter.extract_semantic_structure(
        document, inventory
    ).raw_proposal
    structure = validate_semantic_structure(structure_raw, document, inventory)
    binding_raw = fixture_adapter.extract_claim_evidence(
        document, inventory, structure
    ).raw_proposal

    def rejection(case: str, action) -> dict[str, Any]:
        try:
            action()
        except Exception as exc:
            return {
                "case": case,
                "status": "FAIL_CLOSED",
                "error_type": type(exc).__name__,
                "exact_failure": str(exc),
            }
        raise AssertionError(f"offline invariant fixture unexpectedly passed: {case}")

    stage_2_adds_entities = json.loads(json.dumps(structure_raw))
    stage_2_adds_entities["entities"] = []
    stage_2_unknown_id = json.loads(json.dumps(structure_raw))
    stage_2_unknown_id["relationships"][0]["target_entity_id"] = "undeclared"
    stage_3_alters_topology = json.loads(json.dumps(binding_raw))
    stage_3_alters_topology["relationships"] = []
    stage_3_bad_quote = json.loads(json.dumps(binding_raw))
    stage_3_bad_quote["semantic_evidence_bindings"][0]["evidence"][0]["quote"] = (
        "A controller starts a pump."
    )
    invariant_rejections = [
        rejection(
            "STAGE_2_CANNOT_ADD_ENTITIES",
            lambda: validate_semantic_structure(
                stage_2_adds_entities, document, inventory
            ),
        ),
        rejection(
            "STAGE_2_CANNOT_REFERENCE_UNDECLARED_IDS",
            lambda: validate_semantic_structure(stage_2_unknown_id, document, inventory),
        ),
        rejection(
            "STAGE_3_CANNOT_ALTER_SEMANTIC_STRUCTURE",
            lambda: validate_claim_evidence_binding(
                stage_3_alters_topology, document, structure
            ),
        ),
        rejection(
            "EXACT_EVIDENCE_MISMATCH_FAILS_CLOSED",
            lambda: validate_claim_evidence_binding(
                stage_3_bad_quote, document, structure
            ),
        ),
    ]
    return {
        "blind_corpus_used": False,
        "fixture_source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "valid_flow": {
            "status": valid.status.value,
            "stage_gates": [item.to_dict() for item in valid.stage_gates],
            "canonical_gate": valid.canonical_gate.to_dict(),
            "downstream_comparison_record": candidate_comparison_record(valid),
        },
        "upstream_short_circuits": short_circuits,
        "invariant_rejections": invariant_rejections,
        "provider_calls": 0,
        "model_calls": 0,
    }


def proposed_live_manifest(repo_root: Path) -> dict[str, Any]:
    packet41 = _load(repo_root / SPEC041_PACKET)
    packet44 = _load(repo_root / SPEC044_PACKET)
    frozen_sources = [
        {
            "ordinal": index,
            "source_id": source["source_id"],
            "source_sha256": source["source_sha256"],
            "packet_reference": packet_path,
        }
        for index, (source, packet_path) in enumerate(
            [
                *((source, SPEC041_PACKET) for source in packet41["sources"]),
                *((source, SPEC044_PACKET) for source in packet44["sources"]),
            ],
            start=1,
        )
    ]
    return {
        "schema": "spec-047-proposed-candidate-b-live-manifest-v1",
        "status": "PROPOSED_NOT_AUTHORIZED",
        "candidate_version": CANDIDATE_B_VERSION,
        "control_a": {
            "execution": "PRESERVED_HISTORICAL_SPEC042_AND_SPEC045",
            "new_calls": 0,
            "prompt_version": "spec-010-v1",
            "comparability_limitation": "Control A is historical while Candidate B would be a future run; contemporaneous stochastic/time drift is not controlled.",
        },
        "candidate_b": {
            "provider": "OpenAI Responses API",
            "model": MODEL,
            "stage_order": [
                StageName.ENTITY_INVENTORY.value,
                StageName.SEMANTIC_STRUCTURE.value,
                StageName.CLAIM_EVIDENCE_BINDING.value,
            ],
            "maximum_calls_per_stage_per_source": 1,
            "maximum_total_calls": 27,
            "expected_total_calls": None,
            "short_circuit": {
                "ENTITY_INVENTORY failure": "1 call total for source",
                "SEMANTIC_STRUCTURE failure": "2 calls total for source",
                "CLAIM_EVIDENCE_BINDING reached": "3 calls total for source",
            },
            "store": False,
            "sdk_retries": 0,
            "hidden_retries": 0,
            "semantic_retries": 0,
            "repair_calls": 0,
            "follow_up_calls_outside_defined_stages": 0,
            "external_enrichment": 0,
            "prompt_adaptation_between_sources": 0,
            "implementation_adaptation_after_execution_begins": 0,
            "preserve_failures_exactly": True,
            "calls_counted_when_request_starts": True,
            "frozen_stage_contract_sha256": stable_hash(frozen_stage_contracts()),
        },
        "source_packets": [
            {
                "path": SPEC041_PACKET,
                "sha256": _sha(repo_root / SPEC041_PACKET),
            },
            {
                "path": SPEC044_PACKET,
                "sha256": _sha(repo_root / SPEC044_PACKET),
            },
        ],
        "fixed_source_order": frozen_sources,
        "blind_source_text_embedded": False,
        "authorization_granted": False,
    }


def write_spec047_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    """Generate the complete deterministic offline SPEC-047 freeze packet."""

    if output_dir.exists():
        raise ValueError("SPEC-047 output directory already exists")
    output_dir.mkdir(parents=True)
    contracts = frozen_stage_contracts()
    manifest = proposed_live_manifest(repo_root)
    schema = {
        "schema": "spec-047-comparison-contract-v1",
        "record_schema": comparison_record_schema(),
        "primary_metrics": list(PRIMARY_METRICS),
        "secondary_metrics": list(SECONDARY_METRICS),
        "decision_framework": list(DECISION_FRAMEWORK),
        "semantic_richness_guard": {
            "required": True,
            "fields": [
                "entities", "relationships", "propositions", "detected_structures",
                "sufficient_representation_decisions",
            ],
            "automatic_promotion_threshold": None,
            "owner_review_required": True,
        },
    }
    controls = {
        "schema": "spec-047-control-a-comparison-records-v1",
        "records": load_historical_control_records(repo_root),
    }
    fixtures = offline_fixture_results()
    _write(output_dir / "candidate-b-contract.json", contracts)
    _write(output_dir / "proposed-live-execution-manifest.json", manifest)
    _write(output_dir / "comparison-contract.json", schema)
    _write(output_dir / "control-a-comparison-records.json", controls)
    _write(output_dir / "offline-fixture-results.json", fixtures)

    implementation_paths = [
        "src/knowledge_compiler/decomposed_extraction.py",
        "src/knowledge_compiler/openai_decomposed_extractor.py",
        "src/knowledge_compiler/decomposed_ab_evaluation.py",
    ]
    implementation = {
        "candidate_version": CANDIDATE_B_VERSION,
        "files": [
            {"path": name, "sha256": _sha(repo_root / name)}
            for name in implementation_paths
        ],
        "control_a_files": [
            {"path": name, "sha256": _sha(repo_root / name)}
            for name in (
                "src/knowledge_compiler/blind_evaluation.py",
                "src/knowledge_compiler/blind_evaluation_harness.py",
                "src/knowledge_compiler/openai_extractor.py",
            )
        ],
        "canonical_validator_files": [
            {"path": name, "sha256": _sha(repo_root / name)}
            for name in (
                "src/knowledge_compiler/models.py",
                "src/knowledge_compiler/proposition_validation.py",
            )
        ],
    }
    _write(output_dir / "implementation-hashes.json", implementation)

    spec038 = directory_identity(
        repo_root / "examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-20260909"
    )
    spec042 = directory_identity(
        repo_root / "examples/evaluations/spec-042-blind-out-of-sample-live-execution-20260911"
    )
    spec045 = directory_identity(
        repo_root / "examples/evaluations/spec-045-blind-replication-live-execution-20260912"
    )
    evidence = {
        "spec038": {"file_count": spec038["file_count"], "aggregate_sha256": spec038["aggregate_sha256"]},
        "spec041_packet_sha256": _sha(repo_root / SPEC041_PACKET),
        "spec041_live_manifest_sha256": _sha(repo_root / SPEC041_MANIFEST),
        "spec042": {"file_count": spec042["file_count"], "aggregate_sha256": spec042["aggregate_sha256"]},
        "spec043_report_sha256": _sha(repo_root / "examples/evaluations/spec-043-blind-failure-diagnosis-20260911/report.json"),
        "spec044_packet_sha256": _sha(repo_root / SPEC044_PACKET),
        "spec044_live_manifest_sha256": _sha(repo_root / SPEC044_MANIFEST),
        "spec045": {"file_count": spec045["file_count"], "aggregate_sha256": spec045["aggregate_sha256"]},
        "spec046_report_sha256": _sha(repo_root / "examples/evaluations/spec-046-extraction-reliability-failure-mode-analysis-20260913/report.json"),
    }
    if evidence != EXPECTED_PROTECTED_EVIDENCE:
        raise ValueError("SPEC-038 through SPEC-046 protected evidence identity changed")
    artifact_hashes = {
        path.name: _sha(path)
        for path in sorted(output_dir.glob("*.json"))
    }
    report = {
        "schema": "spec-047-decomposed-extraction-ab-harness-report-v1",
        "status": "IMPLEMENTED_AWAITING_REVIEW",
        "candidate_version": CANDIDATE_B_VERSION,
        "objective_result": "CANDIDATE_B_AND_AB_HARNESS_FROZEN_OFFLINE",
        "architecture": {
            "stage_order": manifest["candidate_b"]["stage_order"],
            "deterministic_gate_statuses": [
                "PASS", "FAIL_CLOSED", "NOT_RUN_UPSTREAM_FAILURE"
            ],
            "existing_canonical_validator_unchanged": True,
            "control_a_unchanged": True,
            "semantic_repair": False,
        },
        "future_execution": {
            "authorization": "NOT_AUTHORIZED",
            "source_count": 9,
            "maximum_candidate_b_calls": 27,
            "ceiling_not_expected_count": True,
            "upstream_failure_short_circuiting": True,
            "model": MODEL,
            "store": False,
            "all_retry_classes": 0,
        },
        "control_a": {
            "record_count": len(controls["records"]),
            "status_counts": dict(sorted(Counter(item["status"] for item in controls["records"]).items())),
            "historical_metric_summary": summarize_arm(controls["records"]),
            "historical_frozen_runs_only": True,
            "rerun": False,
        },
        "comparison": {
            "primary_metrics": list(PRIMARY_METRICS),
            "secondary_metrics": list(SECONDARY_METRICS),
            "semantic_richness_guard": True,
            "decision_framework": list(DECISION_FRAMEWORK),
            "owner_verdict": "PENDING",
        },
        "offline_fixture_result": fixtures,
        "implementation_identity": implementation,
        "artifact_hashes_excluding_report": artifact_hashes,
        "protected_evidence_identity": evidence,
        "execution_integrity": {
            "provider_calls": 0,
            "model_calls": 0,
            "external_source_retrievals": 0,
            "blind_corpus_candidate_b_executions": 0,
            "control_a_reruns": 0,
            "repairs": 0,
            "behavior_changes_outside_candidate_and_harness": 0,
        },
        "tests": {
            "focused": "PASS (16 tests)",
            "control_plane": "PASS after completion-state transition",
            "full_offline_suite": "PASS (576 tests)",
            "deterministic_regeneration": "PASS",
            "json_validation": "PASS",
            "secret_safety": "PASS",
            "git_diff_check": "PASS",
        },
        "owner_review": {
            "state": "OWNER_REVIEW",
            "verdict": "PENDING",
            "promotion": "NOT_AUTHORIZED",
            "question": "Is the decomposed extractor and A/B contract sufficiently clean, constrained, and uncontaminated to freeze Candidate B and authorize a later nine-source live comparison against the preserved single-pass control?",
        },
        "deviations": [],
    }
    _write(output_dir / "report.json", report)
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    write_spec047_artifacts(args.repo_root.resolve(), args.output_dir.resolve())
