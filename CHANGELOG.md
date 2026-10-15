# Changelog

Template versions of `main`. Personal branches can tell which one they've merged
from `git describe --tags main`.

## Unreleased

- Cross-platform (macOS, Linux, Windows): `uv run` / `just` everywhere instead of
  `.venv/bin/`; `scripts/setup.sh` and `scripts/setup.ps1`; MiKTeX auto-detection in `common.py`.
- `justfile`: `new`, `check`, `list`, `snap`, `render`, `check-all`, `lint`, `fmt`,
  `agent`, `agent-sync`, `style`, `doctor`, `setup`.
- `just new` (`scripts/new_topic.py`) replaces the manual copy steps; new areas get
  `<area>/AGENTS.md` from `templates/area/`.
- Read-only guard for every `SOURCES.local.md` folder; `readonly_guard.py` understands
  Windows paths.
- `common.py`: `txt()`/`tex()` honor `color=`; area folders are importable
  (`<area>/<module>.py`); house style in `DEFAULT_STYLE`, with per-machine overrides
  in `style.local.yml` (`set-style-default` skill, `just style`).
- Agent docs: `AGENTS.md` is canonical; `CONTRIBUTING.md` for the template/personal-branch
  workflow.
- Ruff (correctness rules) + pre-commit hook; CI on macOS, Linux, and Windows.
- More footguns documented: Text/Tex `color=`, CMU Serif θ and `~`, Tex `--` and `:`,
  `--fps` crash, `-s` without `-w`, fractional-frame run_times.
- No slide-deck assumptions: `SOURCES.example.md` is one flat `- <label>: /abs/path`
  list (the deck section and assets-folder line are gone), and `just new` warns on any
  position-style name (`part2_clip3`, `video1`, `s03_vid1`), not just deck slots.
- **Breaking:** style presets `light-slides` / `navy-slides` are now `light` / `navy`
  (`style.local.yml` stores values, so existing overrides are unaffected).
- Agent-agnostic: Claude Code, Codex CLI, Cursor and Gemini CLI are supported from one set
  of tracked sources (`AGENTS.md`, `.agents/skills/`, `.agents/hooks/`). `just setup [agent]`
  / `just agent <name>` (`scripts/agents.py`) generate each agent's gitignored folder:
  skills links, `CLAUDE.md` shims, allowlist, and the read-only guard (one hook for all four,
  reading `SOURCES.local.md` at call time, plus deny rules where the agent has them).
  `AGENT_SUPPORT.md` replaces `PORTING.md`. Setup can be run by the agent: README checklist,
  `setup.sh --check` / `--yes` / `--agent` (`setup.ps1 -Check` / `-Yes` / `-Agent`).
- **Breaking:** skills moved from `.claude/skills/` to `.agents/skills/`; `doctor.py` and
  `snapshot.py` to `tools/`; `just guard-sync` is now `just agent-sync`; worktrees go in
  `.worktrees/` instead of `.claude/worktrees/`; `CLAUDE.md` files are generated, not tracked,
  and the pre-commit hook rejects generated agent files.
- Migrating a personal branch: `git merge main`, then set up again with your agent (README)
  or `just setup <agent>`. It removes the old guard entries from
  `.claude/settings.local.json` and prints a `git rm --cached` command for any leftover tracked
  `<area>/CLAUDE.md`; run it, then commit. Move a worktree under `.claude/worktrees/` with
  `git worktree move .claude/worktrees/<name> .worktrees/<name>`.

## 0.1.0

- Initial workspace: ManimGL 1.7.2 via uv, `common.py`, topic template, `manimgl` and
  `iteration-workbench` skills, headless `snapshot.py`, per-topic output routing.
