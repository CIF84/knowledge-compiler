# SPEC-019 ADDENDUM — Required Handoff

## Contract Status

This file is part of the canonical SPEC-019 contract together with:

```text
specs/SPEC-019-navigation-learning-workspace.md
```

Codex must read both before implementation.

## Required Handoff

Report:

1. workspace architecture implemented;
2. exact BASELINE-001 assets referenced;
3. exact BASELINE-002/navigation assets referenced;
4. baseline immutability/hash verification;
5. fixture/domain composition used;
6. provenance labeling for composed fixtures;
7. workspace layout choice and rationale;
8. navigation-pane responsibilities;
9. learning-pane responsibilities;
10. shared focus-state design;
11. camera-state separation from semantic focus;
12. navigation→learning concept synchronization;
13. learning→navigation concept synchronization;
14. relationship synchronization;
15. stable-ID matching strategy;
16. unnecessary-recenter avoidance strategy;
17. parent-context/path treatment;
18. learning representation types demonstrated;
19. confirmation representation selection was not flattened into generic graph rendering;
20. pan behavior;
21. zoom behavior;
22. Overview/Home behavior;
23. focus suppression in navigation;
24. focus suppression in learning representation;
25. hover vs persistent selection behavior;
26. detail/evidence behavior;
27. blue-artifact status and fix if applied;
28. keyboard focus-visible behavior;
29. machine synchronization diagnostics;
30. pure pan/zoom learning-state preservation;
31. camera preservation across learning updates;
32. baseline comparison diagnostics;
33. exact offline test result;
34. browser mouse verification;
35. browser keyboard verification;
36. browser console result;
37. dependencies added/removed;
38. semantic IR/vocabulary changes, expected none;
39. representation algorithm changes, expected none;
40. personalization implementation, expected none;
41. semantic zoom implementation, expected none;
42. live model calls, expected zero;
43. complexity impact;
44. known UX weaknesses;
45. deviations;
46. exact generation command;
47. exact viewer command;
48. local URL/port example;
49. separate BASELINE-001 comparison command;
50. separate BASELINE-002/navigation comparison command where available;
51. machine integrity verdict;
52. human review status, initially `PENDING_OWNER_REVIEW`;
53. implementation commit SHA;
54. evaluation/final commit SHA if separate;
55. push confirmation to canonical `origin/main`;
56. `HEAD == origin/main` confirmation;
57. working-tree state;
58. confirmation no replacement baseline was created;
59. confirmation no `DEBRIEF-019` was created.

## Human Review Handoff Rule

Before owner cognitive review, do not provide the implementation report above.

First provide only:

```text
<viewer command>

Use this to understand the subject, but move around whenever the map makes you curious.
```

Wait for spontaneous owner feedback.

## Decision Gate After SPEC-019

### If `HYBRID_WORKSPACE_BETTER`

Preserve BASELINE-001 and BASELINE-002 independently, then prepare a separate owner-approved hybrid baseline capture.

The next experiment should then address the highest remaining product uncertainty, likely representation personalization or semantic-resolution integration—not basic navigation composition.

### If `MIXED`

Identify whether the problem is workspace proportion, attention hierarchy, synchronization, or duplication. Preserve both component baselines while iterating only the weak integration seam.

### If `NO_MEANINGFUL_IMPROVEMENT`

Do not weaken either baseline. Keep exploration and learning surfaces separate until a better integration hypothesis emerges.

### If `INCONCLUSIVE`

Resolve only the implementation/review blocker.

## Preserved Architecture

```text
semantic compiler
→ truth

representation engine
→ meaning expressed appropriately

navigation engine
→ spatial orientation

workspace
→ synchronized interaction
```

Personalization belongs above truthful representation availability, not inside semantic truth.
