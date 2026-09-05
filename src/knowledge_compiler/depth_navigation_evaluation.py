"""Build and finalize the deterministic offline SPEC-024 owner-review artifact."""

from __future__ import annotations

import hashlib
import json
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable

from .baseline004 import BASELINE004_EXECUTABLE_HASHES, baseline004_directory, verify_baseline004
from .depth_navigation import (
    DEPTH_EXPANSION_ID,
    DepthMapState,
    build_depth_map_packet,
    close_expansion,
    open_expansion,
    select_depth_item,
)
from .explanatory_projection import FROZEN_SPEC020_HASHES, canonical_bytes
from .learner_navigation import SPEC021_SEMANTIC_HASHES
from .models import ValidationError
from .semantic_depth_review_evaluation import (
    FIX023_DEPTH_RELATIONSHIP_ID,
    FROZEN_SPEC023_TREATMENT_HASHES,
    apply_fix023_depth_entry,
    default_spec020_directory,
    default_spec021_directory,
    protected_baseline_hashes,
    remove_fix023_depth_entry,
)


EVALUATION_NAME = "spec-024-depth-as-continuous-map-expansion-20260905"
EVALUATION_RELATIVE_PATH = f"examples/evaluations/{EVALUATION_NAME}"
FROZEN_SPEC023_DIRECTORY_SHA256 = (
    "e8dba3c16e9d02985c4e908e939fa67f38b0e4cfb82bfcdbd7199298a0686b42"
)
OWNER_REVIEW_INSTRUCTION = (
    "Navigate naturally to the double-slit experiment and explore it more deeply. "
    "Then move around between the deeper material and the surrounding knowledge "
    "world. Tell me whether going deeper now feels like continuing to navigate the "
    "same knowledge space, whether you can still tell how you got there, and anything "
    "that feels awkward or confusing."
)

_INDEX_STYLE_ANCHOR = '  <link rel="stylesheet" href="grammar.css">'
_INDEX_SCRIPT_ANCHOR = '  <script src="learner-grammar.js"></script>'
_SPEC024_STYLE = '  <link rel="stylesheet" href="depth-expansion.css">'
_SPEC024_SCRIPT = '  <script src="depth-expansion.js"></script>'

_BASELINE_REFRESH_PREFIX = (
    "function learnerRefreshChrome(){if(window.__SPEC021_PROJECTION__?.isActive())return;"
)
_SPEC024_REFRESH_PREFIX = (
    "function learnerRefreshChrome(){if(window.__SPEC024_DEPTH__?.isExpanded()&&!window."
    "__BASELINE003_SEAM__.state.selectedEntityId&&!window.__BASELINE003_SEAM__.state."
    "selectedRelationshipId){window.__SPEC024_DEPTH__.refreshChrome();return;}"
    "if(window.__SPEC021_PROJECTION__?.isActive())return;"
)

_FIX023_ENTER = (
    "function learnerEnterDepth(){const api=window.__BASELINE003_SEAM__;"
    "if(!learnerDepthEligible(api.state))throw new Error(\"Depth is not admitted for "
    "this selection\");learnerState.depthSnapshot=api.cameraSnapshot();"
    "window.__SPEC021_PROJECTION__.enter();learnerById(\"context-path\")"
    ".replaceChildren(...[\"Electromagnetism\",\"double-slit experiment\",\"Deeper\"]"
    ".map(text=>learnerElement(\"span\",text)));const returnButton=learnerElement("
    "\"button\",\"Return\",\"projection-return\");returnButton.addEventListener("
    "\"click\",learnerReturnDepth);document.querySelector(\".projection-meta\")"
    ".append(returnButton);learnerById(\"clear-selection\").disabled=true;}"
)
_SPEC024_ENTER = (
    "function learnerEnterDepth(){const api=window.__BASELINE003_SEAM__;"
    "if(!learnerDepthEligible(api.state))throw new Error(\"Depth is not admitted for "
    "this selection\");if(!window.__SPEC024_DEPTH__)throw new Error(\"Depth map is "
    "not ready\");learnerState.depthSnapshot=api.cameraSnapshot();window.__SPEC024_DEPTH__"
    ".expand({originEntityId:api.state.selectedEntityId,originRelationshipId:"
    "api.state.selectedRelationshipId});}"
)
_FIX023_RETURN = (
    "function learnerReturnDepth(){if(!window.__SPEC021_PROJECTION__?.isActive())return;"
    "window.__SPEC021_PROJECTION__.exit();learnerState.depthSnapshot=null;"
    "learnerRefreshChrome();}"
)
_SPEC024_RETURN = (
    "function learnerReturnDepth(){if(!window.__SPEC024_DEPTH__?.isExpanded())return;"
    "window.__SPEC024_DEPTH__.collapse();learnerState.depthSnapshot=null;"
    "learnerRefreshChrome();}"
)
_FIX023_LOCAL = (
    "function learnerLocalDepth(){const existing=learnerById(\"learning-detail\")"
    ".querySelector(\".contextual-depth\"),eligible=!window.__SPEC021_PROJECTION__?"
    ".isActive()&&learnerDepthEligible(window.__BASELINE003_SEAM__.state);if(!eligible)"
    "{existing?.remove();return;}if(existing)return;const button=learnerElement(\"button\","
    "\"Explore deeper\",\"contextual-depth\");button.addEventListener(\"click\","
    "learnerEnterDepth);learnerById(\"learning-detail\").append(button);}"
)
_SPEC024_LOCAL = (
    "function learnerLocalDepth(){const existing=learnerById(\"learning-detail\")"
    ".querySelector(\".contextual-depth\"),eligible=!window.__SPEC024_DEPTH__?"
    ".isExpanded()&&learnerDepthEligible(window.__BASELINE003_SEAM__.state);if(!eligible)"
    "{existing?.remove();return;}if(existing)return;const button=learnerElement(\"button\","
    "\"Explore deeper\",\"contextual-depth\");button.addEventListener(\"click\","
    "learnerEnterDepth);learnerById(\"learning-detail\").append(button);}"
)


def repository_root() -> Path:
    return Path(__file__).parents[2]


def default_spec023_directory() -> Path:
    return repository_root() / "examples/evaluations/spec-023-realistic-semantic-depth-20260905"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def _directory_identity(directory: Path) -> dict[str, Any]:
    file_hashes = {
        str(path.relative_to(directory)): _hash(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }
    try:
        location = str(directory.resolve().relative_to(repository_root()))
    except ValueError:
        location = str(directory.resolve())
    return {
        "directory": location,
        "file_count": len(file_hashes),
        "files": file_hashes,
        "aggregate_sha256": hashlib.sha256(canonical_bytes(file_hashes)).hexdigest(),
    }


def _verify_spec023(directory: Path) -> dict[str, Any]:
    identity = _directory_identity(directory)
    if identity["aggregate_sha256"] != FROZEN_SPEC023_DIRECTORY_SHA256:
        raise ValidationError("SPEC-023/FIX-023 historical artifact identity mismatch")
    return identity


def _extend_index(source: str) -> str:
    if source.count(_INDEX_STYLE_ANCHOR) != 1 or source.count(_INDEX_SCRIPT_ANCHOR) != 1:
        raise ValidationError("BASELINE-004 HTML extension seam changed")
    return source.replace(
        _INDEX_STYLE_ANCHOR,
        f"{_INDEX_STYLE_ANCHOR}\n{_SPEC024_STYLE}",
    ).replace(
        _INDEX_SCRIPT_ANCHOR,
        f"{_INDEX_SCRIPT_ANCHOR}\n{_SPEC024_SCRIPT}",
    )


def _remove_index_extension(source: str) -> str:
    return source.replace(f"\n{_SPEC024_STYLE}", "").replace(f"\n{_SPEC024_SCRIPT}", "")


def apply_spec024_depth_navigation(source: str) -> str:
    """Replace only FIX-023's nested entry/return seam with map expansion."""

    result = apply_fix023_depth_entry(source)
    for before, after in (
        (_BASELINE_REFRESH_PREFIX, _SPEC024_REFRESH_PREFIX),
        (_FIX023_ENTER, _SPEC024_ENTER),
        (_FIX023_RETURN, _SPEC024_RETURN),
        (_FIX023_LOCAL, _SPEC024_LOCAL),
    ):
        if result.count(before) != 1:
            raise ValidationError("SPEC-024 learner depth seam changed")
        result = result.replace(before, after)
    return result


def remove_spec024_depth_navigation(source: str) -> str:
    result = source
    for candidate, fixed in (
        (_SPEC024_REFRESH_PREFIX, _BASELINE_REFRESH_PREFIX),
        (_SPEC024_ENTER, _FIX023_ENTER),
        (_SPEC024_RETURN, _FIX023_RETURN),
        (_SPEC024_LOCAL, _FIX023_LOCAL),
    ):
        if result.count(candidate) != 1:
            raise ValidationError("SPEC-024 learner depth seam identity mismatch")
        result = result.replace(candidate, fixed)
    return result


def nested_expansion_regression() -> dict[str, Any]:
    registry = {
        "root": {"id": "root", "parent_expansion_id": None},
        "child": {"id": "child", "parent_expansion_id": "root"},
        "grandchild": {"id": "grandchild", "parent_expansion_id": "child"},
    }
    state = DepthMapState()
    state = open_expansion(state, registry, "root")
    state = open_expansion(state, registry, "child")
    state = open_expansion(state, registry, "grandchild")
    opened = state.open_path
    state = select_depth_item(state, "concept", "synthetic-item")
    state = close_expansion(state, "child")
    checks = {
        "three_level_path_represented": opened == ("root", "child", "grandchild"),
        "closing_parent_closes_descendants": state.open_path == ("root",),
        "selection_cleared_on_retraction": state.selected_id is None,
        "camera_not_encoded_in_depth_state": not hasattr(state, "camera"),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}


def _reject_protected_output(output_dir: Path, protected: Iterable[Path]) -> None:
    resolved = output_dir.resolve()
    for directory in protected:
        candidate = directory.resolve()
        if resolved == candidate or resolved.is_relative_to(candidate):
            raise ValidationError("SPEC-024 output must be isolated from frozen artifacts")


def prepare_depth_navigation_evaluation(
    *,
    output_dir: Path,
    baseline_dir: Path = baseline004_directory(),
    spec020_dir: Path = default_spec020_directory(),
    spec021_dir: Path = default_spec021_directory(),
    spec023_dir: Path = default_spec023_directory(),
) -> dict[str, Any]:
    _reject_protected_output(
        output_dir,
        (repository_root() / "baselines", baseline_dir, spec020_dir, spec021_dir, spec023_dir),
    )
    baseline_before = protected_baseline_hashes()
    baseline004_hashes = verify_baseline004(baseline_dir)
    spec023_before = _verify_spec023(spec023_dir)
    spec020_hashes = {name: _hash(spec020_dir / name) for name in FROZEN_SPEC020_HASHES}
    if spec020_hashes != FROZEN_SPEC020_HASHES:
        raise ValidationError("SPEC-020 frozen semantic input identity mismatch")
    spec021_hashes = {name: _hash(spec021_dir / name) for name in SPEC021_SEMANTIC_HASHES}
    if spec021_hashes != SPEC021_SEMANTIC_HASHES:
        raise ValidationError("SPEC-021 explanatory semantic payload identity mismatch")
    projection = json.loads((spec021_dir / "projection.json").read_text(encoding="utf-8"))
    packet = build_depth_map_packet(projection)

    output_dir.mkdir(parents=True, exist_ok=False)
    for name in BASELINE004_EXECUTABLE_HASHES:
        shutil.copyfile(baseline_dir / name, output_dir / name)
    baseline_index = (baseline_dir / "index.html").read_text(encoding="utf-8")
    (output_dir / "index.html").write_text(_extend_index(baseline_index), encoding="utf-8")
    baseline_learner = (baseline_dir / "learner-grammar.js").read_text(encoding="utf-8")
    candidate_learner = apply_spec024_depth_navigation(baseline_learner)
    (output_dir / "learner-grammar.js").write_text(candidate_learner, encoding="utf-8")
    assets = files("knowledge_compiler").joinpath("depth_navigation_assets")
    for name in ("depth-expansion.css", "depth-expansion.js"):
        with assets.joinpath(name).open("rb") as source, (output_dir / name).open("wb") as target:
            shutil.copyfileobj(source, target)
    for name in ("projection-diagnostics.json", "semantic-tier-audit.json"):
        shutil.copyfile(spec021_dir / name, output_dir / name)
    _write_json(output_dir / "depth-map.json", packet)

    candidate_hashes = {
        path.name: _hash(path)
        for path in sorted(output_dir.iterdir())
        if path.is_file()
    }
    script = (output_dir / "depth-expansion.js").read_text(encoding="utf-8")
    css = (output_dir / "depth-expansion.css").read_text(encoding="utf-8")
    nested = nested_expansion_regression()
    semantic_checks = {
        "spec020_frozen_inputs_unchanged": spec020_hashes == FROZEN_SPEC020_HASHES,
        "spec021_projection_payload_unchanged": spec021_hashes == SPEC021_SEMANTIC_HASHES,
        "spec023_treatment_files_reused_byte_identically": {
            name: _hash(output_dir / name) for name in FROZEN_SPEC023_TREATMENT_HASHES
        } == FROZEN_SPEC023_TREATMENT_HASHES,
        "known_rejected_causal_item_remains_noncanonical": any(
            item["assertion_id"] == "assertion-ae10fa8748fdac1f"
            and item["semantic_tier"] == "SOURCE_BACKED_NON_CANONICAL"
            for item in packet["expansions"][0]["explanatory_items"]
        ),
        "known_rejected_causal_item_not_promoted": all(
            item["assertion_id"] != "assertion-ae10fa8748fdac1f"
            for item in packet["expansions"][0]["canonical_items"]
        ),
        "pairwise_edge_fabrication_count_zero": len(packet["expansions"][0]["canonical_items"])
        == len(projection["canonical_items"]),
        "origin_path_explicitly_noncanonical": packet["expansions"][0]["semantic_connection_kind"]
        == "SPATIAL_DEPTH_ORIGIN_NOT_CANONICAL_EDGE",
    }
    runtime_checks = {
        "baseline004_source_identity_verified": baseline004_hashes == BASELINE004_EXECUTABLE_HASHES,
        "baseline004_shell_composed_not_reimplemented": _remove_index_extension(
            (output_dir / "index.html").read_text(encoding="utf-8")
        ) == baseline_index,
        "baseline004_workspace_engine_byte_identical": (output_dir / "workspace.js").read_bytes()
        == (baseline_dir / "workspace.js").read_bytes(),
        "baseline004_styles_byte_identical": (output_dir / "workspace.css").read_bytes()
        == (baseline_dir / "workspace.css").read_bytes(),
        "baseline004_fixture_and_coordinates_byte_identical": (
            output_dir / "workspace-fixture.json"
        ).read_bytes() == (baseline_dir / "workspace-fixture.json").read_bytes(),
        "learner_grammar_reuses_fix023_then_varies_only_depth_transition": (
            remove_fix023_depth_entry(remove_spec024_depth_navigation(candidate_learner))
            == baseline_learner
        ),
        "contextual_depth_relationship_preserved": FIX023_DEPTH_RELATIONSHIP_ID
        in candidate_learner,
        "nested_right_navigation_not_entered": "__SPEC021_PROJECTION__.enter()"
        not in candidate_learner,
        "map_expansion_api_used": "__SPEC024_DEPTH__.expand" in candidate_learner,
        "visible_spatial_origin_path_present": all(
            token in script for token in ("depth-origin-path", "DEEPER FROM", "depth-entry")
        ),
        "expanded_bounds_use_existing_camera_engine": all(
            token in script for token in ("expanded_world_bounds", "api.setCamera", "api.clampCamera")
        ),
        "deep_items_use_right_detail_and_evidence": all(
            token in script
            for token in (
                'depthById("learning-detail")',
                "Trusted canonical relationship",
                "Source-backed explanation · non-canonical",
                "Show exact source evidence",
            )
        ),
        "retraction_restores_parent_camera_and_selection": all(
            token in script
            for token in (
                "parentSnapshot=api.cameraSnapshot()",
                "api.state.selectedEntityId=snapshot.selectedEntityId",
                "api.setCamera(snapshot.camera,false)",
            )
        ),
        "recursive_open_path_supported": all(
            token in script for token in ("openPath", "parent_expansion_id", "Depth expansion parent is not open")
        ) and nested["status"] == "PASS",
        "browser_selection_suppression_preserved": "user-select:none" in (
            output_dir / "workspace.css"
        ).read_text(encoding="utf-8"),
        "spec024_style_is_additive": "SPEC-024 composes" in css,
    }
    baseline_after = protected_baseline_hashes()
    spec023_after = _verify_spec023(spec023_dir)
    runtime_checks["baseline001_through_004_unchanged"] = baseline_before == baseline_after
    runtime_checks["spec023_historical_artifact_unchanged"] = spec023_before == spec023_after
    if not all(runtime_checks.values()) or not all(semantic_checks.values()):
        raise ValidationError("SPEC-024 deterministic machine gate failed closed")

    machine_gate = {
        "status": "PASS_PENDING_BROWSER",
        "runtime_checks": runtime_checks,
        "semantic_checks": semantic_checks,
        "nested_expansion_regression": nested,
        "browser_checks": "PENDING_MANUAL_BROWSER_VERIFICATION",
    }
    report = {
        "spec": "SPEC-024",
        "execution_mode": "OFFLINE_DETERMINISTIC",
        "execution_stage": "PENDING_BROWSER_VERIFICATION",
        "machine_integrity_verdict": "PASS_PENDING_BROWSER",
        "human_review_status": "NOT_YET_AVAILABLE",
        "product_verdict": "PENDING_OWNER_REVIEW",
        "owner_review_instruction": OWNER_REVIEW_INSTRUCTION,
        "integration_seam": (
            "additive recursive map-expansion layer over the byte-identical BASELINE-004 "
            "workspace engine; the frozen explanatory projection remains the semantic payload"
        ),
        "origin_and_path_representation": (
            "a labeled dashed spatial path connects the parent double-slit node to a translated "
            "copy of the frozen focus-centered projection in the same pan/zoom world"
        ),
        "baseline_hashes_before": baseline_before,
        "baseline_hashes_after": baseline_after,
        "baseline004_executable_hashes": baseline004_hashes,
        "spec020_input_hashes": spec020_hashes,
        "spec021_projection_hashes": spec021_hashes,
        "spec023_historical_identity_before": spec023_before,
        "spec023_historical_identity_after": spec023_after,
        "candidate_runtime_hashes_at_prepare": candidate_hashes,
        "machine_gate": machine_gate,
        "nested_expansion_regression": nested,
        "camera_pan_zoom_result": "PASS_PENDING_BROWSER",
        "selection_and_evidence_synchronization_result": "PASS_PENDING_BROWSER",
        "deterministic_regeneration_result": "PENDING_OFFLINE_VERIFICATION",
        "offline_test_result": "PENDING",
        "browser_verification": "browser-verification.json",
        "files_changed": "PENDING_FINAL_INVENTORY",
        "repository_state": "PENDING_COMMIT_AND_PUSH",
        "dependencies_added": [],
        "dependencies_removed": [],
        "live_model_or_external_calls": 0,
        "semantic_changes": [],
        "semantic_vocabulary_or_admission_changes": [],
        "representation_algorithm_changes": [],
        "ui_behavior_changes": [
            "contextual double-slit depth opens as a reversible continuous-map expansion"
        ],
        "deviations": [],
        "viewer_command": (
            ".venv/bin/knowledge-compiler view-representations "
            f"{EVALUATION_RELATIVE_PATH} --port 8024"
        ),
    }
    manifest = {
        "spec": "SPEC-024",
        "title": "Depth as continuous map expansion",
        "workspace_fixture": "workspace-fixture.json",
        "projection": "projection.json",
        "depth_map": "depth-map.json",
        "machine_gate": "machine-gate.json",
        "browser_verification": "browser-verification.json",
        "human_review": "human-review-template.json",
        "report": "report.json",
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "machine-gate.json", machine_gate)
    _write_json(
        output_dir / "input-manifest.json",
        {
            "baseline004": {"directory": str(baseline_dir.relative_to(repository_root())), "hashes": baseline004_hashes},
            "spec020": {"directory": str(spec020_dir.relative_to(repository_root())), "hashes": spec020_hashes},
            "spec021": {"directory": str(spec021_dir.relative_to(repository_root())), "hashes": spec021_hashes},
            "spec023": spec023_before,
            "identity_verified": True,
        },
    )
    _write_json(output_dir / "report.json", report)
    _write_json(output_dir / "browser-verification.json", {"status": "PENDING_MANUAL_BROWSER_VERIFICATION", "checks": {}, "console": {}})
    _write_json(
        output_dir / "human-review-template.json",
        {
            "instruction": OWNER_REVIEW_INSTRUCTION,
            "status": "BLOCKED_PENDING_MACHINE_GATE",
            "owner_response": None,
            "verdict": "PENDING",
            "allowed_verdicts": [
                "DEPTH_NAVIGATION_BETTER",
                "MIXED",
                "NESTED_DEPTH_BETTER",
                "INCONCLUSIVE",
            ],
        },
    )
    (output_dir / "README.md").write_text(
        "# SPEC-024 depth as continuous map expansion\n\n"
        "This isolated offline artifact composes a spatial depth layer with the frozen "
        "BASELINE-004 learner workspace and frozen SPEC-020/021 semantics.\n\n"
        f"```sh\n{report['viewer_command']}\n```\n",
        encoding="utf-8",
    )
    return report


def finalize_depth_navigation_evaluation(
    output_dir: Path, browser_verification: dict[str, Any]
) -> dict[str, Any]:
    """Admit a complete browser check without assigning the owner verdict."""

    if browser_verification.get("status") != "PASS":
        raise ValidationError("SPEC-024 browser verification did not pass")
    checks = browser_verification.get("checks", {})
    required = {
        "ordinary_navigation_intact",
        "contextual_explore_deeper",
        "left_map_expands",
        "origin_path_visible",
        "deep_concept_selection_syncs_right",
        "canonical_relationship_evidence_syncs_right",
        "noncanonical_explanation_labeled_and_evidence_reveals",
        "parent_world_remains_navigable",
        "pan_zoom_with_expansion",
        "collapse_restores_parent_state",
        "no_blue_selection_artifact",
    }
    if set(checks) != required or not all(checks.values()):
        raise ValidationError("SPEC-024 browser verification is incomplete")
    console = browser_verification.get("console", {})
    if console.get("errors") != [] or console.get("warnings") != []:
        raise ValidationError("SPEC-024 browser console was not clean")
    _write_json(output_dir / "browser-verification.json", browser_verification)
    gate = json.loads((output_dir / "machine-gate.json").read_text(encoding="utf-8"))
    gate["status"] = "PASS"
    gate["browser_checks"] = checks
    gate["browser_console_clean"] = True
    _write_json(output_dir / "machine-gate.json", gate)
    review = json.loads((output_dir / "human-review-template.json").read_text(encoding="utf-8"))
    review["status"] = "PENDING_OWNER_REVIEW"
    _write_json(output_dir / "human-review-template.json", review)
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    report["execution_stage"] = "IMPLEMENTED_AWAITING_OWNER_REVIEW"
    report["machine_integrity_verdict"] = "PASS"
    report["human_review_status"] = "PENDING_OWNER_REVIEW"
    report["machine_gate"] = gate
    report["camera_pan_zoom_result"] = "PASS"
    report["selection_and_evidence_synchronization_result"] = "PASS"
    _write_json(output_dir / "report.json", report)
    return report
