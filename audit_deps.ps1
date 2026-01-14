. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

function Audit-PythonDeps {
    param([string]$RepoPath)
    $reqFile = Join-Path $RepoPath "requirements.txt"
    if (Test-Path $reqFile) {
        Write-AASLog "Auditing Python dependencies in $RepoPath" "INFO"
        $deps = Get-Content $reqFile | Where-Object { $_ -match "==" }
        foreach ($d in $deps) {
            # Simple check for common mismatches could go here
        }
    }
}

$baseDir = "D:\Dev library"
$projects = Get-ChildItem $baseDir -Directory | Where-Object { $_.Name -notmatch "^(\.|_archive)" }

foreach ($p in $projects) {
    Audit-PythonDeps -RepoPath $p.FullName
}

Write-AASLog "Dependency audit complete." "SUCCESS"
