#Requires -Version 5.1
<#
    Synthetic scrantic_data.zip archives carrying ONE deliberate defect each.

    WHY THESE EXIST. The bounds this repository was missing in its two bytecode
    VMs and its resource parsers are all unreachable through the shipped
    archive - measured, not assumed: every one of the 41 TTM and 10 ADS scripts
    decodes to its own exact last byte, all 116 BMPs and all 10 SCRs sum to
    exactly their decoded size, every TTM's bytecode contains exactly as many
    tags as its TAG: chunk declares, and every ADS names TTM slots 1..7 out of
    10. Zero slack everywhere. A check with no reachable input is a check nobody
    can trust, so the input is built here instead.

    HOW THE BINARY IS STEERED ONTO THEM. zipvfs_init() tries the bare path
    "scrantic_data.zip" FIRST, relative to the current directory, and only then
    falls back to locations beside the executable (platform/zipvfs.c). So
    dropping one of these archives into a scratch directory and running the real
    shipped binary there is enough - no build flag, no test-only entry point, no
    change to any file outside tests/.

    Each archive is a genuine RESOURCE.MAP + RESOURCE.001 pair: same 13-byte
    names, same uint32 sizes, same VER:/PAG:/TT3:/TTI:/TAG: chunk layout, and
    real method-1 RLE payloads, because the parser refuses anything else. The
    only thing wrong with each one is the single field the test is about.

    Dot-source this file to get New-MalformedArchive.
#>

Add-Type -AssemblyName System.IO.Compression      | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null


# ---------------------------------------------------------------- byte helpers

function New-ByteBuf {
    New-Object 'System.Collections.Generic.List[byte]'
}

function Add-U8 {
    param([System.Collections.Generic.List[byte]]$B, [long]$V)
    $B.Add([byte]($V -band 0xFF))
}

function Add-U16 {
    param([System.Collections.Generic.List[byte]]$B, [long]$V)
    Add-U8 $B $V
    Add-U8 $B ($V -shr 8)
}

function Add-U32 {
    param([System.Collections.Generic.List[byte]]$B, [long]$V)
    Add-U8 $B $V
    Add-U8 $B ($V -shr 8)
    Add-U8 $B ($V -shr 16)
    Add-U8 $B ($V -shr 24)
}

function Add-Ascii {
    param([System.Collections.Generic.List[byte]]$B, [string]$S)
    foreach ($x in [Text.Encoding]::ASCII.GetBytes($S)) { $B.Add($x) }
}

function Add-Cstr {
    param([System.Collections.Generic.List[byte]]$B, [string]$S)
    Add-Ascii $B $S
    $B.Add([byte]0)
}

# NUL-padded fixed-width field, as the resource file stores names.
function Add-Fixed {
    param([System.Collections.Generic.List[byte]]$B, [string]$S, [int]$N)
    $bytes = [Text.Encoding]::ASCII.GetBytes($S)
    for ($i = 0; $i -lt $N; $i++) {
        if ($i -lt $bytes.Length) { $B.Add($bytes[$i]) } else { $B.Add([byte]0) }
    }
}

function Add-Raw {
    param([System.Collections.Generic.List[byte]]$B, [byte[]]$A)
    foreach ($x in $A) { $B.Add($x) }
}

<#
    Method-1 RLE, literal runs only.

    uncompressRLE() asserts it consumed EXACTLY inSize bytes and fatals
    otherwise, so the encoding has to be exact rather than merely valid: each
    chunk is [count][count literal bytes] with count <= 127, which makes the
    compressed size outSize + ceil(outSize/127).
#>
function Get-RleBytes {
    param([byte[]]$Data)
    $o = New-ByteBuf
    $i = 0
    while ($i -lt $Data.Length) {
        $n = [Math]::Min(127, $Data.Length - $i)
        $o.Add([byte]$n)
        for ($k = 0; $k -lt $n; $k++) { $o.Add($Data[$i + $k]) }
        $i += $n
    }
    , $o.ToArray()
}

# uint16 opcode/argument stream, little-endian, as peekUint16 reads it.
function Get-CodeBytes {
    param([int[]]$Words)
    $o = New-ByteBuf
    foreach ($w in $Words) { Add-U16 $o $w }
    , $o.ToArray()
}


# ------------------------------------------------------------ resource payloads

function New-PalPayload {
    # graphicsInit() calls grLoadPalette(palResources[0]) unconditionally, so
    # every archive that will be used with a graphical mode needs one of these.
    $b = New-ByteBuf
    Add-Ascii $b 'PAL:'
    Add-U16 $b 780
    Add-U8  $b 0
    Add-U8  $b 0
    Add-Ascii $b 'VGA:'
    Add-U32 $b 768                       # four unknown bytes, read individually
    for ($i = 0; $i -lt 256; $i++) {
        $v = $i % 64                     # 6-bit components, as the format stores them
        Add-U8 $b $v; Add-U8 $b $v; Add-U8 $b $v
    }
    , $b.ToArray()
}

function New-TtmPayload {
    param([byte[]]$Code, [int]$NumTags, [int[]]$TagIds)
    $rle = Get-RleBytes $Code
    $b = New-ByteBuf
    Add-Ascii $b 'VER:'; Add-U32 $b 5; Add-Ascii $b '1.0'; Add-U8 $b 0; Add-U8 $b 0
    Add-Ascii $b 'PAG:'; Add-U32 $b 1;  Add-U8 $b 0; Add-U8 $b 0
    Add-Ascii $b 'TT3:'; Add-U32 $b ($rle.Length + 5); Add-U8 $b 1; Add-U32 $b $Code.Length
    Add-Raw   $b $rle
    Add-Ascii $b 'TTI:'; Add-U32 $b 0
    Add-Ascii $b 'TAG:'; Add-U32 $b 0;  Add-U16 $b $NumTags
    foreach ($t in $TagIds) { Add-U16 $b $t; Add-Cstr $b ("tag" + $t) }
    , $b.ToArray()
}

function New-AdsPayload {
    param([byte[]]$Code, [int]$NumTags, [int[]]$TagIds, [object[]]$ResList)
    $rle = Get-RleBytes $Code
    $b = New-ByteBuf
    Add-Ascii $b 'VER:'; Add-U32 $b 5; Add-Ascii $b '1.0'; Add-U8 $b 0; Add-U8 $b 0
    Add-Ascii $b 'ADS:'; Add-U32 $b 0
    Add-Ascii $b 'RES:'; Add-U32 $b 0; Add-U16 $b @($ResList).Count
    foreach ($r in $ResList) { Add-U16 $b $r.Id; Add-Cstr $b $r.Name }
    Add-Ascii $b 'SCR:'; Add-U32 $b ($rle.Length + 5); Add-U8 $b 1; Add-U32 $b $Code.Length
    Add-Raw   $b $rle
    Add-Ascii $b 'TAG:'; Add-U32 $b 0; Add-U16 $b $NumTags
    foreach ($t in $TagIds) { Add-U16 $b $t; Add-Cstr $b ("tag" + $t) }
    , $b.ToArray()
}

function New-BmpPayload {
    param([int]$DeclaredNumImages, [int[]]$Widths, [int[]]$Heights, [byte[]]$Pixels)
    $rle = Get-RleBytes $Pixels
    $b = New-ByteBuf
    Add-Ascii $b 'BMP:'; Add-U16 $b 64; Add-U16 $b 64
    Add-Ascii $b 'INF:'; Add-U32 $b 0; Add-U16 $b $DeclaredNumImages
    foreach ($w in $Widths)  { Add-U16 $b $w }
    foreach ($h in $Heights) { Add-U16 $b $h }
    Add-Ascii $b 'BIN:'; Add-U32 $b ($rle.Length + 5); Add-U8 $b 1; Add-U32 $b $Pixels.Length
    Add-Raw   $b $rle
    , $b.ToArray()
}


# --------------------------------------------------------------- the container

function Write-ResourceArchive {
    param([object[]]$Resources, [string]$ZipPath)

    $res     = New-ByteBuf
    $offsets = @()
    $lengths = @()

    foreach ($r in $Resources) {
        $offsets += $res.Count
        Add-Fixed $res $r.Name 13
        Add-U32   $res $r.Payload.Length
        Add-Raw   $res $r.Payload
        $lengths += ($r.Payload.Length + 17)
    }

    $map = New-ByteBuf
    for ($i = 0; $i -lt 6; $i++) { Add-U8 $map 0 }     # six unknown header bytes
    Add-Fixed $map 'RESOURCE.001' 13
    Add-U16   $map @($Resources).Count
    for ($i = 0; $i -lt @($Resources).Count; $i++) {
        Add-U32 $map $lengths[$i]
        Add-U32 $map $offsets[$i]
    }

    if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }

    $zip = [System.IO.Compression.ZipFile]::Open($ZipPath, 'Create')
    try {
        foreach ($pair in @(
                @{ Name = 'data/RESOURCE.MAP'; Bytes = $map.ToArray() },
                @{ Name = 'data/RESOURCE.001'; Bytes = $res.ToArray() })) {
            $entry  = $zip.CreateEntry($pair.Name)
            $stream = $entry.Open()
            try { $stream.Write($pair.Bytes, 0, $pair.Bytes.Length) }
            finally { $stream.Dispose() }
        }
    }
    finally { $zip.Dispose() }

    $ZipPath
}


# ----------------------------------------------------------------- the defects

function New-MalformedArchive {
    <#
        Writes <OutDir>\scrantic_data.zip carrying exactly one defect and
        returns its path. Run the binary with OutDir as its working directory.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('ttm-extra-tag', 'ttm-args-past-end', 'ttm-wide-args',
                     'ads-bad-slot', 'ads-args-past-end',
                     'bmp-too-many-images', 'bmp-short-pixels',
                     'short-resource-name')]
        [string]$Defect,

        [Parameter(Mandatory = $true)]
        [string]$OutDir
    )

    if (-not (Test-Path -LiteralPath $OutDir)) {
        New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
    }
    $zipPath   = Join-Path $OutDir 'scrantic_data.zip'
    $resources = @(@{ Name = 'DEFAULT.PAL'; Payload = (New-PalPayload) })

    switch ($Defect) {

        'ttm-extra-tag' {
            # Two :TAG opcodes, a TAG: chunk that declares one. The tag table is
            # allocated from the declared count and filled from the bytecode.
            $code = Get-CodeBytes @(0x1111, 1, 0x1111, 2, 0x0FF0)
            $resources += @{ Name = 'BAD.TTM'
                             Payload = (New-TtmPayload $code 1 @(1)) }
        }

        'ttm-args-past-end' {
            # SET_CLIP_ZONE wants four words; two bytes of script follow it.
            $code = Get-CodeBytes @(0x4004, 0)
            $resources += @{ Name = 'BAD.TTM'
                             Payload = (New-TtmPayload $code 1 @(0)) }
        }

        'ttm-wide-args' {
            # NOT malformed: a well-formed opcode whose low nibble asks for 12
            # argument words. Legal in the encoding (0..14), never used by the
            # shipped archive, and eight bytes wider than the old args[10].
            # This one must RUN, which is what proves the buffer is sized for
            # the encoding rather than for the data that happens to ship.
            $words = @(0x000C) + (1..12) + @(0x0FF0)
            $code  = Get-CodeBytes $words
            $resources += @{ Name = 'WIDE.TTM'
                             Payload = (New-TtmPayload $code 1 @(0)) }
        }

        'ads-bad-slot' {
            # RES: entry naming TTM slot 60000; ttmSlots has 10.
            $adsCode = Get-CodeBytes @(0x0001, 0xFFFF)
            $ttmCode = Get-CodeBytes @(0x1111, 1, 0x0FF0)
            $resources += @{ Name = 'OK.TTM'
                             Payload = (New-TtmPayload $ttmCode 1 @(1)) }
            $resources += @{ Name = 'BAD.ADS'
                             Payload = (New-AdsPayload $adsCode 1 @(1) @(
                                 @{ Id = 60000; Name = 'OK.TTM' })) }
        }

        'ads-args-past-end' {
            # ADD_SCENE wants four words; one word of script follows it.
            $adsCode = Get-CodeBytes @(0x0001, 0x2005, 0)
            $ttmCode = Get-CodeBytes @(0x1111, 1, 0x0FF0)
            $resources += @{ Name = 'OK.TTM'
                             Payload = (New-TtmPayload $ttmCode 1 @(1)) }
            $resources += @{ Name = 'BAD.ADS'
                             Payload = (New-AdsPayload $adsCode 1 @(1) @(
                                 @{ Id = 1; Name = 'OK.TTM' })) }
        }

        'bmp-too-many-images' {
            # 200 images into a slot that holds MAX_SPRITES_PER_BMP = 120.
            $n       = 200
            $widths  = @(2) * $n
            $heights = @(2) * $n
            $pixels  = New-Object byte[] ($n * 2)
            $ttmCode = Get-CodeBytes @(0xF02F)                       # LOAD_IMAGE
            $b = New-ByteBuf
            Add-Raw   $b $ttmCode
            Add-Cstr  $b 'BAD.BMP'                                   # 8 bytes, even
            Add-U16   $b 0x0FF0                                      # UPDATE
            $resources += @{ Name = 'BAD.BMP'
                             Payload = (New-BmpPayload $n $widths $heights $pixels) }
            $resources += @{ Name = 'LOAD.TTM'
                             Payload = (New-TtmPayload $b.ToArray() 1 @(0)) }
        }

        'bmp-short-pixels' {
            # Two 4x4 images need 16 pixel bytes; 8 decoded.
            $pixels  = New-Object byte[] 8
            $ttmCode = Get-CodeBytes @(0xF02F)
            $b = New-ByteBuf
            Add-Raw  $b $ttmCode
            Add-Cstr $b 'BAD.BMP'
            Add-U16  $b 0x0FF0
            $resources += @{ Name = 'BAD.BMP'
                             Payload = (New-BmpPayload 2 @(4, 4) @(4, 4) $pixels) }
            $resources += @{ Name = 'LOAD.TTM'
                             Payload = (New-TtmPayload $b.ToArray() 1 @(0)) }
        }

        'short-resource-name' {
            # A one-character name, so resName + strlen(resName) - 4 points three
            # bytes BEFORE the allocation.
            $resources += @{ Name = 'X'; Payload = (New-PalPayload) }
        }
    }

    Write-ResourceArchive $resources $zipPath
}
