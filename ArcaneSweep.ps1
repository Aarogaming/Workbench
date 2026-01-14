. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

function Clean-Project {
    param([string]$RepoPath)
    
    Write-AASLog "Cleaning $RepoPath..." "INFO"
    
    $targets = @(
        "bin", "obj", "dist", "build", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"
    )

    foreach ($target in $targets) {
        $path = Join-Path $RepoPath $target
        if (Test-Path $path) {
            Write-AASLog "Removing $path" "INFO"
            Remove-Item -Recurse -Force $path
        }
    }
}

$baseDir = "D:\Dev library"
$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    Clean-Project -RepoPath $p.FullName
}

Write-AASLog "Global cleanup complete." "SUCCESS"
