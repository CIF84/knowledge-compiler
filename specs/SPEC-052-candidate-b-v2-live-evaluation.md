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

Candidate version: `spec-051-candidate-b-v2`

Contract SHA-256:

`6a149b1d3bac5789652de77af2630ffea84893413e892f4606df3c718e48d148`

Frozen implementation files:

- `src/knowledge_compiler/decomposed_extraction_v2.py` — SHA-256 `0d6676676fa69aaf55d3b3f974bbbbaf02d1f30d0568e9df071805bcbe4a688b`
- `src/knowledge_compiler/openai_decomposed_extractor_v2.py` — SHA-256 `c6b30749be659006cf69fa451ee5d287d52f7e30b20e232755be0231bc31edbb`
- `src/knowledge_compiler/spec051_offline_evaluation.py` — SHA-256 `144fa68607a64277a112301e9cba19e6377a5ab4cf7831c26719ca414b6457af`

Frozen stage identities:

- Stage 1 `ENTITY_INVENTORY`: prompt `spec-047-entity-inventory-v1`, prompt SHA-256 `b1c00eb4547de56c62dcc18c7aec013ee1e2de4a8c1dfa45bcb475f00591f785`, schema SHA-256 `003db7546ae3ffafe7dc098bc50e1a5f223b891f6ee3160f7537214c8e9c9956`.
- Stage 2 `SEMANTIC_STRUCTURE`: prompt `spec-051-semantic-structure-v2`, prompt SHA-256 `72e6b878794ac2fa45404970e2f0a931dc4c1c2efc97f64a4c7aed0ecf212299`, schema-template SHA-256 `b9c5861354e3423f8712778048efd451b81bc52178ef798219b52e56b94d5560`.
- Stage 3 `CLAIM_EVIDENCE_BINDING`: prompt `spec-051-claim-evidence-binding-v2`, prompt SHA-256 `a450efcc629ab3a28bb1357f5139dc343e62c4cf9772a497e7b7f1c65dedd97f`, schema-template SHA-256 `bd8957cc40b49c7482767fb1cbbfec958ae924ad89ded740aeaa18c168e699de`.

Dynamic Stage-2/Stage-3 schemas may substitute exact frozen upstream IDs as designed, but must otherwise derive deterministically from the frozen templates/contracts.

## Exact authorized source set

Use the same nine frozen passages in this exact order:

1. `usgs-divergent-plate-boundaries-1996` — `a9539d135ff1577d7e2791d498b92f55239175565b925b24aec2ed0bf633f186`
2. `noaa-nesdis-jet-stream-2025` — `256ade61be620cfaa7b1327e3c982576611dd29b6a1fb42217d86ffdc0783ca1`
3. `crs-legislative-process-r42843-17` — `fe61b7c3b2a9373e7eb3b30d16b94adc2c8b5f4307327265943995550a6384b4`
4. `nasa-solar-system-formation-2026` — `c0cb2519673b8f3ef23c0be2856e03790f53d44971cbff09d593190ab3fa155d`
5. `epa-ecological-processes-2026` — `70e7e3d20325dd5d22e9cf4484934419447907ba9f6cf5a4dfd65ddcbfa80ad5`
6. `doe-iron-platinum-atomic-structure-2017` — `e9d2260c9980239431fc195e7dc687afea93598af4f28d774ed5e4c4317f9e1e`
7. `nhgri-dna-fact-sheet-2020` — `54e2147221cf186fe1b4f965422c69e815f986a7d009eddae9c01bf32ec25f89`
8. `fhwa-traffic-bottleneck-concepts-2016` — `1fd7e9851839f5f35cd2a231cd3ce5aea8196ec85cabd04694f681c063ea4345`
9. `nist-measurement-uncertainty-2025` — `b3ae508f3982dfdd89f41a1d9ca59eb1f658b1648e3fae35168feba212046730`

Source packets:

- `examples/evaluations/spec-041-blind-source-set-freeze-20260911/blind-source-packet.json` — SHA-256 `ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0`
- `examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/blind-source-packet.json` — SHA-256 `85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b`

No other source text is authorized.

## Exact provider authority

Provider: OpenAI Responses API.

Model: `gpt-5.6-luna`.

Storage: `store=False`.

Maximum provider calls: **27**.

Maximum calls per source: **3**.

Maximum calls per stage per source: **1**.

Stage order: `ENTITY_INVENTORY` → `SEMANTIC_STRUCTURE` → `CLAIM_EVIDENCE_BINDING`.

Mandatory short-circuit:

- Stage-1 failure → stop source after 1 call;
- Stage-2 failure → stop source after 2 calls;
- Stage-3 reached → maximum 3 calls for source.

Retries/follow-ups: SDK `0`, hidden `0`, semantic `0`, repair `0`, follow-up outside defined stages `0`, additional calls without new owner approval `0`.

External retrieval/enrichment during execution: `0`.

Prompt adaptation between sources: `0`.

Implementation adaptation after execution begins: `0`.

## Mandatory preflight

Before the first provider call verify all frozen Candidate-B-v2 contract/implementation/stage identities, both source packet hashes, all nine source hashes/order, historical Control-A/B-v1 protected evidence, canonical proposition/validator identities, structure detection/representation identities, `store=False`, zero retry classes, and absence of source-specific adaptation.

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

Preserve every raw response and stage outcome. Do not repair, retry, reinterpret through another model, or alter implementation after seeing results.

## Semantic omission audit

For every source reaching Stage 3, record mechanically:

- Stage-3 claims;
- claims not represented by Stage-2 topology;
- exact grounding/evidence status;
- whether those claims remain in the admitted KnowledgeModel;
- whether they create any relationship/proposition/topology implicitly (must be zero);
- whether current assertion-aware/explanatory representation preserves them under existing behavior.

Do not use historical source-specific expected claims as an answer key.

## Historical comparison arms

Do not rerun either historical arm.

Control A historical: 4/9 admitted, 9 calls, 54,586 total tokens, zero known-invalid admission.

Candidate B v1 historical: 2/9 admitted, 19 calls, 94,574 total tokens, zero known-invalid admission, 6 Stage-2 proposition-construction failures.

Record explicitly that all arms are non-contemporaneous and stochastic/time drift is uncontrolled.

## Evaluation questions

Report:

1. Candidate B v2 admission rate.
2. Known-invalid/malformed object admission.
3. Failure count by stage and SPEC-046 origin taxonomy where applicable.
4. Proposition-construction failure count and whether the B-v1 six-failure concentration materially disappeared.
5. Claim-only preservation and unintended-topology count.
6. Entity/relationship/proposition/claim counts for admitted sources.
7. Detected structures and representation decisions.
8. Calls, tokens, latency, and available monetary-cost evidence.
9. Descriptive comparison A vs B v1 vs B v2, respecting same-source overlap and non-contemporaneous limitations.
10. Whether v2 materially improves over B v1 and is competitive enough with Control A to justify continued decomposition work.

## Semantic richness guard

Do not credit v2 merely for passing by emitting less. Preserve semantic counts, structures, representation decisions, and claim-only preservation for every admitted source. Aggregate totals are descriptive only when arms admit different sources; same-source comparisons may be treated as paired descriptive evidence.

## Frozen decision framework

Use exactly:

- `B_V2_RECOVERS_DECOMPOSITION`
- `B_V2_STRUCTURAL_FIX_ONLY`
- `B_V2_TOO_SPARSE`
- `B_V2_REGRESSION`
- `INCONCLUSIVE`

Mechanical evidence may identify a supported branch if unambiguous, but final owner verdict/promotion remain human-gated.

## Failure taxonomy

For failed sources use the established SPEC-046 origin taxonomy where evidence permits: `ENTITY_INVENTORY`, `RELATIONSHIP_SEMANTICS`, `PROPOSITION_CONSTRUCTION`, `EVIDENCE_FIDELITY`, `CROSS_REFERENCE_CONSISTENCY`, `GROUNDING_RESOLUTION`, `CANONICAL_VALIDATION`, `OTHER`. Record detection stage separately. Do not alter historical classifications.

## Audit artifacts

Create:

`examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915/`

Preserve per source/stage: source/hash, stage/version/prompt/schema identities, dynamic schema hash, provider request/response ID, raw response, parsed proposal, deterministic gate/failure, upstream/output identities, call-ledger entry, tokens/latency, and downstream short-circuit state.

Per source preserve final outcome, admitted model or exact failure evidence, failure classification, semantic-omission audit if Stage 3 ran, and detected structures/representation decisions if admitted.

Create canonical aggregate `final-report.json` and provider call ledger.

## Instrumentation

Count provider calls at request start. The authoritative ledger must reconcile exactly with preserved raw responses and stage invocations.

## Validation after execution

Without rerunning provider calls, verify call/order/short-circuit/retry/store constraints; frozen implementation/prompt/schema/source identities; historical evidence and canonical behavior unchanged; raw-response/provenance completeness; semantic-omission audit; failure taxonomy; focused SPEC-052 tests; control-plane tests; full offline suite; JSON; secret safety; and `git diff --check`.

Do not make additional provider calls during validation.

## Explicitly forbidden

Do not:

- rerun Control A or Candidate B v1;
- exceed 27 calls;
- retry/repair any stage;
- change v2 prompt/schema/implementation after execution starts;
- add source-specific rules/examples;
- add proposition types/predicates or reinterpret canonical proposition semantics;
- weaken canonical validation;
- force omitted claims into topology;
- change structure detection, representation/renderers, navigation, or UI;
- use external enrichment;
- promote any extractor;
- implement follow-up fixes automatically.

## Completion state

After the single authorized run:

- set SPEC-052 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report canonical final report/ledger paths, call/token/latency totals, admission/failure evidence, omission audit, and mechanically supported branch;
- stop at `OWNER_REVIEW`;
- do not promote or implement follow-up work.

## Owner review question

> Did schema-constrained semantic omission allow Candidate B v2 to recover the value of extraction decomposition — improving materially over B v1 while preserving trusted knowledge and non-topological source truth — or does the evidence now favor abandoning this decomposition architecture?
