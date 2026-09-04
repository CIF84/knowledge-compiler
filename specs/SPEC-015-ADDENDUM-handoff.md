# SPEC-015 ADDENDUM — Required Handoff

## Contract Status

This file is part of the canonical SPEC-015 contract together with:

```text
specs/SPEC-015-semantic-compression-adequacy.md
```

Codex must read both files.

The addendum is separated intentionally to avoid long-contract transport truncation.

## Required Handoff

Report:

1. architecture implemented;
2. provider-independent judge interface;
3. provider-specific adapter boundary;
4. frozen source packet path;
5. frozen packet SHA-256 verification;
6. confirmation frozen packet remained byte-identical;
7. positive/negative case counts;
8. blinded packet construction;
9. opaque case-ID strategy;
10. exact fields exposed to the model;
11. exact fields withheld for blinding;
12. blinding/leakage validation result;
13. verdict vocabulary;
14. deterministic judge-output validation rules;
15. confirmation candidate rewriting is impossible in the output contract;
16. confirmation no semantic IR/vocabulary changes;
17. exact live command;
18. provider/model;
19. prompt/evaluator versions;
20. live-call count;
21. retry count;
22. request ID;
23. token usage;
24. runtime;
25. authoritative cost or `NOT_AVAILABLE`;
26. per-case verdicts after offline unblinding;
27. positive-control results;
28. negative-control results;
29. Pauli-case result;
30. true adequate admits;
31. false adequate admits;
32. true inadequate rejects;
33. false inadequate rejects;
34. adequate-admission precision;
35. adequate-admission recall;
36. negative rejection rate;
37. overall agreement;
38. per-predicate/per-family diagnostics where meaningful;
39. any evidence of blanket rejection or trivial strategy;
40. diagnostic-category usefulness on negative cases;
41. residual error class if any;
42. final verdict from the allowed set;
43. interpretation relative to SPEC-014 without invalid direct statistical claims;
44. conclusion on narrow gates vs multi-agent deliberation;
45. conclusion on production integration readiness;
46. dependencies added/removed;
47. complexity impact;
48. deviations;
49. exact offline test result;
50. preservation of prior artifacts;
51. implementation commit SHA;
52. evaluation/final commit SHA if separate;
53. confirmation pushed to canonical `origin/main`;
54. confirmation `HEAD == origin/main`;
55. working-tree state;
56. confirmation no `DEBRIEF-015` was created.

## Push Discipline

Follow `AGENTS.md` and the repository operating model.

If the environment requests explicit confirmation before pushing already approved implementation/evaluation commits to canonical `origin/main`, stop and request that confirmation rather than changing workflow silently.

## Decision Gate After SPEC-015

Do not automatically integrate the judge or create a multi-agent system.

### If `COMPRESSION_JUDGE_BETTER`

Close the experiment and decide whether the next highest-value uncertainty is:

- broader semantic reliability validation on a second realistic source/domain;
- assertion-aware representation of trustworthy claims;
- or another narrowly observed residual semantic error.

Do not assume production integration from ten cases.

### If `MIXED`

Inspect residual errors before designing another mechanism.

### If `NO_MEANINGFUL_SIGNAL`

Reject or pause the compression-judge hypothesis. Do not compensate by adding more agents automatically.

### If `INCONCLUSIVE`

Resolve only the operational/provider issue that prevented fair evaluation.

## Experimental Memory

The benchmark packet was created before SPEC-015 implementation and validated with 125/125 integrity checks. It intentionally includes correlated and heterogeneous historical cases and is suitable only for one bounded exploratory experiment.

Do not generalize benchmark accuracy into a production reliability claim.
