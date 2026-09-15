# SPEC-051 — Schema-Constrained Candidate B v2

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Implement and freeze Candidate B v2 offline by making exactly two evidence-backed changes to Candidate B v1:

1. make Stage-2 typed propositions structurally discriminated so canonically invalid proposition combinations are not expressible by the model-facing schema; and
2. make semantic omission explicit: source-supported meaning that does not truthfully fit an existing canonical relationship or proposition must not be forced into topology and must remain available for Stage-3 grounded claim preservation.

This packet does **not** authorize model/provider calls or blind-corpus execution. It builds and freezes Candidate B v2 for later owner review and separately authorized live evaluation.

## Owner verdict entering this packet

SPEC-050 owner verdict:

`NO_ONTOLOGY_GAP_SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION_APPROVED`

Accepted evidence:

- Candidate B v1 regressed to 2/9 admission versus historical Control A's 4/9;
- 6/7 Candidate-B-v1 failures concentrated in Stage-2 proposition construction;
- SPEC-049 showed all six exact failed proposition outputs were expressible by the broad v1 schema but canonically invalid;
- SPEC-050 showed the five mixed semantic cases do not demonstrate ontology gaps:
  - 4 are `CLAIM_ONLY_FIT`;
  - 1 is `EXISTING_RELATIONSHIP_FIT`;
  - 0 are `TRUE_SEMANTIC_COVERAGE_GAP`;
- a source-supported statement does not require topology merely because it is comparative or relational in ordinary language;
- strict deterministic validation and fail-closed behavior remain protected.

## Core principles

### 1. Not every true statement deserves topology

A source-supported statement may remain a grounded claim when no existing canonical relationship/proposition truthfully captures it.

Do not invent topology to avoid omission.

### 2. Invalid proposition states should be hard or impossible to express

The model-facing Stage-2 schema should encode the canonical proposition subtype structure as directly as the provider/schema mechanism allows.

### 3. Omission is not information loss when Stage 3 preserves the meaning

Stage 2 may omit non-topological meaning. Stage 3 must remain capable of preserving exact grounded claims independently of Stage-2 topology.

### 4. Trust boundary remains unchanged

Candidate B v2 may reduce invalid proposals reaching validation, but canonical validation remains authoritative and unchanged.

## Candidate lineage

Control A remains frozen historical single-pass behavior.

Candidate B v1 remains preserved historical experimental evidence and must not be edited in place.

Candidate B v2 must have a distinct implementation/version identity, e.g.:

`spec-051-candidate-b-v2`

Implement v2 as a new version/seam or clearly versioned behavior so v1 evidence remains reproducible.

## Architecture retained

Keep the three-stage decomposition:

```text
SOURCE
   ↓
STAGE 1 — ENTITY INVENTORY
   ↓ deterministic validation / freeze
FROZEN ENTITY SET
   ↓
STAGE 2 — SEMANTIC STRUCTURE v2
   ↓ deterministic validation / freeze
CANONICAL RELATIONSHIPS + CANONICAL TYPED PROPOSITIONS
   ↓
STAGE 3 — CLAIM / EVIDENCE BINDING
   ↓ exact grounding
EXISTING canonical KnowledgeModel validation
   ↓
trusted KnowledgeModel or fail closed
```

Do not add more model stages in SPEC-051.

## Change A — subtype-discriminated Stage-2 proposition schema

Candidate B v1 exposed one broad proposition object with globally legal fields/values whose combinations were often canonically illegal.

Candidate B v2 must expose proposition alternatives that encode the two existing canonical variants separately.

### Canonical `COMPARISON_CONDITION`

The model-facing representation must encode, as strongly as supported:

- proposition type fixed to `COMPARISON_CONDITION`;
- relationship type fixed to `CAUSES`;
- comparison operator fixed to `GREATER_THAN`;
- exactly these semantic roles:
  - `LEFT_OPERAND`;
  - `RIGHT_OPERAND`;
  - `OUTCOME`;
- no additional proposition roles;
- all role entity IDs constrained to the exact frozen Stage-1 inventory;
- left and right operand identities must be distinct under deterministic validation;
- no inferred standalone comparison may be represented as this proposition merely because it uses comparative language.

Prefer a discriminated union / `oneOf`-style or equivalent schema construction if supported by the provider structured-output contract. If the provider schema mechanism cannot express a required invariant, encode the strongest valid schema and preserve the remaining invariant in deterministic validation. Document the boundary explicitly.

### Canonical `TRANSFER_EVENT`

The model-facing representation must encode, as strongly as supported:

- proposition type fixed to `TRANSFER_EVENT`;
- relationship type fixed to `TRANSFERS_TO`;
- comparison operator fixed/null according to canonical contract;
- exactly these semantic roles:
  - `EVENT`;
  - `OBJECT`;
  - `DESTINATION`;
- no additional proposition roles;
- all role entity IDs constrained to the exact frozen Stage-1 inventory;
- canonical entity-type constraints (including EVENT-as-PROCESS and destination restrictions) remain deterministically enforced if they cannot be fully encoded in provider schema;
- no generic input-to-process relationship may be forced into a transfer event when the canonical endpoint semantics do not fit.

### No proposition expansion

Do not add:

- standalone comparison proposition;
- scalar ordering proposition;
- new transfer variants;
- new proposition types;
- new trusted predicates.

SPEC-050 found no demonstrated coverage gap.

## Change B — semantic omission in Stage 2

Stage-2 v2 instructions and contract must make the following behavior explicit:

> Emit a relationship or typed proposition only when the exact source-supported meaning fits an existing canonical contract. Otherwise omit that meaning from Stage-2 topology. Do not approximate, coerce, or choose the nearest relationship/proposition type.

Examples of categories that should be omitted from topology when no canonical fit exists include:

- standalone numeric/scalar comparisons without a canonical causal outcome;
- descriptive contrasts between actors/scales without a trusted predicate;
- source-supported statements whose exact meaning is explanatory but not topological.

Do **not** embed the five historical blind answers or source-specific examples in the production prompt.

The production instruction must remain generic.

### Missing-symbol diagnostics

Preserve `missing_symbols` only for cases where a semantically valid canonical relationship/proposition cannot be expressed because the Stage-1 inventory lacks a required identity.

Do not misuse `missing_symbols` for statements intentionally omitted because no canonical topology fits.

If useful, add a separate deterministic/model-output diagnostic field such as `omitted_semantics` only if it is generic, non-authoritative, does not become trusted topology, and does not complicate Stage 3. Prefer the smallest design. It is acceptable for Stage 2 simply to omit such statements if Stage 3 independently sees the source.

## Stage 3 claim preservation invariant

Stage 3 already receives the exact source and frozen semantic structure. Candidate B v2 must preserve or strengthen the invariant that Stage 3 can emit grounded claims that are not represented by Stage-2 relationships/propositions.

Offline tests must prove:

- a source-supported standalone comparison omitted by Stage 2 can still become an exact grounded claim in Stage 3;
- that claim does not silently create topology;
- structure detection remains driven by canonical semantic structure, not claim-only material;
- assertion-aware/explanatory representation can still preserve the claim as explanatory content under existing behavior.

Do not change representation strategy or structure detection in this packet.

## Stage 1

Do not redesign Stage 1 based on the single NASA duplicate-entity failure in SPEC-048.

Candidate B v2 may inherit Candidate-B-v1 Stage-1 behavior unchanged unless a purely versioning/integration change is required.

The purpose of SPEC-051 is Stage-2 proposition interface + semantic omission, not broad extraction cleanup.

## Deterministic validation

Canonical validators remain unchanged.

Candidate-specific prevalidation may enforce v2 schema/stage invariants before canonical validation, but must not:

- repair outputs;
- infer missing roles;
- substitute predicates;
- normalize semantically invalid objects into valid ones;
- create missing entities;
- turn omitted claims into topology.

Invalid output fails closed.

## Offline counterfactual regression fixtures

Use synthetic/local fixtures and preserved historical objects for **validation of the interface**, not for tuning source-specific production behavior.

At minimum prove:

1. the six exact SPEC-048 failed proposition objects are rejected by the v2 Stage-2 contract before canonical validation;
2. valid canonical `COMPARISON_CONDITION` remains expressible/admissible;
3. valid canonical `TRANSFER_EVENT` remains expressible/admissible;
4. standalone comparison can be omitted from Stage 2 and preserved as Stage-3 claim;
5. existing-relationship fit can be represented as the relationship without coercing it into a proposition;
6. Stage 2 cannot add entities or reference undeclared IDs;
7. Stage 3 cannot alter Stage-2 topology;
8. exact evidence mismatch still fails closed;
9. upstream failure still short-circuits downstream model stages;
10. canonical validators remain byte/behavior unchanged.

Historical failed objects may be replayed mechanically against the v2 contract. Do not put their source-specific answers into production prompts.

## Future evaluation design

Freeze a proposed later live manifest but do not execute it.

The later Candidate-B-v2 evaluation should use the same nine frozen blind source passages from SPEC-041 + SPEC-044, in the same fixed order.

Control A remains historical.

Candidate B v1 remains historical.

The later comparison should therefore report three arms descriptively:

```text
Control A historical
Candidate B v1 historical
Candidate B v2 future
```

Primary comparison for the v2 hypothesis:

- B v2 vs B v1 on admission/failure concentration/cost;
- B v2 vs Control A on overall viability.

Preserve the caveat that these are non-contemporaneous stochastic runs.

## Proposed future call budget

Same three-stage ceiling:

`9 sources × up to 3 stages = 27 maximum provider calls`

Short-circuit remains mandatory.

SPEC-051 authorizes **zero** provider/model calls.

## Frozen future metrics

At minimum preserve:

- source admission rate;
- known-invalid-object admission;
- stage failure distribution;
- SPEC-046 origin-stage distribution where applicable;
- proposition-construction failure count;
- semantic omission/claim-preservation evidence where observable;
- entity/relationship/proposition/claim counts;
- detected structures and representation decisions;
- provider calls;
- tokens;
- latency;
- available cost evidence;
- semantic richness guard.

A v2 pass-rate increase is not sufficient if it merely drops useful source meaning. Claim preservation must be audited.

## Future decision framework

Freeze these owner-review branches for the later live experiment:

### `B_V2_RECOVERS_DECOMPOSITION`

V2 materially improves over B v1, preserves zero known-invalid admission, substantially removes the Stage-2 proposition failure concentration, preserves source-supported omitted meaning as claims, and is competitive enough with Control A to justify continued decomposition work.

### `B_V2_STRUCTURAL_FIX_ONLY`

V2 removes malformed proposition failures but does not materially improve end-to-end admission/usefulness enough to justify the decomposition cost.

### `B_V2_TOO_SPARSE`

V2 gains admission by omitting materially useful semantics that are not adequately preserved as grounded claims.

### `B_V2_REGRESSION`

V2 worsens reliability, trust containment, or semantic preservation.

### `INCONCLUSIVE`

Evidence remains too stochastic or mixed for a decision.

No automatic promotion threshold.

## Required artifacts

Create:

`examples/evaluations/spec-051-schema-constrained-candidate-b-v2-20260915/`

Include at minimum:

- `report.json`;
- Candidate-B-v2 contract/version identity;
- stage prompt/schema identities and SHA-256 hashes;
- implementation hashes;
- offline fixture results;
- historical failed-object replay results;
- proposed future live-execution manifest with exact nine source hashes/order, model, 27-call ceiling, `store=False`, zero retries, and short-circuit rules;
- frozen comparison metrics/decision framework.

## Protected state

Do not modify:

- Control A;
- Candidate B v1 implementation or evidence;
- SPEC-038 learner-facing baseline;
- canonical semantic vocabulary;
- canonical proposition types/semantics;
- canonical validators;
- grounding/provenance behavior;
- structure detection;
- representation strategy/renderers;
- navigation/UI;
- historical blind evidence.

## No live authority

Provider/model calls: `0`.

External evidence retrieval: `0`.

Blind-corpus Candidate-B-v2 execution: `0`.

Do not test prompts against a provider.

## Validation

At minimum:

- focused v2 schema/stage tests;
- six-object historical replay test;
- claim-preservation fixture tests;
- v1 regression tests;
- Control-A regression tests;
- canonical proposition/validator tests;
- control-plane tests;
- full offline suite;
- deterministic artifact regeneration;
- JSON validation;
- secret-safety checks;
- `git diff --check`;
- verify zero provider/model/network calls;
- verify all protected historical evidence and implementation hashes unchanged.

## Explicitly forbidden

Do not:

- call a model/provider;
- run v2 on the blind corpus;
- rerun Control A or B v1;
- add proposition types or predicates;
- change canonical proposition semantics;
- weaken validation;
- add deterministic semantic repair;
- add source-specific production rules/examples;
- force standalone comparisons into topology;
- alter structure detection to consume claims;
- alter representation/UI behavior;
- promote Candidate B v2;
- authorize the future live run automatically.

## Completion state

On completion:

- set SPEC-051 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report Candidate-B-v2 identity/hashes, tests, replay result, future call ceiling, and zero-call confirmation;
- stop at `OWNER_REVIEW`.

## Owner review question

> Is Candidate B v2 now a clean test of decomposition itself — with canonically shaped proposition interfaces and explicit semantic omission/claim preservation — such that another bounded nine-source live evaluation is justified?
