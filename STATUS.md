# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. It points to the active approved work packet; agents must not infer active work from filename recency.

## Current accepted learner-navigation baseline

`BASELINE-004 — learner navigation workspace`

BASELINE-001 through BASELINE-004 remain preserved historical/accepted states and must not be modified by ordinary implementation work.

## Best-known focused-learning candidate

`SPEC-030 — distinct learning surface representation`

Owner verdict: `ROLE_SEPARATION_CONFIRMED`

Accepted invariant:

```text
MY MAP
→ navigate revealed knowledge

WHAT DOES THIS MEAN?
→ translate selected knowledge for understanding

EXPLORE NEXT
→ reveal trusted frontier
```

## Owner review of current revealed-navigation candidate

`SPEC-033 — canonical revealed-knowledge tree`

Owner observation: implementation behaves as intended in the reviewed navigation flows and is the strongest navigation architecture so far. The revealed, deduplicated, collapsible tree is sufficient to stop treating navigation as the primary product bottleneck.

Formal debrief/promotion remains separate; SPEC-034 must preserve the current SPEC-033 implementation/candidate state and must not redesign navigation.

## Current approved work packet

```text
specs/SPEC-034-representation-strategy-grammar.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current product direction

The project returns to the core learning thesis.

The focused learning surface must not equate explanation with either prose or diagrams. It should choose a representation because the representation fits the trusted semantic structure currently in focus.

```text
selected canonical object
        ↓
trusted local semantic structure
        ↓
representation strategy resolver
        ↓
learner-facing representation
```

Candidate forms include causal/mechanism, process/sequence, hierarchy/composition, compare/contrast, worked example, focused relationship, and concise prose fallback. The grammar is intentionally small and deterministic in SPEC-034.

The active principle is:

> The compiler should choose the representation that minimizes the cognitive work required to understand the trusted structure currently in focus.

## Current gate

Implement and evaluate an explicit deterministic representation-strategy grammar using committed trusted material only.

Success requires materially different representation forms for different semantic structures, structure-driven rather than domain-driven selection, truthful fallback when richer forms are unsupported, preserved provenance, depth independence, and no regression to the revealed-navigation architecture.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- prior SPEC evaluation artifacts;
- SPEC-030 role separation;
- SPEC-031 reciprocal/multi-edge semantic identity;
- current SPEC-033 canonical revealed-knowledge navigation implementation/candidate;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- source-bounded depth behavior;
- unrelated user work.

## Explicitly deferred

Do not yet implement:

- live/model-generated pedagogy;
- personalization or learner-state modeling;
- quizzes/mastery;
- guided pathways/courses;
- automatic analogy generation;
- broad navigation redesign;
- universal final renderer.

A later packet may test model-assisted explanatory generation only after the deterministic representation seam demonstrates value.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
