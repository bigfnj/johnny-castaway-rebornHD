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
    # Seed 9, chosen by measurement against a FRESH profile (story day 1), which
    # is what a clean machine and every CI runner starts from. numClouds is
    # rand() % 6, so a seed can legitimately produce no clouds at all for many
    # island scenes, and the night branch skips the rand() % 3 backdrop pick,
    # which shifts the whole stream - so a seed good by day can be barren at
    # night. Swept 1-12 with day and night pinned: seed 9 gives 1,280 cloud draws
    # by day and 2,592 at night, the only seed strong in both.
    [int]$Seed = 9
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
    $fakeHome = Join-Path ([IO.Path]::GetTempPath()) ("jcr-home-" + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $work, $fakeHome | Out-Null

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

        #  AN ISOLATED PROFILE PER RUN, which is not tidiness but correctness.
        #
        #  config.c persists the story day (1-11) to $HOME/.jc_reborn, falling
        #  back to %USERPROFILE%, and story.c picks eligible scenes from that day.
        #  So the developer's saved progress silently decided which scenes a test
        #  exercised. This machine sits at currentDay=11 and a clean CI runner
        #  starts at 1, which is exactly how two cloud assertions passed here and
        #  failed in CI: measured, 1,244 cloud draws with the inherited profile
        #  and 0 with a fresh one, same seed.
        #
        #  Pointing both variables at a throwaway directory makes every run start
        #  from the same state everywhere, and leaves the real file untouched.
        $psi.EnvironmentVariables['HOME'] = $fakeHome
        $psi.EnvironmentVariables['USERPROFILE'] = $fakeHome

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
        Remove-Item -LiteralPath $work     -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $fakeHome -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n== the binary answers without touching the archive ==" -ForegroundColor Cyan

It 'version exits 0 and reports the version from CMakeLists' {
    # Asserts the NUMBER, not just the name. The binary previously printed
    # "Development version" and the project carried no version at all, so there
    # was nothing for a release to be consistent with. JC_VERSION now comes from
    # project(... VERSION ...) as a compile definition, with an "unknown"
    # fallback for hand-rolled builds - and "unknown" reaching a release is
    # exactly what this test exists to catch.
    #
    # .github/workflows/release.yml refuses to publish when the git tag and that
    # same CMake version disagree, so tag, source and binary are pinned together.
    $repo = Split-Path $PSScriptRoot -Parent
    $cmake = Get-Content (Join-Path $repo 'CMakeLists.txt') -Raw
    if ($cmake -notmatch 'project\(jc_reborn VERSION (\d+\.\d+\.\d+)') {
        Write-Host '     no version found in CMakeLists.txt' -ForegroundColor Red
        return $false
    }
    $expected = $Matches[1]

    $r = Invoke-Jc @('version') 60
    ($r.Code -eq 0) -and ($r.Output -match 'Johnny Reborn') -and
        ($r.Output -match [regex]::Escape($expected)) -and
        ($r.Output -notmatch 'unknown')
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
    # `day` is PINNED. Without it this inherited the wall clock: night is
    # 21:00-05:59, and the night branch shifts the RNG stream, so the same seed
    # reaches different scenes. That is precisely how this passed locally in the
    # afternoon and failed in CI at 22:43 UTC.
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys','debug', 'day',
                     'seed', "$Seed", 'frames', '400') 600
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

It 'night forces the NIGHT.SCR backdrop' {
    # Night was reachable ONLY between 21:00 and 05:59 off the system clock, so
    # every daytime test run left NIGHT.SCR and its HD replacement completely
    # unexercised - a whole rendering path nothing could look at, let alone
    # assert on, without changing the machine's clock.
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys', 'debug', 'night',
                     'seed', "$Seed", 'frames', '900') 900
    ($r.Code -eq 0) -and ($r.Output -match 'island backdrop: NIGHT\.SCR')
}

It 'day forces an OCEAN backdrop even at night' {
    # The negative half. Without it an override that simply ignored its argument,
    # or a clock that happened to read daytime, would pass the test above.
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys', 'debug', 'day',
                     'seed', "$Seed", 'frames', '900') 900
    ($r.Code -eq 0) -and ($r.Output -match 'island backdrop: OCEAN0\d\.SCR') -and
        ($r.Output -notmatch 'island backdrop: NIGHT\.SCR')
}

It 'clouds still animate over the night backdrop' {
    # Night and clouds are set up in the same function but composited as separate
    # layers, so "night works" and "clouds work" passing separately does not mean
    # they work TOGETHER.
    #
    # Uses $Seed, which is chosen to work in BOTH lighting conditions. Night
    # skips the `rand() % 3` that picks OCEAN0N, so the whole stream shifts and
    # numClouds (rand() % 6) lands elsewhere: seed 2 gives 1,244 cloud draws by
    # day and exactly 0 at night. An earlier revision pinned seed 5 here, chosen
    # against this developer's saved story day; from a fresh profile seed 5 is
    # barren at night, which is one of the two failures CI caught.
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys', 'debug', 'night',
                     'seed', "$Seed", 'frames', '900') 900
    ($r.Code -eq 0) -and ($r.Output -match 'island backdrop: NIGHT\.SCR') -and
        ($r.Output -match 'Clouds Pos')
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
