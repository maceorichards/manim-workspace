# Video contract — "From sinusoids to spectra" (Beat C, impedance, was cut 2026-10-01)

Sources: deck spec, slide 1 (content, video visuals, Say, If asked) and Video production notes;
deck manifest (video box). Read 2026-09-30. Every number was re-verified on 2026-09-30 (see
`model.md`).

## 1. Header

| | |
|---|---|
| Scene class | `SinusoidsToPowerSpectrum` (`main.py`) |
| Output | `videos/sinusoids_to_power_spectrum.mp4` and `videos/sinusoids_to_power_spectrum_end.png` |
| Format | 1920 × 1080, **60 fps**, **~56 s**, silent |
| Place | The deck's first background slide ("the frequency-domain toolkit"). The video fills the whole 8.89 × 5.0 in video box on its build slide. |

## 2. Purpose

It shows three things, in three beats:
- **A:** A signal is a sum of sinusoids, and each one is stored as a single complex number
  (Re = cosine part, Im = sine part).
- **B:** A power spectrum shows one peak for each rhythm present.
- **C:** A membrane's impedance Z(f) can create a spectral peak from input that has no rhythm.
  This is the logic of the paper's Fig 7D.

## 3. Must / must not

Must:
- Beat A's stems are drawn **analytically from (a, b)**: Re stem = a, Im stem = b, power stem =
  a² + b². **Never read them off an FFT.** The FFT convention gives (N/2)(a − ib) and would flip
  the Im stems.
- Show the footnote "convention: x = a cos + b sin ↔ X = a + ib" throughout Beat A, in small
  `MUTED` text.
- Beat B's spectrum is recomputed every frame from the trailing 2-s window.
- Beat C uses the **complex** Z(f) (`P.impedance_complex`), not just |Z|.

Must not:
- **No rotating phasors, complex-plane dials or circles anywhere.** The rotating point in a
  complex plane is reserved for a later video (`eigenvalues_integrator_vs_resonator`). Re and Im appear only as stem
  plots against frequency.
- No class colours (`CLASS1`/`CLASS2`) on the three components. They use the slide-only
  palette. The single exception is Beat C's "× |Z(f)|²" panel, in `RESONANT`.
- No axis autoscaling; every range below is fixed.

## 4. Colours

- Components: 3 Hz `P.COMP_3HZ` (sky), 6 Hz `P.COMP_6HZ` (lime), 12 Hz `P.COMP_12HZ` (violet).
  A component's stems use its own colour.
- Sums and traces: `P.VOLT`. The θ band is `P.THETA_BAND` at `P.THETA_ALPHA` and the γ band
  `P.GAMMA_BAND` at `P.GAMMA_ALPHA`. Highlights (the "unchanged" outline, peak markers) use
  `P.HIGHLIGHT`. The |Z|² curve is `P.RESONANT`.

## 5. Layout (frame 14.22 × 8 units; ink inside ±6.9 × ±3.85)

A caption band sits at the **bottom**, centred at y ≈ −3.55, font 36–40, one caption at a time.
The boxes below are guides; adjust them after the first snapshot so nothing collides.

**Beat A**
- **Left 60%** (x −6.9 … 1.3): three stacked component rows, 3 Hz on top, then 6 Hz, then
  12 Hz.
  - Each row: x "time (s)" 0–1 (tick labels only on the bottom row), y ±1.1 (a.u.). Height ≈ 1.2
    units.
  - A small colour-coded label at the left of each row: "3 Hz", "6 Hz", "12 Hz".
  - Below them, a taller running-sum row (≈ 2.0 units): y ±2.2, label "sum".
- **Right 40%** (x 1.9 … 6.9): three stacked stem plots sharing x "frequency (Hz)" 0–15:
  - "Re X(f) — cosine part" (y −1.1 … 1.1)
  - "Im X(f) — sine part" (y −1.1 … 1.1)
  - "|X(f)|² — power" (y 0 … 1.1)
  - Stems are vertical lines with a dot at the tip, in the component's colour.
- Footnote: "convention: x = a cos + b sin ↔ X = a + ib", under the stem plots, font ≈ 26,
  `MUTED`.

**Beat B**
- **Top 45%:** a scrolling trace with a 2-s window. x "time (s)" shows the actual signal time (the
  ticks scroll with the data), y "δV (mV)" ±3.
- **Bottom 45%:** the power spectrum. x "frequency (Hz)" 0–60, linear. y "power (mV²/Hz)", log
  10⁻⁴ … 10¹ (ticks at the decades). Values below 10⁻⁴ are clipped to the floor.
- Band shading over the full plot height: θ 3–10 Hz (label `tex(R"\theta")`) and γ 30–60 Hz
  (label "γ →", since the band continues past the axis to 80 Hz). Write γ with `tex`.
- Peak markers: vertical dashed `HIGHLIGHT` lines at 6 Hz and 40 Hz, added at their captions.

**Beat C**
- **Left 45%:** two static 2-s time traces. "input current I(t)" (white noise, `MUTED`) above
  "output voltage V(t)" (`VOLT`). Each is scaled to its own SD, with no y tick numbers.
- **Right 55%:** three stacked spectra on x "frequency (Hz)" 0–20, linear, each normalised to its
  own maximum over 0.5–20 Hz (y 0 … 1.1):
  - "|I(f)|² (input)", in `MUTED`
  - "× |Z(f)|²", in `RESONANT`, with a dashed marker at the |Z|² peak (5.1 Hz) labelled "5.1 Hz"
  - "= |V(f)|² (output)", in `VOLT`

## 6. Beat sheet (video time)

| t (s) | On screen | Caption |
|---|---|---|
| 0–2 | Beat A axes, empty | "Any signal is a sum of sinusoids." |
| 2–5 | The 3-Hz component draws left→right over 1 s. Its Re stem grows to 1.0 and its power stem to 1.0; the sum trace equals it. | (same) |
| 5–8 | The 6-Hz component is added the same way (Re 0.6, power 0.36). The sum updates. | |
| 8–11 | The 12-Hz component is added: a pure sine, so its Im stem is 0.35, it has no Re stem, and its power is 0.1225. | |
| 11–17 | The 6-Hz component slides right by a quarter period (41.7 ms), smoothly: (a, b) = 0.6·(cos φ, sin φ), φ 0 → 90°. Its Re stem shrinks to 0 and its Im stem grows to 0.6; the sum changes shape. Its **power stem stays at 0.36**, outlined in `HIGHLIGHT` with the label "unchanged". | |
| 17–20 | Hold | "Phase lives in the Re/Im split — power ignores it." |
| 20–21 | 1-s crossfade to Beat B | |
| 21–~27 | Noise-only trace scrolls; the spectrum is smooth | from ~23 s: "Noise only: a smooth spectrum." |
| ~29 | The 6-Hz peak is fully up. Marker at 6 Hz. | "+ 6 Hz (θ): a peak rises at 6 Hz." |
| ~35 | The 40-Hz peak is fully up. Marker at 40 Hz. | "+ 40 Hz (γ): a second peak — each rhythm gets its own peak." |
| to 42 | Hold (still scrolling) | |
| 42–45 | Beat C: input trace and its flat spectrum | "Noise: every frequency, equal power." |
| 45–49 | The |Z|² panel draws in, with its 5.1-Hz marker | "The membrane's impedance Z(f)." |
| 49–53 | A vertical "multiply" cursor sweeps left→right across the frequency axis (all three panels), revealing the output spectrum behind it. Then the output trace appears, with a visible ~5-Hz wobble. | "V(f) = Z(f)·I(f): no rhythm in, rhythm out." |
| 53–56 | Add the subcaption (smaller, under the caption) | "This is the logic of the paper's Fig 7D." Hold. |

In the captions, write θ and γ with `tex`, or build each caption as a `tex(R"\text{…}")` single
string.

Beat B clock: signal time T = (video time − 20 s) + 2 s. At the start of the beat, the window
already shows signal 0–2 s. Beat B ends at signal time 24 s. Each peak lags its onset by up to
the 2-s window, so time every caption **after** its peak has visibly risen. The times above
already allow for this: the 6-Hz peak is fully in the window at video ≈ 27 s, and the 40-Hz peak
at ≈ 33 s.

## 7. End frame

Beat C complete: both traces, all three spectra, the 5.1-Hz marker, the caption and the
subcaption. Export as `videos/sinusoids_to_power_spectrum_end.png`. Hold ≥ 3 s (53–56 s).

## 8. Acceptance checks (print from `__main__`, then assert)

- Beat A: the 6-Hz power stem stays at 0.36 ± 1% at every φ in the slide.
- Beat A: the 12-Hz Re stem is exactly 0. The sum trace equals the sum of the three components.
- Beat B: once present (window fully past onset), the 6-Hz and 40-Hz peaks are each ≥ 10× the
  local background. The background is the median PSD over bins 4–12 Hz away from the peak.
  Verified: 50–200×.
- Beat C: the smoothed output spectrum (seed 0) has its argmax at 5 Hz (1-Hz bins), and that
  argmax lies inside |Z|²'s ≥ 90% band, 3.6–6.9 Hz. The |Z|² peak is 5.07 ± 0.05 Hz.
- Beat C: the input spectrum is visibly flat, with min/max ≥ 0.7 over 0.5–20 Hz. Verified
  0.73–0.85.
- The Welch of V matches |Z|² × Welch of I within 5% RMS over 0.5–20 Hz (both normalised).

This deliberately deviates from the deck spec, and the user approved it on 2026-09-30. The spec
asked for "output peak between 4.5 and 5.5 Hz" using a 30-s record with nperseg 4000. That
estimate is too noisy for |Z|²'s flat top: the argmax falls in the window for only 8 of 20 seeds,
and the input spectrum looks jagged rather than flat. Hence the 300-s record and nperseg 1000 in
`model.md`.
