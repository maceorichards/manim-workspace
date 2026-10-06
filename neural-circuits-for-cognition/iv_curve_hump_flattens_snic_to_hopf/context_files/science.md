# Science — "The hump unbends"

Sources: deck outline slide 7 (content, static visuals, "Say") and top matter; debrief
(Results 1–2); background notes §10–12, §14, §23–26, §45; paper Results p. 3032–3033, Fig. 1
legend, Methods. Read 2026-09-28.

## The paper in one line

CA1 pyramidal neurons behave as class 1 integrators in a quiet slice but become class 2
resonators under in-vivo-like conditions (tonic depolarization + shunting conductance), because
the extra outward current near threshold switches the spike-initiating mechanism from SNIC to
subcritical Hopf (Prescott, Ratté, De Koninck & Sejnowski 2008, J Neurophysiol 100:3030–3042).

## Concepts the video relies on (plain language)

- **Net current and its sign.** The membrane is a capacitor: voltage moves in whichever direction
  the net ionic current pushes it. Convention here (as in the paper): outward current is
  positive and pushes V down; inward current is negative and pushes V up.
- **Steady-state I–V curve.** For each voltage, let every channel settle, then add up the
  currents: I_Na + leak/shunt + I_K,dr (+ I_M when adaptation is present). The paper's Fig. 1C
  legend defines it exactly this way; the "instantaneous" curve uses only I_Na + leak.
- **The hump.** In control the steady-state curve is nonmonotonic: it has a local maximum
  (≈ −38 mV) and past it a short stretch of **negative slope** where depolarizing further makes
  the net current *more inward*. Inject just enough current and the cell can creep upward through
  that stretch slowly → it can fire arbitrarily slowly → SNIC, class 1, continuous f–I curve.
- **Unbent (monotonic).** Add outward current and the curve only rises: net current near
  threshold stays outward. Then fast I_Na has to win a race against slower K⁺ current before the
  net current turns outward → Hopf, class 2, a minimum firing rate (f_min > 0) and subthreshold
  oscillations.
- **Why shunt counts as outward current.** The shunt reverses at −70 mV; threshold is around −40
  to −30 mV, so at threshold a shunt pulls V down (outward). Adaptation (I_M) is a K⁺ current
  reversing near −100 mV, also outward there (background §14; paper Results p. 3032).
- **SNIC vs Hopf (only as words).** SNIC: the resting state and a threshold state merge and
  vanish; the cell then cycles through the spot where they vanished, arbitrarily slowly. Hopf:
  the resting state stays single but starts to ring and then loses stability, so firing starts
  at a finite rate; "subcritical" means it jumps straight to large spikes and there is a range
  where rest and firing coexist (background §25–26).

## What the slide says around the video (paraphrased)

- Takeaway: adding shunting and/or adaptation converts the model from SNIC to subcritical Hopf —
  the predicted class switch. The switch does not depend on which manipulation, only that
  outward current increased (Fig. 1B a–d).
- Teach the I–V read-out once, reuse it: the same nonmonotonic → monotonic conversion appears in
  Figs. 2C, 8E and 9E under different manipulations.
- **Say:** this is a model result, not yet data; be explicit that the experiments come next.
- Thesis sentence to repeat on this slide (see contract §2).

## Paper numbers relevant here (model, µA/cm², mS/cm²)

- Low- and high-conductance states: g_shunt 2 → 4 mS/cm², E_shunt = −70 mV (Methods; results
  were qualitatively the same with E = −57 mV).
- Adaptation: I_M with g_M = 2 mS/cm², τ_z = 200 ms, β_z = −30 mV, γ_z = 5 mV (Methods).
- Fig. 1B: control → SNIC at I_stim ≈ 39; shunt → Hopf ≈ 114; adaptation → Hopf ≈ 70; both →
  Hopf ≈ 160 (paper, z frozen). Our recomputation: 38.74, 114.24, 70.9 (68.3 with full 3-D),
  192.6 (with z at steady state; the paper froze z at a value taken from its Fig. 1A run).
- Fig. 1C inset: control hump between ≈ −40 and −30 mV, ≈ 1 µA/cm² deep (our value 1.06).
- Area conversion: 300 µm² (3 × 10⁻⁶ cm²), so µA/cm² × 3 = pA and mS/cm² × 3 = nS (Methods;
  background §45).
- Experiments (for "if asked", not shown): 10-nS dynamic-clamp shunt, E = −70 mV, cut input
  resistance by 56% on average; cells' resting R_in 159 ± 9 MΩ (paper Methods).

## Numbers this video puts on screen (verified in `model.md`)

- Shunt ramp readout 0 → 2.00 mS/cm² added; input resistance −0% → −52% (model).
- Mechanism switch at +0.17 mS/cm²; negative slope gone at +0.24 mS/cm² (R_in −11%).
- g_M 0 → 2.00 mS/cm² added on top.

## Likely audience questions (short answers)

- *"Why mS/cm², not the 10 nS they used?"* The model is per unit area; the paper models the
  high-conductance state as +2 mS/cm². For a 300-µm² cell that is 6 nS; what matches the
  experiment is the effect — input resistance halves in both (−52% model, −56% cells).
- *"The hump vanishes after only a tenth of the shunt — is that real?"* In this model, yes: the
  hump is only ~1 µA/cm² deep, and a shunt adds a constant slope (its conductance) at every
  voltage, so +0.24 mS/cm² is enough to cancel the steepest negative slope (−0.24 mS/cm²). The
  full +2 mS/cm² then pushes the model far into class 2 (f_min ≈ 78–80 Hz at the low edge of the
  bistable window, matching paper Fig. 4A's ~80 spikes/s; the deck build contract's 90–100 Hz
  overstates it — see `class2_hopf_onset_spiral_escape`).
- *"Is 'monotonic' exactly the same as 'Hopf'?"* Nearly. Monotonic guarantees Hopf. In a very
  thin band just before the hump disappears (added shunt 0.17–0.24 mS/cm²) the model already
  starts via Hopf while a vestigial hump remains; the video flips the label at 0.17 and the band
  closes at 0.24 within one flash.
- *"What does the y-axis mean exactly?"* Net steady-state current with the injected current set
  so the cell would sit at −34.4 mV (the middle of the hump) — every curve passes through 0
  there. The vertical scale is compressed (sign-preserving log-like) because the hump is ~1
  µA/cm² against a ~300 µA/cm² range; signs and zero crossings are exact.
- *"Does adaptation do the same thing alone?"* Yes (Fig. 1B c, 1C c): with g_M = 2 and no extra
  shunt the curve is monotonic too (it needs only g_M ≈ 0.08 with I_M at steady state).
- *"Why is the model's class 2 so fast (100 Hz)?"* Known limitation the authors fix on slide 11
  with a slower I_M (τ_z = 400 ms).
- *"Is this data?"* No — model. The experimental test (threshold shift, f_min) is slide 8.
