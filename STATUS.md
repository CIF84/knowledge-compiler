# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

Protected learner-facing architecture remains unchanged.

## Extraction state

Candidate B v2 (`spec-051-candidate-b-v2`) admitted 8/9 blind sources in SPEC-052 with zero known-invalid admission. Extraction decomposition remains unpromoted pending downstream learner-facing evidence.

## Representation-selection evidence

SPEC-055 established claim representability beyond prose.

SPEC-056 established that representability alone does not justify visualization.

SPEC-057 established the cognitive-utility gate.

`SPEC-058 — utility-gated learner-surface A/B experiment`

Implementation status: `IMPLEMENTED_REVIEWED`

Owner verdict: `UTILITY_GATE_CONFIRMED_REPRESENTATION_FORM_REMAINS_UNRESOLVED`

Accepted SPEC-058 findings:

- retained structural visuals are strongly preferred to prose;
- retained claim visuals are mixed: some information plausibly benefits from visualization, but current visual grammar is not consistently effective;
- suppressed richer candidates are mixed: historical visuals are usually unhelpful, while important factual fragments may benefit from inline perceptual emphasis;
- prose/low-complexity controls show no benefit from separate visualization;
- prose remains a first-class selected representation;
- a middle representation layer is now justified for experiment: semantically enriched prose;
- visual-grammar selection for genuinely visual claim knowledge remains unresolved and is not part of the current packet.

Canonical principles:

> **A representation must earn its complexity by externalizing cognitive work the learner would otherwise have to perform mentally.**

> **Prose is a first-class representation, not a fallback.**

Canonical evidence:

`examples/evaluations/spec-058-utility-gated-learner-surface-ab-experiment-20260917/report.json`

## Emerging representation architecture

```text
trusted knowledge
      ↓
what cognitive work exists?
      │
      ├─ little → PLAIN PROSE
      │
      ├─ salience / visual-search burden → ENRICHED PROSE (experimental)
      │
      └─ structure / perceptual computation → VISUAL REPRESENTATION
                                                ↓
                                      visual grammar selection
                                      (future unresolved work)
```

Structural topology/mechanism/composition remains the strongest validated visual family.

## Current approved work packet

```text
NONE
```

Status: `NONE`

Authority: `NONE`

Human gate: `NONE`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-059 is implemented and awaiting owner review.

The deterministic A/B/C artifact contains exactly 18 frozen cases:

- 6 quantitative facts;
- 4 comparisons/contrasts;
- 4 qualification/scope cases;
- 4 low-complexity prose controls.

Treatments:

- A = exact plain trusted prose;
- B = exact same prose with only source-traceable semantic typography;
- C = frozen richer reference where one legitimately exists, otherwise explicitly unavailable.

The B treatment preserves sentence order, punctuation, wording, and meaning. All 24 emphasis spans remain inline, exact, and source-traceable; the four low-complexity controls remain un-emphasized. C preserves 16 frozen richer references and explicitly reports two unavailable references without manufacturing replacements.

Desktop and 390×844 browser gates pass all 18 cases, A/B/C switching, text and span identity, responsive layout, and console safety.

Canonical evidence:

`examples/evaluations/spec-059-semantic-typography-enriched-prose-experiment-20260917/report.json`

No packet is active. No learner benefit has been assigned mechanically; promotion remains unauthorized and the owner verdict is pending.

## Current product question

```text
important trusted fact inside prose
        ↓
plain prose
        vs
same prose + restrained semantic typography
        vs
frozen richer representation where available
        ↓
Does enriched prose reduce visual-search/salience work
without introducing another decoding grammar?
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
- SPEC-057 cognitive-utility decisions/evidence;
- SPEC-058 learner-review evidence/artifact;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- production representation strategies/renderers;
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
- modify SPEC-057 utility decisions;
- rewrite trusted prose;
- detach facts into giant-number callouts as enriched prose;
- invent semantic importance;
- use source/domain identity as an emphasis signal;
- encode owner comments as case-specific routing rules;
- redesign production UI/navigation;
- promote experimental enriched prose/renderers;
- implement visual-grammar selection;
- assign the human pedagogical verdict.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract, and its control metadata must agree with that contract. Completed work must not remain active.
