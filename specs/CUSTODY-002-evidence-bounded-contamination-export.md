# CUSTODY-002 — Evidence-Bounded Contamination Export

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Repair the over-constrained contamination contract exposed by CUSTODY-001 without weakening benchmark independence.

CUSTODY-001 incorrectly required complete original-source lineage for every exclusion family. The recovered electromagnetism artifact proves historical exposure to substantial electromagnetism content and representations, but does not preserve the identity of the original input source/passage. That uncertainty must remain explicit; it must not block unrelated benchmark strata globally and must not be filled by inference.

Canonical principle:

> **Known uncertainty becomes an exclusion constraint, not invented certainty and not automatically a global stop.**

CUSTODY-002 creates an evidence-bounded source-only contamination export and, only if sufficiently complete for safe selection, a narrowly bounded selector-v1.1 continuation package.

It does not inspect the selector's provisional candidates, select sources, retrieve sources, or run benchmark arms.

## Entering CUSTODY-001 finding

Record:

`FAMILY_COMPLETENESS_UNRESOLVED_DUE_TO_OVERCONSTRAINED_LINEAGE_REQUIREMENT`

Accepted facts:
- recovered electromagnetism response artifacts exist and are immutable historical evidence;
- original electromagnetism input source/passage identity is unknown;
- wholesale export of the response artifact would leak learner/representation context;
- later fixtures cannot be substituted for the unknown original;
- CUSTODY-001 correctly stopped under its contract;
- no continuation authority or ZIP was issued.

## Family-level completeness states

Audit **every** exclusion family independently. Do not stop at the first incomplete family.

Each family receives exactly one status:

### `COMPLETE_EXACT`
Exact historical source/passages and relevant lineage are available.

### `COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION`
Available evidence is sufficient to impose conservative contamination exclusions, but some original-source/revision lineage is explicitly unknown.

### `PARTIAL`
Some historical source material is known, but coverage is insufficient to claim safe contamination screening for that family.

### `UNRESOLVED`
Repository evidence cannot establish a usable exclusion boundary.

A family may be safe for selector use only if status is `COMPLETE_EXACT` or `COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION`.

If any required family remains `PARTIAL` or `UNRESOLVED`, do not issue selector continuation authority.

## Required exclusion families

Audit:

1. recovered electromagnetism;
2. golden fixtures;
3. quantum/economics/software controls;
4. SPEC-042/045 nine-source corpus;
5. SPEC-060–068 sources/derivatives.

For each family enumerate all distinct historical source documents/passages supported by repository evidence.

## Electromagnetism special contract

Do not attempt to identify or reconstruct the missing original input source.

Record:

- canonical recovered artifacts:
  - `audits/electromagnetism.pdf`
  - `audits/electromagnetism.rtf`
- artifact hashes;
- subject/content exposure represented by those artifacts;
- `original_input_source_identity = UNKNOWN`;
- `original_input_passage = UNKNOWN`;
- `original_input_lineage = UNKNOWN`.

The sanitized selector export must **not** include the full recovered response artifact.

Instead derive a source-only exclusion fingerprint sufficient to conservatively detect substantive overlap without revealing the response architecture. Allowed fields:

- exclusion family;
- subject/domain labels directly evidenced by artifact;
- distinctive factual/content phrases or n-gram/minhash/simhash-style fingerprints generated mechanically from artifact text;
- normalized content hashes/chunk hashes;
- explicit blacklist rule covering introductory electromagnetism / the preserved response's substantive content;
- lineage limitation statement.

Do not include:
- representation headings;
- diagrams;
- learner recommendations;
- conclusions about how to teach;
- architecture/product language;
- owner judgments.

Electromagnetism should normally qualify as `COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION` only if the exported fingerprint + blacklist can conservatively prevent selection of materially overlapping electromagnetism content. If not, mark `PARTIAL`.

## Exact-source families

Where historical source passages are known, export only contamination-relevant source evidence:

- family;
- source_id;
- canonical URL where known;
- title/publisher/revision/date;
- original-document hash;
- exact historical passage text or source-only bytes where repository-resident;
- exact and normalized passage hashes;
- normalization identity;
- lineage/derivative relationships needed to reject revisions/paraphrases/overlap;
- repository evidence paths.

Do not export experimental outputs or semantic interpretations.

## Sanitization boundary

The continuation package must not contain:

- benchmark arm names/prompts/schemas;
- architecture descriptions;
- experiment outcomes;
- model performance;
- learner verdicts;
- current-team hypotheses;
- IA-001 recommendation;
- STATUS.md;
- semantic/representation artifacts except source-only historical text required for overlap;
- implementation code beyond minimal standalone overlap verifier/normalizer.

Run explicit leakage tests.

## Completeness methodology

For each family document:

- repository paths searched/enumerated;
- manifest/report fields used to enumerate source identities;
- deduplication rule;
- known lineage;
- known gaps;
- why assigned completeness state is justified.

Do not equate “no more files found” with completeness without explaining the enumeration boundary.

## Sanitized export

If all five families are safe (`COMPLETE_EXACT` or `COMPLETE_WITH_KNOWN_LINEAGE_LIMITATION`), create:

`audits/independent-architecture-audit-001/benchmark-readiness-v1/contamination-reference-export-v2/`

with:
- `README.md`;
- `contamination-reference-manifest.json`;
- source-only evidence/fingerprints;
- normalization spec;
- optional minimal offline overlap checker;
- family completeness report.

Package with continuation authority as:

`source-selector-continuation-v1.1.zip`

## Selector v1.1 authority

The ZIP may authorize the **same independent selector context** to:

1. preserve its frozen source-selection-v1 package byte-identically;
2. use this contamination export only for overlap/lineage checks;
3. adjudicate its three already-quarantined provisional passages;
4. extend only:
   - neuroscience / mechanism;
   - hydrology / process;
5. before any new retrieval, freeze an ordered D3–D6 candidate document list for each exhausted slot;
6. append after exhausted v1 D1/D2; never reorder/revisit them;
7. preserve all v1 domain/shape/length/authority/whole-unit/figure-dependence/logging/first-eligible rules;
8. retrieve candidates only after both D3–D6 lists are frozen;
9. take first eligible passage under frozen order;
10. preserve all failures/rejections;
11. freeze all five together only after eligibility + contamination gates pass.

Maximum extension: four additional documents per exhausted slot. If D3–D6 exhaust, preserve missingness and stop. No further automatic extension.

The selector must not receive Knowledge Compiler repo access, benchmark arms, architecture context or performance evidence.

## Decision branches

Choose exactly one:

- `SANITIZED_CONTAMINATION_EXPORT_READY`
- `HISTORICAL_EXCLUSION_COVERAGE_INSUFFICIENT`
- `SANITIZATION_LEAKAGE_RISK`
- `INCONCLUSIVE`

Recommended next step exactly one:

- `RETURN_V1_1_PACKAGE_TO_SAME_SELECTOR`
- `MANUAL_HISTORICAL_SOURCE_RECOVERY_REQUIRED`
- `BENCHMARK_CONTAMINATION_PROTOCOL_REDESIGN`
- `MORE_DIAGNOSIS_REQUIRED`

## Validation

At minimum:

- audit all five families independently;
- exact/normalized hash regeneration;
- family enumeration/deduplication tests;
- electromagnetism UNKNOWN lineage preserved;
- no fabricated source identity;
- sanitization/leakage tests;
- no selector provisional candidate content imported or inspected;
- historical evidence unchanged;
- deterministic package regeneration;
- zero network/model/provider calls;
- zero benchmark retrieval;
- secret safety;
- control-plane tests;
- full offline suite with the known owner-accepted AUDIT-001 STATUS-hash failure reported separately rather than repaired;
- `git diff --check`.

## Completion

If safe, create/push the sanitized ZIP and report its exact path/hash plus the exact continuation prompt for the same selector.

If unsafe, do not create authority/ZIP.

Clear STATUS active packet and stop at `OWNER_REVIEW`.

Do not perform source selection or contamination adjudication in this project context.
