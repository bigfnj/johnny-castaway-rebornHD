# Compatibility entrypoint. Local SDK activation happens only in a child shell.
[CmdletBinding()]
param(
    [ValidateSet('Auto', 'Container', 'Local')][string]$Backend = 'Auto',
    [string]$OutputDirectory = $env:JCR_BUILD_DIR,
    [string]$Sdk = $env:EMSDK,
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
try {
    if (-not $OutputDirectory) { $OutputDirectory = Join-Path $repoRoot 'build_web' }
    # Legacy relative JCR_BUILD_DIR values are relative to the invoking directory.
    $outputPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDirectory)
    $pythonPath = @(Get-Command $Python -CommandType Application -ErrorAction Stop)[0].Source
    if ($Backend -eq 'Auto') {
        if ($Sdk) { $Backend = 'Local' } else { $Backend = 'Container' }
    }
    if ($Backend -eq 'Local') {
        if (-not $Sdk) { throw 'scripts/build_web.ps1: Local requires -Sdk or EMSDK' }
        $sdkPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Sdk)
        $shellPath = (Get-Process -Id $PID).Path
        & $shellPath -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'build_web_local.ps1') -Sdk $sdkPath -OutputDirectory $outputPath -Python $pythonPath
    } else {
        & $pythonPath -B (Join-Path $repoRoot 'tools/build_web.py') --backend container --output $outputPath
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} catch {
    [Console]::Error.WriteLine("FAIL $($_.Exception.Message)")
    exit 1
}
