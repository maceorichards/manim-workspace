"""Shared helpers for every scene file in this project. `from common import *`.

Two decisions made once instead of once per label:

- Pango substitutes a missing font silently, so the font is named explicitly
  and per platform. Change FONT if the on-screen language changes.
- manimlib's `Tex` wraps content in `align*`, which needs amsmath. The
  `empty_ctex` template (required on MiKTeX) has an empty preamble, so the
  packages are injected per call. Harmless on TeX Live.
"""

import sys

from manimlib import *

FONT = {
    "win32": "Segoe UI",
    "darwin": "Helvetica Neue",
}.get(sys.platform, "DejaVu Sans")

# For Korean labels swap in: "Malgun Gothic" / "Apple SD Gothic Neo" / "Noto Sans CJK KR".
# CJK text must be revealed with FadeIn, never Write (see the skill's footguns).

TEX_PREAMBLE = "\n".join([R"\usepackage{amsmath}", R"\usepackage{amssymb}"])


def txt(s, **kwargs):
    """Label text, rendered by Pango — no LaTeX involved."""
    return Text(s, font=FONT, **kwargs)


def tex(s, **kwargs):
    """Math, rendered by LaTeX with amsmath/amssymb available."""
    return Tex(s, additional_preamble=TEX_PREAMBLE, **kwargs)
