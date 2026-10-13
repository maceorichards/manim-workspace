# context_files — <topic> (optional)

Reference notes for **this movie only**: stable facts from its sources,
translated into render settings and code choices. Delete this folder if the
workbench's "Decisions in force" is enough.

These notes are tracked in git alongside `main.py`, so keep them free of
absolute paths (those belong in the gitignored `SOURCES.local.md`) and of
source content copied word for word.

## What goes where

- **Here:** facts from the sources that don't change while you iterate, such as
  a table mapping a source's colors to Manim colors, a spec for each clip's
  visual, or fixed durations and sizes.
- **`WORKBENCH.md`:** decisions still in flux. They get rewritten after each
  render and pruned once `main.py` reflects them.
- **`<area>/<module>.py` or `common.py`:** conventions shared with other
  movies in the area, or with every area (e.g. a neuron-color scheme). Put
  shared things in code, not in notes.

## Rules

- **Translate, don't copy.** Write the decision a source leads to, not the
  source itself. For example: "target 1920x1080 → `just render … hd`;
  background `#0B1020` → `camera.background_color`; accent → `BLUE_C`;
  ≤ 8 s". The external files stay the source of truth.
- **Cite each note's source** by its label in `SOURCES.local.md` plus the date
  you read it, so you know which notes to recheck when a source changes.
- One short markdown file per concern, e.g. `theme.md`, `sizes.md`, `timing.md`.
