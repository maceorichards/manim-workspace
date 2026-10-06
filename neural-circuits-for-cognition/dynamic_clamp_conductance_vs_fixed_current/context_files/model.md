# Model — "Dynamic clamp in action"

Sources: paper Methods (Eqs. 1–6, parameter list, noise model, 300-µm² unit conversion,
dynamic-clamp settings); deck model module (same equations; used to cross-check); deck build
contract §6. All numbers computed 2026-09-29 by running the snippet in §4.

## 1. Equations (units: V mV, t ms, C µF/cm², g mS/cm², I µA/cm²)

Paper's modified Morris–Lecar, 2-D (adaptation z omitted, g_adapt = 0):

    C dV/dt = I0 + I_noise(t) + I_inj(t) − g_Na m∞(V)(V − E_Na) − g_Kdr w (V − E_K) − g_shunt (V − E_shunt)
    dw/dt   = φ_w (w∞(V) − w) / τ_w(V)
    m∞ = ½[1 + tanh((V − β_m)/γ_m)],  w∞ = ½[1 + tanh((V − β_w)/γ_w)],  τ_w = 1 / cosh((V − β_w)/(2γ_w))

| Parameter | Value | Note |
|---|---|---|
| C | 2 µF/cm² | |
| E_Na, E_K, E_shunt | +50, −100, −70 mV | |
| g_Na, g_Kdr | 20, 20 mS/cm² | |
| g_shunt | 2 mS/cm² | low-conductance (control) state = the cell's own leak |
| φ_w | 0.25 | |
| β_m, γ_m | −1.2, 18 mV | |
| β_w, γ_w | −9, 10 mV | |

All verified against the paper's Methods text ("unless otherwise stated" defaults); the deck
module matches. The paper's high-conductance state is g_shunt 2 → 4.

Injected current (positive = depolarizing, as the rig injects it):
- **Right, dynamic clamp:** I_inj = −g_dc (V − E_dc), g_dc = 10/3 mS/cm², E_dc = −70 mV.
- **Left, current clamp:** I_inj = OFFSET (constant) = mean of the right column's I_inj over the
  displayed 500 ms = **−58.443 µA/cm²** (computed, not hard-coded; run right first).

Drawn "injected current (outward ↑)" = −I_inj × 3 (pA). Input strip = (I0 + I_noise) × 3 (pA).

## 2. Units and the 10-nS reconciliation

- Paper: model cell area ≈ 300 µm² = 3×10⁻⁶ cm², so I[pA] = 3 × I[µA/cm²] and
  g[nS] = 3 × g[mS/cm²]. Check from paper Fig. 1A: model 71 and 153 µA/cm² ↔ 213 and 459 pA vs
  the experiment's 320 and 480 pA (approximate by design).
- 10 nS → 3.333 mS/cm². The paper's own shunt increment is +2 mS/cm² (≈ 6 nS).
- Model resting slope conductance (CONTROL, V_rest −69.39 mV): 1.8753 mS/cm². R_in drop:
  +2 → 51.6 %; +3.333 → 64.0 %; the measured 56 % would need +2.39 (≈ 7.2 nS).
- Choice: g_dc = 3.333 mS/cm² (label "10 nS" literally true under the paper's conversion).

## 3. Noise and drive

- I0 = 90 µA/cm² (270 pA), both columns.
- I_noise: Ornstein–Uhlenbeck, τ = 5 ms, stationary SD = 12 µA/cm² (36 pA), exact discrete
  update `x[i] = a·x[i−1] + b·ξ[i]`, a = exp(−dt/τ), b = SD·sqrt(1 − a²), x[0] = 0,
  ξ = `np.random.default_rng(1).standard_normal(n)` drawn once for all n = 60000 steps.
  (Paper's convention σ_noise with variance σ²τ/2 ⇒ σ = SD·sqrt(2/τ) = 7.6 µA/cm²·ms^-½; the
  paper used σ = 0.1 for weak MPO noise, so this is ~76× larger, standing in for the in vivo
  barrage.)
- The same `noise` array drives both columns.

## 4. Simulation recipe + verified snippet

Forward Euler, dt = 0.01 ms, 600 ms total; discard the first 100 ms (burn-in); display 500 ms
(50000 samples). Start V = −69.39, w = w∞(V). Spike = upward crossing of 0 mV. Runs in < 1 s.

```python
import numpy as np
C, ENa, EK, Esh = 2.0, 50.0, -100.0, -70.0
gNa, gKdr, gsh, phi = 20.0, 20.0, 2.0, 0.25
bm, gm, bw, gw = -1.2, 18.0, -9.0, 10.0
minf = lambda V: 0.5*(1+np.tanh((V-bm)/gm))
winf = lambda V: 0.5*(1+np.tanh((V-bw)/gw))
tauw = lambda V: 1/np.cosh((V-bw)/(2*gw))
DT, BURN, T = 0.01, 100.0, 500.0
I0, SD, TAU, SEED = 90.0, 12.0, 5.0, 1
G_DC, E_DC = 10/3, -70.0
n = int(round((BURN+T)/DT)); k = int(round(BURN/DT))
rng = np.random.default_rng(SEED)
xi = rng.standard_normal(n); a = np.exp(-DT/TAU); b = SD*np.sqrt(1-a*a)
noise = np.empty(n); noise[0] = 0.0
for i in range(1, n): noise[i] = a*noise[i-1] + b*xi[i]
def sim(g_dc=0.0, offset=0.0):
    V = -69.39; w = float(winf(V)); out = np.empty((n, 2))
    for i in range(n):
        Iinj = offset - g_dc*(V-E_DC)
        Iion = gNa*minf(V)*(V-ENa) + gKdr*w*(V-EK) + gsh*(V-Esh)
        dV = (I0 + noise[i] + Iinj - Iion)/C
        dw = phi*(winf(V)-w)/tauw(V)
        V += DT*dV; w += DT*dw
        out[i] = V, Iinj
    return out[k:, 0], out[k:, 1]
VR, IR = sim(g_dc=G_DC)             # right: dynamic clamp
OFFSET = IR.mean()                  # -58.443 uA/cm2
VL, IL = sim(offset=OFFSET)         # left: constant offset
t = np.arange(len(VL))*DT; inp = I0 + noise[k:]
spikes = lambda V: t[1:][(V[:-1] < 0) & (V[1:] >= 0)]
assert len(spikes(VL)) == 9 and len(spikes(VR)) == 0
assert abs(OFFSET + 58.443) < 0.01
```

## 5. Verified numbers (seed 1)

| Quantity | Left (constant offset) | Right (dynamic clamp) |
|---|---|---|
| Spikes in 500 ms | **9**, at 26.1, 114.8, 162.4, 210.1, 269.6, 297.0, 328.8, 337.5, 449.0 ms | **0** |
| V range | −76.0 to +27.0 mV | −57.9 to −43.9 mV |
| Sub-threshold V (V < −30) mean / SD | −53.6 / 6.63 mV | −52.5 / 2.25 mV |
| Injected current, outward-positive | flat 58.44 µA/cm² = 175.3 pA | 40.3–87.0 µA/cm² (121–261 pA), mean 175.3 pA, SD 7.49 µA/cm² (22 pA) |
| corr(right current, right V) | — | 0.99997 (one-step lag) |

- Input (I0 + noise) over the window: mean 86.7, SD 10.9, range 56.3–130.0 µA/cm²
  (169–390 pA).
- Right-column local V maxima (prominence ≥ 3 mV) include t = 209.2 ms: V −46.7 mV, current
  233 pA (left fires spike 4 at 210.1 ms) → callout moment. The largest, t = 450.6 ms: −43.9 mV,
  261 pA.
- Robustness: dt = 0.005 ms (noise held per 0.01-ms sample) → same 9 / 0 spikes. Seeds 1–6 at
  SD 10–12 and I0 85–90: left 4–10 spikes, right 0 in all 18 runs.
- Alternatives (same seed/SD/I0): g_dc = 2 mS/cm² with matched offset (−152 pA) → 22 vs 3
  spikes, SD 8.4 vs 3.9 mV, sub-threshold means −49.6 vs −45.1 mV. Left offset 0 with
  g_dc = 3.33 → left fires 121 spikes (unusable).

## 6. Drawing recipe

Precompute everything in `construct()`; decimate to every 5th sample (0.05 ms, 10000 points)
for the polylines — spikes (~1 ms wide) still resolve. Drive one ValueTracker `t_ms`
(0 → 500, linear over 10.5 s); each trace is `VMobject().set_points_as_corners(...)` of samples
with t ≤ t_ms (updater), cursors at `x(t_ms)`. Spike counters = count of spike times ≤ t_ms
(`Integer` or rebuilt `txt`). Map values with per-panel linear functions (not `Axes`) for speed.
