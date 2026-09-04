# DEBRIEF-014 — Independent Semantic Admission Gate

## Status

Accepted positive result: `GATE_BETTER`.

## Question

Could one bounded independent semantic admission decision capture meaningful reliability gains before resorting to broad multi-agent deliberation?

## Result

Yes on the frozen nine-candidate benchmark.

```text
positive controls: 3/3 admitted
negative controls: 5/6 rejected or demoted
false rejects: 0
false admits: 1
ADMIT precision: 75%
justified-admission recall: 100%
negative rejection rate: 83.33%
overall agreement: 88.89%
```

One `gpt-5.6-luna` call used 6,035 tokens and 11.951 seconds. No retries, repair, enrichment, rewriting, or additional agent were used.

## Validated Architectural Principle

A narrow independent semantic gate can add substantial value after assertion-first canonicalization without modifying canonical semantic IR.

```text
generator proposes
      ↓
trusted grounding / canonicalization
      ↓
independent gate asks only:
"is this semantic commitment justified?"
      ↓
admit or demote
```

The gate does not rewrite candidates, mint entities, create evidence, or expand the ontology.

This is preferable to broad deliberation at the current evidence level because the decision is smaller, cheaper, easier to audit, and experimentally clearer.

## Multi-Agent Decision

Broad multi-agent semantic deliberation is **not justified yet**.

The project should continue to prefer the smallest independent decision mechanism that addresses an observed error class.

Working principle:

> When reliability fails, first make the decision smaller before adding more decision-makers.

## Sole False Admit

The gate admitted the preserved Pauli candidate:

```text
Pauli exclusion principle
        ↓ CONSTRAINS
electron
```

The source assertion is more precise:

```text
There cannot exist an atom in a quantum state
where two electrons have the same set of quantum numbers.
```

The semantic target is therefore closer to the allowed joint atomic quantum state / quantum-number assignment than to the electron object itself.

The false candidate remains plausible in coarse ordinary language, which makes this a harder failure than obvious wrong-predicate or overstated-causality cases.

## Recurring Endpoint-Compression Family

The Pauli failure belongs to a recurring family already observed across experiments:

- transfer process/destination confusion;
- tunneling compressed to electron;
- tunneling compressed to transistor;
- Pauli constraint compressed to electron.

Common pattern:

```text
source assertion contains richer event/state/condition semantics
        ↓
canonical binary form selects a nearby available entity
        ↓
statement remains superficially plausible
        ↓
source meaning is compressed or shifted
```

## Important Packet Observation

The SPEC-014 Pauli assertion participant list contains:

```text
pauli-exclusion-principle
electron
atom
```

but the independently reviewed missing semantic target — joint quantum state / quantum-number assignment — is not itself present as a frozen assertion participant symbol.

Therefore a simple deterministic rule such as:

```text
candidate endpoints must be a subset of assertion participants
```

cannot detect this failure: the bad `electron` endpoint is already a valid assertion participant.

This weakens the hypothesis that endpoint-role adequacy can be solved purely by set comparison over existing participant IDs.

## Cheapest Next Discriminator

Before introducing another general semantic agent, test whether endpoint-role adequacy can be diagnosed from existing frozen artifacts using deterministic structural signals plus a tiny historical case set.

Questions:

1. Does the candidate endpoint correspond to the grammatical/semantic role being constrained, transferred, measured, etc., or merely appear somewhere in the assertion?
2. Does the assertion text refer to an implicit state/event/condition that is absent from the symbol table?
3. Can existing entity types and predicate role contracts identify impossible or suspicious endpoint compression without domain-specific rules?

This analysis should be offline first.

If deterministic signals cannot distinguish the Pauli case without brittle/domain-specific semantics, the next live experiment should be a narrowly scoped **endpoint-role adequacy gate**, not broad multi-agent deliberation.

## Decisions

1. Accept SPEC-014 as `GATE_BETTER`.
2. Preserve the independent gate as an experimentally validated seam, not yet mandatory production architecture.
3. Do not integrate it universally from a nine-item packet alone.
4. Defer broad multi-agent deliberation.
5. Investigate endpoint-role compression as the next specific reliability uncertainty.
6. Prefer offline/deterministic discrimination before another model call.
7. Do not loosen canonical semantic admission to increase graph density.
8. Keep SPEC-013 assertion-first compilation as the strongest realistic-source semantic baseline.

## Repository Evidence

Implementation commit:

```text
76e1dd12c5546bf9efd1c28e8a43f049b69c51eb
```

Evaluation commit:

```text
be42017a718b58c0e44c3fa1ed7fb1c88e4c0e9f
```

Offline suite:

```text
184 passed
```

## Final Conclusion

A single independent semantic gate caught five of six known bad canonicalizations while preserving all three good ones. This is strong evidence that meaningful reliability improvement does not currently require multi-agent deliberation.

The remaining miss is narrower and more interesting: a plausible endpoint can still be propositionally wrong when the true semantic target is an implicit state, event, or condition absent from the available symbol space.

The next step should isolate that endpoint-role problem rather than making the whole semantic system more elaborate.
