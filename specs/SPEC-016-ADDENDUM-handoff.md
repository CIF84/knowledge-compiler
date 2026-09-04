# SPEC-016 ADDENDUM — Required Handoff

## Contract Status

This file is part of the canonical SPEC-016 contract together with:

```text
specs/SPEC-016-assertion-aware-representation.md
```

Codex must read both files before implementation.

## Required Handoff

Report:

1. architecture implemented;
2. exact frozen SPEC-013 inputs used;
3. input identity/hash verification;
4. assertion-aware representation model design;
5. semantic tiers represented;
6. visual grammar for canonical relationships;
7. visual grammar for propositions;
8. visual grammar for claims/assertions;
9. how assertion participants attach to concepts without fabricating semantic edges;
10. deterministic salience/orientation strategy;
11. initial density limits;
12. neighborhood/grouping strategy;
13. presentation-only metadata and how it is distinguished from semantic truth;
14. provenance path for canonical relationships;
15. provenance path for assertions/claims;
16. evidence-inspection behavior;
17. interaction behavior;
18. files changed;
19. confirmation no semantic IR changes;
20. confirmation no relationship/proposition vocabulary changes;
21. confirmation no live model/provider calls;
22. input symbol count;
23. input canonical relationship count;
24. input proposition count;
25. input grounded assertion/claim count;
26. represented concept count;
27. represented canonical relationship count;
28. represented assertion/claim count;
29. initial visible concept/assertion counts;
30. coverage diagnostics;
31. neighborhood counts/sizes;
32. layout diagnostics;
33. semantic-tier labeling integrity;
34. provenance completeness;
35. deterministic regeneration result;
36. baseline/prior-artifact preservation;
37. exact offline test result;
38. dependencies added/removed;
39. complexity impact;
40. known visual/cognitive weaknesses;
41. deviations;
42. exact command to generate the experimental artifact;
43. exact command to launch the viewer;
44. local address/port example;
45. machine integrity verdict;
46. human review status, initially `PENDING_OWNER_REVIEW` unless completed;
47. implementation commit SHA;
48. evaluation/final commit SHA if separate;
49. push confirmation to canonical `origin/main`;
50. working-tree state;
51. confirmation no `DEBRIEF-016` was created.

## Human Review Handoff

Do not lead the owner with implementation details when asking for cognitive review.

After integrity verification, first provide only:

```text
viewer command
minimal instruction:
"Use this to orient yourself in the quantum-mechanics material."
```

Let the owner explore before presenting machine metrics or design rationale.

The final product verdict should be recorded only after that review.

## Decision Gate After SPEC-016

### If `ASSERTION_AWARE_BETTER`

The project has regained a useful learner-facing surface without weakening semantic truth. Reassess the original Phase-II learning slice and decide whether the next uncertainty is navigation/semantic zoom or validation on another realistic source.

### If `MIXED`

Identify whether the limiting factor is density, salience, assertion grouping, visual grammar, or interaction before changing semantics.

### If `NO_MEANINGFUL_IMPROVEMENT`

Do not loosen semantic admission. Reconsider the cognitive projection strategy.

### If `INCONCLUSIVE`

Resolve only the implementation/review blocker.

## Product Principle

Preserve this distinction:

```text
semantic compiler decides what is justified
presentation decides how justified knowledge is useful to think with
```

SPEC-016 belongs entirely to the second responsibility.
