"""Second half of setup, the same on every OS: run by setup.sh / setup.ps1 after `uv sync`.

    uv run python scripts/post_setup.py [--agent claude|codex|cursor|gemini|auto]

Installs the git pre-commit hook, generates the agent adapter (scripts/agents.py;
`auto` or no --agent detects the agent from this shell), runs the doctor, then the
template's asserts and one headless snapshot. Prints a pass/fail summary. Safe to re-run.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
TEMPLATE = ROOT / "templates" / "topic"


def step(label, cmd, required=True):
    print(f"\n== {label}", flush=True)
    ok = subprocess.run(cmd, cwd=ROOT).returncode == 0
    return label, ok, required


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", default="auto", help="agent to generate the adapter for (default: detect)")
    args = ap.parse_args()

    results = []
    if (ROOT / ".git").exists():
        results.append(step("git hooks (pre-commit)", [PY, "-m", "pre_commit", "install"], required=False))
    results.append(step(
        f"agent adapter ({args.agent}; pick another with `just agent <name>`)",
        [PY, "scripts/agents.py", args.agent], required=False,
    ))
    results.append(step("doctor", [PY, "tools/doctor.py", "--font", "CMU Serif"]))
    results.append(step("template asserts", [PY, "templates/topic/main.py"]))
    results.append(step(
        "template snapshot (Text, Tex, Axes; needs LaTeX and an OpenGL context)",
        [PY, "tools/snapshot.py", "templates/topic/main.py", "FiringRateCurve", "--quiet"],
    ))
    frame = TEMPLATE / "frames" / "FiringRateCurve_final.png"
    if frame.exists():
        kept = ROOT / "setup_check.png"
        shutil.copyfile(frame, kept)
        print(f"open {kept.name} to eyeball it (gitignored, delete when done)")
    shutil.rmtree(TEMPLATE / "frames", ignore_errors=True)  # don't let it be copied into new topics

    print("\n== summary")
    for label, ok, required in results:
        print(f"{'ok  ' if ok else ('FAIL' if required else 'WARN')}  {label}")
    failed = [label for label, ok, required in results if required and not ok]
    if failed:
        print("\nFix the FAIL rows (doctor's output above says how), then re-run `just setup`.")
        return 1
    print("\nReady. Next: `just new <area> <topic>`, or open templates/topic/main.py in the editor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
