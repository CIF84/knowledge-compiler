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
| Product alignment | ALIGNED | SPEC-004 tested the next architectural assumption directly: whether the semantic IR can yield useful higher-order structures. |
| Scope discipline | ALIGNED | Work stayed deterministic and downstream; no new LLM behavior, ingestion, persistence, visualization, or ontology expansion was introduced. |
| Architecture alignment | ALIGNED | `StructureDetector` consumes `KnowledgeModel` directly and produces a separate `DetectedStructureSet` without bypassing the semantic IR. |
| Memory alignment | ALIGNED | SPEC-004 now has a paired DEBRIEF and canonical project models reflect the new structure layer. |
| Process effectiveness | ALIGNED | Fourth complete repo-centered cycle succeeded; accepted SPEC-003 artifacts were reused as stable downstream evaluation inputs. |
| Test confidence | ALIGNED | Reported suite expanded to 60 offline tests; five-domain structure artifacts were reproduced byte-for-byte and 5/5 domains met expectations. |
| Complexity discipline | ALIGNED | No graph library, new provider, ontology framework, or visualization stack was added; algorithms use the standard library. |
| Reproducibility | ALIGNED | Structure detection is deterministic and accepted artifacts reproduced byte-for-byte. Fresh-thread reconstruction remains a separate watch item. |
| Repository state discipline | ALIGNED | Implementation was committed and pushed before review; canonical remote state was explicit. |
| Semantic generality | ALIGNED | The same detector operates across five unrelated domains and correctly allows domains with no composable structures. |
| Relationship vocabulary fitness | ALIGNED | SPEC-004 required no vocabulary expansion, strengthening the current freeze. |
| Semantic relationship precision | WATCH | Upstream endpoint, chronology, state, polarity, and measurement issues still affect downstream structures. |
| Source grounding | ALIGNED | Structure detection preserves relationship IDs and therefore retains the path back to grounded source evidence. |
| Structure composition | ALIGNED | Useful hierarchies, causal paths, dependency chains, chronology, and feedback candidates were detected without source re-reading. |
| Entity/event/state modeling | WATCH | SPEC-004 provides concrete evidence that weak event/state endpoints degrade process and feedback representations in several domains. |
| Duplicate relationship control | ALIGNED | Exact duplicate triples are safely collapsed for traversal while original relationship IDs remain preserved. |
| Pedagogical salience | WATCH | Some structurally valid outputs are weak learning artifacts, e.g. a one-edge classification hierarchy. Representation must distinguish existence from usefulness. |
| Prompt complexity | WATCH | SPEC-003 grammar remains large; SPEC-004 extracted downstream value without increasing it. |
| Human semantic review burden | WATCH | Offline deterministic structure evaluation reduces variance, but deciding pedagogical usefulness still requires judgment. |
| Security / secret handling | WATCH | Security rules remain active; exposed SPEC-002 key rotation is not confirmed in repository evidence. |
| Cost / effort efficiency | ALIGNED | SPEC-004 answered its question with zero model/API cost and reused accepted artifacts as fixtures. |

## Highest-Value Current Uncertainty

> Can a small set of deterministic visual/interactive representations turn `DetectedStructureSet` plus grounded `KnowledgeModel` context into a learning artifact that is materially easier to think with than the underlying text or JSON?

This should drive SPEC-005.

## Active Watch Items

### W-001 — Fresh-context reconstruction

A genuinely fresh-thread reconstruction test remains unperformed.

### W-002 — Endpoint / event / state semantics

SPEC-004 shows this is no longer merely an extraction-quality concern. Endpoint/state weaknesses can prevent expected paths from composing or make chronology/feedback structures misleading.

**Response:** carry as a known constraint into representation; redesign only when a focused experiment demonstrates the minimum needed change.

### W-003 — Polarity preservation

Current causal paths and feedback candidates do not reliably preserve positive/negative/prevention polarity.

**Response:** do not expand predicates opportunistically; observe what the first representation experiment actually needs.

### W-004 — Pedagogical salience

The detector can return technically correct but low-value structures.

**Response:** representation should select/emphasize useful structures without changing detector truth semantics.

### W-005 — Prompt complexity

The canonical grammar remains materially larger after SPEC-003.

**Response:** continue extracting value downstream before adding semantic prompt complexity.

### W-006 — Human semantic review bottleneck

Direct computation/model cost is tiny; judgment about correctness and learning usefulness is increasingly the expensive step.

**Response:** automate only deterministic checks; keep human product evaluation for representation quality until a reliable measurement method exists.

### W-007 — Inference provenance model

The strict `SOURCE` vs `INFERRED` distinction remains useful. A separate supporting-evidence concept remains unproven.

### W-008 — Secret rotation

SPEC-002 exposed an API key in terminal-state output.

**Response:** keep rotation/secret-handling rule active until explicitly confirmed resolved outside repository state.

## Resolved / Improved Items

### R-001 — Relationship vocabulary drift

Resolved in SPEC-003 and strengthened in SPEC-004: no new predicate was required for structure detection.

### R-002 — Semantic edge precision drift

Severe predicate/direction failures remain improved; residual issues remain WATCH rather than DRIFT.

### R-003 — Duplicate relationships for downstream traversal

SPEC-004 safely collapses exact duplicate triples during discovery while retaining provenance IDs.

### R-004 — Structure-detection uncertainty

Resolved positively: the current IR supports useful deterministic higher-order composition with known upstream limitations.

### R-005 — Local vs remote repository state

Push-before-review remains reliable.

## Drift Triggers

Mark a dimension `DRIFT` when examples such as these occur:

- implementation bypasses `KnowledgeModel`;
- provider-specific types leak into the semantic core;
- representation or structure detection re-reads source independently instead of consuming canonical IR/context;
- source-derived evidence provenance is lost;
- detector invents missing links or treats generic connectivity as semantics;
- weak/empty structures are hidden or repaired solely for presentation completeness;
- relationship vocabulary grows without cross-domain evidence;
- structurally valid output is treated as automatically pedagogically useful;
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
