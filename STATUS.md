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

## Current approved work packet

```text
specs/SPEC-040-blind-out-of-sample-evaluation-harness.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-040 is authorized to build and freeze the generic blind out-of-sample evaluation harness only.

The final blind source set must remain undisclosed during implementation. No live/model/external calls are authorized. SPEC-040 must stop after producing the frozen harness/compiler commit, dry-run evidence, and exact proposed live-execution plan.

The next gate, if owner/ChatGPT review confirms the harness is generic, will freeze a genuinely out-of-sample source set and separately authorize bounded live execution without modifying the frozen compiler/harness.

## Current product direction

The primary uncertainty is now generalization beyond the development corpus:

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

The blind experiment must distinguish semantic fidelity, structural usefulness, representation appropriateness, and owner-judged learner usefulness.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing visual/interaction baseline;
- SPEC-039 semantic-to-representation compiler behavior and accepted principles;
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

Do not yet implement:

- real blind-source execution;
- live/model/external calls;
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
