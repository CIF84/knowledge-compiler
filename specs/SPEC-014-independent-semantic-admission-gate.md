# SPEC-014 — Independent Semantic Admission Gate

## Status

Ready for implementation.

## Phase

Phase II — realistic-source semantic reliability.

## Primary Question

> Does a single independent semantic admission gate materially improve realistic-source canonical semantic reliability over assertion-first normalization alone, without excessive false rejection, weakened grounding, or disproportionate cost?

## Why This Experiment Now

SPEC-013 materially improved realistic-source semantic reliability by separating:

```text
WHAT DOES THE SOURCE ASSERT?
        ↓
grounded SourceAssertion
        ↓
WHAT CAN WE SAFELY CANONICALIZE?
```

The accepted quantum benchmark produced:

```text
24 grounded assertions
3 canonical relationships
21 claims
0 uncompiled assertions
```

All three admitted relationships were independently reviewed as supported and precise.

This is a strong result, but it does not establish that assertion-first normalization will remain perfectly conservative on future realistic sources.

The next cheapest credible reliability mechanism is therefore not broad multi-agent deliberation. It is a single independent discriminator positioned after candidate canonicalization.

The experimental question is intentionally narrow:

> Can an independent semantic gate detect unjustified canonical commitments while preserving justified ones?

## Control

Use the accepted SPEC-013 artifacts as the control.

Do **not** rerun assertion extraction or canonical normalization for the primary experiment unless a fair comparison is impossible without explicit owner approval.

Control artifacts include:

```text
frozen quantum source metadata
frozen 41-symbol table
24 grounded assertions
SPEC-013 canonicalization result
SPEC-013 canonical semantic review
```

The control canonical result is:

```text
3 relationships
0 propositions
21 claims
```

with reviewed relationship precision:

```text
3 / 3 supported = 100%
```

Because the control is already precise on admitted graph edges, SPEC-014 must test more than simple preservation of those three edges. It should also test whether the gate can correctly classify deliberately preserved negative/control candidates drawn from known SPEC-012 semantic failures.

## Experimental Design

The gate receives one candidate canonical commitment at a time together with only the information needed to judge admission.

Candidate flow:

```text
GROUNDED ASSERTION
      ↓
CANDIDATE CANONICAL FORM
      ↓
INDEPENDENT SEMANTIC GATE
      ├── ADMIT
      └── REJECT / DEMOTE
```

The gate is **not** allowed to rewrite the candidate during the primary experiment.

It judges admission only.

## Gate Inputs

For each candidate, provide:

- grounded assertion statement;
- exact source evidence for that assertion;
- participant symbols referenced by the assertion;
- proposed canonical form;
- canonical predicate/proposition contract relevant to the candidate;
- origin/provenance metadata needed for trust checks.

Do not provide unrelated source material if the grounded assertion and evidence are sufficient.

This keeps the gate local and cheap.

If the experiment demonstrates that broader context is required for fair judgment, preserve that as a limitation rather than silently widening context after seeing results.

## Gate Output

Use a small fixed verdict vocabulary chosen before live evaluation.

Recommended minimum:

```text
ADMIT
TOO_STRONG
WRONG_PREDICATE
WRONG_ENDPOINT
REQUIRES_STRUCTURED_PROPOSITION
INSUFFICIENT_FOR_CANONICALIZATION
```

The implementation may refine labels before live evaluation, but the final set must be frozen before observing live gate outputs.

Each gate decision should include a brief structured rationale tied to the candidate and semantic contract.

The gate must not:

- invent a replacement edge;
- create entities;
- create evidence;
- change the grounded assertion;
- expand the relationship vocabulary;
- expand the proposition vocabulary;
- perform general tutoring or explanation.

## Candidate Packet Set

Evaluate the gate against a fixed packet containing both positive and negative cases.

### Positive packet

Include all accepted SPEC-013 canonical relationships.

Expected behavior:

```text
ADMIT
```

for each relationship that independent review already judged supported and precise.

### Negative packet

Include a bounded set of known bad canonical candidates from the preserved SPEC-012 rejected proposal and semantic review.

Prefer defects already classified independently, including examples of:

```text
OVERSTATED_CAUSALITY
WRONG_PREDICATE
IMPRECISE_ENDPOINT
UNSUPPORTED
```

The negative packet should include representative examples such as:

- explanation/development language overstated as causality;
- application language overstated as `ENABLES`;
- superfluidity misclassified as `EXAMPLE_OF` quantum mechanics;
- tunneling endpoint substitution;
- Pauli endpoint compression;
- unsupported or mismatched QED/QFT classification.

Use preserved source assertion/evidence and candidate semantics. Do not alter them to make the gate's task easier.

## Packet Freezing

Build the evaluation packet entirely offline before any live gate call.

Record:

```text
packet ID
candidate ID
source assertion/evidence
candidate canonical form
independent expected category
positive/negative label
```

Freeze and commit packet metadata/hashes before live evaluation if consistent with the repository workflow.

The gate must not participate in creating its own benchmark labels.

## Primary Metric

The core question is semantic admission discrimination.

Report at least:

```text
true admits
false admits
true rejects/demotions
false rejects
precision of ADMIT decisions
recall of justified admissions
negative-case rejection rate
```

Because the control graph is already conservative, **false rejection matters**.

A gate that rejects every candidate is not successful.

## Success Principle

The gate should:

```text
retain justified canonical commitments
        +
reject/demote known unjustified commitments
```

without becoming a universal abstention machine.

## Verdict Set

Final verdict must be exactly one of:

```text
GATE_BETTER
NO_MEANINGFUL_IMPROVEMENT
GATE_TOO_CONSERVATIVE
GATE_UNRELIABLE
INCONCLUSIVE
```

### GATE_BETTER

Appropriate when the gate retains most/all positive controls while rejecting most known negative candidates at acceptable cost.

### NO_MEANINGFUL_IMPROVEMENT

Appropriate when discrimination is not materially better than the existing normalizer's behavior or the added call yields little new protection.

### GATE_TOO_CONSERVATIVE

Appropriate when negative candidates are rejected but too many independently supported SPEC-013 relationships are also rejected.

### GATE_UNRELIABLE

Appropriate when gate decisions are inconsistent with independent semantic review in both directions.

### INCONCLUSIVE

Use only for provider/operational failure preventing a fair test.

## Experimental Independence

The gate must be independent from the generation decision it reviews.

At minimum:

- use a separate provider call/session from candidate generation;
- do not expose the normalizer's hidden reasoning;
- do not ask the normalizer to self-grade;
- do not let the gate rewrite candidates and then judge its own rewrite.

Using the same model family is acceptable for this experiment because the mechanism under test is independent decision context, not model diversity.

Do not introduce multiple agents/models yet.

## Live Call Design

Prefer the cheapest credible live design.

If the entire fixed packet fits comfortably in one structured-output gate call, use **one** live gate call for the primary experiment.

If implementation constraints require packet batching, use the minimum number of deterministic batches and justify them before execution.

Do not create one live call per candidate unless strictly necessary.

No hidden retries.

No prompt repair after seeing results.

No second-stage deliberation.

No critic/rewrite loop.

## Deterministic Baseline Checks

Before live evaluation, implement cheap deterministic checks for only obvious contract violations already expressible from canonical schemas/contracts.

Examples may include:

- unknown symbol IDs;
- invalid proposition role bindings;
- source/target type violations that are already explicit hard invariants;
- SOURCE/INFERRED evidence violations.

Do **not** encode broad semantic heuristics such as:

```text
CAUSES requires certain words
ENABLES requires certain phrases
```

unless those are already canonical hard contracts.

The purpose is to keep deterministic validation distinct from semantic judgment.

## Comparison to Multi-Agent Deliberation

SPEC-014 is explicitly a discriminator before broader multi-agent architecture.

Record whether the gate's result suggests escalation.

Possible outcomes:

```text
simple gate works well
→ do not add multi-agent deliberation

simple gate catches errors but has difficult borderline disagreements
→ multi-role deliberation may become justified

simple gate adds little value
→ reconsider root cause before adding more agents
```

Do not implement multi-agent deliberation inside SPEC-014.

## Canonical Integration Boundary

Primary experiment should evaluate the gate offline/on preserved candidate packets first.

Do not automatically insert it into production canonicalization until the experiment verdict supports doing so.

If `GATE_BETTER`, implementation may include a clearly isolated integration seam demonstrating how:

```text
candidate canonicalization
      ↓
gate verdict
      ↓
ADMIT → KnowledgeModel
REJECT → claim/uncompiled preservation path
```

would work, but do not rerun the full quantum extraction pipeline unless separately authorized.

## Grounding and Truth Preservation

The gate must never weaken grounding.

It may use only evidence already attached to grounded assertions.

If a canonical candidate is rejected, source meaning must remain preserved through its existing lower-commitment representation where available:

```text
claim
or
uncompiled assertion
```

Do not delete source meaning merely because a graph edge is rejected.

## Cost Accounting

Report:

```text
packet size
prompt/input tokens
output tokens
total tokens
runtime
request ID
number of gate calls
authoritative monetary cost if available
```

Compare the added cost with SPEC-013's two-call compilation cost.

The mechanism should be judged partly on information/reliability gained per added call/token.

## Testing Strategy

All normal tests remain offline.

Add deterministic tests for:

- gate packet schema;
- frozen packet serialization/order;
- verdict vocabulary validation;
- positive/negative label integrity;
- mapping gate verdicts to admit/demote decisions;
- no candidate rewrite;
- no new evidence generation;
- no entity minting;
- aggregation metrics;
- verdict selection logic;
- preservation of claims/assertions after rejection;
- prior SPEC-013 artifacts unchanged.

Keep the complete offline suite passing.

## Evaluation Artifacts

Create a directory such as:

```text
examples/evaluations/spec-014-independent-semantic-gate-<date>/
```

Likely artifacts:

```text
gate-packet.json
gate-result.json
metrics.json
comparison.json
report.json
run-history.json
README.md
```

Preserve the exact frozen packet used for the live call.

## Explicit Non-Goals

Do not implement:

- new source extraction;
- symbol discovery;
- assertion extraction rerun;
- canonical normalization rerun;
- source segmentation;
- relationship-vocabulary expansion;
- proposition-vocabulary expansion;
- multi-agent deliberation;
- debate protocols;
- critic/rewrite loops;
- model ensembles;
- external retrieval;
- map-navigation changes;
- assertion-aware representation redesign;
- semantic zoom;
- Journey/course mode;
- learning evaluation.

## Acceptance Criteria — Implementation

- [ ] Provider-independent semantic gate boundary exists.
- [ ] Gate input is restricted to grounded assertion/evidence, participants, candidate semantics, and canonical contract.
- [ ] Gate verdict vocabulary is fixed before live output.
- [ ] Gate cannot rewrite candidates.
- [ ] Gate cannot mint entities or evidence.
- [ ] Positive packet includes all accepted SPEC-013 canonical relationships.
- [ ] Negative packet uses preserved independently reviewed SPEC-012 failures.
- [ ] Packet labels are created independently from gate execution.
- [ ] Packet ordering/serialization is deterministic.
- [ ] Existing KnowledgeModel semantics remain unchanged.
- [ ] Existing 20 predicates remain unchanged.
- [ ] Existing proposition vocabulary remains unchanged.
- [ ] Existing grounding rules remain unchanged.
- [ ] Full offline tests pass.
- [ ] Prior benchmark artifacts remain unchanged.
