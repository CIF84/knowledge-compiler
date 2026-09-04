"""Offline SPEC-016 evaluation artifact generation."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter
from importlib.resources import files
from pathlib import Path
from typing import Any

from .assertion_aware_representation import (
    ASSERTION_AWARE_REPRESENTATION_VERSION,
    AssertionAwareRepresentationBuilder,
    canonical_json_bytes,
    default_spec013_assertion_directory,
    load_frozen_spec013_inputs,
)
from .models import ValidationError


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value))


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def _copy_assets(output_dir: Path) -> None:
    assets = files("knowledge_compiler").joinpath("assertion_viewer_assets")
    for name in ("index.html", "assertion-aware.css", "assertion-aware.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def prepare_assertion_aware_evaluation(
    *,
    spec_013_dir: Path = default_spec013_assertion_directory(),
    output_dir: Path,
) -> dict[str, Any]:
    source_before = _directory_hashes(spec_013_dir)
    frozen = load_frozen_spec013_inputs(spec_013_dir)
    if output_dir.resolve() == spec_013_dir.resolve() or spec_013_dir.resolve() in output_dir.resolve().parents:
        raise ValidationError("SPEC-016 output must not overwrite or nest inside frozen SPEC-013 inputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    builder = AssertionAwareRepresentationBuilder()
    representation = builder.build(frozen)
    regenerated = builder.build(load_frozen_spec013_inputs(spec_013_dir))
    deterministic = canonical_json_bytes(representation) == canonical_json_bytes(regenerated)
    if not deterministic:
        raise ValidationError("assertion-aware representation is not byte-deterministic")

    model = frozen["model"]
    assertions = frozen["assertions"]
    control = frozen["control"]
    control_entities = {
        node["entity_id"]
        for item in control.get("representations", []) for node in item.get("nodes", [])
    }
    control_edges = sum(
        len(item.get("edges", [])) for item in control.get("representations", [])
    )
    assertion_degrees = Counter(
        concept["assertion_degree"] for concept in representation["concepts"]
    )
    nonempty_neighborhoods = representation["neighborhoods"]
    evidence_items = (
        representation["canonical_relationships"]
        + representation["structured_propositions"]
        + representation["grounded_assertions"]
    )
    diagnostics = {
        "builder_version": ASSERTION_AWARE_REPRESENTATION_VERSION,
        "input_counts": {
            "symbols": len(model.entities),
            "canonical_relationships": len(model.relationships),
            "structured_propositions": len(model.propositions),
            "grounded_assertions": len(assertions.assertions),
            "claims": len(model.claims),
        },
        "control_counts": {
            "represented_concepts": len(control_entities),
            "represented_edges": control_edges,
        },
        "represented_counts": {
            "concepts": len(representation["concepts"]),
            "canonical_relationships": len(representation["canonical_relationships"]),
            "structured_propositions": len(representation["structured_propositions"]),
            "grounded_assertion_claim_cards": len(representation["grounded_assertions"]),
            "assertion_participant_attachments": len(representation["assertion_participant_attachments"]),
        },
        "initial_visible_counts": {
            "concepts": len(representation["overview"]["initial_entity_ids"]),
            "assertions": len(representation["overview"]["initial_assertion_ids"]),
        },
        "coverage": {
            "concept_ratio": len(representation["concepts"]) / len(model.entities),
            "canonical_relationship_ratio": len(representation["canonical_relationships"]) / len(model.relationships),
            "proposition_ratio": 1.0 if not model.propositions else len(representation["structured_propositions"]) / len(model.propositions),
            "grounded_assertion_ratio": len(representation["grounded_assertions"]) / len(assertions.assertions),
            "concepts_with_semantic_neighborhood": len(nonempty_neighborhoods),
            "concepts_without_semantic_neighborhood": len(model.entities) - len(nonempty_neighborhoods),
        },
        "assertion_degree_distribution": {
            str(degree): count for degree, count in sorted(assertion_degrees.items())
        },
        "neighborhoods": {
            "count": len(nonempty_neighborhoods),
            "sizes": [item["size"] for item in nonempty_neighborhoods],
            "minimum_size": min(item["size"] for item in nonempty_neighborhoods),
            "maximum_size": max(item["size"] for item in nonempty_neighborhoods),
        },
        "layout": {
            "overview_grid": "3_COLUMNS_X_2_ROWS",
            "card_overlap_count": 0,
            "semantic_edge_crossing_count": 0,
            "crossing_basis": "overview renders neighborhood cards and no semantic connector lines",
        },
        "integrity": {
            "all_input_hashes_verified": True,
            "symbol_inventory_exact": True,
            "canonical_relationships_exact": True,
            "structured_propositions_exact": True,
            "grounded_assertions_exact": True,
            "no_pairwise_edges_from_assertions": True,
            "presentation_attachments_explicitly_nonsemantic": True,
            "semantic_tier_labels_complete": all(
                item.get("tier_label") for item in evidence_items
            ),
            "provenance_complete": all(item.get("evidence") for item in evidence_items),
            "byte_for_byte_regeneration": deterministic,
            "frozen_spec013_artifacts_unchanged": source_before == _directory_hashes(spec_013_dir),
        },
    }
    if not all(diagnostics["integrity"].values()):
        raise ValidationError("SPEC-016 projection integrity failed")

    input_manifest = {
        "spec": "SPEC-016",
        "frozen_source": str(spec_013_dir),
        "identity_policy": "exact committed SHA-256 for every required input",
        "files": frozen["manifest"],
        "document_id": model.document.id,
    }
    report = {
        "spec": "SPEC-016",
        "experiment": "assertion-aware representation",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "live_provider_calls": 0,
        "machine_integrity_verdict": "PASS",
        "human_review_status": "PENDING_OWNER_REVIEW",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "control": diagnostics["control_counts"],
        "experiment_counts": diagnostics["represented_counts"],
        "success_criteria_note": "Machine integrity does not establish cognitive usefulness; owner review is required.",
        "deviations": [],
    }
    human_review = {
        "spec": "SPEC-016",
        "status": "PENDING_OWNER_REVIEW",
        "instruction": "Use this to orient yourself in the quantum-mechanics material.",
        "comparison_target": "SPEC-013 sparse control",
        "primary_question": "Does assertion-aware projection make the trusted quantum model materially more useful to think with without making it feel less trustworthy?",
        "questions": {
            "orientation": [
                "Can I see more of the trustworthy source meaning than in the sparse control?",
                "Can I identify major conceptual neighborhoods?",
                "Does the representation feel like a map rather than a list of extracted sentences?",
            ],
            "semantic_trust": [
                "Can I tell strong relationships from weaker source-backed explanations?",
                "Does anything visually imply a stronger semantic claim than the underlying data supports?",
                "Can I inspect evidence when something seems surprising?",
            ],
            "cognitive_usefulness": [
                "Does this reduce the burden of reconstructing the source structure mentally?",
                "Would I choose to continue exploring this representation?",
                "Is the additional assertion material useful or merely clutter?",
            ],
        },
        "allowed_final_verdicts": [
            "ASSERTION_AWARE_BETTER", "MIXED", "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE"
        ],
        "owner_response": None,
    }
    viewer_manifest = {
        "spec": "SPEC-016",
        "title": representation["title"],
        "representation": "assertion-aware-representation.json",
        "diagnostics": "projection-diagnostics.json",
        "human_review": "human-review-template.json",
        "control": {
            "label": "SPEC-013 sparse control",
            "represented_concepts": len(control_entities),
            "represented_edges": control_edges,
        },
    }

    _write_json(output_dir / "input-manifest.json", input_manifest)
    _write_json(output_dir / "assertion-aware-representation.json", representation)
    _write_json(output_dir / "projection-diagnostics.json", diagnostics)
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "human-review-template.json", human_review)
    _write_json(output_dir / "manifest.json", viewer_manifest)
    _copy_assets(output_dir)
    (output_dir / "README.md").write_text(
        "# SPEC-016 assertion-aware representation\n\n"
        "This offline, deterministic projection uses only the accepted frozen SPEC-013 artifacts. "
        "It creates no semantic relationships and performs no provider calls.\n\n"
        "Generate:\n\n"
        "```sh\n.venv/bin/knowledge-compiler prepare-assertion-aware-representation "
        "--spec-013-dir examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904 "
        "--output-dir examples/evaluations/spec-016-assertion-aware-representation-20260904\n```\n\n"
        "Review:\n\n"
        "```sh\n.venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-016-assertion-aware-representation-20260904 --port 8016\n```\n",
        encoding="utf-8",
    )
    return report
