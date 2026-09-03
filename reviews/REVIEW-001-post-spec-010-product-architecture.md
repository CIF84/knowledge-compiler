# REVIEW-001 — Knowledge Compiler After SPEC-010

## Status

Decision review. No product implementation authorized by this document.

## Why Review Now

SPEC-001 through SPEC-010 have moved Knowledge Compiler well beyond its original JSON-first experiment. The project now contains validated semantic, representation, interaction, and multi-resolution primitives.

The main risk has changed from **“can this idea work?”** to **“which uncertainty should we attack next?”**

A linear continuation into SPEC-011 without reconstructing the whole system risks local optimization.

## Original Thesis

The original product question was:

> What underlying structure is this information describing, and what representation makes that structure easiest to understand?

North star:

> **Paste difficult text. Get a model you can think with.**

That thesis has survived, but the project has discovered a richer version:

> **Compile source-grounded information into a navigable, multi-resolution knowledge space whose cognitive projection can adapt to how the learner wants to think.**

## What Has Been Demonstrated

### 1. Source-grounded semantic extraction

A provider-independent semantic pipeline can transform explanatory text into typed entities, claims, relationships, evidence spans, and uncertainty/origin metadata.

Exact source grounding is resolved by trusted code rather than trusted provider offsets.

### 2. Canonical relationship semantics

A bounded relationship vocabulary with explicit direction/meaning contracts materially improves semantic consistency.

The project learned that schema validity alone does not guarantee semantic truthfulness.

### 3. Higher-order structure detection

Deterministic downstream composition can identify useful hierarchies, causal paths, process chains, dependency chains, and feedback candidates without repairing upstream semantic defects.

### 4. Useful representation

The same semantic IR can produce inspectable representations with complete provenance.

Biology's truthful empty state demonstrated that absence is preferable to fabricated structure.

### 5. Structure-aware interactive UI

SPEC-006 established a strong empirical interaction baseline:

```text
structure visible at a glance
+
structure-specific deterministic spatial grammar
+
click = persistent semantic selection
+
hover = temporary preview
+
edge/control/detail/evidence behave as one semantic object
```

The owner described the result as something they would genuinely want to learn with.

### 6. Semantic zoom / contextual layers

SPEC-007 showed that the target learner strongly prefers peeling semantic layers while retaining parent context over conventional replacement drill-down.

This produced the map-navigation product metaphor.

### 7. Automatic multi-resolution compilation

SPEC-008 demonstrated one real source-grounded automatic parent→child semantic-resolution transition in Economics and correct fail-closed behavior elsewhere.

This proved that multi-resolution knowledge can be compiled rather than only handcrafted.

### 8. Role-dependent resolution

SPEC-009 positively validated `PROCESS → STAGES` for the owner benchmark and showed that resolution strategy should depend on what kind of semantic object is being explored.

The current strategy registry is experimental, not a universal ontology.

### 9. Richer proposition truth

SPEC-010 demonstrated that ordinary binary edges should remain the default, but compound conditions and role-rich events need structured propositions when binary representation loses truth.

The hybrid semantic model solved two real endpoint/proposition failures without universal ontology expansion.

### 10. Development operating system

OPS-001 introduced persistent `AGENTS.md` context, lazy historical loading, canonical Git expectations, and cleaner role separation.

The first observed run materially reduced repetitive bootstrap reasoning.

## Emerging Product Model

The project can now be understood as several orthogonal dimensions rather than one graph pipeline.

### Semantic truth

```text
SOURCE
  ↓
entities / relationships / claims
  ↓
structured propositions where required
  ↓
source provenance
```

### Structural projection

```text
semantic truth
  ↓
hierarchy / causal / dependency / process / feedback
```

### Semantic resolution

```text
high abstraction
      ↕
semantic zoom
      ↕
fine explanatory resolution
```

### Cognitive projection

```text
same trusted knowledge
      ↓
Overview / Focus / Contextual-Layers / future validated modes
```

### Navigation

```text
horizontal movement
→ conceptual topology / neighboring concepts

vertical movement
→ abstraction / semantic resolution

history
→ Back

ancestry
→ path / breadcrumb
```

These dimensions should remain separated architecturally where practical.

## Map Metaphor

The Google-Maps analogy has become architectural rather than decorative:

| Geographic map | Knowledge Compiler |
| --- | --- |
| pan | move across concepts |
| zoom in | increase explanatory resolution |
| zoom out | increase abstraction |
| current location | current focus |
| map topology | conceptual topology |
| history/back | navigation history |
| map layers | cognitive projections/presets |
| tiles | potentially on-demand compiled local knowledge |

The default abstract surface should remain **2D topology + semantic zoom**.

3D is reserved for subjects where physical/spatial dimensionality itself carries explanatory meaning.

## Personalization Thesis

The project began from one systems thinker's mismatch with linear text.

The cognitive-preset discovery offers a path to broader personalization without personalizing factual truth:

```text
              SAME GROUNDED KNOWLEDGE
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Overview       Focus      Contextual
          │            │            │
       learner A    learner B    learner/task C
```

The important separation is:

```text
WHAT IS KNOWN
      ≠
HOW I WANT TO THINK ABOUT IT
```

No personalization engine is yet justified.

## What Is Still Weak or Unproven

### A. Generalization across real source material

Most experiments still use small fixed benchmark texts. The system has not yet demonstrated robust behavior on realistic long-form inputs such as a substantial Wikipedia article, textbook chapter, paper, transcript, or documentation page.

### B. Automatic semantic-resolution policy

`PROCESS_STAGES` has positive evidence. Variable causal neighborhood is not validated. Component internals has only safe-refusal evidence.

The system cannot yet reliably decide what “zoom in” should mean for arbitrary semantic objects.

### C. Proposition topology

Structured propositions preserve truth but currently sit outside higher-order graph traversal. The product has not proven whether propositions need first-class topology or can remain explanatory semantic objects.

### D. On-demand depth

The project has demonstrated one generated child level, not recursive/local compilation across an exploration session.

### E. Active map navigation

The parent context map remains largely passive. The owner repeatedly finds `Explore` / `Back` scaffolding inelegant and wants map-like lateral movement plus semantic zoom.

### F. Learning efficacy beyond owner intuition

The owner has strong positive cognitive reaction to the interface, which is valuable product evidence, but the project has not measured comprehension, recall, mechanism explanation, transfer, or time-to-understanding against source text or conventional AI summaries.

### G. Input product surface

The original end-user workflow — paste or provide real material and compile it — is still less mature than the internal evaluation/viewer tooling.

## Candidate Next Directions

### Option 1 — Active Knowledge Map Navigation

Build the interaction the owner already wants:

```text
click neighbor → move laterally
zoom concept → deeper resolution
zoom parent → higher abstraction
breadcrumb → ancestry
back → history
```

**Value:** high experiential/product value; makes current capabilities feel like one coherent product.

**Risk:** could optimize navigation before general source compilation is robust.

### Option 2 — Real-Source Vertical Slice

Take one realistic long-form source, normalize it, compile it, generate a useful overview, allow at least one semantic zoom, preserve evidence, and navigate it in the current UI.

Possible benchmark: one carefully chosen Wikipedia article or equivalent committed source fixture.

**Value:** tests whether the accumulated architecture works outside tiny laboratory texts.

**Risk:** failures may span ingestion, extraction, abstraction selection, proposition modeling, structure detection, and UI simultaneously.

### Option 3 — Proposition-Aware Topology

Allow structured propositions to participate in graph/structure representations without flattening them.

**Value:** improves semantic fidelity of maps.

**Risk:** no current evidence that this is the highest-value learner bottleneck; could become graph-engine work.

### Option 4 — On-Demand Local Compilation

Compile deeper resolution only when the learner zooms into a concept; cache validated results and grow the explored knowledge space incrementally.

**Value:** aligns with map-tile architecture and avoids eager combinatorial graph expansion.

**Risk:** depends on reliable semantic-resolution strategy and introduces session/cache/navigation complexity.

### Option 5 — Learning Evaluation

Compare source vs summary vs Knowledge Compiler on one difficult topic.

**Value:** directly tests product value rather than architecture.

**Risk:** current end-user flow may still be too experimental to evaluate fairly.

### Option 6 — Cognitive Presets

Formalize Overview / Focus / Contextual as stable user-facing projections and test preference by task/learner.

**Value:** advances broader personalization thesis.

**Risk:** premature before a broader audience and realistic source workflow exist.

## Recommended Next Phase

### Recommendation: Real-Source Vertical Slice before another deep architecture expansion

The project has enough internal machinery.

The highest-information question now is increasingly:

> **Does the complete accumulated system produce a compelling learning experience on realistic source material?**

A real-source vertical slice would exercise, together:

```text
real source
  ↓
normalization
  ↓
semantic extraction + propositions
  ↓
structure detection
  ↓
minimal useful overview
  ↓
representation/layout
  ↓
contextual semantic zoom
  ↓
source evidence
```

This should be intentionally bounded to one source and one or two zoom interactions.

Do not add podcast/PDF/video ingestion yet. Use plain text from a realistic source so the experiment isolates **scale and semantic richness**, not adapter engineering.

### Why not map navigation first?

The navigation direction is already strongly preferred by the owner. Another UI experiment would likely confirm a known preference while leaving generalization risk untouched.

### Why not proposition topology first?

SPEC-010 solved the concrete truth-loss cases. Topological integration has not yet been shown to block understanding.

### Why not recursion first?

Recursive depth multiplies the cost of any remaining semantic-resolution weakness. First prove one realistic source works coherently.

### Why not formal learning evaluation first?

The product should first survive a realistic source end-to-end. Then a comparative learning test becomes much more meaningful.

## Proposed Next Experiment

Working title:

```text
SPEC-011 — Real-Source End-to-End Learning Slice
```

Primary question:

> Can Knowledge Compiler transform one realistic, substantially richer plain-text source into a trustworthy, useful overview with at least one automatically generated deeper semantic resolution that the owner would prefer to learn from over the original source alone?

Hold back:

- new input adapters;
- active map-navigation redesign;
- recursive unlimited depth;
- personalization engine;
- proposition ontology expansion;
- simulator;
- database/persistence.

## Repository Hygiene Gate

Before SPEC-011 implementation, resolve the long-lived local README/ROADMAP edits so the preferred invariant becomes:

```text
local main == origin/main
working tree clean
active contract exists
```

Do not destroy or silently canonicalize those edits. Inspect them first and decide whether they are:

1. current product thinking → merge/commit deliberately;
2. useful unfinished copy → preserve on a WIP branch;
3. obsolete → discard only with owner approval.

## Decision Summary

The project should temporarily stop expanding architecture and test the **whole compiled learning experience** against realistic information.

If the vertical slice succeeds, active map navigation and on-demand compilation become much more justified.

If it fails, the failure location will tell us which layer deserves the next architecture experiment.
