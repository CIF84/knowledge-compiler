# SPEC-013 assertion-first semantic compilation

Final verdict: `ASSERTION_FIRST_BETTER`.

This evaluation used the complete frozen Wikipedia article [Introduction to quantum mechanics, revision 1359567407](https://en.wikipedia.org/w/index.php?title=Introduction_to_quantum_mechanics&oldid=1359567407), licensed under CC BY-SA 4.0, with normalized SHA-256 `9e978db999ee67134d347f91fe9f32934c982f4de9b496e4bf664cb00cce23ea`. It reused the SPEC-012 41-symbol table byte-for-byte.

Exactly two `gpt-5.6-luna` calls ran with `store=False`, SDK retries disabled, no retries, no enrichment, no prompt repair, and no child-resolution call. Assertion extraction produced 24 grounded assertions backed by 25 exact, unique evidence spans. Independent review found 17 `FAITHFUL`, 7 `PARTIAL`, 0 `DISTORTED`, and 0 `UNSUPPORTED`. Canonicalization produced 3 relationships, 0 propositions, 21 claims, and 0 uncompiled assertions. All 3 graph relationships were independently supported, for 100% reviewed precision versus the rejected SPEC-012 proposal's 6/16 (37.5%); no recall or completeness claim is made.

Read `assertion-review.json`, `canonical-semantic-review.json`, `control-comparison.json`, `report.json`, and `run-history.json` before using the trusted parent viewer. Visualization is diagnostic rather than semantic proof.

Launch from the repository root:

```sh
.venv/bin/knowledge-compiler view-representations examples/evaluations/spec-013-assertion-first-semantic-compilation-20260904 --port 8013
```
