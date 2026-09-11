# SPEC-038 — Dominant Explanatory Diagram Canvas

Status: `IMPLEMENTED_REVIEWED`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW_PASSED`
Promotion: `ACCEPTED_AS_CURRENT_VISUAL_BASELINE`

## Purpose

Preserve the cleaner responsibility architecture established by SPEC-033 through SPEC-037 while restoring the spatial explanatory power that earlier learner-facing candidates demonstrated exceptionally well.

## Owner review verdict

`NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Owner review confirms that SPEC-038 materially restored the diagram canvas for structural representations while maintaining representation diversity and the newer My Map territory/tree navigation.

Accepted responsibility model:

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

Accepted interaction invariant:

> Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.

Accepted representation principle:

> The compiler should choose the representation that minimizes the cognitive work required to understand the trusted structure currently in focus.

Accepted visual principle:

> Explanation should not look like navigation, but semantic structure must still look like structure.

## Review observations

The reviewed implementation establishes the strongest learner-facing visual baseline so far:

- My Map remains a quiet, directory/tree-like representation of revealed territory.
- Structural explanations again have a visually dominant diagram canvas.
- Economics can read as a causal/system model rather than repeated rows.
- reciprocal electromagnetism can read as a reciprocal mechanism.
- History of Printing can read as dependency/enablement structure.
- focused relationships can remain deliberately sparse when the trusted structure is sparse.
- representation-local hover/click inspection remains useful and non-navigational.
- representation diversity remains authoritative; prose-first knowledge is not forced into a graph.

This acceptance freezes the responsibility architecture, not every pixel or renderer detail. Future work must justify changes to the four-surface model rather than casually redesigning it.

## What this packet established

For knowledge whose meaning is inherently structural, the dominant explanatory representation can behave like a real diagram canvas: semantic objects occupy space, relationships connect them visibly, topology carries meaning, and local hover/click inspection remains available without reintroducing navigation into the explanatory surface.

Representation strategy remains heterogeneous:

```text
causal / mechanism
→ causal or system diagram

hierarchy / composition
→ hierarchy / composition diagram

process / sequence
→ ordered sequence / timeline / flow

focused relationship
→ spatial source–relationship–target representation

compare / contrast
→ aligned comparison structure

worked example
→ rule-to-instance / transformation representation

spatial knowledge
→ spatial representation

argument / proposition
→ argument / objection structure where supported

thin or inherently verbal knowledge
→ concise prose
```

## Preserved constraints

- SPEC-033 canonical revealed-knowledge navigation behavior and data semantics;
- SPEC-034 representation-strategy resolver and diversity;
- SPEC-035 explanatory/navigation isolation;
- SPEC-036 representation-local hover/click inspection semantics;
- SPEC-037 quiet My Map tree/territory grammar;
- trusted semantic vocabulary;
- grounding and provenance;
- fail-closed behavior;
- source-bounded depth behavior;
- Explore Next as the explicit forward-learning mechanism.

## Deferred

This packet does not implement:

- Back / learner traversal history;
- traversal persistence or history UI;
- breadcrumbs as traversal history;
- personalization or learner-state modeling;
- quizzes/mastery;
- guided pathways/courses;
- automatic analogy generation;
- broad navigation redesign;
- universal graph viewer;
- decorative animation as a product goal.

## Next product uncertainty

The dominant uncertainty now moves below the interface:

> Can the compiler reliably infer enough trusted semantic structure from arbitrary source material to select and populate the appropriate representation strategy without handcrafted fixture logic?

The next experiment should therefore test the source-material → semantic-structure → representation-strategy seam while preserving this accepted learner-facing baseline.
