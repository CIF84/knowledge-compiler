# Project Health

## Purpose

This document is the lightweight monitoring surface for alignment, drift, uncertainty, and operating effectiveness.

## Status Vocabulary

- **ALIGNED** — current evidence and implementation agree
- **WATCH** — no current failure, but an uncertainty or weakness deserves attention
- **DRIFT** — implementation/process/documentation materially disagrees with the current model
- **UNKNOWN** — insufficient evidence

## Current Baseline

| Dimension | Status | Evidence / interpretation |
| --- | --- | --- |
| Product alignment | ALIGNED | SPEC-003 tested the highest-value uncertainty identified by SPEC-002: whether explicit relationship semantics improve cross-domain edge truthfulness. |
| Scope discipline | ALIGNED | Work stayed limited to relationship semantics, prompting, regression evaluation, and tests. |
| Architecture alignment | ALIGNED | `KnowledgeModel` and `KnowledgeExtractor` boundaries remain intact; relationship semantics were added as provider-independent core metadata. |
| Memory alignment | ALIGNED | SPEC-003 now has a paired DEBRIEF and canonical project models reflect its findings. |
| Process effectiveness | ALIGNED | Third complete repo-centered cycle succeeded; prior debrief evidence became regression input and push-before-review again avoided state ambiguity. |
| Test confidence | ALIGNED | Reported suite expanded to 32 offline tests; live five-domain evaluation and artifact round-trips also completed. |
| Complexity discipline | ALIGNED | Vocabulary grew by only three general predicates; no universal ontology, UI, persistence, or structure engine was introduced. |
| Reproducibility | WATCH | Repository context continues to support concise handoffs, but a deliberately fresh-thread reconstruction test remains outstanding. |
| Repository state discipline | ALIGNED | Implementation was committed and pushed before review; canonical remote state was explicit. |
| Semantic generality | ALIGNED | The same grammar and IR operate across five unrelated domains. |
| Real extraction reliability | WATCH | SPEC-003 completed five domains with no retries, but one successful run is not enough to claim robust probabilistic reliability. |
| Relationship vocabulary fitness | ALIGNED | Explicit contracts plus three general predicates materially improved vocabulary fit across the benchmark. No immediate further expansion is justified. |
| Semantic relationship precision | WATCH | Precision improved materially, but endpoint selection, polarity, `MEASURED_BY`, and duplicate-edge issues remain. |
| Source grounding | ALIGNED | Exact-quote → deterministic-offset grounding remained intact. |
| Entity/event/state modeling | WATCH | Remaining failures increasingly involve endpoint choice, actor/event distinctions, and state/process representation. |
| Duplicate relationship control | WATCH | New duplicate edges appeared in electromagnetism and economics. |
| Prompt complexity | WATCH | Relationship instructions grew substantially (~1.5k → ~9.7k characters); current cost remains low but ontology/prompt growth is no longer free. |
| Security / secret handling | WATCH | Secret-handling rules exist; confirm exposed SPEC-002 key rotation outside repository evidence. |
| Cost / effort efficiency | ALIGNED | Five-domain live experiments remain inexpensive and now provide meaningful before/after product evidence. |

## Highest-Value Current Uncertainty

> Can the current grounded semantic graph be composed deterministically into useful higher-order structures — such as hierarchies, causal paths, temporal/process chains, dependencies, and feedback candidates — without re-reading the source text?

This should drive SPEC-004.

## Active Watch Items

### W-001 — Fresh-context reconstruction

A genuinely fresh-thread reconstruction test remains unperformed.

### W-002 — Endpoint / event / state semantics

Remaining errors often select a nearby entity rather than the actual policy, regulation, event, state, or process named by the proposition.

**Response:** carry as a known constraint into structure detection; redesign the IR only if the next experiment demonstrates a concrete blocker.

### W-003 — Polarity preservation

`AFFECTS` can preserve directional influence while losing prevention/negative polarity.

**Response:** do not add predicates yet; observe whether structure detection requires explicit polarity metadata.

### W-004 — Duplicate relationships

SPEC-003 introduced duplicate semantic edges in two domains.

**Response:** investigate conservative relationship deduplication only when a focused need is demonstrated; do not weaken entity deduplication or merge semantically distinct edges.

### W-005 — Prompt complexity

The canonical grammar substantially increased prompt size.

**Response:** freeze vocabulary expansion for now and extract more value from the current grammar before growing instructions further.

### W-006 — Human semantic review bottleneck

Direct model cost is tiny; human review is becoming the dominant cognitive cost.

**Response:** prefer deterministic regression checks where possible, but do not replace semantic judgment with an unvalidated probabilistic judge.

### W-007 — Inference provenance model

The strict `SOURCE` vs `INFERRED` distinction remains useful. A separate supporting-evidence concept remains unproven.

### W-008 — Secret rotation

SPEC-002 exposed an API key in terminal-state output.

**Response:** keep rotation/secret-handling rule active until explicitly confirmed resolved outside repository state.

## Resolved / Improved Items

### R-001 — Relationship vocabulary drift

SPEC-003 materially improved vocabulary fit using explicit contracts plus three general predicates. Status moved from DRIFT to ALIGNED.

### R-002 — Semantic edge precision drift

The severe predicate/direction failures from SPEC-002 were substantially reduced. Status moved from DRIFT to WATCH because residual semantic errors remain.

### R-003 — Local vs remote repository state

Push-before-review has now worked across SPEC-002 and SPEC-003.

### R-004 — Installed CLI fixture path

Fixture extraction uses explicit `--fixture`; installed-wheel ambiguity is resolved.

## Drift Triggers

Mark a dimension `DRIFT` when examples such as these occur:

- implementation bypasses `KnowledgeModel`;
- provider-specific types leak into the semantic core;
- UI or structure detection re-reads source independently instead of consuming the IR;
- source-derived evidence provenance is lost;
- semantic contracts diverge between registry and prompt;
- relationship vocabulary grows without cross-domain evidence;
- schema-valid outputs are treated as semantically correct without evaluation;
- SPEC scope repeatedly expands;
- project memory becomes stale relative to implementation;
- documentation overhead materially slows learning.

## Review Cadence

After each completed SPEC/DEBRIEF pair ask:

1. Did the increment test the intended uncertainty?
2. Did scope remain bounded?
3. Does implementation match current architecture?
4. Were findings preserved?
5. Did the process reduce or create friction?
6. Did tests cover product-relevant behavior?
7. Was added complexity proportionate to learning?
8. Could a fresh context reconstruct the project?
9. What uncertainty was reduced?
10. What is now the highest-value uncertainty?

## Convergence Goal

```text
SPEC → implementation → evidence → DEBRIEF → better product/architecture decisions
SPEC → implementation → friction/results → DEBRIEF → better operating model
```

The desired result is progressively lower uncertainty, lower rework, stronger architectural alignment, and cheaper decision-relevant learning — not maximum documentation.
