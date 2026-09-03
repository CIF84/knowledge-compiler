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

EXPERIMENTAL SEMANTIC-DEPTH PATH

parent KnowledgeModel + focus concept
   ↓
ResolutionCompiler
   ↓
provider nomination from permitted source
   ↓
exact quote → SourceSpan resolution
   ↓
validated child KnowledgeModel
   ↓
StructureDetector
   ↓
RepresentationBuilder
   ↓
deterministic layout
   ↓
generated contextual exploration artifact
```

The system now has evidence for both a stable single-resolution semantic pipeline and one bounded automatic parent → child semantic-resolution compilation success.

## Semantic Intermediate Representation

`KnowledgeModel` remains the central semantic boundary. It contains source document, entities, claims, typed relationships, evidence spans, confidence, source-vs-inferred provenance, and metadata.

SPEC-008 preserves this boundary by keeping parent and child semantic truth independently serializable and inspectable. The parent model remains immutable. Navigation state remains outside semantic IR.

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

SPEC-008 reuses the same pattern for child-resolution generation.

### Validation
The semantic model validates vocabularies, confidence bounds, identifiers, endpoints, evidence spans, exact quotes, and provenance. Validation remains fail-closed.

SPEC-008 strengthened this principle: Software Architecture child generation was rejected because an `INFERRED` claim carried source evidence. The system did not repair or relax the trust contract.

### Structure Detection
`StructureDetector` consumes `KnowledgeModel` only and deterministically detects:

```text
HIERARCHY
CAUSAL_PATH
PROCESS_CHAIN
DEPENDENCY_CHAIN
FEEDBACK_CANDIDATE
```

Composition remains deliberately conservative.

### Detected Structure Boundary
`DetectedStructureSet` remains the boundary between semantic graph composition and representation input.

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

The representation layer preserves canonical direction, source structure IDs, provenance, warnings, empty states, and deterministic salience.

### Structure-Aware Layout
Current spatial grammars:

```text
HIERARCHY          → top-down layered hierarchy
CAUSAL_PATH        → left-to-right layered causal graph
DEPENDENCY_CHAIN   → left-to-right layered dependency graph
PROCESS_CHAIN      → compact left-to-right chronological axis
FEEDBACK_CANDIDATE → explicit loop geometry
```

Layout is deterministic and non-random.

### Interactive Viewer
Viewer state separates persistent selection from temporary preview:

```text
CLICK = persistent selection
HOVER = temporary preview
```

One relationship identity synchronizes connector/arrow, label/control, detail, and source evidence.

SPEC-007 adds a distinct semantic interaction:

```text
SELECT
→ inspect semantic object

EXPLORE
→ increase semantic resolution
```

### Cognitive Presets
SPEC-007 established a product-level distinction between one trusted semantic model and multiple cognitive projections.

Current working intents:

```text
Overview
→ landscape / system at a glance

Focus
→ isolate one mechanism

Contextual / Layers
→ peel semantic layers while preserving orientation
```

These are projections over shared semantic truth, not separate truth models.

### ResolutionCompiler
SPEC-008 adds an experimental bounded semantic-depth compiler.

Current constraints:

- parent `KnowledgeModel` immutable;
- child truth independently serializable;
- maximum generated depth = 1;
- provider nomination uses permitted source only;
- exact evidence coordinates resolved deterministically;
- canonical relationship grammar reused unchanged;
- no automatic retry/cherry-picking requirement in the experiment;
- child goes through existing deterministic downstream structure/representation/layout machinery;
- navigation remains outside semantic IR.

One live Economics generation succeeded end-to-end. One Software Architecture generation failed closed at grounding validation.

### Semantic Resolution
SPEC-008 establishes an important working definition:

> Semantic resolution is explanatory refinement, not universal decomposition.

Likely forms differ by semantic role:

```text
SYSTEM
→ subsystems + interactions

COMPONENT / OBJECT
→ internal components

PROCESS
→ internal stages

VARIABLE
→ causal drivers + consequences

EVENT
→ antecedents + outcomes

CONCEPT
→ mechanisms + principles + relationships
```

This mapping is not yet a finalized ontology or algorithm. It is the next experimental frontier.

### Knowledge-Space Navigation
The emerging default model for abstract knowledge is:

```text
vertical dimension
→ abstraction / semantic resolution

horizontal dimension
→ conceptual neighborhood / topology
```

Default representation should remain **2D + semantic zoom**. Literal 3D should be reserved for subjects where physical/spatial third-dimensional structure itself carries explanatory information.

Navigation concepts remain distinct:

```text
Back
→ history

Breadcrumb / ancestry path
→ lineage across abstraction

Context map
→ neighborhood / lateral movement

Explore / semantic zoom
→ deeper resolution
```

Active context-map navigation is not yet implemented.

### Baseline Interface
`baselines/BASELINE-001-interface.md` preserves the first empirically successful cognitive interaction baseline.

Future material UI/interaction changes should compare against this baseline rather than assume novelty is improvement.

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
RepresentationBuilder
    ↓
RepresentationModel
    ↓
structure-aware layout + viewer interaction

AND, EXPERIMENTALLY:

parent KnowledgeModel + focus
    ↓
ResolutionCompiler
    ↓
child KnowledgeModel
    ↓
existing deterministic downstream stack
    ↓
Contextual / Layers navigation
```

## Architectural Principles

1. **Structure before presentation.** Establish semantic quality before visualization.
2. **Stable IR between source and representation.** `KnowledgeModel` remains the semantic truth boundary.
3. **Typed boundaries around probabilistic systems.** LLM output must cross validation before becoming project state.
4. **Evidence survives transformation.** Parent and child semantic truth remain traceable to source material.
5. **Resolve deterministic facts deterministically.** Models nominate quotes; code computes coordinates.
6. **Fail closed on grounding/provenance ambiguity.** Do not weaken invariants to make generation pass.
7. **Canonical semantics over duplicated prompt prose.** Relationship meanings live in one provider-independent registry.
8. **Prefer truthful claims over forced edges.** Graph density is subordinate to semantic correctness.
9. **Conservative ontology evolution.** Add predicates only when repeated evidence demonstrates a general gap.
10. **Compose semantics conservatively.** Connectivity alone does not justify higher-order meaning.
11. **Use the least probabilistic layer that can solve the problem.** Once semantics are validated, deterministic algorithms are preferred downstream.
12. **Empty/failure output can be correct.** Do not manufacture depth when trust checks fail.
13. **Presentation stays downstream.** Layout, cognitive preset, and viewer state must not mutate semantic truth.
14. **Provenance is learner-facing.** Evidence inspection is part of understanding and trust.
15. **Semantic identity survives UI duplication.** One relationship behaves as one semantic object across surfaces.
16. **Spatial layout carries semantics.** Geometry should expose hierarchy, direction, branching, chronology, and loops.
17. **Selection and exploration are distinct.** Inspecting an object is not the same as changing semantic resolution.
18. **Cognitive projection is separate from semantic truth.** Different presets may show the same knowledge differently without changing canonical facts.
19. **Semantic zoom is explanatory refinement.** Do not assume every concept decomposes into contained parts.
20. **2D + semantic zoom is the default abstract knowledge surface.** Use literal 3D only where the subject's spatial third dimension matters.
21. **Do not recurse before resolution semantics are understood.** Maximum generated depth remains bounded for now.
22. **Successful cognitive behavior deserves a baseline.** Future UI sophistication must demonstrate value against BASELINE-001.
23. **Architecture follows evidence.** Avoid abstractions for hypothetical future needs.

## Known Architectural Questions

- What should “zoom in” mean for different semantic object types?
- Can a small set of resolution strategies generalize across domains without a large brittle ontology?
- How should a child model prove a compression/coherence relationship with its parent focus?
- When should source insufficiency stop generation rather than trigger retrieval?
- How should active context-map navigation move laterally across concepts while preserving abstraction level?
- Should deeper resolutions be compiled on demand and cached rather than eagerly precomputed?
- At what graph scale does the current custom layout stop being sufficient?
- How should endpoint/state/polarity limitations be improved when they become hard blockers?

## Known Compromises

- Only one real provider adapter exists.
- Automatic multi-resolution generation has one real success and one grounding rejection; cross-domain reliability is unproven.
- Resolution strategy is still generic rather than explicitly semantic-role aware.
- Maximum generated depth is one.
- No active context-map navigation exists yet.
- Current layout targets small benchmark graphs.
- Human learning-value evidence is still primarily owner-based.
- Endpoint selection, polarity, chronology, and state/event errors remain upstream.

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
- **DEBRIEF-002** — validated real LLM extraction and deterministic evidence resolution.
- **DEBRIEF-003** — established canonical relationship contracts and semantic families.
- **DEBRIEF-004** — demonstrated deterministic higher-order structure detection.
- **DEBRIEF-005** — demonstrated the first strong positive human response to interactive representation.
- **DEBRIEF-006** — validated structure-aware layout and synchronized semantic selection; established BASELINE-001.
- **DEBRIEF-007** — validated contextual semantic navigation / peeling layers and introduced the cognitive-preset concept.
- **DEBRIEF-008** — demonstrated one real automatic source-grounded child resolution, one correct fail-closed rejection, and established semantic-resolution strategy as the next major question.
