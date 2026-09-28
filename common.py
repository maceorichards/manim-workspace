"""Shared helpers for every scene file in this project. `from common import *`.

Adapted from .claude/skills/manimgl/core/assets/templates/common.py (MIT).
Installed editable via pyproject.toml, so it imports from any topic folder,
and manimgl's autoreload picks up edits without restarting a scene.

- Pango substitutes a missing font silently, so the font is named explicitly.
  CMU Serif (Computer Modern) matches LaTeX output, so Text and Tex agree.
- manimlib's `Tex` wraps content in `align*`, which needs amsmath. The
  packages are injected per call; harmless with MacTeX's default template.
"""

from manimlib import *

FONT = "CMU Serif"

TEX_PREAMBLE = "\n".join([R"\usepackage{amsmath}", R"\usepackage{amssymb}"])


def txt(s, **kwargs):
    """Label text, rendered by Pango — no LaTeX involved."""
    kwargs.setdefault("font", FONT)
    return Text(s, **kwargs)


def tex(*strings, **kwargs):
    """Math, rendered by LaTeX with amsmath/amssymb available."""
    return Tex(*strings, additional_preamble=TEX_PREAMBLE, **kwargs)
