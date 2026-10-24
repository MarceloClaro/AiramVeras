param([Parameter(Mandatory=$true)][string]$Python,[Parameter(Mandatory=$true)][string]$Config,[Parameter(Mandatory=$true)][string]$Artifacts)
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -m airam gate --nome release --config $Config --artefatos $Artifacts
    $gateExit = $LASTEXITCODE
} finally { Pop-Location }
exit $gateExit
