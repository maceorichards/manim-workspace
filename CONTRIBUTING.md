# Contributing

## Two kinds of change

| Change | Where it goes |
|---|---|
| Template: `common.py`, scripts, skills, docs, `templates/`, config | `main` |
| Your movies: `<area>/…` | your personal branch (e.g. `checkpoint_<initials>`) |

`main` must stay a clean template that anyone can clone. The pre-commit hook
(`scripts/check_staged.py`, installed by `just setup`) refuses commits on `main`
that touch anything outside `.claude/ .github/ .vscode/ scripts/ templates/` and
the root files. On every branch, it also refuses generated output (`videos/`,
`frames/`, `cache/`, `scratch/`), media files, and `*.local.*` files.

## Branch workflow

```bash
git switch -c checkpoint_<initials> main     # once: your branch for movies
# ... make movies, commit as usual ...
git merge main                               # pull in template updates
```

When you improve the template while making a movie, commit the generic part to
`main` (not to your branch), then `git merge main` into your branch. Use merge,
not rebase, since your branch is pushed. Area-specific agent notes go in
`<area>/AGENTS.md`, never the root `AGENTS.md`, so merges don't conflict.

### Optional: keep `main` checked out next to your branch

So template fixes don't need a branch switch or a stash:

```bash
git worktree add .claude/worktrees/main main     # .claude/worktrees/ is gitignored
cd .claude/worktrees/main && uv sync             # its own .venv, see below
# edit, `just lint && just check-all`, commit, push
cd ../../.. && git merge main                    # back in your branch's checkout
```

The worktree needs **its own** `uv sync`. `common.py` is installed editable, so
with a shared `.venv`, `from common import *` silently loads the other checkout's
`common.py`. Run commands from the worktree's root so its `custom_config.yml` is
used. Without a worktree, `git switch main` works too: area folders are tracked
only on your branch, so they leave and come back cleanly.

## Before committing

- `just lint` and `just check-all` pass (CI runs both on macOS, Linux, and Windows).
- For scene or `common.py` changes, `just snap templates/topic FiringRateCurve`,
  then look at the PNG. Delete `templates/topic/frames/` afterwards.
- Names describe content: topics, scene classes, and output files, never their position
  (`s03_vid1`, `part2_clip3`).
- Docs say `just …` or `uv run …`, never `.venv/bin/…` (that path doesn't exist on Windows).
- A new ManimGL footgun goes in `MANIM_WORKFLOW.md` and the `manimgl` skill's
  footgun section, with how it was verified.
- Template release: add a `CHANGELOG.md` entry and tag it (`git tag v0.2.0`).

## Vendored material

`.claude/skills/manimgl/` is vendored from two upstreams with different
licenses; read its `NOTICE.md` before editing or re-syncing. Ruff skips it on purpose.
