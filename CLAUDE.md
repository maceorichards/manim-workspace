# ManimGL workspace

- Engine is **ManimGL 1.7.2** (`from manimlib import *`, `manimgl` CLI). Never Manim CE
  (`from manim import *`). Use the `manimgl` skill for scene code and the
  `iteration-workbench` skill for anything longer than one beat.
- Read `MANIM_WORKFLOW.md` before suggesting how to run, preview, or render anything.
- Always run Python through `.venv/bin/python` (or `.venv/bin/manimgl`) from the project
  root, so `custom_config.yml` is picked up.
- One movie = one topic: `<area>/<topic>/` with `main.py`, `WORKBENCH.md`, and a gitignored
  `SOURCES.local.md`. Start new topics by copying `templates/topic/` (rename the scene class
  and copy `SOURCES.example.md` to `SOURCES.local.md`). Current area: `neural-circuits-for-cognition/`.
- External context (slide deck specs, notes) stays in its own directory. Before working on a
  topic, read its `SOURCES.local.md` for the paths, then read those files. Don't copy their
  content into this repo. Record the Manim decisions they lead to in `WORKBENCH.md` (still
  changing) or the topic's optional `context_files/` (stable reference notes, tracked in git),
  citing sources by their label in `SOURCES.local.md`, never by absolute path. Movies in an
  area are independent; conventions shared between them go in code (`common.py`), not notes.
- Directories named in any `SOURCES.local.md` are **read-only**: read them, never write,
  move, copy into, or delete there. Enforced by `.claude/settings.local.json` (Edit/Write
  deny rules) and the Bash hook `.claude/hooks/readonly_guard.py`.
- Start scene files with `from common import *` and use `txt()` / `tex()` from `common.py`.
- Verify with the headless path only (asserts → `snapshot.py --list` → `snapshot.py <indices>`,
  then read the PNGs). Scripts live in `.claude/skills/manimgl/core/assets/`.
- Output is per topic: renders go to `<area>/<topic>/videos/` (routed by `common.py`), snapshots
  to `<area>/<topic>/frames/` (`snapshot.py` default). Don't pass `--video_dir` / `--out` to put
  them elsewhere. Both are generated and gitignored; don't commit them.
- Environment is managed by uv (`pyproject.toml`); add dependencies with `uv add`.
