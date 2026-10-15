"""Pre-tool hook for every enabled agent: keep external source directories read-only.

Wired into each agent's own hook config by `just agent <name>` (scripts/agents.py):
    uv run --quiet --project <root> --no-sync python <root>/.agents/hooks/readonly_guard.py --agent <name>

The protected directories are read on every call from each <area>/<topic>/SOURCES.local.md
(the absolute paths on any line), so the hook command never changes and a SOURCES edit
takes effect without a restart.

Reads the agent's hook payload as JSON on stdin:
- a shell command (`tool_input.command` for Claude Code, Codex, Gemini CLI; `command` for
  Cursor) is denied when it names a protected directory (absolute, ~-relative, or a cd into
  it) AND contains a write form (redirect, rm/mv/cp/touch/..., in-place edits, git, archive
  extraction, a Python/Node write);
- a patch (Codex `apply_patch`, whose text is in `tool_input.command`) is denied when it
  names a protected directory;
- a file-writing tool that passes a path (`tool_input.file_path`) is denied when the path
  is inside a protected directory.
Anything else passes. A deny exits 2 with the reason on stderr, which all four agents
treat as "block this tool call and tell the model why".

Known gap: a script file that writes there without naming the path on its command line
is not caught. The agents' own deny rules (where they have them) cover their file tools.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WRITE_FORMS = [
    r"(?<![0-9&])>{1,2}(?!&)",          # > and >> redirects (not 2>&1)
    r"\b(rm|rmdir|mv|cp|rsync|touch|mkdir|ln|chmod|chown|chflags|xattr|tee|truncate|dd|install|ditto|shred|unlink)\b",
    r"\bsed\b[^|;&]*\s-[a-zA-Z]*i",     # sed -i / sed -Ei
    r"\bperl\b[^|;&]*\s-[a-zA-Z]*i",    # perl -i / perl -pi
    r"\bgit\b",
    r"\b(unzip|gunzip|bunzip2|7z|zip)\b",
    r"\btar\b[^|;&]*\s-?[a-zA-Z]*[xc]",
    r"\bopen\([^)]*['\"][wax+]",        # python open(..., 'w'/'a'/'x'/'r+')
    r"\.(write_text|write_bytes|mkdir|unlink|rename|replace|rmdir|touch)\(",
    r"\b(shutil|os)\.(copy|move|remove|rename|replace|unlink|makedirs|mkdir|rmdir|rmtree)",
    r"\b(writeFile|appendFile|mkdirSync|rmSync|unlinkSync)\b",
    r"\bfind\b[^|;&]*\s-(delete|exec|execdir|ok)\b",
    r"\bsavefig\b|\.to_csv\(|\.save\(",
]

# Tools that write the file named in tool_input.file_path (Gemini CLI; Claude Code's names
# too, in case a hook matcher ever routes them here).
WRITE_TOOLS = {"write_file", "replace", "Write", "Edit", "MultiEdit", "NotebookEdit"}

PLACEHOLDER = re.compile(r"/absolute/path|<[^>]+>")
PATH = re.compile(r"(?<![\w/])(~[/\\][^\s`'\")]+|/[^\s`'\")]+|[A-Za-z]:[/\\][^\s`'\")]*)")


# --- which directories are protected -----------------------------------------------------

def source_files(root):
    return sorted(p for p in Path(root).glob("*/*/SOURCES.local.md") if not p.parts[-3].startswith("."))


def to_dir(raw):
    """Directory to protect for one path mentioned in a SOURCES file."""
    p = Path(raw).expanduser()
    if p.exists():
        return p.resolve() if p.is_dir() else p.resolve().parent
    # Not on this machine (yet): a name with a suffix is a file, anything else a folder.
    return p.parent if p.suffix else p


def protected_dirs(root=ROOT):
    """Every directory named in any SOURCES.local.md, minus the repo and its ancestors."""
    root = Path(root).resolve()
    dirs = set()
    for f in source_files(root):
        for line in f.read_text(encoding="utf-8").splitlines():
            for raw in PATH.findall(line):
                raw = raw.rstrip(".,;:")
                if PLACEHOLDER.search(raw):
                    continue
                d = to_dir(raw)
                if d == root or root in d.parents or d in root.parents or d == Path(d.anchor):
                    continue  # never lock the repo itself, an ancestor of it, or a drive root
                dirs.add(d)
    # Drop directories already covered by a protected ancestor.
    return sorted(d for d in dirs if not any(a in dirs for a in d.parents))


# --- does this call write there ----------------------------------------------------------

def variants(path):
    path = os.path.normpath(path)
    home = os.path.expanduser("~")
    out = {path}
    if path.startswith(home + os.sep):
        rel = path[len(home):]
        out |= {"~" + rel, "$HOME" + rel, "${HOME}" + rel}
    if re.match(r"[A-Za-z]:\\", path):
        # Windows: agents often run commands through Git Bash, so the same directory can
        # appear as C:\x, C:/x or /c/x.
        fwd = path.replace("\\", "/")
        out |= {fwd, "/" + fwd[0].lower() + fwd[2:]}
        out |= {v.replace("\\", "/") for v in out}
    return out


def contains(cmd, needle):
    if sys.platform == "win32":
        return needle.lower() in cmd.lower()
    return needle in cmd


def names_protected(cmd, protected):
    for p in protected:
        for v in variants(str(p)):
            if contains(cmd, v):
                return p
        # a bare cd into the directory by its last component (e.g. `cd lecture-notes`)
        base = re.escape(os.path.basename(os.path.normpath(str(p))))
        if re.search(r"\b(cd|pushd)\s+[^;&|]*" + base + r"(/|\s|$|['\"])", cmd):
            return p
    return None


def inside(path, protected, cwd=None):
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path(cwd or os.getcwd()) / p
    p = Path(os.path.realpath(p))
    for d in protected:
        if p == d or d in p.parents:
            return d
    return None


def call_from(payload):
    """("shell" | "patch", text) or ("path", file_path) from any agent's hook payload, else None."""
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("command"), str):          # Cursor beforeShellExecution
        return "shell", payload["command"]
    ti = payload.get("tool_input")
    if not isinstance(ti, dict):
        return None
    cmd = ti.get("command")
    if isinstance(cmd, list):                            # argv form
        cmd = " ".join(str(c) for c in cmd)
    if isinstance(cmd, str):
        if payload.get("tool_name") == "apply_patch":    # Codex file edits
            return "patch", cmd
        return "shell", cmd                              # Claude Code, Codex, Gemini CLI
    if payload.get("tool_name") in WRITE_TOOLS and isinstance(ti.get("file_path"), str):
        return "path", ti["file_path"]
    return None


def verdict(payload, protected):
    """The deny reason, or None to allow."""
    call = call_from(payload)
    if not call or not protected:
        return None
    kind, value = call
    if kind == "path":
        hit = inside(value, protected, payload.get("cwd"))
    elif kind == "patch":
        hit = names_protected(value, protected)
    else:
        hit = names_protected(value, protected)
        if hit and not any(re.search(rx, value) for rx in WRITE_FORMS):
            hit = None
    if not hit:
        return None
    return (
        f"{hit} is a read-only source directory (see SOURCES.local.md). "
        "Read from it only; write outputs inside this repo instead."
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", help="which agent is calling (informational)")
    ap.parse_args()
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    reason = verdict(payload, protected_dirs())
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
