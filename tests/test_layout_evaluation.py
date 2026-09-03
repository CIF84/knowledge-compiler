from __future__ import annotations

import json
from pathlib import Path

from knowledge_compiler.layout_evaluation import (
    default_spec005_representations_directory,
    prepare_layout_evaluation,
)
from knowledge_compiler.representation_evaluation import default_spec004_structures_directory
from knowledge_compiler.structure_evaluation import default_spec003_models_directory


ROOT = Path(__file__).parents[1]


def prepare(output: Path):
    return prepare_layout_evaluation(
        input_dir=default_spec005_representations_directory(),
        models_dir=default_spec003_models_directory(),
        structures_dir=default_spec004_structures_directory(),
        output_dir=output,
    )


def test_spec006_evaluation_is_offline_complete_and_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    report = prepare(first)
    prepare(second)
    assert report["network_or_llm_calls"] is False
    assert report["all_semantic_content_unchanged"] is True
    assert report["all_selection_identity_complete"] is True
    assert report["all_canonical_directions_preserved"] is True
    assert report["all_provenance_preserved"] is True
    assert report["all_layouts_have_no_node_overlap"] is True
    assert len(report["results"]) == 5
    assert sorted(path.name for path in first.iterdir()) == sorted(path.name for path in second.iterdir())
    for path in first.iterdir():
        assert path.read_bytes() == (second / path.name).read_bytes()


def test_interaction_map_covers_every_control_edge_and_provenance_identity(tmp_path: Path) -> None:
    output = tmp_path / "evaluation"
    prepare(output)
    mapping = json.loads((output / "interaction-map.json").read_text())
    for domain in mapping["domains"]:
        for representation in domain["representations"]:
            keys = [edge["edge_key"] for edge in representation["relationships"]]
            assert len(keys) == len(set(keys))
            assert all(edge["relationship_ids"] for edge in representation["relationships"])


def test_human_review_template_is_focused_unscored_before_after_comparison(tmp_path: Path) -> None:
    output = tmp_path / "evaluation"
    prepare(output)
    template = json.loads((output / "human-review-template.json").read_text())
    assert template["status"] == "NOT_EVALUATED"
    assert template["overall_verdict"] == "NOT_EVALUATED"
    assert set(template["domains"]) == {
        "electromagnetism", "software_architecture", "economics", "biology", "history"
    }
    assert all(
        set(item["comparison_inputs"]) == {"spec_005", "spec_006"}
        for item in template["domains"].values()
    )


def test_viewer_assets_encode_shared_click_hover_and_reset_state() -> None:
    script = (ROOT / "src" / "knowledge_compiler" / "viewer_assets" / "viewer.js").read_text()
    css = (ROOT / "src" / "knowledge_compiler" / "viewer_assets" / "viewer.css").read_text()
    html = (ROOT / "src" / "knowledge_compiler" / "viewer_assets" / "index.html").read_text()
    for state_field in (
        "selectedNodeId", "selectedEdgeKey", "previewNodeId", "previewEdgeKey"
    ):
        assert state_field in script
    assert 'edgeButton.dataset.edgeKey = edge.edge_key' in script
    assert '"data-edge-key": edge.edge_key' in script
    assert 'hit.addEventListener("mouseenter", () => previewEdge(edge.edge_key))' in script
    assert 'hit.addEventListener("click", () => selectEdge(edge.edge_key))' in script
    assert 'edgeButton.addEventListener("click", () => selectEdge(edge.edge_key))' in script
    assert 'group.addEventListener("click", () => selectNode(node.entity_id))' in script
    assert 'select.addEventListener("change"' in script
    assert 'byId("clear-selection").addEventListener("click", clearSelection)' in script
    assert "is-selected" in css and "is-preview" in css and "is-unrelated" in css
    assert 'id="clear-selection"' in html
    assert "innerHTML" not in script
    assert ".reverse(" not in script
