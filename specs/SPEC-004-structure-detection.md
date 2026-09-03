# SPEC-004 — Structure Detection

## Status

Ready for implementation.

## Primary Question

> Can the current grounded `KnowledgeModel` be composed deterministically into useful higher-order structures — hierarchies, causal paths, temporal/process chains, dependency structures, and feedback candidates — without re-reading the source text?

## Purpose

The project has now established three foundations:

```text
SPEC-001  a source-grounded semantic IR is viable
SPEC-002  a real LLM can populate that IR across multiple domains
SPEC-003  explicit relationship semantics materially improve edge truthfulness
```

The next architectural assumption is that useful learning structures can be derived from the semantic graph itself.

This matters because the product thesis is not merely:

```text
text → graph
```

It is:

```text
Source → Structure → Model → Intuition
```

SPEC-004 therefore tests whether the existing semantic IR is already rich enough to expose larger explanatory patterns without introducing another LLM interpretation pass or re-reading the source text.

This is a deterministic graph-analysis experiment.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `debriefs/DEBRIEF-003-relationship-semantics.md`
8. `specs/SPEC-003-relationship-semantics.md`
9. current `KnowledgeModel`, relationship registry, evaluation fixtures, and tests

Treat DEBRIEF-003 as the accepted baseline.

Important carried decisions:

- `KnowledgeModel` remains the semantic IR;
- relationship semantics come from the canonical provider-independent registry;
- relationship vocabulary is frozen for now;
- prefer truthful incompleteness over invented semantics;
- downstream reasoning should consume `KnowledgeModel`, not raw source text;
- remaining endpoint/state/polarity issues are known constraints, not automatic blockers.

## Experiment Hypothesis

The working hypothesis is:

> Explicit semantic relationships can be composed into deterministic higher-order structures that are useful enough to justify a future representation layer.

Examples:

```text
A PART_OF B
C PART_OF B
        ↓
   HIERARCHY

A CAUSES B
B AFFECTS C
        ↓
  CAUSAL PATH

A PRECEDES B
B PRECEDES C
        ↓
 PROCESS CHAIN

A REQUIRES B
B REQUIRES C
        ↓
DEPENDENCY CHAIN

A CAUSES B
B CAUSES C
C AFFECTS A
        ↓
FEEDBACK CANDIDATE
```

The important word is **candidate**. Structure detection should preserve the semantics and uncertainty already present in the graph; it must not invent unsupported domain truth.

## Scope

Implement a deterministic structure-detection layer that consumes only `KnowledgeModel` and canonical relationship semantics and can identify at least:

1. structural hierarchies;
2. causal paths;
3. temporal/process chains;
4. dependency chains;
5. feedback candidates;
6. connected semantic subgraphs useful as system-level groupings, only if a minimal deterministic definition is justified.

Also implement:

- typed output models for detected structures;
- provenance back to the underlying relationship IDs;
- deterministic ordering;
- conservative duplicate suppression;
- offline tests across multiple domains;
- a CLI or equivalent inspectable artifact path for running detection on existing `KnowledgeModel` JSON;
- fixture/golden outputs for representative models;
- a five-domain evaluation using the accepted SPEC-003 generated models as inputs, without new LLM calls;
- explicit reporting of structures found, missed, and misleading structures caused by known upstream semantic imperfections.

## Explicit Non-Goals

Do not implement in SPEC-004:

- graph visualization;
- web or Streamlit UI;
- interactive exploration;
- source-text re-reading during detection;
- new LLM calls for structure detection;
- relationship-vocabulary expansion;
- prompt changes;
- source ingestion changes;
- PDF/audio/video/web ingestion;
- graph database persistence;
- embeddings;
- clustering via vector similarity;
- community-detection frameworks unless a tiny deterministic use is clearly necessary;
- quantitative simulation;
- qualitative what-if simulation;
- progressive disclosure UX;
- learning recommendations;
- event/state/entity redesign unless a concrete structure-detection blocker proves it necessary;
- ontology redesign;
- automatic semantic repair of bad upstream edges.

Do not solve presentation in this increment.

## Architectural Boundary

Introduce a new downstream layer conceptually equivalent to:

```text
KnowledgeModel
      ↓
StructureDetector
      ↓
DetectedStructureSet
```

The detector must not depend on:

- raw source text;
- the OpenAI SDK;
- provider-specific metadata;
- prompt code;
- visualization libraries.

It may depend on:

- `KnowledgeModel`;
- `RelationshipType`;
- canonical relationship definitions/families;
- standard-library graph logic or a very small justified dependency.

Prefer standard-library implementation unless an external graph library clearly reduces complexity without changing the architecture.

Do not introduce NetworkX merely because this is graph-shaped. The structures required here are simple enough that adjacency maps and deterministic traversal may be preferable. If a dependency is added, justify it in the handoff.

## Output Model

Create one provider-neutral typed representation for detected structures.

The exact names are implementation choices, but the output should express at least:

```text
structure id
structure type
ordered or unordered entity IDs as appropriate
supporting relationship IDs
confidence / certainty basis if useful
detection metadata
```

A possible conceptual model:

```python
StructureType:
    HIERARCHY
    CAUSAL_PATH
    PROCESS_CHAIN
    DEPENDENCY_CHAIN
    FEEDBACK_CANDIDATE

DetectedStructure:
    id
    structure_type
    entity_ids
    relationship_ids
    metadata
```

Do not encode UI layout, coordinates, colors, labels for rendering, or prose summaries into this layer.

The structure model should represent **what pattern exists in the semantic graph**, not how it will be displayed.

## Relationship-Family Mapping

Structure detection should derive its semantics from the canonical relationship registry rather than duplicating an independent hard-coded ontology where practical.

Expected family usage:

```text
STRUCTURAL
    hierarchy candidates

CAUSAL
    causal paths and feedback candidates

DEPENDENCY
    dependency chains

TEMPORAL
    process / chronology chains

INTERACTION
    potentially useful context, but not automatically causal

TRANSFORMATION
    may participate in process chains when semantically appropriate

DESCRIPTIVE
    generally not chain-forming unless a concrete use is justified
```

Do not treat every relationship family as transitively composable.

For example:

```text
A BINDS_TO B
B BINDS_TO C
```

does not imply a meaningful three-step process merely because the graph is connected.

Likewise:

```text
A AFFECTS B
B AFFECTS C
```

supports a causal/influence path, but not necessarily the stronger claim that A directly causes C.

Detected structures must preserve the original edge semantics rather than collapsing them into stronger derived claims.

## Hierarchy Detection

At minimum, use structural edges such as:

```text
PART_OF
IS_A
EXAMPLE_OF
```

but do not combine them indiscriminately into one semantic hierarchy.

The detector should distinguish different structural meanings where necessary.

Examples:

```text
component PART_OF system
subtype IS_A type
instance EXAMPLE_OF concept
```

A useful output may be a tree/forest or connected structural chain, but do not force a tree if the graph naturally forms a DAG.

Requirements:

- preserve relationship types;
- preserve direction;
- handle multiple roots;
- avoid infinite traversal on malformed cycles;
- deterministic output order.

## Causal Path Detection

Use relationship semantics from the causal family.

Likely chain-forming predicates include:

```text
CAUSES
AFFECTS
INCREASES
DECREASES
INDUCES
```

`EXERTS_FORCE_ON` is an interaction predicate and must not automatically be treated as equivalent to a causal edge unless the existing graph contains a separate causal relation.

The detector should identify meaningful multi-edge paths without asserting transitive equivalence.

For example:

```text
A CAUSES B
B DECREASES C
```

may be represented as a causal path:

```text
A → B → C
```

with original predicate sequence retained:

```text
[CAUSES, DECREASES]
```

Do not derive a new `A CAUSES C` relationship.

Avoid path explosion. Use a bounded and explicit rule such as:

- minimum length: 2 relationships;
- maximum length: choose a small justified value, e.g. 4 or 5;
- report maximal/non-redundant paths where practical.

Document the chosen strategy.

## Temporal / Process Chain Detection

At minimum use `PRECEDES` edges.

The detector should identify ordered sequences such as:

```text
A PRECEDES B
B PRECEDES C
```

and emit an ordered process/temporal chain.

Transformation relationships may be included only if a deterministic semantic rule justifies composition with temporal edges.

Do not infer chronological order from causal direction alone.

Do not infer missing `PRECEDES` relationships from source order or entity order.

Known limitation from SPEC-003: biology sometimes fails to extract explicit chronology. SPEC-004 must report the resulting missing structure rather than repairing it from raw text.

## Dependency Detection

Use dependency-family relationships such as:

```text
REQUIRES
ENABLES
CONSTRAINS
```

but preserve their different meanings.

A dependency chain should show dependency topology, not erase edge semantics.

For example:

```text
service REQUIRES database
operation REQUIRES service
```

may form:

```text
operation → service → database
```

with both `REQUIRES` edges retained.

Be cautious with `ENABLES` direction because its semantic direction differs conceptually from `REQUIRES`.

Do not merge opposite dependency semantics into a single transitive assertion.

The output can identify a dependency structure while preserving the actual predicate sequence.

## Feedback Candidates

Feedback detection is intentionally conservative.

A feedback candidate exists when a directed cycle is present through causal-family edges.

For example:

```text
A AFFECTS B
B INCREASES C
C DECREASES A
```

forms a causal cycle.

The detector should:

- detect directed causal cycles;
- canonicalize cycles so the same cycle is not emitted repeatedly from different starting nodes;
- preserve original relationship IDs and predicate sequence;
- label the output **FEEDBACK_CANDIDATE**, not proven feedback loop;
- avoid classifying cycles containing only structural, descriptive, or symmetric interaction edges as feedback.

Do not infer reinforcing vs balancing polarity in SPEC-004 unless it can be determined strictly from existing predicates without ambiguity.

`INCREASES` and `DECREASES` contain polarity information, but `CAUSES` and `AFFECTS` do not. Mixed cycles therefore often cannot be classified safely.

## Duplicate and Redundancy Handling

SPEC-003 exposed duplicate relationships in some live models.

Structure detection should not multiply identical higher-order structures merely because equivalent duplicate edges exist.

Implement conservative structure-level canonicalization.

Do not silently rewrite or delete the upstream `KnowledgeModel`.

If two distinct relationship IDs express the same source/type/target triple, the detector may treat them as equivalent for path/cycle discovery while preserving all supporting IDs in metadata if useful.

Do not perform semantic similarity deduplication.

## Determinism

Given the same `KnowledgeModel`, structure detection output must be byte-for-byte stable after serialization, assuming stable serialization settings.

Ensure deterministic:

- entity traversal order;
- relationship traversal order;
- path ordering;
- cycle canonicalization;
- generated IDs;
- JSON output order where project conventions support it.

This is important because SPEC-004 is intended to create a trusted deterministic layer downstream of probabilistic extraction.

## Provenance

Every detected structure must point back to the relationships that support it.

Minimum requirement:

```text
DetectedStructure.relationship_ids
```

From those relationships, downstream code must be able to recover the existing entity and source evidence provenance.

Do not copy raw source spans unnecessarily into the detected structure unless it materially simplifies the architecture.

Preferred chain:

```text
DetectedStructure
      ↓
relationship IDs
      ↓
KnowledgeModel relationships
      ↓
evidence spans
      ↓
SourceDocument
```

This preserves one provenance source of truth.

## Five-Domain Evaluation

Use the committed SPEC-003 live models as deterministic inputs:

```text
examples/evaluations/spec-003-relationship-semantics-20260903/
```

Specifically the five `*.knowledge.json` models.

Do **not** make new LLM calls for the primary SPEC-004 evaluation.

For each domain, run structure detection and save inspectable output under a new directory such as:

```text
examples/evaluations/spec-004-structure-detection-20260903/
```

The exact path may vary, but do not overwrite SPEC-003 artifacts.

## Evaluation Questions

For each domain, assess at minimum:

```text
hierarchies found
causal paths found
temporal/process chains found
dependency structures found
feedback candidates found
useful structures found
expected structures missed
misleading structures produced
failures attributable to detector logic
failures attributable to upstream KnowledgeModel quality
```

Use qualitative verdicts:

```text
GOOD
MIXED
POOR
NOT_APPLICABLE
```

Do not create a fake aggregate precision score unless the fixtures become formally labeled enough to support one.

## Golden Expectations

Add a small deterministic expectation layer for the five domains.

At minimum encode a handful of load-bearing expected structures based on the accepted SPEC-003 models, not the original raw source.

Examples conceptually:

### Electromagnetism

Expect at least one causal/mechanistic path connecting field/force/motion concepts where the actual SPEC-003 graph supports it.

Do not invent changing-field entities that are absent upstream.

### Software architecture

Expect structural hierarchy from `PART_OF` edges and useful dependency paths from `REQUIRES`/related edges where present.

### Economics

Expect causal paths involving price, supply/demand, shortage/surplus where supported by the SPEC-003 graph.

### Biology

Expect interaction edges to remain context, not be falsely composed as causal paths. Detect temporal/process structure only if the upstream model actually contains `PRECEDES`.

### History

Expect chronology from the improved `PRECEDES` edge(s), but expose limitations caused by actor/event endpoint imprecision.

The expectations should test structure detection, not re-litigate whether SPEC-003 extraction was perfect.

## Fixture Strategy

Add focused synthetic `KnowledgeModel` fixtures specifically for deterministic graph behavior.

Include at least:

1. clean hierarchy / DAG;
2. simple causal chain;
3. branching causal graph;
4. temporal chain;
5. dependency chain;
6. simple directed causal cycle;
7. duplicate-edge case;
8. non-causal graph that must not become feedback;
9. mixed relationship-family graph;
10. disconnected graph.

These fixtures should make algorithmic behavior testable independently of LLM quality.

## CLI / Inspection Surface

Provide a simple way to run structure detection against an existing `KnowledgeModel` JSON.

Conceptually:

```bash
knowledge-compiler detect-structures model.knowledge.json --output structures.json
```

The exact command name may vary if current CLI conventions strongly suggest another shape.

Requirements:

- no network access;
- no API key;
- reads existing model JSON;
- validates input using existing domain model;
- emits deterministic JSON;
- clear non-zero failure on invalid input.

Do not build a rich interactive CLI.

## Suggested Module Shape

The exact structure is up to Codex, but a small design may resemble:

```text
src/knowledge_compiler/
    structures.py
    structure_detection.py
```

Possible responsibilities:

```text
structures.py
    StructureType
    DetectedStructure
    DetectedStructureSet
    serialization / validation

structure_detection.py
    adjacency construction
    hierarchy detection
    path detection
    cycle detection
    canonicalization
    StructureDetector
```

Avoid excessive abstractions. One or two modules are sufficient if they remain clear.

## Testing Strategy

All SPEC-004 tests must be deterministic and offline.

Test at least:

- hierarchy detection;
- multiple hierarchy roots;
- structural cycles do not hang;
- causal path detection;
- path length boundaries;
- branching-path canonicalization;
- temporal chain ordering;
- dependency-chain behavior with differing predicate directions;
- causal cycle / feedback-candidate detection;
- same cycle emitted once regardless of starting node;
- non-causal cycle does not become feedback;
- duplicate input edges do not duplicate detected structures;
- disconnected components handled correctly;
- provenance relationship IDs preserved;
- stable IDs/order across repeated runs;
- serialization round-trip;
- CLI success/failure behavior;
- five-domain evaluation can run entirely offline from committed SPEC-003 models.

Retain all prior tests.

## Semantic Safety Rules

The detector must follow these principles:

### 1. Compose; do not reinterpret

The detector may identify graph patterns from existing edges. It must not decide that an upstream relationship means something different from its canonical contract.

### 2. Do not create stronger derived facts

A path:

```text
A AFFECTS B
B CAUSES C
```

may be represented as a causal path, but must not create a new asserted edge:

```text
A CAUSES C
```

### 3. Preserve predicate sequence

Higher-order structures must retain which predicates make up the path or cycle.

### 4. Missing input means missing structure

If chronology, event, state, or polarity information is absent upstream, report the resulting limitation. Do not reconstruct it from raw text or external knowledge.

### 5. Known bad upstream edges are evidence, not detector bugs

Evaluation should distinguish:

```text
detector error
vs
faithful composition of an imperfect upstream graph
```

This distinction is a core purpose of SPEC-004.

## Acceptance Criteria

SPEC-004 is complete when all are true:

- [ ] A provider-neutral deterministic structure-detection layer consumes `KnowledgeModel` only.
- [ ] Typed detected-structure output exists and is serializable/validatable.
- [ ] Hierarchy detection is implemented.
- [ ] Causal path detection is implemented.
- [ ] Temporal/process-chain detection is implemented.
- [ ] Dependency-structure detection is implemented.
- [ ] Directed causal cycles are emitted conservatively as feedback candidates.
- [ ] Original relationship types and supporting relationship IDs are preserved in detected structures.
- [ ] Duplicate relationships do not cause duplicate higher-order structures.
- [ ] Output is deterministic across repeated runs.
- [ ] No new LLM calls are required for detection or primary evaluation.
- [ ] No source-text re-reading occurs in the detector.
- [ ] Relationship vocabulary remains unchanged unless a genuine blocker forces a documented deviation.
- [ ] Focused synthetic graph fixtures cover core algorithms.
- [ ] Existing SPEC-003 five-domain models are used for offline evaluation.
- [ ] Evaluation distinguishes detector failures from upstream semantic limitations.
- [ ] An inspectable CLI/artifact path exists for structure detection.
- [ ] All normal tests pass offline.
- [ ] No visualization, UI, persistence, simulation, or unrelated architecture is introduced.
- [ ] Implementation is committed and pushed to canonical GitHub before handoff.

The primary qualitative acceptance test is:

> Do the detected structures reveal useful larger-scale organization already latent in the semantic graph, with enough fidelity that building a representation layer would now be justified?

A valid result may be **NO**. If the current IR does not support useful structure detection, preserve that result and identify the concrete missing semantic information rather than repairing it ad hoc.

## Required Evaluation Artifact

Commit an inspectable human review for SPEC-004, separate from machine output.

It should answer:

1. Which structure types worked reliably?
2. Which domains produced genuinely useful structures?
3. Which expected structures were absent because upstream edges were missing?
4. Which structures were technically correct but pedagogically weak?
5. Did known endpoint/state problems materially block composition?
6. Did structure detection expose a concrete need for event/state modeling?
7. Is the current IR sufficient to proceed to representation/UI experimentation?

Do not write `DEBRIEF-004`. That remains the independent-review step after implementation.

## Required Handoff to Review

When implementation is complete, Codex must report:

1. architecture implemented;
2. detected-structure data model;
3. detection algorithms for each structure type;
4. relationship-family/type mapping used;
5. canonicalization/deduplication approach;
6. deterministic-ordering strategy;
7. files added/changed;
8. exact automated test result;
9. CLI command for structure detection;
10. five-domain evaluation command;
11. counts/types of structures found per domain;
12. useful findings per domain;
13. expected structures missed;
14. misleading structures produced;
15. detector failures vs upstream-model limitations;
16. whether event/state/polarity limitations became blockers;
17. dependencies added, if any, and justification;
18. deliberate deviations from this SPEC;
19. commit SHA;
20. confirmation that the commit is pushed to canonical `origin/main`.

Do not write `DEBRIEF-004` during implementation.

## Operating Learning Capture

SPEC-004 should also observe the development process.

In the eventual independent debrief, assess:

- whether moving from probabilistic extraction to deterministic graph analysis reduced implementation/review ambiguity;
- whether the relationship-family metadata from SPEC-003 materially simplified downstream reasoning;
- whether project memory remained sufficient for a short Codex handoff prompt;
- whether human semantic review remains the dominant cognitive cost;
- whether the current SPEC/debrief cadence is still proportionate to learning value;
- whether the five-domain corpus is now sufficiently mature to become a durable regression suite.

## Likely Decision After SPEC-004

Do not implement this section during SPEC-004.

If the current IR yields useful higher-order structures, the next likely experiment should expose those structures through the first minimal representation layer.

That would begin testing the original product proposition:

> Paste difficult text. Get a model you can think with.

The likely future sequence would become:

```text
KnowledgeModel
      ↓
Detected structures
      ↓
minimal interactive representation
      ↓
progressive disclosure
      ↓
qualitative simulator
```

If structure detection instead fails because entity/event/state distinctions are insufficient, the next experiment should address that specific semantic-model deficiency before visualization.
