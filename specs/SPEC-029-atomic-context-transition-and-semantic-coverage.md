# SPEC-029 — Atomic Context Transition and Semantic Coverage

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can every learner-visible semantic interaction use the same canonical state path while changing active knowledge context atomically replaces all semantic interaction state and projections from the previous context?

## Owner verdict on SPEC-028

Record SPEC-028 as:

```text
MIXED
```

Owner evidence:

- materially improved: most previously reported deep-map/right-pane divergence is fixed;
- materially improved: recursive concept, relationship, and source-explanation interaction now behaves substantially coherently;
- failed: some ordinary ground-level Software Architecture relationships do not propagate correctly into the learning pane;
- failed: after leaving a deep double-slit context for ground-level History of Printing, the map changed correctly while the right pane remained on the stale double-slit deeper map.

See `debriefs/DEBRIEF-028-single-canonical-interaction-state.md`.

## Why this is next

SPEC-028 tested whether semantic interaction state should have one canonical owner. The evidence supports that architecture.

The remaining defect is now narrower:

```text
canonical interaction state exists
but
context lifecycle is not yet canonical
and
some semantic interaction paths may still bypass it
```

The next experiment must not add more cross-surface synchronization. It must finish the invariant:

```text
user interaction
→ resolve active knowledge context + stable semantic object
→ one canonical transition
→ one resulting canonical learner state
→ every visible surface projects that state
```

When context changes:

```text
old context + old semantic focus
→ atomic replacement
→ new context + valid focus/no-focus
→ all projections render only the new state
```

No stale projection from the previous context may survive.

## Core principle

> **There is exactly one active learner context and one canonical learner interaction state. A context transition replaces them atomically.**

And:

> **Every learner-visible semantic object, at every depth and in every domain, enters the same canonical interaction path.**

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- SPEC-023/FIX-023 historical artifact;
- SPEC-024 through SPEC-028 historical/evaluation artifacts;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, admission, and fail-closed behavior.

Create an isolated SPEC-029 evaluation. Do not overwrite prior evaluations or baselines.

## Experimental variables

Only these architecture variables are in scope:

1. lifecycle of the active learner context;
2. completeness of semantic-object routing into the canonical interaction state.

No semantic regeneration, new knowledge generation, ontology change, or UI redesign is authorized.

## Required canonical state seam

Prefer a model conceptually equivalent to:

```text
canonical learner state
├── active_context_identity
├── context ancestry / revealed expansion state needed for visible knowledge
├── semantic hover target
├── semantic selected target
├── semantic class
├── active relationship/explanation identity
└── valid clear/no-focus state
```

A semantic focus is valid only inside the active context or its currently revealed descendants.

Changing the active knowledge context must perform one canonical transition. Surface-specific callbacks must not independently clear or replace semantic state.

## Atomic context-transition invariant

A context transition includes any learner action that changes which knowledge context is authoritative, including at minimum:

- moving from one ground-level domain/context to another;
- leaving a revealed/deeper structure and selecting a different ground-level context;
- moving from one revealed context to another where supported;
- collapse/retraction when the current semantic focus belongs only to the retracted context;
- ordinary map navigation that changes the active context.

After the transition completes:

- exactly one active context exists;
- every semantic focus belongs to that context or a valid revealed descendant;
- no right-pane representation from the prior context remains active;
- no explanation/evidence projection from the prior context remains active;
- no stale selected/preview styling from the prior context remains;
- pan/zoom/layout state may remain surface-local where valid, but cannot preserve semantic activity from the old context.

The transition must be atomic from the learner-visible perspective. Intermediate contradictory semantic states must not be observable.

## Semantic-object coverage invariant

Audit every learner-visible interactive semantic class already present in the accepted workspace and SPEC-028 fixture, including at least:

- concept nodes;
- canonical relationships/edges;
- source-backed non-canonical explanations;
- ground-level relationships in all fixed example domains used by the viewer;
- the same classes inside revealed/deeper maps;
- duplicate visual instances of the same semantic identity where present.

Every supported interaction must resolve into the same canonical event/reducer path.

Forbidden:

- a legacy ground-level relationship handler that directly updates only one pane;
- depth-specific semantic state ownership;
- domain-specific semantic selection state;
- surface-to-surface semantic synchronization as the repair mechanism.

If a semantic object class intentionally has different interaction semantics, that difference must already exist in the accepted grammar and must still dispatch through the canonical state owner.

## Ground-level relationship regression

Add deterministic coverage specifically for the owner-observed class of failure:

```text
ordinary ground-level relationship
→ hover/preview
→ select
→ right-pane relationship representation/explanation
→ map and right pane agree
```

Use at least the fixed Software Architecture fixture and another ordinary ground-level domain fixture.

Test both event origins where the representation itself is interactive.

Required result:

```text
ground-level relationship projection agreement = PASS
```

## Cross-context stale-state regression

Create a deterministic interaction sequence reproducing the owner failure class. At minimum:

```text
enter Electromagnetism
action on double-slit relationship
open deeper structure
select/preview a deep concept or explanation
switch to History of Printing
interact with Printing
interact with Printed controversy / relationship
```

At every step after the context switch, assert that no semantic identity, representation title/body, relationship focus, explanation focus, or selected/preview style from Electromagnetism remains authoritative.

Also run the reverse sequence and a Software Architecture transition.

## Adversarial transition matrix

Mechanically exercise at least these sequences:

```text
A ground concept → B ground concept
A ground relationship → B ground relationship
A deep concept → B ground concept
A deep relationship → B ground relationship
A deep source explanation → B ground concept
A deep object → clear → B context
A deep object → collapse/retract → B context
A → B → A rapid switching
A depth 1 → A depth 2 → B → A
Software Architecture relationship → History of Printing → Electromagnetism deep object
```

Where A/B are distinct fixed contexts.

For each transition record at least:

- active context identity;
- selected semantic identity/class;
- hover/preview identity/class;
- active relationship/explanation identity;
- map projected active state;
- right-pane projected active state;
- explanation/evidence projected state;
- stale semantic identities from prior context;
- stale prior-context DOM/projection activity where deterministically inspectable.

Required result:

```text
active context count = 1
cross-surface projection agreement = PASS
stale prior-context semantic state = 0
stale prior-context authoritative projection = 0
```

## Recursive continuity invariant

Do not regress SPEC-028's depth result.

The existing deterministic synthetic recursion fixture through depth 10 must continue to pass.

Add context transitions from synthetic depths 0, 1, 2, 5, and 10 into a distinct ground-level context and back where practical.

Required result:

```text
context-transition behavior is depth-independent = PASS
```

The owner should not experience a different lifecycle because the previous focus happened to be ten levels deep.

## Observable owner-facing invariants

The owner should be able to:

1. interact naturally inside a ground-level map;
2. go deeper several levels;
3. interact from either map or right pane;
4. jump to a different domain/context;
5. immediately continue interacting there;

without ever seeing the previous context remain active in the other surface.

Specifically:

- map and right pane always describe the same active context;
- semantic selection/preview remains mutually coherent;
- ground-level relationships behave with the same grammar as deep relationships;
- a context switch cannot leave a stale deeper map in the right pane;
- rapid switching cannot resurrect old semantic focus;
- returning to a prior context starts from only the state intentionally preserved by accepted navigation semantics, never accidental stale projection.

## Preserve accepted learner grammar

Preserve:

- BASELINE-004 shell and visual language;
- `WHERE AM I?` as the spatial knowledge surface;
- `WHAT DOES THIS MEAN?` as the active representation/explanation surface;
- current preview vs selected distinction;
- current map ↔ representation ↔ explanation interaction grammar;
- relationship direction/predicate labels;
- canonical vs source-backed/non-canonical distinction;
- evidence/provenance display;
- current continuous depth-expansion geometry;
- ordinary pan/zoom;
- predictable collapse/retraction;
- current typography, spacing, colors, controls, and node geometry.

This is not a UI redesign.

## Semantic trust invariants

This packet changes interaction lifecycle only.

Preserve:

- trusted semantic IR;
- canonical predicates;
- exact evidence/provenance;
- all rejected/demoted semantic items;
- no fabricated semantic edges;
- no semantic vocabulary changes;
- no weakened grounding/admission;
- no semantic enrichment.

If fixing coverage requires inventing semantic meaning, stop and report the boundary.

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
SPEC-024..028 historical artifacts preserved
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
known rejected causal item not promoted
pairwise-edge fabrication = 0
exactly one authoritative active-context state path exists
exactly one authoritative semantic interaction state path exists
context changes do not use surface-by-surface semantic clearing
all supported concept interactions use canonical path
all supported canonical relationship interactions use canonical path
all supported source-backed explanation interactions use canonical path
Software Architecture ground relationship regression passes
second ground-level relationship-domain regression passes
deep → ground History of Printing stale-state regression passes
reverse and Software Architecture context transitions pass
active context count always 1 after transition
stale prior-context semantic identity count = 0
stale prior-context authoritative projection count = 0
A → B → A rapid switching passes
clear then context switch passes
collapse/retract then context switch passes
context transitions from depths 0,1,2,5,10 are equivalent
existing SPEC-028 ten-level interaction parity remains passing
map/right-pane projected context always agrees
map/right-pane selected/preview semantics agree
browser hover/click behavior manually verified across context switch
browser console clean
pan/zoom remain functional
full offline suite passes
```

If any machine gate fails, do not request owner review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-029-atomic-context-transition-and-semantic-coverage-<date>/
```

Do not mutate BASELINE-004 or prior SPEC evaluations.

## Owner review

Do not prime the owner with implementation details.

If the machine gate passes, provide only the low-attention completion handoff, exact viewer command, and approximately this task:

```text
Use the workspace naturally. Interact with a few ordinary relationships, then open the double-slit deeper structure and interact there from both panes. Without clearing anything first, move to History of Printing and then another domain and continue interacting. Switch back and forth a few times. Tell me whether the map and right pane ever disagree about which context or object is active, whether an old context remains visible after you have left it, or whether any ordinary relationship behaves differently from the deeper ones.
```

## Verdict set

Final subjective verdict must be exactly one of:

```text
CONTEXT_LIFECYCLE_CONFIRMED
MIXED
CONTEXT_OR_COVERAGE_STILL_DIVERGES
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`CONTEXT_LIFECYCLE_CONFIRMED` requires owner evidence that:

- ordinary and recursive semantic objects participate in one interaction grammar;
- map and right pane always agree on active context and semantic focus;
- changing context atomically eliminates stale prior-context semantic activity and authoritative projections;
- behavior remains coherent regardless of prior recursive depth or event origin.

## Explicit non-goals

Do not implement:

- new semantic depth generation;
- new domain facts;
- new canonical relationships;
- semantic predicate changes;
- navigation history/timeline UI;
- browser back-stack semantics;
- workspace redesign;
- general visual redesign;
- automatic depth triggering;
- baseline promotion;
- unrelated refactoring.

## Required durable report

Record at least:

- frozen/baseline hash verification;
- files changed;
- active-context owners/seams found before repair;
- semantic object paths found outside the canonical interaction reducer, if any;
- canonical context-transition representation introduced or consolidated;
- atomic transition/reducer behavior;
- ground-level relationship coverage results;
- cross-context stale-state regression results;
- adversarial transition matrix results;
- recursive depth-transition results;
- retained surface-local state and why it is non-semantic;
- semantic-invariant checks;
- browser verification;
- console result;
- full offline tests;
- dependencies/live calls;
- deviations;
- commit/push state;
- exact viewer command.

## Low-attention completion handoff

On successful implementation, return only:

- `SPEC-029` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep implementation detail in the durable report.

## Final constraint

Do not solve this by layering another synchronization mechanism over SPEC-028.

This experiment exists to establish one stronger invariant:

> **One active context and one semantic interaction state drive every learner-visible projection, regardless of domain, surface, or recursive depth.**
