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
StructureDetector
   ↓
DetectedStructureSet
   ↓
JSON / CLI / evaluation artifacts
```

The system transforms explanatory text into a validated, source-grounded semantic IR and can now deterministically compose that graph into higher-order structural candidates.

## Semantic Intermediate Representation

`KnowledgeModel` remains the central semantic boundary. It contains source document, entities, claims, typed relationships, evidence spans, confidence, source-vs-inferred provenance, and metadata.

SPEC-004 materially strengthens this decision: the IR is rich enough to support deterministic higher-order composition without re-reading source text.

## Current Components

### Normalization

Converts plain text into a deterministic `SourceDocument` with stable identity and metadata.

### Extraction Boundary

`KnowledgeExtractor` is vendor-neutral. Current implementations are `FixtureExtractor` and `OpenAILLMExtractor`. Provider SDK concerns, prompting, model identifiers, and usage metadata remain isolated behind the extractor boundary.

### Relationship Semantics

`relationships.py` is the canonical provider-independent relationship grammar.

Each active relationship defines semantic family, meaning, direction, source role, target role, appropriate usage, misuse/exclusion guidance, and symmetry.

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

Current vocabulary contains 20 predicates. Further expansion remains frozen until new cross-domain evidence justifies it.

### Evidence Resolution

The LLM nominates exact source quotes; trusted deterministic code resolves those quotes to character coordinates and rejects missing or ambiguous matches.

### Validation

The semantic model validates enum vocabularies, confidence bounds, identifiers, relationship endpoints, source evidence spans, exact quotes, and provenance. Relationship-registry validation ensures every active predicate has exactly one canonical definition.

Validation remains fail-closed. Deterministic code should not pretend to prove arbitrary semantic truth from entity names.

### Structure Detection

`StructureDetector` is a deterministic downstream layer that consumes `KnowledgeModel` only.

Current detected structures are:

```text
HIERARCHY
CAUSAL_PATH
PROCESS_CHAIN
DEPENDENCY_CHAIN
FEEDBACK_CANDIDATE
```

The detector derives composition rules from semantic relationship types/families and remains deliberately conservative:

- structural predicates are grouped without indiscriminate mixing;
- causal-family edges may form causal paths and feedback candidates;
- process chains require explicit `PRECEDES` edges;
- dependency chains are predicate-specific rather than treating all dependency relations as safely transitive;
- interaction and descriptive relationships are not promoted into generic higher-order paths;
- transformation is not treated as chronology without temporal evidence.

Exact duplicate source/type/target relationships are collapsed into logical traversal edges while preserving all supporting relationship IDs.

Detected structure IDs and ordering are deterministic.

### Detected Structure Boundary

`DetectedStructureSet` is the provisional boundary between semantic graph and future representation.

Each detected structure preserves the participating entity IDs, supporting relationship IDs, predicate sequence, type, stable ID, and detection metadata.

This boundary must remain traceable back through `KnowledgeModel` relationships to source evidence.

### Evaluation

The five-domain benchmark now supports both probabilistic extraction evaluation and fully offline structure evaluation. SPEC-004 used accepted SPEC-003 models as fixed inputs, allowing the structure layer to be evaluated independently of LLM variance.

## Dependency Direction

```text
provider SDK
    ↓
provider adapter / KnowledgeExtractor
    ↓
canonical relationship semantics
    ↓
KnowledgeModel
    ↓
StructureDetector
    ↓
DetectedStructureSet
    ↓
representation engine      future
    ↓
interaction / simulator    future
```

## Architectural Principles

1. **Structure before presentation.** Establish semantic quality before visualization.
2. **Stable IR between source and representation.** `KnowledgeModel` remains the semantic boundary.
3. **Typed boundaries around probabilistic systems.** LLM output must cross validation before becoming project state.
4. **Evidence survives transformation.** Semantic and detected structures remain traceable to source material.
5. **Resolve deterministic facts deterministically.** Models nominate quotes; code computes coordinates.
6. **Fail closed on grounding ambiguity.** Do not weaken invariants to make extraction pass.
7. **Canonical semantics over duplicated prompt prose.** Relationship meanings live in one provider-independent registry.
8. **Explicit meaning and direction are part of the contract.** Enum names alone are insufficient.
9. **Prefer truthful claims over forced edges.** Graph density is subordinate to semantic correctness.
10. **Conservative ontology evolution.** Add predicates only when repeated evidence demonstrates a general gap.
11. **Compose semantics conservatively.** Graph connectivity alone does not justify hierarchy, causality, dependency, chronology, or transitivity.
12. **Use the least probabilistic layer that can solve the problem.** Once semantics are validated, deterministic graph algorithms are preferred for composition.
13. **Empty structure can be correct structure.** Do not manufacture higher-order patterns for presentation completeness.
14. **Vendor neutrality at the extraction boundary.** Provider choice must not redesign the semantic core.
15. **Architecture follows evidence.** Avoid abstractions for hypothetical future needs.

## Known Architectural Questions

- What minimal representation best exposes each detected structure type?
- How should representation rank or suppress structurally valid but pedagogically weak structures?
- Should representation consume only `DetectedStructureSet` or also selected claims/entities from `KnowledgeModel`?
- How should structure → relationship → evidence provenance be exposed interactively?
- How should endpoint selection preserve policies, regulations, states, events, or intermediate processes instead of substituting nearby entities?
- How should negative/prevention polarity be represented without predicate proliferation?
- Should entity, event, state/condition, and process be modeled more distinctly before richer process/feedback representations?
- How should progressive disclosure map onto detected structures?

## Known Compromises

- Only one real provider adapter exists; vendor neutrality is architecturally preserved but not multi-provider-proven.
- Prompt size remains materially larger after SPEC-003.
- Some endpoint selection, polarity, chronology, and state/event errors remain upstream.
- `DetectedStructureSet` is proven sufficient only for a minimal representation experiment, not yet as a permanent public API.
- Some detected structures are technically correct but pedagogically weak.
- Feedback candidates currently do not classify loop polarity.
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
- **DEBRIEF-003** — established canonical relationship contracts and semantic families; showed material cross-domain precision improvement with only three new general predicates.
- **DEBRIEF-004** — demonstrated deterministic higher-order structure detection from `KnowledgeModel`, established `StructureDetector` / `DetectedStructureSet`, and showed that remaining process/feedback weaknesses are predominantly inherited from upstream endpoint/state semantics rather than detector logic.
