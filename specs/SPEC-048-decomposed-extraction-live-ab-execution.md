# SPEC-048 — Decomposed Extraction Live A/B Execution

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Execute frozen Candidate B from SPEC-047 against the exact nine frozen blind source passages, compare the resulting evidence against preserved historical Control A, and stop for owner review.

This packet authorizes only the live Candidate-B arm. Control A must not be rerun.

No repair, prompt tuning, semantic adaptation, source substitution, or product promotion is authorized.

## Owner approval incorporated

Owner/ChatGPT reviewed SPEC-047 and approved the decomposed extractor and A/B contract for live evaluation.

Owner verdict:

`CANDIDATE_B_FROZEN_LIVE_AB_EXECUTION_APPROVED`

Accepted caveat:

- Control A is historical SPEC-042/SPEC-045 evidence;
- Candidate B is a future execution;
- contemporaneous stochastic/model-time drift is therefore not controlled;
- a marginal effect must be treated conservatively/inconclusively rather than overinterpreted.

## Frozen Candidate B identity

Candidate version:

`spec-047-candidate-b-v1`

Frozen implementation commit:

`9ad5e0854e6866c73b3f6febd989e0766cc14a13`

Implementation hashes:

- core: `a09bb36a2214364f915b05e0f7818ffe0b145760b76afb1f00fc66ed09dc75ea`
- OpenAI adapter: `2d91a2fdfcf04bcc2180331571e3d7c2a20e797fe9fbc83c046aafdad1764280`
- A/B harness: `85e60376aabc797e75bafbda71df3ec2a68d24f0220f931b2eb89f0d9b9824fc`

Frozen stage-contract SHA-256:

`b13c96ac01b2f0730f57852078c702f01a2234bca1f7567654686d214c50f694`

Frozen SPEC-047 proposed manifest:

`examples/evaluations/spec-047-decomposed-extraction-ab-harness-20260913/proposed-live-execution-manifest.json`

## Source packet identities

Initial blind packet:

`examples/evaluations/spec-041-blind-source-set-freeze-20260911/blind-source-packet.json`

SHA-256:

`ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0`

Replication blind packet:

`examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/blind-source-packet.json`

SHA-256:

`85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b`

## Exact source order

Execute Candidate B only for these nine sources in exactly this order:

1. `usgs-divergent-plate-boundaries-1996`
   - SHA-256 `a9539d135ff1577d7e2791d498b92f55239175565b925b24aec2ed0bf633f186`
2. `noaa-nesdis-jet-stream-2025`
   - SHA-256 `256ade61be620cfaa7b1327e3c982576611dd29b6a1fb42217d86ffdc0783ca1`
3. `crs-legislative-process-r42843-17`
   - SHA-256 `fe61b7c3b2a9373e7eb3b30d16b94adc2c8b5f4307327265943995550a6384b4`
4. `nasa-solar-system-formation-2026`
   - SHA-256 `c0cb2519673b8f3ef23c0be2856e03790f53d44971cbff09d593190ab3fa155d`
5. `epa-ecological-processes-2026`
   - SHA-256 `70e7e3d20325dd5d22e9cf4484934419447907ba9f6cf5a4dfd65ddcbfa80ad5`
6. `doe-iron-platinum-atomic-structure-2017`
   - SHA-256 `e9d2260c9980239431fc195e7dc687afea93598af4f28d774ed5e4c4317f9e1e`
7. `nhgri-dna-fact-sheet-2020`
   - SHA-256 `54e2147221cf186fe1b4f965422c69e815f986a7d009eddae9c01bf32ec25f89`
8. `fhwa-traffic-bottleneck-concepts-2016`
   - SHA-256 `1fd7e9851839f5f35cd2a231cd3ce5aea8196ec85cabd04694f681c063ea4345`
9. `nist-measurement-uncertainty-2025`
   - SHA-256 `b3ae508f3982dfdd89f41a1d9ca59eb1f658b1648e3fae35168feba212046730`

No other source is authorized.

## Candidate-B stage order

For each source:

```text
STAGE 1 — ENTITY_INVENTORY
        ↓ deterministic PASS/FAIL_CLOSED
STAGE 2 — SEMANTIC_STRUCTURE
        ↓ deterministic PASS/FAIL_CLOSED
STAGE 3 — CLAIM_EVIDENCE_BINDING
        ↓ deterministic PASS/FAIL_CLOSED
EXISTING CANONICAL VALIDATOR
        ↓
trusted KnowledgeModel or fail closed
```

Stage-order and upstream identities must remain frozen.

## Exact call authority

Provider: OpenAI Responses API.

Model: `gpt-5.6-luna`.

Storage: `store=False`.

Maximum provider calls: **27**.

Maximum calls per stage per source: **1**.

Maximum stages per source: **3**.

Short-circuit rules:

- Stage 1 failure → no Stage 2/3 calls;
- Stage 2 failure → no Stage 3 call;
- Stage 3 reached → maximum three calls total for that source.

Retries/follow-ups:

- SDK retries: `0`;
- hidden retries: `0`;
- semantic retries: `0`;
- repair calls: `0`;
- extra follow-up calls: `0`;
- source-specific prompt edits: `0`;
- implementation adaptations after execution begins: `0`;
- external retrieval/enrichment: `0`.

## Mandatory preflight

Before the first provider request verify all of the following:

1. Candidate-B implementation file hashes match SPEC-047 exactly;
2. stage-contract SHA-256 matches exactly;
3. both source-packet SHA-256 values match exactly;
4. all nine passage SHA-256 values match exactly;
5. source order matches the frozen SPEC-047 manifest;
6. canonical validator files/hashes remain unchanged from SPEC-047;
7. Control-A implementation and preserved historical evidence remain unchanged;
8. representation compiler and SPEC-038 baseline remain unchanged;
9. Candidate-B prompts/schemas are byte-identical to frozen SPEC-047 identities;
10. `store=False`;
11. every retry class is zero;
12. no source-specific adaptation/tuning occurred after SPEC-047 freeze.

Any mismatch stops the run before provider transmission. Do not repair the mismatch under this packet.

## Execution evidence

Create:

`examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/`

For each source and stage preserve at minimum:

- source ID/hash;
- stage name/version;
- prompt/schema identity/hash;
- exact frozen upstream identity/hash;
- provider request/response IDs;
- raw provider response;
- parsed proposal;
- input/output/total token usage;
- latency;
- deterministic gate status;
- exact rejection reason when failed;
- downstream execution status;
- request-start call ledger entry.

For each source preserve final Candidate-B outcome:

- `PASS` or `FAILED_CLOSED`;
- canonical admitted entity/relationship/proposition/claim counts if PASS;
- detected structures;
- representation strategy counts/sufficiency;
- failure origin/detection stages if rejected;
- total calls, tokens, and latency.

## Historical Control A

Do not make any Control-A provider call.

Use only frozen SPEC-042/SPEC-045 historical comparison records already materialized by SPEC-047.

Control-A baseline remains:

- 9 attempted sources;
- 4 admitted;
- admission rate `4/9`;
- 0 known-invalid objects admitted;
- 54,586 total historical tokens;
- 9 total historical calls;
- preserved semantic richness/structure/representation evidence.

Do not reinterpret historical failures using Candidate-B outcomes.

## Comparison metrics

Use the exact SPEC-047 frozen comparison contract.

Primary:

1. source admission rate;
2. trust-boundary containment;
3. failure-origin distribution.

Secondary:

- entity inventory consistency;
- undeclared-reference failures;
- relationship/proposition semantic rejections;
- evidence-fidelity rejections;
- admitted entity/relationship/proposition/claim counts;
- detected structure counts/types;
- representation strategy counts/sufficiency;
- calls per source;
- token usage per attempted/admitted source;
- provider latency per source;
- available monetary cost evidence.

## Semantic-richness guard

Candidate B must not be credited with improvement merely for producing less semantic content.

Compare, for admitted sources:

- entity count;
- relationship count;
- proposition count;
- claims;
- detected structures;
- representation decisions with sufficient trusted structure.

Report source-by-source and aggregate differences.

## Trust-boundary invariant

The deterministic trust boundary remains unchanged.

A Candidate-B output that passes only because validation became weaker invalidates the experiment.

Known-invalid/malformed objects admitted must remain `0`.

## Failure analysis

Use SPEC-046 origin/detection-stage taxonomy for Candidate-B failures where applicable.

Do not use a model to diagnose failures.

Do not repair or rerun a failure.

A failure at Stage 1/2/3 is evidence about decomposition and must remain preserved.

## Decision framework

Evaluate evidence against the frozen SPEC-047 owner framework:

- `B_CLEAR_IMPROVEMENT`
- `B_SAFER_BUT_TOO_SPARSE`
- `B_NO_MATERIAL_GAIN`
- `B_REGRESSION`
- `INCONCLUSIVE`

Codex may report which branch is mechanically best supported, but final owner verdict remains pending.

Because Control A is historical rather than contemporaneous, small/marginal differences should be treated as `INCONCLUSIVE` rather than strong causal evidence.

## No adaptation during execution

Once the first Candidate-B request starts, do not change:

- prompts;
- schemas;
- implementation;
- stage boundaries;
- model;
- source order/text;
- validation;
- semantic vocabulary;
- grounding;
- representation strategy;
- renderer/UI;
- comparison metrics/decision framework.

Do not tune later sources based on earlier outputs.

## Failure policy

Provider failure or deterministic stage failure:

- preserve complete attempt;
- no retry;
- no repair;
- short-circuit remaining stages for that source;
- continue to next already-authorized source.

Frozen-identity/experiment-contamination failure:

- stop entire run;
- preserve evidence;
- mark run invalidated;
- do not repair/resume under SPEC-048.

## Validation after live execution

Without rerunning provider calls:

- verify call count `<= 27`;
- verify one-call-per-stage-per-source maximum;
- verify short-circuit behavior;
- verify fixed source order;
- verify request-start accounting;
- verify zero retries/repairs/follow-ups;
- verify all frozen identities/hashes;
- verify raw-response and provenance completeness;
- verify canonical validator unchanged;
- verify trust-boundary containment;
- validate A/B comparison metrics and semantic-richness calculations;
- run focused SPEC-048 tests;
- run control-plane tests;
- run full offline suite;
- validate JSON;
- secret-safety checks;
- `git diff --check`;
- verify protected historical evidence unchanged.

Do not rerun model calls to satisfy validation.

## Explicitly forbidden

Do not:

- rerun Control A;
- exceed 27 Candidate-B calls;
- retry any Candidate-B stage;
- repair a failed stage;
- change model;
- edit source text/order;
- use web/network enrichment;
- change prompts/schemas between sources;
- normalize missing IDs automatically;
- weaken evidence exactness;
- weaken canonical validation;
- change semantic vocabulary;
- change representation/renderers/UI/navigation;
- implement further extraction improvements;
- promote Candidate B automatically.

## Completion state

After the authorized live comparison:

- set SPEC-048 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report exact call count, token/latency evidence, source outcomes, A/B metrics, semantic-richness comparison, and mechanically supported decision branch;
- stop at `OWNER_REVIEW`;
- do not prepare or implement follow-up work automatically.

## Owner review question

> Does decomposed extraction materially improve trustworthy admission and failure isolation enough to justify its additional model-call, token, latency, and architectural cost compared with the preserved single-pass control?
