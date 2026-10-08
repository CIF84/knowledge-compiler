"""Offline evidence packaging, not a compiler pass or architecture audit.

Run from the checkout: .venv/bin/python tools/audit001_prepare.py
No provider imports, retrieval, extraction, candidate generation or PDF rewriting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import io
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = Path("audits/independent-architecture-audit-001")
FREEZE = "9af8366b49ee83bd280d7e06c9e0673fd3164cb1"
ORIGINALS = {
    "audits/electromagnetism.pdf": "33cf1338f57bcd95ac23418be99f5a28c9eea0f560ea7e38fa5d780abbb1b10f",
    "audits/electromagnetism.rtf": "6a75e4f5878773769f370c2ad468422fa6beea015ffc601de02de53ba5d4e2a3",
}
CATEGORIES = {
    "HISTORICAL_EVIDENCE", "CURRENT_IMPLEMENTATION", "HUMAN_LEARNER_EVIDENCE",
    "RESEARCH_TRUST_FINDINGS", "INTERNAL_HYPOTHESIS",
}

# Exact field selections; recommendations/next steps and architecture decision
# menus intentionally withheld. The source report itself remains unchanged.
FIELDS = {
    38: ["machine_gate", "fixed_evaluation_cases", "structural_layout_count"],
    40: ["known_coverage_gaps_preserved", "dry_run_result"],
    42: ["execution", "source_status_counts", "outcomes", "usage_totals", "billing"],
    45: ["execution", "aggregate_replication", "usage_totals", "billing"],
    46: ["reliability_separation", "failure_inventory"],
    48: ["candidate_b_summary", "control_a_summary", "historical_control_caveat"],
    49: ["canonical_contracts", "valid_state_preservation", "post_hoc_restriction_audit"],
    50: ["mixed_cases", "structural_only_control"],
    51: ["claim_preservation", "offline_fixtures", "schema_boundary"],
    52: ["three_arm_summaries", "provider_calls_started", "provider_latency_ms_total",
         "usage_total", "monetary_cost", "semantic_omission_audit", "audit_notes"],
    53: ["claim_path_counts"],
    54: ["outcome_distribution", "strategy_family_distribution"],
    55: ["final_strategy_distribution", "richer_than_prose", "semantic_topology_safety_audit"],
    56: ["selection", "truthfulness_and_provenance_audit"],
    57: ["claim_utility_outcome_distribution", "structural_control_outcome_distribution",
         "spec056_owner_review_audit"],
    58: ["selection", "machine_evidence"],
    59: ["selection", "machine_evidence", "restraint_audit"],
    60: ["compression_metrics", "corpus", "preservation_summary"],
    61: ["compression_metrics", "corpus", "preservation_summary", "block_function_traversal_distribution"],
    62: ["corpus", "preservation_summary", "schema_distribution"],
    63: ["corpus", "preservation", "per_case", "grammar_distribution"],
    64: ["aggregate_measurements", "per_stage_measurements", "preservation", "limitations"],
    65: ["fixture_summary", "capability_gaps", "execution_integrity", "provider_support", "call_budget"],
    66: ["fixture_count", "domains", "label_verdicts", "protocol_metrics", "budget_summary",
         "decomposition_boundary", "judge_calls", "provider_calls"],
    67: ["live_calls", "fixture_transmissions", "J1_metrics", "J2_metrics", "reason",
         "provider_contract", "observed_cost", "observed_latency", "observed_usage"],
    68: ["audited_fixtures", "atomization_distribution", "admissible_atoms", "atom_truth_distribution",
         "mixed_validity_composite_controls", "remaining_categories", "remaining_domains",
         "lost_categories", "representative_future_subset_exists", "why_not_representative",
         "scope_limit", "future_J1_calls", "future_J2_calls", "future_maximum_calls", "live_calls"],
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def stable(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()

def record(root: Path, path: str) -> dict:
    raw = (root / path).read_bytes()
    return {"path": path, "sha256": digest(raw), "bytes": len(raw)}

def report_path(root: Path, number: int) -> Path:
    dirs = sorted((root / "examples/evaluations").glob(f"spec-{number:03}-*"))
    if len(dirs) != 1:
        raise ValueError(f"ambiguous evaluation directory: {number}")
    return dirs[0] / ("final-report.json" if number == 52 else "report.json")

def exact_text(root: Path, path: str, quote: str, identity: str, category: str) -> dict:
    text = (root / path).read_text()
    if text.count(quote) != 1:
        raise ValueError(f"non-unique text evidence {identity}: {path}")
    start = text.index(quote)
    return {"id": identity, "category": category, "source": record(root, path),
            "locator": {"kind": "UTF8_DECODED_CHARACTER_RANGE", "start": start,
                        "end": start + len(quote), "line": text[:start].count("\n") + 1},
            "value": quote, "limit": "Exact project record excerpt; not an independent learner measurement."}

def evidence(root: Path) -> dict:
    rows = []
    for n, fields in FIELDS.items():
        p = report_path(root, n)
        data = json.loads(p.read_text())
        for field in fields:
            if field not in data:
                raise ValueError(f"missing frozen evidence: SPEC-{n:03}/{field}")
            rows.append({"id": f"M{n:03}.{field}", "category": "RESEARCH_TRUST_FINDINGS",
                         "source": record(root, str(p.relative_to(root))),
                         "locator": {"kind": "JSON_POINTER", "pointer": "/" + field},
                         "value": data[field],
                         "limit": "Recorded mechanical result within this experiment's declared audit; not general semantic or learner efficacy proof."})
    quotes = [
        ("debriefs/DEBRIEF-001-text-to-knowledge-model.md", "Because the extractor is deterministic and fixture-backed, we still do not know whether a real LLM can reliably produce useful `KnowledgeModel` instances from previously unseen explanatory text.", "D001", "RESEARCH_TRUST_FINDINGS"),
        ("debriefs/DEBRIEF-002-llm-semantic-extraction.md", "However, the live five-domain evaluation was **MIXED**. Schema validity and source grounding were strong, but relationship precision and vocabulary fit degraded materially in some domains. A valid graph is therefore not equivalent to a semantically correct or pedagogically useful graph.", "D002", "RESEARCH_TRUST_FINDINGS"),
        ("debriefs/DEBRIEF-003-relationship-semantics.md", "However, improved predicate semantics did not eliminate semantic errors. The dominant remaining failures shifted from **wrong relationship type/direction** toward **wrong endpoint selection, lost polarity, duplicate edges, and weak event/state modeling**.", "D003", "RESEARCH_TRUST_FINDINGS"),
        ("debriefs/DEBRIEF-004-structure-detection.md", "The dominant limitations were not detector failures. They were inherited from upstream semantic modeling: missing or substituted endpoints, collapsed states, absent chronology edges, and missing feedback-closing relationships.", "D004", "RESEARCH_TRUST_FINDINGS"),
        ("debriefs/DEBRIEF-005-minimal-representation.md", "The project owner reported:\n\n- an immediate subjective improvement in cognitive orientation;\n- the first-draft UI was already perceived as unusually strong for the maturity of the project;\n- interactivity materially increased engagement;\n- the tool was something they would definitely want available while learning;\n- node and relationship inspection were useful enough that the next requested improvements concerned coherence of interaction and spatial organization rather than questioning the representation concept itself.", "H005", "HUMAN_LEARNER_EVIDENCE"),
        ("specs/AUDIT-001-independent-architecture-audit-preparation.md", "An early electromagnetism prototype reportedly demonstrated strong learner value using a frontier model", "H-original", "HUMAN_LEARNER_EVIDENCE"),
        ("specs/AUDIT-001-independent-architecture-audit-preparation.md", "However, owner review through SPEC-063 found that recent learner-facing outputs remained materially inferior to the original prototype experience.", "H-relative", "HUMAN_LEARNER_EVIDENCE"),
        ("docs/PROJECT-VISION.md", "Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.", "V-objective", "HISTORICAL_EVIDENCE"),
    ]
    rows.extend(exact_text(root, *q) for q in quotes)
    status = (root / "STATUS.md").read_text()
    # Owner observations only. Stop before forward design doctrines/hypotheses.
    sections = {
        38: ("## Accepted learner-facing baseline", "## Extraction state"),
        58: ("SPEC-058 owner verdict:", "SPEC-059 owner verdict:"),
        59: ("SPEC-059 owner verdict:", "## Progressive semantic compression direction"),
        60: ("SPEC-060 owner verdict:", "Canonical refinement:"),
        61: ("## SPEC-061 owner verdict", "## SPEC-062 owner verdict"),
        62: ("## SPEC-062 owner verdict", "Canonical lesson:"),
        63: ("## SPEC-063 owner verdict", "Canonical doctrine:"),
        64: ("## SPEC-064 owner verdict", "Canonical division-of-labor hypothesis:"),
        65: ("## SPEC-065 owner verdict", "Canonical architecture under investigation:"),
        66: ("## SPEC-066 owner verdict", "Canonical trust architecture under test:"),
        67: ("## SPEC-067 owner verdict", "Canonical rule:"),
    }
    for n, (begin, end) in sections.items():
        quote = status[status.index(begin):status.index(end, status.index(begin))].rstrip()
        # Trust/research owner verdicts are not learner efficacy observations.
        category = "HUMAN_LEARNER_EVIDENCE" if n <= 63 else "RESEARCH_TRUST_FINDINGS"
        rows.append(exact_text(root, "STATUS.md", quote, f"H{n:03}", category))
    rows.append(exact_text(root, "STATUS.md",
        "- the safe atomic subset retained all eight domains but only 2/18 semantic categories;\n- no representative semantic-judge experiment can be run from the current safely atomized corpus;",
        "H068", "RESEARCH_TRUST_FINDINGS"))
    # Preserve the verdict without its architecture instruction in initial evidence.
    rows.append(exact_text(root, "STATUS.md",
        "`ATOMIC_TRUST_CONTRACT_VALID_BUT_ARCHITECTURE_AUDIT_REQUIRED_BEFORE_FURTHER_COMPLEXITY`",
        "H068-verdict", "RESEARCH_TRUST_FINDINGS"))
    return {"schema": "audit001.evidence-extracts.v1", "freeze_commit": FREEZE,
            "notice": "These are exact excerpts, not rewritten originals. Source hashes and locators support recovery; complete originals remain frozen in the repository. Initial excerpts omit forward proposals. PENDING in historical machine records is preserved even when a later owner record exists.",
            "records": rows}

def frozen_paths(root: Path) -> list[str]:
    return subprocess.check_output(["git", "ls-tree", "-r", "--name-only", FREEZE],
                                   cwd=root, text=True).splitlines()

def initial_historical_paths(root: Path) -> list[str]:
    paths = []
    for n in (38, 56, 58, 59, 60, 61, 62, 63, 64):
        directory = report_path(root, n).parent
        for p in sorted(directory.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(directory)
            # Exact learner payloads/assets and source/substrate recovery, not
            # reports containing team architectural recommendations.
            include = (p.suffix in {".html", ".css", ".js"}
                       or rel.parts[0] in {"cases", "views", "substrates"}
                       or p.name in {"cases.json", "diagram-cases.json", "workspace-fixture.json",
                                     "representation-plans.json", "projection.json", "diagram-layouts.json",
                                     "revealed-knowledge-fixture.json", "depth-map.json", "owner-review-rubric.json",
                                     "workspace-manifest.json"})
            if include:
                paths.append(str(p.relative_to(root)))
    d = report_path(root, 52).parent
    paths.extend(str(p.relative_to(root)) for p in sorted(d.glob("sources/*/admitted-knowledge-model.json")))
    for n in (42, 45, 48, 52):
        paths.append(str((report_path(root, n).parent / "provider-call-ledger.json").relative_to(root)))
    # Implemented core, not proposed future pipeline prompt scaffolds.
    modules = ["normalize", "pipeline", "extractor", "deduplicate", "models", "relationships",
               "proposition_validation", "openai_extractor", "structure_detection",
               "structures", "representation_builder", "representations", "representation_strategy",
               "semantic_representation_compiler", "resolution_compiler", "resolution_strategies",
               "assertion_aware_representation", "control_plane"]
    for name in modules:
        p = Path(f"src/knowledge_compiler/{name}.py")
        if not (root / p).is_file():
            raise ValueError(f"missing implemented module {p}")
        paths.append(str(p))
    return sorted(set(paths))

def build(root: Path = ROOT) -> dict[str, bytes]:
    for path, sha in ORIGINALS.items():
        if digest((root / path).read_bytes()) != sha:
            raise ValueError(f"owner-recovered artifact changed: {path}")
    historical = frozen_paths(root)
    # Every previously tracked file except the two authorized coordination
    # updates must remain byte-identical, not merely selected baselines.
    protected = []
    archive_bytes = subprocess.check_output(["git", "archive", FREEZE], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as frozen:
        originals = {m.name: frozen.extractfile(m).read() for m in frozen.getmembers() if m.isfile()}
    for path in historical:
        if path in {"STATUS.md", "specs/AUDIT-001-independent-architecture-audit-preparation.md"}:
            continue
        before = originals[path]
        after = (root / path).read_bytes()
        if after != before:
            raise ValueError(f"historical protected file changed: {path}")
        protected.append({"path": path, "sha256": digest(before), "bytes": len(before)})
    generated = {str(DOSSIER / "evidence-extracts.json"): stable(evidence(root)),
                 str(DOSSIER / "protected-state.json"): stable({"freeze_commit": FREEZE, "files": protected})}
    docs = sorted(str(p.relative_to(root)) for p in (root / DOSSIER).glob("0[0-8]-*.md"))
    if len(docs) != 9:
        raise ValueError("expected introduction and eight initial dossier documents")
    members = sorted(set(docs + list(ORIGINALS) + initial_historical_paths(root)
                         + [str(DOSSIER / "evidence-extracts.json"), str(DOSSIER / "original-inspection-record.json")]))
    entries = []
    for p in members:
        data = generated[p] if p in generated else (root / p).read_bytes()
        entries.append({"path": p, "sha256": digest(data), "bytes": len(data)})
    initial_manifest_path = str(DOSSIER / "initial-package-manifest.json")
    initial_manifest = {"schema": "audit001.initial-package.v1", "freeze_commit": FREEZE,
                        "scope": "INITIAL_INDEPENDENT_AUDIT_ONLY", "files": entries,
                        "original_artifacts": [{**record(root, p), "provenance": "OWNER_RECOVERED_HISTORICAL_ARTIFACT",
                                                "role": "CANONICAL_VISUAL_EVIDENCE" if p.endswith(".pdf") else "MACHINE_READABLE_COMPANION"} for p in ORIGINALS],
                        "exclusions": "Current-team future architecture hypotheses, raw coordination/contract documents, and preselected benchmark arms are withheld until the auditor freezes its independent diagnosis and recommendation."}
    generated[initial_manifest_path] = stable(initial_manifest)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as z:
        for p in sorted(members + [initial_manifest_path]):
            info = zipfile.ZipInfo(p, date_time=(2026, 10, 8, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            z.writestr(info, generated[p] if p in generated else (root / p).read_bytes())
    archive_path = str(DOSSIER / "initial-auditor-package.zip")
    generated[archive_path] = archive.getvalue()
    # Full custodian manifest, NEVER part of the initial auditor package.
    context = [p for p in historical if p.startswith(("specs/", "debriefs/", "reviews/", "baselines/"))
               or p in {"STATUS.md", "AGENTS.md", "ARCHITECTURE.md", "PROJECT_MEMORY.md", "docs/PROJECT-VISION.md"}
               or (p.startswith("examples/evaluations/") and
                   (Path(p).name in {"report.json", "final-report.json", "provider-call-ledger.json", "review.json"}))]
    audit_files = [str(p.relative_to(root)) for p in sorted((root / DOSSIER).glob("*"))
                  if p.is_file() and p.name not in {"audit-manifest.json"} and p.suffix in {".md", ".json"}]
    context += audit_files + ["tools/audit001_prepare.py", "tests/test_audit001_dossier.py"]
    full = []
    for p in sorted(set(context + list(ORIGINALS) + list(generated))):
        data = generated[p] if p in generated else (root / p).read_bytes()
        visibility = "INITIAL_PACKAGE" if p in members + [initial_manifest_path, archive_path] else "CUSTODIAN_ONLY_NOT_FOR_INITIAL_AUDITOR"
        full.append({"path": p, "sha256": digest(data), "bytes": len(data), "visibility": visibility})
    generated[str(DOSSIER / "audit-manifest.json")] = stable({
        "schema": "audit001.custodian-manifest.v1", "freeze_commit": FREEZE,
        "purpose": "Evidence preparation only; independent audit not performed.",
        "authority": "OFFLINE_ONLY", "human_gate": "OWNER_REVIEW", "promotion": "NOT_AUTHORIZED",
        "owner_amendment": "Recovered originals primary; no predefined architecture or benchmark-arm menu in initial dossier.",
        "initial_archive": {"path": archive_path, "sha256": digest(generated[archive_path])},
        "files": full, "protected_file_count": len(protected),
        "protected_state_sha256": digest(generated[str(DOSSIER / "protected-state.json")]),
        "self_hash_policy": "This manifest is excluded from its own file list; compute SHA256 externally. No recursive commit identity or archive hash cycle.",
    })
    return generated

def validate(root: Path = ROOT) -> dict:
    expected = build(root)
    for p, raw in expected.items():
        if (root / p).read_bytes() != raw:
            raise ValueError(f"non-reproducible audit output: {p}")
    ids = {r["id"] for r in json.loads(expected[str(DOSSIER / "evidence-extracts.json")])["records"]}
    for p in sorted((root / DOSSIER).glob("0[0-8]-*.md")):
        text = p.read_text()
        for ref in re.findall(r"\[evidence:([^\]]+)\]", text):
            if ref not in ids:
                raise ValueError(f"unresolved evidence reference: {p}:{ref}")
        # All local Markdown links must be real and inside the initial archive.
        members = {r["path"] for r in json.loads(expected[str(DOSSIER / "initial-package-manifest.json")])["files"]}
        members.add(str(DOSSIER / "initial-package-manifest.json"))
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("http:", "https:")):
                raise ValueError("initial documents must not require network retrieval")
            resolved = (p.parent / target.split("#")[0]).resolve()
            if not resolved.is_file() or str(resolved.relative_to(root.resolve())) not in members:
                raise ValueError(f"initial link escapes package or is missing: {p}:{target}")
    return {"result": "PASS", "freeze_commit": FREEZE, "originals_unchanged": True,
            "deterministic_regeneration": True, "historical_files_unchanged": True,
            "model_provider_retrieval_calls": 0, "independent_audit_performed": False,
            "benchmark_executed": False, "human_verdict": "PENDING", "promotion": "NOT_AUTHORIZED"}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        for p, raw in build().items():
            (ROOT / p).write_bytes(raw)
    print(json.dumps(validate(), indent=2))

if __name__ == "__main__":
    main()
