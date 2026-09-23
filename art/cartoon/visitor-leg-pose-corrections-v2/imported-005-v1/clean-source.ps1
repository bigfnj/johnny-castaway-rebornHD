$ErrorActionPreference = 'Stop'
$inputPath = Join-Path $PSScriptRoot 'source-screenshot.png'
$repairedPath = Join-Path $PSScriptRoot '005-dot-repaired-v1.png'
$candidatePath = Join-Path $PSScriptRoot 'background-candidates.png'
$floodPath = Join-Path $PSScriptRoot 'background-connected.png'
$alphaPath = Join-Path $PSScriptRoot 'foreground-alpha.png'
$outputPath = Join-Path $PSScriptRoot '005-transparent-v1.png'
function Invoke-Magick {
    param([string[]]$ImageArguments)
    & magick @ImageArguments
    if ($LASTEXITCODE -ne 0) { throw "ImageMagick failed: $LASTEXITCODE" }
}
# Repair only the accidental dot: 21 pixels inside x=196..200, y=141..145.
# Interpolate each affected row between the nearest unaffected skin pixels.
$repairExpression = '((j==141 || j==145) && i>=197 && i<=199) ? ((200-i)*p{196,j}+(i-196)*p{200,j})/4 : ((j>=142 && j<=144 && i>=196 && i<=200) ? ((201-i)*p{195,j}+(i-195)*p{201,j})/6 : u)'
Invoke-Magick @($inputPath, '-channel', 'RGB', '-fx', $repairExpression, '+channel', $repairedPath)
Invoke-Magick @($repairedPath, '-alpha', 'off', '-fx', '(r>0.60 && g>0.60 && b>0.50 && (max(r,max(g,b))-min(r,min(g,b)))<0.16) ? 1 : 0', $candidatePath)
# The narrow gap under the bottle hand is enclosed by the drawing. Clear its
# 9-pixel component and adjacent 1-pixel sliver; retain the separate cream area.
Invoke-Magick @($candidatePath, '-fill', 'red', '-draw', 'color 0,0 floodfill color 34,109 floodfill color 30,120 floodfill', $floodPath)
Invoke-Magick @($floodPath, '-fx', '(r>0.9 && g<0.1 && b<0.1) ? 0 : 1', $alphaPath)
Invoke-Magick @($repairedPath, $alphaPath, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', '-define', 'png:color-type=6', $outputPath)
Invoke-Magick @($outputPath, '-background', '#142936', '-alpha', 'remove', '-alpha', 'off', '-filter', 'point', '-resize', '300%', (Join-Path $PSScriptRoot 'dark-proof.png'))
Invoke-Magick @($repairedPath, '-crop', '32x32+184+128', '+repage', '-scale', '640x640', (Join-Path $PSScriptRoot 'dot-after-proof.png'))
