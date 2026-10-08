"""Frozen-repository, offline source-only custody export; never a source selector.

Only enumerated canonical evidence is read. No selector inputs, network libraries,
production compiler imports, semantic outputs, or inferred historical identities.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REF = "65c31162c4a11ff67f88309a46981fb1eecb12f5"
CONTRACT = "specs/CUSTODY-002-evidence-bounded-contamination-export.md"
BASE = Path("audits/independent-architecture-audit-001")
OUT = BASE / "benchmark-readiness-v1/contamination-reference-export-v2"
ZIP = OUT.parent / "source-selector-continuation-v1.1.zip"
FAMILIES = ["recovered electromagnetism", "golden fixtures",
            "quantum/economics/software controls", "SPEC-042/045 nine-source corpus",
            "SPEC-060–068 sources/derivatives"]
SAFE = {"COMPLETE_EXACT", "COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION"}
ORIGINALS = {
    "audits/electromagnetism.pdf": "33cf1338f57bcd95ac23418be99f5a28c9eea0f560ea7e38fa5d780abbb1b10f",
    "audits/electromagnetism.rtf": "6a75e4f5878773769f370c2ad468422fa6beea015ffc601de02de53ba5d4e2a3",
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def stable(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def canonical(value):
    # Historical SPEC-066 uses compact canonical JSON, including JSON strings.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def normalize(text):
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def shingles(text):
    words = re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold())
    return sorted({digest(" ".join(words[i:i + 5]).encode()) for i in range(len(words) - 4)})


def snapshot(root):
    raw = subprocess.check_output(["git", "archive", REF], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {m.name: archive.extractfile(m).read() for m in archive.getmembers() if m.isfile()}


def require_safe(rows):
    if (len(rows) != 5 or {r["family"] for r in rows} != set(FAMILIES)
            or any(r["status"] not in SAFE for r in rows)):
        raise ValueError("unsafe family coverage: no continuation authority or ZIP")


def safe_provenance(provenance):
    result = {k: provenance[k] for k in ["canonical_url", "institutional_publisher",
              "source_document_identity", "source_document_date", "revision_or_date", "source_scope"]
              if k in provenance}
    retrieval = provenance.get("retrieval", {})
    result["original_document"] = {k: retrieval[k] for k in
        ["document_sha256", "document_byte_count", "format", "timestamp_utc"] if k in retrieval}
    return result


def zip_bytes(entries):
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, raw in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw)
    return result.getvalue()


README = """# Historical source contamination reference

This package is only for the same independent selector's overlap/lineage screening.
It does not supply new candidate documents, candidate rankings, or eligibility verdicts.

Read contamination-reference-manifest.json, family-completeness.json,
normalization.json and recovered-electromagnetism-fingerprint.json first. Passage
files are exact historical UTF-8 input text, not summaries or generated answers.
Source metadata is allowlisted; UNKNOWN means unknown, not inferred.

Exclude the same historical document (including other revisions/excerpts), its
derivatives/paraphrases and materially overlapping content. Missing original
publication bytes are not a license to reuse another passage from that document.
For local inputs of unknown external origin, use the exact text and conservative
content overlap; do not infer a publisher. Ambiguous overlap is quarantined, not
cleared. A nonmatching hash or n-gram set does NOT certify noncontamination.

The recovered response itself is not included. Its original input source,
passage and lineage are UNKNOWN. Its unordered hashed five-word shingles are
an auxiliary fingerprint only; the introductory-electromagnetism/substantive
content blacklist is mandatory even if no shingles match. No phrase ordering,
headings, diagrams or explanatory organization is supplied.

Repository evidence locators are content-addressed blob identities plus source
field pointers. The exact repository-path index is held separately by custody,
not supplied here: it contains context the selector must not receive. No repo
access is required. These locators identify source extraction, not external
publication bytes. Public metadata separately identifies publication hashes.

verify.py verifies package bytes and passage normalization locally, without
network access. It does not adjudicate contamination or establish eligibility.
Use selector-v1.1-authority.txt for the only permitted continuation. If a rule
or source identity is uncertain, preserve uncertainty and stop/quarantine.
"""

AUTHORITY = """SOURCE SELECTOR v1.1 — NARROW CONTINUATION AUTHORITY

Recipient: ONLY the same independent selector context that froze source-selection-v1.
Preserve that entire v1 package byte-identically. Do not replace, repair, revisit
or reorder its records. No repository access or additional project context is
authorized. This package contains historical source exclusions, not benchmark
outputs or guidance about which candidate should succeed.

Use the reference solely for overlap/lineage checks. Adjudicate the THREE
already-quarantined v1 provisional passages, preserving their prior evidence and
recording the exact contamination evidence and uncertainty for each disposition.
Do not treat a missing hash match as clearance. Ambiguous substantive overlap
fails closed. Introductory electromagnetism and substantive overlap with the
listed electromagnetism content are blacklisted regardless of fingerprint match.

Extend ONLY neuroscience / mechanism and hydrology / process. Before ANY new
retrieval, freeze BOTH ordered D3–D6 document lists, with document identities,
ordering rationale and a timestamp/hash commitment. Append after exhausted v1
D1/D2; never reorder or revisit D1/D2. At most FOUR additional documents per
slot. Retrieve only after both lists are frozen. Preserve all v1 domain, shape,
length, authority, whole-unit, figure-dependence, logging and first-eligible
rules unchanged. This authority does not supply or relax those rules: if the
frozen v1 contract is unavailable or contradictory, stop rather than invent it.

Take the first eligible passage under the frozen order, not the most attractive
later candidate. Preserve every retrieval failure, rejection, contamination
finding and missing slot. Freeze ALL FIVE sources together only after every
eligibility and contamination gate passes. If D3–D6 exhaust, preserve missingness
and STOP. No further automatic extension or new domain/slot is authorized.

Return the continuation log, both pre-retrieval list freezes, contamination
dispositions, all failures/rejections and the joint source freeze or explicit
missingness. Do not execute any benchmark or receive architecture, performance,
learner-review or current-team hypothesis material. No project verdict is assigned.
"""

VERIFIER = '''"""Source-reference integrity only; no network and no contamination clearance."""
import hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parent
manifest = json.loads((root / "package-integrity.json").read_text())
for name, expected in manifest["files"].items():
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe path")
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected["sha256"] or len(raw) != expected["bytes"]:
        raise ValueError("identity mismatch: " + name)
sources = json.loads((root / "contamination-reference-manifest.json").read_text())["sources"]
for item in sources:
    text = (root / item["passage_file"]).read_bytes().decode("utf-8")
    normalized = text.replace("\\r\\n", "\\n").replace("\\r", "\\n").strip()
    if hashlib.sha256(normalized.encode()).hexdigest() != item["normalized_passage_sha256"]:
        raise ValueError("normalization mismatch")
print("PASS: integrity/normalization only; not contamination clearance")
'''


def leakage_check(entries):
    allowed = {"README.md", "normalization.json", "family-completeness.json",
               "contamination-reference-manifest.json", "recovered-electromagnetism-fingerprint.json",
               "selector-v1.1-authority.txt", "verify.py", "package-integrity.json"}
    forbidden = [b"Knowledge Compiler", b"KnowledgeModel", b"candidate-b-v2", b"provider_request_id",
                 b"SEMANTIC_JUDGMENT_REQUIRED", b"NEW_VISUAL_BASELINE", b"IA-001-BENCH",
                 b"current-team candidate", b"arm_label", b"C+-inventory", b"STATUS.md",
                 b"representation_strategy", b"admitted-knowledge-model", b"candidate_text"]
    for name, raw in entries.items():
        if name not in allowed and not re.fullmatch(r"passages/[0-9a-f]{64}\.txt", name):
            raise ValueError("unallowlisted export member: " + name)
        if any(marker in raw for marker in forbidden):
            raise ValueError("context leakage: " + name)
    # A full recovered artifact, decoded response, or repository tree is never copied.
    if any(name.endswith((".pdf", ".rtf")) for name in entries):
        raise ValueError("historical response leakage")


def build(root=ROOT):
    files = snapshot(root)
    if ((root / CONTRACT).read_bytes().replace(b"Status: `IMPLEMENTED_AWAITING_REVIEW`",
            b"Status: `APPROVED_FOR_IMPLEMENTATION`", 1) != files[CONTRACT]):
        raise ValueError("active contract drift")
    protected = []
    for path, raw in sorted(files.items()):
        if path in {"STATUS.md", CONTRACT}:
            continue
        if (root / path).read_bytes() != raw:
            raise ValueError("historical evidence drift: " + path)
        protected.append({"path": path, "sha256": digest(raw), "bytes": len(raw)})
    for path, sha in ORIGINALS.items():
        if digest(files[path]) != sha:
            raise ValueError("recovered artifact mismatch")
    decoded = subprocess.check_output(["/usr/bin/textutil", "-convert", "txt", "-stdout",
                                      str(root / "audits/electromagnetism.rtf")]).decode()
    fingerprint = {
        "family": FAMILIES[0], "status": "COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION",
        "original_input_source_identity": "UNKNOWN", "original_input_passage": "UNKNOWN",
        "original_input_lineage": "UNKNOWN", "recovered_artifact_hashes": ORIGINALS,
        "subject_labels": ["introductory electromagnetism", "charge", "electric fields",
                           "current", "magnetic fields", "induction", "electromagnetic waves"],
        "decoded_response_normalized_sha256": digest(normalize(decoded).encode()),
        "fingerprint": {"algorithm": "NFKC-casefold-Unicode-alphanumeric-5-word-SHA256-sorted-set-v1",
                        "ordered_text_exported": False, "shingle_hashes": shingles(decoded)},
        "blacklist": "Exclude introductory electromagnetism and substantive coverage of charge, electric fields, current, magnetic fields, induction or electromagnetic waves; quarantine ambiguous overlap. Apply regardless of n-gram matches.",
        "limitation": "Recovered historical response, NOT the missing original input. Its input identity/passage/lineage remain UNKNOWN. This blacklist deliberately over-excludes introductory electromagnetism; fingerprint absence cannot clear content. No later fixture is asserted equivalent to the original input.",
    }
    for label in ["charge", "current", "induction"]:
        if label not in decoded.casefold():
            raise ValueError("unevidenced subject label")

    records, private, enumerations = {}, [], {f: [] for f in FAMILIES}
    enumerations[FAMILIES[0]] = [{"path": path, "file_sha256": sha,
        "fields": ["immutable artifact byte identity", "RTF decoded text to unordered hashed shingles only"],
        "boundary": "Owner-recovered response evidence; missing original input is not reconstructed"}
        for path, sha in sorted(ORIGINALS.items())]
    json_cache = {}

    def load(path):
        if path not in json_cache:
            json_cache[path] = json.loads(files[path])
        return json_cache[path]

    def enumerate_path(family, path, fields, boundary):
        enumerations[family].append({"path": path, "fields": fields,
                                    "boundary": boundary, "file_sha256": digest(files[path])})

    def add(text, family, path, pointer, source_id=None, metadata=None, raw=None, commit=REF):
        data = text.encode() if raw is None else raw
        if data.decode() != text or not normalize(text):
            raise ValueError("invalid source bytes")
        sha = digest(data)
        blob = digest(b"blob " + str(len(files[path])).encode() + b"\0" + files[path])
        # SHA-256 locators identify bytes, not Git's SHA-1 object namespace.
        locator = {"repository_blob_sha256": digest(files[path]), "source_field_locator": digest(pointer.encode()),
                   "repository_commit": commit, "evidence_locator": "source-evidence/" + blob}
        row = records.setdefault(sha, {"passage_sha256": sha, "normalized_passage_sha256": digest(normalize(text).encode()),
            "passage_file": "passages/" + sha + ".txt", "utf8_bytes": len(data), "families": [],
            "identities": [], "repository_evidence_paths": [], "text": data})
        if family not in row["families"]:
            row["families"].append(family)
        identity = {"source_id": source_id or "local-passage-" + sha[:16],
                    "canonical_url": None, "title": None, "publisher": None, "revision_date": "UNKNOWN",
                    "original_document_sha256": (metadata or {}).get("original_document", {}).get("document_sha256", "UNKNOWN"), **(metadata or {})}
        if identity not in row["identities"]:
            row["identities"].append(identity)
        if locator not in row["repository_evidence_paths"]:
            row["repository_evidence_paths"].append(locator)
        trace = {"path": path, "pointer": pointer, "commit": commit, "family": family,
                 "exact_text_sha256": sha, "repository_file_sha256": digest(files[path]), "public_locator": locator}
        if trace not in private:
            private.append(trace)
        return sha

    def model_source(path, family, identity=None):
        document = load(path)["document"]
        p = document.get("metadata", {}).get("provenance", {})
        meta = safe_provenance(p)
        if identity:
            for key in ["canonical_url", "title", "institutional_publisher"]:
                if key in identity:
                    meta[key] = identity[key]
            if identity.get("model_sha256") and digest(files[path]) != identity["model_sha256"]:
                raise ValueError("parent source carrier mismatch: " + path)
            if identity.get("source_sha256") and digest(document["text"].encode()) != identity["source_sha256"]:
                raise ValueError("parent source text mismatch: " + path)
        return add(document["text"], family, path, "/document/text",
                   (identity or {}).get("source_id", document.get("id", document.get("document_id"))), meta)

    # Golden boundary: every canonical TXT fixture and every committed historical
    # version of those paths. Structural graph tuples are not source passages.
    golden = sorted(p for p in files if p.startswith("tests/fixtures/") and p.endswith(".txt"))
    historical = subprocess.check_output(["git", "log", REF, "--format=%H", "--",
                                         "tests/fixtures"], cwd=root).decode().splitlines()
    history_paths = set(golden)
    for commit in historical:
        names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", commit,
                                         "tests/fixtures"], cwd=root).decode().splitlines()
        history_paths.update(p for p in names if p.endswith(".txt"))
    for path in sorted(history_paths):
        if path in files:
            enumerate_path(FAMILIES[1], path, ["entire UTF-8 TXT bytes"], "canonical golden source fixtures")
        commits = subprocess.check_output(["git", "log", REF, "--format=%H", "--", path], cwd=root).decode().splitlines()
        versions = {}
        for commit in commits + [REF]:
            result = subprocess.run(["git", "show", commit + ":" + path], cwd=root, capture_output=True)
            if result.returncode == 0:
                versions.setdefault(digest(result.stdout), (commit, result.stdout))
        for commit, raw in versions.values():
            carrier = path if path in files and files[path] == raw else "historical-fixture/" + digest(raw)
            if carrier not in files:
                files[carrier] = raw
            add(raw.decode(), FAMILIES[1], carrier, "/", "local-" + Path(path).stem,
                {"title": Path(path).stem.replace("_", " "), "external_origin": "UNKNOWN"}, raw, commit)
            private.append({"family": FAMILIES[1], "historical_repository_path": path,
                            "version_commit": commit, "source_sha256": digest(raw)})

    # Early source-carrier census is a conservative superset of the named controls.
    # Only source document/text and explicitly named source-scope text are extracted.
    early = sorted(p for p in files if p.endswith(".json") and (p.startswith("examples/")
        and ("/evaluations/" not in p or re.search(r"/spec-0(?:0[1-9]|[12][0-9]|3[0-9])[-/]", p))))
    def walk(value, pointer=""):
        if isinstance(value, dict):
            yield pointer, value
            for k, v in value.items():
                yield from walk(v, pointer + "/" + k.replace("~", "~0").replace("/", "~1"))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                yield from walk(v, pointer + "/" + str(i))

    control_documents = {}
    for path in early:
        for _, value in walk(load(path)):
            doc = value.get("document")
            if isinstance(doc, dict) and isinstance(doc.get("text"), str):
                document_id = doc.get("id", doc.get("document_id"))
                if document_id:
                    if document_id in control_documents and control_documents[document_id] != doc["text"]:
                        raise ValueError("control document ID reused for different text")
                    control_documents[document_id] = doc["text"]
    for path in early:
        for pointer, value in walk(load(path)):
            doc = value.get("document")
            if isinstance(doc, dict) and isinstance(doc.get("text"), str):
                enumerate_path(FAMILIES[2], path, [pointer + "/document/text"], "pre-040 source input carriers; conservative superset")
                add(doc["text"], FAMILIES[2], path, pointer + "/document/text", doc.get("id", doc.get("document_id")))
            if (path.endswith("source-scope.json") and pointer == "" and isinstance(value.get("text"), str)):
                enumerate_path(FAMILIES[2], path, ["/text", "/start_char", "/end_char"], "explicit earlier source scope")
                parent_id = value.get("parent_document_id", value["document_id"])
                parent = control_documents.get(parent_id)
                if parent is None or parent[value["start_char"]:value["end_char"]] != value["text"]:
                    raise ValueError("control scope-to-parent mismatch")
                add(value["text"], FAMILIES[2], path, "/text", value.get("document_id"),
                    {"parent_passage_sha256": digest(parent.encode()),
                     "passage_range": {k: value[k] for k in ["start_char", "end_char", "parent_document_id"] if k in value}})
    quantum_path = "examples/sources/spec-011-wikipedia-introduction-to-quantum-mechanics.json"
    qmeta = load(quantum_path)
    qtext_path = "examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904/parent.knowledge.json"
    qtext = load(qtext_path)["document"]["text"]
    if digest(qtext.encode()) != "9e978db999ee67134d347f91fe9f32934c982f4de9b496e4bf664cb00cce23ea":
        raise ValueError("full quantum recovery mismatch")
    add(qtext, FAMILIES[2], qtext_path, "/document/text", "wikipedia-introduction-to-quantum-mechanics",
        {"canonical_url": qmeta["source_url"], "revision_date": qmeta["revision_timestamp"],
         **{k: qmeta[k] for k in ["title", "publisher", "authors", "source_url", "permanent_url", "revision_id", "revision_timestamp", "retrieved_at", "license", "license_url", "revision_history_url"] if k in qmeta}})
    enumerate_path(FAMILIES[2], quantum_path, ["URL/title/publisher/revision/hash metadata only"], "full article recovered from later exact-text carrier")

    packet_sets = {}
    source_by_id = {}
    for number in [41, 42, 44, 45]:
        suffix = "/blind-source-packet.json" if number in [41, 44] else "/source-packet.json"
        paths = sorted(p for p in files if re.search(rf"/spec-0{number}-", p) and p.endswith(suffix))
        if len(paths) != 1:
            raise ValueError("source packet enumeration ambiguity")
        path = paths[0]
        packet_sets[number] = {}
        enumerate_path(FAMILIES[3], path, ["/sources/*/{source_id,text,source_sha256,title,provenance}"], "frozen input packet, never stage outputs")
        for source in load(path)["sources"]:
            sha = digest(source["text"].encode())
            if sha != source["source_sha256"]:
                raise ValueError("corpus passage hash mismatch")
            packet_sets[number][source["source_id"]] = sha
            meta = safe_provenance(source["provenance"])
            meta["title"] = source["title"]
            add(source["text"], FAMILIES[3], path, "/sources/source_id=" + source["source_id"] + "/text", source["source_id"], meta)
            source_by_id[source["source_id"]] = sha
    if (packet_sets[41] != packet_sets[42] or packet_sets[44] != packet_sets[45]
            or len(packet_sets[42]) != 3 or len(packet_sets[45]) != 6 or len(source_by_id) != 9):
        raise ValueError("nine-source freeze identity drift")

    # Late-family closure follows ALL input identity carriers in the nine increment
    # directories. Derived views are excluded because their authoritative parents
    # are included in full; a paraphrase is not treated as a new primary source.
    late_paths = sorted(p for p in files if p.endswith(".json") and re.search(r"/spec-06[0-8]-", p))
    for path in late_paths:
        used = []
        for pointer, value in walk(load(path)):
            identity = value.get("source_identity")
            if isinstance(identity, dict) and identity.get("model_path"):
                model_source(identity["model_path"], FAMILIES[4], identity)
                used.append(pointer + "/source_identity/{model_path,model_sha256,source_sha256}")
            if isinstance(value.get("source_text"), str):
                identity = value.get("source_identity", {})
                text = value["source_text"]
                if identity.get("source_sha256") and digest(text.encode()) != identity["source_sha256"]:
                    raise ValueError("substrate source hash mismatch")
                metadata = {k: identity[k] for k in ["canonical_url", "title", "institutional_publisher"] if k in identity}
                if not identity:
                    parents = []
                    for source_id, sha in sorted(source_by_id.items()):
                        parent = records[sha]["text"].decode()
                        if text in parent:
                            parents.append({"source_id": source_id, "parent_passage_sha256": sha,
                                            "start_char": parent.index(text), "end_char": parent.index(text) + len(text)})
                    if not parents:
                        raise ValueError("unresolved source excerpt parent: " + path + pointer)
                    metadata["exact_parent_ranges"] = parents
                add(text, FAMILIES[4], path, pointer + "/source_text", identity.get("source_id"), metadata)
                used.append(pointer + "/source_text")
            if isinstance(value.get("document"), dict) and isinstance(value["document"].get("text"), str):
                add(value["document"]["text"], FAMILIES[4], path, pointer + "/document/text", value["document"].get("document_id"))
                used.append(pointer + "/document/text")
        if used:
            enumerate_path(FAMILIES[4], path, sorted(set(used)), "source-carrier-only walk; derived/semantic fields never exported")
    freeze_path = next(p for p in late_paths if p.endswith("/fixture-freeze-manifest.json"))
    freeze = load(freeze_path)
    for source in freeze["sources"]:
        if digest(files[source["path"]]) != source["sha256"]:
            raise ValueError("fixture source carrier hash mismatch")
        model_source(source["path"], FAMILIES[4])
    enumerate_path(FAMILIES[4], freeze_path, ["/sources/*/{path,sha256,document_id}", "/corpus_canonical_sha256"], "frozen fixture parents")
    corpus_path = next(p for p in late_paths if p.endswith("/fixture-corpus.json"))
    corpus = load(corpus_path)
    if digest(canonical(corpus)) != freeze["corpus_canonical_sha256"] or len(corpus) != 92:
        raise ValueError("frozen derivative corpus mismatch")
    evidence_checks = 0
    for fixture in corpus:
        for evidence in fixture["packet"]["evidence"].values():
            path = evidence["model_path"]
            text = load(path)["document"]["text"]
            if (digest(files[path]) != evidence["model_sha256"] or digest(canonical(text)) != evidence["source_text_sha256"]
                    or text[evidence["start_char"]:evidence["end_char"]] != evidence["quote"]):
                raise ValueError("derivative-to-source lineage mismatch")
            model_source(path, FAMILIES[4])
            evidence_checks += 1
    enumerate_path(FAMILIES[4], corpus_path, ["/*/packet/evidence/*/{model_path,model_sha256,source_text_sha256,start_char,end_char,quote}"], "all 92 carriers; no candidate/label export")
    definitions = "tests/fixtures/spec066/case-definitions.json"
    defs = load(definitions)
    if isinstance(defs, dict):
        defs = defs.get("cases", defs.get("definitions"))
    if {re.sub(r"^\d+-", "", r["source"]) for r in defs} - set(source_by_id):
        raise ValueError("uncovered derivative definition source")
    enumerate_path(FAMILIES[4], definitions, ["/*/source"], "definition parent identity only; numeric corpus prefixes stripped")
    for path in late_paths:
        if path.endswith(("/selection-manifest.json", "/frozen-identities.json")):
            value = load(path)
            for pointer, child in walk(value):
                if child.get("corpus_sha256") and child["corpus_sha256"] != freeze["corpus_canonical_sha256"]:
                    raise ValueError("late derivative corpus identity mismatch")
            enumerate_path(FAMILIES[4], path, ["source corpus identity fields only"], "later consumers bind to the same source corpus")

    counts = {family: sum(family in r["families"] for r in records.values()) for family in FAMILIES}
    rules = [
        ("COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION", "Both recovered originals verified; decoded RTF yields an order-free fingerprint. Mandatory broad subject blacklist bounds unknown input conservatively.", "Original input identity/passage/lineage UNKNOWN. Response is not substituted for source. Fingerprint alone cannot clear overlap."),
        ("COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION", "All TXT golden paths and their committed historical versions enumerated; exact bytes retained. Structural edge tuples are not source documents.", "Local authored fixtures have no established external publisher/revision. Exclude substantive overlap conservatively; do not fabricate origin."),
        ("COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION", "All earlier document.text input carriers plus explicit source scopes enumerated as a conservative superset. Full frozen quantum article recovered and checked, not reconstructed.", "Local authored controls lack external origin. Quantum fixed revision known; original HTML bytes not resident. All controls and derivative/paraphrase overlaps excluded."),
        ("COMPLETE_EXACT", "Three plus six frozen source IDs/texts crosschecked against both earlier freezes. All exact input passages and recorded publication identities/hashes retained.", "Some original fetched document bytes are not repository-resident; their recorded hashes are not claimed to be passage hashes. Exclude entire canonical documents, other revisions/excerpts and derivatives."),
        ("COMPLETE_EXACT", "Every source identity/text carrier across 060–068 resolved to its exact parent; 92 derivative packets traced through evidence ranges and canonical-JSON hashes. Synthetic source fixture included independently.", "Derived output prose/candidates are intentionally withheld; complete parent texts and document/derivative blacklists cover their overlap. No claim that withheld candidates are original sources."),
    ]
    families = [{"family": family, "status": status, "distinct_exact_passage_byte_variants": counts[family],
                 "enumeration_rationale": rationale, "known_gaps": gaps}
                for family, (status, rationale, gaps) in zip(FAMILIES, rules)]
    require_safe(families)
    if any(counts[f] == 0 for f in FAMILIES[1:]):
        raise ValueError("empty exact source family")
    public_records = []
    entries = {"README.md": README.encode(), "selector-v1.1-authority.txt": AUTHORITY.encode(),
               "verify.py": VERIFIER.encode(), "recovered-electromagnetism-fingerprint.json": stable(fingerprint),
               "family-completeness.json": stable({"families": families, "all_five_safe": True,
                   "deduplication": "Exact UTF-8 byte SHA-256; normalized equivalence grouped separately, never conflated with exact bytes. Families may share passages."}),
               "normalization.json": stable({"id": "UTF8-CRLF-CR-to-LF-strip-v1", "exact": "UTF-8 bytes of repository source TXT or decoded JSON source text; unchanged",
                   "normalized": "CRLF and CR to LF, then Python str.strip; no other rewrites",
                   "fingerprint_only": "NFKC casefold; Unicode alphanumeric tokens excluding underscores; unordered SHA-256 set of five-word windows. Not a source reconstruction or clearance certificate.",
                   "hash_domains": "Passage hashes are raw UTF-8, carrier hashes are full repository file bytes; original document hashes retain recorded domain. Historical fixture JSON-string hashes verified privately as canonical JSON, not raw passage hashes."})}
    for sha, record in sorted(records.items()):
        data = record.pop("text")
        entries[record["passage_file"]] = data
        record["families"].sort()
        record["identities"].sort(key=lambda r: stable(r))
        record["repository_evidence_paths"].sort(key=lambda r: stable(r))
        public_records.append(record)
    entries["contamination-reference-manifest.json"] = stable({"schema": "source-contamination-reference.v2",
        "sources": public_records, "recovered_response": "recovered-electromagnetism-fingerprint.json",
        "family_completeness": "family-completeness.json", "normalization": "normalization.json",
        "repository_path_index": "Withheld context-bearing canonical paths mapped exactly to source-evidence locators by custody; not needed for selector access.",
        "exclusion_policy": "Same documents across revisions/excerpts, derivatives/paraphrases and substantive content overlap are excluded. UNKNOWN origin requires conservative overlap screening, not guessed lineage. Fingerprints are auxiliary; ambiguity quarantines."})
    entries["package-integrity.json"] = stable({"files": {name: {"sha256": digest(raw), "bytes": len(raw)} for name, raw in sorted(entries.items())},
        "excluded_self": "package-integrity.json self hash external to avoid cycle"})
    leakage_check(entries)
    outputs = {str(OUT / name): raw for name, raw in entries.items()}
    archive = zip_bytes(entries)
    outputs[str(ZIP)] = archive
    report = {
        "packet": CONTRACT, "input_commit": REF, "result": "SANITIZED_CONTAMINATION_EXPORT_READY",
        "recommended_next_step": "RETURN_V1_1_PACKAGE_TO_SAME_SELECTOR", "human_gate": "OWNER_REVIEW",
        "owner_verdict": "PENDING", "promotion": "NOT_AUTHORIZED", "families": families,
        "family_enumeration": enumerations, "source_path_index": private,
        "deduplication": "Exact UTF-8 SHA-256 across families; raw/newline variants distinct. Normalize only for overlap equivalence, never to claim exact identity.",
        "exact_passages": len(public_records), "normalized_passages": len({r["normalized_passage_sha256"] for r in public_records}),
        "nine_source_identities": source_by_id, "derivative_evidence_range_checks": evidence_checks,
        "historical_fixture_paths": sorted(history_paths), "historical_fixture_commits_examined": historical,
        "late_family_census_paths": late_paths,
        "enumeration_limit": "Canonical tracked source-input carriers and their formal fixture history at frozen input commit, not arbitrary inline unit-test sentences or unavailable external history. No external or provisional selector package is enumerated.",
        "sanitization": "Positive source-field allowlist plus negative leakage checks on all ZIP members. Full context-bearing path index and diagnostics withheld outside ZIP. Software architecture is legitimate historical source subject, not project architecture.",
        "electromagnetism_inspection": "Read-only textutil conversion to stdout; full decoded response held only transiently. PDF/RTF untouched and not copied. Order-free hashed tokens plus blanket intro-domain exclusion only.",
        "known_gate_collision": "Required nested README.md is newly included by BENCH-001's open-ended Markdown scan when regenerating its old lock. Original benchmark files, executable and frozen lock remain byte-identical. No benchmark freeze repair or waiver is made here; owner review must resolve this mechanical gate before future benchmark execution.",
        "readiness_scope": "READY describes safe source-only export, not a new benchmark-harness readiness claim or full-suite success. BENCH-001's accepted readiness result and immutable artifacts are unchanged; its new regeneration collision is separately unresolved.",
        "dependencies": {"production_changes": [], "packages_added": [],
                         "custody_generator": "Existing Git, Python stdlib and macOS /usr/bin/textutil read-only RTF decoding",
                         "standalone_verifier": "Python stdlib only; no repository or network access"},
        "custody_executable_identities": {p: digest((root / p).read_bytes())
            for p in ["tools/custody002_prepare.py", "tests/test_custody002.py"]},
        "exact_source_git_policy": {"path": str(BASE / ".gitattributes"),
            "sha256": digest((root / BASE / ".gitattributes").read_bytes()),
            "scope": "Only new export-v2 passages/*.txt: -text -diff. Original quantum input has trailing spaces that must remain exact. Rule is outside selector ZIP; source bytes and hashes unchanged."},
        "zip_path": str(ZIP), "zip_sha256": digest(archive), "zip_bytes": len(archive),
        "review_command": "open " + str(OUT / "README.md"),
        "continuation_prompt": "In the SAME independent selector context, use only source-selector-continuation-v1.1.zip. Verify integrity locally, read its reference and narrow authority, preserve frozen source-selection-v1 byte-identically, adjudicate the three quarantined v1 candidates, and extend ONLY neuroscience/mechanism and hydrology/process after BOTH ordered D3–D6 lists are frozen. Preserve every v1 eligibility/logging/first-eligible rule and every failure/rejection; freeze all five jointly only after eligibility and contamination gates pass. At D3–D6 exhaustion preserve missingness and stop. Do not request repository, architecture, performance, learner or benchmark-arm context; do not execute any benchmark.",
        "zero_activity": {"provider_calls": 0, "model_calls": 0, "benchmark_retrieval": 0,
                          "selector_candidates_read": 0, "contamination_adjudications": 0,
                          "evaluation_network_calls": 0, "git_coordination_only": True},
        "protected_historical_files": len(protected),
        "validation_evidence": "custody-002-gate-results.json and custody-002-full-offline-suite.txt (outside selector ZIP)",
        "stopping_boundary": "OWNER_REVIEW; no follow-up activation or selector action performed by this project context",
    }
    outputs[str(BASE / "custody-002-report.json")] = stable(report)
    outputs[str(BASE / "custody-002-protected-state.json")] = stable({"input_commit": REF, "files": protected})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build()
    for path, raw in outputs.items():
        target = ROOT / path
        if args.check:
            if not target.is_file() or target.read_bytes() != raw:
                raise ValueError("non-deterministic output: " + path)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    print(json.dumps({"result": "SANITIZED_CONTAMINATION_EXPORT_READY", "files": len(outputs),
                      "zip_sha256": digest(outputs[str(ZIP)]), "provider_calls": 0, "owner_verdict": "PENDING"}))


if __name__ == "__main__":
    main()
