# SPEC-002 — LLM Semantic Extraction

## Status

Ready for implementation.

## Primary Question

> Can a real LLM reliably transform previously unseen explanatory text into the existing validated `KnowledgeModel` across deliberately different domains without changing downstream architecture?

This is the highest-value uncertainty identified after SPEC-001.

## Purpose

SPEC-001 proved that a useful semantic intermediate representation can exist and that the deterministic pipeline can validate, deduplicate, source-ground, and serialize it.

SPEC-002 replaces the manually prepared extraction fixture with a **real structured-output LLM extractor** and evaluates whether the current semantic IR survives contact with probabilistic extraction.

The intended architecture remains:

```text
plain text
   ↓
SourceDocument normalization
   ↓
KnowledgeExtractor
   ├── FixtureExtractor      existing deterministic path
   └── LLMExtractor          new experimental path
             ↓
       ExtractionResult
             ↓
     existing validation
             ↓
existing conservative deduplication
             ↓
      KnowledgeModel
             ↓
        JSON / CLI
```

The experiment succeeds only if the LLM can be introduced **behind the existing extractor boundary**. Do not redesign downstream architecture merely to accommodate a provider SDK.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `specs/SPEC-001-text-to-knowledge-model.md`
8. `debriefs/DEBRIEF-001-text-to-knowledge-model.md`
9. current implementation and tests

Treat the current repository state as authoritative over assumptions in this SPEC where they conflict with implemented reality. If a material conflict exists, report it before changing architecture.

## Experiment Design

The goal is not to demonstrate that an LLM can emit JSON.

The goal is to determine whether it can produce **useful, grounded semantic structure** under the existing contracts.

The experiment therefore needs deliberately different explanatory domains:

1. **Electromagnetism** — physical mechanisms and reciprocal field relationships
2. **Software architecture** — components, dependencies, constraints, design relationships
3. **Economics** — causal relationships, variables, incentives, trade-offs
4. **Biology** — entities, mechanisms, processes, hierarchy
5. **History** — actors/events, temporal sequence, causes, consequences

Use short, repository-owned source fixtures written specifically for this experiment. Do not depend on live web content.

The fixtures should be long enough to contain non-trivial structure but small enough for human inspection and inexpensive repeated LLM calls. Aim approximately for several paragraphs per domain, not chapters.

## Scope

Implement the smallest real-extraction slice that can:

1. call one real LLM provider through a concrete `KnowledgeExtractor` implementation;
2. request structured semantic extraction matching the existing `ExtractionResult` contract;
3. convert provider output into existing domain types;
4. reject malformed or invalid extraction through existing validation boundaries;
5. preserve exact source evidence spans;
6. distinguish `SOURCE` from `INFERRED` output;
7. run the existing deduplication and `KnowledgeModel` pipeline unchanged where practical;
8. expose real extraction through the existing CLI;
9. retain the deterministic fixture extractor for offline/unit tests;
10. add five domain fixtures and a repeatable evaluation harness/report;
11. capture enough metadata to reproduce and compare extraction runs.

## Explicit Non-Goals

Do not implement in SPEC-002:

- graph visualization;
- Streamlit or web UI;
- structure detection;
- feedback-loop detection;
- causal simulation;
- URL/Wikipedia/PDF/audio/video ingestion;
- chunking for long documents unless the chosen provider requires it for these fixtures;
- persistent database storage;
- embeddings or vector search;
- cross-document knowledge graphs;
- autonomous web fact checking;
- multiple LLM-provider implementations;
- model-routing infrastructure;
- prompt optimization frameworks;
- agent loops;
- automatic ontology expansion;
- user accounts;
- production observability infrastructure.

Do not turn provider integration into a generalized AI platform.

## Provider Choice

Implement exactly **one** real provider for this experiment.

Prefer a provider/model that supports reliable structured output / JSON schema enforcement and can be used through a small official SDK.

The concrete provider is an adapter behind `KnowledgeExtractor`. Provider-specific types, request objects, and SDK concerns must not leak into `models.py`, `pipeline.py`, deduplication, or downstream semantic contracts.

Configuration must come from environment variables or explicit CLI/config arguments. Never commit API keys or secrets.

If the provider/model name is configurable, define a sensible default but record the actual model used in extraction metadata.

## LLM Extractor Contract

Add a concrete extractor conceptually equivalent to:

```python
class LLMExtractor:
    def extract(self, document: SourceDocument) -> ExtractionResult:
        ...
```

The extractor should:

1. receive the normalized `SourceDocument`;
2. send the source plus explicit semantic extraction instructions;
3. constrain output to the current extraction schema as strongly as the provider allows;
4. parse provider output;
5. convert it through the existing `ExtractionResult.from_dict(...)` or equivalent validation path;
6. return only validated typed extraction state.

Raw model output must never bypass the existing validation boundary.

## Extraction Instructions

The prompt/instructions should describe the semantic task rather than prescribe a visual representation.

The model should be instructed to:

- identify important concepts, objects, processes, variables, systems, and components;
- extract meaningful propositions that do not naturally form graph edges as claims;
- extract relationships only using the current `RelationshipType` vocabulary;
- prefer important explanatory relationships over exhaustive sentence decomposition;
- distinguish explicitly stated relationships from useful inference;
- preserve exact evidence from the supplied source for `SOURCE` items;
- avoid external knowledge unless marking the result `INFERRED`;
- avoid creating entities solely to reproduce grammar;
- avoid duplicate entities where possible;
- use aliases for genuine naming equivalence;
- avoid merging related but distinct concepts;
- keep descriptions concise and grounded;
- represent uncertainty conservatively.

The extractor should not ask the model to generate mind maps, Mermaid, summaries, teaching prose, or visualization instructions.

## Evidence Grounding

Evidence correctness is a critical part of this experiment.

Existing `SourceSpan` invariants remain authoritative:

```text
document_id
start_char
end_char
quote
```

For every `SOURCE` claim or relationship:

- evidence must refer to the supplied normalized document;
- offsets must be valid;
- `quote` must exactly match `document.text[start_char:end_char]`;
- invalid evidence must cause validation failure rather than silent acceptance.

### Evidence-coordinate strategy

LLMs are often unreliable at counting character offsets directly. Do not weaken the domain invariant to accommodate this.

Prefer an adapter-level strategy such as:

1. ask the model for exact source quote(s), not trusted numeric offsets;
2. resolve those quotes deterministically against the normalized source in application code;
3. construct `SourceSpan` offsets only after deterministic matching;
4. reject ambiguous or missing matches unless a conservative deterministic disambiguation is possible.

The exact implementation may differ, but **the final `KnowledgeModel` must retain exact validated coordinates**.

If this proves materially difficult, preserve the failure as experimental evidence rather than silently loosening source grounding.

## SOURCE vs INFERRED

Retain the current semantic distinction.

### SOURCE

Use when the relationship/claim is explicitly supported by supplied text.

It must have valid source evidence.

### INFERRED

Use only for useful semantic structure not explicitly stated by the source.

Do not invent source evidence for inferred items merely because nearby text motivated the inference.

The current model's strict treatment of inferred evidence is intentionally retained for this experiment. If real extraction demonstrates that `supporting_evidence` is needed as a distinct concept, record that in DEBRIEF-002 rather than redesigning the IR during extraction implementation unless the existing contract makes the experiment impossible.

## Relationship Vocabulary

Use the existing vocabulary unchanged initially:

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

A major purpose of the five-domain test is to discover whether this grammar is sufficiently expressive.

Do not add new relationship types merely because one generated extraction would be more convenient with them.

If a fixture exposes a recurring relationship that cannot be represented without material semantic loss:

1. document the gap;
2. prefer the closest honest existing representation for this experiment where possible;
3. record the proposed vocabulary change for DEBRIEF-002 / a subsequent SPEC.

Only change the enum during SPEC-002 if the existing vocabulary makes a meaningful multi-domain evaluation impossible.

## Domain Fixtures

Add repository-owned fixtures approximately like:

```text
tests/fixtures/domains/
├── electromagnetism.txt
├── software_architecture.txt
├── economics.txt
├── biology.txt
└── history.txt
```

The electromagnetism fixture may reuse the existing source if appropriate.

Each new fixture should intentionally exercise different semantic structures.

### Software architecture

Include concepts such as components/modules, dependency direction, interfaces, coupling, constraints, or separation of concerns.

### Economics

Choose a compact mechanism such as supply/demand equilibrium, price signals, elasticity, incentives, or a similarly bounded explanatory system.

### Biology

Choose a bounded mechanism such as cellular respiration, immune response, gene expression, or another process containing components and causal/temporal structure.

### History

Choose a bounded historical mechanism/event where chronology and causation can be distinguished. Avoid politically contentious current events; the goal is semantic extraction, not historical debate.

## Evaluation Harness

Create a small repeatable evaluation command or script that runs the real extractor over the five fixtures and writes inspectable outputs without requiring manual code edits.

Conceptually:

```bash
knowledge-compiler evaluate \
  --extractor llm \
  --output-dir examples/evaluations/run-001
```

Exact CLI design may differ if a simpler extension of `translate` is cleaner.

For each run, preserve at minimum:

```text
domain
source fixture
provider
model
run timestamp
extractor/prompt version if practical
entity count
claim count
relationship count
validation success/failure
output KnowledgeModel JSON when successful
failure reason when unsuccessful
```

Do not commit secrets or opaque provider response dumps containing unnecessary metadata.

Evaluation output generated from live calls does not need to be deterministic.

## Evaluation Dimensions

The project needs more than schema-valid output.

For each domain, support human review against these dimensions:

### 1. Grounding

Are `SOURCE` claims and relationships actually supported by the cited text?

### 2. Entity quality

Are important system concepts represented without excessive grammatical/noise entities?

### 3. Relationship quality

Do edges capture explanatory structure rather than merely restating adjacent sentences?

### 4. Coverage

Does the model preserve the major mechanisms needed to understand the source?

### 5. Precision

Does the model avoid unsupported causality, equivalence, or external facts?

### 6. Deduplication quality

Does extraction avoid or correctly merge obvious duplicate concepts while preserving distinct concepts?

### 7. Vocabulary fit

Can the current relationship grammar represent the important structure without distortion?

### 8. Cross-domain usefulness

Does the same IR remain intelligible across physics, software, economics, biology, and history?

Do not reduce these dimensions to a fabricated aggregate score. A simple qualitative review vocabulary is sufficient, for example:

```text
GOOD
MIXED
POOR
NOT_EVALUATED
```

Optional factual counts may accompany qualitative judgments.

## Golden Expectations

Do not create exhaustive hand-authored target graphs for all domains; that risks turning evaluation into exact-output matching against subjective annotations.

Instead, define a small set of **load-bearing expectations** per fixture: concepts and relationships whose absence would make the resulting model materially misleading or incomplete.

For electromagnetism, retain expectations approximately equivalent to:

```text
charge → CREATES → electric field
moving charge/current → CREATES → magnetic field
changing magnetic field → INDUCES → electric field
changing electric field → INDUCES → magnetic field
light → IS_A → electromagnetic wave
```

For each new domain, define roughly 3–6 similarly important expectations in test/evaluation metadata.

The LLM does not need to produce identical IDs or exhaustive identical graphs. Evaluate semantic equivalence where practical.

## Testing Strategy

### Deterministic automated tests

Real network LLM calls must **not** be required for the normal `pytest` suite.

Use mocked/fake provider responses to test:

- provider output conversion into `ExtractionResult`;
- structured-output parsing;
- evidence quote → deterministic source-span resolution;
- ambiguous quote handling;
- missing quote handling;
- invalid relationship types rejected;
- invalid entity references rejected downstream;
- `SOURCE` items without resolvable evidence rejected;
- provider/API errors surfaced cleanly;
- provider-specific types do not leak into core domain state;
- CLI configuration/error behavior.

Retain all SPEC-001 tests.

### Live evaluation

Provide an explicit opt-in command for real provider calls.

Live calls should be used during implementation to generate at least one complete five-domain evaluation run.

Do not make CI or normal unit tests depend on API credentials.

## Reproducibility Metadata

Each successful live extraction should include enough metadata to understand the experiment later, at minimum:

```text
extractor = llm
provider
model
```

If practical without adding infrastructure, also include:

```text
prompt_version
provider request identifier
```

Do not mistake model randomness for a reproducibility guarantee. The goal is experimental traceability.

## CLI

Extend the existing CLI conservatively.

A real translation should be possible conceptually as:

```bash
knowledge-compiler translate source.txt \
  --extractor llm \
  --output model.json
```

Provider/model configuration may come from environment variables and/or explicit arguments.

Requirements:

- fixture extraction remains available;
- missing credentials produce a clear non-zero failure;
- provider failures produce a clear non-zero failure;
- validation failures produce a clear non-zero failure;
- successful output remains the same `KnowledgeModel` JSON format used by SPEC-001.

While touching CLI packaging, correct the SPEC-001 default-fixture packaging issue if doing so is small and does not distract from the extraction experiment.

## Architecture Constraints

The following should remain true after SPEC-002:

```text
LLM provider SDK
      │
      ▼
provider adapter / LLMExtractor
      │
      ▼
KnowledgeExtractor contract
      │
      ▼
ExtractionResult
      │
      ▼
existing semantic pipeline
```

Specifically:

- `models.py` does not import provider SDK types;
- `pipeline.py` does not know which provider is used;
- deduplication remains provider-independent;
- `KnowledgeModel` JSON remains provider-independent;
- fixture extraction remains usable without network access;
- downstream architecture does not fork into fixture-vs-LLM paths.

## Failure Is a Valid Experimental Outcome

SPEC-002 is a product/architecture experiment, not a requirement to prove the current design correct.

Examples of valuable negative findings:

- evidence spans cannot be made reliable with the current extraction strategy;
- relationship vocabulary is too narrow across domains;
- entity extraction becomes excessively noisy;
- `SOURCE` vs `INFERRED` is insufficiently expressive;
- one-shot extraction produces structurally inconsistent graphs;
- provider structured output still requires significant repair;
- the IR works for mechanistic domains but poorly for historical/temporal material.

Do not hide these by adding broad repair heuristics or expanding scope. Capture them for DEBRIEF-002.

## Acceptance Criteria

SPEC-002 is complete when all are true:

- [ ] One real LLM provider is implemented behind the existing `KnowledgeExtractor` boundary.
- [ ] Provider-specific dependencies remain isolated from the semantic core.
- [ ] Existing fixture extraction still works offline.
- [ ] Normal `pytest` requires no network or API key and all tests pass.
- [ ] Real extraction produces the existing `KnowledgeModel` JSON format.
- [ ] `SOURCE` evidence resolves to exact validated source coordinates.
- [ ] Invalid/unresolvable evidence fails explicitly rather than silently drifting.
- [ ] Five repository-owned domain fixtures exist: electromagnetism, software architecture, economics, biology, history.
- [ ] Each fixture has a small set of load-bearing semantic expectations.
- [ ] A repeatable live evaluation mechanism exists.
- [ ] At least one live five-domain evaluation run is completed during implementation.
- [ ] Evaluation preserves provider/model and useful run metadata.
- [ ] Outputs are human-inspected for grounding, entity quality, relationship quality, coverage, precision, vocabulary fit, and cross-domain usefulness.
- [ ] Observed semantic failures are reported rather than hidden through out-of-scope heuristics.
- [ ] No visualization, structure engine, persistence layer, or multi-provider framework is introduced.
- [ ] Completed work is committed and pushed to the canonical GitHub branch before handoff for independent review.

The primary acceptance question remains qualitative:

> Does the same semantic IR produce models across five unrelated domains that expose meaningful system structure rather than merely converting prose into schema-valid noise?

## Required Handoff to Review

When implementation is complete, Codex must report:

1. architecture implemented;
2. provider and model used;
3. files added/changed;
4. exact automated test result;
5. live evaluation command;
6. live evaluation result for each of the five domains;
7. entity/claim/relationship counts by domain;
8. evidence-resolution failures, retries, or extraction failures observed;
9. relationship-vocabulary gaps observed;
10. other semantic-quality concerns;
11. deliberate deviations from this SPEC;
12. approximate live-call cost/token usage if readily available from the provider, otherwise state that it was unavailable;
13. commit SHA;
14. confirmation that the commit was pushed to the canonical GitHub branch.

Do not write `DEBRIEF-002` as part of implementation. The debrief follows independent review and should reflect verified reality, not the implementer's self-assessment.

## Operational Learning Capture

Because SPEC-002 is also the second trial of the project's operating model, the review/debrief should explicitly observe:

- whether reading the repository memory was sufficient to reconstruct intent;
- whether the SPEC reduced implementation ambiguity;
- where Codex required interpretation despite the SPEC;
- whether the implementation/review handoff was smoother than SPEC-001;
- whether pushing before review removed repository-state friction;
- whether the documentation/control layer created useful alignment or excessive overhead;
- what should change in `OPERATING_MODEL.md` before SPEC-003.

The project is experimenting with both the product and the process used to build it.
