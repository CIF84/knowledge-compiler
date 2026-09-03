# SPEC-010 — Proposition and Endpoint Modeling

## Status

Ready for implementation.

## Primary Question

> Can Knowledge Compiler represent compound conditions, events, states, and endpoint roles more faithfully without turning `KnowledgeModel` into a general-purpose ontology?

## Why This Now

SPEC-009 demonstrated a hard boundary in the current semantic model:

```text
GROUNDING CORRECTNESS
        ≠
PROPOSITION CORRECTNESS
```

Two source-grounded, mechanically valid outputs still represented the wrong proposition:

```text
quantity demanded > quantity supplied
              ↓
           shortage
```

was collapsed toward:

```text
quantity demanded
      ↓ CAUSES
   shortage
```

and a transfer proposition confused the transfer process/event with the transfer destination.

These are not presentation bugs. They indicate that some source propositions cannot be represented truthfully as a single simple:

```text
entity ─predicate→ entity
```

edge.

Endpoint/event/state limitations were previously visible but tolerable. Multi-resolution compilation now makes them materially consequential.

## Objective

Design and test the **minimum semantic extension** needed to represent the two concrete failure classes more faithfully:

1. **compound condition / relation-as-cause**
2. **event/process with explicit semantic roles such as destination**

The experiment must improve semantic truthfulness while preserving:

- source grounding;
- canonical relationship semantics;
- deterministic validation;
- downstream structure/representation compatibility where possible;
- provider independence;
- current simple architecture.

Do not build a universal proposition language.

## Required Context

Use `AGENTS.md` for invariant operating context.

Read only the material needed for this experiment, especially:

- `debriefs/DEBRIEF-009-semantic-resolution-strategy.md`
- current `models.py`
- current `relationships.py`
- current extraction / resolution compiler boundaries
- relevant SPEC-009 live artifacts for Economics and Process
- relevant structure-detection and representation code that consumes current relationships

Do not eagerly load all project documents unless a concrete ambiguity requires them.

## Experimental Principle

Change the smallest semantic boundary that can encode the proposition truthfully.

Prefer:

```text
minimal typed proposition structure
```

over:

```text
new ontology
new graph database
new universal logical language
new relationship explosion
```

## Benchmark Regression A — Compound Condition

Use the accepted Economics source proposition expressing that shortage occurs when quantity demanded exceeds quantity supplied.

The current incorrect simplification is conceptually:

```text
quantity demanded ─CAUSES→ shortage
```

The target representation must preserve that the causal antecedent is a **compound condition comparing two quantities**.

A valid solution could resemble one of these shapes:

```text
Condition
  left: quantity demanded
  operator: GREATER_THAN
  right: quantity supplied
        ↓ CAUSES
     shortage
```

or:

```text
quantity demanded
      \ 
       >  [comparison condition] ─CAUSES→ shortage
      /
quantity supplied
```

Exact type names are implementation choices.

Required properties:

- both participating quantities remain explicit;
- the comparison operator remains explicit;
- the condition is the causal source, not either quantity alone;
- source evidence remains exact and traceable;
- no fake entity should be created merely to satisfy graph shape unless the semantic model clearly distinguishes proposition nodes from domain entities.

## Benchmark Regression B — Event / Endpoint Roles

Use the accepted SPEC-009 process proposition in which an order command is transferred to the order component.

The current defect confuses:

```text
transfer event/process
```

with:

```text
transfer destination
```

The target representation must distinguish at least:

```text
transfer event/process
    thing transferred: order command
    destination: order component
```

and preserve chronology/dependency semantics where present.

A valid shape could resemble:

```text
TransferEvent
   object → order command
   destination → order component
```

with other relations such as `PRECEDES` attached to the event as appropriate.

Do not add a general actor/event ontology unless the regression requires it.

## Design Space

Investigate the smallest viable design among options such as:

### Option A — Proposition Nodes

Introduce typed proposition nodes distinct from ordinary domain entities, e.g.:

```text
CONDITION
EVENT
STATE
```

with explicit role bindings.

### Option B — Relationship Qualifiers / Arguments

Allow selected relationships to carry structured arguments/roles beyond source and target.

### Option C — Hybrid

Use proposition nodes only when a proposition cannot be represented truthfully as a binary relationship.

Do not assume one option in advance. Choose based on minimality, validation clarity, downstream compatibility, and evidence from the two regressions.

## Required Semantic Constraints

Whatever design is chosen:

1. Ordinary existing entity-to-entity relationships must remain valid and backwards-compatible where practical.
2. Existing artifacts should not require a wholesale migration if avoidable.
3. New proposition structures must have stable IDs and deterministic serialization.
4. Source-grounded proposition structures must preserve exact evidence/provenance.
5. Inferred proposition structures must not fabricate evidence.
6. Endpoint roles must be explicit enough that trusted code can reject role confusion.
7. Compound conditions must preserve all semantically required operands.
8. The representation must distinguish domain entities from proposition/event/condition structures.
9. Provider output must remain typed and validated before becoming canonical state.

## Predicate Vocabulary

Do not expand the existing 20 canonical predicates unless a repeated, general gap is proven unavoidable.

Prefer structured proposition roles such as:

```text
left_operand
right_operand
comparison_operator
object
source
destination
participant
```

rather than inventing many new binary predicates.

If one new predicate is genuinely necessary, justify it explicitly in the handoff.

## Comparison Operators

If compound-condition support requires comparison operators, introduce only the minimum needed for the regression.

For example:

```text
GREATER_THAN
```

Do not create a full expression language unless implementation evidence makes it necessary.

## Extraction / Resolution Integration

Update the probabilistic boundary only enough to nominate the richer proposition structure.

The prompt/schema should explicitly distinguish:

```text
ordinary binary relationship
compound condition proposition
event/process proposition with roles
```

Trusted code must validate role requirements.

Do not let the model silently decide that a binary edge is acceptable when the source proposition requires a compound structure.

Where deterministic validation can identify information loss, fail closed.

## Validation Rules

Add fail-closed invariants at minimum for:

### Compound condition

- required operands exist;
- comparison operator is valid;
- operands are not silently dropped;
- causal relationship points from the condition proposition rather than one operand when the source proposition is conditional/comparative;
- exact evidence validates.

### Event / transfer

- transfer object exists where required;
- destination exists where required;
- event node cannot be used as its own destination;
- destination role points to a domain entity/component, not the transfer process itself;
- chronology/dependency edges preserve canonical direction.

## Downstream Compatibility

Assess the impact on:

```text
StructureDetector
DetectedStructureSet
RepresentationBuilder
layout
viewer
semantic navigation
ResolutionCompiler
```

The goal is **not** to fully redesign all downstream layers.

Implement the smallest compatibility seam that allows the two richer proposition cases to remain truthful and inspectable.

Acceptable outcomes include:

- richer propositions are preserved in `KnowledgeModel` and rendered minimally while existing structure detection ignores unsupported proposition shapes;
- one focused deterministic adapter exposes safe edges for existing downstream composition without losing the richer proposition semantics;
- structure detection gains a narrowly scoped ability to traverse proposition nodes where semantically valid.

Do not flatten the richer structure back into the same misleading binary edge merely to keep downstream code unchanged.

## Representation Requirement

The owner must be able to inspect the richer proposition clearly enough to verify what the system believes.

For the Economics condition, the representation/detail should make visible that shortage depends on:

```text
quantity demanded > quantity supplied
```

For the transfer case, the representation/detail should make visible:

```text
object transferred → order command
destination        → order component
```

This may be a minimal detail-panel or proposition-card treatment. Do not redesign the viewer broadly.

## Controlled Evaluation

Use the exact source material that exposed the defects.

Compare:

```text
CURRENT / BINARY MODEL
        vs
PROPOSITION-AWARE MODEL
```

For each regression record:

```text
source proposition
old representation
new representation
source grounding status
semantic truthfulness verdict
information preserved/lost
structure-detection effect
representation effect
```

## Live Provider Evaluation

If live LLM calls are necessary to test whether the provider can populate the richer schema, keep the experiment narrow.

Prefer one call per regression plus a control only if needed.

Preserve all failed proposals and do not hide retries.

Do not perform external enrichment.

Normal `pytest` must remain fully offline/deterministic.

## Machine Evaluation

Machine checks should verify semantic invariants, not pretend to judge all proposition truth.

At minimum verify:

- both operands preserved for the Economics condition;
- comparison operator preserved;
- shortage caused by the condition proposition, not an operand alone;
- transfer object preserved;
- transfer destination preserved;
- transfer destination cannot equal the transfer event;
- exact source evidence/provenance preserved;
- stable deterministic IDs/serialization;
- existing ordinary relationships still validate;
- parent artifacts remain immutable;
- no accidental predicate-vocabulary growth;
- no product-navigation behavior change.

## Human Review

After repository/semantic review, provide the simplest viewer/artifact command for owner inspection.

The owner should answer only:

1. Does the Economics proposition now say what the source actually says?
2. Does the transfer proposition now distinguish the event, transferred object, and destination correctly?
3. Does the richer representation remain understandable rather than feeling like ontology machinery leaking into the learning interface?

Do not require broad UX scoring.

## Explicit Non-Goals

Do not implement:

- first-order logic;
- arbitrary boolean expression trees;
- a general theorem prover;
- RDF/OWL migration;
- graph database;
- event sourcing architecture;
- full temporal logic;
- universal role ontology;
- automatic map navigation;
- recursive semantic zoom;
- personalization;
- new cognitive presets;
- broad UI redesign;
- external retrieval;
- broad event/state repair across all benchmark domains;
- large relationship-vocabulary expansion;
- schema changes motivated only by hypothetical future use.

## Acceptance Criteria

- [ ] The current Economics shortage proposition can be represented without dropping `quantity supplied`.
- [ ] The comparison condition remains explicit.
- [ ] The causal source is the compound condition rather than a single operand.
- [ ] The process transfer proposition distinguishes transfer event/process from destination.
- [ ] Transfer object and destination roles are explicit.
- [ ] Exact source grounding/provenance remains intact.
- [ ] Rich proposition structures have deterministic IDs and serialization.
- [ ] Existing ordinary binary relationships remain valid.
- [ ] Existing relationship vocabulary remains unchanged unless one narrowly justified addition is unavoidable.
- [ ] Trusted validation rejects the two original endpoint-loss patterns.
- [ ] Downstream behavior preserves richer semantics rather than silently flattening back to the defective binary form.
- [ ] Minimal owner-inspectable representation exists for both regressions.
- [ ] Offline tests pass.
- [ ] Live evaluation, if used, is fully reported with no hidden retries.
- [ ] No navigation/personalization/frontend redesign is introduced.
- [ ] Implementation is committed and pushed to canonical `origin/main`.
- [ ] No `DEBRIEF-010` is created by Codex.

## Required Handoff

Report:

1. chosen semantic design and alternatives rejected;
2. exact new/changed semantic types/fields;
3. why the design is the minimum sufficient extension;
4. Economics old vs new proposition representation;
5. Process transfer old vs new proposition representation;
6. validation invariants added;
7. extraction/resolution schema changes;
8. relationship-vocabulary changes, if any;
9. deterministic ID/serialization behavior;
10. source grounding/provenance result;
11. downstream compatibility changes;
12. structure-detection impact;
13. representation/viewer impact;
14. exact offline test result;
15. live-call matrix/result if applicable;
16. machine semantic regression results;
17. exact owner-review command/artifact;
18. known semantic limitations remaining;
19. complexity added;
20. dependencies added/removed;
21. deviations;
22. commit SHA;
23. confirmation pushed to canonical `origin/main`.

Do not create `DEBRIEF-010`. Human semantic review follows independent repository inspection.

## Decision Gate After SPEC-010

### If the minimal proposition model fixes both regressions cleanly

Promote the richer proposition boundary cautiously and revisit whether multi-resolution generation can use it broadly.

### If only one regression improves

Keep the successful capability narrow and avoid forcing a single proposition abstraction across unrelated semantic roles.

### If downstream complexity explodes

Reject the design and reconsider whether proposition truth should live in a parallel canonical proposition layer rather than expanding graph structure directly.

### If the richer structure is semantically correct but cognitively unreadable

Keep semantic truth in the IR and solve learner-facing projection separately. Do not weaken the semantic model for UI simplicity.

## Final Constraint

SPEC-010 should prove only this:

> Knowledge Compiler can preserve proposition truth when binary entity-to-entity edges are insufficient.

Nothing more.
