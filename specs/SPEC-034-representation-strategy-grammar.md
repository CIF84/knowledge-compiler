# SPEC-034 — Representation Strategy Grammar

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can Knowledge Compiler deterministically translate different kinds of trusted semantic structure into genuinely different learner-facing representation forms, choosing the form because it fits the knowledge rather than because every selected object is rendered as prose or a diagram?

## Owner evidence entering this packet

Owner review of the canonical revealed-knowledge candidate indicates that navigation now behaves substantially as intended:

```text
MY MAP → revealed knowledge territory
WHAT DOES THIS MEAN? → focused learner-facing translation
EXPLORE NEXT → trusted frontier
```

The left pane is no longer the main product bottleneck. The newly exposed weakness is the focused learning surface: many concepts still resolve to a title, one-sentence description, and provenance. Some relationships receive a useful source → predicate → target representation, but there is not yet a general translation mechanism that selects among meaningfully different explanatory forms.

This packet returns to the original representation thesis of SPEC-005/SPEC-006 while preserving the role separation confirmed by SPEC-030.

## Guiding principle

> **Representation strategy must not equal diagram.**

The representation should fit the information structure and the learner's immediate understanding problem. Depending on trusted semantic structure, the best representation may be a causal/mechanism view, process/sequence, hierarchy/composition view, compare/contrast, worked example, focused relationship view, concise prose, or a small local explanatory diagram.

SPEC-034 does not attempt a universal final renderer. It tests whether **representation choice can become an explicit deterministic architectural decision**.

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

`EXPLORE NEXT` remains a frontier/revelation mechanism, not a representation selector. Do not reintroduce map ↔ explanation visual mirroring.

## Required prior context

Before implementation inspect only what is needed to preserve accepted seams:

- `specs/SPEC-005-minimal-representation.md`;
- `specs/SPEC-006-structure-aware-layout-and-synchronized-interaction.md`;
- `specs/SPEC-030-distinct-learning-surface-representation.md`;
- `debriefs/DEBRIEF-030-distinct-learning-surface-representation.md`;
- current canonical revealed-knowledge implementation and focused-learning resolver/renderer;
- current representation models/builders and relevant tests.

## Experimental control

Hold constant canonical semantic facts/vocabulary, grounding/provenance/fail-closed behavior, reciprocal/multi-edge identity, revealed-knowledge navigation, collapse/current-focus behavior, Explore-next semantics, recursive/depth semantics, source material, and accepted fixtures.

Change only what is required to introduce and demonstrate a richer representation-strategy layer. Do not make navigation more complex.

## Representation architecture

Introduce or strengthen an explicit seam conceptually equivalent to:

```text
RepresentationContext
    semantic_object
    semantic_class
    trusted_local_structure
    descriptions / propositions
    supporting_relationships
    evidence / provenance
    warnings / uncertainty

RepresentationStrategyResolver
    RepresentationContext → RepresentationPlan

RepresentationPlan
    strategy_type
    semantic_focus_identity
    payload
    evidence_refs
    deterministic_rule_metadata

FocusedLearningRenderer
    RepresentationPlan → learner-facing surface
```

Required invariants:

1. representation selection is explicit and deterministic;
2. selection is based on semantic/structural characteristics, not domain-name hardcoding;
3. renderers consume presentation payloads rather than rediscovering meaning from source text;
4. every factual claim remains traceable to trusted semantic material/evidence;
5. presentation may simplify but may not alter semantic truth;
6. unsupported rich representation degrades truthfully to a simpler form.

## Minimum representation grammar

Implement **at least four genuinely different strategies, including prose fallback**. Choose only forms current trusted fixtures can honestly support.

### Causal / mechanism
Use for trusted directional causes, effects, influences, induction, enabling, constraining, or mechanism-like chains/networks. Make branching/convergence visible where supported. Do not invent missing causal closure.

### Process / sequence
Use only where trusted structure contains genuine chronology/order such as `PRECEDES` or admitted stages. Do not infer chronology from prose ordering or layout.

### Hierarchy / composition
Use for trusted `PART_OF`, `IS_A`, composition, containment, or comparable structural organization. Preserve canonical predicate direction even if visual hierarchy uses another spatial orientation.

### Compare / contrast
Use only where trusted material provides a legitimate contrast, distinction, alternative, or paired structure. Do not manufacture a two-column comparison from unrelated concepts. If current material cannot support this truthfully, use another supported strategy instead.

### Worked example / concrete instance
Use where trusted material contains an example/instance and enough context to map abstract idea → concrete case. Do not generate novel examples in this offline packet.

### Focused relationship
Preserve the successful source → predicate → target representation for a single canonical relationship where it remains the clearest explanation. It must not become the universal fallback for richer local structure.

### Concise prose fallback
Plain prose is valid where richer structure is absent or adds no explanatory value. Truthful simplicity is preferable to decorative visualization.

## Strategy-selection rules

Rules may consider semantic object class, detected structure types, predicates around focus, topology of supporting relationships, explicit sequence/hierarchy/example semantics, grounded propositions/descriptions, and weakness/warning metadata.

Rules must not use domain switches such as `Economics → causal`, `History → timeline`, or `Software Architecture → hierarchy`.

The durable report must record per reviewed object: selected strategy, deterministic rule/rationale, trusted inputs consumed, and fallback/rejection reason where relevant. Do not create fake numerical pedagogical scores.

## Focused explanatory content

The owner needs enough actual content to judge translation. Do not stop at empty shells or one-line definitions when richer trusted structure already exists.

A representation may combine:

```text
representation/model
        ↓
short grounded interpretation
        ↓
key distinction/implication when grounded
        ↓
evidence & provenance
```

Every factual statement must derive from existing trusted committed material. If a candidate object is too thin, record that as evidence and choose another fixed case rather than inventing enrichment.

## No LLM-generated pedagogy yet

This packet is `OFFLINE_ONLY`. Do not call a model to write explanations, analogies, examples, comparisons, or diagrams. First prove:

```text
trusted semantic structure
        ↓
explicit representation choice
        ↓
useful learner-facing form
```

A later packet may test model-assisted population/adaptation only after this seam demonstrates value.

## Fixed evaluation cases

Use committed trusted fixtures and collectively exercise genuinely different forms.

- **Economics:** real causal structure around market price, shortage/supply, quantity demanded, or quantity supplied. Where trusted context exists, produce more than a glossary definition.
- **Software Architecture:** composition/hierarchy/dependency structure such as the modular order-processing service and components.
- **History of Printing:** trusted enablement/process/chronology where available; do not inflate sparse chronology.
- **Electromagnetism / double-slit:** at least one concept/local structure whose best form differs from cases above. Preserve reciprocal semantics and canonical vs source-backed distinction. Use double-slit / wave-particle / complementarity only if current trusted semantics support the form without invention.

## Structure-not-domain proof

Add at least one synthetic or existing cross-domain fixture proving representation choice follows structure rather than domain. If two domains contain the same supported structural class, they should resolve through the same rule path. A History object must not receive a sequence merely because it belongs to History.

## Depth independence

A concept or relationship revealed through repeated deeper exploration must enter the same resolver as an equivalent object at root level. Forbidden: `if depth > 0: use special deeper renderer`.

> **Depth changes what trusted knowledge is available, not the grammar used to translate it for learning.**

## Interaction responsibility

This packet is about explanation, not multi-surface synchronization. Focused representations may contain interactive semantic elements only where they materially help understanding. Any such interaction must use the existing canonical selection/reveal path; do not create independent right-pane semantic state. Not every representation needs to be interactive.

## Evidence and provenance

Evidence remains mandatory but subordinate to explanation. Displayed canonical claims must trace to existing evidence/provenance. Source-backed explanatory material remains explicitly non-canonical where applicable.

## Preserve navigation/learning separation

SPEC-030 established:

> **One semantic state, two complementary responsibilities: navigate on the map; understand on the learning surface.**

Forbidden: reproducing MY MAP inside the right pane; explanatory diagrams in the left tree; visual mirroring requirements; representation state encoded into revealed topology; Explore-next as a second representation selector; generic graph-viewer behavior in the focused pane.

## Protected state

Preserve BASELINE-001..004, prior SPEC artifacts, SPEC-030 role separation, SPEC-031 reciprocal/multi-edge identity, current SPEC-033 revealed-knowledge navigation, trusted vocabulary/grounding/provenance/fail-closed behavior, source-bounded depth behavior, and unrelated user work.

If local SPEC-033 implementation is newer than the remote control-plane snapshot, follow `AGENTS.md`: reconcile safely and preserve it. Do not overwrite newer local implementation with older remote state.

## Explicit non-goals

No live LLM pedagogy, personalization, learner modeling/mastery, quizzes, guided courses/pathways, new ingestion, ontology expansion merely to force strategy selection, new canonical facts/relationships, automatic analogy generation, universal final renderer, broad navigation redesign, general graph visualizer, speculative polish, or baseline promotion.

## Required implementation work

1. Inspect current focused-learning and representation seams.
2. Introduce/strengthen `RepresentationContext → RepresentationPlan`.
3. Define a small deterministic strategy vocabulary.
4. Implement at least four genuinely different strategies including prose fallback.
5. Resolve strategies from semantic/structural inputs, never domain name.
6. Render enough grounded content for meaningful owner evaluation.
7. Preserve provenance for every factual/canonical representation.
8. Add cross-domain structure-driven selection proof.
9. Preserve revealed-tree navigation unchanged except minimal integration seams.
10. Add deterministic tests for resolution, payload integrity, fallback, provenance, depth independence, and navigation non-regression.
11. Produce an isolated browser evaluation artifact and durable report.

## Machine acceptance

Before owner review verify:

```text
control plane valid
no live/model/external calls
trusted semantic vocabulary unchanged
grounding/provenance unchanged
fail-closed behavior unchanged
protected baselines/artifacts unchanged
revealed-tree navigation regression suite passes
SPEC-031 reciprocal/multi-edge semantics pass
representation resolver explicit and deterministic
>= 4 genuinely different strategies including prose fallback
strategy choice contains no domain-name branching
cross-domain same-structure case follows same rule path
representation payload retains canonical focus identity
displayed canonical claims trace to trusted inputs
unsupported rich form falls back truthfully
no fabricated comparison/example/causal/process semantics
depth-independent strategy resolution passes
right pane does not reproduce revealed navigation tree
Explore-next remains separate
browser console clean
full offline suite passes
git diff --check passes
```

## Owner review artifact

Create:

```text
examples/evaluations/spec-034-representation-strategy-grammar-<date>/
```

Provide one exact local command launching the fixed review candidate. The owner should be able to move naturally among the four evaluation domains and encounter materially different explanation forms without implementation knowledge.

## Owner review question

> **When I select different kinds of knowledge, does the right pane choose a form that actually makes that particular thing easier to understand — and does it feel like the form follows the knowledge rather than a generic template?**

Also observe whether structure is exposed rather than mentally reconstructed, prose remains where visualization adds nothing, evidence bounds remain truthful, and MY MAP stays focused on navigation.

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

`REPRESENTATION_GRAMMAR_CONFIRMED` requires owner evidence that different semantic structures receive meaningfully different forms; those forms improve understanding over thin descriptions; choices feel structurally justified; prose remains a valid fallback; evidence/canonical truth remain intact; navigation remains separated and usable; and the architecture works independent of depth.

## Required durable report

Record files changed, protected-state verification, strategies implemented, deterministic selection rules, per-case strategy/trusted inputs, cross-domain proof, fallback cases, provenance/trust checks, depth-independence, navigation regression, browser/console result, focused/full tests, dependencies/live calls, deviations, commit/push/clean state, and exact owner-review command.

## Completion state and handoff

On successful implementation set SPEC-034 to `IMPLEMENTED_AWAITING_REVIEW` and update `STATUS.md` consistently so completed work is not left executable. Return only the low-attention handoff required by `AGENTS.md`.

Do not promote a baseline or begin model-generated pedagogy automatically.

## Final constraint

Do not optimize for the number of diagrams.

> **The compiler should choose the representation that minimizes the cognitive work required to understand the trusted structure currently in focus.**
