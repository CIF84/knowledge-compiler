# Project Memory

Knowledge Compiler uses paired specification and debrief documents as its internal project memory.

The purpose is to preserve not only **what was intended**, but also **what actually happened and what the project learned**.

This is especially important for a project whose architecture and product thesis are expected to evolve through experiments.

## Memory Unit

Every implementation increment should produce a pair:

```text
specs/SPEC-NNN-short-name.md
        ↕
debriefs/DEBRIEF-NNN-short-name.md
```

The number and short name must match.

## Role of a SPEC

A SPEC is prospective. It records the problem, uncertainty, scope, non-goals, architectural constraints, acceptance criteria, and implementation guidance.

## Role of a DEBRIEF

A DEBRIEF is retrospective. It records what was actually implemented, what happened, what was learned, material deviations, decisions, unresolved questions, and implications for the next experiment.

A debrief is not a changelog. Its main job is to preserve **why the project now believes what it believes**.

## Lifecycle

```text
QUESTION / UNCERTAINTY
        ↓
      SPEC-N
        ↓
 IMPLEMENT + TEST
        ↓
   REVIEW REALITY
        ↓
    DEBRIEF-N
        ↓
UPDATED PROJECT MODEL
        ↓
      SPEC-N+1
```

## Rules

1. No completed SPEC should remain without a matching DEBRIEF.
2. The DEBRIEF should be written only after implementation and review.
3. Do not rewrite old debriefs simply because later thinking changes.
4. If a previous decision is overturned, record the change in the new debrief and reference the earlier decision.
5. Keep speculative future architecture out of debrief decisions unless implementation produced evidence for it.
6. Record deferred issues without automatically expanding the completed milestone to fix them.
7. Every new SPEC should read relevant prior DEBRIEFs before defining scope.
8. Prefer explicit uncertainty over retrospective certainty.

## Current Memory Index

| Increment | Spec | Debrief | State |
| --- | --- | --- | --- |
| 001 — Text to KnowledgeModel | [`SPEC-001`](specs/SPEC-001-text-to-knowledge-model.md) | [`DEBRIEF-001`](debriefs/DEBRIEF-001-text-to-knowledge-model.md) | Accepted |
| 002 — LLM Semantic Extraction | [`SPEC-002`](specs/SPEC-002-llm-semantic-extraction.md) | [`DEBRIEF-002`](debriefs/DEBRIEF-002-llm-semantic-extraction.md) | Accepted — mixed semantic outcome |
| 003 — Relationship Semantics | [`SPEC-003`](specs/SPEC-003-relationship-semantics.md) | [`DEBRIEF-003`](debriefs/DEBRIEF-003-relationship-semantics.md) | Accepted — improved semantic precision |

## Current Learning Summary

### After SPEC-001

- a source-grounded semantic `KnowledgeModel` is a viable intermediate representation;
- strict validation, conservative deduplication, and provider-neutral extraction boundaries are useful architectural foundations;
- deterministic fixtures provide a strong offline test seam around probabilistic extraction.

### After SPEC-002

- a real LLM can populate the same IR across physics, software architecture, economics, biology, and history without downstream redesign;
- exact evidence grounding works better when the LLM returns quotes and deterministic code resolves source coordinates;
- schema validity is not semantic correctness;
- the initial relationship vocabulary and bare enum labels caused cross-domain semantic distortion;
- multi-domain live experiments are cheap enough to repeat frequently.

### After SPEC-003

- explicit relationship contracts materially improve predicate choice and direction across the same five-domain corpus;
- only three new general predicates (`AFFECTS`, `BINDS_TO`, `TRANSFERS_TO`) were needed to fix several cross-domain distortions;
- relationship families provide useful lightweight semantic organization without requiring a schema migration;
- truthful claims are preferable to forced graph edges when no predicate fits;
- remaining semantic errors now concentrate more on endpoint selection, polarity, duplicates, event/state distinctions, and entity modeling than on missing predicates;
- further vocabulary expansion is not currently justified;
- the next important architectural question is whether the current graph can support useful higher-order structure detection.

## Active Decisions

```text
KnowledgeModel is the semantic IR.
Origin: DEBRIEF-001
Strengthened: DEBRIEF-002
Status: active

Provider-specific extraction stays behind KnowledgeExtractor.
Origin: DEBRIEF-001
Strengthened: DEBRIEF-002
Status: active

Evidence coordinates are resolved deterministically from model-nominated exact quotes.
Origin: DEBRIEF-002
Status: active

Semantic quality is evaluated separately from schema validity.
Origin: DEBRIEF-002
Status: active

Relationship vocabulary evolves through cross-domain evidence, not opportunistic enum growth.
Origin: DEBRIEF-002
Strengthened: DEBRIEF-003
Status: active

Relationship semantics have one canonical provider-independent definition.
Origin: DEBRIEF-003
Status: active

Explicit meaning and direction are part of a relationship contract.
Origin: DEBRIEF-003
Status: active

Prefer truthful claims over forced edges.
Origin: DEBRIEF-003
Status: active

Freeze relationship-vocabulary expansion until new cross-domain evidence justifies it.
Origin: DEBRIEF-003
Status: active
```

## Why This Exists

Git history tells us **what changed**.

Specs tell us **what we intended to change**.

Debriefs tell us **what we learned from changing it**.

Together they provide enough context for a future human or AI collaborator to reconstruct the project’s reasoning even if the original conversation history is unavailable.
