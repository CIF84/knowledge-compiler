# SPEC-011 — Real-Source Quantum Learning Slice

## Status

Ready for implementation.

## Phase

Phase II — prove that the accumulated Knowledge Compiler primitive survives contact with realistic knowledge.

## Primary Question

> Can Knowledge Compiler transform one realistic, substantially richer plain-text source about introductory quantum mechanics into a trustworthy, useful overview with at least one automatically generated deeper semantic resolution that the owner would genuinely prefer to learn from over the original source alone?

## Why This Experiment Now

SPEC-001 through SPEC-010 established the core machinery:

```text
source-grounded extraction
        ↓
canonical semantic relationships
        ↓
structured propositions when binary edges lose truth
        ↓
higher-order structure detection
        ↓
interactive representation
        ↓
structure-aware layout
        ↓
context-preserving semantic navigation
        ↓
automatic bounded semantic-resolution compilation
```

Most evidence, however, comes from small laboratory fixtures.

The largest remaining uncertainty is no longer whether another semantic feature can be implemented. It is whether the **whole accumulated system remains coherent on realistic explanatory material**.

Phase II operating rule:

> **Do not add architecture unless realistic use exposes a concrete failure that requires it.**

SPEC-011 is therefore an end-to-end learning experiment, not an architecture-expansion milestone.

## Learning Goal

The owner wants to begin learning quantum physics.

Bound the learning target to an introductory conceptual slice:

> **Build an intuitive mental model of why quantum mechanics behaves differently from classical mechanics and how quantum state, superposition, probability amplitudes, interference, measurement, uncertainty, and entanglement relate.**

The source need not cover every listed concept equally, and the compiler must not invent missing material merely to satisfy the learning goal.

The learning objective guides source selection and human review; **the source remains the authority for generated knowledge**.

## Experimental Philosophy

This experiment is intentionally different from prior fixture-centric evaluation.

The owner should encounter the resulting artifact primarily as a **learner**, not first as a schema reviewer.

Machine/repository review still happens before subjective acceptance, but do not optimize the generated model to reproduce a predetermined expected graph.

The decisive question is experiential:

> **If I genuinely wanted to understand this material, would I rather learn through this compiled knowledge space than through the original source alone?**

## Source Selection

Use one real, coherent, reputable, explanatory plain-text source on introductory conceptual quantum mechanics.

### Desired source properties

Prefer material that:

- is substantially richer than current benchmark fixtures;
- is roughly article/chapter scale rather than a few paragraphs;
- contains meaningful conceptual interdependence;
- contains enough mechanistic explanation for at least one deeper semantic resolution;
- discusses several of the target concepts naturally;
- is understandable without advanced graduate-level prerequisites;
- is explanatory rather than primarily historical or journalistic;
- contains enough source-local context that external enrichment should not be necessary for the primary experiment.

### Approximate scale

Target roughly **5,000–15,000 words** if a suitable source exists.

This is guidance, not a hard acceptance threshold. Prefer conceptual coherence over hitting a word count.

### Source acquisition

The source may be selected from a publicly accessible reputable educational/scientific source.

Examples of acceptable source categories:

- reputable university educational material;
- open textbook chapter;
- reputable scientific/educational institution;
- high-quality public reference material with coherent exposition.

Do not use random AI-generated prose as the benchmark source.

### Copyright / repository constraint

Do **not** commit a copyrighted long-form source to the repository unless its license clearly permits redistribution.

Prefer an openly licensed/public-domain source where practical.

If the best benchmark source cannot legally/safely be redistributed:

- preserve source metadata and URL/reference information;
- keep only the minimum local evaluation material permitted;
- do not commit the full text;
- ensure evaluation artifacts do not reproduce large portions of copyrighted text;
- exact evidence excerpts should remain limited to what is needed for provenance/review.

The implementation handoff must state the source, license/redistribution basis, and how the local source material was handled.

## Consent / External Transmission

If a live provider evaluation requires sending the selected source text or substantial excerpts to OpenAI, obtain explicit owner approval immediately before the first live transmission if required by the current workflow/policy.

No data should be transmitted before that approval.

## Experimental Boundary

SPEC-011 should exercise the current system as much as possible **without broad redesign**.

Expected conceptual flow:

```text
REAL QUANTUM SOURCE
        ↓
SourceDocument
        ↓
existing extraction boundary
        ↓
KnowledgeModel
  ├── entities
  ├── relationships
  ├── claims
  ├── propositions where required
  └── provenance
        ↓
StructureDetector
        ↓
RepresentationBuilder
        ↓
structure-aware layout
        ↓
useful orientation representation
        ↓
select one promising concept
        ↓
ResolutionCompiler
        ↓
automatically generated child resolution
        ↓
Contextual/Layers viewer
        ↓
owner learns from artifact
```

## No Predetermined Golden Graph

Do not encode a large expected quantum ontology or force the source into a hand-authored conceptual map.

The experiment should discover what the existing compiler produces.

Small evaluation expectations are acceptable for integrity, such as:

- source provenance is valid;
- important source concepts are not systematically absent;
- unsupported concepts are not invented;
- selected child resolution remains source-grounded;
- parent/child relationship is coherent;
- output remains inspectable.

Human semantic review determines usefulness.

## Real-Source Scale Handling

The current extraction path was developed on small sources. SPEC-011 may expose context/scale limits.

Do not immediately build a generalized chunking/retrieval architecture.

First attempt the simplest safe approach supported by the existing provider/model/context window.

If the full source cannot be processed reliably or within practical provider limits, record the concrete failure.

A **minimal bounded segmentation strategy** is allowed only if necessary to make this single-source experiment possible.

If segmentation is introduced, it must:

- be deterministic;
- preserve original source coordinates;
- preserve evidence provenance;
- avoid silently duplicating entities/relationships across segments;
- have an explicit merge/reconciliation boundary;
- remain narrowly scoped to the observed scale failure;
- not become a general retrieval/vector architecture.

Report whether segmentation was actually necessary.

## Orientation / Overview Requirement

The compiled source should produce a learner-usable orientation surface.

Do not require one giant graph containing every extracted entity.

Use existing structure/salience/representation machinery to expose the smallest useful orientation available from the current architecture.

The owner should be able to answer approximately:

```text
What are the major ideas in this source?
How are they related?
Where am I in the topic?
What looks worth exploring next?
```

If the current representation machinery cannot produce such an overview from the richer source, preserve that failure. Do not solve it with hand-authored curation during the primary experiment.

## Semantic Zoom Requirement

Attempt at least **one automatically generated deeper semantic resolution** from the compiled source.

Prefer a concept where the source contains enough explanatory detail and where deeper resolution would materially help learning.

Candidate concepts may include, if present and sufficiently supported:

```text
quantum state
superposition
interference
measurement
probability amplitude
uncertainty
entanglement
```

Do not hard-code one concept before inspecting the actual compiled source.

### Strategy selection

Use the existing `ResolutionStrategy` boundary.

Do not add a new strategy merely because the topic is quantum mechanics.

If no existing type-aware strategy is justified, use `GENERIC_DETAIL` and record the limitation.

If a concept naturally maps to an existing strategy, use it only when semantically appropriate.

### Child success criteria

A useful child should:

- remain centered on the selected parent concept;
- expose genuinely finer explanatory structure rather than paraphrasing the parent;
- remain source-grounded;
- preserve proposition truth where relevant;
- plausibly compress back into the parent concept;
- render through existing downstream representation/navigation machinery.

A truthful `INSUFFICIENT_SOURCE_DETAIL` is a valid result.

## Proposition Handling

Use the SPEC-010 hybrid rule:

> Binary relationships remain the default. Structured propositions are used only when a binary edge would necessarily lose proposition truth.

Do not expand proposition types/operators/roles speculatively.

If the quantum source repeatedly exposes a proposition form the current model cannot represent truthfully, preserve examples and report the gap.

Do not add new proposition semantics unless the experiment is blocked and the smallest possible addition is clearly justified by repeated source evidence.

## Relationship Vocabulary

Keep the canonical 20 predicates unchanged by default.

Do not add quantum-specific predicates.

If repeated source propositions cannot be represented honestly with the existing vocabulary, report the vocabulary gap rather than forcing misleading edges.

## Structure Detection

Use existing deterministic structure detection unchanged unless a concrete failure prevents the experiment from producing any meaningful representation.

Do not introduce a general graph engine, clustering framework, embedding model, or community-detection architecture merely because the real source is larger.

If structure detection produces too many, too few, or fragmented structures, preserve diagnostics. That may be the experimental finding.

## Representation and UI

Use the existing validated representation/layout/viewer system.

Do not redesign navigation in SPEC-011.

Known interaction weakness is explicitly accepted:

```text
Explore / Back
```

is experimental scaffolding and is less elegant than the desired future map-navigation grammar.

Do not fix it here.

Likewise, do not implement:

- active parent-map navigation;
- lateral pan semantics;
- zoom gestures;
- new breadcrumbs;
- Journey/course mode;
- animation/storytelling;
- cognitive-preset personalization.

If realistic source scale makes the current navigation materially unusable, record that as evidence for the next experiment.

## Explore / Journey Vision Snapshot

Preserve, but do not implement, the emerging interaction vision:

```text
                  COMPILED KNOWLEDGE SPACE
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
              EXPLORE             JOURNEY
        learner chooses route   system proposes route
                 │                   │
                 └─────────┬─────────┘
                           ↓
                    same topology
```

Working product language:

> **Knowledge Compiler builds the map. You can explore it yourself, or ask it to take you somewhere.**

SPEC-011 tests the **terrain**, not route generation.

## Learning Review Procedure

After technical/repository integrity review, the owner should use the artifact as a learner.

### Important ordering

Do not begin owner review with a large machine-quality report or expected-concept checklist.

First provide:

1. the original source or source reference;
2. the exact command to launch the compiled artifact;
3. a minimal instruction such as: **“Use this to try to understand the topic.”**

Capture spontaneous reaction before structured questioning.

### Then evaluate

#### Orientation

- Can I quickly see what the source is fundamentally about?
- Do I understand the major conceptual neighborhoods?
- Does the map reduce the burden of mentally reconstructing structure from prose?

#### Semantic usefulness

- Are the displayed relationships meaningful rather than merely technically grounded?
- Do proposition cards preserve distinctions that simple edges would lose?
- Does the representation omit something central?
- Does anything important look misleading?

#### Semantic zoom

- Does the deeper resolution genuinely feel like peeling another layer?
- Does the parent remain a plausible compression of the child?
- Does the deeper model help rather than merely add information?

#### Evidence / trust

- Can I inspect why an important relationship exists?
- Does source evidence increase confidence without overwhelming the learning experience?

#### Learning preference

The decisive subjective question:

> **For this material, would I prefer to continue learning through Knowledge Compiler, the original source, or a conventional AI textual explanation? Why?**

Do not claim measured learning efficacy from this review.

## Machine Evaluation

Machine evaluation should focus on integrity and scale diagnostics, not pretend to score learning.

Report at least:

```text
source identity / provenance
source word and character count
provider/model/prompt versions
source processing strategy
segment count if any
input/output token usage
entity count
relationship count
claim count
proposition count
SOURCE vs INFERRED counts
grounding failures
validation failures
deduplication diagnostics
structure counts by type
representation counts/salience
layout diagnostics
selected zoom focus
resolution strategy
child outcome
child entity/relationship/claim/proposition counts
child grounding/provenance integrity
parent immutability
runtime/cost where authoritative
```

Also record useful scale ratios such as relationships/entities and represented/extracted entities, but do not invent quality thresholds from them.

## Failure Attribution

If the vertical slice is weak, attribute the failure before changing architecture.

Use categories such as:

```text
SOURCE_SELECTION
SOURCE_SCALE / CONTEXT
EXTRACTION
GROUNDING
SEMANTIC_RELATIONSHIP
PROPOSITION_MODEL
DEDUPLICATION
STRUCTURE_DETECTION
OVERVIEW / SALIENCE
REPRESENTATION
LAYOUT
SEMANTIC_RESOLUTION
NAVIGATION
HUMAN_USEFULNESS
```

Multiple categories may apply.

The purpose of SPEC-011 is partly to discover **which layer breaks first under realistic load**.

## Live Provider Discipline

Normal tests remain offline and deterministic.

For live evaluation:

- use explicit provider/model versions;
- preserve run history;
- no hidden retries;
- no silent prompt repair;
- no cherry-picking;
- no external semantic enrichment during the primary experiment;
- if a retry is required for provider/transient failure, record it explicitly and distinguish it from semantic retries;
- do not weaken validation to obtain a successful artifact.

## Source Truth vs External Knowledge

Quantum mechanics is a domain where the model may possess substantial pretrained knowledge.

The experiment specifically tests compilation of **the selected source**.

Therefore:

- do not ask the model to supplement missing explanations from general knowledge;
- do not use web retrieval to fill semantic gaps during compilation;
- unsupported but scientifically correct model knowledge is still unsupported for this experiment;
- source-grounded incompleteness is preferable to ungrounded completeness.

## Existing Baselines

Preserve:

- `BASELINE-001` as the accepted cognitive-interaction comparison baseline;
- SPEC-007 A/B/C experimental modes where existing infrastructure requires them;
- SPEC-008/009 generated-resolution evidence;
- SPEC-010 proposition semantics.

Do not overwrite prior evaluation artifacts.

## Explicit Non-Goals

Do not implement:

- PDF ingestion;
- URL ingestion as a product feature;
- Wikipedia adapter;
- YouTube/podcast ingestion;
- OCR;
- vector database;
- embeddings retrieval architecture;
- persistent knowledge atlas;
- recursive unlimited semantic zoom;
- active map-navigation redesign;
- Journey/course generation;
- learning-path planning;
- personalization engine;
- cognitive-preset recommendation;
- simulator;
- quantitative quantum simulation;
- equation solver;
- general mathematical notation engine;
- universal proposition ontology;
- broad relationship-vocabulary expansion;
- frontend framework migration;
- mobile/responsive redesign;
- accounts/database/cloud deployment;
- formal multi-user learning study.

## Testing Strategy

Keep the full offline suite passing.

Add only tests required by any minimal real-source handling introduced by this SPEC.

If no product code change is required to run the vertical slice, prefer evaluation artifacts/harness additions over unnecessary architecture.

Potential focused tests if relevant:

- realistic SourceDocument normalization;
- source-coordinate preservation at larger scale;
- segmentation boundary behavior if segmentation becomes necessary;
- merge/deduplication across segments if used;
- proposition round-trip on real-source-derived fixtures;
- deterministic evaluation-report generation;
- generated child navigation artifact integrity;
- no mutation of prior baselines/evaluations.

## Evaluation Artifacts

Create a committed evaluation directory such as:

```text
examples/evaluations/spec-011-quantum-real-source-<date>/
```

Keep artifacts sufficient for reconstruction and review without unnecessarily duplicating copyrighted source material.

Likely artifacts:

```text
source-metadata.json
processing-report.json
parent.knowledge.json
parent.structures.json
parent.representation.json
resolution-result.json
child.knowledge.json            if successful
child.structures.json           if successful
child.representation.json       if successful
generated-exploration.json      if successful
report.json
run-history.json
repository-semantic-review.json
human-review-template.json
README.md                       if needed for launch/reconstruction
```

Artifact names may differ if existing evaluation conventions provide a cleaner fit.

## Acceptance Criteria — Technical

- [ ] One realistic coherent quantum-mechanics source is selected and provenance recorded.
- [ ] Source redistribution/licensing handling is explicit and safe.
- [ ] The source is materially richer than existing tiny benchmark fixtures.
- [ ] The source is normalized through `SourceDocument`.
- [ ] Real extraction uses the existing provider boundary.
- [ ] Evidence grounding remains exact/fail-closed.
- [ ] Existing canonical relationship semantics remain authoritative.
- [ ] SPEC-010 proposition semantics remain available.
- [ ] No unsupported source enrichment is