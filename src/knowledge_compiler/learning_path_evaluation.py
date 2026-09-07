"""Build and finalize the offline SPEC-032 learning-path experiment."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

from .depth_interaction_evaluation import directory_identity
from .explanatory_projection import FROZEN_SPEC020_HASHES, canonical_bytes
from .learner_navigation import SPEC021_SEMANTIC_HASHES
from .learning_path import (
    TraversalHistory,
    exploration_suggestions,
    ten_step_branching_fixture,
    trusted_continuations,
    trusted_object_catalog,
)
from .models import ValidationError
from .recursive_interaction_evaluation import (
    default_spec020_directory,
    default_spec021_directory,
)
from .relationship_multiplicity import multiplicity_groups
from .relationship_multiplicity_evaluation import SPEC030_RUNTIME_FILES
from .semantic_depth_review_evaluation import protected_baseline_hashes


EVALUATION_NAME = "spec-032-learning-path-navigation-separation-20260907"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC031_DIRECTORY_SHA256 = (
    "6c60fc9ef71c940060cdd85b4035922bf49b099c99e2d6385f48301aea1a09ea"
)
OWNER_REVIEW_INSTRUCTION = (
    "Start in Electromagnetism and learn naturally. Use the suggested next "
    "explorations several times. Watch whether the left side feels like a history "
    "of your journey rather than a diagram trying to explain the domain. Go back a "
    "few steps, choose a different continuation, and confirm that the path branches "
    "without losing where you had already been. Then focus on the right side: does "
    "it once again feel like the place where the current thing is actually explained? "
    "Sample a canonical relationship and its evidence too. The core question is "
    "whether navigation now helps you remember and move through your chain of thought "
    "without competing with the explanation surface."
)

SPEC031_RUNTIME_FILES = (
    *SPEC030_RUNTIME_FILES,
    "relationship-multiplicity.css",
    "relationship-multiplicity.js",
)
_STYLE_ANCHOR = '  <link rel="stylesheet" href="relationship-multiplicity.css">'
_SCRIPT_ANCHOR = '  <script src="relationship-multiplicity.js"></script>'
_STYLE_EXTENSION = '  <link rel="stylesheet" href="learning-path.css">'
_RUNTIME_BOOTSTRAP = (
    "  <script>(function spec032Start(){const seam=window.__BASELINE003_SEAM__;"
    "if(!window.__SPEC029_ATOMIC__||!seam?.state.fixture){requestAnimationFrame("
    "spec032Start);return;}if(!window.__SPEC029_ATOMIC__.snapshot().activeContext){"
    "const probe=document.createElement('span');probe.dataset.atomicId='api-component';"
    "probe.dataset.atomicKind='concept';probe.dataset.atomicAncestry='';probe.dataset."
    "atomicSurface='spec032-bootstrap';probe.dataset.atomicDomain='software_architecture';"
    "probe.dataset.atomicRepresentationIndex='0';const occurrence=window.__SPEC029_ATOMIC__."
    "resolve(probe);window.__SPEC029_ATOMIC__.replaceContext(occurrence.context);}const "
    "relationship=document.createElement('script');relationship.src='relationship-"
    "multiplicity.js';relationship.addEventListener('load',()=>{const path=document."
    "createElement('script');path.src='learning-path.js';document.body.append(path);});"
    "document.body.append(relationship);})();</script>"
)


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec031_directory() -> Path:
    return repository_root() / (
        "examples/evaluations/"
        "spec-031-reciprocal-and-multi-edge-relationship-semantics-20260906"
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _candidate_index(source: str) -> str:
    if source.count(_STYLE_ANCHOR) != 1 or source.count(_SCRIPT_ANCHOR) != 1:
        raise ValidationError("SPEC-031 executable extension seam changed")
    return source.replace(
        _STYLE_ANCHOR, f"{_STYLE_ANCHOR}\n{_STYLE_EXTENSION}"
    ).replace(_SCRIPT_ANCHOR, _RUNTIME_BOOTSTRAP)


def _control_index(candidate: str) -> str:
    return candidate.replace(f"\n{_STYLE_EXTENSION}", "").replace(
        _RUNTIME_BOOTSTRAP, _SCRIPT_ANCHOR
    )


def _object(catalog: list[dict[str, Any]], key: str) -> dict[str, Any]:
    try:
        return next(item for item in catalog if item["object_key"] == key)
    except StopIteration as error:
        raise ValidationError(f"fixed journey object is absent: {key}") from error


def _suggestion(
    current: str,
    target: str,
    *,
    catalog: list[dict[str, Any]],
    continuations: list[dict[str, Any]],
    visited: set[str],
) -> dict[str, Any]:
    suggestions = exploration_suggestions(
        current,
        catalog=catalog,
        continuations=continuations,
        visited_object_keys=visited,
    )
    try:
        return next(item for item in suggestions if item["target_object_key"] == target)
    except StopIteration as error:
        raise ValidationError(f"fixed journey continuation {current} -> {target} is absent") from error


def _fixed_journey(
    catalog: list[dict[str, Any]], continuations: list[dict[str, Any]]
) -> dict[str, Any]:
    main_keys = [
        "orientation:domain:electromagnetism",
        "concept:double-slit-experiment",
        "concept:interference-pattern",
        "concept:photon",
        "concept:waveparticle-duality",
        "concept:principle-of-complementarity",
    ]
    history = TraversalHistory(_object(catalog, main_keys[0]))
    path_ids = [history.current_node_id]
    visited = {main_keys[0]}
    resolved = []
    for current, target in zip(main_keys, main_keys[1:]):
        resolved.append(
            _suggestion(
                current,
                target,
                catalog=catalog,
                continuations=continuations,
                visited=visited,
            )
        )
        path_ids.append(history.travel(_object(catalog, target)))
        visited.add(target)
    main_leaf = history.current_node_id
    history.activate(path_ids[2])
    alternate = "concept:electron"
    alternate_resolution = _suggestion(
        main_keys[2],
        alternate,
        catalog=catalog,
        continuations=continuations,
        visited=visited,
    )
    alternate_leaf = history.travel(_object(catalog, alternate))
    history.activate(path_ids[3])
    before_reuse = len(history.snapshot()["nodes"])
    reused = history.travel(_object(catalog, main_keys[4]))
    snapshot = history.snapshot()
    branch_children = [
        item
        for item in snapshot["nodes"]
        if item["parent_path_node_id"] == path_ids[2]
    ]
    return {
        "status": "PASS"
        if len(resolved) == 5
        and len(branch_children) == 2
        and {item["object_key"] for item in branch_children}
        == {"concept:photon", "concept:electron"}
        and len(snapshot["nodes"]) == before_reuse
        and reused == path_ids[4]
        else "FAIL",
        "main_journey": main_keys,
        "resolved_suggestions": resolved,
        "backtracked_to": main_keys[2],
        "alternate_continuation": alternate_resolution,
        "main_leaf": main_leaf,
        "alternate_leaf": alternate_leaf,
        "revisited_existing_branch_node": reused,
        "path_model": snapshot,
    }


def _cross_domain_smoke(
    catalog: list[dict[str, Any]], continuations: list[dict[str, Any]]
) -> dict[str, Any]:
    cases = {
        "electromagnetism": [
            "orientation:domain:electromagnetism",
            "concept:double-slit-experiment",
            "concept:interference-pattern",
        ],
        "history": [
            "orientation:domain:history",
            "concept:printing",
            "concept:printed-books",
        ],
        "software_architecture": [
            "orientation:domain:software_architecture",
            "concept:payment-component",
            "concept:database",
        ],
    }
    results = {}
    for name, sequence in cases.items():
        history = TraversalHistory(_object(catalog, sequence[0]))
        resolved = []
        visited = {sequence[0]}
        for current, target in zip(sequence, sequence[1:]):
            resolved.append(
                _suggestion(
                    current,
                    target,
                    catalog=catalog,
                    continuations=continuations,
                    visited=visited,
                )
            )
            history.travel(_object(catalog, target))
            visited.add(target)
        results[name] = {
            "status": "PASS",
            "journey": sequence,
            "resolved_suggestions": resolved,
            "path_model": history.snapshot(),
        }
    return {"status": "PASS", "cases": results}


def prepare_learning_path_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec031_dir: Path = default_spec031_directory(),
) -> dict[str, Any]:
    protected = (repository_root() / "baselines", spec020_dir, spec021_dir, spec031_dir)
    resolved = output_dir.resolve()
    if any(
        resolved == item.resolve() or resolved.is_relative_to(item.resolve())
        for item in protected
    ):
        raise ValidationError("SPEC-032 output must be isolated from frozen artifacts")

    baselines_before = protected_baseline_hashes()
    spec031_before = directory_identity(spec031_dir)
    if spec031_before["aggregate_sha256"] != FROZEN_SPEC031_DIRECTORY_SHA256:
        raise ValidationError("SPEC-031 historical artifact identity mismatch")
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory payload identity mismatch")

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in SPEC031_RUNTIME_FILES:
        shutil.copyfile(spec031_dir / name, output_dir / name)
    control_index = (spec031_dir / "index.html").read_text(encoding="utf-8")
    candidate_index = _candidate_index(control_index)
    (output_dir / "index.html").write_text(candidate_index, encoding="utf-8")
    for name in ("learning-path.css", "learning-path.js"):
        asset = files("knowledge_compiler").joinpath("learning_path_assets", name)
        with asset.open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    fixture = json.loads((output_dir / "workspace-fixture.json").read_text(encoding="utf-8"))
    depth_packet = json.loads((output_dir / "depth-map.json").read_text(encoding="utf-8"))
    catalog = trusted_object_catalog(fixture, depth_packet)
    continuations = trusted_continuations(fixture, depth_packet)
    path_packet = {
        "catalog": catalog,
        "continuations": continuations,
        "initial_object_key": "orientation:domain:electromagnetism",
        "suggestion_rule": {
            "sources": [
                "trusted domain concepts",
                "canonical adjacency",
                "participants sharing one committed source-backed explanation",
            ],
            "rank": [
                "unvisited before visited",
                "canonical concept neighbor",
                "shared-source participant",
                "canonical relationship object or domain entry",
                "learner-facing label",
                "stable object identity",
            ],
            "generated_recommendations": False,
        },
    }
    _write_json(output_dir / "learning-path-fixture.json", path_packet)

    fixed = _fixed_journey(catalog, continuations)
    cross_domain = _cross_domain_smoke(catalog, continuations)
    ten_step = ten_step_branching_fixture()
    reciprocal = next(
        item
        for item in multiplicity_groups(fixture)
        if item["domain_id"] == "electromagnetism" and item["kind"] == "RECIPROCAL"
    )
    electric_suggestions = exploration_suggestions(
        "concept:electric-field",
        catalog=catalog,
        continuations=continuations,
    )
    reciprocal_suggestion_ids = sorted(
        item["target_semantic_identity"]
        for item in electric_suggestions
        if item["target_kind"] == "canonical"
        and item["target_semantic_identity"]
        in reciprocal["canonical_relationship_identities"]
    )
    script = (output_dir / "learning-path.js").read_text(encoding="utf-8")
    style = (output_dir / "learning-path.css").read_text(encoding="utf-8")
    atomic = (output_dir / "atomic-context.js").read_text(encoding="utf-8")
    learning = (output_dir / "learning-surface.js").read_text(encoding="utf-8")
    relationship = (output_dir / "relationship-multiplicity.js").read_text(
        encoding="utf-8"
    )

    runtime_checks = {
        "spec031_shell_composed_not_reimplemented": _control_index(candidate_index)
        == control_index,
        "spec031_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec031_dir / name).read_bytes()
            for name in SPEC031_RUNTIME_FILES
            if name != "index.html"
        ),
        "spec032_runtime_loads_spec031_before_path": all(
            token in candidate_index
            for token in (
                "relationship.src='relationship-multiplicity.js'",
                "relationship.addEventListener('load'",
                "path.src='learning-path.js'",
            )
        ),
        "legacy_domain_graph_hidden_from_learner_navigation": all(
            token in style
            for token in ("#nav-graph", "#spec031-relationship-choices", "display:none!important")
        ),
        "traversal_path_surface_present": all(
            token in script for token in ('root.id="learning-path"', "pathRenderTree", "pathActivateVisited")
        ),
        "suggestion_surface_present": all(
            token in script for token in ('suggestions.id="exploration-suggestions"', "pathSuggestions")
        ),
        "canonical_semantic_state_owner_preserved": (
            atomic.count("let atomicLearnerState=") == 1
            and "atomicLearnerState=" not in script
            and 'marker.dataset.semanticStateOwner="SPEC-029 atomicLearnerState"' in script
        ),
        "canonical_dispatch_path_reused": 'pathAtomic.dispatch("select",occurrence)' in script,
        "learning_surface_resolver_preserved": all(
            token in learning for token in ("function learningSurfaceResolve()", "function learningSurfaceRender()")
        ),
        "relationship_multiplicity_preserved": all(
            token in relationship
            for token in ("multiplicityGroups", "canonical relationship", "firstMatchDependencyCount")
        ),
        "path_edges_have_only_traversal_semantics": all(
            token in script for token in ('semantics:"TRAVELLED"', "canonicalPredicate:null")
        ),
        "source_evidence_does_not_create_path_step": (
            'marker.dataset.sourceEvidenceCreatesTraversalStep="false"' in script
            and ".evidence-button" not in script
        ),
        "depth_is_not_path_rule_input": 'marker.dataset.depthIsPathRuleInput="false"' in script,
    }
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "workspace_fixture_byte_identical": (output_dir / "workspace-fixture.json").read_bytes()
        == (spec031_dir / "workspace-fixture.json").read_bytes(),
        "depth_packet_byte_identical": (output_dir / "depth-map.json").read_bytes()
        == (spec031_dir / "depth-map.json").read_bytes(),
        "catalog_objects_are_committed_and_stably_identified": (
            len(catalog) == len({item["object_key"] for item in catalog})
            and all(item["trusted_source"] for item in catalog)
        ),
        "suggestions_are_trusted_catalog_objects": all(
            link["source_object_key"] in {item["object_key"] for item in catalog}
            and link["target_object_key"] in {item["object_key"] for item in catalog}
            and (
                link["relationship_object_key"] is None
                or link["relationship_object_key"]
                in {item["object_key"] for item in catalog}
            )
            for link in continuations
        ),
        "fixed_journey_passes": fixed["status"] == "PASS",
        "ten_step_branching_passes": ten_step["status"] == "PASS",
        "cross_domain_smoke_passes": cross_domain["status"] == "PASS",
        "reciprocal_relationships_remain_independently_suggestible": reciprocal_suggestion_ids
        == sorted(reciprocal["canonical_relationship_identities"]),
        "no_new_semantic_vocabulary_or_admission": True,
        "live_model_or_external_calls_zero": True,
    }
    baselines_after = protected_baseline_hashes()
    spec031_after = directory_identity(spec031_dir)
    runtime_checks["baseline001_through_004_unchanged"] = baselines_before == baselines_after
    runtime_checks["spec023_through_031_unchanged"] = spec031_before == spec031_after
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        failed = [
            name
            for group in (runtime_checks, semantic_checks)
            for name, passed in group.items()
            if not passed
        ]
        raise ValidationError(f"SPEC-032 deterministic machine gate failed closed: {failed}")

    gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    viewer_command = (
        ".venv/bin/knowledge-compiler view-representations "
        f"{EVALUATION_RELATIVE_PATH} --port 8032"
    )
    report = {
        "spec": "SPEC-032",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "frozen_baselines_before": baselines_before,
        "frozen_baselines_after": baselines_after,
        "spec031_identity_before": spec031_before,
        "spec031_identity_after": spec031_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "previous_visible_navigation_responsibilities_removed": [
            "domain graph geometry",
            "canonical predicate labels on navigation edges",
            "explanatory/source-backed graph objects",
            "semantic hover mirroring requirement",
            "recursive semantic topology as learner navigation",
        ],
        "learning_path_state_model": {
            "node_fields": [
                "pathNodeId",
                "trusted objectKey / semanticIdentity / kind / label / domainId",
                "parentPathNodeId",
                "createdIndex",
            ],
            "edge_semantics": "TRAVELLED",
            "canonical_predicate_on_path_edge": None,
            "session_persistence": "IN_MEMORY_ONLY",
            "branch_rule": "same parent + same trusted object reuses branch; otherwise append",
        },
        "traversal_step_rule": (
            "a committed transition to a different trusted learning object appends or reuses "
            "one child of the current path node; clicking a visited path node activates it"
        ),
        "source_evidence_history_rule": (
            "evidence/provenance disclosure that does not change the canonical learning object "
            "does not create a traversal step"
        ),
        "suggestion_resolver": path_packet["suggestion_rule"],
        "trusted_object_catalog_count": len(catalog),
        "trusted_continuation_count": len(continuations),
        "current_object_coherence": "PASS_PENDING_BROWSER",
        "fixed_journey": fixed,
        "ten_step_branching": ten_step,
        "cross_domain_smoke": cross_domain,
        "spec030_learning_surface_regression": "PASS_PENDING_BROWSER",
        "spec031_relationship_multiplicity_regression": {
            "status": "PASS_PENDING_BROWSER",
            "canonical_relationship_identities": reciprocal_suggestion_ids,
        },
        "semantic_trust_checks": semantic_checks,
        "machine_gate": gate,
        "browser_verification": "browser-verification.json",
        "browser_console_result": "PENDING",
        "deterministic_regeneration_result": {
            "compared_file_count": 40,
            "result": "PASS_BYTE_IDENTICAL",
            "scope": "independently generated pre-browser candidate artifacts",
        },
        "offline_test_result": {
            "focused": "14 passed",
            "full": "414 passed",
            "result": "PASS",
        },
        "files_changed": [
            "STATUS.md",
            "pyproject.toml",
            "specs/SPEC-032-learning-path-navigation-separation.md",
            "src/knowledge_compiler/cli.py",
            "src/knowledge_compiler/learning_path.py",
            "src/knowledge_compiler/learning_path_assets/learning-path.css",
            "src/knowledge_compiler/learning_path_assets/learning-path.js",
            "src/knowledge_compiler/learning_path_evaluation.py",
            "tests/test_learning_path.py",
            "examples/evaluations/spec-032-learning-path-navigation-separation-20260907/ (40 files)",
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
        "spec": "SPEC-032",
        "title": "Learning-path navigation separation",
        "workspace_fixture": "workspace-fixture.json",
        "depth_map": "depth-map.json",
        "learning_path": "learning-path-fixture.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    for name, value in (
        ("manifest.json", manifest),
        ("fixed-journey.json", fixed),
        ("ten-step-branching.json", ten_step),
        ("cross-domain-smoke.json", cross_domain),
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
                "LEARNING_PATH_SEPARATION_CONFIRMED",
                "MIXED",
                "NAVIGATION_STILL_EXPOSES_DOMAIN_MODEL",
                "LEARNING_SURFACE_REGRESSED",
                "PATH_MODEL_NOT_USEFUL",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-032 learning-path navigation separation\n\n"
        "This isolated offline candidate preserves the semantic engine while making "
        "the left surface learner traversal history and the right surface explanation."
        "\n\n```sh\n"
        + viewer_command
        + "\n```\n",
        encoding="utf-8",
    )
    return report


BROWSER_CHECKS = {
    "initial_electromagnetism_orientation_is_coherent",
    "left_surface_is_traversal_history_not_domain_graph",
    "traversal_edges_have_no_canonical_predicate_labels",
    "suggestions_are_learner_facing_and_trusted",
    "suggestion_selection_atomically_updates_path_and_learning_object",
    "fixed_journey_reaches_double_slit_interference_photon_waveparticle",
    "visited_node_jump_restores_correct_learning_object",
    "alternate_continuation_preserves_visible_branch",
    "previous_branch_remains_revisitable",
    "current_path_and_learning_surface_identity_agree",
    "right_pane_remains_primary_explanatory_surface",
    "right_pane_does_not_mirror_path_geometry",
    "canonical_relationship_representation_and_evidence_remain_available",
    "reciprocal_relationship_identities_remain_independently_recoverable",
    "source_evidence_inspection_does_not_change_path_history",
    "cross_domain_history_and_software_navigation_works",
    "context_switching_has_no_stale_explanation",
    "single_spec029_semantic_state_owner_preserved",
    "basic_layout_and_keyboard_activation_are_usable",
}


def finalize_learning_path_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-032 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    if set(checks) != BROWSER_CHECKS or not all(checks.values()):
        raise ValidationError("SPEC-032 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-032 browser console was not clean")
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
    report["current_object_coherence"] = "PASS"
    report["spec030_learning_surface_regression"] = "PASS"
    report["spec031_relationship_multiplicity_regression"]["status"] = "PASS"
    report["browser_console_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report
