. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

$repo = Get-ProjectRoot -ProjectName "AaroneousAutomationSuite"
if (-not $repo) { return }

$handoffDir = Join-Path $repo "artifacts\handoff\to_hub"

if (-not (Test-Path $handoffDir)) {
    Write-AASLog "Creating handoff directory at $handoffDir" "INFO"
    New-Item -ItemType Directory -Path $handoffDir -Force
}

Write-AASLog "Monitoring handoff directory: $handoffDir" "SUCCESS"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $handoffDir
$watcher.Filter = "*.json"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    Write-Host "[$(Get-Date)] NEW HANDOFF REQUEST: $name" -ForegroundColor Cyan
}

Register-ObjectEvent $watcher "Created" -Action $action

while ($true) {
    Start-Sleep -Seconds 5
}
