# SPEC-025 — Depth-Invariant Interaction Grammar

Status: `APPROVED`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can every revealed knowledge element use the same map ↔ representation ↔ explanation/evidence interaction grammar regardless of depth, so that depth changes what knowledge is available without changing how the learner interacts with it?

## Why this is next

Owner review of SPEC-024 validates the central spatial-depth hypothesis: deeper material feels like a continuation of the same knowledge world, the origin/path remains visible, pan/zoom gives the deeper structure room, and the right pane remains an explanation surface.

The remaining defect is interaction asymmetry.

At the accepted/base level, selection behaves as a synchronized contract:

```text
map selection
↔ right-side representation
↔ explanation / evidence
```

At the SPEC-024 deeper level, the map expands correctly, but deeper selections are treated as a special class. Selecting `photon`, `electron`, `wave-particle duality`, `interference-pattern`, or source-backed explanatory material can update a lower detail area while the upper `WHAT DOES THIS MEAN?` representation remains anchored to the original double-slit relationship. The learner therefore sees two different interaction grammars depending on how the selected knowledge was reached.

The owner expectation is stronger and simpler:

> Depth should change what knowledge is available, not how the interface behaves.

A concept revealed through depth is still a concept. A canonical relationship revealed through depth is still a canonical relationship. Source-backed explanatory material retains its existing semantic distinction, but should participate in the same selection/synchronization grammar appropriate to its type.

## Experimental hypothesis

If selection and explanatory synchronization are made depth-invariant, deeper exploration will feel like ordinary navigation through progressively revealed knowledge rather than navigation through a special nested subsystem.

The intended invariant is:

```text
ANY VISIBLE SELECTABLE KNOWLEDGE ITEM
        ↓
select on map
        ↓
WHAT DOES THIS MEAN? updates to that selection
        ↓
appropriate representation / context appears
        ↓
explanation and evidence synchronize
        ↓
map and right pane mirror the same current focus
```

The right pane should not need to know that an item is a "deeper concept" merely to explain it.

## Owner verdict on SPEC-024

Record SPEC-024 as:

```text
DEPTH_NAVIGATION_BETTER
```

with an interaction gap carried into this packet.

Do not promote SPEC-024 to an accepted baseline as part of this packet unless separately authorized after owner review of SPEC-025.

Preserve SPEC-024 unchanged as a functional historical experiment/snapshot.

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- SPEC-023/FIX-023 historical depth artifact;
- SPEC-024 continuous-map depth artifact;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior.

Create an isolated SPEC-025 evaluation. Do not overwrite previous evaluations.

## Experimental variable

The only product variable is **interaction/synchronization behavior for knowledge selected inside an expanded depth region**.

Control:

```text
SPEC-024
continuous spatial depth expansion works
but deeper selections use partial/special-case explanatory behavior
```

Candidate:

```text
SPEC-025
continuous spatial depth expansion retained
+ same selection grammar at parent and deeper levels
+ right pane follows the actual current selection
```

Do not use this packet as permission for semantic regeneration, general UI redesign, new course UI, or new depth-generation behavior.

## Core interaction invariant

### 1. Selection semantics are depth-invariant

For a selectable concept or relationship, interaction must be determined by semantic/item type and current selection — not by whether the item lives in the parent map or a depth expansion.

Avoid durable concepts such as `selected deeper concept` if ordinary `selected concept` semantics are sufficient.

Depth/provenance may remain available as contextual metadata, but must not create a second learner interaction grammar.

### 2. `WHAT DOES THIS MEAN?` follows current focus

When the learner selects a deeper concept, canonical relationship, or source-backed explanation, the upper right learning surface must update appropriately for that current focus.

It must not remain misleadingly pinned to the relationship that originally opened the depth expansion.

The origin relationship remains spatially visible/recoverable on the map and may be represented as ancestry/context, but it is not the current explanatory focus unless selected.

### 3. Right-pane and map selection mirror one another

At every tested depth:

- map selection must produce the corresponding right-pane focus;
- right-pane representation/detail/evidence must correspond to the same selected identity;
- preview vs selected behavior must remain coherent;
- focus suppression/highlighting must remain coherent;
- clearing/changing selection must not leave stale deeper detail behind.

### 4. Item type determines presentation

Reuse the existing accepted grammar wherever possible:

- concept → concept representation/detail;
- canonical relationship → relationship representation/detail + evidence;
- source-backed explanation → explicitly non-canonical explanatory detail + exact evidence/provenance.

Do not flatten semantic-strength distinctions merely to make the UI uniform.

Uniform interaction does **not** mean pretending all knowledge items have the same semantic status.

### 5. Depth expansion remains spatial

Retain the successful SPEC-024 model:

- deeper knowledge appears in the continuous map;
- origin/path remains visible or spatially recoverable;
- pan/zoom work normally;
- parent and child material can be traversed without a modal return stack;
- collapse/retraction remains predictable if exposed.

Do not regress to nested replacement views.

### 6. Recursion uses the same contract

Only one real trusted semantic depth level is required in the owner-facing quantum fixture.

However, deterministic fixture tests must demonstrate that if a concept inside an expansion exposes another expansion, selections in that second expansion use the same synchronization contract rather than introducing `depth-2` special handling.

The architectural target is conceptually:

```text
selection(item)
→ resolve presentation from item identity/type/context
→ synchronize map + learning surface
```

not:

```text
if parent ...
if deeper ...
if deeper-deeper ...
```

This is guidance, not a mandated implementation schema.

## Preserve accepted learner grammar

Outside the narrow synchronization seam, preserve:

- two-pane `WHERE AM I?` / `WHAT DOES THIS MEAN?` workspace;
- continuous world overview;
- region entry/orientation;
- pan and geometric zoom;
- concept and relationship selection;
- selected/preview styling;
- focus suppression;
- evidence synchronization;
- BASELINE-004 visual language;
- SPEC-024 spatial expansion/origin/path behavior;
- no blue browser selection/drag artifacts.

No general typography, color, spacing, node, control, or layout redesign.

## Semantic trust invariants

This packet changes interaction only.

Preserve:

- canonical relationships as canonical;
- source-backed explanatory material as non-canonical;
- exact participant-preserving explanatory semantics;
- exact evidence/provenance;
- rejected/demoted overstated causal item remains rejected/demoted;
- no fabricated pairwise edges;
- no semantic vocabulary changes;
- no weakened grounding/admission rules.

If uniform interaction appears to require changing semantic truth, stop and report the conflict.

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
- agent/model judging.

Use committed artifacts and deterministic fixture logic only.

## Mechanical gate

Before owner review, verify at least:

```text
BASELINE-001..004 hashes unchanged
SPEC-023/FIX-023 preserved
SPEC-024 preserved unchanged
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
known rejected causal item not promoted
pairwise-edge fabrication = 0
ordinary BASELINE-004 navigation behavior intact
SPEC-024 continuous map expansion behavior intact
select deeper concept → WHAT DOES THIS MEAN? updates to that concept
select deeper canonical relationship → right pane updates to that relationship and evidence
select source-backed explanation → right pane identifies it as non-canonical and shows synchronized evidence
switch among deep items → no stale previous selection/detail remains
switch from deep item back to parent item → normal parent interaction resumes without special reset
map highlight/suppression mirrors right-pane focus at depth
clear selection behaves coherently at depth
synthetic second expansion uses the same interaction contract
pan/zoom remain functional with expansion open
collapse/retraction, if exposed, restores predictable state
browser drag creates no blue selection artifacts
browser console clean in normal interaction
full offline suite passes
```

If any machine gate fails, do not request owner cognitive review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-025-depth-invariant-interaction-grammar-<date>/
```

Do not mutate BASELINE-004 or previous SPEC evaluations to produce it.

## Owner review

Do not prime the owner with implementation architecture.

If the machine gate passes, provide only the concise low-attention handoff, exact viewer command, and this approximate task:

```text
Navigate naturally to the double-slit experiment and explore deeper. Once the deeper map opens, select several different concepts, relationships, and explanatory items. Move back and forth between deeper material and the surrounding electromagnetism material. Tell me whether the map and the learning pane now feel like one synchronized interface everywhere, and note anything that behaves differently or leaves you unsure what is currently selected or explained.
```

## Owner-review questions for ChatGPT

After spontaneous feedback, evaluate:

### Interaction invariance

- Does selecting an item feel the same regardless of depth?
- Does `WHAT DOES THIS MEAN?` consistently follow the learner's actual focus?

### Mirroring

- Do map highlighting and right-pane content represent the same selected identity?
- Are preview, selection, clearing, and switching coherent?

### Recursion

- Does the interaction model appear capable of continuing through another expansion without introducing a new mode or return stack?

### Learning

- Does the learner gain context from deeper structures without losing the explanation surface?
- Is parent context still recoverable while the selected deeper item receives full attention?

### Trust

- Are canonical relationships and non-canonical source-backed explanations still visually/semantically distinct?
- Does uniform interaction accidentally imply uniform semantic authority?

## Verdict set

Final subjective verdict must be exactly one of:

```text
DEPTH_INTERACTION_INVARIANT
MIXED
DEPTH_SPECIALIZATION_PREFERRED
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`DEPTH_INTERACTION_INVARIANT` requires owner evidence that parent and deeper knowledge now share one intuitive map ↔ learning synchronization grammar, `WHAT DOES THIS MEAN?` reliably follows current focus, semantic-strength distinctions remain honest, and the successful spatial continuity of SPEC-024 is preserved.

## Explicit non-goals

Do not implement:

- new semantic depth generation;
- new quantum facts;
- new representation archetypes unless strictly required by already-existing item types;
- semantic predicate/proposition changes;
- automatic semantic zoom/depth triggering;
- guided course/Journey mode;
- personalization;
- history/timeline UI;
- browser-style back-stack UI;
- a new workspace shell;
- a new global navigation panel;
- baseline promotion;
- unrelated polish/refactoring.

## Required durable report

Record at least:

- exact baseline and frozen-input hashes;
- SPEC-024 preserved-state evidence;
- files changed;
- selection/synchronization integration seam;
- how current focus is resolved independent of depth;
- concept/relationship/explanation synchronization tests;
- synthetic second-expansion regression result;
- camera/pan/zoom behavior;
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

- `SPEC-025` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep detailed inventories in the durable report.

## Final constraint

Do not solve interaction consistency by adding another depth-specific mode.

This experiment exists to test one idea:

> **Knowledge may become deeper; the learner's interaction grammar should not.**
