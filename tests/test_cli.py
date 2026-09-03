import json
from pathlib import Path

from knowledge_compiler.cli import main


def test_cli_writes_human_readable_model(tmp_path: Path) -> None:
    fixtures = Path(__file__).parent / "fixtures"
    output = tmp_path / "model.json"
    result = main([
        "translate", str(fixtures / "electromagnetism.txt"),
        "--extractor", "fixture", "--fixture", str(fixtures / "electromagnetism_extraction.json"),
        "--output", str(output),
    ])
    assert result == 0
    raw = output.read_text()
    assert raw.startswith("{\n  \"document\"")
    assert len(json.loads(raw)["relationships"]) == 9


def test_llm_cli_reports_missing_credentials(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    source = tmp_path / "source.txt"
    source.write_text("Some explanatory text.")
    result = main(["translate", str(source), "--extractor", "llm", "--output", str(tmp_path / "model.json")])
    assert result == 1
    assert "OPENAI_API_KEY is required" in capsys.readouterr().err


def test_fixture_cli_requires_explicit_fixture(tmp_path: Path, capsys) -> None:
    source = tmp_path / "source.txt"
    source.write_text("Some explanatory text.")
    result = main(["translate", str(source), "--extractor", "fixture", "--output", str(tmp_path / "model.json")])
    assert result == 1
    assert "--fixture is required" in capsys.readouterr().err


def test_evaluate_cli_reports_missing_credentials(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = main(["evaluate", "--output-dir", str(tmp_path / "run")])
    assert result == 1
    assert "OPENAI_API_KEY is required" in capsys.readouterr().err


def test_detect_structures_cli_is_offline_and_deterministic(tmp_path: Path, capsys) -> None:
    model_path = (
        Path(__file__).parents[1] / "examples" / "evaluations"
        / "spec-003-relationship-semantics-20260903" / "software_architecture.knowledge.json"
    )
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    assert main(["detect-structures", str(model_path), "--output", str(first)]) == 0
    assert main(["detect-structures", str(model_path), "--output", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()
    assert len(json.loads(first.read_text())["structures"]) == 2
    assert "2 structures" in capsys.readouterr().out


def test_detect_structures_cli_rejects_invalid_model(tmp_path: Path, capsys) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"document": {}}')
    assert main(["detect-structures", str(invalid), "--output", str(tmp_path / "out.json")]) == 1
    assert "knowledge-compiler: error:" in capsys.readouterr().err


def test_represent_cli_builds_presentation_json(tmp_path: Path, capsys) -> None:
    root = Path(__file__).parents[1] / "examples" / "evaluations"
    model = root / "spec-003-relationship-semantics-20260903" / "economics.knowledge.json"
    structures = root / "spec-004-structure-detection-20260903" / "economics.structures.json"
    output = tmp_path / "representation.json"
    assert main(["represent", str(model), str(structures), "--output", str(output)]) == 0
    value = json.loads(output.read_text())
    assert len(value["representations"]) == 1
    assert value["representations"][0]["representation_type"] == "CAUSAL_PATH"
    assert "1 representations" in capsys.readouterr().out


def test_prepare_representations_cli_builds_viewer(tmp_path: Path, capsys) -> None:
    output = tmp_path / "review"
    assert main(["prepare-representations", "--output-dir", str(output)]) == 0
    assert (output / "index.html").is_file()
    assert (output / "manifest.json").is_file()
    assert "5/5 domains, provenance complete" in capsys.readouterr().out


def test_prepare_layout_interaction_cli_uses_fixed_spec005_artifacts(tmp_path: Path, capsys) -> None:
    output = tmp_path / "review"
    assert main(["prepare-layout-interaction", "--output-dir", str(output)]) == 0
    report = json.loads((output / "report.json").read_text())
    assert report["fixed_input_baseline"] == "SPEC-005 committed representation artifacts"
    assert report["all_selection_identity_complete"] is True
    assert "5/5 domains, layout and interaction integrity complete" in capsys.readouterr().out


def test_prepare_semantic_navigation_cli_uses_fixed_spec006_artifacts(tmp_path: Path, capsys) -> None:
    output = tmp_path / "review"
    assert main(["prepare-semantic-navigation", "--output-dir", str(output)]) == 0
    report = json.loads((output / "report.json").read_text())
    assert report["fixed_parent_baseline"].startswith("BASELINE-001")
    assert report["all_provenance_truthful"] is True
    assert "2/2 fixtures, semantic-navigation integrity complete" in capsys.readouterr().out
