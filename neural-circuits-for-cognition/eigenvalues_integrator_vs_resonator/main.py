"""Decay vs ring: from eigenvalues to the phase plane (~100 s, 1920x1080, 60 fps).

Spec: context_files/contract.md. Model tables and recipes: context_files/model.md.
Three scenes, rendered separately and concatenated to videos/eigenvalues_integrator_vs_resonator.mp4:
  EigenvalueDecayVsRing           Part 1: cartoon complex plane (real lambda decays, complex lambda rings)
  PhasePlaneCurrentSteps          Part 2: the paper's V-w phase plane, class 1 vs class 2 staircases
  PulsePairIntegratorVsResonator  Part 3: pulse-pair test, integrator vs resonator

Module layout: pure model/data functions (checked in __main__), then shared screen builders
(header, caption, speed badge, chip), then the three scenes.
"""

import pathlib

from common import *

import prescott2008 as P  # <area>/prescott2008.py, on sys.path via common

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "cache"
MAX_STEP = 0.02
DT = 0.05                       # ms, uniform sample grid for every model run
DT_ONSET = 0.01                 # finer grid for the onset runs (spike loops drawn smoothly)
HOLD = 50.0                     # ms per staircase step
FPS = 60

# ============================================================ Part 1 (pure numpy cartoon)
P1_C1_LAMBDAS = [-5.0, -1.0, -0.2]              # s^-1
P1_C1_WINDOWS = [1.2, 3.0, 3.0]                  # s (1x playback)
P1_OMEGA = 2 * np.pi * 5.0                       # s^-1, class 2 ladder
P1_C2_SIGMAS = [-2.0, -5.0]
P1_C2_WINDOWS = [2.0, 1.0]                       # s of model time (0.5x playback)
P1_ROT_T = 4.5                                   # s of model time
P1_SLOW = 2.0                                    # 0.5x playback = video time / model time
P1_LEAD = 1.5                                    # s of video a caption is up before its beat
P1_HOLD, P1_RESET = 0.3, 0.5                     # s: finished trace held, then reset to rest


def rot_freq(t):
    """Rotation-beat ring frequency (Hz): raised cosine 2 -> 8 -> 2 over P1_ROT_T."""
    t = np.asarray(t, float)
    return 2.0 + 6.0 * 0.5 * (1 - np.cos(2 * np.pi * np.clip(t, 0, P1_ROT_T) / P1_ROT_T))


def rot_phase(t):
    """theta(t) = integral of 2 pi f dt (closed form of the raised-cosine ramp)."""
    t = np.clip(np.asarray(t, float), 0, P1_ROT_T)
    return 2 * np.pi * (5.0 * t - 3.0 * P1_ROT_T / (2 * np.pi) * np.sin(2 * np.pi * t / P1_ROT_T))


def per_cycle(sigma, omega=P1_OMEGA):
    return float(np.exp(2 * np.pi * sigma / omega))


# ============================================================ Parts 2-3 (the paper's model)
C1_LEVELS = [0.25, 0.5, 0.75, 0.9]
C2_LEVELS = [0.75, 0.9, 0.97, 0.99]
C1_ONSET, C1_ONSET_MS, C1_SLOW = 1.0005, 300.0, 10.0
C2_ONSET, C2_ONSET_MS, C2_SLOW = 1.002, 120.0, 25.0
STAIR_SLOW = 40.0
RAMP_MS = 5.0                    # each staircase step is a raised-cosine ramp this long (not a jump)
PULSE_MS, PAIR_FRAC, PAIR_DTS = 0.5, 0.75, [2, 5, 10, 20]
PULSE_T0 = 10.0
P3_SLOW = 25.0

IB = {"c1": P.find_I_bif(P.CONTROL), "c2": P.find_I_bif(P.SHUNT)}
PARAMS = {"c1": P.CONTROL, "c2": P.SHUNT}
LEVELS = {"c1": C1_LEVELS, "c2": C2_LEVELS}
ONSET = {"c1": (C1_ONSET, C1_ONSET_MS), "c2": (C2_ONSET, C2_ONSET_MS)}
I0_P3 = {"c1": 0.9 * IB["c1"], "c2": 0.99 * IB["c2"]}


def grid(t_ms, dt=DT):
    return np.round(np.arange(0.0, t_ms + 1e-9, dt), 6)


def stable_fp(p, I):
    """The stable 2-D fixed point (lowest V) for a subthreshold current."""
    return next(f for f in P.fixed_points(p, I) if f["kind"].startswith("stable"))


def stair_I(key, t):
    """Staircase current (uA/cm2) at model time t: each step ramps from the previous level
    (0 before the first) with a raised cosine over RAMP_MS, starting at the step boundary."""
    Ib, lv = IB[key], LEVELS[key]
    t = np.asarray(t, dtype=float)
    k = np.clip((t // HOLD).astype(int), 0, len(lv) - 1)
    lvl = np.asarray(lv)
    prev = np.where(k > 0, lvl[np.maximum(k - 1, 0)], 0.0)
    u = np.clip((t - k * HOLD) / RAMP_MS, 0.0, 1.0)
    return Ib * (prev + (lvl[k] - prev) * 0.5 * (1 - np.cos(np.pi * u)))


def staircase_run(key):
    p, Ib, lv = PARAMS[key], IB[key], LEVELS[key]

    def I(t):
        return float(stair_I(key, t))

    def fn():
        T = len(lv) * HOLD
        t, V, w, _ = P.simulate(p, 0.0, t_ms=T, y0=P.rest_state(p, 0.0), I_func=I,
                                max_step=MAX_STEP, t_eval=grid(T))
        return dict(t=t, V=V, w=w)
    return P.npz_cache(CACHE / f"stair_{key}.npz", fn, levels=lv, hold=HOLD, max_step=MAX_STEP,
                       dt=DT, Ib=round(Ib, 6), ramp=RAMP_MS)


def onset_run(key, stair):
    p, Ib = PARAMS[key], IB[key]
    s, T = ONSET[key]
    y0 = [stair["V"][-1], stair["w"][-1], P.rest_state(p, 0.0)[2]]

    def fn():
        t, V, w, _ = P.simulate(p, s * Ib, t_ms=T, y0=y0, max_step=MAX_STEP,
                                t_eval=grid(T, DT_ONSET))
        return dict(t=t, V=V, w=w)
    return P.npz_cache(CACHE / f"onset_{key}.npz", fn, s=s, T=T, max_step=MAX_STEP, dt=DT_ONSET,
                       y0=np.round(y0, 9))


def local_max(t, V):
    k = np.where((V[1:-1] > V[:-2]) & (V[1:-1] >= V[2:]))[0] + 1
    return t[k], V[k]


def staircase_stats(key, stair):
    """Per step: V*, lambda (s^-1), kind, max V - V*, first overshoot above V*."""
    p, Ib, lv = PARAMS[key], IB[key], LEVELS[key]
    out = []
    for k, s in enumerate(lv):
        fp = stable_fp(p, s * Ib)
        m = (stair["t"] >= k * HOLD) & (stair["t"] <= (k + 1) * HOLD)
        t, V = stair["t"][m], stair["V"][m]
        tp, Vp = local_max(t, V)
        above = Vp[Vp > fp["V"]]
        out.append(dict(s=s, V=fp["V"], w=fp["w"], eig=fp["eig"] * 1000.0, kind=fp["kind"],
                        max_over=float(V.max() - fp["V"]),
                        first_over=float(above[0] - fp["V"]) if len(above) else 0.0,
                        end_err=float(abs(V[-1] - fp["V"]))))
    return out


def onset_stats(on):
    st = P.spike_times(on["t"], on["V"])
    tp, Vp = local_max(on["t"], on["V"])
    pre = Vp[(tp < st[0]) & (Vp < 0)] if len(st) else Vp
    return dict(spikes=st, rate=1000.0 / np.diff(st)[-1] if len(st) > 1 else 0.0,
                n_pre_peaks=int(len(pre)), pre_peaks=pre,
                Vlim=(on["V"].min(), on["V"].max()), wlim=(on["w"].min(), on["w"].max()))


def zoom_window(on):
    """Limit-cycle window: data extent +5% per side, w from 0, rounded outward."""
    V0, V1 = on["V"].min(), on["V"].max()
    w1 = on["w"].max()
    dv = 0.05 * (V1 - V0)
    return (float(np.floor(V0 - dv)), float(np.ceil(V1 + dv)), 0.0,
            float(np.ceil((w1 * 1.05) * 100) / 100))


# ---- Part 3 pulse pairs
def trial(key, amps, times, T):
    p, I0 = PARAMS[key], I0_P3[key]
    y0 = P.rest_state(p, I0)

    def I(t):
        return I0 + sum(a for a, t0 in zip(amps, times) if t0 <= t < t0 + PULSE_MS)
    t, V, w, _ = P.simulate(p, I0, t_ms=T, y0=y0, I_func=I, max_step=MAX_STEP, t_eval=grid(T))
    return t, V, w


def fires(V):
    return bool((V > 0).any())


def threshold_A1(key):
    def fn():
        lo, hi = 0.0, 200.0
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            if fires(trial(key, [mid], [PULSE_T0], 50.0)[1]):
                hi = mid
            else:
                lo = mid
        return dict(A1=np.array(hi))
    return float(P.npz_cache(CACHE / f"A1_{key}.npz", fn, I0=round(I0_P3[key], 6), it=30,
                             max_step=MAX_STEP)["A1"])


A1 = {k: threshold_A1(k) for k in ("c1", "c2")}


def pair_grid(key):
    """Fired (bool) for dt = 1..20 ms."""
    a = PAIR_FRAC * A1[key]

    def fn():
        return dict(fired=np.array([fires(trial(key, [a, a], [PULSE_T0, PULSE_T0 + d],
                                                d + 40.0)[1]) for d in range(1, 21)]))
    return P.npz_cache(CACHE / f"grid_{key}.npz", fn, a=round(a, 6), max_step=MAX_STEP)["fired"]


def pair_trial(key, d):
    a = PAIR_FRAC * A1[key]

    def fn():
        t, V, w = trial(key, [a, a], [PULSE_T0, PULSE_T0 + d], d + 40.0)
        return dict(t=t, V=V, w=w)
    return P.npz_cache(CACHE / f"pair_{key}_{d}.npz", fn, a=round(a, 6), d=d, max_step=MAX_STEP,
                       dt=DT)


def single_pulse(key):
    a = PAIR_FRAC * A1[key]

    def fn():
        t, V, w = trial(key, [a], [PULSE_T0], 50.0)
        return dict(t=t, V=V, w=w)
    return P.npz_cache(CACHE / f"single_{key}.npz", fn, a=round(a, 6), max_step=MAX_STEP, dt=DT)


def ring_period(sp):
    """Period between the first two post-pulse peaks (peak times refined by a parabola)."""
    t, V = sp["t"], sp["V"]
    k = np.where((V[1:-1] > V[:-2]) & (V[1:-1] >= V[2:]))[0] + 1
    k = k[t[k] > PULSE_T0]
    y0, y1, y2 = V[k - 1], V[k], V[k + 1]
    tp = t[k] + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) * (t[k + 1] - t[k])
    return float(tp[1] - tp[0]), tp


# ---- everything the scenes draw, computed once (cached runs)
def model_data():
    D = {}
    for k in ("c1", "c2"):
        D[f"stair_{k}"] = st = staircase_run(k)
        D[f"onset_{k}"] = on = onset_run(k, st)
        D[f"stats_{k}"] = staircase_stats(k, st)
        D[f"ostats_{k}"] = onset_stats(on)
        D[f"zoom_{k}"] = zoom_window(on)
        for d in PAIR_DTS:
            D[f"pair_{k}_{d}"] = pair_trial(k, d)
    D["single_c2"] = single_pulse("c2")
    D["T_ring"], D["ring_peaks"] = ring_period(D["single_c2"])
    return D


def frames_per_cycle():
    """(label, f_model Hz, slow-down, frames/cycle) for every displayed oscillation."""
    D = MODEL
    st2 = D["stats_c2"]
    ring_c2 = max(P.ring_hz(s["eig"] / 1000.0) for s in st2)
    o1, o2 = D["ostats_c1"], D["ostats_c2"]
    lam_on = stable_or_any_fp(P.SHUNT, C2_ONSET * IB["c2"])["eig"]
    rows = [
        ("P1 rotation (max 8 Hz)", 8.0, P1_SLOW),
        ("P1 class 2 ladder", P1_OMEGA / (2 * np.pi), P1_SLOW),
        ("P2 class 2 staircase ring", ring_c2, STAIR_SLOW),
        ("P2 class 1 onset firing", o1["rate"], C1_SLOW),
        ("P2 class 2 spiral", P.ring_hz(lam_on), C2_SLOW),
        ("P2 class 2 firing", o2["rate"], C2_SLOW),
        ("P3 class 2 ring", 1000.0 / D["T_ring"], P3_SLOW),
    ]
    return [(n, f, s, FPS * s / f) for n, f, s in rows]


def stable_or_any_fp(p, I):
    fps = P.fixed_points(p, I)
    return next((f for f in fps if f["kind"].startswith("stable")), fps[0])


MODEL = model_data()


# ============================================================ shared screen builders
HEADER_POS = np.array([-6.85, 3.62, 0.0])     # left edge, top-left beat header
BADGE_POS = np.array([6.85, 3.62, 0.0])       # right edge, speed badge
CAPTION_Y = -3.42                             # bottom caption band (1-2 lines)
CAPTION_MAX_W = 13.6
FS_CAP, FS_LAB, FS_TICK = 36, 30, 26

BADGES = {"1/2": R"\times\tfrac{1}{2}", "1/40": R"\times 1/40", "1/10": R"\times 1/10",
          "1/25": R"\times 1/25"}


def header(text, color):
    m = txt(text, font_size=34)
    m.set_fill(color)
    return m.move_to(HEADER_POS, aligned_edge=LEFT)


def speed_badge(key):
    lab = tex(BADGES[key], font_size=36)
    lab.set_fill(WHITE)
    box = RoundedRectangle(width=lab.get_width() + 0.4, height=0.6, corner_radius=0.12)
    box.set_fill(P.CHIP_FILL, 1).set_stroke(P.MUTED, 2)
    lab.move_to(box)
    return VGroup(box, lab).move_to(BADGE_POS, aligned_edge=RIGHT)


def chip(lines, corner, buff=0.14):
    """Chip on CHIP_FILL: lines (mobjects) stacked left-aligned; `corner` = its top-left."""
    body = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    box = RoundedRectangle(width=body.get_width() + 0.4, height=body.get_height() + 0.3,
                           corner_radius=0.1)
    box.set_fill(P.CHIP_FILL, 0.92).set_stroke(P.MUTED, 1.5)
    body.move_to(box)
    return VGroup(box, body).move_to(corner, aligned_edge=UL)


def caption(s, is_tex=False, fs=FS_CAP, **kw):
    """Bottom-band caption. `s` may hold one '\\n' (txt) for two lines; for tex pass a list of
    lines (each centred)."""
    if is_tex and isinstance(s, (list, tuple)):
        m = VGroup(*[tex(x, font_size=fs, **kw) for x in s]).arrange(DOWN, buff=0.14)
    else:
        m = tex(s, font_size=fs, **kw) if is_tex else txt(s, font_size=fs, **kw)
    if m.get_width() > CAPTION_MAX_W:
        m.set_width(CAPTION_MAX_W)
    return m.move_to([0, CAPTION_Y, 0])


class FrameExact:
    """Scene mixin: 60 fps, and every play/wait lasts a whole number of frames."""
    default_camera_config = dict(fps=FPS)

    @staticmethod
    def _frames(x):
        return max(1, round(x * FPS)) / FPS - 1e-7

    def play(self, *anims, run_time=None, **kw):
        if run_time is None:
            run_time = max(prepare_animation(a).get_run_time() for a in anims)
            anims = [prepare_animation(a) for a in anims]
        super().play(*anims, run_time=self._frames(run_time), **kw)

    def wait(self, duration=None, **kw):
        super().wait(self._frames(1.0 if duration is None else duration), **kw)


def label(s, fs=FS_LAB, color=P.INK, **kw):
    m = txt(s, font_size=fs, **kw)
    m.set_fill(color)
    return m


def tlabel(s, fs=FS_LAB, color=P.INK, **kw):
    m = tex(s, font_size=fs, **kw)
    m.set_fill(color)
    return m


def set_runs(vm, runs):
    """Load several polylines ((n, 2) or (n, 3) arrays) into one VMobject, with path breaks."""
    parts = []
    for r in runs:
        if len(r) < 2:
            continue
        A = np.zeros((len(r), 3))
        A[:, :2] = np.asarray(r)[:, :2]
        pts = np.empty((2 * len(A) - 1, 3))
        pts[0::2] = A
        pts[1::2] = 0.5 * (A[:-1] + A[1:])
        if parts:
            parts.append(parts[-1][-1:])      # handle on the previous anchor = path break
        parts.append(pts)
    vm.set_points(np.vstack(parts) if parts else np.zeros((1, 3)))
    return vm


def dash_runs(Pts, dash=0.13, gap=0.09):
    """Split a polyline into dash runs of the given arc length."""
    Pts = np.asarray(Pts)[:, :2]
    if len(Pts) < 2:
        return []
    d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(Pts, axis=0), axis=1))]
    runs = []
    for a in np.arange(0.0, d[-1], dash + gap):
        b = min(a + dash, d[-1])
        k = np.where((d > a) & (d < b))[0]
        pa = [np.interp(a, d, Pts[:, 0]), np.interp(a, d, Pts[:, 1])]
        pb = [np.interp(b, d, Pts[:, 0]), np.interp(b, d, Pts[:, 1])]
        runs.append(np.vstack([pa, Pts[k], pb]))
    return runs


def clip_runs(Pts, box):
    """Split polyline Pts (n, 2) into the runs inside box (x0, x1, y0, y1), edges included."""
    x0, x1, y0, y1 = box
    Pts = np.asarray(Pts)[:, :2]
    inside = (Pts[:, 0] >= x0) & (Pts[:, 0] <= x1) & (Pts[:, 1] >= y0) & (Pts[:, 1] <= y1)

    def cross(p_in, p_out):
        dd = p_out - p_in
        s = 1.0
        for k, lo, hi in ((0, x0, x1), (1, y0, y1)):
            if dd[k] > 0:
                s = min(s, (hi - p_in[k]) / dd[k])
            elif dd[k] < 0:
                s = min(s, (lo - p_in[k]) / dd[k])
        return p_in + max(s, 0.0) * dd

    runs, n, i = [], len(Pts), 0
    while i < n:
        if not inside[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and inside[j + 1]:
            j += 1
        seg = [Pts[i:j + 1]]
        if i > 0:
            seg.insert(0, cross(Pts[i], Pts[i - 1])[None])
        if j < n - 1:
            seg.append(cross(Pts[j], Pts[j + 1])[None])
        run = np.vstack(seg)
        if len(run) >= 2:
            runs.append(run)
        i = j + 1
    return runs


def fade_env(a, t_in, t_out, total, ramp=0.25):
    """Opacity at alpha a of a play of length `total` s: up at t_in, down at t_out (video s)."""
    t = a * total
    up = np.clip((t - t_in) / ramp, 0, 1) if ramp > 0 else float(t >= t_in)
    down = 1 - np.clip((t - t_out) / ramp, 0, 1)
    return float(min(up, down))


def swap_in(new, total, start=0.0, ramp=0.3):
    """FadeIn inside a longer play (starting `start` s into it)."""
    a0, a1 = start / total, min((start + ramp) / total, 1.0)
    return FadeIn(new, rate_func=squish_rate_func(smooth, a0, a1))


def swap_out(old, total, start=0.0, ramp=0.3):
    a0, a1 = start / total, min((start + ramp) / total, 1.0)
    return FadeOut(old, rate_func=squish_rate_func(smooth, a0, a1))


# ============================================================ Part 1 layout
S1 = 2.0                                  # scene units per unit of z (both panels)
PC = np.array([-3.95, -0.05])             # complex-plane origin (rest)
ZMAX = 1.2
RP_X0, RP_X1 = 0.35, 6.7                  # trace panel time axis
Y_BOT = PC[1] - S1 * ZMAX                 # trace panel bottom (= plane bottom)
Y_TOP = PC[1] + S1 * ZMAX
SCROLL_WIN = 1.5                          # s of model time held in the rotation beat
SL_X0, SL_X1 = 0.35, 2.35                 # slider bars
SL_Y = (3.62, 3.12)
RE_RANGE, IM_RANGE = (-22.0, 2.0), (0.0, 56.0)


def plane_pt(z):
    z = np.asarray(z, complex)
    return np.column_stack([PC[0] + S1 * z.imag, PC[1] + S1 * z.real])


def trace_pts(t, re, t_left, width):
    return np.column_stack([RP_X0 + (np.asarray(t) - t_left) / width * (RP_X1 - RP_X0),
                            PC[1] + S1 * np.asarray(re)])


class Seg:
    """One Part-1 segment: z(t) (complex), readouts Re/Im lambda (s^-1), trace window."""

    def __init__(self, dur, z, re_l, im_l, window, color, scroll=False, env=None, kick=False):
        self.dur, self.z, self.re_l, self.im_l = dur, z, re_l, im_l
        self.window, self.color, self.scroll, self.env, self.kick = (window, color, scroll, env,
                                                                    kick)


def seg_rest(z0=0.0, re_l=-20.0, im_l=0.0, color=P.CLASS1):
    return Seg(0.0, lambda t: np.full(np.shape(t), z0, complex), lambda t: re_l,
               lambda t: im_l, 1.0, color)


def seg_class1(lam, window):
    return Seg(window, lambda t: np.exp(lam * np.asarray(t, float)).astype(complex),
               lambda t: lam, lambda t: 0.0, window, P.CLASS1,
               env=[lambda t: np.exp(lam * t)], kick=True)


def seg_rotation():
    return Seg(P1_ROT_T, lambda t: np.exp(1j * rot_phase(t)), lambda t: 0.0,
               lambda t: 2 * np.pi * float(rot_freq(t)), SCROLL_WIN, P.CLASS2, scroll=True)


def seg_class2(sigma, window):
    return Seg(window, lambda t: np.exp((sigma + 1j * P1_OMEGA) * np.asarray(t, float)),
               lambda t: sigma, lambda t: P1_OMEGA, window, P.CLASS2,
               env=[lambda t: np.exp(sigma * t), lambda t: -np.exp(sigma * t)], kick=True)


TICKS_P1 = {1.2: [0, 0.4, 0.8, 1.2], 3.0: [0, 1, 2, 3], 2.0: [0, 0.5, 1, 1.5, 2],
            1.0: [0, 0.5, 1.0]}


def fmt_tick(v):
    return f"{v:g}"


def time_ticks(window):
    g = VGroup()
    for v in TICKS_P1[window]:
        x = RP_X0 + v / window * (RP_X1 - RP_X0)
        tk = Line([x, Y_BOT, 0], [x, Y_BOT - 0.1, 0]).set_stroke(P.MUTED, 2)
        lb = label(fmt_tick(v), FS_TICK, P.MUTED).next_to(tk, DOWN, buff=0.06)
        g.add(VGroup(tk, lb))
    return g


class EigenvalueDecayVsRing(FrameExact, Scene):
    """Part 1 (0-31.6 s): the lambda plane. Re is vertical, lined up with the delta-V trace."""

    def construct(self):
        self.T = ValueTracker(0.0)
        self.seg = seg_rest(re_l=P1_C1_LAMBDAS[0])
        self.p1_setup()
        self.p1_class1_ladder()
        self.p1_to_class2()
        self.p1_rotation()
        self.p1_class2_ladder()
        self.p1_outro()
        print(f"PART1 duration {self.time:.3f} s")

    # ------------------------------------------------------------------ helpers
    def z_now(self):
        return complex(self.seg.z(np.array([self.T.get_value()]))[0])

    def run_seg(self, seg, video_s, *extra):
        self.seg = seg
        self.T.set_value(0.0)
        self.update_mobjects(0)
        self.play(self.T.animate.set_value(seg.dur).set_anim_args(rate_func=linear), *extra,
                  run_time=video_s)

    def set_caption(self, new, total=None, start=0.0):
        """Animations that swap the caption (inside a play of length `total`)."""
        old = self.cap
        self.cap = new
        if total is None:
            return [FadeOut(old), FadeIn(new)] if old is not None else [FadeIn(new)]
        anims = [swap_in(new, total, start)]
        if old is not None:
            anims.append(swap_out(old, total, start))
        return anims

    def kick_anim(self, total):
        """Kick arrow + label: on at the kick, off after 0.9 s of video."""
        g = self.kick.copy()
        self.add(g)
        return UpdateFromAlphaFunc(g, lambda m, a: m.set_opacity(fade_env(a, -1.0, 0.7, total)),
                                   remover=True)

    # ------------------------------------------------------------------ beats
    def p1_setup(self):
        ## Part 1 setup: axes appear
        # complex plane
        ext = S1 * ZMAX
        ax_h = Line([PC[0] - ext, PC[1], 0], [PC[0] + ext, PC[1], 0])
        ax_v = Line([PC[0], PC[1] - ext, 0], [PC[0], PC[1] + ext, 0])
        for a in (ax_h, ax_v):
            a.set_stroke(P.MUTED, 2)
            a.add_tip(length=0.16, width=0.14)
            a.tip.set_fill(P.MUTED).set_stroke(width=0)
        ticks = VGroup()
        for v in (-1, 1):
            ticks.add(Line([PC[0] + S1 * v, PC[1] - 0.07, 0], [PC[0] + S1 * v, PC[1] + 0.07, 0]))
            ticks.add(Line([PC[0] - 0.07, PC[1] + S1 * v, 0], [PC[0] + 0.07, PC[1] + S1 * v, 0]))
        ticks.set_stroke(P.MUTED, 2)
        tl = VGroup(
            label("1", FS_TICK, P.MUTED).move_to([PC[0] + S1, PC[1] + 0.27, 0]),
            label("−1", FS_TICK, P.MUTED).move_to([PC[0] - S1, PC[1] + 0.27, 0]),
            label("1", FS_TICK, P.MUTED).next_to([PC[0] - 0.07, PC[1] + S1, 0], LEFT, 0.1),
            label("−1", FS_TICK, P.MUTED).next_to([PC[0] - 0.07, PC[1] - S1, 0], LEFT, 0.1),
        )
        lab_im = tlabel(R"\mathrm{Im}", FS_LAB, P.MUTED).next_to(ax_h.get_end(), DOWN, 0.14)
        lab_re = VGroup(tlabel(R"\mathrm{Re} = \delta V", FS_LAB, P.INK),
                        label("(what the electrode sees)", FS_TICK, P.MUTED)).arrange(RIGHT, buff=0.2)
        lab_re.next_to([PC[0], Y_TOP + 0.18, 0], UP, buff=0.05)
        rest_dot = Dot([PC[0], PC[1], 0], radius=0.06, fill_color=P.MUTED)
        rest_lab = label("rest (fixed point)", FS_TICK, P.MUTED)
        rest_lab.next_to([PC[0], PC[1], 0], DL, buff=0.12)
        self.plane = VGroup(ax_h, ax_v, ticks, tl, lab_im, lab_re, rest_dot, rest_lab)

        # trace panel
        tax = Line([RP_X0, Y_BOT, 0], [RP_X1 + 0.1, Y_BOT, 0]).set_stroke(P.MUTED, 2)
        vax = Line([RP_X0, Y_BOT, 0], [RP_X0, Y_TOP, 0]).set_stroke(P.MUTED, 2)
        vax.add_tip(length=0.16, width=0.14)
        vax.tip.set_fill(P.MUTED).set_stroke(width=0)
        zero = VMobject().set_stroke(GREY_D, 2)
        set_runs(zero, dash_runs([[RP_X0, PC[1]], [RP_X1, PC[1]]], 0.1, 0.1))
        vticks = VGroup(*[Line([RP_X0 - 0.07, PC[1] + S1 * v, 0], [RP_X0 + 0.07, PC[1] + S1 * v, 0])
                          for v in (-1, 1)]).set_stroke(P.MUTED, 2)
        lab_dv = tlabel(R"\delta V", FS_LAB, P.INK).next_to(vax.get_end(), RIGHT, buff=0.12)
        lab_t = label("time (s)", FS_TICK, P.MUTED).move_to([RP_X1, Y_BOT + 0.25, 0],
                                                            aligned_edge=RIGHT)
        self.tpanel = VGroup(tax, vax, zero, vticks, lab_dv, lab_t)
        self.tticks = time_ticks(P1_C1_WINDOWS[0])

        # sliders
        self.sliders = self.make_sliders()

        # dynamic: path in the plane, state dot, trace, trace head, projector, envelope
        self.path = VMobject(stroke_width=3, fill_opacity=0)
        self.dot = Dot(radius=0.09, fill_color=P.STATE_DOT, stroke_color=BLACK, stroke_width=1.5)
        self.trace = VMobject(stroke_color=P.VOLT, stroke_width=4, fill_opacity=0)
        self.head = Dot(radius=0.06, fill_color=P.VOLT)
        self.proj = VMobject(stroke_color=P.MUTED, stroke_width=2, fill_opacity=0)
        self.env = VMobject(stroke_width=2.5, fill_opacity=0)
        self.path.add_updater(self.upd_path)
        self.trace.add_updater(self.upd_trace)
        self.dot.add_updater(lambda m: m.move_to([*plane_pt(self.z_now())[0], 0]))
        self.head.add_updater(self.upd_head)
        self.proj.add_updater(self.upd_proj)
        self.env.add_updater(self.upd_env)
        self.scroll_ticks = self.make_scroll_ticks()

        # kick arrow + label (copied per kick)
        arr = Arrow([PC[0] + 0.22, PC[1], 0], [PC[0] + 0.22, PC[1] + S1, 0], buff=0,
                    thickness=4, fill_color=P.HIGHLIGHT)
        kl = label("kick (brief current pulse)", FS_TICK, P.HIGHLIGHT)
        kl.next_to([PC[0] - 0.15, PC[1] + 0.55 * S1, 0], LEFT, buff=0.05)
        self.kick = VGroup(arr, kl)

        self.hdr = header("Class 1 (integrator)", P.CLASS1)
        self.foot = label("cartoon of the linearized dynamics · units schematic", FS_TICK, P.MUTED)
        self.foot.move_to(HEADER_POS + np.array([0, -0.48, 0]), aligned_edge=LEFT)
        self.cap = caption("Real λ: straight back to rest, no overshoot. |λ| sets how fast.")
        self.badge = None
        self.note = None

        # first frame of the whole video: layout + first caption (reads when paused)
        self.add(self.plane, self.tpanel, self.tticks, self.sliders, self.hdr, self.foot,
                 self.path, self.env, self.trace, self.proj, self.head, self.dot, self.cap)
        self.wait(P1_LEAD)

    def make_sliders(self):
        g = VGroup()
        self.sl_knobs = []
        for row, (rng, y) in enumerate(zip((RE_RANGE, IM_RANGE), SL_Y)):
            bar = Line([SL_X0, y, 0], [SL_X1, y, 0]).set_stroke(GREY_C, 5)
            x0 = SL_X0 + (0 - rng[0]) / (rng[1] - rng[0]) * (SL_X1 - SL_X0)
            zt = Line([x0, y - 0.13, 0], [x0, y + 0.13, 0]).set_stroke(P.MUTED, 2)
            knob = Dot(radius=0.1, fill_color=WHITE, stroke_color=BLACK, stroke_width=1.5)

            def upd_knob(m, rng=rng, y=y, row=row):
                t = self.T.get_value()
                v = self.seg.re_l(t) if row == 0 else self.seg.im_l(t)
                x = SL_X0 + (np.clip(v, *rng) - rng[0]) / (rng[1] - rng[0]) * (SL_X1 - SL_X0)
                m.move_to([x, y, 0])
            knob.add_updater(upd_knob)
            g.add(bar, zt, knob)
        # readouts
        re_lab = tlabel(R"\mathrm{Re}\,\lambda =", FS_LAB)
        re_num = DecimalNumber(P1_C1_LAMBDAS[0], num_decimal_places=1, font_size=FS_LAB)
        re_unit = tlabel(R"\mathrm{s}^{-1}", FS_LAB)
        im_lab = tlabel(R"\mathrm{Im}\,\lambda =", FS_LAB)
        im_num = DecimalNumber(0.0, num_decimal_places=1, font_size=FS_LAB)
        im_unit = tlabel(R"\mathrm{s}^{-1}", FS_LAB)
        lpar, rpar = tlabel("(", FS_LAB), tlabel(")", FS_LAB)
        hz_num = DecimalNumber(0.0, num_decimal_places=1, font_size=FS_LAB)
        hz_unit = tlabel(R"\mathrm{Hz}", FS_LAB)
        x_read = SL_X1 + 0.3
        re_lab.move_to([x_read, SL_Y[0], 0], aligned_edge=LEFT)
        im_lab.move_to([x_read, SL_Y[1], 0], aligned_edge=LEFT)

        def upd_read(_):
            t = self.T.get_value()
            re, im = self.seg.re_l(t), self.seg.im_l(t)
            re_num.set_value(re)
            im_num.set_value(im)
            hz_num.set_value(im / (2 * np.pi))
            re_num.next_to(re_lab, RIGHT, buff=0.15)
            re_unit.next_to(re_num, RIGHT, buff=0.1)
            im_num.next_to(im_lab, RIGHT, buff=0.15)
            im_unit.next_to(im_num, RIGHT, buff=0.1)
            for m, ref in ((re_num, re_lab), (im_num, im_lab)):
                m.align_to(ref, DOWN)
            re_unit.next_to(re_num, RIGHT, buff=0.1, aligned_edge=DOWN)
            im_unit.next_to(im_num, RIGHT, buff=0.1, aligned_edge=DOWN)
            lpar.next_to(im_unit, RIGHT, buff=0.18)
            lpar.set_y(im_num.get_y())
            hz_num.next_to(lpar, RIGHT, buff=0.05)
            hz_num.align_to(im_num, DOWN)
            hz_unit.next_to(hz_num, RIGHT, buff=0.1, aligned_edge=DOWN)
            rpar.next_to(hz_unit, RIGHT, buff=0.05)
            rpar.set_y(im_num.get_y())
            re_unit.align_to(re_num, DOWN).shift(0 * UP)
        reads = VGroup(re_lab, re_num, re_unit, im_lab, im_num, im_unit, lpar, hz_num, hz_unit,
                       rpar)
        reads.add_updater(upd_read)
        upd_read(None)
        g.add(reads)
        return g

    def make_scroll_ticks(self):
        vals = np.arange(0, P1_ROT_T + 1e-9, 0.5)
        g = VGroup()
        for v in vals:
            tk = Line([0, Y_BOT, 0], [0, Y_BOT - 0.1, 0]).set_stroke(P.MUTED, 2)
            lb = label(fmt_tick(v), FS_TICK, P.MUTED).next_to(tk, DOWN, buff=0.06)
            g.add(VGroup(tk, lb))

        def upd(grp):
            t = self.T.get_value()
            left = max(0.0, t - SCROLL_WIN)
            for v, m in zip(vals, grp):
                x = RP_X0 + (v - left) / SCROLL_WIN * (RP_X1 - RP_X0)
                m.move_to([x, m.get_center()[1], 0])
                m.set_opacity(1.0 if left - 1e-9 <= v <= left + SCROLL_WIN + 1e-9 else 0.0)
        g.add_updater(upd)
        return g

    def window_now(self):
        t = self.T.get_value()
        if self.seg.scroll:
            return max(0.0, t - SCROLL_WIN), SCROLL_WIN
        return 0.0, self.seg.window

    def trace_samples(self):
        t = self.T.get_value()
        left, width = self.window_now()
        if t <= left or self.seg.dur == 0:
            return None
        n = int(np.clip((t - left) / width * 700, 2, 700))
        ts = np.linspace(left, t, n)
        return trace_pts(ts, self.seg.z(ts).real, left, width)

    def upd_trace(self, m):
        pts = self.trace_samples()
        set_runs(m, [pts] if pts is not None else [])
        m.set_stroke(opacity=1.0 if pts is not None else 0.0)

    def upd_head(self, m):
        pts = self.trace_samples()
        if pts is None:
            m.set_opacity(0)
            return
        m.set_opacity(1)
        m.move_to([*pts[-1], 0])

    def upd_path(self, m):
        t = self.T.get_value()
        if self.seg.dur == 0 or t <= 0:
            m.set_stroke(opacity=0)
            return
        t0 = max(0.0, t - 1.0) if self.seg.scroll else 0.0
        ts = np.linspace(t0, t, 500)
        set_runs(m, [plane_pt(self.seg.z(ts))])
        m.set_stroke(self.seg.color, 3, opacity=0.9)

    def upd_proj(self, m):
        pts = self.trace_samples()
        zp = plane_pt(self.z_now())[0]
        if pts is None:
            m.set_stroke(opacity=0)
            return
        tip = pts[-1]
        set_runs(m, dash_runs([zp + [0.12, 0], [tip[0] - 0.1, zp[1]]], 0.12, 0.1))
        m.set_stroke(P.MUTED, 2, opacity=1)

    def upd_env(self, m):
        if not self.seg.env or self.seg.scroll:
            m.set_stroke(opacity=0)
            return
        W = self.seg.window
        ts = np.linspace(0, W, 400)
        runs = []
        for f in self.seg.env:
            runs += dash_runs(trace_pts(ts, f(ts), 0.0, W), 0.12, 0.09)
        set_runs(m, runs)
        m.set_stroke(self.seg.color, 2.5, opacity=0.95)

    def rebuild(self, new_window, video_s, *extra, z_rest=0.0, re_l=None, im_l=None,
                color=None):
        """Between rungs: point at rest, trace cleared, time axis rebuilt."""
        prev = self.seg
        t = self.T.get_value()
        z_prev = self.z_now()
        re_v = prev.re_l(t) if re_l is None else re_l
        im_v = prev.im_l(t) if im_l is None else im_l
        mover = ValueTracker(0.0)
        self.seg = Seg(0.0, lambda tt: np.full(np.shape(tt), z_prev + (z_rest - z_prev)
                                               * mover.get_value(), complex),
                       lambda tt: re_v, lambda tt: im_v, 1.0, color or prev.color)
        self.T.set_value(0.0)
        new_ticks = time_ticks(new_window) if new_window else VGroup()
        anims = [FadeOut(self.tticks, rate_func=squish_rate_func(smooth, 0.0, 0.5)),
                 FadeIn(new_ticks, rate_func=squish_rate_func(smooth, 0.5, 1.0)),
                 mover.animate.set_value(1.0)]
        anims += list(extra)
        self.play(*anims, run_time=video_s)
        self.tticks = new_ticks

    def p1_class1_ladder(self):
        ## Class 1 kick -> decay ladder (1x)
        cap2 = caption("λ → 0: the return takes forever (critical slowing) —\n"
                       "why class 1 can fire arbitrarily slowly.")
        for i, (lam, W) in enumerate(zip(P1_C1_LAMBDAS, P1_C1_WINDOWS)):
            if i > 0:
                self.wait(P1_HOLD)
                self.rebuild(W, P1_RESET, re_l=lam, im_l=0.0)
            extra = [self.kick_anim(W)]
            if i == len(P1_C1_LAMBDAS) - 1:
                extra += self.set_caption(cap2, W, 0.0)
            self.run_seg(seg_class1(lam, W), W, *extra)

    def p1_to_class2(self):
        ## Header -> class 2, badge x1/2, point to z = 1
        new_hdr = header("Class 2 (resonator)", P.CLASS2)
        self.badge = speed_badge("1/2")
        cap = caption("Im λ sets how fast it rotates → the ring frequency.")
        self.note = label("Re λ = 0 exactly: the idealized edge.", FS_TICK, P.MUTED)
        self.note.move_to([RP_X1, Y_TOP + 0.05, 0], aligned_edge=RIGHT)
        mover = ValueTracker(0.0)
        self.seg = Seg(0.0, lambda t: np.full(np.shape(t), mover.get_value(), complex),
                       lambda t: 0.0, lambda t: 2 * np.pi * 2.0, 1.0, P.CLASS2)
        self.T.set_value(0.0)
        self.play(FadeTransform(self.hdr, new_hdr), FadeIn(self.badge), FadeOut(self.tticks),
                  mover.animate.set_value(1.0), *self.set_caption(cap),
                  FadeIn(self.note), run_time=1.0)
        self.hdr = new_hdr
        self.tticks = VGroup()
        self.add(self.scroll_ticks)
        self.wait(P1_LEAD)

    def p1_rotation(self):
        ## Pure rotation at Re lambda = 0, Im lambda/2pi 2 -> 8 -> 2 Hz (x1/2)
        self.run_seg(seg_rotation(), P1_ROT_T * P1_SLOW)

    def p1_class2_ladder(self):
        ## Class 2 kick -> decay ladder at 5 Hz (x1/2)
        cap = caption("Re λ sets how fast the voltage decays.")
        for i, (sig, W) in enumerate(zip(P1_C2_SIGMAS, P1_C2_WINDOWS)):
            f = per_cycle(sig)
            note = tlabel(Rf"\times {f:.2f}\ \text{{per cycle}}", FS_TICK, P.MUTED)
            note.move_to([RP_X1, Y_TOP + 0.05, 0], aligned_edge=RIGHT)
            extra = [FadeOut(self.note), FadeIn(note)]
            if i == 0:
                self.remove(self.scroll_ticks)
                extra += self.set_caption(cap)
            else:
                self.wait(P1_HOLD)
            self.rebuild(W, 0.3 if i == 0 else P1_RESET, *extra, re_l=sig, im_l=P1_OMEGA,
                         color=P.CLASS2)
            self.note = note
            if i == 0:
                self.wait(P1_LEAD)
            self.run_seg(seg_class2(sig, W), W * P1_SLOW, self.kick_anim(W * P1_SLOW))

    def p1_outro(self):
        ## Fade out Part 1: axes swap warning
        for m in (self.path, self.trace, self.head, self.proj, self.env, self.dot):
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
        self.wait(0.2)


# ============================================================ PARTS 2-3 SCENES (below)
# ============================================================ Part 2 data + layout
PP_BOX = (-5.45, 0.7, -2.2, 1.9)          # phase-plane plot area (scene units)
SUB_WIN = (-70.0, -25.0, 0.0, 0.015)      # subthreshold zoom (V mV, w)
AX_OFF = 0.14                             # axes sit this far outside the plot area
VT_RANGE = {"c1": (-75.0, 30.0), "c2": (-75.0, 25.0)}
TAIL_MS = 30.0
CHIP_CORNER = np.array([-6.85, 3.28, 0.0])
P2_SUB_WIN = (-80.0, -17.0, 0.0, 0.024)   # Part 2 subthreshold view (V mV, w); Part 3 keeps SUB_WIN
P2_ZOOM_OUT = 1.2                         # full view = limit-cycle window x this, in warped units
P2_W_FLOOR = 0.015                        # warped units below w = 0, so rest sits off the axis
P2_V_MIN = -90.0                          # never widen past this (V-nullcline pole at E_K = -100)
CLASS_NAME = {"c1": "Class 1 (integrator)", "c2": "Class 2 (resonator)"}
CLASS_COLOR = {"c1": P.CLASS1, "c2": P.CLASS2}
P2_TAG = {"c1": "Class 1 · SNIC", "c2": "Class 2 · Hopf"}
P2_VT_BOX = (2.0, 6.6, 0.0, 2.55)         # V(t): the whole class run, builds up, no scrolling
P2_CUR_BOX = (2.0, 6.6, -2.05, -1.35)     # injected-current strip (no numbers)
P2_VT_FULL = (-80.0, 35.0)                # mV
P2_VT_ZOOM = (-48.0, -26.0)               # class 2 V(t) before its zoom-out, so the rings show
P2_BAR_Y = -0.62                          # scale bars sit under the V(t) box
TRAIL_RECENT, OLD_TRAIL_OP = 30.0, 0.35   # ms of trail drawn opaque; opacity of the rest
READOUT_POS = np.array([6.85, 2.95, 0.0])
FS_P2_CAP = 40
P2_CAPS = {"sweep": "current lifts the V-nullcline; the fixed point slides along",
           "c1": "arbitrarily slow firing",
           "c2": "already ringing when it lets go → fires fast at once"}
# inline nullcline labels: per class, (sub view, full view) x (V label, w label), each
# (height fraction of the plot, side of the curve, branch: "left" = before the curve's lowest
# point, "right" = after it)
NULL_LABEL_SPEC = {
    "c1": (((0.9, RIGHT, "left"), (0.9, UL, "right")),
           ((0.4, RIGHT, "left"), (0.85, RIGHT, "right"))),
    "c2": (((0.9, RIGHT, "left"), (0.3, DR, "right")),
           ((0.55, RIGHT, "left"), (0.5, LEFT, "right"))),
}


def class_run(key):
    """Staircase (0-200 ms) + onset step (200 ms on) as one model-time series."""
    st, on = MODEL[f"stair_{key}"], MODEL[f"onset_{key}"]
    Ib, lv = IB[key], LEVELS[key]
    t = np.r_[st["t"], len(lv) * HOLD + on["t"][1:]]
    V = np.r_[st["V"], on["V"][1:]]
    w = np.r_[st["w"], on["w"][1:]]
    I = np.r_[stair_I(key, st["t"]), np.full(len(on["t"]) - 1, ONSET[key][0] * Ib)]
    return dict(t=t, V=V, w=w, I=I)


def ghost_point():
    fp = P.fixed_points(P.CONTROL, IB["c1"])[0]
    return fp["V"], fp["w"]


def lift_I(a):
    """Class 1 lift 0.9 -> I_bif (a = 0.9, the merge): most of it spent where the saddle
    exists (I_min = 0.9727 I_bif .. I_bif)."""
    Ib = IB["c1"]
    pts = [(0.0, 0.9), (0.3, 0.9727), (0.9, 1.0), (1.0, C1_ONSET)]
    return Ib * float(np.interp(a, [p[0] for p in pts], [p[1] for p in pts]))


def lift2_I(a):
    """Class 2 lift 0.99 -> 1.0 I_bif (Re lambda -> 0), as a fraction of I_bif: most of it
    spent close to the crossing."""
    return float(np.interp(a, [0.0, 0.45, 1.0], [0.99, 0.998, 1.0]))


def p2_t_axis(key):
    """Model ms on the V(t) / current time axis: the whole class run."""
    return len(LEVELS[key]) * HOLD + ONSET[key][1]


def vt_range(key, a):
    """V(t) range: class 1 fixed; class 2 zoomed on its rings, opening with the plane's zoom."""
    if key == "c1":
        return P2_VT_FULL
    return tuple((1 - a) * np.array(P2_VT_ZOOM) + a * np.array(P2_VT_FULL))


def decimate(t, X, Y, min_step, max_dt):
    """Indices of samples at least min_step apart in (X, Y), or max_dt apart in time."""
    keep = [0]
    lx, ly, lt = X[0], Y[0], t[0]
    for i in range(1, len(t)):
        if np.hypot(X[i] - lx, Y[i] - ly) >= min_step or t[i] - lt >= max_dt:
            keep.append(i)
            lx, ly, lt = X[i], Y[i], t[i]
    if keep[-1] != len(t) - 1:
        keep.append(len(t) - 1)
    return np.array(keep)


def flash_ring(c, r0=0.1, grow=0.85):
    """The s05 bifurcation flash, made louder: a thick red ring that grows and fades at c
    (remover)."""
    ring = Circle(radius=r0).set_stroke(P.HIGHLIGHT, 10).move_to(c)

    def f(m, a):
        m.set_width(2 * (r0 + grow * a))
        m.move_to(c)
        m.set_stroke(P.HIGHLIGHT, 10 * (1 - a) + 2, opacity=(1 - a) ** 0.7)
    return UpdateFromAlphaFunc(ring, f, remover=True, rate_func=linear)


def half_dot(c, r=0.1):
    """Half-filled dot: node (filled) and saddle (open) at the moment they merge."""
    a = np.linspace(PI / 2, 3 * PI / 2, 25)
    disk = Polygon(*[[r * np.cos(x), r * np.sin(x), 0] for x in a])
    disk.set_fill(WHITE, 1).set_stroke(width=0)
    ring = Circle(radius=r).set_fill(BLACK, 1).set_stroke(WHITE, 3)
    return VGroup(ring, disk).move_to(c)


def warp_v(V):
    """Phase-plane display warp (the s05 videos'): stretches the knee, squeezes the spike."""
    return np.arcsinh((np.asarray(V, dtype=float) + 36.0) / 8.0)


def warp_w(w):
    """Signed w^0.4, so negative w (V-nullcline below zero) falls below the view and clips."""
    w = np.asarray(w, dtype=float)
    return np.sign(w) * np.abs(w) ** 0.4


def unwarp_v(x):
    return 8.0 * np.sinh(x) - 36.0


def warped_win(win, grow=1.0):
    """(V0, V1, w0, w1) in model units -> warped window, widened about its centre by grow."""
    x0, x1 = warp_v(win[0]), warp_v(win[1])
    y0, y1 = warp_w(win[2]), warp_w(win[3])
    cx, hx = (x0 + x1) / 2, grow * (x1 - x0) / 2
    hy = grow * (y1 - y0)
    return float(max(cx - hx, warp_v(P2_V_MIN))), float(cx + hx), -P2_W_FLOOR, float(y0 + hy)


SUB_WARP = warped_win(P2_SUB_WIN)


def window_at(a, full):
    """Warped plot window at zoom a (0 = subthreshold, 1 = full limit-cycle window, given in
    model units): centre linear, size geometric, as in the s05 videos."""
    k0, k1, k2, k3 = SUB_WARP
    f0, f1, f2, f3 = warped_win(full, P2_ZOOM_OUT)
    cx = (1 - a) * (k0 + k1) / 2 + a * (f0 + f1) / 2
    cy = (1 - a) * (k2 + k3) / 2 + a * (f2 + f3) / 2
    sx = (k1 - k0) ** (1 - a) * (f1 - f0) ** a
    sy = (k3 - k2) ** (1 - a) * (f3 - f2) ** a
    return cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2


def warped_to_scene(X, Y, win):
    """Warped (X, Y) -> scene (x, y) in PP_BOX for a warped window."""
    x0, x1, y0, y1 = PP_BOX
    return np.column_stack([x0 + (np.asarray(X) - win[0]) / (win[1] - win[0]) * (x1 - x0),
                            y0 + (np.asarray(Y) - win[2]) / (win[3] - win[2]) * (y1 - y0)])


def pp_xy(V, w, win):
    """Model (V, w) -> scene (x, y) in PP_BOX for a warped window."""
    return warped_to_scene(warp_v(np.atleast_1d(V)), warp_w(np.atleast_1d(w)), win)


def win_Vs(win, n=700):
    """V samples spaced evenly across the warped window."""
    return unwarp_v(np.linspace(win[0], win[1], n))


def box_xy(t, y, box, t_left, t_width, yr):
    x0, x1, y0, y1 = box
    return np.column_stack([x0 + (np.asarray(t) - t_left) / t_width * (x1 - x0),
                            y0 + (np.asarray(y) - yr[0]) / (yr[1] - yr[0]) * (y1 - y0)])


def lam_tex(ev):
    """Chip lines for a 2-D eigenvalue pair in s^-1."""
    ev = np.asarray(ev)
    if np.all(np.abs(ev.imag) < 1e-9):
        a, b = sorted(ev.real, key=abs)
        return [Rf"\lambda = {a:.0f},\ {b:.0f}\ \mathrm{{s^{{-1}}}}".replace("-", "{-}")]
    v = ev[np.argmax(ev.imag)]
    f = P.ring_hz(ev / 1000.0)
    k = P.per_cycle_factor(v / 1000.0)
    if k < 0.01:
        e = int(np.floor(np.log10(k)))
        ks = Rf"{k / 10 ** e:.0f}{{\cdot}}10^{{{e}}}"
    else:
        ks = f"{k:.2f}"
    sign = "+" if v.real > 0 else "{-}"
    return [Rf"\lambda = {sign}{abs(v.real):.0f} \pm {abs(v.imag):.0f}i\ \mathrm{{s^{{-1}}}}",
            Rf"\text{{ring}} \approx {f:.0f}\ \text{{Hz}},\ \times {ks}\ \text{{per cycle}}"]


def lam_chip(ev):
    lines = lam_tex(ev)
    return chip([tlabel(lines[0], FS_LAB)] + [tlabel(s, 28) for s in lines[1:]], CHIP_CORNER)


def text_chip(*strings):
    return chip([label(s, 28) for s in strings], CHIP_CORNER)


def make_live(c, upd):
    """Mark a chip as live (its updater changes digits), with its own opacity c.vis."""
    c.vis = 0.0
    c.live = True
    c.add_updater(upd)
    upd(c)
    return c


def live_chip_opacity(c, texts):
    c[0].set_fill(P.CHIP_FILL, 0.92 * c.vis).set_stroke(P.MUTED, 1.5, c.vis)
    for m in texts:
        m.set_opacity(c.vis)


def chip_fade(m, a0, a1, out):
    """Fade a chip over alpha a0..a1 of its play. Live chips fade through c.vis (a Transform
    fade would break when their digits change mid-play); static chips use FadeIn/FadeOut."""
    if not getattr(m, "live", False):
        rf = squish_rate_func(smooth, a0, a1)
        return FadeOut(m, rate_func=rf) if out else FadeIn(m, rate_func=rf)

    def f(mob, a):
        u = smooth(float(np.clip((a - a0) / max(a1 - a0, 1e-6), 0, 1)))
        mob.vis = 1 - u if out else u
    return UpdateFromAlphaFunc(m, f, remover=out)


class PhasePlaneCurrentSteps(FrameExact, Scene):
    """Part 2: the paper's V-w phase plane in the s05 SNIC/Hopf look; class 1 then class 2.

    Warped plane (asinh V, w^0.4), inline nullcline labels, white fixed points, class-coloured
    trail, V(t) and current that build up over each class run, live lambda chips. Beats:
    sweep 0 -> 0.9 I_bif; class 1 staircase (x1/40); lift to the saddle-node with a live
    "slowest lambda" -> 0, half dot + red flash; slow crawl at the halo (x1/10), zoom, caption;
    class 2 staircase (x1/40, rings); lift through Re lambda = 0 with a live chip, red flash,
    focus opens; spiral (x1/25), zoom, fast firing, caption; fade."""

    def construct(self):
        self.T = ValueTracker(0.0)          # model time (ms) since the class run started
        self.Z = ValueTracker(0.0)          # zoom: 0 subthreshold, 1 limit-cycle window
        self.Iov = ValueTracker(0.0)        # displayed I while model time is frozen
        self.use_ov = True
        self.traj_op = ValueTracker(0.0)    # trajectory + traces visibility
        self.ghost_op = ValueTracker(0.0)
        self.null_lab_op = ValueTracker(1.0)
        self.bar_op = ValueTracker(1.0)     # live scale bars (class 2), faded in with the class
        self.intro = ValueTracker(0.0)      # opacity of updater-driven layout (fade in / out)
        self.fp_cache = {}
        self.set_class("c1")
        self.p2_setup()
        self.p2_sweep()
        self.p2_class1_staircase()
        self.p2_class1_lift()
        self.p2_class1_onset()
        self.p2_to_class2()
        self.p2_class2_staircase()
        self.p2_class2_lift()
        self.p2_class2_onset()
        print(f"PART2 duration {self.time:.3f} s")

    # ------------------------------------------------------------------ state
    def set_class(self, key):
        self.key = key
        self.p = PARAMS[key]
        self.run = r = class_run(key)
        self.full = MODEL[f"zoom_{key}"]
        # trail in warped units, decimated at the finest (subthreshold) scale
        X, Y = warp_v(r["V"]), warp_w(r["w"])
        S = warped_to_scene(X, Y, SUB_WARP)
        k = decimate(r["t"], S[:, 0], S[:, 1], 0.01, 0.5)
        self.tr = dict(t=r["t"][k], X=X[k], Y=Y[k])
        B = box_xy(r["t"], r["V"], P2_VT_BOX, 0, p2_t_axis(key), vt_range(key, 0.0))
        k = decimate(r["t"], B[:, 0], B[:, 1], 0.006, 0.5)
        self.vt_data = dict(t=r["t"][k], V=r["V"][k])
        C = box_xy(r["t"], r["I"], P2_CUR_BOX, 0, p2_t_axis(key), (0.0, 1.1 * IB[key]))
        k = decimate(r["t"], C[:, 0], C[:, 1], 0.006, 2.0)
        self.cur_data = (r["t"][k], r["I"][k])

    def win(self):
        return window_at(self.Z.get_value(), self.full)

    def I_now(self):
        if self.use_ov:
            return self.Iov.get_value()
        return float(np.interp(self.T.get_value(), self.run["t"], self.run["I"]))

    def state(self, t):
        r = self.run
        return float(np.interp(t, r["t"], r["V"])), float(np.interp(t, r["t"], r["w"]))

    def fps_now(self):
        I = round(self.I_now(), 5)
        key = (self.key, I)
        if key not in self.fp_cache:
            self.fp_cache[key] = P.fixed_points(self.p, I)
        return self.fp_cache[key]

    def scr(self, V, w):
        return np.array([*pp_xy(V, w, self.win())[0], 0.0])

    def inside(self, pt):
        x0, x1, y0, y1 = PP_BOX
        return x0 - 1e-6 <= pt[0] <= x1 + 1e-6 and y0 - 1e-6 <= pt[1] <= y1 + 1e-6

    # ------------------------------------------------------------------ builders
    def build_axes(self):
        x0, x1, y0, y1 = PP_BOX
        ax_x = Line([x0 - AX_OFF, y0 - AX_OFF, 0], [x1 + 0.15, y0 - AX_OFF, 0])
        ax_y = Line([x0 - AX_OFF, y0 - AX_OFF, 0], [x0 - AX_OFF, y1 + 0.15, 0])
        for a in (ax_x, ax_y):
            a.set_stroke(P.MUTED, 2)
            a.add_tip(length=0.15, width=0.13)
            a.tip.set_fill(P.MUTED).set_stroke(width=0)
        lab_v = tlabel("V", FS_LAB + 2, P.MUTED).next_to(ax_x.get_end(), DOWN, buff=0.12)
        lab_v.align_to(ax_x.get_end(), RIGHT)
        lab_w = tlabel("w", FS_LAB + 2, P.MUTED).next_to(ax_y.get_end(), RIGHT, buff=0.14)
        lab_w.align_to(ax_y.get_end(), UP)
        lab_k = label("K⁺ activation", 26, P.MUTED).rotate(PI / 2)
        lab_k.next_to(ax_y, LEFT, buff=0.12)
        return VGroup(ax_x, ax_y, lab_v, lab_w, lab_k)

    def build_nullclines(self):
        vn = VMobject(stroke_color=P.V_NULL, stroke_width=3.5, fill_opacity=0)
        wn = VMobject(stroke_color=P.W_NULL, stroke_width=3.5, fill_opacity=0)

        def upd_v(m):
            win = self.win()
            Vs = win_Vs(win)
            set_runs(m, clip_runs(pp_xy(Vs, P.V_nullcline_w(Vs, self.p, self.I_now()), win),
                                  PP_BOX))

        def upd_w(m):
            win = self.win()
            Vs = win_Vs(win)
            set_runs(m, clip_runs(pp_xy(Vs, P.w_nullcline(Vs, self.p), win), PP_BOX))
        vn.add_updater(upd_v)
        wn.add_updater(upd_w)
        upd_v(vn)
        upd_w(wn)
        return vn, wn

    def build_null_labels(self):
        """Inline nullcline labels, riding on their curves in every view. Each sits beside the
        point where its curve crosses a set height of the plot (NULL_LABEL_SPEC)."""
        vl = label("V-nullcline", 28, P.V_NULL)
        wl = label("w-nullcline", 28, P.W_NULL)
        x0, x1, y0, y1 = PP_BOX

        def place(m, pts, spec):
            frac, side, branch = spec
            ty = y0 + frac * (y1 - y0)
            k_min = int(np.argmin(pts[:, 1]))
            seg = pts[:k_min + 1] if branch == "left" else pts[k_min:]
            ys = seg[:, 1]
            hit = np.where((ys[:-1] - ty) * (ys[1:] - ty) <= 0)[0]
            if len(hit) == 0:
                return False
            i = hit[0]
            u = (ty - ys[i]) / (ys[i + 1] - ys[i]) if ys[i + 1] != ys[i] else 0.0
            c = seg[i] + u * (seg[i + 1] - seg[i])
            m.next_to([c[0], c[1], 0], side, buff=0.16)
            return True

        def upd(g):
            win = self.win()
            a = self.Z.get_value()
            sub, full = NULL_LABEL_SPEC[self.key]
            Vs = win_Vs(win)
            for m, w_of, j in ((vl, lambda V: P.V_nullcline_w(V, self.p, self.I_now()), 0),
                               (wl, lambda V: P.w_nullcline(V, self.p), 1)):
                s0, s1 = sub[j], full[j]
                dip = 1.0
                spec = ((1 - a) * s0[0] + a * s1[0], s0[1] if a < 0.5 else s1[1],
                        s0[2] if a < 0.5 else s1[2])
                ok = place(m, pp_xy(Vs, w_of(Vs), win), spec)
                if not np.allclose(s0[1], s1[1]):
                    dip *= abs(2 * a - 1)
                m.set_opacity(self.null_lab_op.get_value() * self.intro.get_value() * dip
                              if ok else 0)
        g = VGroup(vl, wl)
        g.add_updater(upd)
        upd(g)
        return g

    def build_fps(self):
        """Fixed points, s05 look: stable white with a rim (reads under the state dot), saddle
        and unstable open; grey labels "rest" (node), "focus", "saddle"."""
        dots = VGroup(*[Dot(radius=0.1) for _ in range(3)])
        labs = {s: label(s, 26, P.MUTED) for s in ("rest", "focus", "saddle")}

        def upd(g):
            fps = self.fps_now()
            k = self.intro.get_value()
            shown = {}
            for i, d in enumerate(dots):
                f = fps[i] if i < len(fps) else None
                c = self.scr(f["V"], f["w"]) if f is not None else None
                if f is None or not self.inside(c):
                    d.set_opacity(0)
                    continue
                d.move_to(c)
                if f["kind"].startswith("stable"):
                    d.set_fill(WHITE, k).set_stroke(WHITE, 6, k)
                    shown["rest" if ("node" in f["kind"] or self.key == "c1") else "focus"] = c
                else:
                    d.set_fill(BLACK, k).set_stroke(WHITE, 3, k)
                    if f["kind"] == "saddle":
                        shown["saddle"] = c
                    elif self.key == "c2":            # the class 2 rest, after it goes unstable
                        shown["focus"] = c
            a = self.Z.get_value()
            for s, m in labs.items():
                if s in shown:
                    if s == "saddle":
                        m.next_to(shown[s], UL, buff=0.06)
                    elif self.key == "c2":
                        m.next_to(shown[s], DR if a < 0.5 else UL, buff=0.2)
                    else:
                        m.next_to(shown[s], DR, buff=0.06)
                    m.set_opacity(k)
                else:
                    m.set_opacity(0)
        g = VGroup(dots, *labs.values())
        g.add_updater(upd)
        upd(g)
        g.p2_live = True
        return g

    def build_traj(self):
        """Class-coloured trail that builds up (s05): the last TRAIL_RECENT ms opaque, the rest
        at OLD_TRAIL_OP; yellow state dot on top."""
        old = VMobject(fill_opacity=0)
        new = VMobject(fill_opacity=0)
        dot = Dot(radius=0.09, fill_color=P.STATE_DOT, stroke_color=BLACK, stroke_width=1.5)

        def upd(g):
            op = self.traj_op.get_value()
            t = self.T.get_value()
            tr = self.tr
            n = np.searchsorted(tr["t"], t, side="right")
            Vn, wn = self.state(t)
            tq = np.append(tr["t"][:n], t)
            pts = warped_to_scene(np.append(tr["X"][:n], warp_v(Vn)),
                                  np.append(tr["Y"][:n], warp_w(wn)), self.win())
            cut = int(np.searchsorted(tq, t - TRAIL_RECENT))
            set_runs(old, clip_runs(pts[:cut + 1], PP_BOX) if cut >= 1 else [])
            set_runs(new, clip_runs(pts[max(cut, 0):], PP_BOX))
            col = CLASS_COLOR[self.key]
            old.set_stroke(col, 3, opacity=op * OLD_TRAIL_OP)
            new.set_stroke(col, 3, opacity=op)
            c = np.array([*pts[-1], 0.0])
            dot.move_to(c)
            dot.set_opacity(op if self.inside(c) else 0)
        g = VGroup(old, new, dot)
        g.add_updater(upd)
        upd(g)
        return g

    def build_ghost(self):
        """Soft halo where the node and saddle merged (no label)."""
        Vg, wg = ghost_point()
        halo = VGroup(*[Circle(radius=r).set_fill(P.CLASS1, 0.0).set_stroke(width=0)
                        for r in (0.55, 0.4, 0.26)])

        def upd(g):
            op = self.ghost_op.get_value()
            c = self.scr(Vg, wg)
            for h in g:
                h.move_to(c)
                h.set_fill(P.CLASS1, op * 0.13)
        halo.add_updater(upd)
        upd(halo)
        return halo

    def build_traces(self):
        """Right column, s05 look: V(t) and the injected current build up over the whole class
        run; yellow V pen, grey current pen. While model time is frozen (the lifts), the current
        pen rises to the displayed I."""
        vt = VMobject(stroke_color=P.VOLT, stroke_width=3, fill_opacity=0)
        cur = VMobject(stroke_color=P.MUTED, stroke_width=3, fill_opacity=0)
        vpen = Dot(radius=0.05, fill_color=P.STATE_DOT, stroke_width=0)
        ipen = Dot(radius=0.045, fill_color=P.MUTED, stroke_width=0)

        def upd(g):
            t, op = self.T.get_value(), self.traj_op.get_value()
            key = self.key
            T_ax = p2_t_axis(key)
            d = self.vt_data
            n = np.searchsorted(d["t"], t, side="right")
            pts = box_xy(np.append(d["t"][:n], t), np.append(d["V"][:n], self.state(t)[0]),
                         P2_VT_BOX, 0, T_ax, vt_range(key, self.Z.get_value()))
            set_runs(vt, clip_runs(pts, P2_VT_BOX))
            vt.set_stroke(opacity=op)
            y0, y1 = P2_VT_BOX[2], P2_VT_BOX[3]
            vpen.move_to([pts[-1, 0], np.clip(pts[-1, 1], y0, y1), 0]).set_opacity(op)
            tc, Ic = self.cur_data
            m = tc <= t
            I_run = float(np.interp(t, self.run["t"], self.run["I"]))
            ci = box_xy(np.r_[tc[m], t, t], np.r_[Ic[m], I_run, self.I_now()], P2_CUR_BOX, 0,
                        T_ax, (0.0, 1.1 * IB[key]))
            set_runs(cur, [ci])
            cur.set_stroke(opacity=op)
            ipen.move_to([ci[-1, 0], ci[-1, 1], 0]).set_opacity(op)
        g = VGroup(vt, cur, vpen, ipen)
        g.add_updater(upd)
        upd(g)
        return g

    def build_cur_chrome(self, key):
        """"current" label and the dashed I_bif line on the current strip (0 .. 1.1 I_bif)."""
        x0, x1, y0, y1 = P2_CUR_BOX
        lab = label("current", FS_TICK, P.MUTED).move_to([x0, y1 + 0.24, 0], aligned_edge=LEFT)
        y = box_xy(0, IB[key], P2_CUR_BOX, 0, 1, (0.0, 1.1 * IB[key]))[0, 1]
        ln = VMobject().set_stroke(CLASS_COLOR[key], 2)
        set_runs(ln, dash_runs([[x0, y], [x1, y]], 0.1, 0.08))
        ib = tlabel(R"I_{\mathrm{bif}}", FS_TICK, CLASS_COLOR[key])
        ib.next_to([x1, y, 0], UP, buff=0.06).align_to([x1, 0, 0], RIGHT)
        return VGroup(lab, ln, ib)

    def build_scale_bars(self, key):
        """s05 scale bars under the V(t) box: (static bars, live bars). Class 1 20 mV / 100 ms;
        class 2 50 ms and a 5 mV bar that hands over to 20 mV through its zoom."""
        x0, x1, y0, y1 = P2_VT_BOX
        y = P2_BAR_Y
        ms = 100 if key == "c1" else 50
        L = ms / p2_t_axis(key) * (x1 - x0)
        hbar = Line([x1 - L, y, 0], [x1, y, 0]).set_stroke(P.MUTED, 3)
        ms_lab = label(f"{ms} ms", FS_TICK, P.MUTED).next_to(hbar, DOWN, buff=0.08)
        ms_lab.align_to(hbar, RIGHT)
        static = VGroup(hbar, ms_lab)
        live = VGroup()
        for mv, rng, which in ([(20, P2_VT_FULL, None)] if key == "c1" else
                               [(5, P2_VT_ZOOM, 0), (20, P2_VT_FULL, 1)]):
            vb = Line([x1, y, 0], [x1, y + mv / (rng[1] - rng[0]) * (y1 - y0), 0])
            vb.set_stroke(P.MUTED, 3)
            vl = label(f"{mv} mV", FS_TICK, P.MUTED).next_to(vb, LEFT, buff=0.1)
            vl.align_to(vb, DOWN).shift(UP * 0.12)
            grp = VGroup(vb, vl)
            grp.which = which
            (static if which is None else live).add(grp)

        def upd(g):
            a, k = self.Z.get_value(), self.intro.get_value() * self.bar_op.get_value()
            for grp in g:                      # one bar at a time: out, then in, at mid-zoom
                on = (a < 0.5) == (grp.which == 0)
                grp.set_opacity(k * abs(2 * a - 1) if on else 0.0)
        if len(live):
            live.add_updater(upd)
            upd(live)
        live.p2_live = True
        return static, live

    def build_readouts(self):
        """s05 readouts under the badge, timed by model time: class 1 firing rate; class 2
        ring frequency, then firing rate."""
        o1, o2 = MODEL["ostats_c1"], MODEL["ostats_c2"]
        t1, t2 = len(C1_LEVELS) * HOLD, len(C2_LEVELS) * HOLD
        ring = P.ring_hz(MODEL["stats_c2"][-1]["eig"] / 1000.0)
        specs = [
            ("c1", Rf"\approx {o1['rate']:.0f}\ \text{{spikes/s}}", P.INK,
             t1 + o1["spikes"][1] + 3.0, np.inf),
            ("c2", Rf"\text{{rings at}} \approx {ring:.0f}\ \text{{Hz}}", P.CLASS2,
             2 * HOLD + 3.0, t2 + o2["spikes"][1]),
            ("c2", Rf"\text{{fires at}} \approx {o2['rate']:.0f}\ \text{{spikes/s}}", P.INK,
             t2 + o2["spikes"][1] + 3.0, np.inf),
        ]
        g = VGroup()
        for key, s, col, on, off in specs:
            m = tlabel(s, FS_LAB, col).move_to(READOUT_POS, aligned_edge=RIGHT)
            m.spec = (key, on, off)
            g.add(m)

        def upd(grp):
            t = self.T.get_value()
            k = self.intro.get_value() * self.traj_op.get_value()
            for m in grp:
                key, on, off = m.spec
                up = np.clip((t - on) / 5.0, 0, 1)
                down = 1 - np.clip((t - off) / 3.0, 0, 1)
                m.set_opacity(k * up * down if key == self.key else 0.0)
        g.add_updater(upd)
        upd(g)
        g.p2_live = True
        return g

    def swap_chip(self, new, total=None, start=0.0):
        """Old chip fades out, then the new one fades in (never both at once)."""
        old = self.chip
        self.chip = new
        if total is None:
            spans = (0.0, 0.5), (0.5, 1.0)
        else:
            spans = (start / total, (start + 0.2) / total), ((start + 0.2) / total,
                                                            min((start + 0.4) / total, 1.0))
        return [chip_fade(old, *spans[0], out=True), chip_fade(new, *spans[1], out=False)]

    def swap_caption(self, new, total=None, start=0.0):
        old = self.cap
        self.cap = new
        if old is None:
            return [FadeIn(new)] if total is None else [swap_in(new, total, start)]
        if total is None:
            return [FadeOut(old, rate_func=squish_rate_func(smooth, 0.0, 0.5)),
                    FadeIn(new, rate_func=squish_rate_func(smooth, 0.5, 1.0))]
        return [swap_out(old, total, start), swap_in(new, total, start + 0.3)]

    def run_T(self, t1, video_s, *extra):
        self.play(self.T.animate.set_value(t1).set_anim_args(rate_func=linear), *extra,
                  run_time=video_s)

    def p2_setup(self):
        ## Part 2 setup: phase plane, nullclines at I = 0, rest
        self.axes = self.build_axes()
        self.vnull, self.wnull = self.build_nullclines()
        self.null_labs = self.build_null_labels()
        self.null_labs.p2_live = True
        self.fpg = self.build_fps()
        self.traj = self.build_traj()
        self.ghost = self.build_ghost()
        self.traces = self.build_traces()
        self.cur_chrome = self.build_cur_chrome("c1")
        self.bars, self.bars_live = self.build_scale_bars("c1")
        self.readouts = self.build_readouts()
        self.hdr = header(P2_TAG["c1"], P.CLASS1)
        self.sweep_tab = self.sweep_table()
        self.chip = self.sweep_chip()
        self.cap = None
        self.badge = None
        self.add(self.ghost, self.wnull, self.vnull, self.null_labs, self.traj, self.traces,
                 self.readouts, self.bars_live)
        cap = caption(P2_CAPS["sweep"], fs=FS_P2_CAP)
        self.play(FadeIn(self.axes), FadeIn(self.vnull), FadeIn(self.wnull), FadeIn(self.fpg),
                  FadeIn(self.cur_chrome), FadeIn(self.bars), FadeIn(self.hdr), FadeIn(self.chip),
                  self.intro.animate.set_value(1.0), *self.swap_caption(cap), run_time=1.0)
        self.add(self.traj)                # state dot drawn over the fixed points

    def sweep_table(self):
        Ib = IB["c1"]
        s = np.linspace(0, 0.9, 181)
        fps = [stable_fp(P.CONTROL, x * Ib) for x in s]
        assert all(f["kind"] == "stable node" for f in fps)
        lam = np.array([sorted(f["eig"].real * 1000, key=abs) for f in fps])
        return s * Ib, lam

    def sweep_chip(self):
        Is, lam = self.sweep_tab
        l1 = tlabel(R"\lambda =", FS_LAB)
        n1 = DecimalNumber(lam[0, 0], num_decimal_places=0, font_size=FS_LAB, group_with_commas=False)
        cm = tlabel(",", FS_LAB)
        n2 = DecimalNumber(lam[0, 1], num_decimal_places=0, font_size=FS_LAB, group_with_commas=False)
        u1 = tlabel(R"\mathrm{s^{-1}}", FS_LAB)
        l2 = tlabel(R"I_{\mathrm{stim}} =", 28)
        n3 = DecimalNumber(0.0, num_decimal_places=1, font_size=28)
        u2 = tlabel(R"\mu\mathrm{A/cm^2}", 28)
        row1 = VGroup(l1, n1, cm, n2, u1)
        row2 = VGroup(l2, n3, u2)
        c = chip([row1.copy().arrange(RIGHT, buff=0.12), row2.copy().arrange(RIGHT, buff=0.12)],
                 CHIP_CORNER)
        box = c[0]
        box.stretch_to_fit_width(box.get_width() + 0.3).align_to(CHIP_CORNER, LEFT)
        base1 = c[1][0][0].get_bottom()[1]
        base2 = c[1][1][0].get_bottom()[1]
        x_left = box.get_left()[0] + 0.2

        def upd(_):
            I = self.I_now()
            a = float(np.interp(I, Is, lam[:, 0]))
            b = float(np.interp(I, Is, lam[:, 1]))
            n1.set_value(float(round(a)))     # DecimalNumber truncates at 0 decimals
            n2.set_value(float(round(b)))
            n3.set_value(I)
            l1.move_to([x_left, 0, 0], aligned_edge=LEFT).set_y(base1, DOWN)
            n1.next_to(l1, RIGHT, buff=0.15).set_y(base1, DOWN)
            cm.next_to(n1, RIGHT, buff=0.05).set_y(base1 - 0.06, DOWN)
            n2.next_to(cm, RIGHT, buff=0.15).set_y(base1, DOWN)
            u1.next_to(n2, RIGHT, buff=0.12).set_y(base1, DOWN)
            l2.move_to([x_left, 0, 0], aligned_edge=LEFT).set_y(base2, DOWN)
            n3.next_to(l2, RIGHT, buff=0.15).set_y(base2, DOWN)
            u2.next_to(n3, RIGHT, buff=0.12).set_y(base2 - 0.07, DOWN)
        g = VGroup(box, row1, row2)
        g.add_updater(upd)
        upd(g)
        return g

    def lift_chip_c1(self):
        """Live chip for the class 1 lift. Only the slowest eigenvalue's real value is written:
        between 0.93 and 0.999 I_bif the stable point is a heavily damped focus, and writing its
        imaginary part would promise a ring that never shows."""
        l1 = tlabel(R"\text{slowest}\ \lambda =", FS_LAB)
        n1 = DecimalNumber(-1000, num_decimal_places=0, font_size=FS_LAB, group_with_commas=False)
        u1 = tlabel(R"\mathrm{s^{-1}}", FS_LAB)
        row2 = label("node + saddle merge → λ → 0", 28)
        c = chip([VGroup(l1, n1, u1).arrange(RIGHT, buff=0.15), row2], CHIP_CORNER)
        base = l1.get_bottom()[1]

        def upd(_):
            st = [f for f in self.fps_now() if f["kind"].startswith("stable")]
            v = round(float(st[0]["eig"].real.max() * 1000)) + 0.0 if st else 0.0
            n1.set_value(v)
            n1.set_fill(P.HIGHLIGHT if v >= 0 else P.INK)
            n1.next_to(l1, RIGHT, buff=0.15).set_y(base, DOWN)
            u1.next_to(n1, RIGHT, buff=0.12).set_y(base, DOWN)
            live_chip_opacity(c, [l1, n1, u1, row2])
        return make_live(c, upd)

    def lift_chip_c2(self):
        """Live chip for the class 2 lift: lambda = Re +- Im i, Re turning red above 0, and a
        second line that flips from damped to unstable at the crossing."""
        l1 = tlabel(R"\lambda =", FS_LAB)
        nr = DecimalNumber(-100, num_decimal_places=0, font_size=FS_LAB, include_sign=True,
                           group_with_commas=False)
        pm = tlabel(R"\pm", FS_LAB)
        ni = DecimalNumber(600, num_decimal_places=0, font_size=FS_LAB, group_with_commas=False)
        u1 = tlabel(R"i\ \mathrm{s^{-1}}", FS_LAB)
        pos = label("Re λ > 0: unstable — the spiral opens", 28, P.HIGHLIGHT)
        neg = label("Re λ < 0: the ring dies out", 28)
        zero = label("Re λ = 0: on the edge", 28, P.HIGHLIGHT)
        c = chip([VGroup(l1, nr, pm, ni, u1).arrange(RIGHT, buff=0.12), pos], CHIP_CORNER)
        for m in (neg, zero):
            m.move_to(pos, aligned_edge=LEFT)
            c.add(m)
        base = l1.get_bottom()[1]

        def upd(_):
            ev = self.fps_now()[0]["eig"] * 1000
            v = ev[np.argmax(ev.imag)]
            re = round(float(v.real)) + 0.0
            nr.set_value(re)
            nr.set_fill(P.HIGHLIGHT if re > 0 else P.INK)
            ni.set_value(round(abs(float(v.imag))))
            nr.next_to(l1, RIGHT, buff=0.15).set_y(base, DOWN)
            pm.next_to(nr, RIGHT, buff=0.12).set_y(base + 0.02, DOWN)
            ni.next_to(pm, RIGHT, buff=0.12).set_y(base, DOWN)
            u1.next_to(ni, RIGHT, buff=0.06).set_y(base, DOWN)
            live_chip_opacity(c, [l1, nr, pm, ni, u1])
            for m, on in ((neg, re < 0), (zero, re == 0), (pos, re > 0)):
                m.set_opacity(c.vis if on else 0)
        return make_live(c, upd)

    def p2_sweep(self):
        ## Step 1: I sweeps 0 -> 0.9 I_bif, fixed point slides (no trajectory)
        Ib = IB["c1"]
        self.play(self.Iov.animate.set_value(0.9 * Ib), run_time=4.0, rate_func=smooth)
        self.wait(0.5)
        self.play(self.Iov.animate.set_value(0.0), run_time=1.0, rate_func=smooth)

    def p2_class1_staircase(self):
        ## Step 2: class 1 staircase at x1/40
        self.chip.clear_updaters()
        self.badge = speed_badge("1/40")
        self.play(FadeIn(self.badge), self.traj_op.animate.set_value(1.0), FadeOut(self.cap),
                  *self.swap_chip(lam_chip(stable_fp(P.CONTROL, 0.0)["eig"] * 1000)),
                  run_time=0.8)
        self.cap = None
        self.use_ov = False
        for k, st in enumerate(MODEL["stats_c1"]):
            self.run_T((k + 1) * HOLD, HOLD * STAIR_SLOW / 1000.0,
                       *self.swap_chip(lam_chip(st["eig"]), 2.0, 0.0))

    def p2_class1_lift(self):
        ## Class 1: freeze, lift the V-nullcline 0.9 -> 1.0005 I_bif (saddle-node)
        Ib = IB["c1"]
        self.Iov.set_value(0.9 * Ib)
        self.use_ov = True
        a = ValueTracker(0.0)
        self.Iov.add_updater(lambda m: m.set_value(lift_I(a.get_value())))
        self.play(a.animate.set_value(0.9).set_anim_args(rate_func=linear),
                  *self.swap_chip(self.lift_chip_c1(), 0.9, 0.0), run_time=0.9)
        self.Iov.clear_updaters()
        # past the merge (1.0005 I_bif, a hair above): node and saddle are gone
        self.Iov.set_value(C1_ONSET * Ib)
        c = self.scr(*ghost_point())
        half = half_dot(c)
        self.add(half)
        self.wait(2 / FPS)
        self.remove(half)
        self.play(flash_ring(c), run_time=0.7)
        self.wait(0.3)

    def p2_class1_onset(self):
        ## Class 1: crawl past the ghost at x1/10, zoom out at the first spike
        t0 = len(C1_LEVELS) * HOLD
        new_badge = speed_badge("1/10")
        self.play(FadeTransform(self.badge, new_badge), self.ghost_op.animate.set_value(1.0),
                  *self.swap_chip(text_chip("no fixed point — saddle-node passed")),
                  run_time=0.6)
        self.badge = new_badge
        self.use_ov = False
        t_exit = t0 + self.exit_time()
        self.run_T(t_exit, (t_exit - t0) * C1_SLOW / 1000.0)
        self.play(self.Z.animate.set_value(1.0), run_time=1.0, rate_func=smooth)
        t_end = t0 + C1_ONSET_MS
        self.run_T(t_end, (t_end - t_exit) * C1_SLOW / 1000.0)
        self.cap = caption(P2_CAPS["c1"], fs=FS_P2_CAP)
        self.play(Write(self.cap), run_time=1.0)
        self.wait(2.0)

    def exit_time(self):
        """Model time after the onset step when the first spike leaves the subthreshold view."""
        on = MODEL[f"onset_{self.key}"]
        xy = pp_xy(on["V"], on["w"], window_at(0.0, self.full))
        x0, x1, y0, y1 = PP_BOX
        out = (xy[:, 0] > x1) | (xy[:, 1] > y1)
        return float(on["t"][np.argmax(out)])

    def p2_to_class2(self):
        ## Class 2: fade class 1, nullclines for SHUNT, zoom back, restart at rest
        self.play(self.traj_op.animate.set_value(0.0), self.ghost_op.animate.set_value(0.0),
                  FadeOut(self.cap), run_time=0.8)
        self.cap = None
        self.set_class("c2")
        self.full = MODEL["zoom_c1"]       # keep class 1's zoomed-out window while zooming in
        self.T.set_value(0.0)
        self.Iov.set_value(0.0)
        self.use_ov = True
        new_hdr = header(P2_TAG["c2"], P.CLASS2)
        new_badge = speed_badge("1/40")
        new_chrome = self.build_cur_chrome("c2")
        new_bars, new_live = self.build_scale_bars("c2")
        self.remove(self.bars_live)
        self.bar_op.set_value(0.0)
        self.add(new_live)
        first, second = squish_rate_func(smooth, 0.0, 0.5), squish_rate_func(smooth, 0.5, 1.0)
        self.play(self.Z.animate.set_value(0.0).set_anim_args(rate_func=smooth),
                  *[FadeOut(m, rate_func=first) for m in (self.hdr, self.badge, self.cur_chrome,
                                                          self.bars)],
                  *[FadeIn(m, rate_func=second) for m in (new_hdr, new_badge, new_chrome,
                                                          new_bars)],
                  self.bar_op.animate.set_value(1.0).set_anim_args(rate_func=second),
                  *self.swap_chip(lam_chip(stable_fp(P.SHUNT, 0.0)["eig"] * 1000)),
                  run_time=1.2)
        self.full = MODEL["zoom_c2"]
        self.hdr, self.badge, self.cur_chrome = new_hdr, new_badge, new_chrome
        self.bars, self.bars_live = new_bars, new_live
        self.use_ov = False
        self.play(self.traj_op.animate.set_value(1.0), run_time=0.4)

    def p2_class2_staircase(self):
        ## Step 3: class 2 staircase at x1/40 (rings at 0.97 and 0.99)
        for k, st in enumerate(MODEL["stats_c2"]):
            self.run_T((k + 1) * HOLD, HOLD * STAIR_SLOW / 1000.0,
                       *self.swap_chip(lam_chip(st["eig"]), 2.0, 0.0))

    def p2_class2_lift(self):
        ## Class 2: freeze, lift 0.99 -> 1.002 I_bif with a live chip; Re lambda crosses 0
        Ib = IB["c2"]
        self.Iov.set_value(C2_LEVELS[-1] * Ib)
        self.use_ov = True
        b = ValueTracker(0.0)
        self.Iov.add_updater(lambda m: m.set_value(Ib * lift2_I(b.get_value())))
        new_badge = speed_badge("1/25")
        self.play(b.animate.set_value(1.0).set_anim_args(rate_func=linear),
                  FadeTransform(self.badge, new_badge),
                  *self.swap_chip(self.lift_chip_c2(), 1.4, 0.0), run_time=1.4)
        self.badge = new_badge
        self.Iov.clear_updaters()
        self.Iov.set_value(Ib)
        f = self.fps_now()[0]
        self.play(flash_ring(self.scr(f["V"], f["w"])), run_time=0.7)
        self.wait(0.3)
        self.play(self.Iov.animate.set_value(C2_ONSET * Ib).set_anim_args(rate_func=smooth),
                  run_time=0.4)
        self.wait(0.3)

    def p2_class2_onset(self):
        ## Class 2: step to 1.002 I_bif, spiral opens (x1/25), zoom out, fast firing
        t0 = len(C2_LEVELS) * HOLD
        self.T.set_value(t0 + DT)          # onto the onset step (0.05 ms of model time)
        self.use_ov = False
        t_exit = t0 + self.exit_time()
        self.run_T(t_exit, (t_exit - t0 - DT) * C2_SLOW / 1000.0)
        self.play(self.Z.animate.set_value(1.0), run_time=1.0, rate_func=smooth)
        t_end = t0 + C2_ONSET_MS
        self.run_T(t_end, (t_end - t_exit) * C2_SLOW / 1000.0)
        self.cap = caption(P2_CAPS["c2"], fs=FS_P2_CAP)
        self.play(Write(self.cap), run_time=1.0)
        self.wait(2.5)
        keep = [m for m in self.mobjects if not isinstance(m, ValueTracker)
                and not getattr(m, "p2_live", False) and m is not self.chip]
        self.play(*[FadeOut(m) for m in keep], chip_fade(self.chip, 0.0, 1.0, out=True),
                  self.intro.animate.set_value(0.0), self.traj_op.animate.set_value(0.0),
                  run_time=1.0)

# ============================================================ Part 3 layout
P3_CX = {"c1": -3.35, "c2": 3.6}
P3_PP_Y, P3_VT_Y, P3_IT_Y = (1.05, 3.05), (-1.35, 0.2), (-2.4, -1.75)
P3_DX = (-2.6, 2.85)                      # plot x extent relative to the column centre
P3_T = 60.0                               # ms, fixed trial time axis
P3_VT_RANGE = {"c1": (-50.0, -30.0), "c2": (-37.0, -25.5)}
P3_VT_TICKS = {"c1": [-45, -35], "c2": [-35, -30]}
P3_HOLD = 1.5


def check_mark(color, size=0.42):
    m = VMobject().set_points_as_corners([[-0.5, 0.05, 0], [-0.15, -0.38, 0], [0.55, 0.5, 0]])
    return m.set_stroke(color, 8).scale(size / 1.05)


def cross_mark(color, size=0.36):
    h = size / 2
    return VGroup(Line([-h, -h, 0], [h, h, 0]), Line([-h, h, 0], [h, -h, 0])).set_stroke(color, 7)


def stamp(fired, key, size=None):
    return check_mark(CLASS_COLOR[key]) if fired else cross_mark(P.MUTED)


class P3Column:
    """One column of Part 3: small phase plane, V(t), I_stim(t) for one class."""

    def __init__(self, scene, key):
        self.sc, self.key, self.p = scene, key, PARAMS[key]
        cx = P3_CX[key]
        self.xr = (cx + P3_DX[0], cx + P3_DX[1])
        self.pp = (*self.xr, *P3_PP_Y)
        self.vt = (*self.xr, *P3_VT_Y)
        self.it = (*self.xr, *P3_IT_Y)
        self.I0 = I0_P3[key]
        self.amp = PAIR_FRAC * A1[key]
        self.run = None
        self.col = CLASS_COLOR[key]

    def pp_xy(self, V, w):
        return pp_xy_box(V, w, SUB_WIN, self.pp)

    def static(self):
        g = VGroup()
        x0, x1, y0, y1 = self.pp
        ax = VGroup(Line([x0 - AX_OFF, y0 - AX_OFF, 0], [x1 + 0.12, y0 - AX_OFF, 0]),
                    Line([x0 - AX_OFF, y0 - AX_OFF, 0], [x0 - AX_OFF, y1 + 0.12, 0]))
        ax.set_stroke(P.MUTED, 2)
        g.add(ax)
        for v in (-70, -50, -30):
            x = self.pp_xy(v, 0)[0, 0]
            g.add(Line([x, y0 - AX_OFF - 0.06, 0], [x, y0 - AX_OFF + 0.06, 0]).set_stroke(P.MUTED, 2))
            if v != -30:
                g.add(label(f"{v}".replace("-", "−"), FS_TICK, P.MUTED)
                      .move_to([x, y0 - AX_OFF - 0.25, 0]))
        g.add(label("V (mV)", FS_TICK, P.MUTED).move_to([x1, y0 - AX_OFF - 0.25, 0], aligned_edge=RIGHT))
        for w in (0.0, 0.015):
            y = self.pp_xy(-70, w)[0, 1]
            g.add(Line([x0 - AX_OFF - 0.06, y, 0], [x0 - AX_OFF + 0.06, y, 0]).set_stroke(P.MUTED, 2))
            g.add(label(f"{w:g}", FS_TICK, P.MUTED).next_to([x0 - AX_OFF - 0.06, y, 0], LEFT, 0.08))
        g.add(label("w", FS_TICK, P.MUTED).next_to([x0 - AX_OFF, y1 + 0.12, 0], RIGHT, 0.1))
        # nullclines at I0
        Vs = np.linspace(SUB_WIN[0], SUB_WIN[1], 600)
        for col, w in ((P.V_NULL, P.V_nullcline_w(Vs, self.p, self.I0)), (P.W_NULL, P.w_nullcline(Vs, self.p))):
            m = VMobject(fill_opacity=0).set_stroke(col, 3)
            set_runs(m, clip_runs(self.pp_xy(Vs, w), self.pp))
            g.add(m)
        fp = stable_fp(self.p, self.I0)
        g.add(Dot(radius=0.08, fill_color=self.col, stroke_color=BLACK, stroke_width=2)
              .move_to([*self.pp_xy(fp["V"], fp["w"])[0], 0]))
        # V(t) and I(t) panels
        for box in (self.vt, self.it):
            bx0, bx1, by0, by1 = box
            g.add(VGroup(Line([bx0, by0, 0], [bx1, by0, 0]), Line([bx0, by0, 0], [bx0, by1, 0]))
                  .set_stroke(P.MUTED, 2))
        vr = P3_VT_RANGE[self.key]
        for i, v in enumerate(P3_VT_TICKS[self.key]):
            y = box_xy(0, v, self.vt, 0, 1, vr)[0, 1]
            g.add(Line([self.vt[0] - 0.06, y, 0], [self.vt[0], y, 0]).set_stroke(P.MUTED, 2))
            tl = label(f"{v}".replace("-", "−"), FS_TICK, P.MUTED)
            g.add(tl.next_to([self.vt[0] - 0.06, y, 0], LEFT, 0.08))
        g.add(label("mV", FS_TICK, P.MUTED).next_to([self.vt[0] - 0.14, self.vt[3], 0], LEFT, 0.0)
              .shift(0.05 * DOWN))
        ir = self.i_range()
        for v, s in ((self.I0, R"I_0"), (self.I0 + self.amp, R"I_0 + 0.75\,A_1")):
            y = box_xy(0, v, self.it, 0, 1, ir)[0, 1]
            g.add(Line([self.it[0] - 0.06, y, 0], [self.it[0], y, 0]).set_stroke(P.MUTED, 2))
            lab = tlabel(s, FS_TICK, P.MUTED)
            if v > self.I0:
                lab.move_to([self.it[1], y + 0.02, 0], aligned_edge=RIGHT + DOWN)
            else:
                lab.next_to([self.it[0] - 0.06, y, 0], LEFT, 0.08)
            g.add(lab)
        for tv in (0, 20, 40, 60):
            x = box_xy(tv, 0, self.it, 0, P3_T, (0, 1))[0, 0]
            g.add(Line([x, self.it[2], 0], [x, self.it[2] - 0.07, 0]).set_stroke(P.MUTED, 2))
            g.add(label(f"{tv}", FS_TICK, P.MUTED).move_to([x, self.it[2] - 0.24, 0]))
        g.add(label("time (ms)", FS_TICK, P.MUTED).move_to([self.it[1], self.it[2] - 0.24, 0])
              .shift(0.9 * LEFT))
        return g

    def i_range(self):
        return (self.I0 - 0.12 * self.amp, self.I0 + 1.25 * self.amp)

    def I_of(self, t, d):
        t = np.asarray(t, float)
        on = ((t >= PULSE_T0) & (t < PULSE_T0 + PULSE_MS)) | ((t >= PULSE_T0 + d) & (t < PULSE_T0 + d + PULSE_MS))
        return self.I0 + self.amp * on

    def dynamic(self):
        """Tail + dot in the plane, V(t), I(t); driven by scene.T3 and self.run."""
        n = 15
        segs = VGroup(*[VMobject(fill_opacity=0) for _ in range(n)])
        dot = Dot(radius=0.08, fill_color=P.STATE_DOT, stroke_color=BLACK, stroke_width=1.5)
        vt = VMobject(fill_opacity=0).set_stroke(P.VOLT, 3.5)
        it = VMobject(fill_opacity=0).set_stroke(GREY_A, 3)
        fp = stable_fp(self.p, self.I0)

        def upd(_):
            t = self.sc.T3.get_value()
            op = self.sc.traj_op.get_value()
            r = self.run
            if r is None:
                for m in (*segs, vt, it):
                    set_runs(m, [])
                dot.move_to([*self.pp_xy(fp["V"], fp["w"])[0], 0]).set_opacity(op)
                return
            edges = np.linspace(t - TAIL_MS, t, n + 1)
            for k, m in enumerate(segs):
                a, b = max(edges[k], 0.0), edges[k + 1]
                if b <= a:
                    set_runs(m, [])
                    continue
                i0, i1 = np.searchsorted(r["t"], [a, b])
                ts = np.r_[a, r["t"][i0:i1], b]
                pts = self.pp_xy(np.interp(ts, r["t"], r["V"]), np.interp(ts, r["t"], r["w"]))
                set_runs(m, clip_runs(pts, self.pp))
                m.set_stroke(P.STATE_DOT, 3, opacity=op * (0.08 + 0.92 * (k + 1) / n))
            Vn, wn = np.interp(t, r["t"], r["V"]), np.interp(t, r["t"], r["w"])
            c = self.pp_xy(Vn, wn)[0]
            x0, x1, y0, y1 = self.pp
            dot.move_to([*c, 0]).set_opacity(op if (x0 <= c[0] <= x1 and y0 <= c[1] <= y1) else 0)
            i1 = np.searchsorted(r["t"], t)
            ts = np.r_[r["t"][:i1], t]
            Vs = np.interp(ts, r["t"], r["V"])
            set_runs(vt, clip_runs(box_xy(ts, Vs, self.vt, 0, P3_T, P3_VT_RANGE[self.key]), self.vt))
            vt.set_stroke(opacity=op)
            ti = np.unique(np.r_[np.linspace(0, t, 400), [PULSE_T0, PULSE_T0 + PULSE_MS,
                                                          PULSE_T0 + self.d, PULSE_T0 + self.d + PULSE_MS]])
            ti = ti[ti <= t]
            ti = np.sort(np.r_[ti, ti[(ti > 0)] - 1e-6])
            set_runs(it, [box_xy(ti, self.I_of(ti, self.d), self.it, 0, P3_T, self.i_range())])
            it.set_stroke(opacity=op)
        g = VGroup(segs, dot, vt, it)
        g.add_updater(upd)
        upd(g)
        return g


def pp_xy_box(V, w, win, box):
    x0, x1, y0, y1 = box
    V, w = np.atleast_1d(V), np.atleast_1d(w)
    return np.column_stack([x0 + (V - win[0]) / (win[1] - win[0]) * (x1 - x0),
                            y0 + (w - win[2]) / (win[3] - win[2]) * (y1 - y0)])


class PulsePairIntegratorVsResonator(FrameExact, Scene):
    """Part 3 (78-100 s): pulse pairs, both classes at once; ends on the check/cross grid."""

    def construct(self):
        self.T3 = ValueTracker(0.0)
        self.traj_op = ValueTracker(0.0)
        self.cols = {k: P3Column(self, k) for k in ("c1", "c2")}
        self.cap = None
        self.p3_setup()
        for d in PAIR_DTS:
            self.p3_trial(d)
        self.p3_grid()
        print(f"PART3 duration {self.time:.3f} s")

    def swap_caption(self, new):
        old = self.cap
        self.cap = new
        return [FadeOut(old), FadeIn(new)] if old is not None else [FadeIn(new)]

    def p3_setup(self):
        ## Part 3 setup: two columns at their holding currents
        hdr1 = header(CLASS_NAME["c1"], P.CLASS1)
        hdr2 = header(CLASS_NAME["c2"], P.CLASS2).move_to(
            [P3_CX["c2"] + P3_DX[0] - 0.5, HEADER_POS[1], 0], aligned_edge=LEFT)
        self.dt_x = 0.5 * (hdr1.get_right()[0] + hdr2.get_left()[0])
        self.badge = speed_badge("1/25")
        self.statics = VGroup(*[c.static() for c in self.cols.values()])
        for c in self.cols.values():
            c.d = PAIR_DTS[0]
        self.dyn = VGroup(*[c.dynamic() for c in self.cols.values()])
        self.dt_labels = VGroup()
        self.headers = VGroup(hdr1, hdr2)
        self.add(self.dyn)
        self.play(FadeIn(self.statics), FadeIn(self.headers), FadeIn(self.badge),
                  self.traj_op.animate.set_value(1.0), run_time=1.2)

    def dt_label(self, d):
        m = tlabel(Rf"\Delta t = {d}\ \mathrm{{ms}}", 34, P.INK)
        return m.move_to([self.dt_x, HEADER_POS[1], 0])

    def p3_trial(self, d):
        ## Pulse-pair trial (both classes simultaneously)
        T = d + 40.0
        labs = VGroup(self.dt_label(d))
        for k, c in self.cols.items():
            c.run = MODEL[f"pair_{k}_{d}"]
            c.d = d
        self.T3.set_value(0.0)
        self.traj_op.set_value(1.0)
        self.play(FadeIn(labs), run_time=0.25)
        self.play(self.T3.animate.set_value(T).set_anim_args(rate_func=linear),
                  run_time=T * P3_SLOW / 1000.0)
        stamps = VGroup()
        for k, c in self.cols.items():
            s = stamp(fires(c.run["V"]), k).move_to([c.vt[1] - 0.3, c.vt[3] - 0.25, 0])
            stamps.add(s)
        self.play(*[GrowFromCenter(s) for s in stamps], run_time=0.4)
        extra = []
        if d == 10:
            extra = self.ring_bracket()
            cap = caption("Resonator: fires only when the second kick arrives in rhythm —\n"
                          "about one ring period later.")
            self.play(FadeIn(extra), *self.swap_caption(cap), run_time=0.6)
            self.wait(2.2)
        else:
            self.wait(P3_HOLD)
        if d != PAIR_DTS[-1]:
            self.play(FadeOut(stamps), FadeOut(labs), self.traj_op.animate.set_value(0.0),
                      *([FadeOut(extra)] if d == 10 else []), run_time=0.3)
            for c in self.cols.values():
                c.run = None
        else:
            self.last_trial = VGroup(stamps, labs)

    def ring_bracket(self):
        c = self.cols["c2"]
        sp = MODEL["single_c2"]
        t, V = sp["t"], sp["V"]
        ghost = VMobject(fill_opacity=0).set_stroke(P.MUTED, 2.5)
        pts = box_xy(t[t <= P3_T], V[t <= P3_T], c.vt, 0, P3_T, P3_VT_RANGE["c2"])
        set_runs(ghost, dash_runs(pts, 0.08, 0.06))
        t1, t2 = MODEL["ring_peaks"][:2]
        yb = c.vt[3] + 0.1
        xa = box_xy(t1, 0, c.vt, 0, P3_T, (0, 1))[0, 0]
        xb = box_xy(t2, 0, c.vt, 0, P3_T, (0, 1))[0, 0]
        br = VMobject().set_points_as_corners([[xa, yb - 0.1, 0], [xa, yb, 0], [xb, yb, 0], [xb, yb - 0.1, 0]])
        br.set_stroke(P.CLASS2, 3)
        lab = tlabel(Rf"\text{{ring period}} \approx {MODEL['T_ring']:.1f}\ \mathrm{{ms}}", FS_TICK, P.CLASS2)
        lab.next_to([xb, yb, 0], RIGHT, buff=0.12)
        end = pts[-1]
        note = VGroup(label("1 pulse", FS_TICK, P.MUTED), label("alone", FS_TICK, P.MUTED))
        note.arrange(DOWN, aligned_edge=LEFT, buff=0.06).next_to([*end, 0], RIGHT, buff=0.1)
        return VGroup(ghost, br, lab, note)

    def p3_grid(self):
        ## End frame: check/cross grid over the dimmed columns
        dim = Rectangle(width=14.4, height=6.3).set_fill(BLACK, 0.0).set_stroke(width=0)
        dim.move_to([0, 0.15, 0])
        rows = VGroup()
        head = VGroup(tlabel(R"\Delta t", FS_LAB), label("Class 1", FS_LAB, P.CLASS1),
                      label("Class 2", FS_LAB, P.CLASS2))
        xs = [-2.1, 0.0, 2.1]
        for m, x in zip(head, xs):
            m.move_to([x, 0, 0])
        rows.add(head)
        for d in PAIR_DTS:
            r = VGroup(label(f"{d} ms", FS_LAB).move_to([xs[0], 0, 0]))
            for k, x in zip(("c1", "c2"), xs[1:]):
                r.add(stamp(fires(MODEL[f"pair_{k}_{d}"]["V"]), k).move_to([x, 0, 0]))
            rows.add(r)
        for i, r in enumerate(rows):
            r.set_y(2.05 - 0.72 * i)
        box = RoundedRectangle(width=6.6, height=4.1, corner_radius=0.15)
        box.set_fill(P.CHIP_FILL, 0.96).set_stroke(P.MUTED, 1.5).move_to([0, rows.get_center()[1], 0])
        rule = Line([-3.0, 1.7, 0], [3.0, 1.7, 0]).set_stroke(P.MUTED, 1.5)
        cap = caption("Integrator asks how close together? — resonator asks in rhythm?",
                      t2s={"how close together?": ITALIC, "in rhythm?": ITALIC})
        self.add(dim)
        self.play(dim.animate.set_fill(BLACK, 0.8), FadeIn(box),
                  FadeOut(self.last_trial[1]), FadeOut(self.badge), run_time=0.8)
        self.play(LaggedStartMap(FadeIn, rows, lag_ratio=0.25), FadeIn(rule), *self.swap_caption(cap),
                  run_time=1.2)
        self.wait(3.5)




# ============================================================ acceptance checks
if __name__ == "__main__":
    D = MODEL

    def check(name, text, ok):
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {text}")
        assert ok, name

    def lam_str(ev):
        ev = np.asarray(ev)
        if np.all(np.abs(ev.imag) < 1e-9):
            return ", ".join(f"{v.real:.1f}" for v in ev)
        v = ev[np.argmax(ev.imag)]
        return f"{v.real:.1f} ± {abs(v.imag):.1f}i"

    print("== bifurcation currents")
    check("I_bif CONTROL", f"{IB['c1']:.3f} uA/cm2 (x3 = {3 * IB['c1']:.1f} pA)",
          abs(IB["c1"] - 38.74) <= 0.01)
    check("I_bif SHUNT", f"{IB['c2']:.3f} uA/cm2 (x3 = {3 * IB['c2']:.1f} pA)",
          abs(IB["c2"] - 114.24) <= 0.01)

    print("== chip lambda values (s^-1) vs contract tables (2%)")
    TABLE = {"c1": [(-64.11, [-895, -1972]), (-58.47, [-820, -1484]), (-51.95, [-686, -1036]),
                    (-46.76, [-564, -676])],
             "c2": [(-45.23, [-1111, -973]), (-37.96, [-583 + 459j]), (-33.57, [-196 + 612j]),
                    (-32.32, [-65 + 641j])]}
    for k in ("c1", "c2"):
        for st, (Vt, lt) in zip(D[f"stats_{k}"], TABLE[k]):
            ev = st["eig"]
            if len(lt) == 2:
                got = sorted(ev.real)
                ok = all(abs(g - e) <= 0.02 * abs(e) for g, e in zip(got, sorted(lt)))
            else:
                v = ev[np.argmax(ev.imag)]
                ok = (abs(v.real - lt[0].real) <= 0.02 * abs(lt[0].real)
                      and abs(v.imag - lt[0].imag) <= 0.02 * abs(lt[0].imag))
            extra = ""
            if np.any(np.abs(ev.imag) > 1e-9):
                v = ev[np.argmax(ev.imag)]
                extra = (f"  ring {P.ring_hz(ev / 1000):.1f} Hz, "
                         f"x{P.per_cycle_factor(v / 1000):.3g}/cycle")
            check(f"{k} {st['s']:.2f}xIbif", f"V* {st['V']:.2f} mV, lambda {lam_str(ev)} "
                  f"({st['kind']}){extra}", ok and abs(st["V"] - Vt) < 0.02)
        if k == "c1":
            check("c1 kinds", "all stable node",
                  all(s["kind"] == "stable node" for s in D["stats_c1"]))
    lam_on = stable_or_any_fp(P.SHUNT, C2_ONSET * IB["c2"])["eig"] * 1000
    check("c2 1.002xIbif lambda", f"{lam_str(lam_on)} ({stable_or_any_fp(P.SHUNT, C2_ONSET * IB['c2'])['kind']})",
          abs(lam_on.real.max() - 12.9) < 1.0)

    print("== staircase responses")
    mo = max(s["max_over"] for s in D["stats_c1"])
    check("class 1 max overshoot (max V - V*)", f"{mo:.4f} mV (<= 0.01)", mo <= 0.01)
    for st in D["stats_c2"]:
        print(f"      class 2 {st['s']:.2f}x first overshoot {st['first_over']:.2f} mV")
    for st in D["stats_c2"][2:]:
        check(f"class 2 rings at {st['s']:.2f}x", f"first overshoot {st['first_over']:.2f} mV (>= 1)",
              st["first_over"] >= 1.0)

    print("== onset")
    o1, o2 = D["ostats_c1"], D["ostats_c2"]
    check("class 1 onset rate", f"{o1['rate']:.1f} Hz (< 15); spikes {np.round(o1['spikes'], 1)} ms",
          o1["rate"] < 15)
    check("class 2 onset rate", f"{o2['rate']:.1f} Hz (> 100); first spike {o2['spikes'][0]:.1f} ms",
          o2["rate"] > 100)
    check("class 2 visible spiral", f"{o2['n_pre_peaks']} pre-spike peaks "
          f"{np.round(o2['pre_peaks'], 1)} (>= 3)", o2["n_pre_peaks"] >= 3)
    for k in ("c1", "c2"):
        print(f"      zoom window {k}: V {D[f'zoom_{k}'][0]:.0f} .. {D[f'zoom_{k}'][1]:.0f} mV, "
              f"w {D[f'zoom_{k}'][2]:.2f} .. {D[f'zoom_{k}'][3]:.2f}")

    print("== pulse pairs")
    check("A1 CONTROL", f"{A1['c1']:.2f} uA/cm2 (48.0 +- 2%)", abs(A1["c1"] - 48.0) <= 0.96)
    check("A1 SHUNT", f"{A1['c2']:.2f} uA/cm2 (12.5 +- 2%)", abs(A1["c2"] - 12.5) <= 0.25)
    g1, g2 = pair_grid("c1"), pair_grid("c2")
    print("      CONTROL dt 1..20:", "".join("Y" if f else "." for f in g1))
    print("      SHUNT   dt 1..20:", "".join("Y" if f else "." for f in g2))
    want = {2: (True, True), 5: (False, False), 10: (False, True), 20: (False, True)}
    got = {d: (fires(D[f"pair_c1_{d}"]["V"]), fires(D[f"pair_c2_{d}"]["V"])) for d in PAIR_DTS}
    txt_grid = " · ".join(f"{d} ms {''.join('✓' if f else '✗' for f in got[d])}" for d in PAIR_DTS)
    check("pulse grid", txt_grid, got == want)
    check("ring period", f"{D['T_ring']:.2f} ms (9.7 +- 0.3); peaks {np.round(D['ring_peaks'], 2)}",
          abs(D["T_ring"] - 9.7) <= 0.3)

    print("== Part 1 cartoon")
    pcs = [per_cycle(s) for s in P1_C2_SIGMAS]
    check("per-cycle factors", ", ".join(f"{v:.3f}" for v in pcs),
          all(abs(a - b) <= 0.005 for a, b in zip(pcs, [0.670, 0.368])))
    turns = rot_phase(P1_ROT_T) / (2 * np.pi)
    check("rotation phase closes", f"theta({P1_ROT_T:g} s)/2pi = {turns:.4f} (2x whole)",
          abs(turns - 5 * P1_ROT_T) < 1e-9 and abs(2 * turns - round(2 * turns)) < 1e-9)

    print("== frames per cycle at 60 fps (>= 12)")
    for name, f, slow, fpc in frames_per_cycle():
        check(name, f"{f:.1f} Hz x slow-down {slow:g} -> {fpc:.1f} frames/cycle", fpc >= 12)
    print("all acceptance checks passed")
