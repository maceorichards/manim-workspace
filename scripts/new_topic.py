"""Start a movie: copy templates/topic/ to <area>/<topic>/.

    uv run python scripts/new_topic.py <area> <topic> [--scene ClassName]
    just new <area> <topic> [ClassName]

Renames the template scene class (default: the topic in CamelCase), turns
SOURCES.example.md into SOURCES.local.md, and leaves out any generated output
the template may hold. A new area also gets <area>/AGENTS.md from
templates/area/. Ends by refreshing the read-only guard (sync_guard.py).
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "topic"
AREA_TEMPLATE = ROOT / "templates" / "area"
TEMPLATE_SCENE = "FiringRateCurve"
SKIP = shutil.ignore_patterns("videos", "frames", "cache", "__pycache__", "*.local.md")
NAME = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
DECK_SLOT = re.compile(r"(^|_)s\d+_?(vid|slide)\d+", re.I)


def camel(name):
    return "".join(part.capitalize() for part in re.split(r"[-_]", name))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("area", help="e.g. neural-circuits (lowercase, - or _ separated)")
    ap.add_argument("topic", help="named for its content, e.g. firing_rate_adaptation")
    ap.add_argument("--scene", help="scene class name (default: topic in CamelCase)")
    args = ap.parse_args()

    for label, value in (("area", args.area), ("topic", args.topic)):
        if not NAME.fullmatch(value):
            sys.exit(f"{label} {value!r}: use lowercase letters, digits, - or _")
        if DECK_SLOT.search(value):
            print(f"warning: {label} {value!r} looks like a deck slot; name it for its content")
    if args.area in {"templates", "scripts", "docs"} or args.area.startswith("."):
        sys.exit(f"{args.area!r} is reserved")

    scene = args.scene or camel(args.topic)
    if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", scene):
        sys.exit(f"scene {scene!r}: use a CamelCase class name")

    area = ROOT / args.area
    dest = area / args.topic
    if dest.exists():
        sys.exit(f"{dest.relative_to(ROOT)} already exists")

    if not area.exists():
        shutil.copytree(AREA_TEMPLATE, area)
        for f in area.rglob("*.md"):
            f.write_text(f.read_text(encoding="utf-8").replace("<area>", args.area), encoding="utf-8")
        print(f"created area {args.area}/ (edit {args.area}/AGENTS.md)")

    shutil.copytree(TEMPLATE, dest, ignore=SKIP)
    (dest / "SOURCES.example.md").rename(dest / "SOURCES.local.md")
    for f in [dest / "main.py", *dest.rglob("*.md")]:
        text = f.read_text(encoding="utf-8")
        text = re.sub(rf"\b{TEMPLATE_SCENE}\b", scene, text).replace("<topic>", args.topic)
        f.write_text(text, encoding="utf-8")

    rel = dest.relative_to(ROOT).as_posix()
    print(f"created {rel}/ with scene {scene}")
    print(f"next: fill in {rel}/SOURCES.local.md, then `just guard-sync`")
    print(f"      replace the firing-rate example in {rel}/main.py and WORKBENCH.md")
    sys.stdout.flush()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_guard.py")], check=False)


if __name__ == "__main__":
    main()
