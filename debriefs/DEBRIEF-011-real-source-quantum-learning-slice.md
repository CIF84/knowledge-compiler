# DEBRIEF-011 — Real-Source Quantum Learning Slice

## Status

Accepted negative result.

SPEC-011 did not produce a learner-facing artifact. It did successfully identify the first concrete failure boundary encountered when the accumulated Knowledge Compiler architecture was exposed to substantially richer real-world source material.

## Source

Benchmark:

- Wikipedia — `Introduction to quantum mechanics`
- fixed revision: `1359567407`
- revision date: `2026-06-16`
- scale: 5,965 words / 39,735 characters
- license: CC BY-SA 4.0
- full source not committed
- source metadata and revision provenance preserved

The source was deliberately processed as one full document. No segmentation or external semantic enrichment was used.

## Primary Question

> Can Knowledge Compiler transform one realistic, substantially richer plain-text source about introductory quantum mechanics into a trustworthy, useful overview with at least one automatically generated deeper semantic resolution that the owner would genuinely prefer to learn from over the original source alone?

## Outcome

**No — under the current one-pass extraction architecture.**

No valid parent `KnowledgeModel` was produced, so structure detection, representation, semantic zoom, navigation, and human learning review were correctly not attempted.

This is a high-information failure rather than an inconclusive experiment.

## Live Attempts

Provider/model:

```text
OpenAI Responses API
gpt-5.6-luna
store=False
SDK retries disabled
```

Parent extraction prompt remained `spec-010-v1`.

### Attempt 1

Runtime: 23.695 seconds.

Failed closed because relationship:

```text
measurement-collapses-wave-function
```

referenced undefined entity:

```text
measurement
```

The original harness exited before rejected-response capture was added, so request ID and token usage are unavailable. This limitation is preserved rather than reconstructed.

### Attempt 2 — explicit owner-authorized semantic retry

The source, prompt, model, validation, and enrichment policy were unchanged.

Runtime: 20.798 seconds.

Request:

```text
resp_03e8e3188410c6cf016a99f49ebcc487d2b0627039c1a06684
```

Usage:

```text
input   11,006
output   2,788
total   13,794
```

Rejected proposal:

```text
27 entities
11 relationships
9 claims
0 propositions
```

All 20 semantic items carrying source evidence had exact, uniquely occurring source spans.

Deduplication retained 27 → 27 entities with zero merges and zero endpoint rewrites.

The proposal nevertheless failed because:

```text
rel-quantum-is-study
```

referenced undefined entity:

```text
quantum-theory
```

No third extraction call was authorized or made.

Because the second extraction failed, the conditionally authorized child-resolution call was correctly not made.

## Critical Finding 1 — Referential Integrity Fails at Realistic Scale

Two independent full-source generations produced relationships whose endpoints were absent from the generated entity inventory.

```text
Attempt 1
relationship → measurement
               ↑
          entity absent

Attempt 2
relationship → quantum-theory
               ↑
          entity absent
```

This was not observed as a persistent blocker on the small benchmark fixtures.

The current extraction task asks one probabilistic generation to simultaneously:

```text
read realistic source
        +
discover concepts
        +
normalize identities
        +
assign entity types
        +
select canonical predicates
        +
select endpoints
        +
construct claims
        +
construct propositions
        +
nominate evidence
        +
maintain global referential consistency
```

SPEC-011 provides concrete evidence that this one-pass contract is not reliable enough at the tested source scale.

## Critical Finding 2 — Grounding Correctness Still Does Not Guarantee Semantic Correctness

The preserved second proposal had perfect mechanical evidence resolution for its accepted source-evidence items, yet independent repository review found materially misleading semantic relationships.

Examples included interpretations equivalent to:

```text
quantum mechanics ─CAUSES→ molecules

energy quanta ─CAUSES→ black-body radiation

wave-function collapse → wave-function collapse
```

Other issues included unsupported or mismatched `IS_A` edges around QFT/QED and a tunneling relationship targeting an electron rather than electron penetration.

Therefore SPEC-011 independently reinforces the earlier result:

```text
GROUNDING CORRECTNESS
        ≠
PROPOSITION / RELATIONSHIP CORRECTNESS
```

Fixing dangling endpoints alone would not make the realistic-source model trustworthy.

## Critical Finding 3 — The Trust Architecture Worked

The system did not render either invalid proposal.

```text
realistic source
      ↓
plausible semantic proposal
      ↓
trusted validation
      ↓
invalid symbol reference detected
      ↓
FAIL CLOSED
```

This prevented a visually authoritative but semantically invalid quantum-learning map from reaching the learner.

The vertical slice failed, but the trust boundary passed.

## Proposition Boundary Finding

The quantum source exposed semantic forms that the current proposition layer may eventually need to address, including uncertainty tradeoffs and entanglement correlations.

These were safely retained as claims rather than forced into misleading binary edges or used to justify speculative ontology expansion.

SPEC-011 does **not** authorize new proposition types from this evidence alone.

## Failure Attribution

Primary:

```text
EXTRACTION / SOURCE_SCALE
```

Specifically, global entity inventory and relationship endpoint consistency under realistic source complexity.

Secondary:

```text
SEMANTIC_RELATIONSHIP
```

Specifically, endpoint attribution and predicate interpretation despite exact source grounding.

Not meaningfully tested because no trusted parent existed:

```text
STRUCTURE_DETECTION
OVERVIEW / SALIENCE
REPRESENTATION
LAYOUT
SEMANTIC_RESOLUTION
NAVIGATION
HUMAN_USEFULNESS
```

Do not attribute failure to those downstream layers.

## Architectural Hypothesis Earned by the Failure

SPEC-011 suggests that the LLM should be treated less as **the extractor** and more as a **probabilistic semantic proposal stage inside a trusted compiler**.

A plausible next architecture is staged semantic compilation:

```text
SOURCE
  ↓
PASS 1 — SYMBOL DISCOVERY
  ↓
canonical entity inventory / symbol table
  ↓
freeze symbol identities
  ↓
PASS 2 — SEMANTIC LINKING
  ↓
relationships / claims / propositions
restricted to known symbols
  ↓
trusted validation
  ↓
KnowledgeModel
```

This resembles conventional compiler separation between symbol discovery and semantic linking.

However, this remains a **hypothesis**, not an accepted architecture.

The next experiment should compare it against the current one-pass control on the exact same frozen quantum benchmark.

## Why Not Retry Again?

A third one-pass call might eventually produce a schema-valid model by chance.

That would provide less information than the two independent failures already observed.

The project is not optimizing for obtaining a successful screenshot. It is optimizing for reducing uncertainty about trustworthy compilation.

Therefore no further one-pass retry is justified before testing the architectural hypothesis.

## Recommended Next Experiment

Working title:

```text
SPEC-012 — Staged Semantic Compilation
```

Primary question:

> Does separating canonical entity/symbol discovery from semantic linking materially improve referential integrity and semantic relationship precision on the same frozen realistic quantum source that repeatedly broke one-pass extraction?

### Experimental comparison

Hold constant:

```text
same fixed source revision
same source text
same provider/model
same canonical relationship vocabulary
same proposition vocabulary
same evidence rules
same validation
no external enrichment
```

Compare:

```text
CONTROL
current one-pass extraction

vs

EXPERIMENT
two-pass symbol-table-first extraction
```

Do not introduce a third pass unless evidence from the two-pass experiment requires it.

## Evaluation Layers for SPEC-012

Success must not mean only `KnowledgeModel` validation.

Evaluate separately:

### 1. Structural validity

```text
dangling endpoints
duplicate identities
schema violations
symbol-table violations
```

### 2. Grounding validity

```text
exact evidence
unique evidence spans
SOURCE / INFERRED integrity
```

### 3. Semantic validity

```text
does the source actually support
this predicate
between these exact semantic endpoints?
```

Precision should dominate graph volume.

A smaller trustworthy model is preferable to a larger questionable model.

## Phase-II Implication

The Phase-II thesis remains valid:

> **Prove that the primitive survives contact with realistic knowledge.**

SPEC-011 showed that it currently does not survive the extraction boundary reliably enough.

This is exactly the kind of result Phase II was designed to expose.

Do not move to active map navigation, Journey, recursive zoom, or learning-efficacy testing until the realistic-source semantic terrain is trustworthy enough to reach those layers.

## Product Vision Impact

The broader interaction vision remains unchanged:

```text
                  COMPILED KNOWLEDGE SPACE
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
              EXPLORE             JOURNEY
        learner chooses route   system proposes route
```

But SPEC-011 reinforces the dependency:

> **Before routing through the map, prove that the map is semantically trustworthy.**

## Decisions

1. Accept SPEC-011 as a valid negative result.
2. Record real-source vertical slice as FAIL under current one-pass extraction.
3. Record fail-closed trust architecture as PASS.
4. Do not retry one-pass extraction merely to obtain a valid output.
5. Do not work on map-navigation UX next.
6. Do not expand proposition ontology from isolated quantum examples.
7. Preserve the fixed quantum source revision as the benchmark for the next experiment.
8. Test staged/symbol-table-first semantic compilation against the one-pass control.
9. Evaluate semantic precision independently from grounding and schema validity.
10. Continue Phase II through failure-driven architecture rather than feature accumulation.

## Repository Evidence

Implementation commit:

```text
9c9b775
```

Final diagnostic correction:

```text
755c0c17446b144c0188792f09471183ba9db97f
```

Offline suite after SPEC-011:

```text
149 passed
```

No `DEBRIEF-011` was created by Codex; this document closes the experiment after independent review.

## Final Conclusion

SPEC-011 failed to produce a quantum-learning artifact, but succeeded at its deeper purpose: realistic knowledge found the first architecture boundary that the small benchmark suite had hidden.

The current one-pass semantic extraction contract can produce perfectly grounded evidence while simultaneously losing global symbol consistency and semantic endpoint truth.

The next step is therefore not more UI and not more retries.

It is to test whether **staged semantic compilation** can turn probabilistic semantic proposals into a more reliable trusted knowledge model.
