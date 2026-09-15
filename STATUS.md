# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected four-surface model remains unchanged.

## Semantic-to-representation compiler

`SPEC-039 — semantic-to-representation compiler gate`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `SEMANTIC_REPRESENTATION_COMPILER_CONFIRMED_WITH_COVERAGE_GAPS`

## Blind extraction evidence

SPEC-040 through SPEC-046 remain accepted historical evidence.

Accepted diagnostic conclusion from SPEC-046:

`FAILURE_STAGES_MAPPED_EXTRACTION_DECOMPOSITION_NEXT`

## Candidate B v1

`SPEC-047 — decomposed extraction A/B harness`

Implementation status: `IMPLEMENTED_REVIEWED`

`SPEC-048 — decomposed extraction live A/B execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DIAGNOSIS`

Owner verdict: `CANDIDATE_B_V1_REJECTED_STAGE2_INTERFACE_FAILURE_DOMINATES`

Accepted result:

- historical Control A: 4/9 admitted;
- Candidate B v1: 2/9 admitted;
- B v1 is a regression as implemented;
- zero known-invalid admissions in both arms;
- six of seven B-v1 failures concentrated in Stage-2 proposition construction.

## Proposition diagnostics

`SPEC-049 — stage2 proposition contract diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED`

Accepted finding:

- all six exact failed proposition outputs were machine-schema expressible but canonically invalid;
- 1 was purely structurally preventable;
- 5 mixed structural + semantic mismatches required further diagnosis.

`SPEC-050 — proposition semantic coverage diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `NO_ONTOLOGY_GAP_SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION_APPROVED`

Accepted findings:

- 4 mixed cases are `CLAIM_ONLY_FIT`;
- 1 is `EXISTING_RELATIONSHIP_FIT`;
- 0 are `TRUE_SEMANTIC_COVERAGE_GAP`;
- NHGRI structural-only control remains a canonical proposition fit;
- no proposition/predicate expansion is justified;
- not every true statement deserves topology;
- Stage 2 should omit source-supported meaning that does not truthfully fit canonical topology, while Stage 3 preserves it as grounded claim material;
- proposition subtype schemas should encode canonical shape directly.

Canonical SPEC-050 evidence:

`examples/evaluations/spec-050-proposition-semantic-coverage-diagnosis-20260914/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-051 is implemented and awaiting owner review. Candidate B v2 is frozen as
`spec-051-candidate-b-v2` with exactly two evidence-backed changes:

1. subtype-discriminated Stage-2 proposition arrays aligned to the unchanged canonical contracts;
2. generic Stage-2 semantic omission with independent Stage-3 grounded claim preservation.

Canonical evidence:

`examples/evaluations/spec-051-schema-constrained-candidate-b-v2-20260915/report.json`

All six historical failed source outputs are rejected at the v2 interface; the offline claim-only and relationship-preservation fixtures pass. Control A and B v1 remain frozen historical arms.

No packet is active. The proposed later nine-source manifest retains a 27-call ceiling, but those calls, blind-corpus execution, ontology expansion, production promotion, and further changes are not authorized.

## Current product question

```text
Candidate B v1 failure diagnosis
        ↓
SPEC-051 Candidate B v2 frozen offline
        ↓
canonical subtype arrays + generic omission
        ↓
Stage 3 preserves independent exact grounded claims
        ↓
zero provider calls; no blind execution
        ↓
OWNER REVIEW before live execution
```

The immediate goal is owner review of the frozen v2 contract, not live execution or promotion.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 Control-A implementation/frozen identity;
- SPEC-041/042/044/045 blind source packets, manifests, raw responses, run histories, and evidence;
- SPEC-043 taxonomy/classifications;
- SPEC-046 failure-stage analysis;
- SPEC-047 Candidate-B-v1 implementation, prompts, schemas, harness, fixtures, and evidence;
- SPEC-048 B-v1 live evidence, ledger, comparison, and taxonomy audit;
- SPEC-049 proposition contract diagnosis;
- SPEC-050 semantic coverage diagnosis;
- trusted semantic vocabulary;
- canonical proposition types and semantics;
- canonical grounding/provenance behavior;
- strict declared-identity validation;
- canonical proposition/KnowledgeModel validators;
- structure detection;
- representation strategy/renderers;
- navigation/UI behavior;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external evidence retrieval;
- execute B v2 on blind sources;
- rerun Control A or B v1;
- edit B-v1 historical behavior/evidence;
- add proposition types or trusted predicates;
- reinterpret canonical proposition semantics;
- weaken/change canonical validation;
- add deterministic semantic repair;
- add source-specific production rules/examples;
- force standalone comparisons into topology;
- alter structure detection to consume claims;
- change representation/renderers/UI/navigation;
- promote B v2;
- authorize future live execution automatically.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
