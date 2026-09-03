# DEBRIEF-008 — Automatic Multi-Resolution Compilation

## Status

Accepted — mixed live outcome with one genuine source-grounded automatic resolution success and one correct fail-closed grounding rejection.

The experiment demonstrates that automatic multi-resolution compilation is possible in reality, but not yet reliably general across domains.

## Implementation

Primary implementation commit:

```text
467dabbf7d1051ed78699009816a43930a220d44
```

Live evaluation commit:

```text
570c16efcdfea3d7bc579a8686b01c196658a884
```

The implemented pipeline is:

```text
parent KnowledgeModel + validated focus
        ↓
deterministic source scope
        ↓
provider nomination
        ↓
exact quote → SourceSpan resolution
        ↓
child KnowledgeModel
        ↓
StructureDetector
        ↓
RepresentationBuilder
        ↓
deterministic layout
        ↓
generated exploration artifact
```

The parent semantic model remains immutable. Navigation state remains outside semantic IR. Maximum generated depth is exactly one. No recursive graph-of-graphs architecture was introduced.

## Primary Question

> Can Knowledge Compiler automatically derive one trustworthy deeper semantic resolution for selected concepts from source-grounded material, replacing the manually authored SPEC-007 child fixtures without losing provenance, semantic honesty, or useful abstraction change?

## Outcome

**Yes, once — and importantly, not by weakening validation.**

### Economics

Outcome:

```text
SUCCESS
```

The compiler generated:

- 11 child entities;
- 11 source-grounded relationships;
- 4 source-grounded claims;
- 10 detected structures;
- 2 representations;
- one selected contextual navigation representation containing 9 nodes and 8 source-grounded edges.

All 11 source relationships and all 4 source claims preserved validated source evidence.

Independent semantic review recorded:

- focus relevance: PASS;
- mechanistic/detail gain: PASS;
- relationship truthfulness: PASS_WITH_NOTE;
- source grounding: PASS;
- parent coherence: PASS.

The contextual viewer preserved parent context, Back navigation, exact evidence quotes/spans, and visibly identified the deeper layer as `Generated from source`.

### Software Architecture

Outcome:

```text
GROUNDING_FAILURE
```

The provider proposed an `INFERRED` claim while also attaching source evidence. The compiler rejected the complete child rather than relaxing provenance invariants.

No retry, hidden retry, favorable-run selection, or prompt mutation was performed.

This is a positive architectural result even though it is a failed product result: the probabilistic layer was not allowed to redefine the trust contract.

## Live Usage

```text
Software Architecture
input:  2,848
output: 1,213
total:  4,061

Economics
input:  3,073
output: 1,697
total:  4,770

Combined
8,831 tokens
```

Monetary cost remained `NOT_AVAILABLE` because the provider returned usage but not an authoritative charge and the evaluation deliberately did not substitute an unverified estimate.

## Source Scope

Both benchmark source documents were sufficiently small that the experiment used:

```text
FULL_DOCUMENT_SMALL_SOURCE
```

Software Architecture:

```text
characters 0–936
```

Economics:

```text
characters 0–785
```

No web retrieval or hidden enrichment was used.

## Human Review

The owner inspected the automatically generated Economics contextual layer and found that the observed structure almost exactly mirrored their own expectations for semantic exploration.

The critical finding is that the generated child is not merely “more information.” It forms a genuine higher-resolution explanatory neighborhood around `market price`.

The parent representation is substantially simpler:

```text
shortage → upward pressure → market price
                              ├→ quantity demanded
                              └→ quantity supplied
```

The generated child expands that concept into a richer causal neighborhood involving:

- demand elasticity;
- reduction in supply;
- surplus;
- downward pressure on price;
- market price;
- shortage;
- upward pressure on price;
- quantity demanded;
- quantity supplied.

The owner agreed that this corresponds to “peeling another layer” and that the parent concept can plausibly be treated as a higher-level compression of the child model.

## Key Finding — Resolution Is Explanatory, Not Merely Decompositional

SPEC-008 exposed an important semantic distinction.

A deeper model is not always “inside” a concept.

Different semantic object types may require different forms of higher resolution:

```text
SYSTEM
→ subsystems + interactions

OBJECT / COMPONENT
→ internal components

PROCESS
→ internal stages

VARIABLE
→ causal drivers + consequences

EVENT
→ antecedents + outcomes

CONCEPT
→ mechanisms + principles + relationships
```

For `market price`, the deeper resolution is naturally a **causal neighborhood**, not a literal decomposition.

Therefore:

> semantic zoom should mean increasing explanatory resolution, not universally decomposing a node into contained parts.

This becomes the highest-value architectural question for the next experiment.

## Key Finding — Knowledge Navigation Appears Naturally Two-Dimensional

During SPEC-008 review, the owner independently arrived at a map-like navigation model.

The emerging interface has two meaningful semantic dimensions:

```text
vertical
→ abstraction / semantic resolution

horizontal
→ conceptual neighborhood / topology
```

This suggests the default knowledge-navigation surface should remain 2D.

The effective third dimension is supplied by **semantic zoom**, not literal 3D graph rendering.

The working principle is:

> dimensionality follows semantic dimensionality, not visualization capability.

For abstract knowledge topology, use 2D + semantic zoom. Use 3D only where physical/spatial dimensionality itself carries explanatory information.

## Key Finding — Parent Context Should Become a Navigation Surface

The parent-context mini-map was originally passive orientation.

The owner’s natural next expectation is to use it actively, like a geographic map:

```text
Back
→ navigation history

Breadcrumb / path
→ ancestry

Context map
→ conceptual neighborhood

Explore / zoom
→ abstraction depth
```

This is not implemented by SPEC-008 and should not be retrofitted into it.

However, it is now a strong product-navigation hypothesis.

## Key Finding — Compile Resolution On Demand

Automatic recursive generation could explode combinatorially if the project attempted to precompute every possible child graph.

The more natural architecture may be demand-driven:

```text
coarse knowledge map
        ↓
learner explores concept
        ↓
compile local higher resolution
        ↓
validate + ground
        ↓
cache/preserve result
        ↓
render
```

This resembles map-tile generation more than eager recursive graph construction.

This is not yet an implemented architectural decision, but SPEC-008 gives it strong plausibility.

## Key Finding — Cognitive Presets and Semantic Resolution Are Orthogonal

SPEC-007 established the emerging preset idea:

```text
Overview
Focus
Contextual / Layers
```

SPEC-008 suggests these should consume the same underlying multi-resolution knowledge rather than generate different semantic truth.

Conceptually:

```text
trusted semantic knowledge
        ↓
multi-resolution compilation
        ↓
cognitive projection / preset
        ↓
learner
```

This preserves the distinction:

```text
WHAT IS KNOWN
≠
HOW I WANT TO THINK ABOUT IT
```

That remains the most promising route toward broader personalization without fragmenting factual truth.

## Architecture Findings

### ResolutionCompiler is a viable bounded boundary

The new experimental boundary successfully preserves:

- parent immutability;
- independent child semantic serialization;
- provider isolation;
- deterministic evidence resolution;
- canonical relationship semantics;
- deterministic downstream structure/representation/layout;
- navigation outside semantic IR.

### Child semantic truth should remain independently inspectable

The successful Economics child can be reviewed as semantic truth before rendering.

This validates the decision not to have the provider directly generate diagrams or viewer state.

### Fail-closed behavior remains non-negotiable

Software Architecture demonstrated that probabilistic output may violate provenance conventions even when the rest of the proposal looks plausible.

The project should continue rejecting such outputs rather than automatically repairing provenance unless a separate, explicit repair experiment proves safe.

## Product Findings

### Automatic multi-resolution compilation is demonstrated, not generalized

The correct claim is:

> Knowledge Compiler has produced one real, source-grounded, useful deeper semantic resolution automatically.

The incorrect claims would be:

- automatic semantic zoom now works reliably across domains;
- arbitrary recursion is solved;
- every source contains enough depth;
- every semantic object should use the same resolution strategy.

### Generated child usefulness is real in Economics

The owner did not view the Economics result as merely technically impressive. Its structure aligned closely with how they expected the concept to unfold cognitively.

### The handcrafted SPEC-007 fixture remains useful as an experimental reference, not ground truth

The generated Economics layer differs from the handcrafted child and is valuable precisely because it follows the source rather than reproducing our fixture.

## Deviations and Process Notes

### Truncated SPEC-008 file

The committed SPEC-008 document ended abruptly at:

```text
Report explicitly:
```

This was an authoring/write truncation error in the SPEC itself.

Codex correctly surfaced the defect rather than pretending a missing handoff section existed. The substantive experimental requirements before the truncation were sufficient to implement and evaluate the spike, and the handoff covered validation, complexity, artifacts, deviations, commit, and push.

This should be recorded as process debt, not silently forgotten.

### API-key preflight failure preserved

The initial evaluation with no `OPENAI_API_KEY` correctly recorded provider failures rather than fabricating generated artifacts. The later successful live run was committed separately.

### Consent before sending source material

Codex explicitly requested approval before sending the accepted benchmark source texts and parent metadata to the provider. This was a useful boundary and should remain the expected pattern when external transmission is not already clearly authorized.

## Decisions

### Accept SPEC-008

The experiment successfully answers the narrow question: automatic trustworthy multi-resolution compilation is possible in at least one real source/domain.

### Do not claim cross-domain reliability

One of two live domains failed grounding. Reliability remains an open problem.

### Keep fail-closed provenance enforcement

Do not weaken the `SOURCE` / `INFERRED` evidence contract to improve success rate.

### Keep child generation bounded to one level for now

Do not introduce arbitrary recursion yet.

### Treat semantic resolution as type/context-dependent explanatory refinement

Do not assume one universal decomposition strategy.

### Keep abstract knowledge navigation 2D + semantic zoom

Reserve literal 3D for subject matter whose third spatial dimension itself carries explanatory information.

### Preserve Back + ancestry path + context map + semantic zoom as distinct navigation concepts

Do not collapse these into one generic navigation control.

### Do not implement active context-map navigation yet

It is promising, but resolution semantics should be better understood first.

### Do not implement eager recursive compilation

On-demand local compilation is the stronger current hypothesis, but it remains to be tested explicitly.

## Highest-Value Next Question

> What should “zoom in” mean for different semantic object types, and can Knowledge Compiler choose or apply the right resolution strategy while preserving source grounding and parent-child compression coherence?

This question should come before active map navigation or recursive generation because both depend on the semantics of resolution.

## Recommended Next Experiment

### SPEC-009 — Semantic Resolution Strategy Spike

Primary question:

> Can the compiler generate meaningfully different, source-grounded higher-resolution models according to the semantic role of the selected focus — for example process → stages, variable → causal neighborhood, component → internals — without introducing a large ontology or brittle prompt branching?

Suggested scope:

- 2–3 semantic focus types;
- one level only;
- fixed source material;
- reuse `ResolutionCompiler`;
- explicit strategy metadata;
- compare generic “more detail” prompting against type-aware resolution instructions;
- evaluate parent-child compression coherence;
- preserve exact grounding;
- no active map navigation yet;
- no recursion;
- no personalization;
- no new cognitive preset implementation;
- no simulator.

## Operating-Model Learning

SPEC-008 reinforces the project’s preferred sequence:

```text
manual interaction fixture
        ↓
prove product behavior
        ↓
automate generation
        ↓
validate semantics + grounding
        ↓
human usefulness review
```

It also adds:

```text
probabilistic proposal
        ↓
strict deterministic trust boundary
        ↓
accept or fail closed
```

A failed provider output is useful experimental evidence when the system rejects it for the right reason.

## Final Conclusion

SPEC-008 is the first evidence that Knowledge Compiler can automatically compile **knowledge itself** at more than one semantic resolution.

The Economics result demonstrates the complete path from source to parent model to selected concept to generated child semantic truth to deterministic structure to representation to contextual navigation.

The next challenge is no longer whether semantic zoom can exist.

It is defining what semantic zoom **means** across different kinds of knowledge.
