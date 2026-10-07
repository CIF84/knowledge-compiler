# SPEC-066 — Semantic Validation Boundary Experiment

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

SPEC-065 established that exact/restricted deterministic checks can validate identity, provenance, schema, coverage, quantities, and structural invariants, but cannot prove the meaning of genuinely novel synthesis or abstraction.

Mechanical result:

`VALIDATION_BOUNDARY_INSUFFICIENT`

SPEC-066 isolates the semantic trust problem before any live synthesis execution.

The experiment asks:

> **Can a conservative, auditable semantic-entailment boundary distinguish faithful abstractive transformations from subtle semantic drift well enough to gate future generative compression?**

No live synthesis of the three frozen source cases is authorized.

## Owner verdict entering this packet

Record SPEC-065 owner verdict:

`DETERMINISTIC_TRUST_BOUNDARY_CONFIRMED_SEMANTIC_ENTAILMENT_GAP_NEXT`

Accepted architecture:

```text
trusted substrate
      ↓
GENERATOR
candidate synthesis / abstraction
      ↓
DETERMINISTIC VALIDATION
identity / provenance / schema /
coverage / quantities / invariants
      ↓
SEMANTIC VALIDATION
does the candidate follow from evidence?
      ↓
ADMIT / REJECT / UNCERTAIN
```

Canonical rule:

> **UNCERTAIN fails closed.**

Do not treat a semantic judge's confidence as proof.

## SPEC-065 gaps to resolve

The experiment must explicitly cover all four frozen gaps:

1. novel semantic synthesis/paraphrase;
2. novel shared mechanism/abstraction;
3. natural-language quantities, entity substitution, and implicit dependencies;
4. relations projected onto compressed endpoints.

## Core hypothesis

A decomposed semantic-validation protocol may be safer and more auditable than holistic “is this summary faithful?” judgment.

Candidate:

```text
candidate abstraction
       ↓
decompose into atomic commitments
       ↓
for each commitment:
  identify supporting frozen evidence
  classify entailment / contradiction / uncertain
       ↓
audit qualifications / scope / causality / quantities
       ↓
recompose coverage
       ↓
ADMIT only if every required commitment passes
```

SPEC-066 must test this hypothesis rather than assume it.

## Scope

This is a validation-boundary experiment.

Allowed:
- deterministic fixture construction from frozen repository evidence;
- schemas/prompts for bounded semantic judgment;
- offline deterministic validators;
- offline fixtures with known expected outcomes;
- optional live semantic-judge calls **only if separately authorized below by this SPEC's live authority section**.

This packet is initially **OFFLINE_ONLY**. Provider/model calls: **0**.

The packet must first determine whether deterministic decomposition plus frozen labels can resolve enough cases. If model judgment is still required, it must freeze a later judge-execution contract and stop.

Do not silently call a model.

## Fixture corpus

Build a frozen, domain-diverse semantic-validation fixture corpus with at least 48 cases.

Use trusted frozen evidence already in the repository; no external retrieval.

Required categories, with both positive and negative examples where meaningful:

- exact entailment;
- faithful paraphrase;
- faithful synthesis of multiple commitments;
- valid explanatory abstraction;
- unsupported abstraction;
- overgeneralization;
- lost qualification;
- strengthened certainty;
- correlation → causation drift;
- entity/referent substitution;
- quantity/unit drift;
- temporal/scope drift;
- implicit dependency preserved;
- implicit dependency invented;
- valid relation projection onto compressed endpoints;
- invalid relation projection due to changed scope;
- contradiction;
- evidence insufficient / genuinely uncertain.

Ensure difficult near-miss negatives, not only obvious corruption.

Fixture labels are evaluation truth for this experiment and must be frozen before validator evaluation.

## Anti-contamination rule

Validator logic/prompts may be designed using category definitions, but must not route on:
- fixture ID;
- source/domain identity;
- expected label;
- literal memorized fixture text.

Include no-hardcoding tests.

## Validation protocols to compare

### Protocol A — deterministic restricted proof

Reuse/freeze SPEC-065 capabilities:
- exact identity;
- exact evidence references;
- literal quantities/units where applicable;
- frozen relationship assertions;
- schema/coverage invariants;
- exact/restricted structural encoding.

Expected strength: high precision, low coverage.

### Protocol B — deterministic decomposition

Attempt generic offline decomposition into candidate atomic commitments using only operations that are genuinely deterministic.

If natural-language decomposition itself requires semantic interpretation, mark that boundary explicitly rather than pretending it is solved.

Evaluate whether Protocol B increases safe coverage.

### Protocol C — bounded semantic judge contract

Design and freeze, but do not execute unless later authorized.

Judge task is narrow:
- evidence + one atomic candidate commitment;
- return `ENTAILED`, `CONTRADICTED`, or `UNCERTAIN`;
- identify exact evidence IDs;
- separately flag scope, epistemic force, causality, entity, quantity/unit, temporal, and relation-projection issues.

The judge must not rewrite the candidate or repair it.

### Protocol D — optional independent adjudication design

Define a later experiment option for independent second judgment on first-judge `ENTAILED` cases or selected risk classes.

Do not assume two agreeing judges equal truth.

The report must analyze correlated-error risk and whether independent prompting/model diversity would actually add evidence.

No Protocol-D calls under SPEC-066.

## Atomic semantic-commitment schema

Freeze a schema that can represent, where applicable:

- subject/entity references;
- predicate/relation;
- object/value;
- quantity + unit;
- temporal scope;
- spatial/domain scope;
- condition;
- modality/uncertainty;
- causal force;
- attribution;
- supporting evidence IDs.

The schema must support `UNRESOLVED` fields rather than forcing interpretation.

## Semantic verdict schema

For each atomic commitment:

- `verdict`: `ENTAILED | CONTRADICTED | UNCERTAIN`;
- `supporting_evidence_ids`;
- `contradicting_evidence_ids`;
- `scope_preserved`;
- `epistemic_force_preserved`;
- `causal_force_preserved`;
- `entities_preserved`;
- `quantities_units_preserved`;
- `temporal_context_preserved`;
- `relation_projection_valid`;
- `reason_code`;
- `notes` bounded and non-authoritative.

Admission rule:

> all atomic commitments must be ENTAILED and all required preservation flags must pass; otherwise reject/fail closed.

No majority vote.

## Holistic-vs-decomposed control

Include a diagnostic comparing the proposed decomposed protocol against a hypothetical holistic verdict contract.

The experiment should document failure modes expected from holistic judgment:
- plausible-summary bias;
- missed qualification;
- hidden conjunction;
- partial entailment;
- scope collapse;
- causal strengthening.

Do not claim superiority without fixture evidence.

## Deterministic capability matrix

For every semantic operation classify validation capability:

- `PROVABLE_DETERMINISTICALLY`
- `RESTRICTED_DETERMINISTIC_PROOF`
- `REQUIRES_SEMANTIC_JUDGMENT`
- `NOT_VALIDATABLE_WITH_CURRENT_EVIDENCE`

This matrix is a first-class output.

## Model-judge risk analysis

The report must explicitly analyze:

- correlated generator/judge errors;
- shared-model bias if generator and judge use the same family;
- verbosity/plausibility bias;
- judge sensitivity to evidence ordering;
- false certainty;
- prompt injection/content contamination risk from source text;
- whether a judge can verify abstraction rather than merely agree with it.

Do not solve these rhetorically; map each risk to a mitigation or unresolved limitation.

## Future judge contract

If semantic judgment remains required, freeze a proposed later live contract.

Preferred first candidate:
- model: `gpt-6.1-sol`;
- reasoning effort: `high`;
- `store=False`;
- structured output;
- zero retries;
- zero repair/follow-up calls;
- one atomic commitment per judgment call or a rigorously justified bounded batch.

However, SPEC-066 must calculate the resulting call cost/scale before recommending it. If one-call-per-atom is operationally excessive, propose a bounded batching contract while preserving per-atom verdicts.

Provider compatibility must remain unverified unless checked without a provider call. Do not substitute models silently.

## Future live-call budget design

Do not authorize calls now.

Produce two candidate budgets:

1. **precision-first** — one atomic commitment per call;
2. **bounded-batch** — small fixed number of atomic commitments per call with independent verdicts.

For the frozen fixture corpus and projected SPEC-065 live synthesis, estimate:
- calls;
- input/output tokens where mechanically estimable;
- latency implications;
- failure/retry policy (still zero retries by default);
- judge cost as proportion of generator cost where price data is unavailable.

Do not invent monetary prices.

## Mechanical evaluation metrics

Against frozen fixture labels report:

- coverage;
- admission rate;
- rejection rate;
- uncertain rate;
- false admission count/rate;
- false rejection count/rate;
- category-level results;
- preservation-flag accuracy;
- relation-projection accuracy;
- quantity/entity/scope/causal-drift detection.

For trust-boundary evaluation, **false admission is the primary failure**.

A protocol with lower coverage but zero false admissions may be preferable.

## Decision criteria

SPEC-066 offline branch chooses exactly one:

### `DETERMINISTIC_SEMANTIC_BOUNDARY_SUFFICIENT`
Offline decomposition/restricted proof resolves the fixture set conservatively with zero false admissions and useful coverage sufficient for future synthesis admission.

### `SEMANTIC_JUDGE_REQUIRED_LIVE_CONTRACT_READY`
Deterministic methods remain insufficient, but a bounded judge contract, fixtures, risk model, and execution budgets are ready for separate authorization.

### `SEMANTIC_VALIDATION_ARCHITECTURE_UNSAFE`
The proposed judge architecture cannot adequately control correlated error or semantic drift.

### `FIXTURE_EVIDENCE_INSUFFICIENT`
The corpus is too weak/unrepresentative to justify the next step.

### `INCONCLUSIVE`

No live judge call is authorized by these branches.

## Required outputs

Create:

`examples/evaluations/spec-066-semantic-validation-boundary-20261007/`

Include at minimum:
- `report.json`;
- frozen fixture corpus + labels;
- atomic commitment schema;
- semantic verdict schema;
- Protocol A/B results;
- deterministic capability matrix;
- SPEC-065 four-gap coverage matrix;
- holistic-vs-decomposed analysis;
- model-judge risk register;
- future judge prompts/schema identities;
- precision-first and bounded-batch execution manifests/budgets;
- protected-state hashes;
- deterministic regeneration evidence;
- zero-call statement;
- owner verdict `PENDING`.

## Project vision update

Update `docs/PROJECT-VISION.md` minimally:

- deterministic validation has a semantic-entailment boundary;
- abstractive candidate generation and semantic admission are separate trust problems;
- semantic judgment, if required, is a bounded trust component, not proof by model confidence;
- uncertain semantic validation fails closed.

Do not claim semantic judging is validated.

## Protected state

Do not modify:
- SPEC-065 evidence/harness;
- SPEC-064 and earlier evidence;
- frozen three-source substrate;
- production validators;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance;
- production StructureDetector;
- production representation/UI;
- accepted SPEC-038 baseline.

Prefer isolated experimental validators/fixtures.

## Explicitly forbidden

Do not:
- call any model/provider;
- retrieve external sources;
- execute SPEC-065 live synthesis;
- execute semantic-judge calls;
- weaken validators;
- treat lexical overlap as semantic entailment;
- route on fixture/source/domain identity;
- hard-code expected labels;
- use owner comments as fixture truth unless independently encoded/frozen as an explicit test case with provenance;
- promote experimental validators;
- change production behavior;
- do UI/visualization work;
- infer owner verdict;
- activate follow-up live execution.

## Validation

At minimum:
- focused SPEC-066 tests;
- fixture label freeze before protocol evaluation;
- no-hardcoding tests;
- Protocol A/B deterministic regeneration;
- capability-matrix consistency;
- SPEC-065 four-gap reconciliation;
- protected hashes;
- control-plane tests;
- full offline suite;
- JSON/schema validation;
- secret safety;
- `git diff --check`;
- zero provider/model/network calls.

## Completion state

On completion:
- set SPEC-066 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report fixture results, false-admission count, deterministic coverage, unresolved semantic categories, judge risk/budget findings, mechanical branch, and recommended next step;
- stop at `OWNER_REVIEW`;
- do not execute any future judge manifest.

## Owner review question

> **Have we designed a semantic trust boundary conservative enough to evaluate genuinely abstractive model output without confusing model agreement, lexical similarity, or plausible language with entailment?**
