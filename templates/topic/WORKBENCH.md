# Workbench — <topic>

Sources: see `SOURCES.local.md` (gitignored). Name them here by their labels
there (e.g. "deck spec, slide 3"), never by absolute path.

## Workspace smoke scene

Status: Shaping
Scenes: FiringRateCurve

### Intent

A sigmoid firing-rate curve that uses Text, Tex, Axes, and a ValueTracker,
so a broken install shows up here first. Also the example layout for new topics.

### Decisions in force

- Labels use `txt()` (CMU Serif via Pango); math uses `tex()` as a single string.
- `firing_rate` is a pure function checked by the `__main__` asserts.

### Checklist

- [x] Curve, equation and labels fit the frame at 480p
  - Outcome: revised — multi-string Tex lost the spacing around `=` and `Dot(color=)` rendered white; fixed both, moved axes up off the bottom edge
- [x] Manim Notebook loop in Cursor starts and previews cells
  - Outcome: kept — needed `ipython<9`; a black window at start is expected when the cursor is above the first `self.play`

### Open questions

### Parking lot
