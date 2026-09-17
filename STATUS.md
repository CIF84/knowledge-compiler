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

SPEC-054 confirmed safe claim-focus routing.

SPEC-055 confirmed representation semantics: 53/98 claims safely supported richer-than-prose experimental plans without semantic/topology mutation.

`SPEC-056 — claim learner-surface binding experiment`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `VISUALIZATION_REQUIRES_COGNITIVE_UTILITY_GATE`

Accepted SPEC-056 findings:

- representability is not sufficient evidence that visualization helps;
- prose is a first-class positive representation choice;
- reviewed `QUALIFIED_STATEMENT` visuals mostly added complexity or decomposed grammar rather than reducing cognitive work;
- reviewed `QUANTITATIVE_CALLOUT` treatment often emphasized a number without externalizing meaningful structure;
- comparisons remain promising where visual form externalizes magnitude/difference/contrast;
- multi-node relationship/topology representations remain valuable where diagrams externalize structure otherwise held in working memory;
- a representation must earn its complexity by reducing cognitive work.

Canonical evidence:

`examples/evaluations/spec-056-claim-learner-surface-binding-experiment-20260916/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-057 is implemented and awaiting owner review.

The offline gate evaluated:

- all 53 richer SPEC-055 claim candidates;
- all 45 prose controls;
- four deterministic accepted structural controls;
- the exact 12 SPEC-056 owner-review cases as a post-hoc audit subset.

Results:

- 7/53 richer claim candidates retained `COMPARISON`;
- 46/53 richer claim candidates returned to `CONCISE_PROSE`;
- all 45 prose controls remained prose;
- all 33 qualifier-only treatments and all 13 quantitative callouts were suppressed;
- the economics system, software composition, and reciprocal mechanism survived as strong structural controls;
- the simple focused relationship remained only possible value and returned to prose automatically;
- the exact SPEC-056 audit was directionally aligned across all 12 cases, without using owner comments as routing labels.

Mechanically supported branch: `COGNITIVE_UTILITY_GATE_SUPPORTED`.

Recommended next step: `UTILITY_GATED_LEARNER_SURFACE_AB_EXPERIMENT`.

Canonical evidence:

`examples/evaluations/spec-057-cognitive-utility-gate-experiment-20260917/report.json`

No packet is active. The owner verdict remains pending, no learner-facing rendering changed, and promotion remains unauthorized.

## Current product question

```text
trusted knowledge
      ↓
representable structure?
      ↓ yes
would externalizing it reduce cognitive work?
      ├─ no / uncertain → prose (91/98 claims)
      ↓ yes
comparison + concise prose (7/98 claims)
      ↓
OWNER REVIEW
```

The experiment asks whether representation complexity can be selected by cognitive utility rather than representability alone.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing architecture/baseline;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- SPEC-053/054 claim-focus evidence;
- SPEC-055 classifications/plans;
- SPEC-056 learner-review artifact/evidence;
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
- modify SPEC-055 or SPEC-056 evidence;
- use source/domain identity as a utility signal;
- encode owner comments as case-specific routing rules;
- add/polish learner-facing renderers;
- redesign navigation/UI;
- promote experimental strategies/renderers;
- automatically claim pedagogical effectiveness.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
