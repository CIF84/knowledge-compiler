# BASELINE-004 — Learner Navigation Workspace

## Status

Frozen executable product baseline.

Owner approved after direct human review of SPEC-022 with the final verdict:

```text
NAVIGATION_GRAMMAR_BETTER
```

BASELINE-004 does not modify, rename, delete, or supersede BASELINE-001,
BASELINE-002, or BASELINE-003. Those historical baselines remain independent
diagnostic controls. BASELINE-004 records the later learner-navigation grammar
that was accepted on top of the restored BASELINE-003 shell.

## Executable Artifact

The frozen viewer is stored at:

```text
baselines/BASELINE-004-learner-navigation-workspace/
```

Review it with:

```sh
.venv/bin/knowledge-compiler view-representations baselines/BASELINE-004-learner-navigation-workspace --port 8022
```

The machine-readable identity record is:

```text
baselines/BASELINE-004-learner-navigation-workspace/baseline-manifest.json
```

The executable files are byte-for-byte copies of the owner-reviewed SPEC-022
viewer. Their frozen SHA-256 identities are:

| File | SHA-256 |
| --- | --- |
| `index.html` | `2023e876c965f723e796f135460798b1c7538d05b693b979db3128934ec210e6` |
| `workspace.css` | `53a6c5593da5c5da7935698d6c8682b4f1f542f6d082d96e77c634cb0432d211` |
| `workspace.js` | `d9eff687be246fc0ac42506b71d55944bb26a10046be4f8ca38270cd4ee94d33` |
| `workspace-manifest.json` | `e1ed270a97bf182120f3dd74fda76d2c961516f013b686c110f5fd7ebc976344` |
| `workspace-fixture.json` | `c214158c546fcbed1184b22ab6ac52371c49e7801b1ffb548ed453984fa1fb69` |
| `projection.css` | `ecf9e962889be2e5d2b096118cb9f10f4669fffd3ee6197575c0f20c7029597d` |
| `projection-extension.js` | `05ea171074c69f85c64a817ae75741fb6396be3ea2554322df5baa09fed9cc42` |
| `projection.json` | `8f1d3beb0e9954040f59862c904a6d9d17574f048bdfcb1cc9059d5df3761232` |
| `grammar.css` | `7158525143670c4dbfa6294eca9ffc8d55587af00a478744616d87e90050484e` |
| `learner-grammar.js` | `bab6defc170c4e00cfafda4e8afee4d66690d33e3447d38b608543c616f8793b` |

## Baseline Lineage

```text
BASELINE-001
focused learning and explanatory representation
        +
BASELINE-002
continuous spatial navigation
        ↓
BASELINE-003 / SPEC-019
synchronized hybrid workspace
        +
restored executable BASELINE-003 shell / SPEC-021
        +
SPEC-022
learner navigation grammar
        ↓
BASELINE-004
owner-approved executable learner navigation workspace
```

The SPEC-022 executable reused the actual restored BASELINE-003 shell and
interaction engine. The learner grammar was added through isolated region,
automatic-selection, and contextual-depth seams.

## Frozen Interaction Contract

Preserve all of the following together:

- continuous knowledge world;
- two-pane workspace;
- pan, geometric zoom, and Overview/Home behavior;
- stable spatial regions and world coordinates;
- region-as-entrance behavior;
- automatic region orientation;
- automatic representation selection;
- concept and relationship selection;
- map ↔ learning synchronization by stable semantic identity;
- focus suppression;
- contextual deeper-resolution affordance;
- deeper-resolution transition;
- clear Return behavior;
- parent map and camera preservation across depth transitions;
- detail and evidence behavior;
- separation of navigation — “Where am I / where can I go?” — from learning —
  “What does this mean?”.

## Learner Interaction Grammar

```text
REGION → ORIENT
CONCEPT → UNDERSTAND
RELATIONSHIP → EXPLAIN
CONCEPT + admitted depth → DEEPEN
```

The current frozen fixture admits deeper resolution only for
`double-slit-experiment`.

## Product Principle

> **The learner chooses what to understand. The compiler chooses how that
> meaning is represented. A future guided course chooses a trajectory through
> the same knowledge world.**

## Cross-Domain Owner Evidence

The owner manually reviewed the grammar across Economics, Electromagnetism,
History of Printing, and the Software Architecture control. The observed
learning surfaces retained distinct structure-appropriate representations in
the same navigation grammar:

- Economics — causal structure;
- Electromagnetism — feedback and relationship structure;
- History of Printing — enabling and process structure;
- Software Architecture — hierarchy and dependency structure.

This is owner-observed evidence supporting the baseline. It is not permission
to change, generalize, or retune the representation algorithms, ranking rules,
semantic vocabulary, or structure detectors.

## Mechanical Reuse Rule

Future experiments must import/copy/compose with the executable files in the
BASELINE-004 artifact directory and verify them with
`knowledge_compiler.baseline004.verify_baseline004`.

Do not recreate the shell, styling, layout, world coordinates, or interactions
from this Markdown description. A hash mismatch is a failed baseline gate, not
an invitation to update the hashes. Only explicit owner approval may create a
new baseline version.

## Baseline Verdict

`NAVIGATION_GRAMMAR_BETTER`
