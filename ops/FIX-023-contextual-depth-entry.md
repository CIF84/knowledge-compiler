# FIX-023 — Contextual Depth Entry

Status: `IMPLEMENTED_AWAITING_REVIEW`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Purpose

Repair one integration defect in the fixed SPEC-023 owner-review artifact so the already-approved semantic-depth treatment is actually reachable through the normal BASELINE-004 learner interaction grammar.

This is a corrective packet for SPEC-023, not a new semantic experiment.

## Observed owner evidence

The owner navigated naturally to and selected the canonical relationship:

```text
double-slit-experiment → CAUSES → interference-pattern
```

The normal relationship detail and source evidence rendered correctly.

However, no learner-facing `Explore deeper` action was available from that selected relationship.

Therefore the SPEC-023 experimental treatment was not reachable from the semantic object where the learner naturally encountered it.

The owner has **not** evaluated the deeper treatment. No SPEC-023 cognitive verdict may be inferred from this failed entry path.

## Primary uncertainty

There is no new product hypothesis in FIX-023.

The corrective question is simply:

> Can the existing deeper double-slit treatment be entered contextually from the selected canonical relationship, and can the learner return with the parent workspace state intact, without changing BASELINE-004 or the experimental semantic treatment?

## Frozen controls

Preserve byte-for-byte:

- BASELINE-001;
- BASELINE-002;
- BASELINE-003;
- BASELINE-004 frozen executable assets;
- SPEC-020 frozen quantum semantic packet;
- SPEC-021 explanatory projection semantics;
- SPEC-023 deeper treatment semantics/representation content.

Do not redesign or polish BASELINE-004.

Do not change the deeper representation merely to improve the experiment.

## Required learner path

The fixed artifact must support:

```text
navigate normally
      ↓
select double-slit-experiment → CAUSES → interference-pattern
      ↓
normal relationship detail + evidence
      ↓
Explore deeper
      ↓
existing SPEC-023 deeper treatment
      ↓
interact / inspect deeper items
      ↓
Return
      ↓
exact parent learning/navigation state restored
```

## Contextual eligibility

The `Explore deeper` affordance must appear only when the currently selected semantic object has the registered/admitted deeper treatment.

For this frozen experiment, the canonical double-slit relationship/focus is eligible.

Unrelated relationships and concepts must not gain a double-slit depth affordance.

Do not reintroduce a global `Double-slit depth` control.

## Entry seam

Prefer the smallest deterministic integration seam already supported by the learner workspace.

The normal relationship-detail renderer should expose the learner-facing depth action when a stable semantic ID/focus registration says a deeper treatment exists.

Use stable semantic identity rather than matching visible label text where the current architecture permits it.

Do not build speculative generalized infrastructure beyond what this repair requires.

## Parent state preservation

Entering depth must not mutate the parent knowledge world.

Returning must restore at minimum:

- left-map camera position;
- geometric zoom;
- selected parent relationship;
- active parent representation/orientation state;
- relevant right-panel learning state.

Pure semantic-depth transition must not reset navigation.

## Deeper state

When entered:

- the existing SPEC-023 deeper treatment is shown coherently in the learning surface;
- deeper canonical/explanatory items remain interactive as already implemented;
- detail/evidence synchronization remains intact;
- the learner can identify the deeper state and the parent focus;
- Return is clear and restores the parent state.

Do not stack unrelated parent content above the deeper treatment if the existing accepted depth seam already provides a cleaner transition.

## Semantic invariants

The parent canonical relationship remains exactly:

```text
double-slit-experiment → CAUSES → interference-pattern
```

Do not rewrite it.

Do not add new parent semantics.

Do not promote the known rejected/overstated causal item from SPEC-020/021.

Do not fabricate pairwise canonical edges from explanatory assertions.

No semantic vocabulary or grounding/provenance behavior may change.

## BASELINE-004 invariants

Preserve the executable learner-navigation behavior:

- two-pane workspace;
- continuous map;
- pan/drag;
- geometric zoom;
- Overview;
- region entry/orientation;
- automatic learner-facing representation selection;
- concept and relationship selection;
- focus suppression;
- map ↔ learning synchronization;
- evidence/detail behavior;
- current styling/layout/interaction grammar.

FIX-023 may add only the minimum contextual depth entry/return wiring in the isolated SPEC-023 review artifact or compatible integration seam.

## No live calls

`OFFLINE_ONLY`.

Forbidden:

- OpenAI/provider calls;
- external retrieval/enrichment;
- semantic retry/regeneration;
- new assertion extraction/canonicalization;
- embeddings;
- additional model/agent judges.

## Validation

Add focused deterministic checks proving at least:

1. selecting the canonical double-slit relationship exposes `Explore deeper`;
2. unrelated relationships without registered depth do not expose it;
3. activating `Explore deeper` opens the exact existing deeper treatment;
4. parent camera/zoom/selection/representation state survives entry;
5. Return restores the parent state;
6. deeper items remain interactive and evidence-resolvable;
7. BASELINE-004 frozen hashes remain byte-identical;
8. SPEC-020/021/023 semantic payload hashes remain unchanged where frozen;
9. no semantic vocabulary/representation algorithm changes occurred;
10. full offline suite passes.

Where the existing deterministic browser/fixture harness permits it, test the same interaction path the owner used rather than only invoking internal functions directly.

## Owner review handoff

After the machine gate passes, use the low-attention handoff protocol.

Do not provide a long implementation inventory.

The next genuine gate is owner browser review.

Provide the exact viewer command and this instruction only:

```text
Navigate normally to the double-slit experiment. Select its relationship to the interference pattern. Read what the normal view tells you, then click Explore deeper. Spend a little time exploring only what the deeper view gives you. Tell me what you understand after opening it that you did not understand before, and whether anything became more confusing.
```

Codex must not assign the SPEC-023 cognitive verdict.

## Completion state

On successful repair, set this packet to `IMPLEMENTED_AWAITING_REVIEW`, clear the active packet in `STATUS.md`, and record that the next gate is owner review of the repaired SPEC-023 artifact.

## Required durable evidence

Record detailed machine evidence in an isolated corrective/report artifact rather than chat, including:

- verified root cause;
- exact repair seam;
- files changed;
- frozen hashes before/after;
- contextual eligibility tests;
- entry/return state tests;
- deeper interaction/evidence tests;
- full offline test result;
- deviations/dependencies;
- commit/push state;
- viewer command.

## Acceptance criteria

- [ ] Owner-observed missing depth entry reproduced/verified.
- [ ] `Explore deeper` appears on the selected canonical double-slit relationship.
- [ ] No global depth control reintroduced.
- [ ] Unrelated objects do not expose double-slit depth.
- [ ] Existing deeper treatment opens without semantic/representation redesign.
- [ ] Deeper items remain interactive.
- [ ] Parent camera/zoom/selection/representation state preserved.
- [ ] Return restores parent state.
- [ ] BASELINE-001 through BASELINE-004 remain byte-identical.
- [ ] Frozen SPEC-020/021/023 semantic treatment remains unchanged.
- [ ] No live/model/external calls.
- [ ] No semantic vocabulary/grounding/provenance changes.
- [ ] Full offline suite passes.
- [ ] Low-attention owner-review handoff produced.
- [ ] No subjective SPEC-023 verdict assigned by Codex.

## Final constraint

Repair discoverability only.

Do not turn a missing experimental entry point into another UI, semantic, or architecture experiment.
