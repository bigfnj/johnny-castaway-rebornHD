#Requires -Version 5.1
<#
    THE gate: configure, build, smoke, regression, one exit code.

    Run this before committing. It exists because this repository had no way to
    answer "is it still working" at all: no tests, no CI, and three of its four
    platforms unbuilt since a tree reorganisation. A build that merely compiles
    proved nothing here, since the binary could not even locate its own data
    archive and therefore died on startup in every configuration.

    Order is deliberate. The build must succeed before anything can run; smoke
    proves the binary starts, does real work and tears down cleanly; regression
    proves the decoders still produce byte-identical output. Smoke first because
    a binary that cannot start makes a regression diff meaningless noise.
#>
[CmdletBinding()]
param(
    [ValidateSet('Release', 'Debug')]
    [string]$Config = 'Release',

    # Skip the configure+build and test whatever is already there.
    [switch]$NoBuild,

    # Smoke only, for a fast inner loop. The gate is the full run.
    [switch]$SmokeOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repo  = $PSScriptRoot
$build = Join-Path $repo 'build'
$exe   = Join-Path $build "$Config\jc_reborn.exe"
$failed = $false

function Write-Step { param([string]$Msg) Write-Host "`n=== $Msg ===" -ForegroundColor Cyan }

Write-Host "=== gate: johnny-castaway-rebornHD ($Config) ===" -ForegroundColor Cyan

if (-not $NoBuild) {
    Write-Step 'configure + build'

    # WHICH cmake runs is decided by PATH order, silently, and that broke a run.
    #
    # There are two on this box: 4.3.1 under Program Files, which knows the
    # "Visual Studio 18 2026" generator, and an older 3.31.6 bundled with another
    # tool, which does not. A shell resolving the older one first cannot open a
    # cache the newer one wrote, and says
    #     Error: could not create CMAKE_GENERATOR "Visual Studio 18 2026"
    # which reads as a broken toolchain rather than a PATH accident. It cost real
    # time once.
    #
    # So the cache decides: it records the cmake that wrote it, and that one is
    # by definition able to read it back.
    $cmake = 'cmake'
    $cache = Join-Path $build 'CMakeCache.txt'
    if (Test-Path -LiteralPath $cache) {
        $rec = @(Select-String -LiteralPath $cache -Pattern '^CMAKE_COMMAND:INTERNAL=(.+)$')
        if ($rec.Count -and (Test-Path -LiteralPath $rec[0].Matches[0].Groups[1].Value)) {
            $cmake = $rec[0].Matches[0].Groups[1].Value
        }
    }
    #  Compare the RESOLVED paths. CMakeCache.txt stores forward slashes and
    #  Get-Command returns backslashes, so a plain string compare called the same
    #  file a mismatch and printed this note on every single run - a warning that
    #  is always wrong is a warning people learn to skip past.
    $onPath = (Get-Command cmake -ErrorAction SilentlyContinue).Source
    $sameFile = $false
    if ($onPath -and $cmake -ne 'cmake') {
        $sameFile = ([IO.Path]::GetFullPath($cmake) -eq [IO.Path]::GetFullPath($onPath))
    }
    if ($cmake -ne 'cmake' -and $onPath -and -not $sameFile) {
        Write-Host "NOTE using the cmake that configured this build tree, not the one on PATH" -ForegroundColor Yellow
        Write-Host "     cache: $cmake" -ForegroundColor Yellow
        Write-Host "     PATH : $onPath" -ForegroundColor Yellow
    }

    # The generator is NOT pinned. CMake 4.3.1 here defaults to "Visual Studio 18
    # 2026", which matches the v145 toolset the hand-maintained vs/ projects pin,
    # so the default is already the right answer and hard-coding it would break
    # the moment the toolchain moves.
    if (-not (Test-Path -LiteralPath $cache)) {
        & $cmake -S $repo -B $build -A x64 | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Host 'FAIL cmake configure' -ForegroundColor Red; exit 1 }
    }

    $out = & $cmake --build $build --config $Config 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'FAIL build' -ForegroundColor Red
        $out | Select-Object -Last 25 | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
        exit 1
    }

    # Warnings are surfaced, not hidden. /W4 is on and this codebase is old
    # enough that new warnings are worth seeing even when they are not fatal.
    $warn = @($out | Select-String -Pattern ': warning ')
    if ($warn.Count) {
        Write-Host ("WARN {0} compiler warning(s)" -f $warn.Count) -ForegroundColor Yellow
        $warn | Select-Object -First 8 | ForEach-Object { Write-Host "     $_" -ForegroundColor Yellow }
    }
    else {
        Write-Host 'OK   build clean, no warnings' -ForegroundColor Green
    }
}

if (-not (Test-Path -LiteralPath $exe)) {
    Write-Host "FAIL no binary at $exe" -ForegroundColor Red
    exit 1
}

# The archive must sit beside the binary. Asserted rather than assumed, because
# its absence is the exact failure this project shipped with: the build
# succeeded and the program died on startup.
$zip = Join-Path (Split-Path $exe -Parent) 'scrantic_data.zip'
if (-not (Test-Path -LiteralPath $zip)) {
    Write-Host "FAIL scrantic_data.zip is not next to the binary ($zip)" -ForegroundColor Red
    Write-Host '     build the executable target to run its jc_runtime_data prerequisite' -ForegroundColor Red
    exit 1
}

$sourceZip = Join-Path $repo 'assets\scrantic_data.zip'
if ((Get-FileHash -LiteralPath $sourceZip).Hash -ne (Get-FileHash -LiteralPath $zip).Hash) {
    Write-Host "FAIL runtime archive differs from assets/scrantic_data.zip: $zip" -ForegroundColor Red
    Write-Host '     run the normal build to refresh art-only asset changes' -ForegroundColor Red
    exit 1
}

Write-Step 'smoke'
& powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $repo 'tests\Invoke-SmokeTests.ps1') -Exe $exe
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GATE FAILED: smoke failed; regression was not run' -ForegroundColor Red
    exit 1
}

# The /p preview is the one screensaver path no command line can reach: Windows
# hands over the HWND of the little monitor in the Settings dialog and expects a
# CHILD window. The classic broken screensaver still "runs" - it just goes
# fullscreen and steals the foreground while the user is in Settings, which is
# precisely what this engine did while parseArgs was discarding unknown tokens.
# So it gets a real parent window and an assertion that no top-level window
# appeared. Skipped, loudly, where no .scr was built.
#
# The same script also covers the focus rules, which need the CONSOLE build to
# run the engine both with and without /s, so both binaries are passed in.
$scr = Join-Path (Split-Path $exe -Parent) 'jc_reborn.scr'
if (Test-Path -LiteralPath $scr) {
    Write-Step 'screensaver behaviour (/p preview, and the focus rules)'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $repo 'tests\Test-ScreensaverPreview.ps1') -Scr $scr -Exe $exe
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'GATE FAILED: screensaver smoke failed; regression was not run' -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Step 'screensaver preview'
    Write-Host "SKIP no jc_reborn.scr at $scr - the /p path is UNTESTED in this run" -ForegroundColor Yellow
}

Write-Step 'art-style smoke'
& powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $repo 'tests\Invoke-ArtStyleTests.ps1') -Exe $exe -Phase Smoke
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GATE FAILED: art-style smoke failed; regression was not run' -ForegroundColor Red
    exit 1
}

Write-Step 'wave renderer smoke'
& python -B (Join-Path $repo 'tests\test_wave_renderer.py') --exe $exe --archive $sourceZip --phase smoke
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GATE FAILED: wave smoke failed; regression was not run' -ForegroundColor Red
    exit 1
}

Write-Step 'palm renderer smoke'
$palmDriver = Join-Path (Split-Path $exe -Parent) 'jc_palm_test.exe'
& python -B (Join-Path $repo 'tests\test_palm_renderer.py') --driver $palmDriver --archive $sourceZip --phase smoke
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GATE FAILED: palm smoke failed; regression was not run' -ForegroundColor Red
    exit 1
}

Write-Step 'RESOURCE decoder smoke'
$decoderProbe = Join-Path (Split-Path $exe -Parent) 'jc_uncompress_test.exe'
& python -B (Join-Path $repo 'tests\test_uncompress.py') --probe $decoderProbe --engine $exe --phase smoke
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GATE FAILED: decoder smoke failed; regression was not run' -ForegroundColor Red
    exit 1
}

Write-Step 'engine ownership smoke'
$lifecycleProbe = Join-Path (Split-Path $exe -Parent) 'jc_lifecycle_test.exe'
& python -B (Join-Path $repo 'tests\test_lifecycle.py') --exe $lifecycleProbe --phase smoke
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GATE FAILED: lifecycle smoke failed; regression was not run' -ForegroundColor Red
    exit 1
}

Write-Step 'platform constructor smoke'
$platformProbe = Join-Path (Split-Path $exe -Parent) 'jc_platform_alloc_test.exe'
& powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File (Join-Path $repo 'tests\Test-PlatformAlloc.ps1') -Exe $platformProbe -Phase Smoke
if ($LASTEXITCODE -ne 0) {
    Write-Host 'GATE FAILED: platform smoke failed; regression was not run' -ForegroundColor Red
    exit 1
}

if (-not $SmokeOnly) {
    Write-Step 'regression (platform constructors and failures)'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $repo 'tests\Test-PlatformAlloc.ps1') -Exe $platformProbe -Phase Regression
    if ($LASTEXITCODE -ne 0) { $failed = $true }

    Write-Step 'regression (RESOURCE decoder completeness)'
    & python -B (Join-Path $repo 'tests\test_uncompress.py') --probe $decoderProbe --engine $exe
    if ($LASTEXITCODE -ne 0) { $failed = $true }

    Write-Step 'regression (engine ownership and cleanup)'
    & python -B (Join-Path $repo 'tests\test_lifecycle.py') --exe $lifecycleProbe
    if ($LASTEXITCODE -ne 0) { $failed = $true }

    Write-Step 'regression (art-style pixels and configuration)'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $repo 'tests\Invoke-ArtStyleTests.ps1') -Exe $exe -Phase Regression
    if ($LASTEXITCODE -ne 0) { $failed = $true }

    Write-Step 'regression (wave alpha, restoration and fallback)'
    & python -B (Join-Path $repo 'tests\test_wave_renderer.py') --exe $exe --archive $sourceZip
    if ($LASTEXITCODE -ne 0) { $failed = $true }

    Write-Step 'regression (palm alpha, clipping and fallback)'
    & python -B (Join-Path $repo 'tests\test_palm_renderer.py') --driver $palmDriver --archive $sourceZip
    if ($LASTEXITCODE -ne 0) { $failed = $true }

    Write-Step 'regression (art authoring tools)'
    $authoringSuite = Join-Path $repo 'tests\test_art_tools.py'
    if (-not (Test-Path -LiteralPath $authoringSuite)) {
        Write-Host "FAIL missing art authoring test suite: $authoringSuite" -ForegroundColor Red
        $failed = $true
    }
    else {
        & python -B -m unittest discover -s (Join-Path $repo 'tests') -p test_art_tools.py -v
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    }

    Write-Step 'regression (golden dump corpus)'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $repo 'tests\Invoke-DumpRegression.ps1') -Exe $exe
    if ($LASTEXITCODE -ne 0) { $failed = $true }
}

Write-Host ''
if ($failed) {
    Write-Host 'GATE FAILED' -ForegroundColor Red
    exit 1
}
Write-Host 'gate passed' -ForegroundColor Green
exit 0
