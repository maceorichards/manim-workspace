# Model — "Class 2: the whirlpool lets go"

Everything on screen comes from the paper's model with SHUNT parameters (control + 2 mS/cm²
shunt), exact in the (V, w) plane since g_M = 0. No noise in this video.

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

### Hopf point, SHUNT (g_shunt = 4, g_M = 0)
Method: brentq on max Re λ of the single fixed point over I ∈ [105, 120], xtol 1e-8.
- **I_Hopf = 114.2358 µA/cm²** (≈ 343 pA); V* = −31.725 mV, w* = 0.01051; λ = ±0.6522i /ms →
  **103.8 Hz** at the bifurcation. Single fixed point at every current (monotonic I–V).
- Subcritical: a large limit cycle coexists with the stable focus below the Hopf.

### Bistable window and f_min
Method: start on the spiking cycle at I = 120, step I down (each step starting from the last
state, runs of 0.6–2.5 s), keep the rate of the last ISI; spiking "stops" when no spike occurs.

| I | 120 | 116 | 115 | 114.24 | 114.0 | 113.6 | 113.3 | 113.2 | 113.15 | 113.14 | 113.138 | 113.137 | 113.136 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rate (spikes/s) | 139.4 | 118.8 | 111.7 | 104.9 | 102.2 | 96.8 | 90.6 | 86.8 | 82.6 | 80.1 | 79.0 | 78.0 | stops |

- Lowest current with spiking **≈ 113.137**; **bistable window 113.137 – 114.236** (rest and
  spiking coexist). **f_min ≈ 78–80 spikes/s** (the rate falls steeply at the very end).
- Δf (max ringing frequency − f_min) ≈ 103.8 − 78 ≈ 26 Hz. Paper Fig. 5B: f_min ≈ 77,
  max MPO ≈ 103 Hz; Fig. 4A: shunted f_min 80 spikes/s. Consistent.
- Deck build contract §6's "f_min ≈ 90–100 Hz" is too high (flag).
- Spiking loop: V −64.4 … +20 mV, w 0.0056 … 0.28.

### Focus eigenvalues vs current (why "ringing decays more slowly")

| I | V* | w* | λ (1/ms) | ring f (Hz) | decay τ (ms) | amplitude kept per cycle |
|---|---|---|---|---|---|---|
| 100 | −39.35 | 0.00231 | −0.685 ± 0.399i | 63.5 | 1.5 | ≈ 0 (no visible ring) |
| 105 | −36.82 | 0.00382 | −0.492 ± 0.505i | 80.4 | 2.0 | 0.002 |
| **110** | −34.03 | 0.00666 | −0.241 ± 0.599i | 95.3 | 4.2 | **0.08** |
| 112 | −32.91 | 0.00832 | −0.128 ± 0.628i | 100.0 | 7.8 | 0.28 |
| **112.5** | −32.63 | 0.00878 | −0.099 ± 0.634i | 101.0 | 10.1 | **0.37** |
| 113 | −32.37 | 0.00926 | −0.070 ± 0.640i | 101.9 | 14.2 | 0.50 |
| **114** | −31.84 | 0.01026 | −0.013 ± 0.650i | 103.5 | 75 | **0.88** |
| 114.24 | −31.73 | 0.01051 | 0 ± 0.652i | 103.8 | ∞ | 1 |
| 115 | −31.35 | 0.01133 | +0.043 ± 0.658i (unstable) | 104.8 | grows, e-fold 23 ms | 1.50 |

Per-cycle factor = exp(2π·Re λ/|Im λ|). Kick thresholds (smallest instantaneous +ΔV that fires,
bisection, 300 ms runs): 4.85 (110), 4.21 (111), 3.63 (112), 3.36 (112.5), 3.10 (113),
2.84 (113.5), 2.13 mV (114). Hyperpolarising kicks up to −10 mV never fire at I ≤ 113.

### Schedule (one run drives the video)
Start at the I = 110 focus (V = −34.0253, w = 0.006659). Cosine ramps 110 → 112.5 over 25–45 ms,
112.5 → 114.0 over 80–100 ms, 114.0 → 115.0 over 165–175 ms (passes I_Hopf at **t = 168.23 ms**).
Kicks ΔV = **+1.2 mV at t = 5, 50, 105 ms**. Integrate segment by segment with `run` to 260 ms.

Verified results (assert ±0.5 ms / ±0.05 mV):
- Ringing peaks above the local focus: kick 1 → 1.217, 0.107 mV (10.5 ms later);
  kick 2 → 1.388, 0.531, 0.201 mV (at +0.9, +10.7, +20.5 ms);
  kick 3 → 1.636, 1.464, 1.305 mV (+1.3, +11.0, +20.7 ms). Measured ratios 0.09, 0.38, 0.89 per
  cycle match the eigenvalue prediction (0.08, 0.37, 0.88).
- No spike before 168 ms (margin: the third kick would have to reach 2.2 mV to fire).
- After the Hopf: growing peaks at 174.1 (−29.92), 184.0 (−28.97), 194.6 ms (−25.76 mV);
  **spikes at 203.9, 212.8, 221.8, 230.7, 239.7, 248.6, 257.6 ms**, ISI 8.95 ms (111.7 Hz).
- Ranges: 0–168 ms V −34.42 … −30.21, w 0.0064 … 0.0124; up to 195 ms V ≤ −25.76, w ≤ 0.0225
  (inside the focus window); after 204 ms the loop spans V −64.3 … +19.3, w 0.0059 … 0.280.

### Display
Same warp as class1_snic_onset_slow_crawl: screen-x = asinh((V + 36)/8), screen-y = w^0.4. Focus window V −40 … −24,
w 0.004 … 0.026; full window V −78 … +30, w 0 … 0.36. V(t) y range −36 … −24 mV, then
−80 … +30 mV (animate from model t = 195 to 210 ms).

### Suggested asserts for `main.py`
```python
fp = fixed_points(114.0, SHUNT)[0]; assert fp[3].real.max() < 0 and abs(fp[3].imag).max() > 0.6
fp = fixed_points(114.5, SHUNT)[0]; assert fp[3].real.max() > 0
assert np.allclose(spikes(t, V), [203.9, 212.8, 221.8, 230.7, 239.7, 248.6, 257.6], atol=0.5)
assert V[t < 168].max() < -29.0          # all kicks stayed subthreshold
```
