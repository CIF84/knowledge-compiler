# SPEC-008 — Automatic Multi-Resolution Compilation Spike

## Status

Ready for implementation.

## Primary Question

> Can Knowledge Compiler automatically derive one trustworthy deeper semantic resolution for selected concepts from source-grounded material, replacing the manually authored SPEC-007 child fixtures without losing provenance, semantic honesty, or useful abstraction change?

## Purpose

SPEC-007 validated the **navigation grammar** for semantic depth. For the target learner, contextual expansion was the clear conceptual winner because it supports “peeling layers” while preserving orientation in the larger system.

However, SPEC-007 deliberately cheated: the deeper child models were manually authored experiment fixtures.

The project has therefore proven:

```text
IF a useful child model exists
        ↓
contextual semantic navigation is useful
```

It has **not** proven:

```text
source-grounded material
        ↓
Knowledge Compiler
        ↓
useful child semantic resolution
```

SPEC-008 tests that missing capability.

This is not a recursive knowledge-atlas implementation. It is a narrow compilation spike: generate exactly one deeper resolution for one or two selected parent concepts and compare the generated result against source evidence and the accepted SPEC-007 handcrafted reference fixtures.

## Product Hypothesis

The working hypothesis is:

> A real source document contains enough grounded explanatory structure for a compiler to produce more than one useful semantic resolution, and an LLM can nominate a deeper local mechanism while deterministic validation preserves provenance and semantic integrity.

The important phrase is **semantic resolution**.

A child model is not automatically better merely because it has:

- more nodes;
- more edges;
- longer descriptions;
- more words;
- a narrower subset of the parent graph.

A useful child model should explain **what happens inside, around, or through the selected parent concept at a meaningfully finer level of abstraction**.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `debriefs/DEBRIEF-006-structure-aware-layout-and-synchronized-interaction.md`
8. `debriefs/DEBRIEF-007-progressive-disclosure-semantic-navigation.md`
9. `baselines/BASELINE-001-interface.md`
10. `specs/SPEC-007-progressive-disclosure-semantic-navigation.md`
11. `src/knowledge_compiler/openai_extractor.py`
12. `src/knowledge_compiler/relationships.py`
13. `src/knowledge_compiler/models.py`
14. `src/knowledge_compiler/representations.py`
15. `src/knowledge_compiler/semantic_navigation.py`
16. accepted SPEC-002/003 source fixtures and live artifacts for the chosen domains
17. accepted SPEC-007 handcrafted exploration fixtures

Treat the SPEC-007 handcrafted fixtures as **reference models for comparison**, not as training targets to reproduce exactly.

## Experimental Scope

Implement the smallest end-to-end path that can:

1. accept an existing source-grounded `KnowledgeModel` plus a selected parent concept;
2. identify source material relevant to that concept using deterministic evidence/source context where practical;
3. ask a real LLM to propose one finer-resolution local semantic model;
4. require exact source grounding for source-derived child claims/relationships;
5. deterministically resolve nominated evidence quotes to source spans;
6. validate child entities/relationships against the existing canonical relationship grammar;
7. preserve explicit provenance for every source-derived child edge;
8. distinguish unsupported/inferred content from source-grounded content;
9. fail closed when the source does not contain enough information for a trustworthy deeper model;
10. produce a deterministic validated child representation artifact after probabilistic extraction;
11. plug that generated child into the existing SPEC-007 semantic-navigation viewer with minimal adaptation;
12. compare the generated child against the handcrafted SPEC-007 reference fixture and source text;
13. evaluate whether the result is genuinely a finer semantic resolution rather than merely a graph subset or paraphrase.

## Benchmark Domains

Use the same two concepts from SPEC-007 if the underlying accepted source material is sufficient:

### Software Architecture

Parent focus:

```text
API component
```

Reference handcrafted child:

```text
fixture-api-request-handling
```

### Economics

Parent focus:

```text
market price
```

Reference handcrafted child:

```text
fixture-market-price-response
```

### Source sufficiency is part of the experiment

Do **not** silently enrich the source from the web or general model knowledge if the accepted source fixture lacks enough detail.

If one or both domains cannot support a meaningful child model from the existing source, that is an important result.

In that case:

- report `INSUFFICIENT_SOURCE_DETAIL` or equivalent;
- preserve the failure artifact;
- do not hallucinate the handcrafted reference content;
- optionally use a deliberately richer **local fixed source fixture** only as a second controlled sub-experiment, clearly separated from the original-source result.

The project needs to learn whether multi-resolution compilation requires richer source material.

## Explicit Non-Goals

Do not implement:

- arbitrary recursive depth;
- more than one generated child level per focus concept;
- automatic exploration for every node;
- web retrieval;
- Wikipedia retrieval;
- PDF/video/podcast ingestion;
- cross-document synthesis;
- embeddings/vector databases;
- persistent knowledge atlas;
- graph database;
- user accounts;
- personalization engine;
- automatic cognitive-preset selection;
- new permanent cognitive presets;
- simulator/counterfactual propagation;
- quantitative modeling;
- event/state IR redesign unless the experiment proves it is a hard blocker;
- broad relationship-vocabulary expansion;
- new frontend framework;
- UI redesign;
- BASELINE-002;
- general recursive ontology/decomposition architecture;
- hidden source enrichment from model pretraining knowledge.

Do not build the eventual system. Answer the primary question.

## Preserve Existing Architecture

The current semantic pipeline remains authoritative:

```text
SourceDocument
      ↓
KnowledgeExtractor
      ↓
ExtractionResult
      ↓
KnowledgeModel
      ↓
StructureDetector
      ↓
DetectedStructureSet
      ↓
RepresentationModel
```

SPEC-008 introduces an experimental **multi-resolution compiler boundary** downstream of the parent `KnowledgeModel` but still grounded in the same source document.

Conceptually:

```text
KnowledgeModel + focus concept
            ↓
ResolutionCompiler
            ↓
ChildExtractionResult
            ↓
validation / evidence resolution
            ↓
ChildKnowledgeModel or equivalent bounded semantic artifact
            ↓
structure / representation
            ↓
GeneratedExploration
```

The exact intermediate types are implementation choices.

Important constraints:

- do not mutate the parent `KnowledgeModel`;
- do not place navigation state inside semantic IR;
- do not let viewer code call the LLM;
- provider-specific logic stays behind a narrow adapter/boundary;
- source grounding remains deterministic after model nomination;
- generated child semantic truth must be inspectable independently from its rendered representation.

## Parent-to-Child Semantic Contract

A generated child must explicitly identify:

```text
parent document ID
parent representation / focus entity ID
focus label
resolution compiler version
provider/model/prompt version
source scope used
child entities
child relationships
child claims if needed
provenance/evidence
resolution assessment metadata
```

The child must not pretend to be an unrelated new document.

The parent → child relationship should be explicit in metadata, but do not invent a new semantic predicate such as `HAS_DEEPER_MODEL` inside `KnowledgeModel` merely for navigation.

## Source Scope

The compiler should not blindly send arbitrary unrelated source text if a smaller deterministic context can be selected safely.

Investigate a conservative source-scope strategy using existing evidence around the focus concept, for example:

```text
focus entity mentions / evidence
+ directly connected source-grounded relationships
+ nearby source sentences/paragraph context
```

However, avoid overfitting a brittle retrieval algorithm to tiny fixtures.

The implementation must report exactly what source text/span was provided to the child extractor.

If using the full source document is simpler and small enough for this spike, that is acceptable. Record the choice.

## Resolution Extraction Contract

The LLM should receive:

1. the selected parent concept;
2. enough parent semantic context to understand its role;
3. the allowed canonical relationship grammar;
4. the permitted source text only;
5. an explicit instruction to produce a **finer-resolution explanatory model**, not a summary of the parent;
6. an explicit permission to return `INSUFFICIENT_SOURCE_DETAIL` rather than fabricate depth.

The model should nominate exact unique source quotes for every source-grounded relationship/claim using the successful SPEC-002/003 grounding pattern.

Trusted code resolves coordinates.

Do not allow the model to provide trusted source offsets directly.

## What Counts as a Finer Resolution?

This is the central experimental challenge.

A child model should satisfy most of these qualitative properties:

### Locality

The child is centered on the selected parent concept rather than reproducing the entire document.

### Mechanistic/detail gain

The child exposes internal steps, components, variables, interactions, or mechanisms not visible in the parent representation.

### Parent coherence

The child remains recognizably about the parent concept and does not drift into a neighboring topic.

### Explanatory structure

The child contains meaningful typed relationships, not merely isolated definitions.

### Source support

Source-derived detail is grounded in the permitted source.

### Compression relationship

A reviewer should be able to plausibly view the parent concept as a higher-level compression/abstraction of the child model.

This last property is especially important.

Conceptually:

```text
CHILD MODEL
   many lower-level semantic elements
          ↓ compress
PARENT CONCEPT
```

SPEC-008 does not need to implement automatic reverse summarization, but evaluation should ask whether this relationship holds.

## Failure Outcomes

The compiler must support explicit non-success outcomes rather than always producing a graph.

At minimum distinguish:

```text
SUCCESS
INSUFFICIENT_SOURCE_DETAIL
GROUNDING_FAILURE
SEMANTIC_VALIDATION_FAILURE
PROVIDER_FAILURE
```

Use existing error/validation conventions where practical.

Do not turn repeated retries into hidden success selection.

## Relationship Grammar

Reuse the current canonical relationship registry unchanged by default.

Do not add predicates merely because the child extractor wants more vocabulary.

If a repeated, important child-resolution proposition cannot be represented honestly, report the vocabulary gap in the handoff. Do not expand the enum unless the experiment cannot proceed without it and the change is strongly justified.

Prefer truthful claims over forced edges.

## Evidence Grounding

Reuse the proven pattern:

```text
LLM nominates exact unique quote
        ↓
deterministic quote resolution
        ↓
validated SourceSpan
```

For every `SOURCE` child relationship/claim:

- evidence quote must exist in the permitted source scope;
- quote must resolve unambiguously;
- span must validate against the original source document;
- source provenance must survive into child representation/detail view.

If the child includes `INFERRED` relationships, they must remain clearly marked and must not fabricate source evidence.

## Child Semantic Artifact

Prefer a typed semantic artifact rather than jumping directly from LLM output to `Representation`.

It may reuse `KnowledgeModel` if that is semantically clean, or introduce a narrowly scoped child-resolution type if necessary.

Decision criteria:

- can it be validated independently of the viewer?
- does it preserve source/provenance semantics?
- can existing structure detection/representation code consume it with minimal adaptation?
- does it avoid contaminating the parent semantic model?

Do not create a generalized recursive hierarchy merely for future extensibility.

## Structure and Representation

Where practical, run generated child semantics through existing deterministic downstream machinery:

```text
child semantic model
    ↓
StructureDetector
    ↓
RepresentationBuilder
    ↓
layout
```

This is preferable to asking the LLM to design a diagram.

If the child semantic graph does not form one of the existing detected structure types but remains meaningful, report that honestly. Do not silently invent a presentation-only structure without explaining the deviation.

## Navigation Integration

The generated child should be usable in the existing SPEC-007 Contextual mode with minimal viewer changes.

Do not redesign Contextual mode.

For this spike it is acceptable to prepare generated exploration artifacts offline and then launch them in the current semantic-navigation viewer.

The viewer must clearly distinguish:

```text
Generated from source
```

from the old:

```text
Experimental handcrafted fixture
```

without overwhelming the learner with implementation metadata.

## Handcrafted Reference Comparison

The SPEC-007 handcrafted child is a **reference**, not ground truth.

Compare generated vs handcrafted models on:

```text
focus relevance
mechanistic/detail gain
relationship truthfulness
source grounding
structure usefulness
parent coherence
compression relationship
cognitive usefulness
```

Also report useful differences where the generated child is better because it follows the source more faithfully than the handcrafted fixture.

Do not score based on lexical overlap with the handcrafted fixture.

## Original Source vs Richer Source Sub-Experiment

If the original benchmark source is insufficient, perform at most one controlled richer-source sub-experiment for the affected domain.

Requirements:

- richer source must be a committed local text fixture;
- provenance must remain exact;
- source must be clearly labeled as SPEC-008 experimental source material;
- no web retrieval during evaluation;
- report original-source failure separately from richer-source result;
- do not claim the richer-source success proves the original pipeline can generate depth from sparse inputs.

The richer source should contain enough explanatory detail to test compilation, not be written to match a desired graph exactly.

## Provider / Model

Use the same OpenAI provider boundary and preferably the same model family used successfully in SPEC-003 if still available and practical.

Keep provider/model explicit in artifacts.

Use one prompt version initially.

Prompt iteration is allowed only in response to clearly documented failure. Preserve/report attempts; do not cherry-pick a favorable run silently.

## Offline vs Live Tests

Normal `pytest` must remain fully offline and deterministic.

Use deterministic fixture adapters for child-resolution extraction tests.

Real provider calls belong only in an explicit live evaluation command.

## Live Evaluation

Run the automatic child-resolution compiler on Software Architecture and Economics using the accepted original source fixtures first.

For each focus concept record:

```text
outcome
source scope
provider/model
prompt version
entities
relationships
claims
SOURCE vs INFERRED counts
grounding failures/retries
structure detection result
representation result
usage/cost
```

If original source is insufficient, preserve that result and optionally run the richer-source sub-experiment as specified above.

## Human Review

The owner should inspect generated child models in Contextual mode only **after** independent repository/semantic review.

Compare:

```text
handcrafted SPEC-007 child
        vs
generated SPEC-008 child
```

The key questions are:

- Does the generated child actually feel like peeling one semantic layer?
- Is it still clearly about the selected parent concept?
- Does it expose useful mechanism/detail?
- Does source grounding make the model trustworthy enough?
- Is the handcrafted version materially better, and if so why?
- Does the generated version contain source-faithful insight the handcrafted reference missed?

Do not create BASELINE-002 from this experiment.

## Cognitive Presets

Preserve the SPEC-007 A/B/C modes and the emerging cognitive-preset concept.

Do not implement personalization in SPEC-008.

The current working cognitive purposes remain:

```text
Overview    → landscape
Focus       → isolate
Contextual  → peel layers while preserving orientation
```

Automatic multi-resolution compilation should feed these projections; it should not hard-code itself specifically to one learner preset.

## Evaluation Artifacts

Create a committed directory such as:

```text
examples/evaluations/spec-008-multi-resolution-20260903/
```

Include:

- machine-generated child semantic artifacts;
- generated structure/representation artifacts;
- source-scope metadata;
- live run report;
- comparison against handcrafted references;
- failures/retries;
- human-review template;
- richer-source fixture/results if used.

Keep raw provider payloads only if safe and genuinely useful. Never include secrets.

## Testing Strategy

Add offline deterministic tests covering at least:

- resolution request validation;
- parent focus exists in parent model;
- source-scope construction;
- exact quote resolution against original source;
- ambiguous/missing quote rejection;
- child semantic validation;
- SOURCE evidence integrity;
- INFERRED evidence absence;
- canonical relationship semantics/direction;
- explicit insufficient-source outcome;
- provider failure outcome;
- deterministic fixture extractor path;
- child artifact round-trip;
- downstream structure detection where applicable;
- child representation provenance;
- generated-vs-handcrafted comparison logic;
- navigation artifact preparation;
- no mutation of parent `KnowledgeModel`;
- no mutation of BASELINE-001 artifacts;
- prior tests continue to pass.

## Complexity Budget

SPEC-008 is where recursive-knowledge architecture could easily explode.

Report explicitly:
