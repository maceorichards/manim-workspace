# context_files — m_current_theta_ringing

**Self-contained:** everything needed to build this video is in these files, plus the area
module `neural-circuits-for-cognition/prescott2008.py` (model, 3-D fixed points, I_bif, V–z
nullcline, FIG9 sets, noisy simulation, cache, palette). Do not open the deck folder listed in
`SOURCES.local.md`; it is read-only, and nothing in it is needed.

- `contract.md` — the build contract: purpose, must/must-not, layouts, both beats' timelines,
  captions verbatim, end frame, acceptance checks, and the recorded deviations from the deck spec
  (per-segment windows with shared spans; retuned noise and holding levels; I_M 2.11).
- `model.md` — the model, noise model, verified run tables (Beat A, Beat B), rejected settings,
  the lag and peak-ratio definitions, caching, and asserts.
- `science.md` — the argument of the slide (Figs 2, 8, 9), honesty notes, the speaker line and
  likely questions.
- `style.md` — delivery, look, colour roles, floors and ManimGL 1.7.2 footguns. It is shared by
  the four Prescott-deck videos; don't edit it here.

Provenance labels cited (see `SOURCES.local.md`): deck spec (slide 6; Code prerequisites; Video
production notes), paper (Methods noise model; Fig 8 and Fig 9 legends), deck model module. All
were read 2026-09-30.
