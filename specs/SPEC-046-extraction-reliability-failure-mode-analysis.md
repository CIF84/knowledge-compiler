# SPEC-046 — Extraction Reliability Failure-Mode Analysis

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Aggregate and diagnose extraction reliability failures across the complete blind evidence from SPEC-042 and SPEC-045 before changing prompts, schemas, validators, semantic contracts, model choice, or pipeline architecture.

This packet asks **where extraction reliability is actually failing**, not how to fix it yet.

It is evidence-only / diagnostic work.

## Owner verdict entering this packet

SPEC-045 owner verdict:

`REPLICATION_CONFIRMS_HETEROGENEOUS_MODEL_ERROR_DOMINATED_FAILURES`

Accepted interpretation:

- the SPEC-043 process/event dangling-identity pattern did not replicate systematically;
- narrow extraction→contract alignment is therefore not justified now;
- strict declared-identity validation remains protected;
- failures across blind sources are heterogeneous and model-error dominated;
- the next step is to locate the dominant failure stages before choosing an intervention.

## Evidence set

Use only immutable committed evidence from:

- SPEC-041 / SPEC-042 initial blind source set and execution;
- SPEC-043 failure diagnosis;
- SPEC-044 / SPEC-045 replication source set and execution.

No new source retrieval or model execution is authorized.

Across the two blind runs there are nine unseen sources total. Preserve source-level outcomes exactly as recorded.

Known rejected-object taxonomy totals entering this packet:

```text
SPEC-042 / SPEC-043
MODEL_ERROR             1
EXTRACTION_GRANULARITY  2

SPEC-045
MODEL_ERROR             3
EXTRACTION_GRANULARITY  1

combined known rejected objects
MODEL_ERROR             4
EXTRACTION_GRANULARITY  3
CONTRACT_GAP            0
VALIDATION_BUG          0
AMBIGUOUS               0
```

Do not alter those primary classifications unless immutable evidence demonstrates that a prior diagnostic artifact is internally inconsistent. If such inconsistency exists, stop and report it rather than silently reclassifying history.

## Primary question

> At which stages of the extraction pipeline do blind failures originate, and what class of intervention should be tested next without weakening the trusted-knowledge boundary?

## Failure-stage taxonomy

For every rejected semantic object from SPEC-042 and SPEC-045, assign exactly one **origin stage** from this fixed taxonomy:

### `ENTITY_INVENTORY`

The extraction fails to declare, duplicates, fragments, aliases, or otherwise inconsistently identifies an entity needed by downstream semantic objects.

Examples may include a relationship/proposition referring to a source-supported identity that was never placed in the entity array.

### `RELATIONSHIP_SEMANTICS`

Declared entities are available, but the model proposes an unsupported, incorrect, reversed, over-specific, or otherwise semantically invalid relationship/predicate.

### `PROPOSITION_CONSTRUCTION`

The model constructs a typed proposition whose roles, operands, event structure, comparison baseline, condition, or semantic composition is unsupported or malformed at the semantic level.

### `EVIDENCE_FIDELITY`

The proposed semantic meaning may be plausible or partly supported, but the extraction fabricates, paraphrases where exact evidence is required, misquotes, misanchors, or otherwise fails the exact source-evidence contract.

### `CROSS_REFERENCE_CONSISTENCY`

Individually defensible semantic objects are produced, but IDs/references across entities, relationships, propositions, claims, or evidence do not resolve consistently. Use this only when the failure is primarily referential consistency rather than missing conceptual granularity itself.

### `GROUNDING_RESOLUTION`

The provider output is semantically/source-supported and internally coherent, but deterministic grounding cannot resolve it correctly to the source under the intended current grounding contract.

### `CANONICAL_VALIDATION`

The proposal is grounded and internally coherent, but violates a canonical semantic rule. This stage does not imply validator bug; record whether rejection is correct under the current trusted contract.

### `OTHER`

Use only if none of the above fits. Requires explicit rationale. Do not invent additional stage names.

## Distinguish origin from detection

For every failure record both:

- `origin_stage` — where the bad or inconsistent information first entered the pipeline;
- `detection_stage` — where the deterministic system actually rejected it.

These may differ.

Example:

```text
undeclared source-supported entity
origin: ENTITY_INVENTORY
detected: CANONICAL_VALIDATION
```

This distinction is central to SPEC-046.

## Required analysis

### 1. Build complete blind failure inventory

Enumerate every rejected semantic object across SPEC-042 and SPEC-045.

For each preserve:

- experiment/spec;
- source ID/domain;
- source-level PASS/FAILED_CLOSED status;
- object ID/type;
- existing SPEC-043 primary classification;
- exact provider proposal relevant to failure;
- exact source evidence;
- validation/grounding error;
- origin stage;
- detection stage;
- confidence `HIGH` / `MEDIUM` / `LOW`;
- concise rationale.

### 2. Analyze successful blind sources as controls

Use admitted blind sources only as controls to understand what successful extraction looks like.

Do not perform subjective pedagogy review.

Record mechanically useful contrasts such as:

- entity count;
- relationship/proposition count;
- exact-evidence acceptance;
- declared-reference consistency;
- structure detection;
- representation-plan production.

The purpose is to determine whether failed sources differ by identifiable pipeline behavior, not to rank domains.

### 3. Aggregate by origin stage

Report:

- rejected-object count per origin stage;
- source count affected per origin stage;
- MODEL_ERROR vs EXTRACTION_GRANULARITY composition within each stage;
- whether any stage recurs across unrelated domains;
- whether one stage dominates or failures remain broadly heterogeneous.

### 4. Separate safety success from extraction success

Report two independent measures:

**Extraction reliability:** how often provider output reaches trusted admission without rejected semantic objects/source-level fail-close.

**Trust-boundary reliability:** how often known invalid/malformed outputs were prevented from becoming trusted knowledge.

Do not collapse these into one score.

A failed-closed source is an extraction failure but may simultaneously be a trust-boundary success.

### 5. Map failure stages to intervention classes

For each origin stage observed, identify the smallest **class of intervention worth experimentally testing**, without implementing it.

Allowed intervention-class vocabulary:

- `PROMPT_CONSTRAINT`
- `SCHEMA_CONSTRAINT`
- `DETERMINISTIC_PREVALIDATION`
- `EXTRACTION_DECOMPOSITION`
- `GROUNDING_IMPROVEMENT`
- `MODEL_SELECTION`
- `NO_CHANGE_YET`

Multiple candidate intervention classes may be recorded per stage, but rank them and explain evidence.

Do not specify final implementation details.

### 6. Recommend exactly one next experiment class

Based on aggregate evidence, recommend one and only one next experimental direction from the intervention classes above.

The recommendation must include:

- why it targets the dominant/repeated observed failure mechanism;
- what protected behavior must remain unchanged;
- what evidence would falsify the hypothesis;
- why competing intervention classes are not first priority.

If no intervention has sufficient evidence, choose `NO_CHANGE_YET` and specify what additional evidence is required.

## Important analytical constraints

Do not assume every model error is best solved by prompting.

Do not assume every dangling ID is a schema/contract problem.

Do not assume provider/model quality is the bottleneck merely because `MODEL_ERROR` is the largest SPEC-043 class.

Trace each error to its origin stage first.

For example, a fabricated evidence quote and an unsupported predicate may both classify as MODEL_ERROR while requiring very different intervention experiments.

## Harness counter limitation

SPEC-045 disclosed that the frozen harness reports four completed adapter returns while the authoritative provider ledger and six preserved raw responses establish six actual calls, because two calls failed inside extraction-boundary processing before a `BlindExtractionAttempt` returned.

Treat this as an **observability limitation**, not an extraction failure classification.

Record it separately under `instrumentation_findings`.

Do not modify the frozen harness in this packet.

## Required artifact

Create:

`examples/evaluations/spec-046-extraction-reliability-failure-mode-analysis-20260913/report.json`

The canonical report must include:

- immutable evidence references/hashes;
- nine-source outcome inventory;
- complete rejected-object inventory;
- existing SPEC-043 classification for every rejected object;
- origin-stage + detection-stage assignment;
- successful-source control summary;
- aggregate origin-stage counts;
- extraction-reliability vs trust-boundary-reliability separation;
- intervention-class mapping;
- exactly one recommended next experiment class;
- instrumentation findings;
- explicit zero-call/zero-repair statement;
- tests and integrity validation;
- owner-review state.

A Markdown summary may be added but is not required.

## No new model judgment

All diagnosis must be performed from committed evidence and deterministic inspection.

Do not use an LLM/API call to classify the failures.

Codex may reason over the committed artifacts as part of implementation, but no provider/model tool or external semantic service is authorized.

## Validation

At minimum:

- verify SPEC-042, SPEC-043, SPEC-044, and SPEC-045 canonical evidence hashes/identities;
- verify all nine source identities and recorded outcomes;
- verify rejected-object count reconciles with prior reports;
- validate fixed failure-stage vocabulary;
- validate fixed intervention-class vocabulary;
- validate every rejected object has one origin and one detection stage;
- validate exactly one recommended next experiment class;
- run focused tests for diagnostic tooling if added;
- run control-plane tests;
- run full offline suite;
- validate JSON;
- run secret-safety/provenance checks;
- run `git diff --check`;
- verify no provider/model/network call occurred;
- verify protected implementation/evidence unchanged.

Prefer evidence-only artifacts over production-code changes unless deterministic diagnostic tooling is genuinely necessary.

## Protected state

Do not modify:

- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler;
- SPEC-040 frozen harness/compiler;
- SPEC-041/042/044/045 source packets, manifests, raw responses, execution evidence;
- SPEC-043 taxonomy and accepted classifications;
- prompt `spec-010-v1`;
- extraction schema;
- semantic vocabulary;
- grounding/provenance;
- declared-identity invariant;
- semantic validator;
- representation strategy logic;
- renderer coverage;
- navigation/UI behavior.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- access external web/network sources;
- rerun extraction;
- repair or regenerate historical outputs;
- change historical classifications silently;
- change prompt/schema/model;
- change entity/relationship/proposition extraction behavior;
- normalize missing entities;
- weaken or alter validation;
- add deterministic repair logic;
- implement the recommended intervention;
- create new learner-facing artifacts;
- redesign UI/navigation;
- promote product/baseline state.

## Completion state

On completion:

- set SPEC-046 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- record objective diagnostic result and recommended next experiment class;
- commit/push according to repository protocol;
- stop at `OWNER_REVIEW`;
- do not automatically prepare or implement the recommended intervention.

## Owner review question

> Across all nine blind sources, where do extraction failures actually originate, and which single intervention class now has the strongest evidence for being tested next while preserving the strict trusted-knowledge boundary?
