# Video contract — "Two clocks, and sliding the threshold"

Sources: deck spec, slide 6 (takeaway, content, static visuals, video visuals, Say, If asked),
Code prerequisites, Video production notes; paper, Fig 8 and Fig 9 legends and Methods (noise).
Read 2026-09-30. Every number was re-verified on 2026-09-30 (`model.md`). Deviations from the
deck spec are marked **Deviation**, with the reason.

## 1. Header

| | |
|---|---|
| Scene class | `MCurrentThetaRinging` (`main.py`) |
| Output | `videos/m_current_theta_ringing.mp4` and `videos/m_current_theta_ringing_end.png` |
| Format | 1920 × 1080, **60 fps**, **~50 s**, silent |
| Place | The deck's mechanism slide ("the authors overturn their own hypothesis: I_M, not I_K,dr"), after the paper's Fig 2B/9A, 8C, 8D and Fig 9 spectra panels. The video fills the whole video box. |

## 2. Purpose

It reuses `eigenvalues_integrator_vs_resonator`'s visual grammar (nullclines, focus = ring) to show two things:
- **(A)** θ ringing lives on the **V–z** plane, because g_M, not g_K,dr, supplies the *delayed*
  outward current.
- **(B)** The V* shifters (slow Na⁺ inactivation, shunting) recruit I_M, and deleting I_M kills
  the θ peak.

## 3. Must / must not

Must:
- Colours: V `P.VOLT`; g_K,dr `P.IKDR` (gold, like the paper's Fig 8C orange); g_M and I_M `P.IM`
  (green, as in Fig 8C); nullclines `P.V_NULL` / `P.W_NULL`; θ band `P.THETA_BAND`.
  - Beat B conditions: control `P.CLASS1`, 33% Na⁺ inactivation `P.CLASS2`, shunt `P.SHUNT_COLOR`,
    I_M removed `P.MUTED` grey.
- **Never use green for "I_M removed"**, even though the paper's Fig 9 does. Green means I_M
  everywhere else in this deck.
- Every slowed segment is badged ("×1/40", "×1/4").
- Beat B's spectra are **precomputed per condition, not live**. Transitions between conditions
  interpolate the log spectra over 1 s, for display only. Footnote: "spectra precomputed per
  condition".
- The λ chips show the **3-D** eigenvalues at the fixed point (`P.stable_fp_3d`), in s⁻¹, with
  the ring in Hz.

Must not:
- No live Welch; no autoscaling within a beat; no spikes in any displayed trace. The noise
  settings in `model.md` are chosen to avoid them.

## 4. Beat A — two clocks (video 0–24 s)

**Layout**
- **Left column:** two stacked phase planes, sharing the V axis mapping.
  - Top: "V–w plane (fast recovery, I_K,dr)". Bottom: "V–z plane (slow recovery, I_M)".
  - Both have x "V (mV)".
  - V–w nullclines: `P.V_nullcline_w(V, p, I, z=z_fp)` (z frozen at its fixed-point value) and
    `P.w_nullcline(V, p)`.
  - V–z nullclines: `P.z_Vnull(V, p, I)` (w slaved to w∞) and `P.z_nullcline(V, p)` (= z∞).
  - The trajectory is drawn on **both** planes at once (dot + fading tail covering the last ~20%
    of the displayed window).
- **Right column:** "V(t)" on top. Below it, g_K,dr(t) = ḡ_K,dr·w and g_M(t) = ḡ_M·z overlaid,
  **each normalised to its own min–max over the displayed window**, as in Fig 8C, with the label
  "normalized".
  - Next to each conductance trace, a small `MUTED` amplitude tag giving its real modulation over
    the window, e.g. "g_M varies 0.1%". This keeps the normalisation honest: A1's g_M really is
    nearly constant.
- **λ chip** (3-D, s⁻¹, ring Hz) at the top of the left column. Speed badge top-right. Caption
  band at the bottom.

**Windows — Deviation.** The spec says to fix all windows once, at ±3 SD of the noisy trajectory.
One window shared by A1 and A2 cannot work: the fixed points differ by ~10 mV and by z 0.52 vs
0.13, so the V–z plane would squash both oscillations to specks. Instead:
- each segment's windows are **centred on its own fixed point**
- the **spans are shared** by both segments: per axis, the larger of the two segments' ±3 SD
  ranges, plus 20%
- the windows are fixed within each segment and change only during the A1 → A2 crossfade, with
  the tick labels updated

Result: A1's spiral fills the V–w plane while its V–z dot slides along an almost flat line. A2's
V–w dot slides along the w-nullcline (w follows V instantly) while it spirals on V–z. Approximate
spans (recompute from your cached runs): **V 2.2 mV, w 0.0018, z 0.0036** (`model.md` §3).

**Segment A1 — fast ring (0–9 s)**
- Model `replace(P.THETA_MODEL, g_shunt=4.0)` (I_M still present, ḡ_M 2, τ_z 400).
  I_bif = 183.06; hold at 0.99 × I_bif = 181.23.
- 3-D λ = **−22.0 ± 721.2i s⁻¹** (115 Hz; the paper reports ~70 Hz for its shunted case), plus a
  slow real −10.7.
- **Noise — Deviation:** τ_noise = **5 ms**, σ = **0.1**. These are the paper's equal-variance
  fast-noise settings. With the spec's τ 500 ms / σ 0.01, the 115-Hz mode is barely driven
  (0.2 mV p-p).
  - Result: ≈ 1.5 mV p-p, no spikes, spectral peak at 115 Hz.
- Show 75 ms of model time at **×1/40** (3 s of video; 115 Hz appears at 2.9 Hz, 21 frames per
  cycle).
- Expected: the spiral is on V–w. On V–z the dot barely moves vertically. g_M's normalised trace
  is a slow drift that does not follow the ring (it varies 0.11%). g_K,dr visibly lags V (≈ 56°)
  and varies 14%.
- Caption: "Fast ring: g_K,dr lags V, g_M barely moves → the spiral lives on the V–w plane."

**Segment A2 — θ ring (9–21 s)**
- Model `P.THETA_MODEL` (γ_w 8, ḡ_K,dr 30, ḡ_M 2, τ_z 400, g_shunt 2). I_bif = 53.39
  (V* −39.2 mV); hold at 0.99 × I_bif = 52.86.
- 3-D λ = **−6.9 ± 63.2i s⁻¹** (10.1 Hz). For reference, at 0.97× it is −21 ± 58i (9.2 Hz).
- **Noise — Deviation:** τ_noise 500 ms (as in the spec) but σ = **0.004**. With σ = 0.01 the
  model spikes 30 times in 10 s.
  - Result: ≈ 1.6 mV p-p, no spikes, spectral peak at 9.5 Hz.
- Show 2 s of model time at **×1/4** (8 s of video; 10 Hz appears at 2.5 Hz, 24 frames per
  cycle).
- Expected: the dot jitters along a line on V–w (no spiral) and **spirals slowly on V–z**.
  g_K,dr tracks V with no visible lag (≈ 5°, varies 43%). g_M lags V by roughly a quarter cycle
  (≈ 88°, varies 1.8%).
- Caption: "θ ring: g_K,dr keeps up with V, g_M lags → the spiral moved to the V–z plane."

**21–24 s:** caption "Same spiral as slide 3 — on a slower variable." Crossfade to Beat B.

Write θ with `tex` in every caption.

## 5. Beat B — slide the threshold (video 24–50 s)

**Model:** `P.FIG9` (ḡ_Na 24, ḡ_K,dr 30, γ_w 8, ḡ_M 2, β_z −29, γ_z 2, τ_z 400, φ_w 0.25,
g_shunt 2). Variants:
- control `P.FIG9`
- 33% Na⁺ inactivation `P.FIG9_INACT` (ḡ_Na 16.08)
- shunt `P.FIG9_SHUNT` (**g_shunt 3.5**, not 4.0: at 4.0 the model's focus is the fast ~36-Hz
  I_K,dr-type mode)
- I_M removed `P.FIG9_INACT_NO_IM` (33% inactivation with ḡ_M 0)

**Holding level and noise — Deviation.** Hold every variant at **0.995 × its own I_bif**, with
σ = **0.001** and τ_noise 500 ms. At the spec's 0.99× and σ 0.01, the inactivation and shunt
variants spike 30–40 times. At 0.99× with σ 0.002 nothing spikes, but the shunt peak is weak and
lands at 4.25 Hz. At 0.995× both θ peaks are clear. The spec allowed lowering σ or changing the
holding level, provided the values used are recorded. Same seed (0) for all four.

**Values used on screen** (verified):

| Variant | I_bif | V* at I_bif | z∞(V*) | I_M at V* (µA/cm²) | 3-D λ at 0.995× (s⁻¹) | fixed point on V–z | θ peak (precomputed) |
|---|---|---|---|---|---|---|---|
| control | 33.19 | −43.1 | 0.09% | 0.10 | all real (−1113, −104, −2.8) | "saddle-node" (no ring) | none |
| 33% inactivation | 44.12 | −37.1 | 1.68% | **2.11** | −7.8 ± 39.3i (6.3 Hz) | "focus" | 5.75 Hz (×140 bg) |
| shunt 3.5 | 83.08 | −35.8 | 3.23% | 4.15 | −18.4 ± 60.3i (9.6 Hz) | "focus" | 9.5 Hz (×89 bg) |
| inactivation, no I_M | 42.02 | −37.4 | — | 0 | all real | (plane greyed: "no I_M") | none |

- I_M at V* = ḡ_M z∞(V*)(V* − E_K).
- **Spec correction:** the spec lists 2.3 for inactivation; the correct value is 2.11.
- The shunt's θ peak sits at 9.5 Hz, not the spec's 7.4 Hz, because it is held closer to
  threshold. That is still inside θ (3–10 Hz).

**Layout**
- **Left 40%:** "I_M activation z∞(V)" for FIG9 (β_z −29, γ_z 2) over x "V (mV)" −50 … −30 and
  y "z∞ (%)" 0 … 10.
  - A V* dot sits on the curve, with a ΔV* bracket from the control position (inactivation
    +5.9 mV, shunt +7.3 mV).
  - Underneath, a horizontal bar meter "I_M at threshold (µA/cm²)", 0 … 5, in `IM` green.
- **Right top:** the V–z plane, with nullclines at 0.995 × I_bif for the current variant and the
  fixed point labelled "saddle-node" or "focus". Fit the window once across the three I_M
  variants (e.g. V −46 … −33, z 0 … 0.04; recompute).
- **Right bottom:** the power spectrum. x "frequency (Hz)" log 1–100; y "power (mV²/Hz)" log,
  fixed after precomputing all four (≈ 10⁻⁹ … 10⁻²). The θ band is shaded.
- Condition label (coloured) at the top. Caption band at the bottom. Footnote "spectra
  precomputed per condition" (small, `MUTED`).

**Timeline** (~6 s per condition)
1. **24–30 s, control.** The V* dot sits low on the curve (−43.1 mV). The meter shows ≈ 0.1. The
   V–z plane shows a saddle-node, and the spectrum has no θ peak.
   Caption: "Control: threshold sits low on I_M's curve → I_M ≈ off → no ring."
2. **30–36 s, 33% Na⁺ inactivation.** The dot slides up the flank to −37.1 mV, and the meter
   rises to ≈ 2.1. The V–z intersection becomes a focus, and a θ peak grows at ≈ 5.75 Hz.
   Caption: "Slow Na⁺ inactivation raises threshold → I_M recruited → θ ring."
3. **36–42 s, shunt instead** (reset to control, then g_shunt 2 → 3.5). The dot goes to
   −35.8 mV and the meter to ≈ 4.1. The plane shows a focus, and a peak appears at ≈ 9.5 Hz.
   Caption: "Shunting does the same."
4. **42–48 s, inactivation with I_M deleted.** The z∞ curve fades out and the meter drops to 0.
   The V–z plane greys out with the label "no I_M", and the θ peak collapses.
   Caption: "Delete I_M → no θ ring: the effect runs through I_M."
5. **48–50 s:** hold, fading in the end-frame overlay.

## 6. End frame

The four spectra overlaid in their condition colours (control `CLASS1`, inactivation `CLASS2`,
shunt `SHUNT_COLOR`, no I_M `MUTED`), with a legend and the θ band. Export
`videos/m_current_theta_ringing_end.png`. Hold ≥ 2 s.

## 7. Acceptance checks (print, then assert, in `__main__`)

- Beat A:
  - the A2 spectral peak is at 8–11 Hz (verified 9.5)
  - g_M's phase lag behind V is ≥ 60° (88°) and g_K,dr's is < 15° (5°), with lag measured as in
    `model.md` §4
  - A1 and A2 show no spikes, and each has 1–2 mV p-p (99% range)
- Beat B:
  - the precomputed spectra show a θ peak ≥ 5× background for inactivation and for shunt, and
    none (< 3×) for control or no-I_M
  - no variant spikes
- The eigenvalues match the tables here within 3%.
- The recorded noise values (σ, τ, holding fraction, seed) are printed.
