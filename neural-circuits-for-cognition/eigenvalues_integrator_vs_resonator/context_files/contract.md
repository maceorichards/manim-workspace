# Video contract — "Decay vs ring: from eigenvalues to the phase plane"

Sources: deck spec, slide 3 (takeaway, content, video visuals, Say, If asked) and Video
production notes. Read 2026-09-30. Every model number was re-verified on 2026-09-30
(`model.md`). Where this contract departs from the deck spec, it says so and gives the reason.

## 1. Header

| | |
|---|---|
| Scene classes | `EigenvalueDecayVsRing` (Part 1), `PhasePlaneCurrentSteps` (Part 2), `PulsePairIntegratorVsResonator` (Part 3), all in `main.py` |
| Output | Render the three parts, then concatenate them losslessly with ffmpeg's concat demuxer (`-c copy`; same resolution and fps) → `videos/eigenvalues_integrator_vs_resonator.mp4`. End frame `videos/eigenvalues_integrator_vs_resonator_end.png`, the last frame of Part 3. |
| Format | 1920 × 1080, **60 fps**, **~100 s** in total (Part 1 ≈ 34 s, Part 2 ≈ 44 s, Part 3 ≈ 22 s), silent |
| Place | The deck's third background slide. The video carries the whole slide, and its end frame is the slide's still. |

The video is split into three scenes only so it is quicker to iterate on. Parts 1 and 2 end on
fades, and Part 3 opens on a new layout, so the cuts are clean. Keep the shared style (badge,
chip and caption positions) identical across the parts, and define shared builders at module
level.

## 2. Purpose

- Make "λ real vs complex" visible: decay vs ring.
- Show that injected current moves the fixed point.
- Show class 1 sliding and creeping versus class 2 ringing and jumping.
- End with the pulse-pair test that defines integrator vs resonator.

## 3. Must / must not

Must:
- This is **the only video in the deck with a rotating point in a complex plane**. The
  sinusoids/spectra video deliberately avoids one. Part 1 is that plane.
- Part 1 carries the footnote "cartoon of the linearized dynamics · units schematic".
- Parts 2 and 3 use the paper's model (`prescott2008.py`: `P.CONTROL` = class 1, `P.SHUNT` =
  class 2, both with g_adapt = 0, so the (V, w) reduction is exact).
- **Every slowed segment carries a speed badge** in a fixed top-right position ("×½", "×1/40",
  "×1/10", "×1/25").
- The λ chip values come from `P.fixed_points(p, I)[i]["eig"] × 1000` (the 2-D eigenvalues, s⁻¹).

Must not:
- **Class 1 steps between ~0.93 and 0.999 × I_bif.** There the stable point is a very heavily
  damped focus (e.g. −491 ± 69i s⁻¹ at 0.95×). No ringing is visible, but the chip would show a
  complex λ and contradict Part 1. (It is already a focus at 0.93×; 0.9× is a node.)
- Noise. Each current step is itself the kick.
- Axes that change within a view. The only allowed change is the one planned 1-s zoom-out per
  class, when spiking starts. Its window is computed once, beforehand.

## 4. Colours

Class 1 elements `P.CLASS1`, class 2 elements `P.CLASS2`. Kicks and flashes `P.HIGHLIGHT`.
V-nullcline `P.V_NULL`, w-nullcline `P.W_NULL`. Voltage traces `P.VOLT`, current traces `P.INK`
(white; use a thinner stroke, or `MUTED`, if it competes with V). Chips on `P.CHIP_FILL`. The
state point is `P.STATE_DOT` with a fading tail. The projector line is `P.MUTED`, dashed.

## 5. Part 1 — the λ planes (`EigenvalueDecayVsRing`, video 0–34 s)

A schematic linear system, not the neuron model.

**Layout**
- **Left: a square "complex plane" panel**, ~800×800 px ≈ 5.9 × 5.9 units (e.g. centred at
  x ≈ −3.6, y ≈ −0.3). Horizontal axis "Im", vertical axis "Re = δV (what the electrode sees)",
  both −1.2 … 1.2. The origin is marked "rest (fixed point)". **Note the orientation: Re is
  vertical**, so it lines up with the trace.
- **Right: a "δV vs time" panel**, ~1000×800 px ≈ 7.4 × 5.9 units. Its vertical axis matches the
  left panel's (same −1.2 … 1.2, the **same pixel scale and aligned rows**). x "time (s)", whose
  range changes per rung (see below), with a short axis rebuild between rungs.
- A **dashed horizontal projector line** (`MUTED`) runs from the moving point to the trace's tip,
  so the audience sees that the electrode records only the vertical shadow of the motion.
- Top-right: two horizontal slider bars with numeric readouts, "Re λ = … s⁻¹" and
  "Im λ = … s⁻¹ (… Hz)".
- Top-left: the segment header, "Class 1 (integrator)" / "Class 2 (resonator)".
- Captions go in a bottom band. The footnote sits small in a corner, `MUTED`.

**Math**
- The state is a complex number z. The point is drawn at (Im z, Re z), and the trace plots Re z.
- Class 1: z stays real, z(t) = z₀e^{λt}. The point moves only along the vertical axis.
- Class 2: z(t) = z₀ e^{σt} e^{iθ(t)} with θ(t) = ∫ω dt. **Integrate the phase**, because ω
  varies in the rotation beat.
- **Kick:** z ← z + 1, a vertical jump of +1 ("1 mV"), marked with a short `HIGHLIGHT` arrow
  labelled "kick (brief current pulse)". The trace restarts at t = 0 after every kick, with no
  ghost of the previous rung.

**Timeline**
- **0–2 s:** the axes appear; header "Class 1 (integrator)".
- **2–10 s, class 1 kick → decay ladder at 1× playback.**
  - Real λ steps −20 → −5 → −1 → −0.2 s⁻¹, one kick per rung.
  - The time windows per rung are 0.6, 1.2, 3.0 and 3.0 s. That is 7.8 s in all; fit the axis
    rebuilds into the remaining 0.2 s, or overlap them with the kick.
  - A dashed envelope e^{λt} is drawn on the trace.
  - Caption on the first three rungs: "Real λ: straight back to rest, no overshoot. |λ| sets how
    fast."
  - Caption on the −0.2 rung, which barely returns in 3 s: "λ → 0: the return takes forever
    (critical slowing) — why class 1 can fire arbitrarily slowly."
- **10–11 s:** the header changes to "Class 2 (resonator)". Playback switches to **0.5×** (badge
  "×½").
- **11–23 s, pure rotation at Re λ = 0.**
  - Start at z = 1. Im λ/2π ramps 2 → 8 → 2 Hz smoothly over 6 s of model time (12 s of video).
  - The circle has radius 1. The trace is a sinusoid whose frequency visibly changes. The trace
    window scrolls, or holds the last ~1.5 s of model time; choose one and keep it.
  - Caption: "Im λ sets how fast it rotates → the ring frequency."
  - Small note: "Re λ = 0 exactly: the idealized edge."
- **23–32 s, kick → decay ladder at fixed Im λ = 2π·5 Hz (31.4 s⁻¹), 0.5× playback.**
  - Re λ steps −1 → −5 → −20 s⁻¹, with one kick of the same size per rung.
  - Model windows: 3.0, 1.0 and 0.5 s (9 s of video at 0.5×).
  - A dashed envelope ±e^{Re λ·t} is drawn on the trace.
  - Per-cycle amplitude factors: ×0.82 (~10 visible cycles), ×0.37 (2–3 cycles), ×0.02 (a single
    swing).
  - Caption: "Re λ sets how fast the ring dies."
- **32–34 s:** fade out Part 1. Caption: "Now the real model — voltage now runs left → right."
  The phase plane's V axis is horizontal, the opposite of Part 1's vertical δV axis, and this
  caption warns about the swap.

## 6. Part 2 — the V–w phase plane (`PhasePlaneCurrentSteps`, video 34–78 s ≈ 44 s)

**Layout**
- **Left ~55%, "phase plane"**: x "V (mV)", y "w (K⁺ activation)".
  - Subthreshold zoom: V −70 … −25 mV, w 0 … 0.015.
  - When spiking starts, zoom out over 1 s of video to the class's limit-cycle window
    (precomputed, +5% margin; `model.md` §4): class 1 ≈ V −78 … +30, w 0 … 0.33; class 2 ≈
    V −69 … +24, w 0 … 0.30.
  - The V-nullcline `P.V_nullcline_w(V, p, I)` is labelled "V-nullcline: dV/dt = 0". The
    w-nullcline `P.w_nullcline(V, p)` is labelled "w-nullcline: dw/dt = 0". Clip both to the
    view.
  - Fixed points from `P.fixed_points(p, I)`: a filled circle if stable, an open circle if
    unstable or a saddle.
  - The trajectory is a moving dot with a fading tail covering the last 30 ms of model time.
- **Top-right, "V(t)"**: y "V (mV)" fixed per class (class 1 −75 … +30, class 2 −75 … +25),
  x "time (ms)" scrolling.
- **Bottom-right, "injected current"**: y "I_stim (µA/cm²)", with a secondary tick label in pA
  (×3; the model cell is ~300 µm²). It shows the staircase.
- **λ chip**, top-left of the phase plane: "λ = … s⁻¹". When λ is complex, add "ring ≈ … Hz,
  ×… per cycle", using |Im λ|/2π and exp(2π·Re λ/|Im λ|) (`P.ring_hz`, `P.per_cycle_factor`).
- **Speed badge**, top-right (e.g. "×1/40").

**Bifurcation currents** (`P.find_I_bif`): CONTROL **38.74 µA/cm²** (≈ 116 pA), SHUNT
**114.24 µA/cm²** (≈ 343 pA).

**Integration.** Use `P.simulate(p, I_stim, y0=..., I_func=staircase, max_step=0.02)` with a
deterministic step function. Start at the stable fixed point for I = 0 (`P.rest_state(p, 0)`).
Precompute everything and cache it (`model.md` §5).

**Step 1 — nullclines only (34–40 s), CONTROL.**
- I sweeps 0 → 0.9·I_bif over 4 s. The V-nullcline rises and the stable fixed-point dot slides
  along it; there is no trajectory yet.
- Caption: "Injected current lifts the V-nullcline → the fixed point (where they cross) moves."
- Then reset to I = 0 (≈ 1 s).

**Step 2 — class 1 staircase (40–58 s).**
- Steps at **0.25, 0.5, 0.75, 0.9 × I_bif**, each held for 50 ms of model time at ×1/40 (2 s of
  video each). The trajectory slides monotonically to each new fixed point with no overshoot.
  Chip values:

  | step | V* (mV) | λ (s⁻¹) |
  |---|---|---|
  | 0.25× | −64.11 | −895, −1972 |
  | 0.5× | −58.47 | −820, −1484 |
  | 0.75× | −51.95 | −686, −1036 |
  | 0.9× | −46.76 | −564, −676 |

- **Final step to 1.0005 × I_bif.**
  - First freeze the trajectory, and animate the V-nullcline rising from 0.9 to 1.0005 × I_bif
    over 1 s of video. A saddle (open circle) appears near the node; the two merge at I_bif and
    both vanish.
  - During this interpolation the chip shows text instead of numbers: "node + saddle merge →
    λ → 0 (saddle-node)".
  - Resume integration at **×1/10** for 300 ms of model time (3 s of video), zooming out when the
    first spike starts.
  - Expected: spikes at t ≈ 82, 170 and 258 ms after the step (≈ 11.4 Hz, ISI ≈ 88 ms), each
    preceded by a long slow ramp as the trajectory crawls past the ghost.
  - Put a soft halo around the ghost region (near V ≈ −38 mV, w ≈ 0.003: the vanished saddle-node) labelled "ghost of the
    fixed point: slow passage → long ISI".
  - The chip reads "no fixed point — saddle-node passed".
- Caption: "Class 1: slides straight to each new rest; at threshold it crawls past the ghost →
  fires arbitrarily slowly."

**Step 3 — class 2 staircase (58–78 s).**
- Fade the class 1 trajectory and its traces. Redraw the nullclines for SHUNT, zoom back to the
  subthreshold window, and restart from SHUNT's I = 0 rest.
- Steps at **0.75, 0.9, 0.97, 0.99 × I_bif**, each held 50 ms at ×1/40 (100-Hz ringing shows at
  2.5 Hz, ~24 frames per cycle):

  | step | V* | λ (s⁻¹) | chip extra | first overshoot |
  |---|---|---|---|---|
  | 0.75× | −45.23 | node −1111, −973 | — | 0.02 mV |
  | 0.9× | −37.96 | −583 ± 459i | 73 Hz, ×3·10⁻⁴ per cycle (not visibly ringing) | 0.4 mV |
  | 0.97× | −33.57 | −196 ± 612i | 97 Hz, ×0.13 per cycle | **2.8 mV**, 1–2 visible overshoots |
  | 0.99× | −32.32 | −65 ± 641i | 102 Hz, ×0.53 per cycle | **1.9 mV**, ~5 visible cycles |

- **Final step to 1.002 × I_bif.** *This deviates from the deck spec, which asked for 1.02×.*
  From the 0.99× state, a 1.02× step fires within 3.4 ms, about 4 frames, so the "spiral opens"
  is never seen. At 1.002× the spiral visibly opens over ~6 growing cycles (first spike at
  64 ms) and then fires at once at ~107 Hz.
  - Chip: "Re λ = +13 s⁻¹ > 0: unstable — the spiral opens" (λ ≈ +12.9 ± 654i).
  - The trajectory spirals outward, the view zooms out when the first spike starts, and it jumps
    onto the large limit cycle.
  - Playback **×1/25** for 120 ms of model time (3.0 s of video). The spec said ×1/20, but 107 Hz
    at ×1/20 is only 11 frames per cycle; ×1/25 gives 14. Trim the model window if Part 2 runs
    long, but keep ≥ 3 spikes after the spiral.
  - The firing rate is ≈ 107 Hz (ISI 9.34 ms) immediately, with no slow onset.
- Caption: "Class 2: rings around each new rest; at threshold the spiral opens → fires fast at
  once (f_min > 0)." Set it with `tex` so f_min gets its subscript.

## 7. Part 3 — the pulse-pair test (`PulsePairIntegratorVsResonator`, video 78–100 s)

**Layout.** Two columns, headed "Class 1 (integrator)" (left, `CLASS1`) and "Class 2
(resonator)" (right, `CLASS2`). Each column holds, from top to bottom:
- a small phase plane (~480 px ≈ 3.5 units tall; the same axes as the Part 2 subthreshold zoom,
  V −70…−25, w 0…0.015; spikes leave the view and are clipped)
- V(t) (~250 px ≈ 1.85 units)
- I_stim(t) (~150 px ≈ 1.1 units)

The speed badge "×1/25" is top-right. The spec said ×1/20, but the ~103-Hz ring would then show only 11.6 frames per cycle. Captions go in a bottom band, or across the top, above the
columns.

**Protocol.**
- CONTROL is held at I₀ = 0.9·I_bif = **34.87 µA/cm²**, SHUNT at I₀ = 0.99·I_bif =
  **113.09 µA/cm²**. Each starts at its stable fixed point.
- Pulses are 0.5 ms long. Each class's single-pulse threshold A₁ (bisection; spike = V crosses
  0 mV within 40 ms) is **CONTROL 48.0, SHUNT 12.5 µA/cm²**.
- Each pulse of a pair is **0.75 × A₁** (the class's own), so neither pulse alone fires.
- Pulse 1 is at trial t = 10 ms and pulse 2 at 10 + Δt. The trial lasts Δt + 40 ms.

**Trials, both columns simultaneously:** Δt = 2, 5, 10, 20 ms.
- At ×1/25, a trial plays in 1.05–1.5 s. Pad each to ~3.5–4 s of video with a short hold that
  stamps ✓ (fired, `CLASS` colour) or ✗ (`MUTED`) in the column, then a reset.
- Mark the ring period (**≈ 9.7 ms**) on the class 2 V(t) trace with a bracket. It is measured
  from the post-pulse peaks of a single subthreshold pulse (`model.md` §6).

**Expected outcomes (verified).**
- CONTROL fires only for Δt ≤ 3 ms.
- SHUNT fires at Δt 1–2 and 8–11 ms, fails at 3–7 and 12–18 ms, and fires again at 19–20 ms.
- For the four trials (class 1, class 2): **2 ms ✓ ✓ · 5 ms ✗ ✗ · 10 ms ✗ ✓ · 20 ms ✗ ✓**.
- If recalibration shifts the ring period, keep the four Δt values at ≈ 0.2T, 0.5T, 1.0T and 2.0T.

**Captions.**
- After the Δt = 10 ms trial: "Resonator: fires only when the second kick arrives in rhythm —
  about one ring period later."
- End: a ✓/✗ grid (rows Δt, columns class) over the dimmed columns, with the caption
  "Integrator asks *how close together?* — resonator asks *in rhythm?*". Italicise via `tex`
  `\textit{}`, or with `txt` slant.

## 8. End frame

The ✓/✗ grid over the dimmed columns, with the final caption. Export
`videos/eigenvalues_integrator_vs_resonator_end.png`. Hold ≥ 3 s.

## 9. Acceptance checks (print, then assert, in `__main__`)

- Chip λ values match the tables above within 2%.
- Class 1 never overshoots its fixed point after a subthreshold step (max V − V* ≤ 0.01 mV).
- Class 2 rings visibly at 0.97× and 0.99×: first overshoot ≥ 1 mV in both cases.
- Class 1 onset rate < 15 Hz (11.4). Class 2 onset rate > 100 Hz (107).
- The pulse grid matches 2 ms ✓✓ · 5 ms ✗✗ · 10 ms ✗✓ · 20 ms ✗✓.
- The ring period is 9.7 ± 0.3 ms.
- Part 1: the per-cycle factors are exp(2π·σ/31.4) = 0.82, 0.37, 0.018 for σ = −1, −5, −20.
- No displayed oscillation has fewer than 12 frames per cycle at 60 fps. Check it from each
  segment's frequency × slow-down.
