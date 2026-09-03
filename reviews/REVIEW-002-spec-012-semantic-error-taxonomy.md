# REVIEW-002 — SPEC-012 Semantic Error Taxonomy

## Status

Decision review. No implementation authorized by this document.

## Purpose

SPEC-012 improved structural consistency but left 10 of 16 reviewed semantic items unsupported, imprecise, or otherwise defective.

The goal of this review is to ask:

> Do those failures share a common mechanism strong enough to justify the next architecture experiment?

## Evidence Set

Use the independently reviewed rejected Pass-2 proposal from SPEC-012.

Reviewed items:

```text
16 total
6 SUPPORTED
10 defective
```

Observed defect classes:

```text
OVERSTATED_CAUSALITY
WRONG_PREDICATE
IMPRECISE_ENDPOINT
UNSUPPORTED
```

No reversed-direction defect was observed in the staged set.

## Error Taxonomy

### A. Premature predicate commitment

Examples:

- quantum revolution `CAUSES` quantum mechanics;
- superfluidity `EXAMPLE_OF` quantum mechanics;
- electron microscope / laser / transistor / MRI represented with `ENABLES`;
- QED `IS_A` quantum field theory from evidence that only calls it a quantum theory of electromagnetic force.

Common pattern:

```text
source says X in ordinary explanatory language
        ↓
model must choose one canonical predicate immediately
        ↓
closest available graph predicate is selected
        ↓
source meaning is strengthened or changed
```

This accounts for most staged semantic defects.

### B. Endpoint compression / missing proposition participant

Examples:

- tunneling targeted `transistor` instead of electron penetration through an oxide barrier;
- Pauli exclusion targeted `electron` instead of the constrained joint state / quantum-number assignment.

Common pattern:

```text
source assertion involves an event/state/condition
        ↓
frozen symbol inventory contains nearby concrete concepts
        ↓
semantic linker selects an available endpoint
        ↓
relationship becomes grammatically valid but propositionally wrong
```

This suggests that a correct symbol table is necessary but not sufficient: the semantic unit the source asserts may not correspond to a simple pair of entity symbols.

### C. Evidence nomination error

Example:

- Stern–Gerlach item used a non-verbatim quote.

This is a distinct mechanical grounding defect.

It should not dominate architecture decisions because 27/28 evidence nominations were exact and the semantic proposal remained weak even excluding this failure.

### D. Good cases

The six supported items are also informative. The current direct graph mapping works well when the source itself already expresses a relationship close to the canonical grammar, for example:

```text
explicit experimental production
explicit example/classification
collapse → eigenstate
Standard Model → quantum field theory
photon classification
structured transfer event
```

The architecture therefore should not abandon direct binary relationships. It needs a safer boundary for assertions that are not already graph-shaped.

## Root-Cause Assessment

The ten defects do not point to ten unrelated ontology gaps.

The dominant shared mechanism is:

> **Canonicalization happens before the source assertion has been preserved in a neutral enough form.**

The semantic linker is solving two tasks simultaneously:

```text
TASK 1
What exactly does this sentence/passage assert?

TASK 2
Which Knowledge Compiler semantic form best represents that assertion?
```

When Task 2 is forced too early, the model frequently strengthens weak explanatory language into causality/dependency/classification or substitutes a nearby available endpoint for a richer event/state/condition.

## Proposition-First Hypothesis

A candidate next experiment is not simply “add a third LLM pass.”

The stronger hypothesis is to introduce a provider-independent **source assertion IR** between frozen symbols and canonical graph semantics.

Conceptually:

```text
SOURCE
  ↓
SYMBOL TABLE
  ↓
SOURCE ASSERTIONS
  ↓
trusted / bounded semantic normalization
  ├── binary relationship
  ├── structured proposition
  ├── claim
  └── preserve as uncompiled assertion
  ↓
KnowledgeModel
```

A source assertion should preserve meaning before deciding whether it is causal, structural, dependency-like, descriptive, or not safely representable as an edge.

Possible minimum fields might include:

```text
assertion text / normalized proposition
participant symbol IDs
source evidence
origin
optional relation hint
```

But this review does **not** authorize a schema. The next SPEC should test the minimum sufficient form.

## Why Not Just Improve the Predicate Prompt?

Prompt tightening could reduce individual mistakes, but SPEC-003 already showed diminishing returns from increasingly elaborate relationship grammar.

The realistic-source failures are broader:

- application language becomes dependency;
- explanation becomes classification;
- conceptual development becomes causality;
- event/state participants collapse into nearby entities.

These are representation-boundary problems, not only missing predicate definitions.

A prompt-only control may still be useful inside the next experiment, but should not be assumed sufficient.

## Why Not Expand the Relationship Vocabulary?

Several errors tempt new predicates such as:

```text
EXPLAINS
APPLIED_IN
USED_BY
```

Do not add them yet.

A larger vocabulary could simply give the model more ways to prematurely canonicalize source language. The problem is not proven to be vocabulary scarcity.

Preserve unsupported explanatory assertions as claims/assertions until evidence justifies new canonical semantics.

## Why Not Add More Symbols?

Endpoint defects partly reflect missing event/state symbols, but blindly expanding Pass-1 inventory would increase symbol volume and may not solve proposition structure.

The Pauli example is not simply missing a noun. The source assertion is about a constraint on allowed joint states/quantum numbers.

The tunneling example concerns a process outcome, not merely another object.

This supports richer assertion preservation before deciding whether new semantic entities are needed.

## Decision

Evidence is strong enough to justify a next experiment around **assertion-first semantic compilation**.

The next experiment should not assume a full three-pass production architecture. It should compare the smallest assertion-preserving approach against the current staged Pass-2 direct-to-canonical approach on the same frozen quantum source.

## Proposed SPEC-013 Question

> Does preserving source assertions in a neutral intermediate form before canonical relationship/proposition normalization materially improve semantic precision on the frozen quantum benchmark without weakening grounding or exploding complexity?

## Recommended Experimental Control

Keep Pass 1 symbol discovery from SPEC-012 constant.

Compare:

```text
CONTROL
symbols
  ↓
direct canonical semantic linking
(SPEC-012 Pass 2)

EXPERIMENT
symbols
  ↓
source assertion extraction
  ↓
canonical semantic normalization
```

Do not rerun the SPEC-012 control unless needed; use preserved artifacts where fair.

## Success Condition

A next-stage architecture should materially improve semantic precision, especially by reducing:

```text
overstated causality
wrong predicate selection
endpoint substitution
```

without weakening:

```text
exact grounding
symbol integrity
fail-closed behavior
```

It is acceptable for fewer assertions to compile into graph edges.

Precision remains more important than graph volume.

## Final Conclusion

SPEC-012's remaining failures share a strong enough pattern to justify a new hypothesis.

The project should stop asking the model to translate source prose directly into canonical graph grammar whenever the prose is not already graph-shaped.

The next experiment should test whether **preserve assertion first, compile semantics second** produces a more trustworthy realistic-source knowledge model.
