# Core API

Signatures extracted from manimlib source via AST. Only `**kwargs`-level detail is
elided. Usage-frequency notes come from counting occurrences across the `_2025`
and `_2026` directories of `3b1b/videos` — a proxy for what the engine's author
actually reaches for.

## Text and math

`Tex` and `TexText` require a working LaTeX install. `Text` and `Code` do not —
they render through Pango.

```python
Tex(*tex_strings, font_size=48, alignment=R"\centering", template="",
    additional_preamble="", tex_to_color_map={}, t2c={}, isolate=[],
    use_labelled_svg=True)

TexText(...)   # same signature; renders in text mode instead of math mode

Text(text, font_size=48, height=None, justify=False, indent=0, alignment="",
     line_width=None, font="", slant=NORMAL, weight=NORMAL, gradient=None,
     t2c={}, t2f={}, t2g={}, t2s={}, t2w={}, lsh=None, disable_ligatures=True)

Code(code, font="Consolas", font_size=24, language="python", code_style="monokai")
```

`Tex` is by far the most used mobject in 3b1b's own code; `TexText` is roughly a
tenth as common. Reach for `Tex` and wrap prose in `\text{...}` rather than
switching classes mid-scene.

### Addressing parts of an equation

```python
eq = Tex(R"e^{i\pi} + 1 = 0", isolate=[R"e^{i\pi}", "1", "0"])
eq.set_color_by_tex(R"e^{i\pi}", YELLOW)
part = eq.get_part_by_tex("1")        # single VMobject
parts = eq.get_parts_by_tex("0")      # VGroup of all matches
```

Useful `Tex` methods: `get_part_by_tex(selector, index=0)`,
`get_parts_by_tex(selector)`, `set_color_by_tex(selector, color)`,
`set_color_by_tex_to_color_map(map)`, `get_tex()`,
`make_number_changeable(value, index=0, replace_all=False)`.

`make_number_changeable` swaps a literal number inside rendered LaTeX for a live
`DecimalNumber` — the clean way to animate a constant inside a formula without
re-rendering the whole expression.

Colour shorthand at construction: `Tex(R"x + y", t2c={"x": BLUE, "y": RED})`.
`Text` takes the same `t2c`, plus `t2f` (font), `t2s` (slant), `t2w` (weight),
`t2g` (gradient).

### CJK text

On-screen text defaults to English. Read this section only when the user has
asked for Korean, Japanese or Chinese. Both rules below were established by
rendering rather than by reasoning, and neither failure mode raises an error.

**Pick the font per platform.** Pango substitutes a missing font silently — no
error, just the wrong typeface:

```python
KR_FONT = "Malgun Gothic" if sys.platform == "win32" else "Noto Sans CJK KR"
Text("한글", font=KR_FONT)
```

**Do not animate it with `Write`.** `Write` is `DrawBorderThenFill`: it traces
each glyph's outline. A Hangul syllable is several independent contours (one per
jamo), so mid-animation the glyph is a pile of disconnected strokes. It looks
wrong for the whole animation, and on a long title several glyphs are partial at
once.

The font is not the lever — a Thin weight mangles exactly like a regular one.
The animation is:

| Animation | Result on Hangul |
|---|---|
| `Write` | in-progress glyphs are illegible strokes |
| `FadeIn(t, shift=0.3*UP)` | always a complete glyph, only opacity changes |
| `AddTextWordByWord(t)` | complete glyphs revealed by word — keeps progressive reveal |

`AddTextWordByWord` is the drop-in when the point of `Write` was the sense of text
appearing over time.

## Geometry

```python
Arc(start_angle=0, angle=TAU/4, radius=1.0, arc_center=ORIGIN)
ArcBetweenPoints(start, end, angle=TAU/4)
Circle(start_angle=0, stroke_color=RED)
Dot(point=ORIGIN, radius=DEFAULT_DOT_RADIUS, fill_color=DEFAULT_MOBJECT_COLOR)
SmallDot(point=ORIGIN)
Ellipse(width=2.0, height=1.0)
Annulus(inner_radius=1.0, outer_radius=2.0, fill_opacity=1.0)
AnnularSector(angle=TAU/4, start_angle=0.0, inner_radius=1.0, outer_radius=2.0)
Sector(angle=TAU/4, radius=1.0)

Line(start=LEFT, end=RIGHT, buff=0.0, path_arc=0.0)
DashedLine(start=LEFT, end=RIGHT, dash_length=DEFAULT_DASH_LENGTH)
TangentLine(vmob, alpha, length=2)
Arrow(start=LEFT, end=LEFT, buff=MED_SMALL_BUFF, thickness=3.0, path_arc=0)
StrokeArrow(start, end, stroke_width=5, buff=0.25)
Vector(direction=RIGHT, buff=0.0)
CurvedArrow(start_point, end_point)
CurvedDoubleArrow(start_point, end_point)
Elbow(width=0.2, angle=0)

Polygon(*vertices)
RegularPolygon(n=6)
Triangle()
Rectangle(width=..., height=...)
Square(side_length=...)
RoundedRectangle(corner_radius=...)
CubicBezier(a0, h0, h1, a1)
```

`Line` and `Arrow` accept a `Mobject` for `start`/`end`, not just a point — the
line then anchors to that mobject's centre and `buff` keeps it clear of the edge.

### Decorating an existing mobject

```python
SurroundingRectangle(mobject, buff=SMALL_BUFF, color=YELLOW)
BackgroundRectangle(mobject, fill_opacity=0.75, buff=0)
Cross(mobject, stroke_color=RED)
Underline(mobject, buff=SMALL_BUFF, stretch_factor=1.2)
Brace(mobject, direction=DOWN, buff=0.2)          # needs LaTeX
BraceLabel(obj, text, brace_direction=DOWN, label_scale=1.0)
LineBrace(line, direction=UP)
```

`Brace` methods: `get_text(*text)`, `get_tex(*tex)`, `put_at_tip(mob)`,
`get_tip()`, `get_direction()`.

## Grouping

`VGroup` is the workhorse — the single most frequent name in 3b1b's code. It holds
vectorized mobjects only. `Group` holds anything, including images and surfaces.

```python
group = VGroup(a, b, c)
group.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
group[0]            # indexable
group.add(d)
```

Animating a `VGroup` animates all members together — that is usually what you want
for a caption plus its underline, or an equation plus its brace.

## Positioning and transforms

These are `Mobject` methods, so they work on every visual object. They mutate and
return `self`, which makes them chainable — and makes them work with `.animate`.

```
move_to(point_or_mobject)      next_to(mob, direction, buff=...)
to_edge(direction, buff=...)   to_corner(direction)
shift(vector)                  center()
align_to(mob, direction)       surround(mob)
scale(factor)                  rotate(angle, axis=OUT, about_point=...)
stretch(factor, dim)           flip(axis=UP)
set_width(w)                   set_height(h)
match_width(mob)               match_height(mob)  match_x(mob)  match_y(mob)
set_color(c)                   set_opacity(o)     fade(darkness)
get_center()  get_top()  get_bottom()  get_left()  get_right()  get_corner(d)
save_state()  restore()        copy()  become(mob)
add_updater(fn)  remove_updater(fn)  clear_updaters()
```

`set_fill(color, opacity)` and `set_stroke(color, width, opacity)` exist on
`VMobject` for finer control than `set_color`.

`save_state()` paired with the `Restore` animation is the idiomatic way to return
a mobject to an earlier look — heavily used in 3b1b's code.

## Constants

Directions are unit vectors and compose by addition: `UP + RIGHT == UR`.

```
ORIGIN  UP  DOWN  LEFT  RIGHT  IN  OUT
UL  UR  DL  DR
X_AXIS  Y_AXIS  Z_AXIS
PI  TAU  DEG  DEGREES
FRAME_WIDTH  FRAME_HEIGHT  FRAME_X_RADIUS  FRAME_Y_RADIUS
SMALL_BUFF  MED_SMALL_BUFF  MED_LARGE_BUFF  LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFF  DEFAULT_MOBJECT_TO_EDGE_BUFF
```

`DEG` converts degrees to radians: `mob.rotate(30 * DEG)`.

The frame is `8.0` units tall by default, so `FRAME_Y_RADIUS` is `4.0`. Positions
are in these scene units, never pixels — a scene composed in units survives a
resolution change untouched.

### Colours

Each hue has five shades, `_A` (lightest) through `_E` (darkest):

```
BLUE_A..BLUE_E   TEAL_A..TEAL_E    GREEN_A..GREEN_E
YELLOW_A..YELLOW_E  GOLD_A..GOLD_E  RED_A..RED_E
MAROON_A..MAROON_E  PURPLE_A..PURPLE_E  GREY_A..GREY_E
WHITE  BLACK  PINK  LIGHT_PINK  ORANGE
GREY_BROWN  DARK_BROWN  LIGHT_BROWN
PURE_RED  PURE_GREEN  PURE_BLUE  GREEN_SCREEN
```

Unsuffixed aliases (`BLUE`, `RED`, `GREEN`, …) map to the `_C` shade. Any
hex string works too: `Circle(color="#4F8EF7")`.

## Numbers

```python
DecimalNumber(number=0, num_decimal_places=2, include_sign=False, unit=None,
              show_ellipsis=False, font_size=48, edge_to_fix=LEFT)
Integer(number=0, num_decimal_places=0)
```

Methods: `set_value(x)`, `get_value()`, `increment_value(dx)`.

`edge_to_fix=LEFT` keeps the left edge pinned as digits change width — without it
a counter visibly jitters. Set it to `RIGHT` for right-aligned readouts.
