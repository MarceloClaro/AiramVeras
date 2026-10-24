param([Parameter(Mandatory=$true)][string]$Python,[Parameter(Mandatory=$true)][string]$Config)
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    & $Python -m airam gate --nome preflight --config $Config
    $gateExit = $LASTEXITCODE
} finally { Pop-Location }
exit $gateExit
