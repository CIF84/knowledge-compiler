# SPEC-065 — Bounded Generative Semantic Synthesis Harness

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

SPEC-064 established a clean division-of-labor boundary.

Deterministic machinery preserved all 141 frozen semantic commitments and all 54 material implications with full backwards recovery, but failed to produce explanatory abstractions:

- R0: 1,315 words / 66 carriers
- R1: 1,275 words / 69 carriers
- R2: 1,315 words / 63 carriers
- R3: 1,576 words / 63 carriers
- supported groups: 3
- labels: 2
- explanatory abstractions: 0

Mechanical branch:

`GROUPING_REMAINS_NON_ABSTRACTIVE`

Architecture finding:

`BOUNDED_MODEL_CANDIDATE_REQUIRES_SEPARATE_AUTHORIZATION`

SPEC-065 implements and freezes the **harness and contracts** for the first bounded generative synthesis experiment. It does **not** authorize provider/model execution.

The experiment asks:

> **Can a generative model propose materially compressed semantic syntheses and higher-order explanatory abstractions while deterministic machinery remains the authority for preservation, provenance, recoverability, and admission?**

## Owner verdict entering this packet

Record SPEC-064 owner verdict as:

`DETERMINISTIC_PRESERVATION_CONFIRMED_SEMANTIC_ABSTRACTION_REQUIRES_GENERATIVE_CANDIDATE`

Canonical division of labor:

> **Generative intelligence proposes semantic synthesis and abstraction; deterministic compiler machinery validates trust boundaries and decides admission.**

This is a hypothesis to test, not permission to trust model output automatically.

## Scope

Use exactly the same three frozen sources/substrates from SPEC-064:

1. Geology — Understanding plate motions
2. Astronomy — How did our Solar System form?
3. Meteorology — What Is the Jet Stream?

No retrieval.
No extraction rerun.
No production semantic changes.
No UI/visualization work.

SPEC-065 may implement code, schemas, prompts, validators, fixtures, deterministic dry-runs, and a future live-execution manifest.

Provider/model calls under SPEC-065: **0**.

A later separately approved packet must authorize any source/semantic transmission.

## Architecture

```text
FROZEN TRUSTED SUBSTRATE
        ↓
deterministic input package
        ↓
GENERATIVE STAGE A
candidate semantic synthesis
        ↓
deterministic validation / admission
        ↓
GENERATIVE STAGE B
candidate explanatory abstraction
        ↓
deterministic validation / admission
        ↓
GENERATIVE STAGE C
candidate conceptual architecture
        ↓
deterministic validation / admission
        ↓
OWNER REVIEW
```

A downstream stage may consume only:
- frozen authoritative substrate;
- admitted outputs from prior stages;
- frozen contract/context explicitly allowed by this SPEC.

Rejected output must fail closed. No repair call is permitted by the future frozen execution contract unless a later packet explicitly changes that rule.

## Why staged calls

Do not ask one model response to solve R1/R2/R3 simultaneously.

The stages test distinct capabilities:

### Stage A — `SEMANTIC_SYNTHESIS`

Goal:
Produce fewer, stronger knowledge statements by truthfully subsuming overlapping or mutually explanatory frozen commitments.

It must not create conceptual handles merely to group items.

### Stage B — `EXPLANATORY_ABSTRACTION`

Goal:
Given frozen substrate plus admitted Stage-A synthesis, propose higher-order concepts that explain **why multiple items belong together** through a shared mechanism, rule, dependency, contrast, constraint, or causal principle.

### Stage C — `CONCEPTUAL_ARCHITECTURE`

Goal:
Organize admitted syntheses and abstractions into a minimal text/ASCII knowledge architecture preserving implications, qualifications, context, and recoverability.

No polished visualization.

## Compression objective

Compression is again an explicit experimental objective.

But no target ratio is hard-coded.

For each stage measure:
- words;
- characters;
- learner-visible carriers;
- frozen commitments covered explicitly;
- frozen commitments truthfully subsumed;
- implications explicit/structurally encoded;
- conceptual handles;
- explanatory abstractions;
- unsupported additions;
- material omissions;
- provenance/recovery coverage.

Success requires **cost reduction plus preservation**, not either alone.

## Stage A contract — Semantic synthesis

Each candidate synthesized unit must include:

- `candidate_id`;
- concise learner-facing statement;
- exact frozen semantic IDs covered;
- exact material implication IDs covered/encoded;
- qualifications/scope/epistemic constraints inherited;
- explanation of why these items can be synthesized;
- provenance/evidence references;
- no-new-meaning declaration.

A unit may be admitted only if deterministic validation can establish that every covered item is:
- `EXPLICIT`, or
- truthfully `SUBSUMED`, or
- `STRUCTURALLY_ENCODED`,
with exact backwards trace.

The harness must reject:
- unsupported facts;
- lost qualifiers;
- strengthened certainty/causality;
- ambiguous entity substitution;
- detached quantities/units;
- claims of coverage not supported by the candidate text/structure;
- irreversible detail loss.

## Stage B contract — Explanatory abstraction

Each candidate abstraction must include:

- `abstraction_id`;
- concise handle;
- grounded definition;
- member synthesized units and/or frozen semantic IDs;
- abstraction type from a small domain-neutral registry;
- explicit statement of the common explanatory principle;
- exact evidence/support;
- material implications carried;
- why the abstraction has explanatory power beyond a heading/container;
- backwards recovery map.

Allowed experimental abstraction types:

- `SHARED_MECHANISM`
- `GENERAL_RULE`
- `COMMON_DEPENDENCY`
- `CAUSAL_PRINCIPLE`
- `CONTRASTING_CASES`
- `CONSTRAINT_OR_BOUNDARY`
- `PROCESS_PATTERN`
- `UNRESOLVED`

Do not add domain-specific types.

Deterministic validation must classify each candidate as:

- `EXPLANATORY_ABSTRACTION`
- `SUPPORTED_GROUPING_ONLY`
- `LABEL_ONLY`
- `UNSUPPORTED`
- `UNRESOLVED`

Only `EXPLANATORY_ABSTRACTION` is admitted as an abstraction.

## Stage C contract — Conceptual architecture

Input:
- frozen authoritative substrate;
- admitted Stage-A units;
- admitted Stage-B abstractions.

Output:
- minimal text/ASCII architecture;
- explicit hierarchy/branching/process/causal relations only when supported;
- concise prose for irreducible nuance;
- exact mapping from every displayed handle/unit/relation to admitted inputs;
- hidden/recoverable detail manifest.

The model must not introduce a new abstraction in Stage C. Any novel handle/relation absent from admitted Stage B or frozen semantics must be rejected.

## Deterministic validation boundary

The validator is authoritative.

Where strict deterministic entailment cannot be established, classify conservatively and fail closed.

Do not weaken validators merely to admit model output.

The harness must distinguish:

- candidate-generation failure;
- schema/format failure;
- preservation failure;
- grounding/provenance failure;
- abstraction-quality failure;
- compression failure;
- architecture failure.

## Important feasibility constraint

SPEC-065 must explicitly report which semantic checks are genuinely deterministic and which cannot be validated without another semantic judge.

If a proposed validation rule secretly requires model-level interpretation, record it as:

`SEMANTIC_VALIDATION_GAP`

Do not disguise heuristic matching as proof of entailment.

This is a key experiment question: the architecture may require generative synthesis **and** a bounded semantic-judge layer later. SPEC-065 must expose that possibility rather than assume deterministic validation can prove everything.

## Frozen prompt contracts

Create exact versioned prompts for Stages A/B/C.

Prompt requirements:
- use only provided frozen/admitted material;
- no external knowledge;
- preserve uncertainty/scope/causal status;
- prefer omission from candidate output over unsupported inference;
- produce structured machine-readable output matching frozen schema;
- no citations fabricated beyond supplied provenance IDs;
- no learner personalization;
- no visual styling;
- no meta commentary.

Freeze prompt text/hashes in the report.

## Future model contract

SPEC-065 must define but not execute a future live contract.

Default proposed model:
`gpt-6.1-sol`

Reasoning effort:
`high`

If repository/provider integration does not support this exact model/effort contract, fail the harness review rather than silently substituting another model.

Future execution settings:
- `store=False`;
- temperature/other sampling parameters only if supported and explicitly frozen;
- zero retries;
- zero hidden repair calls;
- zero semantic follow-ups;
- fixed call order;
- exact usage ledger;
- raw responses preserved;
- secrets excluded from artifacts.

No calls are authorized now.

## Proposed future call budget

Freeze a **maximum of 9 model calls**:

- 3 sources × Stage A = 3
- only sources admitted through A proceed to Stage B, max 3
- only sources admitted through B proceed to Stage C, max 3

Total maximum: 9.

No retry budget.

The later live packet may authorize fewer calls if fail-closed stages stop progression.

## Offline fixtures

Build deterministic fixtures for:
- valid synthesis with truthful subsumption;
- invalid synthesis losing a qualifier;
- invalid causal strengthening;
- valid abstraction explaining shared mechanism;
- grouping-only false abstraction;
- label-only false abstraction;
- unsupported abstraction;
- valid architecture using only admitted handles;
- invalid architecture inventing a new handle;
- recoverability/provenance failures.

Fixtures must exercise both admission and rejection.

## Evaluation metrics for later live packet

Per source/stage:

### Preservation
- semantic commitments: explicit/subsumed/structurally encoded/lost;
- material implications preserved/lost;
- qualification/epistemic preservation;
- provenance coverage;
- backwards recovery.

### Compression
- words;
- characters;
- carriers;
- semantic units before/after;
- compression ratios.

### Abstraction
- candidate abstractions;
- admitted explanatory abstractions;
- grouping-only;
- label-only;
- unsupported/unresolved;
- average members per admitted abstraction;
- top-level conceptual handles.

### Trust
- unsupported additions;
- semantic-validation gaps;
- fail-closed count;
- validator disagreement/uncertainty where mechanically detectable.

No cognitive/pedagogical claim from machine metrics.

## Human review plan for later execution

If future live outputs are admitted, owner review must remain text/ASCII-first.

For each source show:
- R0 source;
- admitted R1 model synthesis;
- admitted R2 abstraction layer;
- admitted R3 architecture;
- compression ratios;
- preservation/recovery audit.

No polished UI.

Owner questions:
1. Is reading cost genuinely lower?
2. Did synthesis reduce semantic units rather than merely shorten sentences?
3. Do abstractions explain why members belong together?
4. Does architecture expose the core mechanism/schema?
5. Is important nuance still perceptible?
6. Can omitted detail be recovered?
7. Is the result more useful than the source for first learning/review?

## Mechanical result for SPEC-065

Choose exactly one:

- `BOUNDED_GENERATIVE_HARNESS_READY_FOR_OWNER_REVIEW`
- `VALIDATION_BOUNDARY_INSUFFICIENT`
- `HARNESS_CONTRACT_TOO_PERMISSIVE`
- `HARNESS_CONTRACT_TOO_RESTRICTIVE`
- `INCONCLUSIVE`

This result concerns harness readiness only.

## Recommended next-step vocabulary

Choose exactly one:

- `FREEZE_LIVE_GENERATIVE_EXECUTION_PACKET`
- `SEMANTIC_VALIDATION_BOUNDARY_EXPERIMENT`
- `HARNESS_REFINEMENT_REQUIRED`
- `MORE_DIAGNOSIS_REQUIRED`

No live execution is authorized.

## Required outputs

Create:

`examples/evaluations/spec-065-bounded-generative-semantic-synthesis-harness-20261007/`

Include at minimum:
- `report.json`;
- frozen three-source input manifest;
- Stage A/B/C schemas;
- prompt texts and hashes;
- implementation hashes;
- deterministic validator capability matrix;
- `SEMANTIC_VALIDATION_GAP` inventory;
- fixture corpus/results;
- proposed future live-execution manifest;
- max-nine-call ledger template;
- protected-state hash manifest;
- zero-call statement;
- owner verdict `PENDING`.

## Project vision update

Update `docs/PROJECT-VISION.md` minimally:

- deterministic machinery is the trust/admission layer;
- generative intelligence may serve as bounded synthesis/abstraction candidate generation where deterministic transformation fails;
- model output is never canonical merely because it was generated;
- representation/UI work remains downstream and paused until synthesis/abstraction is validated.

Do not claim model-assisted synthesis is validated yet.

## Protected state

Do not modify:
- SPEC-064 evidence;
- SPEC-063 and earlier experiment evidence;
- frozen three-source substrate;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators except isolated experimental validator adapters explicitly required by this harness;
- production StructureDetector;
- production representation strategies/renderers;
- accepted SPEC-038 baseline;
- navigation/My Map/Explore Next.

## Explicitly forbidden

Do not:
- call any model/provider;
- retrieve external sources;
- rerun extraction;
- generate live R1/R2/R3 candidates;
- weaken production validators;
- modify frozen semantics/schema/evidence;
- route on source/domain/case identity;
- hard-code expected geology/astronomy/meteorology abstractions;
- add polished UI/visualization;
- personalize output;
- promote any experimental behavior;
- implement follow-up live execution;
- infer owner verdict.

## Validation

At minimum:
- focused SPEC-065 tests;
- all offline fixture admission/rejection tests;
- prompt/schema deterministic identity;
- protected SPEC-064 and earlier hashes;
- control-plane tests;
- full offline suite;
- deterministic regeneration;
- JSON/schema validation;
- secret safety;
- `git diff --check`;
- explicit assertion of zero provider/model/network calls.

## Completion state

On completion:
- set SPEC-065 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report validator capability/gaps, fixture results, prompt/model/call-budget identities, mechanical branch, recommended next step, and validation;
- stop at `OWNER_REVIEW`;
- do not execute the future live manifest.

## Owner review question

> **Is this harness strict enough to let a generative model attempt the semantic synthesis deterministic code could not perform, while keeping trust, provenance, recoverability, and admission outside the model?**
