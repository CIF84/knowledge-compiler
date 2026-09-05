# SPEC-019 — Navigation + Learning Workspace

## Status

Ready for implementation.

## Phase

Phase II — integration of validated UX primitives.

## Primary Question

> Can continuous spatial navigation provide persistent orientation around the focused BASELINE-001 learning representation without degrading either learning clarity or navigation quality?

## Why This Experiment Is Earned

The project now has two independently strong UX references.

### BASELINE-001 — learning

Strongest reference for focused understanding:

- parent context;
- local representation appropriate to information structure;
- explicit relationships/trajectories;
- selection and detail;
- evidence;
- explanatory scaffolding.

### BASELINE-002 — navigation

Strongest reference for spatial exploration:

- continuous world;
- drag/pan;
- geometric zoom;
- spatial continuity;
- focus/recenter;
- relationship exploration while moving.

Owner assessment:

> “i'd prefer new one for general exploration, but the old one for learning.”

The old BASELINE-001 parent-context box already hints at the integration model: navigation context and focused explanation should coexist.

## Experimental Hypothesis

Do not force one interface to replace the other.

Test a synchronized workspace with two responsibilities:

```text
NAVIGATION SURFACE
Where am I?
What is around me?
Where can I move next?

LEARNING SURFACE
What does the current thing mean?
What representation best explains it?
What evidence supports it?
```

The navigation surface provides spatial context.

The learning surface provides semantic/cognitive explanation.

## Architectural Boundary

Preserve three distinct responsibilities:

```text
SEMANTIC COMPILER
What is justified?

REPRESENTATION ENGINE
How is this structure best expressed?

NAVIGATION ENGINE
Where am I in the larger knowledge space?
```

SPEC-019 integrates the last two at the UI level without changing semantic truth.

## Baseline Invariants

### BASELINE-001 invariant

Do not redesign the focused learning representation.

Preserve as closely as practical:

- local graph/representation grammar;
- parent context idea;
- explicit canonical relationship direction/labels;
- hover preview;
- persistent click selection;
- detail panel;
- evidence inspection;
- focus suppression;
- representation badges/presets where present;
- restrained visual hierarchy.

### BASELINE-002 invariant

Do not redesign continuous navigation.

Preserve as closely as practical:

- stable world coordinates;
- drag/pan;
- geometric zoom;
- Overview/Home;
- focus/recenter;
- spatial continuity;
- concept/relationship selection while moving;
- local attention suppression;
- viewport-anchored detail behavior where reused.

Known blue-browser/SVG artifact is a defect, not an invariant. Fix it if possible without changing the experiment.

## Experimental Variable

The experiment is **workspace composition + synchronization**.

Not:

- new semantic extraction;
- new graph representation;
- new topology algorithm;
- new navigation architecture;
- new personalization engine.

## Workspace Model

Create one page containing both:

```text
CONTINUOUS NAVIGATION CONTEXT
+
FOCUSED LEARNING REPRESENTATION
```

The exact layout is experimental.

Possible arrangements include:

```text
side-by-side
map above / learning below
learning main + navigation inset
resizable split workspace
```

Do not hard-code a 50/50 split merely because it was discussed conceptually.

Choose the simplest composition that gives both surfaces enough space to perform their jobs.

## Preferred Initial Direction

Start with a desktop split workspace because it makes the integration hypothesis easy to inspect.

Conceptually:

```text
┌────────────────────────┬──────────────────────────────┐
│                        │                              │
│   NAVIGATION CONTEXT   │      LEARNING SURFACE       │
│                        │                              │
│   pan / zoom / move    │   appropriate local model   │
│   surrounding world    │   explanation / evidence    │
│                        │                              │
└────────────────────────┴──────────────────────────────┘
```

But implementation may choose map-above/learning-below if existing viewer architecture makes that substantially cleaner and the cognitive roles remain distinct.

## Navigation Surface Role

The navigation pane should be visually subordinate enough that it does not steal attention during focused learning, but large/clear enough to remain genuinely navigable.

It should answer:

```text
Where is the selected concept in the larger world?
What concepts/relationships surround it?
Where could I go next?
```

It should not duplicate the full explanatory detail of the learning pane.

## Learning Surface Role

The learning pane should remain the primary place for understanding the current focus.

It should answer:

```text
What is this?
How does it work?
What structure am I looking at?
What relationships matter locally?
What evidence supports them?
```

Use the appropriate representation produced by the existing representation engine.

Do not replace it with the generic navigation graph merely for UI consistency.

## Representation Heterogeneity

This is critical.

The navigation layer may use a stable graph/world abstraction for orientation.

The learning layer must preserve the principle:

> **The appropriate representation should depend upon the information structure.**

If the current subject is best represented as:

- causal model;
- hierarchy;
- process chronology;
- dependency structure;
- feedback structure;

then the learning pane should use that representation rather than a universal generic graph.

SPEC-019 must not collapse structure detection/representation selection into navigation.

## Personalization Boundary

Do not implement a personalization engine in SPEC-019.

Preserve the future boundary:

```text
trusted semantics
→ structure detection
→ available truthful representations
→ personalized representation priority
→ learning surface
```

For this experiment use existing PRIMARY/SECONDARY/SPARSE representation decisions/presets where available.

Do not hard-code the owner's systems-thinking preference as universal behavior.

## Synchronization — Navigation to Learning

Selecting a concept in the navigation surface should update the learning surface to the corresponding local representation/context where available.

Desired behavior:

```text
click concept in map
      ↓
map preserves/recenters spatial context
      ↓
workspace focus becomes concept
      ↓
learning pane updates
      ↓
appropriate local representation shown
```

Avoid full-page navigation/reload.

## Synchronization — Learning to Navigation

Selecting/focusing a concept in the learning surface should update the navigation context.

Desired behavior:

```text
select concept in learning representation
      ↓
navigation map highlights same concept
      ↓
map recenters only if needed
      ↓
spatial surroundings remain visible
```

Do not gratuitously recenter if the selected concept is already comfortably visible.

## Relationship Synchronization

Where the same canonical relationship exists in both contexts:

- selecting it in the learning pane may highlight it in navigation;
- selecting it in navigation may select/show it in learning if the learning representation contains it;
- evidence/detail should remain sourced from canonical semantic material.

Do not invent cross-pane relationship matches based on labels alone. Use stable IDs.

## Focus State

Use one shared presentation-level focus state for synchronization, conceptually:

```text
focused entity ID
focused relationship ID
navigation camera state
learning representation state
```

Navigation camera state remains independent from semantic focus so the user can pan without changing what they are learning.

This distinction is important:

> Looking somewhere is not necessarily selecting something.

## Parent Context Evolution

BASELINE-001's static `PARENT CONTEXT` box should not simply be deleted.

Treat the navigation pane as its richer descendant.

Possible approaches:

- replace the static parent mini-map with the synchronized continuous navigation pane;
- retain a compact parent-context label/path above the learning representation while the full navigation map sits elsewhere;
- reuse parent-context visual cues inside navigation.

Preserve the cognitive function:

```text
where am I?
what larger structure contains this?
```

Do not preserve redundant UI merely for historical fidelity.

## Information Hierarchy

Navigation must not dominate learning by default.

The workspace should have an obvious attentional hierarchy:

```text
current learning focus
        strongest

local learning representation
        strong

navigation context
        available / supportive

secondary controls / metadata
        quiet
```

When the user actively interacts with navigation, the map may temporarily become visually stronger.

## Optional Resizing

If straightforward, allow the user to resize the split between navigation and learning surfaces.

This is attractive because exploration and learning require different proportions at different moments.

However, do not add significant implementation complexity solely for resizable panes.

A fixed initial split is acceptable for the experiment.

## Exploration ↔ Learning Without Mode Switching

Do not add an explicit `Explore mode / Learn mode` toggle in SPEC-019 unless technically unavoidable.

The hypothesis is that both can coexist and attention can shift naturally.

The user should be able to:

```text
learn
→ glance at map
→ move somewhere
→ learn new focus
→ inspect evidence
→ move again
```

without changing application mode.

## Explanation and Evidence

Keep explanation/evidence primarily in the learning surface.

Navigation may show lightweight concept labels and relationship labels but should not become text-heavy.

Do not reproduce SPEC-016's assertion-card overload.

## Camera Controls

Navigation pane retains:

- drag/pan;
- geometric zoom;
- Overview/Home;
- focus/recenter.

These controls affect only navigation camera state.

They must not geometrically scale the learning representation.

## Semantic Resolution

Do not integrate generated semantic zoom yet.

SPEC-019 uses existing/frozen semantic resolution artifacts/fixtures.

If existing contextual parent/child fixtures are useful for demonstrating synchronization, they may be used, but do not call providers or generate new child models.

## Benchmark / Fixture Strategy

Use existing deterministic artifacts sufficient to demonstrate both:

1. a navigable larger world;
2. at least one high-quality BASELINE-001-style local learning representation.

It is acceptable to compose existing experimental fixtures for this UI integration test, provided the interface clearly labels fixture provenance and does not pretend the combined world is extracted source truth.

Prefer existing Software Architecture/Economics fixtures rather than creating a new domain.

Do not use sparse realistic quantum semantics if it prevents honest testing of the workspace interaction.

## Blue Artifact Regression

The default blue browser/SVG artifact remains unacceptable.

Restore the known SPEC-006A intent:

```text
mouse interaction
→ no default blue browser outline

keyboard :focus-visible
→ intentional accessible focus treatment
```

Verify in both navigation and learning surfaces.

## No Live Calls

SPEC-019 is offline only.

Do not call OpenAI or any external semantic provider.

## Machine Evaluation

Report at least:

```text
navigation fixture concepts/relationships
learning representations available
shared concept IDs across panes
shared relationship IDs across panes
navigation→learning synchronization cases
learning→navigation synchronization cases
relationship synchronization cases
camera-state preservation across learning changes
learning-state preservation during pure pan/zoom
unnecessary recenter count in deterministic scenarios
parent-context/path preservation
focus suppression integrity in both panes
blue-artifact regression checks
baseline artifact hashes
```

## Human Review Protocol

Human review is decisive.

After machine integrity checks, provide only:

```text
<viewer command>

Use this to understand the subject, but move around whenever the map makes you curious.
```

Do not explain the split architecture first.

Capture spontaneous reaction.

Then evaluate:

### Learning

- Is focused understanding at least as good as BASELINE-001?
- Does the learning pane still feel calm and explanatory?
- Does the representation match the structure rather than becoming generic?

### Navigation

- Is navigation still genuinely useful rather than a decorative mini-map?
- Can I pan/zoom naturally?
- Do I retain spatial orientation?

### Integration

- Does selecting in either surface make the other more useful?
- Do the panes feel like two views of one knowledge space?
- Does either pane unnecessarily compete with the other?
- Does the map help answer “where am I?” while the learning pane answers “what does this mean?”

### Preference

Two strict comparisons:

> Would I rather learn with this than BASELINE-001 alone?

and

> Would I rather explore with this than BASELINE-002 alone?

The experiment is strongest if both answers are yes.

A useful hybrid that improves one task while slightly weakening another may still be `MIXED`, not failure.

## Success Criteria

SPEC-019 succeeds strongly if:

1. BASELINE-001 learning clarity is preserved;
2. BASELINE-002 navigation quality is preserved;
3. synchronization feels natural in both directions;
4. navigation provides useful parent/global context without dominating attention;
5. learning representations remain heterogeneous/structure-appropriate;
6. map camera state and learning focus are correctly separated;
7. no semantic truth is changed;
8. owner prefers the integrated workspace for actual learning/exploration.

## Allowed Verdicts

Final verdict must be exactly one of:

```text
HYBRID_WORKSPACE_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

## Baseline Decision

Do not replace BASELINE-001 or BASELINE-002 automatically.

If `HYBRID_WORKSPACE_BETTER`, create a separate owner-approved baseline capture later.

The two component baselines remain historically valuable even if the hybrid wins.

## Explicit Non-Goals

Do not implement:

- new semantic extraction;
- semantic-gate integration;
- new predicates/propositions;
- new representation-selection algorithm;
- personalization engine;
- semantic zoom generation;
- LLM clustering;
- assertion cards as overview;
- 3D;
- course/Journey mode;
- simulation;
- production ingestion shell;
- mobile redesign.

## Testing Strategy

All tests offline.

Add focused tests for:

```text
shared focus state
navigation→learning sync
learning→navigation sync
relationship ID sync
camera independence from semantic focus
pure pan/zoom does not alter learning selection
unnecessary recenter avoidance
Overview behavior
parent-context/path preservation
focus suppression in both panes
mouse vs keyboard focus styling
baseline immutability
fixture provenance
```

Keep full suite passing.

## Evaluation Artifacts

Create:

```text
examples/evaluations/spec-019-navigation-learning-workspace-<date>/
```

Likely artifacts:

```text
workspace-manifest.json
synchronization-diagnostics.json
baseline-comparison.json
report.json
human-review-template.json
index.html
viewer assets
README.md
```

## Acceptance Criteria — Technical

- [ ] BASELINE-001 preserved unchanged.
- [ ] BASELINE-002 preserved unchanged.
- [ ] Navigation and learning surfaces coexist on one page.
- [ ] Navigation retains pan/zoom.
- [ ] Learning retains structure-appropriate representation.
- [ ] Navigation concept selection updates learning focus.
- [ ] Learning concept selection updates navigation focus.
- [ ] Pure navigation pan/zoom does not change learning focus.
- [ ] Stable IDs used for synchronization.
- [ ] Relationship synchronization works where shared.
- [ ] Unnecessary recenter avoided.
- [ ] Parent/global context remains perceptible.
- [ ] Detail/evidence remains available.
- [ ] Blue mouse artifact absent or explicitly documented as unresolved if restoration cannot be completed without baseline regression.
- [ ] Keyboard focus-visible behavior preserved.
- [ ] No semantic IR/vocabulary changes.
- [ ] No new representation algorithm.
- [ ] No personalization engine.
- [ ] No semantic zoom.
- [ ] No live model calls.
- [ ] Full offline suite passes.
- [ ] Human review required for final verdict.

## Final Constraint

Do not compromise two strong interfaces merely to make them coexist.

The experiment asks:

> **Can the map answer “where am I?” while the learning representation answers “what does this mean?” — simultaneously, as two synchronized views of the same knowledge space?**
