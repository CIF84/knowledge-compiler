# DEBRIEF-009 — Semantic Resolution Strategy

## Status

Accepted — `MIXED_BY_ROLE`.

SPEC-009 provides positive evidence that semantic zoom should depend on the semantic role/nature of the focus concept, but does not validate the current strategy set as a general ontology of resolution behavior.

## Implementation

Implementation commit:

```text
71da114
```

Final live-evaluation commit:

```text
3fd8a4aabde960b8abfb5bd4e31506752fd1db86
```

## Primary Question

> Does semantic-role-aware resolution guidance produce meaningfully better semantic zoom than a generic deeper-detail compiler?

## Outcome

**Mixed by semantic role.**

The six-call controlled live matrix produced:

| Focus | Strategy | Outcome |
| --- | --- | --- |
| market price | Generic | SUCCESS |
| market price | Variable causal neighborhood | INSUFFICIENT_SOURCE_DETAIL / detail-gain rejection |
| order-processing workflow | Generic | GROUNDING_FAILURE |
| order-processing workflow | Process stages | SUCCESS |
| API component | Generic | GROUNDING_FAILURE |
| API component | Component internals | INSUFFICIENT_SOURCE_DETAIL |

No retries, hidden repairs, prompt iterations, cherry-picking, or external enrichment were used.

## Human Review

The owner directly inspected the successful `PROCESS_STAGES` child in Contextual/Layers mode.

Verdict:

> **PASS.**

The transformation from a higher-level `order-processing workflow` concept into a chronological sequence of process stages felt like the correct kind of semantic zoom.

The owner separately noted that the current `Explore` / `Back` button navigation is not elegant or intuitive. This does not invalidate the resolution strategy; it reinforces the already emerging map-navigation hypothesis.

## Strategy Findings

### PROCESS_STAGES — positive evidence

The strategy produced the intended stage-oriented representation where Generic failed grounding.

The deeper model exposed chronological internal progression such as:

```text
API order-request acceptance
        ↓ PRECEDES
payload parsing
        ↓ PRECEDES
required-field validation
        ↓
...
```

The owner judged **process → stages** to be a natural semantic-resolution transformation.

This is the strongest positive finding of SPEC-009.

### COMPONENT_INTERNALS — safe refusal, not positive usefulness evidence

The accepted Software Architecture source established the existence and role of an API component but did not support trustworthy internal decomposition.

`COMPONENT_INTERNALS` returned `INSUFFICIENT_SOURCE_DETAIL` rather than inventing internals.

This is positive evidence for source honesty and strategy-specific restraint, but it does not establish that `COMPONENT_INTERNALS` is useful when sufficient source detail exists.

### VARIABLE_CAUSAL_NEIGHBORHOOD — not validated

The type-aware Economics proposal did not outperform Generic. Although focus relevance, structure, grounding, and parent coherence passed, it failed the existing mechanistic-detail-gain gate.

The accepted SPEC-008 Economics child remains stronger than the new SPEC-009 Generic control.

Do not generalize `VARIABLE_CAUSAL_NEIGHBORHOOD` as the correct universal zoom strategy for variables from this experiment.

### GENERIC_DETAIL — useful control, inconsistent behavior

Generic succeeded for Economics but failed grounding on Process and Component benchmarks.

Generic remains useful as an experimental control but should not be treated as a robust semantic-resolution policy.

## Critical Semantic Finding

Independent semantic review found endpoint-role defects in both machine-accepted children despite:

- exact quote grounding;
- valid SourceSpan coordinates;
- canonical predicates;
- mechanically valid direction;
- source-grounded provenance.

This demonstrates a major distinction:

```text
GROUNDING CORRECTNESS
        ≠
PROPOSITION CORRECTNESS
```

### Economics defect

The source describes a compound condition roughly equivalent to:

```text
quantity demanded > quantity supplied
        ↓
     shortage
```

The generated graph reduces this to something closer to:

```text
quantity demanded
        ↓ CAUSES
     shortage
```

The quote may be exact and the edge direction mechanically valid, yet the proposition represented by the edge is semantically incomplete/wrong.

### Process defect

The process child uses an order-command-transfer process as the destination of `TRANSFERS_TO` rather than the order component itself.

This confuses:

```text
TRANSFER EVENT / PROCESS
```

with:

```text
TRANSFER DESTINATION
```

Again, grounding alone cannot detect this.

## Architectural Implication

The existing semantic IR is strongest when knowledge can be represented as:

```text
entity ─predicate→ entity
```

SPEC-009 provides concrete evidence that some important propositions require richer semantic roles, for example:

```text
COMPOUND CONDITION(A, B)
        ↓ causes
       EVENT
```

or:

```text
ACTOR
  ↓ performs
TRANSFER EVENT
  ↓ destination
COMPONENT
```

Endpoint/event/state concerns were first observed much earlier, but deeper semantic-resolution generation now makes them materially consequential.

This is the evidence threshold the project had intentionally been waiting for before considering semantic-IR expansion.

## Resolution Strategy Decision

Do **not** create a large ontology of zoom strategies yet.

Current evidence supports only:

```text
PROCESS
→ internal stages / chronology
→ positive evidence

COMPONENT
→ internal composition when source supports it
→ safe-refusal evidence only

VARIABLE
→ causal neighborhood
→ hypothesis remains unvalidated
```

The provider-independent `ResolutionStrategy` boundary is useful and should remain, but strategy expansion should continue through evidence rather than taxonomy design.

## Navigation Finding

The owner again found explicit `Explore` and `Back` navigation inelegant.

The emerging navigation grammar remains:

```text
BACK
→ navigation history

ZOOM OUT
→ higher semantic abstraction

ZOOM IN
→ finer semantic resolution

CLICK NEIGHBOR
→ lateral movement through conceptual topology

PATH / BREADCRUMB
→ abstraction ancestry / current location
```

The parent context map should eventually evolve from passive orientation into an active semantic navigation surface.

However, navigation should not be the immediate next product implementation. Improving navigation over semantically misleading propositions would optimize the wrong layer.

## 2D / 3D Decision

The current product direction remains **2D topology + semantic zoom**.

The effective dimensions are:

```text
horizontal / topology
→ neighboring concepts / conceptual location

semantic zoom
→ abstraction / explanatory resolution
```

3D should be reserved for domains where a third physical/spatial dimension itself carries explanatory meaning, not used as the default abstract knowledge topology.

## On-Demand Compilation Direction

SPEC-008/009 continue to support a future architecture in which deeper semantic resolution is compiled on demand around learner focus rather than eagerly generating an enormous recursive graph.

This remains a hypothesis, not an implementation decision.

## Process Finding

During SPEC-009 implementation, Codex spent avoidable context and reasoning on repository/bootstrap reconciliation:

- interpreting ChatGPT-authored commits between Codex runs;
- rediscovering project roles;
- repeatedly protecting long-lived uncommitted README/ROADMAP edits;
- reading broad project memory eagerly;
- repairing a lifecycle-temporary test assertion that incorrectly assumed `DEBRIEF-008` must never exist.

This exposed a development-operating-system inefficiency.

The project should distinguish:

```text
INVARIANT IMPLEMENTATION CONTEXT
→ persistent Codex instructions

ACTIVE EXPERIMENT CONTEXT
→ current SPEC

HISTORICAL / DEEP CONTEXT
→ debriefs, architecture, project memory, health
→ retrieve only when relevant
```

A small operational maintenance increment should address this before the next major product SPEC.

## Decisions

1. Accept SPEC-009 as `MIXED_BY_ROLE`.
2. Record `PROCESS_STAGES` as positively validated for the owner benchmark.
3. Preserve `COMPONENT_INTERNALS` as a promising safe-refusal strategy, not a validated usefulness result.
4. Keep `VARIABLE_CAUSAL_NEIGHBORHOOD` provisional/unvalidated.
5. Keep Generic as a control, not a product policy.
6. Preserve the provider-independent strategy boundary.
7. Do not expand the strategy registry opportunistically.
8. Promote proposition/endpoint-role correctness to the highest-value semantic uncertainty.
9. Defer active map navigation until semantic proposition quality is improved.
10. Perform an operational context/Git-workflow cleanup before the next product SPEC.

## Recommended Sequence

```text
DEBRIEF-009
    ↓
OPS-001
Codex context + Git workflow optimization
    ↓
next product SPEC
semantic proposition / endpoint-role modeling
    ↓
later
active context-map navigation + semantic zoom
```

## Final Conclusion

SPEC-009 validates the central idea that **semantic zoom is role-dependent** in at least one important case: a process naturally resolves into stages.

It also reveals a more fundamental bottleneck. Knowledge Compiler can now generate source-grounded, structurally coherent, cognitively useful-looking deeper models whose individual propositions are still subtly wrong because the current semantic IR collapses compound conditions, events, states, and endpoint roles into simple entity-to-entity edges.

The next semantic breakthrough therefore depends less on producing more graph and more on representing propositions more faithfully.
