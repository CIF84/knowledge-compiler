from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from knowledge_compiler.models import Origin, ValidationError
from knowledge_compiler.semantic_navigation import (
    FixtureProvenanceKind,
    default_spec006_representations_directory,
    fixed_exploration_fixtures,
    prepare_semantic_navigation_evaluation,
)


ROOT = Path(__file__).parents[1]
ASSETS = ROOT / "src" / "knowledge_compiler" / "viewer_assets"


def prepare(output: Path):
    return prepare_semantic_navigation_evaluation(
        input_dir=default_spec006_representations_directory(),
        output_dir=output,
    )


def test_fixed_fixtures_target_only_intended_accepted_parent_nodes() -> None:
    fixtures = fixed_exploration_fixtures()
    assert [(item.domain, item.focus_entity_id) for item in fixtures] == [
        ("software_architecture", "api-component"),
        ("economics", "market-price"),
    ]
    assert all(
        item.provenance_kind is FixtureProvenanceKind.EXPERIMENT_FIXTURE_AUTHORED
        for item in fixtures
    )
    assert [len(item.child_representation.nodes) for item in fixtures] == [5, 5]
    assert [len(item.child_representation.edges) for item in fixtures] == [4, 4]
    for fixture in fixtures:
        parent = json.loads(
            (default_spec006_representations_directory() / f"{fixture.domain}.representation.json")
            .read_text()
        )
        parent_ids = {
            node["entity_id"]
            for representation in parent["representations"]
            if representation["id"] == fixture.parent_representation_id
            for node in representation["nodes"]
        }
        assert fixture.focus_entity_id in parent_ids


def test_fixture_authored_relationships_never_masquerade_as_source_spans() -> None:
    for fixture in fixed_exploration_fixtures():
        raw = fixture.to_dict()
        assert raw["provenance_kind"] == "EXPERIMENT_FIXTURE_AUTHORED"
        for edge in fixture.child_representation.edges:
            assert edge.origins == (Origin.INFERRED,)
            assert edge.evidence == ()
        for edge in raw["child_representation"]["edges"]:
            assert edge["origins"] == (Origin.INFERRED,)
            assert edge["evidence"] == ()
            assert edge["provenance_status"] == "INFERRED_NO_SOURCE_EVIDENCE"


def test_fixture_validation_rejects_source_origin_without_source_truth() -> None:
    fixture = fixed_exploration_fixtures()[0]
    edge = replace(fixture.child_representation.edges[0], origins=(Origin.SOURCE,))
    child = replace(fixture.child_representation, edges=(edge, *fixture.child_representation.edges[1:]))
    with pytest.raises(ValidationError, match="cannot masquerade"):
        replace(fixture, child_representation=child)


def test_prepared_comparison_is_complete_offline_and_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    report = prepare(first)
    prepare(second)
    assert report["network_or_llm_calls"] is False
    assert report["all_modes_available"] is True
    assert report["all_return_targets_valid"] is True
    assert report["all_parent_selections_restorable"] is True
    assert report["all_child_selection_identities_complete"] is True
    assert report["all_canonical_directions_preserved"] is True
    assert report["all_provenance_truthful"] is True
    assert report["all_layouts_deterministic"] is True
    assert report["all_contextual_identities_present"] is True
    assert report["baseline_artifacts_byte_preserved"] is True
    assert sorted(path.name for path in first.iterdir()) == sorted(path.name for path in second.iterdir())
    for path in first.iterdir():
        assert path.read_bytes() == (second / path.name).read_bytes()


def test_manifest_exposes_same_child_fixture_to_replacement_and_contextual_modes(tmp_path: Path) -> None:
    output = tmp_path / "evaluation"
    prepare(output)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["modes"] == ["BASELINE", "REPLACEMENT", "CONTEXTUAL"]
    entries = {item["id"]: item for item in manifest["domains"]}
    assert "exploration" in entries["software_architecture"]
    assert "exploration" in entries["economics"]
    assert all("exploration" not in entries[domain] for domain in ("electromagnetism", "biology", "history"))
    fixture = json.loads((output / entries["economics"]["exploration"]).read_text())
    assert fixture["child_representation"]["id"] == "fixture-market-price-response"


def test_navigation_asset_keeps_selection_distinct_and_restores_parent_state() -> None:
    script = (ASSETS / "semantic-navigation.js").read_text()
    for field in (
        "activeResolution", "parentRepresentationId", "focusEntityId", "childRepresentationId",
        "parentSelectionSnapshot", "childSelection",
    ):
        assert field in script
    assert 'group.addEventListener("click", () => selectNode(node.entity_id))' in script
    assert 'explore.addEventListener("click", enterChildResolution)' in script
    assert "selectNode(node.entity_id); enterChildResolution" not in script
    assert 'state.navigation.mode === "BASELINE"' in script
    assert 'state.navigation.mode !== "CONTEXTUAL"' in script
    assert 'state.selectedNodeId = snapshot?.selectedNodeId || null' in script
    assert 'state.selectedEdgeKey = snapshot?.selectedEdgeKey || null' in script
    assert 'state.fixture.parent_representation_id === state.representation?.id' in script
    assert 'state.fixture.focus_entity_id === nodeId' in script
    assert 'edgeButton.dataset.edgeKey = edge.edge_key' in script
    assert 'hit.addEventListener("click", () => selectEdge(edge.edge_key))' in script
    assert "innerHTML" not in script
    assert ".reverse(" not in script


def test_contextual_view_encodes_all_three_identities_and_obvious_return() -> None:
    script = (ASSETS / "semantic-navigation.js").read_text()
    html = (ASSETS / "semantic-navigation.html").read_text()
    css = (ASSETS / "semantic-navigation.css").read_text()
    assert "context.dataset.parentRepresentationId" in script
    assert "context.dataset.focusEntityId" in script
    assert "context.dataset.childRepresentationId" in script
    assert 'back.id = "return-to-parent"' in script
    assert 'explore.id = "explore-selection"' in script
    assert 'id="parent-context"' in html
    assert 'id="context-graph"' in html
    assert ".parent-context[hidden] { display:none; }" in css


def test_baseline_assets_and_captured_representation_data_remain_unchanged(tmp_path: Path) -> None:
    baseline = ROOT / "examples" / "evaluations" / "spec-006-layout-interaction-20260903"
    assert (ASSETS / "viewer.js").read_bytes() == (baseline / "viewer.js").read_bytes()
    assert (ASSETS / "viewer.css").read_bytes() == (baseline / "viewer.css").read_bytes()
    assert (ASSETS / "index.html").read_bytes() == (baseline / "index.html").read_bytes()
    output = tmp_path / "evaluation"
    prepare(output)
    for domain in ("electromagnetism", "software_architecture", "economics", "biology", "history"):
        name = f"{domain}.representation.json"
        assert (output / name).read_bytes() == (baseline / name).read_bytes()


def test_human_template_keeps_product_verdict_unscored_and_owner_led(tmp_path: Path) -> None:
    output = tmp_path / "evaluation"
    prepare(output)
    template = json.loads((output / "human-review-template.json").read_text())
    assert template["status"] == "NOT_EVALUATED"
    assert template["overall_verdict"] == "NOT_EVALUATED"
    assert set(template["domains"]) == {"software_architecture", "economics"}
    assert "spontaneous_reaction" in template["domains"]["economics"]
    assert template["rating_vocabulary"] == ["BETTER", "SAME", "WORSE"]
