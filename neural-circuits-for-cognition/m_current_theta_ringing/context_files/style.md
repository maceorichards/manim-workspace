# Style — shared by the four Prescott-deck (7-slide outline) videos

This file is identical in `sinusoids_to_power_spectrum`, `iv_curve_assembled_unbent`,
`eigenvalues_integrator_vs_resonator` and `m_current_theta_ringing`. Colours, the model and the helpers live in
code: `neural-circuits-for-cognition/prescott2008.py` (read-only for topic builders).

Sources: deck spec ("Video production notes"; each slide's "Video visuals"); deck video-box
size from the deck build manifest (v4); the old topics' style notes (workspace look). Read
2026-09-30.

## Delivery

- **1920 × 1080, 16:9.** It fills an 8.89 × 5.0 in box on a 13.333 × 7.5 in slide, so it is
  about two-thirds of the slide width.
- MP4 (manimgl's default H.264 output). fps is set per video in its `contract.md`: 60 for fast
  motion, 30 otherwise.
- **Silent.** Played on click. The first frame must read sensibly when paused. The last frame is
  a usable still: hold it ≥ 1 s and export it as a PNG.
- **Output names come from the topic, never from the deck position.** Render with
  `--file_name <topic>` so the movie is `videos/<topic>.mp4`, and save the end frame as
  `videos/<topic>_end.png`. The user copies the files into the deck by hand. Nothing in this repo
  writes to the deck folder.

## Frame and render commands

- Frame: 14.22 × 8 units (x ∈ [−7.11, 7.11], y ∈ [−4, 4]), 135 px per unit at 1080p. Keep ink
  inside **±6.9 × ±3.85**.
- Asserts: `.venv/bin/python <area>/<topic>/main.py`
- Frames: `.venv/bin/python .claude/skills/manimgl/core/assets/snapshot.py <area>/<topic>/main.py <Scene> --list`,
  then `... <Scene> <indices> --hd`, then read the PNGs. The frames are 16:9, the same as the
  delivered video.
- Timing pass: `.venv/bin/manimgl <area>/<topic>/main.py <Scene> -w -l`. **Do not pass `--fps`**: manimgl 1.7.2 hands it to the scene as a string and the render crashes. Set fps in the scene with `default_camera_config = dict(fps=<N>)` (30 is already the config default).
- Final: `.venv/bin/manimgl <area>/<topic>/main.py <Scene> -w --hd --file_name <topic>`.
- End frame: `... <Scene> -s -w --hd --file_name <topic>_end` saves the last frame as a PNG. Without `-w`, `-s` tries to open a window and fails headless. Check
  where it lands and copy it to `videos/<topic>_end.png` if needed.
- Always run from the repo root, or `custom_config.yml` (black background, CMU Serif,
  saturation 1.5) silently drops.

## Look (workspace 3b1b look — not the deck's white theme)

- Black background, CMU Serif. Labels use `txt()`, math uses `tex()` with a **single string**.
  Both come from `common.py`.
- **Text floors** (the 1080p frame shown ~8.9 in wide): `font_size ≥ 26` for anything the
  audience must read (ticks, footnotes), 30–34 for axis labels and readouts, 36–44 for captions.
  Captions go in one reserved band, top or bottom (the contract says which), one at a time, and
  they replace each other.
- **Strokes:** curves ≥ 3, the main trace 4–5, axes 2, reference/dashed lines 2.
- No title inside the video; the slide has one. Beat headers appear only where the contract
  asks for them.
- **Axes are fixed for the whole video (or for the whole beat, when the layout changes).**
  Compute every range before rendering and never autoscale. The only exception is one the
  contract names explicitly.
- **Slowed model time is always badged** ("×1/40") in a fixed corner. Pick speeds so that no
  oscillation shows fewer than ~12 frames per cycle; at 60 fps, the displayed rate must stay
  ≤ 5 Hz.
- **Determinism:** fix every RNG seed. `main.py`'s `__main__` computes and **prints** every
  number under the contract's "Acceptance checks", and asserts it is within tolerance.
- **Slow runs are precomputed** into `<topic>/cache/*.npz` (gitignored) through
  `P.npz_cache(path, fn, **meta)`. The meta holds the recipe (seed, σ, dt …), so a changed
  recipe recomputes.

## Colour roles (constants in `prescott2008.py` — always use the name)

| Role | Constant | ManimGL colour |
|---|---|---|
| Class 1 / integrator / control / SNIC | `CLASS1` | `BLUE_C` |
| Class 2 / resonator / shunted / Hopf; resonant Z | `CLASS2`, `RESONANT` | `ORANGE` |
| Na⁺ / inward | `NA` | `PINK` |
| K⁺ generic / outward | `K` | `TEAL_C` |
| g_K,dr / w | `IKDR` | `GOLD_C` |
| g_M / z / I_M (green means I_M, nothing else) | `IM` | `GREEN_C` |
| Shunt / dynamic clamp (`P.SHUNT` is the parameter set) | `SHUNT_COLOR` | `PURPLE_C` |
| Voltage traces, sums, text | `VOLT`, `INK` | `WHITE` |
| Secondary text, projector lines, "removed" | `MUTED` | `GREY_B` |
| V-nullcline / w- (z-) nullcline | `V_NULL` / `W_NULL` | `GREY_A` / `PURPLE_A` |
| Moving state point | `STATE_DOT` | `YELLOW` |
| θ band / γ band shading | `THETA_BAND`, `GAMMA_BAND` (+ `_ALPHA` 0.2) | `YELLOW` / `BLUE_B` |
| Kicks, flashes, call-outs | `HIGHLIGHT` | `RED_C` |
| Chip fill (stroke `GREY_B`) | `CHIP_FILL` | `GREY_E` |
| Slide-1-only components | `COMP_3HZ`, `COMP_6HZ`, `COMP_12HZ` | sky / lime / violet hex |

Near-collisions to keep apart: `IKDR` gold vs `CLASS2` orange, and `SHUNT_COLOR` purple vs `W_NULL`
lavender. Never set a pair side by side as competing categories.

Phase-plane markers: stable fixed point = filled dot; saddle or unstable = open circle (black
fill, coloured stroke); state point = `STATE_DOT` with a fading tail.

## ManimGL 1.7.2 footguns (each is silent until you look at a frame)

- `Dot(color=X)`, `txt(..., color=X)` and `tex(..., color=X)` all render **white**. Use
  `fill_color=X`, `.set_color(X)` or `t2c`.
- The CMU Serif Pango font draws θ as ϑ and draws "~" raised. Write θ, γ and "≈" in `tex()`
  (e.g. `tex(R"\theta")`).
- In `tex`: `--` renders as two hyphens (use `\text{\textendash}`), and a bare `:` gets relation
  spacing (use `{:}`). Multi-string `Tex("a", "=", "b")` loses the `=` spacing, so use one
  string with `isolate=`/`t2c`.
- Keep `directories.mirror_module_path` off. Keep `ipython<9`. The `pkg_resources` warning is
  harmless.
- Redrawing many curves every frame is slow at 60 fps. Prefer updating the points of one
  `VMobject` (`set_points_as_corners`) over rebuilding with `always_redraw`, and precompute
  arrays.
- Importing the area module from `main.py`, after `from common import *`:
  `import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent)); import prescott2008 as P`.
