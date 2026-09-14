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

Frozen single-pass Control-A identity:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

## Blind reliability evidence

SPEC-042 through SPEC-046 remain accepted historical evidence. The current accepted diagnostic conclusion is:

`FAILURE_STAGES_MAPPED_EXTRACTION_DECOMPOSITION_NEXT`

Key evidence:

- 9 blind sources total;
- historical Control A admitted 4/9;
- all 7 known invalid/malformed semantic objects were contained by the deterministic boundary;
- failure origins span entity inventory, relationship semantics, proposition construction, and evidence fidelity;
- entity inventory is the only origin stage recurring across unrelated domains.

## Decomposed extraction A/B harness

`SPEC-047 — decomposed extraction A/B harness`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `CANDIDATE_B_FROZEN_LIVE_AB_EXECUTION_APPROVED`

Accepted Candidate-B architecture:

```text
STAGE 1 — ENTITY_INVENTORY
  ↓ deterministic gate / freeze IDs
STAGE 2 — SEMANTIC_STRUCTURE
  ↓ deterministic gate against frozen IDs
STAGE 3 — CLAIM_EVIDENCE_BINDING
  ↓ exact evidence grounding
EXISTING canonical validator
  ↓
trusted KnowledgeModel or fail closed
```

Frozen Candidate-B implementation commit:

`9ad5e0854e6866c73b3f6febd989e0766cc14a13`

Frozen implementation hashes:

- core `a09bb36a2214364f915b05e0f7818ffe0b145760b76afb1f00fc66ed09dc75ea`
- OpenAI adapter `2d91a2fdfcf04bcc2180331571e3d7c2a20e797fe9fbc83c046aafdad1764280`
- A/B harness `85e60376aabc797e75bafbda71df3ec2a68d24f0220f931b2eb89f0d9b9824fc`

Frozen stage-contract SHA-256:

`b13c96ac01b2f0730f57852078c702f01a2234bca1f7567654686d214c50f694`

Control A remains historical only; no rerun is authorized.

## Decomposed extraction live A/B execution

`SPEC-048 — decomposed extraction live A/B execution`

Implementation status: `IMPLEMENTED_AWAITING_REVIEW`

Candidate B admitted 2/9 sources in 19 calls versus historical Control A's
4/9 in 9 calls. All seven Candidate-B rejections failed closed, zero known-invalid
objects were admitted, and the mechanically supported branch is `B_REGRESSION`.

Canonical evidence:

`examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/final-report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-048 is implemented and awaiting owner review. Its canonical report is
`examples/evaluations/spec-048-decomposed-extraction-live-ab-execution-20260913/final-report.json`.

No packet is active. No further provider/model call, retry, repair, adaptation,
promotion, or follow-up implementation is authorized.

## Current product question

```text
historical Control A: 4/9 admitted, 9 calls
        ↔
frozen Candidate B: 2/9 admitted, 19 calls
        ↓
zero known-invalid admission in both arms
        ↓
7 Candidate-B failures preserved closed
        ↓
mechanical branch: B_REGRESSION
        ↓
OWNER REVIEW
```

The immediate goal is owner review of the observed regression and cost evidence,
not promotion, repair, or another extraction experiment.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 representation compiler behavior;
- SPEC-040 Control-A implementation/frozen identity;
- SPEC-041/042/044/045 exact source packets, manifests, raw responses, run histories, and evidence;
- SPEC-043 taxonomy and classifications;
- SPEC-046 failure-stage analysis;
- SPEC-047 Candidate-B implementation, prompts/schemas, stage contracts, comparison contract, Control-A comparison records, offline fixtures, and proposed live manifest;
- SPEC-048 raw provider responses, parsed proposals, request ledger, stage gates,
  final outcomes, A/B comparison, and post-run taxonomy audit;
- trusted semantic vocabulary;
- canonical grounding/provenance behavior;
- strict declared-identity validation;
- canonical KnowledgeModel validator;
- representation strategy logic and renderer coverage;
- navigation/UI behavior;
- unrelated user work.

## Explicitly forbidden

Do not:

- rerun Control A;
- make any additional Candidate-B provider call;
- exceed 27 Candidate-B provider calls;
- retry or repair any failed stage;
- change model/source/order/prompt/schema between sources;
- retrieve external enrichment;
- automatically normalize missing IDs;
- weaken evidence exactness or canonical validation;
- change trusted semantic vocabulary;
- change representation/renderers/UI/navigation;
- implement additional extraction improvements during or after the run;
- promote Candidate B automatically;
- authorize follow-up work without owner review.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
