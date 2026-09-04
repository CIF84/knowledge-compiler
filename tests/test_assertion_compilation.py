from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from knowledge_compiler.assertion_compilation import (
    AssertionExtractionProposal,
    AssertionGroundingError,
    AssertionParticipantError,
    CanonicalizationProposal,
    compile_assertion_semantics,
    ground_assertions,
)
from knowledge_compiler.assertion_evaluation import (
    ASSERTION_REVIEW_CATEGORIES,
    CANONICAL_REVIEW_CATEGORIES,
    finalize_assertion_first_evaluation,
    run_assertion_first_evaluation,
)
from knowledge_compiler.models import Entity, EntityType, KnowledgeModel, SourceDocument, ValidationError
from knowledge_compiler.openai_assertion_compiler import OpenAIAssertionCompiler
from knowledge_compiler.staged_compilation import SymbolTable


SOURCE = (
    "Alpha causes beta. "
    "When alpha exceeds beta, output rises. "
    "Alpha is noteworthy. "
    "Alpha and beta participate in a context the graph cannot preserve."
)


def symbol_table() -> SymbolTable:
    return SymbolTable(
        (
            Entity("alpha", "Alpha", "A variable.", EntityType.VARIABLE),
            Entity("beta", "beta", "A variable.", EntityType.VARIABLE),
            Entity("output", "output", "An outcome.", EntityType.VARIABLE),
        ),
        {"fixture": True},
    )


def assertion_output(*, bad_quote: bool = False, unknown: bool = False) -> dict:
    return {
        "assertions": [
            {
                "statement": "Alpha causes beta.",
                "participant_entity_ids": ["alpha", "missing" if unknown else "beta"],
                "evidence": [{"quote": "absent" if bad_quote else "Alpha causes beta."}],
                "origin": "SOURCE",
            },
            {
                "statement": "Alpha exceeding beta is the condition for output rising.",
                "participant_entity_ids": ["alpha", "beta", "output"],
                "evidence": [{"quote": "When alpha exceeds beta, output rises."}],
                "origin": "SOURCE",
            },
            {
                "statement": "Alpha is noteworthy.",
                "participant_entity_ids": ["alpha"],
                "evidence": [{"quote": "Alpha is noteworthy."}],
                "origin": "SOURCE",
            },
            {
                "statement": "Alpha and beta participate in a context the graph cannot preserve.",
                "participant_entity_ids": ["alpha", "beta"],
                "evidence": [{"quote": "Alpha and beta participate in a context the graph cannot preserve."}],
                "origin": "SOURCE",
            },
        ]
    }


def canonical_output(assertions) -> dict:
    ids = {item.statement: item.id for item in assertions.assertions}
    return {
        "relationships": [{
            "assertion_id": ids["Alpha causes beta."],
            "source_entity_id": "alpha",
            "relationship_type": "CAUSES",
            "target_entity_id": "beta",
            "statement": "Alpha causes beta.",
            "confidence": 0.95,
        }],
        "propositions": [{
            "assertion_id": ids["Alpha exceeding beta is the condition for output rising."],
            "proposition_type": "COMPARISON_CONDITION",
            "statement": "Alpha exceeding beta causes output to rise.",
            "role_bindings": [
                {"role": "LEFT_OPERAND", "entity_id": "alpha"},
                {"role": "RIGHT_OPERAND", "entity_id": "beta"},
                {"role": "OUTCOME", "entity_id": "output"},
            ],
            "relationship_type": "CAUSES",
            "comparison_operator": "GREATER_THAN",
            "confidence": 0.93,
        }],
        "claims": [{
            "assertion_id": ids["Alpha is noteworthy."],
            "statement": "Alpha is noteworthy.",
            "confidence": 0.9,
        }],
        "uncompiled_assertions": [{
            "assertion_id": ids["Alpha and beta participate in a context the graph cannot preserve."],
            "reason": "No existing canonical predicate preserves the contextual participation.",
        }],
    }


class FixtureCompiler:
    def __init__(self, *, bad_quote: bool = False, bad_canonical: bool = False) -> None:
        self.bad_quote = bad_quote
        self.bad_canonical = bad_canonical
        self.canonicalization_called = False
        self.last_assertion_raw = assertion_output(bad_quote=bad_quote)
        self.last_assertion_metadata = {
            "provider": "fixture", "model": "fixture",
            "prompt_version": "fixture-assertions-v1", "usage": {},
        }
        self.last_canonicalization_raw = None
        self.last_canonicalization_metadata = {
            "provider": "fixture", "model": "fixture",
            "prompt_version": "fixture-canonical-v1", "usage": {},
        }

    def extract_assertions(self, document, table):
        return AssertionExtractionProposal.from_dict({
            **self.last_assertion_raw, "metadata": self.last_assertion_metadata,
        })

    def canonicalize_assertions(self, assertions, table):
        self.canonicalization_called = True
        self.last_canonicalization_raw = canonical_output(assertions)
        if self.bad_canonical:
            self.last_canonicalization_raw["uncompiled_assertions"] = []
        return CanonicalizationProposal.from_dict({
            **self.last_canonicalization_raw,
            "metadata": self.last_canonicalization_metadata,
        })


def write_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    source = tmp_path / "source.txt"
    source.write_text(SOURCE, encoding="utf-8")
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({
        "title": "Fixture", "publisher": "Fixture", "authors": "Fixture",
        "source_url": "https://example.test/source",
        "permanent_url": "https://example.test/source?oldid=1", "revision_id": 1,
        "revision_timestamp": "2026-01-01T00:00:00Z", "license": "Fixture",
        "license_url": "https://example.test/license", "redistribution_basis": "Fixture",
        "committed_source_handling": "Fixture",
        "normalized_sha256": hashlib.sha256(SOURCE.encode()).hexdigest(),
    }), encoding="utf-8")
    table = tmp_path / "symbols.json"
    table.write_text(json.dumps(symbol_table().to_dict(), indent=2) + "\n", encoding="utf-8")
    return source, metadata, table


def grounded_fixture():
    document = SourceDocument("doc", SOURCE)
    proposal = AssertionExtractionProposal.from_dict(assertion_output())
    return document, ground_assertions(document, symbol_table(), proposal)


def test_source_assertions_are_grounded_before_semantic_commitment_with_stable_ids() -> None:
    document, first = grounded_fixture()
    second = ground_assertions(
        document, symbol_table(), AssertionExtractionProposal.from_dict(assertion_output())
    )
    assert first == second
    assert all(item.id.startswith("assertion-") for item in first.assertions)
    assert all(span.quote == SOURCE[span.start_char:span.end_char] for item in first.assertions for span in item.evidence)
    assert "relationship_type" not in AssertionExtractionProposal.from_dict(assertion_output()).to_dict()["assertions"][0]


def test_unknown_participant_and_missing_evidence_have_distinct_failures() -> None:
    document = SourceDocument("doc", SOURCE)
    with pytest.raises(AssertionParticipantError, match="unknown frozen symbols"):
        ground_assertions(
            document, symbol_table(),
            AssertionExtractionProposal.from_dict(assertion_output(unknown=True)),
        )
    with pytest.raises(AssertionGroundingError, match="grounding failed"):
        ground_assertions(
            document, symbol_table(),
            AssertionExtractionProposal.from_dict(assertion_output(bad_quote=True)),
        )


def test_assertion_extraction_and_canonicalization_cannot_mint_entities() -> None:
    raw = assertion_output()
    raw["entities"] = []
    with pytest.raises(ValidationError, match="cannot create entities"):
        AssertionExtractionProposal.from_dict(raw)
    raw_canonical = {
        "relationships": [], "propositions": [], "claims": [],
        "uncompiled_assertions": [], "entities": [],
    }
    with pytest.raises(ValidationError, match="cannot create entities"):
        CanonicalizationProposal.from_dict(raw_canonical)


def test_separate_canonicalization_supports_relationship_proposition_claim_and_abstention() -> None:
    document, assertions = grounded_fixture()
    canonical = CanonicalizationProposal.from_dict(canonical_output(assertions))
    result = compile_assertion_semantics(document, symbol_table(), assertions, canonical)
    assert len(result.model.relationships) == 1
    assert len(result.model.propositions) == 1
    assert len(result.model.claims) == 1
    assert len(result.canonicalization.uncompiled_assertions) == 1
    assert KnowledgeModel.from_dict(result.model.to_dict()) == result.model
    assert result.model.entities == symbol_table().entities


def test_every_assertion_must_be_accounted_exactly_once() -> None:
    document, assertions = grounded_fixture()
    raw = canonical_output(assertions)
    raw["uncompiled_assertions"] = []
    with pytest.raises(ValidationError, match="every assertion exactly once"):
        compile_assertion_semantics(
            document, symbol_table(), assertions, CanonicalizationProposal.from_dict(raw)
        )


class FakeResponses:
    def __init__(self) -> None:
        self.calls = []
        self.assertion_output = assertion_output()
        self.canonical_output = None

    def create(self, **kwargs):
        self.calls.append(kwargs)
        output = self.assertion_output if len(self.calls) == 1 else self.canonical_output
        return SimpleNamespace(
            output_text=json.dumps(output), id=f"resp_{len(self.calls)}", model="gpt-test",
            usage=SimpleNamespace(input_tokens=100, output_tokens=20, total_tokens=120),
        )


def test_openai_adapter_enforces_two_distinct_schemas_and_store_false() -> None:
    responses = FakeResponses()
    compiler = OpenAIAssertionCompiler(client=SimpleNamespace(responses=responses), model="requested")
    document = SourceDocument("doc", SOURCE)
    proposal = compiler.extract_assertions(document, symbol_table())
    grounded = ground_assertions(document, symbol_table(), proposal)
    responses.canonical_output = canonical_output(grounded)
    canonical = compiler.canonicalize_assertions(grounded, symbol_table())
    assert len(responses.calls) == 2
    assert all(item["store"] is False for item in responses.calls)
    first_schema = responses.calls[0]["text"]["format"]["schema"]
    assert "relationship_type" not in first_schema["properties"]["assertions"]["items"]["properties"]
    assert "CAUSES" not in responses.calls[0]["instructions"]
    second_schema = responses.calls[1]["text"]["format"]["schema"]
    assert "entities" not in second_schema["properties"]
    assert set(second_schema["properties"]) == {"relationships", "propositions", "claims", "uncompiled_assertions"}
    assert len(canonical.uncompiled_assertions) == 1


def test_assertion_client_disables_sdk_retries(monkeypatch) -> None:
    calls = []

    def client_factory(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(responses=SimpleNamespace())

    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-secret")
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=client_factory))
    OpenAIAssertionCompiler()._client_or_create()
    assert calls == [{"api_key": "test-key-not-a-secret", "max_retries": 0}]


def test_assertion_grounding_failure_is_preserved_and_prevents_canonicalization(tmp_path: Path) -> None:
    source, metadata, table = write_inputs(tmp_path)
    compiler = FixtureCompiler(bad_quote=True)
    output = tmp_path / "failed"
    with pytest.raises(AssertionGroundingError):
        run_assertion_first_evaluation(
            source_path=source, source_metadata_path=metadata, symbol_table_path=table,
            output_dir=output, compiler_factory=lambda: compiler,
        )
    assert compiler.canonicalization_called is False
    result = json.loads((output / "assertion-extraction-result.json").read_text())
    assert result["failure_boundary"] == "ASSERTION_GROUNDING"
    assert result["raw_proposal"] is not None
    assert len(json.loads((output / "run-history.json").read_text())["attempts"]) == 1
    assert not (output / "parent.knowledge.json").exists()


def test_evaluation_reuses_symbol_table_and_finalizes_reviews(tmp_path: Path) -> None:
    source, metadata, table = write_inputs(tmp_path)
    output = tmp_path / "evaluation"
    initial = run_assertion_first_evaluation(
        source_path=source, source_metadata_path=metadata, symbol_table_path=table,
        output_dir=output, compiler_factory=FixtureCompiler,
    )
    assert initial["symbol_table"]["reused_from_spec_012"] is True
    assert (output / "symbol-table.json").read_bytes() == table.read_bytes()
    assert initial["canonicalization"]["uncompiled_assertions"] == 1

    assertion_path = output / "assertion-review.json"
    assertion_review = json.loads(assertion_path.read_text())
    assert assertion_review["review_categories_fixed_before_live_output"] == list(ASSERTION_REVIEW_CATEGORIES)
    for item in assertion_review["items"]:
        item["classification"] = "FAITHFUL"
        item["notes"] = "The fixture assertion preserves its exact source meaning."
        if item["canonical_disposition"] == "UNCOMPILED_ASSERTION":
            item["abstention_quality"] = "APPROPRIATE"
    assertion_path.write_text(json.dumps(assertion_review), encoding="utf-8")

    canonical_path = output / "canonical-semantic-review.json"
    canonical_review = json.loads(canonical_path.read_text())
    assert canonical_review["review_categories_fixed_before_live_output"] == list(CANONICAL_REVIEW_CATEGORIES)
    for item in canonical_review["items"]:
        item.update({
            "classification": "SUPPORTED", "endpoint_precision": "PRECISE",
            "predicate_precision": "PRECISE", "notes": "The fixture supports this mapping.",
        })
    for item in canonical_review["known_control_defects"]:
        item.update({"experiment_status": "ABSTAINED", "notes": "Not present in fixture."})
    canonical_review.update({
        "verdict": "ASSERTION_FIRST_BETTER",
        "verdict_rationale": {
            "assertion_fidelity": "All fixture assertions are faithful.",
            "structural_integrity": "All fixture references validate.",
            "grounding_integrity": "All fixture evidence is exact.",
            "canonical_semantic_precision": "All compiled fixture semantics are supported.",
            "abstention_behavior": "The one fixture abstention is appropriate.",
            "cost_complexity": "The fixture gain justifies the boundary only for this fixture.",
        },
        "semantic_gain_worth_assertion_boundary_on_this_benchmark": True,
    })
    canonical_path.write_text(json.dumps(canonical_review), encoding="utf-8")
    final = finalize_assertion_first_evaluation(output)
    assert final["verdict"] == "ASSERTION_FIRST_BETTER"
    assert final["assertion_fidelity_review"]["faithful_rate"] == 1.0
    assert final["canonical_semantic_review"]["precision"] == 1.0
    comparison = json.loads((output / "control-comparison.json").read_text())
    assert comparison["canonical_semantics"]["spec_012_rejected_proposal_precision"] == 0.375
    assert (output / "parent.structures.json").is_file()
    assert (output / "parent.representation.json").is_file()


def test_canonicalization_failure_is_distinct_and_preserved_without_parent(tmp_path: Path) -> None:
    source, metadata, table = write_inputs(tmp_path)
    output = tmp_path / "canonical-failure"
    with pytest.raises(ValidationError, match="every assertion exactly once"):
        run_assertion_first_evaluation(
            source_path=source, source_metadata_path=metadata, symbol_table_path=table,
            output_dir=output,
            compiler_factory=lambda: FixtureCompiler(bad_canonical=True),
        )
    result = json.loads((output / "canonicalization-result.json").read_text())
    assert result["failure_boundary"] == "CANONICALIZATION"
    assert result["raw_proposal"] is not None
    assert len(json.loads((output / "run-history.json").read_text())["attempts"]) == 2
    assert not (output / "parent.knowledge.json").exists()


def test_source_hash_mismatch_fails_before_provider_call(tmp_path: Path) -> None:
    source, metadata, table = write_inputs(tmp_path)
    raw = json.loads(metadata.read_text())
    raw["normalized_sha256"] = "0" * 64
    metadata.write_text(json.dumps(raw))
    called = False

    def factory():
        nonlocal called
        called = True
        return FixtureCompiler()

    with pytest.raises(ValidationError, match="frozen hash"):
        run_assertion_first_evaluation(
            source_path=source, source_metadata_path=metadata, symbol_table_path=table,
            output_dir=tmp_path / "evaluation", compiler_factory=factory,
        )
    assert called is False


def test_normalized_assertion_artifacts_are_deterministic(tmp_path: Path) -> None:
    source, metadata, table = write_inputs(tmp_path)
    first = tmp_path / "first"
    second = tmp_path / "second"
    for output in (first, second):
        run_assertion_first_evaluation(
            source_path=source, source_metadata_path=metadata, symbol_table_path=table,
            output_dir=output, compiler_factory=FixtureCompiler,
        )
    for name in (
        "symbol-table.json", "grounded-assertions.json", "uncompiled-assertions.json",
        "parent.knowledge.json", "parent.structures.json", "parent.representation.json",
        "assertion-review.json", "canonical-semantic-review.json",
    ):
        assert (first / name).read_bytes() == (second / name).read_bytes()
