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
| Product alignment | ALIGNED | SPEC-007/008 moved the product toward the core “peel layers while preserving context” thesis; owner reaction remained strongly positive. |
| Scope discipline | ALIGNED | SPEC-008 kept automatic resolution to one level, two focuses, no recursion, no retrieval, no personalization, and no frontend rewrite. |
| Architecture alignment | ALIGNED | Parent `KnowledgeModel` remains immutable; child semantic truth is independent; navigation stays outside semantic IR. |
| Memory alignment | ALIGNED | SPEC-007 and SPEC-008 now have paired debriefs and canonical project models reflect semantic navigation and multi-resolution compilation. |
| Process effectiveness | ALIGNED | Handcrafted interaction first, automation second, live validation third produced clear architectural learning with bounded cost. |
| Test confidence | ALIGNED | SPEC-008 reported 115 passing tests; live artifacts and fail-closed behavior are preserved separately. |
| Complexity discipline | ALIGNED | No recursive graph architecture, graph DB, frontend framework, new runtime dependency, retrieval system, or personalization machinery was added. |
| Reproducibility | ALIGNED | Offline fixtures and deterministic downstream artifacts remain reproducible; live provider results are preserved as committed evidence. |
| Repository state discipline | ALIGNED | Implementation, live evaluation, and debrief/canonical model updates are committed to canonical GitHub. |
| Semantic generality | WATCH | Automatic depth has one real success and one grounding rejection; cross-domain reliability is not established. |
| Relationship vocabulary fitness | ALIGNED | SPEC-008 required zero new predicates. |
| Semantic relationship precision | WATCH | Existing endpoint/state/polarity limitations remain; child generation may amplify them at deeper resolution. |
| Source grounding | ALIGNED | Economics generated 11/11 source relationships and 4/4 source claims with validated evidence; Software Architecture failed closed rather than weakening provenance. |
| Structure composition | ALIGNED | Generated child truth can flow through existing `StructureDetector` and `RepresentationBuilder`. |
| Representation usefulness | ALIGNED | Owner judged the generated Economics layer as genuinely matching expected deeper exploration rather than merely technically impressive. |
| Interaction coherence | ALIGNED | Existing Contextual mode remains coherent for generated child models. |
| Spatial layout | ALIGNED | Current 2D structure-aware layout remains suitable for the generated Economics child at benchmark scale. |
| Cognitive presets | WATCH | Overview / Focus / Contextual are promising distinct cognitive projections, but broader-user value and product naming remain unvalidated. |
| Semantic navigation | ALIGNED | Contextual/layered navigation is validated conceptually for the owner benchmark. |
| Multi-resolution compilation | WATCH | Demonstrated in Economics, rejected in Software Architecture; reliability and resolution strategy remain open. |
| Resolution semantics | WATCH | “Zoom in” is now understood as explanatory refinement, but strategy by semantic object type is not yet operationalized. |
| Context-map navigation | WATCH | Parent context naturally wants to become an active lateral navigation map; not yet implemented or tested. |
| Recursive/on-demand compilation | WATCH | On-demand local compilation is a strong hypothesis; eager recursion remains explicitly unjustified. |
| 2D vs 3D knowledge navigation | ALIGNED | Default abstract knowledge surface should be 2D + semantic zoom; literal 3D reserved for domains where spatial depth itself carries meaning. |
| Layout scale | WATCH | Custom deterministic layout is still validated only for small benchmark graphs. |
| Human review burden | WATCH | Human judgment remains decisive for compression relationship and cognitive usefulness. |
| Broader-user generalization | WATCH | Strong evidence remains owner-based. Hyper-personalization is promising but not yet tested. |
| Security / secret handling | ALIGNED | Old key was rotated and new key handled via environment variable; source transmission required explicit approval. |
| Cost / effort efficiency | ALIGNED | Live SPEC-008 used 8,831 tokens total and produced high-value architectural evidence without broadening scope. |
| Spec integrity | WATCH | SPEC-008 was accidentally truncated at `Report explicitly:`; implementation still succeeded but spec-writing reliability needs attention. |

## Highest-Value Current Uncertainty

> What should “zoom in” mean for different semantic object types, and can Knowledge Compiler apply the right resolution strategy while preserving source grounding and a coherent parent-child compression relationship?

This should drive SPEC-009.

## Active Watch Items

### W-001 — Fresh-context reconstruction
A genuinely fresh-thread reconstruction test remains unperformed.

### W-002 — Endpoint / event / state semantics
Known endpoint/state weaknesses may become more consequential at deeper semantic resolution.

**Response:** revisit only when a focused resolution experiment shows they are a hard blocker.

### W-003 — Polarity preservation
Current causal structures do not reliably encode reinforcing/balancing or prevention polarity.

### W-004 — Layout scale
Current custom layout is strong for small graphs but unproven at larger scales.

### W-005 — Resolution-strategy generality
One generic deeper-resolution prompt produced one success and one rejected output.

**Response:** test a small set of semantic-role-aware resolution strategies before recursion or active map navigation.

### W-006 — Context-map navigation
The parent mini-map currently orients but does not support lateral movement.

**Response:** preserve as next navigation hypothesis; do not implement before resolution semantics are better understood.

### W-007 — On-demand compilation
Recursive eager generation risks combinatorial explosion.

**Response:** maintain one-level generation until an explicit on-demand compilation experiment is warranted.

### W-008 — Cognitive presets / personalization
Overview, Focus, and Contextual may support different learner/task intents.

**Response:** preserve successful modes but do not build adaptive personalization yet.

### W-009 — Human review bottleneck
Compression relationship and cognitive usefulness still need human judgment.

### W-010 — Broader-user generalization
Current strong product evidence is owner-based.

### W-011 — Spec truncation
SPEC-008 ended abruptly because of an authoring/write failure.

**Response:** verify future specs contain a complete acceptance and required-handoff section before implementation handoff.

## Resolved / Improved Items

### R-001 — Relationship vocabulary drift
Resolved; downstream semantic-depth work still requires no vocabulary growth.

### R-002 — Structure-detection uncertainty
Resolved positively in SPEC-004.

### R-003 — Minimal representation uncertainty
Resolved positively in SPEC-005.

### R-004 — Interaction coherence
Resolved positively in SPEC-006.

### R-005 — Spatial-layout uncertainty
Resolved positively at current graph scale in SPEC-006.

### R-006 — Semantic navigation usefulness
Resolved positively for the owner benchmark in SPEC-007: Contextual/Layers is the preferred conceptual mode.

### R-007 — Automatic depth possibility
Resolved positively but narrowly in SPEC-008: one real source-grounded automatic child model was successfully compiled and rendered.

### R-008 — Fail-closed child grounding
Demonstrated in SPEC-008 Software Architecture run.

## Drift Triggers

Mark a dimension `DRIFT` when examples such as these occur:

- implementation bypasses `KnowledgeModel`;
- provider-specific types leak into semantic truth models;
- generated child content cannot be independently inspected before rendering;
- provenance is weakened to improve success rate;
- viewer/navigation state mutates parent or child semantic truth;
- recursive depth is added before resolution semantics are understood;
- active context-map navigation invents semantic adjacency unsupported by the model;
- cognitive presets silently alter canonical facts/provenance;
- generic 3D visualization is introduced without subject-matter dimensional meaning;
- eager generation creates complexity before on-demand behavior is justified;
- project memory becomes stale;
- documentation/spec truncation goes unnoticed before implementation.

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
11. If probabilistic generation was involved, did the trust boundary fail closed correctly?
12. If a semantic-depth artifact was generated, does the parent plausibly compress/summarize the child?
13. If BASELINE-001 is relevant, is the change BETTER / SAME / WORSE on the claimed cognitive dimension?
14. Was the SPEC file itself complete before handoff?

## Convergence Goal

```text
SPEC → implementation → evidence → DEBRIEF → better product/architecture decisions
SPEC → implementation → friction/results → DEBRIEF → better operating model
```

The desired result is progressively lower uncertainty, lower rework, stronger architectural alignment, and cheaper decision-relevant learning — not maximum documentation.
