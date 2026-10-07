# SPEC-067 — fail-closed preflight result

Owner verdict: `PENDING`

Mechanical branch: `FIXTURE_OR_PREFLIGHT_INVALID`

Recommended next step: `FIXTURE_REDESIGN_REQUIRED`

Promotion: `NOT_AUTHORIZED`

No fixture was transmitted. No provider client was constructed. No model,
catalog, synthesis, retry, repair, or follow-up request was made. Credential
availability was checked without exposing its value; it does not cure this
contract inconsistency. Remote provider compatibility remains unverified.

## Blocking evidence

The immutable SPEC-066 corpus contains 92 fixtures: 76 opaque carriers marked
`UNRESOLVED` and 16 explicit AND fixtures containing two declared components
each (108 carriers in total). Declared components are not independently
validated exhaustive semantic atoms.

The unchanged precision-first prompt requires **one previously validated atomic
commitment per call**. The frozen protocol-C admission policy separately requires
independently validated exhaustive decomposition. Its actual receipt gate,
`admit_judge_verdicts`, returns false even for an otherwise perfectly structured
ENTAILED response unless that separate condition is established. This is an
executable boundary, not merely a documentation warning.

The frozen, category/domain-stratified proposal selects 48 fixtures covering all
18 categories and eight domains. It includes 47 opaque carriers plus
`case-023`, a two-component AND negative control. Therefore it contains **49
declared carriers**, not 48 validated atoms. Case 023 combines the exact
jet-stream assertion with the unsupported claim that every warm/cold-air meeting
produces an equally powerful jet stream. One valid conjunct must not license
the unsupported conjunct.

Executing these 48 fixture slots as 48 atomic judgments would require an
unapproved whole-fixture replacement or collapse of components. Expanding slots
to individual judgments would change the 48+12 design and budget. Treating
UNRESOLVED as validated would bypass the frozen admission boundary. None was
done. The proposed manifests explicitly remain **non-transmittable**; their
serialization is evidence of the conflict, not an executable request contract.

Independent offline inspection used the eight frozen full source texts and
evidence/rationales only. Range/hash binding, corpus/label regeneration,
prompt/schema identity, and label-metadata isolation passed. This was not a
blinded domain-expert gold adjudication and did not establish exhaustive
natural-language decomposition. Frozen labels, categories, evidence, source
texts, prompts, schemas, and historical artifacts were not repaired.

## What was and was not measured

The ledger has 60 unattempted slots: J1 48 and J2 12. The eight-item order subset
and deterministic four-fixture batches were preserved before any possible
transmission. Proposed J2 evidence reversal changes ordering only, not content.
Batching and ordering would remain confounded.

J1/J2 false admissions, true admissions, uncertainty, evidence/flag accuracy,
category failures, batching degradation, order sensitivity, usage, cost, and
latency are **unmeasured**, not zero-success metrics. There are no rejected live
responses to report. Same-family generator/judge correlated error remains
unresolved; neither generator nor judge ran.

All 2,120 protected paths retain their frozen hashes. Three pre-existing
untracked `.DS_Store` files are preserved outside the commit. No production,
UI, semantic vocabulary, validator, or representation behavior changed.

## Owner decision required

Resolve the fixture-versus-validated-atom boundary in a newly explicit contract
before any transmission. Potential design choices must preserve every conjunct
and source qualification; this result does not authorize selecting a choice,
changing frozen fixtures, introducing a whole-candidate judge, or executing any
new packet. Useful coverage and the human verdict remain pending.

Offline replay (no provider transport):

```sh
.venv/bin/python -m knowledge_compiler.spec067_judge_preflight --replay --output /tmp/spec067-preflight-review
```

Detailed immutable identities, packets, counts, and unattempted slots are in the
adjacent JSON artifacts. Validation outcomes are in `validation-record.json`.
