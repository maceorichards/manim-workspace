# Science — "Dynamic clamp in action"

Sources: deck outline slide 6 (content, static visuals, video visual 1) and slide 4 (sign of a
conductance); paper Methods (recordings, dynamic clamp, model, unit conversion) and Fig. 1A +
legend; background notes §3, §13, §14, §41, §45; debrief. Read 2026-09-29.

## Concepts the video depends on (plain language)

- **Current clamp.** The amplifier injects whatever current you command, regardless of what the
  cell's voltage does. A constant offset stays constant.
- **A conductance is a current that depends on voltage.** A channel with reversal potential E
  carries I = g(V − E): zero at E, outward (pulling V down) above E, inward below. A shunt with
  E = −70 mV is outward everywhere between −70 mV and threshold — the slide-4 "hinge".
- **Dynamic clamp.** The rig reads V in real time (10 kHz in the paper), computes g(V − E) and
  injects that current, so the cell behaves as if the channel existed. Ordinary current
  injection cannot do this, because a fixed current cannot push back harder when V rises.
- **Why the right trace is squashed.** Whenever the input pushes V up, the clamp immediately
  pulls back harder; whenever V dips, it pulls less. Fluctuations are damped (the membrane is
  "leakier": lower input resistance, faster time constant). With the same average extra current
  on the left, the left V is free to swing and cross threshold.
- **What it does to excitability.** Extra outward current at threshold is what, by slide 5,
  should push a neuron from class 1 (integrator, SNIC) toward class 2 (resonator, Hopf).

## Slide content around the video (paraphrased)

Slide 6 ("What the slice is missing, and how to put it back", ~3.5 min, background → the
hypothesis). Takeaway: in vivo background input adds **outward current at threshold**, which,
by slide 5, should push the cell from class 1 toward class 2.
- In the awake brain pyramidal cells are bombarded continuously (Destexhe & Paré 1999): ~80 %
  drop in input resistance, ~20 mV tonic depolarization, ~10× more voltage noise. A slice has
  almost none.
- Two effects matter: **shunting** (added conductance reversing near −70 mV, or −57 mV as the
  conductance-weighted E/I average — below threshold, so net outward near threshold) and
  **tonic depolarization**, which recruits adaptation currents (I_M, I_AHP), also outward.
- **Dynamic clamp in one sentence:** the rig reads V in real time and injects I = g(V − E), so
  the cell experiences a conductance that isn't there. Here: 10 nS, E = −70 mV, giving a 56 %
  drop in R_in. You cannot do this with current injection — that is the point of the technique.
- **The model:** modified Morris–Lecar, fast V, slow w (I_K,dr), very slow z (I_M); the minimum
  model that spikes and can still be drawn on a phase plane. Parameters taken from previous
  work, not fitted to these data — say this plainly; the model is qualitative by design.
- **Prediction:** shunting and/or adaptation → more outward current at threshold → SNIC becomes
  Hopf → class 1 becomes class 2.
- Static visuals on this slide: slice vs intact brain (s06_v1), the dynamic-clamp loop (s06_v2,
  with the inset "ordinary current clamp: I is fixed and ignores V"), paper Fig. 1A, the three
  timescales clocks, the prediction chain.

Suggested narration: "Same neuron, same input. On the left we add a fixed current — the same
amount, on average, that the dynamic clamp adds on the right. On the right the current follows
the voltage: the higher V goes above −70, the harder it pulls back. Same average current, but
only the voltage-dependent one squashes the cell. That dependence on voltage is what makes it a
conductance."

## Paper facts relevant here

- Recordings: whole-cell, CA1 pyramidal cells, rat slices at 30–31 °C, fast synaptic
  transmission blocked. Rest −73 ± 1 mV (SE), R_in 159 ± 9 MΩ; V held at −70 mV by tonic
  current; junction potential corrected (9 mV).
- Dynamic clamp: Digidata 1200A + DYNCLAMP2, update 10 kHz; a single conductance level,
  **10 nS, E = −70 mV**, causing an **average 56 % reduction in R_in**. Noisy current was
  injectable but its effects were not analyzed (one exception).
- Fig. 1A: a typical cell fires repetitively to a 320-pA step in the low-conductance state but
  only an initial burst to 480 pA in the high-conductance state; the model (with adaptation)
  reproduces this at 71 vs 153 µA/cm².
- Model units: currents and conductances are densities; assume 300 µm² → µA/cm² × 3 ≈ pA.
  The model's high-conductance state is g_shunt 2 → 4 mS/cm² (+2 ≈ 6 nS); 10 nS would be
  3.33 mS/cm². The video uses 3.33 (see `contract.md` flag 1).
- Downstream results using the same 10-nS shunt (slides 8, 10): V* shifted +2.3 ± 0.5 mV
  (P < 0.01, n = 6); f_min rose 3.5 ± 1.0 → 16.4 ± 1.4 spikes/s (P < 0.001, n = 6).

## Likely audience questions

- *Why not just inject a hyperpolarizing current?* It would lower the mean V but would not
  damp fluctuations or increase outward current more at threshold than at rest. The left column
  is exactly that experiment: same average current, no squash, still spiking.
- *Is a somatic dynamic-clamp conductance like real synaptic bombardment?* Partly: it is a
  point conductance at the soma standing in for input distributed over the dendrites; the
  update rate also limits how fast a conductance it can mimic. The paper cites prior validation
  (Chance et al. 2002; Destexhe et al. 2001).
- *Why −70 mV and not −57 mV?* −57 mV is the conductance-weighted E/I average; the paper says
  model results were qualitatively unchanged with −57 mV. Either is below threshold, so the
  shunt is outward at threshold.
- *Are the noise and drive from the paper?* No; they are chosen so the left column fires
  irregularly (~18 Hz). The model and the 10-nS/−70-mV clamp are the paper's.
- *Does the right cell never fire?* Not at this drive; stronger drive would make it fire, but
  with a higher threshold and a minimum rate (class 2) — slides 8 and 10.
