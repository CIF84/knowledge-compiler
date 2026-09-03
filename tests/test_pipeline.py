import json
from pathlib import Path

import pytest

from knowledge_compiler.extractor import ExtractionResult, FixtureExtractor
from knowledge_compiler.models import ValidationError
from knowledge_compiler.pipeline import compile_knowledge_model


FIXTURES = Path(__file__).parent / "fixtures"


def test_electromagnetism_fixture_pipeline_is_deterministic_and_coherent() -> None:
    text = (FIXTURES / "electromagnetism.txt").read_text(encoding="utf-8")
    extractor = FixtureExtractor(FIXTURES / "electromagnetism_extraction.json")
    first = compile_knowledge_model(text, extractor)
    second = compile_knowledge_model(text, extractor)
    assert first == second
    names = {entity.name.casefold() for entity in first.entities}
    assert {"charge", "electric field", "magnetic field", "force", "motion", "electromagnetic wave", "light"} <= names
    edges = {(edge.source_entity_id, edge.relationship_type.value, edge.target_entity_id) for edge in first.relationships}
    assert ("charge", "CREATES", "electric-field") in edges
    assert ("changing-magnetic-field", "INDUCES", "electric-field") in edges
    assert ("light", "IS_A", "electromagnetic-wave") in edges
    assert all(span.document_id == first.document.id for item in (*first.claims, *first.relationships) for span in item.evidence)


def test_invalid_fixture_output_is_rejected(tmp_path: Path) -> None:
    fixture = json.loads((FIXTURES / "electromagnetism_extraction.json").read_text())
    fixture["relationships"][0]["evidence"][0]["quote"] = "not the source"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(fixture))
    with pytest.raises(ValidationError, match="mismatch"):
        compile_knowledge_model((FIXTURES / "electromagnetism.txt").read_text(), FixtureExtractor(path))


def test_invalid_raw_extraction_is_rejected_before_state() -> None:
    class BrokenExtractor:
        def extract(self, document):
            return ExtractionResult.from_dict({"relationships": [{"relationship_type": "UNKNOWN"}]}, document)

    with pytest.raises(ValidationError):
        compile_knowledge_model("some text", BrokenExtractor())
