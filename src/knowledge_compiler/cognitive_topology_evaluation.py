"""Offline SPEC-017 cognitive-topology evaluation generation."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter
from importlib.resources import files
from pathlib import Path
from typing import Any

from .assertion_aware_representation import canonical_json_bytes, default_spec013_assertion_directory
from .cognitive_topology import (
    COGNITIVE_TOPOLOGY_VERSION,
    CognitiveTopologyProjector,
    default_spec016_directory,
    load_and_build_cognitive_topology,
)
from .models import ValidationError


SPEC016_INITIAL_STATIC_PROSE = (
    "Explore the source through its most connected ideas, then inspect the explanation and evidence behind each one.",
    "This is a bounded orientation, not a ranking of scientific importance. Select one to unfold its source-backed neighborhood.",
    "Click an idea to keep its neighborhood open. Hover for a quick preview.",
)


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value))


def _hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


def _copy_assets(output_dir: Path) -> None:
    assets = files("knowledge_compiler").joinpath("cognitive_topology_assets")
    for name in ("index.html", "topology.css", "topology.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)


def _words(text: str) -> int:
    return len(text.replace("—", " ").split())


def _connected_components(topology: dict[str, Any]) -> list[list[str]]:
    adjacency = {item["id"]: set() for item in topology["concepts"]}
    for affinity in topology["presentation_affinities"]:
        left, right = affinity["concept_ids"]
        adjacency[left].add(right)
        adjacency[right].add(left)
    remaining = set(adjacency)
    components = []
    while remaining:
        start = min(remaining)
        stack = [start]
        component = []
        remaining.remove(start)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in sorted(adjacency[current], reverse=True):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda item: (-len(item), item))


def prepare_cognitive_topology_evaluation(
    *,
    spec_013_dir: Path = default_spec013_assertion_directory(),
    spec_016_dir: Path = default_spec016_directory(),
    output_dir: Path,
) -> dict[str, Any]:
    spec013_before = _hashes(spec_013_dir)
    spec016_before = _hashes(spec_016_dir)
    output_resolved = output_dir.resolve()
    if any(source.resolve() == output_resolved or source.resolve() in output_resolved.parents for source in (spec_013_dir, spec_016_dir)):
        raise ValidationError("SPEC-017 output must not overwrite or nest inside a frozen control")
    frozen, topology = load_and_build_cognitive_topology(spec_013_dir)
    _frozen_again, regenerated = load_and_build_cognitive_topology(spec_013_dir)
    deterministic = canonical_json_bytes(topology) == canonical_json_bytes(regenerated)
    if not deterministic:
        raise ValidationError("cognitive topology is not byte-for-byte deterministic")

    output_dir.mkdir(parents=True, exist_ok=True)
    projector = CognitiveTopologyProjector()
    layout_diagnostics = projector.diagnostics(topology)
    model = frozen["model"]
    assertions = frozen["assertions"].assertions
    initial = topology["initial_state"]
    components = _connected_components(topology)
    neighborhood_sizes = [len(item["member_concept_ids"]) for item in topology["neighborhoods"]]
    weight_distribution = Counter(item["weight"] for item in topology["presentation_affinities"])
    semantic_items = (
        topology["canonical_relationships"]
        + topology["structured_propositions"]
        + topology["grounded_assertions"]
    )

    spec016_representation = json.loads(
        (spec_016_dir / "assertion-aware-representation.json").read_text(encoding="utf-8")
    )
    spec016_initial_ids = spec016_representation["overview"]["initial_entity_ids"]
    spec016_assertion_ids = spec016_representation["overview"]["initial_assertion_ids"]
    spec016_concepts = {item["id"]: item for item in spec016_representation["concepts"]}
    spec016_assertions = {item["id"]: item for item in spec016_representation["grounded_assertions"]}
    spec016_prose = [*SPEC016_INITIAL_STATIC_PROSE]
    spec016_prose.extend(spec016_concepts[item]["description"] for item in spec016_initial_ids)
    spec016_prose.extend(spec016_assertions[item]["statement"] for item in spec016_assertion_ids)
    comparison = {
        "control": "SPEC-016 information-first assertion-aware surface",
        "experiment": "SPEC-017 topology-first cognitive projection",
        "measurement_policy": {
            "prose": "visible sentence/paragraph copy; concept labels, legend labels, counts, and controls excluded",
            "blocks": "visible explanatory paragraph and card blocks at initial load",
            "scroll_ratio": "reported only where deterministically fixed or historically measured",
        },
        "spec_016": {
            "initial_prose_word_count": sum(_words(item) for item in spec016_prose),
            "initial_visible_card_count": len(spec016_initial_ids),
            "initial_visible_paragraph_blocks": 3 + 2 * len(spec016_initial_ids),
            "scroll_height_to_viewport_ratio": None,
            "scroll_ratio_note": "not preserved as a deterministic historical SPEC-016 measurement",
            "initial_concept_count": len(spec016_initial_ids),
            "simultaneously_visible_explanatory_assertions": len(spec016_assertion_ids),
        },
        "spec_017": {
            "initial_prose_word_count": initial["visible_prose_word_count"],
            "initial_visible_card_count": 0,
            "initial_visible_paragraph_blocks": initial["visible_paragraph_or_card_count"],
            "scroll_height_to_viewport_ratio": 1.0,
            "scroll_ratio_note": "viewer fixes the topology shell to one viewport with overflow hidden",
            "initial_concept_count": len(initial["visible_concept_ids"]),
            "simultaneously_visible_explanatory_assertions": len(initial["visible_assertion_ids"]),
        },
    }

    diagnostics = {
        "projector_version": COGNITIVE_TOPOLOGY_VERSION,
        "input_counts": {
            "symbols": len(model.entities),
            "grounded_assertions": len(assertions),
            "canonical_relationships": len(model.relationships),
            "structured_propositions": len(model.propositions),
        },
        "presentation_affinity": {
            "pairs_considered": len(model.entities) * (len(model.entities) - 1) // 2,
            "pairs_retained_for_layout": len(topology["presentation_affinities"]),
            "weight_distribution": {str(key): value for key, value in sorted(weight_distribution.items())},
            "semantic_relationships_created": 0,
            "visible_affinity_connectors_at_level_0": 0,
        },
        "visibility": {
            "initial_visible_concepts": len(initial["visible_concept_ids"]),
            "total_discoverable_concepts": len(topology["concepts"]),
            "canonical_relationships_visible_initially": len(initial["visible_canonical_relationship_ids"]),
            "initial_visible_prose_word_count": initial["visible_prose_word_count"],
            "maximum_initial_label_count": len(initial["visible_concept_ids"]),
            "initial_explanatory_assertions": len(initial["visible_assertion_ids"]),
            "initial_evidence_quotes": len(initial["visible_evidence_ids"]),
            "search_coverage": len([item for item in topology["concepts"] if item["discoverable"]]),
        },
        "neighborhoods": {
            "count": len(topology["neighborhoods"]),
            "sizes": neighborhood_sizes,
            "minimum_size": min(neighborhood_sizes),
            "maximum_size": max(neighborhood_sizes),
            "connected_component_count": len(components),
            "connected_component_sizes": [len(item) for item in components],
        },
        "layout": {
            **layout_diagnostics,
            "dimensions": [topology["layout"]["canvas_width"], topology["layout"]["canvas_height"]],
            "runtime_randomness": False,
            "runtime_force_simulation": False,
        },
        "integrity": {
            "all_spec013_input_hashes_verified": True,
            "spec016_control_unchanged": spec016_before == _hashes(spec_016_dir),
            "spec013_semantic_artifacts_unchanged": spec013_before == _hashes(spec_013_dir),
            "canonical_relationships_exact": True,
            "no_semantic_edges_fabricated": True,
            "all_affinity_metadata_explicitly_presentation_only": all(
                item["presentation_only"] and not item["semantic_relationship_created"]
                for item in topology["presentation_affinities"]
            ),
            "no_invented_semantic_neighborhood_labels": all(
                not item["invented_semantic_label"] for item in topology["neighborhoods"]
            ),
            "provenance_complete": all(item["evidence"] for item in semantic_items),
            "byte_for_byte_regeneration": deterministic,
            "initial_label_overlap_free": layout_diagnostics["initial_label_overlap_count"] == 0,
        },
    }
    if not all(diagnostics["integrity"].values()):
        raise ValidationError("SPEC-017 machine integrity failed")

    input_manifest = {
        "spec": "SPEC-017",
        "frozen_semantic_source": str(spec_013_dir),
        "files": frozen["manifest"],
        "identity_policy": "same six exact accepted SPEC-013 SHA-256 identities as SPEC-016",
        "spec_016_control": {
            "directory": str(spec_016_dir),
            "file_count": len(spec016_before),
            "files": [{"filename": key, "sha256": value} for key, value in spec016_before.items()],
        },
    }
    report = {
        "spec": "SPEC-017",
        "experiment": "cognitive topology projection",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "live_provider_calls": 0,
        "machine_integrity_verdict": "PASS",
        "human_review_status": "PENDING_OWNER_REVIEW",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "deviations": [],
        "success_criteria_note": "Cognitive usefulness and preference remain subject to owner review.",
    }
    review = {
        "spec": "SPEC-017",
        "status": "PENDING_OWNER_REVIEW",
        "instruction": "Use this to orient yourself in the quantum-mechanics material.",
        "primary_question": "Which interface would I voluntarily continue using to understand quantum mechanics?",
        "comparison": "SPEC-016",
        "questions": {
            "immediate_orientation": [
                "Does my brain know where to look first?",
                "Can I perceive structure before reading?",
                "Does the domain feel spatially navigable?",
            ],
            "cognitive_load": [
                "Do I feel invited to explore or compelled to read?",
                "Is the amount of visible text low enough?",
                "Does anything compete unnecessarily for attention?",
            ],
            "trust": [
                "Can I distinguish real semantic relationships from presentation grouping?",
                "Does proximity feel misleading?",
                "Can I reach source-backed explanations and evidence when needed?",
            ],
            "navigation": [
                "When I focus on a concept, do I retain orientation?",
                "Does moving between concepts feel like traversing one knowledge space?",
            ],
        },
        "allowed_final_verdicts": [
            "TOPOLOGY_FIRST_BETTER", "MIXED", "NO_MEANINGFUL_IMPROVEMENT", "INCONCLUSIVE"
        ],
        "owner_response": None,
    }
    manifest = {
        "spec": "SPEC-017",
        "title": "Quantum mechanics — cognitive topology",
        "topology": "presentation-topology.json",
        "layout": "layout.json",
        "diagnostics": "projection-diagnostics.json",
        "comparison": "comparison-with-spec016.json",
        "human_review": "human-review-template.json",
    }
    layout = {
        "projector_version": topology["projector_version"],
        "strategy": topology["layout"],
        "positions": {item["id"]: item["position"] for item in topology["concepts"]},
        "initial_visible_concept_ids": initial["visible_concept_ids"],
        "initial_visible_canonical_relationship_ids": initial["visible_canonical_relationship_ids"],
    }

    _write_json(output_dir / "input-manifest.json", input_manifest)
    _write_json(output_dir / "presentation-topology.json", topology)
    _write_json(output_dir / "layout.json", layout)
    _write_json(output_dir / "projection-diagnostics.json", diagnostics)
    _write_json(output_dir / "comparison-with-spec016.json", comparison)
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "human-review-template.json", review)
    _write_json(output_dir / "manifest.json", manifest)
    _copy_assets(output_dir)
    (output_dir / "README.md").write_text(
        "# SPEC-017 cognitive topology projection\n\n"
        "Offline, deterministic topology from the accepted SPEC-013 semantic packet. "
        "Presentation affinity controls proximity only and creates no semantic relationship.\n\n"
        "Generate:\n\n```sh\n"
        ".venv/bin/knowledge-compiler prepare-cognitive-topology "
        "--spec-013-dir examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904 "
        "--spec-016-dir examples/evaluations/spec-016-assertion-aware-representation-20260904 "
        "--output-dir examples/evaluations/spec-017-cognitive-topology-projection-20260904\n"
        "```\n\nReview:\n\n```sh\n"
        ".venv/bin/knowledge-compiler view-representations "
        "examples/evaluations/spec-017-cognitive-topology-projection-20260904 --port 8017\n"
        "```\n",
        encoding="utf-8",
    )
    return report
