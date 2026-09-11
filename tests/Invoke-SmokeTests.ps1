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

# Synthetic malformed archives for the bounds no shipped resource can reach.
# See the header of that file for why they have to be built rather than found.
. (Join-Path $PSScriptRoot 'New-MalformedArchive.ps1')

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
    param([string[]]$JcArgs, [int]$TimeoutSec = 300, [string]$WorkDir)

    # A caller-supplied working directory is how the malformed-fixture tests
    # steer the binary onto their archive: zipvfs_init() tries the bare
    # "scrantic_data.zip" relative to the current directory before it looks
    # beside the executable. The caller owns that directory, so it is not
    # cleaned up here.
    $ownWork = $false
    if (-not $WorkDir) {
        $WorkDir = Join-Path ([IO.Path]::GetTempPath()) ("jcr-smoke-" + [Guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
        $ownWork = $true
    }
    $work = $WorkDir

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
        if ($ownWork) { Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue }
    }
}

function Invoke-JcOnDefect {
    <#
        Build a one-defect archive, run the binary against it, throw the archive
        away. Nothing here is a test-only code path in the engine: it is the
        shipped binary reading a resource file it does not like.
    #>
    param([string]$Defect, [string[]]$JcArgs, [int]$TimeoutSec = 180)

    $work = Join-Path ([IO.Path]::GetTempPath()) ("jcr-fixture-" + [Guid]::NewGuid().ToString('N'))
    try {
        New-MalformedArchive -Defect $Defect -OutDir $work | Out-Null
        return Invoke-Jc $JcArgs $TimeoutSec $work
    }
    finally {
        Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
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
    # Seed 5 rather than $Seed, and the reason is worth keeping: night skips the
    # `rand() % 3` that picks OCEAN0N, so the whole RNG stream shifts and
    # numClouds (rand() % 6) lands on a different value than it does by day. Seed
    # 2 renders clouds by day and none at night purely for that reason. Measured
    # across six seeds at night: 3, 5 and 42 produce clouds; 2, 7 and 11 do not.
    $r = Invoke-Jc @('window', 'nosound', 'maxspeed', 'hotkeys', 'debug', 'night',
                     'seed', '5', 'frames', '900') 900
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

Write-Host "`n== malformed resources are refused, not executed ==" -ForegroundColor Cyan

# THE SHIPPED ARCHIVE CANNOT REACH ANY OF THESE. Measured over it: every TTM and
# ADS script decodes to its exact last byte, every BMP and SCR sums to exactly
# its decoded size, every TTM's bytecode holds exactly as many tags as its TAG:
# chunk declares, every ADS names slots 1..7 of 10, every resource name is 8 to
# 12 characters. Zero margin on all five, which is precisely why an off-by-one
# in a length field is a memory-safety bug and not a cosmetic one - and why the
# input has to be synthesised (tests/New-MalformedArchive.ps1).
#
# Each assertion checks the MESSAGE as well as the exit code. A refusal that does
# not name the offending value is not much better than a crash: the exit code
# alone would also be satisfied by the process dying for an unrelated reason.

It 'a TTM with more tags in its bytecode than its TAG: chunk declares is refused' {
    $r = Invoke-JcOnDefect 'ttm-extra-tag' @('window', 'nosound', 'maxspeed', 'hotkeys',
                                             'frames', '5', 'ttm', 'BAD.TTM')
    ($r.Code -ne 0) -and ($r.Output -match 'BAD\.TTM') -and
        ($r.Output -match 'declares more tags') -and ($r.Output -match 'tag #2')
}

It 'a TTM opcode whose arguments run past the end of the script is refused' {
    $r = Invoke-JcOnDefect 'ttm-args-past-end' @('window', 'nosound', 'maxspeed', 'hotkeys',
                                                 'frames', '5', 'ttm', 'BAD.TTM')
    ($r.Code -ne 0) -and ($r.Output -match 'opcode 4004') -and
        ($r.Output -match 'needs 8 argument bytes')
}

It 'and the dump disassembler refuses that same truncated TTM' {
    # dump.c reaches the bounded reader with no pre-check in front of it, so this
    # is what exercises peekUint16's own refusal rather than the VM's. Headless,
    # which also means it is the one of these the Linux container can run.
    $r = Invoke-JcOnDefect 'ttm-args-past-end' @('dump') 300
    ($r.Code -ne 0) -and ($r.Output -match 'BAD\.TTM') -and
        ($r.Output -match 'runs past the end of the 4-byte script')
}

It 'a 12-argument TTM opcode is decoded rather than overflowing the argument buffer' {
    # The POSITIVE half, and the one that pins the buffer size. A TTM opcode's
    # low nibble is its argument count and 0x0f selects the string form, so the
    # numeric form admits up to 14 words; the shipped archive never exceeds 6.
    # This script is well-formed and must simply RUN - it is the only thing here
    # that would have written past the old ten-word buffer.
    $r = Invoke-JcOnDefect 'ttm-wide-args' @('window', 'nosound', 'maxspeed', 'hotkeys',
                                             'frames', '5', 'ttm', 'WIDE.TTM')
    (-not $r.TimedOut) -and ($r.Code -eq 0)
}

It 'an ADS naming a TTM slot outside the slot table is refused' {
    $r = Invoke-JcOnDefect 'ads-bad-slot' @('window', 'nosound', 'maxspeed', 'hotkeys',
                                            'frames', '5', 'ads', 'BAD.ADS', '1')
    ($r.Code -ne 0) -and ($r.Output -match 'names TTM slot 60000') -and
        ($r.Output -match 'only 10 slots exist')
}

It 'an ADS opcode whose arguments run past the end of the script is refused' {
    $r = Invoke-JcOnDefect 'ads-args-past-end' @('window', 'nosound', 'maxspeed', 'hotkeys',
                                                 'frames', '5', 'ads', 'BAD.ADS', '1')
    ($r.Code -ne 0) -and ($r.Output -match 'opcode 2005') -and
        ($r.Output -match 'needs 8 argument bytes')
}

It 'a BMP declaring more images than a sprite slot holds is refused' {
    $r = Invoke-JcOnDefect 'bmp-too-many-images' @('window', 'nosound', 'maxspeed', 'hotkeys',
                                                   'frames', '5', 'ttm', 'LOAD.TTM')
    ($r.Code -ne 0) -and ($r.Output -match 'declares 200 images') -and
        ($r.Output -match 'at most 120')
}

It 'a BMP whose image table outruns its pixel data is refused when loaded' {
    $r = Invoke-JcOnDefect 'bmp-short-pixels' @('window', 'nosound', 'maxspeed', 'hotkeys',
                                                'frames', '5', 'ttm', 'LOAD.TTM')
    ($r.Code -ne 0) -and ($r.Output -match 'needs 8 pixel bytes at offset 8')
}

It 'and refused on the headless dump path, which walks the same pixels separately' {
    # dump.c carries its own copy of the decoder, which is how the disassemblers
    # and the VM drifted apart in the first place. Fixing one is not fixing both.
    $r = Invoke-JcOnDefect 'bmp-short-pixels' @('dump') 300
    ($r.Code -ne 0) -and ($r.Output -match 'needs 8 pixel bytes at offset 8')
}

It 'a resource name shorter than its own type suffix is refused' {
    $r = Invoke-JcOnDefect 'short-resource-name' @('dump') 300
    ($r.Code -ne 0) -and ($r.Output -match '1-character name') -and
        ($r.Output -match 'type suffix')
}

Write-Host ""
if ($script:failed) {
    Write-Host ("{0} passed, {1} failed" -f $script:passed, $script:failed) -ForegroundColor Red
    exit 1
}
Write-Host ("{0} passed, 0 failed" -f $script:passed) -ForegroundColor Green
exit 0
