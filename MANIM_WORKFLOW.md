# ManimGL workflow

How scenes are written, previewed, checked, and rendered in this workspace.
Engine: **ManimGL 1.7.2** (`from manimlib import *`). Never Manim Community Edition.

Run everything from the project root, through `just` (`just --list`) or `uv run`.
`custom_config.yml` is read from the current working directory, so running from a
topic folder silently drops the 3b1b look. `just` recipes always run at the root.
`uv run` works the same on macOS, Linux, and Windows; every `just` recipe below is
a thin wrapper around a `uv run` command you can also type directly.

## Layout

```
<area>/<topic>/main.py           scene classes + pure helper functions
<area>/<topic>/WORKBENCH.md      queue of beats to try (iteration-workbench skill)
<area>/<topic>/SOURCES.local.md  absolute paths to external context (gitignored)
<area>/<topic>/context_files/    optional stable reference notes (tracked)
<area>/<topic>/videos/           renders, named by scene (gitignored)
<area>/<topic>/frames/           snapshot PNGs (gitignored)
<area>/<module>.py               optional model/palette shared by that area's topics
<area>/AGENTS.md                 agent notes for the area (read by every agent)
templates/topic/                 what `just new` copies; also the smoke test
templates/area/                  what a new area starts with
common.py                        txt(), tex(), FONT, STYLE -- `from common import *`
custom_config.yml                black bg, CMU Serif, saturation 1.5, autoreload
style.local.yml                  optional per-machine style override (gitignored)
.agents/skills/                  agent skills: manimgl, iteration-workbench, set-style-default
.agents/hooks/                   read-only guard hook, wired into each agent by `just agent`
tools/                           snapshot.py, doctor.py
scripts/                         new_topic, check_all, agents, set_style, setup
justfile                         the commands below
```

Output is per topic, with no flags needed: `common.py` points manimgl at the
scene file's `videos/` (CLI renders, `-s -w` stills, and Manim Notebook alike),
and `snapshot.py` writes to the scene file's `frames/`. Frames are disposable;
videos are deliverables. Don't pass `--video_dir` / `--out` to send them
elsewhere.

One movie = one topic, and topics in an area are independent. If several
clips share objects or helpers, make them one topic with one scene class per
clip. Keep to two levels (area/topic); the skills and scripts
assume it.

Sharing code:

- **Within an area:** put it in `<area>/<module>.py` (pure functions, constants,
  palette; its own `__main__` asserts). `from common import *` puts the area on
  `sys.path`, so a topic just writes `import <module>`. Don't name a module
  `common`, or one that shadows a library.
- **Across areas:** put it in `common.py`. Conventions shared between movies go
  in code, not in notes.

`main.py` puts its pure functions (the math the scene draws) at module level
and checks them in `if __name__ == "__main__":` asserts.

### Starting a topic

```bash
just new <area> <topic> [SceneClass]
```

This copies `templates/topic/` and renames the scene class (the default is the
topic in CamelCase). It turns `SOURCES.example.md` into `SOURCES.local.md`, and a
new area also gets `<area>/AGENTS.md`. Then fill in `SOURCES.local.md`, run
`just agent-sync`, and replace the firing-rate example and its workbench
initiative. Name topics and scene classes for their content. Each topic has its
own `videos/`, so scene names only need to be unique within the topic.

### External context

Sources (specs, notes, papers, figures) stay in their own directories and remain the
source of truth. This repo holds only:

- **paths**, in each topic's `SOURCES.local.md`. It's gitignored (`*.local.*`),
  one per topic, and holds no copied content.
- **translations**: the Manim decisions a source leads to. Decisions still in
  flux go in `WORKBENCH.md`; stable reference notes (color mappings,
  per-clip specs, sizes) go in the topic's optional `context_files/`, which is
  tracked in git. Cite sources by their labels in `SOURCES.local.md`, never by
  absolute path. Delete `context_files/` from a new topic if you don't need it.

Source directories are read-only for agents. Every enabled agent gets a hook
(`.agents/hooks/readonly_guard.py`) that reads every `SOURCES.local.md` on each
call and blocks shell commands that write there, so it is always current. Agents
with path rules also get deny rules for their file tools; those are written by
`just agent-sync` (also run by `just new` and `just setup`), so re-run it after
editing a `SOURCES.local.md`, then reload or restart your agent. What each agent
gets: `AGENT_SUPPORT.md`.

## Interactive loop: Manim Notebook in Cursor or VS Code

The Manim Notebook extension turns `##` comments into cells. It is not Jupyter:
it drives a live `manimgl` process in the integrated terminal and replays cells
into it with `checkpoint_paste()`.

Keybindings below use `mod`: `cmd` on macOS, `ctrl` on Linux and Windows.

1. Open `main.py`. The integrated terminal must have `.venv` active
   (`.vscode/settings.json` does this; `which manimgl` / `where manimgl` should
   point into `.venv`).
2. Put the cursor on a line inside `construct` and press `mod+' mod+s`
   (**Start scene at cursor**). manimgl runs up to that line, opens the preview
   window, and drops into IPython with the scene live. **A black window is
   normal** if the cursor was above the first `self.play`/`self.add`: nothing
   has been added yet. The window is a separate app; switch to it if it hides
   behind the editor.
3. Edit a cell, then `mod+' mod+e` (**Preview Manim Cell**) replays just that
   cell from its checkpoint. `mod+' mod+r` previews the current selection.
4. `mod+' mod+c` clears the window; `mod+' mod+w` exits the scene.

Each cell's leading `##` comment is its checkpoint key. **Keep it stable while
iterating**: renaming it discards the checkpoint, and the next preview replays
from further back. Rename only once the beat is settled.

Autoreload is on (extension setting + `embed.autoreload`), so edits to
`common.py` and other imported modules take effect without restarting.
Changes to `style.local.yml` need a scene restart (the camera reads its config
when the scene starts).

In the preview window: `d` + mouse rotates in 3D, `z` + scroll zooms, `r`
resets the camera, `q` quits. In IPython: `play(...)`, `add(...)`, `frame`,
`touch()`.

## Headless check (what agents use)

No window, one process per batch of frames:

```bash
just check <area>/<topic>                        # asserts on pure functions
just list  <area>/<topic> <Scene>                # number every self.play / self.wait
just snap  <area>/<topic> <Scene> 3 7 12         # PNGs after animations 3, 7, 12
just check-all                                   # every topic + area module (CI runs this)
```

`list` numbers every `self.play` / `self.wait`. `snap` writes
`<area>/<topic>/frames/<Scene>_<K>.png` at 480p; for 1080p call the script
directly with `--hd`: `uv run python tools/snapshot.py <file> <Scene> 3 --hd`. Read the PNGs and look for: text over text, anything
touching the frame edge (14.2 x 8 units), leftovers from an earlier beat, labels
unreadable at 480p, a `Tex` rendered as prose.

## Render ladder

```bash
just render <area>/<topic> <Scene>         # 480p, judge timing
just render <area>/<topic> <Scene> hd      # 1080p final
just render <area>/<topic> <Scene> uhd     # 4K final
```

For other flags, call manimgl directly: `uv run manimgl <file> <Scene> -w -l -n 8`
starts at animation 8. Do not render `hd`/`uhd` while composition or timing is
still moving. Output lands in `<area>/<topic>/videos/<Scene>.mp4`.

## Style

The house look (black background, CMU Serif, saturation 1.5, 30 fps) is
`DEFAULT_STYLE` in `common.py`, mirrored in `custom_config.yml`. To change it
on your machine only, use the `set-style-default` skill or `just style`
(`--preset light`, `--set background=#0B1020 palette.accent=#E07A5F`,
`--reset`). That writes the gitignored `style.local.yml`. Palette entries become
uppercase names in scene code (`ACCENT`). Change `DEFAULT_STYLE` only to change
the template for everyone.

## Known footguns in this setup

None of these raise an error. They only show up when you look at the frame.

- A scene file that doesn't `from common import *` skips the output routing,
  style, and area imports, so its renders land in a root `./videos/`.
- `Dot(color=YELLOW)` renders **white** in 1.7.2: `Dot` defaults
  `fill_color=WHITE`, which wins over `color`. Use `Dot(fill_color=YELLOW)`.
  Plain `Text(..., color=)` / `Tex(..., color=)` have the same problem;
  `txt()` / `tex()` from `common.py` fix it, and `.set_color()` and `t2c` work.
- Multi-string `Tex("r", "=", "x")` braces each piece, so `=` loses its relation
  spacing. Use one string (plus `isolate=` / `t2c` for coloring) when spacing matters.
- CMU Serif through Pango (`txt()`) draws θ as ϑ and `~` as a raised tilde;
  use `tex()` for those. In `tex()`, `--` renders as two hyphens (use
  `\text{\textendash}`), and a bare `:` gets relation spacing (use `{:}`).
- `--fps 60` on the CLI reaches the scene as a string and crashes the render.
  Set `fps` in `style.local.yml`, or `default_camera_config = dict(fps=60)` on
  the scene.
- Headless `-s` without `-w` tries to open a window and fails. Use
  `-s -w --file_name <x>_end` to save the last frame.
- A `self.play` whose `run_time` isn't a whole number of frames adds an extra
  frame. Round run_times to exact frames when total duration matters.
- `directories.mirror_module_path` crashes in 1.7.2 unless an absolute
  `removed_mirror_prefix` is set, and breaks `snapshot.py`. Leave it off.
- `ipython<9` is pinned: manimlib 1.7.2 calls `shell.magic()` to enable
  autoreload, which IPython 9 removed, so every Manim Notebook session (which
  passes `--autoreload`) would crash on start. Headless runs never open the
  shell, so they won't catch a regression here. Don't lift the pin.
- The `pkg_resources is deprecated` warning on every run is harmless;
  `setuptools<81` is pinned in `pyproject.toml` to keep it importable.
- Windows + MiKTeX: `latex.exe` rejects manimlib's `-no-pdf` flag. `common.py`
  switches to the `empty_ctex` (xelatex) template when it detects MiKTeX, and
  `tex()` adds amsmath/amssymb. Plain `Tex` gets no packages under that template.

## When something outside the scene breaks

```bash
just doctor
```

Do not pass `--write-config` to `doctor.py`: it would overwrite `custom_config.yml` with a
minimal one. More troubleshooting: `.agents/skills/manimgl/core/references/cli-config.md`.
