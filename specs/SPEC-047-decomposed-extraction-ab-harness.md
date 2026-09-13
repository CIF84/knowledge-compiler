# SPEC-047 — Decomposed Extraction A/B Harness

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Implement and freeze a decomposed extraction candidate and an A/B evaluation harness that can later compare it against the existing single-pass `spec-010-v1` extractor on the same frozen blind corpus.

This packet is **implementation without live execution**. It may create the decomposed extraction architecture, prompts/schemas for its stages, deterministic stage boundaries, instrumentation, and the comparison harness. It must not transmit any blind source to a model/provider.

A later packet will separately authorize the exact A/B model calls after the implementation and experiment contract are frozen and owner-reviewed.

## Owner verdict entering this packet

SPEC-046 owner verdict:

`FAILURE_STAGES_MAPPED_EXTRACTION_DECOMPOSITION_NEXT`

Accepted evidence:

- nine blind sources yielded extraction reliability of 4/9;
- all 7 known invalid/malformed semantic objects were contained by the trusted boundary;
- origin stages: 3 `ENTITY_INVENTORY`, 2 `RELATIONSHIP_SEMANTICS`, 1 `PROPOSITION_CONSTRUCTION`, 1 `EVIDENCE_FIDELITY`;
- `ENTITY_INVENTORY` is the only origin stage recurring across unrelated domains;
- failures remain heterogeneous overall;
- the next experiment should test whether explicit staged extraction improves reliability without weakening deterministic admission.

## Core hypothesis

> Freezing a validated entity inventory before asking the model to construct relationships/propositions/evidence will reduce cross-reference and semantic-composition failures because later stages are constrained to already-declared identities, while deterministic validation remains unchanged.

The experiment is not “more calls are better.”

The experiment is:

> **Do explicit validated intermediate contracts reduce extraction errors enough to justify their added latency/token/call cost?**

## A/B architecture

### Control A — existing single-pass extractor

Control A remains exactly the frozen behavior used in SPEC-042/SPEC-045:

```text
SOURCE
   ↓
spec-010-v1 single-pass extraction
   ↓
entities + relationships + propositions + claims/evidence
   ↓
existing deterministic grounding + canonical validation
   ↓
trusted KnowledgeModel or fail closed
```

Do not modify Control A.

### Candidate B — decomposed extractor

Implement the smallest staged architecture that directly tests SPEC-046's hypothesis:

```text
SOURCE
   ↓
STAGE 1 — ENTITY INVENTORY
   ↓ deterministic validation / freeze
FROZEN DECLARED ENTITY SET
   ↓
STAGE 2 — SEMANTIC STRUCTURE
   ↓ deterministic validation against frozen entity IDs
RELATIONSHIPS + TYPED PROPOSITIONS
   ↓
STAGE 3 — CLAIM / EVIDENCE BINDING
   ↓ deterministic exact-evidence grounding
CANDIDATE EXTRACTION RESULT
   ↓
EXISTING canonical KnowledgeModel validation
   ↓
trusted KnowledgeModel or fail closed
```

Three stages are the default experimental design. Do not add stages merely for architectural elegance.

## Stage 1 — Entity Inventory

Stage 1 may propose only entity declarations needed to represent source-supported knowledge.

Each entity must contain the minimum fields required by the existing semantic model, including stable ID, label/name, type, and source grounding/evidence as required by current contracts.

Requirements:

- IDs are frozen after Stage 1 validation;
- later stages may reference only these IDs;
- later stages may not invent new IDs;
- no deterministic aliasing/repair of missing IDs;
- duplicate/conflicting entity declarations fail according to explicit deterministic rules;
- entity evidence must remain source-bounded.

If Stage 1 fails, Candidate B fails closed for that source. Do not call later stages.

## Stage 2 — Semantic Structure

Stage 2 receives:

- exact source text;
- validated frozen entity inventory;
- existing trusted relationship/proposition vocabulary and schema constraints.

It may emit only:

- relationships between frozen entity IDs;
- typed propositions whose role bindings use frozen entity IDs.

Requirements:

- unknown IDs are structurally impossible or deterministically rejected before canonical admission;
- relationship direction/predicate semantics remain subject to existing validation;
- proposition roles/comparison semantics remain subject to existing validation;
- no new entity declaration is allowed in this stage;
- no semantic repair is allowed.

If Stage 2 fails, Candidate B fails closed for that source. Do not call Stage 3.

## Stage 3 — Claim / Evidence Binding

Stage 3 receives:

- exact source text;
- frozen entities;
- validated Stage 2 semantic structure.

Its purpose is to bind learner-useful claims/explanatory statements and exact source evidence without altering semantic identity or topology.

Requirements:

- evidence quotes must satisfy the existing exact-source grounding contract;
- Stage 3 cannot add entities, relationships, propositions, predicates, or role bindings;
- it cannot repair Stage 1/2 output;
- unsupported or non-exact evidence fails closed according to explicit deterministic rules.

If existing architecture makes claims/evidence inseparable from earlier grounding, implement the narrowest compatible seam that preserves the experimental principle. Record any necessary deviation for owner review rather than broadening scope.

## Deterministic stage gates

Each stage must have a machine-inspectable gate result:

- `PASS`
- `FAIL_CLOSED`
- `NOT_RUN_UPSTREAM_FAILURE`

Record exact deterministic rejection reason.

No model self-critique or model-based validation is allowed between stages.

The trusted boundary remains deterministic.

## Prompt design constraints

Candidate B requires new stage-specific prompts/schemas. These are part of the experimental candidate and must be frozen by this packet before any blind execution.

Prompt principles:

- one job per stage;
- explicitly prohibit responsibilities belonging to later stages;
- Stage 2 must receive the exact frozen entity inventory and be instructed to reference only supplied IDs;
- Stage 3 must receive frozen semantic structure and be instructed not to change it;
- exact evidence requirements must be explicit;
- use the same model family intended for the later comparison unless a later owner decision explicitly changes model selection.

Do not tune prompts against the blind source outputs from SPEC-042/SPEC-045.

Historical blind failures may be used to define failure categories and invariants, but not as source-specific few-shot answers or prompt examples.

## Corpus for later A/B execution

The later experiment should use the **same nine frozen blind passages** from SPEC-041 and SPEC-044.

Why:

- Control A outcomes are already preserved for all nine sources;
- no new Control A calls are scientifically necessary if the later comparison contract accepts the immutable historical runs;
- Candidate B can be executed once per staged source under separately bounded authority;
- this avoids paying for/reintroducing stochastic variation into the established control unless owner review later decides paired contemporaneous reruns are necessary.

SPEC-047 must freeze the proposed comparison design but must not execute Candidate B.

## Proposed later call budget

Because Candidate B has up to three stages per source, proposed maximum future calls are:

```text
9 sources × up to 3 calls = 27 maximum Candidate-B calls
```

But calls must short-circuit after a failed stage:

- Stage 1 failure → 1 call total for that source;
- Stage 2 failure → 2 calls total;
- Stage 3 reached → 3 calls total.

SPEC-047 does **not** authorize these calls.

The frozen future manifest must record 27 as a ceiling, not an expected call count.

## Comparison metrics

Freeze the later A/B metrics now, before Candidate-B results exist.

### Primary metrics

1. **Source admission rate**
   - Control A: trusted KnowledgeModel admitted / 9.
   - Candidate B: trusted KnowledgeModel admitted / 9.

2. **Trust-boundary containment**
   - known invalid/malformed candidate objects admitted: target remains `0`.

3. **Failure-origin distribution**
   - use SPEC-046 origin-stage taxonomy for Candidate B failures where applicable.

### Secondary metrics

4. entity-inventory consistency / undeclared-reference failures;
5. relationship/proposition semantic rejection count;
6. evidence-fidelity rejection count;
7. admitted entity/relationship/proposition counts;
8. detected structure counts/types;
9. representation strategy counts/sufficiency;
10. provider calls per source;
11. input/output/total tokens per admitted source and per attempted source;
12. end-to-end provider latency per source;
13. available monetary cost evidence, without inventing prices when unavailable.

## Decision framework

Freeze the later owner decision framework:

### `B_CLEAR_IMPROVEMENT`

Candidate B materially improves admission/reliability, preserves zero known-invalid admission, and the improvement is not explained solely by weaker semantics or dramatically emptier output. Added cost/latency is measurable and reviewable.

### `B_SAFER_BUT_TOO_SPARSE`

Candidate B admits more sources primarily by emitting materially less semantic structure, making the apparent reliability improvement questionable.

### `B_NO_MATERIAL_GAIN`

Candidate B does not materially improve reliability enough to justify decomposition complexity/cost.

### `B_REGRESSION`

Candidate B reduces admission, weakens semantic richness materially, violates trust-boundary containment, or introduces new systematic failure modes.

### `INCONCLUSIVE`

Evidence cannot distinguish the above without another experiment.

Do not encode an automatic promotion threshold based solely on source count. Owner review remains required.

## Semantic richness guard

A higher pass rate is not automatically better.

For every source admitted by either arm, the later report must compare semantic richness mechanically:

- entity count;
- relationship count;
- proposition count;
- detected structures;
- representation decisions with sufficient trusted structure.

Candidate B must not be credited for “improvement” merely because it emits a nearly empty graph that passes validation.

## Control comparability

Create a deterministic adapter that can transform preserved SPEC-042/SPEC-045 Control-A evidence into the same comparison-record schema used for Candidate B.

Do not alter historical Control-A outcomes.

Record that Control A uses historical frozen runs while Candidate B will be a future run. This is a limitation: model stochasticity/time drift is not controlled by contemporaneous paired calls.

The later owner may decide whether the observed effect is large enough despite this limitation or whether paired reruns are warranted.

## Instrumentation requirements

Candidate B must record per stage:

- source ID/hash;
- stage name/version;
- prompt/schema identity/hash;
- provider request/response IDs when later executed;
- input/output/total tokens;
- latency;
- raw provider response;
- parsed proposal;
- deterministic gate status;
- exact gate failure;
- frozen upstream input identity/hash;
- whether downstream stages ran.

The future execution harness must count provider calls when a request starts, not only when an adapter returns, addressing the observability limitation documented in SPEC-045 without modifying historical evidence.

## Offline fixture testing

SPEC-047 may create synthetic/local deterministic fixtures to test stage contracts and orchestration.

Fixtures should prove at minimum:

- Stage 2 cannot reference undeclared IDs;
- Stage 2 cannot add entities;
- Stage 3 cannot alter semantic structure;
- exact evidence mismatch fails closed;
- upstream failure prevents downstream stage execution;
- call accounting occurs at request start;
- canonical validator remains unchanged;
- same valid semantic content can flow through Candidate B into the existing downstream structure detector and representation compiler.

Do not use the nine blind source texts to manually craft successful Candidate-B answers.

## Implementation boundaries

Allowed:

- new decomposed-extractor module(s);
- stage-specific prompt/schema definitions;
- deterministic stage validators/adapters;
- Candidate-B orchestration;
- A/B comparison-record schema/harness;
- offline fixtures/tests;
- proposed future live-execution manifest;
- documentation/evaluation artifacts.

Not allowed:

- modifying Control A behavior;
- weakening canonical validation;
- changing trusted semantic vocabulary;
- changing representation strategy logic;
- changing SPEC-038 UI;
- live execution.

## Required artifact

Create:

`examples/evaluations/spec-047-decomposed-extraction-ab-harness-20260913/`

Include at minimum:

- `report.json`;
- frozen Candidate-B stage prompt/schema identities and hashes;
- proposed future live-execution manifest containing the nine source hashes, fixed order, model, per-stage call rules, 27-call ceiling, zero retry policy, and `store=False`;
- comparison schema/metric definitions;
- offline fixture results;
- implementation file hashes sufficient to freeze Candidate B for later execution.

## No live authority

`OFFLINE_ONLY` is strict.

Provider/model calls: `0`.

External source retrieval: `0`.

Do not test prompts by calling a model.

If implementation cannot be validated without a model call, stop and report the boundary.

## Future execution policy to freeze

The proposed later manifest must specify:

- exact nine source IDs/hashes from SPEC-041 + SPEC-044;
- fixed source order independent of historical outcome;
- model `gpt-5.6-luna` unless owner changes this before execution authorization;
- Stage 1 → Stage 2 → Stage 3 order;
- maximum one call per stage per source;
- short-circuit on failed stage;
- `store=False`;
- SDK retries `0`;
- hidden retries `0`;
- semantic retries `0`;
- repair calls `0`;
- follow-up calls outside the defined stages `0`;
- no external enrichment;
- no prompt adaptation between sources;
- no implementation adaptation after source execution begins;
- preserve failures exactly.

## Validation

At minimum:

- focused Candidate-B stage/orchestration tests;
- comparison-harness tests;
- control-plane tests;
- full offline suite;
- deterministic regeneration of SPEC-047 artifacts;
- JSON validation;
- secret-safety checks;
- `git diff --check`;
- verify zero provider/model/network calls;
- verify SPEC-038 through SPEC-046 protected evidence/behavior unchanged;
- verify Control A implementation hashes unchanged;
- verify canonical validator hashes/behavior unchanged.

## Explicitly forbidden

Do not:

- execute Candidate B against a provider/model;
- rerun Control A;
- retrieve new sources;
- tune Candidate B against observed blind outputs;
- include historical failed-source answers as prompt examples;
- add deterministic semantic repair;
- normalize undeclared IDs automatically;
- loosen evidence exactness;
- weaken fail-closed behavior;
- change model in Control A;
- change semantic vocabulary;
- change representation/renderers/UI/navigation;
- promote Candidate B;
- automatically authorize the future 27-call run.

## Completion state

On completion:

- set SPEC-047 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report implementation identity/hashes, tests, proposed future call ceiling, and zero-call confirmation;
- stop at `OWNER_REVIEW`.

## Owner review question

> Is the decomposed extractor and A/B contract sufficiently clean, constrained, and uncontaminated to freeze Candidate B and authorize a later nine-source live comparison against the preserved single-pass control?
