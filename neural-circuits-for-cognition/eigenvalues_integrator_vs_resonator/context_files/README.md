# context_files — eigenvalues_integrator_vs_resonator

**Self-contained:** everything needed to build this video is in these files, plus the area
module `neural-circuits-for-cognition/prescott2008.py` (model, fixed points, I_bif, palette,
cache). Do not open the deck folder listed in `SOURCES.local.md`; it is read-only, and nothing in
it is needed.

- `contract.md` — the build contract for all three parts: header (three scenes + concat),
  must/must-not, colours, layouts in frame units, timelines, captions verbatim, end frame,
  acceptance checks, and the two deliberate deviations from the deck spec (final class 2 step
  1.002× instead of 1.02×; ×1/25 instead of ×1/20).
- `model.md` — the model, verified tables (I_bif, staircase λ, overshoots, onset runs, zoom
  windows, pulse thresholds and grid), simulation recipes, and asserts.
- `science.md` — the concepts, where the video sits in the talk, the speaker lines and likely
  questions.
- `style.md` — delivery, look, colour roles, floors and ManimGL 1.7.2 footguns. It is shared by
  the four Prescott-deck videos; don't edit it here.

Provenance labels cited (see `SOURCES.local.md`): deck spec (slides 1–3; Video production notes;
Code prerequisites), deck model module, paper (Methods and Fig 5, as quoted in the deck spec).
All were read 2026-09-30.
