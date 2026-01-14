param(
    [string]$ConfigPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsRoot = Resolve-Path (Join-Path $scriptDir "..")
$aasRoot = Resolve-Path (Join-Path $toolsRoot "..")
$maelstromRoot = Join-Path $aasRoot "Maelstrom"
Set-Location $toolsRoot

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = "DevTools/UiAuditSelfCapture/ui_self_capture_config.json"
}
if (-not [System.IO.Path]::IsPathRooted($ConfigPath)) {
    $ConfigPath = Join-Path $toolsRoot $ConfigPath
}

$tessdata = Join-Path $maelstromRoot "src/ProjectMaelstrom/tessdata"
if (Test-Path $tessdata) {
    $env:TESSDATA_PREFIX = $tessdata
}

$baselineDir = Join-Path $toolsRoot "ui-audit/ui_baseline"

Write-Host "== UI baseline refresh =="
if (Test-Path $baselineDir) {
    Write-Host "Cleaning $baselineDir ..."
    Remove-Item $baselineDir -Recurse -Force
}
New-Item -ItemType Directory -Path $baselineDir | Out-Null

Write-Host "Running UiAuditSelfCapture to $baselineDir ..."
dotnet run --project DevTools/UiAuditSelfCapture/UiAuditSelfCapture.csproj -- $ConfigPath --out $baselineDir

Write-Host "Baseline ready at: $(Resolve-Path $baselineDir)"
