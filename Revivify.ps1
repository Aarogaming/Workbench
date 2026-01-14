. "$PSScriptRoot\log_helper.ps1"

$baseDir = "D:\Dev library"
$workspaceFile = Join-Path $baseDir "AaroneousAutomationSuite\AaroneousAutomationSuite.code-workspace"

if (-not (Test-Path $workspaceFile)) {
    Write-AASLog "Workspace file not found at $workspaceFile" "ERROR"
    return
}

$folders = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive|Assets|Education|Games)" }

$workspaceJson = Get-Content $workspaceFile | ConvertFrom-Json
$newFolders = @()

foreach ($folder in $folders) {
    $relPath = "..\" + $folder.Name
    $newFolders += @{ path = $relPath }
}

$workspaceJson.folders = $newFolders
$workspaceJson | ConvertTo-Json -Depth 10 | Set-Content $workspaceFile

Write-AASLog "Updated workspace folders in $workspaceFile" "SUCCESS"
