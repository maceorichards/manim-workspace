# Workbench — m_current_theta_ringing

Context: `context_files/contract.md` (the build contract), `model.md`, `science.md` and
`style.md`. Sources: see `SOURCES.local.md` (deck spec, slide 6).

## Two clocks, and sliding the threshold

Status: Building (rendered; awaiting review)
Scenes: MCurrentThetaRinging

### Intent

In ~50 s (1920×1080, 60 fps): (A) fast ringing spirals on the V–w plane (g_K,dr lags) while θ
ringing spirals on the V–z plane (g_M lags); (B) raising threshold by Na⁺ inactivation or
shunting slides V* up I_M's activation curve, recruits I_M and creates a θ peak, while deleting
I_M kills it.

### Decisions in force

- Workspace look; colours from `prescott2008.py`. "I_M removed" is `MUTED` grey, never green.
  Shunt colour is `PURPLE_C` taken locally (see Open questions: `P.SHUNT` is shadowed).
- Beat A windows: centred per segment on the run mean, shared spans (computed: V 2.13 mV,
  w 0.00179, z 0.00352). Fixed within a segment; the A1 → A2 change is fade-out 0.45 s then
  fade-in 0.55 s (a simultaneous crossfade overlaid both tick sets).
- Beat A noise: A1 τ 5 ms / σ 0.1; A2 τ 500 ms / σ 0.004; both at 0.99× I_bif, seed 0.
  Displayed stretches are the first 75 ms / 2 s after burn-in (both fit inside the windows).
- Normalised conductance traces (own min–max over the displayed stretch) plus real-amplitude
  tags: A1 g_K,dr 14%, g_M 0.11%; A2 g_K,dr 43%, g_M 1.8%.
- After each run a faint full path (opacity 0.35) stays on both planes so the hold frames show
  the spiral; the moving tail covers the last 20% of the window.
- Emphasis on the spiral plane (A1 V–w at ~4–5.5 s, A3 V–z at ~21.5–23 s) brightens that faint
  path and lets it settle back. A yellow FlashAround on the padded plot box was dropped: its
  sweep ran along the box edge through "V (mV)" and read as a stray, clamped trajectory. Both
  displayed stretches lie strictly inside their windows (asserted in `__main__`), so nothing is
  clipped or clamped.
- Beat B: 0.995× I_bif, σ 0.001, τ 500 ms, seed 0; spectra precomputed; one tracker
  interpolates V*, the meter, the V-nullcline, log power and colour between conditions. The
  V–z fixed-point dot follows the nearest in-window intersection of the interpolated curves
  and fades out through the middle of each transition. The interpolated family loses the
  control node/saddle pair early on, so a tracking dot would otherwise jump or leave the plane.
- Beat B order: control → inact → (control) → shunt → (inact) → delete I_M. The brief return
  to inactivation before deleting I_M makes step 4 a single-variable change.
- No-I_M state: z∞ curve and V* dot fade to a grey ghost; ΔV* bracket stays (threshold is still
  raised, +5.6 mV); V–z plane veiled with "no I_M"; meter 0.
- End frame: four spectra overlaid; 2×2 legend in the empty low-f/low-power corner of the
  spectrum. Footnote "spectra precomputed per condition" sits under the I_M meter (inside the
  spectrum it collided with the high-frequency tails).
- Output: `--file_name m_current_theta_ringing`; end frame `videos/m_current_theta_ringing_end.png`.
- `--fps 60` reaches the scene as a string in manimgl 1.7.2; `setup()` coerces it to int.

### Checklist

- [x] Precompute and cache all runs + spectra; asserts from `model.md` pass and print
  - Outcome: kept — all six I_bif, all eigenvalues (<1%), A2 peak 9.50 Hz, lags g_K,dr 4.8° /
    g_M 88.0°, A p-p 1.51 / 1.58 mV, B ratios 1.5 / 140.5 / 88.8 / 1.4, no spikes anywhere,
    I_M at V* 0.10 / 2.11 / 4.15 / 0.00. Cache ~10 s cold.
- [x] Beat A layout: two stacked planes + V(t) + normalised conductances + tags + chip + badge
  - Outcome: revised — "t (ms)" collided with the last tick label ("75", "2000"); right column
    narrowed to x 1.0–5.5 and the label moved out.
- [x] A1 (0–9 s): the spiral on V–w, a flat line on V–z, g_K,dr lags, g_M flat; caption
  - Outcome: kept — spiral fills V–w; V–z shows flat horizontal loops (z spans ~0.0006 of a
    0.0035 window); normalised g_M is a slow drift with a small ripple (tag says 0.11%).
- [x] A2 (9–21 s): a line on V–w, the spiral on V–z, g_M lags ~90°; caption; 21–24 s caption + crossfade
  - Outcome: kept — V–w dot slides along the overlapping nullclines; V–z spiral clear; caption
    fades in at 13 s during the run.
- [x] Beat B layout: z∞ panel + V* dot + ΔV* bracket + I_M meter; V–z plane; spectrum with θ band
  - Outcome: revised — "focus" label sat on the V-nullcline (moved below-right of the fixed
    point); peak readout overlapped the θ label (moved right of the band at peak height).
- [x] Beat B conditions 1–4 with captions; the no-I_M greying; end-frame spectra overlay + legend
  - Outcome: revised — first legend (top-right, 1 column) sat on the shunt / no-I_M curves;
    moved to a 2×2 grid in the lower-left strip. Mid-transition fixed-point dot drifted off the
    curves; now tracks the intersection.
- [x] Timing pass `-l --fps 60`; final `--hd --fps 60` + end PNG; acceptance checks printed
  - Outcome: revised — first pass was 51.0 s (B1 hold 1 s too long); fixed to 50.0 s.

### Open questions

- `prescott2008.py`: palette `SHUNT = PURPLE_C` is overwritten by the parameter set
  `SHUNT = MLParams(g_shunt=4.0)` later in the module, so `P.SHUNT` is not a colour. Worked
  around locally (`SHUNT_COLOR = PURPLE_C`); the module owner should rename one of them.
- Beat B V p-p differs from model.md's table (inact 0.57 vs 0.87, shunt 0.28 vs 0.43; 99%
  central range here). Not an acceptance check; the definition in model.md may be max−min.
- Control's V–z fixed point at 0.995× sits at V −44.3 (node) with a saddle at −41.2; the
  z∞ panel's V* dot is the threshold V* = −43.1, not the fixed point. Both are as specified.

### Parking lot

- Short 0.5-s ring-down "kick" on each plane to show the spiral without noise.
