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
specs/SPEC-055-claim-representation-strategy-experiment.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-055 is authorized to test whether the 98 trusted non-topological claims contain enough explicit representation semantics to select richer explanatory plans while preserving concise prose.

Experimental representation characters are non-canonical presentation metadata only:

- `QUANTITATIVE_COMPARISON`
- `DESCRIPTIVE_CONTRAST`
- `QUALIFICATION_OR_CONDITION`
- `DEFINITION_OR_DESCRIPTION`
- `QUANTITATIVE_FACT`
- `CONTEXTUAL_FACT`
- `AMBIGUOUS`

Experimental richer forms may include `COMPARISON`, `QUALIFIED_STATEMENT`, and `QUANTITATIVE_CALLOUT`, but no production renderer or learner-surface binding may be added.

Representation metadata must never become KnowledgeModel semantics or topology.

## Current product question

```text
trusted non-topological claim
        ↓
what representation character is explicit in the truth?
        ↓
visual / structured explanatory form
        +
concise source-faithful prose
        ↓
(no topology mutation)
        ↓
OWNER REVIEW
```

The experiment asks whether claim-like knowledge can support representation diversity before we invest in learner-facing rendering.

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
