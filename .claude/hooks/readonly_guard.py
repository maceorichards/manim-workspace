"""PreToolUse hook for Bash: keep external source directories read-only.

Usage (in .claude/settings.local.json, since the paths are machine-specific; written by
`just guard-sync` from every SOURCES.local.md):
    uv run --project "$CLAUDE_PROJECT_DIR" python "$CLAUDE_PROJECT_DIR/.claude/hooks/readonly_guard.py" /abs/dir ...

Denies a Bash command when it names a protected directory (absolute, ~-relative, or a
cd into it) AND contains a write form (redirect, rm/mv/cp/touch/..., in-place edits,
git, archive extraction, a Python/Node write). Read-only commands pass untouched.

Known gap: a script file that writes there without naming the path on its command line
is not caught. The Edit/Write deny rule in settings covers the file tools.
"""

import json
import os
import re
import sys

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


def variants(path):
    path = os.path.normpath(path)
    home = os.path.expanduser("~")
    out = {path}
    if path.startswith(home + os.sep):
        rel = path[len(home):]
        out |= {"~" + rel, "$HOME" + rel, "${HOME}" + rel}
    if re.match(r"[A-Za-z]:\\", path):
        # Windows: Claude Code runs Bash through Git Bash, so the same directory can
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
        for v in variants(p):
            if contains(cmd, v):
                return p
        # a bare cd into the directory by its last component (e.g. `cd lecture-notes`)
        base = re.escape(os.path.basename(os.path.normpath(p)))
        if re.search(r"\b(cd|pushd)\s+[^;&|]*" + base + r"(/|\s|$|['\"])", cmd):
            return p
    return None


def main():
    protected = [a for a in sys.argv[1:] if a]
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    cmd = (payload.get("tool_input") or {}).get("command", "")
    hit = names_protected(cmd, protected)
    if not hit:
        return 0
    if not any(re.search(rx, cmd) for rx in WRITE_FORMS):
        return 0
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{hit} is a read-only source directory (see SOURCES.local.md). "
                "Read from it only; write outputs inside this repo instead."
            ),
        }
    }, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
