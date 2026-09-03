# SPEC-006 — Structure-Aware Layout and Synchronized Interaction

## Status

Ready for implementation.

## Primary Question

> Can structure-aware deterministic layout plus synchronized semantic selection make the existing representations materially easier to parse and manipulate as coherent mental models, without adding semantic inference or general frontend complexity?

## Purpose

SPEC-005 produced the first direct positive evidence for the core product thesis: the project owner immediately felt cognitively better oriented in the interactive representation and would prefer to learn with the tool available.

That review also exposed two tightly related weaknesses:

1. **interaction coherence** — one semantic relationship appears as a graph edge, relationship control, detail panel, and evidence, but selection is not persistently synchronized across those surfaces;
2. **spatial legibility** — node and edge placement is functional but does not consistently expose hierarchy, branching, convergence, chronology, or loops in visual harmony.

These are not generic UI-polish requests. They concern whether the representation behaves like one coherent mental model.

SPEC-006 therefore keeps all semantic and structural inputs fixed and changes only the viewer behavior/layout necessary to test those two findings.

## Product Hypothesis

The working hypothesis is:

> A semantic representation becomes easier to reason with when spatial organization reflects the structure being represented and when every visible occurrence of a selected semantic object responds as one coordinated interaction state.

Conceptually:

```text
semantic correctness
        +
spatial legibility
        +
interaction coherence
        ↓
coherent mental representation
```

SPEC-006 tests the second and third terms while holding the first constant.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `specs/SPEC-005-minimal-representation.md`
8. `debriefs/DEBRIEF-005-minimal-representation.md`
9. `src/knowledge_compiler/representations.py`
10. `src/knowledge_compiler/representation_builder.py`
11. `src/knowledge_compiler/viewer.py`
12. `src/knowledge_compiler/viewer_assets/`
13. committed SPEC-005 five-domain representation artifacts

Use the accepted SPEC-005 representation artifacts as fixed experimental inputs. Do not regenerate semantic extraction or structure detection merely to improve the examples.

## Experimental Control

This increment depends on a clean before/after comparison.

Hold constant:

- `KnowledgeModel` artifacts;
- `DetectedStructureSet` artifacts;
- `RepresentationModel` semantic content unless a presentation-only field is genuinely necessary;
- relationship vocabulary and definitions;
- provenance;
- salience rules;
- domain corpus;
- upstream warnings/limitations.

Change only:

- interaction state/behavior;
- graph layout/geometry;
- minimal presentation metadata required to support those changes.

If an upstream defect becomes visually obvious, preserve it and report it. Do not repair it in SPEC-006.

## Scope

Implement the smallest changes needed to:

1. introduce shared semantic selection state in the viewer;
2. distinguish hover preview from persistent click selection;
3. synchronize relationship selection across graph edge/arrow, relationship control/chip, detail panel, and evidence;
4. synchronize node selection across graph node and detail surfaces where applicable;
5. make graph and relationship controls reciprocal interaction targets;
6. visibly distinguish selected, previewed, and unselected states;
7. replace generic placement with structure-aware deterministic layout strategies;
8. make hierarchy, causal/dependency, process, and feedback geometry visibly appropriate to their semantics;
9. reduce unnecessary line crossings, long diagonals, ambiguous direction, and uneven spacing on the current benchmark graphs;
10. preserve canonical semantic direction at all times;
11. preserve all SPEC-005 provenance and warning behavior;
12. reuse the same five-domain fixed artifacts for before/after owner review;
13. keep the viewer lightweight and local;
14. keep deterministic behavior testable without requiring an LLM or network call.

## Explicit Non-Goals

Do not implement in SPEC-006:

- new semantic extraction;
- prompt changes;
- new relationship predicates;
- relationship reclassification;
- source repair;
- structure repair;
- event/state/process IR redesign;
- inferred missing edges;
- graph editing;
- user-authored relationships;
- canonical relationship reversal;
- hypothetical simulation/reversal mode;
- counterfactual propagation;
- quantitative simulation;
- nested knowledge atlas;
- arbitrary zoom/drill-down architecture;
- new ingestion sources;
- accounts;
- persistence/database;
- cloud deployment;
- collaboration;
- mobile application;
- production responsive redesign;
- branding redesign;
- animation framework;
- general-purpose graph editor;
- broad accessibility redesign beyond avoiding regressions in current interaction semantics;
- formal user study infrastructure.

Do not turn this into a frontend rewrite.

## Preserve Architecture Boundaries

The accepted architecture remains:

```text
KnowledgeModel + DetectedStructureSet
              ↓
     RepresentationBuilder
              ↓
     RepresentationModel
              ↓
             viewer
```

SPEC-006 should operate primarily inside the viewer/presentation boundary.

If deterministic layout coordinates or layout hints belong in `RepresentationModel`, adding a small presentation-only field is acceptable, but justify it. Do not move layout into `KnowledgeModel` or `DetectedStructureSet`.

Semantic truth remains upstream and immutable from the viewer.

## Interaction State Model

Introduce one coherent viewer-level selection model rather than independent per-widget behavior.

Conceptually:

```text
ViewerState
    selectedNodeId: optional
    selectedEdgeKey / relationship identity: optional
    previewNodeId: optional
    previewEdgeKey: optional
```

The exact implementation is flexible. The important invariant is that one semantic object has one effective interaction state even when represented in multiple DOM/SVG elements.

### Selection precedence

Use a simple rule:

```text
CLICK = persistent selection
HOVER = temporary preview
```

Hover must not destroy the persistent selection.

A useful behavior is:

```text
persistent selection exists
        ↓
hover another object
        ↓
temporary preview appears
        ↓
mouse leaves
        ↓
persistent selection is restored visually
```

Do not create complicated multi-select behavior.

### Relationship selection

Selecting a relationship from any supported surface must synchronize all corresponding surfaces:

```text
click graph edge/arrow
        ↓
edge highlighted
relationship control highlighted
detail/evidence panel populated

click relationship control
        ↓
control highlighted
corresponding graph edge highlighted
detail/evidence panel populated
```

Where one rendered logical edge represents multiple supporting relationship IDs, selection should still behave as one rendered semantic edge while preserving all provenance in detail.

### Node selection

Selecting a node should:

- persistently highlight the node;
- populate node detail;
- clear conflicting edge selection if the current viewer model requires single selection;
- behave consistently when the same entity is rendered more than once, if that occurs.

Do not invent new semantic relationships merely to show node neighborhoods.

### Click-away / reset

Provide a simple way to clear selection, such as clicking empty graph space or an explicit minimal reset affordance.

Domain or representation changes must clear stale selection state.

## Visual Interaction States

Selected and previewed states must be visually distinguishable.

The exact visual treatment is an implementation choice, but the learner should be able to tell at a glance:

```text
what I selected
what I am merely hovering
what is unrelated/unselected
```

Prefer restrained changes such as border/stroke weight, background emphasis, or equivalent existing-theme cues.

Do not add decorative animation solely for feedback.

### Relationship line emphasis

When an edge is selected, the actual connector/arrow should become visibly emphasized, not only its text label or detail panel.

The edge label and relationship control should participate in the same selected state.

## Canonical Direction Is Immutable

The owner previously suggested that relationship direction changes could interactively change the line direction. Preserve the underlying product idea for a future hypothetical/exploration mode, but **do not implement semantic reversal in SPEC-006**.

Current invariant:

```text
canonical KnowledgeModel relationship direction
                =
viewer arrow direction
```

The viewer must not silently transform:

```text
A CAUSES B
```

into:

```text
B CAUSES A
```

through interaction.

If any UI control visually implies reversibility, remove or avoid that implication in this increment.

## Structure-Aware Layout

The current layout should be replaced or refined using deterministic strategies that reflect representation type.

The goal is not mathematically optimal graph drawing. The goal is cognitive legibility on the current small benchmark structures.

### Hierarchy

Desired grammar:

```text
whole / general
      ↑ or ↓ according to canonical edge direction
parts / specializations
```

Use a layered tree/DAG-like arrangement that makes levels obvious and minimizes crossing.

Remember that canonical predicate direction must remain truthful. For example, `component PART_OF service` remains component → service even if the spatial hierarchy places the whole above the part.

Layout orientation and semantic arrow direction are related but not identical concepts.

### Causal model

Use a layered directional DAG-like arrangement.

Goals:

- causes/drivers generally occupy earlier layers;
- effects generally occupy later layers;
- branching from one cause is visually obvious;
- convergence on one effect is visually obvious;
- minimize crossings and long diagonal edges;
- avoid making one path appear more causally important merely because it is visually straighter unless salience supports that interpretation.

For the current economics benchmark, the resulting geometry should make the relationships around shortage, supply reduction, upward price pressure, market price, quantity demanded, and quantity supplied easier to parse than the SPEC-005 layout.

### Dependency model

Use a layered directional arrangement similar to causal layout but preserve dependency semantics rather than visually implying causality.

Where chains are simple, prefer a clean axis. Where they branch, use layers.

### Process chain

Use an explicit chronological axis, preferably left-to-right unless there is a compelling reason otherwise.

`PRECEDES` direction must be visually unambiguous.

Sparse one-edge chronology should remain visibly sparse rather than being stretched into a misleadingly rich timeline.

### Feedback candidate

Use geometry that makes the cycle perceptible as a loop rather than merely a path whose final edge happens to return to an earlier node.

Do not label polarity or claim reinforcing/balancing behavior.

If the current electromagnetism candidate is weakened by collapsed state semantics, retain that warning.

## Layout Algorithm / Dependency Decision

Do not assume either custom layout or a library is automatically better.

First inspect the current graph sizes and viewer implementation.

A small focused layout dependency is acceptable only if it materially improves:

- deterministic layered placement;
- edge routing;
- crossing reduction;
- maintainability;

and does not force a frontend framework/build pipeline.

If a compact custom deterministic layout is sufficient for the current structures, prefer it.

The handoff must explain the choice and complexity cost.

Do not hand-build a general Sugiyama/graphviz-class engine merely to avoid a reasonable small dependency.

## Determinism

Layout must be deterministic for the same `RepresentationModel` and viewport assumptions used by the experiment.

At minimum:

- node layer assignment deterministic;
- ordering within layers deterministic;
- coordinates deterministic where generated explicitly;
- edge routing deterministic;
- no random force simulation;
- repeated artifact/viewer-data generation stable where practical.

Avoid force-directed physics layouts for this increment.

## Spatial Quality Heuristics

Introduce only simple explainable layout-quality measurements if useful for automated comparison.

Potential measurements:

- number of edge crossings;
- total or average connector length in normalized layout units;
- number of backward-looking edges relative to chosen layout orientation;
- layer count;
- node overlap count;
- label overlap count if cheaply measurable without a browser.

These are diagnostic metrics, not a fake universal visual-quality score.

Do not optimize a metric at the expense of semantic legibility.

## Fixed Benchmark Cases

Use the committed SPEC-005 artifacts.

### Economics — primary spatial benchmark

This is the strongest branching causal model.

The new layout should make these patterns immediately legible:

```text
shortage → upward pressure on price → market price
reduction in supply → market price
market price → quantity demanded
market price → quantity supplied
```

The missing market feedback-closing edge remains an upstream limitation and must not be added.

### Software architecture

Use hierarchy and dependency representations to test:

- level clarity;
- direction clarity;
- clean chain/branch organization;
- synchronized selection.

### Electromagnetism

Use the feedback candidate to test explicit loop geometry and relationship synchronization.

Retain the known state-collapse warning.

### History

Use dependency and sparse process representations to verify that layout does not inflate weak structures.

### Biology

Keep the explicit empty state unchanged. SPEC-006 should not invent layout for absent structure.

## Before/After Human Review

The owner should compare SPEC-005 and SPEC-006 using the same fixed semantic artifacts.

The review should focus narrowly on:

### Interaction coherence

- Does clicking an edge make it obvious everywhere which relationship is selected?
- Does clicking a relationship control clearly select the graph edge?
- Does hover behave as preview rather than conflicting with selection?
- Does node selection feel consistent?
- Does the detail/evidence panel feel attached to the selected object rather than like a separate UI widget?

### Spatial legibility

- Is the structure understandable faster?
- Are direction and branching clearer?
- Are there fewer visually awkward diagonals/crossings?
- Does each representation type look spatially appropriate to what it means?
- Does the feedback candidate read as a loop?
- Do sparse structures still look honestly sparse?

### Overall

> Does the representation now feel more like one coherent model that I can manipulate mentally, rather than a diagram plus separate controls?

Use qualitative verdicts:

```text
BETTER
SAME
WORSE
```

Do not claim measured learning improvement from one evaluator.

## Review Ergonomics

Provide an exact local command to launch the SPEC-006 viewer.

Prefer keeping the SPEC-005 committed artifacts available so the owner can compare versions without rebuilding upstream data.

If practical, provide a simple way to launch/view the old and new viewer states separately. Do not build an in-product A/B testing framework.

## Testing Strategy

All normal tests must remain offline and deterministic.

Add tests covering at least:

- viewer selection-state transitions where testable outside a browser;
- relationship-control ↔ rendered-edge identity mapping;
- persistent click selection vs hover preview behavior;
- selection clearing on domain/representation change;
- node selection behavior;
- canonical direction preservation;
- deterministic layout for every supported representation type;
- deterministic node ordering/layer assignment;
- no node overlap in benchmark coordinate output where applicable;
- causal branching/convergence fixture;
- hierarchy fixture;
- dependency fixture;
- process fixture;
- feedback-cycle fixture;
- sparse structure behavior unchanged;
- empty state behavior unchanged;
- provenance unchanged;
- prior tests continue to pass.

If browser-console or lightweight DOM tests already exist, extend them where useful. Do not introduce a heavy end-to-end browser framework solely for SPEC-006 unless there is no simpler reliable seam.

## Evaluation Artifacts

Create a committed evaluation directory, for example:

```text
examples/evaluations/spec-006-layout-interaction-20260903/
```

Include only artifacts useful for independent review, such as:

- deterministic layout data or representation outputs if changed;
- machine report of per-domain layout strategy and diagnostics;
- interaction-state mapping metadata if useful;
- human-review template for the before/after comparison.

Do not commit browser caches or large screenshot suites.

A small number of screenshots may be included only if they materially document deterministic layout behavior and are easy to maintain; they are not mandatory.

## Machine Evaluation

The machine report should summarize at least:

```text
domain
representation type
layout strategy
node count
edge count
crossing count if available
warnings
selection identity coverage
provenance integrity
canonical direction integrity
```

The evaluation should confirm that every selectable relationship control maps to the intended rendered edge and vice versa.

## Acceptance Criteria

SPEC-006 is technically complete when all are true:

- [ ] Shared viewer-level semantic selection state exists.
- [ ] Click produces persistent selection.
- [ ] Hover produces temporary preview without destroying persistent selection.
- [ ] Selecting a graph relationship highlights the corresponding relationship control.
- [ ] Selecting a relationship control highlights the corresponding graph edge/arrow.
- [ ] The detail/evidence panel follows the effective selected/previewed semantic object.
- [ ] Selected graph connector/arrow is visibly emphasized.
- [ ] Node selection is persistent and coherent.
- [ ] Domain/representation changes do not retain stale selection.
- [ ] Canonical semantic direction is never changed by interaction.
- [ ] Layout strategy differs appropriately by representation type.
- [ ] Causal/dependency layouts use deterministic directional layering.
- [ ] Hierarchy layout exposes levels clearly.
- [ ] Process layout exposes chronology clearly.
- [ ] Feedback candidate is visually loop-like.
- [ ] Layout is deterministic and non-random.
- [ ] Current benchmark geometry is materially cleaner by direct inspection, especially economics.
- [ ] Sparse and empty behavior remains truthful.
- [ ] Provenance remains intact.
- [ ] No semantic extraction, predicate, IR, or detector changes are introduced merely for visual quality.
- [ ] No heavy frontend architecture is introduced without explicit evidence/justification.
- [ ] Automated tests pass offline.
- [ ] Fixed five-domain artifacts can be reviewed locally.
- [ ] A focused before/after human-review artifact/template is provided.
- [ ] Implementation is committed and pushed to canonical GitHub before handoff.

The primary product acceptance criterion remains human:

> Compared with SPEC-005 on the same fixed semantic content, does SPEC-006 make the representation materially easier to parse and interact with as one coherent mental model?

A valid outcome may be **SAME** or **WORSE**. If structure-aware layout or synchronized interaction adds complexity without cognitive benefit, preserve that finding.

## Required Handoff to Review

When implementation is complete, Codex must report:

1. architecture changes;
2. interaction-state model;
3. exact hover vs click semantics;
4. relationship synchronization behavior;
5. node selection behavior;
6. layout strategy for each representation type;
7. custom-layout vs dependency decision and rationale;
8. deterministic-layout mechanism;
9. files added/changed;
10. exact automated test result;
11. exact machine-evaluation command/result;
12. exact command to launch SPEC-006 viewer;
13. how to compare against SPEC-005 locally;
14. per-domain layout diagnostics;
15. interaction identity/integrity result;
16. canonical-direction integrity result;
17. provenance integrity result;
18. known visual weaknesses;
19. whether any new upstream semantic limitation became visible;
20. dependencies added/removed;
21. deviations from this SPEC;
22. commit SHA;
23. confirmation that commit is pushed to canonical GitHub.

Do not write `DEBRIEF-006` during implementation. It follows independent repository review plus owner interaction with the new viewer.

## Operational Learning Capture

SPEC-006 should test whether the current repo-centered workflow remains effective when the primary changes are behavioral and spatial rather than semantic/data-oriented.

The debrief should observe:

- whether interaction behavior can be meaningfully tested without a heavy browser framework;
- whether deterministic layout diagnostics correlate with owner visual judgment;
- whether fixed upstream artifacts make UI iteration faster and causally cleaner;
- whether screenshots become more useful as evidence at this stage;
- whether viewer code remains simple or starts demanding a frontend architecture change;
- whether synchronized semantic state becomes a reusable product concept for future progressive disclosure;
- whether structure-specific layout should remain viewer logic or become a formal presentation-model concern.

## Likely Decision After SPEC-006

Do not implement this section during SPEC-006.

If synchronized interaction and structure-aware layout materially improve the experience, the next experiment should likely test **progressive disclosure / semantic navigation**:

```text
high-level model
    ↓ select node / relationship
focused explanation
    ↓
related substructure / source evidence
```

If the layout improves but semantic defects dominate the experience, return upstream to a focused event/state/endpoint modeling experiment.

If the changes do not materially improve cognition, preserve the simple SPEC-005 viewer and reconsider the representation strategy before adding further product surface.
