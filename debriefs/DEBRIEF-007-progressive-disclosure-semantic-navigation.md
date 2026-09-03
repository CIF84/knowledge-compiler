# DEBRIEF-007 — Progressive Disclosure and Semantic Navigation

## Status

Accepted — contextual semantic expansion is the clear conceptual winner for the target learner. Navigation grammar validated; current contextual visual implementation is not treated as final.

## Implementation

SPEC-007 implementation commit:

```text
8cc3be3c7e61b20b6e25a5aec12c07a6ea451a60
```

The implementation added a presentation-only `ExplorationFixture` boundary downstream of the existing semantic architecture. No `KnowledgeModel`, extraction, relationship grammar, or structure-detection redesign was introduced.

## Primary Question

> Can a learner move from a high-level model into a deeper local model while preserving enough parent context to remain oriented in the larger system?

## Outcome

**Yes — conceptually and strongly for the owner benchmark.**

The owner described their baseline learning preference as wanting an interface that helps them understand higher-level principles while being able to “peel different layers” while exploring a topic.

That preference led strongly to **C — Contextual semantic expansion** over both:

```text
A — BASELINE-001
    select concept → detail

B — Replacement drill-down
    parent disappears → child model

C — Contextual expansion
    parent context remains → child model
```

The owner explicitly noted that the current contextual implementation is not necessarily visually perfect, but that **conceptually it is the obvious choice** for how they want to learn.

This distinction matters. SPEC-007 validates the navigation/learning grammar, not the current pixel-level realization of contextual mode.

## Technical Result

SPEC-007 introduced two deterministic manually authored exploration fixtures:

### Software Architecture

`API component` expands into a five-node request-handling process:

```text
request arrival
    ↓
request parsing
    ↓
request validation
    ↓
order command creation
    ↓
order-component handoff
```

### Economics

`market price` expands into a five-node response mechanism covering buyer affordability/purchase plans and seller incentives/supply offers.

The fixture deliberately does not repair the known missing market feedback-closing edge.

### Provenance discipline

Fixture content is explicitly marked:

```text
EXPERIMENT_FIXTURE_AUTHORED
```

with `INFERRED` origins, fixture-prefixed relationship IDs, and no fabricated source spans.

This was the correct experimental compromise: test semantic-depth interaction before designing automatic multi-resolution compilation.

## Technical Verification

Reported automated result:

```text
101 passed in 0.23s
```

The committed machine evaluation records:

- 2/2 exploration fixtures valid;
- BASELINE, REPLACEMENT, and CONTEXTUAL modes available;
- return targets valid;
- parent selections restorable;
- child edge/control identity complete;
- canonical direction preserved;
- fixture provenance truthful;
- layouts deterministic;
- contextual parent/focus/child identities present;
- BASELINE-001 parent artifacts byte-preserved;
- no network or LLM calls.

Independent repository review confirmed the implementation is exactly one focused commit after the SPEC and remains downstream of the semantic IR.

## Human Review

### Core reaction

The owner did not frame the desired behavior as “show me more detail.”

They framed it as:

> understand higher-level principles, or peel different layers while exploring the topic.

This sharpens the product concept substantially.

The desired interaction is not ordinary progressive disclosure in the generic UI sense. It is **movement across levels of abstraction while preserving system context**.

### Why contextual mode wins

Replacement drill-down creates a cognitive transition roughly like:

```text
MODEL A
   ↓
MODEL B
```

The parent model must then be retained substantially in working memory.

Contextual expansion instead carries part of that orientation burden in the interface:

```text
PARENT MODEL
     │
[focus concept]
     │
   EXPLORE
     ↓
CHILD MODEL
```

while the parent identity and focus relationship remain perceptually available.

For the target learner, this corresponds much more closely to systems reasoning: understand the whole, inspect a constituent mechanism, move deeper, and retain the relationship to the larger system.

### “Peeling layers” is better product language

The owner’s phrase is more precise than generic “progressive disclosure.”

The relevant conceptual axis is:

```text
HIGH ABSTRACTION
    ↓
governing principles
    ↓
system
    ↓
subsystem
    ↓
mechanism
    ↓
interaction
    ↓
evidence / formal detail
LOW ABSTRACTION
```

Future work should think in terms of **semantic resolution / abstraction layers**, not merely hiding and revealing UI detail.

## New Product Insight — Cognitive Presets

During review, the owner made an additional important observation: successful prior interfaces should remain accessible rather than being overwritten by later experiments.

This produces a new distinction:

```text
EXPERIMENT HISTORY             COGNITIVE PRESETS
──────────────────             ─────────────────
BASELINE-001                   Overview
replacement experiment         Focus
contextual experiment          Contextual / Layers
future successful modes        future cognitive projections
```

These are not necessarily obsolete generations of one interface.

They may represent genuinely different ways a learner wants to interrogate the same underlying knowledge.

### Current candidate presets

| Preset | Cognitive purpose |
| --- | --- |
| Overview | Understand the landscape/system at a glance |
| Focus | Isolate one mechanism and remove surrounding distraction |
| Contextual / Layers | Peel abstraction layers while retaining system orientation |

The experimental labels `BASELINE`, `REPLACEMENT`, and `CONTEXTUAL` describe the experiment. The product-facing labels above describe learner intent and are therefore better candidates for future product vocabulary.

### Important constraint

Not every experimental UI should become a permanent preset.

A mode earns preservation only if it demonstrates a distinct cognitive purpose or meaningful user preference. Otherwise mode proliferation would increase cognitive load and product complexity.

## Hyper-Personalization Implication

The owner identified the larger implication immediately:

> preserving multiple cognitive presets could make Knowledge Compiler hyper-personalized for a broader audience.

This is a significant product hypothesis.

The project began from one learner’s mismatch with linear text. A single fixed “systems thinker UI” would solve that learner’s problem but might simply create a different mismatch for others.

Cognitive presets suggest a more general architecture:

```text
                TRUSTED KNOWLEDGE MODEL
                         │
                  REPRESENTATION
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
       OVERVIEW        FOCUS       CONTEXTUAL/LAYERS
          │              │              │
      landscape       isolate        preserve context
          └──────────────┼──────────────┘
                         ↓
                       learner
```

The underlying semantic truth remains stable while the **cognitive projection** can vary.

This potentially reframes personalization from:

> generate different factual content for different users

into:

> project the same trustworthy knowledge through the cognitive representation that best supports this learner and task.

That is a much more architecturally attractive form of personalization because it preserves semantic consistency and provenance.

## Key Findings

### 1. Semantic depth is useful when it preserves orientation

For the target learner, deeper content is not enough. The interface should carry the relationship between abstraction levels.

### 2. Selection and exploration remain distinct operations

The SPEC-007 distinction holds:

```text
SELECT
→ inspect this semantic object

EXPLORE
→ increase semantic resolution
```

This should remain part of the interaction grammar.

### 3. BASELINE-001 is not superseded

The successful overview representation remains useful as a cognitive mode and as an empirical comparison baseline.

Contextual semantic expansion extends it rather than invalidating it.

### 4. Replacement drill-down may still have a purpose

Although it loses the owner’s preferred context, removing surrounding information can be valuable when a learner already understands the parent system and wants concentrated attention on one mechanism.

Therefore it should not be deleted merely because Contextual won this experiment.

### 5. Interface variants may be cognitive projections, not versions

The project should stop assuming every successful interaction experiment creates a linear UI version chain.

Some successful modes may coexist because they optimize different cognitive tasks.

### 6. Personalization can occur downstream of semantic truth

A stable source-grounded knowledge model can potentially support multiple learner-specific representations without recompiling or altering factual semantics.

This is a powerful separation of concerns:

```text
WHAT IS KNOWN
    ≠
HOW I WANT TO THINK ABOUT IT
```

### 7. Automatic multi-resolution generation is now the main technical uncertainty

SPEC-007 deliberately cheated by manually authoring child models.

The navigation grammar worked conceptually. The next hard problem is therefore not more navigation UI; it is generating trustworthy abstraction layers automatically.

## Decisions

### Accept SPEC-007

Contextual semantic expansion is validated conceptually for the owner benchmark.

### Preserve all three experimental modes for now

Do not delete BASELINE, REPLACEMENT, or CONTEXTUAL behavior while the cognitive-preset concept is being explored.

### Adopt “peeling layers” / semantic resolution as product language

Use “progressive disclosure” as an implementation/design term where useful, but reason about the learner experience as movement across semantic resolution / abstraction layers.

### Treat cognitive preset as a product concept

Successful interaction grammars may become named cognitive presets when they serve distinct learner intents.

Current working concepts:

```text
Overview
Focus
Contextual / Layers
```

These names are provisional product vocabulary, not a request for immediate UI renaming.

### Preserve one semantic truth beneath presets

Presets should project the same trusted knowledge differently. They must not silently alter canonical relationship direction, provenance, or factual semantics.

### Do not build personalization machinery yet

The hyper-personalized Knowledge Compiler is a promising product direction, but no user profile, recommendation engine, adaptive UI, account system, or preset-learning mechanism is justified yet.

First prove that trustworthy multi-resolution knowledge can be generated automatically.

### Do not create BASELINE-002 yet

The contextual navigation grammar is validated, but the owner explicitly noted that its current visual implementation is not necessarily perfect. BASELINE-001 remains the current empirical visual/interaction baseline.

## Architectural Implication

The emerging stack can now be expressed as:

```text
SOURCE
  ↓
KnowledgeModel                 semantic truth
  ↓
DetectedStructureSet           higher-order structure
  ↓
RepresentationModel            presentation-ready structure
  ↓
Multi-resolution model?        next uncertainty
  ↓
Cognitive preset               Overview / Focus / Layers / future
  ↓
Viewer interaction
  ↓
Learner
```

The `Multi-resolution model?` line is deliberately unresolved. SPEC-007 does **not** establish the correct architecture for automatic abstraction layers.

## Highest-Value Next Question

> Can Knowledge Compiler automatically derive a small, trustworthy set of useful abstraction layers from source-grounded knowledge, such that a concept can be explored at higher resolution without manually authored child fixtures?

This is the next major technical/product uncertainty.

The challenge is not merely recursive graph expansion. A useful abstraction layer must change **semantic resolution**, not simply add more nodes or words.

Questions include:

- What makes two representations different abstraction levels rather than different subsets?
- How should a high-level concept map to a lower-level mechanism?
- How many levels are useful before navigation becomes arbitrary?
- Can levels be derived from one source document, or do deeper levels require external knowledge?
- How should evidence/provenance survive across abstraction levels?
- How should missing evidence limit expansion?
- Should layer generation be probabilistic while validation remains deterministic?
- How do we prevent hallucinated decomposition?
- How should a child model summarize back into its parent concept?

## Recommended Next Experiment

### SPEC-008 — Automatic Multi-Resolution Compilation Spike

Primary question:

> Can the compiler generate one trustworthy child resolution for selected concepts from existing source-grounded material, replacing the manually authored SPEC-007 fixtures while preserving the validated semantic-navigation grammar?

The first experiment should remain narrow:

- one or two domains;
- one parent → child transition each;
- fixed source material;
- compare generated child model against SPEC-007 handcrafted fixture and source evidence;
- no arbitrary recursion;
- no external web retrieval unless the experiment explicitly tests source insufficiency;
- no personalization engine;
- no new cognitive preset implementation;
- no simulator;
- preserve BASELINE-001 and all successful experimental modes.

## Operating-Model Finding

SPEC-007 reinforces a useful project pattern:

```text
product interaction hypothesis
        ↓
manual/fixed semantic fixture
        ↓
human test
        ↓
if useful
        ↓
earn the right to automate/generate it
```

This avoids building expensive generalized architecture for an interaction that may not help the learner.

The same principle should govern multi-resolution compilation.

## Final Conclusion

SPEC-007 changes the product thesis in two important ways.

First, Knowledge Compiler should not merely turn text into a visual model. It should allow the learner to **peel semantic layers while retaining orientation in the whole**.

Second, there may not be one ideal interface. Overview, Focus, Contextual/Layers, and future validated modes may be different **cognitive projections of the same trusted knowledge**.

That opens a path from a tool optimized for one systems thinker toward a potentially broader, hyper-personalized Knowledge Compiler — without sacrificing a common semantic truth layer.
