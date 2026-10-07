# Knowledge Compiler — Project Vision

## Vision

**Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.**

The project is moving toward a compiler that can expose the same grounded knowledge at different levels of detail and in different appropriate forms. This direction is broader than the capabilities implemented today: it is a durable architectural commitment, not a claim that arbitrary media, learners, subjects, or output formats are already solved.

## Mission

Build the smallest trustworthy compiler architecture that can:

1. extract grounded knowledge;
2. preserve claims, relationships, evidence, scope, uncertainty, qualifications, and provenance;
3. expose the same knowledge at progressively compressed resolutions;
4. make compression a reversible view-layer operation over a richer semantic substrate rather than destructive chained summarization;
5. use prose when prose is cognitively efficient;
6. use structural or perceptual representation only when it reduces cognitive work; and
7. eventually support different goals, prior knowledge, time budgets, and output media from one grounded substrate.

## Architectural direction

```text
INGESTION
text / document / possible future audio or video
        ↓
GROUNDED EXTRACTION
trusted claims / relationships / evidence / provenance
        ↓
EXPLANATORY STRUCTURE
meaning blocks / explanatory functions / supported traversal
        ↓
CONCEPTUAL ORGANIZATION
supported chunks / schema / necessary implications
        ↓
GOAL-PRESERVING SEMANTIC COMPRESSION
multiple non-destructive resolutions over one richer substrate
        ↓
REPRESENTATION SELECTION
concise prose / enriched prose / structural or perceptual form
        ↓
LEARNER-FACING RESOLUTION AND MEDIA
an appropriate view for a future task, context, or time budget
```

The central rule is:

> **Compression is a view over knowledge, not destruction of knowledge.**

The learner-exposure boundary is equally explicit:

> **Intermediate representation is not learner representation. Internal schema must be compiled through a separate cognitive-utility boundary before exposure.**

```text
grounded semantics
→ explanatory structure
→ conceptual schema (IR)
→ cognitive representation compiler
→ learner representation
```

Its preservation boundary is broader than modeled domain facts:

> **Semantic preservation is necessary but not sufficient; useful explanatory structure is itself information that compression should preserve.**

Compression can reduce different kinds of burden. Linguistic compression reduces expression, chunk compression reduces the number of independent units, and structural compression reduces relational organization the learner must reconstruct. These are distinct operations and must be evaluated independently. Explanatory traversal preserves how an explanation is followed; conceptual schema externalizes how its knowledge is organized. A trustworthy compiler should preserve both when each is supported.

The architecture therefore does not treat `source → summary → shorter summary → visual` as a trustworthy pipeline. Each resolution and representation must derive from the grounded substrate, preserve useful explanatory work already present in the source, retain provenance, and remain recoverable to richer trusted information.

The current division-of-labor hypothesis is that **deterministic machinery is the trust/admission layer**, while generative intelligence may propose bounded semantic synthesis and explanatory abstraction where deterministic transformation fails. Generated output is never canonical merely because a model produced it. Novel semantic claims that deterministic checks cannot establish remain explicit validation gaps and fail closed; model-assisted synthesis is not yet validated. Representation and UI remain downstream and paused until synthesis and abstraction are validated.

Deterministic validation has a semantic-entailment boundary: abstractive candidate generation and semantic admission are separate trust problems. If semantic judgment is required, it must be a bounded, auditable trust component—not proof by model confidence or agreement. Uncertain semantic validation fails closed. Semantic judging itself has not yet been validated.

## Principles

- **Meaning before medium.** Establish grounded meaning before deciding how to present it.
- **Explanatory structure is information.** Preserve coherent meaning blocks, their functions, and supported traversal before compressing language inside them.
- **Schema and traversal are complementary.** Organize supported chunks and implications without erasing the path through which the explanation becomes intelligible.
- **Reduce avoidable reconstruction.** Preserve useful explanatory work from the source while externalizing organization the learner would otherwise have to rebuild mentally.
- **Compression before visualization.** First preserve semantics, explanatory traversal, and supported conceptual organization; visualization remains downstream of schema and representation selection.
- **Non-destructive compression.** A compressed view never replaces or mutates its richer semantic substrate.
- **Provenance at every resolution.** Every retained unit must trace back to trusted evidence and source identity.
- **Prose is first-class.** Prose is an intentional representation when it is already cognition-efficient, not a fallback.
- **Visuals must earn their complexity.** Structural or perceptual form is warranted only when it externalizes cognitive work the learner would otherwise perform mentally.
- **Form follows cognitive work.** Representation choice depends on the work inherent in the knowledge, not on source or domain identity.
- **UI tests the compiler; it does not compensate for it.** Experimental surfaces should expose whether compression and abstraction are strong enough, not hide weak compiler output behind layout, interaction, or visual polish.
- **Validate abstraction before representation.** Learner-facing representation work remains paused until the core compression, synthesis, conceptual-abstraction, and schema-formation architecture is validated.
- **Future context may select resolution.** Learner goals, prior knowledge, task, and time budget may eventually influence resolution, but current experiments use explicit frozen goals rather than personalization.
- **One substrate, multiple outputs.** A single grounded knowledge substrate should be capable of supporting several independently generated resolutions and media.
- **Fail closed on unsupported inference.** Compression must retain uncertain or qualified material when omission or reformulation could strengthen, distort, or detach it from evidence.

## Current validated direction

The repository currently contains grounded extraction, semantic admission, deterministic representation experiments, a cognitive-utility gate, and evidence that plain prose, semantically enriched prose, and structural representation each have legitimate but different roles. Progressive semantic compression is being evaluated between grounded knowledge and representation selection. Explanatory traversal and conceptual schema are distinct experimental layers: one preserves how meaning is followed, while the other tests whether supported knowledge can be organized into fewer coherent units without deleting facts or optimizing word count.

Current work does not establish optimal teaching, universal essentiality, personalized learning paths, arbitrary multimodal ingestion, or an optimal visual grammar. Human review remains necessary for cognitive and pedagogical judgments.

## Ambition boundary

Podcast and video ingestion, personalized explanations, generated presentations, revision materials, courses, and other multimodal educational outputs are possible future applications of this architecture. They are not current implemented capabilities or commitments.

The project does not currently claim that it can:

- identify universally essential information;
- optimally teach an arbitrary learner;
- compile arbitrary audio or video into a trusted course;
- select the optimal visual grammar;
- prove learning improvement from machine checks; or
- generate perfect personalized courses or presentations.

Those possibilities may be explored only through separately authorized, evidence-preserving work packets.
