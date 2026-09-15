# SPEC-052 — Candidate B v2 Live Evaluation

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Execute the frozen `spec-051-candidate-b-v2` extractor exactly once against the same nine frozen blind passages used by the historical Control A and Candidate B v1 experiments, compare the resulting evidence against both historical arms, and stop for owner review.

This packet authorizes only Candidate B v2 live execution. It does not authorize rerunning Control A or Candidate B v1, changing Candidate B v2, repairing any result, or promoting an extractor.

## Owner approval incorporated

Owner/ChatGPT reviewed SPEC-051 and approved the frozen Candidate B v2 contract for live evaluation.

Owner verdict:

`CANDIDATE_B_V2_FROZEN_LIVE_EVALUATION_APPROVED`

Accepted rationale:

- Candidate B v2 is a distinct versioned seam; Control A and B v1 remain frozen historical arms;
- all eight invalid historical proposition objects are rejected at the v2 interface offline;
- valid canonical `COMPARISON_CONDITION` and `TRANSFER_EVENT` remain supported;
- Stage-2 omission can preserve non-topological source truth through independent Stage-3 exact grounded claims without creating topology;
- canonical validators, structure detection, representation strategy, and learner-facing baseline remain unchanged;
- zero model calls and zero blind executions occurred during SPEC-051.

## Frozen Candidate B v2 identity

Candidate version:

`spec-051-candidate-b-v2`

Contract SHA-256:

`6a149b1d3bac5789652de77af2630ffea84893413e892f4606df3c718e48d148`

Frozen implementation files:

- `src/knowledge_compiler/decomposed_extraction_v2.py`
  - SHA-256 `0d6676676fa69aaf55d3b3f974bbbbaf02d1f30d0568e9df071805bcbe4a688b`
- `src/knowledge_compiler/openai_decomposed_extractor_v2.py`
  - SHA-256 `c6b30749be659006cf69fa451ee5d287d52f7e30b20e232755be0231bc31edbb`
- `src/knowledge_compiler/spec051_offline_evaluation.py`
  - SHA-256 `144fa68607a64277a112301e9cba19e6377a5ab4cf7831c26719ca414b6457af`

Frozen stage identities:

### Stage 1 — ENTITY_INVENTORY

- prompt version `spec-047-entity-inventory-v1`
- prompt SHA-256 `b1c00eb4547de56c62dcc18c7aec013ee1e2de4a8c1dfa45bcb475f00591f785`
- schema SHA-256 `003db7546ae3ffafe7dc098bc50e1a5f223b891f6ee3160f7537214c8e9c9956`

### Stage 2 — SEMANTIC_STRUCTURE

- prompt version `spec-051-semantic-structure-v2`
- prompt SHA-256 `72e6b878794ac2fa45404970e2f0a931dc4c1c2efc97f64a4c7aed0ecf212299`
- schema template SHA-256 `b9c5861354e3423f8712778048efd451b81bc52178ef798219b52e56b94d5560`

Dynamic Stage-2 schemas may substitute the exact frozen Stage-1 entity IDs as designed, but must otherwise derive deterministically from this frozen template/contract.

### Stage 3 — CLAIM_EVIDENCE_BINDING

- prompt version `spec-051-claim-evidence-binding-v2`
- prompt SHA-256 `a450efcc629ab3a28bb1357f5139dc343e62c4cf9772a497e7b7f1c65dedd97f`
- schema template SHA-256 `bd8957cc40b49c7482767fb1cbbfec958ae924ad89ded740aeaa18c168e699de`

Dynamic Stage-3 schemas may substitute exact frozen Stage-2 semantic object IDs as designed, but must otherwise derive deterministically from this frozen template/contract.

## Exact authorized source set

Use the same nine frozen passages, in this exact order:

1. `usgs-divergent-plate-boundaries-1996`
   - SHA-256 `a9539d135ff1577d7e2791d498b92f55239175565b925b24aec2ed0bf633f186`
   - packet: `examples/evaluations/spec-041-blind-source-set-freeze-20260911/blind-source-packet.json`
2. `noaa-nesdis-jet-stream-2025`
   - SHA-256 `256ade61be620cfaa7b1327e3c982576611dd29b6a1fb42217d86ffdc0783ca1`
   - packet: SPEC-041 packet above
3. `crs-legislative-process-r42843-17`
   - SHA-256 `fe61b7c3b2a9373e7eb3b30d16b94adc2c8b5f4307327265943995550a6384b4`
   - packet: SPEC-041 packet above
4. `nasa-solar-system-formation-2026`
   - SHA-256 `c0cb2519673b8f3ef23c0be2856e03790f53d44971cbff09d593190ab3fa155d`
   - packet: `examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/blind-source-packet.json`
5. `epa-ecological-processes-2026`
   - SHA-256 `70e7e3d20325dd5d22e9cf4484934419447907ba9f6cf5a4dfd65ddcbfa80ad5`
   - packet: SPEC-044 packet above
6. `doe-iron-platinum-atomic-structure-2017`
   - SHA-256 `e9d2260c9980239431fc195e7dc687afea93598af4f28d774ed5e4c4317f9e1e`
   - packet: SPEC-044 packet above
7. `nhgri-dna-fact-sheet-2020`
   - SHA-256 `54e2147221cf186fe1b4f965422c69e815f986a7d009eddae9c01bf32ec25f89`
   - packet: SPEC-044 packet above
8. `fhwa-traffic-bottleneck-concepts-2016`
   - SHA-256 `1fd7e9851839f5f35cd2a231cd3ce5aea8196ec85cabd04694f681c063ea4345`
   - packet: SPEC-044 packet above
9. `nist-measurement-uncertainty-2025`
   - SHA-256 `b3ae508f3982dfdd89f41a1d9ca59eb1f658b1648e3fae35168feba212046730`
   - packet: SPEC-044 packet above

Source packet hashes remain:

- SPEC-041 packet SHA-256 `ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0`
- SPEC-044 packet SHA-256 `85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b`

No other source text is authorized.

## Exact provider authority

Provider: OpenAI Responses API.

Model: `gpt-5.6-luna`.

Storage: `store=False`.

Maximum provider calls: **27**.

Maximum calls per source: **3**.

Maximum calls per stage per source: **1**.

Stage order:

1. `ENTITY_INVENTORY`
2. `SEMANTIC_STRUCTURE`
3. `CLAIM_EVIDENCE_BINDING`

Mandatory short-circuit:

- Stage-1 failure → stop source after 1 call;
- Stage-2 failure → stop source after 2 calls;
- Stage-3 reached → maximum 3 calls for source.

Retries/follow-ups:

- SDK retries `0`;
- hidden retries `0`;
- semantic retries `0`;
- repair calls `0`;
- follow-up calls outside the defined stages `0`;
- additional calls without new owner approval `0`.

External retrieval/enrichment during execution: `0`.

Prompt adaptation between sources: `0`.

Implementation adaptation after execution begins: `0`.

## Mandatory preflight

Before the first provider call verify:

1. Candidate B v2 contract hash matches exactly;
2. all frozen implementation file hashes match;
3. all three stage prompt/schema template identities match;
4. SPEC-041 and SPEC-044 source packet hashes match;
5. all nine exact source hashes match;
6. source order matches this packet;
7. Control A and Candidate B v1 protected implementation/evidence remain unchanged;
8. canonical proposition semantics and validators remain unchanged;
9. structure detection and representation strategy remain unchanged;
10. `store=False`;
11. all retry/follow-up classes are zero;
12. no source-specific prompt/schema adaptation has occurred.

Any mismatch must stop execution before provider transmission. Do not repair a mismatch.

## Execution policy

For each source in fixed order:

```text
exact frozen source
   ↓
Stage 1: one entity-inventory call
   ↓ deterministic gate/freeze or fail closed
Stage 2: one v2 semantic-structure call
   ↓ deterministic gate/freeze or fail closed
Stage 3: one v2 claim/evidence call
   ↓ deterministic exact grounding
existing canonical KnowledgeModel validation
   ↓
PASS or FAIL_CLOSED
   ↓
if PASS: existing structure detection + representation decisions
```

Preserve every raw response and stage outcome.

Do not repair, retry, reinterpret through another model, or alter implementation after seeing results.

## Semantic omission audit

SPEC-052 must explicitly audit the v2 hypothesis that non-topological truth survives omission.

For each source that reaches Stage 3, record:

- claims emitted by Stage 3;
- which claims are not represented by Stage-2 topology;
- exact grounding/evidence status;
- whether those claims remain present in the admitted KnowledgeModel;
- whether they create any relationship/proposition/topology implicitly (they must not);
- whether existing explanatory/assertion-aware representation can preserve them under current behavior.

Do not require historical source-specific expected claims as an answer key. The audit is mechanical over actual v2 output.

## Historical comparison arms

Do not rerun either historical arm.

Compare against preserved evidence only:

### Control A

Historical admission: 4/9.

Historical calls: 9.

Historical total tokens: 54,586.

Known-invalid admission: 0.

### Candidate B v1

Historical admission: 2/9.

Historical calls: 19.

Historical total tokens: 94,574.

Known-invalid admission: 0.

Historical B-v1 Stage-2 proposition-construction failures: 6.

Record the non-contemporaneous stochastic/time-drift limitation explicitly.

## Primary evaluation questions

Answer mechanically where possible:

1. What is Candidate B v2 source admission rate?
2. Are known-invalid/malformed objects still contained (target 0 admitted)?
3. How many failures occur at each stage?
4. How many failures originate in proposition construction?
5. Did the six-failure B-v1 Stage-2 concentration materially disappear?
6. For admitted sources, are omitted non-topological meanings preserved as grounded claims where the model emitted them?
7. Does claim preservation create zero unintended topology?
8. How do entity/relationship/proposition/claim counts compare descriptively across A, B v1, and B v2?
9. How do detected structures and representation decisions compare descriptively?
10. What are v2 calls, tokens, latency, and available monetary-cost evidence?
11. Is v2 materially better than B v1?
12. Is v2 competitive enough with Control A to justify continued decomposition work?

## Semantic richness guard

Do not credit v2 merely for passing by emitting less.

For each admitted v2 source preserve:

- entity count;
- relationship count;
- proposition count;
- claim count;
- detected structure count/types;
- representation strategy/sufficiency counts;
- claim-only preservation evidence.

Because historical arms may pass different sources, do not treat aggregate richness totals as paired evidence unless the same source passed both compared arms.

## Frozen decision framework

Use exactly these branches from SPEC-051:

- `B_V2_RECOVERS_DECOMPOSITION`
- `B_V2_STRUCTURAL_FIX_ONLY`
- `B_V2_TOO_SPARSE`
- `B_V2_REGRESSION`
- `INCONCLUSIVE`

Mechanical evidence may identify a supported branch when unambiguous, but final owner verdict and promotion remain human-gated.

### Interpretation guidance

`B_V2_RECOVERS_DECOMPOSITION` requires evidence that v2 materially improves over B v1, preserves trust containment, substantially removes the Stage-2 proposition failure concentration, preserves omitted source meaning as claims, and is competitive enough with Control A to justify further work.

`B_V2_STRUCTURAL_FIX_ONLY` applies if malformed proposition failures are removed but end-to-end admission/usefulness does not improve enough to justify decomposition cost.

`B_V2_TOO_SPARSE` applies if improved admission is achieved by materially dropping useful meaning that is not adequately preserved as claims.

`B_V2_REGRESSION` applies if v2 worsens reliability, trust containment, or semantic preservation.

`INCONCLUSIVE` applies when non-contemporaneous stochastic evidence or mixed results prevent a defensible decision.

## Failure taxonomy

For any failed source, classify origin using the established SPEC-046 taxonomy where evidence permits:

- `ENTITY_INVENTORY`
- `RELATIONSHIP_SEMANTICS`
- `PROPOSITION_CONSTRUCTION`
- `EVIDENCE_FIDELITY`
- `CROSS_REFERENCE_CONSISTENCY`
- `GROUNDING_RESOLUTION`
- `CANONICAL_VALIDATION`
- `OTHER`

Record detection stage separately.

Do not alter historical classifications.

## Audit artifacts

Create:

`examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915/`

Preserve per source/stage at minimum:

- source identity/hash;
- stage/version/prompt/schema identities;
- dynamic schema hash where applicable;
- provider request/response ID;
- raw provider response;
- parsed proposal;
- deterministic gate status/failure;
- upstream/output identity hashes;
- call ledger entry;
- tokens and latency;
- downstream short-circuit state.

Per source preserve:

- final PASS/FAILED_CLOSED outcome;
- admitted KnowledgeModel or exact failure evidence;
- failure origin/detection classification where applicable;
- semantic omission/claim-preservation audit if Stage 3 ran;
- detected structures/representation decisions if admitted.

Create canonical aggregate `final-report.json` and provider call ledger.

## Instrumentation

Count provider calls at request start.

The authoritative call ledger must reconcile exactly with preserved raw responses and stage invocations.

Do not repeat the historical SPEC-045 completed-adapter-return observability limitation.

## Validation after live execution

Without rerunning provider calls:

- verify call count ≤27;
- verify maximum one call per stage/source;
- verify source/stage order;
- verify mandatory short-circuit behavior;
- verify zero retries/repairs/follow-ups;
- verify `store=False`;
- verify frozen implementation/prompt/schema/source identities;
- verify Control A/B-v1 historical evidence unchanged;
- verify canonical validators/structure/representation behavior unchanged;
- validate raw response/provenance completeness;
- validate semantic omission audit;
- validate failure taxonomy;
- run focused SPEC-052 tests;
- run control-plane tests;
- run full offline suite;
- validate JSON;
- run secret-safety checks;
- run `git diff --check`.

Do not make additional provider calls during validation.

## Explicitly forbidden

Do not:

- rerun Control A;
- rerun Candidate B v1;
- exceed 27 calls;
- retry any stage;
- repair any output;
- change v2 prompt/schema/implementation after execution starts;
- add source-specific rules/examples;
- add proposition types/predicates;
- reinterpret canonical proposition semantics;
- weaken canonical validation;
- force omitted claims into topology;
- change structure detection;
- change representation/renderers/UI/navigation;
- use external enrichment