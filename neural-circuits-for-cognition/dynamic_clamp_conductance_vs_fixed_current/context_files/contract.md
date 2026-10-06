# Video contract — "Dynamic clamp in action"

## 1. Header

| | |
|---|---|
| Deck id | `s06_vid1` |
| Title | Dynamic clamp in action |
| Scene class | `DynamicClampVsFixedCurrent` |
| Slide | Outline slide 6 ("What the slice is missing, and how to put it back"), build **6d, left box** (only placeholder on that build) |
| Duration target | ~15 s (hard cap 25 s) |
| Delivery | Silent, click-to-play, 1344 × 1200 (see `style.md`) |

Sources: deck outline slide 6 (content, static visuals 1–3, video visual 1) and slide 4
(sign of a −70 mV conductance); deck manifest; deck static figure s06_v2 (dynamic-clamp loop)
+ status note, s06_v1 status note; deck model module; paper Methods (dynamic clamp, model,
noise, unit conversion) and Fig. 1A; background notes §13, §14, §41, §45. Read 2026-09-29.

## 2. Purpose

**Takeaway:** a dynamic clamp injects a current that depends on voltage, I = g(V − E). That
voltage dependence is what makes it act like a real conductance: it pulls harder the further V
rises above −70 mV, so the same input produces smaller voltage excursions and fewer spikes.
A fixed current of the same average size does not do this.

Where it sits: slide 6 explains the in vivo barrage (R_in ↓ ~80 %, +~20 mV, ~10× noise) and
that the shunt reverses near −70 mV, i.e. below threshold, so it is **outward** at
perithreshold voltages. Build 6b showed the dynamic-clamp loop (static s06_v2) and paper Fig. 1A
(a CA1 cell stops repetitive firing in the high-conductance state). This video makes the loop's
"I depends on V" visible. It sets up the prediction (outward current ↑ → class 1 → class 2) and
the 10-nS experiments on slides 8 and 10.

## 3. Must show / Must not show

Must show
- Two columns, the same model neuron, the same fluctuating input (identical input trace in both).
- Left column titled "current clamp, constant offset": injected-current trace is a flat line.
- Right column titled "dynamic clamp, 10 nS at −70 mV": injected-current trace mirrors V (more
  outward current the further V is above −70 mV); V trace visibly squashed (smaller excursions,
  fewer spikes).
- A cursor sweeping both columns in sync; live spike counters.
- End caption: **"the injected current depends on voltage — that is what makes it a
  conductance."**

Must not show
- No equations on screen (the loop figure s06_v2 already showed I = g(V − E)); say it in words.
- No title. No synapse cartoons (that is static s06_v1).
- Do not let the two columns differ in anything except the injected current (same drive, same
  noise seed, same model, same axes).

## 4. Layout (frame 8.96 × 8)

Two columns: left x ∈ [−4.2, −0.25], right x ∈ [0.25, 4.2] (3.95 wide each). Same y layout:

| Row | y range | Content |
|---|---|---|
| Column title | ≈ 3.2–3.75 | Two lines, font 28. Left (WHITE): "current clamp," / "constant offset". Right (PURPLE_C): "dynamic clamp," / "10 nS at −70 mV" |
| Input strip | 2.35–2.85 | GREY_B trace, stroke 2, y range 150 → 400 pA. Label "same input" (GREY_B, font 24) above the left end of each strip |
| V panel | −0.3–2.1 | WHITE trace, stroke 2.5; y range −80 → +30 mV; PURPLE_C dashed line at −70 mV (label "−70 mV", PURPLE_C, font 24, left column only). Tick labels "−70", "0" on the left column's left edge only (font 24). Spike counter top-right inside the panel: "spikes: N" (font 28, WHITE) |
| Current panel | −2.55 to −0.75 | Label above (font 24, GREY_B): "injected current (outward ↑)". y range 100 → 275 pA, outward plotted **up**. Left: flat line at 175 pA (GREY_A, stroke 3). Right: PURPLE_C trace, stroke 2.5. Faint GREY_D dashed line at 175 pA in both panels. Ticks "100", "200" (font 24) on the left column only |
| Scale bar | ≈ −2.85 | "100 ms" bar under the left current panel (font 24) |
| Caption | ≈ −3.3 to −3.75 | Two lines, font 32, WHITE: "the injected current depends on voltage —" / "that is what makes it a conductance" |

- Time axis 0–500 ms across each column (0.0079 units/ms). No time ticks except the scale bar.
- Cursor: YELLOW vertical line (stroke 2) from the input strip to the bottom of the current
  panel, one per column, at the same sim time.
- Sign convention: currents plotted as the clamp's contribution to **membrane** current,
  outward positive and up — the same convention as `s04_vid1` (K⁺ up) and the paper's I–V
  curves. Numerically this is −I_inj (the rig injects negative, hyperpolarizing current).
- Persisting: everything; traces accumulate behind the cursors.

## 5. Beat sheet (15.0 s)

Sim time 0–500 ms (after a 100-ms burn-in; `model.md`). Sweep speed 47.6 ms/s.

| t (s) | On screen / motion | Data |
|---|---|---|
| 0.0–1.5 | Opening still: both titles, empty panels, labels, −70 mV lines, 175-pA dashed lines, "spikes: 0" ×2. | |
| 1.5–12.0 | Cursors sweep 0 → 500 ms together; input, V and current traces draw behind them. Left V fluctuates widely and spikes (counter ticks at 26, 115, 162, 210, 270, 297, 329, 338, 449 ms → 9). Right V stays in a narrow band (−58 to −44 mV), no spikes; right current wobbles 121–261 pA in lock-step with V. Left current stays flat at 175 pA. | seed 1 run |
| 5.9–7.9 | Callout while the cursor passes t ≈ 209 ms: on the right column, a small PURPLE_C up-arrow at the V bump (−46.7 mV) and one at the current peak (233 pA), with the label "V ↑ → outward current ↑" (font 24, PURPLE_C) between the two panels; fades out by 7.9 s. (At the same moment the left column fires its 4th spike.) | t = 209.2 ms |
| 12.0–12.5 | Cursors fade; 175-pA dashed lines brighten with a label in the left current panel: "same average: 175 pA" (font 24, GREY_B). | mean clamp current |
| 12.5–13.5 | Caption writes in. | |
| 13.5–15.0 | Hold end frame. | |

## 6. End frame

Two columns over 500 ms. Top strips: identical grey noisy input traces. Left V: noisy trace
around −54 mV with 9 full spikes to ≈ +27 mV and troughs to ≈ −76 mV; "spikes: 9". Right V:
a much narrower wiggle around −52 mV (SD 2.3 vs 6.6 mV, range −58 to −44), no spikes;
"spikes: 0". Left current: flat grey line at 175 pA. Right current: purple trace that is an
exact scaled copy of the right V trace (correlation 0.99997), wobbling around 175 pA between
121 and 261 pA. Dashed 175-pA line labelled "same average: 175 pA". Caption at the bottom. No
deck static corresponds; the end frame complements static s06_v2 (its inset "ordinary current
clamp: I is fixed and ignores V" = the left column).

## 7. Data

`model.md`: paper's modified Morris–Lecar (control, low-conductance state g_shunt = 2 mS/cm²,
no adaptation), drive I0 = 90 µA/cm² plus OU noise (τ 5 ms, SD 12 µA/cm², seed 1), Euler
dt 0.01 ms. Right: clamp g = 10/3 mS/cm² (= 10 nS) at −70 mV. Left: constant current equal to
the right clamp's mean (−58.44 µA/cm² = 175 pA outward). Display: currents × 3 → pA.

## 8. Continuity

- Same model family as slides 5, 7–11 (`class1_snic_onset_slow_crawl`, `class2_hopf_onset_spiral_escape`,
  `iv_curve_hump_flattens_snic_to_hopf`, `s08_vid1_mechanism_sync`): same equations and control parameters.
- Sign convention (outward up) = `s04_vid1_the_race`.
- The "−70 mV conductance is outward above −70 mV" point = slide 4 static s04_v2.
- PURPLE_C = shunt / dynamic-clamp role everywhere (`style.md`).

## 9. Accuracy flags

1. **10 nS in model units.** Paper conversion: 300 µm² = 3×10⁻⁶ cm², so µA/cm² × 3 = pA and
   10 nS = 3.33 mS/cm². The paper's own high-conductance state adds only **+2 mS/cm²**
   (≈ 6 nS). Verified R_in drop at rest in the model: +2 → 51.6 %, +3.33 → 64.0 % (measured in
   cells: 56 %, which the model would reach with +2.39). **Decision: use 3.33 mS/cm²** so the
   on-screen "10 nS" and the pA scale agree; say "≈ 10 nS" if challenged. Alternative in
   `WORKBENCH.md`.
2. **Matched constant offset (a design addition).** The outline leaves the left offset
   unspecified. Using the drive alone (offset 0) makes the left column fire 121 spikes in
   500 ms (~240 Hz, unreadable) and conflates "extra outward current" with "voltage
   dependence". Matching the left offset to the clamp's mean isolates the voltage dependence —
   exactly the caption's point. Verified: sub-threshold mean V is nearly equal (−53.6 vs
   −52.5 mV) while SD drops 6.63 → 2.25 mV (×2.9) and spikes 9 → 0.
3. **"Fewer spikes" = zero here.** Across seeds 1–6 (SD 10–12, I0 85–90) the right column never
   spiked (0/18 runs) while the left fired 4–10. This matches paper Fig. 1A (repetitive spiking
   suppressed in the high-conductance state). If the user wants 1–3 right-column spikes, see
   the +2 mS/cm² alternative (22 vs 3 spikes, but right mean V sits 4.5 mV higher).
4. The noise is far larger than the paper's MPO noise (σ = 0.1 µA/cm²); it stands in for the in
   vivo barrage, not for the paper's simulations. Adaptation (z, I_M) is omitted to isolate the
   conductance effect; the paper's Fig. 1A model includes it.
5. Right V never goes below −70 mV (100 % of samples above), so the clamp current is always
   outward — consistent with the drawn "outward ↑" axis staying positive.

## 10. Acceptance checklist

- [ ] First frame: both titles, labelled empty panels, "spikes: 0" in both columns.
- [ ] Input strips identical in both columns.
- [ ] Left current is a perfectly flat line at 175 pA; right current visibly tracks right V.
- [ ] Right V excursions ~⅓ of the left's; no right spikes; left counter ends at 9.
- [ ] Cursors stay in sync; the callout appears at ≈ 209 ms and is gone before the caption.
- [ ] "same average: 175 pA" label and the two-line caption in the end frame; held ≥ 1.5 s.
- [ ] No equations, no title; text ≥ font 24; PURPLE_C only on dynamic-clamp elements.
- [ ] Fits ±4.2 × ±3.75 at `-r 672x600`; total ≈ 15 s.
