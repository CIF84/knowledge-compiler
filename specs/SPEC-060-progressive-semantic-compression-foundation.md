# SPEC-060 — Progressive Semantic Compression Foundation

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Commit Knowledge Compiler to a bounded new trajectory: **progressive, provenance-preserving semantic compression**, without committing to the full long-term product ambition.

Deliver two things:

1. canonical project vision/mission documentation;
2. the first upstream experiment on `SOURCE / TRUSTED INFORMATION → ESSENTIAL INFORMATION`, before visualization.

## Updated vision

> **Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.**

Long-term direction:

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
        ├─ NO  → concise / enriched language
        └─ YES → structural / perceptual representation
                         ↓
                  visual grammar
```

This is a direction, not a claim that all stages/media are solved.

## Mission

Build the smallest trustworthy compiler architecture that can:

1. extract grounded knowledge;
2. preserve claims, relationships, evidence, scope, uncertainty, qualifications and provenance;
3. expose the same knowledge at progressively compressed resolutions;
4. make compression a reversible/view-layer operation over a richer semantic substrate, not destructive chained summarization;
5. use prose when prose is cognitively efficient;
6. use structural/perceptual representation only when it reduces cognitive work;
7. eventually support different goals, prior knowledge, time budgets and output media from one grounded substrate.

## Ambition boundary

Do not claim current ability to optimally teach arbitrary learners, identify universally essential information, compile arbitrary multimodal video, choose the optimal visual grammar, prove learning improvement, or generate perfect personalized courses/presentations. Podcast/video ingestion, personalization, presentations, revision material and multimodal educational outputs are possible applications, not current commitments.

## Core principle

> **Compression is a view over knowledge, not destruction of knowledge.**

Do not build `source → summary → shorter summary → visual`.

Prefer:

```text
SOURCE → GROUNDED KNOWLEDGE → COMPRESSION POLICY → multiple resolutions
                              ↓
                       REPRESENTATION POLICY
                       prose / enriched / visual
```

Every compressed view must remain traceable to richer trusted information and evidence/source.

## Essentiality is goal-relative

Conceptually:

`essential(information, learner_goal, prior_knowledge, desired_resolution)`

SPEC-060 does not implement personalization. Freeze this neutral goal:

> Preserve the information necessary to accurately understand the source's core explanatory content, including material qualifications and epistemic status, while removing rhetorical, repetitive and linguistically redundant expression.

Call this **goal-preserving semantic compression**.

## Evidence entering SPEC-060

Record SPEC-059 owner verdict:

`ENRICHED_PROSE_CONCEPT_SUPPORTED_SELECTION_MODEL_REQUIRES_REFINEMENT`

Accepted findings:

- B was rarely better than A under lexical/category emphasis;
- useful emphasis selects contextual meaning-bearing fragments, not tokens merely because they are quantities/qualifiers;
- case 01 suggests useful compression in the joint fragments `more than 23,000 atoms` and `22 picometer precision`;
- comparison cases often justify richer representation when emphasis would cover almost all or almost none of the sentence;
- simple claims generally favor prose;
- even a two-node relation can justify structure when the relation itself is the idea;
- node count is not a sufficient utility criterion;
- visual-grammar quality remains separately unresolved.

Do not encode these as case/source-specific production rules.

SPEC-053–059 moved downstream from trusted claims toward representation/UI. SPEC-060 deliberately moves upstream.

## Experiment question

> **Can the compiler produce a substantially smaller essential-information representation of trusted source-derived material while preserving accurate meaning, relationships, scope, qualifications, uncertainty and provenance?**

No visualization experiment is authorized here.

## Frozen corpus

Use exactly **6 deterministic cases** from already frozen/admitted repository evidence. Require no provider/network calls. Maximize diversity and cover across the set:

- process/mechanism-rich information;
- structural/relational information;
- quantitative information;
- material qualification/scope/uncertainty;
- repetition/rhetorical framing where frozen material permits;
- at least four domains if available.

Publish deterministic selection logic and identities. Do not cherry-pick expected successes.

Prefer the richest frozen trustworthy source-derived material available, not a previously compressed one-line claim when richer admitted material exists.

Preserve identities for source fragment, admitted model, claims/propositions/relationships, evidence/provenance and qualifications/uncertainty where available. No network retrieval.

## Experimental intermediate representation

Create an isolated experimental `EssentialInformationModel` (minor naming adaptation allowed) without changing production semantic vocabulary. It must support auditability, approximately:

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
    upstream_identity/range
    omission_reason
  compression_metrics
```

Broad evidence-derived roles only, such as `CORE_FACT`, `MECHANISM`, `RELATIONSHIP`, `QUANTITATIVE_FACT`, `SCOPE_OR_CONDITION`, `QUALIFICATION_OR_UNCERTAINTY`, `CONTEXT_REQUIRED_FOR_MEANING`. Do not invent domain semantics.

## Compression policy

May remove rhetorical transitions and demonstrable repetition, normalize verbose wording into shorter faithful language, faithfully combine grounded information, reorganize it into dense meaning-bearing units, and preserve source terminology when paraphrase risks drift.

Must preserve:

- core claims required by the frozen goal;
- material relationships/mechanisms;
- values and units;
- scope/conditions;
- uncertainty/epistemic status;
- causal vs correlational status;
- exceptions/material qualifications;
- temporal context where material;
- evidence/provenance.

Under uncertainty, retain rather than remove.

Forbidden: strengthening association into causation; deleting uncertainty/conditions/units to save words; ambiguous entity collapse; unsupported abstractions; inferred learner goals; source/domain-specific compression rules; optimization for word count alone.

## Three non-destructive resolutions

Generate all three independently from the same grounded substrate:

### R0 — `SOURCE_RICH`
Richest frozen trustworthy source-derived view used by the experiment.

### R1 — `ESSENTIAL_EXPLANATION`
Concise coherent language preserving all information necessary under the frozen neutral goal.

### R2 — `ESSENTIAL_UNITS`
Denser structured text containing minimal meaning-bearing units/roles. Labels, bullets and line breaks are allowed; diagrams, arrows, charts, visual topology and perceptual grammar are not.

Required invariant:

```text
R0 ─┐
    ├→ grounded semantic substrate → R1
    └→ grounded semantic substrate → R2
```

R2 must not be a summary of already-lossy R1 alone.

## Metrics

Per case report:

- R0/R1/R2 words and characters;
- R1:R0 and R2:R0 compression ratios;
- grounded semantic-unit counts where mechanically definable;
- preserved core claims, relationships, quantitative facts and qualifications/uncertainties;
- omitted/redundant fragments;
- unsupported/new information (must be zero for admission);
- provenance coverage.

Maximum compression is not maximum quality.

## Semantic preservation audit

Classify every required upstream semantic item as one of:

- `PRESERVED_EXPLICITLY`
- `PRESERVED_BY_FAITHFUL_COMBINATION`
- `OMITTED_AS_DEMONSTRABLY_REDUNDANT`
- `OMITTED_MATERIAL_INFORMATION`
- `SEMANTICALLY_CHANGED`
- `UNSUPPORTED_ADDITION`
- `UNRESOLVED`

Fail closed on material omission, semantic change, unsupported addition, or unresolved loss affecting accurate understanding.

Explicitly audit uncertainty, observational vs causal status, material attribution, conditions/scope, exceptions, temporal boundaries, precision and units. A shorter representation that strengthens certainty/causality fails.

## Owner-review artifact

Create a simple deterministic six-case review surface switching among R0, R1, R2 and preservation/provenance audit. This is evaluation UI, not product redesign. Keep presentation neutral.

Rubric:

1. Meaning preservation — anything necessary missing?
2. Noise reduction — linguistic/rhetorical material removed without loss?
3. Epistemic fidelity — uncertainty, scope and causal status unchanged?
4. Information density — more useful information per unit of attention?
5. Coherence — is R1 understandable without reconstructing missing context?
6. Unit quality — does R2 expose meaning-bearing rather than lexical fragments?
7. Overcompression — where does useful meaning begin disappearing?
8. Recoverability — can compressed information trace to richer evidence/source?

Do not auto-score or infer owner verdict.

## Canonical project vision document

Create/update the appropriate existing canonical vision document; if none clearly exists, create `docs/PROJECT-VISION.md`.

It must durably capture:

- the Vision and Mission above;
- architecture separation: ingestion → grounded extraction → goal-preserving compression → representation selection → learner-facing resolution/media;
- principles: meaning before medium; compression before visualization; non-destructive compression; provenance at every resolution; prose first-class; visuals earn complexity; form follows cognitive work; future learner/task context may select resolution; one grounded substrate can support multiple outputs; fail closed on unsupported inference;
- ambition boundary distinguishing current validated direction from possible future podcast/video, personalization, presentation, revision and multimodal applications.

Do not present future ambition as implemented capability.

## Required evidence

Create `examples/evaluations/spec-060-progressive-semantic-compression-foundation-20260917/` containing at minimum:

- `report.json`;
- frozen six-case manifest and selection logic;
- R0/R1/R2 per case;
- EssentialInformationModel per case;
- compression metrics;
- semantic + epistemic preservation audits;
- provenance/recoverability audit;
- deterministic regeneration evidence;
- browser review artifact/gates;
- zero-call/zero-retrieval statement;
- project-vision identity/hash;
- owner-review command and verdict `PENDING`.

## Mechanical branch

Choose exactly one:

- `SEMANTIC_COMPRESSION_SAFE_FOR_OWNER_REVIEW` — admitted views preserve required meaning/epistemic status/provenance with measurable linguistic reduction.
- `COMPRESSION_CAUSES_MATERIAL_INFORMATION_LOSS`
- `COMPRESSION_CAUSES_SEMANTIC_DRIFT`
- `FROZEN_SUBSTRATE_INSUFFICIENT_FOR_COMPRESSION`
- `INCONCLUSIVE`

Do not claim learning improvement mechanically.

Recommended next step: choose exactly one of `OWNER_REVIEW_REQUIRED`, `SEMANTIC_COMPRESSION_POLICY_REFINEMENT`, `VARIABLE_RESOLUTION_EXPERIMENT`, `MORE_DIAGNOSIS_REQUIRED`. No follow-up implementation authorized.

## Protected state

Do not modify Candidate B v2 extraction/evidence; SPEC-052 admitted models; trusted semantic vocabulary/propositions; grounding/provenance/validators; StructureDetector; SPEC-055–059 evidence/artifacts; SPEC-057 utility decisions; production representation strategies/renderers; accepted SPEC-038 baseline; My Map/navigation/Explore Next; historical evidence.

Prefer isolated experimental compression code/artifacts.

## Explicitly forbidden

Do not call a model/provider; retrieve external sources; rerun extraction; modify KnowledgeModel semantics; create unsupported relationships/topology; implement learner personalization, podcast/video ingestion, presentation generation or visual-grammar selection; promote enriched prose/compression/renderers; redesign production UI; use owner feedback as source-specific rules; assign the pedagogical verdict; implement follow-up product changes.

## Validation

At minimum:

- focused SPEC-060 tests;
- semantic + epistemic preservation tests;
- provenance/recoverability tests;
- R0/R1/R2 independent-generation invariant;
- compression metrics validation;
- browser gate desktop + 390×844, clean console;
- SPEC-038 and SPEC-055–059 regressions;
- control-plane tests;
- full offline suite;
- deterministic regeneration;
- JSON validation;
- protected-state hashes;
- secret safety;
- `git diff --check`;
- zero provider/model/network calls.

## Completion

On completion set SPEC-060 `IMPLEMENTED_AWAITING_REVIEW`, clear `STATUS.md` to `NONE`, commit/push per protocol, report corpus distribution, compression metrics, preservation results, browser/validation results, project-vision path/hash and owner-review command, then stop at `OWNER_REVIEW`.

## Owner review question

> **Can Knowledge Compiler reduce trusted source-derived material into progressively denser information views while preserving everything necessary for accurate understanding and retaining a recoverable path back to richer evidence?**
