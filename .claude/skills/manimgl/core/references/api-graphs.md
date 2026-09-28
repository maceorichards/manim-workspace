# Coordinate systems, graphs, and continuous change

## Axes and planes

```python
Axes(x_range=(-8, 8, 1), y_range=(-4, 4, 1), axis_config={}, x_axis_config={},
     y_axis_config={}, height=None, width=None, unit_size=1.0)

NumberPlane(x_range=(-8.0, 8.0, 1.0), y_range=(-4.0, 4.0, 1.0),
            background_line_style=dict(stroke_color=BLUE_D, stroke_width=2,
                                       stroke_opacity=1),
            faded_line_style=dict(stroke_width=1, stroke_opacity=0.25),
            faded_line_ratio=4)

ComplexPlane(...)        # NumberPlane subclass, adds n2p / p2n
ThreeDAxes(x_range=(-6,6,1), y_range=(-5,5,1), z_range=(-4,4,1))

NumberLine(x_range=(-8, 8, 1), unit_size=1.0, width=None, include_ticks=True,
           include_numbers=False, include_tip=False, big_tick_spacing=None,
           big_tick_numbers=[], numbers_to_exclude=None,
           decimal_number_config=dict(num_decimal_places=0, font_size=36))
```

Ranges are `(min, max, step)`. Pass `width=`/`height=` to force a pixel-independent
size, or `unit_size=` to fix how many scene units one data unit occupies — set one
or the other, not both.

### Converting between data and screen

This is the part that trips people up. Axes coordinates are **not** scene
coordinates; always convert.

```python
axes = Axes(x_range=(0, 10, 1), y_range=(0, 5, 1), width=10, height=5)
point = axes.c2p(3, 4)          # data (3, 4)  -> scene position
x, y  = axes.p2c(point)         # scene position -> data
origin = axes.get_origin()
```

`c2p`/`p2c` are aliases for `coords_to_point`/`point_to_coords`. Place every dot,
label, and line via `c2p` — hardcoding scene positions breaks the moment the range
or size changes.

### Graphing a function

```python
graph = axes.get_graph(lambda x: x**2, x_range=(0, 3), color=BLUE)
label = axes.get_graph_label(graph, Tex("x^2"))
point = axes.i2gp(1.5, graph)               # input -> graph point
```

`CoordinateSystem` also provides `get_parametric_curve`, `bind_graph_to_func`,
`get_v_line_to_graph`, `get_h_line_to_graph`, `get_tangent_line`,
`angle_of_tangent`, `slope_of_tangent`, `get_riemann_rectangles`,
`get_area_under_graph`, `get_scatterplot`, `add_coordinate_labels`,
`get_axis_labels`.

`get_riemann_rectangles` and `get_area_under_graph` are the ready-made calculus
visuals — do not rebuild them from `Rectangle`.

Not every helper forwards styling. `get_graph` passes `**kwargs` through, so
`axes.get_graph(f, color=BLUE)` works — but `get_tangent_line` does not:

```python
get_tangent_line(x, graph, length=5, line_func=Line)   # no color, no **kwargs
```

Passing `color=` to it raises `TypeError`. Style it after construction:

```python
axes.get_tangent_line(x, graph, length=4).set_color(RED)
```

Check the signature before assuming a helper accepts styling kwargs; several on
`CoordinateSystem` take a fixed argument list.

**Sampling is per-tick, not per-pixel.** A graph with high-frequency content
renders visibly angular at the default density. Pass an explicit step as the third
element of `x_range`:

```python
axes.get_graph(f, x_range=(0, 1, 0.002))   # dense enough for ~10 cycles
```

**Fractional ticks need decimal places.** `add_coordinate_labels` defaults to
`num_decimal_places=0`, so a `y_range` step of `0.5` labels 0.5 as `0` — the axis
reads wrong rather than merely ugly:

```python
Axes(
    y_range=(0, 1.2, 0.5),
    y_axis_config=dict(decimal_number_config=dict(num_decimal_places=1)),
)
```

### Standalone function mobjects

When no axes are needed, these draw directly in scene coordinates:

```python
FunctionGraph(function, x_range=(-8, 8, 0.25), color=YELLOW)
ParametricCurve(t_func, t_range=(0, 1, 0.1), discontinuities=[],
                use_smoothing=True)
ImplicitFunction(func, x_range=(-FRAME_X_RADIUS, FRAME_X_RADIUS),
                 y_range=(-FRAME_Y_RADIUS, FRAME_Y_RADIUS))
```

`ImplicitFunction` plots `func(x, y) == 0` — the way to draw a curve you cannot
solve for `y`.

Pass `discontinuities=[...]` to `ParametricCurve` for functions like `tan`;
without it the curve draws a vertical streak across the asymptote.

## ValueTracker

A `ValueTracker` holds a number as a mobject, so `self.play` can interpolate it.
It is the backbone of every "slide the parameter and watch the picture change"
animation.

```python
ValueTracker(value=0)
ComplexValueTracker(value=0)
ExponentialValueTracker(value=0)     # interpolates multiplicatively
```

Methods: `get_value()`, `set_value(x)`, `increment_value(dx)`.

`ExponentialValueTracker` matters when a quantity spans orders of magnitude —
linear interpolation from 1 to 1000 spends most of its time looking large.

## Updaters

Four tools, and picking the wrong one is the usual cause of a sluggish preview.

```python
always_redraw(func, *args)        # rebuild the mobject from scratch each frame
mob.add_updater(lambda m, dt: ...)  # mutate in place each frame
always(method, *args)             # call mob.method(args) each frame
f_always(method, *arg_generators) # call mob.method(g()) each frame
always_rotate(mob, rate=20*DEG)
always_shift(mob, direction=RIGHT, rate=0.1)
```

Choose by what changes:

- The mobject's **shape or structure** depends on the tracker → `always_redraw`.
- The mobject only **moves, rotates, or recolours** → `add_updater` or `f_always`.
  These mutate the existing object instead of rebuilding it.

`f_always` is the tidy form for "call one setter with a computed value":

```python
number = DecimalNumber(0)
f_always(number.set_value, tracker.get_value)
```

That reads better than the equivalent lambda updater and is what 3b1b's code
actually uses — `f_always` appears roughly twice as often as `always_redraw` there.

### The two rules

**Add the mobject to the scene, or its updater never runs.** `self.add(mob)` (or
an animation that adds it) is what puts it on the update list.

**Clear updaters when the effect ends.** An orphaned updater keeps firing for the
rest of the scene and quietly drifts the object during later beats:

```python
dot.clear_updaters()
```

### Worked pattern

```python
tracker = ValueTracker(0.5)
axes = Axes(x_range=(0, 3, 1), y_range=(0, 9, 1), width=6, height=4)
graph = axes.get_graph(lambda x: x**2, color=BLUE)

dot = Dot(color=YELLOW)
dot.add_updater(lambda m: m.move_to(axes.i2gp(tracker.get_value(), graph)))

readout = DecimalNumber(0, num_decimal_places=2)
readout.add_updater(lambda m: m.next_to(dot, UR, buff=SMALL_BUFF))
f_always(readout.set_value, lambda: tracker.get_value() ** 2)

self.add(axes, graph, dot, readout)
self.play(tracker.animate.set_value(2.5), run_time=3)
dot.clear_updaters()
readout.clear_updaters()
```

Note `self.play(tracker.animate.set_value(...))` — the tracker is animated, and
everything attached to it follows. Never animate the dependent mobjects directly.
