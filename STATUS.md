# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

## Extraction state

Candidate B v2 (`spec-051-candidate-b-v2`) admitted 8/9 blind sources in SPEC-052 with zero known-invalid admission. Extraction decomposition remains unpromoted.

## Representation evidence

SPEC-057 established:

> **A representation must earn its complexity by externalizing cognitive work the learner would otherwise perform mentally.**

SPEC-058 owner verdict: `UTILITY_GATE_CONFIRMED_REPRESENTATION_FORM_REMAINS_UNRESOLVED`.

SPEC-059 owner verdict: `ENRICHED_PROSE_CONCEPT_SUPPORTED_SELECTION_MODEL_REQUIRES_REFINEMENT`.

## Progressive semantic compression direction

> **Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.**

Core principle:

> **Compression is a view over knowledge, not destruction of knowledge.**

SPEC-060 established mechanically that six frozen sources can be represented at smaller R1/R2 resolutions with zero detected loss under the current semantic/epistemic audits and 100% provenance coverage.

Owner review of case 01 exposed a missing preservation dimension.

SPEC-060 owner verdict:

`SEMANTIC_CONTENT_PRESERVED_EXPLANATORY_STRUCTURE_NOT_PRESERVED`

Accepted owner findings:

- R1 mostly shortened/broke apart source prose and did not materially improve cognitive processing;
- R2 exposed information types but disrupted the natural chain of thought;
- R0's paragraphs sometimes acted as useful containers of coherent meaning;
- paragraph boundaries are evidence, not a universal semantic unit;
- the source carried useful explanatory traversal in addition to domain facts;
- preserving modeled facts while losing mechanism → example → consequence → observation/generalization flow increases reconstruction burden;
- raw word-count compression is not a sufficient objective;
- some linguistic/discourse material is useful because it tells the learner how pieces of domain knowledge fit into an explanation.

Canonical refinement:

> **Semantic preservation is necessary but not sufficient; useful explanatory structure is itself information that compression should preserve.**

> **Preserve useful explanatory work already present in the source before compressing its language.**

## Current conceptual pipeline

```text
SOURCE
  ↓
GROUNDED / TRUSTED KNOWLEDGE
  ↓
EXPLANATORY STRUCTURE
  ├─ meaning blocks
  ├─ explanatory functions
  └─ traversal / discourse relations
  ↓
CONCEPTUAL ORGANIZATION
  ├─ supported chunks
  ├─ schema / hierarchy
  └─ necessary implications
  ↓
GOAL-PRESERVING SEMANTIC COMPRESSION
  ↓
VARIABLE-RESOLUTION INFORMATION
  ↓
FURTHER COGNITIVE GAIN?
  ├─ no  → language
  └─ yes → structural/perceptual representation
               ↓
          visual grammar
```

## SPEC-061 owner verdict

`EXPLANATORY_STRUCTURE_SUPPORTED_HIERARCHY_AND_CHUNKING_INCOMPLETE`

Owner review established that SPEC-061 is a meaningful improvement over SPEC-060: block-preserving explanation can preserve natural thought flow and useful compression. Remaining gaps are hierarchical conceptual chunking and preservation of necessary implications/edges.

Key findings:
- geology: one shared spreading mechanism should organize multiple example/manifestation branches rather than a flat chain;
- astronomy: endpoint facts survived but E2 weakened a crucial implication from accumulated mass to eventual star/planet formation;
- meteorology: information density may be irreducible linguistically, while the number of independent conceptual units remains cognitively expensive;
- linguistic compression, chunk compression, and structural compression are distinct;
- traversal describes how an explanation is presented; schema describes how knowledge is organized;
- visualization remains downstream.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-062 is implemented and awaiting owner review.

The isolated generic offline inducer organized all 244 frozen semantic items and all 46 SPEC-061 explanatory blocks into 52 total conceptual chunks and 10 independent top-level units across the six cases. Per-case top-level-unit ratios are `0.2857`, `0.1667`, `0.2500`, `0.2000`, `0.0909`, and `0.4286`; lower ratios are diagnostic and are not treated as automatic cognitive success.

All 95 identified material implications remain explicit or schema-preserved, including the astronomy `r14` and `r15` accumulation-to-planet/star implications. Semantic, epistemic, explanatory, membership, schema-edge, implication, and provenance audits report zero forbidden outcomes and full recoverability. The geology, astronomy, and meteorology comparisons ran only after generic outputs were frozen and did not alter them.

The mechanical branch is `CONCEPTUAL_SCHEMA_SAFE_FOR_OWNER_REVIEW`. Desktop and 390×844 browser gates pass all six cases, peer-view identity, fact/edge preservation, trace selection, responsive layout, no-diagram checks, and clean-console checks. No model/provider call, retrieval, extraction rerun, production change, visualization, personalization, promotion, or human verdict assignment occurred.

Canonical evidence:

`examples/evaluations/spec-062-conceptual-chunking-schema-induction-20261007/report.json`

No packet is active. Promotion remains unauthorized and the owner verdict is pending.

## Current product question

```text
same grounded information
      ↓
S0 explanatory baseline
      ↕
S1 conceptual schema
      ↕
S2 schema + traversal
      ↓
Are fewer supported conceptual units
easier to think with before deleting facts
or drawing a diagram?
      ↓
OWNER REVIEW
```

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing architecture/baseline;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- SPEC-055–060 evidence/artifacts;
- SPEC-057 cognitive-utility decisions;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- production representation strategies/renderers;
- My Map/navigation/Explore Next;
- historical evaluation evidence;
- unrelated user work.

## Explicitly forbidden

Do not call a model/provider; retrieve external sources; rerun extraction; modify production KnowledgeModel semantics; add discourse relations to the production semantic registry; hard-code case-01 owner structure; equate paragraphs with meaning blocks; optimize only for word count; implement personalization, podcast/video ingestion, presentation generation, visualization or visual-grammar selection; promote experimental work; redesign production UI; assign the human pedagogical verdict; implement follow-up product changes.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract and metadata must agree with that contract. Completed work must not remain active.
