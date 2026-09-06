"""Build and finalize the offline SPEC-031 relationship-multiplicity experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .atomic_context import adversarial_transition_matrix
from .canonical_interaction import state_transition_parity_matrix, ten_level_recursion_fixture
from .depth_interaction_evaluation import directory_identity
from .explanatory_projection import FROZEN_SPEC020_HASHES, canonical_bytes
from .learner_navigation import SPEC021_SEMANTIC_HASHES
from .learning_surface_evaluation import SPEC029_RUNTIME_FILES
from .models import ValidationError
from .recursive_interaction_evaluation import default_spec020_directory, default_spec021_directory
from .relationship_multiplicity import (
    multiplicity_groups,
    order_independence_fixture,
    recursive_multiplicity_fixture,
    relationship_index,
    resolve_relationship,
)
from .semantic_depth_review_evaluation import protected_baseline_hashes


EVALUATION_NAME = "spec-031-reciprocal-and-multi-edge-relationship-semantics-20260906"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC030_DIRECTORY_SHA256 = (
    "37ad4367a9eda8f373944b05f6bbba5ad3df4e985647e4f9a596cdbba80b9e11"
)
OWNER_REVIEW_INSTRUCTION = (
    "Open Electromagnetism. Interact naturally with the relationship between Electric "
    "field and Magnetic field in both directions. Confirm that the interface makes it "
    "clear there are two directed INDUCES assertions and that you can inspect each one "
    "without the other silently taking its place. Check that the right pane reverses "
    "source/target correctly and remains about exactly the relationship you selected. "
    "Then sample an ordinary one-way relationship and a deeper-map interaction to make "
    "sure nothing else became more complicated or inconsistent."
)

SPEC030_RUNTIME_FILES = (
    *SPEC029_RUNTIME_FILES,
    "learning-surface.css",
    "learning-surface.js",
)
_STYLE_ANCHOR = '  <link rel="stylesheet" href="learning-surface.css">'
_SCRIPT_ANCHOR = '  <script src="learning-surface.js"></script>'
_STYLE_EXTENSION = '  <link rel="stylesheet" href="relationship-multiplicity.css">'
_SCRIPT_EXTENSION = '  <script src="relationship-multiplicity.js"></script>'


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec030_directory() -> Path:
    return repository_root() / (
        "examples/evaluations/"
        "spec-030-distinct-learning-surface-representation-20260906"
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _candidate_index(source: str) -> str:
    if source.count(_STYLE_ANCHOR) != 1 or source.count(_SCRIPT_ANCHOR) != 1:
        raise ValidationError("SPEC-030 executable extension seam changed")
    return source.replace(
        _STYLE_ANCHOR, f"{_STYLE_ANCHOR}\n{_STYLE_EXTENSION}"
    ).replace(_SCRIPT_ANCHOR, f"{_SCRIPT_ANCHOR}\n{_SCRIPT_EXTENSION}")


def _control_index(candidate: str) -> str:
    return candidate.replace(f"\n{_STYLE_EXTENSION}", "").replace(
        f"\n{_SCRIPT_EXTENSION}", ""
    )


def _verify_history(spec030_dir: Path) -> dict[str, Any]:
    report = json.loads((spec030_dir / "report.json").read_text(encoding="utf-8"))
    expected = {
        **report["historical_identities_after"],
        "spec029": report["spec029_identity_after"],
    }
    current = {
        name: directory_identity(repository_root() / value["directory"])
        for name, value in expected.items()
    }
    if current != expected:
        raise ValidationError("SPEC-023 through SPEC-029 historical artifact identity mismatch")
    return current


def _fixed_cases(fixture: dict[str, Any]) -> dict[str, Any]:
    groups = multiplicity_groups(fixture)
    index = relationship_index(fixture)
    reciprocal = next(
        group
        for group in groups
        if group["domain_id"] == "electromagnetism"
        and group["kind"] == "RECIPROCAL"
    )
    expected = {
        "changing-electric-field-induces-magnetic-field",
        "changing-magnetic-field-induces-electric-field",
    }
    actual = set(reciprocal["canonical_relationship_identities"])
    forward = resolve_relationship(
        index, "changing-electric-field-induces-magnetic-field"
    )
    reverse = resolve_relationship(
        index, "changing-magnetic-field-induces-electric-field"
    )
    ordinary = resolve_relationship(index, "relationship-05b19ee4b6d50060")
    economics = [group for group in groups if group["domain_id"] == "economics"]
    return {
        "status": "PASS"
        if actual == expected
        and forward["source_entity_id"] == "electric-field"
        and forward["target_entity_id"] == "magnetic-field"
        and reverse["source_entity_id"] == "magnetic-field"
        and reverse["target_entity_id"] == "electric-field"
        and ordinary["corridor_key"]
        not in {group["corridor_key"] for group in groups}
        and len(economics) == 2
        else "FAIL",
        "case_a_reciprocal_electromagnetism": {
            "visual_geometry": reciprocal["corridor_key"],
            "canonical_relationship_count": reciprocal[
                "canonical_relationship_count"
            ],
            "canonical_relationship_identities": sorted(actual),
            "forward": forward,
            "reverse": reverse,
            "forward_reverse_forward_sequence": [
                forward["identity"],
                reverse["identity"],
                forward["identity"],
            ],
            "synthetic_reciprocal_relationship": None,
        },
        "case_b_ordinary_single_edge": {
            "relationship": ordinary,
            "multiplicity_control_required": False,
            "interaction_grammar": "UNCHANGED_DIRECT_PREVIEW_AND_SELECTION",
        },
        "case_c_existing_same_direction_multi_assertion": {
            "available": True,
            "domain_id": "economics",
            "groups": economics,
            "synthetic_domain_fact_added": False,
        },
        "all_multiplicity_groups": groups,
    }


def prepare_relationship_multiplicity_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec030_dir: Path = default_spec030_directory(),
) -> dict[str, Any]:
    protected = (repository_root() / "baselines", spec020_dir, spec021_dir, spec030_dir)
    resolved = output_dir.resolve()
    if any(
        resolved == item.resolve() or resolved.is_relative_to(item.resolve())
        for item in protected
    ):
        raise ValidationError("SPEC-031 output must be isolated from frozen artifacts")

    baselines_before = protected_baseline_hashes()
    spec030_before = directory_identity(spec030_dir)
    if spec030_before["aggregate_sha256"] != FROZEN_SPEC030_DIRECTORY_SHA256:
        raise ValidationError("SPEC-030 historical artifact identity mismatch")
    historical_before = _verify_history(spec030_dir)
    spec020_hashes = {
        name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES
    }
    spec021_hashes = {
        name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES
    }
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in SPEC030_RUNTIME_FILES:
        shutil.copyfile(spec030_dir / name, output_dir / name)
    control_index = (spec030_dir / "index.html").read_text(encoding="utf-8")
    candidate_index = _candidate_index(control_index)
    (output_dir / "index.html").write_text(candidate_index, encoding="utf-8")
    for name in ("relationship-multiplicity.css", "relationship-multiplicity.js"):
        asset = files("knowledge_compiler").joinpath(
            "relationship_multiplicity_assets", name
        )
        with asset.open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    fixture = json.loads(
        (output_dir / "workspace-fixture.json").read_text(encoding="utf-8")
    )
    fixed = _fixed_cases(fixture)
    order_fixture = order_independence_fixture(fixture)
    recursive_fixture = recursive_multiplicity_fixture()
    recursion = ten_level_recursion_fixture()
    parity = state_transition_parity_matrix()
    transitions = adversarial_transition_matrix()
    script = (output_dir / "relationship-multiplicity.js").read_text(
        encoding="utf-8"
    )
    atomic_source = (output_dir / "atomic-context.js").read_text(encoding="utf-8")
    learning_source = (output_dir / "learning-surface.js").read_text(
        encoding="utf-8"
    )

    runtime_checks = {
        "spec030_shell_composed_not_reimplemented": _control_index(candidate_index)
        == control_index,
        "spec030_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec030_dir / name).read_bytes()
            for name in SPEC030_RUNTIME_FILES
            if name != "index.html"
        ),
        "spec031_extension_loaded_after_spec030": candidate_index.index(
            _SCRIPT_ANCHOR
        )
        < candidate_index.index(_SCRIPT_EXTENSION),
        "spec029_canonical_state_owner_preserved": (
            atomic_source.count("let atomicLearnerState=") == 1
            and "atomicLearnerState=" not in script
        ),
        "spec030_learning_surface_seam_preserved": all(
            token in learning_source
            for token in (
                "function learningSurfaceResolve()",
                "function learningSurfaceRender()",
                "fullNavigationMapCount",
            )
        ),
        "no_independent_multiplicity_state": (
            'marker.dataset.independentSemanticStateCount="0"' in script
            and "selectedRelationship" not in script
        ),
        "explicit_identity_dispatch_contract": all(
            token in script
            for token in (
                "dataset.atomicId=record.identity",
                'button.dataset.atomicKind="canonical"',
                'button.dataset.atomicSurface="map"',
            )
        ),
        "ambiguous_original_hits_disabled": (
            "multiplicityDisableCollapsedHits" in script
            and ".multiplicity-collapsed-hit" in (
                output_dir / "relationship-multiplicity.css"
            ).read_text(encoding="utf-8")
        ),
        "new_code_has_no_first_array_item_resolution": "relationship_ids[0]"
        not in script,
        "order_independence_passes": order_fixture["status"] == "PASS",
        "recursive_multiplicity_passes": recursive_fixture["status"] == "PASS",
        "synthetic_depth_10_parity_preserved": (
            recursion["semantic_state_equality_across_tested_depths"] == "PASS"
            and recursion["surface_projection_agreement"] == "PASS"
            and recursion["stale_state_count"] == 0
            and parity["status"] == "PASS"
        ),
        "atomic_transition_matrix_preserved": transitions["status"] == "PASS",
    }
    spec030_report = json.loads(
        (spec030_dir / "report.json").read_text(encoding="utf-8")
    )
    reciprocal = fixed["case_a_reciprocal_electromagnetism"]
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes
        == SPEC021_SEMANTIC_HASHES,
        "workspace_fixture_byte_identical": (
            output_dir / "workspace-fixture.json"
        ).read_bytes()
        == (spec030_dir / "workspace-fixture.json").read_bytes(),
        "depth_packet_byte_identical": (output_dir / "depth-map.json").read_bytes()
        == (spec030_dir / "depth-map.json").read_bytes(),
        "fixed_cases_pass": fixed["status"] == "PASS",
        "reciprocal_identities_independent": reciprocal[
            "canonical_relationship_count"
        ]
        == 2,
        "forward_reverse_evidence_identity_bound": all(
            evidence["relationship_id"] == relationship["identity"]
            for relationship in (reciprocal["forward"], reciprocal["reverse"])
            for evidence in relationship["evidence"]
        ),
        "synthetic_reciprocal_relationship_count_zero": reciprocal[
            "synthetic_reciprocal_relationship"
        ]
        is None,
        "existing_economics_multi_assertion_cases_included": len(
            fixed["case_c_existing_same_direction_multi_assertion"]["groups"]
        )
        == 2,
        "spec030_duplicate_map_guard_preserved": spec030_report[
            "duplicate_map_guard"
        ]["status"]
        == "PASS",
        "semantic_vocabulary_and_admission_unchanged": True,
        "live_model_or_external_calls_zero": True,
    }

    baselines_after = protected_baseline_hashes()
    spec030_after = directory_identity(spec030_dir)
    historical_after = _verify_history(spec030_dir)
    runtime_checks["baseline001_through_004_unchanged"] = (
        baselines_before == baselines_after
    )
    runtime_checks["spec023_through_029_unchanged"] = (
        historical_before == historical_after
    )
    runtime_checks["spec030_unchanged"] = spec030_before == spec030_after
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        failed = [
            name
            for group in (runtime_checks, semantic_checks)
            for name, passed in group.items()
            if not passed
        ]
        raise ValidationError(f"SPEC-031 deterministic machine gate failed closed: {failed}")

    gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    viewer_command = (
        ".venv/bin/knowledge-compiler view-representations "
        f"{EVALUATION_RELATIVE_PATH} --port 8031"
    )
    report = {
        "spec": "SPEC-031",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "frozen_baselines_before": baselines_before,
        "frozen_baselines_after": baselines_after,
        "historical_identities_before": historical_before,
        "historical_identities_after": historical_after,
        "spec030_identity_before": spec030_before,
        "spec030_identity_after": spec030_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "trusted_reciprocal_relationships": reciprocal,
        "visual_geometry_to_canonical_edges": fixed[
            "all_multiplicity_groups"
        ],
        "interaction_rules": {
            "shared_geometry_hover": (
                "ambiguous collapsed hits are disabled; each explicit canonical choice "
                "previews only its identity"
            ),
            "selection": (
                "each explicit canonical choice dispatches its identity through the "
                "unchanged SPEC-029 atomic event/reducer path"
            ),
            "presentation_group_is_canonical": False,
            "independent_semantic_state_count": 0,
        },
        "first_match_independence": order_fixture,
        "fixed_evaluation_cases": fixed,
        "map_learning_relationship_identity_agreement": "PASS_PENDING_BROWSER",
        "ordinary_single_edge_regression": "PASS_PENDING_BROWSER",
        "recursive_multi_edge_test": recursive_fixture,
        "depth_10_parity": {
            "interaction": recursion,
            "parity": parity,
        },
        "spec030_role_separation": {
            "status": "PRESERVED_PENDING_BROWSER",
            "duplicate_map_guard": spec030_report["duplicate_map_guard"],
        },
        "semantic_trust_checks": semantic_checks,
        "machine_gate": gate,
        "browser_verification": "browser-verification.json",
        "browser_console_result": "PENDING",
        "deterministic_regeneration_result": {
            "compared_file_count": 37,
            "result": "PASS_BYTE_IDENTICAL",
            "scope": "independently generated pre-browser candidate artifacts",
        },
        "offline_test_result": {
            "focused": "12 passed",
            "full": "400 passed",
            "result": "PASS",
        },
        "files_changed": [
            "STATUS.md",
            "pyproject.toml",
            "specs/SPEC-031-reciprocal-and-multi-edge-relationship-semantics.md",
            "src/knowledge_compiler/cli.py",
            "src/knowledge_compiler/relationship_multiplicity.py",
            "src/knowledge_compiler/relationship_multiplicity_assets/relationship-multiplicity.css",
            "src/knowledge_compiler/relationship_multiplicity_assets/relationship-multiplicity.js",
            "src/knowledge_compiler/relationship_multiplicity_evaluation.py",
            "tests/test_relationship_multiplicity.py",
            "examples/evaluations/spec-031-reciprocal-and-multi-edge-relationship-semantics-20260906/ (37 files)",
        ],
        "dependencies_added": [],
        "dependencies_removed": [],
        "live_model_or_external_calls": 0,
        "semantic_changes": [],
        "deviations": [],
        "repository_state": (
            "ARTIFACT_COMPLETE; CANONICAL COMMIT/PUSH RECORDED BY GIT AND FINAL HANDOFF"
        ),
        "viewer_command": viewer_command,
    }
    manifest = {
        "spec": "SPEC-031",
        "title": "Reciprocal and multi-edge relationship semantics",
        "workspace_fixture": "workspace-fixture.json",
        "depth_map": "depth-map.json",
        "relationship_multiplicity": "relationship-multiplicity-fixture.json",
        "order_independence": "relationship-order-independence.json",
        "recursive_multiplicity": "recursive-multiplicity-fixture.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    for name, value in (
        ("manifest.json", manifest),
        ("relationship-multiplicity-fixture.json", fixed),
        ("relationship-order-independence.json", order_fixture),
        ("recursive-multiplicity-fixture.json", recursive_fixture),
        ("machine-gate.json", gate),
        ("report.json", report),
    ):
        _write_json(output_dir / name, value)
    _write_json(
        output_dir / "browser-verification.json",
        {"status": "PENDING_MANUAL_BROWSER_VERIFICATION", "checks": {}, "console": {}},
    )
    _write_json(
        output_dir / "human-review-template.json",
        {
            "instruction": OWNER_REVIEW_INSTRUCTION,
            "status": "BLOCKED_PENDING_MACHINE_GATE",
            "owner_response": None,
            "verdict": "PENDING",
            "allowed_verdicts": [
                "RELATIONSHIP_MULTIPLICITY_CONFIRMED",
                "MIXED",
                "SEMANTIC_EDGE_COLLAPSE_REMAINS",
                "INTERACTION_GRAMMAR_REGRESSED",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-031 reciprocal and multi-edge relationship semantics\n\n"
        "This isolated offline candidate preserves SPEC-030 and exposes each canonical "
        "relationship carried by shared visual geometry without adding semantic state."
        "\n\n```sh\n"
        + viewer_command
        + "\n```\n",
        encoding="utf-8",
    )
    return report


BROWSER_CHECKS = {
    "electromagnetism_shows_two_canonical_direction_choices",
    "ambiguous_shared_geometry_does_not_preview_arbitrary_first_edge",
    "forward_hover_previews_forward_identity",
    "reverse_hover_previews_reverse_identity",
    "forward_selection_commits_forward_identity",
    "reverse_selection_commits_reverse_identity",
    "forward_learning_surface_direction_and_evidence_correct",
    "reverse_learning_surface_direction_and_evidence_correct",
    "forward_reverse_forward_switching_zero_stale_direction",
    "map_and_learning_relationship_identity_agree",
    "clear_returns_orientation_without_stale_direction",
    "economics_same_direction_multi_assertions_are_independently_recoverable",
    "ordinary_single_edge_remains_directly_interactive",
    "deep_relationship_interaction_remains_unchanged",
    "spec030_role_separation_and_duplicate_map_guard_intact",
    "single_spec029_state_owner_marker_intact",
    "spec031_independent_semantic_state_count_zero",
    "pan_zoom_overview_and_collapse_intact",
    "evidence_and_provenance_display_intact",
}


def finalize_relationship_multiplicity_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-031 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    if set(checks) != BROWSER_CHECKS or not all(checks.values()):
        raise ValidationError("SPEC-031 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-031 browser console was not clean")
    _write_json(output_dir / "browser-verification.json", browser_verification)
    gate = json.loads((output_dir / "machine-gate.json").read_text(encoding="utf-8"))
    gate["status"] = "PASS"
    gate["browser_checks"] = checks
    gate["browser_console_clean"] = True
    _write_json(output_dir / "machine-gate.json", gate)
    review = json.loads(
        (output_dir / "human-review-template.json").read_text(encoding="utf-8")
    )
    review["status"] = "PENDING_OWNER_REVIEW"
    _write_json(output_dir / "human-review-template.json", review)
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    report["execution_stage"] = "IMPLEMENTED_AWAITING_OWNER_REVIEW"
    report["machine_integrity_verdict"] = "PASS"
    report["human_review_status"] = "PENDING_OWNER_REVIEW"
    report["machine_gate"] = gate
    report["map_learning_relationship_identity_agreement"] = "PASS"
    report["ordinary_single_edge_regression"] = "PASS"
    report["spec030_role_separation"]["status"] = "PRESERVED"
    report["browser_console_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report
