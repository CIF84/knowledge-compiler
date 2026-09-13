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

## Extraction reliability failure-mode analysis

`SPEC-046 — extraction reliability failure-mode analysis`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Owner verdict: `PENDING`

Recorded objective result:

- all nine blind source outcomes and seven rejected objects reconcile with immutable SPEC-042 through SPEC-045 evidence;
- failure origins span four stages: 3 `ENTITY_INVENTORY`, 2 `RELATIONSHIP_SEMANTICS`, 1 `PROPOSITION_CONSTRUCTION`, and 1 `EVIDENCE_FIDELITY`;
- `ENTITY_INVENTORY` is the only origin stage recurring across unrelated domains, but no single stage is a majority of rejected objects;
- extraction reliability is 4/9 admitted sources, while the trusted boundary prevented all 7 known invalid or malformed objects from admission;
- exactly one next experiment class is recommended: `EXTRACTION_DECOMPOSITION`;
- no repair, model/provider call, semantic change, behavior change, or promotion occurred.

Canonical evidence:

`examples/evaluations/spec-046-extraction-reliability-failure-mode-analysis-20260913/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-046 is implemented and awaiting owner review. Its canonical evidence is
`examples/evaluations/spec-046-extraction-reliability-failure-mode-analysis-20260913/report.json`.

No packet is active. No provider/model call, retry, repair, semantic adaptation,
behavior change, implementation of the recommendation, or promotion is authorized.

## Current product question

```text
9 blind sources / 7 rejected objects
        ↓
4 origin stages
        ↓
ENTITY_INVENTORY is the only cross-domain recurrence
        ↓
extraction reliability 4/9
        ↓
trust-boundary containment 7/7
        ↓
OWNER REVIEW of EXTRACTION_DECOMPOSITION recommendation
```

The immediate goal is owner review of the diagnostic result and recommended experiment class, not implementation.

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
