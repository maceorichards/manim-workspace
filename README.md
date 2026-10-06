# Manim workspace

ManimGL (3Blue1Brown's Manim, **not** Community Edition) with the Manim Notebook
extension in Cursor. Day-to-day usage: [MANIM_WORKFLOW.md](MANIM_WORKFLOW.md).

## Setup on a new Mac

Requires Homebrew, uv, a TeX distribution (MacTeX), and Cursor.

```bash
brew install ffmpeg
brew install --cask font-computer-modern   # CMU Serif, matches LaTeX
uv sync                                    # .venv with manimgl 1.7.2, Python 3.12
.venv/bin/python .claude/skills/manimgl/core/assets/doctor.py --font "CMU Serif"
```

Manim Notebook is on the VS Code Marketplace but not Open VSX, so Cursor needs
the VSIX:

```bash
curl -L -o manim-notebook.vsix "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/Manim-Notebook/vsextensions/manim-notebook/1.0.1/vspackage"
cursor --install-extension manim-notebook.vsix
```

Updates are manual: repeat with the new version number from the
[releases page](https://github.com/Manim-Notebook/manim-notebook/releases).

## Check it works

```bash
.venv/bin/python templates/topic/main.py
.venv/bin/manimgl templates/topic/main.py FiringRateCurve -w -l
```

The render lands in `templates/topic/videos/`; delete it afterwards so it isn't
copied into new topics.

Then open that `main.py` in Cursor, put the cursor inside `construct`, and press
`cmd+' cmd+s`.
