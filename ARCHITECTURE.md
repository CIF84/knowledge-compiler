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
static local interactive viewer
```

The system now transforms explanatory text into a validated, source-grounded semantic IR, deterministically composes that graph into higher-order structural candidates, and renders those structures as interactive learner-facing representations.

## Semantic Intermediate Representation

`KnowledgeModel` remains the central semantic boundary. It contains source document, entities, claims, typed relationships, evidence spans, confidence, source-vs-inferred provenance, and metadata.

SPEC-004 demonstrated that the IR supports deterministic higher-order composition. SPEC-005 further demonstrated that the same IR can supply learner-facing descriptions, relationship semantics, and provenance to a separate representation layer without presentation concerns leaking backward.

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

`DetectedStructureSet` is the boundary between semantic graph composition and representation input.

Each detected structure preserves participating entity IDs, supporting relationship IDs, predicate sequence, type, stable ID, and detection metadata.

SPEC-005 provides positive evidence that this boundary is sufficient for the current representation experiment when paired with selected `KnowledgeModel` context/provenance.

### Representation Layer

`RepresentationBuilder` consumes `DetectedStructureSet` plus `KnowledgeModel` context and produces a deterministic presentation-oriented `RepresentationModel`.

Current mappings are:

```text
HIERARCHY          → labeled directed DAG
CAUSAL_PATH        → merged branching causal model
DEPENDENCY_CHAIN   → directional dependency model
PROCESS_CHAIN      → explicit chronology
FEEDBACK_CANDIDATE → directed feedback candidate
```

The representation layer preserves canonical relationship labels/direction, entity context, source structure IDs, supporting relationship IDs, evidence excerpts, warnings, empty states, and simple deterministic salience.

It does not re-read or reinterpret source text, infer missing relationships, call an LLM, or repair upstream semantic defects.

### Representation Salience

Current salience is intentionally simple and explainable:

```text
PRIMARY   → >= 3 edges, or multi-edge feedback candidate
SECONDARY → 2 edges
SPARSE    → 1 edge
```

This is presentation prioritization, not a truth or learning score.

### Interactive Viewer

The current viewer is static HTML/CSS/JavaScript served locally through the Python standard library.

It supports domain and representation selection, directed diagrams, node inspection, relationship inspection, canonical semantic definitions, warnings, and source evidence.

The first owner evaluation strongly supports interactive representation as a useful learning surface.

The next architectural question inside the viewer is how to unify semantic selection state across graph edges/nodes, relationship controls, detail, and evidence surfaces.

### Evaluation

The five-domain benchmark supports probabilistic extraction evaluation, deterministic structure evaluation, deterministic representation-integrity evaluation, and now direct human product review.

SPEC-005 used accepted upstream artifacts as fixed inputs, separating representation usefulness from LLM variance.

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
viewer interaction
    ↓
progressive disclosure / simulator    future
```

## Architectural Principles

1. **Structure before presentation.** Establish semantic quality before visualization.
2. **Stable IR between source and representation.** `KnowledgeModel` remains the semantic boundary.
3. **Typed boundaries around probabilistic systems.** LLM output must cross validation before becoming project state.
4. **Evidence survives transformation.** Semantic, detected, and represented structures remain traceable to source material.
5. **Resolve deterministic facts deterministically.** Models nominate quotes; code computes coordinates.
6. **Fail closed on grounding ambiguity.** Do not weaken invariants to make extraction pass.
7. **Canonical semantics over duplicated prompt prose.** Relationship meanings live in one provider-independent registry.
8. **Explicit meaning and direction are part of the contract.** Enum names alone are insufficient.
9. **Prefer truthful claims over forced edges.** Graph density is subordinate to semantic correctness.
10. **Conservative ontology evolution.** Add predicates only when repeated evidence demonstrates a general gap.
11. **Compose semantics conservatively.** Graph connectivity alone does not justify hierarchy, causality, dependency, chronology, or transitivity.
12. **Use the least probabilistic layer that can solve the problem.** Once semantics are validated, deterministic algorithms are preferred for composition and representation.
13. **Empty structure can be correct structure.** Do not manufacture higher-order patterns for presentation completeness.
14. **Presentation stays downstream.** Representation and viewer concerns must not leak into semantic truth models.
15. **Provenance is learner-facing.** Evidence inspection is part of understanding and trust, not merely debugging metadata.
16. **Semantic identity should survive UI duplication.** If one relationship appears in multiple surfaces, those surfaces should behave as one selected semantic object.
17. **Spatial layout carries semantics.** Geometry should expose hierarchy, direction, branching, chronology, and loops rather than merely avoid overlap.
18. **Vendor neutrality at the extraction boundary.** Provider choice must not redesign the semantic core.
19. **Architecture follows evidence.** Avoid abstractions for hypothetical future needs.

## Known Architectural Questions

- What minimal shared selection-state model should synchronize graph, controls, detail, and evidence?
- Which deterministic spatial grammar best fits each current structure type?
- Can structure-aware layout remain simple, or is a focused graph-layout dependency justified?
- How should branching/converging causal structures minimize crossings while preserving direction?
- How should feedback candidates be spatially represented without unsupported polarity claims?
- How should endpoint selection preserve policies, regulations, states, events, or intermediate processes instead of substituting nearby entities?
- How should negative/prevention polarity be represented without predicate proliferation?
- Should entity, event, state/condition, and process be modeled more distinctly before richer process/feedback representations?
- When should progressive disclosure move beyond the current node/edge detail interaction into nested/deeper models?
- How should representation behavior scale beyond the small benchmark graphs?

## Known Compromises

- Only one real provider adapter exists; vendor neutrality is architecturally preserved but not multi-provider-proven.
- Prompt size remains materially larger after SPEC-003.
- Some endpoint selection, polarity, chronology, and state/event errors remain upstream and become more obvious when rendered.
- Current graph placement is intentionally simple and is not yet structure-aware enough for strong spatial harmony.
- Viewer selection is not yet fully synchronized across all surfaces of the same semantic relationship.
- Current salience is coarse and has only been tested on small benchmark structures.
- Feedback candidates currently do not classify loop polarity.
- Human semantic and learning-value review remains necessary.
- The positive learning-usefulness result is from the project owner, not a broader user study.

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
- **DEBRIEF-005** — demonstrated the first strongly positive human response to an interactive representation, established `RepresentationModel` as a thin downstream layer, and identified synchronized semantic selection plus structure-aware spatial layout as the next representation constraints.
