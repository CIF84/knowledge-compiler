# DEBRIEF-003 — Relationship Semantics

## Status

Accepted.

## Implementation Commit

`a6d06bcadc58cdac3c98d0322a84508e55deaccf`

Pushed to canonical `origin/main`.

## Question Tested

> Can we define and enforce a small, domain-general relationship grammar so that valid edges preserve meaning and direction across domains rather than forcing concepts into the nearest available relationship label?

## Outcome

**Yes, materially.**

SPEC-003 introduced explicit semantic contracts for every relationship type and added only three general predicates: `AFFECTS`, `BINDS_TO`, and `TRANSFERS_TO`. Using the same provider, model, and five-domain corpus as SPEC-002, the resulting graphs improved in software architecture, economics, biology, and history while preserving the core electromagnetism mechanisms.

The experiment therefore supports this claim:

> Relationship semantics should be represented as explicit contracts, not bare enum labels.

However, improved predicate semantics did not eliminate semantic errors. The dominant remaining failures shifted from **wrong relationship type/direction** toward **wrong endpoint selection, lost polarity, duplicate edges, and weak event/state modeling**.

That shift is important. The project should not respond by continuing to expand the predicate vocabulary.

## What Was Implemented

A canonical provider-independent relationship registry was added in `relationships.py`.

Each active predicate now defines:

- semantic family;
- meaning;
- direction;
- source role;
- target role;
- appropriate usage;
- misuse/exclusion guidance;
- symmetry.

Seven semantic families were introduced:

```text
STRUCTURAL
CAUSAL
DEPENDENCY
TEMPORAL
INTERACTION
TRANSFORMATION
DESCRIPTIVE
```

The vocabulary changed from 17 to 20 predicates.

Added:

```text
AFFECTS
BINDS_TO
TRANSFERS_TO
```

No existing serialized predicate was removed or intentionally redefined.

The OpenAI extractor now builds its relationship instructions from the canonical registry and explicitly permits meaningful propositions to remain claims when no edge represents them truthfully.

The evaluation layer also gained relationship-regression metadata and direct comparison against the accepted SPEC-002 baseline.

## Independent Verification

Repository review confirmed:

- the implementation is exactly one commit after the SPEC-003 commit;
- `relationships.py` contains one canonical contract per active predicate;
- contracts explicitly encode families, directionality, source/target roles, usage, exclusions, and symmetry;
- the registry validates coverage against the active `RelationshipType` enum;
- the provider adapter imports and renders the canonical relationship grammar rather than maintaining a separate prompt vocabulary;
- prompt version is `spec-003-v1`;
- the extraction instructions explicitly prefer claims over misleading edges;
- SPEC-003 comparison and human-review artifacts are committed;
- the accepted SPEC-002 artifacts remain untouched.

Reported automated result:

```text
32 passed in 0.06s
```

Codex additionally reported clean diff validation, Python compile validation, secret scan, isolated wheel installation, installed-CLI fixture smoke testing, and round-trip validation of all five live models.

The review environment did not independently rerun local tests or live API calls; those execution results remain Codex-reported evidence.

## Live Evaluation

Provider/model remained unchanged from SPEC-002:

```text
provider: OpenAI
model: gpt-5.6-luna
prompt: spec-003-v1
```

There were no retries or hidden failed runs.

Overall verdict: **IMPROVED**.

| Domain | SPEC-003 result | Main interpretation |
| --- | --- | --- |
| Electromagnetism | MIXED | Core mechanisms preserved; `AFFECTS` improved motion semantics; duplicate edge introduced |
| Software architecture | IMPROVED | `PART_OF` and `REQUIRES` direction corrected; residual endpoint/polarity errors |
| Economics | IMPROVED | Metaphorical `EXERTS_FORCE_ON` eliminated; `MEASURED_BY` misuse remains |
| Biology | IMPROVED | Binding and transfer now represented honestly; chronology and endpoint selection remain imperfect |
| History | IMPROVED | Reversed speed and invalid transformation fixed; residual event/actor endpoint imprecision |

## Strong Findings

### 1. Explicit contracts materially improve LLM semantic behavior

The same model and corpus produced better predicate selection and direction after receiving explicit definitions and misuse guidance.

This is stronger evidence than simply adding examples to a prompt because the semantic contracts now exist as canonical project state and are programmatically rendered into the adapter instructions.

### 2. A small vocabulary expansion was sufficient

Only three new predicates were required to remove several distortions:

- `AFFECTS` provides honest directional influence without overclaiming stronger causality;
- `BINDS_TO` removes the need to misuse literal force for biological binding;
- `TRANSFERS_TO` removes the need to encode delivery as `ENABLES`.

This supports conservative ontology evolution rather than domain-specific predicate proliferation.

### 3. Claims remain an important escape hatch

The instruction to preserve a proposition as a claim when no relationship contract fits is architecturally useful.

The target is not maximum graph density. It is truthful explanatory structure.

### 4. The bottleneck moved

SPEC-002's main problem was relationship vocabulary and predicate misuse.

SPEC-003 substantially reduced that problem. Remaining errors are now concentrated around:

```text
endpoint selection
polarity preservation
duplicate relationship suppression
event / actor distinction
state / process modeling
```

Examples include:

- using `Database` where the source proposition refers to a database-access policy;
- using `Transcription` where the source names regulation of transcription;
- losing prevention polarity in an `AFFECTS` edge;
- targeting an authority actor instead of an authority-response event;
- duplicate causal relationships in electromagnetism and economics.

This means further predicate expansion is unlikely to be the highest-value next move.

### 5. Semantic families appear useful but remain lightweight metadata

The seven families provide a coherent taxonomy for later structure detection without changing the serialized `KnowledgeModel` relationship representation.

This is a useful architectural outcome: richer semantics without a schema migration.

Do not turn these families into a separate ontology framework unless a later experiment demonstrates that need.

## Complexity Finding

SPEC-003 materially increased prompt size:

```text
SPEC-002 prompt: ~1,526 characters
SPEC-003 prompt: ~9,668 characters
relationship grammar: ~7,900 characters
approximate prompt growth: ~2,035 tokens
```

Direct live-run cost remained very low, but prompt complexity is now non-trivial.

The grammar complexity is justified by the observed semantic improvement, but this establishes a new constraint:

> Future semantic improvements should not assume that adding more prompt ontology is free.

The next experiment should attempt to extract more value from the current grammar before adding predicates or significantly expanding instructions.

## Cost / Usage

SPEC-003 recorded:

```text
input tokens:  12,715
output tokens:  8,951
total tokens:  21,666
estimated cost: ~$0.0133
```

SPEC-002 successful calls recorded 12,785 total tokens at approximately `$0.0117`.

The richer grammar increased input usage substantially but absolute experiment cost remained negligible for this development loop.

## Architectural Decisions Carried Forward

### Decision: Relationship semantics have one canonical provider-independent definition

**Origin:** DEBRIEF-003  
**Status:** active

Prompt instructions, tests, and future structure reasoning should derive from the canonical relationship registry rather than maintain separate semantic definitions.

### Decision: Explicit meaning and direction are part of a relationship contract

**Origin:** DEBRIEF-003  
**Status:** active

A relationship enum name alone is insufficient semantic specification.

### Decision: Prefer truthful claims over forced edges

**Origin:** DEBRIEF-003  
**Status:** active

Graph density is subordinate to semantic correctness.

### Decision: Freeze relationship-vocabulary expansion for now

**Origin:** DEBRIEF-003  
**Status:** active until new cross-domain evidence justifies change

The current evidence does not support adding more predicates. Remaining failures are mostly not vocabulary failures.

### Decision: Semantic families remain lightweight metadata

**Origin:** DEBRIEF-003  
**Status:** active

The families are useful for organization and future structure detection, but do not yet justify a larger ontology architecture.

## Unresolved Questions

- How should the extractor preserve the correct semantic endpoint when the source relation acts through a policy, regulation, event, state, or intermediate process?
- How should negative/prevention polarity be represented without multiplying predicates?
- How should semantically equivalent duplicate edges be detected conservatively?
- Does the IR need a clearer distinction among entity, event, state/condition, and process?
- Is `MEASURED_BY` too easy to misuse, or is its remaining failure primarily an entity-modeling problem?
- Can the current semantic graph support reliable higher-order structure detection despite these remaining endpoint/state issues?
- How much of future semantic evaluation can be automated without replacing trustworthy human review with a second probabilistic judge?

## Operating Model Findings

SPEC-003 is a third positive data point for the repository-centered experiment loop.

What worked:

- prior debrief evidence directly became regression inputs;
- the same five-domain benchmark enabled a meaningful causal comparison;
- using the same provider/model isolated relationship grammar as the main changed variable;
- the SPEC successfully prevented ontology expansion from becoming open-ended;
- live semantic evaluation remained inexpensive;
- push-before-review again removed repository-state ambiguity;
- committed machine output, human review, and comparison artifacts made independent inspection straightforward.

A new process observation emerged:

> Human semantic review is becoming the most expensive cognitive step, even while model-call cost remains tiny.

Do not automate that review merely because it is manual. First determine which semantic failures can be checked deterministically or through explicit regression expectations.

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
SPEC-001  semantic IR exists
SPEC-002  real LLM can populate it
SPEC-003  explicit semantic contracts materially improve edge truthfulness
```

The remaining semantic errors are real, but predicate vocabulary is no longer the dominant blocker.

The next highest-value question should test the product's next architectural assumption rather than continue polishing extraction indefinitely:

> Can the current grounded semantic graph be composed deterministically into useful higher-order structures — such as hierarchies, causal paths, temporal/process chains, dependencies, and feedback candidates — without re-reading the source text?

A future SPEC-004 should therefore focus on **structure detection from `KnowledgeModel`**.

It should treat endpoint/state limitations as known constraints and use deterministic fixtures first. The experiment must determine whether the existing IR is already rich enough for the representation layer or whether higher-order detection exposes a concrete need for event/state modeling changes.
