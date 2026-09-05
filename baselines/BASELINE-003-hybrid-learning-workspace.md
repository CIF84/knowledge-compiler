# BASELINE-003 — Hybrid Learning Workspace

## Status

**Preferred integrated product UI baseline.**

Owner approved after direct human review of SPEC-019.

This baseline does not replace the historical value of:

- `BASELINE-001` — focused learning / explanatory representation reference;
- `BASELINE-002` — continuous navigation reference.

BASELINE-003 freezes their successful integration.

## Owner Verdict

> “this. this is it. absolutely stunning.”

> “everything works beautifully.”

> “i love how spaces mirrors actions.”

> “i wouldn't change a thing now.”

> “it's as close to perfection as i could imagine.”

> “this is the thing.”

This is the strongest available human preference signal for the integrated workspace.

## Product Interaction Model

The baseline contains two synchronized cognitive surfaces.

```text
┌──────────────────────────┬────────────────────────────────┐
│ WHERE AM I?              │ WHAT DOES THIS MEAN?           │
│                          │                                │
│ continuous knowledge map │ focused learning surface       │
│                          │                                │
│ navigate                 │ structure-appropriate model    │
│ pan / zoom               │ relationships                  │
│ orient                   │ explanation                    │
│ discover                 │ evidence                       │
│                          │                                │
└──────────────────────────┴────────────────────────────────┘
                 ↕ shared semantic focus
```

The map answers **where**.

The learning surface answers **meaning**.

## Baseline Principle

> **Spaces mirror actions.**

The interface should communicate its cognitive roles through spatial organization rather than explanatory UI chrome.

## Navigation Surface Invariants

Preserve:

- continuous stable knowledge world;
- drag / pan;
- geometric zoom;
- Overview/Home;
- spatial continuity;
- focus/recenter when appropriate;
- broad context across knowledge regions;
- synchronized concept/relationship focus;
- visual suppression of irrelevant topology when focused;
- navigation camera state independent from semantic focus.

Pure pan/zoom must not silently change what the learner is studying.

## Learning Surface Invariants

Preserve:

- strong local visual hierarchy;
- representation chosen according to detected information structure;
- representation preset visibility where useful;
- explicit canonical relationship direction and labels;
- concept selection;
- relationship selection;
- hover preview distinct from persistent selection;
- focus suppression;
- detail / explanation;
- source evidence;
- provenance;
- quiet surrounding UI.

## Synchronization Invariants

### Navigation → learning

Selecting a concept in the map updates the focused learning context/representation when a corresponding representation exists.

### Learning → navigation

Selecting a concept in the learning surface highlights the same stable semantic entity in navigation and recenters only when necessary.

### Relationships

Shared canonical relationships synchronize by stable identity, not label matching.

### Camera independence

Moving the navigation camera does not alter learning selection.

## Representation Invariant

The navigation map is not the universal representation of knowledge.

The learning surface must continue to obey:

> **The appropriate representation should depend upon the information structure.**

Supported/future truthful representation families may include:

```text
hierarchy
causal / system model
process chronology
dependency
feedback
structured proposition
comparison
mathematical / functional
spatial / physical
```

Only representations justified by semantic structure should be shown.

## Personalization Boundary

Personalization must not change truth.

Preserve the architectural direction:

```text
TRUSTED SEMANTICS
       ↓
STRUCTURE DETECTION
       ↓
AVAILABLE TRUTHFUL REPRESENTATIONS
       ↓
PERSONALIZED PRIORITY / PRESET
       ↓
LEARNING SURFACE
```

The owner strongly prefers systems-oriented representations. That may inform future representation ranking, but must not become a universal semantic assumption.

## Information Hierarchy

The learning focus should remain cognitively dominant during focused study.

Navigation remains continuously available for orientation and exploration without becoming a competing wall of information.

When the user actively manipulates the map, navigation may temporarily command attention through interaction rather than permanent visual dominance.

## Anti-Regression Rules

Do not reintroduce:

- document-like Explore / Back as the primary navigation model;
- assertion-card overload;
- Venn/presentation-neighborhood topology as the primary knowledge representation;
- one universal generic graph in the learning pane;
- full-screen navigation that removes explanatory scaffolding;
- text-heavy overview surfaces;
- automatic camera movement on every selection when the target is already visible;
- semantic focus changes caused by pure pan/zoom.

## Freeze Rule

The owner stated that they would not change anything in the reviewed interface.

Therefore **do not polish this baseline speculatively**.

Any future contract that modifies the workspace shell must explicitly state:

1. which BASELINE-003 invariant is being changed;
2. what observed problem motivates the change;
3. what dimension remains frozen;
4. how regression against this baseline will be reviewed.

Changes to semantic compilation, representations, personalization, learning paths, or resolution may use the workspace without changing its shell.

## Component Baselines Remain Canonical References

Use BASELINE-001 when diagnosing focused-learning regressions.

Use BASELINE-002 when diagnosing continuous-navigation regressions.

Use BASELINE-003 when judging the integrated product experience.

This three-baseline structure is intentional.

## Future Product Direction

With foundational workspace interaction now accepted, the highest-value questions move upstream/downstream rather than sideways into another UI metaphor:

- Can realistic sources reliably populate useful semantic structure?
- Can deeper semantic resolution remain truthful and navigable?
- Can representation selection choose the right cognitive form?
- Can representation ranking adapt to the learner?
- Can a generated learning path guide attention through the same topology without removing agency?
- Can the end-to-end input → compile → navigate → understand workflow become a usable product?

## Baseline Verdict

`HYBRID_WORKSPACE_BETTER`

## Historical Interpretation

The sequence that produced this baseline matters:

```text
SPEC-006
strong focused representation
        ↓
SPEC-007/008
contextual depth, awkward page navigation
        ↓
SPEC-016
text-rich assertion surface rejected
        ↓
SPEC-017
presentation topology rejected
        ↓
SPEC-018 / BASELINE-002
continuous movement validated
        ↓
SPEC-019 / BASELINE-003
navigation + learning synchronized
```

The result is not a generic graph product.

It is a synchronized knowledge workspace where the learner can both **move through structure** and **understand the current structure through the appropriate representation**.
