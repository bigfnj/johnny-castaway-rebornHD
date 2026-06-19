# Build Johnny Reborn HD for Web (Emscripten) on Windows.
#
# Configuration (all optional — sensible defaults provided):
#
#   $env:EMSDK          — path to the emsdk install (required; no default on first run)
#                         Example: setx EMSDK "C:\emsdk"
#
#   $env:JCR_BUILD_DIR  — where to put the build output.
#                         Default: <this-script's-parent>\build_web
#
# Usage (from any directory):
#   powershell -ExecutionPolicy Bypass -File .\build_web.ps1
#
# Troubleshooting:
#   If emsdk is not found, set EMSDK:
#     $env:EMSDK = "C:\path\to\emsdk"
#     .\build_web.ps1

$ErrorActionPreference = "Stop"

# --- Resolve emsdk location ---------------------------------------------------
$emsdk = $env:EMSDK

if (-not $emsdk -or -not (Test-Path $emsdk)) {
    # Legacy fallback — preserved so existing workstations still work
    $legacy = "C:\@_WorkingFolder\@_Anthropic\emsdk"
    if (Test-Path $legacy) {
        Write-Host "EMSDK env var not set; falling back to legacy path: $legacy" -ForegroundColor Yellow
        $emsdk = $legacy
    } else {
        Write-Error @"
Could not locate emsdk.

Please set the EMSDK environment variable to your emsdk install directory:
  `$env:EMSDK = "C:\path\to\emsdk"   # in this shell
  setx EMSDK "C:\path\to\emsdk"      # persist for future shells

Then re-run this script.
"@
        exit 1
    }
}

if (-not (Test-Path (Join-Path $emsdk "emsdk_env.ps1")) -and
    -not (Test-Path (Join-Path $emsdk ".emscripten"))) {
    Write-Error "Path '$emsdk' does not look like an emsdk install (no emsdk_env.ps1 or .emscripten)."
    exit 1
}

$env:EM_CONFIG = Join-Path $emsdk ".emscripten"

# Assemble PATH entries that every emsdk install exposes. Unusual vendored
# subdirectories (specific node/python versions) are included where present.
$pathParts = @(
    (Join-Path $emsdk "upstream\emscripten"),
    (Join-Path $emsdk "upstream\bin")
)

# Include vendored node / python if the user hasn't installed their own
$nodeDirs = Get-ChildItem -Path (Join-Path $emsdk "node") -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
if ($nodeDirs) { $pathParts += (Join-Path $nodeDirs[0].FullName "bin") }

$pythonDirs = Get-ChildItem -Path (Join-Path $emsdk "python") -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
if ($pythonDirs) { $pathParts += $pythonDirs[0].FullName }

# Include CMake + WinGet links on PATH (best effort)
$pathParts += "C:\Program Files\CMake\bin"
if ($env:LOCALAPPDATA) { $pathParts += "$env:LOCALAPPDATA\Microsoft\WinGet\Links" }

$env:PATH = ($pathParts -join ";") + ";" + $env:PATH

# --- Resolve repo root (one level up from this script) and build directory ---
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot  = Split-Path -Parent $scriptDir

$buildDir = $env:JCR_BUILD_DIR
if (-not $buildDir) {
    $buildDir = Join-Path $repoRoot "build_web"
}

if (-not (Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
}

Write-Host "emsdk     : $emsdk"
Write-Host "Repo root : $repoRoot"
Write-Host "Build dir : $buildDir"
Write-Host ""

# --- Clean cmake cache --------------------------------------------------------
Remove-Item (Join-Path $buildDir "CMakeCache.txt") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $buildDir "CMakeFiles") -Recurse -Force -ErrorAction SilentlyContinue

Set-Location $buildDir

# --- Configure ----------------------------------------------------------------
# (--preload-file is set in CMakeLists.txt linker flags)
& emcmake cmake $repoRoot -DCMAKE_BUILD_TYPE=Release
if ($LASTEXITCODE -ne 0) { Write-Error "CMake configure failed"; exit 1 }

# --- Build --------------------------------------------------------------------
& emmake cmake --build .
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit 1 }

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Get-ChildItem $buildDir -File -Filter "jc_reborn.*" |
    Where-Object { $_.DirectoryName -eq $buildDir } |
    ForEach-Object { Write-Host "  $($_.Name) ($($_.Length) bytes)" }
