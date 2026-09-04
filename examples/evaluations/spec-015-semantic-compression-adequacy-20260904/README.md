# SPEC-015 semantic compression adequacy

Offline implementation is prepared. The 10-case historical benchmark passed identity, provenance, evidence, candidate, contract, symbol, and blinding checks. Exactly one live `gpt-5.6-luna` judge call is pending explicit owner approval. The frozen REVIEW-003 packet is referenced by hash and is not copied or changed.

After approval, the exact command is:

```text
.venv/bin/knowledge-compiler evaluate-semantic-compression --packet examples/evaluations/review-003-endpoint-role-benchmark-20260904/endpoint-role-packet.json --model gpt-5.6-luna --output-dir examples/evaluations/spec-015-semantic-compression-adequacy-20260904
```
