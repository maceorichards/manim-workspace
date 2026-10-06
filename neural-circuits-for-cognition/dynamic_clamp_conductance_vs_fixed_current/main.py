"""Dynamic clamp in action.

Contract: context_files/contract.md

Beats as built (15.1 s at 30 fps, 1344x1200):
1. 0.0-1.5 s   Opening still: two titled columns (input strip, V, injected current),
               "spikes: 0" x2 in the title row, -70 mV and 175 pA dashed lines.
2. 1.5-12.0 s  One ValueTracker sweeps 0->500 ms at 47.6 ms/s (five linear segments);
               YELLOW cursors in sync; left counter ticks to 9, right stays 0;
               left current flat at 175 pA, right (PURPLE_C) tracks right V.
3. 5.9-7.9 s   Callout at t = 209.2 ms on the right: up-arrows at the V bump and the
               current peak, "V up -> outward current up" between the panels; fades by 7.9 s.
4. 12.0-12.5 s Cursors fade; 175 pA lines brighten; "same average: 175 pA" (left panel).
5. 12.5-13.5 s Two-line caption writes in.
6. 13.5-15.1 s Hold end frame.

Layout deviations from contract section 4 (see WORKBENCH.md): 0.95-unit tick gutter at the
far left, so each column's data is 3.525 wide (0.00705 units/ms) and the gap is 0.4;
spike counters sit in the title row (right-aligned); the current-panel label and the
"-70 mV" label (which doubles as the -70 tick) are in the left column only.
"""

import math

import numpy as np

from common import *

# ---------------------------------------------------------------- model (model.md)
C_M, E_NA, E_K, E_SH = 2.0, 50.0, -100.0, -70.0
G_NA, G_KDR, G_SH, PHI = 20.0, 20.0, 2.0, 0.25
B_M, G_M, B_W, G_W = -1.2, 18.0, -9.0, 10.0
DT, BURN, T_SHOW = 0.01, 100.0, 500.0
I0, NOISE_SD, NOISE_TAU, SEED = 90.0, 12.0, 5.0, 1
G_DC, E_DC = 10 / 3, -70.0
PA_PER_UA = 3.0          # 300 um^2 cell: uA/cm^2 x 3 = pA
DECIMATE = 5             # polyline sample every 0.05 ms
CALLOUT_T = 209.2        # ms, right-column V bump (model.md section 5)


def ou_noise(n, seed=SEED, sd=NOISE_SD, tau=NOISE_TAU, dt=DT):
    """Exact discrete OU update, x[0] = 0, one rng draw for all steps."""
    xi = np.random.default_rng(seed).standard_normal(n)
    a = math.exp(-dt / tau)
    b = sd * math.sqrt(1 - a * a)
    x = np.empty(n)
    x[0] = 0.0
    for i in range(1, n):
        x[i] = a * x[i - 1] + b * xi[i]
    return x


def simulate(noise, g_dc=0.0, offset=0.0):
    """Forward-Euler Morris-Lecar; returns (V, I_inj) after burn-in. I_inj depolarizing +."""
    n = len(noise)
    k = int(round(BURN / DT))
    V = -69.39
    w = 0.5 * (1 + math.tanh((V - B_W) / G_W))
    Vs = np.empty(n)
    Is = np.empty(n)
    for i in range(n):
        Iinj = offset - g_dc * (V - E_DC)
        minf = 0.5 * (1 + math.tanh((V - B_M) / G_M))
        winf = 0.5 * (1 + math.tanh((V - B_W) / G_W))
        tauw = 1 / math.cosh((V - B_W) / (2 * G_W))
        Iion = G_NA * minf * (V - E_NA) + G_KDR * w * (V - E_K) + G_SH * (V - E_SH)
        dV = (I0 + noise[i] + Iinj - Iion) / C_M
        dw = PHI * (winf - w) / tauw
        V += DT * dV
        w += DT * dw
        Vs[i] = V
        Is[i] = Iinj
    return Vs[k:], Is[k:]


def spike_times(t, V):
    """Upward crossings of 0 mV."""
    return t[1:][(V[:-1] < 0) & (V[1:] >= 0)]


def run_model():
    """Right (dynamic clamp) first, then left with the matched constant offset."""
    n = int(round((BURN + T_SHOW) / DT))
    k = int(round(BURN / DT))
    noise = ou_noise(n)
    VR, IR = simulate(noise, g_dc=G_DC)
    offset = IR.mean()
    VL, IL = simulate(noise, offset=offset)
    t = np.arange(len(VL)) * DT
    return dict(
        t=t, VL=VL, VR=VR,
        IL=-IL * PA_PER_UA, IR=-IR * PA_PER_UA,          # outward-positive, pA
        inp=(I0 + noise[k:]) * PA_PER_UA,                 # pA
        offset=offset,
        spikes_L=spike_times(t, VL), spikes_R=spike_times(t, VR),
    )


# ---------------------------------------------------------------- layout (contract.md section 4)
TICK_W = 0.95                     # left tick-label gutter (inside +-4.2)
COL_GAP = 0.4
COL_W = (8.4 - TICK_W - COL_GAP) / 2      # 3.525
COL_X0 = [-4.2 + TICK_W, -4.2 + TICK_W + COL_W + COL_GAP]   # data left edges
MS_TO_X = COL_W / T_SHOW

IN_Y, IN_R = (2.35, 2.85), (150.0, 400.0)
V_Y, V_R = (-0.3, 2.1), (-80.0, 30.0)
I_Y, I_R = (-2.55, -0.75), (100.0, 275.0)
MEAN_PA = 175.0


def lin(val, src, dst):
    return dst[0] + (val - src[0]) * (dst[1] - dst[0]) / (src[1] - src[0])


def to_points(col, t, y):
    x = COL_X0[col] + t * MS_TO_X
    return np.column_stack([x, y, np.zeros_like(x)])


class DynamicClampVsFixedCurrent(Scene):
    def construct(self):
        self.opening()
        self.sweep()
        self.same_average()
        self.caption()
        self.hold()

    def opening(self):
        ## Opening still: titles, labelled empty panels, counters at 0
        d = run_model()
        self.d = d
        t = d["t"][::DECIMATE]
        self.t_dec = t

        chrome = VGroup()
        # column titles (left-aligned) and spike counters (right-aligned) share the top row
        titles = VGroup()
        for col, (l1, l2), color in [(0, ("current clamp,", "constant offset"), WHITE),
                                     (1, ("dynamic clamp,", "10 nS at −70 mV"), PURPLE_C)]:
            ttl = VGroup(txt(l1, font_size=28), txt(l2, font_size=28))
            ttl.set_color(color).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            ttl.move_to([COL_X0[col], 3.75, 0], aligned_edge=UL)
            titles.add(ttl)
        chrome.add(titles)

        self.counter_digits = [txt(f"spikes: {k}", font_size=28) for k in range(10)]
        self.counters = VGroup()
        for col in range(2):
            c = self.counter_digits[0].copy()
            c.move_to([COL_X0[col] + COL_W, titles[col].get_center()[1], 0], aligned_edge=RIGHT)
            self.counters.add(c)

        for col in range(2):
            x0, x1 = COL_X0[col], COL_X0[col] + COL_W
            lab = txt("same input", font_size=24, fill_color=GREY_B)
            lab.move_to([x0, 2.97, 0], aligned_edge=LEFT)
            chrome.add(lab)
            # V panel: -70 mV reversal line
            y70 = lin(-70, V_R, V_Y)
            chrome.add(DashedLine([x0, y70, 0], [x1, y70, 0], dash_length=0.08,
                                  stroke_width=2, color=PURPLE_C))
        # 175 pA reference lines (faint), kept for the end beat
        y175 = lin(MEAN_PA, I_R, I_Y)
        self.mean_lines = VGroup(*[
            DashedLine([COL_X0[c], y175, 0], [COL_X0[c] + COL_W, y175, 0], dash_length=0.08,
                       stroke_width=2, color=GREY_D)
            for c in range(2)])

        # left-column axis chrome
        tick_x = COL_X0[0] - 0.1
        chrome.add(txt("−70 mV", font_size=24, fill_color=PURPLE_C)
                   .move_to([tick_x, lin(-70, V_R, V_Y), 0], aligned_edge=RIGHT))
        chrome.add(txt("0", font_size=24, fill_color=GREY_B)
                   .move_to([tick_x, lin(0, V_R, V_Y), 0], aligned_edge=RIGHT))
        for v in (100, 200):
            chrome.add(txt(str(v), font_size=24, fill_color=GREY_B)
                       .move_to([tick_x, lin(v, I_R, I_Y), 0], aligned_edge=RIGHT))
        chrome.add(txt("injected current (outward ↑)", font_size=24, fill_color=GREY_B)
                   .move_to([COL_X0[0], -0.53, 0], aligned_edge=LEFT))
        bar = Line([COL_X0[0], -2.85, 0], [COL_X0[0] + 100 * MS_TO_X, -2.85, 0],
                   stroke_width=3, color=GREY_B)
        bar_lab = txt("100 ms", font_size=24, fill_color=GREY_B).next_to(bar, RIGHT, buff=0.15)
        chrome.add(bar, bar_lab)

        self.add(self.mean_lines, chrome, self.counters)
        self.wait(1.5)

    def sweep(self):
        ## Sweep: synced cursors, traces draw behind them, live counters
        d, t = self.d, self.t_dec
        s = slice(None, None, DECIMATE)
        series = [  # (col, points, color, stroke)
            (0, to_points(0, t, lin(d["inp"][s], IN_R, IN_Y)), GREY_B, 2),
            (1, to_points(1, t, lin(d["inp"][s], IN_R, IN_Y)), GREY_B, 2),
            (0, to_points(0, t, lin(d["VL"][s], V_R, V_Y)), WHITE, 2.5),
            (1, to_points(1, t, lin(d["VR"][s], V_R, V_Y)), WHITE, 2.5),
            (0, to_points(0, t, lin(d["IL"][s], I_R, I_Y)), GREY_A, 3),
            (1, to_points(1, t, lin(d["IR"][s], I_R, I_Y)), PURPLE_C, 2.5),
        ]
        t_ms = ValueTracker(0.0)
        self.t_ms = t_ms

        traces = VGroup()
        for _, pts, color, sw in series:
            tr = VMobject(stroke_color=color, stroke_width=sw)
            tr.set_points_as_corners(pts[:2])

            def upd(m, pts=pts):
                i = int(np.searchsorted(t, t_ms.get_value(), side="right"))
                m.set_points_as_corners(pts[:max(i, 2)])
            tr.add_updater(upd)
            traces.add(tr)
        self.traces = traces

        cursors = VGroup()
        for col in range(2):
            cur = Line([0, IN_Y[1], 0], [0, I_Y[0], 0], stroke_width=2, color=YELLOW)
            cur.add_updater(lambda m, col=col: m.set_x(COL_X0[col] + t_ms.get_value() * MS_TO_X))
            cursors.add(cur)
        self.cursors = cursors

        spikes = [d["spikes_L"], d["spikes_R"]]
        for col, ctr in enumerate(self.counters):
            anchor = ctr.get_right().copy()
            state = {"n": 0}

            def cupd(m, col=col, anchor=anchor, state=state):
                n = int(np.searchsorted(spikes[col], t_ms.get_value(), side="right"))
                if n != state["n"]:
                    state["n"] = n
                    m.become(self.counter_digits[n].copy().move_to(anchor, aligned_edge=RIGHT))
            ctr.add_updater(cupd)

        self.add(traces, cursors, self.counters)
        speed = T_SHOW / 10.5                       # 47.6 ms per s
        seg = lambda t1: dict(run_time=(t1 - t_ms.get_value()) / speed, rate_func=linear)

        t_in = CALLOUT_T
        self.play(t_ms.animate.set_value(t_in), **seg(t_in))

        ## Callout: V up -> outward current up (right column, t ~209 ms)
        i_c = int(round(CALLOUT_T / DT))
        vx = COL_X0[1] + CALLOUT_T * MS_TO_X
        vy = lin(d["VR"][i_c], V_R, V_Y)
        iy = lin(d["IR"][i_c], I_R, I_Y)
        arrow = dict(buff=0, thickness=3, stroke_width=0, fill_color=PURPLE_C)
        arr_v = Arrow([vx, vy + 0.12, 0], [vx, vy + 0.57, 0], **arrow)
        arr_i = Arrow([vx, iy + 0.08, 0], [vx, iy + 0.42, 0], **arrow)
        lab = txt("V ↑ → outward current ↑", font_size=24).set_color(PURPLE_C)
        lab.move_to([vx, -0.5, 0])
        lab.set_x(min(max(lab.get_x(), COL_X0[1] + lab.get_width() / 2),
                      COL_X0[1] + COL_W - lab.get_width() / 2))
        callout = VGroup(arr_v, arr_i, lab)
        self.callout = callout

        t1 = CALLOUT_T + 0.8 * speed
        self.play(t_ms.animate.set_value(t1), FadeIn(callout), **seg(t1))
        t2 = t1 + 0.6 * speed
        self.play(t_ms.animate.set_value(t2), **seg(t2))
        t3 = t2 + 0.6 * speed
        self.play(t_ms.animate.set_value(t3), FadeOut(callout), **seg(t3))
        self.remove(callout)

        ## Sweep to the end
        self.play(t_ms.animate.set_value(T_SHOW), **seg(T_SHOW))
        for m in [*traces, *cursors, *self.counters]:
            m.clear_updaters()

    def same_average(self):
        ## Cursors fade; 175 pA lines brighten with label
        lab = txt(f"same average: {MEAN_PA:.0f} pA", font_size=24, fill_color=GREY_B)
        lab.move_to([COL_X0[0] + COL_W / 2, lin(145, I_R, I_Y), 0])
        self.play(
            FadeOut(self.cursors),
            self.mean_lines.animate.set_stroke(GREY_B, width=2),
            FadeIn(lab),
            run_time=0.5,
        )
        self.remove(self.cursors)

    def caption(self):
        ## Caption writes in
        cap = VGroup(
            txt("the injected current depends on voltage —", font_size=32),
            txt("that is what makes it a conductance", font_size=32),
        ).arrange(DOWN, buff=0.12)
        cap.move_to([0, -3.75, 0], aligned_edge=DOWN)
        self.play(Write(cap), run_time=1.0)

    def hold(self):
        ## Hold end frame
        self.wait(1.5)


if __name__ == "__main__":
    d = run_model()
    sL, sR = d["spikes_L"], d["spikes_R"]
    assert len(sL) == 9 and len(sR) == 0, (len(sL), len(sR))
    assert abs(d["offset"] + 58.443) < 0.01, d["offset"]
    expect = [26.1, 114.8, 162.4, 210.1, 269.6, 297.0, 328.8, 337.5, 449.0]
    assert np.allclose(sL, expect, atol=0.1), sL
    assert d["VR"].min() > -58.5 and d["VR"].max() < -43.5, (d["VR"].min(), d["VR"].max())
    assert d["VL"].min() > -77 and d["VL"].max() > 26
    assert np.ptp(d["IL"]) < 1e-9 and abs(d["IL"][0] - 175.3) < 0.1
    assert 120 < d["IR"].min() < 122 and 260 < d["IR"].max() < 262
    assert abs(d["IR"].mean() - d["IL"].mean()) < 1e-6
    assert np.corrcoef(d["IR"][1:], d["VR"][:-1])[0, 1] > 0.9999
    assert (d["VR"] > -70).all()                     # clamp current always outward
    assert 168 < d["inp"].min() and d["inp"].max() < 391   # 169-390 pA
    i_c = int(round(CALLOUT_T / DT))
    assert abs(d["VR"][i_c] + 46.7) < 0.2 and abs(d["IR"][i_c] - 233) < 1.5, (d["VR"][i_c], d["IR"][i_c])
    sub = d["VL"] < -30
    print(f"ok  spikes L={len(sL)} R={len(sR)}  offset={d['offset']:.3f}  "
          f"SD L={d['VL'][sub].std():.2f} R={d['VR'].std():.2f}  "
          f"IR {d['IR'].min():.0f}-{d['IR'].max():.0f} pA")
