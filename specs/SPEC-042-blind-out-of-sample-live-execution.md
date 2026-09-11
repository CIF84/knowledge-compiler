# SPEC-042 — Blind Out-of-Sample Live Execution

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Execute the already-frozen three-source blind out-of-sample evaluation exactly once through the already-frozen SPEC-040 harness/compiler, then stop for owner review.

This packet contains no new product design and authorizes no adaptation. It exists solely to make the owner-approved live execution explicit in the repository control plane.

## Owner approval incorporated

Owner/ChatGPT reviewed the exact SPEC-041 source packet and live-execution manifest and explicitly approved transmission of exactly those three frozen passages under the frozen call contract.

Approved source packet:

`examples/evaluations/spec-041-blind-source-set-freeze-20260911/blind-source-packet.json`

Packet SHA-256:

`ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0`

Approved live manifest:

`examples/evaluations/spec-041-blind-source-set-freeze-20260911/live-execution-manifest.json`

Manifest SHA-256:

`f45c8797b94a0a5d6a1902aa50b71a63af6277dfcf1e6956a2d2d1107339d075`

Frozen harness/compiler identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Exact authorized sources

Execute in this order only:

1. `usgs-divergent-plate-boundaries-1996`
   - SHA-256: `a9539d135ff1577d7e2791d498b92f55239175565b925b24aec2ed0bf633f186`
   - 438 words / 2716 UTF-8 bytes
2. `noaa-nesdis-jet-stream-2025`
   - SHA-256: `256ade61be620cfaa7b1327e3c982576611dd29b6a1fb42217d86ffdc0783ca1`
   - 417 words / 2368 UTF-8 bytes
3. `crs-legislative-process-r42843-17`
   - SHA-256: `fe61b7c3b2a9373e7eb3b30d16b94adc2c8b5f4307327265943995550a6384b4`
   - 340 words / 2154 UTF-8 bytes

No other source text is authorized for provider transmission.

## Exact call authority

Provider: OpenAI Responses API

Model: `gpt-5.6-luna`

Purpose: semantic extraction with deterministic local grounding and canonical validation.

Maximum total provider calls: **3**.

Calls per source: **1**.

Execution order: frozen packet order above.

Storage: `store=False`.

Prompt version: `spec-010-v1`.

Schema: `knowledge_extraction`.

Relationship grammar: current frozen trusted relationship vocabulary from the frozen implementation.

Retries and follow-ups:

- SDK retries: `0`;
- hidden retries: `0`;
- semantic retries: `0`;
- repair calls: `0`;
- canonicalization/model follow-up calls: `0`;
- additional provider calls without new approval: `0`.

External retrieval/enrichment during execution: `0`.

## Preflight — mandatory before first call

Before transmitting any source:

1. verify the source packet file hash exactly matches the approved packet SHA-256;
2. verify the live manifest file hash exactly matches the approved manifest SHA-256;
3. verify all three exact source passage hashes match the values above;
4. verify frozen harness/compiler files are byte-equivalent to the SPEC-040 frozen identity recorded in the manifest;
5. verify prompt/version, semantic vocabulary, grounding rules, representation rules, renderer behavior, and evaluation criteria have not changed from the frozen experiment;
6. verify `store=False` and all retry classes are zero;
7. verify no source-specific implementation change occurred after source freeze.

Any mismatch must stop execution **before any provider call**. Do not repair or reinterpret a mismatch.

## Execution policy

For each already-approved source, in fixed order:

```text
exact frozen passage
        ↓
one gpt-5.6-luna extraction call
        ↓
preserve raw proposal + request metadata + usage
        ↓
deterministic local grounding
        ↓
canonical validation / fail closed
        ↓
structure detection
        ↓
semantic representation decision
        ↓
SPEC-038-compatible learner artifact when admitted/supported
```

Do not change implementation after seeing any result.

Do not change prompts after seeing any result.

Do not retry an unattractive, sparse, failed, or surprising output.

Do not add a renderer to make a recognized strategy visible.

Do not repair a semantic proposal to improve the evaluation.

## Failure policy

If a provider or deterministic validation stage fails for a source:

- preserve the complete failed attempt;
- make no retry;
- make no repair call;
- make no implementation change;
- continue only to the next already-approved frozen source.

If execution reveals a frozen-identity mismatch or experiment contamination, stop the entire run and report it as invalidated.

A fail-closed source is valid scientific evidence.

## Audit artifacts

Create a new isolated directory:

`examples/evaluations/spec-042-blind-out-of-sample-live-execution-20260911/`

Preserve per source at minimum:

- frozen source identity and SHA-256;
- exact transmitted text or immutable reference to the frozen packet;
- provider request ID;
- model/provider/prompt version;
- runtime;
- input/output/total token usage;
- raw extraction proposal;
- grounding resolution;
- rejected assertions/relationships where applicable;
- admitted KnowledgeModel or explicit failure state;
- detected structures;
- semantic representation decisions and decision evidence;
- renderer binding or explicit missing-renderer state;
- learner-facing artifact when available;
- complete run history proving zero retries.

Create aggregate `report.json` covering all three sources.

## Evaluation separation

Machine evaluation may report only objective integrity and pipeline outcomes, including:

- provider call count;
- grounding/admission result;
- entity/relationship/proposition counts;
- detected structures;
- selected representation strategies;
- renderer availability;
- fail-closed events;
- provenance completeness;
- deterministic/browser integrity.

Codex must **not** assign the final pedagogical/product verdict.

The owner will later judge whether the resulting representation made each unseen source easier to understand.

## Protected state

Do not modify:

- frozen SPEC-040 harness/compiler behavior;
- SPEC-041 source packet or live manifest;
- SPEC-038 learner-facing visual/interaction baseline;
- SPEC-039 semantic-to-representation compiler principles;
- semantic vocabulary;
- grounding/provenance contracts;
- fail-closed behavior;
- representation strategy rules;
- renderer coverage;
- My Map/navigation behavior;
- Explore Next semantics.

Known gaps remain legitimate:

- comparison renderer unavailable;
- worked-example capability unproven.

Do not close them during this packet.

## Validation after execution

Run the focused blind-execution validation and relevant regressions without altering the frozen implementation.

Verify at minimum:

```text
provider calls <= 3
provider calls == number of attempted frozen sources
one call maximum per source
execution order == frozen order
store == false
all retry classes == 0
source hashes match frozen packet
frozen implementation identity preserved
prompt/version preserved
no external retrieval/enrichment during execution
all provider request IDs and usage preserved
all failures/rejections preserved
no source-specific adaptation
SPEC-038 learner-facing baseline preserved
browser console clean for emitted learner artifacts
full offline suite passes
git diff --check passes
```

Do not rerun provider calls as part of validation.

## Completion state

After the single authorized execution:

- set SPEC-042 to `IMPLEMENTED_AWAITING_REVIEW`;
- set `STATUS.md` active packet to `NONE`;
- commit and push execution evidence according to repository protocol;
- stop for owner review;
- provide exact local viewer command(s) for learner-facing outputs that were actually admitted/renderable;
- provide path to aggregate report;
- do not promote a baseline;
- do not begin fixes or follow-up work.

## Owner review question

The primary owner question is:

> Given three genuinely unseen source passages and no adaptation after source selection, did Knowledge Compiler produce trustworthy representations that actually made the material easier to understand?

Review semantic fidelity, structural usefulness, representation appropriateness, and learning usefulness separately. A sparse or failed result may still demonstrate trustworthy fail-closed behavior even if it is not pedagogically useful.
