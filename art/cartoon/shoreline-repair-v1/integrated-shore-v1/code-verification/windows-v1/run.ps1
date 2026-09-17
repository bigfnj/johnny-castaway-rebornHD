#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) { throw 'Expected Windows PowerShell 5.1' }
Write-Output ('WITNESS Windows PowerShell ' + $PSVersionTable.PSVersion)
$copyRoot = Join-Path $PSScriptRoot 'source'
$buildPath = Join-Path $copyRoot 'build'
$exePath = Join-Path $buildPath 'Release\jc_reborn.exe'
Write-Output 'STEP configure'
& cmake -S $copyRoot -B $buildPath -A x64
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'STEP build required targets'
& cmake --build $buildPath --config Release --target jc_reborn jc_png_test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'STEP base smoke'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $copyRoot 'tests\Invoke-SmokeTests.ps1') -Exe $exePath
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'STEP art smoke'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $copyRoot 'tests\Invoke-ArtStyleTests.ps1') -Exe $exePath -Phase Smoke -KeepArtifacts (Join-Path $PSScriptRoot 'art-smoke-artifacts')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'STEP portable PNG positive'
& (Join-Path $buildPath 'Release\jc_png_test.exe')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'STEP Windows 5.1 mutation writer'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $copyRoot 'tests\Test-ArtMutations.ps1') -Config Release
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output 'PASS isolated PowerShell 5.1 mutation run'
exit 0
