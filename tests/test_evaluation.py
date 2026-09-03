from __future__ import annotations

import json
from pathlib import Path

from knowledge_compiler.evaluation import DOMAINS, REVIEW_DIMENSIONS, run_live_evaluation
from knowledge_compiler.extractor import ExtractionResult


class InferredExtractor:
    def extract(self, document):
        return ExtractionResult((), (), (), {"model": "fake", "prompt_version": "test"})


def test_evaluation_runs_all_domains_and_writes_reviewable_report(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    for domain in DOMAINS:
        (fixtures / f"{domain}.txt").write_text(f"Source for {domain}.")
    (fixtures / "expectations.json").write_text(json.dumps({domain: {"concepts": [], "relationships": []} for domain in DOMAINS}))
    output = tmp_path / "run"

    report = run_live_evaluation(
        extractor_factory=InferredExtractor,
        fixtures_dir=fixtures,
        output_dir=output,
        provider="fake-provider",
        model="fake-model",
    )

    assert len(report["results"]) == 5
    assert all(result["validation_success"] for result in report["results"])
    assert all(set(result["review"]) == set(REVIEW_DIMENSIONS) for result in report["results"])
    assert (output / "report.json").exists()
    assert all((output / f"{domain}.knowledge.json").exists() for domain in DOMAINS)
