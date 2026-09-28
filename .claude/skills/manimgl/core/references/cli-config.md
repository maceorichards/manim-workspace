# CLI and configuration

## Command

```
manimgl <file>.py <SceneName> [flags]
```

Omit the scene name and manimgl prompts with the scenes it found in the file.

| Flag | Long form | Effect |
|---|---|---|
| `-w` | `--write_file` | Render to a movie file. Without it, preview only. |
| `-o` | `--open` | Open the file when done (implies writing). |
| `-s` | `--skip_animations` | Jump to the last frame. Fast way to check final layout. |
| `-l` | `--low_quality` | 854×480. Use for every iteration. |
| `-m` | `--medium_quality` | 1280×720 |
| | `--hd` | 1920×1080 |
| | `--uhd` | 3840×2160 |
| `-n` | `--start_at_animation_number` | Start at animation N. `-n 3,6` also sets an end. |
| `-f` | `--full_screen` | Fullscreen preview window. |
| `-t` | `--transparent` | Render with an alpha channel. |
| `-i` | `--gif` | Save as gif. |
| `-g` | `--save_pngs` | Save every frame as png. |
| `-p` | `--presenter_mode` | Pause at each `wait` until spacebar. |
| `-r` | `--resolution` | e.g. `-r 1920x1080` |
| | `--fps` | Frame rate. |
| | `--config_file` | Point at a specific config yaml. |

The default loop: iterate with no flags at all (interactive window), then `-w -l`
once timing needs checking, then `--hd` at the end. Rendering at `--uhd` while
still composing wastes minutes per attempt.

`-n` is the one flag people forget. When beat 8 of 12 is wrong, `-n 8` skips
straight there instead of replaying the first seven.

## Interactive window

Rendering without `-w` opens a live window with keyboard controls, defined in
`default_config.yml` under `key_bindings`:

```
f  pan            d  pan in 3D        z  z-grab
r  reset          q  quit             s  select
g  grab           h  horizontal grab  v  vertical grab
t  resize         c  color            i  information
```

`self.embed()` inside `construct` drops into an IPython shell at that moment with
the scene live — mobjects can be inspected, modified, and re-played without
restarting. This is the core of the 3b1b workflow and much of the reason ManimGL
exists; set `embed: {autoreload: True}` to have edited modules reload in place.

`InteractiveScene` extends this with mouse editing: ctrl-drag to select, `g` to
move a selection, command-c to copy mobject ids, command-z to restore.

## custom_config.yml

Drop a `custom_config.yml` in the working directory to set defaults permanently.
Configs in subdirectories override parent directories. Only the keys you set are
overridden; everything else falls back to `manimlib/default_config.yml`.

```yaml
camera:
  resolution: (1920, 1080)
  background_color: "#333333"
  fps: 30
text:
  font: "Consolas"
  alignment: "LEFT"
tex:
  template: "default"
file_writer:
  ffmpeg_bin: "ffmpeg"
  video_codec: "libx264"
  pixel_format: "yuv420p"
  saturation: 1.0
  gamma: 1.0
directories:
  base: ""
  subdirs:
    output: "videos"      # note: nested under `subdirs`, not `directories`
embed:
  autoreload: False
```

Other useful sections: `window` (position, monitor, fullscreen), `scene`
(`show_animation_progress`, `default_wait_time`), `vmobject`
(`default_stroke_width: 4.0`, `default_stroke_color: "#DDDDDD"`), `sizes`
(`frame_height: 8.0` and the buff constants), `colors` (redefine any named colour),
`resolution_options`, `log_level`.

### If ffmpeg is not on PATH

`file_writer.ffmpeg_bin` takes a full path, which avoids a system-wide install:

```yaml
file_writer:
  ffmpeg_bin: "C:/tools/ffmpeg/bin/ffmpeg.exe"
```

`pip install imageio-ffmpeg` ships a bundled binary that can be pointed at this way.

## Reproducing the 3blue1brown look

3b1b's production config differs from the defaults in a few deliberate ways:

```yaml
camera:
  resolution: (3840, 2160)
  background_color: "#000000"     # default is the lighter #333333
  fps: 30
text:
  font: "CMU Serif"               # default is Consolas
  alignment: "CENTER"
file_writer:
  saturation: 1.5                 # default 1.0 — the punchy colours
embed:
  autoreload: True
```

`CMU Serif` is the Computer Modern family, which matches LaTeX output — that
consistency between `Text` and `Tex` is a large part of the visual signature. The
font must be installed on the system; without it Pango silently substitutes.

Note that 3b1b's own config also sets
`universal_import_line: "from manim_imports_ext import *"`, which pulls in that
repo's private `custom/` package. Do not copy that line — for standalone work it
must stay `from manimlib import *`.

## Snapshot a frame at a chosen beat

`-s` saves the final frame instead of a movie, **and needs `-w` to write it** —
`-s` alone just skips to the end in the preview window. Combine it with the
two-value form of `-n` to stop early:

```bash
manimgl file.py Scene -s -w -l -n 0,7    # state before animation 7 -> videos/Scene_0_7.png
manimgl file.py Scene -s -w -l           # final frame               -> videos/Scene.png
```

The index counts `self.play()` and `self.wait()` calls from 0, in execution
order (`Scene.num_plays`). With `-n 0,K` every animation is skipped — end states
are applied instantly — and `construct()` is cut off right before animation K, so
a frame costs a few seconds regardless of scene length. `--file_name` and
`--video_dir` override the output name and folder.
[assets/snapshot.py](../assets/snapshot.py) wraps this for a list of indices.

## Output location

Files land under `directories.subdirs.output` (default `videos`), relative to
`directories.base`. The key is nested one level deeper than it looks — setting
`directories.output` silently does nothing and renders still land in `videos/`.
With `mirror_module_path: True`, the output path mirrors the source file's
directory structure, which is how a repo with many scene files keeps renders
organised.

## Requirements

- Python 3.7+
- FFmpeg — required for `-w`; preview alone does not need it
- OpenGL — required always; a headless machine with no GL context cannot render
- LaTeX (texlive / MiKTeX) — required only for `Tex`, `TexText`, `Brace`

Check all of the above in one go, before or after installing:

```bash
python assets/doctor.py                 # report: python, manimlib, ffmpeg, LaTeX, font, config
python assets/doctor.py --write-config  # also write ./custom_config.yml with the fixes below
```

It catches the traps in this section mechanically — MiKTeX's `-no-pdf` clash,
a non-ASCII config, an `ffmpeg_bin` path left over from a previous Python install.

Install with `pip install manimgl`, or from a clone with `pip install -e .`.
The PyPI package name differs from the repository name; `pip install manim`
installs the Community Edition instead, which is a different library.

### setuptools 81+: `No module named 'pkg_resources'`

`manimlib/__init__.py` starts with `import pkg_resources` to read its own
version. setuptools removed `pkg_resources` in release 81, and a fresh Python
install pulls the newest setuptools, so `import manimlib` fails before anything
else runs. Pin it:

```bash
pip install "setuptools<81"
```

Observed with manimgl 1.7.2 and setuptools 84.

### `manimgl` command not found

pip installs the `manimgl` script into the interpreter's `Scripts` directory,
which a per-user Python on Windows often leaves off PATH. `python -m manimlib`
takes the same arguments and needs no PATH change.

### Windows Smart App Control blocks a wheel's DLL

`ImportError: DLL load failed while importing _odepack` on `import manimlib`
(Korean Windows gives the reason as an application control policy block) means
Smart App Control refused one of scipy's compiled extensions. The Python code is
fine; the policy rejects that particular binary. Another build of the same
package usually passes — `pip install --force-reinstall scipy==1.16.2` worked
where 1.18.1 was blocked. Turning Smart App Control off is the other option,
and a system-wide one.

### Python 3.13: install audioop-lts

manimgl imports `pydub`, which imports `audioop` — removed from the standard
library in Python 3.13 by PEP 594. Without a backport, `manimgl` fails at import
with `ModuleNotFoundError: No module named 'audioop'` before any scene runs.

```bash
pip install audioop-lts
```

Verified against manimgl 1.7.2 on Python 3.13. A `pkg_resources is deprecated`
warning and a pydub `Couldn't find ffmpeg or avconv` warning both appear on
startup and are harmless — pydub probes PATH independently of the `ffmpeg_bin`
setting that manimgl actually writes with.

### Windows + MiKTeX: every `Tex()` fails

manimlib invokes the compiler with `-no-pdf`, which is an **xelatex-only** flag.
MiKTeX's `latex.exe` is pdfTeX and rejects it, so every `Tex`, `TexText` and
`Brace` fails — while `Text` keeps working, which makes it look like a broken
LaTeX install rather than a flag mismatch.

Fix by selecting a template whose compiler is xelatex:

```yaml
tex:
  template: "empty_ctex"
```

Despite the name, `empty_ctex` does not load ctex — it is xelatex with an empty
preamble, and that is what makes it usable, since the CJK font machinery real
ctex wants is usually not configured.

**An empty preamble then makes every `Tex()` fail with `Environment align*
undefined`.** `Tex` wraps its content in `align*` unconditionally
(`tex_mobject.py`, `tex_environment = "align*"`), and `align*` comes from
amsmath. Supply it per call, or wrap `Tex` once per scene file:

```python
TEX_PREAMBLE = "\n".join([R"\usepackage{amsmath}", R"\usepackage{amssymb}"])

def tex(s, **kwargs):
    return Tex(s, additional_preamble=TEX_PREAMBLE, **kwargs)
```

The other xelatex templates are not drop-in replacements: `ctex` and `basic_ctex`
load ctex, and `american_typewriter` sets a macOS-only font.

TeX Live and TinyTeX are unaffected; this is specific to MiKTeX's `latex.exe`.

### custom_config.yml must be ASCII

manimlib opens the config without specifying an encoding, so it decodes with the
system locale codec. On Korean Windows that is cp949, and a single non-ASCII byte
— a Korean comment, a curly quote — crashes manimgl at startup before any scene
runs. Keep the config file's comments ASCII-only.

### Headless Linux, without root

Rendering on a remote box hits three separate walls. All three have user-level
answers; none needs `sudo`. Verified end to end on Ubuntu 24.04.

**1. `manimpango` publishes no Linux wheels** — pip always builds it from source
and needs cairo/pango headers. Chasing missing `.pc` files one at a time does not
converge. Install it as a prebuilt package instead:

```bash
micromamba install -p ./env -c conda-forge manimpango
pip install manimgl "setuptools<81"     # manimpango already satisfied
```

conda-forge also supplies `ffmpeg` here, so the `ffmpeg_bin` workaround is
unnecessary. `setuptools<81` is required because manimlib imports `pkg_resources`.

**2. No display** — `import manimlib` itself fails without one, because pyglet
opens a display at import time. An EGL context alone is not enough:

```bash
xvfb-run -a -s "-screen 0 1920x1080x24" manimgl scene.py SceneName -w --hd
```

Under Xvfb the renderer is Mesa llvmpipe (software), not the GPU. For 2D scenes on
a many-core machine that is fine. `moderngl.create_standalone_context(backend="egl")`
does reach the real GPU, but manimlib calls `create_standalone_context()` with no
backend argument, so using it would mean patching manimlib.

**3. LaTeX** — conda's `texlive-core` ships a broken `tlmgr` and no `dvisvgm`,
which manimlib needs. Use TinyTeX, which installs into `~/.TinyTeX`:

```bash
wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh
export PATH="$HOME/.TinyTeX/bin/x86_64-linux:$PATH"
tlmgr install dvisvgm
```

manimlib's default preamble pulls in packages a minimal TeX Live lacks. Rather
than guessing names, let the error name the file and look up its provider:

```bash
need=ragged2e.sty
tlmgr install "$(tlmgr search --global --file "/$need" | grep -E '^[A-Za-z0-9._-]+:$' | head -1 | tr -d ':')"
```

The same trick handles font-metric failures (`Metric (TFM) file not found`) by
searching for `/<fontname>.tfm`. In practice the run needs `doublestroke`,
`ragged2e`, and `wasy` on top of a fresh TinyTeX.

**Fonts are not portable.** Pango silently substitutes a missing font instead of
erroring, so a scene that looks right on Windows can render in the wrong typeface
on Linux with no warning. Select per platform:

```python
KR_FONT = "Malgun Gothic" if sys.platform == "win32" else "Noto Sans CJK KR"
```
