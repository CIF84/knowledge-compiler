from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from knowledge_compiler.models import KnowledgeModel, SourceDocument, ValidationError
from knowledge_compiler.openai_extractor import (
    ExtractionError,
    OpenAILLMExtractor,
    build_instructions,
    resolve_evidence_quote,
)
from knowledge_compiler.pipeline import compile_knowledge_model


def provider_output(*, quote: str = "Alpha causes beta.", relationship_type: str = "CAUSES") -> dict:
    return {
        "entities": [
            {"id": "alpha", "name": "Alpha", "description": "The cause.", "entity_type": "CONCEPT", "aliases": []},
            {"id": "beta", "name": "Beta", "description": "The effect.", "entity_type": "CONCEPT", "aliases": []},
        ],
        "claims": [],
        "relationships": [
            {
                "id": "alpha-causes-beta",
                "source_entity_id": "alpha",
                "relationship_type": relationship_type,
                "target_entity_id": "beta",
                "statement": "Alpha causes beta.",
                "evidence": [{"quote": quote}],
                "confidence": 0.95,
                "origin": "SOURCE",
            }
        ],
    }


class FakeResponses:
    def __init__(self, output: dict | None = None, error: Exception | None = None) -> None:
        self.output = output
        self.error = error
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(
            output_text=json.dumps(self.output),
            id="resp_test",
            model="gpt-test",
            usage=SimpleNamespace(input_tokens=100, output_tokens=50, total_tokens=150),
        )


def extractor_for(output: dict | None = None, error: Exception | None = None):
    responses = FakeResponses(output or provider_output(), error)
    return OpenAILLMExtractor(model="requested-model", client=SimpleNamespace(responses=responses)), responses


def test_provider_output_crosses_existing_validation_boundary() -> None:
    extractor, responses = extractor_for()
    model = compile_knowledge_model("Alpha causes beta.", extractor)
    assert isinstance(model, KnowledgeModel)
    evidence = model.relationships[0].evidence[0]
    assert (evidence.start_char, evidence.end_char, evidence.quote) == (0, 18, "Alpha causes beta.")
    assert model.metadata == {
        "extractor": "llm", "provider": "openai", "model": "gpt-test",
        "prompt_version": "spec-003-v1", "provider_request_id": "resp_test",
        "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
    }
    assert responses.kwargs["text"]["format"]["strict"] is True
    assert responses.kwargs["reasoning"] == {"effort": "low"}
    assert responses.kwargs["store"] is False


def test_prompt_prefers_claims_and_contains_canonical_direction_contracts() -> None:
    prompt = build_instructions()
    assert "claim instead of forcing" in prompt
    assert "PART_OF [STRUCTURAL; direction=part_to_whole]" in prompt
    assert "Never use metaphorically for influence" in prompt
    assert "BINDS_TO [INTERACTION; symmetric]" in prompt


def test_quote_resolution_rejects_missing_and_ambiguous_quotes() -> None:
    document = SourceDocument("doc", "same and same")
    with pytest.raises(ValidationError, match="ambiguous"):
        resolve_evidence_quote(document, "same")
    with pytest.raises(ValidationError, match="not found"):
        resolve_evidence_quote(document, "absent")


def test_source_item_without_evidence_is_rejected() -> None:
    output = provider_output()
    output["relationships"][0]["evidence"] = []
    extractor, _ = extractor_for(output)
    with pytest.raises(ValidationError, match="require evidence"):
        compile_knowledge_model("Alpha causes beta.", extractor)


def test_invalid_relationship_type_is_rejected() -> None:
    extractor, _ = extractor_for(provider_output(relationship_type="MAGIC"))
    with pytest.raises(ValidationError, match="must be one of"):
        compile_knowledge_model("Alpha causes beta.", extractor)


def test_unknown_relationship_endpoint_is_rejected_downstream() -> None:
    output = provider_output()
    output["relationships"][0]["target_entity_id"] = "missing"
    extractor, _ = extractor_for(output)
    with pytest.raises(ValidationError, match="unknown entities"):
        compile_knowledge_model("Alpha causes beta.", extractor)


def test_provider_errors_are_clear_and_chained() -> None:
    extractor, _ = extractor_for(error=RuntimeError("rate limited"))
    with pytest.raises(ExtractionError, match="request failed: rate limited"):
        extractor.extract(SourceDocument("doc", "Alpha causes beta."))


def test_missing_credentials_fail_before_sdk_import(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ExtractionError, match="OPENAI_API_KEY"):
        OpenAILLMExtractor().extract(SourceDocument("doc", "text"))


def test_core_models_do_not_import_provider_sdk() -> None:
    import knowledge_compiler.models as models

    assert "openai" not in models.__dict__
