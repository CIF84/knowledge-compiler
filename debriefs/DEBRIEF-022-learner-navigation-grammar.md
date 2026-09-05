# DEBRIEF-022 — Learner Navigation Grammar

## Status

Final product verdict: `NAVIGATION_GRAMMAR_BETTER`.

The exact owner-reviewed SPEC-022 viewer and interaction state are promoted to
`BASELINE-004 — Learner Navigation Workspace`.

No model calls were made. No semantic vocabulary, semantic artifact,
representation algorithm, representation archetype, layout, styling, or
learner interaction behavior changed during promotion.

## Owner Review

The owner completed cognitive review of the learner interaction grammar and
explicitly accepted it as better.

Review extended beyond the Software Architecture regression control. The owner
also manually verified Economics, Electromagnetism, and History of Printing.
Across those domains, different semantic structures retained different
appropriate representations inside one navigation/learning grammar:

- Economics appeared as causal structure;
- Electromagnetism appeared as feedback and relationship structure;
- History of Printing appeared as enabling and process structure;
- Software Architecture appeared as hierarchy and dependency structure.

This is evidence about the reviewed interface and fixture only. It does not
authorize generalizing, changing, or tuning the representation algorithms.

## What Earned Promotion

### Region as entrance

A region boundary or title acts as an entrance rather than passive decoration.
Entering a region fits the unchanged map camera to its stable world region,
marks the current context, and opens the strongest existing orientation
representation without page navigation.

### Learner-facing representation choice

The learner chooses a region, concept, or relationship. The compiler-facing
representation choices remain available in `?debug=1`, but the default learner
surface does not require the learner to choose among hierarchy, causal,
feedback, process, or dependency labels.

The deterministic selection rules are:

- region orientation — salience rank, then descending concept coverage, then
  stable representation ID;
- concept — best existing containing representation by salience rank, then
  stable representation ID;
- relationship — best existing containing representation by salience rank,
  then stable representation ID.

These are the exact SPEC-022 orchestration rules. Promotion does not broaden or
retune them.

### Contextual semantic depth

The global `Double-slit depth` control is absent from learner mode. Only the
selected `double-slit-experiment` concept exposes `Explore deeper` because it is
the only object with an admitted deeper resolution in the frozen fixture.

Entering depth replaces only the right-hand learning payload. The left map and
camera remain unchanged. The deeper surface supports concept and relationship
selection plus exact evidence inspection. `Return` restores the parent causal
representation and selected double-slit concept without moving the camera.

### One knowledge world

The successful cognitive separation remains:

```text
LEFT:  Where am I / where can I go?
RIGHT: What does this mean?
```

Map and learning selection remain synchronized by stable entity and
relationship identity. Camera movement remains independent from semantic focus.

## Preserved Interaction Grammar

```text
REGION → ORIENT
CONCEPT → UNDERSTAND
RELATIONSHIP → EXPLAIN
CONCEPT + admitted depth → DEEPEN
```

## Product Principle

> **The learner chooses what to understand. The compiler chooses how that
> meaning is represented. A future guided course chooses a trajectory through
> the same knowledge world.**

## Frozen Executable Lineage

The implementation directly reused these restored BASELINE-003 controls:

| File | BASELINE-003 SHA-256 before and after SPEC-022 |
| --- | --- |
| `index.html` | `471257a95c9fd31483e69b436daeed2397f8e052bddc94ddbcf847c19dab2335` |
| `workspace.css` | `53a6c5593da5c5da7935698d6c8682b4f1f542f6d082d96e77c634cb0432d211` |
| `workspace.js` | `a6bb507a4bff2eea0f968ea2d3e3dad736b2db865bc10f50124776aad79ca8de` |
| `workspace-fixture.json` | `a2c8c24bbd58e28f9a41598e22868916c1808133798c738bbf27712124c1b4e9` |

The SPEC-022 viewer adds only isolated executable seams for region entry,
automatic selection, learner-facing control visibility, contextual depth, and
the minimum BASELINE-003 export required to compose those behaviors.

The final executable is frozen at:

```text
baselines/BASELINE-004-learner-navigation-workspace/
```

Its exact hashes are recorded in `baseline-manifest.json` and enforced through
`knowledge_compiler.baseline004.verify_baseline004`.

## Regression Results

- Electromagnetism region entry: PASS; the unchanged region fit to view box
  `1110 750 720 480` and the existing primary feedback representation oriented
  the learner.
- Light: PASS; the hierarchy containing Electromagnetic wave and Light appeared
  automatically, with no deeper affordance.
- Double slit: PASS; the exact frozen SPEC-020 parent representation appeared,
  local depth was offered, and the SPEC-021 projection loaded unchanged.
- Deeper interaction: PASS; 7 concepts, 2 canonical relationships, and 6
  source-backed explanatory items remained interactive with evidence.
- Return and camera invariance: PASS; parent selection and surface restored with
  the same map view box.
- Software Architecture: PASS; concept and relationship selection synchronized
  both panes; focus suppression, zoom, and Overview/Home remained intact.
- Cross-domain owner review: PASS; Economics, Electromagnetism, History of
  Printing, and Software Architecture retained their distinct appropriate
  representations inside the shared grammar.
- Debug separation: PASS; manual presets and compiler metadata remain available
  through `?debug=1` but are hidden in learner mode.
- Browser console: PASS; no errors or warnings.

## Semantic and Representation Boundaries

- semantic changes: none;
- predicate or proposition changes: none;
- representation algorithms changed: none;
- representation archetypes added: none;
- selection/orchestration change: SPEC-022 only;
- source enrichment: none;
- model/live calls: 0;
- hidden retries: 0;
- dependencies added or removed: none.

The deeper projection semantic artifacts remained byte-identical:

- `projection.json` — `8f1d3beb0e9954040f59862c904a6d9d17574f048bdfcb1cc9059d5df3761232`;
- `projection-diagnostics.json` — `324a70df4cb3c05ba13bd2c8bdac7ed08e4d76d09546c10aeb3c5924bb2f2dc0`;
- `semantic-tier-audit.json` — `592b286bde05bf56cd6cd818b9ccb1de3716c7445018765dbc7a2534710935c9`.

## Evaluation and Handoff

- evaluation artifact:
  `examples/evaluations/spec-022-learner-navigation-grammar-20260905/`;
- machine integrity: `PASS`;
- complete offline suite: 274 tests passed;
- focused SPEC-022 / BASELINE-004 regression suite: 20 tests passed;
- deterministic regeneration: byte-identical for generated artifacts, excluding
  the deliberately owner-completed review records;
- human review: `COMPLETE`;
- verdict: `NAVIGATION_GRAMMAR_BETTER`;
- implementation commit: `06064b9`;
- replacement baseline created: `BASELINE-004` only;
- BASELINE-001, BASELINE-002, and BASELINE-003: preserved byte-for-byte.

## Decision

1. Accept SPEC-022 as `NAVIGATION_GRAMMAR_BETTER`.
2. Freeze the exact executable viewer and reviewed state as BASELINE-004.
3. Preserve all three prior baselines independently.
4. Require future experiments to compose with the BASELINE-004 executable
   artifact and pass its hash gate.
5. Treat the cross-domain observation as support for the baseline, not as an
   instruction to generalize representation logic.
6. Keep guided learning future work inside the same world and interaction
   grammar rather than creating a separate course interface.

## Final Conclusion

SPEC-022 made the accepted hybrid workspace legible as a learner-operated
knowledge world without replacing its spatial model. Regions now orient,
semantic objects select their appropriate existing representations, and deeper
resolution appears only where admitted.

The result preserves agency at the right layer: the learner chooses the object
of attention; the compiler chooses the truthful form; a future guide may choose
a trajectory without inventing another interface.
