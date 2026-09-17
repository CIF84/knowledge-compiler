# SPEC-058 — Utility-Gated Learner-Surface A/B Experiment

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Test the learner-facing consequence of the SPEC-057 cognitive-utility gate.

The experiment must answer both sides of the selection decision:

1. where the gate retains richer representation, does that representation actually improve explanation relative to prose-only control?
2. where the gate suppresses richer representation, does prose feel appropriately restrained rather than impoverished?

This is a bounded human A/B experiment. Machine gates prove identity, safety, rendering, interaction, and deterministic selection. They must not assign the pedagogical verdict.

## Owner verdict entering this packet

SPEC-057 owner verdict:

`COGNITIVE_UTILITY_GATE_CONFIRMED`

Canonical principle:

> **A representation must earn its complexity by externalizing cognitive work the learner would otherwise have to perform mentally.**

Accepted SPEC-057 findings:

- SPEC-055 before gate: 53 richer claim plans, 45 prose controls;
- after utility gate: 7 `COMPARISON`, 91 `CONCISE_PROSE`;
- all 33 qualifier-only treatments were suppressed;
- all 13 quantitative callouts were suppressed;
- all 45 prose controls remained prose;
- economics system, software composition, and reciprocal mechanism structural controls survived;
- a simple focused relationship was only possible value and returned to prose;
- the 12 SPEC-056 cases aligned directionally with owner review without owner feedback being used as routing labels;
- cognitive utility, not representability alone, is the current experimental selection criterion.

## Core hypothesis

> Utility-gated representation selection will produce a learner surface where retained visuals materially externalize cognitive work, while suppressed candidates feel clearer or equally effective as prose without unnecessary visual decoding overhead.

## Experimental architecture

Preserve the accepted explanatory architecture:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ dominant representation selected by the utility gate

INSPECT / SELECTED / PREVIEW
→ local explanation of meaningful representation components

EXPLORE NEXT
→ future traversal
```

The review artifact may simplify fixed review navigation, as SPEC-056 did, but must not change product navigation semantics or production UI.

## Review groups

Build a deterministic owner-review artifact containing exactly **16 cases** across four groups.

### Group A — retained claim visuals: 4 cases

Select 4 of the 7 SPEC-057 claim `COMPARISON` survivors.

Selection rules:

- maximize source/domain diversity first;
- prefer cases with strongest explicit comparison payload and complete traceability;
- deterministic ordering by source ID then claim ID after diversity selection;
- do not hand-pick based on visual attractiveness.

For each case show:

- A: prose-only control;
- B: utility-gated comparison representation + the same concise prose.

### Group B — retained structural visuals: 4 cases

Use the deterministic SPEC-057 structural controls, including:

- economics multi-node system;
- software composition/dependency;
- reciprocal mechanism;
- one additional deterministic accepted structural case with strong externalization value, if frozen evidence supports it.

If no fourth strong frozen structural case exists, use the strongest remaining deterministic structural case but disclose its utility classification; do not invent one.

For each case show:

- A: faithful prose/textual control derived only from already-trusted explanation content;
- B: existing accepted structural representation + concise prose.

Do not regenerate semantic content.

### Group C — suppressed richer candidates: 4 cases

Select deterministically:

- 2 former `QUALIFIED_STATEMENT` candidates suppressed by SPEC-057;
- 2 former `QUANTITATIVE_CALLOUT` candidates suppressed by SPEC-057.

For each case show:

- A: prose-only utility-gated result;
- B: the preserved SPEC-056/SPEC-055 richer candidate treatment as a counterfactual comparison.

Clearly label B as **suppressed candidate**, not selected representation.

The purpose is to test whether the absence of visualization feels correct.

### Group D — prose / low-complexity controls: 4 cases

Select deterministically:

- 2 original SPEC-055 `CONCISE_PROSE` controls;
- the SPEC-057 simple focused relationship that was classified `POSSIBLE_EXTERNALIZATION_VALUE` and returned to prose;
- 1 additional deterministic low/possible-value case.

A and B should not manufacture visual complexity. Where a historical candidate exists, it may be shown only if frozen and clearly marked as non-selected; otherwise both views may remain prose.

These cases test restraint.

## A/B semantics

The experiment is not always “A prose, B better.” It is designed to pressure-test the gate.

For retained cases:

```text
A = prose/text control
B = utility-gated selected richer representation + prose
```

For suppressed cases:

```text
A = utility-gated selected prose
B = suppressed richer candidate + prose
```

The UI must make this distinction unmistakable.

Do not bias the owner by labeling one side “better,” “recommended,” or “correct.” It is acceptable to label factual system state such as `SELECTED BY GATE` and `SUPPRESSED BY GATE`, but the review question must remain neutral.

## Representation requirements

### Retained comparisons

The visual must actually externalize comparison work.

Prefer the simplest truthful comparative grammar supported by the frozen payload:

- aligned bars for explicit magnitudes;
- paired columns/rows for explicit categorical contrasts;
- another minimal comparison form only when dictated by frozen data.

Avoid decorative cards that merely repeat prose.

### Retained structural representations

Reuse accepted structural rendering semantics from the SPEC-038 baseline where possible.

The diagram should visibly carry topology/process/mechanism/composition that prose would otherwise require the learner to maintain mentally.

Do not redesign these renderers broadly in this packet.

### Suppressed qualifier/callout candidates

Preserve the historical richer candidate sufficiently faithfully to evaluate why it was suppressed.

Do not polish it into a materially new representation that could invalidate the gate comparison.

### Prose controls

Render prose cleanly and confidently.

Do not present prose as an apology, fallback warning, or empty state. Prose is a first-class selected representation.

## Prose composition

Every retained richer representation must include concise source-faithful prose.

The desired composition remains:

```text
representation that performs cognitive work
                 +
       concise explanatory prose
```

Avoid redundant repetition where the visual already carries an explicit value or relationship, while preserving the trusted claim/explanation meaning.

## Interaction

Allowed:

- hover/focus emphasis on meaningful representation components;
- click/select to update local `INSPECT / PREVIEW` content;
- A/B toggle;
- previous/next review case;
- direct navigation among the 16 fixed review cases.

Invariant:

> local representation interaction must never change learner territory or semantic location.

Do not add traversal/history product features.

## Owner-review rubric

For every case expose a compact neutral rubric:

1. **Comprehension** — Which treatment makes the meaning easier/faster to grasp?
2. **Cognitive work** — Does the visual actually perform comparison/topology/process work that A leaves to the learner?
3. **Decoding overhead** — Does the visual introduce more representational grammar than it removes?
4. **Truthfulness** — Does either treatment imply meaning absent from trusted evidence?
5. **Text burden** — Does useful visualization make prose cognitively lighter rather than merely duplicating it?
6. **Restraint** — Where the gate selected prose, does that choice feel appropriate?
7. **Distinctiveness** — Where the gate selected a visual, does it read immediately as a representation rather than UI chrome?

Do not require numeric scoring and do not infer owner answers.

## Human verdict capture

The artifact may provide optional per-case controls for the owner to record one of:

- `A_CLEARER`;
- `B_CLEARER`;
- `EQUIVALENT`;
- `UNSURE`;

and an optional short note.

If implemented, keep verdict state local/exportable and separate from canonical semantic artifacts. Do not automatically commit subjective review data.

This feature is optional; screenshots/notes remain sufficient.

## Browser artifact

Create:

`examples/evaluations/spec-058-utility-gated-learner-surface-ab-experiment-20260917/`

with an executable static/local browser review artifact and simple owner review command.

No model/network calls may be required to review it.

## Browser/machine gate

At minimum verify:

- all 16 cases load;
- group/category identities match frozen SPEC-057 evidence;
- retained/suppressed system state is labeled accurately;
- A/B toggle works for every case;
- retained claim comparison views render the frozen comparison payload;
- retained structural views reuse frozen accepted semantics;
- suppressed candidate views match frozen historical candidate evidence rather than newly invented treatments;
- prose controls do not acquire fake structure;
- inspection interaction remains local;
- case navigation does not mutate trusted semantic state;
- exact traced values/labels/qualifiers remain source-backed;
- no console errors/warnings;
- usable desktop layout;
- usable 390×844 narrow/mobile-like layout.

## Machine evidence vs human evidence

The report must keep these separate.

Machine evidence may establish:

- selection identity;
- rendering integrity;
- provenance;
- deterministic behavior;
- safety;
- no semantic mutation.

Machine evidence must **not** establish:

- comprehension improvement;
- cognitive-load reduction;
- pedagogical superiority;
- product promotion.

Those remain owner-review questions.

## Required report

Create:

`examples/evaluations/spec-058-utility-gated-learner-surface-ab-experiment-20260917/report.json`

Include at minimum:

- SPEC-057 report identity/hash;
- deterministic 16-case selection algorithm and IDs;
- group membership;
- utility classification and gate decision for each case;
- A/B treatment identities;
- representation/prose payload hashes;
- provenance/truthfulness audit;
- browser gate results;
- responsive checks;
- deterministic artifact regeneration evidence;
- zero-call/zero-extraction statement;
- owner-review command;
- owner-review state `PENDING`.

## Protected state

Do not modify:

- Candidate B v2 extraction/evidence;
- admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- SPEC-055 evidence/plans;
- SPEC-056 evidence/artifact;
- SPEC-057 utility decisions/evidence;
- production representation strategy semantics;
- production renderers except narrowly shared non-behavioral primitives if unavoidable and regression-proven;
- accepted SPEC-038 baseline behavior;
- My Map/navigation/Explore Next product behavior;
- historical experiment artifacts.

Prefer an isolated experimental review artifact.

## Explicitly forbidden

Do not:

- call a model/provider;
- use external retrieval;
- rerun extraction;
- change KnowledgeModel semantics;
- create topology from claims;
- modify StructureDetector;
- change SPEC-057 utility decisions;
- invent comparison values/operands/dimensions;
- improve suppressed historical visuals into new treatments;
- use owner feedback as hidden routing labels;
- redesign production UI/navigation;
- promote strategies/renderers;
- claim pedagogical effectiveness from machine checks;
- implement follow-up product changes.

## Validation

At minimum:

- focused SPEC-058 tests;
- browser machine gate;
- SPEC-038/056/057 regressions;
- control-plane tests;
- full offline suite;
- deterministic artifact regeneration;
- JSON validation;
- provenance/secret safety;
- `git diff --check`;
- verify protected hashes/state unchanged;
- verify zero provider/model/network calls.

## Completion state

On completion:

- set SPEC-058 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report sample/group distribution, browser gate, validation, artifact path, and owner-review command;
- stop at `OWNER_REVIEW`;
- do not assign the learner/product verdict or promote anything.

## Owner review question

> Does the cognitive-utility gate select richer representation precisely where the representation performs useful mental work — and select prose where visualization would merely add decoding overhead?
