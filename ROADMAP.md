# Knowledge Compiler — Roadmap

This roadmap is organized around **risk reduction**, not feature accumulation.

The biggest unknown is not whether an LLM can draw a graph. It is whether a general translation grammar can consistently turn difficult source material into representations that improve human understanding.

## North Star

> **Paste difficult text. Get a model you can think with.**

Before expanding input formats or product surface area, prove that transformation quality is genuinely useful.

# Phase 0 — Define the Experiment

## Goal

Turn the thesis into something testable before building significant infrastructure.

## Tasks

- [ ] Define the first `KnowledgeModel` schema.
- [ ] Define the initial relationship vocabulary.
- [ ] Define confidence / uncertainty fields.
- [ ] Define evidence references back to source spans.
- [ ] Create five golden test cases.
- [ ] Establish qualitative evaluation criteria.

## Golden Domains

1. Electromagnetism — physical / causal system
2. Software architecture — abstract technical system
3. Economics — probabilistic causal system with feedback
4. Biology — hierarchical + mechanistic system
5. History — temporal + causal narrative

## Evaluation Questions

- Can the major system components be identified quickly?
- Are important relationships represented correctly?
- Does the representation expose relationships obscured by prose?
- Is the abstraction level appropriate?
- Are causal claims distinguished from association?
- Can important generated claims be traced to evidence?
- Does the model omit important structure?
- Does it invent unsupported structure?
- Does it improve understanding versus a conventional summary?

# Phase 1 — Text → Structured Knowledge

## Goal

Build the semantic core without worrying about visualization.

```text
Text
 ↓
LLM / extractor
 ↓
validated schema
 ↓
KnowledgeModel
```

## Tasks

- [ ] Accept plain text.
- [ ] Normalize into a `SourceDocument`.
- [ ] Preserve source locations.
- [ ] Extract entities / concepts.
- [ ] Extract claims.
- [ ] Extract typed relationships.
- [ ] Attach evidence spans.
- [ ] Add confidence / origin metadata.
- [ ] Validate structured output.
- [ ] Merge conservative duplicate entities.
- [ ] Serialize the resulting model.
- [ ] Add automated tests.

## Exit Criterion

Given the electromagnetism source, the system reliably extracts a coherent graph whose important nodes and edges can be inspected without reconstructing them from prose.

Implementation scope is defined in [`specs/SPEC-001-text-to-knowledge-model.md`](specs/SPEC-001-text-to-knowledge-model.md).

# Phase 2 — Structure Detection

## Goal

Move from a bag of relationships to recognizable system structures.

## Tasks

- [ ] Detect hierarchies.
- [ ] Detect causal chains.
- [ ] Detect dependency chains.
- [ ] Detect temporal sequences.
- [ ] Detect feedback loops.
- [ ] Detect comparison structures.
- [ ] Identify structurally important concepts.
- [ ] Identify candidate system boundaries.
- [ ] Identify variables and constraints.
- [ ] Generate a minimal top-level model.
- [ ] Generate progressively deeper model layers.

## Principle

Prefer:

```text
extract → classify → detect → select → render
```

over:

```text
text → pretty diagram
```

# Phase 3 — First Interactive UI

## Goal

Make the structured model genuinely usable for learning.

## Minimum Interface

```text
SOURCE
Paste text... [Translate]

OVERVIEW
Smallest useful conceptual model

SYSTEM MAP
Interactive graph

SELECTED RELATIONSHIP
A ──CAUSES──► B
Why? / Evidence / Explain / Expand
```

## Tasks

- [ ] Build paste-text input.
- [ ] Render the top-level model.
- [ ] Render an interactive graph using an existing library.
- [ ] Allow node and edge selection.
- [ ] Explain selected relationships.
- [ ] Show source evidence.
- [ ] Expand/collapse model depth.
- [ ] Preserve location within the model while exploring.

## Exit Criterion

The electromagnetism experience is meaningfully better than reading an AI summary.

# Phase 4 — Progressive Disclosure

## Goal

Turn the graph from a visualization into a navigable knowledge space.

```text
DOMAIN
  ↓ zoom
SUBSYSTEM
  ↓ zoom
MECHANISM
  ↓ zoom
FORMAL MODEL
  ↓ zoom
DETAIL / EVIDENCE
```

## Tasks

- [ ] Define abstraction levels.
- [ ] Generate a minimal orientation layer.
- [ ] Expand individual concepts on demand.
- [ ] Expand mechanisms separately from definitions.
- [ ] Reveal mathematical detail only when useful.
- [ ] Allow users to follow causal paths.
- [ ] Highlight feedback loops.
- [ ] Focus temporarily on a subsystem.
- [ ] Preserve context across zoom levels.

# Phase 5 — Qualitative Simulator

## Goal

Move from passive exploration to active model interrogation.

```text
change X
   ↓
identify affected edges
   ↓
trace first-order effects
   ↓
trace second-order effects
   ↓
identify feedback
   ↓
show uncertainty / assumptions
```

## Tasks

- [ ] Select a variable or concept.
- [ ] Support qualitative changes such as increase/decrease/remove/add.
- [ ] Traverse relevant causal paths.
- [ ] Separate direct from indirect consequences.
- [ ] Detect conflicting pathways.
- [ ] Surface feedback effects.
- [ ] Display assumptions and uncertainty.
- [ ] Distinguish source-supported consequences from inference.
- [ ] Prevent qualitative reasoning from masquerading as quantitative simulation.

# Phase 6 — Learning Evaluation

## Goal

Determine whether the product actually improves learning rather than merely looking compelling.

Compare:

```text
A → original source
B → AI summary
C → Knowledge Compiler
```

Measure:

- comprehension
- recall
- ability to explain mechanisms
- ability to answer novel “what if?” questions
- time to useful understanding
- confidence calibration

# Phase 7 — Additional Input Sources

Only expand ingestion after the translation core is validated.

Suggested order:

- [ ] Web page / URL
- [ ] Wikipedia entry
- [ ] PDF
- [ ] YouTube transcript
- [ ] Podcast transcript
- [ ] Uploaded audio/video transcription

All inputs should normalize to the same abstraction:

```text
anything
   ↓
SourceDocument
   ↓
existing translation pipeline
```

# Phase 8 — Personal Knowledge Atlas

Explore whether translated sources can accumulate into a durable learning system.

Potential capabilities:

- [ ] Save translated models.
- [ ] Connect overlapping concepts across sources.
- [ ] Detect contradictions between sources.
- [ ] Merge compatible models.
- [ ] Track explored concepts.
- [ ] Suggest prerequisite knowledge.
- [ ] Show how a user's domain model expands over time.

This remains optional until single-source translation proves valuable.

# Phase 9 — Productization Experiments

Possible directions:

- consumer learning tool
- technical learning / documentation
- education
- explorable knowledge publishing

Do not select a market purely from intuition. Observe who repeatedly finds the primitive product valuable.

# Architecture Principles

```text
INGESTION
   │
   ▼
NORMALIZATION
   │
   ▼
SEMANTIC EXTRACTION
   │
   ▼
KNOWLEDGE MODEL
   │
   ▼
STRUCTURE DETECTION
   │
   ▼
REPRESENTATION
   │
   ▼
INTERACTION
```

Each layer should have a clear contract.

- Source adapters should not know about visualization.
- Visualization should not parse source text.
- The knowledge model should not depend on a graph library.
- LLM output should cross validated typed boundaries before entering core state.
- Evidence should survive every transformation.
- Inference should remain distinguishable from source-derived knowledge.

# Deliberately Not Solving Yet

- perfect ontology design
- universal causal inference
- autonomous fact checking of arbitrary domains
- quantitative simulation of arbitrary systems
- full personal knowledge management
- collaborative editing
- social learning
- course generation
- spaced repetition
- flashcards
- AI tutor personalities
- custom diagram rendering
- every possible source format

# Immediate Builder Sequence

1. Define `KnowledgeModel` and relationship schemas.
2. Save a fixed electromagnetism source fixture.
3. Build one structured extraction boundary.
4. Validate and serialize its output.
5. Inspect the graph manually.
6. Iterate the extraction grammar until the graph is useful.
7. Add the other golden domains.
8. Build structure detection.
9. Only then build the interactive UI.

The first milestone is **not** a polished application.

It is a JSON representation of electromagnetism that makes us think:

> **Yes. This actually captures the system.**

Once that exists, rendering it is an engineering problem. Getting the representation right is the product-discovery problem.
