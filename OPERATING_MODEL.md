# Operating Model

## Purpose

This document describes the **current experimentally supported way of building Knowledge Compiler**.

The operating model is itself a hypothesis that improves through use. We preserve practices that reduce uncertainty, implementation cost, rework, and coordination overhead; we change practices when evidence shows a better way.

The goal is not process compliance. The goal is faster and more reliable learning.

## Core Operating Loop

```text
QUESTION / UNCERTAINTY
        │
        ▼
ChatGPT — product and architecture reasoning
        │
        ▼
SPEC-N — bounded implementation experiment
        │
        ▼
Codex — implementation + tests + commit
        │
        ▼
GitHub — canonical implementation state
        │
        ▼
ChatGPT — independent review against SPEC
        │
        ▼
DEBRIEF-N — evidence, findings, deviations, learnings
        │
        ▼
update canonical project models when warranted
        │
        ├── PROJECT_MEMORY.md
        ├── ARCHITECTURE.md
        ├── OPERATING_MODEL.md
        └── PROJECT_HEALTH.md
        │
        ▼
next highest-value uncertainty
```

## Roles

### ChatGPT

Primary responsibilities:

- product reasoning
- architecture reasoning
- identify the highest-value uncertainty
- define narrow experiments
- write implementation SPECs
- independently inspect completed implementation
- write/review DEBRIEFs
- maintain canonical project models

ChatGPT should not accept implementation summaries as verification when repository inspection is possible.

### Codex

Primary responsibilities:

- inspect the repository and relevant project memory before implementation
- treat the active SPEC as the implementation contract
- implement autonomously within scope
- run tests and relevant packaging/validation checks
- avoid unrelated refactoring
- commit completed work
- report architecture, changed files, validation results, deviations, and commit SHA

### GitHub Repository

The repository is the durable source of truth for:

- implementation
- specifications
- debriefs
- project memory
- architecture baseline
- operating model
- project health
- roadmap and product thesis

Conversation threads are working contexts, not durable project memory.

## SPEC Protocol

Every implementation increment should have one primary SPEC.

A good SPEC should contain:

- question or uncertainty being tested
- objective
- rationale
- scope
- explicit non-goals
- architectural constraints
- acceptance criteria
- tests/validation expectations
- expected outputs
- relevant prior debriefs and canonical documents to read

Prefer one major uncertainty per SPEC.

## DEBRIEF Protocol

Every completed SPEC must have a matching DEBRIEF.

```text
specs/SPEC-NNN-name.md
debriefs/DEBRIEF-NNN-name.md
```

The debrief records reality rather than intent:

- what was implemented
- what was verified
- deviations from the SPEC
- unexpected findings
- design decisions
- what worked
- what created friction
- unresolved questions
- implications for the next experiment
- whether product, architecture, or operating-model understanding changed

A debrief is not a changelog. It preserves why the project now believes what it believes.

## Canonical-Model Update Rule

At the end of each debrief ask:

```text
Did this increment change our understanding of:

[ ] Product / project memory
[ ] Architecture
[ ] Operating process
[ ] Project health / risk
[ ] None
```

Only update a canonical document when evidence warrants it.

This prevents speculative discussion from silently becoming project doctrine.

## Current Practices With Positive Evidence

The following practices have worked in the initial project cycle and should remain defaults until contradicted by evidence:

- separate product/architecture reasoning from implementation orchestration
- convert decisions into a focused repository SPEC
- define explicit non-goals to resist scope expansion
- test semantic foundations before investing in UI
- use deterministic fixtures around probabilistic boundaries where possible
- have Codex implement autonomously rather than micromanaging individual edits
- require tests before accepting an increment
- independently inspect repository state after Codex reports completion
- distinguish local commits from pushed GitHub state
- pair every SPEC with a DEBRIEF
- preserve current architecture separately from future architecture
- let evidence update project models

Current evidence strength is low because only one full implementation cycle has completed. These are working hypotheses, not immutable rules.

## Process Failure Signals

Watch for:

- SPECs containing multiple unrelated experiments
- repeated scope expansion during implementation
- implementation summaries accepted without inspection
- architecture documentation describing planned rather than current reality
- decisions existing only in conversation history
- repeated rediscovery of previously answered questions
- local/remote repository divergence causing verification friction
- documentation maintenance costing more than the uncertainty it removes
- tests validating implementation details rather than product-relevant behavior
- abstractions introduced before a concrete second use case exists

## Efficiency Principle

The operating model should converge toward lower cost per useful learning.

We care about the relationship:

```text
implementation effort
        ↓
validated learning
        ↓
reduced uncertainty
        ↓
better next experiment
```

A technically larger increment is not necessarily more productive. Prefer experiments that maximize decision-relevant learning for the least implementation and coordination cost.

## Reconstruction Test

A new ChatGPT/Codex thread should be able to reconstruct the project by reading, approximately in this order:

1. `README.md` — what and why
2. `ROADMAP.md` — direction
3. `PROJECT_MEMORY.md` — accumulated learning
4. `ARCHITECTURE.md` — current system
5. `OPERATING_MODEL.md` — how the project is built
6. `PROJECT_HEALTH.md` — current alignment, drift, risks, uncertainty
7. relevant `DEBRIEF-*` files — evidence/history
8. active `SPEC-*` — current experiment
9. implementation/tests — executable reality

If this is insufficient to resume work safely, project memory is incomplete.

## Evolution Rule

The operating model is versioned implicitly through Git history and explicitly through debrief evidence.

When a process change is proposed:

```text
process hypothesis
      ↓
try it on a bounded increment
      ↓
observe effort / friction / quality / uncertainty reduction
      ↓
DEBRIEF
      ↓
retain, modify, or reject
```

Do not optimize process from preference alone when it can be tested through normal project work.
