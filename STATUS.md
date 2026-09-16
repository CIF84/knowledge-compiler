# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected learner-facing architecture remains unchanged.

## Extraction state

Candidate B v2 (`spec-051-candidate-b-v2`) admitted 8/9 blind sources in SPEC-052 with zero known-invalid admission. Extraction decomposition remains unpromoted pending downstream learner-facing evidence.

## Claim representation evidence

SPEC-053 confirmed the claim focus-selection gap.

SPEC-054 confirmed safe claim-focus routing: 98/98 claims reached the existing resolver and safely fell back to concise prose.

`SPEC-055 — claim representation strategy experiment`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `REPRESENTATION_SEMANTICS_CONFIRMED_LEARNER_SURFACE_BINDING_NEXT`

Accepted SPEC-055 findings:

- 98 trusted claim-only items received traceable non-canonical representation characters;
- 53/98 safely support richer-than-prose plans;
- final strategies: 7 `COMPARISON`, 33 `QUALIFIED_STATEMENT`, 13 `QUANTITATIVE_CALLOUT`, 45 `CONCISE_PROSE`;
- every richer plan retains unchanged concise prose;
- all richer display fields trace to trusted claim text;
- zero semantic/topology mutation or unsafe final plans;
- existing non-claim decisions and detected structures remain unchanged;
- representation diversity is supported offline, but learner value is untested.

Canonical evidence:

`examples/evaluations/spec-055-claim-representation-strategy-experiment-20260916/report.json`

## Current approved work packet

```text
specs/SPEC-056-claim-learner-surface-binding-experiment.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-056 is authorized to bind exactly 12 deterministically selected SPEC-055 claim cases into a dedicated learner-review artifact using the existing SPEC-038 explanatory architecture.

Required sample:

- 3 `COMPARISON`;
- 3 `QUALIFIED_STATEMENT`;
- 3 `QUANTITATIVE_CALLOUT`;
- 3 `CONCISE_PROSE` controls.

Each case must support owner-visible A/B review:

- A = prose-only control;
- B = experimental structured/visual representation + the same concise prose.

No extraction, semantic/topology change, production renderer promotion, navigation redesign, or model/provider call is authorized.

## Current product question

```text
same trusted claim
        ↓
A: prose only
        versus
B: fitting structured/visual representation + concise prose
        ↓
owner judges comprehension / text burden / truthfulness / restraint
```

This is a human learner-surface experiment. Machine gates prove integrity and interaction; they do not decide pedagogical value.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing architecture/baseline;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- SPEC-053/054 claim focus evidence;
- SPEC-055 classifications/plans and report;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- existing production representation semantics/renderers;
- My Map/navigation/Explore Next behavior;
- historical experiment evidence;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external evidence retrieval;
- rerun extraction;
- alter KnowledgeModel semantics;
- create topology from claims;
- modify StructureDetector;
- change SPEC-055 plan semantics;
- invent display semantics;
- promote experimental strategies/renderers;
- redesign navigation/My Map/Explore Next;
- add unrelated product features;
- automatically assign the owner learner verdict.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
