# 05 — Complexity and economics, with denominator discipline

## Executable and experimental stage accounting

The core `pipeline.py` has five named orchestration operations: normalize document,
extract, deduplicate, construct/validate KnowledgeModel, validate proposition coverage.
Only extraction is inherently probabilistic in the provider path. Downstream structure
detection, representation planning/building and viewer interaction are separately
implemented consumers; this is not a count of semantic model calls.

Candidate B v2 records four evaluation stages: entity inventory, semantic structure,
claim/evidence binding (three conditional provider stages), then canonical validation
(offline). A failure can halt downstream stages; hence 26, not 27, calls on nine sources.
[evidence:M052.provider_calls_started] [evidence:M052.three_arm_summaries]

The 060–064 views are isolated deterministic experiments, not extra mandatory provider
stages in the core executable product. The 065 future harness proposes three conditional
semantic transformations per source, nine generation calls maximum for three sources.
No live candidates established that route. [evidence:M065.call_budget]
[evidence:M065.execution_integrity]

## Actual recorded live experiments

This table covers the directly comparable extraction experiments, not an exhaustive
project lifetime billing total. Historical controls are counted only once. Token and
latency fields include rejected responses where the authoritative record supplies them.

| Experiment | Actual calls | Admissions | Input / output / total tokens | Sum of recorded provider durations |
| --- | ---: | ---: | --- | ---: |
| 042 [evidence:M042.execution] [evidence:M042.usage_totals] | 3 | 1/3 | 9,754 / 8,179 / 17,933 | 71,847.705 ms |
| 045 [evidence:M045.execution] [evidence:M045.usage_totals] | 6 | 3/6 | 19,674 / 16,979 / 36,653 | 127,568.440 ms |
| A historical combined 042+045 [evidence:M048.control_a_summary] | 9 (not nine additional calls) | 4/9 | 29,428 / 25,158 / 54,586 | 199,416.145 ms |
| B v1 048 [evidence:M048.candidate_b_summary] | 19 | 2/9 | 59,160 / 35,414 / 94,574 | 312,910.941 ms |
| B v2 052 [evidence:M052.usage_total] [evidence:M052.provider_latency_ms_total] | 26 | 8/9 | 97,662 / 49,351 / 147,013 | 516,088.727 ms |

For these distinct runs only, arithmetic totals are 54 calls, 296,173 tokens and
1,028,415.812 ms (~17.14 minutes) summed provider duration. This is not elapsed project
time, concurrent end-to-end latency, all historical calls, or learner time saved.
B v2 mean recorded duration per attempted source: ~57.34 seconds; model output/trust
latency remains separate from unmeasured time-to-understanding.

The 045 frozen harness counted four constructed attempts, while the authoritative
ledger recorded six transmissions/responses. The two exact-evidence failures were not
free/no-call outcomes. This discrepancy is preserved. [evidence:M045.execution]

No monetary amount was supplied by these provider records. No price lookup or inferred
dollar figure is performed. Provider payer identity is not cost evidence.
[evidence:M042.billing] [evidence:M045.billing] [evidence:M052.monetary_cost]
Earlier experiment artifacts are indexed in the custodian manifest, but not summed
without a normalized, deduplicated authoritative all-project ledger. Prototype costs
and model identity are unknown. That missingness is not treated as zero cost.

## Projected contracts, not executed usage

| Frozen proposal | Budget | Important qualification |
| --- | --- | --- |
| 065 generation [evidence:M065.call_budget] | At most nine calls | Three conditional stages × three frozen sources, not authorized/executed here |
| 066 synthesis judging [evidence:M066.budget_summary] | 423 precision-first OR 111 bounded-batch calls | Alternative judging caps, not additive; atom/decomposition and semantic coverage assumptions unresolved |
| 067 attempted experiment contract [evidence:H067] [evidence:M067.live_calls] | Proposed 48 J1 + 12 J2 | Actual zero; atomic preflight invalid; model/provider contract not reached |
| 068 native subset [evidence:M068.future_J1_calls] [evidence:M068.future_J2_calls] | Proposed 32 J1 + 8 J2 = 40 | Actual zero; only 2/18 categories despite 8/8 domains; not representative |

The 066 423/111 projections correspond to ~47/~12.33 judge calls per nine generation
calls, not token/cost ratios. Do not multiply historical per-call token/latency means
into these proposals: model, payload, batching and proof scope differ.
No live semantic-judge quality, token, latency, cost or order/batch effect was measured.
[evidence:M067.observed_usage] [evidence:M067.observed_latency] [evidence:M067.observed_cost]

## Fail-closed and maintenance surfaces

Current local gates include normalized source identity, quote uniqueness/offset matching,
origin rules, vocabulary/schema consistency, referenced endpoints, proposition role/coverage,
structure sufficiency, parent/child scope, plan/layout correspondence and viewer selection
isolation. Their existence can prevent bad state but can also halt a learner output.
See the frozen executable inventory and [evidence:M046.reliability_separation].

Experimental contracts add coverage/recovery certificates, block/traversal membership,
implication witnesses, schema membership, preservation modes, prompt/schema hashes,
protected-state snapshots, fixture labels, atom truth/decomposition receipts, aggregation,
call budgets, raw response ledgers, order/batch identities and human review. These are
operational surfaces requiring maintenance; this dossier has no measured person-hour cost.
[evidence:M064.preservation] [evidence:M065.capability_gaps] [evidence:M066.decomposition_boundary]
[evidence:M068.scope_limit]

Counting locally checkable invariants does not establish that the whole chain is necessary,
scalable, affordable or learner-effective. Conversely, missing economic measurements are
not evidence that a component is useless. Those judgments remain open for the auditor.
