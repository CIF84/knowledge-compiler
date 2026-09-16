# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected learner-facing architecture remains unchanged.

## Semantic-to-representation compiler

`SPEC-039 — semantic-to-representation compiler gate`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `SEMANTIC_REPRESENTATION_COMPILER_CONFIRMED_WITH_COVERAGE_GAPS`

## Blind extraction history

SPEC-040 through SPEC-046 remain accepted historical evidence.

Historical Control A: 4/9 admitted with strict fail-closed containment.

## Candidate B v1

SPEC-047/048 remain frozen historical evidence.

Owner verdict: `CANDIDATE_B_V1_REJECTED_STAGE2_INTERFACE_FAILURE_DOMINATES`

Historical B v1: 2/9 admitted, 19 calls, 94,574 tokens, zero known-invalid admission; six failures concentrated in Stage-2 proposition construction.

## Proposition diagnosis

SPEC-049/050 remain accepted diagnostic evidence.

Owner verdict from SPEC-050:

`NO_ONTOLOGY_GAP_SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION_APPROVED`

Accepted principle:

- not every true statement deserves topology;
- canonical proposition shapes should be encoded in the model-facing interface;
- source-supported non-topological meaning should be omitted from Stage-2 topology and preserved as grounded Stage-3 claims;
- no ontology expansion is justified by current evidence.

## Candidate B v2

`SPEC-051 — schema-constrained Candidate B v2`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `CANDIDATE_B_V2_FROZEN_LIVE_EVALUATION_APPROVED`

Frozen candidate version: `spec-051-candidate-b-v2`

Contract SHA-256:

`6a149b1d3bac5789652de77af2630ffea84893413e892f4606df3c718e48d148`

Accepted offline evidence:

- all eight invalid historical proposition objects rejected at v2 interface;
- valid canonical proposition variants preserved;
- claim-only omission/preservation fixture passes without added topology;
- existing-relationship fit fixture passes;
- canonical validators/structure/representation remain unchanged;
- zero model calls and zero blind executions during SPEC-051.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-052 is implemented and awaiting owner review. The single frozen Candidate B v2 run completed with:

- 8/9 admitted sources;
- 26 provider calls and 147,013 total tokens;
- zero retries, repairs, enrichment, or known-invalid admission;
- one Stage-2 `PROPOSITION_CONSTRUCTION` rejection, with correct short-circuiting;
- 152/152 parsed claims exactly grounded and admitted;
- 98 mechanically claim-only items preserved as grounded claims;
- zero unintended topology from claim-only material;
- zero dedicated claim-focus representation decisions, an explicit representation-coverage limitation.

Canonical evidence:

`examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915/final-report.json`

The mechanically supported branch remains `INCONCLUSIVE`; the product verdict and promotion remain owner-gated. No packet is active and no additional calls are authorized.

## Current product question

```text
Control A historical: 4/9
B v1 historical: 2/9 + 6 Stage-2 proposition failures
        ↓
frozen B v2 live: 8/9
1 Stage-2 proposition failure
        ↓
152 exact grounded claims admitted
98 mechanically claim-only; zero unintended topology
        ↓
no dedicated claim-focus representation decisions
        ↓
OWNER REVIEW
```

The owner must decide whether the large admission recovery justifies continued decomposition work despite higher cost and the unresolved claim-to-representation coverage limitation.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler;
- SPEC-040 Control-A implementation/evidence;
- SPEC-041/042/044/045 source packets and historical live evidence;
- SPEC-043/046 failure taxonomies/analysis;
- SPEC-047/048 Candidate-B-v1 implementation/evidence;
- SPEC-049/050 diagnostics;
- SPEC-051 Candidate-B-v2 implementation, prompts, schemas, contract, fixtures, report, and proposed manifest;
- trusted semantic vocabulary;
- canonical proposition types/semantics;
- canonical grounding/provenance and validators;
- structure detection;
- representation strategy/renderers;
- navigation/UI;
- unrelated user work.

## Explicitly forbidden

Do not:

- rerun Control A or B v1;
- exceed 27 B-v2 calls;
- retry or repair any stage;
- alter sources/order/model;
- alter B-v2 prompt/schema/implementation after execution starts;
- add source-specific rules/examples;
- add proposition types/predicates;
- reinterpret or weaken canonical semantics/validation;
- force omitted claims into topology;
- change structure detection, representation, renderers, navigation, or UI;
- retrieve external enrichment;
- promote any extractor;
- implement follow-up fixes automatically.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
