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

Example:

```text
specs/SPEC-001-text-to-knowledge-model.md
debriefs/DEBRIEF-001-text-to-knowledge-model.md
```

## Role of a SPEC

A SPEC is prospective.

It records:

- the problem being addressed;
- the hypothesis or uncertainty being tested;
- scope;
- explicit non-goals;
- architectural constraints;
- expected interfaces and data contracts;
- acceptance criteria;
- implementation guidance.

A SPEC should describe the desired increment without pretending to know what implementation will teach us.

## Role of a DEBRIEF

A DEBRIEF is retrospective.

It records:

- what was actually implemented;
- outcome against the original hypothesis;
- findings and learnings;
- material deviations from the spec;
- architecture or product decisions that should carry forward;
- engineering follow-ups discovered but deliberately deferred;
- unresolved questions;
- implications for the next spec;
- relevant implementation commit(s).

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

The debrief closes the learning loop.

## Rules

1. No completed SPEC should remain without a matching DEBRIEF.
2. The DEBRIEF should be written only after implementation and review.
3. Do not rewrite old debriefs simply because later thinking changes. They are historical records.
4. If a previous decision is overturned, record the change in the new debrief and reference the earlier decision.
5. Keep speculative future architecture out of debrief decisions unless implementation produced evidence for it.
6. Record deferred issues without automatically expanding the completed milestone to fix them.
7. Every new SPEC should read relevant prior DEBRIEFS before defining scope.
8. Prefer explicit uncertainty over retrospective certainty.

## Decision Provenance

When an architectural or product decision matters across increments, record where it came from.

Example:

```text
Decision: KnowledgeModel is the semantic IR.
Origin: DEBRIEF-001
Status: active
```

If later overturned:

```text
Decision: Replace single KnowledgeModel with layered semantic IR.
Origin: DEBRIEF-006
Supersedes: DEBRIEF-001 decision on single semantic IR
```

This creates an evolutionary trail without requiring a separate heavyweight architecture-decision process during the early builder phase.

## Current Memory Index

| Increment | Spec | Debrief | State |
| --- | --- | --- | --- |
| 001 — Text to KnowledgeModel | [`SPEC-001`](specs/SPEC-001-text-to-knowledge-model.md) | [`DEBRIEF-001`](debriefs/DEBRIEF-001-text-to-knowledge-model.md) | Accepted |
| 002 — LLM Semantic Extraction | [`SPEC-002`](specs/SPEC-002-llm-semantic-extraction.md) | [`DEBRIEF-002`](debriefs/DEBRIEF-002-llm-semantic-extraction.md) | Accepted — mixed semantic outcome |

## Current Learning Summary

### After SPEC-001

- a source-grounded semantic `KnowledgeModel` is a viable intermediate representation;
- strict validation, conservative deduplication, and provider-neutral extraction boundaries are useful architectural foundations;
- deterministic fixtures provide a strong offline test seam around probabilistic extraction.

### After SPEC-002

- a real LLM can populate the same IR across physics, software architecture, economics, biology, and history without downstream architectural redesign;
- exact evidence grounding works better when the LLM returns quotes and deterministic code resolves source coordinates;
- fail-closed validation caught real provenance and ambiguity failures without weakening invariants;
- cross-domain schema validity is not enough: relationship meaning and direction can still be wrong;
- the initial relationship vocabulary is too narrow in several domains and can force semantic distortions;
- multi-domain live experiments are cheap enough to repeat frequently;
- the next important product problem is relationship semantics, not visualization.

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
Status: active
```

## Why This Exists

Git history tells us **what changed**.

Specs tell us **what we intended to change**.

Debriefs tell us **what we learned from changing it**.

Together they provide enough context for a future human or AI collaborator to reconstruct the project’s reasoning even if the original conversation history is unavailable.
