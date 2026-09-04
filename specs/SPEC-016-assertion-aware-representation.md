# SPEC-016 — Assertion-Aware Knowledge Representation

## Status

Ready for implementation.

## Phase

Phase II — return from semantic reliability to learner-facing cognition.

## Primary Question

> Can Knowledge Compiler construct a cognitively useful orientation from trustworthy grounded assertions and claims without promoting them into stronger canonical graph relationships or weakening the semantic truth boundary?

## Why This Experiment Now

SPEC-011 through SPEC-015 progressively improved realistic-source semantic reliability.

SPEC-013 produced the first trusted realistic-source parent for the frozen quantum benchmark:

```text
41 symbols
24 grounded assertions
21 claims
3 canonical relationships
```

All three canonical relationships passed independent semantic review.

But existing downstream structure/representation produced only:

```text
2 represented entities
1 sparse edge
```

This is truthful but cognitively inadequate for the original learning objective.

The semantic compiler is now intentionally conservative. Most trustworthy source meaning survives as grounded assertions/claims rather than canonical graph edges.

Therefore the next bottleneck is no longer extraction reliability. It is representation.

## Core Principle

Do **not** solve sparse representation by weakening semantic admission.

The semantic truth layer remains authoritative:

```text
canonical relationship
    = strong typed semantic commitment

structured proposition
    = richer typed semantic commitment

claim / grounded assertion
    = source meaning preserved without stronger canonical topology
```

Representation may project all of these differently, but it must never imply that a claim/assertion is a canonical relationship when it is not.

## Experimental Benchmark

Use the accepted SPEC-013 realistic-source artifacts as the primary frozen input:

```text
examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904/
```

At minimum consume the accepted/frozen:

```text
symbol-table.json
grounded-assertions.json
parent.knowledge.json
parent.structures.json
parent.representation.json
canonicalization-result.json
```

Verify artifact hashes/identity before building the experimental projection.

Do not rerun source extraction, symbol discovery, assertion extraction, canonicalization, or any semantic gate.

Primary SPEC-016 evaluation should be **offline only**.

## Experimental Comparison

### Control

Existing SPEC-013 representation:

```text
canonical graph semantics
        ↓
existing structure detection
        ↓
existing representation
        ↓
2 represented entities / 1 sparse edge
```

### Experiment

Build a presentation-only assertion-aware projection:

```text
trusted KnowledgeModel
+
grounded assertions / claims
        ↓
AssertionAwareRepresentationBuilder
        ↓
orientation model
        ↓
viewer
```

The experiment must preserve the distinction between semantic tiers.

## Representation Tiers

The learner-facing projection should visually and structurally distinguish at least:

```text
CANONICAL RELATIONSHIP
STRUCTURED PROPOSITION
GROUNDED CLAIM / ASSERTION
```

If SPEC-013 contains no structured proposition in the primary artifact, keep proposition support compatible but do not manufacture one for the experiment.

### Canonical relationship

May use the existing strong directed-edge grammar.

It should remain visually identifiable as canonical/typed semantics.

### Structured proposition

May use proposition cards or a suitable multi-part visual form already established by SPEC-010.

Do not flatten it into a binary edge.

### Grounded claim/assertion

Must not masquerade as a canonical predicate edge.

It may be represented through a weaker visual grammar such as:

- assertion cards attached to concepts;
- evidence-backed semantic neighborhoods;
- lightweight association ribbons;
- grouped explanatory statements;
- concept-centered assertion clusters;
- other clearly non-canonical presentation forms.

Choose the smallest representation that makes the source's conceptual structure usable.

## No New Semantic Truth

The representation builder must be deterministic and presentation-only.

It must not:

- create new semantic relationships;
- infer predicates;
- change endpoints;
- rewrite claims into stronger statements;
- create new assertions;
- mint entities;
- add proposition types;
- classify claims into new ontology categories;
- call an LLM;
- use embeddings or external enrichment.

It may only project existing trusted semantic material.

## Assertion-to-Concept Attachment

Grounded assertions already carry participant entity IDs.

Use those participant identities as the primary deterministic attachment mechanism.

Conceptually:

```text
assertion
  ├── participant A
  ├── participant B
  └── participant C
```

may become a presentation neighborhood around those concepts without claiming a canonical A→B or A→C relationship.

Do not invent pairwise edges from an N-participant assertion merely for layout convenience.

## Orientation Goal

The experiment is not to display all 24 assertions simultaneously at full detail.

The learner should be able to answer approximately:

```text
What are the major ideas in this source?
Which concepts participate in the same explanations?
Where are the few strong canonical relationships?
What source-backed statements explain each neighborhood?
Where could I inspect evidence?
```

The goal is **orientation before exhaustive detail**.

## Projection Strategy

Implement the smallest deterministic strategy that produces a coherent orientation from assertion participation.

A reasonable minimum approach may include:

1. build a bipartite presentation graph:

```text
concept nodes ↔ assertion nodes/cards
```

2. compute deterministic participation/connectivity diagnostics;
3. group or rank assertion neighborhoods using transparent structural rules;
4. surface a bounded number of high-information neighborhoods initially;
5. preserve access to the remaining grounded assertions through interaction/detail.

This is guidance, not a mandate to use a literal bipartite SVG if another simpler presentation is cognitively better.

## Salience

Do not use an LLM to rank importance.

Use transparent deterministic signals available from the frozen artifacts, for example:

```text
assertion participant count
concept assertion-degree
canonical relationship participation
claim/assertion overlap
existing entity type
existing structure membership
```

Avoid pretending these are universal semantic-importance scores.

Record the exact heuristic and diagnostics.

If no deterministic salience rule produces a useful overview, preserve that finding rather than hand-curating the quantum map.

## Density Control

Realistic source material can create visual overload.

The initial orientation must be bounded.

Do not render a 41-node / 24-assertion hairball by default.

Prefer progressive disclosure using existing interaction ideas:

```text
overview
  ↓ select concept / assertion neighborhood
focus
  ↓ inspect assertion
source evidence
```

Do not implement full semantic zoom or active map navigation in this SPEC.

## Interaction

Reuse existing interaction principles where practical:

- click persists selection;
- hover previews;
- selected visual object synchronizes with details;
- evidence remains inspectable;
- canonical relationships remain distinguishable from assertion-level material.

Do not redesign the entire viewer.

A dedicated experimental viewer/assets are acceptable to protect accepted baselines.

## Visual Grammar Requirement

The user should be able to tell **without reading implementation metadata** whether an item is:

```text
strong canonical semantic relationship
vs
source-grounded explanatory assertion/claim
```

Use restrained visual differentiation.

Do not use visual confidence percentages unless already grounded in existing semantics.

Possible distinction dimensions:

```text
line style
node/card shape
label treatment
layer/section
interaction detail
legend
```

Do not rely on color alone for semantic distinction.

## Evidence / Provenance

Every displayed assertion/claim must preserve provenance back to its existing grounded source evidence.

Every canonical relationship must preserve its existing relationship/proposition provenance.

The viewer must not fabricate evidence for presentation-only links/layout constructs.

If a presentation construct has no semantic evidence because it is merely layout/grouping, label it as presentation metadata rather than semantic truth.

## Truthful Labels

Use learner-readable language.

Avoid exposing internal compiler jargon as the primary interface where possible.

For example, the UI may describe tiers as:

```text
Established relationship
Source-backed explanation
Structured condition/event
```

while machine artifacts retain canonical internal names.

Do not imply scientific certainty beyond source support.

## Quantum Learning Objective

Return to the original SPEC-011 learner target:

> Build an intuitive mental model of why quantum mechanics behaves differently from classical mechanics and how quantum state, superposition, probability amplitudes, interference, measurement, uncertainty, and entanglement relate.

However, SPEC-016 must not force these concepts into the view if the accepted SPEC-013 source artifacts do not contain them as trustworthy symbols/assertions.

The source remains authoritative.

## Human Review

This SPEC reintroduces owner cognitive review.

### Review ordering

After machine integrity checks, provide the owner:

1. exact viewer launch command;
2. minimal instruction: **“Use this to orient yourself in the quantum-mechanics material.”**

Do not lead with a long machine report.

Capture spontaneous reaction first.

Then ask:

### Orientation

- Can I see more of the trustworthy source meaning than in the sparse control?
- Can I identify major conceptual neighborhoods?
- Does the representation feel like a map rather than a list of extracted sentences?

### Semantic trust

- Can I tell strong relationships from weaker source-backed explanations?
- Does anything visually imply a stronger semantic claim than the underlying data supports?
- Can I inspect evidence when something seems surprising?

### Cognitive usefulness

- Does this reduce the burden of reconstructing the source structure mentally?
- Would I choose to continue exploring this representation?
- Is the additional assertion material useful or merely clutter?

### Comparison

Compare against the SPEC-013 sparse control.

The primary human question:

> **Does assertion-aware projection make the trusted quantum model materially more useful to think with without making it feel less trustworthy?**

Do not claim measured learning efficacy.

## Machine Evaluation

Report at least:

```text
input symbol count
input canonical relationship count
input proposition count
input grounded assertion / claim count
represented concept count
represented canonical relationship count
represented assertion/claim count
initial visible concept count
initial visible assertion count
coverage ratios
assertion-degree distribution
number/size of displayed neighborhoods
layout overlaps/crossings where meaningful
provenance completeness
semantic-tier labeling completeness
determinism / byte-for-byte regeneration
```

Do not invent universal quality thresholds from these metrics.

## Success Criteria

SPEC-016 is successful if:

1. substantially more trustworthy source meaning becomes accessible than in the 2-node/1-edge control;
2. canonical relationships remain semantically distinct from claims/assertions;
3. no new semantic truth is introduced;
4. provenance remains complete;
5. the initial view avoids an unreadable hairball;
6. the owner finds the representation materially more useful for orientation than the sparse control.

A representation can fail despite high coverage if it is cognitively noisy.

## Allowed Verdicts

Final verdict must be exactly one of:

```text
ASSERTION_AWARE_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

Human cognitive review is required for the final usefulness verdict.

Machine integrity can pass while the product verdict remains pending owner review.

## No Live Model Calls

SPEC-016 primary experiment is offline.

Do not call OpenAI or any external semantic provider.

If implementation discovers that an LLM call is necessary to produce the representation, stop and report why rather than making the call.

## Baseline Protection

Do not modify accepted baseline viewer assets in place if doing so risks changing prior evaluation artifacts.

Prefer isolated experimental assets or backward-compatible additions.

Preserve:

```text
BASELINE-001
SPEC-007 navigation experiments
SPEC-010 proposition review
SPEC-013 accepted semantic artifacts
SPEC-014/015 gate artifacts
```

## Explicit Non-Goals

Do not implement:

- new extraction;
- new semantic gates;
- production integration of SPEC-014/015;
- semantic vocabulary changes;
- proposition vocabulary changes;
- source segmentation;
- embeddings;
- clustering models;
- LLM salience ranking;
- semantic zoom generation;
- active Google-Maps-style navigation;
- Journey/course mode;
- learning-path generation;
- simulation;
- ingestion/product shell;
- multi-user study.

## Testing Strategy

All tests offline.

Add focused coverage for:

```text
SPEC-013 artifact identity verification
assertion/claim participant attachment
no pairwise-edge fabrication
semantic-tier preservation
canonical relationship preservation
provenance preservation
salience determinism
density limits
layout determinism
viewer artifact generation
baseline immutability
byte-for-byte regeneration
```

Keep full suite passing.

## Evaluation Artifacts

Create:

```text
examples/evaluations/spec-016-assertion-aware-representation-<date>/
```

Likely artifacts:

```text
input-manifest.json
assertion-aware-representation.json
projection-diagnostics.json
report.json
human-review-template.json
index.html
viewer assets
README.md
```

Do not duplicate copyrighted source text beyond existing evidence excerpts.

## Acceptance Criteria — Technical

- [ ] SPEC-013 frozen inputs verified.
- [ ] No semantic source artifacts modified.
- [ ] No live model calls.
- [ ] Provider-independent deterministic projection boundary exists.
- [ ] Canonical relationships remain unchanged.
- [ ] Claims/assertions are never serialized as canonical relationships.
- [ ] No pairwise semantic edges are fabricated from assertion participants.
- [ ] Structured propositions retain their distinct representation semantics.
- [ ] Assertion/claim provenance is complete.
- [ ] Presentation-only grouping is explicitly non-semantic.
- [ ] Initial orientation is bounded.
- [ ] More trustworthy semantic material is accessible than in SPEC-013 control.
- [ ] Semantic tiers are visually distinguishable without color alone.
- [ ] Viewer interaction preserves evidence inspection.
- [ ] Generation is deterministic.
- [ ] Prior baselines/artifacts unchanged.
- [ ] Full offline suite passes.

## Final Constraint

SPEC-016 must not trade semantic reliability back for visual richness.

The experiment asks:

> **Now that Knowledge Compiler has learned to preserve trustworthy meaning conservatively, can its presentation layer make that meaning cognitively useful without pretending it knows more than it does?**
