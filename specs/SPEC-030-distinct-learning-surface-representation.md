# SPEC-030 — Distinct Learning Surface Representation

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can the map and learning surface remain perfectly state-coherent while taking deliberately different representational roles: the map for navigation/orientation and the learning surface for learner-appropriate explanation?

## Owner verdict on SPEC-029

Record SPEC-029 as:

```text
MIXED
```

Owner evidence:

- major breakthrough: recursive/deeper interaction behavior is now substantially coherent;
- major breakthrough: the reviewed deep map ↔ right-pane state behavior appears to resolve the main UI capability bottleneck;
- improvement: the previously observed stale deep-context pane failure did not recur in the reviewed cross-domain sequence;
- remaining concern: apparent ground-level semantic propagation gaps remain in Software Architecture and History of Printing;
- product concern: the right pane now resembles the navigation map too closely, risking duplicate use of space rather than translation into a representation optimized for learning.

See `debriefs/DEBRIEF-029-atomic-context-transition-and-semantic-coverage.md`.

## Why this is next

The interaction architecture is now sufficiently capable that the next uncertainty is not primarily synchronization plumbing.

The current implementation proved that map and learning surface can project the same semantic state. But visual duplication is not the goal.

The intended distinction is:

```text
MAP
Where am I?
What exists around this?
How is it connected?
Where can I go next?
How did I get here?

LEARNING SURFACE
What does this mean?
Why does it matter?
How should I understand it?
What representation makes it clearest?
What evidence supports it?
```

The next experiment must test this division of responsibility without weakening the canonical interaction-state architecture established by SPEC-029.

## Core principle

> **The map and learning surface share semantic state, but not representational responsibility.**

And:

> **The learning surface should translate selected knowledge into the representation best suited to understanding it, not reproduce navigation merely because the map already exists.**

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- SPEC-023/FIX-023 historical artifact;
- SPEC-024 through SPEC-029 historical/evaluation artifacts;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, admission, and fail-closed behavior.

Treat the SPEC-029 implementation as the best-known working UI behavior to preserve in the isolated SPEC-030 candidate. Do not overwrite or promote it as a formal baseline in this packet.

Create an isolated SPEC-030 evaluation.

## Experimental variable

Only this product/UI variable is in scope:

```text
learning-surface representation responsibility
```

Do not reopen canonical interaction state, recursive map geometry, semantic extraction, ontology, or knowledge generation unless a hard blocker proves the current architecture cannot support the experiment.

## Required role separation

The left map remains the authoritative spatial/navigation surface.

It may show:

- surrounding concepts;
- relationships;
- recursive/deeper expansions;
- path/ancestry/context;
- hover/preview/selection state;
- pan/zoom and spatial orientation.

The right learning surface must not default to a second full navigation map merely to mirror state.

Instead it must render a learner-facing representation derived from the same canonical semantic focus.

At minimum support the existing fixed semantic classes:

- concept;
- canonical relationship;
- source-backed explanation;
- orientation/no-focus state.

## Representation strategy

Do not attempt a universal final renderer.

Implement the smallest deterministic representation-selection seam that demonstrates the architecture. Conceptually:

```text
canonical learner state
+ semantic object / local trusted context
→ representation resolver
→ learner-facing representation payload
→ learning surface renderer
```

The resolver must be deterministic and offline for this packet.

It may choose among a small fixed set of representation forms already supportable from committed trusted data, for example:

- concise concept explanation;
- focused relationship diagram plus explanation;
- causal chain;
- hierarchy/part-whole view;
- comparison;
- sequence/timeline where trusted structure actually supports it;
- evidence/provenance view;
- small local explanatory subgraph when a diagram is genuinely the clearest representation.

These are examples, not a requirement to implement every form.

The key requirement is that representation choice is explicit and semantically justified rather than always cloning the map.

## No fabricated pedagogy or semantics

A prettier explanation is not permission to invent knowledge.

Every learning-surface representation must derive only from trusted committed semantic material and evidence already available to the candidate.

Forbidden:

- fabricated intermediate concepts;
- inferred causal links not admitted by trusted semantics;
- invented chronology;
- unsupported analogy;
- model-generated enrichment;
- hiding uncertainty by converting weak explanatory material into canonical structure.

If the available semantic material cannot support a richer representation, render a simpler truthful representation.

## State-coherence invariant

Representation may differ. Semantic state may not.

For every supported semantic object:

```text
map semantic focus == canonical learner semantic focus == learning-surface semantic focus
```

Hover remains preview. Click remains committed selection. Clear remains clear.

Changing representation form must never create an independent learning-surface selection state.

The right pane may render a different shape, but it must always be recognizably about the same semantic object or relationship currently active in canonical state.

## Bidirectional interaction requirement

Where the learning-surface representation contains interactive semantic elements, interaction must dispatch through the same canonical event/reducer path used by the map.

Do not reintroduce surface-to-surface synchronization.

If a learning representation contains no additional interactive semantic elements, that is acceptable for this experiment provided the current semantic focus remains clear and map interaction remains coherent.

## Avoid duplicate-map failure

Add a deterministic/browser assertion or inspectable report criterion that the default learning representation for the selected SPEC-030 test cases is not simply a second full copy of the active navigation map.

A focused local diagram is allowed when pedagogically justified, but it must be scoped to explanation and should omit unrelated navigation context.

The owner should be able to answer:

> “Why is this representation on the right helping me understand something the map on the left does not already tell me?”

If the answer is “it is just the same graph again,” the experiment fails.

## Fixed evaluation cases

Use committed fixtures only.

Evaluate at least:

### 1. History of Printing

Exercise a concept and at least one trusted relationship.

The learning surface should explain the selected meaning/relationship without reproducing the entire History of Printing navigation map.

### 2. Software Architecture

Exercise a concept and at least one trusted relationship.

This case must also explicitly probe the owner-observed ground-level propagation gap. If the selected payment/database or equivalent trusted relationship does not enter canonical state correctly, record it as a blocker/failure rather than disguising it with the new renderer.

### 3. Electromagnetism / double-slit deeper structure

Enter the deeper structure and exercise:

- a concept;
- a canonical relationship;
- a source-backed explanation.

The learning surface should use the same representation grammar as ground level while preserving recursive navigation on the left.

## Ground-level unresolved-defect guard

SPEC-029 owner review reported apparent ground-level propagation gaps.

Before judging the new representation experiment, mechanically determine whether those examples are:

```text
A. valid interactive semantic objects that fail to enter/project canonical state
B. intentionally non-interactive/non-canonical visual structure
C. fixture/data ambiguity
```

Record the classification with evidence.

If A, repair only if the fix is narrow and clearly within the existing canonical interaction path. Do not create a parallel handler. If repair would materially expand scope, stop and report the blocker.

If B or C, make the distinction inspectable in the durable report and do not fabricate interactivity.

## Recursive continuity

Do not regress the established recursive interaction behavior.

The existing synthetic depth-10 state tests must continue to pass.

Representation resolution must depend on semantic identity/class and trusted context, not on a special-case `depth == 1` renderer.

Required principle:

```text
depth changes available knowledge
not interaction grammar
not representation architecture
```

A semantic object encountered at depth 10 must be representable through the same learning-surface pipeline as the same class at depth 0.

## Right-pane capacity

The learning surface must not assume that every useful representation fits into the current visible viewport without scrolling or local navigation.

For this packet, preserve the existing shell and allow ordinary pane scrolling where needed. Do not build a new nested navigation system.

The representation architecture must not depend on shrinking a complex explanation until it visually matches the map dimensions.

## Preserve accepted learner grammar

Preserve:

- current shell and visual language;
- `WHERE AM I?` as spatial/navigation responsibility;
- `WHAT DOES THIS MEAN?` as learning/translation responsibility;
- canonical learner state and atomic context lifecycle from SPEC-029;
- preview vs selected distinction;
- recursive depth expansion on the map;
- relationship direction/predicate semantics;
- canonical vs source-backed distinction;
- exact evidence/provenance access;
- pan/zoom and collapse/retraction behavior;
- typography, spacing, colors, and controls unless a minimal local change is required to express the learning representation.

This is not a general visual redesign.

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
SPEC-024..029 historical artifacts preserved
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
no fabricated semantic edges/facts
SPEC-029 canonical active-context path preserved
SPEC-029 canonical interaction-state path preserved
map remains navigation/orientation surface
learning surface uses explicit representation resolver/seam
learning surface does not default to full duplicate navigation map for fixed cases
concept representation resolves from canonical state
canonical relationship representation resolves from canonical state
source-backed explanation representation resolves from canonical state
History of Printing fixed case passes
Software Architecture fixed case passes or unresolved defect is explicitly classified/stopped
Electromagnetism deeper fixed case passes
map → learning surface semantic identity agreement passes
learning surface interactive element → canonical state → map agreement passes where applicable
clear/preview/selection semantics preserved
context switching does not resurrect stale representations
synthetic depth-10 interaction parity remains passing
representation architecture is depth-independent
browser console clean
pan/zoom remain functional
full offline suite passes
```

If any machine gate fails, do not request owner review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-030-distinct-learning-surface-representation-<date>/
```

Do not mutate accepted baselines or prior SPEC evaluations.

## Owner review

Do not prime the owner with implementation details.

If the machine gate passes, provide only the low-attention completion handoff, exact viewer command, and approximately this task:

```text
Use the workspace naturally across History of Printing, Software Architecture, and the double-slit deeper structure. Pick concepts, relationships, and source explanations. Ignore whether the right pane is visually impressive. Ask instead: does the left side help you navigate while the right side helps you understand? Does the right side tell or show you something useful that is not merely a duplicate of the map? And do both sides still always agree about what you are currently exploring?
```

## Verdict set

Final subjective verdict must be exactly one of:

```text
ROLE_SEPARATION_CONFIRMED
MIXED
LEARNING_SURFACE_STILL_DUPLICATES_NAVIGATION
STATE_COHERENCE_REGRESSED
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`ROLE_SEPARATION_CONFIRMED` requires owner evidence that:

- the map remains useful for orientation/navigation;
- the learning surface materially helps understanding rather than duplicating navigation;
- both surfaces remain projections of one canonical semantic state;
- concepts, relationships, and source explanations retain coherent interaction semantics;
- the architecture remains valid across recursive depth;
- no semantic trust invariant is weakened.

## Explicit non-goals

Do not implement:

- final universal pedagogical renderer;
- personalized learner modeling;
- model-generated explanations;
- new semantic depth generation;
- new domain facts;
- new canonical relationships;
- semantic predicate changes;
- broad UI redesign;
- navigation history/timeline UI;
- automatic depth triggering;
- baseline promotion;
- unrelated refactoring.

## Required durable report

Record at least:

- frozen/baseline hash verification;
- files changed;
- SPEC-029 interaction/context seams preserved;
- representation resolver/seam introduced;
- representation forms implemented and deterministic selection rules;
- semantic inputs used by each representation;
- duplicate-map guard result;
- fixed evaluation-case results;
- classification of the owner-observed Software Architecture / History of Printing propagation gaps;
- map ↔ learning-surface semantic-state agreement results;
- bidirectional interaction results where applicable;
- recursive depth results;
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

- `SPEC-030` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep implementation detail in the durable report.

## Final constraint

Do not solve this experiment by making the map less capable or by giving the learning surface independent semantic state.

Establish the stronger product invariant:

> **One semantic state, two complementary responsibilities: navigate on the map; understand on the learning surface.**
