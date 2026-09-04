# SPEC-018 — Continuous Graph Navigation

## Status

Ready for implementation.

## Phase

Phase II — interaction/navigation.

## Primary Question

> Can the proven SPEC-006 graph grammar become a continuous, pannable knowledge surface where focusing frontier nodes smoothly reveals adjacent topology while preserving spatial orientation?

## Critical Experimental Rule

**Do not redesign the graph.**

SPEC-006 is the visual invariant for this experiment.

SPEC-018 changes navigation/camera behavior only.

## Why This Experiment

The strongest historical visual result remains SPEC-006.

Owner reaction:

> “006 is insanely good.”

SPEC-007 added preferred contextual depth but exposed awkward `Explore` / `Back` navigation.

The owner subsequently described the desired interaction as Google-Maps-like parent-context navigation.

SPEC-016 and SPEC-017 then reopened representation and both regressed cognitively.

The owner has now clarified the desired interaction directly:

> “all we really needed was to drag map and leave visuals to move. when you click node close to edge of the screen, new part of the map appears as new nodes are moving to the center of the screen.”

Therefore the next uncertainty is navigation, not representation.

## Visual Invariant — SPEC-006

Preserve the visual grammar established by SPEC-006 / BASELINE-001 as closely as practical:

```text
explicit concept nodes
explicit relationship connectors
arrow direction
relationship labels
hierarchy layouts
causal layouts
dependency layouts
process chronology
feedback loops
selection highlighting
hover preview
detail panel
source evidence
```

Do not replace these with:

- Venn/neighborhood bubbles;
- card grids;
- assertion nodes;
- unlabeled proximity topology;
- new graph metaphor;
- 3D.

The purpose of SPEC-018 is to make the existing graph movable.

## Baseline Reference

Use:

```text
baselines/BASELINE-001-interface.md
baselines/BASELINE-001-interface/
examples/evaluations/spec-006-layout-interaction-20260903/
```

as the visual/interaction baseline.

Do not modify those artifacts.

## Navigation Fixture

The existing SPEC-006 benchmark graphs are too small to test continuous navigation honestly.

Create one deterministic **presentation/navigation fixture** with enough topology to exceed a single viewport.

The fixture exists only to test navigation mechanics.

### Requirements

- approximately 18–30 nodes;
- multiple connected local neighborhoods;
- enough depth/width that some nodes begin outside the viewport;
- explicit canonical-style relationship predicates/directions using existing vocabulary;
- no new predicate types;
- deterministic identities;
- deterministic layout;
- no live model calls;
- clearly labeled as experimental fixture content, not extracted source truth.

Prefer extending an existing domain fixture (Software Architecture, Economics, or another already familiar benchmark) rather than inventing a new visual grammar.

The fixture may be authored specifically for navigation testing.

Do not use the sparse SPEC-013 quantum parent as the primary navigation benchmark; it cannot exercise frontier movement adequately.

## World vs Viewport

Introduce a presentation-only world/camera model.

Conceptually:

```text
WORLD COORDINATES
stable deterministic node/edge positions
        ↓
CAMERA / VIEWPORT
x, y, scale
        ↓
SCREEN COORDINATES
```

Node world positions must remain stable while the camera moves.

Panning the camera must not recompute semantic layout.

## World Stability

This is essential for spatial memory.

If node A is left of node B before navigation, it should remain left of node B after panning/focusing unless a deliberately documented frontier-layout extension requires otherwise.

Do not continuously re-run layout on every selection.

The graph should feel like a place, not a slideshow.

## Pan / Drag

Support direct pointer/mouse drag of the graph surface.

Expected behavior:

```text
pointer down on empty canvas
      ↓
drag
      ↓
camera pans
      ↓
all graph visuals move together
```

Do not drag individual nodes in SPEC-018.

Cursor/interaction should make canvas movement discoverable without adding tutorial text.

## Frontier Concept

A frontier node is a visible concept whose connected local topology extends beyond the currently revealed/visible navigation region or viewport.

The experiment may implement frontier reveal using one of two approaches:

### A. Full world precomputed, viewport clips it

All fixture nodes exist in stable world coordinates from load time, but only the viewport exposes part of the world.

### B. Deterministic lazy reveal

The world contains a deterministic graph, but only a bounded local region is rendered/revealed initially. Focusing a frontier node reveals its already-known adjacent region.

Prefer the simpler implementation that best preserves stable spatial coordinates.

Do not use live semantic generation.

## Frontier Focus Behavior

Clicking a frontier node should:

1. preserve normal node selection semantics;
2. make that node the navigation focus;
3. smoothly move the camera so the focus approaches a comfortable central position;
4. reveal/show additional neighboring topology that was previously off-screen/hidden;
5. keep previously visible context spatially consistent;
6. avoid replacing the entire graph or navigating to a new page;
7. preserve detail/evidence behavior.

The desired feeling is:

> **the map moves and more knowledge comes into view.**

Not:

> **I opened another representation.**

## Focus Position

Do not require exact center if doing so causes excessive movement.

Use a deterministic comfortable focus zone near the viewport center.

If the selected node is already comfortably visible, selection should not trigger gratuitous camera movement.

## Animation

Use restrained smooth camera animation for focus/recenter.

Requirements:

- deterministic target;
- short enough not to feel slow;
- no physics bounce;
- no random motion;
- user can understand where the map moved;
- respect `prefers-reduced-motion` by moving immediately or reducing animation.

Do not animate graph topology independently from camera motion unless required for lazy reveal.

## Existing Selection vs Navigation

Preserve the SPEC-006 distinction:

```text
hover = temporary preview
click = persistent selection
```

Add navigation without conflating these.

A click may both select and recenter/reveal when the node qualifies as frontier.

A normal interior-node click should remain primarily selection/inspection.

## Detail Panel

Preserve SPEC-006-style detail/evidence inspection.

The detail panel should remain anchored to the viewport/UI, not move with world coordinates.

Selecting nodes/relationships while panning must keep detail synchronization intact.

Do not convert details into large in-map cards.

## Relationship Interaction

Preserve:

- edge click selection;
- hover preview;
- synchronized relationship control/detail/evidence;
- canonical direction;
- relationship labels;
- focus-visible keyboard treatment from SPEC-006A.

Panning must not break edge hit targets or selection.

## Navigation History

Track a lightweight focus history in presentation state.

Minimum:

```text
previous focused node IDs
previous camera targets/positions where useful
```

Provide a subtle way to return to the previous focus/viewport.

This may use browser-like back/forward controls or small map-navigation controls.

Do not make `Back to X` a large primary workflow button.

The dominant interaction remains spatial traversal.

## Overview / Home

Provide a small `Overview` or home affordance that returns the camera to the initial viewport.

It should not reload/rebuild the graph.

## Search

Search is optional for SPEC-018.

If implemented/reused:

```text
search concept
      ↓
select result
      ↓
camera moves to existing world position
      ↓
node selected
```

Do not scroll to a text section.

## Zoom

Do **not** implement semantic zoom in SPEC-018.

If basic geometric zoom is nearly free and necessary for navigation usability, it may be included only as camera scale:

```text
same graph
same semantic resolution
larger/smaller viewport scale
```

Do not reveal different semantic models based on zoom level.

Prefer pan/focus as the primary experiment.

## Semantic Resolution Explicitly Deferred

Do not implement:

```text
parent → child generated semantic model
resolution compilation
contextual expansion
semantic zoom
```

SPEC-018 isolates continuous topological navigation.

SPEC-007/008 resolution work remains preserved for a later integration experiment.

## Keyboard Accessibility

Preserve existing keyboard selection behavior.

Add reasonable keyboard navigation if straightforward:

- arrow/WASD pan is optional;
- Tab focus must remain visible;
- Enter/Space activation preserved.

Do not let accessibility expansion dominate the experiment.

## Determinism

The navigation fixture and world layout must regenerate byte-for-byte.

Camera runtime state is interactive and need not serialize every animation frame.

Initial world coordinates, initial viewport, frontier identities, and deterministic focus targets must be reproducible.

## Machine Evaluation

Report at least:

```text
fixture node count
fixture relationship count
world bounds
initial viewport bounds
initial visible node count
initial visible edge count
frontier-node count
number of focus targets tested
camera target determinism
world-coordinate stability
node relative-order stability
edge geometry stability under camera transform
selection synchronization after pan
relationship hit-target integrity after pan
history restoration correctness
overview restoration correctness
layout crossings/overlaps
baseline visual asset preservation
```

If lazy reveal is used, also report:

```text
initial revealed nodes
nodes revealed per tested frontier action
no duplicate identities
no world-coordinate mutation for already revealed nodes
```

## Automated Interaction Tests

Add focused tests where practical for:

```text
camera transform math
drag-pan state
focus target calculation
no-motion threshold for interior nodes
frontier classification
frontier reveal
world-coordinate stability
selection preservation
hover/selection independence
edge hit mapping after transform
history push/pop
overview reset
reduced-motion behavior
```

A heavy browser automation dependency is not required unless already justified by the repository.

Use existing in-app browser/manual verification for final interaction behavior if appropriate.

## Human Review Protocol

Human review is decisive.

After machine integrity verification, provide only:

```text
viewer command

Explore the map naturally. Try moving through it rather than systematically testing it.
```

Do not first explain implementation details.

Observe spontaneous behavior/reaction.

Then ask:

### Movement

- Does dragging the map feel obvious and natural?
- Does the graph feel like one continuous place?

### Frontier traversal

- When clicking something near the edge/frontier, does the resulting movement match what I expected?
- Do I understand where I came from?
- Does newly visible topology feel like discovering more of the same map?

### Spatial memory

- Do concepts remain where I mentally expect them to be?
- Does movement preserve orientation rather than reshuffle the graph?

### Graph quality

- Does this still feel like the SPEC-006 visual language I liked?
- Are relationships, trajectories, and directions still immediately understandable?

### Preference

> Would I rather navigate knowledge this way than with Explore/Back or the SPEC-016/017 alternatives?

## Success Criteria

SPEC-018 succeeds if:

1. SPEC-006 visual grammar remains recognizably intact;
2. drag/pan feels natural;
3. frontier selection smoothly brings new topology into view;
4. existing context moves coherently rather than disappearing;
5. world positions remain stable enough for spatial memory;
6. relationship trajectories/directions remain clear;
7. detail/evidence interaction remains intact;
8. navigation does not feel page-based;
9. owner strongly prefers it to Explore/Back and SPEC-016/017;
10. no semantic architecture is changed.

## Allowed Verdicts

Final product verdict must be exactly one of:

```text
CONTINUOUS_NAVIGATION_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

## No Live Model Calls

SPEC-018 is offline only.

Do not call OpenAI or any external semantic provider.

## Baseline Protection

Do not modify BASELINE-001 or SPEC-006 evaluation artifacts in place.

Implement isolated experimental viewer/assets or backward-compatible navigation assets.

The baseline must remain launchable separately for A/B comparison.

## Explicit Non-Goals

Do not implement:

- new graph visual metaphor;
- assertion-aware overview;
- presentation neighborhoods;
- Venn/hull topology;
- semantic extraction;
- semantic gates;
- production semantic-gate integration;
- semantic zoom;
- generated child models;
- course/Journey mode;
- 3D;
- force-directed runtime physics;
- node dragging;
- collaborative editing;
- mobile redesign.

## Evaluation Artifacts

Create:

```text
examples/evaluations/spec-018-continuous-graph-navigation-<date>/
```

Likely artifacts:

```text
navigation-fixture.json
world-layout.json
navigation-diagnostics.json
report.json
human-review-template.json
index.html
viewer assets
README.md
```

## Acceptance Criteria — Technical

- [ ] SPEC-006 visual grammar preserved.
- [ ] BASELINE-001/SPEC-006 artifacts unchanged.
- [ ] Deterministic navigation fixture created.
- [ ] Fixture large enough to exceed one viewport.
- [ ] Stable world-coordinate model exists.
- [ ] Camera/viewport transform separated from world layout.
- [ ] Canvas drag pans camera, not nodes.
- [ ] Frontier focus target deterministic.
- [ ] Frontier click preserves selection and recenters/reveals appropriately.
- [ ] Existing world context remains spatially stable.
- [ ] Previously visible nodes are not arbitrarily relaid out.
- [ ] Relationship labels/directions remain intact.
- [ ] Detail/evidence synchronization survives camera movement.
- [ ] Edge hit targets survive transforms.
- [ ] Hover vs persistent selection remains intact.
- [ ] Navigation history works if implemented.
- [ ] Overview/home restores initial camera without graph rebuild.
- [ ] Reduced-motion behavior supported for focus animation.
- [ ] No semantic IR/vocabulary changes.
- [ ] No live model calls.
- [ ] Full offline suite passes.

## Final Constraint

Do not improve navigation by changing the representation the owner already preferred.

The experiment asks one narrow question:

> **What happens if the SPEC-006 graph stops being a page and becomes a place?**
