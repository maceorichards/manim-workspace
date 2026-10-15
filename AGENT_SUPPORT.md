# Agent support

Everything an agent needs lives in neutral, tracked places:

| Source | What it is |
|---|---|
| `AGENTS.md`, `<area>/AGENTS.md` | the rules (the only instructions file you edit) |
| `.agents/skills/<name>/SKILL.md` | skills, in the open Agent Skills format (`name`, `description` front matter) |
| `.agents/hooks/readonly_guard.py` | one pre-tool hook for every agent: blocks writes into `SOURCES.local.md` folders |
| `scripts/agents.py` | the generator: one registry entry per agent |

`just setup [agent]` or `just agent <name>` turns those into the agent's own folder. Those
folders and the `CLAUDE.md` shims are **generated and gitignored**: never edit or commit
them; change the sources (or the generator) and run `just agent-sync`.

```bash
just agent                  # enabled agents, what detection sees, protected folders
just agent claude           # enable or regenerate one (claude | codex | cursor | gemini | auto)
just agent --remove cursor  # delete what was generated for it
just agent-sync             # regenerate all enabled agents (after editing SOURCES.local.md,
                            # adding an area, or adding a skill; `just new` runs it)
```

Several agents can be enabled at once. The generator owns only what it wrote, recorded in
`.agents/state.local.json`: its links, its shims, whole files it created, and the individual
entries it added to an agent's JSON config. Your own entries in those files survive
regeneration and removal.

## What each agent gets

| | Claude Code | Codex CLI | Cursor | Gemini CLI |
|---|---|---|---|---|
| Reads `AGENTS.md` | via generated `CLAUDE.md` shims (`@AGENTS.md`, root and each area) | natively | natively | via `context.fileName` in `.gemini/settings.json` |
| Skills | links `.claude/skills/<name>` → `.agents/skills/<name>` | natively (`.agents/skills`) | natively (`.agents/skills`) | natively (`.agents/skills` alias) |
| `just` / `uv run` allowed without asking | `.claude/settings.json` `permissions.allow` | `.codex/rules/workspace.rules` (`prefix_rule`) | `.cursor/cli.json` `Shell(just)`, `Shell(uv)` | `.gemini/settings.json` `tools.allowed` |
| Guard: shell commands | `PreToolUse` hook (Bash) | `PreToolUse` hook (Bash, apply_patch) in `.codex/hooks.json` | `beforeShellExecution` in `.cursor/hooks.json` | `BeforeTool` hook (run_shell_command) |
| Guard: file edits | `Edit` deny rules (they cover every file-editing tool) | `apply_patch` in the same hook; the workspace-write sandbox blocks writes outside the repo anyway | `Write(...)` deny rules in `.cursor/cli.json` | same hook (write_file, replace) |
| After generating | accept the trust dialog once (until then the allowlist is ignored); `/reload-skills` if skills don't show | trust the project, then trust the hook in `/hooks` | nothing (hooks.json reloads on save) | trust the folder and approve the hook |

The hook reads every `SOURCES.local.md` on each call, so a new source folder is protected
immediately. Deny rules are static: run `just agent-sync` after editing a `SOURCES.local.md`.

Known gaps:

- **Cursor:** `cli.json` permissions are documented for the Cursor CLI (`cursor-agent`); the
  IDE agent may ignore them, leaving its file edits covered only by the `AGENTS.md` rule.
  Cursor also loads `.claude/skills/`, so with Claude enabled too it may list each skill
  twice (same files).
- **Every agent:** a script file that writes into a source folder without naming it on its
  command line is not caught (see the hook's docstring).
- **Codex and Gemini** fingerprint project hooks: if the hook command changes (it only does
  when the repo moves), approve it again.

Other agents that read `AGENTS.md` and `.agents/skills/` natively (GitHub Copilot, Windsurf,
OpenCode, Amp) work without an adapter, but get no allowlist or guard; they must honor the
read-only rule in `AGENTS.md` themselves.

## Detection

`just agent auto` (and `just setup` without an agent) picks the agent from this shell:

1. a marker the agent sets in the shells it runs: `CLAUDECODE` (Claude Code),
   `CODEX_SANDBOX` / `CODEX_THREAD_ID` (Codex), `GEMINI_CLI` (Gemini CLI), `CURSOR_AGENT` (Cursor);
2. otherwise an editor-terminal marker (`CURSOR_CLI`, `CURSOR_TRACE_ID`). These rank lower
   because any agent started inside Cursor's terminal inherits them;
3. otherwise the one agent CLI on `PATH` (`claude`, `codex`, `cursor-agent`, `gemini`).

If that is ambiguous, it asks (in a terminal) or stops with the choices. Naming the agent
(`just agent claude`) always wins; agents setting up the repo should name themselves.

## Adding an agent

1. In `scripts/agents.py`, write a builder `def myagent(root, dirs) -> Adapter` that returns
   its links, shims, whole files, JSON entries and `next:` notes. `dirs` are the protected
   folders.
2. Add it to `AGENTS` with its shell markers and CLI name.
3. If its hook payload puts the command or path somewhere new, teach `call_from()` in
   `.agents/hooks/readonly_guard.py`.
4. Add a case to `selftest()` (`just check-all` runs it), a column here, and the agent
   folder to `.gitignore` and `GENERATED_AGENT_DIRS` in `scripts/check_staged.py`.
