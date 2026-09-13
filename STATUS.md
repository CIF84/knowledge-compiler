# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected four-surface model:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ represents the current idea using the fitting semantic representation

INSPECT / SELECTED / PREVIEW
→ explains representation-local semantic components without changing learner location

EXPLORE NEXT
→ proposes future traversal
```

## Semantic-to-representation compiler

`SPEC-039 — semantic-to-representation compiler gate`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `SEMANTIC_REPRESENTATION_COMPILER_CONFIRMED_WITH_COVERAGE_GAPS`

## Blind evaluation harness

`SPEC-040 — blind out-of-sample evaluation harness`

Implementation status: `IMPLEMENTED_REVIEWED`

Frozen harness/compiler identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Initial blind run and diagnosis

`SPEC-042 — blind out-of-sample live execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DIAGNOSIS`

`SPEC-043 — blind failure diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `DIAGNOSIS_CONFIRMED_NO_CONTRACT_CHANGE_REPLICATION_REQUIRED`

Accepted findings:

- 2 `EXTRACTION_GRANULARITY` rejected objects;
- 1 `MODEL_ERROR` rejected object;
- 0 `CONTRACT_GAP`, `VALIDATION_BUG`, or `AMBIGUOUS`;
- strict declared-identity validation behaved correctly;
- evidence was insufficient for a contract change;
- replication was required before repair.

## Blind replication source set

`SPEC-044 — blind replication source set freeze`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `SIX_SOURCE_REPLICATION_PACKET_APPROVED_FOR_EXACT_TRANSMISSION`

Accepted evidence:

- six unrelated priority-rank-1 U.S. institutional sources;
- fixed predeclared domain order;
- exact 300–650-word passages frozen with provenance and SHA-256;
- repository non-overlap: zero matches;
- semantic shape not used for selection;
- no answer key and no model behavior inspected during selection;
- frozen compiler/harness and SPEC-038 baseline preserved;
- zero provider/model calls during source freeze.

Frozen packet SHA-256:

`85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b`

Frozen manifest SHA-256:

`beaf3df4a941afc7fadf2abf13543affeae798e3d14486798cbb0060fccdc57e`

## Blind replication live execution

`SPEC-045 — blind replication live execution`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Owner verdict: `PENDING`

Recorded objective result:

- exactly six approved `gpt-5.6-luna` Responses API calls executed in the frozen source order;
- astronomy, ecology, and transportation passed deterministic admission;
- chemistry, biology, and statistics failed closed with complete attempts preserved;
- four rejected objects classify as 3 `MODEL_ERROR`, 1 `EXTRACTION_GRANULARITY`, 0 `CONTRACT_GAP`, 0 `VALIDATION_BUG`, and 0 `AMBIGUOUS`;
- one materially source-supported undeclared identity occurred, but it was not a process/event reification and the same dangling-identity mechanism did not recur across two new strata;
- frozen compiler, validator, representation behavior, and protected baselines remained unchanged.

Canonical evidence:

`examples/evaluations/spec-045-blind-replication-live-execution-20260912/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-045 is implemented and awaiting owner review. Its canonical evidence is
`examples/evaluations/spec-045-blind-replication-live-execution-20260912/report.json`.

No packet is active. No provider/model call, retry, repair, semantic adaptation,
semantic-contract change, or product promotion is authorized.

## Current product question

```text
3 admitted / 3 failed closed
        ↓
4 rejected objects classified offline
        ↓
3 MODEL_ERROR / 1 EXTRACTION_GRANULARITY
        ↓
no repeated process/event dangling-identity mechanism
        ↓
OWNER REVIEW
        ↓
decide whether evidence supports narrow alignment work or points elsewhere
```

The immediate goal is owner interpretation of the preserved replication evidence, not repair.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 frozen harness/compiler identity `5622df131dc71346d5890f42ce16fe1e3e55f33a`;
- SPEC-042 complete execution evidence;
- SPEC-043 taxonomy, diagnosis, and canonical report;
- SPEC-044 exact six-source packet, order, hashes, manifest, selection evidence, and decision framework;
- prompt `spec-010-v1`;
- extraction schema;
- semantic vocabulary;
- grounding/provenance;
- strict declared-identity validation;
- representation strategy rules and current renderer coverage;
- SPEC-033 navigation semantics;
- SPEC-035 explanation/navigation isolation;
- SPEC-036 inspection semantics;
- SPEC-037 My Map grammar;
- unrelated user work.

## Explicitly forbidden

Do not:

- exceed six provider calls;
- retry or repair any result;
- use another model;
- edit or substitute frozen sources;
- retrieve external evidence during execution or classification;
- add/normalize missing entities;
- change extraction granularity;
- change prompt/schema/vocabulary/validation;
- adapt implementation between calls;
- change representation or renderer logic;
- redesign UI/navigation;
- implement Back/history or other deferred product features;
- implement a fix after classification;
- promote the result or authorize follow-up work.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
