from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from knowledge_compiler.models import KnowledgeModel, SourceDocument, ValidationError
from knowledge_compiler.openai_extractor import resolve_output_evidence
from knowledge_compiler.openai_staged_extractor import (
    OpenAIStagedExtractor,
    semantic_linking_schema,
)
from knowledge_compiler.staged_compilation import (
    SemanticLinkingResult,
    SymbolDiscoveryProposal,
    SymbolTableViolation,
    assemble_staged_knowledge_model,
    canonicalize_symbol_table,
    compile_staged_knowledge_model,
)
from knowledge_compiler.staged_semantic_evaluation import (
    SEMANTIC_REVIEW_CATEGORIES,
    build_control_semantic_review,
    finalize_staged_semantic_evaluation,
    run_staged_semantic_evaluation,
)


SOURCE = "Measurement affects a quantum state. A quantum state determines probability."
CONTROL = Path(
    "examples/evaluations/spec-011-quantum-real-source-20260904-run-002/"
    "rejected-parent-extraction.json"
)


def symbols() -> dict:
    return {
        "symbols": [
            {
                "name": "quantum state",
                "description": "A state represented by quantum mechanics.",
                "entity_type": "CONCEPT",
                "aliases": ["state"],
            },
            {
                "name": "measurement",
                "description": "A process that affects a state.",
                "entity_type": "PROCESS",
                "aliases": [],
            },
            {
                "name": "probability",
                "description": "Likelihood of an outcome.",
                "entity_type": "VARIABLE",
                "aliases": [],
            },
        ]
    }


def semantics() -> dict:
    return {
        "claims": [],
        "relationships": [
            {
                "id": "measurement-affects-state",
                "source_entity_id": "measurement",
                "relationship_type": "AFFECTS",
                "target_entity_id": "quantum-state",
                "statement": "Measurement affects a quantum state.",
                "evidence": [{"quote": "Measurement affects a quantum state."}],
                "confidence": 0.96,
                "origin": "SOURCE",
            },
            {
                "id": "state-affects-probability",
                "source_entity_id": "quantum-state",
                "relationship_type": "AFFECTS",
                "target_entity_id": "probability",
                "statement": "A quantum state determines probability.",
                "evidence": [{"quote": "A quantum state determines probability."}],
                "confidence": 0.9,
                "origin": "SOURCE",
            },
        ],
        "propositions": [],
        "missing_symbols": [],
    }


class FixtureStagedExtractor:
    def __init__(self, *, fail_pass_1: bool = False, unknown_pass_2: bool = False) -> None:
        self.fail_pass_1 = fail_pass_1
        self.unknown_pass_2 = unknown_pass_2
        self.pass_2_called = False
        self.last_pass_1_raw = symbols()
        self.last_pass_2_raw = None
        self.last_pass_1_metadata = {
            "provider": "fixture",
            "model": "fixture",
            "prompt_version": "fixture-symbols-v1",
            "usage": {},
        }
        self.last_pass_2_metadata = {
            "provider": "fixture",
            "model": "fixture",
            "prompt_version": "fixture-linking-v1",
            "usage": {},
        }

    def discover_symbols(self, document):
        if self.fail_pass_1:
            raise ValidationError("fixture Pass 1 failed")
        return SymbolDiscoveryProposal.from_dict({
            **symbols(), "metadata": self.last_pass_1_metadata,
        })

    def link_semantics(self, document, symbol_table):
        self.pass_2_called = True
        raw = semantics()
        if self.unknown_pass_2:
            raw["relationships"][0]["target_entity_id"] = "unknown-state"
        self.last_pass_2_raw = raw
        resolved = resolve_output_evidence(raw, document)
        resolved["metadata"] = self.last_pass_2_metadata
        return SemanticLinkingResult.from_dict(resolved, document)


def write_source(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source.txt"
    source.write_text(SOURCE, encoding="utf-8")
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({
        "title": "Fixture",
        "publisher": "Fixture",
        "authors": "Fixture",
        "source_url": "https://example.test/source",
        "permanent_url": "https://example.test/source?oldid=1",
        "revision_id": 1,
        "revision_timestamp": "2026-01-01T00:00:00Z",
        "license": "Fixture",
        "license_url": "https://example.test/license",
        "redistribution_basis": "Fixture",
        "committed_source_handling": "Fixture",
        "normalized_sha256": hashlib.sha256(SOURCE.encode()).hexdigest(),
    }), encoding="utf-8")
    return source, metadata


def test_symbol_ids_and_order_are_stable_and_provider_ids_are_not_accepted() -> None:
    first = canonicalize_symbol_table(SymbolDiscoveryProposal.from_dict(symbols()))
    reversed_symbols = {"symbols": list(reversed(symbols()["symbols"]))}
    second = canonicalize_symbol_table(SymbolDiscoveryProposal.from_dict(reversed_symbols))
    assert first == second
    assert [item.id for item in first.entities] == ["measurement", "probability", "quantum-state"]
    assert first.diagnostics["ordering"] == "LEXICOGRAPHIC_STABLE_ENTITY_ID"
    bad = symbols()
    bad["symbols"][0]["id"] = "provider-id"
    with pytest.raises(ValidationError, match="unknown symbol nomination fields"):
        SymbolDiscoveryProposal.from_dict(bad)


def test_duplicate_names_normalize_aliases_but_cross_symbol_alias_conflicts_fail_closed() -> None:
    proposal = symbols()
    proposal["symbols"].append({
        "name": "quantum state",
        "description": "A longer deterministic description for the same concept.",
        "entity_type": "CONCEPT",
        "aliases": ["wave state"],
    })
    table = canonicalize_symbol_table(SymbolDiscoveryProposal.from_dict(proposal))
    state = next(item for item in table.entities if item.id == "quantum-state")
    assert state.aliases == ("state", "wave state")
    assert table.diagnostics["duplicate_nomination_count"] == 1

    conflict = symbols()
    conflict["symbols"][1]["aliases"] = ["state"]
    with pytest.raises(ValidationError, match="conflicts between canonical symbols"):
        canonicalize_symbol_table(SymbolDiscoveryProposal.from_dict(conflict))


def test_pass_2_cannot_create_entities_and_unknown_symbols_fail_closed() -> None:
    document = SourceDocument("doc", SOURCE)
    table = canonicalize_symbol_table(SymbolDiscoveryProposal.from_dict(symbols()))
    raw = resolve_output_evidence(semantics(), document)
    raw["entities"] = []
    with pytest.raises(ValidationError, match="cannot create entities"):
        SemanticLinkingResult.from_dict(raw, document)

    raw.pop("entities")
    raw["relationships"][0]["target_entity_id"] = "missing"
    linking = SemanticLinkingResult.from_dict(raw, document)
    with pytest.raises(SymbolTableViolation, match="unknown frozen symbols") as caught:
        assemble_staged_knowledge_model(document, table, linking)
    assert caught.value.violations[0]["unknown_entity_ids"] == ["missing"]


def test_staged_compilation_assembles_existing_knowledge_model_with_exact_evidence() -> None:
    result = compile_staged_knowledge_model(SOURCE, FixtureStagedExtractor())
    assert isinstance(result.model, KnowledgeModel)
    assert result.model.document.text == SOURCE
    assert len(result.model.entities) == 3
    assert result.model.metadata["compiler_version"] == "spec-012-v1"
    assert KnowledgeModel.from_dict(result.model.to_dict()) == result.model
    assert all(
        span.quote == SOURCE[span.start_char:span.end_char]
        for relationship in result.model.relationships for span in relationship.evidence
    )


def test_pass_2_schema_enumerates_only_frozen_ids() -> None:
    schema = semantic_linking_schema(frozenset({"a", "b"}))
    relationship = schema["properties"]["relationships"]["items"]
    assert relationship["properties"]["source_entity_id"]["enum"] == ["a", "b"]
    assert relationship["properties"]["target_entity_id"]["enum"] == ["a", "b"]
    assert "entities" not in schema["properties"]


class FakeResponses:
    def __init__(self) -> None:
        self.outputs = [symbols(), semantics()]
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        index = len(self.calls) - 1
        return SimpleNamespace(
            output_text=json.dumps(self.outputs[index]),
            id=f"resp_{index + 1}",
            model="gpt-test",
            usage=SimpleNamespace(input_tokens=100 + index, output_tokens=20, total_tokens=120 + index),
        )


def test_openai_staged_adapter_makes_two_store_false_calls_with_frozen_schema() -> None:
    responses = FakeResponses()
    extractor = OpenAIStagedExtractor(
        model="requested", client=SimpleNamespace(responses=responses)
    )
    result = compile_staged_knowledge_model(SOURCE, extractor)
    assert len(responses.calls) == 2
    assert all(call["store"] is False for call in responses.calls)
    assert all(call["reasoning"] == {"effort": "low"} for call in responses.calls)
    endpoint_schema = responses.calls[1]["text"]["format"]["schema"]["properties"]["relationships"]["items"]["properties"]["source_entity_id"]
    assert endpoint_schema["enum"] == ["measurement", "probability", "quantum-state"]
    assert result.model.metadata["symbol_discovery_provider"]["provider_request_id"] == "resp_1"
    assert result.model.metadata["semantic_linking_provider"]["provider_request_id"] == "resp_2"


def test_staged_client_disables_sdk_retries(monkeypatch) -> None:
    calls = []

    def client_factory(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(responses=SimpleNamespace())

    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-secret")
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=client_factory))
    OpenAIStagedExtractor()._client_or_create()
    assert calls == [{"api_key": "test-key-not-a-secret", "max_retries": 0}]


def test_pass_1_failure_is_preserved_and_prevents_pass_2(tmp_path: Path) -> None:
    source, metadata = write_source(tmp_path)
    extractor = FixtureStagedExtractor(fail_pass_1=True)
    output = tmp_path / "failed"
    with pytest.raises(ValidationError, match="Pass 1 failed"):
        run_staged_semantic_evaluation(
            source_path=source,
            source_metadata_path=metadata,
            control_proposal_path=CONTROL,
            output_dir=output,
            extractor_factory=lambda: extractor,
        )
    assert extractor.pass_2_called is False
    history = json.loads((output / "run-history.json").read_text())
    assert len(history["attempts"]) == 1
    assert history["attempts"][0]["rejected_output_preserved"] is True
    assert json.loads((output / "report.json").read_text())["verdict"] == "INCONCLUSIVE"
    assert not (output / "parent.knowledge.json").exists()


def test_pass_2_symbol_violation_preserves_raw_proposal_without_rendering(tmp_path: Path) -> None:
    source, metadata = write_source(tmp_path)
    output = tmp_path / "failed-linking"
    with pytest.raises(SymbolTableViolation, match="unknown frozen symbols"):
        run_staged_semantic_evaluation(
            source_path=source,
            source_metadata_path=metadata,
            control_proposal_path=CONTROL,
            output_dir=output,
            extractor_factory=lambda: FixtureStagedExtractor(unknown_pass_2=True),
        )
    result = json.loads((output / "pass-2-result.json").read_text())
    assert result["raw_proposal"]["relationships"][0]["target_entity_id"] == "unknown-state"
    assert result["symbol_table_violations"][0]["unknown_entity_ids"] == ["unknown-state"]
    assert len(json.loads((output / "run-history.json").read_text())["attempts"]) == 2
    assert not (output / "parent.knowledge.json").exists()
    assert not (output / "parent.representation.json").exists()


def test_evaluation_and_independent_review_finalize_complete_comparison(tmp_path: Path) -> None:
    source, metadata = write_source(tmp_path)
    output = tmp_path / "evaluation"
    initial = run_staged_semantic_evaluation(
        source_path=source,
        source_metadata_path=metadata,
        control_proposal_path=CONTROL,
        output_dir=output,
        extractor_factory=FixtureStagedExtractor,
    )
    assert initial["outcome"] == "PENDING_INDEPENDENT_SEMANTIC_REVIEW"
    assert initial["structural"]["dangling_relationship_endpoint_count"] == 0
    assert initial["grounding"]["exact_evidence_resolution_rate"] == 1.0
    review_path = output / "staged-semantic-review.json"
    review = json.loads(review_path.read_text())
    assert review["review_categories_fixed_before_live_output"] == list(SEMANTIC_REVIEW_CATEGORIES)
    for item in review["items"]:
        item.update({
            "classification": "SUPPORTED",
            "endpoint_precision": "PRECISE",
            "predicate_precision": "PRECISE",
            "notes": "The fixture sentence directly supports the endpoints and predicate.",
        })
    review.update({
        "verdict": "STAGED_BETTER",
        "verdict_rationale": {
            "structural": "The fixture staged model has no dangling endpoints.",
            "grounding": "All fixture source evidence resolves exactly and uniquely.",
            "semantic": "All reviewed fixture items are supported.",
            "cost_complexity": "The extra fixture pass is justified for this fixture only.",
        },
        "reliability_gain_worth_additional_pass_on_this_benchmark": True,
    })
    for item in review["control_defect_comparison"]:
        item.update({
            "staged_status": "FIXED",
            "notes": "The fixture does not reproduce this control defect.",
        })
    review_path.write_text(json.dumps(review), encoding="utf-8")
    final = finalize_staged_semantic_evaluation(output)
    assert final["verdict"] == "STAGED_BETTER"
    assert final["semantic_review"]["staged_precision"] == 1.0
    comparison = json.loads((output / "comparison.json").read_text())
    assert comparison["structural"]["control_observed_dangling_endpoint_failures"] == 2
    assert comparison["structural"]["control_preserved_proposal_dangling_relationship_endpoints"] == 1
    assert comparison["semantic"]["control_semantic_precision"] == pytest.approx(2 / 11)
    assert (output / "parent.structures.json").is_file()
    assert (output / "parent.representation.json").is_file()


def test_control_mapping_preserves_known_spec_011_defects() -> None:
    review = build_control_semantic_review(json.loads(CONTROL.read_text()))
    by_id = {item["id"]: item for item in review["items"]}
    assert by_id["rel-qm-explains-molecules"]["classification"] == "OVERSTATED_CAUSALITY"
    assert by_id["rel-measurement-collapses-state"]["classification"] == "LOSSY_BINARY_FORM"
    assert by_id["rel-tunneling-enables-electron-penetration"]["classification"] == "IMPRECISE_ENDPOINT"
    assert review["supported_item_count"] == 2
