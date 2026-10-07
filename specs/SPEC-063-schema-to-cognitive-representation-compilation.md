# SPEC-063 — Schema-to-Cognitive-Representation Compilation Experiment

Status: `COMPLETED`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Final verdict

`REPRESENTATION_COMPILATION_BLOCKED_BY_INSUFFICIENT_CONCEPTUAL_ABSTRACTION`

Owner review is complete. All three P2 treatments were materially insufficient as learner representations. They reorganized or decorated largely uncompressed semantic material without producing a cognitively useful compressed knowledge architecture; too much text and information still required direct reading, and the conceptual schema remained the primary failure.

Accepted findings:

- `GROUPING_IS_NOT_ABSTRACTION`
- `REPRESENTATION_WORK_PAUSED_PENDING_CORE_COMPILER_ARCHITECTURE`

SPEC-063 is closed without promotion. Its implementation and evaluation evidence remain frozen. See `debriefs/DEBRIEF-063-schema-to-cognitive-representation-compilation.md` for the durable outcome and proposed next diagnostic boundary.

## Purpose

SPEC-062 produced a mechanically valid, provenance-supported conceptual schema, but owner review rejected the raw S1/S2 learner surfaces.

The key distinction is now explicit:

> **An internal representation may compress knowledge for the machine without being a useful representation for the learner.**

SPEC-063 freezes the SPEC-062 schema completely and tests only the projection problem:

> **Can the compiler transform a trusted conceptual schema into a learner representation whose perceptual organization mirrors the conceptual organization and reduces reconstruction work?**

This is not a schema-induction experiment, extraction experiment, or general UI redesign.

## SPEC-062 owner verdict

Record the human verdict as:

`CONCEPTUAL_SCHEMA_SUPPORTED_RAW_SCHEMA_NOT_COGNITIVELY_USEFUL`

Also record:

`S1_S2_DISTINCTION_NOT_PERCEPTIBLE`

Accepted owner findings:

- S1/S2 looked like system/debug output rather than a learner explanation;
- labels such as `MECHANISM · 6 BLOCKS`, raw block counts, repeated facts, chunk IDs, and relation ledgers exposed compiler internals rather than knowledge;
- the schema/path was not intuitively understandable;
- the difference between S1 and S2 was not perceptible in the primary learner surface;
- raw schema metadata increased rather than reduced interpretation burden;
- this does **not** invalidate the induced schema as an intermediate representation;
- the learner-facing failure is a projection/representation failure.

Canonical lesson:

> **IR is not UI. Every internal abstraction must earn learner exposure through a separate cognitive-utility test.**

## Frozen input

Use the exact frozen SPEC-062 `ConceptualSchemaModel` outputs and identities.

Do not:
- regenerate schema;
- change chunk membership;
- change hierarchy;
- add/remove schema edges;
- change implications;
- change semantic items;
- rerun extraction;
- retrieve source material;
- call a model/provider.

The experiment must be capable of proving byte/hash identity of all frozen SPEC-062 semantic/schema inputs before and after execution.

## Experimental corpus

Use exactly three diagnostic cases:

1. Geology — Understanding plate motions
2. Astronomy — How did our Solar System form?
3. Meteorology — What Is the Jet Stream?

Why these three:
- geology tests one shared mechanism with multiple manifestations/branches;
- astronomy tests preservation/perceptibility of a necessary implication;
- meteorology tests whether hierarchy can externalize organization in an information-heavy case.

No new owner interpretation of the frozen schema may be encoded into implementation. Existing owner observations are post-hoc review criteria only.

## Architecture under test

```text
FROZEN GROUNDED SEMANTICS
          ↓
FROZEN EXPLANATORY STRUCTURE
          ↓
FROZEN CONCEPTUAL SCHEMA       ← SPEC-062 IR
          ↓
COGNITIVE REPRESENTATION COMPILER  ← SPEC-063
          ↓
LEARNER REPRESENTATION
          ↓
concise prose + perceptual organization
```

The representation compiler may choose a perceptual grammar only from properties already present in the frozen schema.

## Core principle

> **Represent the organization, not the metadata describing the organization.**

Learner-facing output should make the schema perceptible without requiring the learner to read schema labels, chunk IDs, block counts, edge ledgers, or compiler terminology.

## Cognitive jobs

Treat prose, schema, and perceptual form as complementary:

- **Prose** serializes explanation and nuance.
- **Schema** determines conceptual organization.
- **Perceptual representation** externalizes organization/relationships that would otherwise need to be reconstructed mentally.

Do not force every schema into a diagram.

## Bounded representation grammar

Implement an isolated experimental grammar with only the minimum forms required by the frozen schemas.

Allowed families:

### `HIERARCHY`
Use when parent/child organization is the primary cognitive structure.

### `BRANCHING`
Use when one supported concept/mechanism organizes multiple sibling manifestations/examples/consequences.

### `SEQUENCE_OR_PROCESS`
Use when supported ordered stages or necessary implications form the primary structure.

### `CAUSAL_OR_DEPENDENCY_CHAIN`
Use when supported directed dependency/causal relations are the primary cognitive work.

### `COMPARISON`
Use only when the frozen schema contains genuine aligned contrast/comparison structure.

### `PROSE_WITH_STRUCTURE`
Use when spatial/diagrammatic externalization does not earn its complexity; preserve concise prose with restrained grouping/headings.

These are experimental representation families, not production semantic types.

Do not introduce a representation family merely because it looks attractive.

## Grammar selection

Selection must be deterministic and generic.

It may inspect only frozen schema properties such as:
- root/parent-child shape;
- branching factor;
- schema depth;
- supported relation families;
- necessary implications;
- shared mechanisms;
- sibling examples/manifestations;
- traversal/order.

It must not inspect:
- source/domain names as routing keys;
- owner comments;
- case numbers;
- expected screenshots;
- hard-coded entity names.

Produce a decision artifact explaining why each family was selected.

## Learner projection contract

The learner surface must not expose, as primary content:
- chunk IDs;
- hashes;
- block counts;
- schema-edge ledgers;
- `required_for_reconstruction`;
- internal enum names such as `EXAMPLE_OR_MANIFESTATION`;
- raw compiler relation tables;
- provenance IDs.

These may appear only in a separate audit/inspect surface.

Learner-facing labels must be derived from grounded content, not internal metadata.

## Information preservation

Every learner representation must preserve access to all frozen information, but not all information must be simultaneously visible.

Progressive disclosure is allowed.

The primary representation may surface:
- concept labels;
- concise grounded prose;
- supported relations;
- necessary implications;
- representative evidence/details.

Additional frozen detail may be available through deterministic expansion/inspection.

No semantic deletion is authorized.

## Prose requirement

Every representation must retain concise prose where prose carries nuance, qualification, or traversal more efficiently than perceptual form.

Do not convert the entire explanation into boxes/arrows.

A successful representation may be hybrid:

```text
perceptual schema
      +
concise explanatory prose
      +
recoverable detail
```

## Visual restraint

The experiment may use restrained spatial/perceptual organization, including:
- nesting;
- columns;
- branching lines;
- directed connectors;
- sequence;
- alignment;
- typographic hierarchy.

Do not add:
- decorative illustrations;
- generated images;
- icons without semantic function;
- animation;
- 3D;
- color as the sole carrier of meaning;
- visual embellishment unrelated to cognitive structure.

## Required treatments

For each of the three cases generate peer treatments:

### P0 — `EXPLANATORY_PROSE_BASELINE`
Use the frozen SPEC-061 readable explanation baseline.

### P1 — `RAW_SCHEMA_CONTROL`
Use the frozen SPEC-062 raw learner-facing schema/control sufficiently faithfully to preserve the known failure for comparison. Do not improve it.

### P2 — `COMPILED_COGNITIVE_REPRESENTATION`
New experimental learner projection compiled from the exact frozen SPEC-062 schema.

P2 must be visually/perceptually distinct from P1 if the selected grammar differs. If P2 cannot improve on P0/P1 without unsupported inference, fail closed to `PROSE_WITH_STRUCTURE`.

## Diagnostic anchors

These are post-hoc owner-review questions, not implementation rules.

### Geology
Can P2 make perceptible:
- one plate-divergence/spreading mechanism;
- multiple manifestations/examples under it;
- branch-specific consequences/evidence;
without presenting them as one flat chain?

### Astronomy
Can P2 make the necessary accumulation → sufficiently large mass → eventual star/planet formation implication perceptible rather than merely preserving endpoint facts?

### Meteorology
Can P2 make a small number of meaningful conceptual handles perceptible so the learner need not organize many independent units mentally?

## Cognitive-utility audit

For each P2 representation report:

- selected grammar;
- selection evidence;
- number of primary learner-visible conceptual units;
- number of relations externalized perceptually;
- number of necessary implications perceptually explicit;
- amount of frozen detail initially hidden but recoverable;
- prose retained;
- unsupported learner-facing statements: must be zero;
- frozen semantic/schema identity preservation;
- provenance/recoverability coverage.

Do not invent a cognitive-load score.

## Owner-review surface

Create a neutral review artifact with easy P0/P1/P2 switching.

The primary question should be perceptually obvious without scrolling into debug metadata.

For P2:
- learner content first;
- optional evidence/provenance inspection second;
- internal compiler metadata only in Audit.

The review surface must make P1 vs P2 obviously distinguishable.

Include a short neutral rubric, not a system/debug explanation.

## Owner-review rubric

1. **Immediate grasp** — Can I understand the high-level organization faster in P2?
2. **Reconstruction burden** — Does P2 remove organization I would otherwise build mentally?
3. **Conceptual fidelity** — Does perceptual organization match the knowledge rather than merely decorate it?
4. **Hierarchy/branching** — Are shared mechanisms and sibling examples perceptible where supported?
5. **Implication** — Are important directed relationships obvious?
6. **Prose complementarity** — Does prose explain nuance rather than duplicate the representation?
7. **Information access** — Can I recover detail without crowding the primary view?
8. **Restraint** — Has anything been visualized that was easier as prose?
9. **P1 distinction** — Is P2 meaningfully different from the raw schema control?
10. **Preference** — For first learning and later review, would I choose P0, P1, or P2?

Do not auto-score or infer the human verdict.

## Mechanical decision branches

Choose exactly one:

### `COGNITIVE_REPRESENTATION_SAFE_FOR_OWNER_REVIEW`
All three P2 outputs are grounded, distinct from raw schema, preserve frozen identities/information, and externalize supported schema organization without unsupported inference.

### `RAW_SCHEMA_CANNOT_BE_PROJECTED_WITH_CURRENT_GRAMMAR`
Frozen schema is valid but the bounded representation grammar cannot produce a truthful useful projection.

### `REPRESENTATION_REQUIRES_UNSUPPORTED_INFERENCE`
A useful projection would require relationships or abstractions absent from the frozen schema.

### `PROSE_REMAINS_DOMINANT`
The compiler correctly fails closed to prose/structured prose because perceptual externalization does not earn complexity.

### `INCONCLUSIVE`
Mixed mechanical evidence.

No mechanical learning claim.

## Project vision update

Update `docs/PROJECT-VISION.md` minimally to add:

> **Intermediate representation is not learner representation. Internal schema must be compiled through a separate cognitive-utility boundary before exposure.**

Clarify the architecture as:

```text
grounded semantics
→ explanatory structure
→ conceptual schema (IR)
→ cognitive representation compiler
→ learner representation
```

Do not otherwise expand ambition.

## Required outputs

Create:

`examples/evaluations/spec-063-schema-to-cognitive-representation-20261007/`

Include at minimum:
- `report.json`;
- frozen-input identity manifest;
- grammar-selection decisions;
- P0/P1/P2 artifacts for three cases;
- cognitive-utility audit;
- semantic/schema preservation audit;
- implication preservation audit;
- provenance/recoverability audit;
- diagnostic-anchor audit;
- deterministic regeneration evidence;
- browser gate results;
- zero-call/zero-retrieval statement;
- project-vision hash;
- owner-review command;
- owner verdict `PENDING`.

## Protected state

Do not modify:
- SPEC-062 ConceptualSchemaModel outputs;
- SPEC-062 chunk membership, hierarchy, edges, implications, evidence, report, or evaluation artifacts;
- SPEC-061 explanatory structures;
- SPEC-060 source/semantic substrate;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- canonical semantic vocabulary/propositions;
- grounding/provenance/validators;
- production StructureDetector;
- SPEC-055–062 historical evidence;
- SPEC-057 utility decisions;
- production representation strategies/renderers;
- accepted SPEC-038 baseline;
- My Map/navigation/Explore Next.

Prefer isolated experimental compiler/rendering code and artifacts.

## Explicitly forbidden

Do not:
- call OpenAI or another model/provider;
- retrieve external sources;
- rerun extraction;
- regenerate or repair SPEC-062 schema;
- modify frozen chunking/schema to make P2 easier;
- hard-code geology/astronomy/meteorology owner expectations;
- route on domain/source/case identity;
- invent unsupported abstractions/relations;
- delete semantic information;
- optimize word count;
- expose raw IDs/debug metadata as learner content;
- build decorative visualizations;
- implement learner personalization;
- implement podcast/video ingestion;
- promote experimental representations;
- modify production learner UI;
- assign the human verdict;
- implement follow-up product changes.

## Validation

At minimum:
- focused SPEC-063 tests;
- frozen SPEC-062 byte/hash identity checks;
- SPEC-061/062 regression tests;
- relevant SPEC-038/057–060 regressions;
- grammar-selection determinism tests;
- no-domain-routing/no-hardcoding tests;
- semantic/schema/implication preservation;
- provenance/recoverability;
- P1/P2 perceptual-distinction assertions;
- explicit absence of learner-visible raw IDs/debug metadata in P2;
- deterministic regeneration;
- JSON validation;
- secret safety;
- `git diff --check`;
- protected-state hashes;
- zero provider/model/network calls;
- browser gate at desktop and 390×844;
- browser gate must assert all three cases and all P0/P1/P2/Audit treatments load with non-empty content, P1/P2 are distinguishable, interactions work, console is clean, and no horizontal overflow occurs.

## Completion state

On completion:
- set SPEC-063 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` active packet to `NONE`;
- commit/push according to repository protocol;
- report selected grammar per case, preservation results, primary-unit counts, perceptually externalized relations/implications, browser gate, tests, artifact path, and owner-review command;
- stop at `OWNER_REVIEW`;
- do not promote or infer the human verdict.

## Owner review question

> **Can a trusted machine schema be compiled into a learner representation that makes its organization perceptible without exposing the machinery that produced it?**
