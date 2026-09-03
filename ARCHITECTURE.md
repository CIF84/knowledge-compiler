# Architecture

## Purpose

This document describes the **current architecture** of Knowledge Compiler and the architectural beliefs currently supported by project evidence. It is not an aspirational design document.

## Current System Boundary

```text
plain text
   ↓
SourceDocument normalization
   ↓
KnowledgeExtractor boundary
   ├── FixtureExtractor
   └── OpenAILLMExtractor
           ↓
 canonical relationship grammar
           ↓
 provider structured output
           ↓
 exact-quote evidence resolution
           ↓
ExtractionResult
   ↓
conservative entity deduplication
   ↓
validated KnowledgeModel
   ↓
JSON / CLI / evaluation artifacts
```

The system transforms normalized explanatory text into a validated, source-grounded semantic intermediate representation. It supports deterministic fixture extraction and one real LLM provider adapter.

## Semantic Intermediate Representation

`KnowledgeModel` remains the central architectural boundary. It contains source document, entities, claims, typed relationships, evidence spans, confidence, source-vs-inferred provenance, and metadata.

Downstream structure detection, representation, visualization, interaction, and simulation must consume this model rather than reinterpret source text independently.

**Evidence:** DEBRIEF-001, DEBRIEF-002, DEBRIEF-003.

## Current Components

### Normalization

Converts plain text into a deterministic `SourceDocument` with stable identity and metadata.

### Extraction Boundary

`KnowledgeExtractor` is vendor-neutral. Current implementations are `FixtureExtractor` and `OpenAILLMExtractor`. Provider SDK concerns, prompting, model identifiers, and usage metadata remain isolated behind the extractor boundary.

### Relationship Semantics

`relationships.py` is now the canonical provider-independent relationship grammar.

Each active relationship defines:

- semantic family;
- meaning;
- direction;
- source role;
- target role;
- appropriate usage;
- misuse/exclusion guidance;
- symmetry.

Seven lightweight families currently exist:

```text
STRUCTURAL
CAUSAL
DEPENDENCY
TEMPORAL
INTERACTION
TRANSFORMATION
DESCRIPTIVE
```

The OpenAI adapter renders its relationship instructions from this registry. Prompt semantics and core relationship semantics therefore have one source of truth.

Current vocabulary contains 20 predicates. SPEC-003 added `AFFECTS`, `BINDS_TO`, and `TRANSFERS_TO`. Further expansion is frozen until new cross-domain evidence justifies it.

### Evidence Resolution

The LLM nominates exact source quotes; trusted deterministic code resolves those quotes to character coordinates and rejects missing or ambiguous matches.

### Validation

The semantic model validates enum vocabularies, confidence bounds, identifiers, relationship endpoints, source evidence spans, exact quotes, and provenance. Relationship-registry validation additionally ensures every active predicate has exactly one canonical definition.

Validation remains fail-closed. Deterministic code should not pretend to prove arbitrary semantic truth from entity names.

### Deduplication

Entity deduplication remains deliberately conservative. SPEC-003 exposed duplicate relationships as a separate remaining issue; do not broaden entity deduplication to solve it indirectly.

### Evaluation

The five-domain evaluation harness records machine output separately from human semantic review. SPEC-003 added regression metadata and direct comparison against the accepted SPEC-002 baseline.

## Dependency Direction

```text
provider SDK
    ↓
provider adapter / KnowledgeExtractor
    ↓
canonical relationship semantics
    ↓
semantic model / KnowledgeModel
    ↓
structure detection        future
    ↓
representation engine      future
    ↓
interaction / simulator    future
```

## Architectural Principles

1. **Structure before presentation.** Establish semantic quality before visualization.
2. **Stable IR between source and representation.** `KnowledgeModel` remains the semantic boundary.
3. **Typed boundaries around probabilistic systems.** LLM output must cross validation before becoming project state.
4. **Evidence survives transformation.** Semantic objects remain traceable to source material.
5. **Resolve deterministic facts deterministically.** Models nominate quotes; code computes coordinates.
6. **Fail closed on grounding ambiguity.** Do not weaken invariants to make extraction pass.
7. **Canonical semantics over duplicated prompt prose.** Relationship meanings live in one provider-independent registry.
8. **Explicit meaning and direction are part of the contract.** Enum names alone are insufficient.
9. **Prefer truthful claims over forced edges.** Graph density is subordinate to semantic correctness.
10. **Conservative ontology evolution.** Add predicates only when repeated evidence demonstrates a general gap.
11. **Vendor neutrality at the extraction boundary.** Provider choice must not redesign the semantic core.
12. **Architecture follows evidence.** Avoid abstractions for hypothetical future needs.

## Known Architectural Questions

- Can the current graph be composed into useful hierarchies, causal paths, temporal/process chains, dependencies, and feedback candidates without re-reading source text?
- How should endpoint selection preserve policies, regulations, states, events, or intermediate processes instead of substituting nearby entities?
- How should negative/prevention polarity be represented without predicate proliferation?
- How should semantically duplicate relationships be suppressed conservatively?
- Should entity, event, state/condition, and process be modeled more distinctly?
- Is remaining `MEASURED_BY` misuse a predicate problem or primarily an entity-modeling problem?
- How should inferred relationships retain supporting evidence if a concrete use case eventually requires it?
- How should progressive disclosure map onto detected structures?

## Known Compromises

- Only one real provider adapter exists; vendor neutrality is architecturally preserved but not multi-provider-proven.
- Prompt size grew materially in SPEC-003 because the full relationship grammar is supplied on each extraction.
- Some endpoint selection, polarity, chronology, and duplicate-edge errors remain.
- State/event distinctions are still weak in some domains.
- `INFERRED` evidence remains intentionally strict.
- Human semantic review remains necessary.

## Change Protocol

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

## Evidence Index

- **DEBRIEF-001** — established `KnowledgeModel` as semantic IR and deterministic semantic validation workflow.
- **DEBRIEF-002** — validated the IR with a real LLM across five domains; established deterministic quote-to-span resolution and the distinction between schema validity and semantic correctness.
- **DEBRIEF-003** — established canonical relationship contracts and semantic families; showed material cross-domain precision improvement with only three new general predicates; shifted the main remaining failures toward endpoints, polarity, duplicate edges, and event/state modeling.
