# Model — eigenvalue_phasor_ringing_frequency

The paper's modified Morris–Lecar in the (V, w) plane, z frozen at 0 (g_M = 0), so CONTROL
and SHUNT are exactly two-dimensional. The eigenvalues are those of the 2×2 Jacobian at a
fixed point. Sources: paper Methods, Eqs. 1–6; deck model; background §20–26. Numbers computed
2026-09-29 with the model block in `main.py`, and all of them are pinned by `check_model()`.

## Equations and parameters

```
C dV/dt = I − g_Na·m∞(V)·(V − E_Na) − g_Kdr·w·(V − E_K) − g_shunt·(V − E_shunt)
dw/dt   = φ_w·(w∞(V) − w)/τ_w(V)
m∞ = ½[1 + tanh((V − β_m)/γ_m)]   w∞ = ½[1 + tanh((V − β_w)/γ_w)]   τ_w = 1/cosh((V − β_w)/(2γ_w))
```

C = 2, E_Na = +50, E_K = −100, E_shunt = −70, g_Na = 20, g_Kdr = 20, φ_w = 0.25,
β_m = −1.2, γ_m = 18, β_w = −9, γ_w = 10.
- **CONTROL**: g_shunt = 2 (class 1, SNIC).
- **SHUNT**: g_shunt = 4 (class 2, subcritical Hopf).

Units: V in mV, t in ms, I in µA/cm² (≈ pA/3 for the paper's 300 µm² cell), λ in 1/ms.
- Frequency is **f = |Im λ|/2π × 1000 Hz**.
- The e-fold decay time is −1/Re λ ms.
- "Cycles per e-fold" is |Im λ|/(2π|Re λ|); ringing is visible only when this is around 0.3
  or more.

The model block in `main.py` has the same `BASE`, `f2`, `V_null`, `fixed_points` and `run` as
class1_snic_onset_slow_crawl / class2_hopf_onset_spiral_escape (which match the deck model bit for bit). New here:
- `jac`: the Jacobian by central differences, h = 1e-5.
- `rest_eigs`, `saddle_eigs`: sorted pairs, with a complex pair ordered +Im first and a real
  pair by Re descending. They return `None` when the point does not exist.
- `complex_window`: roots of tr² − 4 det.
- `kick_modes`, `lin_kick`.
- `saddle_birth`.

## Landmarks

| Quantity | Value |
|---|---|
| I_SN (class 1 rest meets saddle; SNIC) | **38.7409** |
| I_BIRTH (saddle + upper unstable node born, at V ≈ −31.6 mV) | 37.6842 |
| Class 1 rest complex window (brief overdamped focus) | 35.601 – 38.634 |
| Class 2 rest becomes complex (focus) | 86.373 |
| Class 2 complex blip (negligible: Im ≤ 0.053, \|Re\|/Im ≥ 35) | 20.9 – 31.0 |
| I_Hopf (class 2 pair crosses Re = 0) | **114.2358**, λ = ±0.6522i → **103.8 Hz** |

`rest_eigs(I, CONTROL)` is `None` for I ≥ I_SN. Without that guard, `fixed_points()[0]` would
jump to the upper branch near −29 mV.

## Class 1 (CONTROL): rest and saddle eigenvalues

| I | rest λ | saddle λ |
|---|---|---|
| 0 | −0.938, −2.566 | — |
| 30 | −0.668, −0.989 | — |
| 36.0 | −0.552 ± 0.041i | — |
| 37.0 | −0.475 ± 0.073i | — |
| 37.85 | −0.383 ± 0.084i (max Im) | +0.760, −0.058 |
| 38.0 | −0.362 ± 0.083i | +0.644, −0.084 |
| 38.3 | −0.310 ± 0.076i | +0.446, −0.128 |
| 38.6 | −0.230 ± 0.035i | +0.229, −0.176 |
| 38.65 | −0.181, −0.234 | +0.181, −0.187 |
| 38.7 | −0.116, −0.239 | +0.119, −0.201 |
| 38.73 | −0.059, −0.234 | +0.060, −0.213 |
| → I_SN | → 0, → −0.22 | → 0, → −0.22 |

**How it moves:**
1. Rest's two real eigenvalues approach each other and meet at 35.60.
2. They lift into a faint pair (Im ≤ 0.084, so at most 13 Hz, with |Re|/Im ≈ 4.6 and 0.035
   cycles per e-fold, meaning no visible ringing) and fall back to the real axis at 38.63.
3. They split again. The right one runs to 0 while the saddle's positive eigenvalue runs down
   to 0 to meet it. The two negative eigenvalues also converge, to −0.22.

At I_SN the pairs coincide; above it neither point exists. The saddle's eigenvalues are born at
about (0, ≈ +1) at I_BIRTH, where the saddle is created with the unstable upper node.

## Class 2 (SHUNT): rest eigenvalues

| I | λ | f (Hz) | cycles per e-fold |
|---|---|---|---|
| 0 | −1.941, −2.606 | — | — |
| 80 | −0.957, −1.329 | — | — |
| 86.4 | −1.028 ± 0.014i | 2 | 0.002 |
| 90 | −0.954 ± 0.171i | 27 | 0.03 |
| 95 | −0.834 ± 0.290i | 46 | 0.06 |
| 100 | −0.685 ± 0.399i | 63.5 | 0.09 |
| 105 | −0.492 ± 0.505i | 80.4 | 0.16 |
| 110 | −0.241 ± 0.599i | 95.3 | 0.40 |
| 112.5 | −0.0991 ± 0.6344i | 101.0 | 1.02 |
| 114.0 | −0.0133 ± 0.6501i | 103.5 | 7.8 |
| **114.2358** | **±0.6522i** | **103.8** | ∞ |
| 115 | +0.0428 ± 0.6583i | 104.8 | (grows) |
| 116 | +0.0976 ± 0.6648i | 105.8 | (grows) |

The pair crosses the imaginary axis well above 0. That is the geometric reason class 2 cannot
fire slowly. Just above the Hopf the model fires at ≈ 105–112 spikes/s, and the bistable window
113.14–114.24 has f_min ≈ 80 (class2_hopf_onset_spiral_escape model.md).

## Kick decomposition (stories 2 and 3)

A kick of dV from rest, V → V* + dV with w unchanged, gives exactly
δV(t) = Σ c_k e^{λ_k t} in the linearization (`kick_modes`, `lin_kick`).
- **KICK_DV = 0.2 mV.** The error against the full model is second order: over 40 ms it is
  1.3 / 2.6 / 7 / 16% of the kick for 0.1 / 0.2 / 0.5 / 1.0 mV at I = 112.5, and 0.7 / 1.4 / 4 /
  8% at I = 110. At 0.2 mV the simulated dots sit on the linear curve.
- **Class 2 at I = 112.5, dV = 0.2:** c = 0.1 ∓ 0.0547i, so each phasor starts at length
  0.114 and angle ∓28.7°. The two are conjugate, so their sum is real and starts at 0.2. The
  period is 9.90 ms (101 Hz) and the e-fold time 10.1 ms.
- **Class 1 at I = 38.7, dV = 0.2:** real modes λ = −0.1156 (c = +0.7745) and λ = −0.2392
  (c = −0.5745). Two arrows lie on the real axis pointing in opposite directions, the long slow
  one to the right and the shorter fast one to the left, and they sum to 0.2. They never turn,
  and the sum never undershoots. It is not monotone: the fast (negative) arrow dies first, so
  δV first rises to 0.268 mV (1.34 kicks) at 3.5 ms, then relaxes (1.61 kicks at 5.5 ms for
  38.73). The linearization is 13.5% (38.7) / 39% (38.73) of the kick off the full model over
  40 ms near I_SN, so the video draws class 1 without sim dots (checked 2026-09-29).
- **Class 1 at I = 38.0:** the pair is complex (−0.362 ± 0.083i), but a 0.2 mV kick undershoots
  by less than 0.001 mV. It is complex, yet decays about 4.4× faster than it turns (|Re|/Im at 38.0).

## λ-plane display (shared by all three videos)

- **Scale:** Re [−1.1, 0.8] × Im [−0.75, 0.75] with the same units on both axes, so a 45° line
  means |Re| = Im.
- **What each class looks like on it:** class 1's Im blip (≤ 0.084) shows as a small lift. The
  class 1 ramp spans Re −0.94 … +0.76 when starting from I = 0 and including the saddle, so
  either start the ramp at I ≈ 30 or accept the saddle's entry at +0.76 from 37.85.
- **Axis labels:** "Re λ" / "Im λ" in 1/ms, with a secondary Hz reading only on Im.
