from __future__ import annotations

import json
from pathlib import Path

from knowledge_compiler.cli import main
from knowledge_compiler.structure_evaluation import (
    default_spec003_models_directory,
    default_structure_expectations_path,
    evaluate_structure_models,
)
from knowledge_compiler.structures import DetectedStructureSet


def test_five_domain_evaluation_runs_offline_and_meets_golden_expectations(tmp_path: Path) -> None:
    output = tmp_path / "evaluation"
    report = evaluate_structure_models(
        models_dir=default_spec003_models_directory(),
        output_dir=output,
        expectations_path=default_structure_expectations_path(),
    )
    assert report["network_or_llm_calls"] is False
    assert len(report["results"]) == 5
    assert all(item["all_golden_expectations_met"] for item in report["results"])
    for item in report["results"]:
        raw = json.loads((output / item["output"]).read_text())
        assert DetectedStructureSet.from_dict(raw).source_document_id


def test_structure_evaluation_cli(tmp_path: Path, capsys) -> None:
    output = tmp_path / "evaluation"
    assert main(["evaluate-structures", "--output-dir", str(output)]) == 0
    assert "5/5 domains met expectations" in capsys.readouterr().out
