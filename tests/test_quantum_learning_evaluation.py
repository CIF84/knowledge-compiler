import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.extractor import ExtractionResult
from knowledge_compiler.models import KnowledgeModel, ValidationError
from knowledge_compiler.openai_extractor import resolve_output_evidence
from knowledge_compiler.quantum_learning_evaluation import (
    run_quantum_learning_evaluation,
    select_zoom_focus,
)
from knowledge_compiler.representation_builder import RepresentationBuilder
from knowledge_compiler.resolution_compiler import (
    FixtureResolutionExtractor,
    ResolutionNomination,
    ResolutionOutcome,
)
from knowledge_compiler.structure_detection import StructureDetector


SOURCE = (
    "Quantum mechanics differs from classical mechanics. "
    "A measurement causes state reduction. "
    "State reduction causes an observed outcome. "
    "The measurement process affects probability."
)


class InlineExtractor:
    def extract(self, document):
        return ExtractionResult.from_dict(
            resolve_output_evidence(parent_extraction(), document), document
        )


def parent_extraction() -> dict:
    return {
        "entities": [
            {"id": "quantum-mechanics", "name": "quantum mechanics", "description": "A physical framework.", "entity_type": "SYSTEM", "aliases": []},
            {"id": "classical-mechanics", "name": "classical mechanics", "description": "A classical framework.", "entity_type": "SYSTEM", "aliases": []},
            {"id": "quantum-state", "name": "quantum state", "description": "A state of a quantum system.", "entity_type": "CONCEPT", "aliases": []},
            {"id": "measurement", "name": "measurement", "description": "A quantum measurement process.", "entity_type": "PROCESS", "aliases": []},
            {"id": "state-reduction", "name": "state reduction", "description": "A measurement-induced state change.", "entity_type": "PROCESS", "aliases": []},
            {"id": "outcome", "name": "observed outcome", "description": "A measurement result.", "entity_type": "OBJECT", "aliases": []},
            {"id": "probability", "name": "probability", "description": "Likelihood of an outcome.", "entity_type": "VARIABLE", "aliases": []},
        ],
        "claims": [],
        "relationships": [
            {"id": "r1", "source_entity_id": "measurement", "relationship_type": "CAUSES", "target_entity_id": "state-reduction", "statement": "Measurement causes state reduction.", "evidence": [{"quote": "A measurement causes state reduction."}], "confidence": 0.9, "origin": "SOURCE"},
            {"id": "r2", "source_entity_id": "state-reduction", "relationship_type": "CAUSES", "target_entity_id": "outcome", "statement": "State reduction causes an outcome.", "evidence": [{"quote": "State reduction causes an observed outcome."}], "confidence": 0.9, "origin": "SOURCE"},
            {"id": "r3", "source_entity_id": "measurement", "relationship_type": "AFFECTS", "target_entity_id": "probability", "statement": "Measurement affects probability.", "evidence": [{"quote": "The measurement process affects probability."}], "confidence": 0.9, "origin": "SOURCE"},
        ],
        "propositions": [],
        "metadata": {"provider": "fixture", "model": "fixture", "prompt_version": "fixture-v1"},
    }


def child_nomination() -> ResolutionNomination:
    return ResolutionNomination(
        ResolutionOutcome.SUCCESS,
        "The source supports a finer measurement neighborhood.",
        {
            "entities": [
                {"id": "measurement", "name": "measurement", "description": "The selected measurement focus.", "entity_type": "PROCESS", "aliases": []},
                {"id": "measurement-interaction", "name": "measurement interaction", "description": "Interaction during measurement.", "entity_type": "PROCESS", "aliases": []},
                {"id": "observed-outcome", "name": "observed outcome", "description": "The resulting observation.", "entity_type": "OBJECT", "aliases": []},
            ],
            "claims": [],
            "relationships": [
                {"id": "c1", "source_entity_id": "measurement", "relationship_type": "CAUSES", "target_entity_id": "measurement-interaction", "statement": "Measurement causes a measurement interaction.", "evidence": [], "confidence": 0.6, "origin": "INFERRED"},
                {"id": "c2", "source_entity_id": "measurement-interaction", "relationship_type": "CAUSES", "target_entity_id": "observed-outcome", "statement": "The interaction causes an observed outcome.", "evidence": [{"quote": "State reduction causes an observed outcome."}], "confidence": 0.9, "origin": "SOURCE"},
            ],
            "propositions": [],
        },
        {"provider": "fixture", "model": "fixture", "prompt_version": "fixture-v1"},
    )


def write_source_inputs(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source.txt"
    source.write_text(SOURCE, encoding="utf-8")
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({
        "title": "Fixture quantum source",
        "publisher": "Fixture publisher",
        "authors": "Fixture author",
        "source_url": "https://example.test/quantum",
        "permanent_url": "https://example.test/quantum?revision=1",
        "revision_id": 1,
        "revision_timestamp": "2026-01-01T00:00:00Z",
        "license": "Fixture license",
        "license_url": "https://example.test/license",
        "redistribution_basis": "Fixture authored for tests.",
        "committed_source_handling": "Fixture only.",
        "normalized_sha256": hashlib.sha256(SOURCE.encode()).hexdigest(),
    }), encoding="utf-8")
    return source, metadata


def test_quantum_evaluation_builds_round_trippable_learning_slice(tmp_path: Path) -> None:
    source, metadata = write_source_inputs(tmp_path)
    output = tmp_path / "evaluation"
    report = run_quantum_learning_evaluation(
        source_path=source,
        source_metadata_path=metadata,
        output_dir=output,
        extractor_factory=InlineExtractor,
        resolution_extractor_factory=lambda: FixtureResolutionExtractor(child_nomination()),
    )
    assert report["processing"]["full_source_processing_succeeded"] is True
    assert report["processing"]["segmentation_required"] is False
    assert report["semantic_zoom"]["focus_label"] == "measurement"
    assert report["semantic_zoom"]["outcome"] == "SUCCESS"
    assert report["parent_immutable"] is True
    assert report["live_call_count"] == 0
    assert report["automatic_retry_count"] == 0
    assert KnowledgeModel.from_dict(json.loads((output / "parent.knowledge.json").read_text()))
    assert KnowledgeModel.from_dict(json.loads((output / "child.knowledge.json").read_text()))
    for name in (
        "parent.structures.json", "parent.representation.json", "resolution-result.json",
        "child.structures.json", "child.representation.json", "generated-exploration.json",
        "report.json", "run-history.json", "repository-semantic-review.json",
        "human-review-template.json", "manifest.json", "index.html", "viewer.css", "viewer.js",
    ):
        assert (output / name).is_file()


def test_zoom_focus_is_selected_from_actual_represented_target_candidates() -> None:
    fixture = InlineExtractor()
    from knowledge_compiler.pipeline import compile_knowledge_model

    model = compile_knowledge_model(SOURCE, fixture)
    structures = StructureDetector().detect(model)
    representation = RepresentationBuilder().build(model, structures)
    entity, view, diagnostics = select_zoom_focus(model, representation)
    assert entity.name == "measurement"
    assert any(node.entity_id == entity.id for node in view.nodes)
    assert diagnostics["fallback_to_non_target_entity"] is False


def test_source_revision_hash_mismatch_fails_before_provider_call(tmp_path: Path) -> None:
    source, metadata = write_source_inputs(tmp_path)
    raw = json.loads(metadata.read_text())
    raw["normalized_sha256"] = "0" * 64
    metadata.write_text(json.dumps(raw))
    called = False

    def factory():
        nonlocal called
        called = True
        return InlineExtractor()

    with pytest.raises(ValidationError, match="fixed revision hash"):
        run_quantum_learning_evaluation(
            source_path=source,
            source_metadata_path=metadata,
            output_dir=tmp_path / "evaluation",
            extractor_factory=factory,
            resolution_extractor_factory=lambda: FixtureResolutionExtractor(child_nomination()),
        )
    assert called is False


def test_failed_parent_validation_preserves_rejected_proposal_and_review_files(
    tmp_path: Path,
) -> None:
    source, metadata = write_source_inputs(tmp_path)

    class InvalidEndpointExtractor(InlineExtractor):
        def extract(self, document):
            result = super().extract(document)
            broken = parent_extraction()
            broken["relationships"][0]["target_entity_id"] = "missing-entity"
            return ExtractionResult.from_dict(
                resolve_output_evidence(broken, document), document
            )

    output = tmp_path / "failed"
    with pytest.raises(ValidationError, match="unknown entities"):
        run_quantum_learning_evaluation(
            source_path=source,
            source_metadata_path=metadata,
            output_dir=output,
            extractor_factory=InvalidEndpointExtractor,
            resolution_extractor_factory=lambda: FixtureResolutionExtractor(child_nomination()),
        )
    assert (output / "rejected-parent-extraction.json").is_file()
    assert (output / "processing-report.json").is_file()
    assert (output / "repository-semantic-review.json").is_file()
    assert (output / "human-review-template.json").is_file()
    assert (output / "README.md").is_file()
    history = json.loads((output / "run-history.json").read_text())
    assert history["attempts"][0]["rejected_output_preserved"] is True
