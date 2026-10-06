"""Pre-commit guard: keep generated output, machine-local files, and (on main) area content out of git.

    uv run python scripts/check_staged.py [FILE ...]           # pre-commit passes staged files
    uv run python scripts/check_staged.py --branch main FILE   # test a branch without switching

Everywhere: rejects videos/, frames/, cache/, scratch/, media files, *.local.*
files, and .claude/settings.local.json.
On branch `main` only: rejects anything outside the template (MAIN_ALLOWED),
because `main` is the template and areas live on personal branches.
"""

import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath

TEMPLATE_BRANCH = "main"
MAIN_ALLOWED_DIRS = {".claude", ".github", ".vscode", "scripts", "templates"}
GENERATED_DIRS = {"videos", "frames", "cache", "scratch", "__pycache__"}
MEDIA = re.compile(r"\.(mp4|mov|gif|png|jpe?g|npz|vsix)$", re.I)
LOCAL = re.compile(r"(^|/)[^/]*\.local\.[^/]+$")


def current_branch():
    out = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    return out.stdout.strip()


def problems(path, branch):
    p = PurePosixPath(path.replace("\\", "/"))
    if GENERATED_DIRS & set(p.parts[:-1]):
        yield "generated output"
    if MEDIA.search(p.name):
        yield "media/binary file"
    if LOCAL.search(str(p)) or str(p) == ".claude/settings.local.json":
        yield "machine-local file"
    if branch == TEMPLATE_BRANCH and len(p.parts) > 1 and p.parts[0] not in MAIN_ALLOWED_DIRS:
        yield f"not part of the template (commit areas on a personal branch, not {TEMPLATE_BRANCH})"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--branch", help="branch to check against (default: the current one)")
    args = ap.parse_args()

    branch = args.branch or current_branch()
    bad = [(f, why) for f in args.files for why in problems(f, branch)]
    for f, why in bad:
        print(f"{f}: {why}")
    if bad:
        print("\nUnstage these (git restore --staged <file>) or fix .gitignore.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
