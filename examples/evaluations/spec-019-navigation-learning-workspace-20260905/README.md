# SPEC-019 navigation + learning workspace

This offline integration composes unchanged SPEC-006 structure-aware representations into a BASELINE-002-style continuous navigation world. Stable entity and relationship IDs synchronize both panes.

Generate:

```sh
.venv/bin/knowledge-compiler prepare-navigation-learning-workspace --output-dir examples/evaluations/spec-019-navigation-learning-workspace-20260905
```

Review:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-019-navigation-learning-workspace-20260905 --port 8019
```

BASELINE-001 comparison:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-006-layout-interaction-20260903 --port 8006
```

BASELINE-002 comparison:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/ops-002-continuous-interface-baseline-restoration-20260905 --port 8020
```
