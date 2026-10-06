"""Class 1: rest vanishes, the ball crawls.

Contract: context_files/contract.md. Everything is driven by one deterministic run of the
paper's CONTROL model (model.md schedule) through two trackers: model time T (1 video s =
50 ms) and the phase-plane window Z (0 knee, 1 full; hidden warp asinh / w^0.4).

Beats as built (video s; total 19.67 s at 30 fps):
1. 0.00-1.00  Still: knee window, nullclines at I = 38.0, filled "rest" dot with the yellow
              state point on it, open "saddle" dot, tag, V(t) start dot, scale bars.
2. 1.00-4.49  T 0 -> 174.4 ms: staircase drawn, V-nullcline lifts, rest and saddle slide
              together along the knee (fixed_points per frame), V(t) creeps -42.0 -> -39.1 mV.
3. 4.49-5.33  Collision at I_SN = 38.741: half-filled dot for 2 frames, RED_C ring flash
              (0.3 s) at (V_SN, w_SN), labels fade, dots gone; model paused.
4. 5.33-13.05 T 174.4 -> 560: zoom knee -> full (1.5 s, done at model 249 ms, before the
              first spike at 272), ghost blob fades in; then ghost / nullcline labels; crawl
              through the ghost and 3 slow spikes; "8 spikes/s" at the 2nd spike (~9.8 s).
5. 13.05-15.65 T 560 -> 690: step to 39.0, 4 fast spikes; readout swaps to "34 spikes/s"
              at the 2nd fast spike (~14.0 s).
6. 15.65-16.67 Caption "arbitrarily slow firing is possible" writes in; ISI brackets
              "125 ms" and "30 ms" fade in over V(t).
7. 16.67-19.67 Hold end frame (3 s).
"""

from common import *

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar


# ---------------------------------------------------------------- model (model.md)

BASE = dict(C=2.0, ENa=50.0, EK=-100.0, Esh=-70.0, gNa=20.0, gK=20.0, gsh=2.0, phi=0.25,
            bm=-1.2, gm=18.0, bw=-9.0, gw=10.0, gM=0.0, bz=-30.0, gz=5.0)
CONTROL = dict(BASE)


def minf(V, p):
    return 0.5 * (1 + np.tanh((V - p['bm']) / p['gm']))


def winf(V, p):
    return 0.5 * (1 + np.tanh((V - p['bw']) / p['gw']))


def tauw(V, p):
    return 1 / np.cosh((V - p['bw']) / (2 * p['gw']))


def I_fixed(V, p, z=0.0):
    """Every current except the w-gated K+ current."""
    return p['gNa'] * minf(V, p) * (V - p['ENa']) + p['gsh'] * (V - p['Esh']) + p['gM'] * z * (V - p['EK'])


def f2(V, w, I, p, z=0.0):
    """Reduced (V, w) system; keep this summation order (bit-for-bit with the deck module)."""
    Iion = (p['gNa'] * minf(V, p) * (V - p['ENa']) + p['gK'] * w * (V - p['EK'])
            + p['gsh'] * (V - p['Esh']) + p['gM'] * z * (V - p['EK']))
    return (I - Iion) / p['C'], p['phi'] * (winf(V, p) - w) / tauw(V, p)


def V_null(V, I, p, z=0.0):
    return (I - I_fixed(V, p, z)) / (p['gK'] * (V - p['EK']))


def I_ss(V, p):
    """Steady-state I-V curve (all gates at steady state)."""
    return I_fixed(V, p) + p['gK'] * winf(V, p) * (V - p['EK'])


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
    return out  # sorted by V; out[0] is rest


def saddle_node(p):
    """(I_SN, V_SN, w_SN): maximum of the steady-state I-V curve on [-50, -30] mV."""
    r = minimize_scalar(lambda V: -I_ss(V, p), bounds=(-50, -30), method='bounded',
                        options=dict(xatol=1e-10))
    return I_ss(r.x, p), r.x, winf(r.x, p)


def run(p, I_of_t, t0, t1, y0):
    s = solve_ivp(lambda t, y: f2(y[0], y[1], I_of_t(t), p), (t0, t1), y0,
                  method='LSODA', max_step=0.02, rtol=1e-9, atol=1e-11)
    return s.t, s.y[0], s.y[1]


def spikes(t, V):
    """Upward crossings of 0 mV."""
    k = np.where((V[:-1] < 0) & (V[1:] >= 0))[0]
    return t[k]


# ---------------------------------------------------------------- the schedule (model.md "Schedule")

RAMPS = [(38.0, 38.5, 40.0, 70.0), (38.5, 38.7, 100.0, 130.0),
         (38.7, 38.75, 160.0, 180.0), (38.75, 39.0, 560.0, 570.0)]
T_END = 690.0
Y0 = (-42.038, 0.001351)


def I_of_t(t):
    """Cosine-ramp staircase; scalar or array t (ms)."""
    t = np.asarray(t, dtype=float)
    I = np.full_like(t, RAMPS[0][0])
    for I0, I1, a, b in RAMPS:
        s = np.clip((t - a) / (b - a), 0, 1)
        I = np.where(t >= a, I0 + (I1 - I0) * 0.5 * (1 - np.cos(np.pi * s)), I)
    return I if I.ndim else float(I)


I_SN, V_SN, W_SN = saddle_node(CONTROL)
T_SN = brentq(lambda t: I_of_t(t) - I_SN, 160.0, 180.0)   # 174.40 ms


def simulate():
    """The one deterministic run that drives the whole video."""
    return run(CONTROL, I_of_t, 0.0, T_END, list(Y0))


def isis(spike_times):
    return np.diff(spike_times)



# ---------------------------------------------------------------- precomputed data for the scene

def fp_table(t_grid):
    """Rest and saddle (V, w) along the schedule up to the collision; merged at T_SN."""
    rest, sad = [], []
    for tt in t_grid:
        fp = fixed_points(I_of_t(min(tt, T_SN)), CONTROL)
        if tt >= T_SN or len(fp) < 3:
            rest.append((V_SN, W_SN)); sad.append((V_SN, W_SN))
        else:
            rest.append(fp[0][:2]); sad.append(fp[1][:2])
    return np.array(rest), np.array(sad)


def decimate(t, X, Y, min_step, max_dt):
    """Keep samples at least min_step apart in (X, Y), or max_dt apart in time."""
    keep = [0]
    lx, ly, lt = X[0], Y[0], t[0]
    for i in range(1, len(t)):
        if np.hypot(X[i] - lx, Y[i] - ly) >= min_step or t[i] - lt >= max_dt:
            keep.append(i); lx, ly, lt = X[i], Y[i], t[i]
    if keep[-1] != len(t) - 1:
        keep.append(len(t) - 1)
    return np.array(keep)


# ---------------------------------------------------------------- display warp (model.md)

def warp_x(V):
    return np.arcsinh((np.asarray(V) + 36.0) / 8.0)


def warp_y(w):
    return np.clip(np.asarray(w), 0, None) ** 0.4


def unwarp_x(sx):
    return 8.0 * np.sinh(sx) - 36.0


KNEE_WIN = (float(warp_x(-47)), float(warp_x(-31)), float(warp_y(0.0003)), float(warp_y(0.012)))
FULL_WIN = (float(warp_x(-78)), float(warp_x(30)), float(warp_y(0.0)), float(warp_y(0.36)))


def window(a):
    """Warped-coordinate window at zoom a (0 knee, 1 full): centre linear, size geometric."""
    (k0, k1, k2, k3), (f0, f1, f2_, f3) = KNEE_WIN, FULL_WIN
    cx = (1 - a) * (k0 + k1) / 2 + a * (f0 + f1) / 2
    cy = (1 - a) * (k2 + k3) / 2 + a * (f2_ + f3) / 2
    wx = (k1 - k0) ** (1 - a) * (f1 - f0) ** a
    wy = (k3 - k2) ** (1 - a) * (f3 - f2_) ** a
    return cx - wx / 2, cx + wx / 2, cy - wy / 2, cy + wy / 2


def clip_runs(P, box):
    """Split polyline P (n, 2) into the runs inside box, with boundary crossing points added."""
    x0, x1, y0, y1 = box
    inside = (P[:, 0] >= x0) & (P[:, 0] <= x1) & (P[:, 1] >= y0) & (P[:, 1] <= y1)

    def cross(p_in, p_out):
        d = p_out - p_in
        s = 1.0
        for k, lo, hi in ((0, x0, x1), (1, y0, y1)):
            if d[k] > 0:
                s = min(s, (hi - p_in[k]) / d[k])
            elif d[k] < 0:
                s = min(s, (lo - p_in[k]) / d[k])
        return p_in + max(s, 0.0) * d

    runs = []
    n = len(P)
    i = 0
    while i < n:
        if not inside[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and inside[j + 1]:
            j += 1
        pts = [P[i:j + 1]]
        if i > 0:
            pts.insert(0, cross(P[i], P[i - 1])[None])
        if j < n - 1:
            pts.append(cross(P[j], P[j + 1])[None])
        run = np.vstack(pts)
        if len(run) >= 2:
            runs.append(run)
        i = j + 1
    return runs


# ---------------------------------------------------------------- layout (contract section 4)

PP_BOX = (-3.55, 0.0, -2.05, 2.7)        # plot area inside the phase-plane region
VT_X = (0.45, 4.15)                       # 0-700 ms
VT_Y = (-0.45, 2.45)                      # -80 ... +30 mV
T_AXIS = 700.0
CUR_Y = (-2.35, -1.65)                    # 38.0 ... 39.0 uA/cm2 (no numbers on screen)
I_LO, I_HI = 38.0, 39.0

MS_PER_S = 50.0                           # 1 video second = 50 ms of model time
COLLISION_HOLD = 0.81
TRAIL_RECENT = 60.0                       # ms of trail drawn fully opaque
OLD_TRAIL_OPACITY = 0.35

C_VNULL, C_WNULL = GREY_A, PURPLE_A
C_CLASS1 = BLUE_C
C_STATE = YELLOW
C_FLASH = RED_C
C_AXIS = GREY_B


def to_pp(sx, sy, win):
    """Warped coordinates -> scene points in the phase-plane box."""
    x0, x1, y0, y1 = win
    X = PP_BOX[0] + (np.asarray(sx) - x0) / (x1 - x0) * (PP_BOX[1] - PP_BOX[0])
    Y = PP_BOX[2] + (np.asarray(sy) - y0) / (y1 - y0) * (PP_BOX[3] - PP_BOX[2])
    return np.column_stack([np.atleast_1d(X), np.atleast_1d(Y)])


def vt_xy(t, V):
    X = VT_X[0] + np.asarray(t) / T_AXIS * (VT_X[1] - VT_X[0])
    Y = VT_Y[0] + (np.asarray(V) + 80.0) / 110.0 * (VT_Y[1] - VT_Y[0])
    return np.column_stack([np.atleast_1d(X), np.atleast_1d(Y)])


def cur_xy(t, I):
    X = VT_X[0] + np.asarray(t) / T_AXIS * (VT_X[1] - VT_X[0])
    Y = CUR_Y[0] + (np.asarray(I) - I_LO) / (I_HI - I_LO) * (CUR_Y[1] - CUR_Y[0])
    return np.column_stack([np.atleast_1d(X), np.atleast_1d(Y)])


def video_time(t_model):
    """Beat-sheet clock: 1 s still, then 50 ms/s, with the collision hold after T_SN."""
    return 1.0 + t_model / MS_PER_S + (COLLISION_HOLD if t_model > T_SN else 0.0)


def set_runs(vm, runs):
    """Load several polylines into one VMobject (quadratic corners, path breaks between)."""
    parts = []
    for r in runs:
        A = np.column_stack([r, np.zeros(len(r))])
        pts = np.empty((2 * len(A) - 1, 3))
        pts[0::2] = A
        pts[1::2] = 0.5 * (A[:-1] + A[1:])
        if parts:
            parts.append(parts[-1][-1:])      # handle on the previous anchor = path break
        parts.append(pts)
    if parts:
        vm.set_points(np.vstack(parts))
    else:
        vm.set_points(np.zeros((1, 3)))
    return vm


def blob_outline(win, scale):
    """Ghost blob: a lens along the w-nullcline, V_SN +/- 4 mV, in scene units."""
    V = np.linspace(V_SN - 4, V_SN + 4, 48)
    C = to_pp(warp_x(V), warp_y(winf(V, CONTROL)), win)
    d = np.gradient(C, axis=0)
    nrm = np.column_stack([-d[:, 1], d[:, 0]])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    u = (V - V_SN) / 4.0
    h = scale * 0.2 * np.sqrt(np.clip(1 - u ** 2, 0, 1)) + 0.02
    ends = 0.10 * scale * (C[-1] - C[0]) / np.linalg.norm(C[-1] - C[0])
    upper = C + nrm * h[:, None]
    lower = C - nrm * h[:, None]
    return np.vstack([C[0] - ends, upper, C[-1] + ends, lower[::-1]])


class SceneData:
    """Everything the scene draws, computed once."""

    def __init__(self):
        t, V, w = simulate()
        self.t, self.V, self.w = t, V, w
        self.spikes = spikes(t, V)
        isi = isis(self.spikes)
        self.isi_slow, self.isi_fast = isi[1], isi[-1]
        sx, sy = warp_x(V), warp_y(w)
        F = to_pp(sx, sy, FULL_WIN)
        k = decimate(t, F[:, 0], F[:, 1], 0.012, 1.0)
        self.tr_t, self.tr_sx, self.tr_sy = t[k], sx[k], sy[k]
        P = vt_xy(t, V)
        k = decimate(t, P[:, 0], P[:, 1], 0.008, 1.0)
        self.vt_t, self.vt_pts = t[k], P[k]
        self.fp_t = np.linspace(0, T_SN, 400)
        self.fp_rest, self.fp_sad = fp_table(self.fp_t)
        self.cur_t = np.linspace(0, T_END, 1400)
        self.cur_pts = cur_xy(self.cur_t, I_of_t(self.cur_t))

    def state(self, tt):
        return np.interp(tt, self.t, self.V), np.interp(tt, self.t, self.w)

    def fps(self, tt):
        tt = min(tt, T_SN)
        r = [np.interp(tt, self.fp_t, self.fp_rest[:, k]) for k in (0, 1)]
        s = [np.interp(tt, self.fp_t, self.fp_sad[:, k]) for k in (0, 1)]
        return r, s


def ramp01(x, x0, width):
    return float(np.clip((x - x0) / width, 0, 1))


class Class1SnicOnset(Scene):
    def construct(self):
        self.D = SceneData()
        self.T = ValueTracker(0.0)          # model time, ms
        self.Z = ValueTracker(0.0)          # window: 0 knee, 1 full
        self.opening()
        self.approach()
        self.collision()
        self.crawl()
        self.step_up()
        self.caption_and_brackets()
        self.end_hold()

    # helpers ---------------------------------------------------------------
    def t(self):
        return self.T.get_value()

    def win(self):
        return window(self.Z.get_value())

    def pp_point(self, V, w):
        x, y = to_pp(warp_x(V), warp_y(w), self.win())[0]
        return np.array([x, y, 0.0])

    def nullcline(self, color, fn):
        vm = VMobject(stroke_color=color, stroke_width=4, fill_opacity=0)

        def upd(m):
            win = self.win()
            sx = np.linspace(win[0], win[1], 500)
            Vs = unwarp_x(sx)
            P = to_pp(sx, warp_y(fn(Vs)), win)
            set_runs(m, clip_runs(P, PP_BOX))
        vm.add_updater(upd)
        upd(vm)
        return vm

    # beats -----------------------------------------------------------------
    def opening(self):
        ## Beat 1: still first frame (knee window, rest + saddle, tag)
        D = self.D
        x0, x1, y0, y1 = PP_BOX
        ax_x = Line([x0 - 0.05, y0 - 0.05, 0], [x1 + 0.12, y0 - 0.05, 0],
                    stroke_color=C_AXIS, stroke_width=2).add_tip(length=0.14, width=0.12)
        ax_y = Line([x0 - 0.05, y0 - 0.05, 0], [x0 - 0.05, y1 + 0.12, 0],
                    stroke_color=C_AXIS, stroke_width=2).add_tip(length=0.14, width=0.12)
        lab_V = tex("V", font_size=34, fill_color=C_AXIS).next_to(ax_x.get_end(), DOWN, buff=0.1)
        lab_V.align_to(ax_x.get_end(), RIGHT)
        lab_w = tex("w", font_size=34, fill_color=C_AXIS).next_to(ax_y.get_end(), RIGHT, buff=0.12)
        lab_w.align_to(ax_y.get_end(), UP)
        lab_k = txt("K⁺ activation", font_size=24, fill_color=C_AXIS)
        lab_k.rotate(PI / 2).next_to(ax_y, LEFT, buff=0.1)
        self.axes = VGroup(ax_x, ax_y, lab_V, lab_w, lab_k)

        tag = txt("Class 1 · SNIC", font_size=32, fill_color=C_CLASS1)
        tag.move_to([-4.15, 3.45, 0], aligned_edge=LEFT)

        cur_label = txt("current", font_size=24, fill_color=C_AXIS)
        cur_label.move_to([VT_X[0], CUR_Y[1] + 0.25, 0], aligned_edge=LEFT)

        # scale bars, lower right of the V(t) box
        sb_y = -0.95
        sb_x1 = VT_X[1]
        sb_x0 = sb_x1 - 100.0 / T_AXIS * (VT_X[1] - VT_X[0])
        sb_h = 20.0 / 110.0 * (VT_Y[1] - VT_Y[0])
        bars = VGroup(
            Line([sb_x0, sb_y, 0], [sb_x1, sb_y, 0]),
            Line([sb_x1, sb_y, 0], [sb_x1, sb_y + sb_h, 0]),
        ).set_stroke(C_AXIS, 3)
        lab_ms = txt("100 ms", font_size=24, fill_color=C_AXIS).next_to(bars[0], DOWN, buff=0.08)
        lab_mv = txt("20 mV", font_size=24, fill_color=C_AXIS).next_to(bars[1], LEFT, buff=0.1)
        lab_mv.shift(UP * 0.1)
        self.scale_bars = VGroup(bars, lab_ms, lab_mv)

        # ghost blob (hidden until the zoom)
        self.ghost_op = ValueTracker(0.0)
        self.label_op = ValueTracker(0.0)    # full-window labels, after the zoom
        blob = VGroup(*[VMobject(fill_color=C_CLASS1, fill_opacity=0, stroke_width=0)
                        for _ in range(3)])

        def upd_blob(g):
            win = self.win()
            op = self.ghost_op.get_value()
            for layer, s in zip(g, (1.0, 0.72, 0.45)):
                P = blob_outline(win, s)
                P = np.vstack([P, P[:1]])
                layer.set_points_as_corners(np.column_stack([P, np.zeros(len(P))]))
                layer.set_fill(C_CLASS1, 0.065 * op)
        blob.add_updater(upd_blob)
        upd_blob(blob)
        ghost_lab = txt("ghost", font_size=28, fill_color=C_CLASS1, slant=ITALIC)

        def upd_glab(m):
            c = self.pp_point(V_SN, W_SN)
            m.move_to(c + np.array([0.55, -0.42, 0]))
            m.set_opacity(self.label_op.get_value())
        ghost_lab.add_updater(upd_glab)
        upd_glab(ghost_lab)
        self.ghost = VGroup(blob, ghost_lab)

        # nullclines at I(t)
        self.v_null = self.nullcline(C_VNULL, lambda Vs: V_null(Vs, I_of_t(self.t()), CONTROL))
        self.w_null = self.nullcline(C_WNULL, lambda Vs: winf(Vs, CONTROL))

        # trail: old part at 35 %, last 60 ms opaque
        old = VMobject(stroke_color=C_CLASS1, stroke_width=3, stroke_opacity=OLD_TRAIL_OPACITY,
                       fill_opacity=0)
        new = VMobject(stroke_color=C_CLASS1, stroke_width=3, fill_opacity=0)

        def upd_trail(_):
            tt = self.t()
            win = self.win()
            Vn, wn = D.state(tt)
            n = np.searchsorted(D.tr_t, tt, side="right")
            sx = np.append(D.tr_sx[:n], warp_x(Vn))
            sy = np.append(D.tr_sy[:n], warp_y(wn))
            tq = np.append(D.tr_t[:n], tt)
            P = to_pp(sx, sy, win)
            cut = np.searchsorted(tq, tt - TRAIL_RECENT)
            set_runs(old, clip_runs(P[:cut + 1], PP_BOX) if cut >= 1 else [])
            set_runs(new, clip_runs(P[max(cut, 0):], PP_BOX))
        self.trail = VGroup(old, new)
        self.trail.add_updater(upd_trail)
        upd_trail(None)

        # fixed points (rest filled, saddle open) and their labels
        # white rim so the filled rest dot still reads with the state point sitting on it
        self.rest_dot = Dot(radius=0.09, fill_color=WHITE, stroke_color=WHITE, stroke_width=8)
        self.sad_dot = Dot(radius=0.09, fill_color=BLACK, stroke_color=WHITE, stroke_width=3)
        self.rest_lab = txt("rest", font_size=26, fill_color=GREY_B)
        self.sad_lab = txt("saddle", font_size=26, fill_color=GREY_B)

        def upd_fp(_):
            (rv, rw), (sv, sw) = D.fps(self.t())
            self.rest_dot.move_to(self.pp_point(rv, rw))
            self.sad_dot.move_to(self.pp_point(sv, sw))
            self.rest_lab.next_to(self.rest_dot, DR, buff=0.04)
            self.sad_lab.next_to(self.sad_dot, UL, buff=0.04)
        self.fp_group = VGroup(self.rest_dot, self.sad_dot, self.rest_lab, self.sad_lab)
        self.fp_group.add_updater(upd_fp)
        upd_fp(None)

        # state point
        self.state = Dot(radius=0.08, fill_color=C_STATE, stroke_color=BLACK, stroke_width=2)
        self.state.add_updater(lambda m: m.move_to(self.pp_point(*D.state(self.t()))))
        self.state.update()

        # V(t) trace + head, current staircase
        vt = VMobject(stroke_color=WHITE, stroke_width=3, fill_opacity=0)
        head = Dot(radius=0.05, fill_color=C_STATE)

        def upd_vt(_):
            tt = self.t()
            n = np.searchsorted(D.vt_t, tt, side="right")
            end = vt_xy(tt, D.state(tt)[0])
            P = np.vstack([D.vt_pts[:n], end])
            set_runs(vt, [P] if len(P) >= 2 else [])
            head.move_to([end[0, 0], end[0, 1], 0])
        self.vt = VGroup(vt, head)
        self.vt.add_updater(upd_vt)
        upd_vt(None)

        cur = VMobject(stroke_color=C_AXIS, stroke_width=3, fill_opacity=0)

        def upd_cur(m):
            tt = self.t()
            n = np.searchsorted(D.cur_t, tt, side="right")
            end = cur_xy(tt, I_of_t(tt))
            P = np.vstack([D.cur_pts[:n], end])
            set_runs(m, [P] if len(P) >= 2 and tt > 0 else [])
        cur.add_updater(upd_cur)
        upd_cur(cur)
        self.cur = cur

        # rate readout (appears at the 2nd spike of each rate)
        s = D.spikes
        rate_slow = round(1000.0 / D.isi_slow)
        rate_fast = round(1000.0 / D.isi_fast)
        self.readouts = VGroup()
        # swap = fade out (3 ms) then fade in, so the two strings never overlap
        for text, on, off in ((f"{rate_slow} spikes/s", s[1] + 3.0, s[4]),
                              (f"{rate_fast} spikes/s", s[4] + 3.0, np.inf)):
            r = txt(text, font_size=32, fill_color=WHITE)
            r.move_to([4.15, 3.45, 0], aligned_edge=RIGHT)

            def upd_r(m, on=on, off=off):
                tt = self.t()
                m.set_opacity(ramp01(tt, on, 5.0) * (1 - ramp01(tt, off, 3.0)))
            r.add_updater(upd_r)
            upd_r(r)
            self.readouts.add(r)

        self.add(self.ghost, self.axes, self.w_null, self.v_null, self.trail,
                 self.fp_group, self.state, self.scale_bars, cur_label, self.cur,
                 self.vt, tag, self.readouts)
        self.wait(1.0)

    def approach(self):
        ## Beat 2: current steps up; rest and saddle slide together
        self.play(self.T.animate.set_value(T_SN), run_time=T_SN / MS_PER_S, rate_func=linear)

    def collision(self):
        ## Beat 3: collision flash, dots vanish
        c = self.pp_point(V_SN, W_SN)
        a = np.linspace(PI / 2, 3 * PI / 2, 25)
        half_disk = Polygon(*[[0.09 * np.cos(x), 0.09 * np.sin(x), 0] for x in a],
                            fill_color=WHITE, fill_opacity=1, stroke_width=0)
        ring0 = Circle(radius=0.09, fill_color=BLACK, fill_opacity=1,
                       stroke_color=WHITE, stroke_width=3)
        half = VGroup(ring0, half_disk)
        half_disk.shift(ring0.get_center() - ORIGIN)
        half.shift(c - ring0.get_center())
        self.fp_group.clear_updaters()
        self.remove(self.rest_dot, self.sad_dot)
        self.add(half)
        self.wait(2 / 30)
        ring = Circle(radius=0.1, stroke_color=C_FLASH, stroke_width=6).move_to(c)

        def flash(m, a):
            m.set_width(2 * (0.1 + 0.55 * a))
            m.move_to(c)
            m.set_stroke(C_FLASH, 6 * (1 - a) + 1, opacity=1 - a)
        self.remove(half)
        self.play(UpdateFromAlphaFunc(ring, flash, remover=True),
                  FadeOut(self.rest_lab), FadeOut(self.sad_lab),
                  run_time=0.3, rate_func=linear)
        self.wait(COLLISION_HOLD - 0.3 - 2 / 30)

    def crawl(self):
        ## Beat 4: zoom to the full plane; the crawl through the ghost; 3 slow spikes
        t0 = T_SN
        zoom_ms = 1.5 * MS_PER_S
        self.play(self.T.animate.set_value(t0 + zoom_ms),
                  self.Z.animate.set_value(1.0).set_anim_args(rate_func=smooth),
                  self.ghost_op.animate.set_value(1.0),
                  run_time=1.5, rate_func=linear)
        self.null_labels = self.make_null_labels()
        self.add(self.null_labels)
        self.play(self.T.animate.set_value(t0 + zoom_ms + 0.5 * MS_PER_S),
                  self.label_op.animate.set_value(1.0), run_time=0.5, rate_func=linear)
        t1 = self.t()
        self.play(self.T.animate.set_value(560.0), run_time=(560.0 - t1) / MS_PER_S,
                  rate_func=linear)

    def make_null_labels(self):
        vl = txt("V-nullcline", font_size=26, fill_color=C_VNULL)
        wl = txt("w-nullcline", font_size=26, fill_color=C_WNULL)
        # inside the spiking loop, where the plane is empty: right of the V-nullcline's
        # left branch, left of the w-nullcline's rise
        vl.next_to(self.pp_point(-62.0, V_null(-62.0, 39.0, CONTROL)), RIGHT, buff=0.15)
        wl.next_to(self.pp_point(-22.0, winf(-22.0, CONTROL)), LEFT, buff=0.15)
        g = VGroup(vl, wl)
        g.add_updater(lambda m: m.set_opacity(self.label_op.get_value()))
        g.update()
        return g

    def step_up(self):
        ## Beat 5: one more current step; faster firing
        self.play(self.T.animate.set_value(T_END), run_time=(T_END - 560.0) / MS_PER_S,
                  rate_func=linear)

    def caption_and_brackets(self):
        ## Beat 6: caption and ISI brackets
        D = self.D
        s = D.spikes
        y = VT_Y[1] + 0.08
        brackets = VGroup()
        for a, b, isi in ((s[1], s[2], D.isi_slow), (s[4], s[5], D.isi_fast)):
            xa, xb = vt_xy(a, 0)[0, 0], vt_xy(b, 0)[0, 0]
            shape = VMobject(stroke_color=C_AXIS, stroke_width=2.5, fill_opacity=0)
            shape.set_points_as_corners([[xa, y - 0.1, 0], [xa, y, 0], [xb, y, 0], [xb, y - 0.1, 0]])
            lab = txt(f"{round(isi)} ms", font_size=24, fill_color=C_AXIS).next_to(shape, UP, buff=0.08)
            brackets.add(VGroup(shape, lab))
        caption = txt("arbitrarily slow firing is possible", font_size=40, fill_color=WHITE)
        caption.move_to([0, -3.3, 0])
        self.play(Write(caption), FadeIn(brackets), run_time=0.98)

    def end_hold(self):
        ## Beat 7: hold end frame
        self.wait(3.0)


if __name__ == "__main__":
    fp = fixed_points(38.0, CONTROL)
    assert len(fp) == 3 and abs(fp[0][0] + 42.04) < 0.01, fp
    assert abs(fp[1][0] + 33.81) < 0.01
    assert len(fixed_points(38.75, CONTROL)) == 1          # rest and saddle gone
    assert abs(I_SN - 38.7409) < 1e-3 and abs(V_SN + 38.34) < 0.01 and abs(W_SN - 0.00282) < 1e-5
    assert abs(T_SN - 174.40) < 0.01, T_SN
    t, V, w = simulate()
    st = spikes(t, V)
    assert np.allclose(st, [272.0, 396.6, 521.2, 577.5, 607.2, 636.9, 666.6], atol=0.5), st
    print("I_SN", I_SN, "V_SN", V_SN, "w_SN", W_SN, "T_SN", T_SN)
    print("spikes", st, "ISIs", isis(st))
    print("V range", V.min(), V.max(), "w range", w.min(), w.max(), "n", len(t))
    print("ok")
