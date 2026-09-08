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

Formal debrief/promotion remains separate. Follow-up work must preserve the current SPEC-033 implementation/candidate state and must not redesign navigation semantics.

## Representation-strategy candidate

`SPEC-034 — representation strategy grammar`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `CAPABILITY_CONFIRMED_SURFACE_NEEDS_PURIFICATION`

The deterministic representation seam works and representation diversity should be preserved. Owner review found the right learning pane behaviorally incoherent because legacy navigation semantics remained mixed into explanatory representations: representation components could act as navigation, and `Explore deeper` duplicated the explicit `Explore Next` frontier.

## Explanatory-surface purification

`SPEC-035 — explanatory surface purification`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner observation: the separation of navigation, explanation, and recommendation is materially clearer. My Map works as revealed territory; Explore Next works as the explicit future-learning frontier; legacy implicit navigation from the explanatory surface is no longer the main bottleneck.

Accepted invariant:

> Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.

## Structure-aware explanatory surface

`SPEC-036 — structure-aware explanatory surface`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `EXPLANATORY_INTERACTION_RESTORED_VISUAL_GRAMMAR_NEXT`

Owner review confirms that SPEC-036 restored important explanatory capability on the cleaner architecture:

- concepts and relationships in the explanatory pane are locally inspectable again;
- hover/click interaction feels materially better and should be preserved;
- explanatory interaction remains separate from learner navigation;
- representation diversity remains the correct architectural direction.

The remaining dominant issue is visual-semantic ambiguity rather than interaction mechanics. Too many learner-facing objects still use the same bordered-card / pill / button-like grammar across My Map and the explanatory surface. This makes territory, semantic objects, relationships, recommendations, and actual controls look too similar and makes the interface visually repetitive.

Owner also flagged learner-facing remnants such as `Trusted relationships` that may duplicate the dominant representation without providing active explanatory value.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current product direction

The project keeps the clean responsibility model established by SPEC-033 through SPEC-036 while making visual form communicate semantic role.

```text
MY MAP
→ revealed territory / deliberate navigation
→ quiet tree / territory grammar

WHAT DOES THIS MEAN?
→ dominant representation of the current knowledge object
→ representation-specific visual grammar
→ local inspectable semantic components

INSPECT / SELECTED / PREVIEW
→ grounded text for the inspected component/relationship

EXPLORE NEXT
→ explicit trusted frontier / forward learning
→ intentionally actionable recommendation grammar

LEARNING HISTORY / BACK
→ traversal memory (deferred)
```

The explanatory surface must not equate explanation with either prose or diagrams. It should choose a representation because the representation fits the trusted semantic structure currently in focus.

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

SPEC-037 adds the visual principle:

> Visual form should communicate semantic role.

A concept, relationship, region, recommendation, inspection state, and actual control should not all look like variants of the same button.

Representation strategy remains heterogeneous: causal/mechanism, process/sequence, hierarchy/composition, compare/contrast, worked example, focused relationship, concise prose, or another truthfully supported form.

## Current gate

SPEC-037 is implemented and awaiting owner review. There is no active approved implementation packet. Baseline promotion, live/model/external calls, and unrelated follow-up implementation remain unauthorized.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- prior SPEC evaluation artifacts;
- SPEC-030 role separation;
- SPEC-031 reciprocal/multi-edge semantic identity;
- SPEC-033 canonical revealed-knowledge navigation behavior and data semantics;
- SPEC-034 deterministic representation-strategy capability;
- SPEC-035 explanatory/navigation interaction isolation;
- SPEC-036 representation-local hover/click inspection semantics;
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
- broad navigation architecture redesign;
- universal final renderer;
- decorative animation as a product goal.

My Map visual grammar is no longer deferred: SPEC-037 explicitly authorizes visual tree/territory restyling while freezing its revealed-knowledge data model and navigation behavior.

A later packet may separately test traversal-memory semantics after the learner-facing semantic grammar is stable.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
