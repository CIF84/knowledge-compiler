"""Repeatable five-domain live evaluation harness for SPEC-002."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .models import KnowledgeModel
from .pipeline import compile_knowledge_model

DOMAINS = ("electromagnetism", "software_architecture", "economics", "biology", "history")
REVIEW_DIMENSIONS = (
    "grounding",
    "entity_quality",
    "relationship_quality",
    "coverage",
    "precision",
    "deduplication_quality",
    "vocabulary_fit",
    "cross_domain_usefulness",
)


def default_domains_directory() -> Path:
    return Path(__file__).parents[2] / "tests" / "fixtures" / "domains"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_review_comparison(
    baseline: Mapping[str, Any],
    current: Mapping[str, Any],
    *,
    relationship_changes: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a review comparison without inventing numeric semantic scores."""
    baseline_domains = baseline.get("domains", {})
    current_domains = current.get("domains", {})
    if set(baseline_domains) != set(DOMAINS) or set(current_domains) != set(DOMAINS):
        raise ValueError("baseline and current reviews must cover all evaluation domains")
    domains = {}
    for domain in DOMAINS:
        current_domain = current_domains[domain]
        domains[domain] = {
            "spec_002_assessment": baseline_domains[domain]["review"],
            "spec_003_assessment": current_domain["review"],
            "known_regressions_fixed": current_domain.get("known_regressions_fixed", []),
            "known_regressions_remaining": current_domain.get("known_regressions_remaining", []),
            "new_regressions_introduced": current_domain.get("new_regressions_introduced", []),
            "verdict": current_domain["verdict"],
        }
    return {
        "baseline": "SPEC-002",
        "current": "SPEC-003",
        "relationship_changes": dict(relationship_changes),
        "domains": domains,
        "overall_verdict": current["overall_verdict"],
    }


def run_live_evaluation(
    *,
    extractor_factory: Callable[[], Any],
    fixtures_dir: Path,
    output_dir: Path,
    provider: str,
    model: str,
) -> dict[str, Any]:
    """Evaluate all domains, recording each failure without aborting the run."""
    output_dir.mkdir(parents=True, exist_ok=False)
    started = datetime.now(UTC).isoformat()
    expectations_path = fixtures_dir / "expectations.json"
    expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
    regressions_path = fixtures_dir / "relationship_regressions.json"
    regressions = json.loads(regressions_path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []

    for domain in DOMAINS:
        source_path = fixtures_dir / f"{domain}.txt"
        item: dict[str, Any] = {
            "domain": domain,
            "source_fixture": str(source_path),
            "provider": provider,
            "requested_model": model,
            "started_at": datetime.now(UTC).isoformat(),
            "expectations": expectations[domain],
            "relationship_regressions": regressions[domain],
            "review": {dimension: "NOT_EVALUATED" for dimension in REVIEW_DIMENSIONS},
        }
        try:
            source = source_path.read_text(encoding="utf-8")
            knowledge_model: KnowledgeModel = compile_knowledge_model(
                source,
                extractor_factory(),
                source_metadata={"filename": source_path.name, "domain": domain},
            )
            output_name = f"{domain}.knowledge.json"
            _write_json(output_dir / output_name, knowledge_model.to_dict())
            item.update(
                {
                    "validation_success": True,
                    "output": output_name,
                    "actual_model": knowledge_model.metadata.get("model", model),
                    "prompt_version": knowledge_model.metadata.get("prompt_version"),
                    "provider_request_id": knowledge_model.metadata.get("provider_request_id"),
                    "usage": knowledge_model.metadata.get("usage", {}),
                    "entity_count": len(knowledge_model.entities),
                    "claim_count": len(knowledge_model.claims),
                    "relationship_count": len(knowledge_model.relationships),
                    "failure_reason": None,
                }
            )
        except Exception as exc:
            item.update(
                {
                    "validation_success": False,
                    "output": None,
                    "entity_count": 0,
                    "claim_count": 0,
                    "relationship_count": 0,
                    "failure_reason": f"{type(exc).__name__}: {exc}",
                }
            )
        item["completed_at"] = datetime.now(UTC).isoformat()
        results.append(item)

    report = {
        "spec": "SPEC-003",
        "run_started_at": started,
        "run_completed_at": datetime.now(UTC).isoformat(),
        "provider": provider,
        "requested_model": model,
        "fixtures_dir": str(fixtures_dir),
        "results": results,
    }
    _write_json(output_dir / "report.json", report)
    return report
