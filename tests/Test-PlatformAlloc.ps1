#Requires -Version 5.1
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Exe,
      [ValidateSet('Smoke','Regression','All')][string]$Phase = 'All')
$ErrorActionPreference = 'Stop'
$cases = @('success','png-success','surface-struct','surface-pixels','borrowed-wrapper','window-1','window-2','window-3','native-window','native-context','png-wrapper')
if ($Phase -eq 'Smoke') { $cases = @('success','png-success') }
elseif ($Phase -eq 'Regression') { $cases = @('surface-struct','surface-pixels','borrowed-wrapper','window-1','window-2','window-3','native-window','native-context','png-wrapper') }
foreach ($case in $cases) {
    $source = 'platform/platform_windows.c'
    if ($case -like 'png-*') { $source = 'platform/png_loader.c' }
    $output = & $Exe $case 2>&1
    if ($LASTEXITCODE -ne 0 -or -not ($output -match "WITNESS platform allocation $case PASS")) {
        Write-Error "FAIL $source allocation $case`: $output"
        exit 1
    }
    Write-Host "PASS platform allocation $case"
}
