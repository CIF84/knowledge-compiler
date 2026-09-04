# DEBRIEF-015 — Semantic Compression Adequacy

## Status

Accepted positive exploratory result: `COMPRESSION_JUDGE_BETTER`.

## Result

One blinded independent semantic-compression judge call over the frozen 10-case benchmark achieved:

```text
true adequate admits: 4
false adequate admits: 0
true inadequate rejects: 5
false inadequate rejects: 1
adequate-admission precision: 100%
adequate-admission recall: 80%
negative rejection rate: 100%
overall agreement: 90%
```

The judge rejected all five historically known lossy binary compressions and caught the SPEC-014 Pauli false admit.

It falsely rejected one accepted relationship:

```text
correspondence-principle CONSTRAINS quantum-mechanics
```

## Cost

One `gpt-5.6-luna` call:

```text
input: 2,878 tokens
output: 1,360 tokens
total: 4,238 tokens
runtime: 16.754 seconds
```

No retry, repair, enrichment, second judge, rewriting, or deliberation occurred.

## Validated Finding

A narrowly scoped independent judge can distinguish faithful from lossy binary semantic compression on this small frozen historical benchmark substantially better than trivial blanket rejection.

The experiment strengthens the current strategy:

> Prefer bounded independent semantic decisions before broad multi-agent deliberation.

Broad multi-agent deliberation remains unjustified by current evidence.

## Error Asymmetry

SPEC-015 produced:

```text
false admits: 0
false rejects: 1
```

For a trust-oriented knowledge compiler, this is the safer error direction: false rejection reduces topology; false admission can make topology wrong.

This does not justify unlimited conservatism, but it is preferable to the earlier realistic-source failure pattern.

## Residual Error — Contextual vs Constitutive Omission

The sole false rejection appears to confuse contextual qualification with propositionally essential content.

Accepted relationship:

```text
correspondence principle
        ↓ CONSTRAINS
quantum mechanics
```

The assertion contains classical-limit context describing how/when the correspondence constraint applies.

Omitting that context makes the edge less qualified but does not necessarily make the binary proposition false.

Contrast the rejected demand case:

```text
quantity demanded
        ↓ CAUSES
shortage
```

where quantity supplied and the condition `demand > supply` are constitutive of the causal proposition. Removing them changes what the source asserts.

This suggests a useful distinction:

```text
CONTEXTUAL OMISSION
omitted material qualifies a relationship
but the binary core remains faithful

CONSTITUTIVE OMISSION
omitted material is necessary for the proposition
and the binary edge changes the meaning
```

This distinction is worth preserving as an observed residual, but the current benchmark is too small to justify another semantic mechanism immediately.

## Stop Condition on Semantic Micro-Optimization

SPEC-011 through SPEC-015 progressively addressed:

```text
dangling symbols
→ staged symbol discovery

premature predicate commitment
→ assertion-first compilation

semantic overcommitment
→ independent admission gate

lossy binary compression
→ semantic-compression judge
```

At this point further tuning against a 10-case historical packet risks local overfitting and diminishing information gain.

Do not create another semantic gate solely to solve the correspondence-principle miss.

Collect broader realistic-source evidence before revisiting production semantic admission.

## Production Integration Decision

Do not integrate SPEC-014 or SPEC-015 gates into the default production pipeline yet.

Reasons:

- tiny historical benchmark;
- correlated cases;
- heterogeneous source domains/review vintages;
- no second realistic-source prospective validation;
- no production threshold established.

The experimental seams remain valuable architecture candidates.

## Downstream Bottleneck Reopened

SPEC-013 produced the first trusted realistic-source parent, but current representation consumed only a tiny fraction of its trustworthy knowledge:

```text
41 symbols
24 grounded assertions
21 claims
3 canonical relationships
        ↓
current representation
        ↓
2 represented entities
1 sparse edge
```

The semantic system became conservative enough to preserve truth, exposing a downstream limitation:

> Most trustworthy knowledge is not currently visible in the cognitive map because representation is graph-edge-centric.

This is now a higher-value uncertainty than another semantic micro-gate.

## Recommended Next Experiment

Test **assertion-aware knowledge representation** using the already accepted SPEC-013 artifacts, preferably offline.

Primary question:

> Can Knowledge Compiler construct a cognitively useful orientation from grounded assertions and claims without pretending those assertions are stronger canonical graph relationships?

The semantic truth layer must remain unchanged.

The representation layer may project different confidence/semantic-strength forms visually, but it must not silently promote claims/assertions into canonical relationships.

## Decisions

1. Accept SPEC-015 as `COMPRESSION_JUDGE_BETTER`.
2. Record zero false admits and one conservative false reject on the frozen packet.
3. Preserve contextual-vs-constitutive omission as a residual semantic distinction.
4. Do not tune another semantic judge against this packet.
5. Defer broad multi-agent deliberation.
6. Do not production-integrate experimental gates yet.
7. Return Phase II attention downstream to representation.
8. Use trusted SPEC-013 artifacts as the next offline benchmark.
9. Resume the original learning-product question: can the trustworthy quantum knowledge actually be made useful to a learner?

## Repository Evidence

Implementation commit:

```text
5265c26ba3795e9b5ad3cad010119977e7e01671
```

Evaluation commit:

```text
d65b94901b42f1027210c02b977c873bf68d6660
```

Offline suite:

```text
196 passed
```

## Final Conclusion

SPEC-015 demonstrates that a small, independent, compression-specific semantic decision can catch all tested known lossy binary canonicalizations while preserving most legitimate relationships.

That is enough evidence to keep multi-agent deliberation deferred, but not enough to justify production integration.

The project should now stop optimizing semantics against this small packet and address the more important downstream problem exposed by semantic conservatism: trustworthy assertions and claims need a useful cognitive projection.
