# SPEC-003 — Relationship Semantics

## Status

Ready for implementation.

## Primary Question

> Can we define and enforce a small, domain-general relationship grammar so that valid edges preserve meaning and direction across domains rather than forcing concepts into the nearest available relationship label?

## Purpose

SPEC-002 established that:

- a real LLM can populate the existing `KnowledgeModel` across five unrelated domains;
- the `KnowledgeExtractor` boundary and downstream architecture hold;
- exact source grounding is practical;
- schema validation catches important structural failures;
- but schema-valid relationships can still be semantically wrong.

Examples from the accepted SPEC-002 evaluation include:

```text
RNA polymerase → EXERTS_FORCE_ON → DNA
transfer RNA → ENABLES → amino acid
hand copying → INCREASES → speed
printers → TRANSFORMS_INTO → attempts to control printing
service → PART_OF → component     # reversed direction
```

These failures suggest two related problems:

1. the relationship vocabulary has semantic gaps;
2. relationship labels currently communicate too little about their meaning, directionality, and appropriate use.

SPEC-003 is therefore a **semantic grammar experiment**, not a general ontology project.

The objective is to improve relationship precision across the existing five-domain benchmark with the smallest principled change to the semantic model.

## Required Project Context

Before implementation, read:

1. `README.md`
2. `ROADMAP.md`
3. `PROJECT_MEMORY.md`
4. `ARCHITECTURE.md`
5. `OPERATING_MODEL.md`
6. `PROJECT_HEALTH.md`
7. `specs/SPEC-002-llm-semantic-extraction.md`
8. `debriefs/DEBRIEF-002-llm-semantic-extraction.md`
9. the committed SPEC-002 evaluation artifacts under `examples/evaluations/`
10. current implementation and tests

Treat the accepted SPEC-002 findings as experimental evidence. Do not discard them merely because another ontology design appears theoretically cleaner.

## Experiment Hypothesis

The working hypothesis is:

> Extraction precision will improve if relationships are treated as explicit semantic contracts rather than bare enum labels, and if a small number of evidence-supported relationship types fill genuine cross-domain gaps.

A relationship contract should make clear at least:

```text
name
semantic meaning
source role
target role
directionality
appropriate use
common misuse / exclusion
```

Example conceptually:

```text
PART_OF

Meaning:
    source is a constituent/component of target

Direction:
    part → whole

Valid example:
    payment component → PART_OF → payment service

Invalid reversal:
    payment service → PART_OF → payment component
```

The experiment should determine whether this richer grammar materially improves extraction before introducing more sophisticated semantic validation architecture.

## Scope

Implement the smallest relationship-semantics layer that can:

1. define explicit semantic contracts for every active relationship type;
2. organize relationship types into a small set of semantic families/categories where useful;
3. revise the vocabulary only where SPEC-002 evidence justifies a missing general relationship;
4. expose relationship contracts to the LLM extraction prompt/schema in a maintainable way;
5. reduce ambiguity about relationship direction and intended use;
6. convert the concrete SPEC-002 failures into regression expectations;
7. rerun the same five-domain live evaluation using the improved grammar;
8. compare SPEC-003 results against the accepted SPEC-002 baseline;
9. preserve all existing evidence-grounding and provider-boundary invariants;
10. report improvements, regressions, unresolved gaps, and complexity cost honestly.

## Explicit Non-Goals

Do not implement in SPEC-003:

- graph visualization;
- Streamlit or web UI;
- structure detection;
- feedback-loop detection;
- causal simulation;
- progressive disclosure;
- URL/PDF/audio/video ingestion;
- persistence;
- embeddings;
- cross-document graphs;
- multiple LLM providers;
- a universal ontology;
- WordNet/RDF/OWL integration;
- automatic ontology induction;
- arbitrary user-defined predicates;
- domain-specific ontology packs;
- graph databases;
- general semantic reasoning engines;
- automatic fact checking;
- entity/state/process redesign unless strictly required to complete this experiment;
- broad LLM output-repair heuristics.

Do not solve future representation problems in this increment.

## Preserve the Existing Architecture

The intended system remains:

```text
SourceDocument
      ↓
KnowledgeExtractor
      ↓
ExtractionResult
      ↓
validation / deduplication
      ↓
KnowledgeModel
```

SPEC-003 may improve the semantic contract used by extraction and validation, but must not introduce a parallel representation path.

The `KnowledgeModel` remains the semantic IR unless the experiment uncovers a genuine blocker. Any material IR redesign must be reported explicitly as a deviation and justified by observed evidence.

## Relationship Grammar

Create one canonical definition for relationship semantics rather than scattering definitions independently across prompt text, tests, and documentation.

The exact implementation is up to Codex, but conceptually each active relationship should be describable by metadata equivalent to:

```python
RelationshipDefinition(
    type=RelationshipType.PART_OF,
    family=RelationshipFamily.STRUCTURAL,
    meaning="The source is a constituent or component of the target.",
    direction="part_to_whole",
    use_when="The source exists as a component/subpart of the target.",
    avoid_when="The source merely interacts with, depends on, or precedes the target.",
)
```

Do not overengineer this into a plugin framework or ontology service. A typed/static registry is sufficient if it keeps semantics explicit and testable.

## Semantic Families

Evaluate whether the current predicates can usefully be grouped into a small number of families such as:

```text
STRUCTURAL
CAUSAL
DEPENDENCY
TEMPORAL
INTERACTION
TRANSFORMATION
COMPARATIVE / DESCRIPTIVE   only if evidence warrants
```

These names are hypotheses, not mandatory final categories.

Families should exist only if they improve reasoning, prompting, validation, evaluation, or future structure detection. Do not create taxonomy for taxonomy's sake.

The likely conceptual distinction is:

```text
STRUCTURAL
    what something is / what contains what

CAUSAL
    what changes or produces what

DEPENDENCY
    what requires, enables, or constrains what

TEMPORAL
    what occurs before what

INTERACTION
    what acts on, binds to, transfers to, or otherwise directly interacts

TRANSFORMATION
    what becomes or produces a transformed state/object
```

Codex may refine this based on the actual existing vocabulary and SPEC-002 evidence.

## Vocabulary Evolution Rule

Do **not** simply add every missing predicate observed in SPEC-002.

A new relationship type should be introduced only when all of the following are reasonably true:

1. an important proposition cannot be represented honestly by the existing grammar;
2. the missing concept is general enough to be useful beyond one sentence/domain;
3. adding it reduces semantic distortion rather than merely increasing specificity;
4. its direction and meaning can be defined clearly;
5. it does not substantially overlap an existing predicate.

Prefer a small general predicate over many domain-specific predicates.

For example, investigate whether a general interaction predicate such as:

```text
ACTS_ON
```

could represent multiple currently distorted directional interactions more honestly than adding separate biology-, economics-, and history-specific verbs.

Likewise, investigate whether concepts such as:

```text
BINDS_TO
TRANSFERS_TO / DELIVERS_TO
PROHIBITS / MUST_NOT
```

are genuinely general semantic primitives or whether their propositions belong in claims rather than edges.

The SPEC deliberately does not prescribe the final vocabulary. The implementation must justify additions from evidence.

## Domain-Specific Predicates

Reassess the existing highly specific predicates:

```text
INDUCES
EXERTS_FORCE_ON
```

Do not automatically remove them. Determine whether:

- they are useful precise specializations;
- they cause misuse outside their natural domain;
- stronger semantic contracts are sufficient to prevent misuse;
- a more general parent/family concept is useful;
- they should remain available but with explicit applicability guidance.

Backward compatibility with SPEC-001/002 artifacts is desirable but not more important than establishing a correct current grammar. If enum changes are justified, document migration impact clearly.

## Directionality Contracts

Directionality must become explicit for every directional relationship.

Examples:

```text
A PART_OF B
    A = part
    B = whole

A PRECEDES B
    A occurs before B

A INCREASES B
    A causally increases B

A REQUIRES B
    A depends on B

A CREATES B
    A produces/brings B into existence
```

The extraction instructions must communicate these semantics clearly enough that a model is not expected to infer them merely from the enum name.

Where a relationship is symmetric, explicitly mark it as such.

Where inverse direction has a materially different meaning, do not silently normalize it unless the semantics are provably equivalent.

## Applicability and Misuse Guidance

For predicates with known SPEC-002 failure modes, include explicit negative guidance.

Examples:

```text
EXERTS_FORCE_ON
    use only for literal physical force
    do not use as a metaphor for influence, contribution, binding, pressure, or causation

TRANSFORMS_INTO
    source itself becomes target
    do not use when an actor merely causes, attempts, creates, or participates in target

INCREASES
    source causally raises the amount/rate/value of target
    do not use merely because source and target are associated with a statement containing "more", "faster", etc.

PART_OF
    source is part; target is whole
    do not reverse the direction
```

These rules should come from the canonical relationship definitions where practical rather than duplicate prompt-only prose.

## Claims vs Relationships

SPEC-002 showed that some important propositions remained claims because no honest edge existed.

Do not assume every meaningful statement must become a relationship.

Use this principle:

> Prefer a truthful claim over a misleading edge.

The extractor should be explicitly allowed to retain propositions as claims when the active relationship grammar cannot represent them without semantic distortion.

A lower edge count is acceptable if precision improves.

## Regression Corpus

Use the same five domain fixtures from SPEC-002:

```text
electromagnetism
software_architecture
economics
biology
history
```

Do not rewrite the source fixtures merely to make extraction easier unless a factual/linguistic defect in a fixture is discovered. If changed, record exactly why because the SPEC-002 comparison depends on corpus stability.

The accepted SPEC-002 artifacts are the baseline.

## Required Regression Cases

Convert at least these observed SPEC-002 failures into explicit semantic regression expectations.

### Software architecture

Prevent or flag:

```text
service → PART_OF → component
```

when the source semantics are component → part of → service.

Preserve the prohibition that one component must not directly call another as a claim unless a justified general predicate represents it honestly.

### Economics

Do not use:

```text
EXERTS_FORCE_ON
```

as a generic relationship for quantities contributing to shortage/surplus.

Do not produce a misleading `MEASURED_BY` relationship for elasticity.

### Biology

Do not represent binding as literal physical force:

```text
RNA polymerase → EXERTS_FORCE_ON → DNA
```

Do not distort delivery/transport into:

```text
transfer RNA → ENABLES → amino acid
```

Prefer explicit chronology where the source states that transcription precedes translation.

### History

Do not reverse the source meaning into:

```text
hand copying → INCREASES → speed
```

Do not represent an actor becoming an action/event:

```text
printers → TRANSFORMS_INTO → attempts to control printing
```

Prefer explicit `PRECEDES` where chronology is directly stated and semantically important.

### Electromagnetism

Retain the strong mechanism edges from SPEC-002 without causing regressions through ontology changes.

The changing-field state-collapse issue should be observed but is **not** the primary problem of SPEC-003. Do not redesign state modeling merely to fix it.

## Semantic Validation

Implement only validation that is justified and deterministic.

The project already validates syntactic/domain invariants such as known enums and valid endpoints. SPEC-003 may add deterministic semantic checks where the relationship contract makes them unambiguous.

Examples might include:

- canonical definition exists for every enum value;
- relationship family is known;
- symmetric/directional metadata is internally consistent;
- definitions have required meaning/direction fields;
- no duplicate active predicate definitions;
- prompt vocabulary is generated from or synchronized with canonical definitions.

Do **not** pretend deterministic code can prove that arbitrary real-world causality is correct.

Avoid building a rule engine that attempts to infer domain truth from entity names.

The main semantic-quality mechanism in this increment is better explicit grammar + extraction behavior + regression evaluation.

## Prompt Construction

Refactor the LLM instructions so relationship semantics are provided systematically.

The model should receive, for each allowed predicate, enough information to distinguish:

```text
what it means
which direction it points
when to use it
when not to use it
```

Avoid an enormous prompt full of examples for every imaginable domain.

The relationship registry should preferably be the source used to construct this portion of the prompt so code vocabulary and prompt vocabulary cannot silently drift.

Increment the prompt version for SPEC-003.

Preserve the successful SPEC-002 evidence-grounding instructions:

```text
LLM nominates exact unique quote
        ↓
deterministic quote resolution
        ↓
validated SourceSpan
```

Do not weaken these invariants.

## Evaluation Design

Run the same five-domain live evaluation after the new grammar is implemented.

Create a new output directory; never overwrite SPEC-002 artifacts.

The evaluation must compare the new run with the accepted SPEC-002 baseline.

For each domain assess at minimum:

```text
grounding
entity quality
relationship quality
coverage
precision
deduplication quality
vocabulary fit
cross-domain usefulness
```

Also add a focused **relationship regression** assessment for the known SPEC-002 failures.

## Comparison Against SPEC-002

Produce an inspectable comparison artifact, for example:

```text
examples/evaluations/<spec-003-run>/comparison.json
```

or an equally simple format.

For each domain, record:

```text
SPEC-002 assessment
SPEC-003 assessment
known regressions fixed
known regressions remaining
new regressions introduced
relationship types added/removed/changed
qualitative verdict
```

Use a simple verdict vocabulary such as:

```text
IMPROVED
UNCHANGED
REGRESSED
MIXED
```

Do not invent a mathematically precise aggregate score from subjective judgments.

The experiment should make it easy for independent review to answer:

> Did semantic precision improve enough to justify the added grammar complexity?

## Complexity Budget

Relationship quality could easily lead to ontology overengineering.

Treat complexity as part of the experiment.

At handoff, report:

- number of relationship types before SPEC-003;
- number after;
- number of semantic families introduced;
- approximate prompt growth attributable to relationship definitions if readily measurable;
- new core concepts/classes/modules introduced;
- whether any downstream model/schema migration was required.

A larger vocabulary is not automatically a better result.

The desired direction is:

```text
minimum grammar complexity
        +
maximum semantic precision
        +
useful cross-domain coverage
```

## Testing Strategy

Normal automated tests must remain offline and deterministic.

Add tests covering at least:

- every active relationship enum has exactly one semantic definition;
- relationship definitions expose required semantics/directionality;
- prompt construction includes the canonical definitions;
- known high-risk predicates contain their exclusion/misuse guidance where applicable;
- any newly added predicates serialize/deserialize correctly;
- existing `KnowledgeModel` round-trip remains valid;
- evidence grounding behavior remains unchanged;
- fixture extraction still works offline;
- evaluation comparison logic works without network access;
- semantic regression metadata covers the required SPEC-002 failure cases.

Retain all existing tests unless a justified semantic-model change requires updating them.

Real API calls must remain opt-in and outside normal `pytest`.

## Live Evaluation

At least one complete live five-domain SPEC-003 evaluation is required before handoff.

Use the same provider/model as the accepted SPEC-002 baseline if still available and practical, so relationship grammar is the primary changed variable.

If provider/model must change, report that explicitly because it weakens direct causal comparison.

Do not silently retry until a favorable run appears.

If retries are required:

1. preserve/report failed attempts;
2. explain why they failed;
3. do not weaken validation;
4. do not select only the best run without disclosure.

## Acceptance Criteria

SPEC-003 is complete when all are true:

- [ ] Every active relationship type has one explicit canonical semantic contract.
- [ ] Directionality is explicit for directional predicates.
- [ ] Known misuse cases are documented for high-risk predicates.
- [ ] Relationship semantics are systematically exposed to the LLM extractor.
- [ ] Any vocabulary additions are justified by SPEC-002 evidence and remain deliberately small/general.
- [ ] The extractor is explicitly allowed to prefer claims over misleading edges.
- [ ] The same five-domain corpus is used for live evaluation.
- [ ] Known SPEC-002 semantic failures are represented as regression expectations.
- [ ] Normal automated tests remain deterministic/offline and pass.
- [ ] Existing source-evidence invariants remain intact.
- [ ] Provider-specific concerns remain behind `KnowledgeExtractor`.
- [ ] At least one complete live five-domain evaluation is performed.
- [ ] SPEC-003 outputs are compared explicitly with the accepted SPEC-002 baseline.
- [ ] New regressions and remaining semantic failures are reported, not hidden.
- [ ] Complexity cost of the richer grammar is reported.
- [ ] No visualization, structure-detection, persistence, universal ontology, or unrelated architecture is introduced.
- [ ] Completed implementation is committed and pushed to canonical GitHub before review.

The primary qualitative acceptance test is:

> Across the same five domains, does the new grammar produce materially more truthful relationship meaning and direction than SPEC-002 without becoming an uncontrolled ontology?

A valid outcome may be **NO**. If richer relationship definitions do not materially improve extraction, that is important evidence and should be preserved rather than further expanding scope.

## Required Handoff to Review

When implementation is complete, Codex must report:

1. architecture implemented;
2. relationship grammar design;
3. semantic families introduced, if any;
4. relationship types before vs after;
5. predicates added, removed, or redefined and the evidence for each change;
6. files added/changed;
7. exact automated test result;
8. live evaluation command;
9. provider/model/prompt version used;
10. results for each of the five domains;
11. SPEC-002 regressions fixed;
12. SPEC-002 regressions still present;
13. new regressions introduced;
14. vocabulary gaps still observed;
15. complexity impact;
16. deliberate deviations from this SPEC;
17. approximate live-call usage/cost if available;
18. commit SHA;
19. confirmation that the commit is pushed to canonical GitHub.

Do not write `DEBRIEF-003` during implementation. It follows independent review.

Do not expose API keys, secrets, or environment values in terminal captures, logs, committed artifacts, or the handoff. If a secret is accidentally exposed, stop and report only that rotation is required; never reproduce the secret value.

## Operational Learning Capture

SPEC-003 is the third full experiment through the repository-centered operating model.

The independent review/debrief should observe:

- whether SPEC-002 evidence was easy to reconstruct and use as regression input;
- whether canonical project memory prevented rediscovery;
- whether the SPEC successfully kept ontology work bounded;
- whether the five-domain benchmark reduced decision ambiguity;
- whether live evaluation remained cheap enough for routine use;
- whether manual semantic review is becoming the dominant bottleneck;
- whether any process step can now be simplified or automated without losing learning quality.

## Likely Decision After SPEC-003

Do not implement this section during SPEC-003; it exists only to clarify why this experiment matters.

If relationship precision improves materially while complexity remains controlled, the next likely uncertainty becomes:

> Can reliable semantic edges be composed into higher-order structures such as hierarchies, causal paths, processes, dependencies, and feedback loops?

That would justify a future structure-detection experiment.

If relationship precision remains poor, do **not** proceed to visualization merely because the roadmap says so. The next experiment should instead address whichever semantic failure SPEC-003 isolates.
