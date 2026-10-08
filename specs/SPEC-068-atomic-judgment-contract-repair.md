# SPEC-068 — Atomic Judgment Contract Repair

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

SPEC-067 correctly stopped before any provider call because the proposed live semantic-judge contract conflated **fixtures** with **independently validated atomic commitments**.

The frozen 92-fixture SPEC-066 corpus contains:

- 76 opaque carriers marked `UNRESOLVED`;
- 16 explicit AND fixtures with two declared components each;
- 108 declared carriers in total;
- but no independently validated exhaustive natural-language atomization.

The selected 48-fixture SPEC-067 subset contained 49 declared carriers, including a mixed-validity two-component AND case.

SPEC-068 resolves only this execution-contract boundary.

It does **not** run a semantic judge.

Primary question:

> **Can we establish a conservative, explicit fixture → atomic-commitment → fixture-aggregation contract that is safe enough to support a later live semantic-judge evaluation without pretending unresolved natural language is already atomized?**

## Owner verdict entering this packet

Record SPEC-067 owner verdict:

`LIVE_JUDGE_NOT_TESTED_ATOMIC_EXECUTION_CONTRACT_REQUIRES_REPAIR`

Accepted findings:

- zero provider/model calls occurred;
- semantic-judge quality remains completely unmeasured;
- J1's trust unit must remain an independently validated atomic commitment, not an arbitrary fixture;
- one valid conjunct must never license another unsupported conjunct;
- silently treating a whole fixture as one atom would weaken the trust contract;
- silently expanding 48 fixture slots to 49+ atomic calls would violate the frozen execution manifest;
- fixture identity and atomic judgment identity are distinct layers.

Canonical rule:

> **Fixture is the evaluation container; atomic commitment is the semantic judgment unit.**

## Scope

Use the exact frozen SPEC-066 92-fixture corpus and labels unchanged.

No model/provider calls.
No source retrieval.
No extraction rerun.
No fixture-label changes.
No production changes.

This packet may:
- inspect frozen fixture structure;
- define an atomic-commitment representation;
- admit atomization only where it can be established without unsupported semantic interpretation;
- freeze fixture→atom mappings;
- define fixture aggregation;
- build offline negative/positive controls;
- design a later live manifest for only atomically admissible fixtures.

## Do not assume all 92 fixtures are atomizable

This is critical.

The 76 opaque `UNRESOLVED` carriers must not be relabeled as atomic merely because they contain one string.

For every fixture classify atomization as exactly one:

- `EXPLICIT_ATOMIC`
- `EXPLICIT_COMPOSITE_DECOMPOSABLE`
- `OPAQUE_ATOMIZATION_UNRESOLVED`
- `MALFORMED`

Only the first two may enter a future precision-first live judge experiment under the current trust model.

If this leaves too few or too unrepresentative cases, the packet must say so.

## Explicit composite decomposition

For `EXPLICIT_COMPOSITE_DECOMPOSABLE` fixtures:

- every declared component must become its own atomic commitment;
- component text/semantics must be frozen from already-declared fixture structure;
- no component may be dropped;
- no new component may be inferred;
- conjunction/disjunction/negation structure must be preserved;
- exact fixture membership must be retained.

Do not use heuristic sentence splitting as proof of atomization.

## Opaque carriers

For `OPAQUE_ATOMIZATION_UNRESOLVED`:

- preserve the fixture;
- exclude it from future atomic live execution;
- record why deterministic exhaustive atomization cannot be established.

Do not ask a model to atomize under SPEC-068.

A later separately authorized experiment may test bounded atomization if needed.

## Atomic commitment schema

Freeze an explicit schema including at minimum:

- `atom_id`;
- `fixture_id`;
- `component_ordinal`;
- exact candidate text or frozen structured assertion;
- composition role;
- evidence packet identity;
- expected semantic verdict inherited/derived only where frozen fixture truth permits;
- required preservation flags;
- provenance;
- atomization status;
- atomization proof type.

No atom may exist without a fixture parent.

## Expected-label derivation

Do not invent atom-level truth labels.

For fixtures with already-declared per-component truth, freeze those exact component labels.

If a fixture-level label does not uniquely determine each component's atom-level label, classify atom truth as unresolved and exclude it from scored precision-first execution.

This prevents deriving:
- “fixture rejected” → “every atom contradicted”;
- “fixture admitted” → “every hidden component entailed”;
without evidence.

## Fixture aggregation contract

For a fixture composed entirely of independently judged required atoms:

### Conjunction / all-required fixture

- fixture `ENTAILED` only if **all** required atoms are `ENTAILED` and preservation flags pass;
- any `CONTRADICTED` → fixture reject;
- any `UNCERTAIN` → fixture reject/fail closed;
- malformed atom result → fixture reject/fail closed.

### Other composition

If frozen fixture semantics require another aggregation operator, it must already be explicit and deterministically supported.

Otherwise aggregation status is unresolved and fixture is excluded.

No majority vote.

## Negative control requirement

The repaired corpus must retain at least one mixed-validity composite control if the frozen data supports one.

For example, the SPEC-067 case-023 pattern must demonstrate:

```text
atom A → ENTAILED
atom B → not admissible
fixture A AND B → not admissible
```

The implementation must prove that atom A cannot license the parent fixture.

## Full-corpus audit

Audit all 92 fixtures before selecting any future subset.

Report:

- fixtures by atomization status;
- declared carriers;
- independently admissible atoms;
- fixtures with fully known atom truth;
- fixtures with unresolved atom truth;
- category/domain coverage remaining after atomic admission;
- categories/domains lost by conservative exclusion.

## Future live-subset design

Only after the full audit, design a proposed future semantic-judge subset from atomically admissible fixtures.

Do not force 48 fixtures.

Selection priorities:

1. preserve difficult near-miss negatives;
2. maximize semantic-category coverage;
3. maximize domain diversity;
4. retain faithful positives needed to measure usefulness;
5. retain mixed-validity composite controls;
6. prefer fewer trustworthy cases over larger ambiguous coverage.

The report must state whether the remaining subset is sufficient to evaluate the judge.

## Future J1 contract

One independently validated atom per call.

Call count = exact number of selected atoms.

No fixed 48-call assumption.

Each call returns an atom verdict.

Fixture verdict is reconstructed by the frozen aggregation contract.

## Future J2 contract

Batch **atoms**, not fixtures.

Use a fixed batch size proposed by this packet (prefer 4 if compatible).

Requirements:

- independent per-atom verdict objects;
- preserve fixture membership;
- avoid placing sibling atoms from the same composite fixture in the same batch where possible;
- fixture aggregation occurs only after individual atom verdicts;
- no batch-level semantic verdict.

Freeze the proposed batching algorithm and exact future call count.

## Budget

SPEC-068 makes zero live calls.

For the proposed future executable packet calculate:

- selected fixtures;
- selected atoms;
- J1 calls;
- J2 batch size;
- J2 calls;
- maximum total live calls;
- zero-retry policy;
- expected category/domain coverage.

Do not inherit SPEC-067's 60-call budget if atom counts differ.

## Atomization quality audit

For every admitted atom prove:

- exact fixture parent;
- exact component origin;
- no lost conjunct;
- no invented split;
- no merged components;
- no semantic rewriting during atomization;
- evidence binding;
- label derivation validity.

Any failure excludes the atom/fixture.

## Decision branches

Choose exactly one:

### `ATOMIC_EXECUTION_CONTRACT_READY`

A representative enough atomically admissible subset exists, atom/fixture truth is frozen, aggregation is safe, and future J1/J2 manifests can be executed without unresolved atomization.

### `ATOMIC_SUBSET_TOO_NARROW`

Safe atomization exists but leaves insufficient category/domain/positive-negative coverage for meaningful judge evaluation.

### `ATOMIZATION_REQUIRES_SEMANTIC_JUDGMENT`

The frozen corpus cannot provide a useful live subset without semantically decomposing opaque natural language.

### `FIXTURE_TRUTH_INSUFFICIENT_FOR_ATOM_LABELS`

Components can be identified but atom-level expected truth cannot be derived safely.

### `INCONCLUSIVE`

Mixed evidence.

## Recommended next-step vocabulary

Choose exactly one:

- `REAUTHORIZE_SEMANTIC_JUDGE_LIVE_EVALUATION`
- `BOUNDED_ATOMIZATION_EXPERIMENT`
- `FIXTURE_REDESIGN_REQUIRED`
- `MORE_DIAGNOSIS_REQUIRED`

No live execution is authorized.

## Required outputs

Create:

`examples/evaluations/spec-068-atomic-judgment-contract-repair-20261008/`

Include at minimum:

- `report.json`;
- frozen SPEC-066 corpus/label identity manifest;
- full 92-fixture atomization audit;
- atomic commitment schema;
- fixture→atom mapping;
- atom-level truth derivation audit;
- fixture aggregation contract;
- mixed-validity composite negative-control evidence;
- excluded opaque-fixture inventory;
- category/domain coverage analysis;
- proposed future subset;
- proposed J1 atom manifest;
- proposed J2 atom-batch manifest;
- future call-budget calculation;
- deterministic regeneration evidence;
- protected-state hashes;
- zero-call statement;
- owner verdict `PENDING`.

## Project vision update

No project-vision change is required unless implementation reveals a durable architectural principle not already captured.

Do not expand product ambition.

## Protected state

Do not modify:

- SPEC-067 evidence/preflight findings;
- SPEC-066 fixtures/labels/evidence;
- SPEC-065 harness;
- SPEC-064 and earlier evidence;
- frozen source/semantic substrate;
- production validators;
- production KnowledgeModel semantics;
- production representation/UI/navigation.

Prefer isolated contract/audit code and artifacts.

## Explicitly forbidden

Do not:

- call any model/provider;
- retrieve sources;
- alter fixture text or labels;
- treat opaque carrier text as atomic by assertion;
- use heuristic punctuation/sentence splitting as atomization proof;
- infer atom-level expected labels from fixture labels when logically underdetermined;
- weaken the one-atom J1 trust contract;
- execute semantic judging;
- execute SPEC-065 synthesis;
- modify production behavior;
- promote anything;
- do UI/visualization work;
- assign owner verdict;
- activate follow-up live execution.

## Validation

At minimum:

- focused SPEC-068 tests;
- exact SPEC-066/SPEC-067 frozen identity checks;
- full 92-fixture reconciliation;
- carrier/atom count reconciliation;
- no-lost-conjunct tests;
- mixed-validity composite aggregation tests;
- atom-label derivation tests;
- no-heuristic-atomization tests;
- proposed J1/J2 manifest reconciliation;
- call-budget reconciliation;
- protected hashes;
- control-plane tests;
- full offline suite;
- deterministic regeneration;
- JSON/schema validation;
- secret safety;
- `git diff --check`;
- explicit zero provider/model/network calls.

## Completion state

On completion:

- set SPEC-068 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report atomization distribution, admissible fixtures/atoms, category/domain coverage, aggregation controls, proposed future J1/J2 budgets, mechanical branch and recommended next step;
- stop at `OWNER_REVIEW`;
- do not execute the future live manifests.

## Owner review question

> **Have we established a trustworthy distinction between evaluation fixtures and independently judgeable semantic atoms, without weakening the trust boundary simply to make the live experiment executable?**
