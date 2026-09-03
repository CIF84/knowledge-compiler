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
- independently inspect completed implementation;
- guide focused human review when product behavior cannot be established from repository evidence;
- write DEBRIEFS;
- maintain project memory, architecture, operating model, and health.

Do not accept implementation summaries as verification when repository inspection is possible.

### Codex

- inspect the repository and relevant project memory;
- treat the active SPEC as the implementation contract;
- implement autonomously within scope;
- run deterministic tests and only the evaluation needed to answer the active uncertainty;
- avoid unrelated refactoring;
- preserve failed experimental attempts when required;
- commit and push before review handoff;
- report architecture, validation, evaluation, deviations, and commit SHA;
- for human-facing increments, provide the simplest exact command needed for owner review rather than declaring subjective product success itself.

### GitHub Repository

GitHub is the durable source of truth for implementation, specs, debriefs, project memory, architecture, operating model, health, roadmap, and product thesis. Conversation threads are working context, not durable memory.

## SPEC Protocol

Every increment should have one primary uncertainty. A good SPEC includes objective, rationale, bounded scope, explicit non-goals, architecture constraints, acceptance criteria, validation, expected artifacts, and relevant prior debriefs.

Prefer one major uncertainty per SPEC.

For human-facing experiments, distinguish deterministic implementation acceptance from the human product verdict.

## DEBRIEF Protocol

Every completed SPEC must have a matching DEBRIEF. Debriefs preserve actual outcome, evidence, deviations, findings, decisions, unresolved questions, next implications, and whether canonical models changed.

For UI-bearing increments, do not finalize the debrief until the relevant human interaction has occurred when that interaction is part of the primary experiment.

## Current Practices With Positive Evidence

The following practices have now worked across five implementation cycles:

- separate product/architecture reasoning from implementation orchestration;
- convert decisions into a focused repository SPEC;
- define explicit non-goals to resist scope expansion;
- use the repository as the context carrier so Codex prompts remain short;
- use deterministic fixtures around probabilistic boundaries;
- use accepted outputs from an earlier layer as stable fixtures when testing a downstream layer;
- require live LLM/network evaluation only when it actually tests the active uncertainty;
- prefer fully deterministic/offline experiments when they can answer the question;
- keep provider/model constant when a probabilistic before/after experiment benefits from causal comparability;
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
- accept negative or empty outputs when they truthfully reflect insufficient upstream structure;
- improve probabilistic behavior at prompt/adapter boundaries before weakening trusted invariants;
- let evidence, not preference, update project models;
- for UI-bearing increments, verify repository integrity first and then let the owner interact with the exact fixed artifact before subjective acceptance;
- use screenshots and natural-language observations as lightweight diagnostic evidence when they reveal spatial/interaction issues, without requiring a design-management process.

SPEC-005 strengthens confidence that the operating model can move from architecture experiments into product experiments without losing separation of roles.

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
```

Do not invoke an LLM merely because one exists in the architecture.

## Experimental Comparison Practice

When a SPEC tests an improvement to probabilistic behavior, prefer changing one major variable at a time where practical.

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

Accepted outputs may become fixed inputs for the next deterministic/product layer, isolating downstream behavior from upstream variance.

For interaction/layout experiments, reuse the same representation data where possible so the human comparison isolates presentation behavior rather than semantic changes.

Use this pattern when the comparison itself is decision-relevant. Do not create baseline machinery for every implementation change.

## Failure Attribution Principle

When downstream output is weak, identify whether the weakness comes from:

```text
upstream semantic model
structure detection
representation model
spatial layout
interaction behavior
evaluation expectation
```

Do not repair an upstream defect inside a downstream layer unless the architecture explicitly assigns that responsibility there.

SPEC-005 reinforced this discipline: missing chronology, collapsed states, and endpoint substitutions became more obvious when rendered but remained visible rather than being silently reconstructed by presentation code.

## Human Review Principle

Model calls and deterministic computation are inexpensive; semantic/pedagogical human review is increasingly the larger cognitive cost.

Respond conservatively:

- automate deterministic regression checks when semantics are explicit enough;
- preserve inspectable artifacts;
- use fixed inputs when evaluating downstream product behavior;
- do not replace human semantic or learning-value review with a second LLM judge until that judging mechanism is validated;
- reduce review burden through focused experiments rather than larger evaluation suites by default;
- when the primary uncertainty is subjective product usefulness, let the owner use the artifact before acceptance;
- capture the first natural reaction before turning review into a long questionnaire when that reaction is itself decision-relevant;
- distinguish visual polish feedback from cognitive/interaction feedback.

SPEC-005 showed that a short owner session can expose product constraints — synchronized semantic selection and structure-aware layout — that code inspection and integrity tests cannot reveal.

## UI Experiment Principle

For current-stage viewer work, optimize for cognitive behavior rather than production polish.

Prefer experiments that ask questions such as:

```text
Can I see the structure quickly?
Does selection behave as one semantic object?
Does spatial placement expose the relationship pattern?
Can I inspect why an edge exists?
```

Avoid premature work on branding, broad responsive design, frontend frameworks, animation systems, account flows, or design systems unless a later product experiment requires them.

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
- subjective UI/product success declared without relevant human interaction;
- probabilistic calls used where fixed accepted artifacts could answer the question;
- downstream layers silently repairing upstream semantic defects;
- multiple major variables changing in an experiment that depends on before/after attribution;
- aspirational architecture becoming canonical before implementation evidence;
- decisions living only in chat history;
- repeated rediscovery of prior findings;
- local/remote divergence;
- secrets in logs or handoffs;
- ontology or prompt growth without demonstrated value;
- documentation maintenance costing more than the uncertainty it removes;
- tests validating implementation details rather than product-relevant behavior;
- structurally valid output being mistaken for pedagogically useful output;
- visual polish being mistaken for cognitive improvement.

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

SPEC-004 was an efficiency benchmark for deterministic downstream computation. SPEC-005 extends the pattern: fixed upstream artifacts plus a small viewer and short human session produced direct product evidence with zero model/API cost.

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

A deliberately fresh-thread reconstruction test remains outstanding, although five increasingly concise implementation handoffs provide indirect positive evidence.

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
