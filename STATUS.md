# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected four-surface model:

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

## Semantic-to-representation compiler

`SPEC-039 — semantic-to-representation compiler gate`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `SEMANTIC_REPRESENTATION_COMPILER_CONFIRMED_WITH_COVERAGE_GAPS`

## Blind evaluation foundation

`SPEC-040 — blind out-of-sample evaluation harness`

Implementation status: `IMPLEMENTED_REVIEWED`

Frozen single-pass control identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Blind reliability evidence

`SPEC-042 — blind out-of-sample live execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DIAGNOSIS`

`SPEC-043 — blind failure diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED`

`SPEC-044 — blind replication source set freeze`

Implementation status: `IMPLEMENTED_REVIEWED`

`SPEC-045 — blind replication live execution`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_FAILURE_MODE_ANALYSIS`

## Extraction reliability failure-mode analysis

`SPEC-046 — extraction reliability failure-mode analysis`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `FAILURE_STAGES_MAPPED_EXTRACTION_DECOMPOSITION_NEXT`

Accepted findings:

- nine blind sources: 4 admitted, 5 failed closed;
- all 7 known invalid/malformed semantic objects were prevented from admission;
- failure origin stages: 3 `ENTITY_INVENTORY`, 2 `RELATIONSHIP_SEMANTICS`, 1 `PROPOSITION_CONSTRUCTION`, 1 `EVIDENCE_FIDELITY`;
- detection stages: 4 `CANONICAL_VALIDATION`, 3 `GROUNDING_RESOLUTION`;
- `ENTITY_INVENTORY` is the only origin stage recurring across unrelated domains, but failures remain heterogeneous overall;
- extraction reliability and trust-boundary reliability must remain separate measures;
- exactly one next experiment class is accepted: `EXTRACTION_DECOMPOSITION`.

Canonical evidence:

`examples/evaluations/spec-046-extraction-reliability-failure-mode-analysis-20260913/report.json`

## Current approved work packet

```text
specs/SPEC-047-decomposed-extraction-ab-harness.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-047 is authorized to implement and freeze a decomposed Candidate-B extractor and A/B evaluation harness **without any live/model execution**.

Candidate B is constrained to three stages:

```text
SOURCE
  ↓
STAGE 1 — ENTITY INVENTORY
  ↓ deterministic gate / freeze IDs
STAGE 2 — SEMANTIC STRUCTURE
  ↓ deterministic gate against frozen IDs
STAGE 3 — CLAIM / EVIDENCE BINDING
  ↓ exact evidence grounding
EXISTING canonical validator
  ↓
trusted KnowledgeModel or fail closed
```

Control A remains the unchanged historical single-pass `spec-010-v1` extractor used in SPEC-042/SPEC-045.

SPEC-047 must freeze the future nine-source comparison contract and proposed Candidate-B call ceiling (27 maximum calls with upstream-failure short-circuiting), but it must not authorize or make those calls.

## Current product question

```text
single-pass Control A
        versus
explicitly staged Candidate B
        ↓
same 9 frozen blind sources
        ↓
compare admission + semantic richness + failure origin
        ↓
compare calls/tokens/latency/cost evidence
        ↓
trusted boundary must remain unchanged
```

The immediate goal is to build a scientifically clean candidate and experiment harness, not to prove Candidate B better.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 Control-A implementation and frozen identity;
- SPEC-041/042/044/045 source packets, manifests, raw responses, run histories, and evidence;
- SPEC-043 taxonomy and historical classifications;
- SPEC-046 failure-stage analysis and accepted recommendation;
- prompt `spec-010-v1` and Control-A extraction behavior;
- trusted semantic vocabulary;
- canonical grounding/provenance behavior;
- strict declared-identity validation;
- canonical KnowledgeModel validator;
- representation strategy logic and renderer coverage;
- navigation/UI behavior;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use web/network retrieval;
- execute Candidate B on the blind corpus;
- rerun Control A;
- tune Candidate B using historical failed-source answers/examples;
- modify Control A;
- weaken canonical validation or evidence exactness;
- add deterministic semantic repair or automatic missing-ID normalization;
- change trusted semantic vocabulary;
- change representation/renderers/UI/navigation;
- promote Candidate B;
- authorize the future live A/B execution automatically.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
