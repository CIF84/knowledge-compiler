# REVIEW-003 — Endpoint-Role Compression

## Status

Decision review. No live call or product implementation authorized.

## Purpose

Determine whether the sole SPEC-014 false admit and related historical endpoint defects can be separated by a cheap deterministic discriminator, or whether a narrowly scoped probabilistic endpoint-role judge is actually required.

## Evidence Cases

### Case A — Pauli exclusion principle

Grounded assertion:

```text
The Pauli exclusion principle states that two electrons within an atom cannot have the same set of quantum numbers.
```

Evidence expresses a prohibited **atomic quantum state / joint quantum-number assignment**.

Candidate:

```text
Pauli exclusion principle
        ↓ CONSTRAINS
electron
```

Problem: `electron` participates in the assertion but is not the semantic object whose possible values/states are constrained.

### Case B — quantum tunneling → electron

Earlier candidate compressed the tunneling proposition to an electron endpoint although the source semantics concerned electron penetration through a barrier.

Problem: participant object substituted for process/outcome.

### Case C — quantum tunneling → transistor

SPEC-012 improved the endpoint away from electron but substituted the application/device context (`transistor`) for the source-supported penetration process/outcome.

Problem: contextual object substituted for process/outcome.

### Case D — transfer event / destination

Earlier process experiment used an order-command-transfer process as a `TRANSFERS_TO` destination rather than the actual destination component.

SPEC-010 introduced explicit transfer-event roles because binary endpoint compression could not preserve event, object, and destination simultaneously.

## Deterministic Tests Considered

### 1. Candidate endpoint must occur in assertion participants

Insufficient.

Pauli candidate target `electron` is already a valid assertion participant.

Therefore set membership catches unknown symbols but not semantic-role adequacy.

### 2. Candidate endpoint must occur lexically in evidence

Insufficient.

`electron` occurs explicitly in the Pauli evidence and is still the wrong constrained semantic unit.

### 3. Entity-type compatibility with predicate role

Potentially useful as a weak warning, but insufficient as a decisive rule.

`CONSTRAINS` legitimately targets entities, processes, or variables under the current canonical contract. An `OBJECT` endpoint is not inherently invalid.

Making rules such as `Pauli cannot constrain OBJECT` would be domain-specific ontology disguised as validation.

### 4. Candidate endpoints must cover all assertion participants

Incorrect.

Assertions commonly contain contextual participants that should not become graph endpoints. Requiring full participant coverage would reject many legitimate binary compressions.

### 5. Participant-drop count / compression ratio

Useful diagnostic only.

A relationship necessarily compresses many assertions from N participants to two endpoints. Counting dropped participants cannot determine whether the dropped semantics were essential.

### 6. Predicate-role phrase heuristics

Potential examples:

```text
CONSTRAINS → detect values/state/choices being limited
TRANSFERS_TO → detect destination phrase
MEASURED_BY → detect measured subject vs instrument
```

These might catch specific cases but quickly become a hand-built semantic parser and duplicate the role reasoning already performed probabilistically.

No current evidence supports a small universal deterministic grammar sufficient for these cases.

## Review Conclusion

The preserved cases do **not** support a reliable purely deterministic endpoint-role discriminator using current symbols, entity types, lexical occurrence, or participant-set arithmetic.

The critical information is semantic:

> Which participant — explicit or implicit — occupies the role required by the proposed canonical predicate?

In the Pauli case, the correct constrained semantic object is not even available as a frozen symbol. The system must recognize that the proposed endpoint is a participant but still an inadequate compression of the assertion.

## Smallest Credible Next Mechanism

If we test another probabilistic mechanism, it should be narrower than the SPEC-014 general gate.

Proposed task:

> Given one grounded assertion, its evidence, available participants/symbols, a proposed canonical relationship, and the predicate's source/target role contract, decide whether the proposed endpoints faithfully fill those semantic roles.

Possible verdicts:

```text
ROLE_ADEQUATE
SOURCE_ROLE_INADEQUATE
TARGET_ROLE_INADEQUATE
MISSING_IMPLICIT_PARTICIPANT
REQUIRES_STRUCTURED_PROPOSITION
INSUFFICIENT_FOR_BINARY_RELATIONSHIP
```

The judge must not rewrite the relationship or mint a new entity.

## Why This Is Not Multi-Agent Deliberation

This is a single bounded classification decision over an already grounded candidate.

It does not introduce:

- conversational agents;
- iterative critique/repair;
- consensus protocols;
- multiple independent generators;
- arbitration loops.

It is another example of reducing the decision before adding decision-makers.

## Experimental Design Recommendation

Do **not** use only the Pauli case. A one-item benchmark would be meaningless.

Build a small frozen packet containing:

### Negative endpoint-role cases

- Pauli → electron;
- tunneling → electron;
- tunneling → transistor;
- transfer-event → transfer-process destination confusion;
- any other independently reviewed endpoint-compression cases already preserved in repository artifacts.

### Positive endpoint-role controls

Select accepted relationships where:

- endpoints are semantically precise;
- assertions contain additional contextual participants;
- a naive participant-drop heuristic would therefore be insufficient;
- multiple predicate families are represented if available.

The positive controls are necessary to ensure the judge does not simply reject compressed binary relationships.

## Decision Threshold

A live endpoint-role gate is justified only if the offline packet can be assembled from already independently reviewed repository evidence without inventing labels after the fact.

If too few historical cases exist, collect more evidence through future realistic-source runs rather than manufacturing synthetic confidence.

## Recommendation

Proceed in two steps:

```text
STEP 1 — OFFLINE PACKET
assemble and validate historical endpoint-role cases
no live calls

STEP 2 — ONLY IF PACKET IS ADEQUATE
SPEC-015 endpoint-role adequacy experiment
one bounded live call if technically feasible
```

The packet itself is the next discriminator.

## Final Conclusion

The Pauli miss cannot be repaired credibly with simple deterministic endpoint membership/type rules. The true distinction is semantic-role adequacy, especially when the source's real target is an implicit event/state/condition absent from the symbol table.

A narrowly scoped endpoint-role judge is credible, but only after we prove that the repository contains enough independently reviewed positive and negative cases to test it fairly.
