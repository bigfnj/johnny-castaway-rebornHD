#Requires -Version 5.1
<#
    Real-engine art-style integration tests. A tiny RESOURCE.MAP/.001 archive
    drives the ordinary TTM loader, PNG decoder, compositing, flip, clip and
    capture paths. Deliberate colors make the oracle independent of generated
    art and of random scene selection. No graphics functions are mocked.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [ValidateSet('Smoke', 'Regression', 'All')][string]$Phase = 'All',
    # A named assertion keeps mutation runs bounded to one observable failure.
    [string]$OnlyCheck,
    [string]$KeepArtifacts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'New-MalformedArchive.ps1')
Add-Type -AssemblyName System.Drawing

$Exe = (Resolve-Path -LiteralPath $Exe).Path
$work = Join-Path ([IO.Path]::GetTempPath()) ('jcr-art-test-' + [Guid]::NewGuid().ToString('N'))
$script:failed = 0
$script:passed = 0
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Check-Art {
    param([string]$Name, [bool]$Ok, [string]$Detail = '')
    if ($OnlyCheck -and $Name -ne $OnlyCheck) { return }
    if ($Ok) { Write-Host "  ok   $Name"; $script:passed++ }
    else {
        Write-Host "  FAIL tests/Invoke-ArtStyleTests.ps1: $Name$(if ($Detail) { ' - ' + $Detail })"
        $script:failed++
    }
    if ($OnlyCheck) {
        Write-Host "WITNESS art assertion executed: $Name"
        if ($Ok) { exit 0 } else { exit 1 }
    }
}

function Invoke-ArtProcess {
    param([string[]]$Arguments, [string]$Directory, [string]$Profile, [int]$TimeoutSeconds = 40)
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Exe
    $psi.Arguments = (($Arguments | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }) -join ' ')
    $psi.WorkingDirectory = $Directory
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.EnvironmentVariables['HOME'] = $Profile
    $psi.EnvironmentVariables['USERPROFILE'] = $Profile
    $proc = [Diagnostics.Process]::Start($psi)
    try {
        $stdout = $proc.StandardOutput.ReadToEndAsync()
        $stderr = $proc.StandardError.ReadToEndAsync()
        if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
            $proc.Kill()
            $proc.WaitForExit()
            return [pscustomobject]@{ Code = -999; Text = 'TIMED OUT'; TimedOut = $true }
        }
        $proc.WaitForExit()
        [pscustomobject]@{ Code = $proc.ExitCode; Text = ($stdout.Result + $stderr.Result); TimedOut = $false }
    }
    finally { $proc.Dispose() }
}

function New-ArtPng {
    param([int]$Width = 8, [int]$Height = 4)
    # Columns exercise opaque, transparent, half-alpha, legacy key color,
    # opaque black, quarter-alpha, green and white. Every row is identical.
    $colors = @(
        @(255, 17, 34, 51), @(0, 250, 100, 50), @(128, 200, 100, 50),
        @(255, 168, 0, 168), @(255, 0, 0, 0), @(64, 255, 0, 255),
        @(255, 0, 220, 0), @(255, 255, 255, 255))
    $bmp = New-Object System.Drawing.Bitmap($Width, $Height, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $stream = New-Object IO.MemoryStream
    try {
        for ($y = 0; $y -lt $Height; $y++) {
            for ($x = 0; $x -lt $Width; $x++) {
                $c = $colors[$x % $colors.Count]
                $bmp.SetPixel($x, $y, [Drawing.Color]::FromArgb($c[0], $c[1], $c[2], $c[3]))
            }
        }
        $bmp.Save($stream, [Drawing.Imaging.ImageFormat]::Png)
        , $stream.ToArray()
    }
    finally { $stream.Dispose(); $bmp.Dispose() }
}

function Set-ArtEntry {
    param([string]$Archive, [string]$Name, [byte[]]$Bytes)
    $zip = [IO.Compression.ZipFile]::Open($Archive, 'Update')
    try {
        $entry = $zip.GetEntry($Name)
        if ($entry) { $entry.Delete() }
        if ($null -ne $Bytes) {
            $entry = $zip.CreateEntry($Name)
            $stream = $entry.Open()
            try { $stream.Write($Bytes, 0, $Bytes.Length) }
            finally { $stream.Dispose() }
        }
    }
    finally { $zip.Dispose() }
}

function Get-ArtEntry {
    param([string]$Archive, [string]$Name)
    $zip = [IO.Compression.ZipFile]::OpenRead($Archive)
    try {
        $entry = $zip.GetEntry($Name)
        if (-not $entry) { throw "Missing archive fixture source: $Name" }
        $inputStream = $entry.Open()
        $outputStream = New-Object IO.MemoryStream
        try { $inputStream.CopyTo($outputStream); , $outputStream.ToArray() }
        finally { $inputStream.Dispose(); $outputStream.Dispose() }
    }
    finally { $zip.Dispose() }
}

function New-ArtFixture {
    param([string]$Name, [string]$Defect = '')
    $dir = Join-Path $work $Name
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $profile = Join-Path $dir 'profile'
    New-Item -ItemType Directory -Path $profile -Force | Out-Null
    $code = New-ByteBuf
    Add-U16 $code 0xF02F
    Add-Cstr $code 'TEST.BMP'
    Add-U8 $code 0 # string including NUL is odd; TTM strings are padded even
    # A flat 60,60,60 layer is the independently known destination color.
    Add-Raw $code (Get-CodeBytes @(0x2002, 15, 15, 0xA104, 0, 0, 640, 480,
        0xA504, 10, 10, 0, 0, 0xA524, 20, 10, 0, 0,
        0xA504, 638, 10, 0, 0))
    foreach ($unused in 1..10) { Add-U16 $code 0x0FF0 }
    $resources = @(
        @{ Name = 'DEFAULT.PAL'; Payload = (New-PalPayload) },
        @{ Name = 'TEST.BMP'; Payload = (New-BmpPayload 1 @(4) @(2) ([byte[]]@(0xFF, 0xFF, 0xFF, 0xFF))) },
        @{ Name = 'KEEP.BMP'; Payload = (New-BmpPayload 1 @(4) @(2) ([byte[]]@(0xFF, 0xFF, 0xFF, 0xFF))) },
        @{ Name = 'TEST.TTM'; Payload = (New-TtmPayload $code.ToArray() 1 @(0)) })
    $archive = Join-Path $dir 'scrantic_data.zip'
    Write-ResourceArchive $resources $archive | Out-Null
    Set-ArtEntry $archive 'data/hd/manifest.json' ([Text.Encoding]::UTF8.GetBytes('{"scale":2}'))
    Set-ArtEntry $archive 'data/styles/cartoon/manifest.json' ([Text.Encoding]::UTF8.GetBytes(
        '{"id":"cartoon","scale":2,"alpha":"straight","coverage":"partial"}'))
    $png = New-ArtPng
    Set-ArtEntry $archive 'data/hd/BMP/TEST.BMP/000.png' $png
    Set-ArtEntry $archive 'data/styles/cartoon/BMP/TEST.BMP/000.png' $png
    # Keep one real replacement when removing TEST's frame to exercise fallback
    # in a valid partial pack, rather than the distinct empty-pack error.
    Set-ArtEntry $archive 'data/styles/cartoon/BMP/KEEP.BMP/000.png' $png
    switch ($Defect) {
        'missing-cartoon' { Set-ArtEntry $archive 'data/styles/cartoon/BMP/TEST.BMP/000.png' $null }
        'missing-both' {
            Set-ArtEntry $archive 'data/styles/cartoon/BMP/TEST.BMP/000.png' $null
            Set-ArtEntry $archive 'data/hd/BMP/TEST.BMP/000.png' $null
        }
        'wrong-size' { Set-ArtEntry $archive 'data/styles/cartoon/BMP/TEST.BMP/000.png' (New-ArtPng 7 4) }
        'corrupt-png' { Set-ArtEntry $archive 'data/styles/cartoon/BMP/TEST.BMP/000.png' ([byte[]]@(1, 2, 3, 4)) }
        'unsupported-png' {
            $invalid = [byte[]]$png.Clone()
            $invalid[24] = 16 # unsupported IHDR bit depth, before platform decode
            Set-ArtEntry $archive 'data/styles/cartoon/BMP/TEST.BMP/000.png' $invalid
        }
        'missing-manifest' { Set-ArtEntry $archive 'data/styles/cartoon/manifest.json' $null }
        'nested-manifest' {
            Set-ArtEntry $archive 'data/styles/cartoon/manifest.json' ([Text.Encoding]::UTF8.GetBytes(
                '{"metadata":{"id":"cartoon","scale":2,"alpha":"straight","coverage":"partial"}}'))
        }
        'incomplete-pack' {
            Set-ArtEntry $archive 'data/styles/cartoon/BMP/TEST.BMP/000.png' $null
            Set-ArtEntry $archive 'data/styles/cartoon/manifest.json' ([Text.Encoding]::UTF8.GetBytes(
                '{"id":"cartoon","scale":2,"alpha":"straight","coverage":"complete"}'))
        }
    }
    [pscustomobject]@{ Directory = $dir; Profile = $profile; Archive = $archive }
}

function Read-ArtPpm {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { throw "Missing capture: $Path" }
    $bytes = [IO.File]::ReadAllBytes($Path)
    $prefix = [Text.Encoding]::ASCII.GetString($bytes, 0, [Math]::Min(100, $bytes.Length))
    $match = [regex]::Match($prefix, '\AP6\s+(\d+)\s+(\d+)\s+255\r?\n')
    if (-not $match.Success) { throw "Not a binary RGB PPM: $Path" }
    $width = [int]$match.Groups[1].Value
    $height = [int]$match.Groups[2].Value
    if ($bytes.Length -ne ($match.Length + $width * $height * 3)) { throw "Invalid PPM byte count: $Path" }
    [pscustomobject]@{ Width = $width; Height = $height; Offset = $match.Length; Bytes = $bytes }
}

function Test-ArtPixel {
    param($Image, [int]$X, [int]$Y, [int[]]$Rgb)
    $offset = $Image.Offset + ($Y * $Image.Width + $X) * 3
    ($Image.Bytes[$offset] -eq $Rgb[0]) -and ($Image.Bytes[$offset + 1] -eq $Rgb[1]) -and
        ($Image.Bytes[$offset + 2] -eq $Rgb[2])
}

function Capture-ArtFixture {
    param($Fixture, [string]$Style, [string]$Name)
    $capture = Join-Path $Fixture.Directory ($Name + '.ppm')
    $argsForRun = @('window', 'nosound', 'hotkeys', 'maxspeed', 'debug', 'day', 'seed', '9',
        'frames', '5', 'capture', $capture, 'ttm', 'TEST.TTM')
    if ($Style) { $argsForRun += @('style', $Style) }
    $result = Invoke-ArtProcess $argsForRun $Fixture.Directory $Fixture.Profile
    [IO.File]::WriteAllText((Join-Path $Fixture.Directory ($Name + '.log')), $result.Text, $utf8)
    $ok = ($result.Code -eq 0) -and (-not $result.TimedOut) -and
        ($result.Text -match 'stopping after 5 frame') -and (Test-Path -LiteralPath $capture)
    [pscustomobject]@{ Ok = $ok; Result = $result; Capture = $capture }
}

try {
    New-Item -ItemType Directory -Path $work -Force | Out-Null
    $fixture = New-ArtFixture 'valid'
    if ($Phase -ne 'Regression') {
        Write-Host '== art styles: bounded real-engine smoke =='
        foreach ($style in @('hd', 'cartoon')) {
            $run = Capture-ArtFixture $fixture $style ('smoke-' + $style)
            Check-Art "$style loads TEST.TTM and captures a bounded run" $run.Ok $run.Result.Text
        }
        if ($script:failed) { throw 'Art-style smoke failed; pixel/configuration regression was not run' }
    }

    if ($Phase -ne 'Smoke') {
        Write-Host '== portable PNG decoder: premultiplied alpha =='
        $probe = Join-Path (Split-Path $Exe -Parent) 'jc_png_test.exe'
        if (-not (Test-Path -LiteralPath $probe)) { throw "Missing decoder probe: $probe" }
        $probeOutput = & $probe 2>&1
        Check-Art 'portable PNG decoder executes and preserves all alpha controls' (
            $LASTEXITCODE -eq 0 -and ($probeOutput -join "`n") -match 'WITNESS portable PNG decoder executed') ($probeOutput -join "`n")

        Write-Host '== art styles: real rendered pixels =='
        $cartoonRun = Capture-ArtFixture $fixture 'cartoon' 'cartoon'
        $hdRun = Capture-ArtFixture $fixture 'hd' 'hd'
        $defaultRun = Capture-ArtFixture $fixture '' 'default'
        if (-not ($cartoonRun.Ok -and $hdRun.Ok -and $defaultRun.Ok)) {
            throw "Capture precondition failed: $($cartoonRun.Result.Text) $($hdRun.Result.Text) $($defaultRun.Result.Text)"
        }
        $cartoon = Read-ArtPpm $cartoonRun.Capture
        $hd = Read-ArtPpm $hdRun.Capture
        Check-Art 'Cartoon preserves the fixed 1280x960 render dimensions' ($cartoon.Width -eq 1280 -and $cartoon.Height -eq 960)
        Check-Art 'default style produces the same pixels as explicit HD' (
            (Get-FileHash -LiteralPath $defaultRun.Capture).Hash -eq (Get-FileHash -LiteralPath $hdRun.Capture).Hash)
        Check-Art 'opaque color survives PNG channel conversion' (Test-ArtPixel $cartoon 20 20 @(17, 34, 51))
        Check-Art 'fully transparent source preserves destination color' (Test-ArtPixel $cartoon 21 20 @(60, 60, 60))
        Check-Art 'half-alpha source blends over the known destination' (Test-ArtPixel $cartoon 22 20 @(130, 80, 55))
        Check-Art 'quarter-alpha source blends over the known destination' (Test-ArtPixel $cartoon 25 20 @(109, 45, 109))
        Check-Art 'Cartoon retains intentional opaque magenta' (Test-ArtPixel $cartoon 23 20 @(168, 0, 168))
        Check-Art 'HD retains its legacy magenta transparency behavior' (Test-ArtPixel $hd 23 20 @(60, 60, 60))
        Check-Art 'sprite flip reverses actual PNG columns' (
            (Test-ArtPixel $cartoon 40 20 @(255, 255, 255)) -and (Test-ArtPixel $cartoon 47 20 @(17, 34, 51)))
        Check-Art 'right-edge clipping preserves the visible source columns' (
            (Test-ArtPixel $cartoon 1276 20 @(17, 34, 51)) -and (Test-ArtPixel $cartoon 1279 20 @(168, 0, 168)))

        foreach ($defect in @('missing-cartoon', 'missing-both')) {
            $fallback = New-ArtFixture $defect $defect
            $run = Capture-ArtFixture $fallback 'cartoon' $defect
            Check-Art "$defect fallback still completes a bounded capture" $run.Ok $run.Result.Text
            if ($run.Ok) {
                $frame = Read-ArtPpm $run.Capture
                $expected = if ($defect -eq 'missing-cartoon') { @(17, 34, 51) } else { @(60, 60, 60) }
                Check-Art "$defect fallback renders the correct source" (
                    (Test-ArtPixel $frame 20 20 $expected) -and (Test-ArtPixel $frame 23 20 @(60, 60, 60)))
            }
        }
        foreach ($defect in @('wrong-size', 'corrupt-png', 'unsupported-png', 'missing-manifest', 'nested-manifest', 'incomplete-pack')) {
            $broken = New-ArtFixture $defect $defect
            $run = Capture-ArtFixture $broken 'cartoon' $defect
            $path = if ($defect -in @('missing-manifest', 'nested-manifest', 'incomplete-pack')) { 'data/styles/cartoon/manifest.json' } else { 'data/styles/cartoon/BMP/TEST.BMP/000.png' }
            Check-Art "$defect refuses the named asset without timing out" (
                (-not $run.Result.TimedOut) -and ($run.Result.Code -ne 0) -and
                ($run.Result.Text -match [regex]::Escape($path))) $run.Result.Text
        }

        Write-Host '== art styles: persisted setting and transient CLI override =='
        $profilePath = Join-Path $fixture.Profile '.jc_reborn'
        [IO.File]::WriteAllText($profilePath, "currentDay=7`ndate=20260914`n", $utf8)
        $set = Invoke-ArtProcess @('setstyle', 'cartoon') $fixture.Directory $fixture.Profile
        Check-Art 'setstyle cartoon saves without opening graphics' ($set.Code -eq 0 -and -not $set.TimedOut) $set.Text
        $saved = [IO.File]::ReadAllText($profilePath)
        Check-Art 'style persistence retains existing story progress' ($saved -match 'currentDay=7' -and $saved -match 'date=20260914') $saved
        $persisted = Capture-ArtFixture $fixture '' 'persisted'
        Check-Art 'a fresh process uses the saved Cartoon setting' (
            $persisted.Ok -and (Test-ArtPixel (Read-ArtPpm $persisted.Capture) 23 20 @(168, 0, 168))) $persisted.Result.Text
        $override = Capture-ArtFixture $fixture 'hd' 'override'
        Check-Art 'explicit HD overrides the saved style for this run' (
            $override.Ok -and (Test-ArtPixel (Read-ArtPpm $override.Capture) 23 20 @(60, 60, 60))) $override.Result.Text
        Check-Art 'a transient CLI override leaves saved settings unchanged' ($saved -ceq [IO.File]::ReadAllText($profilePath))
        [IO.File]::SetAttributes($profilePath, [IO.FileAttributes]::ReadOnly)
        try {
            $refused = Invoke-ArtProcess @('setstyle', 'hd') $fixture.Directory $fixture.Profile
            Check-Art 'failed settings replacement retains the previous file and reports failure' (
                $refused.Code -ne 0 -and -not $refused.TimedOut -and
                $refused.Text -match 'Could not save' -and ($saved -ceq [IO.File]::ReadAllText($profilePath))) $refused.Text
        }
        finally { [IO.File]::SetAttributes($profilePath, [IO.FileAttributes]::Normal) }
        $bad = Invoke-ArtProcess @('setstyle', 'not-a-style') $fixture.Directory $fixture.Profile
        Check-Art 'unknown style is refused without changing saved settings' (
            (-not $bad.TimedOut) -and $bad.Code -ne 0 -and $bad.Text -match 'not-a-style' -and
            ($saved -ceq [IO.File]::ReadAllText($profilePath))) $bad.Text

        foreach ($invalid in @('not-a-style', ('x' * 200))) {
            # A preceding valid choice catches an overlong-line branch that
            # logs a fallback while accidentally retaining the earlier value.
            [IO.File]::WriteAllText($profilePath, "currentDay=7`ndate=1`nartStyle=cartoon`nartStyle=$invalid`n", $utf8)
            $run = Capture-ArtFixture $fixture '' ('invalid-saved-' + $invalid.Length)
            Check-Art "invalid saved style length $($invalid.Length) uses HD after a preceding Cartoon setting" (
                $run.Ok -and $run.Result.Text -match 'Invalid saved art style' -and
                (Test-ArtPixel (Read-ArtPpm $run.Capture) 23 20 @(60, 60, 60))) $run.Result.Text
        }

        # The real story loop owns day rollover. A TTM-only run cannot prove
        # that its separate config write preserves the style key.
        $storyDir = Join-Path $work 'story-rollover'
        New-Item -ItemType Directory -Path $storyDir -Force | Out-Null
        $storyProfile = Join-Path $storyDir 'profile'
        New-Item -ItemType Directory -Path $storyProfile -Force | Out-Null
        $storyArchive = Join-Path $storyDir 'scrantic_data.zip'
        Copy-Item -LiteralPath (Join-Path (Split-Path $Exe -Parent) 'scrantic_data.zip') -Destination $storyArchive
        Set-ArtEntry $storyArchive 'data/styles/cartoon/manifest.json' ([Text.Encoding]::UTF8.GetBytes(
            '{"id":"cartoon","scale":2,"alpha":"straight","coverage":"partial"}'))
        $backdropSprite = Get-ArtEntry $storyArchive 'data/hd/BMP/BACKGRND.BMP/000.png'
        Set-ArtEntry $storyArchive 'data/styles/cartoon/BMP/BACKGRND.BMP/000.png' $backdropSprite
        $storyConfigPath = Join-Path $storyProfile '.jc_reborn'
        [IO.File]::WriteAllText($storyConfigPath, "currentDay=7`ndate=-1`nartStyle=cartoon`n", $utf8)
        $story = Invoke-ArtProcess @('window', 'nosound', 'hotkeys', 'maxspeed', 'debug', 'day', 'seed', '9', 'frames', '400') $storyDir $storyProfile 120
        $rolled = [IO.File]::ReadAllText($storyConfigPath)
        Check-Art 'real story day rollover preserves the saved Cartoon style' (
            $story.Code -eq 0 -and -not $story.TimedOut -and $story.Text -match 'stopping after 400 frame' -and
            $story.Text -match 'The day of the story is: 8' -and
            $rolled -match '(?m)^currentDay=8\r?$' -and $rolled -match '(?m)^artStyle=cartoon\r?$' -and
            $rolled -notmatch '(?m)^date=-1\r?$') ($story.Text + $rolled)
    }
}
catch {
    Write-Host "FAIL art-style test harness: $($_.Exception.Message)"
    $script:failed++
}
finally {
    if ($KeepArtifacts) {
        New-Item -ItemType Directory -Path $KeepArtifacts -Force | Out-Null
        Copy-Item -LiteralPath $work -Destination $KeepArtifacts -Recurse
        Write-Host "art-style fixtures and captures: $KeepArtifacts"
    }
    $resolved = [IO.Path]::GetFullPath($work)
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not $resolved.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing cleanup outside temporary root: $resolved"
    }
    if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}

if (($script:passed + $script:failed) -eq 0) {
    Write-Host "FAIL tests/Invoke-ArtStyleTests.ps1: no matching assertion executed: $OnlyCheck"
    exit 1
}
Write-Host "$script:passed art-style checks passed, $script:failed failed"
if ($script:failed) { exit 1 }
exit 0
