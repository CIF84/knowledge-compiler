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
