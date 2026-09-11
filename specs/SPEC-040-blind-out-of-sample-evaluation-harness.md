# SPEC-040 — Blind Out-of-Sample Evaluation Harness

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Prepare a genuinely blind out-of-sample compilation experiment without exposing the final evaluation sources before the compiler/evaluator is frozen.

SPEC-039 established convincing evidence that representation strategy can be inferred from trusted semantic structure rather than fixture/domain identity. The next uncertainty is whether that capability survives source material outside the project's development world.

This packet builds and freezes the generic evaluation harness only. It must stop before any live/model/external source execution.

## Scientific question

> Can a frozen Knowledge Compiler pipeline process previously unseen source material end-to-end and produce trustworthy semantic structure and representation decisions without fixture-specific adaptation?

SPEC-040 does **not** answer that question yet. It creates the conditions under which the next execution can answer it credibly.

## Why the source set must remain undisclosed during implementation

If the final evaluation sources are known while the harness/compiler is being implemented, even accidental source-specific adaptation weakens the experiment.

Therefore the order is deliberately:

```text
freeze compiler + evaluation harness
        ↓
record implementation commit/hash
        ↓
select and freeze out-of-sample source set
        ↓
explicitly authorize bounded live execution
        ↓
run without implementation changes
        ↓
owner reviews learner-facing outputs
```

The source set for the live experiment must not be committed or disclosed in SPEC-040.

## Protected state

Preserve:

- SPEC-038 learner-facing visual/interaction baseline;
- SPEC-039 semantic-to-representation compiler behavior and accepted principles;
- SPEC-033 revealed-territory navigation semantics;
- SPEC-034 representation diversity;
- SPEC-035 explanation/navigation isolation;
- SPEC-036 local inspection semantics;
- SPEC-037 My Map visual grammar;
- trusted semantic vocabulary, grounding, provenance, and fail-closed behavior;
- existing provider/model adapter behavior unless a generic harness seam is strictly required.

Do not close known coverage gaps merely for this experiment:

- comparison renderer coverage remains incomplete;
- worked-example capability remains unproven.

Those gaps are part of the current frozen capability and should remain visible during the blind evaluation.

## Scope

Implement a generic evaluation path capable of accepting a later frozen source packet and producing, per source:

```text
raw source document
        ↓
normalization / source identity
        ↓
semantic extraction proposal
        ↓
deterministic grounding + validation
        ↓
trusted KnowledgeModel
        ↓
structure detection
        ↓
SemanticRepresentationDecision
        ↓
SPEC-038-compatible representation plan when renderer coverage exists
        ↓
learner-facing review artifact
```

The harness must not contain source-specific branch logic.

## Required source-packet contract

Define a minimal deterministic input contract for the later blind execution. It should support at least:

- stable source ID;
- title / neutral display label;
- exact source text or approved bounded excerpt;
- source/provenance metadata;
- optional focus hint only if the experiment design requires one, and if used it must be generic rather than representation-prescriptive;
- immutable source hash;
- explicit statement that no expected representation strategy is supplied.

The later source packet must **not** contain:

- expected concepts;
- expected relationships;
- expected structure type;
- expected representation strategy;
- expected diagram topology;
- evaluator hints such as "this is causal" or "render as hierarchy".

## Generic evaluation output

For each blind source, the harness must preserve machine-inspectable stages sufficient for independent review:

1. source identity/hash;
2. provider request metadata and exact bounded source scope when live execution is later authorized;
3. proposed assertions/semantic extraction output;
4. exact grounding/evidence resolution;
5. rejected/failed assertions;
6. admitted trusted semantic model;
7. detected structures;
8. representation decision and deterministic decision evidence;
9. renderer binding or truthful missing-renderer state;
10. learner-facing review artifact;
11. complete run history and failure state.

Do not hide failures or retry until a favorable result appears.

## Blindness / anti-overfitting checks

The harness must mechanically verify that representation selection does not depend on:

- source title;
- source filename;
- domain display label;
- source packet ordinal;
- source ID string;
- evaluator-provided expected strategy (which must not exist);
- source-specific conditional logic introduced by SPEC-040.

Add a code-level or test-level guard against fixture/source identifiers appearing in strategy-selection rules.

## Evaluation design for the later execution

The next live execution should use a small set of genuinely out-of-sample sources spanning materially different kinds of knowledge, selected **after SPEC-040 is frozen**.

The later source selection should optimize for domain novelty, not for guaranteed strategy coverage.

A valid blind set might therefore naturally produce:

- several structural representations;
- several prose/focused-relationship fallbacks;
- unsupported/failed cases.

Do not require one source per renderer family. That would bias source selection toward the system's existing capabilities.

## Product evaluation dimensions

Prepare the report schema so the later run can answer separately:

### Semantic fidelity

- Are admitted claims/relationships supported by exact source evidence?
- Did fail-closed validation reject unsupported claims?

### Structural usefulness

- Did detected structures expose meaningful organization in the source?
- Did the compiler avoid inventing topology?

### Representation appropriateness

- Does the selected representation follow the trusted structure?
- Did a missing renderer remain explicit rather than silently substitute misleading UI?

### Learner usefulness

Reserved for owner review of the fixed artifact:

> Did the compiled representation make the unfamiliar source materially easier to understand than the source text alone?

Machine code must not assign that subjective verdict.

## Provider-call planning

SPEC-040 is `OFFLINE_ONLY` and must make **zero live/model/external calls**.

However, the harness must produce an exact proposed execution plan for the next gate, including:

- model/provider intended for extraction/canonicalization;
- number of planned calls per source;
- maximum total calls;
- retry policy;
- whether source text is transmitted;
- prompt/version identifiers;
- storage setting;
- failure/stop behavior;
- expected artifacts;
- estimated token accounting if deterministically available before execution.

The implementation handoff must request explicit owner approval before any source material is transmitted to an external provider.

## Live execution integrity for the follow-up packet

The follow-up execution must run from the frozen SPEC-040 compiler/harness commit.

If the blind sources expose an implementation defect before provider execution begins, stop and report it. Do not silently patch after seeing the source set.

After any source has been submitted to the provider, implementation changes invalidate the blind run. A repair requires a new frozen experiment/run designation.

## UI constraints

Do not redesign the interface.

The learner-facing review artifact must use the accepted SPEC-038 surface unchanged except for generic plumbing required to load blind-run outputs.

Preserve:

```text
MY MAP
WHAT DOES THIS MEAN?
INSPECT / SELECTED / PREVIEW
EXPLORE NEXT
```

No Back/history implementation is authorized.

## Required implementation work

1. Create the generic blind source-packet schema and parser/validator.
2. Create a generic end-to-end evaluation orchestrator that can consume the later packet.
3. Ensure no source-specific expectations are required by the runner.
4. Preserve every intermediate semantic/grounding/representation artifact needed for audit.
5. Add anti-overfitting/source-identity invariance tests.
6. Add fail-closed tests for malformed, semantically thin, or unsupported source packets using synthetic neutral fixtures only.
7. Add a deterministic dry-run mode that exercises orchestration without provider calls.
8. Prove the dry-run can reach the protected SPEC-038 rendering seam using accepted deterministic semantic fixtures without changing UI behavior.
9. Generate a blank/future-run report template and exact bounded live-execution plan.
10. Freeze the implementation and stop for owner review/next-gate authorization.

## Machine acceptance

Before handoff verify at least:

```text
control plane valid
OFFLINE_ONLY respected
live/model/external calls == 0
SPEC-038 baseline behavior preserved
SPEC-039 semantic representation compiler preserved
source packet contains no expected strategy/structure answers
evaluation runner contains no source/domain-specific branching
source/title/id invariance tests pass
malformed input fails closed
semantically thin dry-run case remains conservative
all intermediate audit artifacts are preserved
dry-run deterministic regeneration is byte-identical
browser/regression gate against SPEC-038 passes
console clean
full offline suite passes
git diff --check passes
```

## Durable artifacts

Create an isolated evaluation-preparation directory:

`examples/evaluations/spec-040-blind-out-of-sample-evaluation-harness-<date>/`

Include at least:

- `report.json`;
- source-packet JSON schema/example containing only synthetic neutral text;
- dry-run artifacts;
- anti-overfitting/invariance evidence;
- exact proposed live-execution plan;
- frozen harness/compiler commit identifier;
- browser regression evidence where applicable.

Do **not** include the real blind source set.

## Completion state

On successful offline implementation:

- set SPEC-040 to `IMPLEMENTED_AWAITING_REVIEW`;
- set `STATUS.md` active packet to `NONE`;
- commit and push according to repository protocol;
- stop;
- report the exact frozen commit and proposed live-execution plan;
- request explicit approval for the separate blind source selection/execution gate.

Do not begin live execution automatically.

## Owner review question

The owner/ChatGPT review at this stage is procedural/scientific rather than pedagogical:

> Is the evaluation harness genuinely generic and frozen before the blind source set is selected, such that a later out-of-sample run cannot reasonably benefit from source-specific implementation adaptation?

If yes, the next packet should freeze the source set and explicitly bound the live calls without changing the compiler/harness implementation.

## Implementation record

The generic harness implementation is frozen at commit
`5622df131dc71346d5890f42ce16fe1e3e55f33a`, before selection or disclosure of
any blind source. The committed preparation artifact contains only neutral synthetic
dry-run text. It records source-packet validation, complete intermediate audit output,
fail-closed behavior, source-identity invariance, a protected SPEC-038 renderer-seam
and browser regression, and the exact separately gated live-execution proposal.

No live/model/external calls were made. No real blind source set is present. The owner
verdict, source selection, execution authority, and promotion all remain pending.
