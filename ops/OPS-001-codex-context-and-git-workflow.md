# OPS-001 — Codex Context and Git Workflow Optimization

## Status

Ready for implementation.

## Type

Operational maintenance increment. **Not a product SPEC.**

Do not create a `DEBRIEF-010` or consume the next product SPEC number for this work.

## Primary Question

> Can we reduce repetitive Codex bootstrap/reconciliation work and token usage by making stable repository roles, Git expectations, and context-loading rules explicit and automatically available?

## Observed Problem

During SPEC-009, Codex spent meaningful context/reasoning on questions that should already be settled by the repository operating system:

- interpreting ChatGPT-authored commits that appeared between Codex runs;
- deciding whether canonical remote commits were safe to fast-forward;
- rediscovering the ChatGPT/Codex role split;
- repeatedly proving that long-lived local `README.md` / `ROADMAP.md` edits were unrelated;
- eagerly reading broad project-memory documents even when the active SPEC already contained the relevant contract;
- encountering a permanent test that encoded a temporary lifecycle condition (`DEBRIEF-008` must not exist), then repairing that mismatch.

This is operational entropy rather than product implementation.

## Desired Context Architecture

Separate project context into three layers:

```text
INVARIANT CONTEXT
→ AGENTS.md
→ stable Codex role / Git / lifecycle / safety contract
→ automatically applicable every run

ACTIVE EXPERIMENT CONTEXT
→ current SPEC or OPS document
→ exact delta being implemented

HISTORICAL / DEEP CONTEXT
→ DEBRIEFs
→ PROJECT_MEMORY.md
→ ARCHITECTURE.md
→ PROJECT_HEALTH.md
→ OPERATING_MODEL.md
→ read only when the active work actually requires them
```

Principle:

> **Memory should be available, not eagerly loaded.**

## Scope

### 1. Add root `AGENTS.md`

Create a concise root `AGENTS.md` containing stable implementation instructions for Codex.

Target roughly 1–2k tokens. Do not duplicate the full operating model.

It should establish at least:

### Role

```text
ChatGPT
→ product/architecture reasoning
→ SPEC/OPS authoring
→ independent repository review
→ human-review guidance
→ DEBRIEFs and canonical project-model updates

Codex
→ implement the active SPEC/OPS contract
→ test/evaluate
→ preserve scope
→ commit/push
→ provide handoff
```

Codex should not create the active increment's DEBRIEF unless explicitly instructed.

### Canonical repository state

```text
origin/main is canonical implementation/project state.

Commits appearing on origin/main between Codex runs may legitimately come from
ChatGPT maintaining SPECs, DEBRIEFs, architecture, project memory, health, or
operational records.

Such commits are expected project evolution, not suspicious foreign changes.
```

### Startup protocol

A normal implementation run should approximately do:

```text
1. inspect git status
2. fetch origin
3. reconcile/fast-forward canonical main when safe
4. preserve unrelated local user changes
5. read AGENTS.md automatically/applicably
6. read the active SPEC/OPS document
7. read only prior DEBRIEFs/files explicitly required by that contract or needed to resolve a concrete ambiguity
8. inspect implementation/tests relevant to the change
9. implement
```

Do not require eager rereading of every project document.

### Finish protocol

```text
implementation
→ required tests
→ required evaluation
→ inspect diff / secret safety
→ commit
→ push canonical origin/main
→ handoff
```

### Stable prohibitions

Include concise rules such as:

- do not weaken grounding/semantic invariants merely to make an experiment pass;
- do not repair upstream defects inside downstream layers unless the active contract assigns that responsibility;
- do not modify unrelated README/ROADMAP/product-copy work;
- do not opportunistically redesign architecture;
- do not create a DEBRIEF for the active implementation unless explicitly requested;
- do not encode temporary workflow/lifecycle state as permanent product tests;
- do not expose secrets;
- preserve failed experimental outcomes when the active contract requires them.

### Human/product verdict

Codex should not declare subjective cognitive/product success when the active experiment requires owner interaction. It should provide the exact review artifact/command and leave the human verdict pending.

## 2. Remove lifecycle-temporary test invariants

Inspect tests for assertions whose only purpose is to enforce temporary implementation-stage workflow state, especially assertions equivalent to:

```text
DEBRIEF-N must not exist
```

A completed increment is expected to gain a debrief after owner/repository review, so such assertions become false by design.

Remove or replace these with durable implementation invariants.

Do **not** remove tests that genuinely protect product behavior, provenance, semantic integrity, or artifact boundaries.

Search beyond SPEC-008 for the same anti-pattern.

## 3. Simplify future SPEC bootstrap expectations

Do not rewrite all historical SPECs.

Instead, update the durable operating guidance so future SPECs no longer need boilerplate requiring Codex to read all of:

```text
README.md
ROADMAP.md
PROJECT_MEMORY.md
ARCHITECTURE.md
OPERATING_MODEL.md
PROJECT_HEALTH.md
```

The active contract should reference only historical documents materially required for the experiment.

Update `OPERATING_MODEL.md` to record this lazy-context-loading practice.

If appropriate, add a small authoring rule:

> New SPECs should assume `AGENTS.md` supplies invariant Codex operating context and should list only experiment-specific prerequisite documents.

## 4. Resolve persistent README/ROADMAP dirty-tree friction safely

The local working tree has carried unrelated user edits to `README.md` and `ROADMAP.md` through multiple implementation cycles.

**Do not discard, rewrite, commit, stash, or move these user edits without explicit owner approval.**

For OPS-001:

- identify and report their presence;
- ensure `AGENTS.md` tells Codex how to preserve unrelated user changes;
- do not spend repeated reasoning trying to reinterpret them;
- propose the simplest one-time cleanup option in the handoff.

Preferred future invariant is:

```text
local main == origin/main
working tree clean
active contract exists
```

But achieving that invariant must not destroy or silently canonicalize the owner's current product-copy edits.

Possible handoff options may include:

- owner approves committing them to main;
- owner approves moving them to a dedicated WIP branch;
- owner deliberately keeps them local and accepts the remaining friction.

Do not choose on the owner's behalf.

## 5. Measure bootstrap improvement

Create a lightweight deterministic or documented comparison of old vs new startup behavior.

Do not pretend to measure exact token savings unless tooling exposes reliable counts.

At minimum report:

```text
before:
- broad mandatory docs normally read
- repeated role/Git ambiguity
- lifecycle-test mismatch risk

after:
- AGENTS.md invariant context
- active contract as primary delta
- historical docs on demand
- canonical-commit expectation explicit
- lifecycle-temporary tests removed
```

If Codex can report approximate context/file reads for this run and a subsequent fresh run, preserve them as observational evidence, not a scientific benchmark.

## 6. No product behavior changes

OPS-001 must not change:

- semantic extraction;
- relationship grammar;
- KnowledgeModel;
- resolution strategies;
- structure detection;
- representation;
- layout;
- navigation;
- viewer behavior;
- cognitive presets;
- live evaluation outputs.

This is repository-operating-system maintenance only.

## Files Expected

Likely changes:

```text
AGENTS.md
OPERATING_MODEL.md
relevant lifecycle-only tests
possibly a small ops evidence artifact
```

Do not update `ARCHITECTURE.md`, `PROJECT_MEMORY.md`, or `PROJECT_HEALTH.md` unless the operational change genuinely requires it. ChatGPT can update canonical project records after review.

## Validation

Run the complete offline test suite.

Verify:

- no product behavior artifacts changed unexpectedly;
- no semantic/evaluation golden outputs changed unless caused solely by removing invalid lifecycle assertions;
- `AGENTS.md` is concise and non-duplicative;
- current role split matches `OPERATING_MODEL.md`;
- no secrets are present;
- unrelated README/ROADMAP edits are byte-preserved locally;
- Git diff contains only OPS-001 work plus the pre-existing user edits.

## Acceptance Criteria

- [ ] Root `AGENTS.md` exists.
- [ ] `AGENTS.md` defines ChatGPT/Codex roles concisely.
- [ ] `AGENTS.md` defines canonical `origin/main` expectations.
- [ ] ChatGPT-authored canonical commits between Codex runs are explicitly treated as expected project state.
- [ ] Startup and finish protocols are concise and explicit.
- [ ] Historical project memory is lazy-loaded rather than mandatory every run.
- [ ] Future SPEC authoring assumes invariant context comes from `AGENTS.md`.
- [ ] Lifecycle-temporary permanent tests are removed/replaced.
- [ ] Product behavior is unchanged.
- [ ] Full offline tests pass.
- [ ] README/ROADMAP user edits remain untouched.
- [ ] No secrets are introduced.
- [ ] Changes are committed and pushed to canonical `origin/main`.

## Required Handoff

Report:

1. `AGENTS.md` structure and approximate size;
2. startup protocol;
3. finish protocol;
4. role contract;
5. Git/canonical-state contract;
6. lazy context-loading rule;
7. tests removed/changed and why they were lifecycle-temporary rather than product invariants;
8. `OPERATING_MODEL.md` changes;
9. before/after bootstrap comparison;
10. exact offline test result;
11. confirmation product artifacts/behavior did not change;
12. README/ROADMAP preservation confirmation and hashes if useful;
13. recommended one-time resolution for those local edits, without executing it;
14. dependencies added/removed;
15. deviations;
16. commit SHA;
17. confirmation pushed to canonical `origin/main`.

Do not create another DEBRIEF as part of OPS-001. ChatGPT will review the operational change and update canonical project records if warranted.
