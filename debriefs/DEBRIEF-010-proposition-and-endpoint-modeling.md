# DEBRIEF-010 — Proposition and Endpoint Modeling

## Status

Accepted — semantic PASS.

## Implementation

Commit:

```text
0fcc0d9ea938e0766dd1cb151ffc484c6d95bebe
```

Offline validation:

```text
143 passed in 0.35s
```

No live provider calls were required.

## Primary Question

> Can Knowledge Compiler represent compound conditions and transfer endpoint roles more faithfully without turning `KnowledgeModel` into a general-purpose ontology?

## Outcome

**Yes.**

A minimal hybrid proposition layer preserves the simplicity of ordinary binary relationships while providing richer structured semantics only where a binary edge demonstrably loses proposition truth.

The owner reviewed both canonical regression examples and accepted the semantic improvement.

## Economics Regression

The previous lossy representation was effectively:

```text
quantity demanded ──CAUSES──→ shortage
```

The source proposition actually depends on a comparison between two quantities:

```text
quantity demanded > quantity supplied
                 │
               CAUSES
                 ↓
              shortage
```

SPEC-010 now preserves explicit roles:

```text
LEFT_OPERAND   = quantity demanded
RIGHT_OPERAND  = quantity supplied
OPERATOR       = GREATER_THAN
OUTCOME        = shortage
RELATIONSHIP   = CAUSES
```

The exact source evidence remains grounded to characters 275–364.

Human verdict: the richer proposition materially preserves meaning that the old binary edge necessarily distorted.

## Transfer Regression

The previous binary representation conflated the transfer event and destination.

SPEC-010 now represents:

```text
TRANSFER EVENT
EVENT        = order command transfer
OBJECT       = order command
DESTINATION  = order component
RELATIONSHIP = TRANSFERS_TO
```

Exact source evidence remains grounded to characters 238–352.

Human verdict: the structured roles clearly distinguish what happened, what moved, and where it went.

## Architecture Decision

Use a hybrid semantic model:

```text
KnowledgeModel
    │
    ├── ordinary binary relationships
    │      A ─predicate→ B
    │
    └── structured propositions
           only where binary representation loses truth
```

This is preferable to making every relationship hyper-structured.

### Current proposition scope

Exactly:

- `COMPARISON_CONDITION`
- `TRANSFER_EVENT`
- `GREATER_THAN`
- the minimum explicit role vocabulary required by those forms

No general expression tree, universal event ontology, or state language was introduced.

## Core Rule

The project now has an experimentally earned semantic rule:

> **Use binary relationships whenever they preserve proposition truth. Promote to a structured proposition only when binary representation necessarily loses meaning.**

This rule should constrain future IR evolution.

## Important Non-Decision

Do not proactively add imagined proposition forms such as:

```text
AND / OR / NOT
LESS_THAN / EQUALS
ACTOR / INSTRUMENT / LOCATION
arbitrary STATE / TRANSITION
nested expressions
```

Future source failures should earn additional semantic forms through evidence.

## Downstream Finding

Structure detection intentionally ignores proposition shapes rather than flattening them back into false binary edges.

Representation exposes proposition cards separately from ordinary graph topology.

This was correct for SPEC-010 because it preserved semantic truth without forcing a second large downstream redesign.

However, it reveals a future possibility: propositions may eventually need to become first-class topological/visual objects.

Illustrative future form:

```text
quantity demanded ──┐
                    ▼
                   [>] ──CAUSES──→ shortage
                    ▲
quantity supplied ──┘
```

and:

```text
order command ──object──→ [TRANSFER EVENT] ──destination──→ order component
```

This is not yet justified as the immediate next implementation.

## Compatibility Finding

Existing artifacts remain valid without migration. Empty proposition collections are omitted from serialization. The canonical relationship vocabulary remains exactly 20 predicates.

This confirms that the proposition seam can coexist with the previously validated binary IR rather than replacing it.

## Product/Architecture Position After SPEC-010

Knowledge Compiler now has experimentally demonstrated pieces across a substantial stack:

```text
TEXT
 ↓
grounded semantic extraction
 ↓
canonical binary relationships
 ↓
structured propositions where required
 ↓
higher-order structure detection
 ↓
representation
 ↓
structure-aware layout
 ↓
interactive semantic selection
 ↓
contextual semantic navigation
 ↓
automatic multi-resolution compilation
 ↓
role-aware resolution strategies
```

The project has therefore reached a natural review point. Continuing directly into SPEC-011 risks optimizing the most recently visible local problem rather than selecting the highest-information next experiment.

## Navigation Finding Preserved

The owner has repeatedly preferred the emerging map-navigation model over explicit `Explore` / `Back` scaffolding:

```text
BACK
→ navigation history

ZOOM OUT
→ higher abstraction

ZOOM IN
→ finer semantic resolution

CLICK NEIGHBOR
→ lateral movement through conceptual topology

PATH
→ current abstraction ancestry/location
```

The default abstract knowledge surface remains 2D topology + semantic zoom. 3D is reserved for domains where physical/spatial dimensionality itself carries explanatory information.

## Operational Finding

OPS-001 was observed during SPEC-010 and appears successful:

- Codex accepted `origin/main` as canonical without lengthy commit-forensics;
- invariant role/context reconstruction was largely eliminated;
- historical context was loaded selectively;
- time to architecture reasoning was substantially shorter;
- the user prompt reduced to one sentence;
- the remaining known startup friction is the persistent local README/ROADMAP dirty state.

## Decisions

1. Accept SPEC-010 as a semantic PASS.
2. Preserve the minimal hybrid proposition architecture.
3. Do not expand proposition vocabulary speculatively.
4. Preserve ordinary binary relationships as the default semantic primitive.
5. Keep propositions out of structure traversal until a concrete use case earns topological integration.
6. Do not immediately start SPEC-011.
7. Perform a project-level product/architecture review across SPEC-001 through SPEC-010.
8. Resolve the long-lived README/ROADMAP local edits before the next major implementation phase if possible.

## Next Decision Gate

The next work should answer:

> Given everything experimentally learned from SPEC-001 through SPEC-010, what remaining uncertainty has the highest expected information value for the product?

Candidate directions include, but are not limited to:

- active context-map navigation + semantic zoom;
- proposition-aware topology;
- further semantic IR refinement only if evidence demands it;
- on-demand recursive/local compilation;
- real-source ingestion beyond fixed text;
- broader learning evaluation;
- cognitive presets/personalization experiments.

Do not choose merely because a capability is technically adjacent to SPEC-010.
