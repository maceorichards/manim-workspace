# Manim workspace

An agent-first template for making math and science explainer movies with
**ManimGL** (3Blue1Brown's Manim, **not** Community Edition). You describe the
beats; a coding agent (Claude Code, Codex, Cursor or Gemini CLI; see
[AGENT_SUPPORT.md](AGENT_SUPPORT.md)) writes the scene, checks frames headlessly, and works through a checklist with
you. You preview live in Cursor or VS Code with the Manim Notebook extension.

Runs on macOS, Linux, and Windows. Day-to-day usage: [MANIM_WORKFLOW.md](MANIM_WORKFLOW.md).

## What's inside

| Path | What it is |
|---|---|
| `AGENTS.md` | rules every agent follows in this repo |
| `.agents/skills/` | `manimgl` (API + footguns), `iteration-workbench` (beat-by-beat loop), `set-style-default` |
| `.agents/hooks/readonly_guard.py` | keeps your source folders read-only for the agent |
| `scripts/agents.py` | generates your agent's own folder (`.claude/`, `.codex/`, …) from the above |
| `common.py` | `txt()`, `tex()`, house style, per-topic output, area imports |
| `templates/topic/` | starting point for a movie, and the install smoke test |
| `justfile`, `scripts/`, `tools/` | `just new`, `check`, `snap`, `render`, `style`, `agent`, `setup`, … |

## Setup

You need [git](https://git-scm.com) and a coding agent. Setup installs system
packages (uv, just, ffmpeg, LaTeX, the CMU Serif font), runs `uv sync`, installs
the git hook, generates your agent's adapter (its skills, permissions and the
read-only guard; see [AGENT_SUPPORT.md](AGENT_SUPPORT.md)), runs the doctor, and
snapshots the template scene as a smoke test. It's safe to re-run.

### With your agent

Open this folder in your agent and say: **set up this workspace by following README.md**.

### Setup checklist (for the agent)

1. Your agent name is one of `claude`, `codex`, `cursor`, `gemini`.
2. See what's missing, without installing anything:
   `sh scripts/setup.sh --check` (macOS/Linux) or
   `powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -Check` (Windows).
3. Show the user that list and ask once whether to install it. Steps marked as asking for a
   password (`sudo apt-get …`, the MacTeX cask) are theirs to run: give them the command.
4. On a yes, run `sh scripts/setup.sh --yes --agent <name>` (Windows:
   `… scripts/setup.ps1 -Yes -Agent <name>`). On a no (uv must be installed either way), run
   just the rest: `uv sync`, then `uv run python scripts/post_setup.py --agent <name>`.
5. If the output lists generated files that git still tracks, show the user the
   `git rm --cached …` command it printed and run it only if they agree. Don't commit.
6. Relay every `next:` line from the agent-adapter step (trust or reload steps).
7. Read the `summary` rows. For each FAIL, follow the doctor's output above it. Then open
   `setup_check.png` and confirm the firing-rate curve, its equation and labels rendered.

### By hand

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
Agents on Windows often run commands and hooks through Git Bash, so keep Git installed.

Add `--agent <name>` (`-Agent <name>` on Windows) to set up your agent too; without
it, setup tries to detect the agent. After the first run, `just setup [agent]` re-runs
it, `just agent <name>` adds or regenerates one agent's adapter, and `just doctor`
checks the environment alone.

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

Point `SOURCES.local.md` at your specs or notes, then `just agent-sync`. Then
ask your agent to use the `iteration-workbench` skill, describing what the viewer should see.
It queues beats, builds the ones you pick, and checks frames
(`just snap …`) before handing back. When the timing settles, `just render <topic> <Scene> hd`.

Your own style (light background, your own colors, another font) without touching
the template: ask your agent to use the `set-style-default` skill, or `just style --help`.

## Using this template

`main` holds only the template. Keep your own movies on a branch made from it
and merge `main` in for template updates. See [CONTRIBUTING.md](CONTRIBUTING.md).
Changes: [CHANGELOG.md](CHANGELOG.md).

The vendored skill material has its own licenses: `.agents/skills/manimgl/core/`
(and `tools/`, which came from it) is MIT, and `.agents/skills/manimgl/extra/` is
**CC BY-NC-SA 4.0**. See [NOTICE.md](.agents/skills/manimgl/NOTICE.md). The rest of the repo has no
license yet.
