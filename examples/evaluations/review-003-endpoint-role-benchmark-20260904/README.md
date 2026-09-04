# REVIEW-003 STEP 1 — Offline Endpoint-Role Benchmark

## Result

`SUFFICIENT_FOR_BOUNDED_SPEC_015_EXPERIMENT`

The repository contains enough already reviewed evidence for one fair, frozen, exploratory SPEC-015 endpoint-role experiment. The packet contains ten historical cases: five endpoint-role failures and five accepted positive controls. No label was created from a new judgment made for this packet.

This is not evidence for production readiness. The sample is small, partly correlated, historically heterogeneous, and concentrated in the frozen quantum source.

No live call was made. No endpoint-role model or judge was implemented. No external enrichment was used.

## Artifacts

- `endpoint-role-packet.json` — frozen inputs, binary gold labels, predicate-role contracts, source hashes, exact locators, and future-call blinding rules
- `validation-report.json` — automated integrity results, manual provenance validation, fairness decision, and limitations

The packet SHA-256 is:

```text
cbbef7b3eca555c4691024f987d6ba04be6cb6091d90d91d2121290782591088
```

## Negative cases

| Case | Preserved candidate | Exact independent provenance | Why inadequate |
|---|---|---|---|
| Economics comparison | `quantity-demanded CAUSES shortage` | `examples/evaluations/spec-009-resolution-strategy-20260903/repository-semantic-review.json`, `run_reviews.variable-market-price.generic_detail.findings[0]`; accepted correction in `examples/evaluations/spec-010-proposition-modeling-20260903/comparison.json` and `debriefs/DEBRIEF-010-proposition-and-endpoint-modeling.md` | The causal antecedent is the compound condition `quantity-demanded > quantity-supplied`, not one operand. |
| Pauli constraint | `pauli-exclusion-principle CONSTRAINS electron` | `examples/evaluations/spec-012-staged-semantic-compilation-20260904/staged-semantic-review.json`, item `r12`; `reviews/REVIEW-003-endpoint-role-compression.md`, Case A | The constrained unit is the implicit joint atomic state / quantum-number assignment, not the electron participant. |
| Transfer destination | `order-command TRANSFERS_TO order-command-transfer` | `examples/evaluations/spec-009-resolution-strategy-20260903/repository-semantic-review.json`, `run_reviews.process-order-workflow.process_stages.findings[1]`; accepted correction in `examples/evaluations/spec-010-proposition-modeling-20260903/comparison.json` and `debriefs/DEBRIEF-010-proposition-and-endpoint-modeling.md` | The transfer event was substituted for the absent destination `order-component`. |
| Tunneling to electron | `quantum-tunneling ENABLES electron` | `examples/evaluations/spec-011-quantum-real-source-20260904-run-002/repository-semantic-review.json`, finding for `rel-tunneling-enables-electron-penetration`; `reviews/REVIEW-003-endpoint-role-compression.md`, Case B | The enabled unit is electron penetration through a barrier, not the electron object. |
| Tunneling to transistor | `quantum-tunneling ENABLES transistor` | `examples/evaluations/spec-012-staged-semantic-compilation-20260904/staged-semantic-review.json`, item `r9`; `reviews/REVIEW-003-endpoint-role-compression.md`, Case C | An available application/device symbol replaced the source-supported penetration process/outcome. |

## Positive controls

| Case | Preserved candidate | Exact independent provenance | Context that must not trigger rejection |
|---|---|---|---|
| API containment | `api-component PART_OF modular-order-processing-service` | `examples/evaluations/spec-003-relationship-semantics-20260903/review.json`, `domains.software_architecture.known_regressions_fixed` | Database, order component, and payment component are sibling context. |
| Amino-acid transfer | `amino-acid TRANSFERS_TO ribosome` | `examples/evaluations/spec-003-relationship-semantics-20260903/review.json`, `domains.biology.known_regressions_fixed` | Transfer RNA is the contextual carrier. |
| Correspondence constraint | `correspondence-principle CONSTRAINS quantum-mechanics` | `examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904/canonical-semantic-review.json`, item `relationship-56b4330de6aef867` | Classical physics supplies limit context. |
| Double-slit result | `double-slit-experiment CAUSES interference-pattern` | `examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904/canonical-semantic-review.json`, item `relationship-05b19ee4b6d50060` | Photon/light is experiment context. |
| Polymerase binding | `rna-polymerase BINDS_TO dna` | `examples/evaluations/spec-003-relationship-semantics-20260903/review.json`, `domains.biology.known_regressions_fixed` | Gene is contextual location. |

The controls cover five predicates across causal, dependency, interaction, and structural families. Every positive assertion contains at least one additional participant, so a judge cannot pass by rejecting every compressed relationship or by treating any dropped participant as fatal.

## Fair-use protocol for a future SPEC-015

Gold and provenance remain in the repository packet, but they must not be sent to a future judge. Construct the judge input exactly from:

- the top-level `predicate_contracts`;
- each case's `blind_id`;
- `assertion.statement`, `assertion.participant_symbol_ids`, and `assertion.evidence`;
- `symbols`; and
- the proposed `candidate.source_entity_id`, `candidate.relationship_type`, and `candidate.target_entity_id`, ordered by `blind_id`.

Exclude case names, labels, classifications, defect descriptions, endpoint diagnostics, positive-control explanations, provenance, and the historical candidate ID, statement, confidence, and origin. Candidate IDs and statements can themselves disclose the historical defect—for example, by naming a missing process or acknowledging a target mismatch. The neutral order is frozen by ranking `SHA-256(case_id)` lexicographically, so it is reproducible and not grouped by label.

## Validation

All 125 integrity checks passed. They verified source artifact hashes, exact evidence slices, exact candidate preservation, preserved assertion equality, symbol resolution, predicate contracts, neutral IDs, balance, contextual-positive construction, provenance existence, and predicate-family coverage. Each gold label was then checked manually against the cited independent review text.

The packet is sufficient only for the bounded experiment described in REVIEW-003. Additional independently reviewed realistic-source cases are required before interpreting any result as a general endpoint-role capability.
