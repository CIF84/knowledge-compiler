# SPEC-036 — Structure-Aware Explanatory Surface

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Restore the explanatory power that existed in the strongest earlier learning-surface experiments, but on top of the cleaner responsibility boundaries established by SPEC-033 through SPEC-035.

The current architecture is now clear enough to preserve:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ represents the current idea for understanding

EXPLORE NEXT
→ proposes explicit future traversal

LEARNING HISTORY / BACK
→ remembers traversal history (future package; not implemented here)
```

SPEC-035 successfully removed implicit navigation from explanatory components and removed the duplicate `Explore deeper` affordance. The remaining product gap is explanatory quality: the right pane is structurally cleaner but often too thin, too box-like, or less cognitively useful than earlier representation experiments.

This package tests whether the system can restore a **dominant, structure-fitting, inspectable explanation** without re-coupling explanation to navigation.

## Primary uncertainty

> Can the right pane become materially better at helping a learner understand the selected knowledge object while preserving the strict rule that explanation interaction is local and never silently navigates the learner?

## Owner review entering this packet

Owner review of SPEC-035 confirms the architectural separation is directionally correct:

- My Map is now distinct from explanation;
- Explore Next is the sole explicit forward-learning frontier;
- explanatory components no longer need to mirror or control navigation;
- the current main weakness is explanatory representation quality, not navigation mechanics.

The owner specifically wants the earlier explanatory strengths restored:

1. a dominant visual/structural representation where that form fits the knowledge;
2. inspectable semantic components that react to hover/click locally;
3. a separate textual explanation area for the currently inspected component or relationship;
4. preservation of representation diversity rather than turning every object into a diagram.

## Guiding principle

> **The explanatory surface needs a dominant representation with inspectable semantic components.**

But representation strategy must remain structure-aware rather than diagram-first.

Examples:

```text
causal system / mechanism      → causal or mechanism view
ordered process / algorithm    → sequence / stage view
composition / inheritance      → hierarchy / structure view
confusable alternatives        → compare / contrast matrix
abstract rule                  → worked example
philosophical proposition      → argument / objection prose structure
spatially dependent concept    → spatial representation
thin unsupported structure     → concise prose
```

The compiler should continue to choose the representation that minimizes the cognitive work required to understand the trusted structure currently in focus.

## Product contract

The right pane should converge on three conceptual zones:

```text
1. WHAT DOES THIS MEAN?
   dominant representation of the current knowledge object

2. INSPECT / SELECTED / PREVIEW
   grounded explanation of the component or relationship currently inspected

3. EXPLORE NEXT
   explicit future-learning frontier
```

A future fourth navigation control may introduce `Back`, but it is not implemented in this package.

### Zone 1 — dominant representation

The dominant representation should occupy the explanatory role previously served by the best SPEC-005/SPEC-006-style diagrams, but now through the SPEC-034 representation-strategy seam.

It must:

- fit the trusted semantic structure;
- expose structure directly where useful;
- be visually primary over metadata/provenance;
- use semantic components rather than generic decorative boxes;
- preserve canonical relationship direction and truth;
- degrade truthfully when richer structure is not supported.

It must **not**:

- reproduce My Map;
- behave like a graph browser;
- reveal new knowledge merely because a component is clicked;
- silently change current learning focus;
- add a second forward-navigation mechanism.

### Zone 2 — inspectable explanation

Components of the dominant representation may be interactive for explanation only.

Allowed local interactions include:

- hover highlight;
- click-to-pin local inspection;
- relationship emphasis;
- stage/component annotation;
- toggling between supported local explanatory details;
- inspecting a definition or grounded proposition.

These interactions may update a local explanatory state such as:

```text
current_learning_focus = double-slit experiment
representation_local_selection = interference pattern
```

They must not mutate:

```text
current_learning_focus
revealed_knowledge
navigation_history
Explore Next state
```

The lower textual area should explain the locally inspected item or relationship in grounded prose. If no local component is selected, it may summarize the current focus.

The learner should be able to inspect the explanation without leaving the thing being learned.

### Zone 3 — Explore Next

Preserve the current Explore Next responsibility and semantics from SPEC-035.

It remains the explicit place for:

- revealing related trusted concepts;
- following grounded canonical connections;
- entering committed deeper knowledge;
- revealing another knowledge region where appropriate.

Do not redesign it in this package except for minimal integration required by the explanatory surface.

## Preserve representation diversity

Do not restore explanatory power by forcing all cases through a single node-link diagram.

SPEC-034 strategy selection remains authoritative.

At minimum, preserve and meaningfully exercise multiple existing strategies such as:

- causal mechanism;
- hierarchy/composition;
- focused relationship;
- concise prose;
- any already-supported sequence, comparison, or worked-example strategy where trusted fixtures exist.

If a strategy currently resolves to a shallow or awkward representation, improve that strategy’s learner-facing form rather than bypassing the resolver.

## Restore explanatory richness, not legacy navigation

Earlier UI experiments sometimes made explanatory nodes behave as navigation targets. Do not restore that coupling.

A visually rich representation may look similar to an old explanatory diagram, but its semantics must now be different:

```text
OLD
click component → navigate

SPEC-036
click component → inspect locally
```

This is the central regression boundary.

## Visual interaction model

The owner’s earlier successful interaction grammar may be used as inspiration:

- the focused concept remains visually anchored;
- directly relevant components/relationships are emphasized;
- unrelated context may fade;
- hover may preview local semantic meaning;
- click may pin local inspection;
- the textual inspection area updates to explain that local semantic object;
- clearing local inspection restores the focus-level explanation.

Do not require exact visual parity with old screenshots. Preserve the cognitive effect, not historical CSS.

## Representation strategy expectations

### Causal / mechanism

Prefer a mechanism/system representation where trusted relationships form meaningful causal or influence structure.

A one-edge causal relation may remain simple; do not fabricate a network.

Where richer local structure exists, expose branching, convergence, or mechanism stages rather than flattening everything to `source → predicate → target` cards.

### Hierarchy / composition

Use a visibly hierarchical representation when trusted semantics support `IS_A`, `PART_OF`, containment, inheritance, or composition.

Avoid making hierarchy members look like unrelated action buttons.

### Focused relationship

For a selected canonical relationship, preserve a clear source–predicate–target representation, but make it explanatory rather than navigational.

Endpoints and predicate may be inspectable locally.

### Sequence / process

Where trusted chronology or ordered stages exist, render order as order. Do not infer chronology from prose position.

### Compare / contrast

Where the trusted structure genuinely contains contrasting alternatives, prefer aligned dimensions or a comparison structure rather than generic graph nodes.

### Worked example

Where a trusted example exists, make the mapping from abstract rule to concrete instance explicit and inspectable.

### Concise prose

Remain willing to use prose where no richer structure is justified. Prose fallback is not a failure.

## Sparse-structure discipline

Current review shows cases such as `Light → Electromagnetic wave` where the resolver correctly detects hierarchy/composition but trusted structure is sparse.

Do not inflate sparse cases into oversized pseudo-diagrams.

The UI should distinguish:

```text
rich structure → dominant structural representation
sparse structure → compact structural cue + prose
thin evidence → concise prose
```

Warnings such as “Sparse structure” may remain where materially useful, but they should not dominate the learning experience.

## Evidence and provenance

Evidence remains mandatory but subordinate to explanation.

The main learner-facing hierarchy should be:

```text
understanding first
supporting provenance second
```

Keep provenance collapsible/secondary where currently appropriate. Do not remove traceability.

No new factual claim may be introduced solely to make a representation richer.

## My Map is frozen for this packet

Do not redesign My Map in SPEC-036.

The owner has a separate visual concern that My Map currently looks too much like a stack of buttons and may ultimately benefit from a more folder-tree-like visual grammar. That is explicitly deferred.

For this package, preserve navigation behavior and structure exactly except for unavoidable integration seams.

## Learning history / Back is still deferred

The owner now expects the eventual product to distinguish:

```text
MY MAP
→ what territory have I revealed?

LEARNING HISTORY
→ how did I get here?
```

And expects a future `Back` affordance in or near the right-pane traversal controls.

Do not implement traversal history, persistence, Back, breadcrumbs, or inferred ontology-parent navigation in SPEC-036.

Avoid assumptions that would make browser-history-like traversal difficult later.

## Fixed evaluation cases

Use committed trusted fixtures and review at least the following categories.

### 1. Electromagnetism — reciprocal field relationship

Exercise electric-field / magnetic-field induction semantics.

Expected:

- focused relationship representation is clear;
- reciprocal canonical directions remain distinct where selected;
- endpoints/predicate can be locally inspected if useful;
- local interaction does not navigate.

### 2. Electromagnetism — double-slit experiment

Expected:

- causal/mechanism strategy remains selected where justified;
- representation is materially more explanatory than the current shallow two-card surface where trusted local structure supports more;
- local semantic components may be inspected;
- no `Explore deeper` returns;
- Explore Next remains the navigation path into deeper committed knowledge.

### 3. Light / Electromagnetic wave

Expected:

- hierarchy/composition strategy remains truthful;
- sparse structure is represented compactly rather than inflated;
- learner can distinguish the class/kind relationship without reconstructing it from prose.

### 4. History of Printing

Use the richest trusted supported concept or relationship in the fixture.

Expected:

- if the trusted structure supports enablement/process structure, the representation should expose it directly;
- interaction should support local inspection without navigation;
- do not force a diagram if the fixture is too sparse.

### 5. Software Architecture

Exercise a composition/hierarchy/dependency case with enough trusted structure to demonstrate that a non-causal representation can be visually rich and inspectable.

### 6. Concise-prose fallback

Include at least one case where the correct result is predominantly prose and verify the system does not force structural decoration.

## Required implementation work

1. Inspect SPEC-005, SPEC-006, SPEC-030, SPEC-034, SPEC-035 and the current focused-learning renderer/state seams only as needed.
2. Preserve the current navigation architecture and SPEC-035 interaction isolation.
3. Introduce or strengthen explicit representation-local inspection state independent of current learning focus.
4. Refine renderer contracts so each representation strategy can expose inspectable semantic components where useful.
5. Restore a dominant learner-facing representation for supported rich structures.
6. Add/update the secondary textual inspection surface for locally hovered/selected components or relationships.
7. Ensure local hover/click never mutates navigation focus or revealed territory.
8. Keep Explore Next as the only forward-learning control.
9. Do not restore `Explore deeper`.
10. Preserve evidence/provenance traceability and fail-closed behavior.
11. Exercise multiple representation strategies and at least one prose fallback.
12. Produce an isolated browser evaluation artifact and durable report.

## State model

Prefer an explicit separation conceptually equivalent to:

```text
NavigationState
    current_learning_focus
    revealed_knowledge

RepresentationPlan
    strategy_type
    semantic_focus_identity
    inspectable_components
    payload
    evidence_refs

RepresentationLocalState
    hovered_component_id | null
    selected_component_id | null
```

Invariant:

```text
representation interaction
    may change RepresentationLocalState
    must not change NavigationState
```

If current code uses different names, preserve the conceptual boundary rather than forcing these exact classes.

## Acceptance cases

### A. Dominant representation restored

Open at least one sufficiently rich causal/mechanism case, one hierarchy/composition case, and one focused relationship.

Expected: the learner-facing representation is visually and structurally dominant, not merely title + one sentence + metadata.

### B. Local hover inspection

Hover a supported semantic component in the explanation.

Expected:

- local highlight/preview may change;
- textual inspect area may update;
- current learning focus is unchanged;
- revealed territory is unchanged.

### C. Local click-to-pin inspection

Click a supported semantic component.

Expected:

- local inspection may pin;
- textual inspect area reflects the pinned component/relationship;
- current learning focus is unchanged;
- no reveal or navigation occurs.

### D. Clear local inspection

Clear or replace the local inspection state.

Expected: focus-level explanation returns without changing learner location.

### E. Explore Next remains explicit navigation

Choose an Explore Next candidate.

Expected: this may reveal/navigate normally because it is an explicit traversal action.

### F. My Map remains explicit return navigation

Choose a revealed object in My Map.

Expected: current learning focus changes normally.

### G. No duplicate depth navigation

Expected: no active `Explore deeper` affordance exists anywhere in the explanatory surface.

### H. Representation diversity

Expected: strategy resolution still yields materially different representation forms for different semantic structures.

### I. Prose remains valid

Expected: a thin/non-structural case renders primarily as prose rather than an artificial graph.

### J. Depth independence

Open equivalent semantic structure through deeper/recursive traversal.

Expected: it enters the same representation strategy and interaction grammar as root-level knowledge; depth does not select a special renderer.

## Machine acceptance

Before owner review verify:

```text
control plane valid
OFFLINE_ONLY respected
no live/model/external calls
trusted semantic vocabulary unchanged
grounding/provenance unchanged
fail-closed behavior unchanged
SPEC-033 My Map behavior unchanged
SPEC-034 strategy resolver preserved
SPEC-035 navigation/isolation invariants preserved
no active Explore deeper affordance
Explore Next remains sole forward-learning control
representation-local hover/click cannot mutate current_learning_focus
representation-local hover/click cannot mutate revealed_knowledge
multiple materially different representation strategies exercised
at least one prose fallback exercised
rich supported cases produce dominant explanatory representations
sparse structure is not artificially inflated
depth-independent representation behavior passes
browser console clean
full offline suite passes
git diff --check passes
```

## Browser review artifact

Create:

```text
examples/evaluations/spec-036-structure-aware-explanatory-surface-<date>/
```

The owner-review candidate should make it easy to compare at least:

- double-slit causal/mechanism;
- field focused relationship;
- Light / Electromagnetic wave hierarchy;
- one History of Printing case;
- one Software Architecture case;
- one concise-prose fallback.

The report should record, per case:

- semantic focus identity;
- selected representation strategy;
- trusted structure consumed;
- inspectable components exposed;
- local interaction tested;
- focus before/after local interaction;
- revealed knowledge before/after local interaction;
- evidence/provenance source;
- fallback/sparsity rationale where relevant.

## Testing

Run:

1. focused SPEC-036 tests;
2. SPEC-035 explanatory-interaction isolation regression tests;
3. SPEC-034 representation-strategy regression tests;
4. SPEC-033 navigation/revealed-knowledge regression tests;
5. reciprocal/multi-edge semantic identity tests;
6. full offline suite;
7. browser/machine gate.

Report exact counts, browser result, console status, changed files, commits, push state, and clean-working-tree state.

## Explicit non-goals

Do not:

- redesign My Map visuals or behavior;
- implement folder-tree styling for My Map;
- implement Back;
- implement traversal history or persistence;
- use breadcrumbs as traversal history;
- add live/model-generated pedagogy;
- add learner personalization/modeling;
- add quizzes/mastery;
- add courses/guided pathways;
- add automatic analogy generation;
- add new domains merely to showcase a renderer;
- expand ontology/canonical facts merely to make a representation richer;
- reintroduce map/explanation mirroring;
- make explanatory semantic components navigational;
- introduce a second forward-learning mechanism;
- make every representation a diagram;
- build a universal graph viewer;
- promote a baseline.

## Human review questions

After implementation the owner should be able to answer:

1. Does the right pane once again feel like a place where difficult ideas become easier to understand?
2. Is the dominant representation better than the current thin title/card treatment for rich structures?
3. Can I inspect components and relationships without accidentally navigating?
4. Does the textual inspection area make the interactive representation more useful rather than duplicate it?
5. Does the representation form genuinely vary with the knowledge structure?
6. Does prose remain the right answer where visual structure would be decorative?
7. Are My Map, explanation, and Explore Next still clearly separate responsibilities?
8. Has any legacy `Explore deeper` or implicit right-pane navigation returned?

## Verdict set

Owner verdict must be exactly one of:

```text
EXPLANATORY_POWER_RESTORED
PROMISING_BUT_REPRESENTATION_WEAK
INTERACTION_MODEL_CONFUSING
REPRESENTATION_STRATEGY_REGRESSED
NAVIGATION_BOUNDARY_REGRESSED
TRUST_OR_PROVENANCE_REGRESSED
INCONCLUSIVE
```

Codex must not assign the subjective verdict.

## Success criterion

SPEC-036 succeeds if the explanatory pane recovers the cognitive advantage of the best earlier UI experiments while preserving the cleaner architecture achieved since then.

In practical terms:

> The learner can stay on one idea, manipulate or inspect its representation, understand its important parts and relationships, and then choose explicitly whether to go somewhere else.

## Completion state and handoff

On successful implementation:

- set SPEC-036 to `IMPLEMENTED_AWAITING_REVIEW`;
- update `STATUS.md` consistently so no follow-up implementation is accidentally authorized;
- do not assign the owner verdict;
- do not promote a baseline;
- do not begin SPEC-037 automatically.

Return only the low-attention handoff required by `AGENTS.md`.
