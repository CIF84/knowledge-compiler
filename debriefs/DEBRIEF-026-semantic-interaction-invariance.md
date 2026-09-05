# DEBRIEF-026 — Semantic Interaction Invariance

## Outcome

Final owner verdict:

```text
MIXED
```

SPEC-026 improved deeper-map semantic legibility and interaction, but did not achieve full depth-invariant interaction grammar.

## What worked

Owner review confirmed meaningful progress:

- deeper-map concept nodes are interactive;
- deeper-map canonical relationships now expose learner-readable labels;
- the right learning pane mirrors deeper-map selections correctly;
- canonical relationship selection can surface relationship meaning and evidence;
- source-backed explanatory material is distinguishable from canonical relationships;
- continuous map expansion from SPEC-024 remains intact;
- the accepted BASELINE-004 visual/workspace grammar remains recognizable.

## What failed

The owner observed that the interface still behaves differently at depth:

- deeper-map items do not consistently respond to hover the way parent-map items do;
- interaction initiated in the right pane does not consistently propagate back to the deeper map;
- map → representation/explanation synchronization is stronger than representation/explanation → map synchronization;
- therefore the deeper region still behaves like a partially separate interaction implementation rather than another region of the same knowledge world.

The central invariant remains unmet:

> Depth should change what knowledge is available, not how the interface behaves.

## Key finding

SPEC-026 treated semantic legibility correctly, but the remaining problem is broader than connection rendering.

The system still appears to contain distinct interaction paths for ordinary map content and depth-expanded content. Continuing to patch missing behaviors individually risks an endless sequence of depth-specific fixes.

The next experiment should therefore test a stronger architectural requirement:

> A learner should interact with any revealed knowledge using the same map ↔ representation ↔ explanation grammar regardless of how many depth expansions led to it.

Stronger formulation:

> Depth is a property of knowledge availability, never a property of interaction.

## Product implication

The desired interaction model is one bidirectional current-focus system shared by every visible semantic object:

```text
map
↕
representation
↕
explanation / evidence
```

Hover, preview, selection, relationship inspection, evidence synchronization, clear-selection behavior, and focus styling should derive from semantic object identity/type—not parent-vs-depth location.

## Preservation decision

Preserve SPEC-026 unchanged as historical evidence of improved semantic legibility and partial interaction convergence.

Do not promote SPEC-026 to a new baseline.

BASELINE-004 remains the accepted learner-navigation baseline.

## Next implication

Create SPEC-027 to collapse parent and depth interaction paths into one recursive, bidirectional interaction contract and test parity at ground level, first expansion, and synthetic second expansion.

The next packet should not be framed as a hover fix or right-pane synchronization patch. Those are symptoms of the duplicated interaction architecture.
