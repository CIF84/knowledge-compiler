# SPEC-020 — Realistic Semantic Depth in the Hybrid Workspace

## Status

Ready for implementation.

## Phase

Phase III — reconnect realistic-source semantics and semantic depth to the accepted product workspace.

## Primary Question

> Can one realistic source produce a trustworthy deeper semantic resolution inside BASELINE-003, while the continuous knowledge map remains spatially stable and the focused learning surface gains useful source-supported understanding?

## Why This Experiment Is Earned

Two previously separate branches of the project are now strong enough to reconnect.

### Semantic branch

SPEC-011 exposed realistic full-source extraction as unreliable.

SPEC-012 removed dangling-symbol failures but semantic precision remained weak.

SPEC-013 established `ASSERTION_FIRST_BETTER` on the frozen quantum benchmark:

- grounded assertions preserved source meaning;
- graph admission became conservative;
- accepted relationships reviewed at high precision;
- misleading source meaning could remain available as claims rather than bad edges.

SPEC-014 and SPEC-015 showed that narrow semantic discriminators can catch known lossy canonicalizations without requiring broad multi-agent deliberation.

### Interaction branch

BASELINE-001 established focused learning quality.

BASELINE-002 established continuous navigation quality.

SPEC-019 / BASELINE-003 established the preferred integrated workspace:

```text
WHERE AM I?               WHAT DOES THIS MEAN?
navigation                focused representation
```

The owner judged this interface essentially complete at the foundational level.

The next uncertainty is therefore not another shell design.

It is whether **real semantic depth can inhabit the accepted shell**.

## Experimental Hypothesis

A learner should be able to select a meaningful concept in a realistic-source knowledge world and request/deepen its resolution without leaving the workspace.

The expected interaction is conceptually:

```text
realistic source
      ↓
trusted parent semantics
      ↓
BASELINE-003 workspace
      ↓ select focus
source-bounded deeper compilation
      ↓
learning surface gains deeper local model
      ↓
navigation surface preserves larger-world orientation
```

The experiment succeeds only if the deeper view adds trustworthy understanding **and** the spatial/interaction model remains coherent.

## Frozen Product Shell

Treat `BASELINE-003 — Hybrid Learning Workspace` as a strong invariant.

Do not redesign:

- left/right cognitive responsibilities;
- workspace composition;
- navigation interaction grammar;
- learning-surface visual grammar;
- pan/zoom behavior;
- selection synchronization;
- information hierarchy;
- typography/layout merely for polish.

Any unavoidable shell change must be called out before implementation if it materially changes owner-approved behavior.

## Component Baselines

Preserve independently:

- BASELINE-001 for focused-learning regression comparison;
- BASELINE-002 for continuous-navigation regression comparison;
- BASELINE-003 for integrated-workspace regression comparison.

Do not mutate baseline artifacts in place.

## Frozen Realistic Benchmark

Reuse the realistic quantum source already established by SPEC-011 through SPEC-015:

- Wikipedia — `Introduction to quantum mechanics`;
- fixed revision `1359567407`;
- existing recorded source hash/provenance;
- existing frozen source metadata;
- existing SPEC-012 symbol table where still appropriate;
- existing SPEC-013 grounded assertion / trusted-parent artifacts where valid.

Do not silently substitute a simpler source merely to obtain a successful demo.

## Parent Semantic Starting Point

Prefer reusing the trusted SPEC-013 parent semantic artifacts rather than rerunning already-settled stages.

The experiment should begin from the strongest accepted realistic-source semantic state already in the repository.

Do not rerun symbol discovery or parent assertion extraction unless a concrete technical incompatibility makes reuse impossible.

If reuse is impossible, stop and explain why before introducing additional live calls.

## Focus Selection

Select exactly one meaningful focus from the trusted realistic parent.

The focus must satisfy all of the following:

1. exists in the frozen parent symbol/model artifacts;
2. has enough source material to plausibly support deeper explanation;
3. is pedagogically meaningful rather than chosen solely for extraction convenience;
4. can be located in the BASELINE-003 navigation context;
5. does not require external enrichment to explain.

### Preferred focus selection process

Select offline using committed source/semantic evidence before any new live output is observed.

Record:

- focus entity ID/name;
- why it is meaningful;
- source spans/sections likely to support depth;
- expected resolution strategy;
- explicit reasons alternatives were not chosen.

Do not cherry-pick a focus after seeing a live child result.

## Resolution Strategy

Use the existing resolution-strategy architecture from SPEC-009 where applicable.

Do not invent a new strategy family merely for quantum mechanics.

Select the best existing strategy based on the focus's semantic type/structure.

If none is appropriate, the experiment may use `GENERIC_DETAIL` as the explicit control, but must state that strategy mismatch is a limitation.

No hidden classifier is required.

## Source Scope for Child Resolution

The child must remain source-bounded.

Use the smallest honest source scope that contains enough material to resolve the focus while preserving context.

This may be:

- the full fixed source;
- a deterministic contiguous source section/range selected offline;
- another deterministic source-bounded scope already supported by repository architecture.

Do not use retrieval from external sources.

Do not enrich from model world knowledge.

Record exact scope boundaries and hash where applicable.

## Child Semantic Pipeline

The child-resolution path should use the strongest existing semantic reliability architecture compatible with resolution.

Preferred principle:

```text
source-bounded child material
        ↓
neutral / assertion-preserving semantic stage where feasible
        ↓
trusted grounding
        ↓
canonicalization / admission
        ↓
child KnowledgeModel
```

Do not regress to knowingly weaker direct canonical edge generation merely because it is easier to connect to SPEC-008/009.

### Integration decision

Codex must inspect the current implementation and choose the smallest seam that reuses the assertion-first reliability boundary for child generation.

If doing so would require a broad rewrite of the compiler, stop and report the incompatibility rather than silently building a second semantic pipeline.

## Semantic Admission

Use deterministic validation and existing narrow semantic checks where they can be applied without changing the experiment into a multi-agent system.

The objective is not maximum graph density.

Prefer:

```text
fewer trusted relationships
+ grounded claims/assertions
```

over misleading canonical structure.

If a child cannot be trusted, fail closed and preserve the rejected proposal.

A truthful negative result remains valid evidence.

## Parent Immutability

Child generation must not mutate the parent semantic model.

Verify parent artifact hashes before and after the experiment.

The parent remains the stable world context.

## Workspace Integration

If and only if a trusted child exists, integrate it into BASELINE-003.

### Navigation surface

The navigation surface must preserve the parent knowledge world as the stable orientation layer.

The child should not replace the world map.

The selected parent focus remains locatable in the parent world.

### Learning surface

The learning surface may transition from the parent/local representation to the deeper child representation.

Conceptually:

```text
WHERE AM I?
parent world stays stable
selected focus remains visible

WHAT DOES THIS MEAN?
parent local model
      ↓ deepen
child local model
```

### Context indication

The learner must be able to understand that the right-hand representation is a deeper resolution of the selected parent concept.

Use the minimum BASELINE-003-compatible context cue.

Do not restore the old full-width Explore/Back banner UI.

A compact breadcrumb/path/depth cue is acceptable if necessary.

## Navigation at Deeper Resolution

Do not add the child as a giant new cluster to the parent world merely to visualize depth.

For SPEC-020, keep the parent map stable and treat the child primarily as focused semantic depth in the learning surface.

The map may visually indicate that the selected parent concept has deeper resolution available/active, but do not invent a new map metaphor.

## Returning to Parent Resolution

Provide a simple, integrated way to return the learning surface to the parent/local representation while keeping navigation position intact.

This should feel like changing semantic resolution, not browser/page navigation.

Avoid `Back to X` as a large page-navigation control if a quieter depth/breadcrumb mechanism fits BASELINE-003.

## Semantic Zoom vs Geometric Zoom

Keep these separate.

### Geometric zoom

Left navigation camera scale. Already frozen in BASELINE-003.

### Semantic depth

Right learning-surface resolution. Experimental in SPEC-020.

Wheel/trackpad zoom must **not** automatically trigger semantic child generation or resolution changes.

SPEC-020 is not testing coupled semantic zoom gestures.

## Representation Selection in Child

Compile the trusted child through existing structure detection and representation selection.

Do not force the child into the same representation type as the parent.

If the child structure is best expressed differently, that is desirable evidence for the architecture.

Example:

```text
parent focus represented as hierarchy
child mechanism represented as causal/process structure
```

The representation must follow detected semantic structure.

## Evidence and Provenance

Child relationships/claims/propositions must remain inspectably grounded.

The learning surface must preserve source evidence/provenance behavior for child semantic items.

The user should be able to distinguish:

- parent semantic context;
- generated deeper child model;
- source evidence supporting the child.

Do not add verbose provenance chrome to the overview unless selected.

## Live Call Discipline

The experiment should use the minimum live calls necessary for one child resolution.

Target architecture should ideally require no more than two calls:

```text
Call A — source-bounded child assertion extraction
Call B — child canonical normalization
```

If an existing trusted deterministic stage removes the need for one call, use fewer.

Before any live call, Codex must:

1. complete implementation and offline tests;
2. freeze focus selection;
3. freeze source scope;
4. freeze prompt/version/model configuration;
5. report exact intended call count and transmitted public source content;
6. request explicit owner approval.

No live call may occur before that approval.

## Provider Controls

For approved live calls:

- use the project's current approved OpenAI Responses API model unless the contract is explicitly amended;
- `store=False`;
- SDK automatic retries disabled;
- no hidden retries;
- no semantic retry without explicit owner approval;
- no prompt repair after seeing output;
- no external enrichment;
- preserve request ID, timing, usage, raw/rejected output where available.

## Human Learning Question

If a trusted child is produced and rendered, the owner review should answer:

> Does deeper resolution inside the accepted workspace help me understand the selected quantum concept while preserving my sense of where I am?

This is a product-learning question, not merely a rendering check.

## Human Review Protocol

After machine validation, provide only the viewer command and a minimal instruction such as:

```text
Use this to explore the quantum-mechanics material. When something offers deeper detail, follow it and see whether you still feel oriented.
```

Do not explain implementation choices first.

Capture spontaneous reaction.

Then evaluate:

### Trust

- Does the deeper representation appear semantically coherent?
- Does evidence support the relationships shown?
- Are unsupported details absent rather than confidently invented?

### Learning

- Does the child add understanding rather than restating the parent?
- Is the representation appropriate to the deeper structure?
- Does the depth feel useful enough to justify the additional complexity?

### Orientation

- Does the left map still tell me where I am?
- Does the selected parent concept remain an understandable anchor?
- Can I return to the parent resolution without losing navigation context?

### Interaction

- Does semantic depth feel integrated into BASELINE-003 rather than like opening another page?
- Is geometric navigation unaffected?

## Comparison

Compare against at least:

1. BASELINE-003 with parent-only realistic semantics;
2. the same workspace with the trusted child active;
3. original source passage for the selected focus where practical.

Do not claim general learning improvement from one owner review.

## Verdict Set

Final verdict must be exactly one of:

```text
SEMANTIC_DEPTH_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

`SEMANTIC_DEPTH_BETTER` requires:

- trusted child semantics;
- source grounding intact;
- parent immutability;
- useful deeper understanding;
- BASELINE-003 navigation/workspace behavior preserved;
- owner preference for having the deeper resolution available.

## Machine Evaluation

Report at least:

```text
parent artifact hashes before/after
focus selection record
source scope/hash
resolution strategy
live call count
retries
usage/runtime
assertion count if applicable
grounding success/failures
canonical relationships/propositions/claims
uncompiled assertions if applicable
semantic admission outcomes
child model round-trip
structure counts
representation types
layout diagnostics
child evidence integrity
parent/child shared entity IDs
workspace synchronization diagnostics
navigation camera invariance during semantic-depth changes
baseline asset hashes
```

## Explicit Non-Goals

Do not implement:

- new workspace shell;
- pane resizing redesign;
- new navigation metaphor;
- coupled wheel semantic zoom;
- recursive depth beyond one child level;
- multi-source retrieval;
- web/PDF ingestion;
- personalization engine;
- guided course/Journey mode;
- new canonical predicate vocabulary;
- broad proposition ontology expansion;
- simulation;
- production persistence/accounts;
- multi-agent deliberation.

## Testing

All ordinary tests remain offline.

Add deterministic tests for at least:

- focus-selection artifact validation;
- source-scope immutability;
- parent immutability;
- child assertion/grounding boundary where used;
- child canonicalization fail-closed behavior;
- no entity minting outside permitted child semantics;
- child model round-trip;
- child representation compilation;
- parent map remains stable when child activates;
- learning surface switches parent ↔ child resolution;
- navigation camera unchanged by semantic-depth toggle;
- evidence/detail synchronization for child items;
- BASELINE-003 asset immutability;
- deterministic evaluation artifact generation.

Keep the full offline suite passing.

## Evaluation Artifacts

Create:

```text
examples/evaluations/spec-020-realistic-semantic-depth-<date>/
```

Likely artifacts:

```text
focus-selection.json
source-scope.json
parent-hashes.json
child-assertion-result.json          if applicable
child-grounded-assertions.json       if applicable
child-canonicalization-result.json   if applicable
child.knowledge.json                 if trusted
child.structures.json                if trusted
child.representation.json            if trusted
semantic-review.json
workspace-manifest.json
workspace-diagnostics.json
report.json
run-history.json
human-review-template.json
README.md
viewer assets
```

Do not reproduce the full source unnecessarily.

## Acceptance Criteria — Offline / Architecture

- [ ] BASELINE-003 shell treated as frozen.
- [ ] BASELINE-001 and BASELINE-002 preserved.
- [ ] Frozen realistic quantum benchmark reused.
- [ ] Strongest accepted parent semantic artifacts reused where compatible.
- [ ] Focus selected and frozen before live output.
- [ ] Source scope selected and frozen before live output.
- [ ] Existing resolution strategy reused where appropriate.
- [ ] Child generation source-bounded.
- [ ] Strongest existing semantic reliability boundary reused where feasible.
- [ ] Parent model immutable.
- [ ] Parent navigation world remains stable.
- [ ] Child depth appears in learning surface, not as a replacement world map.
- [ ] Parent ↔ child learning resolution can be changed without losing camera context.
- [ ] Child representation follows detected structure.
- [ ] Evidence/provenance preserved.
- [ ] Geometric zoom remains independent from semantic depth.
- [ ] No recursive second child level.
- [ ] No personalization/Journey mode.
- [ ] No new semantic vocabulary unless a concrete blocker requires stopping for owner review.
- [ ] Full offline suite passes before live approval request.
- [ ] No live calls before explicit owner approval.

See `SPEC-020-ADDENDUM-acceptance-and-handoff.md` for live, review, verdict, and handoff requirements.
