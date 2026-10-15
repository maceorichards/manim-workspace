# Workspace setup for Windows 10/11 (winget).
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1                 # asks before installing
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -Check          # list what's missing only
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -Yes            # no prompts
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -Agent claude   # also set up an agent
# System packages: Git (Git Bash runs agent hooks), uv, just, ffmpeg, MiKTeX, CMU Serif.
# Then: uv sync and scripts/post_setup.py (git hooks, agent adapter, doctor, smoke test).
param([switch]$Yes, [switch]$Check, [string]$Agent = "")
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
$Missing = @()
function Ask($question) {
    if ($Check) { $script:Missing += $question; return $false }
    if ($Yes) { return $true }
    (Read-Host "$question [y/N]") -match '^[yY]'
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Host "== system packages (Windows)"
if (-not (Have winget)) {
    Write-Host "winget is required (App Installer from the Microsoft Store)."; exit 1
}

$packages = [ordered]@{
    git = "Git.Git"; uv = "astral-sh.uv"; just = "Casey.Just"; ffmpeg = "Gyan.FFmpeg"; latex = "MiKTeX.MiKTeX"
}
foreach ($cmd in $packages.Keys) {
    if (-not (Have $cmd) -and (Ask "winget install $($packages[$cmd])?")) {
        winget install --id $packages[$cmd] -e --accept-source-agreements --accept-package-agreements
    }
}
Refresh-Path

if (-not $Check -and (Have initexmf)) {
    # Let MiKTeX fetch missing LaTeX packages on first use instead of prompting mid-render.
    initexmf --set-config-value "[MPM]AutoInstall=1" | Out-Null
}

# CMU Serif (Computer Modern Unicode), installed per user; no admin rights needed.
$fontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$haveFont = (Test-Path "$fontDir\cmunrm.otf") -or (Test-Path "$env:WINDIR\Fonts\cmunrm.otf")
if (-not $haveFont -and (Ask "Download and install the CMU Serif font for this user?")) {
    $tmp = Join-Path $env:TEMP "cm-unicode"
    Invoke-WebRequest "https://mirrors.ctan.org/fonts/cm-unicode.zip" -OutFile "$tmp.zip"
    Expand-Archive "$tmp.zip" -DestinationPath $tmp -Force
    New-Item -ItemType Directory -Force $fontDir | Out-Null
    $reg = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    Get-ChildItem $tmp -Recurse -Filter "cmun*.otf" | ForEach-Object {
        Copy-Item $_.FullName $fontDir -Force
        New-ItemProperty -Path $reg -Name "$($_.BaseName) (OpenType)" `
            -Value (Join-Path $fontDir $_.Name) -PropertyType String -Force | Out-Null
    }
    Write-Host "Installed CMU fonts. Open a new terminal (or sign out and in) if doctor can't see them."
}

if ($Check) {
    if ($Missing) { Write-Host "missing:"; $Missing | ForEach-Object { Write-Host "  - $_" } }
    else { Write-Host "nothing missing" }
    Write-Host "(-Check installs nothing; winget may show a Windows permission prompt on a full setup)"
    exit 0
}

if (-not (Have uv)) { Write-Host "uv is required: https://docs.astral.sh/uv/"; exit 1 }

Write-Host "`n== python environment"
uv sync
if ($LASTEXITCODE) { exit $LASTEXITCODE }
if ($Agent) { uv run python scripts/post_setup.py --agent $Agent } else { uv run python scripts/post_setup.py }
exit $LASTEXITCODE
