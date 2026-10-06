# Model — "Decay vs ring"

Sources: the paper's Methods (Eqs. 1–6) as summarised in the deck spec (slide 2 "If asked");
deck spec slide 3; deck model module. Read 2026-09-30. Every number below was recomputed on
2026-09-30 with `prescott2008.py`. The scratch scripts ran `P.simulate(..., max_step=0.02)`.

## 1. Model and parameter sets

Modified Morris–Lecar (V mV, t ms, C 2 µF/cm², g mS/cm², I µA/cm²; outward +):

    C dV/dt = I_stim − ḡ_Na m∞(V)(V − 50) − ḡ_K,dr w (V + 100) − g_shunt (V + 70)
    dw/dt   = φ_w (w∞(V) − w)/τ_w(V),   τ_w = 1/cosh((V − β_w)/(2γ_w))
    m∞, w∞  = ½[1 + tanh((V − β)/γ)]

ḡ_Na = ḡ_K,dr = 20, φ_w 0.25, β_m −1.2, γ_m 18, β_w −9, γ_w 10. There is no adaptation
(g_adapt = 0), so the model is exactly 2-D.
- **`P.CONTROL`** (g_shunt 2) = class 1, SNIC.
- **`P.SHUNT`** (g_shunt 4) = class 2, Hopf.

`P.simulate` integrates the 3-D system, but z has no effect when g_adapt = 0. Keep z at its value
from `P.rest_state` and ignore it.

## 2. Part 1 (cartoon, pure numpy — no model)

- Class 1 rung: z(t) = e^{λt}, with λ ∈ {−20, −5, −1, −0.2} s⁻¹ and windows 0.6, 1.2, 3.0, 3.0 s.
  At the end of its window, the −0.2 rung is still at e^{−0.6} = 0.55.
- Rotation: θ(t) = ∫ 2π f(t) dt, with f ramping 2 → 8 → 2 Hz smoothly (e.g. a raised cosine)
  over 6 s of model time. z = e^{iθ}, radius 1.
- Class 2 rungs: z(t) = e^{σt} e^{iωt}, ω = 2π·5 = 31.4 s⁻¹, σ ∈ {−1, −5, −20}, windows 3.0,
  1.0, 0.5 s. Per-cycle factors e^{2πσ/ω}: 0.819, 0.368, 0.018.
- Kick: z ← z + 1, drawn from the current point.

## 3. Bifurcation currents and fixed points (Parts 2–3)

| | I_bif (µA/cm²) | pA (×3) | type at I_bif | V* |
|---|---|---|---|---|
| CONTROL | **38.741** | 116.2 | SN (real λ; SNIC) | −38.34 |
| SHUNT | **114.236** | 342.7 | Hopf (λ = ±652i) | −31.72 |

Rest at I = 0: CONTROL V −69.39 (λ −938, −2566); SHUNT V −69.70 (λ −1941, −2606). Both are
nodes.

Class 1 staircase (`P.fixed_points(P.CONTROL, s·I_bif)`; stable point, λ in s⁻¹):

| s | V* | λ | kind |
|---|---|---|---|
| 0.25 | −64.11 | −895.0, −1972.3 | stable node |
| 0.5 | −58.47 | −820.0, −1484.2 | stable node |
| 0.75 | −51.95 | −685.7, −1036.3 | stable node |
| 0.9 | −46.76 | −564.1, −676.2 | stable node |
| (0.93) | −45.37 | −549.5 ± 42.1i | focus — do not use |
| (0.95) | −44.28 | −491.5 ± 68.7i | focus — do not use |
| (0.999) | −39.21 | −112.3, −239.0 | node again |

Class 2 staircase (`P.fixed_points(P.SHUNT, s·I_bif)`):

| s | V* | λ | ring | ×/cycle |
|---|---|---|---|---|
| 0.75 | −45.23 | −1111.3, −973.3 | — | — |
| 0.9 | −37.96 | −583.1 ± 459.0i | 73.1 Hz | 3.4·10⁻⁴ |
| 0.97 | −33.57 | −195.7 ± 611.6i | 97.3 Hz | 0.134 |
| 0.99 | −32.32 | −65.1 ± 641.1i | 102.0 Hz | 0.528 |
| 1.002 | −31.62 (unstable) | +12.9 ± 654.2i | 104 Hz | growing |
| (1.02, spec) | −30.64 | +125.4 ± 667.5i | 106 Hz | ×3.25 |

Staircase responses (each step from the previous step's end state, 50 ms):
- CONTROL: overshoot −0.000 mV at every step. It ends within 10⁻⁴ mV of V*.
- SHUNT first overshoot above V*: 0.75× 0.02 mV · 0.9× 0.40 · 0.97× **2.79** · 0.99× **1.87** mV.
  - w ranges over 0.0030–0.0101 (0.97×) and 0.0073–0.0116 (0.99×): inside the 0–0.015 window.

## 4. Onset runs and the zoom-out windows

- **Class 1:** from the 0.9× fixed point, step to 1.0005 × I_bif, 300 ms. Spikes at 82.3, 170.3
  and 258.3 ms (ISI 88 ms ≈ 11.4 Hz).
  - Reference (continuous f–I): 1.002× → 20.7 Hz, 1.005× → 30.1 Hz.
  - Extent: V −73.3 … 24.8, w 0.0005 … 0.316 → **zoom window ≈ V −78 … +30, w 0 … 0.33** (+5%).
- **Class 2:** from the 0.99× fixed point, step to 1.002 × I_bif, 120 ms. It spirals out for about
  6 cycles (pre-spike peaks −30.1, −29.8, −29.4, −28.8, −27.9, −22.1 mV). The first spike is at
  64.2 ms, then an ISI of 9.34 ms (107 Hz).
  - Extent: V −64.4 … 19.1, w 0.0057 … 0.279 → **zoom window ≈ V −69 … +24, w 0 … 0.30**.
- Why not the spec's 1.02×: from the 0.99× state the first spike comes at 3.4 ms, with no
  visible spiral (0 pre-spike peaks). Onset rate at 1.02× is 122 Hz.

## 5. Recipes (precompute and cache)

```python
from dataclasses import replace
import numpy as np
Ib = P.find_I_bif(p)
def staircase(levels, hold=50.0):          # levels: fractions of I_bif; returns I_func(t)
    def I(t):
        k = min(int(t // hold), len(levels) - 1)
        return levels[k] * Ib
    return I
t, V, w, z = P.simulate(p, 0.0, t_ms=len(levels) * 50.0, y0=P.rest_state(p, 0.0),
                        I_func=staircase(levels), max_step=0.02,
                        t_eval=np.arange(0, len(levels) * 50.0, 0.05))
```

- Run the final onset step as a separate `P.simulate` from the end state of the 0.9× (class 1)
  or 0.99× (class 2) step, with a constant I_stim.
- Sample on a uniform `t_eval` grid (0.05 ms) so the animation can index by model time. At ×1/40
  and 60 fps, one frame is 0.417 ms of model time.
- Cache all runs with `P.npz_cache("<topic>/cache/<name>.npz", fn, levels=..., max_step=0.02)`.
- For nullclines: `P.V_nullcline_w(V, p, I)` (z = 0) and `P.w_nullcline(V, p)`. Clip to the
  window: the V-nullcline blows up near V = E_K and goes negative for low V.

## 6. Part 3 — pulse pairs

```python
def trial(p, I0, amps, times, T):
    y0 = P.rest_state(p, I0)
    I = lambda t: I0 + sum(a for a, t0 in zip(amps, times) if t0 <= t < t0 + 0.5)
    t, V, w, z = P.simulate(p, I0, t_ms=T, y0=y0, I_func=I, max_step=0.02)
    return (V > 0).any(), t, V, w
```

- I₀: CONTROL 0.9·38.741 = **34.87**; SHUNT 0.99·114.236 = **113.09** µA/cm².
- A₁ is found by bisection on `trial(p, I0, [A], [10], 50)[0]` over [0, 200], 30 iterations:
  **CONTROL 48.01, SHUNT 12.52**. A pair uses 0.75·A₁ (36.0 / 9.39) at t = 10 and 10 + Δt, with a
  trial length of Δt + 40 (or + 50) ms.
- Fired vs Δt = 1 … 20 ms (Y = spike):
  - CONTROL `YYY.................`
  - SHUNT `YY.....YYYY.......YY`
- Displayed trials: Δt 2 → ✓✓ · 5 → ✗✗ · 10 → ✗✓ · 20 → ✗✓.
- Ring period: after one 0.75·A₁ pulse (SHUNT), V peaks at t = 11.81, 21.47, 31.15, 40.87 ms →
  **T ≈ 9.7 ms**. Put the bracket between the first two peaks.
- Kick sizes: ΔV = A·0.5/C → CONTROL 9.0 mV, SHUNT 2.35 mV per pulse.

## 7. Asserts for `main.py __main__` (print each value)

- `find_I_bif(CONTROL)` = 38.74 ± 0.01; `find_I_bif(SHUNT)` = 114.24 ± 0.01.
- The staircase λ tables above hold within 2%, and the kind is "stable node" at each class 1
  step.
- Class 1 max overshoot ≤ 0.01 mV. Class 2 first overshoot ≥ 1 mV at 0.97× and 0.99×.
- Onset: class 1 rate < 15 Hz; class 2 rate > 100 Hz, with ≥ 3 pre-spike peaks (a visible
  spiral).
- A₁ within 2% of 48.0 / 12.5, and the grid pattern for Δt ∈ {2, 5, 10, 20} as above.
- Ring period 9.7 ± 0.3 ms.
- Frames per cycle ≥ 12 for every displayed oscillation: (60 × slow-down factor) / f_model.
