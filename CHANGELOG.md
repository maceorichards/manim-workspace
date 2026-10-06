# Changelog

Template versions of `main`. Personal branches can tell which one they've merged
from `git describe --tags main`.

## Unreleased

- Cross-platform (macOS, Linux, Windows): `uv run` / `just` everywhere instead of
  `.venv/bin/`; `scripts/setup.sh` and `scripts/setup.ps1`; MiKTeX auto-detection in `common.py`.
- `justfile`: `new`, `check`, `list`, `snap`, `render`, `check-all`, `lint`, `fmt`,
  `guard-sync`, `style`, `doctor`, `setup`.
- `just new` (`scripts/new_topic.py`) replaces the manual copy steps; new areas get
  `<area>/AGENTS.md` from `templates/area/`.
- Read-only guard generated from every `SOURCES.local.md` (`just guard-sync`);
  `readonly_guard.py` understands Windows paths.
- `common.py`: `txt()`/`tex()` honor `color=`; area folders are importable
  (`<area>/<module>.py`); house style in `DEFAULT_STYLE`, with per-machine overrides
  in `style.local.yml` (`set-style-default` skill, `just style`).
- Agent docs: `AGENTS.md` is canonical, `CLAUDE.md` imports it; `PORTING.md` for
  other agents; `CONTRIBUTING.md` for the template/personal-branch workflow.
- Ruff (correctness rules) + pre-commit hook; CI on macOS, Linux, and Windows.
- More footguns documented: Text/Tex `color=`, CMU Serif θ and `~`, Tex `--` and `:`,
  `--fps` crash, `-s` without `-w`, fractional-frame run_times.

## 0.1.0

- Initial workspace: ManimGL 1.7.2 via uv, `common.py`, topic template, `manimgl` and
  `iteration-workbench` skills, headless `snapshot.py`, per-topic output routing.
