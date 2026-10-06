"""The hump unbends.

Contract: context_files/contract.md. Render: 1344x1200, 30 fps, 12.0 s, silent.

Beats as built (Δg = added shunt, mS/cm²; every curve is the model's pinned steady-state
current asinh(net/0.45), recomputed each frame from the two ValueTrackers dg and gm):
1. B0 0.0-1.0 s  wait 1.0: control frame -- blue I-V with its hump, BLUE_C band -38.3..-31.6 mV,
   hump-top dot, "SNIC · class 1", "added shunt 0.00 mS/cm²", "input resistance −0%",
   sign-convention texts. Frame 0 is this picture.
2. B1 1.0-4.0 s  ghost of the control curve added; Δg 0 -> 0.1656 linear (3.0 s); band and
   hump shrink; readouts 0.17 / −8%.
3. B2 4.0-4.5 s  label -> "Hopf · class 2" and curve -> ORANGE on the first frame; curve stroke
   5 -> 9 -> 5 with a RED_C glow copy fading 0.8 -> 0; label pulse; dot fades; Δg 0.1656 ->
   0.2395 linear, band closes to zero width at 4.5 s; readouts 0.24 / −11%.
4. B3 4.5-6.5 s  Δg 0.2395 -> 2.00 smooth; curve becomes a steep monotonic S through
   (-34.4 mV, 0); readouts 2.00 / −52%.
5. B4 6.5-7.0 s  "(cells, 10 nS: −56%)" fades in (0.3 s) as the R_in line slides left; hold 0.2.
6. B5 7.0-9.5 s  "added g_M" line fades in (first 0.4 s); g_M 0 -> 2.00 smooth; curve steepens
   (ends −118 / +174 µA/cm²), label stays "Hopf · class 2".
7. B6 9.5-12.0 s hold end frame (contract §6).
"""

from common import *

import numpy as np
from scipy.optimize import brentq, minimize_scalar

# ---------------------------------------------------------------- model (model.md §4)
C, E_NA, E_K, E_SH = 2.0, 50.0, -100.0, -70.0
G_NA, G_KDR, PHI_W = 20.0, 20.0, 0.25
BETA_M, GAMMA_M, BETA_W, GAMMA_W, BETA_Z, GAMMA_Z = -1.2, 18.0, -9.0, 10.0, -30.0, 5.0
V_REF, KNEE = -34.435, 0.45
G_SH0 = 2.0             # control shunt (the model's only leak), mS/cm²
DG_BT = 0.1656          # added shunt at the SNIC -> Hopf switch (Bogdanov–Takens)
DG_IV = 0.2395          # added shunt at which the negative-slope region closes
DG_END, GM_END = 2.0, 2.0
G_REST = 1.8753         # control input conductance at rest, mS/cm²
V_GRID = np.linspace(-62, -21, 600)
Y_LO, Y_HI = float(np.arcsinh(-125 / KNEE)), float(np.arcsinh(180 / KNEE))


def m_inf(V): return 0.5 * (1 + np.tanh((V - BETA_M) / GAMMA_M))
def w_inf(V): return 0.5 * (1 + np.tanh((V - BETA_W) / GAMMA_W))
def tau_w(V): return 1 / np.cosh((V - BETA_W) / (2 * GAMMA_W))
def z_inf(V): return 1 / (1 + np.exp((BETA_Z - V) / GAMMA_Z))


def i_ss(V, g_sh=2.0, g_m=0.0):
    return (G_NA * m_inf(V) * (V - E_NA) + G_KDR * w_inf(V) * (V - E_K)
            + g_sh * (V - E_SH) + g_m * z_inf(V) * (V - E_K))


def net(V, g_sh=2.0, g_m=0.0): return i_ss(V, g_sh, g_m) - i_ss(V_REF, g_sh, g_m)
def yplot(i): return np.arcsinh(np.asarray(i) / KNEE)


def hump(g_sh):
    """(V_max, V_min) of the negative-slope region, or None (g_M = 0)."""
    if g_sh >= G_SH0 + DG_IV:
        return None
    a = minimize_scalar(lambda v: -i_ss(v, g_sh), bounds=(-42, V_REF), method="bounded").x
    b = minimize_scalar(lambda v: i_ss(v, g_sh), bounds=(V_REF, -28), method="bounded").x
    return a, b


def _d(f, V, h=1e-5): return (f(V + h) - f(V - h)) / (2 * h)
def slope_ss(V, g_sh): return _d(lambda v: i_ss(v, g_sh), V)


def trace(V, g_sh):
    """Trace of the 2-D (V, w) Jacobian on the fixed-point branch."""
    dIinst = _d(lambda v: G_NA * m_inf(v) * (v - E_NA), V) + G_KDR * w_inf(V) + g_sh
    return -dIinst / C - PHI_W / tau_w(V)


def v_star(g_sh):
    """Bifurcation at threshold (g_M = 0): ('SN' | 'Hopf', V)."""
    Vs = np.arange(-70, -20, 0.01)
    for a, b in zip(Vs[:-1], Vs[1:]):
        if slope_ss(b, g_sh) <= 0:
            return "SN", brentq(lambda v: slope_ss(v, g_sh), a, b)
        if trace(b, g_sh) >= 0:
            return "Hopf", brentq(lambda v: trace(v, g_sh), a, b)


def is_class2(dg, gm):
    """Label rule (contract §7): Hopf once Δg reaches the switch, or with any g_M."""
    return dg >= DG_BT - 1e-9 or gm > 0


def rin_drop(dg):
    """Input-resistance drop in % (contract §7)."""
    return 100 * dg / (G_REST + dg)


def band_edges(dg, gm):
    """Negative-slope band (V_max, V_min) while it exists, else None."""
    if gm > 0 or dg >= DG_IV:
        return None
    return hump(G_SH0 + dg)


# ---------------------------------------------------------------- layout (contract §4)
X0, X1 = -3.30, 4.00          # axes box, screen x  <->  V -62 … -21 mV
YB0, YB1 = -3.20, 1.90        # axes box, screen y  <->  yplot Y_LO … Y_HI
V_LO, V_HI = -62.0, -21.0
R_EDGE = 4.15                 # readouts right edge

C_CLASS1, C_CLASS2 = BLUE_C, ORANGE
C_SHUNT, C_GM = PURPLE_C, GREEN_C
C_OUT, C_IN, C_FLASH = TEAL_C, PINK, RED_C
C_AXIS = GREY_B


def v2x(V): return X0 + (np.asarray(V) - V_LO) / (V_HI - V_LO) * (X1 - X0)
def p2y(y): return YB0 + (np.asarray(y) - Y_LO) / (Y_HI - Y_LO) * (YB1 - YB0)


def curve_points(dg, gm):
    x = v2x(V_GRID)
    y = p2y(yplot(net(V_GRID, G_SH0 + dg, gm)))
    return np.column_stack([x, y, np.zeros_like(x)])


def iv_curve(dg, gm, color, width, opacity=1.0):
    mob = VMobject()
    mob.set_points_as_corners(curve_points(dg, gm))
    mob.set_stroke(color, width, opacity)
    mob.set_fill(opacity=0)
    return mob


class IVHumpFlattens(Scene):
    def construct(self):
        self.class2 = False               # label / curve colour state
        self.dg = ValueTracker(0.0)
        self.gm = ValueTracker(0.0)
        self.sw = ValueTracker(5.0)       # curve stroke (flash)
        self.glow = ValueTracker(0.0)     # RED_C glow copy opacity (flash)
        self.dot_op = ValueTracker(1.0)   # hump-top marker opacity
        self.rin_right = ValueTracker(R_EDGE)
        self.gm_op = ValueTracker(0.0)    # g_M readout opacity

        self.control_frame()
        self.shunt_ramp()
        self.flip_and_flash()
        self.unbend()
        self.add_adaptation()
        self.end_hold()

    # ------------------------------------------------------------ static pieces
    def build_axes(self):
        x_axis = Line([X0, YB0, 0], [X1, YB0, 0]).set_stroke(C_AXIS, 2)
        y_axis = Line([X0, YB0, 0], [X0, YB1, 0]).set_stroke(C_AXIS, 2)
        ticks, tick_labels = VGroup(), VGroup()
        for V in (-60, -50, -40, -30):
            x = float(v2x(V))
            ticks.add(Line([x, YB0, 0], [x, YB0 - 0.1, 0]).set_stroke(C_AXIS, 2))
            lab = txt(f"−{abs(V)}", font_size=28, fill_color=C_AXIS)
            lab.move_to([x, YB0 - 0.2, 0], aligned_edge=UP)
            tick_labels.add(lab)
        x_label = txt("V (mV)", font_size=28, fill_color=C_AXIS)
        # on the tick-label row at the axis end: centred under the axis it collides with "−40"
        x_label.move_to([X1, tick_labels[0].get_center()[1], 0], aligned_edge=RIGHT)
        y0 = float(p2y(0))
        zero = Line([X0, y0, 0], [X1, y0, 0]).set_stroke(WHITE, 2)
        zero_lab = txt("0", font_size=28, fill_color=C_AXIS)
        zero_lab.move_to([X0 - 0.12, y0, 0], aligned_edge=RIGHT)
        y_label = txt("net steady-state current", font_size=26, fill_color=C_AXIS)
        y_label.rotate(PI / 2).move_to([-3.75, (YB0 + YB1) / 2, 0])
        return VGroup(x_axis, y_axis, ticks, tick_labels, x_label, zero, zero_lab, y_label)

    def build_sign_texts(self):
        out1 = txt("above 0 = net outward", font_size=24, fill_color=C_OUT)
        out2 = txt("(pushes V down)", font_size=24, fill_color=C_OUT)
        out1.move_to([-3.15, 1.55, 0], aligned_edge=LEFT)
        out2.move_to([-3.15, 1.20, 0], aligned_edge=LEFT)
        in1 = txt("below 0 = net inward", font_size=24, fill_color=C_IN)
        in2 = txt("(pushes V up)", font_size=24, fill_color=C_IN)
        in1.move_to([3.95, -2.55, 0], aligned_edge=RIGHT)
        in2.move_to([3.95, -2.90, 0], aligned_edge=RIGHT)
        return VGroup(out1, out2, in1, in2)

    def class_label(self, class2):
        if class2:
            lab = txt("Hopf · class 2", font_size=40, fill_color=C_CLASS2)
        else:
            lab = txt("SNIC · class 1", font_size=40, fill_color=C_CLASS1)
        return lab.move_to([-3.2, 3.3, 0], aligned_edge=LEFT)

    # ------------------------------------------------------------ live pieces
    def build_live(self):
        dg, gm = self.dg, self.gm

        # The colour follows the label (flipped together at the start of B2), so the last
        # frame of B1 (Δg = 0.1656 exactly) is still blue under "SNIC · class 1".
        def color():
            return C_CLASS2 if self.class2 else C_CLASS1

        curve = always_redraw(lambda: iv_curve(dg.get_value(), gm.get_value(),
                                               color(), self.sw.get_value()))
        glow = always_redraw(lambda: iv_curve(dg.get_value(), gm.get_value(), C_FLASH,
                                              16, self.glow.get_value()))

        def band():
            e = band_edges(dg.get_value(), gm.get_value())
            if e is None:
                return VMobject()
            xa, xb = float(v2x(e[0])), float(v2x(e[1]))
            r = Rectangle(width=max(xb - xa, 1e-4), height=YB1 - YB0)
            r.move_to([(xa + xb) / 2, (YB0 + YB1) / 2, 0])
            return r.set_stroke(width=0).set_fill(C_CLASS1, 0.15)

        def dot():
            e = band_edges(dg.get_value(), gm.get_value())
            if e is None or self.dot_op.get_value() <= 0:
                return VMobject()
            V = e[0]
            y = float(p2y(yplot(net(V, G_SH0 + dg.get_value()))))
            d = Dot([float(v2x(V)), y, 0], radius=0.07, fill_color=C_CLASS1)
            return d.set_fill(opacity=self.dot_op.get_value())

        self.curve = curve
        self.glow_curve = glow
        self.band = always_redraw(band)
        self.dot = always_redraw(dot)

    def build_readouts(self):
        dg, gm = self.dg, self.gm

        def shunt_line():
            t = txt(f"added shunt  {dg.get_value():.2f} mS/cm²", font_size=28,
                    fill_color=C_SHUNT)
            return t.move_to([R_EDGE, 3.35, 0], aligned_edge=RIGHT)

        # Width of the two-digit state, so the prefix does not jump at 10%.
        rin_ref_w = txt("input resistance −00%", font_size=24).get_width()

        def rin_line():
            n = int(round(rin_drop(dg.get_value())))
            t = txt(f"input resistance −{n}%", font_size=24, fill_color=C_AXIS)
            t.move_to([self.rin_right.get_value() - rin_ref_w, 2.85, 0], aligned_edge=LEFT)
            return t

        self.rin_suffix = txt("(cells, 10 nS: −56%)", font_size=24, fill_color=C_AXIS)
        self.rin_suffix.move_to([R_EDGE, 2.85, 0], aligned_edge=RIGHT)
        self.rin_gap = 0.15

        gm_prefix = VGroup(txt("added", font_size=28, fill_color=C_GM),
                           tex(R"g_{\mathrm{M}}", font_size=30, fill_color=C_GM))

        def gm_line():
            val = txt(f"{gm.get_value():.2f} mS/cm²", font_size=28, fill_color=C_GM)
            val.move_to([R_EDGE, 2.35, 0], aligned_edge=RIGHT)
            base = val[0].get_bottom()[1]            # digit sits on the baseline
            pre = gm_prefix.copy()
            word, sym = pre
            word.next_to(val, LEFT, buff=0.12)
            word.shift((base - word.get_bottom()[1]) * UP)
            sym.next_to(val, LEFT, buff=0.22)
            word.next_to(sym, LEFT, buff=0.12, coor_mask=RIGHT)
            sym.shift((word[0].get_top()[1] - sym[0].get_top()[1]) * UP)  # x-heights match
            grp = VGroup(pre, val)
            return grp.set_fill(opacity=self.gm_op.get_value())

        self.shunt_line = always_redraw(shunt_line)
        self.rin_line = always_redraw(rin_line)
        self.gm_line = always_redraw(gm_line)

    # ------------------------------------------------------------ beats
    def control_frame(self):
        ## B0 control frame: blue I-V with its hump, band, dot, label, readouts, sign texts
        self.axes = self.build_axes()
        self.signs = self.build_sign_texts()
        self.build_live()
        self.build_readouts()
        self.label = self.class_label(False)
        self.ghost = iv_curve(0.0, 0.0, C_CLASS1, 3, 0.3)
        self.add(self.band, self.axes, self.signs, self.glow_curve, self.curve, self.dot,
                 self.label, self.shunt_line, self.rin_line)
        self.wait(1.0)

    def shunt_ramp(self):
        ## B1 shunt ramp: added shunt 0 -> 0.17 linear, hump shrinks, ghost of control stays
        self.add(self.ghost)
        self.bring_to_back(self.ghost)
        self.bring_to_back(self.band)
        self.play(self.dg.animate.set_value(DG_BT), run_time=3.0, rate_func=linear)

    def flip_and_flash(self):
        ## B2 flip + flash: label -> Hopf, curve -> orange at 0.17; band closes at 0.24
        assert is_class2(self.dg.get_value(), 0.0)
        new_label = self.class_label(True)
        self.class2 = True
        self.remove(self.label)
        self.label = new_label
        self.add(self.label)
        self.glow.set_value(0.8)
        self.play(
            self.dg.animate(rate_func=linear).set_value(DG_IV),
            self.sw.animate(rate_func=there_and_back).set_value(9.0),
            self.glow.animate(rate_func=linear).set_value(0.0),
            self.dot_op.animate(rate_func=linear).set_value(0.0),
            self.label.animate(rate_func=there_and_back).scale(1.12, about_edge=LEFT),
            run_time=0.5,
        )

    def unbend(self):
        ## B3 unbend: added shunt 0.24 -> 2.00, monotonic S through (-34.4, 0), R_in -52%
        self.remove(self.glow_curve, self.dot)
        self.play(self.dg.animate.set_value(DG_END), run_time=2.0, rate_func=smooth)
        ## B4 cells suffix fades in, then hold
        w = self.rin_suffix.get_width()
        self.play(FadeIn(self.rin_suffix),
                  self.rin_right.animate.set_value(R_EDGE - w - self.rin_gap),
                  run_time=0.3)
        self.wait(0.2)

    def add_adaptation(self):
        ## B5 adaptation: added g_M 0 -> 2.00 on top, curve steepens, no second flip
        self.add(self.gm_line)
        self.play(
            self.gm_op.animate(rate_func=squish_rate_func(smooth, 0, 0.16)).set_value(1.0),
            self.gm.animate(rate_func=smooth).set_value(GM_END),
            run_time=2.5,
        )

    def end_hold(self):
        ## B6 end frame hold
        self.remove(self.band)
        self.wait(2.5)


if __name__ == "__main__":
    # model.md §5 verified numbers
    vmax, vmin = hump(2.0)
    assert abs(vmax + 38.343) < 0.01 and abs(vmin + 31.624) < 0.01, (vmax, vmin)
    assert abs(i_ss(vmax) - 38.741) < 0.01 and abs(i_ss(vmin) - 37.684) < 0.01
    assert abs(i_ss(V_REF) - 38.148) < 0.01
    assert abs(net(vmax) - 0.593) < 0.005 and abs(net(vmin) + 0.464) < 0.005
    zc = [brentq(net, a, b) for a, b in [(-45, -40), (-36, -33), (-31, -28)]]
    for got, want in zip(zc, [-41.656, -34.435, -29.748]):
        assert abs(got - want) < 0.01, zc
    assert v_star(2.0)[0] == "SN" and abs(v_star(2.0)[1] + 38.343) < 0.01
    assert v_star(2.0 + DG_BT - 0.002)[0] == "SN"
    assert v_star(2.0 + DG_BT + 0.002)[0] == "Hopf"
    assert v_star(2.2)[0] == "Hopf"
    assert hump(2.239) is not None and hump(2.2396) is None
    assert abs(v_star(4.0)[1] + 31.725) < 0.01
    # minimum slope of control = -DG_IV at V_REF
    ms = minimize_scalar(lambda v: slope_ss(v, 2.0), bounds=(-38, -31), method="bounded")
    assert abs(ms.x - V_REF) < 0.01 and abs(ms.fun + DG_IV) < 1e-3, (ms.x, ms.fun)
    # SHUNT and SHUNT_ADAPT are monotonic over the window
    for g_sh, g_m in [(4.0, 0.0), (4.0, 2.0)]:
        assert np.all(np.diff(i_ss(V_GRID, g_sh, g_m)) > 0)
    # hump table along the ramp
    for d, wmax, wmin in [(0.05, -37.828, -31.899), (0.10, -37.270, -32.224),
                          (0.1656, -36.416, -32.780), (0.20, -35.844, -33.199)]:
        a, b = hump(2.0 + d)
        assert abs(a - wmax) < 0.01 and abs(b - wmin) < 0.01, (d, a, b)
    # pinned extremes at -62 / -21 mV
    for g_sh, g_m, lo, hi in [(2, 0, -24.7, 49.6), (4, 0, -79.9, 76.5), (4, 2, -118.0, 173.8)]:
        assert abs(net(-62, g_sh, g_m) - lo) < 0.1 and abs(net(-21, g_sh, g_m) - hi) < 0.1
    # whole video stays inside the fixed y range
    for d, g in [(0, 0), (DG_BT, 0), (DG_IV, 0), (DG_END, 0), (DG_END, GM_END)]:
        y = yplot(net(V_GRID, 2 + d, g))
        assert y.min() >= Y_LO and y.max() <= Y_HI
    # readouts
    assert round(rin_drop(DG_BT)) == 8 and round(rin_drop(DG_IV)) == 11
    assert round(rin_drop(DG_END)) == 52
    assert f"{DG_BT:.2f}" == "0.17" and f"{DG_IV:.2f}" == "0.24"
    assert not is_class2(DG_BT - 0.001, 0) and is_class2(DG_BT, 0) and is_class2(DG_END, GM_END)
    assert band_edges(DG_IV, 0) is None and band_edges(DG_END, GM_END) is None
    # sign-text regions stay empty of curve in every state
    for d, g in [(0, 0), (0.1, 0), (DG_BT, 0), (DG_IV, 0), (1.0, 0), (DG_END, 0),
                 (DG_END, 1.0), (DG_END, GM_END)]:
        sy = p2y(yplot(net(V_GRID, 2 + d, g)))
        assert not np.any((V_GRID < -36) & (sy > 0.9)), (d, g)
        assert not np.any((V_GRID > -34) & (sy < -2.3)), (d, g)
    print("ok")
