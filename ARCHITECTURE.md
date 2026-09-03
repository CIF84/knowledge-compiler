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
   ├── FixtureExtractor
   └── OpenAILLMExtractor
           │
           ▼
    provider structured output
           │
           ▼
 exact-quote evidence resolution
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
JSON / CLI / evaluation artifacts
```

The implemented system currently transforms normalized explanatory text plus semantic extraction into a validated, source-grounded semantic intermediate representation. It now supports both deterministic fixture extraction and one real LLM provider adapter.

## Semantic Intermediate Representation

`KnowledgeModel` remains the central architectural boundary.

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

**Evidence:** DEBRIEF-001, strengthened by DEBRIEF-002.

## Current Components

### Normalization

Converts plain text into a deterministic `SourceDocument` with stable identity and metadata.

### Extraction Boundary

`KnowledgeExtractor` is vendor-neutral.

Current implementations:

```text
FixtureExtractor      deterministic/offline
OpenAILLMExtractor    real structured-output LLM adapter
```

Provider-specific request objects, SDK concerns, prompting, model identifiers, and usage metadata remain isolated behind the extractor boundary.

### Evidence Resolution

For real LLM extraction, the model nominates exact source quotes. Trusted deterministic code resolves those quotes to character coordinates and rejects missing or ambiguous matches.

```text
LLM quote
   ↓
unique deterministic lookup
   ↓
SourceSpan
   ↓
normal domain validation
```

This is now the preferred architecture for evidence coordinates. Do not trust model-generated character offsets when deterministic resolution is available.

### Validation

The semantic model enforces important invariants including valid enum vocabularies, confidence bounds, unique identifiers, valid relationship endpoints, valid source evidence spans, exact evidence quotes, and explicit provenance.

SPEC-002 demonstrated that these invariants catch real LLM failures. Validation remains fail-closed; probabilistic extraction problems should not be repaired by silently weakening domain contracts.

### Deduplication

Entity deduplication remains deliberately conservative. Case-normalized names and explicit aliases may establish equivalence; semantic similarity alone does not.

### Evaluation

A repeatable five-domain evaluation harness now exists. Machine-run output and human semantic review are stored separately so that raw experimental artifacts remain distinguishable from later interpretation.

### CLI / Serialization

The CLI supports fixture and LLM extraction plus multi-domain evaluation. Successful extraction emits the same provider-independent `KnowledgeModel` JSON format.

## Dependency Direction

```text
provider SDK
    │
    ▼
provider adapter / KnowledgeExtractor
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

- extractors may depend on semantic contracts;
- provider SDK types must not leak into the semantic core;
- the semantic model must not depend on visualization libraries;
- future visualization must not independently parse source text;
- evidence provenance must survive downstream transformations;
- inferred knowledge must remain distinguishable from explicitly source-derived knowledge;
- schema validity must not be treated as semantic correctness;
- relationship direction and meaning require explicit semantic discipline.

## Architectural Principles

1. **Structure before presentation.** Semantic quality is established before visualization.
2. **Stable IR between source and representation.** `KnowledgeModel` isolates source/extraction concerns from downstream learning representations.
3. **Typed boundaries around probabilistic systems.** LLM output must cross validation before becoming project state.
4. **Evidence survives transformation.** Important semantic objects remain traceable to source material.
5. **Resolve deterministic facts deterministically.** The LLM may nominate source quotes; code computes exact coordinates.
6. **Fail closed on grounding ambiguity.** Missing or ambiguous evidence is a failed extraction, not an invitation to loosen validation.
7. **Conservative semantics over clever inference.** Unsupported equivalence and causality are more damaging than incomplete graphs.
8. **Vendor neutrality at the extraction boundary.** Provider choice should be replaceable without redesigning the semantic core.
9. **Semantic validity is distinct from structural validity.** Typed JSON can still encode wrong meaning.
10. **Architecture follows evidence.** Do not add abstractions for hypothetical future requirements.

## Known Architectural Questions

These remain unresolved and should be answered experimentally rather than assumed:

- What is the smallest relationship grammar that works across mechanistic, software, economic, biological, and historical domains?
- Should relationship types carry explicit semantic contracts for directionality and valid source/target roles?
- Should entity, state/condition, process, and event be modeled more distinctly?
- How should claims and graph edges divide responsibility when a proposition could be represented either way?
- How should inferred relationships retain supporting evidence without presenting inference as explicit source content?
- What structures can be reliably detected from combinations of semantic edges?
- How should progressive disclosure map onto the IR?
- When does persistence become necessary?
- What information must survive chunked extraction for long sources?

## Known Compromises

- Only one real provider adapter exists; provider neutrality is architectural rather than multi-provider-proven.
- The relationship vocabulary works unevenly across domains and currently encourages some semantic distortion.
- The current model does not cleanly represent state distinctions such as "changing electric field" versus the base field entity.
- `INFERRED` evidence remains strict: inferred claims/relationships cannot carry source evidence. A separate supporting-evidence concept remains only a possible future need.
- Human semantic review is still required to distinguish valid structure from incorrect edge meaning.

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
- **DEBRIEF-002** — validated the IR and extractor boundary with a real LLM across five domains; established deterministic quote-to-span resolution; demonstrated that structural/schema validity is insufficient without semantic relationship evaluation.
