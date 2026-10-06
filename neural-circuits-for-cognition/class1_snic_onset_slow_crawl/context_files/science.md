# Science — "Class 1: rest vanishes, the ball crawls"

Sources: deck outline, slide 5 (content, table, static and video visuals, "Say", "If asked") and
slide 6 (model description); background notes §18–26, §28, §31; debrief; paper Methods, Results
(f–I and MPO sections), Fig. 1, 4 and 5 legends. Read 2026-09-29.

## Concepts the video depends on (plain language)

- **State and phase plane.** The model neuron's condition at any instant is two numbers: the
  voltage V (fast) and w, how open the delayed-rectifier K⁺ channels are (slow). Plot V across and
  w up: the neuron is a point, and the equations say which way and how fast that point moves.
- **Nullclines.** The V-nullcline is every (V, w) where V is momentarily not changing; the
  w-nullcline is where w is not changing. The V-nullcline is N-shaped (only its lower bend, "the
  knee", matters here); the w-nullcline is a rising S-curve.
- **Fixed points.** Where the two nullclines cross, nothing changes: a resting state. A *stable*
  one pulls nearby states in (rest). A *saddle* pulls in along one direction and pushes out along
  another: it is the "threshold" point, the pass over the ridge.
- **Injecting current** lifts the V-nullcline. In the class 1 model, lifting it slides the rest
  point and the saddle toward each other along the lower knee.
- **Saddle-node bifurcation.** At one current (I_SN) the two points touch (the nullclines become
  tangent) and then both disappear. There is no rest state left, so the neuron must fire.
- **SNIC (saddle-node on invariant circle).** The collision happens on the loop that the spiking
  trajectory follows. Just after the collision, the flow near the spot where the points died is
  almost zero: a **ghost** or bottleneck. Every cycle has to squeeze through it, and the closer
  the current is to I_SN, the longer it takes. The period can be made arbitrarily long, so the
  rate starts from 0 Hz and rises continuously (≈ √(I − I_SN)): the class 1, continuous f–I curve.
- **Why no ringing.** Nothing is spinning: the rest point loses its existence, not its stability.
  There is no spiral point, so no subthreshold oscillation (this is the slide 9 point).
- **Net current is inward at threshold.** The steady-state I–V curve of the control model has a
  local maximum (a region of negative slope); the saddle-node sits exactly at that maximum,
  where net steady current is zero and its slope is zero (paper Fig. 5A legend). Past it,
  depolarisation brings in net inward current.

## Slide 5 content around the video (paraphrased)

Takeaway: class 1 and class 2 are not about firing rate; they are two geometries of spike
initiation, and each brings a package of properties.

| | Class 1 (integrator) | Class 2 (resonator) |
|---|---|---|
| Net current near threshold | inward | outward |
| Rest disappears by | two fixed points colliding (SNIC) | a fixed point destabilising while spiralling (Hopf) |
| Analogy | a valley that flattens out and vanishes; the ball can crawl through arbitrarily slowly | a whirlpool that spins you out; already turning when it lets go |
| Rate at onset | can be arbitrarily slow (0 Hz) | jumps to a minimum rate f_min |
| f–I curve | continuous | discontinuous |
| Subthreshold oscillations | impossible (nothing to spiral around) | yes, ringing around the spiral point |
| Computation | sums inputs broadly | prefers an input frequency |

Speaker ("Say"): land two points: (1) the spiral is why class 2 cells oscillate below threshold;
the oscillation and the minimum rate are the same fact seen twice; (2) this is a qualitative
distinction, not "faster vs slower". For this video: "rest does not become unstable, it stops
existing; afterwards the neuron keeps passing through the place where rest used to be, and it
crawls there — that is why it can fire as slowly as you like."

"If asked": the rate of spiralling (class 2) is the imaginary part of the eigenvalue at the fixed
point; the outline phrases it "the sharper the nullcline crossing, the faster the oscillation", but the paper says frequency rises as the crossing becomes *less* acute, so say "the wider the crossing, the faster" (see `s09_vid2_frequency_geometry`). No algebra needed.

## Paper results and numbers relevant here

- Model (paper Fig. 1, 4A, 5Aa): the low-conductance (control) model starts spiking through a
  SNIC; its f–I curve is continuous. Adding shunting (g_shunt 2 → 4) or adaptation (g_M = 2)
  converts it to a subcritical Hopf with a discontinuous f–I curve (shunted f_min ≈ 80 spikes/s).
- Model numbers verified here (model.md): I_SN = 38.741 µA/cm² (≈ 116 pA for the paper's
  300 µm² cell), V_SN = −38.3 mV; 8 spikes/s at 0.009 µA/cm² above I_SN, 34 spikes/s at +0.26.
- Experiment (paper Fig. 4B–C): CA1 cells, f_min rose from 3.5 ± 1.0 to 16.4 ± 1.4 spikes/s
  with a 10-nS dynamic-clamp shunt (P < 0.001, paired t-test, n = 6).
- The paper's own caveat: no experiment can show firing arbitrarily close to 0 spikes/s (channel
  noise sets a floor), so the argument rests on the *increase* in f_min, not a literal 0 Hz.
- Parameters were taken from previous modelling work, not fitted to these data; the model is
  qualitative by design (paper Methods; outline slide 6).

## Likely audience questions

- *Why does the dot slow down if there is no fixed point any more?* Just past the collision the
  flow at that spot is almost zero, because a fixed point nearly exists there. The closer the
  current is to the collision value, the slower the passage.
- *Is "arbitrarily slow" real?* In the model yes (f ∝ √(I − I_SN)). In cells, noise gives a floor;
  what the paper measures is that f_min rises when the cell is shunted.
- *Where is the threshold?* Below I_SN it is the saddle: kicks that push past it trigger a spike.
  At I_SN the threshold and rest merge.
- *Why does current lift the V-nullcline?* More injected current must be balanced by more K⁺
  current for V to stay put, so the balance point needs a larger w at every voltage.
- *What is the third crossing further right?* An unstable point that the spiking loop circles;
  it plays no role in spike initiation, so it is not drawn.
- *Why a 2-D model?* It is the smallest model that can spike and still be drawn on a page; the
  third variable (slow adaptation, z) is absent in this control version.
