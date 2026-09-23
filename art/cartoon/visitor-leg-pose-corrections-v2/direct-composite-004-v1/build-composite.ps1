$ErrorActionPreference = 'Stop'
$family = Split-Path -Parent $PSScriptRoot
$upper = Join-Path $family 'generation/SSUZY1.BMP/004-generated-v3.png'
$lower = Join-Path $family 'generation/SSUZY1.BMP/003-generated-v2.png'
function Invoke-ImageMagick {
    param([string[]]$ImageArguments)
    & magick @ImageArguments
    if ($LASTEXITCODE -ne 0) { throw "ImageMagick failed with exit code $LASTEXITCODE" }
}
$upperMask = Join-Path $PSScriptRoot 'upper-mask.png'
$lowerMask = Join-Path $PSScriptRoot 'lower-mask.png'
$upperCut = Join-Path $PSScriptRoot 'upper-cut.png'
$lowerCut = Join-Path $PSScriptRoot 'lower-cut.png'
$output = Join-Path $PSScriptRoot '004-composite-v1.png'
Invoke-ImageMagick @('-size','1642x958','xc:none','-fill','white','-draw',
    'polygon 0,0 700,0 700,480 558,480 585,525 613,570 646,619 672,661 686,693 676,719 652,742 620,760 580,777 545,788 534,790 533,796 527,804 518,813 503,819 495,819 495,958 0,958',
    $upperMask)
Invoke-ImageMagick @('-size','1724x912','xc:none','-fill','white','-draw',
    'polygon 704,0 1724,0 1724,912 658,912 658,731 649,721 665,680 680,630 697,587 704,557',
    $lowerMask)
Invoke-ImageMagick @($upper,$upperMask,'-compose','DstIn','-composite',$upperCut)
Invoke-ImageMagick @($lower,$lowerMask,'-compose','DstIn','-composite',$lowerCut)
Invoke-ImageMagick @('-size','1642x958','xc:none',$lowerCut,'-geometry','-120+68',
    '-compose','Over','-composite',$upperCut,'-geometry','+0+0','-compose','Over',
    '-composite','-define','png:color-type=6',$output)
Write-Output $output
