# DEBRIEF-028 — Single Canonical Interaction State

## Outcome

Owner verdict:

```text
MIXED
```

SPEC-028 materially improved the interaction architecture but did not yet establish complete learner-visible state coherence.

## What worked

Owner review found that most previously reported recursive-depth divergence was fixed:

- deeper-map concept, relationship, and source-explanation interactions are substantially coherent across map and right pane;
- hover/preview and committed selection are much more consistently projected;
- recursive depth no longer appears to require an independent interaction grammar;
- the one-canonical-interaction-state direction remains supported rather than falsified.

The implementation's deterministic gates also passed the ten-level recursion, state-equality, stale-state, browser-interaction, and console checks recorded in the SPEC-028 evaluation artifact.

## Remaining failures

Two important boundary failures remain.

### 1. Incomplete semantic-object coverage at ground level

The owner observed that some relationships in an ordinary ground-level Software Architecture map did not propagate correctly into the learning/right pane.

This suggests that some existing learner-visible interaction paths still bypass, incompletely resolve into, or incompletely project from the canonical semantic interaction state.

### 2. Context-transition stale projection

The owner moved from a deep double-slit interaction back to the ground-level History of Printing map. The map correctly changed context and responded to History of Printing interactions, while the right pane continued to show the previous double-slit deeper map.

This is a context lifecycle failure rather than a depth-recursion failure.

## Main learning

SPEC-028 supports the architectural principle:

> There is exactly one learner interaction state. Every learner-visible surface is a projection of it.

But the stronger required principle is now:

> There is exactly one active learner context and one learner interaction state, and context transitions replace them atomically.

A canonical interaction store is insufficient if an old context-specific projection can survive after the active knowledge context changes.

## Failure attribution

Primary attribution:

```text
interaction-state lifecycle / context transition
```

Secondary attribution:

```text
incomplete migration of learner-visible semantic object classes into the canonical interaction path
```

Do not reopen recursive-depth geometry or add new surface-to-surface synchronization callbacks as the default repair.

## Decision

Preserve SPEC-028 as evidence of a materially improved but incomplete architecture.

Do not promote a new learner-navigation baseline.

Proceed to a narrow follow-up experiment testing atomic context transitions and complete semantic-object coverage through the canonical state path.

## Next uncertainty

Can every learner-visible semantic interaction, including ordinary ground-level relationships, pass through the same canonical state path, while changing active knowledge context atomically invalidates all semantic state and projections belonging to the previous context?
