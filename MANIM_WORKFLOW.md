# ManimGL workflow

How scenes are written, previewed, checked, and rendered in this workspace.
Engine: **ManimGL 1.7.2** (`from manimlib import *`). Never Manim Community Edition.

Run everything from the project root. `custom_config.yml` is read from the
current working directory, so running from a topic folder silently drops the
3b1b look.

## Layout

```
<area>/<topic>/main.py           scene classes + pure helper functions
<area>/<topic>/WORKBENCH.md      queue of beats to try (iteration-workbench skill)
<area>/<topic>/SOURCES.local.md  absolute paths to external context (gitignored)
<area>/<topic>/context_files/    optional stable reference notes (tracked)
templates/topic/                 copy this to start a topic; also the smoke test
common.py                        txt(), tex(), FONT -- `from common import *`
custom_config.yml                black bg, CMU Serif, saturation 1.5, autoreload
frames/                          snapshot PNGs (gitignored)
videos/                          rendered movies, flat, named by scene (gitignored)
```

One movie = one topic, and topics in an area are independent. If several
slides share the same deck, objects, or helpers, make them one topic with one
scene class per slide. Conventions shared across movies go in code
(`common.py`), not in notes. Keep to two levels
(area/topic); the skills assume it.

`main.py` puts its pure functions (the math the scene draws) at module level
and checks them in `if __name__ == "__main__":` asserts.

### Starting a topic

```bash
cp -R templates/topic <area>/<topic>
mv <area>/<topic>/SOURCES.example.md <area>/<topic>/SOURCES.local.md
```

Then fill in `SOURCES.local.md`, rename the scene class, and replace the
example workbench initiative. Scene class names must not repeat across topics,
because `videos/` is flat. Prefixing with the slide number (`S03FiringRate`)
keeps them sorted and unique.

### External context

The slide deck and other sources stay in their own directories and remain the
source of truth. This repo holds only:

- **paths**, in each topic's `SOURCES.local.md`. It's gitignored (`*.local.md`),
  one per topic, and holds no copied content.
- **translations**: the Manim decisions a source leads to. Decisions still in
  flux go in `WORKBENCH.md`; stable reference notes (color mappings, slide
  specs, sizes) go in the topic's optional `context_files/`, which is
  tracked in git. Cite sources by their labels in `SOURCES.local.md`, never by
  absolute path. Delete `context_files/` from a new topic if you don't need it.

Finished renders go one way: copy from `videos/` into the deck's assets
folder (listed in `SOURCES.local.md`) under a stable name.

## Interactive loop: Manim Notebook in Cursor

The Manim Notebook extension turns `##` comments into cells. It is not Jupyter:
it drives a live `manimgl` process in the integrated terminal and replays cells
into it with `checkpoint_paste()`.

1. Open `main.py`. The integrated terminal must have `.venv` active
   (`.vscode/settings.json` does this; `which manimgl` should point into `.venv`).
2. Put the cursor on a line inside `construct` and press `cmd+' cmd+s`
   (**Start scene at cursor**). manimgl runs up to that line, opens the preview
   window, and drops into IPython with the scene live. **A black window is
   normal** if the cursor was above the first `self.play`/`self.add`: nothing
   has been added yet. The window is a separate app; `cmd+tab` if it hides
   behind Cursor.
3. Edit a cell, then `cmd+' cmd+e` (**Preview Manim Cell**) replays just that
   cell from its checkpoint. `cmd+' cmd+r` previews the current selection.
4. `cmd+' cmd+c` clears the window; `cmd+' cmd+w` exits the scene.

Each cell's leading `##` comment is its checkpoint key. **Keep it stable while
iterating** -- renaming it discards the checkpoint and the next preview replays
from further back. Rename only once the beat is settled.

Autoreload is on (extension setting + `embed.autoreload`), so edits to
`common.py` and other imported modules take effect without restarting.

In the preview window: `d` + mouse rotates in 3D, `z` + scroll zooms, `r`
resets the camera, `q` quits. In IPython: `play(...)`, `add(...)`, `frame`,
`touch()`.

## Headless check (what Claude uses)

No window, one process per batch of frames:

```bash
.venv/bin/python <area>/<topic>/main.py                         # asserts on pure functions
.venv/bin/python .claude/skills/manimgl/core/assets/snapshot.py <area>/<topic>/main.py <Scene> --list
.venv/bin/python .claude/skills/manimgl/core/assets/snapshot.py <area>/<topic>/main.py <Scene> 3 7 12
```

`--list` numbers every `self.play` / `self.wait`; the indexed form writes
`frames/<Scene>_<K>.png` (480p; add `--hd` for 1080p). Read the PNGs and look
for: text over text, anything touching the frame edge (14.2 x 8 units),
leftovers from an earlier beat, labels unreadable at 480p, a `Tex` rendered as
prose.

## Render ladder

```bash
.venv/bin/manimgl <area>/<topic>/main.py <Scene> -w -l    # 480p, judge timing
.venv/bin/manimgl <area>/<topic>/main.py <Scene> -w --hd  # 1080p final
.venv/bin/manimgl <area>/<topic>/main.py <Scene> -w --uhd # 4K final
```

`-n 8` starts at animation 8. Do not render `--hd`/`--uhd` while composition or
timing is still moving. Output lands in `videos/<Scene>.mp4`; files from
different topics with the same scene name overwrite each other, so give scene
classes distinct names.

## Known footguns in this setup

- `Dot(color=YELLOW)` renders **white** in 1.7.2: `Dot` defaults
  `fill_color=WHITE`, which wins over `color`. Use `Dot(fill_color=YELLOW)`.
- Multi-string `Tex("r", "=", "x")` braces each piece, so `=` loses its relation
  spacing. Use one string (plus `isolate=` / `t2c` for coloring) when spacing matters.
- `directories.mirror_module_path` crashes in 1.7.2 unless an absolute
  `removed_mirror_prefix` is set, and breaks `snapshot.py`. Leave it off.
- `ipython<9` is pinned: manimlib 1.7.2 calls `shell.magic()` to enable
  autoreload, which IPython 9 removed, so every Manim Notebook session (which
  passes `--autoreload`) would crash on start. Don't lift the pin.
- The `pkg_resources is deprecated` warning on every run is harmless;
  `setuptools<81` is pinned in `pyproject.toml` to keep it importable.

## When something outside the scene breaks

```bash
.venv/bin/python .claude/skills/manimgl/core/assets/doctor.py --font "CMU Serif"
```

Do not pass `--write-config`: it would overwrite `custom_config.yml` with a
minimal one. More troubleshooting: `.claude/skills/manimgl/core/references/cli-config.md`.
