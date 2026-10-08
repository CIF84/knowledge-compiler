# SPEC-068 — atomic contract audit

Owner verdict: `PENDING`

Mechanical branch: `ATOMIC_SUBSET_TOO_NARROW`

Recommended next step: `BOUNDED_ATOMIZATION_EXPERIMENT` — **not activated**.

## Result

All 92 frozen SPEC-066 fixtures were audited before subset design. No fixture,
label, source, prior evaluation, production validator, or semantic model changed.

| Classification | Fixtures | Admitted components |
| --- | ---: | ---: |
| EXPLICIT_ATOMIC | 0 | 0 |
| EXPLICIT_COMPOSITE_DECOMPOSABLE | 16 | 32 |
| OPAQUE_ATOMIZATION_UNRESOLVED | 76 | 0 |
| MALFORMED | 0 | 0 |

There are 108 declared carriers, but only 32 native-grammar components admitted
under this increment's explicit-component contract. These belong to 16 fixtures
with fully known component truth. The other 76 fixtures remain unresolved and
excluded; matching an opaque fixture as a truth reference does not admit that
opaque fixture's atomization.

The proof is deliberately restricted: the frozen native AND grammar declares
the units and exact membership. Each declared component becomes its own judge
unit with unchanged text, evidence, scope, and qualification. Exact recomposition
proves no declared conjunct disappeared or was invented. It does **not** prove
that arbitrary English is irreducibly atomic or solve natural-language
decomposition. SPEC-066/067's unresolved findings remain byte-identical.

## Truth and aggregation

Component truth is 24 `ENTAILED`, 8 `UNCERTAIN`, and 0 `CONTRADICTED`.

Truth is derived only by:

- elimination of an explicit positive AND whose component independently matches
  a frozen grounded witness;
- exact component-text identity with a separately frozen proposition label in
  identical evidence/witness authority.

A rejected parent is never distributed into component verdicts. No semantic
similarity, sentence splitting, punctuation rule, model, or new truth judgment
was used. Conflicting or absent component truth remains unresolved and excludes
the fixture from scored future execution. The labels remain authored,
evidence-relative gold, not blinded expert truth.

Eight mixed-validity controls—including `case-023`—have an entailed first atom
and an uncertain second atom. Synthetic offline receipts show that the full
parent fails closed. Supplying only the entailed atom also fails closed for
missing coverage. These are **not** model outputs or measured judge performance.

Receipt aggregation requires all requested atoms, exact membership/binding,
valid per-atom citations, and every required flag `PASS`. Any contradiction
rejects; uncertainty, malformed/missing/duplicate/extra results, failed flags,
or invalid citations fail closed. Neither notes, expected labels, pooled
verdicts, nor a majority can license admission.

## Coverage and proposed budgets

The safe pool retains 16/92 fixtures across all eight domains, but only 2/18
parent-fixture categories: exact entailment and unsupported abstraction.
Sixteen categories are lost. All faithful paraphrase, synthesis, explanatory
abstraction, and valid relation-projection positives are excluded, as are the
subtle quantity/entity/causal/scope drift categories. The component's historical
truth-source category is recorded separately and is not used to inflate parent
category coverage.

No representative subset for the broad semantic-judge evaluation can be formed
from this safe pool. The proposed subset therefore keeps all 16 safe fixtures
as a **narrow control design only**, retaining all eight mixed controls.

The recalculated design is:

- J1: 32 calls, exactly one component per call;
- J2: 8 calls, four components per batch;
- total maximum: 40 calls, zero retries/repairs;
- no sibling components share a J2 batch;
- fixture aggregation happens after independent atom verdicts.

These manifests are proposed and **not authorized**. They do not inherit
SPEC-067's 48-fixture/60-call budget. Inputs contain one exact component and its
evidence/context only; evaluator truth, rationale, categories and witnesses
are excluded. Binding hashes are explicitly supplied for echoing.

Zero model/provider/evaluation-network calls, semantic judgments, source
retrievals, extraction reruns or synthesis calls occurred. Repository-required
Git fetch/push are coordination only, not experimental network execution.
No project-vision update was needed: the fixture/atom distinction is already
canonical. No dependencies or production behavior changed. No promotion or
human verdict is assigned, and no DEBRIEF-068 is created.

## Owner decision

Review the restricted native-component contract and the lost coverage before
authorizing any new packet. The recommendation identifies the next unresolved
boundary; it does not authorize atomization or semantic judging.

Offline deterministic replay:

```sh
.venv/bin/python -m knowledge_compiler.spec068_atomic_contract --replay --output /tmp/spec068-owner-review
```

The adjacent report, 92-fixture audit, truth-derivation proofs, mappings,
quality audit, coverage analysis and manifests contain exact IDs and hashes.
Validation is recorded in `validation-record.json`.
