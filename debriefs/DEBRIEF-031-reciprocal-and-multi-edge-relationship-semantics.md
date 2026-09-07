# DEBRIEF-031 — Reciprocal and Multi-Edge Relationship Semantics

## Outcome

Owner verdict:

```text
RELATIONSHIP_MULTIPLICITY_CONFIRMED
```

SPEC-031 succeeds at the narrow semantic-interaction problem it was designed to test. Reciprocal canonical relationships sharing one visual corridor are now independently recoverable and truthfully projected into the learning surface.

## What worked

Owner review found that:

- the Electric field / Magnetic field connection now exposes both canonical `INDUCES` directions;
- the learner can deliberately choose either directed assertion;
- the map highlights the chosen direction rather than silently collapsing to one default edge;
- the learning surface reverses source and target correctly for the selected canonical identity;
- evidence/provenance follows the selected direction;
- ordinary relationship interaction remains usable;
- no new functional defect was observed in the SPEC-031 target behavior.

## Product-level realization exposed by the success

The successful fix also made a larger architectural problem easier to see.

The current interface has progressively asked the navigation map to carry too much of the domain model directly. Over successive experiments the map acquired:

- domain concepts;
- canonical predicates;
- explanatory/source-backed nodes;
- recursive deeper structures;
- relationship multiplicity controls;
- interaction-state mirroring with the learning surface.

This is technically capable, but it is no longer obviously the best learner-facing abstraction.

Comparing the current workspace with the earlier SPEC-006/007-style learning surface reveals that the older representation was substantially stronger for explanation. The later work improved navigation, recursion, semantic identity, provenance, and relationship correctness, but some of that implementation complexity leaked into the learner-visible navigation surface.

## Revised decomposition

The product should separate four responsibilities that have been partially conflated:

```text
KNOWLEDGE MODEL
what is known and how it is semantically connected

LEARNING SURFACE
how the current object should be represented for understanding

EXPLORATION SUGGESTIONS
where the learner may choose to go next

LEARNING-PATH NAVIGATION
how the learner arrived at the current object and where prior branches remain available
```

The key distinction is:

```text
knowledge graph != learning-path graph
```

The knowledge graph is an internal/domain model.

The learning-path graph is a learner-specific traversal history. Its edges mean "I travelled from here to there", not necessarily a canonical domain predicate such as `CAUSES`, `INDUCES`, `PART_OF`, or `EXAMPLE_OF`.

## Why this matters

This decomposition offers a simpler recursion model.

At arbitrary depth, the learner should not encounter a new interaction grammar or an increasingly overloaded map. A ten-step exploration can simply extend a traversal path:

```text
A → B → C → D → ... → J
```

Branches remain visible as alternate previously visited paths, similar to navigating a filesystem path and returning to an earlier directory to choose another branch.

Meanwhile the learning surface remains free to use whatever grounded representation best explains the current object: focused diagram, comparison, causal chain, text, evidence view, hierarchy, timeline, or another supported form.

## What must be preserved

This architectural correction must not discard the capabilities developed through SPEC-031.

Preserve as engine/infrastructure capability:

- canonical semantic identity;
- trusted predicates and directed relationships;
- source-backed explanatory distinction;
- provenance and evidence;
- canonical interaction state;
- recursive/depth-independent semantics;
- relationship multiplicity;
- deterministic representation resolution;
- fail-closed semantic behavior.

The change is primarily about which of those capabilities must be visible in the navigation UI.

## Decision

Do not continue incrementally enriching the current domain-graph navigation UI.

The next experiment should test whether navigation can be reduced to a learner-specific traversal graph while restoring the learning surface as the primary explanatory representation and moving "where next?" into an explicit suggestion mechanism.

Do not revert to SPEC-006/007 code. Recover its product principle, not its historical implementation.

## Stronger product invariant

> **The knowledge model describes what is known. The learning surface explains what I am learning. Exploration suggestions tell me where I could go. The learning-path map remembers how I got here.**

And:

> **A richer internal knowledge model should permit a simpler learner-visible interface, not require the interface to expose the model literally.**
