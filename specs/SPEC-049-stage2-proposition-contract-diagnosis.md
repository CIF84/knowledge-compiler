# SPEC-049 — Stage-2 Proposition Contract Diagnosis

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Diagnose the concentrated SPEC-048 Candidate-B failure pattern before implementing Candidate B v2.

The specific question is whether the six Stage-2 `PROPOSITION_CONSTRUCTION` failures were primarily caused by an under-constrained machine-readable proposition interface — meaning invalid proposition states remained expressible in the Stage-2 schema — or by genuine source/semantic misunderstanding that a stronger schema would not have prevented.

This is a diagnostic packet only. It must not implement a new extractor, alter Candidate B, rerun any model call, or change validation.

## Owner verdict entering this packet

SPEC-048 owner verdict:

`CANDIDATE_B_V1_REJECTED_STAGE2_INTERFACE_FAILURE_DOMINATES`

Accepted interpretation:

- Candidate B v1 regressed from historical Control A: 2/9 admitted versus 4/9;
- Candidate B used 19 calls and 94,574 tokens versus Control A's preserved 9 calls and 54,586 tokens;
- trust-boundary containment remained perfect: zero known-invalid objects admitted;
- seven Candidate-B sources failed closed;
- six of those seven failures originated in `PROPOSITION_CONSTRUCTION` during Stage 2;
- one failure originated in `ENTITY_INVENTORY`;
- Candidate B v1 is rejected as implemented;
- extraction decomposition itself is not yet rejected because the failures are unusually concentrated at one intermediate interface.

## Primary question

> Could each of the six invalid Stage-2 proposition outputs from SPEC-048 have been made structurally impossible to emit through a more restrictive machine-readable proposition contract, without weakening semantic validation, adding repair logic, or encoding source-specific answers?

## Evidence scope

Use only committed repository evidence and code, including:

- SPEC-047 Candidate-B implementation and frozen prompt/schema contracts;
- SPEC-048 raw Stage-2 provider outputs;
- SPEC-048 stage-gate failures;
- SPEC-048 `post-run-failure-taxonomy-audit.json`;
- current proposition model/schema/validation code;
- historical proposition validation tests/contracts as needed.

No new model/provider call or external retrieval is authorized.

## Six authoritative failures

Analyze exactly the six SPEC-048 Stage-2 proposition-construction failures identified by the authoritative taxonomy audit:

1. `noaa-nesdis-jet-stream-2025`
   - comparison-condition validation failure;
2. `crs-legislative-process-r42843-17`
   - comparison-condition validation failure;
3. `epa-ecological-processes-2026`
   - comparison-condition validation failure;
4. `doe-iron-platinum-atomic-structure-2017`
   - transfer-event validation failure;
5. `nhgri-dna-fact-sheet-2020`
   - transfer-event validation failure;
6. `fhwa-traffic-bottleneck-concepts-2016`
   - comparison-condition validation failure.

The NASA duplicate-entity failure is a separate `ENTITY_INVENTORY` failure and serves only as a control demonstrating that SPEC-049 is intentionally scoped to the Stage-2 concentration.

## Required proposition contracts to reconstruct

Reconstruct the intended canonical constraints for each supported proposition type from actual validator/model code, not from assumptions.

At minimum document the exact intended legal shape for:

### `COMPARISON_CONDITION`

Determine and record:

- required roles;
- allowed role cardinality;
- required/allowed relationship type(s);
- required/allowed comparison operator(s);
- nullability constraints;
- whether additional roles are legal;
- whether role uniqueness is required;
- entity-ID requirements.

### `TRANSFER_EVENT`

Determine and record the corresponding constraints:

- required roles;
- cardinality;
- required/allowed relationship type(s);
- comparison-operator constraints;
- additional-role legality;
- role uniqueness;
- entity-ID requirements.

If repository code supports more proposition types than Stage 2 currently exposes, record them separately but do not expand scope.

## Distinguish three kinds of constraint

For every proposition rule, classify where it currently exists:

- `SCHEMA_EXPRESSED` — impossible for structured output to violate if provider respects the JSON schema;
- `PROMPT_ONLY` — described in instructions but not structurally encoded;
- `VALIDATOR_ONLY` — enforced only after model output is parsed;
- `MULTI_LAYER` — enforced in more than one layer.

This is a central deliverable.

## Failure-by-failure counterfactual audit

For each of the six failed Stage-2 outputs:

1. preserve the exact provider proposition object;
2. identify the exact canonical validation rule violated;
3. identify which individual fields were schema-valid;
4. identify the invalid **combination** of fields/roles;
5. determine whether the current JSON schema allowed that combination;
6. determine whether the prompt explicitly prohibited it;
7. determine whether a discriminated/conditional schema could make that exact invalid state unrepresentable;
8. determine whether the proposition's underlying semantic intent was source-supported, unsupported, or cannot be determined mechanically from existing evidence;
9. assign one primary diagnosis from the fixed taxonomy below.

## Fixed diagnosis taxonomy

Each of the six failures must receive exactly one primary diagnosis:

### `STRUCTURALLY_PREVENTABLE`

The output violated a proposition-shape invariant that could be encoded directly in the machine-readable schema/typed interface, making the exact invalid state impossible to emit while preserving the same semantic vocabulary.

### `SEMANTICALLY_WRONG`

The output's underlying proposition meaning is unsupported or wrong; a structurally perfect proposition schema would still permit an invalid-but-well-formed semantic claim of this kind.

### `BOTH_STRUCTURE_AND_SEMANTICS`

The output is structurally malformed and also semantically unsupported; stronger schema would prevent this instance but would not address the full underlying error mechanism.

### `NOT_SCHEMA_EXPRESSIBLE`

The violated invariant cannot reasonably be encoded in the structured-output/schema layer without embedding semantic/source truth or source-specific logic.

### `AMBIGUOUS`

Committed evidence is insufficient to choose among the above.

Do not invent additional primary categories.

## Machine-readable contract feasibility

Evaluate the narrow technical feasibility of making proposition variants structurally discriminated.

At minimum determine whether the current provider structured-output mechanism and repository schema-generation approach can represent a contract conceptually equivalent to:

```text
if proposition_type == COMPARISON_CONDITION:
    roles = exactly LEFT_OPERAND + RIGHT_OPERAND + OUTCOME
    relationship_type = CAUSES
    comparison_operator = GREATER_THAN

if proposition_type == TRANSFER_EVENT:
    roles = exactly EVENT + OBJECT + DESTINATION
    relationship_type = TRANSFERS_TO
    comparison_operator = null
```

Do not implement this contract.

The diagnosis should examine viable schema forms such as discriminated unions / `oneOf` / variant-specific objects / separate arrays or another repository-compatible equivalent, but it must stay at design/feasibility level.

## Important constraint: do not overfit six outputs

A proposed structural contract is valid only if it follows from the pre-existing canonical proposition semantics, not from memorizing the six observed failures.

The diagnostic must prove this by tracing every proposed restriction to existing proposition validation/model rules that predate SPEC-048.

If a restriction cannot be justified from existing canonical semantics, mark it as post-hoc and do not recommend it.

## Stage-2 interface analysis

Assess whether Candidate B v1 violated the deeper decomposition principle:

> Each decomposed stage should expose an interface narrow enough that locally valid output is also structurally compatible with the next deterministic gate.

Answer mechanically where possible:

- Did Stage 2 expose fields independently that are only legal in correlated combinations?
- Did it allow role enums that are valid globally but invalid for the selected proposition subtype?
- Did it allow relationship predicates that are globally trusted but invalid for that subtype?
- Did it allow null/non-null operator combinations inconsistent with subtype?
- Could a model produce a JSON-schema-valid object that was guaranteed to fail proposition validation?

## Counterfactual replay without model calls

Where possible, implement an **offline diagnostic-only schema checker or synthetic schema fixture** that proves whether the six preserved invalid proposition objects would be rejected at schema validation time under a candidate discriminated contract derived exclusively from existing canonical rules.

Allowed:

- local schema construction;
- local JSON/schema validation;
- synthetic valid proposition fixtures;
- replaying preserved SPEC-048 proposition objects through diagnostic-only schema validation.

Forbidden:

- changing production Candidate B;
- changing prompts;
- changing canonical validation;
- repairing preserved outputs;
- rerunning the model.

If diagnostic tooling is added, it must be clearly non-production and not wired into extraction.

## Valid-state preservation test

A stronger contract is only useful if it still admits canonical valid proposition states.

Create deterministic synthetic fixtures proving at minimum:

- one valid `COMPARISON_CONDITION` remains schema-admissible;
- one valid `TRANSFER_EVENT` remains schema-admissible;
- invalid role combinations fail schema validation;
- invalid relationship type for subtype fails;
- invalid comparison-operator state fails;
- duplicate/missing required proposition roles fail where the canonical contract forbids them.

Do not use blind-source answers as synthetic fixtures.

## Required aggregate answers

The canonical report must answer:

1. How many of the six failures are `STRUCTURALLY_PREVENTABLE`?
2. How many are `SEMANTICALLY_WRONG`?
3. How many are `BOTH_STRUCTURE_AND_SEMANTICS`?
4. How many are `NOT_SCHEMA_EXPRESSIBLE` or `AMBIGUOUS`?
5. For how many would a stronger schema have prevented the exact provider output before canonical validation?
6. Would the stronger schema preserve all currently legal proposition variants represented by canonical tests/contracts?
7. Is the Stage-2 regression primarily an **interface expressiveness defect** or a **semantic extraction defect**?
8. Does evidence justify one narrowly scoped Candidate-B-v2 experiment, or should decomposition be abandoned/reframed?

## Decision framework

Recommend exactly one owner-review branch:

### `SCHEMA_CONSTRAINED_B_V2_JUSTIFIED`

Use only if most Stage-2 failures are structurally preventable, restrictions derive from pre-existing canonical rules, and valid-state preservation is demonstrated.

### `DECOMPOSITION_SEMANTIC_FAILURE_NOT_SCHEMA_FIXABLE`

Use if failures are primarily semantically wrong even when proposition structure could be made valid.

### `MIXED_SIGNAL_MORE_DIAGNOSIS_REQUIRED`

Use if structural and semantic causes are too mixed for a clean next experiment.

### `DECOMPOSITION_ABANDON_RECOMMENDED`

Use only if evidence indicates the staged architecture itself introduces broad failure modes unlikely to be addressed by a narrow proposition-interface correction.

Do not implement the selected branch.

## Required artifact

Create:

`examples/evaluations/spec-049-stage2-proposition-contract-diagnosis-20260914/report.json`

Include at minimum:

- immutable SPEC-047/048 evidence references/hashes;
- canonical proposition-rule reconstruction;
- rule-layer matrix (`SCHEMA_EXPRESSED`, `PROMPT_ONLY`, `VALIDATOR_ONLY`, `MULTI_LAYER`);
- six failure audits;
- fixed-taxonomy classifications;
- diagnostic schema-feasibility analysis;
- offline counterfactual replay results;
- valid-state preservation fixture results;
- aggregate answers 1–8;
- exactly one recommended decision-framework branch;
- explicit zero-provider/model/network-call statement;
- validation evidence;
- deviations/blockers if any.

## Protected state

Do not modify:

- Control A;
- Candidate B v1 production implementation;
- SPEC-047 prompt/schema contracts;
- SPEC-048 raw outputs and evidence;
- canonical proposition models/validation;
- trusted semantic vocabulary;
- grounding/provenance;
- representation strategy/renderers;
- SPEC-038 UI/navigation baseline.

## Explicitly forbidden

Do not:

- call OpenAI or another provider/model;
- use external web/network retrieval;
- rerun Control A or Candidate B;
- implement Candidate B v2;
- edit Stage-2 production schema/prompt;
- repair or reinterpret provider outputs through a model;
- weaken proposition validation;
- add new proposition types;
- alter trusted relationship vocabulary;
- add source-specific schema exceptions;
- create learner-facing artifacts;
- promote any extractor.

## Validation

At minimum:

- verify SPEC-047 and SPEC-048 implementation/evidence identities;
- reconcile exactly six authoritative Stage-2 proposition failures;
- verify every proposed structural restriction traces to pre-existing canonical proposition rules;
- run diagnostic schema replay tests;
- run focused tests for any diagnostic tooling;
- run control-plane tests;
- run full offline suite;
- validate JSON artifacts;
- secret-safety and provenance checks;
- `git diff --check`;
- verify no provider/model/network calls;
- verify protected production code/evidence unchanged.

## Completion state

On completion:

- set SPEC-049 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear the active `STATUS.md` packet to `NONE`;
- record the objective diagnosis and exactly one recommended decision branch;
- commit/push according to repository protocol;
- stop at `OWNER_REVIEW`;
- do not prepare or implement Candidate B v2 automatically.

## Owner review question

> Did Candidate B v1 fail because Stage 2 exposed proposition states that should have been structurally impossible, strongly enough to justify one narrowly scoped schema-constrained Candidate-B-v2 experiment — or did decomposition simply expose a deeper semantic extraction failure?
