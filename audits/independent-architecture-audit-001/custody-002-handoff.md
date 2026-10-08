# CUSTODY-002 — Owner review

Result: `SANITIZED_CONTAMINATION_EXPORT_READY`.
Next step: `RETURN_V1_1_PACKAGE_TO_SAME_SELECTOR`.
Human gate: `OWNER_REVIEW`. Owner verdict: `PENDING`. Promotion: `NOT_AUTHORIZED`.
STATUS active pointer is `NONE`; no follow-up packet is activated.

## Independent family findings

| Exclusion family | Classification | Exact passage byte variants |
| --- | --- | ---: |
| Recovered electromagnetism | `COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION` | 0; response fingerprint only |
| Golden fixtures | `COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION` | 6 |
| Quantum/economics/software controls (conservative earlier-input superset) | `COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION` | 9 |
| SPEC-042/045 nine-source corpus | `COMPLETE_EXACT` | 9 |
| SPEC-060–068 sources/derivatives | `COMPLETE_EXACT` | 55, including exact source excerpts |

Families overlap. Across the export there are 71 distinct exact UTF-8 passage
byte variants / 65 normalized texts. The later family includes all eight fixture
parent sources, 46 exact source excerpts and the independently preserved synthetic
source fixture. All 92 derivative carriers were traced, with 587 evidence-range
checks. Exact source excerpts carry parent hashes and recoverable character ranges;
they are not newly synthesized prose. Corpus input packets also crosscheck against
their earlier three-source and six-source freezes.

Recovered original-input **source identity, passage and lineage remain UNKNOWN**.
The PDF and RTF remain byte-identical. Neither response is exported. The decoded
RTF contributes only order-free hashed five-word shingles and a normalized hash;
the mandatory introductory-electromagnetism/content blacklist is conservative
even when no fingerprint matches. Later electromagnetism fixtures are distinct,
not substitutes for the missing original input.

Exact/source-only coverage is bounded by canonical tracked input carriers and
formal golden-fixture history at `65c31162c4a11ff67f88309a46981fb1eecb12f5`.
Unavailable external history, original publication bytes where only their hashes
survive, and local authored inputs' unknown external origins are explicitly
recorded, not fabricated. Whole-document/revision/derivative and substantive-overlap
exclusions, plus quarantine for ambiguity, make those limits conservative.

## Export and inspection

Only send this ZIP, not this handoff, repository reports or the audit dossier:

`audits/independent-architecture-audit-001/benchmark-readiness-v1/source-selector-continuation-v1.1.zip`

SHA-256: `b4116ca663de52c67ab1334d657b9996d458fef929e130137997bc0bc8e8911d`

Bytes: 465,149. Members: 79. Fixed ZIP timestamps and sorted members;
deterministic regeneration and standalone integrity/normalization verifier pass.

Source-only directory:
`audits/independent-architecture-audit-001/benchmark-readiness-v1/contamination-reference-export-v2/`

Owner review command:

```sh
open audits/independent-architecture-audit-001/custody-002-handoff.md
```

Offline integrity check (does not adjudicate contamination):

```sh
.venv/bin/python audits/independent-architecture-audit-001/benchmark-readiness-v1/contamination-reference-export-v2/verify.py
.venv/bin/python tools/custody002_prepare.py --check
```

Full canonical path/pointer mappings, enumeration boundaries, checked fields,
deduplication and gaps remain in `custody-002-report.json` **outside the ZIP**.
Public evidence uses opaque content-addressed file/field locators mapped exactly
by custody. This avoids leaking architecture-bearing filenames or block-path
structure while retaining traceability. The selector requires no repository access.

## Validation and limits

Focused custody/control-plane suite: **43 passed**. Source identity, normalization,
all-family coverage, UNKNOWN-lineage, unsafe-family negatives, leakage injections,
standalone verification/corruption and deterministic regeneration pass. All 2,461
protected historical files remain exact, including BENCH-001's original lock,
historical sources, baselines, production code and prior evidence. Six pre-existing
untracked `.DS_Store` files are preserved unchanged and excluded from the commit.
No dependencies added; the custody generator uses existing Git/Python stdlib and
macOS `textutil`. The standalone verifier uses only Python stdlib.

A repository-only `.gitattributes` rule marks just the new passage copies
`-text -diff` for exact byte custody (outside the selector ZIP). Frozen quantum
input includes two inherited trailing-space occurrences across the full article
and scope; they are preserved, not cleaned or silently normalized. Exact hashes
and source files remain independently inspectable; code/docs still receive the
normal staged diff check. The log preserves failure content with whitespace-only
terminal padding removed.

Full offline suite: **1,212 passed, 2 failed**. This is not a green full-suite result.

- Owner-accepted AUDIT-001 mutable-STATUS regeneration failure: reported unchanged,
  not repaired.
- Newly exposed BENCH-001 recursive-Markdown enumeration collision: its old
  generator picks up the required nested export README, so its regenerated lock
  differs. The original lock, rules, harness and readiness report are byte-identical.
  This failure is **not waived**. Owner resolution is required before future
  benchmark execution; no benchmark freeze repair is authorized/performed here.

`SANITIZED_CONTAMINATION_EXPORT_READY` is a source-export safety result, not a new
benchmark-readiness claim. BENCH-001's recorded owner acceptance and original
mechanical `INCONCLUSIVE` result are preserved. Detailed gate outcomes and full
failure output: `custody-002-gate-results.json`, `custody-002-full-offline-suite.txt`.

Zero model/provider/experimental-network calls, zero benchmark retrieval/selection,
zero provisional-selector candidate reads/imports, zero contamination adjudications
in this context, zero benchmark execution, zero historical evidence changes.
Only authorized Git fetch/push coordinate canonical state.

## Exact continuation prompt — same selector only

> In the SAME independent selector context, use only source-selector-continuation-v1.1.zip. Verify integrity locally, read its reference and narrow authority, preserve frozen source-selection-v1 byte-identically, adjudicate the three quarantined v1 candidates, and extend ONLY neuroscience/mechanism and hydrology/process after BOTH ordered D3–D6 lists are frozen. Preserve every v1 eligibility/logging/first-eligible rule and every failure/rejection; freeze all five jointly only after eligibility and contamination gates pass. At D3–D6 exhaustion preserve missingness and stop. Do not request repository, architecture, performance, learner or benchmark-arm context; do not execute any benchmark.

Both ordered extension lists must be pre-frozen before any new retrieval; at most
four additional documents per exhausted slot. Never reorder/revisit exhausted
D1/D2. No further automatic extension, architecture decision or project verdict.
If the frozen v1 contract is unavailable or contradictory, the selector must stop
rather than reconstruct it. This repository run stops at owner review and does
not send the package or perform selector actions.
