"""ManimGL environment doctor -- stdlib only, safe to run before manimgl is installed.

Checks the pieces that fail silently or with misleading errors, and can write a
custom_config.yml that encodes the fixes:

    python doctor.py                         # report only
    python doctor.py --font "Malgun Gothic"  # also check a Pango font by name
    python doctor.py --write-config          # write ./custom_config.yml (refuses to overwrite)
    python doctor.py --write-config --force

Exit code 1 when anything is marked FAIL.
"""

import argparse
import importlib
import importlib.util
import os
import platform
import shutil
import subprocess
import sys
import warnings

OK, WARN, FAIL = "ok  ", "WARN", "FAIL"
CJK_FONTS = {
    "Windows": "Malgun Gothic",
    "Darwin": "Apple SD Gothic Neo",
    "Linux": "Noto Sans CJK KR",
}


def run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def check_python(rows, fixes):
    v = sys.version_info
    rows.append((OK, f"python {v.major}.{v.minor}.{v.micro} at {sys.executable}"))
    if v >= (3, 13) and importlib.util.find_spec("audioop") is None:
        rows.append((FAIL, "audioop missing (removed in 3.13); manimgl fails at import"))
        fixes.append("pip install audioop-lts")


def check_manimlib(rows, fixes):
    warnings.filterwarnings("ignore")  # manimlib's pkg_resources deprecation notice
    argv, sys.argv = sys.argv, sys.argv[:1]  # manimlib parses sys.argv on import
    try:
        m = importlib.import_module("manimlib")
    except ImportError as e:
        if e.name == "manimlib":
            rows.append((FAIL, "manimlib not importable in this interpreter"))
            fixes.append("pip install manimgl   # not 'manim', that is Community Edition")
        elif e.name == "pkg_resources":
            rows.append((FAIL, "pkg_resources missing: setuptools>=81 dropped it and manimlib 1.7.2 imports it at startup"))
            fixes.append('pip install "setuptools<81"')
        elif "DLL load failed" in str(e):
            rows.append((FAIL, f"a compiled extension is blocked from loading: {e}"))
            fixes.append("Windows Smart App Control can reject a wheel's .pyd; another build usually passes, "
                         "e.g. pip install --force-reinstall scipy==1.16.2")
        else:
            rows.append((FAIL, f"manimlib import failed: {e}"))
        return
    finally:
        sys.argv = argv
    rows.append((OK, f"manimlib {getattr(m, '__version__', '?')} at {os.path.dirname(m.__file__)}"))
    if not shutil.which("manimgl"):
        rows.append((WARN, "manimgl script not on PATH (pip's Scripts dir); run `python -m manimlib` instead"))
    if importlib.util.find_spec("manim") is not None:
        rows.append((WARN, "Manim CE ('manim') is also installed; keep imports as 'from manimlib import *'"))


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe, True
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe(), False
    except Exception:
        return None, False


def check_ffmpeg(rows, fixes):
    """Returns the bundled ffmpeg path when it must go into custom_config.yml, else None."""
    exe, on_path = find_ffmpeg()
    if not exe:
        rows.append((FAIL, "ffmpeg not found on PATH and imageio-ffmpeg not installed; -w cannot write files"))
        fixes.append("pip install imageio-ffmpeg   # then --write-config points ffmpeg_bin at its binary")
    elif on_path:
        rows.append((OK, f"ffmpeg on PATH: {exe}"))
    else:
        rows.append((WARN, f"ffmpeg not on PATH; imageio-ffmpeg bundled binary: {exe}"))
    return exe if exe and not on_path else None


def check_latex(rows, fixes):
    """Returns True when the tex template must be switched to xelatex (MiKTeX)."""
    latex, xelatex, dvisvgm = (shutil.which(x) for x in ("latex", "xelatex", "dvisvgm"))
    if not latex and not xelatex:
        rows.append((WARN, "no LaTeX on PATH; Tex/TexText/Brace unavailable, Text still works"))
        return False
    rows.append((OK, f"latex: {latex or '-'}   xelatex: {xelatex or '-'}"))
    if not dvisvgm:
        rows.append((FAIL, "dvisvgm not on PATH; manimlib needs it to turn dvi into svg"))
        fixes.append("tlmgr install dvisvgm   # or install it through the MiKTeX console")
    is_miktex = "MiKTeX" in run([latex or xelatex, "--version"])
    if is_miktex:
        if xelatex:
            rows.append((WARN, "MiKTeX: latex.exe rejects manimlib's -no-pdf flag; use tex.template: empty_ctex "
                               "and pass amsmath via additional_preamble (see cli-config.md)"))
        else:
            rows.append((FAIL, "MiKTeX without xelatex; every Tex() will fail"))
            fixes.append("install the xelatex package through the MiKTeX console")
    return is_miktex


def list_fonts():
    try:
        import manimpango  # type: ignore

        return set(manimpango.list_fonts())
    except Exception:
        pass
    out = run(["fc-list", ":", "family"])
    if out:
        return {f.strip() for line in out.splitlines() for f in line.split(",")}
    if platform.system() == "Windows":
        # ponytail: file-name heuristic, enough for the CJK default; manimpango is the real answer
        fonts_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
        names = {f.lower() for f in os.listdir(fonts_dir)} if os.path.isdir(fonts_dir) else set()
        return {"Malgun Gothic"} if "malgun.ttf" in names else set()
    return None


def check_font(rows, font):
    fonts = list_fonts()
    if fonts is None:
        rows.append((WARN, f"cannot enumerate fonts here; verify '{font}' manually (Pango substitutes silently)"))
    elif font in fonts:
        rows.append((OK, f"font '{font}' is installed"))
    else:
        rows.append((WARN, f"font '{font}' not found; Pango will substitute another font without an error"))


def check_config(rows, fixes):
    path = os.path.join(os.getcwd(), "custom_config.yml")
    if not os.path.exists(path):
        rows.append((WARN, "no custom_config.yml in cwd (run with --write-config to create one)"))
        return
    with open(path, "rb") as f:
        raw = f.read()
    if any(b > 127 for b in raw):
        rows.append((FAIL, "custom_config.yml contains non-ASCII bytes; crashes on cp949 locales"))
        fixes.append("make custom_config.yml ASCII-only (comments included)")
    else:
        rows.append((OK, "custom_config.yml is ASCII-only"))
    for line in raw.decode("ascii", "replace").splitlines():
        if line.strip().startswith("ffmpeg_bin:"):
            bin_path = line.split(":", 1)[1].strip().strip("\"'")
            if bin_path != "ffmpeg" and not os.path.exists(bin_path):
                rows.append((FAIL, f"ffmpeg_bin points at a missing file: {bin_path}"))
                fixes.append("rerun with --write-config --force to refresh ffmpeg_bin")


def write_config(ffmpeg_bin, use_xelatex, force):
    path = os.path.join(os.getcwd(), "custom_config.yml")
    if os.path.exists(path) and not force:
        print(f"\n{path} exists; pass --force to overwrite")
        return
    lines = ["# generated by doctor.py -- keep ASCII only (manimlib reads it with the locale codec)"]
    if ffmpeg_bin:
        lines += ["file_writer:", f'  ffmpeg_bin: "{ffmpeg_bin.replace(os.sep, "/")}"']
    if use_xelatex:
        lines += ["# MiKTeX latex.exe rejects -no-pdf; empty_ctex is xelatex with an empty preamble.",
                  "# Add amsmath per Tex() call: Tex(s, additional_preamble=r'\\usepackage{amsmath}')",
                  "tex:", '  template: "empty_ctex"']
    lines += ["camera:", '  background_color: "#000000"', "  fps: 30"]
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", default=CJK_FONTS.get(platform.system(), "Noto Sans CJK KR"),
                    help="Pango font name to check (default: platform CJK font)")
    ap.add_argument("--write-config", action="store_true", help="write ./custom_config.yml with the fixes")
    ap.add_argument("--force", action="store_true", help="overwrite an existing custom_config.yml")
    args = ap.parse_args()

    rows, fixes = [], []
    check_python(rows, fixes)
    check_manimlib(rows, fixes)
    ffmpeg_bin = check_ffmpeg(rows, fixes)
    use_xelatex = check_latex(rows, fixes)
    check_font(rows, args.font)
    check_config(rows, fixes)

    for status, msg in rows:
        print(f"[{status}] {msg}")
    if fixes:
        print("\nfixes:")
        for fx in fixes:
            print(f"  {fx}")
    if args.write_config:
        write_config(ffmpeg_bin, use_xelatex, args.force)
    sys.exit(1 if any(s == FAIL for s, _ in rows) else 0)


if __name__ == "__main__":
    main()
