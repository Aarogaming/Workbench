. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

$repo = Get-ProjectRoot -ProjectName "AaroneousAutomationSuite"
if (-not $repo) { return }

$guildDir = Join-Path $repo "artifacts\guild\to_hub"

if (-not (Test-Path $guildDir)) {
    Write-AASLog "Creating guild directory at $guildDir" "INFO"
    New-Item -ItemType Directory -Path $guildDir -Force
}

Write-AASLog "Monitoring guild directory: $guildDir" "SUCCESS"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $guildDir
$watcher.Filter = "*.json"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    Write-Host "[$(Get-Date)] NEW GUILD REQUEST: $name" -ForegroundColor Cyan
}

Register-ObjectEvent $watcher "Created" -Action $action

while ($true) {
    Start-Sleep -Seconds 5
}
