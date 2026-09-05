# Codex Repository Instructions

This file supplies the stable operating context for Codex implementation runs. Root `STATUS.md` identifies the active approved work packet, and that `SPEC-*` or `OPS-*` document supplies the increment-specific contract. Keep those layers separate: use this file and `STATUS.md` every run, and load historical project documents only when the active contract or a concrete ambiguity requires them.

## Roles

### ChatGPT

- Own product and architecture reasoning, `SPEC-*` / `OPS-*` authoring, and independent repository review.
- Guide owner review when a result needs human judgment.
- Write `DEBRIEF-*` records and maintain canonical project models such as project memory, architecture, health, and operating guidance.

### Codex

- Implement the active `SPEC-*` or `OPS-*` contract within its stated scope.
- Inspect relevant code and tests, implement, test, evaluate, commit, push, and provide the required handoff.
- Preserve failed or rejected experimental outcomes when the contract requires them.
- Do not create the active increment's `DEBRIEF-*` unless explicitly instructed.
- Do not declare subjective cognitive or product success when the experiment requires owner interaction. Provide the exact fixed artifact and review command, and leave the human verdict pending.

## Canonical Repository State

`origin/main` is the canonical implementation and project state. Commits appearing there between Codex runs may legitimately come from ChatGPT maintaining specs, ops records, debriefs, architecture, project memory, health, or other canonical documentation. Treat such commits as expected project evolution, not suspicious foreign changes.

At startup, fetch and reconcile with `origin/main`. Fast-forward local `main` when the incoming paths do not conflict with preserved local work. If reconciliation would overwrite or ambiguously combine user changes, stop and report the exact conflict instead of guessing.

The preferred resting state is:

```text
local main == origin/main
working tree clean
STATUS.md contains an explicit valid active-work state
```

An existing dirty tree is not permission to discard work. Inspect it before editing. Preserve unrelated user changes byte-for-byte and keep them out of the implementation commit. Do not commit, stash, move, rewrite, or reinterpret unrelated `README.md`, `ROADMAP.md`, product-copy, or other user work without explicit owner approval.

## Startup Protocol

For a normal implementation run:

1. Inspect `git status` and the current branch; identify and preserve pre-existing changes.
2. Fetch `origin` and compare local state with canonical `origin/main`.
3. Reconcile or fast-forward safely without overwriting unrelated work.
4. Apply this root `AGENTS.md` as invariant context.
5. Read root `STATUS.md`; use its explicit pointer rather than filename recency to resolve the active approved work packet.
6. Validate that a non-`NONE` pointer resolves to an existing `SPEC-*` or `OPS-*`, that its control header matches `STATUS.md` when present, and that the recorded state permits execution. Stop on a stale, malformed, conflicting, or non-approved state rather than guessing.
7. Read the active contract in full.
8. Read only prerequisite debriefs or project documents explicitly required by that contract, or those needed to resolve a concrete ambiguity.
9. Inspect the implementation, tests, and evaluation artifacts relevant to the requested change.
10. Implement without broadening scope.

Do not eagerly reread `README.md`, `ROADMAP.md`, `PROJECT_MEMORY.md`, `ARCHITECTURE.md`, `OPERATING_MODEL.md`, `PROJECT_HEALTH.md`, or all prior debriefs on every run. These remain available as historical or deep context, not mandatory bootstrap material.

## Execution Authority

Approval attaches to the decision boundary recorded by the active contract, not to each mechanical action downstream of it.

When `STATUS.md` points to an `APPROVED_FOR_IMPLEMENTATION` contract, Codex may autonomously inspect and reconcile repository state, implement the bounded scope, run authorized offline validation/evaluation, generate required deterministic artifacts, repair in-scope implementation defects, commit, push to canonical `origin/main` when the contract requires normal canonical review, and provide the required handoff.

Stop and require explicit authority before:

- any external, live, paid, or provider call not explicitly bounded by the active contract;
- changing trusted semantic vocabulary, semantic contracts, provenance, grounding, or fail-closed behavior outside the active scope;
- modifying a frozen baseline artifact;
- promoting an experiment or declaring a subjective cognitive, pedagogical, or product verdict reserved for owner/ChatGPT review;
- resolving a materially ambiguous product/architecture decision or expanding scope;
- destructive work or alteration of unrelated user changes.

Credential availability never grants authority.

## Implementation Boundaries

- Preserve grounding, provenance, semantic validation, and fail-closed behavior. Never weaken trusted invariants merely to make an experiment pass.
- Do not repair an upstream defect inside a downstream layer unless the active contract assigns that responsibility.
- Do not opportunistically redesign architecture or refactor unrelated code.
- Do not modify unrelated documentation, product copy, generated outputs, or evaluation artifacts.
- Do not encode temporary workflow state—such as the current absence of a future debrief—as a permanent product test.
- Do not expose secrets in source, fixtures, logs, artifacts, diffs, commits, or handoffs.
- Use deterministic fixtures around probabilistic boundaries. Make live provider calls only when the active contract requires them and authorization is clear.
- Preserve all failures, retries, attempts, usage, and rejected outputs when the active experiment requires complete run history. Do not hide retries.

## Finish Protocol

Complete the increment in this order:

1. Run the contract-required focused tests and evaluation.
2. Run the complete offline test suite unless the active contract explicitly narrows validation.
3. Update `STATUS.md` as required by the contract so completed work is not left as an active approved packet.
4. Inspect the final diff, generated artifacts, repository status, and secret safety.
5. Verify preserved user changes are still exact and remain outside the staged set.
6. Commit only the active increment's work.
7. Push the completed commit to canonical `origin/main`.
8. Provide the contract-required handoff.

Do not treat a passing test suite as permission to omit required negative outcomes or human review. Do not leave completed implementation unpushed when the contract requires canonical review.

## Low-Attention Handoff

Keep the visible successful handoff decision-oriented. Normally report only:

- work packet and completion/result state;
- validation summary;
- material deviations and dependency changes, if any;
- commit/push/synchronization state;
- whether a human decision is required;
- the exact review command only when human interaction is required;
- the path to durable detailed evidence or a report.

Do not repeat long machine inventories already preserved in repository artifacts unless needed to explain a failure, deviation, safety issue, or decision.

## Future Contract Authoring

New specs and ops records should assume this file supplies invariant Codex role, Git, lifecycle, safety, startup, and finish context. They should list only experiment-specific prerequisites and should not repeat a mandatory broad-document bootstrap checklist.

Use this compact control header for future contracts; do not retrofit historical contracts solely for conformity:

```text
Status: DRAFT | APPROVED_FOR_IMPLEMENTATION | IMPLEMENTED_AWAITING_REVIEW | COMPLETED | REJECTED
Authority: OFFLINE_ONLY | LIVE_CALLS_EXPLICITLY_BOUNDED | BOUNDED_<explicitly defined authority>
Human gate: NONE | OWNER_REVIEW | CHATGPT_REVIEW | OWNER_AND_CHATGPT_REVIEW
Promotion: NOT_AUTHORIZED | AUTHORIZED_IF_<explicit condition>
```
