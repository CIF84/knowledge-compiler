from __future__ import annotations

import hashlib
import json
from pathlib import Path

from knowledge_compiler.assertion_aware_representation import default_spec013_assertion_directory
from knowledge_compiler.cognitive_topology import (
    CognitiveTopologyProjector,
    default_spec016_directory,
    load_and_build_cognitive_topology,
)
from knowledge_compiler.cognitive_topology_evaluation import prepare_cognitive_topology_evaluation


SPEC013 = default_spec013_assertion_directory()
SPEC016 = default_spec016_directory()


def hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def test_affinity_is_deterministic_transparent_and_nonsemantic() -> None:
    frozen, topology = load_and_build_cognitive_topology()
    second = CognitiveTopologyProjector().build(frozen)

    assert topology == second
    assert topology["affinity_policy"]["formula"] == (
        "4*shared_grounded_assertions + 8*canonical_relationship_adjacency + "
        "6*structured_proposition_coparticipation"
    )
    assert len(topology["presentation_affinities"]) == 59
    assert all(item["presentation_only"] for item in topology["presentation_affinities"])
    assert not any(item["semantic_relationship_created"] for item in topology["presentation_affinities"])
    assert all(item["predicate"] is None and item["direction"] is None for item in topology["presentation_affinities"])
    by_pair = {tuple(item["concept_ids"]): item for item in topology["presentation_affinities"]}
    strongest = by_pair[("double-slit-experiment", "interference-pattern")]
    assert strongest["shared_grounded_assertions"] == 2
    assert strongest["canonical_relationship_adjacency"] == 1
    assert strongest["weight"] == 16


def test_canonical_edges_are_exact_and_no_pairwise_semantic_edges_are_fabricated() -> None:
    frozen, topology = load_and_build_cognitive_topology()
    model = frozen["model"]

    expected = {
        (item.id, item.source_entity_id, item.relationship_type.value, item.target_entity_id)
        for item in model.relationships
    }
    actual = {
        (item["id"], item["source_entity_id"], item["relationship_type"], item["target_entity_id"])
        for item in topology["canonical_relationships"]
    }
    assert actual == expected
    assert len(actual) == 3
    assert "relationships" not in topology
    assert all("relationship_type" not in item for item in topology["presentation_affinities"])


def test_neighborhoods_use_only_focal_concept_labels_and_bound_local_density() -> None:
    _frozen, topology = load_and_build_cognitive_topology()

    assert len(topology["neighborhoods"]) == 34
    assert all(item["label_source"] == "FOCAL_TRUSTED_CONCEPT_ONLY" for item in topology["neighborhoods"])
    assert not any(item["invented_semantic_label"] for item in topology["neighborhoods"])
    assert all(2 <= len(item["member_concept_ids"]) <= 8 for item in topology["neighborhoods"])
    assert all(item["member_concept_ids"][0] == item["focus_concept_id"] for item in topology["neighborhoods"])


def test_initial_topology_density_text_budget_and_layout() -> None:
    _frozen, topology = load_and_build_cognitive_topology()
    diagnostics = CognitiveTopologyProjector().diagnostics(topology)
    initial = topology["initial_state"]

    assert len(initial["visible_concept_ids"]) == 10
    assert len(topology["concepts"]) == 41
    assert initial["visible_prose_word_count"] == 8
    assert initial["visible_paragraph_or_card_count"] == 0
    assert initial["visible_assertion_ids"] == []
    assert initial["visible_evidence_ids"] == []
    assert len(initial["visible_canonical_relationship_ids"]) == 2
    assert diagnostics == {"initial_label_overlap_count": 0, "canonical_edge_crossing_count": 0}
    assert topology["layout"]["runtime_simulation"] is False
    assert topology["layout"]["iterations"] == 360


def test_all_assertions_and_evidence_remain_available_with_complete_provenance() -> None:
    frozen, topology = load_and_build_cognitive_topology()

    assert len(topology["grounded_assertions"]) == 24
    assert {item["id"] for item in topology["grounded_assertions"]} == {
        item.id for item in frozen["assertions"].assertions
    }
    assert all(item["visibility"] == "LEVEL_2_EXPLICIT_REQUEST" for item in topology["grounded_assertions"])
    assert all(item["evidence_visibility"] == "LEVEL_3_EXPLICIT_REQUEST" for item in topology["grounded_assertions"])
    assert all(item["evidence"] for item in topology["grounded_assertions"])
    assert all(item["evidence"] for item in topology["canonical_relationships"])
    assert all(item["discoverable"] for item in topology["concepts"])


def test_evaluation_is_byte_deterministic_and_preserves_spec016_control(tmp_path: Path) -> None:
    spec013_before = hashes(SPEC013)
    spec016_before = hashes(SPEC016)
    left = tmp_path / "left"
    right = tmp_path / "right"

    first = prepare_cognitive_topology_evaluation(
        spec_013_dir=SPEC013, spec_016_dir=SPEC016, output_dir=left
    )
    second = prepare_cognitive_topology_evaluation(
        spec_013_dir=SPEC013, spec_016_dir=SPEC016, output_dir=right
    )

    assert first == second
    assert first["machine_integrity_verdict"] == "PASS"
    assert first["human_review_status"] == "PENDING_OWNER_REVIEW"
    assert first["live_provider_calls"] == 0
    assert hashes(left) == hashes(right)
    assert hashes(SPEC013) == spec013_before
    assert hashes(SPEC016) == spec016_before
    expected = {
        "README.md", "comparison-with-spec016.json", "human-review-template.json",
        "index.html", "input-manifest.json", "layout.json", "manifest.json",
        "presentation-topology.json", "projection-diagnostics.json", "report.json",
        "topology.css", "topology.js",
    }
    assert {item.name for item in left.iterdir()} == expected


def test_comparison_reports_topology_first_reduction_without_claiming_product_success(tmp_path: Path) -> None:
    prepare_cognitive_topology_evaluation(
        spec_013_dir=SPEC013, spec_016_dir=SPEC016, output_dir=tmp_path
    )
    comparison = json.loads((tmp_path / "comparison-with-spec016.json").read_text())
    report = json.loads((tmp_path / "report.json").read_text())

    assert comparison["spec_016"]["initial_prose_word_count"] == 223
    assert comparison["spec_017"]["initial_prose_word_count"] == 8
    assert comparison["spec_016"]["simultaneously_visible_explanatory_assertions"] == 6
    assert comparison["spec_017"]["simultaneously_visible_explanatory_assertions"] == 0
    assert comparison["spec_017"]["scroll_height_to_viewport_ratio"] == 1.0
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"


def test_viewer_implements_topology_first_progressive_disclosure_and_search(tmp_path: Path) -> None:
    prepare_cognitive_topology_evaluation(
        spec_013_dir=SPEC013, spec_016_dir=SPEC016, output_dir=tmp_path
    )
    html = (tmp_path / "index.html").read_text()
    css = (tmp_path / "topology.css").read_text()
    javascript = (tmp_path / "topology.js").read_text()

    assert "<svg" in html
    assert "concept-list" not in html
    assert "overflow: hidden" in css
    assert "marker-end: url(#arrow)" in css
    assert "stroke-dasharray" in css
    assert "showConceptInspector" in javascript
    assert "showExplanation" in javascript
    assert "showEvidence" in javascript
    assert "focusConcept(button.dataset.result, true)" in javascript
    assert 'setAttribute("viewBox"' in javascript
    assert "affinity-guide" in javascript
    assert "marker-end" not in javascript.split("function renderAffinityGuides", 1)[1].split("function renderRelationships", 1)[0]
