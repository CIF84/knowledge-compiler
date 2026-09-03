"""Offline five-domain evaluation for deterministic structure detection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .evaluation import DOMAINS
from .models import KnowledgeModel, ValidationError
from .structure_detection import StructureDetector
from .structures import DetectedStructure, DetectedStructureSet


def default_spec003_models_directory() -> Path:
    return Path(__file__).parents[2] / "examples" / "evaluations" / "spec-003-relationship-semantics-20260903"


def default_structure_expectations_path() -> Path:
    return Path(__file__).parents[2] / "tests" / "fixtures" / "domains" / "structure_expectations.json"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _matches(structure: DetectedStructure, expectation: dict[str, Any]) -> bool:
    if structure.structure_type.value != expectation["structure_type"]:
        return False
    expected_entities = tuple(expectation["entity_ids"])
    if expectation.get("entity_order_matters", True):
        return structure.entity_ids == expected_entities
    return set(structure.entity_ids) == set(expected_entities)


def evaluate_structure_models(
    *, models_dir: Path, output_dir: Path, expectations_path: Path
) -> dict[str, Any]:
    """Detect and assess structures from the committed SPEC-003 models only."""
    output_dir.mkdir(parents=True, exist_ok=False)
    expectations = json.loads(expectations_path.read_text(encoding="utf-8"))
    if set(expectations) != set(DOMAINS):
        raise ValidationError("structure expectations must cover exactly the five domains")
    detector = StructureDetector()
    results = []
    for domain in DOMAINS:
        model_path = models_dir / f"{domain}.knowledge.json"
        model = KnowledgeModel.from_dict(json.loads(model_path.read_text(encoding="utf-8")))
        detected = detector.detect(model)
        output_name = f"{domain}.structures.json"
        _write_json(output_dir / output_name, detected.to_dict())
        expected_results = []
        for expectation in expectations[domain]["expected"]:
            expected_results.append({
                "name": expectation["name"],
                "found": any(_matches(structure, expectation) for structure in detected.structures),
            })
        results.append({
            "domain": domain,
            "input": str(model_path),
            "output": output_name,
            "structure_counts": detected.metadata["structure_counts"],
            "golden_expectations": expected_results,
            "all_golden_expectations_met": all(item["found"] for item in expected_results),
            "known_upstream_limitations": expectations[domain]["known_upstream_limitations"],
        })
    report = {
        "spec": "SPEC-004",
        "detector_version": "spec-004-v1",
        "source_baseline": "SPEC-003",
        "network_or_llm_calls": False,
        "models_dir": str(models_dir),
        "expectations": str(expectations_path),
        "results": results,
    }
    _write_json(output_dir / "report.json", report)
    return report


def load_structure_set(path: Path) -> DetectedStructureSet:
    return DetectedStructureSet.from_dict(json.loads(path.read_text(encoding="utf-8")))
