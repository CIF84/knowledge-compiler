# DEBRIEF-016 — Assertion-Aware Representation

## Status

Product verdict: `NO_MEANINGFUL_IMPROVEMENT`.

Technical and semantic integrity may pass, but the learner-facing experiment failed cognitively.

## Primary Question

> Can Knowledge Compiler construct a cognitively useful orientation from trustworthy grounded assertions and claims without promoting them into stronger canonical graph relationships or weakening the semantic truth boundary?

## Owner's Spontaneous Review

The owner explored the viewer before reading implementation metrics or design rationale, as required.

Immediate reaction:

> “my brain immediately shut down.”

> “visuals are gone, page is extremely overloaded with text-rich information plus i don't understand architecture straightforwardly.”

> “it seems to work technically, but cognitively it's massive step back.”

> “my brain wanted to leave interface.”

This is treated as the decisive cognitive result.

## What Worked

The experiment appears to have solved the literal information-access problem:

- trustworthy assertions became visible;
- source-backed explanations remained distinguishable from established relationships;
- evidence remained inspectable;
- the interface exposed more of the accepted semantic material than the sparse SPEC-013 graph.

These are necessary but not sufficient conditions for Knowledge Compiler's product goal.

## What Failed

The interface largely converted trustworthy semantic material into a document/dashboard surface:

```text
concept list
+
concept cards
+
counts/chips
+
preview panel
+
relationship sections
+
source-backed explanation cards
+
long vertical scrolling
```

The learner must reconstruct the domain's structure mentally from textual items.

That reverses the core product thesis.

## Core Cognitive Failure

The overview does not immediately answer:

> **What is the shape of this domain?**

The screen exposes items rather than architecture.

The user's attention has no obvious spatial starting point or route.

The result is information accessibility without cognitive orientation.

## Key Lesson — Space Is Information

Earlier visual experiments succeeded because spatial arrangement itself carried meaning.

SPEC-016 largely discarded that primitive in favor of cards and prose.

A knowledge map should use geometry/topology to externalize relationships that the learner would otherwise need to reconstruct mentally.

If the learner must read many cards to infer the architecture, Knowledge Compiler has failed to perform the cognitive compression it exists to provide.

## Assertion Visibility Hypothesis Rejected

SPEC-016 implicitly tested:

> If trustworthy assertions cannot become canonical graph edges, make the assertions themselves visible as first-class overview objects.

The human result rejects that as a default-overview strategy.

Assertions may be important **evidence for constructing presentation topology** without themselves belonging visibly on the overview.

Their prose should usually remain latent until attention requests it.

## Progressive Disclosure Failure

SPEC-016 effectively exposed several semantic/cognitive resolutions at once:

```text
domain concepts
concept neighborhoods
relationship status
assertion summaries
source-backed explanations
source evidence
```

This is the opposite of the Google-Maps interaction model previously identified by the owner.

A better hierarchy is closer to:

```text
ZOOM 0 — domain shape
ZOOM 1 — major conceptual neighborhoods
ZOOM 2 — concepts + important relationships
ZOOM 3 — explanations/assertions
ZOOM 4 — source evidence
```

Information should be available but latent until the learner's attention asks for it.

## Two-Compiler Principle

The experiment reveals a useful architectural distinction:

```text
SOURCE
  ↓
SEMANTIC COMPILER
  ↓
truth-preserving knowledge
  ↓
COGNITIVE COMPILER
  ↓
attention-preserving representation
```

The semantic compiler asks:

> What can we safely claim?

The cognitive compiler asks:

> What should the human see right now?

These are different optimization problems and should remain separate.

## Product Principle Earned

> **Topology first. Text on demand.**

Corollary:

> The default surface should communicate structure before content.

This does not authorize fabricated semantic edges. Presentation topology must remain explicitly distinct from canonical semantic truth.

## Presentation Topology

Trusted assertion participation may support a weaker presentation-level topology such as:

```text
concepts that repeatedly participate in the same grounded assertions
→ presentation proximity / neighborhood
```

This does **not** mean:

```text
concept A → inferred canonical relationship → concept B
```

Presentation topology answers orientation questions, not semantic predicate questions.

It may determine:

- spatial proximity;
- neighborhood membership;
- visual prominence;
- focus transitions;
- what is initially hidden or revealed.

All such constructs must remain presentation metadata.

## Decision

1. Close SPEC-016 as `NO_MEANINGFUL_IMPROVEMENT`.
2. Record technical/semantic integrity separately from cognitive failure.
3. Preserve the owner's spontaneous negative reaction as primary human evidence.
4. Do not increase graph density by weakening semantic admission.
5. Do not expose assertion prose by default merely because it is trustworthy.
6. Restore spatial topology as the primary orientation primitive.
7. Keep text latent and reveal it on demand.
8. Separate semantic compilation from cognitive compilation.
9. Use the same trusted SPEC-013 material for the next experiment.
10. Keep the next experiment offline.

## Recommended Next Experiment

`SPEC-017 — Cognitive Topology Projection`

Primary question:

> Can deterministic presentation topology derived from trustworthy assertion participation make the domain's structure immediately perceptible while keeping explanation text latent and without inventing semantic relationships?

The next experiment should intentionally show **less**, not more.

## Final Conclusion

SPEC-016 proved that trustworthy information can still be cognitively unusable.

The problem is not lack of data. It is failure to compress that data into perceptible structure.

Knowledge Compiler should not behave like a source-backed document dashboard. Its distinctive value is to externalize the topology of complex information so the learner does not have to reconstruct that topology mentally.

**Topology first. Text on demand.**
