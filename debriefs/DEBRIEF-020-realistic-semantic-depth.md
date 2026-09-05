# DEBRIEF-020 — Realistic Semantic Depth in the Hybrid Workspace

## Status

Final verdict: `INCONCLUSIVE`.

The experiment did not reach the human/product semantic-depth question because the generated child failed the trusted representation-admission gate before workspace rendering.

## What Passed

The realistic-source child pipeline progressed substantially further than earlier failures.

### Assertion extraction

- 9 grounded assertions;
- 9/9 exact unique evidence spans;
- 0 unknown participants;
- fidelity review: 8 `FAITHFUL`, 1 `PARTIAL`.

### Canonicalization

- 3 proposed relationships;
- 6 claims;
- 0 propositions;
- 0 uncompiled assertions;
- no unknown endpoints/roles;
- no entity minting;
- `KnowledgeModel` round-trip passed.

### Semantic review

- 2 relationships `SUPPORTED`;
- 1 relationship `OVERSTATED_CAUSALITY`.

The remaining semantic defect converted weaker “same pattern is seen” language into `CAUSES`.

## Where the Experiment Stopped

Structure detection produced only one hierarchy representation:

```text
wave-particle duality
        ↓
principle of complementarity
```

The requested focus `double-slit-experiment` was not represented.

Duplicate double-slit causal proposals collapsed to one logical edge, below the existing two-edge causal-path threshold.

Therefore the child failed the existing focus-preserving representation admission gate.

No trusted child artifact entered BASELINE-003.

## Why `INCONCLUSIVE` Is Correct

The intended product question was:

> Does deeper resolution inside BASELINE-003 help the learner understand a realistic quantum concept while preserving orientation?

That question was never tested.

The actual first blocker was:

```text
trusted-ish grounded semantic material
        ↓
structure detection / representation admission
        ↓
focus disappears
```

Therefore the result is not evidence that semantic depth is useless.

## New Bottleneck

Assertion-first compilation deliberately preserves much realistic-source meaning as assertions/claims rather than forcing it into binary graph edges.

The representation pipeline remains primarily relationship/structure driven.

This creates a mismatch:

```text
REALISTIC SEMANTIC COMPILER
relationships: few
claims/assertions: many

        ↓

REPRESENTATION COMPILER
primarily consumes canonical relationship structures
```

The semantic architecture is becoming safer while the representation layer is starved of usable explanatory structure.

## Important Distinction from SPEC-016

SPEC-016 showed that **displaying assertions directly as the UI** creates cognitive overload.

It did not prove that assertions are useless for representation construction.

Preserve the distinction:

```text
BAD
assertions → text cards → learner

UNTESTED
assertions → deterministic explanatory projection → learner
```

Assertions may be excellent representation inputs while remaining poor default visual objects.

## Do Not Tune Structure Thresholds to This Case

Do not simply lower the causal-path threshold from two edges to one in order to admit the double-slit child.

Reasons:

- one proposed causal edge was already semantically overstated;
- threshold tuning after observing this benchmark risks local overfitting;
- the deeper problem is that source meaning survives outside canonical graph topology.

## Next Hypothesis

Test whether grounded assertions can contribute to a focus-preserving explanatory representation without:

- becoming canonical semantic edges;
- being dumped as text cards;
- weakening semantic admission;
- introducing new ontology;
- calling another model.

The representation may contain two visually distinct semantic strengths:

```text
CANONICAL STRUCTURE
strong typed relationships/propositions

SOURCE-BACKED EXPLANATORY STRUCTURE
presentation-only composition grounded in assertions
```

The second must never masquerade as canonical truth.

## Frozen Regression Packet

SPEC-020 produced an unusually useful offline benchmark for the next experiment:

- focus: `double-slit-experiment`;
- 7 frozen child symbols;
- 9 grounded assertions;
- exact evidence spans;
- canonicalization proposal;
- independent semantic review;
- known overstated-causality defect;
- known failed representation admission;
- frozen BASELINE-003 shell.

No additional live call is needed to test the representation hypothesis.

## Decision

1. Close SPEC-020 as `INCONCLUSIVE`.
2. Do not retry the same probabilistic generation.
3. Do not lower structure thresholds merely to make this child render.
4. Preserve the generated semantic packet as a regression fixture.
5. Keep BASELINE-003 frozen.
6. Test assertion-aware **representation construction**, not assertion-heavy UI.
7. Keep the next experiment offline.
8. Preserve canonical vs explanatory semantic strength visibly and structurally.
9. Require the selected focus to survive in the explanatory representation.
10. Return to the SPEC-020 human semantic-depth question only if the offline representation gate succeeds.

## Recommended Next Experiment

`SPEC-021 — Focus-Preserving Explanatory Projection`

Primary question:

> Can the exact frozen SPEC-020 grounded semantic packet produce a truthful, cognitively useful representation centered on `double-slit-experiment` without inventing canonical semantics or exposing assertion prose as the overview?

## Final Conclusion

SPEC-020 did not fail because the realistic source contained no useful deeper meaning.

Most assertions grounded faithfully and most proposed canonical relationships were semantically supported.

The experiment exposed the next architectural seam: **truthworthy meaning that is intentionally too weak/rich for canonical graph edges still needs a disciplined path into representation.**
