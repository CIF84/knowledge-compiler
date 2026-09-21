# SPEC-061 — Explanatory Structure Preservation Experiment

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

SPEC-060 demonstrated that the current grounded substrate can produce mechanically smaller R1/R2 views without detected loss of modeled semantic items, epistemic status, or provenance.

Owner review of case 01 (Understanding plate motions) exposed a missing preservation dimension:

> **Semantic-content preservation is not sufficient for cognitive/explanatory preservation.**

The source text already performed useful cognitive work by arranging information into a coherent explanatory traversal. SPEC-060 R1/R2 preserved facts but weakened that traversal, increasing reconstruction effort.

This packet tests the missing layer before any further compression, personalization, or visualization work:

> **Can Knowledge Compiler recover an explanation's latent meaning blocks, their explanatory functions, and their traversal, then compress within those blocks without flattening the explanation into atomic facts?**

## SPEC-060 owner verdict

Record SPEC-060 owner review as:

`SEMANTIC_CONTENT_PRESERVED_EXPLANATORY_STRUCTURE_NOT_PRESERVED`

Accepted findings from case 01:

- R0 was not merely verbose source prose; its paragraphs often acted as useful containers of meaning;
- R1 felt primarily like source text broken into shorter/single-sentence units and was not a meaningful cognitive improvement;
- R2 improved visible structure but disrupted the natural chain of thought;
- preserving all modeled facts did not preserve the explanation;
- the owner's approximate mental compression of R0 preserved a path:
  1. mechanism — plates separate; magma rises; new crust forms;
  2. canonical example — Mid-Atlantic Ridge;
  3. timescale/consequence — slow spreading over millions of years produces ocean-scale change;
  4. observational/example block — Iceland/Krafla;
  5. further example/generalization — Red Sea / Arabia–Africa separation;
- paragraph boundaries were useful in this source, but `paragraph == meaning block` must NOT become a rule;
- some linguistic material that does not encode a domain fact nevertheless encodes how facts should be traversed;
- raw word-count compression is secondary if reduced text increases mental reconstruction.

Owner review was stopped after case 01 because this architectural failure is upstream of the remaining cases. Do not infer verdicts for cases 02–06.

## Architectural refinement

Extend the progressive-compression architecture conceptually:

```text
SOURCE
  ↓
GROUNDED KNOWLEDGE
  ↓
EXPLANATORY STRUCTURE
  ├─ meaning blocks
  ├─ explanatory functions
  └─ traversal / discourse relations
  ↓
GOAL-PRESERVING COMPRESSION
  ↓
VARIABLE-RESOLUTION REPRESENTATION
  ↓
FURTHER COGNITIVE GAIN?
  ├─ no  → language
  └─ yes → structural/perceptual representation
```

Canonical principle:

> **Preserve useful explanatory work already present in the source before compressing its language.**

Refine the optimization target from minimum word count to:

> **Reduce representational cost without increasing the cognitive work required to reconstruct meaning or explanatory traversal.**

## Key distinction

Do not confuse domain semantics with explanatory/discourse semantics.

Domain semantics include:
- entities;
- claims;
- relationships;
- quantities;
- scope/conditions;
- uncertainty;
- evidence.

Explanatory structure includes relations such as:
- this block establishes a mechanism;
- this block grounds it with a canonical example;
- this block explains scale/timescale/consequence;
- this block provides observation/evidence;
- this block supplies another example/generalization;
- this block qualifies or limits the previous explanation.

These discourse relations may not themselves be claims about the domain, but they can be necessary to understand the domain efficiently.

## Hypothesis

> A compressed explanation that preserves coherent meaning blocks and their explanatory traversal will require less learner reconstruction than atomized essential units, even when both preserve the same modeled semantic content.

This packet tests whether such structure can be recovered safely and deterministically from frozen evidence. It does not claim learning improvement mechanically.

## Frozen corpus

Use the same exact six frozen source identities from SPEC-060.

No external retrieval and no extraction rerun.

Case 01 remains the diagnostic anchor because owner feedback exists for it, but:
- do not hard-code its expected block structure;
- do not use the owner's five-block description as implementation truth;
- use it only as post-hoc owner evidence against which generic output can later be reviewed.

Cases 02–06 remain blind with respect to owner pedagogical verdict.

## Experimental model

Introduce an isolated experimental model, e.g. `ExplanatoryStructureModel`, without changing production KnowledgeModel semantics.

Suggested shape:

```text
ExplanatoryStructureModel
  source_identity
  goal
  blocks[]
    id
    source_ranges[]
    concise_core
    explanatory_function
    semantic_support[]
    evidence_support[]
    qualifications[]
  traversal[]
    from_block
    to_block
    discourse_relation
    support
  unassigned_material[]
  diagnostics
```

Names may adapt to repository conventions.

## Meaning blocks

A meaning block is a coherent explanatory unit, not necessarily:
- a paragraph;
- a sentence;
- a claim;
- a proposition;
- one semantic item.

A block may span multiple sentences/paragraphs or split a paragraph if evidence justifies it.

Every block must remain source/provenance traceable.

## Experimental explanatory functions

Use a small domain-neutral registry. At minimum consider:

- `ORIENTATION`
- `MECHANISM`
- `CORE_IDEA`
- `CANONICAL_EXAMPLE`
- `EVIDENCE_OR_OBSERVATION`
- `SCALE_OR_TIMESCALE`
- `CONSEQUENCE`
- `SECONDARY_EXAMPLE`
- `GENERALIZATION`
- `QUALIFICATION_OR_LIMIT`
- `CONTEXT`

The implementation may refine names if needed, but must not proliferate source-specific labels.

Under uncertainty, prefer a broad function or `UNRESOLVED`; do not invent precision.

## Experimental discourse relations

Use a bounded domain-neutral set, e.g.:

- `ELABORATES`
- `EXEMPLIFIES`
- `GROUNDS`
- `EXPLAINS_WHY`
- `LEADS_TO`
- `SCALES_TO`
- `CONTRASTS_WITH`
- `QUALIFIES`
- `GENERALIZES`
- `CONTINUES`

These are explanatory/discourse relations, not production domain relationships.

Do not mutate the canonical semantic relationship registry.

## Detection evidence

Recover explanatory structure only from frozen local evidence, including where available:
- source order;
- paragraph/sentence boundaries;
- lexical/discourse cues;
- existing grounded semantic identities;
- repeated/shared entities;
- existing relationships;
- evidence spans;
- qualification/uncertainty metadata.

No model/provider calls.

No source/domain-specific rules.

Paragraph boundaries may be evidence, never identity.

## Compression views

For each case create three peer views from the same frozen substrate.

### E0 — `SOURCE_RICH`

Exact SPEC-060 R0 identity.

### E1 — `BLOCK_PRESERVING_EXPLANATION`

Compress language **within detected meaning blocks** while preserving:
- block order where supported;
- explanatory function;
- material discourse transitions/relations;
- semantic/epistemic content;
- provenance.

E1 should read as an explanation, not a list of atomic facts.

### E2 — `EXPLANATORY_OUTLINE`

Expose:
- meaning blocks;
- concise block cores;
- explanatory functions;
- traversal/discourse relations.

E2 may use headings, indentation, sequence markers, and restrained textual connectors.

E2 is not a visual diagram and must not introduce arrows/topology as a learner-facing visual grammar. The experiment concerns explanatory architecture, not visualization.

All views must derive independently from the same frozen substrate/model, not by repeatedly summarizing the previous view.

## Case-01 diagnostic comparison

The report must compare generic machine-detected case-01 structure against the owner-observed pattern without changing output after inspection.

Owner-observed pattern for audit only:

```text
mechanism
→ canonical example: Mid-Atlantic Ridge
→ slow rate + long timescale → Atlantic Ocean consequence
→ Iceland/Krafla observational example
→ Red Sea / Arabia–Africa further example
```

Classify alignment mechanically where possible:
- `ALIGNED`
- `PARTIALLY_ALIGNED`
- `MISALIGNED`
- `UNRESOLVED`

Do not claim owner approval from alignment.

## Preservation audits

Retain SPEC-060 semantic and epistemic preservation audits.

Add explanatory-preservation audits:

For every source block/transition considered materially useful, classify:
- `PRESERVED`
- `MERGED_WITHOUT_TRAVERSAL_LOSS`
- `REORDERED_WITH_JUSTIFICATION`
- `DROPPED_AS_REDUNDANT`
- `TRAVERSAL_LOST`
- `FUNCTION_CHANGED`
- `UNSUPPORTED_STRUCTURE_ADDED`
- `UNRESOLVED`

A case fails closed for experimental admission if it contains:
- material `TRAVERSAL_LOST`;
- `FUNCTION_CHANGED`;
- `UNSUPPORTED_STRUCTURE_ADDED`;
- unresolved explanatory loss affecting comprehension.

## Metrics

Word/character counts remain diagnostics, not objectives.

Report per case:
- E0/E1/E2 word and character counts;
- block count;
- source paragraphs and sentences per block;
- explanatory-function distribution;
- discourse-relation distribution;
- semantic preservation;
- epistemic preservation;
- explanatory preservation;
- provenance coverage;
- unassigned material;
- compression ratio;
- any reordering.

Add a conceptual diagnostic for reconstruction burden where mechanically approximable, but do not invent a pseudo-scientific score. Prefer descriptive counts such as:
- explicit traversal links preserved;
- block boundaries retained/merged/split;
- required cross-block relations made implicit or explicit.

## Owner-review artifact

Build a neutral six-case artifact allowing:
- E0 source-rich;
- E1 block-preserving explanation;
- E2 explanatory outline;
- preservation audit.

For E2, make block boundaries/functions/traversal legible without turning it into a diagram.

For E1, preserve natural reading flow.

Include a source-order/paragraph overlay in the audit so the owner can see how detected blocks map to source paragraphs without detective work.

## Owner-review rubric

1. **Thought flow** — Can I follow the explanation naturally?
2. **Meaning blocks** — Do blocks correspond to coherent ideas rather than sentence fragments?
3. **Traversal** — Is it clear why the explanation moves from one block to the next?
4. **Compression** — Was language removed without removing useful explanatory work?
5. **Reconstruction burden** — Am I doing more mental work than in E0?
6. **Structure utility** — Does E2 expose the system of the explanation without flattening it?
7. **Paragraph independence** — Did the compiler discover meaning blocks rather than mechanically copying paragraph boundaries?
8. **Semantic/epistemic fidelity** — Are meaning, qualification, scope, certainty and causality preserved?
9. **Recoverability** — Can every compressed block/transition be traced back?
10. **Resolution preference** — Which view is useful for first learning vs later review, if any?

Do not auto-score.

## Mechanical decision branches

Choose exactly one:

### `EXPLANATORY_STRUCTURE_SAFE_FOR_OWNER_REVIEW`

Meaning blocks/traversal can be recovered without unsupported structure and compressed views preserve semantic, epistemic and explanatory content.

### `EXPLANATORY_STRUCTURE_NOT_RECOVERABLE_OFFLINE`

Frozen evidence is insufficient to infer coherent explanatory structure without model-level interpretation.

### `BLOCKS_RECOVERABLE_TRAVERSAL_UNRELIABLE`

Coherent blocks can be detected but their explanatory relations/order cannot be safely recovered.

### `EXPLANATORY_COMPRESSION_CAUSES_RECONSTRUCTION_LOSS`

Structure is detected but E1/E2 materially increase reconstruction or lose traversal.

### `INCONCLUSIVE`

Mixed evidence prevents a clean branch.

Do not mechanically claim learning improvement.

## Required outputs

Create:

`examples/evaluations/spec-061-explanatory-structure-preservation-experiment-20260921/`

Include at minimum:
- `report.json`;
- exact six-case frozen manifest;
- `ExplanatoryStructureModel` artifacts;
- E0/E1/E2 per case;
- block/function/traversal manifests;
- semantic preservation audit;
- epistemic preservation audit;
- explanatory preservation audit;
- case-01 owner-pattern alignment audit;
- paragraph/source-range mapping;
- metrics;
- deterministic regeneration evidence;
- browser gate results;
- zero-call/zero-retrieval statement;
- owner-review command;
- owner verdict `PENDING`.

## Project vision update

Update `docs/PROJECT-VISION.md` minimally to capture the newly discovered principle:

> **Semantic preservation is necessary but not sufficient; useful explanatory structure is itself information that compression should preserve.**

The canonical pipeline should place explanatory structure between grounded knowledge and compression.

Do not otherwise expand the product ambition.

## Protected state

Do not modify:
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- canonical semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- SPEC-055–060 evidence/artifacts;
- SPEC-057 utility decisions;
- production representation strategies/renderers;
- accepted SPEC-038 baseline;
- My Map/navigation/Explore Next;
- historical evaluation evidence.

Prefer isolated experimental code/artifacts.

## Explicitly forbidden

Do not:
- call OpenAI or another model/provider;
- retrieve external sources;
- rerun extraction;
- modify production KnowledgeModel semantics;
- add discourse relations to the production semantic relationship registry;
- hard-code the owner's case-01 block sequence;
- equate paragraphs with meaning blocks;
- optimize for word count at the expense of traversal;
- implement learner personalization;
- implement podcast/video ingestion;
- implement visual grammar selection;
- redesign production UI;
- promote experimental compression/structure;
- assign the human pedagogical verdict;
- implement follow-up product changes.

## Validation

At minimum:
- focused SPEC-061 tests;
- SPEC-060 semantic/epistemic regression;
- SPEC-038/057/058/059 regressions where applicable;
- control-plane tests;
- full offline suite;
- deterministic regeneration;
- frozen-input identity verification;
- block source-range/provenance checks;
- traversal support checks;
- case-01 no-hardcoding check;
- JSON validation;
- secret safety;
- `git diff --check`;
- protected-state hashes;
- zero provider/model/network calls;
- browser gate at desktop and 390×844 with clean console and no horizontal overflow.

## Completion state

On completion:
- set SPEC-061 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report block/function/traversal distributions, case-01 alignment, preservation results, compression metrics, browser gate, tests, artifact path and owner-review command;
- stop at `OWNER_REVIEW`;
- do not promote anything or infer the human verdict.

## Owner review question

> **Can Knowledge Compiler reduce linguistic cost while preserving not only what an explanation says, but the useful path by which it makes the idea understandable?**
