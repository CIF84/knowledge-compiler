# SPEC-028 — Single Canonical Interaction State

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can every learner-visible semantic object at every revealed depth be rendered from one canonical interaction state, so map and representation surfaces never synchronize copies of state and recursive depth becomes interaction-invariant by construction?

## Owner verdict on SPEC-027

Record SPEC-027 as:

```text
MIXED
```

Owner evidence:

- improved: deeper-map nodes now respond to click;
- improved: deeper relationships are visibly labeled;
- improved: map → right-pane selection propagation works substantially better;
- improved: right pane behaves as the active explanation surface;
- failed: map and right-pane states are still not mirrored reliably;
- failed: right-pane actions can appear as hover/preview rather than selection on the map;
- failed: an object can appear active in one surface and inactive in the other;
- failed: stale or conflicting highlights can remain after switching targets;
- failed: parity remains insufficient for arbitrary recursive depth.

Preserve SPEC-027 unchanged as historical evidence. Do not promote it.

## Why this is next

SPEC-027 attacked depth-specific event handling by introducing a shared semantic-object interaction path. The owner review shows that this was necessary but not sufficient.

The remaining defect is architectural:

```text
map interaction state
↕ synchronization
representation interaction state
```

The system still behaves as though two surfaces own related state and attempt to mirror each other.

That architecture is fragile under recursion because every additional revealed depth introduces another rendering location that must remain perfectly synchronized.

The next experiment must therefore test a stronger model:

```text
one canonical learner interaction state
→ map projection
→ representation projection
→ explanation projection
```

No surface owns independent semantic interaction state.

## Core principle

> **There is exactly one learner interaction state. Every learner-visible surface is a projection of it.**

And:

> **Depth is metadata for knowledge availability and geometry, never for interaction state.**

## Experimental hypothesis

If hover, preview, selection, relationship focus, explanation focus, clear-selection, and stale-focus suppression are represented once in a canonical semantic interaction state keyed by stable semantic identity, then all surfaces at all depths will render identical interaction meaning without bidirectional synchronization logic.

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- SPEC-023/FIX-023 historical artifact;
- SPEC-024 continuous-map artifact;
- SPEC-025 depth-selection artifact;
- SPEC-026 semantic-interaction artifact;
- SPEC-027 recursive-interaction artifact;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, admission, and fail-closed behavior.

Create an isolated SPEC-028 evaluation. Do not overwrite prior evaluations or baselines.

## Experimental variable

The only architecture/product variable is:

```text
semantic interaction state ownership
```

Control:

```text
SPEC-027
shared semantic-object routing exists
but observable state can still diverge across learner surfaces
```

Candidate:

```text
SPEC-028
one canonical semantic interaction store/state machine
all learner surfaces render from the same state
no surface-to-surface state mirroring
```

No semantic regeneration or new knowledge generation is authorized.

## Required architectural seam

Prefer a model conceptually equivalent to:

```text
user action from any learner surface
→ resolve stable semantic identity + semantic class
→ dispatch one canonical interaction event
→ canonical interaction reducer/state transition
→ one resulting learner interaction state
→ render map projection from state
→ render representation projection from state
→ render explanation/evidence projection from state
```

The exact implementation may differ, but the contract forbids independent semantic selection/hover ownership in map and representation surfaces.

Surface-local state may exist only for genuinely local presentation concerns such as pan/zoom, DOM geometry, animation timing, or scroll position. It must not encode semantic hover, semantic preview, semantic selection, active relationship, or active explanation independently.

## Canonical state requirements

The canonical interaction state must minimally distinguish, where the accepted parent grammar already distinguishes them:

- semantic hover / transient preview target;
- semantic selected / committed focus target;
- semantic object class;
- stable semantic identity;
- canonical relationship focus;
- source-backed explanation focus;
- expansion ancestry needed to locate visible instances;
- clear/no-focus state.

Do not collapse hover and selection merely to simplify implementation.

If the same semantic object is rendered in more than one place, all visible instances must derive styling and active behavior from the same semantic identity and canonical state.

## Stable semantic identity invariant

Every learner-visible concept, canonical relationship, and source-backed explanation participating in interaction must resolve to a stable identity independent of:

- parent vs revealed depth;
- depth number;
- map vs right-pane representation;
- duplicate visual instance;
- current geometric location.

Rendering-location identifiers may coexist for DOM targeting, but they must not become the authoritative semantic interaction identity.

## One-way projection invariant

Forbidden architecture:

```text
map state changes
→ update representation state
→ update map state
```

or any equivalent bidirectional state-copy mechanism.

Required architecture:

```text
canonical state changes once
→ every surface observes/renders it
```

Events may originate from any surface. State must not.

## Recursive interaction invariants

### 1. Hover parity

For every object class supporting hover at ground level:

- hovering any visible instance dispatches the same canonical hover event;
- all other visible instances/projections of that semantic object render the corresponding preview state;
- hover exit clears only transient hover state and never silently destroys committed selection;
- behavior is identical at parent, depth 1, and deeper synthetic depths.

### 2. Selection parity

Click/select from map or representation must produce the same canonical selected state.

The resulting visual/semantic meaning must be identical regardless of event origin.

A selected object must never appear merely hovered in another projection.

### 3. Relationship parity

Canonical relationship interaction must use stable relationship identity and one state path.

Direction, predicate label, selection, preview, evidence, and corresponding map emphasis must all derive from the same canonical state.

### 4. Source-backed explanation parity

Source-backed/non-canonical explanation items remain non-canonical but participate in the same canonical interaction system.

Selecting or previewing one in either pane must project coherently everywhere it is visible.

### 5. Clear-selection parity

`Clear selection` dispatches one canonical clearing transition.

After clear:

- no stale selected object remains in any map depth;
- no stale selected object remains in the representation;
- no stale relationship/explanation state remains;
- transient hover may subsequently appear normally.

### 6. Switching-target parity

Switching from A → B must result in exactly one selected target B unless the accepted parent grammar specifies otherwise.

No prior A state may survive in another projection.

### 7. Duplicate-instance parity

If one semantic object appears in both a parent context and a revealed expansion, or in map and representation simultaneously, interaction with any instance must update all visible instances from one canonical state.

No copy may maintain independent active/inactive meaning.

### 8. Arbitrary-depth invariance

Depth must not appear in semantic interaction branching.

The same reducer/transition path must support a deterministic synthetic recursive fixture of at least 10 revealed depth levels.

This fixture need not introduce new product semantics. It exists to falsify depth-specific state behavior.

At every tested depth, the same event sequence must yield the same canonical semantic state and equivalent projected state.

## Ten-level deterministic recursion fixture

Create or extend an isolated deterministic regression fixture sufficient to test at least depths 0 through 10.

The fixture may reuse synthetic semantic objects and relationships. It must not modify trusted product semantics.

For each depth, mechanically exercise at least:

```text
hover concept
click/select concept
hover canonical relationship
click/select canonical relationship
focus source-backed explanation
switch concept A → B
switch relationship → concept
right-pane concept click
right-pane relationship click
right-pane explanation click
clear selection
hover after clear
```

The expected canonical interaction-state transitions must be depth-independent.

## State-transition parity matrix

Produce a deterministic report comparing event results across depths 0, 1, 2, 5, and 10 at minimum.

For each event record:

- canonical semantic identity;
- semantic class;
- hover target;
- selected target;
- active relationship/explanation identity where applicable;
- map projected state;
- representation projected state;
- explanation projected state;
- stale-state count.

Required result:

```text
semantic state equality across tested depths = PASS
surface projection agreement = PASS
stale-state count = 0
```

## Observable owner-facing invariants

The owner should be unable to tell from interaction behavior whether an object is at depth 0, depth 1, or depth 10.

Specifically:

- hover means the same thing everywhere;
- click means the same thing everywhere;
- selected styling means the same thing everywhere;
- map and right pane always agree on the active semantic object;
- switching target never leaves stale focus elsewhere;
- relationship interaction never degrades with depth;
- source-backed explanation interaction never degrades with depth;
- recursion changes only what knowledge is visible and where it is spatially placed.

## Preserve spatial depth behavior

Preserve SPEC-024 behavior:

- expansion occurs in the knowledge map;
- ancestry/path remains visible;
- pan/zoom remain ordinary;
- expanded structure may exceed the panel;
- collapse/retraction remains predictable.

Canonical semantic state must remain independent from pan/zoom and layout state.

## Preserve accepted learner grammar

Outside the state-ownership seam, preserve:

- BASELINE-004 workspace shell and visual language;
- `WHERE AM I?` spatial world;
- `WHAT DOES THIS MEAN?` active representation/explanation surface;
- current typography, spacing, controls, colors, and node geometry;
- accepted preview vs selected visual distinction;
- relationship direction/predicate labels;
- canonical vs non-canonical distinction;
- evidence/provenance display;
- current depth-expansion geometry;
- no browser-native blue selection artifacts.

This is not a UI redesign.

## Semantic trust invariants

This packet changes interaction architecture only.

Preserve:

- trusted semantic IR;
- canonical predicates;
- exact evidence/provenance;
- rejected/demoted causal proposal remains rejected/demoted;
- no fabricated semantic edges;
- no semantic vocabulary changes;
- no weakened grounding/admission;
- no semantic enrichment.

If architectural unification appears to require semantic invention, stop and report the conflict.

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
SPEC-024 preserved unchanged
SPEC-025 preserved unchanged
SPEC-026 preserved unchanged
SPEC-027 preserved unchanged
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
known rejected causal item not promoted
pairwise-edge fabrication = 0
ordinary BASELINE-004 navigation intact
continuous spatial expansion intact
canonical/non-canonical legibility intact
exactly one authoritative semantic interaction state path exists
map does not own independent semantic hover/selection state
representation does not own independent semantic hover/selection state
explanation surface does not own independent semantic focus state
stable semantic identity is independent of depth/location
same semantic object rendered twice resolves to one state
hover and selection remain distinct
map-origin and representation-origin click yield identical selected state
map-origin and representation-origin hover yield identical preview semantics
relationship focus is projection-consistent
source-backed explanation focus is projection-consistent
clear selection produces zero stale semantic state
switching A → B produces zero stale A state
depths 0,1,2,5,10 pass deterministic state-transition equality
10-level synthetic recursion uses no depth-specific semantic state branch
pan/zoom remain functional
collapse/retraction remains predictable
browser hover/click behavior manually verified
browser console clean
full offline suite passes
```

If any machine gate fails, do not request owner review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-028-single-canonical-interaction-state-<date>/
```

Do not mutate BASELINE-004 or prior SPEC evaluations.

## Owner review

Do not prime the owner with implementation details.

If the machine gate passes, provide only the low-attention completion handoff, exact viewer command, and approximately this task:

```text
Explore the map naturally. Open the double-slit deeper structure and interact with concepts, relationships, and explanations in both the map and the right pane. Switch rapidly among items, hover and click in both places, clear selection, and repeat after moving deeper. Tell me whether the two surfaces ever disagree about what is hovered, selected, active, or inactive, or whether depth still changes how interaction behaves.
```

## Owner-review questions for ChatGPT

After spontaneous feedback, evaluate:

- Do map and right pane always agree on preview vs selected state?
- Does event origin matter observably?
- Can any stale highlight survive target switching?
- Does clear-selection clear all projections coherently?
- Do canonical relationships behave identically everywhere?
- Do source-backed explanations remain synchronized and honestly non-canonical?
- Does recursive depth feel interaction-invariant?

## Verdict set

Final subjective verdict must be exactly one of:

```text
CANONICAL_INTERACTION_STATE_CONFIRMED
MIXED
STATE_STILL_DIVERGES
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`CANONICAL_INTERACTION_STATE_CONFIRMED` requires owner evidence that map and representation behave as projections of one semantic interaction state: hover, preview, selection, relationship focus, explanation focus, switching, and clear-selection remain coherent regardless of event origin or depth, with no stale or contradictory active states.

## Explicit non-goals

Do not implement:

- new semantic depth generation;
- new quantum facts;
- new canonical relationships;
- semantic predicate changes;
- guided Journey/course mode;
- personalization;
- history/timeline UI;
- browser back-stack navigation;
- workspace redesign;
- general visual redesign;
- automatic depth triggering;
- baseline promotion;
- unrelated refactoring.

## Required durable report

Record at least:

- frozen/baseline hash verification;
- files changed;
- semantic state owners/seams found in SPEC-027 implementation;
- canonical state representation introduced or consolidated;
- event dispatch/reducer path;
- stable semantic identity strategy;
- any retained surface-local state and why it is non-semantic;
- deterministic 10-level recursion fixture design;
- state-transition equality results;
- surface-projection agreement results;
- stale-state checks;
- semantic-invariant checks;
- browser hover/click verification;
- console result;
- full offline tests;
- dependencies/live calls;
- deviations;
- commit/push state;
- exact viewer command.

## Low-attention completion handoff

On successful implementation, return only:

- `SPEC-028` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep implementation detail in the durable report.

## Final constraint

Do not solve this by adding more synchronization callbacks.

This experiment exists to test one architectural idea:

> **One semantic interaction state must drive every projection, at every depth.**
