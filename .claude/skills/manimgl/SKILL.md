---
name: manimgl
description: >-
  Writes math explainer animation code with ManimGL — 3Blue1Brown's own Manim
  (`from manimlib import *`, `manimgl` CLI). Use for animated equations, function
  graphs and coordinate systems, geometric constructions, ValueTracker-driven
  change, 3D surfaces and solids, and camera moves. Do NOT use for Manim
  Community Edition (`from manim import *`) — the two libraries share class names
  with different meanings.
argument-hint: 'Fourier transform of a mixed waveform | eigenvectors staying on their span | a rotating 3D surface'
---

# ManimGL

ManimGL is 3Blue1Brown's rendering engine. It is **not** Manim Community
Edition. Both are called "Manim", both define a class named `Tex`, and the two
mean opposite things.

Detect the engine from the project:

- `from manimlib import *` / `manimgl` CLI / `custom_config.yml` → **ManimGL, this skill**
- `from manim import *` / `manim -ql` CLI / `manim.cfg` → **Manim CE, stop**

## Do not confuse with Manim CE

Verified against manimlib 1.7.2. The `Tex` row is the dangerous one: the name
exists in both engines, so the wrong choice raises no error — it silently
renders text as math or math as text.

| | ManimGL (this skill) | Manim CE (different tool) |
|---|---|---|
| import | `from manimlib import *` | `from manim import *` |
| CLI | `manimgl file.py Scene -w -l` | `manim -ql file.py Scene` |
| **math mode** | **`Tex("x^2")`** | `MathTex("x^2")` |
| **text mode (LaTeX)** | **`TexText("hello")`** | `Tex("hello")` |
| draw a shape | `ShowCreation(mob)` | `Create(mob)` |
| camera | `self.frame` | `self.camera.frame` |
| fix to screen | `mob.fix_in_frame()` | `self.add_fixed_in_frame_mobjects(mob)` |
| default background | `#333333` | `#000000` |

**These CE names do not exist in manimlib** — using them is an immediate
`NameError`: `Create`, `MathTex`, `Unwrite`, `AddTextLetterByLetter`, `Angle`,
`RightAngle`, `Star`, `Axes3D`, `Dot3D`, `DoubleArrow`, `SpinInFromNothing`,
`Wait`.

Substitutes: `Star` → `RegularPolygon(5)`; `Dot3D` → `TrueDot`;
`DoubleArrow` → `Arrow(...)` + `.add_tip(at_start=True)`;
`SpinInFromNothing` → `GrowFromCenter` + `Rotate`;
`Wait` → there is no wait *animation*; use `self.wait()` or `lag_ratio`.

## Minimal scene

```python
from manimlib import *


class Demo(Scene):
    def construct(self):
        title = Text("Pythagoras", font_size=48)
        eq = Tex(R"a^2 + b^2 = c^2", font_size=60)
        eq.next_to(title, DOWN, buff=LARGE_BUFF)

        self.play(Write(title))
        self.play(FadeIn(eq, shift=UP))
        self.wait()
```

## Workflow

This project iterates in VS Code or Cursor with the Manim Notebook extension,
**not** the `manimgl -se <line>` CLI loop. Read `MANIM_WORKFLOW.md` at the
project root before suggesting how to run or re-run anything. Commands go
through `just` or `uv run` from the project root, never `.venv/bin/`, which
doesn't exist on Windows.

1. Write the scene outline in prose first — one thing proved per scene.
2. Iterate in the editor with `##` cell markers; each cell's leading comment is
   its checkpoint. Keep the comment stable while iterating.
3. Look at the frames before anyone else does:
   `just list <area>/<topic> Scene` numbers every `self.play`/`self.wait`;
   `just snap <area>/<topic> Scene 4 9 14` writes `<topic>/frames/Scene_004.png`.
4. Once composition is settled, `just render <area>/<topic> Scene` for a
   low-quality file to judge timing.
5. Only after timing is final, render `hd` or `uhd`.

What to look for in a snapshot: text crossing text, anything touching the frame
edge (the frame is 14.2 × 8 units), leftovers from an earlier beat, labels too
small to read at 480p, a `Tex` that rendered as prose.

## On-screen text

The animation carries the argument. **If a narrator could speak the line, it
does not belong on screen.**

Keep what the picture cannot state on its own: labels and names, counts and
units, formulas, and emphasis (color coding, `Indicate`, `FlashAround`). Cut
prose that restates the motion. Prefer noun phrases to sentences, including for
section titles.

## Reference files

Open only what the current task needs. A scene longer than two or three beats
should start from `core/references/patterns.md`.

| Open when | File |
|---|---|
| Tex/Text, geometry, VGroup, positioning, colors | `core/references/api-core.md` |
| Axes, NumberPlane, graphs, ValueTracker, updaters | `core/references/api-graphs.md` |
| Which animation class, timing, `lag_ratio`, rate functions | `core/references/animations.md` |
| CLI flags, `custom_config.yml`, the 3b1b look | `core/references/cli-config.md` |
| **Structuring a multi-beat scene** | `core/references/patterns.md` |
| 3D solids, surfaces, parametric surfaces, lighting | `extra/rules/3d.md` |
| Camera: `reorient`, Euler angles, `fix_in_frame` | `extra/rules/camera.md` |
| `self.frame` methods, zoom, reset | `extra/rules/frame.md` |
| Coloring math with `tex_to_color_map` | `extra/rules/t2c.md` |
| `Transform`, `ReplacementTransform`, `TransformMatchingTex` | `extra/rules/transform-animations.md` |
| `LaggedStart`, `Succession`, `AnimationGroup` | `extra/rules/animation-groups.md` |
| Fill, stroke, opacity, backstroke, gloss, shadow | `extra/rules/styling.md` |
| `self.embed()`, IPython debugging | `extra/rules/embedding.md` |

Runnable scripts (stdlib only):

- `core/assets/doctor.py` — environment check: manimlib, ffmpeg, LaTeX/MiKTeX,
  dvisvgm, fonts, `custom_config.yml`. `--write-config` writes the fixes. Run
  this first when a render fails for a reason that is not the scene code.
- `core/assets/snapshot.py` — PNG of the scene at chosen animation indices.
- `core/assets/smoke_test.py` — geometry and `Text` only, no LaTeX required.

`extra/examples/` holds 192 scene classes across 75 files; `extra/templates/`
has four starting points; `extra/walkthroughs/` annotates eight of the examples.
**These are CC BY-NC-SA 4.0** — model fresh code on them, do not paste them into
work you publish. See `NOTICE.md`.

## Footguns

**`reorient` takes theta first, then phi.**
`frame.reorient(theta_degrees, phi_degrees, gamma_degrees, center, height)`.
Several manimgl docs online reverse these; pass by keyword when unsure.

**`Tex` takes multiple strings.** `Tex("a", "+", "b")` auto-isolates each string
so submobjects line up with what you passed. A *single-string* `Tex` has an empty
`isolate`, so its submobjects are individual glyphs — `Tex(R"a^2+b^2")[0]` is one
symbol, not `a^2`. Use multi-string form, or `isolate=[...]` with
`get_part_by_tex`.

**LaTeX is required for `Tex`, `TexText`, and `Brace`.** `Text` and `Code` use
Pango and need none. Without LaTeX, build the scene from `Text` plus geometry and
say so rather than letting the render fail.

**Updaters must be removed.** `clear_updaters()` when the effect is over, or the
object drifts through later beats.

**`always_redraw(func)` rebuilds every frame.** Right for shape that depends on a
tracker, wrong for something that merely moves — use `add_updater` or `f_always`.

**`ReplacementTransform` leaves its target in the scene.** Transforming N
mobjects into copies of one target leaves N copies; remove them and add the
canonical object.

**`self.play()` needs an animation, not a mobject.** Use
`self.play(square.animate.shift(RIGHT))`.

**`color=` renders white on `Dot`, `Text`, and `Tex`.** Their `fill_color=WHITE`
default wins over `color`. Use `Dot(fill_color=X)`, `.set_color(X)`, or `t2c`.
This project's `txt()` / `tex()` (from `common.py`) map `color=` to
`fill_color=` for you.

**Pango CMU Serif draws θ as ϑ and `~` as a raised tilde.** Put those in
`tex()`. In `Tex`, `--` is two hyphens (use `\text{\textendash}`), and a bare
`:` gets relation spacing (use `{:}`).

**Multi-string `Tex` loses relation spacing.** `Tex("r", "=", "x")` braces each
piece, so `=` is spaced like an ordinary symbol. Use one string with `isolate=`
or `t2c` when spacing matters.

**CLI traps.** `--fps 60` arrives as a string and crashes the render. Set
`default_camera_config = dict(fps=60)` on the scene, or `fps` in
`style.local.yml`. `-s` without `-w` tries to open a window when run headless.
A `run_time` that isn't a whole number of frames adds a frame.

## Attribution

`3b1b/manim` (the engine) is MIT. `3b1b/videos` (per-video scene code) is
CC BY-NC-SA 4.0 and depends on `manim_imports_ext.py` — do not paste from it.
Write fresh code modeled on the API.
