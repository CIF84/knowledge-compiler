# SPEC-039 — Semantic-to-Representation Compiler Gate

Status: `IMPLEMENTED_REVIEWED`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW_PASSED`
Promotion: `CAPABILITY_ACCEPTED_WITH_COVERAGE_GAPS`

## Owner verdict

`SEMANTIC_REPRESENTATION_COMPILER_CONFIRMED_WITH_COVERAGE_GAPS`

## Purpose

Test whether Knowledge Compiler can take source-bounded material, infer enough trusted semantic structure, and deterministically choose and populate a fitting learner-facing representation without handcrafted per-fixture representation logic.

## Accepted findings

SPEC-039 provides convincing evidence that representation strategy can be compiler output rather than UI/fixture logic.

The reviewed evidence establishes that:

- strategy selection is driven by trusted semantic structure rather than domain names, fixture filenames, concept labels, source IDs, or renderer-side inference;
- semantically equivalent structures remain strategy-invariant when labels/domain metadata change;
- materially different trusted structures resolve to materially different representation strategies;
- the compiler supports causal mechanism, reciprocal mechanism, hierarchy/composition, dependency structure, process sequence, focused relationship, compare/contrast recognition, and concise-prose fallback in the evaluated corpus;
- grounding/provenance survives into the representation decision;
- insufficient structure fails closed rather than inventing topology;
- SPEC-038 remains the protected learner-facing renderer/interaction baseline.

## Coverage gaps preserved as evidence

Two important gaps remain deliberately unresolved:

1. `COMPARE_CONTRAST` is recognized semantically, but the protected SPEC-038 baseline has no comparison renderer. The semantic decision is accepted; renderer coverage is incomplete.
2. Worked-example / rule-to-instance capability remains unproven because the committed evaluated corpus contains no sufficiently grounded rule→instance mapping. The negative transfer case correctly fails closed.

These gaps must not be hidden by fixture-specific UI repair or invented semantic data.

## Accepted architectural principles

1. **Representation strategy is compiler output, not UI logic.**
2. **Renderer coverage may lag semantic recognition without invalidating the semantic decision.**
3. **Absence of sufficient trusted structure must produce a weaker representation rather than invented structure.**
4. **Renderer code consumes a semantic representation decision; it is not the authority that infers semantic truth.**

## Protected learner-facing baseline

SPEC-038 remains the accepted learner-facing architecture:

```text
MY MAP
→ remembers revealed territory

WHAT DOES THIS MEAN?
→ represents the current idea using the fitting semantic representation

INSPECT / SELECTED / PREVIEW
→ explains representation-local semantic components without changing learner location

EXPLORE NEXT
→ proposes future traversal
```

## Next uncertainty

The current corpus is heterogeneous but still belongs to the project's development world. The next experiment should test whether the accepted semantic-to-representation compiler generalizes to material it was not developed around.

The next scientific question is therefore:

> Can the frozen compiler process genuinely out-of-sample source material end-to-end without fixture-specific adaptation and produce trustworthy, useful representation decisions?

To preserve blindness, the evaluation harness/compiler should be frozen **before** the final out-of-sample source set is disclosed and executed.
