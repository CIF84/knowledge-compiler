# SPEC-021 ADDENDUM — Required Handoff

## Contract Status

This file is part of the canonical SPEC-021 contract together with:

```text
specs/SPEC-021-focus-preserving-explanatory-projection.md
```

Codex must read both before implementation.

## Required Handoff

Report:

1. final machine integrity status;
2. exact frozen SPEC-020 artifacts consumed;
3. input hashes/identity verification;
4. frozen focus ID;
5. focus-direct assertion count;
6. explanatory-projection architecture;
7. exact presentation-only model/schema added;
8. confirmation canonical `KnowledgeModel` unchanged;
9. confirmation global structure detector unchanged;
10. trusted canonical items included;
11. known rejected/overstated items excluded;
12. explanatory-item construction rule;
13. any explanatory role vocabulary used and why it is not a hidden ontology;
14. participant-preservation behavior;
15. pairwise-edge fabrication result;
16. semantic-tier visual grammar;
17. canonical relationship visual grammar;
18. explanatory-item visual grammar;
19. initial text budget / visible prose count;
20. explanation reveal behavior;
21. evidence reveal behavior;
22. provenance completeness;
23. focus-preservation result;
24. represented concept count;
25. represented canonical relationship count;
26. represented explanatory item count;
27. layout strategy;
28. layout diagnostics;
29. deterministic regeneration result;
30. canonical-control comparison;
31. BASELINE-003 integration design;
32. parent navigation/camera invariance;
33. parent ↔ deeper projection transition;
34. return-to-parent behavior;
35. selection/detail synchronization;
36. baseline hash/immutability result;
37. exact offline test result;
38. confirmation live model calls = 0;
39. dependencies added/removed;
40. semantic IR/vocabulary changes, expected none;
41. workspace-shell changes, expected none;
42. complexity impact;
43. known UX/cognitive weaknesses;
44. deviations;
45. exact generation command;
46. exact viewer command;
47. local URL/port example;
48. machine comparison with existing canonical detector;
49. human review status, initially `PENDING_OWNER_REVIEW` if viewer produced;
50. implementation commit SHA;
51. evaluation/final commit SHA if separate;
52. push confirmation to canonical `origin/main`;
53. confirmation `HEAD == origin/main`;
54. working-tree state;
55. confirmation BASELINE-001/002/003 preserved;
56. confirmation no new baseline created;
57. confirmation no `DEBRIEF-021` created before owner verdict.

## Human Review Handoff Rule

If the machine gate passes and a viewer exists, do not provide the full report before owner review.

First provide only:

```text
<viewer command>

Use this to understand the double-slit experiment. Follow anything that seems useful, and tell me what the representation makes easier or harder to understand.
```

Wait for spontaneous owner feedback.

## Decision Gate After SPEC-021

### If `EXPLANATORY_PROJECTION_BETTER`

The representation layer has a credible path for trustworthy assertion-rich realistic semantics without weakening canonical graph admission.

The next step should resume the SPEC-020 semantic-depth product question using this projection path inside BASELINE-003, preferably without another semantic generation call if the frozen packet remains sufficient.

### If `MIXED`

Identify whether the weakness is explanatory-item selection, visual grammar, focus composition, or semantic-tier clarity. Change only that dimension.

### If `NO_MEANINGFUL_IMPROVEMENT`

Do not compensate by promoting more assertions into canonical relationships. Reconsider the explanatory projection mechanism.

### If `INCONCLUSIVE`

Resolve only the implementation/review blocker.

## Final Constraint

The representation layer may compress attention, but it may not strengthen truth.

SPEC-021 must make grounded meaning easier to think with while preserving the distinction between:

```text
what the compiler knows canonically
and
what the source explains reliably
```
