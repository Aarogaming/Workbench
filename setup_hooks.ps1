. "$PSScriptRoot\log_helper.ps1"
. "$PSScriptRoot\AuraSense.ps1"

function Install-Hooks {
    param([string]$ProjectName)
    
    $repoPath = Get-ProjectRoot -ProjectName $ProjectName
    if (-not $repoPath) { return }

    $gitDir = Join-Path $repoPath ".git"
    if (-not (Test-Path $gitDir)) {
        Write-AASLog "No .git directory in $ProjectName. Skipping hooks." "WARN"
        return
    }

    $hooksDir = Join-Path $gitDir "hooks"
    $preCommit = Join-Path $hooksDir "pre-commit"

    $hookContent = @"
#!/bin/sh
# AAS Shared Pre-commit Hook
echo "Running shared pre-commit checks for $ProjectName..."
# Add cross-repo checks here
"@

    Set-Content $preCommit $hookContent
    Write-AASLog "Installed pre-commit hook for $ProjectName" "SUCCESS"
}

$projects = @("AaroneousAutomationSuite", "MyFortress", "AndroidApp")
foreach ($p in $projects) {
    Install-Hooks -ProjectName $p
}
