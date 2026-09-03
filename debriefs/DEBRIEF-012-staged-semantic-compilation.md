# DEBRIEF-012 — Staged Semantic Compilation

## Status

Accepted `MIXED` result.

SPEC-012 tested whether separating symbol discovery from semantic linking improves realistic-source compilation on the frozen SPEC-011 quantum benchmark.

## Result

The staged architecture solved the referential-integrity failure exposed by SPEC-011, but it did not produce a trusted parent model.

```text
SOURCE
  ↓
PASS 1 — SYMBOL DISCOVERY
  ↓
41 frozen canonical symbols
  ↓
PASS 2 — SEMANTIC LINKING
  ↓
15 relationships + 12 claims + 1 proposition
  ↓
existing grounding + validation
```

Pass 1 succeeded. Pass 2 had zero dangling relationship endpoints, zero dangling proposition roles, zero unknown symbols, and no entity creation. One non-verbatim evidence quote failed unchanged grounding validation, so the entire candidate was rejected.

## Structural Finding

The symbol-table hypothesis worked for the problem it targeted.

SPEC-011 produced dangling references in two independent one-pass attempts. SPEC-012 produced none. This is strong evidence that realistic-source compilation should separate symbol discovery from semantic linking.

## Grounding Finding

Pass 2 resolved 27 of 28 evidence quotes exactly and uniquely. One missing/non-verbatim quote caused fail-closed rejection.

Do not weaken this rule yet. The rejected proposal still contained substantial semantic error, so item-level evidence repair would risk making an untrustworthy model appear successful.

## Semantic Finding

Independent review found:

```text
SPEC-011 one-pass control: 2 / 11 supported = 18.18%
SPEC-012 staged proposal:  6 / 16 supported = 37.5%
```

This is a meaningful directional improvement but remains far below the precision required for a trusted learning map.

Staging fixed some prior defects, including the black-body causal distortion and wave-function-collapse self-loop. It did not solve semantic attribution generally.

Remaining/new defects included:

- overstated causality;
- wrong predicate selection;
- application-list statements forced into `ENABLES`;
- unsupported `IS_A` attribution around QED/QFT;
- imprecise tunneling and Pauli endpoints;
- one non-verbatim Stern–Gerlach evidence quote.

## Architectural Interpretation

SPEC-012 separates one problem from the next.

Before staging, the model had to discover symbols and reference them consistently in one generation. After staging, symbol identity became coherent, exposing the next bottleneck:

> The compiler still asks the model to jump too directly from source prose into canonical semantic graph grammar.

The remaining failures cluster around two questions that may need separation:

```text
WHAT DOES THE SOURCE ACTUALLY ASSERT?
              ↓
HOW SHOULD THAT ASSERTION BE REPRESENTED?
```

Current:

```text
SOURCE
  ↓
SYMBOLS
  ↓
CANONICAL RELATIONSHIPS / CLAIMS / PROPOSITIONS
```

Emerging hypothesis:

```text
SOURCE
  ↓
SYMBOLS
  ↓
SOURCE ASSERTIONS
  ↓
SEMANTIC NORMALIZATION
  ├── safe binary relationship
  ├── structured proposition
  ├── claim
  └── cannot represent safely
  ↓
KnowledgeModel
```

This is not yet an accepted architecture. It must first be tested against an explicit taxonomy of SPEC-012 semantic errors.

## Cost / Complexity

Staging used two calls and 26,142 tokens versus 13,794 known tokens for the preserved SPEC-011 control retry. It added a real compiler boundary but still produced no accepted parent.

Verdict therefore remains `MIXED`: structural reliability improved, semantic precision improved directionally, grounding failed once, and the total reliability gain is not yet sufficient to justify the additional pass as the complete solution.

## Decisions

1. Keep staged symbol discovery as a validated structural improvement.
2. Do not treat staged extraction as a complete realistic-source solution.
3. Do not weaken grounding or add automatic repair.
4. Do not add a third pass automatically.
5. Do not return to map-navigation or learning-efficacy work yet.
6. Analyze the staged semantic failures before authoring SPEC-013.
7. Test whether premature predicate/endpoint assignment is the dominant common mechanism.
8. Continue using the frozen quantum benchmark until parent semantic compilation becomes trustworthy.

## Repository Evidence

Implementation commit: `acacab6775bbf864b9fdb0b2de3c2e9a52a32707`

Evaluation commit: `11feee1554bd39e5a225b549191b95f93fd009a7`

Offline suite: `160 passed`.

## Final Conclusion

Freezing the symbol space before semantic linking materially improves structural reliability. But coherent symbols do not make semantic linking trustworthy. The next step is an error-taxonomy review to determine whether the remaining failures justify a source-assertion-preservation stage before canonical graph semantics.
