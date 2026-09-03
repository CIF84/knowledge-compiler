# SPEC-007 — Progressive Disclosure and Semantic Navigation

## Status

Ready for implementation.

## Primary Question

> Can a learner move from a high-level model into a deeper local model while preserving enough parent context to remain oriented in the larger system?

## Purpose

SPEC-006 established the first strongly successful cognitive interaction baseline. Structure-aware spatial grammar plus synchronized semantic selection materially improved the owner's ability to parse and interact with the same fixed semantic content. The post-fix interface is preserved as `BASELINE-001`.

The next product problem is no longer whether a useful model can be rendered. It is whether the learner can **increase semantic resolution without losing orientation**.

Knowledge Compiler's long-term product metaphor is closer to a map than a document:

```text
DOMAIN
  ↓
SYSTEM
  ↓
SUBSYSTEM
  ↓
MECHANISM
  ↓
RELATIONSHIP
  ↓
EVIDENCE
```

A conventional drill-down replaces one screen with another. That may expose detail but can destroy the larger mental model the learner was using for orientation.

SPEC-007 tests a different interaction:

> **semantic zoom** — open a deeper local model while preserving perceptual and navigational context from the parent model.

This is deliberately a small interaction/product experiment. It must not become recursive knowledge architecture, automatic decomposition, a knowledge atlas, or a frontend rewrite.

## Product Hypothesis

The working hypothesis is:

> Progressive disclosure is cognitively useful when deeper detail is presented as increased resolution of the current model rather than as navigation away from it.

The learner should be able to answer continuously:

```text
Where am I?
What am I looking at?
How does this relate to the larger system?
How do I go deeper?
How do I return?
```

The experiment should distinguish **detail availability** from **orientation preservation**.

## Baseline

`baselines/BASELINE-001-interface.md` is the control.

Do not redesign the baseline interface merely because SPEC-007 adds a new interaction.

Future behavior should preserve the validated grammar unless the experiment itself demonstrates a better alternative:

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
source provenance immediately inspectable
        +
weak / empty structure remains truthful
```

SPEC-007 adds one new conceptual operation:

```text
EXPLORE  = increase semantic resolution
RETURN   = restore parent resolution
```

Do not overload ordinary node selection to mean navigation.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `debriefs/DEBRIEF-005-minimal-representation.md`
8. `debriefs/DEBRIEF-006-structure-aware-layout-and-synchronized-interaction.md`
9. `baselines/BASELINE-001-interface.md`
10. `specs/SPEC-006-structure-aware-layout-and-synchronized-interaction.md`
11. current `RepresentationModel`, layout, viewer, evaluation, and viewer-asset code
12. committed SPEC-006 representation artifacts

Treat BASELINE-001 as a product comparison artifact, not merely historical documentation.

## Experimental Control

This experiment is specifically about **navigation and orientation**.

Hold constant where practical:

- current semantic extraction;
- relationship vocabulary;
- canonical relationship definitions/direction;
- `KnowledgeModel` architecture;
- `StructureDetector` architecture;
- current structure-aware layout grammar;
- synchronized selection grammar;
- provenance behavior;
- warnings;
- visual language of BASELINE-001;
- current upstream semantic defects.

Do not call an LLM or regenerate source semantics merely to create deeper examples.

The deeper models for this experiment should be **fixed, explicit, deterministic fixtures authored for the experiment**.

This is intentional. First prove that semantic zoom is useful. Only then decide how deeper models should be generated automatically.

## Experiment Design

Implement enough data and viewer behavior to compare three conceptual modes on the same deeper content:

### A — BASELINE-001

```text
select concept
    ↓
concept detail only
```

This is the current control.

### B — Replacement drill-down

```text
select/explore concept
    ↓
parent graph disappears
    ↓
deep graph replaces it
```

This represents conventional navigation.

### C — Contextual semantic expansion

```text
select concept
    ↓
EXPLORE
    ↓
parent context remains perceptually available
    +
focused concept is clearly identified
    +
deep local model appears
    ↓
RETURN
    ↓
parent model and prior orientation restored
```

Mode C is the primary hypothesis, but implementation and evaluation must not assume it wins.

The experiment may implement B as a simple comparison toggle/state rather than a polished product feature. Do not build a generic A/B framework.

## Benchmark Domains

Use **Software Architecture** as the primary benchmark because its whole/component structure provides a natural parent → subsystem relationship.

Use **Economics** as the secondary benchmark because its causal structure tests whether deeper explanation can remain anchored to a causal parent model rather than only a hierarchy.

Do not require all five existing domains to have deep fixtures.

Electromagnetism, History, and Biology should continue to render normally at BASELINE-001 behavior unless a minimal fixture is genuinely useful for a regression check.

### Software Architecture fixture

Create one fixed deeper local model beneath an existing concept from the accepted Software Architecture representation.

Prefer an existing node such as the API component if it is present in the accepted artifact.

The deeper fixture should be small — roughly 3–6 nodes and only enough relationships to make exploration meaningful.

Illustrative only:

```text
API component
    ↓ receives
request
    ↓ validated by
validation
    ↓ enables/invokes
order handling
```

Do not blindly use these exact nodes/predicates if they conflict with accepted semantics. Inspect the existing artifact and author a coherent deterministic fixture with explicit provenance metadata appropriate to an experimental fixture.

### Economics fixture

Create one fixed deeper model beneath a concept with obvious causal importance, preferably `market price` if it matches the accepted artifact.

The local model should explain one meaningful mechanism around that concept without pretending to repair the missing higher-order feedback loop.

Keep it small and clearly marked as an experimental fixed deeper model.

## Fixture Semantics and Provenance

The experiment must not blur fixture content with automatically compiled source truth.

Every deeper model must be explicitly identifiable in data as an **experiment fixture**.

If fixture relationships quote or reuse accepted source evidence, preserve that provenance exactly.

If additional explanatory content is manually authored solely for the experiment, mark it clearly as fixture-authored rather than `SOURCE` evidence.

Do not fabricate `SourceSpan` coordinates for manually authored material.

The viewer need not expose ugly developer labels to the learner, but the model/evaluation artifacts must preserve the distinction.

## Minimal Data Model

Introduce the smallest presentation-layer concept needed to express semantic depth.

A possible shape is:

```text
ExplorableRepresentation
    parentRepresentationId
    focusEntityId
    childRepresentation
    provenanceKind
```

or an equivalent explicit structure.

The exact naming is flexible.

Important constraints:

- semantic depth metadata belongs downstream of `KnowledgeModel` / `DetectedStructureSet` for this experiment;
- do not redesign `KnowledgeModel` into a recursive graph-of-graphs;
- do not make every node recursively explorable;
- do not introduce persistence;
- do not create an ontology of semantic resolution levels yet;
- fixed fixtures may be wired through a small presentation/evaluation boundary.

If the cleanest experiment requires no persistent model change and can be represented in evaluation fixture data, prefer that.

## Interaction Grammar

### Selection remains selection

BASELINE-001 behavior stays intact:

```text
click node → persistent selection + detail
hover node → preview
click edge → persistent relationship selection + detail/evidence
```

Selecting a node must **not automatically navigate**.

### Explore

An explorable selected node should expose one clear `Explore` affordance.

`Explore` means:

> Show me a higher-resolution local model of this concept.

Do not use ambiguous labels such as `Open`, `More`, or a bare icon unless an accessible label makes the semantic action clear.

Nodes without a deeper fixture should not pretend to be explorable.

### Return

The learner must have one obvious way to return to the parent resolution.

Use a simple semantic label such as:

```text
Back to Software Architecture
```

or equivalent.

Do not rely solely on browser Back.

### Preserve prior orientation

When returning from a deeper model:

- restore the parent representation;
- restore the parent focus node if practical;
- restore the parent's prior selected state if practical;
- do not return the learner to an arbitrary default representation;
- do not retain stale child selections in the parent.

This restoration behavior is part of the experiment, not polish.

## Contextual Expansion Requirements

Mode C must keep parent context perceptually available while the child model is active.

The implementation may choose the simplest effective technique, for example:

- parent model remains visible but deemphasized around the focused node;
- parent model remains in a compact context panel/header;
- child model opens adjacent to/below the parent while the parent remains legible;
- a parent-context mini-map preserves topology and highlights the focus node.

Do **not** assume a specific layout before testing it.

However, contextual expansion must satisfy these invariants:

1. the parent domain/model name remains visible;
2. the focused parent concept remains identifiable;
3. the child model is visually distinguishable as a deeper resolution;
4. the relationship between parent concept and child model is explicit;
5. the learner can return in one obvious action;
6. provenance/details remain inspectable at the active resolution;
7. the parent context is not so visually dominant that it defeats progressive disclosure.

Avoid trying to render two full-size equally weighted graphs simultaneously if that produces clutter.

## Replacement Drill-Down Requirements

Mode B exists as a comparison, not as a product commitment.

It should use the same child fixture as Mode C but hide/replace the parent graph sufficiently to simulate conventional drill-down.

Keep the implementation minimal.

The purpose is to isolate whether **preserved parent context** adds cognitive value beyond simply having access to deeper information.

## Semantic Navigation State

Use a small explicit navigation state rather than ad hoc DOM hiding.

Conceptually:

```text
NavigationState
    mode: BASELINE | REPLACEMENT | CONTEXTUAL
    parentRepresentationId
    focusEntityId
    childRepresentationId
    parentSelectionSnapshot
    childSelection
```

The exact implementation is flexible.

Important invariants:

- active resolution is explicit;
- selection state and navigation state are related but distinct;
- entering child resolution does not mutate parent semantic truth;
- returning restores parent orientation deterministically;
- domain/representation changes clear incompatible navigation state;
- child node/edge selection uses the same synchronized interaction grammar as BASELINE-001 where practical.

## Visual Language

Stay close to BASELINE-001.

Use the existing typography, colors, cards, relationship controls, evidence treatment, and selected/preview states.

Introduce only the visual cues necessary to communicate:

```text
current resolution
parent context
focused parent concept
child model
Explore / Return
```

Do not redesign the application shell.

Do not add decorative zoom animations. A small transition is acceptable only if already trivial and useful for orientation, but animation is not part of the hypothesis.

## Progressive Disclosure vs Detail Panel

Do not duplicate the existing detail panel as the child model.

The distinction is:

```text
DETAIL
What is this node / relationship?
Why does this edge exist?
What evidence supports it?

EXPLORE
What system/mechanism exists inside or around this concept at a deeper semantic resolution?
```

The existing detail/evidence panel should remain useful within both parent and child resolutions.

## Layout

Reuse current deterministic structure-aware layout logic for child representations wherever possible.

Do not create a new nested-graph layout engine.

If contextual mode needs a compact parent-context layout, implement the smallest deterministic adaptation required.

Preserve canonical semantic direction.

No force simulation or random layout.

## BASELINE-001 Protection

The existing baseline must remain launchable and visually/behaviorally unchanged except for infrastructure changes that are demonstrably neutral.

Do not overwrite `baselines/BASELINE-001-interface/` screenshots.

Do not rewrite `BASELINE-001-interface.md` merely to describe SPEC-007.

If SPEC-007 changes shared viewer code, add regression checks for the baseline interaction grammar.

## Evaluation Interface

Provide a simple way for the owner to compare A/B/C without running multiple complicated commands if practical.

A minimal mode selector in the experimental viewer is acceptable:

```text
Baseline
Replacement drill-down
Contextual expansion
```

Alternatively, separate deterministic URLs/artifact directories are acceptable if simpler.

Do not create experimentation infrastructure beyond what this comparison needs.

## Human Evaluation

The owner must directly compare the three modes using the same child content.

Do not ask for a large questionnaire before natural use.

Capture spontaneous reaction first, then evaluate these dimensions:

### Orientation

- At the deeper level, do I still know where I am in the larger model?
- Can I identify which parent concept I explored?
- Can I return without reconstructing context mentally?

### Understanding

- Does the child model add useful mechanism/detail beyond the node detail panel?
- Does the parent context help me interpret the child model?

### Cognitive load

- Does contextual expansion clarify or clutter?
- Is replacement drill-down actually simpler despite losing context?
- Is the baseline detail panel sufficient, making semantic zoom unnecessary at this scale?

### Interaction coherence

- Does `Explore` feel like a natural extension of select/inspect?
- Does returning restore orientation?
- Does the child model preserve the edge/control/detail/evidence grammar?

### Overall comparison

For each relevant dimension use:

```text
A BASELINE
B REPLACEMENT
C CONTEXTUAL

BETTER / SAME / WORSE
```

The decisive question is:

> When learning something complex, would I rather deepen the model using contextual semantic expansion, replacement drill-down, or stay with the BASELINE-001 detail interaction?

Do not claim measured learning gains from the owner evaluation.

## Machine Evaluation

Machine evaluation should verify integrity, not pretend to score cognition.

At minimum report:

```text
domain
parent representation
focus entity
child representation
fixture provenance kind
mode availability
return target integrity
parent selection restoration integrity
child edge/control identity coverage
canonical direction integrity
provenance integrity
layout determinism
```

For contextual mode, also verify that parent identity, focus identity, and child identity are all present in the rendered/view data.

## Testing Strategy

All normal tests must remain offline and deterministic.

Add focused tests for at least:

- deeper fixture validation;
- fixture provenance distinction;
- only intended nodes expose Explore;
- selection does not automatically navigate;
- Explore enters the intended child representation;
- Replacement mode uses the same child semantic content as Contextual mode;
- Contextual mode retains parent identity and focus identity;
- Return restores parent representation;
- Return restores parent focus/selection where specified;
- domain/representation change clears incompatible navigation state;
- child node selection works;
- child relationship selection synchronizes edge/control/detail/evidence;
- canonical direction remains unchanged;
- source provenance remains unchanged;
- manually authored fixture content never masquerades as source-grounded spans;
- layout remains deterministic;
- BASELINE-001 interaction regression checks continue to pass;
- Biology truthful empty state remains unchanged;
- prior tests continue to pass.

Use lightweight browser/manual validation for the actual interaction. Do not add a heavy browser automation framework solely for this SPEC unless the existing seams prove insufficient.

## Evaluation Artifacts

Create a committed directory such as:

```text
examples/evaluations/spec-007-progressive-disclosure-20260903/
```

Include only useful review artifacts:

- fixed child fixture data;
- deterministic prepared viewer data if applicable;
- machine integrity report;
- human-review template;
- concise README only if needed to launch/compare modes.

Screenshots are optional. Do not create BASELINE-002 before human acceptance.

## Explicit Non-Goals

Do not implement:

- automatic child-model generation;
- recursive semantic compilation;
- arbitrary unlimited depth;
- graph-of-graphs semantic IR;
- new relationship predicates;
- extraction prompt changes;
- event/state redesign;
- source repair;
- inferred missing parent edges;
- Wikipedia/PDF/video/podcast ingestion;
- global search;
- knowledge atlas navigation;
- freeform breadcrumbs across arbitrary graphs;
- persistent user navigation history;
- accounts;
- database/persistence;
- cloud deployment;
- collaboration;
- graph editing;
- simulator/counterfactual propagation;
- quantitative modeling;
- frontend framework migration;
- general nested-graph engine;
- production animation system;
- responsive/mobile redesign;
- formal user-study infrastructure;
- BASELINE-002 before evaluation.

Do not use this experiment as an excuse to repair known upstream semantic limitations.

## Acceptance Criteria

SPEC-007 is technically complete when all are true:

- [ ] BASELINE-001 remains available and behaviorally intact.
- [ ] Fixed deterministic deeper fixtures exist for Software Architecture and Economics.
- [ ] Fixture-authored content is distinguishable from source-grounded content.
- [ ] Selection remains distinct from navigation.
- [ ] Only nodes with child fixtures expose `Explore`.
- [ ] `Explore` enters the correct child model.
- [ ] Replacement drill-down and Contextual expansion use the same child semantic content.
- [ ] Contextual mode preserves visible parent-model identity.
- [ ] Contextual mode preserves visible focus-concept identity.
- [ ] Child resolution is visually distinguishable from parent resolution.
- [ ] `Return` restores the correct parent representation.
- [ ] Parent focus/selection restoration is deterministic where specified.
- [ ] Child node/relationship interactions retain synchronized semantic-selection behavior.
- [ ] Provenance remains truthful and inspectable.
- [ ] Canonical semantic direction remains unchanged.
- [ ] Layout remains deterministic.
- [ ] No new LLM/network calls are required.
- [ ] No semantic IR redesign is introduced merely to support the fixture experiment.
- [ ] No frontend framework/general nested-graph engine is introduced.
- [ ] Existing tests plus new focused tests pass offline.
- [ ] Machine integrity report is committed.
- [ ] Human comparison template is committed.
- [ ] Exact local review command(s) are provided.
- [ ] Implementation is committed and pushed to canonical GitHub before handoff.
- [ ] No `DEBRIEF-007` is created during implementation.

The primary product acceptance criterion is human:

> Does contextual semantic expansion preserve orientation and improve useful depth enough to beat both replacement drill-down and BASELINE-001 for the owner benchmark?

A valid outcome is **NO**. If the contextual model is cluttered, confusing, or unnecessary, preserve that result rather than expanding architecture to rescue the hypothesis.

## Required Handoff

When complete, Codex must report:

1. architecture/data changes;
2. exact deeper-fixture structure and provenance distinction;
3. Software Architecture fixture content;
4. Economics fixture content;
5. navigation-state model;
6. selection vs Explore behavior;
7. Replacement mode behavior;
8. Contextual mode behavior;
9. Return/restoration behavior;
10. how BASELINE-001 was protected;
11. child layout strategy;
12. synchronized interaction behavior inside child models;
13. files added/changed;
14. exact automated test result;
15. exact machine-evaluation command/result;
16. exact local launch/review command(s);
17. simplest A/B/C comparison procedure;
18. provenance-integrity result;
19. canonical-direction result;
20. determinism result;
21. known UX weaknesses;
22. dependencies added/removed;
23. deviations from SPEC;
24. commit SHA;
25. confirmation pushed to canonical `origin/main`.

Do not create `DEBRIEF-007`. Human evaluation follows independent repository review.

## Operational Learning Capture

The eventual debrief should record whether:

- fixed handcrafted depth fixtures were sufficient to test navigation before recursive semantic architecture;
- preserved parent context materially helped orientation;
- replacement drill-down was simpler or cognitively worse;
- the current detail panel already provides enough depth at this graph scale;
- parent selection restoration matters in practice;
- semantic navigation state remains simple enough for the current vanilla viewer;
- deeper models make upstream event/state/provenance limitations more consequential;
- the project has earned the right to design automatic multi-resolution compilation;
- BASELINE-001 remains the best control or a future BASELINE-002 is justified.

## Decision Gate After SPEC-007

Do not implement this section during SPEC-007.

### If Contextual expansion strongly wins

The project has evidence for semantic zoom. The next architectural question becomes:

> How should Knowledge Compiler automatically generate trustworthy multi-resolution models from source material?

Only then consider recursive/multi-resolution semantic architecture.

### If Replacement drill-down wins

Depth is useful, but persistent parent context may be unnecessary or too visually expensive. Preserve the simpler navigation grammar.

### If BASELINE-001 wins

The current model/detail interaction may already be near the right cognitive density. Do not add semantic-depth architecture until a harder learning case demonstrates need.

### If all modes expose upstream semantic weakness

Return upstream to event/state/endpoint modeling before adding more navigation depth.

## Final Constraint

SPEC-007 must answer a product question before creating an architecture:

```text
DOES SEMANTIC ZOOM HELP?
        ↓ yes
HOW SHOULD MULTI-RESOLUTION KNOWLEDGE BE GENERATED?
```

Do not reverse that order.
