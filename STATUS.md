# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. It points to the active approved work packet; agents must not infer active work from filename recency.

## Current accepted learner-navigation baseline

`BASELINE-004 — learner navigation workspace`

BASELINE-001 through BASELINE-004 remain preserved historical/accepted states and must not be modified by ordinary implementation work.

## Best-known focused-learning candidate

`SPEC-030 — distinct learning surface representation`

Owner verdict: `ROLE_SEPARATION_CONFIRMED`

Accepted invariant:

```text
MY MAP
→ navigate revealed knowledge

WHAT DOES THIS MEAN?
→ translate selected knowledge for understanding

EXPLORE NEXT
→ reveal trusted frontier
```

## Owner review of current revealed-navigation candidate

`SPEC-033 — canonical revealed-knowledge tree`

Owner observation: implementation behaves as intended in the reviewed navigation flows and is the strongest navigation architecture so far. The revealed, deduplicated, collapsible tree is sufficient to stop treating navigation as the primary product bottleneck.

Formal debrief/promotion remains separate. Follow-up work must preserve the current SPEC-033 implementation/candidate state and must not redesign navigation.

## Representation-strategy candidate

`SPEC-034 — representation strategy grammar`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `CAPABILITY_CONFIRMED_SURFACE_NEEDS_PURIFICATION`

The deterministic representation seam works and representation diversity should be preserved. Owner review found the right learning pane behaviorally incoherent because legacy navigation semantics remained mixed into explanatory representations: representation components could act as navigation, and `Explore deeper` duplicated the explicit `Explore Next` frontier. SPEC-035 is the approved narrow follow-up to remove those navigation semantics without discarding SPEC-034 representation capability.

## Explanatory-surface candidate

`SPEC-035 — explanatory surface purification`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Machine and browser gates: `PASS`

The candidate composes the exact SPEC-034 runtime with a narrow interaction layer. Representation components now own only local highlight state, the old explanatory-pane depth control is inactive, the existing Explore Next surface admits the committed deeper model, and My Map remains the authority for returning to revealed knowledge. The product verdict remains pending owner review.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current product direction

The project returns to a strict separation of learning responsibilities:

```text
MY MAP
→ revealed territory / deliberate navigation

WHAT DOES THIS MEAN?
→ representation of the current knowledge object for understanding

EXPLORE NEXT
→ explicit trusted frontier / forward learning
```

The focused learning surface must not equate explanation with either prose or diagrams. It should choose a representation because the representation fits the trusted semantic structure currently in focus.

```text
selected canonical object
        ↓
trusted local semantic structure
        ↓
representation strategy resolver
        ↓
learner-facing representation
```

Candidate forms include causal/mechanism, process/sequence, hierarchy/composition, compare/contrast, worked example, focused relationship, and concise prose fallback.

The active interaction invariant is:

> Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.

The active representation principle remains:

> The compiler should choose the representation that minimizes the cognitive work required to understand the trusted structure currently in focus.

## Current gate

No implementation packet is active. SPEC-035 is implemented with offline machine and browser gates passing and awaits owner review. Baseline promotion, live/model/external calls, and unrelated follow-up implementation remain unauthorized.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- prior SPEC evaluation artifacts;
- SPEC-030 role separation;
- SPEC-031 reciprocal/multi-edge semantic identity;
- current SPEC-033 canonical revealed-knowledge navigation implementation/candidate;
- SPEC-034 deterministic representation-strategy capability;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- source-bounded depth behavior;
- unrelated user work.

## Explicitly deferred

Do not yet implement:

- Back / learner traversal history;
- traversal persistence or history UI;
- breadcrumbs as a substitute for traversal history;
- live/model-generated pedagogy;
- personalization or learner-state modeling;
- quizzes/mastery;
- guided pathways/courses;
- automatic analogy generation;
- broad navigation redesign;
- universal final renderer.

A later packet may test learning-history semantics and, separately, model-assisted explanatory generation only after the deterministic representation seam and purified learning-surface interaction demonstrate value.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
