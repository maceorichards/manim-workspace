# Science — "Decay vs ring"

Sources: deck spec, top matter, slides 1–3 (takeaways, content, Say, If asked). Read
2026-09-30.

## The talk around it

- Paper: Prescott et al. (2008), *Pyramidal neurons switch from integrators in vitro to
  resonators under in vivo-like conditions*, J Neurophysiol 100.
- The audience knows none of: complex eigenvalues, phase planes, nullclines, bifurcation types.
  Build every idea geometrically first.
- Slide 1 (`sinusoids_to_power_spectrum`) ends by planting "a neuron returning to rest after a
  small kick behaves like e^{λt}, λ = σ + iω; Re sets the decay, Im the rotation". That video
  never shows a rotating point. **This video cashes it in** and is the only one with a rotating
  point in a complex plane.
- Slide 2 (`iv_curve_assembled_unbent`) introduced class 1 (SNIC, hump, integrator) vs class 2
  (Hopf, monotonic I–V, resonator), using the same model and the same CONTROL/SHUNT states.
- The refrain: *Whether a neuron is an integrator or a resonator is decided by the sign of the
  net current near threshold — and that sign is set by the synaptic background, not by the cell.*
  It is not repeated on this slide.
- **This video carries the slide.** The slide has no static visuals, and the end frame is the
  slide's still.

## Slide takeaway

A small perturbation returns as e^{λt}.
- **Class 1:** λ is real. The cell slides straight back with no overshoot, and just above
  threshold it can fire arbitrarily slowly.
- **Class 2:** λ is complex. The cell **rings** at Im λ/2π, damped by Re λ, and the moment Re λ
  crosses 0 it fires, already at f_min.

## Concepts, in plain words

1. δV(t) = Re[c·e^{λt}] = e^{Re λ·t} × (rotation at Im λ). **Re λ sets the decay; Im λ sets the
   ring frequency.** The electrode sees only the real part: the "vertical shadow" of the rotating
   point, which is why Part 1 puts Re on the vertical axis and draws a projector line.
2. **A bifurcation is λ crossing zero.**
   - SNIC: a real λ passes through 0 as the stable node and a saddle merge. They leave a "ghost"
     that the trajectory crawls past, so the first spikes are slow.
   - Hopf: a complex pair crosses the imaginary axis (Re λ = 0), so the first spikes are already
     fast.
3. **Phase-plane vocabulary:** the nullclines are where V or w stops changing. The fixed point
   (rest) is where they cross. A **saddle-node** (tangent crossing) means no ringing. A **focus**
   means ringing.
4. **Integrator vs resonator, concretely.** An integrator asks *"how close together were the
   inputs?"*; a resonator asks *"were they in rhythm?"* That is the pulse-pair test at the end.

## Speaker lines (Say)

- "Part 1 is a cartoon of what happens right next to rest; Part 2 is the paper's own model."
- Point out that the model's ringing is ~100 Hz, far too fast for θ: "Hold that thought — it's
  exactly the problem the authors hit on slide 6." Slide 6's video (`m_current_theta_ringing`)
  reuses this video's visual grammar (nullclines, focus = ring) on a slower variable.

## Likely questions

- *"Isn't Re λ always negative, since a time constant is positive?"* For a passive membrane, yes:
  λ = −1/τ_m. Near threshold, though, Na⁺ activation makes the slope conductance negative (the
  falling side of slide 2's hump). The effective τ passes through ∞ and changes sign, so λ
  crosses 0, and that crossing *is* threshold. The paper's onset conditions (Fig 5) are λ = 0
  statements:
  - SNIC: ∂I_ss/∂V = 0.
  - Hopf: −(1/C)∂I_inst/∂V = φ_w/τ_w, i.e. zero trace, so Re λ = 0.
- *Is the class 1 λ exactly real?* Well below threshold, yes (a stable node). Very close to
  threshold, the control model's stable point briefly becomes a focus, but it is so damped that
  no ringing is visible. "Real λ" is the right cartoon. This is why the staircase avoids
  0.93–0.999 × I_bif.
- *Why is class 1 onset slow?* Past a saddle-node, the time spent near the ghost scales like
  1/√(I − I_bif), so the rate rises continuously from 0: 11 Hz at 1.0005×, 21 Hz at 1.002×, 30 Hz
  at 1.005×.
- *Why the pulse pair?* Two subthreshold kicks summate in an integrator only if they come close
  together, because each one decays monotonically. In a resonator the first kick starts a ring,
  and the second fires the cell only if it lands in phase, about one ring period (~9.7 ms) later.
