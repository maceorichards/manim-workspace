# Video contract — "The phasor behind the ringing" (DRAFT, ideation stage)

## 1. Header

| | |
|---|---|
| Deck id | `s09_vid3` (new; not yet in the deck manifest) |
| Title | The phasor behind the ringing |
| Scene class | `EigenvaluePhasorRinging` |
| Placement | candidate: slide 9 build 9d, beside or instead of s09_vid2, or backup. The user decides. |
| Duration | ~24 s (hard cap 25 s) |
| Audio | silent |
| Playback | click-to-play; the first frame reads when paused; the last frame works as a still |

Sources: deck outline slide 9 ("frequency is geometry", MPO section), slide 5 "If asked";
background §20–21; debrief (MPO frequency = imaginary eigenvalue component); paper Results.
Read 2026-09-29. Numbers are from `model.md`.

## 2. Purpose

Takeaway: **a kick's aftermath is a spinning, shrinking arrow. Im λ is how fast it spins, so
MPO frequency = Im λ / 2π; Re λ is how fast it shrinks. A class 1 cell's arrows never spin, so
there is nothing to ring with.**

It explains why s09_vid2's MPO readout is |Im λ|. It is the 3b1b "circle → sine" picture,
applied to the paper's model.

## 3. Must show / must not show

Must show
- Two conjugate arrows, c·e^{λt} and c̄·e^{λ̄t}, counter-rotating and shrinking in a complex
  plane. Their sum stays on the real axis and is δV(t).
- The sum's shadow drawing δV(t) on a time strip, over simulated dots from the full model
  (0.2 mV kick, so they coincide within 3%).
- λ's two parts named: spin (Im λ → Hz) and shrink (Re λ → e-fold time).
- At I_Hopf the arrows keep their length (sustained ringing at ≈ 104 Hz).
- Class 1: real λ, so the arrows lie on the real axis and never turn; the shadow is a plain
  relaxation.

Must not show
- No θ labels (≈ 100 Hz here).
- No arrow that changes λ while it spins. Each phasor run uses one fixed current; a change of
  current is shown as λ moving in the inset, then a fresh kick.

## 4. Layout (8.96 × 8 frame)

| Region | Box | Content |
|---|---|---|
| Tag | anchor (−4.15, 3.45), left | "Class 2 · Hopf" `ORANGE` / "Class 1 · SNIC" `BLUE_C`, font 32 |
| λ inset | x [2.4, 4.15] × y [2.0, 3.6] | mini λ-plane, same scale as s05_vid3/4; one filled × pair in the class color |
| Phasor plane | x [−4.15, −0.5] × y [−1.4, 2.2] | complex plane of δV contributions, "Re", "Im", unit = the kick size; arrows: λ-arrow in the class color, conjugate arrow in the class color at 60%, sum as a `YELLOW` dot on the real axis |
| Time strip | x [−0.2, 4.15] × y [−1.4, 1.6] | δV(t), 0–40 ms, with the vertical axis aligned to the phasor plane's real axis rotated (3b1b style: the shadow travels right along a guide line); curve `WHITE` stroke 3, sim dots `GREY_A`; dashed envelope ±e^{Re λ t} |
| Equation | (−2.3, −2.1) | `\delta V(t) = c\,e^{\lambda t} + \bar c\,e^{\bar\lambda t}`, then `e^{\lambda t} = e^{\mathrm{Re}\,\lambda\,t}\,e^{i\,\mathrm{Im}\,\lambda\,t}`, font 32–36 |
| Readouts | (2.0, −2.1) | "spin = Im λ → 101 Hz", "shrink = Re λ → 10 ms" |
| Caption | (0, −3.3) | font 36–40 |

Projection geometry (decided 2026-09-29): the phasor plane is rotated 90°, with the real axis
vertical and labelled "Re (= δV)" and the imaginary axis horizontal. The sum's shadow then runs
straight right along a guide line into the time strip. Confirm on the beat 1 snapshot; the
fallback is to keep Re horizontal and draw δV(t) with time running downward.

## 5. Beat sheet (≈ 7 ms model per video second during phasor runs)

| # | Video t (s) | Model | On screen / motion | Text |
|---|---|---|---|---|
| 1 | 0.0–1.5 | class 2, I = 112.5 | Still: inset λ = −0.099 ± 0.634i; the two arrows at t = 0 (length 0.114 × scale, angles ∓28.7°), their sum at +0.2 mV; empty strip; kick marker | tag |
| 2 | 1.5–7.0 | t 0 → 40 ms | The arrows counter-rotate (period 9.90 ms) and shrink (e-fold 10.1 ms); the sum's shadow draws a damped cosine over the sim dots; the envelope fades in at ~4 s | equation line 1 |
| 3 | 7.0–9.5 | freeze | Equation line 2 writes. Spin angle highlighted, then "spin = Im λ → 101 Hz"; radius shrink highlighted, then "shrink = Re λ → 10 ms" | readouts |
| 4 | 9.5–13.0 | I 112.5 → I_Hopf, then a fresh 0.1 mV kick (`KICK_HOPF`) | The inset × slides to the imaginary axis (0.652i). A new kick, the same size on screen because the plane's unit is the kick: the arrows spin at 104 Hz without shrinking (circles), and the shadow is a steady sine | "at the crossing it is already spinning" |
| 5 | 13.0–19.0 | class 1, I = 38.7 → 38.73 | Cut; tag swaps. Inset: two real ×'s (−0.116, −0.239). Phasors: two arrows on the real axis, +0.775 (slow) and −0.575 (fast, pointing left), summing to +0.2. They shrink without turning; the shadow rises briefly (the fast arrow dies first) and then relaxes, never undershooting. Then the inset × slides toward 0 and a fresh kick at 38.73: the slow arrow barely shrinks | "Im λ = 0 → nothing to ring with" |
| 6 | 19.0–24.0 | end frame | Two mini panels: class 2 (spiral trace of the arrow tip + damped cosine) vs class 1 (flat arrows + relaxation) | caption "MPO frequency = spin rate = Im λ / 2π" |

## 6. End frame (still-image fallback)

Left mini panel: orange, the tip's inward spiral and a damped cosine. Right mini panel: blue,
two collinear arrows and a smooth relaxation. The λ inset shows both λ's. Caption as above.

## 7. Data

| Element | Source |
|---|---|
| Arrows, their angles and lengths | `kick_modes(I, p, KICK_DV)` → (λ, c); arrow k at time t = c_k e^{λ_k t} |
| Shadow curve | `lin_kick(I, p, KICK_DV, t)` |
| Sim dots | `run(p, I, 0, 40, [V* + KICK_DV, w*])`, subsampled every 0.5 ms |
| Readouts | `mpo_hz(λ)`, −1/Re λ |

## 8. Continuity

- s09_vid1 (noise-driven spiral) and s09_vid2 (MPO readout = |Im λ| vs shunt) use the same
  SHUNT operating point, I = 112.5, and ≈ 100 Hz.
- s05_vid3/s05_vid4 share the λ scale and the × markers.

## 9. Accuracy flags

1. The phasor picture is the linearization. It is exact only for small kicks: 2.6% of the kick
   at 0.2 mV over 40 ms at I = 112.5, rising to 7% at 0.5 mV (model.md). Keep KICK_DV = 0.2 and
   scale the display.
2. **At I_Hopf the full model is not a pure circle.** The Hopf is subcritical, so the nonlinear
   ringing slowly grows: over 30 ms at I_Hopf the sim-vs-linear error is 4.6% of a 0.2 mV kick.
   Decided: beat 4 uses a 0.1 mV kick (`KICK_HOPF`), 2.2%, asserted < 3%, and keeps the dots.
3. **Near I_SN a kick can cross the saddle's stable manifold and fire.** At 38.74 the saddle is
   only 0.27 mV from rest along V. Use 38.73 or lower (0.94 mV gap; verified that a 0.2 mV kick does not fire at 38.719, 38.73 or 38.735), and assert it in main.py.
4. Class 1 at 38.0 is complex but overdamped (arrows turn about 13° per e-fold). Not shown in
   this video; it is a Q&A answer in science.md: "it spins too slowly to ring".
5. ~100 Hz, not θ.

## 10. Acceptance checklist

- [ ] The two arrows' sum stays on the real axis every frame (assert |Im(sum)| < 1e-9).
- [ ] The shadow meets the sim dots within 3% of the kick.
- [ ] The Hz and ms readouts match `mpo_hz` and −1/Re λ.
- [ ] Class 1 arrows never leave the real axis.
- [ ] End frame held ≥ 1 s; total ≤ 25 s.
