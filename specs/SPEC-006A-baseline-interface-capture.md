# SPEC-006A — Baseline Interface Capture

## Status

Ready for implementation.

## Purpose

SPEC-006 produced a very strong positive owner evaluation. The structure-aware layout and synchronized interaction were perceived as materially better than SPEC-005, with no substantive criticism except one small browser-focus artifact: selecting an SVG relationship hit target can produce an unwanted blue rectangular focus outline around part of the graph.

Before moving into the next product experiment, preserve this interface as the first empirically successful UI/interaction baseline.

This is a maintenance-and-evidence increment, not a new product experiment.

## Objective

1. Remove the unintended blue rectangular SVG focus artifact without removing keyboard accessibility.
2. Preserve the post-fix SPEC-006 interface as `BASELINE-001`.
3. Capture a very small curated screenshot set and a concise written baseline explaining what is being preserved and why.
4. Do not otherwise redesign, polish, or expand the interface.

## Required Context

Read:

- `debriefs/DEBRIEF-005-minimal-representation.md`
- `specs/SPEC-006-structure-aware-layout-and-synchronized-interaction.md`
- current SPEC-006 implementation at commit `e74412a28c7d4571adb8e5e74cf0a0d5d6270e8b`
- current viewer CSS/JS and SPEC-006 evaluation artifacts

Do not create `DEBRIEF-006` yet.

## Scope

### Focus-visible fix

The selected relationship should continue to be represented by the intended application state:

```text
selected connector / arrow emphasis
+ selected relationship control
+ selected detail / evidence
```

The browser must not draw the large default blue rectangular focus outline around the SVG relationship hit target.

Preserve keyboard focusability and keyboard selection. Replace/suppress only the inappropriate default focus rendering and provide an intentional `:focus-visible` treatment consistent with the current interaction grammar.

A keyboard user must still be able to identify the focused node/relationship before activating it.

Do not solve this by removing `tabindex`, keyboard handlers, roles, or accessibility state.

### Baseline capture

Create a baseline document, preferably:

```text
baselines/BASELINE-001-interface.md
```

The document should state clearly:

> BASELINE-001 is the first interface for which direct owner evaluation produced a very strong positive cognitive/learning response. It is a comparison baseline, not a frozen final design.

Record:

- originating SPEC and implementation commit;
- post-focus-fix commit;
- why the baseline was captured;
- core interaction grammar;
- structure-aware layout grammar;
- what specifically tested well;
- known limitations that remain;
- what future UI changes must compare against;
- explicit warning that visual novelty or additional functionality is not sufficient reason to replace the baseline.

### Curated screenshots

Capture only a small canonical set, ideally four states:

1. Economics — causal overview.
2. Economics — selected relationship showing synchronized connector/control/detail/evidence.
3. Software Architecture — hierarchy with selected relationship.
4. Electromagnetism — feedback candidate.

A fifth screenshot may be added only if it captures a materially different product state, such as Biology's truthful empty state.

Store under a clear path such as:

```text
baselines/BASELINE-001-interface/
```

Use stable descriptive filenames.

Screenshots should show the application itself cleanly. Avoid capturing unrelated desktop/app chrome where practical.

If deterministic automated screenshot capture would require a heavy browser dependency, do not add one solely for this baseline. A lightweight existing browser capability or manual capture is acceptable.

## Baseline Meaning

This baseline preserves a **cognitive interaction grammar**, not a pixel-perfect visual contract.

The important preserved properties are:

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

Future interfaces may change typography, spacing, component shapes, responsive behavior, technology, or navigation if evidence supports doing so.

## Future Comparison Rule

Future meaningful UI/interaction changes should explicitly ask whether they beat BASELINE-001 on relevant dimensions:

```text
cognitive orientation
spatial legibility
interaction coherence
cognitive load
trust / provenance clarity
overall learning usefulness
```

Use qualitative comparison where appropriate:

```text
BETTER / SAME / WORSE
```

Do not create a fake aggregate score.

BASELINE-001 should remain available even after later interfaces replace it.

## Known Limitations To Preserve Honestly

Do not repair these as part of the baseline capture:

- long node labels may be truncated in-graph and require detail inspection;
- layout algorithms target the current small benchmark scale;
- crossing diagnostics are approximate;
- electromagnetism retains upstream state collapse and missing field → force → motion composition;
- economics still lacks the edge required to close the market feedback loop;
- biology lacks chronology and remains empty;
- history retains its actor endpoint limitation;
- the strong human evaluation is from the project owner, not a broader user population.

## Non-Goals

Do not:

- redesign the viewer;
- change layout algorithms;
- change semantic extraction;
- change `KnowledgeModel`;
- change `DetectedStructureSet`;
- change relationship semantics;
- add progressive disclosure;
- add navigation architecture;
- add simulation;
- add animations;
- introduce a frontend framework;
- introduce a screenshot-testing framework solely for this task;
- polish typography/spacing/components beyond what is strictly required for the focus-visible fix;
- modify unrelated README/ROADMAP working-tree changes;
- write `DEBRIEF-006`.

## Validation

Run the existing offline test suite.

Add a focused regression check where practical to ensure:

- SVG relationship hit targets remain keyboard-focusable;
- keyboard activation remains supported;
- intentional focus-visible styling exists;
- the default blue bounding-box artifact is no longer present during normal click selection;
- selected relationship synchronization remains unchanged;
- provenance remains unchanged;
- deterministic layout output remains unchanged.

Perform a manual browser check of mouse selection and keyboard focus.

## Acceptance Criteria

- [ ] Unwanted blue SVG focus rectangle is gone for mouse relationship selection.
- [ ] Keyboard focus remains visible and usable.
- [ ] Keyboard activation remains functional.
- [ ] Existing selected/preview interaction behavior is unchanged.
- [ ] Existing structure-aware layouts are unchanged.
- [ ] Existing semantic content and provenance are unchanged.
- [ ] `baselines/BASELINE-001-interface.md` exists.
- [ ] A curated 4–5 screenshot baseline exists.
- [ ] Baseline document clearly distinguishes successful interaction grammar from final visual design.
- [ ] Known limitations are documented rather than repaired.
- [ ] Existing tests pass.
- [ ] No unnecessary dependency or frontend architecture is added.
- [ ] Unrelated local README/ROADMAP edits remain untouched.
- [ ] Changes are committed and pushed to canonical `origin/main`.
- [ ] No `DEBRIEF-006` is created.

## Required Handoff

Report:

1. cause of the blue focus artifact;
2. exact fix and how keyboard accessibility was preserved;
3. tests and browser validation;
4. baseline document path;
5. screenshot paths;
6. confirmation that semantic/layout/provenance outputs are unchanged;
7. dependencies added/removed;
8. deviations;
9. commit SHA;
10. confirmation pushed to canonical GitHub.

After this handoff, ChatGPT will independently review the baseline capture, write `DEBRIEF-006`, update canonical project models, and choose the next product experiment.
