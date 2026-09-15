#Requires -Version 5.1
<# Verify an art-only ZIP edit reaches the native runtime without a C relink.
   Requires exclusive ownership of assets/scrantic_data.zip and the build tree.
   The source archive is restored byte-for-byte in finally. #>
[CmdletBinding()]
param([ValidateSet('Release', 'Debug')][string]$Config = 'Release')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$repo = Split-Path $PSScriptRoot -Parent
$build = Join-Path $repo 'build'
$source = Join-Path $repo 'assets\scrantic_data.zip'
$deployed = Join-Path $build ($Config + '\scrantic_data.zip')
$binary = Join-Path $build ($Config + '\jc_reborn.exe')
$original = [IO.File]::ReadAllBytes($source)
$originalHash = (Get-FileHash -LiteralPath $source).Hash
$before = (Get-Item -LiteralPath $binary).LastWriteTimeUtc
$record = @(Select-String -LiteralPath (Join-Path $build 'CMakeCache.txt') -Pattern '^CMAKE_COMMAND:INTERNAL=(.+)$')
$cmake = if ($record.Count) { $record[0].Matches[0].Groups[1].Value } else { 'cmake' }
$sentinel = 'tests/art-refresh-' + [Guid]::NewGuid().ToString('N') + '.txt'

function Run-RefreshProcess {
    param([string]$Program, [string[]]$Arguments)
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $Program
    $psi.Arguments = (($Arguments | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }) -join ' ')
    $psi.WorkingDirectory = $repo
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $p = [Diagnostics.Process]::Start($psi)
    try {
        $stdout = $p.StandardOutput.ReadToEndAsync()
        $stderr = $p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit(180000)) { $p.Kill(); $p.WaitForExit(); throw 'Asset refresh process timed out' }
        $p.WaitForExit()
        [pscustomobject]@{ Code = $p.ExitCode; Text = ($stdout.Result + $stderr.Result) }
    }
    finally { $p.Dispose() }
}

try {
    $zip = [IO.Compression.ZipFile]::Open($source, 'Update')
    try {
        $entry = $zip.CreateEntry($sentinel)
        $stream = $entry.Open()
        $bytes = [Text.Encoding]::ASCII.GetBytes('art-only refresh witness')
        try { $stream.Write($bytes, 0, $bytes.Length) }
        finally { $stream.Dispose() }
    }
    finally { $zip.Dispose() }
    $changedHash = (Get-FileHash -LiteralPath $source).Hash
    if ($changedHash -eq $originalHash) { throw 'Archive mutation changed no bytes' }

    $stale = Run-RefreshProcess 'powershell.exe' @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $repo 'gate.ps1'), '-NoBuild', '-SmokeOnly')
    if ($stale.Code -eq 0 -or [regex]::Matches($stale.Text, '(?m)^FAIL ').Count -ne 1 -or
        $stale.Text -notmatch 'FAIL runtime archive differs from assets/scrantic_data.zip:' -or
        $stale.Text -match '=== smoke ===') {
        throw 'Stale-asset mutation did not trigger exactly one archive-naming gate failure'
    }
    Write-Host 'FIRED stale archive: gate rejected exactly one named runtime archive mismatch before smoke'
    $targetOnly = Run-RefreshProcess $cmake @('--build', $build, '--config', $Config, '--target', 'jc_reborn')
    if ($targetOnly.Code -ne 0) { throw $targetOnly.Text }
    $targetCopied = (Get-FileHash -LiteralPath $deployed).Hash -eq $changedHash
    Write-Host "OBSERVED explicit jc_reborn target refreshes an art-only archive: $targetCopied"

    $normal = Run-RefreshProcess $cmake @('--build', $build, '--config', $Config)
    if ($normal.Code -ne 0) { throw $normal.Text }
    if ((Get-FileHash -LiteralPath $deployed).Hash -ne $changedHash) { throw 'Normal build did not deploy changed archive bytes' }
    $zip = [IO.Compression.ZipFile]::OpenRead($deployed)
    try { if (-not $zip.GetEntry($sentinel)) { throw 'Deployed archive lacks the unique mutation witness member' } }
    finally { $zip.Dispose() }
    if ((Get-Item -LiteralPath $binary).LastWriteTimeUtc -ne $before) { throw 'Expected no C relink during the art-only refresh test' }
    Write-Host 'WITNESS native art-only edit deployed by normal build; archive hash/member match and executable timestamp unchanged'
}
finally {
    [IO.File]::WriteAllBytes($source, $original)
    $restored = Run-RefreshProcess $cmake @('--build', $build, '--config', $Config)
    if ($restored.Code -ne 0) { throw "Archive restored but deployment rebuild failed: $($restored.Text)" }
    if ((Get-FileHash -LiteralPath $source).Hash -ne $originalHash -or
        (Get-FileHash -LiteralPath $deployed).Hash -ne $originalHash) {
        throw 'Original archive bytes were not restored in source and deployment'
    }
    Write-Host 'RESTORED original source and runtime archive SHA-256'
}
exit 0
