# SPEC-055 — Claim Representation Strategy Experiment

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Determine whether trusted non-topological claims contain enough **representation-relevant semantics** to select richer explanatory forms than universal concise prose, without converting claims into topology or changing what the Knowledge Compiler says is true.

The experiment should establish a clean boundary between:

```text
KNOWLEDGE COMPILER
What is true?
→ entities / relationships / propositions / grounded claims

REPRESENTATION COMPILER
How is this truth easiest to understand?
→ visual/structural representation + concise prose where appropriate
```

This packet is an offline representation-strategy experiment. It does not authorize learner-surface binding, new production renderers, extraction/model calls, ontology expansion, or claim-to-topology conversion.

## Owner verdict entering this packet

SPEC-054 owner interpretation:

`CLAIM_FOCUS_ROUTING_CONFIRMED_REPRESENTATION_SEMANTICS_NEXT`

Accepted evidence:

- 98/98 trusted claim-only items became deterministic claim focuses;
- 98/98 safely resolved through the existing explanation resolver;
- 98/98 selected `CONCISE_PROSE` via truthful fallback;
- 0 `NO_STRATEGY` and 0 unsafe decisions;
- existing models, topology, detected structures, and non-claim representation decisions remained identical;
- routing is therefore proven safe;
- universal prose does not establish that prose is the best explanatory form for every claim;
- prose is expected to remain part of explanation even when a richer visual/structural representation carries part of the cognitive load.

## Core hypothesis

> Some grounded claims contain enough explicit, source-supported representation semantics to justify a richer explanatory strategy than prose alone, while other claims genuinely should remain prose. The representation layer can classify that distinction without asserting new world topology.

## Critical distinction

### Knowledge semantics

Describe what the source says about the world. These remain frozen in the admitted KnowledgeModel.

### Representation semantics

Describe how an already-trusted piece of knowledge may be communicated to a learner.

Representation semantics may identify that a claim is suitable for, for example, a quantitative comparison display without asserting a new canonical `GREATER_THAN` proposition in the KnowledgeModel.

Representation semantics must never be fed back into trusted topology.

## Experimental representation-character contract

Implement a versioned, non-canonical claim representation-character layer derived only from the claim text, exact evidence, and already-admitted context.

Use the smallest useful fixed taxonomy:

### `QUANTITATIVE_COMPARISON`

The claim explicitly compares two or more quantities, magnitudes, percentages, rates, durations, counts, or measurable values in a way that can be faithfully displayed comparatively.

### `DESCRIPTIVE_CONTRAST`

The claim explicitly contrasts two or more named things/conditions along a stated dimension without requiring a canonical causal/structural relationship.

### `QUALIFICATION_OR_CONDITION`

The claim's explanatory value depends materially on an explicit condition, exception, scope qualifier, permission, requirement, possibility, or boundary.

### `DEFINITION_OR_DESCRIPTION`

The claim primarily states what something is, means, consists of descriptively, or characterizes a single focus without comparative/conditional structure.

### `QUANTITATIVE_FACT`

The claim states one or more explicit quantities/measurements but does not materially compare alternatives.

### `CONTEXTUAL_FACT`

A truthful factual/explanatory statement for which no richer representation character above is justified.

### `AMBIGUOUS`

The claim/evidence does not safely support one representation character.

Every claim must receive exactly one experimental character.

This taxonomy is **representation metadata only**. It must not become trusted semantic vocabulary or KnowledgeModel content.

## Character derivation

Prefer deterministic derivation where semantics are explicit enough.

Allowed inputs:

- exact claim statement;
- exact grounding/evidence;
- already-admitted entity labels/types when explicitly referenced or deterministically associated;
- source-local numeric literals/units present in the claim/evidence;
- existing trusted semantic context only when it does not require inference beyond the claim.

Forbidden inputs:

- external knowledge;
- model calls;
- hidden source-specific rules;
- SPEC-053 diagnostic labels as authoritative answers;
- inferred canonical relationships/propositions;
- domain identity as a routing signal.

SPEC-053 diagnostic characters may be used after the experiment for comparison/audit, not as the production input that determines the result.

If deterministic classification cannot safely distinguish a character, choose `AMBIGUOUS` or `CONTEXTUAL_FACT`; do not guess.

## Experimental strategy mapping

Map representation characters to **experimental strategy candidates**, not production promotion.

Use only representation forms already conceptually present in the project where possible. The experiment may define a representation-plan shape for claim-focused forms, but must not build production renderers or learner UI.

### `QUANTITATIVE_COMPARISON`

Candidate strategy: `COMPARISON`

Plan should preserve explicit compared labels/values/units only when directly recoverable from trusted claim/evidence. If operands/values cannot be extracted safely, fall back to `CONCISE_PROSE`.

### `DESCRIPTIVE_CONTRAST`

Candidate strategy: `COMPARISON`

Plan may represent named sides and the explicitly stated contrast dimension/content. Do not invent a matrix of unstated attributes.

### `QUALIFICATION_OR_CONDITION`

Candidate strategy: `QUALIFIED_STATEMENT`

This is an **experimental claim representation form**, not a new KnowledgeModel proposition or topology type. It may separate the main statement from explicit qualifier/condition/exception for presentation.

### `DEFINITION_OR_DESCRIPTION`

Candidate strategy: `CONCISE_PROSE` unless an already-existing non-topological representation contract truthfully applies.

### `QUANTITATIVE_FACT`

Candidate strategy: `QUANTITATIVE_CALLOUT`

This is an experimental presentation form for explicit source-backed quantities, not topology.

### `CONTEXTUAL_FACT`

Candidate strategy: `CONCISE_PROSE`.

### `AMBIGUOUS`

Candidate strategy: `CONCISE_PROSE` with explicit fallback reason.

## Important scope rule about new forms

`QUALIFIED_STATEMENT` and `QUANTITATIVE_CALLOUT` may exist only as **experimental representation-plan types** in SPEC-055 artifacts/code seams.

They must not be added to production renderer bindings, promoted representation vocabulary, or learner UI in this packet.

The point is to test whether the representation compiler can make a semantically justified distinction before investing in rendering.

## Prose composition principle

Every richer experimental plan must retain concise prose as part of the explanation payload.

The experiment should model richer representation as:

```text
visual / structured explanatory form
        +
concise source-faithful prose
```

not as visual replacement for prose.

The expected benefit is reduced text burden and improved perceptual structure, not elimination of language.

## Corpus

Run over all 98 trusted claim-only SPEC-052 items.

Preserve the same claim-focus identities from SPEC-054 where possible.

No extraction rerun or model call.

## Required controls

Prove:

- admitted KnowledgeModels unchanged;
- exact grounding unchanged;
- detected topology/structures unchanged;
- existing entity/relationship/proposition representation decisions unchanged;
- SPEC-054 claim-focus baseline can still regenerate as 98 `CONCISE_PROSE` decisions when experimental representation-character routing is disabled;
- enabling SPEC-055 changes only experimental claim-focused plans.

## Safety constraints

For every non-prose experimental plan:

- every displayed value/label/condition must trace to claim/evidence;
- no invented operand, axis, category, dimension, causal link, sequence, hierarchy, or relationship;
- no KnowledgeModel mutation;
- no topology creation;
- no representation metadata fed back into semantic compilation;
- concise prose remains source-faithful;
- provenance remains attached.

Unsafe richer representation must fail back to `CONCISE_PROSE`, with the attempted character and fallback reason recorded.

## Evaluation outcomes

For every claim record:

- experimental representation character;
- confidence/rule evidence;
- proposed strategy;
- final safe experimental strategy;
- whether richer-than-prose representation survived safety validation;
- fallback reason if not;
- provenance refs;
- representation payload summary.

Aggregate:

- character distribution;
- final strategy distribution;
- richer-than-prose count/rate;
- fallback count/rate;
- safety violations caught;
- cross-tab versus SPEC-053 diagnostic character labels (audit only);
- distribution by source/domain (descriptive only).

## Deterministic review sample

Create a compact owner-review sample that includes, where available:

- 2 quantitative comparisons;
- 2 descriptive contrasts;
- 2 qualifications/conditions;
- 2 quantitative facts;
- 2 definitions/descriptions;
- 2 contextual facts.

For each show:

1. exact grounded claim;
2. evidence quote;
3. representation character;
4. experimental representation-plan JSON/summary;
5. concise prose component;
6. safety/provenance trace.

Do not create learner-facing HTML yet.

## Experiment questions

Answer:

1. What share of claims can be safely distinguished into representation characters beyond generic contextual fact?
2. What share can safely receive a richer-than-prose experimental plan?
3. Which characters most often support richer representation?
4. Which claims correctly remain prose?
5. Do any richer plans require semantic facts not already explicit in trusted claim/evidence?
6. Does the safety fallback prevent all such cases from becoming richer plans?
7. Does representation-character routing leave semantic/topological state untouched?
8. Is the resulting plan diversity sufficient to justify learner-surface binding/rendering as the next experiment?

## Decision framework

Choose exactly one branch:

### `REPRESENTATION_SEMANTICS_SUPPORTED`

A meaningful subset of claims safely receives richer representation plans, prose remains appropriate for another subset, no semantic/topology leakage occurs, and the resulting diversity justifies learner-surface evaluation.

### `MOSTLY_PROSE_IS_JUSTIFIED`

The majority of claims cannot safely support richer forms from trusted evidence alone; universal/near-universal prose appears substantively justified.

### `REPRESENTATION_SEMANTICS_TOO_BRITTLE`

Deterministic character extraction frequently misclassifies, requires unsupported inference, or generates unsafe richer plans.

### `STRATEGY_FORMS_INSUFFICIENT`

Claim characters can be identified safely, but available/experimental plan forms cannot express them usefully without further representation-strategy design.

### `INCONCLUSIVE`

Evidence cannot distinguish the above.

## Recommended next-step vocabulary

Choose exactly one:

- `CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT`
- `CLAIM_REPRESENTATION_STRATEGY_REFINEMENT`
- `KEEP_CLAIMS_PROSE_FIRST`
- `REPRESENTATION_SEMANTICS_REDESIGN`
- `MORE_DIAGNOSIS_REQUIRED`

Do not implement it.

## Required artifacts

Create:

`examples/evaluations/spec-055-claim-representation-strategy-experiment-20260916/`

Include at minimum:

- `report.json`;
- experimental representation-character contract/version identity;
- implementation hashes;
- all 98 classifications/plans;
- strategy and character distributions;
- SPEC-054 disabled/enabled control comparison;
- semantic/topology safety audit;
- deterministic owner-review sample;
- exactly one decision branch;
- exactly one recommended next step;
- zero-call/zero-extraction statement.

## No live authority

Provider/model calls: `0`.

External retrieval: `0`.

Extraction reruns: `0`.

Learner-facing browser/UI implementation: `0`.

## Protected state

Do not modify:

- Candidate B v2 extraction/evidence;
- admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- existing production representation strategy semantics;
- existing production renderers;
- SPEC-038 learner-facing baseline;
- navigation/UI;
- historical experiment artifacts.

## Explicitly forbidden

Do not:

- call a model/provider;
- rerun extraction;
- convert representation character into KnowledgeModel semantics;
- create relationships/propositions from claims;
- modify StructureDetector;
- route using domain/source identity;
- use SPEC-053 labels as hidden answers;
- invent missing comparison operands/values/conditions;
- add production renderers;
- implement learner-surface binding;
- redesign UI/navigation;
- promote experimental strategy forms automatically.

## Validation

At minimum:

- reconcile exactly 98 claim focuses;
- verify exact grounding/provenance unchanged;
- verify one representation character per claim;
- verify one final strategy per claim;
- verify all richer-plan fields trace to trusted claim/evidence;
- verify zero KnowledgeModel/topology mutation;
- verify detected structures unchanged;
- verify non-claim decisions unchanged;
- verify SPEC-054 baseline regenerates when experimental routing disabled;
- run focused SPEC-055 tests;
- run control-plane tests;
- run full offline suite;
- deterministic artifact regeneration;
- JSON validation;
- secret/provenance safety;
- `git diff --check`;
- verify zero provider/model/network calls.

## Completion state

On completion:

- set SPEC-055 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report character/strategy distributions, richer-plan rate, safety result, decision branch, recommended next step, and validation;
- stop at `OWNER_REVIEW`.

## Owner review question

> Can the representation layer distinguish how different kinds of trusted non-topological truth want to be explained — composing visual/structured forms with concise prose where useful — without changing what the Knowledge Compiler says is true?
