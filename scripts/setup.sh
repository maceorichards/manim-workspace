#!/bin/sh
# Workspace setup for macOS and Linux (Debian/Ubuntu apt; other distros get the package list).
#   sh scripts/setup.sh                  # asks before installing system packages
#   sh scripts/setup.sh --check          # only list what's missing; installs nothing
#   sh scripts/setup.sh --yes            # no prompts; steps that need a password are printed
#   sh scripts/setup.sh --agent claude   # also set up an agent (claude|codex|cursor|gemini|auto)
# System packages: uv, just, ffmpeg, CMU Serif font, LaTeX (checked, see below).
# Then: uv sync and scripts/post_setup.py (git hooks, agent adapter, doctor, smoke test).
set -eu
cd "$(dirname "$0")/.."

YES=0
CHECK=0
AGENT=""
while [ $# -gt 0 ]; do
    case "$1" in
    --yes) YES=1 ;;
    --check) CHECK=1 ;;
    --agent) AGENT="${2:?--agent needs a name}"; shift ;;
    --agent=*) AGENT="${1#--agent=}" ;;
    *) echo "unknown option: $1 (use --check, --yes, --agent <name>)"; exit 2 ;;
    esac
    shift
done

MISSING=""
have() { command -v "$1" >/dev/null 2>&1; }
need() { MISSING="$MISSING
  - $*"; }
ask() {
    [ "$YES" = 1 ] && return 0
    printf '%s [y/N] ' "$1"
    read -r reply
    case "$reply" in [yY]*) return 0 ;; *) return 1 ;; esac
}
run() { echo "+ $*"; "$@"; }
yourself() { echo "This step needs your password. Run it yourself, then re-run setup:"; echo "  $*"; }

OS=$(uname -s)
echo "== system packages ($OS)"

case "$OS" in
Darwin)
    if ! have brew; then
        if [ "$CHECK" = 1 ]; then need "Homebrew: https://brew.sh"; else echo "Homebrew is required: https://brew.sh"; exit 1; fi
    fi
    missing=""
    for tool in uv just ffmpeg; do have "$tool" || missing="$missing $tool"; done
    if [ -n "$missing" ]; then
        if [ "$CHECK" = 1 ]; then need "brew install$missing"
        elif ask "brew install$missing?"; then run brew install $missing; fi
    fi
    if ! fc-list 2>/dev/null | grep -q "CMU Serif" && ! ls ~/Library/Fonts/cmun* >/dev/null 2>&1 \
        && ! ls /Library/Fonts/cmun* >/dev/null 2>&1; then
        if [ "$CHECK" = 1 ]; then need "brew install --cask font-computer-modern  (CMU Serif)"
        elif ask "brew install --cask font-computer-modern (CMU Serif)?"; then
            run brew install --cask font-computer-modern
        fi
    fi
    if ! have latex; then
        if [ "$CHECK" = 1 ]; then
            need "brew install --cask mactex-no-gui  (LaTeX for Tex/TexText; ~5 GB; asks for your password)"
        else
            echo "No LaTeX found. Tex/TexText need it. Install one, then open a new terminal:"
            echo "  brew install --cask mactex-no-gui    # full TeX Live, ~5 GB, asks for your password"
        fi
    fi
    ;;
Linux)
    pkgs="ffmpeg fonts-cmu texlive texlive-latex-extra texlive-fonts-extra texlive-latex-recommended texlive-science tipa dvisvgm libgl1 libegl1"
    if have apt-get; then
        absent=""
        for p in $pkgs; do dpkg -s "$p" >/dev/null 2>&1 || absent="$absent $p"; done
        nojust=""; have just || nojust=" just"
        sudo=""; [ "$(id -u)" = 0 ] || sudo="sudo"
        if [ -n "$absent$nojust" ]; then
            if [ "$CHECK" = 1 ]; then need "$sudo apt-get install -y$absent$nojust  (asks for your password)"
            elif ask "apt-get install$absent$nojust?"; then
                if [ -z "$sudo" ] || sudo -n true 2>/dev/null; then
                    run $sudo apt-get update
                    [ -z "$absent" ] || run $sudo apt-get install -y $absent
                    [ -z "$nojust" ] || run $sudo apt-get install -y just || echo "just not in apt here: https://just.systems"
                else
                    yourself "sudo apt-get update && sudo apt-get install -y$absent$nojust"
                fi
            fi
        fi
    else
        echo "Not an apt system. Install the equivalents of: $pkgs just"
    fi
    if ! have uv; then
        if [ "$CHECK" = 1 ]; then need "uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
        elif ask "install uv (curl -LsSf https://astral.sh/uv/install.sh | sh)?"; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
            PATH="$HOME/.local/bin:$PATH"
        fi
    fi
    ;;
*)
    echo "Unsupported OS $OS; on Windows run: powershell -ExecutionPolicy Bypass -File scripts/setup.ps1"
    exit 1
    ;;
esac

if [ "$CHECK" = 1 ]; then
    if [ -n "$MISSING" ]; then echo "missing:$MISSING"; else echo "nothing missing"; fi
    echo "(--check installs nothing; uv sync, the agent adapter, doctor and the smoke test run on a full setup)"
    exit 0
fi

if ! have uv; then
    echo "uv is required: https://docs.astral.sh/uv/"; exit 1
fi

echo; echo "== python environment"
run uv sync
if [ -n "$AGENT" ]; then
    run uv run python scripts/post_setup.py --agent "$AGENT"
else
    run uv run python scripts/post_setup.py
fi
