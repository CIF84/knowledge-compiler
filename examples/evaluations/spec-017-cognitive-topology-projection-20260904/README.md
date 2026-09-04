# SPEC-017 cognitive topology projection

Offline, deterministic topology from the accepted SPEC-013 semantic packet. Presentation affinity controls proximity only and creates no semantic relationship.

Generate:

```sh
.venv/bin/knowledge-compiler prepare-cognitive-topology --spec-013-dir examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904 --spec-016-dir examples/evaluations/spec-016-assertion-aware-representation-20260904 --output-dir examples/evaluations/spec-017-cognitive-topology-projection-20260904
```

Review:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-017-cognitive-topology-projection-20260904 --port 8017
```
