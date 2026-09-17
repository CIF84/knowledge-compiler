# SPEC-059 — Semantic Typography / Enriched Prose Experiment

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Test whether a middle representation layer — **semantically enriched prose** — can improve perceptual access to important trusted facts without imposing the decoding overhead of a separate visual representation.

SPEC-058 showed that the current binary distinction between `PROSE` and `VISUAL REPRESENTATION` is too coarse.

The experimental representation continuum is now:

```text
PLAIN PROSE
    ↓
SEMANTICALLY ENRICHED PROSE
    ↓
MICRO-REPRESENTATION
    ↓
FULL STRUCTURAL / PERCEPTUAL REPRESENTATION
```

This packet tests only the second layer: semantically enriched prose.

## Owner verdict entering this packet

SPEC-058 owner verdict:

`UTILITY_GATE_CONFIRMED_REPRESENTATION_FORM_REMAINS_UNRESOLVED`

Accepted owner findings:

- retained structural visuals are strongly preferred to prose;
- retained claim visuals are mixed: visualization can plausibly reduce cognitive work, but the chosen visual grammar is not always effective;
- suppressed richer candidates are also mixed: the richer historical visuals are usually not useful, but salient trusted facts inside prose may benefit from perceptual emphasis;
- prose/low-complexity controls show no benefit from separate visuals;
- low-complexity prose should remain prose;
- the next unresolved question is whether important factual fragments can become easier to perceive through semantic typography without creating a separate representational grammar.

Canonical principles retained:

> **A representation must earn its complexity by externalizing cognitive work the learner would otherwise have to perform mentally.**

and:

> **Prose is a first-class representation, not a fallback.**

## Hypothesis

> For selected factual claims, source-faithful semantic typography can reduce visual-search and salience cost while preserving the low decoding overhead of prose.

Examples of the intended class of treatment:

```text
Bottlenecks and poor signal timing account for **45% of congestion**.
```

or:

```text
Scientists determined the position of **more than 23,000 atoms**
with **22-picometer precision**.
```

The experiment must not assume these examples are successful. Human owner review decides that.

## What enriched prose is

Enriched prose remains a sentence/paragraph as the dominant representation.

It may use bounded semantic typography to increase perceptual accessibility of trusted fragments, including:

- weight (`font-weight`);
- restrained size hierarchy;
- restrained semantic color/accent;
- typographic grouping;
- inline numeric/unit treatment;
- subtle emphasis of explicit contrast operands;
- subtle emphasis of explicit condition/exception fragments where useful.

It must remain readable in ordinary linear order without learning a new diagram grammar.

## What enriched prose is NOT

Do not turn enriched prose into:

- cards containing sentence fragments;
- disconnected giant-number callouts;
- diagrams;
- charts;
- relationship arrows;
- badges that replace meaning;
- decorative highlighting of arbitrary words;
- inferred semantic structure;
- a new KnowledgeModel semantic layer.

The sentence must remain the representation.

## Experimental semantic-emphasis metadata

Derive non-canonical presentation metadata only from already frozen trusted claim/representation payloads.

Allowed emphasis roles:

### `QUANTITY`

An explicit trusted number plus its semantically bound unit/object where traceable.

Prefer emphasizing the meaningful phrase (`45% of congestion`) rather than an isolated token (`45%`).

### `COMPARISON_OPERAND`

An explicit trusted operand/value participating in a comparison.

### `CONTRAST`

Explicit source-backed contrasted terms/fragments where perceptual differentiation may reduce search cost.

### `CONDITION_OR_SCOPE`

An explicit trusted condition/scope/exception fragment.

This role is experimental and must be tested conservatively because SPEC-056 showed that pulling conditions out into separate visual structures often increased cognitive load.

### `KEY_FACT_FRAGMENT`

A bounded explicit factual fragment whose salience is supported by frozen representation metadata but which does not justify a separate visual grammar.

Do not infer importance from domain/source identity.

## Emphasis constraints

- every emphasized character range must trace exactly to trusted prose;
- no paraphrasing inside emphasis spans;
- no added values/units/labels;
- preserve sentence order;
- preserve punctuation and full trusted meaning;
- do not emphasize more than is needed;
- default to no emphasis under uncertainty;
- no source-specific rules;
- no model judgment;
- emphasis metadata is presentation-only and must not mutate KnowledgeModel semantics.

## Experiment design

Create a deterministic browser A/B/C owner-review artifact with exactly **18 cases**.

### Group A — quantitative facts: 6 cases

Select 6 deterministic quantitative/factual claims from frozen SPEC-055/057/058 evidence, maximizing source/domain diversity.

Include, if identities remain frozen and available, the SPEC-058 examples involving:

- `45 percent` congestion;
- `more than 23,000 atoms` / `22 picometer` precision.

Treat these as frozen evidence cases, not privileged routing rules.

### Group B — comparisons/contrasts: 4 cases

Select 4 deterministic claim comparison/contrast cases from the SPEC-057 survivors.

This group asks whether enriched prose captures enough of the benefit that a separate comparison visual may not always be necessary.

### Group C — qualification/scope: 4 cases

Select 4 deterministic former `QUALIFIED_STATEMENT` candidates suppressed by SPEC-057.

This group tests whether inline semantic emphasis succeeds where separate qualification visuals failed.

### Group D — low-complexity prose controls: 4 cases

Select 4 deterministic prose/low-complexity cases, including the simple focused relationship control if compatible with the frozen evidence.

These are restraint controls. Enriched prose should be allowed to remain visually identical to plain prose if no emphasis earns its cost.

## A/B/C treatments

Each case must expose neutral treatments:

### A — `PLAIN_PROSE`

Exact trusted concise prose with ordinary typography.

### B — `ENRICHED_PROSE`

The exact same trusted prose with only source-traceable semantic typography.

### C — `RICHER_REFERENCE`

Where a frozen historical or utility-gated richer representation exists, show it unchanged as the third treatment.

If no legitimate frozen richer representation exists, C must be unavailable and clearly state `NO_FROZEN_RICHER_REFERENCE`; do not manufacture one.

Do not label any treatment as better/correct/recommended.

## Rendering principles

The experiment should test semantic typography, not visual decoration.

Use a deliberately restrained grammar:

- ordinary prose remains dominant;
- emphasis should be visible at a glance but not shout;
- keep semantic phrase and context spatially together;
- prefer bold/weight before large size changes;
- use size changes only where they improve scanability without breaking sentence flow;
- use color sparingly and with sufficient contrast;
- never rely on color alone;
- avoid multiple simultaneous emphasis techniques unless required for explicit multi-role distinction;
- no pill/badge/card treatment for emphasized facts;
- no animation required.

## Cognitive-utility framing

The middle layer should earn itself by reducing **visual search/salience work**, not by externalizing topology.

Conceptually:

```text
plain prose
    ↓
learner searches sentence for high-information fragment

vs.

enriched prose
    ↓
high-information fragment is perceptually accessible
while sentence grammar/context remain intact
```

This is distinct from full structural representation, which externalizes relational/topological/process work.

## Structural representation control

Do not reinterpret SPEC-058's strong structural result.

Structural diagrams remain outside this experiment and remain the preferred experimental form for high-utility topology/mechanism/composition cases.

SPEC-059 must not attempt to replace structural diagrams with enriched prose.

## Owner-review rubric

Expose a compact neutral rubric:

1. **Scanability** — Can the important factual content be found faster in B than A?
2. **Comprehension** — Does B make the sentence easier to understand without fragmenting it?
3. **Context preservation** — Does emphasized content remain clearly attached to what it means?
4. **Decoding overhead** — Does B avoid introducing a second visual grammar?
5. **Restraint** — Is emphasis absent/subtle when it adds little?
6. **Comparison with C** — Where C exists, which treatment best balances speed, meaning, and complexity?
7. **Truthfulness** — Does emphasis accidentally imply importance/contrast not warranted by the trusted text?

Do not infer or auto-score owner answers.

## Optional owner verdict capture

The artifact may allow local per-case selection among:

- `A_PREFERRED`;
- `B_PREFERRED`;
- `C_PREFERRED`;
- `EQUIVALENT`;
- `UNSURE`;

plus optional notes.

If implemented, keep subjective state local/exportable and outside canonical semantic artifacts.

## Machine/browser gate

At minimum verify:

- all 18 cases load;
- deterministic group/sample identity;
- A prose is byte/character faithful to frozen trusted prose;
- B prose has identical textual content/order/punctuation to A;
- every B emphasis span maps exactly to frozen trusted character ranges;
- no invented text/values/units;
- C is frozen historical/selected representation or explicitly unavailable;
- A/B/C switching works;
- no emphasis is represented as a detached card/callout/diagram;
- low-complexity controls may remain un-emphasized;
- no console errors/warnings;
- usable desktop layout;
- usable 390×844 narrow/mobile-like layout.

## Required outputs

Create:

`examples/evaluations/spec-059-semantic-typography-enriched-prose-experiment-20260917/`

Include at minimum:

- `report.json`;
- deterministic 18-case selection algorithm and IDs;
- group membership;
- A/B/C treatment identities;
- semantic-emphasis role and exact character ranges per B treatment;
- provenance/truthfulness audit;
- restraint audit;
- browser gate results;
- responsive results;
- deterministic regeneration evidence;
- zero-call/zero-extraction statement;
- owner-review command;
- owner-review state `PENDING`.

## Evaluation questions

The report must answer mechanically where possible and leave pedagogical questions to the owner:

1. Can enriched prose be generated deterministically from frozen trusted representation metadata?
2. Are all emphasis spans exactly source/trusted-text traceable?
3. How often does the conservative policy choose no emphasis?
4. Which emphasis roles are used and how often?
5. Can quantitative values remain semantically attached to their objects/units rather than becoming detached callouts?
6. Can qualification/scope be emphasized inline without reproducing SPEC-056's grammar-decomposition problem?
7. Can comparison operands be made perceptually accessible while retaining linear prose?
8. Do low-complexity controls remain restrained?
9. Does any case require new semantic inference? If yes, fail closed for that emphasis.
10. Is the artifact suitable for human A/B/C review?

## Mechanical decision branches

Choose exactly one:

### `ENRICHED_PROSE_SAFE_FOR_OWNER_REVIEW`

Traceable, restrained semantic typography can be generated without semantic mutation or unsupported emphasis.

### `ENRICHED_PROSE_TOO_PERMISSIVE`

The policy materially emphasizes unsupported/arbitrary fragments.

### `ENRICHED_PROSE_TOO_CONSERVATIVE`

Frozen explicit salience candidates cannot be represented meaningfully under the bounded contract.

### `ENRICHMENT_METADATA_INSUFFICIENT`

Frozen evidence cannot support deterministic semantic emphasis without new inference.

### `INCONCLUSIVE`

Evidence is mixed or mechanically insufficient.

Do not mechanically claim learner benefit.

## Recommended next-step vocabulary

Choose exactly one after machine evidence:

- `OWNER_REVIEW_REQUIRED`
- `ENRICHED_PROSE_POLICY_REFINEMENT`
- `VISUAL_GRAMMAR_SELECTION_EXPERIMENT`
- `MORE_DIAGNOSIS_REQUIRED`

No follow-up implementation is authorized.

## Protected state

Do not modify:

- Candidate B v2 extraction/evidence;
- admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- SPEC-055 evidence/plans;
- SPEC-056 artifact/evidence;
- SPEC-057 utility decisions/evidence;
- SPEC-058 artifact/evidence;
- production representation strategies/renderers;
- accepted SPEC-038 baseline;
- My Map/navigation/Explore Next product behavior;
- historical experiment artifacts.

Prefer isolated experimental code/artifacts.

## Explicitly forbidden

Do not:

- call a model/provider;
- use external retrieval;
- rerun extraction;
- change KnowledgeModel semantics;
- create relationships/propositions/topology from claims;
- modify StructureDetector;
- change SPEC-057 gate decisions;
- rewrite trusted prose;
- detach quantities from their meaning into giant-number callouts as the B treatment;
- invent semantic importance;
- use source/domain identity as an emphasis signal;
- encode owner comments as case-specific rules;
- redesign production UI/navigation;
- promote enriched prose or any renderer;
- claim pedagogical effectiveness from machine checks;
- implement visual-grammar selection in this packet.

## Validation

At minimum:

- focused SPEC-059 tests;
- browser machine gate;
- SPEC-038/056/057/058 regressions;
- control-plane tests;
- full offline suite;
- deterministic artifact regeneration;
- exact A/B textual identity checks;
- emphasis-range provenance checks;
- JSON validation;
- secret safety;
- `git diff --check`;
- protected-state hash verification;
- zero provider/model/network calls.

## Completion state

On completion:

- set SPEC-059 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report sample distribution, emphasis-role distribution, no-emphasis count, browser gate, validation, artifact path, and owner-review command;
- stop at `OWNER_REVIEW`;
- do not assign the human learner verdict or promote anything.

## Owner review question

> Can semantically enriched prose make important trusted facts perceptually easier to find and process while preserving the simplicity, context, and low decoding overhead that made prose preferable to unnecessary visualization?
