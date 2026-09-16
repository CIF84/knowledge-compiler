# SPEC-054 — Claim Focus Selection Experiment

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Run the smallest downstream experiment that makes trusted `KnowledgeModel.claims` eligible as representation-focus candidates and observes how the **existing** representation strategy grammar handles them.

The experiment must answer whether the diagnosed SPEC-053 gap is primarily routing/focus selection, or whether claim-focused inputs expose a second gap in representation-strategy coverage.

This packet does not authorize new representation families, new renderers, learner-surface redesign, extraction changes, model/provider calls, or claim-to-topology conversion.

## Owner verdict entering this packet

SPEC-053 owner verdict:

`CLAIM_FOCUS_GAP_CONFIRMED_SELECTION_EXPERIMENT_NEXT`

Accepted evidence:

- all 98 mechanically claim-only SPEC-052 items remain exactly grounded and present in admitted KnowledgeModels;
- 98/98 terminate as `NOT_CONSIDERED`;
- focus enumeration excludes claims before strategy resolution;
- semantic compiler dispatch has no claim focus class;
- StructureDetector is topology-only by design and is not the defect;
- no claim-only item currently reaches dedicated strategy selection, supporting-content attachment, or generic fallback;
- the first blocking seam is focus selection.

## Core hypothesis

> If trusted claims are admitted as first-class representation-focus candidates without becoming topology, the existing representation strategy resolver will truthfully handle at least some claim forms; the resulting distribution will reveal whether routing alone is sufficient or whether representation-family coverage is the next bottleneck.

## Experiment boundary

Implement an **experimental claim-focus seam**, versioned and isolated from the accepted production baseline.

Do not silently change existing entity/relationship/proposition behavior.

The experiment should operate on already-admitted SPEC-052 KnowledgeModels offline.

No extraction rerun is needed or allowed.

## Focus model

Introduce the minimum representation-focus abstraction needed to identify a claim as a focus.

A claim focus must preserve at minimum:

- source/model identity;
- claim ID;
- claim text/statement;
- exact grounding/provenance;
- origin/confidence where already available;
- related entity IDs only when deterministically available from existing data;
- semantic class `CLAIM` for compiler dispatch.

Do not infer topology or create relationship/proposition endpoints.

If the existing focus abstraction can be extended safely, do so in an experimental/versioned seam. Otherwise create the smallest adapter needed for the experiment.

## Focus enumeration

Experimental enumeration must include trusted claims from an admitted KnowledgeModel in addition to existing focus classes.

Requirements:

- every enumerated claim must already be admitted and exactly grounded;
- no duplicate focus for the same claim ID;
- claims do not enter `StructureDetector`;
- claims do not alter existing detected structures;
- claims do not alter existing entity/relationship/proposition decisions;
- claim focus enumeration is deterministic.

## Strategy resolution

Pass claim focuses to the **existing representation strategy logic** with the minimum context required to obtain a truthful decision.

Do not add claim-specific strategy families in this packet.

Do not hard-code diagnostic surface-form classes from SPEC-053 into production strategy selection.

The experiment must distinguish at least:

### `EXISTING_NON_FALLBACK_STRATEGY`

An existing strategy family other than generic truthful prose/fallback is selected and the decision is semantically defensible from the claim/context.

### `TRUTHFUL_PROSE_FALLBACK`

The existing resolver safely falls back to prose/truthful explanation.

### `NO_STRATEGY`

The current resolver cannot produce a valid claim-focused decision.

### `INVALID_OR_UNSAFE_DECISION`

The resolver chooses a strategy that would require invented topology, unsupported semantics, or otherwise misrepresent the claim.

Do not add more outcome categories during execution.

## Existing strategy-family integrity

Use only strategy families already present in the repository at packet start.

Examples may include comparison, hierarchy, sequence/process, causal/mechanism, worked example, spatial, truthful prose fallback, or other existing canonical families — but do not assume a claim fits one merely from surface wording.

A standalone numeric comparison may be diagnostically compatible with an existing comparison family only if the existing strategy contract can truthfully operate on the available claim semantics without fabricating operands/topology.

## Deterministic corpus

Primary corpus: all 98 mechanically claim-only items from SPEC-052.

Run the experimental claim-focus resolver over all 98 offline.

Additionally preserve the deterministic SPEC-053 learner-value sample as named review cases where available.

No model/provider call is authorized.

## Required control

Re-run the existing representation compilation for the same admitted SPEC-052 models **without experimental claim focus enabled** and prove byte/decision equivalence to the preserved baseline where deterministic regeneration permits.

Then enable only the experimental claim-focus seam and prove:

- existing entity/relationship/proposition representation decisions remain unchanged;
- detected structures remain unchanged;
- only additional claim-focus decisions appear.

If existing baseline cannot be deterministically reproduced, record the limitation and compare canonical decision identities instead of guessing.

## Semantic safety audit

For every claim-focus decision verify:

- claim text/evidence remains unchanged;
- no relationship/proposition is created;
- no topology is inferred;
- selected strategy does not assert semantics absent from the claim/evidence/context;
- provenance remains attached;
- no claim focus mutates the KnowledgeModel.

Any unsafe claim-focused decision must be classified `INVALID_OR_UNSAFE_DECISION`; do not repair it during this packet.

## Claim character analysis

Reuse SPEC-053 diagnostic semantic-character labels only for **post-hoc analysis**, never as strategy-selection inputs unless those labels already exist as canonical production semantics (they currently do not).

Aggregate outcome distribution by the diagnostic character classes to see whether, for example, scalar comparisons naturally receive useful existing strategies while contextual facts fall back to prose.

This analysis must not create a new ontology.

## Required experiment questions

Answer:

1. Can all 98 admitted claim-only items now become deterministic representation focuses?
2. How many resolve to `EXISTING_NON_FALLBACK_STRATEGY`?
3. How many resolve to `TRUTHFUL_PROSE_FALLBACK`?
4. How many resolve to `NO_STRATEGY`?
5. How many produce `INVALID_OR_UNSAFE_DECISION`?
6. Which existing strategy families are selected and for what diagnostic claim characters?
7. Do existing entity/relationship/proposition decisions remain unchanged?
8. Do detected structures remain unchanged?
9. Does any claim focus create topology? Target: zero.
10. Does claim focus require learner-surface/rendering changes before it can be meaningfully reviewed?

## Decision framework

Choose exactly one mechanically supported experimental branch:

### `FOCUS_SELECTION_SUFFICIENT`

Claims can be selected as focuses, existing strategy logic produces useful truthful decisions for the relevant forms (including safe fallback where appropriate), no unsafe decisions occur, and no new strategy-family gap is materially demonstrated.

### `STRATEGY_COVERAGE_GAP_REVEALED`

Claim focus routing works, but a material share of claims fall to `NO_STRATEGY`, inappropriate fallback, or otherwise demonstrate missing representation-family capability.

### `CLAIM_FOCUS_UNSAFE`

Claim focus causes invalid/unsafe semantic decisions, topology leakage, or mutation of protected existing decisions.

### `LEARNER_SURFACE_REQUIRED_TO_DECIDE`

Compiler-level decisions are valid, but the evidence cannot determine usefulness without binding/rendering them into the learner-facing explanatory surface.

### `INCONCLUSIVE`

Evidence cannot distinguish the above.

Do not promote based on this branch automatically.

## Recommended next-step vocabulary

At completion recommend exactly one:

- `CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT`
- `CLAIM_REPRESENTATION_STRATEGY_EXPERIMENT`
- `CLAIM_FOCUS_SAFETY_REDESIGN`
- `CLAIM_FOCUS_PROMOTION_REVIEW`
- `MORE_DIAGNOSIS_REQUIRED`

Do not implement the recommendation.

## Required artifacts

Create:

`examples/evaluations/spec-054-claim-focus-selection-experiment-20260916/`

Include at minimum:

- `report.json`;
- experimental claim-focus contract/version identity;
- implementation hashes;
- baseline-control comparison;
- all 98 claim-focus decisions;
- outcome/strategy-family distributions;
- diagnostic-character cross-tab;
- semantic-safety audit;
- named deterministic review sample;
- exactly one experiment branch;
- exactly one recommended next step;
- zero-call/zero-extraction statement.

If useful, emit a machine-readable claim-focus decision artifact per admitted source, but do not build new learner-facing HTML/UI in this packet.

## No live authority

Provider/model calls: `0`.

External evidence retrieval: `0`.

Extraction reruns: `0`.

The experiment is deterministic/offline over committed admitted models.

## Protected state

Do not modify:

- Candidate B v2 extraction behavior/evidence;
- historical Control A/B-v1 evidence;
- KnowledgeModel semantic content;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector behavior;
- existing representation strategy-family semantics;
- existing renderer behavior;
- SPEC-038 learner-facing architecture;
- navigation/UI.

## Explicitly forbidden

Do not:

- call a model/provider;
- rerun extraction;
- convert claims into relationships/propositions;
- modify StructureDetector to consume claims;
- add claim-specific representation families;
- add source-specific routing rules;
- use SPEC-053 diagnostic labels as hidden production routing features;
- repair unsafe decisions;
- change existing representation decisions;
- implement learner-facing rendering/binding;
- redesign UI/navigation;
- promote Candidate B v2 or claim focus automatically.

## Validation

At minimum:

- reconcile exactly 98 claim-only focuses;
- verify all are admitted/exactly grounded;
- verify every focus has exactly one outcome category;
- verify no KnowledgeModel mutation;
- verify zero topology creation;
- verify detected structures unchanged;
- verify existing non-claim representation decisions unchanged;
- validate strategy decisions against current contracts;
- run focused SPEC-054 tests;
- run control-plane tests;
- run full offline suite;
- deterministic artifact regeneration;
- JSON validation;
- provenance/secret safety;
- `git diff --check`;
- verify zero provider/model/network calls.

## Completion state

On completion:

- set SPEC-054 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report outcome distribution, strategy-family distribution, safety result, experiment branch, recommended next step, and validation;
- stop at `OWNER_REVIEW`.

## Owner review question

> Once trusted claims are finally allowed to become representation focuses, does the existing representation compiler already know how to teach them safely, or does claim routing reveal the next missing representation capability?
