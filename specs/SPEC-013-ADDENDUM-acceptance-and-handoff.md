# SPEC-013 ADDENDUM — Acceptance Criteria and Required Handoff

## Contract Status

This file is part of the canonical SPEC-013 contract together with:

```text
specs/SPEC-013-assertion-first-semantic-compilation.md
```

Both files must be read before implementation.

The split is deliberate to avoid silent truncation of long contracts.

## Acceptance Criteria — Live Experiment

- [ ] Exact frozen quantum source/revision from SPEC-011/012 is used.
- [ ] Source text/hash is verified before live execution.
- [ ] SPEC-012 frozen-symbol concept is preserved.
- [ ] Reuse of the SPEC-012 symbol table is preferred if fair and technically compatible.
- [ ] If a fresh symbol-discovery call is required, explicit owner approval is obtained for the resulting three-call budget before any transmission.
- [ ] Otherwise primary live budget is exactly two calls: assertion extraction and canonical normalization.
- [ ] `store=False` is used where supported.
- [ ] SDK automatic retries are disabled.
- [ ] No hidden retries occur.
- [ ] No semantic retry occurs without explicit owner approval.
- [ ] No prompt repair occurs after inspecting live output.
- [ ] No external enrichment occurs.
- [ ] No child-resolution call occurs.
- [ ] Provider/model, prompt versions, request IDs, usage, and runtime are preserved where available.

## Acceptance Criteria — Assertion Stage

- [ ] SourceAssertion schema is minimal and provider-independent.
- [ ] Assertion text/meaning is preserved before canonical graph semantics are selected.
- [ ] Assertion participants reference frozen symbol IDs when applicable.
- [ ] Unknown participant symbols fail closed or are preserved as explicit diagnostics according to a fixed pre-run rule.
- [ ] Exact source evidence is resolved by trusted code.
- [ ] Missing/ambiguous assertion evidence is preserved as a grounding failure.
- [ ] Assertion extraction does not require one of the 20 canonical predicates.
- [ ] Assertions that are not naturally binary remain representable at the assertion stage.
- [ ] Assertion extraction cannot create canonical entities.
- [ ] Raw/rejected assertion proposals are preserved where available.

## Acceptance Criteria — Canonicalization Stage

- [ ] Canonical normalization occurs after assertion grounding.
- [ ] The normalization stage sees the frozen symbol table and grounded assertions.
- [ ] The normalization stage cannot create entities.
- [ ] Every compiled relationship uses the existing canonical predicate registry.
- [ ] Every compiled structured proposition uses the existing SPEC-010 vocabulary.
- [ ] Claims remain available for source meaning that should not be promoted to stronger graph semantics.
- [ ] `UNCOMPILED_ASSERTION` / abstention is explicit and reviewable.
- [ ] Abstention does not fabricate unsupported semantics.
- [ ] Canonicalization failures are distinguished from assertion-extraction and grounding failures.
- [ ] No uncompiled assertion is silently dropped from evaluation accounting.

## Acceptance Criteria — Assertion Fidelity Review

Before inspecting live assertion output, fix the assertion-review categories.

Recommended:

```text
FAITHFUL
PARTIAL
DISTORTED
UNSUPPORTED
```

For the live result:

- [ ] Review all assertions if the set is practical, otherwise use a deterministic declared sample plus all assertions that compile canonically.
- [ ] Report faithful assertion count/rate.
- [ ] Report partial/distorted/unsupported assertions separately.
- [ ] Do not let downstream canonical correctness hide assertion-stage distortion.
- [ ] Distinguish assertion extraction quality from canonicalization quality.

## Acceptance Criteria — Canonical Semantic Review

Use the existing SPEC-012 review categories unless a change is documented before live inspection:

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

- [ ] Review every compiled relationship and structured proposition where practical.
- [ ] Report canonical semantic precision = supported / reviewed compiled semantic items when denominator is non-zero.
- [ ] Compare directly against the preserved SPEC-012 6/16 (37.5%) reviewed proposal precision, while clearly noting SPEC-012 was rejected and not accepted truth.
- [ ] Compare the known SPEC-012 defects individually: fixed, retained, replaced, or avoided via abstention.
- [ ] Record new assertion-first defects.
- [ ] Report endpoint and predicate quality separately where useful.
- [ ] Do not claim recall/completeness from this benchmark.

## Acceptance Criteria — Abstention Review

- [ ] Count total grounded assertions.
- [ ] Count canonical relationships.
- [ ] Count structured propositions.
- [ ] Count claims generated from assertions.
- [ ] Count uncompiled assertions.
- [ ] Report canonicalization/abstention rates.
- [ ] Review whether abstentions are semantically appropriate.
- [ ] Identify obvious safe relationships that were unnecessarily abstained from.
- [ ] `ASSERTION_FIRST_BETTER` cannot be justified solely by compiling almost nothing.

## Acceptance Criteria — Structural and Grounding Integrity

- [ ] Zero silent entity minting after the frozen symbol stage.
- [ ] Dangling relationship endpoints are measured.
- [ ] Dangling proposition roles are measured.
- [ ] Unknown assertion participants are measured.
- [ ] `KnowledgeModel` round-trip is verified if a trusted parent exists.
- [ ] SOURCE/INFERRED counts are reported.
- [ ] Exact evidence-resolution rate is reported for assertions and compiled semantics where applicable.
- [ ] Missing/ambiguous evidence failures are reported.
- [ ] No grounding rule is weakened relative to SPEC-012.

## Verdict

Final experiment verdict must be exactly one of:

```text
ASSERTION_FIRST_BETTER
NO_MEANINGFUL_IMPROVEMENT
ASSERTION_FIRST_WORSE
MIXED
INCONCLUSIVE
```

The rationale must separately state:

```text
assertion fidelity
structural integrity
grounding integrity
canonical semantic precision
abstention behavior
cost/complexity
```

### `ASSERTION_FIRST_BETTER`

Requires meaningful improvement in canonical semantic precision over the SPEC-012 control without weakened grounding/symbol integrity and without relying on trivial near-total abstention.

### `NO_MEANINGFUL_IMPROVEMENT`

Use when assertion preservation adds machinery but canonical semantic precision remains essentially weak or comparable.

### `ASSERTION_FIRST_WORSE`

Use when assertion-first loses semantic fidelity, grounding, useful coverage, or precision versus the control without compensating trust gains.

### `MIXED`

Use when assertion fidelity/precision improves but cost, grounding, abstention, or another dimension introduces a material tradeoff.

### `INCONCLUSIVE`

Use only when provider/operational failure prevents a fair test.

## Downstream Diagnostic Gate

If and only if a trusted parent `KnowledgeModel` is produced:

- [ ] run existing structure detection unchanged;
- [ ] run existing representation building unchanged;
- [ ] run existing layout unchanged;
- [ ] record structure/representation/layout diagnostics;
- [ ] optionally provide the existing local viewer command;
- [ ] label any viewer as diagnostic pending owner learning review.

Do not run semantic zoom or a child provider call.

If no trusted parent exists, do not render rejected semantics as learner-facing truth.

## Cost / Complexity Accounting

Report:

- assertion-extraction prompt/version;
- canonicalization prompt/version or deterministic-normalizer version;
- whether the SPEC-012 symbol table was reused;
- any fresh symbol-discovery usage if applicable;
- tokens per live call and combined;
- runtime per live call and combined;
- available SPEC-012 control token/runtime comparison;
- authoritative monetary cost or `NOT_AVAILABLE`;
- new models/modules added;
- dependencies added/removed;
- approximate code/architecture surface;
- whether the semantic gain appears worth the added assertion boundary on this benchmark.

Do not fabricate monetary estimates under project convention.

## Failure Preservation

Preserve where available:

```text
raw assertion proposal
assertion grounding result
raw canonicalization proposal
uncompiled assertions
rejected canonical items
request IDs
usage
runtime
exact validation failures
run history
```

Do not repair primary experimental outputs before evaluation.

## Evaluation Artifacts

Expected directory:

```text
examples/evaluations/spec-013-assertion-first-semantic-compilation-<date>/
```

Expected artifacts may include:

```text
source-metadata.json
symbol-table.json
assertion-extraction-result.json
grounded-assertions.json
assertion-review.json
canonicalization-result.json
uncompiled-assertions.json
parent.knowledge.json              if trusted
parent.structures.json             if trusted
parent.representation.json         if trusted
canonical-semantic-review.json
control-comparison.json
report.json
run-history.json
README.md
```

Artifact naming may follow existing conventions if clearer.

## Required Handoff

Report:

1. architecture implemented;
2. exact provider-independent assertion boundary;
3. SourceAssertion schema and why it is minimal;
4. participant-symbol behavior;
5. assertion evidence/grounding behavior;
6. assertion ID and deterministic processing strategy;
7. canonical-normalization architecture;
8. how separation between assertion extraction and canonical commitment is enforced;
9. abstention / uncompiled-assertion representation;
10. confirmation entity minting is prohibited after frozen symbols;
11. relationship-vocabulary changes, expected `none`;
12. proposition-vocabulary changes, expected `none`;
13. grounding-rule changes, expected `none`;
14. canonical `KnowledgeModel` compatibility;
15. exact frozen source identity/hash;
16. whether SPEC-012 symbol table was reused or regenerated;
17. provider/model;
18. prompt/compiler versions;
19. exact live commands;
20. live-call count;
21. retries and confirmation of no hidden retries;
22. assertion extraction outcome;
23. assertion count;
24. assertion grounding counts/results;
25. assertion fidelity review categories and result;
26. canonicalization outcome;
27. canonical relationship/claim/proposition counts;
28. uncompiled-assertion count/rate;
29. structural-integrity result;
30. grounding-integrity result;
31. canonical semantic-review categories;
32. canonical semantic precision;
33. SPEC-012 control precision used for comparison;
34. known SPEC-012 defects fixed/retained/replaced/abstained;
35. new assertion-first defects;
36. abstention-quality assessment;
37. final verdict from the fixed verdict set;
38. verdict rationale by assertion fidelity, structural, grounding, semantic, abstention, and complexity;
39. downstream structure/representation/layout diagnostics if trusted parent exists;
40. local viewer command if available, otherwise `NOT_AVAILABLE`;
41. token usage per call and combined;
42. runtime per call and combined;
43. authoritative cost or `NOT_AVAILABLE`;
44. dependency changes;
45. complexity impact;
46. deviations;
47. exact offline test result;
48. preservation of SPEC-012 and earlier artifacts;
49. main files/artifacts created or materially changed;
50. implementation commit SHA;
51. evaluation/final commit SHA if separate;
52. push confirmation to canonical `origin/main` if owner authorizes push;
53. final working-tree status;
54. confirmation no `DEBRIEF-013` was created.

## Decision Gate After SPEC-013

Do not automatically proceed to the next feature.

### If `ASSERTION_FIRST_BETTER`

Assertion-first becomes the leading candidate semantic compilation architecture for realistic sources. The next step should likely retry the original end-to-end quantum learning slice from the trusted parent boundary before adding unrelated UI architecture.

### If `NO_MEANINGFUL_IMPROVEMENT`

Do not add a fourth semantic pass. Reconsider whether canonical graph precision requires deterministic semantic admission rules, richer assertion semantics, a different provider strategy, or a narrower representation policy.

### If `MIXED`

Identify the precise tradeoff. Do not generalize the assertion layer until the limiting dimension is understood.

### If `ASSERTION_FIRST_WORSE`

Reject the hypothesis for now and preserve the simpler SPEC-012 staged architecture as the better-tested baseline.

### If `INCONCLUSIVE`

Resolve only the operational/provider issue preventing fair comparison.

## Final Constraint

The goal is not to make more graph.

The goal is to answer:

> **Does preserving source meaning before canonical graph commitment make the graph we do produce materially more trustworthy?**

A negative result is fully acceptable.
