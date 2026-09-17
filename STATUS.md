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
specs/SPEC-057-cognitive-utility-gate-experiment.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-057 is authorized to test a conservative cognitive-utility gate between representation-semantic eligibility and richer representation selection.

The experiment must evaluate:

- all 53 richer SPEC-055 claim candidates;
- all 45 prose controls;
- a deterministic bounded sample of accepted structural positive controls;
- the exact 12 SPEC-056 owner-review cases as a post-hoc audit subset.

Utility outcomes:

- `STRONG_EXTERNALIZATION_VALUE`;
- `POSSIBLE_EXTERNALIZATION_VALUE`;
- `LOW_EXTERNALIZATION_VALUE`;
- `UNSAFE_OR_UNSUPPORTED`.

Only strong externalization value retains richer automatic representation. Possible/low/unsafe cases return to `CONCISE_PROSE` experimentally.

No learner-facing rendering changes are authorized.

## Current product question

```text
trusted knowledge
      ↓
representable structure?
      ↓ yes
would externalizing it reduce cognitive work?
      ├─ no / uncertain → prose
      ↓ yes
richer representation + concise prose
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
