param(
    [string]$ConfigPath = "",
    [int[]]$Dpis = @(100,125,150,175)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsRoot = Resolve-Path (Join-Path $scriptDir "..")
$aasRoot = Resolve-Path (Join-Path $toolsRoot "..")
Set-Location $toolsRoot

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = "DevTools/UiAuditRunner/config.json"
}
if (-not [System.IO.Path]::IsPathRooted($ConfigPath)) {
    $ConfigPath = Join-Path $toolsRoot $ConfigPath
}

$configFull = $ConfigPath
$uiAuditDir = Join-Path $toolsRoot "ui-audit"

if (-not (Test-Path $configFull)) {
    Write-Error "Config file not found: $configFull"
    exit 1
}

function Update-DpiLabel {
    param($Path, $Dpi)
    $json = Get-Content $Path -Raw | ConvertFrom-Json
    $json.dpiLabel = "$Dpi"
    ($json | ConvertTo-Json -Depth 10) | Set-Content $Path -Encoding UTF8
}

$results = @()

foreach ($dpi in $Dpis) {
    Write-Host "=== UI Audit for DPI $dpi% ==="
    Write-Host "Set Windows display scale to $dpi% now, then press Enter to continue."
    Read-Host | Out-Null

    Update-DpiLabel -Path $configFull -Dpi $dpi

    Write-Host "Running UiAuditRunner..."
    dotnet run --project DevTools/UiAuditRunner/UiAuditRunner.csproj -- $configFull

    $zipName = "ui_audit_pack_$dpi.zip"
    if (-not (Test-Path $uiAuditDir)) {
        New-Item -ItemType Directory -Path $uiAuditDir | Out-Null
    }
    $zipPath = Join-Path $uiAuditDir $zipName
    if (Test-Path $zipPath) {
        Write-Host "Created: $zipPath"
        $results += @{ Dpi = $dpi; Path = $zipPath }
    } else {
        Write-Warning "Zip not found for DPI $dpi"
        $results += @{ Dpi = $dpi; Path = "<missing>" }
    }
}

Write-Host "`n=== Summary ==="
foreach ($r in $results) {
    Write-Host ("DPI {0}: {1}" -f $r.Dpi, $r.Path)
}
