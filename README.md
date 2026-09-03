# Knowledge Compiler

> Transform information optimized for communication into representations optimized for understanding.

## The Problem

Most educational material is linear: books, articles, documentation, Wikipedia entries, podcasts, lectures, and videos unfold as sequences. Complex concepts are not necessarily best understood that way.

They are often systems of entities, relationships, causes, dependencies, processes, feedback loops, constraints, and trade-offs. Conventional AI learning tools usually transform text into more text: summaries, notes, flashcards, quizzes, or chat.

Knowledge Compiler explores a different question:

> **What underlying structure is this information describing, and what representation makes that structure easiest to understand?**

The goal is not to visualize sentences. It is to extract the system described by them.

## Product Thesis

```text
Source → Structure → Model → Intuition
```

The system accepts source material, extracts a structured knowledge model, detects the kinds of relationships present, and eventually chooses representations suited to those relationships.

```text
SOURCE
  │
  ▼
canonical text
  │
  ▼
SEMANTIC EXTRACTION
  │
  ▼
KNOWLEDGE MODEL
  │
  ├── entities
  ├── relationships
  ├── claims
  ├── evidence
  └── uncertainty
  │
  ▼
STRUCTURE DETECTION
  │
  ├── hierarchy
  ├── causality
  ├── dependency
  ├── process
  ├── feedback
  └── comparison
  │
  ▼
REPRESENTATION ENGINE
  │
  ├── concept map
  ├── causal model
  ├── process model
  ├── timeline
  ├── matrix
  └── system view
  │
  ▼
MENTAL MODEL
  │
  ▼
SIMULATOR — “What if...?”
```

## Why Not Just Mind Maps?

Mind maps are one useful representation, not the destination.

| Information structure | Better representation |
| --- | --- |
| X consists of A, B, C | Hierarchy / decomposition tree |
| A influences B | Causal graph |
| A happens before B | Process / sequence diagram |
| A and B interact | System diagram |
| A trades off against B | Trade-off matrix |
| A changes over time | Timeline |
| If X, do Y | Decision tree |
| A depends on B | Dependency graph |
| A reinforces B, which reinforces A | Feedback-loop diagram |

The application should infer the structure first and render it second.

## Core Learning Model

Knowledge Compiler is organized around three artifacts:

### Map — What exists?

The domain structure: concepts, components, mechanisms, boundaries, and constraints.

### Model — How does it work?

Relationships and dynamics: causality, dependencies, processes, state changes, interactions, feedback loops, and trade-offs.

### Simulator — What happens if...?

Counterfactual exploration of the model. Change a variable or assumption and trace likely consequences.

```text
MAP → MODEL → SIMULATOR
what?   how?     what if?
```

The simulator must distinguish qualitative reasoning from quantitative simulation and must not imply precision the source does not support.

## Representation Grammar

The core capability is translation into a reusable semantic structure, not drawing arrows.

An initial relationship vocabulary may include:

```text
IS_A
PART_OF
CAUSES
INCREASES
DECREASES
ENABLES
REQUIRES
CONSTRAINS
PRECEDES
TRANSFORMS_INTO
INTERACTS_WITH
MEASURED_BY
EXAMPLE_OF
CONTRADICTS
CREATES
INDUCES
EXERTS_FORCE_ON
```

Higher-order structures can then emerge from combinations of edges:

```text
PART_OF chains             → hierarchy
CAUSES chains              → causal model
CAUSES returning to origin → feedback loop
PRECEDES chains            → process / timeline
REQUIRES graph             → dependency model
alternatives + attributes  → comparison matrix
```

## Progressive Disclosure

Complex domains are connected at many abstraction levels. Showing everything at once creates graph spaghetti.

Knowledge Compiler should behave more like a map than a document:

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

## Nodes, Edges, Paths, and Loops

- **Nodes** answer: *What is X?*
- **Edges** answer: *Why does X affect Y?*
- **Paths** answer: *How does X eventually lead to Z?*
- **Loops** answer: *How does the system behave over time?*
- **Counterfactuals** answer: *What happens if X changes?*

Systems understanding often lives in the edges rather than isolated definitions.

## Source Grounding

Every important node, relationship, and claim should remain traceable to the source material from which it was derived.

```text
changing magnetic field
          │
          │ INDUCES
          ▼
    electric field
          │
          └── Evidence
                 ├── source section
                 ├── source paragraph
                 └── transcript timestamp
```

The AI should act as an interface over the source, not an opaque replacement for it.

## MVP

The first version is deliberately small.

### Input

Paste explanatory text.

### Transformation

1. Normalize the source.
2. Extract entities and concepts.
3. Extract claims and typed relationships.
4. Preserve evidence references.
5. Validate structured output.
6. Merge conservative duplicates.
7. Produce a `KnowledgeModel`.

### Output

For the first milestone, the output is inspectable structured JSON — not a polished UI.

```text
Text
 ↓
LLM / extractor
 ↓
validated schema
 ↓
KnowledgeModel JSON
```

### Explicitly Not in the First MVP

- user accounts
- podcast or YouTube ingestion
- PDF ingestion
- browser extension
- mobile app
- giant persistent personal knowledge graph
- collaboration
- custom visualization engine
- arbitrary quantitative simulation

First prove one thing:

> **Paste difficult text. Get a model you can think with.**

## Golden Test Case

The first benchmark is **electromagnetism**.

A useful transformation should reveal relationships such as:

```text
Matter ↔ Electromagnetic Field

Charge → Electric Field → Force → Motion

Moving Charge → Magnetic Effects

Changing E ↔ Changing B → Electromagnetic Wave → Light
```

The acceptance criterion is experiential:

> Does the generated model make the source substantially easier to understand than reading or summarizing the source alone?

After electromagnetism, test deliberately different domains:

- software architecture
- economics
- biology
- history

If one translation grammar produces useful models across all five, the project has demonstrated something more interesting than a domain-specific prompt.

## Design Principles

- **Structure before presentation.** Extract the knowledge model before deciding how to visualize it.
- **Relationships over isolated facts.** Preserve mechanisms, dependencies, and causality.
- **Progressive disclosure.** Start with the smallest useful model and reveal complexity deliberately.
- **Source over hallucination.** Distinguish source-derived claims from inference.
- **Intuition before notation.** When appropriate: `SYSTEM → RELATIONSHIP → INTUITION → MATHEMATICS`.
- **Models over summaries.** Compression is useful only when explanatory structure survives.
- **Show uncertainty.** Generated causal edges and counterfactuals must communicate uncertainty.
- **Build the smallest useful thing.** Prove translation quality before solving every ingestion or UI problem.

## Architecture Direction

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
KNOWLEDGE MODEL  ← semantic intermediate representation
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

The `KnowledgeModel` is intentionally similar to a compiler intermediate representation: source-specific details are normalized into a stable semantic form that many downstream renderers or interactions can consume.

## Current Builder Focus

See [`specs/SPEC-001-text-to-knowledge-model.md`](specs/SPEC-001-text-to-knowledge-model.md).

The first implementation milestone is not a polished application. It is a JSON representation of electromagnetism that makes us think:

> **Yes. This actually captures the system.**

Once that exists, rendering it becomes primarily an engineering problem. Getting the representation right is the product-discovery problem.
