# Model — "Class 1: rest vanishes, the ball crawls"

Everything on screen comes from the paper's model with CONTROL parameters, reduced to the
(V, w) plane (exact here, since g_M = 0). No schematic curves.

## The paper's model (modified Morris–Lecar)

Source: paper Methods, Eqs. 1–6 and parameter paragraph; deck model module; deck build contract §6.
Read 2026-09-29. Every parameter below was checked against the paper's Methods text and matches.

Units: V in mV, t in ms, C in µF/cm², g in mS/cm², I in µA/cm². The paper converts current by
treating the cell as 300 µm²: I (pA) ≈ 3 × I (µA/cm²).

```
C dV/dt = I_stim + I_noise − g_Na·m∞(V)·(V − E_Na) − g_Kdr·w·(V − E_K)
                          − g_shunt·(V − E_shunt) − g_M·z·(V − E_K)
dw/dt   = φ_w·(w∞(V) − w)/τ_w(V)
dz/dt   = (z∞(V) − z)/τ_z
m∞(V) = ½[1 + tanh((V − β_m)/γ_m)]       w∞(V) = ½[1 + tanh((V − β_w)/γ_w)]
τ_w(V) = 1/cosh((V − β_w)/(2γ_w))        z∞(V) = 1/(1 + exp((β_z − V)/γ_z))
```

| Parameter | Value | Parameter | Value |
|---|---|---|---|
| C | 2 µF/cm² | φ_w | 0.25 |
| E_Na | +50 mV | β_m, γ_m | −1.2 mV, 18 mV |
| E_K | −100 mV | β_w, γ_w | −9 mV, 10 mV |
| E_shunt | −70 mV | g_M (I_M) | 0 or 2 mS/cm² |
| g_Na | 20 mS/cm² | β_z, γ_z | −30 mV, 5 mV |
| g_Kdr | 20 mS/cm² | τ_z | 200 ms |
| g_shunt | 2 (low-conductance) or 4 (high) | | |

Parameter sets: **CONTROL** g_shunt = 2, g_M = 0 (class 1, SNIC). **SHUNT** g_shunt = 4, g_M = 0
(class 2, subcritical Hopf). **ADAPT** g_shunt = 2, g_M = 2 (class 2). With g_M = 0 the z equation
does not feed back, so CONTROL and SHUNT are exactly two-dimensional (V, w). For ADAPT the paper
freezes z at its steady-state value z∞(V*) and analyses the (V, w) plane ("z treated as a
parameter", paper Methods).

**Noise (paper Methods):** Ornstein–Uhlenbeck current, dI_noise/dt = −I_noise/τ_noise + σ·N(0,1),
σ = 0.1 µA/cm², τ_noise = 5 ms, stationary variance σ²τ/2 (SD 0.158 µA/cm²). Described as weak
on purpose: just enough to knock the model off its fixed point.

**Geometry.** V-nullcline (dV/dt = 0): `w = (I − I_Na(V) − I_shunt(V) − I_M(V,z)) / (g_Kdr (V − E_K))`,
N-shaped (only its lower knee and middle branch matter here). w-nullcline: `w = w∞(V)`, a rising
sigmoid. Fixed points: roots of `I − I_ss(V) = 0` with w = w∞(V) (steady-state I–V). Type from
the eigenvalues λ of the 2×2 Jacobian (central differences, h = 1e-5): complex with Re < 0 →
stable focus; real, both < 0 → stable node; real, opposite signs → saddle. λ is in 1/ms, so the
spiral frequency is **f = |Im λ|/(2π) × 1000 Hz** and the e-fold decay time is −1/Re λ ms.

### Reference implementation (self-contained; reproduces the deck module bit-for-bit)

Verified 2026-09-29: this code gives exactly the same fixed points, eigenvalues and noisy traces
(max difference 0.0 for the seeds used here) as the deck model module.

```python
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
BASE = dict(C=2.0, ENa=50.0, EK=-100.0, Esh=-70.0, gNa=20.0, gK=20.0, gsh=2.0, phi=0.25,
            bm=-1.2, gm=18.0, bw=-9.0, gw=10.0, gM=0.0, bz=-30.0, gz=5.0)
CONTROL = dict(BASE); SHUNT = dict(BASE, gsh=4.0); ADAPT = dict(BASE, gM=2.0)
minf = lambda V, p: 0.5 * (1 + np.tanh((V - p['bm']) / p['gm']))
winf = lambda V, p: 0.5 * (1 + np.tanh((V - p['bw']) / p['gw']))
tauw = lambda V, p: 1 / np.cosh((V - p['bw']) / (2 * p['gw']))
zinf = lambda V, p: 1 / (1 + np.exp((p['bz'] - V) / p['gz']))
def I_fixed(V, p, z):          # every current except the w-gated K+ current
    return p['gNa']*minf(V, p)*(V - p['ENa']) + p['gsh']*(V - p['Esh']) + p['gM']*z*(V - p['EK'])
def f2(V, w, I, p, z=0.0):     # reduced (V, w) system, z frozen; keep this summation order
    Iion = (p['gNa']*minf(V, p)*(V - p['ENa']) + p['gK']*w*(V - p['EK'])
            + p['gsh']*(V - p['Esh']) + p['gM']*z*(V - p['EK']))
    return (I - Iion) / p['C'], p['phi'] * (winf(V, p) - w) / tauw(V, p)
def V_null(V, I, p, z=0.0):
    return (I - I_fixed(V, p, z)) / (p['gK'] * (V - p['EK']))
def fixed_points(I, p, z=0.0, zss=False):   # zss=True: z = z∞(V*) (ADAPT, 2-D Jacobian)
    g = lambda V: I - (I_fixed(V, p, zinf(V, p) if zss else z) + p['gK']*winf(V, p)*(V - p['EK']))
    Vs = np.linspace(-90, 20, 4000); gv = g(Vs); out = []
    for i in np.where(np.sign(gv[:-1]) != np.sign(gv[1:]))[0]:
        V0 = brentq(g, Vs[i], Vs[i+1]); w0 = winf(V0, p); zz = zinf(V0, p) if zss else z; h = 1e-5
        J = np.column_stack([(np.array(f2(V0+h, w0, I, p, zz)) - f2(V0-h, w0, I, p, zz)) / (2*h),
                             (np.array(f2(V0, w0+h, I, p, zz)) - f2(V0, w0-h, I, p, zz)) / (2*h)])
        out.append((V0, w0, zz, np.linalg.eigvals(J)))
    return out                  # sorted by V; out[0] is the rest (lowest) fixed point
def run(p, I_of_t, t0, t1, y0):             # deterministic segment
    s = solve_ivp(lambda t, y: f2(y[0], y[1], I_of_t(t), p), (t0, t1), y0,
                  method='LSODA', max_step=0.02, rtol=1e-9, atol=1e-11)
    return s.t, s.y[0], s.y[1]
def noisy(p, I, V0, w0, T, dt=0.02, sigma=0.1, tau=5.0, seed=0):   # Euler–Maruyama + OU
    rng = np.random.default_rng(seed); n = int(T / dt); V, w, In = V0, w0, 0.0
    a = np.exp(-dt / tau); b = sigma * np.sqrt(tau / 2) * np.sqrt(1 - a*a); out = np.empty((n, 3))
    for i in range(n):
        dV, dw = f2(V, w, I + In, p); V += dt*dV; w += dt*dw
        In = a*In + b*rng.standard_normal(); out[i] = (i*dt, V, w)
    return out                  # columns t, V, w (state after step i is stored at t = i*dt)
def spikes(t, V):               # upward crossings of 0 mV
    k = np.where((V[:-1] < 0) & (V[1:] >= 0))[0]; return t[k]
```

Current schedules use cosine ramps: between levels I0 → I1 over [a, b],
`I(t) = I0 + (I1 − I0)·½(1 − cos(π (t − a)/(b − a)))`. An instantaneous "kick" ΔV means: stop
the integration, add ΔV to V, restart (a very brief current pulse).

## Numbers (verified 2026-09-29 with a local copy of the deck model module)

### Saddle-node (SNIC) point, CONTROL
Method: maximise the steady-state I–V curve I_ss(V) (all gates at steady state, g_M = 0) on
V ∈ [−50, −30] (bounded scalar minimisation of −I_ss, xatol 1e-10).
- **I_SN = 38.7409 µA/cm²** (≈ 116 pA), at **V_SN = −38.34 mV, w_SN = 0.00282**. Deck build
  contract §6 says ≈ 38.74: confirmed.
- The saddle (with the unstable third point) is born at the I–V local minimum: I = 37.684 at
  V = −31.62 mV. Between 37.684 and 38.741 there are three fixed points.
- Rest point changes from (overdamped) focus to node at I = 38.634 (discriminant of J = 0, brentq).

### Fixed points at the sub-threshold steps (z = 0; `fixed_points(I, CONTROL)`)

| I | rest V, w | rest λ (1/ms) | saddle V, w | saddle λ | gap | third point |
|---|---|---|---|---|---|---|
| 38.00 | −42.04, 0.00135 | −0.362 ± 0.084i (overdamped) | −33.81, 0.00695 | +0.644, −0.084 | 8.2 mV | unstable node −30.04, 0.0147 |
| 38.50 | −40.47, 0.00184 | −0.263 ± 0.060i (overdamped) | −36.02, 0.00448 | +0.310, −0.158 | 4.5 mV | −29.23, 0.0172 |
| 38.70 | −39.23, 0.00236 | −0.116, −0.239 (node) | −37.42, 0.00339 | +0.119, −0.201 | 1.8 mV | −29.00, 0.0180 |
| 38.74 | −38.48, 0.00274 | −0.017, −0.227 | −38.21, 0.00290 | +0.018, −0.221 | 0.3 mV | −28.96, 0.0181 |

Damping ratio at 38.0 is |Re|/|λ| = 0.97: an overshoot of e^(−πζ/√(1−ζ²)) ≈ 3e−6, i.e. none.

### Firing above I_SN (2-D run from the 38.7 rest point, 6 s, LSODA, max_step 0.05)

| I | ISI (ms) | rate (Hz) | fraction of ISI with −44 < V < −34 mV |
|---|---|---|---|
| 38.745 | 181.8 | 5.50 | 0.94 |
| **38.75** | **124.6** | **8.02** | 0.92 |
| 38.76 | 88.7 | 11.3 | 0.89 |
| 38.80 | 54.1 | 18.5 | 0.81 |
| **39.0** | **29.7** | **33.7** | 0.68 |
| 39.5 | 19.6 | 51.0 | 0.54 |
| 40.0 | 16.1 | 62.0 | 0.48 |

Near onset f ≈ 85·√(I − I_SN) Hz (5.5 Hz at +0.004; deck contract's "6 Hz at +0.005" agrees).
Spiking loop extent: V −73.3 … +24.8 mV, w 0.0005 … 0.316.

### Schedule (the one run that drives the whole video)

Start at the I = 38.0 rest point (V = −42.038, w = 0.001351). Cosine ramps:

| ramp | from → to (µA/cm²) | model t (ms) |
|---|---|---|
| 1 | 38.0 → 38.5 | 40–70 |
| 2 | 38.5 → 38.7 | 100–130 |
| 3 | 38.7 → 38.75 | 160–180 (crosses I_SN at **t = 174.40 ms**) |
| 4 | 38.75 → 39.0 | 560–570 |

Integrate with `run` (LSODA, max_step 0.02, rtol 1e-9, atol 1e-11) from 0 to 690 ms.
Results (assert these, ±0.5 ms): **spikes at 272.0, 396.6, 521.2, 577.5, 607.2, 636.9, 666.6 ms**;
ISIs 124.6, 124.6, 56.3 (transition), 29.7, 29.7, 29.7. During holds the state tracks the rest
point: V = −42.04 (0–40 ms), −40.47…−40.68 (70–100), −39.25…−39.58 (130–160).
Whole-run range: V −73.3 … +24.8 mV, w 0.0005 … 0.3163 (fits the full window).

### Display warp and windows
screen-x = asinh((V + 36)/8), screen-y = w^0.4 (clip w ≥ 0). Map linearly into the panel box.
Knee window V −47 … −31, w 0.0003 … 0.012 (contains rest and saddle for all steps, excludes the
third point). Full window V −78 … +30, w 0 … 0.36. Animate the four window bounds (in screen
coordinates) with a ValueTracker; redraw nullclines, dots and trail through the same map.
The static s05_v1 used linear V and sqrt(w) plus an inset instead; both are monotone maps.

### Suggested asserts for `main.py`
```python
fp = fixed_points(38.0, CONTROL); assert len(fp) == 3 and abs(fp[0][0] + 42.04) < 0.01
assert len(fixed_points(38.75, CONTROL)) == 1          # rest and saddle gone
st = spikes(t, V); assert np.allclose(st, [272.0, 396.6, 521.2, 577.5, 607.2, 636.9, 666.6], atol=0.5)
```
