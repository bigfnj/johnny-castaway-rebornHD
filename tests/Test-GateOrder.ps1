#Requires -Version 5.1
<#
    Exercise the actual gate orchestration with isolated child-script fixtures.
    A failed smoke must prevent every regression command from being executed.
    -VerifyMutation disables that guard in a scratch copy and proves this test
    detects the bad ordering. The repository gate is never modified.
#>
[CmdletBinding()]
param(
    [ValidateSet('powershell.exe', 'pwsh')]
    [string]$GateShell = 'powershell.exe',
    [switch]$VerifyMutation
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$gateSource = [IO.File]::ReadAllText((Join-Path $repo 'gate.ps1')).Replace("`r`n", "`n")
$work = Join-Path ([IO.Path]::GetTempPath()) ('jcr-gate-order-' + [Guid]::NewGuid().ToString('N'))
$script:failures = 0
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Write-FixtureText {
    param([string]$Relative, [string]$Content)
    [IO.File]::WriteAllText((Join-Path $work $Relative), $Content, $utf8)
}

function Run-GateCase {
    param([string]$FailPhase, [switch]$SmokeOnly)
    Write-FixtureText 'tests\Invoke-SmokeTests.ps1' (
        "param(`$Exe)`nWrite-Output 'WITNESS smoke'`n" +
        $(if ($FailPhase -eq 'smoke') { "Write-Output 'FAIL fixture tests/Invoke-SmokeTests.ps1'; exit 1`n" } else { "exit 0`n" }))
    Write-FixtureText 'tests\Test-ScreensaverPreview.ps1' (
        "param(`$Scr, `$Exe)`nWrite-Output 'WITNESS screensaver'`n" +
        $(if ($FailPhase -eq 'screensaver') { "Write-Output 'FAIL fixture tests/Test-ScreensaverPreview.ps1'; exit 1`n" } else { "exit 0`n" }))
    Write-FixtureText 'tests\Invoke-ArtStyleTests.ps1' (
        "param(`$Exe, `$Phase)`nWrite-Output ('WITNESS art-' + `$Phase)`n" +
        $(if ($FailPhase -eq 'art') { "if (`$Phase -eq 'Smoke') { Write-Output 'FAIL fixture tests/Invoke-ArtStyleTests.ps1'; exit 1 }`n" } else { '' }) + "exit 0`n")
    Write-FixtureText 'tests\Invoke-DumpRegression.ps1' "param(`$Exe)`nWrite-Output 'WITNESS dump-regression'`nexit 0`n"
    Write-FixtureText 'tests\test_art_tools.py' "import unittest`nclass OrderFixture(unittest.TestCase):`n    def test_reached(self):`n        print('WITNESS authoring-regression')`n        self.assertTrue(True)`n"
    Write-FixtureText 'tests\test_wave_renderer.py' (
        "import sys`nphase = 'Smoke' if '--phase' in sys.argv else 'Regression'`nprint('WITNESS wave-' + phase)`n" +
        $(if ($FailPhase -eq 'wave') { "if phase == 'Smoke':`n    print('FAIL fixture tests/test_wave_renderer.py')`n    sys.exit(1)`n" } else { '' }))
    $gateArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $work 'gate.ps1'), '-NoBuild')
    if ($SmokeOnly) { $gateArgs += '-SmokeOnly' }
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $GateShell
    $psi.Arguments = (($gateArgs | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }) -join ' ')
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $proc = [Diagnostics.Process]::Start($psi)
    try {
        $stdout = $proc.StandardOutput.ReadToEndAsync()
        $stderr = $proc.StandardError.ReadToEndAsync()
        if (-not $proc.WaitForExit(60000)) {
            $proc.Kill(); $proc.WaitForExit()
            throw 'Gate order fixture timed out'
        }
        $proc.WaitForExit()
        [pscustomobject]@{ Code = $proc.ExitCode; Text = ($stdout.Result + $stderr.Result) }
    }
    finally { $proc.Dispose() }
}

function Check-Ordering {
    param([string]$Phase, $Result)
    $names = @{
        smoke = 'tests/Invoke-SmokeTests.ps1'
        screensaver = 'tests/Test-ScreensaverPreview.ps1'
        art = 'tests/Invoke-ArtStyleTests.ps1'
        wave = 'tests/test_wave_renderer.py'
    }
    $marker = 'FAIL fixture ' + $names[$Phase]
    ($Result.Code -ne 0) -and
        ([regex]::Matches($Result.Text, [regex]::Escape($marker)).Count -eq 1) -and
        ($Result.Text -notmatch 'WITNESS art-Regression') -and
        ($Result.Text -notmatch 'WITNESS wave-Regression') -and
        ($Result.Text -notmatch 'WITNESS authoring-regression') -and
        ($Result.Text -notmatch 'WITNESS dump-regression')
}

function Assert-Case {
    param([string]$Name, [bool]$Pass)
    if ($Pass) { Write-Host "ok   $Name" }
    else { Write-Host "FAIL $Name"; $script:failures++ }
}

try {
    foreach ($dir in @('tests', 'assets', 'build\Release')) {
        New-Item -ItemType Directory -Path (Join-Path $work $dir) -Force | Out-Null
    }
    foreach ($file in @('build\Release\jc_reborn.exe', 'build\Release\jc_reborn.scr',
                        'build\Release\scrantic_data.zip', 'assets\scrantic_data.zip')) {
        [IO.File]::WriteAllBytes((Join-Path $work $file), [byte[]]@(0))
    }
    Write-FixtureText 'gate.ps1' $gateSource
    foreach ($phase in @('smoke', 'screensaver', 'art', 'wave')) {
        $result = Run-GateCase $phase
        Assert-Case "$phase failure prevents regression" (Check-Ordering $phase $result)
    }
    $result = Run-GateCase 'none'
    Assert-Case 'passed smoke reaches every regression witness in order' (
        ($result.Code -eq 0) -and
        ($result.Text -match '(?s)WITNESS smoke.*WITNESS screensaver.*WITNESS art-Smoke.*WITNESS wave-Smoke.*WITNESS art-Regression.*WITNESS wave-Regression.*WITNESS authoring-regression.*WITNESS dump-regression'))
    $result = Run-GateCase 'none' -SmokeOnly
    Assert-Case 'SmokeOnly executes smoke without regression' (
        ($result.Code -eq 0) -and ($result.Text -match 'WITNESS wave-Smoke') -and
        ($result.Text -notmatch 'WITNESS art-Regression') -and ($result.Text -notmatch 'WITNESS wave-Regression') -and
        ($result.Text -notmatch 'WITNESS authoring-regression') -and ($result.Text -notmatch 'WITNESS dump-regression'))

    if ($VerifyMutation) {
        $guard = "if (`$LASTEXITCODE -ne 0) {`n    Write-Host 'GATE FAILED: smoke failed; regression was not run'"
        if ([regex]::Matches($gateSource, [regex]::Escape($guard)).Count -ne 1) {
            throw 'Expected exactly one smoke short-circuit guard in gate.ps1'
        }
        $mutant = $gateSource.Replace($guard, "if (`$false) {`n    Write-Host 'GATE FAILED: smoke failed; regression was not run'")
        Write-FixtureText 'gate.ps1' $mutant
        $result = Run-GateCase 'smoke'
        Assert-Case 'mutation executes regression witness and the ordering assertion rejects it' (
            (-not (Check-Ordering 'smoke' $result)) -and
            ($result.Text -match 'WITNESS dump-regression') -and
            ([regex]::Matches($result.Text, 'FAIL fixture tests/Invoke-SmokeTests.ps1').Count -eq 1))
        Write-FixtureText 'gate.ps1' $gateSource
        Assert-Case 'restored gate blocks regression again' (Check-Ordering 'smoke' (Run-GateCase 'smoke'))

        $guard = "if (`$LASTEXITCODE -ne 0) {`n    Write-Host 'GATE FAILED: wave smoke failed; regression was not run'"
        if ([regex]::Matches($gateSource, [regex]::Escape($guard)).Count -ne 1) {
            throw 'Expected exactly one wave smoke short-circuit guard in gate.ps1'
        }
        $mutant = $gateSource.Replace($guard, "if (`$false) {`n    Write-Host 'GATE FAILED: wave smoke failed; regression was not run'")
        Write-FixtureText 'gate.ps1' $mutant
        $result = Run-GateCase 'wave'
        Assert-Case 'wave mutation executes regression witness and the ordering assertion rejects it' (
            (-not (Check-Ordering 'wave' $result)) -and
            ($result.Text -match 'WITNESS wave-Regression') -and ($result.Text -match 'WITNESS dump-regression') -and
            ([regex]::Matches($result.Text, 'FAIL fixture tests/test_wave_renderer.py').Count -eq 1))
        Write-FixtureText 'gate.ps1' $gateSource
        Assert-Case 'restored wave gate blocks regression again' (Check-Ordering 'wave' (Run-GateCase 'wave'))
    }
}
finally {
    $resolved = [IO.Path]::GetFullPath($work)
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not $resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing cleanup outside temporary root: $resolved"
    }
    if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}

if ($script:failures) { exit 1 }
Write-Host 'gate order verified'
exit 0
