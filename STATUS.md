# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

## Extraction state

Candidate B v2 (`spec-051-candidate-b-v2`) admitted 8/9 blind sources in SPEC-052 with zero known-invalid admission. Extraction decomposition remains unpromoted.

## Representation evidence

SPEC-056 established that representability alone does not justify visualization.

SPEC-057 established the cognitive-utility gate:

> **A representation must earn its complexity by externalizing cognitive work the learner would otherwise perform mentally.**

SPEC-058 owner verdict: `UTILITY_GATE_CONFIRMED_REPRESENTATION_FORM_REMAINS_UNRESOLVED`.

SPEC-059 owner verdict: `ENRICHED_PROSE_CONCEPT_SUPPORTED_SELECTION_MODEL_REQUIRES_REFINEMENT`.

Accepted SPEC-059 findings:

- lexical/category emphasis was rarely better than plain prose;
- useful emphasis must preserve contextual meaning-bearing fragments rather than isolated quantities/qualifiers;
- comparisons often require richer representation when emphasis would cover almost all or none of a sentence;
- simple claims generally favor prose;
- even a two-node relation can justify structure when the relation itself is the explanatory content;
- node count is not a sufficient utility criterion;
- visual-grammar quality remains unresolved.

## New committed direction

Knowledge Compiler now treats representation as downstream of **progressive semantic compression**.

> **Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.**

Core architectural principle:

> **Compression is a view over knowledge, not destruction of knowledge.**

Current conceptual pipeline:

```text
SOURCE
  ↓
GROUNDED / TRUSTED KNOWLEDGE
  ↓
GOAL-PRESERVING SEMANTIC COMPRESSION
  ↓
VARIABLE-RESOLUTION INFORMATION
  ↓
FURTHER COGNITIVE GAIN?
  ├─ no  → concise/enriched language
  └─ yes → structural/perceptual representation
               ↓
          visual grammar
```

This commits the project to the direction, not the full product ambition. Podcast/video ingestion, learner personalization, presentation generation and arbitrary multimodal compilation remain possible future applications, not current capabilities or authorized work.

## Current approved work packet

```text
specs/SPEC-060-progressive-semantic-compression-foundation.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-060 must:

1. create/update canonical project vision/mission documentation;
2. freeze six diverse cases from existing trusted repository evidence;
3. create an isolated experimental essential-information model;
4. generate three independent non-destructive views from the same grounded substrate: R0 source-rich, R1 essential explanation, R2 essential units;
5. measure compression while auditing semantic, epistemic and provenance preservation;
6. create a neutral six-case owner-review artifact;
7. stop at owner review.

No visualization experiment is part of SPEC-060.

## Current product question

```text
trusted source-derived material
        ↓
remove rhetorical/repetitive/linguistic overhead
without removing meaning
        ↓
R0 source-rich
R1 essential explanation
R2 essential units
        ↓
How far can representation cost fall
before useful semantic information is lost?
        ↓
OWNER REVIEW
```

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing architecture/baseline;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- SPEC-055–059 evidence/artifacts;
- SPEC-057 cognitive-utility decisions;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- production representation strategies/renderers;
- My Map/navigation/Explore Next;
- historical evaluation evidence;
- unrelated user work.

## Explicitly forbidden

Do not call a model/provider; retrieve external sources; rerun extraction; modify KnowledgeModel semantics; create unsupported topology; implement learner personalization, podcast/video ingestion, presentation generation or visual-grammar selection; promote compression/enriched prose/renderers; redesign production UI; encode owner feedback as case-specific rules; assign the human pedagogical verdict; implement follow-up product changes.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract and metadata must agree with that contract. Completed work must not remain active.
