# SPEC-013 — Assertion-First Semantic Compilation

## Status

Ready for implementation.

## Phase

Phase II — realistic-source semantic reliability.

## Primary Question

> Does preserving source assertions in a neutral intermediate form before canonical relationship/proposition normalization materially improve semantic precision on the frozen quantum benchmark without weakening grounding, symbol integrity, or fail-closed behavior?

## Evidence That Earned This Experiment

SPEC-012 fixed the specific referential-integrity failure exposed by SPEC-011:

```text
frozen symbol table
→ zero dangling relationship endpoints
→ zero dangling proposition roles
→ zero unknown-symbol diagnostics
```

But semantic quality remained weak.

Independent review of the rejected staged Pass-2 proposal found:

```text
16 reviewed semantic items
6 supported
10 defective
37.5% reviewed proposal precision
```

The dominant defects were not random. REVIEW-002 identified a recurring mechanism:

```text
source assertion
      ↓
model must immediately choose a canonical graph predicate / endpoint pair
      ↓
meaning is strengthened, compressed, or distorted
```

Examples included:

- explanatory language becoming `CAUSES`;
- application language becoming `ENABLES`;
- explained phenomena becoming `EXAMPLE_OF`;
- process/state assertions compressed into nearby concrete entity endpoints.

The evidence therefore supports testing a new boundary:

> **Preserve what the source asserts before deciding how to compile that assertion into Knowledge Compiler semantics.**

## Experimental Control

Keep the accepted SPEC-012 Pass-1 symbol-discovery architecture constant.

Use the preserved SPEC-012 direct semantic-linking result as the control where fair.

Control:

```text
SOURCE
  ↓
SYMBOL TABLE
  ↓
DIRECT CANONICAL SEMANTIC LINKING
  ↓
relationships / claims / propositions
```

Experiment:

```text
SOURCE
  ↓
SAME SYMBOL TABLE CONCEPT
  ↓
SOURCE ASSERTIONS
  ↓
CANONICAL SEMANTIC NORMALIZATION
  ├── relationship
  ├── structured proposition
  ├── claim
  └── preserve as uncompiled assertion
  ↓
KnowledgeModel
```

The experiment is about the **assertion-preservation boundary**, not about adding a larger ontology.

## Frozen Benchmark

Use exactly the same realistic source as SPEC-011 and SPEC-012:

- Wikipedia — `Introduction to quantum mechanics`
- revision `1359567407`
- 5,965 words
- 39,735 characters
- existing recorded source hash/provenance

Do not shorten, segment, enrich, or substitute the source in the primary comparison.

## Keep Symbol Discovery Stable

Re-use the provider-independent staged symbol-discovery boundary from SPEC-012.

Do not redesign Pass 1 unless implementation compatibility requires a minimal non-semantic change.

The primary experimental variable begins **after the frozen symbol table exists**.

If a fresh live symbol-discovery call is required for the experimental run, it must use the same symbol-discovery prompt/version unless a schema-only compatibility change is unavoidable and documented.

Where fair, prefer reusing the existing frozen symbol-table artifact from SPEC-012 to avoid introducing symbol-table variance and unnecessary provider cost.

## New Boundary — SourceAssertion

Introduce the smallest provider-independent assertion representation sufficient to preserve source meaning before canonical graph compilation.

### Design constraint

Do not build a universal proposition language.

The source-assertion layer exists to delay commitment to canonical graph semantics, not to replace `KnowledgeModel` with another ontology.

### Minimum conceptual information

A source assertion should preserve enough information to answer:

```text
What does the source assert?
Which frozen symbols participate?
What source evidence supports it?
Is the assertion safely compilable into an existing canonical form?
```

Candidate minimum fields may include:

```text
assertion ID
normalized assertion text / proposition
participant symbol IDs
evidence quote / SourceSpan after trusted resolution
origin
optional non-canonical semantic hint
```

Codex may choose a slightly different minimum schema if it is simpler and better aligned with existing models, but must justify it.

### Explicitly avoid

Do not add:

- general first-order logic;
- nested expression trees;
- arbitrary predicate strings as a new canonical ontology;
- unrestricted event-role ontology;
- confidence taxonomies not required by current architecture;
- embeddings or semantic vectors;
- free-form world knowledge.

## Assertion Extraction

The assertion-extraction stage should answer approximately:

> **What source-supported statements are being made about the frozen symbols, before deciding which Knowledge Compiler relationship or proposition type they map to?**

### Requirements

- source-bounded;
- uses only frozen symbol IDs as participants where participants correspond to known symbols;
- cannot mint canonical entities;
- preserves exact evidence nomination for trusted quote resolution;
- does not require choosing one of the 20 canonical relationship predicates;
- does not require forcing every assertion into a binary relation;
- may preserve an assertion even when it cannot later be safely canonicalized.

### Neutrality

Avoid canonical labels such as `CAUSES`, `ENABLES`, `IS_A`, etc. inside the assertion representation unless used only as an explicitly non-binding hint.

The core assertion should survive even if the canonical semantic normalization rejects the hint.

## Assertion Grounding

Trusted code resolves nominated assertion evidence using the existing exact quote-to-SourceSpan mechanism.

Missing or ambiguous source evidence fails closed for that assertion according to the fixed contract.

Do not weaken grounding relative to SPEC-012.

The implementation must distinguish:

```text
assertion extraction failure
assertion grounding failure
canonicalization failure
```

rather than collapsing them into one generic error.

## Canonical Semantic Normalization

After grounded assertions exist, compile each assertion into one of the existing downstream semantic forms:

```text
BINARY_RELATIONSHIP
STRUCTURED_PROPOSITION
CLAIM
UNCOMPILED_ASSERTION
```

### Critical principle

> **Canonicalization may decline to compile.**

It is preferable to preserve a grounded source assertion as `UNCOMPILED_ASSERTION` than to force it into a misleading edge.

### Existing semantics remain authoritative

Do not change by default:

- the canonical 20 relationship predicates;
- SPEC-010 proposition types;
- proposition roles;
- comparison operators;
- SourceSpan rules;
- SOURCE/INFERRED rules;
- `KnowledgeModel` downstream contract.

If the current `KnowledgeModel` has no place for uncompiled assertions, keep them in the assertion-stage/evaluation artifact rather than expanding canonical IR merely for storage.

Only compiled canonical forms enter the ordinary `KnowledgeModel` unless the SPEC addendum explicitly permits a minimal compatible seam.

## Normalization Architecture

The canonical-normalization step may be implemented as:

- trusted deterministic rules where semantics are unambiguous;
- one bounded provider call over grounded assertions and frozen symbols;
- or a minimal hybrid.

Choose the smallest design that tests the hypothesis cleanly.

### Experimental preference

Prefer a design where the generating model first commits to the neutral assertion before being asked to choose canonical semantics.

Do not simply combine assertion extraction and canonical predicate selection into one response object, because that would reproduce the simultaneous-commitment problem being tested.

## Live Call Discipline

Keep the primary experiment small and explicit.

Likely live calls:

```text
Call A — assertion extraction
Call B — assertion → canonical semantic normalization
```

If reuse of the SPEC-012 frozen symbol table is accepted, no new symbol-discovery call is necessary.

If implementation requires a fresh symbol-discovery call, that makes three total experimental calls and requires explicit owner approval before transmission.

No hidden retries.

No semantic retries without explicit owner approval.

No prompt repair after seeing live output.

No external enrichment.

No child-resolution call.

Use `store=False` and disable SDK automatic retries where supported, consistent with current project practice.

## Precision-First Objective

Do not optimize for number of graph edges.

The expected desirable behavior may be:

```text
source assertions extracted: many
canonical relationships compiled: fewer
claims/propositions: some
uncompiled grounded assertions: some
semantic precision: materially higher
```

This is acceptable.

The system should become comfortable saying:

> **The source says something meaningful here, but the current canonical grammar cannot represent it safely as a graph edge.**

## Target Error Classes

SPEC-013 specifically tests whether assertion-first compilation reduces the defect classes identified in REVIEW-002:

```text
OVERSTATED_CAUSALITY
WRONG_PREDICATE
IMPRECISE_ENDPOINT
UNSUPPORTED_CANONICALIZATION
LOSSY_BINARY_FORM
```

Examples from the control include:

```text
quantum revolution → CAUSES → quantum mechanics
superfluidity → EXAMPLE_OF → quantum mechanics
quantum mechanics → ENABLES → laser / MRI / transistor / electron microscope
tunneling → ENABLES → transistor
Pauli exclusion principle → CONSTRAINS → electron
```

Do not hard-code fixes for those exact rows into the implementation prompt. They are regression evidence, not a training answer key.

## Evaluation Layers

Evaluate separately:

### 1. Assertion fidelity

Does the neutral assertion accurately preserve what the source says before canonicalization?

Classify assertions using a small review vocabulary such as:

```text
FAITHFUL
PARTIAL
DISTORTED
UNSUPPORTED
```

Fix the exact labels before live output is inspected.

### 2. Structural validity

Measure:

```text
unknown participant symbols
dangling compiled endpoints
dangling proposition roles
canonical model validation
```

### 3. Grounding validity

Measure:

```text
exact evidence resolution
unique evidence resolution
missing/ambiguous evidence
SOURCE/INFERRED integrity
```

### 4. Canonical semantic validity

Use the existing semantic review categories from SPEC-012 where possible:

```text
SUPPORTED
IMPRECISE_ENDPOINT
WRONG_PREDICATE
REVERSED_DIRECTION
OVERSTATED_CAUSALITY
UNSUPPORTED
LOSSY_BINARY_FORM
OTHER
```

### 5. Abstention quality

Inspect `UNCOMPILED_ASSERTION` cases.

A good abstention is a source-faithful assertion that would likely have become a misleading edge under direct canonicalization.

Do not count all abstentions as successes. Excessive abstention that removes obvious safe relationships is also a weakness.

## Primary Comparison

Compare the assertion-first experiment against the preserved SPEC-012 direct-linking proposal.

Report at least:

```text
control reviewed canonical precision
experiment reviewed canonical precision
number of canonical semantic items
number of grounded assertions
number/rate of uncompiled assertions
structural errors
grounding errors
known control defects fixed / retained / replaced
new experiment defects
```

The central question is not whether every source assertion becomes canonical.

It is whether the canonical semantics that do survive are materially more trustworthy.

## Verdict Set

Final experiment verdict must be one of:

```text
ASSERTION_FIRST_BETTER
NO_MEANINGFUL_IMPROVEMENT
ASSERTION_FIRST_WORSE
MIXED
INCONCLUSIVE
```

`ASSERTION_FIRST_BETTER` requires a meaningful semantic-precision improvement without weakening grounding or symbol integrity and without achieving precision solely by trivial near-total abstention.

## Downstream Gate

If and only if the assertion-first pipeline produces a trusted parent `KnowledgeModel`, existing downstream structure detection / representation / layout may run as diagnostics.

Do not perform child semantic zoom.

Do not redesign UI/navigation.

Do not use attractive rendering as semantic evidence.

## Explicit Non-Goals

Do not implement:

- new source selection;
- chunking/segmentation;
- multi-source compilation;
- retrieval/embeddings;
- new relationship predicates;
- broad proposition ontology expansion;
- recursive reasoning agents;
- automatic critique/repair loops;
- child semantic zoom;
- map navigation;
- Journey/course mode;
- simulator;
- learning-efficacy study;
- production API/UI.

## Testing

All normal tests remain offline.

Add deterministic fixture coverage for at least:

- SourceAssertion model/validation;
- participant-symbol validation;
- assertion evidence grounding;
- assertion-stage failure preservation;
- canonicalization into safe relationship;
- canonicalization into existing structured proposition;
- canonicalization into claim;
- canonicalization abstention / uncompiled assertion;
- no entity minting;
- existing `KnowledgeModel` downstream compatibility;
- evaluation comparison with SPEC-012 control;
- deterministic artifact generation.

Keep the complete offline suite passing.

## Artifacts

Create an evaluation directory such as:

```text
examples/evaluations/spec-013-assertion-first-semantic-compilation-<date>/
```

Likely artifacts:

```text
source-metadata.json
symbol-table.json
assertion-extraction-result.json
grounded-assertions.json
canonicalization-result.json
parent.knowledge.json               if trusted
parent.structures.json              if trusted
parent.representation.json          if trusted
assertion-review.json
canonical-semantic-review.json
control-comparison.json
report.json
run-history.json
README.md
```

Do not reproduce the full source unnecessarily.

## Acceptance Criteria — Core

- [ ] SPEC-012 symbol-discovery architecture is preserved.
- [ ] Provider-independent SourceAssertion boundary exists.
- [ ] Assertions can be grounded before canonical predicate commitment.
- [ ] Assertion participants are checked against frozen symbols.
- [ ] Assertion extraction cannot mint canonical entities.
- [ ] Canonical normalization is a separate stage from assertion extraction.
- [ ] Canonicalization may abstain safely.
- [ ] Existing 20 relationship predicates remain unchanged.
- [ ] Existing proposition vocabulary remains unchanged unless implementation is impossible without a minimal compatible change, in which case stop and report.
- [ ] Existing grounding rules remain unchanged.
- [ ] Existing canonical `KnowledgeModel` remains the downstream IR.
- [ ] No segmentation/retrieval architecture is introduced.
- [ ] No UI/navigation work is introduced.
- [ ] Offline tests pass.
- [ ] Prior evaluation artifacts remain unchanged.

See `SPEC-013-ADDENDUM-acceptance-and-handoff.md` for the remaining live, evaluation, verdict, and handoff requirements.
