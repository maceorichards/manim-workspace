"""Shared helpers for every scene file in this project. `from common import *`.

Adapted from .agents/skills/manimgl/core/assets/templates/common.py (MIT).
Installed editable via pyproject.toml, so it imports from any topic folder,
and manimgl's autoreload picks up edits without restarting a scene.

- Pango substitutes a missing font silently, so the font is named explicitly.
  CMU Serif (Computer Modern) matches LaTeX output, so Text and Tex agree.
- manimlib's `Tex` wraps content in `align*`, which needs amsmath. The
  packages are injected per call; harmless with MacTeX's default template.
- Renders land in <topic>/videos/ next to the scene file, not a flat root
  videos/. An explicit --video_dir still wins.
- `txt(..., color=X)` / `tex(..., color=X)` honor X. Plain Text/Tex in 1.7.2
  render white because their fill_color default wins over color.
- The scene's area folder is importable, so `import prescott2008` finds
  <area>/prescott2008.py without a sys.path line in the scene file.
- STYLE holds the house look. A gitignored style.local.yml next to this file
  overrides it for this machine only (the set-style-default skill writes it).
"""

import shutil as _shutil
import sys as _sys
from pathlib import Path as _Path

import yaml as _yaml
from manimlib import *
from manimlib.config import manim_config as _manim_config

ROOT = _Path(__file__).resolve().parent
STYLE_FILE = ROOT / "style.local.yml"

# Keep in step with custom_config.yml, which covers files that skip common.py.
DEFAULT_STYLE = {
    "background": "#000000",
    "font": "CMU Serif",
    "text_color": None,  # None: manimlib's default (white)
    "saturation": 1.5,
    "fps": 30,
    "tex_template": None,  # None: "default", or "empty_ctex" under MiKTeX
    "palette": {},  # name -> hex; each becomes an uppercase global, e.g. NA_COLOR
}

TEX_PREAMBLE = "\n".join([R"\usepackage{amsmath}", R"\usepackage{amssymb}"])


def _load_style():
    style = dict(DEFAULT_STYLE)
    if STYLE_FILE.exists():
        local = _yaml.safe_load(STYLE_FILE.read_text(encoding="utf-8")) or {}
        unknown = set(local) - set(DEFAULT_STYLE)
        if unknown:
            raise ValueError(f"{STYLE_FILE.name}: unknown keys {sorted(unknown)}")
        style.update(local)
    return style


def _apply_style(style):
    """Patch manim_config before any Scene or Text reads it.

    Scene.__init__ copies manim_config.camera / .file_writer, and Text reads
    manim_config.text, at creation time, so patching at import still applies
    to the CLI, Manim Notebook, and snapshot.py alike.
    """
    _manim_config.camera.background_color = style["background"]
    _manim_config.camera.fps = int(style["fps"])
    _manim_config.file_writer.saturation = float(style["saturation"])
    _manim_config.text.font = style["font"]
    template = style["tex_template"]
    if template is None and _uses_miktex():
        # MiKTeX's latex.exe rejects manimlib's -no-pdf flag; xelatex with an
        # empty preamble works, and tex() adds amsmath/amssymb itself.
        template = "empty_ctex"
    if template:
        _manim_config.tex.template = template


def _uses_miktex():
    latex = _shutil.which("latex") or _shutil.which("xelatex") or ""
    return _sys.platform == "win32" and "miktex" in latex.lower()


def _scene_file():
    """The scene file being run: manimgl's argument, or `python main.py`'s."""
    name = _manim_config.run.file_name
    if not name and _sys.argv and _sys.argv[0].endswith(".py"):
        name = _sys.argv[0]
    return _Path(name).resolve() if name else None


def _route_output_to_topic(scene_file):
    """Point manimgl's output directory at <scene file's folder>/videos.

    manimlib builds its config before importing the scene module, but every
    Scene copies manim_config.file_writer when it is created, so changing it
    here still takes effect (CLI, Manim Notebook, reloads). Left alone when
    --video_dir was passed (snapshot.py passes one).
    """
    fw = _manim_config.file_writer
    if _manim_config.run.file_name and fw.output_directory == _manim_config.directories.output:
        fw.output_directory = str(scene_file.parent / "videos")


def _add_area_to_path(scene_file):
    """Make <area>/*.py importable from <area>/<topic>/main.py."""
    area = scene_file.parent.parent
    if area != ROOT and ROOT in area.parents and str(area) not in _sys.path:
        _sys.path.insert(1, str(area))


STYLE = _load_style()
FONT = STYLE["font"]
PALETTE = {name.upper(): color for name, color in STYLE["palette"].items()}
globals().update(PALETTE)
_apply_style(STYLE)

_scene = _scene_file()
if _scene:
    _route_output_to_topic(_scene)
    _add_area_to_path(_scene)


def _text_color(kwargs):
    if "color" in kwargs:
        kwargs.setdefault("fill_color", kwargs["color"])
    elif STYLE["text_color"]:
        kwargs.setdefault("fill_color", STYLE["text_color"])
    return kwargs


def txt(s, **kwargs):
    """Label text, rendered by Pango — no LaTeX involved."""
    kwargs.setdefault("font", FONT)
    return Text(s, **_text_color(kwargs))


def tex(*strings, **kwargs):
    """Math, rendered by LaTeX with amsmath/amssymb available."""
    return Tex(*strings, additional_preamble=TEX_PREAMBLE, **_text_color(kwargs))
