$ErrorActionPreference = 'Stop'
$inputPath = Join-Path $PSScriptRoot '004-cropped-v1.png'
$candidatePath = Join-Path $PSScriptRoot 'background-candidates.png'
$floodPath = Join-Path $PSScriptRoot 'background-connected.png'
$alphaPath = Join-Path $PSScriptRoot 'foreground-alpha.png'
$outputPath = Join-Path $PSScriptRoot '004-transparent-v1.png'
function Invoke-Magick {
    param([string[]]$ImageArguments)
    & magick @ImageArguments
    if ($LASTEXITCODE -ne 0) { throw "ImageMagick failed: $LASTEXITCODE" }
}
Invoke-Magick @($inputPath, '-alpha', 'off', '-fx', '(r>0.60 && g>0.60 && b>0.50 && (max(r,max(g,b))-min(r,min(g,b)))<0.16) ? 1 : 0', $candidatePath)
Invoke-Magick @($candidatePath, '-fill', 'red', '-draw', 'color 0,0 floodfill', $floodPath)
Invoke-Magick @($floodPath, '-fx', '(r>0.9 && g<0.1 && b<0.1) ? 0 : 1', $alphaPath)
Invoke-Magick @($inputPath, $alphaPath, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', '-define', 'png:color-type=6', $outputPath)

