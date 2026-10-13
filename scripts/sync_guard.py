"""Keep every source directory named in a SOURCES.local.md read-only for Claude Code.

    uv run python scripts/sync_guard.py          # rewrite the guard in .claude/settings.local.json
    uv run python scripts/sync_guard.py --dry    # print what would be protected

Collects the absolute paths in <area>/<topic>/SOURCES.local.md (lines such as
`- notes: /abs/notes/`), reduces each to a directory, and writes three things into
.claude/settings.local.json:

- allow Read(...) for each directory, so reading sources needs no prompt;
- deny Edit/Write(...) for each directory (Edit also covers NotebookEdit);
- one PreToolUse Bash hook running .claude/hooks/readonly_guard.py on them.

Only entries this script wrote last time (remembered in .claude/guard.local.json)
and the readonly_guard.py hook are replaced; everything else in the file is kept.
Paths inside this repo are never protected. Other agents: see PORTING.md.
"""

import argparse
import json
import re
import sys
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / ".claude" / "settings.local.json"
STATE = ROOT / ".claude" / "guard.local.json"
# Edit rules also cover NotebookEdit, whose own path rules Claude Code does not check.
TOOLS_DENY = ("Edit", "Write")
PLACEHOLDER = re.compile(r"/absolute/path|<[^>]+>")
PATH = re.compile(r"(?<![\w/])(~[/\\][^\s`'\")]+|/[^\s`'\")]+|[A-Za-z]:[/\\][^\s`'\")]*)")
HOOK = (
    'uv run --project "$CLAUDE_PROJECT_DIR" --no-sync python '
    '"$CLAUDE_PROJECT_DIR/.claude/hooks/readonly_guard.py"'
)


def source_files():
    return sorted(p for p in ROOT.glob("*/*/SOURCES.local.md") if not p.parts[-3].startswith("."))


def to_dir(raw):
    """Directory to protect for one path mentioned in a SOURCES file."""
    p = Path(raw).expanduser()
    if p.exists():
        return p.resolve() if p.is_dir() else p.resolve().parent
    # Not on this machine (yet): a name with a suffix is a file, anything else a folder.
    return p.parent if p.suffix else p


def collect():
    dirs = set()
    for f in source_files():
        for line in f.read_text(encoding="utf-8").splitlines():
            for raw in PATH.findall(line):
                raw = raw.rstrip(".,;:")
                if PLACEHOLDER.search(raw):
                    continue
                d = to_dir(raw)
                if d == ROOT or ROOT in d.parents or d in ROOT.parents or d == Path(d.anchor):
                    continue  # never lock the repo itself, an ancestor of it, or a drive root
                dirs.add(d)
    # Drop directories already covered by a protected ancestor.
    return sorted(d for d in dirs if not any(a in dirs for a in d.parents))


def rule_path(d):
    """Claude Code permission syntax for an absolute path: //abs/path/**.

    Windows paths take the POSIX form, so C:\\Users\\me\\notes -> //c/Users/me/notes/**.
    """
    s = str(d)
    if re.match(r"[A-Za-z]:[\\/]", s):
        w = PureWindowsPath(s)
        s = "/" + w.drive[0].lower() + "/" + "/".join(w.parts[1:])
    return "/" + s.rstrip("/") + "/**"


def rules(dirs):
    allow = [f"Read({rule_path(d)})" for d in dirs]
    deny = [f"{tool}({rule_path(d)})" for d in dirs for tool in TOOLS_DENY]
    return allow, deny


def load(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write(dirs):
    settings = load(SETTINGS, {})
    previous = load(STATE, {"allow": [], "deny": []})
    allow, deny = rules(dirs)

    perms = settings.setdefault("permissions", {})
    for key, new in (("allow", allow), ("deny", deny)):
        kept = [r for r in perms.get(key, []) if r not in previous.get(key, []) and r not in new]
        perms[key] = kept + new
        if not perms[key]:
            del perms[key]
    if not perms:
        del settings["permissions"]

    hooks = settings.setdefault("hooks", {})
    groups = [
        g for g in hooks.get("PreToolUse", [])
        if not any("readonly_guard.py" in h.get("command", "") for h in g.get("hooks", []))
    ]
    if dirs:
        args = " ".join(json.dumps(str(d)) for d in dirs)
        groups.append({"matcher": "Bash", "hooks": [{"type": "command", "command": f"{HOOK} {args}"}]})
    hooks["PreToolUse"] = groups
    if not groups:
        del hooks["PreToolUse"]
    if not hooks:
        del settings["hooks"]

    SETTINGS.parent.mkdir(exist_ok=True)
    SETTINGS.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    STATE.write_text(json.dumps({"allow": allow, "deny": deny}, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry", action="store_true", help="print the directories, change nothing")
    args = ap.parse_args()

    dirs = collect()
    for d in dirs:
        print(f"read-only: {d}")
    if not dirs:
        print("no source directories found in any SOURCES.local.md")
    if args.dry:
        return
    write(dirs)
    rel = SETTINGS.relative_to(ROOT).as_posix()
    print(f"updated {rel} ({len(dirs)} director{'y' if len(dirs) == 1 else 'ies'}); restart Claude Code to load it")


if __name__ == "__main__":
    sys.exit(main())
