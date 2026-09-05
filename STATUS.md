# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. It points to the active approved work packet; agents must not infer active work from filename recency.

## Current accepted learner-navigation baseline

`BASELINE-004 — learner navigation workspace`

BASELINE-001, BASELINE-002, BASELINE-003, and BASELINE-004 remain preserved historical/accepted states and must not be modified by ordinary implementation work.

## Last completed work packet

`SPEC-024 — depth as continuous map expansion`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Owner verdict: `DEPTH_NAVIGATION_BETTER`

Result: continuous spatial depth expansion is validated as a better navigation model than nested replacement depth. Deeper material remains connected to its origin in the knowledge map, parent context stays recoverable, and map pan/zoom provides a scalable surface. Owner review identified a remaining interaction gap: deeper selections do not yet inherit the same map ↔ representation ↔ explanation/evidence synchronization grammar as ordinary selections.

SPEC-024 remains preserved unchanged as a functional historical experiment. It is not promoted to an accepted baseline by this verdict.

## Current approved work packet

```text
specs/SPEC-025-depth-invariant-interaction-grammar.md
```

Status: `APPROVED`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-025 implementation is authorized offline. Codex may execute the canonical active packet without additional owner interpretation. No live/model/external calls, semantic changes, baseline mutation, or promotion are authorized. If the machine gate passes, owner cognitive review is required before a product verdict.

## Frozen / protected state

- executable and frozen assets for BASELINE-001 through BASELINE-004;
- BASELINE-004 learner-navigation behavior accepted after SPEC-022;
- frozen SPEC-020 realistic quantum semantic packet and its reviewed defects;
- frozen SPEC-021 explanatory projection semantics;
- completed SPEC-023/FIX-023 functional depth artifact as historical evidence;
- completed SPEC-024 continuous-map depth artifact, preserved unchanged after owner verdict `DEPTH_NAVIGATION_BETTER`;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- unrelated user work.

## Next intended action

Codex executes the current approved packet. The experiment tests whether every revealed knowledge item can use one depth-invariant map ↔ learning synchronization grammar while preserving SPEC-024 spatial depth continuity and semantic trust.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
