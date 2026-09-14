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

## Blind extraction evidence

SPEC-040 through SPEC-046 remain accepted historical evidence.

Accepted diagnostic conclusion from SPEC-046:

`FAILURE_STAGES_MAPPED_EXTRACTION_DECOMPOSITION_NEXT`

## Decomposed extraction Candidate B v1

`SPEC-047 — decomposed extraction A/B harness`

Implementation status: `IMPLEMENTED_REVIEWED`

`SPEC-048 — decomposed extraction live A/B execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DIAGNOSIS`

Owner verdict: `CANDIDATE_B_V1_REJECTED_STAGE2_INTERFACE_FAILURE_DOMINATES`

Accepted SPEC-048 findings:

- Candidate B v1 regressed versus historical Control A: 2/9 admitted vs 4/9;
- Candidate B used more calls/tokens while preserving zero known-invalid admissions;
- 6 of 7 Candidate-B failures originated in Stage-2 `PROPOSITION_CONSTRUCTION`;
- the concentration warranted proposition-interface diagnosis before abandoning decomposition entirely.

## Stage-2 proposition contract diagnosis

`SPEC-049 — stage2 proposition contract diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_FOLLOWUP_DIAGNOSIS`

Owner interpretation: `MIXED_SIGNAL_MORE_DIAGNOSIS_REQUIRED`

Accepted objective findings:

- all six exact failed Stage-2 outputs were expressible under Candidate-B-v1's broad machine-readable proposition schema;
- a stricter subtype-specific interface could reject all six before canonical validation while preserving valid canonical proposition variants;
- 1 failure is `STRUCTURALLY_PREVENTABLE` only;
- 5 failures are `BOTH_STRUCTURE_AND_SEMANTICS`;
- four mixed cases involve source-supported standalone comparisons that do not fit canonical causal `COMPARISON_CONDITION` semantics;
- at least one mixed transfer case conflicts with canonical `TRANSFER_EVENT` role semantics;
- schema tightening alone is therefore insufficient evidence for Candidate B v2;
- no semantic-model expansion is yet justified.

Canonical evidence:

`examples/evaluations/spec-049-stage2-proposition-contract-diagnosis-20260914/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-050 is implemented and awaiting owner review. Its canonical report is:

`examples/evaluations/spec-050-proposition-semantic-coverage-diagnosis-20260914/report.json`

Objective destination findings:

- 4 cases are `CLAIM_ONLY_FIT`;
- 1 case is `EXISTING_RELATIONSHIP_FIT`;
- 0 cases are `TRUE_SEMANTIC_COVERAGE_GAP` or `AMBIGUOUS`;
- the structural-only control remains a canonical `TRANSFER_EVENT` fit.

Recommended branch: `SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION`.

No packet is active. No provider/model call, production change, Candidate-B-v2 implementation, semantic expansion, or promotion is authorized.

## Current product question

```text
5 source-supported mixed proposition failures
        ↓
4 grounded-claim fits + 1 existing-relationship fit
        ↓
0 demonstrated semantic-model coverage gaps
        ↓
SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION
        ↓
OWNER REVIEW
```

The immediate goal is owner review of the diagnosis, not Candidate-B-v2 implementation or ontology expansion.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 Control-A implementation/frozen identity;
- SPEC-041/042/044/045 source packets, manifests, raw responses, run histories, and evidence;
- SPEC-043 taxonomy and historical classifications;
- SPEC-046 failure-stage analysis;
- SPEC-047 Candidate-B-v1 implementation, prompts, schemas, contracts, harness, fixtures, and evidence;
- SPEC-048 raw provider outputs, ledger, stage gates, A/B comparison, final report, and taxonomy audit;
- SPEC-049 diagnostic contract analysis and preserved canonical proposition semantics;
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
- edit Candidate-B-v1 prompts/schemas;
- add proposition types or trusted predicates;
- reinterpret canonical proposition semantics;
- change canonical validation;
- repair preserved outputs;
- force claims into graph topology;
- weaken trust-boundary behavior;
- change representation/renderers/UI/navigation;
- promote any extractor or baseline;
- automatically implement the recommended next branch.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
