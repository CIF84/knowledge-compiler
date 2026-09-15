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
specs/SPEC-052-candidate-b-v2-live-evaluation.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-052 is authorized to execute the exact frozen Candidate B v2 once against the exact nine frozen blind passages.

Provider authority:

- OpenAI Responses API;
- model `gpt-5.6-luna`;
- `store=False`;
- maximum 27 provider calls;
- maximum one call per stage per source;
- fixed source order;
- Stage 1 → Stage 2 → Stage 3;
- mandatory upstream-failure short-circuiting;
- SDK/hidden/semantic/repair/follow-up retries/calls all zero;
- no external retrieval/enrichment;
- no prompt/schema/implementation adaptation after execution begins.

Control A and Candidate B v1 must not be rerun.

SPEC-052 must audit whether Stage-2 omitted non-topological meaning survives as exact grounded Stage-3 claims without creating topology.

## Current product question

```text
Control A historical: 4/9
B v1 historical: 2/9 + Stage-2 proposition failure concentration
        ↓
frozen B v2
canonical proposition interface + semantic omission
        ↓
9-source bounded live execution
        ↓
admission + trust containment + claim preservation
+ semantic richness + cost/latency
        ↓
OWNER REVIEW
```

The experiment asks whether B v2 recovers decomposition or whether the decomposition architecture should be abandoned.

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
