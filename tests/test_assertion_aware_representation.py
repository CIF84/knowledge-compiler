from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.assertion_aware_evaluation import prepare_assertion_aware_evaluation
from knowledge_compiler.assertion_aware_representation import (
    FROZEN_INPUT_SHA256,
    AssertionAwareRepresentationBuilder,
    default_spec013_assertion_directory,
    load_frozen_spec013_inputs,
)
from knowledge_compiler.models import ValidationError


INPUT = default_spec013_assertion_directory()


def hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def test_frozen_spec013_identity_and_cross_artifact_validation() -> None:
    frozen = load_frozen_spec013_inputs(INPUT)

    assert {item["filename"]: item["sha256"] for item in frozen["manifest"]} == FROZEN_INPUT_SHA256
    assert len(frozen["symbol_table"].entities) == 41
    assert len(frozen["assertions"].assertions) == 24
    assert len(frozen["model"].relationships) == 3
    assert len(frozen["model"].propositions) == 0
    assert len(frozen["model"].claims) == 21


def test_frozen_input_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    for name in FROZEN_INPUT_SHA256:
        shutil.copyfile(INPUT / name, tmp_path / name)
    (tmp_path / "symbol-table.json").write_bytes((tmp_path / "symbol-table.json").read_bytes() + b" ")

    with pytest.raises(ValidationError, match="hash mismatch"):
        load_frozen_spec013_inputs(tmp_path)


def test_projection_preserves_tiers_provenance_and_nonsemantic_attachments() -> None:
    frozen = load_frozen_spec013_inputs(INPUT)
    value = AssertionAwareRepresentationBuilder().build(frozen)

    assert len(value["concepts"]) == 41
    assert len(value["canonical_relationships"]) == 3
    assert len(value["structured_propositions"]) == 0
    assert len(value["grounded_assertions"]) == 24
    assert {item["tier_label"] for item in value["canonical_relationships"]} == {
        "Established relationship"
    }
    assert {item["tier_label"] for item in value["grounded_assertions"]} == {
        "Source-backed explanation"
    }
    assert all(item["evidence"] for item in value["canonical_relationships"])
    assert all(item["evidence"] for item in value["grounded_assertions"])
    assert all(item["presentation_only"] for item in value["assertion_participant_attachments"])
    assert not any(item["semantic_relationship_created"] for item in value["assertion_participant_attachments"])
    assert set(value) >= {
        "canonical_relationships", "structured_propositions", "grounded_assertions",
        "assertion_participant_attachments",
    }
    assert "relationships" not in {
        key for attachment in value["assertion_participant_attachments"] for key in attachment
    }


def test_salience_density_neighborhood_and_layout_are_deterministic() -> None:
    builder = AssertionAwareRepresentationBuilder()
    first = builder.build(load_frozen_spec013_inputs(INPUT))
    second = builder.build(load_frozen_spec013_inputs(INPUT))

    assert first == second
    assert first["overview"]["initial_entity_ids"] == [
        "quantum-mechanics", "atom", "classical-physics", "electron", "photon",
        "quantum-field-theory",
    ]
    assert len(first["overview"]["initial_entity_ids"]) == 6
    assert len(first["overview"]["initial_assertion_ids"]) == 6
    assert len(first["neighborhoods"]) == 35
    boxes = first["overview"]["layout"]
    for left_index, left in enumerate(boxes):
        for right in boxes[left_index + 1:]:
            overlaps = not (
                left["x"] + left["width"] <= right["x"]
                or right["x"] + right["width"] <= left["x"]
                or left["y"] + left["height"] <= right["y"]
                or right["y"] + right["height"] <= left["y"]
            )
            assert not overlaps


def test_evaluation_generation_is_byte_deterministic_and_preserves_baseline(tmp_path: Path) -> None:
    before = hashes(INPUT)
    left = tmp_path / "left"
    right = tmp_path / "right"
    left_report = prepare_assertion_aware_evaluation(spec_013_dir=INPUT, output_dir=left)
    right_report = prepare_assertion_aware_evaluation(spec_013_dir=INPUT, output_dir=right)

    assert left_report["machine_integrity_verdict"] == "PASS"
    assert left_report["human_review_status"] == "PENDING_OWNER_REVIEW"
    assert left_report["live_provider_calls"] == 0
    assert hashes(left) == hashes(right)
    assert hashes(INPUT) == before
    expected = {
        "input-manifest.json", "assertion-aware-representation.json",
        "projection-diagnostics.json", "report.json", "human-review-template.json",
        "manifest.json", "index.html", "assertion-aware.css", "assertion-aware.js", "README.md",
    }
    assert {path.name for path in left.iterdir()} == expected
    diagnostics = json.loads((left / "projection-diagnostics.json").read_text())
    assert diagnostics["integrity"] == {
        "all_input_hashes_verified": True,
        "byte_for_byte_regeneration": True,
        "canonical_relationships_exact": True,
        "frozen_spec013_artifacts_unchanged": True,
        "grounded_assertions_exact": True,
        "no_pairwise_edges_from_assertions": True,
        "presentation_attachments_explicitly_nonsemantic": True,
        "provenance_complete": True,
        "semantic_tier_labels_complete": True,
        "structured_propositions_exact": True,
        "symbol_inventory_exact": True,
    }


def test_viewer_uses_distinct_non_color_grammar_and_evidence_interaction(tmp_path: Path) -> None:
    prepare_assertion_aware_evaluation(spec_013_dir=INPUT, output_dir=tmp_path)
    html = (tmp_path / "index.html").read_text()
    css = (tmp_path / "assertion-aware.css").read_text()
    javascript = (tmp_path / "assertion-aware.js").read_text()

    assert "Established relationship" in html
    assert "Source-backed explanation" in html
    assert "Structured condition/event" in html
    assert "border: 3px double" in css
    assert "border: 2px dashed" in css
    assert "border-left: 4px solid" in css
    assert "Source evidence" in javascript
    assert 'addEventListener("click"' in javascript
    assert 'addEventListener("mouseenter"' in javascript
