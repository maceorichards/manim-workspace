# Style — shared by all 15 Prescott-deck videos

This file is identical in every `s??_vid?_*` topic. If you change a convention, change it in
all of them (or, better, move it into code — see "Later" at the bottom).

Sources: deck build contract §4/§7 and the deck style module (palette roles, motif constants,
placeholder box sizes); deck outline "Assembly notes". Read 2026-09-28.

## Delivery constraints (from the deck)

- Each video fills a placeholder box **5.95 × 5.3 in** (aspect ≈ 1.12:1) on a 13.333 × 7.5 in
  slide. Two videos sit side by side on the same build slide (left box / right box).
- **Silent.** No narration, no audio track needed.
- **≤ 25 s** each (the per-video target is in its `contract.md`).
- Set to **play on click**, not autoplay, so the speaker controls pacing. Open on a frame that
  is meaningful when paused (the video will sit on its first frame until clicked).
- **The last frame must work as a still image** in case playback fails. Hold it ≥ 1 s.
- Finished renders go to the deck by hand; the deck itself is not edited from this repo.

## Frame and render settings

- Render at **1344 × 1200** (ratio 1.12). In ManimGL 1.7.2 `FRAME_WIDTH = frame_height ×
  pixel aspect`, so with the default `frame_height = 8` the frame is **≈ 8.96 × 8 units**
  (x ∈ [−4.48, 4.48], y ∈ [−4, 4]). Keep content inside ±4.2 × ±3.75.
- Iterate: `.venv/bin/manimgl <topic>/main.py <Scene> -w -r 672x600`.
  Final: `-w -r 1344x1200 --file_name <topic>` (or `-r 2688x2400` for a 4K-class master),
  so the movie is `videos/<topic>.mp4`.
- `snapshot.py` renders 16:9 frames (854×480 / 1920×1080) today, so its frames are wider than
  the delivered video. Until it takes a resolution flag, judge horizontal fit from a `-w -r
  672x600` render, not from snapshot PNGs.
- 30 fps (from `custom_config.yml`).

## Look

Workspace defaults, **not** the deck's white theme: black background, CMU Serif, saturation
1.5 — all from `custom_config.yml`, which only loads when you run from the repo root.

- Labels: `txt()`; math: `tex()` with a single string (multi-string `Tex` breaks relation
  spacing). Both come from `common.py` (`from common import *`).
- Minimum readable size: the video plays at ~5.95 in wide on a projected slide, i.e. roughly
  40% of the screen width. Treat `font_size=24` as the floor for anything the audience must
  read, 28–32 for axis labels and readouts, 36–44 for captions.
- Thin lines vanish at this size: curves `stroke_width ≥ 3`, axes 2, reference lines 2 dashed.
- Minimal chrome: no titles inside the video (the slide has one). Captions only where the
  contract asks for them.

## Semantic color roles (keep identical across all videos)

The deck assigns a fixed color to each role; the hue family is kept, the shade is chosen to read
on black. Use the ManimGL constant, not a hex literal, so a later global swap is easy.

| Role | ManimGL color | Deck hue it replaces |
|---|---|---|
| Class 1 / integrator / continuous f–I / control / SNIC | `BLUE_C` (#58C4DD) | blue |
| Class 2 / resonator / discontinuous f–I / shunted / Hopf | `ORANGE` (#FF862F) | orange |
| Resonant membrane (band-pass) | `ORANGE` (same as class 2 on purpose) | orange |
| Passive RC membrane (low-pass) | `GREY_B` (#BBBBBB) | gray |
| Na⁺ / inward / depolarizing | `PINK` (#D147BD) | crimson-magenta |
| K⁺ generic / outward / hyperpolarizing | `TEAL_C` (#5CD0B3) | teal |
| g_K,dr / w (delayed rectifier) | `GOLD_C` (#F0AC5F) | orange (paper Fig. 8C) |
| g_M / z (M-current) | `GREEN_C` (#83C167) | green (paper Fig. 8C) |
| Membrane voltage traces | `WHITE` | near-black |
| Shunting conductance / dynamic clamp | `PURPLE_C` (#9A72AC) | purple |
| V-nullcline | `GREY_A` (#DDDDDD) | dark slate |
| w- (or z-) nullcline | `PURPLE_A` (#CAA3E8) | violet |
| Phase-plane state point / moving marker | `YELLOW` (#FFFF00) | — (new, video only) |
| θ band 3–10 Hz shading | `YELLOW`, fill_opacity 0.2 | gold, α 0.35 |
| γ band 30–80 Hz shading | `BLUE_B` (#9CDCEB), fill_opacity 0.2 | light blue |
| Call-outs, "the answer", flashes | `RED_C` (#FC6255) | red |
| "Works" / good arrows | `GREEN_B` (#A6CF8C) | green |
| Text | `WHITE`; secondary text `GREY_B` | ink / muted |
| Grid / light rules | `GREY_D` (#444444) | light gray |
| Chip / box fill | `GREY_E` (#222222), stroke `GREY_B` | light gray |
| Excitatory / inhibitory synapses | `RED_B` / `BLUE_B` | salmon / blue |

Collisions to know about: `GOLD_C` (g_K,dr) is close to `ORANGE` (class 2), and `PURPLE_C`
(shunt) is close to `PURPLE_A` (w-nullcline). The deck accepts the same near-collisions; never
put the two members of a pair side by side as competing categories.

`Dot` footgun: `Dot(color=X)` renders **white** in 1.7.2. Use `Dot(fill_color=X)`.

## Recurring motifs (numbers shared with the deck's static figures)

Keep these identical wherever a motif appears, so the video's end frame matches the static
figure the audience already saw.

- **f–I pair** (schematic, pA on x, Hz on y):
  - class 1: `f = 5.5·sqrt(I − 100)` for I > 100 pA, else 0 (rheobase 100 pA).
  - class 2: `f = 16 + 4.6·sqrt(I − 140)` for I ≥ 140 pA, else 0 (rheobase 140 pA, f_min 16 Hz).
  - Axes on the deck's static: x 0–250 pA, y 0–75 Hz. Open circle at the bottom of the jump,
    filled circle at f_min; bracket the jump "f_min".
- **Impedance pair** (MΩ vs Hz, 0–20 Hz, y 0–190):
  - passive `|Z| = R/sqrt(1 + (ωτ)²)`, R = 100 MΩ, τ = 20 ms.
  - resonant `Z = R' / (1 + iωτ + g/(1 + iωτ_w))` with τ = 20 ms, g = 1, τ_w = 80 ms, rescaled
    so Z(0) = 100 MΩ; peak ≈ 171 MΩ at **f_res ≈ 5.07 Hz**.
- **MPO trace**: V_m near −55 mV, noisy ~2–4 mV peak-to-peak ripples at ~5 Hz, spike threshold
  dashed at −50 mV. (Generator: white noise through a damped oscillator, Q ≈ 4.)
- **Boltzmann activation**: `1/(1 + exp(−(V − V½)/k))`, V½ = −45 mV, k = 5 mV (schematic);
  threshold marked at −50 mV.
- **Bands**: θ = 3–10 Hz, γ = 30–80 Hz.
- **Phase planes**: x = V (mV), y = w (K⁺ activation, 0–1). V-nullcline is N-shaped; w-nullcline
  is a rising sigmoid. Saddle-node = half-filled dot; stable focus/node = filled dot; saddle =
  open dot; unstable focus = open dot. Stripped down: no tick numbers unless the contract asks.
- **Tug-of-war** (slide 4): rope over a −70 → −40 mV axis, threshold at −50 mV, flag at the
  current V; K⁺ team (teal) pulls left/hyperpolarized, Na⁺ team (pink) pulls right/depolarized.
- **Chips** (loop and chain diagrams): rounded rectangles, `GREY_E` fill, colored stroke, one
  short phrase each, arrows between them.

## ManimGL 1.7.2 footguns (from MANIM_WORKFLOW.md)

- `Dot(color=)` renders white — use `fill_color=`.
- Multi-string `Tex("a", "=", "b")` loses relation spacing — use one string plus `isolate=`/`t2c`.
- Run from the repo root or the black/CMU Serif config silently drops.
- Keep `##` cell comments stable while iterating (Manim Notebook checkpoints).

## Later

When the first two or three of these scenes exist, move the color-role table and the motif
functions into code (an area helper imported next to `common.py`) so the videos share one
definition, and trim this file to a pointer.
