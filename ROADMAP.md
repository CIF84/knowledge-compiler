# Knowledge Compiler — Roadmap

This roadmap is organized around risk reduction, not feature accumulation. It records what the repository has demonstrated, what its evaluations rejected or left unresolved, and which question should be answered next.

## North star

> **Paste difficult text. Get a model you can think with.**

The project thesis remains:

> Compile source-grounded information into a navigable, multi-resolution knowledge space whose cognitive projection can adapt to how the learner wants to think.

## Product architecture now established

The project has converged on four distinct responsibilities:

```text
SEMANTIC COMPILER
What is justified?
        ↓
trusted semantic model
        ↓
REPRESENTATION ENGINE
How should this structure be expressed?
        ↓
NAVIGATION ENGINE
Where is this in the larger knowledge space?
        ↓
SYNCHRONIZED WORKSPACE
Move and understand without losing context
```

Personalization belongs above truthful representation availability, not inside semantic truth.

## Interface milestone — BASELINE-003

SPEC-019 produced the strongest owner-approved integrated interface result to date and is accepted as `HYBRID_WORKSPACE_BETTER`.

The preferred product workspace now contains two synchronized cognitive surfaces:

```text
WHERE AM I?                       WHAT DOES THIS MEAN?
continuous navigation             focused learning representation
pan / zoom / orient               structure / relationships / evidence
```

The owner verdict was explicit: “this is it” and “I wouldn't change a thing now.”

Therefore foundational workspace invention is considered solved enough until contradictory evidence appears.

Three references must remain independently preserved:

- `BASELINE-001` — what good looks like for focused learning / explanatory representation;
- `BASELINE-002` — what good looks like for continuous spatial navigation;
- `BASELINE-003` — preferred integrated navigation + learning workspace.

Future UI-affecting work must declare which BASELINE-003 invariant it intentionally changes. Do not perform speculative shell polish.

## Status vocabulary

- **Implemented** means the behavior exists and is covered by repository tests.
- **Evaluated** means committed machine or human evidence exercises the behavior.
- **Accepted** means the relevant SPEC handoff or debrief accepted the result, including mixed or negative results.
- **Future** means product direction only; it must not be presented as current capability.

## Completed semantic and compiler foundation

SPEC-001 through SPEC-015 established the semantic compiler and realistic-source reliability boundary.

| Increment | Capability / finding | Accepted outcome |
| --- | --- | --- |
| SPEC-001 | Plain text → validated `KnowledgeModel` | Grounded entities, relationships, claims, evidence, confidence, serialization. |
| SPEC-002 | Live semantic extraction | Golden-domain extraction with failures/retries preserved. |
| SPEC-003 | Canonical relationship semantics | Expanded predicate vocabulary and regression review. |
| SPEC-004 | Higher-order structure detection | Hierarchy, causal, dependency, process, feedback-candidate detection. |
| SPEC-005 | Representation compiler | Deterministic inspectable semantic projections. |
| SPEC-006 / 006A | Structure-aware interaction baseline | Strong focused learning representation and accepted visual interaction grammar. |
| SPEC-007 | Contextual semantic navigation | Preferred contextual expansion concept; Explore/Back navigation rejected as inelegant. |
| SPEC-008 | One-level automatic resolution | One useful real child; insufficiency fails closed. |
| SPEC-009 | Resolution strategies | Process-stage strategy useful; other strategies mixed/weak. |
| SPEC-010 | Structured propositions | Comparison conditions and transfer events fix concrete lossy binary semantics. |
| SPEC-011 | Realistic quantum source | Full-source extraction failed closed twice; realistic-source semantic reliability exposed as bottleneck. |
| SPEC-012 | Staged symbol/link compilation | Dangling-reference problem improved; semantic/grounding reliability still insufficient. |
| SPEC-013 | Assertion-first compilation | `ASSERTION_FIRST_BETTER`; grounded assertions preserve meaning while graph admission becomes conservative and precise. |
| SPEC-014 | Independent semantic gate | `GATE_BETTER`; narrow admission review catches most known bad candidates cheaply. |
| SPEC-015 | Semantic compression judge | `COMPRESSION_JUDGE_BETTER`; all known lossy compressions rejected with one conservative false rejection. |

The important semantic lesson is now stable: realistic-source reliability benefits from separating grounded assertions from canonical graph admission and using narrow discriminators rather than broad multi-agent deliberation.

## Completed learner-facing interface exploration

| Increment | Question | Human outcome |
| --- | --- | --- |
| SPEC-016 | Can trustworthy assertions become the orientation surface? | `NO_MEANINGFUL_IMPROVEMENT`; text-rich cognitive overload. |
| SPEC-017 | Can presentation-only topology replace text overload? | `NO_MEANINGFUL_IMPROVEMENT`; semantic trajectories became unclear. |
| SPEC-018 | Can the graph become a continuous navigable world? | `MIXED`; movement primitive strongly validated but baseline interaction quality regressed. |
| OPS-002 | Restore SPEC-006 clarity around continuous navigation | Navigation quality became strong enough to freeze independently as BASELINE-002. |
| SPEC-019 | Can navigation and focused learning coexist? | `HYBRID_WORKSPACE_BETTER`; owner considered the result essentially complete at the foundational UI level. |

Subsequent increments preserved the accepted workspace while testing realistic depth and interaction semantics:

| Increment | Capability / finding | Outcome |
| --- | --- | --- |
| SPEC-020–021 | Realistic semantic depth and focus-preserving explanation | Useful semantic payload work; one attempted viewer failed the BASELINE-003 preservation gate and was restored before further evaluation. |
| SPEC-022 | Learner navigation grammar | `NAVIGATION_GRAMMAR_BETTER`; exact executable promoted to BASELINE-004. |
| SPEC-023–031 | Depth, recursive interaction, atomic context, focused learning, reciprocal/multi-edge identity | Deterministic interaction seams established while preserving trusted semantics and frozen baselines. |
| SPEC-032 | Visible learning-history navigation | Rejected: duplicated territory, exhausted horizontal space, broke label legibility, and eventually froze after deeper exploration. |
| SPEC-033 | Canonical revealed-knowledge tree | Implemented candidate awaiting owner review; not promoted. |

## Current semantic boundary

### Binary relationship vocabulary

```text
IS_A              PART_OF            CAUSES
INCREASES         DECREASES           ENABLES
REQUIRES          CONSTRAINS          PRECEDES
TRANSFORMS_INTO   INTERACTS_WITH      MEASURED_BY
EXAMPLE_OF        CONTRADICTS         CREATES
INDUCES           EXERTS_FORCE_ON     AFFECTS
BINDS_TO          TRANSFERS_TO
```

### Detected structures

```text
HIERARCHY
CAUSAL_PATH
PROCESS_CHAIN
DEPENDENCY_CHAIN
FEEDBACK_CANDIDATE
```

### Structured propositions

Binary relationships remain the default. Structured propositions are used only when truth requires multiple participants or explicit roles.

```text
types:     COMPARISON_CONDITION, TRANSFER_EVENT
roles:     LEFT_OPERAND, RIGHT_OPERAND, OUTCOME,
           EVENT, OBJECT, DESTINATION
operator:  GREATER_THAN
```

## Product principles earned by evidence

1. **Truth before fluency.** Do not trade grounding or semantic validation for a smoother demo.
2. **Structure before presentation.** Extract, classify, detect, select, then render.
3. **The appropriate representation depends upon the information structure.** Do not flatten all knowledge into one generic graph.
4. **Navigation and representation are different jobs.** The map answers “where am I?”; the learning surface answers “what does this mean?”
5. **Personalization changes projection, not truth.** Rank truthful representations differently for different learners without changing semantics.
6. **Progressive disclosure over graph density.** More visible information is not automatically more understanding.
7. **Failures are artifacts.** Preserve insufficiency, retries, mixed comparisons, usage, and reviewer decisions.
8. **Freeze validated dimensions.** Once a dimension has a strongly preferred baseline, hold it constant while testing another dimension.
9. **Spaces mirror actions.** Prefer spatial/interaction architecture that makes the cognitive job obvious without instructional chrome.
10. **One semantic core.** Views and future product surfaces compile from the same grounded model.

## Current accepted limitations

1. Realistic-source semantic reliability has improved substantially but is not broadly validated across domains.
2. Assertion-first compilation is validated on one realistic quantum benchmark, not general source classes.
3. Narrow semantic gates/compression judges are promising but are not yet production-integrated.
4. Automatic semantic resolution remains only partly validated and has not yet been reintegrated into BASELINE-003.
5. Representation selection exists structurally but has not been evaluated as a personalized learner-facing decision system.
6. Personalization is architectural direction only; no learner model exists.
7. Guided learning paths / course journeys have not been implemented; traversal history is explicitly not visible navigation topology.
8. The end-to-end user workflow from arbitrary source ingestion to the BASELINE-003 workspace is not yet a polished product.
9. Learning impact—retention, transfer, explanation quality, calibration—remains unevaluated.

## Current decision frontier

The immediate gate is owner review of SPEC-033:

> Does a canonical, deduplicated, collapsible map of revealed knowledge feel like territory rather than click history, remain legible at materially larger scale, and stay interactive through repeated depth changes?

Hold constant canonical semantic truth, provenance, fail-closed behavior, BASELINE-004, focused-learning role separation, reciprocal/multi-edge identity, and admitted source-bounded depth.

If accepted, later experiments may attach learner understanding state or recommend pathways through the same topology. Neither may redefine the revealed map:

```text
knowledge topology ≠ revealed subset ≠ learner understanding
revealed subset ≠ traversal history ≠ recommended pathway
```

## Later candidates, contingent on evidence

1. **Representation-personalization evaluation** — compare system/causal, hierarchy, process, dependency, and other truthful projections across learner preferences/tasks.
2. **Guided pathway mode** — a recommendation should act as coordinates through the same knowledge world and must not replace or restructure the revealed map.
3. **Learning evaluation** — compare source, conventional summary, and Knowledge Compiler on orientation, explanation, transfer, recall, and confidence calibration.
4. **Qualitative simulator** — counterfactual exploration only where direction, assumptions, and source/inference boundaries remain explicit.
5. **Additional source adapters** — web/PDF/transcript ingestion only after the plain-text semantic pipeline is sufficiently reliable.
6. **Personal learning state** — attach understanding/calibration evidence to canonical concepts and relationships without equating visibility with mastery.
7. **Productization** — input shell, persistence, history telemetry, export/share, and other workflow infrastructure after the core transformation earns expansion.

## Current non-goals

- redesigning BASELINE-003 without observed evidence;
- building a generic knowledge-graph platform;
- treating the continuous map as the universal representation;
- using visit history as visible knowledge topology;
- ingesting every content format prematurely;
- inventing unsupported detail to satisfy requested depth;
- broad multi-agent semantic deliberation where narrow discriminators suffice;
- personalization that changes semantic truth;
- 3D representation except for inherently spatial/physical subject matter.

## Decision records

- [OPERATING_MODEL.md](OPERATING_MODEL.md) defines how work moves from contract to evidence and handoff.
- [ARCHITECTURE.md](ARCHITECTURE.md) documents implemented technical boundaries.
- [PROJECT_MEMORY.md](PROJECT_MEMORY.md) preserves durable constraints and accepted outcomes.
- [BASELINE-001](baselines/BASELINE-001-interface.md) preserves focused-learning interaction quality.
- [BASELINE-002](baselines/BASELINE-002-continuous-navigation-reference.md) preserves continuous-navigation quality.
- [BASELINE-003](baselines/BASELINE-003-hybrid-learning-workspace.md) is the preferred integrated UI baseline.
- [DEBRIEF-019](debriefs/DEBRIEF-019-navigation-learning-workspace.md) records the decisive owner review and accepted hybrid-workspace result.
