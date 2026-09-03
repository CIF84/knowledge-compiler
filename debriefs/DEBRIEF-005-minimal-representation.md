# DEBRIEF-005 — Minimal Representation Experiment

## Status

Accepted — strong positive human outcome with interaction and spatial-layout limitations.

## Implementation

SPEC-005 implementation commit:

```text
614e3a2a693f871f4ddad848c03f4722d573186e
```

The implementation added a deterministic presentation layer:

```text
KnowledgeModel + DetectedStructureSet
              ↓
     RepresentationBuilder
              ↓
     RepresentationModel
              ↓
       static local viewer
```

No LLM, network call, source reinterpretation, relationship-vocabulary change, semantic-IR change, or structure-detector change was introduced.

## Primary Question

> Can a small set of deterministic visual/interactive representations turn `DetectedStructureSet` plus grounded `KnowledgeModel` context into a learning artifact that is materially easier to think with than the underlying text or JSON?

## Outcome

**Yes, for this first owner evaluation.**

The technical acceptance criteria were satisfied and the first human evaluation produced a strong positive reaction rather than merely tolerance of the representation.

The project owner reported:

- an immediate subjective improvement in cognitive orientation;
- the first-draft UI was already perceived as unusually strong for the maturity of the project;
- interactivity materially increased engagement;
- the tool was something they would definitely want available while learning;
- node and relationship inspection were useful enough that the next requested improvements concerned coherence of interaction and spatial organization rather than questioning the representation concept itself.

The central product hypothesis therefore moves from untested to provisionally supported:

> Spatial, semantic, interactive representations can reduce the cognitive work required to build a mental model from explanatory material.

This is a single-owner qualitative evaluation, not evidence of general population effectiveness or measured learning gains.

## What Was Implemented

### Representation model

A typed deterministic `RepresentationModel` separates presentation concerns from semantic and structure-detection concerns.

It includes representations, nodes, edges, evidence excerpts, salience, warnings, empty states, source structure IDs, and deterministic metadata.

### Structure mappings

Current mappings are:

```text
HIERARCHY          → labeled directed DAG
CAUSAL_PATH        → merged branching causal model
DEPENDENCY_CHAIN   → directional dependency model
PROCESS_CHAIN      → explicit chronology
FEEDBACK_CANDIDATE → directed loop explicitly labeled as candidate
```

Overlapping structures of the same type are merged while preserving all contributing structure IDs.

### Salience

The first deterministic salience rule is deliberately simple:

```text
PRIMARY   = >= 3 edges, or multi-edge feedback candidate
SECONDARY = 2 edges
SPARSE    = 1 edge
```

Sparse structures are warned and sorted after richer views.

### Provenance

The viewer preserves the path:

```text
displayed edge
    ↓
canonical predicate meaning / direction
    ↓
KnowledgeModel relationship ID(s)
    ↓
validated source evidence span(s)
```

Duplicate supporting relationships retain their provenance. Inferred relationships do not fabricate source evidence.

### Viewer

The viewer uses static HTML/CSS/JavaScript served locally with Python standard-library HTTP serving. No runtime dependency was added.

It supports:

- domain switching;
- representation selection;
- directed diagrams;
- node inspection;
- edge/relationship inspection;
- canonical semantic definitions;
- warnings;
- exact evidence quotes.

## Deterministic Evaluation

Reported automated test result:

```text
75 passed in 0.14s
```

The implementation also reported successful compile, secret, diff, installed-wheel, browser-console, and byte-for-byte regeneration checks.

The committed five-domain report records valid references and complete provenance across all domains.

Representation outputs:

| Domain | Result |
| --- | --- |
| Electromagnetism | feedback candidate + sparse hierarchy |
| Software architecture | hierarchy + dependency model |
| Economics | merged branching causal model |
| Biology | explicit empty state |
| History | dependency model + sparse process chronology |

Biology correctly remains empty rather than receiving a manufactured diagram.

## Human Review

### Core verdict

**BETTER.**

The owner would prefer to learn with the representation available rather than without it.

The strongest qualitative signal was immediate cognitive orientation: the representation felt closer to the form in which the owner naturally reasons than linear explanatory text.

This matters more than visual approval alone. The experiment was designed to test whether the representation reduces model-building friction; the first reaction indicates that it does.

### Interactivity

Interactivity was identified as a particularly valuable feature because it promotes active engagement with the model rather than passive viewing.

The current interaction already demonstrates the intended learning grammar:

```text
node → inspect concept
edge → inspect semantic relationship + provenance
```

However, the same semantic object is currently represented in multiple UI locations without fully synchronized persistent selection state.

### Interaction weakness discovered

When an edge is selected, the right-side relationship detail behaves correctly, but the corresponding relationship control/chip below the visualization is not persistently highlighted. It highlights only on hover.

The desired interaction model is:

```text
HOVER = preview
CLICK = persistent selection
```

Selecting a relationship from any surface should synchronize all representations of that semantic object:

```text
relationship selected
      ↓
edge / arrow highlighted
relationship chip highlighted
detail panel populated
```

Likewise, selecting the relationship chip should select/highlight the corresponding graph edge.

This is not merely cosmetic. It reinforces that the graph edge, predicate, explanation, evidence, and control are manifestations of one semantic relationship.

### Spatial-layout weakness discovered

The owner also identified that node placement and connective lines are not yet in visual harmony.

This is especially visible in branching causal models: the semantics are useful, but uneven spacing and long diagonal connectors impose avoidable spatial interpretation work.

The important learning is:

> Layout is part of representation semantics, not merely visual polish.

Different structure types likely require different deterministic spatial grammars, for example:

```text
HIERARCHY        → top-down tree / DAG
CAUSAL_PATH      → directional layered DAG
DEPENDENCY_CHAIN → directional layered chain / DAG
PROCESS_CHAIN    → strict chronological axis
FEEDBACK         → visually explicit loop
```

The exact layouts remain unproven. The evidence supports testing structure-aware layout rather than adopting a particular graph library or algorithm prematurely.

## Upstream Limitations Made More Visible

Rendering strengthened rather than weakened the SPEC-004 finding that visualization exposes upstream semantic weaknesses.

Known examples remain:

- electromagnetism lacks the expected field → force → motion composition;
- changing-field states are collapsed in the feedback candidate;
- biology lacks composable chronology and therefore remains empty;
- history chronology terminates at an actor rather than a response event;
- economics lacks the edge required to close a market feedback loop.

These defects should remain attributed upstream. SPEC-005 correctly did not repair them in presentation code.

## Key Findings

### 1. The representation thesis has its first direct positive evidence

Previous increments proved extraction, semantic representation, relationship quality, and deterministic composition. SPEC-005 is the first increment to show that the resulting artifact can actually feel easier to think with.

### 2. Interaction is not an accessory to the diagram

The ability to inspect nodes and relationships changes the artifact from a static visualization into an explorable model.

This supports continuing toward interactive learning representations rather than exporting static diagrams as the primary product.

### 3. Semantic identity should be synchronized across UI surfaces

A relationship exists once semantically but may appear as an arrow, label/chip, detail panel, and evidence block. Selection state should unify those surfaces.

This suggests a viewer interaction-state concept, not duplicate per-widget behavior.

### 4. Spatial arrangement carries meaning

A semantically correct graph can still impose unnecessary cognitive load if its geometry obscures hierarchy, direction, branching, sequence, or loops.

Representation quality therefore has at least three distinct dimensions:

```text
semantic correctness
spatial legibility
interaction coherence
```

### 5. Human product review now provides information code tests cannot

All deterministic integrity checks could pass while the viewer remained cognitively poor. Direct owner interaction revealed the next important product constraints quickly.

The repository-centered process should therefore continue pairing deterministic artifact verification with focused human review for UI-bearing increments.

### 6. The current UI is sufficient as an experimental surface

The first draft was already positively received. There is no evidence supporting a broad visual redesign, frontend framework migration, branding exercise, or design-system project.

The next work should improve cognitive behavior, not polish for its own sake.

## Decisions

### Accept SPEC-005

The technical implementation and first human usefulness test are sufficient to accept the increment.

### Keep RepresentationModel as a thin downstream layer

No evidence suggests moving presentation concerns into `KnowledgeModel` or `DetectedStructureSet`.

### Preserve provenance as a first-class interaction

Evidence inspection is part of the learning/trust experience, not developer-only metadata.

### Treat selection as shared semantic state

Future viewer interaction should make the selected node/relationship coherent across graph, controls, detail, and evidence surfaces.

### Treat layout as representation semantics

Future layout should be structure-aware and deterministic where practical. The goal is cognitive legibility, not generic graph aesthetics.

### Do not return upstream yet

The observed upstream event/state limitations remain real, but they do not block useful representations generally. The next experiment should improve the representation experience before redesigning semantic IR.

### Do not broaden into full progressive disclosure yet

Before adding deeper zoom/navigation/submodels, first test whether synchronized interaction and structure-aware spatial layout materially improve the current representation itself.

## Unresolved Questions

1. What is the smallest viewer-level selection-state model that synchronizes graph, relationship controls, details, and evidence?
2. Should node selection similarly synchronize all occurrences/context surfaces?
3. Which deterministic layout grammar best fits each current structure type?
4. Can structure-aware layout be implemented simply, or does a small graph-layout dependency provide better complexity/value?
5. How should branching and converging causal models be layered to minimize crossings and ambiguous direction?
6. How should feedback candidates be laid out when loop polarity remains unknown?
7. Should relationship direction ever be interactively reversible for exploration, and if so how can that be clearly separated from changing the underlying semantic truth?
8. How should layout respond as representations become larger than the current benchmark examples?
9. At what point do upstream event/state weaknesses become severe enough to justify a focused semantic-modeling increment?
10. How should learning usefulness eventually be tested beyond the project owner without prematurely building formal research infrastructure?

## Important Clarification About Direction Interaction

The owner suggested that changing relationship direction could interactively change the connection-line direction.

This idea is worth preserving but requires semantic caution.

A canonical relationship direction is currently part of the trusted semantic model. A UI control must not silently mutate `A CAUSES B` into `B CAUSES A` merely as a visual operation.

A future experiment may distinguish:

```text
canonical semantic direction
        vs
user exploration / hypothetical reversal
```

If explored, the hypothetical state must be visibly non-canonical and must not alter source-grounded model truth.

## Recommended Next Experiment

### SPEC-006 — Structure-Aware Layout and Synchronized Interaction

Primary question:

> Can structure-aware deterministic layout plus synchronized semantic selection make the existing representations materially easier to parse and manipulate as coherent mental models, without adding semantic inference or general frontend complexity?

Likely scope:

- shared selected-node / selected-relationship viewer state;
- click-to-select and hover-to-preview semantics;
- synchronized highlighting across graph edge, relationship control, and detail/evidence panel;
- reciprocal selection from graph and relationship controls;
- structure-specific deterministic layout strategies;
- clearer branching/convergence geometry;
- explicit feedback-loop geometry;
- preserve canonical semantic direction;
- repeat owner evaluation on the same fixed artifacts.

Likely non-goals:

- new semantic extraction;
- new predicates;
- event/state redesign;
- arbitrary user graph editing;
- semantic relationship reversal;
- simulation;
- nested knowledge atlas;
- production UI redesign;
- mobile/responsive product work;
- accounts/persistence/deployment.

## Operating-Model Findings

The fifth repo-centered cycle worked, but this increment introduced a useful change in review mechanics:

```text
implementation verification
        +
actual human interaction with artifact
        ↓
product evidence
```

For UI-bearing experiments, repository inspection alone is insufficient. The implementation handoff should continue providing an exact local review command and deterministic artifacts, followed by a short owner interaction before acceptance.

Screenshots were useful for communicating spatial/interaction issues, but there is not yet evidence that screenshots need to become mandatory committed artifacts.

The current process remains lightweight enough: no separate design-management workflow is justified.

## Final Conclusion

SPEC-005 produced the first direct evidence that Knowledge Compiler's central product idea can work in practice.

The pipeline has progressed from:

```text
source
  ↓
semantic model
  ↓
higher-order structure
  ↓
interactive representation
```

and the first human interaction with that representation was strongly positive.

The next constraint is no longer whether a representation can be generated. It is whether **space and interaction can make that representation behave like a coherent mental model**.
