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
RepresentationBuilder ← KnowledgeModel context/provenance
   ↓
RepresentationModel
   ↓
deterministic structure-aware layout metadata
   ↓
static local interactive viewer
```

The system transforms explanatory text into a validated, source-grounded semantic IR, deterministically composes that graph into higher-order structures, and renders those structures as interactive learner-facing representations with structure-aware spatial grammar and synchronized semantic selection.

## Semantic Intermediate Representation

`KnowledgeModel` remains the central semantic boundary. It contains source document, entities, claims, typed relationships, evidence spans, confidence, source-vs-inferred provenance, and metadata.

Presentation concerns remain downstream. SPEC-006 strengthened this separation by improving layout and interaction while holding semantic content fixed.

## Current Components

### Normalization
Converts plain text into a deterministic `SourceDocument` with stable identity and metadata.

### Extraction Boundary
`KnowledgeExtractor` is vendor-neutral. Current implementations are `FixtureExtractor` and `OpenAILLMExtractor`. Provider SDK concerns, prompting, model identifiers, and usage metadata remain isolated behind the extractor boundary.

### Relationship Semantics
`relationships.py` is the canonical provider-independent relationship grammar. Each active relationship defines semantic family, meaning, direction, source role, target role, appropriate usage, misuse/exclusion guidance, and symmetry.

Current semantic families:

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
The semantic model validates vocabularies, confidence bounds, identifiers, endpoints, evidence spans, exact quotes, and provenance. Validation remains fail-closed.

### Structure Detection
`StructureDetector` consumes `KnowledgeModel` only and deterministically detects:

```text
HIERARCHY
CAUSAL_PATH
PROCESS_CHAIN
DEPENDENCY_CHAIN
FEEDBACK_CANDIDATE
```

Composition remains deliberately conservative. Exact duplicate source/type/target relationships may collapse into logical traversal edges while preserving all supporting relationship IDs.

### Detected Structure Boundary
`DetectedStructureSet` is the boundary between semantic graph composition and representation input. It preserves participating entity IDs, supporting relationship IDs, predicate sequence, type, stable ID, and detection metadata.

### Representation Layer
`RepresentationBuilder` consumes `DetectedStructureSet` plus selected `KnowledgeModel` context and produces deterministic `RepresentationModel` artifacts.

Current mappings:

```text
HIERARCHY          → labeled directed DAG
CAUSAL_PATH        → merged branching causal model
DEPENDENCY_CHAIN   → directional dependency model
PROCESS_CHAIN      → explicit chronology
FEEDBACK_CANDIDATE → directed feedback candidate
```

The representation layer preserves canonical relationship labels/direction, entity context, source structure IDs, supporting relationship IDs, evidence excerpts, warnings, empty states, and deterministic salience.

It does not re-read source text, infer missing semantic relationships, call an LLM, or repair upstream defects.

### Representation Salience

```text
PRIMARY   → >= 3 edges, or multi-edge feedback candidate
SECONDARY → 2 edges
SPARSE    → 1 edge
```

This is presentation prioritization, not a truth or learning score.

### Structure-Aware Layout
SPEC-006 added deterministic presentation-only layout metadata.

Current spatial grammars:

```text
HIERARCHY          → top-down layered hierarchy
CAUSAL_PATH        → left-to-right layered causal graph
DEPENDENCY_CHAIN   → left-to-right layered dependency graph
PROCESS_CHAIN      → compact left-to-right chronological axis
FEEDBACK_CANDIDATE → explicit loop geometry
```

Layout assignment, ordering, routing, and geometry are deterministic. No random/force simulation is used.

Spatial orientation does not redefine semantic direction. Example: a hierarchy may place the whole above its parts while canonical `PART_OF` arrows still point part → whole.

A custom deterministic layout is sufficient for the current small benchmark graphs. A general graph-layout engine is not justified until graph scale/complexity produces contrary evidence.

### Interactive Viewer
The viewer is static HTML/CSS/JavaScript served locally through the Python standard library.

Viewer state separates persistent selection from temporary preview:

```text
CLICK = persistent selection
HOVER = temporary preview
```

One relationship identity synchronizes connector/arrow, label, relationship control, detail, and source evidence. Node selection follows the same single-object principle.

Domain/representation changes clear stale state. Canonical semantic direction is immutable from the viewer.

Keyboard interaction remains supported. SVG relationship hit paths use intentional `:focus-visible` styling rather than browser-default rectangular focus outlines.

### Baseline Interface
`baselines/BASELINE-001-interface.md` preserves the first empirically successful cognitive interaction baseline.

It is not a frozen visual design. It preserves the validated grammar:

```text
structure visible at a glance
+ structure-specific spatial grammar
+ persistent semantic selection
+ temporary hover preview
+ synchronized semantic identity across UI surfaces
+ immediate source provenance
+ truthful sparse / empty states
```

Future material UI/interaction changes should compare against this baseline.

### Evaluation
The five-domain benchmark supports probabilistic extraction evaluation, deterministic structure evaluation, representation-integrity evaluation, layout/interaction integrity checks, and direct human product review.

Fixed accepted upstream artifacts should continue to be used when a downstream experiment benefits from causal isolation.

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
RepresentationBuilder ← selected KnowledgeModel context
    ↓
RepresentationModel
    ↓
structure-aware layout + viewer interaction
    ↓
progressive disclosure / semantic navigation    future candidate
    ↓
simulator                                      future
```

## Architectural Principles

1. **Structure before presentation.** Establish semantic quality before visualization.
2. **Stable IR between source and representation.** `KnowledgeModel` remains the semantic boundary.
3. **Typed boundaries around probabilistic systems.** LLM output must cross validation before becoming project state.
4. **Evidence survives transformation.** Semantic, detected, represented, and interactive structures remain traceable to source material.
5. **Resolve deterministic facts deterministically.** Models nominate quotes; code computes coordinates.
6. **Fail closed on grounding ambiguity.** Do not weaken invariants to make extraction pass.
7. **Canonical semantics over duplicated prompt prose.** Relationship meanings live in one provider-independent registry.
8. **Explicit meaning and direction are part of the contract.** Enum names alone are insufficient.
9. **Prefer truthful claims over forced edges.** Graph density is subordinate to semantic correctness.
10. **Conservative ontology evolution.** Add predicates only when repeated evidence demonstrates a general gap.
11. **Compose semantics conservatively.** Connectivity alone does not justify hierarchy, causality, dependency, chronology, or transitivity.
12. **Use the least probabilistic layer that can solve the problem.** Once semantics are validated, deterministic algorithms are preferred downstream.
13. **Empty structure can be correct structure.** Do not manufacture patterns for presentation completeness.
14. **Presentation stays downstream.** Layout and viewer concerns must not leak into semantic truth models.
15. **Provenance is learner-facing.** Evidence inspection is part of understanding and trust.
16. **Semantic identity should survive UI duplication.** One relationship appearing in multiple surfaces behaves as one semantic object.
17. **Spatial layout carries semantics.** Geometry should expose hierarchy, direction, branching, chronology, and loops.
18. **Layout orientation and semantic direction are distinct.** Spatial clarity must not mutate source-grounded truth.
19. **Accessibility states should be intentional.** Remove browser-default visual noise only when an accessible designed state replaces it.
20. **Successful cognitive behavior deserves a baseline.** Future UI sophistication must demonstrate value against BASELINE-001.
21. **Vendor neutrality at the extraction boundary.** Provider choice must not redesign the semantic core.
22. **Architecture follows evidence.** Avoid abstractions for hypothetical future needs.

## Known Architectural Questions

- How should progressive disclosure deepen a model without losing orientation in the larger system?
- Should deeper navigation reuse the same semantic selection identity across overview and detail levels?
- How should selected nodes/relationships reveal related substructures without manufacturing unsupported connections?
- At what graph scale does the current custom layout stop being sufficient?
- How should endpoint selection preserve states, events, policies, and intermediate processes more faithfully?
- How should negative/prevention polarity be represented without predicate proliferation?
- Should entity, event, state/condition, and process be modeled more distinctly before richer process/feedback representations?
- How should feedback polarity eventually be represented?

## Known Compromises

- Only one real provider adapter exists.
- Prompt size remains materially larger after SPEC-003.
- Endpoint selection, polarity, chronology, and state/event errors remain upstream and become more obvious when rendered.
- Current layout targets small benchmark graphs.
- Crossing diagnostics are approximate rather than full curve/label collision analysis.
- Long labels may be truncated in-graph and require detail inspection.
- Current salience is coarse.
- Feedback candidates do not classify loop polarity.
- Human learning-value evidence is still primarily owner-based.

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

- **DEBRIEF-001** — established `KnowledgeModel` as semantic IR.
- **DEBRIEF-002** — validated real LLM extraction and deterministic evidence resolution; separated schema validity from semantic correctness.
- **DEBRIEF-003** — established canonical relationship contracts and semantic families.
- **DEBRIEF-004** — demonstrated deterministic higher-order structure detection.
- **DEBRIEF-005** — demonstrated the first strong positive human response to interactive representation and identified layout/selection as next constraints.
- **DEBRIEF-006** — validated structure-aware layout and synchronized semantic selection with a very strong before/after owner result; established BASELINE-001.
