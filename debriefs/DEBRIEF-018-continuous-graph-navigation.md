# DEBRIEF-018 — Continuous Graph Navigation

## Status

Product verdict: `MIXED` with a validated navigation primitive.

The experiment is the first post-SPEC-006 interface direction that clearly returns the project toward the preferred interaction model, but it does not yet preserve enough of the SPEC-006 baseline to become the new baseline.

## Owner's First Impression

> “we're finally back on track.”

That is the strongest positive result since the representation detour.

The owner also immediately identified regressions:

- the blue browser focus/selection artifact returned;
- geometric zoom is missing;
- selected-focus suppression is much weaker than SPEC-006;
- multiple useful baseline interaction/visual behaviors were not preserved;
- the generic continuous graph raises concern that representation personalization/structure matching could be lost.

## What Passed

The central SPEC-018 hypothesis is supported:

> The graph can behave like a continuous spatial world rather than a page.

The owner can finally move through the map.

This validates the world/camera separation as a useful interaction primitive.

## What Did Not Pass

SPEC-018 is not yet an improvement over SPEC-006 overall.

Continuous movement alone does not compensate for regressions in:

- focus hierarchy;
- noise suppression;
- interaction polish;
- visual clarity;
- zoom;
- previously fixed browser focus treatment.

Therefore do not snapshot SPEC-018 itself as the new baseline.

## Immediate Restoration Requirements

Before another conceptual experiment, restore the known-good interface behaviors around the continuous canvas.

### 1. Restore SPEC-006A focus treatment

Mouse interaction must not show the browser's default blue rectangular outline around SVG hit regions.

Keyboard accessibility remains intact with intentional `:focus-visible` treatment.

This is a regression fix, not an experiment.

### 2. Add geometric camera zoom

Zoom is mandatory for a continuous knowledge world.

Support at least:

- mouse wheel / trackpad gesture;
- zoom around pointer or another spatially stable focal point;
- deterministic min/max scale;
- Overview/Home restores initial camera scale/position;
- world coordinates remain unchanged;
- semantic resolution remains unchanged.

This is **geometric zoom only**.

Semantic zoom remains deferred.

### 3. Restore focus suppression

Selection should create an attention hierarchy while preserving spatial context.

Conceptually:

```text
selected object                         strongest
its canonical relationships            strongest
immediate semantic neighbors           strong
nearby contextual topology             subdued
unrelated visible topology             strongly subdued
```

Do not remove unrelated nodes or relayout them. Suppression is visual attention control over a stable world.

### 4. Preserve continuous movement

The restoration pass must not regress:

- drag/pan;
- stable world coordinates;
- frontier traversal/focus recenter;
- spatial continuity;
- detail synchronization.

## Representation Personalization Is Still Core

Continuous navigation is a transport mechanism, not the universal representation.

Preserve the earlier architectural principle:

> **The appropriate representation should depend upon the information structure.**

And the cognitive premise that motivated the project:

> The representation of information should match the representation the learner's brain wants to construct.

For the owner, systems representations are especially effective, but this is a personalization preference over truthful representations—not a reason to turn every domain into one generic network graph.

## Representation Architecture

The future architecture remains:

```text
TRUSTED SEMANTIC MODEL
        ↓
STRUCTURE DETECTION
        ↓
AVAILABLE REPRESENTATIONS
        ├── causal/system
        ├── hierarchy
        ├── process/chronology
        ├── dependency
        ├── feedback
        ├── comparison
        └── future truthful forms
        ↓
PERSONALIZED PRIORITIZATION
        ↓
CONTINUOUS KNOWLEDGE WORLD
```

The continuous world hosts/navigates appropriate representations. It does not replace representation selection.

## Personalization Boundary

Personalization must not change semantic truth.

```text
semantic truth
    │ invariant
    ▼
available truthful representations
    │ personalized preference/ranking
    ▼
cognitive interface
```

Users should retain the ability to switch representation presets because personalization is a preference hypothesis, not authority.

## Two Types of Zoom

Keep these conceptually separate.

### Geometric zoom

```text
same semantic model
same representation
camera scale changes
```

Required now.

### Semantic zoom

```text
overview
→ subsystem
→ mechanism
→ detail
```

Deferred until the continuous baseline is restored and frozen.

## Operating-Model Lesson Reinforced

The visual baseline was not preserved strictly enough during SPEC-018.

Future contracts must distinguish:

```text
FROZEN BASELINE BEHAVIOR
vs
EXPERIMENTAL DELTA
```

Acceptance should fail if frozen behavior regresses, even when the new experimental capability works.

## Decision

1. Close SPEC-018 as `MIXED`.
2. Accept continuous world/camera navigation as a validated primitive.
3. Do not call SPEC-018 an overall improvement over SPEC-006.
4. Perform a baseline-restoration pass before any new conceptual UX experiment.
5. Restore SPEC-006A focus treatment.
6. Add geometric zoom.
7. Restore SPEC-006 focus suppression/attention hierarchy.
8. Preserve continuous pan/frontier navigation.
9. Preserve representation selection/personalization as a separate architecture dimension.
10. After owner approval, snapshot the combined result as `BASELINE-002 — Continuous Graph Interface`.

## Next Step

Prepare a bounded restoration contract rather than another exploratory SPEC.

Suggested name:

`OPS-002 — Continuous Interface Baseline Restoration`

The goal is not new product behavior. It is to combine:

```text
SPEC-006 visual/selection quality
+
SPEC-006A focus fix
+
SPEC-018 continuous navigation
+
geometric camera zoom
```

into one coherent candidate baseline.

## Final Conclusion

SPEC-018 found the missing movement primitive.

The next task is integration discipline: restore the known-good interaction quality around that primitive without reopening representation design.
