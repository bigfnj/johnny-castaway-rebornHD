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
    [int]$Seconds = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Scr) {
    $repo = Split-Path $PSScriptRoot -Parent
    $Scr = Join-Path $repo 'build\Release\jc_reborn.scr'
}
if (-not (Test-Path -LiteralPath $Scr)) {
    Write-Host "FAIL no screensaver binary at $Scr" -ForegroundColor Red
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
try {
    #  CreateProcess, NOT Start-Process. Start-Process uses ShellExecute, and
    #  .scr is a registered shell type whose DEFAULT VERB is Install/Config
    #  rather than Open - so the arguments are discarded and the config dialog
    #  opens instead, which looks exactly like a broken preview.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Scr
    $psi.Arguments = "/p $parent"
    $psi.UseShellExecute = $false
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
}

Write-Host ''
if ($script:failed) {
    Write-Host "$($script:passed) passed, $($script:failed) failed" -ForegroundColor Red
    exit 1
}
Write-Host "$($script:passed) passed, 0 failed" -ForegroundColor Green
exit 0
