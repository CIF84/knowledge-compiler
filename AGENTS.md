# Codex Repository Instructions

This file supplies the stable operating context for Codex implementation runs. The active `SPEC-*` or `OPS-*` document supplies the increment-specific contract. Keep those layers separate: use this file every run, and load historical project documents only when the active contract or a concrete ambiguity requires them.

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
active contract exists
```

An existing dirty tree is not permission to discard work. Inspect it before editing. Preserve unrelated user changes byte-for-byte and keep them out of the implementation commit. Do not commit, stash, move, rewrite, or reinterpret unrelated `README.md`, `ROADMAP.md`, product-copy, or other user work without explicit owner approval.

## Startup Protocol

For a normal implementation run:

1. Inspect `git status` and the current branch; identify and preserve pre-existing changes.
2. Fetch `origin` and compare local state with canonical `origin/main`.
3. Reconcile or fast-forward safely without overwriting unrelated work.
4. Apply this root `AGENTS.md` as invariant context.
5. Read the active `SPEC-*` or `OPS-*` document in full.
6. Read only prerequisite debriefs or project documents explicitly required by that contract, or those needed to resolve a concrete ambiguity.
7. Inspect the implementation, tests, and evaluation artifacts relevant to the requested change.
8. Implement without broadening scope.

Do not eagerly reread `README.md`, `ROADMAP.md`, `PROJECT_MEMORY.md`, `ARCHITECTURE.md`, `OPERATING_MODEL.md`, `PROJECT_HEALTH.md`, or all prior debriefs on every run. These remain available as historical or deep context, not mandatory bootstrap material.

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
3. Inspect the final diff, generated artifacts, repository status, and secret safety.
4. Verify preserved user changes are still exact and remain outside the staged set.
5. Commit only the active increment's work.
6. Push the completed commit to canonical `origin/main`.
7. Provide the contract-required handoff with validation and evaluation results, deviations, dependency changes, commit SHA, push confirmation, and any exact human-review command.

Do not treat a passing test suite as permission to omit required negative outcomes or human review. Do not leave completed implementation unpushed when the contract requires canonical review.

## Future Contract Authoring

New specs and ops records should assume this file supplies invariant Codex role, Git, lifecycle, safety, startup, and finish context. They should list only experiment-specific prerequisites and should not repeat a mandatory broad-document bootstrap checklist.
