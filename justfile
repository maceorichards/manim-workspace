# Task runner for the workspace. `just` lists recipes; run from anywhere inside the repo
# (recipes run at the repo root, so custom_config.yml is always picked up).
# Topic paths are <area>/<topic>, e.g. `just snap neural-circuits/firing_rate FiringRate 3 7`.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

snapshot := "tools/snapshot.py"
doctor := "tools/doctor.py"

# List recipes
default:
    @just --list --unsorted

# Install system deps (asks first), uv sync, git hooks, agent adapter, then doctor + smoke test
[unix]
setup agent="":
    sh scripts/setup.sh {{ if agent != "" { "--agent " + agent } else { "" } }}

# Install system deps (asks first), uv sync, git hooks, agent adapter, then doctor + smoke test
[windows]
setup agent="":
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1 {{ if agent != "" { "-Agent " + agent } else { "" } }}

# Check ffmpeg, LaTeX, fonts, and config
doctor font="CMU Serif":
    uv run python {{doctor}} --font "{{font}}"

# Start a movie: copy templates/topic to <area>/<topic>
new area topic scene="":
    uv run python scripts/new_topic.py {{area}} {{topic}} {{ if scene != "" { "--scene " + scene } else { "" } }}

# Run a topic's __main__ asserts (pure functions only)
check topic:
    uv run python {{topic}}/main.py

# Number every self.play / self.wait in a scene
list topic scene:
    uv run python {{snapshot}} {{topic}}/main.py {{scene}} --list

# PNGs after the given animation indices (none: final frame) -> <topic>/frames/
snap topic scene *indices:
    uv run python {{snapshot}} {{topic}}/main.py {{scene}} {{indices}}

# Render to <topic>/videos/ at low (480p), hd (1080p), or uhd (4K)
render topic scene quality="low":
    uv run manimgl {{topic}}/main.py {{scene}} -w {{ if quality == "hd" { "--hd" } else if quality == "uhd" { "--uhd" } else { "-l" } }}

# Run every topic's and area module's asserts plus the agent-adapter selftest (what CI runs)
check-all:
    uv run python scripts/check_all.py

# Lint (correctness rules only; see pyproject.toml)
lint:
    uv run ruff check .

# Reformat files with ruff (opt-in; not enforced)
fmt *paths=".":
    uv run ruff format {{paths}}

# Agent adapters: status (no args), enable one (claude|codex|cursor|gemini|auto), or --remove one
agent *args:
    uv run python scripts/agents.py {{args}}

# Regenerate every enabled agent's adapter (read-only rules from SOURCES, CLAUDE.md shims)
agent-sync:
    uv run python scripts/agents.py --sync

# Show or change this machine's style override (style.local.yml); see the set-style-default skill
style *args="--show":
    uv run python scripts/set_style.py {{args}}
