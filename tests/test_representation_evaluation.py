from __future__ import annotations

import json
from pathlib import Path

from knowledge_compiler.representation_evaluation import (
    default_presentation_metadata_path,
    default_spec004_structures_directory,
    prepare_representation_evaluation,
)
from knowledge_compiler.structure_evaluation import default_spec003_models_directory


def prepare(output: Path):
    return prepare_representation_evaluation(
        models_dir=default_spec003_models_directory(),
        structures_dir=default_spec004_structures_directory(),
        output_dir=output,
        metadata_path=default_presentation_metadata_path(),
    )


def test_five_domain_evaluation_is_offline_complete_and_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    report = prepare(first)
    prepare(second)
    assert report["network_or_llm_calls"] is False
    assert report["all_references_valid"] is True
    assert report["all_provenance_complete"] is True
    assert len(report["results"]) == 5
    assert all(item["integrity"]["expected_evidence_excerpt_count"] == item["integrity"]["actual_evidence_excerpt_count"] for item in report["results"])
    assert sorted(path.name for path in first.iterdir()) == sorted(path.name for path in second.iterdir())
    for path in first.iterdir():
        assert path.read_bytes() == (second / path.name).read_bytes()


def test_human_review_template_is_unscored_and_has_three_comparisons(tmp_path: Path) -> None:
    prepare(tmp_path / "evaluation")
    template = json.loads((tmp_path / "evaluation" / "human-review-template.json").read_text())
    assert template["status"] == "NOT_EVALUATED"
    assert template["overall_verdict"] == "NOT_EVALUATED"
    assert set(template["domains"]) == {"software_architecture", "economics", "electromagnetism"}
    assert all(set(item["comparison_inputs"]) == {"source", "knowledge_model", "detected_structures", "rendered_representation"} for item in template["domains"].values())


def test_local_viewer_manifest_and_static_app_load_the_generated_data(tmp_path: Path) -> None:
    directory = tmp_path / "evaluation"
    prepare(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    html = (directory / "index.html").read_text()
    assert len(manifest["domains"]) == 5
    assert all((directory / item["representation"]).is_file() for item in manifest["domains"])
    assert "Representation review" in html
    assert "viewer.js" in html


def test_viewer_javascript_uses_representation_data_without_source_parsing() -> None:
    script = (
        Path(__file__).parents[1] / "src" / "knowledge_compiler" / "viewer_assets" / "viewer.js"
    ).read_text()
    assert 'fetch("manifest.json")' in script
    assert "document.text" not in script
    assert "innerHTML" not in script
