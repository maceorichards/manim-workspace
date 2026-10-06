"""Run every `__main__` assert block in the workspace: the template, each topic, each area module.

    uv run python scripts/check_all.py            # all of them
    uv run python scripts/check_all.py <area>     # one area only

Each file runs in its own process from the repo root, as `python <file>` does.
Exit code 1 if any fails. Needs no LaTeX, ffmpeg, or display: asserts only touch
the pure functions (importing manimlib is fine headless).
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOT_AREAS = {"templates", "scripts", "docs", "scratch", "videos", "__pycache__"}


def targets(only=None):
    files = [ROOT / "templates" / "topic" / "main.py"] if not only else []
    for area in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        if area.name.startswith(".") or area.name in NOT_AREAS or (only and area.name != only):
            continue
        modules = [f for f in sorted(area.glob("*.py")) if "__main__" in f.read_text(encoding="utf-8")]
        files += modules + sorted(area.glob("*/main.py"))
    return files


def main():
    files = targets(sys.argv[1] if len(sys.argv) > 1 else None)
    failed = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        t0 = time.monotonic()
        p = subprocess.run([sys.executable, str(f)], cwd=ROOT, capture_output=True, text=True)
        dt = time.monotonic() - t0
        print(f"{'ok  ' if p.returncode == 0 else 'FAIL'} {dt:5.1f}s  {rel}", flush=True)
        if p.returncode:
            failed.append(rel)
            tail = (p.stdout + p.stderr).strip().splitlines()[-10:]
            print("\n".join("       " + line for line in tail))
    print(f"\n{len(files) - len(failed)}/{len(files)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
