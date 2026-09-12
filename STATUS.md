# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected four-surface model:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ represents the current idea using the fitting semantic representation

INSPECT / SELECTED / PREVIEW
→ explains representation-local semantic components without changing learner location

EXPLORE NEXT
→ proposes future traversal
```

SPEC-038 is an architectural/visual baseline, not a declaration that every renderer family is complete.

## Semantic-to-representation compiler

`SPEC-039 — semantic-to-representation compiler gate`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `SEMANTIC_REPRESENTATION_COMPILER_CONFIRMED_WITH_COVERAGE_GAPS`

Accepted findings:

- representation strategy is compiler output rather than fixture/UI logic;
- strategy selection follows trusted semantic structure rather than domain/label/source identity;
- insufficient structure fails closed;
- renderer coverage may lag semantic recognition without invalidating the semantic decision;
- compare/contrast recognition is demonstrated but SPEC-038 lacks a comparison renderer;
- worked-example / rule-to-instance capability remains unproven because the committed corpus lacks a grounded case.

## Blind evaluation harness

`SPEC-040 — blind out-of-sample evaluation harness`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `GENERIC_HARNESS_CONFIRMED_SOURCE_FREEZE_NEXT`

Frozen harness/compiler identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Blind source set freeze

`SPEC-041 — blind source set freeze`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `BLIND_SOURCE_SET_APPROVED_FOR_EXACT_TRANSMISSION`

Frozen packet SHA-256:

`ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0`

Frozen live-manifest SHA-256:

`f45c8797b94a0a5d6a1902aa50b71a63af6277dfcf1e6956a2d2d1107339d075`

## Blind out-of-sample live execution

`SPEC-042 — blind out-of-sample live execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DIAGNOSIS`

Owner verdict: `FAILURES_REQUIRE_DIAGNOSIS_NO_REPAIR_AUTHORIZED`

Recorded objective result:

- exactly three approved `gpt-5.6-luna` Responses API calls executed in frozen source order;
- geology failed closed on undeclared `spreading-processes`;
- meteorology failed closed on undeclared `jet-stream-weather-transport` and `average-temperature-difference`;
- civics passed deterministic admission and produced semantic/representation output;
- frozen behavior remained unchanged throughout the run.

## Blind failure diagnosis

`SPEC-043 — blind failure diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `DIAGNOSIS_CONFIRMED_NO_CONTRACT_CHANGE_REPLICATION_REQUIRED`

Accepted findings:

- 2 rejected objects are `EXTRACTION_GRANULARITY` failures: source-supported process/event identities were used without corresponding entity declarations;
- 1 rejected object is a genuine `MODEL_ERROR`: `average-temperature-difference` was unsupported by the source;
- 0 `CONTRACT_GAP`;
- 0 `VALIDATION_BUG`;
- 0 `AMBIGUOUS`;
- strict declared-identity validation behaved correctly and remains protected;
- the current sample is insufficient to justify changing the semantic contract;
- the correct next experiment is blind replication before repair.

Canonical evidence:

`examples/evaluations/spec-043-blind-failure-diagnosis-20260911/report.json`

## Blind replication source set freeze

`SPEC-044 — blind replication source set freeze`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Owner verdict: `PENDING`

Recorded objective result:

- six unrelated U.S. federal sources were selected in the predeclared domain order;
- each exact explanatory passage is 300–650 words and is frozen with retrieval provenance and SHA-256 identity;
- repository contamination checks found no prior URL, title, source ID, passage hash, or exact passage occurrence;
- the later six-call manifest freezes one `gpt-5.6-luna` Responses API call per source, `store=False`, and zero SDK, semantic, repair, hidden, or follow-up retries/calls;
- source transmission remains unauthorized pending a later canonical owner-approved execution packet;
- SPEC-044 made zero provider/model calls and performed no semantic extraction or protected implementation change.

Frozen packet SHA-256:

`85f7a7be47fa827799d532ab7ca5edc03b359162894dc2ee4e72a750de28e52b`

Frozen live-manifest SHA-256:

`beaf3df4a941afc7fadf2abf13543affeae798e3d14486798cbb0060fccdc57e`

Canonical evidence:

`examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-044 is implemented and awaiting owner review. Its canonical evidence is
`examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/report.json`.

No packet is active. No provider/model call, source transmission, semantic extraction,
repair, retry, semantic adaptation, semantic-contract change, or product promotion is
authorized.

## Current product direction

The present uncertainty is whether the SPEC-043 extraction-granularity pattern is systematic or incidental:

```text
frozen semantic/compiler behavior
        ↓
6 new unrelated blind sources frozen exactly
        ↓
OWNER REVIEW
        ↓
later bounded execution packet, if separately approved
        ↓
SPEC-043 taxonomy applied unchanged
        ↓
decide whether any narrow repair experiment is justified
```

The immediate goal is owner review of the frozen replication sample, not execution or improving pass rate.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing visual/interaction baseline;
- SPEC-039 semantic-to-representation compiler behavior and accepted principles;
- SPEC-040 frozen harness/compiler identity `5622df131dc71346d5890f42ce16fe1e3e55f33a`;
- SPEC-041 exact source packet and live-execution manifest;
- SPEC-042 complete three-call run history and admitted/failed-closed outcomes;
- all exact SPEC-041/042 source passage hashes and raw provider responses/provenance;
- SPEC-043 rejection reconstruction, taxonomy, and accepted diagnosis;
- SPEC-044 six-source packet, fixed order, exact passages, source hashes, later execution manifest, frozen taxonomy, and decision framework;
- prompt `spec-010-v1`;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- declared-identity invariant;
- representation strategy rules and current renderer coverage;
- SPEC-033 navigation semantics;
- SPEC-034 representation diversity;
- SPEC-035 explanation/navigation isolation;
- SPEC-036 local inspection semantics;
- SPEC-037 quiet My Map grammar;
- unrelated user work.

## Explicitly forbidden pending owner review

Do not:

- call OpenAI or any other model/provider;
- transmit selected source text to a model;
- perform semantic extraction on selected sources;
- retry or repair provider/model output;
- modify extraction outputs;
- add or normalize missing entities;
- modify prompt `spec-010-v1`;
- modify extraction schema;
- modify canonical semantic vocabulary or validation behavior;
- weaken declared-identity validation;
- modify SPEC-039 strategy selection or renderer behavior;
- complete comparison/worked-example renderer coverage;
- redesign navigation or the learner-facing baseline;
- implement Back/history;
- add personalization, quizzes, mastery, or guided courses;
- assign expected semantic answers to the six blind sources;
- choose sources for attractive expected output;
- execute the later six-call manifest;
- promote the product or assign a final architectural verdict.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
