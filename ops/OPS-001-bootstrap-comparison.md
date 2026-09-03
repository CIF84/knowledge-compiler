# OPS-001 Bootstrap Comparison

This is a deterministic, documented comparison of repository startup expectations. It does not claim an exact token or timing benchmark because this workflow does not expose reliable per-file context accounting.

## Before

- Normal implementation prompts repeatedly required broad reading of `README.md`, `ROADMAP.md`, `PROJECT_MEMORY.md`, `ARCHITECTURE.md`, `OPERATING_MODEL.md`, `PROJECT_HEALTH.md`, and prior debriefs.
- The stable ChatGPT/Codex role split had to be reconstructed from project history.
- Canonical documentation commits arriving on `origin/main` between Codex runs invited repeated authorship and safety analysis.
- Persistent unrelated local `README.md` and `ROADMAP.md` edits required repeated reinterpretation.
- Permanent tests asserted a temporary lifecycle state: `DEBRIEF-009` must not yet exist.

## After

- Root `AGENTS.md` supplies stable role, Git, lifecycle, safety, startup, and finish context automatically.
- The active `SPEC-*` or `OPS-*` document is the primary implementation delta.
- Historical documents and debriefs are loaded only when explicitly required or needed to resolve a concrete ambiguity.
- ChatGPT-authored canonical project-document commits are expected repository evolution; path overlap and local-work safety still determine whether a fast-forward is safe.
- Unrelated user changes are identified once, byte-preserved, and excluded from implementation commits without repeated product interpretation.
- The two `DEBRIEF-009` absence assertions are removed. Their surrounding tests continue to enforce durable evaluation output, navigation, source preservation, retry, complexity, and parent-artifact invariants.

## OPS-001 Run Observation

Before `AGENTS.md` existed, this run needed to obtain and read the active OPS contract, inspect the relevant portions of `OPERATING_MODEL.md`, locate lifecycle assertions across the test suite, and inspect the nearby tests. It did not need to read all canonical project-memory documents to make the bounded operational change.

A subsequent normal run can start from `AGENTS.md` plus its active contract and inspect only relevant code and tests. This is observational evidence of fewer mandatory reads and less repeated role/Git reasoning, not a scientific token-savings benchmark.
