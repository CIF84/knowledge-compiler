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

Frozen single-pass Control-A identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Blind reliability evidence

SPEC-042 through SPEC-046 remain accepted historical evidence.

Accepted diagnostic verdict from SPEC-046:

`FAILURE_STAGES_MAPPED_EXTRACTION_DECOMPOSITION_NEXT`

## Decomposed extraction Candidate B v1

`SPEC-047 — decomposed extraction A/B harness`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `CANDIDATE_B_FROZEN_LIVE_AB_EXECUTION_APPROVED`

`SPEC-048 — decomposed extraction live A/B execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DIAGNOSIS`

Owner verdict: `CANDIDATE_B_V1_REJECTED_STAGE2_INTERFACE_FAILURE_DOMINATES`

Accepted SPEC-048 findings:

- historical Control A admitted 4/9 sources in 9 calls;
- Candidate B v1 admitted 2/9 sources in 19 calls;
- Candidate B used 94,574 total tokens versus historical Control A's 54,586;
- both arms admitted zero known-invalid objects;
- Candidate B v1 mechanically satisfies `B_REGRESSION`;
- seven Candidate-B sources failed closed;
- six failures originate in `PROPOSITION_CONSTRUCTION` at Stage 2;
- one failure originates in `ENTITY_INVENTORY`;
- the six Stage-2 failures are sufficiently concentrated to diagnose the intermediate proposition interface before rejecting decomposition as a whole.

Canonical SPEC-048 evidence:

`examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/final-report.json`

Authoritative taxonomy correction:

`examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/post-run-failure-taxonomy-audit.json`

## Current approved work packet

```text
specs/SPEC-049-stage2-proposition-contract-diagnosis.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-049 is authorized to diagnose whether the six concentrated Stage-2 proposition failures arose because Candidate B v1 exposed structurally invalid proposition states in its machine-readable schema/interface.

It must reconstruct the pre-existing canonical contracts for `COMPARISON_CONDITION` and `TRANSFER_EVENT`, distinguish schema/prompt/validator enforcement, replay the six preserved failures offline against a diagnostic discriminated contract where feasible, and determine whether a narrowly schema-constrained Candidate-B-v2 experiment is justified.

No production behavior change is authorized.

No provider/model/network call is authorized.

## Current product question

```text
Candidate B v1 regression
        ↓
6/7 failures concentrated in Stage-2 proposition construction
        ↓
inspect proposition interface
        ↓
were invalid combinations structurally expressible?
        ↓
can pre-existing canonical rules make them impossible at schema level?
        ↓
OWNER REVIEW
```

The goal is diagnosis, not improving Candidate B in this packet.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 Control-A implementation/frozen identity;
- SPEC-041/042/044/045 source packets, manifests, raw responses, run histories, and evidence;
- SPEC-043 taxonomy and historical classifications;
- SPEC-046 failure-stage analysis;
- SPEC-047 Candidate-B-v1 implementation, prompts, schemas, stage contracts, harness, fixtures, and evidence;
- SPEC-048 raw provider outputs, provider ledger, stage gates, comparison results, final report, and authoritative post-run taxonomy audit;
- trusted semantic vocabulary;
- canonical grounding/provenance behavior;
- strict declared-identity validation;
- canonical proposition and KnowledgeModel validation;
- representation strategy logic and renderer coverage;
- navigation/UI behavior;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external web/network retrieval;
- rerun Control A or Candidate B;
- implement Candidate B v2;
- edit Candidate-B-v1 production prompt/schema;
- change canonical proposition validation;
- repair preserved outputs;
- weaken trust-boundary behavior;
- add proposition types or trusted predicates;
- add source-specific exceptions;
- change representation/renderers/UI/navigation;
- promote any extractor;
- automatically prepare follow-up implementation after diagnosis.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
