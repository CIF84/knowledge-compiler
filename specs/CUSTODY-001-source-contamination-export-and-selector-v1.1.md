# CUSTODY-001 — Benchmark Source Contamination Export and Selector v1.1 Authority

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Prepare the minimum **source-only** exclusion package required by the independent source selector's frozen `source-selection-v1` result, and freeze narrowly bounded authority for that same selector to continue only the two exhausted strata under `source-selection-v1.1`.

This packet does not select benchmark sources and must not inspect provisional selector candidates.

## Frozen selector finding

The independent selector froze v1 with:
- zero admitted sources;
- three provisional passages quarantined solely pending contamination review;
- mechanism/neuroscience and process/hydrology unfilled after their pre-frozen two-document lists failed retrieval;
- exact request for a complete source-only exclusion export and explicit versioned authority to extend only those exhausted lists.

The selector package remains external and unchanged.

## Workstream A — source-only contamination export

Create:

`audits/independent-architecture-audit-001/benchmark-readiness-v1/contamination-reference-export-v1/`

It must contain **only** information needed to determine whether a candidate source overlaps prohibited historical benchmark/evaluation material.

Required exclusion families:

1. recovered electromagnetism;
2. golden fixtures;
3. quantum/economics/software controls;
4. SPEC-042/045 nine-source corpus;
5. SPEC-060–068 sources/derivatives.

For every distinct historical source/document/passsage represented by these families, export where repository evidence supports it:

- family;
- source_id;
- canonical_url;
- title;
- publisher;
- revision/date;
- original_document_sha256;
- original bytes OR independently reproducible repository identity/path;
- exact historical passage text;
- exact_passage_sha256;
- normalized_passage_sha256;
- normalization specification;
- revision/derivative/overlap lineage;
- source/evidence repository paths.

Include a **family completeness declaration** explaining exactly how repository evidence was searched/enumerated and any limitations.

### Critical sanitization boundary

The export must NOT contain:

- benchmark arm prompts/schemas;
- architecture descriptions;
- learner verdicts;
- experiment outcomes;
- model performance;
- current-team hypotheses;
- IA-001 recommendations;
- STATUS.md;
- implementation code except a minimal standalone verifier/normalizer if needed;
- semantic models or derived conclusions except source lineage needed for contamination detection.

This is a source-identity/text package, not project context.

If an excluded family cannot be made complete from repository evidence, report `FAMILY_COMPLETENESS_UNRESOLVED` and stop; do not guess.

## Workstream B — selector v1.1 authority

Create a standalone:

`selector-v1.1-authority.md`

that authorizes the **same independent selector context** to:

1. preserve source-selection-v1 byte-identically;
2. consume the source-only contamination export solely for overlap/lineage checks;
3. adjudicate the three quarantined v1 passages against that export;
4. extend only:
   - slot 1 neuroscience/mechanism;
   - slot 2 hydrology/process;
5. before any new retrieval, freeze a new ordered candidate list for each exhausted slot;
6. retain the same domain, shape, length, authority, whole-unit, figure-dependence, contamination, logging and first-eligible rules from v1;
7. append candidates after the exhausted v1 D1/D2 entries; never reorder/revisit them;
8. take the first eligible new passage in the pre-frozen v1.1 order;
9. preserve all retrieval failures/rejections;
10. jointly freeze all five only after every eligibility and contamination gate passes.

### v1.1 extension limits

For each exhausted slot:
- maximum 4 additional documents (`D3`–`D6`);
- same domain and dominant shape;
- stable public institutional/revision-addressable/archival sources;
- selector chooses and freezes ordered D3–D6 identities before retrieving any D3–D6 passage;
- no source may be selected because it appears easy, visually attractive, or likely to favor an arm;
- no broadening to another domain/shape;
- no replacement of v1 provisional sources because of difficulty;
- no arm output or Knowledge Compiler access.

If D3–D6 exhaust, preserve missingness and stop. No further automatic extension.

## Export manifest

Create:
- `contamination-reference-manifest.json`;
- exact file hashes;
- family coverage;
- completeness status;
- normalization identity;
- zero-sensitive-context declaration.

Package the sanitized export and authority into:

`source-selector-continuation-v1.1.zip`

The ZIP must contain only:
- contamination reference export;
- standalone v1.1 authority;
- verifier/readme if needed.

It must not contain the benchmark harness or project architecture.

## Validation

At minimum:
- all exported source claims trace to repository evidence;
- exact/normalized hashes regenerate;
- exclusion-family enumeration test;
- no forbidden project-context strings/files in package;
- historical evidence unchanged;
- no selector candidate material imported into repository;
- no network/provider/model calls;
- no benchmark source retrieval;
- deterministic package regeneration;
- secret safety;
- `git diff --check`.

## Completion

Commit/push the sanitized package and report:
- package path/hash;
- family completeness;
- any unresolved historical source identities;
- exact selector continuation prompt.

Stop at `OWNER_REVIEW`.

Do not perform contamination adjudication or source selection in this project context.
