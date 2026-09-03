# DEBRIEF-002 — LLM Semantic Extraction

## Status

Accepted with mixed semantic outcome.

## Implementation Commit

`52a4fc0b2e16b5c0841904d7f312d38ebc4aff9d`

Pushed to canonical `origin/main`.

## Question Tested

> Can a real LLM reliably transform previously unseen explanatory text into the existing validated `KnowledgeModel` across deliberately different domains without changing downstream architecture?

## Outcome

**Partially yes.**

A real OpenAI extractor was introduced behind the existing `KnowledgeExtractor` boundary without changing the downstream semantic pipeline. The same `KnowledgeModel` IR produced recognizable, grounded system structure across physics, software architecture, economics, biology, and history.

However, the live five-domain evaluation was **MIXED**. Schema validity and source grounding were strong, but relationship precision and vocabulary fit degraded materially in some domains. A valid graph is therefore not equivalent to a semantically correct or pedagogically useful graph.

The important product finding is:

> The current architecture survives real LLM extraction, but the current semantic grammar is not yet sufficiently expressive or constrained to treat successful validation as semantic success.

## What Was Implemented

The implemented path is:

```text
SourceDocument
  → KnowledgeExtractor
    → FixtureExtractor | OpenAILLMExtractor
  → ExtractionResult validation
  → conservative deduplication
  → KnowledgeModel
  → JSON / CLI
```

New implementation includes:

- OpenAI Responses API adapter in `openai_extractor.py`
- strict structured-output schema
- exact quote extraction with deterministic quote-to-offset resolution
- explicit rejection of missing or ambiguous evidence
- provider/model/prompt/usage metadata
- live evaluation harness across five repository-owned fixtures
- load-bearing expectations per domain
- CLI support for real LLM translation/evaluation
- optional OpenAI dependency
- `.env` ignore rules
- provider/evidence/CLI/evaluation tests
- committed live evaluation artifacts and human review

The existing fixture path remains available offline.

## Verification

Reported automated result:

```text
25 passed in 0.05s
```

Independent repository review confirmed that:

- the implementation commit exists as one commit after SPEC-002;
- provider-specific logic is isolated in the adapter;
- `KnowledgeModel` and pipeline remain provider-neutral;
- evidence quotes are resolved deterministically before entering the domain model;
- ambiguous or absent quotes fail rather than weakening source-span invariants;
- the live evaluation artifacts and human review are committed;
- five domain fixtures and dedicated provider/evaluation tests are present.

The review environment did not independently rerun the local test suite or live API calls; those execution results remain Codex-reported evidence.

## Five-Domain Evaluation

| Domain | Entities | Claims | Relationships | Outcome |
| --- | ---: | ---: | ---: | --- |
| Electromagnetism | 9 | 2 | 8 | Good mechanisms; some state distinctions collapsed |
| Software architecture | 17 | 5 | 16 | Useful dependency model; some reversed/imprecise edges |
| Economics | 14 | 3 | 16 | Good causal coverage; vocabulary-driven distortions |
| Biology | 16 | 3 | 14 | Good process coverage; poor vocabulary fit in places |
| History | 20 | 3 | 17 | Grounded but materially weaker relationship precision |

Overall assessment: **MIXED**.

## Strong Findings

### 1. The extractor boundary held

The provider could be added without redesigning the semantic core.

This strengthens the architectural decision that `KnowledgeModel` is the semantic IR and `KnowledgeExtractor` is the provider boundary.

### 2. Exact source grounding is practical

The successful strategy was not to trust the LLM with character offsets.

Instead:

```text
LLM returns exact quote
        ↓
deterministic source lookup
        ↓
validated SourceSpan coordinates
```

This preserves strong evidence invariants while keeping probabilistic behavior outside the trusted domain state.

### 3. Validation caught real failures

The software-architecture fixture failed twice before succeeding:

1. an `INFERRED` relationship incorrectly carried source evidence;
2. a short evidence quote was ambiguous;
3. a prompt-only revision requiring unique clauses/sentences and provenance self-check succeeded.

No validation invariant was relaxed and no output-repair heuristic was introduced.

This is positive evidence for typed, fail-closed boundaries around probabilistic extraction.

### 4. One IR can represent multiple domains

All five domains produced recognizable semantic models under the same core data structure. This is meaningful evidence that the project is not merely an electromagnetism-specific prompt.

### 5. Schema correctness is not semantic correctness

The largest discovery of SPEC-002 is that structurally valid output can still contain semantically poor edges.

Examples included:

- reversed `PART_OF` direction;
- `EXERTS_FORCE_ON` used for economic contribution and biological binding;
- `ENABLES` used to represent delivery;
- `INCREASES` reversing a historical statement about slowness;
- `TRANSFORMS_INTO` used for an invalid actor/event relationship;
- important temporal relationships represented only as claims rather than `PRECEDES` edges.

Future evaluation must therefore treat semantic relationship quality as a first-class product concern.

## Relationship Vocabulary Findings

The initial grammar is not sufficiently expressive across all five domains.

Observed gaps include:

- binding / attachment;
- transport / delivery;
- prohibition such as `MUST_NOT_CALL`;
- generic directional influence that is not physical force;
- unchanged-property / explicit absence-of-causation statements;
- actor/event relationships common in historical narratives.

Do not respond by indiscriminately adding edge types. The next design step should determine a principled relationship grammar and clarify edge semantics/directionality.

## Entity / State Modeling Finding

Electromagnetism exposed another important issue: changing electric and magnetic fields were collapsed into the base field entities.

This suggests the IR may eventually need a clearer distinction among:

```text
entity
state / condition
process / transition
```

Do not redesign this yet without a focused experiment. Record it as a semantic-model question.

## SOURCE vs INFERRED Finding

The strict rule remains useful. A live failure showed that the model can incorrectly attach source evidence to inferred relationships, and validation caught it.

The previously suspected need for `supporting_evidence` on inferred items was not required to complete this experiment. Keep the current contract for now; revisit only with a concrete use case.

## Prompt Finding

Prompting materially affected evidence reliability. A small targeted change from `spec-002-v1` to `spec-002-v2` solved both provenance and ambiguous-evidence failures for the software fixture without changing domain invariants.

This supports the operating principle:

> Improve probabilistic behavior at the adapter/prompt boundary before weakening trusted semantic contracts.

## Deviations From SPEC

- Fixture extraction now requires explicit `--fixture`; this intentionally fixes the repository-relative default path problem discovered after SPEC-001.
- Human review is stored separately in `review.json`, while machine-run `report.json` remains unchanged.
- Four successful domain artifacts were produced with prompt v1; software architecture succeeded on v2 after two rejected attempts.
- No relationship types were added despite observed gaps.
- `DEBRIEF-002` was correctly deferred until independent review.

These deviations are acceptable and consistent with the experiment's intent.

## Cost / Efficiency

Recorded successful calls used:

```text
input:   3,600 tokens
output:  9,185 tokens
total:  12,785 tokens
```

Recorded estimated successful-call cost was approximately `$0.0117`; actual experiment cost was somewhat higher because rejected-call usage was unavailable.

The key operational point is that multi-domain semantic experiments are cheap enough to repeat frequently. This materially lowers the cost of product discovery.

## Security Finding

The API key used for evaluation appeared in internal terminal-state output during environment handoff.

The key should be treated as exposed and rotated. No key pattern was reported in committed repository files and `.env` files are now ignored.

Future operating practice should avoid placing secrets into visible handoff output and should treat secret rotation as mandatory whenever accidental exposure is suspected.

## Operating Model Findings

SPEC-002 provides a second positive data point for the repository-centered workflow.

What worked:

- the repository memory/control documents were sufficient to express the implementation context in a very short Codex prompt;
- one primary uncertainty kept scope bounded;
- explicit non-goals prevented UI, persistence, multi-provider, and ontology expansion;
- requiring a push before handoff eliminated the SPEC-001 local-vs-remote review blocker;
- the required handoff contained enough structured evidence for independent review;
- separating machine evaluation output from human review preserved experimental evidence cleanly;
- explicit acceptance of negative findings prevented semantic failures being hidden behind repair heuristics.

New process improvement:

- secrets must never be echoed into implementation handoffs or terminal-state artifacts; rotate immediately if exposure occurs.

The documentation/control layer did not show evidence of excessive overhead in this increment. It materially reduced context-reconstruction and review ambiguity.

## Canonical Model Changes

This increment changes our understanding of:

```text
[x] Product / project memory
[x] Architecture
[x] Operating process
[x] Project health / risk
```

## Decisions Carried Forward

### Decision: Keep `KnowledgeModel` as the semantic IR

**Origin:** DEBRIEF-001  
**Strengthened by:** DEBRIEF-002  
**Status:** active

A real provider integrated without forcing downstream redesign.

### Decision: Keep provider concerns behind `KnowledgeExtractor`

**Origin:** DEBRIEF-001  
**Strengthened by:** DEBRIEF-002  
**Status:** active

### Decision: Resolve evidence coordinates deterministically

**Origin:** DEBRIEF-002  
**Status:** active

LLMs may nominate exact source quotes; trusted code resolves and validates coordinates.

### Decision: Semantic quality must be evaluated separately from schema validity

**Origin:** DEBRIEF-002  
**Status:** active

Future experiments need explicit semantic checks or human review around relationship meaning, direction, coverage, and vocabulary fit.

### Decision: Do not expand relationship vocabulary opportunistically

**Origin:** DEBRIEF-002  
**Status:** active

Vocabulary evolution should be principled and evidence-driven across domains.

## Unresolved Questions

- What is the smallest relationship grammar that is expressive across domains without becoming an uncontrolled ontology?
- Should relationship types have explicit semantic contracts including directionality and valid entity-role patterns?
- Can extraction quality improve materially if the model selects from richer relationship definitions/examples rather than enum labels alone?
- Should entity, state, and process be represented more distinctly?
- How should claims and relationships interact when the same proposition could be represented either way?
- How should temporal/event structure be modeled for history without degrading mechanistic domains?
- Can semantic quality be evaluated automatically enough to reduce manual review while remaining trustworthy?

## Recommended Next Experiment

Do **not** move to visualization yet.

The next highest-value uncertainty is no longer whether real LLM extraction works. It is:

> Can we define and enforce a better semantic relationship grammar so that valid edges preserve meaning and direction across domains rather than forcing concepts into the nearest available label?

A focused SPEC-003 should therefore target **relationship semantics / ontology refinement and semantic validation**, using the five-domain corpus and the concrete failures from this debrief as regression cases.

The objective should be better semantic precision with the smallest justified change to the IR—not a universal ontology.
