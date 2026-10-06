"""Topic template: a neuron's firing-rate curve.

`just new <area> <topic>` copies this folder to start a movie and renames
the scene class to describe its content. It doubles as the
workspace smoke test. Exercises Text (Pango), Tex (LaTeX), Axes and a
ValueTracker so a broken install shows up here before it shows up in real work.

Beats:
  1. Title
  2. Sigmoid rate equation
  3. Rate curve on axes, with a dot tracking input current
"""

import math

from common import *

R_MAX = 100.0  # Hz
I_HALF = 5.0   # input current at half-max rate (nA)
GAIN = 1.2     # 1/nA


def firing_rate(i, r_max=R_MAX, i_half=I_HALF, gain=GAIN):
    """Sigmoid rate model r(I) = r_max / (1 + exp(-gain * (I - I_half)))."""
    return r_max / (1.0 + math.exp(-gain * (i - i_half)))


class FiringRateCurve(Scene):
    def construct(self):
        ## Title
        title = txt("Firing-rate curve", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))

        ## Rate equation
        eq = tex(R"r(I) = \frac{r_{\max}}{1 + e^{-g\,(I - I_{1/2})}}", font_size=40)
        eq.next_to(title, DOWN, buff=MED_LARGE_BUFF)
        self.play(FadeIn(eq, shift=UP))
        self.wait()

        ## Curve on axes
        axes = Axes(
            x_range=(0, 10, 2),
            y_range=(0, 100, 25),
            width=8,
            height=3.6,
        )
        axes.add_coordinate_labels(font_size=20)
        axes.to_edge(DOWN, buff=1.0)
        x_label = txt("input current (nA)", font_size=24)
        x_label.next_to(axes.x_axis, DOWN, buff=0.4)
        y_label = txt("rate (Hz)", font_size=24)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        curve = axes.get_graph(firing_rate, color=BLUE)

        current = ValueTracker(0)
        dot = Dot(fill_color=YELLOW)  # Dot ignores color=; fill_color defaults to WHITE
        dot.add_updater(lambda d: d.move_to(axes.i2gp(current.get_value(), curve)))

        self.play(ShowCreation(axes), FadeIn(x_label), FadeIn(y_label))
        self.play(ShowCreation(curve))
        self.add(dot)
        self.play(current.animate.set_value(10), run_time=3)
        dot.clear_updaters()
        self.wait()


if __name__ == "__main__":
    assert abs(firing_rate(I_HALF) - R_MAX / 2) < 1e-9
    assert firing_rate(0) < 1.0
    assert firing_rate(10) > 0.99 * R_MAX
    assert all(firing_rate(i) < firing_rate(i + 0.5) for i in range(10))
    print("ok")
