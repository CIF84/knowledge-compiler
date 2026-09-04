# SPEC-016 assertion-aware representation

This offline, deterministic projection uses only the accepted frozen SPEC-013 artifacts. It creates no semantic relationships and performs no provider calls.

Generate:

```sh
.venv/bin/knowledge-compiler prepare-assertion-aware-representation --spec-013-dir examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904 --output-dir examples/evaluations/spec-016-assertion-aware-representation-20260904
```

Review:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-016-assertion-aware-representation-20260904 --port 8016
```
