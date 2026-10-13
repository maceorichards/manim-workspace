# Manim workspace

An agent-first template for making math and science explainer movies with
**ManimGL** (3Blue1Brown's Manim, **not** Community Edition). You describe the
beats; an agent (Claude Code, or Codex/Cursor, see [PORTING.md](PORTING.md))
writes the scene, checks frames headlessly, and works through a checklist with
you. You preview live in Cursor or VS Code with the Manim Notebook extension.

Runs on macOS, Linux, and Windows. Day-to-day usage: [MANIM_WORKFLOW.md](MANIM_WORKFLOW.md).

## What's inside

| Path | What it is |
|---|---|
| `AGENTS.md` (`CLAUDE.md` imports it) | rules every agent follows in this repo |
| `.claude/skills/` | `manimgl` (API + footguns), `iteration-workbench` (beat-by-beat loop), `set-style-default` |
| `common.py` | `txt()`, `tex()`, house style, per-topic output, area imports |
| `templates/topic/` | starting point for a movie, and the install smoke test |
| `justfile`, `scripts/` | `just new`, `check`, `snap`, `render`, `style`, `setup`, … |
| `.claude/hooks/readonly_guard.py` | keeps your source folders read-only for the agent |

## Setup

You need [git](https://git-scm.com), then run the setup script for your OS. It asks
before installing system packages (uv, just, ffmpeg, LaTeX, the CMU Serif font),
then runs `uv sync`, installs the git hook, runs the doctor, and snapshots the
template scene as a smoke test. It's safe to re-run.

**macOS** (needs [Homebrew](https://brew.sh)):
```bash
sh scripts/setup.sh
```
If you have no LaTeX, it tells you to `brew install --cask mactex-no-gui` (large).

**Linux** (Debian/Ubuntu via apt; other distros get the package list):
```bash
sh scripts/setup.sh
```

**Windows** (needs winget; installs Git, uv, just, ffmpeg, MiKTeX, CMU Serif):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
```
Claude Code on Windows runs its hooks through Git Bash, so keep Git installed.

After the first run, `just setup` re-runs it, and `just doctor` checks the environment alone.

### Editor

- **VS Code:** install the recommended extensions when prompted (Python, Manim Notebook).
- **Cursor:** Manim Notebook isn't on Open VSX, so install the VSIX:
  ```bash
  curl -L -o manim-notebook.vsix "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/Manim-Notebook/vsextensions/manim-notebook/1.0.1/vspackage"
  cursor --install-extension manim-notebook.vsix
  ```
  Updates are manual: repeat with the new version number from the
  [releases page](https://github.com/Manim-Notebook/manim-notebook/releases).

Then open `templates/topic/main.py`, put the cursor inside `construct`, and press
`cmd+' cmd+s` (`ctrl+' ctrl+s` on Linux/Windows). A preview window opens.

## First movie

```bash
just new my-course firing_rate_adaptation   # -> my-course/firing_rate_adaptation/
```

Point `SOURCES.local.md` at your specs or notes, then `just guard-sync`. Then
ask your agent to run `/iteration-workbench` with what the viewer should see.
It queues beats, builds the ones you pick, and checks frames
(`just snap …`) before handing back. When the timing settles, `just render <topic> <Scene> hd`.

Your own style (light background, your own colors, another font) without touching
the template: `/set-style-default` or `just style --help`.

## Using this template

`main` holds only the template. Keep your own movies on a branch made from it
and merge `main` in for template updates. See [CONTRIBUTING.md](CONTRIBUTING.md).
Changes: [CHANGELOG.md](CHANGELOG.md).

The vendored skill material has its own licenses: `.claude/skills/manimgl/core/`
is MIT, and `.claude/skills/manimgl/extra/` is **CC BY-NC-SA 4.0**. See
[NOTICE.md](.claude/skills/manimgl/NOTICE.md). The rest of the repo has no
license yet.
