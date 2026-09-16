# SPEC-053 — Claim-to-Representation Coverage Diagnosis

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Trace the trusted claim-only knowledge produced by Candidate B v2 through the existing downstream representation pipeline and determine why none of the 98 mechanically claim-only items from SPEC-052 received a dedicated claim-focus representation decision.

This is a downstream coverage diagnosis, not an extraction experiment and not a UI redesign.

No model/provider calls, source retrieval, extraction reruns, or production behavior changes are authorized.

## Owner verdict entering this packet

SPEC-052 owner verdict:

`B_V2_EXTRACTION_RECOVERED_CLAIM_TO_REPRESENTATION_GAP_NEXT`

Accepted interpretation:

- Candidate B v2 materially recovered extraction reliability: 8/9 admitted versus B v1 2/9 and historical Control A 4/9;
- known-invalid admission remained zero;
- Stage-2 proposition-construction failures fell from six in B v1 to one in B v2;
- 152/152 Stage-3 claims were exactly grounded and admitted;
- 98 were mechanically claim-only and created zero unintended topology;
- extraction decomposition has earned continuation despite higher call/token cost;
- the unresolved question is downstream: trusted non-topological knowledge is present in the KnowledgeModel, but dedicated claim-focus representation coverage was zero.

## Core question

> Does the representation compiler know how to use trusted knowledge that deliberately is not topology, and if not, exactly where is that knowledge lost, ignored, deprioritized, or collapsed into generic fallback behavior?

## Architectural principle

Keep the semantic tiers distinct:

```text
relationships / propositions
→ trusted topology / structure

claims
→ trusted source-supported meaning that may not be topology

representation compiler
→ decides how trusted knowledge should be taught
```

Do not solve missing claim representation by turning claims into relationships/propositions.

## Evidence scope

Use only committed repository evidence and code, primarily:

- SPEC-052 admitted KnowledgeModels and claim-preservation audit;
- SPEC-052 detected structures and representation decisions;
- SPEC-039 semantic-to-representation compiler behavior;
- assertion-aware representation behavior;
- representation strategy/compiler code;
- structure detection code;
- SPEC-038 learner-facing representation baseline;
- relevant fixtures/tests.

No external evidence is needed or authorized.

## Required trace

For all 98 mechanically claim-only SPEC-052 items, trace the path as far as deterministically possible:

```text
Stage-3 grounded claim
        ↓
admitted KnowledgeModel
        ↓
representation input selection
        ↓
structure / assertion awareness
        ↓
representation strategy decision
        ↓
representation plan / fallback / omission
        ↓
learner-facing artifact eligibility
```

For every claim-only item record whether it is:

- present in admitted KnowledgeModel;
- discoverable by assertion-aware logic;
- considered by representation planning;
- attached to a topology-focused representation as supporting material;
- preserved through generic prose/fallback behavior;
- eligible for a dedicated claim-focused representation;
- actually assigned a dedicated representation decision;
- omitted before learner-facing planning.

## Fixed claim-path taxonomy

Assign each claim-only item exactly one terminal path classification:

### `DEDICATED_REPRESENTATION`

The claim receives its own representation decision/plan focused on the claim meaning.

### `SUPPORTING_CONTENT`

The claim is deliberately attached to another representation as supporting explanatory material rather than receiving its own plan.

### `GENERIC_FALLBACK`

The claim survives only through generic prose/truthful fallback rather than a semantically fitting representation strategy.

### `NOT_CONSIDERED`

The claim is trusted and present but is never presented to the representation-decision mechanism as a candidate focus.

### `FILTERED_OR_DROPPED`

The claim is removed/filtered before representation planning or otherwise becomes unavailable downstream.

### `AMBIGUOUS`

Committed evidence/code cannot establish the terminal path without changing behavior or assumptions.

Do not add categories during execution.

## Required analyses

### 1. Inventory all 98 claim-only items

For each preserve:

- source ID/domain;
- claim ID/text;
- exact grounding/provenance identity;
- related entity IDs if any;
- whether related Stage-2 topology exists;
- terminal claim-path classification;
- code/artifact trace supporting classification;
- confidence `HIGH`, `MEDIUM`, or `LOW`.

### 2. Aggregate by source and semantic character

Without inventing a new ontology, characterize mechanically useful claim forms where evidence permits, such as:

- scalar/numeric comparison;
- descriptive contrast;
- quantitative fact;
- qualification/condition;
- definition/description;
- contextual fact;
- other/unclear.

This characterization is diagnostic only and must not become trusted semantic vocabulary.

Report whether certain forms systematically lack representation coverage.

### 3. Trace representation compiler gates

Document the exact downstream gates/interfaces that decide representation focus.

Answer:

- What objects can currently become a representation focus?
- Are claims first-class candidates or only attachments/fallback assertions?
- Does `StructureDetector` ignore claims by design?
- Does representation strategy require a detected structure or relationship/proposition focus?
- Where does assertion-aware representation consume claims today?
- What produces `PRESERVED_AS_CLAIM` and what learner-facing effect does that have?
- Why did SPEC-052 report zero dedicated claim-focus decisions?

Distinguish intentional architecture from accidental coverage gap.

### 4. Sample learner-value counterfactuals offline

Select a small deterministic sample from the 98 claim-only items, including at least:

- one standalone numeric/scalar comparison if present;
- one descriptive contrast if present;
- one quantitative/contextual fact if present;
- one claim closely associated with existing topology if present.

For each answer without implementation:

> If this claim were a representation focus, what existing representation strategy family (if any) could truthfully teach it without inventing topology?

Allowed diagnostic destinations:

- existing `COMPARISON`/compare-contrast family if already recognized by current representation grammar;
- existing truthful prose/fallback;
- existing worked-example family if genuinely supported by current semantics;
- existing sequence/hierarchy/mechanism/etc. only if claim semantics actually fit;
- `NO_EXISTING_FIT`.

Do not create a new representation family in this packet.

### 5. Determine gap class

Choose exactly one primary aggregate diagnosis:

#### `FOCUS_SELECTION_GAP`

Existing representation capabilities could handle meaningful claim-only content, but claims are not admitted as representation-focus candidates.

#### `REPRESENTATION_FAMILY_GAP`

Claims reach planning, but the current strategy grammar lacks fitting representation families for the dominant claim forms.

#### `LEARNER_SURFACE_BINDING_GAP`

Plans/strategies exist for claims, but they are not bound/rendered into the learner-facing explanatory surface.

#### `INTENTIONAL_SUPPORTING_CONTENT_ONLY`

Claims are intentionally and adequately preserved as supporting content; zero dedicated claim-focus plans are not demonstrated to be a defect.

#### `MIXED_GAP`

More than one materially important gap class is evidenced and no single class dominates.

#### `INSUFFICIENT_EVIDENCE`

Committed evidence cannot distinguish the above.

### 6. Recommend exactly one next experiment class

Choose one:

- `CLAIM_FOCUS_SELECTION_EXPERIMENT`
- `CLAIM_REPRESENTATION_STRATEGY_EXPERIMENT`
- `CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT`
- `NO_CHANGE_CLAIMS_AS_SUPPORTING_CONTENT`
- `MORE_DIAGNOSIS_REQUIRED`

The recommendation must identify:

- evidence supporting it;
- protected behavior;
- falsification condition;
- why competing experiment classes are not first priority.

Do not implement the recommendation.

## Important constraints

### Claims must not become topology

Do not add relationships/propositions to make claims visible.

### Structure detection remains topology-oriented

Do not modify `StructureDetector` in this packet. If its topology-only nature is relevant, diagnose it rather than changing it.

### Representation diversity principle remains protected

A claim-focused representation does not imply “everything becomes prose” or “everything becomes a diagram.” The existing principle remains:

> representation strategy follows the semantics of what the learner is trying to understand.

### Navigation remains separate

Do not modify My Map, traversal, Explore Next, history, or explanatory-pane architecture.

## Required artifact

Create:

`examples/evaluations/spec-053-claim-to-representation-coverage-diagnosis-20260916/report.json`

Include at minimum:

- SPEC-052 evidence identities/hashes;
- complete 98-item claim trace inventory;
- claim-path taxonomy counts;
- source/form aggregates;
- representation gate/interface trace;
- assertion-aware behavior analysis;
- deterministic learner-value sample analysis;
- exactly one primary gap diagnosis;
- exactly one recommended next experiment class;
- explicit zero-call/zero-change statement;
- tests/integrity validation;
- owner-review state.

A Markdown companion may be added if useful, but JSON is canonical.

## Validation

At minimum:

- verify SPEC-052 final report and claim audit identities;
- reconcile exactly 98 mechanically claim-only items;
- verify all 98 are admitted/exactly grounded as recorded by SPEC-052;
- verify every item receives exactly one fixed claim-path classification;
- verify exactly one aggregate gap diagnosis;
- verify exactly one next experiment class;
- run focused diagnostic tests if tooling is added;
- run control-plane tests;
- run full offline suite;
- validate JSON;
- run secret-safety/provenance checks;
- run `git diff --check`;
- verify zero provider/model/network calls;
- verify protected implementation/evidence unchanged.

Prefer evidence-only analysis over production code changes.

## Protected state

Do not modify:

- Candidate B v2 extraction behavior or evidence;
- Control A/B-v1 historical evidence;
- canonical semantic vocabulary/proposition model;
- grounding/provenance/validators;
- StructureDetector;
- representation strategy/compiler;
- assertion-aware representation behavior;
- renderers;
- SPEC-038 learner-facing baseline;
- navigation/UI.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external web/network evidence;
- rerun extraction;
- repair historical outputs;
- add claim-to-topology conversion;
- change structure detection;
- implement claim focus;
- add representation families;
- bind new learner-surface behavior;
- change renderers/UI/navigation;
- promote Candidate B v2 or another extractor;
- automatically implement the recommended next experiment.

## Completion state

On completion:

- set SPEC-053 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report claim-path distribution, aggregate gap diagnosis, recommended next experiment, and validation;
- stop at `OWNER_REVIEW`.

## Owner review question

> The extraction compiler now preserves trusted non-topological truth. What exactly prevents that truth from becoming a fitting learner-facing representation, and which single downstream experiment should we run next without corrupting the topology/claim distinction?
