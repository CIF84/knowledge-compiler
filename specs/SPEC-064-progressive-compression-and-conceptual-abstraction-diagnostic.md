# SPEC-064 — Progressive Compression and Conceptual Abstraction Diagnostic

Status: `DRAFT`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_AND_CHATGPT_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Authorization state

This document is a proposed architecture-reset packet. It is not an active work packet and does not authorize implementation, evaluation execution, model/provider calls, source retrieval, or production changes.

Activation requires explicit owner and ChatGPT approval plus a matching `STATUS.md` pointer and control header.

## Purpose

SPEC-063 preserved trusted information and projected its frozen schema into several perceptual forms, but owner review found that all three learner representations remained materially insufficient.

The failure was not primarily visual polish. The compiler reorganized largely uncompressed semantic material without producing a sufficiently compressed knowledge architecture.

SPEC-064 therefore moves the experiment upstream and asks:

> **Can grounded source material be progressively transformed into fewer, stronger conceptual handles while preserving meaning, implications, explanatory context, provenance, and backwards recoverability?**

This is a compiler architecture diagnostic, not a learner-interface experiment.

## Prior owner verdict

Record SPEC-063 as:

```text
REPRESENTATION_COMPILATION_BLOCKED_BY_INSUFFICIENT_CONCEPTUAL_ABSTRACTION
```

Accepted findings:

```text
GROUPING_IS_NOT_ABSTRACTION
REPRESENTATION_WORK_PAUSED_PENDING_CORE_COMPILER_ARCHITECTURE
```

## Frozen corpus

Use exactly the same three sources and committed identities used by SPEC-063, in this order:

### 1. Geology — Understanding plate motions

```text
source_id: usgs-divergent-plate-boundaries-1996
source_sha256: a9539d135ff1577d7e2791d498b92f55239175565b925b24aec2ed0bf633f186
document_id: text-a9539d135ff1577d
spec062_case_identity: spec062-case-8b1c200c2a20a2
spec062_model_file_sha256: 65a39024a5b74bb099b9a5656c95eaf15042fedd7a322eca35b080ecca29a006
```

### 2. Astronomy — How did our Solar System form?

```text
source_id: nasa-solar-system-formation-2026
source_sha256: c0cb2519673b8f3ef23c0be2856e03790f53d44971cbff09d593190ab3fa155d
document_id: text-c0cb2519673b8f3e
spec062_case_identity: spec062-case-10f36869d722e6
spec062_model_file_sha256: 4e3d0b9c9bb3cfe4f535cf749f55f124cd753055a526eb0dfae6573a16ee00fa
```

### 3. Meteorology — What Is the Jet Stream?

```text
source_id: noaa-nesdis-jet-stream-2025
source_sha256: 256ade61be620cfaa7b1327e3c982576611dd29b6a1fb42217d86ffdc0783ca1
document_id: text-256ade61be620cfa
spec062_case_identity: spec062-case-36e0b4a5d75932
spec062_model_file_sha256: a69ce37ac59bacab57e37b85929d4522d1e1a6cb2060104b995720d5c92107ac
```

The committed source, semantics, epistemic status, evidence, explanatory structure, material implications, and provenance are frozen. No retrieval, extraction rerun, semantic repair, or schema repair is permitted.

## Architecture under diagnosis

Evaluate this explicit progressive ladder:

```text
R0 SOURCE
  ↓ linguistic compression
R1 ESSENTIAL PROSE
  ↓ semantic synthesis
R2 SYNTHESIZED KNOWLEDGE
  ↓ conceptual abstraction + schema formation
R3 CONCEPTUAL ARCHITECTURE
```

Every stage must derive from the same frozen grounded substrate. The ladder must not be implemented as destructive chained summarization. Each stage must remain backwards-recoverable to the richer frozen layer and exact evidence.

## Distinct compiler operations

The diagnostic must evaluate these operations separately rather than treating them as synonyms.

### Linguistic compression

Reduce wording, repetition, and discourse overhead without silently changing or merging distinct semantic commitments.

Evidence of success is lower language cost with preserved semantic units, epistemic force, implications, context, and provenance.

### Semantic synthesis

Combine overlapping or mutually explanatory semantic items into a smaller set of synthesized knowledge statements.

Every synthesis must declare:

- the exact frozen semantic items it covers;
- the relationship that permits synthesis;
- preserved qualifications and epistemic status;
- material implications retained;
- exact backwards recovery links;
- why the synthesis is more than shorter wording.

### Conceptual abstraction

Introduce a grounded higher-order conceptual handle only when that handle explains multiple supported items through a shared mechanism, rule, dependency, contrast, constraint, or causal principle.

A conceptual handle is valid only if it:

- has a concise grounded definition;
- explains why its members belong together;
- carries more explanatory power than a heading or container label;
- reduces the number of independent units the learner must reconstruct;
- preserves access to every member and its evidence;
- introduces no unsupported inference or strengthened certainty.

### Schema formation

Organize validated conceptual handles and remaining irreducible items into supported hierarchy, branching, mechanism, dependency, sequence, or causal structure.

Schema formation must not be credited with abstraction merely because it places existing items in groups.

## Required treatments

Generate all four peer resolutions independently from the frozen substrate.

### R0 — `SOURCE`

Exact frozen source text for the diagnostic scope. No rewriting.

### R1 — `ESSENTIAL_PROSE`

Compact grounded prose that removes linguistic redundancy while retaining every material semantic commitment, qualification, implication, explanatory dependency, and provenance link.

### R2 — `SYNTHESIZED_KNOWLEDGE`

A smaller set of explicit synthesized knowledge statements. Each statement must include its covered semantic-item set and backwards-recovery trace.

R2 must demonstrate unit reduction through synthesis, not sentence shortening alone.

### R3 — `CONCEPTUAL_ARCHITECTURE`

A minimal text/ASCII architecture of validated conceptual handles and their supported relationships. R3 may retain concise prose where nuance is irreducible.

R3 must demonstrate whether higher-order abstractions explain membership and reduce reconstruction, rather than merely hiding items behind labels or disclosure.

## Minimal representation constraint

Use text and restrained ASCII only.

Permitted forms include:

```text
MECHANISM
  input/condition
      ↓
  transformation
      ↓
  outcome
```

```text
SHARED PRINCIPLE
  ├─ manifestation A
  ├─ manifestation B
  └─ consequence C
```

```text
CAUSE → MEDIATOR → EFFECT
```

```text
WHOLE
  ├─ component
  └─ component
```

The ASCII surface exists only to expose whether the compiler produced useful mechanisms, hierarchy, branching, dependencies, and causal structure. No polished learner UI, visualization system, animation, decorative styling, or new representation grammar is authorized.

## Grouping-versus-abstraction diagnostic

For every proposed R3 conceptual handle, record:

- handle statement;
- grounded definition;
- members covered;
- supported membership explanation;
- shared mechanism/rule/dependency/contrast/constraint, if any;
- semantic-unit reduction attributable to the handle;
- material implications carried by the handle;
- details hidden initially but backwards-recoverable;
- evidence and provenance coverage;
- unsupported inference count.

Classify each handle as exactly one of:

```text
EXPLANATORY_ABSTRACTION
SUPPORTED_GROUPING_ONLY
LABEL_ONLY
UNSUPPORTED
```

`SUPPORTED_GROUPING_ONLY` and `LABEL_ONLY` do not count as conceptual abstraction or cognitive compression.

## Measurements at every resolution

For R0, R1, R2, and R3, report per case and in aggregate:

- word count;
- character count;
- explicit semantic-unit count;
- material implication count;
- qualification/epistemic-status preservation;
- explanatory-context preservation;
- redundancy removed, with a deterministic definition and trace;
- conceptual-handle count;
- explanatory-abstraction count;
- supported-grouping-only count;
- provenance coverage;
- backwards-recovery coverage;
- unsupported inference count;
- material omission count.

Compression ratios are evidence, not automatic success. A shorter stage fails if it loses, strengthens, detaches, or obscures required information.

## Preservation contract

Across all stages preserve:

- every material source-grounded semantic commitment;
- epistemic status and uncertainty;
- qualifications and scope;
- every identified material implication;
- explanatory context needed to understand relationships;
- exact evidence and source identity;
- backwards recoverability to the richer frozen stage and source.

Fail closed on any material omission, unsupported synthesis, invented abstraction, strengthened causality/certainty, provenance break, or irrecoverable detail.

## Deterministic-versus-bounded-generation decision gate

The diagnostic must first test the best bounded deterministic machinery that can be implemented without domain/source/case routing.

After the deterministic R1/R2/R3 candidates and audits are frozen, choose exactly one architecture finding:

### `DETERMINISTIC_COMPILATION_ADEQUATE`

Deterministic machinery produces grounded synthesis and explanatory abstractions across all three cases with preservation and measurable unit reduction.

### `BOUNDED_MODEL_CANDIDATE_REQUIRES_SEPARATE_AUTHORIZATION`

Deterministic machinery preserves information but cannot produce adequate synthesis or abstraction. A later packet may propose an exact bounded model-generated candidate plus deterministic validation. This branch does not authorize a model call.

### `CURRENT_SUBSTRATE_INSUFFICIENT_FOR_ABSTRACTION`

The frozen substrate lacks information required to support the abstractions needed for a useful architecture.

### `INCONCLUSIVE`

Evidence is mixed or the diagnostic cannot distinguish algorithmic limitation from substrate limitation.

Do not prejudge this decision. No model-generated candidate may be produced under SPEC-064 unless a later approved revision explicitly changes authority and freezes the exact live-call contract.

## Required artifacts if authorized

Create an isolated evaluation directory containing at minimum:

- frozen-input identity manifest;
- R0/R1/R2/R3 text artifacts for all three cases;
- per-stage measurement table;
- linguistic-compression audit;
- semantic-synthesis audit;
- conceptual-abstraction audit;
- grouping-versus-abstraction classifications;
- schema-formation audit;
- semantic/epistemic preservation audit;
- implication/explanatory-context preservation audit;
- provenance/backwards-recovery audit;
- deterministic-versus-bounded-generation decision artifact;
- deterministic regeneration evidence;
- zero-call/zero-retrieval statement;
- owner-review rubric;
- final machine report with owner verdict `PENDING`.

The owner-review surface should be plain Markdown, text files, or a minimal unstyled local text/ASCII page. It must not become a UI-design task.

## Mechanical decision branches

Choose exactly one result for the progressive ladder:

```text
PROGRESSIVE_ABSTRACTION_SAFE_FOR_OWNER_REVIEW
GROUPING_REMAINS_NON_ABSTRACTIVE
COMPRESSION_BREAKS_PRESERVATION
ABSTRACTION_REQUIRES_UNSUPPORTED_INFERENCE
CURRENT_SUBSTRATE_INSUFFICIENT_FOR_ABSTRACTION
INCONCLUSIVE
```

Record the separate deterministic-versus-bounded-generation architecture finding without treating it as an owner verdict.

## Owner-review questions

For each case and resolution:

1. Does R1 reduce reading cost without changing the knowledge?
2. Does R2 express fewer genuine semantic units rather than shorter sentences?
3. Does each R3 handle explain why its members belong together?
4. Does R3 reduce reconstruction work compared with R0/R1/R2?
5. Is hidden detail genuinely recoverable rather than silently omitted?
6. Are important qualifications, implications, and explanatory context still perceptible?
7. Is the ASCII architecture revealing compiler quality rather than compensating for weak abstraction?

Codex must not assign the subjective owner verdict.

## Protected state

Do not modify:

- SPEC-063 implementation or evaluation evidence;
- SPEC-062 schema, chunking, hierarchy, edges, implications, semantics, or evidence;
- SPEC-061 explanatory structure;
- SPEC-060 source/semantic substrate;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- trusted semantic vocabulary, propositions, grounding, provenance, or validators;
- production StructureDetector, representation strategies, renderers, or learner UI;
- SPEC-038 or BASELINE-001 through BASELINE-004;
- navigation, My Map, or Explore Next;
- historical evidence and owner verdicts.

## Explicitly forbidden

Do not:

- call a model/provider;
- retrieve a source;
- rerun extraction;
- repair the frozen schema;
- route on source, domain, case identity, owner comments, or expected answers;
- invent facts, implications, abstractions, or relationships;
- delete or irreversibly hide semantic information;
- optimize word count at the expense of preservation;
- build a polished learner UI or visualization;
- add a representation grammar;
- personalize outputs;
- modify production behavior;
- promote an experiment;
- assign a human cognitive or pedagogical verdict.

## Validation if authorized

At minimum:

- exact frozen-input identity checks before and after;
- focused SPEC-064 tests;
- SPEC-060 through SPEC-063 regression tests;
- semantic, epistemic, qualification, implication, explanatory-context, and provenance preservation;
- backwards-recovery checks at every stage;
- no-domain-routing/no-hardcoding checks;
- grouping-versus-abstraction negative controls;
- deterministic regeneration;
- JSON/text artifact validation;
- secret safety;
- `git diff --check`;
- complete offline suite;
- zero provider/model/network calls;
- evidence-tree hash verification for all protected experiments.

## Completion state if authorized

On implementation completion:

- set SPEC-064 to `IMPLEMENTED_AWAITING_REVIEW`;
- clear `STATUS.md` to `NONE`;
- commit/push according to repository protocol;
- report per-stage measurements, preservation results, abstraction classifications, the mechanical branch, and the deterministic-versus-bounded-generation finding;
- stop at owner review;
- do not promote or infer the human verdict.

## Decision required before implementation

Owner and ChatGPT must review whether this diagnostic cleanly isolates the compiler layers, whether the preservation contract is feasible without conflating recovery with primary-view clutter, and whether the deterministic decision gate is sufficiently bounded.

Until that review is complete, SPEC-064 remains a draft and must not be executed.
