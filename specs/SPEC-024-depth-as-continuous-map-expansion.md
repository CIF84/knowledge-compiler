# SPEC-024 — Depth as Continuous Map Expansion

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Does representing semantic depth as an expansion of the continuous knowledge map preserve orientation and chain of thought better than entering a nested replacement view, while retaining the accepted BASELINE-004 learner workspace and semantic trust?

## Why this is next

SPEC-023 proved that trustworthy semantic depth can be reached and explored inside the accepted learner workspace. FIX-023 repaired contextual entry, and owner review confirmed that `Explore deeper`, deeper interaction, and `Return` work correctly.

The remaining problem is interaction grammar, not semantic generation.

In SPEC-023, going deeper replaces the active learning representation with a nested deeper view. This works at one level but creates a scaling problem:

```text
world
  → depth A
      → depth B
          → depth C
```

The learner's actual chain of thought becomes a hidden return stack while the continuous map no longer depicts the route being followed.

The owner prefers a spatial model: **going deeper should expand the knowledge world itself**. The path taken should remain visible or spatially recoverable, and deeper structures should inherit the map's proven pan/zoom/navigation behavior rather than being constrained to a bounded learning-panel viewport.

See `debriefs/DEBRIEF-023-realistic-semantic-depth-through-explanatory-projection.md`.

## Experimental hypothesis

A deeper semantic structure will feel more intuitive and scalable if it is opened as a map expansion anchored to the concept or relationship that exposed it, while the right pane remains the explanation/evidence surface for the currently selected item.

The intended learner model is:

```text
LEFT: WHERE AM I?
continuous knowledge world
+ visible depth expansion
+ preserved origin / traversal path

RIGHT: WHAT DOES THIS MEAN?
representation/detail/evidence
for the current selection
```

Depth therefore becomes **navigation**, not a separate mode.

## Frozen control and protected state

BASELINE-004 remains the accepted learner-navigation baseline and must remain byte-identical.

Preserve all BASELINE-001 through BASELINE-004 assets byte-for-byte.

Also preserve the working SPEC-023/FIX-023 artifact as a functional historical snapshot. Do not overwrite it to implement this experiment.

The new experiment must be isolated under its own SPEC-024 evaluation directory.

## Frozen semantic inputs

Reuse the exact already-committed semantic material used by SPEC-023:

- frozen SPEC-020 double-slit semantic packet;
- SPEC-021 focus-preserving explanatory projection;
- known semantic-strength distinctions;
- exact source evidence/provenance;
- known rejected/demoted overstated causal item.

No semantic regeneration, enrichment, repair, reinterpretation, or new quantum facts are permitted.

The focus remains the existing `double-slit-experiment` depth seam.

## Experimental variable

The only product variable is **where and how the already-existing deeper structure appears during navigation**.

Control:

```text
SPEC-023
contextual Explore deeper
→ nested replacement deeper view
→ Return to parent
```

Candidate:

```text
SPEC-024
contextual Explore deeper
→ deeper structure expands into the continuous map
→ origin/path remains represented
→ selection continues through normal map ↔ learning synchronization
```

Do not use this packet as permission for general UI redesign.

## Required interaction

Starting from the accepted BASELINE-004-style world:

```text
WORLD
  ↓
enter Electromagnetism
  ↓
select double-slit relationship / eligible focus
  ↓
Explore deeper
  ↓
MAP EXPANDS at or from the depth origin
  ↓
learner navigates/selects deeper concepts and explanatory material
  ↓
right pane explains current selection
  ↓
learner can reorient to parent and deeper material without unwinding a modal stack
```

The exact geometry is deliberately not prescribed. Codex should choose the smallest deterministic implementation that tests the hypothesis while respecting the constraints below.

## Core depth-navigation invariants

### 1. The origin remains meaningful

Opening depth must preserve a legible connection to the originating concept or relationship.

The learner should be able to answer:

- where did this deeper structure come from?
- what was I exploring when I opened it?
- how do I get back to the surrounding world?

without relying on browser history or a sequence of modal `Return` clicks.

### 2. The map carries the chain of thought

The left knowledge world must encode the traversal spatially enough that the learner's route is not hidden exclusively in application state.

A breadcrumb may supplement this, but must not be the only representation of depth history.

### 3. The right pane remains explanatory

Do not turn the right pane into another navigation world.

It continues to show the appropriate representation, selected concept/relationship detail, semantic-strength distinction, and evidence for whatever the learner selects in the expanded world.

### 4. Depth uses map mechanics

Expanded deeper content must participate in the map's existing navigation grammar wherever applicable:

- pan;
- geometric zoom;
- stable coordinates within the experiment;
- selection;
- focus suppression/highlighting;
- map ↔ right-pane synchronization.

A large deeper structure must not require fitting all content into the right-pane viewport.

### 5. Expansion must be reversible without destructive disorientation

The learner must be able to close/collapse/retract an expansion if the implementation offers that action.

Doing so must preserve a predictable parent-world location and must not corrupt selection, camera, or semantic state.

Do not require multiple `Return` operations merely to understand where the learner is.

### 6. Future recursion must not be architecturally blocked

Only one real semantic depth level is required for the owner-facing fixture because that is the trustworthy material currently available.

However, the state model and interaction seam must not hard-code the assumption that there can only ever be one expansion.

Add deterministic tests using fixture data if needed to prove that a second nested expansion can be represented as another spatially anchored expansion/path rather than a modal replacement stack. Do not invent new canonical quantum semantics for this test.

## Preserve BASELINE-004 behavior

Outside the new depth-expansion seam, preserve the accepted learner grammar:

- two-pane `WHERE AM I?` / `WHAT DOES THIS MEAN?` workspace;
- continuous world overview;
- region entry/orientation;
- map dragging/panning;
- geometric zoom and Overview;
- concept selection;
- relationship selection;
- selected/preview styling;
- focus suppression;
- evidence synchronization;
- current visual language and layout behavior;
- no blue browser selection/drag artifacts.

Do not redesign controls, typography, colors, spacing, node styling, or ordinary region behavior unless a minimal change is strictly necessary to express the depth expansion.

## Semantic trust invariants

The experiment changes navigation only.

Preserve:

- canonical relationships as canonical;
- source-backed explanatory material as non-canonical;
- participant-preserving explanatory semantics;
- exact evidence/provenance;
- rejected causal item remains rejected/demoted;
- no fabricated pairwise edges;
- no semantic vocabulary changes;
- no weakened admission or grounding rules.

If the navigation experiment appears to require changing semantic truth, stop and report the conflict rather than changing semantics.

## No live calls

This packet is `OFFLINE_ONLY`.

Forbidden:

- OpenAI/provider/model calls;
- web retrieval;
- external enrichment;
- embeddings;
- assertion extraction;
- canonicalization;
- semantic retries;
- new agent/model judging.

Use only committed artifacts and deterministic fixture logic.

## Implementation guidance

Prefer extension/composition around the accepted workspace rather than copying or rewriting it.

The likely seam is a map-level depth-expansion state that can associate:

```text
origin identity
→ child/deeper projection identity
→ spatial expansion state
→ optional parent expansion identity
```

This is guidance, not a required schema.

Do not build a generalized production graph database, arbitrary recursive compiler, or new semantic-resolution engine. Implement only enough abstraction to avoid a one-off `double-slit` modal hack and to demonstrate that recursive spatial expansion is structurally possible.

## Mechanical gate

Before owner review, verify at least:

```text
BASELINE-001..004 hashes unchanged
SPEC-023/FIX-023 historical artifact preserved
SPEC-020 frozen semantic input hashes unchanged
SPEC-021 explanatory semantic payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
known rejected causal item not promoted
pairwise-edge fabrication = 0
ordinary BASELINE-004 navigation behavior intact
Explore deeper is still contextual
opening depth changes/extends the left map rather than replacing the right pane with a nested navigation world
depth origin remains identifiable after expansion
deep items are selectable through the normal synchronization grammar
right pane explains selected deep items/evidence
parent world remains navigable/recoverable without modal-stack unwinding
collapse/retraction, if exposed, restores predictable state
synthetic nested-expansion regression demonstrates no one-level hard-code
pan/zoom works with expanded structure
browser drag does not create blue selection artifacts
browser console clean in normal interaction
full offline suite passes
```

If any machine gate fails, do not ask for owner cognitive review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-024-depth-as-continuous-map-expansion-<date>/
```

Do not mutate the accepted baseline or SPEC-023 evaluation to produce it.

## Owner review

The owner should not be primed with implementation details before interaction.

If the machine gate passes, provide a concise handoff and exact viewer command only.

The human task should be approximately:

```text
Navigate naturally to the double-slit experiment and explore it more deeply. Then move around between the deeper material and the surrounding knowledge world. Tell me whether going deeper now feels like continuing to navigate the same knowledge space, whether you can still tell how you got there, and anything that feels awkward or confusing.
```

Do not ask the owner to inspect implementation architecture.

## Owner-review questions for ChatGPT

After spontaneous feedback, evaluate:

### Continuity

- Does `Explore deeper` feel like continuing the same navigation rather than opening a different mode?
- Does the learner retain a sense of where the deeper structure came from?

### Chain of thought

- Is the path from parent concept/relationship to deeper material spatially legible?
- Can the learner move among parent and child material without mentally unwinding a stack?

### Scale

- Does pan/zoom make deeper structures feel unconstrained by panel size?
- Does the design appear naturally extensible to another depth level?

### Learning

- Does the right pane remain useful as the explanation/evidence surface?
- Does adding depth to the map improve understanding without making the world visually incoherent?

### Trust

- Are canonical and explanatory semantics still represented honestly?
- Does the new spatial connection accidentally imply a canonical relationship that does not exist?

## Verdict set

Final subjective verdict must be exactly one of:

```text
DEPTH_NAVIGATION_BETTER
MIXED
NESTED_DEPTH_BETTER
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`DEPTH_NAVIGATION_BETTER` requires owner evidence that deeper material feels like a continuation of the same knowledge world, preserves the route/origin sufficiently for orientation, and retains BASELINE-004 learning and trust behavior without creating materially worse visual complexity.

## Explicit non-goals

Do not implement:

- new semantic depth generation;
- new quantum facts;
- production-grade arbitrary recursion;
- semantic zoom as an automatic depth trigger;
- guided course/Journey mode;
- personalization;
- history timeline UI;
- browser-style back-stack UI;
- a new overall workspace shell;
- a new global navigation panel;
- new representation archetypes;
- semantic predicate/proposition changes;
- baseline promotion;
- unrelated polish/refactoring.

## Required durable report

Record at least:

- exact baseline and frozen-input hashes;
- exact SPEC-023 preserved-state evidence;
- files changed;
- depth-expansion state/integration seam;
- how origin/path is represented;
- nested-expansion fixture/regression result;
- camera/pan/zoom behavior;
- selection/evidence synchronization result;
- semantic-invariant checks;
- deterministic regeneration result where relevant;
- browser verification result;
- full offline test result;
- dependencies/live calls;
- deviations;
- commit/push state;
- exact viewer command.

## Low-attention completion handoff

On successful implementation, Codex should return only:

- `SPEC-024` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep detailed inventories in the report.

## Final constraint

Do not solve depth by adding another navigation mode.

This experiment exists to test one idea:

> **The learner's chain of thought should remain part of the knowledge map.**
