# SPEC-018 continuous graph navigation

This deterministic offline experiment preserves the SPEC-006 graph grammar and tests only camera movement over an authored 24-node software-architecture navigation fixture.

Generate:

```sh
.venv/bin/knowledge-compiler prepare-continuous-navigation --output-dir examples/evaluations/spec-018-continuous-graph-navigation-20260904
```

Review:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-018-continuous-graph-navigation-20260904 --port 8018
```

Baseline comparison:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-006-layout-interaction-20260903 --port 8006
```
