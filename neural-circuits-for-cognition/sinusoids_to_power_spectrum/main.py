"""From sinusoids to spectra (~40 s, 1920x1080, 60 fps).

Spec: context_files/contract.md (Beat C cut, timings moved: see WORKBENCH.md).
Model/data recipes: context_files/model.md.

Beats:
  A. Build a signal from three sinusoids; Re/Im/power stems; a phase spin leaves power unchanged
  B. Live power spectrum: noise, then a 6-Hz and a 40-Hz rhythm each raise a peak

As built (video s; 2400 frames = 40.0 s at 60 fps):
  0-2 empty axes + caption | 2-11 each component draws 1 s, stems grow 1 s, hold 1 s |
  11-11.9 "unchanged" box + label | 11.3 on: 6-Hz phase spins (0.5 turn/s after a 1-s ramp) |
  17 caption 2 | 20-21 A out (spin frozen), B in | 21.5 "Noise only" | 25 6-Hz rhythm enters +
  caption, 26.5 marker | 31 40-Hz rhythm enters + caption, 32.5 marker | 37.5-38.5 scroll eases
  to a stop | still hold to 40.

Everything on screen is a pure function of one master clock (video time, s) held in a
ValueTracker; `advance(t)` moves it linearly and runs any fades alongside. Live objects fade by
a clock-driven opacity rather than FadeIn/FadeOut, because animations suspend updaters.
"""


from common import *

from scipy.signal import welch

import prescott2008 as P  # <area>/prescott2008.py, on sys.path via common

FS = 1000

# ================================================================ Beat A model (model.md)
COMP_F = (3.0, 6.0, 12.0)
COMP_COL = (P.COMP_3HZ, P.COMP_6HZ, P.COMP_12HZ)
A6 = 0.6


def comp_ab(k, phi):
    """(a, b) of component k; the 6-Hz one slides by phase phi: 0.6 (cos phi, sin phi)."""
    if k == 0:
        return 1.0, 0.0
    if k == 1:
        return A6 * np.cos(phi), A6 * np.sin(phi)
    return 0.0, 0.35


def comp_wave(t, k, phi):
    a, b = comp_ab(k, phi)
    w = 2 * np.pi * COMP_F[k] * t
    return a * np.cos(w) + b * np.sin(w)


def stems_ab(a, b):
    """Analytic stems (convention x = a cos + b sin <-> X = a + ib). Never from an FFT."""
    return a, b, a * a + b * b


def sum_wave(t, phi, weights=(1.0, 1.0, 1.0)):
    return sum(np.asarray(w) * comp_wave(t, k, phi) for k, w in enumerate(weights))


# ================================================================ Beat B model
B_SEED, B_DUR, B_TAU, B_SD = 0, 20.0, 0.010, 0.4
B_WIN = 2.0
ON6_T, ON40_T = 7.0, 13.0       # signal time each rhythm starts (1-s amplitude ramp)


def make_beat_b():
    n = int(B_DUR * FS)
    rng = np.random.default_rng(B_SEED)
    xi = rng.standard_normal(n)
    a = np.exp(-1 / (FS * B_TAU))
    c = np.sqrt(1 - a * a)
    x = np.empty(n)
    x[0] = xi[0]
    for i in range(1, n):
        x[i] = a * x[i - 1] + c * xi[i]
    x = x / x.std() * B_SD
    T = np.arange(n) / FS
    r6 = np.clip(T - ON6_T, 0, 1)
    r40 = np.clip(T - ON40_T, 0, 1)
    s = x + 1.0 * r6 * np.sin(2 * np.pi * 6 * T) + 0.6 * r40 * np.sin(2 * np.pi * 40 * T)
    return T, s


B_T, B_S = make_beat_b()


def b_window(T):
    """Sample slice of the trailing 2-s window ending at signal time T."""
    end = int(round(T * FS))
    return slice(end - int(B_WIN * FS), end)


def b_spectrum(T):
    """Welch PSD (mV^2/Hz) of the trailing window, 1-Hz bins; returns f, p over 0.5-60 Hz."""
    f, p = welch(B_S[b_window(T)], fs=FS, nperseg=1000, noverlap=500)
    keep = (f >= 0.5) & (f <= 60.0)
    return f[keep], p[keep]


def peak_ratio(f, p, f0):
    """Peak bin / median of bins 4-12 Hz away from the peak."""
    i = np.argmin(np.abs(f - f0))
    d = np.abs(f - f0)
    return p[i] / np.median(p[(d >= 4) & (d <= 12)])


# ================================================================ timeline (video s)
DRAW_T = (2.0, 5.0, 8.0)        # component k draws over [d, d+1], stems grow over [d+1, d+2]
SPIN_T0, SPIN_RAMP, OMEGA = 11.3, 1.0, np.pi   # 6-Hz phase spin: 0 -> 0.5 turn/s over 1 s
OUTLINE_T = 11.0
CAP_A2 = 17.0
XF_AB = (20.0, 21.0)
B_OFFSET = 18.0                 # signal T = video - 18 (window shows 0-2 s at video 20)
CAP_NOISE = 21.5
CAP_6 = ON6_T + B_OFFSET        # caption swaps as the rhythm enters the window ...
CAP_40 = ON40_T + B_OFFSET
MARK_LAG = 1.5                  # ... and its marker draws once the peak is up (ratio > 30)
STOP_T = (37.5, 38.5)           # scroll eases to a stop, then a still hold
END = 40.0


def ramp01(c, t0, dur=1.0):
    return float(smooth(np.clip((c - t0) / dur, 0, 1)))


def phi_at(c):
    """6-Hz phase: angular speed ramps linearly 0 -> OMEGA over SPIN_RAMP, then constant."""
    s = c - SPIN_T0
    if s <= 0:
        return 0.0
    if s < SPIN_RAMP:
        return OMEGA * s * s / (2 * SPIN_RAMP)
    return OMEGA * (s - SPIN_RAMP / 2)


def signal_T(c):
    """Beat B clock: T = video - 18 from 2 s, easing (speed 1 -> 0) to a stop over STOP_T."""
    if c <= STOP_T[0]:
        return float(max(c - B_OFFSET, 2.0))
    d = STOP_T[1] - STOP_T[0]
    u = min((c - STOP_T[0]) / d, 1.0)
    return float(STOP_T[0] - B_OFFSET + d / 2 * (1 - (1 - u) ** 2))


def first_half(a):
    return smooth(min(1.0, 2 * a))


def second_half(a):
    return smooth(max(0.0, 2 * a - 1))


# ================================================================ drawing helpers
TICK = 26
AXL = 30
CAP = 38
AX_STROKE = 2


class Box:
    """Map data (x, y) to frame coords; y may be log10."""

    def __init__(self, x0, x1, xr, y0, y1, yr, log=False):
        self.x0, self.x1, self.xr = x0, x1, xr
        self.y0, self.y1, self.yr = y0, y1, yr
        self.log = log

    def X(self, x):
        return self.x0 + (np.asarray(x, float) - self.xr[0]) / (self.xr[1] - self.xr[0]) * (self.x1 - self.x0)

    def Y(self, y):
        y = np.asarray(y, float)
        if self.log:
            y = np.log10(np.clip(y, 10 ** self.yr[0], 10 ** self.yr[1]))
        return self.y0 + (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * (self.y1 - self.y0)

    def pts(self, x, y):
        x, y = self.X(x), self.Y(y)
        return np.column_stack([x, y, np.zeros_like(x)])

    def p(self, x, y):
        return np.array([float(self.X(x)), float(self.Y(y)), 0.0])


def hline(x0, x1, y, color=GREY_B, w=AX_STROKE):
    return Line([x0, y, 0], [x1, y, 0], stroke_width=w, color=color)


def vline(x, y0, y1, color=GREY_B, w=AX_STROKE):
    return Line([x, y0, 0], [x, y1, 0], stroke_width=w, color=color)


def label(s, size=AXL, color=None):
    m = txt(s, font_size=size)
    if color is not None:
        m.set_color(color)
    return m


def tlabel(s, size=AXL, color=None):
    m = tex(s, font_size=size)
    if color is not None:
        m.set_color(color)
    return m


def x_ticks(box, values, y_axis, labels=True, fmt=None, size=TICK, tick=0.08):
    g = VGroup()
    for v in values:
        x = float(box.X(v))
        g.add(Line([x, y_axis, 0], [x, y_axis - tick, 0], stroke_width=AX_STROKE, color=GREY_B))
        if labels:
            s = fmt(v) if fmt else (f"{v:g}")
            g.add(label(s, size, GREY_B).move_to([x, y_axis - tick - 0.2, 0]))
    return g


def curve(color, width=4):
    m = VMobject()
    m.set_stroke(color, width)
    m.set_fill(opacity=0)
    return m


def set_curve(m, pts):
    if len(pts) < 2:
        pts = np.array([pts[0], pts[0]]) if len(pts) else np.zeros((2, 3))
    m.set_points_as_corners(pts)


# ================================================================ scene
class SinusoidsToPowerSpectrum(Scene):
    # manimlib 1.7.2 parses `--fps` as a string (no type=int) and crashes in
    # get_time_progression; the scene's camera config is merged last, so it wins.
    default_camera_config = dict(fps=60)

    def construct(self):
        self.clock = ValueTracker(0.0)
        self.caption = None
        ## Beat A
        self.beat_a()
        ## Beat B
        self.beat_b()

    # ------------------------------------------------------------ timing helpers
    def now(self):
        return self.clock.get_value()

    def advance(self, t_to, *anims):
        # Exact frame count: np.arange(0, run_time, 1/fps) in manimlib otherwise adds a frame
        # whenever run_time*fps lands a hair above an integer (56.2 s instead of 56.0).
        fps = self.camera.fps
        n = int(round(t_to * fps)) - int(round(self.now() * fps))
        assert n > 0, (self.now(), t_to)
        self.play(self.clock.animate.set_value(t_to).set_anim_args(rate_func=linear), *anims,
                  run_time=n / fps - 1e-7)

    def cap_mob(self, s, math=False, size=CAP, y=-3.55):
        m = tlabel(s, size) if math else label(s, size)
        m.move_to([0, y, 0])
        return m

    def swap_caption(self, new):
        """Back-to-back cross-fade so the two captions never overlap."""
        anims = []
        if self.caption is not None:
            anims.append(FadeOut(self.caption, rate_func=first_half))
        if new is not None:
            anims.append(FadeIn(new, rate_func=second_half))
        self.caption = new
        return anims

    # ------------------------------------------------------------ Beat A
    def beat_a(self):
        clock = self.clock
        LX0, LX1 = -5.75, 1.2
        rows_c = (3.2, 1.85, 0.5)
        rows = [Box(LX0, LX1, (0, 1), yc - 0.6, yc + 0.6, (-1.1, 1.1)) for yc in rows_c]
        sbox = Box(LX0, LX1, (0, 1), -2.2, -0.3, (-2.2, 2.2))
        static = VGroup()
        for k, (bx, yc) in enumerate(zip(rows, rows_c)):
            static.add(hline(LX0, LX1, yc), vline(LX0, bx.y0, bx.y1))
            static.add(label(f"{COMP_F[k]:g} Hz", AXL, COMP_COL[k]).move_to([-6.35, yc, 0]))
        static.add(hline(LX0, LX1, float(sbox.Y(0))), vline(LX0, sbox.y0, sbox.y1))
        static.add(label("sum", AXL, P.VOLT).move_to([-6.35, float(sbox.Y(0)), 0]))
        ruler_y = -2.3
        static.add(hline(LX0, LX1, ruler_y))
        static.add(x_ticks(sbox, [0, 0.25, 0.5, 0.75, 1.0], ruler_y, labels=False))
        for v in (0, 0.5, 1):
            static.add(label(f"{v:g}", TICK, GREY_B).move_to([float(sbox.X(v)), ruler_y - 0.27, 0]))
        static.add(label("time (s)", AXL, P.INK).move_to([(LX0 + LX1) / 2, -2.97, 0]))

        # stem plots
        SX0, SX1 = 2.55, 6.75
        re_b = Box(SX0, SX1, (0, 15), 2.55 - 0.62, 2.55 + 0.62, (-1.1, 1.1))
        im_b = Box(SX0, SX1, (0, 15), 0.45 - 0.62, 0.45 + 0.62, (-1.1, 1.1))
        pw_b = Box(SX0, SX1, (0, 15), -2.1, -2.1 + 1.35, (0, 1.1))
        titles = [
            (re_b, R"\mathrm{Re}\,X(f)\ \text{\textemdash\ cosine part}", 3.62),
            (im_b, R"\mathrm{Im}\,X(f)\ \text{\textemdash\ sine part}", 1.5),
            (pw_b, R"|X(f)|^2\ \text{\textemdash\ power}", -0.5),
        ]
        for bx, s, y in titles:
            static.add(tlabel(s, AXL, P.INK).move_to([(SX0 + SX1) / 2, y, 0]))
            y0 = float(bx.Y(0))
            static.add(hline(SX0, SX1, y0), vline(SX0, bx.y0, bx.y1))
            ticks_y = [-1, 0, 1] if bx is not pw_b else [0, 1]
            for v in ticks_y:
                yy = float(bx.Y(v))
                static.add(Line([SX0, yy, 0], [SX0 - 0.08, yy, 0], stroke_width=AX_STROKE, color=GREY_B))
                s_ = "−1" if v == -1 else f"{v:g}"
                static.add(label(s_, TICK, GREY_B).next_to([SX0 - 0.08, yy, 0], LEFT, buff=0.08))
            static.add(x_ticks(bx, [3, 6, 9, 12, 15], y0, labels=(bx is pw_b)))
        static.add(label("frequency (Hz)", AXL, P.INK).move_to([(SX0 + SX1) / 2, -2.72, 0]))
        foot = tlabel(R"\text{convention: } x = a\cos{} + b\sin\enspace\leftrightarrow\enspace X = a + ib",
                      TICK, P.MUTED)
        foot.move_to([4.25, -3.08, 0])
        static.add(foot)
        self.a_static = static

        # live: component curves, sum, stems
        comps = [curve(COMP_COL[k], 4) for k in range(3)]
        sum_c = curve(P.VOLT, 5)
        EPS = 0.03

        def reveal(c, k):
            return ramp01(c, DRAW_T[k])

        def grow(c, k):
            return ramp01(c, DRAW_T[k] + 1.0)

        def upd_comp(k):
            def f(m):
                c = clock.get_value()
                r = reveal(c, k)
                t = np.linspace(0, max(r, 1e-4), max(2, int(600 * r)))
                set_curve(m, rows[k].pts(t, comp_wave(t, k, phi_at(c))))
                m.set_stroke(opacity=1.0 if r > 1e-3 else 0.0)
            return f

        def upd_sum(m):
            c = clock.get_value()
            r0 = reveal(c, 0)
            t = np.linspace(0, max(r0, 1e-4), max(2, int(800 * r0)))
            w = [np.ones_like(t)]
            for k in (1, 2):
                e = reveal(c, k) * (1 + EPS)
                w.append(np.clip((e - t) / EPS, 0, 1))
            set_curve(m, sbox.pts(t, sum_wave(t, phi_at(c), w)))
            m.set_stroke(opacity=1.0 if r0 > 1e-3 else 0.0)

        for k, m in enumerate(comps):
            m.add_updater(upd_comp(k))
        sum_c.add_updater(upd_sum)

        stems = VGroup()
        for j, bx in enumerate((re_b, im_b, pw_b)):
            for k in range(3):
                ln = Line(ORIGIN, UP, stroke_width=4, color=COMP_COL[k])
                dot = Dot(radius=0.065, fill_color=COMP_COL[k])
                st = VGroup(ln, dot)

                def upd(m, j=j, k=k, bx=bx):
                    c = clock.get_value()
                    v = stems_ab(*comp_ab(k, phi_at(c)))[j] * grow(c, k)
                    base, tip = bx.p(COMP_F[k], 0), bx.p(COMP_F[k], v)
                    m[0].set_points_as_corners([base, tip])
                    m[1].move_to(tip)
                    op = float(np.clip(abs(v) / 0.04, 0, 1))
                    m[0].set_stroke(opacity=op)
                    m[1].set_fill(opacity=op)

                st.add_updater(upd)
                stems.add(st)
        live = VGroup(*comps, sum_c, stems)
        for m in live:
            m.update()
        self.a_live = live

        # "unchanged" outline around the 6-Hz power stem (constant 0.36)
        tip = pw_b.p(6, 0.36)
        outline = Rectangle(width=0.36, height=tip[1] - pw_b.y0 + 0.28)
        outline.set_stroke(P.HIGHLIGHT, 3).set_fill(opacity=0)
        outline.move_to([tip[0], (tip[1] + pw_b.y0) / 2 + 0.04, 0])
        unchanged = label("unchanged", 28, P.HIGHLIGHT).next_to(outline, UP, buff=0.1)

        # ---- 0-2 s: empty axes + caption (first frame reads when paused)
        cap1 = self.cap_mob("Any signal is a sum of sinusoids.")
        self.caption = cap1
        self.add(static, live, cap1)
        self.advance(DRAW_T[0])
        ## Beat A: components draw in, stems grow
        for k in range(3):
            self.advance(DRAW_T[k] + 1.0)      # draw
            self.advance(DRAW_T[k] + 2.0)      # stems
            self.advance(DRAW_T[k] + 3.0)      # hold
        ## Beat A: phase slide, power unchanged
        self.advance(OUTLINE_T + 0.4, ShowCreation(outline))
        self.advance(OUTLINE_T + 0.9, FadeIn(unchanged))
        cap2 = self.cap_mob("Phase lives in the Re/Im split — power ignores it.")
        self.advance(CAP_A2)
        self.advance(CAP_A2 + 0.6, *self.swap_caption(cap2))
        self.advance(XF_AB[0])
        self.a_all = VGroup(static, live, outline, unchanged)

    # ------------------------------------------------------------ Beat B
    def beat_b(self):
        clock = self.clock
        BX0, BX1 = -5.3, 6.5
        tr = Box(BX0, BX1, (0, B_WIN), 1.45, 3.7, (-3, 3))
        sp = Box(BX0, BX1, (0, 60), -2.3, 0.45, (-4, 1), log=True)
        static = VGroup()
        # trace axes
        static.add(hline(BX0, BX1, tr.y0), vline(BX0, tr.y0, tr.y1))
        static.add(hline(BX0, BX1, float(tr.Y(0)), color=GREY_D, w=1.5))
        for v in (-3, 0, 3):
            yy = float(tr.Y(v))
            static.add(Line([BX0, yy, 0], [BX0 - 0.08, yy, 0], stroke_width=AX_STROKE, color=GREY_B))
            static.add(label("−3" if v < 0 else f"{v}", TICK, GREY_B).next_to([BX0 - 0.08, yy, 0], LEFT, buff=0.08))
        yl = tlabel(R"\delta V\ \text{(mV)}", AXL, P.INK).rotate(PI / 2).move_to([-6.45, (tr.y0 + tr.y1) / 2, 0])
        static.add(yl)
        static.add(label("time (s)", AXL, P.INK).move_to([(BX0 + BX1) / 2, 0.82, 0]))
        # spectrum axes + bands
        th = Rectangle(width=float(sp.X(10) - sp.X(3)), height=sp.y1 - sp.y0)
        th.set_fill(P.THETA_BAND, P.THETA_ALPHA).set_stroke(width=0)
        th.move_to([float(sp.X(6.5)), (sp.y0 + sp.y1) / 2, 0])
        ga = Rectangle(width=float(sp.X(60) - sp.X(30)), height=sp.y1 - sp.y0)
        ga.set_fill(P.GAMMA_BAND, P.GAMMA_ALPHA).set_stroke(width=0)
        ga.move_to([float(sp.X(45)), (sp.y0 + sp.y1) / 2, 0])
        th_l = tlabel(R"\theta", AXL, P.THETA_BAND).move_to([float(sp.X(8.4)), sp.y1 - 0.25, 0])
        ga_l = tlabel(R"\gamma \rightarrow", AXL, P.GAMMA_BAND).move_to([float(sp.X(54)), sp.y1 - 0.25, 0])
        static.add(th, ga, th_l, ga_l)
        static.add(hline(BX0, BX1, sp.y0), vline(BX0, sp.y0, sp.y1))
        for d in range(-4, 2):
            yy = float(sp.Y(10.0 ** d))
            static.add(Line([BX0, yy, 0], [BX0 - 0.08, yy, 0], stroke_width=AX_STROKE, color=GREY_B))
            static.add(tlabel(f"10^{{{d}}}", TICK, GREY_B).next_to([BX0 - 0.08, yy, 0], LEFT, buff=0.08))
        static.add(x_ticks(sp, range(0, 61, 10), sp.y0))
        static.add(label("frequency (Hz)", AXL, P.INK).move_to([(BX0 + BX1) / 2, -2.92, 0]))
        yl2 = label("power (mV²/Hz)", 28, P.INK).rotate(PI / 2).move_to([-6.5, (sp.y0 + sp.y1) / 2, 0])
        static.add(yl2)

        def alpha_b(c):
            # back-to-back cross-fade: Beat A out in the first half, Beat B in the second
            h_ab = (XF_AB[1] - XF_AB[0]) / 2
            return float(np.clip((c - XF_AB[0] - h_ab) / h_ab, 0, 1))

        trace = curve(P.VOLT, 3)
        spec = curve(P.VOLT, 4)

        def upd_trace(m):
            c = clock.get_value()
            T = signal_T(c)
            sl = b_window(T)
            ts, vs = B_T[sl], B_S[sl]
            set_curve(m, tr.pts(ts - (T - B_WIN), np.clip(vs, -3, 3)))
            m.set_stroke(opacity=alpha_b(c))

        def upd_spec(m):
            c = clock.get_value()
            f, p = b_spectrum(signal_T(c))
            set_curve(m, sp.pts(f, p))
            m.set_stroke(opacity=alpha_b(c))

        # scrolling time ticks (labels show the actual signal time)
        tick_lbls = {s: label(f"{s}", TICK, GREY_B) for s in range(0, int(B_DUR) + 1)}
        ticks = VGroup()

        def upd_ticks(m):
            c = clock.get_value()
            T = signal_T(c)
            a = alpha_b(c)
            subs = []
            for s in range(int(np.ceil(T - B_WIN)), int(np.floor(T)) + 1):
                x = float(tr.X(s - (T - B_WIN)))
                edge = min(s - (T - B_WIN), T - s)          # s from the window edges
                op = a * float(np.clip(edge / 0.12, 0, 1))
                tk = Line([x, tr.y0, 0], [x, tr.y0 - 0.08, 0], stroke_width=AX_STROKE, color=GREY_B)
                tk.set_stroke(opacity=a)
                lb = tick_lbls[s].copy().move_to([x, tr.y0 - 0.3, 0]).set_opacity(op)
                subs += [tk, lb]
            m.set_submobjects(subs)

        trace.add_updater(upd_trace)
        spec.add_updater(upd_spec)
        ticks.add_updater(upd_ticks)
        live = VGroup(trace, spec, ticks)
        for m in live:
            m.update()

        def marker(f0):
            m = DashedLine(sp.p(f0, 10 ** -4), sp.p(f0, 10 ** 1), dash_length=0.1)
            return m.set_stroke(P.HIGHLIGHT, 2)

        mk6, mk40 = marker(6), marker(40)

        # ---- crossfade A -> B (20-21 s). Beat A is frozen by now; drop its updaters, or they
        # would reset the opacity FadeOut animates (1.7.2 does not suspend updaters).
        self.a_all.clear_updaters()
        self.add(live)
        self.advance(XF_AB[1], FadeOut(self.a_all, rate_func=first_half), FadeIn(static, rate_func=second_half),
                     *self.swap_caption(None))
        self.b_static = static
        ## Beat B: noise only
        self.advance(CAP_NOISE)
        cap = self.cap_mob("Noise only: no peaks.")
        self.advance(CAP_NOISE + 0.6, *self.swap_caption(cap))
        self.advance(CAP_6)
        ## Beat B: + 6 Hz
        cap = self.cap_mob(R"\text{+ 6 Hz (}\theta\text{): a peak rises at 6 Hz.}", math=True)
        self.advance(CAP_6 + 0.6, *self.swap_caption(cap))
        self.advance(CAP_6 + MARK_LAG)
        self.advance(CAP_6 + MARK_LAG + 0.6, ShowCreation(mk6))
        self.advance(CAP_40)
        ## Beat B: + 40 Hz
        cap = self.cap_mob(R"\text{+ 40 Hz (}\gamma\text{): a second peak \textemdash\ each rhythm gets its own peak.}",
                           math=True)
        self.advance(CAP_40 + 0.6, *self.swap_caption(cap))
        self.advance(CAP_40 + MARK_LAG)
        self.advance(CAP_40 + MARK_LAG + 0.6, ShowCreation(mk40))
        self.advance(STOP_T[1])
        self.advance(END)
        for m in live:
            m.clear_updaters()


# ================================================================ checks
def beat_a_checks():
    phis = np.array([phi_at(c) for c in np.linspace(SPIN_T0, XF_AB[0], 1001)])
    pw = np.array([stems_ab(*comp_ab(1, ph))[2] for ph in phis])
    dev = np.abs(pw - 0.36).max()
    re12 = stems_ab(*comp_ab(2, 0.0))[0]
    t = np.linspace(0, 1, 1001)
    err = max(np.abs(sum_wave(t, ph) - sum(comp_wave(t, k, ph) for k in range(3))).max()
              for ph in phis[::10])
    return phis, pw, dev, re12, err


def beat_b_checks():
    """(6-Hz ratio, 40-Hz ratio, PSD min, PSD max) at the caption swaps, markers and end."""
    out = {}
    for c in (CAP_6, CAP_6 + MARK_LAG, CAP_40, CAP_40 + MARK_LAG, END):
        T = signal_T(c)
        f, p = b_spectrum(T)
        out[c] = (T, peak_ratio(f, p, 6), peak_ratio(f, p, 40), p.min(), p.max())
    return out


if __name__ == "__main__":
    phis, pw, dev, re12, err = beat_a_checks()
    print(f"A: phase spin reaches {np.degrees(phis[-1]):.0f} deg ({phis[-1] / (2 * np.pi):.2f} turns) "
          f"by {XF_AB[0]:g} s")
    print(f"A: 6-Hz power stem over the spin: min {pw.min():.6f} max {pw.max():.6f} "
          f"(max |dev| {dev:.2e}, tol 0.0036)")
    print(f"A: 12-Hz Re stem = {re12!r}")
    print(f"A: max |sum - (x3 + x6 + x12)| = {err:.2e}")
    assert dev < 0.0036
    assert re12 == 0.0
    assert err < 1e-12

    bb = beat_b_checks()
    for c, (T, r6, r40, pmin, pmax) in bb.items():
        print(f"B: video {c:4.1f} s  T={T:4.1f}  6-Hz ratio {r6:7.1f}  40-Hz ratio {r40:7.1f}  "
              f"PSD {pmin:.1e} .. {pmax:.2e}")
    print(f"B: trace range {B_S.min():.2f} .. {B_S.max():.2f} mV (axis +-3); "
          f"OU SD {B_S[:6000].std():.3f}")
    assert signal_T(END) == B_DUR               # scroll stops exactly at the end of the record
    assert bb[CAP_6][1] < 10                    # caption swap: 6-Hz rhythm not yet in the window
    assert bb[CAP_6 + MARK_LAG][1] >= 10        # 6-Hz marker: peak is up
    assert bb[CAP_40][2] < 10
    assert min(bb[CAP_40 + MARK_LAG][1:3]) >= 10
    assert min(bb[END][1:3]) >= 10
    assert bb[END][4] < 10.0
    print("ok")
