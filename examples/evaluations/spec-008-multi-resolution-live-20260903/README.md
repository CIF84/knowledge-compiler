# SPEC-008 review

This directory preserves the original-source live outcomes. Generated child files and Explore actions exist only for successful compilations.

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-008-multi-resolution-live-20260903 --port 8000
```

Compare handcrafted references separately with the SPEC-007 viewer on port 8001.

The first run, preserved in `../spec-008-multi-resolution-20260903/`, did not call
the provider because `OPENAI_API_KEY` was unavailable. `run-history.json` records
that preflight failure alongside this directory's authorized live attempt. No live
domain was retried. The richer-source procedure was not triggered because neither
live result was `INSUFFICIENT_SOURCE_DETAIL`.

`repository-semantic-review.json` records an independent inspection of the accepted
Economics child and the rejected Software Architecture response. The owner-facing
questions remain intentionally unanswered in `human-review-template.json`.
