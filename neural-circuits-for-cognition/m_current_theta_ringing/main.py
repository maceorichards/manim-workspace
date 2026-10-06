"""Two clocks, and sliding the threshold (~50 s, 1920x1080, 60 fps).

Spec: context_files/contract.md. Runs, settings and verified numbers: context_files/model.md.

Beats as built (video seconds):
  A1  0.0-9.0   shunted theta-model at 0.99 I_bif (tau 5 ms, sigma 0.1). 0.5 s still, 75 ms at
                x1/40 (3 s), caption + faint full path, flash on the V-w plane, hold.
  A2  9.0-21.0  theta-model at 0.99 I_bif (tau 500 ms, sigma 0.004). Out 0.45 s / in 0.55 s
                (windows re-centred, same spans), 2 s at x1/4 (8 s; caption at 13 s), path, hold.
  A3  21.0-24.0 "Same spiral as slide 3" caption, flash on the V-z plane, fade out.
  B1  24.0-30.0 FIG9 control at 0.995 I_bif (sigma 0.001, tau 500 ms): layout fades in.
  B2  30.0-36.0 control -> 33% Na+ inactivation (1 s interpolation).
  B3  36.0-42.0 back to control (0.8 s), then shunt 3.5 (1 s).
  B4  42.0-47.4 back to inactivation (0.8 s), then delete I_M (1 s).
  End 47.4-50.0 four precomputed spectra + legend fade in; 2 s hold.

Beat A windows are centred on each segment's mean with spans shared by A1 and A2 (contract 4).
Beat B spectra are precomputed per condition; transitions interpolate log power for display.
"""

import pathlib
from dataclasses import replace
from functools import lru_cache

import numpy as np
from scipy.signal import butter, filtfilt, hilbert, welch

from common import *

import prescott2008 as P  # <area>/prescott2008.py, on sys.path via common

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "cache"
DT, SEED = 0.02, 0

# ================================================================ run settings (model.md)
# Beat A: 13 s from the 3-D fixed point, first 3 s discarded.
A_RUN_MS, A_BURN_MS = 13000.0, 3000.0
SEGMENTS = {
    # name: (params, hold fraction, sigma, tau_noise ms, displayed window ms, slow-down)
    "A1": (replace(P.THETA_MODEL, g_shunt=4.0), 0.99, 0.1, 5.0, 75.0, 40),
    "A2": (P.THETA_MODEL, 0.99, 0.004, 500.0, 2000.0, 4),
}
# Beat B: 23 s, first 3 s discarded, 0.995 x own I_bif, sigma 0.001, tau 500 ms, seed 0.
B_RUN_MS, B_BURN_MS = 23000.0, 3000.0
B_FRAC, B_SIGMA, B_TAU = 0.995, 0.001, 500.0
VARIANTS = {
    "control": P.FIG9,
    "inact": P.FIG9_INACT,
    "shunt": P.FIG9_SHUNT,
    "noIM": P.FIG9_INACT_NO_IM,
}
# prescott2008.py bug: its palette `SHUNT = PURPLE_C` is overwritten further down by the
# parameter set `SHUNT = MLParams(g_shunt=4.0)`, so `P.SHUNT` is not a colour. Use the palette
# value (style.md: Shunt = PURPLE_C) locally.
SHUNT_COLOR = PURPLE_C
VARIANT_COLOR = {"control": P.CLASS1, "inact": P.CLASS2, "shunt": SHUNT_COLOR, "noIM": P.MUTED}
VARIANT_NAME = {
    "control": "control",
    "inact": "33% Na⁺ inactivation",
    "shunt": "shunt (g_shunt 3.5)",
    "noIM": "33% Na⁺ inactivation, I_M removed",
}

# Verified values (contract / model.md), checked in __main__.
EXPECT_IBIF = {"A1": 183.06, "A2": 53.39, "control": 33.19, "inact": 44.12, "shunt": 83.08,
               "noIM": 42.02}
EXPECT_EIG = {  # s^-1
    "A1": [-21.99 + 721.21j, -10.71],
    "A2": [-6.93 + 63.22j, -740.4],
    "control": [-1112.9, -103.6, -2.8],
    "inact": [-7.8 + 39.3j, -558.7],
    "shunt": [-18.4 + 60.3j, -408.3],
    "noIM": [-709.6, -137.2, -2.5],
}
EXPECT_IM = {"control": 0.10, "inact": 2.11, "shunt": 4.15, "noIM": 0.0}


# ================================================================ model numbers
@lru_cache(maxsize=None)
def ibif(name):
    p = SEGMENTS[name][0] if name in SEGMENTS else VARIANTS[name]
    return P.find_I_bif(p)


@lru_cache(maxsize=None)
def bif(name):
    """(type, V*, I at V*) from the exact rest-branch walk."""
    return P.bifurcation_type(VARIANTS[name])


def params(name):
    return SEGMENTS[name][0] if name in SEGMENTS else VARIANTS[name]


def hold_I(name):
    frac = SEGMENTS[name][1] if name in SEGMENTS else B_FRAC
    return frac * ibif(name)


@lru_cache(maxsize=None)
def fp(name):
    return P.stable_fp_3d(params(name), hold_I(name))


def eig_s(name):
    """3-D eigenvalues at the held fixed point, s^-1, sorted: complex (Im>0) first, then real."""
    ev = fp(name)["eig"] * 1000.0
    ev = [e for e in ev if e.imag >= -1e-9]
    return sorted(ev, key=lambda e: (-abs(e.imag), e.real))


def im_at_vstar(name):
    p = VARIANTS[name]
    V = bif(name)[1]
    return float(p.g_adapt * P.z_inf(V, p) * (V - p.E_K))


# ================================================================ cached runs
def _run(p, I, t_ms, burn_ms, sigma, tau):
    y0 = P.stable_fp_3d(p, I)
    y0 = [y0["V"], y0["w"], y0["z"]]
    t, V, w, z, _ = P.simulate_noisy(p, I, t_ms=t_ms, dt=DT, sigma=sigma, tau_noise=tau, y0=y0,
                                     seed=SEED)
    k = int(round(burn_ms / DT))
    return t[k:] - t[k], V[k:], w[k:], z[k:]


@lru_cache(maxsize=None)
def run_A(name):
    """Kept 10 s of a Beat A run at full resolution: dict t, V, w, z."""
    p, frac, sigma, tau, _, _ = SEGMENTS[name]

    def fn():
        t, V, w, z = _run(p, hold_I(name), A_RUN_MS, A_BURN_MS, sigma, tau)
        return dict(t=t, V=V, w=w, z=z)

    return P.npz_cache(CACHE / f"{name}.npz", fn, sigma=sigma, tau=tau, frac=frac, seed=SEED,
                       dt=DT, run=A_RUN_MS, burn=A_BURN_MS, g_shunt=p.g_shunt)


def spectrum(V):
    """model.md 3: decimate by 5 (fs 10 kHz), subtract mean, Welch nperseg 40000."""
    x = V[::5] - V[::5].mean()
    return welch(x, fs=10000.0, nperseg=40000)


@lru_cache(maxsize=None)
def run_B(name):
    """Beat B run summary + precomputed spectrum: f, Pxx, n_spikes, pp, vmax."""
    p = VARIANTS[name]

    def fn():
        t, V, w, z = _run(p, hold_I(name), B_RUN_MS, B_BURN_MS, B_SIGMA, B_TAU)
        f, Pxx = spectrum(V)
        return dict(f=f, Pxx=Pxx, n_spikes=np.array(len(P.spike_times(t, V))),
                    pp=np.array(pp99(V)), vmax=np.array(V.max()))

    return P.npz_cache(CACHE / f"B_{name}.npz", fn, sigma=B_SIGMA, tau=B_TAU, frac=B_FRAC,
                       seed=SEED, dt=DT, run=B_RUN_MS, burn=B_BURN_MS, g_Na=p.g_Na,
                       g_shunt=p.g_shunt, g_adapt=p.g_adapt)


# ================================================================ measurements
def pp99(V):
    """Peak-to-peak over the central 99% (0.5th to 99.5th percentile)."""
    lo, hi = np.percentile(V, [0.5, 99.5])
    return float(hi - lo)


def peak_freq(f, Pxx, lo, hi):
    m = (f >= lo) & (f <= hi)
    return float(f[m][np.argmax(Pxx[m])])


def peak_ratio(f, Pxx):
    """Max over 2-15 Hz / log-log line through 1-1.5 Hz and 25-40 Hz bins, at the peak."""
    m = (f >= 2) & (f <= 15)
    i = np.argmax(Pxx[m])
    fpk, ppk = f[m][i], Pxx[m][i]
    b = ((f >= 1) & (f <= 1.5)) | ((f >= 25) & (f <= 40))
    c = np.polyfit(np.log10(f[b]), np.log10(Pxx[b]), 1)
    return float(ppk / 10 ** np.polyval(c, np.log10(fpk))), float(fpk)


def lag_deg(x, g, f_ring, fs):
    """Lag of g behind x (deg), model.md 4: Butterworth 0.6-1.5 f_ring, filtfilt, Hilbert."""
    b, a = butter(2, [0.6 * f_ring, 1.5 * f_ring], btype="band", fs=fs)
    hx = hilbert(filtfilt(b, a, x - x.mean()))
    hg = hilbert(filtfilt(b, a, g - g.mean()))
    return float(np.degrees(np.angle(np.mean(hx * np.conj(hg)))))


def ring_hz(name):
    return P.ring_hz(fp(name)["eig"])


@lru_cache(maxsize=None)
def window_A(name):
    """Displayed stretch: first window of length win after burn-in (indices i0, i1)."""
    win = SEGMENTS[name][4]
    i1 = int(round(win / DT)) + 1
    return 0, i1


@lru_cache(maxsize=None)
def spans_A():
    """Shared spans per axis: larger of the two segments' +-3 SD ranges (6 SD), x 1.2."""
    out = {}
    for ax in ("V", "w", "z"):
        out[ax] = 1.2 * max(6 * run_A(n)[ax].std() for n in SEGMENTS)
    return out


@lru_cache(maxsize=None)
def centre_A(name):
    r = run_A(name)
    return {ax: float(r[ax].mean()) for ax in ("V", "w", "z")}


def ranges_A(name):
    c, s = centre_A(name), spans_A()
    return {ax: (c[ax] - s[ax] / 2, c[ax] + s[ax] / 2) for ax in ("V", "w", "z")}


def modulation(x):
    """Real modulation over the window: (max - min) / |mean|."""
    return float((x.max() - x.min()) / abs(x.mean()))


@lru_cache(maxsize=None)
def stats_A(name):
    r = run_A(name)
    p = params(name)
    i0, i1 = window_A(name)
    V, w, z = r["V"], r["w"], r["z"]
    f, Pxx = spectrum(V)
    fr = ring_hz(name)
    return dict(
        spikes=len(P.spike_times(r["t"], V)), pp=pp99(V), sd=float(V.std()),
        peak=peak_freq(f, Pxx, 1.0, 500.0),
        lag_K=lag_deg(V, p.g_Kdr * w, fr, 1000.0 / DT),
        lag_M=lag_deg(V, p.g_adapt * z, fr, 1000.0 / DT),
        mod_V=modulation(V[i0:i1]), mod_K=modulation(w[i0:i1]), mod_M=modulation(z[i0:i1]),
    )


@lru_cache(maxsize=None)
def stats_B(name):
    r = run_B(name)
    ratio, fpk = peak_ratio(r["f"], r["Pxx"])
    m = (r["f"] >= 1) & (r["f"] <= 100)
    return dict(spikes=int(r["n_spikes"]), pp=float(r["pp"]), vmax=float(r["vmax"]),
                ratio=ratio, peak=fpk, pmin=float(r["Pxx"][m].min()),
                pmax=float(r["Pxx"][m].max()))


# ================================================================ layout helpers
AX_COLOR = GREY_B
TICK_FS, LABEL_FS, CAP_FS = 26, 30, 36
CAP_Y = -3.5
TICK_LEN = 0.08


def nice_ticks(lo, hi, n=2, margin=0.06):
    """Largest 1/2/5 step giving >= n ticks strictly inside [lo, hi] (with a margin)."""
    span = hi - lo
    a, b = lo + margin * span, hi - margin * span
    for s in sorted((m * 10.0 ** e for e in range(-6, 3) for m in (1, 2, 5)), reverse=True):
        ticks = np.arange(np.ceil(a / s) * s, b + 1e-12, s)
        if len(ticks) >= n:
            d = max(0, -int(np.floor(np.log10(s) + 1e-9)))
            return [float(v) for v in ticks], d
    raise ValueError


def num_str(v, d):
    s = f"{v:.{d}f}"
    if float(s) == 0:
        s = "0"
    return s.replace("-", "−")


class Panel:
    """Maps a data rectangle onto a screen box; draws L-shaped axes, ticks and labels."""

    def __init__(self, box, xr, yr):
        self.x0, self.x1, self.y0, self.y1 = box
        self.xr, self.yr = xr, yr

    def pts(self, xs, ys):
        xs, ys = np.asarray(xs, float), np.asarray(ys, float)
        X = self.x0 + (xs - self.xr[0]) / (self.xr[1] - self.xr[0]) * (self.x1 - self.x0)
        Y = self.y0 + (ys - self.yr[0]) / (self.yr[1] - self.yr[0]) * (self.y1 - self.y0)
        return np.column_stack([X, Y, np.zeros_like(X)])

    def pt(self, x, y):
        return self.pts([x], [y])[0]

    def inside(self, xs, ys):
        xs, ys = np.asarray(xs), np.asarray(ys)
        return ((xs >= self.xr[0]) & (xs <= self.xr[1]) & (ys >= self.yr[0]) & (ys <= self.yr[1])
                & np.isfinite(ys))

    def axes(self):
        return VGroup(
            Line([self.x0, self.y0, 0], [self.x1, self.y0, 0]),
            Line([self.x0, self.y0, 0], [self.x0, self.y1, 0]),
        ).set_stroke(AX_COLOR, 2)

    def xticks(self, values, labels=None, d=0, fs=TICK_FS):
        g = VGroup()
        for i, v in enumerate(values):
            x = self.pt(v, self.yr[0])[0]
            g.add(Line([x, self.y0, 0], [x, self.y0 - TICK_LEN, 0]).set_stroke(AX_COLOR, 2))
            if labels is not False:
                lab = labels[i] if labels else txt(num_str(v, d), font_size=fs)
                lab.set_color(AX_COLOR).next_to([x, self.y0 - TICK_LEN, 0], DOWN, buff=0.08)
                g.add(lab)
        return g

    def yticks(self, values, labels=None, d=0, fs=TICK_FS):
        g = VGroup()
        for i, v in enumerate(values):
            y = self.pt(self.xr[0], v)[1]
            g.add(Line([self.x0, y, 0], [self.x0 - TICK_LEN, y, 0]).set_stroke(AX_COLOR, 2))
            lab = labels[i] if labels else txt(num_str(v, d), font_size=fs)
            lab.set_color(AX_COLOR).next_to([self.x0 - TICK_LEN, y, 0], LEFT, buff=0.08)
            g.add(lab)
        return g

    def auto_ticks(self):
        (xv, xd), (yv, yd) = nice_ticks(*self.xr, n=3), nice_ticks(*self.yr, n=2)
        return VGroup(self.xticks(xv, d=xd), self.yticks(yv, d=yd))

    def curve_points(self, xs, ys):
        """Points of the longest contiguous run of (xs, ys) inside the data rectangle."""
        m = self.inside(xs, ys)
        if m.sum() < 2:
            return None
        idx = np.flatnonzero(m)
        runs = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)
        r = max(runs, key=len)
        return self.pts(np.asarray(xs)[r], np.asarray(ys)[r])

    def curve(self, xs, ys, color, width=3):
        mob = VMobject()
        p = self.curve_points(xs, ys)
        if p is not None:
            mob.set_points_as_corners(p)
        return mob.set_stroke(color, width)


def chip(mob, pad=(0.18, 0.1)):
    box = RoundedRectangle(width=mob.get_width() + 2 * pad[0], height=mob.get_height() + 2 * pad[1],
                           corner_radius=0.08)
    box.set_fill(P.CHIP_FILL, 1).set_stroke(GREY_B, 1.5).move_to(mob)
    return VGroup(box, mob)


def caption(s):
    t2c = {R"g_{\mathrm{K,dr}}": P.IKDR, R"g_{\mathrm{M}}": P.IM, R"I_{\mathrm{M}}": P.IM}
    c = tex(s, font_size=CAP_FS, t2c={k: v for k, v in t2c.items() if k in s})
    if c.get_width() > 13.6:
        c.set_width(13.6)
    return c.move_to([0, CAP_Y, 0])


def set_path(mob, pts):
    if pts is None or len(pts) < 2:
        p = pts[0] if pts is not None and len(pts) else ORIGIN
        pts = np.array([p, p + 1e-4 * RIGHT])
    mob.set_points_as_corners(pts)
    return mob


def pct_str(x):
    v = 100 * x
    return f"{v:.0f}%" if v >= 10 else (f"{v:.1f}%" if v >= 1 else f"{v:.2f}%")


def lam_tex(name):
    """3-D eigenvalues at the held fixed point for a chip, s^-1, with the ring in Hz."""
    ev = eig_s(name)
    cplx = [e for e in ev if abs(e.imag) > 1e-9]
    real = [e.real for e in ev if abs(e.imag) <= 1e-9]

    def r(x):
        return f"{x:.1f}" if abs(x) < 100 else f"{x:.0f}"

    parts = [f"{r(e.real)} \\pm {abs(e.imag):.1f}i" for e in cplx] + [r(x) for x in real]
    s = R"\lambda = " + R",\ ".join(parts) + R"\ \mathrm{s^{-1}}"
    if cplx:
        f = ring_hz(name)
        s += R"\quad \text{ring } " + (f"{f:.0f}" if f > 20 else f"{f:.1f}") + R"\ \text{Hz}"
    else:
        s += R"\quad \text{(all real: no ring)}"
    return s


# ---------------------------------------------------------------- Beat A layout
AL_X = (-5.7, -1.2)          # phase planes (shared V mapping)
AR_X = (1.0, 5.5)            # time panels
A_TOP_Y = (0.75, 2.6)
A_BOT_Y = (-2.2, -0.35)
TAIL_FRAC = 0.2
A_STEP = {"A1": 2, "A2": 25}  # display subsampling (0.04 ms, 0.5 ms)
A_TIME_TICKS = {"A1": [0, 25, 50, 75], "A2": [0, 500, 1000, 1500, 2000]}
A_LEAD = 0.5                 # still before each run (s)


class SegmentA:
    """Everything that depends on the Beat A segment (A1 or A2)."""

    def __init__(self, name):
        self.name = name
        p, frac, sigma, tau, win, slow = SEGMENTS[name]
        self.p, self.win, self.slow = p, win, slow
        rg = ranges_A(name)
        self.pw = Panel((*AL_X, *A_TOP_Y), rg["V"], rg["w"])
        self.pz = Panel((*AL_X, *A_BOT_Y), rg["V"], rg["z"])
        self.pv = Panel((*AR_X, *A_TOP_Y), (0.0, win), rg["V"])
        self.pg = Panel((*AR_X, *A_BOT_Y), (0.0, win), (-0.06, 1.06))

        r = run_A(name)
        i0, i1 = window_A(name)
        k = A_STEP[name]
        sl = slice(i0, i1, k)
        self.t = r["t"][sl] - r["t"][i0]
        V, w, z = r["V"][sl], r["w"][sl], r["z"][sl]
        gK, gM = p.g_Kdr * w, p.g_adapt * z
        nK = (gK - gK.min()) / (gK.max() - gK.min())
        nM = (gM - gM.min()) / (gM.max() - gM.min())
        self.xy = {
            "w": self.pw.pts(V, w), "z": self.pz.pts(V, z),
            "V": self.pv.pts(self.t, V), "K": self.pg.pts(self.t, nK), "M": self.pg.pts(self.t, nM),
        }
        self.stats = stats_A(name)
        self.T = ValueTracker(0.0)

    # ---- static, segment-dependent parts
    def static(self):
        rg = ranges_A(self.name)
        f = fp(self.name)
        I = hold_I(self.name)
        Vg = np.linspace(*rg["V"], 400)
        g = VGroup()
        g.add(self.pw.auto_ticks(), self.pz.auto_ticks())
        vt, vd = nice_ticks(*rg["V"], n=3)
        g.add(self.pv.yticks(vt, d=vd))
        tt = A_TIME_TICKS[self.name]
        g.add(self.pv.xticks(tt, labels=False), self.pg.xticks(tt))
        g.add(self.pg.yticks([0, 1]))
        # nullclines (V-w with z frozen at its fixed-point value; V-z with w slaved to w_inf)
        g.add(self.pw.curve(Vg, P.V_nullcline_w(Vg, self.p, I, z=f["z"]), P.V_NULL),
              self.pw.curve(Vg, P.w_nullcline(Vg, self.p), P.W_NULL),
              self.pz.curve(Vg, P.z_Vnull(Vg, self.p, I), P.V_NULL),
              self.pz.curve(Vg, P.z_nullcline(Vg, self.p), P.W_NULL))
        for pan, y in ((self.pw, f["w"]), (self.pz, f["z"])):
            g.add(Dot(pan.pt(f["V"], y), radius=0.06, fill_color=P.V_NULL))
        # lambda chip (3-D), speed badge
        lam = chip(tex(lam_tex(self.name), font_size=30))
        lam.move_to([0, 3.5, 0]).align_to([AL_X[0] - 1.1, 0, 0], LEFT)
        badge = chip(tex(R"\times 1/" + str(self.slow), font_size=36))
        badge.move_to([0, 3.5, 0]).align_to([6.9, 0, 0], RIGHT)
        # conductance legend with real-amplitude tags
        s = self.stats
        leg = VGroup(
            tex(R"g_{\mathrm{K,dr}}", font_size=LABEL_FS).set_color(P.IKDR),
            txt("varies " + pct_str(s["mod_K"]), font_size=TICK_FS).set_color(P.MUTED),
            tex(R"g_{\mathrm{M}}", font_size=LABEL_FS).set_color(P.IM),
            txt("varies " + pct_str(s["mod_M"]), font_size=TICK_FS).set_color(P.MUTED),
        )
        leg[1].next_to(leg[0], RIGHT, buff=0.15)
        leg[2].next_to(leg[1], RIGHT, buff=0.5)
        leg[3].next_to(leg[2], RIGHT, buff=0.15)
        for m in (leg[1], leg[3]):
            m.align_to(leg[0], DOWN)
        leg.move_to([0, A_BOT_Y[1] + 0.33, 0]).align_to([AR_X[0], 0, 0], LEFT)
        g.add(lam, badge, leg)
        return g

    # ---- moving parts
    def cursor(self):
        T = self.T.get_value()
        i = int(np.searchsorted(self.t, T, side="right"))
        return max(i, 1)

    def interp(self, key, T):
        a = self.xy[key]
        return np.array([np.interp(T, self.t, a[:, j]) for j in range(3)])

    def dynamic(self):
        g = VGroup()
        ntail = int(round(TAIL_FRAC * self.win / (self.t[1] - self.t[0])))
        for key, pan in (("w", self.pw), ("z", self.pz)):
            tail = VMobject()

            def upd_tail(m, key=key):
                i = self.cursor()
                T = self.T.get_value()
                pts = np.vstack([self.xy[key][max(0, i - ntail):i], self.interp(key, T)])
                set_path(m, pts)
                m.set_stroke(P.STATE_DOT, width=[0.5, 4.0], opacity=[0.0, 1.0])

            tail.add_updater(upd_tail)
            dot = Dot(radius=0.08, fill_color=P.STATE_DOT)
            dot.add_updater(lambda m, key=key: m.move_to(self.interp(key, self.T.get_value())))
            g.add(tail, dot)
        for key, color, width in (("K", P.IKDR, 3.5), ("M", P.IM, 3.5), ("V", P.VOLT, 4)):
            tr = VMobject()

            def upd_trace(m, key=key, color=color, width=width):
                i = self.cursor()
                pts = np.vstack([self.xy[key][:i], self.interp(key, self.T.get_value())])
                set_path(m, pts)
                m.set_stroke(color, width)

            tr.add_updater(upd_trace)
            g.add(tr)
        g.update()
        return g

    def full_path(self):
        return VGroup(*(VMobject().set_points_as_corners(self.xy[k]).set_stroke(P.STATE_DOT, 2, 0.35)
                        for k in ("w", "z")))

    def run(self, scene, extra=(), t0=None, t1=None):
        """Advance model time t0 -> t1 (ms) at the segment's slow-down."""
        t0 = self.T.get_value() if t0 is None else t0
        t1 = self.win if t1 is None else t1
        scene.play(self.T.animate.set_value(t1), *extra, run_time=(t1 - t0) / 1000 * self.slow,
                   rate_func=linear)


def emphasize(path):
    """Brighten a faint full path and let it settle back (replaces a FlashAround on the plot
    box, whose yellow sweep along the box edge read as a stray trajectory)."""
    return path.animate(rate_func=there_and_back).set_stroke(width=3.5, opacity=0.95)


def beat_a_frame():
    """Segment-independent Beat A parts: axes, titles, axis labels."""
    pw = Panel((*AL_X, *A_TOP_Y), (0, 1), (0, 1))
    pz = Panel((*AL_X, *A_BOT_Y), (0, 1), (0, 1))
    pv = Panel((*AR_X, *A_TOP_Y), (0, 1), (0, 1))
    pg = Panel((*AR_X, *A_BOT_Y), (0, 1), (0, 1))
    g = VGroup(pw.axes(), pz.axes(), pv.axes(), pg.axes())
    t_w = tex(R"V\text{\textendash}w\text{ plane (fast recovery, }I_{\mathrm{K,dr}}\text{)}",
              font_size=LABEL_FS, t2c={R"I_{\mathrm{K,dr}}": P.IKDR})
    t_z = tex(R"V\text{\textendash}z\text{ plane (slow recovery, }I_{\mathrm{M}}\text{)}",
              font_size=LABEL_FS, t2c={R"I_{\mathrm{M}}": P.IM})
    t_v = tex(R"V(t)", font_size=LABEL_FS)
    for m, y in ((t_w, A_TOP_Y[1]), (t_z, A_BOT_Y[1]), (t_v, A_TOP_Y[1])):
        m.move_to([0, y + 0.3, 0])
    t_w.align_to([AL_X[0], 0, 0], LEFT)
    t_z.align_to([AL_X[0], 0, 0], LEFT)
    t_v.align_to([AR_X[0], 0, 0], LEFT)
    g.add(t_w, t_z, t_v)
    for y0 in (A_TOP_Y[0], A_BOT_Y[0]):
        lab = txt("V (mV)", font_size=LABEL_FS)
        lab.next_to([AL_X[1], y0, 0], RIGHT, buff=0.12).shift(0.12 * DOWN)
        g.add(lab)
    for y0 in (A_TOP_Y[0], A_BOT_Y[0]):
        lab = txt("t (ms)", font_size=LABEL_FS)
        lab.next_to([AR_X[1], y0, 0], RIGHT, buff=0.4).shift(0.12 * DOWN)
        g.add(lab)
    for sym, color, (y0, y1) in (("w", P.IKDR, A_TOP_Y), ("z", P.IM, A_BOT_Y)):
        g.add(tex(sym, font_size=36).set_color(color).move_to([AL_X[0] - 1.05, (y0 + y1) / 2, 0]))
    g.add(txt("mV", font_size=TICK_FS).set_color(AX_COLOR)
          .move_to([AR_X[0] - 0.45, A_TOP_Y[1] + 0.3, 0]))
    norm = txt("normalized", font_size=TICK_FS).set_color(AX_COLOR).rotate(PI / 2)
    norm.move_to([AR_X[0] - 0.55, sum(A_BOT_Y) / 2, 0])
    g.add(norm)
    return g


# ---------------------------------------------------------------- Beat B layout
ZP_BOX = (-5.6, -1.6, -0.3, 2.6)
VZ_BOX = (1.0, 5.9, 0.8, 2.75)
SP_BOX = (1.0, 5.9, -2.45, 0.0)
VZ_RANGE = ((-46.0, -33.0), (-0.002, 0.04))
SP_X, SP_Y = (0.0, 2.0), (-9.0, -2.0)
METER_X, METER_Y, METER_MAX = (-5.6, -1.6), -1.95, 5.0
B_ORDER = ("control", "inact", "shunt", "noIM")
FP_LABEL = {"control": "saddle-node", "inact": "focus", "shunt": "focus"}


@lru_cache(maxsize=None)
def spec_log(name):
    r = run_B(name)
    m = (r["f"] >= 1.0) & (r["f"] <= 100.0)
    return np.log10(r["f"][m]), np.log10(r["Pxx"][m])


def vnull_B(name, Vg):
    p = VARIANTS[name]
    return P.z_Vnull(Vg, p, hold_I(name)) if p.g_adapt > 0 else None


class MCurrentThetaRinging(Scene):
    def setup(self):
        super().setup()
        # manimgl 1.7.2 passes `--fps 60` through argparse untyped, as the string "60", and
        # Scene.get_time_progression then fails on 1 / fps. Coerce it here.
        self.camera.fps = int(self.camera.fps)

    def construct(self):
        ## Beat A1 (0-9 s): fast ring on the V-w plane
        frame_a = beat_a_frame()
        a1 = SegmentA("A1")
        st1, dy1 = a1.static(), a1.dynamic()
        self.add(frame_a, st1, dy1)
        self.wait(A_LEAD)
        a1.run(self)                                               # 75 ms at x1/40 = 3 s
        cap1 = caption(R"\text{Fast ring: } g_{\mathrm{K,dr}} \text{ lags } V,\ g_{\mathrm{M}}"
                       R"\text{ barely moves} \rightarrow \text{the spiral lives on the } "
                       R"V\text{\textendash}w \text{ plane.}")
        path1 = a1.full_path()
        self.play(FadeIn(cap1), FadeIn(path1), run_time=0.6)
        self.play(emphasize(path1[0]), run_time=1.4)                # the spiral on V-w
        self.wait(9.0 - (A_LEAD + 3.0 + 0.6 + 1.4))

        ## Beat A2 (9-21 s): theta ring on the V-z plane
        a2 = SegmentA("A2")
        st2, dy2 = a2.static(), a2.dynamic()
        for m in dy1:
            m.clear_updaters()
        # windows change only here: out, then in (a simultaneous crossfade overlays both tick sets)
        self.play(FadeOut(VGroup(st1, dy1, path1, cap1)), run_time=0.45)
        self.play(FadeIn(VGroup(st2, dy2)), run_time=0.55)
        cap2 = caption(R"\theta \text{ ring: } g_{\mathrm{K,dr}} \text{ keeps up with } V,\ "
                       R"g_{\mathrm{M}} \text{ lags} \rightarrow \text{the spiral moved to the } "
                       R"V\text{\textendash}z \text{ plane.}")
        a2.run(self, extra=[FadeIn(cap2, time_span=(3.0, 3.6))])   # 2 s at x1/4 = 8 s
        path2 = a2.full_path()
        self.play(FadeIn(path2), run_time=0.6)
        self.wait(21.0 - (10.0 + 8.0 + 0.6))

        ## Beat A3 (21-24 s): same spiral, slower variable; crossfade to Beat B
        cap3 = caption(R"\text{Same spiral as slide 3 \textemdash{} on a slower variable.}")
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.5)
        self.play(emphasize(path2[1]), run_time=1.5)                # the spiral on V-z
        for m in dy2:
            m.clear_updaters()
        beat_a = VGroup(frame_a, st2, dy2, path2, cap3)
        self.play(FadeOut(beat_a), run_time=1.0)

        ## Beat B1 (24-30 s): control
        self.build_b()
        self.play(FadeIn(self.b_static), FadeIn(self.b_live), FadeIn(self.b_disc["control"]),
                  run_time=1.0)
        self.set_caption(R"\text{Control: threshold sits low on } I_{\mathrm{M}}\text{'s curve}"
                         R" \rightarrow I_{\mathrm{M}} \approx \text{off} \rightarrow \text{no ring.}")
        self.wait(30.0 - 25.5)

        ## Beat B2 (30-36 s): 33% Na+ inactivation
        self.to_state("inact", run_time=1.0)
        self.set_caption(R"\text{Slow Na}^{+}\text{ inactivation raises threshold} \rightarrow "
                         R"I_{\mathrm{M}} \text{ recruited} \rightarrow \theta \text{ ring.}")
        self.wait(36.0 - 31.5)

        ## Beat B3 (36-42 s): reset to control, then shunt
        self.to_state("control", run_time=0.8)
        self.to_state("shunt", run_time=1.0)
        self.set_caption(R"\text{Shunting does the same.}")
        self.wait(42.0 - 38.3)

        ## Beat B4 (42-47.4 s): inactivation, then delete I_M
        self.to_state("inact", run_time=0.8)
        self.to_state("noIM", run_time=1.0)
        self.set_caption(R"\text{Delete } I_{\mathrm{M}} \rightarrow \text{no } \theta"
                         R" \text{ ring: the effect runs through } I_{\mathrm{M}}\text{.}")
        self.wait(47.4 - 44.3)

        ## End frame (47.4-50 s): four spectra overlaid
        self.end_overlay()
        self.wait(2.0)

    # ------------------------------------------------------------ Beat B construction
    def build_b(self):
        zp = Panel(ZP_BOX, (-50.0, -30.0), (0.0, 10.0))
        vz = Panel(VZ_BOX, *VZ_RANGE)
        sp = Panel(SP_BOX, SP_X, SP_Y)
        self.zp, self.vz, self.sp = zp, vz, sp
        st = VGroup()

        # z_inf panel
        st.add(zp.axes(), zp.xticks([-50, -45, -40, -35, -30]), zp.yticks([0, 5, 10]))
        zt = tex(R"I_{\mathrm{M}}\text{ activation } z_\infty(V)", font_size=LABEL_FS,
                 t2c={R"I_{\mathrm{M}}": P.IM})
        zt.move_to([0, ZP_BOX[3] + 0.32, 0]).align_to([ZP_BOX[0], 0, 0], LEFT)
        zx = txt("V (mV)", font_size=LABEL_FS).next_to([ZP_BOX[1], ZP_BOX[2], 0], DOWN, buff=0.45)
        zx.align_to([ZP_BOX[1], 0, 0], RIGHT)
        zy = tex(R"z_\infty\ (\%)", font_size=LABEL_FS).rotate(PI / 2)
        zy.move_to([ZP_BOX[0] - 0.85, (ZP_BOX[2] + ZP_BOX[3]) / 2, 0])
        st.add(zt, zx, zy)
        Vz = np.linspace(-50, -30, 600)
        self.zcurve = zp.curve(Vz, 100 * P.z_inf(Vz, P.FIG9), P.IM, 4)

        # I_M meter
        mx0, mx1 = METER_X
        mw = mx1 - mx0
        m_lab = tex(R"I_{\mathrm{M}}\text{ at threshold } (\mu\mathrm{A/cm^2})", font_size=LABEL_FS,
                    t2c={R"I_{\mathrm{M}}": P.IM})
        m_lab.move_to([0, METER_Y + 0.5, 0]).align_to([mx0, 0, 0], LEFT)
        m_box = Rectangle(width=mw, height=0.32).move_to([(mx0 + mx1) / 2, METER_Y, 0])
        m_box.set_stroke(AX_COLOR, 2)
        m_ticks = VGroup()
        for k in range(6):
            x = mx0 + k / METER_MAX * mw
            m_ticks.add(Line([x, METER_Y - 0.16, 0], [x, METER_Y - 0.24, 0]).set_stroke(AX_COLOR, 2))
            m_ticks.add(txt(str(k), font_size=TICK_FS).set_color(AX_COLOR)
                        .move_to([x, METER_Y - 0.42, 0]))
        st.add(m_lab, m_box, m_ticks)

        # V-z plane
        st.add(vz.axes(), vz.xticks([-45, -40, -35]),
               vz.yticks([0, 0.02, 0.04], labels=[txt(s, font_size=TICK_FS)
                                                  for s in ("0", "0.02", "0.04")]))
        vt = tex(R"V\text{\textendash}z\text{ plane}\ \ (0.995\times I_{\mathrm{bif}})",
                 font_size=LABEL_FS)
        vt.move_to([0, VZ_BOX[3] + 0.3, 0]).align_to([VZ_BOX[0], 0, 0], LEFT)
        vx = txt("V (mV)", font_size=LABEL_FS).next_to([VZ_BOX[1], VZ_BOX[2], 0], RIGHT, buff=0.12)
        vx.shift(0.12 * DOWN)
        vy = tex("z", font_size=36).set_color(P.IM).move_to([VZ_BOX[0] - 0.85,
                                                             (VZ_BOX[2] + VZ_BOX[3]) / 2, 0])
        st.add(vt, vx, vy)
        self.Vg = np.linspace(*VZ_RANGE[0], 700)
        self.znull = vz.curve(self.Vg, P.z_nullcline(self.Vg, P.FIG9), P.W_NULL)

        # spectrum
        band = Rectangle(width=sp.pt(1.0, -9)[0] - sp.pt(np.log10(3), -9)[0],
                         height=SP_BOX[3] - SP_BOX[2])
        band.set_fill(P.THETA_BAND, P.THETA_ALPHA).set_stroke(width=0)
        band.move_to([(sp.pt(1.0, -9)[0] + sp.pt(np.log10(3), -9)[0]) / 2,
                      (SP_BOX[2] + SP_BOX[3]) / 2, 0])
        theta = tex(R"\theta", font_size=LABEL_FS).set_color(P.THETA_BAND)
        theta.next_to(band, UP, buff=0.05).shift(0.02 * DOWN)
        minor = [np.log10(m * 10 ** e) for e in (0, 1) for m in range(2, 10)]
        st.add(band, theta, sp.axes(),
               sp.xticks([0, 1, 2], labels=[txt(s, font_size=TICK_FS) for s in ("1", "10", "100")]))
        for x in minor:
            X = sp.pt(x, -9)[0]
            st.add(Line([X, SP_BOX[2], 0], [X, SP_BOX[2] - 0.05, 0]).set_stroke(AX_COLOR, 1.5))
        st.add(sp.yticks([-8, -6, -4, -2], labels=[tex(f"10^{{{e}}}", font_size=TICK_FS)
                                                   for e in (-8, -6, -4, -2)]))
        sx = txt("frequency (Hz)", font_size=LABEL_FS)
        sx.next_to([sum(SP_BOX[:2]) / 2, SP_BOX[2], 0], DOWN, buff=0.4)
        sy = tex(R"\text{power (mV}^2\text{/Hz)}", font_size=TICK_FS).rotate(PI / 2)
        sy.move_to([SP_BOX[0] - 0.95, (SP_BOX[2] + SP_BOX[3]) / 2, 0])
        foot = txt("spectra precomputed per condition", font_size=TICK_FS).set_color(P.MUTED)
        foot.move_to([0, METER_Y - 0.9, 0]).align_to([METER_X[0], 0, 0], LEFT)
        st.add(sx, sy, foot)
        self.b_static = st

        # live state: every continuous quantity interpolates prev -> target with one tracker
        self.s = ValueTracker(1.0)
        self.state = self.b_target("control")
        self.prev = dict(self.state)

        def cur(key):
            a, b = np.asarray(self.prev[key]), np.asarray(self.state[key])
            return a + self.s.get_value() * (b - a)

        self.cur = cur
        live = VGroup()

        # z_inf curve (fades to a grey ghost when I_M is deleted)
        def upd_zcurve(m):
            a = float(cur("im_on"))
            m.set_stroke(interpolate_color(P.MUTED, P.IM, a), 4, 0.25 + 0.75 * a)
        self.zcurve.add_updater(upd_zcurve)

        vstar_dot = Dot(radius=0.1, fill_color=P.IM)

        def upd_vstar(m):
            v, a = float(cur("vstar")), float(cur("im_on"))
            m.move_to(zp.pt(v, 100 * P.z_inf(v, P.FIG9)))
            m.set_fill(interpolate_color(P.MUTED, P.IM, a))
        vstar_dot.add_updater(upd_vstar)
        v_ctrl = bif("control")[1]
        ctrl_mark = Circle(radius=0.08).set_stroke(P.CLASS1, 2).set_fill(BLACK, 1)
        ctrl_mark.move_to(zp.pt(v_ctrl, 100 * P.z_inf(v_ctrl, P.FIG9)))
        vstar_lab = tex(R"V^{*}", font_size=LABEL_FS)
        vstar_lab.add_updater(lambda m: m.next_to(vstar_dot, UL, buff=0.04))

        # Delta V* bracket from the control position, at z_inf = 7%
        YB = 7.0
        bracket = VMobject()
        dv_lab = VGroup(tex(R"\Delta V^{*} = ", font_size=TICK_FS + 2),
                        DecimalNumber(0, num_decimal_places=1, include_sign=True,
                                      font_size=TICK_FS + 2),
                        txt("mV", font_size=TICK_FS + 2))

        def upd_bracket(m):
            v = float(cur("vstar"))
            a = zp.pt(v_ctrl, YB)
            b = zp.pt(v, YB)
            pts = [zp.pt(v_ctrl, YB - 0.5), a, b, zp.pt(v, YB - 0.5)]
            set_path(m, np.array(pts))
            op = float(np.clip((v - v_ctrl - 0.3) / 1.5, 0, 1))
            m.set_stroke(P.HIGHLIGHT, 3, op)
            dv_lab[1].set_value(v - v_ctrl)
            dv_lab.arrange(RIGHT, buff=0.08, aligned_edge=DOWN)
            dv_lab.next_to((a + b) / 2, UP, buff=0.1)
            dv_lab.set_opacity(op)
        bracket.add_updater(upd_bracket)
        guides = VMobject()

        def upd_guides(m):
            v = float(cur("vstar"))
            op = float(np.clip((v - v_ctrl - 0.3) / 1.5, 0, 1))
            pts = [zp.pt(v, YB - 0.5), zp.pt(v, 100 * P.z_inf(v, P.FIG9) + 0.35)]
            m.set_points(DashedLine(pts[0], pts[1], dash_length=0.06).get_points()
                         if pts[0][1] - pts[1][1] > 0.1 else np.array([pts[0]] * 3))
            m.set_stroke(P.HIGHLIGHT, 2, 0.8 * op)
        guides.add_updater(upd_guides)

        # meter fill + readout
        m_fill = Rectangle(width=1, height=0.3).set_stroke(width=0).set_fill(P.IM, 1)
        readout = DecimalNumber(0, num_decimal_places=2, font_size=LABEL_FS)
        readout.set_color(P.IM)

        def upd_meter(m):
            im = float(cur("im"))
            w = max(im / METER_MAX * mw, 1e-3)
            m.stretch_to_fit_width(w).move_to([mx0 + w / 2, METER_Y, 0])
            readout.set_value(im)
            readout.next_to([mx1, METER_Y, 0], RIGHT, buff=0.15)
        m_fill.add_updater(upd_meter)

        # V-z nullcline (V) and fixed point; greys out when I_M is deleted
        vnull = VMobject()

        def upd_vnull(m):
            a = float(cur("im_on"))
            set_path(m, vz.curve_points(self.Vg, cur("vnull")))
            m.set_stroke(P.V_NULL, 3, a)
        vnull.add_updater(upd_vnull)
        self.znull.add_updater(lambda m: m.set_stroke(P.W_NULL, 3, 0.15 + 0.85 * float(cur("im_on"))))
        fp_dot = Dot(radius=0.08, fill_color=WHITE)

        zn_g = P.z_nullcline(self.Vg, P.FIG9)

        def upd_fp(m):
            # follow the intersection of the (interpolated) V-nullcline with z_inf that is
            # nearest the interpolated fixed point, so the dot never leaves the curves
            v, z = cur("fp")
            d = cur("vnull") - zn_g
            i = np.flatnonzero(np.sign(d[:-1]) != np.sign(d[1:]))
            roots = self.Vg[i] - d[i] * (self.Vg[i + 1] - self.Vg[i]) / (d[i + 1] - d[i])
            roots = roots[(np.abs(roots - v) < 1.5)
                          & (P.z_nullcline(roots, P.FIG9) < VZ_RANGE[1][1])]
            near = len(roots) > 0
            if near:
                v = float(roots[np.argmin(np.abs(roots - v))])
                z = float(P.z_nullcline(v, P.FIG9))
            m.move_to(vz.pt(v, z))
            # the interpolated curves are display-only and can lose an intersection midway
            # (a jump), so the dot fades out through the middle of each transition and hides
            # whenever no intersection lies near the interpolated fixed point
            mid = float(np.clip((abs(2 * self.s.get_value() - 1) - 0.4) / 0.6, 0, 1))
            m.set_opacity(float(cur("im_on")) * mid * near)
        fp_dot.add_updater(upd_fp)

        # spectrum
        fx = spec_log("control")[0]
        spec = VMobject()

        def upd_spec(m):
            set_path(m, sp.pts(fx, cur("spec")))
            m.set_stroke(rgb_to_color(cur("color")), 4)
        spec.add_updater(upd_spec)
        self.spec_live = spec

        live.add(self.zcurve, ctrl_mark, guides, bracket, dv_lab, vstar_dot, vstar_lab,
                 m_fill, readout, self.znull, vnull, fp_dot, spec)
        live.update()
        self.b_live = live

        # discrete, per-condition labels
        self.b_disc = {n: self.b_discrete(n) for n in B_ORDER}
        self.cur_state = "control"
        self.cap = None

    def b_target(self, name):
        p = VARIANTS[name]
        f = fp(name)
        vn = vnull_B(name, self.Vg)
        prev = getattr(self, "state", None)
        return dict(
            vstar=bif(name)[1], im=im_at_vstar(name), im_on=1.0 if p.g_adapt > 0 else 0.0,
            vnull=vn if vn is not None else prev["vnull"],
            fp=np.array([f["V"], f["z"]]) if p.g_adapt > 0 else prev["fp"],
            spec=spec_log(name)[1], color=color_to_rgb(VARIANT_COLOR[name]),
        )

    def b_discrete(self, name):
        g = VGroup()
        cond = {
            "control": R"\text{control}",
            "inact": R"\text{33\% Na}^{+}\text{ inactivation}",
            "shunt": R"\text{shunt } (g_{\mathrm{shunt}}\ 2 \rightarrow 3.5)",
            "noIM": R"\text{33\% Na}^{+}\text{ inactivation, } I_{\mathrm{M}}\text{ removed}",
        }[name]
        lab = tex(cond, font_size=38).set_color(VARIANT_COLOR[name])
        lab.move_to([0, 3.55, 0]).align_to([ZP_BOX[0] - 1.0, 0, 0], LEFT)
        g.add(lab)
        lam = chip(tex(lam_tex(name), font_size=26))
        lam.move_to([0, 3.55, 0]).align_to([6.9, 0, 0], RIGHT)
        g.add(lam)
        vz = self.vz
        if name in FP_LABEL:
            f = fp(name)
            fl = txt(FP_LABEL[name], font_size=LABEL_FS).set_color(WHITE)
            if name == "control":
                sad = next(x for x in P.fixed_points_3d(VARIANTS[name], hold_I(name))
                           if x["kind"] == "saddle")
                ring = Circle(radius=0.08).set_stroke(WHITE, 2).set_fill(BLACK, 1)
                ring.move_to(vz.pt(sad["V"], sad["z"]))
                g.add(ring)
                fl.next_to(vz.pt((f["V"] + sad["V"]) / 2, 0.004), UP, buff=0.35)
            else:
                fl.next_to(vz.pt(f["V"], f["z"]), DR, buff=0.2)
            g.add(fl)
        else:
            veil = Rectangle(width=VZ_BOX[1] - VZ_BOX[0], height=VZ_BOX[3] - VZ_BOX[2])
            veil.move_to([sum(VZ_BOX[:2]) / 2, sum(VZ_BOX[2:]) / 2, 0])
            veil.set_fill(BLACK, 0.6).set_stroke(width=0)
            nolab = tex(R"\text{no } I_{\mathrm{M}}", font_size=40).set_color(P.MUTED)
            nolab.move_to(veil)
            g.add(veil, nolab)
        st = stats_B(name)
        if name in ("inact", "shunt"):
            y = np.log10(run_B(name)["Pxx"][
                np.argmin(np.abs(run_B(name)["f"] - st["peak"]))])
            pk = txt(f"{st['peak']:.2f} Hz".replace(".50 ", ".5 "), font_size=TICK_FS)
            pk.set_color(VARIANT_COLOR[name])
            pk.move_to(self.sp.pt(np.log10(10.5), y), aligned_edge=LEFT).shift(0.05 * UP)
            g.add(pk)
        return g

    def set_caption(self, s):
        new = caption(s)
        anims = [FadeIn(new)]
        if self.cap is not None:
            anims.append(FadeOut(self.cap))
        self.play(*anims, run_time=0.5)
        self.cap = new

    def to_state(self, name, run_time=1.0):
        self.prev = {k: self.cur(k) for k in self.state}
        self.state = self.b_target(name)
        self.s.set_value(0.0)
        old = self.b_disc[self.cur_state]
        self.play(self.s.animate.set_value(1.0), FadeOut(old), FadeIn(self.b_disc[name]),
                  run_time=run_time, rate_func=smooth)
        self.cur_state = name

    def end_overlay(self):
        sp = self.sp
        curves, legend = VGroup(), VGroup()
        names = {"control": R"\text{control}", "inact": R"\text{Na}^{+}\text{ inact.}",
                 "shunt": R"\text{shunt}", "noIM": R"\text{no } I_{\mathrm{M}}"}
        for n in B_ORDER:
            fx, fy = spec_log(n)
            curves.add(VMobject().set_points_as_corners(sp.pts(fx, fy))
                       .set_stroke(VARIANT_COLOR[n], 3))
            row = VGroup(Line(ORIGIN, 0.4 * RIGHT).set_stroke(VARIANT_COLOR[n], 4),
                         tex(names[n], font_size=TICK_FS).set_color(VARIANT_COLOR[n]))
            row.arrange(RIGHT, buff=0.12)
            legend.add(row)
        legend.arrange_in_grid(2, 2, h_buff=0.3, v_buff=0.1, aligned_edge=LEFT, fill_rows_first=True)
        legend.move_to([SP_BOX[0] + 0.12, SP_BOX[2] + 0.1, 0], aligned_edge=DL)
        self.spec_live.clear_updaters()
        self.play(FadeIn(curves), FadeIn(legend), FadeOut(self.spec_live), run_time=0.6)


# ================================================================ acceptance checks
def _close(a, b, rel):
    return abs(a - b) <= rel * abs(b)


if __name__ == "__main__":
    print("Noise / holding settings (seed %d, dt %.2f ms):" % (SEED, DT))
    for n, (p, frac, sig, tau, win, slow) in SEGMENTS.items():
        print(f"  {n}: hold {frac} x I_bif, sigma {sig}, tau_noise {tau} ms, "
              f"window {win} ms at x1/{slow}")
    print(f"  Beat B: hold {B_FRAC} x I_bif, sigma {B_SIGMA}, tau_noise {B_TAU} ms")

    print("I_bif:")
    for n, v in EXPECT_IBIF.items():
        print(f"  {n:8s} {ibif(n):8.3f}  (expect {v})")
        assert abs(ibif(n) - v) <= 0.05, n

    print("3-D eigenvalues at the held fixed point (s^-1):")
    for n, exp in EXPECT_EIG.items():
        got = eig_s(n)
        print(f"  {n:8s} " + ", ".join(f"{e.real:.2f}{e.imag:+.2f}i" if abs(e.imag) > 1e-9
                                         else f"{e.real:.2f}" for e in got)
              + (f"   ring {ring_hz(n):.2f} Hz" if ring_hz(n) > 0 else ""))
        assert len(got) == len(exp), (n, got)
        for g, e in zip(got, exp):
            assert _close(g.real, e.real, 0.03), (n, g, e)
            assert _close(g.imag, e.imag, 0.03) if abs(e.imag) > 0 else abs(g.imag) < 1e-9

    print("Beat A:")
    for n in SEGMENTS:
        s = stats_A(n)
        print(f"  {n}: spikes {s['spikes']}, V p-p(99%) {s['pp']:.2f} mV, SD {s['sd']:.2f}, "
              f"peak {s['peak']:.2f} Hz, lag g_Kdr {s['lag_K']:.1f} deg, g_M {s['lag_M']:.1f} deg,"
              f" window mod V {100*s['mod_V']:.1f}% g_Kdr {100*s['mod_K']:.1f}% "
              f"g_M {100*s['mod_M']:.2f}%")
        assert s["spikes"] == 0 and 1.0 <= s["pp"] <= 2.0, n
    print("  spans", {k: round(v, 5) for k, v in spans_A().items()},
          "centres", {n: {k: round(v, 5) for k, v in centre_A(n).items()} for n in SEGMENTS})
    for n in SEGMENTS:  # the displayed stretch never leaves its fixed windows
        r, rg, (i0, i1) = run_A(n), ranges_A(n), window_A(n)
        for ax in ("V", "w", "z"):
            lo, hi = r[ax][i0:i1].min(), r[ax][i0:i1].max()
            print(f"  {n} {ax} shown {lo:.5f}..{hi:.5f} inside window {rg[ax][0]:.5f}.."
                  f"{rg[ax][1]:.5f}")
            assert rg[ax][0] < lo and hi < rg[ax][1], (n, ax)
    sA2 = stats_A("A2")
    assert 8 <= sA2["peak"] <= 11
    assert sA2["lag_M"] >= 60 and sA2["lag_K"] < 15

    print("Beat B:")
    for n in VARIANTS:
        s, b = stats_B(n), bif(n)
        print(f"  {n:8s} {b[0]:4s} V* {b[1]:.2f}  z_inf(V*) {100*P.z_inf(b[1], VARIANTS[n]):.2f}%"
              f"  I_M(V*) {im_at_vstar(n):.2f}  spikes {s['spikes']}  V p-p {s['pp']:.2f}"
              f"  vmax {s['vmax']:.1f}  peak {s['peak']:.2f} Hz  ratio {s['ratio']:.1f}"
              f"  P {s['pmin']:.1e}..{s['pmax']:.1e}")
        assert s["spikes"] == 0, n
        assert abs(im_at_vstar(n) - EXPECT_IM[n]) <= 0.05, n
    for n in ("inact", "shunt"):
        assert stats_B(n)["ratio"] >= 5 and 3 <= stats_B(n)["peak"] <= 10.5, n
    for n in ("control", "noIM"):
        assert stats_B(n)["ratio"] < 3, n
    print("ok")
