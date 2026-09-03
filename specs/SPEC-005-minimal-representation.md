# SPEC-005 — Minimal Representation Experiment

## Status

Ready for implementation.

## Primary Question

> Can a small set of deterministic visual/interactive representations turn `DetectedStructureSet` plus grounded `KnowledgeModel` context into a learning artifact that is materially easier to think with than the underlying text or JSON?

## Purpose

SPEC-001 through SPEC-004 established the pipeline up to higher-order structure detection:

```text
source text
    ↓
KnowledgeModel
    ↓
StructureDetector
    ↓
DetectedStructureSet
```

SPEC-004 demonstrated that the semantic IR can be composed deterministically into useful hierarchies, causal paths, dependency chains, process chains, and feedback candidates without re-reading source text or invoking an LLM.

The project must now test its original product thesis rather than continue improving internal representations indefinitely.

The product is not valuable because it can produce JSON graphs. It is valuable only if those structures can be transformed into representations that materially reduce the cognitive work required to understand a difficult subject.

SPEC-005 therefore introduces the smallest possible **representation layer** and a deliberately minimal human-facing viewer.

This is an experiment in learning usefulness, not a polished application.

## Product Hypothesis

The working hypothesis is:

> A learner can understand explanatory structure more efficiently when important relationships are presented spatially and by semantic role, with progressive access to explanation and source evidence, rather than as a linear source document or raw semantic JSON.

The experiment should test whether the existing architecture can produce the first credible version of:

```text
Map → Model
```

It does **not** yet implement the Simulator stage.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `specs/SPEC-004-structure-detection.md`
8. `debriefs/DEBRIEF-004-structure-detection.md`
9. `src/knowledge_compiler/models.py`
10. `src/knowledge_compiler/relationships.py`
11. `src/knowledge_compiler/structures.py`
12. `src/knowledge_compiler/structure_detection.py`
13. committed SPEC-003 `KnowledgeModel` artifacts
14. committed SPEC-004 detected-structure artifacts and human review

The implementation should begin from accepted repository artifacts, not regenerate semantic extraction.

## Scope

Implement a minimal deterministic representation pipeline that:

1. consumes `KnowledgeModel` plus `DetectedStructureSet`;
2. converts selected detected structures into a presentation-oriented representation model;
3. renders that model in a minimal local browser interface;
4. supports at least hierarchy, causal-path, dependency-chain, process-chain, and feedback-candidate structures when present;
5. preserves semantic relationship labels and direction;
6. preserves provenance from visible relationships back to the original `KnowledgeModel` relationship/evidence;
7. lets the learner inspect a node and an edge without leaving the representation;
8. distinguishes structure type visually or structurally without relying on decorative complexity;
9. makes weak, sparse, or absent structures explicit rather than inventing content;
10. supports the accepted five-domain artifacts without any LLM or network call;
11. produces deterministic representation artifacts suitable for tests and review;
12. enables a small human usefulness evaluation against source text / JSON.

## Explicit Non-Goals

Do not implement in SPEC-005:

- new LLM extraction behavior;
- new relationship predicates;
- relationship-prompt changes;
- event/state/process IR redesign;
- source repair;
- structure repair;
- automatic missing-edge inference;
- URL ingestion;
- Wikipedia integration;
- PDF ingestion;
- YouTube or podcast ingestion;
- accounts;
- authentication;
- persistence/database;
- cloud deployment;
- collaboration;
- saved knowledge libraries;
- full-text search;
- embeddings/vector databases;
- knowledge-atlas navigation across documents;
- mobile application;
- production design system;
- polished branding;
- complex animation;
- quantitative simulation;
- qualitative counterfactual propagation;
- adaptive tutoring;
- quizzes/flashcards;
- LLM-generated explanations in the viewer;
- automatic pedagogical scoring using an LLM judge.

Do not turn this into a general graph-visualization platform.

## Preserve Architecture Boundaries

The intended flow is:

```text
KnowledgeModel ───────────────┐
                              │
DetectedStructureSet ─────────┤
                              ↓
                    RepresentationBuilder
                              ↓
                    RepresentationModel
                              ↓
                        local viewer
```

Important constraints:

- the viewer must not interpret source text independently;
- the viewer must not call an LLM;
- the representation builder must not invent relationships;
- detected structures remain the primary higher-order input;
- `KnowledgeModel` supplies entity descriptions, relationship semantics, claims/evidence context, and provenance;
- representation-specific concerns must not leak backward into `KnowledgeModel` or `StructureDetector`;
- source evidence must remain traceable through the representation.

## Representation Model

Introduce a small presentation-oriented model between detected structures and the viewer.

The exact names are implementation choices, but conceptually it should support something equivalent to:

```text
RepresentationModel
    document_id
    title / domain label if available
    representations[]
    metadata

Representation
    id
    representation_type
    source_structure_id
    title
    nodes[]
    edges[]
    quality / warning metadata

RepresentationNode
    entity_id
    label
    description
    entity_type

RepresentationEdge
    source_entity_id
    target_entity_id
    relationship_type
    relationship_label
    relationship_ids[]
    evidence[]
```

Do not duplicate the entire `KnowledgeModel`. Include only the context required for presentation and provenance.

The model must serialize deterministically to JSON so rendering behavior can be tested independently from browser behavior.

## Representation Mapping

Start with direct, conservative mappings.

### Hierarchy

Detected:

```text
HIERARCHY
```

Represent as a directed tree/DAG-like structure preserving the original semantic relationship (`PART_OF`, `IS_A`, or `EXAMPLE_OF`).

Do not flatten different hierarchy predicates into a generic unlabeled parent/child relationship.

### Causal path

Detected:

```text
CAUSAL_PATH
```

Represent as a directed explanatory chain or branching causal model.

Edges must retain their actual predicates such as:

```text
CAUSES
INCREASES
DECREASES
AFFECTS
CREATES
INDUCES
```

Do not replace them all with a generic arrow meaning “related to.”

### Dependency chain

Detected:

```text
DEPENDENCY_CHAIN
```

Represent directionally while preserving whether the chain is `REQUIRES`, `ENABLES`, or `CONSTRAINS`.

### Process chain

Detected:

```text
PROCESS_CHAIN
```

Represent as ordered chronology using explicit `PRECEDES` semantics.

Do not infer temporal order from layout alone when the relationship does not support it.

### Feedback candidate

Detected:

```text
FEEDBACK_CANDIDATE
```

Represent as a directed loop/cycle.

Because polarity is currently incomplete, label it explicitly as a **feedback candidate** rather than claiming positive/negative/stabilizing/reinforcing behavior.

## Overview vs Detail

The first useful representation should support two levels of inspection:

```text
OVERVIEW
    structure topology
    entity labels
    semantic edge labels

DETAIL
    selected node → description/type
    selected edge → relationship meaning + source evidence
```

This is the smallest useful version of progressive disclosure.

Do not build arbitrary zoom levels or nested atlas navigation yet.

## Interaction Semantics

The viewer should implement the product interaction grammar at minimal depth:

```text
Node click/select
    → What is X?

Edge click/select
    → Why/how does X relate to Y?
    → predicate meaning
    → grounded source evidence

Structure selection
    → Which model/path/hierarchy am I looking at?
```

Paths and loops do not yet need separate interactive reasoning engines; their topology is already represented by the selected structure.

The viewer may use simple panels, accordions, or equivalent lightweight interaction.

## Provenance

Provenance is mandatory.

For every displayed edge, the learner must be able to reach:

```text
visible edge
    ↓
relationship type / meaning
    ↓
KnowledgeModel relationship ID(s)
    ↓
source evidence quote(s)
```

If a detected logical edge collapsed exact duplicate relationships, preserve all supporting relationship IDs and evidence where practical.

Do not fabricate evidence for inferred relationships.

Where no source evidence exists because an item is `INFERRED`, say so explicitly.

## Weak and Empty Structures

SPEC-004 established that empty output can be correct output and that structurally correct patterns can still be pedagogically weak.

The representation layer must therefore distinguish at least:

```text
no detected structure
sparse / weak structure
normal candidate structure
known upstream limitation
```

Do not invent diagrams to fill empty domains.

Examples from SPEC-004:

- Biology currently has no higher-order detected structure. The viewer should say that no supported higher-order structure was detected rather than manufacture one.
- `Light IS_A Electromagnetic wave` is structurally correct but very sparse. It should not dominate the experience merely because it exists.
- The electromagnetism feedback candidate should retain a warning that upstream state collapse weakens its precision if that information is available in evaluation/presentation metadata.

## Presentation Usefulness / Salience

SPEC-004 established that structural validity and pedagogical usefulness are different.

SPEC-005 should introduce only the smallest deterministic salience mechanism needed to prevent trivial structures from dominating presentation.

A simple rule-based mechanism is preferred over a learned score.

Possible inputs include:

```text
edge count
node count
structure type
whether structure is a multi-step path
whether structure is a cycle
known weakness metadata
```

Do not create fake precision such as `pedagogical_score = 83.7`.

A small ordinal category is sufficient if needed, for example:

```text
PRIMARY
SECONDARY
SPARSE
```

The exact vocabulary is an implementation choice.

The mechanism must remain explainable and deterministic.

## Viewer Technology

Choose the smallest browser-based implementation that supports the experiment cleanly.

Constraints:

- local execution;
- minimal dependency footprint;
- no backend service beyond what is necessary to serve the local viewer;
- no Node/npm build pipeline unless there is a strong implementation reason;
- no large frontend framework merely for future extensibility;
- no cloud dependency;
- deterministic data generation must remain separately testable from rendering.

A lightweight Python-served HTML/JS solution is acceptable. A small visualization dependency is acceptable if it materially simplifies directed graph rendering and is justified in the handoff.

Do not hand-build a graph-layout engine merely to avoid one reasonable visualization dependency.

Conversely, do not import a large application framework to render five small diagrams.

## Visual Design Principle

Optimize for **cognitive legibility**, not visual spectacle.

The viewer should make these questions easy to answer:

1. What are the important things?
2. How are they related?
3. Which direction does the relationship go?
4. What kind of relationship is it?
5. What larger pattern am I looking at?
6. Why should I trust this edge?

Avoid:

- force-directed “hairball” graphs when a directed path/tree layout is clearer;
- unlabeled edges;
- decorative gradients/animations;
- excessive color coding;
- dense control panels;
- displaying every entity in the `KnowledgeModel` regardless of selected structure;
- hiding source provenance behind developer-only JSON.

## Golden Demonstrations

The experiment should create inspectable representations from the accepted SPEC-003/SPEC-004 artifacts.

At minimum demonstrate:

### Software architecture

Expected useful representation:

```text
service
  ↑ PART_OF
components
```

and the dependency chain involving order, payment, and database.

This is a strong hierarchy/dependency test.

### Economics

Expected useful representation:

branching causal paths around price, shortage/supply, and quantity response.

This is the strongest causal-model test.

### Electromagnetism

Expected useful representation:

induction feedback candidate plus the sparse light classification if retained.

The representation must not conceal the known changing-field state limitation.

### History

Expected useful representation:

printing enablement chains and chronology.

The chronology endpoint limitation should remain visible rather than repaired.

### Biology

Expected result:

no supported higher-order representation from the current detector output.

The interface should make this absence understandable and still allow inspection of why no structure was selected if practical.

## Human Evaluation

SPEC-005 must include a deliberately small human evaluation.

The primary evaluator for this increment is the project owner/user because the product hypothesis is specifically about whether the representation improves human understanding.

Create a review artifact/template that allows comparison of:

```text
A. source text
B. raw KnowledgeModel / detected structures
C. rendered representation
```

For each of at least three useful domains — preferably software architecture, economics, and electromagnetism — assess:

```text
orientation
relationship clarity
causal/process clarity where applicable
ability to identify important structure
ability to inspect why an edge exists
cognitive load
trust / provenance clarity
overall usefulness
```

Use qualitative ratings such as:

```text
BETTER
SAME
WORSE
```

plus brief observations.

Do not invent psychometric rigor or statistical significance from one evaluator.

The key question is simply:

> Would I rather learn this concept with this representation available than from the source text alone?

The implementation handoff should prepare the artifacts and exact local command needed for this review. The final human verdict should be completed during independent review/debrief, not fabricated by Codex.

## Deterministic Evaluation

In addition to human review, implement offline checks over all five domains.

At minimum verify:

- every displayed representation references a real detected structure;
- every displayed node references a real `KnowledgeModel` entity;
- every displayed edge traces to real supporting relationship IDs;
- relationship labels/types are preserved;
- evidence quotes are copied from validated source spans rather than regenerated;
- representation serialization is deterministic;
- repeated generation is byte-for-byte stable where practical;
- empty-domain behavior is deterministic;
- sparse structures are classified consistently;
- no source text parsing occurs inside representation building;
- no network/LLM dependency is required.

## CLI / Local Run

Provide a straightforward way to build/view a representation from existing artifacts.

The exact command is an implementation choice, but the desired ergonomics are approximately:

```bash
knowledge-compiler represent \
  model.knowledge.json \
  structures.json \
  --output representation.json
```

and/or:

```bash
knowledge-compiler view \
  model.knowledge.json \
  structures.json
```

For the five-domain experiment, provide one simple command that prepares/serves the accepted evaluation set locally.

Do not require the user to manually edit JSON or frontend source to switch domains.

## Evaluation Artifacts

Create a committed evaluation directory, for example:

```text
examples/evaluations/spec-005-minimal-representation-20260903/
```

It should contain deterministic representation JSON for the five domains and any lightweight static/viewer artifacts necessary for independent review.

Also include a machine report summarizing at least:

```text
domain
representations generated
representation types
node/edge counts
salience/weakness classification
provenance completeness
empty-state behavior
```

Do not commit generated dependency caches, virtual environments, browser profiles, screenshots unless they are genuinely needed as evidence.

## Testing Strategy

Normal tests must remain offline and deterministic.

Add tests covering at least:

- representation-model validation;
- mapping for every supported `StructureType`;
- node/edge provenance resolution;
- duplicate-support relationship preservation;
- relationship-label preservation;
- feedback-candidate labeling without unsupported polarity claims;
- sparse/trivial structure handling;
- empty structure-set handling;
- deterministic ordering and IDs;
- deterministic serialization;
- CLI generation;
- local viewer data loading or rendering seam without requiring a real browser where practical;
- all prior tests continue to pass.

Do not make automated browser screenshot testing a prerequisite unless the chosen implementation makes it trivial and stable.

## Acceptance Criteria

SPEC-005 is complete when all are true:

- [ ] A deterministic representation layer exists downstream of `KnowledgeModel` + `DetectedStructureSet`.
- [ ] A small serialized `RepresentationModel` separates presentation concerns from semantic/detection models.
- [ ] Hierarchy, causal path, dependency chain, process chain, and feedback candidate mappings are supported when present.
- [ ] Relationship type and direction remain visible.
- [ ] Nodes expose useful entity context.
- [ ] Edges expose relationship semantics and source provenance.
- [ ] Inferred relationships do not fabricate source evidence.
- [ ] Exact duplicate supporting relationships retain provenance.
- [ ] Weak/sparse structures are not promoted as equally useful to richer structures.
- [ ] Empty structure sets are represented honestly.
- [ ] No LLM or network call is needed for representation generation/viewing.
- [ ] No source-text reinterpretation occurs in the representation layer.
- [ ] Existing relationship vocabulary and semantic extraction remain unchanged.
- [ ] Existing structure detection remains unchanged unless a genuine implementation defect is discovered and reported.
- [ ] Deterministic five-domain representation artifacts are committed.
- [ ] Offline evaluation confirms provenance/reference integrity across the artifacts.
- [ ] A minimal local browser viewer can inspect the representations.
- [ ] Switching among the five evaluation domains is straightforward.
- [ ] A human-review template/artifact and exact review command are provided.
- [ ] Automated tests pass offline.
- [ ] Scope does not expand into ingestion, persistence, simulation, accounts, or product polish.
- [ ] Implementation is committed and pushed to canonical GitHub before handoff.

The primary product acceptance test is intentionally human:

> Does the representation make at least some of the benchmark concepts materially easier to understand and reason about than their source text or raw semantic JSON?

A valid outcome may be **NO**. If the representations are technically correct but cognitively unhelpful, preserve that result rather than polishing the UI until the experiment appears successful.

## Required Handoff to Review

When implementation is complete, Codex must report:

1. architecture implemented;
2. representation model design;
3. mapping from each detected structure type to presentation;
4. salience/weak-structure logic;
5. provenance path from displayed edge to source evidence;
6. viewer technology and dependency rationale;
7. files added/changed;
8. exact automated test result;
9. exact command to generate the five-domain representation artifacts;
10. exact command to launch the local viewer;
11. URL/address the user should open locally, if applicable;
12. per-domain representation counts/types;
13. empty/sparse behavior observed;
14. deterministic/provenance evaluation result;
15. known visual or semantic weaknesses;
16. whether any upstream limitations became more important once rendered;
17. dependencies added;
18. deviations from this SPEC;
19. commit SHA;
20. confirmation that commit is pushed to canonical GitHub.

Do not write `DEBRIEF-005` during implementation. It follows independent review and the user's human usefulness assessment.

Do not modify extraction prompts, relationship vocabulary, or semantic IR merely to make the diagrams look better.

## Operational Learning Capture

SPEC-005 is the first increment where the product owner must directly judge the human-facing result rather than relying primarily on code/evaluation artifacts.

The independent review/debrief should observe:

- whether the repository-centered handoff remains effective for a UI-bearing increment;
- whether deterministic artifacts still make independent review straightforward;
- how much additional friction visual inspection introduces;
- whether human usefulness can be evaluated with a small benchmark rather than broad user research at this stage;
- whether representation exposes upstream semantic defects more clearly than JSON review;
- whether the product should continue toward progressive disclosure or return upstream to event/state modeling;
- whether the representation layer stays thin or begins duplicating semantic logic;
- whether screenshots or other visual evidence should become part of future experiment artifacts.

## Likely Decision After SPEC-005

Do not implement this section during SPEC-005.

If the minimal representations materially improve understanding, the next experiment should likely test **progressive disclosure / explorable models**:

```text
high-level model
    ↓ select node/edge
focused explanation
    ↓
source evidence / deeper submodel
```

If the representations are weak primarily because upstream endpoints/states/events are wrong or missing, the next experiment should instead return to a focused semantic-modeling problem.

If the representations are structurally correct but simply not cognitively useful, reconsider the representation strategy before adding product surface.
