"""Shared model, helpers and palette for the Prescott et al. (2008) videos in this area.

Prescott, Ratté, De Koninck & Sejnowski (2008) J Neurophysiol 100: 3030–3042: the paper's
modified Morris–Lecar model (Methods Eqs. 1–6), written from the equations, plus the helpers the
videos need (bifurcation current, 3-D fixed points, V–z nullcline, Fig. 9 parameter sets).

Import from a topic's main.py, after `from common import *` (which puts this area on sys.path):

    import prescott2008 as P

Read-only for topic builders: report bugs rather than editing this file.
Units: V mV, t ms, C µF/cm², g mS/cm², I µA/cm² (× 3 ≈ pA for the ~300 µm² model cell).
Eigenvalues are returned in 1/ms; multiply by 1000 for s⁻¹ on screen.
`uv run python neural-circuits-for-cognition/prescott2008.py` runs the asserts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from manimlib import (
    BLUE_B, BLUE_C, GOLD_C, GREEN_B, GREEN_C, GREY_A, GREY_B, GREY_D, GREY_E, ORANGE,
    PINK, PURPLE_A, PURPLE_C, RED_B, RED_C, TEAL_C, WHITE, YELLOW,
)
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# =============================================================== palette (workspace look)
# Semantic roles → ManimGL colours on the black background. The hue family follows the deck's
# palette; the shade is chosen to read on black. Use these names, never a literal, for a role.
CLASS1 = BLUE_C        # class 1 / integrator / continuous f–I / control / SNIC
CLASS2 = ORANGE        # class 2 / resonator / discontinuous f–I / shunted / Hopf
RESONANT = ORANGE      # resonant (band-pass) membrane — same as class 2 on purpose
PASSIVE = GREY_B       # passive RC membrane (low-pass)
NA = PINK              # Na⁺ / inward / depolarizing
K = TEAL_C             # K⁺ generic / outward / hyperpolarizing
IKDR = GOLD_C          # g_K,dr / w (paper Fig. 8C orange)
IM = GREEN_C           # g_M / z / I_M (paper Fig. 8C green) — green means I_M, nothing else
SHUNT_COLOR = PURPLE_C  # shunting conductance / dynamic clamp (SHUNT is the parameter set below)
VOLT = WHITE           # membrane-voltage traces and sums
INK = WHITE            # text
MUTED = GREY_B         # secondary text, projector lines, "removed" conditions
V_NULL = GREY_A        # V-nullcline
W_NULL = PURPLE_A      # w- (or z-) nullcline
STATE_DOT = YELLOW     # moving phase-plane state point
THETA_BAND = YELLOW    # θ band 3–10 Hz, fill_opacity THETA_ALPHA
THETA_ALPHA = 0.2
GAMMA_BAND = BLUE_B    # γ band 30–80 Hz, fill_opacity GAMMA_ALPHA
GAMMA_ALPHA = 0.2
HIGHLIGHT = RED_C      # kicks, flashes, call-outs, "unchanged" outlines
GOOD = GREEN_B
GRID = GREY_D
CHIP_FILL = GREY_E     # chip/box fill; stroke GREY_B
EXC, INH = RED_B, BLUE_B

# Slide-1-only component colours (carry no class meaning)
COMP_3HZ = "#0EA5E9"   # sky
COMP_6HZ = "#84CC16"   # lime
COMP_12HZ = "#A855F7"  # violet

THETA = (3.0, 10.0)
GAMMA = (30.0, 80.0)


# =============================================================== the model
@dataclass(frozen=True)
class MLParams:
    """Modified Morris–Lecar, Methods defaults ("unless otherwise stated")."""
    C: float = 2.0
    E_Na: float = 50.0
    E_K: float = -100.0
    E_shunt: float = -70.0
    g_Na: float = 20.0
    g_Kdr: float = 20.0
    g_shunt: float = 2.0     # control state; this term is the model's only leak. High conductance = 4
    phi_w: float = 0.25
    beta_m: float = -1.2
    gamma_m: float = 18.0
    beta_w: float = -9.0
    gamma_w: float = 10.0
    g_adapt: float = 0.0     # ḡ_M (M-type adaptation); 0 = none
    beta_z: float = -30.0
    gamma_z: float = 5.0
    tau_z: float = 200.0     # ms


CONTROL = MLParams()                                   # SNIC, class 1
SHUNT = MLParams(g_shunt=4.0)                          # Hopf, class 2
ADAPT = MLParams(g_adapt=2.0)
SHUNT_ADAPT = MLParams(g_shunt=4.0, g_adapt=2.0)
# θ model (Fig. 8A/B legends): γ_w 8, ḡ_K,dr 30, ḡ_M 2, τ_z 400 ms
THETA_MODEL = MLParams(gamma_w=8.0, g_Kdr=30.0, g_adapt=2.0, tau_z=400.0)
# Fig. 9 legend set and its variants
FIG9 = MLParams(g_Na=24.0, g_Kdr=30.0, gamma_w=8.0, g_adapt=2.0, beta_z=-29.0, gamma_z=2.0,
                tau_z=400.0)
FIG9_INACT = replace(FIG9, g_Na=24.0 * 0.67)           # 33% steady-state Na⁺ inactivation (16.08)
FIG9_SHUNT = replace(FIG9, g_shunt=3.5)                # not 4.0: that gives the fast (~36 Hz) mode
FIG9_INACT_NO_IM = replace(FIG9_INACT, g_adapt=0.0)


def m_inf(V, p: MLParams):
    return 0.5 * (1 + np.tanh((V - p.beta_m) / p.gamma_m))


def w_inf(V, p: MLParams):
    return 0.5 * (1 + np.tanh((V - p.beta_w) / p.gamma_w))


def tau_w(V, p: MLParams):
    return 1.0 / np.cosh((V - p.beta_w) / (2 * p.gamma_w))


def z_inf(V, p: MLParams):
    return 1.0 / (1 + np.exp((p.beta_z - V) / p.gamma_z))


def currents(V, w, z, p: MLParams):
    """Outward-positive membrane currents (µA/cm²): keys Na, Kdr, shunt, adapt."""
    return dict(
        Na=p.g_Na * m_inf(V, p) * (V - p.E_Na),
        Kdr=p.g_Kdr * w * (V - p.E_K),
        shunt=p.g_shunt * (V - p.E_shunt),
        adapt=p.g_adapt * z * (V - p.E_K),
    )


def rhs(t, y, p: MLParams, I_stim=0.0):
    V, w, z = y
    Iion = sum(currents(V, w, z, p).values())
    return [
        (I_stim - Iion) / p.C,
        p.phi_w * (w_inf(V, p) - w) / tau_w(V, p),
        (z_inf(V, p) - z) / p.tau_z,
    ]


def rest_state(p: MLParams, I_stim=0.0):
    """(V, w, z) at the lowest stable 3-D fixed point for I_stim (the usual starting point)."""
    fp = next(f for f in fixed_points_3d(p, I_stim) if f["stable"])
    return [fp["V"], fp["w"], fp["z"]]


def simulate(p: MLParams, I_stim=0.0, t_ms=1000.0, y0=None, max_step=0.05, I_func=None,
             t_eval=None):
    """Deterministic LSODA run. I_stim constant, or I_func(t_ms) → µA/cm². Returns (t, V, w, z).

    For step protocols pass max_step ≤ the shortest pulse (e.g. 0.05 for 0.5-ms pulses).
    """
    if y0 is None:
        y0 = rest_state(p, 0.0)
    f = (lambda t, y: rhs(t, y, p, I_func(t))) if I_func else (lambda t, y: rhs(t, y, p, I_stim))
    sol = solve_ivp(f, (0, t_ms), y0, method="LSODA", max_step=max_step, rtol=1e-6, atol=1e-8,
                    t_eval=t_eval)
    return sol.t, sol.y[0], sol.y[1], sol.y[2]


def simulate_noisy(p: MLParams, I_stim, t_ms=2000.0, dt=0.02, sigma=0.1, tau_noise=5.0, y0=None,
                   seed=0):
    """Euler–Maruyama with an Ornstein–Uhlenbeck noise current added to I_stim.

    Noise convention (paper): stationary variance σ²τ/2 (µA/cm²)². Returns (t, V, w, z, I_noise).
    Scalar loop (~1 µs/step class); 10⁶ steps take a few seconds — cache long runs (npz_cache).
    """
    rng = np.random.default_rng(seed)
    n = int(round(t_ms / dt))
    if y0 is None:
        y0 = rest_state(p, I_stim)
    V, w, z = (float(v) for v in y0)
    C, ENa, EK, Esh = p.C, p.E_Na, p.E_K, p.E_shunt
    gNa, gK, gsh, gM = p.g_Na, p.g_Kdr, p.g_shunt, p.g_adapt
    bm, gm_, bw, gw, bz, gz = p.beta_m, p.gamma_m, p.beta_w, p.gamma_w, p.beta_z, p.gamma_z
    phi, tz = p.phi_w, p.tau_z
    a = math.exp(-dt / tau_noise)
    b = sigma * math.sqrt(tau_noise / 2.0) * math.sqrt(1 - a * a)
    xi = rng.standard_normal(n)
    tanh, cosh, exp = math.tanh, math.cosh, math.exp
    out = np.empty((n, 5))
    In = 0.0
    for i in range(n):
        m = 0.5 * (1 + tanh((V - bm) / gm_))
        winf = 0.5 * (1 + tanh((V - bw) / gw))
        tw = 1.0 / cosh((V - bw) / (2 * gw))
        zinf = 1.0 / (1 + exp((bz - V) / gz))
        Iion = gNa * m * (V - ENa) + gK * w * (V - EK) + gsh * (V - Esh) + gM * z * (V - EK)
        dV = (I_stim + In - Iion) / C
        dw = phi * (winf - w) / tw
        dz = (zinf - z) / tz
        V += dt * dV
        w += dt * dw
        z += dt * dz
        In = a * In + b * xi[i]
        out[i, 0] = (i + 1) * dt
        out[i, 1] = V
        out[i, 2] = w
        out[i, 3] = z
        out[i, 4] = In
    return out[:, 0], out[:, 1], out[:, 2], out[:, 3], out[:, 4]


def spike_times(t, V, thresh=0.0):
    up = np.where((V[:-1] < thresh) & (V[1:] >= thresh))[0]
    return t[up]


# ---- steady-state I–V and nullclines
def iv_steady(V, p: MLParams, include_adapt=True):
    """Steady-state I–V (outward +): every gate at x∞(V)."""
    z = z_inf(V, p) if include_adapt else 0.0
    return sum(currents(V, w_inf(V, p), z, p).values())


def iv_instantaneous(V, p: MLParams, V_hold=-70.0):
    """Instantaneous I–V: m at m∞(V); w and z frozen at their values at V_hold."""
    return sum(currents(V, w_inf(V_hold, p), z_inf(V_hold, p), p).values())


def V_nullcline_w(V, p: MLParams, I_stim, z=0.0):
    """w on the V-nullcline (dV/dt = 0) as a function of V, with z held fixed."""
    c = currents(V, 0.0, z, p)
    return (I_stim - c["Na"] - c["shunt"] - c["adapt"]) / (p.g_Kdr * (V - p.E_K))


def w_nullcline(V, p: MLParams):
    return w_inf(V, p)


def z_Vnull(V, p: MLParams, I_stim):
    """z on the V-nullcline of the V–z plane, with w slaved to w∞(V). Needs g_adapt > 0."""
    c = currents(V, w_inf(V, p), 0.0, p)
    return (I_stim - c["Na"] - c["Kdr"] - c["shunt"]) / (p.g_adapt * (V - p.E_K))


def z_nullcline(V, p: MLParams):
    return z_inf(V, p)


# ---- fixed points and stability
def _classify(ev):
    if np.all(np.abs(ev.imag) < 1e-12):
        if ev.real.max() < 0:
            return "stable node"
        if ev.real.min() > 0:
            return "unstable node"
        return "saddle"
    return "stable focus" if ev.real.max() < 0 else "unstable focus"


def _fp_voltages(p, I_stim, z=None, V_range=(-90.0, 20.0), n=4000):
    def g(V):
        zz = z_inf(V, p) if z is None else z
        return I_stim - sum(currents(V, w_inf(V, p), zz, p).values())
    Vs = np.linspace(*V_range, n)
    gv = g(Vs)
    return [brentq(g, Vs[i], Vs[i + 1]) for i in np.where(np.sign(gv[:-1]) != np.sign(gv[1:]))[0]]


def jacobian_2d(V, w, z, p: MLParams, h=1e-5):
    """(V, w) Jacobian with z frozen, 1/ms."""
    def f(v, ww):
        return np.array(rhs(0, (v, ww, z), p, 0.0)[:2])
    J = np.empty((2, 2))
    J[:, 0] = (f(V + h, w) - f(V - h, w)) / (2 * h)
    J[:, 1] = (f(V, w + h) - f(V, w - h)) / (2 * h)
    return J


def jacobian_3d(V, w, z, p: MLParams, h=1e-6):
    """Full (V, w, z) Jacobian, central differences, 1/ms."""
    y = np.array([V, w, z], float)
    J = np.empty((3, 3))
    for k in range(3):
        d = np.zeros(3)
        d[k] = h
        J[:, k] = (np.array(rhs(0, y + d, p, 0.0)) - np.array(rhs(0, y - d, p, 0.0))) / (2 * h)
    return J


def fixed_points(p: MLParams, I_stim, z=None):
    """Fixed points of the (V, w) system with z frozen (default z = z∞(V*), i.e. on the 3-D FP).

    Exact 2-D analysis when g_adapt = 0. Returns [{V, w, z, eig (1/ms), kind}], sorted by V.
    """
    out = []
    for V0 in _fp_voltages(p, I_stim, z):
        zz = float(z_inf(V0, p)) if z is None else z
        w0 = float(w_inf(V0, p))
        ev = np.linalg.eigvals(jacobian_2d(V0, w0, zz, p))
        out.append(dict(V=V0, w=w0, z=zz, eig=ev, kind=_classify(ev)))
    return out


def fixed_points_3d(p: MLParams, I_stim):
    """Fixed points of the full (V, w, z) system: solve I = I_ss(V) with w = w∞, z = z∞.

    Returns [{V, w, z, eig (1/ms), kind, stable}], sorted by V. When g_adapt = 0 the extra
    eigenvalue is −1/τ_z and the other two equal the 2-D ones.
    """
    out = []
    for V0 in _fp_voltages(p, I_stim):
        w0, z0 = float(w_inf(V0, p)), float(z_inf(V0, p))
        ev = np.linalg.eigvals(jacobian_3d(V0, w0, z0, p))
        out.append(dict(V=V0, w=w0, z=z0, eig=ev, kind=_classify(ev),
                        stable=bool(np.all(ev.real < 0))))
    return out


def has_stable_fp(p: MLParams, I_stim):
    return any(f["stable"] for f in fixed_points_3d(p, I_stim))


def find_I_bif(p: MLParams, lo=0.0, hi=400.0, tol=1e-6):
    """Largest I_stim with a stable fixed point (bisection on "a stable FP exists")."""
    assert has_stable_fp(p, lo) and not has_stable_fp(p, hi)
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if has_stable_fp(p, mid) else (lo, mid)
    return lo


def stable_fp_3d(p: MLParams, I_stim):
    """The (lowest-V) stable 3-D fixed point, or None."""
    return next((f for f in fixed_points_3d(p, I_stim) if f["stable"]), None)


def bifurcation_type(p: MLParams, V_lo=-75.0, V_hi=0.0, dV=0.01):
    """("SN" | "Hopf", V*, I_bif) for the loss of the rest state, found by walking the rest branch.

    On a fixed point I_stim = I_ss(V), and the Jacobian depends on V only, so walk V upward from
    rest until the first eigenvalue reaches Re λ = 0. A real eigenvalue crossing (det J = 0,
    i.e. dI_ss/dV = 0) is a saddle-node (on the invariant circle here → SNIC); a complex pair
    crossing is a Hopf. Exact even next to the Bogdanov–Takens point, where bisection on I
    cannot separate the two. V* is the paper's threshold.
    """
    def J(V):
        return jacobian_3d(V, float(w_inf(V, p)), float(z_inf(V, p)), p)

    def lead(V):  # (max Re λ, det J)
        return np.linalg.eigvals(J(V)).real.max(), np.linalg.det(J(V))

    Vs = np.arange(V_lo, V_hi, dV)
    r0, d0 = lead(Vs[0])
    assert r0 < 0, "branch start is not stable"
    for a, b in zip(Vs[:-1], Vs[1:]):
        r, d = lead(b)
        if np.sign(d) != np.sign(d0):
            V_star = brentq(lambda v: np.linalg.det(J(v)), a, b)
            return "SN", V_star, float(iv_steady(V_star, p))
        if r >= 0:
            V_star = brentq(lambda v: lead(v)[0], a, b)
            return "Hopf", V_star, float(iv_steady(V_star, p))
        d0 = d
    raise ValueError("rest state never loses stability in the V range")


def ring_hz(eig):
    """Ring frequency |Im λ|/2π in Hz for λ in 1/ms (0 if all real)."""
    return float(np.abs(np.imag(eig)).max() / (2 * np.pi) * 1000.0)


def per_cycle_factor(lam):
    """Amplitude factor per ring cycle, exp(2π·Re λ/|Im λ|), for one complex λ."""
    return float(np.exp(2 * np.pi * lam.real / abs(lam.imag)))


# =============================================================== impedance (slide-1 motif)
def impedance_complex(f_hz, R=100.0, tau_ms=20.0, g=1.0, tau_w_ms=80.0):
    """Complex Z(f) = R / (1 + iωτ + g/(1 + iωτ_w)) in MΩ, ω = 2πf (not rescaled)."""
    iw = 2j * np.pi * np.asarray(f_hz, float) * 1e-3   # 1/ms
    return R / (1 + iw * tau_ms + g / (1 + iw * tau_w_ms))


def impedance_peak_hz(**kw):
    f = np.linspace(0.05, 30, 60000)
    return float(f[np.argmax(np.abs(impedance_complex(f, **kw)))])


# =============================================================== caching
def npz_cache(path, fn, **meta):
    """Load `path` (.npz) if it exists and its stored meta matches, else run fn() → dict and save.

    `meta` values (seeds, σ, dt …) are stored alongside and must match on load, so changing a
    recipe recomputes instead of silently reusing stale data.
    """
    path = Path(path)
    if path.exists():
        d = dict(np.load(path, allow_pickle=False))
        if all(k in d and np.array_equal(d[k], np.asarray(v)) for k, v in
               {f"meta_{k}": v for k, v in meta.items()}.items()):
            return {k: v for k, v in d.items() if not k.startswith("meta_")}
    data = fn()
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **data, **{f"meta_{k}": np.asarray(v) for k, v in meta.items()})
    return data


# =============================================================== checks
if __name__ == "__main__":
    def near(a, b, tol):
        return abs(a - b) <= tol

    V = np.linspace(-70, -20, 20001)

    # I–V: control hump, min slope and where it goes away
    s = np.gradient(iv_steady(V, CONTROL), V)
    assert near(s.min(), -0.2395, 0.001) and near(V[s.argmin()], -34.44, 0.02)
    for g, has_neg in [(2.239, True), (2.2396, False)]:
        s = np.gradient(iv_steady(V, replace(CONTROL, g_shunt=g)), V)
        assert (s.min() < 0) == has_neg

    # bifurcation currents and type (2-D models)
    Ic, Is = find_I_bif(CONTROL), find_I_bif(SHUNT)
    assert near(Ic, 38.74, 0.01) and near(Is, 114.24, 0.01), (Ic, Is)
    assert np.all(np.abs(stable_fp_3d(CONTROL, Ic)["eig"].imag) < 1e-9)       # SNIC: real λ
    assert ring_hz(stable_fp_3d(SHUNT, Is)["eig"]) > 90                          # Hopf: complex
    # SNIC → Hopf switch lies between g_shunt 2.16 and 2.17 (Bogdanov–Takens ≈ 2.1656)
    for g, kind in [(2.0, "SN"), (2.16, "SN"), (2.17, "Hopf"), (2.2, "Hopf"), (4.0, "Hopf")]:
        assert bifurcation_type(replace(CONTROL, g_shunt=g))[0] == kind, g

    # θ models (3-D)
    Ia, It = find_I_bif(replace(THETA_MODEL, g_shunt=4.0)), find_I_bif(THETA_MODEL)
    assert near(Ia, 183.06, 0.05) and near(It, 53.39, 0.05), (Ia, It)
    for pp, Ib in [(FIG9, 33.19), (FIG9_INACT, 44.12), (FIG9_SHUNT, 83.1), (FIG9_INACT_NO_IM, 42.02)]:
        assert near(find_I_bif(pp), Ib, 0.1), (pp, find_I_bif(pp))

    # impedance peak and V–z nullcline consistency
    assert near(impedance_peak_hz(), 5.1, 0.1)
    fp = stable_fp_3d(THETA_MODEL, 0.99 * It)
    assert near(z_Vnull(fp["V"], THETA_MODEL, 0.99 * It), fp["z"], 1e-9)
    assert near(V_nullcline_w(fp["V"], THETA_MODEL, 0.99 * It, z=fp["z"]), fp["w"], 1e-9)
    print("prescott2008: ok")
