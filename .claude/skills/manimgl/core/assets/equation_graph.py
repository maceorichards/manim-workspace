"""ManimGL example — equations plus a coordinate system. REQUIRES LaTeX.

Tex, TexText and Brace shell out to a TeX distribution. If this fails with a LaTeX
error while assets/smoke_test.py renders fine, install texlive or MiKTeX rather
than debugging the scene.

    manimgl equation_graph.py EquationGraph
    manimgl equation_graph.py EquationGraph -w -l

Demonstrates the three things worth copying: isolate= for addressable equation
parts, i2gp for placing objects in data coordinates, and a ValueTracker driving
several dependent mobjects at once.
"""

from manimlib import *


class EquationGraph(Scene):
    def construct(self):
        # isolate= makes substrings individually addressable and gives
        # TransformMatchingTex stable keys to match on.
        start = Tex(R"f(x) = x^2", isolate=["f(x)", "x^2"], font_size=60)
        end = Tex(R"f'(x) = 2x", isolate=["f'(x)", "2x"], font_size=60)
        for eq in (start, end):
            eq.to_edge(UP)

        self.play(Write(start))
        self.wait(0.5)

        axes = Axes(
            x_range=(0, 3, 1),
            y_range=(0, 9, 2),
            width=7,
            height=4.5,
            axis_config=dict(include_tip=True),
        )
        axes.to_edge(DOWN, buff=MED_LARGE_BUFF)
        axes.add_coordinate_labels(font_size=20)

        graph = axes.get_graph(lambda x: x**2, x_range=(0, 3), color=BLUE)
        graph_label = axes.get_graph_label(graph, Tex("x^2"))

        self.play(ShowCreation(axes), FadeIn(graph_label))
        self.play(ShowCreation(graph), run_time=2)

        # One tracker, three dependents. Animate the tracker, never the dependents.
        tracker = ValueTracker(0.4)

        dot = Dot(color=YELLOW)
        dot.add_updater(lambda m: m.move_to(axes.i2gp(tracker.get_value(), graph)))

        # always_redraw rebuilds each frame — correct here because the tangent
        # line's shape, not just its position, changes with x.
        # get_tangent_line takes no color kwarg and no **kwargs; set it after.
        tangent = always_redraw(
            lambda: axes.get_tangent_line(
                tracker.get_value(), graph, length=4
            ).set_color(RED)
        )

        slope = DecimalNumber(0, num_decimal_places=2, font_size=36, edge_to_fix=LEFT)
        slope_label = VGroup(Tex(R"f'(x) =", font_size=36), slope)
        slope_label.arrange(RIGHT, buff=SMALL_BUFF)
        slope_label.next_to(axes, UP, buff=SMALL_BUFF).to_edge(RIGHT, buff=MED_SMALL_BUFF)
        f_always(slope.set_value, lambda: 2 * tracker.get_value())

        self.play(FadeIn(dot), ShowCreation(tangent), FadeIn(slope_label))
        self.play(tracker.animate.set_value(2.6), run_time=4, rate_func=linear)
        self.play(tracker.animate.set_value(1.0), run_time=2, rate_func=linear)

        # Matching keys let the equation morph part by part instead of cross-fading.
        self.play(TransformMatchingTex(start, end, key_map={"x^2": "2x"}))
        self.play(Indicate(slope_label))
        self.wait()

        # Updaters outlive the animation that motivated them unless cleared.
        dot.clear_updaters()
        tangent.clear_updaters()
        slope.clear_updaters()
