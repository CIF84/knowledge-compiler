# DEBRIEF-030 — Distinct Learning Surface Representation

## Outcome

Owner verdict:

```text
ROLE_SEPARATION_CONFIRMED
```

SPEC-030 is a major product/UI success. The learning surface now materially differs from the navigation map while remaining grounded in the same semantic focus.

## What worked

Owner review found that:

- the left map remains the spatial/navigation surface;
- the right pane now translates selected knowledge into focused learner-facing representations rather than reproducing the full map;
- canonical relationships are represented as focused source → predicate → target explanations with evidence;
- source-backed explanatory material is represented directly as grounded explanation plus provenance rather than as a second graph;
- recursive/deeper-map interactions remain coherent with the new learning-surface role;
- the major UI capability bottleneck observed before SPEC-029 remains substantially resolved;
- the SPEC-030 state is the strongest overall UI version reviewed so far.

The deterministic report also records passing duplicate-map, recursive-depth, bidirectional-interaction, state-coherence, and fixed-domain checks.

## Newly exposed defect

The Electromagnetism fixture exposes a narrower semantic-identity problem that SPEC-030 does not solve.

The ground-level map visibly contains two directed canonical relationships between the same endpoint pair:

```text
Electric field → INDUCES → Magnetic field
Magnetic field → INDUCES → Electric field
```

The map correctly renders the reciprocal structure. However, interacting with the shared visual relationship resolves the learning surface only to:

```text
Electric field → INDUCES → Magnetic field
```

The reverse canonical assertion is therefore visually present but not independently recoverable through the current relationship interaction.

## Interpretation

This is not evidence that map/learning-surface role separation failed.

It exposes a more precise semantic-representation question:

> What is the selectable semantic identity when multiple canonical directed edges occupy one shared visual relationship geometry?

The implementation must not silently collapse multiple canonical relationship identities into whichever edge happens to win visual/event resolution.

Nor should reciprocal assertions automatically be rewritten as one synthetic bidirectional fact: the two directed assertions may have independent semantic identity, grounding, evidence, or explanation.

## Decision

Preserve SPEC-030 as the best-known UI candidate.

Do not reopen broad UI architecture, canonical interaction state, recursive behavior, or learning-surface role separation.

The next experiment should isolate reciprocal/multi-edge relationship semantics and prove that every canonical edge represented by shared geometry remains discoverable and truthfully representable.

## Stronger invariant

> A visual relationship containing N canonical semantic edges must not silently resolve to fewer than N semantic identities.

The interface may group reciprocal edges visually, but grouping must never erase semantic multiplicity.
