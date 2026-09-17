# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected learner-facing architecture remains unchanged.

## Extraction state

Candidate B v2 (`spec-051-candidate-b-v2`) admitted 8/9 blind sources in SPEC-052 with zero known-invalid admission. Extraction decomposition remains unpromoted pending downstream learner-facing evidence.

## Representation-selection evidence

SPEC-055 established that 53/98 trusted claims were representable beyond prose without semantic/topology mutation.

SPEC-056 established that representability alone does not justify visualization.

`SPEC-057 — cognitive utility gate experiment`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `COGNITIVE_UTILITY_GATE_CONFIRMED`

Canonical principle:

> **A representation must earn its complexity by externalizing cognitive work the learner would otherwise have to perform mentally.**

Accepted SPEC-057 findings:

- before gate: 53 richer claim plans and 45 prose controls;
- after gate: 7 `COMPARISON`, 91 `CONCISE_PROSE`;
- all 33 qualifier-only treatments and all 13 quantitative callouts were suppressed;
- all 45 prose controls remained prose;
- economics multi-node system, software composition, and reciprocal mechanism survived as strong structural controls;
- the simple focused relationship was only possible value and returned to prose;
- the SPEC-056 12-case audit aligned directionally without owner feedback being used as routing labels;
- cognitive utility, rather than representability alone, is the current experimental representation-selection criterion.

Canonical evidence:

`examples/evaluations/spec-057-cognitive-utility-gate-experiment-20260917/report.json`

## Current approved work packet

```text
specs/SPEC-058-utility-gated-learner-surface-ab-experiment.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `OFFLINE_ONLY`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-058 is authorized to build a bounded 16-case learner-facing A/B review artifact that pressure-tests both sides of the SPEC-057 gate.

Required groups:

- 4 retained claim comparison visuals;
- 4 retained structural visual cases;
- 4 suppressed richer candidates (2 qualifier, 2 quantitative callout);
- 4 prose/low-complexity controls.

For retained cases, compare prose/text control against the utility-gated selected visual + prose.

For suppressed cases, compare utility-gated selected prose against the preserved suppressed richer candidate + prose.

The experiment must keep machine evidence separate from the human learner verdict.

## Current product question

```text
representation candidate
        ↓
SPEC-057 cognitive utility gate
        ↓
selected visual OR selected prose
        ↓
learner-facing A/B review
        ↓
Does the gate put complexity where it actually helps?
        ↓
OWNER REVIEW
```

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing architecture/baseline;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- SPEC-055 representation evidence/plans;
- SPEC-056 learner-review evidence/artifact;
- SPEC-057 utility decisions/evidence;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- production representation strategy semantics/renderers;
- My Map/navigation/Explore Next product behavior;
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
- modify SPEC-057 gate decisions;
- invent display semantics/values;
- polish suppressed historical candidates into new treatments;
- use owner feedback as hidden routing labels;
- redesign production navigation/UI;
- promote experimental strategies/renderers;
- assign the human pedagogical verdict;
- implement follow-up product changes.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
