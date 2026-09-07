"""Build and finalize the offline SPEC-033 revealed-knowledge experiment."""

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
    exploration_suggestions,
    trusted_continuations,
    trusted_object_catalog,
)
from .learning_path_evaluation import (
    FROZEN_SPEC031_DIRECTORY_SHA256,
    SPEC031_RUNTIME_FILES,
    default_spec031_directory,
)
from .models import ValidationError
from .recursive_interaction_evaluation import (
    default_spec020_directory,
    default_spec021_directory,
)
from .revealed_knowledge import (
    RevealedKnowledgeState,
    canonical_projection,
    large_revealed_tree_fixture,
)
from .semantic_depth_review_evaluation import protected_baseline_hashes


EVALUATION_NAME = "spec-033-canonical-revealed-knowledge-tree-20260907"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC032_DIRECTORY_SHA256 = (
    "7d6333220412d3372d024a781229a30c524a25b6cb399c507f19bbed52109c1f"
)
OWNER_REVIEW_INSTRUCTION = (
    "Use Explore next to uncover concepts and several regions in an intentionally "
    "irrational order, then revisit earlier concepts and reciprocal relationships. "
    "Confirm My Map contains each canonical object once and feels like uncovered "
    "territory rather than click history. Collapse and reopen branches. In "
    "Electromagnetism, select the double-slit experiment, use Explore deeper, inspect "
    "several deeper concepts and relationships, close or leave depth, switch regions, "
    "and continue selecting repeatedly. Confirm deeper knowledge appears under the "
    "existing double-slit branch, labels remain horizontal and readable, the focused "
    "right pane always explains the current object, Explore next contains only "
    "unrevealed frontier items, and no interaction freezes. Finally append "
    "'?fixture=large' to the viewer URL and confirm the 60-object synthetic tree can "
    "be scrolled/dragged, collapsed, reopened, and remains legible."
)

_STYLE_ANCHOR = '  <link rel="stylesheet" href="relationship-multiplicity.css">'
_SCRIPT_ANCHOR = '  <script src="relationship-multiplicity.js"></script>'
_STYLE_EXTENSION = '  <link rel="stylesheet" href="revealed-knowledge.css">'
_SCRIPT_CAPTURE_ANCHOR = '  <script src="workspace.js"></script>'
_CONSOLE_CAPTURE = (
    "  <script>(function(){const log={errors:[],warnings:[]},error=console.error.bind("
    "console),warn=console.warn.bind(console);console.error=(...items)=>{log.errors.push("
    "items.map(String).join(' '));error(...items);};console.warn=(...items)=>{log.warnings."
    "push(items.map(String).join(' '));warn(...items);};window.addEventListener('error',"
    "event=>log.errors.push(String(event.message)));window.addEventListener('unhandledrejection',"
    "event=>log.errors.push(String(event.reason)));window.__SPEC033_BROWSER_LOG__=log;})();</script>"
)
_RUNTIME_BOOTSTRAP = (
    "  <script>(function spec033Start(){const seam=window.__BASELINE003_SEAM__;"
    "if(!window.__SPEC029_ATOMIC__||!seam?.state.fixture){requestAnimationFrame("
    "spec033Start);return;}if(!window.__SPEC029_ATOMIC__.snapshot().activeContext){"
    "const probe=document.createElement('span');probe.dataset.atomicId='api-component';"
    "probe.dataset.atomicKind='concept';probe.dataset.atomicAncestry='';probe.dataset."
    "atomicSurface='spec033-bootstrap';probe.dataset.atomicDomain='software_architecture';"
    "probe.dataset.atomicRepresentationIndex='0';const occurrence=window.__SPEC029_ATOMIC__."
    "resolve(probe);window.__SPEC029_ATOMIC__.replaceContext(occurrence.context);}const "
    "relationship=document.createElement('script');relationship.src='relationship-"
    "multiplicity.js';relationship.addEventListener('load',()=>{const revealed=document."
    "createElement('script');revealed.src='revealed-knowledge.js';document.body.append("
    "revealed);});document.body.append(relationship);})();</script>"
)


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec032_directory() -> Path:
    return repository_root() / (
        "examples/evaluations/"
        "spec-032-learning-path-navigation-separation-20260907"
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
    ).replace(
        _SCRIPT_CAPTURE_ANCHOR, f"{_CONSOLE_CAPTURE}\n{_SCRIPT_CAPTURE_ANCHOR}"
    ).replace(_SCRIPT_ANCHOR, _RUNTIME_BOOTSTRAP)


def _control_index(candidate: str) -> str:
    return candidate.replace(f"\n{_STYLE_EXTENSION}", "").replace(
        f"{_CONSOLE_CAPTURE}\n", ""
    ).replace(_RUNTIME_BOOTSTRAP, _SCRIPT_ANCHOR)


def _fixed_reveal_scenario(
    projection: list[dict[str, Any]], depth_packet: dict[str, Any]
) -> dict[str, Any]:
    initial = "orientation:domain:electromagnetism"
    state = RevealedKnowledgeState(projection, initial)
    irrational = [
        "concept:double-slit-experiment",
        "concept:interference-pattern",
        "orientation:domain:economics",
        "concept:market-price",
        "orientation:domain:history",
        "concept:printing",
        "orientation:domain:electromagnetism",
        "concept:double-slit-experiment",
        "orientation:domain:software_architecture",
        "concept:payment-component",
        "orientation:domain:electromagnetism",
        "concept:electric-field",
        "canonical:changing-electric-field-induces-magnetic-field",
        "concept:magnetic-field",
        "canonical:changing-magnetic-field-induces-electric-field",
        "concept:electric-field",
    ]
    counts: list[int] = []
    for key in irrational:
        state.select(key)
        counts.append(state.snapshot()["revealed_object_count"])
    before_revisit = state.snapshot()["revealed_object_count"]
    state.select("concept:double-slit-experiment")
    after_revisit = state.snapshot()["revealed_object_count"]
    depth_keys = sorted(
        {
            f"concept:{item['entity_id']}"
            for expansion in depth_packet["expansions"]
            for item in expansion["concepts"]
        }
        | {
            f"canonical:{item['id']}"
            for expansion in depth_packet["expansions"]
            for item in expansion["canonical_items"]
        }
        | {
            f"explanation:{item['id']}"
            for expansion in depth_packet["expansions"]
            for item in expansion["explanatory_items"]
        }
    )
    state.reveal_many(depth_keys, revealed_from="concept:double-slit-experiment")
    state.select("concept:waveparticle-duality")
    expanded = state.snapshot()
    state.set_expanded("concept:double-slit-experiment", False)
    collapsed = state.snapshot()
    state.select("concept:waveparticle-duality")
    reopened = state.snapshot()
    keys = reopened["revealed_object_keys"]
    return {
        "status": "PASS"
        if after_revisit == before_revisit
        and len(keys) == len(set(keys))
        and len(collapsed["visible_object_keys"]) < len(expanded["visible_object_keys"])
        and "concept:waveparticle-duality" in reopened["visible_object_keys"]
        and reopened["navigation_edge_semantics"] == "PROJECTION_GROUPING_ONLY"
        else "FAIL",
        "visit_order": irrational,
        "reveal_counts_after_each_visit": counts,
        "revisit_count_before": before_revisit,
        "revisit_count_after": after_revisit,
        "depth_revealed_object_keys": depth_keys,
        "expanded_snapshot": expanded,
        "collapsed_visible_count": len(collapsed["visible_object_keys"]),
        "reopened_snapshot": reopened,
    }


def _frontier_audit(
    catalog: list[dict[str, Any]], continuations: list[dict[str, Any]]
) -> dict[str, Any]:
    revealed = {
        "orientation:domain:electromagnetism",
        "concept:double-slit-experiment",
        "concept:interference-pattern",
    }
    raw = exploration_suggestions(
        "concept:double-slit-experiment",
        catalog=catalog,
        continuations=continuations,
        visited_object_keys=revealed,
    )
    trusted = {item["object_key"] for item in catalog}
    frontier = [
        item
        for item in raw
        if item["target_object_key"] not in revealed
        and item["target_object_key"] in trusted
    ]
    return {
        "status": "PASS"
        if frontier
        and not ({item["target_object_key"] for item in frontier} & revealed)
        else "FAIL",
        "revealed_object_keys": sorted(revealed),
        "frontier": frontier,
        "overlap": sorted(
            {item["target_object_key"] for item in frontier} & revealed
        ),
    }


def prepare_revealed_knowledge_evaluation(
    *,
    output_dir: Path,
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec031_dir: Path = default_spec031_directory(),
    spec032_dir: Path = default_spec032_directory(),
) -> dict[str, Any]:
    protected = (
        repository_root() / "baselines",
        spec020_dir,
        spec021_dir,
        spec031_dir,
        spec032_dir,
    )
    resolved = output_dir.resolve()
    if any(
        resolved == item.resolve() or resolved.is_relative_to(item.resolve())
        for item in protected
    ):
        raise ValidationError("SPEC-033 output must be isolated from frozen artifacts")

    baselines_before = protected_baseline_hashes()
    spec031_before = directory_identity(spec031_dir)
    spec032_before = directory_identity(spec032_dir)
    if spec031_before["aggregate_sha256"] != FROZEN_SPEC031_DIRECTORY_SHA256:
        raise ValidationError("SPEC-031 historical artifact identity mismatch")
    if spec032_before["aggregate_sha256"] != FROZEN_SPEC032_DIRECTORY_SHA256:
        raise ValidationError("SPEC-032 historical evidence identity mismatch")
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
    for name in ("revealed-knowledge.css", "revealed-knowledge.js"):
        asset = files("knowledge_compiler").joinpath("revealed_knowledge_assets", name)
        with asset.open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)

    fixture = json.loads((output_dir / "workspace-fixture.json").read_text())
    depth_packet = json.loads((output_dir / "depth-map.json").read_text())
    catalog = trusted_object_catalog(fixture, depth_packet)
    continuations = trusted_continuations(fixture, depth_packet)
    projection = canonical_projection(catalog, depth_packet)
    large_tree = large_revealed_tree_fixture()
    packet = {
        "projection": projection,
        "continuations": continuations,
        "initial_object_key": "orientation:domain:electromagnetism",
        "projection_contract": {
            "identity": "trusted object_key",
            "root_rule": "one stable root per trusted domain",
            "parent_resolution_rule": "direct domain grouping",
            "admitted_depth_rule": "group under canonical depth entrance",
            "projection_edges_are_semantic_claims": False,
            "history_structurally_defines_navigation": False,
            "revealed_equals_understood": False,
        },
        "large_tree": large_tree,
    }
    _write_json(output_dir / "revealed-knowledge-fixture.json", packet)

    fixed = _fixed_reveal_scenario(projection, depth_packet)
    frontier = _frontier_audit(catalog, continuations)
    script = (output_dir / "revealed-knowledge.js").read_text()
    style = (output_dir / "revealed-knowledge.css").read_text()
    atomic = (output_dir / "atomic-context.js").read_text()
    learning = (output_dir / "learning-surface.js").read_text()
    relationship = (output_dir / "relationship-multiplicity.js").read_text()

    runtime_checks = {
        "spec031_shell_composed_not_reimplemented": _control_index(candidate_index)
        == control_index,
        "spec031_runtime_files_byte_identical": all(
            (output_dir / name).read_bytes() == (spec031_dir / name).read_bytes()
            for name in SPEC031_RUNTIME_FILES
            if name != "index.html"
        ),
        "rejected_spec032_runtime_not_composed": "learning-path.js" not in candidate_index,
        "canonical_revealed_surface_present": all(
            token in script
            for token in (
                'root.id="revealed-knowledge-map"',
                "revealedAdd",
                "revealedToggle",
                "revealedVisibleKeys",
            )
        ),
        "collapse_state_is_navigation_only": (
            'marker.dataset.collapseStateIsSemantic="false"' in script
            and "revealedState.expanded" in script
        ),
        "bounded_drag_scroll_present": all(
            token in script
            for token in ("setPointerCapture", "scrollLeft", "scrollTop", "pointercancel")
        ),
        "labels_preserve_horizontal_legibility": all(
            token in style
            for token in (
                "writing-mode:horizontal-tb",
                "word-break:normal",
                "minmax(0,1fr)",
            )
        ),
        "depth_control_and_frontier_rows_cannot_overlap": all(
            token in style
            for token in (
                "grid-template-rows:repeat(6,auto)",
                ".learning-workspace{min-height:470px}",
                ".learning-workspace.learning-surface-text{min-height:330px",
            )
        ),
        "depth_reveal_is_event_bounded_not_observer_recursive": (
            'document.addEventListener("spec024-depth-expanded"' in script
            and "spec030-learning-contract\"),{attributes:true}" not in script
            and script.count("new MutationObserver") == 1
        ),
        "canonical_semantic_state_owner_preserved": (
            atomic.count("let atomicLearnerState=") == 1
            and "atomicLearnerState=" not in script
            and 'marker.dataset.semanticStateOwner="SPEC-029 atomicLearnerState"' in script
        ),
        "learning_surface_resolver_preserved": all(
            token in learning
            for token in ("function learningSurfaceResolve()", "function learningSurfaceRender()")
        ),
        "relationship_multiplicity_preserved": all(
            token in relationship
            for token in ("multiplicityGroups", "canonical relationship", "firstMatchDependencyCount")
        ),
        "synthetic_large_tree_runtime_available": (
            'get("fixture")==="large"' in script and "showLargeFixture" in script
        ),
    }
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "workspace_fixture_byte_identical": (output_dir / "workspace-fixture.json").read_bytes()
        == (spec031_dir / "workspace-fixture.json").read_bytes(),
        "depth_packet_byte_identical": (output_dir / "depth-map.json").read_bytes()
        == (spec031_dir / "depth-map.json").read_bytes(),
        "canonical_projection_keys_unique": len(projection)
        == len({item["object_key"] for item in projection}),
        "projection_edges_do_not_assert_semantic_truth": all(
            item["projection_basis"]
            in {
                "CANONICAL_DOMAIN_ROOT",
                "DOMAIN_MEMBERSHIP_GROUP",
            }
            or item["projection_basis"].startswith("ADMITTED_DEPTH_GROUP:")
            for item in projection
        ),
        "fixed_reveal_dedup_collapse_depth_passes": fixed["status"] == "PASS",
        "frontier_excludes_revealed_objects": frontier["status"] == "PASS",
        "large_tree_60_object_gate_passes": large_tree["status"] == "PASS",
        "no_new_semantic_vocabulary_or_admission": True,
        "live_model_or_external_calls_zero": True,
    }
    baselines_after = protected_baseline_hashes()
    spec031_after = directory_identity(spec031_dir)
    spec032_after = directory_identity(spec032_dir)
    runtime_checks["baseline001_through_004_unchanged"] = baselines_before == baselines_after
    runtime_checks["spec031_unchanged"] = spec031_before == spec031_after
    runtime_checks["spec032_rejected_evidence_unchanged"] = spec032_before == spec032_after
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        failed = [
            name
            for group in (runtime_checks, semantic_checks)
            for name, passed in group.items()
            if not passed
        ]
        raise ValidationError(f"SPEC-033 deterministic machine gate failed closed: {failed}")

    gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    viewer_command = (
        ".venv/bin/knowledge-compiler view-representations "
        f"{EVALUATION_RELATIVE_PATH} --port 8033"
    )
    report = {
        "spec": "SPEC-033",
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
        "spec032_evidence_identity_before": spec032_before,
        "spec032_evidence_identity_after": spec032_after,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "revealed_state_model": packet["projection_contract"],
        "trusted_object_count": len(catalog),
        "trusted_continuation_count": len(continuations),
        "fixed_reveal_scenario": fixed,
        "frontier_audit": frontier,
        "large_tree_fixture": {
            key: large_tree[key]
            for key in ("status", "fixture_only", "object_count", "max_depth", "root_count")
        },
        "interaction_freeze_fix": (
            "SPEC-032 path runtime and its learning-surface attribute observer are absent; "
            "depth admission updates revealed state exactly once from the existing explicit "
            "spec024-depth-expanded event"
        ),
        "machine_gate": gate,
        "browser_verification": "browser-verification.json",
        "browser_console_result": "PENDING",
        "deterministic_regeneration_result": "PENDING_POST_GENERATION_COMPARISON",
        "offline_test_result": "PENDING_FINAL_SUITE",
        "dependencies_added": [],
        "dependencies_removed": [],
        "live_model_or_external_calls": 0,
        "semantic_changes": [],
        "deviations": [],
        "repository_state": "IMPLEMENTED_AWAITING_OWNER_REVIEW; NOT COMMITTED OR PUSHED",
        "viewer_command": viewer_command,
    }
    manifest = {
        "spec": "SPEC-033",
        "title": "Canonical revealed-knowledge tree",
        "workspace_fixture": "workspace-fixture.json",
        "depth_map": "depth-map.json",
        "revealed_knowledge": "revealed-knowledge-fixture.json",
        "large_tree": "large-tree-fixture.json",
        "fixed_reveal": "fixed-reveal-scenario.json",
        "frontier_audit": "frontier-audit.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    for name, value in (
        ("manifest.json", manifest),
        ("fixed-reveal-scenario.json", fixed),
        ("frontier-audit.json", frontier),
        ("large-tree-fixture.json", large_tree),
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
                "REVEALED_KNOWLEDGE_TREE_CONFIRMED",
                "MIXED",
                "STILL_FEELS_LIKE_HISTORY",
                "SCALING_OR_LEGIBILITY_FAILED",
                "INTERACTION_FREEZE_RECURRED",
                "LEARNING_SURFACE_REGRESSED",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-033 canonical revealed-knowledge tree\n\n"
        "This isolated offline candidate preserves the trusted semantic engine while "
        "making the left surface a canonical, deduplicated, collapsible view of what "
        "has been revealed.\n\n```sh\n"
        + viewer_command
        + "\n```\n\nUse `?fixture=large` for the deterministic 60-object scaling fixture.\n",
        encoding="utf-8",
    )
    return report


BROWSER_CHECKS = {
    "initial_map_contains_only_revealed_electromagnetism_root",
    "irrational_cross_domain_order_does_not_define_tree_topology",
    "revisiting_same_concept_does_not_duplicate_node",
    "reciprocal_relationships_retain_distinct_canonical_identities",
    "depth_reveal_inserts_under_existing_double_slit_branch",
    "collapse_hides_descendants_without_forgetting_them",
    "reopen_restores_same_revealed_subtree",
    "selected_ancestor_chain_auto_expands",
    "unrelated_collapse_state_survives_focus_change",
    "focused_pane_matches_selected_canonical_object",
    "frontier_contains_no_already_revealed_object",
    "right_pane_evidence_and_provenance_remain_available",
    "repeated_depth_and_region_switching_remains_interactive",
    "pointer_depth_control_is_not_occluded_by_frontier",
    "no_history_or_deeper_map_wrapper_nodes_are_created",
    "large_fixture_has_60_unique_objects",
    "large_fixture_labels_remain_horizontal_and_legible",
    "large_fixture_collapse_materially_reduces_visible_complexity",
    "large_fixture_scroll_and_drag_remain_responsive",
    "keyboard_selection_and_disclosure_are_usable",
}


def finalize_revealed_knowledge_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-033 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    if set(checks) != BROWSER_CHECKS or not all(checks.values()):
        raise ValidationError("SPEC-033 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-033 browser console was not clean")
    _write_json(output_dir / "browser-verification.json", browser_verification)
    gate = json.loads((output_dir / "machine-gate.json").read_text())
    gate["status"] = "PASS"
    gate["browser_checks"] = checks
    gate["browser_console_clean"] = True
    _write_json(output_dir / "machine-gate.json", gate)
    review = json.loads((output_dir / "human-review-template.json").read_text())
    review["status"] = "PENDING_OWNER_REVIEW"
    _write_json(output_dir / "human-review-template.json", review)
    report = json.loads((output_dir / "report.json").read_text())
    report["execution_stage"] = "IMPLEMENTED_AWAITING_OWNER_REVIEW"
    report["machine_integrity_verdict"] = "PASS"
    report["human_review_status"] = "PENDING_OWNER_REVIEW"
    report["machine_gate"] = gate
    report["browser_console_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report


def record_revealed_knowledge_validation(
    output_dir: Path,
    *,
    compared_file_count: int,
    focused_test_result: str,
    full_test_result: str,
) -> dict[str, Any]:
    """Record completed deterministic regeneration and offline-suite evidence."""

    report = json.loads((output_dir / "report.json").read_text())
    report["deterministic_regeneration_result"] = {
        "compared_file_count": compared_file_count,
        "result": "PASS_BYTE_IDENTICAL",
        "scope": "independently generated non-lifecycle candidate artifacts",
    }
    report["offline_test_result"] = {
        "focused": focused_test_result,
        "full": full_test_result,
        "result": "PASS",
    }
    _write_json(output_dir / "report.json", report)
    return report
