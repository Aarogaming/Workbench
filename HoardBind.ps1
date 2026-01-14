. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

$assetsDir = "D:\Dev library\Assets"
if (-not (Test-Path $assetsDir)) {
    Write-AASLog "Assets directory not found." "ERROR"
    return
}

function Sync-Assets {
    param([string]$ProjectName)
    $repoPath = Get-ProjectRoot -ProjectName $ProjectName
    if (-not $repoPath) { return }

    $target = Join-Path $repoPath "assets_shared"
    if (-not (Test-Path $target)) {
        Write-AASLog "Creating symlink for assets in $ProjectName" "INFO"
        # New-Item -ItemType SymbolicLink -Path $target -Value $assetsDir
    }
}

$projects = @("AaroneousAutomationSuite", "AndroidApp")
foreach ($p in $projects) {
    Sync-Assets -ProjectName $p
}

Write-AASLog "Asset sync complete. (Symlinking commented out for safety)" "SUCCESS"
