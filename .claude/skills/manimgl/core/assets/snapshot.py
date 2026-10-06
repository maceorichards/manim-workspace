"""Snapshot a ManimGL scene at chosen beats so the frames can be inspected as images.

    python snapshot.py file.py Scene --list     # number every play/wait, save nothing
    python snapshot.py file.py Scene 3 7 12     # frames after animations 3, 7 and 12
    python snapshot.py file.py Scene            # final frame only
    python snapshot.py file.py Scene 3 7 --hd   # 1080p instead of the default 480p
    python snapshot.py file.py Scene 3 --res 672x600   # any WxH (sets the frame aspect)

One process, however many frames. `construct()` runs once with every animation
skipped (end states applied instantly) while `Scene.pre_play` is hooked; at each
requested index the hook forces a draw and saves the image. Index K counts
self.play() AND self.wait() calls from 0, in the order they execute, and the
numbering is printed on every run -- so a single call can both number the beats
and grab frames. Output: frames/<Scene>_<K>.png (or <Scene>_final.png) in the
scene file's folder, i.e. <area>/<topic>/frames/.

The earlier version spawned `manimgl -s -w -n 0,K` per index, which replayed the
whole scene from the top for each frame. On a scene whose replay costs ~50 s that
is ~50 s per frame instead of ~50 s per batch.

Stdlib only; runs manimlib through the current interpreter, so the `manimgl`
script does not need to be on PATH.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

RUN = '''
import inspect, os, sys
sys.argv = ["manimgl", {file!r}, {scene!r}, "-s", "-w", *{quality!r},
            "--video_dir", {tmp!r}, "--file_name", "_snap"]
import manimlib
from manimlib.scene.scene import Scene

TARGETS = {targets!r}
BASE = os.path.basename({file!r})
_orig = Scene.pre_play


def pre_play(self):
    k = self.num_plays
    for fr in inspect.stack()[1:]:
        if os.path.basename(fr.filename) == BASE:
            src = fr.code_context[0].strip() if fr.code_context else ""
            print(f"SNAP {{k:3d}}  L{{fr.lineno:<4d}} {{src}}", flush=True)
            break
    if k in TARGETS:
        # force_draw: in skip-animation mode nothing is rendered otherwise.
        self.update_frame(force_draw=True)
        self.get_image().save(TARGETS[k])
        print(f"SAVED {{k}} {{TARGETS[k]}}", flush=True)
    _orig(self)


Scene.pre_play = pre_play
from manimlib.__main__ import main
main()
'''


def run(scene_file, scene, indices, out_dir, quality):
    """One skipped pass: print the numbering, save a frame at each index."""
    os.makedirs(out_dir, exist_ok=True)
    targets = {
        k: os.path.abspath(os.path.join(out_dir, f"{scene}_{k:03d}.png"))
        for k in indices if k is not None
    }
    want_final = None in indices

    with tempfile.TemporaryDirectory() as tmp:
        code = RUN.format(file=scene_file, scene=scene, tmp=tmp,
                          quality=quality, targets=targets)
        p = subprocess.run([sys.executable, "-c", code],
                           capture_output=True, text=True)
        final_src = os.path.join(tmp, "_snap.png")
        final_dst = os.path.abspath(os.path.join(out_dir, f"{scene}_final.png"))
        if want_final and os.path.exists(final_src):
            shutil.copyfile(final_src, final_dst)

    numbering = [ln[5:] for ln in p.stdout.splitlines() if ln.startswith("SNAP ")]
    saved = [ln[6:] for ln in p.stdout.splitlines() if ln.startswith("SAVED ")]
    missing = [k for k, path in targets.items() if not os.path.exists(path)]
    if p.returncode != 0 or not numbering or missing or (want_final and not os.path.exists(final_dst)):
        tail = "\n".join((p.stdout + p.stderr).strip().splitlines()[-15:])
        note = f" (no frame for {missing})" if missing else ""
        raise SystemExit(f"snapshot run failed{note}:\n{tail}")

    return numbering, saved, (final_dst if want_final else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene_file")
    ap.add_argument("scene")
    ap.add_argument("indices", nargs="*", type=int, help="animation indices to stop before")
    ap.add_argument("--list", action="store_true", help="number the play/wait calls, save nothing")
    ap.add_argument("--out", help="output directory (default: frames/ next to the scene file)")
    ap.add_argument("--hd", action="store_true", help="1080p frames instead of 480p")
    ap.add_argument("--res", metavar="WxH", help="explicit resolution, e.g. 672x600; overrides --hd")
    ap.add_argument("--quiet", action="store_true", help="print saved paths only, not the numbering")
    args = ap.parse_args()

    with open(args.scene_file, encoding="utf-8") as f:
        if not re.search(rf"^class {re.escape(args.scene)}\(", f.read(), re.M):
            # manimgl silently falls back to another scene when the name is unknown
            raise SystemExit(f"no `class {args.scene}(` in {args.scene_file}")

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.scene_file)), "frames")

    if args.list:
        indices = []
    else:
        indices = args.indices or [None]

    if args.res:
        if not re.fullmatch(r"\d+x\d+", args.res):
            raise SystemExit(f"--res wants WxH, got {args.res!r}")
        quality = ["-r", args.res]
    else:
        quality = ["--hd" if args.hd else "-l"]

    numbering, saved, final = run(args.scene_file, args.scene, indices,
                                  out, quality)

    if not args.quiet or args.list:
        print("\n".join(numbering))
    for line in saved:
        print(line.split(" ", 1)[1])
    if final:
        print(final)


if __name__ == "__main__":
    main()
