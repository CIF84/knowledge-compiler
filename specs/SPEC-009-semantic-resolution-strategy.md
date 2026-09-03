# SPEC-009 — Semantic Resolution Strategy Spike

## Status

Ready for implementation.

## Primary Question

> Can Knowledge Compiler generate meaningfully different, source-grounded higher-resolution models according to the semantic role of the selected focus — for example process → stages, variable → causal neighborhood, component/system → internals — without introducing a large brittle ontology or weakening grounding?

## Why This Experiment Exists

SPEC-008 demonstrated that automatic multi-resolution compilation is possible in reality. The Economics `market price` child was generated automatically from source, passed strict grounding and semantic validation, flowed through existing deterministic downstream layers, and was cognitively judged to behave like a genuine deeper semantic layer.

SPEC-008 also revealed that **semantic zoom is not universal decomposition**.

A deeper explanation of a variable such as `market price` is naturally its causal neighborhood, while a process may be best explained through internal stages and a component/system through subcomponents and interactions.

The next uncertainty is therefore not recursion, active map navigation, or personalization.

It is:

```text
WHAT SHOULD “ZOOM IN” MEAN
FOR DIFFERENT SEMANTIC OBJECTS?
```

SPEC-009 tests whether a very small set of explicit resolution strategies improves child-model quality over a generic “give me more detail” instruction.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `debriefs/DEBRIEF-007-progressive-disclosure-semantic-navigation.md`
8. `debriefs/DEBRIEF-008-automatic-multi-resolution-compilation.md`
9. `specs/SPEC-008-automatic-multi-resolution-compilation.md`
10. `src/knowledge_compiler/resolution_compiler.py`
11. `src/knowledge_compiler/openai_resolution.py`
12. `src/knowledge_compiler/relationships.py`
13. accepted SPEC-008 live artifacts

Verify this SPEC file is complete before implementation. SPEC-008 was accidentally truncated; do not repeat that failure.

## Experimental Hypothesis

The working hypothesis is:

> A small semantic-role-aware strategy layer can tell the ResolutionCompiler what kind of explanatory refinement to seek, improving parent-child coherence and usefulness without changing canonical semantic truth or requiring a large ontology.

Candidate strategy families:

```text
PROCESS
→ internal stages / transitions / dependencies

VARIABLE
→ causal drivers / constraints / consequences

COMPONENT_OR_SYSTEM
→ subcomponents / responsibilities / interactions
```

These are experimental resolution strategies, not new `KnowledgeModel` entity types or permanent ontology commitments.

## Scope

Implement the smallest changes needed to:

1. add a provider-independent `ResolutionStrategy` concept outside the canonical semantic IR;
2. support exactly three experimental strategies:
   - `PROCESS_STAGES`
   - `VARIABLE_CAUSAL_NEIGHBORHOOD`
   - `COMPONENT_INTERNALS`
3. map selected benchmark focus concepts to one explicit strategy;
4. preserve a `GENERIC_DETAIL` control strategy representing the existing SPEC-008 behavior;
5. run type-aware vs generic resolution generation on the same source/focus where practical;
6. hold provider, model, source scope, grounding rules, relationship grammar, downstream structure detection, representation, and layout constant;
7. compare generated children on source grounding, parent coherence, resolution gain, structural usefulness, and parent-child compression relationship;
8. preserve all failed/rejected provider outputs and do not retry silently;
9. keep maximum generated depth at exactly one;
10. leave navigation UI behavior unchanged apart from exposing strategy metadata in experimental artifacts if useful.

## Benchmark Cases

Use three bounded focus cases representing distinct semantic roles.

### 1. VARIABLE — Economics

Focus:

```text
market price
```

Strategy:

```text
VARIABLE_CAUSAL_NEIGHBORHOOD
```

This is the strongest existing success and should serve as a positive control.

The type-aware instruction should seek:

- upstream drivers;
- constraints/pressures;
- downstream consequences/responses;
- mechanisms connecting them;
- no unsupported loop closure.

Compare against the successful SPEC-008 generic child where possible.

### 2. PROCESS — Software Architecture or a committed richer local fixture

Prefer an accepted process-like focus from existing source if one is semantically appropriate.

If the original Software Architecture source does not expose a process focus with enough depth, add one clearly labeled committed local source fixture for this experiment.

Strategy:

```text
PROCESS_STAGES
```

The type-aware instruction should seek:

- ordered stages;
- transitions;
- prerequisites/dependencies;
- outputs/handoffs;
- explicit temporal order only when supported.

Do not force `PRECEDES` where source chronology is absent.

### 3. COMPONENT / SYSTEM — Software Architecture

Focus:

```text
API component
```

or another accepted component/system focus if the source better supports it.

Strategy:

```text
COMPONENT_INTERNALS
```

The type-aware instruction should seek:

- internal parts/responsibilities;
- interactions among internals;
- interfaces/handoffs;
- dependencies;
- containment only where source supports it.

If the accepted source lacks sufficient internal detail, report `INSUFFICIENT_SOURCE_DETAIL` rather than inventing internals.

## Generic Control

For each benchmark focus that reaches a live provider call, run:

```text
GENERIC_DETAIL
```

and the assigned type-aware strategy against the same permitted source and parent context.

The generic instruction should remain close to SPEC-008's existing resolution prompt.

Do not optimize the generic prompt to lose intentionally. It is a real control.

## Experimental Isolation

Hold constant:

- provider;
- model;
- source scope;
- parent `KnowledgeModel`;
- focus concept;
- canonical relationship registry;
- validation rules;
- evidence-resolution logic;
- maximum child depth;
- structure detection;
- representation building;
- layout;
- viewer.

Primary variable:

```text
resolution strategy instruction
```

If prompt text outside the strategy section must change, report it explicitly.

## ResolutionStrategy Boundary

Add a small provider-independent contract, for example:

```text
ResolutionStrategy
    id
    semantic_role
    objective
    seek
    avoid
```

Exact representation is flexible.

Constraints:

- do not add strategy metadata to canonical `RelationshipType`;
- do not redesign `EntityType` merely to support this experiment;
- do not create a general ontology of all knowledge forms;
- strategy definitions should be inspectable and testable outside provider prompt code;
- provider prompt rendering should consume canonical strategy definitions rather than duplicate their semantics ad hoc.

## Strategy Selection

For SPEC-009, strategy selection may be explicit/configured for benchmark cases.

Do **not** build an automatic strategy classifier yet.

The experiment asks whether strategies help, not whether the compiler can choose one autonomously.

Record enough metadata so a future experiment could test automatic strategy selection.

## Prompt Contract

All strategies must retain the common strict contract:

- use only permitted source material;
- selected parent focus remains central;
- return finer explanatory resolution, not summary/paraphrase;
- exact unique quotes nominate source evidence;
- no trusted offsets from provider;
- `SOURCE` requires evidence;
- `INFERRED` must not carry source evidence;
- canonical relationship semantics/direction unchanged;
- permission to return `INSUFFICIENT_SOURCE_DETAIL`;
- no hidden model knowledge used to fill gaps.

Strategy-specific instructions should alter **what explanatory pattern to seek**, not the grounding/trust rules.

## Failure Outcomes

Preserve current bounded outcomes:

```text
SUCCESS
INSUFFICIENT_SOURCE_DETAIL
GROUNDING_FAILURE
SEMANTIC_VALIDATION_FAILURE
PROVIDER_FAILURE
```

Add no hidden repair/retry machinery.

If type-aware strategy succeeds where generic fails, preserve both outputs.

If generic succeeds and type-aware fails, that is equally important evidence.

## What Counts as Strategy Improvement?

Do not evaluate improvement by node count or lexical similarity.

Compare on:

### Grounding integrity
All source-derived semantic content is exactly grounded.

### Focus relevance
The child remains clearly about the selected parent concept.

### Resolution gain
The child exposes meaningful lower-level explanatory structure not already visible at the parent level.

### Strategy fit
The child exhibits the intended explanatory pattern where source supports it:

```text
PROCESS → stages
VARIABLE → causal neighborhood
COMPONENT → internals/interactions
```

### Structural usefulness
The child produces coherent higher-order structures rather than a bag of isolated concepts.

### Parent-child compression relationship
A reviewer can plausibly treat the parent concept as a higher-level compression/abstraction of the child.

### Cognitive usefulness
The child feels useful when explored in Contextual/Layers mode.

## Deterministic Strategy Diagnostics

Machine evaluation may record simple diagnostics such as:

```text
strategy
focus semantic role
child entity count
child relationship count
SOURCE / INFERRED counts
structure types detected
representation types produced
strategy-pattern coverage
```

Examples of strategy-pattern coverage:

- PROCESS: explicit supported `PRECEDES` sequence or stage dependencies;
- VARIABLE: incoming/outgoing causal-family relationships around focus-related variables;
- COMPONENT: supported `PART_OF`, `REQUIRES`, `ENABLES`, interaction/transfer relationships among internals.

These are diagnostics, not universal quality scores.

## Parent-Child Compression Review

Create a comparison artifact that asks, for each generated child:

```text
Does the child explain the selected parent at finer resolution?
Could the parent plausibly summarize/compress the child?
What child information is lost at the parent resolution?
Does that information loss feel appropriate to higher abstraction?
```

Machine code may record evidence/features, but final compression judgment remains human.

## Source Fixtures

Original accepted source material must be tried first where appropriate.

If a benchmark source lacks the necessary semantic depth, a richer committed local fixture is allowed only when:

- clearly marked experimental;
- source is written as natural explanatory material, not a graph-answer key;
- provenance remains exact;
- original-source insufficiency remains preserved separately;
- no web retrieval occurs during evaluation.

## Provider / Model

Use the same provider and model family as SPEC-008 where available and practical:

```text
OpenAI Responses API
gpt-5.6-luna
```

Record actual provider/model/prompt/compiler/strategy versions in artifacts.

No secret values in repository artifacts.

## Live Evaluation Matrix

Aim for this matrix where source sufficiency permits:

| Focus role | Focus | Generic | Type-aware |
| --- | --- | --- | --- |
| Variable | market price | run | VARIABLE_CAUSAL_NEIGHBORHOOD |
| Process | chosen process | run | PROCESS_STAGES |
| Component/System | API component | run | COMPONENT_INTERNALS |

This is at most six primary live generation calls before explicit failures. Do not expand the matrix opportunistically.

No automatic retries.

## Human Review

After independent repository/semantic inspection, the owner should compare Generic vs Type-aware children in Contextual/Layers mode.

Capture spontaneous reaction first.

Then ask:

- Which child feels more like a genuine semantic zoom?
- Which stays more coherent with the parent focus?
- Does the strategy produce the expected explanatory form?
- Does it omit important source-grounded information the generic child captured?
- Does strategy guidance reduce or increase forced semantics?
- Can the parent plausibly compress the child?
- Would this strategy help while actually learning the topic?

Use qualitative:

```text
TYPE_AWARE_BETTER
GENERIC_BETTER
SAME
BOTH_WEAK
```

Do not claim general learner benefit from owner-only review.

## Navigation / UI

Do not change the validated navigation grammar.

Generated children should continue to plug into existing Contextual/Layers mode.

No active context-map navigation in SPEC-009.

No new cognitive presets.

No BASELINE-002.

## Explicit Non-Goals

Do not implement:

- automatic strategy classification;
- arbitrary recursive depth;
- active semantic-map navigation;
- lateral sibling movement;
- caching/on-demand infrastructure;
- web retrieval;
- cross-document synthesis;
- graph database;
- personalization engine;
- user profiles;
- preset recommendation;
- new canonical relationship predicates unless absolutely blocking and explicitly justified;
- large entity ontology redesign;
- event/state redesign unless proven a hard blocker;
- simulator;
- 3D knowledge graph;
- frontend rewrite;
- mobile/responsive redesign;
- formal user-study infrastructure.

## Offline Testing

Normal tests remain offline and deterministic.

Add tests covering at least:

- strategy registry/contracts;
- unique stable strategy IDs;
- provider-independent strategy rendering/input;
- generic control preserved;
- explicit benchmark strategy mapping;
- source scope unchanged by strategy;
- grounding rules unchanged by strategy;
- canonical relationship semantics unchanged;
- `INSUFFICIENT_SOURCE_DETAIL` supported under every strategy;
- no automatic retries;
- child round-trip;
- downstream structure/representation compatibility;
- parent immutability;
- baseline/navigation artifacts unchanged;
- prior tests continue to pass.

## Evaluation Artifacts

Create a committed directory such as:

```text
examples/evaluations/spec-009-resolution-strategy-20260903/
```

Include:

- per-run source-scope metadata;
- generic and type-aware resolution results;
- successful child semantic/structure/representation artifacts;
- failed/rejected results;
- comparison report;
- strategy diagnostics;
- run history;
- human-review template;
- richer local source fixtures/results if needed.

Keep raw provider payloads only if safe and genuinely useful.

## Complexity Budget

Report explicitly:

- number of strategies added;
- prompt growth attributable to strategy definitions;
- new runtime dependencies;
- new semantic IR fields/types;
- new canonical predicates;
- provider call count;
- retries;
- source fixtures added;
- whether any general recursive/navigation architecture was introduced.

Target:

```text
3 type-aware strategies
+ 1 generic control
0 new canonical predicates
0 recursive depth growth
0 navigation redesign
0 personalization machinery
```

## Acceptance Criteria

SPEC-009 is technically complete when all are true:

- [ ] A provider-independent resolution-strategy contract exists.
- [ ] Exactly three type-aware strategies plus one generic control are supported.
- [ ] Strategy semantics are not duplicated inconsistently inside provider prompt code.
- [ ] Benchmark focus → strategy mapping is explicit, not auto-classified.
- [ ] Existing grounding/provenance validation remains unchanged or stricter.
- [ ] Existing canonical relationship vocabulary/direction remains unchanged unless a blocking exception is explicitly justified.
- [ ] Parent `KnowledgeModel` remains immutable.
- [ ] Maximum generated depth remains one.
- [ ] Generic and type-aware runs use equivalent source scope and parent context.
- [ ] No hidden retries or favorable-run selection occur.
- [ ] All outcomes, including failures, are preserved.
- [ ] Successful children pass existing downstream deterministic structure/representation/layout pipeline.
- [ ] Comparison artifacts assess focus relevance, resolution gain, strategy fit, structural usefulness, grounding, and compression relationship.
- [ ] Existing Contextual/Layers viewer can display successful generated children without navigation redesign.
- [ ] Automated tests pass offline.
- [ ] Live evaluation matrix is completed as far as source sufficiency permits.
- [ ] Human-review template is committed.
- [ ] Implementation and evaluation are committed and pushed to canonical `origin/main`.
- [ ] No `DEBRIEF-009` is created during implementation.

## Product Decision Gate

The primary product question is:

> Does explicit semantic-role-aware resolution guidance produce meaningfully better semantic zoom than a generic deeper-detail compiler?

Valid outcomes:

### TYPE-AWARE WINS
Resolution strategy becomes a justified architectural concept. The next experiment may test automatic strategy selection and/or on-demand compilation.

### GENERIC WINS OR TIES
Do not add strategy complexity. Keep the generic ResolutionCompiler and move to the next constraint.

### MIXED BY ROLE
Preserve only strategies with evidence of distinct value; do not force one architecture across all semantic roles.

### BOTH WEAK
Investigate source sufficiency, entity/event/state modeling, or relationship semantics before adding recursion/navigation complexity.

## Required Handoff

When complete, Codex must report:

1. architecture changes;
2. strategy contract and exact strategies;
3. benchmark focus mappings;
4. generic-control behavior;
5. provider/model/prompt/compiler versions;
6. source-scope equivalence result;
7. offline test result;
8. live evaluation matrix and exact outcomes;
9. per-run token usage and monetary cost if authoritatively available;
10. failures/rejections/retries;
11. generated child entity/relationship/claim counts;
12. SOURCE vs INFERRED counts;
13. structure/representation results;
14. strategy-pattern diagnostics;
15. generated-vs-generic comparison;
16. grounding/provenance integrity;
17. canonical-direction integrity;
18. parent immutability result;
19. exact local review command(s);
20. human-review artifact path;
21. complexity-budget result;
22. dependencies added/removed;
23. deviations;
24. commit SHA;
25. confirmation pushed to canonical GitHub.

Do not create `DEBRIEF-009`. Human review follows independent repository inspection.

## Operational Learning Capture

The eventual debrief should record:

- whether semantic-role-aware strategy adds value over generic prompting;
- whether strategy branching creates prompt/maintenance complexity disproportionate to benefit;
- whether strategy diagnostics correlate with human compression/usefulness judgment;
- whether source insufficiency differs systematically by semantic role;
- whether a small strategy set appears sufficient or begins expanding into an ontology smell;
- whether the project has earned the right to test automatic strategy selection;
- whether on-demand compilation should follow next;
- whether active context-map navigation should remain deferred.

## Final Constraint

SPEC-009 must answer:

```text
WHAT SHOULD ZOOM IN MEAN?
```

before the project attempts:

```text
HOW DO WE ZOOM EVERYWHERE, RECURSIVELY, ON DEMAND?
```
