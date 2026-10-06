# Using another agent (Codex, Cursor, …)

The workspace is written for Claude Code, but most of it is plain files any agent can use.

| Piece | Portable? | Notes |
|---|---|---|
| `AGENTS.md`, `<area>/AGENTS.md` | yes | Codex, Cursor, and most agents read `AGENTS.md` natively. `CLAUDE.md` is a one-line import for Claude Code. |
| `.claude/skills/*/SKILL.md` | yes | Plain markdown with YAML front matter (name, description). Agents that support skills load them from their own folder; others can be told to read `SKILL.md` when the description matches. |
| `justfile`, `scripts/`, `common.py`, `snapshot.py` | yes | Plain commands; nothing agent-specific. |
| `.claude/settings.json` | no | Claude Code permission allowlist (`just`, `uv run`). Re-create it in your agent's own approval settings. |
| `.claude/settings.local.json` + `.claude/hooks/readonly_guard.py` | partly | The read-only guard. The hook script takes the Bash command as JSON on stdin (`{"tool_name": "Bash", "tool_input": {"command": …}}`) and prints a deny decision. Agents with pre-command hooks can reuse it with a small adapter. Without hooks, the rule in `AGENTS.md` is the only protection. |

## Moving the skills

Most agents look for skills in their own dot-folder. Either copy or symlink:

```bash
# Codex (adjust to wherever your version reads project skills)
mkdir -p .codex && ln -s ../.claude/skills .codex/skills
# Cursor
mkdir -p .cursor && ln -s ../.claude/skills .cursor/skills
```

Or rename `.claude/` to your agent's folder outright. If you do, update these paths:

- `AGENTS.md`, `MANIM_WORKFLOW.md`, `justfile` (`snapshot`, `doctor`): `.claude/skills/manimgl/core/assets/`
- `scripts/post_setup.py`, `scripts/sync_guard.py`: the doctor path and `.claude/settings.local.json`
- `pyproject.toml` (`[tool.ruff] extend-exclude`) and `.gitignore` (`.claude/worktrees/`)
- `scripts/check_staged.py`: `MAIN_ALLOWED_DIRS`

On Windows, symlinks need Developer Mode or an elevated shell; copying works too.

## Behaviors to keep

Whatever the agent, these come from `AGENTS.md` and matter more than the tooling:

- verify headlessly (`just check` → `just list` → `just snap`, then *look* at the PNGs);
- never write into a directory named in a `SOURCES.local.md`;
- build only the workbench items the user picks, then hand back (`iteration-workbench`).
