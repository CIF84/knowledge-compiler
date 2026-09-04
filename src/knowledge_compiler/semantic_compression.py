"""Provider-independent semantic-compression adequacy boundary for SPEC-015."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping, Protocol

from .models import RelationshipType, ValidationError
from .relationships import RELATIONSHIP_DEFINITION_MAP


COMPRESSION_PROTOCOL_VERSION = "spec-015-v1"
EXPECTED_SOURCE_PACKET_SHA256 = (
    "cbbef7b3eca555c4691024f987d6ba04be6cb6091d90d91d2121290782591088"
)
EXPECTED_CASE_COUNT = 10


class CompressionVerdict(StrEnum):
    BINARY_ADEQUATE = "BINARY_ADEQUATE"
    SOURCE_ROLE_INADEQUATE = "SOURCE_ROLE_INADEQUATE"
    TARGET_ROLE_INADEQUATE = "TARGET_ROLE_INADEQUATE"
    MISSING_ESSENTIAL_PARTICIPANT = "MISSING_ESSENTIAL_PARTICIPANT"
    MISSING_IMPLICIT_PARTICIPANT = "MISSING_IMPLICIT_PARTICIPANT"
    REQUIRES_STRUCTURED_PROPOSITION = "REQUIRES_STRUCTURED_PROPOSITION"
    INSUFFICIENT_FOR_BINARY_RELATIONSHIP = "INSUFFICIENT_FOR_BINARY_RELATIONSHIP"


class CompressionLabel(StrEnum):
    ROLE_ADEQUATE = "ROLE_ADEQUATE"
    ROLE_INADEQUATE = "ROLE_INADEQUATE"


def _nonempty(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} must be a non-empty string")
    return value


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{path} must be an object")
    return dict(value)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True, slots=True)
class CompressionBenchmarkCase:
    case_id: str
    blind_id: str
    label: CompressionLabel
    assertion: Mapping[str, Any]
    symbols: tuple[Mapping[str, Any], ...]
    candidate: Mapping[str, Any]
    predicate_contract: Mapping[str, Any]
    historical_classification: str
    defect_family: str | None
    provenance: Mapping[str, Any]
    raw: Mapping[str, Any] = field(repr=False)

    def __post_init__(self) -> None:
        _nonempty(self.case_id, "case.case_id")
        _nonempty(self.blind_id, "case.blind_id")
        object.__setattr__(self, "label", CompressionLabel(self.label))
        assertion = _mapping(self.assertion, "case.assertion")
        if set(assertion) != {
            "statement", "construction", "participant_symbol_ids", "evidence"
        }:
            raise ValidationError("benchmark assertion fields do not match the frozen contract")
        _nonempty(assertion.get("statement"), "case.assertion.statement")
        participants = assertion.get("participant_symbol_ids")
        if not isinstance(participants, list) or not participants or len(participants) != len(set(participants)):
            raise ValidationError("assertion participants must be a non-empty unique array")
        evidence = _mapping(assertion.get("evidence"), "case.assertion.evidence")
        if set(evidence) != {"document_id", "start_char", "end_char", "quote"}:
            raise ValidationError("assertion evidence fields do not match the frozen contract")
        _nonempty(evidence.get("document_id"), "case.assertion.evidence.document_id")
        _nonempty(evidence.get("quote"), "case.assertion.evidence.quote")
        if any(isinstance(evidence.get(key), bool) or not isinstance(evidence.get(key), int)
               for key in ("start_char", "end_char")):
            raise ValidationError("assertion evidence offsets must be integers")
        symbols = tuple(_mapping(item, "case.symbol") for item in self.symbols)
        if not symbols or any(set(item) != {"id", "name", "entity_type"} for item in symbols):
            raise ValidationError("benchmark symbols must contain exactly id, name, and entity_type")
        symbol_ids = [item["id"] for item in symbols]
        if len(symbol_ids) != len(set(symbol_ids)) or any(not str(item).strip() for item in symbol_ids):
            raise ValidationError("benchmark symbol IDs must be non-empty and unique")
        if not set(participants) <= set(symbol_ids):
            raise ValidationError("assertion participants must resolve against benchmark symbols")
        candidate = _mapping(self.candidate, "case.candidate")
        if set(candidate) != {
            "id", "source_entity_id", "relationship_type", "target_entity_id",
            "statement", "confidence", "origin",
        }:
            raise ValidationError("historical candidate fields do not match the frozen contract")
        relationship_type = RelationshipType(candidate.get("relationship_type"))
        endpoints = {candidate.get("source_entity_id"), candidate.get("target_entity_id")}
        if not endpoints <= set(symbol_ids):
            raise ValidationError("candidate endpoints must resolve against benchmark symbols")
        contract = _mapping(self.predicate_contract, "case.predicate_contract")
        expected_definition = RELATIONSHIP_DEFINITION_MAP[relationship_type]
        expected_contract = {
            key: getattr(expected_definition, key)
            for key in ("source_role", "target_role", "direction", "meaning")
        }
        if contract != expected_contract:
            raise ValidationError("predicate contract differs from the canonical relationship contract")
        object.__setattr__(self, "assertion", assertion)
        object.__setattr__(self, "symbols", symbols)
        object.__setattr__(self, "candidate", candidate)
        object.__setattr__(self, "predicate_contract", contract)
        object.__setattr__(self, "provenance", _mapping(self.provenance, "case.provenance"))
        object.__setattr__(self, "raw", _mapping(self.raw, "case.raw"))

    def to_blinded_dict(self) -> dict[str, Any]:
        evidence = self.assertion["evidence"]
        return {
            "case_id": self.blind_id,
            "grounded_assertion": {
                "statement": self.assertion["statement"],
                "participant_symbol_ids": list(self.assertion["participant_symbol_ids"]),
                "evidence": {
                    "document_id": evidence["document_id"],
                    "start_char": evidence["start_char"],
                    "end_char": evidence["end_char"],
                    "quote": evidence["quote"],
                },
            },
            "symbols": [dict(item) for item in self.symbols],
            "candidate_relationship": {
                "source_entity_id": self.candidate["source_entity_id"],
                "relationship_type": self.candidate["relationship_type"],
                "target_entity_id": self.candidate["target_entity_id"],
            },
            "predicate_contract": dict(self.predicate_contract),
        }


@dataclass(frozen=True, slots=True)
class CompressionBenchmark:
    source_path: Path
    source_sha256: str
    packet_version: str
    cases: tuple[CompressionBenchmarkCase, ...]
    source_catalog: tuple[Mapping[str, Any], ...]
    raw: Mapping[str, Any] = field(repr=False)

    @property
    def case_ids(self) -> frozenset[str]:
        return frozenset(item.blind_id for item in self.cases)

    def case_by_blind_id(self) -> dict[str, CompressionBenchmarkCase]:
        return {item.blind_id: item for item in self.cases}

    def to_blinded_dict(self) -> dict[str, Any]:
        result = {
            "protocol_version": COMPRESSION_PROTOCOL_VERSION,
            "cases": [item.to_blinded_dict() for item in sorted(self.cases, key=lambda x: x.blind_id)],
        }
        validate_blinded_packet(result, self)
        return result


def load_frozen_benchmark(path: Path) -> CompressionBenchmark:
    raw_bytes = path.read_bytes()
    digest = _sha256_bytes(raw_bytes)
    if digest != EXPECTED_SOURCE_PACKET_SHA256:
        raise ValidationError(
            "SPEC-015 source packet SHA-256 mismatch: "
            f"expected {EXPECTED_SOURCE_PACKET_SHA256}, got {digest}"
        )
    value = json.loads(raw_bytes)
    if not isinstance(value, Mapping):
        raise ValidationError("SPEC-015 source packet must be an object")
    if value.get("packet_version") != "review-003-step-1-v1":
        raise ValidationError("SPEC-015 source packet version mismatch")
    if value.get("status") != "FROZEN_OFFLINE_NO_LIVE_CALL":
        raise ValidationError("SPEC-015 source packet is not frozen")
    raw_cases = value.get("cases")
    contracts = value.get("predicate_contracts")
    if not isinstance(raw_cases, list) or not isinstance(contracts, Mapping):
        raise ValidationError("SPEC-015 source packet lacks cases or predicate contracts")
    cases = tuple(
        CompressionBenchmarkCase(
            case_id=item.get("case_id"),
            blind_id=item.get("blind_id"),
            label=item.get("label"),
            assertion=item.get("assertion"),
            symbols=tuple(item.get("symbols", ())),
            candidate=item.get("candidate"),
            predicate_contract=contracts.get(item.get("candidate", {}).get("relationship_type")),
            historical_classification=item.get("historical_classification"),
            defect_family=item.get("defect_family"),
            provenance=item.get("provenance"),
            raw=item,
        )
        for item in raw_cases
    )
    if len(cases) != EXPECTED_CASE_COUNT or len({item.case_id for item in cases}) != len(cases):
        raise ValidationError("SPEC-015 requires exactly 10 unique historical cases")
    blind_ids = [item.blind_id for item in cases]
    if len(blind_ids) != len(set(blind_ids)):
        raise ValidationError("SPEC-015 blind IDs must be unique")
    ranked = sorted(cases, key=lambda item: hashlib.sha256(item.case_id.encode()).hexdigest())
    expected_blind_ids = [f"endpoint-role-{index:03d}" for index in range(1, 11)]
    if [item.blind_id for item in ranked] != expected_blind_ids:
        raise ValidationError("SPEC-015 opaque IDs do not match the frozen SHA-256 ranking")
    positive = sum(item.label is CompressionLabel.ROLE_ADEQUATE for item in cases)
    negative = sum(item.label is CompressionLabel.ROLE_INADEQUATE for item in cases)
    if (positive, negative) != (5, 5) or value.get("counts") != {
        "total": 10, "positive": 5, "negative": 5
    }:
        raise ValidationError("SPEC-015 requires exactly five positive and five negative cases")
    catalog = value.get("source_catalog")
    if not isinstance(catalog, list) or not catalog:
        raise ValidationError("SPEC-015 source catalog must be non-empty")
    return CompressionBenchmark(
        source_path=path,
        source_sha256=digest,
        packet_version=value["packet_version"],
        cases=cases,
        source_catalog=tuple(dict(item) for item in catalog),
        raw=dict(value),
    )


_BLIND_TOP_LEVEL_FIELDS = {"protocol_version", "cases"}
_BLIND_CASE_FIELDS = {
    "case_id", "grounded_assertion", "symbols", "candidate_relationship", "predicate_contract"
}
_BLIND_ASSERTION_FIELDS = {"statement", "participant_symbol_ids", "evidence"}
_BLIND_CANDIDATE_FIELDS = {"source_entity_id", "relationship_type", "target_entity_id"}
_FORBIDDEN_KEYS = {
    "label", "expected_verdict", "historical_classification", "defect_family", "construction",
    "candidate_endpoint_ids", "dropped_participant_ids",
    "implicit_or_required_role_not_represented", "positive_control_reason", "provenance",
    "candidate_id", "candidate_statement", "confidence", "origin",
    "independent_review_note", "accepted_correction", "fallback",
}


def _walk_keys(value: Any) -> set[str]:
    if isinstance(value, Mapping):
        return set(value) | set().union(*(_walk_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_walk_keys(item) for item in value), set())
    return set()


def validate_blinded_packet(value: Mapping[str, Any], benchmark: CompressionBenchmark) -> None:
    if not isinstance(value, Mapping) or set(value) != _BLIND_TOP_LEVEL_FIELDS:
        raise ValidationError("blinded packet top-level fields do not match the fixed contract")
    if value.get("protocol_version") != COMPRESSION_PROTOCOL_VERSION:
        raise ValidationError("blinded packet protocol version mismatch")
    raw_cases = value.get("cases")
    if not isinstance(raw_cases, list) or len(raw_cases) != EXPECTED_CASE_COUNT:
        raise ValidationError("blinded packet must contain exactly 10 cases")
    expected = benchmark.case_by_blind_id()
    actual_ids: list[str] = []
    for item in raw_cases:
        if not isinstance(item, Mapping) or set(item) != _BLIND_CASE_FIELDS:
            raise ValidationError("blinded case fields do not match the fixed contract")
        blind_id = item.get("case_id")
        actual_ids.append(blind_id)
        source = expected.get(blind_id)
        if source is None:
            raise ValidationError(f"blinded packet contains unknown case ID {blind_id!r}")
        assertion = item.get("grounded_assertion")
        candidate = item.get("candidate_relationship")
        if not isinstance(assertion, Mapping) or set(assertion) != _BLIND_ASSERTION_FIELDS:
            raise ValidationError("blinded assertion fields do not match the fixed contract")
        if not isinstance(candidate, Mapping) or set(candidate) != _BLIND_CANDIDATE_FIELDS:
            raise ValidationError("blinded candidate must contain only source, predicate, and target")
        if dict(item) != source.to_blinded_dict():
            raise ValidationError("blinded case differs from its frozen historical projection")
    if actual_ids != sorted(expected) or len(actual_ids) != len(set(actual_ids)):
        raise ValidationError("blinded cases must be unique and sorted by opaque ID")
    leaked_keys = _walk_keys(value) & _FORBIDDEN_KEYS
    if leaked_keys:
        raise ValidationError(f"blinded packet leaks forbidden fields: {sorted(leaked_keys)}")
    serialized = json.dumps(value, ensure_ascii=False)
    leaked_values = [
        token for token in (*CompressionLabel, *(item.case_id for item in benchmark.cases))
        if str(token) in serialized
    ]
    if leaked_values:
        raise ValidationError("blinded packet leaks benchmark labels or descriptive case IDs")


def _objects(value: Any):
    if isinstance(value, Mapping):
        yield value
        for item in value.values():
            yield from _objects(item)
    elif isinstance(value, list):
        for item in value:
            yield from _objects(item)


def validate_historical_evidence(
    benchmark: CompressionBenchmark, repository_root: Path
) -> dict[str, Any]:
    documents: dict[str, Mapping[str, Any]] = {}
    source_hashes: dict[str, str] = {}
    for source in benchmark.source_catalog:
        path = repository_root / source["source_artifact"]
        if not path.is_file():
            raise ValidationError(f"missing frozen source artifact: {source['source_artifact']}")
        digest = _sha256_bytes(path.read_bytes())
        if digest != source.get("source_artifact_sha256"):
            raise ValidationError(f"frozen source artifact hash mismatch: {path}")
        document = json.loads(path.read_text(encoding="utf-8")).get("document")
        if not isinstance(document, Mapping) or document.get("id") != source["document_id"]:
            raise ValidationError(f"source document identity mismatch: {path}")
        documents[source["document_id"]] = document
        source_hashes[source["document_id"]] = digest
    candidate_fields = {
        "id", "source_entity_id", "relationship_type", "target_entity_id",
        "statement", "confidence", "origin",
    }
    for case in benchmark.cases:
        evidence = case.assertion["evidence"]
        document = documents.get(evidence["document_id"])
        if document is None:
            raise ValidationError(f"case {case.case_id} references an unknown source document")
        actual_quote = document["text"][evidence["start_char"]:evidence["end_char"]]
        if actual_quote != evidence["quote"]:
            raise ValidationError(f"case {case.case_id} evidence does not match the frozen source")
        provenance = case.provenance
        candidate_path = repository_root / provenance["candidate_artifact"]
        review_path = repository_root / provenance["independent_review_artifact"]
        if not candidate_path.is_file() or not review_path.is_file():
            raise ValidationError(f"case {case.case_id} has missing historical provenance")
        historical = json.loads(candidate_path.read_text(encoding="utf-8"))
        matches = [
            item for item in _objects(historical)
            if candidate_fields <= set(item)
            and {key: item[key] for key in candidate_fields} == dict(case.candidate)
        ]
        if not matches:
            raise ValidationError(f"case {case.case_id} candidate differs from historical artifact")
        for key, value in provenance.items():
            if key.endswith("_artifact") or key == "accepted_correction_review":
                if not (repository_root / value).is_file():
                    raise ValidationError(f"case {case.case_id} provenance path is missing: {value}")
    return {
        "source_packet_sha256": benchmark.source_sha256,
        "case_count": len(benchmark.cases),
        "positive_case_count": sum(
            item.label is CompressionLabel.ROLE_ADEQUATE for item in benchmark.cases
        ),
        "negative_case_count": sum(
            item.label is CompressionLabel.ROLE_INADEQUATE for item in benchmark.cases
        ),
        "source_artifact_hashes": source_hashes,
        "evidence_spans_preserved": True,
        "historical_candidates_preserved": True,
        "predicate_contracts_preserved": True,
        "symbol_identity_integrity": True,
        "provenance_paths_exist": True,
    }


@dataclass(frozen=True, slots=True)
class CompressionDecision:
    case_id: str
    verdict: CompressionVerdict
    rationale: str

    def __post_init__(self) -> None:
        _nonempty(self.case_id, "decision.case_id")
        object.__setattr__(self, "verdict", CompressionVerdict(self.verdict))
        _nonempty(self.rationale, "decision.rationale")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> CompressionDecision:
        if not isinstance(value, Mapping) or set(value) != {"case_id", "verdict", "rationale"}:
            raise ValidationError(
                "compression decision may contain only case_id, verdict, and rationale"
            )
        return cls(value.get("case_id"), value.get("verdict"), value.get("rationale"))


@dataclass(frozen=True, slots=True)
class CompressionResult:
    decisions: tuple[CompressionDecision, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any], expected_case_ids: frozenset[str]
    ) -> CompressionResult:
        if not isinstance(value, Mapping) or set(value) - {"decisions", "metadata"}:
            raise ValidationError("compression result has unknown fields")
        raw = value.get("decisions")
        if not isinstance(raw, list):
            raise ValidationError("compression decisions must be an array")
        decisions = tuple(CompressionDecision.from_dict(item) for item in raw)
        actual = [item.case_id for item in decisions]
        unknown = sorted(set(actual) - expected_case_ids)
        missing = sorted(expected_case_ids - set(actual))
        duplicates = sorted(item for item in set(actual) if actual.count(item) > 1)
        if unknown or missing or duplicates:
            raise ValidationError(
                "compression judge must decide every frozen case exactly once; "
                f"unknown={unknown}, missing={missing}, duplicates={duplicates}"
            )
        return cls(
            tuple(sorted(decisions, key=lambda item: item.case_id)),
            dict(value.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "decisions": [
                {**asdict(item), "verdict": item.verdict.value} for item in self.decisions
            ],
            "metadata": dict(self.metadata),
        }


class SemanticCompressionJudge(Protocol):
    """Provider-independent, one-shot judge boundary."""

    last_raw: Mapping[str, Any] | None
    last_metadata: Mapping[str, Any]

    def judge(
        self, blinded_packet: Mapping[str, Any], expected_case_ids: frozenset[str]
    ) -> CompressionResult: ...


def aggregate_compression_metrics(
    benchmark: CompressionBenchmark, result: CompressionResult
) -> dict[str, Any]:
    cases = benchmark.case_by_blind_id()
    true_admits = false_admits = true_rejects = false_rejects = 0
    per_case = []
    per_predicate: dict[str, dict[str, int]] = {}
    per_family: dict[str, dict[str, int]] = {}
    verdict_distribution: dict[str, int] = {}
    for decision in result.decisions:
        case = cases[decision.case_id]
        adequate = decision.verdict is CompressionVerdict.BINARY_ADEQUATE
        expected_adequate = case.label is CompressionLabel.ROLE_ADEQUATE
        true_admits += int(adequate and expected_adequate)
        false_admits += int(adequate and not expected_adequate)
        true_rejects += int(not adequate and not expected_adequate)
        false_rejects += int(not adequate and expected_adequate)
        correct = adequate == expected_adequate
        predicate = case.candidate["relationship_type"]
        family = RELATIONSHIP_DEFINITION_MAP[RelationshipType(predicate)].family.value
        for bucket, key in ((per_predicate, predicate), (per_family, family)):
            values = bucket.setdefault(key, {"correct": 0, "incorrect": 0, "total": 0})
            values["correct" if correct else "incorrect"] += 1
            values["total"] += 1
        verdict_distribution[decision.verdict.value] = (
            verdict_distribution.get(decision.verdict.value, 0) + 1
        )
        per_case.append({
            "blind_id": decision.case_id,
            "historical_case_id": case.case_id,
            "label": case.label.value,
            "candidate": {
                "source_entity_id": case.candidate["source_entity_id"],
                "relationship_type": predicate,
                "target_entity_id": case.candidate["target_entity_id"],
            },
            "historical_classification": case.historical_classification,
            "judge_verdict": decision.verdict.value,
            "judge_rationale": decision.rationale,
            "correct": correct,
        })
    positive = true_admits + false_rejects
    negative = true_rejects + false_admits
    admitted = true_admits + false_admits
    total = positive + negative

    def ratio(numerator: int, denominator: int) -> float | str:
        return numerator / denominator if denominator else "NOT_AVAILABLE"

    all_same = len(verdict_distribution) == 1
    blanket_rejection = admitted == 0
    return {
        "positive_case_count": positive,
        "negative_case_count": negative,
        "true_adequate_admits": true_admits,
        "false_adequate_admits": false_admits,
        "true_inadequate_rejects": true_rejects,
        "false_inadequate_rejects": false_rejects,
        "adequate_admission_precision": ratio(true_admits, admitted),
        "adequate_admission_recall": ratio(true_admits, positive),
        "negative_rejection_rate": ratio(true_rejects, negative),
        "overall_agreement": ratio(true_admits + true_rejects, total),
        "verdict_distribution": verdict_distribution,
        "per_case": per_case,
        "per_predicate": per_predicate,
        "per_family": per_family,
        "trivial_strategy_checks": {
            "all_verdicts_identical": all_same,
            "blanket_rejection": blanket_rejection,
            "all_positive_controls_include_dropped_context": all(
                bool(item.raw.get("dropped_participant_ids"))
                for item in benchmark.cases
                if item.label is CompressionLabel.ROLE_ADEQUATE
            ),
        },
    }


def select_compression_experiment_verdict(
    metrics: Mapping[str, Any], *, operational_failure: bool = False
) -> str:
    """Apply qualitative thresholds frozen before the live output is seen."""
    if operational_failure:
        return "INCONCLUSIVE"
    if metrics["trivial_strategy_checks"]["blanket_rejection"]:
        return "NO_MEANINGFUL_SIGNAL"
    agreement = metrics["overall_agreement"]
    recall = metrics["adequate_admission_recall"]
    rejection = metrics["negative_rejection_rate"]
    precision = metrics["adequate_admission_precision"]
    if agreement >= 0.9 and recall >= 0.8 and rejection >= 0.8 and precision >= 0.8:
        return "COMPRESSION_JUDGE_BETTER"
    if agreement >= 0.7 and recall >= 0.6 and rejection >= 0.6:
        return "MIXED"
    return "NO_MEANINGFUL_SIGNAL"
