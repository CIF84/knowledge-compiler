# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. It points to the active approved work packet; agents must not infer active work from filename recency.

## Current accepted learner-navigation baseline

`BASELINE-004 — learner navigation workspace`

BASELINE-001 through BASELINE-004 remain preserved historical/accepted states and must not be modified by ordinary implementation work.

## Best-known focused-learning candidate

`SPEC-030 — distinct learning surface representation`

Owner verdict: `ROLE_SEPARATION_CONFIRMED`

The separation remains accepted:

```text
navigation / map
→ where am I / what territory have I revealed?

focused learning surface
→ what does this selected object mean?
```

## Last completed work packet

`SPEC-032 — learning-path navigation separation`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `HISTORY_NAVIGATION_REJECTED__REVEALED_KNOWLEDGE_TREE_PREFERRED`

Owner testing produced useful evidence but rejected visit-history nesting as the visible navigation architecture. Repeated history branches duplicated concepts/orientations, exhausted horizontal space, produced unreadable vertical labels, and deeper exploration eventually triggered an interaction freeze. Preserve SPEC-032 as historical evidence; do not patch its history tree as the primary solution.

## Current approved work packet

```text
specs/SPEC-033-canonical-revealed-knowledge-tree.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: implement/test/document SPEC-033 only

Human gate: owner review after implementation

Promotion: `NOT_AUTHORIZED`

## Current product direction

The left navigation surface is now defined as **canonical revealed knowledge**, not learning history.

```text
MY MAP
→ knowledge territory the learner has uncovered

WHAT DOES THIS MEAN?
→ focused explanation of the selected canonical object

EXPLORE NEXT
→ trusted frontier that could be revealed next
```

Only revealed knowledge belongs in the visible map. Revisiting an existing canonical concept/relationship must not duplicate it.

History may still be captured internally as telemetry/evidence, but it must not structurally define navigation.

Critical distinction:

```text
revealed knowledge ≠ understood/mastered knowledge
```

A future learner-state model may represent understanding separately. It is not part of SPEC-033.

## Current gate

Implement a canonical, deduplicated, collapsible revealed-knowledge tree that scales materially better than SPEC-032, preserves the successful focused-learning surface, and remains interactive after repeated deep exploration.

SPEC-033 must specifically address the two owner-observed failures:

1. history nesting exhausted horizontal space and broke label legibility;
2. `Explore deeper` under the double-slit experiment eventually left the web app non-interactive.

## Frozen / protected state

- executable/frozen assets for BASELINE-001 through BASELINE-004;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- SPEC-030 role separation;
- SPEC-031 reciprocal/multi-edge semantic identity;
- prior completed SPEC artifacts as historical evidence;
- source-bounded depth behavior already validated;
- unrelated user work.

## Direction after SPEC-033

Do not implement these yet, but preserve the distinctions:

```text
KNOWLEDGE TOPOLOGY
canonical semantic structure

REVEALED MAP
subset/projection the learner has uncovered

LEARNER STATE
separate evidence about understanding

HISTORY
observed traversal / telemetry

PATHWAY
recommended traversal through knowledge
```

Possible later sequence, contingent on evidence:

1. learner-state model attached to canonical concepts/relationships;
2. guided/recommended pathways as coordinates through the same knowledge world;
3. learning-outcome evaluation;
4. personalization based on explicit/validated learner evidence.

## Coordination rule

This file records durable current coordination state. It is not a manually maintained source for runtime counts, derived product truth, or historical experiment evidence.
