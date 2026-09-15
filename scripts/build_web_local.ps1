# Child process only: do not dot-source this helper into a caller's session.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Sdk,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [Parameter(Mandatory = $true)][string]$Python
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
try {
    $activation = Join-Path $Sdk 'emsdk_env.ps1'
    if (-not (Test-Path -LiteralPath $activation -PathType Leaf)) {
        throw "scripts/build_web.ps1: missing SDK activation script $activation"
    }
    . $activation
    if (-not $?) { throw "scripts/build_web.ps1: SDK activation failed: $activation" }
    & $Python -B (Join-Path $repoRoot 'tools/build_web.py') --backend local --output $OutputDirectory
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} catch {
    [Console]::Error.WriteLine("FAIL $($_.Exception.Message)")
    exit 1
}
