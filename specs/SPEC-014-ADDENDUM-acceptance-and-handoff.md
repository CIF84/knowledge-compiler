# SPEC-014 ADDENDUM — Acceptance Criteria and Required Handoff

## Contract Status

This file is part of the canonical SPEC-014 contract together with:

```text
specs/SPEC-014-independent-semantic-admission-gate.md
```

Both files must be read before implementation.

## Acceptance Criteria — Frozen Packet

- [ ] Packet is constructed entirely from preserved SPEC-013 positive controls and independently reviewed SPEC-012 negative controls.
- [ ] Positive labels correspond to independently supported SPEC-013 canonical relationships.
- [ ] Negative labels correspond to preserved independently reviewed SPEC-012 defects.
- [ ] Packet construction does not use live gate output.
- [ ] Packet has deterministic ordering and stable hash.
- [ ] Packet preserves exact assertion/evidence/candidate semantics needed for judgment.
- [ ] Packet does not contain unnecessary source text.
- [ ] Packet does not silently rewrite any control candidate.

## Acceptance Criteria — Live Discipline

- [ ] Owner approval is obtained before any live gate call if required by current workflow.
- [ ] Provider/model are recorded.
- [ ] `store=False` is used where supported.
- [ ] SDK automatic retries are disabled.
- [ ] Primary experiment uses one gate call if technically feasible.
- [ ] If batching is necessary, batch count is fixed before the first live result.
- [ ] No hidden retries occur.
- [ ] No prompt repair occurs after observing live output.
- [ ] No second model/agent is introduced.
- [ ] No candidate rewriting occurs.
- [ ] No external enrichment occurs.

## Acceptance Criteria — Metrics

Report at least:

```text
positive candidate count
negative candidate count
true admits
false admits
true rejects/demotions
false rejects
ADMIT precision
justified-admission recall
negative rejection rate
overall classification agreement with independent labels
```

Where denominators are zero, report `NOT_AVAILABLE` rather than inventing a value.

Also report verdict distribution by semantic defect category where sample size permits.

## Acceptance Criteria — Safety/Tier Preservation

- [ ] Rejected graph commitments do not delete grounded source meaning.
- [ ] Lower-commitment claim/assertion path is preserved conceptually and in any integration seam.
- [ ] Gate does not upgrade claims into relationships.
- [ ] Gate cannot create stronger semantics than the candidate it reviews.
- [ ] Gate cannot change source evidence.

## Acceptance Criteria — Experimental Verdict

Final verdict is exactly one of:

```text
GATE_BETTER
NO_MEANINGFUL_IMPROVEMENT
GATE_TOO_CONSERVATIVE
GATE_UNRELIABLE
INCONCLUSIVE
```

The rationale must separately address:

```text
positive-control retention
negative-control rejection
failure modes
cost/latency
complexity
whether escalation to multi-agent deliberation is justified
```

`GATE_BETTER` should normally require strong retention of positive controls and strong rejection of known negatives. Do not define a universal production threshold from this tiny packet.

## Required Handoff

Report:

1. architecture implemented;
2. provider-independent gate interface;
3. exact gate input contract;
4. exact verdict vocabulary;
5. confirmation gate cannot rewrite candidates;
6. confirmation gate cannot mint entities/evidence;
7. deterministic contract checks added, if any;
8. frozen packet construction method;
9. packet positive count;
10. packet negative count;
11. positive candidate identities/source;
12. negative candidate identities/source;
13. packet hash;
14. provider/model;
15. prompt/evaluator versions;
16. exact live command;
17. live call count;
18. retry count;
19. request ID(s);
20. input/output/total token usage;
21. runtime;
22. authoritative monetary cost or `NOT_AVAILABLE`;
23. gate results for each positive candidate;
24. gate results for each negative candidate;
25. true admits;
26. false admits;
27. true rejects/demotions;
28. false rejects;
29. ADMIT precision;
30. justified-admission recall;
31. negative rejection rate;
32. notable disagreements with independent review;
33. final verdict;
34. verdict rationale;
35. whether the gate appears worth its incremental cost/complexity;
36. whether broad multi-agent deliberation is now justified, not justified, or still unresolved;
37. any recommended next discriminator;
38. KnowledgeModel changes, expected `none`;
39. relationship-vocabulary changes, expected `none`;
40. proposition-vocabulary changes, expected `none`;
41. grounding-rule changes, expected `none`;
42. dependencies added/removed;
43. implementation complexity;
44. deviations;
45. exact offline test result;
46. confirmation prior SPEC-012/013 artifacts unchanged;
47. files/artifacts created or materially changed;
48. implementation commit SHA;
49. evaluation/final commit SHA if separate;
50. push confirmation to canonical `origin/main`;
51. working-tree status;
52. confirmation no `DEBRIEF-014` was created.

## Decision Gate After SPEC-014

### If `GATE_BETTER`

Treat the independent gate as a credible candidate trust layer. Do not automatically add multi-agent deliberation. First decide whether the gate should be integrated into realistic-source compilation and whether the project should return to the downstream assertion-aware representation bottleneck.

### If `GATE_TOO_CONSERVATIVE`

Do not add more critics. Investigate what context or contract information the gate lacks before increasing agent count.

### If `NO_MEANINGFUL_IMPROVEMENT`

Do not assume more agents will solve the problem. Reassess whether assertion-first normalization already captures most available reliability benefit.

### If `GATE_UNRELIABLE`

Reject the simple admission-gate hypothesis for now. Multi-agent escalation requires a separate argument grounded in the disagreement pattern.

### If `INCONCLUSIVE`

Resolve only the operational/provider issue that prevented fair evaluation.

## Final Constraint

SPEC-014 tests one mechanism only:

> **Can an independent bounded semantic judge discriminate justified from unjustified canonical commitments cheaply enough to improve trust?**

It is not an invitation to build an agent society.
