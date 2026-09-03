# Project Health

## Purpose

This document is the lightweight monitoring surface for alignment, drift, uncertainty, and operating effectiveness.

It observes four project layers:

```text
PRODUCT MODEL
ARCHITECTURE MODEL
OPERATING MODEL
IMPLEMENTATION REALITY
        │
        ▼
   PROJECT HEALTH
```

The purpose is not to create management metrics. It is to detect divergence early and preserve the feedback loops that make the project more effective over time.

## Status Vocabulary

Use qualitative states rather than false precision:

- **ALIGNED** — current evidence and implementation agree
- **WATCH** — no current failure, but an uncertainty or weakness deserves attention
- **DRIFT** — implementation/process/documentation materially disagrees with the current model
- **UNKNOWN** — insufficient evidence

## Current Baseline

| Dimension | Status | Evidence / interpretation |
| --- | --- | --- |
| Product alignment | ALIGNED | SPEC-002 tested the intended next uncertainty: real LLM extraction into the existing IR across five unrelated domains. |
| Scope discipline | ALIGNED | Provider integration, evidence resolution, evaluation, and testing were implemented without adding UI, persistence, multiple providers, or structure detection. |
| Architecture alignment | ALIGNED | The real provider remained behind `KnowledgeExtractor`; `KnowledgeModel`, pipeline, and deduplication stayed provider-neutral. |
| Memory alignment | ALIGNED | SPEC-002 now has a paired DEBRIEF and canonical memory/architecture/process/health documents have been updated from evidence. |
| Process effectiveness | ALIGNED | The second full ChatGPT → SPEC → Codex → push → review → DEBRIEF cycle completed with less repository-state friction and a concise implementation prompt. |
| Test confidence | ALIGNED | Reported suite expanded to 25 offline tests covering provider, evidence resolution, CLI, evaluation, and prior behavior. Live execution was additionally exercised across five domains. |
| Complexity discipline | ALIGNED | No generalized AI platform, visualization stack, database, ontology framework, or repair engine was introduced. |
| Reproducibility | WATCH | Repository context was sufficient for a short implementation prompt, but a deliberately fresh-thread reconstruction test remains unperformed. |
| Repository state discipline | ALIGNED | SPEC-002 required and reported push to canonical `origin/main` before review; the prior local-only review blocker did not recur. |
| Semantic generality | ALIGNED | One unchanged IR represented recognizable structure across physics, software architecture, economics, biology, and history. |
| Real extraction reliability | WATCH | All five domains produced validated outputs, but software architecture required two rejected attempts and a prompt revision. Reliability is promising, not yet robust. |
| Relationship vocabulary fitness | DRIFT | Cross-domain evaluation exposed systematic vocabulary gaps and semantically distorted edges, especially in biology and history. |
| Semantic relationship precision | DRIFT | Several schema-valid edges had reversed direction, incorrect predicates, or meaning not supported by the source. |
| Source grounding | ALIGNED | Exact-quote → deterministic-offset resolution preserved strong evidence invariants and correctly rejected ambiguous/missing evidence. |
| Security / secret handling | WATCH | No key was reported committed, but the evaluation key appeared in internal terminal-state output and should be rotated. |
| Cost / effort efficiency | WATCH | SPEC-002 demonstrates extremely low direct model-call cost for a five-domain experiment, but more cycles are needed before broader implementation-efficiency claims. |

## Highest-Value Current Uncertainty

> Can we define and enforce a better semantic relationship grammar so that valid edges preserve meaning and direction across domains rather than forcing concepts into the nearest available relationship label?

This should drive SPEC-003.

## Active Watch / Drift Items

### W-001 — Fresh-context reconstruction

The repository memory reduced implementation-prompt size and appears sufficient for context recovery, but a genuinely fresh-thread reconstruction has not yet been tested.

**Desired test:** start a future fresh thread/session using only repository artifacts and assess whether product intent, current architecture, operating process, prior learnings, and next work can be reconstructed correctly.

### W-002 — Real extraction retry behavior

Software architecture required two rejected attempts before prompt v2 succeeded.

**Current response:** keep fail-closed validation and improve probabilistic behavior at the prompt/adapter boundary rather than weakening invariants.

### D-001 — Relationship vocabulary fit

Observed gaps include binding/attachment, transport/delivery, prohibition, generic directional influence, unchanged-state semantics, and actor/event relationships.

**Response:** use the five-domain failures as regression evidence for a focused semantic-grammar experiment. Do not add an uncontrolled universal ontology.

### D-002 — Semantic edge precision

Examples include reversed `PART_OF`, misused `EXERTS_FORCE_ON`, misleading `ENABLES`, incorrect `INCREASES`, and invalid `TRANSFORMS_INTO` relationships.

**Response:** future semantic validation must inspect meaning and direction, not merely enum/schema validity.

### W-003 — Entity/state/process distinction

Changing electric/magnetic fields were collapsed into base field entities.

**Response:** treat entity vs state/condition vs process as a concrete modeling question for later experimentation; do not redesign the IR yet.

### W-004 — Inference provenance model

The strict `SOURCE` vs `INFERRED` distinction caught a real provider failure. A separate `supporting_evidence` concept remains unproven.

**Response:** keep current strict behavior until a concrete use case requires more expressive provenance.

### W-005 — Secret rotation

The API key used for SPEC-002 appeared in internal terminal-state output during environment handoff.

**Response:** rotate the key and avoid echoing secrets into visible handoff/logging surfaces in future cycles.

## Resolved Watch Items

### R-001 — Local vs remote repository state

SPEC-002 required push before review and reported matching local/canonical remote state. The SPEC-001 review blocker did not recur.

### R-002 — Installed CLI fixture path

Fixture extraction now requires an explicit `--fixture`, removing dependence on a repository-relative default path during installed use.

## Drift Triggers

Mark a dimension `DRIFT` when examples such as these occur:

- implementation bypasses `KnowledgeModel` for downstream features
- vendor-specific LLM types leak into the semantic core
- UI independently interprets source text
- source-derived claims lose evidence provenance
- schema-valid edges repeatedly encode wrong meaning or direction
- a SPEC repeatedly expands beyond its stated experiment
- architecture documents describe a system that is no longer implemented
- important decisions exist only in chat history
- debrief findings are repeatedly ignored by later SPECs
- project process becomes materially slower because of documentation overhead

## Review Cadence

Review this file after every completed SPEC/DEBRIEF pair, but change only statuses supported by new evidence.

The review should answer:

1. Did implementation test the intended uncertainty?
2. Did scope remain bounded?
3. Does implementation still match current architecture?
4. Were meaningful findings preserved?
5. Did the operating process reduce or create friction?
6. Did tests increase confidence in behavior that matters?
7. Did complexity increase proportionately to learning?
8. Could a fresh context reconstruct the project?
9. What uncertainty was reduced?
10. What is now the highest-value uncertainty?

## Convergence Goal

The project should improve along two coupled feedback loops.

### Product loop

```text
SPEC → implementation → evidence → DEBRIEF → better product/architecture decisions
```

### Operating loop

```text
SPEC → implementation → friction/results → DEBRIEF
                                      │
                                      ▼
                               OPERATING_MODEL
                                      │
                                      ▼
                            better next experiment
```

Over time, evidence should reduce uncertainty about both **what to build** and **how to build it effectively**.

The desired result is not maximum documentation. It is progressively lower cost, faster implementation, less rework, stronger architectural alignment, and greater confidence that useful past practices can be reconstructed and reused.
