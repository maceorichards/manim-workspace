# Scene patterns

How to structure an explainer scene, as opposed to which API to call. Every
pattern here was taken from a rendered, multi-minute ManimGL scene; the symptom
listed under each one is what happened before the pattern was applied.

## One method per beat, `construct()` as the table of contents

```python
class VisionTransformer(Scene):
    def construct(self):
        self.opening()
        self.split_into_patches()
        self.embed_tokens()
        self.self_attention()

    def split_into_patches(self):
        ...
        self.patches = patches        # state the next beat needs

    def embed_tokens(self):
        tokens = self.patches.copy()  # picks up where the last beat stopped
```

State crosses beats only as `self.<name>` set at the end of the producing
method. `construct()` then reads as the outline and reordering a beat is one
line. `snapshot.py --list` runs the scene once with animations skipped and
numbers `play`/`wait` calls as they execute, so a shared helper such as
`set_title()` is counted every time it is called.

Symptom without it: a 600-line `construct()` where a local variable from minute
one is still being referenced in minute four.

## Helpers at the top, never bare `Tex`/`Text`

```python
FONT = "Malgun Gothic" if sys.platform == "win32" else "Noto Sans CJK KR"
TEX_PREAMBLE = "\n".join([R"\usepackage{amsmath}", R"\usepackage{amssymb}"])

def txt(s, **kw):  return Text(s, font=FONT, **kw)
def tex(s, **kw):  return Tex(s, additional_preamble=TEX_PREAMBLE, **kw)
```

Font because Pango substitutes a missing font silently. Preamble because the
`empty_ctex` template needed on MiKTeX has no amsmath, and `Tex` wraps everything
in `align*`. Two helpers make both decisions once per file instead of once per
label. See [cli-config.md](cli-config.md) for why each exists.

## Numbers on screen come from computation

```python
def spectrum(components):
    t = np.arange(N_SAMPLES) * DURATION / N_SAMPLES
    signal = sum(a * np.sin(TAU * f * t) for f, a, _ in components)
    mags = np.abs(np.fft.rfft(signal)) * 2 / N_SAMPLES
    return np.fft.rfftfreq(N_SAMPLES, d=DURATION / N_SAMPLES), mags

freqs, mags = spectrum(COMPONENTS)
bars = VGroup(*[Line(axes.c2p(f, 0), axes.c2p(f, m)) for f, m in zip(freqs, mags)])
```

The spectrum is a real FFT, the attention matrix is a real softmax over patch
distances. Hardcoded bar heights drift from the formula on screen the first
time someone edits either. Choosing inputs that make the output clean (integer
frequencies over a one-second window, so every component lands on a bin) is
allowed; faking the output is not.

Put an `if __name__ == "__main__":` block with a few `assert`s on the pure
functions. It runs without manimgl and catches a broken formula before a
render does.

## `ReplacementTransform` leaves the target in the scene

```python
landing = VGroup(*[sum_graph.copy() for _ in rows])
self.play(*[ReplacementTransform(r, c) for r, c in zip(rows, landing)])
self.remove(landing, *landing)
self.add(sum_graph)
```

When N mobjects transform into copies of one target, N copies are now in the
scene. Remove them and add the canonical object, or a later `.animate.scale()`
on `sum_graph` leaves N full-size ghosts sitting where it was.

The same applies to mobjects animated to opacity 0: `self.remove(pos)` after
the fade, or they keep costing draw time and reappear on `set_opacity(1)`.

## Explicit `x_range` step for `get_graph`

```python
PLOT_STEP = 0.002
axes.get_graph(mixture, x_range=(0, DURATION, PLOT_STEP))
```

The default sampling is chosen for smooth textbook curves. A 9 Hz component over
a one-second axis renders as a jagged polyline with it. Set the step once as a
constant and pass it to every graph on that axis so they stay comparable.

## Emphasis vocabulary

| Intent | Call |
|---|---|
| "look here" for a moment | `Indicate(mob, scale_factor=1.15)` |
| frame a question or result | `FlashAround(mob, time_width=1.5, run_time=2)` |
| dim everything else | `others.animate.set_opacity(0.2)` alongside the `Indicate` |
| track one element across beats | `set_color(RED_C)` it once, never recolor it |

Color coding is the cheapest explanation available: give each frequency its own
color in beat one, draw its spectrum bar in the same color in beat four, and the
correspondence needs no caption.

## Section titles via one `Transform`

```python
def set_title(self, text):
    new = txt(text, font_size=36).to_edge(UP, buff=0.35)
    self.play(Transform(self.title, new))
```

`self.title` is created in the opening beat and thereafter only transformed, so
there is exactly one title mobject for the whole scene. Creating a new title per
beat and forgetting a `FadeOut` is the most common leftover found in snapshots.

## Discrete palette over interpolated color

```python
PALETTE = [BLUE_E, BLUE_D, TEAL_D, TEAL_C, GREEN_C, YELLOW_D, YELLOW_B]
color = PALETTE[int(t * (len(PALETTE) - 1))]
```

`interpolate_color` has changed return type between manimlib versions. Picking
from a list of named colors renders identically everywhere and also reads
better on a dark background than a smooth gradient.
