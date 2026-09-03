# Project Memory

Knowledge Compiler uses paired specification and debrief documents as its internal project memory.

The purpose is to preserve not only **what was intended**, but also **what actually happened and what the project learned**.

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
7. Every new SPEC should read relevant prior DEBRIEFS before defining scope.
8. Prefer explicit uncertainty over retrospective certainty.

## Current Memory Index

| Increment | Spec | Debrief | State |
| --- | --- | --- | --- |
| 001 — Text to KnowledgeModel | [`SPEC-001`](specs/SPEC-001-text-to-knowledge-model.md) | [`DEBRIEF-001`](debriefs/DEBRIEF-001-text-to-knowledge-model.md) | Accepted |
| 002 — LLM Semantic Extraction | [`SPEC-002`](specs/SPEC-002-llm-semantic-extraction.md) | [`DEBRIEF-002`](debriefs/DEBRIEF-002-llm-semantic-extraction.md) | Accepted — mixed semantic outcome |
| 003 — Relationship Semantics | [`SPEC-003`](specs/SPEC-003-relationship-semantics.md) | [`DEBRIEF-003`](debriefs/DEBRIEF-003-relationship-semantics.md) | Accepted — improved semantic precision |
| 004 — Structure Detection | [`SPEC-004`](specs/SPEC-004-structure-detection.md) | [`DEBRIEF-004`](debriefs/DEBRIEF-004-structure-detection.md) | Accepted — useful deterministic composition with limitations |
| 005 — Minimal Representation | [`SPEC-005`](specs/SPEC-005-minimal-representation.md) | [`DEBRIEF-005`](debriefs/DEBRIEF-005-minimal-representation.md) | Accepted — strong positive human outcome |

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
- remaining semantic errors concentrate on endpoint selection, polarity, duplicates, and event/state distinctions more than missing predicates;
- further vocabulary expansion is not currently justified.

### After SPEC-004

- `KnowledgeModel` is not merely an interchange format; it can be deterministically composed into useful higher-order structures;
- hierarchies, causal paths, dependency chains, process chains, and feedback candidates can be detected without source re-reading or LLM calls;
- composition should remain semantically conservative: connectivity alone is not enough to justify transitivity;
- empty output can be correct output when the upstream graph lacks composable structure;
- downstream composition exposes upstream endpoint/state/chronology weaknesses clearly rather than hiding them;
- event/state modeling is now an evidence-backed concern, but not a blocker for a minimal representation experiment;
- exact duplicate semantic edges can be collapsed for traversal while preserving original relationship provenance;
- structurally valid does not necessarily mean pedagogically useful.

### After SPEC-005

- the first direct human evaluation strongly supports the core representation thesis: the interactive spatial model immediately improved the owner's cognitive orientation and was preferred as a learning aid;
- `RepresentationModel` can remain a thin deterministic downstream layer over `KnowledgeModel` + `DetectedStructureSet`;
- node and edge inspection turn the artifact from a static diagram into an explorable model;
- provenance is useful as part of the learner-facing interaction, not merely developer metadata;
- semantic correctness, spatial legibility, and interaction coherence are distinct dimensions of representation quality;
- the same semantic relationship may appear as graph edge, relationship control, detail, and evidence, so selection should synchronize those surfaces;
- layout is part of representation semantics: hierarchy, causal, dependency, process, and feedback structures should not necessarily share one generic placement strategy;
- rendering makes upstream event/state/endpoint defects more obvious but those defects do not yet block useful representation generally;
- the next important product question is whether structure-aware layout and synchronized interaction make the current representations behave more like coherent mental models.

## Active Decisions

```text
KnowledgeModel is the semantic IR.
Origin: DEBRIEF-001
Strengthened: DEBRIEF-002, DEBRIEF-004, DEBRIEF-005
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
Strengthened: DEBRIEF-003, DEBRIEF-004
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
Strengthened: DEBRIEF-004, DEBRIEF-005
Status: active

StructureDetector is a deterministic downstream layer consuming KnowledgeModel.
Origin: DEBRIEF-004
Status: active

DetectedStructureSet is the boundary between semantic graph and representation detection input.
Origin: DEBRIEF-004
Strengthened: DEBRIEF-005
Status: active

Empty or weak detected structures remain explicit; do not manufacture structure merely for presentation.
Origin: DEBRIEF-004
Strengthened: DEBRIEF-005
Status: active

RepresentationModel is a thin presentation-oriented layer downstream of KnowledgeModel + DetectedStructureSet.
Origin: DEBRIEF-005
Status: active

Learner-facing provenance remains first-class in representation interaction.
Origin: DEBRIEF-005
Status: active

Viewer selection should represent shared semantic state across graph, controls, details, and evidence.
Origin: DEBRIEF-005
Status: provisional-active

Structure-aware spatial layout is a representation concern, not generic cosmetic polish.
Origin: DEBRIEF-005
Status: provisional-active
```

## Why This Exists

Git history tells us **what changed**.

Specs tell us **what we intended to change**.

Debriefs tell us **what we learned from changing it**.

Together they provide enough context for a future human or AI collaborator to reconstruct the project’s reasoning even if the original conversation history is unavailable.
