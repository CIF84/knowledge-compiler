# SPEC-035 — Explanatory Surface Purification

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Restore a strict boundary between navigation and explanation.

The explanatory pane exists to help the learner understand the currently selected knowledge object. It must not behave like a second navigation map.

Guiding rule:

> Clicking a component inside an explanation must not silently change the learner’s location in the knowledge model.

SPEC-035 is deliberately narrow: remove legacy navigation semantics from the right learning surface while preserving the representation-strategy capability introduced by SPEC-034.

## Product contract

The workspace now has three active responsibilities and one deferred one:

- **My Map — territory:** what knowledge has been revealed; explicit navigation among already revealed knowledge.
- **Learning surface — explanation:** what the current knowledge object means; representation may vary by semantic structure.
- **Explore Next — frontier:** explicit mechanism for discovering/revealing new knowledge.
- **Learning history — traversal:** future capability answering “how did I get here?”; explicitly out of scope for this package.

The representation strategy may remain heterogeneous: causal mechanism, hierarchy/composition, sequence, compare/contrast, worked example, spatial representation, concise prose, focused relationship, or another evidence-supported strategy. Representation diversity is intentional. Navigation semantics inside those representations are not.

## Required behaviour

### 1. Representation elements must not navigate

Concept boxes, endpoint concepts, arrows, relationship labels, mechanism stages, hierarchy members, sequence stages, comparison items, annotations, or equivalent elements rendered inside the explanatory representation must not change the authoritative current learning focus merely because they are clicked.

Example:

```text
current focus: double-slit experiment

[double-slit experiment] → CAUSES → [interference pattern]
```

Clicking `interference pattern` inside this representation must leave the current focus as `double-slit experiment`.

Likewise, while viewing a focused relationship such as:

```text
Electric field → INDUCES → Magnetic field
```

clicking either endpoint inside the representation must not silently navigate away from the relationship.

### 2. Local explanatory interaction is allowed

Representations do not need to become static. Local interactions may be retained or added where they improve understanding, for example highlighting, annotations, toggles, expanding a mechanism stage, inspecting a definition, or manipulating a worked example.

But these interactions must remain local to the representation and must not mutate learner location.

Conceptually valid state:

```text
current_learning_focus = double-slit experiment
representation_local_state = interference-pattern component highlighted
```

Invalid implicit mutation:

```text
current_learning_focus = interference pattern
```

### 3. Remove `Explore deeper`

Remove the active `Explore deeper` affordance from the explanatory pane. Its navigation responsibility now overlaps with and is superseded by `Explore Next`.

There must be one explicit forward-learning mechanism: `Explore Next`.

### 4. Preserve `Explore Next`

Do not redesign Explore Next in SPEC-035. Preserve its current semantics and behaviour as the frontier from currently revealed knowledge to optional next learning steps.

### 5. Preserve `My Map`

Do not redesign My Map. Do not restore map ↔ explanation mirroring. My Map remains the explicit navigation surface for already revealed knowledge; selecting an object there may change current focus normally.

### 6. Preserve SPEC-034 representation strategy

Do not solve this package by flattening every explanation into prose or into one universal diagram.

Representation strategy must continue to choose forms appropriate to supported structure, e.g.:

```text
causal structure        → causal mechanism
composition             → hierarchy/composition
ordered process         → sequence
confusable alternatives → compare/contrast
abstract rule           → worked example
geometry-dependent      → spatial representation
no stronger fit         → concise prose
```

### 7. One authoritative learning focus

There must be one authoritative current learning focus. It may change through explicit navigation actions such as My Map selection or Explore Next selection. It must not change because of incidental interaction within the explanatory representation.

Representation state and navigation state must remain distinct.

### 8. Hover behaviour

Hover may provide representation-local highlighting or inspection, but must never change persistent learner location. Avoid adding new hover mechanics simply to demonstrate the rule.

### 9. Preserve evidence/provenance discipline

Keep the evidence/provenance behaviour and source-boundedness from earlier specifications. Do not invent richer structure than the trusted knowledge supports merely to force a particular representation.

## Regression protection

The following must continue to work:

- navigating among revealed knowledge through My Map;
- choosing/revealing frontier knowledge through Explore Next;
- returning to previously revealed deeper knowledge through My Map;
- region navigation;
- the representation-strategy grammar from SPEC-034;
- evidence/provenance display;
- recursive/deeper knowledge rendering where currently supported.

SPEC-035 must not reintroduce map/explanation mirroring as a requirement.

## Deferred invariant — learning history / Back

Do **not** implement Back, learning history UI, traversal persistence, or breadcrumbs in SPEC-035.

But preserve this architectural invariant for the next package:

> Revealed knowledge is not the same thing as learner traversal history.

Future behaviour should be able to distinguish:

```text
MY MAP
What territory have I revealed?

LEARNING HISTORY
How did I get here?
```

Example future traversal:

```text
Electromagnetism
→ double-slit experiment
→ interference pattern
→ wave-particle duality
→ cross-region jump
→ another concept
```

A future Back action should return to the prior traversal state, not infer a parent from ontology structure. This is browser-history-like traversal semantics, not ontology-parent semantics.

Do not implement it yet; simply avoid new assumptions that would make it difficult later.

## Explicit non-goals

Do not:

- redesign My Map;
- redesign Explore Next;
- implement Back;
- implement learning-history UI or traversal persistence;
- add breadcrumbs as a substitute for history;
- restore map/explanation mirroring;
- make representation components navigational;
- introduce another forward-navigation mechanism;
- replace heterogeneous representations with universal prose;
- replace heterogeneous representations with universal diagrams;
- substantially restyle the interface;
- expand domain/fixture scope merely to showcase the change.

Prefer deleting obsolete interaction behaviour to layering compatibility logic around it.

## Acceptance cases

### A. Double-slit representation isolation

Open `double-slit experiment`. Interact with the represented `interference pattern` component.

Expected: current focus remains `double-slit experiment`; no silent navigation.

### B. Focused relationship isolation

Open a relationship such as `Electric field → INDUCES → Magnetic field`. Interact with both endpoint representations.

Expected: relationship remains current focus unless an explicit navigation control outside the representation is invoked.

### C. Hierarchy/composition isolation

Open a hierarchy representation such as Light / Electromagnetic wave and interact with its represented members.

Expected: no silent knowledge navigation.

### D. Explore deeper removal

Across rendered learning-surface paths, no active `Explore deeper` affordance remains.

### E. Explore Next regression

Use Explore Next to reveal/navigate to supported frontier knowledge.

Expected: existing explicit forward navigation works.

### F. My Map regression

Navigate among revealed concepts, relationships, deeper knowledge, and regions via My Map.

Expected: current focus changes correctly.

### G. Representation diversity

Exercise multiple SPEC-034 representation strategies.

Expected: representation selection remains operational; the fix does not collapse them into one type.

### H. State separation

Where representation-local interaction exists, verify:

```text
focus_before == focus_after
```

unless the action is an explicit navigation action outside the explanatory representation.

## Evaluation/reporting

Extend evaluation/reporting only as needed to demonstrate:

- representation strategy selected;
- current focus before representation interaction;
- current focus after interaction;
- whether navigation mutation occurred;
- Explore deeper absent;
- Explore Next operational;
- My Map navigation operational.

The key machine-readable invariant for a successful representation-local interaction is:

```text
focus_before == focus_after
```

## Browser gate

Cover representative cases including causal mechanism, hierarchy/composition, focused relationship, concise prose where applicable, My Map navigation, and Explore Next.

Require:

- no unexpected navigation from explanatory-representation interaction;
- no stale selection state;
- no duplicate forward-navigation affordances;
- no new console errors or warnings.

## Testing

Run:

1. focused SPEC-035 tests;
2. SPEC-034 representation-strategy regression tests;
3. navigation/revealed-knowledge regression tests;
4. full offline suite;
5. browser/machine gate.

Report exact counts and resulting commit(s).

## Implementation discipline

Earlier work intentionally coupled map and explanation interactions. That is no longer the product requirement.

Where existing tests conflict with this specification, determine whether they encode obsolete map/explanation mirroring or implicit explanatory-pane navigation. Update or replace only those obsolete expectations while preserving still-valid semantic/navigation coverage.

Keep the package narrow and avoid unrelated refactors.

## Human review questions

After implementation we should be able to answer yes to:

1. Does the right pane feel like a place to understand rather than another place to navigate?
2. Can I interact with a representation without accidentally leaving what I am learning?
3. Is Explore Next clearly the sole forward-learning affordance?
4. Does My Map remain sufficient for returning to revealed knowledge?
5. Is SPEC-034 representational flexibility preserved?
6. Is the product grammar now clear: My Map = territory; right pane = understanding; Explore Next = frontier?

## Success criterion

SPEC-035 succeeds when manipulation or inspection of an explanation can no longer be confused with movement through the knowledge model.

Guiding grammar:

> Navigate deliberately. Represent appropriately. Explore explicitly.

Or structurally:

> My Map remembers territory. The explanatory pane represents the current idea. Explore Next proposes future traversal.

Learning history / Back is intentionally deferred to the next package.
