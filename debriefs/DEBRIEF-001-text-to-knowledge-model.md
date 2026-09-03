# DEBRIEF-001 — Text to KnowledgeModel

## Paired Spec

[`specs/SPEC-001-text-to-knowledge-model.md`](../specs/SPEC-001-text-to-knowledge-model.md)

## Status

Completed and accepted.

Implementation commit: `06f1f5040fc87c3f59b16e115048c31efbfbaf98`

## What We Set Out to Learn

SPEC-001 was designed to answer one foundational product and architecture question:

> Can explanatory prose be transformed into a structured semantic intermediate representation whose entities and relationships preserve the system described by the source?

The goal was deliberately not to build a UI, visualization engine, persistence layer, or real LLM integration. The milestone was successful if the resulting `KnowledgeModel` was coherent enough that a human could inspect it and recover the important structure of the source without reconstructing that structure from prose.

Electromagnetism was used as the first golden test case.

## What Was Built

The implemented pipeline is:

```text
plain text
   ↓
SourceDocument normalization
   ↓
vendor-neutral KnowledgeExtractor
   ↓
validated ExtractionResult
   ↓
conservative entity deduplication
   ↓
validated KnowledgeModel
   ↓
formatted JSON / CLI
```

Core implementation boundaries:

- `models.py` — semantic IR and invariants
- `extractor.py` — vendor-neutral extractor protocol and deterministic fixture adapter
- `normalize.py` — source normalization
- `deduplicate.py` — conservative canonicalization and graph-reference rewriting
- `pipeline.py` — orchestration from source text to `KnowledgeModel`
- `cli.py` — offline `knowledge-compiler translate` command
- `tests/fixtures/` — deterministic electromagnetism source and extraction
- `examples/electromagnetism.knowledge.json` — human-inspectable golden output

The implementation reported 13 passing tests, successful wheel build, successful fresh-environment installation, and successful CLI generation of the golden JSON.

## Outcome

SPEC-001 passed its most important qualitative acceptance criterion.

The generated electromagnetism model makes the source structure visible as relationships approximately equivalent to:

```text
Charge
  ↓ CREATES
Electric field
  ↓ EXERTS_FORCE_ON
Charge

Moving charge
  ↓ CREATES
Magnetic field

Changing magnetic field
  ↓ INDUCES
Electric field

Changing electric field
  ↓ INDUCES
Magnetic field

Changing E + B
  ↓ ENABLE
Electromagnetic wave
  ↑ IS_A
Light
```

This validates the core architectural metaphor:

> `KnowledgeModel` can function as a compiler-like semantic intermediate representation between source material and future learning representations.

That is more important than the specific JSON schema. The project now has a stable conceptual boundary: downstream structure detectors, renderers, interactive explanations, and counterfactual tools should consume the semantic IR rather than raw source text or raw LLM prose.

## What Worked Well

### 1. Structure before presentation

Not building visualization first was the correct decision. It forced the project to prove that explanatory structure could survive transformation independently of how it is displayed.

### 2. Strong semantic invariants

The IR is not merely JSON-shaped model output. Validation includes:

- constrained entity and relationship vocabularies;
- confidence values in `[0, 1]`;
- unique entity, claim, and relationship IDs;
- relationship endpoints that must resolve to known entities;
- source spans constrained to document bounds;
- evidence quotes that must exactly match normalized source text;
- explicit distinction between `SOURCE` and `INFERRED` content.

This creates an important trust boundary for future real LLM extraction.

### 3. Vendor-neutral extraction boundary

`KnowledgeExtractor` is an interface rather than an SDK-specific dependency. This means SPEC-002 can introduce a real LLM without changing the downstream semantic pipeline.

This is the first meaningful proof that the compiler architecture is not just branding:

```text
SourceDocument
      ↓
Extractor
      ↓
semantic IR
      ↓
future passes / renderers
```

### 4. Conservative entity deduplication

Case variants and explicit aliases can merge, while related-but-distinct concepts remain separate. This is preferable to aggressive semantic merging at this stage because false merges destroy graph meaning.

The specific distinction between `electromagnetic field` and `electric field` is a useful benchmark for this principle.

### 5. Provenance was treated as part of the model

Source evidence was not postponed as an optional future feature. Relationships and claims retain evidence spans from the beginning.

This matters because the eventual product should behave as an interface over source material, not as an opaque AI replacement for it.

## Findings and Learnings

### Finding 1 — The semantic IR is the central product asset

The project originally began as a way to translate linear educational material into better representations. SPEC-001 sharpened that idea:

> The hard part is not drawing a map. The hard part is constructing a trustworthy semantic model from which many representations can be derived.

This shifts the project away from being an “AI mind-map generator” and toward a knowledge compiler.

### Finding 2 — Systems understanding lives heavily in edges

The electromagnetism fixture reinforces the original hypothesis that isolated concept definitions are insufficient. Relationships such as `CREATES`, `INDUCES`, `EXERTS_FORCE_ON`, and `IS_A` carry much of the explanatory value.

Future evaluation should therefore score relationship quality separately from entity extraction quality.

### Finding 3 — A deterministic fixture is necessary but not sufficient

SPEC-001 proves the contracts and pipeline, but not the product’s hardest empirical assumption.

Because the extractor is deterministic and fixture-backed, we still do not know whether a real LLM can reliably produce useful `KnowledgeModel` instances from previously unseen explanatory text.

That is now the dominant uncertainty.

### Finding 4 — `SOURCE` versus `INFERRED` is useful but may eventually need refinement

The current rule is deliberately strict:

```text
SOURCE   → must have direct evidence
INFERRED → must not present source evidence
```

This is excellent for the first trust boundary, but future real extraction may reveal a third epistemic situation:

> a relationship is not explicitly stated, but is reasonably inferred from several source passages.

Do not redesign this pre-emptively. SPEC-002 should generate evidence about whether the model needs concepts such as `supporting_evidence`, inference rationale, or multiple provenance classes.

### Finding 5 — False semantic merges are likely more damaging than duplicates

Deduplication should remain conservative until there is evidence that more aggressive entity resolution is needed. Two duplicate nodes are inconvenient; merging two distinct concepts can corrupt paths, causal structure, and later simulations.

### Finding 6 — Human inspectability is valuable during early architecture work

The formatted golden JSON proved useful as both a machine artifact and a human-reviewable model. Until the semantics stabilize, keeping outputs directly inspectable is more valuable than adding opaque infrastructure.

## Deviations From the Spec

No material functional deviations were identified.

The optional real LLM adapter was intentionally omitted. That was consistent with the spec and preserved determinism for SPEC-001.

## Engineering Follow-Up

One small issue was identified during post-implementation review:

The CLI describes the electromagnetism extraction fixture as a default bundled fixture, but the fallback path points to `tests/fixtures`. In a normal installed wheel, repository tests are not necessarily packaged, so invoking fixture mode without an explicit `--fixture` may fail outside a source checkout.

This does not invalidate SPEC-001 because the documented deterministic CLI path explicitly supplies the fixture. Fix when the CLI is next touched rather than expanding this completed milestone.

## Decisions Carried Forward

The following are now project decisions unless later evidence overturns them:

1. `KnowledgeModel` is the semantic intermediate representation of the system.
2. Downstream renderers and reasoning passes consume the IR, not raw source text.
3. Extraction remains behind a vendor-neutral interface.
4. Structured model output is validated before becoming application state.
5. Source provenance is part of the core data model.
6. Source-derived content and inference must remain distinguishable.
7. Entity resolution stays conservative by default.
8. Visualization is downstream of semantic extraction and structure detection.
9. Early outputs should remain human-inspectable.
10. New architecture should be justified by an observed problem rather than anticipated complexity.

## Unresolved Questions

These are deliberately left open for later specs:

- Can a real LLM reliably emit this IR from unseen text?
- How stable are extracted entities and edges across repeated runs?
- How should extraction quality be measured beyond schema validity?
- Does one relationship grammar generalize across scientific, technical, economic, biological, and historical material?
- How often does useful inference require evidence that is supportive but not explicit?
- Will the current entity types and relationship vocabulary remain sufficient once arbitrary text is introduced?
- How should conflicting or ambiguous claims be represented?
- When should ontology expansion occur versus falling back to a generic relationship?

## Implication for the Next Spec

The next risky assumption is no longer whether the pipeline works.

It is:

> Can an actual LLM translate previously unseen source text into a trustworthy and useful `KnowledgeModel` while preserving the architecture established in SPEC-001?

Therefore SPEC-002 should focus on **real semantic extraction**, not visualization.

Suggested experiment set:

```text
electromagnetism      → physical science
software architecture → technical systems
economics             → causal / behavioral systems
biology               → interacting natural systems
history               → temporal / causal narrative
```

The same semantic pipeline should remain unchanged. Only the extractor boundary should become real.

SPEC-002 should also introduce an explicit evaluation rubric so that “valid JSON” cannot be confused with “useful model.” Candidate dimensions include:

- entity precision / coverage;
- relationship precision / coverage;
- evidence correctness;
- source-vs-inference correctness;
- semantic duplication;
- unsupported claims;
- human usefulness;
- run-to-run stability.

## Final Assessment

**SPEC-001: accepted.**

The project now has a working semantic spine and a clearer product thesis than it had before implementation.

The most important learning is:

> Knowledge Compiler should be optimized around the quality of the semantic intermediate representation. Visual representations, progressive disclosure, and simulation are downstream capabilities built on that foundation.
