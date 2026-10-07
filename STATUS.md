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

## SPEC-062 owner verdict

`CONCEPTUAL_SCHEMA_SUPPORTED_RAW_SCHEMA_NOT_COGNITIVELY_USEFUL`

Additional finding: `S1_S2_DISTINCTION_NOT_PERCEPTIBLE`.

Owner review rejected S1/S2 as learner representations. The surfaces exposed compiler machinery—schema enums, block counts, repeated facts, chunk IDs, and relation ledgers—rather than making conceptual organization perceptible. The raw schema may remain a useful intermediate representation, but IR is not UI.

Canonical lesson:

> **Every internal abstraction must cross a separate cognitive-utility boundary before learner exposure.**

Do not modify the frozen SPEC-062 schema in response to this verdict. The next experiment isolates projection only.

## Current approved work packet

```text
specs/SPEC-063-schema-to-cognitive-representation-compilation.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-063 is authorized to compile the exact frozen SPEC-062 schemas for Geology, Astronomy, and Meteorology into learner-facing cognitive representations.

The schema, chunk membership, hierarchy, edges, implications, semantics, explanatory structures, and provenance are frozen. No repair or regeneration of SPEC-062 is authorized.

The experiment must compare:
- P0 — frozen explanatory prose baseline;
- P1 — frozen raw schema control;
- P2 — new cognitive representation compiled from the frozen schema.

P2 may use only a bounded, deterministic representation grammar derived from frozen schema properties. It must represent conceptual organization rather than compiler metadata, retain prose where prose is efficient, keep all detail recoverable, and fail closed rather than invent unsupported structure.

No model/provider calls, retrieval, extraction reruns, schema changes, domain/case routing, personalization, production promotion, or follow-up work are authorized.

## Current product question

```text
frozen conceptual schema (IR)
          ↓
cognitive representation compiler
          ↓
learner-facing perceptual organization
          +
concise explanatory prose
          +
recoverable detail
          ↓
Does the learner perceive the organization
without having to interpret compiler machinery?
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
