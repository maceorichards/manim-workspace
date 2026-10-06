# Workbench — eigenvalue_phasor_ringing_frequency

Context: `context_files/contract.md` (the draft video contract), `science.md`, `model.md`,
`style.md`. Sources: see `SOURCES.local.md` (gitignored; read-only root).

## The phasor behind the ringing

Status: Built — final render `videos/eigenvalue_phasor_ringing_frequency.mp4`, 1344×1200, 30 fps, 23.2 s
Scenes: EigenvaluePhasorRinging

### Intent

A kick's aftermath is δV(t) = c e^{λt} + c̄ e^{λ̄t}: two counter-rotating, shrinking arrows
whose sum stays real. Im λ is the spin rate (MPO frequency = Im λ/2π), Re λ the shrink rate.
Class 1's arrows never spin, so there is nothing to ring with.

### Decisions in force

- Deck box format from `style.md`: 1344×1200, ≤ 25 s, silent, end frame is a still.
- KICK_DV = 0.2 mV: linear vs full model within 2.6% of the kick over 40 ms at I = 112.5.
- Class 2 at 112.5: arrows start at length 0.114 (× scale), angles ∓28.7°, period 9.90 ms,
  e-fold 10.1 ms. Class 1 at 38.7: real modes +0.775 (λ −0.116) and −0.575 (λ −0.239).
- Each phasor run is at one fixed current. A current change moves λ in the inset, then a fresh
  kick.
- Class 1 near I_SN: kick at ≤ 38.73 (asserted: no spike).
- Conjugate pair: two counter-rotating arrows whose sum stays on the real axis, which is why
  δV is real and why λ comes in ± pairs. Class 1's two real arrows then use the same picture.
- Keep beat 4 (λ slides to the axis, the arrows circle at 104 Hz): it is class 2's
  punchline and mirrors class 1's arrow that stops shrinking but never turns.
- Beat 4 kick is `KICK_HOPF` = 0.1 mV, and the sim dots stay: 2.2% error over 30 ms, asserted
  < 3% (0.2 mV gives 4.6%). The phasor plane's unit is the kick, so the arrows look the same
  size as in beat 2.
- No class 1 at 38.0 case. Its arrows turn about 13° per e-fold, invisible at this size, and
  cost about 3 s; it is a Q&A note in `science.md`.
- Phasor plane rotated 90°: real axis vertical, labelled "Re (= δV)", so the sum's shadow runs
  straight right into the time strip. Confirmed on the beat 1 snapshot (kept; +Im points left,
  a pure rotation, so arrow 1 still turns counter-clockwise).
- One ValueTracker `T` (model ms) per run and one `I` for the inset λ; every moving element is
  a pure function of them (`always_redraw`), frozen with `clear_updaters()` at each run's end.
- Shared λ-plane spec as code at the top of `main.py` (`LamPlane`, `lam_cross`,
  `lam_saddle_cross`, color and stroke constants). Inset box x [2.4, 4.15] × y [2.0, 3.6].
- Arrows tip-to-tail (recommended option): arrow 1 = c e^{λt} from 0 in the class color,
  arrow 2 from its tip at 60% opacity, the sum a `YELLOW` dot on the real axis. Arrows fade
  between 0.15 and 0.05 scene units and are hidden below.
- Layout: class 2 view origin (−2.1, 0), 1.5 units per kick; strip x [−0.3, 4.05]; equations
  left-aligned at x −4.0 (y −2.3, −2.9); readouts left-aligned at x 0.45, font 28; caption
  y −3.45, font 36.
- **(agent's call — review)** The plane's unit is the kick in every run, but the display scale
  changes at the class 1 cut (1.5 → 1.0 units per kick, origin moved to y −1.6). Class 1's
  arrows are 3.87 and 2.87 kicks long (they nearly cancel), which cannot fit at the class 2
  scale. The cut redraws the axes, and the "0.2 mV kick" marker shows the new unit.
- **(agent's call — review)** Class 1 is drawn **without sim dots**. Near I_SN the
  linearization is 13.5% (38.7) and 39% (38.73) of the kick off the full model over 40 ms
  (quadratic nonlinearity near the saddle-node); the dots would visibly leave the curve.
  Qualitatively the full model agrees (no undershoot, no spike; asserted).
- **(agent's call — review)** Class 1 runs play at 16.7 ms model per video s (40 ms in 2.4 s)
  instead of ≈ 7 ms/s, to fit both class 1 runs in 6 s. The strip's axis is model time, so
  pacing never distorts the data; nothing spins, so speed costs no legibility. Beat 4 runs at
  8.7 ms/s (20 ms, two circles).
- **(agent's call — review)** Class 1's collinear arrows are split sideways ±0.13 units
  (schematic) and labelled "slow" (left) and "fast" (right); labels fade once the arrow is
  shorter than 0.4 units.
- **(agent's call — review)** Readout wording when a part of λ vanishes: "shrink = Re λ = 0"
  at I_Hopf, "spin = Im λ = 0" for class 1; class 1's shrink readout lists both e-fold times
  ("8.7, 4.2 ms", then "17, 4.3 ms" at 38.73), which is what shows the slow arrow lingering.
- **(agent's call — review)** Class 1 equation line 1 becomes
  `δV(t) = c_1 e^{λ_1 t} + c_2 e^{λ_2 t}` (the class 2 form with c̄, λ̄ is false for two
  real modes); line 2 stays.
- **(agent's call — review)** End frame: class 1 panel is the 38.7 run (arrows at t = 0 +
  relaxation), and the inset's blue ×'s slide back to 38.7 to match it (a 0.05-unit move).
  Panels carry "Im λ/2π = 101 Hz" and "Im λ = 0" under them. Beat transitions are cuts
  (fade out, fade in) because `Transform` between the two layouts and between readouts
  garbled glyphs mid-animation.
- **Correction to the contract:** class 1's shadow is **not monotone**. The fast (negative)
  mode dies first, so δV rises from 1 to 1.34 kicks (at 3.5 ms; 1.61 at 5.5 ms for 38.73)
  before relaxing, in both the linear curve and the full model. It never undershoots, so the
  "nothing to ring with" story stands; no on-screen text claims monotone. `model.md` corrected.

### Checklist

- [x] Beat 1: first frame, class 2 at 112.5, arrows at t = 0, inset λ
  - Outcome: kept — the tip-to-tail arrows land the yellow sum on the vertical Re axis at the
    kick and the dashed guide runs level into the strip, so the rotation reads; the inset's
    "Im λ" label was moved to the inset's top-left corner after it sat on the upper orange ×.
- [x] Beat 2: arrows spin and shrink, shadow draws δV(t) over sim dots, envelope
  - Outcome: revised — scale raised 1.25 → 1.5 units per kick (the first pass left the lower
    half empty); the "0.2 mV kick" label moved above the strip with a dotted leader after the
    curve's first peak ran through it. The 2.2 s frame shows arrow 1 below the axis with arrow 2
    closing to the sum; dots sit on the curve.
- [x] Beat 3: freeze, split λ into spin (101 Hz) and shrink (10 ms)
  - Outcome: revised — at the freeze (40 ms) both arrows are gone, so the spin is shown as a
    red curved arrow around the spiral and the shrink as a red inward arrow, with a red box
    moving from e^{i Im λ t} to e^{Re λ t} and the envelope turning red. `\;` renders as
    nothing in 1.7.2 Tex, so "→" spacing uses `\ `.
- [x] Beat 4: λ slides to the axis, fresh kick at I_Hopf, arrows keep length
  - Outcome: kept — the 12.7 s frame shows a closed orange circle and a steady sine over the
    dots, peaks level with the first; kick label moved up to 1.42 kicks so the sine's peaks
    (1.2 kicks) clear it.
- [x] Beat 5: class 1, collinear real arrows, relaxation; λ → 0, slow arrow barely shrinks
  - Outcome: revised — the cross-fade cut garbled the readouts (Transform between Tex strings)
    and stacked two planes; now a 0.3 s fade-out then 0.35 s fade-in. At 38.73 the frame shows
    the slow arrow still visible at 40 ms and the new curve above the 30% copy of the first.
- [x] Beat 6: end frame, two mini panels, caption
  - Outcome: revised — the Transform of the class 1 view into its panel was chaotic at 19.2 s;
    replaced with fade-out/fade-in. Left panel Im axis shortened (it crossed x −4.2). Last frame:
    orange spiral + damped cosine, blue flat arrows + relaxation, both λ's in the inset.

### Open questions

- Placement (slide 9d vs backup) is still the user's call (contract §1).
- Review the "(agent's call — review)" decisions above, especially the class 1 scale change
  and the missing class 1 sim dots.

### Parking lot

- Extract the model and eigen helpers (copied into all three eigenvalue topics) into a shared
  module once a fourth copy would appear.
- A RED_C ring flash (radius ≥ 0.4) when the inset × reaches the imaginary axis in beat 4.
- Show class 1's full-model dots in a Q&A variant, to make the point that the linear picture
  fails near the saddle-node (13.5% at 38.7, 39% at 38.73 for 0.2 mV).
- Time scale on the end-frame mini strips ("40 ms").
