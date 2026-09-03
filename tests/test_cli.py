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
