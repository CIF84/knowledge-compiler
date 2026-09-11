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

Accepted findings:

- generic harness/compiler frozen at `5622df131dc71346d5890f42ce16fe1e3e55f33a`;
- blind sources remained absent during implementation;
- anti-overfitting and source-identity invariance checks passed;
- dry-run and SPEC-038 browser regressions passed;
- no live/model/external execution occurred;
- the next gate may freeze the exact blind source set, but transmission to OpenAI remains separately gated.

## Current approved work packet

```text
specs/SPEC-041-blind-source-set-freeze.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-041 is authorized only to retrieve public source material needed to select and freeze the exact three-source blind packet.

Allowed external activity is limited to ordinary public HTTPS retrieval/search/navigation for source selection and capture. No OpenAI Responses API call, LLM/model/provider call, semantic extraction, or blind-run execution is authorized.

SPEC-041 must preserve the frozen SPEC-040 harness/compiler identity and stop after committing/pushing the exact source packet, hashes, provenance, and proposed three-call execution manifest. Owner/ChatGPT review is required before any source text may be transmitted to OpenAI.

## Current product direction

The primary uncertainty is generalization beyond the development corpus:

```text
previously unseen source material
        ↓
semantic extraction + grounding
        ↓
trusted semantic structure
        ↓
semantic representation decision
        ↓
SPEC-038 learner-facing representation
```

The experimental order is protected:

```text
frozen compiler + harness
        ↓
freeze three out-of-sample sources
        ↓
owner approves exact transmitted packet
        ↓
exactly three bounded model calls
        ↓
no implementation adaptation
        ↓
owner reviews learner-facing outputs
```

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing visual/interaction baseline;
- SPEC-039 semantic-to-representation compiler behavior and accepted principles;
- SPEC-040 frozen harness/compiler identity `5622df131dc71346d5890f42ce16fe1e3e55f33a`;
- SPEC-033 navigation semantics;
- SPEC-034 representation diversity;
- SPEC-035 explanation/navigation isolation;
- SPEC-036 local inspection semantics;
- SPEC-037 quiet My Map grammar;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- source-bounded depth behavior;
- known renderer/corpus coverage gaps from SPEC-039;
- unrelated user work.

## Explicitly deferred

Do not yet implement or execute:

- OpenAI/model semantic extraction of blind sources;
- any blind-run provider call;
- source-specific compiler/prompt/semantic/renderer adaptation;
- comparison renderer completion;
- worked-example feature work;
- Back / learner traversal history;
- traversal persistence/history UI;
- personalization/learner-state modeling;
- quizzes/mastery;
- guided courses/pathways;
- broad navigation redesign;
- universal graph viewer;
- decorative animation as a product goal.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
