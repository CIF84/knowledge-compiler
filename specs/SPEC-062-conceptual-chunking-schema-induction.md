# SPEC-062 — Conceptual Chunking and Schema Induction Experiment

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

SPEC-061 established that preserving explanatory traversal is materially better than atomizing a source into independent facts, but owner review exposed a further missing layer:

> **Traversal tells us how an explanation is presented; schema tells us how the knowledge itself is organized.**

This packet tests whether Knowledge Compiler can take the frozen grounded semantics plus frozen SPEC-061 explanatory structure and induce a small, coherent, provenance-preserving conceptual schema **without deleting information and without optimizing word count**.

The experiment isolates one thesis:

> **Can structure alone reduce cognitive burden by reducing the number of independent information units a learner must organize mentally?**

No claim of learning improvement may be made mechanically.

## SPEC-061 owner verdict

Record the owner review as:

`EXPLANATORY_STRUCTURE_SUPPORTED_HIERARCHY_AND_CHUNKING_INCOMPLETE`

Accepted findings:

1. **Geology / plate motions**
   - E1 was a clear improvement and much closer to the owner's natural chain of thought.
   - Compression was genuinely useful.
   - Meaning-block structure and classification were broadly correct.
   - The remaining failure is structural: the source presents one underlying plate-spreading mechanism through multiple examples/branches.
   - Mid-Atlantic Ridge / Iceland-Krafla and Red Sea / Arabia-Africa should not merely appear as later steps in one flat chain. They are examples/manifestations organized under the same mechanism, with different consequences/evidence.

2. **Astronomy / solar-system formation**
   - Compression was useful.
   - E2 lost a crucial implication in Block 3: preserving “material sticking together forms a large mass” while omitting that, over time, the mass can form a planet or star weakens the explanation.
   - Endpoint facts are not sufficient if an implication/explanatory edge necessary for reconstruction disappears.
   - E1 preserved this better than E2.

3. **Meteorology / information-heavy source**
   - This was the least useful of the reviewed cases.
   - More aggressive linguistic compression may risk material loss.
   - The likely remaining problem is not simply too many words but too many information units without sufficiently strong conceptual organization.

4. **Emerging cognitive model — hypothesis only**
   Owner reasoning suggests four useful computational jobs:
   - attention/filtering — what deserves processing;
   - chunking — what can be handled as one coherent unit;
   - schema formation — how chunks relate and integrate with concepts;
   - later learner-specific integration/conflict resolution.

   Do **not** encode this as a literal neuroscience model or fixed cognitive-stage theory. It is an engineering decomposition to test.

5. **Compression dimensions**
   Treat these as distinct:
   - linguistic compression — fewer words/symbols;
   - chunk compression — fewer independent units requiring simultaneous handling;
   - structural compression — less relational organization the learner must reconstruct mentally.

6. **Representation implication**
   Prose remains valuable for narrative traversal. Schema externalizes organization. Visuals may later externalize selected relationships/mechanisms. These are complementary cognitive jobs, not competing style families.

## Architectural refinement

Conceptual pipeline:

```text
SOURCE
  ↓
GROUNDED SEMANTICS
  ↓
EXPLANATORY STRUCTURE
  ├─ meaning blocks
  ├─ functions
  └─ traversal
  ↓
CONCEPTUAL CHUNKING
  ↓
SCHEMA INDUCTION
  ├─ hierarchy
  ├─ shared mechanisms
  ├─ examples / manifestations
  ├─ consequences
  ├─ evidence
  └─ necessary implications
  ↓
GOAL-PRESERVING COMPRESSION
  ↓
REPRESENTATION SELECTION
```

Canonical principle to test:

> **Do not ask the learner to hold independently what can safely be organized under a shared concept or mechanism.**

## Experiment scope

Use the exact six frozen SPEC-060/SPEC-061 source identities and frozen SPEC-061 explanatory structures.

No extraction rerun.
No source retrieval.
No model/provider calls.
No production semantic changes.
No linguistic compression optimization.
No learner personalization.
No visual representation work.

Cases 01, 02, and 03 from the owner's latest review may be used only as post-hoc owner evidence:
- geology: one mechanism with multiple example branches;
- astronomy: necessary implication must survive;
- meteorology: information-heavy structure may need stronger chunking.

Do not hard-code these outcomes.

Cases not owner-reviewed remain blind.

## Experimental model

Introduce an isolated experimental `ConceptualSchemaModel` (name may vary with repository conventions) derived from frozen grounded semantics + frozen explanatory structure.

Suggested shape:

```text
ConceptualSchemaModel
  source_identity
  root_or_orientation
  chunks[]
    id
    label
    role
    member_blocks[]
    semantic_support[]
    evidence_support[]
    parent_chunk?
  schema_edges[]
    from
    to
    relation
    support[]
    required_for_reconstruction
  unassigned_blocks[]
  diagnostics
```

This is experimental evaluation state, not a production KnowledgeModel change.

## Conceptual chunks

A conceptual chunk is a coherent group that can be treated as one higher-level unit without deleting its constituent information.

A chunk may group:
- multiple explanatory blocks;
- repeated instances of the same mechanism;
- an example and its evidence;
- consequences under a common cause;
- several details under one concept.

A chunk must not group items merely because they are adjacent.

Every membership decision must be traceable to frozen evidence.

## Experimental schema roles

Use a small domain-neutral set, such as:

- `ORIENTATION`
- `CORE_CONCEPT`
- `MECHANISM`
- `PROCESS`
- `EXAMPLE_OR_MANIFESTATION`
- `EVIDENCE_OR_OBSERVATION`
- `CONSEQUENCE`
- `SCALE_OR_TIMESCALE`
- `QUALIFICATION_OR_LIMIT`
- `CONTEXT`
- `UNRESOLVED`

Do not proliferate domain-specific labels.

## Experimental schema relations

Use a bounded domain-neutral set, e.g.:

- `HAS_PART`
- `INSTANCE_OF`
- `EXEMPLIFIES`
- `MANIFESTS_AS`
- `SUPPORTED_BY`
- `LEADS_TO`
- `RESULTS_IN`
- `DEPENDS_ON`
- `QUALIFIED_BY`
- `SCALES_TO`
- `ELABORATES`

These are experimental schema relations. Do not add them to the production semantic relationship registry.

Reuse an existing grounded relation where one already expresses the necessary meaning; do not invent a parallel relation unnecessarily.

## Necessary implication preservation

Add an explicit preservation contract for explanatory/inferential edges.

A compressed/schema view fails if it preserves endpoint facts but removes a relation required to reconstruct the explanation.

Audit each material implication as:

- `PRESERVED_EXPLICITLY`
- `PRESERVED_BY_SCHEMA`
- `PRESERVED_IN_PROSE_ONLY`
- `LOST_BETWEEN_ENDPOINTS`
- `UNSUPPORTED_EDGE_ADDED`
- `UNRESOLVED`

Any material `LOST_BETWEEN_ENDPOINTS` or `UNSUPPORTED_EDGE_ADDED` fails closed.

## Primary experimental constraint: zero semantic deletion

SPEC-062 is **not a text-shortening experiment**.

All frozen semantic items, qualifications, epistemic status, explanatory blocks, and material implications must remain available.

Do not target a lower word count.

The test is whether the same information can be reorganized into fewer top-level conceptual units and clearer relations.

If additional labels/connectors make the experimental schema textually longer, that is allowed.

## Peer views

Generate three peer views from the same frozen substrate.

### S0 — `EXPLANATORY_BASELINE`

Exact frozen SPEC-061 E1 identity where available as the readable explanatory baseline.

### S1 — `CHUNKED_SCHEMA`

Expose a restrained hierarchical textual schema:
- top-level chunks;
- nested constituent blocks/items;
- schema roles;
- supported relations;
- necessary implications.

No facts may be removed.

### S2 — `SCHEMA_WITH_TRAVERSAL`

Compose the induced conceptual schema with the frozen explanatory traversal:
- preserve how the explanation is read;
- expose where traversal moves within a chunk versus across conceptual branches;
- show shared mechanisms above multiple examples when supported;
- preserve necessary implication edges.

S2 should test whether hierarchy and narrative path can coexist.

These are evaluation surfaces, not production UI.

## No visual-diagram shortcut

Do not solve the experiment by building a graph canvas, mind map, arrows, or polished diagram.

Hierarchy may be expressed with indentation, nesting, restrained connectors, and textual relation labels.

The question is whether the schema is correct/useful before visual grammar is introduced.

## Metrics

Word count remains diagnostic only.

Report per case:

- frozen semantic item count;
- explanatory block count;
- top-level conceptual chunk count;
- total conceptual chunk count;
- schema depth;
- schema edge count;
- material implication count;
- implications preserved/lost;
- blocks grouped under shared parent concepts;
- independent top-level units before vs after;
- unassigned blocks/items;
- unsupported grouping/edge count;
- semantic preservation;
- epistemic preservation;
- explanatory preservation;
- provenance coverage;
- S0/S1/S2 word and character counts for transparency only.

### Chunk compression diagnostic

Compute a transparent structural diagnostic:

```text
top_level_unit_ratio =
  top_level_conceptual_units_after /
  explanatory_blocks_before
```

Do not treat lower as automatically better.

A low ratio achieved through unsupported grouping is failure.

Do not invent a cognitive-load score.

## Post-hoc diagnostic anchors

After outputs are frozen, compare generic results to owner observations.

### Geology

Check whether the induced schema recognizes, where supported:
- a shared plate-spreading/divergence mechanism;
- Mid-Atlantic/Iceland-Krafla as one manifestation/example branch;
- Red Sea/Africa-Arabia as another manifestation/example branch;
- branch-specific consequences/evidence.

Classify:
- `ALIGNED`
- `PARTIALLY_ALIGNED`
- `MISALIGNED`
- `UNRESOLVED`

### Astronomy

Check whether the necessary implication linking accumulation/large mass to eventual star/planet formation remains reconstructable.

### Meteorology

Check whether conceptual chunking reduces the number of independent top-level units without deleting facts or manufacturing hierarchy.

Owner observations are audit references only and must not influence the generic induction algorithm.

## Preservation audits

Retain:
- semantic preservation;
- epistemic preservation;
- explanatory preservation;
- provenance/recoverability.

Add:
- chunk membership support audit;
- schema-edge support audit;
- necessary-implication preservation audit;
- top-level-unit reduction audit.

Fail closed for:
- material semantic omission;
- epistemic strengthening/drift;
- explanatory traversal loss;
- unsupported chunk membership;
- unsupported schema edge;
- material implication loss;
- invented hierarchy;
- provenance loss.

## Owner-review artifact

Create a neutral six-case review surface allowing comparison of:
- S0 explanatory baseline;
- S1 chunked schema;
- S2 schema + traversal;
- audit.

The owner should be able to see:
- what was grouped;
- why it was grouped;
- what remained independent;
- hierarchy depth;
- where implications are preserved;
- source/provenance mapping.

Avoid visual polish or diagrams that could bias the review.

## Owner-review rubric

1. **Chunk quality** — Do grouped items genuinely belong together?
2. **Top-level burden** — Does the schema reduce how many independent things I must hold in mind?
3. **Hierarchy** — Does parent/child organization reflect the concept rather than source order?
4. **Shared mechanisms** — Are multiple examples correctly organized under common mechanisms where appropriate?
5. **Implications** — Are crucial “A therefore/eventually B” relationships preserved?
6. **Traversal** — Can I still follow the explanation naturally?
7. **Schema utility** — Does the organization make retrieval/synthesis easier?
8. **Over-grouping** — Has useful distinction been hidden inside an overly broad chunk?
9. **Under-grouping** — Am I still presented with too many sibling units?
10. **Fidelity** — Are semantics, scope, uncertainty, causality and provenance unchanged?
11. **First learning vs review** — Which view is preferable for first exposure and which for later retrieval?

Do not auto-score or infer owner verdict.

## Mechanical decision branches

Choose exactly one:

### `CONCEPTUAL_SCHEMA_SAFE_FOR_OWNER_REVIEW`

Supported chunking/schema reduces independent top-level units on at least some sources while preserving all protected information and implications.

### `CHUNKING_SUPPORTED_SCHEMA_RELATIONS_UNRELIABLE`

Useful grouping is recoverable but relations/hierarchy cannot be induced reliably offline.

### `SCHEMA_INDUCTION_ADDS_UNSUPPORTED_STRUCTURE`

The experiment requires hierarchy/edges not justified by frozen evidence.

### `NO_STRUCTURAL_COMPRESSION_GAIN`

Safe schema induction does not materially reduce independent conceptual units.

### `INCONCLUSIVE`

Mixed evidence prevents a clean branch.

No mechanical learning claim.

## Recommended next-step vocabulary

Choose exactly one:
- `OWNER_REVIEW_REQUIRED`
- `SCHEMA_POLICY_REFINEMENT`
- `COGNITIVE_COMPRESSION_EXPERIMENT`
- `MORE_DIAGNOSIS_REQUIRED`

No follow-up implementation is authorized.

## Project vision update

Update `docs/PROJECT-VISION.md` minimally to capture, without overstating validation:

- linguistic, chunk, and structural compression are distinct;
- explanatory traversal and conceptual schema are distinct but complementary;
- the compiler should preserve useful explanatory work while reducing avoidable reconstruction;
- visualization remains downstream of schema/representation selection.

Do not add learner personalization as a current capability.

## Required outputs

Create:

`examples/evaluations/spec-062-conceptual-chunking-schema-induction-20261007/`

Include at minimum:
- `report.json`;
- exact frozen six-case manifest;
- `ConceptualSchemaModel` artifacts;
- S0/S1/S2 artifacts per case;
- chunk membership manifest;
- schema edge manifest;
- implication-preservation audit;
- semantic/epistemic/explanatory preservation audits;
- provenance audit;
- top-level-unit metrics;
- geology/astronomy/meteorology post-hoc alignment audits;
- deterministic regeneration evidence;
- browser gate results;
- zero-call/zero-retrieval statement;
- project-vision identity/hash;
- owner-review command;
- owner verdict `PENDING`.

## Protected state

Do not modify:
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- canonical semantic vocabulary/propositions;
- grounding/provenance/validators;
- production StructureDetector;
- SPEC-055–061 evidence/artifacts;
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
- hard-code owner-reviewed geology/astronomy/meteorology structures;
- delete semantic items to improve chunk metrics;
- optimize for word count;
- invent a cognitive-load score;
- implement learner modeling/personalization;
- implement conflict-resolution/memory models;
- implement podcast/video ingestion;
- implement visual diagrams/graph canvas/mind maps;
- implement visual grammar selection;
- redesign production UI;
- promote experimental schema/chunking;
- assign the human pedagogical verdict;
- implement follow-up product changes.

## Validation

At minimum:
- focused SPEC-062 tests;
- SPEC-061 regression and frozen-identity checks;
- SPEC-060 semantic/epistemic regressions;
- relevant SPEC-038/057–059 regressions;
- control-plane tests;
- full offline suite;
- deterministic regeneration;
- chunk membership support checks;
- schema-edge support checks;
- implication preservation checks;
- no-hardcoding checks for owner-reviewed anchors;
- JSON validation;
- secret safety;
- `git diff --check`;
- protected-state hashes;
- zero provider/model/network calls;
- browser gate at desktop and 390×844 with clean console and no horizontal overflow.

## Completion state

On completion:
- set SPEC-062 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report chunk/schema distributions, top-level-unit ratios, implication preservation, anchor audits, browser gate, tests, artifact path and owner-review command;
- stop at `OWNER_REVIEW`;
- do not promote anything or infer the human verdict.

## Owner review question

> **Can Knowledge Compiler make the same information easier to think with by organizing it into fewer coherent conceptual units, before deleting a single fact or drawing a single diagram?**
