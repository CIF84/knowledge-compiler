# OPS-002 continuous interface baseline restoration

This offline candidate integrates BASELINE-001 interaction clarity, the accepted SPEC-006A focus treatment, SPEC-018 continuous navigation, and bounded pointer-centered geometric zoom. It is not BASELINE-002; owner review remains required.

Generate:

```sh
.venv/bin/knowledge-compiler prepare-interface-restoration --output-dir examples/evaluations/ops-002-continuous-interface-baseline-restoration-20260905
```

Review:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/ops-002-continuous-interface-baseline-restoration-20260905 --port 8020
```

Baseline comparison:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-006-layout-interaction-20260903 --port 8006
```
