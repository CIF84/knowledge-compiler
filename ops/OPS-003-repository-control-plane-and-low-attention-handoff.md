# OPS-003 — Repository Control Plane and Low-Attention Handoff

Status: `APPROVED_FOR_IMPLEMENTATION`

## Primary uncertainty

Can Knowledge Compiler reduce owner attention and ChatGPT ↔ Codex relay overhead by making repository state, execution authority, and handoff expectations explicit, while preserving the existing evidence-driven experimental workflow and all accepted baselines?

## Objective

Introduce a lightweight repository control plane so that, after an owner/ChatGPT decision authorizes a work packet, Codex can execute the mechanical downstream lifecycle autonomously and stop only at genuine decision boundaries.

The target normal interaction after this OPS is:

```text
owner / ChatGPT approves work packet
        ↓
repository records approval
        ↓
owner tells Codex:
"Execute the current approved work packet."
        ↓
Codex reads AGENTS.md → STATUS.md → active contract
        ↓
Codex implements, validates, commits, pushes, reports
        ↓
owner / ChatGPT intervenes only if a real decision boundary is reached
```

This is an operational experiment. It changes no product semantics, algorithms, learner behavior, UI, styling, representation, or accepted baseline.

## Rationale

The current workflow already has strong separation of roles, repository-backed memory, bounded SPEC/OPS contracts, independent review, deterministic validation, and preserved baselines. The remaining friction is coordination:

- the current active work packet is not represented by one authoritative repository pointer;
- authorization is often inferred from conversational prose;
- Codex can ask for permission for mechanical actions that are already downstream of an approved decision;
- implementation handoffs can repeat machine evidence that already exists in durable artifacts;
- owner attention is therefore consumed by Git plumbing and relay rather than product judgment.

Opportunity Radar demonstrated useful patterns worth adapting rather than copying wholesale: an authoritative current-status pointer, explicit authority boundaries, and separation between experiment result and promotion. Knowledge Compiler already has SPECs, OPS records, DEBRIEFs, reviews, evaluation artifacts, and baselines, so this increment must not introduce duplicate registries or governance bureaucracy.

## Prerequisites

Codex must apply root `AGENTS.md` as invariant context and read this OPS in full.

Relevant current state:

- `BASELINE-004` is the current accepted learner-navigation workspace baseline.
- `SPEC-022` completed with verdict `NAVIGATION_GRAMMAR_BETTER` and was promoted unchanged to `BASELINE-004`.
- BASELINE-001 through BASELINE-004 must remain preserved.
- Existing semantic vocabulary and trusted semantic/provenance behavior must remain unchanged.

Read `OPERATING_MODEL.md` where necessary to integrate the new control-plane rules without duplicating or contradicting existing policy.

## Scope

### 1. Add root `STATUS.md`

Create a concise authoritative operational handoff document. It must identify, at minimum:

- canonical accepted baseline(s), with `BASELINE-004` identified as the current learner-navigation workspace baseline;
- last completed work packet and verdict;
- current approved work packet;
- work-packet status;
- current gate / decision required;
- frozen or protected state relevant to the active work;
- next intended action when known.

`STATUS.md` is the authoritative pointer to the active work packet. Agents must not infer active work from filename recency.

During implementation of this OPS, `STATUS.md` should point to this OPS as the current approved packet. At successful completion, update it to record OPS-003 as completed and set the active packet to `NONE` unless another packet has explicitly been approved by then.

`STATUS.md` is durable coordination state, not a manually maintained source for runtime counts or derived product truth.

### 2. Refine root `AGENTS.md`

Preserve the existing role, Git, startup, implementation-boundary, safety, and finish rules. Add only the minimum control-plane behavior needed for low-attention execution.

Normal startup should become conceptually:

```text
AGENTS.md
    ↓
STATUS.md
    ↓
active SPEC/OPS named by STATUS.md
    ↓
only materially relevant historical/deep context
```

Codex must follow the explicit active-work pointer rather than infer work from recency.

### 3. Add an explicit authority model

Integrate the following semantics into `AGENTS.md` and/or `OPERATING_MODEL.md` without unnecessary duplication.

#### Autonomous once an approved contract exists

Codex may autonomously:

- inspect and analyze repository state;
- safely fetch/reconcile/fast-forward with `origin/main` under existing preservation rules;
- implement the approved SPEC/OPS within scope;
- run required offline tests and deterministic evaluations;
- generate contract-required deterministic artifacts;
- repair implementation defects that are clearly inside the active contract;
- commit the approved increment;
- push the completed approved increment to canonical `origin/main` when the contract requires normal canonical review;
- produce the required handoff.

Approval attaches to the decision boundary, not to every mechanical action downstream of it.

#### Stop / require explicit authority

Codex must stop rather than infer authority when work would require:

- an external/live/paid/provider call not explicitly authorized by the active contract and its declared limits;
- changing trusted semantic vocabulary, semantic contracts, provenance rules, or fail-closed behavior outside the active contract;
- modifying a frozen baseline artifact;
- promoting an experiment to a new accepted baseline or canonical product decision without explicit owner/ChatGPT verdict where the contract requires one;
- declaring subjective cognitive/pedagogical/product success that requires owner interaction;
- material scope expansion or resolution of a genuinely ambiguous product/architecture decision;
- destructive operations or overwriting/reinterpreting unrelated user work.

Credential availability never implies authority.

### 4. Standardize a compact contract-control header

Define a minimal header convention for future `SPEC-*` and `OPS-*` documents. Do not rewrite historical contracts merely for conformity.

The convention must make at least these fields explicit when applicable:

```text
Status: DRAFT | APPROVED_FOR_IMPLEMENTATION | IMPLEMENTED_AWAITING_REVIEW | COMPLETED | REJECTED
Authority: OFFLINE_ONLY | LIVE_CALLS_EXPLICITLY_BOUNDED | other explicitly defined bounded authority
Human gate: NONE | OWNER_REVIEW | CHATGPT_REVIEW | OWNER_AND_CHATGPT_REVIEW
Promotion: NOT_AUTHORIZED | explicitly authorized condition
```

Exact syntax may be improved if implementation finds a simpler deterministic representation, but the semantics above must be preserved.

Historical contracts remain valid without retrofitting these headers.

### 5. Define concise Codex handoff protocol

Update operating guidance so normal successful handoffs optimize for owner attention.

The visible handoff should normally contain only:

```text
work packet + completion state
verdict/result
validation summary
material deviations, if any
repository/commit/push state
whether a human decision is required
exact review command if human interaction is required
path to durable detailed evidence/report
```

Do not repeat long machine-generated inventories already preserved in report artifacts unless they are necessary to explain a failure, deviation, safety issue, or decision.

Machine evidence belongs in durable repository artifacts. Chat handoff is a decision interface.

### 6. Preserve evidence vs interpretation boundary

Codex owns implementation evidence:

- implementation;
- tests;
- raw/deterministic evaluation;
- machine result/report artifacts required by the contract;
- commit/push;
- concise handoff.

ChatGPT/owner own interpretation where human judgment is required:

- independent review;
- cognitive/product verdict;
- `DEBRIEF-*` interpretation unless explicitly delegated;
- baseline promotion decision;
- canonical project-model updates motivated by the evidence;
- selection of the next highest-value uncertainty.

Codex must not create the active increment's interpretive DEBRIEF unless explicitly instructed.

### 7. Add deterministic control-plane checks where valuable

Add narrowly scoped offline tests or validation only where they materially reduce coordination failure. Prefer simple deterministic checks over framework construction.

Useful candidates include:

- `STATUS.md` active pointer resolves to an existing SPEC/OPS when non-`NONE`;
- active packet status is compatible with execution;
- malformed control headers fail visibly rather than being silently guessed;
- protected baseline assets remain unchanged.

Do not build a workflow engine, database, service, daemon, scheduler, or generalized agent framework.

## Explicit non-goals

Do not:

- change learner-facing UI or interaction behavior;
- change semantic IR, vocabulary, grounding, provenance, structure detection, representation, or layout;
- modify any executable BASELINE-001, BASELINE-002, BASELINE-003, or BASELINE-004 asset;
- replace SPEC/DEBRIEF/baseline artifacts with a new registry system;
- add `decisions.yaml`, an experiment registry, ticket system, or duplicate project ledger merely because Opportunity Radar has one;
- rewrite all historical SPECs/OPS files to add new headers;
- introduce autonomous product decisions;
- allow Codex to promote its own subjective experiment result;
- make live model/provider/network calls;
- add dependencies unless strictly necessary; expected dependency change is none.

## Frozen state

The following must remain byte-identical unless this OPS explicitly names a documentation file for modification:

- all executable assets belonging to BASELINE-001 through BASELINE-004;
- all frozen BASELINE manifests and accepted evaluation fixtures;
- trusted semantic/provenance implementation;
- learner-navigation behavior accepted in SPEC-022 / BASELINE-004.

Documentation explicitly in scope for modification:

- `AGENTS.md`;
- `OPERATING_MODEL.md`;
- new `STATUS.md`;
- this OPS;
- narrowly necessary tests/validation code for the control plane.

Other canonical project documents should change only if a concrete contradiction introduced by this OPS requires a minimal correction.

## Acceptance criteria

### Repository control plane

- root `STATUS.md` exists and is sufficient to identify the active approved work packet without filename inference;
- normal startup semantics are `AGENTS.md → STATUS.md → active contract → relevant context on demand`;
- stale or invalid active pointers are detectable rather than silently guessed.

### Authority

- documentation clearly distinguishes autonomous downstream mechanics from genuine approval boundaries;
- normal approved implementation no longer requires separate owner permission to commit and push when those actions are already required by the active contract;
- unapproved live calls, baseline promotion, subjective owner verdicts, destructive operations, and material scope expansion remain gated.

### Handoff

- normal successful Codex handoff is concise and decision-oriented;
- detailed machine evidence remains available through repository artifacts;
- exact human-review command is included only when human interaction is actually required.

### Preservation

- BASELINE-001 through BASELINE-004 executable/frozen assets remain byte-identical;
- no learner-facing product behavior changes;
- no semantic/provenance behavior changes;
- no live/provider calls occur;
- no new dependency is added unless an unexpected necessity is documented.

### Validation

- focused control-plane tests/checks pass;
- complete offline suite passes;
- final diff contains only OPS-003 scope;
- repository ends with local `main == origin/main` and clean working tree unless an unrelated pre-existing user change makes that impossible, in which case preserve and report it exactly.

## Evaluation

This OPS cannot prove its own operational value merely by producing correct Markdown.

At completion, record the implementation as an operational hypothesis ready for prospective validation.

The first real test is the next approved product/research SPEC:

```text
STATUS.md points to approved packet
        ↓
owner gives Codex only a minimal instruction equivalent to:
"Execute the current approved work packet."
        ↓
Codex completes work autonomously
        ↓
measure whether owner intervention occurred only at genuine decision boundaries
```

The workflow should be retained, modified, or rejected based on observed friction in that prospective run.

## Required handoff

Keep the visible handoff concise. Report:

- `OPS-003` completion state;
- tests/checks;
- files materially changed;
- deviations;
- dependency changes;
- commit SHA and push confirmation;
- final active packet recorded in `STATUS.md`;
- whether any owner decision is required;
- detailed report/artifact path if one exists.

Do not produce a long implementation inventory when repository artifacts already contain it.

## Live-call authority

`OFFLINE_ONLY`

No model, provider, paid API, external semantic, or other live experimental calls are authorized by this OPS.

Ordinary Git fetch/push required by the repository lifecycle is authorized and is not considered an experimental live call.

## Human gate

`CHATGPT_REVIEW`

Implementation correctness should receive independent ChatGPT repository review after Codex completion. No owner cognitive UI review is required because this OPS must not change learner-facing behavior.

## Promotion

`NOT_AUTHORIZED`

Successful implementation establishes the control-plane mechanism for prospective testing. It does not by itself prove that the workflow is superior. Retention as the durable operating model should be judged after at least one real subsequent work packet exercises it.
