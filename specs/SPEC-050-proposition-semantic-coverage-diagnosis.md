# SPEC-050 — Proposition Semantic Coverage Diagnosis

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Diagnose the deeper semantic signal revealed by SPEC-049 before implementing Candidate B v2 or expanding the canonical semantic model.

SPEC-049 showed that all six failed Stage-2 proposition outputs were structurally preventable by a stricter subtype-specific interface, but five of those failures also represented source-supported meanings that do **not** fit the current canonical proposition semantics as emitted.

The next question is therefore:

> Are those source-supported meanings already representable faithfully elsewhere in the existing semantic model, meaning Stage 2 should simply avoid forcing them into proposition types, or do they expose a genuine semantic coverage gap in the canonical model?

This packet is diagnostic only. It must not add proposition types, change Stage 2, change the trusted vocabulary, rerun a model, or alter any production behavior.

## Owner verdict entering this packet

SPEC-049 objective diagnosis:

`MIXED_SIGNAL_MORE_DIAGNOSIS_REQUIRED`

Accepted evidence:

- 6 Stage-2 proposition failures analyzed;
- 1 is `STRUCTURALLY_PREVENTABLE` only;
- 5 are `BOTH_STRUCTURE_AND_SEMANTICS`;
- a stricter subtype-specific proposition contract would reject all six exact failed outputs before canonical validation;
- valid canonical `COMPARISON_CONDITION` and `TRANSFER_EVENT` variants remain expressible under such a stricter contract;
- four source-supported standalone comparisons do not fit the canonical causal `COMPARISON_CONDITION` form;
- at least one transfer-like statement conflicts with canonical `TRANSFER_EVENT` role semantics;
- Candidate B v2 is not yet authorized because schema tightening alone would not explain how those source-supported meanings should be represented.

## Protected canonical proposition semantics

The canonical proposition model remains unchanged in this packet.

### `COMPARISON_CONDITION`

Canonical meaning is a **comparison used as a causal condition**, not a generic comparison statement.

Required semantics:

```text
LEFT_OPERAND
RIGHT_OPERAND
OUTCOME
comparison_operator = GREATER_THAN
relationship_type = CAUSES
```

A standalone statement such as “A is greater than B” is not automatically a valid `COMPARISON_CONDITION`.

### `TRANSFER_EVENT`

Canonical meaning is an explicit transfer event with:

```text
EVENT       → PROCESS entity
OBJECT      → thing transferred
DESTINATION → destination/recipient, not PROCESS
relationship_type = TRANSFERS_TO
comparison_operator = null
```

Do not reinterpret these canonical contracts merely to accommodate preserved failures.

## Evidence scope

Use only immutable committed evidence from SPEC-047 through SPEC-049 and the original frozen source packets.

Primary cases are the five SPEC-049 failures diagnosed as `BOTH_STRUCTURE_AND_SEMANTICS`.

Also use:

- the one `STRUCTURALLY_PREVENTABLE` case as a control;
- valid proposition fixtures/tests from the canonical model;
- historical Control-A outputs where they illuminate how the same source was represented without changing historical truth.

No external retrieval and no provider/model call are allowed.

## Fixed semantic-destination taxonomy

For each source-supported meaning implicated in the five mixed failures, assign exactly one primary destination classification:

### `CANONICAL_PROPOSITION_FIT`

The source meaning genuinely fits an existing canonical proposition type, and the failure arose because Candidate B emitted the wrong roles/predicate/operator/entity typing.

### `EXISTING_RELATIONSHIP_FIT`

The meaning is representable faithfully as one or more existing canonical relationships between existing/source-supported entities, without inventing a new proposition type.

### `CLAIM_ONLY_FIT`

The meaning is source-supported and useful, but the current trusted semantic graph does not need a typed relationship/proposition for it. It can be preserved faithfully as a grounded claim/explanatory statement without adding topology.

This is not a failure if the claim remains source-grounded and downstream representation can still use it appropriately.

### `TRUE_SEMANTIC_COVERAGE_GAP`

The meaning is materially important and source-supported, cannot be faithfully represented by an existing proposition, existing relationship(s), or grounded claim without losing semantics needed by the compiler, and therefore indicates a real gap in the canonical semantic model.

This category requires strong evidence. Do not use it merely because the model emitted an unsupported proposition form.

### `AMBIGUOUS`

Committed evidence is insufficient to distinguish the above without introducing new assumptions.

No other primary destination categories are allowed.

## Core analytical distinction

SPEC-050 must explicitly separate:

```text
SOURCE-SUPPORTED MEANING
        ↓
Does the compiler need typed semantic topology for it?
        ↓
YES → existing proposition/relationship fit or true coverage gap
NO  → grounded claim may be the correct representation
```

The knowledge compiler must not force every true sentence into a graph edge or typed proposition.

This principle is important because representation diversity already allows concise prose and sparse representations when trusted structure is insufficient.

## Required analysis

### 1. Reconstruct the five mixed cases

For each case record:

- source ID/domain;
- exact source-supported meaning;
- exact Candidate-B proposition output(s);
- why canonical proposition validation rejected it;
- SPEC-049 structural diagnosis;
- semantic intent identified in SPEC-049.

### 2. Test existing semantic destinations

For each source-supported meaning, evaluate in this order:

1. Can it truthfully instantiate the existing canonical proposition type with correct roles and semantics?
2. If not, can one or more existing trusted relationships encode the meaning without distortion?
3. If not, can a grounded claim preserve the useful meaning without requiring graph topology?
4. Only then consider whether it is a true semantic coverage gap.

Do not create actual repaired historical outputs. This is a counterfactual classification exercise.

### 3. Preserve topology discipline

For every proposed existing-relationship fit, state:

- exact current predicate(s);
- direction;
- source/target semantic roles;
- why this does not overstate the source.

If no existing predicate fits precisely, do not approximate with a nearby predicate.

### 4. Evaluate claim-only sufficiency

For any `CLAIM_ONLY_FIT`, answer mechanically where possible:

- would the grounded claim remain available to the explanatory layer under current architecture?
- would omitting a typed proposition remove any structure currently required by structure detection or representation selection?
- would the learner lose essential semantics, or merely lose unnecessary graph topology?

Do not modify downstream code to make claim-only fit look better.

### 5. Evaluate true coverage gaps conservatively

For any proposed `TRUE_SEMANTIC_COVERAGE_GAP`, establish all of:

- meaning is explicitly source-supported;
- meaning recurs or is structurally important enough to warrant typed representation;
- existing relationships cannot encode it truthfully;
- existing propositions cannot encode it truthfully;
- claim-only preservation would materially impair compiler understanding/representation;
- the gap is conceptual, not merely a Candidate-B prompt/schema mistake.

If these conditions are not satisfied, do not classify as coverage gap.

### 6. Use the structurally-preventable case as control

Confirm whether the one SPEC-049 `STRUCTURALLY_PREVENTABLE` failure would be resolved simply by a stricter proposition contract without any semantic destination change.

This guards against overgeneralizing the five mixed cases.

### 7. Compare against historical Control A

Where Control A admitted or rejected the same source, inspect preserved historical semantic output only as comparative evidence.

Questions:

- Did Control A preserve the same meaning?
- If yes, was it encoded as relationship, claim, proposition, or omitted?
- Did Control A's choice suggest that typed proposition structure was unnecessary?

Do not treat Control A as ground truth merely because it passed.

## Aggregate questions

The canonical report must answer:

1. How many mixed cases classify as `CANONICAL_PROPOSITION_FIT`?
2. How many classify as `EXISTING_RELATIONSHIP_FIT`?
3. How many classify as `CLAIM_ONLY_FIT`?
4. How many classify as `TRUE_SEMANTIC_COVERAGE_GAP`?
5. How many remain `AMBIGUOUS`?
6. Does the evidence justify expanding the canonical proposition model now?
7. Would a Candidate-B v2 that simply **omits unsupported proposition forms** preserve more truth than Candidate B v1 without weakening validation?
8. Is stricter subtype-specific schema still necessary regardless of semantic destination?
9. What single next branch is best supported?

## Fixed next-branch taxonomy

Recommend exactly one:

### `SCHEMA_CONSTRAINED_B_V2_WITH_SEMANTIC_OMISSION`

Use when mixed cases are largely representable elsewhere or safely claim-only, so Candidate B v2 should structurally prohibit invalid proposition states and instruct Stage 2 to omit proposition forms that do not fit canonical semantics.

This branch does **not** authorize implementation yet.

### `SEMANTIC_MODEL_EXPANSION_DIAGNOSIS`

Use when one or more strong `TRUE_SEMANTIC_COVERAGE_GAP` findings indicate the canonical model is too narrow, and those gaps should be designed before another extractor experiment.

### `ABANDON_DECOMPOSITION_RETURN_TO_CONTROL_A`

Use when failures show decomposition itself is forcing semantic distortions or complexity without a credible narrow correction.

### `MORE_EVIDENCE_REQUIRED`

Use when committed evidence cannot distinguish the above.

No other branch is allowed.

## Important non-goal

Do **not** assume generic comparison support should be added because four failed outputs contained comparisons.

A standalone comparison might be:

- useful as a grounded claim;
- representable through another existing relation;
- not structurally important to the learner model;
- or genuinely deserving of a future comparison proposition.

SPEC-050 exists to distinguish these possibilities rather than jumping directly to ontology expansion.

## Required artifact

Create:

`examples/evaluations/spec-050-proposition-semantic-coverage-diagnosis-20260914/report.json`

The report must contain at minimum:

- immutable evidence identities/hashes;
- five mixed-case reconstructions;
- one structurally-preventable control reconstruction;
- primary semantic-destination classification per mixed case;
- counterfactual existing-proposition/relationship/claim analysis;
- Control-A comparison where applicable;
- aggregate destination counts;
- answers to all nine aggregate questions;
- exactly one recommended next branch;
- explicit zero-call/zero-change statement;
- test/integrity evidence;
- owner-review state.

A Markdown companion is optional.

## Validation

At minimum:

- verify SPEC-047/048/049 canonical evidence identities;
- reconcile all six Stage-2 proposition failures exactly;
- ensure exactly five mixed cases and one structural-only control are analyzed;
- validate fixed semantic-destination taxonomy;
- validate exactly one primary destination per mixed case;
- validate fixed next-branch taxonomy;
- validate exactly one recommended next branch;
- run focused diagnostic tests if tooling is added;
- run control-plane tests;
- run full offline suite;
- validate JSON;
- run provenance/secret-safety checks;
- run `git diff --check`;
- verify no provider/model/network call occurred;
- verify protected implementation and historical evidence unchanged.

Prefer evidence-only artifacts and test-local diagnostic helpers over production-code changes.

## Protected state

Do not modify:

- Control A;
- Candidate B v1;
- SPEC-047/048/049 prompts, schemas, raw outputs, stage gates, or evidence;
- canonical proposition types/semantics;
- canonical relationship vocabulary;
- entity types;
- grounding/provenance behavior;
- strict declared-identity validation;
- canonical KnowledgeModel validation;
- representation strategy/renderers;
- learner-facing UI/navigation.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external web/network retrieval;
- rerun any extractor;
- implement Candidate B v2;
- add generic comparison proposition support;
- add or change transfer proposition semantics;
- add trusted predicates;
- repair preserved outputs;
- change prompts/schemas/validators;
- force source-supported claims into graph topology;
- weaken fail-closed behavior;
- implement the recommended branch;
- promote an extractor or baseline.

## Completion state

On completion:

- set SPEC-050 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- record objective semantic-destination findings and exactly one recommended branch;
- commit/push according to repository protocol;
- stop at `OWNER_REVIEW`;
- do not automatically prepare or implement follow-up work.

## Owner review question

> Do the five mixed Stage-2 failures expose a real gap in the semantic model, or was Candidate B v1 simply trying to force source-supported but non-topological meanings into proposition types they never belonged in — and what should we test next?
