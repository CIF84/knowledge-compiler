# DEBRIEF-013 — Assertion-First Semantic Compilation

## Status

Accepted positive result.

Final experiment verdict:

```text
ASSERTION_FIRST_BETTER
```

SPEC-013 is the strongest Phase-II semantic-reliability result so far. It produced the first trusted parent `KnowledgeModel` from the frozen realistic quantum benchmark while materially improving reviewed canonical semantic precision over SPEC-012.

## Benchmark

Frozen source:

- Wikipedia — `Introduction to quantum mechanics`
- revision `1359567407`
- 5,965 words / 39,735 characters
- normalized source SHA-256: `9e978db999ee67134d347f91fe9f32934c982f4de9b496e4bf664cb00cce23ea`

Frozen symbol table:

- 41 symbols
- reused byte-for-byte from SPEC-012
- SHA-256: `07e79ff8e0d59c62ef181fe4ca7cec7aec9fcd32452b3c734c99482d288aaa08`

## Architecture Validated

SPEC-013 inserted a neutral, source-grounded assertion boundary between symbol discovery and canonical semantic commitment:

```text
SOURCE
  ↓
FROZEN SYMBOL TABLE
  ↓
SOURCE ASSERTIONS
  ↓
exact grounding
  ↓
CANONICAL NORMALIZATION
  ├── relationship
  ├── existing structured proposition
  ├── claim
  └── explicit uncompiled assertion
  ↓
KnowledgeModel
```

This separates two tasks that SPEC-012 performed simultaneously:

```text
WHAT DOES THE SOURCE ASSERT?
             ≠
HOW SHOULD THAT ASSERTION BE REPRESENTED CANONICALLY?
```

## SourceAssertion Boundary

A `SourceAssertion` preserves:

- deterministic identity;
- neutral statement;
- frozen participant IDs;
- resolved source evidence;
- `SOURCE` origin.

It cannot:

- select canonical relationship predicates;
- create entities;
- bypass frozen symbols;
- fabricate evidence;
- force a binary graph representation.

Trusted code resolves evidence and assigns deterministic IDs.

## Live Experiment

Provider/model:

```text
OpenAI Responses API
gpt-5.6-luna
```

Calls:

```text
Call 1 — assertion extraction
Call 2 — canonical normalization
```

No symbol-discovery call was required because the SPEC-012 symbol table was reused exactly.

No retries, enrichment, prompt repair, child-resolution calls, or hidden repairs occurred.

## Assertion Extraction Result

Produced:

```text
24 grounded assertions
24 SOURCE
0 INFERRED
```

Evidence:

```text
25/25 exact
25/25 unique
0 missing
0 ambiguous
0 unknown participants
```

Independent assertion-fidelity review:

```text
17 FAITHFUL
7 PARTIAL
0 DISTORTED
0 UNSUPPORTED
```

Strictly faithful rate:

```text
70.83%
```

The seven partial assertions exposed participant/evidence-scope imperfections, but none became misleading canonical graph edges.

## Canonical Normalization Result

The 24 grounded assertions were normalized into:

```text
3 relationships
0 structured propositions
21 claims
0 uncompiled assertions
```

All assertions received exactly one disposition.

The key behavioral change is conservative semantic commitment:

```text
source meaning preserved
        ↓
strong canonical graph semantics admitted only when justified
```

Claims became an important semantic safety tier rather than merely secondary output.

## Canonical Precision

All three admitted canonical relationships were independently reviewed as:

```text
SUPPORTED
precise endpoints
precise predicates
```

Reviewed canonical relationship precision:

```text
3 / 3 = 100%
```

Control comparison:

```text
SPEC-012 rejected proposal: 6 / 16 supported = 37.5%
SPEC-013 admitted graph:    3 / 3 supported = 100%
```

Do not interpret this as a universal 100% production-quality claim. The benchmark is one source and the admitted graph is deliberately sparse.

## Known SPEC-012 Defects

All six tracked SPEC-012 semantic defects were prevented from becoming misleading graph edges.

Instead, source meaning was retained at lower semantic commitment where necessary, primarily as claims.

This validates the core hypothesis behind REVIEW-002:

> Preserve source assertions before canonicalizing them.

## Important New Semantic Hierarchy

SPEC-013 makes the effective trust hierarchy clearer:

```text
RELATIONSHIP
→ strongest simple canonical commitment

STRUCTURED PROPOSITION
→ stronger multi-part canonical commitment

CLAIM
→ grounded source meaning preserved without unjustified topology

UNCOMPILED ASSERTION
→ grounded meaning preserved when no current KnowledgeModel form is safe
```

The project should protect this conservative admission behavior.

Do not react to graph sparsity by lowering the semantic admission threshold.

## Remaining Assertion-Stage Weaknesses

Independent review identified seven partial assertions, including:

- participant over-attribution;
- omitted measurement trigger;
- evidence-scope mismatch.

These matter because assertion fidelity is upstream of canonical normalization.

However, SPEC-013 demonstrated that conservative normalization prevented these weaknesses from becoming incorrect graph topology.

## Downstream Result

A trusted parent now exists.

Downstream diagnostics produced only:

```text
41 frozen symbols
2 represented entities
1 sparse hierarchy edge
```

This is semantically encouraging but cognitively inadequate.

The project has therefore moved the dominant bottleneck downstream:

```text
SPEC-011
could not produce valid parent

SPEC-012
could not produce trusted parent

SPEC-013
trusted parent exists
        ↓
representation is now too sparse
```

Do not solve sparsity by weakening canonical semantics.

## Architectural Conclusion

The trusted semantic pipeline is increasingly compiler-like:

```text
SOURCE
  ↓
SYMBOL SPACE
  ↓
GROUNDED ASSERTIONS
  ↓
SEMANTIC COMPILATION
  ↓
TRUSTED KNOWLEDGE MODEL
```

The provider is best understood as a probabilistic proposal mechanism inside deterministic trust boundaries.

## Multi-Agent / Deliberation Decision

After SPEC-013, broad multi-agent semantic deliberation is not yet justified as the cheapest reliability mechanism.

The next credible discriminator is narrower:

> Add an independent semantic admission gate after canonical normalization and test whether it catches unjustified semantic commitments without excessive rejection of correct ones.

This is cheaper and experimentally cleaner than multi-agent deliberation.

## Recommended Next Reliability Experiment

Working title:

```text
SPEC-014 — Independent Semantic Admission Gate
```

Primary question:

> Does a single independent semantic admission gate materially improve realistic-source canonical semantic reliability over assertion-first normalization alone, without excessive false rejection, weakened grounding, or disproportionate cost?

Candidate flow:

```text
GROUNDED ASSERTION
      ↓
CANDIDATE CANONICALIZATION
      ↓
INDEPENDENT SEMANTIC GATE
      ├── admit
      └── demote / reject canonical commitment
```

The gate must not rewrite source meaning or generate replacement semantics during the primary experiment.

## Why This Before Multi-Agent Deliberation

Multi-agent deliberation introduces many variables:

```text
agent count
roles
turn protocol
stopping rule
aggregation
shared-context effects
```

An independent gate changes one variable and directly tests whether remaining semantic overcommitment is externally detectable.

Escalate toward multi-agent deliberation only if a simple independent gate demonstrably helps but leaves ambiguous/disputed cases unresolved.

## Representation Frontier

SPEC-013 also establishes an important downstream research question:

> How can Knowledge Compiler build a cognitively useful orientation from trustworthy claims/assertions without pretending they are canonical graph edges?

This likely motivates a later assertion-aware representation experiment.

However, semantic admission reliability should be tested first while the accepted SPEC-013 benchmark artifacts provide a clean control.

## Decisions

1. Accept `ASSERTION_FIRST_BETTER`.
2. Preserve assertion-first compilation as the current leading realistic-source semantic architecture.
3. Preserve conservative graph admission.
4. Treat claims as a first-class semantic safety tier.
5. Do not loosen semantic admission to increase graph density.
6. Do not expand predicates or proposition ontology from this result.
7. Do not introduce multi-agent deliberation yet.
8. Test one independent semantic admission gate first.
9. Keep the frozen quantum benchmark and accepted SPEC-013 artifacts as controls.
10. Revisit assertion-aware representation after the reliability discriminator.

## Repository Evidence

Implementation commit:

```text
a083e08868b7c05ed9b7f09f1999e9f792589bd9
```

Evaluation commit:

```text
d23a03859e2fa9fcb9ca8ed6efda2be48397e98d
```

Offline suite:

```text
172 passed
```

## Final Conclusion

SPEC-013 demonstrates that realistic-source semantic reliability improves materially when Knowledge Compiler first preserves grounded source assertions and only then decides what semantic commitment is justified.

The remaining question is no longer whether source prose should be compiled directly into graph grammar. It should not.

The next question is whether an **independent admission decision** can cheaply make already-conservative canonicalization even more trustworthy before the project invests in broader multi-agent deliberation.
