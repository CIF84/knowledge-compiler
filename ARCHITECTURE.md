# Architecture

## Purpose

This document describes the **current architecture** of Knowledge Compiler and the architectural beliefs currently supported by project evidence.

It is not an aspirational design document. Future architecture belongs in a SPEC until implementation and review provide evidence that it should become part of this baseline.

Architectural decisions should remain traceable to the SPEC/DEBRIEF cycle that established or changed them.

## Current System Boundary

```text
plain text
   │
   ▼
SourceDocument normalization
   │
   ▼
KnowledgeExtractor boundary
   │
   ▼
ExtractionResult
   │
   ▼
conservative entity deduplication
   │
   ▼
validated KnowledgeModel
   │
   ▼
JSON / CLI
```

The implemented system currently solves one problem: transform normalized explanatory text plus semantic extraction into a validated, source-grounded semantic intermediate representation.

## Semantic Intermediate Representation

`KnowledgeModel` is the central architectural boundary.

It contains:

- source document
- entities
- claims
- typed relationships
- evidence spans
- confidence
- source-vs-inferred provenance
- metadata

Downstream representation, visualization, structure detection, interaction, and simulation should consume this model rather than parse source material independently.

**Evidence:** DEBRIEF-001.

## Current Components

### Normalization

Converts plain text into a deterministic `SourceDocument` with stable identity and metadata.

### Extraction Boundary

`KnowledgeExtractor` is vendor-neutral. Semantic extraction implementations produce an `ExtractionResult`; downstream code should not depend on a particular LLM vendor or API.

### Validation

The semantic model enforces important invariants including valid enum vocabularies, confidence bounds, unique identifiers, valid relationship endpoints, valid source evidence spans, exact evidence quotes, and explicit provenance.

### Deduplication

Entity deduplication is deliberately conservative. Case-normalized names and explicit aliases may establish equivalence; semantic similarity alone does not.

### CLI / Serialization

The current interface emits inspectable JSON. Visualization is intentionally deferred until semantic extraction quality is demonstrated.

## Dependency Direction

```text
source adapters / extractors
          │
          ▼
    semantic model
          │
          ▼
structure detection        future
          │
          ▼
representation engine      future
          │
          ▼
interaction / simulator    future
```

Important constraints:

- extractors may depend on the semantic contracts
- the semantic model must not depend on LLM vendors
- the semantic model must not depend on visualization libraries
- future visualization must not independently parse source text
- evidence provenance must survive downstream transformations
- inferred knowledge must remain distinguishable from explicitly source-derived knowledge

## Architectural Principles

1. **Structure before presentation.** Semantic quality is established before visualization.
2. **Stable IR between source and representation.** `KnowledgeModel` isolates source/extraction concerns from downstream learning representations.
3. **Typed boundaries around probabilistic systems.** LLM output must cross validation before becoming project state.
4. **Evidence survives transformation.** Important semantic objects remain traceable to source material.
5. **Conservative semantics over clever inference.** Unsupported equivalence and causality are more damaging than incomplete graphs.
6. **Vendor neutrality at the extraction boundary.** Provider choice should be replaceable without redesigning the semantic core.
7. **Architecture follows evidence.** Do not add abstractions for hypothetical future requirements.

## Known Architectural Questions

These remain unresolved and should be answered experimentally rather than assumed:

- Can real LLM extraction reliably produce the current IR across unrelated domains?
- Is the current relationship vocabulary sufficiently general?
- How should inferred relationships retain supporting evidence without presenting inference as explicit source content?
- What structures can be reliably detected from combinations of semantic edges?
- How should progressive disclosure map onto the IR?
- When does persistence become necessary?
- What information must survive chunked extraction for long sources?

## Known Compromises

- The current deterministic fixture extractor is an experimental adapter, not a production extraction mechanism.
- The CLI default fixture path is repository-oriented and may not survive installed-wheel packaging; this is non-blocking for SPEC-001 and should be corrected when the CLI is next changed.
- The current model treats `INFERRED` evidence strictly: inferred claims/relationships cannot present source evidence. This may later need a distinct concept of supporting evidence.

## Change Protocol

Architecture changes should normally follow:

```text
architectural question
        ↓
      SPEC
        ↓
 implementation
        ↓
     review
        ↓
     DEBRIEF
        ↓
ARCHITECTURE.md update if evidence changed the current model
```

Do not update this file merely because a future architecture was discussed.

## Evidence Index

- **DEBRIEF-001** — established `KnowledgeModel` as semantic IR; validated source grounding, conservative deduplication, vendor-neutral extraction boundary, and deterministic golden-model workflow.
