"""Generate each coding agent's adapter from the neutral, tracked sources.

    uv run python scripts/agents.py                   # status: enabled agents, detection, guard
    uv run python scripts/agents.py claude            # enable (or regenerate) one agent
    uv run python scripts/agents.py auto              # enable the agent detected from this shell
    uv run python scripts/agents.py --remove cursor   # delete what was generated for one agent
    uv run python scripts/agents.py --sync            # regenerate every enabled agent
    uv run python scripts/agents.py --selftest        # generate into a temp repo and check

    just agent [name | auto | --remove name]   just agent-sync   just setup [agent]

Tracked sources: AGENTS.md (root and <area>/AGENTS.md), .agents/skills/,
.agents/hooks/readonly_guard.py, and the paths in every SOURCES.local.md. Generated and
gitignored: .claude/, .codex/, .cursor/, .gemini/ and the CLAUDE.md shims.

The generator owns only what it wrote (recorded in .agents/state.local.json): its links,
shims, whole files, and the individual entries it added to an agent's JSON config. Anything
else in those files is kept. Supported agents and what each gets: AGENT_SUPPORT.md. To add
an agent, add an entry to AGENTS and a case to selftest().
"""

import argparse
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath

REPO = Path(__file__).resolve().parent.parent
GUARD = ".agents/hooks/readonly_guard.py"
SKILLS = ".agents/skills"
STATE = ".agents/state.local.json"
SHIM = "@AGENTS.md\n"
JUNK = {".DS_Store", "Thumbs.db", "desktop.ini", "__pycache__"}
NOT_AREAS = {"templates", "scripts", "docs", "tools", "scratch", "videos", "__pycache__"}


def _load_guard():
    spec = importlib.util.spec_from_file_location("readonly_guard", REPO / GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load_guard()


# --- what an adapter is -------------------------------------------------------------------

@dataclass
class Adapter:
    links: dict = field(default_factory=dict)   # link path -> target dir (both repo-relative)
    shims: dict = field(default_factory=dict)   # path -> text, written only if absent or ours
    files: dict = field(default_factory=dict)   # path -> text, whole file owned
    json: dict = field(default_factory=dict)    # path -> [(keypath, value)], list items owned
    notes: list = field(default_factory=list)


def skills(root):
    base = root / SKILLS
    return sorted(p.name for p in base.iterdir() if (p / "SKILL.md").exists()) if base.is_dir() else []


def instruction_dirs(root):
    """The root and every area with its own AGENTS.md (repo-relative, '' for the root)."""
    out = [""] if (root / "AGENTS.md").exists() else []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        if not d.name.startswith(".") and d.name not in NOT_AREAS and (d / "AGENTS.md").exists():
            out.append(d.name)
    return out


def rule_path(d):
    """Permission-rule form of an absolute directory: //abs/path/** (C:\\x -> //c/x/**)."""
    s = str(d)
    if PureWindowsPath(s).drive:
        w = PureWindowsPath(s)
        s = "/" + w.drive[0].lower() + "/" + "/".join(w.parts[1:])
    return "/" + s.rstrip("/") + "/**"


def hook_command(root_expr, agent):
    py = f"{root_expr}/{GUARD}" if root_expr else GUARD
    project = f'--project "{root_expr}" ' if root_expr else ""
    return f'uv run --quiet {project}--no-sync python "{py}" --agent {agent}'


def absolute(root):
    return root.resolve().as_posix()


ALLOW = ("just", "uv run")


def claude(root, dirs):
    a = Adapter()
    for s in skills(root):
        a.links[f".claude/skills/{s}"] = f"{SKILLS}/{s}"
    for d in instruction_dirs(root):
        a.shims[f"{d}/CLAUDE.md" if d else "CLAUDE.md"] = SHIM
    hook = {"matcher": "Bash", "hooks": [
        {"type": "command", "command": hook_command("${CLAUDE_PROJECT_DIR}", "claude")}]}
    a.json[".claude/settings.json"] = (
        [(("permissions", "allow"), f"Bash({c}:*)") for c in ALLOW]
        + [(("permissions", "allow"), f"Read({rule_path(d)})") for d in dirs]
        + [(("permissions", "deny"), f"Edit({rule_path(d)})") for d in dirs]   # Edit covers every file tool
        + [(("hooks", "PreToolUse"), hook)]
    )
    a.notes.append("Claude Code: start it here once interactively and accept the trust dialog "
                   "(until then it ignores the allowlist); skills, settings and the hook reload on "
                   "their own, or run /reload-skills.")
    return a


def codex(root, dirs):
    a = Adapter()
    top = "$(git rev-parse --show-toplevel)"
    hook = {"matcher": "^(Bash|apply_patch)$", "hooks": [{
        "type": "command",
        "command": hook_command(top, "codex"),
        "commandWindows": hook_command(absolute(root), "codex"),
        "statusMessage": "Checking read-only source folders",
    }]}
    a.json[".codex/hooks.json"] = [(("hooks", "PreToolUse"), hook)]
    rules = "".join(
        f'prefix_rule(pattern = {json.dumps(c.split())}, decision = "allow")\n' for c in ALLOW)
    a.files[".codex/rules/workspace.rules"] = (
        "# Generated by scripts/agents.py (just agent codex); edits are overwritten.\n" + rules)
    a.notes.append("Codex: trust this project (project .codex/ config, hooks and rules load only "
                   "for trusted projects), then review and trust the hook with /hooks. Keep the "
                   "workspace-write sandbox: it already blocks writes outside the repo.")
    return a


def cursor(root, dirs):
    a = Adapter()
    hook = {"command": hook_command("", "cursor"), "timeout": 30}
    a.json[".cursor/hooks.json"] = [(("version",), 1), (("hooks", "beforeShellExecution"), hook)]
    a.json[".cursor/cli.json"] = (
        [(("permissions", "allow"), f"Shell({c.split()[0]})") for c in ALLOW]
        + [(("permissions", "deny"), f"Write({d.as_posix()}/**)") for d in dirs]
    )
    a.notes.append("Cursor: hooks.json reloads on save. cli.json permissions are documented for "
                   "the Cursor CLI (cursor-agent); the IDE agent may ignore them.")
    return a


def gemini(root, dirs):
    a = Adapter()
    hook = {"matcher": "run_shell_command|write_file|replace", "hooks": [{
        "name": "readonly-guard", "type": "command",
        "command": hook_command(absolute(root), "gemini"),
    }]}
    a.json[".gemini/settings.json"] = (
        [(("context", "fileName"), "AGENTS.md"), (("context", "fileName"), "GEMINI.md")]
        + [(("hooks", "BeforeTool"), hook)]
        + [(("tools", "allowed"), f"run_shell_command({c})") for c in ALLOW]
    )
    a.notes.append("Gemini CLI: trust this folder (workspace skills and hooks need it) and "
                   "approve the hook when asked; /memory reload and /skills reload refresh.")
    return a


# Detection: `env` markers are set by the agent in the shells it runs (strong); `weak_env`
# can leak into other agents' shells (Cursor's terminal sets CURSOR_* for whatever runs in
# it); `cli` is the command that, on PATH, means the agent is installed.
AGENTS = {
    "claude": {"build": claude, "env": ["CLAUDECODE"], "weak_env": [], "cli": "claude"},
    "codex": {"build": codex, "env": ["CODEX_SANDBOX", "CODEX_THREAD_ID"], "weak_env": [], "cli": "codex"},
    "gemini": {"build": gemini, "env": ["GEMINI_CLI"], "weak_env": [], "cli": "gemini"},
    "cursor": {"build": cursor, "env": ["CURSOR_AGENT"], "weak_env": ["CURSOR_CLI", "CURSOR_TRACE_ID"],
               "cli": "cursor-agent"},
}


# --- detection ----------------------------------------------------------------------------

def detect(env=None, which=shutil.which):
    """(agent or None, candidates, how)."""
    env = os.environ if env is None else env
    for key, how in (("env", "shell marker"), ("weak_env", "editor terminal marker")):
        hits = [n for n, a in AGENTS.items() if any(env.get(v) for v in a[key])]
        if hits:
            return (hits[0] if len(hits) == 1 else None), hits, how
    hits = [n for n, a in AGENTS.items() if which(a["cli"])]
    return (hits[0] if len(hits) == 1 else None), hits, "CLI on PATH"


# --- file operations ----------------------------------------------------------------------

def load_json(path):
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else {}


def write_json(path, data):
    if data:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    elif path.exists():
        path.unlink()


def add_entry(data, keypath, value):
    """Add value under keypath: list items are appended, other values set if absent.
    True when this call inserted it (and so owns it)."""
    node = data
    for k in keypath[:-1]:
        node = node.setdefault(k, {})
    last = keypath[-1]
    if not isinstance(value, (str, dict)):      # a scalar setting (e.g. "version": 1)
        if last in node:
            return False
        node[last] = value
        return True
    cur = node.get(last)
    if cur is None:
        node[last] = [value]
        return True
    if not isinstance(cur, list):
        cur = node[last] = [cur]
    if value in cur:
        return False
    cur.append(value)
    return True


def remove_entry(data, keypath, value):
    chain = [data]
    for k in keypath[:-1]:
        nxt = chain[-1].get(k)
        if not isinstance(nxt, dict):
            return
        chain.append(nxt)
    node, last = chain[-1], keypath[-1]
    cur = node.get(last)
    if isinstance(cur, list) and value in cur:
        cur.remove(value)
        if not cur:
            del node[last]
    elif cur == value:
        del node[last]
    for parent, k in zip(reversed(chain[:-1]), reversed(keypath[:-1])):
        if parent.get(k) == {}:
            del parent[k]


def is_link(p):
    return p.is_symlink() or p.is_junction()


def only_junk(d):
    """True when d holds nothing but OS litter and Python caches, at any depth (a link is content)."""
    for p in d.rglob("*"):
        if is_link(p) or (not p.is_dir() and p.name not in JUNK and "__pycache__" not in p.parts):
            return False
    return True


def unlink_link(p):
    try:
        p.unlink()
    except (IsADirectoryError, PermissionError, OSError):
        os.rmdir(p)                                # a Windows junction


def make_link(link, target, prev_mode=None):
    """Point link at target: symlink, else (Windows) junction, else a copy. Returns the mode."""
    if is_link(link):
        unlink_link(link)
    elif link.exists():
        if link.is_dir() and (prev_mode == "copy" or only_junk(link)):
            shutil.rmtree(link)
        else:
            raise SystemExit(f"{link} exists and is not a generated link; move it aside, then re-run")
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(os.path.relpath(target, link.parent), link, target_is_directory=True)
        return "symlink"
    except OSError:
        pass
    if sys.platform == "win32":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if r.returncode == 0:
            return "junction"
    shutil.copytree(target, link)
    print(f"warning: copied {target.name} to {link} (no symlinks or junctions here); "
          "re-run `just agent-sync` after editing skills")
    return "copy"


def remove_link(link, mode):
    if is_link(link):
        unlink_link(link)
    elif mode == "copy" and link.is_dir():
        shutil.rmtree(link)


def prune(root, path):
    """Remove now-empty parent directories of path, up to (not including) root."""
    for d in path.parents:
        if d == root or root not in d.parents:
            return
        try:
            if d.is_dir() and only_junk(d):
                shutil.rmtree(d)
            else:
                return
        except OSError:
            return


# --- applying an adapter ------------------------------------------------------------------

def apply(root, adapter, prev):
    """Make the generated state match adapter; prev is what this agent owned last time."""
    prev = prev or {}
    owned = {"links": {}, "shims": [], "files": [], "json": {}}
    gone = []
    for path, mode in prev.get("links", {}).items():
        if path not in adapter.links:
            remove_link(root / path, mode)
            gone.append(root / path)
    for path in prev.get("shims", []):
        p = root / path
        if path not in adapter.shims and p.exists() and p.read_text(encoding="utf-8") == SHIM:
            p.unlink()
            gone.append(p)
    for path in prev.get("files", []):
        if path not in adapter.files and (root / path).exists():
            (root / path).unlink()
            gone.append(root / path)

    for path in sorted(set(prev.get("json", {})) | set(adapter.json)):
        p = root / path
        data = load_json(p)
        for keypath, value in prev.get("json", {}).get(path, []):
            remove_entry(data, tuple(keypath), value)
        inserted = [[list(k), v] for k, v in adapter.json.get(path, []) if add_entry(data, k, v)]
        write_json(p, data)
        if not data:
            gone.append(p)
        if inserted:
            owned["json"][path] = inserted

    for path, target in adapter.links.items():
        owned["links"][path] = make_link(root / path, root / target, prev.get("links", {}).get(path))
    for path, text in adapter.shims.items():
        p = root / path
        if not p.exists():
            p.write_text(text, encoding="utf-8")
        if p.read_text(encoding="utf-8") == text:
            owned["shims"].append(path)
        else:
            print(f"note: {path} has your own content; left as is (add `@AGENTS.md` to it yourself)")
    for path, text in adapter.files.items():
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        owned["files"].append(path)

    for p in gone:
        prune(root, p)
    return owned


def legacy_cleanup(root):
    """Undo what the old scripts/sync_guard.py wrote into .claude/settings.local.json."""
    state, settings = root / ".claude" / "guard.local.json", root / ".claude" / "settings.local.json"
    if not state.exists() and not settings.exists():
        return
    prev = load_json(state) if state.exists() else {}
    data = load_json(settings)
    before = json.dumps(data, sort_keys=True)
    for key in ("allow", "deny"):
        for rule in prev.get(key, []):
            remove_entry(data, ("permissions", key), rule)
    groups = data.get("hooks", {}).get("PreToolUse")
    if isinstance(groups, list):
        for g in [g for g in groups if any(".claude/hooks/readonly_guard.py" in h.get("command", "")
                                           for h in g.get("hooks", []))]:
            remove_entry(data, ("hooks", "PreToolUse"), g)
    if json.dumps(data, sort_keys=True) != before:
        write_json(settings, data)
        print("removed the old read-only guard entries from .claude/settings.local.json")
    if state.exists():
        state.unlink()


def owned_paths(owned):
    return sorted(set(owned["links"]) | set(owned["shims"]) | set(owned["files"]) | set(owned["json"]))


def tracked(root, paths):
    if not paths or not (root / ".git").exists():
        return []
    r = subprocess.run(["git", "ls-files", "--", *paths], cwd=root, capture_output=True, text=True)
    return r.stdout.split()


# --- commands -----------------------------------------------------------------------------

def load_state(root):
    s = load_json(root / STATE)
    return {"enabled": s.get("enabled", []), "owned": s.get("owned", {})}


def save_state(root, state):
    (root / STATE).parent.mkdir(parents=True, exist_ok=True)
    (root / STATE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def sync(root, names=None, quiet=False):
    """Regenerate the given (default: every enabled) agents. Returns the owned paths."""
    state = load_state(root)
    legacy_cleanup(root)
    dirs = guard.protected_dirs(root)
    notes = []
    for name in names or state["enabled"]:
        adapter = AGENTS[name]["build"](root, dirs)
        state["owned"][name] = apply(root, adapter, state["owned"].get(name))
        notes += adapter.notes
        if name not in state["enabled"]:
            state["enabled"].append(name)
    save_state(root, state)
    paths = sorted({p for o in state["owned"].values() for p in owned_paths(o)})
    if not quiet:
        for name in names or state["enabled"]:
            print(f"generated {name} adapter")
        for d in dirs:
            print(f"read-only: {d}")
        for n in notes:
            print(f"next: {n}")
        report_tracked(root, paths)
    return paths


def report_tracked(root, paths):
    hits = tracked(root, paths)
    if hits:
        print("\nThese generated files are still tracked by git (left over from before they were"
              "\ngenerated). Untrack them, keeping the files on disk:")
        print("    git rm --cached -- " + " ".join(hits))


def remove(root, name, quiet=False):
    state = load_state(root)
    apply(root, Adapter(), state["owned"].pop(name, None))
    if name in state["enabled"]:
        state["enabled"].remove(name)
    save_state(root, state)
    if not quiet:
        print(f"removed {name} adapter")


def choose(candidates, how):
    if candidates and sys.stdin.isatty():
        print(f"Several agents found ({how}): {', '.join(candidates)}")
        pick = input("Which one is this for? ").strip()
        if pick in AGENTS:
            return pick
    raise SystemExit(
        "could not tell which agent this is"
        + (f" ({how}: {', '.join(candidates)})" if candidates else "")
        + f"; name it: just agent <{'|'.join(AGENTS)}>")


def status(root):
    state = load_state(root)
    agent, candidates, how = detect()
    print("enabled:  " + (", ".join(state["enabled"]) or "none"))
    print(f"detected: {agent or 'unclear'} ({how}: {', '.join(candidates) or 'nothing'})")
    dirs = guard.protected_dirs(root)
    for d in dirs:
        print(f"read-only: {d}")
    if not dirs:
        print("read-only: no source directories in any SOURCES.local.md")


# --- selftest -----------------------------------------------------------------------------

def run_hook(root, payload):
    """Run the guard as an agent would, against root's SOURCES files."""
    code = (f"import json,sys; sys.path.insert(0, {str(REPO / '.agents' / 'hooks')!r}); "
            "import readonly_guard as g; "
            f"r = g.verdict(json.load(sys.stdin), g.protected_dirs({str(root)!r})); "
            "print(r or '', file=sys.stderr); sys.exit(2 if r else 0)")
    p = subprocess.run([sys.executable, "-c", code], input=json.dumps(payload), capture_output=True, text=True)
    return p.returncode


def selftest():
    with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
        tmp = Path(tmp).resolve()
        root, src = tmp / "repo", tmp / "lecture-notes"
        src.mkdir()
        (src / "spec.md").write_text("spec\n")
        for f, text in {
            "AGENTS.md": "# rules\n",
            "neuro/AGENTS.md": "# area\n",
            "neuro/topic/SOURCES.local.md": f"- notes: {src}/\n- <label>: /absolute/path/to/x\n",
            ".agents/skills/demo/SKILL.md": "---\nname: demo\ndescription: d\n---\n",
        }.items():
            (root / f).parent.mkdir(parents=True, exist_ok=True)
            (root / f).write_text(text, encoding="utf-8")
        assert guard.protected_dirs(root) == [src]

        # Each agent: enable, check, keep hand edits through re-sync and removal.
        (root / ".agents/skills/gone/SKILL.md").parent.mkdir(parents=True)
        (root / ".agents/skills/gone/SKILL.md").write_text("---\nname: gone\ndescription: g\n---\n")
        sync(root, ["claude"], quiet=True)
        assert (root / ".claude/skills/gone/SKILL.md").exists()
        shutil.rmtree(root / ".agents/skills/gone")              # a skill deleted from the sources
        sync(root, ["claude"], quiet=True)
        assert not is_link(root / ".claude/skills/gone") and not (root / ".claude/skills/gone").exists()
        assert (root / ".claude/skills/demo/SKILL.md").exists()
        assert (root / "CLAUDE.md").read_text() == SHIM and (root / "neuro/CLAUDE.md").read_text() == SHIM
        s = load_json(root / ".claude/settings.json")
        assert "Bash(just:*)" in s["permissions"]["allow"]
        assert f"Edit({rule_path(src)})" in s["permissions"]["deny"]
        assert "${CLAUDE_PROJECT_DIR}" in s["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        s["permissions"]["allow"].append("Bash(ls:*)")
        write_json(root / ".claude/settings.json", s)

        sync(root, ["codex"], quiet=True)
        h = load_json(root / ".codex/hooks.json")["hooks"]["PreToolUse"][0]
        assert h["matcher"] == "^(Bash|apply_patch)$" and "commandWindows" in h["hooks"][0]
        assert 'pattern = ["uv", "run"]' in (root / ".codex/rules/workspace.rules").read_text()

        sync(root, ["cursor"], quiet=True)
        c = load_json(root / ".cursor/cli.json")["permissions"]
        assert "Shell(just)" in c["allow"] and f"Write({src.as_posix()}/**)" in c["deny"]
        assert load_json(root / ".cursor/hooks.json")["version"] == 1

        (root / ".gemini").mkdir()
        write_json(root / ".gemini/settings.json", {"context": {"fileName": "MINE.md"}, "theme": "x"})
        sync(root, ["gemini"], quiet=True)
        g = load_json(root / ".gemini/settings.json")
        assert g["context"]["fileName"] == ["MINE.md", "AGENTS.md", "GEMINI.md"]
        assert "run_shell_command(just)" in g["tools"]["allowed"]

        assert load_state(root)["enabled"] == ["claude", "codex", "cursor", "gemini"]
        sync(root, quiet=True)                                   # re-sync is idempotent
        s = load_json(root / ".claude/settings.json")
        assert s["permissions"]["allow"].count("Bash(just:*)") == 1 and "Bash(ls:*)" in s["permissions"]["allow"]

        # A user CLAUDE.md is never overwritten; a new area gets a shim on sync.
        (root / "other").mkdir()
        (root / "other/AGENTS.md").write_text("# other\n")
        (root / "other/CLAUDE.md").write_text("my own notes\n")
        (root / "bio").mkdir()
        (root / "bio/AGENTS.md").write_text("# bio\n")
        sync(root, quiet=True)
        assert (root / "other/CLAUDE.md").read_text() == "my own notes\n"
        assert (root / "bio/CLAUDE.md").read_text() == SHIM

        # Removal takes away only what was generated.
        for name in ("claude", "codex", "cursor", "gemini"):
            remove(root, name, quiet=True)
        assert load_state(root) == {"enabled": [], "owned": {}}
        assert not (root / ".claude/skills").exists() and not (root / "CLAUDE.md").exists()
        assert load_json(root / ".claude/settings.json") == {"permissions": {"allow": ["Bash(ls:*)"]}}
        assert not (root / ".codex").exists() and not (root / ".cursor").exists()
        assert load_json(root / ".gemini/settings.json") == {"context": {"fileName": ["MINE.md"]}, "theme": "x"}
        assert (root / "other/CLAUDE.md").exists() and (root / ".agents/skills/demo/SKILL.md").exists()

        sync(root, ["cursor"], quiet=True)
        remove(root, "cursor", quiet=True)
        assert not (root / ".cursor").exists() and load_state(root)["enabled"] == []

        # A real directory where a link goes: junk is replaced, real content stops the run.
        (root / ".claude/skills/demo/core/__pycache__").mkdir(parents=True)
        (root / ".claude/skills/demo/core/__pycache__/x.cpython-312.pyc").write_text("")
        (root / ".claude/skills/demo/.DS_Store").write_text("")
        sync(root, ["claude"], quiet=True)
        assert is_link(root / ".claude/skills/demo")
        remove(root, "claude", quiet=True)
        (root / ".claude/skills/demo").mkdir(parents=True)
        (root / ".claude/skills/demo/SKILL.md").write_text("hand-made\n")
        try:
            sync(root, ["claude"], quiet=True)
            raise AssertionError("expected a refusal")
        except SystemExit:
            pass
        shutil.rmtree(root / ".claude/skills")
        (root / STATE).unlink()

        # Legacy cleanup of the old sync_guard entries.
        old_hook = {"matcher": "Bash", "hooks": [{"type": "command",
                    "command": 'uv run python "$CLAUDE_PROJECT_DIR/.claude/hooks/readonly_guard.py" /x'}]}
        write_json(root / ".claude/settings.local.json", {
            "permissions": {"allow": ["Read(//x/**)", "Bash(mine:*)"], "deny": ["Edit(//x/**)"]},
            "hooks": {"PreToolUse": [old_hook]}})
        write_json(root / ".claude/guard.local.json", {"allow": ["Read(//x/**)"], "deny": ["Edit(//x/**)"]})
        legacy_cleanup(root)
        assert load_json(root / ".claude/settings.local.json") == {"permissions": {"allow": ["Bash(mine:*)"]}}
        assert not (root / ".claude/guard.local.json").exists()

        # Tracked generated files are reported.
        if shutil.which("git"):
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "neuro/AGENTS.md", "other/CLAUDE.md"], cwd=root, check=True)
            assert tracked(root, ["other/CLAUDE.md", "CLAUDE.md"]) == ["other/CLAUDE.md"]

        # The guard, fed each agent's payload shape.
        w, r = f"touch {src}/new.md", f"ls {src}"
        cases = [
            ({"tool_name": "Bash", "tool_input": {"command": w}}, 2),                # Claude, Codex
            ({"tool_name": "Bash", "tool_input": {"command": r}}, 0),
            ({"tool_name": "run_shell_command", "tool_input": {"command": w}}, 2),   # Gemini
            ({"command": w, "cwd": str(root)}, 2),                                   # Cursor
            ({"command": r, "cwd": str(root)}, 0),
            ({"tool_name": "write_file", "tool_input": {"file_path": f"{src}/a.md"}}, 2),
            ({"tool_name": "replace", "tool_input": {"file_path": str(root / "a.md")}}, 0),
            ({"tool_name": "apply_patch", "tool_input": {"command": f"*** Update File: {src}/spec.md"}}, 2),
            ({"tool_name": "Read", "tool_input": {"file_path": f"{src}/spec.md"}}, 0),
            ({"tool_name": "Bash", "tool_input": {"command": "touch notes.md"}}, 0),
        ]
        for payload, want in cases:
            got = run_hook(root, payload)
            assert got == want, (payload, got)

        assert detect({"CLAUDECODE": "1", "CURSOR_CLI": "1"}, lambda c: None)[0] == "claude"
        assert detect({"CURSOR_CLI": "1"}, lambda c: None)[0] == "cursor"
        assert detect({}, lambda c: c == "codex")[0] == "codex"
        assert detect({}, lambda c: True)[0] is None
    print("agents selftest: ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", nargs="?", choices=[*AGENTS, "auto"], help="agent to enable or regenerate")
    ap.add_argument("--remove", metavar="NAME", choices=list(AGENTS), help="remove one agent's adapter")
    ap.add_argument("--sync", action="store_true", help="regenerate every enabled agent")
    ap.add_argument("--selftest", action="store_true", help="check the generator in a temp repo")
    ap.add_argument("--root", type=Path, default=REPO, help=argparse.SUPPRESS)
    args = ap.parse_args()
    root = args.root.resolve()

    if args.selftest:
        selftest()
    elif args.remove:
        remove(root, args.remove)
    elif args.sync:
        if not load_state(root)["enabled"]:
            print("no agent enabled yet: just agent <" + "|".join(AGENTS) + ">")
        sync(root)
    elif args.name:
        name = args.name
        if name == "auto":
            name, candidates, how = detect()
            name = name or choose(candidates, how)
            print(f"agent: {name} ({how})")
        sync(root, [name])
    else:
        status(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
