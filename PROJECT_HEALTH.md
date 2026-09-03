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
| Product alignment | ALIGNED | SPEC-005 tested the original product promise directly; the owner reported immediate cognitive improvement and a clear preference to learn with the representation available. |
| Scope discipline | ALIGNED | Representation work stayed downstream; no extraction, ontology, structure-repair, persistence, simulation, or product-platform expansion occurred. |
| Architecture alignment | ALIGNED | `RepresentationBuilder` consumes `KnowledgeModel` + `DetectedStructureSet` and produces a separate deterministic `RepresentationModel`. |
| Memory alignment | ALIGNED | SPEC-005 has a paired DEBRIEF and canonical project models reflect the representation layer and human findings. |
| Process effectiveness | ALIGNED | Fifth repo-centered cycle succeeded and added direct owner interaction after repository verification for a UI-bearing increment. |
| Test confidence | ALIGNED | Reported suite expanded to 75 offline tests; deterministic representation regeneration and provenance integrity passed across all five domains. |
| Complexity discipline | ALIGNED | Viewer uses zero runtime dependencies beyond standard-library serving; no frontend framework or general graph platform was introduced. |
| Reproducibility | ALIGNED | Representation artifacts are deterministic and reported byte-for-byte reproducible. Fresh-thread reconstruction remains a separate watch item. |
| Repository state discipline | ALIGNED | Implementation was committed and pushed before review; canonical remote state was explicit. |
| Semantic generality | ALIGNED | The same representation layer handles five unrelated domains and preserves truthful empty output for biology. |
| Relationship vocabulary fitness | ALIGNED | SPEC-005 required no vocabulary expansion, strengthening the freeze. |
| Semantic relationship precision | WATCH | Upstream endpoint, chronology, state, polarity, and measurement issues remain visible in rendered output. |
| Source grounding | ALIGNED | Learner-visible edges retain complete provenance to validated source evidence. |
| Structure composition | ALIGNED | Existing deterministic structures map cleanly into presentation models without source reinterpretation. |
| Representation usefulness | ALIGNED | First direct owner evaluation was strongly positive: improved orientation, engagement, and preference to learn with the tool. Evidence remains single-user qualitative. |
| Representation integrity | ALIGNED | All five committed domain artifacts report valid references, preserved semantics, exact evidence copying, and complete provenance. |
| Interaction coherence | WATCH | Selecting an edge does not yet persistently synchronize highlighting across graph edge, relationship control, detail, and evidence surfaces. |
| Spatial layout | WATCH | Current placement is functional but not sufficiently structure-aware; long diagonals/uneven geometry add avoidable interpretation work. |
| Entity/event/state modeling | WATCH | Rendering makes existing event/state endpoint limitations more obvious, but they do not yet block useful representation generally. |
| Duplicate relationship control | ALIGNED | Duplicate support relationships remain collapsed for presentation while retaining provenance. |
| Pedagogical salience | ALIGNED | Simple PRIMARY/SECONDARY/SPARSE handling prevents trivial one-edge structures from dominating and preserves explicit empty states. It remains coarse. |
| Prompt complexity | WATCH | SPEC-003 grammar remains large; SPEC-005 added downstream value without increasing it. |
| Human review burden | WATCH | Product usefulness now genuinely requires interaction-based review; focused owner evaluation worked, but broader measurement remains unproven. |
| Security / secret handling | WATCH | Security rules remain active; exposed SPEC-002 key rotation is not confirmed in repository evidence. |
| Cost / effort efficiency | ALIGNED | SPEC-005 reused accepted upstream artifacts and required no model/API cost; direct human review quickly exposed the next constraints. |

## Highest-Value Current Uncertainty

> Can structure-aware deterministic layout plus synchronized semantic selection make the existing representations materially easier to parse and manipulate as coherent mental models, without adding semantic inference or general frontend complexity?

This should drive SPEC-006.

## Active Watch Items

### W-001 — Fresh-context reconstruction

A genuinely fresh-thread reconstruction test remains unperformed.

### W-002 — Endpoint / event / state semantics

Rendering strengthens evidence that endpoint/state weaknesses degrade process and feedback representations.

**Response:** keep defects visible and attributed upstream; do not redesign semantic IR until representation work shows they materially block learning value.

### W-003 — Polarity preservation

Current causal paths and feedback candidates do not reliably preserve positive/negative/prevention polarity.

**Response:** do not expand predicates opportunistically; feedback remains explicitly a candidate.

### W-004 — Interaction coherence

The same relationship appears as graph edge, relationship control, detail, and evidence, but selection state is not yet synchronized across all surfaces.

**Response:** test shared semantic selection with click-to-select and hover-to-preview behavior in SPEC-006.

### W-005 — Spatial layout

Current graph geometry is functional but not in sufficient visual harmony with the semantic structures.

**Response:** test structure-specific deterministic layout grammars before broader progressive disclosure or UI polish.

### W-006 — Prompt complexity

The canonical grammar remains materially larger after SPEC-003.

**Response:** continue extracting value downstream before adding semantic prompt complexity.

### W-007 — Human review bottleneck

Direct human interaction now provides product evidence that deterministic tests cannot.

**Response:** keep reviews focused on one product uncertainty and use fixed artifacts to minimize review burden.

### W-008 — Inference provenance model

The strict `SOURCE` vs `INFERRED` distinction remains useful. A separate supporting-evidence concept remains unproven.

### W-009 — Secret rotation

SPEC-002 exposed an API key in terminal-state output.

**Response:** keep rotation/secret-handling rule active until explicitly confirmed resolved outside repository state.

## Resolved / Improved Items

### R-001 — Relationship vocabulary drift

Resolved in SPEC-003 and strengthened through SPEC-005: downstream structure and representation required no new predicates.

### R-002 — Semantic edge precision drift

Severe predicate/direction failures remain improved; residual upstream issues remain WATCH rather than DRIFT.

### R-003 — Duplicate relationships for downstream traversal/presentation

Exact duplicate triples can be collapsed while preserving all provenance IDs/evidence.

### R-004 — Structure-detection uncertainty

Resolved positively in SPEC-004: the current IR supports useful deterministic higher-order composition.

### R-005 — Minimal representation uncertainty

Resolved positively for the owner benchmark: deterministic interactive representations can materially improve cognitive orientation and are preferred as a learning aid.

### R-006 — Pedagogical salience baseline

Improved in SPEC-005: coarse deterministic salience plus explicit sparse/empty states is sufficient for the current benchmark.

### R-007 — Local vs remote repository state

Push-before-review remains reliable.

## Drift Triggers

Mark a dimension `DRIFT` when examples such as these occur:

- implementation bypasses `KnowledgeModel`;
- provider-specific types leak into the semantic core;
- representation or structure detection re-reads source independently instead of consuming canonical IR/context;
- source-derived evidence provenance is lost;
- detector or representation invents missing links solely for presentation completeness;
- weak/empty structures are hidden or repaired;
- relationship vocabulary grows without cross-domain evidence;
- structurally valid output is treated as automatically pedagogically useful;
- viewer interactions silently mutate canonical semantic truth;
- generic graph aesthetics are prioritized over structure-specific cognitive legibility;
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

For UI-bearing experiments also ask:

11. Did a human actually interact with the artifact before acceptance?
12. Did the interaction reveal a semantic, spatial, or behavioral problem that repository inspection could not?

## Convergence Goal

```text
SPEC → implementation → evidence → DEBRIEF → better product/architecture decisions
SPEC → implementation → friction/results → DEBRIEF → better operating model
```

The desired result is progressively lower uncertainty, lower rework, stronger architectural alignment, and cheaper decision-relevant learning — not maximum documentation.
