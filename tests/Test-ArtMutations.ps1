#Requires -Version 5.1
<#
    Bounded proof that the new runtime assertions detect broken production code.
    Requires exclusive build/source ownership. Each source is restored byte for
    byte and rebuilt in finally before another mutation is attempted.
#>
[CmdletBinding()]
param([ValidateSet('Release', 'Debug')][string]$Config = 'Release')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$build = Join-Path $repo 'build'
$logs = Join-Path $build 'art-mutations'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$utf8 = New-Object Text.UTF8Encoding($false)
$cmake = 'cmake'
$record = @(Select-String -LiteralPath (Join-Path $build 'CMakeCache.txt') -Pattern '^CMAKE_COMMAND:INTERNAL=(.+)$')
if ($record.Count) { $cmake = $record[0].Matches[0].Groups[1].Value }

function Invoke-MutationProcess {
    param([string]$Program, [string[]]$Arguments)
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $Program
    $psi.Arguments = (($Arguments | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }) -join ' ')
    $psi.WorkingDirectory = $repo
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $proc = [Diagnostics.Process]::Start($psi)
    try {
        $stdout = $proc.StandardOutput.ReadToEndAsync()
        $stderr = $proc.StandardError.ReadToEndAsync()
        if (-not $proc.WaitForExit(180000)) {
            $proc.Kill(); $proc.WaitForExit()
            throw "Mutation process timed out: $Program"
        }
        $proc.WaitForExit()
        [pscustomobject]@{ Code = $proc.ExitCode; Text = ($stdout.Result + $stderr.Result) }
    }
    finally { $proc.Dispose() }
}

function Build-MutationTarget {
    param([string]$Target, [string]$LogName)
    $result = Invoke-MutationProcess $cmake @('--build', $build, '--config', $Config, '--target', $Target)
    [IO.File]::WriteAllText((Join-Path $logs ($LogName + '.build.log')), $result.Text, $utf8)
    if ($result.Code -ne 0) { throw "Mutation build failed: $LogName (see $logs)" }
}

$mutations = @(
    @{ Name = 'portable-half-alpha'; File = 'platform\png_decoder.c'; Target = 'jc_png_test';
       Old = 'else if (a != 255) {'; New = 'else if (a == 64) {';
       Check = ''; Witness = 'WITNESS portable PNG decoder executed';
       Failure = 'FAIL platform/png_decoder.c: half alpha premultiplied' },
    @{ Name = 'cartoon-magenta'; File = 'src\engine\art_style.c'; Target = 'jc_reborn';
       Old = 'if (image >= 0 && style->legacyColorKey) {'; New = 'if (image >= 0) {';
       Check = 'Cartoon retains intentional opaque magenta'; Witness = 'WITNESS art assertion executed:';
       Failure = 'FAIL tests/Invoke-ArtStyleTests.ps1: Cartoon retains intentional opaque magenta' },
    @{ Name = 'cartoon-dimensions'; File = 'src\engine\art_style.c'; Target = 'jc_reborn';
       Old = 'if (selected == &styles[1] && !registeredFootprint &&';
       New = 'if (selected == &styles[0] && !registeredFootprint &&';
       Check = 'wrong-size refuses the named asset without timing out'; Witness = 'WITNESS art assertion executed:';
       Failure = 'FAIL tests/Invoke-ArtStyleTests.ps1: wrong-size refuses the named asset without timing out' },
    @{ Name = 'config-style-persistence'; File = 'src\engine\config.c'; Target = 'jc_reborn';
       Old = 'artStyle=%s\n'; New = 'unusedStyle=%s\n';
       Check = 'a fresh process uses the saved Cartoon setting'; Witness = 'WITNESS art assertion executed:';
       Failure = 'FAIL tests/Invoke-ArtStyleTests.ps1: a fresh process uses the saved Cartoon setting' }
)

foreach ($mutation in $mutations) {
    $source = Join-Path $repo $mutation.File
    $originalBytes = [IO.File]::ReadAllBytes($source)
    $original = [Text.Encoding]::UTF8.GetString($originalBytes)
    if ([regex]::Matches($original, [regex]::Escape($mutation.Old)).Count -ne 1) {
        throw "Expected one mutation site in $($mutation.File): $($mutation.Old)"
    }
    $binary = Join-Path $build ($Config + '\' + $mutation.Target + '.exe')
    $before = (Get-Item -LiteralPath $binary).LastWriteTimeUtc
    if ($mutation.Check) {
        $program = 'powershell.exe'
        $testArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
            (Join-Path $PSScriptRoot 'Invoke-ArtStyleTests.ps1'), '-Exe', $binary,
            '-Phase', 'Regression', '-OnlyCheck', $mutation.Check)
    }
    else { $program = $binary; $testArgs = @() }
    try {
        [IO.File]::WriteAllText($source, $original.Replace($mutation.Old, $mutation.New), $utf8)
        Build-MutationTarget $mutation.Target $mutation.Name
        $after = (Get-Item -LiteralPath $binary).LastWriteTimeUtc
        if ($after -le $before) { throw "Mutation artifact timestamp did not advance: $binary" }
        $result = Invoke-MutationProcess $program $testArgs
        [IO.File]::WriteAllText((Join-Path $logs ($mutation.Name + '.test.log')), $result.Text, $utf8)
        $failureCount = [regex]::Matches($result.Text, '(?m)^\s*FAIL ').Count
        if ($result.Code -eq 0 -or $failureCount -ne 1 -or
            $result.Text -notmatch [regex]::Escape($mutation.Witness) -or
            $result.Text -notmatch [regex]::Escape($mutation.Failure)) {
            throw "Mutation was not rejected by exactly one witnessed assertion: $($mutation.Name) (see $logs)"
        }
        Write-Host "FIRED $($mutation.Name): rebuilt $($before.ToString('o')) -> $($after.ToString('o')); witnessed exactly one named failure"
    }
    finally {
        [IO.File]::WriteAllBytes($source, $originalBytes)
        Build-MutationTarget $mutation.Target ($mutation.Name + '-restored')
    }
    $restored = Invoke-MutationProcess $program $testArgs
    [IO.File]::WriteAllText((Join-Path $logs ($mutation.Name + '-restored.test.log')), $restored.Text, $utf8)
    if ($restored.Code -ne 0 -or $restored.Text -notmatch [regex]::Escape($mutation.Witness)) {
        throw "Restored source failed its witnessed assertion: $($mutation.Name)"
    }
    Write-Host "RESTORED $($mutation.Name): witnessed assertion passes"
}
Write-Host '4/4 runtime mutations fired and restored successfully'
exit 0
