from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from knowledge_compiler.assertion_compilation import (
    AssertionExtractionProposal,
    CanonicalizationProposal,
)
from knowledge_compiler.continuous_navigation import CameraState
from knowledge_compiler.models import KnowledgeModel, ValidationError
from knowledge_compiler.semantic_depth import (
    CHILD_SYMBOL_IDS,
    EXPECTED_SCOPE_SHA256,
    FOCUS_ENTITY_ID,
    DepthWorkspaceState,
    build_depth_workspace_fixture,
    child_symbol_table,
    depth_camera_invariant,
    freeze_focus_selection,
    freeze_source_scope,
    model_hash,
    switch_semantic_depth,
)
from knowledge_compiler.semantic_depth_evaluation import (
    default_baseline003_assets,
    default_baseline003_document,
    default_spec013_directory,
    finalize_semantic_depth_evaluation,
    prepare_semantic_depth_evaluation,
    run_semantic_depth_evaluation,
)
from knowledge_compiler.representations import RepresentationModel


def _load_parent() -> KnowledgeModel:
    path = default_spec013_directory() / "parent.knowledge.json"
    return KnowledgeModel.from_dict(json.loads(path.read_text(encoding="utf-8")))


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


class FixtureCompiler:
    def __init__(self, *, bad_quote: bool = False, fail_canonical: bool = False) -> None:
        self.bad_quote = bad_quote
        self.fail_canonical = fail_canonical
        self.canonicalization_called = False
        self.last_assertion_raw = None
        self.last_canonicalization_raw = None
        self.last_assertion_metadata = {
            "provider": "fixture", "model": "fixture", "requested_model": "fixture",
            "prompt_version": "spec-013-assertions-v1", "usage": {},
        }
        self.last_canonicalization_metadata = {
            "provider": "fixture", "model": "fixture", "requested_model": "fixture",
            "prompt_version": "spec-013-canonicalization-v1", "usage": {},
        }

    def extract_assertions(self, document, symbols):
        raw = {
            "assertions": [
                {
                    "statement": "Wave–particle duality is an example of quantum complementarity.",
                    "participant_entity_ids": ["waveparticle-duality", "principle-of-complementarity"],
                    "evidence": [{"quote": "missing" if self.bad_quote else "Wave–particle duality is an example of the principle of complementarity in quantum physics."}],
                    "origin": "SOURCE",
                },
                {
                    "statement": "The double-slit experiment is an example of wave–particle duality.",
                    "participant_entity_ids": ["double-slit-experiment", "waveparticle-duality"],
                    "evidence": [{"quote": "An elegant example of wave-particle duality is the double-slit experiment."}],
                    "origin": "SOURCE",
                },
                {
                    "statement": "The double-slit experiment produces an interference pattern.",
                    "participant_entity_ids": ["double-slit-experiment", "interference-pattern", "photon"],
                    "evidence": [{"quote": "a beam of light is directed through two narrow, closely spaced slits, producing an interference pattern of light and dark bands on a screen."}],
                    "origin": "SOURCE",
                },
                {
                    "statement": "Electron and atom variations produce the same interference pattern.",
                    "participant_entity_ids": ["double-slit-experiment", "electron", "atom", "interference-pattern"],
                    "evidence": [{"quote": "Variations of the double-slit experiment have been performed using electrons, atoms, and even large molecules, and the same type of interference pattern is seen."}],
                    "origin": "SOURCE",
                },
            ]
        }
        self.last_assertion_raw = raw
        return AssertionExtractionProposal.from_dict({**raw, "metadata": self.last_assertion_metadata})

    def canonicalize_assertions(self, assertions, symbols):
        self.canonicalization_called = True
        if self.fail_canonical:
            raise ValidationError("fixture canonicalization failure")
        by_statement = {item.statement: item.id for item in assertions.assertions}
        raw = {
            "relationships": [
                {
                    "assertion_id": by_statement["Wave–particle duality is an example of quantum complementarity."],
                    "source_entity_id": "waveparticle-duality",
                    "relationship_type": "EXAMPLE_OF",
                    "target_entity_id": "principle-of-complementarity",
                    "statement": "Wave–particle duality is an example of quantum complementarity.",
                    "confidence": 0.98,
                },
                {
                    "assertion_id": by_statement["The double-slit experiment is an example of wave–particle duality."],
                    "source_entity_id": "double-slit-experiment",
                    "relationship_type": "EXAMPLE_OF",
                    "target_entity_id": "waveparticle-duality",
                    "statement": "The double-slit experiment is an example of wave–particle duality.",
                    "confidence": 0.98,
                },
                {
                    "assertion_id": by_statement["The double-slit experiment produces an interference pattern."],
                    "source_entity_id": "double-slit-experiment",
                    "relationship_type": "CAUSES",
                    "target_entity_id": "interference-pattern",
                    "statement": "The double-slit experiment produces an interference pattern.",
                    "confidence": 0.97,
                },
            ],
            "propositions": [],
            "claims": [{
                "assertion_id": by_statement["Electron and atom variations produce the same interference pattern."],
                "statement": "Electron and atom variations produce the same interference pattern.",
                "confidence": 0.96,
            }],
            "uncompiled_assertions": [],
        }
        self.last_canonicalization_raw = raw
        return CanonicalizationProposal.from_dict({**raw, "metadata": self.last_canonicalization_metadata})


def _prepare_and_run(tmp_path: Path) -> Path:
    output = tmp_path / "evaluation"
    prepare_semantic_depth_evaluation(output_dir=output, model="fixture")
    report = run_semantic_depth_evaluation(
        output_dir=output,
        model="fixture",
        compiler_factory=FixtureCompiler,
    )
    assert report["execution_stage"] == "PENDING_INDEPENDENT_REPOSITORY_SEMANTIC_REVIEW"
    return output


def _approve_review(output: Path) -> None:
    path = output / "semantic-review.json"
    review = json.loads(path.read_text(encoding="utf-8"))
    review["status"] = "COMPLETE"
    for item in review["assertion_items"]:
        item["classification"] = "FAITHFUL"
        item["notes"] = "Exact fixture statement and evidence preserve the source meaning."
    for item in review["canonical_items"]:
        item["classification"] = "SUPPORTED"
        item["notes"] = "Endpoints and canonical predicate are supported by the cited source."
    review["trusted_child"] = True
    path.write_text(json.dumps(review, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def test_focus_and_source_scope_are_frozen_from_committed_parent() -> None:
    parent = _load_parent()
    focus = freeze_focus_selection(parent)
    scope = freeze_source_scope(parent)
    symbols = child_symbol_table(parent)

    assert focus["entity_id"] == FOCUS_ENTITY_ID
    assert focus["selection_status"] == "FROZEN_BEFORE_LIVE_OUTPUT"
    assert focus["parent_relationship_id"] == "relationship-05b19ee4b6d50060"
    assert len(focus["alternatives_not_selected"]) == 3
    assert (scope.start_char, scope.end_char) == (11574, 13300)
    assert len(scope.text) == 1726
    assert scope.sha256 == EXPECTED_SCOPE_SHA256
    assert scope.text.startswith("Wave–particle duality\n\n")
    assert scope.text.endswith("produced by waves.\n")
    assert tuple(item.id for item in symbols.entities) == CHILD_SYMBOL_IDS
    assert symbols.ids.issubset({item.id for item in parent.entities})


def test_pre_live_packet_is_deterministic_and_preserves_parent_and_baselines(tmp_path: Path) -> None:
    parent = _load_parent()
    parent_hash = model_hash(parent)
    baseline_before = (
        hashlib.sha256(default_baseline003_document().read_bytes()).hexdigest(),
        _directory_hashes(default_baseline003_assets()),
    )
    left, right = tmp_path / "left", tmp_path / "right"
    first = prepare_semantic_depth_evaluation(output_dir=left, model="fixture")
    second = prepare_semantic_depth_evaluation(output_dir=right, model="fixture")

    assert first == second
    assert first["execution_stage"] == "PRE_LIVE_READY"
    assert first["live_call_count"] == 0
    for name in (
        "focus-selection.json", "source-scope.json", "child-symbol-table.json",
        "parent.representation.json", "parent-hashes.json", "baseline-manifest.json",
        "prompt-configuration.json", "run-history.json", "report.json",
    ):
        assert (left / name).read_bytes() == (right / name).read_bytes()
    assert model_hash(_load_parent()) == parent_hash
    assert baseline_before == (
        hashlib.sha256(default_baseline003_document().read_bytes()).hexdigest(),
        _directory_hashes(default_baseline003_assets()),
    )


def test_child_pipeline_reuses_assertion_grounding_and_fails_closed_before_call_b(tmp_path: Path) -> None:
    output = tmp_path / "bad-grounding"
    compiler = FixtureCompiler(bad_quote=True)
    prepare_semantic_depth_evaluation(output_dir=output, model="fixture")
    report = run_semantic_depth_evaluation(
        output_dir=output,
        model="fixture",
        compiler_factory=lambda: compiler,
    )

    assert report["execution_stage"] == "ASSERTION_STAGE_FAILED_CLOSED"
    assert report["rejected_child_rendered"] is False
    assert compiler.canonicalization_called is False
    assert not (output / "workspace-fixture.json").exists()
    history = json.loads((output / "run-history.json").read_text())
    assert len(history["attempts"]) == 1
    assert history["semantic_retry_count"] == 0


def test_canonicalization_failure_preserves_rejected_boundary_and_never_renders(tmp_path: Path) -> None:
    output = tmp_path / "bad-canonical"
    prepare_semantic_depth_evaluation(output_dir=output, model="fixture")
    report = run_semantic_depth_evaluation(
        output_dir=output,
        model="fixture",
        compiler_factory=lambda: FixtureCompiler(fail_canonical=True),
    )

    assert report["execution_stage"] == "CANONICALIZATION_STAGE_FAILED_CLOSED"
    assert report["rejected_child_rendered"] is False
    assert (output / "child-grounded-assertions.json").exists()
    assert not (output / "child.knowledge.json").exists()
    assert not (output / "workspace-fixture.json").exists()


def test_trusted_child_round_trip_structure_evidence_and_no_entity_minting(tmp_path: Path) -> None:
    output = _prepare_and_run(tmp_path)
    child = KnowledgeModel.from_dict(json.loads((output / "child.knowledge.json").read_text()))
    scope = json.loads((output / "source-scope.json").read_text())
    representation = RepresentationModel.from_dict(
        json.loads((output / "child.representation.json").read_text())
    )
    admission = json.loads((output / "semantic-admission.json").read_text())

    assert KnowledgeModel.from_dict(child.to_dict()) == child
    assert {item.id for item in child.entities} == set(CHILD_SYMBOL_IDS)
    assert admission["trusted_gate"]["no_silent_entity_minting"] is True
    assert all(admission["trusted_gate"].values())
    assert representation.representations
    assert any(
        node.entity_id == FOCUS_ENTITY_ID
        for item in representation.representations for node in item.nodes
    )
    for item in (*child.claims, *child.relationships, *child.propositions):
        for evidence in item.evidence:
            assert evidence.quote == scope["text"][evidence.start_char:evidence.end_char]


def test_repository_review_gate_withholds_then_admits_workspace(tmp_path: Path) -> None:
    output = _prepare_and_run(tmp_path)
    assert not (output / "workspace-fixture.json").exists()
    with pytest.raises(ValidationError, match="fidelity classification"):
        finalize_semantic_depth_evaluation(output)

    _approve_review(output)
    report = finalize_semantic_depth_evaluation(output)
    fixture = json.loads((output / "workspace-fixture.json").read_text())
    diagnostics = json.loads((output / "workspace-diagnostics.json").read_text())

    assert report["execution_stage"] == "PENDING_OWNER_COGNITIVE_REVIEW"
    assert report["product_verdict"] == "PENDING"
    assert fixture["semantic_depth"]["navigation_world_replaced"] is False
    assert fixture["semantic_depth"]["maximum_child_depth"] == 1
    assert diagnostics["parent_navigation"]["stable"] is True
    assert diagnostics["semantic_depth"]["parent_to_child_camera_unchanged"] is True
    assert diagnostics["semantic_depth"]["child_to_parent_camera_unchanged"] is True


def test_semantic_depth_state_keeps_camera_independent() -> None:
    parent = DepthWorkspaceState(camera=CameraState(240, 180, 1.4))
    child = switch_semantic_depth(parent, "CHILD")
    returned = switch_semantic_depth(child, "PARENT")

    assert depth_camera_invariant(parent, child)
    assert depth_camera_invariant(child, returned)
    assert returned.focused_entity_id == FOCUS_ENTITY_ID
    assert returned.level == "PARENT"


def test_viewer_preserves_hybrid_shell_and_explicit_depth_interaction(tmp_path: Path) -> None:
    output = _prepare_and_run(tmp_path)
    _approve_review(output)
    finalize_semantic_depth_evaluation(output)
    html = (output / "index.html").read_text()
    css = (output / "workspace.css").read_text()
    depth_css = (output / "depth.css").read_text()
    javascript = (output / "workspace.js").read_text()

    assert 'id="navigation-pane"' in html and 'id="learning-pane"' in html
    assert 'id="depth-toggle"' in html
    assert 'id="context-path"' in html and 'id="learning-detail"' in html
    assert ".nav-node:focus,.learn-node:focus { outline:none; }" in css
    assert "button:focus-visible" in css
    assert ".depth-control" in depth_css
    assert 'viewport.addEventListener("wheel"' in javascript
    assert "toggleDepth()" in javascript
    assert 'state.level==="CHILD"' in javascript
    assert "setCamera(focusTarget(entityId))" in javascript
    assert "geometric" not in javascript.lower()


def test_workspace_fixture_rejects_child_entity_outside_parent(tmp_path: Path) -> None:
    output = _prepare_and_run(tmp_path)
    parent = _load_parent()
    parent_representation = RepresentationModel.from_dict(
        json.loads((output / "parent.representation.json").read_text())
    )
    child_representation = json.loads((output / "child.representation.json").read_text())
    child_representation["representations"][0]["nodes"][0]["entity_id"] = "minted"
    with pytest.raises(ValidationError):
        build_depth_workspace_fixture(
            parent,
            parent_representation,
            RepresentationModel.from_dict(child_representation),
        )
