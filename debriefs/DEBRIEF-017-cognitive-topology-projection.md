# DEBRIEF-017 — Cognitive Topology Projection

## Status

Product verdict: `NO_MEANINGFUL_IMPROVEMENT`.

SPEC-017 reduced text overload but replaced an already successful graph language with a weaker presentation metaphor. Human review strongly preferred the earlier graph baseline.

## Owner's Spontaneous Review

> “it's not much of an improvement.”

> “now all information is gone and i am looking at some visuals that remind me of venn diagrams.”

> “they're interactive, but they don't do much.”

> “i don't understand relationships, trajectories, i don't see anything that would help me infer, deduct, understand.”

> “still massive step back vs baseline.”

Most importantly:

> “i loved what had there. all we really needed was to drag map and leave visuals to move. when you click node close to edge of the screen, new part of the map appears as new nodes are moving to the center of the screen.”

And:

> “this feels like we're reinventing wheel.”

## What SPEC-017 Learned

The failure is not simply excessive text.

SPEC-016 failed because information dominated structure.

SPEC-017 failed because structure was abstracted into presentation proximity/neighborhoods that no longer carried enough explicit semantic meaning.

The owner wants:

```text
nodes
+ directed relationships
+ relationship labels
+ trajectories
+ spatial continuity
+ interactive details/evidence
```

not a replacement visual metaphor.

## Strong Historical Evidence

SPEC-006 already produced a strongly preferred visual grammar.

Owner reaction at the time:

> “006 is insanely good.”

SPEC-007 then established contextual expansion as the preferred conceptual depth mode, but its `Explore` / `Back` navigation felt inelegant.

The owner independently proposed a Google-Maps-like parent-context model.

Therefore the unresolved problem was **navigation**, not graph representation.

## Experimental Mistake

When realistic-source semantics became sparse, the project accidentally reopened the already-validated visual-design dimension.

That produced two regressions:

```text
SPEC-016
replace graph orientation with text-rich assertion surface
→ cognitive failure

SPEC-017
replace graph orientation with presentation-neighborhood topology
→ cognitive failure
```

The correct response is not a third representation metaphor.

## Visual Invariant

Freeze the SPEC-006 graph grammar as the visual invariant until contradictory evidence appears.

Preserve:

- explicit nodes;
- explicit canonical connectors;
- arrow direction;
- relationship labels;
- hierarchy/causal/process/dependency/feedback layouts;
- click selection;
- hover preview;
- synchronized detail/evidence;
- restrained visual design.

Future experiments must not redesign these while testing navigation.

## Product Interaction Model

The desired surface is a **continuous spatial knowledge graph**.

The viewport is a camera over a larger graph.

```text
world graph
      ↓
viewport/camera
      ↓
visible local topology
```

The user should be able to drag/pan the map.

Clicking a frontier node should:

```text
select node
      ↓
make it the focus
      ↓
move/recenter viewport smoothly
      ↓
preserve existing graph context
      ↓
reveal additional neighboring nodes beyond the old viewport
```

The graph moves; the user does not navigate to a new document/card/page.

## Google Maps Analogy

The interaction analogy should now be treated literally enough to guide design:

- one continuous world;
- camera/viewport movement;
- context remains spatially stable;
- new regions enter view as the camera moves;
- local detail appears around the selected location;
- navigation history may exist, but `Back` should not be the primary mental model;
- later semantic-resolution changes may behave like zoom, but should not be conflated with the first navigation experiment.

## Two Independent Axes

Preserve the distinction:

```text
TOPOLOGICAL MOVEMENT
left/right/up/down across neighboring concepts

SEMANTIC RESOLUTION
overview → mechanism → submechanism
```

SPEC-018 should test only topological movement/camera navigation.

Do not combine semantic zoom yet.

## Assertion / Claim Role

Do not put assertions on the map as default visual objects.

Use them behind interaction:

```text
MAP
 ↓ select node/relationship
DETAIL
 ↓ request explanation
GROUNDED ASSERTION / CLAIM
 ↓ inspect evidence
SOURCE EVIDENCE
```

This preserves trustworthy information without making the overview textual.

## Operating-Model Lesson

Add this experimental discipline:

> Once a dimension has a strongly preferred baseline, freeze that dimension while experimenting on another dimension.

The project already follows this principle well for semantic IR. It must also apply it to UX.

SPEC-006 should have remained the visual invariant while semantic and navigation experiments proceeded independently.

## Decision

1. Close SPEC-017 as `NO_MEANINGFUL_IMPROVEMENT`.
2. Reject presentation-neighborhood/Venn-like topology as the primary visual surface.
3. Preserve SPEC-006 as the visual invariant.
4. Treat the unresolved UX problem as continuous graph navigation.
5. Do not redesign representation in the next experiment.
6. Do not add semantic zoom in the next experiment.
7. Do not add live semantic generation in the next experiment.
8. Use a sufficiently large deterministic graph fixture if necessary to test navigation honestly.
9. Keep explanations/evidence latent behind selection.
10. Test camera movement, frontier reveal, and spatial continuity only.

## Recommended Next Experiment

`SPEC-018 — Continuous Graph Navigation`

Primary question:

> Can the proven SPEC-006 graph grammar become a continuous, pannable knowledge surface where focusing frontier nodes smoothly reveals adjacent topology while preserving spatial orientation?

## Final Conclusion

The wheel already existed.

The winning visual representation was the explicit graph. The missing interaction was movement through that graph.

The next experiment should preserve the wheel and add navigation.
