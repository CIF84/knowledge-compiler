# SPEC-033 — Canonical Revealed-Knowledge Tree

## Status

`APPROVED_FOR_IMPLEMENTATION`

## Owner verdict on SPEC-032

`HISTORY_NAVIGATION_REJECTED__REVEALED_KNOWLEDGE_TREE_PREFERRED`

SPEC-032 produced useful evidence but its learning-history tree is not the desired navigation architecture. Repeated route history inflated the tree, duplicated orientations/concepts, eventually exhausted horizontal space, rendered labels vertically, and the deeper-map interaction ultimately stopped responding during owner testing.

Preserve SPEC-032 as historical evidence. Do not patch its history-tree geometry as the primary solution.

## Product decision

The left navigation surface is **not a history of learning**.

It is the learner's **currently revealed knowledge territory**: a canonical, deduplicated, progressively disclosed tree-like projection of knowledge that the learner has actually uncovered.

The durable product model is:

```text
LEFT: MY MAP
revealed knowledge territory
what has entered the learner's visible world

RIGHT: WHAT DOES THIS MEAN?
focused explanation of the selected canonical object

RIGHT/LOWER: EXPLORE NEXT
frontier of trusted knowledge that could be revealed next
```

The learner should not see all knowledge the compiler can potentially expose. The visible map grows through exploration.

## Critical distinction

Do not equate `revealed` with `understood`.

```text
REVEALED KNOWLEDGE
what the learner has uncovered / can navigate

LEARNER STATE
how well the learner understands it
```

SPEC-033 implements only revealed-knowledge navigation. A future learner-state model may attach understanding/calibration evidence to canonical concepts and relationships, but it must remain separate from navigation visibility.

## Why history leaves the navigation surface

Traversal order is autobiography, not topology.

The UI does not need to reproduce:

```text
Economics
  → Software Architecture
    → Printing
      → Economics
        → Electromagnetism
```

merely because that was the order of visits.

Navigation should instead show each revealed canonical object in its logical place once, subject to the projection rules below.

History may still be captured privately as interaction telemetry such as:

- `revealed_at`
- `first_visited_at`
- `last_visited_at`
- `visit_count`
- `revealed_from`

but it must not inflate or structurally define the visible map.

Potential future uses of history include resume, revisit, personalization, retrospective journey views, and empirical pathway discovery. None are current navigation requirements.

## Core interaction metaphor

Use the familiar collapsible folder-tree grammar.

Example:

```text
[-] Electromagnetism
    atom
    [-] double-slit experiment
        electron
        photon
        interference pattern
        [-] wave-particle duality
            complementarity
            measurement

[+] History of Printing

[-] Software Architecture
    API component
    order component
    payment component
    database
    modular order-processing service
```

Only already revealed objects appear.

`Explore deeper` means:

> reveal more of the selected object's trusted underlying knowledge structure.

It must not create `Deeper map / Deeper map / Orientation / ...` history wrappers.

## Canonical identity and deduplication

The visible navigation tree must be built from canonical semantic identities, not visit events.

Requirements:

1. Revisiting a concept does not create another navigation node.
2. Revisiting a relationship does not create another navigation node.
3. Orientation/domain roots are stable canonical roots rather than repeated history entries.
4. A newly revealed child is inserted into the existing revealed structure.
5. Selection changes current focus, not tree identity.
6. The same canonical relationship retains one semantic identity across map, focused explanation, evidence, and continuations.
7. Reciprocal relationships remain distinct canonical claims where semantics/evidence distinguish them.

Where the underlying knowledge topology is not naturally a strict tree, the implementation must choose a deterministic navigation projection without mutating semantic truth. Do not duplicate arbitrary visit-history nodes merely to force hierarchy.

## Collapsibility

Collapsibility is now a first-class scaling primitive.

Required behavior:

- expanded branches expose already revealed descendants;
- collapsed branches hide descendants without forgetting them;
- expanding restores the same revealed subtree;
- current selection's ancestor chain auto-expands as needed;
- unrelated branches retain their user's collapsed/expanded state;
- collapse state is UI/navigation state, not semantic state;
- use familiar `+/-` or equivalent disclosure affordances;
- collapsing must materially reduce visual complexity and horizontal/vertical pressure.

## Large-map movement

Restore a bounded drag/pan capability for the left map workspace if compatible with the existing baseline interaction grammar.

The primary scale-management mechanism is collapse/expand. Pan/drag is a secondary workspace affordance for a revealed tree that can become larger than its viewport.

Scrolling remains valid. Zoom may remain if already useful, but do not make zoom a substitute for collapsibility.

## Frontier semantics

`Explore next` remains outside the revealed map until the learner selects/reveals an item.

Conceptually:

```text
REVEALED TERRITORY     CURRENT FOCUS       FRONTIER
      MY MAP       WHAT DOES THIS MEAN?   EXPLORE NEXT
```

The system may know more than the learner can currently see. That asymmetry is intentional progressive disclosure.

A frontier suggestion becomes part of MY MAP only through an explicit reveal/explore action under the existing trusted semantic rules.

## Learning pathways

Do not implement guided pathways in this packet.

Durable direction:

- knowledge tree/topology = revealed territory;
- pathway = suggested traversal through that territory/frontier;
- history = observed traversal that actually occurred.

These are three different objects.

Future pathways may be curated, generated, personalized, goal-specific, or empirically derived from successful learning histories. A pathway must not restructure the canonical revealed map.

## Learner-state direction

Do not implement quizzes, mastery scores, courses, chapters, progress percentages, or a full learner model in SPEC-033.

Future learner state should be able to distinguish at least:

```text
revealed = true/false
understanding = separate evidence/state
```

and should be capable of attaching to relationships as well as concepts. The navigation tree must not imply mastery merely because an object is visible.

## Labels / product language

Replace history-oriented navigation language such as:

```text
MY JOURNEY
Learning path
```

with revealed-territory language, preferably:

```text
MY MAP
What you've uncovered so far.
```

Retain the successful focused-learning language:

```text
WHAT DOES THIS MEAN?
EXPLORE NEXT
```

Exact typography may follow existing UI conventions; semantic responsibility is the important requirement.

## Failure observed during SPEC-032 review

Owner testing observed two concrete failures:

1. repeated branching/history nesting eventually exceeded available horizontal space and labels collapsed into unreadable vertical text;
2. after selecting `Explore deeper` inside the double-slit experiment, web elements stopped being interactive and the app stopped working.

SPEC-033 must add regression coverage for both classes of failure. Do not assume replacing history with a canonical tree alone fixes the interaction freeze.

## Required implementation work

1. Inspect SPEC-032 implementation and preserve reusable canonical selection/focused-learning behavior.
2. Replace visit-history-driven left navigation with canonical revealed-state projection.
3. Introduce stable revealed-node state keyed by canonical identity.
4. Implement collapse/expand with preserved subtree state.
5. Ensure selecting/revisiting an existing node does not duplicate it.
6. Ensure `Explore deeper` reveals trusted child structure into the existing canonical map rather than adding history wrappers.
7. Restore/retain bounded map pan/drag where useful.
8. Preserve right-pane focused explanation, evidence/provenance, reciprocal relationship semantics, and Explore-next behavior.
9. Diagnose and fix the interaction freeze observed after deeper exploration.
10. Add a synthetic large revealed-tree fixture sufficient to test scaling beyond the tiny current examples.
11. Update deterministic/browser evaluation artifacts for owner review.

## Large-tree acceptance fixture

Create a deterministic synthetic revealed structure with enough breadth/depth to exercise at least ~40–60 visible/revealable objects across several roots/branches.

The purpose is interaction/layout validation, not semantic-quality evaluation.

Acceptance:

- no label becomes character-by-character vertical because indentation consumed the viewport;
- branches can be collapsed to recover a compact usable view;
- current node remains findable and its ancestors visible;
- expanding/collapsing does not duplicate nodes;
- pan/scroll remain responsive;
- right-pane interaction remains responsive after repeated reveals;
- repeated deeper exploration does not create unbounded history wrappers.

## Browser acceptance scenarios

At minimum exercise:

1. reveal several domains and revisit them in an intentionally irrational order;
2. revisit the same concept repeatedly;
3. traverse reciprocal relationships in both directions;
4. reveal deeper structure under double-slit experiment;
5. collapse and reopen that branch;
6. switch to another domain and back;
7. exercise the synthetic 40–60 object tree;
8. continue clicking/selecting after repeated deeper reveals to prove no interaction freeze;
9. verify the focused pane always describes the selected canonical object;
10. verify frontier suggestions remain distinct from already revealed map contents.

## Protected invariants

Preserve:

- canonical semantic truth and grounding;
- evidence/provenance;
- fail-closed behavior;
- reciprocal/multi-edge semantics from SPEC-031;
- role separation established by SPEC-030: navigation answers where/what territory; focused pane answers what it means;
- BASELINE-004 and earlier baselines as immutable historical controls;
- existing semantic identity across synchronized surfaces;
- source-bounded depth behavior where already validated.

Do not mutate old baselines or SPEC evaluation artifacts.

## Non-goals

Do not build:

- visible learning-history navigation;
- a course/chapter/lesson hierarchy;
- quizzes/mastery/progress scoring;
- guided pathways;
- recommendation personalization;
- a general graph database;
- a new semantic ontology solely for navigation;
- 3D navigation;
- eager revelation of the entire underlying knowledge model;
- speculative visual polish unrelated to the observed failures/new architecture.

## Durable documentation update

As part of this packet, align repository memory with the new direction:

- `README.md` — describe the progressively revealed knowledge environment and current `MY MAP / WHAT DOES THIS MEAN? / EXPLORE NEXT` product model;
- `ARCHITECTURE.md` — distinguish canonical knowledge topology, revealed navigation state, learner state, history, frontier, and future pathways;
- `ROADMAP.md` — retire learning-history navigation as a direction, make canonical revealed-tree navigation the current UI frontier, and move learner-state/pathways after it;
- `PROJECT_MEMORY.md` — record the owner decision that history is telemetry/future evidence rather than visible topology;
- `STATUS.md` — point to SPEC-033 as the active approved packet and record SPEC-032 owner verdict.

Documentation must clearly distinguish implemented behavior from accepted direction. Do not claim SPEC-033 behavior is implemented before implementation/review.

## Acceptance criteria

Machine gate:

- full existing test suite passes;
- new canonical reveal/dedup/collapse tests pass;
- large-tree scaling tests pass;
- interaction-freeze regression passes;
- no protected baseline artifact changes;
- `git diff --check` passes.

Owner review gate:

The owner should be able to say all of the following after using the candidate:

1. The left pane feels like a map of knowledge uncovered, not a diary of clicks.
2. Revisiting knowledge does not visibly duplicate it.
3. Collapse/expand makes a large map manageable.
4. Deeper exploration reveals structure in place.
5. The right pane remains the focused explanation surface.
6. Explore-next still feels like the frontier of what could be revealed.
7. The app remains interactive after repeated deep exploration.
8. The tree remains legible at materially larger scale.

## Handoff

Implement and validate SPEC-033, then stop for owner review.

Do not promote a new baseline automatically.
Do not begin learner-state or guided-pathway implementation.
Do not commit/push implementation until the normal owner/ChatGPT approval boundary unless repository operating rules explicitly authorize the relevant promotion step.
