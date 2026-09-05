# SPEC-020 ADDENDUM — Acceptance and Required Handoff

## Contract Status

This file is part of the canonical SPEC-020 contract together with:

```text
specs/SPEC-020-realistic-semantic-depth-in-hybrid-workspace.md
```

Codex must read both files before implementation.

## Pre-Live Stop Gate

Implementation must stop for owner approval before transmitting any source/model payload.

The approval request must report only what is necessary to make an informed decision:

1. offline implementation status;
2. exact offline test result;
3. working-tree / commit state;
4. reused parent artifact(s) and hashes;
5. frozen focus concept and rationale;
6. frozen source scope and size/hash;
7. chosen resolution strategy;
8. exact provider/model;
9. exact planned call count;
10. what public source/semantic material each call will transmit;
11. `store=False` status;
12. retry policy;
13. confirmation of no enrichment/prompt repair/hidden calls;
14. conditional rule for later calls if an earlier stage fails.

Do not make the live call in the same step as the approval request.

## Live Failure Discipline

If any approved live stage fails closed:

- preserve the failure;
- do not automatically repair prompts;
- do not silently retry;
- do not continue to a dependent stage whose prerequisites are absent;
- report whether an additional explicit semantic retry would be scientifically justified;
- request new approval before any additional call.

## Trusted Child Gate

A child may enter downstream representation/workspace rendering only if all required trusted validations pass.

At minimum:

```text
source evidence exact/valid
participant/entity integrity
canonical semantic validation
proposition validation where applicable
no unknown endpoints/roles
no silent entity minting outside contract
KnowledgeModel round-trip
```

If the child fails, do not render the rejected semantic proposal as though it were trusted learning content.

## Semantic Review

Before owner cognitive review, perform an independent repository-side semantic inspection of the trusted child.

Use the existing review vocabulary where applicable:

```text
SUPPORTED
IMPRECISE_ENDPOINT
WRONG_PREDICATE
REVERSED_DIRECTION
OVERSTATED_CAUSALITY
UNSUPPORTED
LOSSY_BINARY_FORM
OTHER
```

Also inspect assertion fidelity where assertion-first generation is used.

Do not hide or presentation-repair semantic defects discovered after acceptance.

## Workspace Integrity Gate

Before human review verify:

- BASELINE-003 shell/assets unchanged except isolated SPEC-020 integration assets;
- parent navigation world coordinates unchanged;
- parent camera state does not reset merely because child resolution activates;
- parent semantic focus remains identifiable;
- child learning representation can activate/deactivate without page navigation;
- relationship/concept selection remains synchronized;
- evidence panel shows child evidence when child items are selected;
- geometric pan/zoom remains independent;
- no blue/default browser focus regression is introduced relative to the current accepted workspace;
- browser console is clean under normal review interaction.

## Human Review Handoff Rule

Before owner cognitive review, do not provide the full implementation report.

First provide only:

```text
<viewer command>

Use this to explore the quantum-mechanics material. When something offers deeper detail, follow it and see whether you still feel oriented.
```

Wait for spontaneous owner feedback.

## Human Verdict

After feedback, classify exactly one:

```text
SEMANTIC_DEPTH_BETTER
MIXED
NO_MEANINGFUL_IMPROVEMENT
INCONCLUSIVE
```

Do not infer `SEMANTIC_DEPTH_BETTER` from machine success alone.

## Required Final Handoff

Report:

1. final verdict;
2. owner-review summary if completed;
3. exact BASELINE-003 assets treated as frozen;
4. baseline immutability/hash result;
5. realistic source metadata/revision/hash;
6. reused parent semantic artifacts/hashes;
7. parent immutability result;
8. frozen focus concept and rationale;
9. frozen source scope/range/hash;
10. resolution strategy;
11. child semantic architecture actually used;
12. assertion-first reuse details;
13. semantic-gate/compression checks used, if any;
14. provider/model;
15. prompt/compiler/evaluator versions;
16. exact live command(s);
17. exact call count;
18. retry count and policy;
19. request IDs;
20. per-call usage;
21. per-call runtime;
22. combined usage/runtime;
23. authoritative monetary cost or `NOT_AVAILABLE`;
24. grounding counts/results;
25. assertion fidelity results where applicable;
26. canonical relationship/proposition/claim counts;
27. uncompiled assertion count where applicable;
28. semantic review results;
29. known defects/new defects;
30. child model validation/round-trip;
31. structure-detection results;
32. selected representation type(s);
33. representation/layout diagnostics;
34. child evidence/provenance integrity;
35. parent/child shared semantic IDs;
36. workspace integration design;
37. parent-map stability result;
38. navigation camera invariance result;
39. parent ↔ child resolution interaction;
40. return-to-parent behavior;
41. selection/detail synchronization;
42. geometric zoom independence;
43. browser mouse verification;
44. browser keyboard verification;
45. browser console result;
46. comparison with parent-only BASELINE-003;
47. comparison with relevant original source passage;
48. exact offline test result;
49. dependencies added/removed;
50. semantic IR/vocabulary changes, expected none;
51. workspace-shell changes, expected none;
52. complexity impact;
53. limitations;
54. deviations;
55. evaluation artifact paths;
56. exact viewer command;
57. local URL/port example;
58. implementation commit SHA;
59. evaluation/final commit SHA if separate;
60. push confirmation to canonical `origin/main`;
61. confirmation `HEAD == origin/main`;
62. working-tree state;
63. confirmation BASELINE-001/002/003 remain preserved;
64. confirmation no new baseline was created without explicit owner approval;
65. confirmation no `DEBRIEF-020` was created before owner verdict.

## Decision Gate After SPEC-020

### If `SEMANTIC_DEPTH_BETTER`

Freeze the semantic-depth interaction as an accepted capability of the BASELINE-003 workspace without replacing BASELINE-003 itself.

Then choose the next experiment based on observed bottleneck:

- representation selection if child structure is truthful but the chosen visual form is weak;
- personalized representation priority if multiple truthful forms are already useful;
- guided Journey/course coordinates if both free exploration and semantic depth are strong;
- broader realistic-source validation if semantic reliability remains the dominant uncertainty.

### If `MIXED`

Identify whether the weakness is semantic generation, representation, orientation, or depth interaction. Change only that dimension.

### If `NO_MEANINGFUL_IMPROVEMENT`

Keep BASELINE-003 unchanged and do not add semantic depth merely because the compiler can generate it.

### If `INCONCLUSIVE`

Resolve only the blocker that prevented a fair review.

## Final Constraint

SPEC-020 is not permission to redesign the interface.

It tests whether the strongest semantic architecture can finally populate the strongest interaction architecture with useful depth.
