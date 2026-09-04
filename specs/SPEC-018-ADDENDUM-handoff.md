# SPEC-018 ADDENDUM — Required Handoff

## Contract Status

This file is part of the canonical SPEC-018 contract together with:

```text
specs/SPEC-018-continuous-graph-navigation.md
```

Codex must read both files before implementation.

## Required Handoff

Report:

1. navigation architecture implemented;
2. exact SPEC-006/BASELINE-001 assets treated as visual invariant;
3. confirmation those baseline artifacts remained unchanged;
4. navigation fixture design and why it is sufficient to exceed one viewport;
5. fixture node count;
6. fixture relationship count;
7. world-coordinate model;
8. world bounds;
9. initial viewport/camera state;
10. camera transform implementation;
11. drag/pan behavior;
12. node-drag prevention;
13. frontier definition;
14. frontier-node count;
15. frontier reveal strategy: precomputed world vs deterministic lazy reveal;
16. focus/recenter target calculation;
17. no-motion/interior-node behavior;
18. focus animation behavior;
19. reduced-motion behavior;
20. world-coordinate stability checks;
21. relative spatial-order stability checks;
22. canonical relationship rendering preservation;
23. relationship-label/direction preservation;
24. node selection preservation;
25. hover-preview preservation;
26. detail/evidence synchronization after camera movement;
27. edge hit-target behavior after transforms;
28. navigation-history behavior if implemented;
29. overview/home behavior;
30. search/recenter behavior if implemented;
31. geometric zoom behavior if implemented;
32. confirmation semantic zoom was not implemented;
33. machine navigation diagnostics;
34. layout overlap/crossing diagnostics;
35. deterministic regeneration result;
36. exact offline test result;
37. browser/manual interaction verification;
38. browser console warnings/errors;
39. dependencies added/removed;
40. semantic IR/vocabulary changes, expected none;
41. complexity impact;
42. known UX weaknesses;
43. deviations;
44. exact generation command;
45. exact viewer launch command;
46. local URL/port example;
47. separate baseline launch command for comparison;
48. machine integrity verdict;
49. human review status, initially `PENDING_OWNER_REVIEW` unless completed;
50. implementation commit SHA;
51. evaluation/final commit SHA if separate;
52. push confirmation to canonical `origin/main`;
53. confirmation `HEAD == origin/main`;
54. working-tree state;
55. confirmation no `DEBRIEF-018` was created.

## Human Review Handoff Rule

Before owner review, do not provide the full implementation handoff.

First provide only:

```text
<viewer command>

Explore the map naturally. Try moving through it rather than systematically testing it.
```

Wait for spontaneous feedback.

## Decision Gate After SPEC-018

### If `CONTINUOUS_NAVIGATION_BETTER`

Freeze continuous graph navigation as the interaction baseline.

Then decide whether the next highest-value experiment is:

- integrating the already-preferred contextual semantic depth into the continuous map;
- validating continuous navigation with realistic-source topology;
- or testing semantic zoom as a separate resolution dimension.

Do not reopen visual grammar without contradictory human evidence.

### If `MIXED`

Fix only the observed navigation weakness while preserving the visual invariant.

### If `NO_MEANINGFUL_IMPROVEMENT`

Do not compensate by redesigning representation. Reassess camera/frontier interaction directly.

### If `INCONCLUSIVE`

Resolve only the implementation/review blocker.

## Operating-Model Addition

Preserve this experimental discipline in future contracts:

> **Once a dimension has a strongly preferred baseline, freeze that dimension while experimenting on another dimension.**

For SPEC-018:

```text
visual grammar = frozen
semantic architecture = frozen
navigation = experimental variable
```
