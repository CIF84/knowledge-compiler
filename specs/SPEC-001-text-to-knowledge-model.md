# SPEC-001 — Text to KnowledgeModel

## Status

Ready for implementation.

## Purpose

Build the smallest end-to-end semantic slice of Knowledge Compiler:

```text
source text
   ↓
normalization
   ↓
structured extraction
   ↓
validation
   ↓
KnowledgeModel JSON
```

This phase deliberately stops before visualization, structure detection, web ingestion, persistence, or a user interface.

The product question being tested is:

> Can difficult explanatory text be converted into a structured model whose entities and relationships capture the system described by the source?

The first golden test case is electromagnetism.

## Scope

Implement a Python package that can:

1. accept plain UTF-8 text;
2. normalize it into a `SourceDocument`;
3. extract entities, claims, and typed relationships through a pluggable extractor interface;
4. validate extraction against typed schemas;
5. preserve evidence spans back to the source;
6. distinguish source-derived content from model inference;
7. merge obvious duplicate entities conservatively;
8. serialize the resulting `KnowledgeModel` to JSON;
9. expose the pipeline through a small CLI;
10. run deterministically in tests without real LLM calls.

A real LLM adapter may be added if convenient, but the core package must not depend on a specific model vendor.

## Explicit Non-Goals

Do not implement in SPEC-001:

- graph visualization;
- Streamlit or web UI;
- URL/Wikipedia/PDF/audio/video ingestion;
- structure detection such as feedback-loop discovery;
- causal simulation;
- persistent database storage;
- user accounts;
- vector databases or embeddings;
- a universal ontology;
- autonomous external fact checking;
- prompt-driven Mermaid generation.

Do not add these merely because they are easy.

## Architectural Principle

The semantic model is an intermediate representation, analogous to a compiler IR.

```text
SourceDocument
      ↓
Extractor
      ↓
ExtractionResult
      ↓
validation / normalization
      ↓
KnowledgeModel
```

Downstream renderers must eventually consume `KnowledgeModel`, not raw source text or raw LLM prose.

The core domain model must remain independent of model vendor, CLI framework, visualization library, and persistence technology.

## Suggested Project Shape

```text
knowledge-compiler/
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── specs/
│   └── SPEC-001-text-to-knowledge-model.md
├── src/
│   └── knowledge_compiler/
│       ├── __init__.py
│       ├── models.py
│       ├── normalize.py
│       ├── extractor.py
│       ├── pipeline.py
│       ├── deduplicate.py
│       └── cli.py
├── tests/
│   ├── fixtures/
│   │   ├── electromagnetism.txt
│   │   └── electromagnetism_extraction.json
│   ├── test_models.py
│   ├── test_normalize.py
│   ├── test_pipeline.py
│   └── test_deduplicate.py
└── examples/
    └── electromagnetism.knowledge.json
```

Prefer Python 3.12+ and typed code. Use lightweight schema validation such as Pydantic if useful. Avoid unnecessary infrastructure.

## Domain Model

### `SourceDocument`

Represents normalized input while preserving stable source coordinates.

Minimum fields:

```text
id
text
source_type
metadata
```

For SPEC-001, `source_type` may support only `text`.

### `SourceSpan`

References evidence inside a `SourceDocument`.

Minimum fields:

```text
document_id
start_char
end_char
quote
```

Rules:

- offsets are zero-based;
- `end_char` is exclusive;
- the span must lie within the document;
- `quote` must equal `document.text[start_char:end_char]` after normalization;
- invalid evidence must fail validation rather than silently drift.

### `Entity`

Represents an important concept, object, process, variable, system, or component.

Minimum fields:

```text
id
name
description
entity_type
aliases
```

Keep `entity_type` small initially, for example:

```text
CONCEPT
OBJECT
PROCESS
VARIABLE
SYSTEM
COMPONENT
```

### `Claim`

Represents a meaningful proposition that may not naturally be an edge.

Minimum fields:

```text
id
statement
evidence[]
confidence
origin
```

### `Relationship`

Represents a typed edge between two entities.

Minimum fields:

```text
id
source_entity_id
relationship_type
target_entity_id
statement
evidence[]
confidence
origin
```

Initial relationship vocabulary:

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
```

This is a starting grammar, not a permanent ontology.

### `origin`

Every claim and relationship must identify whether it is:

```text
SOURCE
INFERRED
```

`SOURCE` means directly supported by supplied text evidence.

`INFERRED` means the model constructed a useful relationship that is not explicitly stated. Inferred items must not masquerade as source-derived evidence.

### `confidence`

Use either a normalized numeric confidence in `[0, 1]` or a small explicit enum. Pick one and apply it consistently.

Confidence represents extraction confidence, not metaphysical truth.

### `KnowledgeModel`

Minimum fields:

```text
document
entities[]
claims[]
relationships[]
metadata
```

All relationship references must resolve to existing entity IDs.

## Normalization

Implement deterministic source normalization before extraction.

At minimum:

- normalize line endings;
- trim irrelevant leading/trailing whitespace;
- preserve paragraph boundaries;
- avoid transformations that make evidence offsets difficult to reproduce.

Do not rewrite or summarize during normalization.

## Extractor Boundary

Define an extractor protocol/interface conceptually equivalent to:

```python
class KnowledgeExtractor(Protocol):
    def extract(self, document: SourceDocument) -> ExtractionResult:
        ...
```

The pipeline must depend on this abstraction, not a specific SDK.

Provide a deterministic fake/fixture extractor for tests.

If implementing a real LLM adapter, require structured output matching a defined extraction schema. Raw model output must never become application state without validation.

## Entity Deduplication

Implement a deliberately conservative first pass.

Required example:

```text
"electric field" == "Electric Field"
```

Aliases supplied by extraction may also be merged.

Do not automatically merge distinct concepts such as:

```text
"electromagnetic field"
"electric field"
```

unless extraction explicitly identifies one as an alias.

When entities merge, relationships must be rewritten to canonical entity IDs.

## Electromagnetism Golden Fixture

Add a fixed explanatory text fixture about introductory electromagnetism. Write it specifically for this repository; do not depend on a live Wikipedia page.

The source should support at least these concepts:

```text
charge
electric field
magnetic field
force
motion
moving charge / electric current
changing electric field
changing magnetic field
electromagnetic wave
light
```

And relationships approximately equivalent to:

```text
charge → CREATES → electric field

electric field → EXERTS_FORCE_ON → charge

moving charge/current → CREATES → magnetic field

changing magnetic field → INDUCES → electric field

changing electric field → CREATES/INDUCES → magnetic field

coupled changing electric + magnetic fields → ENABLE/FORM → electromagnetic wave

electromagnetic wave → relationship to → light
```

Do not hard-code these edges into production code. They are expected outcomes of the fixture/extractor boundary.

The checked-in fixture extraction JSON should make tests deterministic and serve as a human-reviewable benchmark.

## CLI

Provide one simple command equivalent to:

```bash
knowledge-compiler translate path/to/source.txt --output model.json
```

The command should:

1. read text;
2. normalize it;
3. run an extractor;
4. validate and deduplicate the result;
5. write formatted JSON;
6. return non-zero on validation/pipeline failure.

For local/offline demonstration, support the fixture extractor explicitly, for example:

```bash
knowledge-compiler translate tests/fixtures/electromagnetism.txt \
  --extractor fixture \
  --output /tmp/electromagnetism.json
```

Do not pretend the fixture extractor is an AI call.

## Validation Invariants

Automated tests must cover at least:

- source spans stay within document bounds;
- span quotes match normalized source text;
- relationship endpoints reference existing entities;
- confidence values are valid;
- relationship types are constrained to the known vocabulary;
- duplicate entity normalization is stable;
- merged entity IDs are correctly rewritten in relationships;
- serialization round-trips without information loss;
- invalid extraction output is rejected;
- deterministic fixture pipeline produces the expected electromagnetism model.

## Output Quality

The JSON must be easy for a human to inspect. Prefer stable ordering where practical.

An abbreviated example:

```json
{
  "entities": [
    {
      "id": "electric-field",
      "name": "Electric field",
      "entity_type": "CONCEPT"
    }
  ],
  "relationships": [
    {
      "source_entity_id": "charge",
      "relationship_type": "CREATES",
      "target_entity_id": "electric-field",
      "origin": "SOURCE",
      "confidence": 0.97,
      "evidence": []
    }
  ]
}
```

Exact IDs may differ; correctness of contracts matters more than matching the example literally.

## Acceptance Criteria

SPEC-001 is complete when all are true:

- [ ] A clean install creates a working Python package and CLI.
- [ ] `pytest` passes.
- [ ] Plain text normalizes into a validated `SourceDocument`.
- [ ] A deterministic extractor produces structured entities, claims, relationships, and evidence.
- [ ] Invalid evidence and broken graph references are rejected.
- [ ] Conservative entity deduplication works.
- [ ] `KnowledgeModel` serializes to human-readable JSON.
- [ ] The electromagnetism fixture produces a coherent model containing the major concepts and relationships above.
- [ ] Core code does not depend on visualization or a particular LLM vendor.
- [ ] No out-of-scope infrastructure is introduced.

The most important acceptance test is qualitative:

> Inspecting the generated electromagnetism JSON should make the underlying system visible without requiring the reader to reconstruct it from prose.

## Implementation Guidance for Codex

Treat this file as the authoritative scope for the increment.

Before coding:

1. inspect the repository;
2. state the proposed architecture briefly;
3. flag only genuine contradictions or blockers;
4. otherwise implement autonomously.

During implementation:

- prefer simple, explicit code;
- keep domain logic pure where practical;
- use typed boundaries;
- avoid abstractions SPEC-001 does not yet need;
- add focused tests alongside behavior;
- do not implement later roadmap phases.

When complete, report:

1. architecture implemented;
2. files added/changed;
3. tests and exact test result;
4. sample CLI command and result;
5. deliberate deviations from this spec;
6. commit SHA.
