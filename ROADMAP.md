# Knowledge Compiler — Roadmap

This roadmap is organized around risk reduction, not feature accumulation. It records what the repository has demonstrated, what its evaluations rejected or left unresolved, and which question should be answered next.

## North star

> **Paste difficult text. Get a model you can think with.**

The project thesis remains:

> Compile source-grounded information into a navigable, multi-resolution knowledge space whose cognitive projection can adapt to how the learner wants to think.

## Status vocabulary

- **Implemented** means the behavior exists and is covered by repository tests.
- **Evaluated** means committed machine or human evidence exercises the behavior.
- **Accepted** means the relevant SPEC handoff or debrief accepted the result, including mixed or negative results.
- **Future** means product direction only; it must not be presented as current capability.

## Completed foundation

SPEC-001 through SPEC-010 are complete. Their value is cumulative: they form a compiler-style pipeline rather than ten independent features.

| Increment | Capability established | Accepted outcome |
| --- | --- | --- |
| [SPEC-001](specs/SPEC-001-text-to-knowledge-model.md) | Plain text to validated `KnowledgeModel` | Source spans, entities, relationships, claims, evidence, confidence, and serialization established. |
| [SPEC-002](specs/SPEC-002-llm-semantic-extraction.md) | Live LLM semantic extraction | Golden-domain extraction exercised with failures and retries preserved. |
| [SPEC-003](specs/SPEC-003-relationship-semantics.md) | Canonical relationship semantics | Vocabulary expanded and domain regressions evaluated without weakening grounding. |
| [SPEC-004](specs/SPEC-004-structure-detection.md) | Deterministic higher-order detection | Hierarchy, causal path, dependency chain, process chain, and feedback-candidate detection established. |
| [SPEC-005](specs/SPEC-005-minimal-representation.md) | Minimal representation compiler | Semantic models compile into inspectable deterministic representations. |
| [SPEC-006](specs/SPEC-006-structure-aware-layout-and-synchronized-interaction.md) | Structure-aware layout and interaction | Graph and detail state synchronize; evidence and selection remain inspectable. |
| [SPEC-006A](specs/SPEC-006A-baseline-interface-capture.md) | Interface baseline capture | Canonical visual and interaction evidence recorded for regression comparison. |
| [SPEC-007](specs/SPEC-007-progressive-disclosure-semantic-navigation.md) | Contextual semantic navigation | Layer preferences and exploration artifacts established; active-map navigation remains incomplete. |
| [SPEC-008](specs/SPEC-008-automatic-multi-resolution-compilation.md) | Automatic one-level resolution | One real child resolution succeeded; source insufficiency fails closed with provenance preserved. |
| [SPEC-009](specs/SPEC-009-semantic-resolution-strategy.md) | Strategy-aware semantic resolution | Process stages beat generic detail in the controlled case; variable strategy stayed unvalidated; component strategy refused safely. |
| [SPEC-010](specs/SPEC-010-proposition-and-endpoint-modeling.md) | Hybrid proposition and endpoint model | Comparison conditions and transfer events preserve truth that binary edges alone distorted. |
| [OPS-001](ops/OPS-001-codex-context-and-git-workflow.md) | Repository operating model | Durable context, branch discipline, evaluation records, and SPEC handoff workflow codified. |

The accepted narrative for each increment lives in its corresponding file under [`debriefs/`](debriefs/). The current synthesis is [REVIEW-001](reviews/REVIEW-001-post-spec-010-product-architecture.md).

## Current architecture

The repository now implements this conceptual flow:

```text
SourceDocument
   ↓ normalize and preserve spans
semantic extraction
   ↓ validate and deduplicate conservatively
KnowledgeModel
   ├── Entity
   ├── Relationship
   ├── Proposition
   └── Evidence / confidence / origin
   ↓
deterministic structure detection
   ↓
representation compiler and layout
   ↓
viewer interaction and semantic navigation
   ↓ optional
resolution strategy selection
   ↓ source-scoped live generation or explicit refusal
child KnowledgeModel + provenance + run history
```

This is deliberately a compiler architecture: semantic intermediate representation first, projections second. UI rendering, resolution strategy, and future learning experiences should consume the same grounded model rather than inventing parallel semantics.

## Current semantic boundary

### Binary relationship vocabulary

```text
IS_A              PART_OF            CAUSES
INCREASES         DECREASES           ENABLES
REQUIRES          CONSTRAINS          PRECEDES
TRANSFORMS_INTO   INTERACTS_WITH      MEASURED_BY
EXAMPLE_OF        CONTRADICTS         CREATES
INDUCES           EXERTS_FORCE_ON     AFFECTS
BINDS_TO          TRANSFERS_TO
```

### Detected structures

```text
HIERARCHY
CAUSAL_PATH
PROCESS_CHAIN
DEPENDENCY_CHAIN
FEEDBACK_CANDIDATE
```

### Structured propositions

Binary relationships remain the default. Structured propositions are used only when a claim's truth requires multiple participants or roles.

```text
types:     COMPARISON_CONDITION, TRANSFER_EVENT
roles:     LEFT_OPERAND, RIGHT_OPERAND, OUTCOME,
           EVENT, OBJECT, DESTINATION
operator:  GREATER_THAN
```

Proposition participants retain direct parent relationships. Proposition cards are implemented, while proposition topology, traversal, and generalized ontology are not.

## Accepted mixed and negative findings

Roadmap decisions must preserve these findings rather than treating every experiment as a feature success:

1. **Real-source generalization is unproven.** Golden fixtures and focused source texts do not establish reliable long-form use.
2. **Automatic resolution is only partly validated.** A process-stage strategy produced useful differentiation; the variable causal-neighborhood strategy did not establish superiority.
3. **Safe refusal is a success condition.** Component internals returned `INSUFFICIENT_SOURCE_DETAIL` when the source could not support the requested detail.
4. **One level is not a zoom system.** Child resolution works, but recursive depth, re-entry, and accumulated context have not been designed or validated.
5. **Navigation is functional, not yet product-quality.** Explore/Back and contextual layers preserve state, but they do not yet provide an elegant active-map experience.
6. **Propositions preserve truth but do not yet shape topology.** SPEC-010 solved two concrete semantic distortions without proving a general proposition ontology.
7. **Learning impact is unknown.** Structural correctness and reviewer preference are prerequisites, not evidence of comprehension or retention gains.
8. **There is no complete end-user workflow.** The repository exposes compiler, artifact, and viewer foundations rather than a polished input-to-learning product.

## Next decision frontier

### Proposed SPEC-011 — Real-Source End-to-End Learning Slice

The next increment should answer one product question:

> Can Knowledge Compiler transform one realistic, richer plain-text source into a trustworthy and useful overview plus at least one automatically generated deeper semantic resolution that its intended learner prefers to the source alone?

This should be a vertical slice, not a platform expansion.

### Scope

- Select one realistic, sufficiently rich plain-text source and record the source-selection rationale.
- Compile it through the existing source-grounded semantic pipeline.
- Produce a minimal orientation representation using the current structure and proposition models.
- Select one meaningful focus and choose its resolution strategy automatically.
- Generate at least one source-supported child resolution, or preserve a truthful failure if the source is insufficient.
- Present overview, focus, child resolution, evidence, and provenance as one coherent learning path.
- Compare the experience with the original source using a predefined human evaluation rubric.
- Preserve every call, failure, retry, usage/cost record, source-sufficiency decision, and generated artifact.

### Hold constant

To isolate the core question, SPEC-011 should not add:

- PDF, web, audio, or video adapters;
- a navigation redesign;
- recursive resolution depth;
- personalization or learner memory;
- a generalized proposition ontology;
- qualitative or quantitative simulation;
- accounts, collaboration, or database infrastructure.

### Exit criteria

The increment is successful only if all of the following are true:

- the overview is faithful, coherent, and useful without reconstructing the source;
- the selected deeper resolution adds source-supported understanding rather than generic elaboration;
- every important generated semantic item remains inspectably grounded;
- insufficiency and validation failures remain explicit and fail closed;
- the evaluator prefers the compiled learning path to the original source for orientation and focused understanding;
- the result identifies whether the next risk is source transformation, representation, navigation, or evaluation—not merely another missing feature.

A negative result is still valuable if its evidence is complete and it narrows the product thesis.

## Later candidates, contingent on evidence

These are possible directions, not promises or current capability:

1. **Active map navigation** — replace document-like Explore/Back behavior with stable spatial and semantic orientation.
2. **Recursive semantic resolution** — only after one-level resolution is consistently useful and provenance remains understandable.
3. **Representation selection** — compare hierarchy, causal, process, dependency, proposition, and mixed projections using learner tasks.
4. **Proposition-aware topology** — add traversal semantics only for proven cases where proposition cards are insufficient.
5. **Learning evaluation** — compare original source, conventional summary, and Knowledge Compiler on explanation, transfer, recall, and confidence calibration.
6. **Qualitative simulator** — explore counterfactuals only when direction, assumptions, and source-versus-inference boundaries can be made explicit.
7. **Additional source adapters** — normalize web pages, PDFs, and transcripts only after the core plain-text transformation earns expansion.
8. **Personal learning state** — defer until the system can reliably identify what should be learned and at what resolution.

The preferred visual metaphor remains a two-dimensional semantic map with zoom and alternate projections. Three-dimensional representation should be reserved for domains whose subject matter is inherently spatial or physical.

## Product principles

1. **Truth before fluency.** Do not trade grounding or semantic validation for a smoother demo.
2. **Structure before presentation.** Extract, classify, detect, select, then render.
3. **Evidence before scope.** Each increment should resolve one important uncertainty.
4. **Failures are artifacts.** Preserve insufficiency, retries, mixed comparisons, usage, and reviewer decisions.
5. **One semantic core.** Views and future product surfaces compile from the same model.
6. **Progressive disclosure over graph density.** More nodes are not automatically more understanding.
7. **Explicit boundaries.** Separate implemented capability, evaluated evidence, and future vision.

## Current non-goals

- renaming the project or repository;
- building a generic knowledge-graph platform;
- ingesting every content format;
- creating a persistent personal knowledge base;
- inventing unsupported detail to satisfy a requested resolution;
- presenting qualitative inference as quantitative simulation;
- optimizing visual polish before the real-source learning slice is validated.

## Decision records

- [OPERATING_MODEL.md](OPERATING_MODEL.md) defines how work moves from SPEC to evidence and handoff.
- [ARCHITECTURE.md](ARCHITECTURE.md) documents implemented technical boundaries.
- [PROJECT_MEMORY.md](PROJECT_MEMORY.md) preserves durable constraints and accepted outcomes.
- [PROJECT_HEALTH.md](PROJECT_HEALTH.md) tracks repository health.
- [DEBRIEF-010](debriefs/DEBRIEF-010-proposition-and-endpoint-modeling.md) records the accepted proposition-modeling result.
- [REVIEW-001](reviews/REVIEW-001-post-spec-010-product-architecture.md) defines the current synthesis and next decision frontier.
