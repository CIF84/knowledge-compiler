# SPEC-026 — Semantic Interaction Invariance

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can the expanded deeper map obey the same learner-facing semantic and interaction grammar as the parent map, so depth changes only what knowledge is available—not how concepts and relationships are read or explored?

## Owner verdict on SPEC-025

Record SPEC-025 as:

```text
MIXED
```

Owner evidence:

- successful: selecting deeper concepts and source-backed explanations now synchronizes map focus, `WHAT DOES THIS MEAN?`, representation, and explanatory detail correctly;
- successful: spatial depth from SPEC-024 remains intact;
- failed: many connective lines inside the deeper map are not interactive;
- failed: many deeper connections lack arrows and/or learner-readable relationship labels;
- failed: clicking deeper nodes changes focus/suppression without consistently exposing the semantics of the connections responsible for the visible structure;
- therefore the stronger invariant remains unmet: `Depth should change what knowledge is available, not how the interface behaves.`

Preserve SPEC-025 unchanged as a functional historical experiment. Do not promote it to a baseline in this packet.

## Why this is next

SPEC-024 established continuous spatial depth. SPEC-025 established depth-invariant selection mirroring for knowledge items.

The remaining failure is now narrower and architectural: the deeper graph exposes topology that does not consistently obey the learner-facing graph grammar already established at the parent level.

At the accepted learner surface, the grammar is approximately:

```text
concept node
relationship edge + direction + predicate label
select either
→ synchronized representation
→ explanation / evidence
```

Inside the deeper map, canonical relationships can obey this grammar, but other visible connective structures are often rendered as dashed unlabeled/non-directional attachments. They may be semantically valid internal explanatory/provenance structures, but the learner cannot reliably tell what a connection means or interact with it as a relationship.

The next experiment must not patch individual arrows. It must test a stronger renderer/product invariant.

## Experimental hypothesis

If every learner-visible semantic connection is rendered and interacted with according to its semantic type, while non-relationship scaffolding is visually prevented from masquerading as a relationship, then parent and deeper maps will feel like one continuous knowledge interface.

Core principle:

> **A deeper map must be a map, not a visualization of internal compiler structure.**

And:

> **Same semantic object → same visual grammar → same interaction grammar → same explanatory behavior, regardless of depth.**

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- SPEC-023/FIX-023 historical depth artifact;
- SPEC-024 continuous-map artifact;
- SPEC-025 depth-invariant-selection artifact;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, admission, and fail-closed behavior.

Create an isolated SPEC-026 evaluation. Do not overwrite prior evaluations or accepted baselines.

## Experimental variable

The only product variable is **learner-facing semantic legibility and interaction of connections inside expanded depth regions**.

Control:

```text
SPEC-025
selection mirroring works at depth
but deeper graph contains visible connections whose meaning and interaction grammar differ from ordinary map relationships
```

Candidate:

```text
SPEC-026
SPEC-025 synchronization retained
+ canonical relationships use ordinary relationship grammar at every depth
+ learner-visible non-canonical explanatory connections are explicitly legible as explanatory, not ambiguous pseudo-relationships
+ selection never hides the semantic meaning of the focused item's relevant connections
```

No semantic regeneration or new knowledge is authorized.

## Core invariants

### 1. Canonical relationship grammar is depth-invariant

Any canonical relationship rendered inside a depth expansion must behave as the same semantic object would at the parent level.

At minimum:

- direction remains readable when the predicate is directional;
- predicate/relationship label remains readable;
- relationship is selectable through an appropriate interaction target;
- selection synchronizes map and right learning pane;
- relationship explanation and evidence are available under the same grammar as ordinary relationships;
- focus/highlight behavior mirrors parent-level behavior.

Do not create a special `deep relationship` learner grammar.

### 2. Non-canonical connections must not masquerade as canonical relationships

Source-backed explanatory material, evidence attachment, provenance, ancestry/depth entrance, and other non-canonical structures may remain visible where useful.

But their rendering must make their semantic status understandable.

A learner must not reasonably interpret an unlabeled dashed connector as an ordinary knowledge relationship and then discover that it cannot be inspected.

Choose the smallest honest treatment supported by existing semantics. Possible treatments include:

- explicit explanatory attachment grammar;
- selectable explanatory attachment with synchronized non-canonical detail;
- visual containment/association rather than edge-like relationship rendering;
- suppression of purely internal scaffolding from the learner-facing map when it contributes no learner-readable semantic meaning.

Do **not** invent canonical predicates or fabricated pairwise relationships merely to make every line look canonical.

### 3. Visible topology must be semantically readable

For every visible connection in the owner-facing deeper map, a learner should be able to answer:

```text
Why are these things connected?
What kind of connection is this?
Can I inspect its meaning?
```

The answer may differ for canonical relationship vs source-backed explanatory attachment, but it must not depend on knowledge of compiler internals.

### 4. Focus must preserve relationship intelligibility

Focus suppression remains useful and should be preserved.

However, selecting a concept must not make the semantic meaning of its relevant visible connections disappear.

When a selected concept is shown with connected context, the learner must retain enough edge direction/label/status information to understand why that context is connected.

Selection should make the graph easier to read, not merely reduce opacity.

### 5. Right pane remains one learning surface

Preserve the successful SPEC-025 synchronization:

```text
map current focus
↔ WHAT DOES THIS MEAN?
↔ representation
↔ explanation / evidence
```

Do not add a second relationship inspector, depth inspector, modal panel, or special deep-learning pane.

### 6. Depth remains continuous and recursive

Preserve SPEC-024 spatial expansion and path/origin behavior.

The design must remain valid if another expansion is later opened from inside the current expansion.

Do not implement a depth-number conditional grammar.

## Semantic-object classification seam

Prefer one semantic/item-type-driven rendering and interaction decision rather than depth-specific branches.

Conceptually:

```text
visible item / connection
→ resolve semantic class
→ render learner grammar for that class
→ resolve interaction for that class
→ synchronize current focus
```

The relevant distinction is semantic authority/type, not parent vs child depth.

This is architectural guidance, not a mandated implementation schema.

## Preserve accepted learner grammar

Outside this narrow seam, preserve:

- BASELINE-004 workspace shell and visual language;
- `WHERE AM I?` / `WHAT DOES THIS MEAN?` two-pane model;
- region orientation;
- pan and geometric zoom;
- concept selection;
- canonical relationship selection;
- preview vs selected styling;
- focus suppression where it remains semantically legible;
- evidence synchronization;
- SPEC-024 continuous spatial expansion;
- SPEC-025 current-focus synchronization;
- no browser blue selection/drag artifacts.

No general redesign of typography, color, spacing, controls, node geometry, or workspace layout.

## Semantic trust invariants

This packet changes rendering/interaction only.

Preserve:

- canonical vs non-canonical distinction;
- exact grounded evidence/provenance;
- participant-preserving explanatory semantics;
- rejected/demoted overstated causal proposal remains rejected/demoted;
- no fabricated pairwise edges;
- no semantic predicate/vocabulary changes;
- no weakened grounding/admission rules;
- no conversion of explanatory attachments into canonical relationships solely for UI convenience.

If semantic legibility appears to require asserting knowledge not present in the trusted IR, stop and report the conflict.

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
- model/agent judging.

Use committed artifacts and deterministic fixture logic only.

## Mechanical gate

Before owner review, verify at least:

```text
BASELINE-001..004 hashes unchanged
SPEC-023/FIX-023 preserved
SPEC-024 preserved unchanged
SPEC-025 preserved unchanged
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
known rejected causal item not promoted
pairwise-edge fabrication = 0
ordinary BASELINE-004 navigation intact
SPEC-024 continuous map expansion intact
SPEC-025 map ↔ WHAT DOES THIS MEAN? synchronization intact
all canonical relationships in the deeper fixture expose readable predicate semantics
all directional canonical relationships preserve readable direction
all canonical deeper relationships have an interaction target and synchronized relationship explanation/evidence
all learner-visible non-canonical connections have an explicit learner-readable semantic treatment or are removed from relationship-like rendering
no unexplained relationship-like connector remains in the owner-facing deeper fixture
select deeper concept → relevant connected semantics remain readable
select deeper canonical relationship → same grammar as parent relationship
select explanatory attachment → explicitly non-canonical explanation/evidence behavior
switch among concepts/relationships/explanations → no stale focus/detail
parent ↔ deeper switching remains ordinary interaction
synthetic second expansion uses the same semantic rendering/interaction classification
pan/zoom functional with expansion open
collapse/retraction remains predictable
browser drag creates no blue selection artifacts
browser console clean
full offline suite passes
```

If any machine gate fails, do not request owner review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-026-semantic-interaction-invariance-<date>/
```

Do not mutate BASELINE-004 or prior SPEC evaluations to produce it.

## Owner review

Do not prime the owner with implementation details.

If the machine gate passes, provide only the low-attention completion handoff, exact viewer command, and approximately this task:

```text
Navigate naturally to the double-slit experiment and explore deeper. Treat the deeper structure exactly as you would the surrounding map: inspect concepts and the connections between them. Tell me whether you can understand why things are connected, whether relationships behave the same way inside and outside the deeper map, and note anything that still makes you stop and wonder what a line, arrow, label, or interaction means.
```

## Owner-review questions for ChatGPT

After spontaneous feedback, evaluate:

### Semantic legibility

- Can the owner read the meaning of the deeper topology without knowing compiler internals?
- Are direction and predicate semantics available where they matter?

### Interaction invariance

- Do canonical relationships behave the same regardless of depth?
- Do concept, relationship, and explanation selection all synchronize through the same learning surface?

### Semantic honesty

- Are canonical and explanatory/non-canonical connections distinguishable without making the latter look broken?
- Did the implementation avoid inventing relationships merely for presentation?

### Focus

- Does selection clarify relevant structure while preserving why connected items are connected?

### Recursion

- Does the grammar appear capable of continuing into another expansion without a new interaction mode?

## Verdict set

Final subjective verdict must be exactly one of:

```text
SEMANTIC_INTERACTION_INVARIANT
MIXED
PARENT_GRAMMAR_DOES_NOT_GENERALIZE
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`SEMANTIC_INTERACTION_INVARIANT` requires owner evidence that the deeper structure can be read and interacted with using the same learner grammar as the parent map; canonical relationship direction, predicate meaning, selection, explanation, and evidence remain coherent; non-canonical explanatory structures remain honest and understandable; and continuous spatial depth plus SPEC-025 synchronization are preserved.

## Explicit non-goals

Do not implement:

- new semantic depth generation;
- new quantum facts;
- new canonical relationships solely for presentation;
- semantic predicate/proposition changes;
- automatic semantic zoom/depth triggering;
- guided Journey/course mode;
- personalization;
- history/timeline UI;
- browser-style back stack;
- new workspace shell;
- global navigation redesign;
- baseline promotion;
- unrelated polish/refactoring.

## Required durable report

Record at least:

- exact baseline and frozen-input hashes;
- SPEC-024 and SPEC-025 preserved-state evidence;
- files changed;
- semantic-object classification/rendering seam;
- canonical deeper relationship rendering/interaction results;
- non-canonical connection treatment and rationale;
- focus-legibility tests;
- synthetic recursive-depth regression result;
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

- `SPEC-026` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep detailed inventories in the durable report.

## Final constraint

Do not solve semantic legibility by making every connector a canonical relationship.

This experiment exists to test one idea:

> **Depth may reveal more knowledge, but it must not reveal a different interface language.**
