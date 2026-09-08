# SPEC-037 — Visual Semantic Grammar

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Preserve the cleaner responsibility model established by SPEC-033 through SPEC-036 while removing the current visual ambiguity that makes navigation and explanation feel like collections of generic buttons.

SPEC-036 restored an important capability: the right explanatory surface can once again expose inspectable semantic components without silently navigating the learner. Owner review confirms that this is directionally correct and materially better than the purified-but-thin SPEC-035 surface.

The remaining problem is now primarily one of **visual semantic grammar and learner-facing hierarchy** rather than navigation mechanics or representation-state architecture.

The system currently overuses the same rounded-box / pill / bordered-control language for:

- revealed territory in My Map;
- concepts inside explanatory representations;
- relationships inside explanatory representations;
- metadata-like relationship summaries;
- recommendation cards;
- actual controls.

This makes too many things look clickable in the same way and flattens the distinction between:

```text
territory
representation
inspection
recommendation
control
```

SPEC-037 tests whether the learner-facing interface becomes substantially clearer and more engaging when those roles receive intentionally different visual grammars, while preserving all semantic and interaction invariants already established.

## Primary uncertainty

> Can the interface communicate semantic role through visual form strongly enough that My Map reads as territory, the right pane reads as explanation, and actual controls/recommendations read as actions — without redesigning the underlying navigation or representation architecture?

## Owner review entering this packet

Owner review of SPEC-036 confirms:

- local explanatory hover/click interaction is worth preserving;
- explanatory components must remain inspection-only and must not navigate;
- representation diversity remains required;
- current explanatory richness is improved but still visually underpowered;
- My Map works behaviorally but visually resembles a stack of buttons;
- the right pane still contains too many generic boxes/pills and therefore feels mechanically repetitive and visually boring;
- legacy learner-facing artifacts such as `Trusted relationships` may remain even when they no longer provide useful behavior or explanation.

The owner specifically wants:

1. a visually distinct My Map territory/tree grammar;
2. richer explanatory composition that does not default to cards for every semantic object;
3. visual distinction between semantic objects and actual controls;
4. preservation of local explanatory interaction from SPEC-036;
5. removal or demotion of obsolete/non-functional learner-facing artifacts;
6. no regression of the clean architecture or navigation semantics.

## Guiding principle

> **Visual form should communicate semantic role.**

A concept, relationship, region, recommendation, inspection state, and control should not all look like variants of the same button.

The secondary principle remains:

> **The compiler should choose the representation that minimizes the cognitive work required to understand the trusted structure currently in focus.**

And the interaction invariant remains:

> **Clicking or manipulating a component inside an explanation must not silently change the learner’s location in the knowledge model.**

## Responsibility model to preserve

```text
MY MAP
→ remembers revealed territory
→ deliberate navigation among already revealed knowledge

WHAT DOES THIS MEAN?
→ dominant representation of the current idea
→ representation-local inspection only

INSPECT / SELECTED / PREVIEW
→ grounded explanation of the locally inspected semantic component

EXPLORE NEXT
→ explicit trusted frontier / forward traversal

LEARNING HISTORY / BACK
→ deferred traversal memory
```

Do not change these responsibilities in SPEC-037.

## Visual semantic grammar

SPEC-037 should introduce a small, explicit learner-facing grammar that separates at least the following roles.

### 1. Territory / My Map

My Map should read as a **quiet revealed-knowledge tree**, not a list of buttons.

Preferred visual direction:

- folder/tree indentation;
- branch lines or equivalent hierarchical cues;
- lightweight labels rather than bordered cards for every row;
- restrained expand/collapse affordances;
- current focus visible but not rendered as an oversized action button;
- regions, concepts, relationships, and explanations distinguishable through typography/iconography/indentation rather than repeated container chrome.

The visual tree may use familiar file-browser grammar as inspiration, but must remain semantically truthful to revealed knowledge rather than pretending the ontology is literally a filesystem.

Behavior is frozen:

- same revealed objects;
- same deduplication;
- same collapse/expand semantics;
- same navigation authority;
- same current-focus behavior;
- no traversal history added;
- no new knowledge inferred or revealed through styling.

### 2. Explanatory semantic objects

Objects inside `WHAT DOES THIS MEAN?` should look like parts of a representation, not generic UI controls.

Depending on representation strategy, prefer native visual forms such as:

```text
causal/mechanism
→ nodes connected by directional paths / flow

process/sequence
→ stages on a temporal or ordered track

hierarchy/composition
→ nested / branched / layered structure

compare/contrast
→ aligned rows/columns or contrasted regions

worked example
→ mapping between rule and instance

focused relationship
→ emphasized source–predicate–target relation

concise prose
→ typographic explanatory structure with little or no box chrome
```

Do not force all strategies through rectangular cards.

### 3. Relationships

Relationships should read primarily as **connective semantics**, not standalone buttons.

Where a relationship is part of a diagram or structured representation, prefer:

- lines;
- arrows;
- connectors;
- spatial alignment;
- labels attached to those connectors;
- emphasis on hover/selection without converting the relationship into an action pill.

A relationship may still be locally inspectable. The hover/click target may be larger than the visible line for usability, but the visual object should not need to look like a button.

For focused-relationship strategy, source / predicate / target may remain explicit, but the predicate should visually read as the relation between endpoints rather than merely a third card.

### 4. Inspection

The lower inspection zone should remain visually subordinate to the dominant representation and clearly read as explanatory detail.

Use typography, dividers, evidence blocks, or other reading-oriented forms rather than action styling.

`Clear inspection` is an actual control and may therefore look like a control.

### 5. Explore Next

Explore Next is an action/recommendation surface and may intentionally use card/button affordances because its job is to propose explicit future traversal.

This is a useful contrast:

```text
representation component
→ looks inspectable / semantic

Explore Next recommendation
→ looks actionable
```

Do not eliminate its interaction affordance merely for visual consistency.

## Remove obsolete learner-facing artifacts

Review the current right-pane output for remnants from earlier experiments that no longer serve a live explanatory or interaction function.

The owner specifically flagged `Trusted relationships` as an example.

For each such artifact:

- determine whether it contributes unique learner-facing meaning;
- if it merely duplicates information already present in the dominant representation or inspection zone and has no active function, remove it from the learner-facing surface;
- if traceability requires retaining the underlying data, keep it in the internal representation model or evidence/provenance layer without displaying redundant chrome;
- do not delete canonical semantic data merely because its current UI treatment is obsolete.

Do not perform a broad content purge. This is a surface cleanup bounded by explanatory usefulness.

## Preserve explanatory interaction

SPEC-036 local interaction must remain:

```text
hover semantic component
→ preview local meaning

click semantic component
→ pin local inspection

clear inspection
→ return to focus-level explanation
```

These interactions must remain local.

They must not mutate:

```text
current_learning_focus
revealed_knowledge
navigation_history
Explore Next state
```

Visual redesign must not make explanatory components navigational again.

## Representation diversity remains authoritative

Do not use this packet to converge all explanation strategies onto one beautiful diagram template.

The visual grammar should make heterogeneous strategies more legible, not less heterogeneous.

At minimum, exercise:

- causal/mechanism;
- hierarchy/composition;
- focused relationship;
- process/sequence if supported by current trusted fixture;
- concise prose fallback.

If existing compare/contrast or worked-example fixtures are already committed and trustworthy, include them, but do not add facts or domains merely to demonstrate styling.

## Visual hierarchy goals

The right pane should read approximately as:

```text
WHAT DOES THIS MEAN?

[dominant representation]

[inspection / selected detail]

[Explore Next]
```

Evidence/provenance remains available but should be visually secondary.

Avoid nested bordered panels inside bordered panels unless a boundary communicates real semantic structure.

Avoid excessive pills, badges, cards, and outlines.

Use whitespace, typography, alignment, connector geometry, and selective emphasis as first-class visual tools.

The goal is not decorative richness. The goal is to reduce cognitive ambiguity and make structure perceptible before the learner reads every label.

## Fixed evaluation cases

### 1. My Map — mixed revealed territory

Use a state with multiple regions and at least one expanded deeper concept.

Expected:

- reads immediately as a territory/tree;
- regions and descendants are visually distinct without every row becoming a boxed button;
- current focus remains obvious;
- collapse/expand works exactly as before;
- navigation behavior is unchanged.

### 2. Electromagnetism — double-slit experiment

Expected:

- causal/mechanism representation remains semantically correct;
- relation visually reads as flow/causation rather than a row of button cards;
- components remain hoverable/clickable for local inspection;
- no local interaction navigates;
- Explore Next remains visually and behaviorally distinct from the representation.

### 3. Electromagnetism — Light / Electromagnetic wave

Expected:

- hierarchy/composition remains compact because structure is sparse;
- visual hierarchy is recognizable without oversized boxes;
- the relation reads as hierarchy/type membership rather than action UI.

### 4. Electromagnetism — focused canonical relationship

Expected:

- source, predicate, target remain clear;
- relationship is visually connective;
- local inspection works;
- focused relation does not become a fake navigation control.

### 5. History of Printing

Expected:

- process/enablement or sequence structure, where trusted, is visually distinct from causal and hierarchy renderers;
- obsolete `Trusted relationships`-style duplication is absent if it carries no unique learner value;
- local inspection remains grounded.

### 6. Software Architecture

Expected:

- composition/hierarchy reads as architecture/structure rather than a card grid;
- semantic components are inspectable;
- representation remains different in visual grammar from History of Printing and causal mechanism.

### 7. Concise prose fallback

Expected:

- prose reads like prose;
- no gratuitous card/diagram chrome is added simply to match richer strategies.

## Required implementation work

1. Inspect current SPEC-036 browser artifact and learner-facing renderer styles/components.
2. Preserve SPEC-033 navigation behavior and SPEC-036 representation-local interaction semantics.
3. Refactor My Map presentation into a restrained tree/territory visual grammar without changing its data model or behavior.
4. Refine explanatory renderer presentation so semantic objects no longer default to generic button/card chrome.
5. Make relationships visually connective in strategies where connection is the meaning.
6. Preserve representation-specific layouts and strengthen their visual differentiation.
7. Keep actual controls and Explore Next recommendations visibly actionable.
8. Remove or demote obsolete/non-functional learner-facing artifacts such as redundant `Trusted relationships` output where verified safe.
9. Keep inspection text and evidence/provenance reading-oriented and visually subordinate to the dominant representation.
10. Preserve all grounding, provenance, fail-closed behavior, canonical relationship direction, and representation-strategy resolution.
11. Add/update browser-level tests for local interaction and navigation invariants after styling/refactor.
12. Produce an isolated browser evaluation artifact and durable report.

## Acceptance cases

### A. My Map no longer reads as a button stack

Expected: a reviewer can visually identify My Map as a hierarchical territory/tree before interacting with it.

### B. Semantic object vs action is distinguishable

Expected: explanatory components do not use the same dominant affordance language as Explore Next controls.

### C. Relationships read as connections

Expected: in causal, hierarchy, sequence, and focused-relationship representations, relationships visually communicate connection/direction/order rather than merely occupying standalone pill/card containers.

### D. Local inspection survives visual redesign

Expected: hover and click update only local explanatory inspection; learner location and revealed territory do not change.

### E. Navigation survives visual redesign

Expected: My Map deliberate navigation and collapse/expand behavior remain unchanged.

### F. Explore Next remains obvious and explicit

Expected: forward-learning recommendations remain clearly actionable and remain the only forward traversal mechanism in the explanatory pane.

### G. Obsolete learner-facing duplication is removed

Expected: non-functional/redundant sections such as `Trusted relationships`, where they add no unique meaning, are absent from the learner-facing surface while underlying trusted data remains intact.

### H. Representation diversity is visually apparent

Expected: causal/mechanism, hierarchy/composition, focused relationship, process/sequence, and concise prose are recognizably different forms rather than the same card system with different labels.

### I. Sparse structure remains sparse

Expected: sparse hierarchy or one-edge relation is not inflated into decorative complexity.

### J. Evidence remains available

Expected: provenance and exact evidence remain reachable and correct after learner-facing visual cleanup.

## Machine acceptance

Before owner review verify:

```text
control plane valid
OFFLINE_ONLY respected
no live/model/external calls
trusted semantic vocabulary unchanged
grounding/provenance unchanged
fail-closed behavior unchanged
SPEC-033 My Map data/behavior unchanged
SPEC-034 representation resolver preserved
SPEC-035 navigation/explanation separation preserved
SPEC-036 representation-local interaction preserved
no active Explore deeper affordance
Explore Next remains sole forward-learning control
representation-local hover/click cannot mutate current_learning_focus
representation-local hover/click cannot mutate revealed_knowledge
My Map collapse/expand and deliberate navigation regressions pass
multiple representation strategies remain materially distinct
concise-prose fallback remains valid
obsolete learner-facing artifact removal does not delete canonical data
browser console clean
full offline suite passes
git diff --check passes
```

## Browser review artifact

Create:

```text
examples/evaluations/spec-037-visual-semantic-grammar-<date>/
```

The owner-review candidate should make side-by-side inspection easy for:

- mixed My Map revealed territory;
- double-slit causal/mechanism;
- focused canonical relationship;
- Light / Electromagnetic wave hierarchy;
- History of Printing process/sequence or enablement case;
- Software Architecture composition case;
- concise-prose fallback.

The report should record:

- semantic focus identity;
- representation strategy;
- visual grammar role(s) rendered;
- inspectable components;
- local interaction tested;
- current focus before/after local interaction;
- revealed knowledge before/after local interaction;
- My Map behavior checks;
- obsolete learner-facing artifacts removed/demoted;
- evidence/provenance preservation;
- screenshots or deterministic browser captures sufficient for owner review.

## Testing

Run:

1. focused SPEC-037 tests;
2. SPEC-036 local explanatory-interaction regression tests;
3. SPEC-035 explanatory/navigation separation regressions;
4. SPEC-034 representation-strategy regressions;
5. SPEC-033 revealed-knowledge/navigation regressions;
6. reciprocal/multi-edge semantic identity tests;
7. full offline suite;
8. browser/machine gate.

Report exact counts, browser result, console status, changed files, commits, push state, and clean-working-tree state.

## Explicit non-goals

Do not:

- change My Map revealed-knowledge semantics;
- redesign navigation architecture;
- implement traversal history;
- implement Back;
- use breadcrumbs as traversal history;
- change Explore Next semantics;
- reintroduce `Explore deeper`;
- make explanatory components navigational;
- add a second forward-learning mechanism;
- introduce live/model-generated pedagogy;
- add personalization or learner-state modeling;
- add quizzes/mastery;
- add courses/guided pathways;
- add automatic analogy generation;
- add new semantic facts merely to improve visuals;
- delete canonical trusted relationships because a learner-facing duplicate is removed;
- force all representations into diagrams;
- build a universal graph viewer;
- pursue decorative animation as a goal;
- promote a baseline.

## Human review questions

After implementation the owner should be able to answer:

1. Does My Map now read as revealed territory rather than a pile of buttons?
2. Does the explanatory pane feel visually richer without becoming visually noisy?
3. Can I tell the difference between a semantic object I can inspect and an action that will navigate/reveal something?
4. Do relationships visually read as relationships rather than generic pills/cards?
5. Do different representation strategies genuinely feel like different explanatory forms?
6. Did we preserve the useful hover/click inspection behavior from SPEC-036?
7. Did we remove learner-facing artifacts that no longer serve a purpose?
8. Is the result less boring because structure is clearer, rather than because decoration was added?
9. Is any previous navigation or grounding behavior worse?
10. Is this a stronger foundation for later traversal history / Back work?

## Owner decision after review

After browser review choose one:

```text
VISUAL_GRAMMAR_CONFIRMED
VISUAL_GRAMMAR_DIRECTIONALLY_RIGHT
REVISE_VISUAL_GRAMMAR
ROLL_BACK_SPEC_037
```

Promotion remains a separate explicit decision.
