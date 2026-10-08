"""Dossier mechanical gates; not an architecture or learner-effectiveness test."""
import hashlib
import importlib.util
import io
import json
import re
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit001_prepare", ROOT / "tools/audit001_prepare.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

@pytest.fixture(scope="module")
def generated():
    return audit.build(ROOT)

def test_deterministic_reproduction_and_all_historical_bytes(generated):
    assert generated == audit.build(ROOT)
    for name, data in generated.items():
        assert (ROOT / name).read_bytes() == data
    assert audit.validate(ROOT)["independent_audit_performed"] is False

def test_recovered_original_identities_and_direct_access(generated):
    archive = zipfile.ZipFile(io.BytesIO(generated[str(audit.DOSSIER / "initial-auditor-package.zip")]))
    for name, sha in audit.ORIGINALS.items():
        assert hashlib.sha256(archive.read(name)).hexdigest() == sha
        assert archive.read(name) == (ROOT / name).read_bytes()
    manifest = json.loads(generated[str(audit.DOSSIER / "initial-package-manifest.json")])
    assert {r["provenance"] for r in manifest["original_artifacts"]} == {"OWNER_RECOVERED_HISTORICAL_ARTIFACT"}
    assert {r["role"] for r in manifest["original_artifacts"]} == {"CANONICAL_VISUAL_EVIDENCE", "MACHINE_READABLE_COMPANION"}

def test_initial_package_is_hermetic_and_excludes_current_team_hypotheses(generated):
    archive = zipfile.ZipFile(io.BytesIO(generated[str(audit.DOSSIER / "initial-auditor-package.zip")]))
    names = archive.namelist()
    assert len(names) == len(set(names))
    assert names == sorted(names)
    assert not any(n.startswith(("specs/", "debriefs/", "reviews/")) for n in names)
    assert "STATUS.md" not in names
    assert "docs/PROJECT-VISION.md" not in names
    assert not any("internal-hypotheses" in n or "custodian" in n or "audit-manifest.json" == Path(n).name for n in names)
    for name in names:
        assert not name.startswith("/") and ".." not in Path(name).parts
        if name.endswith((".md", ".json", ".html", ".js", ".css")):
            raw = archive.read(name).decode()
            for forbidden in ("A — Current research-grade architecture", "B — Radical simplification",
                              "C — Hybrid audit architecture", "D — Prototype reset", "E — Stop/pivot",
                              "CONTINUE / SIMPLIFY / RESET / PIVOT / STOP", "Arm F —", "Arm K —", "Arm M —"):
                assert forbidden not in raw, (name, forbidden)
    excluded = ROOT / audit.DOSSIER / "internal-hypotheses-not-for-initial-auditor.md"
    assert "EXCLUDED_FROM_INITIAL_INDEPENDENT_AUDIT" in excluded.read_text()

def test_every_manifest_member_matches_archive_bytes(generated):
    manifest = json.loads(generated[str(audit.DOSSIER / "initial-package-manifest.json")])
    archive = zipfile.ZipFile(io.BytesIO(generated[str(audit.DOSSIER / "initial-auditor-package.zip")]))
    assert set(archive.namelist()) == {r["path"] for r in manifest["files"]} | {str(audit.DOSSIER / "initial-package-manifest.json")}
    for row in manifest["files"]:
        data = archive.read(row["path"])
        assert audit.digest(data) == row["sha256"]
        assert len(data) == row["bytes"]
    custodian = json.loads(generated[str(audit.DOSSIER / "audit-manifest.json")])
    for row in custodian["files"]:
        data = generated.get(row["path"], (ROOT / row["path"]).read_bytes())
        assert audit.digest(data) == row["sha256"]
    assert custodian["initial_archive"]["sha256"] == audit.digest(generated[custodian["initial_archive"]["path"]])

def test_exact_excerpts_do_not_rewrite_or_merge_epistemic_categories(generated):
    extracts = json.loads(generated[str(audit.DOSSIER / "evidence-extracts.json")])
    ids = [r["id"] for r in extracts["records"]]
    assert len(ids) == len(set(ids))
    for row in extracts["records"]:
        assert row["category"] in audit.CATEGORIES
        source = ROOT / row["source"]["path"]
        assert audit.digest(source.read_bytes()) == row["source"]["sha256"]
        locator = row["locator"]
        if locator["kind"] == "JSON_POINTER":
            expected = json.loads(source.read_text())[locator["pointer"][1:]]
        else:
            expected = source.read_text()[locator["start"]:locator["end"]]
        assert row["value"] == expected
    assert all(r["category"] == "HUMAN_LEARNER_EVIDENCE" for r in extracts["records"] if r["id"] in {"H005", "H038", "H-original", "H-relative"})
    assert all(r["category"] == "RESEARCH_TRUST_FINDINGS" for r in extracts["records"] if r["id"] in {"H064", "H065", "H066", "H067", "H068"})

def test_fail_closed_on_changed_recovered_file(tmp_path):
    original = tmp_path / "audits"
    original.mkdir()
    (original / "electromagnetism.pdf").write_bytes(b"substituted original")
    with pytest.raises(ValueError, match="owner-recovered artifact changed"):
        audit.build(tmp_path)

def test_missing_nonunique_or_changed_evidence_does_not_silently_pass(tmp_path):
    p = tmp_path / "source.md"
    p.write_text("claim claim")
    with pytest.raises(ValueError, match="non-unique text evidence"):
        audit.exact_text(tmp_path, "source.md", "claim", "test", "HISTORICAL_EVIDENCE")
    with pytest.raises(ValueError, match="ambiguous evaluation directory"):
        audit.report_path(tmp_path, 52)

def test_no_live_transport_dependency_or_hidden_experiment_execution():
    text = (ROOT / "tools/audit001_prepare.py").read_text()
    assert not any(token in text for token in ("import openai", "import requests", "urlopen(", "responses.create(", "chat.completions"))
    assert "git\", \"archive" in text
    assert "git\", \"show" not in text

def test_packaged_review_surfaces_have_all_literal_local_assets(generated):
    archive = zipfile.ZipFile(io.BytesIO(generated[str(audit.DOSSIER / "initial-auditor-package.zip")]))
    names = set(archive.namelist())
    for name in names:
        if Path(name).suffix not in {".html", ".js", ".css"}:
            continue
        text = archive.read(name).decode()
        references = re.findall(r'''(?:src|href)=["']([^"']+)["']|fetch\(["']([^"']+)["']\)''', text)
        for group in references:
            target = next(x for x in group if x)
            if target.startswith(("http", "data", "#")):
                continue
            assert str(Path(name).parent / target) in names, (name, target)

def test_historical_call_economics_are_receipt_backed_not_projection(generated):
    archive = zipfile.ZipFile(io.BytesIO(generated[str(audit.DOSSIER / "initial-auditor-package.zip")]))
    totals = []
    for n, expected in [(42, 3), (45, 6), (48, 19), (52, 26)]:
        path = str((audit.report_path(ROOT, n).parent / "provider-call-ledger.json").relative_to(ROOT))
        ledger = json.loads(archive.read(path))
        assert ledger["calls_started"] == expected
        assert len(ledger["entries"]) == expected
        totals.append(expected)
    assert sum(totals) == 54
    brief = archive.read(str(audit.DOSSIER / "08-independent-auditor-brief.md")).decode()
    workspace = archive.read(str(audit.DOSSIER / "06-candidate-architecture-space.md")).decode()
    assert "independently" in brief and "independently" in workspace
    assert "No architectural outcome is assigned here" in workspace
