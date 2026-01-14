param(
    [string]$ConfigPath = "",
    [double]$Threshold = 0.5,
    [string]$ReportPath = ""
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

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportPath = Join-Path $aasRoot "artifacts/ui_diff_report.txt"
} elseif (-not [System.IO.Path]::IsPathRooted($ReportPath)) {
    $ReportPath = Join-Path $aasRoot $ReportPath
}

$tessdata = Join-Path $maelstromRoot "src/ProjectMaelstrom/tessdata"
if (Test-Path $tessdata) {
    $env:TESSDATA_PREFIX = $tessdata
}

$baselineDir = Join-Path $toolsRoot "ui-audit/ui_baseline"
$currentDir = Join-Path $toolsRoot "ui-audit/ui_current"

if (-not (Test-Path $baselineDir)) {
    Write-Error "Baseline not found at '$baselineDir'. Run ops/ui_set_baseline.ps1 first."
    exit 1
}

Write-Host "== UI regression check =="
if (Test-Path $currentDir) {
    Write-Host "Cleaning $currentDir ..."
    Remove-Item $currentDir -Recurse -Force
}
New-Item -ItemType Directory -Path $currentDir | Out-Null

Write-Host "Capturing current UI to $currentDir ..."
dotnet run --project DevTools/UiAuditSelfCapture/UiAuditSelfCapture.csproj -- $ConfigPath --out $currentDir

$reportDir = Split-Path $ReportPath -Parent
if ([string]::IsNullOrWhiteSpace($reportDir)) {
    $reportDir = "."
}
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}
$ReportPath = Join-Path (Resolve-Path $reportDir).ProviderPath (Split-Path $ReportPath -Leaf)

$argsList = @(
    "--baseline", $baselineDir,
    "--current", $currentDir,
    "--threshold", $Threshold.ToString(),
    "--report", $ReportPath
)

Write-Host "Running UiAuditDiff (threshold $Threshold) ..."
dotnet run --project DevTools/UiAuditDiff/UiAuditDiff.csproj -- @argsList
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "UI regression check PASSED. Report: $ReportPath"
} else {
    Write-Host "UI regression check FAILED (code $exitCode). Report: $ReportPath"
}

exit $exitCode
