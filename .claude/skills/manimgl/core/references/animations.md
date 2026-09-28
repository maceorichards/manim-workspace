# Animations

Everything passed to `self.play()` must be an `Animation`. Passing a bare mobject
is an error. Frequency notes reflect counts across `_2025`/`_2026` in `3b1b/videos`.

## Base parameters

Every animation accepts these, inherited from `Animation`:

```python
Animation(mobject, run_time=1.0, time_span=None, lag_ratio=0.0,
          rate_func=smooth, remover=False, final_alpha_value=1.0,
          suspend_mobject_updating=False)
```

- `run_time` — seconds.
- `lag_ratio` — stagger between submobjects. `0` fires them together, `1` fully
  sequentially, fractions overlap.
- `rate_func` — the easing curve.
- `time_span=(start, end)` — run the animation only during that slice of the play
  call, letting animations of different lengths overlap inside one `self.play`.

## Appearing and disappearing

```python
Write(vmobject, run_time=-1, lag_ratio=-1)      # -1 = auto from size
ShowCreation(mobject, lag_ratio=1.0)            # NOT `Create` — that is CE
Uncreate(mobject)
DrawBorderThenFill(vmobject, run_time=2.0, stroke_width=2.0)
FadeIn(mobject, shift=..., scale=...)
FadeOut(mobject, shift=..., scale=...)
FadeInFromPoint(mobject, point)
FadeOutToPoint(mobject, point)
VFadeIn(mobject) / VFadeOut(mobject)
GrowFromCenter(mobject) / GrowFromPoint(mobject, point) / GrowFromEdge(mobject, edge)
GrowArrow(arrow)
ShowIncreasingSubsets(group)
AddTextWordByWord(string_mobject, time_per_word=0.2)
```

`FadeIn`/`FadeOut` dominate real usage, followed by `Write` and `ShowCreation`.
The `shift=` argument gives a fade some direction — `FadeIn(eq, shift=UP)` reads
much better than a bare fade.

Use `Write` for text and equations, `ShowCreation` for shapes and graphs, and
`GrowArrow` for arrows (it grows from tail to tip rather than tracing an outline).

## Changing one thing into another

```python
Transform(mobject, target_mobject)            # mobject becomes target, keeps identity
ReplacementTransform(mobject, target)         # target replaces mobject in the scene
TransformFromCopy(mobject, target)            # leaves the original in place
FadeTransform(mobject, target)                # cross-fade rather than morph
FadeTransformPieces(mobject, target)
TransformMatchingShapes(source, target)
TransformMatchingStrings(source, target, matched_keys=[], key_map={})
TransformMatchingTex(...)                     # subclass of TransformMatchingStrings
Restore(mobject)                              # back to the last save_state()
MoveToTarget(mobject)                         # after mobject.generate_target()
CyclicReplace(*mobjects) / Swap(*mobjects)
ApplyMatrix(matrix, mobject)
ApplyFunction(function, mobject)
ApplyComplexFunction(function, mobject)
ApplyPointwiseFunction(function, mobject)
```

**`Transform` vs `ReplacementTransform`:** after `Transform(a, b)` the scene still
holds `a` (now looking like `b`), so later references must use `a`. After
`ReplacementTransform(a, b)` the scene holds `b`. Mixing them up produces mobjects
that seem to vanish or refuse to update.

`TransformFromCopy` is heavily used — it is how you derive a new expression from an
existing one while keeping the source visible.

**`ReplacementTransform` leaves its target in the scene.** Collapsing several
mobjects into one by giving each its own copy of the target strands those copies:

```python
landing = VGroup(*[target.copy() for _ in sources])
self.play(*[ReplacementTransform(s, c) for s, c in zip(sources, landing)])
self.remove(landing, *landing)   # without this the copies stay
self.add(target)
```

Skipping the `remove` is invisible at first — the copies sit exactly on top of the
real mobject. It only surfaces later, when the real one gets scaled or moved and
the strays stay behind at full size, on top of whatever comes next.

**Morphing equations:** `TransformMatchingTex` matches by LaTeX substring and is
the common choice; `TransformMatchingShapes` matches by glyph geometry and is the
fallback when the strings share no structure. For reliable matching, build both
sides with the same `isolate=[...]` keys, then use `key_map={"a": "b"}` to link
parts whose text changed.

## Emphasis

```python
Indicate(mobject, scale_factor=1.2, color=YELLOW)
CircleIndicate(mobject, scale_factor=1.2)
FlashAround(mobject, time_width=1.0, color=YELLOW, buff=SMALL_BUFF)
FlashUnder(mobject)
Flash(point, color=YELLOW, line_length=0.2, num_lines=12, flash_radius=0.3)
FocusOn(focus_point, opacity=0.2, color=GREY)
ShowPassingFlash(mobject, time_width=0.1)
VShowPassingFlash(vmobject, time_width=0.3)
ShowCreationThenDestruction(vmobject)
ShowCreationThenFadeOut(mobject)
ShowPassingFlashAround(mobject)
ApplyWave(mobject)
WiggleOutThenIn(mobject)
TurnInsideOut(mobject)
```

`FlashAround` is the workhorse for "look here" without disturbing layout.

## Motion and rotation

```python
Rotate(mobject, angle=PI, axis=OUT, run_time=1, about_edge=ORIGIN)
Rotating(mobject, angle=TAU, axis=OUT, run_time=5.0, rate_func=linear)
MoveAlongPath(mobject, path)
Homotopy(homotopy, mobject)
ComplexHomotopy(complex_homotopy, mobject)
PhaseFlow(function, mobject)
MaintainPositionRelativeTo(mobject, tracked_mobject)
```

`Rotate` eases and turns by `PI` once; `Rotating` is linear and turns by `TAU` over
5 seconds — use it for continuous spin, not for a deliberate quarter-turn.

## Combining

```python
AnimationGroup(*animations, run_time=-1, lag_ratio=0.0)
Succession(*animations, lag_ratio=1.0)
LaggedStart(*animations, lag_ratio=DEFAULT_LAGGED_START_LAG_RATIO)
LaggedStartMap(anim_func, group, run_time=2.0, lag_ratio=...)
UpdateFromFunc(mobject, update_function)
UpdateFromAlphaFunc(mobject, update_function)
```

`self.play(a, b, c)` already runs animations concurrently — reach for
`AnimationGroup` only when you need a group as a single unit inside a larger
composition, or a shared `lag_ratio`.

`LaggedStartMap(FadeIn, group)` is the idiom for revealing a list item by item, and
is much shorter than building the animations yourself:

```python
self.play(LaggedStartMap(FadeIn, bullet_points, lag_ratio=0.3))
```

## The `.animate` syntax

Any chainable mobject method can be animated by inserting `.animate`:

```python
self.play(square.animate.shift(RIGHT).set_color(BLUE))
self.play(group.animate.arrange(DOWN, buff=LARGE_BUFF))
self.play(tracker.animate.set_value(5), run_time=3)
```

`.animate` interpolates between the before and after states. That is not always the
same as performing the motion — `.animate.rotate(PI)` interpolates start to end
positions and can pass through the centre instead of arcing. Use the `Rotate`
animation when the path matters.

## Rate functions

```
linear  smooth  rush_into  rush_from  slow_into  double_smooth
there_and_back  there_and_back_with_pause  running_start  overshoot
not_quite_there  wiggle  lingering  exponential_decay  squish_rate_func
```

`smooth` is the default and is right most of the time. Use `linear` for continuous
motion that should not decelerate (rotation, scrolling, tracker sweeps) —
easing a value sweep makes the underlying relationship look wrong.

`squish_rate_func(func, a, b)` compresses an animation into the `[a, b]` slice of
its run time, an alternative to `time_span` for staggering inside one call.
