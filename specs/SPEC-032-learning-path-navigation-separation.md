# SPEC-032 — Learning-Path Navigation Separation

Status: `APPROVED_FOR_IMPLEMENTATION`
Authority: `OFFLINE_ONLY`
Human gate: `OWNER_REVIEW`
Promotion: `NOT_AUTHORIZED`

## Primary uncertainty

> Can the learner-facing interface separate navigation history from domain explanation so that the learning surface regains explanatory primacy, while the navigation map becomes a simple learner-specific path through concepts rather than a literal projection of the internal knowledge graph?

## Owner verdict on SPEC-031

Record SPEC-031 as:

```text
RELATIONSHIP_MULTIPLICITY_CONFIRMED
```

Owner evidence:

- reciprocal Electric field / Magnetic field directions are independently selectable;
- the contextual relationship chooser works as intended;
- map direction and learning-surface direction agree;
- evidence follows the selected canonical edge;
- no material defect was found in the narrow SPEC-031 target behavior.

However, successful completion exposed a larger product-architecture concern:

- the current navigation map has become too responsible for explanation and semantic structure;
- the earlier SPEC-006/007-era learning surface was substantially stronger for learning/explanation;
- later work successfully solved much of navigation, recursion, semantic identity, provenance, state coherence, and relationship multiplicity;
- the next step should preserve those technical capabilities while reducing how literally the learner-facing map exposes them.

See `debriefs/DEBRIEF-031-reciprocal-and-multi-edge-relationship-semantics.md`.

## Why this is next

The dominant question is no longer whether the current graph can be made more semantically correct.

It can.

The question is whether the current learner-visible architecture matches the technical capability now available.

The existing interface partially conflates four concerns:

```text
1. internal domain knowledge
2. learner-facing explanation
3. next-step discovery
4. navigation/traversal history
```

This has created unnecessary coupling between the map and learning surface.

The next experiment should test a cleaner decomposition.

## Core product model

Establish these separate responsibilities:

```text
KNOWLEDGE MODEL
What is known?
What canonical concepts, predicates, explanations, and evidence exist?

LEARNING SURFACE
What am I learning right now?
What representation best helps me understand it?
What evidence supports it?

EXPLORATION SUGGESTIONS
Where could I go next from here?
Which nearby concepts or questions are plausible continuations?

LEARNING-PATH NAVIGATION
How did I get here?
What path have I travelled?
Where did I branch before?
How can I return to an earlier point in that journey?
```

## Strongest distinction

The experiment must make this distinction explicit:

```text
knowledge graph != learning-path graph
```

The internal knowledge graph models the domain.

The learner-visible navigation graph models traversal history.

A learning-path edge means approximately:

```text
learner travelled from A to B
```

It does **not** automatically mean:

```text
A CAUSES B
A PART_OF B
A INDUCES B
A EXAMPLE_OF B
```

Canonical domain relationships remain available to the engine and learning surface, but the navigation path must not be forced to visualize them simply because they exist.

## Frozen control and protected state

Preserve byte-identically:

- BASELINE-001 through BASELINE-004;
- all historical SPEC-023/FIX-023 through SPEC-031 evaluation artifacts;
- frozen SPEC-020 semantic material;
- SPEC-021 explanatory projection semantics;
- trusted semantic vocabulary, grounding, provenance, admission, and fail-closed behavior.

Preserve the SPEC-030 learning-surface role-separation capability and the SPEC-031 relationship-multiplicity capability as implementation infrastructure.

Do not revert repository history or restore historical UI code wholesale.

Recover the explanatory **principle** of the earlier learning surface, not its old implementation state.

## Experimental variable

Only this product-architecture variable is in scope:

```text
learner-visible navigation responsibility
```

Specifically, replace the current assumption:

```text
navigation map ~= visible domain knowledge graph
```

with:

```text
navigation map = learner traversal history
```

while keeping the existing knowledge/semantic engine available behind it.

## Required learning-path model

Implement the smallest deterministic traversal-history model sufficient to demonstrate the architecture.

At minimum, a path node must retain:

- stable concept/object identity;
- learner-facing label;
- traversal parent or equivalent path ancestry;
- current-position state;
- branch identity/history sufficient to revisit a previously travelled branch.

A path edge needs only traversal semantics for this experiment.

Do not copy canonical domain predicates onto traversal edges unless a future design explicitly requires it.

Conceptually:

```text
Electromagnetism
      ↓
Double-slit experiment
      ↓
Interference pattern
      ↓
Wave-particle duality
      ├──→ Principle of complementarity
      ↓
Photon
```

The geometry may remain graph-like, but it represents the learner's journey.

## Navigation behavior

The learning-path surface must answer:

```text
Where am I in my exploration?
How did I get here?
Where have I been before?
Can I return to an earlier visited point?
Can a new branch grow from there?
```

Required behavior:

- selecting a previously visited path node returns the learner to that learning object;
- selecting an exploration suggestion appends a new traversal step from the current path node;
- returning to an earlier path node and choosing a different suggestion creates or reuses a visible branch rather than deleting unrelated history;
- current position is visually explicit;
- previously visited path remains visible enough for orientation;
- navigation does not depend on current recursion depth;
- no stack of "return" buttons is required to recover prior context.

## Arbitrary-depth requirement

The path model must remain structurally valid after repeated exploration.

Do not special-case shallow depth.

Add deterministic synthetic coverage showing at least a ten-step traversal with branching.

The learner-visible behavior at step 10 must use the same grammar as step 1:

```text
choose next object
→ current learning object changes
→ traversal history extends
→ prior path remains navigable
```

## Learning-surface responsibility

The right learning surface must regain explanatory primacy.

It should answer:

```text
What does this mean?
Why does it matter?
How should I understand it?
What representation makes it clearest?
What evidence supports it?
```

Preserve the deterministic representation resolver introduced in SPEC-030.

The right pane may render, where already supported by trusted data:

- concise concept explanation;
- focused canonical relationship representation;
- comparison;
- causal/local chain;
- hierarchy;
- evidence/provenance;
- source-backed explanation;
- another existing deterministic representation form.

It must not be required to mirror the learning-path graph.

## No map ↔ explanation mirroring requirement

Remove the product requirement that navigation geometry and learning-surface geometry mirror each other.

They should agree only on the current learning object / semantic focus required to render the learner-facing explanation.

The stronger desired relation is:

```text
current traversal node
        ↓
current learning object
        ↓
learning representation
```

not:

```text
left graph geometry ↔ right graph geometry
```

Do not introduce duplicated navigation state on the right.

## Exploration suggestions

Move "where can I go next?" out of the navigation graph for this experiment.

Create a small deterministic suggestion area associated with the current learning object.

It may appear in or adjacent to the learning surface.

At minimum, each suggestion must resolve to a trusted existing semantic object available from committed data.

A suggestion should be framed as a learner-facing continuation, not as raw graph metadata.

For example conceptually:

```text
Explore next

→ Why measurement changes what we observe
→ What a photon is
→ Principle of complementarity
```

Do not use model generation or external calls.

For this packet, derive suggestions deterministically from already committed trusted semantic material using a minimal fixed resolver/ranking rule.

The purpose is architectural proof, not final recommendation quality.

## Suggestion selection semantics

Selecting a suggestion must atomically:

```text
1. resolve one trusted semantic object
2. make it the current learning object
3. append or activate the corresponding traversal-path node
4. render its learning representation
```

No surface-to-surface synchronization shortcuts.

The navigation path and learning surface should both derive from the same current learning object, but their visual structures remain independent.

## Preserve semantic engine capability

The experiment must not weaken or delete the technical capability established through SPEC-031.

Preserve:

- canonical semantic identity;
- trusted predicates;
- directed relationship identity;
- reciprocal/multi-edge multiplicity;
- source-backed vs canonical distinction;
- evidence/provenance;
- representation resolver;
- canonical interaction/event path where semantic interaction still occurs;
- recursive/depth-independent semantic handling;
- fail-closed behavior.

The navigation UI may become simpler even while the internal engine remains rich.

## Relationship exploration

Do not remove the ability to learn about a relationship.

If the current learning object is a canonical relationship, the learning surface may continue using the focused relationship representation from SPEC-030/031.

However, the learning-path graph should record the traversal in a simple learner-history form rather than reproducing all relationship geometry.

The implementation may choose a concise path-node label such as:

```text
Electric field → Magnetic field
```

or another deterministic learner-readable identifier.

Do not create synthetic semantic identities merely for navigation.

## Source-backed explanatory material

Source-backed explanation may remain inspectable through the learning surface, but do not automatically add every evidence/explanation object to the traversal path.

For this experiment, the path should primarily track deliberate learning-object transitions.

Incidental evidence inspection should not necessarily become a new navigation step.

Define and report the exact deterministic rule used.

## Fixed evaluation journey

Use committed fixtures only.

Create at least one coherent owner-review journey beginning in Electromagnetism, for example:

```text
Electromagnetism
→ double-slit experiment
→ interference pattern
→ wave-particle duality
→ principle of complementarity or photon
```

The exact available continuation must come from trusted committed data.

The owner must be able to:

- follow suggestions forward;
- see the traversal history grow;
- jump back at least two steps;
- choose a different continuation;
- see a branch preserved;
- return to a previously visited branch;
- continue learning without the right pane turning into a navigation clone.

Also include a relationship-selection case to prove SPEC-031 capability remains available when needed.

## Cross-domain guard

Retain deterministic smoke coverage in at least:

- Electromagnetism;
- History of Printing;
- Software Architecture.

This packet does not require elaborate curated traversal fixtures for every domain.

The purpose is to prove the separation is architectural rather than an Electromagnetism special case.

## Interaction grammar

The learner-facing interaction model should become simpler:

```text
PATH
click visited node → navigate there

LEARNING SURFACE
interact with explanatory representation → inspect/understand current object

SUGGESTIONS
click suggestion → travel to next object
```

Do not require navigation-map hover to mirror explanatory-pane hover.

Do not require every semantic element inside a learning representation to become a path node.

Do not require path edges to be interactive canonical relationships.

This simplification is intentional.

## Current object invariant

Even though visual mirroring is removed, semantic coherence remains required.

At committed selection boundaries:

```text
current path position
→ current learning object identity
→ learning-surface semantic identity
```

must agree.

Returning to any visited node must restore the correct learning object and a fresh correct representation without stale state from the previously visited branch.

## History persistence within the session

For this experiment, persistence beyond the viewer session is not required.

The traversal path may be in-memory deterministic state.

Do not add accounts, databases, sync, or long-term learner profiles.

However, the state model must be clean enough that persistence could be added later without redefining traversal semantics.

## Preserve best-known UI progress

Do not regress the strongest SPEC-030 learning-surface behaviors merely to simplify navigation.

In particular preserve:

- distinct explanatory representation on the right;
- evidence/provenance;
- focused canonical relationship rendering;
- source-backed explanation rendering;
- ordinary pane scrolling/capacity;
- clear typography and visual hierarchy.

The objective is closer in spirit to:

```text
earlier strong explanation surface
+
newly earned semantic/recursive infrastructure
+
new simple path navigation
```

not:

```text
revert to old UI
```

## No live calls

This packet is `OFFLINE_ONLY`.

Forbidden:

- model/provider calls;
- web retrieval;
- external enrichment;
- embeddings;
- new extraction/canonicalization;
- agent/LLM judging;
- generated recommendations.

Use committed deterministic semantic material only.

## Mechanical gate

Before owner review, verify at least:

```text
BASELINE-001..004 hashes unchanged
SPEC-023/FIX-023 through SPEC-031 historical artifacts preserved
SPEC-020 frozen semantic hashes unchanged
SPEC-021 explanatory payload unchanged
no live/model/external calls
no semantic vocabulary/admission changes
no trusted semantic identity deleted or rewritten
SPEC-030 representation resolver preserved
SPEC-031 reciprocal/multi-edge tests remain passing
navigation graph represents traversal history rather than canonical domain geometry
traversal edges do not masquerade as canonical predicates
suggestions resolve only to trusted committed semantic objects
suggestion selection atomically updates current object + path + learning representation
visited-node navigation restores correct learning object
backtracking and alternate continuation creates/preserves a branch
prior branch remains revisitable
ten-step synthetic traversal passes
ten-step traversal with branching passes
path behavior is depth-independent
source/evidence inspection does not accidentally corrupt traversal history
relationship learning representation remains available
map/path and learning surface agree on committed current object identity
no requirement for hover mirroring between path and learning surface
context/branch switching does not resurrect stale explanation state
Electromagnetism fixed journey passes
History of Printing smoke case passes
Software Architecture smoke case passes
browser console clean
basic navigation layout remains usable at ordinary viewport
full offline suite passes
```

If any machine gate fails, do not request owner review.

## Owner-review artifact

Create an isolated evaluation under:

```text
examples/evaluations/spec-032-learning-path-navigation-separation-<date>/
```

Do not mutate accepted baselines or prior SPEC evaluations.

## Owner review

Do not prime the owner with implementation details.

If the machine gate passes, provide only the low-attention handoff, exact viewer command, and approximately this task:

```text
Start in Electromagnetism and learn naturally. Use the suggested next explorations several times. Watch whether the left side feels like a history of your journey rather than a diagram trying to explain the domain. Go back a few steps, choose a different continuation, and confirm that the path branches without losing where you had already been. Then focus on the right side: does it once again feel like the place where the current thing is actually explained? Sample a canonical relationship and its evidence too. The core question is whether navigation now helps you remember and move through your chain of thought without competing with the explanation surface.
```

## Verdict set

Final subjective verdict must be exactly one of:

```text
LEARNING_PATH_SEPARATION_CONFIRMED
MIXED
NAVIGATION_STILL_EXPOSES_DOMAIN_MODEL
LEARNING_SURFACE_REGRESSED
PATH_MODEL_NOT_USEFUL
INCONCLUSIVE
```

Codex must not assign this verdict.

## Success criterion

`LEARNING_PATH_SEPARATION_CONFIRMED` requires owner evidence that:

- the left navigation surface behaves primarily as traversal history;
- it remains useful after repeated exploration and branching;
- the learner can return to previous visited objects without stack-like backtracking friction;
- the right learning surface is clearly the primary explanatory surface;
- suggestions provide a natural mechanism for choosing a next exploration;
- map/path and learning surface remain coherent about the current learning object without visual mirroring;
- SPEC-030/031 semantic and evidence capabilities remain available behind the simpler UI;
- arbitrary depth does not change interaction grammar;
- no semantic trust invariant is weakened.

## Explicit non-goals

Do not implement:

- personalized recommendation models;
- LLM-generated next questions;
- persistent learner accounts/history;
- collaborative paths;
- global graph search;
- bookmarks/favorites;
- final path-layout algorithm;
- polished animation system;
- universal pedagogical renderer;
- new domain facts;
- new canonical predicates;
- semantic extraction changes;
- automatic semantic depth generation;
- baseline promotion;
- unrelated refactoring.

## Required durable report

Record at least:

- frozen/baseline hash verification;
- files changed;
- previous graph responsibilities removed from learner-visible navigation;
- learning-path state model introduced;
- path-node and traversal-edge semantics;
- branching/backtracking behavior;
- exact rule for when a learner action creates a traversal step;
- exact rule for source/evidence inspection and whether it enters history;
- suggestion resolver and deterministic selection/ranking rule;
- proof suggestions resolve only to trusted committed objects;
- current-object coherence results;
- SPEC-030 learning-surface regression results;
- SPEC-031 reciprocal/multi-edge regression results;
- fixed journey results;
- ten-step + branching synthetic results;
- cross-domain smoke results;
- browser verification;
- console result;
- full offline tests;
- dependencies/live calls;
- deviations;
- commit/push state;
- exact viewer command.

## Low-attention completion handoff

On successful implementation, return only:

- `SPEC-032` completion state;
- focused + full test summary;
- machine-gate result;
- material deviations/dependency changes, if any;
- commit/push/repository-clean state;
- durable report path;
- exact viewer command;
- statement that owner review is required.

Keep implementation detail in the durable report.

## Final constraint

Do not make the learner navigate the internal ontology merely because the engine knows it.

Establish the stronger architecture:

> **The knowledge model describes what is known. The learning surface explains what I am learning. Exploration suggestions tell me where I could go. The learning-path map remembers how I got here.**
