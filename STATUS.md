# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. It points to the active approved work packet; agents must not infer active work from filename recency.

## Current accepted learner-navigation baseline

`BASELINE-004 — learner navigation workspace`

BASELINE-001, BASELINE-002, BASELINE-003, and BASELINE-004 remain preserved historical/accepted states and must not be modified by ordinary implementation work.

## Best-known UI baseline candidate

`SPEC-030 — distinct learning surface representation`

Owner verdict: `ROLE_SEPARATION_CONFIRMED`

Result: strongest UI version so far. Map/navigation and learning/understanding responsibilities became materially distinct while retaining shared canonical semantic state and recursive interaction behavior. Preserve this state as the best-known working candidate; it is not promoted to a formal baseline.

## Last completed work packet

`SPEC-031 — reciprocal and multi-edge relationship semantics`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Owner review status: `RELATIONSHIP_MULTIPLICITY_CONFIRMED`

Result: reciprocal canonical directions sharing visual geometry are independently recoverable and truthfully represented. See `debriefs/DEBRIEF-031-reciprocal-and-multi-edge-relationship-semantics.md`.

## Current approved work packet

```text
specs/SPEC-032-learning-path-navigation-separation.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-032 is approved for offline implementation. The experiment separates learner-visible traversal history from the internal domain knowledge graph, restores the right learning surface as the primary explanatory surface, and moves next-step discovery into deterministic exploration suggestions. No live/model/external calls or baseline promotion are authorized.

## Frozen / protected state

- executable and frozen assets for BASELINE-001 through BASELINE-004;
- BASELINE-004 learner-navigation behavior accepted after SPEC-022;
- frozen SPEC-020 realistic quantum semantic packet and its reviewed defects;
- frozen SPEC-021 explanatory projection semantics;
- completed SPEC-023/FIX-023 functional depth artifact as historical evidence;
- completed SPEC-024 continuous-map depth artifact, preserved unchanged after owner verdict `DEPTH_NAVIGATION_BETTER`;
- completed SPEC-025 depth-invariant-selection artifact, preserved unchanged after owner verdict `MIXED`;
- completed SPEC-026 semantic-interaction artifact, preserved unchanged after owner verdict `MIXED`;
- completed SPEC-027 recursive-interaction artifact, preserved unchanged after owner verdict `MIXED`;
- completed SPEC-028 canonical-interaction-state artifact, preserved as evidence after owner verdict `MIXED`;
- completed SPEC-029 atomic-context artifact, preserved as historical evidence after owner verdict `MIXED`;
- completed SPEC-030 distinct-learning-surface candidate, preserved as best-known UI candidate after owner verdict `ROLE_SEPARATION_CONFIRMED`;
- completed SPEC-031 reciprocal/multi-edge candidate, preserved after owner verdict `RELATIONSHIP_MULTIPLICITY_CONFIRMED`;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- unrelated user work.

## Next intended action

Codex executes `specs/SPEC-032-learning-path-navigation-separation.md` exactly as the active approved packet, then returns the required owner-review artifact and handoff.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
