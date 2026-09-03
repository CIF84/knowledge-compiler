# BASELINE-001 — Structure-Aware Interface

## Status

Captured on 2026-09-03 after the SPEC-006 owner review and the SPEC-006A focus-visible correction.

> BASELINE-001 is the first interface for which direct owner evaluation produced a very strong positive cognitive/learning response. It is a comparison baseline, not a frozen final design.

## Origin

- Originating experiment: `SPEC-006 — Structure-Aware Layout and Synchronized Interaction`
- Accepted SPEC-006 implementation: `e74412a28c7d4571adb8e5e74cf0a0d5d6270e8b`
- Post-focus-fix implementation: `59d6cf12dc94cdee77e0f27daf34de916039f239`
- Fixed semantic input: committed SPEC-005 five-domain representation artifacts
- Captured viewer: `examples/evaluations/spec-006-layout-interaction-20260903/`

The baseline was captured because the project owner judged SPEC-006 materially better than SPEC-005 and reported a very strong positive cognitive and learning response. The successful properties should remain independently reviewable before later experiments change the interface.

## What This Baseline Preserves

BASELINE-001 preserves a cognitive interaction grammar rather than a pixel-perfect visual contract:

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

### Interaction grammar

- A mouse click creates persistent single-object selection.
- Hover temporarily previews another node or relationship without destroying persistent selection.
- Leaving the preview restores persistent selection.
- A rendered relationship connector, its arrow and label, its relationship control, its detail, and its evidence share one semantic identity.
- A node and its detail surface share one semantic identity.
- Empty graph space or **Clear selection** resets selection.
- Representation and domain changes clear stale selection.
- Keyboard focus remains available on graph nodes and relationship hit targets; Enter or Space activates them.
- Relationship keyboard focus uses an intentional dashed amber path. Mouse activation does not show the browser's unrelated rectangular SVG outline.

### Structure-aware layout grammar

| Structure | Preserved spatial grammar |
| --- | --- |
| Hierarchy | Top-down layers with the whole above its parts; canonical part-to-whole arrows remain upward where required |
| Causal model | Left-to-right deterministic layers exposing branching and convergence |
| Dependency model | Left-to-right deterministic layers without relabeling dependency as causality |
| Process chain | Compact left-to-right chronological axis |
| Feedback candidate | Explicit opposing arcs that make the candidate cycle visible |

## What Tested Well

The owner evaluation found that the interface:

- materially improved cognitive orientation compared with SPEC-005;
- made the representation feel like one coherent model rather than a diagram plus separate controls;
- made structure and directional relationships faster to parse;
- made persistent synchronized selection valuable for active exploration;
- kept evidence close enough to the selected semantic object to support trust;
- made the feedback candidate visibly loop-like;
- preserved honest sparse and empty states rather than manufacturing structure.

This is strong qualitative evidence from the project owner, not a measured learning result or a population-level conclusion.

## Canonical Screenshots

The screenshots capture representative states of the local viewer without desktop or browser chrome:

| State | File |
| --- | --- |
| Economics causal overview | `BASELINE-001-interface/economics-causal-overview.jpg` |
| Economics synchronized selected relationship | `BASELINE-001-interface/economics-selected-shortage-causes-pressure.jpg` |
| Software Architecture hierarchy with selected relationship | `BASELINE-001-interface/software-architecture-hierarchy-selected-part-of.jpg` |
| Electromagnetism feedback candidate | `BASELINE-001-interface/electromagnetism-feedback-candidate.jpg` |
| Biology truthful empty state | `BASELINE-001-interface/biology-truthful-empty-state.jpg` |

These images are curated evidence, not golden screenshot tests. Small rendering differences across browsers or platforms do not invalidate the baseline when the cognitive grammar remains intact.

## Known Limitations

BASELINE-001 deliberately preserves the following limitations:

- Long node labels may be truncated in the graph and require detail inspection.
- Layout algorithms target the current small benchmark scale.
- Crossing diagnostics are approximate.
- Electromagnetism retains collapsed changing-field states and lacks the field → force → motion composition.
- Economics lacks the edge required to close the market feedback loop.
- Biology lacks explicit chronology and therefore remains empty.
- History retains its actor endpoint limitation.
- The strong human evaluation comes from the project owner rather than a broader user population.

## Future Comparison Rule

Future meaningful UI or interaction changes should compare themselves with BASELINE-001 on the dimensions relevant to the change:

```text
cognitive orientation
spatial legibility
interaction coherence
cognitive load
trust / provenance clarity
overall learning usefulness
```

Use qualitative verdicts:

```text
BETTER / SAME / WORSE
```

Do not combine these dimensions into a fake aggregate score.

Visual novelty, additional functionality, or a more sophisticated frontend architecture is not sufficient reason to replace this baseline. A future interface may change typography, spacing, component shapes, responsive behavior, implementation technology, or navigation, but it should demonstrate that the relevant learning experience is better or that a documented trade-off is worthwhile.

BASELINE-001 should remain available after later interfaces replace it so future experiments retain an empirically successful comparison point.
