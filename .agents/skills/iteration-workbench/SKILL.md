---
name: iteration-workbench
description: Queue animation work as a checklist and build one selected item at a time. Use for any ManimGL work that spans more than one beat, whenever the user describes where a scene is heading, sketches several things they want to see, or says "first ... then ...". Also use when resuming work on a topic that already has a WORKBENCH.md.
---

# Iteration Workbench

An explainer is discovered by looking at frames, not by planning. The workbench
is the queue of things worth looking at next. It is cheap to rewrite while the
direction is fluid and gets pruned once the scene file carries the result.

## Contract

- **One batch at a time.** Build only the checklist item or items the user
  selects, then stop and hand back. Never continue into the next item because
  it is obvious, small, or already described.
- **Describing the future queues it.** When the user says what they want to see
  after this, that is a checklist entry, not an instruction to build it. Write
  it down and say it is queued.
- **Present, then wait.** After shaping the checklist, show it and let the user
  choose. Do not choose for them.
- **Current truth.** Intent, decisions, and pending items describe what is true
  now. Rewriting them after a render changes your mind is normal.
- **Look before reporting.** An item is not resolved until you have rendered
  its frames and read them.

## Open or resume the workbench

The workbench lives next to the scene file it serves:
`<area>/<topic>/WORKBENCH.md`, e.g.
`learning/information_and_neural_coding/WORKBENCH.md`. Honor a path the user
gives instead. Create the file when the topic does not have one; for a new topic, run
`just new <area> <topic>` first, which brings a workbench with it.

One file per topic, one section per initiative. Before the first change, read
the current `main.py`, and read the source the scene is built from (lecture
notes, paper, problem set) when the initiative depends on it.

```markdown
## <Initiative>

Status: Shaping | Building | Parked
Scenes: <scene classes this initiative touches>

### Intent

<What the viewer should end up understanding. Not a solution.>

### Decisions in force

- <Current constraint, convention, or chosen direction.>

### Checklist

- [ ] <One beat, or one visual question about an existing beat.>
- [x] <Resolved item.>
  - Outcome: kept | revised | discarded — <what the frame showed>

### Open questions

- <Question whose answer would change a queued item.>

### Parking lot

- <Undeveloped idea. One line. No task trees.>
```

A checked box means resolved, not necessarily kept.

## Shape

1. Answer factual questions from the file, the frames, and the source material
   before asking the user anything.
2. Ask only about decisions that change what gets built. Give a recommendation.
3. Add one item, a few items, or a new initiative section.
4. Record real ordering constraints only; leave everything else reorderable.

A good item is one beat of a scene, or one question about a beat that a single
rendered frame can answer: *does the 3D box read at this camera angle?*, *does
the posterior go bimodal on the flank?* If an item needs more than a handful of
`self.play` calls to answer, split it.

A bad item is a whole scene, a "polish pass", or anything whose result you
cannot look at.

Stop when at least one item is selectable. Show the checklist and wait.

## Build

1. Note which items the user selected; set the status to `Building`.
2. Write the beat. Keep the leading `##` cell comment stable — renaming it
   discards the Manim Notebook checkpoint (see `MANIM_WORKFLOW.md`).
3. Verify, in this order:
   - `just check <area>/<topic>` — the `if __name__ == "__main__"` asserts on
     the pure functions, which need no rendering.
   - `just list <area>/<topic> <Scene>` — confirms the scene runs end to end
     and numbers the frames.
   - `just snap <area>/<topic> <Scene> <indices>` — then **read the PNGs**.
     Check for text over text, anything touching the frame edge, leftovers from
     an earlier beat, and a `Tex` that rendered as prose.
   - Do not render (`just render`, `-w`, `--hd`, `--uhd`) while iterating.
4. Record an outcome for every selected item, naming the observation that
   decided it: `revised — at a 5 Hz baseline the conditional is a near-delta
   spike that renders as a wall and hides the surface`.
5. Append anything the work surfaced — a new item, an open question, a parking
   lot line — without building it.
6. Reconcile intent and decisions with what happened, then hand back.

## Retcon

When a frame or a preference changes the direction:

1. Rewrite **Intent** and **Decisions in force** first.
2. Split, combine, reorder, replace, or delete queued items to match.
3. Keep a discarded attempt only when its outcome stops a likely repeat.
   Tuning-parameter churn is not worth keeping; "this camera angle hides the r
   axis" is.

## Keep it light

- Detail only for the active initiative.
- Prune resolved items once `main.py` carries the result: the scene file, its
  docstring, and its beat comments are the record. There is no lock-in step and
  no archive section.
- Park a whole future direction as one line, not as a pre-expanded checklist.
- Save to memory only what outlives this topic — a ManimGL footgun, a rendering
  constraint, a stated preference.
