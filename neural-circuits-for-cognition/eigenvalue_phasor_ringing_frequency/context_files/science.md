# Science — eigenvalue_phasor_ringing_frequency

Sources: deck outline (slide 5 content table, "Say", "If asked"; slide 9 "frequency is
geometry"; Assembly notes); background §20–26; debrief (dynamical analysis, MPO frequency);
paper Methods and Fig. 5A/5B legends. Read 2026-09-29. The model numbers are in `model.md`.

## Concepts the three eigenvalue videos rest on (plain language)

- **Linearizing at a fixed point.** Near rest, a small push δx evolves as δx' = J δx, where J
  is the Jacobian. The eigenvalues λ of J are the rest point's "personality": every small
  response is a mix of e^{λt} terms.
- **Reading λ.**
  - Re λ < 0: the push dies away. Re λ > 0: it grows. The imaginary axis is the stability
    line.
  - Im λ ≠ 0: the response turns, at Im λ/2π cycles per ms.
  - Two real λ make a node, with no turning. A complex pair makes a focus, a spiral.
  - A saddle has one positive and one negative real λ.
  - A focus needs complex λ, and the paper's "angle at which the nullclines cross" is the
    geometric stand-in for that (background §21).
- **MPO frequency = Im λ / 2π** at the focus. The paper states this directly (Results, MPO
  section), and it is the deck's "If asked" line on slide 5.
- **Two ways rest can be lost as current rises:**
  - **Saddle-node (class 1).** Rest meets the saddle and both vanish. At the meeting point one
    eigenvalue of each is exactly 0, which is the same as ∂I_ss/∂V = 0, the top of the I–V hump.
    Right after, the trajectory crawls through the "ghost", so firing can start arbitrarily
    slowly (SNIC).
  - **Hopf (class 2).** Rest survives but turns unstable: the complex pair crosses Re = 0 with
    Im ≠ 0. The cell is already turning at Im λ/2π ≈ 104 Hz when it lets go, so firing starts
    at a high rate. In this model the Hopf is subcritical, with a bistable window just below it.
- **The one-line contrast.** Class 1 crosses the stability line **at the origin**; class 2
  crosses it **at ±iω**. The integrator/resonator split is that one number: Im λ at the
  crossing.
- **Complex is not enough to ring.** A pair ringing visibly needs Im λ comparable to |Re λ|.
  Class 1's rest is briefly complex (35.6–38.6 µA/cm²), but it decays ~4–5× faster than it
  turns, so a kick shows no undershoot. That keeps "class 1 has no focus" (slide 5, slide 9)
  true in the sense the deck means: there is no visible ringing. The videos should show this
  honestly rather than hide it.

## Where these videos sit in the talk

- **Slide 5** (two geometries of spike initiation) shows s05_vid1 (the SNIC crawl) and s05_vid2
  (the Hopf whirlpool). Its "If asked" line says the spiralling rate is Im λ, but no picture
  shows λ. s05_vid3 (two planes) and s05_vid4 (traces) would be that picture: optional
  back-pocket or backup-slide material, or a replacement for one of the 5c boxes.
- **Slide 9** (MPOs, f_min and θ are one geometry) shows s09_vid1 (spiral vs ghost) and s09_vid2
  (frequency is geometry, where an MPO readout = |Im λ| rises with the shunt). s09_vid3 (phasor)
  explains *why* the readout is Im λ: the ringing is the shadow of a spinning, shrinking arrow.
- The deck's style rule for s05/s09 was "no equations or eigenvalues on screen". These three
  are the deliberate exception, so they belong where the speaker wants the math (backup, Q&A,
  or a build the speaker chooses).

## Likely audience questions

- *"Why 100 Hz and not θ?"* The fast K⁺ spiral in the (V, w) plane rings near 100 Hz in this
  model. The paper gets θ-range MPOs from slow I_M in the V–z plane (slide 11). Never label the
  ringing here as θ.
- *"The class 1 eigenvalues were complex for a moment. Isn't that a focus?"* Technically yes,
  but it is so overdamped (0.035 cycles per e-fold) that no ringing is observable. What matters
  is Im λ at the crossing, and that is 0. As phasors (s09_vid3), its arrows turn
  about 13° per e-fold at I = 38.0, which is too slow to ring.
- *"Where did the saddle come from?"* It is born together with an unstable node at
  I = 37.68, also at λ = 0. Fixed points are born and die at λ = 0. The videos start at
  38.0 and skip it: the λ = 0 eigenvalue at birth is the unstable node's (at −31.5 mV),
  and the saddle's other λ starts at +1.0.
- *"Is the Hopf supercritical?"* No, it is subcritical: large-amplitude spiking already exists
  just below I_Hopf (113.14–114.24), so the minimum rate f_min ≈ 80 < 104 Hz (paper Fig. 5B,
  Δf).
