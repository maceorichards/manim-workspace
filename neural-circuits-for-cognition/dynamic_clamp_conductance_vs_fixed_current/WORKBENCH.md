# Workbench — dynamic_clamp_conductance_vs_fixed_current

Context: `context_files/contract.md` (the video contract), `science.md`, `model.md`, `style.md`.

## Dynamic clamp in action

Status: Building (complete render delivered: `videos/dynamic_clamp_conductance_vs_fixed_current.mp4`, 1344×1200, 30 fps, 15.1 s)
Scenes: DynamicClampVsFixedCurrent

### Intent
Same neuron, same input: a fixed current leaves V free to swing and spike, while a dynamic-clamp
current that tracks V (10 nS at −70 mV) squashes it. The voltage dependence is what makes it a
conductance.

### Decisions in force
- 1344 × 1200, black, CMU Serif, silent, 15 s; no equations, no title.
- Model: paper's Morris–Lecar, control state (g_shunt 2), no adaptation; I0 = 90 µA/cm²
  + OU noise (τ 5 ms, SD 12, seed 1); Euler dt 0.01 ms, 100 ms burn-in, 500 ms shown.
- Right: g_dc = 10/3 mS/cm² (= 10 nS at 300 µm²), E = −70 mV (contract §9.1 decision).
- Left: constant offset equal to the clamp's mean (175 pA outward), computed, not hard-coded.
  Result: 9 vs 0 spikes, V SD 6.6 vs 2.3 mV.
- Right column fires 0 spikes: accepted as "fewer spikes" (contract §9.3; matches Fig. 1A).
- "same input" strips kept in both columns (contract §3/§4 require them).
- Matched-mean offset kept; the end label "same average: 175 pA" states it on screen, so the
  speaker need not.
- Currents drawn outward-up in pA (×3), same convention as `s04_vid1`.
- Two columns × (input strip, V, injected current); YELLOW synced cursors; live spike counters;
  PURPLE_C for dynamic-clamp elements only (right title, right current, callout, −70 mV lines/label).
- Layout deviations (fit/legibility):
  - Tick labels need a gutter inside ±4.2, so the left 0.95 units hold ticks; each column's data
    is 3.525 wide (0.00705 units/ms, not 0.0079), columns at x ∈ [−3.25, 0.275] and [0.675, 4.2].
  - Spike counters are right-aligned in the title row, not inside the V panel: the left column's
    spikes reach the panel top along its whole width (e.g. 338 and 449 ms under the top-right corner).
  - "−70 mV" (PURPLE_C) doubles as the −70 tick label, so no duplicate "−70" text.
  - "injected current (outward ↑)" is in the left column only, like the other axis chrome, which
    leaves the right column's between-panels row free for the callout label.
- Colored labels use `txt(..., fill_color=X)` (or `.set_color`): `color=` renders white in 1.7.2.
- Polylines decimated to every 5th sample (10000 points); updaters rebuild them from one tracker.

### Checklist
- [x] Data asserts from `model.md` §4 pass inside `main.py`
  - Outcome: kept — 9/0 spikes at the listed times (±0.1 ms), offset −58.443, right V −57.9…−43.9,
    right current 121–261 pA, corr 0.9999+, callout point −46.7 mV / 233 pA.
- [x] Opening still: titles, labelled empty panels, counters at 0
  - Outcome: kept — first mp4 frame shows both two-line titles, "spikes: 0" ×2, "same input" ×2,
    ticks, −70 mV and 175 pA dashed lines, scale bar; no cursors or traces.
- [x] Sweep: traces draw behind synced cursors; left counter reaches 9, right stays 0
  - Outcome: kept — frames at 5.7/6.6/7.95/11.9 s show cursors at the same sim time; left counter
    3→4→6→9, right 0; left current flat, right purple current mirrors V.
- [x] Callout at t ≈ 209 ms ("V ↑ → outward current ↑") appears and clears
  - Outcome: revised — arrows first overlapped the label and the label rendered white (Text color
    kwarg dropped); slimmed arrows and used set_color. At 6.8 s: two purple arrows + purple label;
    gone at 7.95 s. The cursor passes through the label as it sweeps (transient).
- [x] "same average: 175 pA" label + caption; end hold
  - Outcome: kept — label under the left flat line at 12.3 s, caption written by 13.5 s, held 1.6 s.
- [x] Fit and legibility at 672×600 (two-line titles, 24-pt ticks, dense 500-ms traces)
  - Outcome: kept — everything inside ±4.2 × ±3.75; smallest text is font 24; the dense purple
    trace shows faint lighter streaks from overlapping antialiased segments (cosmetic).

### Open questions
- (resolved by contract decisions above; revisit only if the user disagrees)
  - g_dc 3.33 vs +2 mS/cm² → 3.33.
  - 0 right spikes vs tuning for 1–3 → 0.
  - Keep "same input" strips → kept.
  - Matched-mean offset → kept, stated on screen.

### Parking lot
- Small loop glyph from static s06_v2 next to the right title.
- Brief zoom on one right-column bump to show current and V moving together.
- Give the between-panel labels a black backstroke so the cursor passes behind them.
