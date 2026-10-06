"""The e^{lambda t} phasor behind the ringing.

Contract: context_files/contract.md. Render: -w -r 1344x1200 (8.96 x 8 units), 23.2 s, 30 fps.

A kick's aftermath is deltaV(t) = c e^{lambda t} + conj(c) e^{conj(lambda) t}: two
counter-rotating, shrinking arrows whose sum stays real. Im lambda is the spin rate (MPO
frequency = Im lambda / 2pi), Re lambda the shrink rate. Class 1's arrows never spin.

One ValueTracker T (model ms) drives each run and one ValueTracker I drives the inset's
lambda; every moving element is a pure function of them. The phasor plane is rotated 90 deg
(Re = deltaV up, +Im left) and its unit is the kick, so the sum's shadow runs straight right
into the time strip. Arrows are tip-to-tail: arrow 1 = c e^{lam t} from 0, arrow 2 (60%)
from its tip to the yellow sum dot on the real axis.

Beats as built:
1. 0.0-1.2 s   Still: class 2 at I = 112.5, arrows at t = 0 (0.570 kick each, -+28.7 deg), sum
               dot at the kick, dashed guide to the strip, "0.2 mV kick" marker, inset
               lambda = -0.099 +- 0.634i, tag "Class 2 · Hopf".
2. 1.2-6.7 s   T 0 -> 40 ms (7.3 ms per s): arrows counter-rotate and shrink, the tip draws
               an inward spiral (last 1 s opaque, older 35%), the shadow draws the damped
               cosine over the sim dots (every 0.5 ms). Equation line 1 fades in at 1.2 s,
               the dashed envelope +-2|c|e^{Re lam t} at 3.7 s.
3. 6.7-9.2 s   Freeze: equation line 2 writes; red box on e^{i Im lam t} + curved arrow,
               "spin = Im lam -> 101 Hz"; box moves to e^{Re lam t} + inward arrow, envelope
               turns red, "shrink = Re lam -> 10 ms".
4. 9.2-12.7 s  Class 2 run fades, inset x slides to the imaginary axis (I -> I_Hopf),
               readouts -> "104 Hz" / "Re lam = 0", kick -> 0.1 mV (same size on screen);
               fresh kick, T 0 -> 20 ms: the tip circles, the shadow is a steady sine over
               the dots; caption "at the crossing it is already spinning".
5. 12.7-18.75 s Cut to class 1 at 38.7 (tag, two real x's, c1/c2 equation, "spin = Im lam =
               0", "shrink -> 8.7, 4.2 ms"): "slow" arrow up +3.87 kicks, "fast" arrow down
               -2.87 kicks (split sideways 0.13, schematic); T 0 -> 40 ms in 2.4 s: they shrink
               without turning, deltaV rises then relaxes with no undershoot; caption
               "Im lam = 0 -> nothing to ring with". Then lambda -> 0 (38.73), first curve
               kept at 30%, "17, 4.3 ms", fresh kick: the slow arrow lingers.
6. 18.75-23.2 s End frame: class 2 panel (inward spiral + damped cosine, "Im lam/2pi = 101
               Hz") vs class 1 panel (flat arrows + relaxation, "Im lam = 0"); inset shows
               both lambdas; caption "MPO frequency = spin rate = Im lam / 2pi"; hold 2.9 s.
"""

from common import *

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

# ---------------------------------------------------------------------------
# Shared lambda-plane look. The same spec is used by s05_vid3_two_planes (and the
# colors by s05_vid4_lambda_traces); keep these constants identical across videos.
# ---------------------------------------------------------------------------

CLASS1_COLOR = BLUE_C          # class 1 / SNIC / control
CLASS2_COLOR = ORANGE          # class 2 / Hopf / shunted
STATE_COLOR = YELLOW           # state point, sum dot
FLASH_COLOR = RED_C            # flashes, rings, call-outs
FLASH_MIN_RADIUS = 0.4
LAM_RE = (-1.1, 0.8)           # 1/ms; equal units on both axes
LAM_IM = (-0.75, 0.75)
LAM_AXIS_COLOR = GREY_B
LAM_AXIS_STROKE = 2
LAM_LABEL_FONT = 28
LAM_UNSTABLE_OPACITY = 0.10
LAM_UNSTABLE_FONT = 24
LAM_CROSS_LEN = 0.22           # each bar of the x, at +-45 degrees
LAM_CROSS_STROKE = 5
LAM_SADDLE_OUTER = 7           # hollow x: class color stroke 7 under black stroke 3
LAM_SADDLE_INNER = 3
TRAIL_STROKE = 3
TRAIL_RECENT_S = 1.0           # video seconds of trail drawn opaque
TRAIL_OLD_OPACITY = 0.35


def lam_cross(point, color, size=LAM_CROSS_LEN):
    """Rest's lambda: solid x, two crossed bars at +-45 degrees."""
    point = np.asarray(point, float)
    a = size / 2 * np.array([1, 1, 0]) / np.sqrt(2)
    b = size / 2 * np.array([-1, 1, 0]) / np.sqrt(2)
    return VGroup(Line(point - a, point + a), Line(point - b, point + b)).set_stroke(
        color, LAM_CROSS_STROKE)


def lam_saddle_cross(point, color, size=LAM_CROSS_LEN):
    """Saddle's lambda: the same x, hollow (class color stroke 7 under black stroke 3)."""
    return VGroup(lam_cross(point, color, size).set_stroke(color, LAM_SADDLE_OUTER),
                  lam_cross(point, BLACK, size).set_stroke(BLACK, LAM_SADDLE_INNER))


class LamPlane(VGroup):
    """The shared lambda plane fitted (equal units) and centred in box = (x0, x1, y0, y1).

    `l2p(lam)` maps a complex eigenvalue to a scene point. Labels keep their font size
    whatever the box, so a small inset stays readable.
    """

    def __init__(self, box):
        super().__init__()
        x0, x1, y0, y1 = box
        self.u = min((x1 - x0) / (LAM_RE[1] - LAM_RE[0]), (y1 - y0) / (LAM_IM[1] - LAM_IM[0]))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.origin = np.array([cx - self.u * sum(LAM_RE) / 2, cy - self.u * sum(LAM_IM) / 2, 0])
        half = Polygon(self.l2p(LAM_IM[0] * 1j), self.l2p(LAM_RE[1] + LAM_IM[0] * 1j),
                       self.l2p(LAM_RE[1] + LAM_IM[1] * 1j), self.l2p(LAM_IM[1] * 1j))
        half.set_fill(FLASH_COLOR, LAM_UNSTABLE_OPACITY).set_stroke(width=0)
        axes = VGroup(Line(self.l2p(LAM_RE[0]), self.l2p(LAM_RE[1])),
                      Line(self.l2p(LAM_IM[0] * 1j), self.l2p(LAM_IM[1] * 1j)))
        axes.set_stroke(LAM_AXIS_COLOR, LAM_AXIS_STROKE)
        re_lab = tex(R"\mathrm{Re}\,\lambda", font_size=LAM_LABEL_FONT).set_color(LAM_AXIS_COLOR)
        re_lab.next_to(self.l2p(LAM_RE[0]), DOWN, buff=0.1).align_to(self.l2p(LAM_RE[0]), LEFT)
        im_lab = tex(R"\mathrm{Im}\,\lambda", font_size=LAM_LABEL_FONT).set_color(LAM_AXIS_COLOR)
        im_lab.move_to(self.l2p(LAM_RE[0] + LAM_IM[1] * 1j), aligned_edge=UL)
        unst = txt("unstable", font_size=LAM_UNSTABLE_FONT).set_color(FLASH_COLOR)
        unst.next_to(half, DOWN, buff=0.08).align_to(half, RIGHT)
        self.half, self.axes, self.labels = half, axes, VGroup(re_lab, im_lab, unst)
        self.add(half, axes, self.labels)

    def l2p(self, lam):
        lam = complex(lam)
        return self.origin + self.u * np.array([lam.real, lam.imag, 0.0])


# ---------------------------------------------------------------------------
# Model: the paper's modified Morris-Lecar (V, w), z frozen at 0.
# CONTROL (g_shunt = 2) is class 1 / SNIC; SHUNT (g_shunt = 4) is class 2 / Hopf.
# Reference implementation from context_files/model.md (same code as class1_snic_onset_slow_crawl / class2_hopf_onset_spiral_escape).
# Units: V mV, t ms, I uA/cm^2, lambda 1/ms.
# ---------------------------------------------------------------------------

BASE = dict(C=2.0, ENa=50.0, EK=-100.0, Esh=-70.0, gNa=20.0, gK=20.0, gsh=2.0, phi=0.25,
            bm=-1.2, gm=18.0, bw=-9.0, gw=10.0, gM=0.0, bz=-30.0, gz=5.0)
CONTROL = dict(BASE)
SHUNT = dict(BASE, gsh=4.0)


def minf(V, p):
    return 0.5 * (1 + np.tanh((V - p['bm']) / p['gm']))


def winf(V, p):
    return 0.5 * (1 + np.tanh((V - p['bw']) / p['gw']))


def tauw(V, p):
    return 1 / np.cosh((V - p['bw']) / (2 * p['gw']))


def I_fixed(V, p, z=0.0):
    return p['gNa'] * minf(V, p) * (V - p['ENa']) + p['gsh'] * (V - p['Esh']) + p['gM'] * z * (V - p['EK'])


def f2(V, w, I, p, z=0.0):
    Iion = (p['gNa'] * minf(V, p) * (V - p['ENa']) + p['gK'] * w * (V - p['EK'])
            + p['gsh'] * (V - p['Esh']) + p['gM'] * z * (V - p['EK']))
    return (I - Iion) / p['C'], p['phi'] * (winf(V, p) - w) / tauw(V, p)


def V_null(V, I, p, z=0.0):
    return (I - I_fixed(V, p, z)) / (p['gK'] * (V - p['EK']))


def I_ss(V, p):
    """Steady-state I-V curve (all gates at steady state)."""
    return I_fixed(V, p) + p['gK'] * winf(V, p) * (V - p['EK'])


def jac(V, w, I, p, h=1e-5):
    """2-D (V, w) Jacobian by central differences, z frozen."""
    return np.column_stack([
        (np.array(f2(V + h, w, I, p)) - f2(V - h, w, I, p)) / (2 * h),
        (np.array(f2(V, w + h, I, p)) - f2(V, w - h, I, p)) / (2 * h)])


def fixed_points(I, p, z=0.0):
    g = lambda V: I - (I_fixed(V, p, z) + p['gK'] * winf(V, p) * (V - p['EK']))
    Vs = np.linspace(-90, 20, 4000)
    gv = g(Vs)
    out = []
    for i in np.where(np.sign(gv[:-1]) != np.sign(gv[1:]))[0]:
        V0 = brentq(g, Vs[i], Vs[i + 1])
        w0 = winf(V0, p)
        out.append((V0, w0, z, np.linalg.eigvals(jac(V0, w0, I, p))))
    return out  # sorted by V; out[0] is rest while rest exists


def run(p, I_of_t, t0, t1, y0):
    s = solve_ivp(lambda t, y: f2(y[0], y[1], I_of_t(t), p), (t0, t1), y0,
                  method='LSODA', max_step=0.02, rtol=1e-9, atol=1e-11)
    return s.t, s.y[0], s.y[1]


def spikes(t, V):
    """Upward crossings of 0 mV."""
    k = np.where((V[:-1] < 0) & (V[1:] >= 0))[0]
    return t[k]


def saddle_node(p=CONTROL):
    """(I_SN, V_SN, w_SN): maximum of the steady-state I-V curve on [-50, -30] mV."""
    r = minimize_scalar(lambda V: -I_ss(V, p), bounds=(-50, -30), method='bounded',
                        options=dict(xatol=1e-10))
    return I_ss(r.x, p), r.x, winf(r.x, p)


def saddle_birth(p=CONTROL):
    """(I, V): minimum of the I-V hump, where the saddle and the upper node are born."""
    r = minimize_scalar(lambda V: I_ss(V, p), bounds=(-36, -25), method='bounded',
                        options=dict(xatol=1e-10))
    return I_ss(r.x, p), r.x


def hopf_current(p=SHUNT):
    """Current at which the rest focus loses stability (max Re lambda = 0)."""
    return brentq(lambda I: fixed_points(I, p)[0][3].real.max(), 105, 120, xtol=1e-8)


I_SN = saddle_node(CONTROL)[0]
I_BIRTH = saddle_birth(CONTROL)[0]
I_HOPF = hopf_current(SHUNT)
KICK_DV = 0.2  # mV; small enough that the linear phasor picture is within 3%
KICK_HOPF = 0.1  # mV; beat 4 at I_Hopf, where the subcritical Hopf bends 0.2 mV by 4.6%


# ---------------------------------------------------------------------------
# Eigenvalue tracking (new for the eigenvalue videos)
# ---------------------------------------------------------------------------

def sort_pair(lam):
    """Deterministic order: complex pair +Im first; real pair Re descending."""
    lam = np.asarray(lam, dtype=complex)
    if abs(lam[0].imag) > 1e-12:
        return lam[np.argsort(-lam.imag)]
    return np.sort(lam.real)[::-1].astype(complex)


def rest_point(I, p):
    """(V*, w*) of rest, or None when rest no longer exists (CONTROL above I_SN)."""
    if p['gsh'] == CONTROL['gsh'] and I >= I_SN:
        return None
    V0, w0, _, _ = fixed_points(I, p)[0]
    return V0, w0


def rest_eigs(I, p):
    """Sorted eigenvalue pair of rest, or None above I_SN (class 1)."""
    rp = rest_point(I, p)
    return None if rp is None else sort_pair(np.linalg.eigvals(jac(*rp, I, p)))


def saddle_point(I, p=CONTROL):
    """(V*, w*) of the class 1 saddle, or None outside (I_BIRTH, I_SN)."""
    if not (I_BIRTH < I < I_SN):
        return None
    fps = fixed_points(I, p)
    if len(fps) < 3:
        return None
    return fps[1][0], fps[1][1]


def saddle_eigs(I, p=CONTROL):
    sp = saddle_point(I, p)
    return None if sp is None else sort_pair(np.linalg.eigvals(jac(*sp, I, p)))


def discriminant(I, p):
    """tr^2 - 4 det of rest's Jacobian: < 0 means a complex pair (a focus)."""
    J = jac(*rest_point(I, p), I, p)
    return np.trace(J) ** 2 - 4 * np.linalg.det(J)


def complex_window(p, lo, hi):
    """Currents in [lo, hi] where rest's pair leaves and rejoins the real axis."""
    Is = np.linspace(lo, hi, 800)
    d = np.array([discriminant(I, p) for I in Is])
    k = np.where(np.sign(d[:-1]) != np.sign(d[1:]))[0]
    return [brentq(lambda I: discriminant(I, p), Is[i], Is[i + 1], xtol=1e-8) for i in k]


def mpo_hz(lam):
    return abs(lam.imag) / (2 * np.pi) * 1000.0


def kick_modes(I, p, dV):
    """(lam, c) with deltaV(t) = sum_k c_k exp(lam_k t) for a kick of dV mV at rest.

    For a complex pair, c[1] = conj(c[0]): two counter-rotating phasors whose sum is real.
    """
    J = jac(*rest_point(I, p), I, p)
    lam, vec = np.linalg.eig(J)
    coef = np.linalg.solve(vec, np.array([dV, 0.0]))
    c = vec[0] * coef
    order = np.argsort(-lam.imag) if abs(lam[0].imag) > 1e-12 else np.argsort(-lam.real)
    return lam[order], c[order]


def lin_kick(I, p, dV, t):
    """Linearized deltaV(t) after a kick of dV mV from rest (t scalar or array, ms)."""
    lam, c = kick_modes(I, p, dV)
    t = np.asarray(t, dtype=float)
    return np.real(sum(ck * np.exp(lk * t) for lk, ck in zip(lam, c)))


def check_model():
    """The numbers the contract relies on (context_files/model.md)."""
    assert abs(I_SN - 38.7409) < 5e-4, I_SN
    assert abs(I_BIRTH - 37.68) < 0.01, I_BIRTH
    assert abs(I_HOPF - 114.2358) < 5e-4, I_HOPF

    # class 1: rest node -> brief overdamped focus -> node -> lambda = 0 at I_SN
    win = complex_window(CONTROL, 30.0, I_SN - 1e-3)
    assert len(win) == 2 and abs(win[0] - 35.62) < 0.02 and abs(win[1] - 38.64) < 0.02, win
    im_max = max(abs(rest_eigs(I, CONTROL)[0].imag) for I in np.linspace(win[0], win[1], 200))
    assert 0.08 < im_max < 0.09, im_max
    l = rest_eigs(38.0, CONTROL)
    assert abs(l[0] - (-0.362 + 0.083j)) < 2e-3, l
    s = saddle_eigs(38.0)
    assert abs(s[0] - 0.644) < 2e-3 and abs(s[1] + 0.084) < 2e-3, s
    near = I_SN - 1e-6
    lr, ls = rest_eigs(near, CONTROL), saddle_eigs(near)
    assert abs(lr[0]) < 0.01 and abs(ls[0]) < 0.01, (lr, ls)
    lr, ls = rest_eigs(38.74, CONTROL), saddle_eigs(38.74)
    assert abs(lr[0] - ls[0]) < 0.04 and abs(lr[1] - ls[1]) < 0.04, (lr, ls)
    assert rest_eigs(I_SN + 1e-3, CONTROL) is None and saddle_eigs(I_SN + 1e-3) is None
    assert saddle_eigs(I_BIRTH - 1e-3) is None

    # class 2: complex from ~86.4, crosses the imaginary axis at +-0.652i (103.8 Hz)
    win2 = complex_window(SHUNT, 60.0, 120.0)
    assert len(win2) == 1 and abs(win2[0] - 86.38) < 0.05, win2
    l = rest_eigs(112.5, SHUNT)
    assert abs(l[0] - (-0.0991 + 0.6343j)) < 1e-3 and abs(l[1] - l[0].conjugate()) < 1e-12, l
    l = rest_eigs(I_HOPF, SHUNT)
    assert abs(l[0].real) < 1e-5 and abs(l[0].imag - 0.6522) < 1e-3, l
    assert abs(mpo_hz(l[0]) - 103.8) < 0.1
    assert rest_eigs(115.0, SHUNT)[0].real > 0.04

    # tracking: sorted order never swaps between neighbouring grid steps (a swap would
    # make the moving x's jump across each other); branch points move like sqrt, so
    # compare against the swapped assignment rather than bounding the step size
    for p, lo, hi in ((CONTROL, 30.0, I_SN - 1e-4), (SHUNT, 80.0, 116.0)):
        L = np.array([rest_eigs(I, p) for I in np.linspace(lo, hi, 1500)])
        keep = np.abs(L[1:] - L[:-1]).sum(axis=1)
        swap = np.abs(L[1:] - L[:-1, ::-1]).sum(axis=1)
        assert np.all(keep <= swap + 1e-9)

    # linearization: a KICK_DV kick at 112.5 rings like c e^{lam t} + conj. The error is
    # second order (2.6% of the kick at 0.2 mV, 7% at 0.5 mV), hence the small kick
    V0, w0 = rest_point(112.5, SHUNT)
    t, V, _ = run(SHUNT, lambda s: 112.5, 0.0, 40.0, [V0 + KICK_DV, w0])
    err = np.abs(V - V0 - lin_kick(112.5, SHUNT, KICK_DV, t)).max()
    assert err < 0.03 * KICK_DV, err
    lam, c = kick_modes(112.5, SHUNT, KICK_DV)
    assert abs(c[1] - c[0].conjugate()) < 1e-9 and abs((c[0] + c[1]).real - KICK_DV) < 1e-9
    # beat 4: at I_Hopf the smaller kick keeps the sim dots on the linear circle (2.2%)
    V0, w0 = rest_point(I_HOPF, SHUNT)
    t, V, _ = run(SHUNT, lambda s: I_HOPF, 0.0, 30.0, [V0 + KICK_HOPF, w0])
    err = np.abs(V - V0 - lin_kick(I_HOPF, SHUNT, KICK_HOPF, t)).max()
    assert err < 0.03 * KICK_HOPF, err
    # class 1 at 38.0: complex but overdamped -> no visible undershoot
    V0, w0 = rest_point(38.0, CONTROL)
    t, V, _ = run(CONTROL, lambda s: 38.0, 0.0, 60.0, [V0 + KICK_DV, w0])
    assert (V - V0).min() > -0.005 * KICK_DV
    # class 1 beat 5: a KICK_DV kick at 38.73 (0.94 mV from the saddle) must not fire
    V0, w0 = rest_point(38.73, CONTROL)
    t, V, _ = run(CONTROL, lambda s: 38.73, 0.0, 200.0, [V0 + KICK_DV, w0])
    assert len(spikes(t, V)) == 0 and saddle_point(38.73)[0] - V0 > 0.9


# ---------------------------------------------------------------------------
# Phasor runs: one fixed current per run, a kick at t = 0, arrows k = c_k e^{lam_k t}.
# Everything is in units of the kick (u = deltaV / dV), so the plane's unit is the kick.
# ---------------------------------------------------------------------------

T_AXIS = 40.0      # ms shown on the time strip
DT_FINE = 0.05     # ms; curve and trail sampling
SIM_STEP = 0.5     # ms; simulated dots
I_C2 = 112.5
I_C1 = 38.7
I_C1_NEAR = 38.73


class KickRun:
    """Precomputed tables for one kick at one fixed current (pure numbers, no mobjects)."""

    def __init__(self, I, p, dV, t_end, color, sim=True):
        self.I, self.p, self.dV, self.t_end, self.color = I, p, dV, t_end, color
        self.lam, c = kick_modes(I, p, dV)
        self.z0 = c / dV                                      # arrows at t = 0, kick units
        self.t = np.arange(0.0, t_end + 1e-9, DT_FINE)
        self.Z = self.z0[None, :] * np.exp(self.lam[None, :] * self.t[:, None])
        self.u = lin_kick(I, p, dV, self.t) / dV              # the shadow (real part of the sum)
        self.ts = self.us = None
        if sim:
            V0, w0 = rest_point(I, p)
            t, V, _ = run(p, lambda s: I, 0.0, t_end, [V0 + dV, w0])
            self.ts = np.arange(0.0, t_end + 1e-9, SIM_STEP)
            self.us = (np.interp(self.ts, t, V) - V0) / dV

    def idx(self, T):
        return int(np.clip(round(T / DT_FINE), 0, len(self.t) - 1))

    def modes(self, T):
        return self.z0 * np.exp(self.lam * T)

    def sum(self, T):
        return self.modes(T).sum()

    def sim_err(self):
        return np.abs(self.us - lin_kick(self.I, self.p, self.dV, self.ts) / self.dV).max()


RUN_C2 = KickRun(I_C2, SHUNT, KICK_DV, T_AXIS, CLASS2_COLOR)
RUN_HOPF = KickRun(I_HOPF, SHUNT, KICK_HOPF, 20.0, CLASS2_COLOR)
# class 1 near I_SN: the linearization is 13.5% (38.7) / 39% (38.73) off the full model
# for a 0.2 mV kick, so class 1 is drawn without sim dots (see WORKBENCH.md)
RUN_C1 = KickRun(I_C1, CONTROL, KICK_DV, T_AXIS, CLASS1_COLOR, sim=False)
RUN_C1_NEAR = KickRun(I_C1_NEAR, CONTROL, KICK_DV, T_AXIS, CLASS1_COLOR, sim=False)

# lambda paths for the inset slides (rest eigenvalues along the current change)
LAM_PATH_C2 = (np.linspace(I_C2, I_HOPF, 41), np.array(
    [rest_eigs(I, SHUNT) for I in np.linspace(I_C2, I_HOPF, 41)]))
LAM_PATH_C1 = (np.linspace(I_C1, I_C1_NEAR, 21), np.array(
    [rest_eigs(I, CONTROL) for I in np.linspace(I_C1, I_C1_NEAR, 21)]))


def lam_on_path(path, I):
    Is, L = path
    return np.array([np.interp(I, Is, L[:, k].real) + 1j * np.interp(I, Is, L[:, k].imag)
                     for k in range(L.shape[1])])


def spin_hz(run_):
    return mpo_hz(run_.lam[0])


def efold_ms(lam):
    return -1.0 / lam.real


def fmt2(x):
    """Two significant figures, as the readouts print them."""
    return f"{float(f'{x:.2g}'):g}"


# ---------------------------------------------------------------------------
# Layout (frame 8.96 x 8 units; content inside +-4.2 x +-3.75)
# ---------------------------------------------------------------------------

TAG_ANCHOR = np.array([-4.15, 3.45, 0])
INSET_BOX = (2.4, 4.15, 2.0, 3.6)
EQ_POS = (np.array([-4.0, -2.3, 0]), np.array([-4.0, -2.9, 0]))      # left edges
READ_POS = (np.array([0.45, -2.3, 0]), np.array([0.45, -2.9, 0]))     # left edges
CAPTION_POS = np.array([0, -3.45, 0])
END_LABEL_POS = (np.array([-4.15, 1.75, 0]), np.array([0.25, 1.75, 0]))
END_SUB_POS = (np.array([-2.1, -2.55, 0]), np.array([2.2, -2.55, 0]))
ARROW_MIN = 0.05     # scene units; shorter arrows are hidden (tips degenerate)
ARROW_FULL = 0.15    # arrows fade in between ARROW_MIN and ARROW_FULL
CONJ_OPACITY = 0.6


class PhasorView:
    """Geometry of one phasor plane + time strip. Real axis vertical (Re up, +Im left).

    origin: the plane's 0 (and the strip's deltaV = 0 line); S: scene units per kick;
    strip: (x0, x1) for t = 0 .. T_AXIS; re: (lo, hi) and im: half-width of the drawn
    axes, in kicks; offset: sideways split of collinear arrows (class 1, schematic).
    """

    def __init__(self, origin, S, strip, re, im, offset=0.0, font=28):
        self.O = np.array([origin[0], origin[1], 0.0])
        self.S, self.strip, self.re, self.im = S, strip, re, im
        self.offset, self.font = offset, font

    def ph(self, z, dx=0.0):
        z = np.asarray(z, dtype=complex)
        pts = np.stack([-z.imag, z.real, np.zeros(z.shape)], axis=-1) * self.S + self.O
        return pts + dx * RIGHT

    def st(self, t, u):
        t, u = np.asarray(t, float), np.asarray(u, float)
        x0, x1 = self.strip
        return np.stack([x0 + t / T_AXIS * (x1 - x0), self.O[1] + self.S * u,
                         np.zeros(np.broadcast(t, u).shape)], axis=-1)


VIEW_C2 = PhasorView((-2.1, 0.0), 1.5, (-0.3, 4.05), (-1.25, 1.25), 0.95)
VIEW_C1 = PhasorView((-2.1, -1.6), 1.0, (-0.3, 4.05), (-0.25, 3.95), 0.95, offset=0.13)
MINI_C2 = PhasorView((-3.25, -0.25), 1.25, (-2.35, -0.25), (-1.15, 1.15), 0.68)
MINI_C1 = PhasorView((0.95, -1.65), 0.72, (1.75, 4.05), (-0.2, 4.0), 0.8, offset=0.11)
KICK_LABEL_U = (1.42, 1.75)  # kick-label height (kicks) in VIEW_C2 / VIEW_C1


def polyline(points):
    if len(points) < 2:
        points = np.array([points[0], points[0] + 1e-4 * RIGHT])
    return VMobject().set_points_as_corners(points)


# ---- chrome ----

def plane_chrome(view, labels=True):
    """Phasor axes (+ labels) and the strip's zero line (+ '40 ms')."""
    ax = VGroup(Line(view.ph(view.re[0]), view.ph(view.re[1])),
                Line(view.ph(1j * view.im), view.ph(-1j * view.im)),
                Line(view.st(0, 0), view.st(T_AXIS, 0)))
    ax.set_stroke(GREY_B, 2)
    ticks = VGroup(*[Line(view.st(t, 0) + 0.06 * DOWN, view.st(t, 0) + 0.06 * UP)
                     for t in (10, 20, 30, 40)]).set_stroke(GREY_B, 2)
    g = VGroup(ax, ticks)
    if labels:
        re_lab = tex(R"\mathrm{Re}\ ({=}\,\delta V)", font_size=view.font).set_color(GREY_B)
        re_lab.next_to(view.ph(view.re[1]), UP, buff=0.1)
        im_lab = tex(R"\mathrm{Im}", font_size=view.font).set_color(GREY_B)
        im_lab.next_to(view.ph(1j * view.im), LEFT, buff=0.1)
        t_lab = txt("40 ms", font_size=24).set_color(GREY_B)
        t_lab.next_to(view.st(T_AXIS, 0), DOWN, buff=0.12).align_to(view.st(T_AXIS, 0), RIGHT)
        g.add(re_lab, im_lab, t_lab)
    return g


def kick_marker(view, mv, label_u):
    """Vertical arrow at t = 0 on the strip, deltaV 0 -> the kick, labelled with its size.

    The label sits at label_u kicks (its bottom), above everything the run draws, so the
    curve and the guide line never cross it; a dotted leader joins it to the arrow.
    """
    a = Arrow(view.st(0, 0), view.st(0, 1), buff=0, thickness=2.5, fill_color=GREY_B)
    lab = txt(f"{mv:g} mV kick", font_size=24).set_color(GREY_B)
    lab.move_to(view.st(0, label_u), aligned_edge=DOWN).align_to(view.st(0, 0), LEFT)
    lab.shift(0.08 * LEFT)
    lead = DashedLine(view.st(0, 1), lab.get_bottom() * UP + view.st(0, 0) * RIGHT,
                      dash_length=0.05).set_stroke(GREY_B, 2)
    return VGroup(a, lead, lab)


# ---- content: pure functions of (run, view, model time T) ----

def phasor_arrow(a, b, color, opacity):
    L = np.linalg.norm(b - a)
    if L < ARROW_MIN:
        return Arrow(a, a + ARROW_MIN * UP, buff=0, fill_color=color, fill_opacity=0)
    op = opacity * min(1.0, (L - ARROW_MIN) / (ARROW_FULL - ARROW_MIN))
    return Arrow(a, b, buff=0, thickness=4, tip_width_ratio=4, fill_color=color,
                 fill_opacity=op)


def arrows(run_, view, T):
    """Tip-to-tail: arrow 1 from 0 to c1 e^{l1 T}, arrow 2 from there to the (real) sum."""
    z = run_.modes(T)
    d = view.offset
    a1 = phasor_arrow(view.ph(0, -d), view.ph(z[0], -d), run_.color, 1.0)
    a2 = phasor_arrow(view.ph(z[0], d), view.ph(z[0] + z[1], d), run_.color, CONJ_OPACITY)
    return VGroup(a2, a1)


def sum_dot(run_, view, T, radius=0.08):
    return Dot(view.ph(run_.sum(T).real), radius=radius, fill_color=STATE_COLOR)


def tip_trail(run_, view, T, recent_ms, full=False):
    i = run_.idx(T)
    pts = view.ph(run_.Z[:i + 1, 0])
    k = max(0, i - int(round(recent_ms / DT_FINE)))
    old = polyline(pts[:k + 1]).set_stroke(run_.color, TRAIL_STROKE,
                                           opacity=1.0 if full else TRAIL_OLD_OPACITY)
    new = polyline(pts[k:]).set_stroke(run_.color, TRAIL_STROKE)
    return VGroup(old, new)


def strip_curve(run_, view, T):
    i = run_.idx(T)
    return polyline(view.st(run_.t[:i + 1], run_.u[:i + 1])).set_stroke(WHITE, 3)


def pen_dot(run_, view, T):
    return Dot(view.st(T, run_.sum(T).real), radius=0.06, fill_color=STATE_COLOR)


def guide_line(run_, view, T):
    a = view.ph(run_.sum(T).real) + 0.1 * RIGHT
    b = view.st(T, run_.sum(T).real) + 0.08 * LEFT
    return DashedLine(a, b, dash_length=0.08).set_stroke(GREY_B, 2)


def sim_dots(run_, view):
    return VGroup(*[Dot(p, radius=0.04, fill_color=GREY_A) for p in view.st(run_.ts, run_.us)])


def envelope(run_, view):
    """Dashed +-2|c| e^{Re lam t}: the shrinking radius seen from the strip."""
    A = 2 * abs(run_.z0[0]) * np.exp(run_.lam[0].real * run_.t)
    return VGroup(*[DashedVMobject(polyline(view.st(run_.t, s * A)), num_dashes=45)
                    for s in (1, -1)]).set_stroke(GREY_B, 2)


def mode_labels(run_, view, T):
    """'slow' / 'fast' beside the two collinear class 1 arrows (hidden once short)."""
    z = run_.modes(T)
    g = VGroup()
    for k, (a, b, side, word) in enumerate(((0, z[0], LEFT, "slow"),
                                            (z[0], z[0] + z[1], RIGHT, "fast"))):
        L = abs(b - a) * view.S
        lab = txt(word, font_size=24).set_color(run_.color)
        mid = view.ph((a + b) / 2, (-1 if k == 0 else 1) * view.offset)
        lab.next_to(mid, side, buff=0.12)
        lab.set_opacity(float(np.clip((L - 0.4) / 0.3, 0, 1)))
        g.add(lab)
    return g


def lam_marks(plane, lams, color):
    return VGroup(*[lam_cross(plane.l2p(l), color) for l in lams])


# ---- text ----

EQ1 = R"\delta V(t) = c\,e^{\lambda t} + \bar c\,e^{\bar\lambda t}"
EQ1_C1 = R"\delta V(t) = c_1\,e^{\lambda_1 t} + c_2\,e^{\lambda_2 t}"
EQ2_SHRINK = R"e^{\mathrm{Re}\,\lambda\,t}"
EQ2_SPIN = R"e^{i\,\mathrm{Im}\,\lambda\,t}"
EQ2 = R"e^{\lambda t} = " + EQ2_SHRINK + R"\," + EQ2_SPIN
EQ_FONT = 32
READ_FONT = 28


def readout_spin(run_):
    if abs(run_.lam[0].imag) < 1e-12:
        return R"\text{spin} = \mathrm{Im}\,\lambda = 0"
    return R"\text{spin} = \mathrm{Im}\,\lambda\ \to\ %.0f\ \text{Hz}" % spin_hz(run_)


def readout_shrink(run_):
    if abs(run_.lam[0].real) < 1e-6:
        return R"\text{shrink} = \mathrm{Re}\,\lambda = 0"
    vals = sorted({fmt2(efold_ms(l)) for l in run_.lam}, key=float, reverse=True)
    return R"\text{shrink} = \mathrm{Re}\,\lambda\ \to\ %s\ \text{ms}" % R",\ ".join(vals)


def readouts(run_):
    g = VGroup(tex(readout_spin(run_), font_size=READ_FONT),
               tex(readout_shrink(run_), font_size=READ_FONT))
    for m, p in zip(g, READ_POS):
        m.move_to(p, aligned_edge=LEFT)
    return g


def tag_for(p):
    s, c = ("Class 2 · Hopf", CLASS2_COLOR) if p is SHUNT else ("Class 1 · SNIC", CLASS1_COLOR)
    return txt(s, font_size=32).set_color(c).move_to(TAG_ANCHOR, aligned_edge=LEFT)


def caption(s, math=False):
    m = tex(s, font_size=36) if math else txt(s, font_size=36)
    return m.move_to(CAPTION_POS)


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class EigenvaluePhasorRinging(Scene):
    """The e^{lambda t} phasor behind the ringing. See the module docstring."""

    def construct(self):
        self.first_frame()
        self.spin_and_shrink()
        self.split_lambda()
        self.to_hopf()
        self.class1()
        self.end_frame()

    # -- helpers ----------------------------------------------------------

    def live(self, run_, view, trail=True, dots=True, recent_ms=7.3):
        """Tracker-driven mobjects for one run. Returns a dict; self.T is model time."""
        T = self.T.get_value
        L = dict(
            guide=always_redraw(lambda: guide_line(run_, view, T())),
            curve=always_redraw(lambda: strip_curve(run_, view, T())),
            arrows=always_redraw(lambda: arrows(run_, view, T())),
            sum=always_redraw(lambda: sum_dot(run_, view, T())),
            pen=always_redraw(lambda: pen_dot(run_, view, T())),
        )
        if trail:
            L["trail"] = always_redraw(lambda: tip_trail(run_, view, T(), recent_ms))
        if view.offset > 0:
            L["labels"] = always_redraw(lambda: mode_labels(run_, view, T()))
        if dots and run_.ts is not None:
            d = sim_dots(run_, view)
            ts = run_.ts

            def show(m):
                now = T()
                for dot, t in zip(m, ts):
                    dot.set_fill(opacity=1.0 if t <= now + 1e-9 else 0.0)
            d.add_updater(show)
            L["dots"] = d
        return L

    def add_live(self, L):
        order = ("guide", "trail", "curve", "dots", "arrows", "labels", "sum", "pen")
        self.add(*[L[k] for k in order if k in L])

    @staticmethod
    def freeze(L):
        for m in L.values():
            m.clear_updaters()

    # -- beats ------------------------------------------------------------

    def first_frame(self):
        ## Beat 1: first frame, class 2 at 112.5, arrows at t = 0, inset lambda
        self.T = ValueTracker(0.0)
        self.I = ValueTracker(I_C2)
        self.tag = tag_for(SHUNT)
        self.inset = LamPlane(INSET_BOX)
        self.lam2 = always_redraw(lambda: lam_marks(
            self.inset, lam_on_path(LAM_PATH_C2, self.I.get_value()), CLASS2_COLOR))
        self.chrome = plane_chrome(VIEW_C2)
        self.kick = kick_marker(VIEW_C2, KICK_DV, KICK_LABEL_U[0])
        self.L = self.live(RUN_C2, VIEW_C2, recent_ms=T_AXIS / 5.5 * TRAIL_RECENT_S)
        self.add(self.chrome, self.kick, self.inset, self.lam2, self.tag)
        self.add_live(self.L)
        self.wait(1.2)

    def spin_and_shrink(self):
        ## Beat 2: arrows spin and shrink, the shadow draws deltaV(t) over the sim dots
        self.eq1 = tex(EQ1, font_size=EQ_FONT).move_to(EQ_POS[0], aligned_edge=LEFT)
        self.env = envelope(RUN_C2, VIEW_C2)
        self.play(self.T.animate.set_value(18.0),
                  FadeIn(self.eq1, rate_func=squish_rate_func(smooth, 0.0, 0.3)),
                  run_time=2.5, rate_func=linear)
        self.play(self.T.animate.set_value(T_AXIS),
                  FadeIn(self.env, rate_func=squish_rate_func(smooth, 0.0, 0.25)),
                  run_time=3.0, rate_func=linear)

    def split_lambda(self):
        ## Beat 3: freeze; split lambda into spin (Im -> Hz) and shrink (Re -> ms)
        self.freeze(self.L)
        self.eq2 = tex(EQ2, font_size=EQ_FONT, isolate=[EQ2_SHRINK, EQ2_SPIN])
        self.eq2.move_to(EQ_POS[1], aligned_edge=LEFT)
        self.read = readouts(RUN_C2)
        O = VIEW_C2.O
        r = 0.95 * VIEW_C2.S * abs(RUN_C2.z0[0]) + 0.25
        self.spin_arc = Arc(start_angle=100 * DEG, angle=100 * DEG, radius=r, arc_center=O)
        self.spin_arc.set_stroke(FLASH_COLOR, 4).add_tip(width=0.22, length=0.22)
        th = 235 * DEG
        dirv = np.array([np.cos(th), np.sin(th), 0])
        r0 = VIEW_C2.S * abs(RUN_C2.z0[0])
        self.shrink_arrow = Arrow(O + (r0 + 0.12) * dirv, O + 0.2 * dirv, buff=0,
                                  thickness=3.5, fill_color=FLASH_COLOR)
        box = SurroundingRectangle(self.eq2[EQ2_SPIN], buff=0.06).set_stroke(FLASH_COLOR, 3)
        box2 = SurroundingRectangle(self.eq2[EQ2_SHRINK], buff=0.06).set_stroke(FLASH_COLOR, 3)
        self.play(Write(self.eq2), run_time=0.6)
        self.play(ShowCreation(box), ShowCreation(self.spin_arc), run_time=0.5)
        self.play(FadeIn(self.read[0], shift=0.1 * UP), run_time=0.35)
        self.play(Transform(box, box2), GrowArrow(self.shrink_arrow),
                  self.env.animate.set_stroke(FLASH_COLOR), run_time=0.5)
        self.play(FadeIn(self.read[1], shift=0.1 * UP), run_time=0.35)
        self.wait(0.2)
        self.box = box

    def to_hopf(self):
        ## Beat 4: lambda slides to the axis, fresh 0.1 mV kick at I_Hopf, arrows keep length
        old = VGroup(*self.L.values(), self.env, self.spin_arc, self.shrink_arrow, self.box)
        new_read = readouts(RUN_HOPF)
        new_kick = kick_marker(VIEW_C2, KICK_HOPF, KICK_LABEL_U[0])
        self.play(FadeOut(old), self.I.animate.set_value(I_HOPF),
                  FadeTransform(self.read, new_read), FadeTransform(self.kick, new_kick),
                  run_time=0.9)
        self.remove(old)
        self.read, self.kick = new_read, new_kick
        self.T.set_value(0.0)
        self.L = self.live(RUN_HOPF, VIEW_C2, recent_ms=20.0 / 2.3 * TRAIL_RECENT_S)
        self.play(*[FadeIn(self.L[k]) for k in ("arrows", "sum", "pen", "guide")],
                  run_time=0.3)
        self.add_live(self.L)
        self.cap = caption("at the crossing it is already spinning")
        self.play(self.T.animate.set_value(RUN_HOPF.t_end),
                  FadeIn(self.cap, rate_func=squish_rate_func(smooth, 0.0, 0.25)),
                  run_time=2.3, rate_func=linear)

    def class1(self):
        ## Beat 5: class 1, collinear real arrows, relaxation; lambda -> 0, slow arrow lingers
        self.freeze(self.L)
        self.lam2.clear_updaters()
        self.T.set_value(0.0)
        self.I.set_value(I_C1)
        self.lam1 = always_redraw(lambda: lam_marks(
            self.inset, lam_on_path(LAM_PATH_C1, self.I.get_value()), CLASS1_COLOR))
        chrome1 = plane_chrome(VIEW_C1)
        kick1 = kick_marker(VIEW_C1, KICK_DV, KICK_LABEL_U[1])
        L1 = self.live(RUN_C1, VIEW_C1, trail=False)
        eq1 = tex(EQ1_C1, font_size=EQ_FONT).move_to(EQ_POS[0], aligned_edge=LEFT)
        cap = caption(R"\mathrm{Im}\,\lambda = 0\ \to\ \text{nothing to ring with}",
                      math=True)
        tag1 = tag_for(CONTROL)
        read1 = readouts(RUN_C1)
        # a cut: class 2 out, then class 1 in (cross-fading two planes reads as clutter)
        old = VGroup(*self.L.values(), self.chrome, self.kick, self.lam2, self.cap, self.tag,
                     self.eq1, self.read)
        self.play(FadeOut(old), run_time=0.3)
        self.remove(old)
        self.play(FadeIn(chrome1), FadeIn(kick1), FadeIn(self.lam1), FadeIn(tag1),
                  *[FadeIn(L1[k]) for k in ("arrows", "labels", "sum", "pen", "guide")],
                  FadeIn(eq1), FadeIn(read1), run_time=0.35)
        self.add_live(L1)
        self.tag, self.eq1, self.chrome, self.kick, self.cap = tag1, eq1, chrome1, kick1, cap
        self.read = read1
        self.play(self.T.animate.set_value(T_AXIS),
                  FadeIn(cap, rate_func=squish_rate_func(smooth, 0.0, 0.25)),
                  run_time=2.4, rate_func=linear)
        # lambda -> 0: fresh kick at 38.73, the first relaxation kept faint
        self.freeze(L1)
        faint = L1["curve"]
        gone = VGroup(*[L1[k] for k in ("arrows", "labels", "sum", "pen", "guide")])
        self.T.set_value(0.0)
        L2 = self.live(RUN_C1_NEAR, VIEW_C1, trail=False)
        read2 = readouts(RUN_C1_NEAR)
        self.play(FadeOut(gone), faint.animate.set_stroke(opacity=0.3),
                  self.I.animate.set_value(I_C1_NEAR),
                  FadeOut(self.read[1]), FadeIn(read2[1]),
                  *[FadeIn(L2[k]) for k in ("arrows", "labels", "sum", "pen", "guide")],
                  run_time=0.6)
        self.remove(gone, self.read[1])
        self.read = VGroup(self.read[0], read2[1])
        self.add_live(L2)
        self.play(self.T.animate.set_value(T_AXIS), run_time=2.4, rate_func=linear)
        self.freeze(L2)
        self.L1, self.L2 = L1, L2

    def end_frame(self):
        ## Beat 6: end frame, class 2 spiral + damped cosine vs class 1 flat arrows + relaxation
        # right panel: class 1 at 38.7, the arrows at t = 0 (they never turn) + relaxation
        c1_chrome = plane_chrome(MINI_C1, labels=False)
        c1_curve = strip_curve(RUN_C1, MINI_C1, T_AXIS)
        c1_marks = VGroup(arrows(RUN_C1, MINI_C1, 0.0), mode_labels(RUN_C1, MINI_C1, 0.0),
                          sum_dot(RUN_C1, MINI_C1, 0.0, radius=0.07))
        # left panel: class 2 at 112.5, the tip's inward spiral + damped cosine
        c2 = VGroup(plane_chrome(MINI_C2, labels=False),
                    tip_trail(RUN_C2, MINI_C2, T_AXIS, 0.0, full=True),
                    strip_curve(RUN_C2, MINI_C2, T_AXIS))
        lab2 = txt("Class 2 · Hopf", font_size=30).set_color(CLASS2_COLOR)
        lab2.move_to(END_LABEL_POS[0], aligned_edge=LEFT)
        lab1 = txt("Class 1 · SNIC", font_size=30).set_color(CLASS1_COLOR)
        lab1.move_to(END_LABEL_POS[1], aligned_edge=LEFT)
        sub2 = tex(R"\mathrm{Im}\,\lambda/2\pi = %.0f\ \text{Hz}" % spin_hz(RUN_C2),
                   font_size=30).set_color(CLASS2_COLOR).move_to(END_SUB_POS[0])
        sub1 = tex(R"\mathrm{Im}\,\lambda = 0", font_size=30).set_color(CLASS1_COLOR)
        sub1.move_to(END_SUB_POS[1])
        cap = caption(R"\text{MPO frequency} = \text{spin rate} = \mathrm{Im}\,\lambda / 2\pi",
                      math=True)
        lam2 = lam_marks(self.inset, RUN_C2.lam, CLASS2_COLOR)
        L1, L2 = self.L1, self.L2
        gone = VGroup(*L1.values(), *L2.values(), self.chrome, self.kick, self.eq1, self.eq2,
                      self.read, self.cap, self.tag)
        self.play(FadeOut(gone), run_time=0.4)
        self.remove(gone)
        self.play(FadeIn(VGroup(c1_chrome, c1_curve, c1_marks, lab1)),
                  FadeIn(VGroup(c2, lab2)), FadeIn(lam2), self.I.animate.set_value(I_C1),
                  run_time=0.6)
        self.lam1.clear_updaters()
        self.play(FadeIn(VGroup(sub1, sub2)), FadeIn(cap), run_time=0.5)
        self.wait(2.9)


def check_scene():
    """Every number the scene draws (contract section 10)."""
    runs = (RUN_C2, RUN_HOPF, RUN_C1, RUN_C1_NEAR)
    # the two arrows' sum stays on the real axis on every sample
    for r in runs:
        assert np.abs(r.Z.sum(axis=1).imag).max() < 1e-9
        assert np.abs(r.Z.sum(axis=1).real - r.u).max() < 1e-9
        assert abs(r.sum(0.0) - 1.0) < 1e-9                   # the sum starts at the kick
    # class 2 at 112.5: conjugate arrows 0.570 kicks (0.114 mV) at -+28.7 deg, period 9.90 ms,
    # e-fold 10.1 ms
    z = RUN_C2.z0
    assert abs(z[1] - z[0].conjugate()) < 1e-9
    assert abs(abs(z[0]) * KICK_DV - 0.114) < 5e-4
    assert abs(np.degrees(np.angle(z[0])) + 28.66) < 0.05
    assert abs(TAU / RUN_C2.lam[0].imag - 9.90) < 0.01
    assert abs(efold_ms(RUN_C2.lam[0]) - 10.09) < 0.01
    # readouts: spin 101 Hz / shrink 10 ms, then 104 Hz / Re = 0, class 1: 0 / 8.7, 4.2 / 17, 4.3
    assert "101" in readout_spin(RUN_C2) and R"10\ " in readout_shrink(RUN_C2)
    assert f"{mpo_hz(RUN_C2.lam[0]):.0f}" == "101" and fmt2(efold_ms(RUN_C2.lam[0])) == "10"
    assert "104" in readout_spin(RUN_HOPF) and "= 0" in readout_shrink(RUN_HOPF)
    assert abs(RUN_HOPF.lam[0].real) < 1e-6
    assert "= 0" in readout_spin(RUN_C1) and "8.7,\\ 4.2" in readout_shrink(RUN_C1)
    assert "17,\\ 4.3" in readout_shrink(RUN_C1_NEAR)
    # beat 4: same size on screen (plane unit = kick): |c|/kick 0.599 vs 0.570
    assert abs(abs(RUN_HOPF.z0[0]) / abs(RUN_C2.z0[0]) - 1) < 0.06
    # the Hopf circle does not shrink over the 20 ms shown
    assert np.ptp(np.abs(RUN_HOPF.Z[:, 0])) < 1e-6
    # sim dots within 3% of the kick: 2.6% at 112.5 (40 ms), 2.2% at I_Hopf (20 ms)
    assert RUN_C2.sim_err() < 0.03 and abs(RUN_C2.sim_err() - 0.026) < 0.002
    assert RUN_HOPF.sim_err() < 0.03 and abs(RUN_HOPF.sim_err() - 0.022) < 0.002
    # class 1: real modes +0.775 / -0.575 mV that never leave the real axis
    for r in (RUN_C1, RUN_C1_NEAR):
        assert np.all(r.lam.imag == 0) and np.abs(r.Z.imag).max() < 1e-12
        assert r.z0[0] > 0 > r.z0[1]                          # slow up, fast down
        assert np.all(r.u > 0)                                # no undershoot (linear)
    assert abs(RUN_C1.z0[0] * KICK_DV - 0.775) < 1e-3 and abs(RUN_C1.z0[1] * KICK_DV + 0.575) < 1e-3
    assert abs(RUN_C1.lam[0] + 0.116) < 1e-3 and abs(RUN_C1.lam[1] + 0.239) < 1e-3
    # not monotone: the fast (negative) arrow dies first, so deltaV rises to 1.34 kicks
    # (3.5 ms) before relaxing; the full model agrees qualitatively (no undershoot)
    assert abs(RUN_C1.u.max() - 1.34) < 0.01 and abs(RUN_C1_NEAR.u.max() - 1.61) < 0.01
    for I in (I_C1, I_C1_NEAR):
        V0, w0 = rest_point(I, CONTROL)
        t, V, _ = run(CONTROL, lambda s, I=I: I, 0.0, T_AXIS, [V0 + KICK_DV, w0])
        assert (V - V0).min() > 0 and len(spikes(t, V)) == 0
    # the inset slides end where the runs are
    assert np.abs(lam_on_path(LAM_PATH_C2, I_HOPF) - RUN_HOPF.lam).max() < 1e-6
    assert np.abs(lam_on_path(LAM_PATH_C1, I_C1_NEAR) - RUN_C1_NEAR.lam).max() < 1e-6
    # everything drawn fits its view and the frame (+-4.2 x +-3.75)
    for r, v in ((RUN_C2, VIEW_C2), (RUN_HOPF, VIEW_C2), (RUN_C1, VIEW_C1),
                 (RUN_C1_NEAR, VIEW_C1), (RUN_C2, MINI_C2), (RUN_C1, MINI_C1)):
        assert v.re[0] <= r.u.min() and r.u.max() <= v.re[1], (r.I, r.u.min(), r.u.max())
        tips = np.concatenate([r.Z[:, 0], r.Z.sum(axis=1)])
        assert np.all(np.abs(tips.imag) <= v.im) and np.all(tips.real <= v.re[1])
        assert np.all(np.abs(r.Z[:, 0].real) <= v.re[1])
        for pts in (v.ph(tips), v.st(r.t, r.u)):
            assert np.all(np.abs(pts[:, 0]) < 4.2) and np.all(np.abs(pts[:, 1]) < 3.75)


if __name__ == "__main__":
    check_model()
    check_scene()
    print("ok")
