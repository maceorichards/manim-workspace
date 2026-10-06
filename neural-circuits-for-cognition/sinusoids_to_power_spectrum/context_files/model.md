# Model and data — "From sinusoids to spectra to impedance"

Sources: deck spec, slide 1 video visuals; deck model module (impedance motif). Read
2026-09-30. Recomputed on 2026-09-30 with `prescott2008.py` + numpy/scipy.

All signal generation is plain numpy. The only thing used from the area module is
`P.impedance_complex` (and `P.impedance_peak_hz`), plus the palette and `P.npz_cache`.

## Beat A — three components

`x_k(t) = a_k cos(2π f_k t) + b_k sin(2π f_k t)`, t ∈ [0, 1] s.

| f (Hz) | (a, b) | Re stem | Im stem | power stem |
|---|---|---|---|---|
| 3 | (1.0, 0) | 1.0 | 0 | 1.0 |
| 6 | (0.6, 0) → slide | 0.6 cos φ | 0.6 sin φ | 0.36 (always) |
| 12 | (0, 0.35) | 0 | 0.35 | 0.1225 |

Phase slide: φ = 0 → π/2 over 11–17 s (smooth). This equals shifting the 6-Hz component right
(later) by Δ = φ / (2π·6) s, which is 41.7 ms at φ = 90°:
0.6 cos(2π6(t − Δ)) = 0.6 cos φ · cos(2π6t) + 0.6 sin φ · sin(2π6t).
Drive it from one ValueTracker φ, and draw the trace, the stems and the sum from it.
"Draws left→right over 1 s" means the curve is revealed from t = 0 to t = 1 of its own axis.

## Beat B — live spectrum

- fs = 1000 Hz. The signal lasts 24 s. `rng = np.random.default_rng(0)`; draw the OU innovations as `rng.standard_normal(24_000)`.
- OU baseline: τ = 10 ms, SD 0.4 mV. Discrete AR(1): `a = exp(−1/(fs·τ))`,
  `x[i] = a·x[i−1] + sqrt(1−a²)·ξ[i]`, then rescale so SD = 0.4 exactly.
- Ramps: `r6 = clip(T − 6, 0, 1)` and `r40 = clip(T − 12, 0, 1)`.
- `s = x + 1.0·r6·sin(2π·6·T) + 0.6·r40·sin(2π·40·T)`, in mV.
- Frame at video time t: signal time T = t − 18 (t ∈ [20, 42] → T ∈ [2, 24]). Window = samples
  in [T − 2, T]. Spectrum:
  `scipy.signal.welch(window, fs=1000, nperseg=1000, noverlap=500)` → 1-Hz bins. Plot bins
  0.5–60 Hz, with values clipped to [1e−4, 1e1].
- Verified with this recipe (seed 0): Ratios are peak / local
  background:

| T (s) | 6-Hz ratio | 40-Hz ratio | PSD min … max (0–60 Hz) |
|---|---|---|---|
| 5 | 1.8 | 1.6 | 1.9e−4 … 9.3e−3 |
| 9 | 50 | 1.4 | 3.2e−5 … 0.31 |
| 15 | 189 | 168 | 1.1e−4 … 0.29 |
| 24 | 201 | 173 | 1.3e−4 … 0.35 |

  Some noise bins fall below 10⁻⁴ and get clipped to the floor, which is fine.
- Caching is optional (the whole signal is 24 k samples). Welch on 2000 samples per frame is
  cheap enough for 60 fps.

## Beat C — convolution made visible

- Input: white Gaussian noise, `np.random.default_rng(0).standard_normal(300_000)` (300 s at
  1 kHz).
- `F = np.fft.rfftfreq(N, 1/fs)`; `V = np.fft.irfft(P.impedance_complex(F) * np.fft.rfft(I), n=N)`.
- `impedance_complex(f)` computes `Z = R / (1 + iωτ + g/(1 + iωτ_w))`, with ω = 2πf, R = 100 MΩ,
  τ = 20 ms, g = 1 and τ_w = 80 ms. It is not rescaled (|Z(0)| = 50 MΩ), but the panels are
  normalised anyway.
- **Displayed spectra:** `welch(I, fs, nperseg=1000)` and `welch(V, fs, nperseg=1000)`, 1-Hz
  bins, plotted over 0.5–20 Hz and each normalised to its own maximum there. |Z(f)|² is the exact
  curve, on a fine grid of 0–20 Hz, normalised.
- **Displayed traces:** a 2-s excerpt, samples 10 000–12 000 (t = 10–12 s of the record), each
  scaled by its own SD. At 1 kHz that is 2000 points; decimate to ≤ 1000 if drawing is slow.
- The "multiply" cursor at frequency f_c reveals the output spectrum curve for f ≤ f_c. Clip the
  displayed curve, or draw its partial points up to f_c.
- The |Z|² peak marker goes at `P.impedance_peak_hz()` = **5.07 Hz** (label "5.1 Hz").

Verified numbers:

| Quantity | Value |
|---|---|
| |Z|² peak | 5.07 Hz; peak / DC = 2.9 |
| |Z|² ≥ 90% of max | 3.59–6.93 Hz (flat top) |
| Output Welch argmax (seed 0, 300 s, nperseg 1000) | 5 Hz. Across seeds 0–19 it is 5 or 6 Hz (7 once): always inside the 90% band. |
| Input min/max over 0.5–20 Hz | 0.73–0.85 across seeds (visibly flat) |

Why these settings: with the spec's original 30 s and nperseg 4000, the input spectrum varies
0.2–1.0 bin to bin (it does not look flat), and the output argmax scatters over 3–9.75 Hz.
Averaging over a 300-s record fixes both. The time traces are unaffected. A sharper Z was
compared and rejected: the output traces looked almost identical (see WORKBENCH decisions).

## Asserts for `main.py __main__`

- For φ in linspace(0, π/2, 91): |(0.6 cos φ)² + (0.6 sin φ)² − 0.36| < 0.0036.
- The Beat B ratios at T = 24: both ≥ 10.
- The Beat C argmax is 5 Hz for seed 0; `3.59 <= argmax <= 6.93`; |impedance_peak_hz() − 5.07| < 0.05.
- Input flatness min/max ≥ 0.7.
- RMS(norm Welch V − norm(|Z|²·Welch I)) < 0.05 over 0.5–20 Hz.

Print every value before asserting it.
