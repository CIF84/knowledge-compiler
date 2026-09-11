# SPEC-039 — Semantic-to-Representation Compiler Gate

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Test the primary product uncertainty that remains after SPEC-038: whether Knowledge Compiler can take arbitrary source-bounded material, infer enough trusted semantic structure, and deterministically choose and populate a fitting learner-facing representation without handcrafted per-fixture representation logic.

This packet moves below the interface. SPEC-038 is the protected learner-facing baseline and is not to be redesigned.

## Product question

Can the compiler reliably perform this transformation?

```text
source material
        ↓
extraction / normalization
        ↓
trusted semantic structure
        ↓
representation strategy resolver
        ↓
learner-facing dominant representation
```

The important test is not whether a renderer can draw a causal diagram, hierarchy, sequence, comparison, or prose view. SPEC-034 through SPEC-038 already established that capability. The question is whether the compiler can infer the semantic conditions that justify one representation over another and provide the renderer with sufficient grounded structure.

## Hypothesis

Given source-bounded knowledge with materially different semantic shapes, the existing compiler pipeline can produce a trusted intermediate structure from which representation strategy can be selected without fixture-specific UI instructions.

If the source does not support sufficient structure, the compiler must fail closed toward a less committal representation rather than invent topology.

## Protected baseline

Do not redesign or weaken:

- SPEC-033 canonical revealed-knowledge navigation behavior;
- SPEC-034 representation-strategy diversity and resolver seam;
- SPEC-035 explanation/navigation isolation;
- SPEC-036 representation-local hover/click inspection;
- SPEC-037 quiet My Map territory/tree grammar;
- SPEC-038 dominant explanatory diagram canvas and four-surface responsibility model;
- trusted semantic vocabulary, grounding, provenance, and source-bounded depth behavior.

The accepted responsibility model remains:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ represents the current idea using the fitting semantic representation

INSPECT / SELECTED / PREVIEW
→ explains representation-local semantic components without changing learner location

EXPLORE NEXT
→ proposes future traversal
```

## Scope

Implement the smallest compiler-side experiment that can evaluate semantic-to-representation inference across heterogeneous source material.

The packet should exercise at least these semantic shapes where the committed source corpus supports them:

1. causal / mechanism;
2. hierarchy / composition;
3. process / sequence;
4. focused relationship;
5. compare / contrast;
6. worked example or rule-to-instance transformation;
7. prose-first / insufficiently structured material.

Do not manufacture a fixture merely to force every strategy. If a category is unsupported by the existing committed offline corpus, record that explicitly in the evaluation rather than fabricating evidence.

## Required implementation behavior

### 1. Source-first inference

Representation choice must be derived from normalized/trusted semantic output, not from:

- domain names;
- fixture filenames;
- concept labels;
- hard-coded source IDs;
- renderer-specific test switches;
- manually assigned representation labels for individual evaluation examples.

General semantic rules are allowed. Per-example answers are not.

### 2. Explicit intermediate evidence

For every evaluated focus object, emit machine-inspectable evidence sufficient to explain why a representation strategy was selected.

At minimum record:

- focus identity;
- available trusted concepts;
- available trusted relationships and predicates;
- detected structural signals;
- selected representation strategy;
- confidence/sufficiency or equivalent deterministic decision evidence;
- grounding/provenance references used by the selected representation;
- fallback reason when richer structure is rejected.

Do not add opaque model reasoning or chain-of-thought fields. The evidence should be deterministic product metadata.

### 3. Fail-closed strategy selection

A richer representation may be selected only when the trusted semantic structure warrants it.

Examples:

- one causal edge must not be inflated into a complex system diagram unless surrounding trusted structure supports that topology;
- reciprocal mechanism requires grounded reciprocal directions, not visual symmetry alone;
- hierarchy/composition requires supported membership/composition structure;
- process/sequence requires ordering or temporal/process semantics;
- comparison requires grounded comparable dimensions or explicit contrast structure;
- worked example requires a supported rule/example or transformation relation.

When evidence is thin or ambiguous, prefer focused relationship or concise prose as appropriate.

### 4. Renderer independence

The semantic-to-representation decision must exist before learner-facing rendering. Renderer code may consume the decision but must not become the authority that infers semantic truth from labels or layout convenience.

### 5. No navigation coupling

This packet must not alter revealed-territory semantics, traversal semantics, Explore Next behavior, or introduce Back/history.

## Evaluation corpus

Use committed offline material already available in the repository. Prefer a heterogeneous evaluation set spanning the existing domains (for example electromagnetism, economics, history of printing, and software architecture) because the test is semantic generality rather than domain-specific correctness.

Create a deterministic evaluation artifact under:

`examples/evaluations/spec-039-semantic-to-representation-compiler-gate-<date>/`

The artifact must include a `report.json` summarizing every evaluated case and aggregate results.

## Required evaluation questions

For each case answer mechanically where possible:

1. What trusted semantic structure was available?
2. What representation strategy was selected?
3. Which structural signals caused that selection?
4. Was any richer candidate rejected, and why?
5. Is every displayed structural element grounded in committed source evidence?
6. Would changing only a domain/fixture label leave the semantic decision unchanged?
7. Does insufficient structure fall back rather than hallucinate topology?

Aggregate the results by representation strategy and by source domain.

## Tests

Add focused offline tests proving at minimum:

- strategy selection is based on semantic structure rather than fixture/domain identity;
- semantically equivalent structures with different labels resolve consistently;
- materially different structures can resolve to different representation strategies;
- unsupported/ambiguous structure fails closed;
- reciprocal structure is not inferred from a single direction;
- provenance survives into the representation decision/output;
- SPEC-038 rendering can consume the compiler-produced strategy without fixture-specific overrides;
- no explanatory interaction changes learner location;
- deterministic regeneration is byte-identical.

Run the full offline suite and relevant regression suites for SPEC-033 through SPEC-038.

## Browser / learner-facing gate

Render a representative subset through the existing SPEC-038 learner-facing surface solely to verify that compiler-produced decisions reach the protected UI correctly.

This is not a visual redesign packet.

The browser gate must confirm:

- the dominant representation is the first explanatory object where structural evidence warrants it;
- representation diversity remains visible across heterogeneous cases;
- sparse/prose fallbacks remain sparse/prose rather than being forced into diagrams;
- local hover/click inspection remains non-navigational;
- My Map remains the quiet territory tree;
- console has zero errors/warnings attributable to this packet.

## Explicit non-goals

Do not implement:

- broad UI redesign;
- new navigation architecture;
- Back / learner traversal history;
- personalization or learner-state modeling;
- quizzes/mastery;
- guided courses;
- automatic analogy generation;
- universal graph rendering;
- decorative animation;
- live source ingestion;
- live LLM/model calls;
- external network calls;
- new dependencies unless strictly necessary and separately authorized.

## Authority and network policy

`OFFLINE_ONLY` is strict.

No live/model/external calls are authorized. Use committed fixtures and deterministic local logic only.

If implementation appears to require a live model call to answer the product question, stop and report the boundary rather than silently widening authority. That result itself is useful evidence for the next decision.

## Deliverables

1. compiler-side semantic-to-representation inference implementation or the smallest necessary seam/refactor;
2. deterministic decision/evidence schema;
3. focused tests;
4. regression results;
5. evaluation corpus and `report.json`;
6. representative browser verification against SPEC-038;
7. concise implementation report including deviations, if any.

## Success criteria

SPEC-039 succeeds if the offline experiment demonstrates that representation choice is a consequence of trusted semantic structure rather than handcrafted fixture knowledge, while preserving grounding, fail-closed behavior, deterministic output, and the SPEC-038 learner-facing architecture.

Success does **not** require perfect coverage of every representation family. It requires convincing evidence that the architecture can generalize beyond individually authored examples.

## Failure is informative

A valid outcome is that the existing semantic model is too weak to support reliable representation selection.

If so, do not compensate in the renderer. Report precisely what semantic information is missing and where in the compiler pipeline it should be introduced. The next packet should then address that semantic bottleneck.

## Owner review gate

After implementation and validation:

- commit and push only as permitted by repository protocol;
- mark SPEC-039 `IMPLEMENTED_AWAITING_REVIEW`;
- do not promote it to a baseline;
- do not authorize follow-up implementation;
- stop for owner review.

Owner review should answer one primary question:

> Is representation now being chosen because the compiler understands enough of the source's trusted semantic structure, rather than because we taught individual examples how they should look?

## Implementation record

The offline compiler gate is implemented and awaits owner review. Deterministic
semantic decisions cover the supported causal, hierarchy, dependency, process,
reciprocal, focused-relationship, comparison, and prose cases without domain,
fixture, label, or source-ID strategy rules. The protected SPEC-038 runtime binds
exactly to every supported renderer plan and passes the representative browser
gate without navigation or interaction changes.

The evidence is intentionally mixed rather than promoted: the compiler recognizes
an explicit grounded comparison proposition but SPEC-038 has no protected comparison
renderer, and the committed corpus does not contain a grounded rule-to-instance
mapping that would justify `WORKED_EXAMPLE`. The transfer-event candidate therefore
fails closed to prose. No product verdict or baseline promotion is recorded here.
