"""Generic, source-identity-blind orchestration for future evaluation packets."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Protocol

from .deduplicate import deduplicate_entities
from .explanatory_projection import canonical_bytes
from .extractor import ExtractionResult
from .models import KnowledgeModel, Origin, SourceDocument, ValidationError
from .normalize import normalize_document, normalize_text
from .proposition_validation import validate_proposition_coverage
from .semantic_representation_compiler import compile_semantic_representation
from .structure_detection import StructureDetector


SOURCE_PACKET_SCHEMA_VERSION = "spec-040-blind-source-packet-v1"
FORBIDDEN_EXPECTATION_FIELDS = frozenset(
    {
        "expected_concepts",
        "expected_relationships",
        "expected_structure_type",
        "expected_representation_strategy",
        "expected_diagram_topology",
    }
)
_SOURCE_ID = re.compile(r"[a-z0-9][a-z0-9-]{1,127}")


def _canonical_copy(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, sort_keys=True))
    except (TypeError, ValueError) as exc:
        raise ValidationError("blind evaluation metadata must be JSON-compatible") from exc


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{path} must be an object")
    return dict(value)


def _exact_fields(value: Mapping[str, Any], allowed: set[str], path: str) -> None:
    unknown = set(value) - allowed
    missing = allowed - set(value)
    if unknown:
        raise ValidationError(f"{path} contains unknown fields: {sorted(unknown)}")
    if missing:
        raise ValidationError(f"{path} is missing fields: {sorted(missing)}")


def _reject_expectations(value: Any, path: str = "packet") -> None:
    if isinstance(value, Mapping):
        present = FORBIDDEN_EXPECTATION_FIELDS.intersection(value)
        if present:
            raise ValidationError(
                f"{path} contains representation-prescriptive fields: {sorted(present)}"
            )
        for key, nested in value.items():
            _reject_expectations(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_expectations(nested, f"{path}[{index}]")


@dataclass(frozen=True, slots=True)
class BlindSource:
    """One immutable bounded source with no evaluator-provided semantic answer."""

    source_id: str
    title: str
    text: str
    source_sha256: str
    provenance: Mapping[str, Any]

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "BlindSource":
        raw = _object(value, "source")
        _exact_fields(
            raw,
            {"source_id", "title", "text", "source_sha256", "provenance"},
            "source",
        )
        source_id = raw["source_id"]
        title = raw["title"]
        text = raw["text"]
        digest = raw["source_sha256"]
        if not isinstance(source_id, str) or _SOURCE_ID.fullmatch(source_id) is None:
            raise ValidationError("source.source_id must be a stable lowercase identifier")
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("source.title must be a non-empty neutral display label")
        if not isinstance(text, str) or not text.strip():
            raise ValidationError("source.text must contain the exact bounded source scope")
        if normalize_text(text) != text:
            raise ValidationError("source.text must already be canonically normalized")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValidationError("source.source_sha256 must be a lowercase SHA-256")
        actual = sha256(text.encode("utf-8")).hexdigest()
        if digest != actual:
            raise ValidationError("source.source_sha256 does not match exact source text")
        provenance = _object(raw["provenance"], "source.provenance")
        if not provenance:
            raise ValidationError("source.provenance must not be empty")
        _reject_expectations(provenance, "source.provenance")
        return cls(source_id, title, text, digest, _canonical_copy(provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "text": self.text,
            "source_sha256": self.source_sha256,
            "provenance": _canonical_copy(self.provenance),
        }


@dataclass(frozen=True, slots=True)
class BlindSourcePacket:
    """Validated immutable input packet for a later blind execution."""

    sources: tuple[BlindSource, ...]
    schema_version: str = SOURCE_PACKET_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "BlindSourcePacket":
        raw = _object(value, "packet")
        _reject_expectations(raw)
        _exact_fields(raw, {"schema_version", "evaluation_contract", "sources"}, "packet")
        if raw["schema_version"] != SOURCE_PACKET_SCHEMA_VERSION:
            raise ValidationError("unsupported blind source-packet schema version")
        contract = _object(raw["evaluation_contract"], "packet.evaluation_contract")
        _exact_fields(
            contract,
            {"expected_representation_strategy_supplied"},
            "packet.evaluation_contract",
        )
        if contract["expected_representation_strategy_supplied"] is not False:
            raise ValidationError("source packet must explicitly supply no expected strategy")
        values = raw["sources"]
        if not isinstance(values, list) or not values:
            raise ValidationError("packet.sources must be a non-empty array")
        sources = tuple(BlindSource.from_dict(item) for item in values)
        source_ids = [item.source_id for item in sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValidationError("packet source IDs must be unique")
        return cls(sources=sources)

    @classmethod
    def from_path(cls, path: Path) -> "BlindSourcePacket":
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"cannot read blind source packet {path}: {exc}") from exc
        return cls.from_dict(value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "evaluation_contract": {
                "expected_representation_strategy_supplied": False,
            },
            "sources": [item.to_dict() for item in self.sources],
        }


def blind_source_packet_schema() -> dict[str, Any]:
    """Return the portable schema given to the later source-selection gate."""

    string = {"type": "string", "minLength": 1}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://knowledge-compiler.local/schema/spec-040-blind-source-packet-v1.json",
        "title": "Knowledge Compiler blind source packet",
        "type": "object",
        "required": ["schema_version", "evaluation_contract", "sources"],
        "additionalProperties": False,
        "properties": {
            "schema_version": {"const": SOURCE_PACKET_SCHEMA_VERSION},
            "evaluation_contract": {
                "type": "object",
                "required": ["expected_representation_strategy_supplied"],
                "additionalProperties": False,
                "properties": {
                    "expected_representation_strategy_supplied": {"const": False}
                },
            },
            "sources": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": [
                        "source_id",
                        "title",
                        "text",
                        "source_sha256",
                        "provenance",
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "source_id": {
                            "type": "string",
                            "pattern": "^[a-z0-9][a-z0-9-]{1,127}$",
                        },
                        "title": string,
                        "text": string,
                        "source_sha256": {
                            "type": "string",
                            "pattern": "^[0-9a-f]{64}$",
                        },
                        "provenance": {"type": "object", "minProperties": 1},
                    },
                },
            },
        },
        "forbidden_evaluator_fields": sorted(FORBIDDEN_EXPECTATION_FIELDS),
    }


@dataclass(frozen=True, slots=True)
class BlindExtractionAttempt:
    """Auditable result of exactly one extraction boundary invocation."""

    proposal: Mapping[str, Any]
    rejected_assertions: tuple[Mapping[str, Any], ...]
    provider_request_metadata: Mapping[str, Any]
    run_history: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.proposal, Mapping):
            raise ValidationError("extraction proposal must be an object")
        if not isinstance(self.provider_request_metadata, Mapping):
            raise ValidationError("provider request metadata must be an object")
        if not self.run_history or any(not isinstance(item, Mapping) for item in self.run_history):
            raise ValidationError("extraction run history must preserve at least one attempt")
        object.__setattr__(self, "proposal", _canonical_copy(self.proposal))
        object.__setattr__(
            self,
            "rejected_assertions",
            tuple(_canonical_copy(item) for item in self.rejected_assertions),
        )
        object.__setattr__(
            self,
            "provider_request_metadata",
            _canonical_copy(self.provider_request_metadata),
        )
        object.__setattr__(
            self, "run_history", tuple(_canonical_copy(item) for item in self.run_history)
        )


class BlindExtractionAdapter(Protocol):
    live_capable: bool

    def extract_once(self, document: SourceDocument) -> BlindExtractionAttempt:
        """Return one complete auditable attempt; adapters must not retry internally."""


class DryRunProposalAdapter:
    """Deterministic proposal boundary for synthetic, offline orchestration tests."""

    live_capable = False

    def __init__(self, proposals_by_source_sha256: Mapping[str, Mapping[str, Any]]) -> None:
        self._proposals = {
            key: _canonical_copy(value) for key, value in proposals_by_source_sha256.items()
        }

    def extract_once(self, document: SourceDocument) -> BlindExtractionAttempt:
        digest = sha256(document.text.encode("utf-8")).hexdigest()
        if digest not in self._proposals:
            raise ValidationError("no deterministic dry-run proposal for exact source hash")
        return BlindExtractionAttempt(
            proposal=self._proposals[digest],
            rejected_assertions=(),
            provider_request_metadata={
                "execution_mode": "DRY_RUN",
                "provider": None,
                "model": None,
                "live_call": False,
                "source_text_transmitted": False,
                "sdk_retries": 0,
                "semantic_retries": 0,
            },
            run_history=(
                {
                    "attempt": 1,
                    "kind": "DETERMINISTIC_SYNTHETIC_PROPOSAL",
                    "provider_request_id": None,
                    "live_call": False,
                    "retry": False,
                },
            ),
        )


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _evidence_resolution(model: KnowledgeModel) -> dict[str, Any]:
    rows = []
    for collection, values in (
        ("claims", model.claims),
        ("relationships", model.relationships),
        ("propositions", model.propositions),
    ):
        for item in values:
            rows.append(
                {
                    "collection": collection,
                    "semantic_id": item.id,
                    "origin": item.origin.value,
                    "evidence": [asdict(span) for span in item.evidence],
                    "grounding_status": (
                        "PASS_EXACT_SOURCE_SPAN"
                        if item.origin is Origin.SOURCE
                        else "NO_SOURCE_EVIDENCE_INFERRED"
                    ),
                }
            )
    return {
        "status": "PASS",
        "source_document_id": model.document.id,
        "resolved_items": rows,
    }


def _compile_decisions(model: KnowledgeModel) -> list[dict[str, Any]]:
    foci = [
        *(('concept', item.id) for item in model.entities),
        *(('canonical', item.id) for item in model.relationships),
        *(('proposition', item.id) for item in model.propositions),
    ]
    return [
        compile_semantic_representation(model, semantic_class, identity).to_dict()
        for semantic_class, identity in sorted(foci)
    ]


def _renderer_bindings(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    bindings = []
    for decision in decisions:
        plan = decision["representation_plan"]
        bindings.append(
            {
                "decision_id": decision["decision_id"],
                "semantic_focus_identity": decision["semantic_focus_identity"],
                "selected_representation_strategy": decision[
                    "selected_representation_strategy"
                ],
                "status": (
                    "SPEC038_COMPATIBLE_PLAN"
                    if plan is not None
                    else "TRUTHFUL_MISSING_RENDERER_FORM"
                ),
                "representation_plan": plan,
            }
        )
    return {
        "protected_surface_contract": "SPEC038_REPRESENTATION_PLAN",
        "bindings": bindings,
    }


def _case_directory(root: Path, index: int, source_id: str) -> Path:
    return root / "sources" / f"{index + 1:02d}-{source_id}"


def run_blind_evaluation(
    packet: BlindSourcePacket,
    extractor: BlindExtractionAdapter,
    *,
    output_dir: Path,
    allow_live: bool = False,
) -> dict[str, Any]:
    """Run one frozen packet with one adapter invocation per source and no retries."""

    if output_dir.exists():
        raise ValidationError("blind evaluation output directory already exists")
    if not allow_live and getattr(extractor, "live_capable", True):
        raise ValidationError("a live-capable extraction adapter requires explicit authority")
    output_dir.mkdir(parents=True)
    _write_json(output_dir / "source-packet.json", packet.to_dict())
    outcomes: list[dict[str, Any]] = []
    live_call_count = 0
    for index, source in enumerate(packet.sources):
        case_dir = _case_directory(output_dir, index, source.source_id)
        _write_json(case_dir / "source.json", source.to_dict())
        stage = "EXTRACTION_BOUNDARY"
        history: list[dict[str, Any]] = []
        try:
            document = normalize_document(
                source.text,
                metadata={
                    "source_id": source.source_id,
                    "title": source.title,
                    "provenance": source.provenance,
                    "source_sha256": source.source_sha256,
                },
            )
            attempt = extractor.extract_once(document)
            if attempt.provider_request_metadata.get("live_call") is True and not allow_live:
                raise ValidationError("live extraction is disabled for this harness execution")
            live_call_count += int(
                attempt.provider_request_metadata.get("live_call") is True
            )
            history.extend(attempt.run_history)
            _write_json(case_dir / "provider-request-metadata.json", attempt.provider_request_metadata)
            _write_json(case_dir / "extraction-proposal.json", attempt.proposal)
            _write_json(
                case_dir / "rejected-assertions.json",
                {"items": list(attempt.rejected_assertions)},
            )

            stage = "GROUNDING_AND_SEMANTIC_VALIDATION"
            extraction = deduplicate_entities(
                ExtractionResult.from_dict(attempt.proposal, document)
            )
            model = KnowledgeModel(
                document=document,
                entities=extraction.entities,
                claims=extraction.claims,
                relationships=extraction.relationships,
                propositions=extraction.propositions,
                metadata=extraction.metadata,
            )
            validate_proposition_coverage(model)
            grounding = _evidence_resolution(model)
            _write_json(case_dir / "grounding-resolution.json", grounding)
            _write_json(case_dir / "admitted-knowledge-model.json", model.to_dict())

            stage = "STRUCTURE_DETECTION"
            structures = StructureDetector().detect(model)
            _write_json(case_dir / "detected-structures.json", structures.to_dict())

            stage = "REPRESENTATION_DECISION"
            decisions = _compile_decisions(model)
            bindings = _renderer_bindings(decisions)
            _write_json(
                case_dir / "representation-decisions.json",
                {"schema": "semantic-representation-decision-v1", "decisions": decisions},
            )
            _write_json(case_dir / "renderer-bindings.json", bindings)
            _write_json(
                case_dir / "learner-review-artifact.json",
                {
                    "surface_contract": "SPEC038_PROTECTED_FOUR_SURFACE_MODEL",
                    "source": {
                        "source_id": source.source_id,
                        "title": source.title,
                        "source_sha256": source.source_sha256,
                    },
                    "representation_decisions": decisions,
                    "renderer_bindings": bindings["bindings"],
                    "learner_usefulness_verdict": "PENDING_OWNER_REVIEW",
                },
            )
            history.append(
                {
                    "attempt": 1,
                    "outcome": "ADMITTED",
                    "final_stage": "LEARNER_REVIEW_ARTIFACT",
                    "retry_count": 0,
                }
            )
            outcome = {
                "source_id": source.source_id,
                "source_sha256": source.source_sha256,
                "status": "PASS",
                "entity_count": len(model.entities),
                "relationship_count": len(model.relationships),
                "proposition_count": len(model.propositions),
                "detected_structure_count": len(structures.structures),
                "representation_decision_count": len(decisions),
                "selected_strategies": sorted(
                    {item["selected_representation_strategy"] for item in decisions}
                ),
            }
        except (ValidationError, ValueError, TypeError, RuntimeError) as exc:
            history.append(
                {
                    "attempt": 1,
                    "outcome": "FAILED_CLOSED",
                    "failure_stage": stage,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "retry_count": 0,
                }
            )
            failure = {
                "status": "FAILED_CLOSED",
                "stage": stage,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "retry_performed": False,
            }
            _write_json(case_dir / "failure.json", failure)
            outcome = {
                "source_id": source.source_id,
                "source_sha256": source.source_sha256,
                "status": "FAILED_CLOSED",
                "failure": failure,
            }
        _write_json(
            case_dir / "run-history.json",
            {
                "source_id": source.source_id,
                "adapter_invocation_count": 1,
                "hidden_retry_count": 0,
                "history": history,
            },
        )
        outcomes.append(outcome)

    report = {
        "schema": "spec-040-blind-evaluation-report-v1",
        "execution_policy": {
            "allow_live": allow_live,
            "adapter_invocations_per_source": 1,
            "hidden_retries": 0,
            "semantic_retries": 0,
            "source_order_changes_semantic_decisions": False,
        },
        "source_count": len(packet.sources),
        "outcomes": outcomes,
        "passed_source_count": sum(item["status"] == "PASS" for item in outcomes),
        "failed_closed_source_count": sum(
            item["status"] == "FAILED_CLOSED" for item in outcomes
        ),
        "live_model_or_external_calls": live_call_count,
        "learner_usefulness_verdict": "PENDING_OWNER_REVIEW",
    }
    _write_json(output_dir / "report.json", report)
    return report
