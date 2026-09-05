# SPEC-022 — Learner Navigation Grammar

## Status

Ready for implementation.

## Purpose

Make the frozen BASELINE-003 workspace understandable from the learner's point of view without changing its successful spatial/navigation model.

SPEC-022 tests only three interaction ideas:

1. a region is an entrance;
2. representation selection is automatic for the learner;
3. semantic depth is contextual to the concept being explored.

No semantic generation, new visualization archetype, or new model call is permitted.

## Product Thesis

The knowledge world should support both free exploration and future guided learning through the same interaction grammar.

```text
EXPLORATION
learner chooses trajectory through knowledge world

GUIDED LEARNING — future
system chooses/suggests trajectory through same knowledge world
```

Do not create separate course and exploration interfaces.

A future course should be representable as a guided trajectory through the same regions, concepts, relationships, representations, and depth transitions used during free exploration.

## Frozen Control

Use the restored owner-approved BASELINE-003 implementation as the executable control.

Preserve its successful behavior:

- two-pane workspace;
- continuous knowledge world on the left;
- spatial regions;
- stable world coordinates;
- drag/pan;
- geometric zoom;
- overview/home behavior;
- focus suppression;
- map ↔ learning synchronization;
- concept selection;
- relationship selection;
- representation-specific right-hand visualizations;
- detail/evidence behavior;
- independent camera state;
- existing visual styling and interaction behavior.

Do not recreate the shell.

Compose with/reuse the exact implementation that produced the restored viewer.

## Problem 1 — Regions Are Visible but Not Enterable

The map currently shows regions such as:

```text
Software Architecture
Economics
History of Printing
Electromagnetism
```

These visually read as places but are not meaningful interaction targets.

The learner must currently choose an arbitrary internal node before the learning surface becomes useful.

That requires knowledge the learner does not yet possess.

## Requirement — Region as Entrance

A region boundary/title must be directly selectable.

Interaction grammar:

```text
click REGION
    ↓
ENTER / ORIENT
```

Entering a region must:

1. focus/fit that region in the left navigation map without destroying world position;
2. mark the region as current context;
3. open a right-hand orientation representation for that region;
4. provide a sensible conceptual starting point without requiring the learner to choose an arbitrary node first;
5. preserve normal ability to pan/zoom away and explore elsewhere.

Do not turn region entry into page navigation.

## Region Orientation

The right-hand orientation surface should answer at a glance:

```text
What is this area about?
What are its important structural ideas?
Where could I start?
```

Use existing representation artifacts only.

Do not generate new semantic summaries.

Do not dump all region nodes as a catalog.

Choose the existing representation that best provides orientation according to already available representation metadata/ranking.

If no existing representation is clearly suitable, fail/diagnose rather than inventing a new representation in SPEC-022.

## Problem 2 — Compiler Controls Leak Into Learner UI

Current controls expose labels such as:

```text
Feedback candidate · PRIMARY
Hierarchy · SPARSE
Double-slit depth
```

These are useful evaluation/compiler concepts but poor learner controls.

The learner should not need to understand structure-detection terminology in order to learn.

## Requirement — Automatic Representation Selection

For learner mode, representation selection is automatic.

Interaction grammar:

```text
click REGION
→ system chooses best orientation representation

click CONCEPT
→ system chooses best representation containing/explaining concept

click RELATIONSHIP
→ system chooses representation that makes relationship legible
```

The original thesis remains binding:

> The appropriate representation should depend upon the information structure.

Therefore the learner should not ordinarily choose between `Hierarchy`, `Feedback candidate`, `Causal model`, etc.

The compiler chooses the representation; the learner chooses what they want to understand.

## Debug / Evaluator Access

Do not delete representation metadata or evaluator capability.

Compiler-facing labels such as:

```text
PRIMARY
SECONDARY
SPARSE
Feedback candidate
Hierarchy
```

may remain available in a clearly separate evaluator/debug mode or diagnostic artifact.

They should not dominate the default learner interaction surface.

## Problem 3 — Depth Is Global Instead of Contextual

The current `Double-slit depth` control appears while the learner is exploring unrelated concepts such as Electromagnetism → Light.

This exposes experiment implementation history rather than meaningful navigation.

It also produces ambiguous state and return behavior.

## Requirement — Contextual Depth

Remove the concept of a globally available named depth control from learner mode.

Depth belongs to the currently selected concept/relationship.

Interaction grammar:

```text
click CONCEPT
    ↓
UNDERSTAND
    │
    └── if deeper trusted resolution exists
             ↓
           DEEPEN
```

A deeper-resolution affordance may appear only when the currently selected semantic object has an admitted deeper resolution.

For the current frozen fixture:

- `double-slit-experiment` may expose its deeper resolution;
- unrelated concepts such as `Light`, `payment component`, etc. must not expose `Double-slit depth`;
- no other concept gains synthetic depth.

## Depth Affordance

Use a learner-facing action such as:

```text
Explore deeper
```

or an equally clear local affordance.

Do not label it with implementation terms such as:

```text
Double-slit depth
GENERIC_DETAIL
child resolution
semantic depth fixture
```

The affordance must be visually/local-context associated with the selected concept, not presented as a peer representation tab.

## Deeper State

When deeper resolution is entered:

1. left parent knowledge world remains stable;
2. parent map camera is preserved;
3. right learning surface changes resolution;
4. breadcrumb/context clearly states the selected concept and deeper state;
5. the learner can clearly return one level;
6. selection inside deeper representation is interactive;
7. explanatory/canonical items reveal appropriate detail/evidence;
8. no unrelated parent representation remains confusingly stacked above the deeper representation.

The learner should be able to answer:

```text
Where am I?
What did I deepen into?
How do I return?
```

without knowing compiler architecture.

## Navigation Grammar

Treat this as the explicit learner interaction grammar for the experiment:

```text
WORLD
 │
 ├── REGION ───────── click ───────► ORIENT
 │
 ├── CONCEPT ──────── click ───────► UNDERSTAND
 │       │
 │       └── local deeper resolution available
 │                         │
 │                         └────────► DEEPEN
 │
 └── RELATIONSHIP ─── click ───────► EXPLAIN
```

All actions occur inside the same persistent knowledge world/workspace.

## Learner Vocabulary

Default learner mode should converge toward a small conceptual vocabulary:

```text
Enter
Select
Follow
Explore deeper
Return
Overview
```

Avoid making the learner reason in terms of:

```text
primary
secondary
sparse
candidate
representation detector
fixture
generic detail
```

## Spaces Mirror Actions

Preserve the successful principle discovered in BASELINE-003:

> spaces mirror actions.

The left pane answers:

```text
WHERE AM I?
WHERE CAN I GO?
```

The right pane answers:

```text
WHAT DOES THIS MEAN?
```

Region entry must strengthen this distinction rather than blur it.

## Future Guided Learning Compatibility

Do not implement guided learning in SPEC-022.

But ensure the interaction/state model could later express a trajectory such as:

```text
enter Electromagnetism
→ orient
→ select electromagnetic wave
→ follow IS_A to Light
→ inspect relationship
→ deepen selected concept if available
→ return
→ continue
```

A future guide/course should be able to drive or suggest the same actions programmatically without requiring a separate UI architecture.

## No New Semantics

Do not:

- call a model;
- extract new assertions;
- canonicalize new semantics;
- add predicates;
- add proposition types;
- create new source summaries;
- invent region descriptions;
- add manually authored domain facts.

Use only existing frozen semantic/representation artifacts.

## No New Visualization Experiment

Do not design another representation archetype.

SPEC-022 is an interaction experiment.

Reuse existing representations and the existing SPEC-021 deeper projection fixture.

Do not evaluate or redesign the explanatory projection itself yet.

## BASELINE Protection

BASELINE-001, BASELINE-002, and BASELINE-003 remain frozen.

SPEC-022 must use isolated assets.

The executable BASELINE-003 shell must be reused rather than approximately reproduced.

## Mechanical Preservation Gate

Add deterministic regression checks against the actual executable BASELINE-003 implementation/assets.

At minimum protect:

- shell DOM/structural contract where practical;
- map world coordinates;
- region geometry;
- pan/zoom handlers;
- overview behavior;
- focus suppression behavior;
- concept/relationship selection behavior;
- map-learning synchronization;
- right-panel representation rendering seam;
- camera state independence;
- baseline styles/assets.

Permitted changes should be isolated to:

- region hit targets / region-entry state;
- learner-mode automatic representation-selection state;
- learner-facing control visibility/labels;
- contextual depth affordance and depth/return state.

## Required Frozen Interaction Fixtures

At minimum test:

### Electromagnetism region entry

```text
world overview
→ click Electromagnetism region/title
→ left map focuses region
→ right pane shows automatic orientation representation
```

### Light concept

```text
Electromagnetism
→ click Light
→ right pane automatically shows appropriate representation
→ learner does not choose `Hierarchy`/`Feedback candidate`
→ no double-slit depth control appears
```

### Double-slit contextual depth

```text
select double-slit-experiment
→ local Explore deeper affordance appears
→ enter deeper resolution
→ right pane contains only coherent deeper-resolution surface
→ deeper items are interactive
→ Return restores parent learning state
→ left map camera unchanged
```

### Existing BASELINE-003 software-architecture interaction

Must remain behaviorally unchanged except for hidden learner-facing representation selector controls if learner mode applies globally.

## Human Review Gate

After machine integrity passes, provide the viewer for owner review.

Do not explain the internal implementation before review.

Prompt only:

```text
Use the map naturally. Start by entering Electromagnetism, then follow whatever seems useful. Also try going deeper wherever the interface offers it. Tell me where the interaction feels obvious and where you have to stop and think about the interface itself.
```

## Human Review Questions

After spontaneous feedback, assess:

### Region entry

- Did Electromagnetism behave like a place I could enter?
- Did I receive a useful starting orientation?
- Did I know what to do next?

### Representation selection

- Did the right representation appear without requiring compiler knowledge?
- Did I miss manual representation tabs?
- Did any implementation terminology leak into the learning flow?

### Contextual depth

- Was deeper exploration offered only where it made contextual sense?
- Did entering depth feel like learning more about the selected thing?
- Did I always know how to return?
- Did the parent world remain stable?

### Unified world

- Does this feel like one navigable knowledge world rather than several tools/screens?
- Can I imagine a guided course simply moving me through this same interface?

## Verdict Set

Final verdict exactly one of:

```text
NAVIGATION_GRAMMAR_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

Machine success alone cannot produce `NAVIGATION_GRAMMAR_BETTER`; owner cognitive review is required.

## Acceptance Criteria

- [ ] Exact restored BASELINE-003 executable shell reused.
- [ ] No live/model calls.
- [ ] Region/title is selectable.
- [ ] Region entry focuses the map without page navigation.
- [ ] Region entry produces an automatic orientation representation.
- [ ] Learner does not need to select representation archetype manually.
- [ ] Compiler/evaluator metadata remains available outside default learner controls.
- [ ] `Double-slit depth` global control removed from learner mode.
- [ ] Deeper affordance appears only for selected object with admitted depth.
- [ ] Light does not expose double-slit depth.
- [ ] Double-slit experiment does expose local deeper affordance.
- [ ] Entering depth preserves left-map camera.
- [ ] Deeper representation is interactive.
- [ ] Return behavior is obvious and restores parent learning state.
- [ ] Existing concept/relationship selection remains synchronized across panes.
- [ ] Existing BASELINE-003 navigation behavior remains intact.
- [ ] No semantic vocabulary changes.
- [ ] No new representation archetype.
- [ ] No new source/domain content.
- [ ] Full offline suite passes.
- [ ] Human review occurs only after machine integrity passes.

## Required Handoff

Report:

1. exact executable BASELINE-003 assets reused;
2. baseline hashes before/after;
3. files changed;
4. region-entry implementation seam;
5. region hit-target behavior;
6. region orientation-selection rule;
7. automatic representation-selection rule for concepts;
8. automatic representation-selection rule for relationships;
9. learner controls removed/hidden;
10. evaluator/debug access retained;
11. contextual-depth eligibility rule;
12. exact objects with admitted depth in fixture;
13. depth-entry state transition;
14. return state transition;
15. parent camera invariance result;
16. deeper interaction result;
17. Electromagnetism region-entry regression result;
18. Light regression result;
19. double-slit depth regression result;
20. BASELINE-003 software-architecture regression result;
21. map ↔ learning synchronization result;
22. pan/zoom/overview regression result;
23. focus suppression regression result;
24. semantic changes, expected none;
25. representation changes, expected none except selection/orchestration;
26. model/live calls, expected 0;
27. dependencies added/removed;
28. offline test result;
29. deterministic regeneration result;
30. viewer command;
31. human review status, initially `PENDING_OWNER_REVIEW`;
32. implementation commit;
33. push status;
34. `HEAD == origin/main` status;
35. working-tree status;
36. confirmation no new baseline created;
37. confirmation no `DEBRIEF-022` created before owner verdict.

## Final Constraint

The learner chooses **what to understand**.

The compiler chooses **how that meaning is represented**.

A future course chooses **a trajectory through the same world**.
