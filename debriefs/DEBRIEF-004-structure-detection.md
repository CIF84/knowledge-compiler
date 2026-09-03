# DEBRIEF-004 — Structure Detection

## Status

Accepted — yes, with limitations.

## Implementation Commit

`03040fc48b5276726c8b572e668227373d8bad22`

Pushed to canonical `origin/main`.

## Question Tested

> Can the current grounded semantic graph be composed deterministically into useful higher-order structures — such as hierarchies, causal paths, temporal/process chains, dependencies, and feedback candidates — without re-reading the source text?

## Outcome

**Yes, with limitations.**

SPEC-004 demonstrates that the current `KnowledgeModel` already contains enough structure to support useful deterministic downstream composition in multiple domains.

The detector produced useful:

- structural hierarchies;
- causal paths;
- dependency chains;
- temporal/process chains;
- feedback candidates.

The most important architectural result is that this was achieved without source re-reading, LLM calls, provider code, prompt logic, visualization libraries, or new dependencies.

The dominant limitations were not detector failures. They were inherited from upstream semantic modeling: missing or substituted endpoints, collapsed states, absent chronology edges, and missing feedback-closing relationships.

This supports the next-stage product architecture:

```text
source
  ↓
KnowledgeModel
  ↓
StructureDetector
  ↓
DetectedStructureSet
  ↓
representation layer
```

The IR is therefore sufficient to justify a minimal representation experiment, provided candidate quality and empty/missing structures remain explicit rather than being repaired invisibly.

## What Was Implemented

A deterministic downstream structure-detection layer was added:

```text
KnowledgeModel
      ↓
StructureDetector
      ↓
DetectedStructureSet
```

`DetectedStructureSet` contains validated, versioned `DetectedStructure` records with:

- stable structure IDs;
- structure type;
- entity IDs;
- supporting relationship IDs;
- relationship/predicate sequence;
- detection and deduplication metadata.

Detected structure types include:

```text
HIERARCHY
CAUSAL_PATH
PROCESS_CHAIN
DEPENDENCY_CHAIN
FEEDBACK_CANDIDATE
```

## Independent Verification

Repository review confirmed:

- implementation commit is exactly one commit after SPEC-004;
- the detector consumes `KnowledgeModel` directly;
- no provider, prompt, source-text, network, or visualization dependency is present in the detection module;
- exact duplicate source/type/target edges are collapsed into deterministic logical edges while preserving all supporting relationship IDs;
- semantic families from the canonical relationship registry drive composition;
- structural relationship types are not mixed indiscriminately;
- causal-family edges drive causal paths and feedback candidates;
- temporal composition uses explicit `PRECEDES` edges only;
- dependency paths are kept predicate-specific rather than treating all dependency relations as interchangeable/transitive;
- cycles are canonicalized deterministically;
- stable IDs are SHA-256-derived from canonical signatures;
- result ordering is explicit and deterministic;
- committed five-domain structure artifacts and human review exist.

Reported automated result:

```text
60 passed in 0.08s
```

Codex additionally reported compile checks, secret scan, diff checks, artifact reproduction, isolated-wheel installation, and installed CLI smoke tests.

The review environment did not independently rerun the local test suite; those execution results remain Codex-reported evidence.

## Detection Semantics

The implementation correctly avoided several tempting but unsafe compositions.

### Structural

`PART_OF`, `IS_A`, and `EXAMPLE_OF` are detected as separate hierarchy classes rather than merged into one generic transitive graph.

### Causal

Causal-family edges can form deterministic paths and directed feedback candidates. The detector does not invent missing causal links.

### Temporal

Only explicit `PRECEDES` relationships generate process chains. Transformation is not silently interpreted as chronology.

### Dependency

`REQUIRES`, `ENABLES`, and `CONSTRAINS` remain semantically distinct during path detection. This avoids treating the entire dependency family as one safely transitive relation.

### Interaction / descriptive

Interaction and descriptive edges are not promoted into higher-order paths merely because they connect nodes.

This is an important design property: structure detection composes semantics conservatively instead of maximizing connectedness.

## Five-Domain Evaluation

The evaluation was fully offline and used the accepted SPEC-003 models as input.

Reported result:

```text
5/5 domains met expectations
```

| Domain | Hierarchy | Causal | Process | Dependency | Feedback | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Electromagnetism | 1 | 0 | 0 | 0 | 1 | useful induction-cycle candidate, weakened by upstream state collapse |
| Software architecture | 1 | 0 | 0 | 1 | 0 | useful component hierarchy and dependency chain |
| Economics | 0 | 4 | 0 | 0 | 0 | useful branching causal paths |
| Biology | 0 | 0 | 0 | 0 | 0 | truthful absence rather than false composition |
| History | 0 | 0 | 1 | 2 | 0 | useful enablement chains; chronology endpoint remains imprecise |

## Strong Findings

### 1. The semantic IR is composable

SPEC-004 provides the first direct evidence that `KnowledgeModel` is not only a storage/interchange format. It contains enough semantic structure to support deterministic higher-order reasoning.

This materially strengthens the decision to keep `KnowledgeModel` as the central semantic IR.

### 2. Structure detection should remain downstream and deterministic where possible

The detector never re-reads source text and never calls an LLM.

This preserves a clean separation:

```text
probabilistic semantic extraction
        ↓
validated KnowledgeModel
        ↓
deterministic graph composition
```

That separation improves reproducibility, debuggability, cost, provenance, and testability.

### 3. Empty output can be correct output

Biology produced no higher-order structures because the upstream graph did not contain the required composable relationships.

This is a positive product finding, not a failure.

> The detector should expose insufficient structure honestly rather than manufacture a diagram.

That principle should carry into the representation layer.

### 4. Higher-order composition exposes upstream semantic weaknesses sharply

SPEC-004 turned previously local semantic imperfections into visible downstream consequences.

Examples:

- disconnected electromagnetism endpoints prevent the expected field → force → motion path;
- collapsed changing-field states weaken the induction feedback candidate;
- missing `Transcription PRECEDES Translation` prevents the biology process chain;
- an actor endpoint (`Authorities`) weakens historical chronology;
- economics lacks the edge needed to close a feedback loop.

This is useful: downstream composition acts as a diagnostic pressure test on the upstream IR.

### 5. Event/state modeling is now evidence-backed, but not universally blocking

Earlier entity/state/event concerns were speculative enough to defer.

SPEC-004 now provides concrete evidence that event/state distinctions materially affect process and feedback quality in at least several domains.

However, software architecture and economics still produced useful structures without an IR redesign.

Therefore:

> Event/state modeling is a real focused follow-up problem, but not a prerequisite for beginning a minimal representation experiment.

### 6. Relationship deduplication can be handled conservatively downstream

Exact duplicate semantic triples are collapsed for traversal while all original supporting IDs are retained.

This solves the immediate structure-detection problem without broadening entity deduplication or mutating the source `KnowledgeModel`.

That is a good example of placing normalization at the layer that actually needs it.

## Pedagogical Finding

Not every structurally valid pattern deserves visual prominence.

The one-edge `Light IS_A Electromagnetic wave` hierarchy is correct but adds little pedagogical value beyond the original edge.

This means the future representation layer will need a notion of **presentation usefulness or salience** separate from structural validity.

Do not fold that concern back into the detector prematurely. The detector should say what structure exists; the representation layer should decide what deserves attention.

## Determinism Finding

The implementation explicitly sorts entities, edges, paths, components, cycles, and final structures, and derives stable IDs from canonical semantic signatures.

Codex reported byte-for-byte reproducibility for the five-domain artifacts.

This establishes a useful architectural contract for downstream representation experiments: the same `KnowledgeModel` should produce the same detected structures.

## Architecture Decisions Carried Forward

### Decision: Add `StructureDetector` as a deterministic downstream layer

**Origin:** DEBRIEF-004  
**Status:** active

Structure detection consumes `KnowledgeModel`; it does not independently consume source text or provider output.

### Decision: `DetectedStructureSet` is the boundary between semantic graph and representation

**Origin:** DEBRIEF-004  
**Status:** provisional-active

The structure set is sufficient for the next representation experiment. Preserve source relationship IDs and entity IDs so representation can retain provenance.

### Decision: Structure detection composes only semantically justified relationship classes

**Origin:** DEBRIEF-004  
**Status:** active

Do not infer generic transitivity from graph connectivity alone.

### Decision: Empty or weak detected structures remain explicit

**Origin:** DEBRIEF-004  
**Status:** active

Do not use an LLM or repair heuristic merely to ensure every domain produces a visual structure.

### Decision: Keep event/state modeling as a focused follow-up concern

**Origin:** DEBRIEF-003  
**Strengthened by:** DEBRIEF-004  
**Status:** active watch

It now has concrete downstream consequences, but does not block a minimal representation experiment.

### Decision: Keep relationship vocabulary frozen

**Origin:** DEBRIEF-003  
**Strengthened by:** DEBRIEF-004  
**Status:** active

SPEC-004 found no detector problem requiring predicate expansion.

## Unresolved Questions

- What representation is most useful for each detected structure type?
- How should representation distinguish structurally valid but pedagogically weak patterns from useful explanatory models?
- How should empty structure sets be presented without pretending nothing useful exists in the source?
- Should representation operate directly on `DetectedStructureSet`, or also need selected entity/claim context from `KnowledgeModel`?
- How should provenance be surfaced interactively from structure → relationship → source span?
- When should event/state/process modeling be improved: before or after the first representation experiment?
- How should polarity eventually affect causal path and feedback interpretation?
- Should feedback candidates remain unlabeled until polarity is explicit?
- What is the minimum interactive representation that would make the electromagnetism/economics/software examples meaningfully easier to understand than JSON?

## Operating Model Findings

SPEC-004 is a fourth positive data point for the repository-centered experiment loop.

New evidence:

- not every increment needs a live LLM evaluation;
- when the active uncertainty is deterministic downstream behavior, offline accepted artifacts are the better experimental input;
- accepted outputs from one SPEC can become stable fixtures for the next architectural layer;
- the five-domain corpus continues to expose both success and weakness without growing the benchmark;
- deterministic reproduction materially reduces review ambiguity;
- explicitly attributing failures to detector vs upstream semantics prevents unnecessary local repairs.

This supports a process principle:

> Use the least probabilistic experiment that can answer the current uncertainty.

## Canonical Model Changes

This increment changes our understanding of:

```text
[x] Product / project memory
[x] Architecture
[x] Operating process
[x] Project health / risk
```

## Recommended Next Experiment

The project has now established:

```text
SPEC-001  source-grounded semantic IR
SPEC-002  real LLM extraction across domains
SPEC-003  explicit relationship semantics
SPEC-004  deterministic higher-order structure detection
```

We should now test the product thesis at the representation boundary.

The next highest-value question is:

> Can a small set of deterministic visual/interactive representations turn `DetectedStructureSet` + grounded `KnowledgeModel` context into a learning artifact that is materially easier to think with than the underlying text or JSON?

A future SPEC-005 should therefore focus on a **minimal representation experiment**, not a polished application.

It should likely support only a few structure types, preserve provenance, make weak/empty structures explicit, and use the existing five-domain artifacts as fixed inputs.

Do not add broad ingestion, accounts, persistence, simulation, or product polish yet.
