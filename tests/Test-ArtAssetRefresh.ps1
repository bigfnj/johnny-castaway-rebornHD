#Requires -Version 5.1
<# Native artwork refresh checks use isolated CMake projects and small ZIPs.
   The production archive and application's build tree are never changed. #>
[CmdletBinding()]
param([string]$Generator, [string]$Work, [switch]$VerifyMutation)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$testArgs = @('-B', (Join-Path $PSScriptRoot 'test_runtime_data.py'))
if ($Generator) { $testArgs += @('--generator', $Generator) }
if ($Work) { $testArgs += @('--work', $Work) }
if ($VerifyMutation) { $testArgs += '--mutations' }
& python @testArgs
exit $LASTEXITCODE
