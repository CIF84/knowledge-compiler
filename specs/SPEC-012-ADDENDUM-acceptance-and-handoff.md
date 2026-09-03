# SPEC-012 ADDENDUM — Acceptance Criteria and Required Handoff

## Contract Status

This file is part of the canonical SPEC-012 contract together with:

```text
specs/SPEC-012-staged-semantic-compilation.md
```

The main SPEC is intentionally paired with this addendum so long-contract transport does not silently truncate acceptance/handoff requirements.

Codex must read both files before implementation.

Do not infer missing requirements from prior SPECs.

## Acceptance Criteria — Live Experiment

- [ ] Exact frozen SPEC-011 source revision is used.
- [ ] Source text is unchanged from the accepted benchmark.
- [ ] Provider/model are recorded explicitly.
- [ ] `store=False` is used where supported by the current provider path.
- [ ] SDK automatic retries are disabled.
- [ ] Owner approval is obtained before the staged live calls when required by current workflow.
- [ ] Primary live budget is exactly two staged calls: symbol discovery then semantic linking.
- [ ] Pass 2 is not made if Pass 1 fails.
- [ ] No hidden retries occur.
- [ ] No prompt iteration occurs after viewing primary live output.
- [ ] No external semantic enrichment occurs.
- [ ] No third semantic pass occurs.
- [ ] No child-resolution live call occurs.
- [ ] Raw/rejected staged proposals and provider metadata are preserved where available.

## Acceptance Criteria — Structural Comparison

- [ ] SPEC-011 control failures are preserved unchanged.
- [ ] Control dangling-endpoint count is recorded.
- [ ] Staged dangling-endpoint count is recorded.
- [ ] Staged unknown-symbol diagnostics are recorded.
- [ ] Duplicate/alias diagnostics are recorded for Pass 1.
- [ ] Pass 2 cannot add entities outside the frozen symbol table.
- [ ] Accepted staged output round-trips through `KnowledgeModel` if successful.
- [ ] Structural improvement is not treated as sufficient evidence of semantic improvement.

## Acceptance Criteria — Grounding Comparison

- [ ] SOURCE/INFERRED counts are reported.
- [ ] Exact evidence-resolution results are reported.
- [ ] Missing/ambiguous quote failures are preserved.
- [ ] Grounding rules are not weakened relative to SPEC-011.
- [ ] No unsupported source evidence is fabricated.
- [ ] No inferred semantic item carries source evidence.

## Acceptance Criteria — Semantic Comparison

- [ ] Semantic review categories are fixed before inspecting staged semantic results.
- [ ] The preserved SPEC-011 control proposal is mapped into those categories.
- [ ] Every accepted staged relationship/proposition selected for review is judged independently from generation.
- [ ] Known SPEC-011 semantic defects are explicitly compared against staged behavior.
- [ ] Endpoint precision is evaluated separately from predicate precision.
- [ ] Overstated causality is explicitly detectable in review.
- [ ] Lossy binary forms are explicitly detectable in review.
- [ ] Semantic precision is reported as supported reviewed items / reviewed accepted items where denominator is non-zero.
- [ ] Semantic volume is not used as a proxy for quality.
- [ ] No unsupported claim of recall/completeness is made from this single benchmark.

## Acceptance Criteria — Verdict

The final experiment verdict must be exactly one of:

```text
STAGED_BETTER
NO_MEANINGFUL_IMPROVEMENT
STAGED_WORSE
MIXED
INCONCLUSIVE
```

The verdict rationale must separately state:

```text
structural result
grounding result
semantic result
cost/complexity result
```

`STAGED_BETTER` requires more than removal of dangling endpoints. It requires meaningful semantic-precision improvement without weakening grounding.

If structural reliability improves but semantic precision remains weak, prefer `NO_MEANINGFUL_IMPROVEMENT` or `MIXED` depending on the observed tradeoff.

## Acceptance Criteria — Downstream Diagnostic

If and only if a valid staged parent exists:

- [ ] existing structure detection runs unchanged;
- [ ] existing representation builder runs unchanged;
- [ ] existing layout runs unchanged;
- [ ] diagnostic counts are recorded;
- [ ] optional local viewer uses only the trusted accepted parent;
- [ ] viewer is clearly treated as diagnostic, not semantic proof.

If no valid parent exists:

- [ ] no rejected staged graph is rendered as learner-facing truth.

## Acceptance Criteria — Cost and Complexity

Report:

- [ ] Pass-1 prompt/version;
- [ ] Pass-2 prompt/version;
- [ ] Pass-1 token usage;
- [ ] Pass-2 token usage;
- [ ] combined staged token usage;
- [ ] available SPEC-011 control usage;
- [ ] Pass-1 runtime;
- [ ] Pass-2 runtime;
- [ ] combined runtime;
- [ ] symbol-table size;
- [ ] provider request IDs where available;
- [ ] authoritative monetary cost if available, otherwise `NOT_AVAILABLE`;
- [ ] dependencies added/removed;
- [ ] meaningful new code/architecture surface;
- [ ] whether the reliability gain appears worth the additional pass based on this benchmark, without generalizing beyond the evidence.

## Required Handoff

Provide a concise but complete handoff containing:

1. architecture implemented;
2. exact staged boundary and why it is provider-independent;
3. Pass-1 schema/output contract;
4. Pass-1 normalization and ID strategy;
5. frozen-symbol-table invariant;
6. Pass-2 schema/output contract;
7. how Pass 2 is prevented from minting entities;
8. unknown-symbol behavior;
9. confirmation canonical `KnowledgeModel` remains unchanged downstream unless a narrowly necessary compatible field change was required;
10. relationship-vocabulary changes, expected `none`;
11. proposition-vocabulary changes, expected `none`;
12. grounding-rule changes, expected `none`;
13. frozen source identity and revision;
14. control evidence used from SPEC-011;
15. exact live commands;
16. provider/model;
17. prompt/compiler versions;
18. live-call count;
19. retry count and confirmation of no hidden retries;
20. Pass-1 outcome;
21. symbol-table counts/diagnostics;
22. Pass-2 outcome;
23. staged entity/relationship/claim/proposition counts if available;
24. structural-validity comparison control vs staged;
25. grounding-validity comparison control vs staged;
26. semantic-review categories;
27. control semantic-precision assessment;
28. staged semantic-precision assessment;
29. notable control defects and whether staged compilation fixed, retained, or replaced them;
30. any new staged semantic defects;
31. final verdict from the allowed verdict set;
32. verdict rationale separated into structural, grounding, semantic, and complexity dimensions;
33. downstream structure/representation/layout diagnostics if a trusted parent exists;
34. local viewer command if a trusted parent exists, otherwise `NOT_AVAILABLE`;
35. token usage per pass and combined;
36. runtime per pass and combined;
37. authoritative cost or `NOT_AVAILABLE`;
38. dependency changes;
39. complexity impact;
40. deviations from SPEC;
41. exact offline test result;
42. preservation of SPEC-011 and earlier baselines;
43. files/artifacts created or materially changed;
44. implementation commit SHA;
45. evaluation/final commit SHA if separate;
46. confirmation pushed to canonical `origin/main`;
47. confirmation working tree state;
48. confirmation no `DEBRIEF-012` was created.

## Human Review

If a trusted staged parent exists, the owner may inspect it after repository semantic review.

Do not ask the owner to judge whether staging is semantically better solely from graph appearance.

First provide the semantic comparison results, then optionally provide the viewer as a cognitive diagnostic.

Human review questions may include:

- Does the staged parent feel less semantically strange than the rejected one-pass proposal?
- Are important relationships understandable and plausible?
- Does the resulting overview look coherent enough to justify returning to the original SPEC-011 learning-slice objective later?

Do not resume child semantic zoom or formal learning preference testing inside SPEC-012.

## Decision Gate After SPEC-012

Do not automatically proceed to UI/navigation work after implementation.

### If `STAGED_BETTER`

Staged compilation becomes a candidate realistic-source extraction architecture. The next experiment should determine whether the improved parent is trustworthy/useful enough to resume the end-to-end learning slice, potentially re-attempting the downstream SPEC-011 objective without adding unrelated architecture.

### If `NO_MEANINGFUL_IMPROVEMENT`

Do not add more passes automatically. Investigate semantic endpoint/predicate attribution as the dominant problem.

### If `MIXED`

Identify which dimension improved and which remained limiting before designing the next experiment.

### If `STAGED_WORSE`

Reject the staged hypothesis for now and preserve the result.

### If `INCONCLUSIVE`

Resolve only the operational/provider issue that prevented fair comparison before repeating the experiment.

## Final Constraint

The purpose of SPEC-012 is not to make the quantum benchmark pass at any cost.

It is to answer one architecture question cleanly:

> **Does freezing the symbol space before semantic linking make realistic-source compilation materially more trustworthy?**

A negative answer is an acceptable and valuable result.
