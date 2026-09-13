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

## Blind evaluation foundation

`SPEC-040 — blind out-of-sample evaluation harness`

Implementation status: `IMPLEMENTED_REVIEWED`

Frozen harness/compiler identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Initial blind run + diagnosis

`SPEC-042 — blind out-of-sample live execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DIAGNOSIS`

`SPEC-043 — blind failure diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `DIAGNOSIS_CONFIRMED_NO_CONTRACT_CHANGE_REPLICATION_REQUIRED`

Accepted initial diagnosis:

- 2 `EXTRACTION_GRANULARITY` rejected objects;
- 1 `MODEL_ERROR`;
- 0 `CONTRACT_GAP`, `VALIDATION_BUG`, `AMBIGUOUS`;
- strict declared-identity validation behaved correctly;
- replication was required before repair.

## Blind replication

`SPEC-044 — blind replication source set freeze`

Implementation status: `IMPLEMENTED_REVIEWED`

`SPEC-045 — blind replication live execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_FAILURE_MODE_ANALYSIS`

Owner verdict: `REPLICATION_CONFIRMS_HETEROGENEOUS_MODEL_ERROR_DOMINATED_FAILURES`

Accepted replication findings:

- 3 of 6 new sources passed deterministic admission;
- 3 failed closed;
- 4 rejected semantic objects: 3 `MODEL_ERROR`, 1 `EXTRACTION_GRANULARITY`;
- 0 `CONTRACT_GAP`, `VALIDATION_BUG`, `AMBIGUOUS`;
- the earlier process/event dangling-identity pattern did not recur across unrelated new domains;
- model errors numerically dominate the replication failures;
- narrow extraction→contract alignment is not justified by current evidence;
- strict fail-closed behavior remains protected.

Combined blind evidence entering the next diagnostic step:

```text
9 unseen sources total

known rejected objects:
MODEL_ERROR             4
EXTRACTION_GRANULARITY  3
CONTRACT_GAP            0
VALIDATION_BUG          0
AMBIGUOUS               0
```

## Current approved work packet

```text
specs/SPEC-046-extraction-reliability-failure-mode-analysis.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-046 is authorized to analyze immutable SPEC-042 through SPEC-045 evidence offline and determine where extraction failures originate.

It must distinguish failure **origin stage** from deterministic **detection stage**, aggregate failure modes across all nine blind sources, separate extraction reliability from trust-boundary reliability, map observed origin stages to candidate intervention classes, and recommend exactly one next experiment class.

No repair or behavior change is authorized.

No provider/model/network call is authorized.

## Current product question

```text
9 blind sources
        ↓
4 admitted / 5 failed closed
        ↓
7 known rejected semantic objects
        ↓
classify WHERE errors originate
        ↓
separate extraction failure from trust-boundary success
        ↓
identify one evidence-backed intervention class to test next
```

The goal is not to improve pass rate in this packet. The goal is to choose the right experimental lever.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 frozen harness/compiler identity `5622df131dc71346d5890f42ce16fe1e3e55f33a`;
- SPEC-041/042 source packet, manifest, raw responses, run history, and evidence;
- SPEC-043 taxonomy, accepted classifications, and canonical report;
- SPEC-044/045 source packet, manifest, raw responses, run history, classifications, and evidence;
- prompt `spec-010-v1`;
- extraction schema;
- semantic vocabulary;
- grounding/provenance;
- strict declared-identity validation;
- representation strategy rules and renderer coverage;
- SPEC-033 navigation semantics;
- SPEC-035 explanation/navigation isolation;
- SPEC-036 inspection semantics;
- SPEC-037 My Map grammar;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use web/network retrieval;
- rerun or repair historical extraction;
- change historical classifications silently;
- change model, prompt, schema, semantic vocabulary, grounding, or validation;
- add/normalize missing entities;
- add deterministic repair logic;
- implement extraction decomposition or any other recommended intervention;
- change representation/renderers/UI/navigation;
- create new learner-facing artifacts;
- promote product/baseline state;
- automatically prepare follow-up implementation after analysis.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
