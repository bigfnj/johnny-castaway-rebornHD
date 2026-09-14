#Requires -Version 5.1
<#
    Drive the /p preview mode of the screensaver with a REAL parent window.

    WHY THIS EXISTS. /p is the one screensaver path that cannot be exercised from
    a command line: Windows passes the HWND of the small monitor in the Screen
    Saver settings dialog and expects the screensaver to draw INSIDE it, as a
    child window. The classic failure still "runs": a preview that creates a
    top-level fullscreen window and steals the foreground while the user is in
    Settings. That is precisely what this engine did before, because parseArgs
    discarded unknown tokens and /p fell through to the default screensaver.

    So this hands over a real handle and asserts the engine became a CHILD of it
    and owns no top-level window at all.
#>
[CmdletBinding()]
param(
    [string]$Scr,
    # The CONSOLE build, for the focus checks at the end. They need to run the
    # same engine both with and without /s, and the .scr is /SUBSYSTEM:WINDOWS so
    # its diagnostics go nowhere a harness can read them.
    [string]$Exe,
    [int]$Seconds = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repo = Split-Path $PSScriptRoot -Parent
if (-not $Scr) { $Scr = Join-Path $repo 'build\Release\jc_reborn.scr' }
if (-not $Exe) { $Exe = Join-Path (Split-Path $Scr -Parent) 'jc_reborn.exe' }

if (-not (Test-Path -LiteralPath $Scr)) {
    Write-Host "FAIL no screensaver binary at $Scr" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path -LiteralPath $Exe)) {
    Write-Host "FAIL no console binary at $Exe" -ForegroundColor Red
    exit 1
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

#  EnumChildWindows / EnumWindows rather than FindWindowEx.
#
#  FindWindowEx through P/Invoke did not match this window even though it exists
#  and is an immediate child - string marshalling for the class name is the usual
#  culprit and not worth debugging when enumeration is both reliable and more
#  informative: it can tell "created nothing" apart from "created a TOP-LEVEL
#  window", which are completely different failures.
Add-Type @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class JcWin {
    // Loading the .scr AS A DATA FILE reads its resources without running a line
    // of its code - which matters, because running it is what the rest of this
    // script is carefully arranging to do under controlled conditions.
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    public static extern IntPtr LoadLibraryExW(string f, IntPtr h, uint flags);
    [DllImport("kernel32.dll")] public static extern bool FreeLibrary(IntPtr h);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern int LoadStringW(IntPtr h, uint id, StringBuilder b, int n);

    public static string ScreensaverName(string path) {
        IntPtr h = LoadLibraryExW(path, IntPtr.Zero, 0x00000002 /* AS_DATAFILE */);
        if (h == IntPtr.Zero) return "<could not load " + path + ">";
        try {
            var b = new StringBuilder(256);
            int n = LoadStringW(h, 1, b, 256);
            return n > 0 ? b.ToString() : "";
        }
        finally { FreeLibrary(h); }
    }

    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll", CharSet=CharSet.Ansi)]
    public static extern int GetClassNameA(IntPtr h, StringBuilder b, int m);

    public static string Cls(IntPtr h) {
        var b = new StringBuilder(256); GetClassNameA(h, b, 256); return b.ToString();
    }
    public static List<IntPtr> TopLevelOf(uint want) {
        var res = new List<IntPtr>();
        EnumWindows((h, l) => { uint pid; GetWindowThreadProcessId(h, out pid);
                                if (pid == want) res.Add(h); return true; }, IntPtr.Zero);
        return res;
    }
    public static List<IntPtr> ChildrenOf(IntPtr parent) {
        var res = new List<IntPtr>();
        EnumChildWindows(parent, (h, l) => { res.Add(h); return true; }, IntPtr.Zero);
        return res;
    }

    //  POSTED, not synthesized by really stealing the foreground.
    //
    //  SetForegroundWindow is subject to Windows' foreground-lock rules and
    //  fails silently depending on which process last received input, so a test
    //  built on it would be flaky in exactly the way a test must not be. What is
    //  under test here is the ENGINE'S HANDLER, not whether Windows sends
    //  WM_ACTIVATEAPP on deactivation - that part is documented OS behaviour.
    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr h, int id);
    [DllImport("user32.dll", SetLastError=true)]
    public static extern IntPtr SendMessageTimeoutW(IntPtr h, uint msg, IntPtr w,
        IntPtr l, uint flags, uint timeout, out IntPtr result);

    public static int ComboMessage(IntPtr h, uint msg, int value) {
        IntPtr result;
        if (SendMessageTimeoutW(h, msg, new IntPtr(value), IntPtr.Zero, 2, 2000, out result) == IntPtr.Zero)
            throw new InvalidOperationException("Art style control did not answer in two seconds");
        return result.ToInt32();
    }

    public const uint WM_ACTIVATEAPP = 0x001C;

    public static bool SendDeactivate(IntPtr h) {
        return PostMessageW(h, WM_ACTIVATEAPP, IntPtr.Zero, IntPtr.Zero);
    }
}
'@

$script:passed = 0
$script:failed = 0
function Check { param([string]$Name, [bool]$Ok, [string]$Detail='')
    if ($Ok) { Write-Host "  ok   $Name" -ForegroundColor Green; $script:passed++ }
    else { Write-Host "  FAIL $Name$(if($Detail){" - $Detail"})" -ForegroundColor Red; $script:failed++ }
}

Write-Host "`n== Windows can tell the user what this is ==" -ForegroundColor Cyan
#  The Screen Saver dropdown shows string resource 1. With no string table
#  Windows falls back to the file name, so the entry read "jc_reborn" - the one
#  piece of this work every user was guaranteed to see.
$name = [JcWin]::ScreensaverName((Resolve-Path -LiteralPath $Scr).Path)
Check 'the .scr carries the name shown in the Screen Saver dropdown' `
    ($name -eq 'Johnny Reborn') "string resource 1 = '$name'"

#  VERSIONINFO, asserted against CMakeLists.txt rather than against a literal.
#  The point of feeding the version to the .rc from CMake was to stop it living
#  in more than one place; a test that hard-coded the number here would put it
#  back. This turns any future drift between source, binary and tag into a test
#  failure instead of something discovered in a bug report.
$cmakeText = Get-Content (Join-Path $repo 'CMakeLists.txt') -Raw
if ($cmakeText -match 'project\(jc_reborn VERSION (\d+\.\d+\.\d+)') {
    $expected = $Matches[1]
    $vi = [System.Diagnostics.FileVersionInfo]::GetVersionInfo((Resolve-Path -LiteralPath $Scr).Path)
    $got = '{0}.{1}.{2}' -f $vi.FileMajorPart, $vi.FileMinorPart, $vi.FileBuildPart
    Check 'its embedded version matches CMakeLists.txt' ($got -eq $expected) `
        "binary says '$got', CMakeLists.txt says '$expected'"
    Check 'and it identifies itself as the screensaver, not the console build' `
        ($vi.OriginalFilename -eq 'jc_reborn.scr') "OriginalFilename = '$($vi.OriginalFilename)'"
}
else {
    Check 'its embedded version matches CMakeLists.txt' $false 'no version found in CMakeLists.txt'
}

Write-Host "`n== /p preview draws into the window it is given ==" -ForegroundColor Cyan

$form = New-Object System.Windows.Forms.Form
$form.Text = 'jc_reborn preview host'
# About the size of the real Settings preview monitor, so the downscale path is
# exercised at the ratio it will actually face (the engine renders at 1280x960).
$form.ClientSize = New-Object System.Drawing.Size(152, 112)
$form.StartPosition = 'CenterScreen'
$form.Show()
[System.Windows.Forms.Application]::DoEvents()

$parent = $form.Handle
$proc = $null
$previewProfile = Join-Path ([IO.Path]::GetTempPath()) ('jcr-preview-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $previewProfile -Force | Out-Null
try {
    #  CreateProcess, NOT Start-Process. Start-Process uses ShellExecute, and
    #  .scr is a registered shell type whose DEFAULT VERB is Install/Config
    #  rather than Open - so the arguments are discarded and the config dialog
    #  opens instead, which looks exactly like a broken preview.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Scr
    $psi.Arguments = "/p $parent"
    $psi.UseShellExecute = $false
    $psi.EnvironmentVariables['HOME'] = $previewProfile
    $psi.EnvironmentVariables['USERPROFILE'] = $previewProfile
    $proc = [System.Diagnostics.Process]::Start($psi)

    # Startup is not instant: a 3.8 MB archive is opened and every resource
    # parsed before any window exists.
    $deadline = (Get-Date).AddSeconds($Seconds)
    $child = [IntPtr]::Zero
    while ((Get-Date) -lt $deadline) {
        [System.Windows.Forms.Application]::DoEvents()
        foreach ($h in [JcWin]::ChildrenOf($parent)) {
            if ([JcWin]::Cls($h) -eq 'JCRebornWindow') { $child = $h; break }
        }
        if ($child -ne [IntPtr]::Zero) { break }
        Start-Sleep -Milliseconds 200
    }

    $topLevel = @([JcWin]::TopLevelOf([uint32]$proc.Id))

    Check 'a preview window appeared inside the host' ($child -ne [IntPtr]::Zero) `
        "$($topLevel.Count) top-level window(s) owned by the process instead"

    if ($child -ne [IntPtr]::Zero) {
        Check 'it is parented to the supplied handle' ([JcWin]::GetParent($child) -eq $parent)
        Check 'it is visible' ([JcWin]::IsWindowVisible($child))
    }

    #  THE ASSERTION THAT MATTERS. A preview that opens a window of its own is
    #  the broken behaviour, whether or not it also made a child.
    Check 'and the process owns NO top-level window' ($topLevel.Count -eq 0) `
        (($topLevel | ForEach-Object { [JcWin]::Cls($_) }) -join ', ')

    Check 'and it did not steal the foreground' ([JcWin]::GetForegroundWindow() -ne $child)

    # Still alive after a moment means it is rendering, not that it died on
    # startup - which a single handle check would not distinguish.
    Start-Sleep -Seconds 2
    $proc.Refresh()
    Check 'and it is still running rather than having exited immediately' (-not $proc.HasExited)
}
finally {
    if ($proc -and -not $proc.HasExited) {
        # The shell ends a preview by destroying the parent window; do the same,
        # then terminate as a backstop so no process is left behind.
        $form.Close()
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 800
        $proc.Refresh()
        if (-not $proc.HasExited) { $proc.Kill() }
    }
    $form.Dispose()
    if ($proc) { $proc.WaitForExit(); $proc.Dispose() }
    $previewResolved = [IO.Path]::GetFullPath($previewProfile)
    $previewTempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not $previewResolved.StartsWith($previewTempRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing cleanup outside temporary root: $previewResolved"
    }
    Remove-Item -LiteralPath $previewResolved -Recurse -Force
}

#  ---------------------------------------------------------------------------
#  A screensaver must give way when something else takes the foreground, which
#  is what DefScreenSaverProc does. A background utility must NOT. Both come out
#  of the same binary, so the discriminator is the /s switch, and these two
#  checks are a matched pair: the first proves the rule fires, the second proves
#  the gate holds. Deleting the gate has to break exactly the second one.
#  ---------------------------------------------------------------------------

function Test-Deactivate {
    param([string[]]$JcArgs, [int]$WaitSec = 8)

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Exe
    $psi.Arguments = ($JcArgs -join ' ')
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    # Its own profile, so a saved story day cannot change which scene runs.
    $home2 = Join-Path ([IO.Path]::GetTempPath()) ("jcr-focus-" + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $home2 | Out-Null
    $psi.EnvironmentVariables['HOME'] = $home2
    $psi.EnvironmentVariables['USERPROFILE'] = $home2

    $p = [System.Diagnostics.Process]::Start($psi)
    try {
        # Wait for the window to exist before posting anything at it.
        $hwnd = [IntPtr]::Zero
        $deadline = (Get-Date).AddSeconds(20)
        while ((Get-Date) -lt $deadline -and -not $p.HasExited) {
            foreach ($h in [JcWin]::TopLevelOf([uint32]$p.Id)) {
                if ([JcWin]::Cls($h) -eq 'JCRebornWindow') { $hwnd = $h; break }
            }
            if ($hwnd -ne [IntPtr]::Zero) { break }
            Start-Sleep -Milliseconds 200
        }
        if ($hwnd -eq [IntPtr]::Zero) {
            return [pscustomobject]@{ Exited = $false; Reason = 'no window ever appeared' }
        }

        [void][JcWin]::SendDeactivate($hwnd)
        $exited = $p.WaitForExit($WaitSec * 1000)
        # $(...) around the if: a bare `if` inside a hashtable literal is a parse
        # error under Windows PowerShell 5.1, which is what gate.ps1 runs this
        # with, and it would not have shown up under pwsh.
        $why = $(if ($exited) { "exit $($p.ExitCode)" } else { 'still running' })
        return [pscustomobject]@{ Exited = $exited; Reason = $why }
    }
    finally {
        if (-not $p.HasExited) { try { $p.Kill() } catch { } }
        $p.WaitForExit()
        $p.Dispose()
        Remove-Item -LiteralPath $home2 -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n== losing the foreground ends a screensaver, not a background run ==" -ForegroundColor Cyan

$r = Test-Deactivate @('/s', 'window', 'nosound', 'hotkeys', 'frames', '1000000')
Check 'with /s, deactivation ends it' $r.Exited $r.Reason

# THE GATE. This is the one that protects running jc_reborn.exe as a background
# window: no /s means focus is none of its business.
$r = Test-Deactivate @('window', 'nosound', 'hotkeys', 'frames', '1000000') 5
Check 'without /s, deactivation is ignored' (-not $r.Exited) $r.Reason

function Test-ArtConfigDialog {
    param([switch]$Cancel, [switch]$ProgressChanges, [string]$InitialStyle = 'hd')
    $dir = Join-Path ([IO.Path]::GetTempPath()) ('jcr-dialog-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $profile = Join-Path $dir '.jc_reborn'
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $initial = "currentDay=7`ndate=123`nartStyle=$InitialStyle`n"
    [IO.File]::WriteAllText($profile, $initial, $utf8)
    # No archive beside this copied .scr or in its working directory. Settings
    # must remain available even when the runtime data pack is absent.
    $isolatedScr = Join-Path $dir 'jc_reborn.scr'
    Copy-Item -LiteralPath $Scr -Destination $isolatedScr
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $isolatedScr
    $psi.Arguments = '/c'
    $psi.WorkingDirectory = $dir
    $psi.UseShellExecute = $false
    $psi.EnvironmentVariables['HOME'] = $dir
    $psi.EnvironmentVariables['USERPROFILE'] = $dir
    $p = [Diagnostics.Process]::Start($psi)
    $label = if ($Cancel) { "Cancel ($InitialStyle saved)" } elseif ($ProgressChanges) { 'OK after story progress changes' } else { 'OK' }
    try {
        $dialog = [IntPtr]::Zero
        $deadline = (Get-Date).AddSeconds(10)
        while ((Get-Date) -lt $deadline -and -not $p.HasExited) {
            foreach ($h in [JcWin]::TopLevelOf([uint32]$p.Id)) {
                if ([JcWin]::Cls($h) -eq '#32770') { $dialog = $h; break }
            }
            if ($dialog -ne [IntPtr]::Zero) { break }
            Start-Sleep -Milliseconds 100
        }
        $combo = [JcWin]::GetDlgItem($dialog, 201)
        Check "$label config dialog opens without an archive" ($combo -ne [IntPtr]::Zero)
        if ($combo -eq [IntPtr]::Zero) { return }
        $count = [JcWin]::ComboMessage($combo, 0x0146, 0) # CB_GETCOUNT
        $selection = [JcWin]::ComboMessage($combo, 0x0147, 0) # CB_GETCURSEL
        $initialIndex = if ($InitialStyle -eq 'cartoon') { 1 } else { 0 }
        Check "$label shows both styles and the saved selection" ($count -eq 2 -and $selection -eq $initialIndex)
        [void][JcWin]::ComboMessage($combo, 0x014E, (1 - $initialIndex)) # CB_SETCURSEL
        if ($ProgressChanges) {
            [IO.File]::WriteAllText($profile, "currentDay=8`ndate=456`nartStyle=hd`n", $utf8)
        }
        $command = if ($Cancel) { 2 } else { 1 }
        [void][JcWin]::PostMessageW($dialog, 0x0111, [IntPtr]$command, [IntPtr]::Zero)
        $exited = $p.WaitForExit(5000)
        Check "$label closes through the dialog action" ($exited -and $p.ExitCode -eq 0)
        $savedText = [IO.File]::ReadAllText($profile)
        if ($Cancel) {
            Check "$label leaves settings byte-identical" ($savedText -ceq $initial)
        }
        else {
            $day = if ($ProgressChanges) { 8 } else { 7 }
            $date = if ($ProgressChanges) { 456 } else { 123 }
            Check "$label saves Cartoon and retains the latest story progress" (
                $savedText -match '(?m)^artStyle=cartoon\r?$' -and
                $savedText -match "(?m)^currentDay=$day`r?$" -and $savedText -match "(?m)^date=$date`r?$")
        }
    }
    finally {
        if (-not $p.HasExited) { $p.Kill() }
        $p.WaitForExit(); $p.Dispose()
        $resolved = [IO.Path]::GetFullPath($dir)
        $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
        if (-not $resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing cleanup outside temporary root: $resolved"
        }
        # Windows can retain the copied executable briefly after WaitForExit
        # has completed. Retry cleanup for at most two seconds, then surface
        # the real error instead of silently leaving a fixture behind.
        for ($attempt = 0; $attempt -lt 10; $attempt++) {
            try {
                Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
                break
            }
            catch {
                if ($attempt -eq 9) { throw }
                Start-Sleep -Milliseconds 200
            }
        }
    }
}

Write-Host "`n== art style settings use a real Windows dialog ==" -ForegroundColor Cyan
Test-ArtConfigDialog -Cancel
Test-ArtConfigDialog
Test-ArtConfigDialog -ProgressChanges
Test-ArtConfigDialog -Cancel -InitialStyle cartoon

Write-Host ''
if ($script:failed) {
    Write-Host "$($script:passed) passed, $($script:failed) failed" -ForegroundColor Red
    exit 1
}
Write-Host "$($script:passed) passed, 0 failed" -ForegroundColor Green
exit 0
