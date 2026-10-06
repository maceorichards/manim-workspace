"""Shared helpers for every scene file in this project. `from common import *`.

Adapted from .claude/skills/manimgl/core/assets/templates/common.py (MIT).
Installed editable via pyproject.toml, so it imports from any topic folder,
and manimgl's autoreload picks up edits without restarting a scene.

- Pango substitutes a missing font silently, so the font is named explicitly.
  CMU Serif (Computer Modern) matches LaTeX output, so Text and Tex agree.
- manimlib's `Tex` wraps content in `align*`, which needs amsmath. The
  packages are injected per call; harmless with MacTeX's default template.
- Renders land in <topic>/videos/ next to the scene file, not a flat root
  videos/. An explicit --video_dir still wins.
"""

from pathlib import Path as _Path

from manimlib import *
from manimlib.config import manim_config as _manim_config

FONT = "CMU Serif"

TEX_PREAMBLE = "\n".join([R"\usepackage{amsmath}", R"\usepackage{amssymb}"])


def _route_output_to_topic():
    """Point manimgl's output directory at <scene file's folder>/videos.

    manimlib builds its config before importing the scene module, but every
    Scene copies manim_config.file_writer when it is created, so changing it
    here still takes effect (CLI, Manim Notebook, reloads). Left alone when
    --video_dir was passed (snapshot.py passes one).
    """
    scene_file = _manim_config.run.file_name
    fw = _manim_config.file_writer
    if scene_file and fw.output_directory == _manim_config.directories.output:
        fw.output_directory = str(_Path(scene_file).resolve().parent / "videos")


_route_output_to_topic()


def txt(s, **kwargs):
    """Label text, rendered by Pango — no LaTeX involved."""
    kwargs.setdefault("font", FONT)
    return Text(s, **kwargs)


def tex(*strings, **kwargs):
    """Math, rendered by LaTeX with amsmath/amssymb available."""
    return Tex(*strings, additional_preamble=TEX_PREAMBLE, **kwargs)
