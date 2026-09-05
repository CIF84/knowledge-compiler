import hashlib
import json
import shutil
from pathlib import Path

import pytest

from knowledge_compiler.baseline004 import (
    BASELINE004_EXECUTABLE_HASHES,
    baseline004_directory,
)
from knowledge_compiler.cli import main
from knowledge_compiler.learner_navigation import DEPTH_ENTITY_ID
from knowledge_compiler.models import ValidationError
from knowledge_compiler.semantic_depth_review_evaluation import (
    OWNER_REVIEW_INSTRUCTION,
    default_spec021_directory,
    prepare_semantic_depth_review_evaluation,
    protected_baseline_hashes,
)


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def test_spec023_reuses_exact_baseline004_executable(tmp_path: Path) -> None:
    output = tmp_path / "review"
    prepare_semantic_depth_review_evaluation(output_dir=output)

    for name, expected_hash in BASELINE004_EXECUTABLE_HASHES.items():
        assert (output / name).read_bytes() == (
            baseline004_directory() / name
        ).read_bytes()
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == expected_hash


def test_spec023_machine_gate_preserves_semantics_and_rejected_item(
    tmp_path: Path,
) -> None:
    output = tmp_path / "review"
    report = prepare_semantic_depth_review_evaluation(output_dir=output)
    gate = _json(output / "machine-gate.json")

    assert report["focus_entity_id"] == DEPTH_ENTITY_ID
    assert report["live_model_or_external_calls"] == 0
    assert report["semantic_changes"] == []
    assert report["representation_algorithm_changes"] == []
    assert report["ui_behavior_changes"] == []
    assert gate["semantic_checks"]["known_rejected_causal_item_not_canonical"]
    assert gate["semantic_checks"]["known_rejected_causal_item_remains_explanatory"]
    assert gate["semantic_checks"]["pairwise_edge_fabrication_count_zero"]
    assert gate["semantic_checks"]["evidence_resolvable"]


def test_spec023_contextual_depth_camera_return_and_interaction_contracts(
    tmp_path: Path,
) -> None:
    output = tmp_path / "review"
    prepare_semantic_depth_review_evaluation(output_dir=output)
    fixture = _json(output / "workspace-fixture.json")
    runtime = _json(output / "machine-gate.json")["runtime_checks"]

    assert fixture["learner_navigation"]["admitted_depth_entity_ids"] == [
        DEPTH_ENTITY_ID
    ]
    assert runtime["global_depth_control_absent"]
    assert runtime["local_depth_affordance_present"]
    assert runtime["camera_state_not_mutated_by_projection"]
    assert runtime["parent_state_snapshot_and_return_present"]
    assert runtime["deeper_items_selectable"]
    assert runtime["evidence_hidden_until_requested_for_explanations"]
    assert runtime["semantic_strength_distinction_present"]


def test_spec023_preserves_all_frozen_baselines(tmp_path: Path) -> None:
    before = protected_baseline_hashes()
    prepare_semantic_depth_review_evaluation(output_dir=tmp_path / "review")
    assert protected_baseline_hashes() == before
    assert all(value["files"] for value in before.values())


def test_spec023_generation_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_semantic_depth_review_evaluation(output_dir=first)
    prepare_semantic_depth_review_evaluation(output_dir=second)
    assert _hashes(first) == _hashes(second)


def test_spec023_rejects_baseline004_substitution(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    shutil.copytree(baseline004_directory(), baseline)
    with (baseline / "learner-grammar.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")

    with pytest.raises(ValidationError, match="identity mismatch"):
        prepare_semantic_depth_review_evaluation(
            output_dir=tmp_path / "rejected",
            baseline_dir=baseline,
        )


def test_spec023_rejects_projection_substitution(tmp_path: Path) -> None:
    projection = tmp_path / "projection"
    shutil.copytree(default_spec021_directory(), projection)
    with (projection / "projection.json").open("a", encoding="utf-8") as stream:
        stream.write("\n")

    with pytest.raises(ValidationError, match="projection identity mismatch"):
        prepare_semantic_depth_review_evaluation(
            output_dir=tmp_path / "rejected",
            spec021_dir=projection,
        )


def test_spec023_refuses_output_inside_frozen_inputs(tmp_path: Path) -> None:
    output = baseline004_directory() / "forbidden-spec023-output"
    assert not output.exists()
    with pytest.raises(ValidationError, match="must be isolated"):
        prepare_semantic_depth_review_evaluation(output_dir=output)
    assert not output.exists()


def test_spec023_cli_prepares_pending_browser_review(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "review"
    assert main(["prepare-semantic-depth-review", "--output-dir", str(output)]) == 0
    assert "browser verification pending" in capsys.readouterr().out
    assert _json(output / "browser-verification.json")["status"] == (
        "PENDING_MANUAL_BROWSER_VERIFICATION"
    )
    assert _json(output / "human-review-template.json")["status"] == (
        "BLOCKED_PENDING_MACHINE_GATE"
    )
    assert _json(output / "human-review-template.json")["instruction"] == (
        OWNER_REVIEW_INSTRUCTION
    )


def test_committed_spec023_review_passes_machine_gate_for_owner_review() -> None:
    evaluation = (
        Path(__file__).parents[1]
        / "examples/evaluations/spec-023-realistic-semantic-depth-20260905"
    )
    report = _json(evaluation / "report.json")
    gate = _json(evaluation / "machine-gate.json")
    browser = _json(evaluation / "browser-verification.json")
    review = _json(evaluation / "human-review-template.json")

    assert report["machine_integrity_verdict"] == "PASS"
    assert report["product_verdict"] == "PENDING_OWNER_REVIEW"
    assert gate["status"] == "PASS"
    assert all(gate["browser_checks"].values())
    assert browser["status"] == "PASS"
    assert browser["console"] == {"errors": [], "result": "PASS", "warnings": []}
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
