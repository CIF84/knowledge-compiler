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

Owner/ChatGPT reviewed the exact three-source packet and call manifest and approved exactly those frozen passages for the bounded live run. No adaptation after source selection is permitted.

Frozen packet SHA-256:

`ccf1c5e9fb607934f790eb06cd828bf5a1d42e4f6e4d7913722debc4269c72b0`

Frozen live-manifest SHA-256:

`f45c8797b94a0a5d6a1902aa50b71a63af6277dfcf1e6956a2d2d1107339d075`

## Blind out-of-sample live execution

`SPEC-042 — blind out-of-sample live execution`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Owner verdict: `PENDING`

Recorded objective result:

- exactly three approved `gpt-5.6-luna` Responses API calls executed in frozen source order;
- `store=False`; SDK, hidden, semantic, repair, and follow-up retries/calls all remained zero;
- geology failed closed because a relationship referenced an undeclared entity;
- meteorology failed closed because typed propositions referenced undeclared entities;
- civics admitted 20 entities, 10 relationships, 3 detected structures, and 30 representation decisions;
- no source, prompt, compiler, semantic, representation, renderer, or evaluation adaptation occurred;
- the final pedagogical/product verdict remains reserved for owner review.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-042 is implemented and awaiting owner review. The single authorized run is complete,
and its immutable evidence is under
`examples/evaluations/spec-042-blind-out-of-sample-live-execution-20260911/`.

No packet is active. No retry, repair, follow-up model call, implementation change, or
promotion is authorized. Owner review must assess semantic fidelity, structural usefulness,
representation appropriateness, and learning usefulness separately.

## Current product direction

The active uncertainty is genuine out-of-sample generalization:

```text
three frozen unseen source passages
        ↓
exactly one extraction call each
        ↓
deterministic grounding + canonical validation
        ↓
trusted semantic structure or fail closed
        ↓
semantic representation decision
        ↓
protected SPEC-038 learner-facing representation when supported
        ↓
owner judges learning usefulness
```

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing visual/interaction baseline;
- SPEC-039 semantic-to-representation compiler behavior and accepted principles;
- SPEC-040 frozen harness/compiler identity `5622df131dc71346d5890f42ce16fe1e3e55f33a`;
- SPEC-041 exact source packet and live-execution manifest;
- SPEC-042 complete three-call run history and admitted/failed-closed outcomes;
- all three exact source passage hashes;
- prompt `spec-010-v1`;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- representation strategy rules and current renderer coverage;
- SPEC-033 navigation semantics;
- SPEC-034 representation diversity;
- SPEC-035 explanation/navigation isolation;
- SPEC-036 local inspection semantics;
- SPEC-037 quiet My Map grammar;
- unrelated user work.

## Explicitly deferred / forbidden during this packet

Do not:

- retry a provider result;
- repair a provider result;
- substitute or edit a source;
- retrieve external enrichment;
- modify compiler/harness/prompt after seeing source output;
- complete the comparison renderer;
- add worked-example capability;
- implement Back/history;
- add personalization, quizzes, mastery, or guided courses;
- redesign navigation or the learner-facing baseline;
- promote the result or assign the subjective owner verdict.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
