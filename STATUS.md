# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected learner-facing architecture remains unchanged.

## Semantic-to-representation compiler

`SPEC-039 — semantic-to-representation compiler gate`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `SEMANTIC_REPRESENTATION_COMPILER_CONFIRMED_WITH_COVERAGE_GAPS`

## Extraction history

Historical Control A: 4/9 admitted.

Candidate B v1: 2/9 admitted; rejected as implemented after Stage-2 proposition failure concentration.

SPEC-049/050 established that the v1 interface over-forced non-topological truths into proposition slots and that no ontology expansion was justified.

## Candidate B v2

`SPEC-051 — schema-constrained Candidate B v2`

Implementation status: `IMPLEMENTED_REVIEWED`

`SPEC-052 — Candidate B v2 live evaluation`

Implementation status: `IMPLEMENTED_REVIEWED_FOR_DOWNSTREAM_DIAGNOSIS`

Owner verdict: `B_V2_EXTRACTION_RECOVERED_CLAIM_TO_REPRESENTATION_GAP_NEXT`

Accepted SPEC-052 findings:

- B v2 admitted 8/9 frozen blind sources;
- B v1 admitted 2/9 and historical Control A 4/9;
- known-invalid admission remained zero;
- B-v1 Stage-2 proposition-construction failures fell from 6 to 1;
- B v2 used 26 calls / 147,013 tokens, so decomposition carries substantial cost;
- 152/152 claims were exactly grounded and admitted;
- 98 were mechanically claim-only;
- claim-only material created zero unintended topology;
- zero dedicated claim-focus representation decisions were produced;
- extraction decomposition has earned continuation, but promotion remains blocked by downstream representation coverage.

Canonical SPEC-052 evidence:

`examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915/final-report.json`

Claim audit:

`examples/evaluations/spec-052-candidate-b-v2-live-evaluation-20260915/claim-only-preservation-audit.json`

## Current approved work packet

```text
specs/SPEC-053-claim-to-representation-coverage-diagnosis.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-053 is authorized to trace all 98 trusted claim-only SPEC-052 items through the existing representation pipeline and determine why dedicated claim-focus representation coverage is zero.

The fixed terminal path taxonomy is:

- `DEDICATED_REPRESENTATION`
- `SUPPORTING_CONTENT`
- `GENERIC_FALLBACK`
- `NOT_CONSIDERED`
- `FILTERED_OR_DROPPED`
- `AMBIGUOUS`

SPEC-053 must identify exactly one aggregate downstream gap class and recommend exactly one next experiment class.

No extraction change, model/provider call, topology conversion, representation implementation, renderer/UI change, or promotion is authorized.

## Current product question

```text
B v2 extraction
        ↓
trusted topology + 98 claim-only truths
        ↓
existing representation compiler
        ↓
0 dedicated claim-focus decisions
        ↓
WHERE does claim-only knowledge stop becoming learner-facing representation?
        ↓
OWNER REVIEW
```

The goal is to locate the downstream seam, not to change it yet.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 Control-A evidence;
- SPEC-041/042/044/045 historical source/live evidence;
- SPEC-043/046 taxonomies and diagnostics;
- SPEC-047/048 Candidate-B-v1 evidence;
- SPEC-049/050 proposition diagnostics;
- SPEC-051 Candidate-B-v2 implementation/contract;
- SPEC-052 complete live evidence, admitted KnowledgeModels, claim audit, structures, representation decisions, provider ledger;
- trusted semantic vocabulary/proposition semantics;
- grounding/provenance/validators;
- StructureDetector;
- representation strategy/compiler;
- assertion-aware representation behavior;
- renderers;
- navigation/UI;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external evidence retrieval;
- rerun extraction;
- repair historical outputs;
- add relationships/propositions for claims;
- modify StructureDetector;
- implement claim-focus selection;
- add representation strategies/families;
- bind new learner-facing behavior;
- change renderers/UI/navigation;
- promote B v2 or another extractor;
- automatically implement follow-up work.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
