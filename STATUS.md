# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected learner-facing architecture remains unchanged.

## Extraction + semantic compiler state

Historical Control A: 4/9 admitted.

Candidate B v1: 2/9 admitted and rejected as implemented.

Candidate B v2 (`spec-051-candidate-b-v2`): 8/9 admitted in SPEC-052 with zero known-invalid admission; extraction decomposition has earned continuation but remains unpromoted due to downstream representation coverage.

Accepted SPEC-052 owner verdict:

`B_V2_EXTRACTION_RECOVERED_CLAIM_TO_REPRESENTATION_GAP_NEXT`

## Claim-to-representation diagnosis

`SPEC-053 — claim-to-representation coverage diagnosis`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `CLAIM_FOCUS_GAP_CONFIRMED_SELECTION_EXPERIMENT_NEXT`

Accepted findings:

- all 98 mechanically claim-only SPEC-052 items remain exactly grounded in admitted KnowledgeModels;
- 98/98 terminate as `NOT_CONSIDERED`;
- claim focus enumeration excludes them before strategy resolution;
- semantic compiler dispatch has no claim focus class;
- StructureDetector remains topology-only by design and is not the defect;
- assertion-aware claim projection is a separate seam requiring inputs SPEC-052 does not provide;
- first blocking seam is representation focus selection.

Canonical evidence:

`examples/evaluations/spec-053-claim-to-representation-coverage-diagnosis-20260916/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-054 is implemented and awaiting owner review.

All 98 trusted claims became deterministic experimental `CLAIM` focuses. The isolated adapter passed their unchanged source-backed statements to the existing `explanation` resolver contract without nodes, relationships, diagnostic labels, source-specific rules, or inferred structure.

Outcome distribution:

- `EXISTING_NON_FALLBACK_STRATEGY`: 0
- `TRUTHFUL_PROSE_FALLBACK`: 98
- `NO_STRATEGY`: 0
- `INVALID_OR_UNSAFE_DECISION`: 0

Existing entity/relationship/proposition decisions, detected structures, and admitted models regenerate identically. No topology, production behavior, strategy family, renderer, or learner-surface change was made.

Mechanically supported branch: `LEARNER_SURFACE_REQUIRED_TO_DECIDE`.

Recommended next step: `CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT`.

Canonical evidence:

`examples/evaluations/spec-054-claim-focus-selection-experiment-20260916/report.json`

No packet is active. Promotion remains unauthorized.

## Current product question

```text
98 trusted claim-only truths
        ↓
98 deterministic CLAIM focuses
        ↓
existing explanation resolver contract
        ↓
98 CONCISE_PROSE truthful fallbacks
0 unsafe / 0 no-strategy / 0 topology
        ↓
OWNER REVIEW
```

The compiler-level evidence establishes safe routing. Whether an all-prose result teaches these claims usefully requires owner judgment and, if authorized later, a bounded learner-surface binding experiment.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- SPEC-039 existing representation strategy/compiler semantics;
- historical extraction evidence;
- Candidate B v1/v2 extraction implementations/evidence;
- SPEC-052 admitted KnowledgeModels and claim audit;
- SPEC-053 diagnosis and 98-item inventory;
- trusted semantic vocabulary/proposition semantics;
- grounding/provenance/validators;
- StructureDetector;
- existing representation strategy families;
- renderers;
- navigation/UI;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external evidence retrieval;
- rerun extraction;
- convert claims into topology;
- modify StructureDetector;
- add claim-specific strategy families;
- add source-specific routing rules;
- use diagnostic claim labels as production routing features;
- repair unsafe decisions;
- alter existing non-claim representation decisions;
- implement learner-facing rendering/binding;
- redesign UI/navigation;
- promote B v2 or claim focus automatically.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
