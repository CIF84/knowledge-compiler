# SPEC-017 — Cognitive Topology Projection

## Status

Ready for implementation.

## Phase

Phase II — learner-facing cognitive representation.

## Primary Question

> Can deterministic presentation topology derived from trustworthy assertion participation make the domain's structure immediately perceptible while keeping explanatory text latent and without inventing semantic relationships?

## Product Principle

> **Topology first. Text on demand.**

The default surface should communicate structure before content.

## Evidence

SPEC-016 made substantially more trustworthy quantum material accessible but failed human cognitive review.

The owner's spontaneous reaction was:

> “my brain immediately shut down.”

> “visuals are gone, page is extremely overloaded with text-rich information plus i don't understand architecture straightforwardly.”

> “it seems to work technically, but cognitively it's massive step back.”

> “my brain wanted to leave interface.”

The next experiment must not optimize for information quantity on screen.

It must optimize for immediate perceptibility of structure.

## Two-Compiler Boundary

Preserve:

```text
SOURCE
  ↓
SEMANTIC COMPILER
  ↓
trusted semantic material
  ↓
COGNITIVE COMPILER
  ↓
presentation topology
```

Semantic compiler responsibility:

> What can we safely claim?

Cognitive compiler responsibility:

> What should the human see right now?

SPEC-017 belongs entirely to the second responsibility.

## Frozen Semantic Input

Use the same accepted SPEC-013 realistic-source artifacts used by SPEC-016.

At minimum:

```text
examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904/
```

Consume only accepted frozen:

- symbol table;
- grounded assertions;
- canonical KnowledgeModel;
- existing trusted relationships/propositions/claims;
- provenance/evidence already accepted.

Verify identity/hashes before projection.

Do not rerun semantic extraction or modify semantic artifacts.

## Control

Preserve SPEC-016 as the text-rich assertion-aware control.

Do not modify its viewer/artifacts.

Human comparison is primarily:

```text
SPEC-016
information-first / text-rich assertion surface

vs

SPEC-017
structure-first / topology-first surface
```

The earlier SPEC-006 visual baseline may be used as qualitative design inspiration, not as a semantic benchmark.

## Core Experimental Change

SPEC-016 made assertions visible.

SPEC-017 should instead use assertions primarily to determine **presentation geometry**.

Conceptually:

```text
trusted assertion participation
        ↓
presentation affinity
        ↓
spatial proximity / neighborhoods
        ↓
visual orientation
```

This must not become inferred semantic topology.

## Presentation Affinity

Define a deterministic, transparent presentation-only affinity from existing grounded assertion participation.

Minimum permissible signals:

```text
shared assertion participation
number of shared grounded assertions
canonical relationship adjacency
existing proposition co-participation
assertion degree / concept degree
```

A simple weighted scheme is acceptable if fixed before human review and recorded in artifacts.

Do not use:

- embeddings;
- LLM similarity;
- external ontology;
- semantic enrichment;
- hand-authored quantum categories;
- manually curated clusters.

## Critical Semantic Rule

Presentation affinity is **not a relationship**.

Never serialize or label it as:

```text
CAUSES
IS_A
ENABLES
RELATED_TO
ASSOCIATED_WITH
or any other semantic predicate
```

It may only control presentation properties such as:

```text
proximity
neighborhood membership
layout attraction
visual grouping
focus expansion
```

Machine artifacts must label it explicitly as presentation-only metadata.

## No Pairwise Semantic Fabrication

If one assertion has participants:

```text
A, B, C
```

presentation code may use that shared participation to place A/B/C near one another.

It must not create semantic edges:

```text
A → B
A → C
B → C
```

unless those edges already exist canonically.

## Overview Requirement

The initial viewport should be dominated by **visual structure**, not prose.

Target qualities:

```text
one coherent spatial field
clear focal concepts / neighborhoods
very little body text
no long card grid
no alphabetic list dominating attention
no source excerpts visible by default
no large scrolling document as primary interaction
```

The user should be able to look at the page for several seconds and form an impression of the domain's shape before reading explanations.

## Text Budget

Treat text as a scarce overview resource.

At initial load, concept labels and minimal orientation labels are acceptable.

Avoid visible paragraphs.

Do not show full assertion statements, evidence quotes, detailed definitions, or metadata until interaction requests them.

If a short subtitle/legend is needed, keep it subordinate to the map.

## Progressive Disclosure Levels

Implement a bounded interaction hierarchy approximating:

```text
LEVEL 0 — DOMAIN SHAPE
major presentation neighborhoods / focal concepts

LEVEL 1 — LOCAL TOPOLOGY
selected concept and nearby presentation neighbors
canonical relationships emphasized where present

LEVEL 2 — EXPLANATION
source-backed assertions/claims relevant to selection

LEVEL 3 — EVIDENCE
exact source evidence / provenance
```

Do not implement recursive semantic zoom or generated child models.

These are presentation disclosure levels over one frozen semantic model.

## Google-Maps Interaction Analogy

Use the owner's established interaction preference as design guidance:

- preserve orientation while focusing;
- local exploration should not feel like leaving one page and entering another document;
- surrounding topology should remain visible or recoverable;
- details should appear around the selected location rather than replace the entire mental map;
- returning to overview should be obvious.

Do not implement literal geographic-map controls unless useful.

## Layout

Use 2D.

Do not use 3D.

The layout must be deterministic.

Possible approaches include:

- deterministic force-like layout computed offline with fixed initialization/iterations;
- spectral/layout methods if already available without new heavy dependency;
- deterministic neighborhood/radial placement;
- layered/hybrid layout adapted to presentation affinity.

Prefer the simplest approach that makes topology perceptible.

No runtime random force simulation.

## Neighborhoods

If the projection creates neighborhoods/clusters, they must emerge from deterministic presentation-affinity structure.

Do not name them with invented semantic category labels such as `Foundations`, `Phenomena`, or `Theories` unless those labels already exist in trusted source semantics.

Prefer unlabeled or mechanically labeled neighborhoods if semantic naming would require inference.

A neighborhood may be identified by a high-affinity focal concept rather than a fabricated category.

## Visual Hierarchy

The initial map should communicate at least:

1. focal/high-connectivity concepts;
2. spatial neighborhoods;
3. canonical relationships where present;
4. selected/focused concept;
5. weaker presentation affinity without implying semantic direction.

Use visual weight carefully.

Canonical relationships should remain visually distinct from presentation-only topology.

Presentation affinity should be visually weaker and preferably non-arrowed.

Do not rely on color alone.

## Edge Policy

### Canonical semantic edges

May be visible and labeled according to existing semantics.

### Presentation affinity

Prefer one of:

- no visible edge, proximity only;
- extremely subtle non-directional guide;
- neighborhood enclosure/hull;
- another clearly non-semantic device.

Default toward **proximity without visible edges** if that produces sufficient topology.

Avoid turning the overview into another hairball.

## Initial Density

The map should not show all 41 concepts at equal prominence.

Use deterministic disclosure/salience to create an initial subset.

Target a cognitively manageable first view rather than maximum coverage.

The exact number should be chosen from layout evidence, not hard-coded solely from this instruction, but approximately 6–12 prominent concepts is a reasonable experimental range.

All trusted concepts must remain discoverable through interaction/search if practical.

Do not place an alphabetic 41-item list as the dominant default UI.

## Search

Search may remain available as a secondary navigation mechanism.

It should not visually dominate the map.

Selecting a search result should focus/recenter the topology rather than scroll to a text section.

## Selection Behavior

Clicking a concept should:

```text
persist focus
emphasize local presentation neighborhood
emphasize any canonical semantic relationships
reveal minimal concept description
make relevant explanations available on demand
```

Hover may preview nearby topology if useful.

Do not immediately dump all source-backed explanations into the viewport on selection.

## Explanation Reveal

The user should explicitly request or naturally expand explanatory text.

Examples:

- a small `Explain` affordance;
- clicking a local assertion indicator;
- a compact detail panel with one explanation at a time;
- another minimal interaction.

Prefer one/few explanations over an unbounded list.

## Evidence Reveal

Evidence is one layer deeper than explanation.

Do not show source quotes by default.

Evidence must remain accessible from the explanation it supports.

## Canonical Relationship Trust

Where canonical relationships exist, preserve the strong interaction language established earlier:

```text
select relationship
→ highlight connector
→ show predicate meaning
→ show exact evidence
```

Do not let presentation affinity visually overpower canonical semantic edges.

## Machine Diagnostics

Report at least:

```text
input symbols
input grounded assertions
input canonical relationships
presentation-affinity pairs considered
presentation-affinity pairs retained for layout
initial visible concept count
total discoverable concept count
neighborhood count
neighborhood sizes
canonical relationships visible initially
initial visible prose word count
maximum initial label count
layout overlaps
canonical edge crossings
presentation topology diagnostics
search coverage
provenance completeness
deterministic regeneration
```

Also report a direct SPEC-016 comparison:

```text
initial prose word count
initial visible cards/paragraph blocks
scroll-height / viewport ratio if measurable
initial concept count
number of simultaneously visible explanatory assertions
```

The metrics are diagnostic, not universal cognitive thresholds.

## Human Review Protocol

Human review is decisive.

After machine integrity checks, provide only:

```text
viewer launch command

Use this to orient yourself in the quantum-mechanics material.
```

Do not explain the topology algorithm first.

Do not tell the owner what improved.

Do not provide machine metrics before spontaneous reaction.

Capture the owner's first response.

Then ask:

### Immediate orientation

- Does my brain know where to look first?
- Can I perceive structure before reading?
- Does the domain feel spatially navigable?

### Cognitive load

- Do I feel invited to explore or compelled to read?
- Is the amount of visible text low enough?
- Does anything compete unnecessarily for attention?

### Trust

- Can I distinguish real semantic relationships from presentation grouping?
- Does proximity feel misleading?
- Can I reach source-backed explanations/evidence when needed?

### Navigation

- When I focus on a concept, do I retain orientation?
- Does moving between concepts feel like traversing one knowledge space rather than navigating pages/cards?

### Preference

Compare against SPEC-016:

> Which interface would I voluntarily continue using to understand quantum mechanics?

## Success Criteria

SPEC-017 succeeds if:

1. the initial view is visually/topologically legible before reading prose;
2. the owner does not experience the immediate cognitive shutdown observed in SPEC-016;
3. the owner can identify where to begin exploring;
4. explanatory text is latent rather than dominant;
5. local focus preserves global orientation;
6. presentation topology does not masquerade as semantic truth;
7. canonical relationships remain identifiable;
8. source explanations/evidence remain accessible;
9. the owner strongly prefers the experience to SPEC-016;
10. no semantic IR or source truth is changed.

## Allowed Verdicts

Final product verdict must be exactly one of:

```text
TOPOLOGY_FIRST_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

Machine integrity may pass while human product verdict remains pending.

## No Live Model Calls

SPEC-017 is offline only.

Do not call OpenAI or any external semantic provider.

If a model call appears necessary for clustering, labeling, salience, layout, or explanation, stop and report rather than making it.

## Baseline Protection

Do not modify accepted historical viewer/evaluation artifacts in place.

Use isolated SPEC-017 assets.

Preserve SPEC-016 exactly as the human comparison control.

## Explicit Non-Goals

Do not implement:

- semantic extraction;
- new semantic gates;
- semantic vocabulary changes;
- proposition changes;
- LLM clustering;
- embeddings;
- semantic neighborhood naming;
- recursive semantic zoom;
- generated deeper models;
- Journey/course mode;
- simulation;
- 3D visualization;
- production app shell;
- broad responsive/mobile redesign;
- multi-user evaluation.

## Testing Strategy

All tests offline.

Add focused tests for:

```text
frozen SPEC-013 input verification
presentation-affinity determinism
no semantic-edge fabrication
no inferred neighborhood labels
canonical edge preservation
initial density bounds
text-budget diagnostics
progressive disclosure state
search focus/recenter behavior
explanation/evidence reveal
provenance preservation
layout determinism
baseline immutability
byte-for-byte regeneration
```

Keep the full suite passing.

## Evaluation Artifacts

Create:

```text
examples/evaluations/spec-017-cognitive-topology-projection-<date>/
```

Likely artifacts:

```text
input-manifest.json
presentation-topology.json
layout.json
projection-diagnostics.json
comparison-with-spec016.json
report.json
human-review-template.json
index.html
viewer assets
README.md
```

## Acceptance Criteria — Technical

- [ ] Frozen SPEC-013 semantic inputs verified.
- [ ] SPEC-016 preserved unchanged.
- [ ] No live model calls.
- [ ] Deterministic presentation-affinity calculation implemented.
- [ ] Presentation affinity explicitly non-semantic.
- [ ] No pairwise semantic edges fabricated from assertion participation.
- [ ] No invented semantic neighborhood labels.
- [ ] 2D deterministic layout.
- [ ] Initial viewport dominated by topology rather than prose.
- [ ] Initial concept density bounded.
- [ ] Explanatory paragraphs hidden by default.
- [ ] Evidence hidden until requested.
- [ ] Canonical relationships visually distinct.
- [ ] Presentation affinity does not rely on arrowed semantic-looking edges by default.
- [ ] Concept focus preserves orientation.
- [ ] Search focuses/recenters topology if implemented.
- [ ] All trusted concepts remain discoverable where practical.
- [ ] Provenance complete.
- [ ] Regeneration deterministic.
- [ ] Prior artifacts unchanged.
- [ ] Full offline suite passes.

## Final Constraint

Do not solve cognitive overload by deleting trustworthy knowledge.

Do not solve sparse semantic topology by inventing relationships.

Instead separate **availability** from **visibility**:

```text
trustworthy knowledge remains available
        ↓
attention determines what becomes visible
```

The experiment asks:

> **Can Knowledge Compiler make the topology of trustworthy knowledge perceptible before asking the learner to read it?**
