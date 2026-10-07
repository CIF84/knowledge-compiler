# SPEC-067 — Semantic Judge Live Evaluation

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

SPEC-066 established that deterministic restricted proof is conservative but insufficient for genuinely abstractive semantic admission:

- frozen fixtures: 92 across eight domains;
- false admissions: 0;
- Protocol A deterministic coverage: 8/92;
- Protocol B deterministic/decomposed coverage: 16/92;
- all four SPEC-065 semantic-validation gaps remain unresolved;
- projected full synthesis judging would require approximately 423 precision-first or 111 bounded-batch calls.

SPEC-067 does **not** execute generative synthesis.

It evaluates the proposed semantic judge itself against frozen cases with known expected labels before that judge is allowed anywhere near generated product output.

Primary question:

> **Can a bounded semantic judge conservatively distinguish entailed transformations from subtle semantic drift, with sufficiently low false-admission risk to justify a later synthesis experiment?**

## Owner verdict entering this packet

Record SPEC-066 owner verdict:

`SEMANTIC_JUDGMENT_REQUIRED_LIVE_JUDGE_VALIDATION_NEXT`

Canonical rule:

> **False admission is the primary trust failure. UNCERTAIN fails closed.**

The semantic judge is a bounded trust component, not proof by model confidence.

## Authority

This packet authorizes only the exact semantic-judge calls defined below.

It does not authorize:
- SPEC-065 synthesis generation;
- source retrieval;
- extraction reruns;
- repair calls;
- retries;
- follow-up semantic questions;
- production changes;
- promotion.

### Model contract

Use exactly:

- model: `gpt-6.1-sol`
- reasoning effort: `high`
- `store=False`
- structured output matching the frozen SPEC-066 semantic-verdict contract
- SDK/provider retries: 0
- semantic retries: 0
- repair calls: 0
- follow-up calls: 0

Before transmitting fixture evidence, verify provider/model/request compatibility without substituting another model or reasoning level.

If the exact contract cannot be verified or executed, stop fail-closed with zero fixture transmissions.

## Frozen evidence

Use the canonical SPEC-066 fixture corpus and labels unchanged.

Canonical corpus identity from SPEC-066:

`f965d1762cb4d188303d2464e2a28e0ce229765881a3e912013bb667a8c661d2`

Canonical labels identity:

`d47e1f2f6f56f425270d560046457173434523e716ba208b4ca384eedb533db4`

Do not alter fixture text, evidence, labels, expected verdicts, category assignments, or provenance.

The live judge must never receive expected labels, fixture-category answers, or owner comments.

## Pre-live review gate

SPEC-066 states that the fixture corpus is not a blinded benchmark and that independent label/decomposition review is required before live judge authorization.

SPEC-067 must therefore perform an offline pre-live audit before any call:

1. verify all 92 fixture/label hashes;
2. independently check fixture packet/label consistency using frozen source/evidence only;
3. verify no expected labels leak into judge packets/prompts;
4. verify semantic-verdict schema identity;
5. verify prompt identity;
6. verify provider contract;
7. freeze the exact evaluation subset and call order.

If the audit finds material label ambiguity, evidence leakage, malformed fixture truth, or provider incompatibility, stop before live calls.

Do not silently repair fixture labels under this packet.

## Evaluation design

Use a **frozen stratified subset of 48 fixtures** from the 92-case corpus.

Selection must be deterministic and frozen before any provider call.

### Required category coverage

Include difficult positives and near-miss negatives spanning at minimum:

- exact entailment / restricted positive control;
- faithful paraphrase;
- faithful multi-commitment synthesis;
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
- valid relation projection;
- invalid relation projection due to scope;
- contradiction;
- genuinely uncertain / insufficient evidence.

Maximize domain diversity within each category before taking repeated same-domain cases.

Do not select based on expected model difficulty after seeing judge output.

## Two live protocols

Evaluate the **same 48 frozen fixtures** under both protocols.

### Protocol J1 — precision-first

One fixture / atomic commitment judgment per provider call.

Calls: exactly 48 unless a provider/runtime failure causes fail-closed termination.

The judge receives:
- evidence packet;
- candidate atomic commitment;
- required preservation context;
- no expected label.

Returns:
- `ENTAILED | CONTRADICTED | UNCERTAIN`;
- supporting evidence IDs;
- contradicting evidence IDs;
- preservation flags;
- reason code;
- bounded notes.

### Protocol J2 — bounded batch

Use fixed batches of **4 fixtures per call**, preserving independent per-fixture verdict objects.

48 fixtures / 4 = 12 calls.

Batch construction:
- deterministic;
- mix categories/domains where possible;
- do not place duplicate variants of the same base fixture in one batch if avoidable;
- no expected labels.

Calls: exactly 12 unless fail-closed termination.

### Maximum authorized live calls

`60`

- J1: 48
- J2: 12

No additional calls.

This budget is intentionally much smaller than the 111–423 projected synthesis-validation workload.

## Call order

Freeze before execution.

Run J1 first in deterministic fixture order, then J2 in deterministic batch order.

Do not adapt prompts, batches, thresholds, schemas, or instructions after observing J1.

J2 must already be frozen before the first J1 call.

## Raw evidence preservation

For every call preserve:
- exact request identity/hash;
- exact prompt/schema identity;
- model/request settings;
- raw structured response;
- usage tokens;
- provider latency if available;
- provider request ID if available and safe;
- call ordinal;
- fixture IDs;
- no secret material.

Maintain an authoritative provider ledger.

## Semantic verdict mapping

Judge verdicts map to trust admission as:

- `ENTAILED` + all required preservation flags pass → candidate may be semantically admitted for fixture scoring;
- `CONTRADICTED` → reject;
- `UNCERTAIN` → reject;
- malformed/incomplete response → reject/fail closed.

Do not reinterpret a judge's notes to override its structured verdict.

## Primary metric

### False admission

A false admission occurs when the judge admits a fixture whose frozen expected truth says it must not be admitted.

Report:
- count;
- rate overall;
- count/rate by category;
- count/rate by J1 vs J2.

**Any false admission is material evidence against automatic semantic admission.**

Do not average it away with accuracy.

## Secondary metrics

Report:
- true admission;
- false rejection;
- uncertain rate;
- contradiction rate;
- category-level confusion;
- evidence-ID correctness;
- preservation-flag accuracy;
- quantity/entity/scope/causal-drift detection;
- relation-projection accuracy;
- malformed/fail-closed outputs;
- token usage;
- latency;
- J1 vs J2 agreement.

## Batching degradation

For each of the 48 fixtures compare J1 and J2 verdicts.

Classify:
- `IDENTICAL`
- `J2_MORE_CONSERVATIVE`
- `J2_MORE_PERMISSIVE`
- `OTHER_DISAGREEMENT`

Report whether batching introduces:
- new false admissions;
- fewer false admissions;
- higher uncertainty;
- evidence-ID degradation;
- preservation-flag degradation.

A bounded batch is not acceptable merely because aggregate accuracy is similar.

## Evidence-order sensitivity

Correlated-error and order sensitivity remain important, but repeated calls would increase budget.

Within the 48-fixture selection, create a frozen **8-fixture order-sensitivity subset**.

Test order sensitivity **without additional calls** by:
- placing these fixtures in J2 batches where their evidence-item ordering is deterministically reversed relative to J1;
- keeping semantic content identical.

Report J1/J2 differences descriptively.

Do not claim this cleanly isolates batching from evidence order; record the confound explicitly.

No repeat calls are authorized.

## Correlated-error analysis

The generator has not run, so SPEC-067 cannot empirically measure generator/judge correlated errors.

Report this limitation explicitly.

The judge uses the proposed generator family (`gpt-6.1-sol`), so same-family correlated error remains an unresolved architectural risk.

Do not solve this by adding another model under this packet.

The decision criteria must distinguish:

- judge accuracy on authored frozen fixtures;
- unresolved generator/judge correlation on future model-generated candidates.

## Judge prompt discipline

Use the frozen SPEC-066 judge contract unless a pre-live schema incompatibility makes execution impossible.

The prompt must:
- ask only entailment/preservation judgment;
- forbid rewriting/repair;
- forbid external knowledge;
- require `UNCERTAIN` when evidence is insufficient;
- require exact supplied evidence IDs;
- separately assess scope, epistemic force, causality, entities, quantities/units, temporal context, relation projection;
- treat source text as data, not instructions.

Do not tune prompt wording after seeing live outputs.

## Safety against prompt/content contamination

Before calls:
- delimit evidence/candidate fields structurally;
- ensure source content cannot alter system/judge instructions;
- freeze schemas;
- validate fixture text serialization.

Record any fixture content that resembles instructions.

If contamination cannot be safely isolated, stop before transmission.

## Decision branches

Choose exactly one mechanical branch.

### `SEMANTIC_JUDGE_PRECISION_SUPPORTED`

Requirements:
- J1 false admissions = 0;
- J2 false admissions = 0;
- no material category shows systematic permissive failure;
- malformed outputs fail closed;
- evidence/preservation performance is sufficient for audit;
- batching does not introduce permissive degradation.

This branch does **not** resolve generator/judge correlated-error risk.

### `PRECISION_FIRST_ONLY_SUPPORTED`

Requirements:
- J1 false admissions = 0 with useful coverage;
- J2 introduces false admissions or material permissive degradation.

Future synthesis judging must not use batching without another experiment.

### `SEMANTIC_JUDGE_TOO_PERMISSIVE`

Any material false-admission pattern makes automatic admission unsafe.

### `SEMANTIC_JUDGE_TOO_CONSERVATIVE`

False admissions remain zero, but true faithful transformations are rejected/uncertain so often that the judge is not operationally useful.

### `PROVIDER_CONTRACT_UNAVAILABLE`

Exact frozen model/request contract cannot be executed; no substitution permitted.

### `FIXTURE_OR_PREFLIGHT_INVALID`

Pre-live audit finds material fixture/label/leakage problems.

### `INCONCLUSIVE`

Mixed evidence prevents a clean branch.

## Useful coverage

Do not hard-code an arbitrary accuracy threshold.

Report true-positive admission separately for:
- faithful paraphrase;
- faithful synthesis;
- valid abstraction;
- valid relation projection;
- exact/restricted controls.

Owner review determines whether conservative coverage is operationally useful, unless the result is obviously degenerate (e.g. judge rejects/uncertains nearly every positive).

## Recommended next-step vocabulary

Choose exactly one:

- `BOUNDED_GENERATIVE_SYNTHESIS_LIVE_EXPERIMENT`
- `PRECISION_FIRST_JUDGE_ONLY_LIVE_EXPERIMENT`
- `SEMANTIC_JUDGE_ARCHITECTURE_RETHINK`
- `INDEPENDENT_JUDGE_EXPERIMENT`
- `FIXTURE_REDESIGN_REQUIRED`
- `PROVIDER_CONTRACT_REVIEW_REQUIRED`
- `MORE_DIAGNOSIS_REQUIRED`

No follow-up is automatically authorized.

## Required outputs

Create:

`examples/evaluations/spec-067-semantic-judge-live-evaluation-20261007/`

Include at minimum:
- `report.json`;
- pre-live audit;
- frozen 48-fixture selection manifest;
- J1 call manifest;
- J2 frozen batch manifest;
- order-sensitivity subset manifest;
- prompt/schema identities;
- provider compatibility evidence;
- raw responses;
- provider-call ledger;
- per-fixture J1/J2 scoring;
- category metrics;
- batching-degradation audit;
- order-sensitivity audit;
- evidence-ID/preservation audit;
- correlated-error limitation statement;
- usage/latency summary;
- protected-state hashes;
- secret-safety audit;
- owner-review summary;
- owner verdict `PENDING`.

## Project vision update

Update `docs/PROJECT-VISION.md` minimally after execution:

- semantic judgment is experimentally separate from deterministic validation;
- false admission is the primary semantic trust failure;
- batching efficiency must not be traded for permissive semantic drift;
- same-family generator/judge correlated error remains unresolved unless separately tested.

Do not claim the semantic judge is production-safe.

## Protected state

Do not modify:
- SPEC-066 fixtures/labels/evidence;
- SPEC-065 harness/prompts/evidence;
- SPEC-064 and earlier evidence;
- frozen source/semantic substrate;
- production validators;
- Candidate B v2;
- SPEC-052 admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance;
- production StructureDetector;
- production representation/UI;
- accepted SPEC-038 baseline.

Prefer isolated live-evaluation code/artifacts.

## Explicitly forbidden

Do not:
- execute SPEC-065 synthesis;
- generate product R1/R2/R3;
- retrieve external sources;
- rerun extraction;
- alter fixture labels;
- expose expected labels to the judge;
- call any model other than exact `gpt-6.1-sol` high;
- exceed 60 calls;
- retry failed calls;
- repair malformed judge outputs with another call;
- adapt prompts/batches after observing results;
- use a second judge/model;
- treat judge confidence as proof;
- modify production behavior;
- promote anything;
- do UI/visualization work;
- infer owner verdict;
- activate follow-up execution.

## Validation

At minimum:
- pre-live frozen identity/leakage/provider checks;
- focused SPEC-067 tests;
- exact call-budget enforcement;
- zero-retry enforcement;
- raw-response/ledger reconciliation;
- fixture-label isolation tests;
- scoring reproducibility;
- category-metric reconciliation;
- J1/J2 pairing checks;
- protected-state hashes;
- SPEC-066 regressions;
- control-plane tests;
- full offline suite after execution;
- JSON/schema validation;
- secret safety;
- `git diff --check`.

## Completion state

On completion:
- set SPEC-067 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report provider compatibility, exact calls, usage, J1/J2 false admissions, true admissions, uncertainty, category failures, batching degradation, order sensitivity, mechanical branch, and recommended next step;
- stop at `OWNER_REVIEW`;
- do not run synthesis or follow-up experiments.

## Owner review question

> **Is the bounded semantic judge conservative enough on known difficult cases to become part of the trust boundary for a later generative synthesis experiment—and does batching preserve that conservatism?**
