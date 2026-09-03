# SPEC-011 Addendum — Acceptance and Required Handoff

## Authority

This file is the canonical continuation of `SPEC-011-real-source-quantum-learning-slice.md` after the large-file GitHub write boundary truncated that document near the start of its technical acceptance criteria.

**For implementation purposes, SPEC-011 consists of both files together.**

Do not infer the missing tail of the primary file. Use the criteria below.

## Acceptance Criteria — Technical

- [ ] One realistic coherent quantum-mechanics source is selected and provenance recorded.
- [ ] Source redistribution/licensing handling is explicit and safe.
- [ ] The source is materially richer than existing tiny benchmark fixtures.
- [ ] The source is normalized through `SourceDocument`.
- [ ] Real extraction uses the existing provider boundary.
- [ ] Evidence grounding remains exact/fail-closed.
- [ ] Existing canonical relationship semantics remain authoritative.
- [ ] SPEC-010 proposition semantics remain available.
- [ ] No unsupported source enrichment is used.
- [ ] The canonical 20-predicate vocabulary remains unchanged unless repeated real-source evidence proves a hard blocker and the smallest possible change is explicitly justified.
- [ ] No speculative proposition ontology expansion is introduced.
- [ ] Full-source processing is attempted before introducing segmentation unless provider/context constraints make that impossible in advance.
- [ ] If segmentation is necessary, it is deterministic, coordinate-preserving, provenance-preserving, bounded, and explicitly reported.
- [ ] The parent `KnowledgeModel` round-trips successfully.
- [ ] Parent source evidence remains valid against the original normalized source.
- [ ] Existing structure detection is used without broad redesign.
- [ ] Structure counts and scale diagnostics are recorded.
- [ ] At least one learner-facing parent representation is produced if the current architecture supports one truthfully.
- [ ] No hand-authored quantum overview is substituted for a weak machine-generated overview.
- [ ] At least one automatic child-resolution attempt is made against a source-supported focus concept.
- [ ] The selected resolution strategy is explicit and justified from the existing registry.
- [ ] Child output is source-grounded or fails closed with an explicit supported outcome.
- [ ] Successful child output round-trips through semantic, structure, representation, layout, and navigation artifacts.
- [ ] Parent semantic artifacts remain immutable during child compilation.
- [ ] Prior baselines and evaluation artifacts remain unchanged.
- [ ] Existing Contextual/Layers navigation is reused rather than redesigned.
- [ ] Normal automated tests remain offline and deterministic.
- [ ] Full offline test suite passes.
- [ ] Live provider calls, retries, prompt versions, usage, and failures are preserved honestly.
- [ ] No hidden retries, repairs, cherry-picking, or external semantic enrichment occur.
- [ ] Evaluation artifacts are sufficient to reconstruct the experiment without unnecessarily redistributing copyrighted source material.
- [ ] No secrets are committed or exposed.
- [ ] Implementation/evaluation is committed and pushed to canonical `origin/main` before handoff.
- [ ] No `DEBRIEF-011` is created during implementation.

## Acceptance Criteria — Experimental / Evaluation

Machine integrity is necessary but not sufficient.

Before owner review, repository evaluation should establish:

- [ ] source identity and scale are known;
- [ ] source-processing strategy is known;
- [ ] semantic artifacts are structurally valid;
- [ ] source-grounded items have exact valid evidence;
- [ ] inferred items never masquerade as source-grounded evidence;
- [ ] proposition usage, if any, is semantically justified;
- [ ] obvious semantic defects are preserved and attributed rather than hidden;
- [ ] overview/representation output is inspectable;
- [ ] child-resolution outcome and provenance are inspectable;
- [ ] scale/layout limitations are documented;
- [ ] failure attribution identifies the first meaningful bottleneck(s) rather than proposing broad architecture preemptively.

Human acceptance remains pending until the owner uses the exact fixed artifact.

The primary human verdict is:

> **For this quantum-mechanics material, would I prefer to continue learning through Knowledge Compiler, the original source, or a conventional AI textual explanation? Why?**

A valid outcome is `NO` / source preferred / text explanation preferred.

Do not rescue a negative result with opportunistic UI or architecture changes inside SPEC-011.

## Decision Gate After Owner Review

Do not implement this section during SPEC-011.

### If realistic-source compilation is strongly useful

The project has evidence that the Phase I primitive generalizes beyond tiny fixtures. Candidate next uncertainties include active knowledge-map navigation, formal learning comparison, or bounded on-demand compilation.

### If semantic extraction/grounding fails first

Return to that exact layer. Do not optimize UI/navigation.

### If overview/salience fails first

Test overview selection/compression specifically before changing the semantic core.

### If semantic zoom fails first

Return to resolution policy/source scoping using the real-source evidence.

### If navigation becomes the dominant friction

Active 2D map navigation + semantic zoom becomes strongly justified.

### If the artifact is coherent but not preferable for learning

The product thesis itself requires re-examination before additional architecture.

## Required Handoff

When implementation/evaluation is complete, report:

1. exact source title, publisher/authoring institution, source reference, and why it was selected;
2. license/redistribution basis and what source material was or was not committed;
3. source word count and character count;
4. provider, model, extraction prompt/version, and compiler versions;
5. whether full-source processing succeeded directly;
6. whether segmentation was required and, if so, the concrete failure that justified it plus exact segmentation/merge behavior;
7. parent entity, relationship, claim, and proposition counts;
8. SOURCE vs INFERRED counts;
9. grounding/validation failures and how they were handled;
10. deduplication diagnostics at realistic scale;
11. structure counts by type;
12. representation count, salience distribution, and overview/orientation strategy actually used;
13. layout/scale diagnostics and any visible density/crossing/label limitations;
14. selected semantic-zoom focus and why it was selected;
15. resolution strategy used and why;
16. child-resolution outcome;
17. if successful: child entity, relationship, claim, proposition, structure, and representation counts;
18. child grounding/provenance result;
19. parent immutability result;
20. proposition-model or relationship-vocabulary gaps exposed by the real source;
21. repository semantic review findings, including misleading but mechanically valid propositions/edges if any;
22. failure attribution by layer;
23. complete live-call/run history, including retries or provider failures;
24. token usage and authoritative monetary cost if available; otherwise state `NOT_AVAILABLE` rather than inventing a charge;
25. exact offline test result;
26. dependencies added/removed;
27. files added/changed;
28. deviations from SPEC-011 and this addendum;
29. exact command to launch the fixed owner-review artifact;
30. original-source reference/instructions for the owner review;
31. minimal owner instruction: `Use this to try to understand the topic.`;
32. commit SHA;
33. confirmation that `HEAD == origin/main` and the working tree state;
34. confirmation that no `DEBRIEF-011` was created.

Do **not** declare the human learning verdict in the handoff.

## Contract Integrity Note

The split between the primary SPEC and this addendum is an authoring/tooling workaround, not a product architecture decision. Future long contracts should be authored in smaller durable files or through a write mechanism that verifies complete file length after commit.
