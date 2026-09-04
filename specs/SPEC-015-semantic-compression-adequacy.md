# SPEC-015 — Semantic Compression Adequacy

## Status

Ready for implementation.

## Phase

Phase II — realistic-source semantic reliability.

## Primary Question

> Can one blinded, independent, bounded semantic judge distinguish faithful binary relationships from lossy binary canonicalizations that omit, substitute, or collapse essential semantic roles, participants, events, states, or conditions?

## Why This Experiment Is Earned

SPEC-013 established assertion-first semantic compilation as the strongest realistic-source semantic baseline so far:

```text
source
  ↓
symbols
  ↓
grounded source assertions
  ↓
canonical normalization
  ↓
relationships / propositions / claims / abstention
```

SPEC-014 then showed that a single independent semantic admission gate can cheaply reject many bad canonical commitments while preserving good ones:

```text
3/3 positive controls admitted
5/6 negative controls rejected/demoted
1 false admit
0 false rejects
```

The sole false admit was not an obvious wrong predicate. It was a **plausible but lossy semantic compression**:

```text
Pauli exclusion principle
        ↓ CONSTRAINS
electron
```

where the source meaning concerns the allowed joint atomic quantum state / quantum-number assignment.

Historical review found the same family elsewhere:

- `quantity-demanded CAUSES shortage` loses the comparison condition involving supply;
- `order-command TRANSFERS_TO order-command-transfer` confuses transfer object/event/destination roles;
- `quantum-tunneling ENABLES electron` substitutes a participant for the penetration outcome;
- `quantum-tunneling ENABLES transistor` substitutes application context for the penetration outcome.

REVIEW-003 found that simple deterministic rules over participant membership, lexical occurrence, entity type, or participant-drop count are insufficient.

A frozen historical benchmark was therefore assembled **before** this judge exists.

## Frozen Benchmark

Use exactly:

```text
examples/evaluations/review-003-endpoint-role-benchmark-20260904/endpoint-role-packet.json
```

Frozen packet SHA-256:

```text
cbbef7b3eca555c4691024f987d6ba04be6cb6091d90d91d2121290782591088
```

The packet contains exactly:

```text
5 positive cases
5 negative cases
```

All cases have independently reviewed historical provenance.

Do not modify, relabel, regenerate, rebalance, or replace the packet after implementation begins.

## Benchmark Cases

### Negative controls

1. `quantity-demanded CAUSES shortage`
   - loses the essential comparison with quantity supplied;
   - accepted correction exists as SPEC-010 `COMPARISON_CONDITION`.

2. `pauli-exclusion-principle CONSTRAINS electron`
   - electron is a participant but not the precise constrained semantic object;
   - source concerns allowed joint atomic quantum states / quantum-number assignments.

3. `order-command TRANSFERS_TO order-command-transfer`
   - confuses transfer object/event/destination roles;
   - accepted correction exists as SPEC-010 `TRANSFER_EVENT`.

4. `quantum-tunneling ENABLES electron`
   - substitutes electron participant for electron penetration through a barrier.

5. `quantum-tunneling ENABLES transistor`
   - substitutes application/device context for the source-supported penetration process/outcome.

### Positive controls

1. `api-component PART_OF modular-order-processing-service`
2. `amino-acid TRANSFERS_TO ribosome`
3. `correspondence-principle CONSTRAINS quantum-mechanics`
4. `double-slit-experiment CAUSES interference-pattern`
5. `rna-polymerase BINDS_TO dna`

The positive controls span multiple predicates/families and include assertions with additional contextual participants, preventing trivial rejection based on participant compression alone.

## Experimental Hypothesis

A relationship is an adequate semantic compression when its binary canonical form preserves the source assertion strongly enough that the relationship remains true **as the source means it**, even though contextual details may be omitted.

A relationship is inadequate when binary canonicalization changes the proposition by:

```text
substituting a nearby participant for the semantic role-holder
omitting an essential participant or condition
collapsing an event/state/condition into an object
confusing object / event / destination / outcome roles
making a coarse statement that is plausible generally but not faithful to the grounded assertion
```

The judge must discriminate **faithful compression** from **lossy compression**.

## Important Distinction

The task is not:

> Is this statement scientifically plausible?

It is:

> Does this exact binary relationship faithfully preserve the grounded source assertion under the canonical predicate's source and target role contract?

This distinction is central to the Pauli case.

## Judge Boundary

Implement a provider-independent semantic-compression judge interface.

Conceptually:

```text
CompressionPacket
      ↓
SemanticCompressionJudge
      ↓
CompressionResult
```

The provider-specific OpenAI adapter must remain isolated.

The judge is experimental and must not automatically become part of production canonicalization/admission flow.

## Model-Facing Input

Construct a blinded model-facing packet from the frozen benchmark.

For each case, include only information necessary for the semantic decision, such as:

```text
opaque case ID
grounded source assertion
exact evidence excerpt
assertion participant symbols / descriptions
candidate relationship
candidate endpoint symbols / descriptions
canonical predicate contract
```

### Blinding

Do **not** expose to the live judge:

```text
POSITIVE / NEGATIVE labels
expected verdicts
historical defect descriptions
independent-review notes
SPEC numbers that reveal outcome
accepted corrections
fallback answers
provenance paths that reveal labels
case names such as "Pauli failure" or "positive control"
```

Use opaque deterministic case IDs.

The offline evaluator may retain labels separately.

Validate that the blinded packet contains no forbidden label/review leakage before any live call.

## Verdict Vocabulary

Use a small fixed vocabulary that distinguishes adequate binary compression from the main observed failure forms.

Required verdicts:

```text
BINARY_ADEQUATE
SOURCE_ROLE_INADEQUATE
TARGET_ROLE_INADEQUATE
MISSING_ESSENTIAL_PARTICIPANT
MISSING_IMPLICIT_PARTICIPANT
REQUIRES_STRUCTURED_PROPOSITION
INSUFFICIENT_FOR_BINARY_RELATIONSHIP
```

If implementation reveals that one label is structurally redundant, preserve the required set for the primary experiment rather than tuning it after inspecting output.

## Verdict Meaning

### `BINARY_ADEQUATE`

The candidate relationship's predicate and endpoints preserve the essential source assertion well enough to admit as a binary canonical relationship.

Context may be omitted, but the proposition must remain faithful.

### `SOURCE_ROLE_INADEQUATE`

The proposed source endpoint does not faithfully fill the predicate's source semantic role.

### `TARGET_ROLE_INADEQUATE`

The proposed target endpoint does not faithfully fill the predicate's target semantic role.

### `MISSING_ESSENTIAL_PARTICIPANT`

A source-explicit participant omitted from the binary relationship is essential to preserving the assertion's truth/meaning.

### `MISSING_IMPLICIT_PARTICIPANT`

The source assertion semantically depends on a state/event/condition/role-holder not represented as an available participant/symbol, making the binary projection misleading.

### `REQUIRES_STRUCTURED_PROPOSITION`

The assertion is representable using the project's existing structured proposition semantics but not faithfully as the proposed binary relationship.

Do not invent a new proposition type during this experiment.

### `INSUFFICIENT_FOR_BINARY_RELATIONSHIP`

The assertion should remain a claim/assertion rather than be admitted as the proposed binary relationship, but no more specific failure category is justified.

## No Rewriting

The judge must not:

- rewrite the relationship;
- propose replacement endpoints;
- mint symbols/entities;
- create a new predicate;
- create a new proposition type;
- rewrite source assertions;
- repair evidence;
- produce an alternative graph.

Output should contain only:

```text
case ID
verdict
brief rationale
```

Rationale is diagnostic only and must not be used to mutate the candidate in the primary experiment.

## Deterministic Validation

Trusted code must validate at least:

```text
packet SHA / identity
case count = 10
opaque ID uniqueness
blinding/no-label leakage
source evidence preservation
candidate equality to frozen historical candidate
predicate contract equality
symbol identity integrity
one verdict per case
no unknown case IDs
no missing case IDs
no duplicate decisions
verdict vocabulary membership
no rewrite fields in output
```

## Live Experiment

If technically feasible, run the entire 10-case blinded packet in **exactly one** `gpt-5.6-luna` call.

Use:

```text
store=False
SDK retries disabled
no hidden retry
no prompt repair
no enrichment
no second judge
no deliberation
no repair pass
```

No live call may occur before explicit owner approval under the current workflow.

If the packet cannot fit in one call for a genuine technical reason, stop and report rather than splitting it without approval.

## Evaluation

The offline evaluator compares live verdicts to frozen labels.

### Positive expectation

All five positive controls should receive:

```text
BINARY_ADEQUATE
```

Any other verdict is a false rejection.

### Negative expectation

All five negative controls should receive any non-`BINARY_ADEQUATE` verdict.

The exact diagnostic category is secondary but should be reported against the historical defect where useful.

A `BINARY_ADEQUATE` verdict on a negative case is a false admit.

## Metrics

Report at least:

```text
true adequate admits
false adequate admits
true inadequate rejects
false inadequate rejects
adequate-admission precision
adequate-admission recall
negative rejection rate
overall agreement
per-case verdicts
per-predicate results
per-family results where available
```

With only ten cases, do not report misleading statistical significance or production confidence intervals.

## Exploratory Interpretation

This benchmark is deliberately small.

Use qualitative interpretation:

### Strong positive signal

Approximately 9–10 / 10 correct with no systematic positive-control rejection, especially if the historical Pauli/transfer/comparison cases are correctly distinguished.

### Mixed signal

Approximately 7–8 / 10 or a coherent residual error family that reveals a new discriminator.

### Weak signal

Approximately 6 / 10 or below, blanket conservatism, or repeated confusion between adequate contextual compression and essential-role loss.

These are experimental interpretation guides, **not production thresholds**.

## Allowed Verdicts for SPEC-015

Final experiment verdict must be exactly one of:

```text
COMPRESSION_JUDGE_BETTER
MIXED
NO_MEANINGFUL_SIGNAL
INCONCLUSIVE
```

### `COMPRESSION_JUDGE_BETTER`

Use when the judge strongly discriminates faithful vs lossy binary compression on the frozen benchmark without relying on blanket rejection.

### `MIXED`

Use when discrimination is useful but meaningful errors remain or performance differs materially by failure type.

### `NO_MEANINGFUL_SIGNAL`

Use when the judge does not materially outperform trivial/simple discrimination on this packet.

### `INCONCLUSIVE`

Use only for provider/operational failure preventing fair evaluation.

## Comparison to SPEC-014

Do not claim a direct statistical improvement over SPEC-014 because the packet and task differ.

Instead ask:

> Does this narrower judge correctly catch the endpoint/role/compression cases that motivated it while preserving legitimate binary relationships?

Specifically record whether the SPEC-014 Pauli false admit is correctly rejected.

## Multi-Agent Decision Gate

Broad multi-agent deliberation remains deferred.

After SPEC-015:

- if the narrow judge performs strongly, continue preferring bounded independent gates;
- if it fails in a coherent way, inspect the residual mechanism before adding agents;
- if narrow independent judges repeatedly plateau on genuinely ambiguous semantics, only then reconsider multi-agent deliberation.

Do not implement or benchmark multi-agent systems in SPEC-015.

## Production Integration

Do not integrate this judge into the default Knowledge Compiler pipeline in SPEC-015.

This experiment tests discriminative capability only.

Production integration requires broader evidence than ten historical cases.

## Compatibility

Do not change:

```text
KnowledgeModel
20 canonical relationship predicates
SPEC-010 proposition vocabulary
grounding rules
assertion-first compiler
SPEC-014 gate behavior
structure detection
representation
navigation
```

No new runtime dependency should be necessary.

## Testing Strategy

All normal tests remain offline.

Add deterministic tests for:

```text
frozen packet SHA validation
blinded packet construction
forbidden label/review leakage detection
opaque ID stability
candidate/evidence/contract preservation
judge protocol validation
one-decision-per-case accounting
unknown/missing/duplicate case rejection
verdict vocabulary validation
fixture judge outputs
metric calculation
verdict calculation
failure preservation
```

Keep the full offline suite passing.

## Evaluation Artifacts

Create a directory such as:

```text
examples/evaluations/spec-015-semantic-compression-adequacy-<date>/
```

Likely artifacts:

```text
source-packet-reference.json
blinded-packet.json
judge-result.json
metrics.json
comparison.json
report.json
run-history.json
README.md
```

Do not duplicate historical source text unnecessarily.

## Explicit Non-Goals

Do not implement:

- candidate rewriting;
- automatic repair;
- new symbols/entities;
- new relationship predicates;
- new proposition types;
- ontology expansion;
- another assertion extraction pass;
- another canonicalization pass;
- multi-agent deliberation;
- multiple judges;
- consensus/voting;
- critique loops;
- child semantic zoom;
- representation redesign;
- map navigation;
- Journey/course generation;
- production gate integration;
- production threshold setting.

## Acceptance Criteria — Implementation

- [ ] Frozen packet SHA matches `cbbef7b3eca555c4691024f987d6ba04be6cb6091d90d91d2121290782591088`.
- [ ] Frozen packet remains byte-identical.
- [ ] Exactly 5 positive and 5 negative cases are validated offline.
- [ ] Model-facing packet is blinded.
- [ ] Opaque deterministic case IDs are used.
- [ ] No labels/review notes/provenance leaks reach the judge.
- [ ] Provider-independent judge boundary exists.
- [ ] Provider-specific adapter is isolated.
- [ ] Fixed verdict vocabulary is implemented exactly.
- [ ] Judge cannot rewrite candidates or create semantic objects.
- [ ] Deterministic output validation is fail-closed.
- [ ] Metrics/evaluator are deterministic.
- [ ] Existing canonical semantic architecture remains unchanged.
- [ ] No production integration occurs.
- [ ] Offline tests pass.
- [ ] Prior artifacts remain unchanged.

## Acceptance Criteria — Live Experiment

- [ ] Explicit owner approval obtained before transmission.
- [ ] Exactly one live call if technically feasible.
- [ ] `gpt-5.6-luna` used unless owner explicitly approves a different model.
- [ ] `store=False`.
- [ ] SDK retries disabled.
- [ ] No semantic/hidden retry.
- [ ] No prompt repair after output inspection.
- [ ] No enrichment.
- [ ] No second judge/agent.
- [ ] Complete provider metadata preserved where available.
- [ ] Every case receives exactly one validated verdict.

## Required Result Questions

The final report must answer:

1. Did the judge preserve all legitimate binary relationships?
2. Did it reject all known lossy binary compressions?
3. Did it catch the SPEC-014 Pauli false admit?
4. Which diagnostic verdicts were assigned to each negative case?
5. Did any positive control trigger `MISSING_ESSENTIAL_PARTICIPANT` merely because contextual participants were omitted?
6. Does the result support continued narrow-gate development over multi-agent deliberation?
7. What residual error class, if any, remains?
8. Is there enough evidence for production integration? Expected answer: no, unless evidence materially exceeds this SPEC's scope.

## Final Constraint

The purpose of SPEC-015 is not to make ten labels match by prompt engineering.

The packet was frozen before the judge existed specifically to prevent that.

The experiment asks one clean question:

> **Can a narrow independent semantic judge tell when a binary edge is a faithful compression of a grounded assertion and when it silently changes what the source means?**
