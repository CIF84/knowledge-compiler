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
| Product alignment | ALIGNED | SPEC-006 produced the strongest owner result so far: materially better than SPEC-005 with a very strong positive learning/cognitive response. |
| Scope discipline | ALIGNED | SPEC-006 held semantics fixed and changed only layout/interaction; SPEC-006A fixed one focus artifact and captured a baseline without opportunistic polish. |
| Architecture alignment | ALIGNED | Layout remains presentation-only and viewer interaction does not mutate semantic truth. |
| Memory alignment | ALIGNED | SPEC-006 has a paired DEBRIEF and canonical models now reflect the validated layout/interaction behavior and BASELINE-001. |
| Process effectiveness | ALIGNED | Fixed upstream artifacts enabled a clean before/after product experiment and direct human review identified the decisive result. |
| Test confidence | ALIGNED | SPEC-006 reported 88 passing tests; SPEC-006A reported 91. Deterministic layout/identity/provenance checks remain intact. |
| Complexity discipline | ALIGNED | No graph library, frontend framework, build pipeline, screenshot framework, or new runtime dependency was added. |
| Reproducibility | ALIGNED | Layout generation remains deterministic and evaluation artifacts are committed. Fresh-thread reconstruction remains a separate watch item. |
| Repository state discipline | ALIGNED | Implementation, focus fix, baseline, and project-memory updates were committed to canonical GitHub. |
| Semantic generality | ALIGNED | The same representation/layout system handles all five domains while preserving Biology's truthful empty state. |
| Relationship vocabulary fitness | ALIGNED | Layout/interaction work required no ontology expansion. |
| Semantic relationship precision | WATCH | Upstream endpoint, chronology, state, polarity, and measurement issues still constrain some representations. |
| Source grounding | ALIGNED | Provenance remains first-class and learner-visible after layout and interaction changes. |
| Structure composition | ALIGNED | Higher-order structures remain cleanly separated from presentation behavior. |
| Representation usefulness | ALIGNED | Owner before/after verdict strongly favors SPEC-006. |
| Representation integrity | ALIGNED | Semantic content, canonical direction, relationship identity, and provenance remained unchanged through SPEC-006/006A. |
| Interaction coherence | ALIGNED | Persistent selection and temporary preview now synchronize graph/control/detail/evidence as one semantic object. |
| Spatial layout | ALIGNED | Structure-specific layout materially improved legibility on current benchmark graphs. |
| Interface baseline | ALIGNED | `BASELINE-001` preserves the first empirically successful cognitive interaction grammar for future comparisons. |
| Accessibility interaction | ALIGNED | Default SVG focus noise was replaced with an intentional `:focus-visible` treatment while preserving keyboard activation. |
| Layout scale | WATCH | Current custom deterministic layout is validated only for small benchmark graphs. |
| Entity/event/state modeling | WATCH | Known upstream state/event endpoint limitations remain visible, especially in electromagnetism, biology, and history. |
| Pedagogical salience | ALIGNED | Existing simple salience plus truthful sparse/empty states remains adequate at current scale. |
| Prompt complexity | WATCH | SPEC-003 grammar remains large; subsequent product value has been added without increasing it. |
| Human review burden | WATCH | Human product review remains decisive for cognitive usefulness; broader-user evidence is still absent. |
| Security / secret handling | WATCH | Security rules remain active; exposed SPEC-002 key rotation is not confirmed in repository evidence. |
| Cost / effort efficiency | ALIGNED | SPEC-006/006A used fixed local artifacts and zero model/API cost to produce major product learning. |

## Highest-Value Current Uncertainty

> Can a learner move from a high-level model into progressively deeper explanations, mechanisms, and evidence without losing orientation in the larger system?

This is the leading candidate for SPEC-007.

## Active Watch Items

### W-001 — Fresh-context reconstruction
A genuinely fresh-thread reconstruction test remains unperformed.

### W-002 — Endpoint / event / state semantics
Known endpoint/state weaknesses degrade some process and feedback representations.

**Response:** preserve attribution upstream; revisit when progressive disclosure or richer structures are materially blocked.

### W-003 — Polarity preservation
Current causal paths and feedback candidates do not reliably encode reinforcing/balancing or prevention polarity.

**Response:** do not expand predicates opportunistically.

### W-004 — Layout scale
The custom deterministic layout is excellent for current benchmark sizes but not proven on materially larger graphs.

**Response:** continue until scale produces a concrete failure before adopting a general graph-layout dependency.

### W-005 — Progressive disclosure / orientation
The current interface is strong at one representation level. It is unknown whether deeper explanations/submodels can be exposed without losing the learner's place in the larger system.

**Response:** candidate SPEC-007 should test semantic navigation against BASELINE-001 rather than broadly expanding UI.

### W-006 — Prompt complexity
The canonical relationship grammar remains materially larger after SPEC-003.

### W-007 — Human review bottleneck
Direct interaction provides evidence machine metrics cannot.

**Response:** keep product experiments narrow and compare against fixed baselines.

### W-008 — Broader-user generalization
Strong usefulness evidence is owner-based.

**Response:** do not build formal research infrastructure yet; first establish a stronger product surface and repeatable tasks.

### W-009 — Secret rotation
SPEC-002 exposed an API key in terminal-state output.

## Resolved / Improved Items

### R-001 — Relationship vocabulary drift
Resolved; downstream experiments continue without vocabulary growth.

### R-002 — Structure-detection uncertainty
Resolved positively in SPEC-004.

### R-003 — Minimal representation uncertainty
Resolved positively in SPEC-005.

### R-004 — Interaction coherence
Resolved positively in SPEC-006: semantic selection is synchronized across surfaces.

### R-005 — Spatial-layout uncertainty
Resolved positively at current graph scale in SPEC-006.

### R-006 — SVG focus artifact
Resolved in SPEC-006A while preserving keyboard accessibility.

### R-007 — Successful UI reference point
Resolved by capturing BASELINE-001 rather than relying on memory/screenshots in conversation history.

## Drift Triggers

Mark a dimension `DRIFT` when examples such as these occur:

- implementation bypasses `KnowledgeModel`;
- provider-specific types leak into the semantic core;
- representation re-reads source independently instead of consuming canonical context;
- provenance is lost;
- missing links are invented for presentation completeness;
- weak/empty structures are hidden;
- relationship vocabulary grows without evidence;
- viewer interactions mutate canonical semantic truth;
- generic visual polish makes cognitive behavior worse than BASELINE-001 without an explicit worthwhile trade-off;
- progressive disclosure causes the learner to lose orientation without addressing that cost;
- heavy frontend/graph infrastructure is introduced before current simple architecture demonstrably fails;
- project memory becomes stale;
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
11. For UI-bearing experiments, did a human actually interact with the artifact?
12. If BASELINE-001 is relevant, is the change BETTER / SAME / WORSE on the dimensions it claims to improve?

## Convergence Goal

```text
SPEC → implementation → evidence → DEBRIEF → better product/architecture decisions
SPEC → implementation → friction/results → DEBRIEF → better operating model
```

The desired result is progressively lower uncertainty, lower rework, stronger architectural alignment, and cheaper decision-relevant learning — not maximum documentation.
