"""Class 2: the whirlpool lets go.

Contract: context_files/contract.md. Render: -w -r 1344x1200 (8.96 x 8 units), 19.27 s.

Everything moving is driven by one ValueTracker, model time T (ms): nullclines at I(T),
focus dot, state point, trail, V(t), current strip, kick marks and both zoom windows are
redrawn from the single precomputed SHUNT run. 1 video s = 20 ms, 10 ms during the escape.

Beats as built (video s | model ms):
1. 0.0-1.0    | 0        Still: focus window, nullclines at I = 110, filled focus with the
                           state on it, tag; V(t) and current pens at their start.
2. 1.0-2.25   | 0-25     Kick 1 (+1.2 mV, dashed red arrow, red triangle + "kick"):
                           barely one overshoot.
3. 2.25-5.0   | 25-80    Current to 112.5; kick 2 at 50 ms spirals in ~3 turns;
                           "rings at ~100 Hz" fades in from 4.0 s.
4. 5.0-9.25   | 80-165   Current to 114; kick 3 at 105 ms: ringing barely decays.
5. 9.25-9.81  | 165-168.23, hold 0.4 s  Hopf crossing: focus turns open, red ring flash.
6. 9.81-12.65 | 168.23-210  Ring grows; 195-210 ms at half speed both windows zoom out
                           (2 mV bar -> 20 mV); state jumps onto the big loop; spike at 203.9.
7. 12.65-15.15| 210-260  Repetitive spiking, ISI 8.95 ms; "fires at ~110 spikes/s" from 13.3 s.
8. 15.15-16.15| hold     Caption "already turning when it lets go" writes in.
9. 16.15-19.15| hold     End frame (contract section 6).
"""

from common import *

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# ---------------------------------------------------------------------------
# Model: the paper's modified Morris-Lecar, SHUNT set (g_shunt = 4, g_M = 0).
# Reference implementation from context_files/model.md.
# ---------------------------------------------------------------------------

BASE = dict(C=2.0, ENa=50.0, EK=-100.0, Esh=-70.0, gNa=20.0, gK=20.0, gsh=2.0, phi=0.25,
            bm=-1.2, gm=18.0, bw=-9.0, gw=10.0, gM=0.0, bz=-30.0, gz=5.0)
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


def fixed_points(I, p, z=0.0):
    g = lambda V: I - (I_fixed(V, p, z) + p['gK'] * winf(V, p) * (V - p['EK']))
    Vs = np.linspace(-90, 20, 4000)
    gv = g(Vs)
    out = []
    for i in np.where(np.sign(gv[:-1]) != np.sign(gv[1:]))[0]:
        V0 = brentq(g, Vs[i], Vs[i + 1])
        w0 = winf(V0, p)
        h = 1e-5
        J = np.column_stack([
            (np.array(f2(V0 + h, w0, I, p, z)) - f2(V0 - h, w0, I, p, z)) / (2 * h),
            (np.array(f2(V0, w0 + h, I, p, z)) - f2(V0, w0 - h, I, p, z)) / (2 * h)])
        out.append((V0, w0, z, np.linalg.eigvals(J)))
    return out


def run(p, I_of_t, t0, t1, y0):
    s = solve_ivp(lambda t, y: f2(y[0], y[1], I_of_t(t), p), (t0, t1), y0,
                  method='LSODA', max_step=0.02, rtol=1e-9, atol=1e-11)
    return s.t, s.y[0], s.y[1]


def spikes(t, V):
    k = np.where((V[:-1] < 0) & (V[1:] >= 0))[0]
    return t[k]


def hopf_current(p=SHUNT):
    """Current at which the rest focus loses stability (max Re lambda = 0)."""
    return brentq(lambda I: fixed_points(I, p)[0][3].real.max(), 105, 120, xtol=1e-8)


# --- schedule (model.md "Schedule") --------------------------------

RAMPS = [(25.0, 45.0, 110.0, 112.5), (80.0, 100.0, 112.5, 114.0), (165.0, 175.0, 114.0, 115.0)]
KICKS = [5.0, 50.0, 105.0]
KICK_DV = 1.2
T_END = 260.0
V0_REST, W0_REST = -34.0253, 0.006659


def I_of_t(t):
    """Cosine-ramp current schedule, scalar or array (uA/cm^2)."""
    t = np.asarray(t, dtype=float)
    I = np.full_like(t, RAMPS[0][2])
    for a, b, I0, I1 in RAMPS:
        s = np.clip((t - a) / (b - a), 0, 1)
        ramp = I0 + (I1 - I0) * 0.5 * (1 - np.cos(np.pi * s))
        I = np.where(t >= a, ramp, I)
    return I if I.ndim else float(I)


def simulate():
    """The one deterministic run: segments between kicks. Returns t, V, w, seg."""
    edges = [0.0] + KICKS + [T_END]
    y = [V0_REST, W0_REST]
    ts, Vs, ws, segs = [], [], [], []
    for k in range(len(edges) - 1):
        if k > 0:
            y = [y[0] + KICK_DV, y[1]]
        t, V, w = run(SHUNT, lambda s: I_of_t(s), edges[k], edges[k + 1], y)
        ts.append(t); Vs.append(V); ws.append(w); segs.append(np.full(len(t), k))
        y = [V[-1], w[-1]]
    return np.concatenate(ts), np.concatenate(Vs), np.concatenate(ws), np.concatenate(segs)


def focus_table(I_grid, p=SHUNT):
    """Rest fixed point (V*, w*) and max Re lambda along a current grid."""
    rows = [fixed_points(I, p)[0] for I in I_grid]
    return (np.array([r[0] for r in rows]), np.array([r[1] for r in rows]),
            np.array([r[3].real.max() for r in rows]))


def ring_peaks(t, V, seg, k, n=3):
    """Heights of the first n local maxima of V above the local focus after kick k."""
    m = seg == k + 1
    tt, VV = t[m], V[m]
    Vstar = fixed_points(I_of_t(tt[0]), SHUNT)[0][0]
    i = np.where((VV[1:-1] > VV[:-2]) & (VV[1:-1] >= VV[2:]))[0] + 1
    return tt[i[:n]] - tt[0], VV[i[:n]] - Vstar


# Precomputed once at import (a few seconds).
I_HOPF = hopf_current()
SIM_T, SIM_V, SIM_W, SIM_SEG = simulate()
T_HOPF = brentq(lambda s: I_of_t(s) - I_HOPF, 165.0, 175.0)
FOCUS_I = np.linspace(109.9, 115.1, 521)
FOCUS_V, FOCUS_W, FOCUS_RE = focus_table(FOCUS_I)


# ---------------------------------------------------------------------------
# Display: layout boxes (contract section 4), hidden phase-plane warp, clipping.
# ---------------------------------------------------------------------------

# Phase plane: plot area inside the box x [-4.15, 0.05] x y [-2.45, 2.95]
PX0, PX1, PY0, PY1 = -3.70, 0.0, -2.05, 2.80
# V(t): time 0-260 ms across x; data rows above the scale-bar strip
VX0, VX1, VY0, VY1 = 0.45, 4.15, -0.55, 2.95
VT_ZOOM, VT_FULL = (-36.0, -24.0), (-80.0, 30.0)
# Current strip
IY0, IY1, I_LO, I_HI = -2.22, -1.62, 110.0, 115.0

T_ZOOM0, T_ZOOM1 = 195.0, 210.0      # both windows zoom out over this model-time span
TRAIL_RECENT = 15.0                  # ms of trail drawn fully opaque
KICK_SHOW = 8.0                      # ms (0.4 s at 20 ms/s) the kick arrow stays up
OLD_OPACITY = 0.35


def warp_x(V):
    return np.arcsinh((np.asarray(V) + 36.0) / 8.0)


def warp_y(w):
    return np.power(np.maximum(np.asarray(w, dtype=float), 0.0), 0.4)


WIN_FOCUS = np.array([warp_x(-40), warp_x(-24), warp_y(0.004), warp_y(0.026)])
WIN_FULL = np.array([warp_x(-78), warp_x(30), warp_y(0.0), warp_y(0.36)])


def zoom_of_t(T):
    """0 = focus window / zoomed V(t), 1 = full window; eased over 195-210 ms."""
    return float(smooth(np.clip((T - T_ZOOM0) / (T_ZOOM1 - T_ZOOM0), 0.0, 1.0)))


def pp_xy(V, w, a):
    """Model (V, w) -> screen (x, y) in the phase-plane box at zoom a."""
    x0, x1, y0, y1 = (1 - a) * WIN_FOCUS + a * WIN_FULL
    X = PX0 + (warp_x(V) - x0) / (x1 - x0) * (PX1 - PX0)
    Y = PY0 + (warp_y(w) - y0) / (y1 - y0) * (PY1 - PY0)
    return X, Y


def vt_range(a):
    lo = (1 - a) * VT_ZOOM[0] + a * VT_FULL[0]
    hi = (1 - a) * VT_ZOOM[1] + a * VT_FULL[1]
    return lo, hi


def vt_xy(t, V, a):
    lo, hi = vt_range(a)
    return (VX0 + np.asarray(t) / T_END * (VX1 - VX0),
            VY0 + (np.asarray(V) - lo) / (hi - lo) * (VY1 - VY0))


def runs(mask):
    """(start, stop) index pairs of the True runs in a boolean array."""
    m = np.concatenate([[False], mask, [False]]).astype(int)
    d = np.diff(m)
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def clipped_polylines(X, Y, box, extra_mask=None):
    """Split a polyline into the pieces inside box = (x0, x1, y0, y1)."""
    x0, x1, y0, y1 = box
    eps = 1e-3
    m = (X >= x0 - eps) & (X <= x1 + eps) & (Y >= y0 - eps) & (Y <= y1 + eps)
    if extra_mask is not None:
        m &= extra_mask
    out = []
    for i, j in runs(m):
        x, y = X[i:j], Y[i:j]
        # thin by screen arc length so a resting state is not a pile of points
        s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
        keep = np.concatenate([[True], np.diff(np.floor(s / 0.004)) > 0])
        keep[-1] = True
        x, y = x[keep], y[keep]
        if len(x) >= 2 and s[-1] > 0.01:
            out.append(np.column_stack([x, y, np.zeros(len(x))]))
    return out


def polyline_group(pieces, color, width, opacity=1.0):
    g = VGroup()
    for pts in pieces:
        g.add(VMobject().set_points_as_corners(pts).set_stroke(color, width, opacity))
    return g


def state_at(T):
    """Interpolated (V, w) at model time T (right-continuous at kicks)."""
    i = np.searchsorted(SIM_T, T, side="right")
    i = int(np.clip(i, 1, len(SIM_T) - 1))
    t0, t1 = SIM_T[i - 1], SIM_T[i]
    s = 0.0 if t1 == t0 else (T - t0) / (t1 - t0)
    return (SIM_V[i - 1] + s * (SIM_V[i] - SIM_V[i - 1]),
            SIM_W[i - 1] + s * (SIM_W[i] - SIM_W[i - 1]))


def focus_at(T):
    I = I_of_t(T)
    return np.interp(I, FOCUS_I, FOCUS_V), np.interp(I, FOCUS_I, FOCUS_W), I >= I_HOPF


NULL_V = 8.0 * np.sinh(np.linspace(warp_x(-80), warp_x(32), 1600)) - 36.0
PP_BOX = (PX0, PX1, PY0, PY1)
VT_BOX = (VX0, VX1, VY0, VY1)


class Class2HopfOnset(Scene):
    def construct(self):
        self.T = ValueTracker(0.0)
        self.static_frame()
        self.dynamic_layers()
        self.opening()
        self.kick_at_110()
        self.kick_at_112()
        self.kick_at_114()
        self.hopf_crossing()
        self.escape()
        self.spiking()
        self.caption_and_hold()

    # --- helpers ---------------------------------------------------------
    def t(self):
        return self.T.get_value()

    def a(self):
        return zoom_of_t(self.t())

    def advance(self, T1, *anims, rate=20.0):
        """Advance model time to T1 at `rate` ms per video second."""
        dt = (T1 - self.t()) / rate
        self.play(self.T.animate.set_value(T1), *anims, run_time=dt, rate_func=linear)

    # --- static chrome ---------------------------------------------------
    def static_frame(self):
        tag = txt("Class 2 · Hopf", font_size=32).set_color(ORANGE)
        tag.move_to([-4.15, 3.45, 0], aligned_edge=LEFT)

        axes = VGroup(
            Line([PX0, PY0, 0], [PX1, PY0, 0]),
            Line([PX0, PY0, 0], [PX0, PY1, 0]),
        ).set_stroke(GREY_B, 2)
        v_lab = txt("V", font_size=30).set_color(GREY_B).next_to([PX1, PY0, 0], DOWN, buff=0.12)
        v_lab.align_to([PX1, 0, 0], RIGHT)
        w_lab = txt("w", font_size=30).set_color(GREY_B).next_to([PX0, PY1, 0], LEFT, buff=0.15)
        w_lab.align_to([0, PY1, 0], UP)
        k_lab = txt("K⁺ activation", font_size=24).set_color(GREY_B).rotate(PI / 2)
        k_lab.next_to([PX0, 0, 0], LEFT, buff=0.15).set_y(0.9)

        self.hbar = Line([4.12 - 10 / T_END * (VX1 - VX0), -1.0, 0], [4.12, -1.0, 0]).set_stroke(GREY_B, 3)
        ms_lab = txt("10 ms", font_size=24).set_color(GREY_B).next_to(self.hbar, DOWN, buff=0.1)
        ms_lab.align_to([4.15, 0, 0], RIGHT)

        cur_lab = txt("current", font_size=24).set_color(GREY_B)
        cur_lab.move_to([VX0, -1.72, 0], aligned_edge=LEFT)

        self.readout1 = txt("rings at ≈ 100 Hz", font_size=30).set_color(ORANGE)
        self.readout1.move_to([4.15, 3.45, 0], aligned_edge=RIGHT)
        self.readout2 = txt("fires at ≈ 110 spikes/s", font_size=30).set_color(WHITE)
        self.readout2.next_to(self.readout1, DOWN, buff=0.18).align_to(self.readout1, RIGHT)
        self.caption = txt("already turning when it lets go", font_size=40).set_color(WHITE)
        self.caption.move_to([0, -3.3, 0])

        self.add(tag, axes, v_lab, w_lab, k_lab, self.hbar, ms_lab, cur_lab)

    # --- everything driven by model time T ---------------------------------
    def dynamic_layers(self):
        def nullclines():
            Tn, a = self.t(), self.a()
            I = I_of_t(Tn)
            wv = V_null(NULL_V, I, SHUNT)
            X, Y = pp_xy(NULL_V, wv, a)
            vn = polyline_group(clipped_polylines(X, Y, PP_BOX, wv > 1e-6), GREY_A, 4)
            ww = winf(NULL_V, SHUNT)
            X, Y = pp_xy(NULL_V, ww, a)
            wn = polyline_group(clipped_polylines(X, Y, PP_BOX, ww > 1e-6), PURPLE_A, 4)
            return VGroup(wn, vn)

        def trail():
            Tn, a = self.t(), self.a()
            g = VGroup()
            for k in range(len(KICKS) + 1):
                m = (SIM_SEG == k) & (SIM_T <= Tn)
                if m.sum() < 1:
                    continue
                tt, VV, ww = SIM_T[m], SIM_V[m], SIM_W[m]
                if k == int(SIM_SEG[np.searchsorted(SIM_T, Tn, side="right") - 1]) and tt[-1] < Tn:
                    Vn, wn = state_at(Tn)
                    tt, VV, ww = np.append(tt, Tn), np.append(VV, Vn), np.append(ww, wn)
                X, Y = pp_xy(VV, ww, a)
                cut = Tn - TRAIL_RECENT
                old = tt <= cut
                new = tt >= cut
                if old.any():
                    j = min(int(np.where(old)[0][-1]) + 2, len(tt))  # overlap one point
                    g.add(polyline_group(clipped_polylines(X[:j], Y[:j], PP_BOX), ORANGE, 3, OLD_OPACITY))
                g.add(polyline_group(clipped_polylines(X[new], Y[new], PP_BOX), ORANGE, 3, 1.0))
            return g

        def vtrace():
            Tn, a = self.t(), self.a()
            m = SIM_T <= Tn
            tt, VV = SIM_T[m], SIM_V[m]
            Vn, _ = state_at(Tn)
            tt, VV = np.append(tt, Tn), np.append(VV, Vn)
            X, Y = vt_xy(tt, VV, a)
            return polyline_group(clipped_polylines(X, Y, VT_BOX), WHITE, 3)

        def current():
            Tn = self.t()
            tt = np.linspace(0, max(Tn, 1e-3), max(2, int(Tn / 0.5) + 2))
            X = VX0 + tt / T_END * (VX1 - VX0)
            Y = IY0 + (I_of_t(tt) - I_LO) / (I_HI - I_LO) * (IY1 - IY0)
            return VMobject().set_points_as_corners(np.column_stack([X, Y, 0 * X])).set_stroke(GREY_B, 3)

        def vbar():
            Tn, a = self.t(), self.a()
            lo, hi = vt_range(a)
            if Tn < T_ZOOM0 + 5:
                mv, op = 2.0, np.clip((T_ZOOM0 + 5 - Tn) / 5, 0, 1)
            else:
                mv, op = 20.0, np.clip((Tn - (T_ZOOM1 - 5)) / 5, 0, 1)
            L = mv / (hi - lo) * (VY1 - VY0)
            bar = Line([4.12, -1.0, 0], [4.12, -1.0 + L, 0]).set_stroke(GREY_B, 3, op)
            lab = txt(f"{mv:.0f} mV", font_size=24).set_color(GREY_B)
            lab.next_to(bar, LEFT, buff=0.1).set_y(-1.0 + 0.3)
            lab.set_opacity(op)
            return VGroup(bar, lab)

        self.focus_filled = Dot(radius=0.10, fill_color=WHITE)
        self.focus_open = Dot(radius=0.10, fill_color=BLACK, stroke_color=WHITE, stroke_width=3)
        self.focus_label = txt("focus", font_size=26).set_color(GREY_B)
        self.state = Dot(radius=0.06, fill_color=YELLOW)
        self.v_pen = Dot(radius=0.05, fill_color=YELLOW)
        self.i_pen = Dot(radius=0.045, fill_color=GREY_B)

        def place_pens(_):
            Tn, a = self.t(), self.a()
            Vn, _w = state_at(Tn)
            X, Y = vt_xy(Tn, Vn, a)
            self.v_pen.move_to([X, np.clip(Y, VY0, VY1), 0])
            self.i_pen.move_to([X, IY0 + (I_of_t(Tn) - I_LO) / (I_HI - I_LO) * (IY1 - IY0), 0])

        def place_focus(_):
            Vf, wf, unstable = focus_at(self.t())
            X, Y = pp_xy(Vf, wf, self.a())
            p = np.array([X, Y, 0.0])
            self.focus_filled.move_to(p).set_opacity(0.0 if unstable else 1.0)
            self.focus_open.move_to(p)
            self.focus_open.set_fill(BLACK, 1.0 if unstable else 0.0)
            self.focus_open.set_stroke(WHITE, 3, 1.0 if unstable else 0.0)
            self.focus_label.next_to(p, DOWN + RIGHT, buff=0.12 + 0.14 * self.a())

        def place_state(d):
            Vn, wn = state_at(self.t())
            X, Y = pp_xy(Vn, wn, self.a())
            inside = PX0 <= X <= PX1 and PY0 <= Y <= PY1
            d.move_to([X, Y, 0]).set_opacity(1.0 if inside else 0.0)

        def kick_marks():
            Tn = self.t()
            g = VGroup()
            for i, tk in enumerate(KICKS):
                if Tn < tk:
                    continue
                x = VX0 + tk / T_END * (VX1 - VX0)
                y = IY0 + (I_of_t(tk) - I_LO) / (I_HI - I_LO) * (IY1 - IY0)
                tri = Triangle().set_width(0.12).set_fill(RED_C, 1).set_stroke(width=0)
                tri.move_to([x, y - 0.03, 0], aligned_edge=UP)
                g.add(tri)
                if i == 0:
                    g.add(txt("kick", font_size=24).set_color(RED_C).next_to(tri, DOWN, buff=0.08))
            return g

        def kick_arrow():
            Tn, a = self.t(), self.a()
            g = VGroup()
            for k, tk in enumerate(KICKS):
                age = Tn - tk
                if not (0 <= age <= KICK_SHOW):
                    continue
                op = float(np.clip((KICK_SHOW - age) / 3.0, 0, 1))
                i = np.where(SIM_SEG == k + 1)[0][0]
                X0, Y0 = pp_xy(SIM_V[i - 1], SIM_W[i - 1], a)
                X1, Y1 = pp_xy(SIM_V[i], SIM_W[i], a)
                start, end = np.array([X0, Y0, 0]), np.array([X1, Y1, 0])
                tip_len = 0.12
                u = (end - start) / np.linalg.norm(end - start)
                shaft = DashedLine(start, end - u * tip_len, dash_length=0.04).set_stroke(RED_C, 4, op)
                tip = Triangle().set_height(tip_len).set_width(0.14, stretch=True)
                tip.rotate(np.arctan2(u[1], u[0]) - PI / 2)
                tip.move_to(end - u * tip_len / 2).set_fill(RED_C, op).set_stroke(width=0)
                g.add(shaft, tip)
            return g

        self.focus_filled.add_updater(place_focus)
        self.state.add_updater(place_state)
        self.v_pen.add_updater(place_pens)
        self.dyn = [
            always_redraw(nullclines), always_redraw(trail),
            self.focus_open, self.focus_filled, self.focus_label, self.state,
            always_redraw(kick_arrow), always_redraw(vtrace), always_redraw(current),
            always_redraw(kick_marks), always_redraw(vbar), self.i_pen, self.v_pen,
        ]
        self.add(*self.dyn)

    ## Beat 1: still frame - focus window, filled focus, tag
    def opening(self):
        self.wait(1.0)

    ## Beat 2: kick 1 at I = 110, barely one overshoot
    def kick_at_110(self):
        self.advance(25.0)

    ## Beat 3: ramp to 112.5, kick 2 spirals in; "rings at ~100 Hz"
    def kick_at_112(self):
        self.advance(60.0)
        self.advance(80.0, FadeIn(self.readout1))

    ## Beat 4: ramp to 114, kick 3, ringing barely decays
    def kick_at_114(self):
        self.advance(165.0)

    ## Beat 5: Hopf crossing - focus turns open, red flash
    def hopf_crossing(self):
        self.advance(T_HOPF)
        self.ring = Circle(radius=0.42).set_stroke(RED_C, 6).move_to(self.focus_open)
        self.play(GrowFromCenter(self.ring), run_time=0.4)

    ## Beat 6: ring grows; zoom out; state jumps onto the big loop
    def escape(self):
        self.advance(T_ZOOM0, FadeOut(self.ring, scale=1.6))
        self.advance(T_ZOOM1, rate=10.0)

    ## Beat 7: repetitive spiking; "fires at ~110 spikes/s"
    def spiking(self):
        self.advance(223.0)
        self.advance(T_END, FadeIn(self.readout2))

    ## Beat 8-9: caption, then hold the end frame
    def caption_and_hold(self):
        self.play(Write(self.caption), run_time=1.0)
        self.wait(3.0)



if __name__ == "__main__":
    print(f"I_Hopf = {I_HOPF:.4f}, t_Hopf = {T_HOPF:.2f} ms")
    assert abs(I_HOPF - 114.2358) < 1e-3
    assert abs(T_HOPF - 168.23) < 0.02
    fp = fixed_points(114.0, SHUNT)[0]
    assert fp[3].real.max() < 0 and abs(fp[3].imag).max() > 0.6
    fp = fixed_points(114.5, SHUNT)[0]
    assert fp[3].real.max() > 0
    sp = spikes(SIM_T, SIM_V)
    print("spikes", np.round(sp, 2))
    assert np.allclose(sp, [203.9, 212.8, 221.8, 230.7, 239.7, 248.6, 257.6], atol=0.5)
    assert SIM_V[SIM_T < 168].max() < -29.0          # all kicks stayed subthreshold
    expect = [[1.217, 0.107], [1.388, 0.531, 0.201], [1.636, 1.464, 1.305]]
    for k, pk in enumerate(expect):
        dt, h = ring_peaks(SIM_T, SIM_V, SIM_SEG, k, len(pk))
        print(f"kick {k + 1}: peaks {np.round(h, 3)} at +{np.round(dt, 1)} ms")
        assert np.allclose(h, pk, atol=0.05), (k, h)
    # inside the focus window up to 195 ms
    m = SIM_T < 195
    assert SIM_V[m].max() < -24 and SIM_W[m].max() < 0.026 and SIM_W[m].min() > 0.004
    isi = np.diff(sp)
    print(f"ISI {isi.mean():.2f} ms -> {1000 / isi[-1]:.1f} spikes/s")
    assert abs(1000 / isi[-1] - 111.7) < 1.0
    print("ok")
