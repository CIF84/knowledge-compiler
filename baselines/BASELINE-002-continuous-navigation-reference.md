# BASELINE-002 — Continuous Navigation Reference

## Status

Frozen reference artifact.

**This does not replace BASELINE-001.**

BASELINE-001 remains the preferred reference for focused learning / explanatory representation.

BASELINE-002 records what good looks like for **continuous spatial exploration and navigation**.

## Origin

Captured from the OPS-002 candidate after owner review of the continuous graph interface.

The owner explicitly judged the navigation behavior valuable enough to preserve independently even though the interface should not replace the older learning baseline.

Owner reaction:

> “this getting back to sensational again.”

> “i genuinely navigate with ease and can explore the map as i wish. dragging works, zoom works, interactivity works”

> “it's in fact so good, it deserves it's own freeze, i want to be able to reference it a future as ‘what good looks like’, restore it, or integrate it elsewhere”

## Purpose

BASELINE-002 freezes the successful **navigation primitive**, not a universal product UI.

It is the reference for:

```text
continuous knowledge world
camera / viewport separation
drag / pan
geometric zoom
spatial continuity
focus / recenter
selection while moving
relationship inspection while moving
local attention suppression
```

## What It Is Good At

BASELINE-002 is preferred for:

- open exploration;
- traversing a larger knowledge space;
- maintaining spatial continuity;
- following connections opportunistically;
- zooming between broad and local views of the same semantic resolution;
- selecting concepts/relationships while preserving map position;
- discovering adjacent topology.

## What It Is Not Yet Good At

BASELINE-002 is **not** the preferred learning interface.

Compared with BASELINE-001 it loses some of the explanatory scaffolding and representation context that make focused understanding easier.

Known limitations at freeze time:

- blue browser/SVG interaction artifacts remain visible in some click/drag interactions;
- the continuous map can dominate the workspace;
- focused learning/explanation is weaker than BASELINE-001;
- the navigation fixture is a process/system graph and does not prove heterogeneous representation integration;
- personalization/representation prioritization is not implemented.

These limitations are part of the historical reference and should not be silently rewritten.

## Interaction Invariants

Future work referencing BASELINE-002 should preserve unless explicitly testing them:

### World stability

Node positions exist in stable world coordinates independent of camera movement.

### Drag / pan

Dragging empty canvas moves the camera/world view rather than individual nodes.

### Geometric zoom

Wheel/trackpad zoom changes camera scale without changing semantic resolution or world coordinates.

### Selection

Concept and relationship selection remains possible while panned/zoomed.

### Focus suppression

Selected concepts/relationships and their relevant local topology receive stronger visual weight while unrelated visible topology remains spatially present but subdued.

### Detail synchronization

The detail/evidence surface remains viewport-anchored and synchronized with graph selection.

### Overview

Overview/Home returns to a stable broad camera state rather than rebuilding the graph.

## Relationship to BASELINE-001

The two baselines optimize different cognitive jobs.

```text
BASELINE-001
FOCUSED UNDERSTANDING / LEARNING

- parent context
- appropriate local representation
- explanatory scaffolding
- detail/evidence
- strong local cognitive framing


BASELINE-002
SPATIAL EXPLORATION / NAVIGATION

- continuous world
- pan
- zoom
- traverse
- spatial memory
- opportunistic discovery
```

Neither baseline supersedes the other.

The next product hypothesis is that they can coexist in one synchronized workspace.

## Architectural Interpretation

The successful decomposition is:

```text
SEMANTIC COMPILER
What is justified?

REPRESENTATION ENGINE
How is this structure best expressed?

NAVIGATION ENGINE
Where am I in the larger knowledge space?
```

Personalization should influence representation choice/prioritization, not semantic truth.

## Representation Principle

Preserve the founding principle:

> **The appropriate representation should depend upon the information structure.**

BASELINE-002's continuous graph is navigation infrastructure. It must not become evidence that all knowledge should be rendered as one generic network graph.

The future continuous knowledge world must be able to host or contextualize heterogeneous truthful representations such as:

- causal/system models;
- hierarchy;
- process chronology;
- dependency structures;
- feedback structures;
- structured propositions;
- future comparison/mathematical/spatial representations where justified.

## Personalization Principle

Preserve:

```text
semantic truth
      ↓
available truthful representations
      ↓
personalized representation ranking / preference
      ↓
cognitive interface
```

The owner strongly prefers systems-oriented representations, but that preference must not be hard-coded as universal truth.

## Freeze Rule

Future implementation may reuse, integrate, or restore BASELINE-002.

Do not mutate this baseline artifact in place to represent later improvements.

If navigation behavior materially improves, create a new baseline version after explicit owner approval.

## Baseline Decision

BASELINE-002 exists because the navigation behavior itself crossed the qualitative threshold of:

> **“what good looks like”**

while the complete interface did not cross the threshold required to replace BASELINE-001 for learning.

That distinction is intentional.
