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
    Write-FixtureText 'tests\Test-PlatformAlloc.ps1' (
        "param(`$Exe, `$Phase)`nWrite-Output ('WITNESS platform-' + `$Phase)`n" +
        $(if ($FailPhase -eq 'platform') { "if (`$Phase -eq 'Smoke') { Write-Output 'FAIL fixture tests/Test-PlatformAlloc.ps1'; exit 1 }`n" } else { '' }) + "exit 0`n")
    Write-FixtureText 'tests\test_art_tools.py' "import unittest`nclass OrderFixture(unittest.TestCase):`n    def test_reached(self):`n        print('WITNESS authoring-regression')`n        self.assertTrue(True)`n"
    foreach ($suite in @(@{ Name = 'inventory'; File = 'test_art_inventory.py' }, @{ Name = 'history'; File = 'test_art_pilot_history.py' })) {
        $phaseCode = if ($suite.Name -eq 'inventory') { "phase = 'Smoke' if '--smoke' in sys.argv else 'Regression'`n" }
            else { "phase = sys.argv[sys.argv.index('--phase') + 1].title()`n" }
        $failCode = if ($FailPhase -eq $suite.Name) {
            "if phase == 'Smoke':`n    print('FAIL fixture tests/$($suite.File)')`n    sys.exit(1)`n"
        } elseif ($FailPhase -eq ($suite.Name + '-regression')) {
            "if phase == 'Regression':`n    print('FAIL fixture tests/$($suite.File)')`n    sys.exit(1)`n"
        } else { '' }
        Write-FixtureText ('tests\' + $suite.File) (
            "import sys`n" + $phaseCode + "print('WITNESS $($suite.Name)-' + phase)`n" + $failCode)
    }
    Write-FixtureText 'tests\test_wave_renderer.py' (
        "import sys`nphase = 'Smoke' if '--phase' in sys.argv else 'Regression'`nprint('WITNESS wave-' + phase)`n" +
        $(if ($FailPhase -eq 'wave') { "if phase == 'Smoke':`n    print('FAIL fixture tests/test_wave_renderer.py')`n    sys.exit(1)`n" } else { '' }))
    Write-FixtureText 'tests\test_palm_renderer.py' (
        "import sys`nphase = 'Smoke' if '--phase' in sys.argv else 'Regression'`nprint('WITNESS palm-' + phase)`n" +
        $(if ($FailPhase -eq 'palm') { "if phase == 'Smoke':`n    print('FAIL fixture tests/test_palm_renderer.py')`n    sys.exit(1)`n" } else { '' }))
    foreach ($suite in @(@{ Name = 'decoder'; File = 'test_uncompress.py' }, @{ Name = 'lifecycle'; File = 'test_lifecycle.py' })) {
        $failCode = if ($FailPhase -eq $suite.Name) { "if phase == 'Smoke':`n    print('FAIL fixture tests/$($suite.File)')`n    sys.exit(1)`n" } else { '' }
        Write-FixtureText ('tests\' + $suite.File) (
            "import sys`nphase = 'Smoke' if '--phase' in sys.argv else 'Regression'`nprint('WITNESS $($suite.Name)-' + phase)`n" + $failCode)
    }
    Write-FixtureText 'tests\test_frame_limits.py' (
        "import argparse, sys`nfrom pathlib import Path`n" +
        "parser = argparse.ArgumentParser()`nparser.add_argument('--exe', required=True, type=Path)`n" +
        "parser.add_argument('--probe', required=True, type=Path)`nparser.add_argument('--phase', choices=['smoke', 'regression'], default='regression')`n" +
        "args = parser.parse_args()`nexpected = Path(__file__).resolve().parents[1] / 'build' / 'Release'`n" +
        "assert args.exe.resolve() == expected / 'jc_reborn.exe' and args.exe.is_file(), 'tests/test_frame_limits.py: wrong engine path'`n" +
        "assert args.probe.resolve() == expected / 'jc_frame_test.exe' and args.probe.is_file(), 'tests/test_frame_limits.py: wrong probe path'`n" +
        "phase = args.phase.title()`nprint('WITNESS frame-' + phase)`n" +
        $(if ($FailPhase -eq 'frame') { "if phase == 'Smoke':`n    print('FAIL fixture tests/test_frame_limits.py')`n    sys.exit(1)`n" } elseif ($FailPhase -eq 'frame-regression') { "if phase == 'Regression':`n    print('FAIL fixture tests/test_frame_limits.py')`n    sys.exit(1)`n" } else { '' }))
    foreach ($suite in @(@{ Name = 'extractor'; File = 'test_extractors.py' }, @{ Name = 'wrapper'; File = 'test_web_wrapper.py' })) {
        $paths = if ($suite.Name -eq 'extractor') {
            "parser.add_argument('--sound', required=True, type=Path)`nparser.add_argument('--walk', required=True, type=Path)`n"
        } else { '' }
        $validate = if ($suite.Name -eq 'extractor') {
            "expected = Path(__file__).resolve().parents[1] / 'build' / 'Release'`n" +
            "assert args.sound.resolve() == expected / 'extract_sound.exe' and args.sound.is_file(), 'tests/test_extractors.py: wrong sound path'`n" +
            "assert args.walk.resolve() == expected / 'extract_walk_data.exe' and args.walk.is_file(), 'tests/test_extractors.py: wrong walk path'`n"
        } else { '' }
        $failCode = if ($FailPhase -eq $suite.Name) {
            "if phase == 'Smoke':`n    print('FAIL fixture tests/$($suite.File)')`n    sys.exit(1)`n"
        } elseif ($FailPhase -eq ($suite.Name + '-regression')) {
            "if phase == 'Regression':`n    print('FAIL fixture tests/$($suite.File)')`n    sys.exit(1)`n"
        } else { '' }
        Write-FixtureText ('tests\' + $suite.File) (
            "import argparse, sys`nfrom pathlib import Path`nparser = argparse.ArgumentParser()`n" + $paths +
            "parser.add_argument('--phase', choices=['smoke', 'regression'], required=True)`nargs = parser.parse_args()`n" +
            $validate + "phase = args.phase.title()`nprint('WITNESS $($suite.Name)-' + phase)`n" + $failCode)
    }
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
        palm = 'tests/test_palm_renderer.py'
        decoder = 'tests/test_uncompress.py'
        lifecycle = 'tests/test_lifecycle.py'
        frame = 'tests/test_frame_limits.py'
        platform = 'tests/Test-PlatformAlloc.ps1'
        extractor = 'tests/test_extractors.py'
        wrapper = 'tests/test_web_wrapper.py'
        inventory = 'tests/test_art_inventory.py'
        history = 'tests/test_art_pilot_history.py'
    }
    $marker = 'FAIL fixture ' + $names[$Phase]
    ($Result.Code -ne 0) -and
        ([regex]::Matches($Result.Text, [regex]::Escape($marker)).Count -eq 1) -and
        ($Result.Text -notmatch 'WITNESS art-Regression') -and
        ($Result.Text -notmatch 'WITNESS wave-Regression') -and
        ($Result.Text -notmatch 'WITNESS palm-Regression') -and
        ($Result.Text -notmatch 'WITNESS decoder-Regression') -and
        ($Result.Text -notmatch 'WITNESS lifecycle-Regression') -and
        ($Result.Text -notmatch 'WITNESS frame-Regression') -and
        ($Result.Text -notmatch 'WITNESS platform-Regression') -and
        ($Result.Text -notmatch 'WITNESS extractor-Regression') -and
        ($Result.Text -notmatch 'WITNESS wrapper-Regression') -and
        ($Result.Text -notmatch 'WITNESS authoring-regression') -and
        ($Result.Text -notmatch 'WITNESS inventory-Regression') -and
        ($Result.Text -notmatch 'WITNESS history-Regression') -and
        ($Result.Text -notmatch 'WITNESS dump-regression')
}

function Assert-Complete {
    param($Result)
    $expected = @('smoke', 'screensaver', 'art-Smoke', 'wave-Smoke', 'palm-Smoke',
        'decoder-Smoke', 'lifecycle-Smoke', 'frame-Smoke', 'platform-Smoke', 'extractor-Smoke',
        'wrapper-Smoke', 'inventory-Smoke', 'history-Smoke', 'extractor-Regression',
        'wrapper-Regression', 'platform-Regression', 'decoder-Regression', 'lifecycle-Regression',
        'frame-Regression', 'art-Regression', 'wave-Regression', 'palm-Regression',
        'authoring-regression', 'inventory-Regression', 'history-Regression', 'dump-regression')
    $actual = @([regex]::Matches($Result.Text, '(?m)^WITNESS ([^\r\n]+)') | ForEach-Object { $_.Groups[1].Value })
    if (($Result.Code -ne 0) -or (($actual -join ',') -ne ($expected -join ','))) {
        throw 'gate.ps1: expected smoke and regression witnesses missing or out of order'
    }
}

function Assert-Case {
    param([string]$Name, [bool]$Pass)
    if ($Pass) { Write-Host "ok   $Name" }
    else { Write-Host "FAIL $Name"; $script:failures++ }
}

function Assert-Ordering {
    param([string]$Phase, $Result)
    if (-not (Check-Ordering $Phase $Result)) {
        throw "gate.ps1: $Phase smoke failure reached regression or lost its diagnostic/status"
    }
}

try {
    foreach ($dir in @('tests', 'assets', 'build\Release')) {
        New-Item -ItemType Directory -Path (Join-Path $work $dir) -Force | Out-Null
    }
    foreach ($file in @('build\Release\jc_reborn.exe', 'build\Release\jc_reborn.scr',
                        'build\Release\jc_frame_test.exe',
                        'build\Release\extract_sound.exe', 'build\Release\extract_walk_data.exe',
                        'build\Release\scrantic_data.zip', 'assets\scrantic_data.zip')) {
        [IO.File]::WriteAllBytes((Join-Path $work $file), [byte[]]@(0))
    }
    Write-FixtureText 'gate.ps1' $gateSource
    foreach ($phase in @('smoke', 'screensaver', 'art', 'wave', 'palm', 'decoder', 'lifecycle', 'frame', 'platform', 'extractor', 'wrapper', 'inventory', 'history')) {
        $result = Run-GateCase $phase
        Assert-Case "$phase failure prevents regression" (Check-Ordering $phase $result)
    }
    $result = Run-GateCase 'none'
    Assert-Complete $result
    Write-Host 'ok   passed smoke reaches every regression witness in order'
    $result = Run-GateCase 'frame-regression'
    Assert-Case 'frame regression failure fails the gate after all smoke' (
        ($result.Code -ne 0) -and
        ([regex]::Matches($result.Text, 'FAIL fixture tests/test_frame_limits.py').Count -eq 1) -and
        ($result.Text -match '(?s)WITNESS frame-Smoke.*WITNESS platform-Smoke.*WITNESS frame-Regression.*WITNESS dump-regression'))
    foreach ($suite in @(@{ Name = 'extractor'; File = 'test_extractors.py' }, @{ Name = 'wrapper'; File = 'test_web_wrapper.py' },
                        @{ Name = 'inventory'; File = 'test_art_inventory.py' }, @{ Name = 'history'; File = 'test_art_pilot_history.py' })) {
        $result = Run-GateCase ($suite.Name + '-regression')
        Assert-Case "$($suite.Name) regression failure fails the gate after all smoke" (
            ($result.Code -ne 0) -and
            ([regex]::Matches($result.Text, [regex]::Escape('FAIL fixture tests/' + $suite.File)).Count -eq 1) -and
            ($result.Text -match ('(?s)WITNESS wrapper-Smoke.*WITNESS ' + $suite.Name + '-Regression.*WITNESS dump-regression')))
    }
    $result = Run-GateCase 'none' -SmokeOnly
    Assert-Case 'SmokeOnly executes smoke without regression' (
        ($result.Code -eq 0) -and ($result.Text -match 'WITNESS wave-Smoke') -and
        ($result.Text -notmatch 'WITNESS art-Regression') -and ($result.Text -notmatch 'WITNESS wave-Regression') -and
        ($result.Text -match 'WITNESS palm-Smoke') -and ($result.Text -notmatch 'WITNESS palm-Regression') -and
        ($result.Text -match 'WITNESS decoder-Smoke') -and ($result.Text -notmatch 'WITNESS decoder-Regression') -and
        ($result.Text -match 'WITNESS lifecycle-Smoke') -and ($result.Text -notmatch 'WITNESS lifecycle-Regression') -and
        ($result.Text -match 'WITNESS frame-Smoke') -and ($result.Text -notmatch 'WITNESS frame-Regression') -and
        ($result.Text -match 'WITNESS platform-Smoke') -and ($result.Text -notmatch 'WITNESS platform-Regression') -and
        ($result.Text -match 'WITNESS extractor-Smoke') -and ($result.Text -notmatch 'WITNESS extractor-Regression') -and
        ($result.Text -match 'WITNESS wrapper-Smoke') -and ($result.Text -notmatch 'WITNESS wrapper-Regression') -and
        ($result.Text -match 'WITNESS inventory-Smoke') -and ($result.Text -notmatch 'WITNESS inventory-Regression') -and
        ($result.Text -match 'WITNESS history-Smoke') -and ($result.Text -notmatch 'WITNESS history-Regression') -and
        ($result.Text -notmatch 'WITNESS authoring-regression') -and ($result.Text -notmatch 'WITNESS dump-regression'))

    if ($VerifyMutation) {
        foreach ($phase in @('decoder', 'lifecycle', 'frame', 'platform', 'extractor', 'wrapper', 'inventory', 'history')) {
            $guard = "if (`$LASTEXITCODE -ne 0) {`n    Write-Host 'GATE FAILED: $phase smoke failed; regression was not run'"
            if ([regex]::Matches($gateSource, [regex]::Escape($guard)).Count -ne 1) {
                throw "Expected exactly one $phase smoke short-circuit guard in gate.ps1"
            }
            $mutant = $gateSource.Replace($guard, "if (`$false) {`n    Write-Host 'GATE FAILED: $phase smoke failed; regression was not run'")
            Write-FixtureText 'gate.ps1' $mutant
            $result = Run-GateCase $phase
            if ($result.Text -notmatch "WITNESS $phase-Smoke" -or $result.Text -notmatch 'WITNESS dump-regression') {
                throw "gate.ps1: $phase mutant did not execute the guarded smoke and regression witnesses"
            }
            $caught = $false
            try { Assert-Ordering $phase $result }
            catch {
                $expected = "gate.ps1: $phase smoke failure reached regression or lost its diagnostic/status"
                if ($_.Exception.Message -ne $expected) { throw }
                $caught = $true
                Write-Host "FIRED 1/1 $expected"
            }
            if (-not $caught) { throw "gate.ps1: $phase mutation survived" }
            Write-FixtureText 'gate.ps1' $gateSource
            Assert-Ordering $phase (Run-GateCase $phase)
            Write-Host "ok   restored $phase guard blocks regression again"
        }

        foreach ($omission in @(
            @{ Name = 'inventory-Smoke'; Command = "& python -B (Join-Path `$repo 'tests\test_art_inventory.py') --smoke" },
            @{ Name = 'inventory-Regression'; Command = "    & python -B (Join-Path `$repo 'tests\test_art_inventory.py')`n" },
            @{ Name = 'history-Smoke'; Command = "& python -B (Join-Path `$repo 'tests\test_art_pilot_history.py') --phase smoke" },
            @{ Name = 'history-Regression'; Command = "& python -B (Join-Path `$repo 'tests\test_art_pilot_history.py') --phase regression" }
        )) {
            if ([regex]::Matches($gateSource, [regex]::Escape($omission.Command)).Count -ne 1) {
                throw "Expected exactly one $($omission.Name) invocation in gate.ps1"
            }
            $marker = "EXECUTED omitted $($omission.Name)"
            Write-FixtureText 'gate.ps1' ($gateSource.Replace($omission.Command, "Write-Output '$marker'`n"))
            $result = Run-GateCase 'none'
            if (($result.Text -notmatch [regex]::Escape($marker)) -or ($result.Text -notmatch 'WITNESS dump-regression')) {
                throw "gate.ps1: $($omission.Name) omission did not execute the changed gate and final witness"
            }
            $caught = $false
            try { Assert-Complete $result }
            catch {
                if ($_.Exception.Message -ne 'gate.ps1: expected smoke and regression witnesses missing or out of order') { throw }
                $caught = $true
                Write-Host "FIRED 1/1 gate.ps1: omitted $($omission.Name) was detected by the execution trace"
            }
            if (-not $caught) { throw "gate.ps1: $($omission.Name) omission survived" }
            Write-FixtureText 'gate.ps1' $gateSource
        }

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

        $guard = "if (`$LASTEXITCODE -ne 0) {`n    Write-Host 'GATE FAILED: palm smoke failed; regression was not run'"
        if ([regex]::Matches($gateSource, [regex]::Escape($guard)).Count -ne 1) {
            throw 'Expected exactly one palm smoke short-circuit guard in gate.ps1'
        }
        $mutant = $gateSource.Replace($guard, "if (`$false) {`n    Write-Host 'GATE FAILED: palm smoke failed; regression was not run'")
        Write-FixtureText 'gate.ps1' $mutant
        $result = Run-GateCase 'palm'
        Assert-Case 'palm mutation executes regression witness and the ordering assertion rejects it' (
            (-not (Check-Ordering 'palm' $result)) -and
            ($result.Text -match 'WITNESS palm-Regression') -and ($result.Text -match 'WITNESS dump-regression') -and
            ([regex]::Matches($result.Text, 'FAIL fixture tests/test_palm_renderer.py').Count -eq 1))
        Write-FixtureText 'gate.ps1' $gateSource
        Assert-Case 'restored palm gate blocks regression again' (Check-Ordering 'palm' (Run-GateCase 'palm'))
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
