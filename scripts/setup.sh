#!/bin/sh
# Workspace setup for macOS and Linux (Debian/Ubuntu apt; other distros get the package list).
#   sh scripts/setup.sh          # asks before installing system packages
#   sh scripts/setup.sh --yes    # no prompts
# System packages: uv, just, ffmpeg, CMU Serif font, LaTeX (checked, see below).
# Then: uv sync and scripts/post_setup.py (git hooks, guard, doctor, smoke test).
set -eu
cd "$(dirname "$0")/.."

YES=0
[ "${1:-}" = "--yes" ] && YES=1

have() { command -v "$1" >/dev/null 2>&1; }
ask() {
    [ "$YES" = 1 ] && return 0
    printf '%s [y/N] ' "$1"
    read -r reply
    case "$reply" in [yY]*) return 0 ;; *) return 1 ;; esac
}
run() { echo "+ $*"; "$@"; }

OS=$(uname -s)
echo "== system packages ($OS)"

case "$OS" in
Darwin)
    if ! have brew; then
        echo "Homebrew is required: https://brew.sh"; exit 1
    fi
    missing=""
    for tool in uv just ffmpeg; do have "$tool" || missing="$missing $tool"; done
    if [ -n "$missing" ] && ask "brew install$missing?"; then
        run brew install $missing
    fi
    if ! fc-list 2>/dev/null | grep -q "CMU Serif" && ! ls ~/Library/Fonts/cmun* >/dev/null 2>&1 \
        && ! ls /Library/Fonts/cmun* >/dev/null 2>&1; then
        if ask "brew install --cask font-computer-modern (CMU Serif)?"; then
            run brew install --cask font-computer-modern
        fi
    fi
    if ! have latex; then
        echo "No LaTeX found. Tex/TexText need it. Install one, then open a new terminal:"
        echo "  brew install --cask mactex-no-gui    # full TeX Live, ~5 GB, nothing else to add"
    fi
    ;;
Linux)
    pkgs="ffmpeg fonts-cmu texlive texlive-latex-extra texlive-fonts-extra texlive-latex-recommended texlive-science tipa dvisvgm libgl1 libegl1"
    if have apt-get; then
        sudo=""; [ "$(id -u)" = 0 ] || sudo="sudo"
        if ask "apt-get install $pkgs?"; then
            run $sudo apt-get update
            run $sudo apt-get install -y $pkgs
            have just || run $sudo apt-get install -y just || echo "just not in apt here: https://just.systems"
        fi
    else
        echo "Not an apt system. Install the equivalents of: $pkgs just"
    fi
    if ! have uv; then
        if ask "install uv (curl -LsSf https://astral.sh/uv/install.sh | sh)?"; then
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

if ! have uv; then
    echo "uv is required: https://docs.astral.sh/uv/"; exit 1
fi

echo; echo "== python environment"
run uv sync
run uv run python scripts/post_setup.py
