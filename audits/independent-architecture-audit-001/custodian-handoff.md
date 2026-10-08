# AUDIT-001 preparation handoff — not for initial auditor

Owner review is pending. The independent audit has NOT been performed, no architecture
recommended, benchmark selected/retrieved/executed, model/provider call made or experiment
promoted. Git fetch/push are repository coordination, not evaluation network activity.

## Owner amendments applied

The locally recovered electromagnetism PDF/RTF are primary historical artifacts, preserved
byte-for-byte with owner-recovered provenance. They supersede the spec's absent-artifact
fallback. PDF is canonical visual, RTF companion. Export metadata does not independently
date the prototype. All 16 PDF pages and companion text were inspected read-only; reader
warnings and visual limitations are recorded, not repaired.

Workstream F's predefined candidates and H's outcome labels are withheld. Document 06 is
an empty independent working space, not the team scaffold. Workstream G's F/K/M benchmark
arm proposal is also withheld: otherwise it would introduce an equivalent menu through
the benchmark. The rest of the five-source selection/blinding/metrics protocol is preserved.
This is an explicit owner-amendment application, not an architecture choice.

The initial brief/package contain no current-team architecture menu. Master manifest,
raw project coordination/specs and `internal-hypotheses-not-for-initial-auditor.md` are
custodian-only; do not upload the entire audit directory or repository into a fresh context.
Historical report fields are exact excerpts with source hashes/pointers, not rewritten
reports. Complete frozen originals remain in the repository for post-freeze trace requests.

## Exact future fresh-context handoff

After owner approves dossier neutrality, give a fresh independent auditor ONLY
`initial-auditor-package.zip` and this instruction:

> Verify initial-package-manifest.json, inspect the original electromagnetism.pdf directly,
> then follow 00-read-first.md and 08-independent-auditor-brief.md. Derive architectures
> independently from the evidence. Freeze diagnosis, alternatives and recommendation before
> requesting any current-team hypotheses. Do not load surrounding project history or plans.

Do not execute that audit in this implementation context. Current owner-review question:
is the dossier complete, neutral and reproducible enough for that independent handoff?

## Reproduction and validation

```sh
.venv/bin/python tools/audit001_prepare.py --check
.venv/bin/pytest tests/test_audit001_dossier.py tests/test_control_plane.py
.venv/bin/pytest
git diff --check
git diff --cached --check -- . ':(exclude)audits/electromagnetism.rtf'
```

Generation without `--check` writes only audit metadata/excerpts/archive. It does not
regenerate a historical source or learner output. ZIP uses sorted entries, fixed timestamps
and stored unchanged bytes; it contains direct PDF/RTF copies, not reconstructed files.
The full manifest has no self-hash/commit cycle; external SHA-256 supplies its identity.
Repository freeze commit refers to input evidence, not the later publication commit.

The complete staged diff check reports 14 trailing-whitespace lines in the immutable
original RTF. Those original bytes are preserved, not repaired. The exact findings and
narrow authored-file check are recorded in `validation-record.json`. This is an original
artifact exception only; new files pass whitespace checks and original hash validation.

Previously untracked `.DS_Store` files are unrelated user state and remain outside the
commit. Two changed hashes during the run without writes by this workflow; observed
preflight/finish hashes and the limitation are recorded in `validation-record.json`.
All previously tracked files except authorized STATUS/active-contract closure
are protected against byte drift. No dependencies or production behavior changed.
