# SPEC-021 — Focus-Preserving Explanatory Projection

## Status

Ready for implementation.

## Phase

Phase III — representation of trustworthy realistic-source meaning.

## Primary Question

> Can the exact frozen SPEC-020 grounded semantic packet produce a truthful, cognitively useful representation centered on `double-slit-experiment` without inventing canonical semantics or exposing assertion prose as the overview?

## Why This Experiment Is Earned

SPEC-020 produced a useful but rejected realistic child packet.

The semantic pipeline succeeded far enough to establish:

```text
9 grounded assertions
8 faithful / 1 partial
3 proposed relationships
2 supported / 1 overstated causality
6 claims
0 unknown symbols
0 entity minting
KnowledgeModel round-trip PASS
```

But ordinary structure detection produced only a two-node hierarchy that did not contain the requested focus `double-slit-experiment`.

The child was correctly rejected before BASELINE-003 rendering.

The first blocker is now representation admission, not source grounding or workspace navigation.

## Critical Distinction

SPEC-016 tested:

```text
assertions
→ show assertions/cards directly
→ cognitive overload
```

SPEC-021 tests something different:

```text
grounded assertions
→ deterministic explanatory projection
→ visual representation
```

Assertions are **inputs to representation construction**, not default learner-facing cards.

## Frozen Inputs

Use exactly the preserved SPEC-020 evaluation artifacts under:

```text
examples/evaluations/spec-020-realistic-semantic-depth-20260905/
```

At minimum consume and verify the exact frozen:

- focus-selection artifact;
- source scope;
- child grounded assertions;
- child canonicalization result;
- rejected semantic review;
- seven-symbol inventory;
- parent artifact hashes;
- BASELINE-003 manifest/hashes.

Do not rerun any model call.

Do not regenerate semantic content.

## Frozen Focus

The representation must remain centered on:

```text
double-slit-experiment
```

A projection that omits the focus fails the experiment even if another structure is valid.

## Frozen Semantic Review

The known `OVERSTATED_CAUSALITY` relationship from SPEC-020 must not be promoted into a trusted canonical edge in SPEC-021.

Use the preserved semantic-review classification as authoritative experimental input.

Do not presentation-repair the bad edge into a different canonical predicate.

## Representation Boundary

Introduce the smallest provider-independent presentation model needed to combine:

```text
TRUSTED CANONICAL STRUCTURE
+
SOURCE-BACKED EXPLANATORY MATERIAL
```

without merging their semantic status.

Possible conceptual form:

```text
ExplanatoryProjection
  focus_entity_id
  canonical_items
  explanatory_items
  participant_bindings
  evidence_refs
  presentation_links / roles
  layout metadata
```

Exact naming/schema is implementation choice.

Do not add these presentation constructs to canonical `KnowledgeModel`.

## Two Semantic Strengths

The projection must distinguish at least:

### 1. Canonical semantic structure

Existing trusted relationship/proposition semantics.

Examples:

```text
CAUSES
PART_OF
IS_A
...
```

Only independently accepted/trusted canonical items may appear in this tier.

### 2. Source-backed explanatory structure

Grounded assertion-derived presentation material that helps explain the focus but is not a canonical predicate commitment.

This tier may express things like:

- observation;
- contrast;
- condition/context;
- example/evidence;
- co-participation;
- explanatory statement;
- phenomenon associated with the focus.

These are **presentation roles**, not additions to the canonical relationship ontology.

## No Hidden New Ontology

Do not create a second unrestricted semantic predicate vocabulary under another name.

If explanatory roles are needed, keep them minimal and presentation-specific.

Prefer a tiny fixed set such as:

```text
OBSERVATION
CONTEXT
CONTRAST
EXPLANATION
EVIDENCE_OF_BEHAVIOR
```

only if deterministic rules can assign them from the frozen assertions without semantic invention.

If reliable deterministic role classification is not possible, use a more neutral presentation form rather than guessing labels.

A neutral `SOURCE_BACKED_EXPLANATION` item attached to participants is preferable to a misleading pseudo-predicate.

## Deterministic Construction Only

SPEC-021 is offline.

Do not use:

- OpenAI/provider calls;
- embeddings;
- external enrichment;
- LLM classification;
- manually authored quantum facts;
- hand-curated semantic edges;
- post-hoc rewriting of assertions.

Construction must derive only from frozen artifacts.

## Focus-Centered Selection

Not every assertion needs to appear simultaneously.

Select explanatory material deterministically around the focus.

Permissible signals include:

```text
assertion directly contains focus participant
assertion contains a canonical neighbor of focus
shared participant count
existing trusted relationship adjacency
source-span proximity within the frozen scope
```

Record exact rule and diagnostics.

Do not rank using domain knowledge.

## Participant-Preserving Projection

An N-participant assertion may visually connect/attach those participants as one explanatory unit.

Do not flatten it into pairwise canonical edges.

For example:

```text
assertion A
participants: double-slit-experiment, electron, interference-pattern
```

may become one explanatory object associated with all three concepts.

It must not silently become:

```text
double-slit → electron
double-slit → interference-pattern
electron → interference-pattern
```

unless those relationships independently exist canonically.

## Visual Design Constraint

The output should look like a **representation**, not a document.

Preserve the BASELINE-001 / BASELINE-003 learning-surface principles:

- spatial structure first;
- explicit focal concept;
- low default prose density;
- text on demand;
- focus suppression;
- evidence inspectable after selection;
- clear relationship trajectories where canonical;
- restrained explanatory attachments where non-canonical.

Do not recreate SPEC-016 card overload.

## Suggested Visual Grammar

A reasonable experiment is:

```text
canonical concept nodes
        +
strong canonical directed edges where trusted
        +
small explanatory anchors/callouts associated with relevant participants
```

Explanatory items may use:

- small neutral markers;
- bracket/group attachments;
- dashed/non-arrowed connectors;
- compact one-line labels;
- another clearly weaker grammar.

Do not rely on color alone.

Do not make explanatory links look like canonical arrows.

## Text Budget

At initial load:

- concept labels are visible;
- canonical predicate labels may be visible;
- explanatory items should be short labels or hidden indicators;
- full assertion prose hidden by default;
- evidence quotes hidden by default.

Selecting an explanatory item may reveal the exact grounded assertion in the detail surface.

Selecting evidence may reveal the source quote/span.

## Focus Preservation

`double-slit-experiment` must be visually obvious as the central/current focus.

The projection should answer, without reading all prose:

```text
What happens in/around the double-slit experiment?
Which concepts participate?
Which relationships are strong canonical semantics?
Which additional source-backed observations explain the phenomenon?
```

## Representation Archetype

Do not force the result into one existing structure type merely to pass the detector.

SPEC-021 may introduce an **explanatory projection type at the presentation layer** if needed.

This is not a new semantic structure type.

Possible name:

```text
FOCUS_EXPLANATORY_PROJECTION
```

It means only:

> a presentation assembled around a focus from mixed trusted canonical and source-backed explanatory material.

## Existing Structure Detection

Do not modify global structure-detection thresholds in SPEC-021.

The ordinary hierarchy/causal/process/dependency/feedback detector remains unchanged.

The explanatory projection is a fallback/parallel presentation path for a trusted semantic packet that lacks a focus-preserving canonical structure.

## Admission Rule

The explanatory projection may be built only when:

1. focus exists in frozen symbol inventory;
2. grounded assertions involving focus exist;
3. assertion evidence is valid;
4. known rejected canonical items remain excluded/demoted;
5. no semantic item is invented;
6. focus appears in the final representation.

## BASELINE-003 Integration

If machine integrity passes, render the projection inside the frozen BASELINE-003 learning surface.

The left navigation surface remains the same stable parent context from SPEC-020's offline integration fixture.

Do not redesign the workspace.

The right learning surface displays the explanatory projection as the deeper resolution of `double-slit-experiment`.

## Parent / Child Context

Preserve a minimal depth cue showing that the explanatory projection is deeper detail for the selected parent focus.

Do not restore full Explore/Back page navigation.

Returning to parent resolution should preserve left-map camera state.

## Evidence Behavior

Canonical item selection:

```text
select
→ canonical detail
→ predicate meaning
→ exact evidence
```

Explanatory item selection:

```text
select
→ grounded assertion text
→ participant concepts
→ exact source evidence
→ explicit label: source-backed explanation / non-canonical
```

The user must never confuse explanatory attachment with a canonical relationship.

## Machine Comparison

Compare three representation paths over the exact same frozen SPEC-020 semantic packet:

### A. Existing canonical structure detector

Expected preserved result:

```text
2-node hierarchy
focus absent
admission fail
```

### B. Raw assertion visibility

Do not rebuild the full SPEC-016 UI; use existing evidence/history to record why this is not the desired path.

### C. Focus-preserving explanatory projection

Measure whether it:

- contains focus;
- exposes more grounded meaning;
- preserves semantic-tier distinction;
- remains visually bounded.

## Machine Metrics

Report at least:

```text
input symbol count
input grounded assertion count
trusted canonical item count
rejected canonical item count
focus-direct assertion count
selected explanatory item count
represented concept count
represented canonical relationship count
represented explanatory item count
initial visible prose word count
focus present yes/no
semantic-tier labeling completeness
explanatory item evidence completeness
canonical evidence completeness
pairwise-edge fabrication count (must be 0)
rejected-item promotion count (must be 0)
layout overlaps/crossings where meaningful
deterministic regeneration
BASELINE-003 asset immutability
```

## Human Review Gate

Only if machine integrity passes and the focus is represented should owner cognitive review occur.

Provide only:

```text
<viewer command>

Use this to understand the double-slit experiment. Follow anything that seems useful, and tell me what the representation makes easier or harder to understand.
```

Do not explain the assertion/projection architecture first.

## Human Review Questions

After spontaneous reaction, evaluate:

### Understanding

- Can I form a mental model of the double-slit experiment from the visual structure?
- Does it show meaningful phenomena/participants rather than merely listing facts?
- Does the deeper view add something beyond the parent representation?

### Cognitive load

- Does the representation feel spatial and explanatory rather than text-heavy?
- Are explanatory details available without dominating the overview?

### Trust

- Can I tell canonical relationships from source-backed explanatory material?
- Does anything look more certain/structured than the source supports?
- Is evidence easy to inspect?

### Workspace

- Do I remain oriented in BASELINE-003?
- Does this feel like deeper understanding of the selected concept rather than opening another document?

## Verdict Set

Final verdict must be exactly one of:

```text
EXPLANATORY_PROJECTION_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

Machine success alone cannot produce `EXPLANATORY_PROJECTION_BETTER`; owner cognitive review is required.

## No Live Calls

SPEC-021 is entirely offline.

If implementation concludes that a model call is necessary to assign explanatory roles or construct the representation, stop and report rather than calling one.

## Baseline Protection

Preserve BASELINE-001, BASELINE-002, and BASELINE-003 byte-identically.

Use isolated SPEC-021 evaluation/viewer assets.

## Explicit Non-Goals

Do not implement:

- new source extraction;
- new assertion extraction;
- canonical semantic retry;
- semantic threshold tuning;
- new canonical predicates;
- new canonical structure detector;
- ontology expansion;
- embeddings;
- semantic clustering;
- personalization;
- guided Journey/course mode;
- recursive child depth;
- workspace redesign;
- navigation redesign;
- simulation.

## Testing Strategy

All tests offline.

Add focused tests for:

```text
SPEC-020 artifact hash/identity validation
focus preservation
known rejected relationship exclusion
trusted canonical relationship preservation
assertion participant attachment
no pairwise canonical-edge fabrication
explanatory-vs-canonical tier separation
explanatory evidence preservation
text-budget enforcement/diagnostics
layout determinism
BASELINE-003 integration state
parent camera invariance
return-to-parent behavior
baseline immutability
byte-for-byte regeneration
```

Keep the full suite passing.

## Evaluation Artifacts

Create:

```text
examples/evaluations/spec-021-focus-explanatory-projection-<date>/
```

Likely artifacts:

```text
input-manifest.json
projection.json
projection-diagnostics.json
canonical-control.json
semantic-tier-audit.json
workspace-manifest.json
report.json
human-review-template.json
README.md
index.html
viewer assets
```

## Acceptance Criteria — Technical

- [ ] Exact frozen SPEC-020 packet reused.
- [ ] No live calls.
- [ ] `double-slit-experiment` preserved as focus.
- [ ] Existing structure detector unchanged.
- [ ] Known overstated causal item not promoted.
- [ ] Trusted canonical items preserved where applicable.
- [ ] Explanatory material derived only from grounded assertions.
- [ ] No pairwise canonical edges fabricated.
- [ ] Explanatory material explicitly non-canonical.
- [ ] Full assertion prose hidden by default.
- [ ] Evidence hidden until requested.
- [ ] Focus appears in final representation.
- [ ] Representation is visually bounded and spatial.
- [ ] BASELINE-003 shell unchanged.
- [ ] Parent navigation context stable.
- [ ] Parent ↔ deeper projection transition works without page navigation.
- [ ] Provenance/evidence complete.
- [ ] Deterministic regeneration passes.
- [ ] Full offline suite passes.
- [ ] Human review occurs only after machine integrity passes.

See `SPEC-021-ADDENDUM-handoff.md` for required handoff and decision rules.
