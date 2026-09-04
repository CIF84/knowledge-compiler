# OPS-002 — Continuous Interface Baseline Restoration

## Status

Ready for implementation.

## Type

Integration/restoration contract, not a new product hypothesis.

## Objective

Create one coherent candidate interface by combining only already validated/required behaviors:

```text
SPEC-006 visual + selection grammar
+
SPEC-006A browser-focus fix
+
SPEC-018 continuous world/camera navigation
+
required geometric camera zoom
```

Do not introduce a new representation metaphor.

## Intended Outcome

After owner review, this may become:

```text
BASELINE-002 — Continuous Graph Interface
```

Do not create/finalize BASELINE-002 until owner explicitly approves the restored interface.

## Frozen Inputs

### Visual/interaction baseline

Use:

```text
baselines/BASELINE-001-interface.md
baselines/BASELINE-001-interface/
examples/evaluations/spec-006-layout-interaction-20260903/
```

### Focus regression fix

Use the accepted SPEC-006A behavior/commit history documented in repository artifacts:

- mouse click: no default blue browser outline;
- keyboard focus: intentional visible focus path;
- Enter/Space selection remains functional.

### Continuous navigation primitive

Use SPEC-018 world/camera behavior as the movement baseline:

- stable world coordinates;
- drag/pan;
- focus/recenter/frontier movement;
- continuous spatial context;
- viewport-anchored detail panel.

## Frozen Dimensions

Do not change:

```text
semantic IR
canonical predicates
proposition vocabulary
semantic extraction
semantic gates
representation selection architecture
SPEC-006 graph visual grammar except where required for camera transform
relationship labels/directions
selection semantics
hover semantics
detail/evidence semantics
```

## Experimental / Restoration Delta

Only these areas may materially change:

```text
camera zoom
focus suppression restoration
browser focus artifact regression
integration glue needed to preserve SPEC-006 behavior under pan/zoom
```

Continuous pan/frontier navigation already exists and should be preserved rather than redesigned.

## Requirement 1 — Remove Blue Mouse-Focus Artifact

Restore SPEC-006A behavior exactly in intent.

Mouse clicking a node/edge/canvas control must not produce the browser's default blue outline/bounding rectangle.

Keyboard users must retain intentional focus visibility.

Required distinction:

```css
mouse focus
→ no default browser outline

keyboard :focus-visible
→ intentional accessible focus treatment
```

Do not remove keyboard focusability, roles, ARIA state, Enter, or Space behavior to solve the artifact.

Verify after pan and zoom because transformed SVG hit regions must behave identically.

## Requirement 2 — Geometric Camera Zoom

Add geometric zoom to the continuous camera.

### Inputs

Support desktop interaction appropriate to the current review environment:

- mouse wheel;
- trackpad scroll/pinch behavior where browser events permit;
- optional small `+` / `−` controls if useful for discoverability/accessibility.

Do not require buttons as the primary zoom interaction.

### Semantics

Zoom changes only camera scale.

```text
world coordinates: unchanged
semantic model: unchanged
representation: unchanged
selection: unchanged
```

### Pointer-centered zoom

Prefer zooming around the pointer/cursor location so the world point under the cursor remains approximately stable on screen.

If browser trackpad event behavior makes exact pointer anchoring impractical, use the nearest deterministic equivalent and document it.

### Bounds

Define deterministic minimum/maximum scale.

Bounds should allow:

- useful overview of a larger graph region;
- useful close inspection of local topology;
- readable labels at practical scales.

Avoid extreme zoom where labels/nodes become unusable.

### Overview/Home

Overview restores:

```text
initial camera x
a initial camera y
initial scale
```

without rebuilding/re-laying out the graph.

### Selection during zoom

Zoom must not clear selection or detail state.

### Relationship hit testing

Edge/node hit regions must remain aligned with rendered geometry at all supported scales.

## Requirement 3 — Restore Focus Suppression

Reintroduce the attention hierarchy that made SPEC-006 selection cognitively effective.

### Selected node

When a node is persistently selected:

- selected node remains strongest;
- directly connected canonical relationships remain strong;
- direct semantic neighbor nodes remain strong or moderately strong;
- unrelated visible nodes/edges become substantially subdued;
- world positions do not change.

### Selected relationship

When a relationship is selected:

- selected connector/label/source/target remain strongest;
- unrelated topology becomes subdued;
- synchronized detail/evidence remains visible;
- world positions do not change.

### Hover

Hover preview should temporarily emphasize the hovered object/local context without destroying persistent selection.

When hover ends, persistent selection suppression state returns.

### Clear selection

Clearing selection restores normal full-map visual weight.

### Camera independence

Suppression is a rendering/attention state, not a camera/layout state.

Panning and zooming while something is selected must preserve suppression correctly.

## Suppression Design

Start from SPEC-006's known-good styling rather than inventing a new opacity system.

If exact reuse is technically impossible because SPEC-018 uses different isolated assets, reproduce the baseline behavior as closely as possible and document deviations.

Do not hide unrelated nodes completely by default; spatial context should remain perceptible.

## Requirement 4 — Preserve Continuous Navigation

Do not regress:

- drag/pan;
- stable world coordinates;
- focus/recenter behavior;
- frontier traversal;
- navigation history if present;
- Overview/Home;
- detail panel anchoring;
- edge/node selection after transforms.

Pan + zoom must compose as one camera transform.

## Requirement 5 — Preserve Representation Grammar

This restoration pass must not flatten all information structures into a new generic representation architecture.

The current navigation fixture may remain a process/system graph for interaction testing, but implementation must preserve the ability for existing representation types to render through the camera layer.

At minimum verify camera-transform compatibility with representative existing layouts where technically straightforward:

```text
hierarchy
causal/layered
process/chronology
dependency
feedback candidate
```

This may be done through deterministic fixtures/tests rather than building one huge combined world.

Do not redesign these representations.

## Personalization Architecture — Preserve, Do Not Implement

Record but do not implement the future boundary:

```text
trusted semantics
→ detected structures
→ available truthful representations
→ personalized representation priority/preset
→ continuous knowledge world
```

No user-model/personalization engine is required in OPS-002.

Do not hard-code the owner's systems-thinking preference into semantic truth or universal defaults.

## No Semantic Zoom

Do not couple camera scale to semantic-resolution changes.

OPS-002 zoom is geometric only.

Do not invoke SPEC-007/008 child resolution.

## No Live Model Calls

OPS-002 is entirely offline.

Do not call OpenAI or external providers.

## Browser Verification

Manually verify in the current supported desktop browser environment at minimum:

### Mouse

- click node: no blue browser artifact;
- click edge: no blue browser artifact;
- drag canvas: pan works;
- wheel/trackpad: zoom works;
- zoom around pointer behaves spatially coherently;
- selected focus suppression survives pan/zoom;
- edge/node hit targets remain aligned.

### Keyboard

- Tab produces intentional focus-visible treatment;
- Enter/Space activate focused interactive graph elements;
- no accessibility regression from blue-outline fix.

### Overview

- restores initial x/y/scale;
- does not rebuild graph;
- selection behavior follows the documented choice consistently.

### Console

No warnings/errors from normal interaction.

## Automated Tests

Add focused offline tests for:

```text
camera scale bounds
pointer-centered zoom transform math
pan + zoom composition
Overview x/y/scale restoration
world-coordinate invariance under zoom
selection persistence under camera change
focus suppression state calculation
hover + persistent selection interaction
clear-selection restoration
hit-target transform alignment where testable
focus-visible class/style invariants
representation-layout camera compatibility
baseline artifact immutability
```

Keep the full suite passing.

## Machine Diagnostics

Report:

```text
world-coordinate hash before/after camera operations
camera min/max scale
initial scale
zoom target tests
pan+zoom transform tests
selected node suppression counts
selected relationship suppression counts
hover restoration tests
Overview restoration
baseline asset hashes
browser verification result
console result
```

## Human Review Protocol

After implementation/machine verification, provide only:

```text
<viewer command>

Try the map again. Move, zoom, select concepts and relationships, and follow whatever catches your attention.
```

Do not first provide implementation metrics.

Owner review should answer:

- Does this now feel at least as visually clear as SPEC-006?
- Is the blue artifact gone?
- Does zoom feel indispensable/natural rather than bolted on?
- Does selected-focus suppression reduce noise appropriately?
- Do pan + zoom + focus feel like one coherent map interaction?
- Are relationship direction/trajectories still easy to understand?
- Would I now accept this as the continuous successor to BASELINE-001?

## Candidate Baseline Gate

Do **not** create BASELINE-002 automatically.

If owner explicitly approves the interface after human review, then create a separate baseline-capture task preserving:

- documentation;
- representative screenshots;
- exact assets;
- behavior checklist;
- commit SHA;
- regeneration/review commands.

## Acceptance Criteria

- [ ] Blue mouse-focus artifact removed.
- [ ] Keyboard focus-visible treatment preserved.
- [ ] Enter/Space behavior preserved.
- [ ] Geometric zoom implemented.
- [ ] Zoom has deterministic min/max bounds.
- [ ] Zoom preserves world coordinates.
- [ ] Pointer-centered/spatially coherent zoom verified.
- [ ] Pan and zoom compose correctly.
- [ ] Overview restores x/y/scale.
- [ ] Selection persists appropriately through pan/zoom.
- [ ] SPEC-006-like focus suppression restored.
- [ ] Unrelated topology remains spatially present but subdued.
- [ ] Hover does not destroy persistent selection.
- [ ] Relationship selection suppression works.
- [ ] Edge/node hit targets remain correct under transforms.
- [ ] Continuous navigation remains functional.
- [ ] Existing representation grammar remains compatible with camera layer.
- [ ] No semantic zoom.
- [ ] No semantic IR/vocabulary changes.
- [ ] No live model calls.
- [ ] BASELINE-001/SPEC-006 artifacts unchanged.
- [ ] Full offline suite passes.
- [ ] Browser console clean.
- [ ] Human review remains required before BASELINE-002.

## Required Handoff

Report:

1. exact baseline assets referenced;
2. baseline hash/immutability verification;
3. blue-artifact fix implementation;
4. keyboard-focus preservation;
5. zoom event strategy;
6. camera transform math;
7. min/max/initial scale;
8. pointer-centered zoom behavior;
9. pan+zoom composition;
10. Overview restoration behavior;
11. focus suppression implementation;
12. selected-node behavior;
13. selected-relationship behavior;
14. hover/persistent-selection behavior;
15. clear-selection behavior;
16. transform hit-target integrity;
17. continuous-navigation preservation;
18. representation-layout compatibility verification;
19. semantic/personalization boundaries preserved;
20. confirmation no semantic zoom;
21. confirmation no live calls;
22. machine diagnostics;
23. exact offline test result;
24. browser mouse verification;
25. browser keyboard verification;
26. console verification;
27. dependencies added/removed;
28. complexity impact;
29. known UX weaknesses;
30. deviations;
31. exact viewer command;
32. baseline comparison command;
33. human review status `PENDING_OWNER_REVIEW` unless completed;
34. implementation commit SHA;
35. final/evaluation commit SHA if separate;
36. push confirmation;
37. `HEAD == origin/main` confirmation;
38. working-tree state;
39. confirmation BASELINE-002 was not created without owner approval;
40. confirmation no `DEBRIEF-OPS-002` was created unless explicitly requested.

## Final Constraint

This task is integration, not invention.

The target is:

> **SPEC-006 clarity + SPEC-018 movement + geometric zoom, with no regression in truth, representation grammar, or focus behavior.**
