from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[1]
BASELINE_DOC = ROOT / "baselines" / "BASELINE-001-interface.md"
SCREENSHOTS = ROOT / "baselines" / "BASELINE-001-interface"
EXPECTED_SCREENSHOTS = {
    "economics-causal-overview.jpg",
    "economics-selected-shortage-causes-pressure.jpg",
    "software-architecture-hierarchy-selected-part-of.jpg",
    "electromagnetism-feedback-candidate.jpg",
    "biology-truthful-empty-state.jpg",
}


def test_baseline_document_records_origin_grammar_limitations_and_comparison_rule() -> None:
    text = BASELINE_DOC.read_text()
    assert "comparison baseline, not a frozen final design" in text
    assert "e74412a28c7d4571adb8e5e74cf0a0d5d6270e8b" in text
    assert "59d6cf12dc94cdee77e0f27daf34de916039f239" in text
    assert "click = persistent semantic selection" in text
    assert "hover = temporary preview" in text
    assert "BETTER / SAME / WORSE" in text
    assert "Visual novelty" in text
    assert "broader user population" in text


def test_curated_baseline_contains_only_five_valid_descriptive_jpegs() -> None:
    screenshots = {path.name for path in SCREENSHOTS.iterdir() if path.is_file()}
    assert screenshots == EXPECTED_SCREENSHOTS
    for name in EXPECTED_SCREENSHOTS:
        data = (SCREENSHOTS / name).read_bytes()
        assert data.startswith(b"\xff\xd8\xff")
        assert data.endswith(b"\xff\xd9")
        assert len(data) >= 10_000
