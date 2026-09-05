# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. It points to the active approved work packet; agents must not infer active work from filename recency.

## Current accepted learner-navigation baseline

`BASELINE-004 — learner navigation workspace`

BASELINE-001, BASELINE-002, BASELINE-003, and BASELINE-004 remain preserved historical/accepted states and must not be modified by ordinary implementation work.

## Last completed work packet

`SPEC-025 — depth-invariant interaction grammar`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Owner verdict: `MIXED`

Result: depth-level map ↔ learning-pane synchronization now works, but deeper topology still violates the stronger interaction invariant. Canonical and explanatory connections inside the deeper map do not consistently expose the same learner-readable direction, predicate, interaction, and explanation grammar as the parent map. Preserve SPEC-025 unchanged as a functional historical experiment; no baseline promotion is authorized.

## Current approved work packet

```text
specs/SPEC-026-semantic-interaction-invariance.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-026 is approved for autonomous offline implementation under the repository operating model. No live/model/external calls, semantic regeneration, trusted vocabulary/admission changes, baseline mutation, or baseline promotion are authorized. After the machine gate passes, owner cognitive review is required.

## Frozen / protected state

- executable and frozen assets for BASELINE-001 through BASELINE-004;
- BASELINE-004 learner-navigation behavior accepted after SPEC-022;
- frozen SPEC-020 realistic quantum semantic packet and its reviewed defects;
- frozen SPEC-021 explanatory projection semantics;
- completed SPEC-023/FIX-023 functional depth artifact as historical evidence;
- completed SPEC-024 continuous-map depth artifact, preserved unchanged after owner verdict `DEPTH_NAVIGATION_BETTER`;
- completed SPEC-025 depth-invariant-selection artifact, preserved unchanged after owner verdict `MIXED`;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- unrelated user work.

## Next intended action

Codex executes the current approved packet. SPEC-026 tests whether the deeper map can expose semantic connections using the same learner-facing visual, interaction, and explanatory grammar as the parent map without fabricating canonical relationships or weakening semantic-strength distinctions.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
