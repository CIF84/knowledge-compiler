# SPEC-060 — Progressive Semantic Compression Foundation

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Commit Knowledge Compiler to a new bounded trajectory: **progressive, provenance-preserving semantic compression**, while explicitly not committing to the full long-term product ambition.

This packet has two deliverables:

1. capture the updated project vision/mission and architectural principles in canonical repository documentation;
2. run the first upstream experiment on the missing stage: `SOURCE / TRUSTED INFORMATION → ESSENTIAL INFORMATION`, before any visualization.

The experiment must test whether trusted source-derived information can be reduced into a substantially denser representation while preserving semantic payload, epistemic qualifications, and provenance.

## Updated project vision

> **Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.**

It should eventually allow the same grounded knowledge substrate to support multiple learner goals and media outputs without repeatedly re-summarizing or destructively transforming the source.

Conceptual long-term pipeline:

```text
SOURCE
text / document / audio / video
        ↓
TRUSTED KNOWLEDGE
        ↓
GOAL-PRESERVING SEMANTIC COMPRESSION
        ↓
VARIABLE-RESOLUTION INFORMATION
        ↓
IS FURTHER COGNITIVE GAIN AVAILABLE?
        │
        ├─ NO → concise / enriched language
        │
        └─ YES → structural / perceptual representation
                    ↓
              appropriate visual grammar
```

This is a direction, not a commitment that all stages or media will be solved.

## Updated mission

Build and validate the smallest trustworthy compiler architecture that can:

1. extract grounded knowledge from source material;
2. preserve claims, relationships, evidence, scope, uncertainty, qualifications, and provenance;
3. expose that knowledge at progressively compressed resolutions;
4. make compression a reversible/view-layer operation over a richer semantic substrate rather than destructive chained summarization;
5. use prose when prose is already cognitively efficient;
6. use perceptual/structural representation only when it earns its complexity by reducing cognitive work;
7. eventually support different learner goals, prior knowledge, time budgets, and output media from the same grounded knowledge substrate.

## Non-goals / ambition boundary

This trajectory does **not** currently claim that Knowledge Compiler can:

- optimally teach arbitrary learners;
- identify universally essential information independent of goal;
- reliably compile arbitrary multimodal video;
- automatically choose the optimal visual grammar for every concept;
- prove improved learning outcomes without human evaluation;
- generate a perfect personalized course/presentation from arbitrary media;
- compete primarily as a generic summarizer, slide generator, or visual-generation tool.

Those are possible future applications, not current product commitments.

## Core architectural principle

> **Compression is a view over knowledge, not destruction of knowledge.**

Do not build a lossy chain such as:

```text
source → summary → shorter summary → visual
```

Prefer:

```text
                       SOURCE
                          ↓
                 GROUNDED KNOWLEDGE
                          ↓
                 COMPRESSION POLICY
                  /       |       \
             detailed   concise   recall
                  \       |       /
                   REPRESENTATION POLICY
                    /      |      \
                 prose  enriched  visual
```

Every compressed representation must remain traceable to richer trusted information and ultimately to evidence/source.

## Terminology refinement

Avoid treating `ESSENTIAL` as universal.

Essentiality is potentially relative to:

```text
essential(information, learner_goal, prior_knowledge, desired_resolution)
```

SPEC-060 does not implement learner personalization. For this experiment, use a frozen neutral goal:

> **Preserve the information necessary to accurately understand the source's core explanatory content, including material qualifications and epistemic status, while removing rhetorical/repetitive/linguistically redundant expression.**

Call the operation **goal-preserving semantic compression**.

## Why this packet now

SPEC-053–059 moved downstream from trusted claims toward representation and UI.

Owner review established:

- structural representations are strongly useful when topology/mechanism is the idea;
- visualizability alone does not justify visualization;
- simple claims often need only prose;
- enriched prose is conceptually plausible but token/category emphasis is too lexical;
- useful emphasis must preserve meaning-bearing fragments, not merely highlight numbers/qualifiers;
- comparisons and relations may require richer representation when linear emphasis would consume most of the statement;
- the more fundamental missing stage is semantic compression before representation selection.

SPEC-060 deliberately moves upstream.

## SPEC-059 owner verdict

Record the owner review as:

`ENRICHED_PROSE_CONCEPT_SUPPORTED_SELECTION_MODEL_REQUIRES_REFINEMENT`

Accepted findings:

- B was rarely better than A under the SPEC-059 lexical/category emphasis policy;
- useful emphasis must select contextual meaning-bearing fragments rather than tokens merely because they are quantities/qualifiers;
- case 01 suggests useful compression when fragments such as `more than 23,000 atoms` and `22 picometer precision` jointly expose the scale/precision relationship;
- comparison cases 07–10 often justify C because B would highlight almost all or almost none of the sentence;
- simple claims 11–18 generally favor plain prose;
- case 17 indicates that even a simple two-node relation may justify structure when the relation itself is the explanatory content;
- node count is therefore not a sufficient cognitive-utility criterion;
- visual grammar quality remains a separate unresolved problem.

Do not encode these observations as source/case-specific production rules.

## Experiment question

> **Can the compiler produce a substantially smaller essential-information representation of trusted source-derived material while preserving the information required for accurate understanding, including relationships, scope, qualifications, uncertainty, and provenance?**

This experiment is representation-neutral. Do not build diagrams or learner UI beyond a bounded review artifact needed to inspect source vs compressed information.

## Frozen corpus

Use **exactly 6** deterministic sources/cases drawn from already frozen/admitted repository evidence.

Selection must maximize diversity across domains and information character while requiring no provider/network calls.

Required character coverage across the six cases:

- at least one process/mechanism-rich source;
- at least one structural/relational source;
- at least one quantitative source;
- at least one source with material qualification/scope/uncertainty;
- at least one source whose original language contains repetition/rhetorical framing beyond the core information;
- at least four distinct domains if frozen evidence permits.

Do not cherry-pick cases based on expected compression success. Publish deterministic selection logic and identities.

## Inputs

Prefer the richest already frozen trustworthy textual/evidence representation available for each selected case, not a previously compressed one-line claim when richer admitted source-derived material exists.

For each case preserve identities for:

- frozen source/source fragment;
- admitted KnowledgeModel;
- claims/propositions/relationships;
- evidence/provenance;
- any qualifications/uncertainty metadata available.

Do not retrieve source text from the network.

## Experimental intermediate representation

Introduce an isolated experimental `EssentialInformationModel` (name may vary slightly if repository conventions require) that is **not** a production semantic vocabulary change.

It should represent information units with enough structure to audit compression, for example:

```text
EssentialInformationModel
  goal
  source_identity
  units[]
    id
    concise_text
    semantic_role
    support[]
    preserved_from[]
    epistemic_status
    qualification_links[]
  omitted_fragments[]
    source_range / upstream identity
    omission_reason
  compression_metrics
```

Allowed semantic roles should remain broad and evidence-derived, e.g.:

- `CORE_FACT`
- `MECHANISM`
- `RELATIONSHIP`
- `QUANTITATIVE_FACT`
- `SCOPE_OR_CONDITION`
- `QUALIFICATION_OR_UNCERTAINTY`
- `CONTEXT_REQUIRED_FOR_MEANING`

Do not invent new domain semantics.

## Compression policy

The experimental compiler may:

- remove rhetorical transitions;
- remove duplicated/repeated statements when semantic identity is demonstrable;
- normalize verbose wording into shorter faithful language;
- combine information only when all combined content remains explicitly grounded;
- reorganize information into information-dense units;
- preserve semantic roles separately when doing so reduces linguistic overhead;
- preserve source-backed terminology where paraphrase risks semantic drift.

It must preserve:

- all core claims required by the frozen neutral goal;
- material relationships/mechanisms;
- quantitative values and units;
- scope/conditions;
- uncertainty/epistemic status;
- causal vs correlational status;
- exceptions/material qualifications;
- temporal context where meaning depends on it;
- source/evidence provenance.

Under uncertainty, retain information rather than compress it away.

## Explicitly forbidden compression

Do not:

- convert association into causation;
- remove uncertainty or qualification to save words;
- remove a unit/object from a quantity;
- remove a condition that changes applicability;
- collapse distinct actors/entities into an ambiguous pronoun;
- invent abstractions unsupported by frozen evidence;
- infer learner goals beyond the frozen neutral goal;
- use source/domain-specific hand-written compression rules;
- use model/provider calls;
- optimize only for character/word count.

## Progressive resolutions

For each of the six cases generate **three non-destructive views** from the same frozen grounded substrate:

### R0 — `SOURCE_RICH`

The richest frozen trustworthy source-derived text/evidence view used by the experiment.

### R1 — `ESSENTIAL_EXPLANATION`

A concise coherent language representation preserving all information necessary under the frozen neutral goal.

### R2 — `ESSENTIAL_UNITS`

A denser structured-text representation of the same preserved information, organized into minimal meaning-bearing units/roles.

R2 is **not** a diagram. It may use labels/line breaks/bullets as information organization, but no visual topology, charts, cards-as-diagrams, arrows, or perceptual grammar.

The point is to test semantic compression before visualization.

## Non-destructive requirement

R1 and R2 must be independently generated/views over the same grounded input/intermediate model, not generated by summarizing the previous compressed level.

Required conceptual invariant:

```text
R0 ─┐
    ├→ grounded semantic substrate → R1
    └→ grounded semantic substrate → R2
```

Forbidden:

```text
R0 → R1 → R2
```

if R2 depends only on the already lossy R1 text.

## Compression metrics

For each case report at minimum:

- R0 word count / character count;
- R1 word count / character count;
- R2 word count / character count;
- compression ratios R1:R0 and R2:R0;
- number of grounded semantic units before/after where mechanically definable;
- preserved core claim count;
- preserved relationship count;
- preserved quantitative fact count;
- preserved qualification/uncertainty count;
- omitted/redundant fragment count;
- unsupported/new information count (must be zero for admission);
- provenance coverage.

Do not interpret maximum compression as maximum quality.

## Semantic preservation audit

Build an offline audit comparing each compressed view against frozen grounded information.

At minimum classify each required upstream semantic item as:

- `PRESERVED_EXPLICITLY`
- `PRESERVED_BY_FAITHFUL_COMBINATION`
- `OMITTED_AS_DEMONSTRABLY_REDUNDANT`
- `OMITTED_MATERIAL_INFORMATION`
- `SEMANTICALLY_CHANGED`
- `UNSUPPORTED_ADDITION`
- `UNRESOLVED`

A case fails closed if it contains:

- `OMITTED_MATERIAL_INFORMATION`;
- `SEMANTICALLY_CHANGED`;
- `UNSUPPORTED_ADDITION`;
- unresolved loss affecting accurate understanding.

## Epistemic preservation audit

Explicitly audit whether compression preserves:

- uncertainty language;
- observational vs causal status;
- source attribution where material;
- conditions/scope;
- exceptions;
- temporal boundaries;
- measurement precision/units.

A shorter representation that strengthens certainty or causality is a failure even if its factual nouns/numbers remain correct.

## Review artifact

Create a simple deterministic owner-review artifact for all six cases.

It should make it easy to switch among:

- R0 source-rich;
- R1 essential explanation;
- R2 essential units;
- preservation/provenance audit.

This is an evaluation surface, not a product redesign.

Avoid visual polish that could bias the owner toward the more compressed treatment. Keep typography/layout neutral and comparable.

## Owner-review rubric

Expose neutral questions:

1. **Meaning preservation** — Is anything necessary to understand the idea missing?
2. **Noise reduction** — Was linguistic/rhetorical material removed without loss?
3. **Epistemic fidelity** — Are uncertainty, scope and causal status unchanged?
4. **Information density** — Does the compressed form carry more useful information per unit of attention?
5. **Coherence** — Is R1 still natural enough to understand without reconstructing omitted context?
6. **Unit quality** — Does R2 expose meaningful information units rather than lexical fragments?
7. **Overcompression** — At what resolution, if any, does useful meaning begin to disappear?
8. **Recoverability** — Can compressed information be traced back to richer evidence/source?

Do not auto-score or infer the human verdict.

## Project vision documentation deliverable

Create or update a canonical repository document for the project vision. Prefer an existing appropriate vision/architecture document if one clearly exists; otherwise create:

`docs/PROJECT-VISION.md`

It must capture, concisely but durably:

### Vision

Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.

### Mission

Build a provenance-preserving semantic compiler that separates:

1. ingestion;
2. grounded knowledge extraction;
3. goal-preserving semantic compression;
4. representation selection;
5. learner-facing resolution/media.

### Product principles

- meaning before medium;
- compression before visualization;
- compression is non-destructive;
- provenance survives every resolution;
- prose is a first-class representation;
- visuals must earn their complexity;
- representation form follows cognitive work;
- learner/task context may eventually select resolution;
- one grounded substrate should eventually support multiple outputs/media;
- fail closed when compression would require unsupported inference.

### Ambition boundary

Clearly distinguish validated/current direction from possible future applications such as podcast/video ingestion, personalized learning, presentations, revision material, and multimodal educational outputs.

Do not present future ambitions as implemented capability.

## Required outputs

Create:

`examples/evaluations/spec-060-progressive-semantic-compression-foundation-20260917/`

Include at minimum:

- `report.json`;
- six-case frozen selection manifest;
- R0/R1/R2 artifacts per case;
- `EssentialInformationModel` artifacts per case;
- compression metrics;
- semantic-preservation audit;
- epistemic-preservation audit;
- provenance/recoverability audit;
- deterministic regeneration evidence;
- browser review artifact and gate results;
- zero-call/zero-retrieval statement;
- project-vision document identity/hash;
- owner-review command;
- owner verdict `PENDING`.

## Mechanical decision branches

Choose exactly one:

### `SEMANTIC_COMPRESSION_SAFE_FOR_OWNER_REVIEW`

All admitted compressed views preserve required meaning/epistemic status/provenance with measurable reduction in linguistic representation cost.

### `COMPRESSION_CAUSES_MATERIAL_INFORMATION_LOSS`

One or more compressed views remove information required by the frozen neutral goal.

### `COMPRESSION_CAUSES_SEMANTIC_DRIFT`

Compression changes meaning, certainty, causality, scope, or attribution.

### `FROZEN_SUBSTRATE_INSUFFICIENT_FOR_COMPRESSION`

The existing grounded representation does not contain enough information to safely distinguish redundancy from required context.

### `INCONCLUSIVE`

Mixed evidence prevents a clean mechanical branch.

Do not mechanically claim learning improvement.

## Recommended next-step vocabulary

Choose exactly one:

- `OWNER_REVIEW_REQUIRED`
- `SEMANTIC_COMPRESSION_POLICY_REFINEMENT`
- `VARIABLE_RESOLUTION_EXPERIMENT`
- `MORE_DIAGNOSIS_REQUIRED`

No follow-up implementation is authorized.

## Protected state

Do not modify:

- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- SPEC-055 through SPEC-059 evidence/artifacts;
- SPEC-057 utility decisions;
- production representation strategies/renderers;
- accepted SPEC-038 baseline;
- My Map/navigation/Explore Next behavior;
- historical evaluation evidence.

Prefer isolated experimental compression code and artifacts.

## Explicitly forbidden

Do not:

- call OpenAI or another model/provider;
- retrieve external sources;
- rerun extraction;
- modify KnowledgeModel semantics;
- create unsupported relationships/topology;
- implement learner personalization;
- implement podcast/video ingestion;
- implement presentation generation;
- implement visual grammar selection;
- promote enriched prose;
- redesign production UI;
