# SPEC-043 — Blind Failure Diagnosis

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Diagnose the two SPEC-042 blind out-of-sample failures without changing the system that produced them.

The goal is to distinguish whether each rejected semantic object represents a genuine model/extraction error, a mismatch between valid natural-language semantics and the current compiler contract, an extraction-granularity problem, a validator defect, or genuinely ambiguous evidence.

This is an evidence/diagnostic packet, not a repair packet.

## Context

SPEC-042 executed exactly three frozen unseen sources through the frozen SPEC-040 harness/compiler.

Objective outcome:

- geology: `FAILED_CLOSED` because relationship `rel-5` referenced undeclared endpoint `spreading-processes`;
- meteorology: `FAILED_CLOSED` because two propositions referenced undeclared role entities `jet-stream-weather-transport` and `average-temperature-difference`;
- civics: `PASS`, admitting 20 entities and 10 relationships and producing 3 detected structures and 30 representation decisions.

The fail-closed behavior is protected and must not be weakened in this packet.

## Core question

For each rejected semantic object in geology and meteorology:

> Was the proposed meaning wrong, or was it substantially supported by the source but not expressible/admissible under the current extraction + semantic contract?

## Required diagnostic taxonomy

Classify each failure using exactly one primary category:

- `MODEL_ERROR` — the proposed semantic object or endpoint is not supported by the frozen source, materially misstates it, or invents meaning.
- `CONTRACT_GAP` — the proposed meaning is materially source-supported, but the current declared-entity / semantic contract cannot represent or admit it faithfully.
- `EXTRACTION_GRANULARITY` — the source supports the meaning, but the extraction split/merged/reified concepts at an unsuitable level, causing identity mismatch or undeclared references.
- `VALIDATION_BUG` — the proposed object satisfies the intended current contract but deterministic validation rejected it incorrectly.
- `AMBIGUOUS` — evidence is insufficient to assign one of the above without changing assumptions or making a subjective semantic leap.

Secondary observations may be recorded, but every rejected object must have exactly one primary classification.

## Scope

Inspect only immutable evidence already committed by SPEC-041/SPEC-042, including as needed:

- exact frozen source passages;
- exact raw provider responses;
- extraction outputs;
- grounding/validation traces;
- declared entity sets;
- rejected relationships/propositions;
- canonical vocabulary and validators;
- provenance spans;
- frozen prompt/schema and implementation behavior needed to explain the rejection.

The admitted civics source may be used only as a control/comparison for understanding contract behavior. Do not modify or re-evaluate it as a new product experiment.

## Required work

### 1. Reconstruct every rejection

For geology and meteorology, enumerate every rejected semantic object and show:

- source ID;
- object ID/type;
- proposed semantic statement;
- referenced entity IDs;
- which referenced IDs were declared vs undeclared;
- exact supporting or contradicting source evidence;
- validator stage and exact rejection reason.

### 2. Trace the undeclared identities

For each missing identity (`spreading-processes`, `jet-stream-weather-transport`, `average-temperature-difference`):

- determine where it first appears in the provider output;
- determine whether an equivalent or near-equivalent declared entity exists;
- determine whether the identity represents a concept, process, role, event, state, relation reification, or other semantic construction;
- determine whether the source actually supports that construction.

Do not normalize or repair the identity. Diagnose only.

### 3. Assign diagnostic classification

Apply the required taxonomy to each rejected object.

Each classification must include:

- `primary_classification`;
- concise rationale;
- source-support assessment;
- current-contract assessment;
- confidence: `HIGH`, `MEDIUM`, or `LOW`;
- counterfactual statement describing the smallest *kind* of future change that would address the issue, without implementing or prescribing the exact change.

Example counterfactual forms:

- "Would require extraction to declare the referenced process as an entity."
- "Would require validator behavior to accept an already-valid declared identity."
- "Would require the extractor not to reify this phrase as a standalone entity."

### 4. Produce aggregate diagnosis

Report counts by primary classification and answer separately:

1. How many failures appear to be semantic/model correctness failures?
2. How many appear to be interface/contract/granularity failures?
3. Is there evidence of a deterministic validator bug?
4. Do the failures share a common mechanism or are they materially different?
5. Does the evidence justify changing the semantic contract now, or is another diagnostic sample needed first?

The final answer to #5 must be evidence-based and may be `INSUFFICIENT_EVIDENCE`.

### 5. Preserve experimental integrity

No adaptation, repair, retry, or new semantic extraction is permitted. The diagnosis must be reproducible entirely from committed evidence.

## Required artifact

Create:

`examples/evaluations/spec-043-blind-failure-diagnosis-20260911/report.json`

The report must contain at minimum:

- frozen SPEC-042 identity/reference;
- inspected source IDs;
- per-rejection reconstruction;
- per-missing-identity trace;
- per-rejection diagnostic classification;
- aggregate classification counts;
- answers to the five aggregate questions;
- explicit statement that no provider/model/external calls occurred;
- tests/validation evidence;
- deviations, if any.

A concise Markdown companion may be added if useful, but `report.json` is canonical evidence.

## Validation

At minimum:

- run focused tests for any diagnostic tooling added;
- run relevant control-plane tests;
- run the complete offline suite;
- validate generated JSON;
- run provenance/secret-safety checks appropriate to preserved provider artifacts;
- run `git diff --check`;
- verify no network/provider/model calls occurred;
- verify frozen SPEC-041/SPEC-042 evidence is unchanged.

If diagnostic tooling is unnecessary, prefer evidence-only artifacts over adding production code.

## Forbidden

Do not:

- call OpenAI or any other model/provider;
- retrieve or enrich from the web;
- retry, repair, regenerate, or reinterpret through a model;
- edit frozen source passages or raw provider responses;
- change prompt `spec-010-v1`;
- change extraction schema;
- add missing entities to outputs;
- normalize missing identities into existing entities;
- change canonical relationship vocabulary;
- loosen, tighten, or otherwise modify semantic validation;
- change representation strategy or renderers;
- create a learner/browser artifact from the civics result;
- implement comparison/worked-example coverage;
- redesign UI/navigation;
- promote SPEC-042 or assign its final product verdict.

## Stop conditions

Stop rather than guess if:

- frozen SPEC-042 evidence is missing or inconsistent;
- a rejection cannot be reconstructed from committed evidence;
- classification would require a new model call or external source;
- completing the task would require modifying protected semantic behavior.

Record the blocker precisely.

## Completion state

When implementation and validation are complete:

- set this spec to `IMPLEMENTED_AWAITING_REVIEW`;
- clear the active packet in `STATUS.md` to `NONE`;
- record objective results but do not assign the owner's product verdict;
- commit and push according to the repository's established protocol;
- stop for owner review.

## Owner-review question

The owner should be able to answer:

> Did the blind failures reveal that the model misunderstood the sources, or that our compiler interface is too brittle for otherwise defensible semantic output — and do we now have enough evidence to know what class of change should come next?
