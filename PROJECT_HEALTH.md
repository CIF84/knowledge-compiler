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
| Product alignment | ALIGNED | SPEC-001 tested the foundational product assumption that explanatory prose can be represented as structured semantic IR. |
| Scope discipline | ALIGNED | SPEC-001 remained intentionally limited to text → KnowledgeModel; real LLM extraction and UI were deferred. |
| Architecture alignment | ALIGNED | Implementation matches the current normalization → extraction → deduplication → KnowledgeModel architecture. |
| Memory alignment | ALIGNED | SPEC-001 now has a paired DEBRIEF and canonical memory documents exist. |
| Process effectiveness | WATCH | First complete ChatGPT → SPEC → Codex → review → DEBRIEF cycle worked well, but one cycle is weak evidence. |
| Test confidence | ALIGNED | Deterministic semantic pipeline and important invalid states are covered; reported suite passed. |
| Complexity discipline | ALIGNED | No database, UI, vendor SDK, generalized persistence, or premature structure engine was added. |
| Reproducibility | WATCH | Repository now contains reconstruction artifacts, but reconstruction has not yet been tested from a genuinely fresh context. |
| Repository state discipline | WATCH | SPEC-001 initially existed as a local-only commit and required an explicit push before independent verification. |
| Semantic generality | UNKNOWN | Only electromagnetism has been implemented as a golden semantic extraction fixture. |
| Real extraction reliability | UNKNOWN | No actual LLM adapter has yet produced the IR from unseen text. |
| Relationship vocabulary fitness | WATCH | Initial grammar works for electromagnetism but has not been tested across unrelated domains. |
| Cost / effort efficiency | UNKNOWN | Too few cycles exist to establish a useful implementation-efficiency baseline. |

## Highest-Value Current Uncertainty

> Can a real LLM reliably transform previously unseen explanatory text into the existing validated `KnowledgeModel` across deliberately different domains without changing downstream architecture?

This should drive SPEC-002.

## Active Watch Items

### W-001 — Fresh-context reconstruction

The project is designed to survive loss of conversation context, but this has not yet been experimentally tested.

**Desired test:** start a future fresh thread/session using only repository artifacts and assess whether product intent, current architecture, operating process, prior learnings, and next work can be reconstructed correctly.

### W-002 — Local vs remote repository state

SPEC-001 review was briefly blocked because the implementation commit existed locally but had not yet been pushed.

**Current response:** treat GitHub as the canonical review state and include push/remote-state confirmation in implementation handoff.

### W-003 — Installed CLI fixture path

The default fixture path is repository-oriented and may not work in an installed wheel.

**Response:** non-blocking for SPEC-001; correct opportunistically when the CLI is next changed.

### W-004 — Inference provenance model

`INFERRED` semantic objects currently cannot retain evidence spans. Future extraction may demonstrate the need to distinguish explicit evidence from supporting evidence.

**Response:** do not redesign speculatively; observe real extraction behavior first.

## Drift Triggers

Mark a dimension `DRIFT` when examples such as these occur:

- implementation bypasses `KnowledgeModel` for downstream features
- vendor-specific LLM types leak into the semantic core
- UI independently interprets source text
- source-derived claims lose evidence provenance
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
