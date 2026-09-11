# SPEC-041 — Blind Source Set Freeze

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `LIVE_CALLS_EXPLICITLY_BOUNDED`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Freeze the exact three-source out-of-sample evaluation packet for the already-frozen SPEC-040 harness/compiler without executing any OpenAI/model call and without modifying the frozen compiler/harness.

SPEC-040 established and froze the generic evaluation harness at:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

SPEC-041 may select/retrieve public source material solely to construct the blind packet. It must not change the frozen harness/compiler, prompts, semantic vocabulary, representation rules, renderer behavior, evaluation criteria, or learner-facing baseline after seeing the sources.

## Scientific objective

Preserve a credible order of operations:

```text
compiler + harness frozen
        ↓
source-selection rule frozen
        ↓
three public sources selected
        ↓
exact transmitted excerpts frozen + hashed
        ↓
owner inspects source packet and call bounds
        ↓
explicit approval for exactly three model calls
        ↓
execution without implementation changes
```

This packet ends before model execution.

## Bound authority

This packet authorizes only the external retrieval required to select and freeze the public source set.

Allowed external activity:

- ordinary HTTPS GET/search/navigation required to locate the three public source documents;
- retrieval of the exact public source pages/documents selected under the rules below;
- no authenticated/private sources;
- no paid APIs;
- no OpenAI Responses API calls;
- no LLM/model/provider calls of any kind;
- no external enrichment after the exact excerpts are frozen.

Source retrieval is operational input acquisition for this packet. It does **not** authorize semantic extraction/transmission to OpenAI.

If public-source retrieval is unavailable in the execution environment, stop and report the boundary rather than substituting development fixtures or manually authored text.

## Frozen implementation constraint

Before source selection, verify that the SPEC-040 frozen harness/compiler identity is exactly:

`5622df131dc71346d5890f42ce16fe1e3e55f33a`

The repository may contain later lifecycle/documentation commits, but the executable harness/compiler used by the later blind run must remain byte-equivalent to the frozen SPEC-040 identity.

Do not edit implementation files that participate in that frozen identity.

Any implementation change after inspecting a candidate blind source invalidates the experiment and must stop the packet.

## Source-selection rule

The source-selection rule is fixed before retrieval. Do not choose sources because they appear likely to produce attractive diagrams or known representation strategies.

Select exactly one source from each of these three **previously undeveloped domain families**:

1. **Geology / Earth systems**
2. **Meteorology / atmospheric systems**
3. **Civics / institutional process**

These domain families are deliberately outside the main development corpus used for economics, electromagnetism/quantum mechanics, history of printing, software architecture, and prior synthetic/transfer cases.

### Source authority priority

For each domain family, select the first source that satisfies all eligibility rules using this authority order:

1. U.S. federal government science/institutional agency page or publication;
2. another national-government science/institutional source;
3. intergovernmental public source;
4. only if none is available, a stable openly licensed educational/reference source with clear reuse terms.

Do not use commercial tutorials, blogs, SEO pages, social media, user-generated discussions, or sources already committed in the Knowledge Compiler repository.

### Eligibility rules

Each source must:

- be English-language prose;
- be publicly accessible without authentication;
- be attributable to a stable institutional source;
- contain a contiguous explanatory passage between **300 and 650 words** after boilerplate/navigation removal;
- be primarily explanatory rather than a glossary/list/table;
- not be selected because it contains one of the project's known predicate words;
- not be from a development domain named above;
- not already appear in repository source fixtures, evaluation fixtures, prompts, tests, or baselines;
- not require images/tables to make the selected prose passage intelligible;
- contain no personal/private data;
- avoid content where incorrect simplification would create a high-stakes medical, legal, or financial decision for the owner.

Civics material should explain an institutional mechanism/process rather than provide personalized legal advice.

### Deterministic selection discipline

Within each domain family:

1. find the highest-priority eligible institutional source;
2. use the first self-contained explanatory section/passage that satisfies the length bounds;
3. do not compare multiple eligible passages for which one will produce the “best” representation;
4. once an eligible passage is found and frozen, do not replace it because of its semantic shape.

Record rejected candidates only when they failed an explicit eligibility rule. Do not record speculative representation expectations.

## Blindness / anti-contamination rules

Before freezing the packet, verify and record:

- no selected source URL/title/hash exists in repository fixtures or evaluation artifacts;
- no exact selected passage exists in repository text fixtures;
- no implementation branch is introduced based on source identity, title, domain, URL, or expected representation;
- no expected entities, relationships, structure types, or representation strategies are stored in the source packet;
- no human “answer key” is created before execution;
- source ordering is fixed independently of expected semantic difficulty.

Use packet order:

1. geology / Earth systems;
2. meteorology / atmospheric systems;
3. civics / institutional process.

## Exact source packet

Create a canonical frozen packet under:

`examples/evaluations/spec-041-blind-source-set-freeze-20260911/`

Use a machine-readable file such as `blind-source-packet.json` compatible with the SPEC-040 harness.

For each source preserve at minimum:

- stable source identifier;
- domain family;
- institutional publisher;
- canonical public URL;
- page/document title;
- retrieval timestamp;
- source page/document revision/version/date when available;
- exact selected UTF-8 passage;
- UTF-8 character count;
- word count;
- SHA-256 of exact selected passage;
- selection rule evidence;
- licensing/public-source note sufficient for experiment provenance;
- confirmation that no expected semantic/representation answer is included.

If the source is revision-addressable, freeze the revision-specific URL/version when practical.

Do not normalize or rewrite the passage beyond deterministic removal of obvious navigation/formatting boilerplate. Preserve exact punctuation and paragraph order in the transmitted text.

## Pre-execution call contract

Produce a frozen live-execution manifest derived from the SPEC-040 proposed plan but containing the exact source hashes and exact transmitted character counts.

The manifest must specify, without executing:

- provider: OpenAI Responses API;
- model: `gpt-5.6-luna`;
- exactly **3 maximum calls total**;
- exactly **1 call per frozen source**;
- frozen packet order;
- `store=False`;
- SDK retries: `0`;
- hidden retries: `0`;
- semantic retries: `0`;
- repair calls: `0`;
- canonicalization/model follow-up calls: `0`;
- external retrieval/enrichment during execution: `0`;
- prompt version: the frozen SPEC-040 plan (`spec-010-v1`) unless the frozen harness itself proves another already-frozen identifier;
- exact frozen harness/compiler identity;
- failure policy: preserve failure, no retry, continue only to the next already-approved source;
- implementation-change policy: any change to frozen compiler/harness/prompt/semantic rules after source freeze invalidates the run.

Do not estimate or promise monetary cost if unavailable. Record passage sizes so token usage can be audited after execution.

## Required checks

Before owner handoff, verify:

```text
control plane valid
frozen SPEC-040 harness/compiler identity matches
no frozen implementation file changed
exactly 3 sources frozen
3 required domain families represented in fixed order
all sources pass explicit eligibility rules
selected passages are 300–650 words each
source URLs/passages absent from existing repository development fixtures
packet contains no expected strategy/structure/entity/relationship answers
exact passage hashes recorded
exact passage text preserved
live-execution manifest contains exactly 3 maximum calls
model == gpt-5.6-luna
store == false
all retry classes == 0
no model/provider calls executed
no semantic extraction executed
no renderer/evaluation rules changed
working tree clean after commit/push
```

## Durable report

Create `report.json` in the SPEC-041 evaluation directory recording:

- selected sources and domain families;
- eligibility evidence;
- rejected candidates only where an eligibility rule failed;
- exact source/passage hashes and sizes;
- repository non-overlap checks;
- frozen harness/compiler identity check;
- files changed;
- external source-retrieval activity performed;
- explicit confirmation that OpenAI/model calls == 0;
- exact proposed three-call execution manifest path;
- deviations;
- commit/push/clean state.

## Completion state

On successful source freezing:

- set SPEC-041 to `IMPLEMENTED_AWAITING_REVIEW`;
- set `STATUS.md` active packet to `NONE`;
- preserve SPEC-038 and SPEC-039 accepted behavior;
- commit and push according to repository protocol;
- stop for owner review;
- do **not** execute any OpenAI call.

## Owner review gate

Owner/ChatGPT must review the frozen packet and exact call manifest before transmission.

The review question is:

> Are these three sources genuinely out-of-sample, selected under a non-cherry-picking rule, frozen exactly enough to make the later three-call run scientifically interpretable, and safe to transmit under the stated bounds?

Only a separate explicit approval after that review authorizes transmission of the exact frozen passages.
