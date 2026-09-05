import hashlib
import json

import pytest

from knowledge_compiler.baseline004 import (
    BASELINE004_EXECUTABLE_HASHES,
    baseline004_directory,
    repository_root,
    verify_baseline004,
)
from knowledge_compiler.models import ValidationError


HISTORICAL_BASELINE_DOCUMENT_HASHES = {
    "BASELINE-001-interface.md": "5c036e4cb85a058bac11a3949a7581907f219ecd36e797ecc74714148768eeeb",
    "BASELINE-002-continuous-navigation-reference.md": "3a975045cf7e9f56cfe574081b25dee079ed85c63ddc6e227800862a7a2b7730",
    "BASELINE-003-hybrid-learning-workspace.md": "ec2603debaf880ecb762cb2836c26998948456406d2f7be1a428c47048db1340",
}


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_baseline004_executable_assets_match_frozen_hashes():
    assert verify_baseline004() == BASELINE004_EXECUTABLE_HASHES


def test_baseline004_is_byte_identical_to_owner_reviewed_spec022_viewer():
    reviewed = (
        repository_root()
        / "examples/evaluations/spec-022-learner-navigation-grammar-20260905"
    )
    frozen = baseline004_directory()
    for name in BASELINE004_EXECUTABLE_HASHES:
        assert (frozen / name).read_bytes() == (reviewed / name).read_bytes()


def test_baseline004_manifest_freezes_exact_executable_set():
    manifest = json.loads(
        (baseline004_directory() / "baseline-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["baseline"] == "BASELINE-004"
    assert manifest["owner_verdict"] == "NAVIGATION_GRAMMAR_BETTER"
    assert manifest["executable_hashes"] == BASELINE004_EXECUTABLE_HASHES
    assert manifest["source_implementation_commit"] == "06064b9"
    for name, expected in manifest["review_evidence_hashes"].items():
        assert _hash(baseline004_directory() / name) == expected


def test_baseline004_preserves_complete_reviewed_spec022_artifact():
    reviewed = (
        repository_root()
        / "examples/evaluations/spec-022-learner-navigation-grammar-20260905"
    )
    frozen = baseline004_directory()
    for source in reviewed.iterdir():
        if source.is_file():
            assert (frozen / source.name).read_bytes() == source.read_bytes()


def test_baseline004_verification_fails_closed_on_approximation(tmp_path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    for name in BASELINE004_EXECUTABLE_HASHES:
        (candidate / name).write_bytes((baseline004_directory() / name).read_bytes())
    with (candidate / "learner-grammar.js").open("a", encoding="utf-8") as stream:
        stream.write("\n")
    with pytest.raises(ValidationError, match="identity mismatch"):
        verify_baseline004(candidate)


def test_historical_baseline_documents_remain_byte_identical():
    baseline_root = repository_root() / "baselines"
    assert {
        name: _hash(baseline_root / name)
        for name in HISTORICAL_BASELINE_DOCUMENT_HASHES
    } == HISTORICAL_BASELINE_DOCUMENT_HASHES


def test_spec022_owner_verdict_and_cross_domain_review_are_preserved():
    review = json.loads(
        (
            repository_root()
            / "examples/evaluations/spec-022-learner-navigation-grammar-20260905"
            / "human-review-template.json"
        ).read_text(encoding="utf-8")
    )
    assert review["verdict"] == "NAVIGATION_GRAMMAR_BETTER"
    assert review["status"] == "COMPLETE"
    assert review["owner_response"]["domains_reviewed"] == [
        "Economics",
        "Electromagnetism",
        "History of Printing",
        "Software Architecture",
    ]
