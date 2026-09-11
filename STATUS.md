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

The deterministic representation seam works and representation diversity should be preserved.

## Explanatory-surface purification

`SPEC-035 — explanatory surface purification`

Implementation status: `IMPLEMENTED_REVIEWED`

Accepted invariant:

> Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.

## Structure-aware explanatory surface

`SPEC-036 — structure-aware explanatory surface`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `EXPLANATORY_INTERACTION_RESTORED_VISUAL_GRAMMAR_NEXT`

Owner review confirms that SPEC-036 restored representation-local hover/click inspection and that this capability must be preserved.

## Visual semantic grammar

`SPEC-037 — visual semantic grammar`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `TERRITORY_GRAMMAR_CONFIRMED_EXPLANATORY_SPATIAL_ENCODING_REGRESSED`

Owner review confirms:

- My Map is materially improved by the quiet tree/territory grammar and should be preserved;
- the explanatory surface overcorrected away from generic cards and flattened structural representations toward typography;
- structural explanations became less visually distinctive and less immediately legible than the earlier diagram-rich candidates;
- representation-local hover/click inspection remains useful;
- representation diversity remains authoritative.

## Dominant explanatory diagram canvas

`SPEC-038 — dominant explanatory diagram canvas`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Owner review confirms that SPEC-038 materially restores explanatory richness while preserving the cleaner responsibility architecture. Structural representations again use a dominant diagram canvas where trusted semantics warrant it, representation diversity remains intact, local inspection remains non-navigational, and My Map retains the quieter territory/tree grammar.

SPEC-038 is the strongest learner-facing visual baseline so far. The four-surface responsibility model is now protected:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ represents the current idea using the fitting semantic representation

INSPECT / SELECTED / PREVIEW
→ explains components of that representation without changing learner location

EXPLORE NEXT
→ proposes future traversal
```

This is an architectural baseline, not a declaration that the UI is finished. Follow-up work must justify any change to these responsibility boundaries rather than casually redesigning them.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current product direction

The primary product uncertainty now moves below the interface: whether the compiler can reliably infer sufficient trusted semantic structure from arbitrary source material to select and populate these learner-facing representations without handcrafted fixture logic.

The learner-facing architecture remains:

```text
MY MAP
→ revealed territory / deliberate navigation
→ quiet tree / territory grammar

WHAT DOES THIS MEAN?
→ dominant representation of the current knowledge object
→ true spatial/diagrammatic composition for structural strategies
→ heterogeneous representation strategy when another form fits better
→ representation-local inspection only

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
source material
        ↓
extraction / normalization
        ↓
trusted semantic structure
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

The active visual principle remains:

> Explanation should not look like navigation, but semantic structure must still look like structure.

Representation strategy remains heterogeneous: causal/mechanism, process/sequence, hierarchy/composition, compare/contrast, worked example, focused relationship, concise prose, or another truthfully supported form.

## Current gate

SPEC-038 has passed owner review and establishes the current learner-facing visual baseline. There is no active approved implementation packet. The next packet should test compiler-side semantic-to-representation capability rather than perform another broad UI redesign. Live/model/external calls remain unauthorized until explicitly granted by an approved packet.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing visual/interaction architecture as the best-known current baseline;
- prior SPEC evaluation artifacts;
- SPEC-030 role separation;
- SPEC-031 reciprocal/multi-edge semantic identity;
- SPEC-033 canonical revealed-knowledge navigation behavior and data semantics;
- SPEC-034 deterministic representation-strategy capability;
- SPEC-035 explanatory/navigation interaction isolation;
- SPEC-036 representation-local hover/click inspection semantics;
- SPEC-037 My Map quiet tree/territory visual grammar;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- source-bounded depth behavior;
- unrelated user work.

## Explicitly deferred

Do not yet implement:

- Back / learner traversal history;
- traversal persistence or history UI;
- breadcrumbs as a substitute for traversal history;
- personalization or learner-state modeling;
- quizzes/mastery;
- guided pathways/courses;
- automatic analogy generation;
- broad navigation architecture redesign;
- universal graph viewer;
- decorative animation as a product goal.

A later packet may separately test traversal-memory semantics after compiler-side representation intelligence is validated.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
