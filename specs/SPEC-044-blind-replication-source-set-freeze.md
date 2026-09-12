# SPEC-044 — Blind Replication Source Set Freeze

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Prepare a second, larger blind out-of-sample source packet to test whether the SPEC-043 failure pattern replicates across unrelated material **without changing the extraction prompt, semantic contract, validator, compiler, representation logic, renderer behavior, or learner-facing baseline**.

SPEC-043 diagnosed the first three-source blind run as:

- 2 × `EXTRACTION_GRANULARITY`;
- 1 × `MODEL_ERROR`;
- 0 × `CONTRACT_GAP`;
- 0 × `VALIDATION_BUG`;
- 0 × `AMBIGUOUS`.

The owner verdict is:

`DIAGNOSIS_CONFIRMED_NO_CONTRACT_CHANGE_REPLICATION_REQUIRED`

The next question is not how to repair the system. The next question is whether undeclared-but-source-supported process/event identities recur often enough across unrelated sources to establish a systematic extraction→contract alignment problem.

This packet freezes the replication source set and exact later call contract. It performs **no model execution**.

## Scientific objective

Preserve this order of operations:

```text
SPEC-043 diagnosis accepted
        ↓
all semantic/compiler behavior remains frozen
        ↓
replication sampling rule frozen
        ↓
6 unrelated public sources selected
        ↓
exact excerpts frozen + hashed
        ↓
exact six-call manifest frozen
        ↓
OWNER REVIEW
        ↓
later packet may authorize transmission
```

The experiment must remain capable of disproving the working hypothesis.

Working hypothesis:

> If source-supported process/event identities repeatedly appear in relationships or proposition roles without corresponding entity declarations across unrelated blind sources, the extraction→contract boundary has a systematic granularity/alignment defect.

Competing outcomes must remain equally admissible:

- failures are heterogeneous and no systematic interface problem is demonstrated;
- genuine model errors dominate;
- the validator or contract reveals a new class of problem;
- most or all sources pass cleanly.

## Protected state

Before source selection, verify and record that the following remain unchanged from their accepted/frozen state:

- prompt `spec-010-v1`;
- extraction schema;
- trusted semantic vocabulary;
- declared-identity invariant;
- grounding/provenance validation;
- fail-closed behavior;
- SPEC-039 semantic-to-representation compiler rules;
- current renderer coverage;
- SPEC-038 learner-facing visual/interaction baseline;
- SPEC-040 frozen blind evaluation harness/compiler identity `5622df131dc71346d5890f42ce16fe1e3e55f33a` or byte-equivalent executable behavior already established by the repository;
- SPEC-043 taxonomy and diagnosis evidence.

Do not edit implementation files participating in those protected behaviors after inspecting candidate sources.

If frozen identities cannot be verified, stop rather than continue.

## Bound authority

This packet authorizes only ordinary public-web retrieval needed to select and freeze the six-source packet.

Allowed external activity:

- HTTPS search/navigation/GET needed to locate eligible public documents;
- retrieval of selected public source pages/documents;
- retrieval needed to reject a candidate against explicit eligibility criteria.

Not authorized:

- OpenAI Responses API calls;
- any LLM/model/provider call;
- semantic extraction;
- source transmission to a model;
- repair/retry/follow-up calls;
- authenticated/private sources;
- paid APIs;
- external semantic enrichment after an excerpt is frozen.

If public retrieval is unavailable, stop and report the boundary. Do not substitute development fixtures or authored text.

## Replication sample size

Select exactly **6** sources.

The larger sample is intentionally modest: large enough to test recurrence beyond the original two failed sources, but small enough to preserve a bounded, auditable blind experiment.

## Predeclared domain strata

Select exactly one source from each previously undeveloped domain family below, in this fixed order:

1. **Astronomy / planetary science**
2. **Ecology / environmental systems**
3. **Chemistry / materials science**
4. **Biology / organismal or cellular mechanism**
5. **Transportation / infrastructure systems**
6. **Statistics / measurement methodology**

These strata are chosen for domain diversity, not because a particular representation or predicate is expected.

Do not replace a domain after viewing source semantics merely because its material appears too easy, too hard, too sparse, or likely to produce an unattractive representation.

## Source authority priority

Within each stratum, use this authority order:

1. U.S. federal government science/institutional agency page or publication;
2. another national-government science/institutional source;
3. intergovernmental public source;
4. public university or stable institutional educational source with clear attribution;
5. only if none above is available, a stable openly licensed educational/reference source.

Do not use commercial tutorials, blogs, SEO pages, social-media posts, user-generated discussions, or material already committed in the repository.

## Eligibility rules

Each selected source must:

- be English-language prose;
- be publicly accessible without authentication;
- come from a stable attributable institution;
- provide one contiguous self-contained explanatory passage of **300–650 words** after deterministic boilerplate removal;
- be explanatory prose rather than primarily a glossary, list, table, or FAQ fragments;
- remain intelligible without requiring an image/table to supply missing semantics;
- not be selected because it contains project predicate words or an obvious desired semantic structure;
- not belong to the prior main development domains (economics, electromagnetism/quantum mechanics, history of printing, software architecture) or the SPEC-041 blind domains (geology, meteorology, civics);
- not already appear in repository fixtures, tests, prompts, baselines, or evaluation artifacts;
- contain no personal/private data;
- avoid high-stakes personalized medical, legal, or financial decision material.

## Deterministic selection discipline

Within each stratum:

1. Find the highest-priority eligible institutional source.
2. Select the first self-contained explanatory section/passage that satisfies the explicit length and eligibility bounds.
3. Do not compare eligible passages for which one is likely to create better entities, relationships, structures, diagrams, or pass rates.
4. Once frozen, do not replace a passage because of its semantic shape.
5. Record rejected candidates only when an explicit eligibility rule failed.

No human answer key, expected entity list, expected predicates, expected proposition types, expected representation strategies, or anticipated pass/fail result may be created before execution.

## Anti-contamination checks

Before finalizing each source, verify and record:

- URL/title/hash do not already occur in repository evaluation/source fixtures;
- exact selected passage does not already occur in repository text fixtures;
- no source-identity-specific branch exists in implementation;
- no expected semantic output is stored in the packet;
- no source was selected after inspecting model behavior;
- packet ordering remains the fixed domain order above.

## Canonical artifact directory

Create:

`examples/evaluations/spec-044-blind-replication-source-set-freeze-20260912/`

Required canonical artifacts:

- `blind-source-packet.json`
- `live-execution-manifest.json`
- `report.json`

Optional concise Markdown notes are permitted, but JSON artifacts are canonical.

## blind-source-packet.json requirements

For each of the six sources preserve at minimum:

- fixed ordinal 1–6;
- stable source ID;
- domain stratum;
- institutional publisher;
- canonical public URL;
- title;
- retrieval timestamp;
- revision/version/date when available;
- exact selected UTF-8 passage;
- UTF-8 character count;
- word count;
- SHA-256 of exact passage;
- authority-priority level used;
- selection-rule evidence;
- rejected-candidate evidence where applicable;
- public-source/licensing provenance note;
- explicit confirmation that no semantic or representation answer key is included.

Do not rewrite, summarize, normalize, or improve selected text beyond deterministic removal of obvious navigation/formatting boilerplate. Preserve punctuation and paragraph order.

## Frozen later execution contract

Create `live-execution-manifest.json` but do **not** execute it.

It must freeze:

- provider: OpenAI Responses API;
- model: `gpt-5.6-luna`;
- exactly **6 maximum calls total**;
- exactly **1 call per frozen source**;
- fixed source order 1–6;
- exact source hashes and transmitted character counts;
- `store=False`;
- SDK retries: `0`;
- semantic retries: `0`;
- repair calls: `0`;
- hidden/follow-up calls: `0`;
- no source-specific prompt edits;
- no implementation adaptation between calls;
- fail-closed behavior unchanged;
- full raw provider response/provenance preservation in the later execution packet.

The manifest must explicitly state that **source transmission remains unauthorized** until a later canonical execution packet is approved by the owner.

## Replication evaluation plan to freeze now

The future execution must classify outcomes using the existing SPEC-043 primary taxonomy exactly:

- `MODEL_ERROR`
- `CONTRACT_GAP`
- `EXTRACTION_GRANULARITY`
- `VALIDATION_BUG`
- `AMBIGUOUS`

Do not alter the taxonomy after observing replication outputs.

For the later six-source run, freeze these aggregate questions now:

1. How many sources pass deterministic admission completely?
2. How many sources fail closed?
3. Across all rejected semantic objects, what are the counts by SPEC-043 classification?
4. How many failures involve undeclared identities that are nevertheless materially source-supported?
5. Of those, how many are process/event reifications absent from the entity array?
6. Does the same immediate dangling-identity mechanism recur across at least two unrelated new domain strata?
7. Are genuine model errors more frequent than extraction-granularity failures?
8. Is there any evidence of `CONTRACT_GAP` or `VALIDATION_BUG`?
9. Does the replication evidence justify a narrow extraction→contract alignment experiment, or remain insufficient?

No numeric threshold should automatically authorize a contract change. The owner must review the evidence and choose the next experiment.

## Decision framework for owner review after later execution

The later owner review should distinguish these outcomes:

### A. Systematic alignment signal

If source-supported undeclared process/event identities recur across unrelated new strata, especially with otherwise valid semantics, evidence supports designing a **narrow extraction→contract alignment experiment** while preserving strict declared-identity validation.

### B. Heterogeneous failures

If failures do not recur by mechanism/classification, do not optimize the architecture around SPEC-043's two granularity cases.

### C. Model-error dominated

If unsupported semantic inventions dominate, the next problem is extraction/model reliability rather than contract alignment.

### D. Clean replication

If the new sample largely or completely passes, retain the current contract and treat the original granularity cases as insufficient evidence of a systematic defect.

This framework is diagnostic only. It does not authorize implementation changes.

## Validation

At minimum:

- validate control-plane consistency;
- verify protected/frozen identities before source selection;
- verify repository contamination checks for all six sources;
- validate exact passage word/character bounds;
- validate SHA-256 hashes;
- validate packet and manifest JSON;
- validate manifest call count and zero-retry bounds;
- run focused tests for any packet-generation tooling changed;
- run relevant control-plane tests;
- run the complete offline suite if production/test code changes occur;
- run `git diff --check`;
- run secret-safety checks;
- verify provider/model call count is exactly `0` for SPEC-044.

Prefer evidence-only artifacts. Do not add production behavior merely to construct the source packet.

## Forbidden

Do not:

- call OpenAI or another model/provider;
- transmit any selected source to a model;
- perform semantic extraction on selected sources;
- retry, repair, or enrich semantic output;
- modify prompt `spec-010-v1`;
- modify extraction schema;
- modify entity/relationship/proposition vocabulary;
- loosen or alter declared-identity validation;
- add automatic missing-entity repair;
- modify SPEC-039 strategy selection;
- add renderer coverage;
- redesign UI/navigation;
- implement Back/history;
- change SPEC-038 baseline;
- create expected semantic answers for the six sources;
- choose or reject a source based on anticipated compiler success;
- authorize or perform the later six calls;
- promote the product or assign a final architectural verdict.

## Stop conditions

Stop rather than guess if:

- protected identities cannot be verified;
- a stratum has no eligible source under the allowed authority ladder;
- source contamination cannot be ruled out;
- source retrieval requires authentication or disallowed services;
- packet construction would require a model call;
- completing the packet would require implementation adaptation after source inspection;
- exact call bounds cannot be frozen reproducibly.

Record the blocker precisely.

## Completion state

When SPEC-044 is implemented and validated:

- set this spec to `IMPLEMENTED_AWAITING_REVIEW`;
- clear the active packet in `STATUS.md` to `NONE`;
- record exact six-source packet identity and manifest hashes;
- record objective validation evidence;
- explicitly record provider/model call count `0`;
- commit and push according to repository protocol;
- stop for owner review;
- do **not** transmit any source text until a later execution packet is canonically approved.

## Owner-review question

The owner should be able to answer:

> Is this six-source packet a sufficiently blind, diverse, and uncontaminated replication sample to authorize one frozen model call per source without changing any semantic/compiler behavior?