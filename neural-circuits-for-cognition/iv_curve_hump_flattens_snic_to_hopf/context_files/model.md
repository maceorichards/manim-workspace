# Model — "The hump unbends"

Sources: paper Methods Eqs. 1–6 and parameter paragraph; paper Fig. 1 legend; deck model module
(the paper's modified Morris–Lecar, outward-positive currents); deck build contract §6; deck
static figure s07_v1 script + status notes. Read 2026-09-28. Every number below was recomputed
on 2026-09-28 with a copy of the deck model module and cross-checked with the standalone code in
§4 (numpy + scipy, as in the repo venv).

## 1. Equations (modified Morris–Lecar; V mV, t ms, C µF/cm², g mS/cm², I µA/cm²)

    C dV/dt = I_stim − g_Na·m∞(V)·(V − E_Na) − g_Kdr·w·(V − E_K)
                     − g_shunt·(V − E_shunt) − g_M·z·(V − E_K)
    dw/dt   = φ_w·(w∞(V) − w)/τ_w(V)
    dz/dt   = (z∞(V) − z)/τ_z
    m∞(V) = ½[1 + tanh((V − β_m)/γ_m)]      w∞(V) = ½[1 + tanh((V − β_w)/γ_w)]
    τ_w(V) = 1/cosh((V − β_w)/(2γ_w))        z∞(V) = 1/(1 + exp((β_z − V)/γ_z))

The shunt term is the model's only leak ("I_leak" in the Fig. 1C legend). Noise is not used.

| Param | Value | Param | Value |
|---|---|---|---|
| C | 2 µF/cm² | φ_w | 0.25 |
| E_Na | +50 mV | β_m, γ_m | −1.2 mV, 18 mV |
| E_K | −100 mV | β_w, γ_w | −9 mV, 10 mV |
| E_shunt | −70 mV | g_M (adaptation) | 0 or 2 mS/cm² |
| g_Na | 20 mS/cm² | β_z, γ_z, τ_z | −30 mV, 5 mV, 200 ms |
| g_Kdr | 20 mS/cm² | g_shunt | 2 (low) → 4 (high conductance) |

All values verified against the paper's Methods text (2026-09-28); the deck module matches.
(The paper's alternative AHP current, g_AHP = 1, β_z = 0, is not used here.)

Parameter sets: CONTROL (g_shunt 2, g_M 0) · SHUNT (4, 0) · ADAPT (2, 2) · SHUNT_ADAPT (4, 2).
The video path is CONTROL → SHUNT (shunt ramp) → SHUNT_ADAPT (g_M ramp).

## 2. What is drawn

- **Steady-state current:** `I_ss(V) = g_Na m∞(V)(V−E_Na) + g_Kdr w∞(V)(V−E_K) + g_shunt(V−E_shunt)
  + g_M z∞(V)(V−E_K)` (all gates at steady state; with z at z∞(V) this reproduces Fig. 1C c/d).
- **Pinned net current:** `net(V) = I_ss(V) − I_ss(V_REF)`, V_REF = **−34.435 mV** = the voltage
  of minimum slope of the control curve. A shunt adds the constant slope Δg, so V_REF stays the
  minimum-slope voltage for every shunt value. Physical meaning: net current when I_stim is set
  to hold the cell at −34.4 mV. For CONTROL, I_ss(V_REF) = 38.148 µA/cm² (the static s07_v1 used
  38.2, nearly the same).
- **Plotted value:** `y = asinh(net / 0.45)` (knee 0.45 µA/cm², as in s07_v1). Fixed y-range
  [asinh(−125/0.45), asinh(180/0.45)] = [−6.32, +6.68]. V grid linspace(−62, −21, 600).
- **Negative-slope band:** between the local max V_max(g) and local min V_min(g) of I_ss, only
  while g_M = 0 and Δg < 0.2395.
- **Class label:** "SNIC · class 1" while Δg < 0.1656 (and g_M = 0); "Hopf · class 2" after.
- **R_in readout:** input conductance at rest (I_stim = 0) is dI_ss/dV at the stable rest point;
  CONTROL 1.8753 mS/cm² (rest −69.39 mV) → R_in drop = 1 − G0/G(Δg) ≈ Δg/(1.8753 + Δg)
  (exact vs approximation differ < 0.1%). g_M does not change it (z∞ ≈ 0 at rest).

## 3. Timeline drivers

Two ValueTrackers: `dg` (added shunt) and `gm`. Piecewise-linear dg: 0→0.1656 over 1.0–4.0 s
(linear), 0.1656→0.2395 over 4.0–4.5 s (linear), 0.2395→2.0 over 4.5–6.5 s (smooth); gm 0→2
over 7.0–9.5 s (smooth). Redraw the curve with `always_redraw` / updaters from the trackers.

## 4. Reference implementation (paste into main.py; verified)

```python
import numpy as np
from scipy.optimize import brentq, minimize_scalar
C, E_NA, E_K, E_SH = 2.0, 50.0, -100.0, -70.0
G_NA, G_KDR, PHI_W = 20.0, 20.0, 0.25
BETA_M, GAMMA_M, BETA_W, GAMMA_W, BETA_Z, GAMMA_Z = -1.2, 18.0, -9.0, 10.0, -30.0, 5.0
V_REF, KNEE = -34.435, 0.45

def m_inf(V): return 0.5 * (1 + np.tanh((V - BETA_M) / GAMMA_M))
def w_inf(V): return 0.5 * (1 + np.tanh((V - BETA_W) / GAMMA_W))
def tau_w(V): return 1 / np.cosh((V - BETA_W) / (2 * GAMMA_W))
def z_inf(V): return 1 / (1 + np.exp((BETA_Z - V) / GAMMA_Z))

def i_ss(V, g_sh=2.0, g_m=0.0):
    return (G_NA * m_inf(V) * (V - E_NA) + G_KDR * w_inf(V) * (V - E_K)
            + g_sh * (V - E_SH) + g_m * z_inf(V) * (V - E_K))

def net(V, g_sh=2.0, g_m=0.0): return i_ss(V, g_sh, g_m) - i_ss(V_REF, g_sh, g_m)
def yplot(i): return np.arcsinh(np.asarray(i) / KNEE)

def hump(g_sh):            # (V_max, V_min) of the negative-slope region, or None (g_M = 0)
    if g_sh >= 2.2395: return None
    a = minimize_scalar(lambda v: -i_ss(v, g_sh), bounds=(-42, V_REF), method="bounded").x
    b = minimize_scalar(lambda v: i_ss(v, g_sh), bounds=(V_REF, -28), method="bounded").x
    return a, b

def _d(f, V, h=1e-5): return (f(V + h) - f(V - h)) / (2 * h)
def slope_ss(V, g_sh): return _d(lambda v: i_ss(v, g_sh), V)
def trace(V, g_sh):        # trace of the 2-D (V, w) Jacobian on the fixed-point branch
    dIinst = _d(lambda v: G_NA * m_inf(v) * (v - E_NA), V) + G_KDR * w_inf(V) + g_sh
    return -dIinst / C - PHI_W / tau_w(V)

def v_star(g_sh):          # threshold = voltage at the bifurcation (g_M = 0): ('SN'|'Hopf', V)
    Vs = np.arange(-70, -20, 0.01)
    for a, b in zip(Vs[:-1], Vs[1:]):
        if slope_ss(b, g_sh) <= 0:
            return "SN", brentq(lambda v: slope_ss(v, g_sh), a, b)
        if trace(b, g_sh) >= 0:
            return "Hopf", brentq(lambda v: trace(v, g_sh), a, b)
```

Why this works: the Jacobian does not depend on I_stim, so the rest branch can be walked in V
(I_stim = I_ss(V)). det > 0 ⇔ dI_ss/dV > 0, so the first V where the slope hits 0 is a
saddle-node (on the invariant circle here → SNIC); the first V where the trace hits 0 (the
paper's condition −(1/C)∂I_inst/∂V = φ_w/τ_w) is a Hopf.

## 5. Verified key numbers (assert these in `main.py`)

| Quantity | Value | Method |
|---|---|---|
| CONTROL hump: local max | −38.343 mV, I_ss 38.741 (net +0.593) | `hump(2.0)` |
| CONTROL hump: local min | −31.624 mV, I_ss 37.684 (net −0.464); depth 1.057 | same |
| CONTROL min slope | −0.2395 mS/cm² at −34.435 mV (V_REF) | minimize dI_ss/dV |
| CONTROL pinned zero crossings | −41.656, −34.435, −29.748 mV | brentq on `net` |
| CONTROL rheobase (saddle-node) | 38.741 µA/cm² at V* = −38.343 (SNIC; 6.1 Hz at +0.005) | `v_star(2.0)`; simulation |
| Negative slope disappears | g_shunt = **2.2395** (Δg 0.2395 ≈ 0.72 nS), at −34.435 mV | 2 + 0.23952 (shunt adds slope) |
| Mechanism switch (SNIC→Hopf) | g_shunt = **2.1656** (Δg 0.1656), V* −36.417, I 44.13 (Bogdanov–Takens: trace = 0 at the fold) | brentq on trace at V_max(g) |
| SHUNT (g 4) | monotonic, min slope +1.760; Hopf at I 114.236, V* −31.725, 103.8 Hz | `v_star(4.0)` |
| SHUNT_ADAPT (4, 2) | monotonic; Hopf (3-D) I 192.62, V* −29.566, 137 Hz | 3-D Jacobian with z |
| g_M alone to unbend (g_sh 2) | g_M = 0.0824 | min slope with z∞(V) |
| R_in drop, Δg 0.1656 / 0.2395 / 2 | −8.1% / −11.4% / −51.7% (cells, 10 nS: −56%) | rest slope |
| Pinned net extremes (V −62, −21) | CONTROL −24.7, +49.6; SHUNT −79.9, +76.5; SHUNT_ADAPT −118.0, +173.8 | `net` |

Hump shrinking along the shunt ramp (g_M = 0):

| Δg | V_max | V_min | net max | net min | depth |
|---|---|---|---|---|---|
| 0.00 | −38.343 | −31.624 | +0.593 | −0.464 | 1.057 |
| 0.05 | −37.828 | −31.899 | +0.410 | −0.330 | 0.740 |
| 0.10 | −37.270 | −32.224 | +0.254 | −0.211 | 0.465 |
| 0.15 | −36.639 | −32.627 | +0.128 | −0.110 | 0.238 |
| 0.1656 | −36.416 | −32.780 | +0.095 | −0.083 | 0.178 |
| 0.20 | −35.844 | −33.199 | +0.037 | −0.033 | 0.070 |
| 0.2395 | −34.435 | −34.435 | 0 | 0 | 0 |

Suggested asserts: `abs(hump(2.0)[0] + 38.343) < 0.01`; `v_star(2.0)[0] == "SN"`;
`v_star(2.2)[0] == "Hopf"`; `hump(2.239) is not None and hump(2.2396) is None`;
`abs(v_star(4.0)[1] + 31.725) < 0.01`; `abs(i_ss(V_REF) - 38.148) < 0.01`.

## 6. Checks done on the class switch (for the record)

- Between Δg 0 and 0.1656 the saddle-node is on the invariant circle: starting from a spike just
  below the fold (−0.05 µA/cm²) the model does not keep firing, and just above it fires slowly
  (6.1 Hz at Δg 0, rising to 21 Hz at Δg 0.16 for +0.005 µA/cm²).
- Just past the switch (Δg 0.18–0.30) onset is at the Hopf with 26–41 Hz; no bistability found
  at −0.1 µA/cm²; at Δg = 2 the model is clearly bistable (still fires 88 Hz at 1 µA/cm² below
  the Hopf), consistent with f_min ≈ 78–80 Hz at the bistable window's
  low edge (113.14 µA/cm²; paper Fig. 4A ~80 spikes/s). The deck build contract's 90–100 Hz is too high.
- Without adaptation the model is exactly 2-D, so the 2-D analysis is exact for the shunt ramp.
