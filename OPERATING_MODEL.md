# Operating Model

## Purpose

This document describes the **current experimentally supported way of building Knowledge Compiler**. The goal is not process compliance; it is faster and more reliable learning.

## Core Operating Loop

```text
QUESTION / UNCERTAINTY
        ↓
ChatGPT — product and architecture reasoning
        ↓
SPEC-N — bounded implementation experiment
        ↓
Codex — implementation + tests + evaluation + commit + push
        ↓
GitHub — canonical implementation state
        ↓
ChatGPT — independent review against SPEC
        ↓
DEBRIEF-N — evidence, findings, deviations, learnings
        ↓
update canonical project models when warranted
        ↓
next highest-value uncertainty
```

## Roles

### ChatGPT

- identify the highest-value uncertainty;
- define narrow experiments;
- write implementation SPECs;
- independently inspect completed implementation;
- write DEBRIEFs;
- maintain project memory, architecture, operating model, and health.

Do not accept implementation summaries as verification when repository inspection is possible.

### Codex

- inspect the repository and relevant project memory;
- treat the active SPEC as the implementation contract;
- implement autonomously within scope;
- run deterministic tests and required live evaluation;
- avoid unrelated refactoring;
- preserve failed experimental attempts when required;
- commit and push before review handoff;
- report architecture, validation, evaluation, deviations, and commit SHA.

### GitHub Repository

GitHub is the durable source of truth for implementation, specs, debriefs, project memory, architecture, operating model, health, roadmap, and product thesis. Conversation threads are working context, not durable memory.

## SPEC Protocol

Every increment should have one primary uncertainty. A good SPEC includes objective, rationale, bounded scope, explicit non-goals, architecture constraints, acceptance criteria, validation, expected artifacts, and relevant prior debriefs.

Prefer one major uncertainty per SPEC.

## DEBRIEF Protocol

Every completed SPEC must have a matching DEBRIEF. Debriefs preserve actual outcome, evidence, deviations, findings, decisions, unresolved questions, next implications, and whether canonical models changed.

## Current Practices With Positive Evidence

The following practices have now worked across three implementation cycles:

- separate product/architecture reasoning from implementation orchestration;
- convert decisions into a focused repository SPEC;
- define explicit non-goals to resist scope expansion;
- use the repository as the context carrier so Codex prompts remain short;
- use deterministic fixtures around probabilistic boundaries;
- require real evaluation only when it tests the active uncertainty;
- keep provider/model constant when a before/after experiment benefits from causal comparability;
- have Codex implement autonomously rather than micromanaging edits;
- require tests before acceptance;
- require completed implementation to be pushed before independent review;
- independently inspect repository state rather than trusting summaries;
- pair every SPEC with a DEBRIEF;
- preserve current architecture separately from future architecture;
- preserve machine-generated evaluation artifacts separately from human interpretation;
- compare experiments against accepted baselines when possible;
- turn prior observed failures into regression expectations;
- accept negative findings instead of hiding them behind repair heuristics;
- improve probabilistic behavior at prompt/adapter boundaries before weakening trusted invariants;
- let evidence, not preference, update project models.

SPEC-003 strengthens confidence that this operating model is converging rather than merely documenting activity.

## Experimental Comparison Practice

When a SPEC tests an improvement to probabilistic behavior, prefer changing one major variable at a time where practical.

SPEC-003 kept the provider, model, and five-domain corpus constant while changing relationship semantics. This made the before/after result materially more interpretable.

Where an accepted prior artifact exists:

```text
accepted baseline
      ↓
new bounded change
      ↓
same evaluation corpus
      ↓
comparison artifact
      ↓
human review
```

Use this pattern when the comparison itself is decision-relevant. Do not create baseline machinery for every implementation change.

## Human Review Principle

Live model calls are currently inexpensive; semantic human review is becoming the larger cognitive cost.

Respond conservatively:

- automate deterministic regression checks when semantics are explicit enough;
- preserve inspectable artifacts;
- do not replace human semantic review with a second LLM judge until that judging mechanism is itself validated;
- reduce review burden through focused experiments rather than larger evaluation suites by default.

## Security / Secret Handling

- keep API keys in environment variables or approved secret stores;
- never commit `.env` files or literal secrets;
- never echo secret values into handoffs, screenshots, logs, or artifacts;
- report only whether a secret is present, never its value;
- rotate immediately when accidental exposure is suspected.

## Process Failure Signals

Watch for:

- SPECs containing multiple unrelated experiments;
- repeated scope expansion;
- implementation summaries accepted without inspection;
- multiple major variables changing in an experiment that depends on before/after attribution;
- aspirational architecture becoming canonical before implementation evidence;
- decisions living only in chat history;
- repeated rediscovery of prior findings;
- local/remote divergence;
- secrets in logs or handoffs;
- ontology or prompt growth without demonstrated value;
- documentation maintenance costing more than the uncertainty it removes;
- tests validating implementation details rather than product-relevant behavior;
- schema-valid output being mistaken for product-valid output.

## Efficiency Principle

Optimize for:

```text
implementation effort
        ↓
validated learning
        ↓
reduced uncertainty
        ↓
better next experiment
```

SPEC-002 and SPEC-003 show that five-domain live semantic experiments can be run at very low direct model cost. The binding constraint is increasingly interpretation quality, not API spend.

## Reconstruction Test

A fresh collaborator should reconstruct the project approximately in this order:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. relevant `DEBRIEF-*`
8. active `SPEC-*`
9. implementation/tests/evaluation artifacts

If this is insufficient to resume safely, project memory is incomplete.

A deliberately fresh-thread reconstruction test remains outstanding, although three increasingly concise implementation handoffs provide indirect positive evidence.

## Evolution Rule

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

Do not optimize process from preference alone when normal project work can test it.
