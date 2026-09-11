import hashlib
import inspect
import json
from pathlib import Path

import pytest

from knowledge_compiler.blind_evaluation import (
    BlindSourcePacket,
    DryRunProposalAdapter,
    blind_source_packet_schema,
    run_blind_evaluation,
)
from knowledge_compiler.blind_evaluation_harness import (
    BROWSER_CHECKS,
    EVALUATION_NAME,
    FROZEN_SPEC038_DIRECTORY_SHA256,
    finalize_blind_evaluation_harness,
    prepare_blind_evaluation_harness,
    proposed_live_execution_plan,
    synthetic_proposals,
    synthetic_source_packet,
)
from knowledge_compiler.cli import main
from knowledge_compiler.depth_interaction_evaluation import directory_identity
from knowledge_compiler.models import ValidationError


ROOT = Path(__file__).parents[1]
FROZEN_COMMIT = "0" * 40


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hashes(directory: Path, excluded: set[str] | None = None) -> dict[str, str]:
    excluded = excluded or set()
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name not in excluded
    }


def _browser_pass() -> dict:
    return {
        "status": "PASS",
        "browser": "deterministic test fixture",
        "checks": {name: True for name in BROWSER_CHECKS},
        "console": {"errors": [], "warnings": [], "result": "PASS"},
        "observations": {"protected_runtime_loaded": True},
    }


def test_source_packet_example_validates_and_supplies_no_expected_answers() -> None:
    raw = synthetic_source_packet()
    packet = BlindSourcePacket.from_dict(raw)
    assert packet.to_dict() == raw
    assert packet.to_dict()["evaluation_contract"] == {
        "expected_representation_strategy_supplied": False
    }
    encoded = json.dumps(packet.to_dict(), sort_keys=True)
    for forbidden in blind_source_packet_schema()["forbidden_evaluator_fields"]:
        assert f'"{forbidden}"' not in encoded


@pytest.mark.parametrize(
    "field",
    [
        "expected_concepts",
        "expected_relationships",
        "expected_structure_type",
        "expected_representation_strategy",
        "expected_diagram_topology",
    ],
)
def test_source_packet_rejects_representation_prescriptive_fields(field: str) -> None:
    raw = synthetic_source_packet()
    raw["sources"][0]["provenance"][field] = "not allowed"
    with pytest.raises(ValidationError, match="representation-prescriptive"):
        BlindSourcePacket.from_dict(raw)


def test_source_packet_fails_closed_on_hash_mismatch_and_noncanonical_text() -> None:
    mismatch = synthetic_source_packet()
    mismatch["sources"][0]["source_sha256"] = "f" * 64
    with pytest.raises(ValidationError, match="does not match"):
        BlindSourcePacket.from_dict(mismatch)
    noncanonical = synthetic_source_packet()
    noncanonical["sources"][0]["text"] += "\n"
    noncanonical["sources"][0]["source_sha256"] = hashlib.sha256(
        noncanonical["sources"][0]["text"].encode()
    ).hexdigest()
    with pytest.raises(ValidationError, match="canonically normalized"):
        BlindSourcePacket.from_dict(noncanonical)


def test_source_packet_rejects_duplicate_source_ids() -> None:
    raw = synthetic_source_packet()
    raw["sources"][1]["source_id"] = raw["sources"][0]["source_id"]
    with pytest.raises(ValidationError, match="IDs must be unique"):
        BlindSourcePacket.from_dict(raw)


def test_live_capable_adapter_is_rejected_before_invocation(tmp_path: Path) -> None:
    class TrapAdapter:
        live_capable = True

        def __init__(self):
            self.called = False

        def extract_once(self, document):
            self.called = True
            raise AssertionError("must never be called")

    adapter = TrapAdapter()
    with pytest.raises(ValidationError, match="explicit authority"):
        run_blind_evaluation(
            BlindSourcePacket.from_dict(synthetic_source_packet()),
            adapter,
            output_dir=tmp_path / "blocked",
        )
    assert adapter.called is False
    assert not (tmp_path / "blocked").exists()


def test_dry_run_preserves_every_audit_stage_and_reaches_renderer_seam(
    tmp_path: Path,
) -> None:
    output = tmp_path / "run"
    report = run_blind_evaluation(
        BlindSourcePacket.from_dict(synthetic_source_packet()),
        DryRunProposalAdapter(synthetic_proposals()),
        output_dir=output,
    )
    assert report["passed_source_count"] == 2
    assert report["live_model_or_external_calls"] == 0
    sequence = output / "sources/01-neutral-sequence"
    required = {
        "source.json",
        "provider-request-metadata.json",
        "extraction-proposal.json",
        "rejected-assertions.json",
        "grounding-resolution.json",
        "admitted-knowledge-model.json",
        "detected-structures.json",
        "representation-decisions.json",
        "renderer-bindings.json",
        "learner-review-artifact.json",
        "run-history.json",
    }
    assert required <= {path.name for path in sequence.iterdir()}
    decisions = _json(sequence / "representation-decisions.json")["decisions"]
    assert "PROCESS_SEQUENCE" in {
        item["selected_representation_strategy"] for item in decisions
    }
    assert any(item["representation_plan"] is not None for item in decisions)
    assert _json(sequence / "renderer-bindings.json")["protected_surface_contract"] == (
        "SPEC038_REPRESENTATION_PLAN"
    )


def test_semantically_thin_dry_run_fails_closed_to_prose(tmp_path: Path) -> None:
    output = tmp_path / "run"
    run_blind_evaluation(
        BlindSourcePacket.from_dict(synthetic_source_packet()),
        DryRunProposalAdapter(synthetic_proposals()),
        output_dir=output,
    )
    thin = _json(
        output / "sources/02-neutral-thin/representation-decisions.json"
    )["decisions"]
    assert [item["selected_representation_strategy"] for item in thin] == [
        "CONCISE_PROSE"
    ]
    assert thin[0]["fallback_reason"] == (
        "NO_DETECTED_TRUSTED_STRUCTURE_CONTAINS_FOCUS"
    )


def test_invalid_semantic_proposal_preserves_failure_and_does_not_retry(
    tmp_path: Path,
) -> None:
    raw = synthetic_source_packet()
    raw["sources"] = [raw["sources"][1]]
    source_hash = raw["sources"][0]["source_sha256"]
    proposal = synthetic_proposals()[source_hash]
    proposal["relationships"] = [
        {
            "id": "unsupported-edge",
            "source_entity_id": "reference-marker",
            "relationship_type": "CAUSES",
            "target_entity_id": "missing-target",
            "statement": "Unsupported edge.",
            "evidence": [],
            "confidence": 0.5,
            "origin": "INFERRED",
        }
    ]
    output = tmp_path / "failed"
    report = run_blind_evaluation(
        BlindSourcePacket.from_dict(raw),
        DryRunProposalAdapter({source_hash: proposal}),
        output_dir=output,
    )
    case = output / "sources/01-neutral-thin"
    assert report["failed_closed_source_count"] == 1
    assert _json(case / "failure.json")["status"] == "FAILED_CLOSED"
    history = _json(case / "run-history.json")
    assert history["adapter_invocation_count"] == 1
    assert history["hidden_retry_count"] == 0
    assert history["history"][-1]["retry_count"] == 0
    assert (case / "extraction-proposal.json").exists()
    assert not (case / "admitted-knowledge-model.json").exists()


def test_harness_records_title_id_domain_filename_and_ordinal_invariance(
    tmp_path: Path,
) -> None:
    output = tmp_path / "harness"
    prepare_blind_evaluation_harness(
        output_dir=output, frozen_commit=FROZEN_COMMIT
    )
    evidence = _json(output / "anti-overfitting-evidence.json")
    assert evidence["status"] == "PASS"
    changed = evidence["metadata_and_ordinal_invariance"]["changed_only"]
    assert changed == [
        "source title",
        "source ID string",
        "source filename/locator",
        "domain display label",
        "source packet ordinal",
    ]
    assert evidence["source_code_guard"]["representation_expectations_read_by_runner"] is False


def test_runner_contains_no_fixture_or_source_strategy_branches() -> None:
    import knowledge_compiler.blind_evaluation as runner

    source = inspect.getsource(runner.run_blind_evaluation).casefold()
    for forbidden in (
        "economics",
        "electromagnetism",
        "software_architecture",
        "market-price",
        "neutral-sequence",
        "neutral-thin",
        "source_id ==",
        "title ==",
        "domain ==",
        "index ==",
    ):
        assert forbidden not in source


def test_harness_regeneration_is_byte_identical(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    prepare_blind_evaluation_harness(
        output_dir=first, frozen_commit=FROZEN_COMMIT
    )
    prepare_blind_evaluation_harness(
        output_dir=second, frozen_commit=FROZEN_COMMIT
    )
    assert _hashes(first) == _hashes(second)


def test_live_execution_plan_is_exact_and_not_authorized() -> None:
    plan = proposed_live_execution_plan(FROZEN_COMMIT)
    assert plan["status"] == "PROPOSED_NOT_AUTHORIZED"
    assert plan["source_count"] == 3
    assert plan["model"] == "gpt-5.6-luna"
    assert plan["calls_per_source"] == 1
    assert plan["maximum_total_calls"] == 3
    assert plan["storage"] == {"store": False}
    assert set(plan["retry_policy"].values()) == {0}
    assert plan["transmission"]["source_text_transmitted"] is True
    assert plan["source_set"] == "UNDISCLOSED_AND_NOT_SELECTED_DURING_SPEC040"


def test_protected_spec038_identity_is_unchanged() -> None:
    directory = ROOT / (
        "examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-20260909"
    )
    assert directory_identity(directory)["aggregate_sha256"] == (
        FROZEN_SPEC038_DIRECTORY_SHA256
    )


def test_browser_finalize_requires_complete_clean_regression(tmp_path: Path) -> None:
    output = tmp_path / "harness"
    prepare_blind_evaluation_harness(
        output_dir=output, frozen_commit=FROZEN_COMMIT
    )
    invalid = _browser_pass()
    invalid["checks"].pop("browser_console_clean")
    with pytest.raises(ValidationError, match="incomplete"):
        finalize_blind_evaluation_harness(
            output,
            invalid,
            deterministic_file_count=1,
            focused_test_result="test",
            protected_regression_result="test",
            full_test_result="test",
        )
    report = finalize_blind_evaluation_harness(
        output,
        _browser_pass(),
        deterministic_file_count=1,
        focused_test_result="test",
        protected_regression_result="test",
        full_test_result="test",
    )
    assert report["browser_gate"] == "PASS"
    assert _json(output / "human-review-template.json")["status"] == (
        "PENDING_OWNER_REVIEW"
    )


def test_cli_prepares_offline_harness(tmp_path: Path, capsys) -> None:
    output = tmp_path / "harness"
    assert main(
        [
            "prepare-blind-evaluation-harness",
            "--output-dir",
            str(output),
            "--frozen-commit",
            FROZEN_COMMIT,
        ]
    ) == 0
    assert "PASS_PENDING_BROWSER" in capsys.readouterr().out
    assert _json(output / "report.json")["live_model_or_external_calls"] == 0


def test_committed_spec040_artifact_is_ready_for_owner_review() -> None:
    output = ROOT / "examples/evaluations" / EVALUATION_NAME
    if not output.exists():
        pytest.skip("generated only after the harness implementation commit is frozen")
    report = _json(output / "report.json")
    gate = _json(output / "machine-gate.json")
    browser = _json(output / "browser-regression.json")
    frozen = _json(output / "frozen-harness.json")
    review = _json(output / "human-review-template.json")
    assert report["status"] == "IMPLEMENTED_AWAITING_OWNER_REVIEW"
    assert report["live_model_or_external_calls"] == 0
    assert report["browser_gate"] == "PASS"
    assert report["deterministic_regeneration"]["result"] == (
        "PASS_BYTE_IDENTICAL"
    )
    assert report["offline_tests"]["result"] == "PASS"
    assert gate["status"] == "PASS"
    assert browser["console"] == {"errors": [], "warnings": [], "result": "PASS"}
    assert frozen["frozen_harness_commit"] == report["frozen_harness_commit"]
    assert review["status"] == "PENDING_OWNER_REVIEW"
    assert review["verdict"] == "PENDING"
    assert review["live_execution_authorized"] is False
