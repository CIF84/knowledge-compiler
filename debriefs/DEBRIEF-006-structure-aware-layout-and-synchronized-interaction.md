# DEBRIEF-006 — Structure-Aware Layout and Synchronized Interaction

## Status

Accepted — very strong positive human outcome. BASELINE-001 captured.

## Implementation

Primary SPEC-006 implementation:

```text
e74412a28c7d4571adb8e5e74cf0a0d5d6270e8b
```

Follow-up maintenance/evidence increment:

```text
SPEC-006A
focus fix: 59d6cf12dc94cdee77e0f27daf34de916039f239
baseline capture: e5237139c68a676cf15d4151e39bb85a80407adf
```

SPEC-006 changed only presentation behavior/layout while preserving fixed SPEC-005 semantic artifacts.

## Primary Question

> Can structure-aware deterministic layout plus synchronized semantic selection make the existing representations materially easier to parse and manipulate as coherent mental models, without adding semantic inference or general frontend complexity?

## Outcome

**Yes — strongly, for the owner benchmark.**

The owner compared SPEC-006 against SPEC-005 using the same fixed content and described SPEC-006 as:

> “insanely good”

The only criticism was an unintended browser-generated blue SVG focus rectangle that appeared when selecting a relationship. That artifact was subsequently corrected in SPEC-006A without removing keyboard accessibility.

This is stronger evidence than SPEC-005 because the owner evaluated a direct before/after change while semantic content was held constant.

The experiment therefore supports the hypothesis that both **spatial grammar** and **synchronized semantic interaction** materially affect cognitive usefulness.

## What Changed

### Structure-aware deterministic layout

SPEC-006 introduced presentation-only layout metadata and deterministic layout logic.

Current strategies:

```text
HIERARCHY          → top-down layered hierarchy
CAUSAL_PATH        → left-to-right directional layering
DEPENDENCY_CHAIN   → left-to-right directional layering
PROCESS_CHAIN      → compact chronological axis
FEEDBACK_CANDIDATE → explicit loop geometry
```

No force simulation, randomness, graph library, frontend framework, or build pipeline was added.

### Shared semantic interaction state

The viewer now keeps persistent selection and temporary preview separate.

```text
CLICK = persistent selection
HOVER = temporary preview
```

Hovering another object does not destroy persistent selection; leaving the hover restores it.

### Relationship synchronization

A stable edge identity synchronizes:

```text
connector / arrow
relationship label
relationship control
right-side detail
source evidence
```

These now behave as one semantic object rather than independent widgets.

### Node selection

Node selection persists, populates node detail, and clears conflicting edge selection.

### Canonical direction

Semantic arrow direction remains immutable. Hierarchy can place the whole spatially above its parts while preserving canonical `PART_OF` arrows from part to whole.

This confirms that **layout orientation and semantic direction are separate concepts**.

## Technical Verification

SPEC-006 reported:

```text
88 passed in 0.15s
```

SPEC-006A reported:

```text
91 passed in 0.19s
```

The committed SPEC-006 evaluation recorded:

- five-domain integrity complete;
- semantic content unchanged;
- reciprocal relationship-selection identity complete;
- canonical direction preserved;
- provenance preserved;
- no node overlaps in benchmark layouts;
- zero reported center-line crossings in benchmark layouts;
- biology remained explicitly empty.

Independent repository review confirmed SPEC-006 was one focused commit after the SPEC and that SPEC-006A added only the focus correction, baseline documentation/screenshots, and associated tests.

## Human Review

### Economics

The economics causal representation became significantly easier to parse spatially.

The layered causal grammar makes branching and convergence around market price legible at a glance while preserving the missing feedback-loop warning.

Selection synchronizes the chosen edge with its relationship control and explanation/evidence, making the relationship feel like one object.

### Software Architecture

The hierarchy reads immediately as a whole-with-components model.

The spatial whole-above-parts grammar works even though canonical `PART_OF` arrows correctly point upward from components to the service.

### Electromagnetism

The feedback candidate now reads visibly as a loop rather than merely a path with a returning edge.

Existing state-collapse limitations remain explicitly warned rather than cosmetically hidden.

## SPEC-006A — Focus Artifact

### Cause

The transparent, wide SVG relationship hit path receives focus after mouse click. Without custom focus styling, the browser rendered its default blue focus outline around the SVG path's rectangular bounding box.

### Fix

The viewer now suppresses the inappropriate default outline while preserving an intentional keyboard-only focus treatment:

```css
.edge-hit:focus { outline:none; }
.edge-hit:focus-visible {
  stroke:var(--preview);
  stroke-width:6;
  stroke-dasharray:7 4;
}
```

Keyboard focusability, ARIA state, button role, and Enter/Space activation remain intact.

This is a useful UI principle for the project:

> Remove browser-default visual noise only when an intentional accessible interaction state replaces it.

## BASELINE-001

The post-fix interface was preserved as:

```text
baselines/BASELINE-001-interface.md
```

with five curated screenshots:

- economics causal overview;
- economics synchronized relationship selection;
- software architecture hierarchy selection;
- electromagnetism feedback candidate;
- biology truthful empty state.

BASELINE-001 is **not a frozen final design**. It is the first empirically successful cognitive-interaction baseline.

It preserves this grammar:

```text
structure visible at a glance
        +
structure-specific spatial grammar
        +
click = persistent semantic selection
        +
hover = temporary preview
        +
edge / control / detail / evidence behave as one object
        +
source provenance remains immediately inspectable
        +
weak / empty structure remains truthful
```

Future meaningful interface changes should compare against this baseline rather than assuming newer/more sophisticated UI is better.

## Key Findings

### 1. Layout is semantic, not cosmetic

Holding semantics constant while changing geometry materially changed the owner's ability to read the model.

The project should therefore continue treating spatial grammar as part of representation design.

### 2. Semantic identity should be reflected in interaction identity

The same relationship rendered in several surfaces is cognitively easier to use when those surfaces behave as one selected object.

This principle is likely reusable in future progressive disclosure and semantic navigation.

### 3. Simple deterministic layouts are sufficient at current scale

The project does not yet need a general graph-layout engine.

A compact custom deterministic layout provides strong cognitive value on the current benchmark graphs without adding infrastructure complexity.

This decision should be revisited only when graph scale/complexity produces evidence that the custom approach fails.

### 4. A successful UI baseline is now worth preserving

The project now has enough direct product evidence that future UI changes can regress cognitive usefulness even while appearing more polished.

BASELINE-001 therefore becomes a comparison artifact, not merely a historical screenshot.

### 5. Human evaluation is increasingly product-specific

Machine metrics can verify crossings, overlaps, direction, provenance, and identity mapping, but they cannot establish that the result is easier to think with.

Direct owner use remains the decisive acceptance gate for cognitive-interface experiments.

### 6. Fixed upstream artifacts make UI experiments causally clean

Because semantic content did not change between SPEC-005 and SPEC-006, the strong improvement can be reasonably attributed to layout and interaction rather than extraction variance.

This validates the current experiment-selection operating model.

## Decisions

### Accept SPEC-006

The primary question is answered positively for the owner benchmark.

### Promote synchronized semantic selection from provisional to active

Shared selection state across graph/control/detail/evidence is now validated product behavior.

### Promote structure-aware layout from provisional to active

Structure-specific spatial grammar is now validated product behavior at current benchmark scale.

### Preserve BASELINE-001

Future material viewer changes should compare against it on relevant dimensions:

```text
cognitive orientation
spatial legibility
interaction coherence
cognitive load
trust / provenance clarity
overall learning usefulness
```

Use qualitative `BETTER / SAME / WORSE`; do not create a fake aggregate score.

### Keep presentation downstream

No evidence supports moving layout or interaction concerns into semantic IR or structure detection.

### Keep the viewer simple

No evidence justifies a frontend framework, general graph engine, or design-system project yet.

### Do not repair upstream semantic weaknesses inside presentation

Known event/state, chronology, polarity, and endpoint limitations remain visible and correctly attributed upstream.

## Remaining Limitations

- Long node labels may still require detail inspection.
- Layout logic targets the current small graph scale.
- Crossing diagnostics approximate center-line crossings rather than all curve/label collisions.
- Electromagnetism retains collapsed changing-field states and lacks field → force → motion composition.
- Economics still lacks the edge needed to close the feedback cycle.
- Biology still lacks explicit chronology and remains empty.
- History retains its actor endpoint limitation.
- Feedback polarity remains unclassified.
- Human usefulness evidence is still primarily owner-based rather than population-level.

## Highest-Value Next Question

The interface itself is now strong enough that the next experiment should probably move from **representation coherence** to **semantic navigation / progressive disclosure**.

Candidate question:

> Can a learner move from a high-level model into progressively deeper explanations, mechanisms, and evidence without losing orientation in the larger system?

This would test the original “Google Maps for knowledge” direction while preserving BASELINE-001 as the control.

However, the next SPEC should be chosen after updating project health and considering whether upstream event/state weaknesses now block the desired navigation depth.

## Final Conclusion

SPEC-006 is the strongest product result so far.

The project has now demonstrated a sequence:

```text
source-grounded semantic model
        ↓
deterministic higher-order structure
        ↓
interactive representation
        ↓
structure-aware spatial grammar
        ↓
synchronized semantic interaction
        ↓
strong owner preference for learning with the artifact
```

The critical product question has shifted.

It is no longer primarily:

> Can Knowledge Compiler create a useful representation?

It is becoming:

> How should a learner navigate and deepen a representation that already works?
