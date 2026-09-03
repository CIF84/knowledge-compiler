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
ChatGPT — independent repository review against SPEC
        ↓
if human-facing: owner interacts with fixed artifact
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
- verify SPEC completeness before handoff;
- independently inspect completed implementation;
- guide focused human review when product behavior cannot be established from repository evidence;
- write DEBRIEFS;
- maintain project memory, architecture, operating model, and health.

Do not accept implementation summaries as verification when repository inspection is possible.

### Codex

- apply root `AGENTS.md` as invariant operating context;
- inspect the repository and only the experiment-specific history needed by the active contract;
- treat the active SPEC as the implementation contract;
- implement autonomously within scope;
- run deterministic tests and only the evaluation needed to answer the active uncertainty;
- avoid unrelated refactoring;
- preserve failed experimental attempts when required;
- commit and push before review handoff;
- report architecture, validation, evaluation, deviations, and commit SHA;
- for human-facing increments, provide the simplest exact command needed for owner review rather than declaring subjective product success itself;
- when live provider transmission is not already clearly authorized, request explicit approval before sending source material.

### GitHub Repository

GitHub is the durable source of truth for implementation, specs, debriefs, project memory, architecture, operating model, health, roadmap, baselines, and product thesis. Conversation threads are working context, not durable memory.

`origin/main` is the canonical implementation and project state. Between Codex runs, ChatGPT may legitimately add or update SPECs, OPS records, DEBRIEFs, and canonical project documents there. Codex should fetch and safely fast-forward these expected changes while preserving unrelated local user work.

## Context Loading

Repository context has three layers:

```text
invariant context          → AGENTS.md
active experiment context  → current SPEC or OPS
historical / deep context  → DEBRIEFs and canonical project-model documents
```

A normal Codex implementation run reads the first two layers, then loads historical or deep context only when the active contract explicitly requires it or a concrete ambiguity makes it relevant. Memory should be available, not eagerly loaded. Broad rereading of `README.md`, `ROADMAP.md`, `PROJECT_MEMORY.md`, `ARCHITECTURE.md`, `OPERATING_MODEL.md`, and `PROJECT_HEALTH.md` is not a routine startup requirement.

## SPEC Protocol

Every increment should have one primary uncertainty. A good SPEC includes objective, rationale, bounded scope, explicit non-goals, architecture constraints, acceptance criteria, validation, expected artifacts, and relevant prior debriefs.

New SPECs should assume root `AGENTS.md` supplies invariant Codex role, Git, lifecycle, safety, startup, and finish context. List only experiment-specific prerequisite documents rather than repeating a broad project-document bootstrap checklist.

Prefer one major uncertainty per SPEC.

Before handoff, verify that the committed SPEC is complete — especially acceptance criteria, live-evaluation rules where applicable, and required handoff. SPEC-008 was accidentally truncated and should remain a process warning.

For human-facing experiments, distinguish deterministic implementation acceptance from the human product verdict.

## DEBRIEF Protocol

Every completed SPEC must have a matching DEBRIEF. Debriefs preserve actual outcome, evidence, deviations, findings, decisions, unresolved questions, next implications, and whether canonical models changed.

For UI-bearing or cognitively evaluated increments, do not finalize the debrief until relevant human interaction has occurred.

## Current Practices With Positive Evidence

The following practices are strongly supported:

- separate product/architecture reasoning from implementation orchestration;
- convert decisions into a focused repository SPEC;
- define explicit non-goals to resist scope expansion;
- use the repository as the context carrier so Codex prompts remain short;
- separate invariant `AGENTS.md` context from the active contract and load historical context on demand;
- use deterministic fixtures around probabilistic boundaries;
- use accepted outputs from an earlier layer as stable fixtures when testing a downstream layer;
- require live LLM/network evaluation only when it actually tests the active uncertainty;
- prefer fully deterministic/offline experiments when they can answer the question;
- keep provider/model stable when a probabilistic before/after experiment benefits from causal comparability;
- have Codex implement autonomously rather than micromanaging edits;
- require tests before acceptance;
- require completed implementation to be pushed before independent review;
- independently inspect repository state rather than trusting summaries;
- pair every SPEC with a DEBRIEF;
- preserve current architecture separately from future architecture;
- preserve machine-generated evaluation artifacts separately from human interpretation;
- compare experiments against accepted baselines when possible;
- turn prior observed failures into regression expectations;
- explicitly attribute failures to the layer that caused them instead of repairing them locally by default;
- accept negative, empty, or failed output when it truthfully reflects insufficient or invalid upstream/probabilistic behavior;
- improve probabilistic behavior at prompt/adapter boundaries before weakening trusted invariants;
- let evidence, not preference, update project models;
- for UI-bearing increments, verify repository integrity first and then let the owner interact with the exact fixed artifact before subjective acceptance;
- use screenshots and natural-language observations as lightweight diagnostic evidence;
- prove a product interaction manually/fixed-fixture first, then automate generation only after the interaction demonstrates value;
- keep parent semantic truth immutable when experimenting with child resolution;
- make generated semantic truth independently inspectable before rendering;
- fail closed on provenance contradictions rather than auto-repairing them by default;
- preserve provider failures and rejected runs as experiment evidence rather than hiding them.

## Experiment Selection Principle

Use the least probabilistic experiment that can answer the current uncertainty.

Examples:

```text
question about LLM extraction quality
    → live LLM experiment

question about graph composition
    → accepted KnowledgeModel fixtures + deterministic algorithms

question about representation integrity
    → fixed semantic/structure artifacts + deterministic checks

question about representation usefulness
    → fixed artifacts + direct human interaction

question about semantic-navigation usefulness
    → handcrafted child fixtures + human comparison

question about automatic semantic depth
    → bounded live ResolutionCompiler run + strict grounding + human review
```

Do not invoke an LLM merely because one exists in the architecture.

## Manual-First Automation Principle

For expensive/general architecture, first prove the user-facing behavior with a fixed artifact where practical.

SPEC-007 → SPEC-008 established the preferred sequence:

```text
manual/fixed child model
        ↓
prove semantic-navigation value
        ↓
automate child generation
        ↓
validate grounding + semantic structure
        ↓
human review generated result
```

Do not build generalized generation architecture for an interaction that has not shown value.

## Probabilistic Trust-Boundary Principle

The probabilistic system proposes; deterministic trusted code validates.

```text
provider proposal
        ↓
exact evidence resolution
        ↓
semantic/provenance validation
        ↓
ACCEPT
   or
FAIL CLOSED
```

Do not silently repair a provider contradiction merely to improve success rate.

A grounding failure can be a successful architecture result when the invalid artifact is correctly rejected.

## Experimental Comparison Practice

When a SPEC tests an improvement to probabilistic behavior, prefer changing one major variable at a time where practical.

Where an accepted prior artifact exists:

```text
accepted baseline/reference
      ↓
new bounded change
      ↓
same source/task
      ↓
comparison artifact
      ↓
human review
```

Do not score probabilistic output by lexical similarity to a handcrafted reference when the real question is semantic usefulness and source fidelity.

## Failure Attribution Principle

When output is weak, identify whether the weakness comes from:

```text
source insufficiency
provider proposal
semantic grounding/validation
upstream parent semantic model
resolution strategy
structure detection
representation model
spatial layout
interaction behavior
evaluation expectation
```

Do not repair an upstream defect inside a downstream layer unless responsibility is explicitly assigned there.

## Human Review Principle

Machine checks validate integrity; humans still judge semantic/pedagogical usefulness.

For semantic depth specifically, human review should ask:

```text
Is the child genuinely finer resolution?
Is it still about the parent focus?
Does it expose meaningful mechanism/detail?
Can the parent plausibly be viewed as a compression of the child?
Is the generated structure useful to think with?
```

Do not replace these judgments with a second LLM judge until that mechanism is separately validated.

## Cognitive Baseline / Preset Principle

`BASELINE-001` remains the control for material UI/interaction changes.

Successful interaction grammars may be preserved as cognitive presets when they represent distinct learner/task intents rather than successive obsolete versions.

Current working intents:

```text
Overview
Focus
Contextual / Layers
```

Presets must project the same trusted semantic truth rather than silently changing facts or provenance.

## Semantic-Resolution Principle

Do not equate “deeper” with “more nodes” or universal decomposition.

Current working hypothesis:

```text
SYSTEM     → subsystems/interactions
COMPONENT  → internals
PROCESS    → stages
VARIABLE   → causes/consequences
EVENT      → antecedents/outcomes
CONCEPT    → mechanisms/principles/relationships
```

This mapping must be tested before recursive compilation or active context-map navigation is generalized.

## Navigation Principle

For abstract knowledge, prefer **2D topology + semantic zoom**.

Treat navigation operations as distinct:

```text
Back
→ history

Breadcrumb/path
→ ancestry

Context map
→ neighborhood/lateral movement

Explore/zoom
→ abstraction depth
```

Do not introduce literal 3D merely because it is visually possible. Use 3D only where domain spatial structure itself carries explanatory meaning.

## Security / Secret Handling

- keep API keys in environment variables or approved secret stores;
- never commit `.env` files or literal secrets;
- never echo secret values into handoffs, screenshots, logs, or artifacts;
- report only whether a secret is present, never its value;
- rotate immediately when accidental exposure is suspected;
- request explicit approval before transmitting source material to external providers when authorization is not already clear.

## Process Failure Signals

Watch for:

- SPECs containing multiple unrelated experiments;
- incomplete/truncated SPEC files reaching implementation;
- repeated scope expansion;
- implementation summaries accepted without inspection;
- subjective success declared without relevant human interaction;
- probabilistic calls used where fixed accepted artifacts could answer the question;
- downstream layers silently repairing upstream semantic defects;
- multiple major variables changing in an attribution-sensitive experiment;
- aspirational architecture becoming canonical before implementation evidence;
- decisions living only in chat history;
- repeated rediscovery of prior findings;
- local/remote divergence;
- secrets in logs or handoffs;
- ontology/prompt growth without demonstrated value;
- generated child truth that cannot be inspected independently from presentation;
- recursive architecture introduced before semantic-resolution strategy is understood;
- cognitive presets altering canonical truth;
- documentation maintenance costing more than uncertainty it removes.

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

SPEC-008 is a good example: one successful live Economics generation and one fail-closed Software Architecture rejection were enough to identify semantic-resolution strategy — not recursion or navigation polish — as the next important problem.

## Deep Reconstruction Test

The following is an onboarding or project-recovery sequence for a deliberately fresh collaborator. It is not the startup checklist for a normal Codex implementation run; those runs use `AGENTS.md`, the active contract, and only materially relevant history.

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
10. relevant interface baseline(s)

If this is insufficient to resume safely, project memory is incomplete.

A deliberately fresh-thread reconstruction test remains outstanding.

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
