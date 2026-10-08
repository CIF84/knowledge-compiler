"""Source-reference integrity only; no network and no contamination clearance."""
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
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if hashlib.sha256(normalized.encode()).hexdigest() != item["normalized_passage_sha256"]:
        raise ValueError("normalization mismatch")
print("PASS: integrity/normalization only; not contamination clearance")
