# Historical source contamination reference

This package is only for the same independent selector's overlap/lineage screening.
It does not supply new candidate documents, candidate rankings, or eligibility verdicts.

Read contamination-reference-manifest.json, family-completeness.json,
normalization.json and recovered-electromagnetism-fingerprint.json first. Passage
files are exact historical UTF-8 input text, not summaries or generated answers.
Source metadata is allowlisted; UNKNOWN means unknown, not inferred.

Exclude the same historical document (including other revisions/excerpts), its
derivatives/paraphrases and materially overlapping content. Missing original
publication bytes are not a license to reuse another passage from that document.
For local inputs of unknown external origin, use the exact text and conservative
content overlap; do not infer a publisher. Ambiguous overlap is quarantined, not
cleared. A nonmatching hash or n-gram set does NOT certify noncontamination.

The recovered response itself is not included. Its original input source,
passage and lineage are UNKNOWN. Its unordered hashed five-word shingles are
an auxiliary fingerprint only; the introductory-electromagnetism/substantive
content blacklist is mandatory even if no shingles match. No phrase ordering,
headings, diagrams or explanatory organization is supplied.

Repository evidence locators are content-addressed blob identities plus source
field pointers. The exact repository-path index is held separately by custody,
not supplied here: it contains context the selector must not receive. No repo
access is required. These locators identify source extraction, not external
publication bytes. Public metadata separately identifies publication hashes.

verify.py verifies package bytes and passage normalization locally, without
network access. It does not adjudicate contamination or establish eligibility.
Use selector-v1.1-authority.txt for the only permitted continuation. If a rule
or source identity is uncertain, preserve uncertainty and stop/quarantine.
