# Knowledge Compiler

> Transform information optimized for communication into representations optimized for understanding.

Knowledge Compiler is an evidence-led research implementation of a representation translator for learning. It compiles explanatory text into a source-grounded semantic model, detects useful structures, and renders navigable representations at more than one level of resolution.

The project is not yet an end-user learning product. It has a working compiler pipeline, deterministic viewers, live-model evaluation artifacts, and ten completed specification increments. The next question is whether those parts create a trustworthy, useful learning experience on a realistic long-form source.

## The problem

Most educational material is linear: books, articles, documentation, lectures, and videos unfold as sequences. Human understanding is not necessarily linear.

Complex ideas are often understood as systems of entities, relationships, causes, dependencies, processes, feedback loops, constraints, comparisons, and claims. Conventional AI learning tools usually transform text into more text. Knowledge Compiler asks a different question:

> **What underlying structure is this information describing, and what representation makes that structure easiest to understand?**

The goal is not to visualize sentences. It is to recover the system and truth conditions described by them.

## Product thesis

```text
Source → Structure → Model → Intuition
```

Knowledge Compiler treats learning as a representation problem:

- **Map — What exists?** Concepts, components, boundaries, and organization.
- **Model — How does it work?** Causality, dependency, sequence, interaction, comparison, and change.
- **Simulator — What happens if...?** A future counterfactual layer over a sufficiently trustworthy model.

Map and Model have implemented foundations. Simulator remains a product direction, not a current capability. Any future simulator must distinguish qualitative reasoning from quantitative simulation and must not imply precision the source does not support.

## What exists today

The current pipeline is:

```text
plain text
   ↓
normalization and source spans
   ↓
LLM or deterministic semantic extraction
   ↓
validated KnowledgeModel
   ├── entities
   ├── binary relationships
   ├── structured propositions
   ├── evidence
   └── confidence / origin
   ↓
deterministic structure detection
   ↓
representation, layout, interaction, and semantic navigation
   ↓
optional source-grounded child resolution
```

Implemented capabilities include:

- strict models for source documents, entities, relationships, evidence, and confidence;
- source-grounded LLM extraction with fail-closed validation;
- conservative entity deduplication and canonical endpoint handling;
- deterministic detection of hierarchies, causal paths, dependency chains, process chains, and feedback candidates;
- deterministic representation building, structure-aware layout, and synchronized graph/detail interaction;
- contextual progressive disclosure and one-level semantic child resolutions;
- automatic resolution strategy selection with recorded provenance and run history;
- proposition modeling for cases whose truth is distorted by a single binary edge;
- committed machine and human evaluation artifacts across five golden domains and focused live comparisons.

The implementation is currently strongest as a research-grade compiler and artifact viewer. It does not yet provide a polished paste-to-learn application, general long-form ingestion, recursive semantic zoom, or validated counterfactual simulation.

## Semantic model

### Entities and binary relationships

Ordinary assertions remain binary relationships when a source concept can truthfully be represented as `source —predicate→ target`.

The current canonical relationship vocabulary contains 20 predicates:

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
AFFECTS
BINDS_TO
TRANSFERS_TO
```

These relationships support higher-order structures:

```text
PART_OF chains                  → hierarchy
CAUSES / INCREASES / DECREASES → causal path
PRECEDES chains                 → process chain
REQUIRES chains                 → dependency chain
causal return paths             → feedback candidate
```

### Structured propositions

Some claims require more than two endpoints. Knowledge Compiler uses a hybrid model: binary relationships remain the default, while structured propositions are reserved for claims that would otherwise lose essential truth.

Current proposition types:

- `COMPARISON_CONDITION`
- `TRANSFER_EVENT`

Current proposition roles and operator:

```text
LEFT_OPERAND
RIGHT_OPERAND
OUTCOME
EVENT
OBJECT
DESTINATION

GREATER_THAN
```

Examples include “quantity demanded is greater than quantity supplied, producing a shortage” and “an order command transfers to an order component.” The participants keep their direct parent relationships, and the proposition captures the full claim. Proposition cards are currently rendered alongside graph representations; proposition topology is deliberately not yet part of structure traversal.

## Why not just generate mind maps?

Mind maps are useful, but they are only one representation. Structure should determine the view.

| Information structure | Useful representation |
| --- | --- |
| X consists of A, B, C | Hierarchy / decomposition tree |
| A influences B | Causal graph |
| A happens before B | Process / sequence diagram |
| A depends on B | Dependency graph |
| A reinforces B, which reinforces A | Feedback-loop diagram |
| A differs from B under a condition | Proposition or comparison view |
| A transfers an object to B | Event-centered proposition view |

The important capability is the translation grammar, not the arrows.

## Progressive disclosure and semantic resolution

The interface is intended to behave more like a map than a document: begin with orientation, then reveal mechanism or detail without losing context.

The implementation currently provides contextual layer preferences and one-level child resolutions. Live evaluation established that:

- process-focused strategy selection can outperform generic detail expansion;
- component-internals can safely refuse when the source lacks enough detail;
- variable-focused causal-neighborhood selection remains unvalidated;
- deeper recursive resolution and an active navigation model remain future work.

These mixed and negative findings are accepted evidence. They are constraints on the next design, not results to hide or tune away.

## Grounding and trust

Every generated entity, relationship, and proposition must remain traceable to source evidence. Generated child artifacts preserve their parent focus, source scope, strategy choice, and run history. Semantic validation is fail-closed: insufficient source detail produces an explicit refusal instead of invented structure.

The AI is therefore intended to act as an interface over the source, not an opaque replacement for it.

## Current evidence boundary

Demonstrated:

- a source-grounded semantic intermediate representation;
- the 20-predicate relationship vocabulary across the golden domains;
- deterministic structure detection and structure-aware rendering;
- synchronized selection and evidence inspection;
- contextual progressive disclosure;
- one real automatically generated semantic resolution;
- safe refusal when the source is insufficient;
- process-specific resolution value in a controlled comparison;
- proposition-aware modeling for comparison conditions and transfer events.

Not yet demonstrated:

- reliable generalization to realistic long-form source material;
- a broadly reliable automatic resolution policy;
- proposition-aware topology and traversal;
- recursive or deeply nested semantic zoom;
- an elegant active-map navigation experience;
- measurable improvement in learning outcomes;
- a complete end-user input and product workflow.

The current decision frontier is defined in [REVIEW-001](reviews/REVIEW-001-post-spec-010-product-architecture.md): prove one real-source, end-to-end learning slice before expanding the platform.

## Direction, not current scope

The longer-term product vision still includes richer source adapters, alternative views, recursive semantic zoom, personal learning state, and carefully bounded “what if?” exploration. Those ideas become valuable only after the core transformation is shown to help a learner understand a realistic source better than the source alone.

Three principles guide that progression:

1. **Compile before rendering.** Extract, validate, detect, select, then render.
2. **Preserve truth before adding richness.** Grounding, provenance, uncertainty, and refusal are product behavior.
3. **Earn complexity with evidence.** Add a capability only when an evaluation resolves a real product risk.

## Repository guide

- [Architecture](ARCHITECTURE.md) — implemented module and data-flow boundaries.
- [Roadmap](ROADMAP.md) — completed evidence, open risks, and next decision frontier.
- [Operating model](OPERATING_MODEL.md) — specification, implementation, evaluation, and handoff workflow.
- [Project memory](PROJECT_MEMORY.md) — durable project context and accepted decisions.
- [Project health](PROJECT_HEALTH.md) — repository-level health indicators.
- [SPEC-010](specs/SPEC-010-proposition-and-endpoint-modeling.md) — proposition and endpoint modeling contract.
- [DEBRIEF-010](debriefs/DEBRIEF-010-proposition-and-endpoint-modeling.md) — accepted SPEC-010 outcomes.
- [REVIEW-001](reviews/REVIEW-001-post-spec-010-product-architecture.md) — post-SPEC-010 product and architecture review.

## Local development

Knowledge Compiler requires Python 3.12 or newer.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test,llm]'
.venv/bin/pytest
```

The `openai` extra and `OPENAI_API_KEY` are needed only for live model-backed extraction or resolution. Deterministic tests do not require network access.

The command-line entry point is:

```bash
.venv/bin/knowledge-compiler --help
```

## North star

> **Paste difficult text. Get a model you can think with.**
