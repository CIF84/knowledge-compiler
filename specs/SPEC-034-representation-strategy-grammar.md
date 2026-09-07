# SPEC-034 — Representation Strategy Grammar

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can Knowledge Compiler deterministically translate different kinds of trusted semantic structure into genuinely different learner-facing representation forms, choosing the form because it fits the structure of the knowledge rather than because every selected object is rendered as prose or a diagram?

## Owner evidence entering this packet

Owner review of the canonical revealed-knowledge navigation candidate indicates that the navigation architecture now behaves substantially as intended:

```text
MY MAP
→ revealed knowledge territory

WHAT DOES THIS MEAN?
→ focused learner-facing translation

EXPLORE NEXT
→ trusted frontier
```

The left pane is no longer the main product bottleneck. It is sufficiently useful to act as the navigation shell for the next learning experiment.

The newly exposed weakness is the focused learning surface. Many selected concepts currently resolve to little more than a title, one-sentence verbal description, and provenance. A few relationships receive a useful source → predicate → target representation, but the system does not yet demonstrate a general translation mechanism that selects among meaningfully different explanatory forms.

This packet therefore returns to the original product thesis established by SPEC-005/SPEC-006 and the role separation established by SPEC-030.

## Guiding principle

> **Representation strategy must not equal diagram.**

The representation should fit the information structure and the learner's immediate understanding problem.

Depending on trusted semantic structure, the best representation may be:

- a causal/mechanism view;
- a process or sequence;
- a hierarchy / composition view;
- a compare/contrast view;
- a worked example;
- a focused relationship view;
- a concise prose explanation;
- a small local explanatory diagram;
- or another deliberately bounded form justified by existing trusted structure.

The point of SPEC-034 is not to implement every possible pedagogical representation. It is to prove that **representation choice is a first-class deterministic architectural decision** rather than an accidental consequence of whichever renderer already exists.

## Product model to preserve

```text
canonical knowledge
        ↓
revealed navigation state ─────────────→ MY MAP
        ↓
selected canonical semantic object
        ↓
trusted local explanatory context
        ↓
REPRESENTATION STRATEGY RESOLVER
        ↓
learner-facing representation payload
        ↓
WHAT DOES THIS MEAN?
```

`EXPLORE NEXT` remains a frontier/revelation mechanism and is not part of representation selection.

Navigation and explanation are now intentionally weakly coupled:

```text
MY MAP
answers: where can I return / what have I uncovered?

WHAT DOES THIS MEAN?
answers: how should I understand the thing I selected?
```

Do not reintroduce map ↔ explanation visual mirroring.

## Required prior context

Before implementation, inspect only the material necessary to preserve the accepted seams:

- `specs/SPEC-005-minimal-representation.md`;
- `specs/SPEC-006-structure-aware-layout-and-synchronized-interaction.md`;
- `specs/SPEC-030-distinct-learning-surface-representation.md`;
- `debriefs/DEBRIEF-030-distinct-learning-surface-representation.md`;
- the current canonical revealed-knowledge implementation and its focused-learning renderer/resolver;
- current representation models/builders and relevant tests.

Do not broadly reread project history unless a concrete ambiguity requires it.

## Experimental control

Hold constant:

- canonical semantic facts;
- trusted relationship vocabulary;
- grounding and provenance;
- fail-closed behavior;
- reciprocal/multi-edge semantic identity;
- revealed-knowledge navigation architecture;
- collapse/expand and current-focus behavior;
- `Explore next` frontier semantics;
- existing recursive/depth semantics;
- source material and accepted deterministic fixtures.

Change only what is required to introduce and demonstrate a richer representation-strategy layer in the focused learning surface.

Do not make navigation more complex to support this experiment.

## Representation architecture

Introduce or strengthen an explicit seam conceptually equivalent to:

```text
RepresentationContext
    semantic_object
    semantic_class
    trusted_local_structure
    descriptions / propositions
    supporting relationships
    evidence / provenance
    warnings / uncertainty

RepresentationStrategyResolver
    RepresentationContext
        → RepresentationPlan

RepresentationPlan
    strategy_type
    semantic_focus_identity
    payload
    evidence_refs
    rationale / deterministic rule metadata

FocusedLearningRenderer
    RepresentationPlan
        → learner-facing surface
```

Exact names are implementation choices.

The important architectural invariants are:

1. representation selection is explicit;
2. representation selection is deterministic for the same trusted inputs;
3. selection is based on semantic/structural characteristics, not domain-name hardcoding;
4. renderers consume a presentation-oriented payload rather than rediscovering semantic meaning from source text;
5. every displayed factual claim remains traceable to trusted semantic material/evidence;
6. a representation may simplify presentation but may not alter semantic truth;
7. failure to support a rich representation must degrade truthfully to a simpler form.

## Minimum representation grammar

Implement a small grammar containing **at least four genuinely different representation strategies**, including the fallback prose form.

The candidate set should be selected from the forms below according to what current trusted fixtures can support honestly.

### 1. Causal / mechanism representation

Use when trusted structure describes directional causes, effects, influences, induction, enabling, constraining, or another mechanism-like chain/network.

The representation should make the mechanism easier to reason about than a paragraph.

Example shape only:

```text
input / condition
      ↓
mechanism / change
      ↓
outcome
```

Branching and convergence are allowed where trusted structure supports them.

Do not invent missing causal closure.

### 2. Process / sequence representation

Use when trusted structure contains genuine order/chronology/process semantics such as `PRECEDES` or an admitted stage sequence.

Example shape:

```text
stage A → stage B → stage C
```

Do not infer chronology from prose ordering or layout.

### 3. Hierarchy / composition representation

Use for trusted `PART_OF`, `IS_A`, composition, containment, or comparable structural organization.

The learner should be able to see whole/part or general/specific structure without reading a list of sentences.

Preserve canonical predicate direction even when visual hierarchy uses a different spatial orientation.

### 4. Compare / contrast representation

Use only where trusted semantic material provides a legitimate contrast, distinction, alternative, or paired concept structure.

The purpose is to expose discriminating dimensions, not merely place two unrelated concepts in two columns.

If current committed semantic material cannot support a truthful comparison, do not fabricate one merely to satisfy strategy count; implement another supported strategy instead and record why.

### 5. Worked-example / concrete-instance representation

Use where trusted material contains an example/instance and enough context to show how an abstract concept manifests concretely.

The representation should make the mapping from abstract idea → concrete case explicit.

Do not generate novel examples in this offline packet.

### 6. Focused relationship representation

Preserve the successful source → predicate → target representation for a single canonical relationship where that remains the clearest explanation.

This counts as a legitimate representation strategy but must not become the universal fallback for multi-object structure.

### 7. Concise prose fallback

Plain prose is a valid representation when richer structure is absent or would add no explanatory value.

This is not a failure state.

The resolver must prefer truthful simplicity over decorative visualization.

## Strategy-selection rules

Implement deterministic, inspectable rules.

Rules may consider inputs such as:

```text
selected semantic object class
available detected structure types
relationship predicates around the focus
number and topology of trusted supporting relationships
presence of explicit sequence/hierarchy/example semantics
available grounded propositions/descriptions
known weakness/warning metadata
```

Rules must **not** use:

```text
domain == "Economics" → causal diagram
domain == "History" → timeline
domain == "Software Architecture" → hierarchy
```

Domains are evaluation cases, not renderer switches.

The durable report must expose, for each reviewed object:

```text
selected strategy
why the deterministic resolver selected it
which trusted semantic inputs were consumed
what alternative strategies were rejected and why, where useful
```

Avoid fake numerical pedagogical scores.

## Focused explanatory content

The owner needs enough actual content in the right pane to judge the translation mechanism.

For the fixed evaluation cases, do not stop at empty shells or one-line definitions when richer trusted structure already exists.

A representation may combine several grounded layers, for example:

```text
representation / model
        ↓
short explanatory interpretation
        ↓
key distinction / implication when grounded
        ↓
evidence & provenance
```

But every factual statement must derive from existing trusted committed material.

If the current canonical model is too thin to support a richer explanation for a chosen case, that is experiment evidence. Choose another fixed case with sufficient trusted structure rather than silently inventing enrichment.

## No LLM-generated pedagogy yet

SPEC-034 is deliberately `OFFLINE_ONLY`.

Do not call a model to write explanations, analogies, examples, comparisons, or diagrams.

Reason:

The active uncertainty is whether the architecture can distinguish **representation strategy** from **content generation**.

First prove:

```text
trusted semantic structure
        ↓
explicit representation choice
        ↓
useful learner-facing form
```

Only after this seam proves useful should a later packet test whether an LLM can populate/adapt those forms safely.

## Fixed evaluation cases

Use current committed trusted fixtures. Select cases that collectively exercise genuinely different representation forms.

At minimum include:

### Economics

Use a concept/relationship neighborhood with real causal structure around market price, shortage/supply, quantity demanded, or quantity supplied.

The owner should receive something more useful than a glossary definition where trusted causal context exists.

### Software Architecture

Use a concept/relationship neighborhood with composition/hierarchy/dependency structure such as the modular order-processing service and its components.

The representation should expose structural organization rather than merely restating component descriptions.

### History of Printing

Use trusted enablement/process/chronology material where available.

Do not inflate sparse chronology into a rich timeline if the source does not support one.

### Electromagnetism / double-slit structure

Use at least one concept or local structure whose best representation differs from the cases above. Preserve reciprocal relationship semantics and the source-backed/canonical distinction.

The double-slit / wave-particle / complementarity material is a useful candidate if existing trusted semantics can support an example, mechanism, or comparison representation without invention.

## Same-strategy-across-domains test

Add at least one synthetic or existing cross-domain fixture proving that representation choice follows structure rather than domain.

For example, if two domains each contain a genuine hierarchy, both should resolve to the hierarchy strategy through the same rule path.

Likewise, a History object must not receive a sequence merely because it belongs to History if its actual trusted structure is not sequential.

## Depth independence

Representation strategy must remain independent of navigation depth.

A concept or relationship revealed through repeated deeper exploration must enter the same resolver as an equivalent semantic object at root level.

Do not add:

```text
if depth > 0: use special deeper renderer
```

Required invariant:

> Depth changes what trusted knowledge is available, not the grammar used to translate it for learning.

## Interaction responsibility

This packet is primarily about explanation, not synchronized multi-surface interaction.

The focused representation may contain interactive semantic elements only where they materially help understanding.

If it does, interaction must use the existing canonical selection/reveal path. Do not create independent right-pane semantic state.

Do not require every explanatory representation to be interactive. A static but cognitively appropriate representation can be the correct answer.

## Evidence and provenance

Evidence remains mandatory and subordinate to explanation rather than visually dominating it.

The learner must be able to trace displayed canonical claims to existing evidence/provenance.

Do not duplicate raw provenance repeatedly when several visible elements share the same support if a compact truthful presentation can preserve traceability.

Source-backed explanatory material remains explicitly non-canonical where applicable.

## Preserve the learning/navigation separation

SPEC-030 established:

> One semantic state, two complementary responsibilities: navigate on the map; understand on the learning surface.

SPEC-033 then simplified navigation toward revealed canonical territory.

SPEC-034 must not undo either decision.

Specifically forbidden:

- reproducing MY MAP inside the right pane;
- making the left tree carry explanatory diagrams;
- requiring visual mirroring between panes;
- encoding representation state into revealed-tree topology;
- making `Explore next` a second representation selector;
- turning the focused pane into a generic graph viewer.

## Protected state

Preserve:

- BASELINE-001 through BASELINE-004;
- prior SPEC evaluation artifacts;
- SPEC-030 role separation and focused-learning architecture;
- SPEC-031 reciprocal/multi-edge semantic identity;
- canonical revealed-knowledge navigation from the current SPEC-033 candidate/implementation state;
- trusted semantic vocabulary;
- grounding/provenance;
- fail-closed behavior;
- source-bounded depth behavior;
- unrelated user work.

If local SPEC-033 implementation has not yet been reconciled/pushed to `origin/main`, follow `AGENTS.md`: reconcile safely and preserve it. Do not overwrite newer local implementation with the older remote control-plane snapshot.

## Explicit non-goals

Do not implement:

- live LLM explanation generation;
- personalized explanations;
- learner modeling/mastery;
- quizzes;
- guided courses/pathways;
- new ingestion sources;
- semantic ontology expansion merely to force representation selection;
- new canonical facts or relationships;
- automatic analogy generation;
- universal final renderer;
- broad navigation redesign;
- general-purpose graph visualization;
- speculative animation/polish;
- baseline promotion.

## Required implementation work

1. Inspect the current focused-learning resolver/renderer and representation infrastructure.
2. Introduce/strengthen the explicit `RepresentationContext → RepresentationPlan` seam.
3. Define a small deterministic representation-strategy vocabulary.
4. Implement at least four genuinely different strategies including prose fallback.
5. Implement deterministic strategy selection from semantic/structural inputs.
6. Render enough grounded explanatory content for meaningful owner evaluation.
7. Preserve evidence/provenance for every factual/canonical representation.
8. Add fixed cross-domain cases proving structure-driven rather than domain-driven selection.
9. Preserve current revealed-tree navigation unchanged except for in-scope integration seams.
10. Add deterministic tests for strategy resolution, payload integrity, fallback behavior, provenance, depth independence, and navigation non-regression.
11. Produce an isolated browser evaluation artifact and durable report.

## Machine acceptance

Before owner review, verify at least:

```text
control plane valid
no live/model/external calls
trusted semantic vocabulary unchanged
grounding/provenance unchanged
fail-closed behavior unchanged
protected baselines/artifacts unchanged
current revealed-tree navigation regression suite passes
SPEC-031 reciprocal/multi-edge semantics pass
representation resolver is explicit and deterministic
>= 4 genuinely different strategies including prose fallback
strategy choice does not branch on domain name
cross-domain same-structure fixture resolves through same strategy rule
each representation payload retains canonical semantic focus identity
each displayed canonical claim is traceable to trusted semantic/evidence inputs
unsupported rich representation falls back truthfully
no fabricated comparison/example/causal/process semantics
depth-independent strategy resolution passes
right pane does not reproduce the revealed navigation tree
Explore-next behavior remains separate
browser console clean
full offline suite passes
git diff --check passes
```

## Owner review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-034-representation-strategy-grammar-<date>/
```

Provide one exact local command that launches the fixed review candidate.

The owner should be able to move naturally among the four evaluation domains and encounter materially different explanation forms without needing to understand implementation details.

## Owner review question

Do not ask whether the UI is pretty.

Ask:

> **When I select different kinds of knowledge, does the right pane choose a form that actually makes that particular thing easier to understand — and does it feel like the form follows the knowledge rather than a generic template?**

Secondary observations:

- Would I rather learn this object with this representation than with the current one-line explanation?
- Does the representation expose structure I would otherwise have to reconstruct mentally?
- Does prose remain available where a diagram would add nothing?
- Does the representation remain truthful and appropriately bounded by evidence?
- Does MY MAP stay out of the way and continue doing navigation only?

## Verdict set

Owner verdict must be exactly one of:

```text
REPRESENTATION_GRAMMAR_CONFIRMED
PROMISING_BUT_STRATEGY_SELECTION_WEAK
REPRESENTATIONS_NOT_MATERIALLY_BETTER
TRUST_OR_SEMANTIC_BOUNDARY_REGRESSED
NAVIGATION_REGRESSED
INCONCLUSIVE
```

Codex must not assign the subjective verdict.

## Success criterion

`REPRESENTATION_GRAMMAR_CONFIRMED` requires owner evidence that:

1. at least several different semantic structures receive meaningfully different explanation forms;
2. those forms materially help understanding compared with the thin current concept descriptions;
3. representation choice feels structurally justified rather than arbitrary/domain-hardcoded;
