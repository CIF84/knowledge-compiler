# SPEC-031 — Reciprocal and Multi-Edge Relationship Semantics

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can one visual connection faithfully expose every canonical directed relationship it represents, including reciprocal or otherwise multi-edge cases, without weakening the single canonical interaction-state architecture or fabricating a synthetic relationship?

## Owner verdict on SPEC-030

Record SPEC-030 as:

```text
ROLE_SEPARATION_CONFIRMED
```

Owner evidence:

- map and learning surface now have useful complementary roles;
- the right pane no longer defaults to duplicating the navigation map;
- recursive/deeper interaction remains substantially coherent;
- focused relationship and source-backed explanation representations are materially more useful for understanding;
- the reviewed SPEC-030 state is the strongest UI version so far;
- one narrow defect remains: the reciprocal Electric field / Magnetic field `INDUCES` pair is visually bidirectional, but relationship hover/click resolves only the Electric field → Magnetic field assertion.

See `debriefs/DEBRIEF-030-distinct-learning-surface-representation.md`.

## Why this is next

SPEC-030 moved the dominant uncertainty from UI synchronization and role separation back toward semantic capability.

The Electromagnetism fixture contains two canonical directed assertions sharing the same endpoint pair and visual corridor:

```text
Electric field → INDUCES → Magnetic field
Magnetic field → INDUCES → Electric field
```

The map visibly communicates both directions, but the interaction/learning-surface path exposes only one.

This violates the stronger invariant:

> **A visual relationship containing N canonical semantic edges must not silently resolve to fewer than N semantic identities.**

## Core principles

> **Visual grouping may compress geometry; it may not collapse semantic identity.**

> **Reciprocal relationships are two directed assertions unless trusted canonical data explicitly says otherwise.**

> **Every canonical edge shown to the learner must remain discoverable, selectable, explainable, and grounded.**

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- SPEC-023/FIX-023 historical artifact;
- SPEC-024 through SPEC-030 historical/evaluation artifacts;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, admission, and fail-closed behavior.

Treat the SPEC-030 implementation as the best-known working UI behavior to preserve in the isolated SPEC-031 candidate.

Do not reopen or redesign:

- canonical learner state;
- atomic context lifecycle;
- recursive depth grammar;
- map/navigation responsibility;
- learning-surface/understanding responsibility;
- representation resolver architecture;
- semantic extraction or ontology.

## Experimental variable

Only this semantic-interaction variable is in scope:

```text
canonical relationship multiplicity under shared visual geometry
```

## Required semantic model

The implementation must distinguish:

```text
visual relationship geometry
≠ canonical relationship identity
```

A visual connection may correspond to one or more canonical directed relationship identities.

For a reciprocal pair, preserve at minimum:

```text
relationship A
source = Electric field
target = Magnetic field
predicate = INDUCES
identity = canonical edge A

relationship B
source = Magnetic field
target = Electric field
predicate = INDUCES
identity = canonical edge B
```

Do not manufacture a third canonical `BIDIRECTIONAL_INDUCES` relationship unless such an object already exists in trusted committed semantics.

## Interaction requirement

The learner must be able to recover every canonical relationship represented by the shared visual connection.

The exact minimal interaction may be chosen by implementation evidence, but it must satisfy all of the following:

- hovering the shared visual relationship must not falsely imply that only one canonical direction exists;
- clicking/selecting must provide a deterministic path to each represented canonical edge;
- the learning surface must never show one direction while the map interaction semantically represents another;
- each selected directed edge must enter the existing canonical interaction state using its own stable semantic identity;
- map and learning surface must project the same selected edge identity;
- evidence/provenance must remain attached to the correct directed assertion;
- switching between reciprocal edges must be atomic and must not leave stale direction, predicate, evidence, or endpoint state.

## Preferred minimal representation behavior

Do not prescribe a broad visual redesign.

If the existing geometry can reliably distinguish the individual directed arrows, making each directed arrow independently interactive is acceptable and likely simplest.

If the rendered geometry cannot reliably distinguish them, the shared connection may resolve to a small deterministic relationship-choice representation exposing the canonical directed assertions it contains.

For example, conceptually:

```text
Electric field → Magnetic field
INDUCES

Magnetic field → Electric field
INDUCES
```

This chooser/group is a presentation object only. It must not become a new canonical semantic relationship identity.

Choose the smallest implementation that preserves semantic truth and the existing interaction grammar.

## Hover semantics

Hover remains preview, not committed selection.

For single-edge geometry:

```text
hover visual edge → preview that canonical edge
```

For shared geometry representing multiple canonical edges, hover must truthfully communicate multiplicity. It may preview the grouped relationship set or the specifically hovered directed arrow if geometry makes direction unambiguous.

Forbidden:

```text
hover reciprocal geometry → silently preview arbitrary first edge
```

## Selection semantics

Click remains committed semantic selection.

A committed relationship selection must always have one unambiguous canonical relationship identity.

If a shared geometry requires an intermediate relationship-set choice, that presentation state must not masquerade as a canonical edge selection.

Once the learner chooses a direction:

```text
selected map relationship identity
== canonical learner relationship identity
== learning-surface relationship identity
```

## Learning-surface requirement

Reuse the SPEC-030 relationship representation pipeline.

For a selected directed canonical edge, the right pane must render the correct:

- source;
- predicate;
- target;
- meaning;
- evidence/provenance;
- semantic identity.

The two reciprocal selections must visibly reverse source and target while preserving the correct trusted evidence for each edge.

Do not revert to a duplicate navigation map.

## Fixed evaluation case A — Electromagnetism reciprocal pair

This is the primary case.

Start from Electromagnetism orientation and exercise both:

```text
Electric field → INDUCES → Magnetic field
Magnetic field → INDUCES → Electric field
```

Mechanically verify:

- both canonical relationship identities exist independently in trusted candidate data;
- both are represented by the map;
- both are recoverable through interaction;
- each can be previewed/selected without silently becoming the other;
- the learning surface renders the correct direction for each;
- evidence/provenance belongs to the selected directed edge;
- repeated A → B → A switching remains coherent;
- clear returns to orientation with no stale direction.

## Fixed evaluation case B — ordinary single edge

Exercise at least one normal single directed relationship such as:

```text
double-slit experiment → CAUSES → interference pattern
```

Its interaction must remain unchanged. SPEC-031 must not make ordinary relationships require unnecessary multi-edge interaction.

## Fixed evaluation case C — same endpoints / multiple predicates if available

Inspect committed deterministic fixtures for any endpoint pair with more than one canonical relationship identity, whether reciprocal or same-direction/different-predicate.

If such a case already exists, include it in the evaluation.

If none exists, add only a synthetic deterministic test fixture at the interaction/unit-test layer; do not add new domain facts to accepted semantic artifacts.

Verify that multiplicity is keyed by canonical relationship identity, not merely by endpoint pair or predicate text.

## Recursive parity

The semantic model must be depth-independent.

A reciprocal/multi-edge relationship encountered in deeper revealed knowledge must use the same relationship-multiplicity machinery as ground level.

Do not add `depth == 0` special handling.

Existing synthetic depth-10 interaction tests must remain passing.

Add a deterministic synthetic test proving multi-edge identity resolution through recursive context without requiring ten bespoke UI fixtures.

## Identity and event-path constraint

Do not solve this with surface-specific state or direct map → pane synchronization.

All committed directed-edge selections must pass through the same canonical event/reducer path established by SPEC-029 and preserved by SPEC-030.

The implementation should make relationship identity explicit enough that no resolver depends on:

- DOM order;
- first matching source/target pair;
- first matching predicate;
- visual path order;
- array insertion order when multiple semantic edges match one geometry.

Any such first-match behavior is a failure.

## Semantic trust constraints

No new domain semantics are authorized.

Forbidden:

- merging two directed canonical assertions into a fabricated reciprocal assertion;
- inventing reverse evidence;
- reusing forward evidence for reverse direction unless trusted committed data explicitly grounds both;
- inferring symmetry from visual arrows;
- changing predicate meaning;
- promoting source-backed explanation to canonical structure;
- model-generated repair or enrichment.

If the reverse Electromagnetism edge is visually rendered but not independently grounded in trusted canonical data, stop and report that mismatch rather than fabricating support.

## Preserve SPEC-030 role separation

The packet must not regress the accepted distinction:

```text
MAP
navigate / orient / reveal structure

LEARNING SURFACE
translate / explain / provide evidence
```

A multi-edge disambiguation control may appear where necessary, but the right pane must remain an understanding surface rather than becoming a second navigation map.

## No live calls

This packet is `OFFLINE_ONLY`.

Forbidden:

- model/provider calls;
- web retrieval;
- external enrichment;
- embeddings;
- extraction/canonicalization;
- semantic retries;
- agent/LLM judging.

Use committed deterministic artifacts only.

## Mechanical gate

Before owner review, verify at least:

```text
BASELINE-001..004 hashes unchanged
SPEC-023/FIX-023 preserved
SPEC-024..030 historical artifacts preserved
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
no fabricated reciprocal relationship
no fabricated reverse evidence
SPEC-029 canonical active-context path preserved
SPEC-029 canonical interaction-state path preserved
SPEC-030 learning-surface representation seam preserved
SPEC-030 duplicate-map guard passes
Electromagnetism reciprocal canonical identities independently verified
Electric → Magnetic relationship recoverable
Magnetic → Electric relationship recoverable
forward selection projects correct source/predicate/target/evidence
reverse selection projects correct source/predicate/target/evidence
A → B → A reciprocal switching coherent
shared-geometry hover does not silently collapse multiplicity
ordinary single-edge interaction unchanged
multi-edge resolution does not depend on first-match/DOM/array order
map ↔ learning-surface selected relationship identity agreement passes
clear/preview/selection semantics preserved
context switching does not resurrect stale relationship direction
synthetic recursive multi-edge identity test passes
synthetic depth-10 interaction parity remains passing
browser console clean
pan/zoom remain functional
full offline suite passes
```

If any machine gate fails, do not request owner review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-031-reciprocal-and-multi-edge-relationship-semantics-<date>/
```

Do not mutate accepted baselines or prior SPEC evaluations.

## Owner review

Do not prime the owner with implementation details.

If the machine gate passes, provide only the low-attention completion handoff, exact viewer command, and approximately this task:

```text
Open Electromagnetism. Interact naturally with the relationship between Electric field and Magnetic field in both directions. Confirm that the interface makes it clear there are two directed INDUCES assertions and that you can inspect each one without the other silently taking its place. Check that the right pane reverses source/target correctly and remains about exactly the relationship you selected. Then sample an ordinary one-way relationship and a deeper-map interaction to make sure nothing else became more complicated or inconsistent.
```

## Verdict set

Final subjective verdict must be exactly one of:

```text
RELATIONSHIP_MULTIPLICITY_CONFIRMED
MIXED
SEMANTIC_EDGE_COLLAPSE_REMAINS
INTERACTION_GRAMMAR_REGRESSED
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`RELATIONSHIP_MULTIPLICITY_CONFIRMED` requires owner evidence that:

- every canonical directed edge represented by the reciprocal visual connection is discoverable;
- selecting one direction never silently resolves to the other;
- the learning surface truthfully represents the selected direction and its evidence;
- ordinary single-edge relationships remain simple;
- map and learning surface still share one canonical semantic state;
- recursive interaction grammar remains unchanged;
- no semantic trust invariant is weakened.

## Explicit non-goals

Do not implement:

- broad UI redesign;
- generalized graph editor behavior;
- new domain facts;
- new canonical predicates;
- automatic semantic symmetry inference;
- model-generated explanations;
- new depth generation;
- navigation history UI;
- final universal multi-edge visualization system;
- baseline promotion;
- unrelated refactoring.

## Required durable report

Record at least:

- frozen/baseline hash verification;
- files changed;
- exact trusted canonical identities for the reciprocal Electromagnetism pair;
- source/predicate/target/evidence for each direction;
- visual-geometry → canonical-edge multiplicity representation introduced;
- hover and selection resolution rules;
- proof that no first-match/DOM/array-order dependency remains;
- fixed evaluation-case results;
- map ↔ learning-surface relationship-identity agreement results;
- ordinary single-edge regression result;
- recursive multi-edge test result;
- depth-10 parity result;
- SPEC-030 role-separation/duplicate-map guard result;
- semantic trust checks;
- browser verification;
- console result;
- full offline tests;
- dependencies/live calls;
- deviations;
- commit/push state;
- exact viewer command.

## Low-attention completion handoff

On successful implementation, return only:

- `SPEC-031` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep implementation detail in the durable report.

## Final constraint

Do not solve reciprocal geometry by pretending two canonical assertions are one.

Establish the stronger invariant:

> **One visual connection may represent many semantic edges; every edge keeps its own identity, direction, grounding, and learner-facing explanation.**
