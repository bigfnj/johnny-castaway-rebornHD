#Requires -Version 5.1
<#
    Smoke tests for jc_reborn.

    WHAT IS TESTABLE HERE, and why the list looks the way it does. This is a
    screensaver: the shipping mode loops forever and only leaves through exit()
    on an input event, and success is ultimately visual. So these assert the
    things a machine CAN judge - that a mode starts, does real work, tears down
    through the normal path, and returns the exit code it promises - and leave
    "does it look right" to the golden dump corpus and to a human.

    The `frames` option is what makes the graphical modes assertable at all:
    without it a test can only kill the process and guess whether it was healthy
    when it died.
#>
[CmdletBinding()]
param(
    [string]$Exe,
    # Seed 2 is deliberate. numClouds is rand() % 6, so a seed can legitimately
    # produce no clouds for many island scenes: seed 1 renders none inside the
    # first ~6,000 frames and 15,151 cloud draws by 30,000. Seed 2 reaches the
    # cloud path within a few hundred frames, so the smoke run exercises island
    # setup, cloud animation and teardown rather than only the common path.
    [int]$Seed = 2
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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

$script:passed = 0
$script:failed = 0

function It {
    param([string]$Name, [scriptblock]$Body)
    try {
        $ok = & $Body
        if ($ok) { Write-Host "  ok   $Name" -ForegroundColor Green; $script:passed++ }
        else     { Write-Host "  FAIL $Name" -ForegroundColor Red;   $script:failed++ }
    }
    catch {
        Write-Host "  FAIL $Name - $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
    }
}

# Run in a scratch directory: several modes write ./dump/ or pick up files from
# the working directory, and a test must not depend on, or pollute, the repo.
function Invoke-Jc {
    <#
        A DIRECT .NET PROCESS, not Start-Process -PassThru. The latter returned
        $null from .ExitCode here even after WaitForExit reported the process had
        exited, which made every exit-code assertion silently fail against a
        healthy binary. Measured, not assumed: the same object reported
        HasExited=True and a populated output file in the same breath.

        stderr is captured too. fatalError() writes there, so with stdout-only
        redirection the "Invalid seed" diagnostics printed to the console and the
        tests could not assert on them.

        Both streams are read asynchronously BEFORE waiting: reading one to the
        end while the child fills the other is the classic pipe deadlock, and
        this engine is chatty under `debug`.
    #>
    param([string[]]$JcArgs, [int]$TimeoutSec = 300)

    $work = Join-Path ([IO.Path]::GetTempPath()) ("jcr-smoke-" + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $work | Out-Null

    $proc = $null
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName               = $Exe
        $psi.WorkingDirectory       = $work
        $psi.UseShellExecute        = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError  = $true
        $psi.CreateNoWindow         = $true
        # ProcessStartInfo.ArgumentList is .NET Core 2.1+; Windows PowerShell 5.1
        # runs on .NET Framework, where only the Arguments STRING exists. Quote
        # each token so an argument containing a space cannot split in two.
        $psi.Arguments = (($JcArgs | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }) -join ' ')

        $proc = [System.Diagnostics.Process]::Start($psi)
        $stdout = $proc.StandardOutput.ReadToEndAsync()
        $stderr = $proc.StandardError.ReadToEndAsync()

        if (-not $proc.WaitForExit($TimeoutSec * 1000)) {
            try { $proc.Kill() } catch { }
            $proc.WaitForExit()
            return [pscustomobject]@{ Code = -999; Output = 'TIMED OUT'; TimedOut = $true }
        }
        # The no-argument overload after a timed wait: it also settles the async
        # stream readers, so the text below is complete.
        $proc.WaitForExit()

        $text = $stdout.Result + $stderr.Result
        return [pscustomobject]@{ Code = $proc.ExitCode; Output = $text; TimedOut = $false }
    }
    finally {
        if ($proc) { $proc.Dispose() }
        Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n== the binary answers without touching the archive ==" -ForegroundColor Cyan

It 'version exits 0 and names the engine' {
    $r = Invoke-Jc @('version') 60
    ($r.Code -eq 0) -and ($r.Output -match 'Johnny Reborn')
}

It 'help exits non-zero and lists the new options' {
    # usage() exits 1 by design: asking for help is not a successful run.
    $r = Invoke-Jc @('help') 60
    ($r.Code -ne 0) -and ($r.Output -match 'seed <n>') -and ($r.Output -match 'frames <n>')
}

Write-Host "`n== the archive is found without being told where it is ==" -ForegroundColor Cyan

It 'dump runs from an unrelated working directory' {
    # The whole point of the zipvfs search path. This runs in a scratch dir that
    # contains no zip, so it can only pass by locating the archive next to the
    # executable. Before that search existed, the binary could not run anywhere.
    $r = Invoke-Jc @('dump') 900
    ($r.Code -eq 0) -and ($r.Output -match 'Dumping TTM')
}

Write-Host "`n== bad arguments are refused, not silently accepted ==" -ForegroundColor Cyan

It 'a non-numeric seed is rejected rather than read as 0' {
    $r = Invoke-Jc @('window', 'nosound', 'seed', 'abc', 'frames', '5') 120
    $r.Code -ne 0
}

It 'a zero frame count is rejected' {
    # 0 means "unlimited" internally, so accepting it from the command line
    # would turn a bounded test run into one that never returns.
    $r = Invoke-Jc @('window', 'nosound', 'frames', '0') 120
    $r.Code -ne 0
}

It 'an out-of-range ADS tag is rejected' {
    $r = Invoke-Jc @('window', 'nosound', 'ads', 'JOHNNY.ADS', '99999999') 120
    $r.Code -ne 0
}

Write-Host "`n== bounded graphical runs start, work, and tear down cleanly ==" -ForegroundColor Cyan

# Every run below passes `hotkeys`, and that is load-bearing rather than a
# preference. Without it the engine treats ANY keypress as "quit the
# screensaver" and calls exit(255) - correct shipping behaviour, and fatal to an
# automated test, because these runs open a real window that can take stray
# input. A 25,000-frame verification run was lost to exactly that: it exited 255
# at an unknown frame and looked indistinguishable from a clean pass. With
# hotkeys enabled only Esc quits.

It 'a bounded story run exits 0 through the normal shutdown path' {
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','seed', "$Seed", 'frames', '400') 600
    (-not $r.TimedOut) -and ($r.Code -eq 0)
}

It 'and it actually reaches the island cloud path, not just the common case' {
    # Asserts the run did REAL work rather than exiting early. A bounded run that
    # returns 0 having rendered nothing would otherwise pass the test above.
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','debug', 'seed', "$Seed", 'frames', '400') 600
    ($r.Code -eq 0) -and ($r.Output -match 'Clouds Pos')
}

It 'the same seed produces the same run twice' {
    # Determinism is what makes every other runtime assertion meaningful.
    $a = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','debug', 'seed', "$Seed", 'frames', '150') 600
    $b = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','debug', 'seed', "$Seed", 'frames', '150') 600
    ($a.Code -eq 0) -and ($b.Code -eq 0) -and ($a.Output -eq $b.Output)
}

It 'a different seed produces a different run' {
    # The negative half: without this, a seed option that did nothing at all
    # would pass the determinism test above.
    $a = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','debug', 'seed', '2', 'frames', '150') 600
    $b = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','debug', 'seed', '7', 'frames', '150') 600
    ($a.Code -eq 0) -and ($b.Code -eq 0) -and ($a.Output -ne $b.Output)
}

It 'bench mode runs bounded and exits 0' {
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','frames', '120', 'bench') 600
    (-not $r.TimedOut) -and ($r.Code -eq 0)
}

It 'a single TTM plays bounded and exits 0' {
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','frames', '120', 'ttm', 'MJSAND.TTM') 600
    (-not $r.TimedOut) -and ($r.Code -eq 0)
}

Write-Host ""
if ($script:failed) {
    Write-Host ("{0} passed, {1} failed" -f $script:passed, $script:failed) -ForegroundColor Red
    exit 1
}
Write-Host ("{0} passed, 0 failed" -f $script:passed) -ForegroundColor Green
exit 0
