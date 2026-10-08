"""Source-only custody contracts; synthetic negatives, no selector candidates."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import custody002_prepare as c


@pytest.fixture(scope="module")
def built():
    return c.build(ROOT)


def public(built):
    return {name.removeprefix(str(c.OUT) + "/"): raw for name, raw in built.items()
            if name.startswith(str(c.OUT) + "/")}


def manifest(built):
    return json.loads(public(built)["contamination-reference-manifest.json"])


def test_all_five_independent_completeness_boundaries(built):
    report = json.loads(built[str(c.BASE / "custody-002-report.json")])
    rows = report["families"]
    assert [r["family"] for r in rows] == c.FAMILIES
    assert [r["status"] for r in rows] == ["COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION"] * 3 + ["COMPLETE_EXACT"] * 2
    assert all(r["enumeration_rationale"] and r["known_gaps"] for r in rows)
    assert all(report["family_enumeration"][f] for f in c.FAMILIES)
    assert report["historical_fixture_paths"] == sorted(str(p.relative_to(ROOT)) for p in (ROOT / "tests/fixtures").rglob("*.txt"))
    assert {int(Path(p).parts[2].split("-")[1]) for p in report["late_family_census_paths"]} == set(range(60, 69))
    assert report["derivative_evidence_range_checks"] == 587
    assert len(report["nine_source_identities"]) == 9


@pytest.mark.parametrize("status", ["PARTIAL", "UNRESOLVED", "NOT_EVALUATED", "COMPLETE"])
def test_any_unsafe_family_withholds_authority(status):
    rows = [{"family": f, "status": "COMPLETE_EXACT"} for f in c.FAMILIES]
    for i in range(5):
        bad = copy.deepcopy(rows)
        bad[i]["status"] = status
        with pytest.raises(ValueError, match="no continuation authority or ZIP"):
            c.require_safe(bad)


def test_missing_duplicate_or_extra_family_fails_closed():
    rows = [{"family": f, "status": "COMPLETE_EXACT"} for f in c.FAMILIES]
    for bad in [rows[:-1], rows + rows[:1], rows[:-1] + rows[:1]]:
        with pytest.raises(ValueError):
            c.require_safe(bad)


def test_em_unknown_input_not_response_equivalence(built):
    entries = public(built)
    item = json.loads(entries["recovered-electromagnetism-fingerprint.json"])
    assert all(item[k] == "UNKNOWN" for k in ["original_input_source_identity", "original_input_passage", "original_input_lineage"])
    assert item["recovered_artifact_hashes"] == c.ORIGINALS
    assert "regardless" in item["blacklist"]
    hashes = item["fingerprint"]["shingle_hashes"]
    assert hashes == sorted(set(hashes)) and len(hashes) > 100
    assert all(len(s) == 64 and set(s) <= set("0123456789abcdef") for s in hashes)
    assert not item["fingerprint"]["ordered_text_exported"]
    assert all(not name.endswith((".pdf", ".rtf")) for name in entries)
    # Factual local electromagnetism input is separate and has no claimed link.
    assert any("golden fixtures" in r["families"] and b"electromagnet" in entries[r["passage_file"]].lower()
               for r in manifest(built)["sources"])


def test_normalization_exact_hashes_and_equivalence_are_not_conflated(built):
    entries = public(built)
    rows = manifest(built)["sources"]
    assert len({r["passage_sha256"] for r in rows}) == len(rows)
    assert len({r["normalized_passage_sha256"] for r in rows}) < len(rows)
    for r in rows:
        data = entries[r["passage_file"]]
        assert c.digest(data) == r["passage_sha256"]
        assert len(data) == r["utf8_bytes"]
        assert c.digest(c.normalize(data.decode()).encode()) == r["normalized_passage_sha256"]
    assert c.normalize(" \r\nHello\rworld\r\n ") == "Hello\nworld"
    assert c.normalize("Hello  world") == "Hello  world"
    assert c.shingles("One two three four five SIX") == c.shingles("one two three four five six")
    attributes = (ROOT / c.BASE / ".gitattributes").read_text()
    assert "benchmark-readiness-v1/contamination-reference-export-v2/passages/*.txt -text -diff" in attributes


def test_every_source_excerpt_has_exact_parent_trace(built):
    entries = public(built)
    rows = manifest(built)["sources"]
    by_sha = {r["passage_sha256"]: entries[r["passage_file"]].decode() for r in rows}
    ranges_checked = 0
    for r in rows:
        for identity in r["identities"]:
            for parent in identity.get("exact_parent_ranges", []):
                text = by_sha[parent["parent_passage_sha256"]]
                assert text[parent["start_char"]:parent["end_char"]] == by_sha[r["passage_sha256"]]
                ranges_checked += 1
            if "parent_passage_sha256" in identity:
                bounds = identity["passage_range"]
                assert by_sha[identity["parent_passage_sha256"]][bounds["start_char"]:bounds["end_char"]] == by_sha[r["passage_sha256"]]
    assert ranges_checked == 46


def test_quantum_exact_revision_and_attribution_and_synthetic_input(built):
    entries = public(built)
    quantum = next(r for r in manifest(built)["sources"] if r["passage_sha256"] == "9e978db999ee67134d347f91fe9f32934c982f4de9b496e4bf664cb00cce23ea")
    metadata = next(i for i in quantum["identities"] if i["source_id"] == "wikipedia-introduction-to-quantum-mechanics")
    assert metadata["revision_id"] == 1359567407
    assert "oldid=1359567407" in metadata["permanent_url"]
    assert "Creative Commons" in metadata["license"] and metadata["authors"]
    assert len(entries[quantum["passage_file"]].decode()) == 39735
    assert b"the double-slit experiment. \n" in entries[quantum["passage_file"]]
    assert any(r["passage_sha256"] == "959235415a4bafb481456910835346af2d6b9ff8ef4fb21fbd268161878641a6" for r in manifest(built)["sources"])


def test_allowlisted_provenance_drops_context_not_source_identity():
    value = {"canonical_url": "https://example.invalid/source", "source_scope": "opening paragraphs",
             "authority_priority_rank": 1, "model_performance": "SECRET_CONTEXT",
             "selection_rule_evidence": {"semantic_answer_supplied": False},
             "retrieval": {"document_sha256": "f" * 64, "http_status": 200}}
    safe = c.safe_provenance(value)
    assert safe == {"canonical_url": value["canonical_url"], "source_scope": "opening paragraphs",
                    "original_document": {"document_sha256": "f" * 64}}


@pytest.mark.parametrize("member,data", [
    ("STATUS.md", b"anything"), ("prompts/A.txt", b"anything"),
    ("README.md", b"KnowledgeModel"), ("README.md", b"provider_request_id"),
    ("recovered.pdf", b"original"), ("README.md", b"candidate-b-v2"),
])
def test_sanitization_rejects_context_injection(member, data):
    with pytest.raises(ValueError):
        c.leakage_check({member: data})


def test_public_package_has_no_context_bearing_repository_paths(built):
    entries = public(built)
    c.leakage_check(entries)
    report = json.loads(built[str(c.BASE / "custody-002-report.json")])
    assert report["source_path_index"]
    for row in manifest(built)["sources"]:
        for locator in row["repository_evidence_paths"]:
            assert set(locator) == {"repository_blob_sha256", "source_field_locator", "repository_commit", "evidence_locator"}
            assert len(locator["source_field_locator"]) == 64
    all_bytes = b"\n".join(entries.values())
    for p in ["/block-manifest.json", "/admitted-knowledge-model.json", "/fixture-corpus.json", "/parent.knowledge.json"]:
        assert p.encode() not in all_bytes
    # Domain-source prose may mention architecture; it is not project context.
    c.leakage_check({"README.md": b"Software architecture is a historical source subject."})


def test_authority_narrow_bounds_and_no_adjudication(built):
    text = public(built)["selector-v1.1-authority.txt"].decode()
    for required in ["same independent selector context", "THREE", "ONLY neuroscience / mechanism and hydrology / process",
                     "BOTH ordered D3–D6", "FOUR additional documents per", "never reorder", "first eligible",
                     "ALL FIVE", "missingness", "No further automatic extension", "stop rather than invent"]:
        assert required in text
    report = json.loads(built[str(c.BASE / "custody-002-report.json")])
    assert report["owner_verdict"] == "PENDING"
    assert all(v == 0 for k, v in report["zero_activity"].items() if k != "git_coordination_only")
    assert report["result"] == "SANITIZED_CONTAMINATION_EXPORT_READY"
    assert report["recommended_next_step"] == "RETURN_V1_1_PACKAGE_TO_SAME_SELECTOR"


def test_deterministic_package_and_complete_regeneration(built):
    entries = public(built)
    assert c.zip_bytes(entries) == built[str(c.ZIP)]
    assert c.zip_bytes(dict(reversed(list(entries.items())))) == built[str(c.ZIP)]
    assert c.build(ROOT) == built
    for name, data in built.items():
        assert (ROOT / name).read_bytes() == data
    with zipfile.ZipFile(io.BytesIO(built[str(c.ZIP)])) as archive:
        assert archive.namelist() == sorted(entries)
        for name in archive.namelist():
            assert archive.read(name) == entries[name]


def test_standalone_verifier_and_corruption_fails_closed(built, tmp_path):
    for name, raw in public(built).items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    result = subprocess.run([sys.executable, str(tmp_path / "verify.py")], capture_output=True)
    assert result.returncode == 0 and b"not contamination clearance" in result.stdout
    passage = next((tmp_path / "passages").iterdir())
    passage.write_bytes(b"tampered synthetic text")
    result = subprocess.run([sys.executable, str(tmp_path / "verify.py")], capture_output=True)
    assert result.returncode != 0 and b"identity mismatch" in result.stderr


def test_historical_bytes_bench_freeze_and_all_user_work_untouched(built):
    protected = json.loads(built[str(c.BASE / "custody-002-protected-state.json")])
    assert len(protected["files"]) > 1000
    for r in protected["files"]:
        raw = (ROOT / r["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == r["sha256"]
        assert len(raw) == r["bytes"]
    assert c.digest((ROOT / c.OUT.parent / "lock.json").read_bytes()) == "c954e9fe9e3f707989913b994c97933726f82d254b3663eeebbba62a076b41c4"
