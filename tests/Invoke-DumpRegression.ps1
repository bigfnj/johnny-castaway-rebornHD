#Requires -Version 5.1
<#
    Golden-output regression for `jc_reborn dump`.

    WHY THIS IS THE ORACLE. `dump` is the only engine entry point that is both
    deterministic and headless: jc_reborn.c dispatches it WITHOUT calling
    graphicsInit(), and nothing on the path touches rand(). It decodes every
    BMP, SCR, ADS and TTM resource in the archive, so a single run exercises
    zipvfs, miniz inflate, the LZW/RLE decoders, resource parsing, the palette
    and both bytecode disassemblers. 2,452 files, ~11.9 MB.

    The corpus is stored as SHA-256 hashes rather than 11.9 MB of XPM, so the
    repository carries a ~200 KB manifest instead of a second copy of the art.

    Because it needs no display, the SAME check runs inside a Linux container.
    Any hash that differs between Windows and Linux is a real cross-platform
    decode defect, not a rendering difference. That diff is the strongest
    regression signal this project has.
#>
[CmdletBinding()]
param(
    # The binary under test.
    [string]$Exe,

    # Write the manifest instead of comparing against it. Use only when a
    # change to decoder output is INTENDED, and say so in the commit message.
    [switch]$Update,

    # Defaulted in the BODY, not here: under Windows PowerShell 5.1 $PSScriptRoot
    # is empty inside a param() default block, so the Join-Path throws before the
    # script starts.
    [string]$Golden
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Golden) { $Golden = Join-Path $PSScriptRoot 'golden-dump.sha256' }

if (-not $Exe) {
    $repo = Split-Path $PSScriptRoot -Parent
    foreach ($c in @('build\Release\jc_reborn.exe', 'build\Debug\jc_reborn.exe')) {
        $p = Join-Path $repo $c
        if (Test-Path -LiteralPath $p) { $Exe = $p; break }
    }
}
if (-not $Exe -or -not (Test-Path -LiteralPath $Exe)) {
    Write-Host "FAIL no jc_reborn binary found (pass -Exe)" -ForegroundColor Red
    exit 1
}

# Dump into a fresh scratch directory. `dump` writes to ./dump/ relative to the
# CURRENT directory, so the working directory is the only way to steer it, and
# a stale ./dump/ from a previous run would silently mask a deleted resource.
$work = Join-Path ([IO.Path]::GetTempPath()) ("jcr-dump-" + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $work | Out-Null

try {
    Push-Location $work
    $out = & $Exe dump 2>&1
    $code = $LASTEXITCODE
    Pop-Location

    if ($code -ne 0) {
        Write-Host "FAIL dump exited $code" -ForegroundColor Red
        $out | Select-Object -Last 15 | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
        exit 1
    }

    $dumpDir = Join-Path $work 'dump'
    if (-not (Test-Path -LiteralPath $dumpDir)) {
        Write-Host "FAIL dump produced no output directory" -ForegroundColor Red
        exit 1
    }

    # Relative path + hash, sorted, forward slashes. All three matter: sorting
    # makes the manifest stable across filesystem enumeration order, and the
    # separator normalisation is what lets the Linux container compare against
    # a manifest generated on Windows.
    $prefix = $dumpDir.TrimEnd('\', '/').Length + 1
    $rows = Get-ChildItem -Recurse -File -LiteralPath $dumpDir | ForEach-Object {
        $rel = $_.FullName.Substring($prefix).Replace('\', '/')
        '{0}  {1}' -f (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant(), $rel
    } | Sort-Object

    # A FLOOR. An empty or near-empty dump must never be reported as "matches";
    # a run that decoded nothing would otherwise agree with itself.
    if (@($rows).Count -lt 2000) {
        Write-Host ("FAIL dump produced only {0} file(s) - expected ~2452; the run decoded almost nothing" -f @($rows).Count) -ForegroundColor Red
        exit 1
    }

    if ($Update) {
        # LF, WRITTEN EXPLICITLY. Set-Content emits CRLF on Windows PowerShell,
        # which put a trailing \r on all 2,452 lines and made every one of them
        # differ from the same manifest read in a Linux container - a total
        # mismatch that looked exactly like a catastrophic decoder divergence and
        # was purely this file's line endings. The manifest has to be as
        # platform-neutral as the dump it describes.
        [IO.File]::WriteAllText($Golden, (($rows -join "`n") + "`n"),
                                (New-Object System.Text.ASCIIEncoding))
        Write-Host ("wrote {0} hashes to {1}" -f @($rows).Count, $Golden) -ForegroundColor Yellow
        exit 0
    }

    if (-not (Test-Path -LiteralPath $Golden)) {
        Write-Host "FAIL no golden manifest at $Golden (generate with -Update)" -ForegroundColor Red
        exit 1
    }

    $expected = @(Get-Content -LiteralPath $Golden | Where-Object { $_.Trim() })

    $expMap = @{}
    foreach ($line in $expected) {
        $h, $p = $line -split '  ', 2
        if ($p) { $expMap[$p] = $h }
    }
    $gotMap = @{}
    foreach ($line in $rows) {
        $h, $p = $line -split '  ', 2
        if ($p) { $gotMap[$p] = $h }
    }

    $missing = @($expMap.Keys | Where-Object { -not $gotMap.ContainsKey($_) } | Sort-Object)
    $added   = @($gotMap.Keys | Where-Object { -not $expMap.ContainsKey($_) } | Sort-Object)
    $changed = @($expMap.Keys | Where-Object { $gotMap.ContainsKey($_) -and $gotMap[$_] -ne $expMap[$_] } | Sort-Object)

    $bad = $missing.Count + $added.Count + $changed.Count
    if ($bad -eq 0) {
        Write-Host ("OK   dump regression: {0} file(s) byte-identical to the golden corpus" -f @($rows).Count) -ForegroundColor Green
        exit 0
    }

    Write-Host ("FAIL dump regression: {0} missing, {1} added, {2} changed" -f
                $missing.Count, $added.Count, $changed.Count) -ForegroundColor Red
    foreach ($m in ($missing | Select-Object -First 10)) { Write-Host "     missing  $m" -ForegroundColor Red }
    foreach ($a in ($added   | Select-Object -First 10)) { Write-Host "     added    $a" -ForegroundColor Red }
    foreach ($c in ($changed | Select-Object -First 10)) { Write-Host "     changed  $c" -ForegroundColor Red }
    if ($bad -gt 30) { Write-Host "     ... and $($bad - 30) more" -ForegroundColor Red }
    exit 1
}
finally {
    Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
