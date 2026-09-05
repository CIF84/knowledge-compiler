# SPEC-027 — Recursive Bidirectional Interaction Grammar

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can all learner-visible knowledge—parent map, first depth expansion, and further recursive depth—use one bidirectional map ↔ representation ↔ explanation interaction grammar, so depth changes only knowledge availability and never interface behavior?

## Owner verdict on SPEC-026

Record SPEC-026 as:

```text
MIXED
```

Owner evidence:

- improved: deeper concepts are selectable;
- improved: deeper canonical relationship labels are readable;
- improved: right-pane content mirrors deeper-map selections;
- improved: explanatory/non-canonical material is more legible;
- failed: deeper-map hover does not behave like parent-map hover;
- failed: actions initiated in the right pane do not consistently mirror back to the deeper map;
- failed: the interaction contract remains asymmetric and depth-specific in observable behavior.

Preserve SPEC-026 unchanged as historical evidence. Do not promote it.

## Why this is next

SPEC-024 established continuous spatial expansion.
SPEC-025 established partial depth selection synchronization.
SPEC-026 improved semantic legibility of deeper connections.

The remaining defect is no longer best described as a missing hover handler or a missing reverse synchronization callback.

The stronger architectural problem is:

```text
parent-map interaction path != depth-map interaction path
```

That creates repeated parity defects.

The next experiment must therefore test whether parent and depth content can be driven through one semantic-object interaction contract rather than repairing another isolated depth symptom.

## Core principle

> **A learner should interact with any revealed knowledge using the same map ↔ representation ↔ explanation grammar regardless of how many depth expansions led to it.**

Stronger constraint:

> **Depth is a property of knowledge availability, never a property of interaction.**

## Experimental hypothesis

If every visible semantic object resolves through one shared current-focus/interaction pipeline based on semantic identity and type—not depth location—then hover, preview, selection, relationship inspection, evidence synchronization, and reverse mirroring will behave identically at ground level and arbitrary revealed depth.

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- SPEC-023/FIX-023 historical artifact;
- SPEC-024 continuous-map artifact;
- SPEC-025 depth-selection artifact;
- SPEC-026 semantic-interaction artifact;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, admission, and fail-closed behavior.

Create an isolated SPEC-027 evaluation. Do not overwrite prior evaluations or baselines.

## Experimental variable

The only product/architecture variable is:

```text
interaction dispatch + synchronization across revealed semantic objects
```

Control:

```text
SPEC-026
semantic legibility improved
map → right pane works at depth
but hover and right pane → map parity remain incomplete
```

Candidate:

```text
SPEC-027
one shared semantic-object interaction contract
used by parent map and every depth expansion
with bidirectional synchronization across map, representation, and explanation surfaces
```

No new knowledge generation or semantic regeneration is authorized.

## Required architectural seam

Prefer one interaction-resolution path conceptually equivalent to:

```text
visible semantic item
→ stable semantic identity
→ semantic class
→ interaction state transition
→ shared current focus
→ render all learner surfaces from that state
```

The implementation may choose the smallest safe form compatible with the repository, but learner-visible behavior must not depend on branches such as:

```text
if parent map ...
if first depth ...
if second depth ...
```

Depth/location metadata may remain necessary for spatial rendering and expansion ancestry. It must not define a separate learner interaction grammar.

## Core invariants

### 1. One current-focus contract

Concepts, canonical relationships, and learner-visible source-backed explanations must resolve to the same shared interaction state regardless of where they are rendered.

The same semantic object shown in multiple surfaces must behave as one object, not copies with independent state.

### 2. Map → right pane parity at every depth

For any visible semantic object at parent, depth 1, or synthetic depth 2:

- hover produces the ordinary preview behavior where that object type supports preview;
- click/select produces the ordinary selected behavior;
- `WHAT DOES THIS MEAN?` updates consistently;
- representation focus updates consistently;
- explanation/evidence detail updates consistently;
- stale prior focus is cleared consistently.

### 3. Right pane → map parity at every depth

Interaction initiated in the right representation/explanation surface must propagate back to the corresponding visible map object with the same preview/selection semantics as at the parent level.

At minimum:

- representation hover/preview mirrors on map where parent grammar supports it;
- representation click/select mirrors on map;
- canonical relationship focus mirrors on map;
- source-backed explanation focus mirrors on map;
- clear selection clears synchronized map state;
- switching among items never leaves stale highlights at another depth.

### 4. Hover invariance

Any object class that reacts to hover at the accepted parent level must react equivalently when rendered inside a depth expansion.

Do not introduce a distinct `deep hover` visual or semantic contract.

### 5. Relationship invariance

Canonical relationships at any depth must preserve:

- interaction target;
- direction where semantically directional;
- predicate label;
- preview/selection grammar;
- map ↔ right-pane synchronization;
- explanation/evidence behavior.

### 6. Explanatory attachment invariance

Source-backed/non-canonical explanatory items must preserve their honest non-canonical status while participating in the same synchronization machinery.

They must not be promoted to canonical relationships for convenience.

### 7. Recursive-depth invariance

Include a deterministic synthetic second expansion sufficient to verify that the same interaction machinery works another level down.

The second expansion is a regression fixture, not new product semantics.

No depth-number-specific event grammar is permitted.

### 8. Spatial depth remains independent

Preserve SPEC-024 behavior:

- expansion appears in the knowledge map;
- ancestry/path remains visible;
- pan and geometric zoom remain ordinary;
- collapse/retraction remains predictable;
- expanded structure can exceed the original panel without requiring a separate navigation mode.

Interaction unification must not collapse the spatial expansion back into a right-pane-only view.

### 9. One learning surface

Preserve:

```text
WHERE AM I?       → spatial knowledge world
WHAT DOES THIS MEAN? → active explanatory/representation surface
```

Do not create a separate deep inspector, modal, breadcrumb stack, depth toolbar, or alternate interaction mode.

## Bidirectional parity matrix

Before owner review, mechanically demonstrate the same expected behavior for parent, depth 1, and synthetic depth 2:

| Interaction | Parent | Depth 1 | Depth 2 |
| --- | --- | --- | --- |
| map concept hover → right preview | PASS | PASS | PASS |
| map concept click → right selection | PASS | PASS | PASS |
| right concept hover → map preview | PASS | PASS | PASS |
| right concept click → map selection | PASS | PASS | PASS |
| map relationship hover/preview | PASS | PASS | PASS |
| map relationship click/select | PASS | PASS | PASS |
| right relationship focus → map | PASS | PASS | PASS |
| explanation focus → map | PASS | PASS | PASS |
| evidence synchronization | PASS | PASS | PASS |
| clear selection | PASS | PASS | PASS |
| stale focus suppression | PASS | PASS | PASS |

If a particular parent object type does not support one of these interactions today, preserve the parent behavior and require equality rather than inventing new ground-level functionality. Record the exact exception in the durable report.

## Preserve accepted learner grammar

Outside the interaction seam, preserve:

- BASELINE-004 workspace shell and visual language;
- region orientation;
- current typography, color, spacing, controls, and node geometry;
- pan and zoom;
- selection and preview styling;
- relationship direction/predicate labels from SPEC-026;
- canonical vs non-canonical distinction;
- SPEC-024 expansion geometry/path;
- SPEC-025/026 evidence synchronization where already correct;
- no browser-native blue text/drag selection artifacts.

This is not a general UI redesign.

## Semantic trust invariants

This packet changes interaction/state plumbing only.

Preserve:

- trusted semantic IR;
- canonical predicates;
- exact evidence/provenance;
- rejected/demoted causal proposal remains rejected/demoted;
- no fabricated semantic edges;
- no semantic vocabulary changes;
- no weakened grounding or admission;
- no semantic enrichment.

If interaction parity appears to require semantic invention, stop and report the conflict.

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
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
known rejected causal item not promoted
pairwise-edge fabrication = 0
ordinary BASELINE-004 navigation intact
SPEC-024 continuous spatial expansion intact
SPEC-026 canonical/non-canonical legibility intact
shared semantic-object interaction path used across parent/depth where practical
parent concept hover behavior preserved
depth-1 concept hover parity passes
depth-2 concept hover parity passes
parent map → right-pane behavior preserved
depth-1 map → right-pane parity passes
depth-2 map → right-pane parity passes
parent right-pane → map behavior preserved
depth-1 right-pane → map parity passes
depth-2 right-pane → map parity passes
canonical relationship interaction parity passes at all tested depths
source-backed explanation synchronization parity passes at all tested depths
clear-selection parity passes at all tested depths
switching depth/objects leaves no stale focus
pan/zoom functional with expansion open
collapse/retraction remains predictable
browser hover/click behavior manually verified
browser console clean
full offline suite passes
```

If any machine gate fails, do not request owner review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-027-recursive-bidirectional-interaction-grammar-<date>/
```

Do not mutate BASELINE-004 or prior SPEC evaluations.

## Owner review

Do not prime the owner with implementation details.

If the machine gate passes, provide only the low-attention completion handoff, exact viewer command, and approximately this task:

```text
Explore the map naturally. Open the double-slit deeper structure and interact with concepts, relationships, and explanations both on the map and in the right pane. Use hover and click naturally in both places. Tell me whether the interface now behaves like one continuous map at every level, or whether anything still behaves differently simply because it is deeper.
```

## Owner-review questions for ChatGPT

After spontaneous feedback, evaluate:

- Does hover feel identical at parent and depth?
- Does selection feel identical at parent and depth?
- Do actions initiated in either pane mirror bidirectionally?
- Do canonical relationships preserve the same grammar everywhere?
- Do source-backed explanations remain honest and synchronized?
- Does recursive depth feel like more map rather than a new UI mode?
- Is any remaining difference attributable to semantic type rather than depth level?

## Verdict set

Final subjective verdict must be exactly one of:

```text
RECURSIVE_INTERACTION_INVARIANT
MIXED
DEPTH_STILL_HAS_SEPARATE_GRAMMAR
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`RECURSIVE_INTERACTION_INVARIANT` requires owner evidence that parent, first expansion, and further expansion all feel like the same interface: hover, preview, selection, relationship inspection, right-pane interaction, evidence synchronization, and clear-selection behavior remain bidirectionally coherent, while spatial expansion and semantic honesty are preserved.

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
- new workspace shell;
- general visual redesign;
- automatic depth triggering;
- baseline promotion;
- unrelated refactoring.

## Required durable report

Record at least:

- exact frozen/baseline hashes;
- files changed;
- previous parent-vs-depth interaction seams found;
- shared interaction/state seam implemented;
- any unavoidable location/depth metadata retained and why;
- full bidirectional parity matrix with parent/depth-1/depth-2 results;
- semantic-invariant checks;
- deterministic regeneration result where relevant;
- browser hover/click verification;
- console result;
- full offline tests;
- dependencies/live calls;
- deviations;
- commit/push state;
- exact viewer command.

## Low-attention completion handoff

On successful implementation, return only:

- `SPEC-027` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep implementation detail in the durable report.

## Final constraint

Do not solve this by adding another depth-specific callback path.

This experiment exists to test one architectural/product idea:

> **Depth may reveal more knowledge, but every revealed object must remain inside the same bidirectional learner interaction system.**
