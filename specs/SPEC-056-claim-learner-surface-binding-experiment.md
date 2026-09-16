# SPEC-056 — Claim Learner-Surface Binding Experiment

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Bind a bounded representative sample of SPEC-055 experimental claim representation plans into the existing SPEC-038 learner-facing explanatory architecture so the owner can judge whether visual/structured representation plus concise prose improves explanation compared with prose-only claim presentation.

This is the first learner-surface experiment for trusted non-topological claim knowledge.

It is not a redesign of navigation, extraction, knowledge semantics, or the accepted explanatory architecture.

## Owner verdict entering this packet

SPEC-055 owner verdict:

`REPRESENTATION_SEMANTICS_CONFIRMED_LEARNER_SURFACE_BINDING_NEXT`

Accepted evidence:

- 98 trusted claim-only items were classified offline using traceable representation metadata;
- 53/98 safely supported richer-than-prose plans;
- final experimental strategy distribution:
  - `COMPARISON`: 7;
  - `QUALIFIED_STATEMENT`: 33;
  - `QUANTITATIVE_CALLOUT`: 13;
  - `CONCISE_PROSE`: 45;
- every richer plan retained unchanged concise prose;
- all displayed richer-plan fields trace to trusted claim text;
- zero semantic/topology mutation or unsafe final plans;
- existing non-claim decisions and detected structures remained unchanged;
- representation diversity is supported offline, but learner value remains untested.

## Core hypothesis

> For claim forms with explicit representation semantics, a dominant visual/structured representation plus concise prose will reduce text burden and improve perceptual comprehension relative to prose-only presentation, while claims that genuinely lack richer structure should remain concise prose.

## Protected explanatory architecture

Preserve the accepted four-surface model:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ dominant representation of the current idea

INSPECT / SELECTED / PREVIEW
→ concise explanation of selected representation-local meaning

EXPLORE NEXT
→ proposes future traversal
```

SPEC-056 changes only the experimental representation bound inside `WHAT DOES THIS MEAN?` and its local explanatory/inspection content for selected review cases.

Do not change My Map, traversal semantics, Explore Next, or global layout architecture.

## Experiment design

Create a dedicated learner-review artifact rather than modifying the accepted baseline globally.

The artifact must allow the owner to review a deterministic bounded sample of claim-focused cases across the four final SPEC-055 strategies.

### Required sample

Select exactly **12 review cases**, deterministically from SPEC-055 evidence:

- 3 `COMPARISON`;
- 3 `QUALIFIED_STATEMENT`;
- 3 `QUANTITATIVE_CALLOUT`;
- 3 `CONCISE_PROSE`.

Selection rules:

- maximize source/domain diversity before taking multiple cases from one source;
- use only claims already present in SPEC-055;
- prefer `HIGH` confidence/safety cases;
- within a strategy, deterministic order by source ID then claim ID after diversity rule;
- do not hand-pick cases based on visual attractiveness.

Record the selection algorithm and exact selected IDs in the report.

## Comparison mode

Each review case must support an owner-visible comparison between:

### A — prose-only control

The exact SPEC-054-style `CONCISE_PROSE` representation of the trusted claim.

### B — SPEC-055 experimental representation

The richer strategy where applicable, **plus the same concise prose**.

For `CONCISE_PROSE` cases, A and B may be identical; these serve as negative controls demonstrating that the system does not manufacture visual complexity where none is justified.

The comparison may use a simple toggle or deterministic side-by-side/review control, but avoid clutter. The primary goal is human evaluation, not feature polish.

## Representation binding requirements

### `COMPARISON`

Render a visually dominant comparison using only explicitly traced labels/values/dimensions from the SPEC-055 plan.

Possible forms include bars, paired columns, side-by-side contrast, or another minimal comparative layout fitting the frozen payload.

Do not invent missing axes, values, categories, or attributes.

The exact concise claim prose remains visible as explanation.

### `QUANTITATIVE_CALLOUT`

Give the trusted quantity/quantities clear visual hierarchy and perceptual weight.

The number/unit must come directly from the frozen plan trace.

Use concise prose to explain what the number means.

Do not turn a single quantity into a fake comparison/chart.

### `QUALIFIED_STATEMENT`

Make the explicit condition/qualification/exception perceptually distinct from the main statement.

The goal is to reduce syntactic burden by visually separating:

```text
main meaning
    ↕
condition / qualifier / exception
```

Do not infer causal arrows, process topology, or conditions absent from the frozen plan.

### `CONCISE_PROSE`

Render cleanly as prose without decorative pseudo-diagrams.

This is an important control: representation diversity includes choosing not to visualize when prose is genuinely the best form.

## Prose role

Prose must remain part of every case.

The experiment tests composition:

```text
structured / visual representation
              +
      concise source-faithful prose
```

not replacement of language by graphics.

Avoid repeating the exact same sentence multiple times merely to fill UI regions. If the dominant representation already contains textual fragments, the explanatory prose should remain concise and complementary while preserving the exact trusted meaning.

## Interaction

Keep interaction local and minimal.

Allowed:

- hover/focus emphasis on meaningful visual elements;
- click/select a representation-local element to update `INSPECT / SELECTED / PREVIEW`;
- control to switch A prose-only vs B experimental representation;
- next/previous review-case navigation inside the dedicated review artifact.

Required invariant:

> interacting with representation-local elements must not change learner location or My Map territory.

Do not recreate the old map↔explanation mirroring architecture.

## Inspection content

When a richer representation has meaningful components, selection/hover may show:

- the exact trusted fragment/value/qualifier;
- concise explanation of its role in the representation;
- provenance/evidence on demand or in a quiet secondary treatment.

Do not add new semantic claims.

For prose-only controls, the inspection region may remain minimal/empty rather than manufacturing interactivity.

## Visual grammar

The artifact should visibly preserve the lessons from the accepted UI baseline:

- dominant representations should look like representations, not collections of buttons;
- avoid excessive bordered boxes/cards;
- use whitespace, typography, alignment, scale, and connecting marks intentionally;
- controls should look like controls; knowledge should not all look clickable;
- the right explanatory pane should be visually richer than navigation;
- representation should attract attention before explanatory prose;
- prose should be comfortably readable and materially less dominant when a visual form carries structure.

Do not perform a broad style redesign outside the review artifact.

## Browser artifact

Produce an executable static/local learner-review artifact that can be served with the existing project tooling or a narrowly added review command.

Preferred location:

`examples/evaluations/spec-056-claim-learner-surface-binding-experiment-20260916/`

It must be reviewable in a browser without model/network calls.

Provide a simple owner review command.

## Machine/browser gate

Add deterministic browser checks appropriate to the artifact.

At minimum verify:

- all 12 cases load;
- strategy labels/identities match frozen SPEC-055 evidence;
- A/B control works;
- richer cases display the expected strategy-specific DOM/state;
- prose-only controls do not gain fake richer structures;
- all traced values/labels/qualifiers are present exactly as frozen;
- no untrusted text is introduced;
- local interactions do not mutate review-case identity or navigation territory;
- no console errors/warnings;
- responsive layout remains usable at desktop and narrow/mobile-like width.

## Human review rubric

Embed or emit a concise owner-review rubric for each case.

The owner should judge:

1. **Comprehension** — Is the meaning faster/easier to grasp in B than A?
2. **Text burden** — Does the structured form reduce how much prose must carry cognitively?
3. **Truthfulness** — Does B preserve the exact meaning without implying extra semantics?
4. **Visual distinctiveness** — Does the representation look meaningfully different from ordinary prose/control UI?
5. **Prose complementarity** — Does prose explain the representation rather than redundantly duplicate it?
6. **Restraint** — For prose-only cases, does the absence of visualization feel appropriate?

Do not auto-score or infer the owner's subjective verdict.

## Required evidence

Create:

`examples/evaluations/spec-056-claim-learner-surface-binding-experiment-20260916/report.json`

Include at minimum:

- SPEC-055 report identity/hash;
- deterministic sample-selection method and 12 selected cases;
- A/B artifact identities;
- strategy/render binding for each case;
- provenance/truthfulness audit;
- browser/machine gate results;
- responsive checks;
- screenshots if existing repository protocol supports deterministic capture;
- zero-call/zero-extraction statement;
- owner-review command;
- owner-review state.

## Controls and protected state

Prove or preserve:

- admitted KnowledgeModels unchanged;
- topology/detected structures unchanged;
- existing non-claim representation decisions unchanged;
- SPEC-055 plan semantics unchanged;
- no production renderer promotion;
- accepted SPEC-038 baseline files/behavior unchanged unless a narrowly shared rendering primitive is required and proven regression-safe.

Prefer isolated experimental renderer/binding code over modifying production behavior.

## No live authority

Provider/model calls: `0`.

External retrieval: `0`.

Extraction reruns: `0`.

No new semantic generation.

## Explicitly forbidden

Do not:

- call a model/provider;
- rerun extraction;
- change KnowledgeModel semantics;
- create relationships/propositions from claims;
- modify StructureDetector;
- change SPEC-055 classification/plan outputs;
- invent comparison operands, values, qualifiers, or visual semantics;
- promote experimental strategies/renderers;
- redesign My Map/navigation/Explore Next;
- add Back/history or unrelated product features;
- use source/domain identity to alter representation;
- automatically decide the human learner verdict.

## Validation

At minimum:

- focused SPEC-056 rendering/binding tests;
- browser machine gate;
- regression tests for SPEC-038 and existing representation behavior;
- control-plane tests;
- full offline suite;
- deterministic regeneration of review artifacts;
- JSON validation;
- provenance/secret-safety checks;
- `git diff --check`;
- verify zero provider/model/network calls;
- verify protected semantic/topological artifacts unchanged.

## Completion state

On completion:

- set SPEC-056 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report selected-case distribution, browser gate, validation, artifact path, and owner-review command;
- stop at `OWNER_REVIEW`;
- do not promote experimental representation forms or implement follow-up changes.

## Owner review question

> When the same trusted claim is shown as prose-only versus a semantically fitting structured/visual representation plus concise prose, does the richer representation materially improve comprehension and reduce text burden without adding meaning that is not actually present?
