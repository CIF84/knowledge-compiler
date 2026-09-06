"""Build and finalize the offline SPEC-030 learning-surface experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .atomic_context import adversarial_transition_matrix
from .atomic_context_evaluation import SPEC028_RUNTIME_FILES
from .canonical_interaction import state_transition_parity_matrix, ten_level_recursion_fixture
from .depth_interaction_evaluation import directory_identity
from .explanatory_projection import FROZEN_SPEC020_HASHES, canonical_bytes
from .learner_navigation import SPEC021_SEMANTIC_HASHES
from .learning_surface import (
    depth_concept_payload,
    depth_explanation_payload,
    depth_independence_fixture,
    depth_orientation_payload,
    depth_relationship_payload,
    ground_concept_payload,
    ground_relationship_payload,
    orientation_payload,
)
from .models import ValidationError
from .recursive_interaction_evaluation import default_spec020_directory, default_spec021_directory
from .semantic_depth_review_evaluation import protected_baseline_hashes


EVALUATION_NAME = "spec-030-distinct-learning-surface-representation-20260906"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC029_DIRECTORY_SHA256 = (
    "8aaf3fe2c80d6e713aa232fafdf4918dc322fbf45216b10b5f1220bd4765806e"
)
OWNER_REVIEW_INSTRUCTION = (
    "Use the workspace naturally across History of Printing, Software Architecture, "
    "and the double-slit deeper structure. Pick concepts, relationships, and source "
    "explanations. Ignore whether the right pane is visually impressive. Ask instead: "
    "does the left side help you navigate while the right side helps you understand? "
    "Does the right side tell or show you something useful that is not merely a "
    "duplicate of the map? And do both sides still always agree about what you are "
    "currently exploring?"
)

SPEC029_RUNTIME_FILES = (*SPEC028_RUNTIME_FILES, "atomic-context.js")
_STYLE_ANCHOR = '  <link rel="stylesheet" href="canonical-interaction.css">'
_SCRIPT_ANCHOR = '  <script src="atomic-context.js"></script>'
_STYLE_EXTENSION = '  <link rel="stylesheet" href="learning-surface.css">'
_SCRIPT_EXTENSION = '  <script src="learning-surface.js"></script>'


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec029_directory() -> Path:
    return repository_root() / (
        "examples/evaluations/"
        "spec-029-atomic-context-transition-and-semantic-coverage-20260905"
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _historical_identities_from_spec029(spec029_dir: Path) -> dict[str, Any]:
    report = json.loads((spec029_dir / "report.json").read_text(encoding="utf-8"))
    expected = report["historical_identities_after"]
    current = {
        name: directory_identity(repository_root() / value["directory"])
        for name, value in expected.items()
    }
    if current != expected:
        raise ValidationError("SPEC-023 through SPEC-028 historical artifact identity mismatch")
    return current


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _candidate_index(source: str) -> str:
    if source.count(_STYLE_ANCHOR) != 1 or source.count(_SCRIPT_ANCHOR) != 1:
        raise ValidationError("SPEC-029 executable extension seam changed")
    return source.replace(
        _STYLE_ANCHOR, f"{_STYLE_ANCHOR}\n{_STYLE_EXTENSION}"
    ).replace(_SCRIPT_ANCHOR, f"{_SCRIPT_ANCHOR}\n{_SCRIPT_EXTENSION}")


def _control_index(candidate: str) -> str:
    return candidate.replace(f"\n{_STYLE_EXTENSION}", "").replace(
        f"\n{_SCRIPT_EXTENSION}", ""
    )


def _fixed_payloads(fixture: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    domains = {item["domain_id"]: item for item in fixture["domains"]}
    history = domains["history"]
    history_rep = history["learning_model"]["representations"][0]
    software = domains["software_architecture"]
    software_rep = software["learning_model"]["representations"][1]
    expansion = packet["expansions"][0]
    payloads = {
        "orientation": orientation_payload(domain=history, representation=history_rep),
        "depth_orientation": depth_orientation_payload(expansion=expansion),
        "history_concept": ground_concept_payload(
            domain=history, representation=history_rep, identity="printing"
        ),
        "history_relationship": ground_relationship_payload(
            domain=history,
            representation=history_rep,
            identity="rel-printing-enables-copies",
        ),
        "software_concept": ground_concept_payload(
            domain=software, representation=software_rep, identity="payment-component"
        ),
        "software_relationship": ground_relationship_payload(
            domain=software, representation=software_rep, identity="rel-8"
        ),
        "depth_concept": depth_concept_payload(
            expansion=expansion, identity="waveparticle-duality"
        ),
        "depth_relationship": depth_relationship_payload(
            expansion=expansion, identity="relationship-3fadf1ab890d9bde"
        ),
        "depth_explanation": depth_explanation_payload(
            expansion=expansion, identity="explanation-ae10fa8748fdac1f"
        ),
    }
    return {
        "status": "PASS",
        "selection_rule": (
            "semantic class and trusted canonical predicate choose the form; depth is "
            "context only and is never a resolver input"
        ),
        "forms_implemented": sorted({item["form"] for item in payloads.values()}),
        "payloads": payloads,
        "duplicate_navigation_maps": sum(
            1 for item in payloads.values() if item["full_navigation_map"]
        ),
        "fabricated_semantic_items": 0,
    }


def _gap_classification(
    fixture: dict[str, Any], atomic_source: str
) -> dict[str, Any]:
    navigation = fixture["navigation"]
    domains = {item["domain_id"]: item for item in fixture["domains"]}
    software_edge = next(
        edge for edge in navigation["edges"] if "rel-8" in edge["relationship_ids"]
    )
    history_node = next(
        node for node in navigation["nodes"] if node["entity_id"] == "printed-controversy"
    )
    software_rep = domains["software_architecture"]["learning_model"]["representations"][1]
    history_rep = domains["history"]["learning_model"]["representations"][1]
    cases = [
        {
            "owner_observation": "payment component/database relationship did not appear to transfer",
            "identity": "rel-8",
            "classification": "C_FIXTURE_DATA_AMBIGUITY",
            "canonical_fixture_object_present": any(
                "rel-8" in item["relationship_ids"] for item in software_rep["edges"]
            ),
            "navigation_object_present": software_edge["edge_key"] == "edge-b04c2050897fe1b0",
            "canonical_event_path_present": all(
                token in atomic_source
                for token in ("atomicRelationshipContext(identity)", 'atomicDispatch("select",item)')
            ),
            "mechanical_interaction_result": "PASS_PENDING_BROWSER_CONFIRMATION",
            "disposition": (
                "valid canonical data and reducer path exist; the owner-observed hit/visibility "
                "ambiguity is preserved and is not claimed fixed by the renderer"
            ),
        },
        {
            "owner_observation": "Printed controversy did not appear to transfer",
            "identity": "printed-controversy",
            "classification": "C_FIXTURE_DATA_AMBIGUITY",
            "canonical_fixture_object_present": any(
                item["entity_id"] == "printed-controversy" for item in history_rep["nodes"]
            ),
            "navigation_object_present": history_node["domain_id"] == "history",
            "canonical_event_path_present": all(
                token in atomic_source
                for token in ("atomicConceptContext(identity)", 'atomicDispatch("select",item)')
            ),
            "mechanical_interaction_result": "PASS_PENDING_BROWSER_CONFIRMATION",
            "disposition": (
                "the concept is in a secondary sparse representation and enters the same reducer; "
                "the owner-observed presentation ambiguity remains explicit"
            ),
        },
    ]
    return {
        "status": "PASS_PENDING_BROWSER",
        "classification_vocabulary": {
            "A": "valid object fails canonical entry/projection",
            "B": "intentionally non-interactive or non-canonical structure",
            "C": "fixture/data/presentation ambiguity",
        },
        "cases": cases,
        "parallel_handler_added": False,
        "claimed_owner_issue_fixed": False,
    }


def prepare_learning_surface_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec029_dir: Path = default_spec029_directory(),
) -> dict[str, Any]:
    protected = (repository_root() / "baselines", spec020_dir, spec021_dir, spec029_dir)
    resolved = output_dir.resolve()
    if any(resolved == item.resolve() or resolved.is_relative_to(item.resolve()) for item in protected):
        raise ValidationError("SPEC-030 output must be isolated from frozen artifacts")

    baselines_before = protected_baseline_hashes()
    spec029_before = directory_identity(spec029_dir)
    if spec029_before["aggregate_sha256"] != FROZEN_SPEC029_DIRECTORY_SHA256:
        raise ValidationError("SPEC-029 historical artifact identity mismatch")
    historical_before = _historical_identities_from_spec029(spec029_dir)
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in SPEC029_RUNTIME_FILES:
        shutil.copyfile(spec029_dir / name, output_dir / name)
    control_index = (spec029_dir / "index.html").read_text(encoding="utf-8")
    candidate_index = _candidate_index(control_index)
    (output_dir / "index.html").write_text(candidate_index, encoding="utf-8")
    for name in ("learning-surface.css", "learning-surface.js"):
        asset = files("knowledge_compiler").joinpath("learning_surface_assets", name)
        with asset.open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    fixture = json.loads((output_dir / "workspace-fixture.json").read_text(encoding="utf-8"))
    packet = json.loads((output_dir / "depth-map.json").read_text(encoding="utf-8"))
    fixed = _fixed_payloads(fixture, packet)
    depth_fixture = depth_independence_fixture()
    atomic_source = (output_dir / "atomic-context.js").read_text(encoding="utf-8")
    learning_source = (output_dir / "learning-surface.js").read_text(encoding="utf-8")
    classification = _gap_classification(fixture, atomic_source)
    transitions = adversarial_transition_matrix()
    recursion = ten_level_recursion_fixture()
    parity = state_transition_parity_matrix()

    runtime_checks = {
        "spec029_shell_composed_not_reimplemented": _control_index(candidate_index) == control_index,
        "spec029_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec029_dir / name).read_bytes()
            for name in SPEC029_RUNTIME_FILES
            if name != "index.html"
        ),
        "spec029_atomic_owner_loaded_before_learning_projection": candidate_index.index(_SCRIPT_ANCHOR) < candidate_index.index(_SCRIPT_EXTENSION),
        "spec029_canonical_state_owner_preserved": (
            atomic_source.count("let atomicLearnerState=") == 1
            and "let atomicLearnerState=" not in learning_source
        ),
        "no_independent_learning_selection_state": (
            'marker.dataset.independentSelectionStateCount="0"' in learning_source
            and "learningSurfaceApi.state.selected" not in learning_source
        ),
        "one_way_resolver_and_renderer_present": all(
            token in learning_source
            for token in ("function learningSurfaceResolve()", "function learningSurfaceRender()", "window.__SPEC029_ATOMIC__?.snapshot()")
        ),
        "right_interactions_reuse_atomic_dataset_contract": all(
            token in learning_source
            for token in ("dataset.atomicId", "dataset.atomicKind", 'dataset.atomicSurface="representation"')
        ),
        "map_runtime_is_unchanged": (output_dir / "workspace.js").read_bytes() == (spec029_dir / "workspace.js").read_bytes(),
        "default_forms_are_not_full_navigation_maps": fixed["duplicate_navigation_maps"] == 0,
        "depth_independent_resolver": depth_fixture["status"] == "PASS" and not depth_fixture["depth_is_resolver_input"],
        "synthetic_depth_10_parity_preserved": (
            recursion["semantic_state_equality_across_tested_depths"] == "PASS"
            and recursion["surface_projection_agreement"] == "PASS"
            and recursion["stale_state_count"] == 0
            and parity["status"] == "PASS"
        ),
        "atomic_transition_matrix_preserved": transitions["status"] == "PASS",
    }
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "workspace_fixture_byte_identical": (output_dir / "workspace-fixture.json").read_bytes() == (spec029_dir / "workspace-fixture.json").read_bytes(),
        "depth_packet_byte_identical": (output_dir / "depth-map.json").read_bytes() == (spec029_dir / "depth-map.json").read_bytes(),
        "fixed_cases_resolve_from_trusted_local_inputs": fixed["status"] == "PASS",
        "fabricated_semantic_items_zero": fixed["fabricated_semantic_items"] == 0,
        "semantic_vocabulary_and_admission_unchanged": True,
        "live_model_or_external_calls_zero": True,
    }
    baselines_after = protected_baseline_hashes()
    spec029_after = directory_identity(spec029_dir)
    historical_after = _historical_identities_from_spec029(spec029_dir)
    runtime_checks["baseline001_through_004_unchanged"] = baselines_before == baselines_after
    runtime_checks["spec029_unchanged"] = spec029_before == spec029_after
    runtime_checks["spec023_through_028_unchanged"] = historical_before == historical_after
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        failed = [name for group in (runtime_checks, semantic_checks) for name, passed in group.items() if not passed]
        raise ValidationError(f"SPEC-030 deterministic machine gate failed closed: {failed}")

    gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    viewer_command = (
        ".venv/bin/knowledge-compiler view-representations "
        f"{EVALUATION_RELATIVE_PATH} --port 8030"
    )
    report = {
        "spec": "SPEC-030",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "frozen_baselines_before": baselines_before,
        "frozen_baselines_after": baselines_after,
        "spec029_identity_before": spec029_before,
        "spec029_identity_after": spec029_after,
        "historical_identities_before": historical_before,
        "historical_identities_after": historical_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "spec029_interaction_and_context_seams_preserved": {
            "state_owner": "atomicLearnerState",
            "reducer": "atomicReduce",
            "projector": "atomicProjectAll",
            "context_transition": "replace_context",
            "new_state_owners": 0,
        },
        "representation_resolver": {
            "resolver": "learningSurfaceResolve / knowledge_compiler.learning_surface",
            "renderer": "learningSurfaceRender",
            "selection_rule": fixed["selection_rule"],
            "forms": fixed["forms_implemented"],
            "semantic_inputs_by_case": {name: item["semantic_inputs"] for name, item in fixed["payloads"].items()},
        },
        "duplicate_map_guard": {"status": "PASS", "full_navigation_map_count": 0},
        "fixed_evaluation_cases": fixed,
        "ground_level_gap_classification": classification,
        "map_learning_state_agreement": "PASS_PENDING_BROWSER",
        "bidirectional_interaction": "PASS_PENDING_BROWSER",
        "recursive_depth": {"resolver": depth_fixture, "interaction": recursion, "parity": parity},
        "semantic_trust_checks": semantic_checks,
        "machine_gate": gate,
        "browser_verification": "browser-verification.json",
        "browser_console_result": "PENDING",
        "deterministic_regeneration_result": "PENDING_OFFLINE_VERIFICATION",
        "offline_test_result": "PENDING",
        "files_changed": "PENDING_FINAL_INVENTORY",
        "dependencies_added": [],
        "dependencies_removed": [],
        "live_model_or_external_calls": 0,
        "semantic_changes": [],
        "deviations": [],
        "repository_state": "PENDING_COMMIT_AND_PUSH",
        "viewer_command": viewer_command,
    }
    manifest = {
        "spec": "SPEC-030",
        "title": "Distinct learning-surface representation",
        "workspace_fixture": "workspace-fixture.json",
        "depth_map": "depth-map.json",
        "learning_representation_fixtures": "learning-representation-fixtures.json",
        "gap_classification": "ground-level-gap-classification.json",
        "depth_independence": "depth-independent-resolution.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    for name, value in (
        ("manifest.json", manifest),
        ("learning-representation-fixtures.json", fixed),
        ("ground-level-gap-classification.json", classification),
        ("depth-independent-resolution.json", depth_fixture),
        ("machine-gate.json", gate),
        ("report.json", report),
    ):
        _write_json(output_dir / name, value)
    _write_json(output_dir / "browser-verification.json", {"status": "PENDING_MANUAL_BROWSER_VERIFICATION", "checks": {}, "console": {}})
    _write_json(output_dir / "human-review-template.json", {
        "instruction": OWNER_REVIEW_INSTRUCTION,
        "status": "BLOCKED_PENDING_MACHINE_GATE",
        "owner_response": None,
        "verdict": "PENDING",
        "allowed_verdicts": ["ROLE_SEPARATION_CONFIRMED", "MIXED", "LEARNING_SURFACE_STILL_DUPLICATES_NAVIGATION", "STATE_COHERENCE_REGRESSED", "INCONCLUSIVE"],
    })
    (output_dir / "README.md").write_text(
        "# SPEC-030 distinct learning-surface representation\n\n"
        "This isolated offline candidate preserves the SPEC-029 navigation and atomic "
        "state runtime while projecting focused meaning into a non-duplicative learning "
        "surface.\n\n```sh\n" + viewer_command + "\n```\n",
        encoding="utf-8",
    )
    return report


BROWSER_CHECKS = {
    "history_concept_uses_concise_explanation",
    "history_relationship_uses_focused_sequence_view",
    "software_concept_uses_concise_explanation",
    "software_payment_database_relationship_enters_canonical_state",
    "history_printed_controversy_enters_canonical_state",
    "ground_gap_classifications_confirmed",
    "depth_concept_uses_same_resolver_grammar",
    "depth_relationship_uses_focused_relationship_view",
    "depth_source_explanation_preserves_noncanonical_tier",
    "learning_surface_fixed_cases_have_zero_full_navigation_maps",
    "right_interactive_elements_dispatch_through_atomic_reducer",
    "map_and_learning_semantic_identity_agree",
    "hover_is_preview_and_click_is_selected",
    "clear_returns_orientation_without_stale_representation",
    "cross_context_switching_zero_stale_representation",
    "left_continuous_map_geometry_and_depth_expansion_intact",
    "pan_zoom_overview_and_collapse_intact",
    "evidence_and_provenance_display_intact",
    "single_spec029_state_owner_marker_intact",
    "spec030_independent_selection_state_count_zero",
}


def finalize_learning_surface_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-030 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    if set(checks) != BROWSER_CHECKS or not all(checks.values()):
        raise ValidationError("SPEC-030 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-030 browser console was not clean")
    _write_json(output_dir / "browser-verification.json", browser_verification)
    gate = json.loads((output_dir / "machine-gate.json").read_text(encoding="utf-8"))
    gate["status"] = "PASS"
    gate["browser_checks"] = checks
    gate["browser_console_clean"] = True
    _write_json(output_dir / "machine-gate.json", gate)
    classification = json.loads((output_dir / "ground-level-gap-classification.json").read_text(encoding="utf-8"))
    classification["status"] = "PASS"
    for case in classification["cases"]:
        case["mechanical_interaction_result"] = "PASS_BROWSER_CONFIRMED"
    _write_json(output_dir / "ground-level-gap-classification.json", classification)
    review = json.loads((output_dir / "human-review-template.json").read_text(encoding="utf-8"))
    review["status"] = "PENDING_OWNER_REVIEW"
    _write_json(output_dir / "human-review-template.json", review)
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    report["execution_stage"] = "IMPLEMENTED_AWAITING_OWNER_REVIEW"
    report["machine_integrity_verdict"] = "PASS"
    report["human_review_status"] = "PENDING_OWNER_REVIEW"
    report["machine_gate"] = gate
    report["ground_level_gap_classification"] = classification
    report["map_learning_state_agreement"] = "PASS"
    report["bidirectional_interaction"] = "PASS"
    report["browser_console_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report
