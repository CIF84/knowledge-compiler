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

The deterministic representation seam works and representation diversity should be preserved. Owner review found the right learning pane behaviorally incoherent because legacy navigation semantics remained mixed into explanatory representations: representation components could act as navigation, and `Explore deeper` duplicated the explicit `Explore Next` frontier.

## Explanatory-surface purification

`SPEC-035 — explanatory surface purification`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner observation: the separation of navigation, explanation, and recommendation is now materially clearer. My Map works as revealed territory; Explore Next works as the explicit future-learning frontier; legacy implicit navigation from the explanatory surface is no longer the main bottleneck. The remaining product gap is explanatory power: the right pane is cleaner but often too thin and less useful than the strongest earlier explanation experiments.

Accepted invariant:

> Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current product direction

The project keeps the cleaner responsibility model established by SPEC-033 through SPEC-035 while restoring the explanatory strength of earlier learning-surface experiments.

```text
MY MAP
→ revealed territory / deliberate navigation

WHAT DOES THIS MEAN?
→ dominant representation of the current knowledge object
→ local inspectable semantic components
→ grounded text for the inspected component/relationship

EXPLORE NEXT
→ explicit trusted frontier / forward learning

LEARNING HISTORY / BACK
→ traversal memory (deferred)
```

The focused learning surface must not equate explanation with either prose or diagrams. It should choose a representation because the representation fits the trusted semantic structure currently in focus.

```text
selected canonical object
        ↓
trusted local semantic structure
        ↓
representation strategy resolver
        ↓
learner-facing dominant representation
        ↓
representation-local inspection
        ↓
grounded explanatory detail
```

The active interaction invariant remains:

> Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.

The active representation principle remains:

> The compiler should choose the representation that minimizes the cognitive work required to understand the trusted structure currently in focus.

The current SPEC-036 experiment adds one further requirement:

> The explanatory surface needs a dominant representation with inspectable semantic components.

Representation strategy remains heterogeneous: causal/mechanism, process/sequence, hierarchy/composition, compare/contrast, worked example, focused relationship, concise prose, or another truthfully supported form.

## Current gate

SPEC-036 is implemented and awaiting owner review. No work packet is currently approved. The owner must review the fixed SPEC-036 browser artifact before any subjective verdict or follow-up implementation. Baseline promotion, live/model/external calls, and unrelated follow-up implementation remain unauthorized.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- prior SPEC evaluation artifacts;
- SPEC-030 role separation;
- SPEC-031 reciprocal/multi-edge semantic identity;
- current SPEC-033 canonical revealed-knowledge navigation implementation/candidate;
- SPEC-034 deterministic representation-strategy capability;
- SPEC-035 explanatory/navigation interaction isolation;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- source-bounded depth behavior;
- unrelated user work.

## Explicitly deferred

Do not yet implement:

- My Map visual redesign / folder-tree styling;
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

A later packet may separately test traversal-memory semantics and My Map visual grammar after explanatory power has been restored on the clean architecture.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
