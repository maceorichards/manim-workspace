"""ManimGL smoke test — no LaTeX required.

Uses only Text (Pango) and geometry, so it proves the manimgl install, the OpenGL
context, and ffmpeg without depending on a TeX distribution. If this renders and
assets/equation_graph.py does not, the missing piece is LaTeX.

    manimgl smoke_test.py SmokeTest        # interactive preview
    manimgl smoke_test.py SmokeTest -w -l  # write a low-quality mp4
    manimgl smoke_test.py SmokeTest -s     # last frame only
"""

from manimlib import *


class SmokeTest(Scene):
    def construct(self):
        title = Text("ManimGL smoke test", font_size=42)
        title.to_edge(UP)
        self.play(Write(title))

        # Geometry: constructed, arranged as a group, then revealed one by one.
        shapes = VGroup(
            Circle(radius=0.7, color=BLUE),
            Square(side_length=1.4, color=GREEN),
            Triangle(color=YELLOW).set_height(1.4),
        )
        shapes.arrange(RIGHT, buff=LARGE_BUFF)
        self.play(LaggedStartMap(ShowCreation, shapes, lag_ratio=0.4))

        # .animate turns any chainable mobject method into an animation.
        self.play(shapes.animate.shift(DOWN).set_opacity(0.6))
        self.play(FlashAround(shapes[1]))

        # A ValueTracker drives a live readout. f_always wires the setter to a
        # value getter, so the number follows the tracker without a lambda.
        tracker = ValueTracker(0)
        readout = DecimalNumber(0, num_decimal_places=2, edge_to_fix=LEFT)
        readout.next_to(shapes, DOWN, buff=LARGE_BUFF)
        f_always(readout.set_value, tracker.get_value)

        label = Text("tracker", font_size=24)
        label.next_to(readout, LEFT, buff=MED_SMALL_BUFF)

        self.play(FadeIn(readout), FadeIn(label))
        self.play(tracker.animate.set_value(9.99), run_time=2, rate_func=linear)

        # Updaters keep firing until cleared; leaving them on lets the mobject
        # drift during later beats.
        readout.clear_updaters()

        box = SurroundingRectangle(VGroup(shapes, readout), buff=MED_LARGE_BUFF)
        self.play(ShowCreation(box))
        self.wait()
        self.play(FadeOut(VGroup(title, shapes, readout, label, box)))
