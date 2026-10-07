# Knowledge Compiler — Current Status

This is the authoritative repository handoff for current work coordination. Agents must not infer active work from filename recency.

## Accepted learner-facing baseline

`SPEC-038 — dominant explanatory diagram canvas`

Owner verdict: `NEW_VISUAL_BASELINE_EXPLANATORY_ARCHITECTURE_CONFIRMED`

## Extraction state

Candidate B v2 (`spec-051-candidate-b-v2`) admitted 8/9 blind sources in SPEC-052 with zero known-invalid admission. Extraction decomposition remains unpromoted.

## Representation evidence

SPEC-057 established:

> **A representation must earn its complexity by externalizing cognitive work the learner would otherwise perform mentally.**

SPEC-058 owner verdict: `UTILITY_GATE_CONFIRMED_REPRESENTATION_FORM_REMAINS_UNRESOLVED`.

SPEC-059 owner verdict: `ENRICHED_PROSE_CONCEPT_SUPPORTED_SELECTION_MODEL_REQUIRES_REFINEMENT`.

## Progressive semantic compression direction

> **Knowledge Compiler transforms source material into trustworthy, cognition-efficient representations of knowledge at variable resolution.**

Core principle:

> **Compression is a view over knowledge, not destruction of knowledge.**

SPEC-060 established mechanically that six frozen sources can be represented at smaller R1/R2 resolutions with zero detected loss under the current semantic/epistemic audits and 100% provenance coverage.

Owner review of case 01 exposed a missing preservation dimension.

SPEC-060 owner verdict:

`SEMANTIC_CONTENT_PRESERVED_EXPLANATORY_STRUCTURE_NOT_PRESERVED`

Accepted owner findings:

- R1 mostly shortened/broke apart source prose and did not materially improve cognitive processing;
- R2 exposed information types but disrupted the natural chain of thought;
- R0's paragraphs sometimes acted as useful containers of coherent meaning;
- paragraph boundaries are evidence, not a universal semantic unit;
- the source carried useful explanatory traversal in addition to domain facts;
- preserving modeled facts while losing mechanism → example → consequence → observation/generalization flow increases reconstruction burden;
- raw word-count compression is not a sufficient objective;
- some linguistic/discourse material is useful because it tells the learner how pieces of domain knowledge fit into an explanation.

Canonical refinement:

> **Semantic preservation is necessary but not sufficient; useful explanatory structure is itself information that compression should preserve.**

> **Preserve useful explanatory work already present in the source before compressing its language.**

## Current conceptual pipeline

```text
SOURCE
  ↓
GROUNDED / TRUSTED KNOWLEDGE
  ↓
EXPLANATORY STRUCTURE
  ├─ meaning blocks
  ├─ explanatory functions
  └─ traversal / discourse relations
  ↓
CONCEPTUAL ORGANIZATION
  ├─ supported chunks
  ├─ schema / hierarchy
  └─ necessary implications
  ↓
GOAL-PRESERVING SEMANTIC COMPRESSION
  ↓
VARIABLE-RESOLUTION INFORMATION
  ↓
FURTHER COGNITIVE GAIN?
  ├─ no  → language
  └─ yes → structural/perceptual representation
               ↓
          visual grammar
```

## SPEC-061 owner verdict

`EXPLANATORY_STRUCTURE_SUPPORTED_HIERARCHY_AND_CHUNKING_INCOMPLETE`

Owner review established that SPEC-061 is a meaningful improvement over SPEC-060: block-preserving explanation can preserve natural thought flow and useful compression. Remaining gaps are hierarchical conceptual chunking and preservation of necessary implications/edges.

Key findings:
- geology: one shared spreading mechanism should organize multiple example/manifestation branches rather than a flat chain;
- astronomy: endpoint facts survived but E2 weakened a crucial implication from accumulated mass to eventual star/planet formation;
- meteorology: information density may be irreducible linguistically, while the number of independent conceptual units remains cognitively expensive;
- linguistic compression, chunk compression, and structural compression are distinct;
- traversal describes how an explanation is presented; schema describes how knowledge is organized;
- visualization remains downstream.

## SPEC-062 owner verdict

`CONCEPTUAL_SCHEMA_SUPPORTED_RAW_SCHEMA_NOT_COGNITIVELY_USEFUL`

Additional finding: `S1_S2_DISTINCTION_NOT_PERCEPTIBLE`.

Owner review rejected S1/S2 as learner representations. The surfaces exposed compiler machinery—schema enums, block counts, repeated facts, chunk IDs, and relation ledgers—rather than making conceptual organization perceptible. The raw schema may remain a useful intermediate representation, but IR is not UI.

Canonical lesson:

> **Every internal abstraction must cross a separate cognitive-utility boundary before learner exposure.**

Do not modify the frozen SPEC-062 schema in response to this verdict. The next experiment isolates projection only.

## SPEC-063 owner verdict

`REPRESENTATION_COMPILATION_BLOCKED_BY_INSUFFICIENT_CONCEPTUAL_ABSTRACTION`

Accepted findings:

- `GROUPING_IS_NOT_ABSTRACTION`
- `REPRESENTATION_WORK_PAUSED_PENDING_CORE_COMPILER_ARCHITECTURE`

All three P2 treatments were materially insufficient as learner representations. They reorganized or decorated largely uncompressed semantic material, leaving too much text and information for direct reading and failing to produce a cognitively useful compressed knowledge architecture. The primary failure remains in schema, synthesis, and conceptual abstraction rather than learner-facing visual grammar.

SPEC-063 is closed without promotion. Its evidence remains frozen.

Canonical doctrine:

> **UI exists to test the compiler, not to compensate for it.**

> **Representation work remains paused until the core compression and abstraction architecture is validated.**

## SPEC-064 owner verdict

`DETERMINISTIC_PRESERVATION_CONFIRMED_SEMANTIC_ABSTRACTION_REQUIRES_GENERATIVE_CANDIDATE`

Accepted evidence:
- deterministic machinery preserved all 141 semantic commitments and 54 implications with full backwards recovery;
- R0/R1/R2/R3 aggregate words were 1,315 / 1,275 / 1,315 / 1,576;
- carriers were 66 / 69 / 63 / 63;
- only three supported groups and two labels were produced;
- zero explanatory abstractions were earned;
- deterministic transformation is strong at trust/preservation but did not demonstrate semantic synthesis or conceptual abstraction.

Canonical division-of-labor hypothesis:

> **Generative intelligence proposes semantic synthesis and abstraction; deterministic compiler machinery validates trust boundaries and decides admission.**

This remains unvalidated until a bounded live experiment succeeds.

## SPEC-065 owner verdict

`DETERMINISTIC_TRUST_BOUNDARY_CONFIRMED_SEMANTIC_ENTAILMENT_GAP_NEXT`

Accepted findings:
- restricted deterministic proof can validate identity, provenance, schema, exact/restricted coverage, quantities and frozen structural assertions;
- 30/30 adversarial fixtures behaved as expected under those restricted proofs;
- genuinely novel synthesis/paraphrase, shared mechanism/abstraction, implicit semantic substitutions/dependencies, and relation projection onto compressed endpoints cannot be proven by lexical/structural checks;
- pretending those checks establish entailment would create a false trust boundary;
- live synthesis remains unauthorized until semantic admission is addressed.

Canonical architecture under investigation:

```text
generator candidate
      ↓
deterministic validation
      ↓
semantic entailment validation
      ↓
ADMIT / REJECT / UNCERTAIN
```

`UNCERTAIN` fails closed.

## SPEC-066 owner verdict

`SEMANTIC_JUDGMENT_REQUIRED_LIVE_JUDGE_VALIDATION_NEXT`

Accepted evidence:
- 92 frozen fixtures across eight domains;
- zero false admissions under deterministic protocols;
- Protocol A resolved 8/92 and Protocol B 16/92;
- all four genuinely semantic SPEC-065 gaps remain unresolved;
- projected synthesis judging would require 423 precision-first or 111 bounded-batch calls;
- atomization and same-family generator/judge correlated-error risks remain unresolved.

Canonical trust architecture under test:

```text
generative candidate
      ↓
deterministic validation
      ↓
semantic judgment
      ↓
ADMIT / REJECT / UNCERTAIN
```

`UNCERTAIN` fails closed. Model confidence is not proof.

## Current approved work packet

```text
specs/SPEC-067-semantic-judge-live-evaluation.md
```

Status: `APPROVED_FOR_IMPLEMENTATION`

Authority: `LIVE_MODEL_CALLS_BOUNDED`

Human gate: `OWNER_REVIEW`

Promotion: `NOT_AUTHORIZED`

## Current gate

SPEC-067 is authorized to evaluate the semantic judge itself against a frozen stratified 48-fixture subset of the SPEC-066 corpus.

Exact live authority:
- model: `gpt-6.1-sol`;
- reasoning effort: `high`;
- `store=False`;
- J1 precision-first: 48 calls, one fixture per call;
- J2 bounded-batch: 12 calls, four fixtures per call;
- maximum total: 60 calls;
- zero retries, repairs, follow-ups, synthesis calls, or adaptive prompt changes.

The 48-fixture selection, J2 batches, order-sensitivity subset, prompt/schema identities, and call order must be frozen before the first provider call.

Primary trust metric: false admission. Any permissive failure is material evidence against automatic semantic admission.

SPEC-067 does not authorize SPEC-065 synthesis generation. Same-family generator/judge correlated error cannot be resolved by this experiment and must remain explicit.

If the exact provider/model/request contract is unavailable, stop fail-closed without substitution.

## Current product question

```text
known difficult semantic fixture
      ↓
semantic judge
      ↓
ENTAILED / CONTRADICTED / UNCERTAIN
      ↓
compare against frozen truth
      ↓
Does the judge avoid false admission?
And does 4-item batching preserve that conservatism?
```

## Frozen / protected state

- BASELINE-001 through BASELINE-004;
- SPEC-038 learner-facing architecture/baseline;
- Candidate B v2 extraction/evidence;
- SPEC-052 admitted KnowledgeModels;
- SPEC-055–060 evidence/artifacts;
- SPEC-061 through SPEC-063 evidence/artifacts and owner verdicts;
- SPEC-057 cognitive-utility decisions;
- trusted semantic vocabulary/propositions;
- grounding/provenance/validators;
- StructureDetector;
- production representation strategies/renderers;
- My Map/navigation/Explore Next;
- historical evaluation evidence;
- unrelated user work.

## Explicitly forbidden

SPEC-066 offline implementation is complete; stop at owner review and do not continue without a new approved packet. Proposed future manifests grant no authority. Do not call a model/provider; execute SPEC-065 live synthesis or semantic judging; retrieve external sources; rerun extraction; modify production KnowledgeModel semantics; add discourse relations to the production semantic registry; hard-code expected abstractions; equate grouping with abstraction; optimize only for word count; implement personalization, podcast/video ingestion, presentation generation, visualization or visual-grammar selection; promote experimental work; redesign production UI; assign a human cognitive or pedagogical verdict; implement follow-up product changes.

## Coordination rule

`STATUS.md` is coordination state. The active pointer must be the exact repository path of the approved contract and metadata must agree with that contract. Completed work must not remain active.
