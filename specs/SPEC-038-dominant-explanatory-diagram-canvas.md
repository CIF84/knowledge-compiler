# SPEC-038 — Dominant Explanatory Diagram Canvas

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Preserve the cleaner responsibility architecture established by SPEC-033 through SPEC-037 while restoring the spatial explanatory power that earlier learner-facing candidates demonstrated exceptionally well.

Owner review of SPEC-037 confirms one clear success and one clear failure:

- **My Map improved materially.** The quiet tree/territory grammar is cleaner, visually distinct, and should be preserved.
- **The explanatory surface did not improve enough.** Removing generic boxes solved button ambiguity by flattening many structural representations into typography. The result is less ambiguous but also less visual, less immediately legible, and less engaging.

SPEC-038 therefore tests a narrower proposition:

> For knowledge whose meaning is inherently structural, the dominant explanatory representation should again behave like a real diagram canvas: semantic objects occupy space, relationships connect them visibly, topology carries meaning, and local hover/click inspection remains available — without reintroducing navigation into the explanatory surface.

This packet is not a return to the old navigation architecture. It combines the strongest explanatory qualities of the earlier diagram-rich UI with the cleaner responsibility model now established.

## Owner verdict entering this packet

SPEC-037 review verdict:

`TERRITORY_GRAMMAR_CONFIRMED_EXPLANATORY_SPATIAL_ENCODING_REGRESSED`

Owner observations:

- My Map now reads more clearly as navigation/territory and should not be redesigned.
- The right pane now overcorrects away from cards: instead of everything looking like buttons, too much looks like text.
- Earlier explanatory diagrams were visually distinctive, immediately attention-catching, and substantially better at translating abstract structure.
- Local hover/click inspection restored by SPEC-036 remains valuable and must survive.
- The representation-strategy principle remains authoritative: not every explanation should become a diagram.

## Guiding principles

### 1. Explanation should not look like navigation, but semantic structure must still look like structure.

Removing borders is not equivalent to creating a diagram.

### 2. Spatial encoding is explanatory information.

Where trusted semantics describe topology, direction, hierarchy, sequence, composition, or mechanism, the learner should be able to perceive much of that structure before reading every label.

### 3. The representation strategy remains heterogeneous.

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

Do not turn this packet into “everything is a graph.”

### 4. Interaction remains inspection-only inside explanation.

> Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.

Hover and click may alter only representation-local inspection state.

## Responsibility model to preserve

```text
MY MAP
→ remembers revealed territory
→ deliberate navigation among already revealed knowledge
→ preserve SPEC-037 quiet tree grammar

WHAT DOES THIS MEAN?
→ dominant representation of the current idea
→ restore strong spatial/diagrammatic encoding where strategy warrants it
→ local semantic inspection only

PREVIEW / SELECTED / INSPECT
→ grounded text for the semantic object or relationship being inspected

EXPLORE NEXT
→ explicit trusted frontier / forward traversal

LEARNING HISTORY / BACK
→ deferred
```

## Primary uncertainty

> Can we restore the explanatory power and visual distinctiveness of true diagrams on top of the current clean architecture, while preserving representation diversity and keeping explanatory interaction completely separate from navigation?

## Preserve SPEC-037 My Map

The My Map visual direction is accepted for this experiment.

Do not redesign it.

Preserve:

- quiet tree/directory-like territory grammar;
- indentation and branch cues;
- current-focus treatment;
- revealed-object semantics;
- collapse/expand behavior;
- deliberate navigation behavior;
- deduplication;
- all SPEC-033 navigation invariants.

Minor fixes required for implementation compatibility are allowed only if they do not materially alter the reviewed visual grammar.

## Dominant explanatory canvas

For structural representation strategies, `WHAT DOES THIS MEAN?` should contain a visually dominant explanatory canvas rather than a thin row of text fragments.

The canvas should use:

- meaningful 2D placement;
- visible semantic objects;
- visible connectors/edges where relationships exist;
- arrows/direction where direction is canonical and meaningful;
- spacing and grouping as semantic encodings;
- enough whitespace for topology to be perceived;
- selective visual emphasis for current/hovered/selected objects;
- labels integrated into the diagram rather than rendered as unrelated UI pills;
- representation-specific composition rather than a universal card row.

A semantic node may be rectangular when that is an appropriate diagram primitive. A rectangle inside a spatial diagram is not an action button merely because it has a boundary.

The distinction must come from composition and behavior:

```text
diagram object
→ participates in topology
→ connected spatially to other semantic objects
→ inspectable locally
→ does not navigate

Explore Next item
→ explicitly actionable
→ initiates future traversal/reveal
```

## Visual dominance

The dominant representation should receive space proportional to its explanatory role.

Current SPEC-037 structural representations are often compressed into a narrow horizontal strip even when the right pane has substantial unused space.

For genuinely structural cases, allow the diagram to occupy a substantial portion of the visible explanatory surface when doing so improves comprehension.

Do not impose a fixed percentage or artificial minimum height. The renderer should remain content-sensitive:

- sparse one-edge structures stay compact enough to avoid theatrical emptiness;
- multi-object systems receive enough room for their topology to become legible;
- hierarchy and composition receive vertical depth where appropriate;
- process receives directional progression;
- prose remains prose and should not receive an empty diagram canvas.

## Representation-local interaction

Preserve SPEC-036 semantics:

```text
hover semantic object / relationship
→ preview it
→ visually emphasize it and the relevant local structure

click semantic object / relationship
→ pin it as selected
→ keep grounded detail in the inspection section

clear inspection
→ return to focus-level explanatory state
```

Interaction should exploit the diagram rather than merely tint text.

Where useful and semantically truthful, hover/selection may:

- emphasize the selected node;
- emphasize directly relevant connectors;
- fade unrelated structure;
- emphasize relationship direction;
- reveal a concise local label.

It must not:

- change current learning focus;
- reveal new territory;
- add My Map nodes;
- trigger Explore Next;
- open deeper knowledge;
- mutate traversal state.

## Inspection layer

The inspection section remains below the dominant representation.

Its job is textual grounding, not a second visualization.

Use it for:

- concept description;
- relationship meaning;
- canonical predicate/direction where relevant;
- exact source evidence;
- provenance.

Hover should produce `PREVIEW`; click should produce `SELECTED` (or equivalent existing vocabulary). Do not invent additional navigation semantics.

The inspection section should remain visually subordinate to the dominant representation.

## Evidence and engineering notices

Evidence/provenance remains required and reachable but visually secondary.

Engineering/debug-like notices must not compete with the lesson.

The current learner-facing `Sparse structure: this view contains only one supported relationship.` treatment is specifically in scope for demotion.

If the information is useful to preserve:

- make it visually quiet;
- place it with secondary metadata/evidence;
- or omit it from the primary learner surface if it provides no learner value and the underlying state remains available internally.

Do not remove fail-closed behavior or invent structure to make a diagram richer.

Sparse trusted structure must remain sparse.

## Fixed evaluation cases

### 1. Electromagnetism — double-slit experiment

Use the canonical relationship:

```text
double-slit experiment
        ↓ CAUSES
interference pattern
```

Expected:

- visually reads as a causal mechanism, not a sentence spread horizontally across the page;
- source and target have clear objecthood;
- CAUSES is visually connective;
- direction is immediately legible;
- hover/click on source, relationship, and target update only local inspection;
- selection can emphasize the relevant path without navigation;
- Explore Next remains separate.

### 2. Electromagnetism — focused canonical relationship

Expected:

- source, predicate, and target form one coherent spatial relationship;
- predicate reads as the connection, not a third independent text/card object;
- canonical direction is unmistakable;
- all three semantic parts remain inspectable where supported;
- local interaction does not navigate.

### 3. Electromagnetism — Light / Electromagnetic wave

Expected:

- hierarchy/type-membership is visually encoded as hierarchy rather than a flat sentence;
- sparse structure remains appropriately compact;
- direction/type semantics remain truthful;
- local inspection works.

### 4. Software Architecture — modular order-processing service

Expected:

- composition reads as actual architecture/hierarchy;
- parent service and API/order/payment/database components occupy meaningful structural positions;
- PART OF relationships are spatially legible;
- the result should not look like a row of text columns;
- components and relationships remain locally inspectable;
- only canonical trusted relationships are shown.

### 5. History of Printing

Expected:

- use the selected representation strategy actually warranted by the trusted fixture;
- process/sequence/enablement should visually differ from causal and hierarchy representations;
- order or enablement should be perceivable spatially;
- do not invent missing steps or causal claims;
- local inspection remains grounded.

### 6. Economics

Expected:

- causal/mechanism structure should read as a system rather than repeated textual rows;
- multiple relationships should form a coherent spatial model when the trusted graph supports it;
- do not imply a closed feedback loop unless the canonical relationships actually close one;
- hover/selection should help isolate local paths without changing focus.

### 7. Concise prose fallback

Expected:

- remains intentionally prose-first;
- no gratuitous nodes, edges, empty canvas, or decorative graph is introduced;
- representation diversity is therefore visually obvious.

## Required implementation work

1. Inspect current SPEC-037 implementation and earlier committed diagram-rich explanatory implementations/artifacts for reusable rendering/interaction ideas. Do not restore old navigation coupling.
2. Preserve SPEC-037 My Map visual grammar and all SPEC-033 navigation semantics.
3. Preserve SPEC-034 representation-strategy resolver and heterogeneous strategy selection.
4. Preserve SPEC-035 explanatory/navigation isolation.
5. Preserve SPEC-036 hover/click local inspection semantics.
6. Introduce or restore a true dominant diagram canvas for structural strategies rather than representing structure primarily as styled text rows.
7. Give each structural strategy its own truthful spatial composition: causal/mechanism, hierarchy/composition, focused relationship, process/sequence, and any already-supported comparison/worked-example strategy.
8. Ensure semantic objects have clear visual objecthood without becoming navigation controls.
9. Ensure relationships are visibly connective and directional/ordered where canonical semantics require it.
10. Make diagram-local hover/click states visually meaningful and synchronized with Preview/Selected detail.
11. Keep Explore Next as the sole explicit forward-learning mechanism in the explanatory pane.
12. Demote/remove learner-facing engineering notices that compete with the dominant explanation, including the current sparse-structure banner where safe.
13. Keep evidence/provenance available, correct, and subordinate.
14. Do not fabricate additional nodes/edges to improve composition.
15. Add/update browser tests for diagram interaction, representation-local state, and navigation isolation.
16. Produce an isolated SPEC-038 browser evaluation artifact and durable report.

## Acceptance cases

### A. Structural representations are diagrams again

Expected: a reviewer can understand that causal, hierarchy, composition, sequence, and focused-relationship views are spatial semantic representations before reading all labels.

### B. Diagram objecthood is restored without button ambiguity

Expected: semantic objects look like objects in a diagram; Explore Next items and actual controls still look like actions.

### C. Spatial encoding carries meaning

Expected: direction, hierarchy, order, grouping, and connection are communicated through layout/geometry rather than primarily through prose.

### D. Representation diversity survives

Expected: structural cases use appropriate diagrammatic forms while concise prose and other non-spatial strategies remain non-diagrammatic.

### E. Local inspection survives

Expected: hover/click on diagram components updates Preview/Selected and visual emphasis without mutating learner location or revealed territory.

### F. My Map remains stable

Expected: SPEC-037 quiet tree grammar and SPEC-033 navigation behavior are materially unchanged.

### G. Explore Next remains the forward-traversal authority

Expected: no diagram component, inspection component, evidence component, or legacy `Explore deeper` affordance performs forward navigation.

### H. Sparse structure is truthful

Expected: sparse graphs are not padded with invented semantics; engineering notices do not dominate the learner surface.

### I. Evidence remains grounded

Expected: exact source evidence and provenance remain available and correct for inspected semantic components/relationships.

### J. Visual hierarchy improves

Expected: in structural cases the learner's attention is drawn first to the explanatory representation, then to inspected detail, then to future traversal controls.

## Machine acceptance

Before owner review verify:

```text
control plane valid
OFFLINE_ONLY respected
no live/model/external calls
trusted semantic vocabulary unchanged
grounding/provenance unchanged
fail-closed behavior unchanged
SPEC-033 navigation semantics preserved
SPEC-034 representation resolver preserved
SPEC-035 navigation/explanation isolation preserved
SPEC-036 local inspection semantics preserved
SPEC-037 My Map visual grammar materially preserved
no active Explore deeper affordance
Explore Next remains sole forward-learning mechanism
representation-local hover/click cannot mutate current_learning_focus
representation-local hover/click cannot mutate revealed_knowledge
representation-local hover/click cannot reveal new knowledge
structural strategies render materially spatial compositions
focused relationship preserves canonical direction
hierarchy/composition preserves canonical membership direction
process/sequence does not invent order beyond trusted semantics
causal/mechanism does not invent missing causal edges
concise prose fallback remains valid
browser console clean
full offline suite passes
git diff --check passes
```

## Browser review artifact

Create:

```text
examples/evaluations/spec-038-dominant-explanatory-diagram-canvas-<date>/
```

Include deterministic review cases for:

- My Map mixed revealed territory;
- double-slit causal mechanism;
- double-slit focused relationship;
- Light / Electromagnetic wave hierarchy;
- Software Architecture composition;
- History of Printing process/enablement case;
- Economics multi-relationship mechanism case;
- concise prose fallback.

The report should record:

- semantic focus identity;
- representation strategy;
- structural/spatial grammar rendered;
- nodes/components rendered;
- relationships rendered;
- canonical directions represented;
- inspectable components;
- hover/click behavior tested;
- current focus before/after local interaction;
- revealed knowledge before/after local interaction;
- My Map behavior/visual-regression checks;
- Explore Next isolation checks;
- evidence/provenance preservation;
- sparse/fail-closed behavior;
- screenshots or deterministic browser captures sufficient for owner review.

## Testing

Run:

1. focused SPEC-038 tests;
2. SPEC-037 visual-role regressions, especially My Map;
3. SPEC-036 local explanatory-interaction regressions;
4. SPEC-035 explanatory/navigation separation regressions;
5. SPEC-034 representation-strategy regressions;
6. SPEC-033 revealed-navigation regressions;
7. reciprocal/multi-edge semantic identity tests;
8. full offline suite;
9. browser/machine gate.

Report exact counts, browser result, console status, changed files, commits, push state, and clean-working-tree state.

## Explicit non-goals

Do not:

- redesign My Map;
- change revealed-knowledge semantics;
- change navigation architecture;
- implement traversal history;
- implement Back;
- use breadcrumbs as traversal history;
- change Explore Next semantics;
- reintroduce Explore deeper;
- make explanatory components navigational;
- add another forward-learning mechanism;
- change trusted semantic vocabulary;
- add new facts merely to enrich a diagram;
- infer missing edges to improve topology;
- use live/model-generated pedagogy;
- add personalization or learner-state modeling;
- add quizzes/mastery;
- add courses/guided pathways;
- add automatic analogy generation;
- force prose-first knowledge into diagrams;
- build a universal graph/map viewer;
- optimize for decorative animation;
- promote a baseline.

## Human review questions

After implementation the owner should be able to answer:

1. Does My Map remain as clear as SPEC-037?
2. Do structural explanations once again look unmistakably like diagrams rather than text laid out horizontally?
3. Does the diagram make structure perceptible before I read every label?
4. Are causal, hierarchy/composition, process/sequence, focused relationship, and prose visually different because their semantics differ?
5. Do semantic nodes have enough visual objecthood without looking like navigation buttons?
6. Do relationships look like actual connections?
7. Is the dominant representation now the first thing my attention goes to in structural cases?
8. Does hover/click inspection feel integrated with the diagram rather than merely changing text styling?
9. Are Explore Next recommendations still clearly distinct as actions, and are they still the only forward-traversal mechanism in the explanatory pane?
10. Did we preserve grounding, canonical direction, fail-closed behavior, and the cleaner navigation architecture?
11. Does sparse knowledge remain honestly sparse rather than being padded for visual effect?
12. Overall, is this a stronger learning surface than SPEC-037 while retaining the architectural gains made since the earlier diagram-rich UI?

## Owner decision after review

After browser review choose one:

```text
DIAGRAM_CANVAS_CONFIRMED
DIAGRAM_CANVAS_DIRECTIONALLY_CORRECT
DIAGRAM_CANVAS_NEEDS_REVISION
REJECT_AND_RETURN_TO_SPEC_037
```

Do not promote a baseline automatically. Owner review is the required human gate.

## Completion contract

Implementation is complete only when:

- the required offline implementation and regression tests pass;
- the browser/machine gate passes with a clean console;
- the isolated SPEC-038 evaluation artifact and report exist;
- exact test counts, changed files, commits, push state, and working-tree state are reported;
- `STATUS.md` is updated to record SPEC-038 as implemented and awaiting owner review;
- no baseline promotion is performed without explicit owner authorization.
