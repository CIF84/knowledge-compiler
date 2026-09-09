import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.cli import main
from knowledge_compiler.diagram_canvas_evaluation import (
    BROWSER_CHECKS,
    FROZEN_SPEC037_DIRECTORY_SHA256,
    OWNER_REVIEW_INSTRUCTION,
    default_spec037_directory,
    finalize_diagram_canvas_evaluation,
    prepare_diagram_canvas_evaluation,
)
from knowledge_compiler.models import ValidationError


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path, *, exclude_lifecycle: bool = False) -> dict[str, str]:
    excluded = {
        "browser-verification.json",
        "human-review-template.json",
        "machine-gate.json",
        "report.json",
    } if exclude_lifecycle else set()
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name not in excluded
    }


def _browser_pass() -> dict:
    capture_names = (
        "mixed_my_map",
        "double_slit_causal",
        "double_slit_focused_relationship",
        "light_hierarchy",
        "software_composition",
        "history_dependency",
        "history_sequence",
        "economics_system",
        "prose_fallback",
    )
    return {
        "status": "PASS",
        "browser": "test fixture",
        "checks": {name: True for name in BROWSER_CHECKS},
        "console": {"errors": [], "warnings": [], "result": "PASS"},
        "deterministic_captures": [
            {"case": name, "result": "PASS"} for name in capture_names
        ],
    }


def test_frozen_spec037_candidate_identity_is_exact() -> None:
    from knowledge_compiler.depth_interaction_evaluation import directory_identity

    assert directory_identity(default_spec037_directory())["aggregate_sha256"] == (
        FROZEN_SPEC037_DIRECTORY_SHA256
    )


def test_candidate_composes_exact_spec037_runtime(tmp_path: Path) -> None:
    before = _hashes(default_spec037_directory())
    output = tmp_path / "candidate"
    report = prepare_diagram_canvas_evaluation(output_dir=output)
    assert before == _hashes(default_spec037_directory())
    assert report["spec037_identity_before"]["aggregate_sha256"] == (
        FROZEN_SPEC037_DIRECTORY_SHA256
    )
    assert report["spec037_identity_before"] == report["spec037_identity_after"]


def test_machine_gate_preserves_prior_runtime_boundaries(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")
    assert all(gate["runtime_checks"].values())
    assert all(gate["semantic_checks"].values())


def test_diagram_layer_has_no_interaction_or_navigation_handlers(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    script = (output / "diagram-canvas.js").read_text()
    assert "addEventListener(" not in script
    assert "__SPEC029_ATOMIC__.dispatch" not in script
    assert "__SPEC033_REVEALED__.select" not in script
    assert "__SPEC033_REVEALED__.reveal" not in script
    assert "__SPEC024_DEPTH__.expand" not in script
    assert "__SPEC037_VISUAL__" not in script
    assert 'getElementById("spec037-visual-contract")' in script


def test_spec037_my_map_assets_are_byte_identical_and_untargeted(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    for name in ("visual-semantic-grammar.css", "visual-semantic-grammar.js"):
        assert (output / name).read_bytes() == (
            default_spec037_directory() / name
        ).read_bytes()
    styles = (output / "diagram-canvas.css").read_text()
    assert all(
        token not in styles
        for token in (
            "revealed-knowledge-map",
            "revealed-node-button",
            "revealed-disclosure",
            "navigation-pane",
        )
    )


def test_layouts_contain_exact_plan_nodes_relationships_and_directions(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    layouts = _json(output / "diagram-layouts.json")["layouts"]
    plans = _json(output / "representation-plans.json")["plans"]
    for key, layout in layouts.items():
        plan = plans[key]
        assert {item["entity_id"] for item in layout["nodes"]} == {
            item["entity_id"] for item in plan["payload"]["nodes"]
        }
        assert {
            (
                tuple(item["relationship_ids"]),
                item["source_entity_id"],
                item["target_entity_id"],
                item["relationship_type"],
                item["direction"],
            )
            for item in layout["relationships"]
        } == {
            (
                tuple(item["relationship_ids"]),
                item["source_entity_id"],
                item["target_entity_id"],
                item["relationship_type"],
                item["direction"],
            )
            for item in plan["payload"]["relationships"]
        }


def test_economics_layout_is_open_directed_system_not_invented_cycle(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    key = "ground:economics:representation-fe3ba90cb8cfa3d6:concept:market-price"
    layout = _json(output / "diagram-layouts.json")["layouts"][key]
    positions = {item["entity_id"]: item for item in layout["nodes"]}
    assert layout["spatial_grammar"] == "causal-system"
    assert len(layout["nodes"]) == 6
    assert len(layout["relationships"]) == 5
    assert positions["supply-reduction"]["y"] < positions["market-price"]["y"]
    assert positions["market-price"]["y"] < positions["quantity-demanded"]["y"]
    assert positions["shortage"]["x"] < positions["supply-reduction"]["x"]
    assert len(
        {(item["label_x"], item["label_y"]) for item in layout["relationships"]}
    ) == 5
    assert not any(
        item["source_entity_id"] == "quantity-demanded"
        and item["target_entity_id"] == "shortage"
        for item in layout["relationships"]
    )


def test_hierarchy_layout_preserves_member_to_parent_direction(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    key = "ground:software_architecture:representation-985e777f01fa9ec8:concept:modular-order-processing-service"
    layout = _json(output / "diagram-layouts.json")["layouts"][key]
    nodes = {item["entity_id"]: item for item in layout["nodes"]}
    assert nodes["modular-order-processing-service"]["role"] == "hierarchy-root"
    assert all(
        item["target_entity_id"] == "modular-order-processing-service"
        and item["relationship_type"] == "PART_OF"
        for item in layout["relationships"]
    )
    assert all(
        nodes[item["source_entity_id"]]["y"]
        > nodes[item["target_entity_id"]]["y"]
        for item in layout["relationships"]
    )
    member_x = sorted(
        item["x"] for item in layout["nodes"] if item["role"] == "hierarchy-member"
    )
    assert min(right - left for left, right in zip(member_x, member_x[1:])) >= 240


def test_sparse_and_rich_layouts_are_content_sensitive(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    layouts = _json(output / "diagram-layouts.json")["layouts"]
    sparse = layouts[
        "ground:electromagnetism:representation-685bf4f0c2881f95:concept:light"
    ]
    rich = layouts[
        "ground:software_architecture:representation-985e777f01fa9ec8:concept:modular-order-processing-service"
    ]
    assert sparse["sparse"] is True
    assert rich["sparse"] is False
    assert sparse["height"] < rich["height"]
    assert len(sparse["relationships"]) == 1
    assert len(rich["relationships"]) == 4


def test_structural_strategies_have_distinct_spatial_grammars(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    report = prepare_diagram_canvas_evaluation(output_dir=output)
    cases = {item["case"]: item for item in report["fixed_evaluation_cases"]}
    assert cases["double_slit_causal"]["spatial_grammar"] == "causal-system"
    assert cases["light_hierarchy"]["spatial_grammar"] == "hierarchy-composition"
    assert cases["history_printing_dependency"]["spatial_grammar"] == "dependency-flow"
    assert cases["history_authorities_sequence"]["spatial_grammar"] == "ordered-sequence"
    assert cases["double_slit_focused_relationship"]["spatial_grammar"] == "focused-connection"
    assert cases["field_reciprocal_mechanism"]["spatial_grammar"] == "reciprocal-cycle"


def test_local_interaction_evidence_preserves_focus_and_revealed_state(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    report = prepare_diagram_canvas_evaluation(output_dir=output)
    interactions = [
        action
        for case in report["fixed_evaluation_cases"]
        for action in case["hover_click_behavior_tested"]
    ]
    assert interactions
    assert all(action["focus_before"] == action["focus_after"] for action in interactions)
    assert all(
        action["revealed_before"] == action["revealed_after"]
        for action in interactions
    )


def test_prose_fallback_has_no_canvas_or_artificial_structure(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    report = prepare_diagram_canvas_evaluation(output_dir=output)
    cases = {item["case"]: item for item in report["fixed_evaluation_cases"]}
    prose = cases["truthful_prose_fallback"]
    assert prose["representation_strategy"] == "CONCISE_PROSE"
    assert prose["spatial_grammar"] == "prose-first"
    assert prose["nodes_rendered"] == []
    assert prose["relationships_rendered"] == []
    assert prose["inspectable_components"] == []


def test_visual_layer_uses_svg_paths_and_semantic_nodes_not_action_cards(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    script = (output / "diagram-canvas.js").read_text()
    styles = (output / "diagram-canvas.css").read_text()
    assert "diagram-wires" in script
    assert "diagram-wire" in script
    assert "marker-end" in script
    assert "diagram-node" in styles
    assert "#exploration-suggestions" in styles
    assert "overflow:visible" in styles
    assert "repeat(6,max-content)" in styles
    assert "data-explanatory-local-key" not in script
    assert "explanatoryLocalKey" in script


def test_evaluation_regeneration_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_diagram_canvas_evaluation(output_dir=first)
    prepare_diagram_canvas_evaluation(output_dir=second)
    assert _hashes(first, exclude_lifecycle=True) == _hashes(
        second, exclude_lifecycle=True
    )


def test_finalize_requires_complete_clean_browser_gate(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["checks"].pop("browser_console_clean")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_diagram_canvas_evaluation(output, invalid)
    report = finalize_diagram_canvas_evaluation(output, _browser_pass())
    assert report["machine_integrity_verdict"] == "PASS"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_finalize_requires_all_deterministic_browser_captures(
    tmp_path: Path,
) -> None:
    output = tmp_path / "candidate"
    prepare_diagram_canvas_evaluation(output_dir=output)
    invalid = _browser_pass()
    invalid["deterministic_captures"].pop()
    with pytest.raises(ValidationError, match="captures are incomplete"):
        finalize_diagram_canvas_evaluation(output, invalid)


def test_cli_prepares_browser_pending_artifact(tmp_path: Path, capsys) -> None:
    output = tmp_path / "candidate"
    assert main(["prepare-diagram-canvas", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec038_artifact_is_ready_for_owner_review() -> None:
    output = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-20260909"
    )
    if not output.exists():
        pytest.skip("generated after focused implementation checks")
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-verification.json")
    review = _json(output / "human-review-template.json")
    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert report["deterministic_regeneration_result"]["result"] == (
        "PASS_BYTE_IDENTICAL"
    )
    assert report["offline_test_result"]["result"] == "PASS"
    assert gate["status"] == "PASS"
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
