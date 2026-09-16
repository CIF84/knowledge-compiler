# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected learner-facing architecture remains unchanged.

## Extraction state

Candidate B v2 (`spec-051-candidate-b-v2`) admitted 8/9 blind sources in SPEC-052 with zero known-invalid admission. Extraction decomposition has earned continuation but remains unpromoted pending downstream representation work.

## Claim pipeline evidence

`SPEC-053 — claim-to-representation coverage diagnosis`

Owner verdict: `CLAIM_FOCUS_GAP_CONFIRMED_SELECTION_EXPERIMENT_NEXT`

`SPEC-054 — claim focus selection experiment`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `CLAIM_FOCUS_ROUTING_CONFIRMED_REPRESENTATION_SEMANTICS_NEXT`

Accepted SPEC-054 findings:

- 98/98 trusted claim-only items became deterministic `CLAIM` focuses;
- 98/98 received safe existing representation decisions;
- all 98 resolved to `TRUTHFUL_PROSE_FALLBACK` / `CONCISE_PROSE`;
- zero no-strategy or unsafe decisions;
- zero topology creation or KnowledgeModel mutation;
- existing models, detected structures, and non-claim representation decisions remained identical;
- routing is therefore confirmed safe;
- universal prose does not establish that prose is the best explanatory form for every claim;
- prose is expected to remain part of richer explanation rather than be replaced by visuals.

Canonical evidence:

`examples/evaluations/spec-054-claim-focus-selection-experiment-20260916/report.json`

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-055 is implemented and awaiting owner review.

All 98 trusted claims received exactly one non-canonical experimental representation character:

- `QUANTITATIVE_COMPARISON`: 3
- `DESCRIPTIVE_CONTRAST`: 4
- `QUALIFICATION_OR_CONDITION`: 33
- `DEFINITION_OR_DESCRIPTION`: 26
- `QUANTITATIVE_FACT`: 13
- `CONTEXTUAL_FACT`: 19
- `AMBIGUOUS`: 0

Final experimental strategies:

- `COMPARISON`: 7
- `QUALIFIED_STATEMENT`: 33
- `QUANTITATIVE_CALLOUT`: 13
- `CONCISE_PROSE`: 45

53/98 claims received traceable richer-than-prose plans; 45/98 correctly remained prose-only. Every plan retained the unchanged concise claim text. No unsafe final plan, KnowledgeModel mutation, topology creation, production renderer, or learner-surface change occurred.

Mechanically supported branch: `REPRESENTATION_SEMANTICS_SUPPORTED`.

Recommended next step: `CLAIM_LEARNER_SURFACE_BINDING_EXPERIMENT`.

Canonical evidence:

`examples/evaluations/spec-055-claim-representation-strategy-experiment-20260916/report.json`

No packet is active. Promotion remains unauthorized.

## Current product question

```text
trusted non-topological claim
        ↓
explicit traceable representation character
        ↓
53 richer experimental plans + concise prose
45 concise-prose-only plans
        ↓
0 semantic/topology mutation
        ↓
OWNER REVIEW
```

The offline compiler evidence supports representation diversity. Whether those plans improve learning remains an owner decision and requires separately authorized learner-surface evaluation.

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing baseline;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels and claim audit;
- SPEC-053 diagnosis;
- SPEC-054 claim-focus implementation/evidence;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- existing production representation strategy semantics;
- existing production renderers;
- navigation/UI;
- historical experiment evidence;
- unrelated user work.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- use external evidence retrieval;
- rerun extraction;
- convert representation characters into trusted semantics;
- create relationships/propositions from claims;
- modify StructureDetector;
- route by domain/source identity;
- use SPEC-053 diagnostic labels as hidden routing answers;
- invent operands/values/conditions;
- add production renderers;
- bind learner-facing UI;
- redesign navigation/UI;
- promote experimental strategy forms automatically.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
