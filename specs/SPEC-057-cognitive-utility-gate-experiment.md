# SPEC-057 — Cognitive Utility Gate Experiment

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Test whether the representation compiler can distinguish **representable structure** from **usefully visualizable structure** before choosing a richer representation.

SPEC-055 proved that trusted non-topological claims can contain representation semantics. SPEC-056 then showed that semantic representability alone is insufficient: some structurally valid visualizations add decoding burden without reducing the learner's cognitive work.

This packet introduces an experimental cognitive-utility gate between representation-semantic eligibility and representation selection.

## Owner verdict entering this packet

SPEC-056 owner verdict:

`VISUALIZATION_REQUIRES_COGNITIVE_UTILITY_GATE`

Accepted owner findings:

- prose is a first-class positive representation choice, not a failure state;
- `QUALIFIED_STATEMENT` examples in SPEC-056 were mostly visual overkill and often decomposed grammar rather than explaining knowledge;
- `CONCISE_PROSE` controls generally demonstrated appropriate restraint;
- `QUANTITATIVE_CALLOUT` may be useful in some cases, but the reviewed treatment often added prominence rather than explanatory compression;
- `COMPARISON` remains a strong candidate for useful visualization because it can externalize magnitude/difference/contrast;
- some relationship/topology forms can benefit strongly from diagrams when the visual externalizes relational structure;
- the governing principle is:

> **A representation must earn its complexity by reducing cognitive work.**

## Core model

Representation selection should now be treated as two gates:

```text
TRUSTED KNOWLEDGE
       ↓
GATE 1 — REPRESENTABILITY
Does trusted knowledge contain explicit representation-relevant structure?
       ├─ no → PROSE
       ↓ yes
GATE 2 — COGNITIVE UTILITY
Would externalizing that structure plausibly reduce cognitive work?
       ├─ no → PROSE
       ↓ yes
REPRESENTATION STRATEGY
       ↓
visual / structured form + concise prose
```

SPEC-055 tested Gate 1. SPEC-057 tests Gate 2 offline.

## Cognitive-utility principle

Use this conceptual criterion:

```text
representation utility
≈ cognitive work removed
− cognitive work introduced by decoding the representation
```

Do not attempt to calculate a psychometric numeric score. The experiment should derive auditable categorical evidence from the trusted representation payload.

## Experimental utility contract

For each candidate richer representation, classify exactly one utility outcome:

### `STRONG_EXTERNALIZATION_VALUE`

The representation externalizes meaningful work that prose would otherwise require the learner to construct or compare mentally.

### `POSSIBLE_EXTERNALIZATION_VALUE`

There is plausible cognitive benefit, but the frozen payload does not make the benefit strong enough to justify automatic richer representation.

### `LOW_EXTERNALIZATION_VALUE`

The representation mainly reformats, emphasizes, or decomposes language without materially externalizing structure.

### `UNSAFE_OR_UNSUPPORTED`

The utility case would require inferred or invented semantics not present in trusted evidence.

These are experimental representation-selection metadata only. They must not become KnowledgeModel semantics.

## Utility evidence dimensions

Derive utility only from explicit trusted representation payload and already-frozen representation semantics.

Record booleans/evidence for these dimensions:

### `RELATIONAL_LOAD`

Would prose require the learner to hold multiple entities/relationships and their configuration in working memory?

Strong examples: multi-node causal/dependency/feedback/hierarchy structures.

A single trivial subject-predicate statement is not high relational load.

### `PERCEPTUAL_COMPARISON_LOAD`

Would the learner otherwise need to compare magnitude, proportion, distribution, ordered alternatives, or multiple explicit dimensions mentally?

Explicit numeric or structured comparison can qualify.

A lone number does not automatically qualify.

### `TEMPORAL_OR_PROCESS_LOAD`

Does understanding depend on sequence/order/stages/transitions that can be externalized spatially?

### `SPATIAL_OR_MECHANISTIC_LOAD`

Does meaning depend on spatial arrangement, geometry, mechanism, reciprocal physical interaction, or another inherently structural configuration?

### `GRAMMAR_ONLY_DECOMPOSITION`

Would the proposed visual mainly pull a qualifier, condition, adjective, clause, or phrase out of an already-simple sentence without adding explanatory structure?

This is negative utility evidence.

### `EMPHASIS_ONLY`

Would the representation merely make a word/number visually larger or more prominent without revealing a relationship/pattern?

This is negative utility evidence.

### `DECODING_OVERHEAD`

Does the proposed representation introduce labels, arrows, containers, axes, legends, or visual grammar whose interpretation is comparable to or harder than reading the prose?

This is negative utility evidence.

## Deterministic utility rules

Implement the smallest conservative rule set that can be justified from frozen evidence.

The gate should favor prose under uncertainty.

Minimum policy:

1. Strong positive externalization evidence with no material unsupported semantics may yield `STRONG_EXTERNALIZATION_VALUE`.
2. Mixed positive/negative evidence yields `POSSIBLE_EXTERNALIZATION_VALUE` unless a deterministic stronger rule is justified.
3. `GRAMMAR_ONLY_DECOMPOSITION` or `EMPHASIS_ONLY` without another strong positive dimension yields `LOW_EXTERNALIZATION_VALUE`.
4. A single quantity with no comparison/pattern is not strong merely because it is quantitative.
5. A simple qualification/condition is not strong merely because it can be separated typographically.
6. Explicit comparisons with faithfully extractable operands/dimensions/values should be tested as likely strong candidates.
7. Existing trusted multi-node structural representations may be included as positive controls where topology clearly externalizes relational/process/mechanistic load.
8. If useful visualization would require invented structure, classify `UNSAFE_OR_UNSUPPORTED`.

Do not use domain/source identity as a utility signal.

## Corpus

Use two frozen evidence groups.

### Group A — SPEC-055 claim candidates

Evaluate all 53 richer-than-prose SPEC-055 candidates:

- 7 `COMPARISON`;
- 33 `QUALIFIED_STATEMENT`;
- 13 `QUANTITATIVE_CALLOUT`.

The 45 `CONCISE_PROSE` cases remain negative controls and should be audited to ensure the gate does not manufacture utility.

### Group B — existing structural positive controls

Select a deterministic bounded sample of existing accepted non-claim representation cases from SPEC-038/039-era evidence where diagrams previously carried real structure.

Include at minimum, if frozen evidence remains available:

- one multi-node causal/system case (for example economics);
- one dependency/composition case (for example printing/software architecture);
- one reciprocal/mechanistic case (for example electric/magnetic fields);
- one simple focused relationship as a lower-complexity structural control.

Do not change or regenerate their semantics. The purpose is calibration: a utility gate that rejects every visual representation is also wrong.

## Strategy decision experiment

For each SPEC-055 claim candidate, record:

- prior SPEC-055 representation character;
- prior proposed richer strategy;
- utility evidence dimensions;
- utility outcome;
- gated final experimental strategy.

Gating policy:

- `STRONG_EXTERNALIZATION_VALUE` → retain richer experimental strategy;
- `POSSIBLE_EXTERNALIZATION_VALUE` → `CONCISE_PROSE` for automatic selection, but preserve candidate metadata for future/manual study;
- `LOW_EXTERNALIZATION_VALUE` → `CONCISE_PROSE`;
- `UNSAFE_OR_UNSUPPORTED` → `CONCISE_PROSE` and record safety reason.

Do not modify SPEC-055 artifacts; create SPEC-057 derived decisions.

## Key expected falsification opportunities

The experiment must be able to show all of the following if evidence supports them:

- many `QUALIFIED_STATEMENT` candidates collapse back to prose;
- lone-number `QUANTITATIVE_CALLOUT` candidates collapse back to prose;
- some explicit comparisons survive;
- existing multi-node structural diagrams survive as positive controls;
- some relationship representations may or may not survive depending on actual cognitive load.

Do not hard-code these outcomes merely to match owner feedback.

## SPEC-056 owner-review anchor cases

Use the exact reviewed SPEC-056 sample as an audit subset.

The offline gate should report its classification for each of the 12 cases so the owner can compare machine selection with the observed human verdict.

Do not treat the owner's comments as hidden labels in the algorithm. They are post-hoc validation evidence only.

## Required outputs

Create:

`examples/evaluations/spec-057-cognitive-utility-gate-experiment-20260917/`

Include at minimum:

- `report.json`;
- versioned cognitive-utility contract identity/hash;
- all 98 claim-control decisions, including 53 richer candidates and 45 prose controls;
- positive-control structural sample and decisions;
- utility-dimension evidence per evaluated candidate;
- before/after strategy distribution (`SPEC-055` vs utility-gated);
- SPEC-056 12-case audit table;
- safety/topology audit;
- deterministic regeneration evidence;
- exactly one experiment branch;
- exactly one recommended next step.

## Evaluation questions

Answer:

1. How many of the 53 richer SPEC-055 claim plans still earn richer representation after the cognitive-utility gate?
2. Which representation characters survive most often?
3. Does the gate correctly suppress grammar-only qualified-statement visualization?
4. Does it suppress emphasis-only quantitative callouts?
5. Do explicit comparisons survive when the visual can externalize comparison work?
6. Do accepted multi-node structural positive controls survive?
7. Does the gate leave prose controls as prose?
8. Does the gate require any new semantic/topological inference?
9. How well do gate outcomes align descriptively with the SPEC-056 owner-reviewed sample?
10. Is the resulting selection policy constrained enough to justify a second learner-surface A/B experiment?

## Decision branches

Choose exactly one:

### `COGNITIVE_UTILITY_GATE_SUPPORTED`

The gate conservatively suppresses low-value visuals, preserves meaningful positive controls, leaves prose controls alone, and retains a bounded subset of richer claim representations with auditable externalization value.

### `GATE_TOO_PERMISSIVE`

Low-value/decorative representations continue to survive materially.

### `GATE_TOO_CONSERVATIVE`

Representations with clear externalization value, including structural positive controls, are suppressed materially.

### `UTILITY_NOT_DETERMINABLE_FROM_FROZEN_EVIDENCE`

The trusted representation payload is insufficient to distinguish cognitive utility without human/model judgment.

### `INCONCLUSIVE`

Evidence is mixed or insufficient.

## Recommended next-step vocabulary

Choose exactly one:

- `UTILITY_GATED_LEARNER_SURFACE_AB_EXPERIMENT`
- `COGNITIVE_UTILITY_RULE_REFINEMENT`
- `REPRESENTATION_UTILITY_METADATA_REDESIGN`
- `KEEP_PROSE_DEFAULT_AND_STOP_CLAIM_VISUALIZATION`
- `MORE_DIAGNOSIS_REQUIRED`

Do not implement the next step.

## Protected state

Do not modify:

- Candidate B v2 extraction/evidence;
- admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- SPEC-055 classifications/plans;
- SPEC-056 learner-review artifact/evidence;
- production representation strategies/renderers;
- accepted SPEC-038 learner-facing baseline;
- navigation/My Map/Explore Next;
- historical experiment artifacts.

## Explicitly forbidden

Do not:

- call a model/provider;
- use external retrieval;
- rerun extraction;
- infer new KnowledgeModel semantics;
- create relationships/propositions/topology from claims;
- use source/domain identity as a utility signal;
- encode SPEC-056 owner comments as case-specific routing rules;
- add or polish learner-facing renderers;
- redesign UI;
- promote strategies/renderers;
- invent numeric utility scores without evidence;
- automatically claim pedagogical effectiveness.

## Validation

At minimum:

- reconcile all 98 SPEC-055 claim cases;
- reconcile all 53 richer candidates;
- verify 45 prose controls remain prose unless an explicit contract violation is surfaced (which must fail the experiment, not silently reroute them);
- verify utility evidence is traceable to frozen representation payload;
- verify structural positive controls are deterministic and frozen;
- verify zero KnowledgeModel/topology mutation;
- verify SPEC-055/056 artifacts unchanged;
- focused SPEC-057 tests;
- relevant SPEC-038/055/056 regressions;
- control-plane tests;
- full offline suite;
- deterministic regeneration;
- JSON validation;
- provenance/secret safety;
- `git diff --check`;
- zero provider/model/network calls.

## Completion state

On completion:

- set SPEC-057 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report before/after distributions, positive-control results, SPEC-056 audit alignment, decision branch, recommended next step, and validation;
- stop at `OWNER_REVIEW`;
- do not implement learner-surface changes.

## Owner review question

> Can we conservatively predict when a representation will perform useful cognitive work for the learner — rather than merely visualizing structure because that structure happens to be representable?
