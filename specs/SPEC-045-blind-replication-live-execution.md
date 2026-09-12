# SPEC-045 — Blind Replication Live Execution

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Execute the already-frozen SPEC-044 six-source blind replication exactly once through the unchanged frozen SPEC-040 harness/compiler, classify any rejected semantic objects using the already-frozen SPEC-043 taxonomy, and stop for owner review.

This is a replication experiment, not a repair packet. No product, prompt, semantic-contract, validator, representation, renderer, or UI adaptation is authorized.

## Owner approval incorporated

Owner/ChatGPT reviewed the exact SPEC-044 six-source packet and live-execution manifest and explicitly approved transmission of exactly those six frozen passages under the frozen call contract.

Approved packet:

`examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/blind-source-packet.json`

Packet SHA-256:

`85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b`

Approved manifest:

`examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/live-execution-manifest.json`

Manifest SHA-256:

`beaf3df4a941afc7fadf2abf13543affeae798e3d14486798cbb0060fccdc57e`

Frozen harness/compiler identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Exact authorized sources

Execute only these sources, in this exact order:

1. `nasa-solar-system-formation-2026`
   - SHA-256 `c0cb2519673b8f3ef23c0be2856e03790f53d44971cbff09d593190ab3fa155d`
2. `epa-ecological-processes-2026`
   - SHA-256 `70e7e3d20325dd5d22e9cf4484934419447907ba9f6cf5a4dfd65ddcbfa80ad5`
3. `doe-iron-platinum-atomic-structure-2017`
   - SHA-256 `e9d2260c9980239431fc195e7dc687afea93598af4f28d774ed5e4c4317f9e1e`
4. `nhgri-dna-fact-sheet-2020`
   - SHA-256 `54e2147221cf186fe1b4f965422c69e815f986a7d009eddae9c01bf32ec25f89`
5. `fhwa-traffic-bottleneck-concepts-2016`
   - SHA-256 `1fd7e9851839f5f35cd2a231cd3ce5aea8196ec85cabd04694f681c063ea4345`
6. `nist-measurement-uncertainty-2025`
   - SHA-256 `b3ae508f3982dfdd89f41a1d9ca59eb1f658b1648e3fae35168feba212046730`

No other source text is authorized for provider transmission.

## Exact call authority

Provider: OpenAI Responses API.

Model: `gpt-5.6-luna`.

Prompt: frozen `spec-010-v1` / `knowledge_extraction`.

Maximum total provider calls: **6**.

Calls per source: **1**.

Execution order: exact frozen order above.

Storage: `store=False`.

External retrieval or enrichment during execution: `0`.

Source-specific prompt edits: `0`.

Implementation adaptations between calls: `0`.

Canonicalization model follow-up calls: `0`.

Retries/follow-ups:

- SDK retries: `0`;
- semantic retries: `0`;
- repair calls: `0`;
- hidden retries: `0`;
- follow-up calls: `0`;
- additional calls without new approval: `0`.

## Mandatory preflight

Before the first provider call, verify:

1. exact SPEC-044 packet SHA-256;
2. exact SPEC-044 manifest SHA-256;
3. all six exact passage SHA-256 values;
4. frozen harness/compiler files remain byte-equivalent to SPEC-040 identity;
5. SPEC-038 baseline identity remains preserved;
6. SPEC-042 evidence and SPEC-043 diagnostic report remain unchanged;
7. prompt/schema/relationship grammar remain frozen;
8. semantic vocabulary, grounding, provenance, declared-identity validation, representation rules, renderer coverage, and evaluation rules remain unchanged;
9. `store=False`;
10. every retry/follow-up class remains zero;
11. no source-specific adaptation has occurred after source freeze.

Any mismatch must stop execution before transmitting any source. Do not repair a mismatch.

## Execution

For each frozen source in order:

```text
exact frozen passage
        ↓
one gpt-5.6-luna extraction call
        ↓
preserve full raw response + request metadata + usage
        ↓
deterministic local grounding
        ↓
canonical semantic validation / fail closed
        ↓
if admitted: structure detection + representation decisions
        ↓
if rejected: preserve exact rejected objects for offline classification
```

Do not change anything after observing a result.

A failed-closed result is valid experimental evidence.

## Rejection classification

After all six provider calls have completed or failed according to the frozen failure policy, classify every rejected semantic object **offline** using exactly the SPEC-043 primary taxonomy:

- `MODEL_ERROR`
- `CONTRACT_GAP`
- `EXTRACTION_GRANULARITY`
- `VALIDATION_BUG`
- `AMBIGUOUS`

Do not introduce a new category during this experiment.

For every rejected object preserve:

- source ID;
- object ID/type;
- exact proposed semantic statement/object;
- missing or invalid identities;
- exact source evidence;
- validator failure;
- primary classification;
- source-support assessment;
- concise rationale;
- confidence.

Classification must use only the frozen source and committed provider/validation evidence. No new model call or external retrieval is permitted.

## Replication questions

Aggregate results must answer the already-frozen SPEC-044 questions:

1. How many sources pass deterministic admission completely?
2. How many sources fail closed?
3. Across all rejected semantic objects, what are counts by SPEC-043 classification?
4. How many failures involve undeclared identities that are nevertheless materially source-supported?
5. Of those, how many are process/event reifications absent from the entity array?
6. Does the same immediate dangling-identity mechanism recur across at least two unrelated new domain strata?
7. Are genuine model errors more frequent than extraction-granularity failures?
8. Is there any evidence of `CONTRACT_GAP` or `VALIDATION_BUG`?
9. Does the replication evidence support a narrow extraction→contract alignment experiment, or remain insufficient?

Do not alter these questions after seeing results.

## Owner decision framework

Report evidence for the already-frozen outcomes, but do not assign the owner's final architectural decision:

- `A_SYSTEMATIC_ALIGNMENT_SIGNAL`
- `B_HETEROGENEOUS_FAILURES`
- `C_MODEL_ERROR_DOMINATED`
- `D_CLEAN_REPLICATION`

The report may identify which framework branch the objective evidence mechanically satisfies if the frozen criteria make that unambiguous, but must not authorize implementation.

## Audit artifacts

Create:

`examples/evaluations/spec-045-blind-replication-live-execution-20260912/`

Preserve per source at minimum:

- exact source identity/hash;
- exact provider input or immutable frozen-packet reference;
- full raw provider response;
- request/response IDs;
- model/prompt identity;
- timing;
- input/output/total token usage;
- available cost evidence;
- extraction proposal;
- grounding result;
- rejected assertions/relationships/propositions;
- admitted KnowledgeModel or explicit fail-closed state;
- detected structures and representation decisions for admitted sources;
- complete zero-retry run history.

Create canonical aggregate `report.json` containing execution integrity, all six outcomes, rejection classifications, aggregate replication answers, tests, provenance, and owner-review state.

## Failure policy

Provider or semantic validation failure for one source:

- preserve the complete attempt;
- no retry;
- no repair;
- no adaptation;
- continue only to the next already-authorized source.

Frozen identity mismatch or experimental contamination:

- stop the entire run;
- make no provider call if discovered preflight;
- if discovered later, preserve evidence and mark the experiment invalidated;
- do not repair and resume under this packet.

## Protected state

Do not modify:

- SPEC-040 frozen harness/compiler;
- SPEC-044 source packet or manifest;
- SPEC-043 taxonomy or diagnostic definitions;
- prompt `spec-010-v1`;
- extraction schema;
- semantic vocabulary;
- grounding/provenance behavior;
- strict declared-identity validation;
- representation strategy logic;
- renderer coverage;
- SPEC-038 learner-facing baseline;
- navigation/inspection/Explore Next behavior.

## Explicitly forbidden

Do not:

- add missing entities;
- normalize dangling identities into declared identities;
- weaken or change validation;
- change extraction granularity;
- edit prompt/schema;
- add source-specific examples;
- complete comparison/worked-example renderers;
- create new UI/navigation behavior;
- implement Back/history;
- personalize or add quizzes/courses;
- rerun an unattractive result;
- make more than six provider calls;
- use another model;
- retrieve external evidence during execution/classification;
- implement a fix after classification;
- promote the result.

## Validation

After execution/classification, without rerunning provider calls:

- validate call count/order/zero retries;
- validate all packet/source/frozen implementation hashes;
- validate raw-response and provenance completeness;
- validate diagnostic classifications against the fixed taxonomy;
- run focused execution/diagnostic tests;
- run control-plane tests;
- run full offline suite;
- validate JSON;
- run secret-safety checks;
- run `git diff --check`;
- verify protected artifacts unchanged.

## Completion state

On completion:

- set SPEC-045 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit and push according to repository protocol;
- stop at owner review;
- report aggregate evidence and exact canonical report path;
- do not implement any repair or follow-up packet automatically.

## Owner review question

> Across six new unrelated blind sources, did the SPEC-043 extraction-granularity failure pattern replicate strongly enough to justify a narrow extraction→contract alignment experiment, or does the broader evidence point elsewhere?
