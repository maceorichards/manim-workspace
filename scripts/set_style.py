"""Show or change this machine's style override, style.local.yml (gitignored).

    uv run python scripts/set_style.py --show                     # effective style, override marked
    uv run python scripts/set_style.py --preset light             # start from a preset
    uv run python scripts/set_style.py --set background=#0B1020 font="Latin Modern Roman"
    uv run python scripts/set_style.py --set palette.accent=#E07A5F
    uv run python scripts/set_style.py --unset text_color
    uv run python scripts/set_style.py --reset                    # delete the override

The house defaults live in common.py (DEFAULT_STYLE) and apply to everyone.
This file only records what differs on this machine. --preset and --set merge
into the current override. Values are parsed as YAML (1.2 -> float, null -> None).
"""

import argparse
import ast
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STYLE_FILE = ROOT / "style.local.yml"


def house_defaults():
    """DEFAULT_STYLE from common.py, read without importing manimlib (or a broken override)."""
    tree = ast.parse((ROOT / "common.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "DEFAULT_STYLE":
            return ast.literal_eval(node.value)
    raise SystemExit("DEFAULT_STYLE not found in common.py")


DEFAULT_STYLE = house_defaults()

PRESETS = {
    "3b1b-dark": {},  # the house default
    "light": {
        "background": "#FFFFFF",
        "text_color": "#1A1A1A",
        "saturation": 1.0,
    },
    "navy": {
        "background": "#0B1020",
        "saturation": 1.2,
    },
}


def load():
    if not STYLE_FILE.exists():
        return {}
    return yaml.safe_load(STYLE_FILE.read_text(encoding="utf-8")) or {}


def save(style):
    if not style:
        STYLE_FILE.unlink(missing_ok=True)
        print(f"removed {STYLE_FILE.name}; house defaults apply")
        return
    header = "# Local style override, read by common.py. Gitignored. `just style --reset` removes it.\n"
    STYLE_FILE.write_text(header + yaml.safe_dump(style, sort_keys=False), encoding="ascii")
    print(f"wrote {STYLE_FILE.name}")


def set_key(style, assignment):
    key, sep, raw = assignment.partition("=")
    if not sep:
        sys.exit(f"--set wants key=value, got {assignment!r}")
    # Hex colors start with '#', which YAML would read as a comment.
    value = raw if raw.startswith("#") else (yaml.safe_load(raw) if raw else None)
    if key.startswith("palette."):
        style.setdefault("palette", {})[key.split(".", 1)[1]] = value
        return
    if key not in DEFAULT_STYLE or key == "palette":
        sys.exit(f"unknown key {key!r}; one of {sorted(DEFAULT_STYLE)} or palette.<name>")
    style[key] = value


def show(style):
    print(f"# effective style ({'*' if style else 'no'} = from {STYLE_FILE.name})")
    for key, default in DEFAULT_STYLE.items():
        if key == "palette":
            continue
        mark = "*" if key in style else " "
        print(f"{mark} {key:13} {style.get(key, default)!r}")
    for name, color in (style.get("palette") or {}).items():
        print(f"* palette.{name:7} {color!r}  -> {name.upper()} in scene code")
    print("presets:", ", ".join(PRESETS))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", action="store_true", help="print the effective style")
    ap.add_argument("--preset", choices=sorted(PRESETS), help="merge a preset into the override")
    ap.add_argument("--set", nargs="+", default=[], metavar="KEY=VALUE")
    ap.add_argument("--unset", nargs="+", default=[], metavar="KEY")
    ap.add_argument("--reset", action="store_true", help="delete style.local.yml")
    args = ap.parse_args()

    if args.reset:
        save({})
        return
    style = load()
    changed = bool(args.preset or args.set or args.unset)
    if args.preset == "3b1b-dark":
        style = {}
    elif args.preset:
        style.update(PRESETS[args.preset])
    for a in args.set:
        set_key(style, a)
    for key in args.unset:
        if key.startswith("palette."):
            (style.get("palette") or {}).pop(key.split(".", 1)[1], None)
        else:
            style.pop(key, None)
    if changed:
        save(style)
    show(style)


if __name__ == "__main__":
    main()
