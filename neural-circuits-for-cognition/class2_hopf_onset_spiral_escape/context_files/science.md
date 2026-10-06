# Science — "Class 2: the whirlpool lets go"

Sources: deck outline, slide 5 (content, table, video visuals, "Say", "If asked") and slide 6
(model, prediction chain); background notes §19–26, §28, §35, §37; debrief; paper Methods,
Results (MPO section), Fig. 4A, 5A and 5B legends. Read 2026-09-29.

## Concepts the video depends on (plain language)

- **Phase plane, nullclines, fixed point**: as in `class1_snic_onset_slow_crawl` — voltage V across, K⁺ activation w
  up; where the two "no-change" curves cross is rest.
- **Focus (spiral point).** In the shunted model the curves cross at an angle, and rest is a
  point that trajectories *spiral* into. A push off rest does not just slide back; it overshoots,
  swings back, overshoots less: **damped ringing**. The ringing speed is set by how fast the
  spiral turns (the imaginary part of the eigenvalue, ≈ 100 turns per second here); how quickly
  it dies is set by the real part.
- **Why it spirals (biophysics).** Net current at threshold is outward: a depolarising push
  starts to open Na⁺ channels (inward), but the delayed K⁺ current catches up before a full
  spike, pulls V back down past rest, then relaxes, and so on. Inward current racing against
  slower outward current is the oscillation.
- **Hopf bifurcation.** As current increases, the spiral pulls in more and more weakly. At the
  Hopf point it stops pulling in and starts pushing out: rest still exists, but it is unstable.
  The trajectory spirals outward, already turning at ~100 Hz, and lands on the large spiking
  loop. Firing therefore starts at a high rate, never near 0 Hz: a discontinuous f–I curve.
- **Subcritical Hopf and bistability.** In this model the big spiking loop already exists a
  little below the Hopf point (from I ≈ 113.14 to 114.24 µA/cm²). In that window the cell can
  either rest or fire, depending on history: a large enough push starts firing. The slowest
  sustainable rate there is f_min ≈ 80 spikes/s. The largest ringing frequency, at the Hopf
  point, is ≈ 104 Hz. The gap is the paper's Δf, so "MPO frequency < f_min + Δf" (paper Fig. 5B).
- **The two facts are one.** Subthreshold ringing and a minimum firing rate both come from the
  spiral: the neuron is already turning at a certain rate when it lets go.

## Slide 5 content around the video (paraphrased)

The class 1 / class 2 table (see `class1_snic_onset_slow_crawl` science.md for the full grid). Class 2
row: net current outward at threshold; rest disappears by a fixed point destabilising while
spiralling (Hopf); analogy, a whirlpool that spins you out, already turning at some rate when it
lets go; rate jumps to a minimum f_min; discontinuous f–I; subthreshold oscillations yes
(ringing around the spiral point); computation prefers an input frequency.

Speaker ("Say"): (1) the spiral is why class 2 cells oscillate below threshold — the oscillation
and the minimum firing rate are the same fact seen twice; (2) the distinction is qualitative,
not "faster vs slower". For this video: "watch the ringing last longer as I turn the current
up; at threshold the whirlpool throws the ball out, and it leaves at full speed."

"If asked": the spiralling rate is the imaginary part of the eigenvalue at the fixed point, the
formal version of the outline's "the sharper the nullcline crossing, the faster the oscillation". Careful: the paper says frequency rises as the crossing becomes *less* acute (wider angle); say "the wider the crossing, the faster the spiral".

Slide 6 context: the shunted model is the control model plus 2 mS/cm² of conductance reversing
at −70 mV (in the paper's dynamic-clamp experiments: 10 nS at −70 mV, a 56% drop in input
resistance). Since −70 mV is below threshold, the shunt adds outward current at threshold,
which is what converts SNIC into Hopf. Parameters were taken from previous work, not fitted.

## Paper results and numbers relevant here

- Model: shunting (g_shunt 2 → 4), adaptation (g_M = 2) or both convert spike initiation from
  SNIC to subcritical Hopf; the steady-state I–V becomes monotonic (paper Fig. 1).
- Shunted model f–I (paper Fig. 4A): shifted right and discontinuous, f_min 80 spikes/s.
- Fig. 5B (shunted model): bifurcation diagram and f–I over 110–120 µA/cm²; the fixed point
  and the limit cycle overlap between ≈ 113.1 and 114.3; max MPO frequency ≈ 103 Hz vs
  f_min ≈ 77 Hz, gap Δf.
- Verified here (model.md): Hopf at 114.236 µA/cm² (≈ 343 pA), ringing 103.8 Hz at the Hopf,
  spiking from 113.137 (≈ 78–80 spikes/s) upward; 111.7 spikes/s at 115.
- Experiment (paper Fig. 4C): in CA1 cells a 10-nS shunt raised f_min from 3.5 ± 1.0 to
  16.4 ± 1.4 spikes/s (P < 0.001, n = 6); adaptation raised it further (paper Fig. 4E, P < 0.005).
- The model's ~100 Hz is an order of magnitude above θ (3–10 Hz); the paper corrects this with
  slow I_M on slide 11. Numbers here are qualitative illustrations of the geometry.

## Likely audience questions

- *Why does the ringing last longer as current rises?* The spiral's pull (real part of the
  eigenvalue) weakens toward zero at the Hopf point while its turning rate hardly changes
  (95 → 104 Hz). Per cycle the ring keeps 8%, 37%, then 88% of its size in the video.
- *Why ~100 Hz? Cells oscillate at θ.* This model's spiral uses the fast delayed-rectifier K⁺
  current; θ needs the slow M-current (slide 11). The geometry is the point, not the number.
- *Is the jump to firing at f_min?* Not exactly: past the Hopf point it fires at ≈ 105–112
  spikes/s; the lowest possible rate (≈ 80) is reached only in the bistable window just below.
- *What are the kicks?* Brief current pulses (+1.2 mV). In cells, synaptic noise plays this role
  (slide 9).
- *Why does the dot jump so far?* Once the spiral pushes out, the nearest attractor is the big
  spiking loop; there is no small stable oscillation in a subcritical Hopf.
